#!/usr/bin/env python3
"""Inject the Diverter Delegation Gate into a root Codex session."""

import json
import os
from pathlib import Path


def load_policy() -> str:
    codex_home = Path(os.environ.get("CODEX_HOME", "~/.codex")).expanduser()
    path = codex_home / "diverter" / "config.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        policy = data.get("delegation_policy") if isinstance(data, dict) else None
    except (OSError, UnicodeError, json.JSONDecodeError, TypeError):
        return "ask"
    return policy if policy in {"ask", "auto"} else "ask"


def build_gate(policy: str) -> str:
    return f"""## Diverter Delegation Gate

delegation_policy: {policy}

This gate applies only to the main/frontline Codex agent before starting a user-level task.

If the current user message explicitly invokes `$diverter-mode`, execute Mode Control directly. Do not invoke `$diverter`, evaluate delegation, or spawn subagents for that message.

If the current task message explicitly says this is a delegated subagent task, or includes `delegation_context: delegated-subagent`, do not invoke `$diverter`, suggest another lineup, or request Dispatch Authorization. Execute only the assigned handoff within its constraints.

If higher-priority session instructions state that proactive multi-agent delegation is active, stop evaluating this gate. Do not invoke or mention Diverter. Continue under the native policy.

An explicit `$diverter` invocation or explicit request to use subagents is eligible regardless of the implicit threshold, subject to the bypasses above.

Otherwise, invoke `$diverter` only when the task has at least two separable work or evidence lanes, or one concrete high-risk specialist boundary: security, authentication, authorization, secrets, or tool permissions; regression proof or critical test coverage for a known defect; explicit Web performance metrics; or a release-readiness quality gate.

For implicit activation, do not invoke `$diverter` for vague risk language, focused single-domain or single-component work, one-path explanations or fact lookups, tightly coupled work, or work already owned by an explicitly selected focused skill. An explicit user request for subagents or a delegation request from the focused skill still qualifies.

If eligible, invoke `$diverter` first and apply the loaded Delegation Policy. An explicit user instruction may override that policy for the current task without changing persistent configuration. If ineligible, continue silently in the main thread.

Use Sanitized Failure Reporting if loading or using Diverter fails. If an internal failure recovers successfully, continue silently. If an implicit Diverter load fails, say that Diverter could not be loaded and the task is continuing in the main thread. If an explicitly requested Diverter load fails, report that briefly and ask whether to continue in the main thread. If user action is required, explain the problem and the required action. Never expose skill aliases, plugin cache paths, `SKILL.md` loading, or retry steps.
"""


if __name__ == "__main__":
    print(build_gate(load_policy()), end="")
