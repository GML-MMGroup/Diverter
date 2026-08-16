# Changelog

## 0.4.2 - 2026-08-17

- Add a Root-only `UserPromptSubmit` Turn Reminder so every user prompt applies Diverter Preflight before task work.
- Make the `SessionStart`-injected Session Contract the sole normative eligibility source and keep the Diverter skill focused on the post-eligibility Dispatch Workflow.

## 0.4.1 - 2026-08-14

- Restore the tracked Codex marketplace manifest so fresh installations can add the Diverter marketplace.

## 0.4.0 - 2026-08-14

- Distill Ultra-inspired decomposition and routing into non-Ultra Codex sessions.
- Relax implicit eligibility to one bounded Child Lane plus one distinct, useful Root Lane, including Supporting Children for focused skills.
- Default to the Smallest Sufficient Lineup, keep Root progressing during child work, and reuse the same native child for related follow-ups.
- Make native role-specific subagents the only execution backend and remove the CLI worker path.
- Add explicit Write Ownership, leaf-child handoffs, Root integration and verification requirements, paired routing cases, and persisted native lifecycle evidence checks.
- Ask fresh installations to choose `auto` or `ask`, with `auto` recommended for proactive dispatch.

## 0.3.2 - 2026-07-28

- Keep focused, single-lane work in the root session while reserving implicit delegation for separable evidence lanes and concrete specialist risks.
- Respect explicit subagent requests and focused-skill ownership, so the user's chosen workflow stays in charge.
- Report execution-changing failures briefly without exposing aliases, cache paths, skill-loading mechanics, or retries; recovered internal failures stay silent.
- Clarify that repeated marketplace and plugin directory names are valid and keep the returned `installedPath` authoritative.

## 0.3.1 - 2026-07-18

- Use `agent_type` with `fork_turns: "none"` so native subagents reliably apply each role's configured model and reasoning effort.
- Recommend Codex CLI `0.145.0-alpha.20` or later for the full native subagent experience.

## 0.3.0 - 2026-07-15

- Add persistent user-level `ask` and `auto` delegation policies, defaulting new installations to `ask`.
- Add the explicit `$diverter-mode` skill for policy status and changes.
- Load the saved policy through the `SessionStart` Hook on startup, resume, clear, and compaction.
- Let `auto` announce and immediately dispatch suitable `read-only`, `mixed`, and `write-capable` work without weakening existing permissions or write boundaries.
- Update installation guidance, delegation contracts, and focused evaluation coverage for both policies.

## 0.2.0 - 2026-07-14

- Rename the product and all active technical identifiers to Diverter.
- Replace the README hero artwork and adopt the new bilingual tagline.
- Preserve the approval-before-delegation behavior.

## 0.1.0 - 2026-07-14

- Distribute Cast Subagents as a single-repository Codex plugin and marketplace.
- Activate the advisory gate with a stateless `SessionStart` Hook.
- Add capability-based native-agent or ephemeral CLI-worker execution.
- Install the bundled role pack globally with explicit model, effort, sandbox, and live Web Search settings.
- Keep suggest-only delegation and approval-before-work rules.
