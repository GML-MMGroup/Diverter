---
status: accepted
---

# Deliberate task shape and emit one routing receipt

Before applying the existing implicit eligibility conditions, Task-shape Deliberation will privately infer the requested outcome, construct the strongest plausible one-Child-plus-Root split, and test that split against independence, material benefit, duplication, and ownership. User prompts do not need to name lanes, delegation, or multiple directions. Preflight will not expose chain-of-thought or add a new routing state.

Each Root user prompt produces at most one external routing result. Ordinary task-shape `ROOT_ONLY` emits `Routing: ROOT_ONLY — <one task-shape reason>` in the user's language. Eligible work uses its existing policy-specific Dispatch Recommendation or Dispatch Announcement instead of adding another message. Bypass, explicit opt-out, and native unavailability remain silent; `SessionStart`, resume, clear, and compact never produce a receipt by themselves.

Router validation will retain the existing explicit-lane controls and add natural-language positive cases whose Root and Child lanes must be inferred. Routing Receipt correctness is a required prompt invariant and release gate, not an eighth scored rubric dimension.

This amends ADR-0012's silent `ROOT_ONLY` behavior while preserving its two-Hook architecture, pre-task ordering, canonical Session Contract, three final results, and post-`ELIGIBLE` Dispatch Workflow. It does not introduce a routing-discovery phase or change the Native availability boundary.
