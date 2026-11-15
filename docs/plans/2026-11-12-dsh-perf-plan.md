# DSH 编译/运行提速方案（实测基线 + 可裁剪改动）

日期：2026-11-12 · 落点：deepseek-harness-dev（分支 dev），验证走 3081，动生产 3080 另议。

## 1. 实测基线（本机 32 核 / 62 GB）

| 场景 | 命令 | 实测 |
|---|---|---|
| 空转构建（无源码改动） | pnpm run build:artifacts | 35.7 s（门 31.6 s） |
| 改一个 client 叶子文件后 | 同上 | ≈33–35 s（TS 编译只花 0.6 s，其余全是打包） |
| 全量 host 编译（--force） | tsc -b tsconfig.host.json --force | >112 s 后 OOM 崩（4 GB 堆；脚本里才给 8 GB） |
| Web 未压缩体积 | apps/web/dist | index 977 KB + vendor 741 KB（合计 gzip 299 KB）+ sourcemap 8.1 MB |
| Web 冷启动到打印 URL | dsh --profile web --port 3099 --no-open | 12.6 s |
| 会话存储 | ~/.dsh/sessions | 1.8 GB / 1409 个 .jsonl.zstd / 36 个工作区 |
| 每会话固定前缀 | 会话日志 system/message 事件 | 106 KB（含工具 schema）；技能目录 ≈92 KB；AGENTS 注入 45 KB |

空转 35.7 s 的分步耗时（8 个门并行，worker 上限 12/32）：

    native addon 0.68s | Host Typert 6.87s | host compiler 0.73s | Host bundle 6.81s
    Desktop bundle 4.27s | client compiler 0.67s | Client bundle 5.91s | Web build 6.29s

结论：TS 增量编译早已不是瓶颈（0.7 s），时间全在“每次必跑”的 Typert 生成、三处 tsdown 打包和 Web 打包上；冷构建卡在单进程 tsc 串行 + 堆内存。

## 2. 编译侧

### C1 拆门：web 开发不构建 desktop，不动 client 就不打 web（P0）
- 改哪里：scripts/build.ts 加 --scope dev（host 编译 + host bundle + web，跳过 desktop）与 --skip-web；scripts/compile-referenced-projects.ts 的 libraryBuildSteps 已按 faces 分组，加一个 web-dev 分支。
- 预期：空转 35.7 s → ≈18 s；只改 host 代码再省 web 的 6.3 s。
- 风险：低。desktop 只在打包桌面端时需要。

### C2 Typert / 打包按输入哈希跳过（P0，收益最大）
- 现状：Host Typert 6.9 s、三个 bundle 共 17 s，每次无条件重跑。
- 改法：门执行前对 packages/*/*/src 的 mtime+size 清单算哈希，存 .cache/build/<gate>.hash，未变则跳过该门（tsdown 没有跨进程增量，这层只能自己加）。
- 预期：空转 35.7 s → ≈3–5 s。
- 风险：中（判断错会静默用旧产物）。加 --no-cache 逃生开关，只对 dev 实例启用，CI/正式构建保持全量。

### C3 常驻 watch 替代“改一次跑一次”（P1）
- 改法：dev:web 并行拉起 tsc -b --watch（host/client）+ tsdown --watch（host/client）+ vite build --watch；build:artifacts 只在冷启动跑。
- 预期：单次改动反馈 < 2 s（现在 35 s）。
- 风险：低—中（watch 进程吃内存，由 dev 单元托管、退出即收）。

### C4 本地 typecheck 换引擎（P1）
- 现状：pnpm typecheck 走 tsc -b，300+ 工程单线程，冷跑分分钟，4 GB 堆就 OOM。
- 改法：类型检查改 tsgo（@typescript/native-preview）做 --noEmit，emit 仍用 tsc；所有 tsc 调用补 --max-old-space-size=8192。
- 预期：类型检查 5–10×；冷构建不再 OOM。
- 风险：中（原生预览版对 project references 的支持要先在分支上跑通；跑不通就只当快速预检）。

### C5 本地 emit 允许 --noCheck（P2）
- 仓库已有该模式（CompilationMode 的 benchmark-emit 分支就是 tsc -b --noCheck），只是没给开发用。
- 预期：改核心包（级联重建）从十几秒降到 1–2 s。
- 风险：中（会漏类型错误到运行期，只许本地 dev 用）。

### C6 Web 产物（P2）
- 开发构建关 sourcemap（apps/web/vite.config.ts:181 恒 true，每次写 8.1 MB），生产保留；首屏 1.7 MB 未压缩可再按路由切。
- 预期：Web 门 6.3 s → ≈5 s，dist 22 MB → 14 MB。

## 3. 运行侧

### R1 每会话前缀瘦身（P0，收益最大）
- 现状：system/message 106 KB + 技能目录 92 KB + AGENTS 45 KB ≈ 60 k tokens 起步，每会话付一次。
- 改法（按性价比）：
  1. 技能目录改检索式：175 个 allow 技能全量带描述注入（packages/skill/tool-skill/src/index.ts:264 的 <available_skills>）。改成「名字 + 一行触发词」或只留 skill 工具按需搜 → 省 ~20 k tokens。
  2. 收紧 ~/.dsh/skill-filter.yaml：UE 类 99 个已按项目分层，个人层还能再砍。
  3. AGENTS 注入：四份共 45 KB，合并成一页「规则索引 + 指针」，细节留仓库文件按需读。
- 验证：新会话里量 system/message 字节数 + 首轮 usage.input_tokens。

### R2 工具 schema 按需挂载（P0）
- 现状：单会话 system prompt 塞几十个工具完整 schema（ego 一族 30 个、openviking 一批、cbm/zvecgrep 常驻）。
- 改法：MCP 默认不挂、由 preset 按会话挂（mcp-ue/mcp-unity/mcp-rea 已是 disabled: true，cbm/zvecgrep/openviking/ego 仍常驻）；ego/office 这类低频工具同样改成 preset 挂。
- 注意：2026-11-11 用 overlay 一次关掉 cbm+zvecgrep+unity，进程 4.3 s 就退（原因未查）——逐个关、每次验启动，别一把梭。

### R3 启动 12.6 s（P0/P1）
- 现状：MCP 在 Host 启动时就 spawn（unity 的 uvx + FastMCP banner 正好出现在打印 URL 前），Python 侧启动就秒级。
- 改法：① 启动脚本加 NODE_COMPILE_CACHE=$HOME/.cache/dsh-node（Node 26 原生字节码缓存，仓库 CI 已在用，本地没开）；② MCP 首连放后台不阻塞启动（已有 failOnStartupError: false，但没有「后台连」语义，看 packages/mcp/mcp-client/src/connection.ts）；③ unity/ue 这类「编辑器不在就没用」的服务彻底移出 profile 常驻。
- 预期：12.6 s → 6–8 s。

### R4 会话存储（P1）
- 现状：1.8 GB / 1409 个 zstd 日志，最大工作区 379 MB，打开会话要整份解码。
- 改法：90 天前 session 归档到备份盘（保留索引）；启用 session-projection-cache（profile 里没看到启用）。

### R5 客户端（P2）
- 首屏 1.7 MB JS（gzip 299 KB）已算合理；真要提速：生产关 sourcemap（同 C6）、确认静态服务开了 gzip/brotli、大组件按路由懒加载。

### R6 压缩参数（P2，后置）
- compaction-basic 的 thresholdRatio/retention 与 tool-result-pruner 预算决定长会话重复 token；等 R1/R2 落地后按 /route stats 和 usage 再调。

## 4. 落地顺序
1. C2 + C1（空转 35.7 s → 3–5 s，改动日 <18 s）：只动 scripts/，dev 上验一轮。
2. R1 + R2 + R3：以配置为主，随时回滚；每步量 system/message 字节与启动秒数。
3. C3（watch）：C1/C2 稳定后接进 dev:web。
4. C4/C5（tsgo / --noCheck）：单开分支验证，跑不通就退回。
5. C6、R4、R5、R6 有余力再做。

## 5. 不建议
- 引 turbo/nx 做缓存：tsc 增量 + 20 行哈希缓存就够。
- 把 emit 全换 esbuild/swc：verbatimModuleSyntax、project references、declaration 输出都要重做，风险远大于收益。
- 在生产检出 deepseek-harness 上试这些改动：按 AGENTS 只在 dev worktree 做，验证完再谈上生产。
