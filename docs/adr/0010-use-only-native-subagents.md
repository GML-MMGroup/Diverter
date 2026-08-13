---
status: accepted
---

# Use only native subagents

Diverter v0.4.0 uses only native role-specific subagents and removes the CLI Worker Backend without a deprecation release. Native eligibility requires an available target `agent_type` and isolated `fork_turns: "none"` handoffs, while model and reasoning settings remain owned by the installed role definition; if native dispatch is unavailable before activation, Diverter stays inactive and the Root Session silently completes the task, while missing individual roles are dropped and covered by Root. Native children inherit the Root Session's effective permission profile, so a role's `sandbox_mode = "read-only"` records behavioral intent rather than an independent runtime-enforcement boundary. A failure after an announced dispatch is reported briefly and absorbed by Root. Real same-child follow-up reuse is a release gate, and this decision supersedes `0002-use-capability-selected-subagent-backends.md` without removing Bundled Subagent definitions, their Static Model Mapping, or the Role Installer.
