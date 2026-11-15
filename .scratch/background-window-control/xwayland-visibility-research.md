# Arch + niri + xwayland-satellite：显示原 X11 窗口而不抢键盘焦点

调研日期：2026-11-05。范围：本机、原应用实例、原数据；只读网络/源码研究及版本识别，不启动 GUI、不操作窗口、不注入输入、不改配置/服务、不 commit/push。下列改变窗口的命令均为**待授权验收方案，未执行**。

## 结论先行

**“不能让窗口出现而不激活”不是 X11/Wayland 的协议定理，也不能由一次 `xdotool windowactivate` 失败推出。** 现有 niri 已经具备“移动指定窗口但不激活”的能力；普通非全屏场景，最小路径是：**把原窗口设为浮动 → 用 niri 原生 IPC 移到当前可见工作区且 `focus:false` → 指定位置**。不需要新写窗口管理模块，也不需要复制 Unity/浏览器 profile 或重启应用。

但也不能把结论反向夸大成“任意场景永久不抢焦点”：**用户当前窗口处于真全屏、应用之后自行请求有效激活、用户真实鼠标触发既有 focus-follows-mouse 策略等场景，不能用这几条命令提供永久保证。** 本次只完成源码验证，尚未进行 Unity 实窗验收。

证据入口：niri 的 [`MoveWindowToWorkspace` 契约](https://github.com/niri-wm/niri/blob/8ed0da44d974c32c6877d2f4630c314da0717ecb/niri-ipc/src/lib.rs#L508-L526)、[`focus:false → ActivateWindow::No`](https://github.com/niri-wm/niri/blob/8ed0da44d974c32c6877d2f4630c314da0717ecb/src/input/mod.rs#L1322-L1351)、[浮动插入与焦点分别处理](https://github.com/niri-wm/niri/blob/8ed0da44d974c32c6877d2f4630c314da0717ecb/src/layout/floating.rs#L406-L456)。

## 版本与本机识别结果

| 对象 | 本机/上游快照 | 核验方式 |
|---|---|---|
| niri | 安装包 `26.04-1`；运行中的 compositor 与 CLI 均为 `26.04 (8ed0da4)` | `pacman -Q niri`；只读 `niri msg version`。对应 [v26.04](https://github.com/niri-wm/niri/releases/tag/v26.04)，完整提交 `8ed0da44d974c32c6877d2f4630c314da0717ecb` |
| xwayland-satellite | 安装包 `0.8.3-1`，也是查询时最新正式版 | [v0.8.3 release](https://github.com/Supreeeme/xwayland-satellite/releases/tag/v0.8.3)；tag 对应 `b83eab900644e4c7c77982ce3d44cb490f0c5e1d` |
| satellite 正在运行的程序 | PID 3087，`xwayland-satellite :0 -listenfd 100 -listenfd 52` | `ps` 与 `readlink /proc/3087/exe`；活动 inode 和安装二进制的 SHA-256 相同：`a69eb2980a6a0c42d8332de912c9ce0b043ffa0d795eab3cda66f2eea1ceb0d4`。不是只看包版本、忽略旧进程 |
| satellite 最新开发分支 | `7bf5e0dcb0d4250860b24b04a6cb3ddeada515d0`，2026-10-28 | [与 v0.8.3 的 14 个提交差异](https://github.com/Supreeeme/xwayland-satellite/compare/b83eab900644e4c7c77982ce3d44cb490f0c5e1d...7bf5e0dcb0d4250860b24b04a6cb3ddeada515d0)：修输出/弹窗取整、事件排空、root UnmapNotify、依赖与测试；下文涉及的 EWMH 激活、ABOVE/stacking、focus 逻辑没有新增实现 |
| Xwayland | `24.1.14-1` | `pacman -Q xorg-xwayland`；PID 3090 参数含 `-rootless -wm 8` |
| xdotool | `4.20260303.1-1` | `pacman -Q xdotool`；对应源码 [`d37c16111dbe38ea29194f20ac9de03cff8dfc1c`](https://github.com/jordansissel/xdotool/tree/d37c16111dbe38ea29194f20ac9de03cff8dfc1c) |

niri 最新开发快照另查到 `3c06daf928248cbd0c34141b1f9084ce50f9b59e`（2026-11-05）；命令与行为判断以**本机 26.04 对应源码**为准，不把 main 新能力套到本机。

本任务进程最初没有 `NIRI_SOCKET`，所以直接 `niri msg version` 返回：

```text
Error: error connecting to the niri socket
Caused by:
    NIRI_SOCKET is not set, are you running this within niri?
```

随后只读用户服务管理器环境，获得 `/run/user/1000/niri.wayland-1.2585.sock`，显式传入后查到上述运行版本。这是**调用者缺环境变量**，不是 IPC 缺能力。socket 路径随会话变化，不应把此路径写死进长期脚本。未执行 `xprop`、`xdotool` 或任何改变窗口状态的 IPC action。上游 tag 是对应版本的研究依据，不等同于逐项审计发行版所有构建选项。

## 三层边界：X stacking 不等于桌面 stacking

实际链路：

```text
Unity 等 X11 客户端
  ↕ X11（窗口/属性/ClientMessage）
Xwayland ← satellite 作为 XWM 管理它
  ↕ Xwayland 的 wl_surface / buffer
satellite（同时是 Wayland server 和普通 Wayland client）
  ↕ xdg_toplevel / xdg_popup / xdg-activation
niri（决定哪个工作区可见、浮动层、真实键盘焦点）
```

satellite 官方 [架构说明](https://github.com/Supreeeme/xwayland-satellite/blob/b83eab900644e4c7c77982ce3d44cb490f0c5e1d/ARCHITECTURE.md#L24-L53) 明确这三个角色，并说明 X11 侧同一输出上的 toplevel 都被放在该输出的原点；当前 hover 的 X 窗口会被提高 X stacking。它给 X11 兼容逻辑提供坐标和命中语义，**不是把所有窗口在 niri 桌面叠成一摞**。该文 [L64-L81](https://github.com/Supreeeme/xwayland-satellite/blob/b83eab900644e4c7c77982ce3d44cb490f0c5e1d/ARCHITECTURE.md#L64-L81) 进一步说明：Xwayland 的普通 `wl_surface` 必须由 satellite 补成 `xdg_toplevel` / `xdg_popup`，宿主才会显示。

niri 官方 [Xwayland 文档 L3-L6、L27-L32](https://github.com/niri-wm/niri/blob/8ed0da44d974c32c6877d2f4630c314da0717ecb/docs/wiki/Xwayland.md#L3-L32) 对此措辞很直接：satellite 把 X11 细节处理掉，交给 niri “normal Wayland windows to manage”；25.08 起 niri 已按需启动 satellite。**已有 Unity 窗口进入 niri 后，可以直接复用 niri 原生 IPC；无须在 satellite 里新增一套 IPC。**

### Map、visible、activated、keyboard focus 不是同义词

- [xdg-shell XML，固定协议提交，L435-L458](https://gitlab.freedesktop.org/wayland/wayland-protocols/-/blob/b9edf66597586c914b5b1ff3d964d7ed201adab9/stable/xdg-shell/xdg-shell.xml#L435-458)：映射需要 role、提交状态、提交 buffer；**mapped 不保证可见**。条件里没有“必须先激活”。
- 同一协议的 [`activated` 状态 L866-L871](https://gitlab.freedesktop.org/wayland/wayland-protocols/-/blob/b9edf66597586c914b5b1ff3d964d7ed201adab9/stable/xdg-shell/xdg-shell.xml#L866-871)：这是客户端装饰应画成 active 的状态，规范明确说不能据此假设实际有键盘或指针焦点。
- [xdg-activation XML L96-L107](https://gitlab.freedesktop.org/wayland/wayland-protocols/-/blob/b9edf66597586c914b5b1ff3d964d7ed201adab9/staging/xdg-activation/xdg-activation-v1.xml#L96-107)：activation 是请求，如何展示、是否拒绝由 compositor 决定。它不是通用“只显示、不焦点”的命令，更不是 map 的先决条件。
- 普通 xdg-shell 没有 X11 式任意全局坐标/通用 raise API；它有的是诸如 [`set_parent` 的父子层叠约定](https://gitlab.freedesktop.org/wayland/wayland-protocols/-/blob/b9edf66597586c914b5b1ff3d964d7ed201adab9/stable/xdg-shell/xdg-shell.xml#L663-686)。因此只修改 X server 内部栈，不会自动给 niri 下达“搬到当前工作区、浮在用户窗口上”的命令。

## X11/XWM 路线逐项复核

| 候选 | 已验证的实现事实 | 对本需求的判断 |
|---|---|---|
| `_NET_ACTIVE_WINDOW` / `xdotool windowactivate` | satellite 0.8.3 **宣告支持**该 atom，并有 ClientMessage handler | 这是激活路线，不应拿它实现“不激活显示”；旧失败不能推出可见性无解 |
| `XRaiseWindow` / `xdotool windowraise` | 普通受管理窗口的请求被转成 ConfigureRequest；satellite handler 只处理位置/尺寸，没有处理 StackMode | 不能靠这条命令控制 niri 的浮动层/可见工作区；命令成功也不等于宿主已提高窗口 |
| `_NET_WM_STATE_ABOVE` / `wmctrl -b add,above` | satellite 的 `_NET_WM_STATE` handler 只落实 FULLSCREEN，其他 atom 落入空分支；支持列表也无 ABOVE | 0.8.3 与所查最新 main 没有这条桥接；不是 X11 规范不存在“置上但不焦点” |
| `WM_HINTS.input=false` | satellite 会解析并存入 `accepts_input`；不等于把 niri toplevel 设为永不接受焦点 | 不能当 compositor no-focus 开关；修改原应用提示还可能破坏其输入模型 |
| `WM_TAKE_FOCUS` | 支持时，satellite 在宿主 keyboard Enter 后发送该协议消息；否则走 XSetInputFocus | 这是焦点传递协议，不是请求独立可见性的协议 |
| 强改 `override_redirect` / 冒充 popup | satellite 会据 X11 类型、瞬态父窗口、尺寸、hint 判定 toplevel/popup，仍需创建宿主 role | 不建议拿 Unity 主窗冒充菜单绕路；无法据此承诺保留其正常窗口关系和原行为 |

### `windowactivate` 错误究竟证明了什么

本机版本对应的 xdotool [`xdo_activate_window` L473-L510](https://github.com/jordansissel/xdotool/blob/d37c16111dbe38ea29194f20ac9de03cff8dfc1c/xdo.c#L473-L510) 会先检查 WM 的支持声明，失败时原文是：

```text
Your windowmanager claims not to support _NET_ACTIVE_WINDOW, so the attempt to activate the window was aborted.
```

这只证明**那次连接到的 X display/WM 的支持声明未满足 xdotool 前置检查**，没有证明“显示必然激活”。若用户看到的正是这条错误，继续核对原来的 `DISPLAY`、当时 WM/版本、启动时机与 root property 才合理；本次没有复现旧错误，不能替它编根因。

更重要的是，satellite 0.8.3 的 [支持声明 L286-L298](https://github.com/Supreeeme/xwayland-satellite/blob/b83eab900644e4c7c77982ce3d44cb490f0c5e1d/src/xstate/mod.rs#L286-L298) 明列 `active_win`；[`handle_client_message` L563-L565](https://github.com/Supreeeme/xwayland-satellite/blob/b83eab900644e4c7c77982ce3d44cb490f0c5e1d/src/xstate/mod.rs#L563-L565) 会调用 `activate_window`。**所以“当前 satellite 根本不支持 EWMH 激活”也不符合源码。** 源码的声明不等于本次读取了运行时 root property；后者仍未测试。

完整 activation 路径是：

1. X11 ClientMessage → satellite [`activate_window` L1245-L1279](https://github.com/Supreeeme/xwayland-satellite/blob/b83eab900644e4c7c77982ce3d44cb490f0c5e1d/src/server/mod.rs#L1245-L1279)，从 last-focused toplevel、keyboard serial 构造 token 请求；没有 activation 接口/上次焦点等条件时会提前返回。
2. token 到来 → [`handle_activations` L1361-L1377](https://github.com/Supreeeme/xwayland-satellite/blob/b83eab900644e4c7c77982ce3d44cb490f0c5e1d/src/server/mod.rs#L1361-L1377) 向宿主请求 activation。
3. niri [`token_created/request_activation` L778-L840](https://github.com/niri-wm/niri/blob/8ed0da44d974c32c6877d2f4630c314da0717ecb/src/handlers/mod.rs#L778-L840)：无 serial 的 token 标记为 urgency-only；有 serial 要校验；未过期的有效激活会 `layout.activate_window`。超时常量是 [10 秒](https://github.com/niri-wm/niri/blob/8ed0da44d974c32c6877d2f4630c314da0717ecb/src/handlers/mod.rs#L99)。

因此“有 handler”也不等于任意 `windowactivate` 都必然成功。不要用 `windowactivate --sync` 作为无焦点方案，更不要把“先激活、再还焦点”冒充“从未抢焦点”。[EWMH §3.8](https://specifications.freedesktop.org/wm-spec/latest/ar01s03.html) 本来也允许 WM 拒绝 activation。

### 为什么 raise/ABOVE 的问题是实现边界，不是协议绝对限制

[Xlib 官方 `XRaiseWindow` 手册](https://www.x.org/releases/current/doc/man/man3/XRaiseWindow.3.xhtml) 定义的是提高 sibling 栈序，位置不变；有 SubstructureRedirect 且非 override-redirect 时，只产生 ConfigureRequest，不由 X server 直接处理。xdotool 的 [`xdo_raise_window`](https://github.com/jordansissel/xdotool/blob/d37c16111dbe38ea29194f20ac9de03cff8dfc1c/xdo.c#L779-L784) 正是调用 XRaiseWindow。

satellite 选择了 [SubstructureRedirect](https://github.com/Supreeeme/xwayland-satellite/blob/b83eab900644e4c7c77982ce3d44cb490f0c5e1d/src/xstate/mod.rs#L136-L144)，但 [ConfigureRequest L477-L503](https://github.com/Supreeeme/xwayland-satellite/blob/b83eab900644e4c7c77982ce3d44cb490f0c5e1d/src/xstate/mod.rs#L477-L503) 没有把 `STACK_MODE/SIBLING` 送入处理列表；且 [`can_change_position`](https://github.com/Supreeeme/xwayland-satellite/blob/b83eab900644e4c7c77982ce3d44cb490f0c5e1d/src/server/mod.rs#L1068-L1079) 对已映射普通 toplevel 不允许任意移动。

[EWMH §5.7](https://specifications.freedesktop.org/wm-spec/latest/ar01s05.html) 则确实定义了 ABOVE，“位于大多数窗口之上”与 activation 是不同概念；只是 satellite 的 [状态 handler L541-L561](https://github.com/Supreeeme/xwayland-satellite/blob/b83eab900644e4c7c77982ce3d44cb490f0c5e1d/src/xstate/mod.rs#L541-L561) 没有实现它。即使只补 X server 的栈序，仍缺宿主 niri 的跨工作区/浮动层操作，不能据此保证对原生 Wayland 前台窗口生效。

### 为什么改 input hint 不够

[ICCCM 的 WM_HINTS / Input Focus 章节](https://www.x.org/releases/X11R7.6/doc/xorg-docs/specs/ICCCM/icccm.html) 把 No Input 与 Globally Active 都列为 `input=False`，后者仍可通过 WM_TAKE_FOCUS 协调焦点。仅清一个 input 位从协议上就不是“永不焦点”。

satellite [解析 input hint](https://github.com/Supreeeme/xwayland-satellite/blob/b83eab900644e4c7c77982ce3d44cb490f0c5e1d/src/xstate/mod.rs#L1013-L1036)、[存储提示](https://github.com/Supreeeme/xwayland-satellite/blob/b83eab900644e4c7c77982ce3d44cb490f0c5e1d/src/server/mod.rs#L989-L1007)；`require_wm_focus` 的判断是 [`!override_redirect && (has_take_focus || accepts_input)`](https://github.com/Supreeeme/xwayland-satellite/blob/b83eab900644e4c7c77982ce3d44cb490f0c5e1d/src/server/mod.rs#L117-L120)，用于 [popup 首次 configure 的 X 焦点处理](https://github.com/Supreeeme/xwayland-satellite/blob/b83eab900644e4c7c77982ce3d44cb490f0c5e1d/src/server/event.rs#L449-L459)。普通 toplevel 的 [宿主 keyboard Enter 路径](https://github.com/Supreeeme/xwayland-satellite/blob/b83eab900644e4c7c77982ce3d44cb490f0c5e1d/src/server/event.rs#L843-L879) 则根据 WM_TAKE_FOCUS 决定后续动作，并未把 input=false 转成 niri 不可聚焦属性。

最后由 [satellite run L745-L766](https://github.com/Supreeeme/xwayland-satellite/blob/b83eab900644e4c7c77982ce3d44cb490f0c5e1d/src/server/mod.rs#L745-L766) 选择发送 WM_TAKE_FOCUS 或 XSetInputFocus；底层见 [XState L1381-L1453](https://github.com/Supreeeme/xwayland-satellite/blob/b83eab900644e4c7c77982ce3d44cb490f0c5e1d/src/xstate/mod.rs#L1381-L1453)。这只是把已经发生的宿主焦点同步进 X11，不能代替宿主可见性管理。

## niri 已有能力：显示与焦点可以分离

### 明确不激活地搬运原窗口

`MoveWindowToWorkspace { window_id, reference, focus }` 的 `focus` 默认 true，但允许 false；[CLI/类型定义 L508-L525](https://github.com/niri-wm/niri/blob/8ed0da44d974c32c6877d2f4630c314da0717ecb/niri-ipc/src/lib.rs#L508-L525) 和本机 `--help` 一致。指定 `--window-id` 后，派发器找到原窗口，明确做 [`focus:false → ActivateWindow::No`](https://github.com/niri-wm/niri/blob/8ed0da44d974c32c6877d2f4630c314da0717ecb/src/input/mod.rs#L1322-L1351)。

下游 [`Layout::move_to_output` L3283-L3375](https://github.com/niri-wm/niri/blob/8ed0da44d974c32c6877d2f4630c314da0717ecb/src/layout/mod.rs#L3283-L3375) 保留该决定，把原 tile 加进目标 workspace，保留浮动状态；只有 activate 为真才切 active monitor。**这不是临时抢焦点再恢复，而是操作本身不要求激活。**

注意索引陷阱：CLI 的 workspace 参数只能解析成数字索引或名字，[FromStr L1725-L1739](https://github.com/niri-wm/niri/blob/8ed0da44d974c32c6877d2f4630c314da0717ecb/niri-ipc/src/lib.rs#L1725-L1739)；索引在 [查找函数中返回 output=None](https://github.com/niri-wm/niri/blob/8ed0da44d974c32c6877d2f4630c314da0717ecb/src/niri.rs#L3580-L3596)，随后按**目标窗口所在 monitor**搬 workspace。不同屏幕都可能有“workspace 2”，不能把当前屏的 idx 当全局 ID。

原生 JSON 类型还支持 [`reference:{Id:u64}`](https://github.com/niri-wm/niri/blob/8ed0da44d974c32c6877d2f4630c314da0717ecb/niri-ipc/src/lib.rs#L976-L986)，可直接定位全局唯一工作区，跨 monitor 也能同时明确 `focus:false`。CLI 文本参数并不提供这个 ID 语法，不能臆造 `--workspace-id`。

### 浮动、重叠与不激活

官方 [Floating Windows L5-L16](https://github.com/niri-wm/niri/blob/8ed0da44d974c32c6877d2f4630c314da0717ecb/docs/wiki/Floating-Windows.md#L5-L16)：浮动层位于 tiled windows 上方，不滚动，每个 workspace/monitor 各有一层；可显式定位。

- [`toggle_window_floating` L1388-L1436](https://github.com/niri-wm/niri/blob/8ed0da44d974c32c6877d2f4630c314da0717ecb/src/layout/workspace.rs#L1388-L1436) 判断目标是否为该工作区的 active window；转换**非 active 目标**不把目标设为 active。
- [`FloatingSpace::add_tile/add_tile_at` L406-L456](https://github.com/niri-wm/niri/blob/8ed0da44d974c32c6877d2f4630c314da0717ecb/src/layout/floating.rs#L406-L456) 可插入顶部 `index=0`，而是否变 active 是另一个布尔决定。给已有、非空当前工作区加入不激活的浮窗不会迫使键盘跟随它。
- [工作区 `add_tile` L613-L632](https://github.com/niri-wm/niri/blob/8ed0da44d974c32c6877d2f4630c314da0717ecb/src/layout/workspace.rs#L613-L632) 也把“加入浮动层”与“切 active layout”分开。
- [`move_floating_window` 的坐标运算](https://github.com/niri-wm/niri/blob/8ed0da44d974c32c6877d2f4630c314da0717ecb/src/layout/floating.rs#L954-L1001) 不激活窗口，数字 `32` 是相对 working area 的绝对逻辑坐标，`+32` 才是相对移动。

因此，显示不等于获得键盘焦点。若“前台不变”还要求**人的所有像素丝毫不变**，则在同一显示器新增可见窗口本身就不满足该额外定义；这里承诺的候选方案是原窗口/工作区与键盘不被切走，允许小浮窗改变部分画面。

### `open-focused` 与不存在的 `focus-on-activation`

niri 已有 [`open-focused false`](https://github.com/niri-wm/niri/blob/8ed0da44d974c32c6877d2f4630c314da0717ecb/docs/wiki/Configuration:-Window-Rules.md#L504-L530) 与 [`open-floating true`](https://github.com/niri-wm/niri/blob/8ed0da44d974c32c6877d2f4630c314da0717ecb/docs/wiki/Configuration:-Window-Rules.md#L480-L502)，可以让**新建**匹配窗口打开但不自动聚焦；初次 map 时 [优先采用 open_focused 规则](https://github.com/niri-wm/niri/blob/8ed0da44d974c32c6877d2f4630c314da0717ecb/src/handlers/compositor.rs#L153-L177)。不需要为此发明新功能。

但它不是现有窗口的临时开关，也不是“今后一切 activation 均被拒绝”。所查 [26.04 的完整 WindowRule 结构](https://github.com/niri-wm/niri/blob/8ed0da44d974c32c6877d2f4630c314da0717ecb/niri-config/src/window_rule.rs#L11-L82) 以及 [最新 main 的同结构](https://github.com/niri-wm/niri/blob/3c06daf928248cbd0c34141b1f9084ce50f9b59e/niri-config/src/window_rule.rs) **均无 `focus-on-activation` 字段**。不要向生产配置写入猜出来的 `focus-on-activation false`。真正的后续 activation 处理仍走上文 token 检查与 `layout.activate_window`。

本轮不提出需要立即修改配置的方案；新窗规则仅作为已有能力的说明，不对当前原实例强制 remap。

## 推荐最小方案与真实命令

### 前置条件

- 操作的是已经映射、出现在 niri windows 列表中的原 toplevel，而非已经销毁或真正 unmapped 的窗口。
- 目标不是用户当前 focused window；用户窗口及目标在操作期间不被其他主体并发切换/关闭。
- 用户当前不是把普通浮动层隐藏掉的真全屏窗口；见下一节限制。
- 把目标放到不遮住用户主要操作区、且尽量不在鼠标下方的位置。主张“不主动改变键盘焦点”，不是全局“永不可聚焦”。

以下查询只读；本轮只核对过命令 help，没有运行这些窗口枚举/控制示例：

```bash
niri msg -j focused-window
niri msg -j workspaces
niri msg -j windows
```

必须使用 niri 返回的 **`id`**，不是 `xdotool search` 返回的 XID。satellite 从 X11 class 设置宿主 app_id 的代码见 [`set_win_class` L981-L985](https://github.com/Supreeeme/xwayland-satellite/blob/b83eab900644e4c7c77982ce3d44cb490f0c5e1d/src/server/mod.rs#L981-L985)，可以用标题与 app_id 核对窗口。niri 的 [`pid` 定义](https://github.com/niri-wm/niri/blob/8ed0da44d974c32c6877d2f4630c314da0717ecb/niri-ipc/src/lib.rs#L1297-L1328) 是创建 Wayland 连接的进程，不应不经验证就等同 Unity 的 X11 进程 PID。

### 同一 monitor：三条现成 niri 命令

把 `123` 和 `2` 换成刚核实的窗口 ID、该 monitor 当前可见 workspace 索引。**仅适用于目标与当前用户在同一 monitor**；若已经是浮动窗口，可跳过第一条。

```bash
id=123
ws=2
niri msg action move-window-to-floating --id "$id"
niri msg action move-window-to-workspace --window-id "$id" --focus false "$ws"
niri msg action move-floating-window --id "$id" -x 32 -y 32
```

上述 `--id` / `--window-id` 的区别、`--focus false` 的值、`-x/-y` 均已通过**本机 26.04 的对应 `--help`**核对；并非猜参数。若 Unity 窗口过大，可以另行按需执行 `set-window-width --id "$id" 800`、`set-window-height --id "$id" 600`；这些参数也查过本机 help。缩放不是默认步骤，会改变原窗口几何，原大小应先记录。

### 跨 monitor：复用原生 IPC 的 workspace ID，无需新程序

用全局 workspace ID 省掉歧义。jq、socat 在本机分别已有对应可执行程序；不需安装依赖。下面是**报告内待验收示例**，不是已部署脚本；唯一手填值仍是 `id=123`。

```bash
set -euo pipefail
: "${NIRI_SOCKET:?请在 niri 会话环境中执行，或先取得正确的 NIRI_SOCKET}"
id=123

# 拒绝拿当前 focused window 当后台目标；也检查 ID 确实存在。
niri msg -j windows | jq -e --argjson id "$id" \
  'any(.[]; .id == $id and .is_focused == false)'
wsid=$(niri msg -j workspaces | jq -er '.[] | select(.is_focused) | .id')

niri msg action move-window-to-floating --id "$id"
jq -nc --argjson id "$id" --argjson ws "$wsid" \
  '{Action:{MoveWindowToWorkspace:{window_id:$id,reference:{Id:$ws},focus:false}}}' \
  | socat - "$NIRI_SOCKET" | jq -e '.Ok != null'
niri msg action move-floating-window --id "$id" -x 32 -y 32
```

原生 IPC 的“一行 JSON 请求、一行 Reply”来自 [官方 IPC 文档 L31-L60](https://github.com/niri-wm/niri/blob/8ed0da44d974c32c6877d2f4630c314da0717ecb/docs/wiki/IPC.md#L31-L60)；结构来自前引 `Request/Action/WorkspaceReferenceArg`，而非自定义协议。需要保留几何/工作区时，先读出目标原 `workspace_id`、`is_floating` 和 `layout`，回退仍用这些现成 action。还原 tiling 不承诺恢复原列序及全部动画状态，别把它称为完全无痕事务。

另一个已有 CLI 是：

```bash
niri msg action move-window-to-monitor --id "$id" "实际输出名"
```

它把窗口放到目标 monitor 的 active workspace，但**没有 `--focus` 参数**。本机 source 用 [`ActivateWindow::Smart`](https://github.com/niri-wm/niri/blob/8ed0da44d974c32c6877d2f4630c314da0717ecb/src/input/mod.rs#L1839-L1855)，下游只在该目标原本是**全局 active window**时跟随激活，[判断 L3336-L3347](https://github.com/niri-wm/niri/blob/8ed0da44d974c32c6877d2f4630c314da0717ecb/src/layout/mod.rs#L3336-L3347)。已确认目标未聚焦时可以复用；若要明确传 no-focus，优先上面的原生 workspace-ID 请求，而不是给它编造 `--focus false`。

## 不满足项、边界与不该承诺的事

- **当前用户窗口真全屏：** [`Workspace::is_floating_visible`](https://github.com/niri-wm/niri/blob/8ed0da44d974c32c6877d2f4630c314da0717ecb/src/layout/workspace.rs#L1682-L1687) 会在滚动布局的真全屏窗保持焦点时隐藏普通浮动层。内部确有 [`NoButRaised` 状态](https://github.com/niri-wm/niri/blob/8ed0da44d974c32c6877d2f4630c314da0717ecb/src/layout/workspace.rs#L168-L180)，但它为 focus-follows-mouse 的保层叠设计，不能凭这个内部枚举编造现成“raise without focus”命令。本最小方案不覆盖该情形；不擅自取消用户全屏，也不建议修改生产 niri。
- **已在当前 workspace 的老浮窗被别的浮窗遮住：** `move-window-to-floating` 对已浮动窗口是 no-op，`move-floating-window` 改位置但不提高栈序。可先选择未遮挡位置；不能宣称这两条等价于任意 raise。新转浮或从别的 workspace 移入的插入路径才有前述顶部插入。没有为补齐此角落而建议重写模块。
- **真正 unmapped / 已销毁窗口：** native 移动命令不会复活不存在的 toplevel。`XMapWindow` 重新映射是另一条客户端生命周期路径，不保证原 app 不自动新建窗口/请求激活；本次没有实测最小化、Unity modal 与重建行为。
- **后续自动抢焦点：** 本方案不发 activation，但不能屏蔽应用之后获得有效 token 的 activation、新弹出的 modal、其他自动化或用户真实输入。open-focused 只管初次打开，不是永久“focus lock”；要承诺无限期安全，需要另审该应用实际行为与宿主策略，不能在本次未改策略的条件下声称解决。
- **真实指针与键盘：** 这些按 ID 的动作不调用输入注入；nonfocused 路径不需 warp。窗口出现/几何变化仍会让 compositor 重算 pointer contents，[实现](https://github.com/niri-wm/niri/blob/8ed0da44d974c32c6877d2f4630c314da0717ecb/src/niri.rs#L1022-L1067)；hover/光标外观可能变化。既有 focus-follows-mouse 由真实 pointer motion 调用，[调用点](https://github.com/niri-wm/niri/blob/8ed0da44d974c32c6877d2f4630c314da0717ecb/src/input/mod.rs#L2580)、[策略代码](https://github.com/niri-wm/niri/blob/8ed0da44d974c32c6877d2f4630c314da0717ecb/src/niri.rs#L6175-L6224)。这不是一套独立后台 seat，更没有证明可并发 XTest 操作而不影响人。
- **非原子：** niri 官方 [IPC 库警告](https://github.com/niri-wm/niri/blob/8ed0da44d974c32c6877d2f4630c314da0717ecb/niri-ipc/src/lib.rs#L11-L18) 明说请求逐个处理，哪怕共用一条 socket 也不是事务。ID、focus、workspace 应在操作前复核；发生用户并发切换就停止，不“抢回”用户焦点。
- **不采用另起 nested compositor / 新 X server：** 官方确有 [labwc/rootful Xwayland 等办法](https://github.com/niri-wm/niri/blob/8ed0da44d974c32c6877d2f4630c314da0717ecb/docs/wiki/Xwayland.md#L34-L59)，但会引入新 GUI 与显示连接；对“保留当前原实例”的首选路径没有必要，也不能把现存 X 客户端凭空改连到新 server。本次一律不启动。

## 最小验收：需要另获窗口操作授权后进行

此节是**验收计划，不是已测结果**。不点击、不注入键盘/鼠标、不新建 profile、不新启动 Unity。使用用户允许观察的已有 Unity 窗口即可。

1. **只读前置核对。** 记录当前 focused-window 的 niri ID、当前 workspace 的全局 ID/输出、目标 ID/原工作区/浮动状态/几何。确认目标不是 focused window、用户窗非真全屏。跨屏用全局 workspace ID，不混用 monitor 内的 idx；若 `NIRI_SOCKET` 缺失，先从本次 niri 会话环境获得，勿改配置。
2. **监听全过程，而非只看最后焦点还原。** 在已有终端只读运行：

   ```bash
   niri msg -j event-stream | jq --unbuffered \
     'select(has("WindowFocusChanged") or has("WorkspaceActivated"))'
   ```

   事件名及字段来自 [`Event` 定义 L1587-L1598、L1627-L1632](https://github.com/niri-wm/niri/blob/8ed0da44d974c32c6877d2f4630c314da0717ecb/niri-ipc/src/lib.rs#L1587-L1632)。窗口变化事件也可旁路观察；若出现切到目标/其他非原窗口的焦点事件（包括短暂切换），判失败，不用“最后又恢复”抵账。
3. **执行所需最少 action。** 目标若本来浮动则不重复转换；先用同屏三命令或跨屏显式 `focus:false` 请求。只移动目标，绝不先 focus 它。不全屏、不 resize 人的当前窗，不测试 windowactivate。
4. **验收三项。** 目标原 niri ID 仍在、`is_floating=true` 且 `workspace_id` 是目标可见工作区；视觉上 Unity 内容确实出现在预定位置，而不是 IPC 返回成功但仍被遮住；原 focused-window/工作区/显示器全过程不被切走。若要证明实际键盘接收者而不仅是 compositor focus，需另取得人工验证许可，不能偷偷注入输入。
5. **覆盖关键反例后收工。** 至少“不同 workspace 同屏”和“跨屏”各一次；真全屏场景按已知限制记录“不满足”，不擅自绕过。目标主动弹 modal/请求激活的后续场景另列待测。按记录还原目标工作区、浮动/尺寸/位置，不关原应用；停止本次监听，不删除任何共享临时文件/套接字。

## 证据等级与本轮实际做了什么

- **已核实源码事实：** satellite 的 EWMH activation 处理、未实现 ABOVE/ConfigureRequest stacking；map 不要求 activation；niri 指定 ID 的 no-focus 搬运、浮动插入与 focus 分离；真全屏隐藏浮动层；open-focused 与后续 activation 不同；没有猜测的 focus-on-activation 配置项。
- **已核实本机只读事实：** 软件包/活动进程/运行 niri 版本；活动 satellite 二进制与安装文件相同；命令 help 的真实参数；jq/socat 已安装。没有读取本地代码仓，所以没有绕开本地代码的 graph-first 顺序；研究源码均从固定上游 URL 在内存读取。
- **基于源码的工程推断：** 满足上述前提时，现有原 Unity toplevel 可由 niri 浮动展示且操作本身不切键盘焦点。**不是 Unity 实窗已通过验收的声明。**
- **仍待实测：** Unity 特定版本的窗口/弹窗关系、目标是否真正 mapped、绘制/遮挡、后续 app activation、当前桌面策略组合。应用在窗口 resize 时是否修改自身布局/保存状态也未承诺无影响。
- 网络发现先调用了 `web_search`；第一次返回线索，第二次因 `HTTP 402: Insufficient Balance` 失败。没有修改搜索配置、没有继续重试计费接口；后续直接打开官方 GitHub/GitLab/X.org/freedesktop 资料与源码，不是仅引搜索摘要。没有调用浏览器工具或启动 GUI。

**推荐决策：先复用已有 niri IPC 做一次严格无焦点验收，删掉“windowactivate 失败所以只能 focus-window/所以无解”的旧推论；暂不写新模块。若验收要求包含“压过用户真全屏 + 永久禁止目标自行激活 + 后台独立输入”，那是超出这个最小可见性方案的新增边界，应明确标为未满足，而不是用协议禁令或预计代码行数掩盖。**
