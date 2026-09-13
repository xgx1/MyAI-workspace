## 开发位置（本工作区）

- 开发位置：DSH 仓库现在是**单检出** `deepseek-harness/`（分支仍是 `master`）——目录于 2026-09-13 由 `master/` 改名而来。原 `dev/` worktree 同日下线（`dev` 分支、worktree、3081 dev 实例、`dsh-web-dev.service` 一并移除）。
- 生产实例：端口 `3080`、`DSH_HOME=~/.dsh`、由 `dsh-web.service` 托管，**就跑在这份 `deepseek-harness/` 检出上**——改它即改生产，重启生产会中断当前对话，重启前先确认。
- `dsh-extensions/` 是单检出（分支 `main`）：`plugins/`（自研，受本仓版本控制）与 `skills/` 就是生产 `link:` 的目标；`vendor/` 是**第三方上游克隆**（dsh-genui / dsh-toolkit / dsh-drop-to-path，均为生产 `link:` 目标），各自带独立 `.git` 与远端、被本仓 `.gitignore` 忽略——改它们要在各自目录里提交。需要隔离改动时按 `~/.dsh/AGENTS.md`「如果要重新引入…自行开 worktree」的指引新建。
- 位置纪律与动手前确认流程见用户级 `~/.dsh/AGENTS.md`「修改位置」节；本工作区先例复盘：`docs/plans/manager-task-orchestration.md`「经验教训」节。

## Agent skills

### Issue tracker

Issues live as local markdown files under `.scratch/<feature>/` in this workspace (no remote tracker). See `docs/agents/issue-tracker.md`.

### Triage labels

Five canonical triage roles mapped to: `triage`, `info-needed`, `agent-ready`, `human-ready`, `wontfix`. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context layout: one `CONTEXT.md` + `docs/adr/` at the root. See `docs/agents/domain.md`.
