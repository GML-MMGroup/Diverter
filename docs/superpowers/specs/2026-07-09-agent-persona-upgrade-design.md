# Agent Persona Upgrade Design

Date: 2026-07-09
Repository: `917Dhj/cast-subagents`
Source handoff: `/Users/dinghongjing/Downloads/cast_subagents_agent_persona_upgrade_plan.md`

## Goal

Improve the bundled `cast-subagents` subagent roles by adapting the core strengths of `addyosmani/agent-skills` Agent Personas into this repository's Codex TOML role style.

This is a role and lineup-rule upgrade. It must not change the core `cast-subagents` product behavior:

- Advisory only: suggest a lineup, never auto-spawn.
- Approval before work: do not inspect task files, run commands, search docs, or start task content before user approval.
- Exactly one recommended lineup.
- Maximum 4 roles per lineup.
- Always state one work mode: `read-only`, `mixed`, or `write-capable`.
- Delegated subagent handoffs with `delegation_context: delegated-subagent` bypass cast-subagents to avoid recursive suggestions.

## Chosen Approach

Use a rewritten adaptation of Addy Osmani's persona ideas, not a copy-paste port.

The new role definitions should preserve the behavior advantages of the upstream personas: clear specialist scope, stable output format, hard rules, and domain-specific review frameworks. They should be expressed in the existing `cast-subagents` TOML style, with concise but complete `developer_instructions`.

This is not the simplified version. The new roles should be substantial enough to guide real subagent behavior, while avoiding long copied prose from `addyosmani/agent-skills`.

## Role Model

Add three new read-only quality roles under `agents/categories/04-quality/`.

### `security-auditor`

Purpose: security-focused audit of exploitable risk and trust boundaries.

Use when the task explicitly involves:

- trust boundaries
- authentication or authorization
- sessions, tokens, OAuth, password reset, cookies
- secrets, sensitive data, PII, multi-tenant data
- user input, injection, XSS, SSRF, open redirects, uploads
- webhooks and third-party integrations
- dependency or supply-chain risk
- LLM, agent, plugin, or tool permission safety

Do not use for:

- ordinary PR review with only generic "security" as a checklist word
- vague requests like "make this secure" without a concrete artifact or boundary
- non-security code style or maintainability review
- destructive external testing

Required framework:

- Start from trust boundaries.
- Review auth/authz and server-side enforcement.
- Review secrets and sensitive-data exposure.
- Review input handling and injection surfaces.
- Review webhooks and third-party integrations.
- Review dependency and supply-chain risk.
- Review LLM/tool permissions, prompt injection, destructive actions, context leakage, and recursion/token limits when relevant.

Output must include:

- summary by severity
- scope reviewed
- findings with location, description, impact, exploitability, recommendation, and verification
- positive observations
- unverified runtime/config checks

Hard rules:

- Read-only.
- Focus on practical, exploitable issues.
- Critical/High findings need exploitability conditions.
- Do not present hypotheses as facts.
- Every finding needs a specific mitigation.

### `test-engineer`

Purpose: read-only test strategy and coverage-gap analysis.

Use when the task asks:

- what tests are missing
- whether existing tests are enough
- how to prove a bug fix
- which test level is appropriate
- how to design targeted regression coverage before writing tests

Do not use for:

- direct test implementation after behavior is already clear; use `test-automator`
- vague "add some tests" requests without a known behavior boundary, unless the task is to clarify test strategy first
- coverage-number chasing without risk-based value
- broad framework migration

Required framework:

- Read the behavior under test before recommending tests.
- Identify public API or user-observable behavior.
- Inspect existing test style and conventions.
- Choose the lowest test level that captures the behavior: unit, integration, or E2E.
- Use Prove-It regression planning for bugs: define a test expected to fail before the fix and pass after it.
- Prioritize data loss, security, permissions, core business behavior, and common regression paths.

Output must include:

- scope reviewed
- current coverage
- coverage gaps
- recommended tests with level, behavior, risk, expected current result, and priority
- implementation notes
- smallest safe handoff to `test-automator`

Hard rules:

- Read-only.
- Test behavior, not implementation details.
- Mock external boundaries, not ordinary internal functions.
- Do not recommend low-value tests just to increase counts.
- Mark conclusions that require running tests or coverage tools.

### `web-performance-auditor`

Purpose: read-only Web performance audit.

Use when the task explicitly concerns:

- Core Web Vitals
- LCP, INP, CLS
- Lighthouse, PageSpeed Insights, CrUX, DevTools traces
- frontend routes, pages, or components
- loading, rendering, JavaScript, network, caching, images, fonts, bundle size

Do not use for:

- non-Web performance tasks such as CLI parser speed, backend algorithm speed, or database-only tuning
- generic code review
- micro-optimization without evidence
- projects where the Web stack cannot be identified

Required framework:

- Identify the Web framework or rendering model before framework-specific advice.
- Support Quick mode when no performance artifacts are available: source-level findings only, every finding labeled `potential impact`.
- Support Deep mode when Lighthouse, PageSpeed, CrUX, DevTools trace, or live measurement data is available.
- Keep lab, field, and trace data separate.
- Cover Core Web Vitals, loading, rendering/JavaScript, and network/caching risks.

Output must include:

- scorecard with metric value, source, target, and status
- artifacts used
- framework detected
- mode: Quick or Deep
- findings with area, location, impact, recommendation, and verification
- positive observations
- next measurements

Hard rules:

- Read-only.
- Never fabricate metrics.
- Without data, write `not measured`.
- Static source analysis can only claim `potential impact`.
- Do not recommend framework-specific patterns for the wrong stack.

## Existing Role Enhancements

### `reviewer`

Keep the name `reviewer` for compatibility. Strengthen it with a Staff Engineer-style review framework:

- correctness
- readability and maintainability
- architecture and contracts
- light security pass
- tests and verification
- performance and operational risk

Boundaries:

- Not a deep security audit; recommend `security-auditor` when security is central.
- Not a test strategy specialist; recommend `test-engineer` when coverage planning is central.
- Not a Web performance auditor; recommend `web-performance-auditor` for Web performance tasks.
- Does not write tests; use `test-automator` for implementation.

Output should use stable severity buckets:

- `Critical`: blocks merge or release
- `Important`: should fix before merge
- `Suggestion`: optional improvement

### `test-automator`

Keep `test-automator` as the write-capable test implementation role.

Enhance its behavior:

- implement the smallest targeted regression tests after scope is clear
- follow `test-engineer` output when present
- use Prove-It for bug regression tests
- keep tests deterministic
- avoid test framework migrations and broad rewrites
- run the relevant test command when possible
- report what was changed, what command ran, the result, and residual risk

## Selection Rules

The lineup engine remains capability-first, not persona-first.

Add capabilities:

| Capability | Preferred role | Work mode |
| --- | --- | --- |
| security audit | `security-auditor` | `read-only` |
| test strategy | `test-engineer` | `read-only` |
| web performance audit | `web-performance-auditor` | `read-only` |

Keep existing capabilities:

| Capability | Preferred role | Work mode |
| --- | --- | --- |
| code mapping | `code-mapper` | `read-only` |
| risk review / code review | `reviewer` | `read-only` |
| docs/API verification | `docs-researcher` | `read-only` |
| search | `search-specialist` | `read-only` |
| synthesis | `knowledge-synthesizer` | `read-only` |
| planning | `task-distributor` | `read-only` |
| test automation | `test-automator` | `write-capable` |

Common lineups:

| Task shape | Recommended lineup | Work mode |
| --- | --- | --- |
| General PR review | `reviewer + code-mapper` | `read-only` |
| Security-sensitive review | `security-auditor + code-mapper + reviewer` | `read-only` |
| Auth / permission / token flow review | `security-auditor + code-mapper` | `read-only` |
| LLM / agent tool safety review | `security-auditor + code-mapper + docs-researcher` | `read-only` |
| Test coverage analysis | `test-engineer + code-mapper` | `read-only` |
| Add targeted regression tests | `test-engineer + test-automator + code-mapper` | `mixed` |
| Web performance source audit | `web-performance-auditor + code-mapper` | `read-only` |
| Web performance audit with supplied metrics | `web-performance-auditor` | `read-only` |
| Pre-ship quality gate | `reviewer + security-auditor + test-engineer + code-mapper` | `read-only` |

Compression rules:

- Ordinary PR review stays `reviewer + code-mapper`.
- Do not add `security-auditor` unless there is a real security boundary or explicit security audit request.
- Do not add `test-engineer` unless the task asks about tests, coverage, proof, or test strategy.
- Do not add `test-automator` unless test writing/updating is explicitly requested and scope is clear enough to be safe.
- Do not add `web-performance-auditor` unless the target is a Web app, route, page, component, or Web metric artifact.
- If more than 4 roles are triggered, keep the central risk specialist and `code-mapper`, then drop non-core roles.
- Do not present several alternative lineups; recommend exactly one.

## Files To Change

Add:

- `agents/categories/04-quality/security-auditor.toml`
- `agents/categories/04-quality/test-engineer.toml`
- `agents/categories/04-quality/web-performance-auditor.toml`

Modify:

- `agents/categories/04-quality/reviewer.toml`
- `agents/categories/04-quality/test-automator.toml`
- `SKILL.md`
- `references/role-lineups.md`
- `references/decision-rules.md`
- `references/examples-positive.md`
- `references/examples-negative.md`
- `references/suggestion-contract.md` only if needed for wording boundaries
- `README.md`
- `README.zh.md`
- `evals/prompts.yaml`
- `evals/rubric.md`
- `evals/scenarios.md`
- `evals/results-template.md` only if prompt IDs require it
- `CHANGELOG.md`

Do not modify:

- `scripts/install-agent-roles.py`, unless verification finds hard-coded role names. It currently discovers `agents/categories/*/*.toml`.
- `agents/openai.yaml`, unless a role list is added later.
- AGENTS gate or approval-before-work behavior.

## Evaluation Updates

Add positive prompt cases for:

- security-sensitive review
- LLM / agent tool safety review
- test coverage analysis
- targeted regression tests
- Web performance audit
- pre-ship quality gate

Add negative or edge cases for:

- non-Web performance must not use `web-performance-auditor`
- generic small PR review must not inflate to 4 roles
- unclear test writing request should clarify or start with `test-engineer`, not immediate `test-automator`
- vague "make this secure" should clarify unless concrete files, flows, or trust boundaries are provided

Rubric additions:

- correct specialist role selected when explicit signal exists
- unrelated specialist role not added
- lineup still at 4 roles or fewer
- mode remains correct
- write-capable test automation is not suggested before behavior scope is clear
- approval-before-work is preserved

## Verification

Run after implementation:

```bash
git diff --check
/opt/anaconda3/bin/python3 -m compileall -q scripts
```

Manual consistency checks:

- role names match across TOML, `SKILL.md`, references, README files, and eval prompts
- README and README.zh role counts say 10
- common lineups do not exceed 4 roles
- generic PR review examples do not include every quality specialist
- Web performance examples are Web-specific
- `test-engineer` is read-only and `test-automator` remains write-capable
- no advisory-only or approval-gate rule was weakened

## Out Of Scope

- automatic subagent spawning
- new orchestration engine
- new install script behavior
- new role directory taxonomy unless needed later
- copying upstream persona files verbatim
- adding Web performance tooling or benchmark runners
- adding a full automated eval runner

## Open Implementation Notes

- Keep TOML role files substantial but not bloated.
- Prefer existing repository wording patterns over upstream phrasing.
- Add attribution in README acknowledgments: role design was informed by `addyosmani/agent-skills`, adapted for Codex TOML roles and cast-subagents advisory lineup selection.
- `docs/` is local planning material and is intentionally ignored by git.
