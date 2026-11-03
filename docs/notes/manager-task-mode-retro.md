---
tags: [DSH, 管理模式, 复盘, 总结]
status: 已完成（未合并、未人工验收）
---

# 管理模式任务清单闭环 — 复盘与总结

## 做了什么

把一个只在设计文档里的管理模式，变成 3081 上真跑得通的闭环：管理对话发任务 → 代建普通工作对话 → 任务清单出卡片 → 卡片可跳对话、可看执行汇报 → 提问不阻塞、答复后按答复重做。

## 改了什么

| 位置 | 改动 |
| --- | --- |
| `~/.dsh-dev/profiles/web` | 启用 `session-manager` 与空插件 `management` 预设（`workerPresets: [js, unreal]`） |
| `dsh-extensions/plugins/dsh-task-manager` | 纳管视图（读 `session_manager` 域）、回复框投递、执行汇报 Markdown、卡片视觉重做、状态与待答问题分离 |
| `deepseek-harness-dev/packages/session/session-manager` | 提问不阻塞（不结束轮次、不 park、不挡派活）、提问台账 Markdown、README 与 spec 同步 |
| `docs/` | ADR-0011（任务清单降为视图）、ADR-0012（提问非阻塞）、功能文档、实施计划、人工测试文档、本复盘 |

## 学到什么（下次直接照做）

1. **`listEvents` 只给元数据**：`sessionQuery.listEvents` 回的是 `seq/type/time/surface`，正文和 source 都在 `data` 里，要读正文必须用 `readSession(id).events`。这个错单测抓不到——因为单测喂的是我自己捏的事件形状，**只有真跑一遍才发现"永远暂无回报"**。
2. **会等的提问等于把整条工作线挂起**：原生 `ask_user_question` 适合桌面对话，不适合"用户几小时后才回"的编排。提问必须落盘 + 继续干 + 答复后重做，这条已经写死进 ADR-0012。
3. **spec 不许写真实的 home 目录**：台账默认 `<DSH_HOME>/manager-questions`，测试组合必须显式把 `questionsDir` 指到 tmp，否则每跑一次测试就往用户家里扔文件。
4. **重启 dev 实例会让浏览器 cookie 失效**：`journalctl --user -u dsh-web-dev.service | grep 'dsh web:'` 抓新 token，否则页面只剩一句"authentication required"。
5. **跨插件读未类型化域要留降级路径**：`storageDomain.get('session_manager')` 返回未类型化域，读不到就退化成 `unavailable` 让面板回落到旧列表，而不是崩。
6. **验收必须走真实链路**：本轮两个真 bug（汇报读错接口、汇报贴原始 JSON）都是 ego 真跑出来的，单元测试全绿时它们都还活着。

## 交付状态

- 3081 绿：`session-manager` 36 个 spec、`dsh-task-manager` 68 个单测、产物构建 8 个 gate 全过。
- 实测闭环：提问 → 台账落盘 → 卡片「等待你的答复 · 1」→ 回复框作答 → 台账出现「答复」→ 工作对话按答复从蓝改绿并重新回报。
- **未做（按用户要求留到最后）**：合并 dev → master、人工验收。

## 相关文档

- [ADR-0011 任务清单降为视图](../adr/0011-manager-task-list-as-view.md)
- [ADR-0012 提问非阻塞](../adr/0012-non-blocking-questions.md)
- [功能文档](../functional/manager-task-mode.md)
- [实施计划](../plans/manager-task-list-view.md)
- [人工测试](../manual-tests/manager-task-mode.md)
