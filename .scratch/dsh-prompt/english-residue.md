# 英文残留清单（模型可见文本，源码为证）

## 提示词散文（14 条命中源码）

- (22×) type JsonValue = null | boolean | number | string | JsonValue[] | { [key: string]: JsonValue }
- (22×) type ToolName = keyof ToolOutputMap
- (22×) declare class ToolCallError extends Error {
- (12×) /** Canonical absolute path in the filesystem execution world. */
- (8×) /** Task name of at most 120 characters in the user's language: action plus object. Omit timing, status, ids, and bracketed suffixes. */
- (8×) You are interacting with the user through the DeepSeek Harness Web GUI whose URL the runtime context names. When the user refers to "this page", "this GUI", or "this app"
- (3×) When you have your final answer, you MUST report it by calling the `structured_output` tool with arguments matching its parameter schema exactly. Do not finish with a pla
- (3×) /** Registered LLM provider id. */
- (3×) /** 1-based first line to return. Defaults to 1. */
- (3×) /** Maximum number of lines to return. Defaults to 2000. */
- (1×) Non-zero exits are reported as `[exit code: N]` markers; investigate failures before moving on. On Windows a killed process settles as `[exit code: 1]` without a signal m
- (1×) Use session_search to find relevant work from prior sessions, or session_event_search to search earlier events in one session. Search results are cursor-free and workspac
- (1×) var { connectCua } = await import("file://{{cwd}}/cua-runtime/lib/bridge.js");
- (1×) var cua = connectCua(() => tools.cua, text => console.log(text));

## 工具描述/参数注释（18 条，分布在 10 个文件）

### packages/subagent/tool-subagent-control/src/index.ts（3 条）
- The message to deliver to the agent.
- Send a message to an agent. A working agent receives it at its next step; an idle agent starts a new turn with it. Returns delivery confirmation.
- The name of another agent in your subagent tree, as shown by list_agents.

### packages/workflow/workflow/src/types.ts（3 条）
- One-line description of what the workflow does.
- Optional guidance on when this workflow applies.
- Optional model override this phase is expected to use.

### packages/fs/tool-fs-search/src/grep.ts（3 条）
- Regular expression to search for (ripgrep syntax).
- File or directory to search. Defaults to the session workspace; a relative path resolves against it.
- One glob filter for which files to search (e.g. "*.ts", "*.{js,jsx}"). Not a list; negation is not supported.

### packages/experimental/tool-subagent-oar/src/index.ts（2 条）
- Initial child working directory. Relative paths use your current directory; omitted inherits it. Later directory changes in either agent are independe
- Optional short name for the subagent, unique among the subagents you create: lower-case letters, digits, and hyphens, starting with a letter, at most 

### packages/fs/tool-fs-search/src/glob.ts（2 条）
- Glob pattern to match file paths against (e.g. "**/*.ts", "src/**/*.test.js"). A pattern with no "/" matches the basename at any depth, so "*" and "*.
- Directory to search in. Defaults to the session workspace; a relative path resolves against it.

### packages/sandbox/sandbox/src/escalation.ts（1 条）
- The narrowest wider sandbox mode for a one-shot retry of the exact operation the sandbox just denied; the retry asks the user for approval.

### packages/fs/tool-fs/src/sandbox.ts（1 条）
- Required with sandbox_permissions: one sentence for the user explaining why this exact file operation needs the wider access. Use the language of the 

### packages/jobs/tool-jobs/src/index.ts（1 条）
- Job id returned by the tool that started the background work.

### packages/subagent/tool-subagent-control/src/list-agents.ts（1 条）
- List your entire subagent tree: the root agent and all reachable continuable descendants, including yourself. Rows carry names, descriptions, and stat

### packages/fs/tool-fs/src/read.ts（1 条）
- Maximum number of lines to return. Defaults to 2000.

