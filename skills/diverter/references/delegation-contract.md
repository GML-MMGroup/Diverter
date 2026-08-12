# Delegation Contract

Every Diverter message uses one shared structure and one policy ending.

## Shared Information

Convey these in order:

1. Why separate Root and Child lanes materially help.
2. Exactly one Smallest Sufficient Lineup of 1-4 available roles, with a bounded Child Lane for each.
3. The distinct useful Root Lane that will continue while children run.
4. Exactly one Work Mode: `read-only`, `mixed`, or `write-capable`.

Keep the message conversational and concise. Never list alternatives, invent roles, describe results that do not exist, or imply a child started before the message.

## `ask` Ending

End with a direct permission question matched to the Work Mode, then stop before task work and spawning.

> This splits cleanly: `docs-researcher` can verify the API contract as a bounded Child Lane, while I trace the implementation and prepare the decision criteria in the Root Lane. Work Mode is `read-only`. Should I dispatch that supporting check?

Refusal means zero spawn and ordinary Root continuation.

## `auto` Ending

End with a declarative Dispatch Announcement, then spawn in the same turn without asking a question.

> This splits cleanly: `docs-researcher` will verify the API contract as the Child Lane, while I trace the implementation and prepare the decision criteria in the Root Lane. Work Mode is `read-only`. I'm dispatching that check now and will integrate the evidence here.

## Focused Skills

Name the explicitly selected skill's retained Root Lane and describe the delegated role as a Supporting Child. Do not imply that Diverter replaces the skill.

## Failure Cases

Avoid:

- no declared Root Lane;
- Root work that duplicates the Child Lane;
- more roles than independent deliverables;
- an `ask` message without a permission question;
- an `auto` message that asks a question or pauses;
- redispatching an equivalent scope instead of Child Reuse;
- mentioning pre-activation native absence; or
- exposing internal loading, cache, alias, or retry details.
