# XWayland 后台输入隔离与 Unity/UE 可视化研究

研究日期：2026-11-05（+08:00）。本次只联网读官方源码、文档和 issue；**没有运行 GUI、发送输入、启动显示服务器、改配置、安装/卸载、删除文件/socket，也没有 commit/push。**

## 结论

- **“全都无解”不成立。** XWayland 24.1.14 的 XI2 建 master 路径没有显式禁用 MPX；维护者还用 XWayland 重现过新增 master 的问题。未得到保证的是“共享 rootless XWayland + satellite + 未改 Unity”的完整多 seat 行为，不是“XWayland 根本没有 MPX”。[S1]；[S2]；[S3]
- **推荐先验收：独立 GPU XWayland + 独立 satellite，只连接 niri 的 agent-only Wayland socket。** 私有 server 的唯一 core pair 服务 AI，人的 X server 不参与，Unity 不必认识多 seat。公开 niri agent fork 已有独立 socket/隐藏用户 seat 的实现；先查本机 fork 是否已有，不要先改 Unity，也不要先装 Xpra。[S12]；[S13]
- **Xpra 是真正的逐窗口 seamless 转发，不是笼统的 VNC。** 默认 backing display 可以是 Xvfb 或 Xorg dummy 等，GPU 要另外成立；mmap 是同机像素传输优化，不是独立输入设备，也不等于 GPU 零拷贝。Xpra + GPU XWayland、Xpra + VirtualGL/OpenGL 都有官方路线。[S15]；[S16]；[S17]；[S20]
- **保留现有 Unity 进程**与**在隔离显示上重新打开同一份真实工程**是两个要求。后者可行且无须复制工程/profile；前者不能靠改外部 DISPLAY、xpra attach、切 workspace 或 shadow 自动跨 X server 迁移。MPX 是值得重新实验的“保留进程”路线，尚无本机 Unity 完整验证。

## 证据与版本边界

**原理可行**＝协议/隔离边界成立；**源码支持**＝指定版本存在实现；**本机已验证**＝运行整个组合并观察结果。本次没有进行最后一层的 GUI/输入验证。

| 对象 | 核实版本 | 边界 |
|---|---|---|
| niri | 本机包 26.04-1 | 包版本不是当前运行 fork 的 commit 证明；用户给定已有 agent-0 seat |
| xwayland-satellite | 本机包 0.8.3-1；源码 v0.8.3，commit b83eab900644e4c7c77982ce3d44cb490f0c5e1d | 无 --seat 及单份 focus/selection 判断针对此版 |
| XWayland | 本机包 24.1.14-1；tag xwayland-24.1.14，commit d958b4e84c903e8d5851b5ea587b998e4834ce62 | DIX/XI/XTEST/DDX 判断以此 tag 为准 |
| Xorg/Xvfb/Xephyr | 本机 Xvfb 包 21.1.25-2；Xephyr 源码 xorg-server-21.1.25 | 包查询中 Xephyr 未安装，不排除手工副本 |
| Xpra | 官方 release v6.5.5，2026-10-12 发布；commit a2b946884a1656d53982cc0fe3662aeacffec466 | 本机包查询未安装；主要结论用稳定 tag，不偷用 master 新功能 [S14] |
| VirtualGL | 官方 3.1.5，2026-08-14 发布 | 本机包查询未安装；此版支持 GLX 与 EGL/X11 interposition，但不替 Vulkan 做渲染转发 [S22] |
| niri agent fork 参考实现 | SHORiN-KiWATA/niri，commit 4cdb17eb40dc846f7801ce85b64ebedb9204dfaa | **不是本机 fork 身份确认**；参考实现 seat 名不能冒充本机 agent-0 |
| Toolkit 例证 | SDL 2.32.0；GTK 3.24.50；XI2 规范 2.4 | 不冒充 Unity 闭源 Editor 实际链接的版本 |

本机仅执行 `pwd`、`date -Is` 及列明上述包名的 `pacman -Q`；后者 exit=1 来自部分包未安装，不是显示栈测试失败。网页检索工具一次报 HTTP 402，此后直接 GET 官方源码、GitHub/GitLab API 和文档；未用浏览器/共享 profile，未改搜索配置。

## MPX / XI2：支持在哪，缺口在哪

### 不是普通 Xorg 结论套用到 XWayland

XWayland 指定 tag 内的实际路径：

> xinput create-master → XIChangeHierarchy(XIAddMaster) → add_master → AllocDevicePair + AllocXTestDevice → Activate/Enable → AttachDevice

[S1] 的 `add_master`（约 157–226 行）创建 pointer/keyboard **及各自的 XTEST slave**；约 436–550 行请求处理没有 rootless/XWayland 拒绝分支。XI2 构建清单也包括该实现。不能由“不能直接配置 Wayland 物理设备”推导“不能创建 X 逻辑 master”。

更直接的维护者证据：[Xserver #1611][S2] 写明 “I've confirmed this with Xwayland”，附 `xinput create-master`、reattach、disable/enable reproducer；[!1223][S3] 是相关崩溃报告。**历史故障不是 24.1.14 仍有同一 bug 的证明，也不是本机 Unity 已通过的证明。不要照抄其破坏性 reproducer。** issue 未单独证明本机 rootless 全链路；rootless 建 master 不被拒绝的依据是当前源码。

| 能力 | 源码/协议判断 | 关键条件 |
|---|---|---|
| XI2 多 master pointer/keyboard | 有实现；所查版本没有 rootless 显式禁令 | 仍需确认实际编译/发行版行为与应用 |
| 每 master keyboard 独立 focus | 有；focus 存 device 上，core Set/GetInputFocus 经 PickKeyboard(client) 选设备 [S4] | 所有注入者继续用默认 ClientPointer，就仍争同一 pair |
| XISetClientPointer | 有；可用 Unity 所属窗口选择目标 X client，也能设置调用者自身 [S5]；[S7] | 是 **X connection 级**，不是每窗口一份，也不是设备事件过滤器 |
| 普通 XTestFakeKey/Button/Motion | core 请求按注入连接的 PickKeyboard/PickPointer，再取其 XTEST slave [S6] | 每次另开连接的工具不自动继承上一个连接的 ClientPointer；不能给 Unity 设置后继续全局 xdotool |
| XTestFakeDeviceKey/Button/Motion | libXtst 与 server 有显式 device 路径 [S6]；[S31] | 是 XI1 风格 API；XOpenDevice 拒绝 master，应打开新 master 下的 XTEST **slave** [S32] |
| xinput create-master / set-cp / reattach | 官方接口存在 [S33] | 改该 DISPLAY 内的逻辑设备，不是在 Wayland 创建 seat |

另核实了 **xinput 1.6.4**：检测到 XWayland 只打印 WARNING，随后仍分派执行命令；create_master 直接发送 XIChangeHierarchy，并没有因 XWayland 拒绝。不能把这条常见警告误读成不支持 MPX。见 [CLI 分派源码](https://gitlab.freedesktop.org/xorg/app/xinput/-/blob/xinput-1.6.4/src/xinput.c#L426-435) 与 [create_master 实现](https://gitlab.freedesktop.org/xorg/app/xinput/-/blob/xinput-1.6.4/src/hierarchy.c#L38-54)；此版本是源码核验，不是本机安装版本声明。

旧式显式-device XTEST 在 server 按 `deviceid & 0177` 查找，不能假设任意高 device ID 都可直接用；设备 ID 必须查询，不能硬编码 6/8/10。[S6]

### 同 server 不等于只有一份 focus，也不等于完整隔离

**不同 XWayland 进程/监听端点的 DIX inputInfo、core focus、pointer 状态彼此独立；共享同一块 GPU 不会把它们合成一套输入。** 同一 server 的不同 screen 则不是此种隔离。satellite 的每个独立实例会新起自己的 XWayland；但必须确认新实例确实用了新 DISPLAY，且输入没有经 EI/portal 回注到同一用户 seat，才构成完整隔离。参见 [启动实现](https://github.com/Supreeeme/xwayland-satellite/blob/v0.8.3/src/lib.rs#L81-L110)。

- **同一 master pair** 共用指针/focus；**不同 master pair** 可以独立指针、键盘 focus/按键状态。前测默认 XTEST + XSetInputFocus 只覆盖前者。
- ClientPointer 解决 XQueryPointer、core focus/grab 等请求没有 device 参数的歧义；它**不阻止其他 master 的事件**进入应用。core events 不携带源设备 ID，应用可能把两套事件折叠成自己的一个鼠标/键盘状态。参见 [ClientPointer man][S7] 与 [XI2 2.4 协议](https://gitlab.freedesktop.org/xorg/proto/xorgproto/-/blob/master/specs/XI2proto.txt)。
- MPX 不隔离同一 server 的 X selection、X client 权限、资源命名空间。CLIPBOARD/PRIMARY 不会凭新增 master 变成两份；它不是安全沙箱。
- 只有向 AI 的新逻辑 master 注入、且不把人的 slaves 搬过去，才是在验证 MPX；并发调用默认全局 XTEST 不是。

### rootless 的两层特殊问题

**逻辑 X pointer 不自动等于 compositor pointer。** [S34] 的 `xwl_set_cursor` / `xwl_move_cursor` 在 device 没有 xwl_seat 时直接返回；[失焦检查](https://gitlab.freedesktop.org/xorg/xserver/-/blob/xwayland-24.1.14/hw/xwayland/xwayland-input.c#L3193-3264)也忽略非 Wayland device。这给纯合成 master 留下了不驱动人的 Wayland seat 的源码路径；代价是未必有 compositor 渲染的第二 cursor，可能需单独显示 AI 标记。**这不是已测到 Unity 全部可用。**

**XTEST 可能经 EI/EIS 逃出 X server，不能把另一个 DISPLAY 当成无条件保险。** 24.1.14 在 rootless 且编译 EI 时 override XTEST 发送处理器；可以连接 EIS socket，或在显式启用时走 RemoteDesktop portal。实现选择第一个 EIS seat，而不是按 X master ID 一一对应。[S36]

- 若 EIS 给的是人的 seat，输入会重新进入 compositor 的用户设备，隔离就破了。
- v0.8.3 satellite 的启动参数没有 -enable-ei-portal，但仍须核实实际 EIS socket 路径，不能据此认定没有 EI。
- 官方 man 明确说 **nested compositor 不应使用 -enable-ei-portal**。[S37]
- 不依赖“新 master 恰好晚于 override，所以可能绕 hook”的时序漏洞。未来若走私有 XTEST，必须验证失败时封闭在私有 server/agent EIS，不回落到人的设备。本次未触发/申请任何 portal。

### Unity、SDL、GTK 只认 core pointer 时

**core-only 不代表必然不能接收第二 master。** 新 master 设置 send_core=true，应用/注入连接选对 ClientPointer，新 master keyboard 设对 focus，server 可生成旧应用认识的 core events。这正是 MPX 兼容层的意义，不能直接判“Unity 不认识 XI2，所以无解”。[S1]；[S7]

应用级保证仍然欠缺：

- 应用反复 query/warp/grab 时用哪个 master，取决于该 connection 的 ClientPointer；主 Editor、插件、辅助连接要分别确认。
- SDL 2.32.0 的 X11 实现选择 XIAllMasterDevices raw motion，却送进同一个 SDL_Mouse 状态；普通 motion 也使用鼠标 ID 0。多设备事件可能混流，而非自动变成两个游戏鼠标。[S8]；[raw-motion 路径](https://github.com/libsdl-org/SDL/blob/release-2.32.0/src/video/x11/SDL_x11xinput2.c#L274-L308)
- GTK 3.24.50 X11 backend 有 master-pair→GdkSeat 和 XIGetClientPointer 实现，不能笼统说 GTK 只认 core。[S30]；[建 GdkSeat](https://github.com/GNOME/gtk/blob/3.24.50/gdk/x11/gdkdevicemanager-xi2.c#L548-L560)
- Unity Editor 闭源，本次未逆向其二进制或试输入；不能由其他 SDL/GTK 版本声称 Unity 已兼容。必须覆盖菜单、modal、文本、拖拽、Scene/Game 视图、锁鼠/raw relative，不能只测一个字母。

### AI master 能否绑定 Wayland agent-0，需要改谁

XWayland 会绑定多个 wl_seat，但 24.1.14 每 seat 的 pointer/keyboard 被创建为 **slave**。新增 device 默认 coreEvents=true，通用 EnableDevice 把 core slaves 挂到全局 core pair；**没有每 wl_seat 自动分配一对 master**。seat name 回调为空，X device 名后缀是内部 registry ID，不是 agent-0 文本名。[S35]；[S38]；[默认 coreEvents](https://gitlab.freedesktop.org/xorg/xserver/-/blob/xwayland-24.1.14/dix/devices.c#L289-300)

可以研究 XI2 reattach，把 agent 对应 pointer、relative pointer、keyboard 等 slaves 挂到新 master，保留 device 原有 Wayland seat 关联。但 satellite v0.8.3 的 XWM 还需配合：

- 所有 keyboard enter 都写一份 to_focus / last_kb_serial，最终同一 XWM connection 做 core SetInputFocus。[S10]；[S11]
- SelectionStates::seat_created 每次覆盖同一个 clipboard/primary device。上游 [#554][S39] 正报告“两 seat 时最后 seat 的 device 搭上另一 seat 的 serial”；[源码覆盖点](https://github.com/Supreeeme/xwayland-satellite/blob/v0.8.3/src/server/selection.rs#L42-L49)可独立核对。该 issue 无维护者回复，不把报告者局部修法当成维护者承诺。
- v0.8.3 CLI **没有 --seat、-seat 或 seat-name selector**，通读参数解析可确认。换 display number 不是选 seat；也不是 Xorg/logind 的物理 seat 选项。[S9]

两种改法不可混称：

1. **共享一个 XWayland 的完整 MPX 改造**：XWayland 建立/维护 wl_seat↔master pair，处理 hotplug、keymap、pointer hooks；satellite 按 seat 做 XISetFocus/ClientPointer 和激活，明确 selection 策略。可以先用运行时 reattach 实验，但不能掩盖 XWM focus 单份状态；通常无须先改 Unity。
2. **更小：AI 私有 XWayland/satellite 只看 agent-0**。唯一 core pair 就是 AI，不要求 Unity/SDL/GTK 支持多 seat。若 niri 已有 per-client seat filter/agent-only socket，satellite 可不改；没有则优先复用 niri fork 过滤，或给 satellite 做完整的 seat 选择/代理过滤，不能仅改 clipboard 选第一 seat。

公开 niri fork 的 [agent-only socket/global filter][S12] 给从独立 socket 进入的 client 打 agent 标记；[用户 seat 创建处实际应用该 filter](https://github.com/SHORiN-KiWATA/niri/blob/4cdb17eb40dc846f7801ce85b64ebedb9204dfaa/src/niri.rs#L3447-L3455)，不是未接线的辅助函数，用户 seat 对这些 client 不可见；[launch API][S13] 特意 unset DISPLAY，因为普通 X11 会走人的 server。**先在这个 socket 上启动私有 satellite，再让 Unity 指向它的新 DISPLAY，正好补上 X11 缺口。** Unity 不需说 Wayland。

**本机已有 agent-0，不证明已有独立 socket，也不证明 activation/clipboard/relative 已覆盖。** 必须只读核对本机 fork；参考 fork 与本机版本、seat 名不可混用。

## 私有显示、Xpra、Xephyr、nested Wayland 比较

“GPU 可行”指**应用在真实 GPU 渲染**，不是客户端 GL 贴图或编码用了 GPU。新会话均可直接访问原工程路径，不要求工程副本；同文件可访问不等于可同时安全打开同一工程。

| 路线 | GPU / Unity / UE | 输入与呈现 | 现存窗口/迁移 | 判断 |
|---|---|---|---|---|
| 共享 rootless XWayland 新增 MPX master | 原渲染路径不变，已有 GPU 可保留 | 可独立 X focus/逻辑 pointer；toolkit、XWM、EI 仍需验 | 可尝试现存 Unity，不是跨 server 迁移 | 有源码支持；完整组合本机未验证 |
| **私有 GPU XWayland + satellite + agent-only socket** | X11 GL/Vulkan 经 DRI/GBM/dmabuf；Unity/UE 无须多 seat | niri 原生顶层窗口；只有 AI seat 进入私有 core pair | 新 DISPLAY 需新起 Editor；不热迁移任意旧进程 | **首选 POC**，复用已装 satellite 和已有 fork |
| Xpra seamless + Xvfb/Xorg dummy | 默认软件 GL，不能称 GPU UE/Unity | 真逐窗口 native client；输入留私有 backing server | 一般新起；attach 只接 Xpra session | 输入隔离成立，默认 GPU 不成立 |
| 上一项 + VirtualGL 3.1.5 | GPU OpenGL，GLX 和 EGL/X11 均有；Unity 可验 -force-glcore；**不替 Vulkan 加速** | Xpra 同机 mmap 降开销，观看端可只读 | vglrun 启动，不是给活进程补挂库 | 成熟候选；不当现代 UE Vulkan 方案 |
| Xpra seamless + 私有 GPU **rootful** XWayland + --use-display | 官方路线；可保 XWayland 直接 GL/Vulkan，须验实际 driver/DRI | Xpra 做 XWM、输出 native 逐窗口；背后 rootful/nested 可隐藏 | 在此 display 起应用或接管整个既有 display；不跨 server 搬 Unity | 可行替代；不与 satellite 同抢一个 XWM |
| Xpra shadow 人的 display/指定窗口 | 原应用 GPU 不变，多 capture 层 | 适合看；默认控制仍往源 display 的 XTEST/core pointer 发 | 可看现存应用，没有迁移/独立 core focus | **只读观看可用，控制隔离不成立** |
| Xephyr 私有 server，必要时 +VirtualGL | -glamor 是 **2D** 加速，不证明客户端 GPU 3D；+VGL 可 OpenGL；本机 AMD Vulkan 不据此承诺 | 真 nested X server，一个宿主 X 窗口；避免 host grabs | 新起，不迁移活进程 | 隔离原理成立，通用 GPU 路径不如 XWayland |
| GPU nested Wayland（如 Weston wayland backend）+ 内层 XWayland | GL renderer/适当 dmabuf 可保 GPU；Unity 走内层 X，UE 可原生 Wayland | 内部窗口装在外层一个 niri 窗口；内部 focus/pointer 独立 | 内部新起，不搬现有窗口 | 不是 VM；接受单容器窗口时可行，锁鼠须专验 |
| Xpra 原生 Wayland backend + 私有 satellite/XWayland | 6.5.5 有 GPU render-node/compositor 源码 | 可转发新 Wayland surfaces；不应说完全不支持 Wayland | child env 删除 DISPLAY，**并未自动给 Unity 提供 X server** | 实验组合，有代码，额外 X11 桥和整条链本机未验 [S29] |

### Xpra 底层不是一句 VNC

v6.5.5 的 [配置模板][S17] 明列 Xvfb、Xorg/Xdummy、Xephyr、weston+XWayland。Xdummy 是标准 Xorg + dummy video driver，不是远程协议。[S18]

正常 X11 seamless 由 Xpra 做 XWM/compositing，以 Composite 窗口 pixmap 等机制逐窗口取图，经自有协议发客户端。[S15]；[S19] Native client 创建宿主独立顶层窗口；HTML5 client 才把它们留在网页 canvas。因此本需求应考虑 **native client 或 niri 原生窗**，不是再让共享浏览器切一个远程桌面 tab。

**mmap 与 MIT-SHM/capture 不同层。** 官方 man 把 --mmap 定义为 memory-mapped pixel data transfer，本地共享 filesystem namespace 时通常自动启用；它降低网络/传输开销，不新增 GPU、设备或焦点隔离。[S16] 不能宣传成“直接 mmap GPU Unity 窗口、没有 capture 成本/必然零拷贝”。

### attach、use-display、shadow 要分开

- **attach**：连接已有 Xpra server/session；应用继续在原 backing X server。不是收编任意 X11 display 下的单个 Unity。[S16]
- **--use-display**：不创建 framebuffer，使用并管理整个指定 X display。官方明确说接管后原 session 不再照常作为本地 display 使用。对人的 satellite 主 display 用它，会竞争 XWM/Composite，不能当无干扰抓一窗。[S20]；[S21]
- **shadow**：捕获现存 display；有按窗口/应用筛选的实现/实验，[维护者 #3476 评论][S26]给过 xterm 示例。但是源 app 的 X focus/pointer 不因此复制；两个 viewer 不是两个输入席位。[S27]
- **private rootful XWayland + Xpra** 与 **private rootless XWayland + satellite** 是两套管理所有权；不要在同一 server 叠两个 XWM。Shadow 观察者与 use-display 接管者也不是一回事。

当前 master 新 input-capture/KVM 功能会 grab/warp **客户端本地**鼠标键盘；维护者也写了 GTK3 Wayland client 限制。它用于“人把输入交远端”，**不是 AI 不碰人的输入**，不可借“支持 relative”直接推荐开启。[S28] Native viewer 若只观看，可用 --readonly=yes、--clipboard=no，但仍要由 niri 阻止新窗/激活抢焦点；readonly 不自动等于 no-activate。[S16]

### GPU 不能用出现画面代替

**本机 UE 的额外口径**：工作区指令给定已有强制 Wayland 的本地引擎补丁，本次未重新检查其源码/二进制。使用该构建时，应让 UE 直接连 agent-only Wayland socket，不靠 DISPLAY 强迫它走 X11；XWayland 主要解决 Unity。表中“UE 经 XWayland”只针对支持该 backend 的引擎构建，不是本机引擎的运行承诺，也不建议为此撤回现有 Wayland 策略。

- Xpra 默认 virtual framebuffer 的 OpenGL 是软件渲染，官方文档直接说明；客户端 OpenGL 加速是另一回事。[S20]
- VirtualGL 3.1.5 EGL backend 可经 EGL device 使用 GPU，无须另有 3D X server；应修正“必须起独占 GPU 的第二个真实 Xorg”说法。它仍是 **OpenGL 路线**，包含 GLX emulation 和 EGL/X11 interposition。[S22]
- [Xpra 维护者 #4751 评论][S23]明确指出 vkcube 是 Vulkan，vglrun 帮不了。不能把 Unity -force-glcore 成功外推为 UE Vulkan 成功。Unity 2022.3 官方文档同时提供 -force-glcore 与 -force-vulkan，须记录实际 API。[S40]
- Xephyr 帮助明确写 -glamor 为 “Enable 2D acceleration using glamor”；宿主 GLX 成功不是内部客户端硬件 DRI3/Vulkan 的证据。[S25]
- Weston 官方区分 backend 与 renderer：wayland backend 能嵌套在现有 compositor 中，GL renderer 可用 GPU；**不是 VM，无须另一个 VT/DRM master**。反之，headless backend 本身不证明 GPU，Xpra 简单 Weston wrapper 没显式选 GPU renderer。[S41]；[S42]
- Xpra 6.5.5 的原生 Wayland backend 已有 render-node/GLES2 创建代码，但不自动带 X11 bridge：其 child env 主动删除 DISPLAY。Unity 仍需私有 XWayland/satellite；这是新增组合而不是稳定 X11 seamless 默认功能。[S29]；[child env](https://github.com/Xpra-org/xpra/blob/v6.5.5/xpra/wayland/server.py#L91-L100)

## 共同限制

| 维度 | 不能省掉的边界 |
|---|---|
| focus | X client focus、satellite XWM focus、用户 seat、agent seat、浏览器 active tab 是不同状态；一个没变不能替其他几个作证 |
| 显示到人眼 | 非激活地把原生窗/只读预览放到当前输出；不先 focus 再还回去。隐藏 workspace 只存放，不是输入隔离来源 |
| 真实指针 | 私有 server 仍要排除 EI/portal/uinput 返送、宿主 pointer lock/warp、观看端 grab；不只检查 XQueryPointer |
| clipboard | 同 server selection 不随 master 分裂；私有 server 可分离，但桥接仍需 agent seat 或关闭。核对 PRIMARY 与 CLIPBOARD，不复制活 profile |
| relative mouse | 坐标点击通过不等于 Scene 右键相机、raw delta、warp/constraints 通过。参考 fork AgentAction 未显示专门 raw-relative API，不能给本机 fork 臆造一个 [S13] |
| popup/modal | Unity 菜单、native dialog、工具窗都要走私有 server；辅助程序若启动回人的 DISPLAY/旧进程，会逃出边界 |
| GPU | 记录真实 adapter/driver/API/render-node；拒绝 llvmpipe/lavapipe/SwiftShader 被报为 GPU，也不能用 client GL/NVENC/VAAPI 代替应用 GPU |
| 工程 | -projectPath 直接真实目录；HOME/license/prefs 不复制。不能两 Editor 并发写同工程，不删锁、不绕锁；Hub 单实例转发不能假定遵守新 DISPLAY |
| 寿命 | 进程绑显示连接；私有 server 停/重启可能让未保存 Editor 退出，不承诺恢复未保存状态 |
| 安全 | 同 UID/文件/GPU 不是安全沙箱；本题解决输入/焦点互扰，不隔离恶意应用、GPU 负载、DBus、音频或文件权限 |

## 唯一推荐的最小 POC（设计，不实施）

**已有 niri agent-only socket → 独立 satellite 0.8.3 → 独立 GPU XWayland 24.1.14 → 新启动真实 Unity Editor；输入走 niri agent seat，观察走按窗口 capture/非激活原生展示。**

首轮 **不加 MPX、不装 Xpra/VirtualGL、不加 VM、不复制 profile/工程、不改 Unity**。私有 server 只用一套 core pair，避免要求 Unity 支持多 seat。

### 前置闸门

1. 只读确认本机 fork 有 agent-only socket/global filter；连接者只见 agent-0、看不到用户 seat；新窗口/activation 也不抢人的焦点。公开 fork 已有实现，不冒充本机已有。
2. 若只有第二 seat、没有过滤，最小缺口是 **niri per-client seat 可见性/agent 标记**，或 satellite 完整 seat selector，二选一，取本机已有最多的一边。不改默认/生产 satellite，也不把两个 seat 原样塞进私有实例后宣称完成。
3. 选未占用 display number，核对实际认证/连接权限；不删除任何现有 X lock/socket 抢号，不以 -ac 省掉访问控制。
4. 选真实但当前未被 Editor 打开的工程。若用户正开着，保留该进程；是否保存后重开由用户另行授权，不强关、不删锁、不复制工程/profile。

### 验收顺序

1. **记录人的状态**：focused-window id、workspace/output、用户 pointer 位置、当前输入目标、浏览器 active tab、CLIPBOARD/PRIMARY 哨兵。先在人不动设备时测，再让人正常并发输入。
2. **私有显示链**：新 satellite 的外部 Wayland connection 指向已核实的 agent-only socket，内部起自己的 XWayland。注册/绑定只有一个允许 seat；进程和连接证据确认这是新 server，不是 :0 别名。不要改生产。
3. **真实 Editor**：用实际 Editor 二进制、新 DISPLAY、原工程 -projectPath；绕开会请求旧进程的 Hub/单实例代理，确认真实连接。先保实际 GPU API，不强迫降 OpenGL 掩盖 Vulkan 问题。
4. **后台输入**：按 niri window id 从 agent seat 发点击、文本、快捷键、滚轮、拖拽；不用默认 core XTEST，不申请全局 portal/uinput。satellite 将唯一 agent seat 翻译成私有 core 输入。
5. **展示不切人窗口**：按 id 转 floating，再按 id 移到人的当前 workspace，明确 focus=false，不调用 focus-window/workspace。26.04 IPC 有按 id 的 MoveWindowToFloating、MoveFloatingWindow、MoveWindowToWorkspace 和 focus 参数；**参数存在不等于行为已测**，全程监测焦点/workspace。[S43] AI 另用已有按窗口 capture，不开共享浏览器 tab。若呈现仍抢焦点，判失败、限定补 niri 呈现路径，不先抢再还。
6. **最小操作量**：100 次 pointer motion/hover、30 次按键（含组合键和释放）、10 次跨部件拖拽；覆盖菜单→modal→关闭、文本框、Inspector 数值拖动、Scene 右键/relative 相机、独立工具窗。每个动作有明确目标/结果。
7. **GPU/离屏更新**：同真实工程核对 hardware adapter/API；可见、被遮挡、移出可见区域三种状态均要能拿到最新画面并响应。记录 capture 延时、帧更新和失败样本；不靠切回 workspace 隐藏离屏失效。
8. **并发反证**：人先在原生 Wayland app，再在自己的普通 XWayland app 持续输入；AI 同时操作私有 Unity。检查人键不进 Unity、AI 键不进人窗，真实 pointer 不被移动/隐藏/warp/锁定；特别覆盖 modal 与激活请求。

### 通过判据

- 全程人的 focused-window、workspace、输入目标、浏览器 active tab **零次被 AI 改变**，不接受“最后恢复”。
- 人不动设备的样本中，真实 pointer 位置/锁定/显示状态 **零次被 AI 改变**；人并发输入时无 AI 事件进入用户 seat，无粘住修饰键。
- Unity 点击、键入、拖拽、modal、所需 relative mouse 全通过；不是只通过键入。agent API 若缺所需 raw-relative/constraints，按原需求记未通过，不拿绝对坐标冒充。
- 原生窗能进入人的当前视野而不激活；capture 是真实最新画面，GPU 是 hardware 而非 fallback。真实工程、许可/profile 没有复制。
- 人的 clipboard/PRIMARY 哨兵未被自动桥接覆盖；若 agent 用 clipboard，其来源/seat 归属能解释。

### 立即失败与止损

- 绑定用户 seat、落回默认 DISPLAY、出现人 cursor/focus/tab 变化、出现全局回注：**立即停止 POC 输入并保留证据**；低概率不是隔离。
- GPU 退软件、relative 不工作、popup/辅助进程逃回主 display、capture/隐藏窗口不刷新：指出失败层，不宣告可用。
- 本机无 agent-only socket：报告明确最小源码缺口，不先堆远程桌面绕开它。
- 不能接受重开 Unity：停止“私有 server 迁入活进程”的承诺，另立 MPX 接管现有进程实验。它值得做，不是已被证明失败，也不是本次已实施。

## 主要来源

[S1]: https://gitlab.freedesktop.org/xorg/xserver/-/blob/xwayland-24.1.14/Xi/xichangehierarchy.c#L157-226
[S2]: https://gitlab.freedesktop.org/xorg/xserver/-/issues/1611
[S3]: https://gitlab.freedesktop.org/xorg/xserver/-/merge_requests/1223
[S4]: https://gitlab.freedesktop.org/xorg/xserver/-/blob/xwayland-24.1.14/dix/events.c#L4883-5015
[S5]: https://gitlab.freedesktop.org/xorg/xserver/-/blob/xwayland-24.1.14/Xi/xisetclientpointer.c#L62-103
[S6]: https://gitlab.freedesktop.org/xorg/xserver/-/blob/xwayland-24.1.14/Xext/xtest.c#L181-454
[S7]: https://gitlab.freedesktop.org/xorg/lib/libxi/-/blob/libXi-1.8.2/man/XISetClientPointer.txt
[S8]: https://github.com/libsdl-org/SDL/blob/release-2.32.0/src/video/x11/SDL_x11xinput2.c#L149-L156
[S9]: https://github.com/Supreeeme/xwayland-satellite/blob/v0.8.3/src/main.rs#L111-L286
[S10]: https://github.com/Supreeeme/xwayland-satellite/blob/v0.8.3/src/server/event.rs#L843-L934
[S11]: https://github.com/Supreeeme/xwayland-satellite/blob/v0.8.3/src/xstate/mod.rs#L1381-L1390
[S12]: https://github.com/SHORiN-KiWATA/niri/blob/4cdb17eb40dc846f7801ce85b64ebedb9204dfaa/src/agent/mod.rs#L176-L220
[S13]: https://github.com/SHORiN-KiWATA/niri/blob/4cdb17eb40dc846f7801ce85b64ebedb9204dfaa/niri-ipc/src/agent.rs#L18-L145
[S14]: https://github.com/Xpra-org/xpra/releases/tag/v6.5.5
[S15]: https://github.com/Xpra-org/xpra/blob/v6.5.5/docs/Usage/Seamless.md
[S16]: https://github.com/Xpra-org/xpra/blob/v6.5.5/fs/share/man/man1/xpra.1#L469-L522
[S17]: https://github.com/Xpra-org/xpra/blob/v6.5.5/fs/etc/xpra/conf.d/55_server_x11.conf.in
[S18]: https://github.com/Xpra-org/xpra/blob/v6.5.5/docs/Usage/Xdummy.md
[S19]: https://github.com/Xpra-org/xpra/blob/v6.5.5/xpra/x11/bindings/composite.pyx#L18-L81
[S20]: https://github.com/Xpra-org/xpra/blob/v6.5.5/docs/Usage/OpenGL.md
[S21]: https://github.com/Xpra-org/xpra/blob/v6.5.5/xpra/x11/wm_check.py#L79-L121
[S22]: https://rawcdn.githack.com/VirtualGL/virtualgl/3.1.5/doc/index.html
[S23]: https://github.com/Xpra-org/xpra/issues/4751#issuecomment-3714781009
[S24]: https://gitlab.freedesktop.org/xorg/xserver/-/blob/xorg-server-21.1.25/hw/kdrive/ephyr/man/Xephyr.man#L24-68
[S25]: https://gitlab.freedesktop.org/xorg/xserver/-/blob/xorg-server-21.1.25/hw/kdrive/ephyr/ephyrinit.c#L129-141
[S26]: https://github.com/Xpra-org/xpra/issues/3476#issuecomment-1079720512
[S27]: https://github.com/Xpra-org/xpra/blob/v6.5.5/xpra/x11/server/xtest_pointer.py#L14-L36
[S28]: https://github.com/Xpra-org/xpra/issues/5103#issuecomment-6476138990
[S29]: https://github.com/Xpra-org/xpra/blob/v6.5.5/xpra/wayland/compositor.pyx#L285-L334
[S30]: https://github.com/GNOME/gtk/blob/3.24.50/gdk/x11/gdkdevicemanager-xi2.c#L810-L824
[S31]: https://gitlab.freedesktop.org/xorg/lib/libxtst/-/blob/libXtst-1.2.5/src/XTest.c#L298-395
[S32]: https://gitlab.freedesktop.org/xorg/xserver/-/blob/xwayland-24.1.14/Xi/opendev.c#L91-115
[S33]: https://gitlab.freedesktop.org/xorg/app/xinput/-/blob/xinput-1.6.4/man/xinput.man#L113-197
[S34]: https://gitlab.freedesktop.org/xorg/xserver/-/blob/xwayland-24.1.14/hw/xwayland/xwayland-cursor.c#L338-397
[S35]: https://gitlab.freedesktop.org/xorg/xserver/-/blob/xwayland-24.1.14/hw/xwayland/xwayland-input.c#L1672-1745
[S36]: https://gitlab.freedesktop.org/xorg/xserver/-/blob/xwayland-24.1.14/hw/xwayland/xwayland-xtest.c#L645-699
[S37]: https://gitlab.freedesktop.org/xorg/xserver/-/blob/xwayland-24.1.14/hw/xwayland/man/Xwayland.man#L55-64
[S38]: https://gitlab.freedesktop.org/xorg/xserver/-/blob/xwayland-24.1.14/dix/devices.c#L378-400
[S39]: https://github.com/Supreeeme/xwayland-satellite/issues/554
[S40]: https://docs.unity3d.com/2022.3/Documentation/Manual/EditorCommandLineArguments.html
[S41]: https://wayland.pages.freedesktop.org/weston/toc/running-weston.html
[S42]: https://github.com/Xpra-org/xpra/blob/v6.5.5/fs/libexec/xpra/xpra_weston_xvfb
[S43]: https://github.com/YaLTeR/niri/blob/v26.04/niri-ipc/src/lib.rs#L503-L525

补充直接证据：

- [satellite 启动 rootless XWayland 并设置内部 WAYLAND_DISPLAY](https://github.com/Supreeeme/xwayland-satellite/blob/v0.8.3/src/lib.rs#L81-L110)；[逐个代理 host seat](https://github.com/Supreeeme/xwayland-satellite/blob/v0.8.3/src/server/dispatch.rs#L1432-L1450)。
- [satellite 激活使用 last_kb_serial](https://github.com/Supreeeme/xwayland-satellite/blob/v0.8.3/src/server/mod.rs#L1245-L1278)；[#510 焦点抢占请求](https://github.com/Supreeeme/xwayland-satellite/issues/510)。该 issue 的“XSetInputFocus 也触发激活”描述未被本文当作所有版本实现保证。
- [XWayland 多 wl_seat 与空 name 回调](https://gitlab.freedesktop.org/xorg/xserver/-/blob/xwayland-24.1.14/hw/xwayland/xwayland-input.c#L1933-1993)；[XI2 构建清单](https://gitlab.freedesktop.org/xorg/xserver/-/blob/xwayland-24.1.14/Xi/meson.build)。
- [rootless XTEST override 条件](https://gitlab.freedesktop.org/xorg/xserver/-/blob/xwayland-24.1.14/hw/xwayland/xwayland-input.c#L3629-3633)；[EIS 使用第一个 seat](https://gitlab.freedesktop.org/xorg/xserver/-/blob/xwayland-24.1.14/hw/xwayland/xwayland-xtest.c#L783-807)。
- [niri agent launch env](https://github.com/SHORiN-KiWATA/niri/blob/4cdb17eb40dc846f7801ce85b64ebedb9204dfaa/src/agent/mod.rs#L485-L516)；[浮动/位置 IPC](https://github.com/YaLTeR/niri/blob/v26.04/niri-ipc/src/lib.rs#L810-L861)。
- [Xpra Shadow 文档](https://github.com/Xpra-org/xpra/blob/v6.5.5/docs/Usage/Shadow.md)；[native Wayland backend 分派](https://github.com/Xpra-org/xpra/blob/v6.5.5/xpra/scripts/server.py#L270-L275)。
- [VirtualGL 3.1.5 release](https://github.com/VirtualGL/virtualgl/releases/tag/3.1.5)；[维护者：不应干扰 Vulkan，不等于替其加速](https://github.com/VirtualGL/virtualgl/issues/271#issuecomment-2605340665)。

**最终状态：源码/文档研究给出了可验收路线；Unity/UE、多 master、GPU、窗口呈现与并发输入的本机端到端结论均仍未验证。**
