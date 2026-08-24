# Result — P5.S3: Board, summary and event-detail read endpoints

**Status: done.** The four read endpoints the plan asks for are live, every landing number
reproduces the landed grounding pack (shapes exactly; counts drift by two days, as expected), and
both open questions the plan hands this slice now have stated, settings-overridable defaults.

## What landed

### The endpoints (`mijual.web.routers`)

| route | serves |
|---|---|
| `GET /board/summary` | one `BoardSummary`: 감시 중 · 30일 이내 · ② 진행 중 · 추후결정 · 소멸 앞둔 · 읽은 실적보고서 · 「추정」 718.1억원 + 548.7억원 band edge · 소멸/발행 증서 · 소멸률 · `next_lapse{date,corp_name,target}` · `freshness{as_of,stale,age_hours,stale_after_hours}` |
| `GET /board?rights=R1\|R2\|R3` | whole-board tab `counts`, D-day-ascending `rows` (`days >= 0`), the pinned `open_now` (② 진행 중) and `tbd` (일정 추후결정, unranked) strips, `reference`, `freshness` |
| `GET /events/{rcept_no}` | the detail card — identity (본문 disagreement stated, never corrected), countdown, gate-passing fields with citations, ① `offering` / `lapse_result` / `issuer_disagreement`, ② `convertible` fact strip, 철회 `withdrawal` evidence, `corrections` teaser |
| `GET /events/{rcept_no}/corrections` | the CorrectionStory — version rail with `is_current_readable` on exactly one row, `field_moves` and `interpretation` verbatim |

**Route key: `rcept_no`** (recorded), resolved against **every** stored `FilingVersion` and ordered
**renderable-event-first**. That second half is not decoration: 840 stored `rcept_no` values sit
under two event keys (N21 pairing residue), and ordering by 접수일 alone opens 계양전기's
`superseded_by_pairing` twin and 404s a row the board is showing. Found by the live curl pass.

### Supporting work

- **`mijual.web.reads`** — the batched read layer (routers stay transport-thin). The board answers
  in **4 queries for the whole page**, not 4 per row, and loads only the governing countdown field
  per event because a board row renders no field values.
- **`mijual.gates.exposure.exposure_of(event, version=…, rows=…, facts=…)`** — the exposure
  derivation split out as a pure function; `event_exposure` is now just its loading half. One
  definition, two callers (per-event and batched).
- **The version-selection near-miss (S1 note 5) closed by moving, not forking**: `readable_versions`
  / `document_of` / `current_version` now live in `mijual.db.repository`, with
  `mijual.extract.runner` re-exporting them. Every existing caller untouched; the gates, the
  exposure contract and the 철회 detector lost their function-local `import mijual.extract.runner`.
  Verified: importing `mijual.web.app` loads none of `mijual.dart` / `collect` / `extract` /
  `estimate`. New `current_versions` (batched, no decode) is the same rule — **0 divergences
  measured over all 488 exposable events**.
- **The estimate-import blocker closed by a persisted precomputation** (the plan's sanctioned
  route): new table **`offering_input`** (① `EventInputs.as_json()` + `price_confirmed` /
  `subscription_start` / `subscription_end` / `decision_rcept_no` as SQL-filterable columns) and
  additive column **`performance_report.lapse`** (`LapseRow.as_json()`), both written by the new
  worker **`python3 -m mijual.estimate snapshot`** (0 requests, 0 LLM calls, idempotent, additive —
  `create_all` + `ensure_columns`, no Alembic). The request path reads those mappings through
  `present.offering_inputs` / `present.lapse_result`, which now accept an object *or* its stored
  JSON.
- **`mijual.present` additions** (no endpoint re-derives a number): `board_row`/`board_offering`,
  `convertible_view` (R3's six ② facts), `correction_story`, `freshness`/`Freshness`,
  `lapse_totals`/`LapseTotals`, and `board_summary` now derives 소멸률 from the two counts with the
  same 4-decimal quantization `LapseReport` uses.
- **`BodyDocument.company_name`** — the `<COMPANY-NAME>` the filing prints, read once in
  `mijual.bodydoc` instead of being re-typed by each surface that compares it to the master name.

## The two decisions the plan asked for (both recorded in `phase.md`)

1. **Countdown target instant** — `next_lapse.target` = `next_lapse_date + 1 day at 00:00 KST`, i.e.
   **end of the 청약 day**, which is exactly R2's stated assumption (2026-09-04 24:00 KST). Behind
   `MIJUAL_COUNTDOWN_CUTOFF_TIME` (`"24:00"` default, or `"HH:MM"`), so the operator's real 접수 마감
   시각 lands with no code change. `mijual.present` still refuses to invent one; the policy is the
   service's (`mijual.web.reads.countdown_target`). **The open question remains the operator's.**
2. **Stale threshold — 18 hours** (`present.DEFAULT_STALE_AFTER_HOURS`, override
   `MIJUAL_STALE_AFTER_HOURS`), derived from the beat schedule: runs at 07:30 and 19:30 KST make the
   widest healthy gap 12 h and the first *missed* beat ~24 h, so 18 h is the smallest threshold that
   cannot fire on a healthy schedule and still fires on a miss. **기준시각 is defined as
   `max(Event.last_seen_at)`** — a corpus fact ("when did we last look at DART"), never the request
   time, so a dead worker leaves the board stale, never dark. `stale` and the floored `age_hours`
   are served; the client never computes staleness.

## Validation

| command | outcome |
|---|---|
| `.venv/bin/python -m pytest` | **83 passed, ~1 s** (baseline 75 → 83: +3 in `tests/test_present.py`, +5 in the new `tests/test_web_board.py`). No network, no model, no DB service — the router tests run the app through `create_app()` over an in-memory SQLite corpus with `get_session` overridden. |
| `python3 scripts/workflow.py validate` | **passed** |
| `.venv/bin/python -m mijual.estimate snapshot` (out-of-suite) | 543 ① events precomputed (54 priced), 32 lapse rows (29 valued) — matches `headline-numbers.md`'s 32/29/3 |
| out-of-suite curl pass (`docker compose` Postgres :5433, `.venv/bin/uvicorn … --port 8099`) | every endpoint 200/404/422 as intended; server stopped afterwards |

### Curl pass, measured 2026-08-22 against the pack's 2026-08-20

Shapes exact, counts drift as expected:

- 488 exposable (**50 / 422 / 16** ✓) · 389 ranked rows · **57** ② 진행 중 · **4** 추후결정 · 38 past
  ①/③ off the landing (389+57+4+38 = 488 ✓) · within_30d 33 (pack 34, two days later).
- The pack's ② `지남` was 56; today's 57 is date drift, and S2 note 10's narrower "진행 중" definition
  currently excludes nobody — **0** ② in the corpus has a fully-closed 전환청구 window.
- 소멸 앞둔 **15** ✓ · 읽은 실적보고서 **69** ✓ · headline **71,812,971,649원 = 718.1억원** ✓ · floor
  **54,871,647,923원 = 548.7억원** ✓ · 소멸 **51,253,956** / 발행 **365,527,824** ✓ · 소멸률 **0.1402**
  = 14.02% ✓.
- 계양전기 `20260724000546`: D-3 (pack D-5), `price_confirmed: false` and **no money key anywhere**,
  배정비율 `0.2314082845` to ten decimals, 할인율 with its verbatim quote + span, 6 fields.
- 한화솔루션 `20260720000067`: 소멸가치 **20,635,460,625원 = 206.4억원** ✓, 증서 1주 5,525원 ✓.
- 대한광통신 `20260223002079`: `issuer_disagreement` with both readings cited and `used` on 발행−청약.
- ② `20250820000220`: the six-fact strip, `fields: {}` (sparse ②). ② `20250930000508`: 풍전약품 vs
  본문 에스씨엠생명과학 → `corp_name_agrees_with_body: false`.
- ③ `20260811000467`: 반대의사 통지 마감 D-5, two-step windows inside `dissent_notice_procedure`.
- 철회 `20260205000605`: `notice_ko` + `withdrawal{rcept_no,item,before,after,span}`, empty fields,
  dateless countdown, **no** offering / convertible / 정정 teaser.
- 경남제약 `20260623000409`: 추후결정 fields carry no value and no date; the other three render.
- suppressed `20260413002472` → **404 envelope**, `?rights=R9` → **422**, both with **no Korean**.
- Timings/sizes: `/board` 160 KB in ~54 ms, `/board/summary` ~98 ms, a detail 6–15 ms.

## Findings worth the reviewer's attention

1. **D4's trigger has fired and is wider than the deferred note assumed.** 7 figures across **4**
   companies (SKC, 에스에너지, **루닛**, **한화솔루션**) carry a citation cell that does not state the
   number it backs — 청약 is a sum of two table rows while `raw`/`span` point at one addend
   (한화솔루션: 38,430,497 against a cell reading 38,427,609). The note named two companies.
   **Landed interim fix:** `present.money._cited_count` attaches `quote`/`span` only when the cell's
   text parses to exactly that number; otherwise the value keeps its `rcept_no` (the DART link still
   resolves) and carries no verbatim chip — a false citation is worse than none. **Recommendation:
   promote D4 as a fix slice** so those figures become properly citable (a span per addend);
   `P5.S13`/`P5.S14` must not re-attach a one-addend quote.
2. **The snapshot worker is not yet a beat stage.** Wiring it would change `PipelineConfig.stages`'
   default and edit `tests/test_scheduler.py`, outside this slice. **`P5.S9` (already in the
   scheduler for the run log) or P4 must wire it**; until then it runs by hand after a `collect`, or
   the ① extras and the headline age while 기준시각 says the corpus is fresh.
3. **`next_lapse` names 퓨쳐켐, the landed R2 card shows 계양전기.** Three offerings share 청약 마감
   2026-09-04; the pipeline's `min()` was order-dependent, the API sorts `(마감일, 접수번호)` —
   deterministic and collation-independent. The strip's numbers are live by contract, so this is
   data, not a design deviation, but `P5.S12`/`P5.S19` will see a different company than the card.
4. **`P5.S12` still owns one rendering choice**: R2's ① extras cell says `청약 YYYY-MM-DD` without
   saying which end of the 구주주 window that is, so the row carries both (`subscription_start` /
   `subscription_end`) and the surface picks.

## Deviations from `plan.md`

- **The version-selection refactor took the "materially better route" the plan invited.** Besides
  lifting `readable_versions` / `document_of` into `mijual.db.repository`, `current_version` itself
  moved there (re-exported by `gates.exposure`, so every caller is unchanged), `current_document`
  was added so a detail request decodes the 본문 once, and `exposure_of` was split out of
  `event_exposure` so the board can batch its loading without a second copy of the exposure rule.
  Reason: the plan's minimum would have left the board either looping four queries per row or
  re-implementing `FieldView` construction in the web layer.
- **The precomputation is a new table plus one additive column, not only a column.** ①'s money
  inputs are per *event* and the 소멸 rows are per *실적보고서*; one store could not carry both without
  denormalizing. Both are additive and Alembic-free, as the plan requires.
- **`_cited_count` gained a citation guard** (finding 1). This edits S2's layer, which the plan did
  not anticipate; the alternative was serving a citation that does not back its number.
- **The board's ② 진행 중 strip and the 추후결정 strip report `count` (this response) and `total`
  (whole board)** rather than one number, because `?rights=` filters rows but must not change what
  the other tabs hold.
- No `docs/` versions were created — durable-truth changes are recorded in `phase.md`'s *Doc impact*
  for `P5.REVIEW` to consolidate (`api`, `backend`, `architecture`, `data`, `operations`,
  `decisions`, `qa`).
