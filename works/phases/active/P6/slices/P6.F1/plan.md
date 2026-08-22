# Plan — P6.F1: thousands-grouped numerals in agent prose (3,200원)

## Why

`P6.REVIEW` finding 4, dispositioned by the operator (2026-08-23, verbatim:
"make it 3,200원. dk how" — mechanism delegated): the agent's answers print raw
contract numerals (`3200원`) while every other product surface shows grouped
ones (`3,200원`). Make agent prose match the product.

## Read first

- `works/phases/active/P6/phase.md` — notes 19–21 and 24 (the tool payload
  shapes, the citation-gate rule — especially the **numeric membership check**
  and the **verbatim-quote rule** — and S7's finding 4 context: the review
  suggested "whether the tool contract should format" as the natural seam).
- `src/mijual/agent/citations.py` (the gate: sentence release, numeric
  tracing, 「…」/quote handling), `loop.py` (release path), `tools.py`
  (payload assembly), `instructions.py` (system instruction).
- How the rest of the product formats: `frontend/lib/format.ts` (client
  grouping) and what the tool payloads currently carry (raw strings from
  `mijual.present` — check `event_payload` / `values.decimal_str`).
- Tests: `tests/test_agent_loop.py`, `tests/test_agent_tools.py`,
  `tests/test_web_ask.py`.

## Requirements (the mechanism is yours; these are not)

1. **The reader sees grouped numerals in agent prose** — `3,200원`,
   `1,234,567원` — wherever a numeric value ≥1000 that came from a tool
   payload is spoken. Korean counting words, dates, rcept_no (14-digit
   identifiers), spans, D-day numbers and years must NOT be grouped —
   group only genuine quantity/amount values (the payload knows which
   fields are figures; identifiers are not figures).
2. **Verbatim quotes stay verbatim, byte for byte**: text inside 「…」 that
   the gate verified against a tool quote, the in-place quote blocks, and
   `TurnEnd.quotes` are never reformatted. (The detail page's own
   `(4,985원 -> 3,200원)` quote already carries its grouping — that is the
   source's text, untouched.)
3. **The gates stay structural.** The never-compute membership check must
   accept the value in whichever form appears (raw or grouped — normalize
   separators before comparison), and citation forcing is unchanged.
   Grouping is presentation, not computation — say so in a comment where
   the normalization lives.
4. **What the reader saw is what the log stores** (`record_turn` from the
   terminal, unchanged rule) — the stored `answer` carries the grouped
   form because that is what was released.
5. **Consistency across surfaces of the turn**: if the fact-row / footer
   strings carry figures, they follow the same rule (check what S2 signed —
   fact-row formats are copy; do not change signed formats, only the
   numerals inside them if they carry raw figures today).

Suggested seam (from the review, not binding): serve display-grouped figure
strings in the tool payloads (so the model naturally speaks them) + normalize
grouping in the gate's membership check; add a release-time grouping fallback
outside quote spans only if measurement shows the model still emits raw
digits. Whatever you choose, record the mechanism and its limits honestly in
`phase.md`.

## Validation

- Full `pytest` green (baseline **137 passed**) with terse new/updated cases:
  a released sentence shows `3,200원` while its quote block stays verbatim;
  membership passes for both forms; rcept_no is never grouped.
- `npm run build` / `typecheck` / `smoke` only if you touch frontend
  (you likely should not need to).
- A bounded live smoke is allowed if `GEMINI_API_KEY` is present (a couple
  of turns, ▷ reported) to confirm the model actually speaks the grouped
  form; scripted-model verification is acceptable if you skip it.

## Boundaries

- No design-record edits, no new Korean copy, no change to signed formats,
  no schema change, no frontend behavior change beyond what falls out of the
  wire carrying grouped prose. No quota/UI additions. Keep the fix narrow.

## Deliverables

- The fix + tests; `result.md`; `phase.md` note (mechanism + limits) and a
  one-line Doc impact addendum if durable truth moved (likely a line under
  `backend`/`api` about figure display strings — the re-review consolidates).
- `python3 scripts/workflow.py validate` passes. No commits, no status
  transitions.
