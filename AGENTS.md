## 开发位置（本工作区）

- 开发位置：DSH 仓库现在是**单检出** `master/`（分支 `master`）。原 `dev/` worktree 已于 2026-09-13 下线——`dev` 分支（本地与 `fork` 远端）、worktree、3081 dev 实例、`dsh-web-dev.service` 一并移除。
- 生产实例：端口 `3080`、`DSH_HOME=~/.dsh`、由 `dsh-web.service` 托管，**就跑在这份 `master/` 检出上**——改 master 即改生产，重启生产会中断当前对话，重启前先确认。
- `dsh-extensions/` 是单检出（分支 `main`，其插件源码就是生产 `link:` 的目标），需要时按 `-dev/` 约定新建 worktree。
- 位置纪律与动手前确认流程见用户级 `~/.dsh/AGENTS.md`「修改位置」节；本工作区先例复盘：`docs/plans/manager-task-orchestration.md`「经验教训」节。

## Agent skills

### Issue tracker

Issues live as local markdown files under `.scratch/<feature>/` in this workspace (no remote tracker). See `docs/agents/issue-tracker.md`.

### Triage labels

Five canonical triage roles mapped to: `triage`, `info-needed`, `agent-ready`, `human-ready`, `wontfix`. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context layout: one `CONTEXT.md` + `docs/adr/` at the root. See `docs/agents/domain.md`.
