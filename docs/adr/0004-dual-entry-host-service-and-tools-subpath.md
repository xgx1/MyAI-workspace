# dsh-task-manager 双入口：host 服务入口 + tools-only 子路径入口

管理模式预设行引用整包 `dsh-task-manager` 时与 web profile 的 host bundle 实例碰撞：`taskManager` 服务重复注册、HTTP 路由重复挂载（standingKeyFor 实测拒绝，loader leakedServices 审计同源）；而 host 平面挂载下 per-session 工具注册静默失败（tm_diag 实证 task_* 全false，对照 agent_teams_* 同机制成功）。决定拆双入口：主入口维持 host bundle（taskManager 服务 + 路由 + 持久层）；新增 `"./tools"` 子路径入口，仅向调用方会话作用域注册 7 个 `task_*` 工具、消费 `ctx.get('taskManager')`，不 provide 服务、不挂路由（与 tool-todo 同构）；管理模式预设的工具行引用子路径。

## Consequences

- 严禁 bundle 侧与预设侧双注册同名工具（两处同时启用 = 同名工具冲突）。
- 会话能否见到 task_* 工具取决于其预设是否挂 `dsh-task-manager/tools` 行；host bundle 自身不产生会话工具。
- 身份校验线不变：工具经 `ctx.get('taskManager')` 触达服务端校验，会话身份来自 `exec.agent`。
