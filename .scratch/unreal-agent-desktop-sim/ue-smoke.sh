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

# 必须 setsid：普通 nohup 会被本会话回收（父进程死 → UE 退出路径撞 LazySingleton 断言 + Signal 11）。
setsid nohup bash -c "'$EDITOR' '$PROJECT' -windowed -ResX=1280 -ResY=720 -nosplash -abslog='$OUT/ue-smoke.log' >'$OUT/ue-smoke.out' 2>&1" >/dev/null 2>&1 &

# 等窗口出现在自己的桌面（niri msg windows 是 JSON 数组，窗口 id 由该桌面分配）。
WIN=""
for _ in $(seq 1 90); do
  sleep 2
  WIN=$(niri msg --json windows 2>/dev/null | python3 -c 'import json,sys
w=[x for x in json.load(sys.stdin) if x.get("app_id")=="UnrealEditor"]
print(w[0]["id"] if w else "")' 2>/dev/null || true)
  [ -n "$WIN" ] && break
done
[ -z "$WIN" ] && { echo "编辑器窗口未出现，看 $OUT/ue-smoke.out"; exit 1; }
echo "window=$WIN"

# 坐标一律千分数（probe 按钉住表面的比例映射），不是像素。
scoped-target "$WIN" >/dev/null
scoped-shot "$WIN" "$OUT/smoke-01-editor.png"

agent-seat-probe agent-0 click 500 983 >/dev/null   # 底部控制台输入框
agent-seat-probe agent-0 text 'stat fps' >/dev/null
agent-seat-probe agent-0 keys enter >/dev/null
sleep 2
scoped-shot "$WIN" "$OUT/smoke-02-fps.png"
grep -q 'Cmd: stat fps' "$OUT/ue-smoke.log" || { echo "控制台命令没进日志"; exit 1; }

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
