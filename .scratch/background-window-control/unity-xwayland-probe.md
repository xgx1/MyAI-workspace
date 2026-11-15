# Unity（X11/XWayland）后台注入：实测结论

日期 2026-11-05。两个独立实验合并：**A** 在用户真实 niri 会话里跑 Unity 2022.3.62f3（`xwayland-satellite :0`）；**B** 在嵌套 niri 实例里跑 Unity 6000.7.0b5（`xwayland-satellite :2`），同实例另开一个 Wayland 原生 GTK 窗口当作"人正在用的窗口"的替身。

> **后续复核更正（2026-11-05）**：下文保留历史实验。旧版把 `windowactivate` 失败推成“看见窗口必定抢焦点”，推论不成立；本机 niri 有按 ID、`focus=false` 移窗及浮动布局。XTEST 的旧观测也不能证明所有 XWayland 路线必然移动真实光标。新核查见 [源码核对记录](<xwayland-local-source-verification.md>)，新路线尚待端到端验收。

## 一句话结论

Unity 编辑器（本次三个已装版本只有 X11 路线）经 XWayland **可以后台驱动**：历史实验取得截图并投递了键鼠，且部分键盘实验无需改变 niri 焦点。但默认 X 输入路径有焦点共享风险；“显示窗口”和“激活窗口”必须分开处理，不能据此声称显示必然抢焦点。

## 能力矩阵

| 能力 | 结论 | 证据 |
|---|---|---|
| 截图（不聚焦） | ✅ | 真实会话里 niri 焦点在 Helium(id 8) 时 `import -window 20971990 → /tmp/u1.png` 得 1277×1377 完整编辑器画面 |
| 鼠标 | ✅ | 真实会话：`xdotool mousemove --window 20971990 110 851; click 1` 把底部面板从 Project 切到 Console（AE diff 11667/1.76M）；嵌套：点 File 菜单弹出完整下拉 |
| 键盘（XTEST） | ✅ | 真实会话：niri 焦点=Unity(49) 时 `xdotool key ctrl+p` 真进 Play 模式（工具栏 ▶ 高亮、Game 视图出画面）；嵌套：同法进/出 Play，`unity.log` 的 `Reloading assemblies for play mode.` 计数 1→2→3 |
| 键盘（XSendEvent） | ⚠️ 不一致 | 嵌套 Unity 6000.7 接受 `xdotool key --window <xid> b`（Hierarchy 搜索框 `Quiet1`→`Quiet1b`）；真实会话 Unity 2022.3 的 `key --window ctrl+k` 像素差 0。**产品按 XTest 做，不要依赖 SendEvent** |
| 键盘不抢人焦点 | ✅ | 真实会话复现：niri 焦点锁在 Helium(8)，`xdotool windowfocus <zenity X11 xid>` + `xdotool type "xyz123"` → 输入框里真出现 `xyz123`，`niri msg focused-window` 全程 8 helium。嵌套同结论：焦点锁在 textwin(id 5)，Unity 进 Play 而 textwin 的 GTK Entry 收到 `text=` 计数 0→0 |
| EWMH 激活（`windowactivate`） | 该工具路径失败 | `XGetWindowProperty[_NET_ACTIVE_WINDOW] failed (code=1)`。这只证明该路径没成功，不证明只能 `focus-window`；niri 的按 ID、`focus=false` 移窗/浮动布局是另一路径，本轮研究已有源码依据，尚待端到端验收。 |
| 截图（合成器侧） | ✅ | 嵌套：`grim` → 1269×1370；我们 fork 的 `scoped-shot <wid>` → 875×1338（含 25px satellite 标题栏，不碰剪贴板） |
| `import -window root` / `xwd` | ❌ | IM6 参数解析报 `missing an image filename`；`xwd` 未装。抓整屏用 ffmpeg `-f x11grab` |

## 旧实验默认输入路径的边界（不代表所有 XWayland 方案）

1. **当前默认 core master pair 的 X 焦点是共享状态**。`XSetInputFocus` 可能把焦点从另一个 XWayland 应用挪走；仅保存/恢复不能隔离注入期间人的输入。XI2 多主设备、独立 XWayland 实例是不同候选，需要另外验证，不能笼统断言所有 X server 都只有一份键盘焦点。
2. **默认鼠标路径有联动风险，尚不能下“必然可见”的普遍结论**。历史实验记录 `mousemove 400,400` 被回写成 `125,524`；这首先是 X 坐标回写观测，不能单独证明人的真实 Wayland 指针被移动。后续应同时测真实 seat 指针、X 指针、命中窗口及焦点；独立设备/实例路线不能在未测前排除。
3. **启动应用会抢焦点**。Unity 弹出默认拿 niri 焦点 → 必须配 window-rule `match app-id="^Unity-" { open-focused false; }`（harness 的 `poc.kdl` 已有同类规则）。

## 坐标与 id 换算（产品里最容易踩）

- 两个坐标系：**X root** 与 **Wayland 输出**。嵌套实例里 X root 是 1269×1404，输出是 1269×1370（root 高 34px，y>1370 不可见）。
- 注入一律用 **X root 坐标**，与 niri 布局无关：X 客户端在 root 里位于 `(0,0)`，尺寸 875×1313，所以"客户端内 (x,y)"就是"root (x,y)"。要把位置映射到 Wayland 截图才需换算：嵌套里 `screen = root + (16,41)`（模板匹配 err=0 验证过，其中 25px 是 satellite 画的标题栏）。
- X display 号要**探测不要写死**：satellite 的 X11 socket 懒启动，死掉的实例会留下 `X1` 假 socket，嵌套路子里真号是 `:2`。
- 坑：`niri msg -j windows` 对 X11 窗口报的 `pid` 是 **xwayland-satellite 的 pid**，不是应用 pid → 进程↔窗口只能用 `xdotool getwindowpid`（读 `_NET_WM_PID`）。
- 坑：Unity 的辅助窗口（10×10、200×200 asset import worker）都躺在 root `(0,0)`，枚举必须 `--onlyvisible` + 尺寸筛。
- 坑：隐藏/被遮挡的 GL 窗口抓图会拿到**旧帧**（刚打完字抓图还是旧内容，约 1s 后才有）→ 产品要等 damage/重绘或做像素稳定检测。
- 坑：Unity 进出 Play 模式会触发域重载，之后约 4s 内的按键被丢 → 注入要按"应用忙不忙"重试，不能靠固定 sleep。

## 产品化：agent-desktop 的 X11 后端最小模块

1. X 连接：`XOpenDisplay`/`xcb_connect` 到 satellite 的 `:N`（探测）。
2. 窗口枚举/匹配：`XQueryTree` + `WM_CLASS`/`WM_NAME`/`_NET_WM_PID`，过滤 `IsViewable` + 尺寸；不要用合成器的 pid。
3. XTEST 注入：`XTestFakeKeyEvent/ButtonEvent/MotionEvent` + `XKeysymToKeycode` + 修饰键合成（`xdotool type` 的全部逻辑）。
4. 焦点策略：读 X focus → `XSetInputFocus` → 注入 → 恢复；进程内串行化。
5. 截图：`XGetImage(window)` + 等 damage（否则旧帧）；要含装饰就走 niri scoped 截图（不要用会克隆 clipboard 的 legacy 截图）。

以上为历史模块草案，不是新的实现量承诺。后续查实 agent-desktop 已有 XTEST sink、worker，以及提交 984bf5f9 的 scoped 接线；应先复用现有后端，不能照旧草案从零再写。焦点恢复也不能替代真正的输入隔离。

## 与既有结论的关系

- 通道分流补一条：**Chromium/Electron/Helium → CDP**；**Wayland 原生工具包 → agent seat（niri fork 的 agent-0）**；**X11-only 应用（Unity 编辑器）→ XWayland + XTEST**。三条通道互不替代。
- 本实验没有在用户真实会话里触发任何 Unity 之外的窗口行为：Unity 实例用 `systemd-run --user --unit=unity-probe` 启动、测完 `systemctl --user stop unity-probe` 结束；zenity 代理测完 `pkill`；结束时 `ps` 只剩用户自己的 `xwayland-satellite :0`，`/tmp/.X11-unix/` 只剩 `X0`，niri 焦点回到 Helium(8)。
