# Plan — P5.S20: Multi-span citations for multi-addend 실적보고서 figures (promoted D4)

_(Original brief: `works/deferred/promoted/D4/brief.md`. Trigger fired at `P5.S3`, wider
than the brief assumed: **7 figures across 4 companies** — SKC, 에스에너지, 루닛,
한화솔루션 — carry a value summed from two table rows while `raw`/`span` cite one
addend. S3's interim guard (`present.money._cited_count`) drops the quote on any figure
whose cell text doesn't parse to exactly that value, so those figures currently render
with no verbatim chip. This slice makes them properly citable.)_

## Context

Read `works/phases/active/P5/phase.md` (S1–S6 findings; S3 note 5 documents the interim
guard, S5/S6 set the corpus re-run precedents). The defect's exact seat:
`src/mijual/estimate/perf.py` — summed figures keep only the **first** addend's cell
(`used_cell = used_cell or line[column]`; same pattern for `excess_cell`), so
`Cited.value` is the sum but `raw`/`span` is one cell. `Cited` (~line 85) carries a
single `raw` + `span`.

## The job

1. **Extend the citation model** — `Cited` gains multi-part support (e.g. a `parts`
   list of `{raw, span}` — design it so the single-part case stays byte-compatible
   with the stored JSON already in `performance_report.facts` / `.lapse`, or migrate
   the stored form deliberately by re-running the snapshot; decide and record).
   Every addend that contributed to a summed figure keeps its own cell text + span.
2. **Fix the summing sites in `perf.py`** — collect *all* contributing cells, not the
   first. Check for the same pattern anywhere else in the module (any `x = x or cell`
   beside an accumulating `+=`).
3. **Flow it through** — `present` (money/lapse shapes): a multi-part figure serves a
   citation whose parts are each verbatim; relax S3's interim guard only for the case
   it existed to block — the guard's rule becomes "each part's text parses, and the
   parts sum to the value" (never attach a chip whose text doesn't back its number).
   The single-cell path is unchanged.
4. **Re-derive** — `python -m mijual.estimate snapshot` (and whatever re-parse
   populates `performance_report.facts` — find it; S5's sequence is the precedent);
   confirm idempotent/converged.
5. **Measure and prove** — before/after: the 7 affected figures now carry full
   multi-part citations that re-slice to their spans and sum to their values; the
   headline pair 718.1억/548.7억 and every landing number unchanged; 대한광통신's
   two-reading disagreement still intact. Curl 한화솔루션's ① detail (청약 결과 inset
   figures now cited) and a 놓친 돈 breakdown (에스에너지).

## Constraints

- The evidence rule is absolute: no chip whose text does not state (in parts that
  sum) the number it backs. The 발행사 기재 불일치 two-reading rule is untouched.
- Frontend rendering of multi-part chips is `P5.S13`/`P5.S14`'s job; this slice ends
  at the served contract (payload shape recorded for them in `phase.md`).
- Suite green (91 baseline); a terse test for the multi-addend case (build a small
  grid inline, no fixture files). Stored-JSON compatibility pinned by a test if you
  keep dual-shape reading.
- Offline only — 0 OpenDART requests, 0 LLM calls.

## Validation

- `.venv/bin/python -m pytest` — green.
- The re-derivation run + before/after measurements in `result.md`.
- The two curl checks.
- `python3 scripts/workflow.py validate`.

## Wrap-up

`result.md`; `phase.md` *Findings & Notes* (the multi-part payload shape S13/S14
render) and *Doc impact* (`data` — the citation model; `api` — multi-part citations;
`qa` — the D4 fragile area closes). Structured verdict. No commits, no status
transitions.
