<p align="center">
  <img src="assets/diverter-hero-figure.png" alt="Diverter 子代理阵容" width="640">
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

<p align="center">
  <strong>你为复杂任务开启 Ultra，结果连查资料、跑测试这些独立工作，也在消耗宝贵额度。真的每一步，都需要 Ultra 亲自上吗？</strong>
</p>

## 💡 为什么选择 Diverter

⚡ **Diverter 把 Ultra 的委派策略蒸馏到非 Ultra 的 Codex 会话中：该分工时叫专家，主线程继续推进；简单任务，依然保持简单。**

- **不开 Ultra，也能用上从 Ultra 蒸馏出的委派策略。** 把任务拆分、专家路由和结果整合带到非 Ultra 的 Codex 会话。
- **不用手动编排 Agent。** Diverter 判断什么时候值得分工，并找到合适的专家。
- **主线程继续推进。** 专家处理可独立完成的工作，简单任务依然保持简单。

## ✨ 看 Diverter 如何分工

<p align="center">
  <img src="assets/diverter-promo.gif" alt="Diverter 将发布审计分派给不同专家子代理，再汇总返回" width="720">
  <br>
  <sub>一次发布审计如何拆给不同专家，再带着同样的安全边界汇总返回。</sub>
</p>

## 🚀 快速开始

**Diverter 的原生子代理与 Root-only turn Hook 最低需要 Codex CLI `0.145.0`。**

1. 告诉 Codex：

   ```text
   请获取并按照这个安装说明执行：https://raw.githubusercontent.com/GML-MMGroup/Diverter/refs/heads/main/.codex/INSTALL.md
   ```

2. 安装完成后打开 `/hooks`，检查并信任 Diverter 的 `SessionStart` 与 `UserPromptSubmit` Hook，然后新建或重新打开任务。

3. 安装时选择 `auto`（推荐，用于主动分派）或 `ask`（批准后分派）。通过以下命令查看或修改用户级策略：

   ```text
   $diverter-mode status
   $diverter-mode auto
   $diverter-mode ask
   ```

## 🎯 Diverter 如何帮你

Diverter 会识别哪些工作值得交给专家，并让主任务在专家处理独立交付物的同时继续推进。

- 你选择的 skill 继续掌控主流程，只在确实有帮助时获得聚焦支持。
- 清晰的写入边界让独立修改同步推进，并把重叠修改改为串行处理。
- 主线程检查并整合专家结果，最终交付一个一致的答案。

当 Codex 已经拥有原生主动委派的编排权时，Diverter 会静默让路。参见 OpenAI 的[子代理文档](https://learn.chatgpt.com/docs/agent-configuration/subagents)。

已经过 60+ 项自动化测试和真实原生子代理生命周期运行验证。

## 🧭 选择委派策略

<table align="center">
  <thead>
    <tr>
      <th align="center">策略</th>
      <th align="center">行为</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td align="center"><code>ask</code></td>
      <td>提议一个阵容，并在分派前等待批准</td>
    </tr>
    <tr>
      <td align="center"><code>auto</code></td>
      <td>告知一个阵容，并针对任意工作模式立即分派</td>
    </tr>
  </tbody>
</table>

策略变更在下一次 `SessionStart` 生效；重启或重新打开任务是最可预期的方式。`auto` 只改变分派授权的时机，不改变 Codex 权限、sandbox 或 handoff 写入边界。

## 🎭 角色

Diverter 内置十个专业子代理。安装器支持推荐组合（`code-mapper`、`docs-researcher`、`reviewer`、`security-auditor`、`test-engineer` 和 `test-automator`）、全部角色或自定义选择。

| 角色 | GPT-5.6 模型 | Reasoning effort | 功能 |
|---|---|---|---|
| `code-mapper` | `gpt-5.6-terra` | `high` | 追踪代码路径、符号和归属边界 |
| `search-specialist` | `gpt-5.6-luna` | `medium` | 收集聚焦的仓库或外部证据 |
| `docs-researcher` | `gpt-5.6-luna` | `high` | 核验官方 API、版本和文档保证 |
| `knowledge-synthesizer` | `gpt-5.6-luna` | `high` | 对齐冗长或互相冲突的结果 |
| `task-distributor` | `gpt-5.6-sol` | `medium` | 将宽泛目标拆成有边界的工作包 |
| `reviewer` | `gpt-5.6-sol` | `medium` | 审查正确性、回归和可维护性 |
| `security-auditor` | `gpt-5.6-sol` | `high` | 审计信任边界、密钥和 agent-tool 安全 |
| `test-engineer` | `gpt-5.6-luna` | `xhigh` | 针对行为和风险设计最小测试覆盖 |
| `test-automator` | `gpt-5.6-terra` | `xhigh` | 在行为明确后添加有边界的回归测试 |
| `web-performance-auditor` | `gpt-5.6-luna` | `xhigh` | 审计 Web 性能证据和 Core Web Vitals 风险 |

Diverter 先选择能力，再映射到 Codex 环境中已安装的原生角色。自定义角色集可以调整 [`role-lineups.md`](skills/diverter/references/role-lineups.md)。

## 🔄 工作模式

| 工作模式 | 边界 |
|---|---|
| `read-only` | 只检查和报告，不写入文件 |
| `mixed` | 先调查，再按明确的产物归属进行有边界的写入 |
| `write-capable` | 只在显式 handoff 和 sandbox 范围内编辑 |

Diverter 在分派前始终明确标注一种工作模式。

## ⚙️ 工作原理

1. `SessionStart` Hook 加载用户级委派策略和完整 Session Contract，并在 compact 后恢复两者。
2. 每个 Root turn 开始前，`UserPromptSubmit` 只注入一条简短 Turn Reminder；子代理 turn 通过 `agent_id` 被确定性过滤，不接收提醒。
3. Preflight 会在内部判断强正向任务信号、明确排除项，以及偏读或偏写的 tie-breaker。所有 `ROOT_ONLY` 都保持沉默；适合委派的任务会在任何任务工作前加载 Diverter，并把对应策略的分派消息作为回执。
4. Diverter 再选择有边界的 Child Contribution、最小充分阵容和 Work Mode。偏读探索、代码与文档核对、独立证据、专业审查和 Root 上下文节约都会让判断倾向委派，同时不要求另一个并行的 Root 交付物。`ask` 等待批准，`auto` 告知后立即分派。
5. Root 可以继续推进有价值的工作，也可以等待必要的 Child 结果；所有子代理仍保持叶子节点。随后由 Root 负责判断、按风险验证、整合和最终交付。

相关追问会回到同一个原生子代理，延续它已经建立的上下文。

每个 handoff 都包含显式目标、范围、写入策略和可验证交付物。详见 [`delegation-contract.md`](skills/diverter/references/delegation-contract.md) 和 [`handoff-schema.md`](skills/diverter/references/handoff-schema.md)。

Diverter 会匹配用户的语言；角色名称和工作模式标记保持英文。

## 🙏 致谢

- 始终在线门控与 session-bootstrap 模式参考自 [obra/superpowers](https://github.com/obra/superpowers)。
- 内置角色包是对 [VoltAgent/awesome-codex-subagents](https://github.com/VoltAgent/awesome-codex-subagents) 的精选改编。
- 审查、安全、测试和 Web 性能角色的设计参考了 [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills)。

## 🤝 贡献与许可

欢迎提交 Issue 和 Pull Request。有效的贡献可以改进任务形态规则、角色映射、正反例或评估场景。一条好的新规则应同时包含一个应该触发分派的提示，以及一个相似但应留在主线程的提示。

先从规范性的 [`session-contract.md`](skills/diverter/references/session-contract.md) 开始，再用 [`decision-rules.md`](skills/diverter/references/decision-rules.md) 查看案例、用 [`role-lineups.md`](skills/diverter/references/role-lineups.md) 查看角色映射，并用 [`evals/scenarios.md`](evals/scenarios.md) 做验证。

本项目基于 [MIT License](LICENSE) 发布。
