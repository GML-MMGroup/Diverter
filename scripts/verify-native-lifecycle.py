#!/usr/bin/env python3
"""Verify Diverter behavior from persisted native Codex rollout records."""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime
import json
from pathlib import Path
import re
import sys
from typing import Any


ORCHESTRATION_TOOLS = {
    "followup_task",
    "interrupt_agent",
    "list_agents",
    "send_message",
    "spawn_agent",
    "wait_agent",
}
BOOKKEEPING_TOOLS = ORCHESTRATION_TOOLS | {
    "create_goal",
    "get_goal",
    "update_goal",
    "update_plan",
    "wait",
    "write_stdin",
}
FINAL_ANSWER_MESSAGE = "Message Type: FINAL_ANSWER"


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    records = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as error:
            raise ValueError(f"{path}:{line_number}: invalid JSON: {error.msg}") from error
        if not isinstance(record, dict):
            raise ValueError(f"{path}:{line_number}: expected a JSON object")
        records.append(record)
    return records


def load_manifest(path: Path | None) -> dict[str, dict[str, str]] | None:
    if path is None:
        return None
    manifest = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(manifest, dict):
        raise ValueError(f"{path}: expected a JSON object")
    before = manifest.get("before")
    after = manifest.get("after")
    if not isinstance(before, dict) or not isinstance(after, dict):
        raise ValueError(f"{path}: expected before and after hash objects")
    if not all(isinstance(key, str) and isinstance(value, str) for key, value in before.items()):
        raise ValueError(f"{path}: invalid before hash map")
    if not all(isinstance(key, str) and isinstance(value, str) for key, value in after.items()):
        raise ValueError(f"{path}: invalid after hash map")
    return {"before": before, "after": after}


def timestamp(record: dict[str, Any]) -> datetime | None:
    value = record.get("timestamp")
    if not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def payloads(records: list[dict[str, Any]], kind: str) -> list[dict[str, Any]]:
    return [
        record["payload"]
        for record in records
        if record.get("type") == kind and isinstance(record.get("payload"), dict)
    ]


def timed_payloads(
    records: list[dict[str, Any]], record_type: str, payload_type: str
) -> list[tuple[datetime, dict[str, Any]]]:
    found = []
    for record in records:
        payload = record.get("payload")
        when = timestamp(record)
        if (
            record.get("type") == record_type
            and isinstance(payload, dict)
            and payload.get("type") == payload_type
            and when is not None
        ):
            found.append((when, payload))
    return found


def function_calls(records: list[dict[str, Any]]) -> list[tuple[datetime, dict[str, Any]]]:
    calls = []
    for record in records:
        payload = record.get("payload")
        when = timestamp(record)
        if (
            record.get("type") == "response_item"
            and isinstance(payload, dict)
            and payload.get("type") in {"function_call", "custom_tool_call"}
            and when is not None
        ):
            calls.append((when, payload))
    return calls


def decoded_arguments(call: dict[str, Any]) -> dict[str, Any]:
    arguments = call.get("arguments")
    if isinstance(arguments, dict):
        return arguments
    if isinstance(arguments, str):
        try:
            decoded = json.loads(arguments)
        except json.JSONDecodeError:
            return {}
        return decoded if isinstance(decoded, dict) else {}
    return {}


def call_text(call: dict[str, Any]) -> str:
    value = call.get("arguments", call.get("input", ""))
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        return json.dumps(value, sort_keys=True)
    return ""


def content_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    if not isinstance(content, list):
        return ""
    chunks = []
    for item in content:
        if not isinstance(item, dict):
            continue
        text = item.get("text")
        if isinstance(text, str):
            chunks.append(text)
    return "\n".join(chunks)


def messages(
    records: list[dict[str, Any]], role: str
) -> list[tuple[datetime, str]]:
    found = []
    for record in records:
        payload = record.get("payload")
        when = timestamp(record)
        if (
            record.get("type") == "response_item"
            and isinstance(payload, dict)
            and payload.get("type") == "message"
            and payload.get("role") == role
            and when is not None
        ):
            found.append((when, content_text(payload.get("content"))))
    return found


def final_child_outputs(
    records: list[dict[str, Any]], child_path: str | None
) -> list[tuple[datetime, str]]:
    found = []
    for record in records:
        payload = record.get("payload")
        when = timestamp(record)
        if (
            record.get("type") == "response_item"
            and isinstance(payload, dict)
            and payload.get("type") == "agent_message"
            and payload.get("author") == child_path
            and when is not None
        ):
            text = content_text(payload.get("content"))
            if FINAL_ANSWER_MESSAGE in text:
                found.append((when, text))
    return found


def failed_tool_events(
    records: list[dict[str, Any]], *, allow_text_markers: bool = True
) -> list[tuple[datetime, dict[str, Any]]]:
    markers = (
        "script failed",
        "permission denied",
        "operation not permitted",
        "read-only file system",
        "sandbox denied",
        "spawn failed",
        "failed to spawn",
        "unavailable",
        "not available",
    )
    found = []
    for record in records:
        payload = record.get("payload")
        when = timestamp(record)
        if (
            record.get("type") == "response_item"
            and isinstance(payload, dict)
            and payload.get("type") in {"function_call_output", "custom_tool_call_output"}
            and when is not None
        ):
            output = json.dumps(payload.get("output", ""), sort_keys=True).lower()
            exit_codes = re.findall(
                r'\\?"(?:exit_code|returncode)\\?"\s*:\s*(-?\d+)', output
            )
            marker_failure = allow_text_markers and any(
                marker in output for marker in markers
            )
            if marker_failure or any(int(code) != 0 for code in exit_codes):
                found.append((when, payload))
    return found


def has_failure_report(
    records: list[dict[str, Any]],
    after: datetime | None,
    report_marker: str,
    lane_markers: tuple[Any, ...],
) -> bool:
    return any(
        when > after
        and report_marker in text
        and any(marker in text for marker in lane_markers if isinstance(marker, str))
        for when, text in messages(records, "assistant")
        if after is not None
    )


def nested(data: dict[str, Any], *keys: str) -> Any:
    value: Any = data
    for key in keys:
        if not isinstance(value, dict):
            return None
        value = value.get(key)
    return value


def scope_key(arguments: dict[str, Any]) -> str | None:
    message = arguments.get("message")
    if not isinstance(message, str):
        return None
    match = re.search(r"(?im)^\s*(?:scope_in|scope)\s*:\s*(.+)$", message)
    if not match:
        return None
    return " ".join(match.group(1).lower().split())


def substantive_call(call: dict[str, Any]) -> bool:
    if call.get("name") in BOOKKEEPING_TOOLS:
        return False
    nested_tools = re.findall(r"tools\.([A-Za-z0-9_]+)\s*\(", call_text(call))
    return not any(tool in BOOKKEEPING_TOOLS for tool in nested_tools)


def meaningful_call(call: dict[str, Any], marker: str) -> bool:
    return substantive_call(call) and marker in call_text(call)


def patch_call(call: dict[str, Any]) -> bool:
    if call.get("name") == "apply_patch":
        return True
    return call.get("name") == "exec" and "tools.apply_patch" in call_text(call)


def scoped_mutation_call(call: dict[str, Any], scopes: list[str]) -> bool:
    text = call_text(call)
    if not any(scope in text for scope in scopes):
        return False
    return patch_call(call) or call.get("name") in {"exec_command", "write_stdin"} or (
        call.get("name") == "exec"
        and any(
            token in text
            for token in ("tools.exec_command", "tools.write_stdin", "tools.apply_patch")
        )
    )


def scope_matches(path: str, scope: str) -> bool:
    normalized_path = path.replace("\\", "/")
    normalized_scope = scope.replace("\\", "/").lstrip("./")
    return normalized_path == normalized_scope or normalized_path.endswith(
        f"/{normalized_scope}"
    )


def changed_paths(manifest: dict[str, dict[str, str]]) -> list[str]:
    before = manifest["before"]
    after = manifest["after"]
    return sorted(
        path for path in before.keys() | after.keys() if before.get(path) != after.get(path)
    )


def eligible_receipt(text: str, policy: str) -> bool:
    lines = text.strip().splitlines()
    if len(lines) < 5 or lines[0] != "Routing: ELIGIBLE":
        return False
    index = 1
    child_count = 0
    while index < len(lines) and lines[index].startswith("Child: `"):
        role, separator, task = lines[index][len("Child: `") :].partition("` — ")
        if not role or separator != "` — " or not task.strip():
            return False
        child_count += 1
        index += 1
    if child_count == 0 or len(lines) != index + 3:
        return False
    if not lines[index].startswith("Root: ") or not lines[index][
        len("Root: ") :
    ].strip():
        return False
    if lines[index + 1] not in {
        "Work Mode: read-only",
        "Work Mode: mixed",
        "Work Mode: write-capable",
    }:
        return False
    ending = lines[index + 2]
    if policy == "auto":
        return (
            ending.startswith("➡️ Dispatch: ")
            and bool(ending[len("➡️ Dispatch: ") :].strip())
            and "?" not in ending
            and "？" not in ending
        )
    return (
        ending.startswith("➡️ Dispatch Authorization: ")
        and bool(ending[len("➡️ Dispatch Authorization: ") :].strip())
        and ("?" in ending or "？" in ending)
    )


def policy_order(
    root_records: list[dict[str, Any]], policy: str | None, spawn_when: datetime | None
) -> bool:
    if policy is None:
        return True
    assistants = messages(root_records, "assistant")
    users = messages(root_records, "user")
    if policy == "auto":
        announcements = [
            (when, text)
            for when, text in assistants
            if eligible_receipt(text, "auto")
        ]
        return bool(
            spawn_when
            and len(announcements) == 1
            and assistants[0] == announcements[0]
            and announcements[0][0] < spawn_when
        )
    recommendations = [
        (when, text)
        for when, text in assistants
        if eligible_receipt(text, "ask")
    ]
    approvals = [
        when for when, text in users if "Dispatch Authorization" in text
    ]
    return bool(
        spawn_when
        and len(recommendations) == 1
        and assistants[0] == recommendations[0]
        and approvals
        and recommendations[0][0] < approvals[-1] < spawn_when
    )


def verify_root_only(
    root_records: list[dict[str, Any]],
    scenario: str,
    root_progress_scope: str,
    expected_root_model: str | None,
    expected_root_effort: str | None,
) -> dict[str, Any]:
    root_calls = function_calls(root_records)
    spawn_calls = [call for _, call in root_calls if call.get("name") == "spawn_agent"]
    assistants = messages(root_records, "assistant")
    users = messages(root_records, "user")
    if scenario == "ask-refused":
        recommendations = [
            when for when, text in assistants if eligible_receipt(text, "ask")
        ]
        refusals = [when for when, text in users if "Dispatch Refused" in text]
        boundary = max(refusals) if refusals else None
        policy_check = bool(
            len(recommendations) == 1
            and assistants
            and assistants[0][0] == recommendations[0]
            and refusals
            and recommendations[0] < refusals[-1]
            and all("Routing: ROOT_ONLY" not in text for _, text in assistants)
        )
    else:
        boundary = None
        policy_check = all(
            not eligible_receipt(text, "auto")
            and not eligible_receipt(text, "ask")
            and "Dispatch Announcement" not in text
            and "Diverter" not in text
            and "Routing: ROOT_ONLY" not in text
            for _, text in assistants
        )
    root_continues = any(
        meaningful_call(call, root_progress_scope)
        and (boundary is None or when > boundary)
        for when, call in root_calls
    )
    root_contexts = payloads(root_records, "turn_context")
    checks = {
        "zero_native_spawn": not spawn_calls,
        "root_continues": root_continues,
        "policy_or_inert_boundary": policy_check,
        "root_model_frozen": not expected_root_model
        or (
            bool(root_contexts)
            and all(context.get("model") == expected_root_model for context in root_contexts)
        ),
        "root_effort_frozen": not expected_root_effort
        or (
            bool(root_contexts)
            and all(context.get("effort") == expected_root_effort for context in root_contexts)
        ),
    }
    return {
        "ok": all(checks.values()),
        "checks": checks,
        "scenario": scenario,
        "root_models": [context.get("model") for context in root_contexts],
        "root_reasoning_efforts": [context.get("effort") for context in root_contexts],
    }


def verify_spawn_failure(
    root_records: list[dict[str, Any]],
    expected_role: str,
    policy: str | None,
    verification_scope: str,
    failure_report_marker: str,
    expected_root_model: str | None,
    expected_root_effort: str | None,
) -> dict[str, Any]:
    root_calls = function_calls(root_records)
    spawns = [
        (when, call, decoded_arguments(call))
        for when, call in root_calls
        if call.get("name") == "spawn_agent"
    ]
    spawn_when, spawn_call, spawn_arguments = spawns[0] if spawns else (None, {}, {})
    lane_markers = (spawn_arguments.get("task_name"), expected_role)
    spawn_call_id = spawn_call.get("call_id")
    failed_outputs = [
        (when, payload)
        for when, payload in failed_tool_events(root_records)
        if payload.get("call_id") == spawn_call_id
    ]
    failure_when = failed_outputs[0][0] if failed_outputs else None
    report_after_failure = has_failure_report(
        root_records, failure_when, failure_report_marker, lane_markers
    )
    root_takeover = any(
        when > failure_when and meaningful_call(call, verification_scope)
        for when, call in root_calls
        if failure_when is not None
    )
    root_contexts = payloads(root_records, "turn_context")
    checks = {
        "native_spawn_attempt": len(spawns) == 1
        and spawn_arguments.get("agent_type") == expected_role
        and spawn_arguments.get("fork_turns") == "none"
        and "model" not in spawn_arguments
        and "reasoning_effort" not in spawn_arguments,
        "policy_order": policy_order(root_records, policy, spawn_when),
        "spawn_failure_observed": bool(failed_outputs),
        "failure_reported": report_after_failure,
        "root_takeover": root_takeover,
        "no_substitute_spawn": len(spawns) == 1,
        "root_model_frozen": not expected_root_model
        or (
            bool(root_contexts)
            and all(context.get("model") == expected_root_model for context in root_contexts)
        ),
        "root_effort_frozen": not expected_root_effort
        or (
            bool(root_contexts)
            and all(context.get("effort") == expected_root_effort for context in root_contexts)
        ),
    }
    return {
        "ok": all(checks.values()),
        "checks": checks,
        "scenario": "failure",
        "failure_kind": "spawn",
        "root_models": [context.get("model") for context in root_contexts],
        "root_reasoning_efforts": [context.get("effort") for context in root_contexts],
    }


def verify_child(
    root_records: list[dict[str, Any]],
    child_records: list[dict[str, Any]],
    expected_role: str,
    scenario: str,
    policy: str | None,
    require_followup: bool,
    root_progress_scope: str,
    verification_scope: str,
    root_write_scope: str | None,
    child_write_scope: str | None,
    manifest: dict[str, dict[str, str]] | None,
    failure_report_marker: str,
    expected_root_model: str | None,
    expected_root_effort: str | None,
) -> dict[str, Any]:
    root_meta = next(iter(payloads(root_records, "session_meta")), {})
    child_meta = next(iter(payloads(child_records, "session_meta")), {})
    root_contexts = payloads(root_records, "turn_context")
    root_context = next(iter(root_contexts), {})
    child_contexts = payloads(child_records, "turn_context")
    child_context = next(iter(child_contexts), {})
    child_session_id = child_meta.get("id")
    child_path = nested(child_meta, "source", "subagent", "thread_spawn", "agent_path")
    child_role = nested(child_meta, "source", "subagent", "thread_spawn", "agent_role")
    child_depth = nested(child_meta, "source", "subagent", "thread_spawn", "depth")

    root_calls = function_calls(root_records)
    child_calls = function_calls(child_records)
    spawn_calls = [
        (when, call, decoded_arguments(call))
        for when, call in root_calls
        if call.get("name") == "spawn_agent"
    ]
    child_task_name = child_path.rsplit("/", 1)[-1] if isinstance(child_path, str) else None
    matching_spawns = [
        item for item in spawn_calls if item[2].get("task_name") == child_task_name
    ]
    spawn_when, spawn_call, spawn_arguments = (
        matching_spawns[0] if matching_spawns else (None, {}, {})
    )
    spawn_call_id = spawn_call.get("call_id")
    spawn_returns = []
    for record in root_records:
        payload = record.get("payload")
        when = timestamp(record)
        if (
            record.get("type") == "response_item"
            and isinstance(payload, dict)
            and payload.get("type") == "function_call_output"
            and payload.get("call_id") == spawn_call_id
            and when is not None
        ):
            spawn_returns.append(when)

    starts = timed_payloads(child_records, "event_msg", "task_started")
    completes = timed_payloads(child_records, "event_msg", "task_complete")
    failures = timed_payloads(child_records, "event_msg", "turn_aborted")
    child_call_times = {
        call["call_id"]: when
        for when, call in child_calls
        if call.get("call_id") is not None and substantive_call(call)
    }
    failures.extend(
        (when, payload)
        for when, payload in failed_tool_events(
            child_records, allow_text_markers=False
        )
        if payload.get("call_id") in child_call_times
        and child_call_times[payload["call_id"]] < when
    )
    failures.sort(key=lambda item: item[0])
    first_start = starts[0][0] if starts else None
    if scenario == "failure" and failures:
        later_completions = [event for event in completes if event[0] > failures[0][0]]
        terminal_events = later_completions or failures
    else:
        terminal_events = completes
    first_terminal = terminal_events[0][0] if terminal_events else None
    last_terminal = terminal_events[-1][0] if terminal_events else None

    root_progress = any(
        first_start < when < first_terminal
        and meaningful_call(call, root_progress_scope)
        for when, call in root_calls
        if first_start is not None and first_terminal is not None
    )
    received_results = final_child_outputs(root_records, child_path)
    integration_boundary = last_terminal
    if scenario != "failure" and len(received_results) >= len(completes):
        integration_boundary = received_results[-1][0]
    integration_verification = any(
        when > integration_boundary and meaningful_call(call, verification_scope)
        for when, call in root_calls
        if integration_boundary is not None
    )

    start_by_turn = {
        payload.get("turn_id"): when
        for when, payload in starts
        if isinstance(payload.get("turn_id"), str)
    }
    complete_by_turn = {
        payload.get("turn_id"): (when, payload)
        for when, payload in completes
        if isinstance(payload.get("turn_id"), str)
    }
    unique_turn_ids = [
        context.get("turn_id")
        for context in child_contexts
        if isinstance(context.get("turn_id"), str)
    ]
    complete_lifecycle = bool(start_by_turn) and start_by_turn.keys() == complete_by_turn.keys()
    complete_lifecycle = complete_lifecycle and all(
        start_by_turn[turn_id] < complete_by_turn[turn_id][0]
        for turn_id in start_by_turn
    )
    child_results = complete_lifecycle and all(
        isinstance(payload.get("last_agent_message"), str)
        and bool(payload["last_agent_message"].strip())
        for _, payload in complete_by_turn.values()
    )
    if scenario == "failure":
        complete_lifecycle = bool(
            failures and first_start and first_terminal and first_start < failures[0][0]
        )
        child_results = True

    followups = [
        (when, decoded_arguments(call))
        for when, call in root_calls
        if call.get("name") == "followup_task"
    ]
    reuse_chain = False
    if require_followup and len(starts) >= 2 and completes:
        first_complete = completes[0][0]
        second_start = starts[1][0]
        reuse_chain = any(
            arguments.get("target") == child_path
            and first_complete < when < second_start
            for when, arguments in followups
        )

    spawn_scope_keys = [scope_key(arguments) for _, _, arguments in spawn_calls]
    scoped_spawns = [key for key in spawn_scope_keys if key]
    no_duplicate_scope = bool(spawn_scope_keys) and len(scoped_spawns) == len(spawn_scope_keys)
    no_duplicate_scope = no_duplicate_scope and all(
        count == 1 for count in Counter(scoped_spawns).values()
    )

    write_ownership = root_write_scope is None and child_write_scope is None
    hashes: dict[str, str | None] = {}
    if root_write_scope is not None or child_write_scope is not None:
        write_ownership = bool(root_write_scope and child_write_scope and manifest)
        if write_ownership:
            changed = changed_paths(manifest)
            owned = [root_write_scope, child_write_scope]
            write_ownership = root_write_scope != child_write_scope
            write_ownership = write_ownership and all(
                any(scope_matches(path, scope) for scope in owned) for path in changed
            )
            write_ownership = write_ownership and all(
                any(scope_matches(path, scope) for path in changed) for scope in owned
            )
            root_patches = [call for _, call in root_calls if patch_call(call)]
            child_patches = [call for _, call in child_calls if patch_call(call)]
            root_mutations = [
                call
                for _, call in root_calls
                if scoped_mutation_call(call, owned)
            ]
            child_mutations = [
                call
                for _, call in child_calls
                if scoped_mutation_call(call, owned)
            ]
            write_ownership = write_ownership and any(
                root_write_scope in call_text(call) for call in root_patches
            )
            write_ownership = write_ownership and any(
                child_write_scope in call_text(call) for call in child_patches
            )
            write_ownership = write_ownership and all(
                child_write_scope not in call_text(call) for call in root_mutations
            )
            write_ownership = write_ownership and all(
                root_write_scope not in call_text(call) for call in child_mutations
            )
            for scope in owned:
                path = next((path for path in changed if scope_matches(path, scope)), None)
                hashes[f"{scope}:before"] = manifest["before"].get(path) if path else None
                hashes[f"{scope}:after"] = manifest["after"].get(path) if path else None

    failure_reported = True
    no_substitute_spawn = True
    successful_work_preserved = True
    if scenario == "failure":
        lane_markers = (child_task_name, expected_role)
        failure_reported = has_failure_report(
            root_records, last_terminal, failure_report_marker, lane_markers
        )
        no_substitute_spawn = len(spawn_calls) == 1
        failure_when = failures[0][0] if failures else None
        successful_work_preserved = any(
            when > failure_when
            and meaningful_call(call, verification_scope)
            and root_progress_scope in call_text(call)
            for when, call in root_calls
            if failure_when is not None
        )

    root_model_frozen = not expected_root_model or (
        bool(root_contexts)
        and all(context.get("model") == expected_root_model for context in root_contexts)
    )
    root_effort_frozen = not expected_root_effort or (
        bool(root_contexts)
        and all(context.get("effort") == expected_root_effort for context in root_contexts)
    )

    checks = {
        "native_spawn": bool(matching_spawns)
        and spawn_arguments.get("agent_type") == expected_role
        and spawn_arguments.get("fork_turns") == "none"
        and "model" not in spawn_arguments
        and "reasoning_effort" not in spawn_arguments,
        "policy_order": policy_order(root_records, policy, spawn_when),
        "native_role_resolution": child_role == expected_role and child_depth == 1,
        "parent_child_link": bool(root_meta)
        and child_meta.get("parent_thread_id")
        in {root_meta.get("id"), root_meta.get("session_id")},
        "child_lifecycle_complete": complete_lifecycle,
        "child_result_returned": child_results,
        "spawn_returns_before_child_terminal": bool(spawn_returns)
        and first_terminal is not None
        and min(spawn_returns) < first_terminal,
        "root_progress_while_child_active": root_progress,
        "root_integration_verification": integration_verification,
        "leaf_child": all(call.get("name") != "spawn_agent" for _, call in child_calls),
        "single_child_spawn": len(spawn_calls) == 1,
        "no_duplicate_scope_spawn": no_duplicate_scope,
        "same_child_followup": not require_followup
        or (
            reuse_chain
            and len(unique_turn_ids) >= 2
            and len(unique_turn_ids) == len(set(unique_turn_ids))
            and len(matching_spawns) == 1
        ),
        "write_ownership": write_ownership,
        "failure_reported": failure_reported,
        "successful_work_preserved": successful_work_preserved,
        "no_substitute_spawn": no_substitute_spawn,
        "root_model_frozen": root_model_frozen,
        "root_effort_frozen": root_effort_frozen,
    }
    return {
        "ok": all(checks.values()),
        "checks": checks,
        "scenario": scenario,
        "child_session_id": child_session_id,
        "child_path": child_path,
        "child_turn_ids": unique_turn_ids,
        "root_models": [context.get("model") for context in root_contexts],
        "root_reasoning_efforts": [context.get("effort") for context in root_contexts],
        "child_model": child_context.get("model"),
        "child_reasoning_effort": child_context.get("effort"),
        "artifact_hashes": hashes,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify native Root/Child lifecycle evidence from Codex JSONL rollouts."
    )
    parser.add_argument("--root-rollout", type=Path, required=True)
    parser.add_argument("--child-rollout", type=Path)
    parser.add_argument("--expected-role")
    parser.add_argument(
        "--scenario",
        choices=("normal", "failure", "ask-refused", "native-absence", "missing-role"),
        default="normal",
    )
    parser.add_argument("--policy", choices=("auto", "ask-approved"))
    parser.add_argument("--require-followup", action="store_true")
    parser.add_argument("--root-progress-scope", required=True)
    parser.add_argument("--verification-scope")
    parser.add_argument("--root-write-scope")
    parser.add_argument("--child-write-scope")
    parser.add_argument("--ownership-manifest", type=Path)
    parser.add_argument("--failure-report-marker", default="Affected Child Lane")
    parser.add_argument("--expected-root-model")
    parser.add_argument("--expected-root-effort")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.scenario in {"normal", "failure"} and (
        not args.expected_role or not args.verification_scope
    ):
        print(
            json.dumps(
                {
                    "ok": False,
                    "error": "normal/failure scenarios require --expected-role and --verification-scope",
                }
            )
        )
        return 2
    try:
        root_records = load_jsonl(args.root_rollout)
        if args.scenario == "failure" and args.child_rollout is None:
            report = verify_spawn_failure(
                root_records,
                args.expected_role,
                args.policy,
                args.verification_scope,
                args.failure_report_marker,
                args.expected_root_model,
                args.expected_root_effort,
            )
        elif args.scenario in {"normal", "failure"}:
            if args.child_rollout is None:
                raise ValueError("normal scenario requires --child-rollout")
            report = verify_child(
                root_records,
                load_jsonl(args.child_rollout),
                args.expected_role,
                args.scenario,
                args.policy,
                args.require_followup,
                args.root_progress_scope,
                args.verification_scope,
                args.root_write_scope,
                args.child_write_scope,
                load_manifest(args.ownership_manifest),
                args.failure_report_marker,
                args.expected_root_model,
                args.expected_root_effort,
            )
        else:
            report = verify_root_only(
                root_records,
                args.scenario,
                args.root_progress_scope,
                args.expected_root_model,
                args.expected_root_effort,
            )
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as error:
        print(json.dumps({"ok": False, "error": str(error)}))
        return 2
    print(json.dumps(report, sort_keys=True))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
