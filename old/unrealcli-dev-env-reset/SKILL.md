---
name: unrealcli-dev-env-reset
description: unrealcli dev 环境完全清理与重启流程——dev stop 不彻底（后端/UE 端口/进程残留）时的标准清理序列
---

# unrealcli dev 环境完全清理与重启

## 问题
`unrealcli dev stop` 只停 PM2 列表，不杀实际进程——反复出现：
- **<BackendPort> 残留**（后端 dotnet 进程存活）→ 下次 dev run 报 "Port <BackendPort> is already in use"（<BackendPort> = 后端端口，从 unrealcli 配置或 netstat 找占用者确认）
- **<GamePort> 残留**（旧 UE server 存活占 UDP <GamePort>，UE 游戏默认 <GamePort>=7777）→ 新 server 落 7778 → unrealcli 等 "listening on port <GamePort>" 超时 60s
- **UnrealEditor 进程残留**（Live Coding 锁）→ 下次编译 "Unable to build while Live Coding is active"
- **PM2 daemon 环境固化**（dotnet 报 "N/A 不是有效的版本字符串"）→ pm2 kill 自愈

## 完全清理序列（编译或重启 dev 前执行）
```bash
# 1. 杀 <BackendPort> 占用（后端）
PID=$(netstat -ano | grep ":<BackendPort>" | grep LISTEN | awk '{print $5}' | head -1)
powershell -Command "Stop-Process -Id $PID -Force" 2>/dev/null

# 2. 杀所有 UE 进程（Live Coding 锁）
powershell -Command "Get-Process UnrealEditor -ErrorAction SilentlyContinue | Stop-Process -Force"

# 3. 清 PM2 daemon（环境固化）
pm2 kill

# 4. 验证干净
netstat -ano | grep -c ":<BackendPort>.*LISTEN"   # 应 0
netstat -ano | grep ":<GamePort>" | head -2        # 应无 LISTEN
tasklist | grep -c UnrealEditor                     # 应 0
```

## 重启
```bash
unrealcli dev run   # async 后台跑，等 80-100s
pm2 jlist | jq -r '.[] | "\(.name): \(.pm2_env.status)"'   # 4 个全 online
D=$(ls -t <ProjectRoot>/Logs/ | grep "^2026" | head -1)
grep -c "listening on port <GamePort>" "<ProjectRoot>/Logs/$D/ue-server.log"   # 应 1
```

## 验证就绪
- 4 进程 online + <GamePort> listening + 后端 <BackendPort> LISTEN + 无 502（chat/history → 502 = 后端死了/残留）

## 注意
- git-bash 下 `taskkill //F` 双斜杠语法报错——用 PowerShell Stop-Process
- dev run 前必须先清（否则 <BackendPort>/<GamePort> 残留导致启动失败）
- 用户也建议直接 `unrealcli dev stop && unrealcli dev run`——但该命令本身不杀残留进程，失败后必须走本清理序列