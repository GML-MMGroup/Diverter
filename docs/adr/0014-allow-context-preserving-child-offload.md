---
status: superseded
superseded_by: ADR-0015
---

# Allow context-preserving Child offload without a separate Root deliverable

Diverter will implicitly delegate when one bounded Child Contribution can execute autonomously, offers credible material benefit, and has safe responsibility and write ownership. Material benefit includes Root Context Preservation: a Child may absorb substantially larger, noisier, or more exploratory source material and return a compact evidence-grounded handoff. A separate concurrent Root Lane or separate Root deliverable is no longer required.

Root remains the Orchestration Owner. It may continue useful non-duplicative work while the Child runs or wait when the Child result is needed first, but it always owns judgment, proportional verification, integration, and the final response. Waiting alone does not establish benefit. Trivial, ambiguous, low-benefit, unnecessarily duplicative, and overlapping-write tasks remain `ROOT_ONLY`.

This decision supersedes ADR-0009's requirement for Root-child parallelism while preserving its Smallest Sufficient Lineup, Leaf Child, Child Reuse, and Write Ownership constraints. The Session Contract remains the normative eligibility interface; lifecycle validation must accept context-preserving offload without treating concurrent Root progress as mandatory.
