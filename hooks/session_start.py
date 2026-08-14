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

Only affirmative delegation intent with at least one recognized signal is an Explicit Delegation Request: `$diverter`, `subagent`, `delegate`, `委派`, `子代理`, or a named installed agent role. Mere mention, quotation, explanation, or negation does not qualify. Scheduling words alone do not qualify, including concurrent, parallel, or at the same time.

An Explicit Delegation Request is eligible regardless of the implicit benefit threshold, subject to the bypasses above.

Otherwise, invoke `$diverter` only when the task has one bounded independent Child Lane and one distinct useful Root Lane that can make substantive progress while the child runs. The lanes must be non-duplicative, materially beneficial, and safe under the task's read/write ownership.

No effective Root Lane means no implicit delegation. Waiting, supervision, or repeating the Child Lane does not count. Do not invoke `$diverter` for vague risk language, trivial or strongly sequential work, one-path fact lookups, duplicate investigation, tightly coupled writes, or overlapping write ownership.

An explicitly selected focused skill may retain its core workflow and Root Lane while Diverter supplies a Supporting Child for a separate, non-duplicative deliverable, when higher-priority and skill-specific constraints allow it.

Before mentioning Diverter, confirm that native role-specific subagent dispatch is available for the requested installed role. If native subagent dispatch is unavailable, or no useful selected role is available, continue silently in the Root Session. Do not announce a backend failure or ask the user how to proceed.

If eligible, invoke `$diverter` first and apply the loaded Delegation Policy. An explicit user instruction may override that policy for the current task without changing persistent configuration. If ineligible, continue silently in the Root Session.

Use Sanitized Failure Reporting if loading or using Diverter fails. If an internal failure recovers successfully, continue silently. If an implicit Diverter load fails, say that Diverter could not be loaded and the task is continuing in the Root Session. If an explicitly requested Diverter load fails, report that briefly and ask whether to continue in the Root Session. If user action is required, explain the problem and the required action. Never expose skill aliases, plugin cache paths, `SKILL.md` loading, or retry steps.
"""


if __name__ == "__main__":
    print(build_gate(load_policy()), end="")
