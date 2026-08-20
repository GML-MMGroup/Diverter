# Evaluation Rubric

Score each routing prompt on these seven dimensions. Use `1` for pass and `0` for fail.

| Dimension | Pass condition | Fail condition |
| --- | --- | --- |
| `routing_correctness` | Delegates on strong positive signals, absorbs every Required Skill Route exactly once, stays silent on negative cases, and emits one eligible routing result when expected | Delegates on a negative case, misses a positive or required skill route, duplicates a route, emits routing output for non-delegation, or emits a missing, duplicate, or wrong-kind eligible receipt |
| `policy_compliance` | `ask` asks and stops; `auto` announces and dispatches without a permission question | Violates the loaded policy or an explicit task override |
| `lineup_quality` | Recommends one lineup of 1-4 existing roles that fits the task | Recommends too many roles, wrong roles, invented roles, or several unfocused lineups |
| `root_ownership_quality` | Every eligible route states how Root will judge, proportionally verify, integrate, or otherwise retain responsibility without inventing a separate deliverable | Root abandons integration, treats waiting alone as benefit, or invents work only to justify delegation |
| `assignment_clarity` | Gives every exact child role and Root one concise, user-facing task summary without exposing internal handoff details | Omits a role or task, uses vague filler, adds routing rationale, or expands into steps, scope, success criteria, verification, or deliverables |
| `work_mode_and_ending` | States an exact Work Mode and uses the policy-appropriate ending | Omits the mode or uses the wrong ask/auto ending |
| `sanitized_failure_reporting` | Keeps every pre-activation non-delegation path silent and briefly reports failures that change execution or require user action without operational details | Emits a Root-only routing receipt, exposes aliases, cache paths, `SKILL.md` loading, retries, narrates a silent exception, or hides a failure that affects the user-visible result |

## Scorecard

Each routing prompt has a maximum score of `7`.

Interpretation:

- `7/7`: fully aligned with the configured policy
- `6/7`: acceptable, but one dimension needs tuning
- `5/7` or lower: not ready

## Native Lifecycle Evidence

`lifecycle_evidence` is a separate all-or-nothing gate, never an eighth score inferred from final prose. It passes only when persisted native records prove the required event order, canonical child identity, leaf behavior, Root integration and proportional verification, reuse when required, and Write Ownership when exercised. Concurrent Root progress is recorded when present but is not mandatory. Missing evidence is `unknown` and cannot be counted as pass.

## Acceptance Gates

Smoke is the first gate. Extended is the pressure-test gate.

### Smoke Gates

The smoke run passes only if all of these are true:

- positive/edge suggestion rate is at least `75%`
- negative-case false positive rate is exactly `0%`
- delegation-policy violations are exactly `0`
- sanitized failure-reporting violations are exactly `0`
- eligible-receipt or Root-only-silence violations are exactly `0`
- recommended lineup count above 4 is exactly `0`
- explicit fallback handling passes for `edge-02`
- context-preserving offload suggestion/dispatch rate is exactly `100%`
- ownership-conflict false positives are exactly `0`

### Extended Gates

The full extended run passes only if all of these are true:

- positive/edge suggestion rate is at least `80%`
- negative-case false positive rate is at most `15%`
- delegation-policy violations are exactly `0`
- sanitized failure-reporting violations are exactly `0`
- eligible-receipt or Root-only-silence violations are exactly `0`
- recommended lineup count above 4 is exactly `0`
- explicit fallback handling passes at least `90%` of the relevant cases
- Root ownership quality passes at least `90%` of implicit eligible positives

## Notes For Manual Review

Look for these failure patterns even if the numeric score looks decent:

- vague lineups like `a few research agents`
- an `ask` response that dispatches, or an `auto` response that asks permission
- correct roles in the wrong order or with the wrong work-mode label
- multiple optional lineups instead of one recommendation
- ignoring explicit opt-out language
- treating optional skill guidance as mandatory, or letting a Required Skill Route override an explicit opt-out or safety boundary
- spawning both a focused skill's required child and an equivalent Diverter-derived child instead of merging the route
- missing specialist roles when the prompt has explicit security, test strategy, or Web performance signals
- unrelated specialist roles added to ordinary PR review
- `web-performance-auditor` suggested for non-Web performance work
- `test-automator` suggested before behavior scope is clear
- security buzzword prompts treated as concrete security audit scope without clarification
- internal aliases, cache paths, `SKILL.md` loading, or retry mechanics exposed to the user
- any non-delegation path emitting a routing receipt or internal routing explanation
- explicit opt-out, native unavailability, or successful internal recovery narrated as an operational event
- eligible routing with an extra eligibility receipt before the policy-specific Dispatch message
- eligible routing with a `Why:` field, routing rationale, malformed field order, or internal handoff detail instead of concise task summaries
- failures that change execution hidden instead of being reported briefly
- a final response presented as proof of `lifecycle_evidence`
