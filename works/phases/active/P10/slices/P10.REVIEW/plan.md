# Plan — P10.REVIEW (phase review, gated)

Read `works/phases/active/P10/phase.md` whole, `intent.md`, and each slice's `result.md`
verdict block. `CLAUDE.md`'s review rules govern; this plan says what *this* phase needs.

**This phase's acceptance gate is `required: true`.** So the review has gate stages on top of
the usual ones, and the loop ends at a `pending` stop rather than at a recorded verdict.

## 1. Validate the phase as a whole

Not slice-by-slice re-runs — the phase together:

- `.venv/bin/python -m pytest` (expect 154 passing)
- `cd frontend && npm run build && npm run typecheck && npm run smoke` (expect 22/22)
- `python3 scripts/workflow.py validate` (two pre-existing `P9.S1`/`P9.S1B` unknown-kind
  warnings are history, not findings)
- the **whole cumulative `## Regression Checklist`** in `docs/current/qa.md` (~130 lines) —
  this is the review's own job and S5 deliberately did not duplicate it. It includes the four
  AST import scans and the `gates run` byte-identical check; run them.

## 2. Open the product yourself — do not pass on other slices' reports

S5 swept 36 page-views and captured 35 screenshots under `var/p10s5/`. **That is evidence to
check, not a substitute for looking.** Bring the stack up in the `## Operator Runtime` and
spot-check this phase's headline claims with your own eyes:

- both marks paint on the cosmos-dark chrome, dev **and** the production build;
- both document titles;
- the 실권주 disclaimer at one of its two render sites;
- `/docs` carries `주주의관제탑 API`;
- the assistant names itself 주주의관제탑 when asked a Korean meta question.

**`make stack-up` fails** — host port 5433 is held by `changple_web_dev_postgres`, the
operator's unrelated project. `slices/P10.S5/result.md` §0 has the recipe. Never stop the other
project's container; restore whatever you touch.

Then **walk it once with fresh eyes, as a first-time user**, and report everything dead,
confusing or annoying — explicitly **not** judged against the design record. Those observations
go into the walkthrough, never into silent fixes.

## 3. Route all six `## Operator Questions` — none may be left unrouted

A review may not pass with an unrouted entry. Each of the six goes to exactly one of:

- **the acceptance walkthrough**, as a decision the operator takes with the product in front of
  them; or
- **a deferred job** — you *list* them with a title, reason and trigger; **the orchestrator
  files them** with `defer-job`. Do not run `defer-job` yourself.

My read, which you should apply unless you disagree with a reason: the **heights**, the **ops
mark's typography** and the **favicon** are live decisions for the walkthrough — each already
carries a measured recommendation the operator can accept in one word. **P4's `[미주알]` mail
subject** cannot be acted on in this phase and belongs in a deferred job that P4 will pick up.
The **`/ops` 390px stacking** is pre-existing and wider than the mark — a deferred job, named in
the walkthrough so the operator is not surprised by it. The **dev-tooling banners** are yours to
route; say which and why.

## 4. Consolidate the docs — on a pass, before the gate opens

This phase is **not** in parallel mode, so a passing review writes the new doc versions itself,
in the pass path, *before* the gate opens.

**The ledger already exists: `slices/P10.S4/result.md` §2**, line-level, covering six documents.
S4 built it precisely so this step is mechanical rather than a fresh act of judgement. Apply it
with `doc-new-version --doc <doc> --summary "..." --source P10.REVIEW`, plus `qa.md` from the
five checklist lines S5 drafted in `slices/P10.S5/result.md` §6. Cross-check against
`phase.md`'s `## Doc impact` list so nothing filed by S1–S5 is dropped.

Four things in that ledger are **not** renames and must be handled as it says:

- the **latin mark as an English subject** (`security.md:151`, `:396`, `decisions.md:292`) —
  reword, never substitute;
- **content now false rather than stale** — the docs still describe a ring wordmark, "five
  binary assets" where four remain, and a "never a local edit" rule the derived white variant
  breaks;
- **history that must not change** — `frontend.md:120`, `decisions.md:594` (a verbatim operator
  quote), `:649–657`/`:665` (a dated domain fact sheet), `:674–675`. Renaming history is this
  phase's worst available failure;
- S4's two flagged judgement calls (`frontend.md:119` — add a superseding row rather than edit
  an immutable one; `decisions.md:292` — prefer "this product" over stamping the 2026-08-30 name
  onto a 2026-08-22 decision). Decide them, and say what you decided.

Run `rebuild-docs` after, and confirm `docs/current/` regenerated cleanly.

**A non-passing verdict stops you before this step** — complete validation and judgement first,
then return the verdict with numbered findings and proposed `fix` slices, and do no pass-only
work.

## 5. Judge against the objective

`intent.md` is the confirmed intent. Check honestly:

- Is the name uniformly the unspaced `주주의관제탑`, with **no latin mark** left on any
  user-facing surface?
- Did anything **out of scope** get renamed — `src/mijual/`, `MIJUAL_*`, `X-Mijual-CSRF`, both
  `name` fields, the DB credential, "Mijual Design System"? Any such change is a finding.
- Did any **signed design value** change without the operator? The heights and
  `Ops.module.css` must be untouched.
- The phase widened twice past its decomposition — the 미주얼 agent prompts (S3) and the
  impossible `docs/current/` assignment (S4). Confirm both were handled and recorded rather
  than papered over.

## 6. The walkthrough

On a pass, return a **`walkthrough`** the operator can follow start to finish. It must open
with the fact that **`make stack-up` does not work as written** and give the recipe, and note
that `/ops` shows only the door without credentials in `.env`. Then: which URLs to open, at
which viewports, what to look at, and the three live decisions stated as decisions — each with
its measurement and its one-word-acceptable recommendation. Point at `var/p10s5/` screenshots
by filename where they help. Name what is **not** being asked of them, so they do not re-test
what is already proven.

Write it in Korean or English as you judge best for this operator — the product surface is
Korean-only, but the operator works in English and prior gates were written in Korean; match
`P9`'s walkthrough register.

## Constraints

- No commits, no phase/slice status transitions, no `accept-gate` — all the orchestrator's.
- Do not run `defer-job`; list them for me.
- Do not fix findings; propose `fix` slices.
- Do not write a phase explainer. Return the fixed pointer
  `explain: not written — run /explain for this phase`.

## Verdict

Return `review_verdict` `pass` / `changes_requested` / `blocked`, numbered findings if any, the
deferred jobs for me to file, the `walkthrough` on a pass, and the `explain` pointer. On a pass
the phase does **not** become `done` here — I open the gate and stop, and the operator clears it.
