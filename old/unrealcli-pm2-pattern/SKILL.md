---
name: unrealcli-pm2-pattern
description: PM2 ecosystem 生成和 INI 持久化补丁模式，用于 UnrealCli 后台服务管理
---

# PM2 Ecosystem Pattern

UnrealCli 使用 PM2 管理后台进程。通过 `Pm2Helper.GenerateEcosystem(path, apps)` 生成临时 ecosystem JSON。

## Ecosystem App 匿名对象格式

```csharp
new
{
    name = "process-name",
    script = "executable-path-or-command",  // dotnet, UnrealEditor.exe, etc.
    args = "command line arguments",
    cwd = "working-directory",
    windowsHide = true,          // 隐藏窗口
    autorestart = false,         // dev 环境不自动重启
    env = new Dictionary<string, string>
    {
        ["KEY"] = "VALUE"
    }
}
```

## 启动 / 停止

```csharp
await Pm2Helper.EnsureInstalledAsync(runner, console);
var pm2 = Pm2Helper.Pm2Path!;

// 启动
Pm2Helper.GenerateEcosystem(ecoPath, apps);
await runner.RunAsync(pm2, $"start \"{ecoPath}\"");

// 停止
await runner.RunAsync(pm2, $"stop \"{name}\"", silent: true);
await runner.RunAsync(pm2, $"delete \"{name}\"", silent: true);
```

## INI 持久化补丁模式

当进程由 PM2 管理（CLI 退出后仍在运行）时，INI 补丁必须持久化：

```csharp
// dev run — 补丁 + 记录备份
IniPatcher.RecoverStaleBackups(iniPath);
var bak = IniPatcher.Backup(iniPath);
IniPatcher.SetKeyValue(iniPath, key, value);
File.WriteAllLines(stateFile, backups);  // 保存备份列表

// dev stop — 恢复
foreach (var bak in File.ReadAllLines(stateFile).Reverse())
    if (File.Exists(bak)) IniPatcher.Restore(bak);
```

## 相关文件

- `Infrastructure/Pm2Helper.cs` — PM2 安装检测、ecosystem 生成
- `Infrastructure/IniPatcher.cs` — INI 备份/恢复/补丁
- `Commands/Deploy/DeployLocalCommand.cs` — 参考实现
- `Commands/Dev/DevRunCommand.cs` — dev 环境 PM2 启动
- `Commands/Dev/DevStopCommand.cs` — dev 环境停止 + INI 恢复
