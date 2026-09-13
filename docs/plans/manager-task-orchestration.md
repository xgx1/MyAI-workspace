# Manager 任务编排实现计划（v1）

> 需求来源：`/grill-with-docs` 三轮拷问已锁定并经用户确认（2026-09-09）。
> 术语见 `CONTEXT.md`；决策见 `docs/adr/0001`（清单宿主+写权）、`docs/adr/0002`（统一预设+章程）。

## 已锁定决策摘要

| 决策点 | 结论 |
|---|---|
| 清单宿主 | 扩展 `dsh-extensions/plugins/dsh-task-manager`（GUI+6状态机+落盘已在） |
| 写权 | Manager（管理工具）+ 人类（GUI）可写；队长仅受限回报接口 |
| 任务来源 | 用户双入口：GUI 建单 + 口头吩咐 Manager 代建 |
| 队长 | 真实常驻会话、按类别动态创建、复用；统一「队长模式」预设+类别章程注入；全自动创建免批；并发不设限（知情选择） |
| 回报 | 队长调受限接口写回状态+报告（单一事实源）；Manager 形式核验关单；失败重试 1 次后挂单上报 |
| 状态机 | 沿用 6 状态 + 新增编排字段；优先级/依赖不做 |
| 派发节奏 | v1 吩咐 + 巡检制（无事件推送） |

## 架构

```
GUI TaskView ──HTTP(/plugins/dsh-task-manager/*)──┐
                                                  ▼
                              dsh-task-manager (host half, dsh-extensions)
                              ├─ TaskStore: ~/.dsh/task-manager/tasks.json   ← 唯一任务事实源
                              ├─ CaptainRegistry: ~/.dsh/task-manager/captains.json
                              ├─ taskManager 服务（host 平面，供工具通道调用，带会话身份）
                              └─ 队长生命周期：ctx.subagents.startContinuable 创建/复用
                                                 + user/message 投递 + 唤醒
                                   ▲                          ▲
        管理工具行（task_assign 等）│                          │ 回报工具行（task_claim/task_report）
                                   │                          │
                        Manager 会话（管理模式预设）      队长·<类别> 会话（队长模式预设，cwd=任务目录）
```

- **身份模型**：HTTP 路由无会话身份（GUI 全权，人类语义）；模型工具经 `exec.agent` 携带会话身份，服务端校验「队长只能回报/认领派给自己的任务」。
- **派发** = Manager 工具调 `assign(taskId, category)` → 注册表查类别 → 无则 `startContinuable` 新建队长会话（预设=队长模式、首条消息=章程+任务简报），有则向既有会话投递新任务消息。
- **回报** = 队长调 `task_report(taskId, status, text, evidence)` → 服务端写回 TaskRecord 并打 `updatedAt`，Manager 巡检时消费。

## 里程碑

### M0 — Spike：原语确认（只读）
- 读 `deepseek-harness/packages/experimental/agent-team/src/roster.ts:244-290`（spawnAdmitted → `startContinuable` 参数：preset/cwd/model/label）、`mailbox.ts`（dispatchOnce 的 `user/message` 追加+唤醒调用面）、`packages/subagent/subagent-spawn-in-process`（continuable 语义与 GUI 可见性）。
- 确认 dsh-extensions 工具包被预设行引用的装载路径（对照 `editing-cordis-compositions` 技能 + dsh-agent-teams 的挂载方式）。
- **产出**：参数清单 + 装载结论写回本计划附录；若预设无法引用外部包 → 触发 R1 fallback（ADR-0003）。
- 验证：结论可复述出「建会话一行代码长什么样」。

### M1 — 插件 host half 编排增量
- `TaskRecord` 扩展：`category?`、`captainSessionId?`、`dispatchRound`、`report?{text, at, evidence?}`、`needsFinalReview`、`lastNudgeAt?`；旧记录缺字段容忍（读时补默认）。
- 新增 `captains.json` 注册表：`category → { charter, sessionId?, createdAt, lastDispatchAt }`。
- 新增 `taskManager` host 服务：`assign` / `report` / `listMine` / `nudge` / captains CRUD；内部复用 `TaskStore.mutate` 串行写。
- 新增 HTTP 路由（GUI 用）：`/captains`（列表+章程编辑）、`/assign`、`/report`（GUI 手动补录）。
- 单元测试：字段迁移、并发写、队长身份校验拒绝路径。
- 验证：`cd /home/sx/projects/MyAI/dsh-extensions/plugins/dsh-task-manager && pnpm test` 全绿（仓库根无 package.json，pnpm 不向上找——插件级即验收级）。

### M2 — 模型工具消费者
- 管理工具（仅编入管理模式）：`task_assign`、`task_create`、`task_set_status`、`task_list`、`task_nudge`。
- 队长工具（仅编入队长模式）：`task_claim`（领派发）、`task_report`（状态+报告+证据路径）。
- 按 `defineTool` 模式（照 `tool-todo`：`inject:['tools']`、`exec.agent` 身份、output schema + render）。
- 验证：工具单测 + 真会话冒烟调用。

### M3 — 预设铸造（`~/.dsh/.agent-presets/`）
- `agentPresets.copy(omni → manager)`，名「管理模式」：追加管理工具行；persona 注入编排协议（读单→动态分类→派发→巡检→形式核验关单→失败重试一次→挂单上报→终审旗标处理）。
- `agentPresets.copy(omni → captain)`，名「队长模式」：**裁掉** workflow / ralph / 团队编排类工具行；追加 `task_claim` / `task_report`；persona 注入队长纪律（回报必须含状态+证据）。
- 验证：`standingKeyFor('manager')`、`standingKeyFor('captain')` 双通过；GUI 各开一个真会话核对工具清单。

### M4 — GUI 增量（client half）
- 任务详情：类别 / 队长会话 / 派发轮次 / 回报时间线；列表按类别筛选。
- 建单对话框：「需终审」勾选。
- 验证：`pnpm run dev:web` 手动过一遍新建→详情→筛选。

### M5 — 端到端闭环验收
- 手动验收清单（逐条打勾）：
  1. GUI 建单（含需终审旗标）→ Manager 吩咐「巡检」→ 新类别自动建队长并派发；
  2. 同类别第二单复用同一队长（`captainSessionId` 不变、轮次 +1）；
  3. 队长回报 → Manager 形式核验 → `done`；缺证据打回 `problem`；
  4. 失败单：重试 1 次 → 挂单 + 用户可见上报；
  5. 需终审单：回报后停 `waiting-check`，用户终审后才 `done`；
  6. 旧 tasks.json 两条记录原样可见。
- 回归：dsh-extensions 仓全部既有测试。

## 风险与备选

- **R1 装载通道**：预设行引用不了 dsh-extensions 包 → fallback：队长经 bash+curl 调 HTTP 回报（体验降级，写 ADR-0003）。
- **R2 队长会话形态**：`startContinuable` 的父子关系与 GUI 呈现在 M0 定案；倾向 continuable（durable、可恢复、GUI 可见）。
- **R3 并发失控**：不设限为知情选择；出现失控加「类别/在飞任务」熔断属小改。
- **R4 状态语义**：派发后 = `in-progress`；回报待核 = `waiting-check`；打回 = `problem`。M1 在插件 README 定死映射表。

## 定案补记（M0 后，2026-09-09）

用户裁定**路径 A**（详见 docs/adr/0003）：队长 = Manager 的 continuable 子会话；章程（persona）承载类别差异，toolFilter 裁剪工具面；**「队长模式」独立预设取消**，全部 7 个工具行挂管理模式预设。装载通道裁定为「可引用」，R1 fallback 不触发。

**toolFilter 配置面（契约）**：

| 会话 | 工具面 |
|---|---|
| Manager（管理模式） | 管理工具 ×5（task_assign/create/set_status/list/nudge）；**排除** task_claim/task_report |
| 队长（per-child） | **仅含** task_claim/task_report + 父预设干活工具（bash/fs/skills/轻度 subagent）；**排除**全部管理工具 |

toolFilter 白/黑名单语义以「## M0 结论」引用源码为准；表达不了就上报重议，不得放宽服务端身份校验。

受影响任务：t6 收窄为「仅铸造管理模式预设 + 验证」；t7 预设验收相应调整为单预设 + 7 工具行。

## 经验教训（复盘，2026-09-10）

> **2026-09-13 追注**：这份复盘的背景是当时的「主检出 + dev worktree」双检出工作流。该工作流已于 2026-09-13 下线——dev 分支（本地与 fork 远端）、`dev/` worktree、3081 dev 实例与 `dsh-web-dev.service` 一并移除，DSH 仓库现为单检出 `deepseek-harness/`（同日由 `master/` 改名，分支仍叫 `master`），生产实例就跑在它上面。因此下面第 1、3、4 条关于「开发位置」的纪律**不再适用**，仅作历史记录保留（它们记录的教训本身——「位置必须显式确认、描述与实况不符即停」——仍然成立，只是对象从「哪个 worktree」变成「改 `deepseek-harness/` 即改生产」）。第 2、5、6 条与位置无关，继续有效。

1. **开发位置是门禁级需求**：多仓库 + worktree 工作流的工作区，功能开发必须在 dev worktree/分支进行；「代码落在哪」应进 grill-with-docs 拷问清单与任务契约（提交位置/分支策略字段）。
2. **描述与观察不符即停**：用户话语中的环境信号（如「修改都在 dev worktree」）与工作树实况冲突时，停下对齐，不得沿用假设。
3. **队长侧同纪律**：队长亲自补文件（如根 package.json）同样受开发位置纪律约束。
4. **闸门只验产物不验位置**：inScope/验收闸门拦不住「提交到错误的分支」——位置纪律只能靠契约条款 + 队长巡检。
5. **「作用域可见」不等于「预设行生效」**：上层作用域的注册会被下层继承，`tools.get(name, presetScope)` 为 true 只能证明名字可见，不能证明来源。要判归属必须用**无主作用域**对照（一个任何预设都不拥有的 scope key）或直接读真实会话首个 `request/header` 的工具表。本次首轮 t18 验收就被这条假阳过。
6. **bundle 侧与预设侧双注册是静默缺陷**：host bundle 注册落在 tools 注册表全局层，任何预设的会话都继承——文档（ADR-0004）禁止、代码却保留，一条 `pnpm test` 也拦不住。修完必须用「预设 A 会话 vs 预设 B 会话」的对照实证，而不是只看 mount 是否通过。

## 遗留事项

- GUI 人工复验：新建 / 详情 / 类别筛选 / 需终审勾选 / 管理模式真会话派发演示。

> **原「收官记录」节已于 2026-09-13 精简删除。** 该节记录的是 2026-09-10 当时的状态快照——
> 交付状态（提交号 `c2bcd47`、测试 47/47、部署链）、活进程实证（105/98 工具计数、
> `standingKeyFor` 结果、路由返回），以及缺陷修复叙述。这些都能从 git 历史、测试与运行中的
> profile 直接查得，留着只会随现实漂移；缺陷本身与其修复由 ADR-0004 与「经验教训」第 6 条承载。
> 同节另有三条已无对象：`dev/task-manager-orchestration` 合并（分支与 worktree 已删）、
> AgentTeams 团队 `manager-task-orchestration` 清理（`.agent-teams/` 已不存在）、
> `dsh-continual-evolve` 基线日志（该插件已删除）。

## v1 明确不做

优先级/依赖字段；事件推送唤醒；其他会话投递任务；队长空闲归档；多 Manager 并存；Web 移动端适配。

## M0 结论（2026-09-09，scout 只读侦察）

以下路径均相对 `deepseek-harness/` 仓；行号为当日 checkout 实况。

### 结论 1：建队长会话的调用面（startContinuable）

调用链：`packages/experimental/agent-team/src/roster.ts:244-335 spawnAdmitted` → `packages/subagent/subagent/src/index.ts:212 startContinuable(spec)` → `packages/subagent/subagent/src/continuation.ts:409`（continuation manager 组装子 agent 并投递首条 prompt）。

roster 实际调用（roster.ts:280-289）：

```ts
started = await this.ctx.subagents.startContinuable({
  childId,                    // 预留 durable 子会话 id（roster 用 randomUUID，先落 team/member 快照）
  provider: request.provider, // 'spawn'(fresh) | 'fork'(带父前缀 seed)
  label: description,         // 持久化创建标签（GUI 显示用）
  request: {
    prompt: request.prompt,   // ContentBlock[] 首条消息（=成员任务简报）
    parent: root,             // 队长（Lead）Agent；workspace/谱系/深度由其会话状态派生
  },
  signal,                     // 取消权仅管辖到「inbox 接受」为止
})
// 返回 { childId, messageId }：子 agent inbox 接受首条 prompt 即 resolve，
// 不等轮次开始（subagent/README.md:19）；roster 再 checkpointInitialPrompt
// （roster.ts:338-386）等 sessions.flush 后以 messageAccepted 验收（session-message.ts:25-31）
```

完整参数清单（`ContinuableStartSpec`，continuation.ts:112-130；request 体 = `Omit<SubagentStartRequest,'label'|'signal'|'outputSchema'>`，subagent/src/types.ts:100-149）：

| 参数 | 语义 | M0 裁定 |
|---|---|---|
| `provider` | 必需。须具备 `prepareContinuable` 能力的子 agent 后端名（方法在即能力，types.ts:315-330） | 用 `'spawn'` |
| `label` | 必需。持久化为子会话创建标签 | `队长·<类别>` |
| `childId?` | 可选。缺省管理器自配 UUID；提供则沿用调用方预留 id | 建议提供（captains.json 可先落注册表再建会话） |
| `request.prompt` | 必需 ContentBlock[]，首条消息 | 章程+任务简报 |
| `request.parent` | 必需 Agent。in-process 后端从其 durable 会话状态派生 workspace/谱系/深度；ACP 仅在无部署覆盖时读其 cwd（types.ts:105-110） | Manager 的 Agent |
| `request.agentOptions?` | `{ provider?, model?, maxTokens? }`（core/agent/src/runtime-types.ts:24-31），覆盖继承的父路由 | 模型在此定，**无预设字段** |
| `request.maxDepth? / toolFilter? / persona?` | 深度帽 / 工具收窄（`tools.restrict`，只能减不能加）/ 子级 persona（`deployment:persona` 段，遮蔽部署与预设 persona；continuation.ts:428-429、464 传递，1065 经 `applyChildComposition` 应用，冷恢复时从 descriptor 重放 ：985，descriptor.ts:79-82） | **章程注入通道**（见结论 3 修正） |
| `signal` | 取消信号，管辖至 inbox 接受 | — |

**关键否定性事实**：①无 `preset` 参数——continuable 子会话**继承父会话的预设**（`applyChildComposition` 无条件 `composeFrom(childCtx, parent.ctx)`，subagent/src/child-agent.ts:163-175；「this is how a child agent inherits its parent's capabilities」agent-presets/src/index.ts:290-324），且子会话 header 持久化该预设 id（childSessionMeta，child-agent.ts:102-120）；②无 `cwd` 参数——子会话 cwd 复制父 header.cwd（child-agent.ts:110），「cwd=任务目录」需另行裁定；③fork 的 seed=父已完成轮次前缀（ContinuableCreateSpec.seed，types.ts:185-192）。

「建会话一行代码」可复述形式（本插件 host 平面）：

```ts
const { childId, messageId } = await ctx.subagents.startContinuable({
  provider: 'spawn', label: `队长·${category}`,
  request: { prompt: [{ type: 'text', text: charterBrief }], parent: managerAgent },
  signal,
})
```

### 结论 2：向既有会话投递消息的原语（mailbox dispatchOnce 路径）

权威路径：`packages/experimental/agent-team/src/mailbox.ts`。`sendAdmitted`（:109-152）先在 Lead 日志事务内排队（`team/message/queued` 事件、满箱/字节上限校验），随后 `dispatchOnce`（:227-271）一次性投递：

1. **帧构造**：`source = { kind:'team-message', teamId, messageId, senderId, senderName }`（:233-239；MessageSourceMap 经 module augmentation 声明，agent-team/src/types.ts:109-122）；`deliveryContent`（:315-320）在内容前加文本块 `` `Team message ${id} from ${senderName}:` ``。
2. **追加 user/message + 唤醒**（消息经 `createUserMessage({ content, source })` 构造，mailbox.ts:6）：
   - 目标 = Lead 本人：`delivery==='wakeup'` → `root.followup(input)`（排队为下一普通轮次并唤醒驱动，runtime-types.ts:119-124）；否则 `root.inject(input)`（入下一 pre-step 批，**不唤醒**，runtime-types.ts:136-143）。
   - 目标 = 成员且 live：quiet → `target.inject(...)`（:250-254）；wakeup 且不 live → **冷恢复投递** `await this.ctx.subagents.followup(root, message.targetId, content, { source, signal })`（:263），由 subagent 服务从持久化会话恢复并作为下一 FIFO 轮次投递（subagent/README.md:20）。
3. **验收与回执**：`checkpointDelivered`（:279-289）= `ctx.sessions.flush(target)` → `targetRecorded`（`messageAccepted` 扫 `user/message` 历史 + `agent/inbox/spliced` 投影，session-message.ts:25-31）→ Lead 日志 `team/message/delivered`（:292-305）。

我们插件在 host 平面的最小调用序列：

```ts
import { createUserMessage } from '@deepseek-ai/dsh-llm'
const source = { kind: 'team-message', teamId, messageId, senderId, senderName } // 或自定义 MessageSourceMap kind
const input = createUserMessage({ content: [framing, ...content], source })
const target = ctx.agents.get(targetSessionId)          // live 会话
if (target !== undefined) { (wakeup ? target.followup(input) : target.inject(input)) }
else { await ctx.subagents.followup(managerAgent, targetSessionId, content, { source, signal }) } // 冷恢复
// 回执（可选）：ctx.sessions.flush + messageAccepted 验收后写己方状态
```

**边界**：`ctx.subagents.followup(parent, …)` 要求 parent 是**确切 live 的直接父级**（subagent/README.md:149「No host-user continuation」）——队长会话的直接父是 Manager 会话；v1 巡检制下 Manager 先被唤醒再派发，天然满足「父 live」。对 live 会话直接 `Agent.followup/inject` 无父子要求。

### 结论 3：装载通道裁定——**可引用**（无需 curl fallback，不触发 ADR-0003）

证据链：

1. **预设行的裸包名从哪解析**：`PresetTree.import`（agent-presets/src/mount.ts:63-92）——相对路径按预设目录解析（「a preset's own files travel with it」）、绝对路径转 file URL（:82）、**裸包名按 `harnessBase`（ mounting 时 agentCtx.baseUrl，:340-345）解析**，即根 Loader 锚定的 profile 目录（apps/cli/src/profile-boot.ts:91-93、227：根配置 = `~/.dsh/profiles/web/cordis.yml`）。
2. **Node 逐级向上查找命中两级**：`~/.dsh/profiles/web/node_modules/`（profile 自身 dependencies：`dsh-task-manager` → link `~/MyAI/dsh-extensions/plugins/dsh-task-manager`、`@nanmicoder/dsh-agent-teams` 等，package.json + symlink 实测）→ `~/.dsh/profiles/node_modules/`（`healProfilesModuleFallback` 维护的安装闭包平铺链接，253 个，含全部 `@deepseek-ai/dsh-*`；packages/boot/app-boot/src/profile.ts:204-255）。omni 预设全部行即按此解析运作。
3. **旁证（dsh-agent-teams 挂载方式）**：它是 **host 平面 bundle**（声明 `"dsh":{ "bundle":{ "patch":"./cordis.patch.yml" } }`，经 profile package.json `dsh.profile.bundles` 装载；其 cordis.patch.yml 自述「把 `agent_teams_*` 工具注册进共享 tools 注册表 + 全局 system prompt 使用说明段」）——因此其工具对所有会话可见，与预设无关。dsh-task-manager 同为 bundle（node 半空入口 + 浏览器 client 半）。
4. **纪律**（skills/editing-cordis-compositions/SKILL.md）：预设里**提供**服务的行必须置于 `isolate` realm（:79-104；mount 审计拒绝 root-realm 泄漏，mount.ts:361-367）；只**消费** host 注册表的工具行照 `tool-todo` 模式平铺即可（omni 同款）；`standingKeyFor(id)` 是装载验证标准（:108-115，`Cannot find package …` 即裸名解析失败的第一报错）。

**裁定：可引用。** 条件与注意：①被引用的 dsh-extensions 包必须已装入 web profile 依赖（`dsh plugin --profile web add`，dsh-task-manager 已装 ✅；未装包的裸名行会在 standingKeyFor 报 Cannot find package）；②新回报工具行（task_claim/task_report）作为**注册进 host tools 注册表的消费者插件**可被预设行按裸包名引用，与 tool-todo 同构；③不得把 taskManager 服务/provider 类行塞进预设（跨会话服务必须留 host 平面）。

**附带修正（R2 相关新发现，需队长在 M1/M3 决策）**：startContinuable 子会话**装载不了独立预设**（继承父预设，无 preset 参数）。「队长模式」差异化在 M0 证据下有三条可落地路径：
- **A（推荐起点）**：队长仍为 Manager 的 continuable 子会话，继承管理模式预设；差异化用**创建期 per-child 参数**承载——`persona`=队长章程+纪律（遮蔽父预设 persona，durable 于 descriptor、冷恢复重放），`toolFilter` 收窄工具面；task_claim/task_report 工具行挂管理模式预设或 host 平面（服务端已有 `exec.agent` 身份校验兜底）。M3 的「队长模式预设」退化为「预设内 persona 分层 + 身份校验」，或仅作 GUI 展示差异。
- **B**：创建后立刻 `agentPresets.recompose(agentCtx,'captain')`（agent-presets/src/index.ts:458-472）换绑预设——合同要求「agent 未产出任何内容」（caller owns that check），startContinuable resolve（inbox 接受）与首个 turn 开跑之间窗口极窄，风险路径。
- **C**：队长改走顶层会话（sessions 服务创建+预设选择=队长模式）——预设/裁剪/章程全按计划成立，但失去 subagent 父子关系与冷恢复投递通道，唤醒需另建（改动最大）。
