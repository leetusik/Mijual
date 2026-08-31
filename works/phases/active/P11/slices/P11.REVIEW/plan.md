# Plan — P11.REVIEW (phase review — SECOND PASS, after the operator's gate rejection)

Kind `review`, risk `high`, executed by `slice-executor-high`.

**This is a re-review, not a first review.** The first pass passed on the merits
and consolidated the durable docs. The operator then walked the acceptance gate
and **rejected it**, which reset the gate and reopened this slice. Two `fix`
slices have since landed. Your job is to judge the phase **as it now stands** and,
on a pass, open the gate again.

The gate is `required: true` and currently **reset** (`requested_at=none`), so a
passing verdict again returns a **`walkthrough`** rather than closing the phase.
The phase is not in parallel mode, so a pass **does** consolidate docs.

## What changed since the first review

The operator's three gate reports, and where each landed:

1. **Drop two cards** — `P11.F1`. The bare-접수번호 `get_event` card and the 의견
   `save_feedback` card are gone; four cards remain. `save_feedback` being
   undemonstrated from the start screen is **accepted by the operator** — do not
   raise it as a finding.
2. **Cards must be caught in real time, not fixed** — `P11.F1`. The two 공시 cards
   resolve their company per request from the live corpus
   (`GET /ask/start-cards` → `reads.load_start_cards`), with a per-card static
   fallback in `copy.ts`. `/ask` is now a **dynamic** route.
3. **Publish the operator contact** — `P11.F2`. `MIJUAL_OPERATOR_CONTACT` is set
   (in the **gitignored** `.env`), the agent answers with it, and the same values
   are published in the global footer via `GET /site/contact`.

Read both fix slices' `result.md` in full, plus `phase.md` and `intent.md`.

## The doc versions from the first pass are now partly WRONG

This is the part a re-review most easily gets wrong. The first pass created
**`frontend v0012`, `experience v0010`, `qa v0013`**, and `P11.F1`/`P11.F2` have
since superseded parts of all three — most obviously the **six-card** set
(`experience`) and the 「질문 카드 6장」 checklist row (`qa`), both of which now
describe a product that no longer exists.

Never patch a version under `docs/versions/`. On a **pass**, create **new**
versions that supersede them, consolidating every `## Doc impact` note now in
`phase.md` — the F1 and F2 lines *and* the corrections they force on what the
first pass wrote. Expect to touch `frontend`, `experience`, `qa`, `operations`,
`backend` and `security`; let the notes decide, not this list. Then
`rebuild-docs`. **Docs only, never source.**

## Validate the phase as a whole

Re-run everything, not just the fix slices' commands: `.venv/bin/python -m pytest`
(158 expected), `cd frontend && npm run typecheck && npm run build && npm run
smoke`, and `python3 scripts/workflow.py validate`. Cross-check `phase.md`
against all five slices' `result.md` — a dropped decision or an unrouted
`## Operator Questions` entry is a review finding.

## Open the running product yourself

Bring it up in the `## Operator Runtime` runtime (`make stack-up`,
`http://127.0.0.1:3010`, Chrome desktop **and** 390) **and** in the production
build, and check with your own eyes — never on the fix slices' reports alone:

- **The original defect stays fixed.** A sentence resting on 2+ 근거 renders on one
  line, chips side by side, in all three placements, page and widget. This is the
  thing the operator reported and it must not have regressed under F1/F2.
- **Four cards**, and the two 공시 cards name **today's** companies. Confirm the
  derivation is genuinely per-request — the `ƒ (Dynamic)` route kind in
  `npm run build`'s table is the tell, and a static render is the original defect
  returning. Check it in the **production build**, where it would actually bite.
- **The fallback**: stop the API, reload, four cards still draw.
- **The contact** in the agent's 연락처 answer *and* in the footer on several
  routes, at desktop and 390, dev and production.
- **The footer got taller between 481 and 820px** (F2 measured the identity line
  growing ~215px, so the action row wraps earlier). Look at it and judge whether
  it reads acceptably — it is a visible change to a signed surface at widths the
  operator may well browse.

Then **walk it once with fresh eyes as a first-time reader** and report everything
dead, confusing or annoying — **not** judged against the design record; findings
go to the operator in the walkthrough, never into silent fixes.

**Re-run the whole cumulative `## Regression Checklist`** in `docs/current/qa.md`,
including the rows the first pass added, and re-cut this phase's rows to the
product as it now is.

## Route the open questions again

`phase.md` `## Operator Questions` holds three, each already marked with how the
first pass routed it. Re-route for **this** gate:

1. The contact string — **answered and landed** by `P11.F2`. Confirm in the
   product, then it needs no further routing.
2. **The 인용 칩's ≤767 target (14 × 16px, not R16's stated 44px) is still
   unanswered** — the operator did not address it in their gate report. It must be
   carried into this walkthrough again, not quietly dropped.
3. The `conversation_feedback` rows — the 의견 card is **gone**, so no new rows can
   be written from the start screen, but **ids 4–7 still sit in the queue** and
   the operator has not said what to do with them. Carry it forward, corrected to
   what is now true.

Anything your own walk turns up that is not this phase's business goes on the
list for the orchestrator to file with `defer-job` (you list them; the
orchestrator files them). Note **D28 is already promoted** (it became `P11.F1`),
**D29 was dropped** (the 의견 card it described no longer exists), and **D30**
(footer 「AI 질문」 link 40 × 44 at 390) is **open and untouched** — F2 measured it
unchanged.

## If the verdict is not a pass

Stop before the doc consolidation. Complete validation and judgment first so the
orchestrator gets the whole picture in one cycle, then return the verdict with
numbered findings and proposed fix slices, and do no pass-only work.

## Budget

`phase.md` is at **183 lines / 16,099 bytes** against 200 / 16,384 — it will go
over on your first append. **Compress it**: the phase is nearly done, most of its
notes are consumed, superseded decisions can collapse to what is true now, and
every detail is in the five `result.md` files and in git.

## Return

`review_verdict`, the **`walkthrough`** (URLs, actions, what is real and what the
operator must decide — including the two questions still open and the footer's
height change), the deferred jobs for the orchestrator to file, and the fixed
pointer `explain: not written — run /explain for this phase`.

Do **not** run `review-phase`, `accept-gate`, `finish-slice` or any commit.
