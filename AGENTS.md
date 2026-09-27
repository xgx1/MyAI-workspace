# AGENTS.md — MyAI 工作区本地约定

通用的 DSH 规则（重启纪律、submodule 机制、技能软链/分组/平台约定、调用语法、GUI 窗口、代码检索）见用户级 `~/.dsh/AGENTS.md`。本文件只放**这个工作区特有**的路径与仓库事实。

## 仓库布局

- **`deepseek-harness/`** —— **生产检出**（分支 `master`）。**生产实例（3080）就跑在它上**（`~/.local/bin/dsh` → 该检出的 `apps/cli/lib/bin.js`，由 `dsh-web.service` 托管）——改它就是改生产，**默认只读**（见下节「DSH 改动落点」）。
- **`deepseek-harness-dev/`** —— **DSH 功能开发的唯一落点**：`deepseek-harness/` 的 git worktree（分支 `dev`，与生产检出共用同一 `.git`，目录同层级）。开发实例跑在它上面：
  - `dsh-web-dev.service` → **http://127.0.0.1:3081**，`DSH_HOME=~/.dsh-dev`（sessions/storages 与生产隔离）；启动脚本 `~/.dsh-dev/dsh-web-dev-launch.sh`，unit 权威副本 `~/.dsh/deploy/systemd-user/dsh-web-dev.service`。
  - composition 副本在 `~/.dsh-dev/profiles/web/`：**要调开发实例的组成就改这份**，别改生产的 `~/.dsh/profiles/web/`。
  - 开发循环：worktree 里改代码 → `pnpm run build` → `systemctl --user restart dsh-web-dev.service` → 刷新 3081。
  - `~/.dsh-dev/settings.yaml` 与 `profiles/web/` 都是**快照副本**（不跟随生产）：同步生产 composition 用 `cp ~/.dsh/profiles/web/{cordis.patch.yml,package.json,pnpm-lock.yaml} ~/.dsh-dev/profiles/web/ && (cd ~/.dsh-dev/profiles/web && pnpm install --registry=https://registry.npmmirror.com --prefer-offline)`。
  - 依赖装不上时先看 registry：本机 `registry.npmjs.org` 不通，用 `pnpm install --registry=https://registry.npmmirror.com --prefer-offline`。
- **`dsh-extensions/`** —— 单检出（分支 `main`）：`plugins/`（自研，受本仓版本控制）与 `skills/` 是生产 `link:` 的目标。
- **`dsh-extensions/vendor/` 与 `dsh-extensions/skills/` 都是 git submodule**（各 4 个与 14 个，共 18 个）：
  - `vendor/` = 第三方插件源码，均为生产 `link:` 目标。`dsh-genui` / `dsh-toolkit` / `dsh-drop-to-path` 直连上游；`dsh-evolve-modes` 是 `xgx1` fork（origin=fork、upstream=上游）。
  - `skills/` = 技能分组仓，一个上游仓库一组。组树 = 上游树 + 本地改动移植。详见 `docs/adr/0006`。
  - 改它们要在**各自目录里**提交、推送，再回 `dsh-extensions` 更新指针；本仓只保存指针。两者都不被 `.gitignore` 忽略（见 `docs/adr/0005`）。
- 位置纪律与动手前确认流程见用户级 `~/.dsh/AGENTS.md`「修改位置」节；本工作区先例复盘：`docs/plans/manager-task-orchestration.md`「经验教训」节。

## DSH 改动落点（默认只改 worktree）

**除非你在当次需求里主动说明，DSH 的任何代码 / 配置改动只做在 `deepseek-harness-dev/` 里；`deepseek-harness/` 是生产检出，除只读操作外不许动。**（2026-09-26 用户指示）

- 「主动说明」= **当次对话**里点名要改生产检出（例如「这次直接改 `deepseek-harness` 并重启 3080」）。此前对话说过、别处文档写过、任务看起来「顺便也要」——都不算。
- 生产检出上**禁止**：编辑任何文件、`git add/commit/checkout/branch/worktree`、`pnpm install`、任何写产物的构建（`pnpm run build`、`build:lib:*`、`build:web`……）、改 `~/.dsh/profiles/` 下的生产 composition。
- 生产检出上**允许**（只读）：读代码与文档、`git log|status|diff|show`、`systemctl --user status dsh-web.service`、查端口与日志。
- 验证开发改动一律走 dev 实例 3081；**不要**拿 3080 当试验台，也不要用重启 `dsh-web.service` 的方式看效果（会中断当前对话）。
- 真正会影响生产的动作（重启 `dsh-web.service`、改 `~/.dsh` 的生产 composition 或 unit、动 `dsh-extensions` 里被生产 `link:` 的目录）**先问用户**。

## 本地 Laya 决策模型（dev 侧，2026-09-27 接入）

给 agent 补「快判断」能力：state + 类型化问题（`noul` 是/否、`choice` 选一、`score` 打分）→ 一次前向返回校准概率，不生成文本。

- **模型**：`convaiinnovations/laya`（421M，Apache-2.0，ModernBERT-large 编码器 + 决策头）。权重在 `~/.model/laya/hf`（用 `HF_HOME` 指过去，遵守「模型一律在 `~/.model`」的约定）；venv 在 `~/.local/share/laya/venv`（Python 3.12 + `torch 2.10.0+rocm7.0`，gfx1100 轮子）。
- **侧车**：`laya-sidecar.service` = `laya-mcp serve --model english --port 8083`，启动脚本 `~/.local/share/laya/run-sidecar.sh`。实测 **18–24 ms/次**（3 问一次前向），空缓存冷启动 82 s、有缓存 9.4 s。
- **显存**：english + multilingual 常驻约 **5.5 GB**。**与 Bonsai 2 27B（100K 上下文峰值 12.3 GB）无法同时驻留**，二选一：`systemctl --user stop laya-sidecar`。
- **DSH 侧**：npm 插件 `dsh-laya`（v0.1.4）装在 **dev home** 的 `web` 与 `headless` profile 里，`sidecarUrl` 必须在 patch 里覆盖成 `http://127.0.0.1:8083`（插件默认值 8787 是 headroom 的端口）。模型可见工具：`laya_ask`、`laya_plan`。注意：从 profile 目录跑 `node -e "import('dsh-laya')"` 会报 `Cannot find package '@deepseek-ai/dsh-tools'`，**那是误报**——harness 自己解析安装态的 `@deepseek-ai/*`；判据是会话里工具真的出现（headless 实测已出现）。
- **自检**：`curl -s localhost:8083/health`（看 `degraded`）· `~/.local/share/laya/venv/bin/laya-mcp doctor`（先在 GPU 上真跑一个算子再下结论，别信 `torch.cuda.is_available()`）。
- **两个坑**：① 侧车必须清 `*_proxy`——`all_proxy=socks5://` 会让 httpx 报 `socksio` 缺失直接拒启（脚本里已 `unset`）；② 上游 english 检查点自带非法温度，启动日志会警告 `Treat confidence from the affected entries as uncalibrated`。
- **纪律偏差**：这次按「最小闭环」走的是 npm 交付（`dsh plugin add dsh-laya`），不是 ADR-0007 的 fork → submodule → `link:`。要进**生产** profile 前应先补成源码安装。

### 判断层：逐轮模型路由（自研，2026-09-27）

- **代码**：`dsh-extensions/plugins/dsh-laya-router`（受 dsh-extensions 版本控制，`link:` 装进 dev home 的 `web` + `headless` profile，bundle 行 `laya-router`）。改完要 `pnpm run build`——加载的是 `lib/`，源码改了不重建会静默跑旧代码。
- **做什么**：每用户轮次在 `agent/pre-step` 问 Laya 三个 `choice`（难度／时间预算／是否还在原任务上）→ 在 `agent/request` 的 `step === 1` 应用路由与思考档位；判定「换任务 + 上下文 >40%」时在 pre-step 调 `compactIfNeeded(..., 'context-overflow')`。换路由时自己追加 `[model routed: …]` 通知（原生那条只由用户手动切模型触发）。
- **谁会被路由**：模型选择器里有一组「自动（判断层逐轮选择）」的 `auto` 条目（插件注册的 LLM provider；目录是注册表投影）。**只有选中 `auto` 的会话被路由**，选具体模型就完全听人的；会话没显式选择时看部署默认 `agent-default-model`。旧语义（`live` 时路由所有会话）保留为 `applyWhen: always`。
- **模式**：`mode: off | shadow | live`，**dev 实例已开 live**（配置在 `~/.dsh-dev/profiles/web/cordis.patch.yml`）。运行时用 `/route shadow|live|off` 切换，持久化在 `$DSH_HOME/laya-router-state.json`（重启仍生效）；`/route status` 看最近一次决策与当前模式，`/route stats [n]` 看路由/依据/压缩/耗时分布，`/route reset` 回到配置默认。
- **决策日志**：`$DSH_HOME/laya-router.jsonl`（含判断状态裁剪了几条消息、三个答案的置信度、最终路由与依据、侧车耗时）。启动时服务日志会打 `[laya-router] ready (mode=…)` 与 `/route registered …` 两行——**判断 `/route` 有没有挂上就看这两行**（静默失败与正常无法从别处区分）。
- **设计取舍**：见 `docs/adr/0008`（为什么状态要自己拼、为什么全用 `choice`、为什么先影子）；上游坑与实测数字在插件自己的 README 里；`state`/`policy`/`stats`/`auto-route` 四个模块有 49 个单测（`pnpm test`）。
- **验收现状**：shadow 与 live 都在 dev home 的 headless profile 上实测过；live 已切到 3081，`model/selection` 会落库（UI 选择器跟着显示路由结果）、路由与档位真的写进 request/header。**长期效果还没观察**——先跑几天，拿 `/route stats` 与 jsonl 对表再决定要不要调路由表。

## 技能部署

- `dsh-extensions/install-skill.sh` 是安装/更新的唯一入口：递归扫描 `dsh-extensions/skills/`、`~/projects/update-app/skills/`、`~/projects/*/.dsh/skills/` 三源，把技能目录软链到 `~/.dsh/skills/`。覆盖真实目录需 `--force`（先备份到 `~/.dsh/skill-backups/`），`--dry-run` 预演。
- 源①的跳过规则：跳过 `tests/`/`fixtures/`/`examples/`/`sample*` 噪音并打印跳过清单；同名副本取路径最浅者，故 `skills/`、`.agents/skills/` 优先于分发副本。技能目录 = 含 `SKILL.md` 的目录，**不限深度**。
- 自检：`--dry-run` 输出里「新建 N」应为 0，否则有技能没被纳入受管源。

## 本工作区

- 待归位的技能（指向本机不存在项目的）暂存在于 `old/`，见 `old/README.md`。
- `update-app`（CLI + `update-all` 技能）独立仓库位于 `~/projects/update-app`。

## Agent skills

### Issue tracker

Issues live as local markdown files under `.scratch/<feature>/` in this workspace (no remote tracker). See `docs/agents/issue-tracker.md`.

### Triage labels

Five canonical triage roles mapped to: `triage`, `info-needed`, `agent-ready`, `human-ready`, `wontfix`. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context layout: one `CONTEXT.md` + `docs/adr/` at the root. See `docs/agents/domain.md`.
