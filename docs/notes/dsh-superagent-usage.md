# dsh-superagent（DeepSeek Super Agent 原型）使用说明

仓库：<https://github.com/deepseek-ai/dsh-superagent-prototype>（MIT，v0.1.0，研究原型，非官方产品；作者自述“仅供参照，别当生产软件”）。
设计文：*Exploring Super-agent Design: Towards a More Autonomous Agent System*（中文原文，官方 X 有机器翻译版）。

## 一句话

给**一个 GitHub 仓库**配一个常驻 agent：允许的人 `@` 它，它开一张工单（Ticket），在**自己的 DSH Session 和自己的目录**里干活，最后在原来的对话里回一个 PR。面板显示“哪里需要人”。

## 它跑起来是什么形状

- 一个**独立的 DSH profile**（本篇叫 `superagent`，默认端口 `3082`）——它改进程级 `PATH` 和 git 配置，必须和日常 profile 分开，各自重启。
- **Router**（主 Session，`dsh-superagent-router` preset）：常驻，收事件、判来源、建工单。
- **Worker**（执行器 Session，`dsh-superagent-worker` preset）：每张工单一个，独立目录，前台命令 5 秒转后台。
- **Source**：`github-watch`（默认开）、`feishu-watch`（patch 里 `disabled: true`）。
- **Policy**：白名单——不在名单上的人 `@` 也不会变成工单。
- 状态与数据库：`<stateDir>/orchestrator.sqlite`，外加 `worker-bin/`（gh/lark-cli 命令垫片）和 `worker-gitconfig/`（隔离的 git 凭据）。

**这两个 preset 不给手动用**：别在个人会话里选它们，也别删 `cordis.patch.yml` 里那两行——删了工单恢复会报 `agent-preset/not-found`。

## 本机（Windows）为什么没装

三条硬证据，都在本机实测过：

| 证据 | 结果 |
| --- | --- |
| `stateDir` 的 schema 是 `/^\//`（只认 POSIX 绝对路径） | 配 `C:/.../state` 直接 `ValidationError: $.stateDir expect string to match regexp /^\//`，插件不激活 |
| `scripts/dsh-superagent` 是 Python 脚本，`tmux` 不在就 `RuntimeError('Both dsh and tmux must be on PATH.')` | 本机无 tmux，`start/stop/status` 全不可用 |
| `src/infra/environment.ts` 写的是 `#!/bin/sh` 命令垫片，靠 `IFS=:` 重写 PATH | Windows 下 Node `spawn('gh')` 不认无扩展名的垫片，凭据隔离失效 |

第三条最要命：垫片不生效 = worker 会用**你自己的** `gh` 身份推代码。所以这台机器上不装、也不建议硬凑。下面全部按 **Linux** 写。

---

## 前置条件（Linux）

- Node.js 22.19+ 或 24+、pnpm、git 2.32+、Python 3.8+、**tmux**
- GitHub CLI `gh` ≥ 2.48
- 一个 github.com 上的仓库（不支持 GHE）；仓库用 LFS 就装 `git-lfs`
- DSH 能正常跑模型（superagent 用 profile 的默认模型）
- 飞书可选：`lark-cli`（1.0.90 测过）+ 一个带机器人的自建应用

## 安装

```bash
git clone https://github.com/deepseek-ai/dsh-superagent-prototype ~/src/dsh-superagent
cd ~/src/dsh-superagent
pnpm install && pnpm build

# 建 profile（只给新装用！已有 profile 时这条会重建并删掉 cordis.patch.yml）
dsh superagent --from-default-profile web --dump-config > /dev/null
dsh plugin --profile superagent add "link:$PWD"
```

`DSH_HOME` 不是 `~/.dsh` 时先导出它。

**版本**：`package.json` 的 `engines.dsh` 是 `^0.2.1-alpha.2`。本机实测 dsh `0.2.2-rc.1` 能加载这个 bundle（没触发版本拒绝）——文档里那个 `npm install -g @deepseek-ai/dsh@0.2.1-rc.3` 只是发布时的公开版本，**不要**拿它覆盖你自己在用的 dsh。真被版本卡住时，改 checkout 里 `engines.dsh`，别降 dsh。

## 机器配置

把 `examples/profile.cordis.patch.yml` 整个拷成 `$DSH_HOME/profiles/superagent/cordis.patch.yml`，替换占位符：

```yaml
- id: webserver
  config:
    host: 127.0.0.1
    port: 3082
- id: dsh-superagent
  config:
    stateDir: /home/<你>/.dsh/state/superagent
# 飞书才需要：
# - id: dsh-superagent-feishu
#   disabled: false
```

- `stateDir` **必须**是绝对 POSIX 路径，且只有首次启动前能改；升级前备份这里的 `orchestrator.sqlite`。
- `promptMaxChars`、`admissionContextMaxPages`、`admissionContextTimeoutMs` 可选；其余机器上限改在 **Settings → Deployment** 或 Plugin Manager 里，不用重启。
- 写错或写了不认识的键 → 起不来，日志会点出键名。

## 启动 / 停止 / 状态

```bash
cd ~/src/dsh-superagent
scripts/dsh-superagent start     # 在 tmux session dsh-superagent 里跑 dsh --profile superagent
scripts/dsh-superagent status
scripts/dsh-superagent stop      # 优雅退出，最多等执行器 5 分钟，不强杀
scripts/dsh-superagent restart
```

其他 profile / 端口：`--profile`、`--url`，或环境变量 `DSH_SUPERAGENT_PROFILE` / `DSH_SUPERAGENT_URL`。

| 退出码 | 含义 | 重启能修吗 |
| --- | --- | --- |
| 0 | 正常 | — |
| 1 | 没跑 / 跑了两份 / 不响应 / runtime 报错 | 可能 |
| 2 | 跑着，但某个部件（Source、`sync:<source id>`）报错 | 不能 |
| 3 | 跑着，等你去配（setup 未完成） | 不能 |

`status` 有 `errors`（部件与详情）和 `setup`（缺什么）。`--respect-stop` 保留你手动的 `stop`（只有 `stop` 写这个标记）。日志在 `.artifacts/dsh-superagent-<profile>-<日期>-<时间>-<pid>.log`，只留最近 20 份。

## 第一次配置（面板 + Management API）

打开日志里打印的 URL，侧栏选 **Superagent**。setup 不过，轮询和干活都不会开始。

面板四块：

1. **Sources** — 仓库 `owner/name` + 机器人 CLI 绝对路径（如 `/home/me/.local/bin/gh-agent`）。默认靠**机器人账号的 GitHub 通知**收请求；`observeIssues/Pulls/Comments/Ci` 四个开关默认关，开了才收全仓库动静。
2. **Policy** — 每个 Source 一份白名单；列表空着就没人能建工单。
3. **Execution** — 目录根 + 准备命令。每张工单要 checkout 的话，形如：

   ```sh
   git -C /home/me/src/widgets fetch --no-tags "https://github.com/$DSH_SUPERAGENT_GITHUB_REPOSITORY.git" "${DSH_SUPERAGENT_GITHUB_PR_HEAD:-HEAD}:refs/dsh-superagent/$DSH_SUPERAGENT_TICKET" &&
   git -C /home/me/src/widgets worktree add -b "agent/$DSH_SUPERAGENT_NAME" "$DSH_SUPERAGENT_DIR" "refs/dsh-superagent/$DSH_SUPERAGENT_TICKET"
   ```

   你自己的 CLI（比如签了你个人账号的 `gh`）加进 **blockedCommands**。
4. **Prompts** — 团队段落：GitHub 披露行、review 机器人、commit 作者、auto-merge 条件。

命令行等价（面板用的是同一个本地 HTTP API，必须带 `x-orchestrator-request: 1`，Host 必须是 `127.0.0.1:<port>` 或 `localhost:<port>`）：

```bash
api=http://127.0.0.1:3082/orchestrator/api
rev=$(curl -s -H 'x-orchestrator-request: 1' $api/settings | jq '.sources[] | select(.id=="github") | .revision')
curl -s -X PUT -H 'x-orchestrator-request: 1' -H 'content-type: application/json' \
  $api/settings/source:github \
  -d "{\"value\":{\"enabled\":true,\"config\":{\"repository\":\"acme/widgets\",\"cli\":\"$HOME/.local/bin/gh-agent\"}},\"revision\":$rev}"
```

其他常用：`GET state`（setup/health/load）、`POST executor/pause`、`POST tickets/<id>/retry|stop`、`PUT prompts`。返回 `restarting: true` 就是在重启，等 `scripts/dsh-superagent status` 不再退 1 再发下一个请求。别的路由是面板私有的，会变。

## 机器人账号（必须专用，别用你自己的）

```sh
mkdir -p ~/.local/bin
cat > ~/.local/bin/gh-agent <<'EOF'
#!/bin/sh
GH_CONFIG_DIR="$HOME/.config/gh-agent" exec gh "$@"
EOF
chmod +x ~/.local/bin/gh-agent
gh-agent auth login                 # 用机器人账号登录
gh-agent api user --jq .login       # 打印它的 login，superagent 就是这么读的
```

- 必须是**用户账号**并对仓库有写权限；GitHub App 不行——它要读账号通知。
- 它写的一切都以这个账号名义出现。所以：**独立账号**。
- setup 会写 `<stateDir>/worker-bin` 的命令垫片（`gh` 走机器人 CLI、`lark-cli` 走机器人 CLI、被禁命令直接失败）和 `<stateDir>/worker-gitconfig`（只认机器人凭据、SSH 地址改写 HTTPS、LFS 过滤器）。这两个目录里**任何不是它写的文件都会让 setup 直接失败**。

## 日常怎么用

允许名单上的账号，在仓库的 Issue 或评论里写：

```
@<agent-login> 帮我把 xxx 的测试修了
```

- 轮询默认 1 分钟，Overview 上就该出现 Ticket。
- 它会先回一句已收到，然后在自己 Session 与目录里做，最后在原对话回 PR。
- **编辑已有 Issue 的正文加的 @ 收不到**，要新评论。
- 面板能看工单、执行器、暂停处理（`POST executor/pause`），也能重试/停止工单。

## 权限边界（必读）

两个 preset 都以 `danger-full-access`、**你当前的 OS 用户**身份跑。worker 能按路径执行任何程序、能读你的家目录。要隔离就给它一个**独立的 OS 账号**，里面只放机器人的凭据。命令垫片是"默认路径护栏"，不是安全边界。

## 升级

1. 等没有执行器正在跑轮次
2. 备份 `<stateDir>/orchestrator.sqlite`
3. `git pull && pnpm install && pnpm build`
4. `scripts/dsh-superagent restart`，看 status

新版本迁移过的库，旧版本打不开——回滚只能靠备份。DSH 本体升级后也要重启 superagent，否则面板加载不到匹配的产物。升级后看 prompts 里标 **Default updated** 的段落。

## 排障（挑最常撞的）

| 现象 | 原因与处理 |
| --- | --- |
| `The agent GitHub CLI is not set.` / `not found` / `cannot read its account` | GitHub 卡片里 CLI 没配、路径不对、或 wrapper 没 `auth login` |
| `@… cannot push to …` | 机器人账号对仓库没有写权限 |
| `The GitHub Source names no repository.` | 仓库没填 `owner/name` |
| Ticket 报 `The prepare command failed: …` | 输出里有真因（多半是 clone 路径）；修完重试工单 |
| `git does not read the github.com credential configuration…` | git < 2.32 |
| `… was not written by dsh-superagent` | `worker-bin` / `worker-gitconfig` 里有外来文件；挪走或换 `stateDir` |
| `status` 退 2 / 3 / 1 | 分别看 `errors` / `setup` / 日志 |
| 面板说没响应 | 正在重启，或配置没起来；看 DSH 日志 |
| 提了 @ 没反应 | 作者不在白名单、Source 没开、处理被暂停，或你是改正文加的 @ |

挂个每小时自检（在你**日常**的 profile 里建，别建在 `superagent` 里，这样 agent 挂了它还能跑）：让 agent 按 `docs/006-deployment.md` 的 Hourly check 段落建定时任务，退出码语义同上，只有退 1 才 `--respect-stop restart`。

## 本机已经做过的验证（可复现）

在 `.scratch/dsh-superagent/checkout` 留了一份克隆：

```powershell
cd C:\Users\Admin\Project\MyAI\.scratch\dsh-superagent\checkout
pnpm install; pnpm build          # 通过，产物在 lib/
```

再用**隔离的** `DSH_HOME`（`.scratch/dsh-superagent/home`）走了一遍真安装流程：建 profile、`dsh plugin add link:…`、写 patch、`dsh --profile superagent --dump-config` 能看到 3 个插件行 + 2 个 preset，`dsh superagent --no-open` 也能在 `:3099` 起来——**唯一卡死的就是 `stateDir` 那个 `/^\//` 正则**，也就是上面“Windows 为什么没装”。

真要用，去 Linux（或任何有 tmux 的 POSIX 机器）按“安装”那节从头跑一遍；不要把这份 scratch 里的 profile 拷过去，`link:` 路径和 stateDir 都是 Windows 的。
