# Diverter

Diverter recommends and supplies specialized subagents while leaving the parent Codex session under user control.

## Language

**Root Session**:
The user-controlled Codex session that evaluates a task, owns Diverter orchestration when Native Proactive Delegation is inactive, and integrates subagent results.
_Avoid_: Root agent configuration, managed root

**Delegation Policy**:
The user-level rule that determines whether Diverter waits for approval (`ask`) or dispatches immediately after announcing the lineup (`auto`) regardless of Work Mode. A successful change applies at the next `SessionStart` lifecycle event without project-level overrides; missing or invalid configuration resolves to `ask`.
_Avoid_: Work mode, execution mode

**Work Mode**:
The write-risk classification of delegated work: `read-only`, `mixed`, or `write-capable`.
_Avoid_: Delegation policy, Diverter mode

**Dispatch Announcement**:
The brief `auto` policy message that states why delegation fits, names exactly one lineup with role-specific assignments, and identifies the Work Mode before immediate dispatch. It is declarative and never requests approval.
_Avoid_: Suggestion, approval request

**Mode Control**:
The explicit-only `$diverter-mode` skill that reads or changes the user-level Delegation Policy. It bypasses the Delegation Gate and never delegates its own work.
_Avoid_: Core Diverter skill, implicit configuration

**Task Policy Override**:
An explicit user instruction that replaces the loaded Delegation Policy for one task when Diverter owns orchestration. It never changes the user-level configuration.
_Avoid_: Mode change, persistent policy

**Dispatch Authorization**:
The permission to start a selected lineup. User approval grants it under `ask`; the loaded policy grants it under `auto`.
_Avoid_: Work mode, tool permission

**Bundled Subagent**:
A specialized agent definition shipped by Diverter for delegated work. Diverter owns its default model configuration, and every bundled role enables live web search without requiring it to be used.
_Avoid_: Root agent, parent agent

**Static Model Mapping**:
The release mapping from each Bundled Subagent role to a GPT-5.6 model and reasoning effort. It remains the default until later evaluations justify a revision, with no runtime routing or automatic fallback.
_Avoid_: Model router, model profile

| Bundled Subagent | Model | Reasoning effort |
| --- | --- | --- |
| `code-mapper` | `gpt-5.6-terra` | `high` |
| `search-specialist` | `gpt-5.6-luna` | `medium` |
| `docs-researcher` | `gpt-5.6-luna` | `high` |
| `knowledge-synthesizer` | `gpt-5.6-luna` | `high` |
| `task-distributor` | `gpt-5.6-sol` | `medium` |
| `reviewer` | `gpt-5.6-sol` | `medium` |
| `security-auditor` | `gpt-5.6-sol` | `high` |
| `test-engineer` | `gpt-5.6-luna` | `xhigh` |
| `test-automator` | `gpt-5.6-terra` | `xhigh` |
| `web-performance-auditor` | `gpt-5.6-luna` | `xhigh` |

**Recommended Role Set**:
The default installation selection for common Diverter workflows: `code-mapper`, `docs-researcher`, `reviewer`, `security-auditor`, `test-engineer`, and `test-automator`.
_Avoid_: All roles, minimal roles

**Selected Role Set**:
The validated Bundled Subagents chosen through the `recommended`, `all`, or custom installation path. Only these roles are installed and overwritten.
_Avoid_: Lineup, active agents

**Role Installer**:
The plugin-provided script that installs the Selected Role Set into `${CODEX_HOME:-$HOME/.codex}/agents/` during the `.codex/INSTALL.md` flow. Codex runs it after installing the plugin; the user does not invoke it manually. It has no project-scoped mode and does not activate the Delegation Gate or modify instruction files.
_Avoid_: Gate installer, plugin installer

**Role Number**:
A stable numeric identifier used only to select a Bundled Subagent during installation. Existing numbers are never reassigned; new roles receive new numbers.
_Avoid_: Role order, priority

**Selection Intent**:
The set of Bundled Subagents the user means to install, interpreted by the Agent from structured or free-form input. The Agent asks again only when that intent is genuinely unclear; there is no user-facing input grammar.
_Avoid_: Selection syntax, parsed command

**Routing Smoke Test**:
The release check that starts one Terra, one Luna, and one Sol Bundled Subagent and confirms the requested model, reasoning effort, sandbox, and successful return.
_Avoid_: Quality evaluation, benchmark

**Execution Backend**:
The mechanism the Root Session uses after Dispatch Authorization to run a Bundled Subagent while preserving its Static Model Mapping, sandbox, and developer instructions.
_Avoid_: Model router, fallback model

**Native Subagent Backend**:
The preferred Execution Backend when the visible `spawn_agent` interface supports custom agent, model, and reasoning selectors.
_Avoid_: MultiAgent V1, default backend

**CLI Worker Backend**:
The compatibility Execution Backend that runs an independent `codex exec` process with the Bundled Subagent's explicit model, reasoning effort, sandbox, and instructions.
_Avoid_: Generic subagent mode, degraded mode

**CLI Worker Runner**:
The stateless, single-role Python 3.11+ plugin script that uses `tomllib` to read one installed Bundled Subagent TOML, accepts one delegated handoff on stdin, runs one `codex exec` worker, and returns its final output to the Root Session. Parallelism belongs to the Root Session, not the runner.
_Avoid_: Lineup orchestrator, worker daemon

**Backend Capability Check**:
The Root Session's inspection of the visible `spawn_agent` interface. Native Subagent Backend is selected only when the required selectors are exposed; otherwise CLI Worker Backend is selected without relying on the parent model name.
_Avoid_: Sol check, version check

**Native Proactive Delegation**:
A Codex session policy that explicitly permits the Root Session to create subagents without a separate user request. When active, Diverter is ineligible even when explicitly invoked; without that explicit policy signal, Diverter remains eligible.
_Avoid_: Ultra check, Sol check

**Orchestration Ownership**:
The rule that exactly one mechanism may coordinate subagent creation for a Root Session. Native Proactive Delegation owns orchestration whenever it is active; otherwise Diverter may coordinate under the active Delegation Policy.
_Avoid_: Backend preference, delegation priority

**Delegation Gate**:
The Root Session checkpoint that decides whether a task merits delegation before task work begins. The active Delegation Policy determines whether it waits for approval or dispatches immediately.
_Avoid_: Advisory gate, execution backend

**Delegation Gate Activation**:
The delivery of the Delegation Gate to a Root Session so that the checkpoint applies throughout that session.
_Avoid_: Automatic subagent trigger, AGENTS gate

**Sanitized Failure Reporting**:
The user-visible reporting rule that hides internal operational details while still reporting failures that change task execution or require user action. Intentional non-delegation and internal failures that recover successfully remain silent.
_Avoid_: Operational chatter, silent failure, no-operational-chatter
