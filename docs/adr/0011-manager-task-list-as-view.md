# 管理任务模式以纳管对话为事实源，任务清单降为它的视图

2026-11-03，用户确认管理模式的后端从旧的队长编排迁到 session-manager 闭环，任务清单插件不再自己保存任务事实，改为渲染纳管对话与待答问题的派生视图。

## 背景

上一轮侦察确认了三件事：旧「管理模式」预设已于 2026-10-17 随 omni/manager/simple 一并删除（`dsh-extensions` 提交 `22ed30a`），`~/.dsh/.agent-presets/manager/` 是孤儿文件；`dsh-task-manager` 插件与任务清单界面仍在生产实例上挂着，但生产 `tasks.json` 只有 2026-09-12 两条试写记录、`captains.json` 为空，队长编排从未真正投入使用；`@deepseek-ai/dsh-session-manager` 已并入 harness 代码，但任何 profile 都未启用。

## 决定

- **后端**取 session-manager：一张任务卡片对应一个普通工作对话，管理会话只做调度与偏好，不执行任务本身。
- **事实源**是纳管关系与待答问题本身，任务清单**派生**渲染，不另存第二套任务表（延续 [manager-session-dispatch](</home/sx/projects/MyAI/docs/plans/manager-session-dispatch.md>) 「不复制六态任务系统」的约束）。
- **回复框的答复交给管理会话**，由管理模型决定如何答复具体的工作对话；界面不直接与工作对话对话，避免绕过管理端的归属与授权。
- **落地顺序**先在 3081 开发实例启用验证，验收后再切 3080；切换需要重启生产服务，会中断进行中的对话。
- **经验沉淀**分两处：长期偏好进 OpenViking（包内 `manager_preferences` 已有 lookup / remember / correct / forget）；可复用的「同类问题怎么答」判据写成技能目录，落 `dsh-extensions/skills/`。只固化用户明确表达的长期默认，一次性资料、临时批准与模型推测不沉淀。
- **执行汇报**是即时渲染的 Markdown 文档（`GET /plugins/dsh-task-manager/report?taskId=`），不另写盘、不写进任务目录。

## 影响

- 已实现的卡片 UI（状态徽章、对话跳转、回复框、执行汇报文档）在两种后端下都可用；本轮只需替换数据来源。
- 术语表里队长时代的词条（队长、队长类别、队长模式、类别章程、形式核验）标记为已废止，仅保留给历史计划文档引用。
- 旧队长编排代码（`dsh-task-manager` 的 assign / captains / 五个管理工具）**本轮不删**，等新模式验收通过后再单独清理，避免一次改动同时承担替换与删除的风险。
