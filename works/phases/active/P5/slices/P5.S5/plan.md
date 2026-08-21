# Plan — P5.S5: Identity-scope the API-backed gates — re-pair 정정 filings joined to the wrong 사채

_(Promoted D1; original brief: `works/deferred/promoted/D1/brief.md`. Its trigger fired:
P5 renders ② detail pages — `/events/{rcept_no}` is live since P5.S3.)_

## The defect (read these before touching anything)

`works/phases/active/P2/phase.md` notes **N62** (the finding), **N63** (the shape
deliberately not taken then), **N31** (why `hint_mismatch` must stay evidence, not an
event-level blocker), **N81** (pairing-history reach is a correctness knob), and the
S5/N48 decision they protect. Then `src/mijual/collect/pairing.py` and
`src/mijual/collect/runner.py` (`place`, `pair_correction` call site,
`retire_superseded_unpaired`, `unpaired_correction_head`), and `docs/current/qa.md`
*Known Fragile Areas* (D1 entry).

Substance: all 4 remaining ② gate failures are one finding — three 정정 filings
(엑시큐어하이트론 `20260630000509`, 알파AI `20250930000580`, 제이에스링크
`20251204000439`) whose 본문 `최초제출일` names an original never collected
(2024-09-06 / 2025-05-07 / 2024-12-17), so nearest-earlier pairing attached each to a
**different CB of the same corp**. Their 조기상환 schedule and 보호예수 date belong to
another bond; the API-backed gates caught it precisely because gate 7/8's API reference
is also an identity check. The product risk: a ② detail page rendering another bond's
values — the defect class this product cannot ship.

## The job

Make the pairing identity-safe for exactly this failure mode, re-run the affected
pipeline stages, and prove the corpus healed — without reopening N48 (an event-level
`hint_mismatch` blocker would take down 42 passing ① rows + 2 tbd; that decision
stands).

**Recommended shape (verify against the code, adapt if measurement says otherwise, and
record why):** when a 정정's 본문 최초제출일 hint names a date for which the corp has
**no collected original** (the hint is `hint_mismatch`-with-no-candidate, not mere
skew), nearest-earlier pairing must not win: split the correction into its own chain
head (the existing `unpaired_correction_head` machinery is the precedent) so its detail
row, gates, and exposure are scoped to itself — and the previously-polluted event's
version chain is restored (the wrongly-attached versions leave it). N63's field-level
alternative (`not_evaluable(foreign_document)`) is the fallback if chain-head splitting
proves wrong for these cases; prefer the fix that gives each bond its own truth over
one that merely blocks fields. Scoping rule either way: the new behavior must be
conditional on the *no-candidate* case so existing correct pairings (including ①'s
±7-day skew cases) are untouched.

## Constraints

- This is pipeline/corpus work: collector/pairing/gates code + a bounded re-run
  (`python -m mijual.collect ...` / gates re-run — find the actual entry points; the
  evidence is stored, so prefer offline re-derivation; if a narrow re-collect of the
  three corps' history is genuinely needed, keep it scoped to them — DART quota is
  real). No schema changes expected; if one is needed it is additive
  (`schema_sync`/`create_all`, no Alembic).
- **Measure before/after and record in `phase.md`:** the 4 ② gate failures; the 422
  exposable-② count; ① passing/tbd counts (must be unchanged: 42 + 2); total exposable
  488 (any shift explained row by row); board tab counts.
- After the re-run: curl the three affected corps' ② detail pages (live Postgres) and
  confirm each renders its **own** bond's 전환가액/전환청구기간/조기상환 — and that the
  previously-polluted twin events are coherent too.
- Suite stays green (87 baseline ≈ 1 s); add at most a couple of terse pairing tests
  for the no-candidate rule if the code shape makes one cheap. No fixture sprawl.
- The web layer should need no change; if a read-layer assumption breaks (e.g.
  `resolve_event` ordering), fix it minimally and record it.

## Validation

- `.venv/bin/python -m pytest` — green.
- The before/after measurement table (above) in `result.md` + `phase.md`.
- The three-corp curl check.
- `python3 scripts/workflow.py validate`.

## Wrap-up

`result.md`; `phase.md` *Findings & Notes* (what the rule is now, the measured deltas,
anything S13 must know) and *Doc impact* (`data` — pairing rule; `qa` — the D1 fragile
area closes; `operations` if a re-run step matters). Structured verdict. No commits, no
status transitions.
