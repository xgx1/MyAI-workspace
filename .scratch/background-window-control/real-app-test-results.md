# 真实应用验收结果（第一轮）

计划见 [real-app-test-plan.md](real-app-test-plan.md)。本文只记录**实测到了什么**，包括失败项与失败原因。

- 日期：2026-11-05
- 被测实现：`/home/sx/projects/niri` 分支 `scoped-input-poc`，HEAD `d80a4253`（几何映射修复）；`agent-0` 座席 + IPC `scoped-target` + `scoped-screenshot`
- 注入器：`/home/sx/projects/agent-seat-probe`（`click`/`key`/`wheel`/`drag`，坐标用千分比）
- 证据：`runs/2026-11-05/TC-xx/`（焦点前后、剪贴板前后、截图、各步日志）
- 隔离：每个用例起一个**嵌套 niri**（winit 后端，独立 socket），窗口只活在该实例里；用户自己的会话只被读取用于比对，从未被注入、切换或关闭

> 复现脚本放在 `/tmp/poc`，被系统 tmp 清理清掉过一次，所以本文把关键命令与判据都写全，脚本可按需重建。

## 1. 结论表

| 用例 | 结果 | 判据 |
|---|---|---|
| TC-01 GTK 键盘 | 通过 | `zenity --entry` 收到 KEY_A→`a`、KEY_B、KEY_ENTER 后退回 `ab` |
| TC-02 GTK 点击 | 通过 | 点中 `zenity --question` 的 Yes，进程 `exit=0` |
| TC-03 滚轮 | 通过 | 5 档滚轮后 `GtkAdjustment=187.50`（37.5px/档）；人的窗口 0 事件 |
| TC-04 拖拽 | 通过 | GtkScale `value=50.00 → 84.00`（按下跳变 + 拖到 80%）；人的窗口 0 事件 |
| TC-11 .NET GUI | 通过 | Avalonia 窗口收到 click 与 A/B/Return；见 §4 的平台细节 |
| TC-12 截图 | 通过 | 连拍两张 hash 相同（`sha256 8dffe996…`），注入输入后 hash 变化；剪贴板未变 |
| TC-14 并发（人对 AI） | 通过 | AI 目标窗口收到 5 次按键；人的窗口收到 10 次 `seat=winit`、**0 次 `seat=agent-0`** |
| TC-15 目标切换/失效 | 通过 | 切到 B 后 A 冻结、B 收到事件；切回 A 继续；清空目标后两者都收不到；人的窗口 0 事件 |
| TC-17 稳定性 | 通过 | 60 轮 click+key+wheel，`failures=0`、耗时 2s、嵌套 niri RSS +540KB |
| TC-05 浏览器（合成输入） | **不通过** | Chromium 侧 0 事件，原因见 §2 |
| TC-06 浏览器（CDP） | 通过（对照） | `Input.dispatchMouseEvent`/`dispatchKeyEvent` → `clicked:2`、`typed:hello:clicks:2` |
| TC-09 UE | **部分** | 窗口 10s 内出现、点击有画面变化；编辑器主界面未在 5 分钟内加载完，未验证编辑器级交互 |
| TC-16 分数缩放 | 通过 | `output "winit" { scale 1.5 }` 生效后（`logical 846×936`，物理 1269×1404），同一拖拽得到 `value=17.69 → 82.04`，与 scale 1 的 `18.49 → 81.34` 基本一致 |
| TC-07/08 Unity | **未执行** | 见 §5 |
| TC-10 相对鼠标 | 未实现 | 功能未开发，按约定只记录缺口 |
| TC-13 视频 | 未实现 | 同上 |

四条不扰动性不变量（AI 操作期间人的前台窗口、焦点、剪贴板、niri binds）在 TC-01/02/03/04/12/14/15/17 中全部成立；TC-01 的 `focus=CHANGED` 是窗口被回车关闭导致的焦点迁移，属用例设计问题。

## 2. 浏览器：合成输入对 Chromium 无效，机制已查清

**结论：Chromium/Electron/Helium 这一系客户端，在 `agent-0` 座席上永远收不到输入；必须走 CDP。**

两段代码对得上：

- Chromium 每条 Ozone 连接**只认第一个** `wl_seat`（`ui/ozone/platform/wayland/host/wayland_seat.cc:34-37`：`if (connection->seat_ || …) return;`；`wayland_connection.h:459` 只有一个 `seat_`；`wayland_seat.cc:90-92` 的 `OnName()` 只 `NOTIMPLEMENTED_LOG_ONCE()`）。它绑的是 `winit`（seat0），`agent-0` 那条 global 看完就丢，所以那条连接上根本没有该座席的 `wl_pointer`/`wl_keyboard`。
- smithay `wayland/seat/pointer.rs:222-233` 的 `for_each_focused_pointer` 只对"与焦点 surface 同属一个 client"的 pointer 发事件。客户端没建，就没有对象可发，**静默丢弃**，合成器侧再改也发不进去。
- 之前"用 seat0 的虚拟指针点 Chromium 也没反应"是**坐标坑**：`zwlr_virtual_pointer_v1.motion_absolute` 走 seat0 时按 **output** 归一化（1269×1370），`click 500 500` 落在 610 宽的窗口之外；换成窗口中心的 `click 253 495` 立刻 `clicked:1`。

能继续走 agent 座席的是"给每个 `wl_seat` 都建设备"的客户端：GTK3/GTK4（zenity 已证）、Qt、Firefox/WebKitGTK、自写客户端（sink）。Electron 应用与 Chromium 同属死路。

强行把 agent 输入改从 seat0 发，会让人当前窗口收到 `wl_pointer.leave`/`wl_keyboard.leave`——与"不动前台"直接冲突，**不采纳**。

## 3. 产品侧缺陷（本轮新发现，尚未修）

1. **scoped 截图首次请求静默失败**：IPC 回 `handled legacy=false` 但文件不生成，`src/ipc/server.rs:390-418` 的 `with_primary_renderer(...)` 闭包未执行且无日志。每个新嵌套实例的第一张截图必失败，第二张成功（所有用例都靠自动重试绕过）。这是产品缺陷，需要查渲染器就绪时序。
2. ~~嵌套 winit 输出不吃 `scale`~~ —— **已排除，是我的用例外壳传错了配置**：旧版 `start_nested` 不看 `POC_KDL`，永远用 `poc.kdl`。改用参数传配置后 `scale 1.5` 正常生效（`scale` 由 `src/niri.rs:2869-2874` 应用），TC-16 已通过。
3. **headless 后端不可用于验收**：`src/backend/mod.rs:63` 的 headless 分支只被 `src/tests/fixture.rs` 用，main 里 `headless=false` 是硬编码（`src/main.rs:177-186`）；强行打开后 `outputs={}`（`add_output` 无人调用）、没有渲染器，截图直接失败。要么补一个带输出的 headless 引导，要么明确它只服务测试。

## 4. .NET GUI 的平台细节

- Avalonia 默认走 X11，在无 `DISPLAY` 环境里报 `XOpenDisplay failed`；必须 `.UsePlatformDetect().UseWaylandWithFallback()`（顺序反了会抛 `A fallback windowing backend must be configured before calling UseWaylandWithFallback`），并把 `Avalonia`/`Avalonia.Wayland` 版本对齐（12.1.5）。
- 走 Wayland 后 click 与按键全部到达，`clicked text=`、`key=A/B/Return` 均与注入一致。
- 由此推论：**WinForms/WPF 这类纯 Windows GUI 在 Linux 上只能跑在 Wine/X11 里**，与 X11 窗口同属当前设计的排除范围（见 §5）。

## 5. 未验证项与原因

- **Unity（TC-07/08）**：Unity Linux 编辑器是 GTK/X11 程序，而当前实现的 `PinCandidate::X11` 永不成为候选（`src/agent_seat.rs`），X11 窗口在设计上就不可控。另外 `-batchmode -createProject` 在无显示环境下只打 `Gtk-WARNING: cannot open display` 并留下空目录，本轮没能造出工程。结论：**Unity 编辑器不在当前能力范围内**，需要单独设计 X11 通道才有意义。
- **UE（TC-09）**：UE 5.8 在嵌套实例里 10 秒内出窗口，点击后截图从 45% → 73%（画面随输入变化，说明事件到达）；但编辑器主界面在 5 分钟内没加载完（日志停在 `Loading Default Modules for Plugin…`），因此"编辑器内菜单/视口操作"没有证据。这是嵌套合成器的启动成本问题，不是输入通道问题，需要在真机上重测（用户当前正用 UE，未打扰）。
- **相对鼠标（TC-10）**：未实现，属已知缺口。
- **视频（TC-13）**：未实现；`ScopedScreenshot` 连拍可作为替代证据。

## 6. 复现要点（脚本被 /tmp 清掉后按此重建）

- 起嵌套实例：`WAYLAND_DISPLAY=wayland-1 niri -c poc.kdl`（`NIRI_BIN=/home/sx/projects/niri/target/debug/niri`），从日志抓 `listening on Wayland socket: <name>`，再导出 `WAYLAND_DISPLAY=<name>`、`NIRI_SOCKET=/run/user/1000/niri.<name>.*.sock`。
- 环境变量必须显式给：`HOME=/home/sx PATH=/usr/local/bin:/usr/bin:/bin XDG_RUNTIME_DIR=/run/user/1000`，并 `unset DISPLAY`（否则应用走 X11）。
- 不扰动性判据：`niri msg -j focused-window`（id + `focus_timestamp`）、`wl-paste --list-types`、`/tmp/poc/bind-fired` 是否生成、陪跑 sink 窗口里 `seat=winit` 事件计数。
- 浏览器必须显式 `--ozone-platform=wayland`；CDP 走 `--remote-debugging-port=<port>`，判据用 `Runtime.evaluate` 读 `document.title`（页面自己把收到的指针/按键写进标题，`niri msg -j windows` 的 title 也能当免 CDP 判据）。

## 7. 下一步建议（按性价比排序）

1. 修 §3.1 的截图首次失败——它已经在拖慢每个用例。
2. 明确浏览器策略：Chromium 系走 CDP（`browserUse` 已有），合成器只管 GTK/Qt/自写客户端；文档里写清这条分界，避免把"能控"说过头。
3. X11 通道（Unity、WinForms、部分老应用）单独立项，别混进当前实现。
4. ~~缩放正确性无证据~~ —— TC-16 已在 scale 1.5 下通过；剩下的是 1.25/2.0 与多显示器混合缩放的组合，价值不高，按需再补。
