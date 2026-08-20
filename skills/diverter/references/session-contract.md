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

### 3. Explicit Delegation Request and Required Skill Route

An affirmative request using `$diverter`, `subagent`, `delegate`, `委派`, `子代理`, or a named installed agent role is a candidate `ELIGIBLE`. Mere mention, quotation, explanation, hypothesis, negation, or scheduling language such as parallel or concurrent does not qualify.

A Required Skill Route exists when another active skill explicitly requires a subagent contribution for the current task. Here, active means selected and loaded for the current task, not merely available, mentioned in repository text, or listed in a skill catalog. A requirement may use `must`, `required`, or an unqualified imperative such as `use`, `spawn`, or `delegate`; optional language such as `may`, `can`, `consider`, `optional`, or `recommended` does not create a Required Skill Route.

Treat a Required Skill Route as an Explicit Delegation Request with the same force as an affirmative user request, and carry the skill-defined child task into Diverter's selected lineup as a required route.

The focused skill retains its core workflow while Diverter remains the sole Orchestration Owner. If the skill names an available installed role, preserve it. If it names only a capability or child task, map that requirement to a matching available installed role. Two routes are equivalent only when their objective boundary, integration-ready result, and write policy and ownership match; a shared role name alone is insufficient. Merge equivalent skill-required and task-derived contributions into one route, retain its required status, and create one spawn.

If a Required Skill Route cannot map to an available installed role, fit within the four-role safety cap, or satisfy safe Write Ownership, Diverter cannot activate for that task. Do not silently drop the route, substitute a generic role, or claim the requirement was completed; continue under the focused skill's own unavailable-dependency behavior.

Resolve every applicable skill's known delegation requirements before composing an eligible lineup and receipt. If loading an applicable skill reveals a Required Skill Route after an initial silent `ROOT_ONLY`, that discovery may trigger the one allowed reconsideration before implementation.

An Explicit Delegation Request bypasses only the requirement to independently establish material benefit. It does not require a separate concurrent Root Lane, and it does not bypass the rules above, task executability, Codex permissions or sandboxing, safe Write Ownership, or native capability requirements. If the objective cannot yet be acted on safely, return `ROOT_ONLY`; ordinary Root behavior may clarify it.

A requested read-only specialist lane is sufficiently bounded when the current repository and task context identify what to inspect and the Child can report only verified findings. Do not require the user to name a file or link when that context safely bounds the requested inspection.

### 4. Implicit eligibility

Without an Explicit Delegation Request, perform Task-shape Deliberation before classifying the prompt:

1. Infer the concrete outcome and the work needed to produce it. Do not classify from surface wording alone.
2. Look for one strong positive signal for useful offload, then check whether a clear exclusion applies.
3. If the task shape is positive, construct the smallest safe Child Contribution and the Root responsibility that will use it.

Keep this deliberation private. Do not expose chain-of-thought or add a separate reasoning report.

Strong positive signals include any one of:

- read-heavy research, code mapping, log inspection, or other exploration that lets a Child absorb noisy source material and return compact evidence;
- code and documentation or API verification that form complementary evidence;
- multiple independent questions, review dimensions, or planning investigations;
- a specialist viewpoint or independent verification that can materially improve confidence or quality; or
- a focused skill that can use one bounded Supporting Child without giving up its core workflow.

Clear exclusions include:

- trivial, wording-only, or one-fact tasks where delegation overhead is larger than the work;
- an ambiguous objective that needs clarification before useful work can be assigned;
- one strongly sequential critical path with no useful independent contribution;
- tightly coupled work where Root and Child would repeat the same decision; or
- overlapping or unsafe write ownership.

Use these tie-breakers instead of demanding proof of every possible benefit:

- lean `ELIGIBLE` for read-heavy, exploratory, code-plus-docs, multi-perspective, and independent-verification work;
- lean `ROOT_ONLY` for small, tightly coupled, or write-heavy work; and
- when a positive signal is credible and one Child can be bounded safely, prefer the smallest one-Child lineup.

Before dispatch, ensure the selected Child Contribution has a clear scope and completion condition, can proceed without repeatedly waiting for Root decisions, and has safe read and write ownership. These are execution safeguards after a positive task-shape judgment, not a requirement that the user predefine lanes, handoffs, multiple directions, or separate deliverables.

A separate concurrent Root Lane or separate Root deliverable is not required. Root may continue other work or wait for the Child result, but waiting alone is not a benefit. Root remains responsible for judgment, proportional verification, integration, and the final response.

Reading the same artifact does not make responsibilities duplicative when the questions differ or the overlap is intentional independent verification. Root's proportional verification of a Child result is not duplication.

If a clear exclusion applies or no strong positive signal remains after considering the current prompt and conversation context, return `ROOT_ONLY`.

### 5. Native availability

Before final activation, confirm that native role-specific subagent dispatch and at least one useful installed role are available. If not, return `ROOT_ONLY` silently; do not announce an internal capability problem or ask how to proceed.

### 6. Result action

- `BYPASS`: exit Diverter entirely and continue under the owning mechanism.
- `ROOT_ONLY`: continue silently in the Root Session. Every `ROOT_ONLY` result is silent: do not emit a routing receipt, mention Diverter, or expose the internal decision.
- `ELIGIBLE`: load `$diverter` silently before any user-visible message or task work. The completed Preflight is authoritative; do not re-adjudicate eligibility in the normal Skill path. The skill's policy-specific routing receipt is the first user-visible output and the single external receipt; do not add eligibility, loading, recommendation, or announcement prose around it.

`SessionStart`, resume, clear, and compact restore context but never emit a Routing Receipt by themselves. Only `ELIGIBLE` produces a routing receipt.

An emitted `ELIGIBLE` receipt is final for that normalized scope. A silent `ROOT_ONLY` decision may be reconsidered once if user clarification, lightweight read-only Root discovery, or a mandatory skill load materially changes the task shape before implementation; never announce the earlier non-delegation or duplicate an eligible dispatch.

The active `ask` or `auto` Delegation Policy does not change eligibility. It controls the Dispatch Workflow only after `ELIGIBLE`, and an explicit Task Policy Override retains its existing one-task scope.

The strong signals, exclusions, and tie-breakers above are the implicit eligibility standard. Do not convert them into an all-conditions-must-pass checklist.
