## Diverter Session Contract

This contract applies only to the Root Session. For every user prompt, before repository reads, tool calls, skill loading, planning, or other task work, apply this Preflight in order.

### 1. BYPASS

- If the prompt explicitly invokes `$diverter-mode`, execute Mode Control directly. Do not evaluate or load Diverter.
- If the task is a delegated-subagent handoff or includes `delegation_context: delegated-subagent`, execute only that handoff.
- If higher-priority instructions state that proactive multi-agent delegation is active, let Native Proactive Delegation remain the sole Orchestration Owner. Do not evaluate, load, or mention Diverter.

### 2. Explicit opt-out

If the user affirmatively prohibits delegation, return `ROOT_ONLY`.

### 3. Explicit Delegation Request

An affirmative request using `$diverter`, `subagent`, `delegate`, `委派`, `子代理`, or a named installed agent role is a candidate `ELIGIBLE`. Mere mention, quotation, explanation, hypothesis, negation, or scheduling language such as parallel or concurrent does not qualify.

An Explicit Delegation Request bypasses only the implicit benefit threshold. It does not bypass the rules above, task executability, Codex permissions or sandboxing, safe Write Ownership, or native capability requirements. If the objective cannot yet be acted on safely, return `ROOT_ONLY`; ordinary Root behavior may clarify it.

### 4. Implicit eligibility

Without an Explicit Delegation Request, return candidate `ELIGIBLE` ONLY IF all five conditions are affirmatively established from the current prompt, existing conversation context, and this contract:

1. One bounded, independently executable Child Lane has a clear deliverable.
2. One distinct, useful Root Lane can make substantive progress while the child runs. Waiting, supervision, or repeating the Child Lane does not count.
3. Separate execution offers a credible, non-trivial benefit in elapsed time, coverage or quality, relevant expertise, or independent verification. Mere theoretical divisibility is insufficient.
4. Root and Child scopes are non-duplicative.
5. Read and write ownership is safe and non-overlapping.

An explicitly selected focused skill may retain its core workflow and Root Lane while Diverter supplies a Supporting Child only for a separate, non-duplicative deliverable.

If any implicit condition is uncertain or absent, return `ROOT_ONLY`.

### 5. Native availability

Before final activation, confirm that native role-specific subagent dispatch and at least one useful installed role are available. If not, return `ROOT_ONLY` silently; do not announce an internal capability problem or ask how to proceed.

### 6. Result action

- `BYPASS`: exit Diverter entirely and continue under the owning mechanism.
- `ROOT_ONLY`: continue silently in the Root Session.
- `ELIGIBLE`: load `$diverter` before any task work. The completed Preflight is authoritative; do not re-adjudicate eligibility in the normal Skill path.

The active `ask` or `auto` Delegation Policy does not change eligibility. It controls the Dispatch Workflow only after `ELIGIBLE`, and an explicit Task Policy Override retains its existing one-task scope.

Trivial, strongly sequential, one-path, duplicative, or overlapping-write work normally fails the positive conditions above; these are examples, not a second eligibility standard.
