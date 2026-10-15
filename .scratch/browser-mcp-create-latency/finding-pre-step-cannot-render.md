# Finding: `agent/pre-step` cannot put browser tools into the first model request

Read-only investigation in the DSH production checkout
`/home/sx/projects/MyAI/deepseek-harness` (branch `master`, HEAD
`169ea8e457`). No commit was made. The work-in-progress diff is saved beside
this file as `wip-move-wait.patch`.

## What the required design assumed

Move the browser-MCP handshake out of Session creation, then hold the
Session's first step in an `agent/pre-step` listener until the server is
discovered, so "the model's first request still sees the browser tools".

## Why that cannot hold

`packages/core/agent-loop/src/agent.ts:265-289` (`ReactLoopAgent.preStep`):

```ts
private async preStep(target: InboxTarget, position: { turn: number; step: number }): Promise<PreparedStep> {
  const signal = this.phase.abort.signal
  const claimed = this.inbox.claim(target, position.turn)
  const assembly = await this.loopCtx.systemPrompt.assemble(assembleContextFor(this, signal))   // :272
  signal.throwIfAborted()
  const decision = await this.dispatch.waterfall(
    'agent/pre-step', { messages: claimed, ...position, signal }, ...                            // :274
  )
  signal.throwIfAborted()
  if (decision.kind === 'reject') return decision
  return { ...decision, assembly }                                                               // :288
}
```

Two facts defeat the design:

1. The assembly that becomes the step's request tool list is rendered at
   `agent.ts:272`, *before* the waterfall. Tool schemas are collected during
   that call (`packages/core/system-prompt/src/index.ts:631-669`), so a
   listener that awaits them can only influence later steps.
2. Line 288 overwrites whatever a listener attached to the decision with the
   loop's own pre-waterfall `assembly` variable. A listener cannot substitute
   an assembly; `PreStepDecision`
   (`packages/core/agent/src/runtime-types.ts:112-119`) has no assembly field
   to return in the first place.

Verified by instrumentation: a pre-step listener could observe
`ctx.tools.schemas(agent)` containing the two fixture tools, render an
assembly that contained them, and the loop still requested with `tools:
undefined`. Both `mcp.spec.ts:186` and the new "fails the first step while
discovery is pending" case fail on exactly this.

### Consequence

With `mountSessionMcp` no longer awaiting `resources.get()` in
`agent/created`, the first request is sent *without* the browser tools. The
`toolOrder` path makes it worse: `orderTools`
(`packages/core/system-prompt/src/index.ts:229-231`) throws
`toolOrder lists unregistered tool "mcp__browser-fixture__visit"; known
tools: (none)` on that first assembly, so a deployment naming browser tools in
`toolOrder` fails the whole first turn.

## Options

1. **Keep the acquisition awaited in `agent/created`.** Preserves the
   guarantee and needs no package change; Session creation keeps paying the
   measured 0.90-2.47 s.
2. **Move the first assembly after the pre-step waterfall in the loop**, i.e.
   hoist `systemPrompt.assemble` out of `preStep` to after the waterfall for
   the steps that enter. Restores the design as specified; touches
   `agent-loop`, `docs/architecture.md` line 110, the
   `agent/pre-step` JSDoc at `runtime-types.ts:310-320`, `docs/agent-lifecycle.md`
   and `docs/event-producer-consumer.md`.
3. **Cut the handshake cost instead of moving it.** The MCP client hardcodes
   `versionNegotiation: { mode: 'auto' }`
   (`packages/mcp/mcp-client/src/connection.ts:262`) while the bench in the
   task measured auto at 505 ms and legacy at 250 ms. Not the same guarantee,
   but no lifecycle change; the worst-case samples would still need re-measuring.

Option 2 is the only one that satisfies the stated requirement; it is outside
the "one package" surface the task described, so it was not taken unilaterally.

## State of the work in progress

`wip-move-wait.patch` implements the parts that do work and is otherwise green:

- `packages/experimental/browser-use-runtime/src/mcp.ts`: `agent/created`
  starts the acquisition without awaiting and records its failure; a new
  `agent/pre-step` listener awaits it, fails the step with
  `browser MCP server did not initialize, so this step has no browser tools`
  when it failed, and keeps `resources.get(agent, signal)` for cancellation.
- `tests/mcp.spec.ts`, `tests/host-runtime-duplication.spec.ts`: retargeted to
  creation-returns-immediately, step-waits, and process/attachment release.

Suite result: `pnpm exec vitest run
packages/experimental/browser-use-runtime/tests
packages/experimental/browser-use-playwright-mcp/tests
packages/experimental/browser-use-chrome-devtools-mcp/tests
packages/experimental/browser-use/tests` -> 41 passed, 3 failed, and all three
failures are the first-request tool-list assertion this finding explains.
