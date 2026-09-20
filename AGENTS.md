# AGENTS.md — MyAI 工作区本地约定

通用的 DSH 规则（重启纪律、submodule 机制、技能软链/分组/平台约定、调用语法、GUI 窗口、代码检索）见用户级 `~/.dsh/AGENTS.md`。本文件只放**这个工作区特有**的路径与仓库事实。

## 仓库布局

- **`deepseek-harness/`** —— 唯一检出（分支 `master`）。**生产实例（3080）就跑在它上**（`~/.local/bin/dsh` → 该检出的 `apps/cli/lib/bin.js`，由 `dsh-web.service` 托管）——改它就是改生产。
- **`dsh-extensions/`** —— 单检出（分支 `main`）：`plugins/`（自研，受本仓版本控制）与 `skills/` 是生产 `link:` 的目标。
- **`dsh-extensions/vendor/` 与 `dsh-extensions/skills/` 都是 git submodule**（各 4 个与 14 个，共 18 个）：
  - `vendor/` = 第三方插件源码，均为生产 `link:` 目标。`dsh-genui` / `dsh-toolkit` / `dsh-drop-to-path` 直连上游；`dsh-evolve-modes` 是 `xgx1` fork（origin=fork、upstream=上游）。
  - `skills/` = 技能分组仓，一个上游仓库一组。组树 = 上游树 + 本地改动移植。详见 `docs/adr/0006`。
  - 改它们要在**各自目录里**提交、推送，再回 `dsh-extensions` 更新指针；本仓只保存指针。两者都不被 `.gitignore` 忽略（见 `docs/adr/0005`）。
- 位置纪律与动手前确认流程见用户级 `~/.dsh/AGENTS.md`「修改位置」节；本工作区先例复盘：`docs/plans/manager-task-orchestration.md`「经验教训」节。

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
