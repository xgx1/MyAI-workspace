# old/ — 已删除技能的结论存档

> **2026-11-17：5 个技能目录已删，只留这张表。**它们指向的项目至今不存在，留着只是让下一个翻新的人再全盘搜一遍。要找回正文：`git log --oneline -- old/` 里 2026-11-17 之前的提交。

当初的划分：

## 为什么在这里

它们的正文指向**本机不存在的项目**，因此既无法按上游仓库分组（没有上游），也无法移回项目（项目不在本机）：

| 技能 | 指向的项目 | 全盘搜索结果（2026-09-13） |
| --- | --- | --- |
| `unrealcli-dev-env-reset`、`unrealcli-global-tool-reinstall`、`unrealcli-pm2-pattern`、`verify-unrealcli-command` | UnrealCli | 只有痕迹：Windows 盘上装了全局 dotnet 工具 `unrealcli.exe` v1.1.7（编译产物）、一份技能备份 `.dsh/backups/skills-unrealcli-removed-20260826-063238/`、归档记忆指向 `C:/Users/Sx/Project/UnrealCli`（该目录不存在）。**源码不在任何盘上** |
| `media-convert-defaults` | Sx.Cli | 全盘零命中 |
| `batch-file-organizing` | FileOrganizer | 全盘零命中 |

## 当初的取用规则（技能已删，规则仍适用）

项目若重新出现，从 git 历史取回正文，按 `unrealcli-*` → UnrealCli、`media-convert-defaults` → Sx.Cli、`batch-file-organizing` → FileOrganizer 归位。去处：按 2026-08-26 的《UE 技能整理方案》原则——**项目专属技能应落在各项目 workspace 的 `.dsh/skills/`**，而不是回到主技能库。

## 背景

这批技能原在 `~/.dsh/skills/`（运行时技能目录）。2026-09-13 整理技能库时，发现它们属于"项目专属但项目不存在"这一类，用户决定先行暂存、不纳入当轮的按上游仓库分组与子模块化迁移。
