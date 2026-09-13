# dsh-extensions/skills 技能清单（自动生成）

- 生成时间：2026-09-13T09:25:28.455Z
- 命令约定：**Linux（本机 Arch）用 bash，Windows 用 PowerShell**

## 分组总览

| 分组 | 上游 | 技能数 | 可见 | 模型禁用 | YAML 坏 |
| --- | --- | --- | --- | --- | --- |
| `self-ue` | 自建（无上游） | 26 | 26 | 0 | 0 |
| `self-dsh` | 自建（无上游） | 5 | 5 | 0 | 0 |
| `self-ops` | 自建（无上游） | 7 | 7 | 0 | 0 |
| `dotnet-skills` | dotnet/skills | 98 | 93 | 5 | 0 |
| `mattpocock-skills` | mattpocock/skills | 33 | 33 | 0 | 0 |
| `obra-superpowers` | obra/superpowers | 21 | 21 | 0 | 0 |
| `dietrichgebert-ponytail` | DietrichGebert/ponytail | 6 | 6 | 0 | 0 |
| `quodsoler-unreal-engine-skills` | quodsoler/unreal-engine-skills | 30 | 30 | 0 | 0 |
| `rider-skills` | JetBrains/rider-skills | 6 | 6 | 0 | 0 |
| `epicgames-ue-skills` | EpicGames 官方 | 3 | 3 | 0 | 0 |
| `unrealxu-ue5-skills` | unrealxu/ue5-skills | 3 | 3 | 0 | 0 |
| `sipherxyz-universal-ue-skills` | sipherxyz/universal-ue-skills | 1 | 1 | 0 | 0 |
| `kepano-obsidian-skills` | kepano/obsidian-skills | 3 | 3 | 0 | 0 |
| `clawic-marketplace` | clawic/marketplace | 3 | 3 | 0 | 0 |

## 逐技能明细

### self-ue（自建（无上游），26 个）

| 技能 | 状态 | 说明 |
| --- | --- | --- |
| `unreal-blueprint-to-cpp-project` | 可见 | 把纯蓝图 UE 项目（无 Source/ 目录）转成 C++ 项目并编译烘焙：模块骨架、4 个 Target.cs、uproject 注册、清理 Intermediate/Source 残留，以及 Linux(bash) 与 Windows(PowerShell) 双平台的 Bu |
| `unreal-button-migration-checklist` | 可见 | UE 项目中将 UButton 迁移到自定义按钮基类（如 UXxxButtonBase）后的完整检查清单——C++、测试（含 UCommonButtonBase 反射/委托陷阱）、蓝图三层遗漏点与验证 |
| `unreal-cmd` | 可见 | Unreal Engine 命令行工具必用技能：UnrealEditor-Cmd（Linux/Windows 双平台）、Build.sh/Build.bat、RunUAT、AutomationTool、UE Python、截图、日志降噪/落盘、退出码，以及编译与热重载陷阱。 |
| `unreal-code-created-widget-pitfalls` | 可见 | UE 项目 C++ 代码动态创建 UMG/CommonUI 按钮与弹窗时的三个陷阱：RootWidget 绑定、AddToViewport、WidgetTree 守卫 |
| `unreal-commonui-button-dev` | 可见 | UMG buttons: Common UI plugin (UCommonButtonBase + UCommonButtonStyle), centralized styling, 7-state visuals, reusable architecture. |
| `unreal-create-project-starter-content` | 可见 | UE 5.7 创建新项目并添加 Starter Content（GUI 自动化 + UnrealPak 解包）时使用 |
| `unreal-dev-http` | 可见 | 必须在 Unreal 项目涉及后端 HTTP 服务、后端 API、REST API、HTTP endpoint 或客户端/服务器 HTTP 集成时调用。 |
| `unreal-editor-toolbar-button` | 可见 | When adding an editor UI test tool — project setting to reference a UMG widget, toolbar button next to Play, click to fullscreen preview |
| `unreal-featurepack-upack-rebuild` | 可见 | UE 引擎 FeaturePacks 目录缺失 .upack（如 StarterContent.upack）导致启动导入失败弹窗时，用 UnrealPak 从项目现有资产自制 upack 的完整流程。含响应文件格式、挂载点规则、注释行断言坑。 |
| `unreal-fix-simulatedproxy-teleport-interpolation` | 可见 | Fix SimulatedProxy smooth interpolation during teleport in UE5 multiplayer — add NetMulticast RPC to force all clients to snap position |
| `unreal-imc-mapping-verify` | 可见 | UE5 Enhanced Input / IMC 的验证与程序化修复（uasset 解析、C++ 契约测试、幂等迁移保存、冲突分流模式），含输入系统规范、UI 开关时的 IMC 生命周期、PICO 2D 复合键 Y 分量不交付的引擎 bug 绕法。 |
| `unreal-linux-cross-build-deploy` | 可见 | UE5 源码引擎交叉编译 Linux Server + unrealcli 部署：Linux v25 工具链、LINUX_MULTIARCH_ROOT、BuildConfiguration.xml/UBA、PM2 fork 崩循环、DB 缺表缺列、curl scp 绕拦截、ini |
| `unreal-module-build` | 可见 | Build.cs, Target.cs, module creation, plugin setup, build errors, unresolved external symbol, cannot open include file, IWYU, missing API ma |
| `unreal-monolithic-plugin-symbol-conflict` | 可见 | UE 单块链接（monolithic Game/Client/Server）LNK2005/ld.lld duplicate symbol 修复：同名符号冲突须 Target.cs 条件化 DisablePlugins；Editor 不报错、Cook Indeterminism  |
| `unreal-mrq-panorama-setup` | 可见 | UE 5.7 MRQ 全景录制+VR 回放（APanoramaViewer+MediaTexture，H.264）、VR 打包（OpenXR/cook 排除 MRQ）、无头 python、UnrealPak upack。触发：8K 渲染/渲染图报错/VR 打包。 |
| `unreal-multiplayer-replication-debug` | 可见 | UE 多人游戏组件状态/网格复制问题的诊断与修复模式——组件 bool 客户端本地设置第三方不可见（服务器权威 RPC）、公共入口副作用陷阱、环绕第三方同步（手动位置复制）、能量模式变色恢复（DefaultAxeMaterials 数组初始化） |
| `unreal-official-mcp-surgery` | 可见 | 在运行中的 UE 编辑器里用官方 ModelContextProtocol 工具集做资产/UMG 手术（改名/删控件/DataTable 行编辑/保存）与 UMG 交互 C++ 化的实战纪律。触发词：编辑器资产手术、MCP 改控件、RenameWidget、RemoveWidge |
| `unreal-project-context` | 可见 | Create/update Unreal Engine project context document. Trigger: 'project context', 'set up context', 'UE context', 'configure project'. |
| `unreal-skeletal-orbit-attack` | 可见 | UE 骨骼动画驱动的环绕攻击实现（飞轮/武器沿骨骼轨迹环绕目标）——载体 Tick 姿态锁定、手动位置同步跨端复制、StaticMesh CDO 网格陷阱 |
| `unreal-uasset-ref-scan` | 可见 | 删 UE uasset 前用 rg --text 扫二进制引用图判定删除安全性（含 _C 成对、typo twins、umap 不可判读等陷阱） |
| `unreal-umg-bindwidget-default` | 可见 | UE5 UMG 中 BindWidget 默认用必选，仅当明确说可选才用 Optional；按钮文本统一用 SetButtonText()；WBP 控件名与 C++ BindWidget 断链（按钮不存在/数据不更新/面板空）的诊断与修复流程 |
| `unreal-umg-item-button-wiring` | 可见 | Wire action buttons on UMG list item widgets (FriendListItem, EnemyListItem, etc.) with delegates, UFUNCTION handlers, and list-level event  |
| `unreal-unrealmcp-asset-surgery` | 可见 | UE 项目内 UnrealMCP 插件 TCP 协议 + 无头 python 对 .uasset 做控件树/蓝图/资产手术（端口/帧格式/参数名陷阱/reparent/强删） |
| `unreal-vr-button-click-fix` | 可见 | UE VR WidgetInteraction 按钮点击不可靠的完整修复模式——悬停冷却定时器桥接 Slate 振荡 + 可见性纠正 + SimulateClick 直点路径 |
| `unreal-vr-dialog-world-mounting` | 可见 | UE5 VR 头显中添加/修复 UMG 弹窗：AddToViewport 不可见，必须 AddChild 到世界空间面板根；含 outer 链、SetZOrder、UPROPERTY 防 GC、RemoveFromParent、SimulateClick、WidgetTree 守 |
| `unreal-vr-mouse-debug-click` | 可见 | VR/世界空间 UMG 的 PC 鼠标调试点击实现（射线 + WidgetInteraction CustomHitResult），含 InteractionSource=Custom 硬性前提与三轮实证陷阱 |

### self-dsh（自建（无上游），5 个）

| 技能 | 状态 | 说明 |
| --- | --- | --- |
| `browser-mcp-playwright` | 可见 | 浏览器 MCP（@playwright/mcp）实战纪律：快照循环、ref 过期、表单/上传/弹窗、诊断三件套、无头与登录态复用、配置与排障。触发词：操作浏览器、打开网页、网页自动化、抓页面内容、看接口返回、console 报错排查、Pixel Streaming 页面验证。 |
| `cbm-graph-first` | 可见 | 代码检索查图优先（graph-first）：找符号/定义、调用方、调用链、影响面、架构总览、复杂度热点、改动前侦察时，先用 codebase-memory MCP（cbm）查知识图谱，grep/glob 只做兜底。触发：在任何代码库里找代码、分析谁调用谁、评估改动影响、看模块边界 |
| `dotnet-backend-tdd` | 可见 | Write xUnit + EF Core TDD tests for .NET backend services against real relational databases — SQLite in-memory for fast unit tests, PostgreS |
| `dsh-extension-dev` | 可见 | DSH 功能扩展开发元技能（先搜索复用、无现成才自己写、写完传 GitHub）。触发词：扩展 DSH、DSH 插件、给 DSH 加功能、开发 DSH 扩展、DSH 扩展开发、DSH 功能扩展。四条规矩：①动手前先搜本地/网上现成扩展，大致符合就在其基础上改，禁止从零重写；②逐步实 |
| `unreal-editor-mcp-ops` | 可见 | 在运行中的虚幻编辑器里通过 MCP 操作时的决策与纪律：确定性工具优先、console/Python 次之、模拟点击是最后手段；含模拟点击五步流程、高频反模式、PIE 交互、与浏览器 MCP 的联动工作流（Remote Control / Pixel Streaming / 网页 |

### self-ops（自建（无上游），7 个）

| 技能 | 状态 | 说明 |
| --- | --- | --- |
| `aliyunpan-cli-setup-login` | 可见 | 安装/登录 tickstep/aliyunpan（阿里云盘 CLI）：scoop 无包需手动装、资产名 windows-x64、ghfast 镜像 + aria2、login 必须 pty 长驻（stdin EOF 会秒退报登录失败）、授权后按 Enter |
| `baidupcs-batch-pipeline` | 可见 | 百度网盘 BaiduPCS-Go 分批下载+按规则处理的多盘流水线：递归侦查、空间守卫、hub daemon 三步重启、zstd/格式坑、下载处理串行、询问文档模式 |
| `baidupcs-cli` | 可见 | 使用百度网盘 CLI（BaiduPCS-Go）时查阅：安装（Linux pacman / Windows scoop）、BDUSS 与 Cookie 登录、自动化扫码登录（含弹窗/抓图陷阱）、下载落盘结构、GBK 编码坑、命令速查、非 SVIP 并发限制、秒传已失效、备份档案窥探 |
| `local-git-archive-server` | 可见 | 本机 Git 归档服务器全流程：建 bare 仓库、高压缩配置、LFS 对象补全、双推（origin + local，含阿里云 Codeup 断连处理）、merge unrelated 历史、UE/Unity gitignore、fsck 验证后删本体滚动释放空间。合并自原 lo |
| `scanned-doc-ocr-extraction` | 可见 | 扫描型 PDF / 老 .doc 文档提取文本：pymupdf 导出页图 → inspect_image（DSH 原生视觉 OCR）；.doc 用 olefile + utf-16le 提取。处理扫描合同、扫描件、微信收到的旧文档时使用。 |
| `strip-cpp-comments` | 可见 | 批量移除 C++/C 源码中所有注释（// 与 /* */）的安全流程：词法状态机剥离、字符串字面量保护、备份、字节级重放验证、编译验证。用户要求"删除注释""移除注释""清空代码注释"时使用。 |
| `video-transcribe-cn-env` | 可见 | 中文视频（微信/会议 MP4）转文本对话稿：scoop python3、hf-mirror（Purfview turbo）、faster-whisper int8 转录、Silero VAD/SpeechBrain ECAPA 说话人分离、LLM 精简 |

### dotnet-skills（dotnet/skills，98 个）

| 技能 | 状态 | 说明 |
| --- | --- | --- |
| `analyzing-dotnet-performance` | 可见 | Scans .NET code for ~50 performance anti-patterns across async, memory, strings, collections, LINQ, regex, serialization, and I/O with tiere |
| `android-tombstone-symbolication` | 可见 | Symbolicate the .NET runtime frames in an Android tombstone file. Extracts BuildIds and PC offsets from the native backtrace, downloads debu |
| `apple-crash-symbolication` | 可见 | Symbolicate .NET runtime frames in Apple platform .ips crash logs (iOS, tvOS, Mac Catalyst, macOS). Extracts UUIDs and addresses from the na |
| `assertion-quality` | 可见 | Analyzes the variety and depth of assertions across test suites in any language. Use when the user asks to evaluate assertion quality, find  |
| `author-component` | 可见 | Create or review Blazor components (.razor files) with correct architecture. USE FOR: writing new Blazor components that do NOT involve Java |
| `binlog-failure-analysis` | 可见 | Analyze MSBuild binary logs to diagnose build failures. USE FOR: build errors that are unclear from console output, diagnosing cascading fai |
| `binlog-generation` | 可见 | Generate MSBuild binary logs (binlogs) for build diagnostics and analysis. USE FOR: adding /bl:{} to any dotnet build, test, pack, publish,  |
| `build-parallelism` | 可见 | Guide for optimizing MSBuild build parallelism and multi-project scheduling. USE FOR: builds not utilizing all CPU cores, speeding up multi- |
| `build-perf-baseline` | 可见 | Establish build performance baselines and apply systematic optimization techniques. USE FOR: diagnosing slow builds, establishing before/aft |
| `build-perf-diagnostics` | 可见 | Diagnose MSBuild build performance bottlenecks using binary log analysis. USE FOR: identifying why builds are slow by analyzing binlog perfo |
| `check-bin-obj-clash` | 可见 | Detects MSBuild projects with conflicting OutputPath or IntermediateOutputPath. USE FOR: builds failing with 'Cannot create a file when that |
| `clr-activation-debugging` | 可见 | Diagnoses .NET Framework CLR activation issues using CLR activation logs (CLRLoad logs) produced by mscoree.dll. Use when: the shim picks th |
| `code-testing-agent` | 可见 | Generates and writes new unit tests for any programming language — scaffolds test projects and configures coverage tooling (coverlet, pytest |
| `code-testing-extensions` | 模型禁用 | Provides file paths to language-specific extension files for the code-testing pipeline. Call this skill to discover available extension guid |
| `collect-user-input` | 可见 | Build forms, validate data, and react to user input in Blazor. USE FOR adding forms, search boxes, filter panels, inline editing, data-entry |
| `configure-auth` | 可见 | Add authentication and authorization to a Blazor Web App, accounting for the app's render mode. USE WHEN the user needs [Authorize] on pages |
| `configuring-opentelemetry-dotnet` | 可见 | Configure OpenTelemetry distributed tracing, metrics, and logging in ASP.NET Core using the .NET OpenTelemetry SDK. Use when adding observab |
| `convert-blazor-server-to-webapp` | 可见 | Guides conversion of a pre-.NET 8 Blazor Server app into a .NET 8+ Blazor Web App. USE FOR: migrating apps that use AddServerSideBlazor and  |
| `convert-to-cpm` | 可见 | Convert .NET projects and solutions (.sln, .slnx) to NuGet Central Package Management (CPM) using Directory.Packages.props. USE FOR: convert |
| `coordinate-components` | 可见 | Share state between components that don't have a direct parent-child parameter relationship, using cascading values, scoped services with ch |
| `coverage-analysis` | 可见 | Project-wide code coverage and CRAP (Change Risk Anti-Patterns) score analysis for .NET projects. Calculates CRAP scores per method and surf |
| `crap-score` | 可见 | Calculates targeted CRAP (Change Risk Anti-Patterns) scores for a named .NET method, class, or single source file. Use when the user explici |
| `create-blazor-project` | 可见 | Create a new ASP.NET Core web application or web site using Blazor. USE FOR: creating a new Blazor web app, scaffolding a new web project, s |
| `csharp-scripts` | 可见 | Run file-based C# apps with the .NET CLI when the user explicitly wants C#/.NET code without creating a project. Use for C# language/API exp |
| `detect-static-dependencies` | 可见 | Scan C# source files for hard-to-test static dependencies — DateTime.Now/UtcNow, File.*, Directory.*, Environment.*, HttpClient, Console.*,  |
| `directory-build-organization` | 可见 | Guide for organizing MSBuild infrastructure with Directory.Build.props, Directory.Build.targets, Directory.Packages.props, and Directory.Bui |
| `dotnet-aot-compat` | 可见 | Make .NET projects compatible with Native AOT and trimming by systematically resolving IL trim/AOT analyzer warnings. USE FOR: making projec |
| `dotnet-maui-doctor` | 可见 | Diagnoses and fixes .NET MAUI development environment issues. Validates .NET SDK, workloads, Java JDK, Android SDK, Xcode, and Windows SDK.  |
| `dotnet-pinvoke` | 可见 | Correctly call native (C/C++) libraries from .NET using P/Invoke and LibraryImport. Covers function signatures, string marshalling, memory l |
| `dotnet-trace-collect` | 可见 | Guide developers through capturing diagnostic artifacts to diagnose production .NET performance issues. Use when the user needs help choosin |
| `dotnet-webapi` | 可见 | Guides creation and modification of ASP.NET Core Web API endpoints with correct HTTP semantics, OpenAPI metadata, and error handling. USE FO |
| `dump-collect` | 可见 | Configure and collect crash dumps for modern .NET applications. USE FOR: enabling automatic crash dumps for CoreCLR or NativeAOT, capturing  |
| `eval-performance` | 可见 | Guide for diagnosing and improving MSBuild project evaluation performance. USE FOR: builds slow before any compilation starts, high evaluati |
| `exp-mock-usage-analysis` | 可见 | Audits .NET test mock usage by tracing each mock setup through the production code's execution path to find dead, unreachable, redundant, or |
| `exp-simd-vectorization` | 可见 | Optimizes hot-path scalar loops in .NET 8+ with cross-platform Vector128/Vector256/Vector512 SIMD intrinsics, or replaces manual math loops  |
| `exp-test-maintainability` | 可见 | Detects duplicate boilerplate, copy-paste tests, and structural maintainability issues across .NET test suites. Use when the user asks to re |
| `extension-points` | 可见 | Guide for MSBuild extensibility: CustomBefore/CustomAfter hooks, wildcard imports with alphabetic ordering, import gating with control prope |
| `fetch-and-send-data` | 可见 | Call APIs, load data into components, and handle the async lifecycle in Blazor. USE FOR fetching data from a backend, submitting data to an  |
| `filter-syntax` | 模型禁用 | Reference data for test filter syntax across all platform and framework combinations: VSTest --filter expressions, MTP filters for MSTest/NU |
| `find-untested-sources` | 模型禁用 | Parse-only static analysis that pairs source files with the tests referencing them and emits JSON listing untested files ordered by API surf |
| `generate-testability-wrappers` | 可见 | Generate wrapper interfaces and DI registration for hard-to-test static dependencies in C#, when the abstraction does NOT exist yet. Produce |
| `grade-tests` | 可见 | Grades a specified set of test methods individually and produces a concise table mapping each test (fully-qualified name) to a letter grade  |
| `including-generated-files` | 可见 | Fix MSBuild targets that generate files during the build but those files are missing from compilation or output. USE FOR: generated source f |
| `incremental-build` | 可见 | Guide for optimizing MSBuild incremental builds. USE FOR: builds slower than expected on subsequent runs, 'nothing changed but it rebuilds a |
| `item-management` | 可见 | Patterns for managing MSBuild item groups: Include/Remove/Update semantics, item metadata, batching with %(Metadata), transforms, per-item f |
| `maui-app-lifecycle` | 可见 | .NET MAUI app lifecycle guidance — the four app states, cross-platform Window lifecycle events (Created, Activated, Deactivated, Stopped, Re |
| `maui-collectionview` | 可见 | Guidance for implementing CollectionView in .NET MAUI apps — data display, layouts (list & grid), selection, grouping, scrolling, empty view |
| `maui-data-binding` | 可见 | Guidance for .NET MAUI XAML and C# data bindings — compiled bindings, INotifyPropertyChanged / ObservableObject, value converters, binding m |
| `maui-dependency-injection` | 可见 | Guidance for configuring dependency injection in .NET MAUI apps — service registration in MauiProgram.cs, lifetime selection (Singleton / Tr |
| `maui-safe-area` | 可见 | .NET MAUI safe area and edge-to-edge layout guidance for .NET 10+. Covers the new SafeAreaEdges property, SafeAreaRegions enum, per-edge con |
| `maui-shell-navigation` | 可见 | Guide for implementing Shell-based navigation in .NET MAUI apps. Covers AppShell setup, visual hierarchy (FlyoutItem, TabBar, Tab, ShellCont |
| `maui-theming` | 可见 | Guide for theming .NET MAUI apps — light/dark mode via AppThemeBinding, ResourceDictionary theme switching, DynamicResource bindings, system |
| `mcp-csharp-create` | 可见 | Create MCP servers using the C# SDK and .NET project templates. Covers scaffolding, tool/prompt/resource implementation, and transport confi |
| `mcp-csharp-debug` | 可见 | Run and debug C# MCP servers locally. Covers IDE configuration, MCP Inspector testing, GitHub Copilot Agent Mode integration, logging setup, |
| `mcp-csharp-publish` | 可见 | Publish and deploy C# MCP servers. Covers NuGet packaging for stdio servers, Docker containerization for HTTP servers, Azure Container Apps  |
| `mcp-csharp-test` | 可见 | Test C# MCP servers at multiple levels: unit tests for individual tools and integration tests using the MCP client SDK. USE FOR: unit testin |
| `microbenchmarking` | 可见 | Activate this skill when BenchmarkDotNet (BDN) is involved in the task — creating, running, configuring, or reviewing BDN benchmarks. Also a |
| `migrate-dotnet10-to-dotnet11` | 可见 | Migrate a .NET 10 project or solution to .NET 11 and resolve all breaking changes. This is a MIGRATION skill — use it when upgrading from .N |
| `migrate-dotnet8-to-dotnet9` | 可见 | Migrate a .NET 8 project to .NET 9 and resolve all breaking changes. USE FOR: upgrading TargetFramework from net8.0 to net9.0, fixing build  |
| `migrate-dotnet9-to-dotnet10` | 可见 | Migrate a .NET 9 project or solution to .NET 10 and resolve all breaking changes. USE FOR: upgrading TargetFramework from net9.0 to net10.0, |
| `migrate-mstest-v1v2-to-v3` | 可见 | Migrate MSTest v1 or v2 test project to MSTest v3. Use when user says "upgrade MSTest", "upgrade to MSTest v3", "migrate to MSTest v3", "upd |
| `migrate-mstest-v3-to-v4` | 可见 | Fix build errors and breaking changes after upgrading MSTest from v3 to v4, or plan a complete MSTest v3-to-v4 migration. Use when user says |
| `migrate-nullable-references` | 可见 | Enable nullable reference types in a C# project and systematically resolve all warnings. USE FOR: adopting NRTs in existing codebases, file- |
| `migrate-static-to-wrapper` | 可见 | Replace existing static dependency call sites with wrapper or built-in abstraction calls when the abstraction already exists or is already r |
| `migrate-vstest-to-mtp` | 可见 | Migrates .NET test projects from VSTest to Microsoft.Testing.Platform (MTP). Use when user asks to "migrate to MTP", "switch from VSTest", " |
| `migrate-xunit-to-mstest` | 可见 | Migrate .NET test projects from xUnit.net (v2 or v3) to MSTest v4. USE FOR: convert/migrate xUnit tests to MSTest, replace xunit/xunit.v3 pa |
| `migrate-xunit-to-xunit-v3` | 可见 | Migrates .NET test projects from xUnit.net v2 to xUnit.net v3. USE FOR: upgrading xunit to xunit.v3. DO NOT USE FOR: migrating between test  |
| `minimal-api-file-upload` | 可见 | File upload endpoints in ASP.NET minimal APIs (.NET 8+) |
| `msbuild-antipatterns` | 可见 | Catalog of MSBuild anti-patterns with detection rules and fix recipes. USE FOR: reviewing, auditing, or cleaning up .csproj, .vbproj, .fspro |
| `msbuild-modernization` | 可见 | Guide for modernizing and migrating MSBuild project files to SDK-style format. USE FOR: converting legacy .csproj/.vbproj with verbose XML t |
| `msbuild-server` | 可见 | Guide for using MSBuild Server to improve CLI build performance. Activate when developers report slow incremental builds from the command li |
| `mtp-hot-reload` | 可见 | Suggests using Microsoft Testing Platform (MTP) hot reload to iterate fixes on failing tests without rebuilding. Use when user says "hot rel |
| `nuget-trusted-publishing` | 可见 | Set up NuGet trusted publishing (OIDC) on a GitHub Actions repo — replaces long-lived API keys with short-lived tokens. USE FOR: trusted pub |
| `optimizing-ef-core-queries` | 可见 | Optimize Entity Framework Core queries by fixing N+1 problems, choosing correct tracking modes, using compiled queries, and avoiding common  |
| `plan-ui-change` | 可见 | Plan complex Blazor UI features by decomposing them into focused components. USE FOR: building a complex Blazor page with multiple sections, |
| `platform-detection` | 模型禁用 | Reference data for detecting the test platform (VSTest vs Microsoft.Testing.Platform) and test framework (MSTest, xUnit, NUnit, TUnit) from  |
| `property-patterns` | 可见 | MSBuild property definition patterns: conditional defaults, composition/concatenation, path normalization, trailing slash handling, TFM dete |
| `resolve-project-references` | 可见 | Guide for interpreting ResolveProjectReferences time in MSBuild performance summaries. Activate when ResolveProjectReferences appears as the |
| `run-tests` | 可见 | Recommend or run the exact `dotnet test` command. ALWAYS use when the user asks to run, filter, or troubleshoot .NET tests or wants the prec |
| `setup-local-sdk` | 可见 | Install a .NET SDK locally for safe preview testing, specific-version pinning, or reproducible team setups — without modifying the system-wi |
| `support-prerendering` | 可见 | Make interactive Blazor components work correctly with prerendering. USE FOR fixing duplicate data loads, UI flicker during prerender-to-int |
| `system-text-json-net11` | 可见 | Provides guidance on new System.Text.Json APIs introduced in .NET 11. It covers typed JsonTypeInfo access via GetTypeInfo<T> and TryGetTypeI |
| `target-authoring` | 可见 | Canonical patterns for writing custom MSBuild targets. USE FOR: diagnosing and fixing custom target authoring anti-patterns, reviewing MSBui |
| `technology-selection` | 可见 | Guides technology selection and implementation of AI and ML features in .NET 8+ applications using ML.NET, Microsoft.Extensions.AI (MEAI), M |
| `template-authoring` | 可见 | Guides creation and validation of custom dotnet new templates. Generates templates from existing projects and validates template.json for au |
| `template-comparison` | 可见 | Compares two or more dotnet new templates side by side to help users choose between them based on parameters, feature support, frameworks, a |
| `template-discovery` | 可见 | Helps find, inspect, and compare .NET project templates. Resolves natural-language project descriptions to ranked template matches with pre- |
| `template-instantiation` | 可见 | Creates .NET projects from templates with validated parameters, smart defaults, Central Package Management adaptation, and latest NuGet vers |
| `template-smart-defaults` | 可见 | Applies cross-parameter default rules when creating .NET projects with dotnet new, filling gaps consistently without overriding values the u |
| `template-validation` | 可见 | Validates custom dotnet new templates for correctness before publishing. Catches missing fields, parameter bugs, shortName conflicts, constr |
| `test-analysis-extensions` | 模型禁用 | Provides file paths to language-specific reference files for the test ANALYSIS skills (assertion-quality, test-anti-patterns, test-gap-analy |
| `test-anti-patterns` | 可见 | Audits an existing test file or suite in any language for anti-patterns and quality issues — produces a severity-ranked report (Critical/War |
| `test-gap-analysis` | 可见 | Performs pseudo-mutation analysis on production code in any language to find gaps in existing tests. Use when the user asks to find weak or  |
| `test-smell-detection` | 可见 | Deep-dive audit using the full testsmells.org 19-smell academic catalog for tests in any language. Every finding maps to a named, citable sm |
| `test-tagging` | 可见 | Analyzes test suites in any language and tags each test with standardized traits (positive, negative, critical-path, boundary, smoke, regres |
| `thread-abort-migration` | 可见 | Guides migration of .NET Framework Thread.Abort usage to cooperative cancellation in modern .NET. USE FOR: modernizing code that calls Threa |
| `use-js-interop` | 可见 | Add, review, or fix JavaScript interop in Blazor components. USE FOR: calling JavaScript from Blazor, calling .NET from JavaScript, collocat |
| `writing-mstest-tests` | 可见 | Write, create, modernize, or fix comprehensive MSTest unit tests with MSTest 3.x/4.x APIs. USE FOR: write, create, review, or modernize MSTe |

### mattpocock-skills（mattpocock/skills，33 个）

| 技能 | 状态 | 说明 |
| --- | --- | --- |
| `ask-matt` | 可见 | Ask which skill or flow fits your situation. A router over the skills in this repo. |
| `claude-handoff` | 可见 | Hand the current conversation off to a fresh background agent that picks up the work immediately. |
| `code-review` | 可见 | Review the changes since a fixed point (commit, branch, tag, or merge-base) along two axes: Standards (does the code follow this repo's docu |
| `codebase-design` | 可见 | Shared vocabulary for designing deep modules. Use when the user wants to design or improve a module's interface, find deepening opportunitie |
| `diagnosing-bugs` | 可见 | Diagnosis loop for hard bugs and performance regressions. Use when the user says "diagnose"/"debug this", or reports something broken/throwi |
| `domain-modeling` | 可见 | Build and sharpen a project's domain model. Use when discussing codebase terminology, writing or editing a CONTEXT.md, or recording or editi |
| `grill-me` | 可见 | A relentless interview to sharpen a plan or design. |
| `grill-with-docs` | 可见 | 需求门禁（写代码前必经）：用户提出任何需求、功能、想法、方案、改动时，先用多轮追问把需求拷问清楚，并随手沉淀 ADR 与术语表（CONTEXT.md/glossary），再进入实现。触发词：提需求、新需求、新功能、加个功能、加功能、做个功能、做需求、我想做、我想要、帮我实现、实现 |
| `grilling` | 可见 | Grill the user relentlessly about a plan, decision, or idea. Use when the user wants to stress-test their thinking, or uses any 'grill' trig |
| `handoff` | 可见 | Compact the current conversation into a handoff document for another agent to pick up. |
| `implement` | 可见 | Implement a piece of work based on a spec or set of tickets. |
| `implement-spec` | 可见 | Implement a specification in code. |
| `improve-codebase-architecture` | 可见 | Scan a codebase for deepening opportunities, present them as a visual HTML report, then grill through whichever one you pick. |
| `loop-me` | 可见 | Grill me about specs for the workflows I want to build, within this workspace. |
| `prototype` | 可见 | Build a throwaway prototype to answer a design question. Use when the user wants to sanity-check whether a state model or logic feels right, |
| `research` | 可见 | Investigate a question against high-trust primary sources and capture the findings as a Markdown file in the repo. Use when the user wants a |
| `resolving-merge-conflicts` | 可见 | Use when you need to resolve an in-progress git merge/rebase conflict. |
| `retro` | 可见 | Conduct a retrospective on a coding session. |
| `setup-matt-pocock-skills` | 可见 | Configure this repo for the engineering skills: set up its issue tracker, triage label vocabulary, and domain doc layout. Run once before fi |
| `setup-ts-deep-modules` | 可见 | Wire dependency-cruiser into a TypeScript repo so each package is a deep module, with implementation hidden in subfolders and reachable only |
| `tdd` | 可见 | Test-driven development. Use when the user wants to build features or fix bugs test-first, mentions "red-green-refactor", or wants integrati |
| `teach` | 可见 | Teach the user a new skill or concept, within this workspace. |
| `to-questionnaire` | 可见 | Turn a decision you can't fully answer into a questionnaire for someone else to fill in. |
| `to-spec` | 可见 | Turn the current conversation into a spec and publish it to the project issue tracker: no interview, just synthesis of what you've already d |
| `to-tickets` | 可见 | Break a plan, spec, or the current conversation into a set of tracer-bullet tickets, each declaring its blocking edges, published to the con |
| `triage` | 可见 | Move issues and external PRs through a state machine of triage roles, categorise, verify, grill if needed, and write agent-ready briefs. |
| `wait-what` | 可见 | Stop. That last message did not land: re-pitch it. |
| `wayfinder` | 可见 | Plan a huge chunk of work (more than one agent session can hold) as a shared map of decision tickets on your issue tracker, and resolve them |
| `wizard` | 可见 | Generate an interactive bash wizard that walks a human through steps only they can perform. Use when provisioning infrastructure, setting up |
| `writing-beats` | 可见 | Writing, exploit; assemble raw material into a journey of beats, grounding each term before a beat leans on it. |
| `writing-for-agents` | 可见 | Writing documents for agents. Use when creating or editing skills, or modifying AGENTS.md or CLAUDE.md. |
| `writing-fragments` | 可见 | Writing, explore: mine raw fragments, no structure yet. |
| `writing-shape` | 可见 | Writing, exploit: shape raw material into an article, paragraph by paragraph. |

### obra-superpowers（obra/superpowers，21 个）

| 技能 | 状态 | 说明 |
| --- | --- | --- |
| `add-software-feature` | 可见 | Add software feature / "add X feature" "implement Y" "create Z module". 17-phase dev workflow for UE5 + .NET. 大型功能（跨子系统/5+文件/新系统）编排；中小改动轻量流。 |
| `cleanup-worktrees` | 可见 | 清理所有 git worktree 和对应分支。当用户说"清理worktree"、"移除所有worktree"、"合并worktree"时使用。 |
| `compile-feature` | 可见 | Compile project after code changes (编译/构建/build): runs unrealcli dev complic, fixes all compilation errors and warnings. |
| `dev-docs` | 可见 | Obsidian 排版格式规范（禁序号、wikilink、callout、frontmatter、目录结构），写 Docs/ 下文档时作为格式约束；只管排版，功能文档内容由 writing-functional-docs 负责。 |
| `execute-feature-plan` | 可见 | Execute an implementation plan with independent tasks (执行计划/开始实现/并行执行): auto-dispatches subagent-driven-development without asking execution |
| `feature-inventory-docs-first` | 可见 | 功能盘点→行为文档→新功能设计→审核→计划的文档先行工作流 |
| `fix-feature-issues` | 可见 | 修复测试中发现的问题/用户反馈："修复问题"/"修bug"/"处理反馈"。读取反馈文档与 UnrealCli 日志，运行 diagnose + systematic-debugging。 |
| `git-merge-cleanup` | 可见 | 合并当前分支到主分支、推送、删除当前分支的完整工作流。当用户说"合并到主分支"、"merge to main"、"合入并删除分支"时使用。 |
| `init-feature-dev` | 可见 | Start a new development session (初始化开发环境/开始新功能开发): sets up skills, issue tracker, triage labels, domain docs, then runs brainstorming and gr |
| `make-feature-plan` | 可见 | 创建实现计划、生成 TODO 清单："制定计划"/"生成实现方案"/"做TODO清单"。运行 writing-plans、grill-with-docs、brainstorming 迭代至计划清晰。 |
| `optimize-feature-code` | 可见 | Optimize code for minimalism / remove over-engineering. Triggers: "优化代码", "极简化", "ponytail优化". Runs ponytail → ponytail-debt → ponytail-revi |
| `review-feature-code` | 可见 | 代码审查/代码质量 review：Standards + Spec 双轴。Runs code-review on current changes. Triggers: 代码审查, review代码, 审查一下. |
| `sdd-no-git-adaptation` | 可见 | 非 git 仓库环境执行 subagent-driven-development（SDD）的适配流程：sdd-workspace/task-brief/review-package 脚本全依赖 git 会挂，需手工提取 brief、reviewer 直接读文件核对、ledger  |
| `solidify-feature-lessons` | 可见 | Use when completing a feature or user says 记录经验/固化知识/更新AGENTS. Persists lessons to memory, solidifies techniques as skills, updates AGENTS.m |
| `summarize-feature-work` | 可见 | 生成开发总结/post-mortem doc：what was done, changed, generated, learned. Obsidian-formatted. Triggers: 生成总结, 写开发总结, 做了什么总结. |
| `tdd-test-feature` | 可见 | Use when running tests after code changes or user says 跑测试/TDD测试/验证测试. Runs test-driven-development suite, cleans up outdated test cases. |
| `tdd-write-feature` | 可见 | TDD 编写：红-绿-重构 test-first。Runs test-driven-development, cleans up outdated tests. Triggers: TDD编写, 先写测试再写代码. |
| `update-manual-test-doc` | 可见 | Update test docs after bug fixes (更新测试文档/更新QA文档): list what changed and what needs re-testing. |
| `write-feature-docs` | 可见 | 编写功能文档/设计文档：Obsidian 格式 Docs/ 下，用 dev-docs + obsidian-cli-full。Triggers: 编写功能文档, 写设计文档, 更新文档. |
| `write-manual-test-doc` | 可见 | Create manual test documentation for QA/developers. Triggers: "写测试文档", "人工测试文档", "QA测试指南". Produces Obsidian doc: test features, procedures, |
| `writing-functional-docs` | 可见 | 编写玩家/用户视角功能文档（操作→效果）from existing codebase：UE IMC dumps、缺陷排队、并行子 agent。Triggers: 编写功能文档, 行为说明书, 操作效果文档, functional docs from code。排版用 dev-do |

### dietrichgebert-ponytail（DietrichGebert/ponytail，6 个）

| 技能 | 状态 | 说明 |
| --- | --- | --- |
| `ponytail` | 可见 | Forces the laziest solution that actually works, simplest, shortest, most minimal. Channels a senior dev who has seen everything: question w |
| `ponytail-audit` | 可见 | Whole-repo audit for over-engineering. Like ponytail-review, but scans the entire codebase instead of a diff: a ranked list of what to delet |
| `ponytail-debt` | 可见 | Harvest every `ponytail:` comment in the codebase into a debt ledger, so the deliberate shortcuts and deferrals ponytail leaves behind get t |
| `ponytail-gain` | 可见 | Show ponytail's measured impact as a compact scoreboard: less code, less cost, more speed, from the benchmark medians. One-shot display, not |
| `ponytail-help` | 可见 | Quick-reference card for all ponytail modes, skills, and commands. One-shot display, not a persistent mode. Trigger: /ponytail-help, "ponyta |
| `ponytail-review` | 可见 | Code review focused exclusively on over-engineering. Finds what to delete: reinvented standard library, unneeded dependencies, speculative a |

### quodsoler-unreal-engine-skills（quodsoler/unreal-engine-skills，30 个）

| 技能 | 状态 | 说明 |
| --- | --- | --- |
| `unreal-actor-component-architecture` | 可见 | Actor/component composition, lifecycle, spawning, attachment, composition-over-inheritance. Trigger: AActor/UActorComponent design or lifecy |
| `unreal-ai-navigation` | 可见 | Unreal AI navigation: AIController, behavior tree, blackboard, AI perception, NavMesh, EQS, pathfinding, State Tree, Smart Objects. |
| `unreal-animation-system` | 可见 | Unreal animation: AnimInstance, montage playback, blend space, state machine, anim notify, IK, AnimGraph, skeletal mesh, linked anim graphs. |
| `unreal-async-threading` | 可见 | Unreal async tasks, threading, task systems, thread-safety: UE::Tasks, Async(), ParallelFor, futures, locks, game-thread ownership bugs. |
| `unreal-audio-system` | 可见 | Unreal audio: sound, music, UAudioComponent, PlaySoundAtLocation, SoundCue, MetaSound, attenuation, submix, concurrency, SFX, spatial audio. |
| `unreal-character-movement` | 可见 | Unreal character movement: CharacterMovementComponent, CMC, walk/fall/swim/fly, network prediction, FSavedMove, root motion, floor detection |
| `unreal-common-ui` | 可见 | CommonUI and CommonInput for Unreal menus and gamepad-first flows: activatable widgets, button styles, screen stacks, back handling, input r |
| `unreal-cpp-foundations` | 可见 | Unreal C++ reflection, containers, delegates, strings, GC, subsystem foundations. UCLASS/UPROPERTY, TObjectPtr, UE_LOG, core UE C++ patterns |
| `unreal-data-assets-tables` | 可见 | DataAsset, DataTable, soft/hard reference, TSoftObjectPtr, async loading, Asset Manager, StreamableManager, game data structures in Unreal E |
| `unreal-editor-tools` | 可见 | Unreal Editor extensions, menus, toolbars, detail customization, editor modes, Blutilities, editor utility workflows, custom editor UX. |
| `unreal-game-features` | 可见 | GameFeatureAction/Data, GameFrameworkComponentManager, init state, experience, modular components, UPawn/UController/UGameState/UPlayerState |
| `unreal-gameplay-abilities` | 可见 | GAS / Gameplay Ability System: GameplayAbility, GameplayEffect, AttributeSet, GameplayTags, ability system, buffs, debuffs, cooldowns, attri |
| `unreal-gameplay-framework` | 可见 | Unreal Engine gameplay framework classes: GameMode, GameState, PlayerController, PlayerState, Pawn, Character, GameInstance. |
| `unreal-input-system` | 可见 | Enhanced Input, gameplay input mapping in Unreal: InputAction, InputMappingContext, triggers, modifiers, gamepad, keyboard, input binding se |
| `unreal-mass-entity` | 可见 | MassEntity, MassProcessor, MassFragment, MassTag, MassObserver, MassSpawner, MassCrowd, Mass ECS, FMassEntityQuery, FMassEntityManager, ISM  |
| `unreal-materials-rendering` | 可见 | Material, shader, MID, dynamic material, material instance, post-process, render target, parameter collection, decal, Nanite, Lumen, or rend |
| `unreal-networking-replication` | 可见 | Multiplayer networking, replication, RPC calls, net role logic, server/client authority, prediction, synchronizing game state. |
| `unreal-niagara-effects` | 可见 | Use this skill when working with Niagara particle systems, VFX, effects, emitter, Niagara component, or Niagara parameter in Unreal Engine C |
| `unreal-physics-collision` | 可见 | Collision/physics/trace in Unreal. Triggers: 'LineTrace','overlap','sweep','collision channel','physics body','Chaos','raytrace','OnHit','On |
| `unreal-procedural-generation` | 可见 | Unreal procedural generation: PCG framework, ProceduralMesh, instanced mesh, HISM, spline, runtime mesh, noise, terrain, dungeon generation. |
| `unreal-sequencer-cinematics` | 可见 | Sequencer, LevelSequence, cutscene, cinematic, camera, movie scene, sequencer event, or Movie Render Queue in Unreal Engine. |
| `unreal-serialization-savegames` | 可见 | USaveGame save/load, player progress persistence, FArchive serialization. NOT for UGameUserSettings, UDeveloperSettings, config/game setting |
| `unreal-state-trees` | 可见 | State Tree, UStateTree, StateTreeTask/Condition/Evaluator, StateTreeSchema, AI/Mass State Tree, FStateTreeExecutionContext, data-driven stat |
| `unreal-testing-debugging` | 可见 | Unreal tests: UE_LOG, logging, log categories, assertion, check, ensure, verify, DrawDebug, debug draw, console command, profiling, Unreal I |
| `unreal-umg-binding` | 可见 | BindWidget contracts between C++ and Widget Blueprints: name matching, optional/animation bindings, missing-control compile errors. |
| `unreal-umg-input` | 可见 | UMG focus, cursor visibility, input-mode ownership: FInputMode setup, keyboard focus, game/UI transitions, non-CommonUI navigation bugs. |
| `unreal-umg-lifecycle` | 可见 | UUserWidget lifecycle: construction, teardown, viewport attachment, GC. Widget creation/removal/persistence, duplicate-instance bugs in Unre |
| `unreal-umg-lists` | 可见 | UListView, UTileView, entry widget virtualization in Unreal UMG: list population, entry refresh, selection, scrolling, IUserObjectListEntry. |
| `unreal-umg-mvvm` | 可见 | UE5 MVVM and event-driven UI data flow for Unreal: ViewModels, FieldNotify, push-based refresh, separating gameplay state from widget state. |
| `unreal-world-level-streaming` | 可见 | World Partition, level streaming/travel, OpenLevel, ServerTravel, data layer, world subsystem, level instance, sub-level, seamless travel, o |

### rider-skills（JetBrains/rider-skills，6 个）

| 技能 | 状态 | 说明 |
| --- | --- | --- |
| `debugging-code` | 可见 | Use for debugger-driven runtime root-cause analysis in Rider-supported solutions and projects, including .NET/C#, F#, VB, C++, Unity, Unreal |
| `finding-tests` | 可见 | Locates existing tests for a given C# class and method using the test coverage data supplied by IDE. Triggers ONLY for C# production code (` |
| `refactoring-code` | 可见 | Use when semantic refactoring is needed in Rider-supported solutions and projects, including .NET/C#, F#, VB, C++, Unity, Unreal Engine, XAM |
| `unreal-code-authoring` | 可见 | Use when writing or modifying Unreal Engine C++ — classes, actors, components, subsystems, interfaces, ability-system (GAS) code, module dep |
| `unreal-live-debugging` | 可见 | Use when debugging UE C++ crashes, runtime bugs, or unexpected behavior with Rider MCP available. Value over bash/grep: analyze_calls traces |
| `unreal-test-authoring` | 可见 | Use when writing or modifying Unreal Engine automated tests — Automation (IMPLEMENT_SIMPLE_AUTOMATION_TEST, DEFINE_SPEC), CQTest, Functional |

### epicgames-ue-skills（EpicGames 官方，3 个）

| 技能 | 状态 | 说明 |
| --- | --- | --- |
| `create-toolset` | 可见 | Authoring or extending an Unreal Engine toolset: static AI-callable functions registered with ToolsetRegistry, exposed through the unreal-mc |
| `unreal-mcp` | 可见 | Live-editor MCP actions in Unreal Engine (unreal-mcp): change, query, or run project state. Not for conceptual or docs questions. |
| `unreal-skill` | 可见 | Create, edit, or review Unreal Engine Agent Skill: named instruction bundle registered with unreal-mcp server (distinct from Claude Code har |

### unrealxu-ue5-skills（unrealxu/ue5-skills，3 个）

| 技能 | 状态 | 说明 |
| --- | --- | --- |
| `unreal-auto-assistant` | 可见 | UE5.6/5.7 assistant entry: Unreal question without named skill → auto-route to most precise UE5 skill + dedicated MCP tools. |
| `unreal-blueprint-workflow` | 可见 | UE5.6/UE5.7 Blueprint graph workflow: input events, node wiring, graph validation, keyboard input, function chains, event graph edits, pin w |
| `unreal-module-router` | 可见 | Route UE5.6/5.7 questions to most precise skill via module names, aliases, intent keywords, layer context (RenderCore, AIModule, AssetRegist |

### sipherxyz-universal-ue-skills（sipherxyz/universal-ue-skills，1 个）

| 技能 | 状态 | 说明 |
| --- | --- | --- |
| `unreal-run-automation-tests` | 可见 | 运行 UE 自动化测试的正确方式——必须带 -unattended 旗标，结果从 Saved/Logs 解析，含 fixture 陷阱 |

### kepano-obsidian-skills（kepano/obsidian-skills，3 个）

| 技能 | 状态 | 说明 |
| --- | --- | --- |
| `json-canvas` | 可见 | Create/edit JSON Canvas (.canvas): nodes, edges, groups, connections. For .canvas files, mind maps, flowcharts, or Canvas in Obsidian. |
| `obsidian-cli` | 可见 | Interact with Obsidian vaults using the Obsidian CLI to read, create, search, and manage notes, tasks, properties, and more. |
| `obsidian-markdown` | 可见 | Create/edit Obsidian Flavored Markdown: wikilinks, embeds, callouts, properties, frontmatter, tags. Use with .md files in Obsidian. |

### clawic-marketplace（clawic/marketplace，3 个）

| 技能 | 状态 | 说明 |
| --- | --- | --- |
| `git-essentials` | 可见 | Essential Git commands and workflows for version control, branching, and collaboration. |
| `skill-scaffold` | 可见 | AI agent skill scaffolding CLI. Create skills for OpenClaw, Moltbot, Claude, Cursor, ChatGPT, Copilot instantly. Vibe-coding ready. MCP comp |
| `word-docx` | 可见 | Create/inspect/edit Word DOCX: styles, numbering, tracked changes, fields, tables, templates, sections, compatibility, drift-free round-trip |

## 非本仓技能源

- `update-all`（update-app）· `yellowriver-*`（YellowRiverSluice）· `hydrovault-wp-cesium-streaming`（HydroVault2）· `cordis-plugin-development` / `editing-cordis-compositions` / `genui`（插件注册）

## 已退役分组仓（2026-09-13）

unknown-opencode-pack · jykim-claude-obsidian-skills · tobi-qmd · **benoror-obsidianos-work**（本地 + GitHub 远端均已删除）