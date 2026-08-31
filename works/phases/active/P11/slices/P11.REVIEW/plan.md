# Plan — P11.REVIEW (phase review)

Kind `review`, risk `high`, executed by `slice-executor-high`.

**This phase's operator acceptance gate is `required: true`.** So this review runs
the gate stages, and its passing verdict does **not** close the phase: it returns a
**`walkthrough`**, the orchestrator opens the gate, and the operator walks the
running product before any pass is recorded. Plan your work accordingly.

The phase is **not** in parallel mode, so a passing review **does** consolidate the
durable docs.

## What P11 claimed to do

Two operator-reported defects on the AI 질문 surface (`intent.md` is the confirmed
source of truth — read it in full):

1. **Citation chips broke the prose.** `InlineCitation` mounted its quote panel
   unconditionally and `Ask.module.css` gave it `display: grid`, so a block-level
   box sat in `<p class=prose>`'s inline flow and every chip forced a line break —
   `…입니다.[1] ⏎ [2] ⏎ [3]`. `P11.S1` re-cut it onto `Citation.tsx`'s R10
   conditional-mount absolute-popover anatomy.
2. **The start cards showed one capability out of seven.** `P11.S2` replaced the
   four hard-coded `START_CHIPS_KO` questions with six, one per agent capability.

## Validate the phase as a whole

Re-run each slice's validation commands together, not just the last one's:
`cd frontend && npm run typecheck && npm run build && npm run smoke`, and
`python3 scripts/workflow.py validate` from the repo root. Read both slices'
`result.md` and cross-check `phase.md` against them — a decision dropped from the
notebook, or an `## Operator Questions` entry left unrouted, is a review finding.

## Open the running product yourself

**Do not pass on the other slices' reports.** Bring the product up in the
`## Operator Runtime` runtime (`docs/current/operations.md`: `make stack-up`,
`http://127.0.0.1:3010`, Chrome desktop **and** a mobile viewport, plus the
production build) and spot-check the phase's headline claims with your own eyes:

- a sentence resting on **two or more** 근거 renders on **one line**, chips side by
  side after the period — the defect the operator reported, in the three signed
  placements (프로즈 · 데이터 행 값 · 계산 입력), on `/ask` and in the widget;
- opening a chip moves nothing, and a data row's value column does not collapse;
- the six start cards each fire their intended tool row and return a real answer.

Aside is the preferred instrument but is not installed on this machine (both
slices recorded it), so the documented fallback applies — the same sweep, same
viewports, same manifest runtime, through the real browser available. Name the
instrument you used; never claim a run you did not make.

**Then walk the surface once with fresh eyes, as a first-time reader.** Report
everything dead, confusing or annoying. This walk is explicitly **not** judged
against the design record — findings go into the walkthrough for the operator to
decide, never into silent fixes. Two things this phase makes worth looking at
honestly: the popover's new opaque ground against the prose behind it, and whether
six cards read as a helpful menu or as clutter on first sight.

**Re-run the whole cumulative `## Regression Checklist`** in `docs/current/qa.md`
— all of it, not only this phase's rows — and append this phase's headline checks
as part of the doc consolidation below.

## Route every open question — an unrouted entry fails the review

`phase.md` `## Operator Questions` currently holds **three**. Each must be either
folded into the walkthrough as a decision for the operator, or listed for the
orchestrator to file with `defer-job` (you list them; the orchestrator files them):

1. `MIJUAL_OPERATOR_CONTACT` is unset, so the 연락처 card answers 「미정」. Configure
   a contact string before the P4 demo, and which? (Publishing it is the
   operator's own identity decision.)
2. The 인용 칩's ≤767 target is 14×16px, not the 44px R16 §2.6's prose names —
   R16's own CSS never implemented it either, and closing it breaks something
   signed either way. Close it, and at what cost, or leave it as the round's CSS
   has it?
3. Verification wrote **3 real rows** to the 운영자 검토 대기열
   (`conversation_feedback` ids 4–6), and your own gate walk will add more. Clear
   them from `/ops/feedback` before P4, or keep them as evidence?

Also consider filing, as deferred jobs rather than walkthrough decisions: the
**aging start-card companies** (`phase.md` Decision Q1 named a data-derived card
set as a deferred-job candidate — the corpus moves and three of the *old* four
were already dead), and anything your fresh-eyes walk turns up that is not this
phase's business.

## Consolidate the durable docs — pass path only

On a **passing** verdict, and only then, turn `phase.md`'s `## Doc impact` notes
into new versions with `python3 scripts/workflow.py doc-new-version --doc <doc>
--summary "..." --source P11.REVIEW`, then `rebuild-docs`. Write **docs only,
never source**. The three notes are already written; consolidate what they say,
including the two pieces of pre-existing staleness they carry:

- **`frontend.md`** — the ask chip's anatomy;
- **`experience.md`** — the six-card set, **plus the section's stale P9 lines**
  (L205 lists five tools where there are seven; L206 says the agent never
  calculates, which R16's calculator superseded);
- **`qa.md`** — the `## Regression Checklist` rows: L403's 「4장」 → 6장 with its
  capability claim, L384/L410's 「in place」 → overlay popover, and the two new
  checks P11.S1's behaviour needs.

There is also a **pattern worth a durable line**, and it is the orchestrator's
one addition to the doc consolidation: this surface has now produced "a line per
sentence" **twice**, by two different mechanisms — R14 walk finding 3 was leading
whitespace in the streamed text (fixed at the store boundary in `lib/ask.ts`
`leading()`), and P11's was a block-level box in the inline flow. Both times the
symptom was identical and the cause was not. Record that in `frontend.md`'s
consolidation as a standing caution for anyone who puts a new element in prose:
**everything inside `<p class=prose>` must be phrasing content *and* inline-level**
— it is a two-part rule, and each half has now failed once on its own.

If the verdict is **not** a pass, stop before all of this: complete validation and
judgment first so the orchestrator gets the whole picture in one cycle, then return
the verdict with **numbered findings and proposed fix slices**, and do no pass-only
work.

## Budget

`phase.md` is at **177 lines / 15,987 bytes** against a 200-line / 16 KB budget —
nearly full. You will need to **compress** it, not add to it: superseded decisions
collapse, consumed notes go, and the detail is already in the two `result.md`
files and in git. Do not let the notebook go over budget.

## Return

`review_verdict` (`pass` | `changes_requested` | `blocked`), the **`walkthrough`**
(URLs to open, actions to try, in the operator runtime — say plainly what is real
and what the operator is being asked to decide, including the three questions
above and the opaque-ground deviation), the deferred jobs for the orchestrator to
file, and the fixed pointer `explain: not written — run /explain for this phase`.

Do **not** run `review-phase`, `accept-gate`, `finish-slice` or any commit — all
of those are the orchestrator's.
