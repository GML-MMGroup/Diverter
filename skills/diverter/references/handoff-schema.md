# Handoff Schema

Every child receives a self-contained, leaf-only handoff.

| Field | Required content |
| --- | --- |
| `delegation_context` | delegated-subagent bypass plus Leaf Child prohibition |
| `goal` | exact Child Lane outcome |
| `success_criteria` | observable definition of done |
| `scope_in` | owned evidence, artifact, or boundary |
| `scope_out` | excluded adjacent work and Root-owned responsibilities |
| `relevant_context` | files, URLs, IDs, facts, or entrypoints needed from a fresh start |
| `constraints` | task, safety, and process limits |
| `deliverable` | integration-ready result expected by Root |
| `verification` | evidence Root can independently check |
| `write_policy` | `read-only`, `mixed`, or `write-capable` |
| `write_ownership` | exclusive mutable artifact or bounded scope; `none` for read-only |
| `open_questions` | unresolved unknowns to keep visible |

Recommended template:

```md
delegation_context: delegated-subagent; parent Dispatch Authorization already granted; leaf child; do not invoke diverter, delegate, spawn descendants, or request another Dispatch Authorization; execute this handoff only
goal: Verify the documented contract used by the settings-save flow.
success_criteria: Return the applicable guarantee, version boundary, and authoritative evidence.
scope_in: official API contract for the save operation
scope_out: implementation tracing, final recommendation, code edits
relevant_context: framework version, API symbol, official documentation URL
constraints: read-only; distinguish documented fact from inference
deliverable: concise evidence summary with direct citations
verification: Root can open each cited source and match it to the installed version
write_policy: read-only
write_ownership: none
open_questions: whether the repository pins a version older than the documented guarantee
```

## Native Spawn Policy

Default role-specific spawn shape:

```text
agent_type: docs-researcher
fork_turns: "none"
prompt: <structured leaf handoff>
```

Do not pass temporary model or reasoning overrides. Do not combine a role-specific spawn with full-history forking. The installed role definition owns model, reasoning, sandbox, and role instructions.

## Reuse Policy

For a related follow-up, target the same canonical native child. A new child is reserved for a materially different scope or an explicit user request. Never create an equivalent second child for the same normalized scope.

## Write Policy

- `read-only`: no mutable artifact ownership.
- `mixed`: establish scope read-first, then write only within declared ownership.
- `write-capable`: edit only the declared artifact or bounded scope.

Parallel writes require disjoint `write_ownership`; overlapping ownership must be serialized.
