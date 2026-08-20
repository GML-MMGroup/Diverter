---
status: accepted
---

# Absorb required skill routes into Diverter

When another active skill explicitly requires a subagent contribution for the current task, Diverter treats it like an Explicit Delegation Request and carries the skill-defined child task into the selected lineup as a Required Skill Route. Optional suggestions do not create required routes. The focused skill retains its core workflow, while Diverter remains the sole Orchestration Owner, maps capability-only requirements to available roles, preserves an available named role, and merges equivalent routes into one spawn.

Required Skill Routes bypass only the implicit material-benefit threshold. Explicit opt-out, task executability, native availability, permissions and sandboxing, safe Write Ownership, and delegated-child recursion remain authoritative.

This amends D3 in `docs/design/ultra-delegation-distillation.md`: focused-skill support remains optional under ordinary implicit routing, but an explicit subagent requirement from the active skill becomes a required route.
