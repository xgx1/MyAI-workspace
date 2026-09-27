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
