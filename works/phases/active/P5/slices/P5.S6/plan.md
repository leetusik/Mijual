# Plan — P5.S6: ③ 매수예정가 backing (D-15)

## Context

Read `works/phases/active/P5/phase.md` (S1–S5 findings binding — note S5 just
re-derived the corpus; trust current DB state, and its measured counts are the new
baseline) and `docs/current/decisions.md` **D-15**: ③ detail does not render 매수예정가
because it is not in the exposure contract; the apply phase **builds the backing** —
this slice. The rendering itself is `P5.S13`'s; this slice ends with the value in the
contract and served by the API. Design reference: R3 `build-prompt.md` ③ rules (the
"매수예정가: NOT in the contract — do not render (posed back)" line is exactly what
D-15 supersedes once this lands) and `grounding/states-and-trust.md`.

## The job

Extend extraction → gates → (as needed) exposure/present/serving so ③ 매수예정가 is a
first-class gated field:

1. **Field spec** — add a 매수예정가 `FieldSpec` to `src/mijual/extract/fields.py`
   (R3 block, following the existing pattern: `rights="R3"`, location/anchor from the
   real ③ 본문 section, a value schema that handles **per-주식종류 prices** (보통주 /
   우선주 rows — read a few stored ③ 본문s first to get the real shape; the 산정방법
   detail string is part of the value if the filings state it). Korean name/description
   consistent with the section's own wording — the `korean_name` becomes UI copy, so
   take it from the filing/section vocabulary, not invention.
2. **Deterministic gate** — per the §7 pattern in `src/mijual/gates/rules.py`.
   Investigate whether the ③ API row (the `mgsc_*` family the period gate already
   references) carries a 매수예정가 to cross-check against; if yes, gate against it
   (the API reference is also an identity check — S5's lesson); if not, a structural
   gate (positive integer 원, quote must state the number, per-종류 consistency).
   Record which.
3. **Re-extraction, bounded** — run extraction for the new field over the ③ family's
   current readable versions only (exposable 16 plus whatever renders; measure and
   state the filing count first). This spends Gemini calls: keep it to the one field /
   one rights type if the extractor supports scoping (check `mijual.extract`'s CLI);
   record calls + cost from `ExtractionCall` rows. Then `python -m mijual.gates run`
   and re-check exposure counts.
4. **Contract/serving plumbing** — whatever is needed so the value actually reaches
   `/events/{rcept_no}` for a passing ③: the generic field-payload path may carry it
   already; update `present`'s pinned `FIELD_NAMES_KO` (S2 note 9 — a test pins it to
   `fields.py`, so the suite will tell you), and check the ③ detail payload renders it
   as a fact (never `EstimateMarker` — it is a filed number). If the field is `tbd`
   (추후결정) the standard no-date/no-value rules apply unchanged.
5. **Prove it** — curl a ③ detail with the field passing (and confirm each of the 16
   exposable ③ pages still serves; spot-check values against the 본문 quote).

## Constraints

- Extraction prompts/schemas: follow the existing FieldSpec conventions exactly;
  §3.6 stands — the model reads, code computes; no arithmetic in the model.
- Evalset (`evalset/`, P2's frozen artifact) is out of scope — do not regenerate or
  edit it; if the new field affects its reports, note it for `P5.REVIEW` instead.
- Corpus mutations are re-derivable; still, note the run commands in `result.md`
  (S5 set the precedent: the offline repair sequence is documented in `operations`
  doc-impact). Re-run `mijual.estimate snapshot` only if something ①-side moved (it
  shouldn't).
- Suite green (89 baseline ≈ 1.2 s); a terse gate test for the new rule following the
  existing gate-test pattern; no fixture sprawl.
- Secrets: `GEMINI_API_KEY` from `.env`, never echoed/logged.

## Validation

- `.venv/bin/python -m pytest` — green.
- The bounded extraction run + `gates run`; before/after counts recorded (③ field
  rows, pass/tbd/fail for the new field, exposable 488 must stay 488).
- The ③ curl check.
- `python3 scripts/workflow.py validate`.

## Wrap-up

`result.md` (including spend); `phase.md` *Findings & Notes* (the field's key, gate,
measured results — what S13 will render) and *Doc impact* (`data` — the 11th field;
`api` — ③ detail now carries it; `qa` — new counts; `decisions` — D-15's backing
landed). Structured verdict. No commits, no status transitions.
