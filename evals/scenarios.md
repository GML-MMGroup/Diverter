# Evaluation Scenarios

This repository now evaluates the plugin shape, not only a single skill.

There are two prompt suites and two policy arms:

- `smoke`: the reduced first gate, marked with `smoke: true` in [prompts.yaml](prompts.yaml)
- `extended`: the full prompt pressure suite, run only after smoke passes
- `ask`: the default arm; cases without a `policy` field use this policy
- `auto`: the focused cases whose IDs start with `auto-`

CLI is the reproducible surface. Desktop is the manual experience surface.

## Discovery Check

Use an isolated home and install this checkout as a local marketplace so both skills and the SessionStart Hook are present:

The installed plugin must retain `hooks/session_start.py`; copying only `skills/` is not a valid policy test.

```bash
rm -rf /tmp/codex-subagent-eval/skill
rm -rf /tmp/codex-subagent-eval/marketplace
mkdir -p /tmp/codex-subagent-eval/skill
mkdir -p /tmp/codex-subagent-eval/marketplace/plugins
DIVERTER_PLUGIN_ROOT="$(pwd)"
cp -R "$DIVERTER_PLUGIN_ROOT" /tmp/codex-subagent-eval/marketplace/plugins/diverter
cp -R "$DIVERTER_PLUGIN_ROOT/evals/local-marketplace/.agents" \
  /tmp/codex-subagent-eval/marketplace/.agents
CODEX_HOME=/tmp/codex-subagent-eval/skill \
codex plugin marketplace add /tmp/codex-subagent-eval/marketplace
CODEX_HOME=/tmp/codex-subagent-eval/skill \
codex plugin add diverter@diverter-local-eval --json \
  > /tmp/codex-subagent-eval/plugin-install.json
cat /tmp/codex-subagent-eval/plugin-install.json
INSTALLED_PATH="$(python3 -c 'import json; print(json.load(open("/tmp/codex-subagent-eval/plugin-install.json"))["installedPath"])')"
CODEX_HOME=/tmp/codex-subagent-eval/skill \
python3 "$DIVERTER_PLUGIN_ROOT/scripts/install-agent-roles.py" --overwrite
```

Keep the `installedPath` returned by `codex plugin add`. Confirm the implicit core skill is visible and the explicit-only Mode Control skill is present in the installed plugin:

```bash
CODEX_HOME=/tmp/codex-subagent-eval/skill \
codex debug prompt-input | rg "diverter"
test -f "$INSTALLED_PATH/skills/diverter-mode/SKILL.md"
```

Pass condition:

- `diverter` appears
- the `diverter-mode` file check succeeds; it is intentionally absent from implicit prompt input
- no `failed to load skill` error appears

## CLI Baseline

Create an isolated home without plugin skills:

```bash
rm -rf /tmp/codex-subagent-eval/baseline
mkdir -p /tmp/codex-subagent-eval/baseline
```

Run the prompts marked `smoke: true` first:

```bash
CODEX_HOME=/tmp/codex-subagent-eval/baseline \
codex exec -s read-only "REPLACE_WITH_PROMPT"
```

Record raw output and score it with [rubric.md](rubric.md).

## CLI Plugin Smoke

Use the discovered skill home from the discovery check:

```bash
CODEX_HOME=/tmp/codex-subagent-eval/skill \
codex exec --dangerously-bypass-hook-trust -s read-only "REPLACE_WITH_PROMPT"
```

Run only prompts marked `smoke: true`.

`--dangerously-bypass-hook-trust` is limited to this isolated automation home after reviewing the local Hook source. Interactive installation still requires normal `/hooks` review and trust.

Initialize the default `ask` arm before running it:

```bash
CODEX_HOME=/tmp/codex-subagent-eval/skill \
python3 scripts/diverter-mode.py init
```

For the focused `auto-*` cases, set the isolated home to `auto` and start a fresh CLI task for each prompt:

```bash
CODEX_HOME=/tmp/codex-subagent-eval/skill \
python3 scripts/diverter-mode.py auto
```

For cases with a `session_context` field, pass that value as evaluator-controlled developer context rather than appending it to the user prompt:

```bash
CODEX_HOME=/tmp/codex-subagent-eval/skill \
codex exec --dangerously-bypass-hook-trust -s read-only \
  -c "developer_instructions='REPLACE_WITH_SESSION_CONTEXT'" \
  "REPLACE_WITH_PROMPT"
```

This is required for the Native Proactive Delegation, failure-recovery, and compact/resume checks. The provided focused context strings contain no single quotes; if a future case does, encode it as a valid TOML string before passing `-c`.

Run `auto-pos-02` in a disposable writable checkout so the mixed workflow and CLI worker state can execute without touching the development repository:

```bash
AUTO_WRITE_WORKSPACE=/tmp/codex-subagent-eval/auto-pos-02-workspace
rm -rf "$AUTO_WRITE_WORKSPACE"
cp -R "$DIVERTER_PLUGIN_ROOT" "$AUTO_WRITE_WORKSPACE"
CODEX_HOME=/tmp/codex-subagent-eval/skill \
codex exec --dangerously-bypass-hook-trust -s workspace-write \
  --add-dir /tmp/codex-subagent-eval/skill \
  -C "$AUTO_WRITE_WORKSPACE" \
  "Add targeted regression tests for the falsey-value settings save bug in evals/fixtures/settings-save/settings_save.py, but first map the exact behavior boundary."
```

All other focused `auto-*` cases remain read-only.

Smoke pass gates:

- positive/edge trigger rate is at least `75%`
- negative false positive rate is exactly `0%`
- delegation-policy violations are exactly `0`
- sanitized failure-reporting violations are exactly `0`
- recommended lineup count above 4 is exactly `0`
- explicit fallback handling passes for `edge-02`

## CLI Extended Suite

Run the full prompt suite only after smoke passes.

Extended pass gates remain stricter:

- positive/edge trigger rate is at least `80%`
- negative false positive rate is at most `15%`
- delegation-policy violations are exactly `0`
- sanitized failure-reporting violations are exactly `0`
- recommended lineup count above 4 is exactly `0`
- explicit fallback handling passes at least `90%` of relevant cases

## Desktop Manual Validation

Desktop validation is a smoke test for:

- plugin visibility
- entry skill implicit triggering
- user-facing wording
- policy-appropriate ask or auto behavior
- negative-case silence

Recommended prompt subset:

- `pos-01`
- `pos-07`
- `pos-09`
- `pos-11`
- `neg-03`
- `neg-08`
- `edge-06`

Manual setup:

1. Enable this repository as a Codex plugin.
2. Confirm the plugin manifest points at `skills/`.
3. Start a new Codex Desktop session.
4. Verify that `diverter` is visible in the available skills list.
5. Run the prompt subset.
6. Verify that wording matches [../skills/diverter/references/delegation-contract.md](../skills/diverter/references/delegation-contract.md).

## Two-Step Ask-Policy Checks

Use these follow-up turns after the first smoke pass.

### Delegated Handoff Recursion Check

Run `neg-07`.

Pass condition:
- Codex does not suggest another subagent lineup
- Codex does not request another Dispatch Authorization
- Codex treats the prompt as an already-approved handoff and proceeds within the stated constraints

### Reject Path

1. Run `edge-03`.
2. Confirm that Codex suggests a lineup and asks permission.
3. Reply:

   ```text
   No, continue without subagents.
   ```

4. Pass condition:
   - Codex continues in the main thread
   - Codex does not immediately re-suggest

### Approval Path

1. Run `edge-04`.
2. Confirm that Codex suggests a lineup and asks permission.
3. Reply:

   ```text
   Yes, use those subagents.
   ```

4. Pass condition:
   - delegated exploration stays read-first
   - write-capable work stays bounded
   - the main thread summarizes results instead of dumping raw logs

## Subagent-Assisted Evaluation

Subagents may help evaluate, but should not edit repository files.

Recommended split:

- `test-automator`: run CLI smoke shards only when each runner has an independent authenticated `CODEX_HOME`
- `reviewer`: independently score outputs against [rubric.md](rubric.md)
- `knowledge-synthesizer`: summarize failure patterns across evaluator notes

Do not copy the same `auth.json` into multiple parallel `CODEX_HOME` directories for concurrent `codex exec` runs. Parallel refreshes can invalidate or reuse the same token. If only one authenticated home is available, run CLI prompts sequentially and use subagents only for read-only scoring of completed raw outputs.

The main thread owns final judgment and writes result files.

## Recording Results

Use [results-template.md](results-template.md) for each evaluation round.

Recommended naming:

- `evals/results/round-01.md`
- `evals/results/round-02.md`

Record the suite (`smoke` or `extended`) and installation mode (`plugin`, `$CODEX_HOME/skills`, symlink, or legacy root skill). Do not change the prompt set during a round. If you revise the plugin or skills, start a new results file.
