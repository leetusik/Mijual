# Plan — P3.S1: Design grounding pack

## Why

The seven design rounds (P3.S2–S8) must be grounded in real content — never lorem
(`design-cowork`). Claude Design reads this repository through its repo connection, but the
live data lives in Postgres, which it cannot query. This slice exports a dated, regenerable
snapshot of the real product content into the repo so every round's `handoff.md` can point
at real numbers, real Korean copy, and real edge-state examples.

This is the phase's only non-design slice. It writes **documentation/data artifacts only** —
no product implementation code, no HTTP layer, no frontend scaffolding (phase constraint).

## Where

`docs/reference/design/grounding/` (new directory — this also seeds the durable
`docs/reference/design/` tree the rounds will build on). Layout is yours to design; keep it
small and navigable — a `README.md` index plus a handful of focused files beats a sprawl.

## What to export

Everything measured fresh at export time (do NOT copy the numbers in `phase.md` — they are
2026-08-20 measurements and may already have drifted). **0 DART requests, 0 LLM calls** —
local Postgres reads only. Every artifact carries (a) its measurement date and (b) the exact
command(s) that regenerate it.

1. **Board snapshot** — exposable-event counts by rights type (①/②/③), renderable field
   instances, urgency distribution (events within 7/30 days of today and of 2026-09-07),
   and a small table of the most urgent live events per type (corp name, event, key date,
   D-day label via `calc.d_day`).
2. **Headline numbers** — the 소멸가치 estimation report figures (`python -m mijual.estimate
   report`, including the `--korean` rendering): total lapsed value, offering count, open /
   upcoming counts, gate cost. Mark every estimate with `▷` exactly as the product must.
3. **Per-type sample events** — 2–3 real events per rights type as `EventExposure` /
   `FieldView` JSON (from `mijual.gates.exposure`), chosen deliberately to include:
   - a healthy fully-renderable ① with citation spans (quote + span + rcept_no),
   - a **철회** event (shows `WITHDRAWN_NOTICE_KO`),
   - a **추후결정** case (`tbd` — structurally no date),
   - a **발행사 기재 불일치** (`lapse_mismatch`) case,
   - an ② with a populated `option_schedule` (the two-date-convention trap),
   - an ③ showing the `superseded_api_reference` version-scoping split,
   - the `rcept_no 20250930000508` corp_name display trap (풍전약품 vs 에스씨엠생명과학).
   For each: one-paragraph annotation of *what a designer should notice* (state, which
   fields are absent because gates blocked them, what the Korean notice says).
4. **Korean state & copy inventory** — the full reason-code list with Korean renderings
   (`python -m mijual.gates reasons` or equivalent), `WITHDRAWN_NOTICE_KO`,
   `TBD_DISPLAY_KO`, blocking-flag notices, and the product terminology list (신주인수권증서,
   소멸, 오버행, 매수청구권, 정정공시, …) consistent with `docs/current/product.md`. This is
   the design rounds' copy source — UI copy is *locked* by default.
5. **The three product states + trust primitives** — a short prose page (from
   `docs/current/product.md` v0002 + `gates/exposure.py`): fact vs ▷ 추정, the citation
   affordance (quote + span + rcept_no → 원문), state vocabulary (정상/임박/철회/추후결정/
   비노출), and the rule "gate-blocked fields are simply absent, never shown with a warning".
6. **UI traps page** — `option_schedule` needs a `date_basis` marker before rendering as a
   date; `lapse_mismatch` renders the literal string "발행사 기재 불일치", never silently
   reconciled; the corp_name master-data trap affects display only.

## How

- Use the existing modules/CLIs (`mijual.gates`, `mijual.gates.exposure`, `mijual.estimate`,
  `mijual.cb`, `mijual.calc`) — read `src/mijual/gates/exposure.py` and `src/mijual/calc.py`
  first. Repo venv is `.venv`; Postgres is the compose service (host port 5433) — start it
  with docker compose if it isn't running.
- Ad-hoc `python -c` / CLI invocations recorded verbatim in the artifacts are fine. If a
  repeatable export genuinely needs a script, put ONE small script under `scripts/` (e.g.
  `scripts/export_design_grounding.py`) — a documentation tool, not product code; nothing
  under `src/mijual/`.
- Language: artifact meta/annotations in English; all product copy verbatim Korean.
- Keep the pack lean — the designer needs representative truth, not the whole corpus.

## Wrap-up

- Append to `phase.md` → Findings & Notes: the fresh measurements (with date), anything that
  drifted from the 2026-08-20 figures, and any gap a design round will need filled (missing
  real content = a question for the operator, never invented data).
- Doc impact: none expected (this is reference material, not durable-doc truth); add a note
  only if you learn something that changes durable docs.
- Write `result.md` in the slice folder; run `python3 scripts/workflow.py validate`.
- Never commit; never transition status.
