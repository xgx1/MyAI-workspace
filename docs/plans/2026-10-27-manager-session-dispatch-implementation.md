# Manager Session Dispatch — Implementation Plan

> Execute incrementally with test-driven development. Work only in the isolated development checkout and the development profile; production and its linked extension sources remain read-only.

**Goal:** Deliver the approved minimal manager: independent ordinary work sessions, explicit adoption, automatic reports/questions, durable waiting/recovery, and restricted existing OpenViking preference access. No second scheduler, task database, client plugin, or server.

**Architecture:** One opt-in Host package, `@deepseek-ai/dsh-session-manager`, under `packages/session/session-manager`. A copied-and-trimmed preset selects a manager scope. The package uses `sessionController.create/inspect/resolveAgent`, `workspaceRegistry`, scoped tools/prompts, `ToolRunContext.concludeTurn()`, native timed user questions, and one storage-domain for routing identities and pending delivery bookkeeping. Chat and task execution remain in native Sessions. Preference bodies stay in OpenViking, accessed through the already-resolved installed runtime request closure.

**Stack:** TypeScript, Cordis, zod, Vitest, real Loader/application composition, existing JSONL Session persistence and domain storage.

## Verified seams and constraints

- `sessionController.create({ workspaceId, sessionId, agentPreset })` creates an ordinary root; additionally await `workspace.attachSession(sessionId)` because the controller's own attachment is detached asynchronous work.
- `resolveAgent(id)` returns `{ agent } | { error }`; plugin deliveries use `agent.followup(createUserMessage(...))`, never the human-only `sessionController.prompt` route.
- `ctx.sessions.flush(agent.session)` is the durable inbox checkpoint. Persist a receipt only after it resolves and reconcile the stable message identity against native inbox/log state after interruption.
- Scoped tool registrations may shadow inherited tools. `tools.restrict({ allow: [] })` hides inherited capabilities; `tools.guard` enforces the final whitelist. Force `tools.presentAs('native')` so reserved PTC transport cannot remain exposed.
- A sole complete system-prompt section plus suppressed optional runtime context removes inherited prompt/catalog sections. The explicit skill-gesture pre-step listener is separate: the manager must reject/remove skill-invocation additions after downstream pre-step processing as well.
- Existing `user-questions/request` is not a durable wait. Managed workers receive a scoped `ask_user_question` replacement that persists/routes the question, returns an explicit pending outcome, and calls `exec.concludeTurn()`. Do not fabricate empty answers or hold a tool promise indefinitely.
- Manager-to-human questions use the native timed question contract (including logged `timeout`, stable call ID and native pending result), conclude the current turn, and accept the native cold-reply path.
- Observe final `turn/end` and explicit worker reports. A completed turn is not a completed task. User cancellation, failure, waiting, explicit completion and ordinary turn completion remain different outcomes.
- Current installed OpenViking globally auto-captures ordinary root sessions. Production and dev share its source. Any exclusion change must use a development-only source copy with an explicit opt-out contract, not mutate the linked production source or monkeypatch private runtime state.

## Package and restricted scope

**Create:**
- `packages/session/session-manager/package.json`
- `packages/session/session-manager/tsconfig.json`
- `packages/session/session-manager/src/index.ts` — Host service, reversible lifecycle wiring, human-only adoption/detachment/resume command.
- `packages/session/session-manager/src/state.ts` — schema-validated management links, creation operations, questions, outbox/receipts; no task-state machine.
- `packages/session/session-manager/src/tools.ts` — own-scope management tools and managed-worker-only reporting/request tools.
- `packages/session/session-manager/src/questions.ts` — scoped business-question routing and native manager-to-human question consumer.
- `packages/session/session-manager/src/preferences.ts` — restricted existing-runtime adapter, provenance, scoped lookup/correction/deletion and visible unavailability.
- `packages/session/session-manager/manager.patch.yml` — opt-in persistent Host row and trimmed `管理模式` preset; do not modify standard/omni defaults.
- `packages/session/session-manager/README.md`, `README.zh.md` — operating contract, model-visible surfaces, limits and validation evidence.

**Modify:** root `tsconfig.host.json`, generated `tsconfig.paths.json` aliases, `apps/cli/package.json`, and the resulting lockfile. Follow the required five-piece new-package build process. Release apps must not depend on a newly experimental package, so this additive Session-role package is not placed in the experimental group.

**Tests first:** `tests/isolation.host.spec.ts` proves actual scoped schemas and execution deny shell/files/browser/MCP/subagent/plugin-install/skill/PTC capabilities even when mounted globally, and proves another ordinary agent is unchanged. Include an explicit `/skill-name` injection regression and reversible disposal/reload.

**Red → green:** run the new isolated test and observe the missing feature assertion fail; implement scope installation; rerun it and the existing tools/system-prompt regressions. Commit only verified code.

## Explicit ownership and ordinary creation

**Tests first:** `tests/creation.host.spec.ts` covers cross-workspace membership, independent preset, ordinary-root identity, stable creation-key retries, attachment failure, outbox failure/recovery, invalid workspace/preset and manager self-preset rejection. Prove unadopted conversations in the same workspace remain untouched and workers cannot directly invoke manager creation.

Implement one-owner links, manager identity derived from the calling Agent, and human-only `/manage adopt <session-id>`, `/manage detach <session-id>`, `/manage resume <session-id>` controls. Reject runtime subagents, manager workers, conflicting owners and archived targets. Reusing an operation key with different creation input fails rather than silently changing the operation.

Persist a preallocated Session ID before creation. Await validated workspace attribution before delivering the initial task. Retain recoverable partial operations on failure, with a visible diagnostic. A worker's creation request is durable, wakes only its owner, and creates nothing until the manager accepts; the manager may reject it without creation. An accepted requested conversation belongs to the same manager.

Delivery identities are stable, plugin-attributed and schema-preserved in the native log. Never infer human authorization from internal message text. Match pending inbox and admitted message identities on recovery before sending again.

## Questions, reports and event-driven recovery

**Tests first:** `tests/questions.host.spec.ts` and `tests/recovery.host.spec.ts` cover business questions, no blocked tool promise, actual turn termination, manager answers, human escalation, partial answers, duplicate/cold replies, unrelated workers, attachments, no polling, stop/archive/detach and failed delivery.

Persist the original question identity/options and source worker. A worker returns pending and concludes its turn. New unrelated workers remain runnable; do not manufacture a paused task-state engine. A manager can answer from current instructions or scoped preferences, otherwise uses its native timed `ask_user_question`. The manager ends its current turn while waiting. Answers resolve only the original IDs; duplicates are idempotent and conflicting repeats reject. Native admitted attachment references can be forwarded from the actual manager user message; opaque per-Session upload receipts cannot be reused in another Session.

Native `session/event` plus explicit `worker_report` produces summaries keyed by source event/turn. Normal completion is reported as turn-ended, never task-complete; explicit completion, waiting, cancelled and error reports have separate labels. Recover missed reports by folding persisted native events, not by polling status or `whenIdle()`.

At startup and relevant native events, reconcile pending operations/outbox against durable native state. Recheck ownership/archive/membership and the latest user cancellation before every automatic wake. User stop/archive/detachment must prevent revival, including racing reply delivery. Recovery is event-driven; a transient error remains visible and durable for a later valid recovery trigger rather than becoming a silent success.

## Restricted OpenViking reuse

**Tests first:** `tests/preferences.host.spec.ts` covers manager-only access, backend identity/config reuse, no arbitrary URI/HTTP or unrelated resource access, explicit lasting preference evidence, sensitive/temporary-approval rejection, scoped precedence, visible outage, correction/deletion and immediate cache invalidation.

Use the installed runtime's resolved `client.fetchJSON` closure after validating its narrow shape; do not import private package subpaths, expose credentials, start a second memory server or add a preference database. Restrict operations to the caller's preference subtree. Results expose URI, scope and evidence, never imply authorization, and do not claim success on backend error.

The source must be a real user event containing explicit lasting preference intent. An assistant/tool/internal message cannot authorize a write. Temporary approvals, secrets and credentials are not captured. Current user instruction outranks project preference, which outranks global preference.

Add the minimum explicit manager opt-out to a dev-only copy of the installed OpenViking backend and point only the dev profile at that copy. Its nonmanager behavior and request identity must remain unchanged. Test the opt-out with the actual backend plugin lifecycle, not a runtime-method monkeypatch. Preserve the upstream/local delta and dependency provenance for later reviewed promotion.

## Build, integration, review and delivery

Run from `/home/sx/projects/MyAI/deepseek-harness-dev`:

```bash
pnpm run gen-tsconfig-paths
pnpm install --registry=https://registry.npmmirror.com --prefer-offline
pnpm exec vitest run packages/session/session-manager/tests
pnpm run build:lib:host
```

Use a real Loader/application test containing storage, Session persistence, agents/loop, tools/prompt, workspace registry, controller, user questions, manager and an unrelated globally mounted tool. Verify the model-request payload, not only registry methods. Add cold restart cases with a new application reading the same storage.

Only after a successful build and composition load: install/enable the package and preset in `/home/sx/.dsh-dev/profiles/web`, validate the profile, restart only `dsh-web-dev.service`, and refresh/inspect `http://127.0.0.1:3081` in the existing browser. Do not start a replacement server or touch 3080. Verify real manager-only tool visibility, cross-workspace Session attribution, native question card/late reply, asynchronous reports and cold recovery. Use deterministic composition tests for crash windows that cannot be safely forced in a live UI.

Review the final diff against the approved design and minimalism/security constraints. Run the final affected tests and full mandatory Host build after any fixes. Update the approved design's status and actual validation evidence; do not mark untested acceptance cases complete. Commit only the feature's files, leave unrelated root/submodule/worktree changes alone, and report the branch, validation and dev-only deployment state. Production promotion is explicitly excluded.
