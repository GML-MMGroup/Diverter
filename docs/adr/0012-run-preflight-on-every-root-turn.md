---
status: accepted
---

# Run Preflight on every Root turn with two Hooks

Diverter will deliver one canonical Session Contract through `SessionStart` and one short Turn Reminder through `UserPromptSubmit`. `SessionStart` injects the complete normative Preflight rules plus the active Delegation Policy for startup, resume, clear, and compact. `UserPromptSubmit` makes Preflight mandatory before every Root turn without repeating the full Contract; its command emits nothing whenever the hook input contains `agent_id`, so delegated children receive no Diverter context.

**Session Contract**: the complete, compact, normative rules that produce `BYPASS`, `ROOT_ONLY`, or `ELIGIBLE`.

**Turn Reminder**: the short Root-only context that requires the current prompt to apply the active Session Contract.

**Preflight**: the mandatory application of the Session Contract before repository reads, tools, skills, planning, or other task work.

**Dispatch Workflow**: the post-`ELIGIBLE` behavior covering policy, lineup, Work Mode, handoff, dispatch, Root progress, integration, and failure handling.

The Session Contract is the only authority for `BYPASS`, `ROOT_ONLY`, and `ELIGIBLE`. Normal Diverter skill activation trusts the completed Preflight and owns only the Dispatch Workflow. If the Contract is missing, the Turn Reminder directs the model to load Diverter, which reads the same canonical Contract for fallback Preflight. Decision-rule references remain illustrative and cannot override the Contract.

This supersedes ADR-0004's decision-source and activation-only statements while preserving its Native Proactive Delegation ownership decision. It also extends ADR-0007 without changing `ask`, `auto`, policy persistence, or next-SessionStart activation semantics. The existing Codex CLI `0.145.0` minimum remains sufficient; its official release runtime was verified to omit `agent_id` for Root `UserPromptSubmit` input and include `agent_id` plus `agent_type` for a real reviewer Child input.
