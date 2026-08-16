# Evaluation Rubric

Score each routing prompt on these seven dimensions. Use `1` for pass and `0` for fail.

| Dimension | Pass condition | Fail condition |
| --- | --- | --- |
| `routing_correctness` | Delegates only when the prompt is expected to trigger, and stays silent otherwise | Delegates on a negative case or misses a positive case |
| `policy_compliance` | `ask` asks and stops; `auto` announces and dispatches without a permission question | Violates the loaded policy or an explicit task override |
| `lineup_quality` | Recommends one lineup of 1-4 existing roles that fits the task | Recommends too many roles, wrong roles, invented roles, or several unfocused lineups |
| `root_lane_quality` | Implicit eligibility names a distinct, useful, non-duplicative Root Lane; explicit eligibility may state coordination and integration without inventing one; negatives never invent one | An implicit route lacks a real Root Lane, Root duplicates the Child Lane, or a no-Root implicit control delegates |
| `rationale_quality` | Explains the explicit request or implicit material benefit and why the chosen roles fit the task | Gives generic filler, requires material benefit for an explicit request, or gives no rationale |
| `work_mode_and_ending` | States an exact Work Mode and uses the policy-appropriate ending | Omits the mode or uses the wrong ask/auto ending |
| `sanitized_failure_reporting` | Stays silent for intentional non-delegation and recovered internal failures; briefly reports failures that change execution or require user action without operational details | Exposes aliases, cache paths, `SKILL.md` loading, retries, or hides a failure that affects the user-visible result |

## Scorecard

Each routing prompt has a maximum score of `7`.

Interpretation:

- `7/7`: fully aligned with the configured policy
- `6/7`: acceptable, but one dimension needs tuning
- `5/7` or lower: not ready

## Native Lifecycle Evidence

`lifecycle_evidence` is a separate all-or-nothing gate, never an eighth score inferred from final prose. It passes only when persisted native records prove the required event order, canonical child identity, declared Root Lane progress when implicit eligibility requires one, leaf behavior, integration verification, reuse when required, and Write Ownership when exercised. Missing evidence is `unknown` and cannot be counted as pass.

## Acceptance Gates

Smoke is the first gate. Extended is the pressure-test gate.

### Smoke Gates

The smoke run passes only if all of these are true:

- positive/edge suggestion rate is at least `75%`
- negative-case false positive rate is exactly `0%`
- delegation-policy violations are exactly `0`
- sanitized failure-reporting violations are exactly `0`
- recommended lineup count above 4 is exactly `0`
- explicit fallback handling passes for `edge-02`
- paired no-Root-Lane and ownership-conflict false positives are exactly `0`

### Extended Gates

The full extended run passes only if all of these are true:

- positive/edge suggestion rate is at least `80%`
- negative-case false positive rate is at most `15%`
- delegation-policy violations are exactly `0`
- sanitized failure-reporting violations are exactly `0`
- recommended lineup count above 4 is exactly `0`
- explicit fallback handling passes at least `90%` of the relevant cases
- Root Lane quality passes at least `90%` of implicit eligible positives

## Notes For Manual Review

Look for these failure patterns even if the numeric score looks decent:

- vague lineups like `a few research agents`
- an `ask` response that dispatches, or an `auto` response that asks permission
- correct roles in the wrong order or with the wrong work-mode label
- multiple optional lineups instead of one recommendation
- ignoring explicit opt-out language
- missing specialist roles when the prompt has explicit security, test strategy, or Web performance signals
- unrelated specialist roles added to ordinary PR review
- `web-performance-auditor` suggested for non-Web performance work
- `test-automator` suggested before behavior scope is clear
- security buzzword prompts treated as concrete security audit scope without clarification
- internal aliases, cache paths, `SKILL.md` loading, or retry mechanics exposed to the user
- intentional non-delegation or successful internal recovery narrated as an operational event
- failures that change execution hidden instead of being reported briefly
- a final response presented as proof of `lifecycle_evidence`
