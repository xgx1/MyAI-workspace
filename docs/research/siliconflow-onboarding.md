# 硅基流动 SiliconFlow 接入 DSH 操作手册（2026-09-20）

> 目标：把硅基流动的**免费 chat 模型**（11 个，¥0）接进本机 DSH。
> 前置事实（2026-09-20 从官方 pricing 页内嵌 flight data 实取）：
> - 免费 chat 模型 11 个，prompt/completion 双 ¥0，`onlyByChargeBalance=false`（**无需充值**即可调用）
> - 免费模型限流：**L0 = 1000 RPM / TPM 40K–80K**，且不随用户等级提升
> - 官方明确：使用免费模型**必须实名认证**
> - 本机曾用 `headroom-siliconflow`（:8788）代理，2026-09-13 已删除；现 :8788 为商汤。本次**直连** `https://api.siliconflow.cn/v1`，不再走代理

## 1. 你需要做的事（约 5 分钟）

1. 打开 <https://cloud.siliconflow.cn> 注册（手机号/邮箱）
2. **实名认证**（免费模型强制；个人实名即可，几分钟出结果）
3. 控制台 → API 密钥 → 创建新密钥，复制 `sk-...`
4. 把密钥填进 `~/.dsh/.credentials.yaml` 的 `refs:` 下（没有该文件就 `cp ~/.dsh/keys.example.yaml ~/.dsh/.credentials.yaml && chmod 600 ~/.dsh/.credentials.yaml`）：

```yaml
refs:
  SILICONFLOW_API_KEY: sk-你的密钥
```

## 2. settings.yaml 配置

在 `~/.dsh/settings.yaml` 的 `llm-pi-ai.providers` 里追加 `siliconflow`（参照现有 sensenova/md 的 YAML 风格）：

```yaml
llm-pi-ai:
  providers:
    {
      # ……已有 md / local-bonsai / sensenova 保持不动……
      siliconflow:
        {
          displayName: "SiliconFlow free (Qwen2.5-72B)",
          apiKeyEnv: SILICONFLOW_API_KEY,
          api: openai-completions,
          baseURL: "https://api.siliconflow.cn/v1",
          models:
            [
              {
                  id: Qwen/Qwen2.5-72B-Instruct,
                  name: "Qwen2.5-72B-Instruct (free)",
                  contextWindow: 32768,
                  maxTokens: 8192,
                  input: [ text ]
                },
              {
                  id: THUDM/GLM-Z1-9B-0414,
                  name: "GLM-Z1-9B-0414 (free, 131K)",
                  contextWindow: 131072,
                  maxTokens: 16384,
                  input: [ text ]
                },
              {
                  id: Qwen/Qwen3.5-4B,
                  name: "Qwen3.5-4B (free, 262K)",
                  contextWindow: 262144,
                  maxTokens: 8192,
                  input: [ text ]
                }
            ]
        }
    }
```

要点：
- **YAML 里 model id 带斜杠**（`Qwen/Qwen2.5-72B-Instruct`）——上面沿用了本机 settings.yaml 的宽松 YAML 风格（不带引号），如果 `dsh` 校验报错，给 id 加引号：`id: "Qwen/Qwen2.5-72B-Instruct"`
- 免费模型是纯对话（无 reasoning 声明），不要加 `reasoning:` 字段，避免 DSH 发 `reasoning_effort` 参数被 4xx
- 不用 `headers`，key 走 `apiKeyEnv`（DSH 经 `ctx.credentials` 解析 credentials.yaml 里的 refs）

## 3. 验证

填好 key 后，先用一条命令验证 key 与限流（不需要重启 DSH）：

```bash
# 验证 key 有效 + 免费模型可调用（curl 直连）
curl -s https://api.siliconflow.cn/v1/chat/completions \
  -H "Authorization: Bearer $SILICONFLOW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"Qwen/Qwen2.5-72B-Instruct","messages":[{"role":"user","content":"回复 OK 即可"}],"max_tokens":10}'
```

期望：返回 `choices[0].message.content`，且 `usage` 正常（免费模型计费为 0）。
若返回 `402` 或 `onlyByChargeBalance` 相关错误 → 该模型需充值；若返回 `401` → key 填错。

确认后**重启 `dsh-web.service`**（会中断当前会话）使 provider 生效：

```bash
systemctl --user restart dsh-web.service
```

重启后在 DSH 设置 → 模型里应能看到 `SiliconFlow free (Qwen2.5-72B)` 这个 provider。

## 4. 排位建议（与现有 provider 的关系）

| 角色 | 现有 | 新增 siliconflow |
|---|---|---|
| 主力强模型 | sensenova `deepseek-v4-flash`（1M ctx） | `Qwen2.5-72B-Instruct` 可作**免费第二主力**（1,000 RPM 远比商汤 5 小时 1,500 次/模型宽裕） |
| 长上下文 | md `DeepSeek-V4.1-Flash`（1M） | `GLM-Z1-9B-0414`（131K）|
| 超长 | — | `Qwen3.5-4B`（262K）|
| 兜底 | local-bonsai（离线） | — |

**硅基流动的优势**：1000 RPM 的免费额度在"无需充值"的家里是**最宽的**（对比：商汤 1500 次/5h≈300 RPM 均值但按模型；魔搭 2000 次/日合计）。适合做**高吞吐批处理主力**。
**注意**：免费模型限额不随等级提升（L0 封顶 1000 RPM），实名后不要被"充值升 L5"引导——除非你要用付费模型。

## 5. 免费 chat 模型全清单（2026-09-20 实取，供挑选）

| 模型 | ctx | tools | L0 限流 |
|---|---|---|---|
| Qwen/Qwen2.5-72B-Instruct | 32K | ✅ | 1000 RPM / 50K TPM |
| Qwen/Qwen3.5-4B | 262K | ✅ | 1000 RPM / 80K TPM |
| Qwen/Qwen3-8B | 131K | ✅ | 1000 RPM / 50K TPM |
| THUDM/GLM-Z1-9B-0414 | 131K | ✅ | 1000 RPM / 50K TPM |
| THUDM/GLM-4-9B-0414 | 32K | ✅ | 1000 RPM / 50K TPM |
| XingChenAGI/Xing4.0-29B | 262K | ✅ | 1000 RPM / 40K TPM |
| Qwen/Qwen2.5-7B-Instruct | 32K | ✅ | 1000 RPM / 50K TPM |
| deepseek-ai/DeepSeek-R1-0528-Qwen3-8B | 131K | ❌ | 1000 RPM / 50K TPM |
| deepseek-ai/DeepSeek-OCR | 8K | ❌ | 1000 RPM / 80K TPM |
| PaddlePaddle/PaddleOCR-VL-1.5 | — | ❌ | 1000 RPM / 80K TPM |
| tencent/Hunyuan-MT-7B（翻译） | 32K | ❌ | 1000 RPM / 80K TPM |

非 chat 免费：`BAAI/bge-m3`、`bge-reranker-v2-m3`、`bge-large-zh-v1.5`、`bge-large-en-v1.5`（向量/重排）、`Kwai-Kolors/Kolors`（生图）、6 个语音模型（ASR/GSR）。
