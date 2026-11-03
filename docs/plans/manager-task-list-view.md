---
tags: [DSH, 管理模式, 实施计划, 任务清单]
status: 待批准
---

# 管理模式任务清单闭环 — 实施计划

行为契约见[功能文档](</home/sx/projects/MyAI/docs/functional/manager-task-mode.md>)，决策见 [ADR-0011](</home/sx/projects/MyAI/docs/adr/0011-manager-task-list-as-view.md>)。本计划只写"改哪个文件、改成什么、怎么验"。

## 验收标准

在 3081 上，一个普通用户能走完：新建「管理模式」对话 → 让它在一个工作区干活 → 任务清单出现卡片并可跳进那个工作对话 → 工作对话提问时卡片转「等待回复」并出回复框 → 答复后只放行那一件 → 卡片上打开执行汇报 Markdown。

## 事实基础（已核实）

- `@deepseek-ai/dsh-session-manager` 已构建（`lib/`）、已在 `tsconfig.host.json:380` 引用、别名已在 `tsconfig.base.json:532`；缺的是 `apps/cli/package.json` 依赖、profile 依赖与两条 composition 行。
- 包内没有 `ctx.provide`、没有 HTTP 路由（`src/index.ts` 全文只在 `50-64` 扩了 `MessageSourceMap`）；唯一读入口是 `manager_list` 工具。
- 管理关系的持久化在 storage domain `session_manager`：`links`(workerId→…) / `questions`(含 workerId/managerId/status/questions[]) / `deliveries` / `creations`(含 `message`) / `pausedManagers`。
- 管理会话的 pre-step 明确放行 `message.source.kind === 'user'` 的消息（`index.ts:212`）→ 回复框只要能往管理会话投一条 human message 就能进入它的下一轮。
- 冷恢复原语 `sessionController.resolveAgent(sessionId)`（`packages/api/session-controller/src/agent.ts:161`）。
- 会话日志读面 `sessionQuery.listEvents(sessionId)`（`packages/session-query/session-query/src/index.ts:269`）。
- `workerPresets` 必须是真实预设 id；dev 现有 `standard/ptc/minimal/cordis/js/unreal/...`。

## 设计要点

- **不改 harness 包的持久化 schema**：报告正文不落新表，执行汇报从管理会话日志里取（`source.kind === 'session-manager'` 且 `workerSessionId` 匹配的 `user/message`）。这样这一轮对 `deepseek-harness-dev` **零代码改动**，只做 profile 配置启用。
- **视图与投递都放在 `dsh-task-manager`**（dsh-extensions 仓）：它已经 `ctx.provide('taskManager')`、已注册 `/plugins/dsh-task-manager/*`，加两条路由是最小改动面。
- **状态只用能派生出来的三种**：`waiting-reply`（有 pending 问题）、`paused`（被暂停/已分离）、`in-progress`（其余）。功能文档里的六态里其余三种本轮标「待实现」。
- **旧任务列表保留为回落**：`/managed` 拿不到数据（未启用/未纳管）时，面板继续显示原来的 `tasks.json` 列表，不做破坏性替换。

## 文件结构

| 文件 | 改动 | 职责 |
| --- | --- | --- |
| `dsh-extensions/plugins/dsh-task-manager/src/managed.ts` | 新增 | 读 `session_manager` 域并映射成卡片；组装执行汇报 Markdown |
| `dsh-extensions/plugins/dsh-task-manager/src/managed-reply.ts` | 新增 | 把一条人类消息投进管理会话（live 用 followup，冷用 resolveAgent） |
| `dsh-extensions/plugins/dsh-task-manager/src/index.ts` | 修改 | 注册 `GET /managed`、`POST /managed-reply`、`GET /managed-report` |
| `dsh-extensions/plugins/dsh-task-manager/src/client/index.tsx` | 修改 | 优先渲染纳管卡片；回复框接新路由；locale 词条 |
| `dsh-extensions/plugins/dsh-task-manager/tests/managed.test.ts` | 新增 | 视图映射、回复投递、汇报 Markdown |
| `~/.dsh-dev/profiles/web/package.json` | 修改 | 加 `@deepseek-ai/dsh-session-manager` 依赖 |
| `~/.dsh-dev/profiles/web/cordis.patch.yml` | 修改 | insert `session-manager` 行 + `preset-management` 行 |

## 任务

### T1 启用 session-manager（无代码）

- `~/.dsh-dev/profiles/web/package.json`：dependencies 加 `"@deepseek-ai/dsh-session-manager": "link:/home/sx/projects/MyAI/deepseek-harness-dev/packages/session/session-manager"`。
- 该目录下 `pnpm install --registry=https://registry.npmmirror.com --prefer-offline`。
- `~/.dsh-dev/profiles/web/cordis.patch.yml` 追加一个 `- insert:` 段：

```yaml
- insert:
    - id: session-manager
      name: '@deepseek-ai/dsh-session-manager'
      config:
        managerPreset: management
        workerPresets: [js, unreal]
        maxMessageBytes: 16384
        questionWaitSeconds: 1
    - id: preset-management
      name: '@deepseek-ai/dsh-agent-preset'
      config:
        id: management
        name: 管理模式
        description: 只管理对话，不直接执行任务。
        plugins: []
```

- `systemctl --user restart dsh-web-dev.service`。
- **验收**：3081 新建会话能看到「管理模式」；该会话工具目录只有 7 个管理工具、没有 bash/fs；`/manage` 命令存在。
- **注意**：`apps/cli/package.json` 补依赖属正式化步骤，本轮不做（不影响 profile 解析）。

### T2 读视图

- `src/managed.ts`：`readManagedCards(domain)` —— 入参是 `ctx.get('storageDomain')?.get('session_manager')` 的 `DomainImpl`（未类型化，读到后用窄接口断言一次），产出：
  `{ workerId, managerId, workspaceId, preset, title, status, paused, question?: { id, items: [{question, header?, options?}] } }`。
  `title` 取 `creations[workerId].message` 首个非空行，截 60 字；无则用短 id。
- `src/index.ts`：`GET /plugins/dsh-task-manager/managed` → `{ cards }`；域拿不到时返回 `{ cards: [], unavailable: true }`（客户端据此回落）。
- **测试**：`tests/managed.test.ts` 用假 domain 覆盖 —— 有 pending 问题→`waiting-reply`；paused→`paused`；无问题→`in-progress`；无 creations 时标题回落短 id；域缺失返回 `unavailable`。

### T3 回复投递

- `src/managed-reply.ts`：`deliverHumanMessage(runtime, managerSessionId, text)` ——
  先 `agents.get(managerSessionId)`；不在则 `sessionController.resolveAgent(managerSessionId)`；
  拿到 agent 后 `agent.followup({ id, role: 'user', content: [{type:'text',text}], source: { kind: 'user' } })`（与既有 `createOutboundMessage` 同构，只换 source）。失败抛 `DELIVERY_UNAVAILABLE`。
- `src/index.ts`：`POST /managed-reply { managerSessionId, text }`，空文本 400，投递失败 409。
- **测试**：live 分支走 `followup`；不 live 走 `resolveAgent` 后再 `followup`；两者都不可用时报 409。

### T4 客户端

- `TaskView` 的 `refresh()` 并行拉 `/managed`；`cards.length > 0` 时进入「纳管模式」，否则维持现有列表。
- 纳管卡片：标题 + 状态徽章（进行中 / 等待回复 / 已暂停）+ 「打开对话」+「执行汇报（Markdown）」；`waiting-reply` 时卡片下方展示问题与回复框。
- 回复框提交 `POST /managed-reply`，成功后重拉 `/managed`。
- 新增 locale 词条：`managedTitle`、`statusPaused`、`reportPending`、`managedUnavailable`。

### T5 执行汇报

- `src/managed.ts`：`buildManagedReportMarkdown(runtime, card)` —— `sessionQuery.listEvents(managerId)`，筛 `event.type === 'user/message'`、`source.kind === 'session-manager'`、`source.workerSessionId === workerId` 的最后 5 条，正文原样引用。
- `GET /plugins/dsh-task-manager/managed-report?workerSessionId=&managerSessionId=` → `text/markdown; charset=utf-8`。
- 取不到日志时输出卡片信息 + 「暂无回报」，不报错。

### T6 偏好、校正与文档

- 无代码：`manager_preferences` 的 lookup/remember/correct/forget 已在包内；「我进行校正」写进功能文档与使用说明。
- 技能沉淀本轮不落盘，功能文档「偏好沉淀」一节标「待实现（技能）」保持诚实。

### T7 生产切换（门禁）

- 只在 T1–T5 在 3081 全绿后进行：同一份 profile 改动照搬到 `~/.dsh/profiles/web/`（link 路径指向生产检出），重启 `dsh-web.service`。
- **需要用户当场点头**：重启会掐断当时正在进行的对话。

## 验证命令

```sh
cd /home/sx/projects/MyAI/dsh-extensions/plugins/dsh-task-manager
pnpm typecheck && pnpm test && pnpm build
systemctl --user restart dsh-web-dev.service
curl -s http://127.0.0.1:3081/plugins/dsh-task-manager/managed | head -c 400
```

DP：3081 手工走一遍验收标准；`session-manager` 包本身不改，故不跑 harness 的 `pnpm run build` / 快照。

## 风险

- **跨插件读未类型化域**：`storageDomain.get('session_manager')` 的返回是 `DomainImpl`；会话管理包若改 schema，本插件静默降级为 `unavailable` 而不是崩。已在 T2 的测试里固定「域缺失 → 回落」。
- **回复投递依赖管理会话可解析**：管理会话被删除/归档时投递失败，界面显示 409 原因，不假装成功。
- **旧列表并存**：纳管模式与旧任务列表二选一渲染，不会混在一起；旧体系正式下线时再删。
