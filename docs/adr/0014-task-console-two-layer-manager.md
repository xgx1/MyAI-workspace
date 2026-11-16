# 任务台以 Super Agent 工单库为事实源，管理器分大 / 项目两层

2026-11-16，用户在设计稿（[docs/superagent-manager-flow.html](</home/sx/projects/MyAI/docs/superagent-manager-flow.html>)）逐条拍板后确认：

1. **「项目」以 git 仓库根路径为主键**，工作区只是它的一个视图入口。
2. **项目管理器按需创建、空闲 30 分钟休眠**，由「该项目内出现新事件」唤醒；不用常驻会话。
3. **任务事实源归 Super Agent 的工单库**（`<DSH_HOME>/storages/super-agent`），任务台面板是它的视图。
   一张单只有一个 owner，不允许面板与工单库各存一份状态。
4. **触发器配置挂项目**（凭据、配额按项目算），任务只声明「我订阅哪几个源」。
5. **v0.1 交付方式硬编码一份允许清单**：只产 patch、不 push / 不开 PR、不碰受保护分支、不跨仓库。
   要放宽必须改配置并留痕，不允许项目管理器自行决定。
6. **大管理器要做**（覆盖设计稿里「v0.1 先用规则代替」的建议）。v0.1 的它只做两件事：
   判断项目归属、创建或复用该项目的项目管理器。

## 与既有 ADR 的关系

- **取代 [ADR-0011](</home/sx/projects/MyAI/docs/adr/0011-manager-task-list-as-view.md>) 的事实源选择**：任务清单仍然是视图（这点不变），
  但视图背后的 owner 从「纳管会话 / session-manager」改判给 Super Agent 的工单库。
- 沿用 [ADR-0010](</home/sx/projects/MyAI/docs/adr/0010-manager-explicit-adoption-and-creation-authority.md>)：创建工作对话 / 执行会话的权力只在管理端。
- 沿用 [ADR-0012](</home/sx/projects/MyAI/docs/adr/0012-non-blocking-questions.md>) 与 [ADR-0013](</home/sx/projects/MyAI/docs/adr/0013-questions-live-on-the-task-card.md>)：
  提问不阻塞，问题只出现在任务卡片上，管理会话不直接向用户提问。
- 执行会话的创建形态沿用 [ADR-0003](</home/sx/projects/MyAI/docs/adr/0003-captain-continuable-children-with-toolfilter.md>)：
  `ctx.subagents.startContinuable` + per-child `persona` / `toolFilter`。

## 实现落点

| 能力 | 落点 |
|---|---|
| 任务台入口（与 Super Agent 同级） | `dsh-extensions/plugins/dsh-task-manager/src/client/index.tsx`：`sidebar.panellist` + `main` 槽位（2026-11-16 已落地，v0.5.0） |
| 任务面板筛选列（全部 / 已指派 / 问题 / 下一步 / 运行中）、问题与订阅展示 | 同上（2026-11-17 落地） |
| 大管理器 / 项目管理器 | 会话层，一个全局 + 每项目一个；**不用** `startContinuable`，改 `sessionController.agents.createSession`（无宿主会话，见「实现状态」） |
| 管理模式预设 | `~/.dsh-dev/profiles/web/cordis.patch.toml` 新增 preset 行：只含 persona、指令、只读工具与管理工具 |
| 触发器、准入、worktree、交付 | `deepseek-harness-dev/extensions/dsh-super-agent/lib/{engine.js,sources/,delivery/}`（复用，不改上游口径） |
| 允许清单 | 插件侧常量 + 配置项，默认只 patch |

## 后果与风险

- 管理器两层意味着至少一个常驻会话（大管理器），上下文成本比纯面板高一截；项目管理器靠休眠摊平。
- 任务台与这些自主会话语义同进程（3081），Worker 按 `danger-full-access` 跑：切 `accept` 前必须收窄 `acceptSources` 并设满预算。
- `dsh-task-manager` 现有的 captain 编排与 `captains.json` 与本决策并存期间属于迁移中状态，
  新增逻辑不得再往 captain 路径上加。

## 实现状态（2026-11-17）

已在 3081 跑通整条链，代码在 `dsh-extensions`（提交 `a93e0c9` → `724d361` → `c271799`）：

- **指派 → 大管理器 → 项目管理器 → 执行会话**：`POST /dispatch` → 预设 `task-console-global` 的会话 →
  `task_dispatch_project` 建卡 + 起 `task-console-project` 的项目管理器 → 项目管理器 `task_next_step` +
  `task_start_execution`（实测一次跑通，卡片转 in-progress，执行会话在项目目录里开工）。
- **面板**：侧栏「任务管理」→ 五列筛选（全部 / 已指派 / 问题 / 下一步 / 运行中，带计数）+ 卡片 + 详情
  （项目、项目管理器会话、问题与其答复、起执行会话按钮）。
- **问题 / 下一步**：`task_question` / `task_next_step` 写卡，`POST /answer` 逐条答复并投回项目管理器（ADR-0012 语义不变）。
- **触发器订阅**：`task_project_sources` 把 inbox / github / ci 的订阅挂在项目记录上（`console.json`），
  任务卡只记本单引用；`task_console_state` 用「每项目未关单数 + 触发器」充当只读巡查面。

两处与上文「实现落点」不同、且是踩坑换来的：

1. **管理器不是 `startContinuable` 子会话**，而是 `sessionController` 建的顶层会话（`agents.createSession`）：
   两层管理器要跨会话存活、不能挂在某个对话（父）下面。代价是拿不到 per-child `toolFilter`，
   工具面只能靠预设与 `agent-configs` 白名单。
2. **`agent-configs.yaml` 决定工具可见性**：管理器会话的 cwd 不在 `projects` 里 → 一个工具都没有（模型会把调用写成文本）。
   因此管理器统一住 `<DSH_HOME>/task-manager/console`，两个 home 各加一条 `task-console` 配置（`tools: ["task_*"]`）。

仍未做：定时巡查（缺 `@deepseek-ai/dsh-tool-schedule`）、项目管理器 30 分钟空闲休眠（会话目前一直活着）、
受保护分支/跨仓库的机器校验（现在只写在 persona 与简报的允许清单里）。
