---
name: unrealcli-global-tool-reinstall
description: UnrealCli 源码改动后重新打包并更新全局 dotnet tool（unrealcli 命令）的流程，含 TFM 升级检查点
---

# UnrealCli 全局工具重新注册

UnrealCli 以 dotnet global tool 形式安装（`PackAsTool=true`，`ToolCommandName=unrealcli`），本地源码改动后**必须重新打包并更新全局工具**，否则 PATH 里的 `unrealcli` 仍是旧版。

## 重新注册流程

```bash
cd C:/Users/Admin/Project/UnrealCli
dotnet pack UnrealCli/UnrealCli.csproj -c Release
dotnet tool update --global --add-source UnrealCli/bin/Release UnrealCli
```

- 首次安装用 `dotnet tool install --global --add-source UnrealCli/bin/Release UnrealCli`；已装过用 `update`。
- nupkg 输出在 `UnrealCli/bin/Release/UnrealCli.<version>.nupkg`；版本号在 csproj `<Version>`。
- 验证：换到其他目录执行 `where.exe unrealcli`（应指向 `%USERPROFILE%\.dotnet\tools\unrealcli.exe`）+ `unrealcli --help`。

## 升级 TFM 时的注意点

- 两个 csproj 都要改：主项目 + `UnrealCli.Tests`。
- `Commands/Deploy/DeployLocalCommand.cs` 里硬编码的 `net9.0` 是 **<ProjectServer> 后端**的 DLL 输出路径，不属于 UnrealCli 自身 TFM，不要顺手改。
- 升级后跑 `dotnet test UnrealCli.slnx -c Release` 验证（现有 11 个 xUnit 测试）。
