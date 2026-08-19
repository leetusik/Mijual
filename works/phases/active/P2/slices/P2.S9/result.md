# P2.S9 — result

_This slice has an operator co-work gate in the middle. **Phase A is complete and this
result stops at the gate**; Phase B (import the operator's labels, compute and write the
accuracy report) extends this file in a later dispatch._

## Phase A — the evalset is prepared and waiting on the operator

### Status: `needs_operator`

| what | where |
|---|---|
| **labelling sheet** (the operator edits this) | `/Users/sugang/projects/personal/Mijual/evalset/sheet.csv` |
| **instructions** | `/Users/sugang/projects/personal/Mijual/evalset/LABELING.md` |
| frozen sample (regenerable, deterministic) | `/Users/sugang/projects/personal/Mijual/evalset/sample.json` |
| **rows to label** | **344** rows over **99** filings (one row per `(rcept_no, field)`) |
| **▷ operator time** | **75–95 minutes** |

The operator opens `evalset/sheet.csv`, types one of `correct` / `wrong` / `partial` /
`skip` in column **A**, optionally a corrected value in column **B**, saves as CSV, and
runs `.venv/bin/python -m mijual.evalset import`. Nothing else is required of them.

### What was built

`src/mijual/evalset/` — five modules, no database in the read-back path:

| module | job |
|---|---|
| `sample.py` | reads the corpus, draws the stratified sample, freezes it to `sample.json` |
| `sheet.py` | writes the operator's CSV; refuses to overwrite labelled work |
| `labels.py` | validates a labelled sheet → `labels.json`; refuses anything it cannot parse |
| `report.py` | per-field precision + gate-block rate + over-blocking, with 95 % Wilson CIs |
| `__main__.py` | `sample` / `sheet` / `status` / `import` / `report` |

Only `sample` touches Postgres. `import` and `report` read `sample.json` + the sheet, so
the accuracy numbers stay regenerable after the corpus moves under them — which N55/N83
make a real risk, not a hypothetical.

### The sample

Deterministic: seed **20260907**, a seeded shuffle over a **sorted** pool, per-stratum
seeds (`f"{seed}:{stratum}"`) so re-tuning one quota cannot reshuffle another. Two full
runs produced byte-identical `sample.json` (ignoring `generated_at`).

| stratum | filings (forced / random / booster) | rows |
|---|---|---|
| `R1_prose` ① 유상증자 | 39 (11 / 22 / 6) | 180 |
| `R2_prose` ② CB | 26 (4 / 17 / 5) | 75 |
| `R3_prose` ③ 매수청구 | 16 (1 / 14 / 1) | 20 |
| `perf` 증권발행실적보고서 | 18 (6 / 12 / 0) | 69 |
| **total** | **99** | **344** |

Per field, sampled / corpus (deduped): ① five fields 33 / 75 each; ② `refixing_terms`,
`option_schedule`, `lockup_release` 21 / 62 each; ③ `dissent_notice_procedure` 15 / 25;
`correction_interpretation` 32 / 47; the four 실적보고서 figures 17–18 / 30–31.

**Three picks, and the difference is load-bearing arithmetic.** `random` is the seeded
stratified draw and the **only** pick a precision rate is computed from. `forced` is every
known hard case, included whole — 43 rows: `withdrawn_철회` 21, `span_unresolved` 5,
`gate_failed:*` 7, `tbd_추후결정` 4, `lapse_mismatch` 5, `reit_form` 1 — deliberately
over-sampled and therefore reported case by case instead of averaged in. `booster` adds 12
filings that contribute **only** their `correction_interpretation` row, because field 10 is
the corpus's thinnest field (N82) and boosting it any other way would have quietly
de-randomised every other field on those filings.

Hard cases the plan named are all in: LB세미콘 `20260730000278` (span-unresolved 할인율,
with 진양폴리우레탄 `20260312000261` and 캠시스 `20260406001595` — N76's ▷ 49.2억원), 추후결정
×2 (경남제약 `20260623000409`, 에이전트AI `20260619000455`), 철회 (썸에이지 `20260805000454`,
제이알글로벌리츠 `20260205000605` — also the `warrant_conflict` case — 디모아 `20260625000227`
and the ② withdrawals), N62's three 정정-on-the-wrong-사채 filings, and N68's five
실적보고서 whose own 실권주 cell disagrees with their Ⅶ tables.

### The sheet

`label` and `corrected_value` are columns **A and B** so the pass is typing down two
columns; the evidence sits to the right. Written **UTF-8 with BOM** (Excel on macOS reads
Korean as mojibake without one). Every row carries `extracted_value` (normalized, up to 900
chars — not the 400-char display clip), the model's verbatim `quote`, ±120 characters of
surrounding document text with the citation marked `【…】`, the gate verdict + its Korean
reason, and a `dart_url`. Only `row_id`, `label` and `corrected_value` are read back, so a
spreadsheet mangling `20260805000454` into `2.02608E+13` costs nothing.

Three touches added beyond the plan, all to protect the operator's time — the sheet ships
with **0 empty `extracted_value`, `context` or `row_id` cells**:

* the 31 rows with **no citation span** (an unresolved quote, or a field the model called
  absent) would have shown an empty context cell. They now show the field's own anchor
  region marked `(인용 스팬 없음 · 항목 추정 위치)`, or — for 6 rows — the statement that the
  anchor does not occur anywhere in the 본문, which is itself the evidence that an `absent`
  verdict was right (N28).
* a value cell is never blank: a field the model called absent reads
  `(이 문서에 없다고 판단)`, and N40's two `추후결정` rows — a real extraction whose
  sub-fields are all `null` — read `(추출은 됐으나 하위 항목이 모두 null — 값 없음)`. Both are
  judgements the operator must judge, and a blank cell would have hidden them behind what
  looks like a bug.
* `sample` and `sheet` **refuse to run** if the sheet on disk already holds labels, and the
  refusal happens before `sample.json` is written, so the two files can never diverge.

### Validation

| command | outcome |
|---|---|
| `.venv/bin/python -m pytest` | **56 passed** in 0.77 s (5 new in `tests/test_evalset.py`) |
| `.venv/bin/python -m mijual.evalset sample --force` ×2 | identical `sample.json` (byte-compare ignoring `generated_at`) — **PASS** |
| `.venv/bin/python -m mijual.evalset status` | `0 / 344 row(s)` — sheet ships unlabelled |
| `python -m mijual.evalset --labels <tmp> import <bad 3-row csv>` | **REFUSED**, exit 1, names both problems (`unknown label 'maybe'`, `ZZZZ is not in the sample`), imports nothing — **PASS** |
| `python -m mijual.evalset --labels <tmp> import <good 3-row csv>` | 3 labels (`O` → correct, `partial`, `맞음` → correct) — **PASS** |
| `python -m mijual.evalset --labels <tmp> report` | strict 50.0 % (1/2), lenient 100 %, Wilson [9–91 %], over-block 100 % (1/1), corpus block-rate 4.0 % (3/75) — hand-checked — **PASS** |
| clobber guard (`sample` against a sheet holding 1 label) | REFUSED, exit 1, `sample.json` byte-identical afterwards — **PASS** |
| secret scan (both `.env` values × 10 new/generated files) | **0 hits** |
| `python3 scripts/workflow.py validate` | `Workflow validation passed.` |

Spend: **0 OpenDART requests, 0 LLM calls.** No filing was fetched; the corpus was not
modified (the sampler only reads). The scratch label/report files used for the smoke test
live outside the repo; `evalset/labels.json` does not exist yet and is the operator's
import to create.

### Deviations from `plan.md`

1. **The sample is persisted as JSON, not as a table.** The plan allowed either. JSON was
   chosen so `import` and `report` need no database at all — the labels are the one
   artifact in this repo that cannot be regenerated, and tying their scoring to a live
   Postgres would have made the accuracy report perishable.
2. **A fourth label, `skip`.** The plan named `correct` / `wrong` / `partial`. An operator
   with no fourth option guesses, and a guess enters the measurement as a judgement.
   `skip` leaves the denominator and is counted separately in the report. The import still
   refuses everything outside the four.
3. **▷ 75–95 minutes, above the plan's 60–90 target.** Holding the "~100 filings" the
   handoff's §3.6 artifact asks for costs the extra. Two levers exist and neither needs
   code: the sheet is ordered ① → ② → ③ → 실적 with one filing's rows contiguous, so
   stopping at a block boundary still yields a complete measurement for everything above it
   (finishing ① alone is ▷ ~36 minutes); and re-drawing smaller is one command
   (`sample --R1-prose 14 --R2-prose 10 --R3-prose 8 --perf 6 --booster 6 --force`, seconds,
   0 requests). Flagged rather than silently trimmed.
4. **A `qa` Doc-impact line was recorded now** for the measurement harness itself; the
   plan's `data`/`qa` line for the **measured accuracy numbers** stays with Phase B as
   written.

### What Phase B does (not this dispatch)

Import the operator's labels, run `report`, paste the per-field table + both error
directions + the gate-block rates + the 정정 recall proxy into this file, and add the
`data`/`qa` Doc-impact line for the first measured extraction accuracy. Nothing is labelled
or guessed here.
