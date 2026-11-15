# M0 基线记录（2026-11-05）

## 环境

- 桌面：niri `v26.04`（`8ed0da44d974c32c6877d2f4630c314da0717ecb`）
- fork 检出：`/home/sx/projects/agent-desktop`，分支 `niri-scoped-input`，基点 `5e0491ae9cfe0552cd50ca348188411d94b8abdc`
- 工具链：cargo 1.99.1（Arch 包，非 rustup；`rust-toolchain.toml` 钉的 1.89.0 不生效）

## 构建

`cargo build -p agent-desktop -p agent-desktop-linux` → **成功，52.28s**，产物 `target/debug/agent-desktop`。

仅有两条上游既有的 deprecation 警告（`Atomic::fetch_update` 在 `crates/linux/src/input/x11/progress.rs:23` 与 `crates/linux/src/system/x11/bounded.rs:154`），与本功能无关。

## 只读探测（用本地构建产物复跑）

| 命令 | 结果 |
|---|---|
| `status` | `ok`，无障碍 `granted`，支持 window/sheet/alert/menu |
| `list-windows` | 7 个窗口：Helium×2、微信、Dolphin、Unity、waybar、swaync |
| 焦点不变 | 探测前后 `niri msg -j focused-window` 的 `id` 均为 4 |

## 测试基线

`cargo test -p agent-desktop-linux`：**2172 passed；2 failed；233 ignored**。

两个失败逐一定性：

| 测试 | 定性 | 证据 |
|---|---|---|
| `adapter::tests::the_lifecycle_overrides_are_wired_to_the_adapter` | **环境依赖，非缺陷** | 无 `WAYLAND_DISPLAY` 时两边都是 `PlatformNotSupported`；带上会话环境变量单跑 → `ok` |
| `system::x11::reader::popup_tests::a_silent_popup_setup_releases_its_socket_and_reader` | **上游既有测试缺陷** | `popup_reader_tests.rs:87`：`port - 6000` 在内核分配的临时端口小于 6000 时下溢（debug 溢出检查直接 panic）。本机 `ip_local_port_range` = `1024	65535` |

处置：第二条不修（不属于本功能范围），作为已知基线失败记录；执行验证时用过滤器排除它，其余必须全绿。若要顺手修，应单开一个上游 PR，把 `port - 6000` 换成不依赖端口数值的构造方式。

## 结论

M0 通过：可编译、可复跑基线、探测不改变人的焦点。已知失败已定性，不阻塞后续。
