---
doc_id: qa
version: v0002
created_at: 2026-08-20T05:11:01+09:00
source: P2.REVIEW
summary: Extraction-accuracy measurement: method, the frozen evalset, cross-model provenance and the first measured numbers
previous: v0001_bootstrap
---

# QA

## Status

P2 established how this repo measures extraction accuracy and produced the first numbers. The
**method** is the durable part; the numbers are true of the corpus as it stood on 2026-08-20 and are
re-measurable at **0 OpenDART requests and 0 LLM calls**.

## Provenance — read this before quoting any number below

**The labels are cross-model judgements: Claude (Opus 5) judging Gemini extractions, at the
operator's direction (2026-08-20). They are explicitly not human ground truth — 0 of the 344 labels
were verified by a person.** Every quote of an accuracy figure must carry that qualifier.

The qualifier is mechanised, not merely written down: `evalset/labels.json` carries a `judged_by`
block (`judge` / `basis` / `imported_at` in KST), `Labels.write()` refuses to write an unstamped file,
`import --judged-by` is **required and never inherited** from the previous file, and the report prints
what the artifact says rather than any hardcoded sentence. A human re-judgement is cheap and open:
overwrite column A of `evalset/sheet.csv`, re-run `import` with a new `--judged-by`, and the report
states the new judge. See `decisions` D-7.

## Test Commands

| purpose | command | expectation |
|---|---|---|
| unit suite | `.venv/bin/python -m pytest` | **59 passed**, ~1 s, no network, no model |
| workspace | `python3 scripts/workflow.py validate` | `Workflow validation passed.` |
| gates (deterministic) | `.venv/bin/python -m mijual.gates run` | **649 field rows — 566 passed / 4 tbd / 14 failed / 65 not_evaluable**; **488 exposable events**; two runs byte-identical |
| exposure summary | `.venv/bin/python -m mijual.gates summary` | 488 exposable, **409 renderable field instances** |
| estimate | `.venv/bin/python -m mijual.estimate report --today YYYYMMDD` | ▷ 718.1억원 / 32 offerings / 14.02 %; byte-identical across runs |
| accuracy | `.venv/bin/python -m mijual.evalset report` | the table below, incl. the 판정 출처 line |
| whole pipeline, offline | `.venv/bin/python -m mijual.scheduler once --offline` | four stages green, **0 requests / 0 calls / ▷ $0.0000** |
| derived re-scores | `.venv/bin/python -m mijual.extract --dry-run recheck` · `... evalset refresh-recall` | idempotent; a second run writes nothing |

There is no lint/typecheck gate and no E2E layer yet (no UI exists). Tests are deliberately terse —
minimal high-value cases, no fixture sprawl.

## The Measurement Method

- **A frozen, stratified sample.** `evalset/sample.json` holds **344 (filing, field) rows over 99
  filings**, drawn deterministically (seed 20260907, per-stratum seeded shuffle over a sorted pool)
  and frozen with every row's value, quote, context and gate verdict. The report reads two JSON files
  and **never the database**, so a label stays meaningful after the corpus moves under it.
- **Both error directions are measured.** Precision of gate-passed/`tbd` rows (what the product would
  show) **and** the gate's **over-blocking** rate on the rows it blocked — because a gate can buy any
  precision figure by blocking more, and one such pattern is already priced at ▷ 49.2억원 of the
  headline.
- **Rates come only from the random draw.** Known hard cases (철회, 추후결정, span-unresolved, gate
  failures, the 실권주 cells that disagree with their own tables) are over-sampled on purpose and
  reported case by case; a `booster` pick adds 정정-해석 rows *only*, so no field's own sample stops
  being random.
- **Strict is the headline.** `partial` counts as a miss; the lenient figure is stated beside it.
  Every rate carries a **95 % Wilson** interval.

## Measured Results (2026-08-20)

**Precision of what the product would show: 98.6 % strict — 213/216 random picks, 95 % CI
[96–100 %]; 100 % counting `partial`.** Labels: 339 `correct` / 5 `partial` / **0 `wrong`** / 0 `skip`
across all 344 rows.

**Over-blocking: 100 %** — 19/19 blocked rows in the random draw, and **48/48** across every pick,
were judged correct readings. In this sample the gate bought **no** precision: it removed no error and
removed 48 true statements. Of those 48, **30 are blocks the product wants** (`field_absent`,
`superseded_api_reference`); 18 are actionable (stale API reference data, single-span citation for
multi-line quotes, a quantified 개월 withheld for an underived 해제일).

**Corpus-wide gate-block rate: 12.2 % (77 of 633 distinct `(rcept_no, field_key)` rows)** — 0 % on
증권발행실적보고서 figures (no model reads them), 4–8 % on ① prose, and **44 % on ③**, which needs its
split every time it is quoted: of 11 blocked `dissent_notice_procedure` rows, **8 are
`superseded_api_reference`**, 1 `api_deadline_absent`, 1 `field_absent`, and exactly **1** is a real
`dissent_period_mismatch`. Quoting 44 % without that split reads as "③ is badly extracted", which the
data does not say.

**정정-해석 recall proxy: 88.70 %** — 177 deterministic `3. 정정사항` rows, 20 unmentioned by the
model, **0 unsupported of 157 model changes**, over 45 records with a parsed table (3 records without
one are excluded and already blocked `no_correction_rows`). This is a **measurement, not a floor**:
the earlier 85.31 % was a matcher artifact (several model changes could bind to one table row), fixed
in P2.F4 and re-scored over stored records at 0 calls / 0 requests. ▷ At the content level the model
covers ≈ 99 % of investor-meaningful items; the residue is boilerplate rows.

**The whole strict-error surface is one defect class.** All 3 strict misses are 실적보고서 values
**correctly summed** from two table rows (예탁결제원 청약 + 직접청약) but cited by one addend (SKC
`20260522000297` ×2, 에스에너지 `20260312000380`). Summing is the right behaviour — not summing would
under-report 청약 and over-report 실권주 — so the defect is the citation contract, not the reading.
▷ ~3 of the corpus's 31 실적 filings carry the split-row form. Tracked as deferred job **D4**.

## Regression Checklist

- [ ] `pytest` green and `workflow validate` clean.
- [ ] `gates run` twice → **byte-identical** output, and the verdict split still 566/4/14/65 over 649
      rows unless the corpus grew.
- [ ] Exposure invariant re-derived read-only: **0** renderable fields outside `passed`/`tbd`, **0**
      `tbd` fields carrying a value, **0** exposable events in a non-exposable state. (Four lines
      through `mijual.gates.exposure.exposure_of_all`; it is the product's trust claim in one number,
      and anything that touches the exposure contract must re-run it.)
- [ ] `estimate report` twice → byte-identical, headline unchanged.
- [ ] `scheduler once --offline` → four stages green at 0 requests / 0 calls.
- [ ] `extract recheck` and `evalset refresh-recall` → second run writes nothing.
- [ ] No secret value appears in any tracked file or generated artifact.
- [ ] No committed claim describes the evalset labels as human ground truth.
- [ ] Any regenerated summary artifact was regenerated **from the final run** whose numbers the prose
      quotes (P1 shipped a stale one once).

## Known Fragile Areas

| area | state | tracked as |
|---|---|---|
| multi-addend 실적보고서 citations | value right, citation points at one addend | deferred **D4** |
| two `rcept_no` rendering on two exposable events each (코이즈 `20260122000058`, 사토시홀딩스 `20251219000402`) | 2 of 488 events; `hint_duplicate` is deliberately outside the blocking set | deferred **D2** |
| ② 정정 filings paired to the wrong 사채 | 4 gate failures; an API-backed gate catches it, nothing else does | deferred **D1** |
| unattended thinking level for the 정정 해석 task | inherits the project preset; a beat run would decide it for a human | `operations` / `decisions` D-4 |
| the 철회 detector on ③ | no real case in the corpus; unit-tested on a constructed row only | `data` |
| 16 duplicate `(rcept_no, field_key)` extraction rows | harmless for verdicts, but a rate computed on 649 instead of 633 is subtly wrong | note when computing rates |

## Open Questions

- No browser/E2E QA exists yet; P3 will need real-browser verification of the rendered board,
  including that a blocked field genuinely never appears.
- Whether a human spot-check pass over a subset of the 344 labels is worth its time before submission
  (it would upgrade the provenance statement, not the machinery).
