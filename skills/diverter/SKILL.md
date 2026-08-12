---
name: diverter
description: "Use when an explicit delegation request or an eligible task has one bounded independent Child Lane and one distinct useful Root Lane. Apply the loaded ask or auto Delegation Policy. Do not use for Mode Control, delegated subagent handoffs, unclear requests, explicit opt-out, or when native proactive delegation owns orchestration."
---

<NATIVE-PROACTIVE-DELEGATION-STOP>
If higher-priority session instructions explicitly state that proactive multi-agent delegation is active, skip this skill, even when explicitly invoked. Do not mention Diverter, select a lineup, request Dispatch Authorization, or spawn children. Continue the current task under the native policy.
</NATIVE-PROACTIVE-DELEGATION-STOP>

<SUBAGENT-STOP>
If the current task explicitly says it is a delegated subagent task or includes `delegation_context: delegated-subagent`, skip this skill. Execute only the assigned handoff. Never select another lineup, request Dispatch Authorization, spawn a descendant, or transfer orchestration ownership.
</SUBAGENT-STOP>

# Diverter

## Mission

Diverter distills Ultra-inspired task decomposition and role routing for ordinary GPT-5.6 Codex sessions. The Root Session remains the Orchestration Owner and is accountable for the complete user outcome.

For an eligible task:

- choose the Smallest Sufficient Lineup of 1-4 available roles;
- assign every child one bounded independent Child Lane;
- declare the distinct useful Root Lane that will progress while children run;
- state exactly one Work Mode: `read-only`, `mixed`, or `write-capable`;
- apply the loaded `ask` or `auto` Delegation Policy; and
- integrate and proportionally verify child results before answering the user.

If the task is ineligible or native dispatch is unavailable, continue silently in the Root Session.

## Eligibility

The SessionStart Delegation Gate is a coarse checkpoint. This skill is the detailed authority for eligibility, lineup selection, policy, ownership, dispatch, reuse, and integration.

Implicit delegation requires all of the following:

1. one bounded independent Child Lane with a clear deliverable;
2. one distinct useful Root Lane that can make substantive progress while the child is active;
3. a material accuracy, speed, or context benefit from running the lanes separately;
4. non-duplicative scopes; and
5. safe read/write ownership.

No effective Root Lane means no implicit delegation. Waiting, supervising, promising to synthesize later, or repeating the Child Lane is not a Root Lane. A second child is never required merely to meet the threshold.

An explicit `$diverter` invocation or explicit request to use subagents bypasses the implicit benefit threshold. It does not bypass task clarity, explicit opt-out, Native Proactive Delegation ownership, Codex permissions, sandboxing, leaf-child rules, or Write Ownership.

An explicitly selected focused skill may keep its core workflow and Root Lane while Diverter supplies a Supporting Child for a separate, non-duplicative deliverable. Respect higher-priority and focused-skill constraints. Do not replace or duplicate the focused skill.

Do not implicitly delegate:

- trivial, wording-only, or strongly sequential work;
- ambiguous work that needs clarification;
- a one-path fact lookup that blocks all other progress;
- duplicate Root/child investigation;
- tightly coupled or overlapping writes;
- vague security, test, performance, or release language without a concrete artifact or boundary;
- an explicit subagent opt-out;
- a delegated-subagent handoff; or
- work already owned by Native Proactive Delegation.

## Decision Process

Follow this sequence:

1. Apply the Native Proactive Delegation and delegated-subagent stops above.
2. Execute `$diverter-mode` directly when explicitly invoked; never delegate Mode Control.
3. Honor explicit opt-out and clarify an unclear objective.
4. Resolve the Delegation Policy.
5. Identify the Child Lane, Root Lane, expected benefit, and Work Mode.
6. Perform the Native Capability Check before mentioning Diverter or proposing a lineup.
7. Select the Smallest Sufficient Lineup from available roles.
8. Produce the policy-specific Delegation Contract.
9. Dispatch only after Dispatch Authorization.
10. Continue the Root Lane, collect child results, resolve conflicts, verify proportionally, and integrate the final outcome.

## Delegation Policy

Resolve policy in this order:

1. the stops and Mode Control bypasses above;
2. Native Proactive Delegation ownership from higher-priority instructions;
3. an explicit Task Policy Override in the current user message;
4. the loaded `delegation_policy` from the Delegation Gate; and
5. `ask` when no valid policy is available.

Valid values are `delegation_policy: ask` and `delegation_policy: auto`.

- `ask`: recommend one lineup, ask for approval, and stop before task work or spawning. A refusal creates zero children and Root continues.
- `auto`: publish one Dispatch Announcement, then spawn immediately in the same turn without a permission question, regardless of Work Mode.

Task Policy Overrides apply only to the current task. Work Mode describes write risk; it never creates a hidden third policy.

## Native Capability Check

Diverter uses the Native Subagent Backend exclusively. Before activation, confirm that the current host exposes native role-specific spawning with a target `agent_type`, supports isolated `fork_turns: "none"`, and exposes the requested installed role.

- Do not require or pass runtime `model` or `reasoning_effort` overrides. The installed Bundled Subagent definition owns those settings.
- Do not use a generic child as a substitute for a missing requested role.
- If native subagent dispatch is unavailable, do not announce Diverter, report a backend problem, or ask what to do. Continue silently in the Root Session.
- If a role is unavailable, drop it and keep its capability in the Root Lane. If no useful role remains, continue silently in Root.

## Capability Selection

Select capabilities first, then map only to roles available in the current Codex environment.

| Capability | Preferred role | Default mode |
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

- Default to one child plus the Root Lane.
- Add another child only for another necessary, independent, non-duplicative deliverable.
- Never exceed four roles; four is a safety cap, not a target.
- Prefer the central specialist over a generic reviewer when the concrete boundary is security, test strategy, or Web performance.
- Add `test-automator` only for explicitly requested, behaviorally clear test writes.
- Add `web-performance-auditor` only for Web-facing artifacts or named Web metrics.
- If a capability lacks an available role, Root covers it; never invent a replacement.

## Delegation Contract

Every policy branch conveys, in order:

1. why delegation materially fits;
2. exactly one lineup with an assignment for each exact role name;
3. the distinct Root Lane;
4. exactly one Work Mode; and
5. the policy-specific ending.

Keep the message conversational, concise, and in the user's language when natural. Do not list alternatives or imply results already exist.

Under `ask`, end with a direct approval question matched to the Work Mode and stop. Do not inspect, run, search, summarize, implement, or spawn before approval.

Under `auto`, make a declarative Dispatch Announcement, state that dispatch starts now and the Root Lane will continue, ask no question, and spawn in the same turn.

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

After dispatch, Root must make substantive, distinct, traceable progress on the declared Root Lane while the child is active. Choose task-appropriate work under Outcome-Bounded Autonomy; do not force research, writing, planning, design, and code into one action checklist.

Root must:

- avoid duplicating the Child Lane;
- preserve successful results if another lane fails;
- map each child result into the final outcome;
- resolve stale or conflicting evidence rather than trusting it blindly; and
- apply proportional independent verification before completion.

## Child Reuse

For a related follow-up, prefer the same native child identity and send a follow-up to that child instead of spawning an equivalent replacement. A materially different scope may justify a new bounded child. Never redispatch the same normalized scope merely because a prior turn completed or the Root Session compacted.

If a prior child cannot continue, Root retains ordinary accountability and completes or reassigns the outcome without a special recovery protocol.

## Write Ownership

Every write-capable Root or Child Lane declares exclusive Write Ownership over a mutable artifact or bounded scope.

- Parallel writes require clearly disjoint ownership.
- Overlapping ownership is serialized.
- Mixed work starts read-first and establishes ownership before writes.
- Never weaken Codex permissions, sandboxing, approval behavior, or task authorization.
- Do not invent a lock manager; declared ownership and proportional verification are the boundary.

## Sanitized Failure Reporting

- Intentional non-delegation stays silent; if an internal failure recovers successfully, continue silently.
- Pre-activation native absence stays silent and Root completes the task.
- A missing role is dropped and covered by Root without inventing a substitute.
- If a spawn or child fails after Dispatch Announcement, report the affected lane briefly, preserve successful lanes, and let Root take over when possible.
- If an explicitly requested Diverter skill fails to load before the Native Capability Check, report that briefly and ask whether to continue in the Root Session.
- If user action is required, explain only the problem and required action.

Never expose skill aliases, plugin cache paths, `SKILL.md` loading, retry mechanics, or other internal recovery details.

## References

Read only as needed:

- `references/decision-rules.md` for classification examples;
- `references/role-lineups.md` for capability mapping;
- `references/handoff-schema.md` for leaf handoffs and ownership; and
- `references/delegation-contract.md` for policy-specific wording.
