# Decision Rules

Examples for applying the Session Contract's strong signals, clear exclusions, and tie-breakers. The Session Contract remains authoritative.

| Task shape | Example outcome | Child Contribution | Root Responsibility |
| --- | --- | --- | --- |
| Explicit delegation request | Candidate `ELIGIBLE` when remaining safeguards hold | requested bounded specialist work | remaining orchestration or task outcome |
| Active skill explicitly requires a subagent | Candidate `ELIGIBLE` as a Required Skill Route when remaining safeguards hold | skill-defined child task, deduplicated against equivalent routes | focused skill keeps its core workflow and integrates the result |
| Code path plus official docs | Candidate `ELIGIBLE` | verify the documented API contract | trace the implementation and frame the decision |
| Focused skill ownership plus bounded support | Candidate `ELIGIBLE` | complementary Supporting Child check | focused skill keeps its core workflow and integrates the check |
| Known regression plus bounded test work | Candidate `ELIGIBLE` | design or implement the targeted proof | map the behavior boundary and integrate results |
| Web interaction plus named Web metrics | Candidate `ELIGIBLE` | audit LCP, INP, or CLS risks | analyze component, accessibility, and design constraints |
| Context-heavy research or code mapping | Candidate `ELIGIBLE` | absorb noisy source material and return compact evidence | judge the evidence and integrate the final outcome |
| Disjoint mutable artifacts | Candidate `ELIGIBLE` | edit one declared artifact | progress another independently owned artifact |
| Specialist offload with no separate Root deliverable | Candidate `ELIGIBLE` when a strong positive signal applies | complete one bounded specialist contribution | wait if needed, then judge, verify, and integrate |
| Focused skill with duplicate helper | `ROOT_ONLY` | duplicates the selected skill | no independent benefit |
| Active skill says a subagent is optional | Apply ordinary implicit eligibility | no required route | focused skill keeps its core workflow |
| Tightly coupled or overlapping writes | `ROOT_ONLY` | conflicting ownership | serialize in Root |
| Trivial fact lookup | `ROOT_ONLY` | bounded but too small to justify a handoff | answer directly |
| Small local refactor with caller mapping | `ROOT_ONLY` when the handoff would cost more than direct inspection | low-value prerequisite | one local implementation decision |
| Vague risk language | `ROOT_ONLY` until the objective is concrete | no usable specialist scope | clarify the objective |

Before using any implicit row, perform the Session Contract's Task-shape Deliberation. The user does not need to state the contribution or Root responsibility. Every `ROOT_ONLY` outcome stays silent; only `ELIGIBLE` produces a routing receipt.
