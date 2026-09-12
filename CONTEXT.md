# MyAI 工作区 — 任务编排域

本工作区的多会话任务编排语境：Manager 会话统一管理任务清单，按任务性质动态创建队长会话执行任务并回报完成情况。

## Language

**Manager 会话**:
持有任务清单唯一管理权的常驻会话，负责读取、分类、派发任务并验收队长的回报。
_Avoid_: 总管、调度器、captain

**管理模式**:
Manager 会话使用的预设，从全能模式扩展而来，额外具备任务清单管理与队长编排能力。
_Avoid_: Manager 预设、manager mode

**队长模式**:
队长的运行机制：工具行统挂管理模式预设，经 per-child toolFilter 裁出队长工具面，类别差异由章程承载（见 ADR-0003）。
_Avoid_: 队长预设、captain preset

**类别章程 (Charter)**:
随任务派发注入队长的类别职责说明，是类别差异的唯一载体。
_Avoid_: 系统提示词、persona

**形式核验 (Formal Check)**:
Manager 对队长回报的证据与产物做的不重做验证；通过即关单，不通过打回。
_Avoid_: 验收测试、QA

**终审 (Final Review)**:
用户对标记「需终审」的任务所做的完成确认；是此类任务关单前的最后一道门。
_Avoid_: 人工验收、审批

**队长 (Captain)**:
由 Manager 创建、负责实际执行某类任务并向 Manager 回报完成情况的会话。
_Avoid_: 队员、member、worker、agent

**队长类别 (Captain Category)**:
Manager 按任务性质动态划定的队长分类；每个类别对应一个常驻复用的队长。
_Avoid_: 类型、分组、角色

**任务清单 (Task List)**:
由插件服务托管的唯一任务事实源；写入权专属 Manager 与人类（GUI），队长只读自身任务并提交回报。
_Avoid_: 待办、todo、工单
