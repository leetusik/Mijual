# Intent — P5

- Captured at: 2026-08-21T23:08:28+09:00
- Origin: operator

## Original Input (verbatim)

> and before the review slice, we need to /create-phase for the apply.

> and note that split agent and other building. other first, agent part later

> split phase

## Confirmed Intent (refined + clarified)

Create the **apply phase** of the P3 design/apply split now — before `P3.REVIEW`
runs — as a `planned` phase. It implements Mijual per P3's signed design records
(the R1–R7 `build-prompt.md` contracts) **except the AI 질문 agent feature,
which is split out to P6 (operator, 2026-08-22: "other first, agent part
later" / "split phase")**: a FastAPI backend over the P2 exposure contract, a
Next.js frontend faithful to the signed design under **RESPECT THE DESIGN**,
the auth + portfolio layer, the admin panel, and the vocky integration (script
widget + observation API). The whole AI 질문 feature — agent backend,
conversation storage, widget + page surfaces — is **P6**, ordered after this
phase.

Deployment/hosting — including the 결격-grade "web reachable unattended
2026-09-07 → 09-11" requirement — is **out of scope**: it stays in the existing
P4 (Ship & Submit). P5 is ordered 3.5, between P3 and P4, so it executes after
P3 and before Ship & Submit.

Decomposition and execution happen later, after P3's review passes: `P5.DECOMP`
reads the signed design records and cuts build slices backend-first, then the
design implementation (single-pass — this is the *apply* phase of a two-phase
split, so no `DECOMP2`). The D1–D4 deferred jobs, whose triggers fire at the
apply phase, are considered for promotion at that decomposition.

## Clarifications Resolved

- Q: Does the apply phase include deployment/hosting (the unattended 09-07→09-11
  requirement)? — A: "Deploy is a separate phase" — and it already exists: P4
  Ship & Submit carries production deploy, so the apply phase excludes it.
- Q: One apply phase or split backend/frontend into two? — A: "One phase" —
  single apply phase; its DECOMP orders slices backend-first, then the design
  implementation.
- Q: Confirm name/objective and creating it now, `planned`, decomposed only
  after P3 review passes? — A: "Confirmed — create it."
- Q (2026-08-22): "split agent and other building" — within P5 as ordered slice
  groups, or two phases? — A: "Two phases", reconfirmed verbatim "split phase" →
  the AI 질문 agent feature moved out to **P6** (order 3.7); P5 = everything
  else. Boundary note: the admin panel's 대화 로그 / 익명 세션 views depend on
  P6's conversation storage — P5's DECOMP decides frames-now vs move-to-P6.

## Notes

- The design/apply split itself was decided at the P3 re-scope (operator,
  2026-08-20: "make this phase design only. …") — P3 designs, this phase builds.
- Phase ID is P5 (not P4) because P4 "Ship & Submit" already existed from
  2026-08-19; fractional order 3.5 slots this phase between P3 and P4.
