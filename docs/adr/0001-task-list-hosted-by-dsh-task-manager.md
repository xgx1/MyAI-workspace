# 任务清单由 dsh-task-manager 插件托管，Manager 与人类双写权

多会话任务编排需要唯一任务事实源。决定扩展现有 `dsh-extensions/plugins/dsh-task-manager`（而非新建插件或改用 `.scratch/` 文件约定）：写工具只编入管理模式预设、GUI 人类操作保留，队长仅获得「回报自身任务」的受限接口。选插件而非本地文件，是因为任务要被 GUI 与多个会话共同消费；不选 Manager 独写，是因为人类是清单的最终所有者，不应被自己定的规矩锁在门外。

## Considered Options

- `.scratch/` 本地工单约定（Matt Pocock skills）：被否——与「任务清单只由 Manager 管理」的独占性冲突，且没有服务化读写面。
- 全新任务插件：被否——dsh-task-manager 已有 GUI、6 状态机与落盘，重写没有增量价值。
- Manager 独写（GUI 只读）：被否——用户双入口（GUI 建单 + 口头吩咐 Manager）是明确需求。
