# UE 5.8 在嵌套 niri 里卡启动画面：根因与"可被 AI 控制 + 可验收"方案

- 诊断轮日期：2026-11-05
- 被测：`/home/sx/projects/unrealengine/ue5.8/Engine/Binaries/Linux/UnrealEditor`（5.8.2，源码检出含"强制 Wayland"补丁）
- 最小工程：`/tmp/ue-probe2/Probe.uproject`（EngineAssociation 5.8；`EditorStartupMap=/Engine/Maps/Entry`）
- 隔离：嵌套 niri（`/home/sx/projects/niri/target/debug/niri -c /tmp/ue-probe2/poc.kdl`，winit 后端，独立 socket）
- 用户桌面上的 UE6（PID 33710，`/home/sx/projects/template/unreal/pc-game/PCGame.uproject`）全程未被触碰

## 1. 结论

1. **不是嵌套合成器 GPU 能力不足。** 同一个嵌套实例里，UE 5.8 编辑器出图并稳定 **119.7 FPS / 8.4 ms**（§2.3）。
2. **不是工程/资产缺失。** `/Engine/Maps/Entry` 正常打开：截图里大纲有 `Entry (世界)` + `PlayerStart`，视口画出网格与 actor（§2.3）。
3. **不是等网络/许可证/shader 卡死。** TC-09 全程 623 行日志里 error = 0，warning 只有 1 条无关的 `Zen named event`。
4. **真因（高置信）：那次跑的是"刚重编译完 6 秒的引擎"的首次启动。** 当日 15:16:22 改了 `LinuxPlatformApplicationMisc.cpp`（强制 Wayland），15:17:45 重链接 `ApplicationCore`，**16:07:50 重链接 `VulkanRHI`**，而 TC-09 的编辑器 **16:07:56 启动**（重建后 6 秒）。启动过程在"插件模块加载"阶段出现 **163.6 s + 159.2 s** 两段无日志阻塞：进程一直活着（16:10:50 还打了两行日志），没有 error，是被 5 分钟的超时提前杀掉。这是冷启动成本（首次运行这批新二进制 + 首次 PSO/shader 相关工作 + 当时机器同时在跑测试轮/VM），不是挂死。
5. **同一套件今天复跑（18:32 / 18:36）不再复现**：窗口 **< 5 s** 出现，主界面 **17–20 s**，30 s 时界面完整可交互。→ "让 UE 可被 AI 控制"这条路在嵌套环境里本来就走得通。

## 2. 证据

### 2.1 把"72% / Loading Default Modules for Plugin…"坐实到代码

`Engine/Source/Runtime/Projects/Private/PluginManager.cpp`：

- `2848` `bool FPluginManager::LoadModulesForEnabledPlugins(const ELoadingPhase::Type LoadingPhase)`
- `2854` `FScopedSlowTask SlowTask((float)AllPlugins.Num(), "Loading Plugin Modules for Phase {0}")`
- `2869` `FText::Format(LOCTEXT("LoadingModulesForPlugin", "Loading {0} Modules for Plugin: {1}"), <phase>, <plugin>)`
- `2875` `SlowTask.EnterProgressFrame((float)NumProcessedSinceProgress, Message)` ← **百分比 = 已处理插件数 / AllPlugins.Num()**
- `2877` `if (!TryLoadModulesForPlugin(Plugin.Get(), LoadingPhase))`

所以"72% 卡在 Loading Default Modules for Plugin…" = **某**一个插件的 `LoadLibrary` + `StartupModule()` 一直没返回；进度条按插件计数，单个插件慢就把百分比钉住。这条既能解释 TC-09，也说明**它不是"GPU 等渲染"**。

### 2.2 TC-09 日志时间线（旧证据，`runs/2026-11-05/TC-09/ue.log`）

| 本地时刻 | 事件 |
|---|---|
| 16:07:56 | 启动（`-log -stdout -windowed -ResX=1000 -ResY=750`） |
| 16:07:59.364 | `gpu="AMD Radeon RX 7900 GRE (RADV NAVI31)"`、`gpudriver=26.2.6`、`rhifeaturelevel=SM5`、Vulkan async compute ENABLED、wave ops ENABLED → **RHI 已经建好，不是显卡/驱动问题** |
| 16:08:03.902 | Zen DDC `status: OK`（`Latency=0.01ms, RandomReadSpeed=772MB/s`） |
| 16:08:03.908 | `Using 16 local workers for shader compilation` |
| 16:08:07.305 | `LogUdpMessaging: Using asynchronous task graph...` ← **阻塞起点 1** |
| 16:10:50.905 | `LogMetaSound: MetaSound Page Target Initialized`（+163.6 s） |
| 16:10:50.912 | `LogAudio: Registering Engine Module Parameter Interfaces...` |
| 16:13:30.083 | `No Audio Capture implementations found`（+159.2 s）→ 紧接 `RequestExit`（被 kill） |

那个把日志拦腰截断的 `Opening shared memory / Store settings...` 块是 `UnrealTraceServer` 子进程的输出，不是编辑器主线程。

### 2.3 今天的复跑（同一套件，两个新证据）

**复跑 #1 18:32**（带 `-LogCmds` 与 Verbose 模块日志）：无 160 s 级阻塞；t≈23 s 已写完 118.5 MiB 的 AssetRegistry 缓存并进入 shader 编译阶段（`ShaderCompileWorker` 子进程开始输出，最大 gap 74 s）。

**复跑 #2 18:36**（纯计时，5 s 采样）：

| t | 事实 |
|---|---|
| 5.0 s | 出现 `app_id=UnrealEditor` 窗口，标题「虚幻编辑器」（splash） |
| 10–15 s | 日志推进到 WorldPartition / CSV 元数据阶段 |
| 20.2 s | 窗口 id 2 → 3，标题变「Probe - …」= **主界面替换 splash** |
| 30.3 s | scoped 截图：完整编辑器（文件/编辑/构建…菜单、视口、大纲、细节、内容侧滑菜单、Cmd 栏），FPS **119.7**、8.4 ms、内存 3,220.18 mb；大纲里 `Entry (世界)` + `PlayerStart` |

⚠️ 重要旁证：**t=20.2 s 之后日志就停在 681 行不再增长**，而界面已经好了。→ **"日志是不是还在动"不能当作 UE 就绪判据**，必须用窗口/截图。

### 2.4 重建时间戳 vs 启动时刻（本轮根因的确凿部分）

```
15:16:22  Engine/Source/Runtime/ApplicationCore/Private/Linux/LinuxPlatformApplicationMisc.cpp   （Wayland 强制补丁）
15:17:45  Engine/Binaries/Linux/libUnrealEditor-ApplicationCore.so                               （重链接）
16:07:50.29  Engine/Binaries/Linux/libUnrealEditor-VulkanRHI.so  (+ .debug 17MB, .sym 6MB)      （重链接）
16:07:50.55  Engine/Programs/UnrealBuildTool/Log.txt   → "Result: Succeeded, Total execution time: 8.72 seconds"
16:07:56  TC-09 的 UnrealEditor 启动                                                             ← 重建后 6 秒
```

规模：`Engine/Binaries/Linux` = **7.8 GB / 936 个 .so + 912 个 .debug**；`/home` 在 `nvme0n1p5[/@home] btrfs, compress=zstd:6`，**已用 88%**（693G/800G）。当日 15:00 之后被改写的二进制有 7 个、合计约 50 MB（ApplicationCore + VulkanRHI 及配套 .debug/.sym）。

### 2.5 为什么可以排除"GPU/资产/shader"

- RHI 设备在 `16:07:59` 就建好，GPU 名/驱动/特性级全部正确，且后面没有一条 RHI error。
- 两段阻塞中途还有日志（16:10:50），进程未死、未被信号打断，不是死锁症状。
- 资产：`AssetDataGatherer` 正常、编辑器能开 `Entry`；本轮截图直接证明地图与资产没问题。
- shader：进入 shader 编译阶段会在 stdout 看到 `ShaderCompileWorker` 的 `LogInit: Running DelayedAutoRegister Phase ...` 子进程输出——TC-09 日志里**从未出现**，它压根没走到那一步。

### 2.6 残余不确定度（不粉饰）

那两段各 ~160 s 究竟阻塞在**哪个插件的 StartupModule / 哪个 syscall**，已无法从旧日志确定：当时没开 Verbose、进程被 kill 时也没抓栈。能确定的只是"非 error、非 GPU、非资产、非网络"以及"现在不复现"。§5 给出了下次再卡时**一次就能点名**的做法。

## 3. 方案对比（让 UE 编辑器可被 AI 后台控制并可验收）

| 方案 | 做法 | 代价 | 风险 | 判断 |
|---|---|---|---|---|
| **(a) 真实会话里跑 UE，只做输入注入验收** | 在用户 niri 会话里 `niri msg action spawn` 起编辑器（非嵌套），AI 只对目标窗口注入 + 截该窗口 | 占一个 tile；抢占 CPU/GPU；用户可感知 | 低（输入走 `agent-0` 座席，不碰前台） | **推荐**。唯一完全贴近最终形态的验收；本轮因用户正用 UE6 未执行 |
| (b) 换 niri 后端 / 虚拟输出 | 嵌套实例改 udev/DRM，或给 headless 后端补输出 | 要抢显示输出（风险最高）；headless 后端目前 `outputs={}` 且无渲染器 | 高 | **否决，不需要**。嵌套 winit 实测 119.7 FPS 出图，能力不是瓶颈 |
| (c) 换 UE 侧设置 | `-nop4`（免源码控制探测，用户自己的 UE6 也这么跑）、`-nosound`（`Misc/App.h:436` 确认该开关存在，省音频初始化约 2–3 s）、`-windowed -ResX/-ResY` 固定窗口；`-ddc=` 指定 DDC | 近零 | 无 | **部分采纳**，与 (a) 一起用。注意：**5.8 源码里不存在 `-nosplash`**（`rg '\"nosplash\"'` 零命中，splash 是 Slate 窗体）；`-nullrhi` 不能交互，**不可用**于验收 |
| (d) 用打包后的 standalone 而不是编辑器 | `RunUAT BuildCookRun -platform=Linux -clientconfig=Development`，验收 game viewport | 最小工程 cook+package 约 10–20 min（估），每次改设置都要重打 | 中（首次打包易缺 SDK/依赖） | **长期可选**。它是最像"纯 Wayland 客户端"的形态，但本轮不必要 |

**推荐组合：(a) + (c)。** (b) 已用数据否掉，(d) 留作回归形态。

## 4. 下一轮验收：具体怎么跑、判据是什么

### 4.1 前置（每条都来自本轮教训）

1. **验收窗口内不许重编译引擎**——本轮卡顿就发生在重建后 6 秒。
2. 冷启动第一次给足预算，**不要 5 分钟就杀**（本轮被杀在 5 min 34 s，当时它还在推进）。
3. 不用日志判就绪（§2.3：日志停住时界面已好）。

### 4.2 命令（方案 a，真机会话）

```bash
export HOME=/home/sx PATH=/usr/local/bin:/usr/bin:/bin XDG_RUNTIME_DIR=/run/user/1000
unset DISPLAY
niri msg action spawn -- bash -lc '/home/sx/projects/unrealengine/ue5.8/Engine/Binaries/Linux/UnrealEditor \
  /tmp/ue-probe2/Probe.uproject -nop4 -nosound -windowed -ResX=1280 -ResY=720 -log -stdout \
  > /tmp/ue-probe2/ev3/ue.log 2>&1'
```

（嵌套模式复跑时把 `niri msg action spawn` 换成 §6 的 `run2.sh`，其余不变。）

### 4.3 判据（全过才算通过）

| # | 判据 | 阈值 | 实测基线 |
|---|---|---|---|
| 1 | `niri msg -j windows` 里出现 `app_id=UnrealEditor` | ≤ 15 s | 5 s |
| 2 | scoped 截图出现菜单栏+视口+大纲/细节（**不看日志**） | ≤ 180 s（冷启动首次 ≤ 300 s） | 20 s |
| 3 | 输入送达：注入 `W` 按住 0.5 s，视口相机前移 → 前后截图 hash 不同 | 必须不同 | TC-09 只证到"点一下画面变"，本轮升级为相机位移 |
| 4 | 不扰动：注入前后 `niri msg -j focused-window` 的 `id`+`focus_timestamp` 不变；`wl-paste --list-types` 不变；`/tmp/poc/bind-fired` 不出现 | 全部不变 | 前几轮已证 |
| 5 | 性能：截图里的 FPS ≥ 基线 70% | ≥ 84 FPS | 嵌套内 119.7 FPS |
| 6 | 收尾：`pgrep -af UnrealEditor` 只剩用户自己的 ue6 实例 | 必须 | — |

清理用**精确路径**：`pkill -f "UnrealEditor /tmp/ue-probe2/Probe.uproject"`，**永不**通配 `UnrealEditor`。

### 4.4 万一又卡住（3 分钟出结论，别等）

见 §5：抓一次全线程栈，直接点名插件，然后照 §2.1 的代码路径定位。

## 5. 诊断工具：下次再卡时"一次点名"

本机 `/proc/sys/kernel/yama/ptrace_scope = 1`，**`gdb -p <pid>` 从别的 shell 挂不上去**（只能挂后代）。所以让 gdb 当父进程、用信号打断：

```gdb
# /tmp/usrtest.gdb  （本轮已冒烟验证：对 /usr/bin/sleep 30 打出 clock_nanosleep 栈）
set pagination off
set confirm off
handle SIGUSR1 stop nopass print
run
thread apply all bt 25
kill
quit
```

```bash
gdb -q -batch -x /tmp/usrtest.gdb --args <UnrealEditor> /tmp/ue-probe2/Probe.uproject -log -stdout ... &
sleep 40 && kill -USR1 $(pgrep -f "<UnrealEditor> /tmp/ue-probe2")   # 卡住时打一枪
```

备选（**本轮实测无效，别再指望**）：`-LogCmds="LogModuleManager Verbose, LogPluginManager Verbose"` 只输出了 ShaderCompileWorker 子进程的行，编辑器侧没有任何插件名输出。

## 6. 证据文件

| 文件 | 内容 |
|---|---|
| `runs/2026-11-05/TC-09/ue.log` | 旧的那次（5 min 34 s） |
| `runs/2026-11-05/TC-09b/ue-warm.log` | 今天复跑 #2 的完整日志 |
| `runs/2026-11-05/TC-09b/timeline-warm.txt` | 5 s 采样的窗口/标题/日志行数时间线 |
| `runs/2026-11-05/TC-09b/editor-ready-t30.png` | t=30.3 s 的编辑器截图（119.7 FPS，Entry 地图已加载） |
| `runs/2026-11-05/TC-09b/ue-cold1.log` | 今天复跑 #1（带 Verbose），可对照"无 160 s 阻塞" |
| `/tmp/ue-probe2/run.sh`、`run2.sh`、`poc.kdl`、`Probe.uproject` | 复现脚本与最小工程（/tmp 会被清，需要时按 §4.2 重建） |
