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

## Prompt-by-Prompt Results

| ID | Suite | Policy | Score / 6 | Delegated? | Roles used | Policy-appropriate ending? | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |  |  |

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
