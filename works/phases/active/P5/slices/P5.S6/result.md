# Result — P5.S6: ③ 매수예정가 backing (D-15)

**Status: done.** ③ 매수예정가격 is in the exposure contract and served on
`/events/{rcept_no}`: **12 of the 16 exposable ③ events** now carry it as a gated
fact with a verbatim citation, and the other 4 carry no key at all (their filings
state no price). **Zero LLM calls and zero OpenDART requests were spent** — which
is the slice's one real deviation from `plan.md`, and the reason is below.

## The deviation, and the measurement that forced it

`plan.md` step 1/3 specified a `FieldSpec` in `src/mijual/extract/fields.py` plus a
bounded Gemini re-extraction. Reading the ③ 본문s first (the step the plan asked
for) showed the value is **not** LLM-tier at all:

| what was measured | over what | result |
|---|---|---|
| 매수예정가격 is a **본문 form cell** — `13. 주식매수청구권에 관한 사항` → qualifier `매수예정가격`, parsed by `bodydoc.extract_labels` with a real span | all 95 stored ③ 본문 | **95/95** carry exactly one such row (70 a number, 25 `-`) |
| a second row (per-주식종류 보통주/우선주, the shape the plan asked the schema to handle) | same 95 | **0 documents** have one — the form has a single cell |
| the ③ detail API row carries the same number in **`aprskh_plnprc`** | 17 comparable current versions | agrees **17/17, 0 mismatches** |

Two deterministic witnesses. `fields.py`'s own registry rule ("a field that turns
out to be label-readable belongs in `bodydoc`, not here"), the phase constraint
("anything deterministically readable must not be paid for with an LLM call") and
`tests/test_extract.py`'s disjointness assertion all point the same way, so the
field was built as a **`본문-label` tier field** instead: read for free, stored in
the same `Extraction` row shape, gated against the API value.

Everything the plan actually asked for still landed — the value is a first-class
gated field in the contract and served by the API — at **$0.0000** instead of ~16
calls. Nothing else in `plan.md` was skipped.

## What changed

| file | what |
|---|---|
| `src/mijual/extract/labelfields.py` **(new)** | the label tier: `LabelFieldSpec` + `LABEL_SPECS` (one entry, `appraisal_price`), `read_document` (pure), `read_label_fields` (the corpus pass), `LabelFieldReport` |
| `src/mijual/bodydoc/labels.py` | `LABEL_FIELDS` gains `주식매수청구권에관한사항 → appraisal_rights` (one label, eight qualified sub-rows — the `11. 청약예정일` pattern) |
| `src/mijual/gates/rules.py` | `gate_appraisal_price` (citation → positive 원 → value-vs-quote → **value vs API `aprskh_plnprc`**) + registry entry + the docstring note that one gate is not a §7 row |
| `src/mijual/gates/outcome.py` | three reason codes with their Korean operator sentences (`appraisal_price_mismatch`, `_quote_mismatch`, `_out_of_range`) |
| `src/mijual/extract/runner.py` | a label row's citation relocates against the **whole** document (never a prompt-sized window — the cell sits at char 65k of a 120k 합병 본문); the 정정 diff now covers the rights type's label fields too |
| `src/mijual/extract/__main__.py`, `__init__.py` | `python -m mijual.extract labels [--rights R3] [--current-only]` (0 calls); `fields` also prints the label tier |
| `src/mijual/scheduler/pipeline.py` | the free pass runs **first in the `extract` stage and outside `extract_max_calls`**, so a newly collected ③ cannot render its 반대의사 기간 while its 매수예정가격 waits for a hand-run command |
| `src/mijual/present/event.py` | `FIELD_NAMES_KO["appraisal_price"] = "매수예정가격"` — the form's own label, not coined |
| `tests/test_extract.py`, `test_gates.py`, `test_present.py` | one reader test, one gate test, the registry pin widened to both registries |

Design decisions worth carrying forward are in `phase.md` (*`P5.S6` — the ③
매수예정가격 …*); the short version: the citation is composed from the document's own
two adjacent cells (`매수예정가격 5,649`) and **accepted only if it lands on the cell
the label parser already found** (70/70 do), an empty cell is `absent` rather than
`0` or a null, and no Korean product string was invented.

## Validation

| command | outcome |
|---|---|
| `.venv/bin/python -m pytest` | **91 passed**, 1.25 s (89 baseline + 2 new), no network / model / DB |
| `.venv/bin/python -m mijual.extract labels --rights R3` | 18 event(s), 61 document(s), **61 rows**, **0 calls**, 1.4 s — 47 extracted / 14 absent; **47/47 spans resolved *and* verified**, 0 unresolved, 0 fall-backs to the label span |
| `.venv/bin/python -m mijual.gates run` | 1,359 events, 710 field rows — `appraisal_price` **47 passed / 0 tbd / 0 failed / 14 n/a**; no `appraisal_price_*` reason code anywhere |
| `.venv/bin/python -m mijual.scheduler once --stages extract --offline` | `label 61row/0call; r1_prose …` — **0 live calls, ▷ $0.0000**; the stage wiring runs the free pass first |
| curl over all 16 exposable ③ pages | **16/16 → 200**; 12 carry `appraisal_price` (`display: value`, `estimated: false`, `quote`, `span`, `rcept_no`), 4 carry **no key** |
| span re-check (scratch script, live payloads) | **12/12** served citations re-slice to their quote *and* to their value |
| `curl /board/summary` | every landing number identical (see below) |
| `python3 scripts/workflow.py validate` | passed |

### Before → after (the corpus numbers)

Measured with the same script on both sides; the diff is **only** the new field.

- exposable events **488 = 50/422/16 — unchanged**; every event state unchanged.
- every other field's gate distribution **byte-identical** (`warrant_trading_period`
  73/2/0/3, `dissent_notice_procedure` 14 passed / 1 failed / 10 n/a, …).
- extraction rows **649 → 710** (+61, all `appraisal_price`).
- renderable fields on exposable events gain **`appraisal_price: 12`**; nothing else moved.
- landing/board: 488 · 30일 이내 33 · ② 진행 중 57 · 추후결정 4 · 소멸 앞둔 15 · 실적보고서 69 ·
  **718.1억원 / 548.7억원** · 51,253,956 / 365,527,824 · 0.1402 · 퓨쳐켐 2026-09-04 — **all identical**.

### The 12 values (본문 quote = API `aprskh_plnprc`, both)

세기상사 5,649 · 유진스팩10호 2,079 · 아시아나항공 7,030 · 로젠 2,116 · 알에프텍 9,325 ·
파라택시스이더리움 1,779 · 파라택시스코리아 577 · 휴온스 32,886 · 휴맥스 6,591 · 컴투스엔 750 ·
IBKS제24호스팩 2,160 · 한화플러스제5호스팩 2,090.
The 4 without one: 모다이노칩 (소규모합병 — the 본문 says the right is not granted),
케이피항공산업 · 미래에셋비전스팩7호 · IBKS제25호스팩 (스팩 합병 — the price is deferred to the
증권신고서). All four print `-` in the cell **and** `-` in the API row.

## Spend

**0 LLM calls, 0 OpenDART requests, ▷ $0.0000.** `python -m mijual.extract summary`
still reports the corpus's pre-existing **213 stored calls / ▷ $2.7897** — no
`ExtractionCall` row was created by this slice, by construction (a label row is
written with `call=None`, `model=NULL`, which is how a report tells a free reading
from a paid one).

## Run order, for whoever re-derives the corpus

`python -m mijual.extract labels` → `python -m mijual.gates run`. The label pass
goes through `upsert_extraction`, which **clears the gate verdict on every write**
(the existing contract: a re-read invalidates the previous verdict), so the pass
must always be followed by a gate run — the pipeline's stage order does that
automatically. Verified idempotent: `labels` → `gates run` twice reproduces a
byte-identical measurement. `mijual.estimate snapshot` was **not** re-run: nothing
①-side moved (no R1 row changed).

## Notes for later slices

- **`P5.S13`** renders it: `fields.appraisal_price` = `{value: {price: <int 원>},
  quote: "매수예정가격 5,649", span, rcept_no, korean_name: "매수예정가격",
  estimated: false}`. It is a **fact** — never `EstimateMarker` — and 원 formatting is
  the surface's (the payload carries the integer). A ③ page with no such key renders
  **no row at all**, never `-` and never `0`.
- **No `추후결정` case exists** for this field: the 4 blank cells state no price and no
  ③ filing writes 추후결정 in that cell, so the reader records `absent` (N40's rule —
  only positive evidence earns a `tbd`) and the field is simply missing.
- **Evalset** (P2's frozen artifact) is untouched and unaffected: `evalset/sample.py`
  skips a row whose `field_key` is not in `FIELDS`, so the label field is outside its
  universe today. Whether a deterministic two-witness field ever belongs in an
  accuracy evalset is a `P5.REVIEW` question, not a defect.
- **`scripts/export_design_grounding.py`** would now emit `appraisal_price` in ③
  samples. The landed pack is dated 2026-08-20 and must not be regenerated
  (P3.REVIEW note 3) — export to a scratch dir with `--out` if a diff is ever wanted.
