#!/usr/bin/env python3
"""Verify observable Diverter lifecycle invariants from native Codex rollouts."""

from __future__ import annotations

import argparse
from datetime import datetime
import json
from pathlib import Path
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


def argument_text(call: dict[str, Any]) -> str:
    arguments = call.get("arguments")
    if isinstance(arguments, str):
        return arguments
    if isinstance(arguments, dict):
        return json.dumps(arguments, sort_keys=True)
    return ""


def event_times(records: list[dict[str, Any]], event_type: str) -> list[datetime]:
    times = []
    for record in records:
        payload = record.get("payload")
        when = timestamp(record)
        if (
            record.get("type") == "event_msg"
            and isinstance(payload, dict)
            and payload.get("type") == event_type
            and when is not None
        ):
            times.append(when)
    return times


def nested(data: dict[str, Any], *keys: str) -> Any:
    value: Any = data
    for key in keys:
        if not isinstance(value, dict):
            return None
        value = value.get(key)
    return value


def verify(
    root_records: list[dict[str, Any]],
    child_records: list[dict[str, Any]],
    expected_role: str,
    require_followup: bool,
    root_write_scope: str | None,
    child_write_scope: str | None,
) -> dict[str, Any]:
    root_meta = next(iter(payloads(root_records, "session_meta")), {})
    child_meta = next(iter(payloads(child_records, "session_meta")), {})
    child_session_id = child_meta.get("id")
    child_path = nested(child_meta, "source", "subagent", "thread_spawn", "agent_path")
    child_role = nested(child_meta, "source", "subagent", "thread_spawn", "agent_role")
    child_depth = nested(child_meta, "source", "subagent", "thread_spawn", "depth")

    root_calls = function_calls(root_records)
    child_calls = function_calls(child_records)
    spawn_calls = [(when, call) for when, call in root_calls if call.get("name") == "spawn_agent"]
    matching_spawns = []
    child_task_name = child_path.rsplit("/", 1)[-1] if isinstance(child_path, str) else None
    for when, call in spawn_calls:
        arguments = decoded_arguments(call)
        if child_task_name is None or arguments.get("task_name") == child_task_name:
            matching_spawns.append((when, call, arguments))

    spawn = matching_spawns[0] if matching_spawns else (None, {}, {})
    spawn_when, spawn_call, spawn_arguments = spawn
    spawn_call_id = spawn_call.get("call_id")
    spawn_return_times = []
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
            spawn_return_times.append(when)

    starts = event_times(child_records, "task_started")
    results = event_times(child_records, "agent_message")
    completes = event_times(child_records, "task_complete")
    first_start = min(starts) if starts else None
    first_complete = min(completes) if completes else None
    last_complete = max(completes) if completes else None

    root_progress = any(
        first_start < when < first_complete and call.get("name") not in ORCHESTRATION_TOOLS
        for when, call in root_calls
        if first_start is not None and first_complete is not None
    )
    integration_verification = any(
        when > last_complete and call.get("name") not in ORCHESTRATION_TOOLS
        for when, call in root_calls
        if last_complete is not None
    )

    followups = [
        decoded_arguments(call)
        for _, call in root_calls
        if call.get("name") == "followup_task"
    ]
    followup_reuses_child = any(
        arguments.get("target") == child_path for arguments in followups
    )
    turn_count = len(payloads(child_records, "turn_context"))

    root_writes = [call for _, call in root_calls if call.get("name") == "apply_patch"]
    child_writes = [call for _, call in child_calls if call.get("name") == "apply_patch"]
    if root_write_scope is None and child_write_scope is None:
        write_ownership = True
    else:
        write_ownership = bool(root_write_scope and child_write_scope)
        write_ownership = write_ownership and root_write_scope != child_write_scope
        write_ownership = write_ownership and any(
            root_write_scope in argument_text(call) for call in root_writes
        )
        write_ownership = write_ownership and any(
            child_write_scope in argument_text(call) for call in child_writes
        )
        write_ownership = write_ownership and all(
            child_write_scope not in argument_text(call) for call in root_writes
        )
        write_ownership = write_ownership and all(
            root_write_scope not in argument_text(call) for call in child_writes
        )

    checks = {
        "native_spawn": bool(matching_spawns)
        and spawn_arguments.get("agent_type") == expected_role
        and spawn_arguments.get("fork_turns") == "none"
        and "model" not in spawn_arguments
        and "reasoning_effort" not in spawn_arguments,
        "native_role_resolution": child_role == expected_role and child_depth == 1,
        "parent_child_link": (
            bool(root_meta)
            and child_meta.get("parent_thread_id") == root_meta.get("id")
        ),
        "child_lifecycle_complete": bool(starts)
        and len(starts) == len(completes)
        and all(start < complete for start, complete in zip(starts, completes)),
        "child_result_returned": len(results) >= len(completes) > 0,
        "spawn_returns_before_child_completion": bool(spawn_return_times)
        and first_complete is not None
        and min(spawn_return_times) < first_complete,
        "root_progress_while_child_active": root_progress,
        "root_integration_verification": integration_verification,
        "leaf_child": all(call.get("name") != "spawn_agent" for _, call in child_calls),
        "no_duplicate_scope_spawn": len(matching_spawns) == 1,
        "same_child_followup": (
            not require_followup or (followup_reuses_child and turn_count >= 2)
        ),
        "write_ownership": write_ownership,
    }
    return {
        "ok": all(checks.values()),
        "checks": checks,
        "child_session_id": child_session_id,
        "child_path": child_path,
        "child_turn_count": turn_count,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify native Root/Child lifecycle evidence from Codex JSONL rollouts."
    )
    parser.add_argument("--root-rollout", type=Path, required=True)
    parser.add_argument("--child-rollout", type=Path, required=True)
    parser.add_argument("--expected-role", required=True)
    parser.add_argument("--require-followup", action="store_true")
    parser.add_argument("--root-write-scope")
    parser.add_argument("--child-write-scope")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        report = verify(
            load_jsonl(args.root_rollout),
            load_jsonl(args.child_rollout),
            args.expected_role,
            args.require_followup,
            args.root_write_scope,
            args.child_write_scope,
        )
    except (OSError, UnicodeError, ValueError) as error:
        print(json.dumps({"ok": False, "error": str(error)}))
        return 2
    print(json.dumps(report, sort_keys=True))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
