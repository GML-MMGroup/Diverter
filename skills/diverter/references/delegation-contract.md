# Delegation Contract

The literal eligible-receipt templates are owned only by `../SKILL.md`. This reference defines their semantics and failure cases; do not copy or rephrase the templates here. Load the skill silently: its policy-specific routing receipt is the first user-visible output, with no eligibility or loading preface.

## Root-only Receipt

Ordinary task-shape non-delegation uses exactly one line and nothing else about routing:

> `Routing: ROOT_ONLY — <one task-shape reason>`

Match the user's language in the reason. Do not emit this receipt for bypass, explicit opt-out, or native unavailability, and do not mention Diverter or internal checks.

## Shared Information

Each selected child gets one `Child:` line in lineup order with its exact role name and a concise, user-facing summary of its task. The `Root:` line summarizes the distinct Root Lane for implicit eligibility; for explicit eligibility without one, it summarizes coordination and integration instead of inventing work. The receipt also states exactly one Work Mode: `read-only`, `mixed`, or `write-capable`.

Task summaries say who will do what. They do not expose handoff steps, file scope, success criteria, verification, deliverables, or routing rationale. Never list alternatives, invent roles, describe results that do not exist, or imply a child started before the receipt.

## `ask` Ending

Use the `ask` template in `../SKILL.md`, end with a direct permission question in the user's language, then stop before task work and spawning.

Refusal means zero spawn and ordinary Root continuation without a `ROOT_ONLY` receipt.

## `auto` Ending

Use the `auto` template in `../SKILL.md`, end with an immediate-start statement in the user's language, then spawn in the same turn without asking a question.

## Explicit Delegation Requests

An Explicit Delegation Request may have no distinct Root Lane. Do not invent one or claim material lane benefit; state the requested child assignment and Root's coordination and integration responsibility instead.

## Focused Skills

Name the explicitly selected skill's retained Root Lane and describe the delegated role as a Supporting Child. Do not imply that Diverter replaces the skill.

## Failure Cases

Avoid:

- no declared Root Lane for implicit eligibility;
- Root work that duplicates the Child Lane;
- more roles than independent deliverables;
- an `ask` message without a permission question;
- an `auto` message that asks a question or pauses;
- redispatching an equivalent scope instead of Child Reuse;
- mentioning pre-activation native absence; or
- exposing internal loading, cache, alias, or retry details.
