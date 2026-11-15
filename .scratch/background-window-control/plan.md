---
tags: [实现计划, 后台控制, AgentDesktop, niri, 待审核]
---

# 通用后台窗口控制：实现计划

> [!IMPORTANT]
> 状态：计划草案，等审核。审核通过前不动任何生产代码、不重启桌面。
> 功能依据：[功能文档](</home/sx/projects/MyAI/.scratch/background-window-control/spec.md>)（已通过）。

## 一句话方案

DSH 通过 Agent Desktop 自带的 MCP 接口驱动它；Agent Desktop 走应用无障碍接口做**语义控制**（已有，零侵入），画布类界面走 niri 新增的**窗口作用域输入座席**。三处改动都在现成项目上做，不新起框架。

## 代码基线

| 仓库 | 位置 | 分支 | 基点 |
|---|---|---|---|
| Agent Desktop（你的 fork） | `/home/sx/projects/agent-desktop` | `niri-scoped-input` | `5e0491ae9cfe0552cd50ca348188411d94b8abdc`（上游 main） |
| niri（你的 fork） | `/home/sx/projects/niri` | `scoped-input-poc` | `8ed0da44d974c32c6877d2f4630c314da0717ecb`（= 已发布 v26.04，正是你现在跑的版本） |

niri 基点钉在 `v26.04` 而不是上游 main：main 已比它多 245 个提交，拿 main 打补丁会把你桌面换成未验证的一堆新改动。

## 三层架构

| 层 | 承担 | 落地位置 |
|---|---|---|
| DSH 接入层 | 把窗口能力变成模型可调用的工具 | Agent Desktop 自带 `agent-desktop mcp`（stdio MCP）；DSH 侧只加一条 MCP 配置，不写新插件 |
| 控制层 | 窗口发现、语义操作、错误语义、会话与释放 | fork 的 `crates/linux`、`crates/core` |
| 桌面能力层 | 按窗口投递的合成输入、无副作用窗口截图 | fork 的 niri |

## 核心机制

**窗口作用域座席**：niri 额外创建一个独立 `wl_seat`（下称“代理座席”），它的键盘/指针焦点钉在指定窗口上；代理客户端在这个座席上创建 `zwp_virtual_keyboard_v1` / `zwlr_virtual_pointer_v1` 并注入事件。因为你自己的座席焦点、指针位置、键盘输入目标从未被改动，所以事件进不了你的前台。

选定理由：`zwlr_virtual_pointer_manager_v1.create_virtual_pointer` 与 `zwp_virtual_keyboard_manager_v1.create_virtual_keyboard` 都以 `wl_seat` 为参数，天然支持“绑到某个座席”，不需要新协议；而“只给一个座席加第二焦点”在实现上比“劫持全局焦点再还原”干净，也不会出现还原失败的残留态。

底层可行性已核（smithay 上游源码）：`SeatState::new_wl_seat`（[`src/wayland/seat/mod.rs:179`](<https://github.com/Smithay/smithay/blob/master/src/wayland/seat/mod.rs#L179>)）可重复调用建立多个座席；每个 `KeyboardHandle` 有自己的 `input` 与 `set_focus`（[`src/input/keyboard/mod.rs:1094`](<https://github.com/Smithay/smithay/blob/master/src/input/keyboard/mod.rs#L1094>)、[`:1300`](<https://github.com/Smithay/smithay/blob/master/src/input/keyboard/mod.rs#L1300>)），指针的 `motion` 直接收焦点参数（[`src/input/pointer/mod.rs:224`](<https://github.com/Smithay/smithay/blob/master/src/input/pointer/mod.rs#L224>)）。也就是说“第二座席独立焦点”不是靠猜的，是现有 API 支持的做法。

## 里程碑

### M0 基线复现（不改代码）

- 在 `/home/sx/projects/agent-desktop` 用 `cargo build -p agent-desktop -p agent-desktop-linux` 编译，确认本机能出二进制（本机已有 2146 个 crate 缓存，crates.io 可达）。
- 复跑只读探测：`status`、`list-apps`、`list-windows`、对未聚焦窗口 `snapshot`；每次前后记录 `niri msg -j focused-window`，断言焦点未变。
- 产出：`crates/linux/src/*` 相关测试基线（`cargo test -p agent-desktop-linux`）全绿记录。

验收：编译通过、基线探测结果与功能文档表格一致、基线测试全绿。

### M1 niri 代理座席最小 POC（只支持指针移动＋左键）

- 在 niri 复制一份座席创建逻辑（`src/niri.rs` 约 2368 行的 `new_wl_seat`/`add_keyboard`/`add_pointer`），生成代理座席，初始不接管任何焦点。
- 加一个内部命令（先走 niri IPC 扩展或临时代码路径）：`pin <window-id>` / `unpin`，把代理座席的键盘焦点与指针焦点指向该窗口的 surface，并同步发送 `wl_keyboard.enter` / `wl_pointer.enter`。
- 输入分发处对来自代理座席的虚拟指针事件旁路到代理座席焦点，不经过 `self.niri.pointer_contents`。
- 只实现：绝对移动 + 左键按下抬起。

验收（现场，可重复）：
1. 另开一个窗口做目标，人手在前台窗口连续打字，代理端向目标窗口发移动＋左键，目标窗口出现点击效果，前台窗口零变化（含 `focused-window` id、指针位置、输入内容）。
2. 代理进程退出/被杀后，代理座席释放，人的座席无残留按下状态。

### M2 niri 收口（键盘、拖拽、滚轮、多窗口）

- 键盘事件投递到代理座席焦点；按需补 `wl_keyboard.modifiers` 与 `leave` 语义。
- 拖拽、滚轮、相对移动。
- 同一时刻只允许一个代理座席绑定一个窗口；换窗口先解绑；多会话时排队或拒绝（明确错误）。

验收：表格化的动作矩阵逐项通过，且每次前后人的座席状态不变。

### M3 截图与观察（niri 侧）

- 目标：拿到指定窗口画面，不写剪贴板、不弹系统选择框。
- 首选：niri 已有按窗口抓取能力，改造其输出路径，补一条只返回图像数据的通道（不落盘、不占剪贴板）。
- 若不可行：改用输出抓取后按窗口位置裁剪，并明确记录“窗口被遮挡或不在当前工作区时不可用”的限制。

验收：对未聚焦、部分遮挡的窗口取图成功；人的剪贴板内容前后一致。

### M4 fork 接入（Agent Desktop 侧）

- `crates/linux/src/input/` 新增 `scoped/` 后端：连代理座席、注入指针/键盘、按动作矩阵实现。
- 把现在 Wayland 上的 `ACTION_NOT_SUPPORTED`（`cause: wayland_session`）改为：有代理座席时走新后端，没有时保持原有拒绝语义——**绝不**退回抢焦点。
- 窗口截图接入 M3 通道。
- 保持既有错误码与 `disposition`（`retry` 语义）不变，新增原因值须有文档。
- 更新 `crates/linux` 的 README 与平台文档中 Linux 能力表。

验收：`cargo test` 全绿；Windows/macOS crate 不受影响（各平台 crate 独立编译）。

### M5 DSH 接入与验收

- DSH 侧只加 MCP 配置（`agent-desktop mcp`），在 dev 环境验证，先不接生产。
- 跑功能文档里的验收标准全表，含“人同时在前台输入”的并发场景。

## 测试策略（先写测试）

| 层 | 测试 | 先写什么 |
|---|---|---|
| fork 控制层 | `cargo test -p agent-desktop-linux` | 新后端的会话生命周期、解绑清理、失败不回落抢焦点、错误原因值 |
| fork 控制层 | 现有 fake/记录式后端 | 用已有 fake sink 断言事件序列与释放顺序，不依赖真桌面 |
| niri | Rust 单测 + 现场脚本 | 座席状态机（pin/unpin/换窗口/退出）先在纯逻辑层测；再跑现场脚本 |
| 现场 | 可重复脚本 | 脚本前后抓 `niri msg -j focused-window`、指针位置、剪贴板，作为“人的状态未变”的断言 |
| DSH 侧 | MCP 冒烟 | 只读命令先跑通，再跑控制命令 |

## 风险与回退

| 风险 | 处置 |
|---|---|
| 改 niri 导致桌面起不来 | 补丁只在 fork 分支；构建产物单独命名；保留发行版 niri 二进制，一条命令切回；先在不影响日常会话的方式下验证 POC |
| 代理座席抢焦点或事件串台 | 座席分离 + 现场脚本断言人的座席状态不变；任何一次不通过即停 |
| 输入卡住（按键/按钮未释放） | 复用上游已有的释放守卫与 held-input 机制；代理进程退出时强制释放 |
| 应用不认第二座席（部分客户端只处理一个 seat） | 作为兼容性缺陷逐项记录；必要时对这类应用退回语义操作 |
| 无障碍覆盖不到的界面 | 先报准确原因，不静默降级 |

回退顺序：停代理进程 → 解绑座席 → 换回发行版 niri → 移除 MCP 配置。

## 明确不做

- 不抢焦点后恢复、不改你的工作区与标签、不用全局虚拟键鼠冒充后台输入。
- 不复制/热备浏览器资料，不删应用锁，不强开冲突实例，不强退你的应用。
- 不改生产 DSH 检出、不接生产 profile、不动 `~/.dsh` 现有配置。
- 不在没有通过计划审核前重启你的桌面或安装任何东西。

## 需要你在执行时点头的动作

1. 如果你希望我直接在你的日常会话上试装补丁版 niri（会退出当前会话），需要单独确认时点。
2. 安装 Agent Desktop 二进制或往 dev 环境加 MCP 配置时，我会先说明改动再动手。
