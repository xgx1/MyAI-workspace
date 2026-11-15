# XWayland 窗口可见但不激活：本机版本核对

调研日期：2026-11-05。本文只做文档、源码和命令帮助的只读核查，没有移动任何实际窗口，没有发送键鼠，也没有改桌面或服务配置。

## 已确认的版本与更正

- 本机软件包：niri 26.04-1（运行版本 8ed0da4）、xwayland-satellite 0.8.3-1、Xwayland 24.1.14-1。
- niri fork HEAD 是 4c733af9；agent-desktop fork HEAD 是 984bf5f9，后者已经包含 scoped compositor 接线。先前“agent-desktop 接线还是空的”的说法不正确；这次未重跑它的测试，因此不声称已完成产品验收。
- “xdotool windowactivate 报错，所以窗口只能通过 focus-window 送到人眼前”不成立。X11 激活、Wayland 键盘焦点、窗口可见性/堆叠是不同机制。

## 先利用现成能力，不改 XWayland

niri 26.04 自带三组参数，已核实本机 CLI 的 --help 和同版本源码：

~~~bash
# 以下只是方案示例，本轮没有执行。WIN 是 niri 窗口 ID，不是 XID。
niri msg action move-window-to-floating --id "$WIN"
niri msg action move-window-to-workspace --window-id "$WIN" --focus false "$WORKSPACE"
niri msg action move-floating-window --id "$WIN" -x 100 -y 200
~~~

这里的 WORKSPACE 必须是用户当前工作区的有效索引/名称；不能把内部 workspace_id 无条件当成 CLI 索引。需另外按显示器和窗口尺寸挑不会挡住人输入的位置。原应用仍连接原 XWayland、使用原项目；没有复制数据、重启实例或迁移进程。

一手依据：

- [niri v26.04 浮窗说明](https://github.com/niri-wm/niri/blob/v26.04/docs/wiki/Floating-Windows.md)：浮窗在平铺窗口上方；每个工作区/显示器各有浮动布局，和切换焦点不是同一个操作。
- [niri v26.04 IPC 定义](https://github.com/niri-wm/niri/blob/v26.04/niri-ipc/src/lib.rs#L526-L543)：MoveWindowToWorkspace 带 window_id 和 focus。
- 本地 [动作执行路径](</home/sx/projects/niri/src/input/mod.rs#L1326-L1379>)：focus=false 映射到 ActivateWindow::No；按 ID 移动不需要先把目标聚焦。
- 本地 [浮动切换](</home/sx/projects/niri/src/layout/workspace.rs#L1388-L1446>)：target_is_active 由目标原本是否是活动窗口决定，不是对任意 --id 强制激活。
- 本地 [工作区移动](</home/sx/projects/niri/src/layout/monitor.rs#L853-L908>)：移动时保留 is_floating，并传 ActivateWindow::No。
- [上游 issue #1805](https://github.com/niri-wm/niri/issues/1805) 曾报告 move-column 的浮窗 focus=false 被忽略；维护者确认修复于 #1820。不能拿旧故障代表 26.04，也不能混用 move-column 和按 ID 的 move-window。

结论等级：**已有文档和源码依据的最小路线，尚未做本轮端到端验收**。原先只测试 focus-window，没有覆盖这条路径。

## 必须处理的边界

- 本机 [配置第32行](</home/sx/.config/niri/config.kdl#L31-L32>) 启用了 focus-follows-mouse。这会在鼠标进入目标窗口时尝试改变焦点；只保证一次移动动作的 focus=false，不等于永久禁止目标抢焦点。
- [源码焦点跟随路径](</home/sx/projects/niri/src/niri.rs#L6239-L6296>) 调用 activate_window_without_raising，进一步证明 raising 和 activation 可分离。若要求 AI 窗口永远不能被人的鼠标误触，需要按归属过滤人的命中/激活，或采用不接收输入的镜像，而不是定时抢回焦点。
- open-focused false 只管窗口初次打开。[26.04 官方说明](https://github.com/niri-wm/niri/blob/v26.04/docs/wiki/Configuration%3A-Window-Rules.md#open-focused) 和 [本地规则定义](</home/sx/projects/niri/niri-config/src/window_rule.rs#L18-L36>) 均表明它是初始规则，不能冒充永久激活防火墙。
- 最新官网有 on-xdg-activate，但本地 26.04 的 WindowRule 没有该字段；不能把新文档配置直接拷进当前桌面。
- 浮窗在平铺窗口之上，不等于永远在所有浮窗、全屏或 overlay 之上。若人的当前窗口也是浮窗，要额外控制堆叠；不能用临时 focus 再 restore，后者已经违反“不抢前台”。
- 用户没要求看时，AI 窗口仍应留在 AI 工作区；显示必须是显式 peek，不应自动搬过来挡人。移动前保存原工作区、浮动状态、位置和尺寸，关闭预览时恢复。

## 更严格的只看方案：不接收输入的画面镜像

若“看见”不要求把原始可交互窗口搬来，XWayland 窗口可以保持原位，把原窗口捕获的画面显示为只读小窗或 DSH 内的预览。它是同一运行实例的画面，不是复制工程/浏览器数据。

要在桌面悬浮且从机制上不抢键鼠，可采用：

- layer-shell 层 surface 的 keyboard_interactivity=none：协议写明 compositor should never assign it the keyboard focus。
- wl_surface.set_input_region 设置**空 wl_region**并 commit，使指针/触屏事件穿过；注意 NULL 表示无限区域，不能用 NULL 冒充空区域。
- exclusive_zone=0，不挤压人的窗口布局。

一手协议：[wlr-layer-shell XML](https://gitlab.freedesktop.org/wlroots/wlr-protocols/-/blob/master/unstable/wlr-layer-shell-unstable-v1.xml)、[Wayland wl_surface.set_input_region](https://gitlab.freedesktop.org/wayland/wayland/-/blob/main/protocol/wayland.xml)。这只是有协议依据的设计，没有实现 viewer，也没有在本轮实现录屏/视频。

本机已存在 [pin 浮窗规则](</home/sx/.config/niri/config.kdl#L126-L132>)，足以旁证“可见且初次不聚焦”不是系统做不到。现有 [pin 脚本](</home/sx/.local/bin/pin>) 从剪贴板取图，会触及剪贴板，且普通 xdg 小窗仍可能被鼠标聚焦；它不能直接作为严格方案。

## 不另写已有后端

agent-desktop 已有 [XTEST sink](</home/sx/projects/agent-desktop/crates/linux/src/input/x11/xtest_sink.rs>)、[串行 worker](</home/sx/projects/agent-desktop/crates/linux/src/input/x11/worker.rs>) 和 [scoped 窗口类型](</home/sx/projects/agent-desktop/crates/linux/src/input/wayland/scoped/scoped_window.rs>)。后续应该复用已有输入/清理机制，补齐 XWayland 的目标关联、显示策略和隔离，不再根据旧报告从零估算“5模块600–900行”。

## 最小验收提议（未执行）

在嵌套 niri，使用与用户一致的 focus-follows-mouse 设置：原生 Wayland 人窗口 A 保持输入，XWayland 下 Unity B 在另工作区。按 ID 把 B 浮动并 focus=false 搬入 A 工作区；分别测试普通平铺人窗口、浮窗人窗口和全屏情形。记录 A 的窗口ID、工作区、真实指针、剪贴板，以及 B 位置/像素；任何瞬间聚焦 B 都不能用“最后恢复 A”算通过。再单独测试鼠标跨过 B、Unity 自发弹窗和激活请求。显示验收和后台输入验收必须分开，不能用一项通过代替另一项。
