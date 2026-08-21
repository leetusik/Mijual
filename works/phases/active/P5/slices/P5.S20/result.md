# Result — P5.S20: Multi-span citations for multi-addend 실적보고서 figures (D4)

**Done.** The 7 figures that carried a value they could not show are citable: each now
carries **one span per addend**, every part re-slices to the stored bytes, and the parts sum
to the value. **0 OpenDART requests, 0 LLM calls, ▷ $0.0000.** No number the product renders
moved — the headline pair, every landing aggregate and the 발행사 기재 불일치 두 readings are
byte-identical before → after.

## What the defect actually was

`perf.py` summed the Ⅶ 청약내역 rows (`used += amount`) but kept only the **first** cell as
evidence (`used_cell = used_cell or line[column]`). Where a filer splits the same 청약 by
경로 — 한국예탁결제원 **and** 직접청약 — the whole number is printed nowhere in the document,
so `Cited.value` was the sum while `raw`/`span` pointed at one term. Measured over the 32
parsed 실적보고서 (the exact "before"):

| 회사 | 접수번호 | figure | value | cited cell |
|---|---|---|---|---|
| 에스에너지 | 20260312000380 | `warrants_exercised` | 12,002,675 | `12,001,809` |
| 루닛 | 20260430001421 | `warrants_exercised` | 7,335,542 | `7,335,532` |
| 루닛 | 20260430001421 | `excess_subscribed` | 942,960 | `942,958` |
| SKC | 20260522000297 | `warrants_exercised` | 11,307,695 | `11,307,456` |
| SKC | 20260522000297 | `excess_subscribed` | 1,889,859 | `1,889,818` |
| 한화솔루션 | 20260730000366 | `warrants_exercised` | 38,430,497 | `38,427,609` |
| 한화솔루션 | 20260730000366 | `excess_subscribed` | 6,148,454 | `6,148,305` |

Every one is a **two-row** sum; the missing term is the 직접청약/실질주주 row (866 · 10 · 2 ·
239 · 41 · 2,888 · 149). S3's interim guard dropped the quote on all of them, which was the
honest reading but left the product's own headline example uncitable.

## The decisions

1. **The citation model gains parts, and the single-cell case is byte-compatible.**
   `perf.Cited` gains `parts: tuple[CitedPart, ...]` (`CitedPart = raw + span`), **empty for
   the ordinary one-cell figure**, and `as_json()` emits a `"parts"` key **only** when it is
   set. So the stored JSON of the other 262 figures is unchanged to the byte, and a reader
   that knows only `raw`/`span` keeps working. Invariant enforced at construction:
   `parts[0]` **is** `raw`/`span`, and one part is not a sum (raises). `Cited.citations`
   normalizes both forms to "every cell backing this figure".
2. **The stored corpus was migrated deliberately, offline.** `facts` is written by
   `estimate collect`, which needs a client to *discover* filings — but re-reading one costs
   nothing, because the evidence contract keeps `payload_bytes` beside every row. New command
   **`python -m mijual.estimate reparse`** (`runner.reparse_performance`) re-runs
   `parse_performance` over the stored bytes and rewrites only the parse-derived columns
   (`facts` · `form` · `parse_status` · `parse_note`) — never the link, the bytes or the hash.
   **Run order after any collect is now `bodydoc backfill` → `gates run` → `estimate reparse`
   → `estimate snapshot`.**
3. **A served figure has three states and no fourth.** `present.Figure` gains
   `parts: tuple[QuotePart, ...]`; a figure with parts carries **no** `quote`/`span` (raises
   if given both), so the one-addend quote that would look like a citation is
   *unconstructable*, not merely discouraged. S3's guard generalizes to the rule the plan
   names: **each part's text parses, and the parts sum to the value** — otherwise no chip at
   all and the value keeps its `rcept_no` (the DART link still resolves).
4. **No other `x = x or cell` beside an accumulator exists in `perf.py`** (checked): the
   `lapse_stated` / `lapse_with_fractions` / `fractional_shares` assignments are first-header-
   wins over one printed cell, not addends — and the corpus agrees, all 262 single-cell
   figures state their own number exactly.

## The payload shape `P5.S13` / `P5.S14` render

```json
"warrants_exercised": {
  "value": 38430497,
  "estimated": false,
  "parts": [
    {"quote": "38,427,609", "span": [285071, 285081]},
    {"quote": "2,888",      "span": [285911, 285916]}
  ],
  "rcept_no": "20260730000366"
}
```

- Exactly one of: `quote`+`span` (one cell) · `parts` (≥2, and they sum to `value`) ·
  neither (uncitable — render **no** chip, `rcept_no` still links to DART).
- Render **every** part verbatim. Never show one addend as the citation, and never join them
  into a single quote string: the sum is printed nowhere in the filing, so a joined quote
  would be a sentence the document does not contain.

## Files changed

| file | change |
|---|---|
| `src/mijual/estimate/perf.py` | `CitedPart`; `Cited.parts` + `citations` + guarded `__post_init__`; `_cited_sum`; the Ⅶ 청약내역 branch collects **all** contributing cells |
| `src/mijual/estimate/runner.py` | `ReparseReport` + `reparse_performance` — the offline corpus re-read |
| `src/mijual/estimate/__main__.py` | `reparse` subcommand; `show` prints every addend and verifies each span |
| `src/mijual/present/values.py` | `QuotePart`; `Figure.parts` (+ the two refusals); `payload()` emits `parts` |
| `src/mijual/present/money.py` | `_cited_count` → `_backing_parts` / `_printed_number`: "in one part, or in parts that sum" |
| `src/mijual/present/__init__.py` | exports `QuotePart`; the contract's first bullet states the citation rule |
| `src/mijual/evalset/sample.py` | a perf row's `quote` column shows every addend (the grader was being shown a mis-transcription) |
| `tests/test_estimate.py` | the parser case, on an inline 3-row grid — no fixture file |
| `tests/test_present.py` | the served case: parts cited, parts that miss the value cited by nothing, `Figure` refuses a half-citation |

## Validation

| command | outcome |
|---|---|
| `.venv/bin/python -m pytest` | **93 passed**, 1.2 s, no network/model/DB (baseline 91 → 93) |
| `.venv/bin/python -m mijual.estimate reparse` | `69 of 69 re-read, 4 with changed facts, 0 errors — 0 request(s), 0 LLM call(s)` |
| `.venv/bin/python -m mijual.estimate snapshot` | `545 ① precomputed (54 priced) · 32 lapse rows (29 valued)` |
| re-run of both (idempotence) | `0 with changed facts` on the second pass — converged |
| `.venv/bin/python -m mijual.estimate report` | **diff vs. the pre-run capture: identical**, line for line |
| `curl /board/summary` | 488 (50/422/16) · 33 · 57 · 4 · 15 · 69 · **718.1억 / 548.7억** · 51,253,956 / 365,527,824 · 0.1402 · 퓨쳐켐 2026-09-04 — all unchanged |
| `curl /events/20260720000067` (한화솔루션 ①) | `lapse_result.warrants_exercised` = 38,430,497 with **2 parts** |
| `curl "/stocks?q=에스에너지"` | 놓친 돈 1,990,157주 · 14.22% · **7.2억원** ✓, exercised 12,002,675 with 2 parts |
| `curl "/stocks?q=대한광통신"` | `issuer_disagreement` intact — both readings, both quotes, `used` on 발행−청약 |
| `python3 scripts/workflow.py validate` | passed |

**Corpus measurements (2026-08-22, local Postgres).**

- Stored 실적보고서 figures: **269** over 32 parsed reports. **Uncitable: 7 → 0.**
  Multi-part: 0 → **7**, every part re-slicing to its span (`doc.verify` on all 14 spans).
- Served 소멸 counts (`present.lapse_result` over all 31 lapse rows): 58 single quote +
  **4 parts** + **0 bare** (was 58 + 0 + 4).
- Stored diff: **4 of 69 reports changed, and only by gaining a `parts` key on 7 figures** —
  every other key, `parse_note`, `form`, `event_id`, `content_sha1` and the whole `lapse`
  column byte-identical.
- 발행사 기재 불일치 filings: **5** (인베니아 · 라온피플 · 대한광통신 · 피엠티 · LB세미콘),
  unchanged; none of them is one of the four multi-addend filers, and all their readings are
  single-cell quotes.

## Deviations from `plan.md`

- **The plan's step 4 assumed a re-parse already existed** ("find it"). It did not — `facts`
  is only ever written by `collect_performance`, which takes a `DartClient`. Rather than run a
  collect (requests, and it would re-link), I added the offline `estimate reparse` pass; it is
  the same parser over the same stored bytes, with 0 requests. Recorded in `phase.md` as the
  new step in the re-derivation order.
- **One file outside the plan's map: `evalset/sample.py`** (7 lines). Its 실적보고서 rows
  showed the grader the first addend beside the summed value — the same false-citation shape
  D4 exists to remove, in the one other reader of `facts` citations. The change is
  sampling-neutral (the draw keys on `unit`/`stratum`/`hard_case`, never on `quote`), and
  `tests/test_evalset.py`'s determinism test is green.
- Nothing else. The interim guard was generalized, not relaxed: a figure whose text does not
  state its number — in one part or in parts that sum — still carries no chip.
