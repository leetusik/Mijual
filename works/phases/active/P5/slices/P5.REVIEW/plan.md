# Plan — P5.REVIEW: phase review

## Context

P5 "Apply — build the signed design" is fully implemented: 20 middle slices done
(S1–S9 backend, S20 the promoted D4 fix, S5 the promoted D1 fix, S10–S18 frontend,
S19 the fidelity pass). Read `works/phases/active/P5/phase.md` **in full** (the
decomposition, every findings section, the Constraints, the complete Doc impact
list, the Open Questions), `intent.md` (the confirmed scope: everything except the
AI 질문 agent → P6 and deployment → P4), and each slice's `result.md` as needed
(S19's carries the fidelity table and the 19-question operator catalogue).
`docs/current/*.md` is the doc set you review against and — on a pass — version.
P5 is **not** in parallel mode (no `execution` block): a passing review consolidates
docs here.

## Job 1 — validate the whole phase together

Run the phase's validation as one suite (do not re-derive each slice's private
checks; run the standing ones):

- `.venv/bin/python -m pytest` — expect 118 green, ~2.6 s, no network/model/DB.
- `cd frontend && npm run build && npm run typecheck && npm run smoke`.
- `python3 scripts/workflow.py validate`.
- A cross-cutting smoke of the running product (uvicorn + `npm run start`,
  localhost): the landing renders live numbers; one event detail per rights type;
  a 조회 with a breakdown; the auth round-trip; `/portfolio` gated; `/ops` door +
  one tab; then stop everything and clean up any test account. (S19 just did the
  deep fidelity pass — this is a liveness confirmation, not a repeat.)

## Job 2 — judge the phase against its intent

Form a verdict on each, with evidence:

1. **Scope**: everything the intent names is built (FastAPI backend over the P2
   exposure contract · Next.js frontend for R1–R5+R7 surfaces · auth/portfolio ·
   admin panel · vocky integration), and the two exclusions are respected — no AI
   질문 agent code (the nav slot/bare `/ask` shell and the empty conversation port
   are the signed boundary, DECOMP notes 5/7/8), no deployment work (P4).
2. **RESPECT THE DESIGN**: the S19 fidelity table + the phase's recorded readings;
   landed records untouched except S18's sanctioned additive §6.3 update (verify:
   `git log --oneline -- docs/reference/design/` and the no-`-`-lines fact).
3. **Trust rules**: structurally enforced where claimed (present-layer
   construction guards, the AST/import tests, the measured browser invariants).
4. **The deferred-jobs record**: D1/D4 promoted and closed; D2's two checks
   observed and not fired; D3's rationale stands.
5. **The open questions**: the operator catalogue (S19 §4 + phase Open Questions)
   is complete and honestly stated — these are questions, not defects; they do not
   block a pass unless one hides a real scope failure. Judge each.
6. **Workflow hygiene**: every slice has `plan.md`/`result.md`, statuses coherent.

**A non-pass**: complete the whole validation + judgment first, then return
`changes_requested` (or `blocked`) with numbered findings and proposed fix slices
— and do **not** consolidate docs.

## Job 3 — on a pass only: consolidate the Doc impact list into doc versions

The phase's Doc impact list names durable-truth changes across (at least) `api`,
`backend`, `architecture`, `data`, `security`, `operations`, `frontend`,
`experience`, `decisions`, `product`, `qa`. For each affected doc:

- Write the new version content — the current doc updated with the phase's
  accumulated truth (read the existing `docs/current/<doc>.md`, fold in every
  `(P5.Sx)` line's substance from phase.md and the relevant findings; keep each
  doc's own structure and voice; docs only, never source).
- `python3 scripts/workflow.py doc-new-version --doc <doc> --summary "..."
  --source P5.REVIEW` per doc (check the command's exact content mechanism with
  `--help` or by reading `scripts/workflow.py` — follow how P2/P3 reviews did it;
  their versioned files under `docs/versions/` are the precedent).
- `python3 scripts/workflow.py rebuild-docs` and confirm `docs/current/` reflects
  the new versions; `validate` again.

Carry the still-open operator questions into the appropriate docs' Open Questions
sections (they are durable truth too — e.g. `security`'s 수신 주소 재인증,
`operations`' vocky wiring list, `product`'s widget-script gap).

## Wrap-up

Write `result.md`: the validation results, the judgment per Job 2 with evidence,
the doc versions created (or the findings if non-pass), and the operator-question
catalogue pointer. Append a closing note to `phase.md`. Return the structured
verdict with `review_verdict: pass|changes_requested|blocked`, `doc_versions:`
the list you created (or `none`), and the fixed line
`explain: not written — run /explain for this phase`. Do **not** run
`review-phase` or any status transition — the orchestrator records the verdict.
Do not commit.
