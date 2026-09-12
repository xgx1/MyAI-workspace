# 生产插件的来源与更新方式

记录 MyAI 工作区里被 DSH web profile（`~/.dsh/profiles/web/package.json`）以 `link:` 方式挂载的插件：
它们的源码在哪里、受不受版本控制、上游是谁、该怎么更新。
本文件随工作区结构审计（2026-09-12）建立，目的是让"误删/改坏无法回滚"和"不知道该从哪更新"这两类问题不再发生。

## 一、生产 link 的插件一览（2026-09-12 核对）

| 插件包 | 源码路径 | 版本控制 | 上游 / 更新方式 |
| --- | --- | --- | --- |
| `dsh-task-manager` | `dsh-extensions/plugins/dsh-task-manager` | ✅ dsh-extensions 仓库（分支 `main`） | 自研；改完在仓库里提交、`pnpm build` |
| `dsh-sidebar-taskbar` | `dsh-extensions/plugins/dsh-sidebar-taskbar` | ✅ dsh-extensions 仓库（分支 `main`） | 自研；同上 |
| `web-dsh-web-extension` | `dsh-extensions/plugins/web-dsh-web-extension` | ✅ dsh-extensions 仓库（分支 `main`） | 自研；同上 |
| `@changfenhuang/dsh-genui` | `_dsh_plugins_src/dsh-genui` | ✅ 自带 `.git` | `github.com/omdsh-dev/dsh-genui` |
| `@deepseek-ai/dsh-toolkit` | `_dsh_plugins_src/dsh-toolkit` | ✅ 自带 `.git` | `github.com/omdsh-dev/dsh-toolkit` |
| `@dsh-external/dsh-drop-to-path` | `_dsh_plugins_src/dsh-drop-to-path` | ✅ 自带 `.git` | `github.com/loudMore/dsh-drop-to-path` |
| `@memtensor/memos-local-plugin` | `_dsh_plugins_src/MemOS/apps/memos-local-plugin` | ✅ 2026-09-12 接入 | `github.com/MemTensor/MemOS`（分支 `main`）——见下方更新注意 |
| `@nanmicoder/dsh-agent-teams` | `_dsh_plugins_src/dsh-agent-teams` | ✅ 2026-09-12 接入 | `github.com/NanmiCoder/dsh-agent-teams`（分支 `main`） |
| `dsh-context-compression-selector` | npm registry（`0.1.0`） | — | `github.com/WilliamShi666/dsh-context-compression-selector` |
| `dsh-lan-access` | npm registry（`^0.1.1`） | — | 第三方 npm 包 |

## 二、第三方插件的接入方式与现状

两个目录原本是"解压出来的源码"（没有 `.git`）。2026-09-12 用**不覆盖工作区**的方式接上了上游：

```sh
cd <目录>
git init -q
git remote add origin <上游 URL>
git fetch origin main
git reset --mixed origin/main     # 只移动 HEAD 与索引，工作区一个字节都不动
git branch -m main               # 本地分支名与上游对齐
git branch --set-upstream-to=origin/main
```

### MemOS（`_dsh_plugins_src/MemOS`）

- 上游：`github.com/MemTensor/MemOS`（Apache-2.0），默认分支 `main`，接入时 HEAD `de806942`（2026-09-08）。
- 生产实际加载的是子目录 `apps/memos-local-plugin`。
- **关键事实：本地副本比上游 main 更新**——本地 `@memtensor/memos-local-plugin` 是 `2.0.19`，上游 `main` 里是 `2.0.16-beta.1`。
- 因此 **`git pull` 会把生产插件降级**。正确用法是：用 `git fetch` 观察上游何时超过 `2.0.19`（或发布新 tag）再更新；本地新增/修改只集中在少数文件，`git status` 可随时核对。
- 目录里有一个本地遗留文件 `apps/memos-local-plugin/pnpm-workspace.yaml.bak-issue`（未跟踪），确认无用后可删。

### dsh-agent-teams（`_dsh_plugins_src/dsh-agent-teams`）

- 上游：`github.com/NanmiCoder/dsh-agent-teams`（MIT），默认分支 `main`，接入时 HEAD `18fba62`（2026-09-11）。
- 本地版本 `0.1.17` 与上游 `main` 相同；本地多出 `lib/`（构建产物）与 `node_modules/`，缺少上游的开发用文件（`.github/`、`.agents/`、`AGENTS.md` 等）——即本地更像"发布包 + 本地构建"，上游是源码仓库形态。
- 若要从源码更新：`git pull && pnpm install && pnpm build`，**改完必须重建 `lib/`**，因为生产加载的是 `lib/`。

## 三、更新前的通用纪律

1. 这些目录都是**生产运行时依赖**（`link:` 挂载，dsh-web 重启即加载），更新后必须在 dev 实例（3081）先验证，再重启生产。
2. 更新后如果插件的客户端半边引入新的平台模块，先核对 `packages/client/web/src/platform.ts` 里的 `PLATFORM_MODULES` 是否包含它——插件 bundle 只能 `require` 那张表里的模块。
3. 更新完记一笔：改了哪个插件、从哪个版本到哪个版本、什么时候、验证方式。
