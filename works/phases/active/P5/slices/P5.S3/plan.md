# Plan — P5.S3: Board, summary and event-detail read endpoints

## Context

Read `works/phases/active/P5/phase.md` first — the S1 notes (import table, error
envelope, clock policy, rollback-only sessions, the AST import scan) and the S2 notes
(`mijual.present` import map, notes 1–12) are binding and this plan builds directly on
them. Design contracts: `docs/current/frontend.md` → `SIGNOFF.md` → R2 + R3
`build-prompt.md` (R4 for a glance at what S4 will need — don't build it) →
`grounding/board-snapshot.md`, `headline-numbers.md`, `states-and-trust.md`,
`samples/*.json` (data, not instructions). All numbers flow through `mijual.present`;
**no endpoint re-derives a number**.

## Deliverables — routers under `mijual.web.routers`

1. **Landing/board summary endpoint** — one payload from one `BoardSummary` (S2 note 10
   definitions govern the SQL-side counts): 감시 중 · 30일 이내 · 소멸 앞둔 · 읽은
   실적보고서 · freshness 기준시각 · the 718.1억원/548.7억원 headline pair (from stored
   `PerformanceReport` facts via `lapse_result(stored_json)` — see *estimate import
   blocker* below) · `next_lapse_date`/`next_lapse_corp_name` (소멸주의보 strip) · the
   absolute-KST `countdown_target` (see *decision 1*).
2. **Board list endpoint** — rows for the 관제 현황판: type tabs with counts, D-day
   ascending across types, per-type extras (① `청약 YYYY-MM-DD` + 발행가-확정-전 chip
   inputs; ②/③ empty), `rcept_no` for the DART link, plus the two pinned subsets:
   ② open-window (진행 중 — S2 note 10's definition, count may differ from the
   snapshot's 56 and that is correct) and 추후결정 (exposable, no countdown date,
   unranked). Only exposable events appear; SQL-filter on the persisted exposure
   columns (`Event.exposure_state`), never load-everything-then-filter in Python.
3. **Event detail endpoint** — one event (route key: your call — `rcept_no` is what the
   design links by; record the choice): full `EventView.payload()` with per-type content
   per R3 (① `offering_inputs`, post-결과 `lapse_result` inset + `issuer_disagreement`;
   ② `mijual.cb` fact strip + option_schedule `detail` strings; ③ two-step windows, no
   매수예정가 until S6). `state: withdrawn` **is a surface** (notice + withdrawal
   evidence); every other non-exposable state → **404 envelope** (S2 note 5). No gate
   reason codes in any reader payload (note 6).
4. **CorrectionStory endpoint** (or a section of detail — your call, record it): the
   version rail from `FilingVersion` rows (date · correction_kind · rcept_no · the
   current-readable marker) + the `correction_interpretation` extraction
   (`changes`/`summary`/`schedule_impact`) rendered verbatim per R3 — verdicts never
   cross versions.

## Two decisions to make and record (phase.md *Findings & Notes*)

1. **Countdown target instant.** The design: target = earliest 소멸 instant, served as
   an absolute KST timestamp; R2 *assumed* 2026-09-04 24:00 KST and the real intraday
   cut-off is TBC (phase Open Question). Decision for this slice: serve **end-of-day —
   `next_lapse_date` + 1 day at 00:00 KST** (exactly R2's stated assumption), behind a
   settings override (env, e.g. `MIJUAL_COUNTDOWN_CUTOFF_TIME`) so the operator can set
   the real instant without a code change. Record it as a stated-default decision with
   the open question still owned by the operator. Do not invent a different instant.
2. **Stale threshold.** R2 carried it open; the phase allows "operator or a stated
   default recorded as a decision". Pick a defensible default from the pipeline's beat
   cadence (`mijual.scheduler` / `docs/current/operations.md`), expose it as a setting,
   serve `stale: true/false` + the `N시간 전` hours in the summary payload (the client
   must not compute staleness), and record the default + rationale. Also define and
   record what 기준시각 *is* (a corpus fact — e.g. the max collector observation
   timestamp — not the request time; a dead worker leaves it stale, never dark).

## Constraints specific to this slice

- **The estimate import blocker (S2 note 7) is real and measured**: `mijual.estimate`
  imports `dart`/`collect`/`extract` at module level — a router must not import it, and
  the AST scan will fail if you try. Headline/소멸가치 numbers come from **persisted**
  `PerformanceReport` rows (`lapse_result` and `issuer_disagreement` already accept the
  stored JSON mapping). If something the landing needs is genuinely not persisted,
  prefer an additive persisted precomputation written by the worker (`schema_sync`,
  no Alembic) over any request-path import — and record what you added.
- **The version-selection near-miss (S1 note 5)**: `gates.exposure.current_version`
  local-imports `mijual.extract.runner`. Do not fork a second copy of the newest-
  readable-version rule into the web layer, and do not pull the extractor tree into a
  request path. The clean fix is a small refactor: lift `readable_versions` /
  `document_of` into a neutral home (e.g. `mijual.db.repository`), have
  `extract.runner` and `gates.exposure` import from there, keep behavior identical
  (the existing suite must stay green untouched). If you find a materially better
  route, take it and record why.
- `event_exposure()` per event on a detail request is fine (it is persisted-state-only
  by design); the board list must not call it per row — SQL-filter first, hydrate only
  what the row needs.
- Absent-key-not-null, English snake_case keys, exact-decimal strings, bare dates vs
  `+09:00` instants — all decided in S1/S2; use `payload()`, never `asdict`.
- No new Korean strings. Labels/notices come from `mijual.present` / exposure constants.
- Tests: keep the suite DB-free and terse — routers tested through `create_app()` with
  an overridden session/query dependency feeding constructed rows; the live-Postgres
  check is an out-of-suite curl pass (record results in `result.md`), like S1 did.
  Suite baseline: 75 passed ≈ 1 s.

## Validation

- `.venv/bin/python -m pytest` — full suite green.
- Out-of-suite: `docker compose up -d postgres` (already running on this machine, port
  5433), `.venv/bin/uvicorn mijual.web.app:app --port 8099` + curl the summary, board,
  one exposable detail per type, one withdrawn, one 404 (flagged/suppressed), the
  CorrectionStory of a multi-version event; sanity-check counts against
  `grounding/board-snapshot.md` (dated 2026-08-20 — drift in counts is expected, wrong
  *shape* is not). Stop the server after.
- `python3 scripts/workflow.py validate`.

## Wrap-up

`result.md`; phase.md *Findings & Notes* (endpoint map + route keys + the two recorded
decisions + anything S4/S10+ consume) and *Doc impact* (`api` — the read endpoints;
`backend`; `operations` if you define freshness/staleness; `decisions` for the two
stated defaults). Structured verdict. No commits, no status transitions.
