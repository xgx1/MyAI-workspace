# 用本地 Laya 做逐轮模型路由、档位映射与主动压缩

每个用户轮次开始时，判断层（`dsh-laya-router`）把**本对话全部用户消息**交给本地 Laya 决策模型（`convaiinnovations/laya`，跑在 RX 7900 GRE 上），得到三个判断——任务难度、时间预算、是否仍在原任务上——据此在四个已配置模型里选一个、映射思考档位，并在判定「换任务」且上下文占用超过阈值时先压缩再继续。判断只吃**用户消息**，不吃助手输出与工具结果；「有没有额度、provider 此刻健不健康」由插件持有，不问 Laya。

路由表：官方 `deepseek-official/deepseek-flash`（难且人在等）· `md/deepseek-ai/DeepSeek-V4.1-Flash`（难且能等／跨天，额度按天刷新）· `sensenova/deepseek-v4.1-flash`（难但不追求速度）· `sensenova/sensenova-6.8-flash-lite`（简单且可等）。

## Considered Options

- **让 Laya 直接输出模型名**：被否。它看不到额度、provider 可用性与成本，模型名单一变还要重问；改成只判任务属性、路由表归插件。
- **把「还有钱」也做成一个问题**：被否。Laya 没有任何外部状态，问了只会得到编造的概率。
- **把整段用户消息原样喂给 Laya**：被否（实测）。english 检查点给 state 的预算是 320 token、multilingual 768；超出时它**保留开头、丢弃结尾**，等于永远看不到最新那条。判断状态改为插件确定性组装：任务起点 + 最近若干条 + 省略标记，裁剪事实写进决策记录。
- **沿用裸 `noul` 问「是否还在原任务上」**：被否（上游实测）。不给 criteria 的 noul 会被渲染成固定 false/true 对并**恒定输出**（四十道平衡题 40/40，中英文皆然）；全部判据改用 `choice` + criteria。
- **不指定 `lang`，让它自己检测**：被否（实测）。检测器只认 en/fr/de/es/pt/it/nl，中文被塞给 english 检查点且返回不可用结果；改为只预加载 multilingual、每次请求显式传 `lang`。
- **fork `dsh-jev` 换后端**：被否。它的六个模块（loop-guard / safety-guard / tool-pruner / skill-router / result-shaper / tools）一个都不用，而模型路由它没有；只借它的做法（状态栏开关、stats 看板、calibration 文档）。
- **改 preset 把插件挂进 agent 作用域**：不需要。`dsh-scope` 的规则是「监听器挂在祖先作用域也能收到后代事件」，所以 profile 级 bundle 行即可收到 `agent/request`——`dsh-llm-retry-schedule` 钩 `agent/request-error` 是同款先例；这也避免了 dev/prod 预设分叉。

## Consequences

- 路由是**逐轮**的：在 `agent/request` 的 `step === 1` 应用。换模型不开新的 request series，但前缀缓存在新路由上是冷的。
- 思考档位必须**每轮交完整决策**：显式档位会写进 `request/header` 并持续生效，不显式清除就会粘住后面所有 step；目标模型不支持的档位是 loud 失败（`UNSUPPORTED_REASONING_EFFORT`，既不 clamp 也不降级），所以只对声明了档位的 provider 传值，其余显式清除。
- 换模型时插件必须自己追加一条 logged 通知：原生的 `[model changed: …]` 只由 `installModelSelection` 产生，纯 `agent/request` 换模型不会触发它，否则模型会看到别的模型产出的历史而无标记。
- 压缩走 `ctx.compaction.compactIfNeeded(agent, 'context-overflow', signal)`，在 `agent/pre-step` 调用对同一 step 生效；失败（busy／无可压历史）静默降级并记录，绝不拖垮这一轮。
- **先影子后生效**：`mode: shadow | live`，默认 shadow。低置信（< 阈值）与「文本没说」走同一条路——不改动，除非配置了「未标注默认档」（默认 `md`）。
- 新增一个运行期依赖：`laya-sidecar.service`（`:8083`）。侧车不可用时什么都不改，只记录。
- 已知取舍：判断状态被裁剪时，答案只基于幸存的前缀；记录里带 `elided` 字段，便于事后判断「这次错是不是因为信息被剪了」。Laya 基础检查点在它自己的 typed-decisions 基准上接近瞎猜，所以影子期的对表数据是开 live 的前提。
