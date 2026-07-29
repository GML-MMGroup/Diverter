<p align="center">
  <img src="assets/diverter-hero-figure.png" alt="Diverter agent lineup" width="640">
</p>

<h1 align="center">Diverter</h1>

<p align="center">
  <a href="README.md">English</a> | <a href="README.zh.md">简体中文</a>
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="License: MIT"></a>
  <a href="https://github.com/openai/codex"><img src="https://img.shields.io/badge/OpenAI-Codex-000000?labelColor=555555" alt="OpenAI Codex"></a>
  <a href="https://github.com/GML-MMGroup/Diverter/stargazers"><img src="https://img.shields.io/github/stars/GML-MMGroup/Diverter?style=flat" alt="GitHub Stars"></a>
</p>

<p align="center">
  <img src="assets/diverter-hero-tagline.png" alt="One task in. The right subagents out." width="480">
</p>

Diverter helps Codex know when to delegate: complex tasks call in specialists as needed, while simple tasks stay in the main thread.

## ✨ See Diverter in action

<p align="center">
  <img src="assets/diverter-promo.gif" alt="Diverter delegates a release audit to specialist subagents and merges their results" width="720">
  <br>
  <sub>A release audit splits across specialists, then returns through the same guardrails.</sub>
</p>

## 🚀 Quick Start

**Codex CLI `0.145.0+` is recommended for the full native subagent experience.**

1. Tell Codex:

   ```text
   Fetch and follow instructions from https://raw.githubusercontent.com/GML-MMGroup/Diverter/refs/heads/main/.codex/INSTALL.md
   ```

2. After installation, open `/hooks`, review and trust Diverter's `SessionStart` Hook, then start or reopen a task.

3. New installations start in `ask`. Inspect or change the user-level policy with:

   ```text
   $diverter-mode status
   $diverter-mode auto
   $diverter-mode ask
   ```

<table align="center">
  <thead>
    <tr>
      <th align="center">Policy</th>
      <th align="center">Behavior</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td align="center"><code>ask</code></td>
      <td>Proposes one lineup and waits for approval before dispatching</td>
    </tr>
    <tr>
      <td align="center"><code>auto</code></td>
      <td>Announces one lineup and dispatches it immediately for any Work Mode</td>
    </tr>
  </tbody>
</table>

Policy changes apply at the next `SessionStart`; restarting or reopening the task is the predictable way to apply one. `auto` changes dispatch authorization, not Codex permissions, sandboxing, or handoff write boundaries.

## 🎭 Roles

Diverter includes ten Bundled Subagents. The installer offers the recommended set (`code-mapper`, `docs-researcher`, `reviewer`, `security-auditor`, `test-engineer`, and `test-automator`), all roles, or a custom selection.

| Role | GPT-5.6 model | Reasoning effort | What it does |
|---|---|---|---|
| `code-mapper` | `gpt-5.6-terra` | `high` | Traces code paths, symbols, and ownership boundaries |
| `search-specialist` | `gpt-5.6-luna` | `medium` | Gathers focused repository or external evidence |
| `docs-researcher` | `gpt-5.6-luna` | `high` | Verifies official APIs, versions, and guarantees |
| `knowledge-synthesizer` | `gpt-5.6-luna` | `high` | Reconciles long or conflicting findings |
| `task-distributor` | `gpt-5.6-sol` | `medium` | Splits broad goals into bounded work packages |
| `reviewer` | `gpt-5.6-sol` | `medium` | Reviews correctness, regressions, and maintainability |
| `security-auditor` | `gpt-5.6-sol` | `high` | Audits trust boundaries, secrets, and agent-tool safety |
| `test-engineer` | `gpt-5.6-luna` | `xhigh` | Designs minimal test coverage for behavior and risk |
| `test-automator` | `gpt-5.6-terra` | `xhigh` | Adds bounded regression tests after behavior is clear |
| `web-performance-auditor` | `gpt-5.6-luna` | `xhigh` | Audits Web performance evidence and Core Web Vitals risks |

Diverter selects capabilities first, then maps them to roles available in your Codex environment. Missing preferred roles are reported rather than silently substituted. Custom role sets can adapt [`role-lineups.md`](skills/diverter/references/role-lineups.md).

## 🔄 Work Modes

| Work Mode | Boundary |
|---|---|
| `read-only` | Inspect and report; never write files |
| `mixed` | Investigate first, then perform bounded writes; writers stay serialized unless paths are explicitly disjoint |
| `write-capable` | Edit only within the explicit handoff and sandbox |

Diverter always names one Work Mode before dispatch.

## 🎯 When Diverter Delegates

At most intelligence levels, subagent delegation must be requested explicitly; Ultra may delegate proactively. Diverter fills the explicit-delegation path and silently steps aside when native proactive delegation owns the session. See OpenAI's [subagent documentation](https://learn.chatgpt.com/docs/agent-configuration/subagents).

| Delegates when | Stays focused when |
|---|---|
| Independent work lanes can run in parallel | The task is simple or single-lane |
| Code and official documentation need separate verification | Writes are tightly coupled, or one fact is needed first |
| Security, test, performance, or release risk calls for a specialist | The user opts out explicitly, or the request is still ambiguous |

Diverter matches the user's language. Role names and Work Mode tokens remain in English.

## ⚙️ How It Works

1. The `SessionStart` Hook loads the user-level Delegation Policy and activates the Delegation Gate.
2. Diverter first yields to native proactive delegation. Otherwise it decides whether to stay in the main thread or select one lineup of up to four roles and one Work Mode.
3. `ask` waits for approval; `auto` announces and dispatches immediately. The execution backend then runs bounded handoffs through native custom agents or temporary leaf `codex exec` workers.

Every handoff carries an explicit goal, scope, write policy, and verifiable deliverable. See [`delegation-contract.md`](skills/diverter/references/delegation-contract.md) and [`handoff-schema.md`](skills/diverter/references/handoff-schema.md).

## 🙏 Acknowledgments

- The always-on gate and session-bootstrap pattern was inspired by [obra/superpowers](https://github.com/obra/superpowers).
- The bundled role pack is a curated adaptation of [VoltAgent/awesome-codex-subagents](https://github.com/VoltAgent/awesome-codex-subagents).
- Review, security, test, and Web performance role design was informed by [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills).

## 🤝 Contributing & License

Issues and pull requests are welcome. Useful contributions improve task-shape rules, role mappings, positive and negative examples, or eval scenarios. A good new rule includes both a prompt that should trigger delegation and a similar prompt that should stay focused.

Start with [`decision-rules.md`](skills/diverter/references/decision-rules.md), [`role-lineups.md`](skills/diverter/references/role-lineups.md), and [`evals/scenarios.md`](evals/scenarios.md).

This project is released under the [MIT License](LICENSE).
