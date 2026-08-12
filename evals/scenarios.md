# Evaluation Scenarios

V0.4.0 has two evidence seams:

1. **Router Contract** — deterministic and prompt-level evidence for eligibility, Root/Child lanes, focused-skill support, `ask`/`auto`, role removal, native absence, leaf handoffs, reuse instructions, and Write Ownership.
2. **Native Lifecycle** — persisted Codex records proving what actually spawned and happened over time.

Final-response wording is never Native Lifecycle evidence.

## Clean Installation

Evaluate a fresh checkout through a newly created temporary `CODEX_HOME`. Install the checkout as a local marketplace plugin, keep the JSON-returned `installedPath`, install the selected Bundled Subagents, and verify the installed Hook and skills from that exact path.

Discovery fails if the evaluation home contains unrelated user skills, agents, plugins, memories, or configuration. Use a real non-empty workspace for branch and write scenarios. Do not reuse an empty checkout whose diff makes review behavior unobservable.

Required checks:

- `diverter` is visible;
- `diverter-mode` is present but explicit-only;
- `hooks/session_start.py` is installed and trusted;
- every intended role exists under the isolated home;
- no unrelated role or skill is visible; and
- the installed plugin reports version `0.4.0`.

## Installation Policy Choice

Run one fresh install choosing recommended `auto` and one choosing `ask`. Verify that the selected value is persisted and appears in a new SessionStart gate. Missing or invalid configuration must load `ask`.

Do not infer a fresh-install choice from `diverter-mode.py init`; the installation conversation must explicitly ask and recommend `auto`.

## Router Contract Suite

Run all `smoke: true` entries in [prompts.yaml](prompts.yaml) before the extended suite. Use a fresh task for each case and pass `session_context` as evaluator-controlled developer context, never as user text.

The paired controls are central:

- `gate-neg-focused-ui` ↔ `ultra-pos-ui-root-continues`;
- `gate-neg-focused-skill` ↔ `ultra-pos-focused-skill-support`;
- `neg-10` ↔ `ultra-pos-regression-root-continues`;
- `neg-02` ↔ `ultra-pos-disjoint-write` and `ultra-ownership-conflict`;
- `neg-04` ↔ `ultra-pos-doc-check`; and
- `auto-idempotency` ↔ `ultra-reuse-same-scope`.

The positive half must name a bounded Child Lane and a distinct useful Root Lane. The negative half must not invent a Root Lane merely to trigger.

### Policy split

- `ask` approval: the recommendation precedes approval and the first native spawn occurs only afterward.
- `ask` refusal: zero spawn; Root continues.
- `auto`: Dispatch Announcement precedes native spawn in the same turn, asks no permission question, and identifies lineup, Root Lane, and Work Mode.

After authorization, reuse the shared lifecycle primarily under `auto`; do not duplicate the complete matrix under `ask`.

### Missing role

Physically omit or remove the requested role from the isolated role home. Do not tell the model to “assume” it is unavailable. The role is removed from the lineup, Root covers the capability, and no substitute role is invented.

### Native absence

Use a controlled host/task surface without native role-specific spawning. Before activation there must be zero Dispatch Announcement, zero spawn, zero Diverter failure notice, and ordinary Root completion. If the test surface cannot actually hide the capability, record this case as `unknown`, not pass.

## Native Lifecycle Scenario Set

Capture immutable root and child rollout JSONL for every native run. Retain the raw evidence privately and publish only sanitized IDs, timestamps, event types, role/model facts, and artifact hashes.

### Family 1: one child plus Root

Use a domain-neutral task with two explicit deliverables. Require:

- one role-specific spawn using `agent_type` and `fork_turns: "none"`;
- persisted child role metadata;
- spawn return before child completion;
- substantive non-orchestration Root work during the child-active interval;
- a bounded child result;
- Root integration plus a proportional independent verification action;
- no equivalent duplicate spawn; and
- no child descendant.

### Family 2: related follow-up

After the initial child turn, issue a related follow-up. Require the same canonical child session ID, a new turn ID in that session, a Root follow-up targeted to the same child path, zero equivalent second spawn, and zero descendants.

Same-child reuse is a hard release gate.

### Family 3: bounded Write Ownership

Use two domain-neutral mutable Markdown artifacts. Root owns one; the child owns the other. Use observable patch operations so the rollout can attribute each write. Require:

- explicit disjoint scopes before dispatch;
- Root and child writes only inside their owned artifacts;
- no overlapping or unauthorized write;
- Root integration and verification after the child result; and
- before/after artifact hashes in the evidence package.

If a scenario intentionally overlaps ownership, it must serialize rather than run both writers concurrently.

### Family 4: post-announcement failure

Create a deterministic native child failure after Dispatch Announcement without weakening permissions. Require a concise affected-lane report, preservation of successful work, Root takeover of the unfinished outcome, and no generic substitute child.

Prompt-injected failure prose is only a Router Contract probe and cannot pass this family.

## Lifecycle Verifier

Use the real driver for release evidence. It creates a clean `CODEX_HOME`, installs the current committed revision through a local marketplace, installs the selected native role, sets the policy, runs a persisted `codex exec` session, captures Root/child rollouts plus before/after workspace hashes, and invokes the verifier:

```bash
python3 scripts/run-native-lifecycle.py \
  --workspace /absolute/path/to/non-empty-fixture \
  --prompt-file /absolute/path/to/family-1-prompt.txt \
  --codex-home /absolute/path/to/new-empty-codex-home \
  --evidence-dir /absolute/path/to/new-empty-evidence-dir \
  --expected-role docs-researcher \
  --policy auto \
  --model gpt-5.6-terra \
  --reasoning-effort high \
  --root-progress-scope root-brief.md \
  --verification-scope verify-integrated-brief
```

For `ask`, put the exact second-turn marker `Dispatch Authorization` or `Dispatch Refused` in `--resume-prompt-file`. For `native-absence`, the driver disables the native multi-agent features. For `missing-role`, it physically omits the requested role installation. Never copy authentication into the clean home; if the supported host cannot access its existing account identity there, record the run as blocked.

The parser can also verify retained rollout evidence directly:

```bash
python3 scripts/verify-native-lifecycle.py \
  --root-rollout /absolute/path/to/root.jsonl \
  --child-rollout /absolute/path/to/child.jsonl \
  --expected-role docs-researcher \
  --scenario normal \
  --policy auto \
  --root-progress-scope root-brief.md \
  --verification-scope verify-integrated-brief \
  --expected-root-model gpt-5.6-terra \
  --expected-root-effort high \
  --require-followup
```

For the Write Ownership family, also pass the declared artifact strings:

```bash
python3 scripts/verify-native-lifecycle.py \
  --root-rollout /absolute/path/to/root.jsonl \
  --child-rollout /absolute/path/to/child.jsonl \
  --expected-role test-automator \
  --scenario normal \
  --policy auto \
  --root-progress-scope root-brief.md \
  --verification-scope verify-integrated-brief \
  --expected-root-model gpt-5.6-terra \
  --expected-root-effort high \
  --root-write-scope root-brief.md \
  --child-write-scope child-evidence.md \
  --ownership-manifest /absolute/path/to/ownership-manifest.json
```

The verifier accepts real `custom_tool_call` / `exec` patch records, requires scoped Root progress and verification evidence, pairs child completion results by turn ID, checks normalized handoff scopes for duplicates, enforces exactly one child for the standard families, validates same-child follow-up ordering, freezes every Root turn's model and effort, and rejects hash changes or cross-lane mutations outside declared Write Ownership. Its root-only modes cover `ask-refused`, `native-absence`, and `missing-role`; `failure` accepts either a failed spawn with no Child rollout or a child-side abort/tool failure, then requires a marked affected-lane report, Root takeover evidence, and no substitute spawn.

An absent mandatory event is a failure, not an inferred pass.

## GPT-5.6 Validation Matrix

Choose at least one available non-Ultra, non-Sol GPT-5.6 Root model as primary. Freeze the Root model and reasoning setting, Codex version, plugin revision, installed role set, and workspace fixture.

Run the complete Router Contract and Native Lifecycle matrix in **three independent fresh sessions** on the primary model. Require 3/3 clean runs. Do not use majority voting or retry-until-pass.

For every other GPT-5.6 Root model available in the release environment, run one compatibility smoke proving:

- eligibility;
- native role-specific dispatch;
- persisted role resolution;
- child result return; and
- Root integration.

## Release Gate

V0.4.0 is a No-Go if any of these occur:

- a strict or paired negative dispatches;
- `ask` spawns before approval or after refusal;
- `auto` asks permission or fails to announce before spawn;
- the Root Lane is missing, passive, or duplicates the child;
- an equivalent scope is spawned twice;
- a related follow-up creates a replacement child;
- a child spawns a descendant;
- a role is substituted after physical absence;
- native absence activates Diverter;
- write ownership overlaps without serialization;
- child evidence is not integrated and independently checked; or
- any primary-model run misses a mandatory lifecycle event.

Only after smoke passes may the extended routing suite run. Record every executed case in [results-template.md](results-template.md), preserve raw evidence, and label unrun or unobservable cases honestly.
