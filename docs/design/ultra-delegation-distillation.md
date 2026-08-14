---
status: accepted
---

# Distill Ultra-style delegation into Diverter

This document records the agreed product direction for relaxing Diverter v0.3.2's delegation threshold and adopting the task-splitting, routing, coordination, and result-integration discipline associated with Codex Ultra. It is a design record, not an implementation plan or a claim of Ultra-equivalent model capability.

## Product definition

Suggested short positioning:

> Diverter distills Ultra's subagent decomposition and routing capability for non-Ultra Codex sessions.

Suggested user-facing expansion:

> Without enabling Ultra, Diverter helps non-Ultra Codex sessions decide when to delegate, which specialist to use, what the Root Session should continue doing, and how delegated results should be verified and integrated.

Here, **distillation** means extracting and encoding orchestration rules and workflow discipline. It does not mean model-weight distillation, copying Ultra's private scheduler, or making a lower-effort model reason identically to Ultra.

## Model scope

Diverter does not prescribe or allowlist the Root Session model. Eligibility depends on native orchestration ownership, the role-spawn interface, the installed role, and the Delegation Policy rather than a Root-model identifier.

- A non-Ultra Codex session may use Diverter when the required native interface is available.
- Bundled Subagents retain their curated Static Model Mapping unless a separate decision changes it.
- Native Proactive Delegation remains the Orchestration Owner when Codex explicitly enables it; Diverter continues to step aside rather than competing with it.
- Additional Root-model compatibility runs may be recorded as diagnostics without becoming release gates or claims of universal parity.

This scope keeps Root eligibility separate from the bundled child-role model mapping.

## Settled decisions

### D1 — Installation mode choice

Fresh installations explicitly ask the user to choose a Delegation Policy. `auto` is the recommended option for the Ultra-distilled proactive experience, while `ask` remains available for approval-first operation. Diverter does not silently default a user to `auto`; missing or invalid configuration still resolves safely to `ask`.

### D1a — Recommended auto retains one meaning

Recommending `auto` does not create a hidden `auto-safe` tier. After its Dispatch Announcement, `auto` continues to authorize suitable `read-only`, `mixed`, and `write-capable` delegation; the user task, Codex permissions, sandbox, explicit ownership, and write serialization remain the safety boundaries.

### D2 — An effective Root lane is mandatory

Every implicit dispatch requires distinct, useful Root work that can progress while a child runs. Independent specialist work without an effective Root lane does not qualify for implicit delegation; an explicit user request may still authorize it within the normal safety boundaries.

### D3 — Focused skills may receive supporting children

An explicitly selected focused skill retains the Root lane and owns the core workflow. Diverter may implicitly supply a supporting child when that child has a separate deliverable, does not duplicate or replace the focused skill, and does not violate the focused skill's own delegation constraints.

### D4a — Reuse related native child context

Related follow-up work should return to the same native child whenever it remains available. A new child is justified only by a materially different scope; duplicate dispatch is not a substitute for reuse.

### D6 — Diverter children are leaves

Diverter-dispatched children never create descendants. The Root Session remains the sole Orchestration Owner for the delegated workflow, consistent with the existing recursion guard.

### D4b — Use only the Native Subagent Backend

The CLI Worker Backend was a compatibility path for an earlier period when native Codex subagent execution was unreliable. This redesign removes that path and requires the Native Subagent Backend, while retaining bundled role definitions, their curated Static Model Mapping, and the Role Installer for native `agent_type` discovery.

### D4c — Stay inert when native dispatch is unavailable

When the native subagent capability is unavailable, Diverter does not activate, report a backend problem, or ask how to continue. The Root Session completes the task normally, so Diverter behaves as though it were absent even when the task would otherwise qualify. This is a pre-activation bypass, not a recovered execution failure under Sanitized Failure Reporting.

If an individual role is unavailable, Diverter removes it from the lineup and the Root Session covers that capability. If no eligible role remains, the task stays entirely in the Root Session.

### D4d — Use the minimal native capability contract

Native dispatch requires a visible role-selecting spawn interface that supports `agent_type`, `fork_turns: "none"`, and the requested installed role. Diverter does not require runtime `model` or `reasoning_effort` selectors: the Bundled Subagent definition owns those values through its Static Model Mapping.

### D4e — Hard-cut the CLI backend in v0.4.0

v0.4.0 removes the CLI runner and its compatibility contracts without a deprecation release. Diverter will not add another fallback executor; environments without the required native capability receive the inert behavior defined by D4c.

### D4f — Make same-child reuse a release gate

v0.4.0 must prove through a real native lifecycle that a related follow-up returns to the same child identity. Prompt wording or final-response claims are insufficient; without this evidence, same-child reuse cannot ship as a supported Ultra-distilled behavior.

### D4g — Report failures after an announced dispatch

Native capability absence before activation remains silent under D4c. Once Diverter has announced that a child will run, a spawn or child failure changes the announced plan: report the affected lane briefly under Sanitized Failure Reporting and let the Root Session absorb the unfinished outcome.

### D7 — Default to the smallest sufficient lineup

Implicit delegation starts with one child plus the Root lane. Add a child only for another necessary, independent, non-duplicative deliverable; the four-role limit remains a safety cap rather than a utilization target.

### D8 — Preserve outcome-bounded autonomy

Diverter defines outcome and coordination invariants without prescribing a closed catalog of valid actions. The Root Session decides how to advance its lane and how to verify and integrate child work for the task at hand, provided its progress is substantive, distinct from the Child lane, traceable to the final outcome, and checked in proportion to risk.

This standard is intentionally domain-neutral. Examples may illustrate it, but the prompt must not turn examples from coding, research, writing, or any other domain into an exhaustive checklist.

### D9 — Make write ownership explicit

Every write-capable lane owns an explicit mutable artifact or bounded scope. Overlapping writes are serialized; parallel writes are allowed only when ownership is clearly disjoint. Diverter relies on declared ownership and existing platform controls rather than introducing a lock manager.

### D5a — Use capability-first public messaging

README, release notes, and other user-facing promotion should state the verified capabilities Diverter provides in direct, positive language. Public copy should not be organized around limitation lists or cannot-do disclaimers; internal design and evaluation records still preserve the evidence boundaries that keep those positive claims truthful.

### D5b — Verify write ownership before v0.4.0

Because `auto` supports bounded write-capable delegation, the v0.4.0 release gate includes at least one domain-neutral mutable-artifact lifecycle case. The evidence must show explicit ownership and either disjoint parallel writes or serialized overlapping writes without turning the product prompt into a coding-specific checklist.

### D5c — Gate on one frozen primary Root configuration

Run the complete native lifecycle gate on one frozen non-Ultra Root configuration. Additional Root-model compatibility smokes may cover eligibility, native dispatch, role resolution, and result return, but they are diagnostic evidence rather than release requirements.

### D5d — Use the minimum complete native lifecycle set

The v0.4.0 release gate contains four real native lifecycle families:

1. a normal one-child-plus-Root task proving dispatch, concurrent Root progress, leaf-child behavior, result integration, and proportional verification;
2. a related follow-up proving the same canonical child session is reused without a duplicate spawn;
3. a domain-neutral mutable-artifact task proving bounded Write Ownership and final integration; and
4. a failure after Dispatch Announcement proving concise reporting and Root takeover of the affected outcome.

Physical missing-role removal remains a required contract check. A separate pre-activation run may probe Native Absence Bypass as a diagnostic without treating it as a full lifecycle family or a release gate. Focused-skill support, eligibility neighbors, and other routing classifications remain contract and routing-evaluation cases rather than separate runtime families.

### D5e — Require three clean primary lifecycle runs

Run the complete lifecycle matrix in three independent fresh sessions on the frozen primary Root configuration and require 3/3 clean passes. A 2/3 majority does not pass: any missing mandatory event, duplicate dispatch, descendant spawn, or unauthorized write is a release No-Go until the affected behavior is corrected and revalidated.

All static contract tests and required missing-role checks must pass. Additional Root-model smokes and Native Absence Bypass probes are recorded as diagnostics and do not gate the release.

### D5f — Split policy evidence at Dispatch Authorization

Test the distinct authorization behavior of both policies: `ask` must prove approval before spawn and refusal with zero spawn, while `auto` must prove Dispatch Announcement followed by immediate spawn without a question. After Dispatch Authorization, run the shared reuse, write-ownership, failure, and integration lifecycle primarily through the recommended `auto` path instead of duplicating the complete matrix under `ask`.

## Problem with the v0.3.2 threshold

v0.3.2 requires either:

1. at least two separable work or evidence lanes; or
2. one concrete specialist boundary from a finite high-risk set.

In practice, the first condition is commonly interpreted as requiring multiple delegable child lanes. It filters out useful cases where one bounded child can work independently while the Root Session continues the core task.

The design should relax that threshold without returning to delegation based only on broad task categories or vague risk words.

## Target eligibility rule

For implicit delegation, Diverter should dispatch when all of the following are true:

1. **Bounded child task** — at least one concrete subtask has a clear scope and verifiable deliverable.
2. **Independent progress** — the child can proceed without repeatedly waiting for Root decisions or an unfinished prerequisite.
3. **Useful Root lane** — the Root Session has distinct, non-duplicative work it can continue while the child runs.
4. **Material benefit** — delegation is expected to improve speed or final quality enough to justify coordination and token cost.
5. **Safe ownership** — read/write boundaries are clear and concurrent writes do not overlap.

The key reinterpretation is:

```text
v0.3.2: child lane A + child lane B
target: child lane A + Root lane
```

One suitable child is sufficient. Additional children are justified only by additional independent deliverables.

Explicit delegation requests may bypass the implicit benefit threshold, but never clarity, permissions, sandboxing, write boundaries, delegated-child recursion guards, or an explicit opt-out.

## Hard non-trigger cases

Diverter should stay in the Root Session when:

- the task is trivial or coordination would cost more than the work;
- the work is one strong sequential chain;
- no bounded child deliverable can be stated;
- Root and child would investigate the same question;
- concurrent writers would own the same mutable artifact or scope;
- the request is ambiguous and must be clarified first;
- the user opts out of delegation;
- the current task is already a delegated child handoff; or
- Native Proactive Delegation already owns orchestration.

Vague words such as security, performance, regression, or release do not independently justify delegation. They remain useful signals only after the artifact, boundary, or expected evidence is concrete.

## Root Session responsibilities

The Root Session remains accountable for the complete user outcome.

### Before dispatch

- understand the user goal and success criteria;
- identify the Root lane and each child lane;
- confirm that the lanes do not duplicate one another;
- choose the smallest sufficient lineup;
- define write ownership and verification;
- announce both what the child will do and what Root will continue doing.

### While children run

- make substantive, non-duplicative progress on the stated Root lane while useful work remains;
- avoid repeating an investigation already assigned to a child;
- reuse the same native child for related follow-up questions when possible;
- keep write-capable work serialized unless ownership is explicitly disjoint.

### After children return

- collect concise results rather than raw logs;
- resolve contradictions and expose unresolved uncertainty;
- choose and perform verification in proportion to the task and its risk;
- integrate child evidence with Root work;
- preserve successful lanes when another lane fails;
- own the final decision, validation, and user response.

## Child responsibilities

Every child should:

- execute one bounded handoff with a concrete deliverable;
- remain within `scope_in`, `scope_out`, and `write_policy`;
- cite files, symbols, commands, documents, or other inspectable evidence;
- distinguish verified facts from inference and unresolved questions;
- never delegate, spawn descendants, or transfer orchestration ownership;
- return a concise integration-ready result instead of an activity transcript.

Every write-capable child must additionally:

- own explicit mutable artifacts or a bounded write scope;
- recognize that other agents may share the working environment;
- never revert or overwrite work outside that ownership;
- adapt to compatible concurrent changes; and
- report what it changed and how the result was checked.

## Lineup rule

Start with one child. Add another only when it owns a different necessary deliverable that can progress independently.

The existing maximum of four roles remains a safety cap, not a target. Filling available concurrency slots is never a reason to dispatch.

## Existing v0.3.2 behavior to preserve

- explicit user intent and opt-out precedence;
- focused skills retaining ownership of their core workflow;
- Sanitized Failure Reporting;
- read-first mixed work and bounded write policies;
- no sandbox or approval weakening during fallback;
- compact/resume duplicate-dispatch protection;
- capability-first role selection; and
- silent deferral to Native Proactive Delegation.

A focused skill may still own the Root lane while Diverter supplies a distinct supporting lane. Diverter must not replace or duplicate the focused skill's work.

## Evaluation requirements

Do not convert existing narrow negative prompts into positives without changing their task shape. Add paired near-neighbor cases where the only meaningful difference is the presence of a bounded child lane and a useful Root lane.

### Current evidence baseline

The current 33 passing tests are v0.3.2 contract evidence, not v0.4.0 native lifecycle evidence. They cover policy text, role configuration, installation behavior, handoff wording, and the legacy CLI runner, while the prompt evaluations score final responses rather than observing native execution.

The repository currently has no native lifecycle harness or event parser. In particular, existing tests do not prove:

- a native role was actually resolved and dispatched;
- the Root Session made substantive progress before child completion;
- a related follow-up reused the same canonical child identity;
- the child created no descendants at runtime;
- Root independently verified and integrated the child result; or
- concurrent write ownership remained disjoint or serialized.

Static contract tests remain appropriate for eligibility, `ask`/`auto` wording, Root/Child lane declarations, role removal, the leaf-child handoff, native spawn parameters, and removal of CLI references. Lifecycle claims require separate evidence from real native runs.

User-facing release material converts passed evidence into capability-first statements. It does not need to reproduce the internal boundary analysis, but every advertised behavior must map to a passed contract or lifecycle gate.

### Available native trace evidence

A native probe during this design session confirmed that the supported host can provide the raw evidence needed for a lifecycle gate. Persisted records expose the parent spawn and follow-up calls, canonical child session identity, per-turn identities, parent-child linkage, timestamps, task start/completion events, and child tool calls. The probe observed:

- the spawn returning before child completion;
- substantive Root document work during the child's active interval;
- a related follow-up entering a second turn in the same child session; and
- no descendant spawn from that child.

This proves host observability and native follow-up capability for the probe. It does not prove that Diverter's routing rules automatically choose reuse, maintain Root progress, or prevent descendants; those remain product-level end-to-end release evidence.

The next evaluation should measure:

- eligible-task trigger recall;
- strict-negative false-positive rate;
- substantive Root progress before child completion;
- duplicate dispatches for the same scope;
- reuse of an existing child for related follow-ups;
- overlapping write ownership;
- Root integration and independent verification; and
- speed or quality improvement against a serial baseline.

Final-response text alone cannot prove concurrency, reuse, or ownership safety. Claims about those behaviors require lifecycle evidence from real native executions.

## Runtime boundaries

Diverter can encode the discipline of Ultra-style delegation, but it cannot guarantee every host capability:

- the SessionStart gate and skill remain instruction-driven rather than an internal scheduler;
- native thread reuse and follow-up routing depend on the exposed Codex tools and must pass the D4f release gate on the supported native surface;
- host concurrency limits and scheduling fairness remain Codex responsibilities; and
- no routing policy makes a non-Ultra model reason identically to Ultra.

## Non-goals for this design phase

- implementing the changes before the design interview is complete;
- changing the bundled Static Model Mapping;
- claiming universal model parity from a single primary Root configuration;
- reproducing Ultra's internal scheduler or model reasoning;
- retaining or replacing the removed CLI Worker Backend with another compatibility executor;
- defining an exhaustive catalog of acceptable Root progress or verification actions;
- adding a dedicated unavailable-child recovery protocol beyond ordinary Root accountability;
- building a custom lock manager or general-purpose workflow engine; or
- changing Codex sandbox and permission semantics.

## Design conclusion

The design tree is closed. Product positioning, delegation eligibility, Root/child responsibilities, Native-only execution, failure behavior, policy semantics, ownership boundaries, model coverage, and v0.4.0 release evidence are settled and ready for implementation planning.
