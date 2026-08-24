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

---

## Phase B — the accuracy report (2026-08-20)

### Status: `done`. Read the provenance before any number below.

**Who judged.** Every one of the 344 labels was judged by **this slice's executor — Claude
(Opus 5), running as `slice-executor-high`** — under the operator's amendment of 2026-08-20
(verbatim: _"you self evaluate and self validate. since the extraction done by gemini and
you are a claude fable. try by yourself."_). This is a **cross-model** judgement: the ten §7
prose fields were extracted by **Gemini**, and the judge is a different model family, so no
model graded its own output. The 69 실적보고서 rows were never read by any model — they are
deterministic table reads, and judging them is a parser audit, not a model grade.

**What these labels are not.** They are **not human ground truth, and no human has verified
them.** Nothing here is hand-labelled. The honest reading of every rate below is *"a second
model, reading the same stored filings, agrees with the extraction at rate X"* — inter-model
agreement, which is weaker evidence than human adjudication and can share a blind spot with
the extractor wherever a Korean disclosure convention is systematically misread by both.
The human spot-check path is unchanged and costs nothing: overwrite column **A** of
`evalset/sheet.csv` for any rows a human wants to re-judge and re-run `import` + `report`;
the sample is frozen, so the numbers move only where a label moves.

**What each judgement compared.** The normalized `extracted_value`, against the model's
verbatim `quote`, against the document. Where ±120 characters could not settle it, the
**full stored 본문 was read out of Postgres** (snapshot ZIP → `BodyDocument`) — 0 network
calls. Judgement rule per `LABELING.md`: misled → `wrong`; correct but under-informed →
`partial`. `skip` was available and **not used once** — every row was decidable from the
stored document.

**Spend: 0 Gemini/LLM calls, 0 OpenDART requests.** All evidence came from the local
Postgres snapshots (host 5433) already collected by S1–S8.

### How the judging was made checkable rather than impressionistic

Judging 275 prose readings by eye would have produced agreement, not measurement. Wherever a
field carried a checkable scalar, the value was re-derived from the stored document by a
throw-away read-only script and compared, so the label rests on an arithmetic or string
match rather than on a reading:

| field | independent check run against the stored 본문 |
|---|---|
| #5 발행가액 산정방법 | 할인율 % and 확정예정일 re-found in the 본문 by regex (incl. the dotted `2026.01.19` form) |
| #6 리픽싱 | 최저 조정가액 cell, floor ratio (`70%`/`100분의 70`/`85%`), 조정주기 (`매 N개월`) re-read from the table |
| #7 옵션 | put/call 청구기간·조기상환기일 tables re-read row by row; ratio (`30%` 한도 등) matched to its clause |
| #8 보호예수 | release_date recomputed as **본문 납입일 + 12개월** and compared to the stated value |
| #9 반대의사 | 합병일정 표's 통지 접수기간 / 매수청구 행사기간 re-read and compared |
| #10 정정 해석 | model `changes` compared item-by-item against S4's stored deterministic 정정사항 표 |
| 실적 ×4 | every value matched to the table cell its header names; 발행 − 청약 = 실권주 arithmetic checked per filing |

Two rows would have been mislabelled without these checks: `E0179` 형지엘리트's 확정예정일 looked
ungrounded until the dotted `2026.01.19` form was searched for (the value was right), and the
`no_correction_rows` blocks only resolved as parser gaps — not model inventions — after a
full-text search of the filings.

### Headline

| measure | value |
|---|---|
| rows judged | **344 / 344** (0 skip) — 339 `correct`, **5 `partial`**, **0 `wrong`** |
| **precision of what the product would show** (random picks only) | **98.6 %** strict (213/216), 95 % Wilson **[96–100 %]**; **100.0 %** with `partial` counted |
| same, all picks pooled (incl. forced hard cases) | 291 `correct` + 5 `partial` of 296 shown rows |
| **over-blocking** — gate-blocked rows judged to have been right | **100 % (19/19)** on random picks; **100 % (48/48)** across every pick |
| 정정 해석 recall proxy (label-free, corpus) | **85.3 %** as stored → **88.7 %** re-matched (see below) |
| `wrong` readings found | **0** — in 275 model rows and 69 deterministic rows |

**Zero `wrong` deserves suspicion, and here is the honest framing.** Four things inflate it,
and none of them is fraud: (a) the corpus was extracted by the *post-S7/S8* pipeline, i.e.
after two slices of prompt and gate repair — this measures the fixed pipeline, not the
original one; (b) **26 of the 275 model rows (9.5 %) are `absent`/null readings** (15 of them
the five ① fields on three 철회 filings, 9 `refixing_terms` where the 최저 조정가액 cell is
literally `-`, 2 `option_schedule` reading `해당사항 없음`), and "correctly reporting nothing
is there" is the easiest row on the
sheet; (c) the gate had already removed 48 rows from the shown set — which is exactly why
direction (b), over-blocking, is measured too; (d) the judge shares the extractor's
information source, so a shared misreading of a Korean disclosure convention would be
invisible to it. The number that survives all four caveats is the narrow one: **on 216
randomly-picked rows the product would have shown, a second model found no statement that
would mislead a user, and 3 whose citation under-supports the value.**

### Per field (generated — `.venv/bin/python -m mijual.evalset report`)

| 필드 | 노출 n | 정밀도 (strict) | 95% CI | partial 포함 | 차단 n | 과차단 | 코퍼스 게이트 차단율 |
|---|---|---|---|---|---|---|---|
| #1 신주인수권증서 상장·매매기간 | 22 | 100.0% | [85–100%] | 100.0% | 0 | — | 4.0% (3/75) |
| #2 청약 취급처 (대상자별 증권사 + 청약일) | 22 | 100.0% | [85–100%] | 100.0% | 0 | — | 4.0% (3/75) |
| #3 실권주 처리 방식 | 22 | 100.0% | [85–100%] | 100.0% | 0 | — | 6.7% (5/75) |
| #4 초과청약 조건 (비율) | 22 | 100.0% | [85–100%] | 100.0% | 0 | — | 4.0% (3/75) |
| #5 발행가액 산정방법 (1·2차·확정 산식) | 22 | 100.0% | [85–100%] | 100.0% | 0 | — | 8.0% (6/75) |
| #6 리픽싱 세부 조건 | 9 | 100.0% | [70–100%] | 100.0% | 8 | 100.0% | 32.3% (20/62) |
| #7 콜·풋 세부 스케줄 | 15 | 100.0% | [80–100%] | 100.0% | 2 | 100.0% | 14.5% (9/62) |
| #8 보호예수 / 전매제한 해제일 | 13 | 100.0% | [77–100%] | 100.0% | 4 | 100.0% | 22.6% (14/62) |
| #9 반대의사 통지 방법·절차 | 10 | 100.0% | [72–100%] | 100.0% | 4 | 100.0% | 44.0% (11/25) |
| #10 정정 해석 | 11 | 100.0% | [74–100%] | 100.0% | 1 | 100.0% | 6.4% (3/47) |
| [실적] 신주인수권증서 발행 계 | 12 | 100.0% | [76–100%] | 100.0% | 0 | — | 0.0% (0/31) |
| [실적] 신주인수권증서 청약 | 12 | **83.3%** | [55–95%] | 100.0% | 0 | — | 0.0% (0/31) |
| [실적] 초과청약 | 12 | **91.7%** | [65–99%] | 100.0% | 0 | — | 0.0% (0/31) |
| [실적] 신주인수권증서 청약 실권주 | 12 | 100.0% | [76–100%] | 100.0% | 0 | — | 0.0% (0/30) |

**Every CI is wide and that is the truthful shape of n ≈ 10–22.** `100.0% [72–100%]` means
"no error seen in 10 rows", not "the field is solved". The two sub-100 % cells are the entire
strict-error set, and both are the same defect, described next.

### Error direction (a) — what the product would show: 3 rows, one defect, zero false facts

All three strict misses are **실적보고서 figures whose value is an aggregate but whose citation
points at one addend**. No stated fact is wrong; the citation simply does not carry the
number printed beside it.

| row | filing | field | value | quote | why `partial` |
|---|---|---|---|---|---|
| `P0286` | SKC `20260522000297` | 신주인수권증서 청약 | `11,307,695` | `11,307,456` | value = 예탁결제원 청약 11,307,456 **+ 직접청약 239**; the sum is right (발행 11,598,997 − 11,307,695 = 실권주 291,302, the filing's own number), the quote covers one row of two |
| `P0287` | SKC `20260522000297` | 초과청약 | `1,889,859` | `1,889,818` | same shape: 예탁결제원 초과청약 + 직접청약 초과청약 41 |
| `P0314` | 에스에너지 `20260312000380` | 신주인수권증서 청약 | `12,002,675` | `12,001,809` | 한국예탁결제원 12,001,809 **+ 실질주주 직접청약 866** |

**The aggregation is the correct behaviour; the citation contract is what breaks.** A filing
that splits 청약 into 예탁결제원 and 직접청약 rows must be summed, or the product would
under-report 청약 and over-report 실권주. What §3.6 promises, though, is that a user can tap
the number and land on the text that says it — and here they land on a *different* number.
This is a **multi-span citation gap**: the layer needs to cite every summed cell, or to label
the value as a sum of N cited rows. Fix-slice material, not a re-extraction: **2 of the 18
sampled 실적 filings (11 %)** carry the split-row form (SKC, 에스에너지), so ▷ ~3 of the corpus's
31 would be affected. Two other partials (below) are completeness, not
citation, so the whole strict-error surface of this evalset is **one defect class**.

The other two `partial`s are on `correction_interpretation`, which is not scored by the
random-pick rate (both are forced/booster picks):

* **`E0207` 알파AI `20250930000580`** — 7 정정 rows, 4 itemised. 만기일 / 전환조건 / 납입일 /
  이사회결의일 are exact and the 요약 and 일정영향 are accurate, but **6. 이자지급방법** (the whole
  coupon-date schedule was re-cut) is a distinct fact that cannot be derived from the four
  listed changes. Under-informed, not misled.
* **`E0266` 아시아나항공 `20260713000482`** — both listed changes are the **footnote references
  themselves** (`(주1) 정정 전` → `(주1) 정정 후`), i.e. the change list carries no content. The
  `summary` is accurate (회사구조개편 계획 + ESG위원회 공정성 강화조치 — verified against the
  footnote bodies, which describe the LCC 3사 통합 검토 and the ESG 특별위원회). The model
  resolved footnotes correctly in four other filings (`E0202`, `E0214`, `E0222`, `E0226`), so
  this is an inconsistency, not an inability.

### Error direction (b) — over-blocking: the gate threw away 48 correct readings and 0 wrong ones

**Every gate-blocked row in the sample was a correct reading** — 19/19 on random picks,
48/48 pooled. In this sample the gate's blocking has bought **no** precision: it removed no
error, and it removed 48 true statements. Blocked-row causes, judged case by case:

| cause | rows | what the judging found |
|---|---|---|
| API-vs-본문 정정 lag (`release_date_not_derived`, `option_date_out_of_term`, `dissent_period_mismatch`) | 5 | the model read the **corrected 본문** and the gate compared it against a **stale API row**: `E0212`/`E0213` (엑시큐어 납입일 2026-12-30 vs API `[2025-09-18, 2028-09-18]`), `E0206` (알파AI 납입일 2025-12-19 vs API 2025-09-22), `E0225` (제이에스링크 2025-01-15 vs API-derived 2026-10-02), `E0261` (모다이노칩 통지 09-17~10-16 vs API 03-09~03-23). **The gate's reference data was wrong, not the reading.** |
| `span_unresolved` | 5 | `E0021` LB세미콘, `E0115` 진양폴리우레탄, `E0125` 캠시스, `E0209` 에이럭스, `E0211` 엑시큐어 — correct readings whose quote concatenates two non-contiguous lines of the document; the N76 "▷ 49.2억" pattern exactly |
| `lockup_not_quantified` | 4 | `E0186`/`E0192`/`E0233`/`E0240` all state 12개월 correctly; the gate withholds them for lacking a derived 해제일 |
| `field_absent` | 26 | genuinely absent — 철회 filings with no 청약/실권주/발행가 sections, and 리픽싱-free CBs whose 최저 조정가액 cell is `-` |
| `method_not_enumerated` | 2 | 이렘 `E0086`/`E0091`: full-text search confirms the filings contain **no** 일반공모/인수/미발행 clause, so `method: 기타` was faithful |
| `no_correction_rows` | 2 | `E0237` 풍전약품, `E0252` 현대바이오: the model read real changes (이자율 2.0 %→4.0 %; R&D 자금 세부내역 추가) out of tables the deterministic 정정표 parser cannot reach (footnote refs, embedded tables) |
| `superseded_api_reference` | 4 | N46 version-scoping — a correct reading of a superseded 본문, correctly withheld |

**Read this as a price list, not as "the gate is broken".** `field_absent` and
`superseded_api_reference` (30 of 48) are blocks the product *wants*: the field is not there,
or the version is not current. The other 18 are the actionable ones, and they cluster into
three fixable causes — stale API reference data, single-span citation for multi-line quotes,
and withholding a quantified 개월 because a 해제일 could not be derived.

### Forced hard cases, case by case (43 tagged rows — never averaged into a rate)

| hard case | rows | verdict |
|---|---|---|
| `withdrawn_철회` (디모아, 썸에이지 ×2, 제이알글로벌리츠) | 21 | **all `correct`** — every field correctly read as absent, and 썸에이지's #10 correctly reads 유상증자 결정 → **철회** with "모든 일정 취소" |
| `span_unresolved` (LB세미콘, 진양폴리우레탄, 캠시스, 에이럭스, 엑시큐어) | 5 | **all `correct`** — the readings survive; only the citation span failed |
| `gate_failed:*` (모다이노칩 #9, 이렘 #3 ×2, 엑시큐어 #7·#8, 알파AI #8, 제이에스링크 #8) | 7 | **all `correct`** — see the over-block table |
| `tbd_추후결정` (경남제약, 에이전트AI — #1·#2) | 4 | **all `correct`** — a real extraction whose sub-fields are all `null` because the filing says 추후결정 |
| `lapse_mismatch` (LB세미콘, 대한광통신, 라온피플, 인베니아, 피엠티) | 5 | **all `correct`** — see below; the inconsistency is the **issuer's**, and the parser reads the header-named cell and records the mismatch |
| `reit_form` (KB스타리츠) | 1 | **`correct`** — the 리츠 서식's `6. 실권주 처리내역` is read as accurately as the standard `Ⅷ` form (2,167,828 + 단수주 6,983 = 총계 2,174,811) |

**N68's five `lapse_mismatch` filings resolved.** The stated 실권주 differs from `발행 − 청약`
because the **issuers' own tables are internally inconsistent**, and the disagreement is
visible inside a single row. LB세미콘 `20260811000597` is the clearest: under the headers
`신주인수권증서 청약 실권주 | 구주주 배정단수주 | 실권주 및 단수주 총계` the filing prints
`2,109,436 | 1,776,014 | 333,422` — a "총계" smaller than its own first column, because the
issuer filled the row with `[실권주+단수주 총계, 초과청약 배정분, 일반공모 잔여분]`. 인베니아 and
피엠티 have the same shape (`563,178 | 2,821 | 560,357`, `416,831 | 416,276 | 555`); 대한광통신
and 라온피플 are internally consistent and simply define 실권주 to include the 단수주. In all
five the extraction reads the cell its header names and flags the arithmetic gap in
`facts.notes` — which is the right behaviour, and means **`lapse_mismatch` should be surfaced
to the user as "발행사 기재 불일치", never silently reconciled.**

### 정정 해석 recall proxy — and a matcher bug found while judging it

| measure | value |
|---|---|
| as stored by S4 (`deterministic_check`) | 177 deterministic 정정 rows, **26 uncovered → 85.3 %**, 0 unsupported of 157 changes, 45 records (3 unparsed records excluded) |
| **re-matched read-only with a corrected matcher** | **20 uncovered → 88.7 %**, same 177/157/45, still 0 unsupported |
| content-level, from this judging pass (32 sampled rows, 105 items, 19 uncovered) | **1** of the 19 is an omission that costs a reader information (`E0207`'s 이자지급방법); the other 18 are duplicate restatements of an already-listed change or bare `(주N)` footnote references → **≈ 99 % of investor-meaningful items covered**. Coverage is not the whole quality story: `E0266`'s two items are *covered* yet its change entries are contentless footnote refs, which no recall number can see |

**The bug** (`src/mijual/extract/runner.py:464-475`, `check_against_items`). The
value-fallback arm `new_key in _norm(item.get("after"))` is evaluated **per item, inside the
same loop as the item-name match**, so it fires on an early item before a later item's *name*
would have matched, and nothing stops several changes from binding to the same item. When a
filing corrects many rows **to the identical string** — 에이전트AI `20260619000455` moves five
schedule rows to `-(추후 확정)` — all five changes bind to item 0 and four covered rows are
counted `uncovered`. Three records are affected (`20260619000455` 5→1, `20250925000611` 1→0,
`20251204000439` 1→0), and the effect is always to **understate** recall.

**It was not fixed here, on purpose.** `deterministic_check` is stored evidence written by S4
across the corpus; rewriting the matcher without re-running S4 would leave the database and
the code disagreeing, and re-running S4 is not this slice's job (and the plan forbids
touching the machinery beyond true bugs with tests). Recommended as a **fix slice**: correct
the matcher (one-to-one claim, name-match pass before value-fallback pass), re-run the
deterministic check over the stored corpus, and re-freeze the number. Until then the honest
statement is **"≥ 88.7 %, and ≈ 99 % of investor-meaningful items"** — the stored 85.3 % is a
floor.

### Three findings that are not accuracy numbers

1. **#7's `start_date`/`end_date` carry two different conventions.** In some filings they are
   the 조기상환**기일** range (`E0188`: 2028-04-24 ~ 2030-07-24), in others the 청구**기간**
   range (`E0182`: 2027-02-01 ~ 2028-06-02 for the same kind of put). Both are
   document-grounded and each filing is internally consistent, so no row is `wrong` — but a
   UI that puts them on one timeline will silently compare a claim window against an exercise
   date. This wants a per-option `date_basis` marker, not a prompt change.
2. **A corpus metadata anomaly, not an extraction defect.** `rcept_no 20250930000508` is
   stored under DART `corp_name` **풍전약품** (corp_code `01110474`, stock_code `298060`) while
   its own 본문 header reads **에스씨엠생명과학** — a DART master/rename artifact. Every extracted
   value for that filing is correct against its body; only the display name would be wrong.
3. **`labels.json` carries no provenance field.** The machinery stores `source` (the sheet
   path) and the labels, with nowhere to record *who judged*. For this round provenance lives
   in `LABELING.md`, this file and `phase.md`. A one-line `judged_by` on the labels payload is
   fix-slice material — it matters precisely because these labels are not human ones.

### Validation (Phase B)

| command | outcome |
|---|---|
| `.venv/bin/python -m mijual.evalset import` | **344 label(s), 344 judged, 0 skip, 0 corrected value(s)** → `evalset/labels.json` — **PASS** |
| `.venv/bin/python -m mijual.evalset status` | `344 / 344 row(s) (100%)` — **PASS** |
| `.venv/bin/python -m mijual.evalset report` | renders; headline **98.6 % strict (213/216), [96–100 %], lenient 100 %, over-block 100 % (19/19)** — **PASS** |
| `.venv/bin/python -m pytest` | **56 passed** — **PASS** (after the one-word wording fix in `report.py`) |
| read-only re-match of `deterministic_check` over the 45 stored records | 85.3 % → **88.7 %**, 0 unsupported both ways — **PASS** (nothing written) |
| sheet integrity after labelling | 345 lines, UTF-8 **BOM preserved**, CRLF preserved, 344 rows re-parsed, every evidence column byte-unchanged — a cell-by-cell compare against `HEAD:evalset/sheet.csv` shows **`label` as the only column that changed** (column B stayed empty) — **PASS** |
| secret scan (both `.env` values × the 6 touched files) | **0 hits** |
| `python3 scripts/workflow.py validate` | `Workflow validation passed.` |

Spend for Phase B: **0 Gemini/LLM calls, 0 OpenDART requests** (budget allowed ≤ 20 —
none were needed; every filing had a stored snapshot). No secret value was echoed. The
pre-label sheet was copied to scratch before writing, so the unlabelled artifact still
exists.

### Deviations from `plan.md` (Phase B)

1. **One machinery line changed, and it is a provenance bug the amendment created.**
   `report.py` rendered `게이트가 차단한 행 중 **사람이** '맞다'고 본 비율` — with
   Claude-judged labels that sentence is false in the generated report itself, which is
   exactly the "no 'hand-labeled' phrasing anywhere" the amendment forbids. Changed to
   `판정자가` (judge-neutral, true for either labeller). No other machinery, no sample, and no
   stored extraction was touched; `pytest` is green and no test asserted the old wording.
2. **`LABELING.md` gained a provenance footer** naming this round's labels as Claude-judged
   and stating how a human overrides them. The instructions themselves are unchanged — the
   footer exists so the provenance travels with the artifact, not only with this file.
3. **The 정정 recall matcher bug was reported, not fixed** (reasoning above). This is the one
   place where "fix true bugs" was deliberately declined, because the fix's cost is a corpus
   re-run that belongs to a fix slice.
4. **`corrected_value` (column B) is empty for all 5 `partial` rows.** In every case the
   *value* is right and the *citation* or the *completeness* is what falls short, so there is
   no corrected value to state; writing one would have implied a factual error that is not
   there.
