# Delegation Gate Paired Regression

- Date: 2026-07-28
- Branch: `fix/narrow-delegation-gate`
- Surface: fresh `codex exec` sessions
- Installation: local marketplace in an isolated `CODEX_HOME`
- Delegation policy: `ask`
- Worktree: repository checkout at the implementation commit

## Results

| ID | Expected | Observed | Result |
| --- | --- | --- | --- |
| `gate-neg-focused-ui` | Continue in the Root Session without mentioning Diverter or subagents | Answered the sidebar design question directly; did not mention Diverter or subagents | Pass |
| `gate-pos-ui-audit` | Activate Diverter for separable code-path, accessibility, and explicit Web-metric lanes | Proposed `code-mapper`, `reviewer`, and `web-performance-auditor` in `read-only` mode and requested Dispatch Authorization | Pass |

Both runs reported successful SessionStart Hook completion. The first isolated attempt lacked authentication and produced no model result; it was discarded as infrastructure setup, then both prompts were rerun successfully with the same isolated plugin installation.

This is the paired regression required by issue #4, not a full smoke or extended evaluation run.
