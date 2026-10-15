# 上下文溢出恢复的 A/B 复现台

零成本、确定性地复现「内容超窗 → provider 报 400 → 压缩 → 重试」这条链路，用来证明
`compaction-basic` 的溢出恢复与 `auto` 解耦（2026-10-16 事故修复），并在生产合入后随时复跑。

## 文件

- `fake-llm.mjs` —— 本地假 provider，说 DeepSeek Messages（Anthropic wire）协议：
  - 非 `/v1/messages` 一律 404；
  - 末条 user 文本含 `acting as a compaction engine` 的请求判为**摘要调用**，回一段成功 SSE；
  - 否则按 `/tmp/fake-llm.mode` 行事：内容为 `1` 时**只失败下一次对话请求**（回真实报错的
    400 信封，并把该文件改写为 `0`），其余回成功 SSE。
  - 每次请求追加一行到 `/tmp/fake-llm.log`（`conversation`/`SUMMARY`、消息条数、结果）。
- `overlay.patch.yml` —— `--patch` 叠加层，把 `llm-deepseek` 的 `baseURL` 指到
  `http://127.0.0.1:18999`。

## 环境变量

`DSH_HOME` 用 dev home（`~/.dsh-dev`，其 headless profile 的组成里 `compaction-basic.auto`
已被 billion-context 的 bundle patch 置为 `false`，正是要验的姿态）；API key 从
`~/.dsh/dsh-env.sh` 导出即可，假 provider 不校验鉴权。

## 跑法

```bash
source ~/.dsh/dsh-env.sh
export DSH_HOME=/home/sx/.dsh-dev
cd /tmp
rm -f /tmp/fake-llm.log; echo 0 > /tmp/fake-llm.mode
node .scratch/context-overflow-recovery/fake-llm.mjs &   # 或 nohup

CLI=<检出的 apps/cli/lib/bin.js>          # 待验的是哪个检出就指哪个
PATCH=$(pwd)/overlay.patch.yml

# 1) 攒两点历史（都走假 provider，瞬时）
node "$CLI" --profile headless --patch "$PATCH" --json "只回复 OK"   # 记下 sessionId
node "$CLI" --profile headless --patch "$PATCH" --session-id "$S" "回复 OK"
# 2) 让下一发对话请求过窗
echo 1 > /tmp/fake-llm.mode
node "$CLI" --profile headless --patch "$PATCH" --session-id "$S" "回复 OK"; echo "exit=$?"
```

## 判据

- **过窗的那一转必须 exit=0**，且 `/tmp/fake-llm.log` 依次出现
  `conversation -> 400`、`SUMMARY -> 200`、`conversation(msgs=1) -> 200`；
  会话日志里 `compaction/start` → `compaction/summary` → 新的 `request/header` →
  `turn/end {kind: completed}`。
- **未修复的检出**（例如 master 的 `9c04460567`）：只有 `conversation -> 400`，随后
  `turn/end {kind: error, code: CONTEXT_WINDOW_EXCEEDED}`，`exit=1`。

## 2026-10-16 实测

| 检出 | 结果 |
|---|---|
| `deepseek-harness-dev` @ `c9f8e8f3b2`（修复） | `#5 conversation msgs=5 -> 400` → `#6 SUMMARY msgs=5 -> 200` → `#7 conversation msgs=1 -> 200`，`exit=0`；会话里 `compaction/start`/`compaction/summary`/`turn/end completed` 齐全 |
| `/tmp/dsh-base` @ `9c04460567`（master 基线） | `#11 conversation msgs=5 -> 400` 后无任何请求，`exit=1`，`dsh: CONTEXT_WINDOW_EXCEEDED: This model's maximum context length is 1048576 tokens. However, you requested 1098368 tokens (705152 in the messages, 393216 in the completion).` |

两次组成完全相同（同一 `DSH_HOME` 的 headless profile、同一 `auto: false`），差异只在 harness 代码。
