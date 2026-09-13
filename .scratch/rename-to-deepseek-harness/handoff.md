# 交接：`master/` → `deepseek-harness/` 改名（2026-09-13）

## 已完成（fs 工具，不依赖子进程）

- `MyAI/master` → `MyAI/deepseek-harness`（目录改名；**git 分支仍是 `master`**，HEAD `403e69b918`）
- `~/.local/bin/dsh` 符号链 → `deepseek-harness/apps/cli/lib/bin.js`
- `deepseek-harness/.git/config.worktree` 的 `core.hooksPath` → 新路径
- 已改指新路径：三个插件的 `link:` 依赖 · 工作区 `.gitignore` · `MyAI/AGENTS.md` · `~/.dsh/AGENTS.md`

## 为什么还有待办：本会话的子进程工具已失效

改名后，**正在运行的生产进程仍用旧绝对路径拉起子进程**：

```
/usr/bin/node /home/sx/projects/MyAI/deepseek-harness/packages/subprocess/subprocess-local/lib/runner.js -- bash -c ...
```

该路径已不存在 → 本会话的 `bash`（以及一切走子进程的工具）报
`subprocess scope exited before its bootstrap consumed the launch request`。
只有生产重启能重解析，重启后一切恢复。

## 待办（按顺序，需 bash）

1. **重启生产**：`systemctl --user restart dsh-web`
   - 重启会在启动时自动重写 `~/.dsh/profiles/node_modules` 的 243 个 fallback 符号链接
     （`healProfilesModuleFallback` → `moduleFallbackEntryCurrent` 对符号链接做**目标字符串精确比对**，
     路径一变即判过期并重写），并修复 `~/.dsh/profiles/web` 侧同样指向旧路径的链接。
2. **删除过渡残留**：`rm -rf /home/sx/projects/MyAI/deepseek-harness`
   - 这是为救活本会话子进程而临时建的 shim 目录，内容仅
     `packages/subprocess/subprocess-local/lib/runner.js`（一行转发 import，**已验证无效**，可安全删）
3. **重建插件依赖**：三个插件目录各 `pnpm install`
   - `link:` 已改指新路径，但 `pnpm-lock.yaml` 里仍是旧路径
4. **替换剩余文档路径**：`grep -rl 'MyAI/master' … | xargs sed -i 's|MyAI/master|MyAI/deepseek-harness|g'`
   - 已知命中：`docs/vendor-plugins.md` · `dsh-extension-inventory.json` ·
     `docs/plans/manager-task-orchestration.md` · `update-app/applist.toml`（注释行）·
     `dsh-extensions/plugins/web-dsh-web-extension/README.md` ·
     `deepseek-harness/CONTEXT.md` · `deepseek-harness/.agents/skills/dsh-deploy-master/SKILL.md`
5. **提交推送**：工作区 `main` · dsh-extensions `main` · update-app `main` · deepseek-harness `master` → `fork`

## 被阻塞的清理（用户已批准「全部清理」）

- `~/.dsh/profiles/web/node_modules/onnxruntime-node` 的 CUDA（302M）+ TensorRT（836K）provider
  —— 本机显卡是 **AMD RX 7900 XT**，无 NVIDIA 驱动、无 `nvidia-smi`，这两个 `.so` 需要 libcuda，**永远加载不了**
- 四个 `link:` 插件的 `node_modules` **≈793M**
  —— 已核实：`lib/**/*.js` **零动态 `import()`、除 react 系列外零外部 require**（react 由浏览器模块表应答，其余只有 `node:*`）
- `dsh-context-compression-selector/` 17M（生产 profile 用 npm 版 `0.1.0`，该 checkout 不参与运行时）
- `update-app/bin` + `obj` 2.2M
- ⚠ **`deepseek-harness/node_modules`（2.3G）不可删**：它是**运行时依赖**——
  `~/.dsh/profiles/node_modules` 的 243 个 fallback 符号链接就指向
  `deepseek-harness/apps/cli/node_modules/...`。删了生产下次启动起不来。
