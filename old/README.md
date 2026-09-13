# old/ — 等待归位的技能

这里的技能**不参与任何迁移或整理操作**，只是暂存。

## 为什么在这里

它们的正文指向**本机不存在的项目**，因此既无法按上游仓库分组（没有上游），也无法移回项目（项目不在本机）：

| 技能 | 指向的项目 | 全盘搜索结果（2026-09-13） |
| --- | --- | --- |
| `unrealcli-dev-env-reset`、`unrealcli-global-tool-reinstall`、`unrealcli-pm2-pattern`、`verify-unrealcli-command` | UnrealCli | 只有痕迹：Windows 盘上装了全局 dotnet 工具 `unrealcli.exe` v1.1.7（编译产物）、一份技能备份 `.dsh/backups/skills-unrealcli-removed-20260826-063238/`、归档记忆指向 `C:/Users/Sx/Project/UnrealCli`（该目录不存在）。**源码不在任何盘上** |
| `media-convert-defaults` | Sx.Cli | 全盘零命中 |
| `batch-file-organizing` | FileOrganizer | 全盘零命中 |

## 什么时候把它们取出来

- 找到对应项目的源码之后（优先按 `unrealcli-*` → UnrealCli、`media-convert-defaults` → Sx.Cli、`batch-file-organizing` → FileOrganizer 归位）
- 或者项目确认不再需要时，直接删除

取出后的去处：按 2026-08-26 的《UE 技能整理方案》原则——**项目专属技能应落在各项目 workspace 的 `.dsh/skills/`**，而不是回到主技能库。

## 背景

这批技能原在 `~/.dsh/skills/`（运行时技能目录）。2026-09-13 整理技能库时，发现它们属于"项目专属但项目不存在"这一类，用户决定先行暂存、不纳入当轮的按上游仓库分组与子模块化迁移。
