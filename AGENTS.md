## 开发位置（本工作区）

- 开发位置：DSH 仓库现在是**单检出** `deepseek-harness/`（分支仍是 `master`）——目录于 2026-09-13 由 `master/` 改名而来。原 `dev/` worktree 同日下线（`dev` 分支、worktree、3081 dev 实例、`dsh-web-dev.service` 一并移除）。
- 生产实例：端口 `3080`、`DSH_HOME=~/.dsh`、由 `dsh-web.service` 托管，**就跑在这份 `deepseek-harness/` 检出上**——改它即改生产，重启生产会中断当前对话，重启前先确认。
- `dsh-extensions/` 是单检出（分支 `main`）：`plugins/`（自研，受本仓版本控制）与 `skills/` 就是生产 `link:` 的目标。
- **`vendor/` 与 `skills/` 都是 git submodule**（各 3 个与 17 个，共 20 个）：
  - `vendor/` = 第三方上游克隆（dsh-genui / dsh-toolkit / dsh-drop-to-path，均为生产 `link:` 目标），远端指各自上游。
  - `skills/` = **技能分组仓**，一个上游仓库一组，`skills/<上游仓库名>/<技能>/`；有上游的是 `xgx1` 下的公开 fork，无上游的是自建仓。详见 `docs/adr/0006`。
  - 改它们要在**各自目录里**提交、推送，再回 `dsh-extensions` 更新指针；本仓只保存指针。两者都**不再被 `.gitignore` 忽略**（见 `docs/adr/0005`）。
- 技能部署：`dsh-extensions/install-skill.sh` 扫描三个技能源并软链进 `~/.dsh/skills/`；项目专用技能放各项目自己的 `<项目根>/.dsh/skills/`。见用户级 `~/.dsh/AGENTS.md`「技能」节。
- 待归位的技能（指向本机不存在项目的）暂存在 `old/`，见 `old/README.md`。
- 位置纪律与动手前确认流程见用户级 `~/.dsh/AGENTS.md`「修改位置」节；本工作区先例复盘：`docs/plans/manager-task-orchestration.md`「经验教训」节。

## Agent skills

### Issue tracker

Issues live as local markdown files under `.scratch/<feature>/` in this workspace (no remote tracker). See `docs/agents/issue-tracker.md`.

### Triage labels

Five canonical triage roles mapped to: `triage`, `info-needed`, `agent-ready`, `human-ready`, `wontfix`. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context layout: one `CONTEXT.md` + `docs/adr/` at the root. See `docs/agents/domain.md`.
