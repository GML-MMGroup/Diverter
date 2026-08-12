# Load a user-level delegation policy at session start

Diverter will keep one core delegation skill and select its behavior through a user-level Delegation Policy stored at `${CODEX_HOME:-$HOME/.codex}/diverter/config.json`. The explicit-only `$diverter-mode` control changes that policy, while the existing `SessionStart` Hook loads it as developer context: `ask` proposes one lineup and waits for approval, and `auto` announces one lineup and dispatches it immediately. Missing or invalid configuration falls back to `ask`, installation initializes `ask` without overwriting an existing valid preference, and changes apply at the next `SessionStart`. This replaces the advisory-only gate while avoiding two competing behavior skills or project-level configuration precedence.

The fresh-install initialization clause is superseded by ADR-0008. Missing or invalid configuration still falls back to `ask`.
