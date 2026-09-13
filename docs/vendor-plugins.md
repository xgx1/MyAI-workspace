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
| `@memtensor/memos-local-plugin` | npm registry（`2.0.19`） | — | `github.com/MemTensor/MemOS`——2026-09-13 由 link: 源码目录改为 npm 交付，见下 |
| `@nanmicoder/dsh-agent-teams` | npm registry（`0.1.17`） | — | `github.com/NanmiCoder/dsh-agent-teams`——2026-09-13 由 link: 源码目录改为 npm 交付，见下 |
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

### 2026-09-13：这两个插件改为 npm 交付，源码目录已删除

`_dsh_plugins_src/MemOS` 与 `_dsh_plugins_src/dsh-agent-teams` **已整体删除**（含 `.git`）。删除前先做了「无损」验证：

- 用 `npm pack` 取回同版本 tarball，与本地目录逐文件比对：**两边内容不同的文件 = 0**
  （MemOS 92 处差异、agent-teams 7 处，全部是「只在本地存在」的开发文件——`src/`、tsconfig、构建配置，npm 包只发运行时载荷）。
- 因此 npm 包与本地运行时载荷**逐字节一致**，切换不改变行为。

profile 侧改动（`~/.dsh/profiles/web/`）：

1. `package.json`：两条 `link:` 改成版本号 `2.0.19` / `0.1.17`。
2. `pnpm-workspace.yaml` 的 `allowBuilds` 增补：`@memtensor/memos-local-plugin`、`better-sqlite3`、
   `esbuild`、`onnxruntime-node`、`protobufjs` 放行；**`sharp: false` 显式不放行**——
   它靠预编译的 `@img/sharp-linux-x64` 工作（实测可加载），放行反而会走 node-gyp 源码编译并失败
   （缺 `node-addon-api`），让整个 `pnpm install` 非零退出。
3. `pnpm install` 后校验：10 个依赖全部解析、`dsh --profile web --dump-config` 组合出的插件树里两个插件都在。

代价与回滚：

- **磁盘是净增的**：`~/.dsh/profiles/web/node_modules` 从 15M 涨到 1.2G（其中 `onnxruntime-node` 513M、
  MemOS 依赖树 461M），而工作区只回收 600M。`onnxruntime-node` 的 302M CUDA provider 与 34M
  `libonnxruntime.so.1` 由它的 postinstall 拉取，**不能关**（关了 CPU 推理会缺库）。
- 回滚：**不依赖任何 `.bak` 快照**（机器上的备份已于同日清理移除）。把 `package.json` 改回 `link:` 形状本身
  也没用——源码目录已删，链接会悬空。真正的回退路径是：
  1. 重新 clone 上游（`github.com/MemTensor/MemOS`、`github.com/NanmiCoder/dsh-agent-teams`）到 `_dsh_plugins_src/` 下；
  2. 把 `package.json` 里两条依赖改回 `link:`（原路径见本文件第一节表格的「源码路径」列）；
  3. `pnpm install` 重建依赖树，并把 `pnpm-workspace.yaml` 里本文件第 46–50 行提到的 `allowBuilds` 增补去掉。
  换言之：**本文件 + 上游仓库就是完整的回滚材料**，机器上不再保留快照副本。

## 三、更新前的通用纪律

1. 这些目录都是**生产运行时依赖**（`link:` 挂载，dsh-web 重启即加载），更新后必须在 dev 实例（3081）先验证，再重启生产。
2. 更新后如果插件的客户端半边引入新的平台模块，先核对 `packages/client/web/src/platform.ts` 里的 `PLATFORM_MODULES` 是否包含它——插件 bundle 只能 `require` 那张表里的模块。
3. 更新完记一笔：改了哪个插件、从哪个版本到哪个版本、什么时候、验证方式。
