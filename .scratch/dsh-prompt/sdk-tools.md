# DSH 工具 SDK 声明清单

> 来源：本会话提示词中的 `interface ToolArgsMap` / `interface ToolOutputMap`（由各工具包 schema 渲染）。

> 本会话（3080 生产）实际声明 193 条。codebase-memory 的 `mcp__cbm__*` 当日因服务故障未挂载，故不在表内；服务已修复，新会话会出现。

## 分类计数

| 分类 | 条目数 |
| --- | --- |
| 基础 / 上下文 / 编排 / 会话 | 41 |
| Blender（blender_） | 6 |
| CUA 桌面与浏览器（cua_driver_native__） | 59 |
| ego-browser（ego_） | 33 |
| Unity MCP（mcp__unity__） | 48 |
| zvecgrep（mcp__zvecgrep__） | 6 |
| **合计** | **193** |

## 基础 / 上下文 / 编排 / 会话（41）

- **absorb**（ref, summary） — Distill a tool result into a compact summary you write. REQUIRED immediately after a tool result ends with an [ACP absorb] instruction: pass its ref and the dis
- **acp_cache**（detail） — Prompt-cache reconciliation: grand ledger (total input/cached/output, overall hit rate) with every request's miss split into new content / compression re-pay /
- **acp_read_original_image**（ref） — Read the ORIGINAL full-resolution image of a message whose picture was downscaled before reaching you. Beside each shrunken image there is a [bili] note quoting
- **acp_retrieve**（ref） — Retrieve the full original text of a stored message by its id. Large tool results are replaced on the wire with a placeholder shaped like "📦 [acp-stored #m0042
- **acp_status**（scope, view, tool, sort, limit, archiveDetail） — Show context usage and compressible ranges. No args = overview; pass scope/view/tool/sort/limit/archiveDetail for targeted listings. Calling convention: if this
- **ask_user_question**（questions） — Ask the user a concise question when you need confirmation, a choice, or missing information before proceeding. An answer item with empty selected and no custom
- **bash**（description, command, timeoutMs, workdir, run_in_background） — Execute a bash command (`bash -c`) and return its stdout/stderr. Each call runs in a fresh shell; pass `workdir` instead of using `cd`. Managed `$DSH_*` variabl
- **compress**（content） — Replace consumed conversation ranges with self-contained summaries you write, identified by their refs. content = ONE plain string holding ALL ranges — each blo
- **cordis_inspect_list** — List every Cordis Inspect Provider currently known to the Host, including local Host Providers and the latest manifests synchronized from the Client. Each entry
- **cordis_inspect_query**（platform, provider, method, input） — Run a read-only query declared by an Inspect Provider. platform, provider, and method must come from cordis_inspect_list, and input must satisfy that method's s
- **create_goal**（objective, max_goal_rounds） — Create a persisted goal that keeps this session working across automatic continuation rounds. Use it when the direct human request is a long-running objective,
- **create_worktree**（name, from） — Create a new Git branch and worktree from a local commit, branch, or tag, then change this session's working directory to it. Uncommitted files stay in the sour
- **decompress**（blockId, toFile, full, startId, endId, imageRef） — Restores previously compressed content. Use when you need exact details lost in compression. By default restores one tier up. Use full:true for all the way to o
- **edit**（file_path, old_string, new_string, replace_all） — Edit an existing UTF-8 text file by replacing literal text. */
- **get_goal** — Read the current session goal, including the id and revision that update_goal requires. */
- **job_kill**（job_id, reason） — Request cancellation of a running background job. */
- **job_list** — List your background jobs (running and finished) with their ids, kinds, and statuses. */
- **job_output**（job_id, wait, timeout_ms） — Read a background job: output since the previous read for stream jobs, or the result of a finished final-output job. */
- **list_mcp_resource_templates**（server, cursor） — List parameterized resource URI templates from an MCP server. */
- **list_mcp_resources**（server, cursor） — List resources available from an MCP server. */
- **plugin_manager**（action, target, enabled, runtimeVersion, acceptRisk, approvedBuilds, registry, offset, limit） — List plugins or bundles in the current profile, enable or disable them, install a bundle, or remove an installed bundle. Every action requires danger-full-acces
- **ralph**（objective, maxRounds） — Run a foreground fresh-agent Ralph loop toward one immutable objective. Use only when the direct human explicitly asks for Ralph or fresh-agent iteration. Each
- **read**（file_path, offset, limit） — Read a UTF-8 text file and return line-numbered content. */
- **read_image**（file_path） — Read a PNG/JPEG/WebP/GIF file and return the image itself. Large images are downscaled automatically; do not install image libraries or create thumbnails to ins
- **read_mcp_resource**（server, uri） — Read an MCP resource by URI from the named server. Use a listed URI or an expanded resource template. */
- **search_context**（query, limit） — Search through compressed block summaries by keyword. Use BEFORE decompressing to find the right block. Calling convention: if this environment only allows `run
- **skill**（name） — Load the full instructions for a skill. Call it before acting on a task that names or clearly matches a skill in the session skill catalog. */
- **subagent**（cwd, description, name, prompt） — Delegate a self-contained task to a subagent (a separate agent that works in its own context) to offload focused, independent work — research, a scoped implemen
- **subagent_fork**（cwd, description, name, prompt） — Delegate a task to a subagent that inherits this conversation: a child agent seeded with all completed turns so far (it does not see the current in-flight turn)
- **terminal_close**（sessionId） — Close one persistent terminal and wait until its captured owned process tree is gone. */
- **terminal_list** — List persistent terminal sessions owned by the current agent. */
- **terminal_open**（type, name, cwd） — Create a persistent, owner-isolated terminal session from a registered backend type. Use this for shell or REPL state that must survive across tool calls. */
- **terminal_read**（sessionId, offset, count） — Read a bounded page of retained output from a persistent terminal without sending input. */
- **terminal_send**（sessionId, text, submit, run_in_background） — Send text to a persistent terminal. By default Enter is submitted and the call waits for a prompt, stdin wait, output silence, timeout, or session exit. Backgro
- **terminal_signal**（sessionId, signal） — Send an allowed signal to the current foreground process group of a persistent terminal. */
- **todo_write**（todos） — Record and update a task list to plan multi-step work and show progress; skip it for trivial single-step tasks. Add one todo per concrete step before you start.
- **update_goal**（goal_id, revision, action, objective, max_goal_rounds, blocked_reason） — Update the current goal. */
- **web_search**（queries） — Search the web for current information. Returns an optional summary answer and a list of source URLs. */
- **workflow**（script, meta, args, run_in_background） — Run a JavaScript workflow script that orchestrates subagents at scale. Use this for work that fans out across many independent pieces — an audit over many files
- **working_directory**（cd） — Read the current working directory, or change it with cd. Relative paths use the current directory. Existing shells and running processes keep their own directo
- **write**（file_path, content） — Create or fully replace a UTF-8 text file. */

## Blender（blender_）（6）

- **blender_inspect**（command, args） — [v3.1.0-alpha.1] 【只读检查】help 列出 addon 的可执行只读命令（name(args) / enabled / pause_safe / description）；command=<name> args={...} 执行其中一条。内部传输命令（execute_code / get_viewpo
- **blender_op**（action, op, args, path, attach_images, session, target, spec, history, board, limit, groups, top, include_variants, note, iterations, name, kind, tags, names, targets, data, overwrite） — [v3.1.0-alpha.1] 【算子】执行 catalog 的 plan 算子（34 family / 228 op；op=catalog 看目录），以及参数搜索 loop、对象精简 opt、配方库 preset。执行型 op 需要 ready 的 GUI 会话；catalog / 只读 op / args.dry
- **blender_py**（code, file, see, max_size, force, wait_ms） — [v3.1.0-alpha.1] 【执行 Python】在 ready 的 GUI 会话里跑 agent 写的 Python（/act 通道，固定 exclusive，不卡队列）。没有会话直接拒绝，不会启动 headless、不会自动降级。脚本可以重跑；超过 ~1s 的重活请改用 blender_run(kind=he
- **blender_run**（action, kind, id, priority, timeout_ms, tail, state, owner, file, output, outdir, frames, resolution, samples, engine, format, camera, script, script_file, preload, factory_startup, bootstrap, workdir, include_noise, out_json, args, env, op） — [v3.1.0-alpha.1] 【作业 / 渲染】唯一作业入口：submit 立即返回 jobId（无同步模式），之后 status/wait/collect/cancel/list/perf。kind=render 是声明式最终渲染（相机、帧区间、分辨率、采样、引擎、输出文件；不接受 script；支持相机动画）；
- **blender_see**（viewpoint, mode, camera, aspect, max_size, from, look_at, lens, ortho, ortho_scale, full, area, shading, overlays, diagnostics, seconds, fps, force） — [v3.1.0-alpha.1] 【看 GUI】只服务 GUI 会话：viewpoint=viewport（当前视口）/ camera（当前帧相机）/ custom（from+look_at 自定义机位），mode=frame（默认单帧）或 sequence（固定机位序列帧，只 viewport/custom）。固定档
- **blender_session**（action, session_id, instance_id, kind, scopes, target_agent_id, target_dsh_session_id, target_host_id, grant_id, ttl_ms, op, label, note, objects, keep, into, backup, force） — [v3.1.0-alpha.1] 【会话 / 归属 / 权限】管理 GUI 会话：list/status/doctor 看状态；attach 附着到用户已打开的 Blender（多实例必须给 instance_id）；grant/revoke 把写 scope（exclusive | collection:名 | pr

## CUA 桌面与浏览器（cua_driver_native__）（59）

- **cua_driver_native__bring_to_front**（pid, window_id） — Persistently activate a window so subsequent input lands on it. This deliberately breaks the no-foreground contract and is not part of the normal input ladder.
- **cua_driver_native__browser_click**（input_route, ref, session, tab_id, target_id, x, y） — Click a page element (by ref) or viewport coordinates in an exactly-bound tab. Default route is trusted hardware-like input (Input.dispatchMouseEvent), and refu
- **cua_driver_native__browser_dialog**（action, delivery_mode, dialog_id, prompt_text, session, tab_id, target_id） — Inspect or resolve a page-owned JavaScript alert, confirm, prompt, or beforeunload dialog on one exactly-bound tab. This never handles browser permission UI, ex
- **cua_driver_native__browser_download**（destination_root, ref, session, tab_id, target_id） — Trigger one download through an exact live browser ref and save it inside an explicitly approved directory. Requires MCP-host destructive-tool approval, refuses
- **cua_driver_native__browser_navigate**（session, tab_id, target_id, url） — Navigate one tab of an exactly-bound browser target to a new URL (http/https/about only). Refused for heuristic bindings. Navigation invalidates all p<snapshot>
- **cua_driver_native__browser_pointer**（action, delta_x, delta_y, destination_ref, input_route, ref, session, tab_id, target_id, to_x, to_y, x, y） — Perform hover, right-click, double-click, scroll, or drag in an exactly-bound browser tab. Semantic refs must declare pointer for hover, right-click, double-cli
- **cua_driver_native__browser_prepare**（allow_launch, pid, profile, session, strategy, window_id） — Explicitly prepare an owned DevTools endpoint for a browser. pid is required for an existing process or existing-profile attachment, and optional only for allow
- **cua_driver_native__browser_set_input_files** — Assign one or more explicit absolute local files to an exact live <input type=file> ref through CDP. This bypasses native file pickers, rejects symlinks and non
- **cua_driver_native__browser_type**（mode, ref, replace, session, tab_id, target_id, text） — Type text into an exactly-bound tab via the Input domain. mode="insert_text" (default) uses Input.insertText; mode="keystrokes" dispatches per-character key eve
- **cua_driver_native__check_permissions** — Check required permissions for cua-driver-rs on Linux. */
- **cua_driver_native__click** — Click against a target pid. **Prefer `element_index` over pixel coordinates** — element_index works on backgrounded / hidden windows, surfaces a stable handle,
- **cua_driver_native__clipboard_read**（include_text, session） — List available system clipboard types and optionally return privacy-sensitive plain text. Clipboard content is never retained in telemetry. */
- **cua_driver_native__clipboard_write**（file_path, image_path, session, text） — Replace the system clipboard with exactly one value: plain text, an image from an absolute local path, or a file URL from an absolute local path. Returns the av
- **cua_driver_native__double_click** — Double-click at (x,y) or an element_index (AT-SPI bounds) via XSendEvent. No focus steal. Provide either (window_id + x/y) or (pid + element_index). After a zoo
- **cua_driver_native__drag** — Press-drag-release gesture from (from_x, from_y) to (to_x, to_y) in window-local screenshot pixels via XSendEvent (ButtonPress + MotionNotify × steps + ButtonRe
- **cua_driver_native__end_session**（session） — End one visible lifecycle session and run its cursor, recording, configuration, and other cleanup hooks exactly once. Omit `session` to end the authenticated tr
- **cua_driver_native__escalate_session** — Deprecated compatibility tool for legacy capture-scope sessions. New callers select window or desktop modality on each action. No deescalate_session tool exists
- **cua_driver_native__get_accessibility_tree** — Return a lightweight snapshot of the desktop: running processes and on-screen visible X11 windows with their bounds and owner pid. For the full AT-SPI subtree o
- **cua_driver_native__get_agent_cursor_state**（session） — Return the session cursor's theme, semantic playback, position, visibility, and motion. */
- **cua_driver_native__get_browser_state**（continuation, include_screenshot, pid, query, scope_ref, session, snapshot_format, tab_id, target_id, window_id） — Read-only browser inspection. Mode 1 (bind): pass pid + window_id of a native browser window to classify it, correlate it to a CDP target (exact-or-refuse), and
- **cua_driver_native__get_config** — Return current cua-driver-rs configuration. */
- **cua_driver_native__get_cursor_position**（session） — Return the current mouse cursor position in screen points (origin top-left). */
- **cua_driver_native__get_desktop_state**（screenshot_out_file, session） — Capture the full display in the desktop action coordinate frame. Use the returned PNG directly as the coordinate source for actions whose target is {kind:"deskt
- **cua_driver_native__get_recording_state** — Report the current trajectory recorder state: whether recording is enabled, the output directory (when enabled), and the 1-based counter for the next turn folde
- **cua_driver_native__get_screen_size**（session） — Return the logical size of the main display in points plus its backing scale factor. Agents click in points; Retina displays have scale_factor 2.0. Requires no
- **cua_driver_native__get_session**（session） — Read content-free lifecycle, cursor, recording, and idle status for one session visible to this authenticated transport. Omit `session` to inspect its implicit
- **cua_driver_native__get_session_state**（session） — Deprecated compatibility alias that reads a live legacy session's capture policy. Use get_session for lifecycle state. */
- **cua_driver_native__get_window_state** — Walk a running app's AT-SPI tree and return BOTH a structured `elements` array (preferred) AND a Markdown rendering of the same tree (back-compat). Every action
- **cua_driver_native__health_report**（include, skip） — Single-call end-to-end driver diagnostics. Designed to let downstream consumers ship one stable call instead of stitching together check_permissions, doctor, ve
- **cua_driver_native__hotkey** — Press a combination of keys simultaneously, e.g. ["ctrl","c"] for Copy. Sent via XSendEvent directly to the target pid; target does NOT need to be frontmost. */
- **cua_driver_native__install_ffmpeg**（confirm） — Install the ffmpeg binary used by start_recording's video capture (Linux/Windows; macOS records natively and needs no ffmpeg). Two-step and confirmed: called wi
- **cua_driver_native__invoke_menu** — Resolve an exact application-menu path one live native level at a time and invoke its final item through accessibility APIs. Missing, ambiguous, disabled, or st
- **cua_driver_native__kill_app**（pid） — Force-terminate a process by pid (kill -9 equivalent on Linux). Use as escalation when the cooperative close path failed to make the process exit. Unsaved state
- **cua_driver_native__launch_app**（additional_arguments, bundle_id, launch_path, name, urls） — Launch a Linux app in the background. Provide launch_path (preferred — round-trip the value from list_apps), name (tried as a direct command, then matched again
- **cua_driver_native__list_apps** — List Linux apps — both currently running and installed-but-not-running — with per-app state flags: - running: is a process for this app live? (pid is 0 when fal
- **cua_driver_native__list_sessions** — List content-free lifecycle summaries attached to this authenticated transport lease. It does not enumerate other callers' sessions. */
- **cua_driver_native__list_windows**（on_screen_only, pid） — List top-level windows. Each record includes z_index (integer or null; higher values are closer to the front; null means stacking order is unavailable and calle
- **cua_driver_native__mouse_button_down**（button, cursor_id, from_zoom, pid, session, window_id, x, y） — Press and hold a mouse button at (x,y) via background X11 delivery. Does not release the button; pair with mouse_drag / mouse_button_up. Returns the current hel
- **cua_driver_native__mouse_button_up**（cursor_id, from_zoom, pid, session, window_id, x, y） — Release a previously-held mouse button via background X11 delivery. If x/y are omitted, releases at the last held position. Returns the current held-button stat
- **cua_driver_native__mouse_drag** — Move a previously-held mouse button to a new point via background X11 delivery. Requires an active mouse_button_down state; does not release the button. Returns
- **cua_driver_native__move_cursor** — Move the synthetic agent cursor without changing the user's pointer. Only an explicit scope=desktop request moves the real OS pointer in get_desktop_state coord
- **cua_driver_native__page** — Legacy browser compatibility tool. Prefer get_browser_state and the typed browser_* tools for exact targeting, endpoint ownership, and consent. Read-only get_te
- **cua_driver_native__parallel_mouse_drag** — Run multiple mouse drag gestures concurrently via Linux MPX/XI2 virtual master pointers. Each drag item runs on its own session-scoped master pointer (true same
- **cua_driver_native__press_key** — Press a key via XSendEvent to a window. No focus steal. */
- **cua_driver_native__replay_trajectory** — Replay a recorded trajectory by re-invoking every turn's tool call in lexical order. `dir` must point at a directory previously written by `start_recording`. Ea
- **cua_driver_native__right_click** — Right-click at (x,y) or an element_index (AT-SPI bounds) via XSendEvent. No focus steal. Provide either (window_id + x/y) or (pid + element_index). After a zoom
- **cua_driver_native__scroll** — Scroll the target pid's focused region via XSendEvent Button4/5. direction required; by defaults to line, amount defaults to 3. */
- **cua_driver_native__set_agent_cursor_enabled**（enabled, session） — Show or hide the agent cursor owned by a session. */
- **cua_driver_native__set_agent_cursor_motion** — Configure only movement physics and visibility timing for a session cursor. */
- **cua_driver_native__set_agent_cursor_theme** — Select an already-installed cursor theme for a session. */
- **cua_driver_native__set_config**（capture_mode, experimental_pip, experimental_pip_geometry, key, max_image_dimension, value） — Update cua-driver-rs configuration. capture_mode / max_image_dimension take effect immediately. Two input shapes (both accepted, matching Windows/Swift): - **{k
- **cua_driver_native__set_value** — Set value of an AT-SPI element via SetValue action. */
- **cua_driver_native__set_window_frame** — Set one exact top-level window's frame in the desktop-coordinate space reported by list_windows and verify the resulting geometry through an independent readbac
- **cua_driver_native__start_recording**（output_dir, record_video） — Start trajectory recording. Every subsequent action-tool invocation (click, right_click, scroll, type_text, press_key, hotkey, set_value) writes a turn folder u
- **cua_driver_native__start_session** — Optionally create or return a lifecycle session before acting. For multi-call work, prefer a short public `session` label and repeat it on every call that accep
- **cua_driver_native__stop_recording** — Stop trajectory recording. Disables further per-turn capture and, when video was enabled, gracefully terminates the ffmpeg subprocess so the mp4's moov atom is
- **cua_driver_native__type_text** — Type text to a window via XSendEvent (KeyPress/KeyRelease). No focus steal. */
- **cua_driver_native__verify_state** — Deterministically verify bounded predicates against one exact window. The driver evaluates structured window/accessibility state and may return the final screen
- **cua_driver_native__zoom**（pid, window_id, x1, x2, y1, y2） — Capture a cropped JPEG of a window region (x1,y1)–(x2,y2) in screenshot pixels, with 20% padding. Output is at most 500 px wide. After a zoom, pass from_zoom=tr

## ego-browser（ego_）（33）

- **ego_auth_flush** — Force all persistent login cookies in the agent browser to be written to the on-disk profile. Call this after login (or before ending a browsing task) so the lo
- **ego_captcha**（space） — Check the current page for a human-verification (CAPTCHA) challenge — reCAPTCHA / hCaptcha / Cloudflare / Turnstile — and return { detected, kind }. If detected
- **ego_cdp**（method, params, space） — Issue a raw CDP command on the page target, e.g. cdp("Page.handleJavaScriptDialog", { accept: true }). */
- **ego_check**（selector, checked, space） — Check (tick) or uncheck a checkbox/radio element. Does nothing if already in the desired state. */
- **ego_cli**（script） — Escape hatch: run an arbitrary `ego-browser nodejs` heredoc script verbatim (facades page/browser/taskSpaces/site/fetch and the raw cdp() are preloaded). Use wh
- **ego_click**（selector, x, y, label, double, space） — Click an element in the current page. Target with a CSS selector, an xpath=.../loc=.../ref=N value from ego_snapshot, or viewport coordinates. */
- **ego_dialog**（accept, text, space） — Accept or dismiss a native browser dialog (alert/confirm/prompt), optionally supplying text for a prompt. Use right after the action that triggers the dialog. *
- **ego_doctor** — Preflight the ego-browser environment: vendored runtime present, Chrome/Edge/Brave candidates, state dir, CDP/browser.json, ego-cast worker, task spaces. Run fi
- **ego_download**（triggerSelector, triggerScript, savePath, timeout, space） — Wait for a file download triggered by the current action, then return its saved path. Provide `triggerSelector` (a download button/link to click) or `triggerScr
- **ego_drag**（from, to, points, space） — Drag an element to a target (Playwright dragTo) or drag the pointer through coordinates. Use for sliders, sortable rows, and drag-drop zones. */
- **ego_fill**（selector, text, space） — Type text into an input field. Target with a CSS selector, xpath=..., loc=..., or ref=N from ego_snapshot. */
- **ego_help**（topic） — Query the built-in ego-browser tool guide. `topic` may be a category (overview/tools/navigate/observe/input/keyboard-mouse/form/wait/network/login/script/doctor
- **ego_hover**（selector, x, y, space） — Move the pointer over an element (CSS selector / ref) or to viewport coordinates. Triggers CSS :hover, dropdowns and mouseenter handlers. */
- **ego_http**（url, method, headers, body, timeout, mode, space） — Make an HTTP request and return status + body. Default runs in the agent page's browser context (cross-origin allowed when the server's CORS permits); set `mode
- **ego_js**（expression, space） — Evaluate a JavaScript expression in the current page and return its JSON-serializable value (e.g. "document.title", "document.querySelectorAll('a').length"). */
- **ego_key**（key, text, space） — Press a keyboard key or shortcut combination on the current page, e.g. 'Enter', 'Tab', 'Control+a', 'Escape', 'ArrowDown'. Useful for forms, shortcuts and navig
- **ego_login_import**（source, domains, profile, closeSource, dryRun） — Import login cookies from the system browser (Chrome/Edge/Brave) into the agent browser, so sites open already logged in. Works via a throwaway headless instanc
- **ego_navigate**（url, wait, timeout, space） — Open a URL in the task space, or switch to the existing tab for it. Always prefer reusing existing open tabs before opening duplicate URLs. Waits for document l
- **ego_page_info**（space） — Return the current page info: url, title, viewport size (w, h), scroll offsets (sx, sy), device metrics (pw, ph), and whether a native dialog is open. Also repo
- **ego_read_element**（selector, what, attribute, space） — Read a single element (by selector): its text, HTML, input value, an attribute, or visibility/enabled/count. Cheaper and more precise than a full-page snapshot.
- **ego_screenshot**（selector, path, space） — Capture a screenshot of the current page (or of a single element if selector is given). Returns the file path of the saved PNG, which you can then read with a v
- **ego_script**（script, timeoutMs） — Run an arbitrary `ego-browser nodejs` heredoc script in ONE invocation (same runtime/API as ego_cli: page/…locator/browser/taskSpaces/site/fetch/cdp preloaded),
- **ego_scroll**（deltaX, deltaY, selector, space） — Scroll the page: by pixel deltas (wheel), or bring an element into view (scrollIntoView). */
- **ego_select**（selector, value, space） — Choose an option in a <select> dropdown by value, label, or index (a single value or an array for multi-select). */
- **ego_snapshot**（space, scope） — Read the current page as text: the full-page semantic tree annotated with [ref=N, loc=...] selectors that ego_click / ego_fill can target. This is the main obse
- **ego_space_close**（name, keep） — Close an ego-lite task space. WARNING: In persistent profile mode, DO NOT call this tool when finishing tasks! Keep the space, tabs, and browser window alive so
- **ego_space_open**（name） — Open (or reuse) the ego-lite task space. In persistent profile mode (default), ALWAYS use or reuse the single 'default' space. Login credentials automatically p
- **ego_status** — Check whether the ego-browser CLI is usable (runs `ego-browser --status`). Use this first when other ego_* tools report "CLI not found". */
- **ego_upload**（selector, path, space） — Set files on a file <input> element (path-driven). Use to upload a dataset/attachment from a local path. */
- **ego_wait**（ms） — Pause for a fixed number of milliseconds (e.g. for animations or partial loads). For load waits prefer ego_navigate's wait option. */
- **ego_wait_for_response**（url, timeout, body, space） — Wait for a network response matching a URL/glob/regex and return it. Optionally return the body (text or JSON) — ideal for scraping API responses or confirming
- **ego_wait_for_selector**（selector, state, timeout, space） — Wait until an element matching a CSS selector appears (state=visible, default) or disappears (state=hidden). Use instead of a blind fixed wait when a page rende
- **ego_wait_for_url**（pattern, timeout, space） — Wait until the page navigates to a URL matching a substring / glob / regex. Use to catch login redirects or pagination. */

## Unity MCP（mcp__unity__）（48）

- **mcp__unity__apply_text_edits** — Apply small text edits to a C# script identified by URI. IMPORTANT: This tool replaces EXACT character positions. Always verify content at target lines/columns
- **mcp__unity__batch_execute** — Executes multiple MCP commands in a single batch for dramatically better performance. STRONGLY RECOMMENDED when creating/modifying multiple objects, adding comp
- **mcp__unity__blender_bridge** — Bridge to a running Blender that has the BlenderMCP addon connected (socket, default 127.0.0.1:9876; configured in Window > MCP for Unity > Generative > Blender
- **mcp__unity__create_script** — Create a new C# script at the given project path. */
- **mcp__unity__debug_request_context** — Return the current FastMCP request context details (client_id, session_id, and meta dump). */
- **mcp__unity__delete_script**（uri） — Delete a C# script by URI or Assets-relative path. */
- **mcp__unity__execute_code** — Execute arbitrary C# code inside the Unity Editor. The code runs as a method body with access to UnityEngine and UnityEditor namespaces. Use 'return' to send da
- **mcp__unity__execute_menu_item** — Execute a Unity menu item by path. */
- **mcp__unity__find_gameobjects** — Search for GameObjects in the scene by name, tag, layer, component type, or path. Returns instance IDs only (paginated). Then use mcpforunity://scene/gameobject
- **mcp__unity__find_in_file** — Searches a file with a regex pattern and returns line numbers and excerpts. */
- **mcp__unity__generate_audio** — Generate audio (sound effects and background music) with fal.ai models and import them as AudioClips into the Unity project. Bring-your-own-key: the fal key liv
- **mcp__unity__generate_image** — Generate 2D images with AI providers (fal.ai, OpenRouter) and import them as textures/sprites into the Unity project. Bring-your-own-key: provider keys live in
- **mcp__unity__generate_model** — Generate 3D models with AI providers (Tripo, Meshy, fal) and import them into the Unity project. Bring-your-own-key: provider keys live in the editor's secure s
- **mcp__unity__get_sha**（uri） — Get SHA256 and basic metadata for a Unity C# script without returning file contents. Requires uri (script path under Assets/ or mcpforunity://path/Assets/... or
- **mcp__unity__get_test_job** — Polls an async Unity test job by job_id. */
- **mcp__unity__import_model** — Import 3D models from the Sketchfab marketplace into the Unity project. Bring-your-own-key: the Sketchfab token lives in the editor's secure store and never cro
- **mcp__unity__import_model_file** — Import a local 3D model file that already exists on disk (e.g. an FBX/OBJ/glTF exported from Blender or another DCC tool) into the Unity project. The file is co
- **mcp__unity__manage_animation** — Manage Unity animation: Animator control and AnimationClip creation. Action prefixes: animator_* (play, crossfade, set parameters, get info), controller_* (crea
- **mcp__unity__manage_asset** — Performs asset operations (import, create, modify, delete, etc.) in Unity. Tip (payload safety): for `action="search"`, prefer paging (`page_size`, `page_number
- **mcp__unity__manage_build** — Manage Unity player builds — trigger builds, switch platforms, configure settings, manage build scenes and profiles, run batch builds across platforms. Actions:
- **mcp__unity__manage_camera** — Manage cameras (Unity Camera + Cinemachine). Works without Cinemachine using basic Camera; unlocks presets, pipelines, and blending when Cinemachine is installe
- **mcp__unity__manage_components** — Add, remove, or set properties on components attached to GameObjects. Actions: add, remove, set_property. Requires target (instance ID or name) and component_ty
- **mcp__unity__manage_editor** — Controls and queries the Unity editor's state and settings. Read-only actions: telemetry_status, telemetry_ping. Modifying actions: play, pause, stop, set_activ
- **mcp__unity__manage_gameobject** — Performs CRUD operations on GameObjects. Actions: create, modify, delete, duplicate, move_relative, look_at. NOT for searching — use the find_gameobjects tool t
- **mcp__unity__manage_graphics** — Manage rendering graphics: volumes, post-processing, light baking, rendering stats, pipeline settings, and URP renderer features. Use ping to check pipeline and
- **mcp__unity__manage_material** — Manages Unity materials (set properties, colors, shaders, etc). Read-only actions: ping, get_material_info. Modifying actions: create, set_material_shader_prope
- **mcp__unity__manage_packages** — Manage Unity packages: query, install, remove, embed, and configure registries. QUERY (read-only): - list_packages: List all installed packages - search_package
- **mcp__unity__manage_physics** — Manage physics settings, collision matrix, materials, joints, queries, and validation. SETTINGS: ping, get_settings, set_settings COLLISION MATRIX: get_collisio
- **mcp__unity__manage_prefabs** — Manages Unity Prefab assets. Actions: get_info, get_hierarchy, create_from_gameobject, modify_contents, open_prefab_stage, save_prefab_stage, close_prefab_stage
- **mcp__unity__manage_probuilder** — Manage ProBuilder meshes for in-editor 3D modeling. Requires com.unity.probuilder package. SHAPE CREATION: - create_shape: Create a ProBuilder primitive (shape_
- **mcp__unity__manage_profiler** — Unity Profiler session control, counter reads, memory snapshots, and Frame Debugger. SESSION: - profiler_start: Enable profiler, optionally record to .raw file
- **mcp__unity__manage_scene** — Performs CRUD operations on Unity scenes. Read-only actions: get_hierarchy, get_active, get_build_settings, get_loaded_scenes, scene_view_frame. Modifying actio
- **mcp__unity__manage_script** — Compatibility router for legacy script operations. Prefer apply_text_edits (ranges) or script_apply_edits (structured) for edits. Read-only action: read. Modify
- **mcp__unity__manage_script_capabilities** — Get manage_script capabilities (supported ops, limits, and guards). Returns: - ops: list of supported structured ops - text_ops: list of supported text ops - ma
- **mcp__unity__manage_scriptable_object** — Creates and modifies ScriptableObject assets using Unity SerializedObject property paths. */
- **mcp__unity__manage_shader** — Manages shader scripts in Unity (create, read, update, delete). Read-only action: read. Modifying actions: create, update, delete. */
- **mcp__unity__manage_texture** — Procedural texture generation for Unity. Creates textures with solid fills, patterns (checkerboard, stripes, dots, grid, brick), gradients, and noise. Actions:
- **mcp__unity__manage_tools** — Manage which tool groups are visible in this session. Actions: list_groups (show all groups and their status), activate (enable a group), deactivate (disable a
- **mcp__unity__manage_ui** — Manages Unity UI Toolkit elements (UXML documents, USS stylesheets, UIDocument components). Read-only actions: ping, read, get_visual_tree, list. Modifying acti
- **mcp__unity__manage_vfx** — Manage Unity VFX components (ParticleSystem, VisualEffect, LineRenderer, TrailRenderer). Action prefixes: particle_*, vfx_*, line_*, trail_*. Action-specific pa
- **mcp__unity__read_console** — Gets messages from or clears the Unity Editor console. Defaults to 10 most recent entries. Use page_size/cursor for paging. Note: For maximum client compatibili
- **mcp__unity__refresh_unity**（mode, scope, compile, wait_for_ready） — Request a Unity asset database refresh and optionally a script compilation. Can optionally wait for readiness. */
- **mcp__unity__run_tests** — Starts a Unity test run asynchronously and returns a job_id immediately. Poll with get_test_job for progress. */
- **mcp__unity__script_apply_edits** — Structured C# edits (methods/classes) with safer boundaries - prefer this over raw text. Best practices: - Prefer anchor_* ops for pattern-based insert/replace
- **mcp__unity__set_active_instance**（instance） — Set the active Unity instance for this client/session. Accepts Name@hash, hash prefix, or port number (stdio only). */
- **mcp__unity__unity_docs** — Fetch official Unity documentation from docs.unity3d.com. Returns descriptions, parameter details, code examples, and caveats. Use after unity_reflect confirms
- **mcp__unity__unity_reflect** — Inspect Unity's live C# API via reflection. Use this to verify that classes, methods, and properties exist before writing C# code — training data may be wrong o
- **mcp__unity__validate_script**（uri, level, include_diagnostics） — Validate a C# script and return diagnostics. */

## zvecgrep（mcp__zvecgrep__）（6）

- **mcp__zvecgrep__zvec_grep_index** — Activate an absolute workspace root to create, incrementally update, rebuild, or explicitly drop its index. Do not call this tool to create, rebuild, or drop an
- **mcp__zvecgrep__zvec_grep_index_drop** — Delete the persisted index for an absolute workspace root and release its daemon runtime. */
- **mcp__zvecgrep__zvec_grep_index_status** — Read persisted index status for an absolute root. Use only after a missing-index response, indexing failure or cancellation, explicit progress monitoring, or da
- **mcp__zvecgrep__zvec_grep_rg** — Run exhaustive ripgrep across workspace material without an index. Pass a command starting with `rg`; it is parsed as arguments and never executed by a shell. R
- **mcp__zvecgrep__zvec_grep_search** — Search a workspace index for semantic, relational, cross-file, or multi-hop evidence such as architecture, call chains, dependencies, lifecycle, data or control
- **mcp__zvecgrep__zvec_grep_server_status** — Read daemon version, queue, runtime and model-pool summary without exposing repository paths. */
