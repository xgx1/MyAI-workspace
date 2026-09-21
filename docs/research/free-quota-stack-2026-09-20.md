# 可持续免费额度作战表（2026-09-20）

> **筛选口径**：只收「**会刷新**」的免费额度——每日或每月重置、额度内 $0。**排除**新用户一次性赠送、限时活动、无 key 玩具站、社区中转站。
> 姊妹文档：全量清单 [free-llm-api-inventory-2026-09-20.md](./free-llm-api-inventory-2026-09-20.md)。
> 所有额度均为 2026-09-20 快照，**以自己账号的控制台为准**。

## 0. 为什么这个筛选口径是对的

一次性赠送（百炼 100 万/90 天、Kimi 15 元/3 月、Scaleway 100 万、Cerebras $5）**用完就没了**，只能做评估，不能做架构依赖。真正能撑长期使用的是两类：

| 类型 | 机制 | 会不会耗尽 | 典型 |
|---|---|---|---|
| **A. 刷新额度** | 每日/每月重置的配额 | 单日会耗尽，**次日恢复** | Gemini、Groq、Cloudflare、GitHub Models、OpenRouter |
| **B. 永久免费模型** | 定价恒为 $0，限的是 RPM/并发 | **永不耗尽**，但吞吐受限 | GLM-4.7-Flash、ERNIE-Speed、Spark Lite |

**A 撑量、B 保底**——B 类虽然没有"刷新"概念，但它永远不会让你彻底断供，实际上比 A 更适合当降级终点。下面两节分开列。

---

## 1. 每天到底能白跑多少 token（可算实数的部分）

多数平台只公布「请求数/日」，不公布 token 量。**Cloudflare Workers AI 是唯一公布 per-model Neuron 单价的**，因此可以算出精确的每日 token 上限。

`免费额度 = 10,000 Neurons/日`（Free 与 Paid 计划都有，每日 00:00 UTC 重置）

| 模型 | 输入 token/日 | 输出 token/日 | 备注 |
|---|---:|---:|---|
| `@cf/ibm-granite/granite-4.0-h-micro` | **6,485K** | 984K | 额度最大，但模型很弱 |
| `@cf/llama-3.1-8b-instruct-fp8-fast` | 2,428K | 287K | 通用 8B，最实用的量 |
| `@cf/qwen/qwen3-30b-a3b-fp8` | 2,162K | 328K | **MoE 30B，性价比最高** |
| `@cf/zai-org/glm-4.7-flash` | 1,818K | 275K | **与 Z.ai 免费版同款模型** |
| `@cf/google/gemma-4-26b-a4b-it` | 1,100K | 367K | 多模态 |
| `@cf/openai/gpt-oss-20b` | 550K | 367K | |
| `@cf/llama-3.3-70b-instruct-fp8-fast` | 375K | 49K | 70B 输出很贵 |
| `@cf/openai/gpt-oss-120b` | 314K | 147K | |
| `@cf/moonshotai/kimi-k2.6` | 116K | 28K | 大模型吃额度快 |

**同模型横向对比（gpt-oss-120b）**：
- Cloudflare：**输入 314K + 输出 147K** token/日，无公开 RPM 限制
- Groq：**总计 200K** token/日（TPD 硬顶），另 1,000 RPD / 30 RPM

→ **Cloudflare 免费档在 token 量上普遍优于 Groq**，且条款最干净（官方明确不训练、不改进、不外泄）。代价是没有 Groq 快，且大模型吃额度极快。

---

## 2. 每日刷新额度（A 类）

| 平台 | 刷新 | 额度 | 折算量 | 需卡 | 数据条款 | base_url |
|---|---|---|---|---|---|---|
| **Cloudflare Workers AI** | 00:00 UTC | 10,000 Neurons | 见上表，最高 ~6.5M 输入 token | 否 | ✅ 不训练 | `https://api.cloudflare.com/client/v4/accounts/{acct}/ai/v1` |
| **Groq** | 日 | `gpt-oss-120b` 30 RPM / 1,000 RPD / **200K TPD**；Whisper 2,000 RPD | 200K token | 否 | ✅ 默认不留存，可开 ZDR | `https://api.groq.com/openai/v1` |
| **Google AI Studio** | 太平洋午夜 | Gemma 系 **14,400 RPD** / 30 RPM / 16K TPM；Flash-Lite 500 RPD；Flash 20 RPD | Gemma 可做到千万级 token | 否 | ❌ 明示用于改进产品 | `https://generativelanguage.googleapis.com/v1beta/openai/` |
| **GitHub Models** | 日 | Low 15 RPM /**150 RPD**；High 10 RPM / 50 RPD；单请求 8K in + 4K out | 上限约 1.2M 输入 token | 否 | ⚠️ 个人档可能用于训练（可退出） | `https://models.github.ai/inference` |
| **OpenRouter `:free`** | UTC 日 | **50 RPD**；🟡 累计充值 ≥$10 → **1,000 RPD** | 取决于模型上下文 | 否 | ⚠️ 免费变体可能用于训练 | `https://openrouter.ai/api/v1` |
| **SambaNova Cloud** | 日 | 各模型 **20 RPM / 20 RPD / 200K TPD** | 200K token（RPD 仅 20，很紧） | 否 | 未明示 | `https://api.sambanova.ai/v1` |
| **NVIDIA NIM** | 日 | 官方**不公开**，按模型浮动；社区观测 ~40 RPM | 未知 | 否 | ⚠️ 禁用生产 | `https://integrate.api.nvidia.com/v1` |
| **Inference.net** | — | Free $0 计划 30 RPM | 未公布 | 否 | 未明示 | `https://api.inference.net/v1` |
| **OVHcloud AI Endpoints** | — | 匿名 2 RPM；带 key 400 RPM | 速率型，非配额型 | 否 | ✅ 不存储不复用 | `https://oai.endpoints.kepler.ai.cloud.ovh.net/v1` |
| **魔搭 ModelScope** 🇨🇳 | 每日 0 点 | **2,000 次/日（全模型合计）**；单模型动态：历史 500 / DeepSeek-R1 约 200 / 图片约 50 / 部分现仅 100 | 中文开源模型（Qwen3、DeepSeek、GLM） | 否 | 需绑阿里云 + 实名 | `https://api-inference.modelscope.cn/v1` |
| **阿里云百炼（OAuth 通道）** 🇨🇳 | 每日 | **2,000 次/日**——注意这是 **OAuth 认证独立额度**，与控制台 API Key 的额度体系分开、**控制台不显示** | 70+ 模型 | 否 | 需阿里云实名 | `https://dashscope.aliyuncs.com/compatible-mode/v1` |
| **商汤日日新** 🇨🇳 | **每 5 小时** | **1,500 次/5 小时/每模型**（`sensenova-u1.5-lite`，公测） | 图文 | 否 | 注册建 Key | `https://api.sensenova.cn/compatible-mode/v1` |
| **Gitee AI 模力方舟** 🇨🇳 | 每日 | **100 次/日**（免费体验访问令牌） | 全模型 | 否 | Gitee 账号 | `https://ai.gitee.com/v1` |

## 3. 每月刷新额度（A 类）

| 平台 | 刷新 | 额度 | 折算 | 需卡 |
|---|---|---|---|---|
| **Mistral（Experiment）** | 月 | **1B tokens/模型/月**；1 RPS / 500K TPM（🟡 二手） | ~33M token/日 | 否（需手机验证） |
| **Vercel AI Gateway** | 月 | **$5/月**，全模型可用 | 按各家单价折算 | 🟡 第三方称需绑支付 |
| **Cohere** | 月 | Trial key **1,000 calls/月**，Chat 20 RPM | 千次量级 | 否 |
| **Hugging Face** | 月 | **$0.10/月**（PRO $2） | 聊胜于无 | 否 |
| **OpenAI（数据共享补偿）** | 日 | 开启共享后 **1M token/日**，mini 类 **10M/日** | 量大，但需账户有正余额 | 需充值 |
| **阿里云百炼（语音模型）** 🇨🇳 | 每月 1 日 0 点 | Paraformer / SenseVoice 每月发放、有效期 1 个月 | 语音类 | 否（需实名） |

---

## 4. 永久免费模型（B 类：不刷新，但永不耗尽）

**这些应该作为降级链的终点**——额度型全挂了，它们还在，只是慢。

| 平台 | 模型 | 上下文 | 限额 | 需卡 | base_url |
|---|---|---|---|---|---|
| **Z.ai（海外）** | `glm-4.7-flash` | 200K | ~1 并发 / ~1 req/s | 否 | `https://api.z.ai/api/paas/v4`（Anthropic: `/api/anthropic`） |
| **智谱 BigModel（国内）** | `glm-4.7-flash`、`glm-4-flash` | 203K | ✅ **已核实：官方限的是「并发数」**——`glm-4-flash-250414` 按权益等级为 **200 / 1000 / 2000 / 3000**（V0–V3）；`glm-4.7-flash` 并发**未公布** | 否（需实名） | `https://open.bigmodel.cn/api/paas/v4` |
| **百度千帆** | `ERNIE-Speed-8K/128K`、`ERNIE-Lite-8K`、`ERNIE-Tiny-8K` | 8K–128K | ✅ 开发者文档表：**Speed-8K 600 RPM / 600K TPM**；Lite-8K **600/600K**；Tiny-8K **600/600K**；**Speed-128K 仅 60 RPM / 300K TPM**（🟡 官方另称"以控制台为准"） | 否（需实名） | `https://qianfan.baidubce.com/v2` |
| **讯飞星火** | Spark Lite | 8K in / 4K out | ✅ 官方文档原话"**支持 免费使用**"；⚠️ QPS/日上限**不公布**，错误码显示三层流控（日/秒级/并发）；文档称"并发提升（**含免费模型**）"需联系客服 → 确有并发帽。⚠️ 官方**免费包是一次性**的（个人 200 万 token / QPS 2 / 1 年） | 否 | `https://spark-api-open.xf-yun.com/v1` |
| **腾讯混元** | `hunyuan-lite` | — | ❌ **疑似已下线**：2026-06-22 现行模型列表与免费额度表**均无 hunyuan-lite**；混元生文接口默认**并发 5 路**（主子账号共享） | 否（需实名） | `https://api.hunyuan.cloud.tencent.com/v1` |
| **硅基流动** | ✅ **免费 chat 模型 11 个**（官方页面内嵌目录实取）：`Qwen/Qwen2.5-72B-Instruct`(32K,tools)、`Qwen/Qwen3.5-4B`(262K,tools)、`Qwen/Qwen3-8B`(131K,tools)、`THUDM/GLM-Z1-9B-0414`(131K,tools)、`THUDM/GLM-4-9B-0414`(32K,tools)、`XingChenAGI/Xing4.0-29B`(262K,tools)、`Qwen/Qwen2.5-7B-Instruct`(32K,tools)、`DeepSeek-R1-0528-Qwen3-8B`(131K)、`DeepSeek-OCR`、`PaddleOCR-VL-1.5`、`Hunyuan-MT-7B` | 8K–262K | 免费模型 **L0 = 1000 RPM** / TPM 40K–80K，且**不随等级变化** | 否（**需实名**） | `https://api.siliconflow.cn/v1` |
| **PPIO 派欧云** | ⚠️ **存疑**：宣称的"永久免费版 Qwen2.5-7B"仅见于 2025-07 文档；**2026 定价页未见免费模型**，`qwen2.5-7b-instruct` 现价 **¥0.35/Mt**，未实名 RPM 限 1 | — | 疑似已取消 | 否 | `https://api.ppio.com/openai` |
| **面壁 MiniCPM** | MiniCPM-V 4.6 / o 4.5 | — | 官网提供公开免费 Key，但**未见任何 RPM/日限文档**（未核实） | 否 | `https://api.modelbest.cn/v1` |
| **Cloudflare** | `@cf/zai-org/glm-4.7-flash` 等 | 按模型 | 吃上面的 10k Neurons | 否 | 同 §2 |

> **国内的结构性结论**：真正"**每日刷新的大额文本额度**"只有三处——**魔搭 2,000 次/日**、**百炼 OAuth 2,000 次/日**、**商汤 1,500 次/5 小时**。其余国内平台给的是"永久免费模型"，限的是**并发/RPM**（不刷新、永不耗尽，但扛不住高并发）。所以国内长期主力的正确姿势是：**刷新额度扛量 + 免费模型（低并发）常驻兜底**。

---

## 5. 推荐组合（三档）

**档 1：全免费、零信用卡**（目标：每天 1–3M token 白跑）

```
主力量      Cloudflare Workers AI   → qwen3-30b-a3b-fp8 / gemma-4-26b-a4b / glm-4.7-flash（10k Neurons/日）
速度/强模型  Groq                    → openai/gpt-oss-120b（1,000 RPD / 200K TPD）
长上下文     Google AI Studio        → Gemma 4 31B（14,400 RPD，扛批处理）
硬问题       Google AI Studio        → Gemini Flash（20 RPD，省着用）
中文任务     智谱 glm-4.7-flash / 百度 ERNIE-Speed / 硅基流动
中文刷量     魔搭 2,000 次/日 + 百炼 OAuth 2,000 次/日 + 商汤 1,500 次/5h（国内唯一的刷新型额度）
兜底        Z.ai glm-4.7-flash 或本地 llama.cpp（永不耗尽）
```

**档 2：花一次 $10 把日额度翻 20 倍**（推荐，性价比最高）

在档 1 基础上给 OpenRouter 充 **$10（一次性、非订阅）**——免费模型日额度从 **50 → 1,000 请求/日永久生效**，且一个 key 覆盖 24 个免费模型（其中 19 个支持 tool calling，最大上下文 1,048,576）。**这是全清单里唯一"一次性付款买永久日额度"的机制。**

**档 3：加上每月刷新的大额度**

叠加 Mistral（1B token/月）、Vercel（$5/月）、Cohere（1,000 calls/月）覆盖月中峰值。

### 日预算粗算（档 2）

| 来源 | 可预期量/日 |
|---|---|
| Cloudflare（qwen3-30b / gemma-4） | ~2M 输入 + 0.35M 输出 token |
| Groq（gpt-oss-120b） | 0.2M token |
| Gemini（Gemma 系） | 14,400 请求 |
| Gemini（Flash） | 20 请求 |
| GitHub Models | 150 请求（单请求上限 8K in） |
| OpenRouter（充值后） | 1,000 请求 |
| SambaNova | 0.2M token（20 RPD） |
| 魔搭 ModelScope 🇨🇳 | 2,000 请求（全模型合计） |
| 阿里云百炼 OAuth 🇨🇳 | 2,000 请求 |
| 商汤日日新 🇨🇳 | 1,500 次/5 小时 ≈ 7,200 请求/日 |
| Gitee AI 🇨🇳 | 100 请求 |
| **合计** | **保守估 ≥3M token/日 + 约 12,800 次请求/日，全部 $0** |

> 该合计是**上限叠加**，实际受 RPM、并发、单请求上下文共同限制；且各平台额度独立，单家打满不影响其他家——这正是要多家并联的原因。
> 国内那部分（魔搭/百炼 OAuth/商汤）是**唯一能刷新的中文文本额度**，其余国内免费模型都是"并发受限、永不耗尽"型。

---

## 6. 落地：接到 DSH / 任意 OpenAI 兼容客户端

DSH 在 `~/.dsh/settings.yaml` 的 `llm-pi-ai.providers.<名字>` 注册 provider，再在 `subagent-model-selection.allowedModels` 里放行。按上面档 1 的组合：

```yaml
llm-pi-ai:
  providers:
    cf-free:
      displayName: "Cloudflare Workers AI (10k Neurons/日)"
      apiKeyEnv: CF_API_TOKEN
      api: openai-completions
      # ⚠️ baseURL 是纯字符串，DSH 不做 ${VAR} 展开 → 账号 ID 直接写死（它不是密钥）
      baseURL: https://api.cloudflare.com/client/v4/accounts/<你的_account_id>/ai/v1
      models:
        - id: "@cf/qwen/qwen3-30b-a3b-fp8"
          name: "Qwen3-30B-A3B (CF free)"
          contextWindow: 131072
          maxTokens: 16384
          input: [ text ]
    groq-free:
      displayName: "Groq free (1,000 RPD)"
      apiKeyEnv: GROQ_API_KEY
      api: openai-completions
      baseURL: https://api.groq.com/openai/v1
      models:
        - id: openai/gpt-oss-120b
          name: "gpt-oss-120b @ Groq"
          contextWindow: 131072
          maxTokens: 32768
          input: [ text ]
    zai-free:
      displayName: "Z.ai GLM Flash (永久免费)"
      apiKeyEnv: ZAI_API_KEY
      api: openai-completions
      baseURL: https://api.z.ai/api/paas/v4
      models:
        - id: glm-4.7-flash
          name: "GLM-4.7-Flash (free, 200K)"
          contextWindow: 203000
          maxTokens: 16384
          input: [ text ]
```

要点：
1. key 一律走 `apiKeyEnv`，不写进 yaml。
2. **DSH 没有自动的跨 provider 降级**（`llm-pi-ai` 不支持 failover）。所以策略是：**把多家都注册进来**，靠 `subagent-model-selection.allowedModels` 放行多个候选，打满哪家就在 UI 里切到另一家；需要自动化的话，降级逻辑得写在调用侧（自己的脚本里对 429 重试换 provider），不能指望 DSH 替你切。
3. 客户端必须处理 **429 + Retry-After**，并记录各家的 `X-RateLimit-*` 头（OpenRouter 的 `GET /api/v1/key` 可直接读余量）。
4. 改 `settings.yaml` 需**重启 `dsh-web.service`** 才生效，会中断当前会话——动手前先确认。

### 6.1 base_url 路径实测（2026-09-20，无 key 打一发，看是否 404）

| 端点 | 返回 | 判定 |
|---|---|---|
| `https://generativelanguage.googleapis.com/v1beta/openai/chat/completions` | 400 `Missing or invalid Authorization header` | ✅ 路径正确 |
| `https://api.groq.com/openai/v1/chat/completions` | 403 `Forbidden` | ✅ 路径正确 |
| `https://api.z.ai/api/paas/v4/chat/completions` | 401 `Authentication parameter not received` | ✅ 路径正确 |
| `https://open.bigmodel.cn/api/paas/v4/chat/completions` | 401 `Header中未收到Authorization参数` | ✅ 路径正确 |
| `https://api.siliconflow.cn/v1/chat/completions` | 401 `Token is invalid` | ✅ 路径正确 |
| `https://api.cloudflare.com/client/v4/accounts/<id>/ai/v1/chat/completions` | 404 `Could not route ... perhaps your object identifier is invalid` | ✅ 路径形状正确（用假 account id 测试，故报 id 无效） |

---

## 7. 待核与排除

**本轮待核结果（第二轮已完成）**：
- ✅ **已核实**：智谱（限并发：glm-4-flash 200/1000/2000/3000；glm-4.7-flash 未公布）、百度千帆（Speed-8K 600 RPM/600K TPM 等）、**硅基流动（11 个免费 chat 模型，L0 = 1000 RPM；需实名）**、讯飞（Lite 文档背书免费，但 QPS 不公布、存在三层流控）、魔搭（2000 次/日合计）、Gitee AI（100 次/日）、商汤（1500 次/5 小时/模型）、阿里云百炼 OAuth（2000 次/日）
- ⚠️ **仍未核实**：讯飞 Spark Lite 官方 QPS（只有活动页的 QPS 2）；面壁 MiniCPM 无任何限流文档；魔搭**单模型**精确上限（官方页是 SPA，抓不到正文）
- ❌ **已证伪/下线**：腾讯 `hunyuan-lite`（2026-06-22 起不在模型列表）、PPIO 免费模型（定价页已无）
- ↩️ **撤回的修正**：先前据二手信息称"硅基流动 `THUDM/GLM-Z1-9B-0414` 已收费"——**已证伪**。官方页面内嵌目录显示其 `price=0`、`status=normal`、支持 tools；页面无 `0.086` 字样。教训：二手清单与"看起来是价格页"的抓取都可能错，**以内嵌结构化数据为准**。

**已排除（附原因）**：
- 🚫 **一次性赠送**（不可持续）：阿里云百炼 100 万/90 天、腾讯混元 100 万/1 年、Kimi 15 元/3 月、华为云 MaaS、天翼云息壤、Scaleway 100 万、Cerebras $5、Nebius $1、AI21 $10/3 月、潞晨 ¥20、百川 80 元
- 🚫 **需绑卡**：Together AI（已取消免费试用）、Modal（$30/月但必须绑卡且无 OpenAI 端点）、Vercel（🟡 第三方称需绑支付）
- 🚫 **无 key 玩具站**（非额度型、仅供 demo）：Pollinations、LLM7、AI Horde、OVH 匿名
- 🚫 **已死/已停**：Glhf.chat（522/TLS）、Chutes.ai（无免费层）、无问芯穹（2026-03-30 停）、OpenCode Zen 免费档（裸 key 403）
- 🚫 **社区中转站**：数据与凭据风险，禁止

---

## 8. 维护纪律

1. **每月 1 号复查一次**：官方限流页 + 本文档 §1 的 Neuron 算式（Neuron 单价会调，调了额度就变）。
2. **监控而非猜测**：写脚本每天记录各家的 429 次数与实际用量，哪家缩水立刻降级。
3. **额度优先级**：先打"条款干净 + 量大"的（Cloudflare），再打"快但量小"的（Groq），最后才是"条款差但量极大"的（Gemini Gemma）。
4. **B 类兜底不可省**：至少留一个永久免费模型或本地模型作为终点，避免配额耗尽导致工作中断。
