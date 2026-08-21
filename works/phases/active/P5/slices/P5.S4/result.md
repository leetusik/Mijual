# Result — P5.S4: 내 종목 조회 endpoints

The lookup surface's backend exists: a stock resolves server-side, its live rights come back
ranked, and its 2026 놓친 돈 comes back as **factors, not products** — no holding count reaches
the server on any path, and there is no parameter that would accept one.

## What landed

| file | what |
|---|---|
| `src/mijual/web/routers/stocks.py` | **new** — the two routes (`GET /stocks?q=`, `GET /stocks/{corp_code}`) |
| `src/mijual/web/reads.py` | `resolve_corp` · `stock_by_code` · `load_stock` + the private loaders; `_countdown_rows` → `_field_rows(…, fields=…)`; `_pending_lapses(…, corp_code=…)` |
| `src/mijual/present/summary.py` | `LapseTotals.payload()` — a **subset** total with the same fact/estimate split `BoardSummary` makes |
| `src/mijual/present/event.py` | `_bare_name` → public `bare_name` (one definition of "the same company, written differently") |
| `src/mijual/present/__init__.py`, `src/mijual/web/app.py`, `src/mijual/web/routers/__init__.py` | exports / router wiring |
| `tests/test_web_stocks.py` | **new** — 4 terse DB-free cases (SQLite + `get_session` override) |

### The route map

| route | serves |
|---|---|
| `GET /stocks?q=<종목명\|종목코드>` | resolution **and**, on a hit, the whole page: `{query, found, stock, reference, rights, lapse}`. A miss is `200 {"query": …, "found": false}` — a search that finds nothing is a result, not an error, and R4 renders its own locked 검색 불일치 sentence |
| `GET /stocks/{corp_code}` | the same page by stable handle (R3's "내 보유량으로 환산 →" link-out). Unknown code → **404 envelope** (`resource: "stock"`), because that is a link to a resource that does not exist |

`rights` = `{count, rows[]}`; each row is `EventView.payload()` (identity · countdown · the four
loaded fields) plus `offering` (full `OfferingInputs`) on ① and `convertible` (R3's six-value strip)
on ②. `lapse` = `{coverage, totals, rows[], pending?}`.

## Recorded decisions

1. **Matching semantics** — four tiers, each unique-or-decline: 종목코드 exact (digits, zero-padded
   to 6) → 회사명 verbatim → 회사명 normalized (legal form / spacing / case, via
   `present.bare_name`) → **unique** normalized prefix. Ambiguity is a miss, never a pick.
   Measured 2026-08-22: 0/614 normalized-name collisions, and **13 names are a strict prefix of
   another's** (금양/금양그린파워, 디와이/디와이디…) — which is exactly why tier 3 precedes tier 4.
2. **Unknown stock vs stock with no rights** are structurally distinct: `found: false` (nothing
   else in the payload) vs `found: true` with `rights.count == 0` and `totals {offerings: 0,
   valued: 0}` and **no money keys at all** — no figure, no zero. Every `Corp` row is resolvable;
   measured 614/614 corps have events (`ensure_corp` only runs while creating one), so
   "resolvable" and "has events in the corpus" coincide today, and if they ever diverge the reader
   lands on the honest no-event empty state rather than on 검색 불일치.
3. **Live-rights ordering**: upcoming (`days >= 0`) D-day ascending → ② 진행 중 (opened, not
   closed) most-recently-opened first → 일정 추후결정 unranked, last. A deadline you can still act
   on outranks an open window with nothing to exercise (R4-4); past ①/③ are not here at all.
4. **The lookup ① row carries the detail-grade `offering`**, not the board's slim extras cell: R4
   owns the N주 conversion, so it needs 배정비율 (ten decimals), 초과청약 비율, `unit_value` +
   floor, and `final_price_date`. `price_confirmed` is on both shapes, so a client that reads only
   that key works against either.
5. **The 놓친 돈 row's event-derived block is gated on `state == "exposable"`** — `event_id`,
   `rcept_no`, `countdown` (the 매매기간 D+n) and the 매매기간 `Citation` appear only for a
   renderable 유상증자결정. Two corpus rows (한솔테크닉스, 트리니티항공) are linked to *flagged*
   events: they keep their 소멸 계산 (the 실적보고서 attests it) and lose the 기간 line, the quote
   and a link that would 404. `lapse` still carries 배정비율 + `unit_value`, so the N주 math
   survives the degraded row.
6. **Coverage** is served, never assumed by the client: `{start: 2026-01-01, end: <today KST>,
   convertible_start: 2025-06-01}`, matching the corpus's own collection windows
   (`estimate collect --bgn 20260101`, `collect --bgn 20250601`) and R4-3's fixed line. Membership
   is the offering's 청약 종료일 (fallback: the report's 접수일 — a guard, not a path: all 32 stored
   `lapse` rows carry one). A 2025 offering is **absent**, not zero.
7. **Citations**: the 매매기간 quote (single-span 본문 field) attaches per row; the summed
   실적보고서 figures keep S3's `_cited_count` guard untouched — verified live that SKC's and
   한화솔루션's 청약 counts come back with `rcept_no` and **no quote**, so D4 was not re-triggered.
8. `issuer_disagreement` rides on the row when the filing contradicts itself (대한광통신), because
   `ui-traps` #2 is a payload rule, not a detail-page rule.

## Validation

| command | outcome |
|---|---|
| `.venv/bin/python -m pytest` | **87 passed, ~1.0 s** (baseline 83 → +4), no network, no model, no DB |
| `python3 scripts/workflow.py validate` | **Workflow validation passed** |
| `.venv/bin/python -c "import mijual.web.app; …"` | no `mijual.dart` / `collect` / `extract` / `estimate` in `sys.modules` — the request path stays clean with the new router |

**Live curl pass** — `.venv/bin/uvicorn mijual.web.app:app --port 8011` against the local Postgres
(:5433), server stopped afterwards. All figures cross-checked against
`grounding/headline-numbers.md` (dated 2026-08-20; values drift, shapes do not):

- `q=계양전기` / `q=012200` / `q=계양 전기(주)` / `q=계양` → same corp, `found: true`. ① D-3
  (매매기간 마감 2026-08-25), `price_confirmed: false`, **no money key anywhere**,
  `final_price_date 2026-09-01`, 배정비율 `0.2314082845`; `lapse.pending {count: 1,
  subscription_end: 2026-09-04}` — the pack's "가장 빠른 청약 마감 2026-09-04, 계양전기" ✓
- `q=없는종목이름` → `200 {"query": …, "found": false}`; `/stocks/00000000` → 404 envelope, no
  `message_ko`; `?q=` → 422 envelope (our own client's bug)
- `q=한화솔루션` → 소멸 3,734,925 · 확정가 22,100 · 증서 1주 **5,525** · 소멸가치
  **20,635,460,625원 = 206.4억원** ✓, 배정비율 `0.2465120994` (R4's own caption example),
  매매기간 2026-07-06~07-10 **D+43** with its verbatim quote
- `q=에스에너지` → 1,990,157주 · 14.22% · 848원 · 7.2억원 ✓ · `q=대한광통신` → 2,083,302주 ·
  16.2억원 ✓ **plus** `issuer_disagreement` with both readings and both spans (stated 2,117,937 vs
  derived 2,083,302)
- `q=고려아연` (no renderable rights, no 2026 lapse) → `found: true`, `rights {count: 0}`,
  `totals {offerings: 0, valued: 0}` — the no-event empty state
- `q=경남제약` (추후결정) → countdown `date: null`, `dday: null`, field `display: 추후결정` with no
  value, and 초과청약/발행가 산식 rendering normally beside it (`ui-traps` #4)
- `q=유티아이` → four ② rows ordered D-91 · D-280 · D-327 · **D+46 open last** — the recorded
  ranking, live
- Sizes/timings (local Postgres, warm): **1.1–5.7 KB in 8–24 ms** per stock

## Deviations from `plan.md`

None in substance. Three judgment calls the plan explicitly left open, recorded above and in
`phase.md`: the route shapes (decision above), a search miss served as `200 … found: false` rather
than a 404 (the 404-not-explained rule still holds — the payload names no reason), and the
event-derived gate on 놓친 돈 rows (decision 5), which is stricter than the plan's wording and
follows the phase's "the exposure contract is not re-decidable" constraint.

Two small additions outside `mijual.web` were needed to keep "all numbers through
`mijual.present`" true: `LapseTotals.payload()` (a per-stock total is still a presentation shape)
and making `bare_name` public (so 종목 resolution and the 본문 identity check cannot mean two
different things by "the same company"). No new Korean string was introduced anywhere.

## Doc impact

Appended one line to `phase.md`'s *Doc impact* list (`api`, `backend`, `qa`) — no doc version
written here; `P5.REVIEW` consolidates. `data` is untouched: this slice persists nothing new.
