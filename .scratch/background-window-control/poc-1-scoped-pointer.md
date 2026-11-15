# M1 POC 记录：niri 按窗口投递指针（2026-11-05）

## 结论

**核心机制成立。** 在嵌套 niri 实例里，指针事件经独立座席 `agent-0` 投递到被钉住的窗口；持有 seat0 焦点的另一个窗口**一个事件都没收到**，嵌套实例的 `focused-window` 前后完全一致（id、`focus_timestamp` 都不变）。

整个过程在你的会话之外进行：嵌套实例是独立合成器，跑在 `wayland-2`，你的桌面只是多了一个测试窗口。

## 现场输出（原样）

```
nested_socket=wayland-2
nested_ipc=/run/user/1000/niri.wayland-2.3146641.sock
=== probe ===
motion_absolute sent on seat agent-0
left click sent on seat agent-0
=== target sink ===
seats=["winit", "agent-0"]
enter seat=agent-0 x=0.0 y=0.0
button seat=agent-0 code=272 state=Pressed
button seat=agent-0 code=272 state=Released
=== focus sink ===
seats=["winit", "agent-0"]
=== nested focus before/after ===
{"id":3,...,"app_id":"agent-seat-focus",...,"is_focused":true,...}
{"id":3,...,"app_id":"agent-seat-focus",...,"is_focused":true,...}
```

读法：

| 行 | 含义 |
|---|---|
| `seats=["winit", "agent-0"]` | 客户端真的看到了第二个座席（不是内部私有 seat） |
| `enter seat=agent-0` / `button seat=agent-0` | 事件经 agent-0 送到目标窗口 |
| focus sink 无任何 pointer 行 | 持有 seat0 焦点的窗口完全没被打扰 |
| before/after 完全一致 | seat0 焦点没被改动过（`focus_timestamp` 逐位相同） |

## 环境与做法

- 打过补丁的 niri：`/home/sx/projects/niri`，分支 `scoped-input-poc`（基点 `v26.04` = `8ed0da44`），`cargo build` 65s 通过。
- 嵌套启动：`WAYLAND_DISPLAY=wayland-1 NIRI_AGENT_PIN_APP_ID=agent-seat-target niri -c /tmp/poc/poc.kdl`（winit 后端，未用 `--session`）。
- 目标窗口：`SINK_APP_ID=agent-seat-target`，配置里 `open-focused false`，所以它**不是**嵌套实例的焦点窗口。
- 干扰窗口：`SINK_APP_ID=agent-seat-focus`，最后打开，持有 seat0 焦点。
- 投递探针：`agent-seat-probe agent-0 click`，在该座席上建 `zwlr_virtual_pointer_v1` 发绝对移动 + 左键。
- 脚本：`/tmp/poc/run-poc.sh`（可重复执行）。

## 坐标问题已修（提交 `6bfd4a69`）

初版把 50%/50% 映射成了 `x=0.0 y=0.0`。根因是 `PointerHandle::motion` 的语义：焦点元组里带的是**窗口在全局坐标里的原点**，`MotionEvent.location` 才是指针位置，smithay 用两者相减得到窗口内坐标；原实现两处都传了窗口内坐标，相减恒为 0。另一处是尺寸取 `Window::geometry().size`，客户端没设置 window geometry 时是 0，改用布局尺寸兜底。

修完实测：

```
enter  seat=agent-0 x=200.0 y=150.0     ← 50%/50% of 400×300
motion seat=agent-0 x=100.0 y=75.0      ← 25%/25%
button seat=agent-0 code=272 state=Pressed / Released
=== focus sink ===  (无任何事件)
```

## 仍未做

- 键盘、滚轮、拖拽尚未验证（M2 进行中）。
- X11/XWayland 窗口未过滤，直接 pin 会 panic（M2 第一步）。
- 补丁目前用环境变量 `NIRI_AGENT_PIN_APP_ID` 触发，不是配置开关。

## M2：键盘 / 滚轮 / X11（提交 `c1087998`、`adb545fd`）

- **键盘不需要 niri 写路由代码**：`zwp_virtual_keyboard_manager_v1.create_virtual_keyboard(seat)` 本身带座席，smithay 把它记在 `VirtualKeyboardUserData.seat` 上，`Key` 只发给该座席 `for_each_focused_kbds` 的客户端。所以投递路径 = agent 座席自己的 keyboard focus，而 `agent_pin_target()` 早已在 pin 时对它的 keyboard 调过 `set_focus`。`input_forward` 在这里是错的工具（没有东西可 forward）。
- 实测（嵌套实例）：

```
=== target sink ===        (agent-0)
enter/motion/button …      ← 指针
key seat=agent-0 code=30 state=Pressed
key seat=agent-0 code=30 state=Released
axis seat=agent-0 axis=VerticalScroll value=-15
=== focus sink ===         (seat0 焦点窗口)
(无任何事件)
bind_fired=no              ← 注入的键没有触发 niri 自己的 binds
```

- **X11 过滤**：`Mapped::toplevel()` 对 XWayland 窗口会 panic（`window/mapped.rs:319`）。改为 `PinCandidate::{X11, Wayland(Option<String>)}`，X11 永不成为候选也不挡住其它候选；补 2 个单测。用 `xmessage` 真起 X11 窗口验证：X11 窗口在布局里不影响投递、把 pin 指向 X11 则既不投递也不崩。

## M3：窗口截图不碰剪贴板（提交 `55a1d75e`）

`save_screenshot` 原本无条件把编码后的 PNG 设成剪贴板选区——即"看一眼窗口"会覆盖用户复制的东西。改成参数：

- 既有截图动作继续传 `true`；
- 新 IPC 请求 `Request::ScopedScreenshot { window, path }` 传 `false`。

实测（嵌套实例，`/tmp/poc/run-shot.sh`）：

```
clipboard_before=BEFORE-SHOT
scoped 请求后：clipboard_after=BEFORE-SHOT，types=text/plain…
              png_bytes=1101，PNG 400x300 RGBA
对照组（既有 action）：clipboard 变成 image/png   ← 证明这个开关真的有用
```

## 键盘专用的 pin 时机（提交 `2b8cd962`）

原实现只在 agent 座席第一次指针事件时才建立 pin；只打字不点鼠标的窗口收不到任何键。改为在窗口进入布局时（`handlers/compositor.rs` 的 `layout.add_window` 之后）也 reconcile 一次。实测 `PROBE_SKIP_MOTION=1`（指针全程不动）：

```
probe: skipping motion, keyboard only on seat agent-0
target sink: key seat=agent-0 code=30 Pressed / Released
focus sink:  (无事件)
```

## 运行时选目标（提交 `3bfaa1e0`）

目标窗口由 IPC 选定，不再依赖启动期环境变量：`ScopedTarget { window }`。清除目标或目标窗口关闭时会一并释放 agent 座席的键盘与指针焦点——只清 pin 不释放焦点，输入会继续送到那个窗口（实测抓到过这个泄漏）。验证：

```
ipc=handled target=Some(2)
target sink: key seat=agent-0 code=30 Pressed / Released
keys_before_clearing=2   keys_after_clearing=2   ← 清除后同一按键不再到达
```

## 并发：人和 AI 同时输入（验收项）

嵌套实例里用两个窗口：seat0 焦点在 `agent-seat-focus`，agent 目标为 `agent-seat-target`；两边同时注入按键。

```
=== window that holds seat0 focus ===   key seat=winit   code=30 Pressed / Released
=== agent target window ===              key seat=agent-0 code=30 Pressed / Released
=== seat0 focus after ===                "id":3,"title":"agent-seat-sink"   ← 未改变
```

人的按键只到人聚焦的窗口，agent 的按键只到目标窗口，两边不串。

诚实记录：第一次并发跑时，两个窗口都收到过一次 `code=125`（Meta 键，seat=winit），随后两次重跑都没有复现；顺序执行（先人后 agent）也完全没有。判为两个虚拟键盘同时建立时的 keymap 竞态，属于测试脚手架（用虚拟键盘模拟"人"）的产物，不是 agent 投递路径的问题——agent 单跑时 seat0 侧始终零事件。

## 仍未做 / 已知限制

- 任何能绑到 `agent-0` 的客户端都能注入输入；这是投递范围隔离，不是授权隔离。要真防需要座席或全局的客户端白名单。
- 没有按键重复与 IME（注入键是一次性 `wl_keyboard.key`）。
- X11 应用永远不能当投递目标。
- `agent_pin_target()` 每个 agent 事件全量扫一遍布局（有 `ponytail:` 注释）。

## 边界（没做也不该做）

- 没在你的日常会话里重启/替换 niri。
- 没有装任何系统包。
- X11 窗口（走 XWayland）不能这样定位 surface，M2 必须先过滤掉，否则会 panic（设计调研已标注）。