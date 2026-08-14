import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
VERIFIER = ROOT / "scripts" / "verify-native-lifecycle.py"


def write_jsonl(path: Path, records: list[dict]) -> None:
    path.write_text("".join(json.dumps(record) + "\n" for record in records))


def message(timestamp: str, role: str, text: str) -> dict:
    return {
        "timestamp": timestamp,
        "type": "response_item",
        "payload": {
            "type": "message",
            "role": role,
            "content": [{"type": "output_text", "text": text}],
        },
    }


def call(timestamp: str, name: str, arguments: str, call_id: str) -> dict:
    return {
        "timestamp": timestamp,
        "type": "response_item",
        "payload": {
            "type": "function_call",
            "name": name,
            "arguments": arguments,
            "call_id": call_id,
        },
    }


def exec_call(timestamp: str, input_text: str, call_id: str) -> dict:
    return {
        "timestamp": timestamp,
        "type": "response_item",
        "payload": {
            "type": "custom_tool_call",
            "name": "exec",
            "input": input_text,
            "call_id": call_id,
        },
    }


def event(timestamp: str, event_type: str, turn_id: str, **extra: str) -> dict:
    return {
        "timestamp": timestamp,
        "type": "event_msg",
        "payload": {"type": event_type, "turn_id": turn_id, **extra},
    }


class NativeLifecycleVerifierTest(unittest.TestCase):
    def run_verifier(
        self,
        root_records: list[dict],
        child_records: list[dict] | None,
        *extra_args: str,
        manifest: dict | None = None,
    ) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as temp_dir:
            root_path = Path(temp_dir) / "root.jsonl"
            write_jsonl(root_path, root_records)
            command = [
                sys.executable,
                VERIFIER,
                "--root-rollout",
                root_path,
                *extra_args,
            ]
            if child_records is not None:
                child_path = Path(temp_dir) / "child.jsonl"
                write_jsonl(child_path, child_records)
                command.extend(["--child-rollout", child_path])
            if manifest is not None:
                manifest_path = Path(temp_dir) / "manifest.json"
                manifest_path.write_text(json.dumps(manifest))
                command.extend(["--ownership-manifest", manifest_path])
            return subprocess.run(command, text=True, capture_output=True)

    def happy_records(self) -> tuple[list[dict], list[dict], dict]:
        root_records = [
            {
                "timestamp": "2026-08-13T10:00:00Z",
                "type": "session_meta",
                "payload": {"id": "root-rollout", "session_id": "root-session"},
            },
            {
                "timestamp": "2026-08-13T10:00:00.100000Z",
                "type": "turn_context",
                "payload": {"turn_id": "root-turn", "model": "gpt-5.6-terra", "effort": "high"},
            },
            message(
                "2026-08-13T10:00:00.500000Z",
                "assistant",
                "Dispatch Announcement\nRoot Lane: root-progress-artifact.md\nWork Mode: mixed",
            ),
            call(
                "2026-08-13T10:00:01Z",
                "spawn_agent",
                json.dumps(
                    {
                        "task_name": "docs_lane",
                        "agent_type": "docs-researcher",
                        "fork_turns": "none",
                        "message": "goal: collect evidence\nscope_in: child-evidence-artifact.md",
                    }
                ),
                "spawn-1",
            ),
            {
                "timestamp": "2026-08-13T10:00:02Z",
                "type": "response_item",
                "payload": {
                    "type": "function_call_output",
                    "call_id": "spawn-1",
                    "output": '{"task_name":"/root/docs_lane"}',
                },
            },
            exec_call(
                "2026-08-13T10:00:04Z",
                'await tools.apply_patch("*** Begin Patch\\n*** Update File: root-progress-artifact.md")',
                "root-progress",
            ),
            {
                "timestamp": "2026-08-13T10:00:06.500000Z",
                "type": "turn_context",
                "payload": {"turn_id": "root-followup", "model": "gpt-5.6-terra", "effort": "high"},
            },
            call(
                "2026-08-13T10:00:07Z",
                "followup_task",
                json.dumps({"target": "/root/docs_lane", "message": "Verify the related point."}),
                "followup-1",
            ),
            exec_call(
                "2026-08-13T10:00:11Z",
                'await tools.exec_command({"cmd":"verify-integrated-artifact"})',
                "root-verify",
            ),
        ]
        child_records = [
            {
                "timestamp": "2026-08-13T10:00:02Z",
                "type": "session_meta",
                "payload": {
                    "id": "child-session",
                    "parent_thread_id": "root-session",
                    "source": {
                        "subagent": {
                            "thread_spawn": {
                                "depth": 1,
                                "agent_path": "/root/docs_lane",
                                "agent_role": "docs-researcher",
                            }
                        }
                    },
                },
            },
            {
                "timestamp": "2026-08-13T10:00:03Z",
                "type": "turn_context",
                "payload": {"turn_id": "turn-1", "model": "gpt-5.6-luna", "effort": "high"},
            },
            event("2026-08-13T10:00:03Z", "task_started", "turn-1"),
            exec_call(
                "2026-08-13T10:00:05Z",
                'await tools.apply_patch("*** Begin Patch\\n*** Update File: child-evidence-artifact.md")',
                "child-write",
            ),
            event(
                "2026-08-13T10:00:06Z",
                "task_complete",
                "turn-1",
                last_agent_message="Bounded evidence returned to Root.",
            ),
            {
                "timestamp": "2026-08-13T10:00:08Z",
                "type": "turn_context",
                "payload": {"turn_id": "turn-2", "model": "gpt-5.6-luna", "effort": "high"},
            },
            event("2026-08-13T10:00:08Z", "task_started", "turn-2"),
            event(
                "2026-08-13T10:00:10Z",
                "task_complete",
                "turn-2",
                last_agent_message="Related follow-up evidence returned to Root.",
            ),
        ]
        manifest = {
            "before": {
                "root-progress-artifact.md": "root-before",
                "child-evidence-artifact.md": "child-before",
            },
            "after": {
                "root-progress-artifact.md": "root-after",
                "child-evidence-artifact.md": "child-after",
            },
        }
        return root_records, child_records, manifest

    def common_args(self) -> tuple[str, ...]:
        return (
            "--expected-role",
            "docs-researcher",
            "--policy",
            "auto",
            "--require-followup",
            "--root-progress-scope",
            "root-progress-artifact.md",
            "--verification-scope",
            "verify-integrated-artifact",
            "--root-write-scope",
            "root-progress-artifact.md",
            "--child-write-scope",
            "child-evidence-artifact.md",
            "--expected-root-model",
            "gpt-5.6-terra",
            "--expected-root-effort",
            "high",
        )

    def test_accepts_real_native_shapes_progress_reuse_and_ownership(self) -> None:
        root_records, child_records, manifest = self.happy_records()

        result = self.run_verifier(
            root_records, child_records, *self.common_args(), manifest=manifest
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertTrue(report["ok"], report)
        self.assertEqual(report["child_session_id"], "child-session")
        self.assertEqual(report["child_turn_ids"], ["turn-1", "turn-2"])
        self.assertEqual(report["child_model"], "gpt-5.6-luna")
        self.assertTrue(all(report["checks"].values()), report)

    def test_accepts_ask_approval_only_before_spawn(self) -> None:
        root_records, child_records, manifest = self.happy_records()
        root_records[2] = message(
            "2026-08-13T10:00:00.500000Z",
            "assistant",
            "Dispatch Recommendation",
        )
        root_records.insert(
            3,
            message(
                "2026-08-13T10:00:00.750000Z",
                "user",
                "Dispatch Authorization",
            ),
        )
        args = list(self.common_args())
        args[args.index("auto")] = "ask-approved"

        result = self.run_verifier(
            root_records, child_records, *args, manifest=manifest
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(json.loads(result.stdout)["checks"]["policy_order"])

    def test_accepts_integration_after_child_result_before_terminal(self) -> None:
        root_records, child_records, manifest = self.happy_records()
        root_records = root_records[:6]
        root_records.extend(
            [
                {
                    "timestamp": "2026-08-13T10:00:05.500000Z",
                    "type": "response_item",
                    "payload": {
                        "type": "agent_message",
                        "author": "/root/docs_lane",
                        "recipient": "/root",
                        "content": [
                            {
                                "type": "input_text",
                                "text": "Message Type: FINAL_ANSWER\nBounded evidence returned to Root.",
                            }
                        ],
                    },
                },
                exec_call(
                    "2026-08-13T10:00:05.750000Z",
                    'await tools.exec_command({"cmd":"verify-integrated-artifact"})',
                    "root-verify",
                ),
            ]
        )
        child_records = child_records[:5]
        args = list(self.common_args())
        args.remove("--require-followup")

        result = self.run_verifier(
            root_records, child_records, *args, manifest=manifest
        )

        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertTrue(
            json.loads(result.stdout)["checks"]["root_integration_verification"]
        )

    def test_rejects_same_child_followup_before_terminal(self) -> None:
        root_records, child_records, manifest = self.happy_records()
        root_records[7]["timestamp"] = "2026-08-13T10:00:05.500000Z"

        result = self.run_verifier(
            root_records, child_records, *self.common_args(), manifest=manifest
        )

        self.assertEqual(result.returncode, 1)
        self.assertFalse(json.loads(result.stdout)["checks"]["same_child_followup"])

    def test_rejects_bookkeeping_as_root_progress(self) -> None:
        root_records, child_records, manifest = self.happy_records()
        root_records[5] = call(
            "2026-08-13T10:00:04Z",
            "update_plan",
            '{"explanation":"root-progress-artifact.md"}',
            "not-progress",
        )

        result = self.run_verifier(
            root_records, child_records, *self.common_args(), manifest=manifest
        )

        self.assertEqual(result.returncode, 1)
        self.assertFalse(json.loads(result.stdout)["checks"]["root_progress_while_child_active"])

    def test_rejects_wrapped_bookkeeping_as_root_progress(self) -> None:
        root_records, child_records, manifest = self.happy_records()
        root_records[5] = exec_call(
            "2026-08-13T10:00:04Z",
            'await tools.update_plan({"explanation":"root-progress-artifact.md"})',
            "not-progress",
        )

        result = self.run_verifier(
            root_records, child_records, *self.common_args(), manifest=manifest
        )

        self.assertEqual(result.returncode, 1)
        self.assertFalse(json.loads(result.stdout)["checks"]["root_progress_while_child_active"])

    def test_rejects_root_reasoning_drift_across_resume(self) -> None:
        root_records, child_records, manifest = self.happy_records()
        root_records[6]["payload"]["effort"] = "medium"

        result = self.run_verifier(
            root_records, child_records, *self.common_args(), manifest=manifest
        )

        self.assertEqual(result.returncode, 1)
        self.assertFalse(json.loads(result.stdout)["checks"]["root_effort_frozen"])

    def test_rejects_child_descendant_spawn(self) -> None:
        root_records, child_records, manifest = self.happy_records()
        child_records.insert(
            4,
            call("2026-08-13T10:00:04Z", "spawn_agent", "{}", "descendant"),
        )

        result = self.run_verifier(
            root_records, child_records, *self.common_args(), manifest=manifest
        )

        self.assertEqual(result.returncode, 1)
        self.assertFalse(json.loads(result.stdout)["checks"]["leaf_child"])

    def test_rejects_duplicate_scope_under_a_different_task_name(self) -> None:
        root_records, child_records, manifest = self.happy_records()
        root_records.insert(
            4,
            call(
                "2026-08-13T10:00:01.500000Z",
                "spawn_agent",
                json.dumps(
                    {
                        "task_name": "duplicate_lane",
                        "agent_type": "docs-researcher",
                        "fork_turns": "none",
                        "message": "goal: repeat evidence\nscope_in: child-evidence-artifact.md",
                    }
                ),
                "spawn-duplicate",
            ),
        )

        result = self.run_verifier(
            root_records, child_records, *self.common_args(), manifest=manifest
        )

        self.assertEqual(result.returncode, 1)
        self.assertFalse(json.loads(result.stdout)["checks"]["no_duplicate_scope_spawn"])

    def test_rejects_extra_child_even_with_a_different_scope(self) -> None:
        root_records, child_records, manifest = self.happy_records()
        root_records.insert(
            4,
            call(
                "2026-08-13T10:00:01.500000Z",
                "spawn_agent",
                json.dumps(
                    {
                        "task_name": "extra_lane",
                        "agent_type": "reviewer",
                        "fork_turns": "none",
                        "message": "goal: extra review\nscope_in: another-artifact.md",
                    }
                ),
                "spawn-extra",
            ),
        )

        result = self.run_verifier(
            root_records, child_records, *self.common_args(), manifest=manifest
        )

        self.assertEqual(result.returncode, 1)
        self.assertFalse(json.loads(result.stdout)["checks"]["single_child_spawn"])

    def test_rejects_completion_without_a_final_child_result(self) -> None:
        root_records, child_records, manifest = self.happy_records()
        del child_records[4]["payload"]["last_agent_message"]

        result = self.run_verifier(
            root_records, child_records, *self.common_args(), manifest=manifest
        )

        self.assertEqual(result.returncode, 1)
        self.assertFalse(json.loads(result.stdout)["checks"]["child_result_returned"])

    def test_rejects_unauthorized_workspace_change(self) -> None:
        root_records, child_records, manifest = self.happy_records()
        manifest["after"]["unowned.md"] = "unexpected-write"

        result = self.run_verifier(
            root_records, child_records, *self.common_args(), manifest=manifest
        )

        self.assertEqual(result.returncode, 1)
        self.assertFalse(json.loads(result.stdout)["checks"]["write_ownership"])

    def test_rejects_child_shell_write_to_root_owned_scope(self) -> None:
        root_records, child_records, manifest = self.happy_records()
        child_records.insert(
            4,
            exec_call(
                "2026-08-13T10:00:05.500000Z",
                'await tools.exec_command({"cmd":"printf x > root-progress-artifact.md"})',
                "cross-lane-write",
            ),
        )

        result = self.run_verifier(
            root_records, child_records, *self.common_args(), manifest=manifest
        )

        self.assertEqual(result.returncode, 1)
        self.assertFalse(json.loads(result.stdout)["checks"]["write_ownership"])

    def test_accepts_ask_refusal_with_zero_spawn_and_root_continuation(self) -> None:
        root_records = [
            {
                "timestamp": "2026-08-13T09:59:59Z",
                "type": "turn_context",
                "payload": {"turn_id": "proposal", "model": "gpt-5.6-terra", "effort": "high"},
            },
            message("2026-08-13T10:00:00Z", "assistant", "Dispatch Recommendation"),
            message("2026-08-13T10:00:01Z", "user", "Dispatch Refused"),
            {
                "timestamp": "2026-08-13T10:00:01.500000Z",
                "type": "turn_context",
                "payload": {"turn_id": "refusal", "model": "gpt-5.6-terra", "effort": "high"},
            },
            exec_call(
                "2026-08-13T10:00:02Z",
                'await tools.exec_command({"cmd":"root-only-artifact"})',
                "root-only",
            ),
        ]

        result = self.run_verifier(
            root_records,
            None,
            "--scenario",
            "ask-refused",
            "--root-progress-scope",
            "root-only-artifact",
            "--expected-root-model",
            "gpt-5.6-terra",
            "--expected-root-effort",
            "high",
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(json.loads(result.stdout)["ok"])

    def test_rejects_root_only_effort_drift(self) -> None:
        root_records = [
            {
                "timestamp": "2026-08-13T10:00:00Z",
                "type": "turn_context",
                "payload": {"turn_id": "first", "model": "gpt-5.6-terra", "effort": "high"},
            },
            {
                "timestamp": "2026-08-13T10:00:01Z",
                "type": "turn_context",
                "payload": {"turn_id": "second", "model": "gpt-5.6-terra", "effort": "medium"},
            },
            exec_call(
                "2026-08-13T10:00:02Z",
                'await tools.exec_command({"cmd":"root-only-artifact"})',
                "root-only",
            ),
        ]

        result = self.run_verifier(
            root_records,
            None,
            "--scenario",
            "native-absence",
            "--root-progress-scope",
            "root-only-artifact",
            "--expected-root-model",
            "gpt-5.6-terra",
            "--expected-root-effort",
            "high",
        )

        self.assertEqual(result.returncode, 1)
        self.assertFalse(json.loads(result.stdout)["checks"]["root_effort_frozen"])

    def test_accepts_silent_root_continuation_for_preactivation_bypasses(self) -> None:
        root_records = [
            exec_call(
                "2026-08-13T10:00:02Z",
                'await tools.exec_command({"cmd":"root-only-artifact"})',
                "root-only",
            ),
            message("2026-08-13T10:00:03Z", "assistant", "Task completed in Root."),
        ]

        for scenario in ("native-absence", "missing-role"):
            with self.subTest(scenario=scenario):
                result = self.run_verifier(
                    root_records,
                    None,
                    "--scenario",
                    scenario,
                    "--root-progress-scope",
                    "root-only-artifact",
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertTrue(json.loads(result.stdout)["ok"])

    def controlled_failure_records(self) -> tuple[list[dict], list[dict]]:
        root_records, child_records, _ = self.happy_records()
        child_records = child_records[:4]
        root_records[3] = call(
            "2026-08-13T10:00:01Z",
            "spawn_agent",
            json.dumps(
                {
                    "task_name": "failure_lane",
                    "agent_type": "test-automator",
                    "fork_turns": "none",
                    "message": "goal: run controlled failure\nscope_in: nonzero child operation",
                }
            ),
            "spawn-1",
        )
        child_records[0]["payload"]["source"]["subagent"]["thread_spawn"].update(
            {
                "agent_path": "/root/failure_lane",
                "agent_role": "test-automator",
            }
        )
        child_records[3] = exec_call(
            "2026-08-13T10:00:05Z",
            'await tools.exec_command({"cmd":"controlled-failure --exit 23"})',
            "controlled-nonzero",
        )
        child_records.extend(
            [
                {
                    "timestamp": "2026-08-13T10:00:05.500000Z",
                    "type": "response_item",
                    "payload": {
                        "type": "custom_tool_call_output",
                        "call_id": "controlled-nonzero",
                        "output": [
                            {
                                "type": "input_text",
                                "text": '{"exit_code":23,"output":"CONTROLLED_FAILURE_23"}',
                            }
                        ],
                    },
                },
                event(
                    "2026-08-13T10:00:06Z",
                    "task_complete",
                    "turn-1",
                    last_agent_message="The controlled child operation returned exit code 23.",
                ),
            ]
        )
        root_records = [
            record
            for record in root_records
            if record.get("timestamp") != "2026-08-13T10:00:07Z"
        ]
        root_records.extend(
            [
                message(
                    "2026-08-13T10:00:07Z",
                    "assistant",
                    "Affected Child Lane: failure_lane (test-automator). Root is taking over.",
                ),
                exec_call(
                    "2026-08-13T10:00:08Z",
                    'await tools.exec_command({"cmd":"verify root-progress-artifact.md root-takeover-artifact"})',
                    "takeover",
                ),
            ]
        )
        return root_records, child_records

    def run_controlled_failure(
        self, root_records: list[dict], child_records: list[dict]
    ) -> subprocess.CompletedProcess[str]:
        return self.run_verifier(
            root_records,
            child_records,
            "--scenario",
            "failure",
            "--expected-role",
            "test-automator",
            "--policy",
            "auto",
            "--root-progress-scope",
            "root-progress-artifact.md",
            "--verification-scope",
            "root-takeover-artifact",
        )

    def test_accepts_post_announcement_failure_and_root_takeover(self) -> None:
        root_records, child_records = self.controlled_failure_records()

        result = self.run_controlled_failure(root_records, child_records)

        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertTrue(report["checks"]["failure_reported"], report)
        self.assertTrue(report["checks"]["root_integration_verification"], report)

    def test_rejects_nonzero_output_without_a_matching_child_call(self) -> None:
        root_records, child_records = self.controlled_failure_records()
        child_records[4]["payload"]["call_id"] = "unrelated-call"

        result = self.run_controlled_failure(root_records, child_records)

        self.assertEqual(result.returncode, 1)
        self.assertFalse(json.loads(result.stdout)["checks"]["child_lifecycle_complete"])

    def test_rejects_nonzero_output_from_a_bookkeeping_call(self) -> None:
        root_records, child_records = self.controlled_failure_records()
        child_records[3]["payload"]["name"] = "send_message"

        result = self.run_controlled_failure(root_records, child_records)

        self.assertEqual(result.returncode, 1)
        self.assertFalse(json.loads(result.stdout)["checks"]["child_lifecycle_complete"])

    def test_rejects_nonzero_output_before_its_child_call(self) -> None:
        root_records, child_records = self.controlled_failure_records()
        child_records[4]["timestamp"] = "2026-08-13T10:00:04.500000Z"

        result = self.run_controlled_failure(root_records, child_records)

        self.assertEqual(result.returncode, 1)
        self.assertFalse(json.loads(result.stdout)["checks"]["child_lifecycle_complete"])

    def test_rejects_successful_child_output_with_failure_words(self) -> None:
        root_records, child_records = self.controlled_failure_records()
        child_records[4]["payload"]["output"][0]["text"] = (
            '{"exit_code":0,"output":"dependency not available"}'
        )

        result = self.run_controlled_failure(root_records, child_records)

        self.assertEqual(result.returncode, 1)
        self.assertFalse(json.loads(result.stdout)["checks"]["child_lifecycle_complete"])

    def test_rejects_failure_report_that_does_not_identify_the_lane(self) -> None:
        root_records, child_records = self.controlled_failure_records()
        root_records[-2]["payload"]["content"][0]["text"] = (
            "Affected Child Lane: another lane. Root is taking over."
        )

        result = self.run_controlled_failure(root_records, child_records)

        self.assertEqual(result.returncode, 1)
        self.assertFalse(json.loads(result.stdout)["checks"]["failure_reported"])

    def test_rejects_takeover_that_does_not_verify_preserved_root_work(self) -> None:
        root_records, child_records = self.controlled_failure_records()
        root_records[-1]["payload"]["input"] = (
            'await tools.exec_command({"cmd":"root-takeover-artifact"})'
        )

        result = self.run_controlled_failure(root_records, child_records)

        self.assertEqual(result.returncode, 1)
        self.assertFalse(json.loads(result.stdout)["checks"]["successful_work_preserved"])

    def test_accepts_spawn_failure_without_a_child_rollout(self) -> None:
        root_records = [
            {
                "timestamp": "2026-08-13T10:00:00Z",
                "type": "turn_context",
                "payload": {"turn_id": "root-turn", "model": "gpt-5.6-terra", "effort": "high"},
            },
            message(
                "2026-08-13T10:00:00.500000Z",
                "assistant",
                "Dispatch Announcement\nRoot Lane: root-takeover-artifact\nWork Mode: read-only",
            ),
            call(
                "2026-08-13T10:00:01Z",
                "spawn_agent",
                json.dumps(
                    {
                        "task_name": "docs_lane",
                        "agent_type": "docs-researcher",
                        "fork_turns": "none",
                        "message": "goal: evidence\nscope_in: docs evidence",
                    }
                ),
                "spawn-1",
            ),
            {
                "timestamp": "2026-08-13T10:00:02Z",
                "type": "response_item",
                "payload": {
                    "type": "function_call_output",
                    "call_id": "spawn-1",
                    "output": "Spawn failed: requested role unavailable",
                },
            },
            message(
                "2026-08-13T10:00:03Z",
                "assistant",
                "Affected Child Lane: docs_lane (docs-researcher). Root is taking over.",
            ),
            exec_call(
                "2026-08-13T10:00:04Z",
                'await tools.exec_command({"cmd":"root-takeover-artifact"})',
                "takeover",
            ),
        ]

        result = self.run_verifier(
            root_records,
            None,
            "--scenario",
            "failure",
            "--expected-role",
            "docs-researcher",
            "--policy",
            "auto",
            "--root-progress-scope",
            "root-takeover-artifact",
            "--verification-scope",
            "root-takeover-artifact",
            "--expected-root-model",
            "gpt-5.6-terra",
            "--expected-root-effort",
            "high",
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["failure_kind"], "spawn")
        self.assertTrue(report["ok"], report)


if __name__ == "__main__":
    unittest.main()
