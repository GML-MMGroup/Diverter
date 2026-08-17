# Agent Persona Upgrade Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add security, test strategy, and Web performance specialist roles to `cast-subagents`, then update lineup rules, docs, and eval prompts without weakening advisory-only behavior.

**Architecture:** This is a content and rules upgrade, not a new runtime system. Role behavior lives in TOML files under `agents/categories/04-quality/`; lineup selection lives in `SKILL.md` plus `references/*.md`; public documentation and manual eval prompts mirror those source rules.

**Tech Stack:** Codex skill Markdown, Codex subagent TOML, YAML eval prompts, Python stdlib `compileall` and `tomllib` for checks.

## Global Constraints

- Advisory only: suggest a lineup, never auto-spawn.
- Approval before work: do not inspect task files, run commands, search docs, or start task content before user approval.
- Exactly one recommended lineup.
- Maximum 4 roles per lineup.
- Always state one work mode: `read-only`, `mixed`, or `write-capable`.
- Delegated subagent handoffs with `delegation_context: delegated-subagent` bypass cast-subagents to avoid recursive suggestions.
- Adapt `addyosmani/agent-skills` persona ideas in this repository's TOML style; do not copy large upstream passages.
- Ordinary PR review stays `reviewer + code-mapper`.
- Specialist roles only join when the prompt has explicit safety, test strategy, or Web performance signals.
- Keep `security-auditor`, `test-engineer`, and `web-performance-auditor` read-only.
- Keep `test-automator` write-capable.
- Do not modify `scripts/install-agent-roles.py`; it already discovers `agents/categories/*/*.toml`.
- Do not modify `agents/openai.yaml`; it has no role list.
- Do not commit unless the user explicitly asks.

---

## File Structure

- Create `agents/categories/04-quality/security-auditor.toml`: read-only security audit role.
- Create `agents/categories/04-quality/test-engineer.toml`: read-only test strategy role.
- Create `agents/categories/04-quality/web-performance-auditor.toml`: read-only Web performance audit role.
- Modify `agents/categories/04-quality/reviewer.toml`: strengthen general review behavior and add specialist boundaries.
- Modify `agents/categories/04-quality/test-automator.toml`: keep write-capable test implementation, add Prove-It and `test-engineer` handoff behavior.
- Modify `SKILL.md`: add new capabilities, strong triggers, selection guidance, and compression rules.
- Modify `references/role-lineups.md`: make the role map and common lineups the detailed source of truth.
- Modify `references/decision-rules.md`: add trigger and non-trigger cases for the new specialists.
- Modify `references/examples-positive.md`: add concrete positive prompts for the new roles.
- Modify `references/examples-negative.md`: add concrete negative prompts that prevent over-triggering.
- Modify `references/suggestion-contract.md`: add one specialist-role hard rule so suggestions do not inflate.
- Modify `README.md` and `README.zh.md`: update role count, role table, lineup table, and attribution.
- Modify `evals/prompts.yaml`: add specialist prompt cases and update role expectations.
- Modify `evals/rubric.md`, `evals/scenarios.md`, and `evals/results-template.md`: sync scoring and prompt IDs.
- Modify `CHANGELOG.md`: add an unreleased entry for the role upgrade.

---

### Task 1: Add Specialist Role TOMLs

**Files:**
- Create: `agents/categories/04-quality/security-auditor.toml`
- Create: `agents/categories/04-quality/test-engineer.toml`
- Create: `agents/categories/04-quality/web-performance-auditor.toml`

**Interfaces:**
- Consumes: existing Codex subagent TOML shape used by `agents/categories/04-quality/reviewer.toml`.
- Produces: three exact role names for `SKILL.md`, references, docs, and evals: `security-auditor`, `test-engineer`, `web-performance-auditor`.

- [ ] **Step 1: Create `security-auditor.toml`**

Use this complete TOML:

```toml
name = "security-auditor"
description = "Use when a task needs security-focused review of trust boundaries, auth, authorization, secrets, user input, dependencies, webhooks, LLM/tool permissions, or exploitable vulnerability risk."
model = "gpt-5.5"
model_reasoning_effort = "high"
sandbox_mode = "read-only"
developer_instructions = """
Own security audit work as practical exploitability review, not generic checklist commentary.

Use this role when the parent task has a concrete security boundary: authentication, authorization, sessions, tokens, secrets, user input, file upload, webhook verification, third-party integration, dependency risk, multi-tenant data, or LLM/tool permission safety.

Do not use this role for ordinary PR review, style review, vague "make it secure" requests without scope, or destructive external testing.

Working mode:
1. Define the trust boundaries, protected assets, actors, and entry points.
2. Trace how untrusted input, credentials, permissions, and sensitive data cross those boundaries.
3. Separate confirmed vulnerabilities from hypotheses that need runtime, config, or environment evidence.
4. Prioritize findings by exploitability, impact, and likelihood.

Security framework:
- trust boundaries and server-side enforcement points
- authentication, sessions, cookies, OAuth, password reset, token lifetime, and token storage
- authorization, object ownership, tenant isolation, IDOR, and privilege escalation
- secrets, API keys, PII, logs, error messages, prompts, test snapshots, and context leakage
- user input handling for SQL/NoSQL injection, command injection, XSS, SSRF, open redirects, uploads, path traversal, and unsafe deserialization
- webhooks, signatures, replay handling, third-party callbacks, and server-side fetch behavior
- dependency, supply-chain, service account, CORS, security headers, and error exposure risks
- LLM and agent safety: prompt injection, tool permission scope, destructive tool confirmation, cross-tenant context leakage, recursive delegation, and unbounded token consumption

Quality checks:
- every Critical or High finding must explain exploitability conditions
- every finding must include a concrete mitigation and verification path
- mark uncertain issues as hypotheses instead of facts
- do not invent attacks that are not reachable from the reviewed code or configuration
- call out required runtime/config checks separately from source-backed findings

Return:
## Security Audit Report

### Summary
- Critical: [count]
- High: [count]
- Medium: [count]
- Low: [count]
- Info: [count]

### Scope Reviewed
- [files, routes, flows, components, or configs]

### Findings

#### [SEVERITY] [Finding title]
- Location: [file:line, route, component, or config]
- Description: [what is vulnerable]
- Impact: [what an attacker or unauthorized actor could do]
- Exploitability: [required conditions and reachability]
- Recommendation: [specific mitigation]
- Verification: [how to verify the mitigation]

### Positive Observations
- [security practice that is already sound]

### Unverified / Needs Runtime Check
- [environment, config, dependency, or live behavior checks]

Hard rules:
- Stay read-only.
- Do not perform destructive testing, credential probing, scanning against external systems, or exploit attempts.
- Do not treat generic best-practice gaps as vulnerabilities unless they are reachable and material.
- Do not dilute concrete findings with broad security advice.
"""
```

- [ ] **Step 2: Create `test-engineer.toml`**

Use this complete TOML:

```toml
name = "test-engineer"
description = "Use when a task needs read-only test strategy, coverage-gap analysis, test-level selection, or Prove-It regression planning before test code is written."
model = "gpt-5.4-mini"
model_reasoning_effort = "medium"
sandbox_mode = "read-only"
developer_instructions = """
Own test strategy as behavior-risk analysis before test code is written.

Use this role when the parent task asks what tests are missing, whether current tests are enough, how to prove a bug fix, which test level to use, or how to scope targeted regression coverage.

Do not use this role for direct test implementation when the behavior boundary is already clear; use test-automator for that. Do not chase coverage numbers, rewrite test frameworks, or recommend tests that only lock implementation details.

Working mode:
1. Read the behavior under test before recommending coverage.
2. Identify public APIs, user-observable behavior, failure modes, and side-effect boundaries.
3. Inspect existing test style, fixtures, naming, and execution patterns.
4. Choose the lowest-cost test level that proves the behavior: unit, integration, or E2E.
5. For bugs, design a Prove-It regression test that should fail before the fix and pass after it.

Test strategy framework:
- current coverage by behavior, not by file count
- missing normal paths, failure paths, boundary values, permission cases, persistence effects, and integration edges
- test level choice: unit for pure logic, integration for DB/files/network/service boundaries, E2E for critical user journeys
- fixture, mock, and test data choices that keep tests deterministic
- risk priority: data loss, security, authorization, core business logic, recurring regressions, and costly operational failures
- handoff scope for test-automator when implementation is requested later

Quality checks:
- verify each recommended test maps to a concrete behavior or risk
- prefer one high-value regression test over broad low-signal coverage
- mock external systems and time/network boundaries; do not mock ordinary internal functions by default
- mark any conclusion that requires running tests, coverage tools, or the app
- avoid asserting private implementation details unless they are the only stable contract

Return:
## Test Coverage Analysis

### Scope Reviewed
- [files, modules, feature path, or flow]

### Current Coverage
- [behaviors already covered and evidence]

### Coverage Gaps
- [missing behavior, edge case, failure path, or integration edge]

### Recommended Tests
1. [test name]
   - Level: unit | integration | e2e
   - Verifies: [observable behavior]
   - Why it matters: [risk]
   - Expected current result: fail | pass | unknown
   - Priority: Critical | High | Medium | Low

### Test Implementation Notes
- [fixtures, mocks, data setup, boundaries, and command hints]

### Handoff To test-automator
- [smallest safe test-writing scope]

Hard rules:
- Stay read-only.
- Do not write or edit test files.
- Do not recommend tests only to increase a coverage percentage.
- Do not replace test-automator; produce the plan it can implement.
"""
```

- [ ] **Step 3: Create `web-performance-auditor.toml`**

Use this complete TOML:

```toml
name = "web-performance-auditor"
description = "Use when a task needs web performance review for frontend routes, Core Web Vitals, Lighthouse, LCP, INP, CLS, rendering, loading, network, caching, images, fonts, or framework-specific web performance risks."
model = "gpt-5.4-mini"
model_reasoning_effort = "medium"
sandbox_mode = "read-only"
developer_instructions = """
Own Web performance audit work as evidence-bound analysis of frontend loading, rendering, and network risk.

Use this role for Web apps, pages, routes, components, Core Web Vitals, Lighthouse, PageSpeed Insights, CrUX, DevTools traces, bundle size, loading, rendering, caching, images, fonts, JavaScript execution, and network behavior.

Do not use this role for non-Web performance work such as CLI parser speed, backend-only algorithm tuning, database-only optimization, or generic PR review. Do not recommend framework-specific fixes before identifying the stack.

Working mode:
1. Identify the Web framework, routing model, rendering model, and available performance artifacts.
2. Choose Quick mode when no Lighthouse, CrUX, PageSpeed, DevTools trace, or measured artifact is available.
3. Choose Deep mode when supplied artifacts or live measurements support metric-level analysis.
4. Keep field data, lab data, trace data, and source-level inference separate.
5. Prioritize fixes by likely user impact and verification cost.

Quick mode:
- perform source-level risk analysis only
- label every impact as potential impact
- use not measured for metrics without data
- recommend the next measurement that would confirm or reject the risk

Deep mode:
- analyze supplied Lighthouse, PageSpeed, CrUX, DevTools trace, browser capture, or equivalent artifacts
- cite the metric source for each measured claim
- do not present lab data as field data or source inference as measurement

Performance framework:
- Core Web Vitals: LCP, INP, CLS
- loading: TTFB, preload, preconnect, blocking scripts, images, fonts, bundle size, code splitting, hydration, and route-level data loading
- rendering and JavaScript: unnecessary re-renders, long tasks, layout thrashing, virtualization, hydration cost, and framework-specific anti-patterns
- network and caching: over-fetching, sequential requests, missing pagination, compression, cache headers, redirects, CDN usage, and third-party scripts
- framework fit: React, Next.js, Vue, Svelte, Angular, Astro, static HTML, or vanilla JavaScript

Quality checks:
- never fabricate metric values or Lighthouse scores
- write not measured when data is missing
- label source-only findings as potential impact
- ensure framework-specific recommendations match the detected stack
- include a verification method for each finding

Return:
## Web Performance Audit

### Scorecard

| Metric | Value | Source | Target | Status |
| --- | ---: | --- | ---: | --- |
| LCP | not measured | - | <= 2.5s | - |
| INP | not measured | - | <= 200ms | - |
| CLS | not measured | - | <= 0.1 | - |
| Lighthouse Performance | not measured | - | >= 90 | - |

Artifacts used: [none, Lighthouse path, trace path, PageSpeed result, CrUX result, or browser capture]
Framework detected: [framework or unknown]
Mode: Quick | Deep

### Summary
- Critical: [count]
- High: [count]
- Medium: [count]
- Low: [count]

### Findings

#### [SEVERITY] [Finding title]
- Area: Core Web Vitals | Loading | Rendering | Network
- Location: [file:line, route, component, or artifact section]
- Impact: potential impact | measured impact
- Recommendation: [specific fix]
- Verification: [measurement or check after fix]

### Positive Observations
- [performance practice that is already sound]

### Next Measurements
- [measurement needed next]

Hard rules:
- Stay read-only.
- Do not use Web performance findings for non-Web systems.
- Do not invent metrics, benchmarks, or traces.
- Do not recommend micro-optimizations without user-visible or measurable risk.
"""
```

- [ ] **Step 4: Validate TOML parsing**

Run:

```bash
/opt/anaconda3/bin/python3 -c 'from pathlib import Path; import tomllib; [tomllib.loads(p.read_text()) for p in Path("agents/categories/04-quality").glob("*.toml")]; print("toml ok")'
```

Expected:

```text
toml ok
```

---

### Task 2: Strengthen Existing Quality Roles

**Files:**
- Modify: `agents/categories/04-quality/reviewer.toml`
- Modify: `agents/categories/04-quality/test-automator.toml`

**Interfaces:**
- Consumes: new role boundaries from Task 1.
- Produces: a general `reviewer` that delegates deep specialist concerns conceptually, and a write-capable `test-automator` that can consume `test-engineer` output.

- [ ] **Step 1: Replace `reviewer.toml` with strengthened content**

Use this complete TOML:

```toml
name = "reviewer"
description = "Use when a task needs PR-style review focused on correctness, maintainability, contracts, behavior regressions, light security risk, operational risk, and missing tests."
model = "gpt-5.5"
model_reasoning_effort = "high"
sandbox_mode = "read-only"
developer_instructions = """
Own PR-style review work as evidence-driven quality and risk reduction, not checklist theater.

Prioritize actionable findings that reduce user-visible failure risk, preserve delivery speed, and keep the codebase understandable.

Use this role for general branch, PR, diff, or feature review. Do not use it as a substitute for deep security audit, test strategy, or Web performance audit when those are the task's central concern.

Working mode:
1. Map the changed or affected behavior boundary and likely failure surface.
2. Check the change against the task goal, existing contracts, and caller expectations.
3. Separate confirmed evidence from hypotheses before recommending action.
4. Prioritize by real user/system impact and likelihood.
5. Recommend the smallest mitigation that meaningfully reduces risk.

Review framework:
- correctness: task fit, edge cases, null/empty/error paths, off-by-one mistakes, data loss, races, state consistency, and rollback behavior
- readability and maintainability: naming, control flow, local style, duplication, unnecessary abstraction, and future debugging cost
- architecture and contracts: API shape, data structure changes, config behavior, persistence schema, migrations, compatibility, and downstream callers
- light security pass: input boundaries, auth checks, sensitive data, dependency risk, and obvious permission mistakes
- tests and verification: missing normal paths, failure paths, boundary paths, integration edges, and whether existing assertions protect behavior
- performance and operations: obvious regressions, logging, rollout, CI, deployment, monitoring, and migration risk

Specialist boundaries:
- For central auth, authorization, secrets, user input, webhook, dependency, or LLM/tool permission risk, recommend security-auditor rather than treating reviewer as a deep security audit.
- For coverage-gap analysis, test-level selection, or Prove-It regression planning, recommend test-engineer.
- For writing or updating tests, use test-automator.
- For Core Web Vitals, Lighthouse, LCP, INP, CLS, loading, rendering, or frontend network performance, recommend web-performance-auditor.

Quality checks:
- every finding must be specific, reproducible or source-backed, and mapped to file/line evidence when possible
- Critical findings must block merge or release because they involve exploitable security risk, data loss, or core functionality breakage
- Important findings should be fixed before merge because they create likely bugs, broken contracts, or missing critical tests
- Suggestions must be optional improvements, not disguised blockers
- low-confidence concerns must be labeled as hypotheses
- if no blocking issues are found, state residual risk and what was not verified

Return:
## Review Summary

**Verdict:** APPROVE | REQUEST CHANGES

**Scope reviewed:** [files, feature path, component, service, or diff area]

**Overview:** [1-2 sentences]

### Critical Issues
- [file:line] [issue] [recommended fix]

### Important Issues
- [file:line] [issue] [recommended fix]

### Suggestions
- [file:line] [optional improvement]

### What's Done Well
- [specific positive observation]

### Verification Story
- Tests reviewed: [yes/no + details]
- Build/runtime verified: [yes/no + command or limitation]
- Security checked: [light pass only / deeper security-auditor review recommended]
- Residual risk: [remaining uncertainty]

Do not dilute findings with style-only commentary unless explicitly requested by the parent agent.
"""
```

- [ ] **Step 2: Replace `test-automator.toml` with strengthened content**

Use this complete TOML:

```toml
name = "test-automator"
description = "Use when a task needs implementation of targeted automated tests, regression coverage, fixture updates, or small test harness improvements after behavior scope is clear."
model = "gpt-5.4-mini"
model_reasoning_effort = "medium"
sandbox_mode = "workspace-write"
developer_instructions = """
Own test automation engineering as minimal, behavior-focused regression protection.

Use this role when the parent task explicitly allows writing or updating tests and the target behavior is clear enough to implement safely. If the behavior boundary is unclear, ask for or rely on test-engineer coverage analysis first.

Do not use this role for broad test strategy, coverage-number chasing, large framework migrations, snapshot rewrites without behavior value, or speculative tests unrelated to a concrete risk.

Working mode:
1. Identify the behavior, bug, or risk the test must protect.
2. Inspect existing test style, fixtures, naming, and execution commands.
3. For bugs, use the Prove-It pattern: add or identify a test that fails before the fix and passes after it when feasible.
4. Implement the smallest deterministic test or fixture change that protects the behavior.
5. Run the narrowest relevant test command, then a broader command only when cheap and useful.

Implementation rules:
- If test-engineer provided a handoff, follow its smallest safe test-writing scope unless code evidence shows it is wrong.
- Prefer behavior assertions over implementation-detail assertions.
- Mock external systems, wall-clock time, network, filesystem, or randomness when needed for determinism.
- Do not mock ordinary internal functions unless that is already the project style or required to isolate an external boundary.
- Keep fixture changes local and avoid rewriting unrelated tests.
- Every new or changed test must map to one concrete behavior, bug, or risk.

Quality checks:
- verify the new test would fail for the broken behavior when feasible
- confirm tests are deterministic and not timing-dependent
- check that runtime cost is proportionate to the risk
- run the relevant test command and report exact result
- if tests cannot run, explain the blocker and provide the best available static verification

Return:
## Test Automation Result

### Scope Changed
- [files changed]

### Tests Added Or Updated
- [test name] -> [behavior protected]

### Verification
- Command: [command]
- Result: pass | fail | not run
- Notes: [failure details or environment limits]

### Residual Risk
- [what remains untested or uncertain]

Do not introduce broad framework migration in test suites unless explicitly requested by the parent agent.
"""
```

- [ ] **Step 3: Validate TOML parsing**

Run:

```bash
/opt/anaconda3/bin/python3 -c 'from pathlib import Path; import tomllib; [tomllib.loads(p.read_text()) for p in Path("agents/categories/04-quality").glob("*.toml")]; print("toml ok")'
```

Expected:

```text
toml ok
```

---

### Task 3: Update Core Selection Rules

**Files:**
- Modify: `SKILL.md`
- Modify: `references/role-lineups.md`
- Modify: `references/decision-rules.md`
- Modify: `references/suggestion-contract.md`

**Interfaces:**
- Consumes: role names and boundaries from Tasks 1 and 2.
- Produces: source-of-truth lineup rules used by docs and evals.

- [ ] **Step 1: Update `SKILL.md` strong triggers**

In `SKILL.md`, extend the "Strong triggers" list with these bullets:

```markdown
- security-sensitive code review involving auth, authorization, secrets, user input, webhooks, dependencies, or LLM/tool permissions
- test coverage analysis, test strategy, or regression test planning
- targeted test implementation that should start with read-only behavior mapping
- Web performance audit for frontend routes, Core Web Vitals, Lighthouse, LCP, INP, CLS, loading, rendering, or network behavior
- pre-ship quality gate across review, tests, security, and release risk
```

- [ ] **Step 2: Update `SKILL.md` hard stop cases**

In `SKILL.md`, extend "Hard stop cases" with these bullets:

```markdown
- generic PR review that does not need specialist security, test strategy, or Web performance lanes
- Web performance specialist work for non-Web performance tasks
- write-capable test automation when the target behavior is ambiguous
- vague security requests without a concrete artifact, flow, or trust boundary
```

- [ ] **Step 3: Replace `SKILL.md` bundled capability map**

Replace the existing bundled capability map with:

```markdown
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
```

- [ ] **Step 4: Replace `SKILL.md` selection guidance table**

Replace the selection guidance table with:

```markdown
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
```

- [ ] **Step 5: Add `SKILL.md` compression rules after role-count rules**

Add:

```markdown
Specialist compression rules:
- ordinary PR review stays `reviewer + code-mapper`
- add `security-auditor` only when the task has a concrete security boundary or explicit security audit request
- add `test-engineer` only when the task asks about tests, coverage, proof, or test strategy
- add `test-automator` only when test writing or updating is explicitly requested and the scope is clear enough to be safe
- add `web-performance-auditor` only for Web apps, Web routes, Web pages, Web components, or Web performance artifacts
- if more than 4 roles are triggered, keep the central risk specialist and `code-mapper`, then drop non-core roles
```

- [ ] **Step 6: Replace `references/role-lineups.md` capability map and lineup table**

Use these exact tables in `references/role-lineups.md`:

```markdown
| Capability | Preferred bundled role | Use when | Missing-role behavior |
| --- | --- | --- | --- |
| code mapping | `code-mapper` | tracing code paths, ownership, or execution flow | Drop the capability or handle mapping in the main thread after approval. |
| code review | `reviewer` | general PR review, correctness, maintainability, contracts, regressions, and light security/test risk | Handle in the main thread or use another explicit review role if one is available. |
| security audit | `security-auditor` | auth, authorization, secrets, user input, webhooks, SSRF, dependencies, LLM/tool permissions, or exploitable vulnerability risk | Mention that security audit is not delegated; do not substitute a generic reviewer when security is central. |
| docs/API verification | `docs-researcher` | verifying documented API/framework behavior | Mention that docs verification is not delegated; do not substitute an unknown role. |
| search | `search-specialist` | gathering high-signal codebase or external evidence | Drop if code mapping or docs verification already covers the task. |
| synthesis | `knowledge-synthesizer` | consolidating multiple research outputs | Synthesize in the main thread after other agents return. |
| planning | `task-distributor` | decomposing broad work into bounded subtasks | Plan in the main thread if no planning role is available. |
| test strategy | `test-engineer` | coverage gaps, test plan, test level choice, or Prove-It regression planning | Handle test strategy in the main thread; do not jump directly to write-capable test automation. |
| test automation | `test-automator` | writing or updating targeted tests after scope is clear | Do not suggest write-capable testing if unavailable. |
| Web performance audit | `web-performance-auditor` | Core Web Vitals, Lighthouse, frontend route/component performance, loading, rendering, network, caching, images, fonts, or bundle risks | Handle in the main thread or skip the specialist if the task is not Web-specific. |
```

```markdown
| Scenario | Capability lineup | Preferred roles when available | Work mode |
| --- | --- | --- | --- |
| General PR review | code review + code mapping | `reviewer` + `code-mapper` | read-only |
| Multi-axis PR review with docs/API assumptions | code review + code mapping + docs/API verification | `reviewer` + `code-mapper` + `docs-researcher` | read-only |
| Security-sensitive review | security audit + code mapping + code review | `security-auditor` + `code-mapper` + `reviewer` | read-only |
| Auth / permission / token flow review | security audit + code mapping | `security-auditor` + `code-mapper` | read-only |
| LLM / agent tool safety review | security audit + code mapping + docs/API verification | `security-auditor` + `code-mapper` + `docs-researcher` | read-only |
| Test coverage analysis | test strategy + code mapping | `test-engineer` + `code-mapper` | read-only |
| Add targeted regression tests | test strategy + test automation + code mapping | `test-engineer` + `test-automator` + `code-mapper` | mixed |
| Web performance source audit | Web performance audit + code mapping | `web-performance-auditor` + `code-mapper` | read-only |
| Web performance audit with artifacts | Web performance audit | `web-performance-auditor` | read-only |
| Read-heavy repo exploration | code mapping + search | `code-mapper` + `search-specialist` | read-only |
| Docs + codepath verification | docs/API verification + code mapping | `docs-researcher` + `code-mapper` | read-only |
| Research + synthesis | search + synthesis | `search-specialist` + `knowledge-synthesizer` | read-only |
| Planning a broad change | planning + code mapping | `task-distributor` + `code-mapper` | read-only |
| Coverage-focused follow-up | code review + test automation | `reviewer` + `test-automator` | write-capable |
| Pre-ship quality gate | code review + security audit + test strategy + code mapping | `reviewer` + `security-auditor` + `test-engineer` + `code-mapper` | read-only |
```

- [ ] **Step 7: Add specialist compression bullets to `references/role-lineups.md`**

Add under Compression Rules:

```markdown
- Ordinary PR review defaults to `reviewer + code-mapper`; do not add every quality specialist.
- Add `security-auditor` only for concrete security boundaries or explicit security audit requests.
- Add `test-engineer` only for test strategy, coverage gaps, proof, or regression planning.
- Add `test-automator` only when the user explicitly asks for test writes and the behavior scope is clear.
- Add `web-performance-auditor` only for Web-facing performance work.
- For non-Web performance, use `code-mapper + reviewer` only if the task is multi-lane.
- If more than 4 roles are triggered, keep the central specialist and `code-mapper`; drop non-core roles.
```

- [ ] **Step 8: Update `references/decision-rules.md`**

Add these rows to the positive/trigger section:

```markdown
| Security-sensitive review | mentions auth, authorization, session, token, secrets, user input, webhook, SSRF, prompt injection, tool permission, or multi-tenant data | Yes | security audit + code mapping, optionally code review | Use `security-auditor`; do not rely only on generic `reviewer` when security is central. |
| Test strategy / coverage analysis | asks what tests are missing, whether tests are enough, or how to prove a bug fix | Yes | test strategy + code mapping | Use read-only `test-engineer`; do not jump to `test-automator`. |
| Targeted test implementation | asks to add or update tests for a known bug or risk | Yes | test strategy + test automation, optionally code mapping | Use `mixed` unless scope is already clear and bounded. |
| Web performance audit | mentions Lighthouse, Core Web Vitals, LCP, INP, CLS, frontend route, rendering, loading, bundle, caching, images, fonts, or network behavior | Yes | Web performance audit + code mapping | Use only for Web projects or Web-facing components. |
| Pre-ship quality gate | asks for release readiness across code quality, tests, security, and risk | Yes | code review + security audit + test strategy, optionally code mapping | Keep read-only unless the user explicitly asks to fix. |
| LLM / agent safety review | mentions prompt injection, tool permissions, agent delegation, secrets in context, cross-tenant context, or destructive tools | Yes | security audit + code mapping + docs/API verification | Treat as security-sensitive. |
```

Add these rows to the non-trigger/limitation section:

```markdown
| Generic small PR review | only asks for one narrow bug, one small file, or style-only review | No or `reviewer` only if explicit | Avoid over-triggering multiple roles. |
| Non-Web performance task | CLI, backend algorithm, database performance, compiler/runtime issue without Web UI | Maybe, but not `web-performance-auditor` | Use `code-mapper + reviewer` only if task is multi-lane. |
| Test code writing without clear behavior | asks to add tests but target behavior is ambiguous | No | Clarify first; after the behavior boundary is known, use `test-engineer` before `test-automator`. |
| Security buzzword only | user says "make it secure" with no artifact, flow, or trust boundary | No | Clarify first. |
```

Add these tie-breakers:

```markdown
| Specialist role would not add an independent viewpoint | Do not add it | Specialist names should reduce ambiguity, not decorate the lineup. |
| Security boundary is central | Prefer `security-auditor` over generic `reviewer` | Deep security review needs a focused threat model. |
| Test strategy is central | Prefer `test-engineer` over generic `reviewer` | Coverage planning is different from PR review. |
| Web performance is central | Prefer `web-performance-auditor` over generic `reviewer` | Web metrics require measured-vs-potential discipline. |
```

- [ ] **Step 9: Update `references/suggestion-contract.md` hard rules**

Add this bullet under Hard Rules:

```markdown
- Add specialist roles only when the prompt has an explicit signal for that specialty; ordinary PR review should not inflate into every quality role.
```

- [ ] **Step 10: Check role names in rule files**

Run:

```bash
rg -n "security-auditor|test-engineer|web-performance-auditor|worker|explorer" SKILL.md references
```

Expected:

```text
security-auditor appears in SKILL.md and references
test-engineer appears in SKILL.md and references
web-performance-auditor appears in SKILL.md and references
worker does not appear as a recommended bundled role
explorer does not appear as a recommended bundled role
```

---

### Task 4: Sync Documentation, Examples, And Evals

**Files:**
- Modify: `README.md`
- Modify: `README.zh.md`
- Modify: `references/examples-positive.md`
- Modify: `references/examples-negative.md`
- Modify: `evals/prompts.yaml`
- Modify: `evals/rubric.md`
- Modify: `evals/scenarios.md`
- Modify: `evals/results-template.md`
- Modify: `CHANGELOG.md`

**Interfaces:**
- Consumes: source rules from Task 3.
- Produces: public docs and manual eval assets that match the new 10-role bundle.

- [ ] **Step 1: Update `README.md` role count and role table**

Change "Seven specialized roles" to "Ten specialized roles".

Replace the bundled role table with:

```markdown
| Role | What it does |
|---|---|
| `code-mapper` | Traces execution paths and maps file ownership across the codebase |
| `reviewer` | Performs Staff Engineer-style code review across correctness, contracts, regressions, and maintainability |
| `security-auditor` | Reviews trust boundaries, auth, authorization, secrets, user input, dependencies, and LLM/tool permission risks |
| `test-engineer` | Analyzes test strategy, coverage gaps, test levels, and Prove-It regression plans without editing files |
| `test-automator` | Adds targeted automated regression coverage after scope is clear |
| `docs-researcher` | Verifies API guarantees and documentation assumptions |
| `search-specialist` | Gathers high-signal evidence quickly across code or external sources |
| `knowledge-synthesizer` | Consolidates research findings into a concise, actionable summary |
| `task-distributor` | Structures a broad goal into bounded, independent subtasks |
| `web-performance-auditor` | Audits Web performance, Core Web Vitals, loading, rendering, and network risks without fabricating metrics |
```

- [ ] **Step 2: Update `README.md` common lineups**

Replace the common lineups table with:

```markdown
| Task shape | Recommended lineup | Work mode |
|---|---|---|
| General PR review | `reviewer + code-mapper` | `read-only` |
| Security-sensitive review | `security-auditor + code-mapper + reviewer` | `read-only` |
| Test coverage analysis | `test-engineer + code-mapper` | `read-only` |
| Targeted regression tests | `test-engineer + test-automator + code-mapper` | `mixed` |
| Web performance audit | `web-performance-auditor + code-mapper` | `read-only` |
| Pre-ship quality gate | `reviewer + security-auditor + test-engineer + code-mapper` | `read-only` |
| Codepath plus docs/API verification | `code-mapper + docs-researcher` | `read-only` |
| Option research and tradeoff synthesis | `search-specialist + knowledge-synthesizer` | `read-only` |
```

- [ ] **Step 3: Update `README.md` acknowledgments**

Add this paragraph after the VoltAgent acknowledgment:

```markdown
The role design for Staff Engineer review, security auditing, test strategy, and Web performance auditing was informed by [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills). The cast-subagents versions are rewritten for Codex subagent TOML roles and this project's advisory lineup-selection model.
```

- [ ] **Step 4: Update `README.zh.md` role count and role table**

Change "七个专业角色" to "十个专业角色".

Replace the bundled role table with:

```markdown
| 角色 | 功能 |
|---|---|
| `code-mapper` | 追踪代码执行路径，定位文件归属关系 |
| `reviewer` | 以 Staff Engineer 风格审查正确性、契约、回归和可维护性风险 |
| `security-auditor` | 审查信任边界、认证、授权、密钥、用户输入、依赖和 LLM/tool 权限风险 |
| `test-engineer` | 只读分析测试策略、覆盖缺口、测试层级和 Prove-It 回归测试计划 |
| `test-automator` | 在范围清楚后添加有针对性的自动化回归测试 |
| `docs-researcher` | 验证 API 保证和文档假设 |
| `search-specialist` | 在代码或外部资源中快速收集高信号证据 |
| `knowledge-synthesizer` | 将研究结果整合为简洁、可操作的总结 |
| `task-distributor` | 将宏观目标拆分为有边界、独立的子任务 |
| `web-performance-auditor` | 审计 Web 性能、Core Web Vitals、加载、渲染和网络风险，不伪造指标 |
```

- [ ] **Step 5: Update `README.zh.md` common lineups**

Replace the common lineups table with:

```markdown
| 任务形态 | 推荐阵容 | 工作模式 |
|---|---|---|
| 通用 PR 审查 | `reviewer + code-mapper` | `read-only` |
| 安全敏感审查 | `security-auditor + code-mapper + reviewer` | `read-only` |
| 测试覆盖分析 | `test-engineer + code-mapper` | `read-only` |
| 有针对性的回归测试 | `test-engineer + test-automator + code-mapper` | `mixed` |
| Web 性能审计 | `web-performance-auditor + code-mapper` | `read-only` |
| 发布前质量门 | `reviewer + security-auditor + test-engineer + code-mapper` | `read-only` |
| 代码路径加文档/API 验证 | `code-mapper + docs-researcher` | `read-only` |
| 方案研究与权衡综合 | `search-specialist + knowledge-synthesizer` | `read-only` |
```

- [ ] **Step 6: Update `README.zh.md` acknowledgments**

Add this paragraph after the VoltAgent acknowledgment:

```markdown
Staff Engineer 风格审查、安全审计、测试策略和 Web 性能审计的角色设计参考了 [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills)。cast-subagents 中的版本已按 Codex subagent TOML 角色格式和本项目的 advisory lineup-selection 模型重新表达。
```

- [ ] **Step 7: Add positive examples**

Append these examples to `references/examples-positive.md`:

```markdown
9. `Review this auth refactor for permission bypasses, token handling issues, and missing server-side checks.`
10. `Check whether this agent tool integration can leak secrets or let a subagent perform destructive actions without approval.`
11. `Look at the checkout flow and tell me what tests are missing before we change anything.`
12. `Add regression tests for the settings save bug, but first identify the exact behavior boundary.`
13. `Audit the Next.js landing page for LCP, INP, CLS, image loading, and unnecessary client-side rendering.`
14. `Before we ship this branch, check code quality, security risk, and missing tests.`
```

Add this paragraph to the explanation section:

```markdown
- they contain explicit security, test strategy, Web performance, or pre-ship quality signals that justify specialist roles without making ordinary PR review noisy
```

- [ ] **Step 8: Add negative examples**

Append these examples to `references/examples-negative.md`:

```markdown
11. `Optimize this CLI parser. It feels slow on large files.`
12. `Review this small README typo fix.`
13. `Add some tests here, not sure what exactly.`
14. `Make this secure.`
```

Add this paragraph to the explanation section:

```markdown
- Web performance specialists should not be used for non-Web performance tasks, write-capable testing should not start from unclear behavior, and vague security wording should be clarified before suggesting a security lineup
```

- [ ] **Step 9: Update `evals/prompts.yaml` existing expectations**

Make these exact changes:

```yaml
  - id: pos-01
    expected_roles: [reviewer, code-mapper]
    notes: "Canonical general PR review case; should not inflate to every specialist role."
```

```yaml
  - id: edge-01
    expected_roles: [code-mapper, reviewer]
    notes: "Mixed read/write task should start with read-only mapping and review; no generic worker role."
```

```yaml
  - id: edge-02
    expected_roles: [code-mapper]
    notes: "Preferred role unavailable; do not invent a missing fallback role."
```

```yaml
  - id: edge-04
    expected_roles: [code-mapper, reviewer]
    notes: "Approval path should keep any implementation work bounded and avoid generic worker roles."
```

```yaml
  - id: edge-05
    expected_roles: [reviewer, code-mapper, docs-researcher]
    notes: "Role count pressure; compact review should not add every specialist without explicit core risk."
```

- [ ] **Step 10: Add new eval prompts**

Append these prompt blocks to `evals/prompts.yaml` after `edge-06`:

```yaml
  - id: pos-07
    surface: shared
    smoke: true
    category: positive
    prompt: "Review this auth refactor for permission bypasses, token handling issues, and missing server-side checks."
    expected_should_suggest: true
    expected_roles: [security-auditor, code-mapper, reviewer]
    must_not_do:
      - rely only on generic reviewer for central security risk
      - recommend more than 4 roles
      - omit a direct permission question
    notes: "Security-sensitive review."

  - id: pos-08
    surface: shared
    smoke: false
    category: positive
    prompt: "Check whether this agent tool integration can leak secrets or let a subagent perform destructive actions without approval."
    expected_should_suggest: true
    expected_roles: [security-auditor, code-mapper, docs-researcher]
    must_not_do:
      - ignore LLM/tool permission safety
      - start auditing before approval
    notes: "LLM and agent tool safety review."

  - id: pos-09
    surface: cli
    smoke: true
    category: positive
    prompt: "Look at the checkout flow and tell me what tests are missing before we change anything."
    expected_should_suggest: true
    expected_roles: [test-engineer, code-mapper]
    must_not_do:
      - suggest write-capable test automation first
      - skip behavior mapping
    notes: "Read-only test coverage analysis."

  - id: pos-10
    surface: cli
    smoke: false
    category: positive
    prompt: "Add regression tests for the settings save bug, but first identify the exact behavior boundary."
    expected_should_suggest: true
    expected_roles: [test-engineer, test-automator, code-mapper]
    must_not_do:
      - start writing tests before read-only scoping
      - label the work read-only
    notes: "Mixed targeted regression test implementation."

  - id: pos-11
    surface: shared
    smoke: true
    category: positive
    prompt: "Audit the Next.js landing page for LCP, INP, CLS, image loading, and unnecessary client-side rendering."
    expected_should_suggest: true
    expected_roles: [web-performance-auditor, code-mapper]
    must_not_do:
      - fabricate performance metrics
      - recommend non-Web performance roles only
    notes: "Web performance audit."

  - id: pos-12
    surface: shared
    smoke: false
    category: positive
    prompt: "Before we ship this branch, check code quality, security risk, and missing tests."
    expected_should_suggest: true
    expected_roles: [reviewer, security-auditor, test-engineer, code-mapper]
    must_not_do:
      - exceed 4 roles
      - suggest write-capable fixes before approval
    notes: "Pre-ship quality gate."

  - id: neg-08
    surface: cli
    smoke: true
    category: negative
    prompt: "Optimize this CLI parser. It feels slow on large files."
    expected_should_suggest: false
    expected_roles: []
    must_not_do:
      - recommend web-performance-auditor
      - treat non-Web performance as Core Web Vitals work
    notes: "Non-Web performance must not trigger Web performance specialist."

  - id: neg-09
    surface: shared
    smoke: false
    category: negative
    prompt: "Review this small README typo fix."
    expected_should_suggest: false
    expected_roles: []
    must_not_do:
      - inflate generic review into specialist roles
      - add delegation overhead
    notes: "Generic small review should stay silent."

  - id: neg-10
    surface: cli
    smoke: false
    category: negative
    prompt: "Add some tests here, not sure what exactly."
    expected_should_suggest: false
    expected_roles: []
    must_not_do:
      - suggest write-capable test-automator immediately
      - pretend the behavior boundary is clear
    notes: "Unclear test writing request should clarify first."

  - id: neg-11
    surface: shared
    smoke: false
    category: negative
    prompt: "Make this secure."
    expected_should_suggest: false
    expected_roles: []
    must_not_do:
      - invent a concrete security scope
      - suggest a security lineup before clarifying
    notes: "Security buzzword only."
```

- [ ] **Step 11: Update eval result tables**

In `evals/results-template.md`, add rows for `pos-07` through `pos-12` and `neg-08` through `neg-11` to the Prompt-by-Prompt Results table.

Use this exact block:

```markdown
| pos-07 | smoke |  |  |  |  |  |
| pos-08 | extended |  |  |  |  |  |
| pos-09 | smoke |  |  |  |  |  |
| pos-10 | extended |  |  |  |  |  |
| pos-11 | smoke |  |  |  |  |  |
| pos-12 | extended |  |  |  |  |  |
| neg-08 | smoke |  |  |  |  |  |
| neg-09 | extended |  |  |  |  |  |
| neg-10 | extended |  |  |  |  |  |
| neg-11 | extended |  |  |  |  |  |
```

- [ ] **Step 12: Update eval rubric**

In `evals/rubric.md`, add these bullets under "Notes For Manual Review":

```markdown
- missing specialist roles when the prompt has explicit security, test strategy, or Web performance signals
- unrelated specialist roles added to ordinary PR review
- `web-performance-auditor` suggested for non-Web performance work
- `test-automator` suggested before behavior scope is clear
- security buzzword prompts treated as concrete security audit scope without clarification
```

- [ ] **Step 13: Update eval scenarios**

In `evals/scenarios.md`, change "Run the full 18-prompt suite only after smoke passes." to:

```markdown
Run the full prompt suite only after smoke passes.
```

Update the recommended Desktop prompt subset to include:

```markdown
- `pos-01`
- `pos-07`
- `pos-09`
- `pos-11`
- `neg-03`
- `neg-08`
- `edge-06`
```

- [ ] **Step 14: Update changelog**

Add this section above `## 0.1.0` in `CHANGELOG.md`:

```markdown
## Unreleased

- Add security, test strategy, and Web performance bundled agent roles.
- Strengthen reviewer and test-automator role definitions.
- Update lineup rules, examples, docs, and eval prompts for specialist roles.
```

- [ ] **Step 15: Check documentation consistency**

Run:

```bash
rg -n "Seven specialized roles|七个专业角色|worker|explorer|security-auditor|test-engineer|web-performance-auditor" README.md README.zh.md references evals CHANGELOG.md
```

Expected:

```text
No matches for Seven specialized roles
No matches for 七个专业角色
No recommended bundled lineup uses worker
No recommended bundled lineup uses explorer
New specialist role names appear in README, README.zh, references, evals, and CHANGELOG
```

---

### Task 5: Final Verification

**Files:**
- Verify: entire repository working tree

**Interfaces:**
- Consumes: Tasks 1-4.
- Produces: final checked working tree ready for user review.

- [ ] **Step 1: Check all quality-role TOML files parse**

Run:

```bash
/opt/anaconda3/bin/python3 -c 'from pathlib import Path; import tomllib; [tomllib.loads(p.read_text()) for p in Path("agents/categories").glob("*/*.toml")]; print("all toml ok")'
```

Expected:

```text
all toml ok
```

- [ ] **Step 2: Compile scripts**

Run:

```bash
/opt/anaconda3/bin/python3 -m compileall -q scripts
```

Expected: command exits `0` with no output.

- [ ] **Step 3: Check diff whitespace**

Run:

```bash
git diff --check
```

Expected: command exits `0` with no output.

- [ ] **Step 4: Check role count by TOML files**

Run:

```bash
find agents/categories -name '*.toml' | sort
```

Expected output includes exactly these 10 bundled roles:

```text
agents/categories/01-core/code-mapper.toml
agents/categories/02-research/docs-researcher.toml
agents/categories/02-research/knowledge-synthesizer.toml
agents/categories/02-research/search-specialist.toml
agents/categories/03-planning/task-distributor.toml
agents/categories/04-quality/reviewer.toml
agents/categories/04-quality/security-auditor.toml
agents/categories/04-quality/test-automator.toml
agents/categories/04-quality/test-engineer.toml
agents/categories/04-quality/web-performance-auditor.toml
```

- [ ] **Step 5: Check no ignored docs accidentally staged**

Run:

```bash
git status --short --ignored=matching docs .gitignore
```

Expected:

```text
 M .gitignore
!! docs/
```

If implementation changed tracked files beyond `.gitignore`, they also appear in the normal `git status --short`; `docs/` remains ignored.

- [ ] **Step 6: Review final diff for scope**

Run:

```bash
git diff --stat
```

Expected:

```text
Only role TOMLs, SKILL.md, references, README files, evals, CHANGELOG.md, and .gitignore changed.
No changes to scripts/install-agent-roles.py.
No changes to agents/openai.yaml.
No changes to advisory gate behavior.
```

- [ ] **Step 7: Final manual behavior checklist**

Verify these statements against the edited files:

```text
General PR review recommends reviewer + code-mapper.
Security-sensitive review can recommend security-auditor + code-mapper + reviewer.
Auth/token review can recommend security-auditor + code-mapper.
LLM/tool safety review can recommend security-auditor + code-mapper + docs-researcher.
Test coverage analysis can recommend test-engineer + code-mapper.
Targeted regression tests can recommend test-engineer + test-automator + code-mapper in mixed mode.
Web performance audit can recommend web-performance-auditor + code-mapper.
Web performance with supplied metrics can recommend web-performance-auditor alone.
Pre-ship quality gate can recommend reviewer + security-auditor + test-engineer + code-mapper.
No common lineup exceeds 4 roles.
No role file says security-auditor, test-engineer, or web-performance-auditor can write files.
test-automator remains workspace-write.
```

- [ ] **Step 8: Report results**

Final implementation report must include:

```markdown
- Added roles: security-auditor, test-engineer, web-performance-auditor
- Strengthened roles: reviewer, test-automator
- Updated rules/docs/evals: SKILL.md, references, README.md, README.zh.md, evals, CHANGELOG.md
- Checks run: [commands and pass/fail]
- Not changed: scripts/install-agent-roles.py, agents/openai.yaml, advisory gate behavior
- Commit status: not committed unless user explicitly requested a commit
```
