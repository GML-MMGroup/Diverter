# Apply auto policy to every work mode

When Diverter owns orchestration, the `auto` Delegation Policy dispatches suitable subagents after a brief announcement for `read-only`, `mixed`, and `write-capable` work alike. It does not add a separate confirmation before delegated writes: the user's task authorization, Codex sandbox and permission controls, and Diverter's existing serialization rules remain the safety boundaries. Treating writes differently would create an undeclared `auto-safe` policy and make `auto` behavior depend on Work Mode.
