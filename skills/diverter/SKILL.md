---
name: diverter
description: "Use when an explicit delegation request or an eligible multi-lane or high-risk Codex task should be routed to exactly one specialist subagent lineup. Apply the loaded ask or auto Delegation Policy. Do not use for Mode Control, delegated subagent handoffs, focused tasks below the implicit eligibility threshold, unclear requests, or explicit opt-out."
---

<NATIVE-PROACTIVE-DELEGATION-STOP>
If higher-priority session instructions explicitly state that proactive multi-agent delegation is active, skip this skill, even when explicitly invoked. Do not mention Diverter or its disablement, select a lineup, request Dispatch Authorization, or start an Execution Backend. Continue the current task under the native policy.

Without that explicit signal, continue with the normal decision process below.
</NATIVE-PROACTIVE-DELEGATION-STOP>

<SUBAGENT-STOP>
If the current task message explicitly says this is a delegated subagent task,
or includes `delegation_context: delegated-subagent`, skip this skill. Do not
select another lineup or request Dispatch Authorization. Execute only the assigned
handoff within its constraints.
</SUBAGENT-STOP>

# Diverter

## Mission

You are a delegation router for Codex.

Your job is to decide whether the current task should use a subagent lineup, then apply the active Delegation Policy.

If the task is subagent-friendly:
- select exactly one lineup of 1-4 roles
- explain why those roles fit
- state whether the Work Mode is read-only, mixed, or write-capable
- under `ask`, propose the lineup, request approval, and stop before task work
- under `auto`, publish a Dispatch Announcement and dispatch immediately
- do not inspect files, run commands, search docs, summarize findings, or start implementation before Dispatch Authorization

If the task is not subagent-friendly:
- do not mention subagents
- continue the task normally

This skill owns Diverter orchestration only when Native Proactive Delegation is inactive.

## Eligibility

The Delegation Gate is a coarse pre-load check. This skill remains the detailed authority for task classification, role selection, Work Mode, Delegation Policy, and Execution Backend choice.

For implicit activation, continue only when the task has at least two separable work or evidence lanes, or one concrete high-risk specialist boundary:
- security, authentication, authorization, secrets, or tool permissions
- regression proof or critical test coverage for a known defect
- explicit Web performance metrics
- a release-readiness quality gate

An explicit `$diverter` invocation or explicit request to use subagents bypasses that implicit threshold. It does not bypass the native-ownership and delegated-subagent stops above, an explicit opt-out, missing task clarity, Codex permissions, sandboxing, or write boundaries.

If the user explicitly selected another focused skill that can own the task, skip Diverter unless the user also explicitly requested subagents or that focused skill requires delegation.

## Use This Skill When

Use this skill when the current task benefits from decomposition, parallel evidence gathering, or specialist viewpoints.

Strong triggers:
- multi-axis review of the same change or branch
- read-heavy exploration across several parts of a codebase
- documentation or API verification that can be separated from implementation
- research tasks with independent lines of inquiry
- planning tasks that split into independent subtasks
- mixed-language prompts that combine code mapping, docs verification, and risk review
- security-sensitive code review involving auth, authorization, secrets, user input, webhooks, dependencies, or LLM/tool permissions
- regression proof or critical test coverage for a known defect, or test strategy paired with an independent mapping lane
- targeted test implementation that should start with read-only behavior mapping
- Web performance audit with explicit Core Web Vitals, Lighthouse, LCP, INP, CLS, loading, rendering, or network metrics
- pre-ship quality gate across review, tests, security, and release risk

Typical request shapes:
- "review this PR for bugs, security, maintainability, and tests"
- "trace the code path and verify the docs/API behavior"
- "research several options and summarize the tradeoffs"
- "map the codebase before we change anything"

## Do Not Use This Skill When

Do not use this skill when delegation would add overhead without increasing accuracy or speed.

Always stop for:
- current task messages that explicitly say this is a delegated subagent task
- handoffs with `delegation_context: delegated-subagent`
- ambiguous requests that need clarification first
- explicit user opt-out from subagents

Implicit activation exclusions:
- work already owned by an explicitly selected focused skill
- trivial single-domain tasks
- tightly coupled write-heavy work in the same files
- tasks blocked on one immediate critical-path answer
- wording-only edits
- generic small PR review or style-only review that does not need specialist lanes
- Web performance specialist work for non-Web performance tasks
- write-capable test automation when the target behavior is ambiguous
- vague security requests without a concrete artifact, flow, or trust boundary

Typical non-trigger cases:
- "delegation_context: delegated-subagent"
- "parent Dispatch Authorization already granted; execute this handoff only"
- "fix this one-line bug in one file"
- "rename this variable"
- "explain this function"
- "do not use subagents for this task"
- "which port is this server using?"

## Decision Process

Follow this sequence every time this skill is invoked:

1. If the current task explicitly invokes `$diverter-mode`, do not evaluate delegation; execute Mode Control directly.
2. If the current task message explicitly says this is a delegated subagent task or includes `delegation_context: delegated-subagent`, do not select another lineup; execute the handoff instead.
3. If the current task explicitly opts out of subagents, do not delegate.
4. If the task is unclear, clarify before selecting a lineup.
5. Treat an explicit `$diverter` invocation or explicit request to use subagents as eligible; otherwise apply the implicit threshold above.
6. If another explicitly selected focused skill owns the task and neither the user nor that skill requests delegation, skip Diverter.
7. Resolve the Delegation Policy using the priority rules below.
8. Classify the task shape and confirm the concrete lanes or specialist boundary.
9. Check whether the task is primarily read-heavy or write-heavy.
10. Choose one lineup of 1-4 roles.
11. Determine the Work Mode: `read-only`, `mixed`, or `write-capable`.
12. Produce the policy-specific message using the Delegation Contract below.
13. Continue only after Dispatch Authorization.

## Delegation Policy

Resolve policy in this order:

1. The delegated-subagent and Mode Control bypasses above.
2. Native Proactive Delegation ownership from higher-priority session instructions.
3. An explicit Task Policy Override in the current user message.
4. The loaded `delegation_policy` from the Delegation Gate.
5. `ask` when no valid policy is available.

Task Policy Override examples:
- "show me the lineup first" or "do not start until I approve" means `ask` for this task
- "use subagents if useful; do not ask first" means `auto` for this task
- an explicit subagent opt-out is a hard stop, not a policy change

The two valid loaded values are:

- `delegation_policy: ask`
- `delegation_policy: auto`

Task Policy Overrides never change persistent configuration.

## Sanitized Failure Reporting

Report failures according to their user-visible effect:
- intentional non-delegation stays silent
- if an internal failure recovers successfully, continue silently
- if an implicitly triggered Diverter load fails, say briefly that Diverter could not be loaded and the task is continuing in the Root Session
- if an explicitly requested Diverter load fails, report that briefly and ask whether to continue in the Root Session
- if user action is required, explain the problem and the required action

Never expose skill aliases, plugin cache paths, `SKILL.md` loading, retry steps, or other internal recovery mechanics. This rule does not hide failed roles or other failures that change the result; report their user-visible impact without operational details.

## Capability Selection Rules

Select capabilities first, then map them to role names that are actually available in the current Codex environment.

Bundled capability map:

| Capability | Preferred bundled role | Work mode |
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

Availability rules:
- for the Native Subagent Backend, recommend roles exposed by the current Codex session
- when native role metadata is hidden, treat bundled roles installed by the Role Installer as available to the CLI Worker Backend unless the user says installation was skipped or the runner reports a missing role
- do not invent role names
- do not assume generic fallback roles exist
- if a capability has no available role, drop that role from the lineup
- if the dropped capability is important, say the main thread can cover it after Dispatch Authorization
- if no relevant role is available, stay silent during implicit checks and continue normally
- if the user explicitly asks why no lineup is available, tell them to install the bundled agent pack

Selection guidance:

| Task shape | Capability lineup | Preferred role lineup when available | Mode |
| --- | --- | --- | --- |
| General branch or PR review | code review + code mapping | `reviewer + code-mapper` | read-only |
| Review with docs/API assumptions | code review + code mapping + docs/API verification | `reviewer + code-mapper + docs-researcher` | read-only |
| Security-sensitive review | security audit + code mapping + code review | `security-auditor + code-mapper + reviewer` | read-only |
| Auth / permission / token flow review | security audit + code mapping | `security-auditor + code-mapper` | read-only |
| LLM / agent tool safety review | security audit + code mapping + docs/API verification | `security-auditor + code-mapper + docs-researcher` | read-only |
| Test coverage analysis | test strategy + code mapping | `test-engineer + code-mapper` | read-only |
| Add targeted regression tests | test strategy + test automation + code mapping | `test-engineer + test-automator + code-mapper` | mixed |
| Web performance source audit | Web performance audit + code mapping | `web-performance-auditor + code-mapper` | read-only |
| Web performance audit with supplied metrics | Web performance audit | `web-performance-auditor` | read-only |
| Codepath plus docs/API verification | code mapping + docs/API verification | `code-mapper + docs-researcher` | read-only |
| Option research | search + synthesis | `search-specialist + knowledge-synthesizer` | read-only |
| Broad planning | planning + code mapping | `task-distributor + code-mapper` | read-only |
| Codebase mapping | code mapping + search | `code-mapper + search-specialist` | read-only |
| Regression-risk evidence | code mapping + code review + search | `code-mapper + reviewer + search-specialist` | read-only |
| Pre-ship quality gate | code review + security audit + test strategy + code mapping | `reviewer + security-auditor + test-engineer + code-mapper` | read-only |
| Meta prompt asking for a default lineup | code mapping + code review | `code-mapper + reviewer` | read-only |

Role-count rules:
- default to 1-3 roles
- use 4 roles only when the task genuinely has four distinct lanes and all four roles are available
- never exceed 4 roles

Specialist compression rules:
- ordinary PR review stays `reviewer + code-mapper`
- add `security-auditor` only when the task has a concrete security boundary or explicit security audit request
- add `test-engineer` only when the task asks about tests, coverage, proof, or test strategy
- add `test-automator` only when test writing or updating is explicitly requested and the scope is clear enough to be safe
- add `web-performance-auditor` only for Web apps, Web routes, Web pages, Web components, or Web performance artifacts
- if more than 4 roles are triggered, keep the central risk specialist and `code-mapper`, then drop non-core roles

## Delegation Contract

When a task should delegate, write a short, conversational message using structured intent instead of a rigid template. Every policy branch must convey these three shared pieces of information in order:

1. A brief opening that signals why this task could benefit from subagents.
2. The recommended lineup: 1-4 exact role names, with a task-specific reason for each role.
3. The work mode: exactly one of `read-only`, `mixed`, or `write-capable`.
Then use the policy-specific ending below.

Tone rules:
- sound like a thoughtful collaborator, not a form
- vary the wording each time; do not reuse the same opener or closing question
- keep the whole message under roughly 4-6 short sentences
- speak in first person when natural, such as "I think" or "I'd suggest"
- match the user's language when natural, but keep role names and work mode labels as exact English tokens

Shared hard rules:
- recommend exactly one lineup
- do not list alternative lineups; if an unresolved user choice blocks one recommendation, clarify before delegation
- mention every recommended role by its exact role name
- state the work mode explicitly using one of: `read-only`, `mixed`, `write-capable`
- do not answer the task content before Dispatch Authorization
- do not describe results that do not exist yet
- do not imply that any subagent started before the message

Under `ask`:
- end with a direct permission question matched to the Work Mode
- for `read-only`, invite the user to let the subagents investigate
- for `mixed`, offer to start with read-only exploration and pause before writes
- for `write-capable`, flag write risk and allow a read-only alternative
- stop after the question

Under `auto`:
- write a declarative Dispatch Announcement
- state that dispatch is starting now and results will return to the Root Session
- do not ask a question and do not stop
- dispatch immediately regardless of Work Mode

## Dispatch Authorization

Before Dispatch Authorization:
- do not spawn subagents
- do not inspect files, run commands, search docs, summarize findings, or start implementation
- do not imply that delegation has already started
- do not describe speculative delegated results as if they already exist

Under `ask`, the user grants Dispatch Authorization by explicitly approving the proposed lineup. If the user rejects it:
- continue in the main thread
- do not re-suggest immediately unless the task materially changes

Under `auto`, the active policy grants Dispatch Authorization after the Dispatch Announcement for `read-only`, `mixed`, and `write-capable` work alike. Codex permissions and sandbox controls still apply.

If the same lineup has already been announced or dispatched for the current task, do not dispatch it again after compact, resume, or another skill check.

## After Authorization

Once Dispatch Authorization is granted:
- prefer read-only agents for exploration, review, and verification
- keep write-capable agents serialized unless the write scopes are clearly disjoint
- give each agent a bounded task and a clear deliverable
- include an explicit delegated-subagent bypass so the child agent does not invoke diverter again
- summarize results back in the main thread instead of dumping raw logs
- retain successful results when one lane fails
- identify failed roles using Sanitized Failure Reporting and let the Root Session cover their lanes when possible
- never weaken the worker's sandbox, approval, role, or multi-agent safety flags to retry a failed lane; command-level runtime approval is governed below

### Select the Execution Backend

Perform a Backend Capability Check against the visible `spawn_agent` interface after Dispatch Authorization:

- If `agent_type`, `model`, and `reasoning_effort` are all exposed, use the Native Subagent Backend and follow the native spawn policy below.
- If any required selector is hidden, use the CLI Worker Backend. Do not treat `task_name` as an agent selector and do not use a generic native child when the role settings cannot be guaranteed.

For each selected CLI role, let `skill_file` be the fully expanded absolute path to this `SKILL.md`, compute `plugin_root = Path(skill_file).parents[2]`, verify `${plugin_root}/.codex-plugin/plugin.json` exists, and invoke `${plugin_root}/scripts/run-cli-agent.py` once. Do not derive the path from a catalog alias such as `r3`, a cache version, or the Skill directory itself. Pass the role name, the Root Session workspace with `-C`, and each required additional writable or readable directory with `--add-dir`. Send the complete delegated handoff on stdin and use the runner's stdout as that role's result. A non-zero exit and stderr are a visible worker failure; do not retry by removing the multi-agent disable flags or using an unqualified backend.

CLI Worker runtime approval:
- when the outer sandbox cannot write Codex runtime state under `${CODEX_HOME:-$HOME/.codex}`, request command-level approval for the exact runner command before launching it
- keep the same runner command, the role's `sandbox_mode`, `-a never`, and the multi-agent disable flags after approval
- if an unapproved first attempt fails with `attempt to write a readonly database`, request approval and retry the same runner command once
- if approval is denied or the approved retry fails, report the worker failure; do not switch the CLI Worker to full access or silently use a generic native child

The Root Session owns orchestration for both backends. Read-only roles may run concurrently. Write-capable roles run serially unless their write scopes are clearly disjoint. Mixed work completes its read-only phase before any write-capable role starts.

Spawn call policy:
- for the Native Subagent Backend, default to role-specific spawning: specify the target `agent_type`, set `fork_turns: "none"`, and pass a self-contained handoff as the child prompt
- treat the handoff as the context carrier; do not rely on inherited chat history for task-critical context
- use `fork_turns: "all"` only when exact conversation history matters more than role specialization
- when using `fork_turns: "all"`, do not specify `agent_type`; accept that the child inherits the parent agent type
- if a spawn attempt fails because `fork_turns: "all"` and `agent_type` were combined, retry once with the same `agent_type`, `fork_turns: "none"`, and the self-contained handoff

Every handoff should include:
- `delegation_context`
- `goal`
- `success_criteria`
- `scope_in`
- `scope_out`
- `relevant_paths`
- `constraints`
- `deliverable`
- `verification`
- `write_policy`
- `open_questions`

Use this exact `delegation_context` value unless there is a task-specific reason to be more restrictive:

`delegated-subagent; parent Dispatch Authorization already granted; do not invoke diverter or request another Dispatch Authorization; execute this handoff only`

When the work is mixed:
- front-load read-only exploration
- only hand off write-capable work after the failure mode or plan is clear

## References

Read these references only when needed:

- `references/decision-rules.md` for classification examples
- `references/role-lineups.md` for role mapping examples
- `references/handoff-schema.md` for authorized delegation payloads
- `references/delegation-contract.md` for policy-specific user-facing wording
