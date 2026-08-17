# Evaluation Scenarios

Diverter release validation has three evidence seams:

1. **Preflight Delivery** — Hook input/output evidence proving the Session Contract is restored, every Root prompt gets one short Turn Reminder, and child prompts get none.
2. **Router Contract** — deterministic and prompt-level evidence for Task-shape Deliberation, one Routing Receipt, eligibility, Root/Child lanes, focused-skill support, `ask`/`auto`, role removal, native absence, leaf handoffs, reuse instructions, and Write Ownership.
3. **Native Lifecycle** — persisted Codex records proving what actually spawned and happened over time.

Final-response wording is never Native Lifecycle evidence.

## Clean Installation

Evaluate a fresh checkout through a newly created temporary `CODEX_HOME`. Install the checkout as a local marketplace plugin, keep the JSON-returned `installedPath`, install the selected Bundled Subagents, and verify the installed Hook and skills from that exact path.

Discovery fails if the evaluation home contains unrelated user skills, agents, plugins, memories, or configuration. Use a real non-empty workspace for branch and write scenarios. Do not reuse an empty checkout whose diff makes review behavior unobservable.

Required checks:

- `diverter` is visible;
- `diverter-mode` is present but explicit-only;
- `hooks/session_start.py` and `hooks/user_prompt_submit.py` are installed and trusted;
- every intended role exists under the isolated home;
- no unrelated role or skill is visible; and
- the installed plugin reports the release version.

## Installation Policy Choice

Run one fresh install choosing recommended `auto` and one choosing `ask`. Verify that the selected value is persisted and appears in a new SessionStart Contract. Missing or invalid configuration must load `ask`.

Do not infer a fresh-install choice from `diverter-mode.py init`; the installation conversation must explicitly ask and recommend `auto`.

## Root Turn Preflight Delivery

On the minimum supported released Codex version, capture immutable `UserPromptSubmit` command input and hook-completion evidence in a fresh installed task. Submit an ineligible first Root prompt and an eligible second Root prompt in the same task, then allow the eligible turn to create one native child.

Require all of the following:

- `SessionStart` injects the complete Session Contract and active policy at startup and again after compact;
- each Root `UserPromptSubmit` input omits `agent_id` and receives exactly one short Turn Reminder, never the full Contract;
- the ineligible first Root prompt emits exactly one `Routing: ROOT_ONLY — <reason>` receipt after Task-shape Deliberation;
- the eligible second Root prompt loads Diverter before other task work;
- the eligible second Root prompt uses its policy-specific Dispatch message as the single receipt and emits no separate eligibility message;
- the child `UserPromptSubmit` input contains `agent_id` and `agent_type`;
- `hooks/user_prompt_submit.py` exits successfully with zero stdout and zero model context for that child input; and
- InterAgentCommunication produces no extra `UserPromptSubmit` event.

Direct hook subprocess tests prove deterministic filtering, but they do not replace this released-runtime evidence. If the host cannot create or observe the child, record the run as blocked or failed; never infer the Child result from the official schema or Root behavior alone.

## Router Contract Suite

Run all `smoke: true` entries in [prompts.yaml](prompts.yaml) before the extended suite. Use a fresh task for each case and pass `session_context` as evaluator-controlled developer context, never as user text.

The paired controls are central:

- `gate-neg-focused-ui` ↔ `ultra-pos-ui-root-continues`;
- `gate-neg-focused-skill` ↔ `ultra-pos-focused-skill-support`;
- `neg-10` ↔ `ultra-pos-regression-root-continues`;
- `neg-02` ↔ `ultra-pos-disjoint-write` and `ultra-ownership-conflict`;
- `neg-04` ↔ `ultra-pos-doc-check` and `latent-pos-doc-contract`;
- `neg-10` ↔ `latent-pos-regression`;
- `gate-neg-focused-ui` ↔ `latent-pos-web-audit`; and
- `auto-idempotency` ↔ `ultra-reuse-same-scope`.

Explicit-lane implicit positives must name a bounded Child Lane and a distinct useful Root Lane. Explicit delegation positives must name the requested Child Lane but may state Root coordination and integration instead of inventing a Root Lane. The negative half must not invent a Root Lane merely to trigger.

Latent positives state only a realistic outcome, omit routing instructions, and require Task-shape Deliberation to derive a bounded Child Lane plus a distinct useful Root Lane.

For each Root user prompt, require one external routing result at most. Ordinary task-shape `ROOT_ONLY` uses one Routing Receipt; eligible work uses its policy-specific Dispatch Recommendation or Dispatch Announcement. Bypass, explicit opt-out, native absence, and missing-role fallbacks remain silent.

### Policy split

- `ask` approval: the recommendation precedes approval and the first native spawn occurs only afterward.
- `ask` refusal: zero spawn; Root continues.
- `auto`: Dispatch Announcement precedes native spawn in the same turn, asks no permission question, and identifies lineup, Work Mode, and Root activity: the Root Lane for implicit eligibility or coordination and integration for an explicit request without one.

After authorization, reuse the shared lifecycle primarily under `auto`; do not duplicate the complete matrix under `ask`.

### Missing role

Physically omit or remove the requested role from the isolated role home. Do not tell the model to “assume” it is unavailable. The role is removed from the lineup, Root covers the capability, and no substitute role is invented.

### Native absence diagnostic

Optionally use a controlled host/task surface without native role-specific spawning. Before activation there must be zero Routing Receipt, zero Dispatch Announcement, zero spawn, zero Diverter failure notice, and ordinary Root completion. If the test surface cannot actually hide the capability, record this diagnostic as `unknown`, not pass. This result does not gate the release.

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

After Dispatch Announcement, assign `test-automator` one deterministic nonzero operation, such as `/opt/anaconda3/bin/python3 -c 'raise SystemExit(23)'`, and retain structured tool output containing the nonzero exit code. Run it inside the ordinary writable workspace so the failure does not rely on role-level sandbox isolation or weakened permissions. Require a concise affected-lane report, preservation of successful work, Root takeover of the unfinished outcome, and no generic substitute child.

Prompt-injected failure prose, empty wrapper output, and child self-report are not failure evidence. The persisted nonzero operation must precede the affected-lane report and Root takeover.

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

For `ask`, put the exact second-turn marker `Dispatch Authorization` or `Dispatch Refused` in `--resume-prompt-file`. For the optional `native-absence` diagnostic, the driver disables the native multi-agent features. For `missing-role`, it physically omits the requested role installation. Never copy authentication into the clean home; if the supported host cannot access its existing account identity there, record the run as blocked. For interactive authentication, first run the driver with `--prepare-only`, log in to that exact `CODEX_HOME`, then rerun the identical command with `--run-prepared` in place of `--prepare-only`.

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

The verifier accepts real `custom_tool_call` / `exec` patch records, requires scoped Root progress and verification evidence, pairs child completion results by turn ID, checks normalized handoff scopes for duplicates, enforces exactly one child for the standard families, validates same-child follow-up ordering, freezes every Root turn's model and effort, and rejects hash changes or cross-lane mutations outside declared Write Ownership. Its root-only modes cover `ask-refused`, `native-absence`, and `missing-role`; `failure` accepts either a failed spawn with no Child rollout or a child-side abort/tool failure. Child tool failure evidence must match a preceding non-bookkeeping call, the report must identify the actual child task or role, post-failure verification must cover both prior Root work and takeover scope, and no substitute spawn is allowed.

An absent mandatory event is a failure, not an inferred pass.

## Primary Validation and Optional Diagnostics

Choose one non-Ultra Root configuration as primary. Freeze the Root model and reasoning setting, Codex version, plugin revision, installed role set, and workspace fixture.

Run the complete Router Contract and Native Lifecycle matrix in **three independent fresh sessions** on the primary model. Require 3/3 clean runs. Do not use majority voting or retry-until-pass.

Run the physical missing-role check once and require zero substitute role spawn.

Additional Root-model compatibility smokes may diagnose:

- eligibility;
- native role-specific dispatch;
- persisted role resolution;
- child result return; and
- Root integration.

Record exact diagnostic configurations and results. They do not gate the release or establish universal model parity. Native Absence Bypass probes are also diagnostic; when the absence premise cannot be established, record `unknown`.

## Release Gate

A release is a No-Go if any of these occur:

- a strict or paired negative dispatches;
- a prompt governed by ordinary or eligible routing emits a missing, duplicate, or wrong-kind Routing Receipt;
- `ask` spawns before approval or after refusal;
- `auto` asks permission or fails to announce before spawn;
- For implicit eligibility, the Root Lane is missing, passive, or duplicates the child;
- For explicit eligibility, Root coordination or integration responsibility is missing;
- an equivalent scope is spawned twice;
- a related follow-up creates a replacement child;
- a child spawns a descendant;
- a role is substituted after physical absence;
- write ownership overlaps without serialization;
- child evidence is not integrated and independently checked; or
- any primary-model run misses a mandatory lifecycle event.

Only after smoke passes may the extended routing suite run. Record every executed case in [results-template.md](results-template.md), preserve raw evidence, and label unrun or unobservable cases honestly.
