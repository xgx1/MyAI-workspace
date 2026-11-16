# Super-agent 使用教程

Super-agent 是 DeepSeek《Super-agent 设计探索》那套架构的落地实现（第三方 fork），
把「收消息 → 判断要不要干 → 派工单 → 干活 → 交付 → 只在该打扰人时打扰」拆成 Router / Worker 两层。
本文只讲**本机这份怎么用**。

## 0. 现状速查

| 项 | 值 |
|---|---|
| 跑在哪 | dev 实例 :3081（`dsh-web-dev.service`，与你的日常 dev 会话同进程） |
| 代码 | `deepseek-harness-dev/extensions/dsh-super-agent`（dev 分支的子模块，fork: `xgx1/dsh-super-agent`） |
| 插件名 | `dsh-super-agent`，配置在 `~/.dsh-dev/profiles/web/cordis.patch.toml` |
| 状态目录 | `~/.dsh-dev/storages/super-agent`（工单库、工作树、回执） |
| 当前模式 | `observe` —— 只记录准入结果，**不真的执行** |
| 交付模式 | `patch` —— 只产 patch 与 PR 草稿，不 push、不开 PR |

打开控制台（token 每次重启会变）：

```bash
journalctl --user -u dsh-web-dev -n 100 --no-pager | grep -o 'http://127.0.0.1:3081/?token=[^ ]*' | tail -1
```

浏览器打开那条 URL，左侧栏 **Super Agent** 图标就是控制台：架构拓扑、准入漏斗、Worker 泳道、
看门狗健康环、注意力预算、p50/p95、事件流、控制条（切模式 / 暂停 / 立即巡检 / 重放实验 / 清理侧栏）。

## 1. 三个入口，按省事程度排

### a. 在会话里让 agent 调 `superagent` 工具（最省事）

在 3081 的任意会话里说「用 superagent 看一下状态」，agent 会调：

| action | 干什么 |
|---|---|
| `status` | 总览：模式、队列、Worker、看门狗 |
| `trigger` | 注入一条环境事件，走完整两级准入（`text`、`source`） |
| `dispatch` | **直接派真实工单**（`repo`、`text`、`title`） |
| `mode` | 切 `observe`/`accept`、暂停 Router（`accept`、`paused`） |
| `watchdog` | 立即巡检一次 |
| `demo` | 重放论文实验负载（不碰真仓库） |
| `metrics` | 只读指标 |
| `config` | 热改配置（`config` 对象，见第 6 节） |
| `cleanup` | 归档本插件产生的 `sa-` 会话、删掉它的工作区分组 |
| `reset` | 清空记录 |

### b. 控制台上的按钮

切模式、暂停、立即巡检、重放实验、清理侧栏都在控制条上，和上面同名的 action 等价。

### c. HTTP（写脚本/接外部系统）

```bash
# 取 cookie（先访问一次带 token 的首页）
curl -s -c /tmp/sa.cookies "http://127.0.0.1:3081/?token=<TOKEN>" -o /dev/null
curl -s -b /tmp/sa.cookies http://127.0.0.1:3081/api/super-agent/health
curl -s -b /tmp/sa.cookies http://127.0.0.1:3081/api/super-agent/state
curl -s -b /tmp/sa.cookies -X POST http://127.0.0.1:3081/api/super-agent/command \
  -H 'content-type: application/json' -d '{"command":"demo"}'
```

可用 command：`demo` / `cleanup` / `config`（`{"command":"config","config":{…}}`）。
另有 `POST /api/super-agent/hook` 收外部 webhook（`x-github-event` 头存在就按 GitHub 解析，否则按 CI 失败解析）。

## 2. 五分钟第一次跑（不需要任何 GitHub 账号）

inbox 源是零凭据的 Trigger：往一个目录丢 JSON 文件就是一条候选事件。

1. 打开 inbox 源（热改，不用重启）：

   ```
   用 superagent 工具，action=config，
   config={"sources":{"inbox":{"enabled":true,"dir":"/home/sx/.dsh-dev/storages/super-agent/inbox"}}}
   ```

   或者直接把这段写进 `~/.dsh-dev/profiles/web/cordis.patch.toml` 的
   `[entry.config.sources.inbox]`（`enabled = true`、`dir = "…"`）后重启 3081。

2. 丢一条事件（`text` 必填，可选 `author` / `threadId` / `repo`）：

   ```bash
   mkdir -p ~/.dsh-dev/storages/super-agent/inbox
   cat > ~/.dsh-dev/storages/super-agent/inbox/t1.json <<'JSON'
   { "text": "登录页在 375px 宽度下按钮被遮挡，麻烦看一下", "author": "me", "threadId": "local-1" }
   JSON
   ```

3. 看结果：控制台的准入漏斗会依次出现「原始事件 → 规则快筛 → 语义判定 → 已派单」；
   文件会被标记（处理失败的会写明原因，不会被静默吞掉）。
   `observe` 模式停在「已派单」之前——这是安全默认值，不是坏了。

4. 想真执行，见第 4 节，然后**同样这条事件**再丢一次，Worker 会在
   `<stateDir>/worktrees/` 下的独立工作树里干活，产出：
   - `<ticket>.patch`（及二进制补丁）、`<ticket>.pr.md` 草稿
   - 回执写回来源（inbox 的 `outbox/`）

## 3. 直接派活（不用 Trigger）

```
superagent action=dispatch repo=/home/sx/projects/MyAI/deepseek-harness-dev/extensions/dsh-super-agent \
  text="给 README 的安装小节补一段 Linux 上的依赖说明" title="docs: linux deps"
```

`repo` 给本地 git 路径，或 `repoMap` 里的符号键；Worker 在该仓库的独立 worktree（分支 `sa/<ticket>`）里改，
主仓库保持干净。

## 4. 切 accept 之前必须做的三件事

`accept` 才是「自己接活干」。切之前：

1. `acceptSources` 收窄到可信来源（`[]` 等于放行全部）。
2. `budget` 三个上限都设上：`maxWorkersPerHour`、`maxRuntimeMs`、`maxTokensPerDay`。
3. 只在**可信仓库**上开：Worker 会话按 `danger-full-access` 跑，且和你的日常 dev 会话同进程，
   会继承 3081 上的 ego 浏览器（你的真实登录态）、cbm/ue/unity MCP、openviking 记忆。

切法：`superagent action=mode accept=accept`；后悔就 `accept=observe`。

## 5. 交付模式三档

| mode | 产物 | 前提 |
|---|---|---|
| `patch`（当前） | 工作树里提交 + patch + PR 草稿 | 无 |
| `push` | 再把分支推到 `delivery.remote` | 远端写权限 |
| `pr` | 推完直接开 GitHub PR | `delivery.githubToken` |

token 别写进 git 跟踪的文件（`profiles/web/cordis.patch.toml` 是入库的）：用运行时
`superagent action=config` 设，或另开一份不进库的 patch 层。

## 6. 配置在哪、什么时候生效

- 文件层：`~/.dsh-dev/profiles/web/cordis.patch.toml` 里的 `[[entry]] id = "dsh-super-agent"`（入库，改完要重启 3081）。
- 运行时：`superagent action=config config={…}`（合并进当前配置并持久化，部分项热生效）。
- 重要陷阱：插件 `apply()` 对内置默认值只做**浅合并**，配置里不写的键会掉回插件默认值
  （例如 `budget.maxWorkersPerHour` 默认 `0` = 无上限），所以配置层里把整段写全，别只写想改的那一项。

## 7. 维护

同步上游（aowind 是真源；DeepSeek 官方原型只当参考资料，不 merge）：

```bash
bash ~/.dsh-dev/sync-super-agent.sh   # fetch → 合上游 → 推 fork → 顶 dev 指针 → 重启 3081
```

日志：`journalctl --user -u dsh-web-dev -f`；启动诊断文件在 `~/.dsh-dev/logs/startup-*.log`。

## 8. 排障

| 症状 | 原因 / 处理 |
|---|---|
| 侧栏没有 Super Agent | bundle 没进 `dsh.profile.bundles`，或 `pnpm install` 没做；重启 3081 |
| 丢了事件但没执行 | 正常：`observe` 只记录。切 `accept` 或看漏斗停在哪一级 |
| `invalid config: $.stateDir expect string to match regexp /^\//` | `stateDir` 必须是**绝对 POSIX 路径**；Windows 风格路径（`C:\\…`）或相对路径会被拒（本机 2026-11-11 那次就是这么失败的） |
| 打开页面 401 | token 每次重启都换，用第 0 节那条命令重新取 |
| Worker 起不来 | 看 `status` 里的 `presetError`：Worker 用 `standard` 预设做嵌套 subagent，预设缺失会在那里写明 |
| 侧栏堆满会话 | `superagent action=cleanup`（只动 `sa-` 前缀会话与它自己的工作区分组） |

## 9. 扩展点

- **加一个 Trigger 源**：`lib/sources/` 下照现有 `local-inbox.mjs` / `github.mjs` 写一个模块，
  插件侧在 `index.js` 的 `startSources` 处挂上。这是最小改动路径，不用碰 Router/Worker。
- **改调度/授权语义**：`lib/engine.js` 是策略层（准入、线程订阅、看门狗、注意力闸门都在里面）。
- 注意：这个目录是**子模块**，改动在子模块里提交、推 `origin`（你的 fork）；再跑
  `sync-super-agent.sh` 会先合上游，冲突就地解决——别在 dev 检出里改它的文件而不进子模块。
