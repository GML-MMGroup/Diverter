# Evaluation Results Template

## Run Metadata

- Date:
- Plugin revision:
- Evaluator:
- Surface:
- Suite: `smoke` / `extended` / `desktop`
- Arm: `baseline` / `plugin`
- Installation mode: `plugin`
- Delegation policy: `ask` / `auto`
- Evidence class: `required gate` / `diagnostic`
- Raw output directory:

## Discovery

| Check | Result | Pass? |
| --- | --- | --- |
| `diverter` visible |  |  |
| No skill load errors |  |  |

## Summary

| Metric | Result | Pass? |
| --- | --- | --- |
| Positive/edge suggestion rate |  |  |
| Negative-case false positive rate |  |  |
| Delegation-policy violations |  |  |
| Sanitized failure-reporting violations |  |  |
| `>4` role violations |  |  |
| Fallback correctness rate |  |  |
| Root Lane quality rate |  |  |

## Prompt-by-Prompt Results

| ID | Suite | Policy | Router Score / 7 | Delegated? | Roles used | Root Lane valid? | Policy-appropriate ending? | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |  |  |  |

## Native Lifecycle Evidence

| Run | Model | Family | Native spawn | Root progress before child completion | Same-child reuse | Leaf child | Write Ownership | Integration verification | Pass? |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |  |  |  |  |

Record persisted rollout paths and the sanitized JSON report from `scripts/verify-native-lifecycle.py`. Final-response wording is not lifecycle evidence.

Label additional Root-model smokes and Native Absence Bypass probes as `diagnostic`; they do not determine the release decision.

Add one row for every evaluated entry in `prompts.yaml`, including the focused `auto-*` cases.

## Failure Patterns

-
-
-

## Subagent Evaluator Notes

- Runner:
- Reviewer:
- Synthesizer:

## Recommended Revisions

- Files to revise:
- Why:
- Expected effect:

## Go / No-Go

- Decision:
- Reason:
