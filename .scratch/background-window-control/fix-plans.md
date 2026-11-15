# 未通过项的方案（含根因）

测试结果见 [real-app-test-results.md](real-app-test-results.md)。这里只写"为什么不通、怎么让它通、代价是什么"。

四项分头查完了：截图缺陷有确定根因，浏览器有确定通道，UE 其实已经能跑，Unity 只有一部分能走 Wayland。

---

## 1. scoped 截图"第一次失败"——根因已定，不是渲染器没就绪

**根因：`Handled` 在 PNG 落盘之前就回给了客户端。**

实测时序（debug 构建，真实窗口内容）：

| 时刻 | 事件 |
|---|---|
| +0.34 ms | 客户端收到 `{"Ok":"Handled"}` |
| +0.35 ms | idle 闭包才进入 |
| +7.2 ms | 渲染 + 读回完成 |
| +157 ms | 编码线程写盘完成 |

纯色小图 19–22 ms，真实内容 148–181 ms，紧接拖拽后一次 277 ms。客户端拿到 reply 时文件必然还不存在。

**"第二次就成功"也是错的**：harness 的 `shot()` 四次重试共用同一路径，第二次的 `[ -s "$path" ]` 检到的是**第一次写的那张**。也就是说这条重试逻辑一直读的是上一次的 PNG，第一次从来没有失败过。

**修法（三处，最小改动）**：

1. `src/niri.rs`：`save_screenshot` 与 `screenshot_window` 各加一个 `on_done: Option<Sender<Result<Option<PathBuf>, String>>>`，在编码线程的三个出口（编码失败 / 写盘失败 / 成功）send；5 个既有调用点传 `None`。
2. `src/ipc/server.rs:390-418`：分支外建 `bounded(1)` 通道，sender 移进 idle 闭包，`insert_idle` 之后 `recv().await`——拿到成功才回 `Handled`，拿到失败回 `Err`，sender 被 drop（含线程 panic）也回 `Err`。
3. 顺带把两处静默早退改成显式失败：窗口没找到、`with_primary_renderer` 返回 `None`。

代价：reply 从 ~0.5 ms 变成 20–180 ms。客户端 deadline 是秒级，无影响。修好后 harness 的 4 次重试可以退回 1 次。

> 工作区当前留了 `TEMP-DIAG` 日志（`src/ipc/server.rs`、`src/niri.rs`），是排查用的，实施时要换成正式实现或删掉。

---

## 2. 浏览器：走 CDP 挂到日常浏览器，不要第二个实例、不要 BrowserContext

### 现状（读代码与实测）

- 本机日常浏览器是 Helium，pid 30692，profile `~/.config/net.imput.helium`，命令行已带 `--remote-debugging-port=9222`；`9224` 是 `socat` 把 9222 转出来的（ego 挂的就是同一个进程）。**所以"实时共用同一份数据"这条路今天就能走**。
- DSH 自带的 `browser-use` 只是互斥注册器（`packages/browser-use/browser-use/src/index.ts:16-46`），没有任何浏览器操作语义；三个 provider 里 launch 模式起隔离 Chromium、Stagehand 自己 mkdtemp、Playwright attach 到 9222 时**会用 `Page.bringToFront`/不带 background 的 createTarget 抢前台**。
- ego 这条线已经把"不抢前台"补上了：`transport.mjs:216-238` 丢弃 `Target.activateTarget`，`tabs.mjs:102`/`task-spaces.mjs:471` 建 tab 带 `background: true`。

### 三档机制

| 档 | 做法 | 用户看到 | 现状 |
|---|---|---|---|
| A | default context + `createTarget{background:true}` + 抑制 activateTarget | 多出几个 tab，焦点不动 | ego 已实现 |
| B | 再加 `hidden:true` | 标签栏看不到这些 tab | CDP 支持，但 hidden 的寿命=创建它的 CDP session 寿命，需要**常驻 CDP 持有者** |
| C | `newWindow:true` | 多一个后台窗口 | 不可用：后台窗口不渲染，点选/取图都失效 |

**绝对不要**：第二个实例写同一个 user-data-dir（Chromium profile 锁 + LevelDB 损坏）；`Target.createBrowserContext`（cookie 是创建时点的拷贝，违反"实时共用"，且必然独立窗口）。

### 落地要改的地方

1. **composition 收敛成一条线**（零代码）：`~/.dsh/profiles/web/cordis.patch.yml` 里 ops preset 同时挂了 playwright(attach 9222) 和 ego——这是最差组合，playwright 会抢前台。要么只留 ego，要么把 playwright 换成 launch 模式。
2. **每会话一个 task space**：`dsh-ego-browser/lib/index.js:2880` 的 `DEFAULT_SPACE = "dsh-agent"` 是常量，所有会话挤同一个空间；按执行中的 agent 派生。前提未验证：插件 handler 能否拿到 `exec.agent`。
3. **要 B 档才写新包**：`deepseek-harness-dev` 里新增 `packages/experimental/browser-use-cdp-session/`，每个 Agent 一条 CDP 连接 + 一个 hidden target，工具全走 `Target.attachToTarget{flatten:true}`，永不发 `activateTarget`/`bringToFront`。

### 必须实测的（别当结论）

- `createTarget{background:true}` 是否真的不动前台（ego 补丁的核心假设没有验收记录）；
- `hidden:true` 在 Chromium 156 上是否被接受、是否正常渲染、断开创建者后是否立即消失；
- 两个会话并发时空间会不会串；
- `Emulation.setFocusEmulationEnabled` 能否让后台 tab 正常渲染与响应输入（我们的 testpage 实验里 CDP 输入是有效的，但那是前台 tab）。

---

## 3. UE：不是不能跑，是当时赶上"重编译后 6 秒冷启动"

**根因**：16:07:50 VulkanRHI 重链接完成，16:07:56 就启动了编辑器；随后两段各 160 s 的无日志阻塞是首次启动的冷成本，被 5 分钟超时杀在 72%。同一套件今天复跑：**窗口 5 s 出现，20 s 出编辑器界面，30 s 完整可交互，119.7 FPS**，`/Engine/Maps/Entry` 正常加载。

**结论：嵌套 winit 后端能力充足，"换后端/虚拟输出"这条否掉。**

**下一轮验收判据（不要再拿日志当就绪判据——20 s 后日志就冻住了，界面却已好）**：

1. 窗口 `app_id=UnrealEditor` ≤ 15 s；
2. scoped 截图里能看到菜单栏/视口/大纲 ≤ 180 s（冷启动首次给 300 s）；
3. 注入 `W` 按住 0.5 s → 视口相机位移 → 前后截图 hash 不同；
4. 焦点、剪贴板、`bind-fired` 全不变；
5. FPS ≥ 84（基线 119.7 的 70%）；
6. 收尾按精确路径 pkill，只留用户自己的 UE。

---

## 4. Unity：编辑器只有 X11；**能走纯 Wayland 的是 player，不是编辑器**

### 实测与证据

- 三个已装编辑器的动态依赖里 wayland 数量 **0/0/0**；`nm -D` 里 `wl_*` = 0、`egl*` = 0，只有 `X*/glX*/gdk_x11*`。渲染只能画在 X11 drawable 上。
- `-force-wayland` 这个字符串在编辑器二进制里 **不存在**（0 次），只出现在内嵌 SDL2（player 运行时）里；`SDL Wayland video driver`、`SDL_VIDEO_WAYLAND_*`、`VK_KHR_wayland_surface` 都是 player 侧。
- 官方系统需求页：编辑器写 "X11 or Wayland windowing system"（= 允许跑在 Wayland 会话里，经 XWayland），紧跟的注释才是 "Wayland support for Desktop Linux is currently in experimental stage… to run the **Linux player** in Native Wayland mode use `-force-wayland`"。Unity 讨论区被采纳答案（2026-01）也是"编辑器仍然走 XWayland，没听说要原生"。
- **实测**（本机，嵌套 niri）：`GDK_BACKEND=wayland` + `DISPLAY=:1` 起 6000.7.0b5，窗口照常出现在 **X11 侧**（`app_id=Unity-6000.7.0b5`，由 xwayland-satellite 代报），编辑器自己日志写 `Window Protocol: Wayland (XWayland)`——那是它识别会话，不是 surface 类型。同一环境里 `GDK_BACKEND=wayland zenity` 立刻出 Wayland 窗口，说明不是环境问题。
- 只设 `GDK_BACKEND=wayland`、不给 `DISPLAY`：Unity 直接 `Gtk-WARNING: cannot open display` 起不来——**说明它自己把 GDK 钉在 x11**（强推断，验证方法：起编辑器后 `tr '\0' '\n' < /proc/<pid>/environ | grep GDK_BACKEND`）。

### 所以"强制纯 Wayland"能做的只有一半

- **Unity 打包出来的游戏（player）**：可以强制纯 Wayland 跑（`-force-wayland`，或 `SDL_VIDEODRIVER=wayland`）。这类进程是**真正的 Wayland 客户端**，我们的 `agent-0` 座席对它有效——这才是 Unity 生态里能纳入"后台控制"的部分。
- **Unity 编辑器**：没有纯 Wayland 路径，只能 X11。

### Unity 编辑器要控，只有三条路（按推荐排序）

1. **用 Unity 自己的自动化面**（不碰窗口）：`-batchmode -nographics -executeMethod` / `-runTests`，或者本机已装好的 Unity MCP（桥在 127.0.0.1:6400，48 个工具，能建对象、改组件、读控制台、跑 C#）。**这批能力是"AI 能真的干活"的最高性价比**，只是看不见 UI。
2. **私有 X 显示**：`Xvfb :99` + Unity 连它 + XTest 注入，截图用 `xwd`/ffmpeg。与用户桌面零交集，但无 GPU（llvmpipe），编辑器会慢到只够点测。
3. **XWayland 全局注入**（`xdotool`/XTEST）：能点菜单、看 Scene 视图，但**注入是全局的，必然抢焦点**，与"不动前台"直接冲突——只在你明确同意"这条允许打扰"时才有意义。

---

## 5. 建议执行顺序

1. **修截图回执**（1 处根因 + 3 处改动），顺手把 harness 的重试降为 1 次——它现在会读到旧 PNG，等于污染所有验收证据。
2. **浏览器收敛**：composition 只留 ego（或 playwright 改 launch），并把"9222 是日常浏览器"这条写进配置注释；B 档新包等第 1、2 步稳定后再做。
3. **UE 按新判据补一轮验收**（视觉/相机位移证据）。
4. **Unity 先接自动化面**（MCP/batchmode）；player 的 Wayland 通道等有构建产物再验。
