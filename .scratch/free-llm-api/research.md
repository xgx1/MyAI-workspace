# 免费/公益 LLM API 渠道与风险合规调研

检索日期 2026-09-20，中英双语多轮 web_search。分级：🟢 官方免费层 · 🟡 无鉴权公益网关 · 🟠 社区中转公益站 · 🔴 违规逆向。

## 第一部分 渠道

### 🟢 官方免费层（条款明确，可商用但常被用于训练）

| 渠道 | 入口 | 免费范围与限制 | 关键条款/口碑 |
|---|---|---|---|
| Google AI Studio / Gemini API | ai.google.dev | 未付费额度 | 属 "Unpaid Services"：Google 用输入输出改进产品与 ML 技术，人工审核员可读取标注；EEA/CH/UK 例外 |
| Mistral La Plateforme | console.mistral.ai | 免费层 | 默认可能纳入训练；需到 Admin → Privacy 关 "Anonymous improvement data" |
| OpenRouter `:free` | openrouter.ai | 免费模型 | 未充值 50 次/日，充 ≥10 信用点 1000 次/日；官方称免费模型"通常不适合生产" |
| Groq / GitHub Models | 各自控制台 | 免费额度 | Groq gpt-oss-120b 30 RPM / 1K RPD / 200K TPD；GitHub Models Copilot Free 15 RPM / 150 RPD |
| Cloudflare Workers AI | dash.cloudflare.com | 10,000 Neurons/日 | 免费额度每日重置，超额转 Paid |
| NVIDIA NIM | build.nvidia.com | 免费推理端点 | 需手机验证 |
| ⚠️ Cerebras | cloud.cerebras.ai | **无永久免费层** | 仅 $5 试用额度，30 天过期且需绑支付方式 |
| ⚠️ ModelScope 魔搭 | modelscope.cn | 约 2000 次/日 | 社区整理文档口径，非官方条款页 |

### 🟡 开源/无鉴权公益网关

- **AI Horde**（aihorde.net）：志愿者算力众包，匿名 key `0000000000` 即用，但并发时优先级最低；Kudos 不可出售、不可购买。
- **Pollinations.AI**：无需注册、无 key，MIT；Anonymous 1 次/15s，Seed（免费注册）1 次/5s，Flower 付费、Nectar 企业。
- **LLM7.io**：`api.llm7.io/v1`，匿名 key 填 `unused`；dash.llm7.io 的 token 提额（约 30 → 120 RPM）。
- **Kilo Code**：`kilo-auto/free` 自动免费路由。官方明确警告：Auto Free 可能路由到会记录 prompt/输出并用于改进服务的 provider（含 NVIDIA 免费端点），"不要提交个人或机密数据"。模型清单随时变。
- **Cline**：限时轮换的免费模型推广，**仅 IDE 插件与 CLI 可用**，不对 Cline API 开放，额度用完即止。
- **Chutes.ai**：**并非免费渠道** —— 官方文档为按量付费（Plus $10/月、Pro $20/月，无最低承诺），跑在 Bittensor SN64，全模型 TEE。任务假设的 "Chutes 免费" 与现文档不符，需修正。
- 清单类：`open-free-llm-api/awesome-freellm-apis`（40+ provider 结构化目录）、`Free-AI-Things/g4f-working`（每日更新免鉴权可用清单）。

### 🟠 社区中转/公益站（NewAPI/OneAPI 生态）

聚合入口：gongyizhan.com（每日存活探测 + 历史快照）、`1sh1ro/ai-api-zhongzhuan`（GitHub 导航）、jliushi.github.io/ai-relay（实测清单，含邀请参数）、baipiao.org/relay/risk-radar（跑路名单）、linux.do「福利羊毛」版。
通用形态：注册 → 控制台建令牌 → Base URL 多为 `https://站点/v1` → 签到 / LDC 积分换额度。
稳定性口碑普遍差：导航站自标在线率 36%~100%，多家标注"历史失效 1~2 次"；jliushi 写明"按随时可能停来规划，别把它当主力，更别让它成为唯一的路"。
失效/跑路实证：baipiao 判 **88 Code、Privnode 已跑路**（后者被收购后可用率归零、退款拖延、随意封号）；**CowX API** 实测 chat 接口 503、Anthropic 接口 403；另有站点被曝在返回内容中插入广告。

### 🔴 违规/高风险（必须避开）

- **ChatGPT 反代**：把个人 Plus/Pro 账号转成 API。违反 OpenAI 服务协议 3.1（不得在多个用户间共享账号凭据、不得转售或出租账号访问）；社区实测"服务器反代 + 个人网页登录"造成双 IP 并发，极易触发风控封号。
- **Kiro / Max 账号逆向、"官转 + 逆向混合"**：CowX API 被标注后端为逆向 ChatGPT 账号，且**每次请求注入约 5000 token 隐藏系统提示并按你的输入计费**。明确违反禁止逆向工程与规避限流的条款。
- **gpt4free 类项目**：伪造请求头、劫持第三方端点绕过鉴权，WAF/指纹/验证码任一升级即失效；未审计更新有后门风险，Prompt 全量流向不可信第三方。
- **条款依据**：OpenAI 服务协议 3.3 明文禁止逆向工程、买卖/转让 API key、规避限流或绕过安全措施；Anthropic 消费者条款禁止逆向、爬取、以及在无 API key 情况下用自动化手段访问，商业条款禁止用于构建竞品。

## 第二部分 风险清单（附依据）

1. **免费层数据用于训练**：Google 未付费额度会用你的输入输出改进产品与机器学习技术，人工审核员可读取标注，官方直接写"不要向未付费服务提交敏感、机密或个人信息"；Mistral 免费与实验路径默认可能纳入训练，且 Vibe 与 API 两个退出开关相互独立。
2. **商用与转售限制**：OpenRouter ToS 第 4 条禁止"转售 API 访问"与"开发竞品服务"；OpenAI 禁账号共享与 key 买卖；Anthropic 禁构建竞品。→ 不得把免费 key 包装成对外服务。
3. **中转站明文留存与数据变现**：代理解密请求后再转发，Prompt/上下文/输出可被静默记录、匿名化打包，售给做 SFT/RLHF 的模型公司、数据经纪商与学术机构；1sh1ro 与 jliushi 两个导航站都写明"中转站能看到你发过去的全部请求内容"。
4. **实测供应链攻击（2026-09 披露，428 个 LLM Proxy 样本）**：17 个自动提取诱饵云凭证并发起未授权探测，9 个主动篡改 Agent 指令植入反弹 Shell 与后门（**含付费站**），1 个直接转走测试钱包 ETH；91.1% 的开发会话跑在免确认 YOLO 模式下；研究者顺链拿到约 400 台下游开发主机控制权。同批事件中，某头部中转站 **6TB 未脱敏日志** 被买下，泄露 19 家公司（小米、华为、蔚来、MiniMax 等）的内网 Git 地址、SSH 密钥、阿里云 AK、GitLab 令牌。
5. **稳定性/限流/跑路**：免费额度与倍率随时改，站点随时关停；跑路后余额基本无法追回。预警信号：可用率持续走低、客服失联、突然放大额充值优惠（清库存）、迁域名续售。
6. **key 泄露**：写入客户端配置、截图发公开 Issue/群、明文提交进仓库；中转站侧的 key 亦可能被复用或转卖。

## 第三部分 规避建议

- **数据分级**：机密、客户数据、生产凭据绝不经过任何第三方中转；只用本地模型（本机 ROCm + GGUF）或已签约的企业端点。
- **多 provider 轮换 + 本地兜底**：配置 fallback 链（官方免费层 → 付费官方 → 本地 ollama/llama.cpp），不把任何一家当唯一路径。
- **key 管理**：放环境变量或密钥管理器，`.env` 加 gitignore；每 provider 独立 key 便于按站吊销；禁止硬编码与截图外发。
- **关闭训练开关**：业务不要用 Google 免费层；Mistral 到 Admin → Privacy 关闭 "Anonymous improvement data"。
- **收紧 Agent**：关闭 YOLO/免确认模式，限制可读路径，禁止读取 `.env`、`~/.ssh`、云凭据文件。
- **如确要试公益站**：仅做非敏感 demo，专用邮箱 + 一次性 key，小额短期，绝不充值囤余额。

## 主要来源

- Google Gemini API 附加条款 https://ai.google.dev/gemini-api/terms
- Mistral 训练数据退出说明 https://help.mistral.ai/en/articles/455207
- OpenRouter FAQ / 限流 / ToS https://openrouter.ai/docs/faq · https://openrouter.ai/docs/api_reference/limits · https://openrouter.ai/terms
- OpenAI 服务协议 3.1/3.3 https://openai.com/policies/services-agreement/
- Anthropic 消费者条款 https://archive.ph/gqPaS
- AI Horde https://aihorde.net/ · Pollinations https://github.com/pollinations/pollinations · LLM7 https://docs.llm7.io/quickstart
- Kilo 免费用法 https://kilo.ai/docs/getting-started/using-kilo-for-free · Cline 免费模型 https://docs.cline.bot/getting-started/free-models
- Chutes 文档 https://chutes.ai/docs/guides/starter-guide
- Groq 限流 https://console.groq.com/docs/rate-limits · GitHub Models 限流 https://docs.github.com/en/github-models/use-github-models/prototyping-with-ai-models · Cloudflare Workers AI https://developers.cloudflare.com/workers-ai/platform/pricing/ · Cerebras https://inference-docs.cerebras.ai/support/rate-limits
- 公益站聚合与清单 https://gongyizhan.com/ · https://github.com/1sh1ro/ai-api-zhongzhuan · https://jliushi.github.io/ai-relay/ · https://baipiao.org/relay/risk-radar/
- 供应链安全实测 https://zgeo.net/news/llm-proxy-supply-chain-security-geo-guide · 6TB 日志泄露 https://www.163.com/dy/article/L6KRKP0B05561FZE.html · 中转站数据变现 https://finance.sina.com.cn/tech/roll/2026-05-24/doc-inhyyhwn6809228.shtml
- 反代封号与逆向风险 https://www.80aj.com/2026/06/27/chatgpt-proxy-multi-ip-login/ · https://tsight.io/articles/17734335 · https://2libra.com/post/ai-gateway/SnrJgK1
