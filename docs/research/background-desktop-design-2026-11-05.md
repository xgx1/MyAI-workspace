---
tags: [桌面自动化, Wayland, 架构设计, 调研]
---

# 本机独立后台桌面设计

> [!WARNING]
> 本文是未实施的旧候选，不再作为插件实施方案。用户已明确要求“所有有窗口的应用都可控制”及“原数据实时共用”；下文独立浏览器资料、按应用选择接入等前提不能满足该要求。当前以[通用窗口功能文档](</home/sx/projects/MyAI/.scratch/background-window-control/spec.md>)为准。

## 新要求下的现场核验

2026-11-05 只读枚举当前 Wayland 接口，只发现一个带键盘和指针能力的 seat0，存在虚拟键盘、虚拟鼠标与抓屏协议，但未发布临时独立座席协议。不能把“有虚拟鼠标”理解成“有不影响人的第二套输入”。

本机 niri 对应提交的[输入状态](<https://github.com/niri-wm/niri/blob/8ed0da44d974c32c6877d2f4630c314da0717ecb/src/niri.rs#L320-L331>)持有主座席及焦点状态；[虚拟鼠标处理器](<https://github.com/niri-wm/niri/blob/8ed0da44d974c32c6877d2f4630c314da0717ecb/src/handlers/mod.rs#L666-L689>)继续调用现有输入流程，不能直接用于独立后台控制。

按窗口标识截图虽然存在，但[保存路径](<https://github.com/niri-wm/niri/blob/8ed0da44d974c32c6877d2f4630c314da0717ecb/src/niri.rs#L5644-L5678>)还会改写主座席剪贴板；无副作用窗口观察同样需要单独处理。以上只检查了帮助、接口与源码，没有发送任何输入或抓取人的窗口画面。

[独立临时座席规范](<https://gitlab.freedesktop.org/wayland/wayland-protocols/-/raw/main/staging/ext-transient-seat/ext-transient-seat-v1.xml>)可作为后端研究候选，但当前 niri 未暴露它，加入座席也不等于所有界面框架和兼容窗口已经可用。需要先验证窗口系统后端，再谈完整插件；不能让 DSH 插件封装现有全局输入后谎称满足需求。

以下保留此前方案供比较，均未部署。

## 要解决的不是防抢焦点，而是独立操作

人的 niri 桌面保持原样。每个 AI 会话拥有自己的显示服务、窗口集合、键盘焦点、鼠标位置、浏览器进程和运行状态。

AI 可以在自己的桌面里点击、拖拽、滚动、输入文本与组合键、切换窗口并截图。人的窗口、工作区、浏览器当前标签、真实指针和键盘输入目标均不应因此改变。

这里的“工作空间”是**独立显示与输入域**，不是同一个 niri 实例中的另一个工作区；“后台输入”允许改变 AI 桌面内部的焦点，不允许改变人的桌面焦点。

## 旧方案为什么不能作为基础

| 已核验事项 | 结论 |
|---|---|
| 本机 niri | `niri 26.04 (8ed0da4)`；现有配置整体校验通过 |
| 旧核心规则 | `on-xdg-activate "ignore"` 实际报 `unexpected node`；[官方文档](<https://niri-wm.github.io/niri/Configuration:-Window-Rules.html#on-xdg-activate>)标注 **Since: next release**，不能当成本机已支持 |
| 其余旧例子 | `focus-follows-mouse off`、顶层的三个 debug 选项、`xwayland { off }` 均校验失败；`strict-new-window-focus-policy` 放入 `debug` 才通过 |
| 激活策略语义 | 官方说明 `ignore` 是既不聚焦也不标 urgent；`honor-xdg-activation-with-invalid-serial` 是放宽规则，不是加固；`strict-new-window-focus-policy` 仍允许有效 token 激活。见[官方 debug 文档](<https://niri-wm.github.io/niri/Configuration:-Debug-Options.html>) |
| 浏览器连接 | 对 9222、9224 的只读 `/json/version` 查询得到相同 browser WebSocket 标识：确实是同一个浏览器实例，不是两个独立后台环境 |
| 当前 CUA 入口 | [启动包装器](</usr/local/bin/cua-driver-session#L1-L6>)强制 `XDG_CURRENT_DESKTOP=niri`；当前全局服务不是可直接拿来隔离操作的后台桌面 |

当前 [niri 配置](</home/sx/.config/niri/config.kdl#L117-L131>)只有特定窗口的 `open-focused false`，且[鼠标跟随焦点仍开启](</home/sx/.config/niri/config.kdl#L31-L32>)。没有把未落地的建议算成已经生效的保护。

旧清单混淆了四件事：限制新窗口激活、窗口摆放、浏览器内部标签选择、操作系统输入路由。systemd 托管、后台计时器参数、重启 portal 都不会自动建立新的输入域。

## 推荐架构

**主候选：每会话 headless Sway + wayvnc + 独立应用环境。** 人继续使用 niri，不切桌面、不切 VT、不替换登录会话，也不开虚拟机。

这里优先 Wayland 而不是更省事的纯 X11 路线，是因为本机 UE 已使用原生 Wayland，且需求明确覆盖普通应用、浏览器和编辑器，而不仅是网页。若最终范围只剩 X11 普通程序，Xpra desktop 更简单，不应为它们强上这一套。

**无头的是显示服务器，不必把浏览器也设成 headless。** 完整 GUI 路线让浏览器正常以 headed 模式在私有 Sway 中运行，原生弹窗和人工登录也留在里面；浏览器切标签可以照常进行，因为它已经不是人的浏览器。

```text
人的桌面：niri ── 人的键盘/鼠标 ── 日常浏览器、编辑器
                       ↑ AI 不使用这条输入通道

DSH 会话 A ── 会话路由/鉴权 ── A 的后台 worker
                              ├─ headless Sway A / 独立 seat
                              ├─ wayvnc A / 私有 RFB 与 WebSocket socket
                              ├─ Wayland 应用 + A 自己的 Xwayland
                              └─ A 自己的浏览器 profile、CDP、D-Bus

DSH 会话 B ── 同样一套 B 环境，不复用 A 的显示/输入/状态

人主动查看 ── 鉴权后的只读 noVNC 预览 / 截图
人主动接管 ── 暂停该会话 AI 输入，再允许远程键鼠
```

[wlroots 官方环境文档](<https://gitlab.freedesktop.org/wlroots/wlroots/-/raw/master/docs/env_vars.md>)提供 `WLR_BACKENDS=headless` 和 `WLR_HEADLESS_OUTPUTS`；后端明确选 headless，不混入 drm、libinput 或父 Wayland 后端。渲染可使用 GPU render node，不需要把物理屏幕交给 AI。

[wayvnc 官方说明](<https://github.com/any1/wayvnc#readme>)明确支持 headless 会话，创建虚拟输入设备，并以 RFB 暴露显示内容。[官方 FAQ](<https://github.com/any1/wayvnc/blob/master/FAQ.md>)给出 headless Sway 的组合方式。

**不能把 Weston 和 wayvnc 随意拼起来**：wayvnc 官方明确不支持 Weston、GNOME、KDE。这也是选择 wlroots/Sway 而不是泛称“任意后台 Wayland”的原因。

## 键鼠与查看链路

| 能力 | 设计中的执行路径 | 不干扰前台的原因 |
|---|---|---|
| 移动、点击、双击、拖拽、滚轮 | worker → 成熟 RFB 客户端 → 本会话 wayvnc → 本会话 virtual pointer | 不经过人的指针或 `/dev/uinput` |
| 按键、组合键、按下/释放 | 同一 RFB 控制连接 → 本会话 virtual keyboard | 键盘焦点只属于这个 Sway |
| 中文与长文本 | 优先本会话 Unicode 文本注入；必要时用本会话私有剪贴板粘贴 | 不借用人的 fcitx、剪贴板或前台输入框 |
| 窗口列表、标题、PID、位置、内部焦点 | 本会话 [Sway IPC](<https://github.com/swaywm/sway/blob/1652c54b73f67df17b7b4ab0b0f7048204aa8104/sway/sway-ipc.7.scd>) 的 `GET_TREE`，结合输出与 seat 信息 | 不是枚举/聚焦主 niri 的窗口 |
| 当前桌面截图 | 本会话 RFB framebuffer，或绑定该显示的 grim | 不走人的交互式截图 portal |
| 查看被遮挡窗口 | 在后台 Sway 内切换/聚焦该窗口，然后截图 | 只改变 AI 桌面内部的状态 |
| 浏览器 DOM、表单与网页截图 | 本会话浏览器的专用 CDP | 不连 9222/9224，不选择人的标签 |

输入客户端候选采用 [vncdotool](<https://github.com/sibson/vncdotool>)，不自写 RFB。其[命令表](<https://vncdotool.readthedocs.io/en/latest/commands/>)包含键盘按下/释放、鼠标移动/按下/释放、拖动与截图；[源码](<https://github.com/sibson/vncdotool/blob/main/vncdotool/command.py>)可识别已存在的 Unix socket 路径。与 wayvnc 0.10.2 的实际握手、键盘布局、滚轮及 Unicode 路径仍属于必须跑的 POC，不以“都说 VNC”代替兼容性验证。

窗口列表主要是 compositor 管理的顶层窗口；菜单、tooltip、部分 unmanaged Xwayland 窗体可能没有独立树节点。完整 output 截图负责观察这些浮层，不能把“没有独立窗口 ID”当成“没出现弹窗”。菜单操作期间保留后台原有焦点，不要每个输入事件前都重新聚焦父窗口、把菜单自己关掉。

本机已装 wtype、grim、wl-clipboard，可复用而不是另写文本或截图实现。[wtype 官方说明](<https://github.com/atx/wtype>)展示 Unicode 输入、组合键、按下/释放，并说明进程结束会销毁关联虚拟键盘。通用应用的中文仍需实测，不能把 ASCII 成功等同于输入法成功。

[Sway 官方输入手册](<https://github.com/swaywm/sway/blob/master/sway/sway-input.5.scd>)说明每个 seat 有独立键盘焦点与光标；同时已将 IPC 的 `seat cursor` 指令标为 deprecated。因此不把这些旧鼠标指令作为新方案的核心输入接口。

## 每会话需要隔离的东西

| 范围 | 要求 |
|---|---|
| 运行身份 | 正式隔离版每个 AI 会话使用不同的系统 UID，配合受限 mount/PID/network/device 环境；不获得人的 HOME/runtime、会话总线、输入设备或自动化端点。可考虑 systemd DynamicUser，但实际权限、namespace 与 GPU render 访问必须 POC |
| 显示与输入 | 独立 compositor、headless output、seat、Wayland socket；X11 应用使用这个 compositor 启动的 Xwayland，不能继承 `DISPLAY=:0` |
| runtime | 每会话私有 0700 目录；Wayland、Sway IPC、RFB、WebSocket socket 都留在这里 |
| D-Bus | 每会话私有 session bus，不使用人的 bus；不向全局 user manager 导入后台桌面的环境 |
| 应用状态 | 每会话独立 HOME/XDG 配置与状态；Chromium 必须独立 user-data-dir、进程和控制端点 |
| 工程文件 | 明确授权工程路径；会改文件的并行会话使用各自 worktree/副本，避免把“显示隔离”误当“文件互斥” |
| 剪贴板 | 仅在本会话内工作；预览默认不与人的系统剪贴板双向同步 |
| 链接打开与单实例 | 浏览器、文件管理器、`xdg-open` 等必须留在本会话；不能因为共享 profile、D-Bus 或默认应用转投人的桌面 |

**正式保证需要显示隔离和能力隔离一起成立。** 同 UID + 0700 目录只适合协议 POC，不能当作最终隔离交付；换 UID 本身也不会隔断宿主无认证的 loopback CDP。完整候选的 OS 边界如下：

- 每会话进程树共享自己的一组 mount/PID/network namespace，不同会话不共享。私有临时目录隔离 X11 pathname socket，network namespace 还隔离 Linux abstract Unix socket；只设 PrivateTmp 不够，见[官方 Unix socket 语义](<https://man7.org/linux/man-pages/man7/unix.7.html>)与[network namespace 文档](<https://man7.org/linux/man-pages/man7/network_namespaces.7.html>)。
- 应用只看授权工程路径和必要运行库；不挂入人的 runtime、D-Bus、X11 socket、密钥环或预打开的宿主连接 FD。单独开放已验证的 GPU render node，不给 uinput、物理输入、VT 或 KMS primary node。
- 独立网络栈仍要能访问网页：经受控出站通道/NAT 放行所需公网访问，阻断宿主地址和自动化控制端口。需要访问本机项目 HTTP 服务时，另经按会话授权的服务代理，不直接把宿主 loopback 整体打通；不能只开 PrivateNetwork 后就声称联网浏览已实现。
- 只有受限 broker/启动器能创建、连接和回收这些环境。它向 DSH 暴露按会话鉴权的窄入口，不向模型开放任意 systemctl、宿主 shell、全局 CUA 或人的 CDP。受控导出 socket 与内部 0700 runtime 分开；只有 broker 获得必要访问权限，不能为方便把运行目录改成 0777。
- 如果该 DSH 会话仍可通过 run_code/命令/文件写入工具任意执行宿主代码或改启动配置，OS 强隔离承诺就不成立。正式模式必须把这些写入/执行能力也限制到 worker/授权工程；这会改变现有权限工作流，需要作为部署方案一并确认，而非只写一句“禁止抢焦点”。

这是不用 VM 的本机进程隔离，不是已部署能力。若实际系统缺少所需 namespace/权限支持，正式隔离验收失败，不能静默降级为同 UID 裸进程。仍不承诺对共享内核、GPU 驱动漏洞或驱动重置实现 VM 级隔离。

## 进程与状态生命周期

- 复用 systemd 的每会话服务实例管理进程，不自研通用进程调度器。一个实例承载私有 D-Bus、headless Sway、worker、wayvnc 与应用，统一留在自己的 cgroup。服务名称和安装文件在落地阶段确定，本轮不新增 unit。
- 收到首次桌面任务才启动。Sway 用专用最小配置，不沿用人的自启脚本；让 worker 和应用从 compositor 子进程继承实际 WAYLAND_DISPLAY、SWAYSOCK、Xwayland DISPLAY。不能硬猜 socket 名，也要清除继承的 WAYLAND_SOCKET FD。
- 私有 socket 可达、窗口查询正常、至少一帧能回读、虚拟输入协议就绪后，才将该会话标为可操作。启动失败不放行输入，也不迁就到宿主环境。专用配置不启动 swayidle/自动关输出，确保无查看者时仍有可采集的虚拟 output。
- 人工接管是暂停 AI 写入，不是重开桌面；关闭预览不停止服务。服务重启产生新代次，使所有旧窗口句柄/排队输入失效。
- 主动关闭会话时先停输入，再正常保存/关闭应用与专用浏览器，最后回收服务。未保存的编辑器工作不能靠强杀“清理干净”；强制结束须明确提示数据丢失风险。
- 持久 profile 与工程文件不随进程回收删除；临时 socket/帧与持久凭据分开。只清理本实例拥有的进程和临时目录，不能用共享 browser state 去回收人的浏览器。

## 会话路由与失败保护

工具能力只需覆盖：启动应用、读取窗口与截图、提交一段有序输入、停止输入/会话。名称与具体 DSH 接口尚未定义，这里是能力设计，不冒充现有插件 API。

- 归属绑定取自 DSH 的当前会话，不接受模型任意指定另一个会话的 DISPLAY、socket 或控制地址。
- 每会话单写者/输入队列；不同会话并行，不设置全局输入锁。常驻工具进程每会话独立或显式传递上下文，不能在多会话共享进程里临时改全局 process.env 充当路由。
- 一次操作包含：确认会话代次与目标窗口 → 必要时只在后台桌面内聚焦 → 输入 → 回读截图或应用状态。输入成功回执不等于操作效果已验证。
- 窗口标识与 compositor 启动代次一起使用；重启后的旧窗口 ID、旧坐标不能继续执行。
- 第一版只设单一 headless output、scale 1；点击坐标以截图原图尺寸为准，不按网页预览缩放后的尺寸直接点击。改分辨率后必须重新观察。
- 超时、断连或紧急停止时释放本会话持有的键和鼠标按钮；若无法确认释放，销毁/重建该会话的虚拟输入连接或控制实例，不能改用宿主按键补救。恢复后先重新截图，不重放危险输入。
- compositor/VNC/浏览器不可用时明确报错并停止；**禁止退回主桌面、全局 CUA、默认 DISPLAY 或共享浏览器兜底**。
- 现有全局 CUA 与共享 ego 不作为这类会话的输入工具暴露。不能只新加一个“安全工具”，却让旧的抢焦点路径继续可用。

## 查看、人工登录和接管

截图直接返回到当前会话即可看窗口情况；连续画面复用 noVNC，不自研远程桌面前端。初版不需要桌面切换动画、透明效果、全局预览墙或自动弹窗。

[wayvnc v0.10.2 手册](<https://github.com/any1/wayvnc/blob/v0.10.2/wayvnc.scd>)已支持多个监听地址，以及 `unix`、`ws-unix` 等类型。控制实例使用私有 RFB socket 给 worker，私有 WebSocket socket 给人工接管代理；无需为了转换协议先加一整套 websockify 服务。

**只读不能只靠前端勾选。** 人打开纯预览时，按需启动第二个带 `--disable-input` 的 wayvnc 实例，只提供服务端禁输入的预览 socket。人工接管时，网关在撤销 AI 控制连接后，才允许接管页面连接可输入的控制实例；交还时断开人工控制连接，重新只读查看。这样复用现成功能，不自写 RFB 消息过滤器；额外采集开销仅在人查看时发生，须验收。

预览只经带会话鉴权的网关访问，不把无认证 VNC、WebSocket 或 CDP 暴露到局域网。网关必须校验会话归属与 WebSocket Origin，不能仅靠“监听 localhost”当鉴权；socket 权限、短期访问凭据、日志脱敏一并落实。

**认证方案明确选在边界上，而不是碰运气拼参数：**

- wayvnc 只监听本会话受权限保护的 Unix sockets，内层使用 RFB None；不配置可被误认为兼容的 RFB TLS，也不设任何 TCP/0.0.0.0 监听。这里的访问控制是 OS socket 权限与网关会话授权，不是公开无密码 VNC。
- 内部 worker 仅能访问自己的 RFB socket；noVNC 只通过鉴权网关访问自己会话的预览/接管 socket。浏览器无法直接连 Unix socket，网关不可省略。非回环网页访问必须经 HTTPS/WSS；本机 loopback 开发访问也仍需身份、归属与 Origin 校验。
- 这样既不要求 noVNC/vncdotool 支持 wayvnc 的内层强加密类型，也不为兼容而打开弱 DES 认证。只要存在绕过网关的网络监听、跨会话 socket 访问或授权失败，就停止接入。
- 必须跑实际握手与负向权限测试。若部署政策要求内层 RFB 也必须全程强加密，本方案的此项选择需重新选客户端，不能自动改成 relax_encryption。

原因：[所核 noVNC 实现](<https://github.com/novnc/noVNC/blob/e8b5024d4603587b29ffede4fbd28b1fa2939829/core/rfb.js>)与[NeatVNC 的安全类型选择](<https://github.com/any1/neatvnc/blob/175676b6f4505c8d51bfac9d1c7b75271f9e43a3/src/server.c#L295-L346>)并非所有 RSA-AES/VeNCrypt 变体互通。WebSocket 或 websockify 只解决传输，不会翻译不兼容的 RFB 认证。上述私有 socket + 外层鉴权是本提案选择，尚未实机验收。

[noVNC 官方 API](<https://novnc.com/noVNC/docs/API.html>)提供 `viewOnly`、`focusOnClick`、`resizeSession`。预览默认只看、不开自动焦点、不请求重设虚拟分辨率；不自动打开或激活人的标签。打开预览由人主动操作。客户端 viewOnly 只是交互模式，不冒充服务端安全边界。

人工接管按顺序进行：

1. 人主动点“接管”。
2. 后端停止该会话的 AI 输入、释放所有按键/按钮并撤销写入租约。
3. 允许人的远程键鼠输入，人在预览里登录、完成验证码或排查。
4. 人主动交还，前端恢复只读，AI 获取新截图后继续。

登录保存在 AI 专用浏览器 profile 中。不复制正在使用的浏览器目录、不同时打开同一个 profile，也不依靠共享 9224 来“方便复用登录态”。需要真人验证时停下来让人处理，不绕过验证。

## 应用兼容性与明确限制

- 已打开在人的 Wayland compositor 中的任意窗口，没有通用的跨 compositor 无缝迁移/后台注入方案。Wayland 客户端的显示连接与 socket 选择见[官方客户端 API](<https://wayland.freedesktop.org/docs/html/apb.html>)。默认在后台会话重开应用；不允许重开时改走应用自己的 API，并单独评估支持范围。
- 应用专用接口优先：浏览器 CDP、编辑器脚本/API 可以减少坐标操作；没有可靠专用接口时才走后台桌面键鼠。
- 原生 Wayland 应用在 headless Sway 中运行；X11/Wine 应用走该会话的 Xwayland。Xwayland 的 DISPLAY 由实际启动结果取得，不硬编码。
- UE/Vulkan 保留 GPU render node 使用能力，不默认强制 pixman/软件渲染。但 RX 7900 GRE、当前 Mesa/wlroots、UE 菜单/弹窗、图像采集与 GPU 资源竞争必须实测，不能从“有 GPU”推导出“UE 已可用”。
- 普通桌面绝对坐标点击不证明 UE 视口的相对鼠标/指针锁定可用。若 RFB 路径不足，才补接私有 compositor 的 virtual-pointer 相对位移能力；它仍不得经过宿主 uinput。该项未验收前，不将游戏/编辑器视口盖章为完整兼容。
- VR 头显接管、独占物理显示、音视频转发、打印、任意 USB 设备和多显示器不列入第一版；它们不是完成普通窗口后台输入与查看的前提。
- 另开桌面不等于另开应用账户：QQ 等程序的账号互踢/授权限制、同一 UE 工程多实例写入冲突，都要独立处理。
- 人与 AI 仍共享本机 CPU/GPU/磁盘；此设计保证控制通道分离，不保证共享硬件零负载影响或驱动故障互不影响。

## 为什么不以其他方案为主

| 方案 | 适用边界 | 决定 |
|---|---|---|
| niri 工作区/防激活规则 | 摆放窗口、降低意外切焦点 | 不是后台键鼠隔离基础 |
| 同屏嵌套 compositor | 把 AI 桌面装进一个宿主窗口 | 本需求不需要这个宿主窗口，优先 headless，减少父窗口激活通道 |
| Chromium headless + 专用 profile | 纯网页任务 | 是可用的浏览器专项路径，但不能满足所有 GUI 窗口 |
| Xpra/Xvfb + 独立 DISPLAY | 以 X11 应用为主的完整后台会话 | 保留为主方案 POC 失败时的备选；原生 Wayland、GPU/Vulkan 兼容性不是自动具备 |
| 另一 VT、物理 seat 或虚拟机 | 另一个本地登录桌面/强隔离环境 | 切 VT 会扰当前工作；虚拟机被明确排除 |

## 本机已有与需要补齐

只读包查询确认：已有 niri 26.04、Xvfb 21.1.25、Xwayland 24.1.14、wtype 0.4、grim 1.5、wl-clipboard 2.3、D-Bus 1.16。

当前未装 Sway、wayvnc、Xpra、Weston。当前本地 Arch 软件源数据库提供 Sway 1.12 与 wayvnc 0.10.2。noVNC 和 vncdotool 的获取、版本固定与安装形式尚未实施；不能把源代码里存在功能写成“本机现成就能用”。

本机现有 ego 的 [浏览器启动逻辑](</home/sx/.local/share/ego-lite-runtime/runtime/ego-linux/src/chrome.mjs#L748-L758>)会优先复用外部 CDP 或旧 browser state，先于启动参数；[共享包装器](</home/sx/.local/share/ego-lite-runtime/bin/ego-shared-bili.mjs#L16-L34>)也会自动探测 9224。因此**只改 HEADLESS/DISPLAY 不会把当前共享浏览器迁走**。

即使采用 Xvfb 备选，[现有兜底](</home/sx/.local/share/ego-lite-runtime/runtime/ego-linux/src/chrome.mjs#L579-L593>)也会寻找并复用一个已有 Xvfb；“自动兜底”不等于“每会话独立”。浏览器的 [profile 和 state 路径](</home/sx/.local/share/ego-lite-runtime/runtime/ego-linux/src/paths.mjs#L7-L20>)都必须会话化。

## 落地顺序与验收门槛

本轮不动系统、不安装依赖、不重启现有服务。得到方案确认后按依赖顺序推进，不一次性改完再猜哪里坏。

1. 在独立测试运行身份/目录中启动一个 headless Sway，核验没有物理输出和输入设备接管；让普通文本应用接受虚拟键鼠并截图回读。
2. 加入 wayvnc 与控制客户端，验证中文、组合键、右键菜单、拖拽、滚轮、按键释放和无查看者时持续操作。
3. 在同一后台会话测试独立浏览器，以及一个 Xwayland 应用；再单独验证 UE/Vulkan 和菜单弹窗。未通过前不替换原有工作流。
4. 同时运行两个后台会话，验证路由、D-Bus、浏览器 state/profile 和输入互不串扰；杀掉一个会话后另一个与人的桌面继续正常。
5. 接入 DSH 的会话路由、截图返回和只读/人工接管预览；只在 dev 工作树与 3081 验证，不把 3080 当实验台。
6. 验收通过后再单独确认生产切换。用新服务实例承载，不靠重启当前全局 CUA 或主浏览器来试错。

| 验收场景 | 必须观察到的结果 |
|---|---|
| 人在编辑器持续打字，AI 连续执行至少 100 次键鼠/开窗操作 | 人的前台窗口 ID、工作区、标签、真实指针和文本输入目标不因 AI 改变；前后截图相同不算足够，需覆盖操作过程 |
| 后台弹窗、模态对话框、浏览器新标签与网页聚焦 | 只在 AI 桌面内变化；截图能看见且能继续操作 |
| 中文、Ctrl/Shift/Alt、拖拽、滚轮 | 后台应用的内容/状态回读正确，人的输入与剪贴板未改变 |
| AI 操作未被当前虚拟屏幕显示的窗口 | 可在自己的桌面切换到该窗口查看/操作，人的桌面不切换 |
| 两个会话同时输入 | 各自目标正确，不共用浏览器或按键状态 |
| compositor、VNC 或浏览器崩溃，接管、停止、断连 | 无按键卡住；旧请求失效；没有主桌面 fallback |
| 错误会话 ID、旧窗口 ID、旧尺寸截图坐标 | 后端拒绝，不能转投其他会话/人的窗口 |
| 未授权访问预览和控制端点 | 拒绝连接；不能借更换路径/Origin 访问其他会话；实际 RFB security type 与设计一致 |
| 跨会话/宿主访问负向测试 | A 不能连接 B 或人的显示、总线、X11 pathname/abstract socket、CDP/CUA；网络浏览仍可用；仅环境变量不同不算通过 |
| 只读客户端绕过前端 viewOnly 主动发送键鼠消息 | 服务端禁输入，不改变后台窗口；未获接管租约不能连接可输入端点 |
| 人主动登录并关闭/重新打开预览 | 登录能在该 AI profile 中保存，预览不开也能继续自动化 |

> [!WARNING]
> 以上是验收标准，不是已经通过的测试结果。当前已实测的是旧配置校验、现有配置、包信息、控制入口和浏览器连接身份；完整方案仍须按上表验证。

## 可复核的现场证据

[旧核心规则样本](</tmp/focus-kdl-check-1793853075189/valid-core.kdl>)与[正确 debug 层级样本](</tmp/focus-kdl-check-1793853075189/proper-debug-strict.kdl>)保留在临时目录。只读复核：

```bash
niri --version
niri validate -c /tmp/focus-kdl-check-1793853075189/valid-core.kdl
niri validate -c /tmp/focus-kdl-check-1793853075189/proper-debug-strict.kdl
```

预期第二条退出码为 1 并报告不认识 on-xdg-activate；第三条成功。未编辑人的 niri 配置、现有浏览器、CUA 服务或生产 DSH。

代码图服务本轮连接失败，网络搜索服务返回余额不足；没有据此作“不存在”的结论。使用实际文件、官方页面/源码和本机只读命令交叉核验。
