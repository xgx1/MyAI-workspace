# MyAI 工作区

若干独立仓库的宿主与编排层：既定义多会话任务编排的语境，也定义这些仓库之间固定的拓扑关系。

本仓自己不产出可运行代码——它承载的是工作区级资产：Agent 规则、领域术语、架构决策记录与安装指南。

## 仓库拓扑

用 git submodule 管理两层仓库，**层级固定两层，不下探第三层**（[`docs/adr/0005`](docs/adr/0005-submodule-layering.md)）。

| 路径 | 远端 | 是什么 |
|---|---|---|
| `deepseek-harness/` | [xgx1/deepseek-harness](https://github.com/xgx1/deepseek-harness) | DSH 本体（`deepseek-ai/deepseek-harness` 的 fork）。生产 Web 实例就跑在这份检出上 |
| `dsh-extensions/` | [xgx1/dsh-extensions](https://github.com/xgx1/dsh-extensions) | 扩展宿主，自管 20 个子模块：`vendor/` 第三方插件 + `skills/` 技能分组仓 |
| `dsh-Go/` | [xgx1/dsh-Go](https://github.com/xgx1/dsh-Go) | Android 客户端（Flutter + PRoot 里的 DSH 引擎）；与 DSH 本体无共享历史，改动前先读它自己的 `AGENTS.md` |

`update-app` 位于工作区之外（`~/projects/update-app`），因此不是本仓的子模块。

改子模块要在**各自目录里**提交、推送，再回本仓更新指针——本仓只保存指向某个提交的指针。

## 本仓内容

一个顶层条目只有三种身份：**入库的工作区资产**、**子模块**（见上表）、**不入库的本地工作区**（可再生或临时）。没有第四种，说不清归哪一类的就是该删的。

| 路径 | 作用 | 入库 |
|---|---|---|
| `AGENTS.md` | 工作区级 Agent 规则：开发位置、子模块纪律、技能部署 | 是 |
| `CONTEXT.md` | 领域术语表，分「任务编排」「仓库拓扑」两节，每个词带 _Avoid_ 别名 | 是 |
| `INSTALL.md` | 全栈安装 / 新设备恢复指南，Linux 与 Windows 各一套 | 是 |
| `docs/adr/` | 架构决策记录 0001–0015 | 是 |
| `docs/plans/`、`docs/notes/`、`docs/research/` | 实现计划、调研笔记、实验记录（含 fork 分歧） | 是 |
| `docs/functional/`、`docs/manual-tests/` | 功能说明与人工测试用例 | 是 |
| `docs/agents/` | Issue tracker、triage 标签、领域文档布局的约定 | 是 |
| `.scratch/` | 本地 issue tracker（无远程 tracker）+ 实验场。只留三个：`background-window-control/`（scoped 输入回归夹具）、`context-overflow-recovery/`（ADR 0009 的可复跑 A/B 台）、当前在建的那个实验 | 部分是 |
| `old/` | 已删除技能的结论存档：5 个指向不存在项目的技能于 2026-11-17 删除，只剩 `old/README.md` 的检索证据 | 是 |
| `deepseek-harness-dev/` | DSH 开发 worktree（同一 `.git` 的 dev 分支），开发实例 3081 跑它 | 否 |
| `browser-control/` | 浏览器访问链路试验场：`captcha-solver` 的独立克隆（自带 `.git`），用完即删 | 否 |
| `.zvec-grep/` | zvec-grep 的工作区索引，`zg index --rebuild` 可再生 | 否 |

命名约定：顶层目录一律**纯小写、单词间用横线**（子模块沿用各自上游的仓库名，不为了整齐去改——改子模块路径要动 `.gitmodules`，别的机器拉取后得手工 `submodule sync`）。

## 从哪里读起

| 你的问题 | 读这个 |
|---|---|
| 想在新设备上把这套栈跑起来 | [`INSTALL.md`](INSTALL.md) |
| 「队长」「形式核验」是什么意思 | [`CONTEXT.md`](CONTEXT.md) |
| 为什么用子模块而不是忽略式嵌套 | [`docs/adr/0005`](docs/adr/0005-submodule-layering.md) |
| 技能为什么按上游仓库分组 | [`docs/adr/0006`](docs/adr/0006-skills-grouped-by-upstream-repo.md) |
| 任务清单归谁写 | [`docs/adr/0001`](docs/adr/0001-task-list-hosted-by-dsh-task-manager.md)、[`0004`](docs/adr/0004-dual-entry-host-service-and-tools-subpath.md) |

## 相关仓库

| 仓库 | 作用 |
|---|---|
| [xgx1/dsh-extensions](https://github.com/xgx1/dsh-extensions) | 自研插件与技能分组仓（生产 `link:` 的目标） |
| [xgx1/deepseek-harness](https://github.com/xgx1/deepseek-harness) | DSH 本体检出 |
| [xgx1/dsh-home](https://github.com/xgx1/dsh-home) | `~/.dsh` 配置层：全局规则、agent preset、profile composition（不含密钥与运行时数据） |
| [xgx1/update-app](https://github.com/xgx1/update-app) | `update-all` 编排 CLI 及其技能 |

## 克隆

三个子模块与 `dsh-extensions` 的下一层子模块（共 23 个远端）均为公开仓库，未登录即可递归克隆：

```bash
git clone --recurse-submodules https://github.com/xgx1/MyAI-workspace.git
```

已经克隆过的补拉子模块：

```bash
git submodule update --init --recursive
```

装完不等于能用——完整流程（构建 DSH 本体、构建扩展、装配置层、软链技能、起服务）见 [`INSTALL.md`](INSTALL.md)。
