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


class NativeLifecycleVerifierTest(unittest.TestCase):
    def run_verifier(
        self, root_records: list[dict], child_records: list[dict]
    ) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as temp_dir:
            root_path = Path(temp_dir) / "root.jsonl"
            child_path = Path(temp_dir) / "child.jsonl"
            write_jsonl(root_path, root_records)
            write_jsonl(child_path, child_records)
            return subprocess.run(
                [
                    sys.executable,
                    VERIFIER,
                    "--root-rollout",
                    root_path,
                    "--child-rollout",
                    child_path,
                    "--expected-role",
                    "docs-researcher",
                    "--require-followup",
                    "--root-write-scope",
                    "root-progress-artifact.md",
                    "--child-write-scope",
                    "child-evidence-artifact.md",
                ],
                text=True,
                capture_output=True,
            )

    def test_accepts_native_progress_reuse_integration_and_leaf_trace(self) -> None:
        root_records = [
            {
                "timestamp": "2026-08-13T10:00:00Z",
                "type": "session_meta",
                "payload": {"id": "root-session"},
            },
            {
                "timestamp": "2026-08-13T10:00:01Z",
                "type": "response_item",
                "payload": {
                    "type": "function_call",
                    "name": "spawn_agent",
                    "arguments": json.dumps(
                        {
                            "task_name": "docs_lane",
                            "agent_type": "docs-researcher",
                            "fork_turns": "none",
                        }
                    ),
                    "call_id": "spawn-1",
                },
            },
            {
                "timestamp": "2026-08-13T10:00:02Z",
                "type": "response_item",
                "payload": {
                    "type": "function_call_output",
                    "call_id": "spawn-1",
                    "output": '{"task_name":"/root/docs_lane"}',
                },
            },
            {
                "timestamp": "2026-08-13T10:00:04Z",
                "type": "response_item",
                "payload": {
                    "type": "function_call",
                    "name": "apply_patch",
                    "arguments": "root-progress-artifact.md",
                    "call_id": "root-progress",
                },
            },
            {
                "timestamp": "2026-08-13T10:00:07Z",
                "type": "response_item",
                "payload": {
                    "type": "function_call",
                    "name": "followup_task",
                    "arguments": json.dumps(
                        {"target": "/root/docs_lane", "message": "Verify the related point."}
                    ),
                    "call_id": "followup-1",
                },
            },
            {
                "timestamp": "2026-08-13T10:00:11Z",
                "type": "response_item",
                "payload": {
                    "type": "function_call",
                    "name": "exec_command",
                    "arguments": "verify-integrated-artifact",
                    "call_id": "root-verify",
                },
            },
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
                "payload": {"turn_id": "turn-1", "model": "gpt-5.6-luna"},
            },
            {
                "timestamp": "2026-08-13T10:00:03Z",
                "type": "event_msg",
                "payload": {"type": "task_started"},
            },
            {
                "timestamp": "2026-08-13T10:00:05Z",
                "type": "response_item",
                "payload": {
                    "type": "function_call",
                    "name": "apply_patch",
                    "arguments": "child-evidence-artifact.md",
                    "call_id": "child-write",
                },
            },
            {
                "timestamp": "2026-08-13T10:00:05.500000Z",
                "type": "event_msg",
                "payload": {
                    "type": "agent_message",
                    "message": "Bounded evidence returned to Root.",
                },
            },
            {
                "timestamp": "2026-08-13T10:00:06Z",
                "type": "event_msg",
                "payload": {"type": "task_complete"},
            },
            {
                "timestamp": "2026-08-13T10:00:08Z",
                "type": "turn_context",
                "payload": {"turn_id": "turn-2", "model": "gpt-5.6-luna"},
            },
            {
                "timestamp": "2026-08-13T10:00:08Z",
                "type": "event_msg",
                "payload": {"type": "task_started"},
            },
            {
                "timestamp": "2026-08-13T10:00:09Z",
                "type": "event_msg",
                "payload": {
                    "type": "agent_message",
                    "message": "Related follow-up evidence returned to Root.",
                },
            },
            {
                "timestamp": "2026-08-13T10:00:10Z",
                "type": "event_msg",
                "payload": {"type": "task_complete"},
            },
        ]

        result = self.run_verifier(root_records, child_records)

        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertTrue(report["ok"])
        self.assertEqual(report["child_session_id"], "child-session")
        self.assertEqual(report["child_turn_count"], 2)
        self.assertTrue(all(report["checks"].values()), report)

    def test_rejects_child_descendant_spawn(self) -> None:
        root_records = [
            {
                "timestamp": "2026-08-13T10:00:01Z",
                "type": "response_item",
                "payload": {
                    "type": "function_call",
                    "name": "spawn_agent",
                    "arguments": '{"task_name":"docs_lane","agent_type":"docs-researcher","fork_turns":"none"}',
                    "call_id": "spawn-1",
                },
            }
        ]
        child_records = [
            {
                "timestamp": "2026-08-13T10:00:02Z",
                "type": "session_meta",
                "payload": {
                    "id": "child-session",
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
                "payload": {"turn_id": "turn-1"},
            },
            {
                "timestamp": "2026-08-13T10:00:03Z",
                "type": "event_msg",
                "payload": {"type": "task_started"},
            },
            {
                "timestamp": "2026-08-13T10:00:04Z",
                "type": "response_item",
                "payload": {
                    "type": "function_call",
                    "name": "spawn_agent",
                    "arguments": "{}",
                    "call_id": "descendant",
                },
            },
            {
                "timestamp": "2026-08-13T10:00:05Z",
                "type": "event_msg",
                "payload": {"type": "task_complete"},
            },
        ]

        result = self.run_verifier(root_records, child_records)

        self.assertEqual(result.returncode, 1)
        report = json.loads(result.stdout)
        self.assertFalse(report["ok"])
        self.assertFalse(report["checks"]["leaf_child"])


if __name__ == "__main__":
    unittest.main()
