# 技能按上游仓库分组为独立仓；fork 后以本地改编版为主内容

`~/.dsh/skills/` 的 274 个技能此前平铺在 `dsh-extensions/skills/` 下，看不出任何一项来自哪里、能否更新。侦察确认它们分属**约 14 个上游仓库 + 约 85 个本机自写**（另有 4 个来源不明）。决定：按上游仓库分组，每组一个独立仓（GitHub 公开 fork 上游），挂在 `dsh-extensions/skills/<上游仓库名>/` 作为子模块；无上游的归入自研组，并可按主题再分。**fork 之后以本地改编版作为主内容提交，上游只作祖先与对照。**

## Considered Options

- **保持平铺**：被否——这正是要解决的问题。
- **新建私有仓 + `upstream` 远端（不 fork）**：功能与 fork 等价且不产生公开条目，是 agent 的推荐；用户选择公开 fork，以体现"这是我的仓"。
- **直接用上游版本替换本地**：被否——本地普遍改过（`ue-*` → `unreal-*` 改名、frontmatter 中文化、描述缩短），个别是重度再创作（superpowers 派生的中文流程套件，其本地文件自己就写着"superpowers:subagent-driven-development 的脚本全部不可用"）。替换等于丢失全部适配。
- **自研技能全塞进一个仓**：被否——约 85 个技能一个仓，任何改动都产生巨大 diff，且四类主题（UE 项目实践 / 开发流程 / 本机系统 / DSH 运维）没有共同演进理由。

## Consequences

- fork 的 diff 会很大，且 `git pull upstream` 会**按设计**产生冲突——不得盲目 merge 上游覆盖本地。上游更新的正确用法是"取回参考、人工判断是否吸收"。
- **来源判据变更**：此后判断一个技能是否自研，以 `agents/openai.yaml`（本机 36 个技能携带）与残存的 `license:` / `compatibility:` 键为准；**`author: Sx` 与中文 frontmatter 不再是"自研"的证据**——侦察已证明这两者是本地化层批量盖上的痕迹（`author: Sx` 被盖给 33 个技能，其中若干可证为上游派生）。
- `install-skill.sh` 必须从"扫一层目录"改为"扫两层（组 / 技能）"，并保证只软链技能目录、不跨越子模块边界复制内容。（**2026-09-13 更新**：改为按 `SKILL.md` 递归发现——见文末。）

## 更新 2026-09-13：组内结构与上游对齐（改写了上面的「fork 后以本地改编版为主内容」）

**问题**：为把技能装进运行时，`install-skill.sh` 只认「组 / 技能」两级，各组于是把上游的嵌套技能目录（`skills/<名>/`、`.agents/skills/<名>/`、`skills/engineering/<名>/`、`plugins/<插件>/skills/<名>/`）**拍平到组根**，并删掉上游其余文件。结果是每个 fork 的目录结构与文件数都与上游对不上（例：dotnet-skills 上游 2642 文件 / 本机 251；obra-superpowers 上游 195 / 本机 22），`git pull upstream` 无从下手。

**决定**：**组内目录与上游一一对应**。每个 fork 重建为「上游最新树 + 本地改动移植到对应文件」：

- 技能目录按**目录名**匹配上游；改名过的组按前缀归一化匹配（`unreal-` ↔ `ue-` ↔ `ue5-`，用于 quodsoler / rider / sipherxyz / unrealxu）。
- 我们的内容覆盖到上游对应文件（上游目录里我们没动过的文件保留）；上游独有的技能与文件全部收进来。
- 匹配不上的是本地独有技能，放到上游的主技能根下；组 README 与上游 README 同名冲突时，我们的改名为 `README.dsh-local.md`。
- 匹配靠的是**目录名**，所以改名类本地改动的载体是 frontmatter 的 `name:`——技能名不随上游目录名变，引用不受影响。

**`install-skill.sh` 随之改造**：从「扫两层」改为**按 `SKILL.md` 递归发现**（深度 ≤ 6），跳过 `tests/`/`fixtures/`/`examples/`/`sample*/` 噪音；同一技能被多份副本携带时（上游常给多个 harness 各放一份）取**路径最浅**的那份，于是 `skills/`、`.agents/skills/` 优先于 `.openclaw/skills/` 之类的分发副本；技能名优先取 frontmatter 的 `name:`，没有才用目录名。

**Consequences（更新）**

- 每个 fork 现在有 `upstream` 远端，`git diff upstream/<分支>` 就是「本机改了什么」的权威答案；`git fetch upstream && git merge` 恢复为**可用**操作（上游文件都在，不再是删除态）。
- 组内多出来的东西只剩两类：本地独有技能，与 `README.dsh-local.md`。
- 代价：fork 体积与上游同量级（dotnet-skills 2642 文件），`git status`/diff 在那些大组里更慢。
- **执行记录**：10 个有上游的组（dotnet / epicgames / kepano / mattpocock / obra / quodsoler / rider / sipherxyz / unrealxu / dietrichgebert-ponytail）全部对齐并推送，每个组的「缺上游文件」数为 0；安装器发现 307 个技能（对齐前 245）。
- 全库重名冲突两处，靠「先到先得」解决：`unreal-mcp`（epicgames 胜出，sipherxyz 的副本被跳过）、ponytail 的 6 个技能（取上游 `skills/` 而非 `.openclaw/skills/`）。
