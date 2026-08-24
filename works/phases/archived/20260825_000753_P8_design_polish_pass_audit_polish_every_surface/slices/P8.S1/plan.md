# Plan — P8.S1: AskWidget `t1` 중복 키 — collision-free turn ids after a restored thread

Orchestrator plan, written inline (auto mode) on 2026-08-23. Executor: `slice-executor-high`. Kind `fix`, risk `high`.

## Context (read `phase.md` § "`t1` root cause" first — it is verified)

- `frontend/lib/ask.ts:252–255`: module-scope `let counter = 0; nextId() → \`t${counter}\``; restarts at 0 on every full page load.
- `hydrate()` (`ask.ts:438`) installs sessionStorage turns already named `t1`, `t2`, … without advancing the counter, so the first `ask()` after a reload mints `t1` again.
- Symptom is the React duplicate-key warning at `frontend/components/ask/AskWidget.tsx:96` and identically `AskPage.tsx:99` — **but the id is also the store's lookup key**: `patchTurn` (`ask.ts:285`, rewrites every match), `history(exceptId)` (298), `retry(turnId)` (485, first match). A collision streams one answer into two turns and retries the wrong turn. This is a data bug.
- Persistence: `THREAD_KEY = "mijual.ask.thread"`, `Persisted.v === 1`, `readThread` rejects other versions and does not inspect id format. **A thread persisted by the current build (ids `t1…`) must still hydrate after the fix** — no version bump.

## The fix (decided here)

Make turn ids **collision-free at the source** rather than re-seeding a counter:

- In `frontend/lib/ask.ts`, replace `nextId()` so a fresh id can never equal a restored one: use `crypto.randomUUID()` when available (browser + Node ≥19), falling back to a per-module random/time-based prefix plus the counter (e.g. `` `t${Math.random().toString(36).slice(2, 8)}-${counter}` ``) when it is not. Keep the `t` prefix convention if you like; no component or test depends on the id format (verified: `ask.test.ts`, `AskWidget.tsx`, `AskPage.tsx` only use `turn.id` as key / `retry` arg).
- Do **not** change `Persisted`, `readThread`, `writeThread`, or `settle`. Legacy `t1…` ids restored from storage stay as they are; they only need to be distinct from new ones, which they now are.
- Keep the one-file footprint: `lib/ask.ts` plus one terse test case. Do not touch the components.

## Test (terse — repo rule: minimal high-value cases)

Add **one** case to `frontend/lib/ask.test.ts` (no framework; run via `cd frontend && npm run smoke` → `node --test "lib/*.test.ts"`): seed `sessionStorage` (or the store's equivalent hook — `createAskStore` is exported; look at how the existing four cases set the environment up) with a `v: 1` thread holding turns `t1`, `t2`; `hydrate()`; `ask("…")`; assert the new turn's id is not `t1`/`t2` and that the thread now has three distinct ids. If the existing test harness has no `window.sessionStorage` shim, the smallest shim inside the test file is fine — no fixture sprawl.

## Verify

1. `cd frontend && npm run typecheck && npm run smoke` green (smoke currently 15/15 → 16/16 with the new case); `npm run build` green.
2. **Restored-session repro in the operator's runtime** (`## Operator Runtime`, `docs/current/operations.md`): dev stack via `make stack-up` (already-running stack is fine — `make stack-status`), origin `http://127.0.0.1:3000`, dev mode. Open the AI 질문 widget, ask a question (any — a refusal or an answer both mint a turn), reload, ask again: **no** "Encountered two children with the same key" in the console, both turns render, and a 재시도 on the newer turn retries that turn only. Drive the browser with whatever tooling the repo already used for P7's sweeps (see `works/phases/active/P7/slices/P7.S9/result.md` for how it was done — reuse it); if no browser automation is available to you, **say so plainly** in `result.md`, verify at the store level (test) + build/smoke, and write the exact manual repro steps so the orchestrator runs them in Chrome at the same origin. Do not claim a browser check you did not do.
3. `python3 scripts/workflow.py validate`.

## Record

- `result.md` in this slice folder: what changed, the id scheme chosen, test output, the repro result (or the honest "not browser-verified here" + steps).
- `phase.md`: one line under `## Doc impact` — the qa doc's `## Regression Checklist` gains `- [ ] AI 질문: ask → reload → ask again renders two distinct turns, no duplicate-key warning, 재시도 hits the right turn (P8)`; and a note under `## Findings & Notes` if anything about the store surprised you (for R14/`P8.S15`, which will touch this surface).
- `## Operator Questions`: only if a genuine operator decision surfaced (unlikely here).

## Don't

No restyling, no copy changes, no other files, no commits, no status transitions, no `doc-new-version`.
