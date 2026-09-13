# deepseek-harness fork 的分叉现状（2026-09-13 盘点）

本工作区的 `deepseek-harness/` 是你 fork 的仓库（`origin` = `deepseek-ai/deepseek-harness`，`fork` = `xgx1/deepseek-harness`），
**生产实例（3080）就跑在这份检出上**。本文件记录「本地相对上游到底改了什么」，供每次同步上游前对照。

## 同步状态

| 方向 | 数量 |
| --- | --- |
| 落后 `origin/master`（上游） | **0** |
| 领先 `origin/master` | **22 个提交** |
| 与 `fork/master` | 一致（fork 已同步） |

**结论：上游没有可拉取的新提交；本地是纯领先。**

## 22 个领先提交 ≠ 22 份改动

提交历史里有明显的过程性 churn——其中约 8 个是**自我抵消**的：

- 「dev worktree 双实例自我开发」工作流先被引入（`fe4f2767`、`bd118de8`、`eb3ba957`、`4c3b0703`、`0a24275d`、`df9e08ca`），
  又被移除并归档（`b9fb5ea9`、`4eb323f2`）。三个 `dsh-*-loop/sync/deploy` 技能与 `.dsh-dev-launch.sh`
  **在当前工作树里已不存在**——净效果为零。

所以判断分叉规模要看**净差异**，不是提交数。

## 净差异：21 个文件，+460 / −12

```
真实代码改动（7 个文件）
  packages/boot/app-boot/src/profile.ts                    +28     修悬空的 profile 投影链接
  packages/boot/app-boot/tests/profile.spec.ts             +73     上者的测试
  packages/extensions/tool-cordis/src/providers.ts         +48     share-inspect providers
  packages/extensions/tool-cordis/src/index.ts             +4
  packages/extensions/tool-cordis/tests/share-inspect-…    +81     上者的测试
  packages/preset/agent-presets/presets/cordis/agent.cordis.yml  ±7  预设调整
  apps/cli/package.json                                    +1      dsh-web-search-exa 依赖

文档与笔记（其余 13 个文件）
  CONTEXT.md、.agents/notes/**（归档笔记 + 已实现笔记）、tool-cordis README（含 i18n）、
  scripts/doc-budgets.manifest.json、pnpm-lock.yaml
```

## 三类改动及其处置

### ① 可能上游化的真实修复（值得考虑提 PR）

`packages/boot/app-boot/src/profile.ts` 的 **「heal dangling profile module-fallback projections」**——
这是 profile 投影链接悬空的真实 bug 修复，附带完整测试（+73 行），并已按仓库惯例写了
`.agents/notes/implemented/bug-fix/` 笔记。**它是这批改动里唯一看起来上游会接受的**。
若上游仍在受此影响，值得单独提 PR。

### ② 本机专属定制（不该上游化）

- `tool-cordis` 的 **share-inspect providers**：本机工作流需要的能力。
- `apps/cli/package.json` 加 **dsh-web-search-exa**：本机选的搜索后端。
- `agent.cordis.yml` 预设调整：本机配置。

### ③ 工作区专属文档

`CONTEXT.md`、`.agents/notes/archived/**`、README 的本地增补——描述的是**本工作区**的做法，
对上游没有意义。

## 每次同步上游时的操作要点

1. `git fetch origin` 后先看 `git rev-list --left-right --count origin/master...HEAD`。
2. **不要**用 `git merge origin/master` 一把梭后不检查：`packages/boot/app-boot/src/profile.ts`
   是本地改过的文件，上游若也动了同一处会产生冲突——这是唯一预期会冲突的点。
3. `pnpm-lock.yaml` 几乎必然冲突（本地 +3 行，且上游依赖树变动频繁）。以**上游为准 + 重跑 `pnpm install`**，
   不要手工合并 lock 文件。
4. 同步后在主检出重建再重启生产（`pnpm build` + `systemctl --user restart dsh-web.service`）。

## 为什么不重写历史

22 个提交里的 churn 看着难受，但**重写已推送的历史**代价更高：这些提交已存在于 `xgx1/deepseek-harness`，
而生产实例正跑在这份检出上。churn 的实际影响也已被 `b9fb5ea9`（归档提交）就地消解——
净差异只有 21 个文件，核对成本很低。**结论：保留历史，靠本文件对照。**
