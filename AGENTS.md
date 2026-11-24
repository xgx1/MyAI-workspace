# AGENTS.md — MyAI 工作区本地约定

提交/推送与 submodule 纪律、浏览器、后台窗口与桌面相关规则见用户级 `~/.dsh/AGENTS.md`。本文件只放**这个工作区特有**的路径与仓库事实。

## 仓库布局

- **`deepseek-harness/`** —— **生产检出**（分支 `master`）。**生产实例（3080）就跑在它上**（`~/.local/bin/dsh` → 该检出的 `apps/cli/lib/bin.js`，由 `dsh-web.service` 托管）——改它就是改生产，**默认只读**（见下节「DSH 改动落点」）。
- **`deepseek-harness-dev/`** —— **DSH 功能开发的唯一落点**：`deepseek-harness/` 的 git worktree（分支 `dev`，与生产检出共用同一 `.git`，目录同层级）。开发实例跑在它上面：
  - `dsh-web-dev.service` → **http://127.0.0.1:3081**，`DSH_HOME=~/.dsh-dev`（sessions/storages 与生产隔离）；启动脚本 `~/.dsh-dev/dsh-web-dev-launch.sh`，unit 权威副本 `~/.dsh/deploy/systemd-user/dsh-web-dev.service`。
  - composition 副本在 `~/.dsh-dev/profiles/web/`：**要调开发实例的组成就改这份**，别改生产的 `~/.dsh/profiles/web/`。
  - 开发循环：worktree 里改代码 → `pnpm run build` → `systemctl --user restart dsh-web-dev.service` → 刷新 3081。
  - **`~/.dsh-dev` 是 `~/.dsh`（dsh-home 仓）的 git worktree**（orphan 分支 `dev`，2026-11-02 起，已推 origin）：只跟踪开发实例配置层——`profiles/web/*`、`profiles/headless/*`、home 级 `cordis.patch.yml`、`dsh-web-dev-launch.sh`；`sessions/`、`storages/`、`.credentials.yaml`、`node_modules/` 与三个指向生产的软链（`.agent-presets`、`AGENTS.md`、`skills`）由 worktree 里的 `.gitignore` 排除。composition 是**不自动跟随生产的快照**，要同步时整份照搬生产再改 link（2026-11-02 起 dev **不再保留 dev-only 条目**——session-manager/preset-management/web-search-exa/tool-ralph/headless extras 已由用户拍板有意移除，后来者不要「恢复」；**例外**：experimental provider `@deepseek-ai/dsh-experimental-computer-use-cua-driver-native`（playwright-mcp 已于 2026-11-14 按用户要求彻底移除）——2026-11-02 晚由用户拍板**声明进 dev 的 `profiles/web/package.json`**（ops 预设按会话挂载它们，未声明时靠 node_modules 遗留软链解析，`pnpm prune`/重装即失效），此条为例外、不在「不要恢复」之列。
  - **该 provider 在 profile 级的条目保持 `disabled: true` 是刻意设计**（2026-11-02 用户拍板）：`~/.dsh/type-presets.yaml` 的 `disable_host` 生成宿主层禁用、只由 ops 预设按会话挂载，避免所有会话都吃 Chromium/CUA 启动成本；宿主层启用会与预设的挂载形成同插件双实例、工具注册可能冲突。后来者不要「恢复」宿主层启用，也不要在没搞清这条前删 `disable_host` 行。
  - 同步 recipe：`profiles/web|headless` 的 `cordis.yml`/`cordis.patch.yml`/`package.json`/`pnpm-lock.yaml`、home 级 `cordis.patch.yml` 全部 `cp` 过去，**`package.json` 里 `@deepseek-ai/*` 的 `link:` 路径改回 `deepseek-harness-dev/`**（dev home 没有 `~/.dsh/profiles/node_modules` 共享层，root patch 的 hooks 条目只能走 profile 声明解析，2026-11-02 实况），然后 `pnpm install --registry=https://registry.npmmirror.com --prefer-offline` → `systemctl --user restart dsh-web-dev.service` → 在 `~/.dsh-dev` 里 `git commit` 落 dev 分支。
  - 依赖装不上时先看 registry：本机 `registry.npmjs.org` 不通，用 `pnpm install --registry=https://registry.npmmirror.com --prefer-offline`。
  - **配置层两个 home 必须一起提交、双向同步**（2026-11-15 用户指示）：`~/.dsh`（main）与 `~/.dsh-dev`（dev）是同一仓库的两个 worktree，orphan 分支没有共同祖先、git 无法 merge——同步靠搬文件：两边各自 commit + push，然后按上一条 recipe 把生产配置层搬到 dev（含 `link:` 路径改回 `-dev/`）、各自 profile 里 `pnpm install`、重启 3081 验证。**更新 MyAI（update-all / 拉取代码）时把这一步算进去**；落后判断：orphan 分支没有共同祖先、`rev-list` 计数无意义，直接比内容 `git -C ~/.dsh diff --stat main dev -- profiles/ cordis.patch.yml`（差异应只剩 `link:` 的 `-dev/` 行与 dev 独有的 `dsh-web-dev-launch.sh`）。完整四步见用户级 `~/.dsh/AGENTS.md`「修改位置」节。
- **`dsh-extensions/`** —— 单检出（分支 `main`）：`plugins/`（自研，受本仓版本控制）与 `skills/` 是生产 `link:` 的目标。
- **`dsh-extensions/vendor/` 与 `dsh-extensions/skills/` 都是 git submodule**（2026-11-01 实测 `git submodule status`：vendor 6 个、skills 14 个，共 20 个；clawic-marketplace 与 caveman 两组已于 2026-10-26 删除，vendor/dsh-genui 于 2026-11-01 移除）：
  - `vendor/` = 第三方插件源码，均为生产 `link:` 目标（权威是 `~/.dsh/profiles/*/package.json`）。`billion-context` 是 `xgx1` fork（origin=fork、upstream=上游 ranxianglei/billion-context）；`OpenViking`（xgx1 fork）供 `@openviking/dsh-memory-plugin`，dev 与生产 profile 都已 `link:`。**`dsh-ops` 已于 2026-11-10 按用户要求彻底卸载**（依赖、bundle 行、`cordis.patch.yml` 行、pnpm-lock 与 1.3G 本地 checkout 全删，子模块同步从 `.gitmodules` 移除）；fork `xgx1/dsh-ops` 仍在 GitHub（upstream T-Auto/dsh-ops，`LOCAL-PATCHES.md` 记着 Linux 移植改动），要回来的话 `git clone` 后重新加子模块与 profile 行。
  - `skills/` = 技能分组仓，一个上游仓库一组。组树 = 上游树 + 本地改动移植。详见 `docs/adr/0006`。
  - 改它们要在**各自目录里**提交、推送，再回 `dsh-extensions` 更新指针；本仓只保存指针。两者都不被 `.gitignore` 忽略（见 `docs/adr/0005`）。
- **`dsh-Go/`** —— submodule（`xgx1/dsh-Go`，上游 `ccch1mneyyy/dsh-Go` 未配 remote）：Android 客户端 App（Flutter 原生界面 + 纯 Dart 客户端 + PRoot 里打补丁的 DSH 引擎），2026-11-17 按用户要求并入本工作区。钉在 `local-main` 分支（快照提交 `267ddf6d`；fork 的 `main` 比它旧，别在那儿找）。**在那个目录里做事先读它自己的 `AGENTS.md`**：不接受外部 PR、不 commit/push 除非当次要求、手机操控/PRoot/更新安装类改动必须真机验证。与 `deepseek-harness` 没有共享历史、互不依赖。
- 位置纪律与动手前确认流程见用户级 `~/.dsh/AGENTS.md`「修改位置」节；本工作区先例复盘：`docs/plans/manager-task-orchestration.md`「经验教训」节。

## DSH 改动落点（默认只改 worktree）

**除非你在当次需求里主动说明，DSH 的任何代码 / 配置改动只做在 `deepseek-harness-dev/` 里；`deepseek-harness/` 是生产检出，除只读操作外不许动。**（2026-09-26 用户指示）

- 「主动说明」= **当次对话**里点名要改生产检出（例如「这次直接改 `deepseek-harness` 并重启 3080」）。此前对话说过、别处文档写过、任务看起来「顺便也要」——都不算。
- 生产检出上**禁止**：编辑任何文件、`git add/commit/checkout/branch/worktree`、`pnpm install`、任何写产物的构建（`pnpm run build`、`build:lib:*`、`build:web`……）、改 `~/.dsh/profiles/` 下的生产 composition。
- 生产检出上**允许**（只读）：读代码与文档、`git log|status|diff|show`、`systemctl --user status dsh-web.service`、查端口与日志。
- 验证开发改动一律走 dev 实例 3081；**不要**拿 3080 当试验台，也不要用重启 `dsh-web.service` 的方式看效果（会中断当前对话）。
- 真正会影响生产的动作（重启 `dsh-web.service`、改 `~/.dsh` 的生产 composition 或 unit、动 `dsh-extensions` 里被生产 `link:` 的目录）**先问用户**。

## DSH home 仓库（`~/.dsh` = `xgx1/dsh-home`）

`~/.dsh` **本身就是 git 仓库**（公开：<https://github.com/xgx1/dsh-home>），只跟踪配置层。
**不要另建一份 `.dsh`**：新设备、新工作区、别的 agent 一律 clone 这份仓库（或把 `DSH_HOME` 指向
clone 出来的目录）；手工拷配置、自己建空 home、拿别的目录当 home 都会与主库漂移，合并时丢凭据引用与
session 布局。`<项目根>/.dsh/` 只放项目专用技能，**不是** home。

分支约定（完整命令见 `~/.dsh/README.md`「多机：分支约定」）：

1. **强制更新 / 跨机同步一律 Linux → Windows**：先 `git checkout main && git pull`，再
   `git checkout windows && git merge main`。Linux（Arch）是 `main` 的唯一推进方。
2. **Windows 侧改动必须回流 `main`**：windows 分支提交并推送后，
   `git checkout main && git merge --no-ff windows && git push`。只有「换平台就该不一样」的
   （PowerShell 启动器、`link:` 绝对路径、lock、按平台切换的工具行）才留在 `windows`；
   跨平台解析、hook 分发器、文档修正这类通用改动直接进 `main`，否则下次合并会当冲突。

## 本地 Laya 决策模型（dev 侧，2026-09-27 接入）

## DSH 开发红线

以下几条都是崩过生产换来的，别删、别绕：

- **不许删 `packages/llm/llm/src/index.ts` 里的 `assertNever` 兼容导出**（L54-57，注释写明了保留条件）：外部 turtle-ui TUI 还在从这个包 import；删掉再重建，`dsh tui` 的 import 必挂。等 turtle-ui 迁完再删。
- **新增插件包必须走完五件套**，漏一步 preset 就起不来：① 包内 `tsconfig.json`（extends 根 `tsconfig.base.json`、`rootDir: src`、`outDir: lib/types`、references 声明依赖）→ ② 根 `tsconfig.host.json` 的 `references` 加引用 → ③ `pnpm run gen-tsconfig-paths` 重生成包别名 → ④ `apps/cli/package.json` 加依赖 + `pnpm install` → ⑤ 全量 `pnpm run build:lib:host` 通过且该包测试通过。**preset 引用了未构建好的包 = 所有用该 preset 的新会话起不来**，而 `omni` 是默认 preset。
- **包装 provider 时，候选技能上的 `provider` 必须等于外层注册名**：别让内层 provider 顶着旧名字返回数据——名字不匹配会解析到错误的 provider。
- **更新 CBM（`codebase-memory-mcp`）二进制后必须重启 `codebase-memory.service`**，否则常驻 daemon 握着旧 inode，全线 MCP 请求超时。该 unit 是**用户级**：`systemctl --user restart codebase-memory.service`。
- **改完 `profiles/` 后，先确认能加载，再重启 `dsh-web.service`**：顺序反了就是先断了当前对话、再发现 preset 加载不了。（`~/.dsh/.agent-presets/` 自 2026-11-13 起不再被加载，改它无效——预设只有 `profiles/web/cordis.patch.yml` 里的 `preset-all` 一个。）

## 技能

- 运行时技能目录 `~/.dsh/skills/` 里**受管技能全是软链，不是副本**；**不要手工往里面复制技能**——副本会与仓库漂移。
- 技能按上游仓库分组：`<技能源仓>/skills/<上游仓库名>/`。**组内目录与上游一一对应**——组树 = 上游树 + 本地改动移植到对应文件，上游各层级（`skills/<名>/`、`.agents/skills/<名>/`、`plugins/<插件>/skills/<名>/`）原样保留，**不拍平到组根**；分组 README 叫 `README.dsh-local.md`。本地改名只写在 frontmatter 的 `name:` 上，所以技能名不随上游目录名变。
- **项目专用技能不放主库**：落在各项目自己的 `<项目根>/.dsh/skills/`。
- **命令的平台约定**：技能里的命令按平台分节——Linux（本机 Arch）用 `bash`、Windows 用 `PowerShell`，代码块语言标记即平台归属，两者不混写在同一段里。只给 PowerShell 的方案一律补 bash 等价（补不了就写明「Linux 上无对应方案＋原因＋可替代做法」，不许编造跑不通的命令）；只有 bash 的方案不必再写 PowerShell 版本。

## 模型目录

- 所有模型（任何项目/工具加载的）一律存放在 `~/.model/<工具或项目名>/`；工具或项目原本的位置只留软链接指回 `~/.model`，实体不入库、不重复拷贝；同一模型的不同量化/版本只保留实际在用的一份（以运行进程、`/proc/<pid>/cwd` 与配置里的引用为准，不靠猜）。
- 例外（迁不动）：zvec-grep 嵌入模型在 `~/.zvec-grep/models/`；fcitx vinput 的 sherpa-onnx ASR 在 `~/.local/share/vinput/models/`。
- 本机当前没有本地大模型（2026-10-15 弃用并清空配置）。要重用得先重下权重按上面约定落 `~/.model/`，再往 profile 的 `llm-pi-ai` provider 表加条目。

## 技能部署

- `dsh-extensions/install-skill.sh` 是安装/更新的唯一入口：递归扫描 `dsh-extensions/skills/`、`~/projects/update-app/skills/`、**任意深度项目下的** `<项目>/.dsh/skills/` 三源，把技能目录软链到 `~/.dsh/skills/`。覆盖真实目录需 `--force`（先备份到 `~/.dsh/skill-backups/`），`--dry-run` 预演。
- 源①的跳过规则：跳过 `tests/`/`fixtures/`/`examples/`/`sample*` 噪音并打印跳过清单；同名副本取路径最浅者，故 `skills/`、`.agents/skills/` 优先于分发副本。技能目录 = 含 `SKILL.md` 的目录，**不限深度**。
- 源③ 2026-10-12 起也是递归 `find`（旧版单层 `~/projects/*/.dsh/skills/` glob 会漏 `ps-tool/anim/.dsh/skills/` 这类嵌套项目，四个 anime 技能曾长期靠手工软链），并排除 `*/snapshots/*`（DSH 快照夹具里放的是测试用假技能）。
- 自检：`--dry-run` 输出里「新建 N」应为 0，否则有技能没被纳入受管源。装好重启会话，**模型立刻看得见全部技能**——2026-11-24 起已停掉按项目白名单治理（`agent-configs` / `ui-agent-config` 在 `profiles/web/cordis.patch.toml` 里 `disabled = true`，个人层 `skill-filter.yaml` 全禁层已移走），别再往 `~/.dsh/agent-configs.yaml` 加东西。

## 本工作区

- **不设暂存区**：技能指向的项目不存在了就删（正文在 git 历史里），不攒 `old/` 这类抽屉——`old/` 已于 2026-11-17 清空删除，5 个技能正文见 `git log --before=2026-11-17 -- old/`。
- `update-app`（CLI + `update-all` 技能）独立仓库位于 `~/projects/update-app`。

## Agent 技能

### 问题跟踪（Issue tracker）

问题以本地 Markdown 文件落在本工作区的 `.scratch/<feature>/` 下（无远端跟踪器）。见 `docs/agents/issue-tracker.md`。

### 分诊标签（Triage labels）

五个规范分诊角色：`triage`、`info-needed`、`agent-ready`、`human-ready`、`wontfix`。见 `docs/agents/triage-labels.md`。

### 领域文档（Domain docs）

单上下文布局：根目录一份 `CONTEXT.md` + `docs/adr/`。见 `docs/agents/domain.md`。
