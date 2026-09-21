# 海外大模型推理平台「免费 API 层」现状

**核实日 2026-09-20。** 英文 web_search 多轮检索；官方页优先，第三方站标「非官方/二手」；无官方依据一律写「未核实」，不补数字。免费模型清单与限速为**当日快照**，随时变动。

## A. 主力平台（领 key / 免费形式 / 限额 / 兼容与 base_url / 门槛 / 数据与坑 / 可信度）

**OpenRouter** `openrouter.ai/settings/keys`｜永久 `:free`：官方定价页称 Free 档 25+ 免费模型、4 免费 provider（2026-08 非官方快照 14 个零价模型：`nemotron-3-ultra:free`、`gpt-oss-20b:free`、`gemma-4-26b-a4b:free`、`north-mini-code:free` 等），另有 `openrouter/free` 随机路由｜**20 RPM；未充值 50 RPD；累计充值 ≥$10 后 1000 RPD**｜`https://openrouter.ai/api/v1`｜无卡｜坑：官方明示免费变体 prompt/completion 可能被记录并**用于训练**（隐私设置可关），免费端点周变、不可作生产依赖｜可信度：高

**Google AI Studio / Gemini API** `aistudio.google.com/apikey`｜永久 Free tier，Flash/Flash-Lite $0｜官方页（更 2026-09-02）**不再公布 RPM/RPD，改在 AI Studio 查看**；二手（2026-06）称 2.5 Pro 5 RPM/25 RPD、2.5 Flash 10/500、2.0 Flash-Lite 30/1500——**未核实**｜`https://generativelanguage.googleapis.com/v1beta/openai/`｜无卡｜坑：Unpaid Services 内容会被人工评审并用于改进产品；2026-03 起 $300 GCP 试用金不再覆盖 Gemini API｜可信度：高（免费层与条款）/ 数值中

**Groq** `console.groq.com/keys`｜永久免费层，全模型｜主流聊天模型 **30 RPM / 1K RPD / 8K TPM / 200K TPD**；`groq/compound(-mini)` 30/250；Whisper 20 RPM/2K RPD；prompt-guard **14.4K RPD 是分类器、非聊天额度**（常见误传）；按组织计、多 key 不叠加｜`https://api.groq.com/openai/v1`｜邮箱或 GitHub，无卡｜默认不留存，可开 ZDR｜可信度：高

**Cerebras** `cloud.cerebras.ai`｜**已取消永久免费层**（官方 FAQ：No）；现为 Free Trial，**须先绑已验证支付方式**，$5 / 30 天｜`gpt-oss-120b`、`zai-glm-4.7`、`gemma-4-31b` 均 **5 RPM / 30K TPM / 1M TPH / 1M TPD**，用尽须付费才恢复 API｜`https://api.cerebras.ai/v1`｜**需卡**｜可信度：高

**NVIDIA NIM** `build.nvidia.com/settings/api-keys`｜全模型 trial，官方称**无需信用卡、不限时间**｜官方**不公开**限速（按模型/流量浮动，个人上限显示在站点右上角）；论坛普遍报 **40 RPM**，官方称无升额渠道｜`https://integrate.api.nvidia.com/v1`｜无卡｜坑：trial 仅限原型/测试，**转生产必须购 NVIDIA AI Enterprise**｜可信度：高

**Cloudflare Workers AI** `dash.cloudflare.com`｜**10,000 Neurons/天**（Free/Paid 均给）｜按 Neuron 计，无公开 RPM；kimi-k2.6/2.7、glm-5.x、deepseek-v4 等需付费计划｜`https://api.cloudflare.com/client/v4/accounts/{acct}/ai/v1`｜无卡｜官方明确**不训练、不改进、不外泄**用户内容｜可信度：高（更 2026-09-17）

**GitHub Models** GitHub PAT（`models:read`）`github.com/settings/tokens`｜按 Copilot 档位永久免费额度，超出可 opt-in 付费或 BYOK｜Low 15 RPM/150 RPD、High 10 RPM/50 RPD、Embedding 15 RPM/150 RPD；单请求 8K in+4K out、并发 5；o1/o3/gpt-5 类仅 Pro 起 **1 RPM/8 RPD**｜`https://models.github.ai/inference`｜Copilot Free 即可，无卡｜坑：**个人档数据可能被 GitHub 用于训练**（可退出），企业版不训练｜可信度：高

**Mistral（La Plateforme + Codestral）** `console.mistral.ai` → API Keys｜**Free mode 官方称无需信用卡**、含每月 included usage｜官方只给维度（RPS/TPM/月 token），**具体值在 Admin Panel › Limits**——未核实｜`https://api.mistral.ai/v1`（Codestral 同平台）｜第三方称 key 创建需手机验证（官方未提）——未核实｜可信度：中高

**Cohere** `dashboard.cohere.com/api-keys`｜Trial（evaluation）key 永久｜**1,000 calls/月**；Chat 各模型 trial **20 req/min**｜`https://api.cohere.ai/compatibility/v1`（未逐条核实）｜无卡｜trial 条款与生产不同，商用需 production key｜可信度：中高

**Hugging Face Inference Providers** `huggingface.co/settings/tokens`｜**每月 $0.10**（Free 用户，官方称可能变动；PRO $2）｜以美元计，无公开 RPM——未核实；旧 Serverless API 约「每小时数百请求」且限 <10B 模型｜`https://router.huggingface.co/v1`｜无卡｜可信度：中高

**Together AI** `api.together.ai`｜**无免费试用**（官方 2025-07 改版：最低购 $5）；官方 serverless 表仍有 **$0 定价模型**（如 `Ternary-Bonsai-27B`），但调用前置条件未核实｜限额未公布（`-Free` 端点「低速率」）｜`https://api.together.xyz/v1`｜**需卡**｜可信度：中高

**SambaNova Cloud** `cloud.sambanova.ai`｜**Free Tier 永久存在**（未绑卡态）｜`DeepSeek-V3.1`、`Meta-Llama-3.3-70B`、`gpt-oss-120b` 各 **20 RPM / 20 RPD / 200K TPD**（**RPD 仅 20，极紧**）｜`https://api.sambanova.ai/v1`｜无卡｜可信度：中高（同域存在新旧快照）

**Scaleway Generative APIs** `console.scaleway.com`｜一次性 **100 万 tokens**（或 60 分钟音频）｜需**已验证支付方式**才有 **300 RPM / 200K TPM / 并发 100**，再验证身份翻倍；无卡时额度未核实｜`https://api.scaleway.ai/v1`｜可信度：中

**OVHcloud AI Endpoints** `ovhcloud.com/en/public-cloud/ai-endpoints/`｜**匿名 2 RPM** 免费 + 新用户 **$200 Public Cloud 试用金**（1 个月、仅首项目）｜带 key **400 RPM / 项目 / 模型**｜`https://oai.endpoints.kepler.ai.cloud.ovh.net/v1`（未逐条核实）｜官方称数据不存储不复用｜可信度：中高

**Z.ai（海外 GLM）** `z.ai`｜**永久 $0 模型**：`GLM-4.7-Flash`、`GLM-4.5-Flash`、`GLM-4.6V-Flash`（官方 pricing）｜官方未公布（指向需登录的 rate-limits 页）；非官方称约 1 并发、~1 req/s｜`https://api.z.ai/api/paas/v4`（官方确认 OpenAI 兼容，URL 未逐字核实）+ Anthropic 端点 `https://api.z.ai/api/anthropic`｜无卡｜坑：ToS（2026-04-14）允许将个人用户内容用于训练｜可信度：中高

**xAI** `console.x.ai`｜**无常规免费层**（官方 quickstart 2026-08-18 要求先充值；旧 $25/月公测政策已终止）。二手称 Data Sharing Program 给 **$150/月**（需已消费 ≥$5、管理员开启、非排除地区）——**未核实**｜`https://api.x.ai/v1`｜可信度：中（无免费层高 / $150 低）

**OpenAI** `platform.openai.com/api-keys`｜**无永久免费层**；官方唯一持续免费 = **数据共享补偿 token**：1M/日（Tier1-2 为 250k）、mini 类 10M/日（2.5M），UTC 00:00 重置｜**需账户有正余额**；新号 ~$5 自动试用金「已不稳定」（非官方）｜`https://api.openai.com/v1`｜坑：开启共享即同意用于训练｜可信度：高

**Anthropic** `platform.claude.com`（官方已改域）｜官方 pricing 仅称「新用户获得少量免费额度」、**未给金额**；第三方称 **$5 / claim 后 14 天 / 需短信验证**——非官方｜免费层约 5 RPM（非官方）｜`https://api.anthropic.com`｜手机验证｜可信度：低-中

**DeepSeek 官方** `platform.deepseek.com/api_keys`｜**无免费层**；官方 pricing 仅提 "granted balance" 赠额机制、无公开规则；新号送额说法金额不一致——未核实｜`https://api.deepseek.com`｜需充值｜可信度：高（无免费层）

## B. 其他平台与网关（含关键陷阱）

**GPU 云 / 平台**
- **Nebius Token Factory**（原 AI Studio）`tokenfactory.nebius.com`｜一次性 **$1 / 30 天**｜**强制绑卡**｜`https://api.tokenfactory.nebius.com/v1/`｜限流动态不公开；免费额度可随时撤销
- **Fireworks AI** `fireworks.ai/signup`｜一次性 **$1**｜**未绑卡 10 RPM**、绑卡后上限 6000 RPM｜`https://api.fireworks.ai/inference/v1`｜默认 ZDR、不训练
- **Baseten** `app.baseten.co`｜新 workspace 赠额（**金额官方未公布**）｜Basic 未验证 **15 RPM / 100k TPM**，已验证 120 RPM / 500k TPM｜`https://inference.baseten.co/v1`｜ZDR
- **Modal** `modal.com/signup`｜**每月 $30 计算额度**｜100 容器 / 10 GPU / 3 席位｜**必须绑卡**｜**无 OpenAI 兼容端点**（SDK 平台）
- **Novita AI** `novita.ai/user/register`｜新用户 voucher（金额未公布）；官方宣传 **$100 Sandbox / 90 天**（非 Model API）｜分层动态无静态值｜`https://api.novita.ai/openai/v1`｜ToS 禁批量注册套额度、费用不退
- **Inference.net** `inference.net/register/`｜Free $0 计划（赠额未公布，第三方 $25 非官方）｜**30 RPM**｜`https://api.inference.net/v1`｜未设价的公开 serverless 部署可免费
- **Chutes.ai** `chutes.ai/app`｜**官方明示无免费层**（旧 200 请求/天 2026-03 关停）｜`https://llm.chutes.ai/v1`｜须充值｜TEE 加密
- **Nscale** `console.nscale.com`（仅 Google SSO）｜博文称 **$5**、现行文档只写「需购买 $5 起」——**存疑**｜官方称 serverless 不强制限流｜`https://inference.api.nscale.com/v1`｜称不记录不训练
- **Hyperbolic** `hyperbolic.ai`｜Free 档无最低消费但「限速很紧」、不能开 GPU/存储｜具体 RPM 未公开——未核实
- **AI21 Studio** `studio.ai21.com`｜新账号 **$10 / 3 个月**，过期须绑卡｜`https://api.ai21.com/studio/v1`（兼容性未核实）
- **Upstage** `console.upstage.ai`｜2025 官方博客称注册送 **$10**（现行是否有效未核实）；每 agent 10 次免费运行、教育/非营利可申请 Solar Pro 免费一年｜`https://api.upstage.ai/v1`

**网关 / 聚合（免费额度多为日志或请求量，不是 token）**
- **Cloudflare AI Gateway** `dash.cloudflare.com`｜网关本体免费（缓存/限流/分析）｜免费计划 10 gateway、10 万条日志总量；Unified Billing **200 req/60s**（BYOK 不受限）｜`https://gateway.ai.cloudflare.com/v1/{acct}/{gw}/openai`｜不训练
- **Vercel AI Gateway** `vercel.com/signup`｜**每月 $5 额度**（仅免费模型子集）｜按模型限速、数值未公布｜**官方要求团队绑支付方式**｜`https://ai-gateway.vercel.sh/v1`
- **OpenCode Zen** `opencode.ai/auth`｜7 个限时免费型号（Big Pickle、MiMo-V2.5 Free、Ling 3.0 Flash Fin Free 等）｜未公布｜`https://opencode.ai/zen/v1`｜**实测裸 key 403「免费档只能在 OpenCode 客户端内用」**；Muse Spark 1.3 明文用你的 prompt/输出训练 Meta 模型
- **Kilo Code / Kilo Gateway** `app.kilo.ai`｜`:free` 型号 + `kilo-auto/free` 路由，**匿名免 key 可用**｜**200 请求/小时/IP**（实测匿名 200）｜`https://api.kilo.ai/api/gateway`｜Auto Free 可能路由到会记录并用于改进的供应商
- **LLM7.io** `dash.llm7.io`（可匿名 `api_key="unused"`）｜匿名 50 万 tokens/24h、免费 token 100 万/24h，仅 turbo 型号｜匿名 1/s、10/min、60/h（docs 与 GitHub TERMS 冲突——存疑）｜`https://api.llm7.io/v1`｜禁多账号/转售/VPN 绕限
- **Pollinations.AI** `enter.pollinations.ai`｜**匿名免注册**可用免费模型（实测 200）｜匿名 1 请求/15s、Seed 1/5s（官方页与新版 Pollen 口径冲突——存疑）｜`https://text.pollinations.ai/openai`
- **AI Horde** `aihorde.net/register`（匿名 key `0000000000`）｜众筹算力、无 token 额度，kudos 定优先级｜无公开 RPM；kudos 税 1+1｜**无官方 OpenAI 兼容端点**（原生异步 REST）｜kudos 不可买卖
- **Glhf.chat**｜**站点不可达**：2026-09-20 实测 glhf.chat 与 API 均返 Cloudflare 522 / TLS 失败｜无官方免费层页，**存疑**，勿采纳第三方「无限免费」说法
- **Ollama Cloud** `ollama.com/settings/keys`｜Free $0 + 按月 starter credits（数值未公布）｜**1 并发**；官方 blog（2026-08-31）明确无「5 小时/周」限制（第三方说法过时）｜`https://ollama.com/v1`｜无卡｜官方称不保留数据
- **DuckDuckGo duck.ai**｜**无官方 API**（p2d-duck 等为逆向、不受支持）；免费模型：Claude 4.5 Haiku、Llama 4 Scout、Mistral Small 3 24B、GPT-4o/5 mini、gpt-oss-120b｜每日限额官方确认存在但**未公布**、00:00 UTC 重置｜无 OpenAI base_url｜官方称不留存不训练
- **Requesty** `router.requesty.ai/v1`｜免费模型：官方两页冲突（**50 vs 200 请求/日**）｜未核实
- **Portkey** `api.portkey.ai/v1`｜Dev 免费 **10k 日志/月**，超限只丢日志不限请求、保留 3 天
- **Helicone** `ai-gateway.helicone.ai`｜Hobby **10k 请求/月、1GB、保留 7 天**
- **LiteLLM**｜自托管 OSS 永久免费；**托管云版免费层未找到官方页——存疑**
- **NotDiamond**｜官方无免费层；AWS Marketplace 列 Discovery $0（≤10 万路由请求/月）——存疑
- **Unify.ai / Martian**｜官网 pricing 已 404，第三方所称免费额度**不可信**
- **AnyRouter** `anyrouter.dev/pricing`｜Free 无赠额；免费模型需 Go（$2/mo）或捐 key，**1000 请求/日、60 req/min**

## C. 总表

| 名称 | 免费形式 | 限额 | 需卡 | base_url | 亮点模型 |
|---|---|---|---|---|---|
| OpenRouter | 永久 `:free` | 20 RPM；50→1000 RPD（充值≥$10） | 否 | openrouter.ai/api/v1 | nemotron-3-ultra、gpt-oss-20b、gemma-4 |
| Gemini API | 永久 Free tier | 官方未公开（AI Studio 内查看） | 否 | generativelanguage.googleapis.com/v1beta/openai/ | Gemini Flash / Flash-Lite |
| Groq | 永久免费层 | 30 RPM/1K RPD/8K TPM/200K TPD | 否 | api.groq.com/openai/v1 | gpt-oss-120b、qwen3.6-27b |
| Cerebras | $5/30 天（无永久层） | 5 RPM/30K TPM/1M TPD | **是** | api.cerebras.ai/v1 | gpt-oss-120b、zai-glm-4.7 |
| NVIDIA NIM | trial（不限时、无卡） | 未公开（普遍 40 RPM） | 否 | integrate.api.nvidia.com/v1 | Nemotron 系 |
| Cloudflare Workers AI | 10k Neurons/天 | 按 Neuron，无公开 RPM | 否 | api.cloudflare.com/client/v4/accounts/{id}/ai/v1 | llama、@cf 系列 |
| GitHub Models | 永久免费额度 | 15 RPM/150 RPD（Low 档） | 否 | models.github.ai/inference | GPT/Claude/Grok 多厂 |
| Mistral | Free mode | 未公开（Admin Limits 页） | 否 | api.mistral.ai/v1 | mistral-small、Codestral |
| Cohere | Trial key | 1000 calls/月、20 RPM | 否 | api.cohere.ai/compatibility/v1（未核实） | Command A 系 |
| HF Inference Providers | $0.10/月 | 未公开 | 否 | router.huggingface.co/v1 | 路由至多厂开源模型 |
| Together AI | 无试用；有 $0 模型 | 未公开 | **是** | api.together.xyz/v1 | Ternary-Bonsai-27B |
| SambaNova | Free Tier 永久 | 20 RPM/**20 RPD**/200K TPD | 否 | api.sambanova.ai/v1 | DeepSeek-V3.x、gpt-oss-120b |
| Scaleway | 一次性 100 万 token | 300 RPM/200K TPM（需验证卡） | 是（速率档前置） | api.scaleway.ai/v1 | Qwen3、Mistral、glm-5.2 |
| OVHcloud | 匿名 + $200/1 月 | 匿名 2 RPM；带 key 400 RPM | 否 | oai.endpoints.kepler.ai.cloud.ovh.net/v1 | 开源权重模型 |
| Z.ai | 永久 $0 模型 | 官方未公布 | 否 | api.z.ai/api/paas/v4 | GLM-4.7/4.5/4.6V-Flash |
| xAI | 无（$150 数据共享未核实） | — | 是 | api.x.ai/v1 | Grok |
| OpenAI | 无；数据共享 token | 1M/10M 每日（需正余额） | 是（余额） | api.openai.com/v1 | GPT-5 系 |
| Anthropic | 少量（金额未官方） | 未公布 | 手机验证 | api.anthropic.com | Claude |
| DeepSeek | 无 | — | 充值 | api.deepseek.com | V4 系 |
| Nebius | $1/30 天 | 动态未公开 | **是** | api.tokenfactory.nebius.com/v1/ | 开源权重 |
| Fireworks | $1 | 未绑卡 10 RPM | 续用需 | api.fireworks.ai/inference/v1 | 开源权重 |
| Baseten | 赠额（未公布） | 15 RPM/100k TPM | 未核实 | inference.baseten.co/v1 | DeepSeek 系 |
| Modal | $30/月 | 100 容器/10 GPU | **是** | 无（SDK） | 自部署 |
| Novita | voucher + $100 Sandbox | 分层动态 | 否 | api.novita.ai/openai/v1 | 开源权重 |
| Inference.net | Free $0 | 30 RPM | 未核实 | api.inference.net/v1 | 开源权重 |
| Chutes.ai | **无免费层** | — | 充值 | llm.chutes.ai/v1 | 开源权重 |
| Nscale | $5（存疑） | 官方称不限流 | 购额需 | inference.api.nscale.com/v1 | 开源权重 |
| Hyperbolic | Free 档 | 未公开 | 否 | — | 开源权重 |
| AI21 | $10/3 月 | — | 否 | api.ai21.com/studio/v1 | Jamba |
| Upstage | $10（未核实） | — | 否 | api.upstage.ai/v1 | Solar |
| Cloudflare AI Gateway | 网关免费 | 10 万日志、200 req/60s | 否 | gateway.ai.cloudflare.com/v1/{a}/{g}/openai | — |
| Vercel AI Gateway | $5/月 | 未公布 | **是** | ai-gateway.vercel.sh/v1 | 免费模型子集 |
| OpenCode Zen | 限时免费型号 | 未公布 | 要账单信息 | opencode.ai/zen/v1（裸 key 403） | Big Pickle、Ling 3.0 |
| Kilo Gateway | `:free` + 匿名 | 200 请求/小时/IP | 否 | api.kilo.ai/api/gateway | ling-3.0-flash-fin:free |
| LLM7.io | 匿名 50 万 tok/日 | 10/min、60/h | 否 | api.llm7.io/v1 | DeepSeek-V4-Flash、GLM-5.3-Flash |
| Pollinations | 匿名 | 1 请求/15s | 否 | text.pollinations.ai/openai | gpt-oss-20b |
| AI Horde | 众筹算力 | 无 RPM，kudos 税 | 否 | 无官方 OpenAI 端点 | 社区模型 |
| Glhf.chat | **不可达（522）** | 未知 | 未知 | 历史 glhf.chat/api/openai/v1 | — |
| Ollama Cloud | Free $0 + starter 额度 | 1 并发 | 否 | ollama.com/v1 | 云端开源模型 |
| DuckDuckGo | 免费模型（无 API） | 每日限额未公布 | 否 | 无官方 API | Claude 4.5 Haiku、GPT-5 mini |
| Requesty / Portkey / Helicone / LiteLLM | 网关免费额度 | 50–200 请求/日；10k 日志/月 | 否 | router.requesty.ai/v1 等 | — |

**三条最实用结论**：①零卡零账号即可用的 OpenAI 兼容免费入口只有 Kilo Gateway（匿名 200 次/小时）、Pollinations（1 次/15 秒）、LLM7（匿名 50 万 tokens/日）；②Cerebras 已从「永久免费」改为「需绑卡 + $5/30 天」，SambaNova 免费档 RPD 仅 20，Together 已取消免费试用——这三家是 2025→2026 变化最大的；③免费层的真实代价是数据：Gemini 免费层、OpenRouter 免费变体、Kilo Auto Free、OpenCode Zen 免费型号、OpenAI 数据共享 token 都明示或可能用你的 prompt 训练，勿传敏感数据。
