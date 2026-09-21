# 免费大模型 API 全网清单（2026-09-20）

> 情报日期 **2026-09-20**。所有条目要么标注来源，要么标注"未核实"。
> 免费额度是按月变动的活数据，**投产前必须用自己账号的控制台核账**。
> 原始分报告：[cn-llm-free-api-quota-2026-09-20.md](./cn-llm-free-api-quota-2026-09-20.md)（国内 29 家）、[overseas-free-api-tiers.md](../../.scratch/llm-free-api-2026/overseas-free-api-tiers.md)（海外主力 + 长尾 30 余家）、[research.md](../../.scratch/free-llm-api/research.md)（渠道与风险）。

## 0. 先看结论

**免费有五种，别混为一谈**——混用是踩坑的根源：

| 类型 | 含义 | 能否做架构依赖 | 典型 |
|---|---|---|---|
| 🟢 **永久免费模型** | 官方定价恒为 $0，不限期 | ✅ 排序/分类/批处理可用 | GLM-4.7-Flash、ERNIE-Speed、Spark Lite、gpt-oss-120b@Groq |
| 🔵 **永久免费额度** | 每日/每月刷新，额度内免费 | ✅ 但要做限流与降级 | Gemini 免费层、Groq、Cerebras 无、Cloudflare 10k Neurons/日 |
| 🟡 **一次性赠送** | 新用户首赠 token/金额，会过期 | ❌ 只能用来评估 | 百炼 100 万/90 天、Kimi 15 元/3 月、Mistral 无、Scaleway 100 万 |
| 🟠 **免鉴权/无卡网关** | 无 key 或匿名 key 即用 | ⚠️ 仅供 demo | Pollinations、AI Horde、LLM7、Kilo 免费路由 |
| 🔴 **社区公益站/逆向** | 中转站、反代、gpt4free | ❌ 禁止 | NewAPI 公益站、ChatGPT 反代 |

**一句话选型**：想要"永远白嫖"→ 选 🟢（智谱 GLM-4.7-Flash、百度 ERNIE-Speed/Lite、Groq 的 gpt-oss；讯飞 Spark Lite 官方只标 QPS 2，量小）；想要"能力最强"→ Gemini 免费层（但 20 RPD 的旗舰档很紧）；想要"一个 key 打通多家"→ OpenRouter `:free` 或 Kilo 免费路由。

**零卡、零账号、当场可用**的 OpenAI 兼容入口全网只有 **3 个**：**Kilo Gateway**（匿名 200 次/时/IP）、**Pollinations**（1 次/15 秒）、**LLM7.io**（匿名 50 万 tokens/日）——三者今天都实测跑通。

**本清单纠正了 14 条流传很广的过时结论**（Cerebras、NVIDIA credits、Together、Chutes、无问芯穹、Anthropic、Glhf、Groq 的 14.4K 额度、硅基流动免费模型、hunyuan-lite、PPIO、讯飞"无限量"、商汤 base_url 等），见 [§7](#7-已失效--常见误传纠正)。

---

## 1. 海外官方免费层

### 1.1 Google AI Studio / Gemini API 🟢（能力天花板，但限额紧）

- 入口：<https://aistudio.google.com> ｜限流：<https://ai.google.dev/gemini-api/docs/rate-limits>
- **免费层真实存在**：官方定价页对多款模型明写 `Free Tier = Free of charge`（输入/输出/缓存均免费）
- 限额（官方表为 JS 动态渲染，下列为第三方整理 + 社区实测，标注可信度）：
  - Gemini 3.8 / 3.6 / 3.5 / 3 Flash：**20 RPD**、5 RPM、250K TPM（🟡 社区实测，[Google 论坛帖](https://discuss.ai.google.dev/t/gemini-3-8-flash-free-tier-20-rpd-is-too-limited-for-practical-evaluation/180609)）
  - Gemini 3.5 / 3.1 Flash-Lite：**500 RPD**、15 RPM（🟡 同上）
  - Gemma 4 31B / 26B A4B、Gemma 3 全系：**14,400 RPD**、30 RPM、16K TPM（✅ 免费额度极高，适合批量）
  - TTS / 图像 / Grounding：500 RPD 档
- base_url：`https://generativelanguage.googleapis.com/v1beta`（OpenAI 兼容层另有 `/v1beta/openai/`）
- 门槛：**无信用卡**，Google 账号即可
- ⚠️ **数据条款**：官方定价页对免费层明写 `Used to improve our products: Yes`。免费层内容会被用于改进产品，官方明确建议不要提交敏感/机密/个人信息。EEA/CH/UK 另有区域限制。
- 结论：**用 Gemma 系当免费主力（14,400 RPD），用 Gemini Flash 当"偶尔问一次难题"**。

### 1.2 Groq 🟢（速度快，openai/gpt-oss 永久免费）

- 入口：<https://console.groq.com> ｜限流：<https://console.groq.com/docs/rate-limits>
- 免费模型与限额（官方表）：

| 模型 | RPM | RPD | TPM | TPD |
|---|---|---|---|---|
| `openai/gpt-oss-120b` | 30 | 1,000 | 8,000 | 200,000 |
| `openai/gpt-oss-20b` | 30 | 1,000 | 8,000 | 200,000 |
| `groq/compound` / `compound-mini` | 30 | 250 | 70,000 | — |
| `qwen/qwen3.6-27b` | — | 1,000 | 8,000 | — |
| Whisper Large v3 / Turbo | — | 2,000 | — | — |
| `meta-llama/llama-prompt-guard-2-*` | 30 | 14,400 | 15,000 | 500,000 |

- base_url：`https://api.groq.com/openai/v1`（OpenAI 兼容）
- 门槛：**无信用卡**，邮箱注册
- 备注：120B 级模型 + 1000 RPD 是**当前最好用的"永久免费 + 强模型"组合之一**。

### 1.3 Mistral La Plateforme（Experiment 计划）🟢

- 入口：<https://console.mistral.ai> ｜退出训练开关：<https://help.mistral.ai/en/articles/455207>
- 形式：**非金额赠款，而是限速的持续免费**（Experiment 计划）
- 限额：约 **1 RPS**、**500K TPM**、**1B tokens/月/模型**（🟡 二手，官方限流页需登录）
- base_url：`https://api.mistral.ai/v1`（OpenAI 兼容）
- 门槛：邮箱 + **手机号短信验证**，**无信用卡**；一个手机号只能用于一个 Experiment 计划
- ⚠️ **数据条款**：免费/实验路径默认**可能用于训练**，且 **Vibe 与 API 两个退出开关互不覆盖**，必须去 Admin → Privacy 分别关
- 注意：`mistralai` 的 Codestral 另有独立免费档，主要面向 IDE 补全。

### 1.4 NVIDIA NIM（build.nvidia.com）🔵

- 入口：<https://build.nvidia.com> ｜base_url：`https://integrate.api.nvidia.com/v1`（OpenAI 兼容）
- 形式：**面向原型的免费托管推理**，100+ 模型（Nemotron 3 系、DeepSeek-V4、GLM、Llama、Qwen、Kimi、Mistral、Phi）
- ⚠️ **重大变更（纠正旧资料）**：**已取消 credit 制**。旧的"注册送 1000 credits、共 5000"是 2024 年政策，[NVIDIA 论坛](https://forums.developer.nvidia.com/t/api-rate-limit-increase-is-not-granted-by-requesting-it-here/368420)明确"build.nvidia.com 不再使用 credit 系统，限额按模型而变且不公开"。社区流传的 **40 RPM 是历史观测值，不是 SLA**
- 门槛：邮箱注册；部分资料称需手机验证
- 生产用途需 NVIDIA AI Enterprise 授权（$4,500/GPU/年起，有 90 天免费评估）
- 建议：**当"多一个免费档"用，客户端必须实现 429 退避 + fallback**，不要依赖固定 RPM。

### 1.5 GitHub Models 🔵（有 GitHub 账号即用，模型含 GPT-5）

- 入口：<https://github.com/marketplace/models> ｜文档：<https://docs.github.com/en/github-models/use-github-models/prototyping-with-ai-models>
- base_url：`https://models.github.ai/inference`（OpenAI 兼容）
- 40+ 模型（OpenAI GPT-5 系、Meta、Mistral、Cohere、DeepSeek、xAI Grok）
- 限额按 Copilot 档位（官方表）：

| 档 | RPM | RPD | 单请求 token | 并发 |
|---|---|---|---|---|
| Low ｜ Copilot Free | 15 | 150 | 8K in / 4K out | 5 |
| High ｜ Copilot Free | 10 | 50 | 8K in / 4K out | 2 |
| Embedding ｜ Copilot Free | 15 | 150 | 64K | 5 |
| DeepSeek-R1 ｜ Copilot Free | 1 | 8 | 4K in / 4K out | 1 |
| xAI Grok-3 ｜ Copilot Free | 1 | 15 | 4K in / 4K out | 1 |

- 门槛：**GitHub 账号 + PAT（`models:read` 权限），无信用卡**。免费档定位是"上手实验"，不适合生产。
- ⚠️ 数据条款：**个人档内容可能被 GitHub 用于训练**（可退出）；企业版不用于训练。

### 1.6 Cloudflare Workers AI 🔵（每日 10,000 Neurons，量最大的小项目档）

- 入口：<https://dash.cloudflare.com> ｜定价：<https://developers.cloudflare.com/workers-ai/platform/pricing/>（本文实测抓取，页面更新 2026-09-17）
- **官方原文**：免费额度 **10,000 Neurons/日**，Free 与 Paid 计划都有；每日 **00:00 UTC** 重置；超出需 Workers Paid（$0.011/1,000 Neurons）
- 模型：Llama 系、Qwen3-30B、Gemma 4、gpt-oss-120b/20b、Nemotron 3、GLM-4.7-Flash、DeepSeek R1 Distill 等
- ⚠️ 部分模型**已要求付费计划**：`@cf/moonshotai/kimi-k2.6`、`kimi-k2.7-code`、`@cf/zai-org/glm-5.2`、`glm-5.3`、`glm-5.3-flash`、`@cf/deepseek-ai/deepseek-v4-flash-0731`、`deepseek-v4-pro-0813`
- base_url：`https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run`（也提供 OpenAI 兼容的 `/v1/chat/completions`）
- 门槛：Cloudflare 账号，**无信用卡**
- ✅ **数据条款最干净的一家**：官方明确**不用用户内容训练、不改进模型、不外泄**。敏感度高的批处理优先考虑这里。

### 1.7 OpenRouter `:free` 🟠→🔵（一个 key 打通几十家）

- 入口：<https://openrouter.ai> ｜限流：<https://openrouter.ai/docs/api-reference/limits>
- **2026-09-20 实测**（`GET /api/v1/models`，无需 key）：**446 个模型，其中 24 个 input/output 双 $0**

```
google/gemma-4-26b-a4b-it:free      google/gemma-4-31b-it:free
nvidia/nemotron-3-ultra-550b-a55b:free (1M ctx)   nvidia/nemotron-3-super-120b-a12b:free
nvidia/nemotron-3.5-lightning:free (1M ctx)       nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free
qwen/qwen3.8-27b:free               z-ai/glm-5.2:free          stepfun/step-3.7-flash:free
poolside/laguna-s-2.1:free          poolside/laguna-xs-2.1:free
thinkingmachines/inkling:free (1M)  thinkingmachines/inkling-small:free
inclusionai/ling-3.0-flash-{vl,fin,sante}:free    liquid/lfm-2.5-2.6b:free
nex-agi/nex-n2.5-{pro,mini}:free    cohere/north-mini-code:free
dots-studio/dots-3-note-preview:free  google/lyria-3-{pro,clip}-preview
openrouter/free  ← 免费模型自动路由
```

- 限额：**20 RPM**；未充值 **50 请求/日**；**累计充值 ≥$10 → 1,000 请求/日**（官方 FAQ；额度字段 `free_model_daily_requests` 可在 `GET /api/v1/key` 查实时余量）
- ⚠️ **数据条款**：官方明示免费变体的 prompt/completion **可能被记录并用于训练**（隐私设置可关）。免费端点名单周变，不可作生产依赖。
- **支持 tool calling 的免费模型**（做 agent 必须看这一列，2026-09-20 实测 `supported_parameters`）：

| 模型 | 上下文 | tools | reasoning |
|---|---|---|---|
| `thinkingmachines/inkling` / `inkling-small:free` | **1,048,576** | ✅ | ✅ |
| `nvidia/nemotron-3.5-lightning:free` | 1,000,000 | ✅ | ✅ |
| `nvidia/nemotron-3-ultra-550b-a55b:free` | 1,000,000 | ✅ | ✅ |
| `qwen/qwen3.8-27b:free` | 262,144 | ✅ | ✅ |
| `poolside/laguna-s-2.1:free` / `laguna-xs-2.1:free` | 262,144 | ✅ | ✅ |
| `google/gemma-4-31b-it:free` / `gemma-4-26b-a4b-it:free` | 262,144 | ✅ | ✅ |
| `nvidia/nemotron-3-super-120b-a12b:free` | 262,144 | ✅ | ✅ |
| `cohere/north-mini-code:free` | 256,000 | ✅ | ✅ |
| `openrouter/free`（自动路由） | 200,000 | ✅ | ✅ |
| `z-ai/glm-5.2:free` | 32,768 | ❌ | ✅ |

（`google/lyria-3-*` 为音乐生成模型，不属文本对话，故不在上表。）
- base_url：`https://openrouter.ai/api/v1`
- ⚠️ ToS：禁止**转售 API 访问**、禁止**开发竞品服务**（平台级，不限免费模型）；官方称免费模型"通常不适合生产"
- 门槛：注册，无信用卡

### 1.8 Kilo Gateway 🟠（免费路由，无账号可用）

- 入口：<https://kilo.ai> ｜文档：<https://kilo.ai/docs/getting-started/using-kilo-for-free>
- **2026-09-20 实测** `GET https://api.kilo.ai/api/gateway/v1/models`：**380 个模型中 23 个免费**，与 OpenRouter 免费集合高度重叠，外加 `kilo-auto/free`（自动省钱路由）
- base_url：`https://api.kilo.ai/api/gateway`
- ⚠️ 官方明确警告：Auto Free **可能路由到会记录 prompt/输出并用于改进服务的 provider**，不要提交个人或机密数据
- 门槛：免费模型**无需账号**（有 IP 限流）

### 1.9 其他海外免费/试用档

| 平台 | 免费形式 | 关键数字 | base_url | 门槛 |
|---|---|---|---|---|
| **Z.ai (GLM)** 🟢 | 永久免费模型 ×3 | `glm-4.7-flash`(200K)/`glm-4.5-flash`/`glm-4.6v-flash`（视觉）$0/$0，**1 并发** ⚠️ ToS（2026-04-14）允许将**个人用户内容用于训练** | `https://api.z.ai/api/paas/v4`；Anthropic 兼容 `https://api.z.ai/api/anthropic` | 注册，**无卡** |
| **SambaNova Cloud** 🔵 | 免费层（不绑卡即生效） | 每模型 **20 RPM / 20 RPD / 200K TPD**（DeepSeek-V3.1/V3.2、Llama-3.3-70B、gpt-oss-120b、gemma-4-31B） | `https://api.sambanova.ai/v1` | 注册 |
| **Together AI** ⚠️ | **已取消免费试用** | 官方 2025-07 改版：**最低购 $5，需绑卡**；serverless 定价表中仍有 $0 模型（如 Ternary-Bonsai-27B）但调用前置条件未核实 | `https://api.together.xyz/v1` | **需卡** |
| **Vercel AI Gateway** 🔵 | 每月 $5 额度 | **$5/月、全模型可用**、无承诺（官方 pricing 页）；🟡 第三方称需绑支付方式，未核实 | `https://ai-gateway.vercel.sh/v1` | Vercel 账号 |
| **OpenAI（数据共享补偿）** 🟡 | 官方唯一持续免费来源 | 开启 Data Sharing 后：**1M tokens/日**（Tier1-2 为 250k）、mini 类 **10M/日**（2.5M），UTC 00:00 重置。**前提是账户有正余额** | `https://api.openai.com/v1` | 需充值 + 同意数据共享 |
| **Scaleway Generative APIs** 🟡 | 一次性免费额度 | **1,000,000 tokens**（另 60 分钟音频转写），按最贵 token 优先抵扣；🟡 300 RPM 档需已验证支付方式 | `https://api.scaleway.ai/v1` | 注册 |
| **OVHcloud AI Endpoints** 🟠 | 匿名可用！ | **匿名 2 RPM/IP/模型**；带 key **400 RPM**；新用户另有 $200 Public Cloud 试用金（1 个月） | `https://oai.endpoints.kepler.ai.cloud.ovh.net/v1` | 匿名即可，key 需 Public Cloud 项目 |
| **Hugging Face Inference Providers** 🔵 | 每月赠额度 | Free 用户 **$0.10/月**（PRO $2/月）——聊胜于无 | `https://router.huggingface.co/v1` | HF 账号 |
| **Ollama Cloud** 🔵 | Free 计划 | 官方："Free 计划含 starter 用量，覆盖**较小的 starter 模型集**"，**1 并发**；买 credit 才解锁全部模型。官方 blog（2026-08-31）确认**无"5 小时/周"限制** | `https://api.ollama.com` | ollama.com 账号 |
| **Cohere** 🔵 | Trial（evaluation）key 永久 | **1,000 calls/月**；Chat 各模型 trial **20 req/min**。trial 与 production key 条款不同，**商用必须换 production key** | `https://api.cohere.com/v2` | 注册 |
| **Inference.net** 🔵 | Free $0 计划 | **30 RPM** | `https://api.inference.net/v1` | 注册 |
| **OpenCode Zen** ⚠️ | 限时免费型号 | **实测裸 key 返回 403**：「免费档只能在 OpenCode 客户端内用」——不是通用 API | `https://opencode.ai/zen/v1` | 需 OpenCode 客户端 |
| **Cloudflare AI Gateway** 🔵 | 网关本体免费 | 10 万条日志；Unified Billing 200 req/60s；BYOK 不受限 | `https://gateway.ai.cloudflare.com/v1/{acct}/{gw}/openai` | CF 账号 |
| **Modal** 🟡 | 每月 $30 额度 | 但**必须绑卡**，且**无 OpenAI 兼容端点** | — | **需卡** |
| **Nebius Token Factory** 🟡 | $1 / 30 天 | **强制绑卡** | `https://api.tokenfactory.nebius.com/v1/` | **需卡** |
| **Fireworks** 🔵 | 一次性 $1 | **未绑卡 10 RPM**、绑卡 6,000 RPM；默认 ZDR | `https://api.fireworks.ai/inference/v1` | 注册 |
| **AI21 / Upstage / Novita / Baseten / Hyperbolic / Nscale** 🟡 | 一次性试用金 | $10/3 月（AI21）等，各家 $1–$25 不等，**多数需逐家核实当前值** | 各家 | 多需注册/卡 |
| **xAI (Grok)** ⚠️ | **无常规免费层** | 官方 quickstart（2026-08-18）要求先充值；旧 $25/月公测政策已终止。二手称 Data Sharing Program 给 $150/月（需已消费 ≥$5）——**未核实** | `https://api.x.ai/v1` | 需充值 |
| **Glhf.chat** ❌ | **已不可用** | 2026-09-20 实测站点与 API 均 522 / TLS 失败 | — | — |
| **Chutes.ai** ⚠️ | **无免费层** | 官方明示按量付费；旧 200 请求/天政策已关停 | `https://llm.chutes.ai/v1` | 付费 |

---

## 2. 国内官方免费层

> 完整版（29 家、一家一节 + 总表）见 [cn-llm-free-api-quota-2026-09-20.md](./cn-llm-free-api-quota-2026-09-20.md)。这里只留决策所需。

### 2.1 可长期依赖的"永久免费"🟢

| 平台 | 免费模型 / 额度 | base_url | 门槛 |
|---|---|---|---|
| **智谱 BigModel (GLM)** | `glm-4.7-flash`（203K ctx）、`glm-4-flash` **永久 $0**。✅ 限流维度是**并发数**：`glm-4-flash-250414` = **200/1000/2000/3000**（V0–V3）；`glm-4.7-flash` 并发未公布 | `https://open.bigmodel.cn/api/paas/v4` | 注册+实名，**免绑卡** |
| **百度千帆** | `ERNIE-Speed-8K/128K`、`ERNIE-Lite-8K`、`ERNIE-Tiny-8K` **长期免费**。文档表：Speed-8K **600 RPM/600K TPM**、Lite-8K **600/600K**、Tiny-8K **600/600K**、Speed-128K **60/300K**（🟡 官方另称"以控制台为准"，社区另有 300 RPM 版本） | `https://qianfan.baidubce.com/v2`（🟡二手） | 实名认证 |
| **讯飞星火** | ✅ 官方 HTTP 文档原话：Lite 是"轻量级大语言模型…**支持 免费使用**"，规格 **输入 8K / 输出 4K**，model 参数 = `lite`。⚠️ **QPS/日上限官方不公布**，只能从错误码反推存在三层流控：`11201` 日流控超限、`11202` 秒级流控超限、`11203` 并发流控超限；文档另称"如有并发提升(**含免费模型**)"需联系客服 → 免费档确有并发帽。⚠️ 官方"免费包"是**一次性**的：个人 200 万 tokens / 企业 500 万，**QPS 2 / 有效期 1 年**，与 Lite 永久免费不是一回事 | `https://spark-api-open.xf-yun.com/v1` | 注册+建应用，key 用 **APIPassword** |
| **硅基流动 SiliconFlow** | ✅ **已从官方页面内嵌目录解出完整清单**：免费(¥0) **chat** 模型 11 个——`Qwen/Qwen2.5-72B-Instruct`(32K, tools)、`Qwen/Qwen3.5-4B`(262K, tools)、`Qwen/Qwen3-8B`(131K, tools)、`THUDM/GLM-Z1-9B-0414`(131K, tools)、`THUDM/GLM-4-9B-0414`(32K, tools)、`XingChenAGI/Xing4.0-29B`(262K, tools)、`Qwen/Qwen2.5-7B-Instruct`(32K, tools)、`DeepSeek-R1-0528-Qwen3-8B`(131K)、`DeepSeek-OCR`、`PaddleOCR-VL-1.5`、`Hunyuan-MT-7B`；非 chat 免费：`bge-m3`/`bge-reranker-v2-m3`/`bge-large-zh`/`bge-large-en`、`Kolors`(生图)、6 个语音模型 | `https://api.siliconflow.cn/v1` | **需实名认证**；免费模型 L0 = **1000 RPM**（TPM 40K–80K），且不随等级变化 |
| **魔搭 ModelScope** | **每日 2,000 次**推理调用（**全模型合计**），单模型动态：历史 500 / R1 约 200 / 图片约 50 / 现部分仅 100 | `https://api-inference.modelscope.cn/v1` | 需绑阿里云 + 实名 |
| **Gitee AI 模力方舟** | **每日 100 次**全模型免费调用（官方声明**勿用于生产**） | `https://ai.gitee.com/v1` | Gitee 账号 |
| **面壁 MiniCPM** | MiniCPM-V 4.6 / o 4.5 系**公开免费 API Key** | `https://api.modelbest.cn/v1` | 平台注册 |
| **腾讯混元** | ❌ **`hunyuan-lite` 疑似已下线**：2026-06-22 现行模型列表与免费额度表**均无它**；生文接口默认**并发 5 路** | `https://api.hunyuan.cloud.tencent.com/v1` | 腾讯云实名 |
| **商汤日日新** | `sensenova-u1.5-lite` **1500 次/5 小时/每模型**（公测）；Token Plan Free 档 6 万积分/5h | ⚠️ **已修正**：`https://api.sensenova.cn/compatible-mode/v1` | 控制台取 Key |
| **PPIO 派欧云** | ⚠️ **按"已取消"处理**：宣称的"永久免费版 Qwen2.5-7B"仅见于 2025-07 文档，2026 定价页**未见免费模型**，实际标价 ¥0.35/Mt | `https://api.ppio.com/openai` | 未实名 RPM 限 1 |

### 2.2 只是"新用户一次性赠送"🟡（别做架构依赖）

| 平台 | 赠送内容 | 有效期 | 备注 |
|---|---|---|---|
| **阿里云百炼** | 每模型 ~100 万 token，70+ 模型 | **90 天** | 仅华北2（北京）；免实名可用；未实名"用完即停"。✅ **另有一条独立的每日刷新额度**：**OAuth 认证每天 2,000 次调用**，与控制台 API Key 体系分开、**控制台不显示** |
| **火山方舟（豆包）** | 🟡 每模型 50 万 token | — | 官方页存在但数值未从正文核实 |
| **腾讯混元** | 100 万 tokens 资源包（embedding 另 100 万） | **1 年** | 到期不自动转后付费，会直接报错 |
| **Kimi 月之暗面** | 15 元券 | 3 个月 | **不能用于 Kimi K3**；无永久免费模型 |
| **华为云 ModelArts Studio** | 每模型 200 万（官方指南）/100 万（旧博客） | — | 仅华东二；需手动"领取额度"；base_url 领后取 |
| **天翼云息壤** | DeepSeek 系每模型 2500 万；其他 100 万 | **2 周** | 文档标注"停止维护" |
| **潞晨云 / 百川 / 有道 / 零一万物** | ¥20 / 80 元 / 10+40+50 元 / ¥10 | 各异 | 数值来源参差，需自行核 |

### 2.3 已失效或需警惕 🔴

- **无问芯穹 GenStudio**：官方 FAQ —— **自 2026-03-30 起停止提供基础版 LLM API 免费服务**（文档里"海量 Token 免费调用"是过时文案）。嵌入/重排序 API 仍暂不收费。
- **智谱 `glm-4.5-flash`**：**2026-01-30 下线**，自动路由到 GLM-4.7-Flash。
- **讯飞 Max**：2026-03-10 下线并入 Ultra。
- **腾讯元宝 / 京东言犀**：无公开免费 API（元宝是 C 端产品）。
- **移动九天**：需人工审核且社区反馈"审核极慢甚至无回执"，base_url/限额均无官方页。

---

## 3. 无鉴权 / 匿名可用网关 🟠（本文实测）

| 渠道 | 入口 | 实测结果（2026-09-20） | 条款 |
|---|---|---|---|
| **Pollinations.AI** | `https://text.pollinations.ai/openai` | ✅ **实测无 key 调用成功**，返回 `gpt-oss-20b`，`user_tier: anonymous`。模型列表只有 1 个匿名模型：`openai-fast` | MIT 开源项目；匿名 1 次/15s |
| **LLM7.io** | `https://api.llm7.io/v1` | ✅ **实测 `Authorization: Bearer unused` 调用 `GLM-5.3-Flash` 成功**；部分模型返回 "currently unavailable"（模型级可用性波动大）。额度约 **50 万 tokens/24h、10/min、60/h，仅 turbo 档** | 匿名 key `unused`；注册 dash.llm7.io 提额 |
| **AI Horde** | `https://aihorde.net` | ✅ 公开模型列表可读；**kudos 众包算力**，匿名 key `0000000000`（并发优先级最低）。实测部分模型队列 6500+，ETA 10 分钟级 | 志愿者算力；kudos 不可买卖 |
| **Kilo Gateway** | `https://api.kilo.ai/api/gateway` | ✅ 实测模型列表公开可读，23 个免费模型，免账号；限流 **200 请求/小时/IP** | 警告：可能记录 prompt 用于训练 |
| **OVHcloud AI Endpoints** | `https://oai.endpoints.kepler.ai.cloud.ovh.net/v1` | 官方文档：**匿名 2 RPM**/IP/模型 | 数据不落地、欧盟合规 |

---

## 4. 社区公益站 / 中转站 🔴（**强烈建议不用于任何真实工作**）

- 入口生态：`gongyizhan.com`（存活探测）、`github.com/1sh1ro/ai-api-zhongzhuan`、`jliushi.github.io/ai-relay`、`baipiao.org/relay/risk-radar`（跑路名单）、linux.do「福利羊毛」版
- 形态：NewAPI/OneAPI 站 → 注册建令牌 → `https://站点/v1` → 签到/积分换额度
- 实证风险（**这不是"可能跑路"级别，是供应链投毒级别**）：
  - 2026-09 对 428 个 LLM Proxy 的实测：**17 个自动抓取诱饵云凭证**、**9 个主动篡改 Agent 指令植入反弹 Shell/后门（含付费站）**、1 个转走测试钱包 ETH；91.1% 的开发会话跑在免确认 YOLO 模式（[来源](https://zgeo.net/news/llm-proxy-supply-chain-security-geo-guide)）
  - 同批事件中某头部中转站 **6TB 未脱敏日志**被买下，泄露 19 家公司的内网 Git 地址、SSH 密钥、阿里云 AK（[报道](https://www.163.com/dy/article/L6KRKP0B05561FZE.html)）
  - 站点可在返回内容里**插入广告**；已知跑路名单：88 Code、Privnode
- 违规红线（要避开）：**ChatGPT 反代**（违反 OpenAI 服务协议，账号共享/转售，极易封号）、**Kiro/账号逆向**（有站点被曝每次请求注入 ~5000 token 隐藏系统提示并按你的输入计费）、**gpt4free 类**（伪造请求头绕过鉴权；未审计更新有后门风险）
- 判定：**"免费"的真实对价是你的 prompt 和机器凭据。**

---

## 5. 怎么选：按用途

| 用途 | 首选 | 备选 | 理由 |
|---|---|---|---|
| Agent/编程助手 | **Z.ai GLM-4.7-Flash**（免费、200K、Anthropic 兼容） | OpenRouter `:free`、Kilo 免费路由 | 唯一同时免费 + 长上下文 + 双协议 |
| 高吞吐批处理（分类/抽取/翻译） | **Gemma 4/3 @ Gemini 免费层**（14,400 RPD） | Gitee AI 100/日、Cloudflare 10k Neurons | 日额度量级碾压其他免费档 |
| 需要"强模型偶尔问一次" | **Gemini Flash 免费层**（20 RPD） | GitHub Models GPT-5（150 RPD / 低档） | 免费层能碰到 frontier 模型 |
| 低延迟交互 | **Groq** `gpt-oss-120b` | SambaNova、NVIDIA NIM | Groq 是当前最快的免费推理 |
| 中文场景 | **智谱 / 百度千帆 / 讯飞 / 硅基流动** | 魔搭 2000 次/日 | 中文语料与合规更顺 |
| 零门槛试跑（不注册） | **Kilo Gateway**（200 次/时）→ **Pollinations** → **LLM7**（`unused`） | AI Horde、OVHcloud 匿名 2 RPM | 均实测可用，仅供 demo |
| 一个 key 打通所有 | **OpenRouter** | Kilo Gateway | 统一 OpenAI 协议 + 自动 fallback |
| 完全离线/不出网 | 本机 llama.cpp + GGUF（ROCm） | Ollama | 唯一能满足"数据不外流"的选项 |

---

## 6. 把免费 API 接进 DSH / 任意 OpenAI 兼容客户端

DSH 的 provider 注册在 `~/.dsh/settings.yaml` 的 `llm-pi-ai.providers.<名字>` 下，然后由 `subagent-model-selection.allowedModels` 决定子 agent 能用哪些。**照抄下面这段、只改 key 环境变量名即可**（示例：Z.ai 免费 GLM + Groq）：

```yaml
llm-pi-ai:
  providers:
    zai-free:
      displayName: "Z.ai GLM Flash (免费)"
      apiKeyEnv: ZAI_API_KEY
      api: openai-completions
      baseURL: https://api.z.ai/api/paas/v4
      models:
        - id: glm-4.7-flash
          name: "GLM-4.7-Flash (free, 200K)"
          contextWindow: 203000
          maxTokens: 16384
          input: [ text ]
    groq-free:
      displayName: "Groq free tier"
      apiKeyEnv: GROQ_API_KEY
      api: openai-completions
      baseURL: https://api.groq.com/openai/v1
      models:
        - id: openai/gpt-oss-120b
          name: "gpt-oss-120b @ Groq"
          contextWindow: 131072
          maxTokens: 32768
          input: [ text ]
```

要点：
1. **key 放环境变量**（`apiKeyEnv`），不要写进 yaml。
2. `api: openai-completions` 对应 OpenAI 的 `/chat/completions`；打 Anthropic `/v1/messages` 协议的网关要走别的 api 值。
3. 免费档必须配 **fallback 链**（免费 → 付费 → 本地），单点一定会在限流时断掉。
4. 改完 `~/.dsh/settings.yaml` 需重启 `dsh-web.service` 才生效（会中断当前会话）。

---

## 7. 已失效 / 常见误传纠正

| 流传说法 | 实际（2026-09-20） | 依据 |
|---|---|---|
| ❌ "Cerebras 有永久免费层，gpt-oss-120b 免费" | **无永久免费层**。官方 FAQ 原文：新账号**加了已验证支付方式**才拿 **$5 试用金，30 天过期**；"Cerebras doesn't currently offer a no-cost tier that renews automatically or a per-model always-free allowance"。**各个 awesome 清单里的 Cerebras 免费条目均已过时** | [Cerebras 限流文档](https://inference-docs.cerebras.ai/support/rate-limits)（本文实测抓取） |
| ❌ "NVIDIA NIM 注册送 1000/5000 credits" | **credit 制已取消**，改为按模型的、不公开的限流；40 RPM 是历史观测值 | [NVIDIA 论坛](https://forums.developer.nvidia.com/t/api-rate-limit-increase-is-not-granted-by-requesting-it-here/368420) |
| ❌ "Chutes.ai 是免费渠道" | **按量付费**（Plus $10/月、Pro $20/月），无免费层 | [Chutes 文档](https://chutes.ai/docs/guides/starter-guide) |
| ❌ "无问芯穹 GenStudio 海量 Token 免费" | **2026-03-30 起停止基础版 LLM API 免费服务**（文档旧文案未删） | [Infini 计费文档](https://docs.infini-ai.com/gen-studio/api/usage-and-billing/rate-limit.html) |
| ❌ "Anthropic 有免费 Claude API 档" | **没有持续免费层**。官方 pricing 只说"新用户获得少量免费额度"，**未给金额**（第三方称 $5/14 天，非官方）。想要免费 Claude 体验只能把 Claude Code 指向免费后端（`ANTHROPIC_BASE_URL` → Z.ai/Groq/NVIDIA） | 官方无 free tier |
| ❌ "Together AI 有免费试用" | **2025-07 已取消**，现最低购 $5 且**需绑卡**。serverless 表里的 `-Free` / $0 模型前置条件不明，**以控制台为准** | 官方改版公告 |
| ❌ "Glhf.chat 无限免费" | **2026-09-20 实测站点与 API 均 522 / TLS 失败**，已不可用 | 实测 |
| ⚠️ "Groq 每日 14,400 次" | 那是 `meta-llama/llama-prompt-guard-2-*` **分类器**的额度，不是聊天模型的。聊天模型是 30 RPM / **1,000 RPD** | 官方限流表 |
| ❌ "硅基流动 `THUDM/GLM-Z1-9B-0414` 已收费" | **这条修正本身是错的，已撤回**。官方页面内嵌目录显示它仍是 `price=0`、`status=normal`、131K 上下文、支持 tools。页面上根本不存在 `0.086` 这个数 | 官方 pricing 页 flight data（2026-09-20 实取） |
| ⚠️ "硅基流动免费模型只有少数几个" | 公开定价表首屏只渲染部分行；**页面内嵌完整目录里有 11 个免费 chat 模型**，含 **`Qwen/Qwen2.5-72B-Instruct`**（72B 级、tools、免费）——各类清单普遍漏报 | 同上 |
| ❌ "腾讯 `hunyuan-lite` 永久免费" | **2026-06-22 起模型列表与免费额度表均无它**，2024 年的"全面免费"公告已失效 | 腾讯云产品概述 |
| ❌ "PPIO 有永久免费模型" | 该说法仅见于 2025-07 文档；**2026 定价页无免费模型**，`qwen2.5-7b-instruct` 标价 ¥0.35/Mt，按**已取消**处理 | PPIO 定价页 |
| ⚠️ "讯飞 Spark Lite 无限量" | 官方接口文档**未给 QPS**，"无限量"无官方依据；官方活动页免费包标 **QPS 2** | 讯飞文档 / 活动页 |
| ⚠️ 商汤 base_url | 正确值是 **`https://api.sensenova.cn/compatible-mode/v1`**，不是 `platform.sensenova.cn` 或 `token.sensenova.cn` | 商汤官方新闻 + FAQ |
| ⚠️ "ModelScope 每日 2000 次" | 2024 年公告口径，**2026-09 现状未核实** | 社区整理，非官方条款页 |
| ⚠️ "免费 API 随便用没风险" | 免费层普遍用于训练（Google 明写、Mistral 默认开）；中转站存在真实投毒案例 | 见 §1.1 / §1.3 / §4 |

---

## 8. 情报源（建议每季度复查）

- <https://github.com/cheahjs/free-llm-api-resources> —— 更新最勤的免费清单，覆盖免费层 + 试用金，**但对 Cerebras 之类的条目也会滞后**
- <https://freellm.net> / <https://github.com/open-free-llm-api/awesome-freellm-apis> —— 结构化目录，声称每日刷新，含 base_url 与一键配置
- <https://freellmapihub.com> —— 每条带**核验日期**，区分 no-card / no-phone / 可商用，质量较高
- <https://lmspeed.net/free> —— 免费模型 + 实测速度/延迟
- 官方限流页（数字唯一权威）：Gemini AI Studio Limits、Groq `/docs/rate-limits`、Cloudflare Workers AI Pricing、SambaNova `/docs/en/models/rate-limits`、OpenRouter `/docs/api-reference/limits`
- 国内：<https://github.com/dawn0731/cn-freellm>（把十家国内免费额度聚合成一个 OpenAI 端点，`src/catalog.ts` 有核实目录）

**自查方法**（比看任何清单都可靠）：
```bash
# OpenRouter：列出当前所有免费模型
curl -s https://openrouter.ai/api/v1/models | \
  python3 -c "import json,sys;[print(m['id']) for m in json.load(sys.stdin)['data'] if float(m['pricing']['prompt'])==0 and float(m['pricing']['completion'])==0]"

# Kilo 免费路由
curl -s https://api.kilo.ai/api/gateway/v1/models | grep -o '"id":"[^"]*:free"'
```

---

## 9. 风险与合规（必读）

1. **数据用于训练**（按干净度排序）：
   - ✅ **相对干净**：**Cloudflare Workers AI**（官方明确不训练/不改进/不外泄）、**Groq**（默认不留存，可开 ZDR）、**Fireworks / Baseten**（默认 ZDR）、**OVHcloud**（欧盟，数据不存储不复用）
   - ⚠️ **可能训练**：**OpenRouter 免费变体**（官方明示可能记录并用于训练，隐私设置可关）、**GitHub Models 个人档**（可退出，企业版不训练）、**Kilo Auto Free**（官方警告）、**OpenCode Zen 免费型号**、**OpenAI 数据共享 token**（开启即同意训练）、**Z.ai 个人内容**（ToS 2026-04-14）
   - ❌ **明确会训练**：**Google 免费层**（定价页 `Used to improve our products: Yes`，人工审核员可读）、**Mistral 免费/实验路径**（默认开启，**Vibe 与 API 两个退出开关独立**互不覆盖）
   → 不要在免费层提交机密、客户数据、生产凭据。
2. **商用与转售**：OpenRouter ToS 禁止"转售 API 访问"与"开发竞品服务"；Cohere 试用 key 限非商业；OpenAI 禁账号共享/密钥买卖。→ **不得把免费 key 包装成对外服务**。
3. **中转站 = 供应链风险**：站方能解密并留存全部 prompt/上下文/输出；2026-09 已实证存在主动投毒（篡改 Agent 指令、植入后门）。→ 只用官方端点，或本机模型。
4. **key 管理**：一律走环境变量/密钥管理器；`.env` 进 gitignore；每 provider 独立 key 便于按站吊销；**禁止截图外发、禁止写进客户端配置文件**。
5. **稳定性**：免费档限流随时改、模型随时下线（GLM-4.5-Flash、讯飞 Max 都是今年下线的）。→ 客户端必须实现 429 指数退避 + 多 provider fallback + 本地兜底。
6. **Agent 收紧**：关闭 YOLO/免确认模式，限制可读路径，禁止 Agent 读取 `.env`、`~/.ssh`、云凭据文件。

---

## 附：本文档的一手实测记录（2026-09-20）

| 验证项 | 方法 | 结果 |
|---|---|---|
| OpenRouter 免费模型数 | `GET https://openrouter.ai/api/v1/models` | 446 总 / **24 免费**（prompt & completion 双 $0） |
| OpenRouter 免费模型工具能力 | 解析 `supported_parameters` | **19/24 支持 tool calling**，最大上下文 1,048,576（`thinkingmachines/inkling:free`） |
| Kilo Gateway 免费模型数 | `GET https://api.kilo.ai/api/gateway/v1/models` | 380 总 / **23 免费**，含 `kilo-auto/free` |
| Pollinations 无 key 可用性 | `POST https://text.pollinations.ai/openai` | ✅ 成功，`user_tier: anonymous`，模型实为 `gpt-oss-20b` |
| LLM7 匿名 key | `POST https://api.llm7.io/v1/chat/completions`，`Bearer unused` | ✅ `GLM-5.3-Flash` 成功；`DeepSeek-V4-Flash-0731` 报 invalid key（模型级可用性差异） |
| AI Horde 公开接口 | `GET https://aihorde.net/api/v2/status/models?type=text` | ✅ 可读，部分模型队列数千 |
| Cerebras 免费层 | 抓取官方 rate-limits 页正文 | ❌ 官方明写 "Is there a permanently free tier? No." |
| Cloudflare 免费额度 | 抓取官方 pricing 页正文 | ✅ "10,000 Neurons per day"，每日 00:00 UTC 重置 |
| Gemini 免费层条款 | 抓取官方 pricing 页 | ✅ 多模型 `Free Tier / Free of charge`，且 `Used to improve our products: Yes` |
| GitHub Models 限额 | 抓取官方文档表 | ✅ Copilot Free：Low 15 RPM/150 RPD；High 10 RPM/50 RPD |
| SambaNova 免费层 | 抓取官方 rate-limits 文档 | ✅ 免费档每模型 20 RPM / 20 RPD / 200K TPD |
| OVHcloud 匿名额度 | 抓取官方 capabilities 文档 | ✅ 匿名 2 RPM/IP/模型；带 key 400 RPM |
| OVHcloud 匿名实测 | `POST .../v1/chat/completions` 不带 key | ✅ 端点可达、匿名放行，但返回 `API rate limit exceeded`（印证 2 RPM 极紧） |
| Scaleway 免费额度 | 抓取官方 FAQ | ✅ 1,000,000 tokens（一次性） |
| Vercel AI Gateway | 抓取官方 pricing 页 | ✅ 免费档 $5/月，全模型可用 |
| Hugging Face 免费额度 | 抓取官方 pricing 文档 | ✅ Free 用户 $0.10/月，PRO $2/月 |
| Cerebras Free Trial 限流 | 抓取官方 rate-limits 页 | 5 RPM / 30K TPM / 1M TPH / 1M TPD（gpt-oss-120b、zai-glm-4.7、gemma-4-31b） |
| OpenCode Zen 免费档 | 裸 key 调用免费型号 | ❌ **403**：「免费档只能在 OpenCode 客户端内用」——不是通用 API |
| Glhf.chat 可用性 | 访问站点与 API | ❌ **522 / TLS 失败**，已不可用（第三方"无限免费"说法不成立） |
| Kilo Gateway 限流 | 官方文档 | 免费模型 **200 请求/小时/IP** |
