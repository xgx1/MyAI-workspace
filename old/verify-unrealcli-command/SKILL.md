---
name: verify-unrealcli-command
description: "Verify UnrealCli command: compilation, help output, docs consistency, runtime issues. Use when checking availability or debugging command problems."
---

# Verify UnrealCli Command

Checklist for verifying an UnrealCli command's correctness and availability.

## Steps

### 1. Compilation Check
```bash
dotnet build UnrealCli/UnrealCli.csproj
```
Must pass with 0 errors, 0 warnings.

### 2. Help Output
```bash
dotnet run --project UnrealCli/UnrealCli.csproj -- <command> --help
```
Verify command exists, options are documented, no short-option collisions.

### 3. Docs vs Code
Cross-reference `AGENTS.md` command tree against `Program.cs` registration (e.g., `dev run` vs `dev`). Any mismatch is a bug.

### 4. Deep Code Review
Check each referenced dependency:
- **Process spawning**: Is stderr consumed? If `RedirectStandardError = true` but no reader → deadlock risk.
- **Command-line args**: Are positional args semantically correct? (UE: first arg after `.uproject` is map name, not IP. Use `/Game/Map/Main?server={ip}` syntax.)
- **Build freshness**: Does `File.Exists()` suffice, or should timestamps / source hashes be compared?
- **Health checks**: After spawning dependent processes, are they verified as running before proceeding?
- **Short option collision**: Any custom `-h` conflicts with built-in `--help`.

### 5. Smoke Test (if project config exists)
```bash
dotnet run --project UnrealCli/UnrealCli.csproj -- <command> [--dry-run]
```
Must not throw on startup (config detection, path resolution).

## Patterns

### Log-based process readiness check
Replace `Task.Delay` with polling log files for known patterns. See `WaitForReadyAsync` in `DevRunCommand.cs`:
- .NET backend: `"Now listening on"` (30s timeout)
- UE Server: `"LogInit:"` in abslog (60s timeout)

### UE map + server URL syntax
```
"{projectFile}" /Game/Map/Main?server={host} -game -log ...
```
NOT: `{host}` as bare positional argument.

## Anti-Patterns (UnrealCli-specific)
- `ProcessStartInfo` with `RedirectStandardError = true` but no stderr consumer
- IP address passed as positional argument where UE expects map name
- Short option `-h` on custom options (collides with `--help`)
- Command name in docs differs from `AddCommand` / `AddBranch` registration
