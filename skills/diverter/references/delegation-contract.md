# Delegation Contract

The literal eligible-receipt templates are owned only by `../SKILL.md`. This reference defines their semantics and failure cases; do not copy or rephrase the templates here. Load the skill silently: its policy-specific routing receipt is the first user-visible output, with no eligibility or loading preface. If routing returns `ROOT_ONLY`, continue in Root without any routing message.

## Root-only Silence

Every non-delegation path is silent, including ordinary task shape, bypass, explicit opt-out, missing roles, and native unavailability. Continue the user's task normally without mentioning Diverter or internal routing checks.

## Shared Information

Each selected child gets one `Child:` line in lineup order with its exact role name and a concise, user-facing summary of its task. For implicit eligibility, the `Root:` line summarizes Root's judgment, proportional verification, integration, or other retained responsibility. For explicit eligibility, it may summarize coordination and integration. Never invent a separate Root deliverable. The receipt also states exactly one Work Mode: `read-only`, `mixed`, or `write-capable`.

Task summaries say who will do what. They do not expose handoff steps, file scope, success criteria, verification, deliverables, or routing rationale. Never list alternatives, invent roles, describe results that do not exist, or imply a child started before the receipt.

## `ask` Ending

Use the `ask` template in `../SKILL.md`, end with a direct permission question in the user's language, then stop before task work and spawning.

Refusal means zero spawn and ordinary Root continuation without a `ROOT_ONLY` receipt.

## `auto` Ending

Use the `auto` template in `../SKILL.md`, end with an immediate-start statement in the user's language, then spawn in the same turn without asking a question.

## Explicit Delegation Requests

An Explicit Delegation Request does not need independently established material benefit. Do not invent a separate Root deliverable; state the requested child assignment and Root's coordination and integration responsibility instead.

## Focused Skills

Name the explicitly selected skill's retained core responsibility and describe the delegated role as a Supporting Child. A Required Skill Route must appear in the lineup exactly once; do not imply that Diverter replaces the skill or let the focused skill create a second spawn.

## Failure Cases

Avoid:

- no bounded Child Contribution or Root integration responsibility;
- unnecessary Root work that duplicates the Child Contribution;
- more roles than independent Child Contributions;
- an `ask` message without a permission question;
- an `auto` message that asks a question or pauses;
- redispatching an equivalent scope instead of Child Reuse;
- mentioning pre-activation native absence; or
- exposing internal loading, cache, alias, or retry details.
