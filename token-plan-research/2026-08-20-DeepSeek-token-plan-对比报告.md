# DeepSeek Token Plan 市场对比报告（2026-08-20）

> 目标：为 DSH 主链路（必须能调用 **DeepSeek-V4-Flash** 与 **DeepSeek-V4-Pro**，加分项：千问 **Qwen3.8-Max**）寻找市面 token plan，要求**月度成本比 DeepSeek 官方现价便宜 ≥50%（达标）**，≥30%（纳入考虑）。套餐价 ≤3000 元档直接对比其顶配。

---

## 一、为什么现在必须找 plan：官方刚大幅涨价

DeepSeek 于 **2026-08-17 正式调价**，引入**峰谷分时定价**，并同步上架 V4 正式版（Flash-0731 / Pro-0813）：
- 高峰时段：北京时间 **09:00–12:00、14:00–18:00**，价格按 2 倍执行；其余 17 小时半价。
- 据 VentureBeat 转引，V4-Flash 各类 token 涨幅约 **57%–371%**，**缓存命中输入最高涨 1100%**（峰值 11 倍）。
- 官方 API 文档实测价格（2026-08-20 抓取 [api-docs.deepseek.com](https://api-docs.deepseek.com/zh-cn/quick_start/pricing)）：

| 计费项（元/百万 tokens） | V4-Flash 空闲/高峰 | V4-Pro 空闲/高峰 |
|---|---|---|
| 输入·缓存命中 | 0.05 / 0.10 | 0.15 / 0.30 |
| 输入·缓存未命中 | 1.50 / 3.00 | 4.50 / 9.00 |
| 输出 | 4.50 / 9.00 | 13.50 / 27.00 |

参考来源：[zhiding.cn 涨价报道](https://www.zhiding.cn/ai-applications/2026/0818/3196693.shtml)、[36氪：涨价是DeepSeek的原罪？](https://www.36kr.com/p/3944918432267655)、[证券时报：输入缓存降至首发价十分之一（涨价前）](https://stcn.com/article/detail/3821826.html)

你现在 DSH 的现状（已核实本机配置）：
- **`aliyun-tokenplan`**（`llm-pi-ai` provider，本地代理 8789/8787 → `https://token-plan.cn-beijing.maas.aliyuncs.com/compatible-mode/v1`）＝ 阿里云百炼 Token Plan 端点，主模型 `deepseek-v4-flash-0731`；
- **`llm-deepseek`**（本地代理 8787 → DeepSeek 官方 API）＝ 官方按量直连。

---

## 附：省幅 × TPS 极简速查表（2026-08-20）

> 省幅口径：相对 DeepSeek 官方 8/17 涨价后价格，Flash 为主（9:1 混合、8:2 输入/输出、50% 缓存命中），谷/峰平均；TPS 为服务端输出速度（你本地并发与网络也会影响实测值）。

| 方案 | 省多少 | TPS（输出） | 一句话定位 |
|---|---|---|---|
| 官方 · 谷时调度（什么都不换） | **50%** | ~50+（官方文档口径"稳定 50 TPS 以上"） | 零迁移白捡的折扣 |
| 硅基流动 · V4-Flash-0731 | **42–71%（中位 ~60%）** | **60–136**（Artificial Analysis 136 tok/s，其平台最快部署之一） | Flash 主力，稳+便宜 |
| 阿里百炼按量 | 0%（与官方同价）；叠**新客包季 4.5 折 → 省 55%** | ≈官方（国内节点，排队更少） | Pro/千问主腿 |
| 超算互联网 SCNet Token Plan | **59–80%**（Flash ≈¥0.62/百万） | 官方未公布；论坛实测「比官方略慢」（估 30–45），且白天常 429 | 全场最便宜，但条款踩线+稳定性存疑 |
| 火山方舟 Agent Plan | **70%+**（官方口径 Flash 1.9 折） | 主打快（字节自建推理，低延迟卖点；无公开具体值） | Agent/Harness 官方定位 |
| 七牛企业 S（包年 4 折） | ~60% | 无公开；卖点是"无速率限制"+企业 SLA | 大流量/多模型统一 Key |
| 百度千帆 Token 福利包 | 50%（福利包）/ 80%（夜享 2 折） | 无公开 | 夜间批处理神器 |
| NVIDIA NIM | **100%（免费）** | ≤40 次请求/分钟，首 token 慢，无保证 | 测试/巡检兜底 |
| 自部署（超算/GPU 租卡，可选项） | 取决于利用率 | **H20 单并发 600+ TPS**（[GPUStack 实测](https://ai6s.net/6a73fd6310ee7a33f296eba3.html)） | 用量极大才考虑 |

### 三行指导
1. **要"稳 + 真省一半"**：官方谷时调度 + 硅基流动跑 Flash（Pro 走官方谷时/百炼）。
2. **要"最便宜"**：SCNet Token Plan ¥30/月（接受 429 与"严禁 API 自动化"条款风险，或只做第二通道掺着用）。
3. **要"快 + 省 + 场景合规"**：火山方舟 Agent Plan（它自己就是给 Agent/Harness 设计的）；量大再上七牛包年；NVIDIA NIM 永远兜底。

---

## 二、候选 token plan 全景（全市场扫过后的归类）

先划一条硬线：**你的 DSH 是 Agent 后端，属"程序化 API 调用"**。市场三类产品要分清（[SegmentFault 六家横评](https://segmentfault.com/a/1190000048086629)）：

| 类型 | 代表 | 计费单位 | 允许程序化 API？ |
|---|---|---|---|
| 订阅制 Coding Plan | 智谱、阿里 Coding、火山 Coding、MiniMax | 请求次数（5h/周/月） | ❌ 多数明令禁止，违规封号/停订 |
| 按量付费 | DeepSeek 官方、百炼按量、硅基流动、OpenRouter | token | ✅ 无限制 |
| 企业/预付费 Token Plan | 七牛企业套餐、腾讯 TokenHub、百度千帆、火山 Agent Plan、阿里 Token Plan | 积分/Credits/AFP | ⚠️ 看条款（阿里 Token Plan 明文禁止自动化脚本） |

### 人均单价：混合成本测算
统一口径：Flash:Pro = 9:1、输入:输出 = 8:2、缓存命中率 50%（agent 长上下文典型值）。单位：元/百万 tokens。

| 渠道 | Flash | Pro | vs 官方均（Flash 2.28 / Pro 6.84） | 达标判定 |
|---|---|---|---|---|
| **DeepSeek 官方（基准）** | 谷 1.52 / 峰 3.04 | 谷 4.56 / 峰 9.12 | — | — |
| **硅基流动**（[V4-Flash-0731 上线公告](https://www.siliconflow.com/zh/blog/deepseek-v4-flash-0731-now-live-on-siliconflow)） | **0.88**（输入 1.0 / 输出 2.0 / 缓存 0.2，无峰谷） | 10.0（12/24/1） | Flash 省 **61%**（谷时口径省 42%~71%）；**Pro 反而贵 46%** | ✅ Flash 达标；Pro 不适用 |
| **阿里百炼按量**（价格与官方一致，[c114](https://www.c114.net.cn/ainews/78404.html)） | = 官方 | = 官方 | 0%（峰谷同步以官网定价页为准） | ❌ 无折扣时 |
| **百炼新客包月/包季抵扣**（[官方活动](https://developer.aliyun.com/article/1743257)） | — | — | 包季 4.5 折 → **省 55%** | ✅ 达标（仅新客一次） |
| **百炼 AI 节省计划**（[同上](https://developer.aliyun.com/article/1743257)） | — | — | A 类（DeepSeek）24 个月最低 **5.3 折 → 省 47%** | 🟡 接近达标 |
| **火山方舟 Agent Plan**（[官方文章](https://cloud.tencent.cn/developer/article/2673192)） | ¥40/200/500/1000 月，AFP 计量 | 官方口径 V4 Flash **低至 1.9 折**；Pro 官方 2.5 折后再 7 折；¥200 Medium 覆盖等量后付 ¥709 场景 | **省 70–85%**（官方测算口径） | ✅ 达标（需实测换算率） |
| **七牛云企业 Token Plan**（[官网横评](https://news.qiniu.com/archives/1784715210052)、[七牛平替文](https://news.qiniu.com/archives/1787109274281)） | Enterprise S ¥2,999/月（10.7 亿积分），**包年 4 折 → 月均 ¥1,714**；按量=官方同价 | 套餐内约 **省 60%**（4 折） | ✅ 达标（额度大/周刷新/企业向） |
| **腾讯云 TokenHub**（[原厂直供同步峰谷](https://cloud.tencent.com/announce/detail/2353)） | ¥1,000/月起，积分制 | DeepSeek-V4 **与官方同价并同步峰谷** | 0%（只赢多 Key 分账管理） | ❌ 无价格优势 |
| **百度千帆**（[Token 福利包](https://www.csdn.net/article/2026-05-19/161226655)、[夜享 2 折](https://www.geekpark.net/news/368906)） | 席位制 ¥149/月起 + 积分 | 福利包 **单价低至市场价 50%**；夜享 Tokens **2 折** | 省 **50%**（达标线）/ 夜间省 80% | ✅ 达标线 |
| **国家超算互联网 SCNet Token Plan**（[官方 API 文档](https://5.ac.sugon.com/ac/openapi/doc/2.0/moduleapi/plans/token-plan.html)、[9.9元8000万活动文](https://cloud.tencent.com.cn/developer/article/2712148)） | 基础 **¥30**/月（6 万 Credits）→ 标准 ¥110 → 高级 ¥265；V4-Flash-0731 混合折算 **≈ ¥0.62/百万** | Flash 省 **59%–80%**（谷/峰口径），Pro ≈ ¥4.13/百万省 9%–40% | ✅ 全市场最便宜，但红线+稳定性见下 |
| **NVIDIA NIM**（[build.nvidia.com](https://build.nvidia.com/)） | **免费** | deepseek-v4-pro/flash 等开源模型，up to 40 rpm，无稳定性承诺 | 免费 | 🟢 零成本兜底/试验 |
| **中转站（无数非官方代理商）** | 参差 | 可低至官方 3–5 折 | 不推荐：鉴权/稳定性/数据安全无保障 | ❌ 不建议 |

### 订阅制 Coding/Token Plan 额度表（都含 DeepSeek 之外模型，作为横向参考）
- **火山方舟 Coding Plan**：Lite ¥40（首月 ¥9.4）250M tokens、Pro ¥200（首月 ¥47.4）**1,249M tokens**，覆盖 Doubao/GLM/MiniMax/Kimi/**DeepSeek-V4-Pro/Flash**（[横评数据](https://segmentfault.com/a/1190000048086629)）。
- **阿里百炼 Token Plan 个人版**：Lite ¥39（700 credits/5h、2,500/7d）→ Standard ¥139 → Pro ¥499；企业版坐席 ¥150（25k credits/月）→ ¥550（100k）→ ¥1,398（250k）（[阿里云百科](https://www.aliyunbaike.com/tokenplan/)）。
- **七牛 Enterprise**：S ¥2,999 / M ¥4,999 / B ¥9,999（[七牛](https://news.qiniu.com/archives/1784715210052)）。
- Qwen3.8-Max（8/3 发布，1M 上下文）：百炼按量 **输入 12 / 输出 36 / 缓存 1.5** 元每百万；Token Plan 个人版 39 元/月起（首发加量 10 倍）；**Night Plan 夜间（22:00–08:00）2 折**（[首发文](https://developer.aliyun.com/article/1756622)、[ofox 报价](https://ofox.ai/zh/models/bailian/qwen3.8-max)）。

### 国家超算互联网（SCNet）── 全市场最便宜的漏网之鱼
（用户补充发现的"国家超算平台"，补充核实：**就是 超算互联网 www.scnet.cn**，曙光系承建运营，API 文档挂在 5.ac.sugon.com）

- **Token Plan 三档**（Credits 统一计量，月度额度）：基础版 原价 ¥50 → 活动 **¥30/月 / 60,000 Credits**；标准版 ¥185 → **¥110 / 240,000**；高级版 ¥440 → **¥265 / 600,000**。曾推出 **9.9 元 8000 万词元** 年中活动（[活动文](https://cloud.tencent.com.cn/developer/article/2712148)）。
- **模型覆盖**：DeepSeek **V4-Flash / V4-Flash-0731 / V4-Pro**（+V3.2）、GLM-5.2/5.1/5、Kimi-K3/K2.7-Code/K2.6/K2.5、MiniMax-M3/M2.7/M2.5、**Qwen3.8-max** 等——一个订阅全搞定，OpenAI + Anthropic 双协议（[官方文档](https://5.ac.sugon.com/ac/openapi/doc/2.0/moduleapi/plans/token-plan.html)）。
- **积分抵扣表（2026-08-11 生效，积分/百万 tokens；我按 8:2 输入/输出、50% 缓存命中折算）**：

| 模型 | 未命中输入 | 命中输入 | 输出 | 折算混合单价（¥/百万，按 ¥30/6万积分） | vs 官方 |
|---|---|---|---|---|---|
| DeepSeek-V4-Flash-0731 | 1543 | 31 | 3086 | **≈ ¥0.62** | 省 59%–80% |
| DeepSeek-V4-Flash | 1200 | 24 | 2400 | ≈ ¥0.48 | 省 67%–84% |
| DeepSeek-V4-Pro | 10286 | 86 | 20571 | ≈ ¥4.13 | 省 9%（谷）–40%（均）–55%（峰） |

  基础版 6 万 Credits 每月可跑约 **4800 万 Flash-0731 tokens** 或约 **730 万 Pro tokens**；高级版 ¥265/60 万积分是 10 倍量。
- ⚠️ **红线（与百炼 Token Plan 同款条款）**：官方文档明文 **「严禁 API 调用——仅限 AI 工具内交互式使用，禁止用于自动化脚本、自定义应用程序后端或非交互式批量调用，违规可能暂停订阅/封禁 API Key」**；额度用完**不自动转按量**直接报错；额度**不结转**、到期未续费 key 即失效；一账号只能持 1 个套餐、1 个 key，不升降档不退订。
- ⚠️ **实测口碑（论坛 8/18 多方反馈）**：白天频繁 429、缓存命中率约 85%（官方约 95%）、部分档位常"售罄待补"、有用户报基础套餐无法调用、疑为自部署（可能存在量化/版本差异），性能与官方 0731 有差距（[超算 Coding Plan 讨论帖](https://locdd.com/t/topic/81947)）。
- 另有 Coding Plan（按请求次数，sk-sp-）与按量计费（sk-）两条线；5 月曾推"千万词元低至 1 元"智能体特惠（[oschina](https://www.oschina.net/news/502013)，限期活动，是否延续以官网为准）。

### 三方对比：SCNet Token Plan × DeepSeek 官方 × 硅基流动（官方文档 2026-08-20 复核）
（[SCNet Token Plan 官方文档](https://www.scnet.cn/ac/openapi/doc/2.0/moduleapi/plans/token-plan.html)、[SCNet Coding Plan 官方文档](https://www.scnet.cn/ac/openapi/doc/2.0/moduleapi/plans/coding-plan.html)）

混合单价口径：8:2 输入/输出、50% 缓存命中、SCNet 按基础版 ¥30/60,000 Credits 折算（1 Credit = ¥0.0005）。

| 模型 | SCNet Token Plan | DeepSeek 官方（谷 / 峰） | 硅基流动 | SCNet vs 官方 | SCNet vs 硅基 |
|---|---|---|---|---|---|
| **V4-Flash-0731** | **¥0.62/百万**（1543/31/3086 积分） | 1.52 / 3.04 | **¥0.88/百万**（¥1 输入/¥2 输出/¥0.2 缓存） | 省 59%（谷）– 73%（均）– 80%（峰） | 便宜 **30%** |
| V4-Flash | ¥0.48/百万（1200/24/2400） | 同上 | — | 省 67%–84% | — |
| **V4-Pro** | **¥4.13/百万**（10286/86/20571） | 4.56 / 9.12 | ¥10.0/百万（12/24/1） | 省 9%（谷）– 40%（均）– 55%（峰） | 便宜 **59%** |

- **结论**：SCNet Token Plan 是全渠道最低价——**Flash 比硅基还便宜 30%，Pro 直接打到官方均价的 6 折、硅基的 4 折**（硅基 Pro 反而比官方贵，SCNet 是 Pro 的唯一低价腿）。¥30 基础版每月可跑约 4,800 万 Flash-0731 tokens 或约 730 万 Pro tokens；而同样的 Flash 量官方约 ¥110、硅基约 ¥42。
- ⚠️ **但三个硬伤必须背在身上**：①官方文档明文「**严禁 API 调用**（仅限 AI 工具内交互式使用，禁自动化脚本/应用后端）」——DSH 属 Agent 后端，条款踩线；②官方文档"可用模型"列表**未列 V4-Pro 与 -0731**（只有 V4-Flash、V3.2），积分表却含二者——**下单前必须在控制台模型列表确认你要的 Pro/0731 是否真的开放**，模型 id 还需逐字符匹配；③论坛口碑：白天 429、缓存命中率约 85%（官方 95%）、疑自部署/量化、档位常售罄。
- 🚫 **Coding Plan（¥20 Lite / ¥100 Pro，按请求次数）只有 MiniMax-M2.5 与 Qwen3-235B-A22B，不含 DeepSeek**——对 DSH 无意义，排除。

### 月度算例（Flash:Pro=9:1，同口径）
| 月用量 | 官方全按量（均） | 硅基 Flash + 官方 Pro 谷时 | 百炼包季 4.5 折 | 火山 Agent Plan |
|---|---|---|---|---|
| 50M 输入 / 10M 输出 | ≈ ¥137 | ≈ ¥46（Flash 走硅基，Pro 走官方谷） | ≈ ¥62 | ¥40–200 档 |
| 200M 输入 / 40M 输出 | ≈ ¥548 | ≈ ¥183 | ≈ ¥247 | ¥200–500 档 |

---

## 三、结论与推荐组合

1. **最优先（*零迁移成本*）**：**谷时调度**——午间 12–14 点、18 点–次日 9 点用官方，直接省 50%。这是官方自己给的折扣。
2. **Flash 主力 → 硅基流动**（OpenAI 兼容、`deepseek-ai/DeepSeek-V4-Flash-0731`）：输出 ¥2 vs 官方 ¥4.5–9，**省 42%–71%**；无峰谷、无订阅限制、真按量。代价：无企业 SLA、高峰可能限速——DSH 个人使用可接受。
3. **Pro 主力 → 阿里百炼**：价格与官方一致但**无官方排队**（国内节点稳），叠加**新客包季 4.5 折**（¥675 买 1500 元季度额度）或**节省计划 5.3 折**；同样覆盖 **Qwen3.8-Max**（加分项，夜间 Night Plan 2 折）。
4. **重度/合规向 → 火山方舟 Agent Plan ¥200**（官方口径省 70%+，Agent 场景就是为 Harness 设计的）或 **七牛 Enterprise S 包年**（4 折、25 模型一 Key）——但需先实测 AFP/积分换算率并核对自动化脚本条款。
5. **零成本兜底**：NVIDIA NIM 免费跑 V4 Pro/Flash（≤40 rpm），可做巡检/测试负载。

> 🥇 **如果只想要"最便宜"**：国家超算互联网 **Token Plan 基础版 ¥30/月**（Flash-0731 折算 ≈¥0.62/百万，全市场最低，低于硅基流动 0.88 和官方 2.28）——但两件事必须先想清楚：①官方条款**严禁 API 自动化调用**（DSH 属 Agent 后端，与百炼 Token Plan 完全相同条款）；②论坛实测白天 429、缓存命中率偏低、疑似量化/自部署版本、档位经常售罄。**适合场景**：合规上打擦边球的个人试用、低峰期跑 Flash 长任务；生产链路不建议单独押注，可做第二通道掺着用（同模型按质量切换）。

> ⚠️ **合规红线（最重要）**：阿里百炼 **Token Plan（包括你现用的 token-plan 端点）官方条款明文「仅限兼容 AI 工具内交互式使用，不可用于自动化脚本或应用后端，违规可能导致订阅暂停或 API Key 封禁」**；智谱/阿里 Coding Plan 同样禁止 API 调用。DSH 属 Agent 后端——若完全按条款执行，**百炼按量（包季抵扣/节省计划）比订阅制 Token Plan 更安全**。硅基流动/官方/七牛企业套餐（明确允许 API）无此约束。市面上大量用户实际在用订阅跑 harness，属于执行弹性，风险自担。

---

## 四、数据来源
- DeepSeek 官方定价（实测抓取）：https://api-docs.deepseek.com/zh-cn/quick_start/pricing
- 涨价报道：[zhiding](https://www.zhiding.cn/ai-applications/2026/0818/3196693.shtml)、[证券时报](https://stcn.com/article/detail/3821826.html)、[36氪](https://www.36kr.com/p/3944918432267655)
- 六家 Coding Plan 横评（2026-07-28）：https://segmentfault.com/a/1190000048086629
- 七家平台性价比选型（2026-08-03）：https://segmentfault.com/a/1190000048112421
- 企业 Token Plan 六家横评（七牛官方）：https://news.qiniu.com/archives/1784715210052
- 七牛《DeepSeek 涨价后怎么选平替》（2026-08-19）：https://news.qiniu.com/archives/1787109274281
- 硅基流动 V4-Flash-0731 公告：https://www.siliconflow.com/zh/blog/deepseek-v4-flash-0731-now-live-on-siliconflow ；更新公告：https://api-docs.siliconflow.cn/docs/release-notes/overview
- 阿里百炼 DeepSeek-V4 计费/节省计划：https://developer.aliyun.com/article/1743257 ；Token Plan 详解：https://www.aliyunbaike.com/tokenplan/
- Qwen3.8-Max 首发：https://developer.aliyun.com/article/1756622 、https://ofox.ai/zh/models/bailian/qwen3.8-max
- 火山方舟 Agent/Coding Plan 上 DeepSeek V4：https://cloud.tencent.cn/developer/article/2673192
- 腾讯 TokenHub 原厂直供/峰谷：https://cloud.tencent.com/announce/detail/2353
- 百度千帆 Token 福利包：https://www.csdn.net/article/2026-05-19/161226655
- Coding Plan 实际价值对比（含 NVIDIA NIM 免费项）：https://github.com/mahonzhan/awesome-coding-plan
- **国家超算互联网 SCNet Token Plan 官方 API 文档（含积分抵扣表）**：https://5.ac.sugon.com/ac/openapi/doc/2.0/moduleapi/plans/token-plan.html
- SCNet Token Plan 9.9 元 8000 万词元活动介绍：https://cloud.tencent.com.cn/developer/article/2712148
- SCNet 上线 DeepSeek-V4 / V4-Flash 正式版：https://www.chinastarmarket.cn/detail/2356041 、https://app.dahecube.com/nweb/pc/spiderdetail.html?spidid=833102
- SCNet 实测口碑（429/缓存命中率/售罄）：https://locdd.com/t/topic/81947 ；千万词元低至 1 元特惠：https://www.oschina.net/news/502013

> 注：价格为 2026-08-20 前后各官方/原文口径，市场调整极频繁（尤其抢购制套餐），下单前以官网实时价为准。