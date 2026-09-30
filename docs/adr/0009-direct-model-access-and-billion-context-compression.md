# 模型访问层直连上游，压缩权移交 billion-context

三条模型线（`deepseek-official`、`sensenova`、`step`）都经本机 headroom 代理接入：`:8787`、`:8788`、`:8789` 三个 systemd 用户单元，同一份 uv tool 安装（v0.39.1），状态落在 `~/.headroom`。这一层同时干了三件事——把 provider 的 `baseURL` 钉在本机、以 cache 模式压缩上下文、绕开它只放行 `/v1/chat/completions` 带来的协议限制（`~/.dsh/settings.yaml` 的 `llm-deepseek.protocol: chat-completions` 就是为它写的）。与此同时 SenseNova 上线了 OpenAI Responses 全兼容端点，实测 `POST https://token.sensenova.cn/v1/responses` 返回 200 与标准 Responses 结构。用户判定 headroom 这一层整体退场：拆掉它，模型线直连上游，压缩权交给 billion-context。

## Considered Options

- **保留 headroom、只换上游地址**：被否——用户要求彻底删除该层，且它的压缩与即将接入的 billion-context 职责重叠。
- **只停 unit、保留 uv tool 与状态目录**：被否——用户要求永久删除，不留回滚路径，`~/.headroom` 里那份压缩节省记录一并清掉。
- **让 `deepseek-official` 也走 Responses**：被否（能力不存在）。`llm-deepseek` 只实现 `chat-completions` 与 `messages` 两种协议（`packages/llm/llm-deepseek/src/config.ts:81`），没有 responses 分支；Responses 只能由 `llm-pi-ai` 提供（`api: openai-responses`，`packages/llm/llm-pi-ai/src/provider.ts:49`）。
- **`step` 线也改 Responses**：被否——上游没有 responses 端点，只能直连 chat-completions。
- **把默认模型迁到 token plan**：被否（用户决定）。默认仍是 `deepseek-official` / `deepseek-flash`，思考档位从 `max` 降到 `low`；token plan 作为可选线保留。
- **billion-context 走官方 npm 车道**（`dsh plugin --profile web add billion-context`）：被否——与 ADR-0007 的源码安装总纲冲突，且它的自更新会去触碰 pnpm 硬链接 store。改为 fork 上游 → `dsh-extensions/vendor/billion-context` 子模块 → 两个 profile `link:`。
- **保留非官方 selector、只调阈值**：被否——用户要求非官方压缩插件删除；且它在挂载时重写预设组成，会覆盖任何手改的预设行。
- **把官方压缩整组 `disabled: true`**：被否。`ctx.compaction` 服务随之消失，`/compact`、laya-router 的 `compactIfNeeded` 调用、UI 压缩入口都要一并处置；改为只关自动压缩（`auto: false`），手动压缩留在原地。
- **给 billion-context 钉固定端口 + `/bili/` 前缀**：暂不作为首选。车道自身用 OS 随机端口（`port: 0`），钉端口要额外起一个常驻单元；先按原生 fetch 车道接并实测流量，未命中再切。

## Consequences

- headroom 三个 unit、`default.target.wants` 软链、`~/.local/bin/headroom{, -cache-ttl}`、uv tool（578M）、`~/.headroom`（58M）以及 prod 与 dev 两份 composition 里的 `mcp-headroom` 段全部删除；`settings.yaml` 三处 `baseURL` 改为直连。
- `deepseek-official` 删掉 `baseURL` 覆盖，回落插件默认 `https://api.deepseek.com`（`config.ts:104`）；`protocol` 保持 `chat-completions`，不顺手改协议。默认模型仍为 `deepseek-official` / `deepseek-flash`，`reasoningEffort` 由 `max` 改为 `low`。
- `sensenova` 改用 `api: openai-responses` + `baseURL: https://token.sensenova.cn/v1`，只注册 `deepseek-flash` 与 `sensenova-6.8-flash-lite`。**官方映射表里 DeepSeek V4.1 Flash 的 model id 就是 `deepseek-flash`**；沿用旧配置里的 `deepseek-v4.1-flash` 会 403「model is not available in the current token plan」（实测），而 `deepseek-flash` 实测 200。此前 `subagent-model-selection` 里那条 `sensenova/deepseek-v4-flash` 是死引用，一并移除。`step` 直连 `https://api.stepfun.com/step_plan/v1`。
- 判断层（`dsh-laya-router`）自带的默认路由表引用的正是那个不存在的 id（`sensenova/deepseek-v4.1-flash`），而 headless 等 profile 不给覆盖——已就地改成 `deepseek-flash` 并重建（55 个单测通过），否则路由到该档会稳定失败。
- 压缩权归 `bili-native`：官方压缩栈留在预设里但只做手动压缩；`dsh-context-compression-selector` 及其 `context-compression` settings 命名空间一并删除。billion-context 提供的模型工具为 `compress` / `decompress` / `search_context` / `acp_status` / `acp_cache`，斜杠命令为 `/acp` 与 `/acp-cache`。
- **两处上游盲区（实证）**，决定了实现顺序：① billion-context 自带的 `dsh.bundle.patch.yml` 里 `compaction-basic: auto: false` 打的是宿主树那条已被 `packages/bundle/web-app/cordis.patch.yml:467` 设为 `disabled: true` 的行，真正生效的预设行（`~/.dsh/.agent-presets/{omni,manager}/agent.cordis.yml`）收不到——patch 是按 id 整体替换、未知 id 只告警跳过，而预设是独立 `Include` 树；② selector 的 `presetOverlay` 在挂载时重写预设（strip 掉压缩行、按 `thresholdRatio: 0.7` 重新插入）。**所以「关自动压缩」必须在预设文件里改，且必须发生在删除 selector 之后。**
- 一条未证事实压在路径上：上游记有「profile 安装车道下 dsh 的某些 `llm-pi-ai` 传输零流量」（#1158），而 SenseNova 正好骑在这一层。接入后必须先量一次请求是否真的到达代理（`/__bili/stats` 与 `bili.log`），未命中则改走固定端口 + `/bili/` 前缀。
- ADR-0007 的张力如实记录、不改写历史：那份 ADR 以「删除 3 个 npm 交付插件」收尾并声明净损失上下文压缩档位选择器，而该插件随后又以 npm 交付装回（`~/.dsh` 提交 `35ea495`）。本次按「非官方压缩插件删除、billion-context 例外保留但走源码安装」处理。

## 实施结果（2026-09-30 当日完成，证据同段记录）

- **headroom 已永久拆除**：三个 unit 与 `default.target.wants` 软链 stop + disable + 删文件，uv tool（含 `headroom` / `headroom-cache-ttl` 两个可执行）卸载，`~/.headroom`（58M，含 savings 记录）与 uv tool 目录（578M）直接 `rm -rf`，不留档。复核：`list-unit-files 'headroom*'` 为 0、无进程、8787/8788/8789 无监听、PATH 无 `headroom`，两份 settings 与两份 composition 里只剩解释性注释。
- **两处上游盲区都被实证补上**：预设里给 `compaction-basic` 加 `config: {auto: false}`（bili 自带的 patch 那条确为静默 no-op）；selector 先删后改预设，顺序不可换。
- **fork 的两处本地改动**（`xgx1/billion-context`，分支 `2026-09-30_compat-dropfields`，均基于 tag `v0.1.174`）：
  - `30fbf27e` `compat.dropFields`：pi-ai 只要带思考档位就必发 `reasoning.summary`，SenseNova 的 Responses 严格 schema 直接 400（`json: unknown field "summary"`）。逐字段实测确认 `include` / `prompt_cache_key` / `store` 全 200、只有 `summary` 被拒；改动在 `compat.roles` 同一个最终转发边界上按 provider 删字段（并进 `wireTransform`，压缩重试的重发体一致），默认路径 byte-for-byte。配置：`~/.config/billion-context/billion-context.json` 的 `providers["https://token.sensenova.cn/v1"].compat.dropFields: ["reasoning.summary"]`。已提上游 issue #1757 请 owner 裁定配置形状。
  - `141d412b` `BILI_NATIVE_DSH_LANE`：attach 兼容判定只比 lane，而 lane 硬编码 `"dsh"`，同机 prod + dev 会互相 attach 到同一个代理；代理生命周期绑在拉起它的 dsh 进程（父进程 watchdog）上，任一实例重启就把另一方的模型链路带走且无回退。改为 lane 读环境变量（未设仍是 `dsh`），两个启动脚本各导出自己的 lane。重启后实测生效：生产日志 `native-attach: skip http://127.0.0.1:18787 (pid 248254): incompatible (lane-mismatch)`，实例表 `dsh-dev`→18787、`dsh-prod`→18788。
- **实测结论**：① Responses 线在生产通过——临时把默认模型指到 `sensenova/deepseek-flash` 跑一次性，返回「好」，bili 日志 `[compat] dropped reasoning.summary per compat.dropFields` + `forward POST → .../v1/responses`，随后立即还原 settings；② 默认线正常提示通过，且本对话（`session-7319e909`）全程经 bili 直连 `https://api.deepseek.com/chat/completions`、缓存命中 100%；③ 上游 #1158（pi-ai 传输零流量）在本机不成立。
- **实测发现一个待定缺陷（记录在案，未上报）**：headless 一次性跑「退化提示」（如「只回一个字：好」）时，`bili` 的 degenerate-turn 守卫会把它拦成 in-band error（`degenerate terminal turn (no usable output); retrying once with a continuation nudge` → `again after the retry; emitting an in-band error`，对应 #673 / #732 / #821 / #870）。A/B 对照：`BILI_NATIVE_DSH` 在 → 该提示稳定失败，`BILI_NATIVE_DSH=0` → 同提示返回「好」；正常提示（如「用一句话解释什么是二分查找」）与正常多轮 GUI 会话在两处都不受影响。是否上报上游待用户裁定。
