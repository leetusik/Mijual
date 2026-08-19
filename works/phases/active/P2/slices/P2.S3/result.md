# Result: P2.S3 — 본문 deterministic parse layer (labeled rows, `<CORRECTION>`, citation spans)

Status: **done**. `mijual.bodydoc` reads a 본문 snapshot as a pure function and returns typed
values that each carry a character span into **the snapshot as stored** — 23,493 / 23,493
extracted values re-slice to themselves across the 364 documents now held. The two persisted
jobs closed **O-5**, cut the `*_ambiguous` pairing worklist by **55 %**, identified **46 of 99**
unpaired corrections, and made the ① filter's final 본문 test real: **9 events suppressed with a
new reason code, 28 confirmed, 1 conflict kept live and flagged.**

Live OpenDART spend: **289 requests** (plan cap ~300). The whole persisted outcome is
**reproducible from the two on-disk caches at 0 requests** — proven by dropping the database to
its pre-S3 backup and rebuilding it (below).

## What landed

```
src/mijual/bodydoc/__init__.py     public surface + why the layer exists
src/mijual/bodydoc/document.py     BodyDocument / Span / Flat — offset-preserving decode
src/mijual/bodydoc/tables.py       nesting-aware TABLE/TR/TD·TH·TE·TU walk + ROWSPAN grid
src/mijual/bodydoc/labels.py       ① numbered labels → typed values with spans
src/mijual/bodydoc/correction.py   <CORRECTION>: target, 최초제출일 hint, 정정사항 before/after
src/mijual/bodydoc/sections.py     증권신고서 <TITLE> slicer (§5's other regime)
src/mijual/bodydoc/backfill.py     the two persisted jobs (hint backfill, ① 본문 filter)
src/mijual/bodydoc/__main__.py     python -m mijual.bodydoc {scan,backfill,warrants,show}
src/mijual/db/schema_sync.py       ensure_columns — additive-only DDL (see §Deviation 1)
tests/test_bodydoc.py              4 terse cases against the P1 cache (no invented XML)
```

Touched elsewhere (small, additive):

- `db/models.py` — `FilingVersion.hint_status` + `.pairing_note` (+ `pairing_is_ambiguous` /
  `pairing_is_resolved` / `note_pairing`), `Event.drop_flags()`.
- `collect/filters.py` — **O-5 closed**: `주주우선공모증자` removed from `WARRANT_BEARING_IC_MTHN`.
- `tests/test_collect.py`, `tests/test_db_models.py` — the O-5 change, and one case for
  `ensure_columns`.

`scripts/spike/*` untouched.

## The four hard parts

**Offset preservation.** The spike's `text_of` (`sub(r"\s+"," ", sub(r"<[^>]+>"," ", x))`) is
correct for a survey and useless for the product: it destroys positions, and §3.6 layer 2's
*원문 인용 스팬 존재* gate must answer *where in the stored snapshot does this value live*. `flatten()`
walks a raw range once, emitting tag-stripped / entity-decoded / whitespace-collapsed text while
recording per emitted character the raw `[start, end)` it came from (`array('i')`, so a 3.4 M-char
증권신고서 costs ~27 MB, not ~190 MB). A normalized slice therefore converts back to an exact raw
span even when the value was split by markup. The contract is *normalized* equality, not byte
equality — `doc.verify(span, value)` is `normalize(doc.text[span]) == normalize(value)` — because
the raw slice legitimately still holds tags. That one method is what S5's gate will call.

**Cells are `TD | TH | TE | TU`, not `T[DH]`.** The spike's cell regex silently dropped **every
value cell** of a 주요사항보고서: DART puts labels in `TD` and values in `TE` (free text/number with
a stable `ACODE`) or `TU` (typed unit with `AUNIT` + a machine value `AUNITVALUE`). Two further
markup facts had to be got right or nothing parses: `<TABLE\b` also matches DART's
`<TABLE-GROUP>` wrapper (which desynchronises the nesting depth and makes the whole body look
like one unclosed table — this cost the first implementation 46 of its 48 rows), and the ①
form leans on `ROWSPAN` so hard that `11. 청약예정일`'s value rows carry no label cell at all.
`cell_grid()` expands ROWSPAN/COLSPAN, so a `종료일` row still knows it is 청약예정일.

**Typed values, conservatively.** `AUNITVALUE` is preferred and the printed text is the fallback,
so `2026년 07월 28일` and `20260728` both land as `date(2026,7,28)` while the span still points at
the *printed* text (a citation must show what a human sees). Multi-date rows are **not** flattened:
`11. 청약예정일` yields four `LabeledValue`s distinguished by `qualifier`
(`('구주주','종료일')` …), each with its own span — `labels.qualified('subscription_dates',
'구주주','종료일').value == date(2026,9,4)`. Nothing is guessed about which 대상자 a caller wants.

**Nested-table text is kept, not collapsed to `[표]`.** In a `<CORRECTION>` the 정정 전 / 정정 후
cells are frequently whole nested tables (계양전기 `20260724000546`, `4. 자금조달의 목적`), so the
spike's marker threw the actual before/after values away. Nested tables are skipped for
*structure* (they must not contribute rows to their parent) and included for *text*.

## Evidence

### A. Parse coverage over every 본문 held (0 requests)

`python -m mijual.bodydoc --no-fetch scan --from-db`

```
documents  : 364
  11306 주요사항보고서(유상증자결정)   n=312  10/10-labels= 94  <CORRECTION>=308 hint=302  정정사항 rows=1235
  11344 주요사항보고서(회사합병 결정)  n= 52  10/10-labels=  0  <CORRECTION>= 52 hint= 52  정정사항 rows= 215
span check : 23493/23493 values re-slice to themselves
```

| measurement | result |
|---|---|
| documents carrying `18. 신주인수권양도여부` (i.e. the 주주배정 계열 form) | 94 of 312 `piicDecsn` documents |
| … of those, the 10 field-matrix §1.3 target labels | **94 / 94 at 10 / 10** — none missing |
| `<CORRECTION>` blocks parsed | **360 / 364** (the 4 without one are originals) |
| `2. 최초제출일` hint recovered | **354 / 360 = 98.3 %** (6 blocks state no date — see N29) |
| `3. 정정사항` rows parsed | **1,450** |
| every extracted value re-slices to itself | **23,493 / 23,493** |

P1 measured 10/10 labels on **9** filings and a parseable 정정사항 table on **40**; this is the same
result at 10× and 36× the sample, with spans added. The 218 `piicDecsn` documents *without* the
`18.` row are the 제3자배정 / 일반공모 / 주주우선공모 forms — a genuinely different template (see N28).

`--offline --cache-dir scripts/spike/samples scan` (the P1 fixture set, read-only, 0 requests)
also parses the two 증권신고서 and the CB/EB forms: 63 documents, 4,538/4,538 spans.

### B. 증권신고서 slicing — the regime that must never be read whole

| document | XML chars | `<TITLE>` sections | the section the MVP wants |
|---|---|---|---|
| `20260814004100` 증권신고서(지분증권) | 3,447,606 | 69 | `4. 모집 또는 매출절차 등에 관한 사항` → **33,780 chars** |
| `20260713000459` 증권신고서(합병) | 9,559,478 | 110 | `VII. 주식매수청구권에 관한 사항` → **38,033 chars** |

The slices tile the document (adjacent, non-overlapping), so every offset inside a section is
still a real offset into the stored snapshot and a citation span survives the slicing.

### C. `<CORRECTION>` backfill — the pairing worklist

Live, priority-ordered under the ceiling (`--max-requests`), then a consolidated pass:

| worklist | after `P2.S2` | after `P2.S3` |
|---|---|---|
| `*_ambiguous` version pairings | 145 | **66** (79 settled by the 본문 hint, **−55 %**) |
| `unpaired_correction` events | 99 | 99, of which **46 identified** by their own 본문 hint |
| `event_key_collision` events | 36 | 36, of which **9 carry `hint_split_evidence`** (본문 hints disagree → really 2+ events) and **10 lost a version to the hint** (`hint_split`) |
| `detail_conflict` events | 3 | 3 (unchanged — the hint does not speak to a detail-row disagreement) |
| exposable events | 53 (① 38 / ③ 15) | **44** (① 29 / ③ 15) |

Final consolidated run (`--no-fetch backfill`, 0 requests, idempotent — two consecutive runs print
identical numbers):

```
candidates : 803 기재정정 version(s) considered, 360 parsed, 354 carried a 최초제출일 hint, 1450 정정사항 row(s)
outcomes   : absent=6 confirmed=143 duplicate=22 identified=63 mismatch=106 no_document=443 reattached=20
ambiguous  : 66 version(s) | unpaired 99, identified 46 | collisions 36 (detail_conflict 3)
requests   : 0 live OpenDART request(s)
```

**20 versions were re-attached** by the hint, and the move is auditable: exactly 20 rows changed
`event_id` against the pre-S3 database backup, **0 rows removed and 0 added**, each carrying
`pairing_note` = `본문 최초제출일 X 기준으로 <from> -> <to> 이벤트로 재부착 (P2.S2 pairing_method=…)`.
`pairing_method` itself is left exactly as S2 wrote it — the pairing's real standing is the pair
`(pairing_method, hint_status)`, so evidence is relabelled and never overwritten.

The most instructive case is **이렘 `00116426`** — N20(b)'s mis-merge, undone: its
`piicDecsn/2026-02-04` key had collapsed **three** chains, and the hints say so in the data
(`20260206000766` → 2026-02-04, five versions → 2025-04-21, three versions → 2026-04-24). Two
versions moved to the real 2026-04-24 event, three were found already duplicated there
(`hint_duplicate`, N21's residue), and the key now carries `hint_split_evidence`.

### D. The ① filter's final test — 본문 `18. 신주인수권양도여부`

`python -m mijual.bodydoc warrants` — 38 events (29 live + the 9 it suppressed, re-derived every run):

```
outcomes   : confirmed=28 conflict=1 denied=9
```

- **28 confirmed** — 본문 `18.` reads `예` (and `- 신주인수권증서의 상장여부` = `예`); flagged
  `warrant_confirmed`. These are the ① events the product may publish.
- **9 denied → suppressed `no_warrant_bodymun`** (a new plain-string reason, no migration): the
  본문 has no `18.` row at all *and* `ic_mthn` is a non-증서 class. Eight of these were `P2.S2`'s
  **undecided** ① events (no detail row at collection time); the 본문 decided them.
  비비안 `00107677` / 코아스 `00210856` / 포커스에이아이 `01393721` … all 제3자배정증자, plus
  판타지오 `00231691` 일반공모증자 and 상지건설 `00232007` 주주우선공모증자.
- **1 conflict, kept live and flagged `warrant_conflict`** — **제이알글로벌리츠 `01415892`**
  (`20260205000605`): `ic_mthn = 주주배정후 실권주 일반공모`, but 본문 `18. 신주인수권양도여부 = 아니오`
  and `- 신주인수권증서의 상장여부 = 아니오`, at span `(16761, 16764)`. **This is the case that
  proves the whole check**: publishing on `ic_mthn` alone would have advertised a 증서 that does not
  exist. Per the plan and N20 it is **not** suppressed on conflicting evidence — see N30, which
  hands the exposure decision to `P2.S5`.

### E. O-5 — **CLOSED**

`python -m mijual.bodydoc show 20260807000339` (상지건설 `00232007`, the corpus's only
`주주우선공모증자`, 33,886 XML chars):

- its 본문 uses a **different numbered form** — `10. 청약예정일`, `11. 납입일`, `14. 신주의 상장 예정일`,
  `15. 대표주관회사`, `16. 이사회결의일`, `17. 증권신고서 제출대상 여부` — with **no `18. 신주인수권양도여부`
  row and no 신주인수권증서 rows at all**;
- the string `신주인수권` occurs **0 times** in the whole document.

**Answer: 주주우선공모증자 issues no 신주인수권증서.** `주주우선공모증자` was therefore removed from
`WARRANT_BEARING_IC_MTHN`, the event is suppressed `no_warrant_bodymun`, and the ① universe is
`주주배정후 실권주 일반공모` + `주주배정증자` only. Evidence is **one filing** (▷ the class
generalisation rests on the form template, not on a sample) — and because the 본문 check
re-derives the verdict from each document, a counter-example would surface as a
`warrant_conflict` rather than being silently hidden.

### F. Reproducibility and request spend

| run | purpose | live requests |
|---|---|---|
| `warrants --max-requests 40 --max-documents 32` | ① filter + O-5 | 27 |
| `backfill --priorities 0 --max-requests 120` | exposable events | 75 |
| `backfill --priorities 1 --max-requests 95` | ambiguous / collided | 95 (budget exhausted, stopped cleanly) |
| `backfill --priorities 1 --max-requests 45` | finish that list | 42 |
| `backfill --priorities 2 --max-requests 50` | unpaired placeholders | 50 (budget exhausted, stopped cleanly) |
| **total** | | **289** (cap ~300) |

Then the database was **dropped to its pre-S3 `pg_dump` backup and rebuilt entirely from the two
on-disk caches at 0 requests** — two offline `backfill` passes (P1 spike cache read-only, then
`var/dart-cache`) and two offline `warrants` passes. The rebuild converged to the same headline
state (44 exposable, 28 confirmed / 1 conflict / 9 denied, ambiguous 66, identified 46,
`hint_split_evidence` 9) **and strictly improved on the live-run state** by attaching 28 cached
documents the budget-interrupted live runs had fetched but never persisted (330 → 360 parsed).
Final: 434 events / 1,226 versions / 1,963 snapshots, **364 `document` snapshots** (was 13).

No key material anywhere: `grep -F "$DART_API_KEY"` over `src tests docs works scripts var`
returns **0 files**, and 0 of the cached JSON envelopes contain it (the key reaches only the live
request URL).

## Validation

| command | outcome |
|---|---|
| `.venv/bin/python -m pytest` | **19 passed** (14 from S1/S2 + 4 bodydoc + 1 `ensure_columns`) |
| `python -m mijual.bodydoc --no-fetch scan --from-db` | 364 docs, **23,493/23,493** spans round-trip |
| `python -m mijual.bodydoc --offline --cache-dir scripts/spike/samples scan` | 63 docs, **4,538/4,538** spans, 0 requests |
| `python -m mijual.bodydoc --no-fetch backfill` ×2 | identical output, **0 requests** (idempotent) |
| `python -m mijual.bodydoc --no-fetch warrants` ×2 | identical output, **0 requests** (idempotent) |
| full rebuild from the pre-S3 dump + caches | same final state, **0 requests** |
| `.venv/bin/python -m mijual.smoke --database-url sqlite:///var/smoke-s3.db` | **OK** (S1's fixture chain still green; run against a throwaway SQLite file so the collected Postgres survives) |
| key-leak grep (`src tests docs works scripts var`, cache filenames, cached `_url`) | **0 hits** |
| `python3 scripts/workflow.py validate` | **passed** |

## Deviations from `plan.md`

1. **One additive-DDL helper was added (`db/schema_sync.py`), which N16 did not anticipate.**
   The plan allows "whatever tiny column additions those need (free under N16)" — but N16's
   mechanism is `create_all` / `reset_schema`, and `create_all` never adds a *column*. Resetting
   would have destroyed the corpus the plan explicitly says not to reset (291 live requests
   against an unmeasured quota). `ensure_columns` only ever **adds** declared-but-missing nullable
   default-free columns, is idempotent, and refuses anything else — deliberately not a migration
   tool (no version table, no history, no type changes, no drops). Recorded as **N27**.
2. **`pairing_method` is not suffixed; a separate `hint_status` column records the verdict.** The
   plan suggested `pairing_method += '_hint_confirmed'` "or a cleaner scheme — record it".
   Appending would have overflowed `String(30)` (`earlier_history_ambiguous` is 25 chars) *and*
   overwritten S2's evidence. The scheme is: `pairing_method` stays exactly as S2 wrote it,
   `hint_status ∈ {confirmed, reattached, duplicate, identified, mismatch, absent,
   no_correction_block, no_document, unparsed}` carries the 본문's verdict, `pairing_note` carries
   one audit line, and `FilingVersion.pairing_is_resolved` / `.pairing_is_ambiguous` express the
   pair. `reattached` is **sticky** — a later pass never relabels a move as a plain confirmation.
3. **A `mismatch` on an `unpaired_correction` placeholder is reported as `identified`, not as a
   mismatch.** Those are corrections whose original genuinely predates the collection window; the
   hint cannot pair them but it does establish the event's identity. Conflating the two would have
   hidden a real 46-event worklist reduction inside a "94 mismatches" number.
4. **Re-attachment is limited to events that already exist.** The hint may *move* a version only
   when it names an existing event of the same corp + subtype; a hint naming nothing we hold never
   moves anything (N3 — the hint is filer-entered and sometimes years stale). Splitting a collided
   key by minting an event whose original filing was never seen is left flagged
   (`hint_split_evidence`), not performed: creating events is the collector's decision, not a
   parser's.
5. **The budget bought 364 of the ~640 documents the full worklist wants.** Priority order is the
   plan's own — (a) exposable events, (b) ambiguous/collided, (c) unpaired placeholders — and the
   run reports exactly what each pass reached. 443 기재정정 versions still have no 본문
   (`hint_status='no_document'`), all of them on suppressed events.
6. **`collect/filters.py` was edited** (removing `주주우선공모증자`). The plan scoped S3 to the 본문
   layer, but O-5's answer *is* a change to that provisional list, and leaving it stale would have
   made `evaluate()` and the 본문 check disagree on every future collection run.
7. **The ① confirmation writes flags, not a field.** The plan allowed "a flag or field";
   `Event.review_flags` already existed and needed no column. Its verdict flags
   (`warrant_confirmed` / `warrant_conflict` / `warrant_unverified`) are **re-derived** every run —
   `Event.drop_flags()` clears the previous verdict first — because a stale verdict beside its
   replacement would make the record say two things at once.

## Open items handed forward

- **The one `warrant_conflict` (제이알글로벌리츠 `01415892`) needs an exposure decision — `P2.S5`
  owns it.** 본문 says the 증서 is neither transferable nor listed; `ic_mthn` says 주주배정. The plan's
  rule kept it live and flagged; the honest reading is that no tradeable 증서 exists, so the gate
  layer (or the operator) should decide whether `warrant_conflict` blocks exposure. See **N30**.
- **443 기재정정 versions still have no 본문** (all on suppressed events, `hint_status='no_document'`).
  Fetching them is ~443 requests; nothing exposable depends on them.
- **22 `hint_duplicate` versions** sit under two event keys with the twin already holding the
  `rcept_no` (N21's residue). They are flagged, not merged — a de-duplication pass is a candidate
  `defer-job` if `P2.S8`'s corpus work trips over them.
- **9 `hint_split_evidence` collided keys** are proven to be 2+ events each. Splitting them needs a
  collector-side decision (mint an event whose original was never filed in-window?) — `P2.S5` or a
  wider re-collection.
- **O-1 still open.** 289 more requests in this slice drew no quota error (P1 ~1,002 + S2 291 + S3
  289). Still unmeasured; the ceiling flag remains the mitigation.
- **`var/mijual-preS3.dump`** (gitignored) is the pre-S3 database backup used for the
  reproducibility proof; it can be deleted once `P2.S4` starts.
