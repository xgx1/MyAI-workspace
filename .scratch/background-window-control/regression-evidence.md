# 后台窗口控制回归证据（第二轮：复现 → 修复 → 复测）

被测对象：niri fork `/home/sx/projects/niri`（分支 `scoped-input-poc`）+
`/home/sx/projects/agent-seat-probe` 探针。全部测试跑在**自建嵌套环境**
（`regression-visibility/`：Xvfb → niri(`poc.kdl`) → xwayland-satellite），
不碰生产 niri（PID 2585）、生产 satellite（PID 3087，`:0`）、日常浏览器与 DSH。

## 怎么跑

```bash
cd .scratch/background-window-control/regression-visibility
python3 cycle.py 2 suite.py      # 14 项：展示/截图/席位输入/失败关闭/悬停不夺焦
python3 cycle.py 2 suite2.py     # 8 项：同 X server 内键鼠隔离、pin 契约
```

`cycle.py` 每轮：拉起 `environment.py`（Xvfb+`niri -c poc.kdl`+satellite）→ 等
`run/environment.json` → 拉起 `apps.py`（4 个真实 GTK3 fixture）→ 等 `run/apps.json`
→ 跑套件 → 写 `run/results*-roundN.json` → 用 `run/STOP-APPS`/`run/STOP` 收尾、
回收子进程并删掉本次的 `/run/user/1000/bwc-reg-*/`。

## 结果（FAIL 0）

| 套件 | 轮次 | PASS | FAIL | LIMITATION |
| --- | --- | --- | --- | --- |
| `suite.py`（14 项） | 2 | 13 | 0 | 1 |
| `suite2.py`（8 项） | 2（+ 修复前三轮同样 7/0/1） | 7 | 0 | 1 |

修复前第一轮 `suite.py` 是 PASS 10 / FAIL 2 / LIMITATION 2；本轮 `12`、`10`、
`14` 三项从 FAIL/LIMITATION 变为 PASS，剩下唯一的 LIMITATION 是
「XSendEvent 不是投递路径」（见限制 1）。

## 本轮修好的三处「跑不通」

### A) 未知窗口必须失败关闭（原 `12_invalid_target_fails_closed` FAIL → PASS）
- `niri` `src/ipc/server.rs`：`Request::ScopedTarget` 原先是「插 idle → 直接设 pin →
  回 Handled」，未知 id 也会被当真，调用方以为切换/清除成功，而旧窗口继续吃输入。
  现在在 idle 回调里先校验，再经 `async_channel` 回包：未知 id →
  `Err("scoped target: no window with id {raw}")`；**出错不动原 pin**；只有成功才
  `Handled`。
- 探针 `agent-seat-probe/src/bin/scoped-shot.rs` 原先 `Err` 只打印到 stdout 却
  `exit 0`，调用方无法分辨失败；改成 `eprintln!` + `exit(1)`。
- 证据：`pin_error = {"Err": "scoped target: no window with id 99999"}`、
  `capture_error = "error: scoped screenshot: no window with id 99999"`、退出码非 0、
  不落 PNG、焦点不变。
- 配套 `13_rejected_target_keeps_previous_pin`：被拒的切换后原 pin 仍生效
  （agent 席位继续打进原窗口，`text="aaa"`）。

### B) 同一个 X server 里人和 agent 的键鼠互不串（原 `10` 失败 → PASS）
- 做法：在 satellite 的 `:2` 里建额外 master 对 `mpx-agent`（`XIAddMasterInfo`），
  给目标窗口设 ClientPointer/master 焦点后用 XTest 投递；人的输入走真实 core 设备。
- `suite.py` 证据：`{"human": "hhhhhhhhh", "agent": "baaaaaaaa"}`，`focus=5`
  （人仍在自己的 X11 窗口），`focus_transitions=[]`。
- `suite2.py` 证据（两轮一致）：8 次交错 core `h` / MPX `a` →
  `{"agent": "aaaaaaaa", "human": "hhhhhhhh"}`，core 焦点与 core 指针不变。
- 鼠标：`14_MPX_click_into_X11_without_moving_human_pointer` →
  `{"clicks": 3, "core_pointer_unchanged": true}`。

### C) 悬停不再夺焦（原 `14_strict_no_focus_when_human_hovers_real_window` 一直是 LIMITATION → PASS）
- 本机 `~/.config/niri/config.kdl` 开了 `focus-follows-mouse`，鼠标扫过窗口即夺焦；
  agent 窗口被人指针扫到，就会把会话焦点抢过去，等于把 agent 的按键交给人类、人类的
  按键交给 agent。
- `niri` `src/niri.rs` `handle_focus_follows_mouse`：若被扫到的窗口正是当前
  `agent_pin` 的 pin 目标，直接返回——指针经过 agent 的窗口不代表人想在那个窗口工作。
  只影响被 pin 的那一个窗口，其他窗口的 FFM 行为不变。
- 证据：`{"focus_before": 2, "focus_after": 2, "hovered_window": 3, "pointer": [1100, 220]}`，
  指针确实落在 agent 窗口矩形内（800,80 + 400×320）。

## 保持通过的展示 / 截图 / 席位回归

- `03_show_original_X11_no_focus`：把原窗口移进人的 workspace 并悬浮定位，人焦点不变
  （`focus_transitions=[]`），视觉证据 `run/03-visible.png`（X11 窗口贴在人窗口右侧，
  人窗口仍高亮）。
- `04_single_request_hidden_workspace_PNG_complete`：在看不见的 workspace 上单请求直出
  PNG（`png_bytes=13708`, sha256 `16e11a9a…c51602`），人焦点不变。
- `11_twelve_unique_single_request_captures`：12 次单请求截图，尺寸一致
  （`11887` 字节 ×12），不共享输出文件名、不误判上一轮旧文件。
- `08_thirty_show_hide_roundtrips_no_activation`：30 次亮/隐往返，窗口 id 不变、零焦点切换。
- `06`/`07`：`ScopedTarget` 之后 agent 席位的键盘事件只进被 pin 的窗口
  （native 与 X11 各一条），`focus_transitions=[]`，人窗口文本不变。

## 已知限制（记录，不在本轮范围）

1. **XSendEvent 不是投递路径**（suite1 `05`、suite2 `15`）：对 GTK3 fixture 发
   XSendEvent 文本零变化。后台打字必须走 agent 席位或 X11 master 注入。旧文档里
   「Unity 截图不变即证明全拒」正是把这条误当成普遍结论。
2. **satellite 只有一个 Wayland 客户端 = 只有一个键盘焦点**：人的 niri 焦点在原生
   Wayland 窗口时，satellite 的 view surface 没有键盘焦点，注入其 X server 的任何按键
   （core 与 MPX 一样）都会被丢弃。可验证的隔离场景是「人在一个 X11 窗口工作、agent 在
   同一 satellite 的另一个 X11 窗口工作」；**跨「X11 agent ↔ Wayland 人」的键盘隔离
   在本方案里做不到**，那种场景用 niri 的 agent-0 席位。
3. **同一环境连跑第三次起 X11 注入整体失效**（core/MPX 皆然）；harness 因此每轮重建
   环境（`cycle.py`），这属于 harness 事实，不是功能失效。
4. 未 pin 的窗口仍受 focus-follows-mouse 影响（人类自己配置的桌面行为）。
5. 视频录制与相对鼠标/指针锁定是范围外边界，未实现。

## 卫生与落点

- 收尾状态：0 个自建 niri/satellite/fixture 进程，`/run/user/1000/bwc-reg-*` 为 0
  （`environment.py` 已在收尾时 `shutil.rmtree` 自己的 runtime 目录）。
- 生产 `niri --session`（PID 2585）、生产 `xwayland-satellite :0`（PID 3087）全程
  未被触碰；生产 DSH 未重启。
- 证据文件：`run/results-round{1,2}.json`、`run/results2-round{1,2}.json`、
  `run/suite*-round*.log`、`run/03-visible.png`。
- 代码落点：`niri` 分支 `scoped-input-poc` 已推送两个提交——`0647becb`
  `fix(ipc): fail closed on an unknown scoped target`、`b55b7334`
  `fix(focus): keep focus-follows-mouse off the window the agent controls`；
    `agent-seat-probe` 已于 2026-11-05 纳管为私有仓 `xgx1/agent-seat-probe`（`main`），
  `scoped-shot`/`scoped-target` 的退码修复随之入库；`Cargo.toml` 的 `niri-ipc` 改成
  `../niri` 相对路径，clone 时与 niri 检出放同级。
