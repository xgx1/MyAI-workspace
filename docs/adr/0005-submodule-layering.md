# MyAI 用子模块管理两层仓库，不再用忽略式嵌套

工作区此前用 `.gitignore` 排除嵌套的独立仓库（`dsh-extensions/`、`deepseek-harness/` 等），父仓不记录子仓处于哪个提交——"工作区资产版本控制"因此名不副实。决定改为 git submodule，层级固定为**两层**：MyAI 直接管 3 个顶层仓（`dsh-extensions`、`deepseek-harness`、`update-app`），而 `dsh-extensions` 用同一机制管它的两个分组容器——`vendor/`（第三方插件克隆）与 `skills/`（技能分组仓）。不再下探第三层。

## Considered Options

- **保持忽略式嵌套（现状）**：被否——父仓无法记录子仓提交，"版本控制工作区资产"只剩一半语义。
- **把技能分组仓也挂到 MyAI 下**（与 `dsh-extensions` 平级）：被否——MyAI 会直接管约 19 个子模块，且技能源与它的宿主仓被拆到两个不同的父仓下。
- **两级以上递归子模块**：被否——git 对递归子模块的操作极其繁琐，收益为零。

## Consequences

- 子仓每次提交后需在父仓更新指针，否则父仓长期显示 dirty。**这是本方案的固定成本**，不是可以"以后再说"的收尾动作；人与 agent 都必须把它编进提交流程。
- `vendor/` 与 `skills/` 从此**不再被 `.gitignore` 忽略**——原有的忽略条目要转入 `.gitmodules`，这是对 2026-09-13 那次「vendor/ 必须被忽略以免 `git add -A` 记成 gitlink」决定的**反向修订**：当时选忽略是因为没有建立子模块纪律，现在改用显式 submodule 来正面解决同一个问题。
