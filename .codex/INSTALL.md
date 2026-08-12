# Installing Diverter for Codex

Diverter distills Ultra-style task decomposition and role routing into ordinary GPT-5.6 Codex sessions through native role-specific subagents and a user-level `ask` or `auto` Delegation Policy.

This file is the only supported installation entry. Follow it as one agent-led flow; do not ask the user to run the role installer manually.

## Prerequisites

- Codex with plugin and Hook support
- Python 3.11+

## Installation

### 1. Add the repository marketplace

```bash
codex plugin marketplace add GML-MMGroup/Diverter
```

### 2. Install the plugin

```bash
codex plugin add diverter@diverter --json
```

Keep the returned `installedPath`; use that exact absolute path as `DIVERTER_PLUGIN` below. The documented cache layout is `$MARKETPLACE_NAME/$PLUGIN_NAME/$VERSION`; repeated directory names are valid when the marketplace and plugin names match. Do not infer a versioned cache directory because Git-backed marketplace plugins may use `local` as their cache version.

### 3. Choose the global Bundled Subagents

Show this complete table before asking which roles to install. Role numbers are stable and must not be reassigned.

| # | Role | GPT-5.6 model | Reasoning effort | Description |
|---:|---|---|---|---|
| 1 | `code-mapper` | `gpt-5.6-terra` | `high` | Trace code paths, files, symbols, and ownership boundaries. |
| 2 | `search-specialist` | `gpt-5.6-luna` | `medium` | Gather focused evidence from repositories or external sources. |
| 3 | `docs-researcher` | `gpt-5.6-luna` | `high` | Verify official APIs, versions, and documented guarantees. |
| 4 | `knowledge-synthesizer` | `gpt-5.6-luna` | `high` | Reconcile long or conflicting findings without inventing facts. |
| 5 | `task-distributor` | `gpt-5.6-sol` | `medium` | Split broad goals into bounded work packages. |
| 6 | `reviewer` | `gpt-5.6-sol` | `medium` | Review correctness, regressions, contracts, and maintainability. |
| 7 | `security-auditor` | `gpt-5.6-sol` | `high` | Audit trust boundaries, auth, secrets, and agent-tool safety. |
| 8 | `test-engineer` | `gpt-5.6-luna` | `xhigh` | Design minimal test coverage for behavior and risk. |
| 9 | `test-automator` | `gpt-5.6-terra` | `xhigh` | Add bounded regression tests after behavior is clear. |
| 10 | `web-performance-auditor` | `gpt-5.6-luna` | `xhigh` | Audit Web performance evidence and Core Web Vitals risks. |

Warn that each selected role overwrites an existing same-name global Agent file; unselected files remain untouched.

If `request_user_input` is available, ask one structured question with these options and allow the client's free-form choice:

- `Install recommended set (Recommended)` — roles 1, 3, 6, 7, 8, and 9.
- `Install all roles` — all ten roles.

Otherwise ask for `recommended`, `all`, or a custom role selection. Interpret the choice naturally, deduplicate it, and ask one concise follow-up only when the selection is unclear.

### 4. Run the Role Installer for the user

Set `DIVERTER_PLUGIN` to the exact `installedPath` returned in step 2. For example:

```bash
DIVERTER_PLUGIN="/absolute/path/from/the-installedPath-field"
```

Run the installer with `--overwrite` and one `--role` per selected role. For the recommended set:

```bash
python3 "$DIVERTER_PLUGIN/scripts/install-agent-roles.py" --overwrite \
  --role code-mapper \
  --role docs-researcher \
  --role reviewer \
  --role security-auditor \
  --role test-engineer \
  --role test-automator
```

The installer writes only to the global Agent directory under the effective Codex home.

### 5. Choose the Delegation Policy

Ask the user to choose one policy. **Recommended: `auto`** for proactive dispatch; `ask` remains available for approval-first use. Do not silently select a fresh-install policy.

If `request_user_input` is available, ask one structured question with `auto (Recommended)` and `ask`. Otherwise ask the same choice plainly. Then run exactly the selected operation:

```bash
python3 "$DIVERTER_PLUGIN/scripts/diverter-mode.py" auto
# or
python3 "$DIVERTER_PLUGIN/scripts/diverter-mode.py" ask
```

Keep the returned `delegation_policy` for the final response. Missing or invalid configuration still resolves safely to `ask` at SessionStart until the user selects a valid policy.

### 6. Trust the SessionStart Hook

After the selected roles are installed, tell the user to open `/hooks`, review the Diverter `SessionStart` command, and trust it before starting a new Codex task. Do not pause role installation while waiting for Hook trust. Codex's normal warning and fail-open behavior applies when the Hook is untrusted, skipped, times out, or fails.

### 7. Verify and finish

Verify the plugin and selected roles:

```bash
test -f "$DIVERTER_PLUGIN/skills/diverter/SKILL.md"
test -f "$DIVERTER_PLUGIN/skills/diverter-mode/SKILL.md"
test -f "${CODEX_HOME:-$HOME/.codex}/agents/code-mapper.toml"
test -f "${CODEX_HOME:-$HOME/.codex}/diverter/config.json"
```

End with the following fixed structure, translated into the user's language when needed. Keep commands and policy names exact:

```text
Diverter is installed in the selected `<policy>` mode.

Before using it, open `/hooks`, review Diverter's `SessionStart` Hook,
and trust it. Then start or reopen a task.

- `ask` — proposes one lineup and waits for approval.
- `auto` — announces one lineup and dispatches it immediately for any Work Mode.

Change the mode with:
- `$diverter-mode auto`
- `$diverter-mode ask`
- `$diverter-mode status`

Mode changes apply at the next `SessionStart`.
```

Replace `<policy>` with the exact selected `delegation_policy` returned by the command.

## Updating

Refresh the marketplace and reinstall the plugin:

```bash
codex plugin marketplace upgrade diverter
codex plugin add diverter@diverter --json
```

Use the newly returned `installedPath`. Repeat the role selection and run the current release's Role Installer so selected global roles receive the new definitions. Run `python3 "$DIVERTER_PLUGIN/scripts/diverter-mode.py" init`; updates preserve an existing valid policy and safely initialize missing configuration to `ask`. If Codex marks the changed Hook for review, ask the user to repeat `/hooks` trust before starting a new task. Report the policy returned by `init`.
