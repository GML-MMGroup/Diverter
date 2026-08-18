# Role Lineups

Choose capabilities first. Then keep only the roles that are available in the current Codex environment. The tables suggest Child Lanes; Root always keeps a distinct useful Root Lane for implicit delegation.

## Capability Map

| Capability | Preferred bundled role | Use when | Missing-role behavior |
| --- | --- | --- | --- |
| code mapping | `code-mapper` | tracing code paths, ownership, or execution flow | Drop the capability or handle mapping in the main thread after Dispatch Authorization. |
| code review | `reviewer` | general PR review, correctness, maintainability, contracts, regressions, and light security/test risk | Handle in the main thread or use another explicit review role if one is available. |
| security audit | `security-auditor` | auth, authorization, secrets, user input, webhooks, SSRF, dependencies, LLM/tool permissions, or exploitable vulnerability risk | Mention that security audit is not delegated; do not substitute a generic reviewer when security is central. |
| docs/API verification | `docs-researcher` | verifying a named documentation or API/framework contract | Mention that docs verification is not delegated; do not substitute an unknown role. |
| search | `search-specialist` | gathering high-signal evidence for open-ended options or strategy comparisons | Drop if code mapping or named contract verification already covers the task. |
| synthesis | `knowledge-synthesizer` | consolidating multiple research outputs | Synthesize in the main thread after other agents return. |
| planning | `task-distributor` | decomposing broad work into bounded subtasks | Plan in the main thread if no planning role is available. |
| test strategy | `test-engineer` | coverage gaps, test plan, test level choice, or Prove-It regression planning | Handle test strategy in the main thread; do not jump directly to write-capable test automation. |
| test automation | `test-automator` | writing or updating targeted tests after scope is clear | Do not suggest write-capable testing if unavailable. |
| Web performance audit | `web-performance-auditor` | Core Web Vitals, Lighthouse, frontend route/component performance, loading, rendering, network, caching, images, fonts, or bundle risks | Handle in the main thread or skip the specialist if the task is not Web-specific. |

## Common Child Lanes

| Scenario | Child capability | Preferred role when available | Example Root Lane | Work mode |
| --- | --- | --- | --- | --- |
| General branch review | independent correctness review | `reviewer` | map the changed execution path and integrate findings | read-only |
| Docs/API assumption | official contract verification | `docs-researcher` | trace the implementation and frame the decision | read-only |
| Security-sensitive flow | concrete trust-boundary audit | `security-auditor` | map the flow and assess non-security regressions | read-only |
| Test coverage analysis | independent Prove-It strategy | `test-engineer` | map behavior and existing fixtures | read-only |
| Targeted regression implementation | bounded test artifact | `test-automator` | verify the behavior boundary and integrate the test result | mixed |
| Web performance evidence | named metric audit | `web-performance-auditor` | map route/component constraints and synthesize risks | read-only |
| Focused skill workflow | non-duplicative supporting check | matching specialist | focused skill keeps its core workflow | task-dependent |
| Option research | bounded evidence collection | `search-specialist` | define comparison criteria and synthesize the decision | read-only |
| Broad planning | one bounded planning package | `task-distributor` | ground constraints or develop another independent deliverable | read-only |

## Compression Rules

- Recommend exactly one lineup made only of available roles.
- Start with one role. Add another only for another necessary, independent Child Lane.
- If one unavailable capability is non-essential, drop it and keep the remaining useful lineup.
- If a missing capability is important, mention that the main thread can cover it after Dispatch Authorization.
- If no relevant roles are available, stay silent during implicit checks and continue normally.
- Never recommend 4 roles only to sound thorough.
- Ordinary PR review defaults to one useful specialist alongside a substantive Root Lane; do not add every quality role.
- For repository analysis plus official contract verification, use `docs-researcher` for the contract and keep repository mapping in Root.
- Add `security-auditor` only for concrete security boundaries or explicit security audit requests.
- Add `test-engineer` only for test strategy, coverage gaps, proof, or regression planning.
- Add `test-automator` only when the user explicitly asks for test writes and the behavior scope is clear.
- Add `web-performance-auditor` for Web-facing performance work or named metrics such as LCP, INP, or CLS.
- For non-Web performance, use `code-mapper + reviewer` only if the task is multi-lane.
- If more than 4 roles are triggered, keep only the most necessary independent deliverables; Root covers the rest.

## Write-Safety Rules

- `test-automator` is write-capable because it may edit tests.
- Mixed lineups start read-first. Under `ask`, stay within the approved sequence; under `auto`, continue once ownership is clear.
- Do not suggest write-capable implementation work unless an explicit write-capable role for that work is available.
- Every write-capable lane declares an exclusive mutable artifact or bounded scope. Parallel writes require disjoint ownership; overlap is serialized.
