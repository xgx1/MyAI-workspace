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
| `@changfenhuang/dsh-genui` | `dsh-extensions/vendor/dsh-genui` | ✅ 自带 `.git` | `github.com/omdsh-dev/dsh-genui` |
| `@deepseek-ai/dsh-toolkit` | `dsh-extensions/vendor/dsh-toolkit` | ✅ 自带 `.git` | `github.com/omdsh-dev/dsh-toolkit` |
| `@dsh-external/dsh-drop-to-path` | `dsh-extensions/vendor/dsh-drop-to-path` | ✅ 自带 `.git` | `github.com/loudMore/dsh-drop-to-path` |
| `@nanmicoder/dsh-agent-teams` | npm registry（`0.1.17`） | — | `github.com/NanmiCoder/dsh-agent-teams`——2026-09-13 由 link: 源码目录改为 npm 交付，见下 |
| `dsh-context-compression-selector` | npm registry（`0.1.0`） | — | `github.com/WilliamShi666/dsh-context-compression-selector` |
| `dsh-lan-access` | npm registry（`^0.1.1`） | — | 第三方 npm 包；实测 `dependencies: {}`，纯 JS 无构建脚本 |

> `@memtensor/memos-local-plugin` 已于 **2026-09-13 彻底移除**，不再是生产插件——见本节末「MemOS 彻底移除」。

### 目录布局：自研 vs 第三方（2026-09-13 归并）

```text
dsh-extensions/              ← 自研仓库（git 远端 xgx1/dsh-extensions）
├── plugins/                 ← 自研插件源码，受本仓版本控制
├── skills/                  ← 自研技能，受本仓版本控制
└── vendor/                  ← 第三方上游克隆（被本仓 .gitignore 忽略）
    ├── dsh-genui/           ← 各自带 .git 与上游远端，独立提交/拉取
    ├── dsh-toolkit/
    ├── dsh-drop-to-path/
    └── rider-skills/        ← JetBrains 官方 rider-skills
```

原工作区根下的 `_dsh_plugins_src/` 与 `rider-skills/` 两个一级目录已并入 `dsh-extensions/vendor/`。
`vendor/` 必须在 `dsh-extensions/.gitignore` 中忽略——否则 `git add -A` 会把它们记成
gitlink（子模块引用）却不含内容。搬迁同步改了：生产 profile 的 3 条 `link:` 与
`node_modules` 符号链接、`update-app/applist.toml`、本文件、`dsh-extension-inventory.json`。

### 2026-09-13：主检出改名后的 vendor 内链重指（一次真实故障）

同日 DSH 主检出目录由 `master/` 改名为 `deepseek-harness/`（分支仍是 `master`）。上面那次搬迁只改了
生产 profile 的 `link:` 与 `node_modules` 顶层链接，**漏掉了 `vendor/dsh-toolkit` 内部的链接**：
它的根与 10 个子包的 `node_modules` 里存有指向旧目录的绝对符号链接
（`@deepseek-ai/dsh-tools` → `packages/core/tools`、`cordis` → `vendor/cordis`、
`@types/node` → 根 `node_modules/.pnpm/@types+node@26.1.2/...`），改名后 23 条全部悬空。

症状：`dsh-web.service` 每 3 秒崩溃重启一次，journal 报
`plugin tree failed to load: failed to apply loader entry tool-kit (@deepseek-ai/dsh-toolkit): Cannot find package '@deepseek-ai/dsh-tools'`。

修复（幂等，可反复执行；已同时固化为 `applist.toml` 的 fixes.rule）：

```sh
find /home/sx/projects/MyAI/dsh-extensions -xtype l -print0 |
while IFS= read -r -d "" l; do
  t=$(readlink "$l") || continue
  case "$t" in
    /home/sx/projects/MyAI/*/*)
      rest=${t#/home/sx/projects/MyAI/}; rest=${rest#*/}
      [ -e "/home/sx/projects/MyAI/deepseek-harness/$rest" ] \
        && ln -sfn "/home/sx/projects/MyAI/deepseek-harness/$rest" "$l" && echo "relinked: $l";;
  esac
done
```

**纪律**：任何改名/移动 `deepseek-harness` 的动作，做完先跑上面的重指，确认
`find /home/sx/projects/MyAI/dsh-extensions -xtype l` 输出为空，再重启 `dsh-web`；
否则生产直接进崩溃循环。

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
  1. 重新 clone 上游（`github.com/MemTensor/MemOS`、`github.com/NanmiCoder/dsh-agent-teams`）到 `dsh-extensions/vendor/` 下；
  2. 把 `package.json` 里两条依赖改回 `link:`（原路径见本文件第一节表格的「源码路径」列）；
  3. `pnpm install` 重建依赖树，并把 `pnpm-workspace.yaml` 里本文件第 46–50 行提到的 `allowBuilds` 增补去掉。
  换言之：**本文件 + 上游仓库就是完整的回滚材料**，机器上不再保留快照副本。

### 2026-09-13：MemOS 彻底移除（最终态）

用户判定不再需要记忆插件，`@memtensor/memos-local-plugin` 被整体移除。改动面：

| 位置 | 处理 |
| --- | --- |
| `~/.dsh/profiles/web/package.json` | 删除依赖与 bundles 两条目（依赖 10→9、bundles 12→11） |
| `~/.dsh/profiles/web/cordis.patch.yml` | 删除 `- id: memos-local-memory` 覆盖块（含 2026-08-24 的召回上限调整） |
| `~/.dsh/profiles/web/node_modules` | 依赖树随 `pnpm install` 剪除；另清掉 `@huggingface/*`、`js-yaml`、`argparse` 等残留与该批空目录 |
| `~/.dsh/profiles/web/pnpm-workspace.yaml` | `allowBuilds` 清空为 `{}`——原有 8 条（含更早遗留的 `cloudflared`/`ssh2`/`cpu-features`）已全部不在 lockfile 与 node_modules 中 |
| `~/.dsh/memos-plugin/` | 数据目录删除（`memos.db` 13.6M，含 102 条 trace / 102 个 episode） |

**效果**：`memos_*` 工具与每轮注入的 `<memos_context>` 自动召回一并消失；profile 从 **905M 降到 18M**（本文档第 74 行「涨到 1.2G」的记录已作废）。

**一处需要留意**：`pnpm install` 在依赖剪除期间超时被杀过一次，锁文件已按缩减后的树重写；随后复跑 `pnpm install` 返回「Already up to date」并补装 3 个包，`dsh --profile web --dump-config` 仍组合出 54 个插件条目、0 报错、6 条 `link:` 全解析。若日后要复核依赖图，以 `pnpm install` + `dump-config` 的组合为准，不要只看目录大小。

**回滚**：数据目录曾备份在 `/tmp/memos-plugin-backup-20260913-131232.tar.zst`（4.2M，/tmp 重启即失）；插件本体可从 npm 重新安装（`pnpm add @memtensor/memos-local-plugin@2.0.19`）并恢复 cordis patch 块。

## 三、更新前的通用纪律

1. 这些目录都是**生产运行时依赖**（`link:` 挂载，dsh-web 重启即加载）。⚠ **dev 实例（3081）已于 2026-09-13 随 dev worktree 一并下线，不再有可先验证的隔离实例**——插件交付/版本变更现在只能靠静态比对（见第二节的 `npm pack` 逐字节比对做法）加生产重启窗口；重启 `dsh-web.service` 会中断当前对话，先确认。
2. 更新后如果插件的客户端半边引入新的平台模块，先核对 `packages/client/web/src/platform.ts` 里的 `PLATFORM_MODULES` 是否包含它——插件 bundle 只能 `require` 那张表里的模块。
3. 更新完记一笔：改了哪个插件、从哪个版本到哪个版本、什么时候、验证方式。
