---
tags: [DSH, 管理模式, 实施计划]
status: 待实现
---

# 实施计划：管理对话添加工作区

见 [功能文档·添加工作区](../functional/manager-task-mode.md#添加工作区)。

## 结论先行

管理端已有 `workspaceRegistry` 注入，登记工作区就是一次 `create(path)`。**不写新的持久化、不加 HTTP 路由、不改 harness 之外的任何包**。

## 三个决定

| 决定 | 取值 | 理由 |
|---|---|---|
| 目录不存在怎么办 | **创建**（mkdir -p）再登记 | 「在 /x/y 建个工作区」是最自然的说法；一次调用就该立起来。registry 自己的 `initializeDefault` 也这么做 |
| 相对路径 | 拒绝 | mkdir/realpath 都会按进程 cwd 解析，悄悄建错目录比报错更糟 |
| 标题 | 不传，用默认末段名 | `create(path, title?)` 的 `title` 上游正准备删（`packages/workspace/workspace/src/index.ts:266` TODO） |

## 任务

| # | 任务 | 出口 |
|---|---|---|
| T1 | `managerTools` 加 `manager_add_workspace({ path })`；`MANAGER_TOOLS` 白名单加该名 | 管理模式有、其他模式没有 |
| T2 | 校验：必须是绝对路径；目录必须存在且是目录 | 两种坏输入各自报明确的错 |
| T3 | 幂等：先 `resolveByPath`，已在册返回 `created: false` + 原 id | 重复添加不产生第二条登记 |
| T4 | `managerPrompt` 补一句「工作区不够时可以添加已存在的目录」 | 管理端知道有这个手段 |
| T5 | `tests/manager.host.spec.ts` 覆盖：能加、普通会话无此工具、重复幂等、相对路径拒绝、不存在拒绝 | 红→绿 |
| T6 | 功能文档已有；补人工测试用例 | 文档同步 |
| T7 | `pnpm run build:artifacts` + 3081 重启 + ego 实测 | 浏览器里真加出一个工作区 |

## 授权边界

`packages/session/session-manager/src/index.ts:186-200` 的 `install()`：工具只挂到 `role === 'manager'` 的 agent 作用域，并且 `tools.guard` 只放行 `MANAGER_TOOLS`。所以「只授权给管理模式」由现有机制保证，不需要新权限系统。

## 不做的

- 不做「新建目录并登记」。
- 不做重命名 / 删除工作区（UI 已有）。
- 不加 ADR：这是既有决策（管理端不做执行）的顺延。
