# 中国国内大模型厂商免费 API 额度清单

**情报日期：2026-09-20**｜方法：web_search 多轮中文检索｜口径：只收"免费"，不含付费价目

**图例**：🟢 官方页面直接命中｜🟡 二手（博客/聚合站/社区/SEO 文）｜⚪ 未核实或存疑
**核心区分**：`永久免费` ≠ `新用户一次性赠送`，两者已分列。

> 警告：以下 2026 年数字多数来自搜索摘要，**未逐条登录控制台核账**。投产前请以自己账号的控制台余额为准。

---

## 1. 阿里云百炼 Model Studio 🟢
- URL：https://www.aliyun.com/product/bailian ｜额度规则：https://help.aliyun.com/zh/model-studio/new-free-quota
- 形式：**新用户一次性**（首次开通自动发放，无需领取）
- 额度：每模型约 **100 万 token**，70+ 模型 ⇒ 宣传"超 7000 万 / 1 亿+"；**有效期 90 天**；**仅华北2（北京）**；仅实时推理，不含批量
- base_url：`https://dashscope.aliyuncs.com/compatible-mode/v1`（OpenAI 兼容）
- 门槛：**无需实名认证**即可拿免费额度；转按量付费才需实名
- 坑：额度按模型独立、不互通（含快照版）；Coding Plan 专属 Key **不**消耗免费额度；未实名强制"用完即停"（403 `AllocationQuota.FreeTierOnly`）
- 附加：OAuth 认证有独立免费额度 **每天 2000 次调用**（官方同页）

## 2. 魔搭 ModelScope 🟡
- URL：https://modelscope.cn ｜公告：https://developer.aliyun.com/article/1644361
- 形式：**永久免费（每日刷新）**——注册即送 **每日 2000 次**推理调用，0 点重置
- 模型：deepseek-ai/DeepSeek-R1、Qwen3-235B-A22B、Qwen3-Coder-480B、GLM-4.5、MiniMax-M1 等；**2000 次为平台总量**，单模型更低（🟡 称 R1 约 200 次/日）
- base_url：`https://api-inference.modelscope.cn/v1/`（OpenAI 兼容，官方示例）
- 门槛：ModelScope SDK Token；🟡 称需绑阿里云+实名
- 可信度：🟡 2024-12 官方公告 + 2026-04 二手实测；**2026-09 是否仍 2000 次未核实**

## 3. 智谱 BigModel / GLM 🟢
- URL：https://bigmodel.cn/ ｜免费模型文档：https://docs.bigmodel.cn/cn/guide/models/free/glm-4.7-flash
- 形式：**永久免费模型**（不依赖活动）——`glm-4.7-flash`（官方文档归入 free 目录，203K 上下文）、`glm-4-flash`
- 已变：`glm-4.5-flash` 于 **2026-01-30 下线**，请求自动路由至 GLM-4.7-Flash（官方文档原文）
- base_url：`https://open.bigmodel.cn/api/paas/v4`（OpenAI 兼容）
- 门槛：注册 + 实名；**无需绑卡**
- 坑：新用户赠 token 数字官方未承诺固定值（🟡 流传 2000 万/邀请各 2000 万），**别当规划依据**；GLM-5.3-Flash 的"夜间免费"仅对 **Coding Plan 付费套餐**用户（9/3–9/20，23:00–09:00），不是免费 API

## 4. 硅基流动 SiliconFlow 🟢限流文档/🟡清单
- URL：https://cloud.siliconflow.cn ｜价格：https://siliconflow.cn/pricing ｜限流：https://docs.siliconflow.com/cn/faqs/billing-rules
- 形式：**永久免费模型**（费用为 0，账单显示 0），限额固定，**不随 L0–L5 消费等级提升**
- 2026-08-21 快照免费 ID（🟡）：`THUDM/GLM-Z1-9B-0414`、`THUDM/GLM-4-9B-0414`、`tencent/Hunyuan-MT-7B`、`PaddlePaddle/PaddleOCR-VL-1.5`、`BAAI/bge-m3`、`BAAI/bge-reranker-v2-m3`、`BAAI/bge-large-zh-v1.5`、`BAAI/bge-large-en-v1.5`、`Kwai-Kolors/Kolors`、`Qwen/Qwen3-ASR-1.7B`、`TeleAI/TeleSpeechASR`、`FunAudioLLM/SenseVoiceSmall`
- base_url：`https://api.siliconflow.cn/v1`（OpenAI 兼容）
- 门槛：官方限流文档写明**使用全部免费模型需实名认证**（🟡 转载官方）；无需信用卡
- 坑：同一模型常有 `Pro/` 前缀付费版，用错 ID 会以为"免费层没了"；限额按账户+按模型，官方未公开静态 RPM 数字

## 5. 火山方舟（字节豆包）🟢页存在 / 🟡数值
- URL：https://www.volcengine.com/product/ark ｜免费额度文档：https://www.volcengine.com/docs/82379/1399514（页存在、最近更新 2026-08-24，正文未能抓取）
- 形式：**新用户一次性**——🟡 称实名后**每模型各 50 万 tokens**，模型间独立不互通；另有 15 元邀请代金券；老用户邀请最高 145 元
- ⚠ 另有 https://www.volcengine.com/article/2607749 称 Doubao-Seed-2.1-pro 送"30 小时 Agent 运行时 + 500 次 web_search、有效期 2 年"——该文含 2026-Q4 预测段，**疑似 AI 生成 SEO 稿，不要采信**
- base_url：`https://ark.cn-beijing.volces.com/api/v3`（OpenAI 兼容）｜Anthropic 兼容 `.../api/compatible` 🟢官方文档
- 门槛：🟡 实名认证；🟡 称无消费门槛
- **结论：官方免费额度页确实存在，但具体数值我未从官方正文核实 → 标未核实**

## 6. 百度千帆（文心）🟢
- URL：https://cloud.baidu.com/doc/qianfan/s/Imi2rpirg（新用户免费额度，官方）
- 形式 A｜**新用户一次性**：17 个模型**各 100 万 tokens**，**有效期 3 个月**（ERNIE-4.5-Turbo-128K/32K/VL、ERNIE-X1-Turbo-32K、DeepSeek-R1、DeepSeek-V3.1、Kimi-K2-Instruct、Qwen3-235B/30B/Coder、bge 等），2025-10-24 起自动发放
- 形式 B｜**永久免费**：`ERNIE-Speed-8K/128K`、`ERNIE-Lite-8K/128K`、`ERNIE-Tiny` 系列**长期免费**（官方公告：cloud.baidu.com/news/news_c7a145b9-5c99-4870-939f-e09ba506aab3），需实名认证
- base_url：`https://qianfan.baidubce.com/v2`（🟡 二手，官方页未直接确认）
- 坑：免费额度**仅抵扣在线推理**，不抵扣批量推理；RPM/TPM 免费配额以控制台为准

## 7. 讯飞星火 🟢
- URL：https://xinghuo.xfyun.cn/sparkapi ｜HTTP 文档：https://www.xfyun.cn/doc/spark/HTTP调用文档.html
- 形式：**永久免费**——官方文档明写 **Spark Lite** "具有更高的响应速度，**支持免费使用**"；官网另有"**0 元无限量畅享开源模型 API**"（星辰 MaaS 开源模型）
- base_url：`https://spark-api-open.xf-yun.com/v1`（官方文档，OpenAI 兼容）；api_key 用控制台的 **APIPassword**
- 门槛：注册 + 控制台建应用；新用户产品页可领免费额度
- ⚠ 具体 QPS/日限官方正文未给；🟡 称 Lite QPS 2。**Max 套餐 2026-03-10 下线并入 Ultra**

## 8. 腾讯混元 🟢
- URL：https://cloud.tencent.com/document/product/1729/97731 ｜兼容接口：https://cloud.tencent.com/document/product/1729/111007
- 形式 A｜**永久免费**：`hunyuan-lite`（2024-05-23 官方公告"价格调整为全面免费"）——**2026 现状未核实**；🟡 称并发≈5、总量不限
- 形式 B｜**新用户一次性**：100 万 tokens 共享资源包，**有效期 1 年**（覆盖 Hunyuan-a13b/role/translation/vision 系列；embedding 另 100 万）
- base_url：`https://api.hunyuan.cloud.tencent.com/v1`（官方文档，OpenAI 兼容）
- 门槛：需腾讯云**实名认证**（个人或企业）
- 坑：免费包到期**不自动转后付费**，未开通后付费会报错；欠费/停服期间不享受免费额度

## 9. 华为云 ModelArts Studio（昇腾）🟢指南
- URL：https://www.huaweicloud.com/product/modelarts/studio.html ｜对接指南：https://www.huaweicloud.com/guide/productsdesc-bms_71fc23ebc3cd760d78d83023788c2e24support1_a
- 形式：**新用户一次性**——官方指南：**免费服务中单个模型提供 200 万 token** 推理额度（另有 2024 年华为云博客写"每模型 100 万"，**前后不一致**）
- 区域：**仅华东二**支持免费服务（官方）；需在"在线推理→预置服务→免费服务"**手动领取**
- base_url：领取后在"调用说明"中选 OpenAI SDK 获取，**非统一公开 URL → 未核实**
- 注意：`openPangu-2.0-Flash` 是**付费**（输入 0.8 元/百万 tokens），别当成免费

## 10. MiniMax 🟡
- URL：https://platform.minimaxi.com/docs/guides/text-generation ｜国内站 https://platform.minimax.cn
- 形式：**官方平台未见免费层**；免费主要走三条外部渠道（均🟡或半官方）：
  - 阿里云百炼：`abab6.5g/t/s-chat` 仅免费体验，**各 100 万 token，需申请，90 天** 🟢（help.aliyun.com/zh/model-studio/minimax-llm-api）
  - NVIDIA build：MiniMax M2.1，免 token，40 RPM 🟡
  - 第三方 DMXAPI 的 `MiniMax-M2.7-free`（无 token 计费）🟡，**安全性存疑**
- base_url：`https://api.minimaxi.com/v1`（OpenAI 兼容）｜Anthropic 兼容 `/anthropic` 🟢
- 门槛：手机号注册；**无永久免费模型**

## 11. 月之暗面 Kimi 🟢
- URL：https://www.kimi.com/zh-cn/help/kimi-api/api-free-trial（官方帮助中心）
- 形式：**新用户一次性**——国内手机号注册 + **实名认证**后赠 **15 元代金券**，**3 个月**有效，自动优先扣减
- 坑：代金券**不能用于 Kimi K3**；余额为 0 时 API 返回 403。**无永久免费模型**
- base_url：`https://api.moonshot.cn/v1`（🟡 二手，官方页本轮未直接确认）

## 12. 阶跃星辰 StepFun 🟢部分/🟡
- URL：https://platform.stepfun.com/
- 形式 A｜**限时/合作免费**：Step 3.5 Flash 在 **OpenRouter** 有 free tier（模型 ID `stepfun/step-3.5-flash:free`）🟢（官方 GitHub/HF）
- 形式 B｜🟡 新用户 **¥10** 体验额度、**5 RPM**；🟡 另一说 Step-2 新用户 100 万 token —— **两说冲突，未核实**
- base_url：`https://api.stepfun.com/v1`（中国站，官方 GitHub 示例）
- 门槛：手机号注册；官方平台自身未见"永久免费模型"页

## 13. 潞晨 Colossal / 潞晨云 🟢
- URL：https://cloud.luchentech.com/model-apis
- 形式：**新用户一次性**——官方 FAQ："新注册账户将自动获得免费赠金（如 **¥20.00**）"
- 兼容：官网称同时兼容 **OpenAI 与 Anthropic** 标准接口
- base_url：本轮未搜到官方明确 URL → **未核实**

## 14. PPIO 派欧云 🟢
- URL：https://ppio.com/docs/support/faq ｜模型广场：https://ppio.com/docs/model/serverless
- 形式 A｜**永久免费模型**——官方："提供多个高性能模型的**永久免费版本**（如 Qwen 2.5（7B）等）"，模型列表可筛"免费"标签
- 形式 B｜**新用户一次性**：注册后自动获得新用户代金券
- base_url：`https://api.ppio.com/openai`（官方文档，OpenAI 兼容）
- ⚠ **冲突**：Qwen2.5-7B 详情页显示输入/输出 **¥0.35/Mt**（计价），与"永久免费"宣传矛盾 → 可能已改价，**以控制台为准**
- 门槛：手机号注册

## 15. 无问芯穹 Infini（GenStudio）🟢 · 重要变更
- URL：https://docs.infini-ai.com/gen-studio/api/usage-and-billing/rate-limit.html
- **形式：已基本取消免费**——官方 FAQ 明写：**自 2026-03-30 起停止提供基础版 LLM API 免费服务**，API 调用按 Token 计费；体验中心（网页端）仍不计费；**向量嵌入与重排序 API 仍暂不收费**
- 限额（基础服务）：**RPM 12 / RPD 300 / TPM 12000**；高级版 1200 RPM / RPD 不限
- base_url：`https://cloud.infini-ai.com/maas/v1`（OpenAI 兼容；Anthropic → `https://cloud.infini-ai.com/maas`）
- 注意：文档仍有"海量 Token 免费调用"旧文案，**已过时**

## 16. 天翼云 息壤 🟡（文档标注"停止维护"）
- URL：https://www.ctyun.cn/document/10541165/10963340
- 形式：**新用户/活动一次性**——DeepSeek 系列**每模型 2500 万 tokens**（首次使用起**两周**）；Qwen 及其他系列**每模型 100 万**（两周）；耗尽后调用失败
- 活动：2026-03 新春活动文本类模型 2500 万 tokens 免费领，限两周（官方新闻 ctyun.cn/newsboard/1000245559）
- base_url：`https://wishub-x6.ctyun.cn`（官方部署文档示例；星辰 TokenHub 为 `https://ai.ctaigw.cn/v1`）；默认支持 `openai-completions`
- 门槛：天翼云账号 + 创建服务组拿 APP KEY

## 17. 移动云 / 中国移动九天 ⚪
- URL：https://jiutian.10086.cn/portal/ ｜Key 申请：https://jiutian.10086.cn/largemodel/llmstudio/#/callSettings/order
- 形式：**需人工审核**，通过后给免费额度
- 实测反馈（心流社区 2026-04，🟡）：**审核极慢甚至无回执**，用户量约 4k
- base_url / 限额：**未找到官方页，存疑**

## 18. 商汤日日新 SenseNova 🟢
- URL：https://platform.sensenova.cn ｜Token Plan：https://www.sensenova.cn/token-plan ｜新闻：https://www.sensetime.com/cn/news/sensenova-u1-5-lite-token-plan-20260911-1741
- 形式 A｜**公测期免费**：`sensenova-u1.5-lite`，**每 5 小时 1500 次请求**，公测完全免费，`watermark=false` 出无水印原图 🟢
- 形式 B｜Token Plan **Free·公测**：¥0/月，**60,000 积分 / 5 小时** 🟢
- 🟡 另有说法已改"双积分池"：通用池 60,000/5h + 600,000/周，Flash-Lite 专属池同额（jishuzhan 2026-08-30）
- base_url：`https://token.sensenova.cn/v1`（官方新闻；注意**不是** platform.sensenova.cn），OpenAI 兼容
- 门槛：控制台取 API Key

## 19. 零一万物 Yi 🟡
- URL：https://platform.lingyiwanwu.com/docs
- 形式：**未见官方免费层**；🟡 注册送 **¥10**、5 RPM（yangmao.ai 2026-06-24）
- base_url：`https://api.lingyiwanwu.com/v1`（🟡 常见值，本轮未命中官方页 → 存疑）

## 20. 百川智能 🟡（页面过时）
- URL：https://platform.baichuan-ai.com/prices
- 官方价格页只有 **2024-05-22** 的赠送金政策：新用户 **80 元**（≈Baichuan2-Turbo 1000 万 tokens，3 个月有效）
- **2026 年现状未核实**；无永久免费模型；Assistants API 标"限时免费"
- base_url：`https://api.baichuan-ai.com/v1`（🟡，未核实）

## 21. 面壁智能 MiniCPM 🟢
- URL：https://platform.modelbest.cn ｜API 文档：https://github.com/OpenBMB/MiniCPM-V/blob/main/docs/api.md
- 形式：**永久免费 Key**——官方发布日志（2026-05-17）：MiniCPM-V 4.6 **提供公开免费 API Key**；MiniCPM-o 4.5 免费开放全双工 WebSocket API
- 模型：`MiniCPM-V-4.5-9B`、`MiniCPM-V-4.6-1B`、`MiniCPM-V-4.6-Thinking`、`MiniCPM-O-4.5-9B`
- base_url：`https://api.modelbest.cn/v1`（官方 GitHub，OpenAI 兼容），Key 在 platform.modelbest.cn 创建
- 限额：**官方未公布具体 RPM/日限 → 未核实**

## 22. 腾讯元宝 ⚪
- URL：https://yuanbao.tencent.com
- **无公开 API**：元宝是 C 端助手，第三方聚合站（🟡 yangmao.ai）明确写"未记录明确免费 API，需 API 请走腾讯云混元"
- 网页/App 免费使用；开发者请直接看 #8 腾讯混元

## 23. 京东言犀 / JoyAgent ⚪
- URL：https://joyagent.jd.com/ ｜文档：https://docs.jdcloud.com/cn/agents/model
- 支持 OpenAI 与 Anthropic 协议，但页面展示的是 **¥5 / ¥29 / ¥49 积分套餐（付费）**，**未见免费额度**
- **未找到官方免费页，存疑**

## 24. 网易有道 子曰 🟢（数字不一致）
- URL：https://ai.youdao.com/new/price-center.s ｜翻译文档：https://ai.youdao.com/DOCSIRMA/html/trans/api/wbfy/index.html
- 形式：**新用户一次性体验金**——价格中心页：注册 **10 元** + 实名认证 **40 元** + 加客服微信 **50 元**（合计 100 元）
- ⚠ 另一官方文档页却写"平台向每个账户赠送 **50 元**体验金" → **两处不一致，以控制台为准**
- 模型：子曰 pro（14B）/ lite（1.5B），按 token 计费，**无永久免费**
- base_url：`https://openapi.youdao.com/api`，**sha256 签名式，不兼容 OpenAI**

## 25. NVIDIA build.nvidia.com（中国可访问）🟡
- URL：https://build.nvidia.com/
- 形式：**永久免费推理**，100+ 模型；**无需信用卡**
- base_url：`https://integrate.api.nvidia.com/v1`（OpenAI 兼容）
- 限额：🟡 称 **40 RPM**，且已**取消**旧的 1000/5000 次总额限制 → **额度说法未从官方核实**
- 坑：🟡 称免费 API 可能收集使用数据，勿发敏感信息；"中国大陆直连"为二手说法，建议自测

## 26. Gitee AI 模力方舟 🟢
- URL：https://ai.gitee.com/docs/getting-started
- 形式：**永久免费（每日刷新）**——官方文档：每个账号**每天可免费调用各种模型共 100 次**
- 实现：系统默认创建"免费体验访问令牌"，**无需购买资源**即可调用，不会扣费；官方明确"体验次数有限，勿用于生产"
- base_url：`https://ai.gitee.com/v1`（官方文档，OpenAI 兼容）
- 门槛：Gitee 账号登录

## 27. DeepSeek 官方（补充）🟡
- URL：https://platform.deepseek.com ｜定价：https://api-docs.deepseek.com/zh-cn/quick_start/pricing
- 形式：**仅"赠送余额"**（注册后自动到账，**官方未公开承诺金额与期限**），随调用优先扣减；**无永久免费 API 模型**
- 坑：网上"额度中心一键领取每月 100 万 token"的教程**官方文档查无此流程**；网页/App 免费与 API 赠送余额是两套体系
- base_url：`https://api.deepseek.com`（Anthropic 格式 `https://api.deepseek.com/anthropic`）
- 动态：🟡 2026-09-14 12:00 起 `deepseek-v4-pro` 请求路由至 V4.1-Flash 并按 Flash 价计费

## 28. AISA 聚合站 🟢（非免费平台）
- URL：https://aisa.one/zh-cn ｜FAQ：https://aisa.one/docs/zh/guides/faq
- 形式：**按次计费**，官方 FAQ 提到注册后可用"**免费测试额度**"完成第一次统一 API 调用
- 定位：5000+ API / 90 个对话模型，按调用付费（中位 $0.012/次），**不是白嫖源**

## 29. 公益聚合站 / 中转站导航 ⚪
- https://github.com/weed33834/ai-api-gongyi-nav（更新 2026-07-16）：收录 30+ 公益/中转站，注册赠送 6–80 刀不等，含 DeepSeek v4 / Kimi 2.6 / MiniMax 2.7 等国模分组
- https://github.com/dawn0731/cn-freellm：把智谱/硅基流动/魔搭/千帆/讯飞/百炼/方舟/Kimi/DeepSeek/混元/Gitee AI 聚合成一个 OpenAI 端点（`http://127.0.0.1:3210/v1`），自带 429 冷却与故障转移；其 `src/catalog.ts` 有 **2026-08 核实的平台目录**（本清单大量交叉验证来自此文件）
- ⚠ **风险**：第三方站点稳定性、合规性、数据安全均无保障；**不要上传隐私数据、密钥或敏感文件**

---

## 总表

| 平台 | 免费类型 | 免费模型 / 额度 | base_url | 门槛 | 可信度 |
|---|---|---|---|---|---|
| 阿里云百炼 | 新用户一次性 | 每模型 100 万 token，70+ 模型，90 天，仅华北2 | `dashscope.aliyuncs.com/compatible-mode/v1` | 免实名可用免费额度 | 🟢 |
| 魔搭 ModelScope | **永久**（日刷） | 2000 次/日（平台总量） | `api-inference.modelscope.cn/v1` | SDK Token（+阿里云/实名？） | 🟡 |
| 智谱 GLM | **永久** | `glm-4.7-flash`、`glm-4-flash` | `open.bigmodel.cn/api/paas/v4` | 实名，免绑卡 | 🟢 |
| 硅基流动 | **永久**（固定限额） | GLM-9B 系、bge 系、ASR、Kolors 等 | `api.siliconflow.cn/v1` | 实名认证 | 🟢/🟡 |
| 火山方舟 | 新用户一次性 | 每模型 50 万 token（🟡） | `ark.cn-beijing.volces.com/api/v3` | 实名（🟡） | 🟡 |
| 百度千帆 | **永久** + 一次性 | Speed/Lite/Tiny 长期免费；17 模型各 100 万/3 月 | `qianfan.baidubce.com/v2`（🟡） | 实名认证 | 🟢 |
| 讯飞星火 | **永久** | Spark Lite 免费；开源模型 0 元 | `spark-api-open.xf-yun.com/v1` | 注册+控制台建应用 | 🟢 |
| 腾讯混元 | **永久**（疑）+ 一次性 | `hunyuan-lite` 免费（2024 公告）；100 万包/1 年 | `api.hunyuan.cloud.tencent.com/v1` | 实名认证 | 🟢/⚪ |
| 华为云 MaaS | 新用户一次性 | 每模型 200 万（指南）或 100 万（博客），仅华东二 | 领后在调用说明取 | 华为云账号 | 🟢 |
| MiniMax | 无官方免费层 | 走百炼体验（100 万/模型/90 天） | `api.minimaxi.com/v1` | 手机号 | 🟢/🟡 |
| Kimi | 新用户一次性 | 15 元代金券，3 个月，限 K3 除外 | `api.moonshot.cn/v1`（🟡） | 国内手机号+实名 | 🟢 |
| 阶跃星辰 | 限时（OpenRouter 免费档） | `step-3.5-flash:free`；🟡 新用户 ¥10 | `api.stepfun.com/v1` | 手机号 | 🟢/🟡 |
| 潞晨云 | 新用户一次性 | 赠金约 ¥20 | 未核实 | 注册 | 🟢 |
| PPIO 派欧云 | **永久**（宣传）+ 代金券 | 如 Qwen2.5-7B（**页面已标价，冲突**） | `api.ppio.com/openai` | 注册 | 🟢/⚠ |
| 无问芯穹 GenStudio | **已取消**（2026-03-30 起） | LLM API 停止免费；仅嵌入/重排暂不收费 | `cloud.infini-ai.com/maas/v1` | 注册 | 🟢 |
| 天翼云息壤 | 新用户/活动一次性 | DeepSeek 2500 万/模型（两周）；其他 100 万 | `wishub-x6.ctyun.cn` | 天翼云账号 | 🟡 |
| 移动九天 | 审核后发放 | 未公开 | 未核实 | 人工审核（极慢） | ⚪ |
| 商汤日日新 | 公测免费 | `sensenova-u1.5-lite` 1500 次/5 小时；Free 档 6 万积分/5h | `token.sensenova.cn/v1` | 控制台取 Key | 🟢 |
| 零一万物 | 无官方免费层 | 🟡 注册送 ¥10，5 RPM | `api.lingyiwanwu.com/v1`（🟡） | 注册 | 🟡 |
| 百川智能 | 一次性（2024 政策） | 80 元 ≈1000 万 token/3 月（**页面过时**） | `api.baichuan-ai.com/v1`（🟡） | 注册 | 🟡 |
| 面壁 MiniCPM | **永久免费 Key** | MiniCPM-V 4.6 / o 4.5 系 | `api.modelbest.cn/v1` | 平台注册 | 🟢 |
| 腾讯元宝 | 无 API | 仅网页/App 免费 | — | — | ⚪ |
| 京东言犀/JoyAgent | 未见免费 | 积分套餐 ¥5 起 | joyagent 站内 | 注册 | ⚪ |
| 网易有道 | 新用户一次性 | 10+40+50 元（另一页写 50 元，冲突） | `openapi.youdao.com/api`（非 OpenAI 兼容） | 实名 | 🟢 |
| NVIDIA build | **永久** | 100+ 模型，40 RPM（🟡），免信用卡 | `integrate.api.nvidia.com/v1` | 邮箱注册 | 🟡 |
| Gitee AI 模力方舟 | **永久**（日刷） | 100 次/日 | `ai.gitee.com/v1` | Gitee 账号 | 🟢 |
| DeepSeek 官方 | 新用户一次性 | 赠送余额（金额未公开承诺） | `api.deepseek.com` | 实名（FAQ 提及） | 🟡 |
| AISA | 免费测试额度 | 按次计费为主 | aisa.one | 注册 | 🟢 |
| 公益中转站 | 注册赠送 | 6–80 刀不等 | 各家 | 各异 | ⚪ |

---

## 结论速记

- **真正的"永久免费"（可长期依赖）**：智谱 GLM-4.7-Flash、百度 ERNIE-Speed/Lite/Tiny、讯飞 Spark Lite、腾讯 hunyuan-lite（待核）、硅基流动 9B 以下免费模型、魔搭 2000 次/日、Gitee AI 100 次/日、面壁 MiniCPM-V 4.6、PPIO（有冲突）
- **只是"新用户一次性赠送"**：阿里云百炼（90 天）、火山方舟（一次性）、腾讯混元资源包（1 年）、Kimi 15 元（3 月）、华为云 MaaS、天翼云息壤、幻方/百川/有道体验金
- **已失效/需警惕**：无问芯穹 GenStudio（2026-03-30 停止基础版免费）、智谱 GLM-4.5-Flash（2026-01-30 下线）、讯飞 Max（2026-03-10 下线）、火山方舟 SEO 稿的"30 小时 Agent 运行时"
- **数据用于训练/可否商用**：本轮**未系统核实**。已知 ① 智谱/百度/阿里均有标准用户协议，商业使用需遵守各自条款；② NVIDIA 免费档🟡被指可能收集使用数据。**这一列建议单独再查一轮官方协议**。

*所有 URL 均为本轮 web_search 实际命中；未命中官方页的一律标注"未核实/存疑"，未做任何数字补全。*
