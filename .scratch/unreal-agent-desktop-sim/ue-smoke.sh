#!/usr/bin/env bash
# 在 agent 桌面里跑 UE 编辑器冒烟：起编辑器 → 截图 → 控制台命令 → PIE → 停止。
# 用法: ue-smoke.sh <uproject> [日志目录]
# 前置: 生产 fork niri（scoped-input-poc）+ /mnt/Video2/System/repos/agent-seat-probe/target/debug 预编译工具。
set -euo pipefail

PROJECT="${1:?usage: ue-smoke.sh <uproject> [outdir]}"
OUT="${2:-/home/sx/.dsh/tmp/ue-sim}"
EDITOR=/home/sx/projects/unrealengine/ue6/Engine/Binaries/Linux/UnrealEditor
PROBE=/mnt/Video2/System/repos/agent-seat-probe/target/debug
export PATH="$PROBE:$PATH"

mkdir -p "$OUT"
rm -f "$OUT/ue-smoke.log"

# UE 同项目只允许一个实例（"Existing instance is the same age or newer"）：已经有编辑器窗口就先退出，
# 否则新进程拿不到窗口，输入会打进屋主的旧实例、日志却写在新文件里（实测踩过）。
if niri msg --json windows 2>/dev/null | grep -q '"app_id":"UnrealEditor"'; then
  echo "已有 UnrealEditor 窗口在跑；先关掉它再跑本脚本"
  exit 1
fi

# 必须 setsid：普通 nohup 会被本会话回收（父进程死 → UE 退出路径撞 LazySingleton 断言 + Signal 11）。
setsid nohup bash -c "'$EDITOR' '$PROJECT' -windowed -ResX=1280 -ResY=720 -nosplash -abslog='$OUT/ue-smoke.log' >'$OUT/ue-smoke.out' 2>&1" >/dev/null 2>&1 &

# 等窗口出现在自己的桌面，并按 pid 认准是我们起的那个进程（niri msg 的 JSON 里带 pid）。
WIN="" PID=""
for _ in $(seq 1 90); do
  sleep 2
  PID=$(pgrep -n -f "UnrealEditor $PROJECT" || true)
  [ -n "$PID" ] || continue
  read -r WIN PID < <(niri msg --json windows 2>/dev/null | PID="$PID" python3 -c 'import json,os,sys
pid=int(os.environ["PID"])
w=[x for x in json.load(sys.stdin) if x.get("app_id")=="UnrealEditor" and x.get("pid")==pid]
print(w[0]["id"], pid) if w else print(" 0")' 2>/dev/null || echo " 0")
  [ "${WIN:-0}" -gt 0 ] && break
  WIN=""
done
[ -z "$WIN" ] && { echo "编辑器窗口未出现，看 $OUT/ue-smoke.out"; exit 1; }
echo "window=$WIN pid=$PID"

# 窗口出现 ≠ 能接输入：等引擎初始化完（否则点击落空、命令不进日志）。
for _ in $(seq 1 60); do
  grep -q 'Engine is initialized' "$OUT/ue-smoke.log" 2>/dev/null && break
  sleep 2
done
grep -q 'Engine is initialized' "$OUT/ue-smoke.log" || { echo "引擎没初始化完"; exit 1; }
sleep 5
echo "engine ready"

# 坐标一律千分数（probe 按钉住表面的比例映射），不是像素。
scoped-target "$WIN" >/dev/null
scoped-shot "$WIN" "$OUT/smoke-01-editor.png"

agent-seat-probe agent-0 click 500 983 >/dev/null   # 底部控制台输入框
agent-seat-probe agent-0 text 'stat fps' >/dev/null
agent-seat-probe agent-0 keys enter >/dev/null
grep -q 'Cmd: stat fps' "$OUT/ue-smoke.log" || { sleep 5; grep -q 'Cmd: stat fps' "$OUT/ue-smoke.log"; } \
  || { echo "控制台命令没进日志"; exit 1; }
scoped-shot "$WIN" "$OUT/smoke-02-fps.png"

agent-seat-probe agent-0 click 587 59 >/dev/null     # Play
sleep 15
grep -q 'PIE总开始时间' "$OUT/ue-smoke.log" || { echo "PIE 没起来"; exit 1; }
scoped-shot "$WIN" "$OUT/smoke-03-pie.png"

agent-seat-probe agent-0 click 290 380 >/dev/null   # 视口中心 → 鼠标捕获
agent-seat-probe agent-0 keys w >/dev/null
sleep 1
scoped-shot "$WIN" "$OUT/smoke-04-pie-input.png"
agent-seat-probe agent-0 keys escape >/dev/null
agent-seat-probe agent-0 click 586 79 >/dev/null    # 停止 PIE
sleep 2
scoped-shot "$WIN" "$OUT/smoke-05-stopped.png"
echo "PASS: 截图在 $OUT"
