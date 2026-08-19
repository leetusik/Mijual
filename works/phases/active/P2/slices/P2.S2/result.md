# Result: P2.S2 — collector for ① 유증 + ③ 매수청구 (new filings **and** 정정 discovery)

Status: **done**. The collector runs end to end offline over the whole 2026 universe and live
under an explicit request ceiling; it is idempotent, it never drops a filing, and every exclusion
carries a reason code. Total live OpenDART spend for the slice: **291 requests** (cap was ~300).

## What landed

```
src/mijual/collect/__init__.py    public surface + why this layer exists
src/mijual/collect/targets.py     ① piicDecsn / ③ cmpMgDecsn (② is S7; 분할합병·주식교환 out, D-1)
src/mijual/collect/discovery.py   3-month window chunking, list.json paging, report_nm parsing
src/mijual/collect/pairing.py     정정 → original, nearest-earlier-ORIGINAL + corp-history widening
src/mijual/collect/filters.py     the two correctness filters (ic_mthn / mg_stn + aprskh_*)
src/mijual/collect/runner.py      the run: discover → pair → detail → filter → snapshot → persist
src/mijual/collect/__main__.py    `python -m mijual.collect --bgn … --end … [--offline] …`
tests/test_collect.py             5 terse cases, all against the P1 cache (no invented JSON)
```

Touched from S1 (small, additive):

- `dart/client.py` — `request_count` + `max_requests` → `RequestBudgetExceeded`. The daily quota is
  unmeasured (**O-1**), so a long run is bounded by construction rather than by trust. Cached reads
  are unaffected; only live fetches are refused.
- `db/models.py` — `CorrectionKind.from_report_nm` now buckets **any** bracketed prefix (see N19),
  `FilingVersion.pairing_method`, `Event.review_flags` + `add_flag()`.
- `db/repository.py` — `ensure_version(..., pairing_method=…)`, and it backfills `report_nm` /
  `pairing_method` on a version first seen without them.

## How the four hard parts are solved

**Discovery (never the detail endpoint).** `list.json`, `pblntf_ty=B`, KOSPI `Y` + KOSDAQ `K`, paged
to `total_page`, windows chunked to ≤ 3 months — `chunk_windows("20260101","20260818")` reproduces
P1's three sampling windows exactly. Originals **and** `[기재정정]` **and** `[첨부정정]` are all
recorded as versions; only 첨부-class versions skip the 본문 fetch (§4.1). Paging is done in the
collector rather than in `DartClient.filings` so that a mid-window failure keeps the pages already
read and reports the gap instead of silently losing the window.

**정정 pairing without 본문 parsing.** Same corp + same subtype, **nearest earlier _original_** —
deliberately not the spike's nearest-earlier *sibling*, which for a chain is the previous
*correction* (디모아 filed 6 against one 유증) and would have produced six different event keys. When
the window holds no earlier original, the collector widens **once per corp** with a corp-scoped
`list.json` query (no 3-month cap) reaching 3 years back. Every version records how it was attached
(`pairing_method`), including `*_ambiguous` when more than one original could plausibly be the
target — that column is the worklist for S3's `<CORRECTION>` 최초제출일 backfill.

**Unpairable corrections are recorded, never dropped** (plan §3). The correction becomes its own
event keyed on its own `rcept_dt`, is suppressed with reason `unpaired_correction` (so it can never
be published as a live right while its identity is unknown), and its chain-mates within 240 days
attach to that same placeholder instead of minting one event each. When a later run pairs the same
filing properly, the placeholder is re-suppressed as **`superseded_by_pairing`** naming the winner —
evidence is relabelled, never deleted (17 retired in the final run).

**Detail + 본문 snapshotting.** One detail call per `(corp, subtype)`, windowed on the **original**
접수일 (opened 30 days earlier as a cheap guard, same request count), never on a correction's date —
N3's 40/40 `[]` result. Rows are joined back by `rcept_no`; a row for a version `list.json` never
showed us (a correction filed after the window ends) is adopted as a `detail_only` version rather
than discarded. 본문 ZIPs are fetched only for versions with no `document` snapshot yet, which is
what makes re-running a window nearly free.

**The two correctness filters.** ① `ic_mthn ∉ {주주배정후 실권주 일반공모, 주주배정증자,
주주우선공모증자}` → `no_warrant_class`; `주주우선공모증자` stays **unsuppressed pending O-5**, and
the code says in as many words that `ic_mthn` is provisional and 본문 `18. 신주인수권양도여부`
(S3/S5) is the final test. ③ `mg_stn` 소규모/간이합병, or all of `aprskh_plnprc` /
`mgsc_aprskh_expd_bgd·edd` empty → `no_appraisal_right`. An event with **no** detail row is
*undecided*, not suppressed; an event whose detail rows **disagree** stays live and is flagged (see
N20 — this is what stopped a real 주주배정 유증 from being hidden).

## Evidence

### A. Offline, the whole 2026 universe — 0 requests, 0 key, 0 network

`python -m mijual.collect --bgn 20260101 --end 20260818 --offline --cache-dir scripts/spike/samples
--detail-window 20260101 20260818 --reset --no-documents`

```
discovery  : 3820 list rows scanned in 3 chunk(s) -> 1156 target rows original=319 기재정정=739 첨부정정=98
events     : 411 planned cmpMgDecsn=85 piicDecsn=326 | versions 1156
pairing    : earlier=348 earlier_ambiguous=120 original=319 unpaired=114 unpaired_chain=255 | corp-history queries 110
detail     : 344 call(s) -> 382 row(s), matched 349, adopted 16, unmatched 17, events without detail 82
filters    : live 35 (cmpMgDecsn=11 piicDecsn=24), undecided 8, suppressed no_appraisal_right=49 no_warrant_class=205 unpaired_correction=114
database   : (event, version, snapshot) (0, 0, 0) -> (411, 1172, 1521)
requests   : 0 live OpenDART request(s)
gaps       : [('20260101','20260331','K: page 11/14 CacheMiss'), ('20260401','20260630','K: page 11/15 CacheMiss')]
```

The gaps are honest and are P1's, not this collector's: P1 fetched 10 pages per window, so KOSDAQ
Jan–Jun pages 11+ were never cached (see N23). The 110 corp-history queries all miss offline — which
is exactly why 114 events end up `unpaired_correction` here (≈26%, matching P1's own 10/40 = 25%).

**Ground-truth check against P1's field survey.** The P1 cache contains **33** `piicDecsn` rows whose
`ic_mthn` is warrant-bearing. After this run: **24 live, 9 suppressed as `unpaired_correction`,
0 missing.** Nothing in the ① universe was lost; the 9 are corrections whose original predates
2026-01-01 and whose corp history is not in the offline cache.

### B. Live, bounded — 2026-07-01 ~ 2026-08-19, KOSPI+KOSDAQ

`python -m mijual.collect --bgn 20260701 --end 20260819 --max-requests 240 --max-documents 30`

```
discovery  : 955 list rows scanned in 1 chunk(s) -> 348 target rows original=92 기재정정=230 첨부정정=26
events     : 172 planned cmpMgDecsn=34 piicDecsn=138 | versions 348
pairing    : earlier=69 earlier_ambiguous=91 earlier_history=41 earlier_history_ambiguous=40 original=92 unpaired=5 unpaired_chain=10 | corp-history queries 86
detail     : 158 call(s) -> 173 row(s), matched 158, adopted 13, unmatched 2, events without detail 24
filters    : live 27 (cmpMgDecsn=9 piicDecsn=18), undecided 22, suppressed no_appraisal_right=16 no_warrant_class=102 unpaired_correction=5
database   : (event, version, snapshot) (411, 1172, 1521) -> (434, 1226, 1595)
requests   : 240 live OpenDART request(s) — BUDGET EXHAUSTED
```

The ceiling did its job: the run stopped **cleanly** inside the document phase with everything
already collected persisted. Live, the corp-history arm works — 81 corrections paired through it
(`earlier_history*`) and only 5 stayed unpaired, against 114 offline.

Second pass over the same window (`--max-requests 34 --max-documents 8`) — **25 requests**, of which
17 were the detail calls the budget had cut off and 8 were 본문 ZIPs:

```
detail     : 158 call(s) -> 191 row(s), matched 175, adopted 14, unmatched 2, events without detail 6
filters    : live 31 (cmpMgDecsn=11 piicDecsn=20), undecided 4, ...
documents  : fetched 8, skipped 첨부정정 26, skipped suppressed 276
database   : (434, 1226, 1595) -> (434, 1226, 1612)
```

**Idempotency, measured:** events and versions did not move (434 / 1,226 → 434 / 1,226); only the 17
genuinely new bodies became snapshots. A third pass (the offline whole-2026 window again) added
**0 rows at 0 requests** and retired 17 stale placeholders.

### C. O-4 answered — KONEX, for 26 requests

`--corp-cls N --bgn 20260101 --end 20260819 --dry-run --no-pair-history`:

```
events 30 (piicDecsn=27 cmpMgDecsn=3) from 78 target rows
filters: live 0, suppressed no_warrant_class=25 no_appraisal_right=1 unpaired_correction=4
requests: 26
```

**KONEX adds zero exposable rights** in 2026-01-01~08-19: all 27 유증 are 제3자배정/일반공모 계열
and the single 합병 grants no 매수청구권. **O-4 is closed: including `corp_cls=N` changes no coverage
conclusion**, so KOSPI+KOSDAQ stays the frame. (`corp_cls=E` 기타 was not probed.)

### D. Final database state

434 events / 1,226 versions / 1,612 snapshots (1,210 `list`, 304 `piicDecsn`, 85 `cmpMgDecsn`,
13 `document` over 8 distinct `rcept_no`).

| suppressed_reason | events |
|---|---|
| `no_warrant_class` (① 제3자배정·일반공모) | 213 |
| `unpaired_correction` (원본 미발견, 검토 대상) | 99 |
| `no_appraisal_right` (③ 소규모합병 등) | 52 |
| `superseded_by_pairing` (뒤늦게 정상 페어링됨) | 17 |
| — (exposable) | **53** — ① 38 (30 with a detail row, 8 undecided), ③ 15 (14 + 1) |

**Consistency with P1's measured universe.** 30 decided-live ① events over 7.6 months ≈ **▷ 3.9/month**
against P1's ▷ 4–5/month; 14 decided-live ③ ≈ **▷ 1.8/month** against P1's ▷ 2/month. Restricted to
events whose *original* falls inside the live window (2026-07-01~08-19, 1.6 months) the collector
holds 4 exposable ① and 1 ③. Both densities are consistent with P1; neither is a census.

## Validation

| command | outcome |
|---|---|
| `.venv/bin/python -m pytest` | **14 passed** (9 from S1 + 5 new) |
| `.venv/bin/python -m mijual.smoke [--database-url sqlite:///…]` | **OK** — S1's fixture run still green after the model changes (run against a throwaway SQLite file so the collected Postgres data survives) |
| offline whole-2026 collect (above) | 411 events / 1,172 versions / 1,521 snapshots, 0 requests |
| re-run of the same offline window | **0 new rows, 0 requests** (idempotent) |
| live 20260701~20260819 ×2 | 434 / 1,226 / 1,612; second pass added no event or version |
| ground truth: 33 warrant-bearing ① filings | 24 live + 9 flagged, **0 missing** |
| key-leak grep (source, tests, docs, works, `var/`, cache filenames) | **0 hits**; recorded `_url` key-free |
| `python3 scripts/workflow.py validate` | OK |

## Deviations from `plan.md`

1. **Package, not a single module** (`src/mijual/collect/`, the plan left the choice open).
2. **Pairing takes the nearest earlier *original*, not the nearest earlier row.** The plan's wording
   (and the spike) says "nearest earlier original row"; spelled out because taking any earlier row
   breaks every correction chain. Same algorithm, one word load-bearing.
3. **Two small schema additions** (`FilingVersion.pairing_method`, `Event.review_flags`) and a
   behaviour change to `CorrectionKind.from_report_nm` (N19). Free under N16 — no Alembic, and both
   columns are plain `VARCHAR` so a new value never costs a migration.
4. **`RequestBudgetExceeded` added to the client.** The plan asked for ≤ ~300 requests; a hard,
   testable ceiling is a better answer than counting by hand, and it is O-1's mitigation until the
   quota is known.
5. **본문 ZIPs are not fetched for suppressed events by default** (`--documents-for-suppressed` opts
   in). ~90% of the raw universe is suppressed; fetching their 본문 would have cost hundreds of
   requests for text no MVP field reads. The ③ 소규모합병 events themselves are still fully
   collected (event + versions + detail snapshots), so the 6-overlapping-windows demo asset is intact.
6. **Live window is 2026-07-01~08-19, not 06-01~08-19.** Same shape, one chunk, and it keeps the
   whole slice inside the request cap; June is already covered by the offline pass.
7. **Only 8 본문 ZIPs were fetched live** (the first live pass spent its ceiling on discovery,
   pairing and detail). The 본문 path itself is proven twice over — S1's fixture plus these 8 — and
   S3 will pull the rest against its own budget.

## Open items handed forward

- **O-5 is now cheap to close:** exactly one `주주우선공모증자` event is in the corpus
  (`20260807000339`, 00232007) and it is collected, unsuppressed, with its versions — S3 need only
  read its 본문 `18.`.
- **O-1 still open.** 291 requests in this slice drew no quota error (on top of P1's ~1,002 in a
  session). Still unmeasured; the ceiling flag is the mitigation.
- `earlier_ambiguous` / `earlier_history_ambiguous` (145 versions) and `event_key_collision` /
  `detail_conflict` (36 / 3 events) are the concrete worklist for S3's `<CORRECTION>` backfill.
- 5 duplicate rcept_no pairs sit on two *placeholder* events (both suppressed) because the chain head
  depends on the window; 3 sit on two exposable events, all three flagged `detail_conflict`. See N21.
