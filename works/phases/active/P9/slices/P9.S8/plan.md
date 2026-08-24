# P9.S8 — client store: AskBlock union, keyed reduce, transient status, R16 copy

## Context

First frontend slice. The backend (S3–S7) now emits `status`, `data`, and `calc` frames with `block_id`/`persistent`, `text.unverified` spans, `done.filings`, and the 보안 family; the client store must carry all of it before S9 draws anything. Binding spec: `works/phases/active/P9/phase.md` → `### DECOMP2` → **`P9.S8` — the client store** (read in full) + `docs/reference/design/rounds/16-smart-assistant/output/build-prompt.md` §0 (the `frontend/components/ask/copy.ts` strings, verbatim — **4** start cards; the stale "5장" lines are overridden) and §1 (frame schemas as actually landed — read S3's and S5's `result.md` and the `### P9.S3`–`### P9.S7` decision sections in `phase.md` for the landed shapes, e.g. `StatusEvent` carries its signed `text` beside `phase` server-side, so **no status strings go into `copy.ts`**; `TurnEnd` carries `filings`; a tool-less turn emits no footer).

Current seams (verified): `frontend/lib/ask.ts` (582 lines) — `AskBlock` union at ~77, reducer `switch (frame.event)` at ~376 with cases `tool_row|citation|text|refusal|links|footer|done|aborted|error`, sessionStorage persistence under `THREAD_KEY` (~182, write-through at ~241). `frontend/components/ask/copy.ts` (249 lines).

## Scope

1. **`AskBlock` union grows**: `status` (transient), `data`, `calc` variants mirroring the landed frame payloads; `text` blocks gain `unverified` spans. Types stay additive.
2. **Keyed reduce (P10's client half)**: a frame with a `block_id` **replaces in place** the block with the same id; absent id keeps today's append. `calc` `pending → done|error` must not reorder the block.
3. **Transient status**: at most one live status line per streaming turn, replaced per phase, dropped at the first `text` block — and **never persisted to sessionStorage** (filter at the write-through).
4. **Turn metadata**: carry `done.filings` and the marker-count `blocked` semantics; the footer's 근거 N건 stays chip-count (existing behavior) — note S3's recorded interim: data-row chips are defined but not drawn until S9.
5. **`copy.ts` gains the §0 strings verbatim**: `CALC_VERIFIED` · `CALC_EXPR` · `TAG_CALC` · `TAG_UNVERIFIED` · `TAG_INPUT` · `CALC_RESULT` · `CALC_RUNNING` · `calcError` · `DATA_HEADING` · `SHOW_ALL` · `FOLD` · `DETAIL` · `trace` · `START_HEADING_KO` · `NEW_CHAT_KO` · `START_CHIPS_KO` (**exactly 4 cards**) · D1 `AGENT_INTRO_KO`. Do **not** remove the retired constants (`ANONYMITY_KO`-equivalent, the 검증 line, `REASK_KO`-equivalent — whatever their real names are) — S10 removes them **with their call sites** so the build never breaks in between.
6. New `switch` cases stay additive — both views must keep rendering mid-build (S9 draws the new blocks; until then unknown-block rendering must be a safe no-op, not a crash).

## Constraints

- RESPECT THE DESIGN: §0 strings byte-verbatim; no invented Korean.
- Terse tests (smoke additions only where high-value); `npm run typecheck` + `npm run smoke` + `npm run build` + full Python suite (should be untouched) + `python3 scripts/workflow.py validate`.
- Doc impact + durable notes to `phase.md`; `result.md`; structured verdict. Never commit or transition state.
