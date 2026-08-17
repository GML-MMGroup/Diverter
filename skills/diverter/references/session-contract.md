## Diverter Session Contract

This contract applies only to the Root Session. For every user prompt, before repository reads, tool calls, skill loading, planning, or other task work, apply this Preflight in order.

### 1. BYPASS

- If the prompt explicitly invokes `$diverter-mode`, execute Mode Control directly. Do not evaluate or load Diverter.
- If the task is a delegated-subagent handoff or includes `delegation_context: delegated-subagent`, execute only that handoff.
- If higher-priority instructions state that proactive multi-agent delegation is active, let Native Proactive Delegation remain the sole Orchestration Owner. This is a terminal, silent `BYPASS` even when the native owner itself spawns children. Do not evaluate, load, or mention Diverter.
- If the prompt continues an already announced or dispatched workflow, continue that workflow without a new routing decision. Reuse an existing child only for a valid follow-up; after a lane failure, Root takes over without a replacement spawn unless the user explicitly requests a retry or new delegation.
- If an implicitly selected Diverter path failed before dispatch and Root can continue, this is a terminal Root-only recovery state for the entire prompt. Do not call `spawn_agent`, use any role, substitute generic agents, or switch to another delegation backend, even if the task would normally benefit from parallel review.

### 2. Explicit opt-out

If the user affirmatively prohibits delegation, return `ROOT_ONLY`.

An affirmative delegation request that asks to see the lineup or wait for approval is not an opt-out. Treat it as a one-task `ask` policy override after eligibility is established.

### 3. Explicit Delegation Request

An affirmative request using `$diverter`, `subagent`, `delegate`, `委派`, `子代理`, or a named installed agent role is a candidate `ELIGIBLE`. Mere mention, quotation, explanation, hypothesis, negation, or scheduling language such as parallel or concurrent does not qualify.

An Explicit Delegation Request bypasses only the implicit benefit threshold. It does not bypass the rules above, task executability, Codex permissions or sandboxing, safe Write Ownership, or native capability requirements. If the objective cannot yet be acted on safely, return `ROOT_ONLY`; ordinary Root behavior may clarify it.

A requested read-only specialist lane is sufficiently bounded when the current repository and task context identify what to inspect and the Child can report only verified findings. Do not require the user to name a file or link when that context safely bounds the requested inspection.

### 4. Implicit eligibility

Without an Explicit Delegation Request, perform Task-shape Deliberation before classifying the prompt:

1. Infer the concrete outcome and the work needed to produce it. Do not classify from surface wording alone.
2. Construct the strongest plausible split with one bounded Child Lane and one distinct useful Root Lane.
3. Test that candidate split against the five conditions below. Do not treat the absence of user-written lanes, delegation language, or multiple directions as evidence that no useful split exists.

Keep this deliberation private. Do not expose chain-of-thought or add a separate reasoning report.

Return candidate `ELIGIBLE` ONLY IF all five conditions are affirmatively established from the current prompt, existing conversation context, and this contract:

1. One bounded, independently executable Child Lane has a clear deliverable.
2. One distinct, useful Root Lane can make substantive progress while the child runs. Waiting, supervision, repeating the Child Lane, or performing a prerequisite for the same single audit or implementation decision does not count. When the entire requested outcome is one audit and report, mapping the audited flow or its boundaries is part of that audit, not a distinct Root Lane. This exclusion does not apply when Root must derive repository-specific constraints and a plan while a Child independently verifies a named external official contract.
3. Separate execution offers a credible, non-trivial benefit in elapsed time, coverage or quality, relevant expertise, or independent verification. Mere theoretical divisibility is insufficient.
4. Root and Child scopes are non-duplicative.
5. Read and write ownership is safe and non-overlapping.

Reading the same artifact does not make two scopes duplicative when their evidence and outcomes are distinct. For example, component and accessibility acceptance analysis can remain in Root while a Child independently audits named Web metrics such as LCP, INP, and CLS.

For a known regression with a named behavior boundary, a requested minimal fix recommendation and Prove-It test strategy are distinct outcomes: Root can trace the behavior and form the fix recommendation while `test-engineer` independently designs the regression proof.

An explicitly selected focused skill may retain its core workflow and Root Lane while Diverter supplies a Supporting Child only for a separate, non-duplicative deliverable.

If any implicit condition is uncertain or absent, return `ROOT_ONLY`.

### 5. Native availability

Before final activation, confirm that native role-specific subagent dispatch and at least one useful installed role are available. If not, return `ROOT_ONLY` silently; do not announce an internal capability problem or ask how to proceed.

### 6. Result action

- `BYPASS`: exit Diverter entirely and continue under the owning mechanism.
- `ROOT_ONLY` from Explicit opt-out or Native availability: continue silently in the Root Session.
- `ROOT_ONLY` from ordinary eligibility adjudication: emit exactly one Routing Receipt for this Root user prompt, then continue in Root: `Routing: ROOT_ONLY — <one task-shape reason>`. Match the user's language in the reason. Do not mention Diverter, skill loading, role availability, or other internal checks.
- `ELIGIBLE`: load `$diverter` silently before any user-visible message or task work. The completed Preflight is authoritative; do not re-adjudicate eligibility in the normal Skill path. The skill's policy-specific routing receipt is the first user-visible output and the single external receipt; do not add eligibility, loading, recommendation, or announcement prose around it.

`SessionStart`, resume, clear, and compact restore context but never emit a Routing Receipt by themselves. Emit at most one receipt for each Root user prompt.

The first routing result is final for that Root user prompt. After `ROOT_ONLY`, do not later load Diverter, emit an `ELIGIBLE` receipt, or spawn because task analysis reveals a possible split.

The active `ask` or `auto` Delegation Policy does not change eligibility. It controls the Dispatch Workflow only after `ELIGIBLE`, and an explicit Task Policy Override retains its existing one-task scope.

Trivial, strongly sequential, one-path, duplicative, or overlapping-write work normally fails the positive conditions above; these are examples, not a second eligibility standard.
