# 队长会话形态：Manager 的 continuable 子会话 + 章程 + toolFilter（部分取代 ADR-0002）

M0 Spike 证实 `startContinuable` 的子会话**无条件继承父预设**（child-agent.ts:163-175 `composeFrom`）且无 preset/cwd 参数——「给队长挂独立『队长模式』预设」在 continuable 路径上不可实现。用户于 2026-09-09 定案路径 A：队长 = Manager 会话经 `ctx.subagents.startContinuable` 创建的常驻子会话；类别差异由**章程注入（per-child persona）**承载，工具面由 **per-child toolFilter** 裁剪；全部 7 个工具行挂管理模式预设。服务端身份校验（队长只能回报自己的任务）不依赖工具面，继续由 taskManager 服务强制。

取代关系：ADR-0002 中「队长模式为独立预设」一条由本决策取代；「统一预设 + 章程承载类别差异」的精神保留并强化（现在连预设都只有一个）。

## Consequences

- 队长会话不出现在顶层会话列表，而是 Manager 会话下的 continuable 子会话（GUI 子会话视图可见、可恢复、崩溃后冷恢复重放章程与 toolFilter——descriptor durable）。
- 会话 cwd 继承 Manager；任务目录由章程文本显式携带。
- toolFilter 的白/黑名单语义以 M0 结论（docs/plans/manager-task-orchestration.md「## M0 结论」）引用的源码为准；若语义不足以表达「队长只见回报工具」，上报重议而非放宽服务端校验。
- 若未来需要队长成为顶层 GUI 会话（路径 C），属 v2 增强，需重新 spike `ctx.agents.create` 的预设/cwd 参数面。
