# agent 桌面 UE 操作模拟测试

2026-11-27 自测记录：在 agent 桌面（nested niri，`ws-49e1c46e`）里驱动 UE6 编辑器与打包后的 PCGame，
验证「显示别人的窗口 + 定向投键鼠 + 单窗截图」这套链路对 UE 可用。测试工程
`test-project/unreal-pc-game`（在 MyAI `.gitignore` 里、不入库），这里只放脚本与结论。

## 跑法

```bash
. ./.scratch/unreal-agent-desktop-sim/ue-smoke.sh /home/sx/projects/MyAI/test-project/unreal-pc-game/PCGame.uproject
```

## 链路结论（都实测通过）

| 环节 | 证据 |
|---|---|
| 编辑器起在 agent 桌面、真 GPU（RADV NAVI31，Vulkan 1.4.363） | `niri msg --json windows` 出现 `app_id=UnrealEditor`，窗口 900x1338 tile |
| 控制台输入 | 点 (500,983)→`text 'stat fps'`→`keys enter`，日志 `Cmd: stat fps` |
| PIE | 点 Play(587,59)，日志 `PIE总开始时间：0.15秒`，工具栏变暂停/停止 |
| PIE 里键鼠 | 点视口中心触发鼠标捕获（标题变「鼠标光标的Shift+F1」），`keys w` 后画面移动 |
| 打包版 PCGame | 窗口 id 4，`scoped-shot` 出 Starter 画面，`keys w` 后相机推进 |

坐标是**千分数**（`agent-seat-probe agent-0 click 500 983` 表示钉住表面的 50%/98.3%），不是像素。

## 踩到的坑（按处理顺序）

1. **普通 `nohup ... &` 的 UE 会被回收**：本会话的 bash 一退出，UE 走退出路径撞
   `Assertion failed: Ptr [File:Runtime/Core/Public/Misc/LazySingleton.h] [Line: 109]` + `Signal 11`，
   窗口一个都不剩。必须 `setsid nohup bash -c '... >log 2>&1' &`（脚本里就这么写）。
2. **`agent-seat-probe --help` 会 panic**：第一参数被当 seat 名解析（`seat "--help" not found`）。
   不知道用法时去读源码 `/mnt/Video2/System/repos/agent-seat-probe/src/main.rs`。
3. **`repos/agent-seat-probe` 里编译不过**：`Cargo.toml` 依赖 `../niri/niri-ipc`，而
   `repos/niri` 是上游 main（无 `ScopedTarget`/`ScopedScreenshot`）。要用预编译产物
   `/mnt/Video2/System/repos/agent-seat-probe/target/debug/`（配 `/mnt/Video2/.../niri` 的 fork）。
4. **`-ResX/-ResY` 不生效**：niri 把窗口铺满 tile（900x1338），请求的 1280x720 被忽略。
   截图按实际 tile 比例看，别按请求分辨率算坐标。
5. **打包版 `PCGame.sh` 报 `Project file not found: ../../../PCGame/PCGame.uproject`**：
   脚本默认相对路径指向不存在的 uproject，靠 project info helper 兜底起来。产物里没有
   `PCGame.uproject`（BuildCookRun 没 stage 它）——要么 stage 进去，要么改 `PCGame.sh` 的默认路径。
6. **冷启动首次 `ShaderCompileWorker terminated unexpectedly, return code 0`**：setsid 之后未复现，
   疑与父进程被杀同源；真机首次跑要么先预热 DDC，要么接受首帧慢。

7. **帧率只有 ~1 FPS（不是掉帧，是被节流）**：嵌套 niri 的 winit 后端在
   `/mnt/Video2/System/repos/niri/src/backend/winit.rs` 里明确写着
   `FIXME: this should wait until a frame callback from the host compositor, but it redraws right away instead`，
   一次重绘约 1 秒；`stat fps` 在编辑器与打包版都显示 0.58–1.00 FPS、1000–1726 ms/帧，
   GPU 利用率只有 3–5%（GPU 并不忙）。功能不受影响（输入、PIE、截图都对），
   但**不能用这套环境测性能/手感**，要看帧率必须回生产桌面（`AGENT_DESKTOP=0`）。
8. **UE 同项目单实例**：已有同 uproject 的编辑器在跑时，新进程只打印
   `Existing instance is the same age or newer` 就退出，窗口不会出现——脚本里先检测再跑，
   否则会把输入打进屋主的旧实例、日志却写进新文件（实测踩过，误判成"输入没生效"）。

## 已知未测

- VR/OpenXR（需要物理 GPU 会话，agent 桌面不做）。
- 菜单操作、蓝图编辑器、资产导入等更复杂的 UI 路径，只测了控制台 + PIE + 视口。
- 打包版启动脚本的相对路径坑（第 5 条）只是绕过、没修产物。
