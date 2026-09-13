# MyAI 工作区

本工作区是若干独立仓库的宿主与编排层：既定义多会话任务编排语境，也定义这些仓库之间固定的拓扑关系。

## Language

### 任务编排

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

### 仓库拓扑

**子仓库 (Sub-repo)**:
MyAI 用 git submodule 管理的顶层仓库——`dsh-extensions`、`deepseek-harness`、`update-app`。层级固定两层，不下探第三层（见 ADR-0005）。
_Avoid_: 子模块、嵌套仓库

**自研插件 (Own Plugin)**:
`dsh-extensions/plugins/<名字>/` 下、受 dsh-extensions 版本控制的插件。
_Avoid_: 本地插件、自制插件

**第三方插件 (Vendored Plugin)**:
`dsh-extensions/vendor/<名字>/` 下的上游克隆，各自带独立 `.git` 与远端，作为 dsh-extensions 的子模块（见 ADR-0005）。
_Avoid_: 外部插件、依赖插件

**技能分组仓 (Skill Group Repo)**:
`dsh-extensions/skills/<上游仓库名>/`——某个上游技能集合的 fork，一个上游仓库一个分组仓，作为 dsh-extensions 的子模块。
_Avoid_: 技能包、技能目录

**自研技能组 (Self-authored Group)**:
无上游的技能分组仓，收纳本机自写的技能，按主题再分（见 ADR-0006）。
_Avoid_: 自建技能、私有技能

**受管技能 (Managed Skill)**:
由 `install-skill.sh` 软链进 `~/.dsh/skills/` 的技能；运行时读到的永远是分组仓里的那一份，不存在副本。
_Avoid_: 已安装技能、已部署技能

**上游 (Upstream)**:
技能分组仓与第三方插件的原始来源仓库。只作**祖先与对照**，不作覆盖源——本地改编版是主内容，`git pull upstream` 按设计会冲突（见 ADR-0006）。
_Avoid_: 源仓库、原始仓库
