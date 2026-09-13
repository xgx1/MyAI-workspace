# 删除 3 个 npm 交付的插件，而非改为源码安装

生产 profile 的 9 个依赖中，6 个是 `link:` 源码安装、3 个走 npm registry：`@nanmicoder/dsh-agent-teams@0.1.17`、`dsh-context-compression-selector@0.1.0`、`dsh-lan-access@^0.1.1`。在"任何内容都应当源码安装"的总纲下，这三者的上游经实测**全部可 clone**（`git ls-remote` 三次探测均 exit=0），因此「clone 上游 → 改 `link:`」在技术上完全可行、且不损失任何能力。用户判定这三项能力不需要，决定**直接删除**。

## Considered Options

- **改为源码安装**（clone 上游 + `link:`）：机械上可行且零能力损失，是 agent 的推荐；被否——用户判定不需要这三项能力。
- **保留 npm 交付**：被否——与"源码安装"总纲冲突；且 `dsh-lan-access` 声明的是浮动范围 `^0.1.1`（实际装了 0.1.3），版本靠 lockfile 而非意图钉住。

## Consequences

- **净损失三项能力**：AgentTeams 多智能体系统（`agent_teams_*` 整套工具）、局域网访问（GUI 绑定 `0.0.0.0`）、上下文压缩档位选择器。技能 `agent-teams-orchestration-pitfalls` 随之失去对应工具，退化为纯知识文档。
- profile 依赖 9→6、bundles 11→8；`node_modules` 从 18M 降到约 0.2M——那 18M 里约 17.7M 正是这三个包的传递树（`dsh-context-compression-selector-runtime` 独占 13M）。
- 执行顺序固定为**最后一步**，随后重启 `dsh-web.service`（重启会中断当前对话，已获用户授权）。
- 此项推翻 2026-09-13「把 MemOS 与 agent-teams 从 `link:` 改为 npm 交付」的一半——当时为瘦身工作区而改，如今三个包整体退场。
