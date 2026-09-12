## 开发位置（本工作区）

- 开发位置：DSH 仓库按「主检出 + dev worktree」成对摆放——`master/`（分支 master）↔ `dev/`（分支 dev）；`dsh-extensions/` 自 2026-09-12 清理后是单检出（只有分支 `main`，其插件源码就是生产 `link:` 的目标），需要时再按 `-dev/` 约定新建 worktree。
- dev 实例：端口 `3081`、`DSH_HOME=dev/.dsh-home`（启动脚本 `dev/.dsh-dev-launch.sh`），与生产（`master/` 的 `dsh-web.service`、端口 `3080`、`~/.dsh`，即当前对话所在实例）相互隔离 → dev 侧改完可随时重启、测试、复验，不会动到生产。
- 位置纪律、例外与动手前确认流程见用户级 `~/.dsh/AGENTS.md`「修改位置（默认 dev worktree）」节；dev 实例的完整操作流程见 dev 仓库 `.agents/skills/dsh-dev-loop` 技能；本工作区先例复盘：`docs/plans/manager-task-orchestration.md`「经验教训」节。

## Agent skills

### Issue tracker

Issues live as local markdown files under `.scratch/<feature>/` in this workspace (no remote tracker). See `docs/agents/issue-tracker.md`.

### Triage labels

Five canonical triage roles mapped to: `triage`, `info-needed`, `agent-ready`, `human-ready`, `wontfix`. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context layout: one `CONTEXT.md` + `docs/adr/` at the root. See `docs/agents/domain.md`.
