---
name: diverter
description: "Use after the Root Session Preflight returns ELIGIBLE, or when the Diverter Session Contract is missing and fallback Preflight is required. Apply the loaded ask or auto Delegation Policy. Do not use for Mode Control, delegated subagent handoffs, explicit opt-out, or when native proactive delegation owns orchestration."
---

<NATIVE-PROACTIVE-DELEGATION-STOP>
If higher-priority session instructions explicitly state that proactive multi-agent delegation is active, skip this skill, even when explicitly invoked. Do not mention Diverter, select a lineup, request Dispatch Authorization, or spawn children. Continue the current task under the native policy.
</NATIVE-PROACTIVE-DELEGATION-STOP>

<SUBAGENT-STOP>
If the current task explicitly says it is a delegated subagent task or includes `delegation_context: delegated-subagent`, skip this skill. Execute only the assigned handoff. Never select another lineup, request Dispatch Authorization, spawn a descendant, or transfer orchestration ownership.
</SUBAGENT-STOP>

# Diverter

## Mission

Diverter distills Ultra-inspired task decomposition and role routing for non-Ultra Codex sessions. The Root Session remains the Orchestration Owner and is accountable for the complete user outcome.

For an eligible task:

- choose the Smallest Sufficient Lineup of 1-4 available roles;
- assign every child one bounded independent Child Lane;
- for implicit eligibility, declare the distinct useful Root Lane that will progress while children run;
- state exactly one Work Mode: `read-only`, `mixed`, or `write-capable`;
- apply the loaded `ask` or `auto` Delegation Policy; and
- integrate and proportionally verify child results before answering the user.

Only implicit eligibility requires a distinct useful Root Lane and material benefit. An Explicit Delegation Request may have no distinct Root Lane; Root still owns orchestration, integration, verification, and the final outcome.

If the Missing-Contract fallback returns `ROOT_ONLY`, follow the Session Contract's Routing Receipt and silence rules. If native dispatch is unavailable, continue silently in the Root Session.

## Preflight Handoff

The Session Contract is the sole normative authority for `BYPASS`, `ROOT_ONLY`, and `ELIGIBLE`. In the normal path, this skill loads only after `ELIGIBLE`; trust the completed Preflight and do not re-adjudicate eligibility.

Use the Missing-Contract fallback only when the active Session Contract is absent:

1. read `references/session-contract.md` completely;
2. apply its ordered Preflight to the current prompt and existing conversation context; and
3. continue with this skill only for `ELIGIBLE`; otherwise follow the Contract's result action.

The native-proactive and delegated-subagent stops above remain defense in depth. They do not create a second eligibility standard.

## Decision Process

Follow this sequence:

1. Apply the Native Proactive Delegation and delegated-subagent stops above.
2. Execute `$diverter-mode` directly when explicitly invoked; never delegate Mode Control.
3. Trust the completed Preflight, or run the Missing-Contract fallback above.
4. Resolve the Delegation Policy.
5. Confirm the Native Capability Check remains satisfied before mentioning Diverter or proposing a lineup.
6. Select the Smallest Sufficient Lineup from available roles.
7. Classify the complete workflow's Work Mode.
8. Produce the policy-specific Delegation Contract.
9. Dispatch only after Dispatch Authorization.
10. Continue the declared Root Lane when one exists; otherwise coordinate the explicitly requested child. Collect results, resolve conflicts, verify proportionally, and integrate the final outcome.

## Delegation Policy

Resolve policy in this order:

1. the stops and Mode Control bypasses above;
2. Native Proactive Delegation ownership from higher-priority instructions;
3. an explicit Task Policy Override in the current user message;
4. the loaded `delegation_policy` from the Session Contract; and
5. `ask` when no valid policy is available.

Valid values are `delegation_policy: ask` and `delegation_policy: auto`.

- `ask`: recommend one lineup, ask for approval, and stop before task work or spawning. A refusal creates zero children and Root continues.
- `auto`: publish one Dispatch Announcement, then spawn immediately in the same turn without a permission question, regardless of Work Mode.

Task Policy Overrides apply only to the current task. Work Mode describes write risk; it never creates a hidden third policy.

Work Mode classifies the complete Root-and-Child workflow: `read-only` when no active lane may write, `mixed` when only some active lanes may write, and `write-capable` when every active lane may write. Per-role capability and child handoff write policy remain separate.

## Native Capability Check

Diverter uses the Native Subagent Backend exclusively. Before announcement or dispatch, confirm that the current host still exposes native role-specific spawning with a target `agent_type`, supports isolated `fork_turns: "none"`, and exposes the requested installed role.

- Do not require or pass runtime `model` or `reasoning_effort` overrides. The installed Bundled Subagent definition owns those settings.
- Do not use a generic child as a substitute for a missing requested role.
- If native subagent dispatch is unavailable, do not announce Diverter, report a backend problem, or ask what to do. Continue silently in the Root Session.
- If a role is unavailable, drop it and keep its capability in the Root Lane. If no useful role remains, continue silently in Root.

## Capability Selection

Select capabilities first, then map only to roles available in the current Codex environment.

| Capability | Preferred role | Role write capability |
| --- | --- | --- |
| code mapping | `code-mapper` | read-only |
| code review | `reviewer` | read-only |
| security audit | `security-auditor` | read-only |
| docs/API verification | `docs-researcher` | read-only |
| search | `search-specialist` | read-only |
| synthesis | `knowledge-synthesizer` | read-only |
| planning | `task-distributor` | read-only |
| test strategy | `test-engineer` | read-only |
| test automation | `test-automator` | write-capable |
| Web performance audit | `web-performance-auditor` | read-only |

Smallest Sufficient Lineup rules:

- Default to one child. Pair it with the required Root Lane for implicit eligibility.
- When a focused skill owns the Root Lane, select only a separate, non-duplicative Supporting Child.
- Add another child only for another necessary, independent, non-duplicative deliverable.
- Never exceed four roles; four is a safety cap, not a target.
- Prefer the central specialist over a generic reviewer when the concrete boundary is security, test strategy, or Web performance.
- Add `test-automator` only for explicitly requested, behaviorally clear test writes.
- Add `web-performance-auditor` only for Web-facing artifacts or named Web metrics.
- If a capability lacks an available role, Root covers it; never invent a replacement.

## Delegation Contract

Render exactly one user-facing routing receipt using the applicable literal template below. Do not wrap it in a code fence or add eligibility, rationale, recommendation, or announcement prose around it. This restriction applies to the routing message; later normal progress and final-result messages remain allowed.

Repeat `Child:` once per selected role in lineup order. Each `Child:` value contains the exact role name and one concise task summary. `Root:` contains one concise task summary; when an Explicit Delegation Request has no distinct Root Lane, summarize Root's coordination and integration instead of inventing work. Do not include steps, file scope, success criteria, verification, or deliverables in these summaries. Those details belong in the internal handoff.

Keep the literal field labels, exact role names, and Work Mode tokens in English. Write task summaries and the final action text in the user's language.

Under `ask`, render:

```text
Routing: ELIGIBLE
Child: `<exact-role>` — <concise task summary>
Root: <concise task summary>
Work Mode: <read-only | mixed | write-capable>
➡️ Dispatch Authorization: <direct approval question>
```

Then stop. Do not inspect, run, search, summarize, implement, or spawn before approval. After approval, dispatch the declared lineup without repeating the receipt. Refusal creates zero children; continue in Root without emitting a `ROOT_ONLY` receipt.

Under `auto`, render:

```text
Routing: ELIGIBLE
Child: `<exact-role>` — <concise task summary>
Root: <concise task summary>
Work Mode: <read-only | mixed | write-capable>
➡️ Dispatch: <immediate-start statement>
```

Then spawn the declared lineup in the same turn without asking a question and continue the declared Root responsibility.

If the same scope was already announced or dispatched, do not announce or dispatch it again after compact, resume, or another skill check.

## Dispatch and Handoffs

Spawn call policy:

- specify the target `agent_type`;
- set `fork_turns: "none"`;
- pass a self-contained handoff as the child prompt; and
- never pass temporary model or reasoning overrides.

Every handoff includes:

- `delegation_context`;
- `goal` and `success_criteria`;
- `scope_in` and `scope_out`;
- `relevant_context`;
- `constraints` and `deliverable`;
- `verification`;
- `write_policy` and `write_ownership`; and
- `open_questions`.

Use this recursion guard:

`delegation_context: delegated-subagent; parent Dispatch Authorization already granted; leaf child; do not invoke diverter, delegate, spawn descendants, or request another Dispatch Authorization; execute this handoff only`

The child is always a Leaf Child. Root alone owns decomposition, follow-up routing, integration, verification, and the final response.

## Root Progress and Integration

After an implicitly eligible dispatch, Root must make substantive, distinct, traceable progress on the declared Root Lane while the child is active. After an explicit dispatch with no distinct Root Lane, Root may coordinate and wait for the requested child before integration. Choose task-appropriate work under Outcome-Bounded Autonomy; do not force research, writing, planning, design, and code into one action checklist.

Root must:

- avoid duplicating the Child Lane;
- preserve successful results if another lane fails;
- map each child result into the final outcome;
- resolve stale or conflicting evidence rather than trusting it blindly; and
- apply proportional independent verification before completion.

## Child Reuse

For a related follow-up, prefer the same native child identity and send a follow-up to that child instead of spawning an equivalent replacement. A materially different scope may justify a new bounded child. Never redispatch the same normalized scope merely because a prior turn completed or the Root Session compacted.

Root may integrate and verify a received child result immediately. Confirm that the current child turn is terminal or idle only before sending a related follow-up intended to create a new turn; mailbox output alone is not terminal-status proof.

If a prior child cannot continue, Root retains ordinary accountability and completes or reassigns the outcome without a special recovery protocol.

## Write Ownership

Every write-capable Root or Child Lane declares exclusive Write Ownership over a mutable artifact or bounded scope.

- Parallel writes require clearly disjoint ownership.
- Overlapping ownership is serialized.
- Mixed work starts read-first and establishes ownership before writes.
- Never weaken Codex permissions, sandboxing, approval behavior, or task authorization.
- Do not invent a lock manager; declared ownership and proportional verification are the boundary.

## Sanitized Failure Reporting

- Ordinary task-shape non-delegation is already covered by the single Routing Receipt; do not narrate it again.
- Explicit opt-out stays silent; if an internal failure recovers successfully, continue silently.
- Pre-activation native absence stays silent and Root completes the task.
- A missing role is dropped and covered by Root without inventing a substitute.
- If a spawn or child fails after Dispatch Announcement, report the affected lane briefly, preserve successful lanes, and let Root take over when possible.
- If an explicitly requested Diverter skill fails to load before the Native Capability Check, report that briefly and ask whether to continue in the Root Session.
- If user action is required, explain only the problem and required action.

Never expose skill aliases, plugin cache paths, `SKILL.md` loading, retry mechanics, or other internal recovery details.

## References

Read only as needed:

- `references/session-contract.md` only for Missing-Contract fallback Preflight;
- `references/decision-rules.md` for non-normative classification examples;
- `references/role-lineups.md` for capability mapping;
- `references/handoff-schema.md` for leaf handoffs and ownership; and
- `references/delegation-contract.md` for receipt semantics and failure cases; the literal templates live only in this skill.
