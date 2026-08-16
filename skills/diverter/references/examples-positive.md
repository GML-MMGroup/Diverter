# Positive Examples

These are examples that should usually trigger delegation.

## English

1. `Trace the checkout error while a docs specialist independently verifies the framework guarantee; integrate both into a fix recommendation.`
2. `Draft the migration checklist while one specialist maps the affected compatibility boundary.`
3. `Use one subagent to audit keyboard and screen-reader constraints while you continue the sidebar design proposal.`
4. `Add a bounded regression test in tests/settings while you independently verify the behavior boundary and integration risk.`

## Chinese

5. `你继续整理迁移方案，同时让一个子代理独立核对官方 API 的兼容边界。`
6. `你负责分析代码路径，让一个 docs 专家并行核验这个 API 的文档保证。`
7. `你先起草方案的判断标准，同时让一个研究角色收集三种重试策略的证据。`
8. `$grill-with-docs 继续主导这个设计讨论，但可以让一个子代理独立检查无障碍约束。`
9. `In Root, trace the auth request flow and trust boundaries while an independent audit checks permission bypasses, token handling, and missing server-side checks.`
10. `In Root, map the agent tool approval flow while an independent security audit checks secret exposure and destructive actions without approval.`
11. `In Root, map the checkout flow and current coverage while an independent test analysis identifies missing cases before we change anything.`
12. `In Root, identify the settings save behavior boundary while an independent test lane adds only the bounded regression tests.`
13. `In Root, map the Next.js rendering and data-loading boundaries while an independent performance audit checks LCP, INP, CLS, images, and client rendering.`
14. `In Root, trace the branch architecture and release surface while an independent review checks code quality, security risk, and missing tests.`

Why these are positive examples:

- they have a bounded Child Lane and a distinct useful Root Lane
- they are mostly read-heavy before any writes
- they benefit from specialist viewpoints or parallel evidence gathering
- the Root Lane can make substantive progress while the child runs
- the smallest useful lineup can start with one child
