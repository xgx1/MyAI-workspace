---
tags: [DSH, 模型路由, 人工测试, Laya]
---

# Laya 判断层人工测试

判断层（`dsh-laya-router`）按用户轮次决定用哪个模型、什么思考档位、要不要先压缩。本文是它的手工验收步骤：每条都给「操作 → 预期」。自动测试在插件仓库里（`pnpm test`，55 个用例）；这里只写人眼要确认的东西。

> [!IMPORTANT]
> 全部测试都在**开发实例 3081** 上做，`DSH_HOME=~/.dsh-dev`。生产 3080 与它完全隔离，任何时候都不需要、也不应该重启 `dsh-web.service`。

## 前置条件

三条命令都应给出预期输出，任何一条不对就先修环境、不要往下测。

```bash
systemctl --user is-active dsh-web-dev.service laya-sidecar.service   # 两个 active
curl -s http://127.0.0.1:8083/health | python3 -m json.tool            # ok=true, degraded=false
journalctl --user -u dsh-web-dev.service -n 200 | grep -o '\[laya-router\].*' | tail -3
```

第三条的预期是三行：`ready (mode=live, …)`、`/route registered (…)`、`auto selector entry registered (auto/auto, registry=ok)`。**判断 `/route` 有没有挂上就看最后那两行**——插件静默挂载失败与正常工作从别处无法区分。

打开 3081 的地址（token 每次重启都会变）：

```bash
journalctl --user -u dsh-web-dev.service -n 50 | grep -o 'http://127.0.0.1:3081/?token=[A-Za-z0-9_-]*' | tail -1
```

## 测试功能清单

- 模型选择器里的 `auto` 条目
- 单轮简单问答：路由与思考档位
- 多步任务（要调用工具）：全程同一路由、不再整轮失败
- 决策记录与统计：`/route status`、`/route stats`
- 模式的运行时切换：`shadow` / `off` / `reset`
- 侧车不可用时的兜底：什么都不改、只记录

## 测试流程

**选择器里的 auto**。新建会话（或点输入框右侧的模型按钮），预期看到一组「自动（判断层逐轮选择）」，其中只有一个条目 `auto`。选中它，输入框下方显示 `auto`。

> [!WARNING]
> `auto` 是**显式开关**：只有选中它的会话才被路由。选具体模型（例如 `deepseek-flash`）时判断层完全不插手，也不会为那个会话花掉一次 Laya 调用。

**单轮简单问答**。用 `auto` 发一句明确「不着急」的小问题，例如「用一句话说明什么是 git rebase，不着急」。预期：

- 回复正常出来（不会被 `AUTO_ROUTE_UNRESOLVED` 打断）
- 会话里出现一条 `[model routed: this turn continues on …]` 通知
- 输入框下方的模型按钮跟随变成这一轮实际用的模型

**多步任务**。用 `auto` 发一个必须调用工具的任务，例如「写一个判断回文的 bash 脚本并实际运行验证一下」。预期：

- 整轮跑完（多步、有工具调用），**不再报 `route "auto" … no request should reach it`**
- 该轮每一步用的是同一个模型（在会话事件里看 `request/header` 连续相同）

**决策记录与统计**。在同一会话里输入 `/route status`，预期回报当前模式、决策日志路径、以及最近一次决策（路由 key、依据 `laya` 还是 `unlabeled`、耗时）。再输入 `/route stats 20`，预期给出最近 20 条的路由分布、依据分布、压缩次数与平均判定耗时。

也可以直接看文件：

```bash
tail -3 ~/.dsh-dev/laya-router.jsonl | python3 -m json.tool --json-lines
```

每条记录含：`state.elided`（判断状态被裁掉几条消息）、三个答案的 `confidence`、`route.key` 与 `basis`、`applied`（真正跑的路由）、`response.latencyMs`（通常 15–25 ms）。

**模式切换**。依次输入 `/route shadow`、`/route off`、`/route reset`，每次都应有一句确认。切到 `shadow` 后，`auto` 会话仍能正常跑，但跑的是静态默认档（默认 `md`），决策照旧记录；`/route reset` 回到 profile 里配置的 `live`。

**侧车不可用时的兜底**。

```bash
systemctl --user stop laya-sidecar.service
```

然后在 `auto` 会话里再发一句话。预期：这一轮仍然正常完成（落到静态默认档），日志里多一条「没有 `ctx.laya`」的记录，**不会**失败。测完记得起回来：

```bash
systemctl --user start laya-sidecar.service
```

## 预期结果汇总

| 场景 | 预期 |
| --- | --- |
| 选择器 | 出现「自动（判断层逐轮选择）」组，含 `auto` |
| 具体模型的会话 | 判断层不介入，模型不变 |
| `auto` + 单轮 | 正常回复，有 `[model routed: …]` 通知 |
| `auto` + 多步 | 整轮完成，同轮内模型一致 |
| 决策日志 | 每次判定一行 JSON，含置信度与依据 |
| `/route stats` | 给出路由/依据/压缩/耗时分布 |
| 侧车停掉 | 仍能跑（静态默认档），只记录不失败 |

## 注意事项

- **框架会插一条假通知**：harness 自己会在每个 step 追加 `[model changed: … continues with auto/auto]`。它说的是「会话的选择仍是 auto」，**不是**这一轮真正服务的模型；真正跑在哪个模型看 `[model routed: …]` 通知与 `request/header`。插件无法消除它（那个选择是 session-controller 的私有 ref，不是服务），只能在文案里说清楚——见 `docs/adr/0008`「修订二」。
- **显存**：侧车常驻约 5.5 GB，与本地 Bonsai 2 27B（12.3 GB）不能同时驻留，二选一。
- **判断质量尚未标定**：Laya 基础检查点在它自己的基准上接近瞎猜，`/route stats` 里 `unlabeled`（文本没说 → 落到默认档）的占比是第一条该看的指标；占比过高就该调问题措辞或路由表。
- **改代码后必须重建**：`pnpm run build`（profile 加载的是 `lib/`），再 `systemctl --user restart dsh-web-dev.service`。

## 相关文档

- [[0008-laya-per-turn-model-router|ADR-0008 逐轮模型路由]]
- 插件自身文档：`dsh-extensions/plugins/dsh-laya-router/README.md`
