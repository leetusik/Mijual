# Plan — P11.DECOMP (decompose phase)

Kind `decomposition`, risk `high`, executed by `slice-executor-high`.

## What this slice is

Cut P11's middle slices. **Bare folders only** — `new-slice` for each, never a
pre-filled `plan.md` in any of them — plus the breakdown, findings, decisions and
handoff notes written into `works/phases/active/P11/phase.md` under its budget
(200 lines / 16 KB). No product code is written here.

## Read first

1. `works/phases/active/P11/intent.md` — the confirmed operator intent, in full. It
   is unusually complete: both defects are already root-caused with file and line
   pointers, and it names two questions it deliberately left for you.
2. `works/phases/active/P11/phase.md` — the notebook you will be rewriting.
3. Only the `docs/current/` **sections** this phase touches, just in time:
   - `frontend.md` — the ask surface's component rules and the one-Korean-string
     rule (~L412–413) the card question turns on;
   - `experience.md` — R6-4 / R16 §2.6 chip behaviour and R16 §2.7b start screen;
   - `qa.md` — the `## Regression Checklist`, so you know which existing entries
     these two items put at risk (the start-screen card entry is stale at
     「5장」 per `copy.ts`'s own note — worth a finding);
   - `operations.md` `## Operator Runtime` — the runtime every later slice's
     browser verification must use (`make stack-up`, `http://127.0.0.1:3010`,
     Chrome desktop + a mobile viewport, plus the production build when the two
     could differ). Do not re-derive it; just note it applies.
4. The code the two items land in (read, do not edit):
   `frontend/components/ask/InlineCitation.tsx`, `Ask.module.css` (the chip and
   `.quoteWrap`/`.quoteClip`/`.quotePanel`/`.citationRow` rules), `Answer.tsx`,
   `DataBlock.tsx`, `CalcBlock.tsx`, `ValueMarker.tsx`, `copy.ts`, `AskPage.tsx`,
   `AskWidget.tsx`; and the pattern to copy — `frontend/components/Citation.tsx`
   with `Citation.module.css`.

## Two things that are already decided — do not re-open them

- **This is not a visual-design phase.** `intent.md` has no `## Design Style`
  section and none is owed: the operator explicitly declined a design round
  ("Copy + card count may change, existing visual style kept, no design round").
  Do **not** read that absence as an unanswered question, do **not** stop
  `pending` to ask for a style, and do **not** cut a `co-work` slice. R16's signed
  chip and card visuals are the spec these slices must land *on*, not move.
- **Server-side numbering is correct and out of scope.** `agent/citations.py`
  `_number_for()` and `agent/events.py` `TextEvent.citations` are not touched by
  item 1. If your reading contradicts that, say so as a finding rather than
  quietly widening the phase.

## Two questions this slice must decide

`intent.md` § Notes leaves these to you, with its leanings. Decide both, record the
decision and its reason in `phase.md` `## Decisions`, and let the slice breakdown
follow from them. Neither is an operator question — do not park them on
`## Operator Questions`.

1. **Hard-coded card companies, or data-derived?** The four current cards name
   companies that will age out of the corpus; a start card offering a question the
   agent can no longer answer is worse than a generic one. Weigh keeping them as
   signed Korean strings in `copy.ts` (the frontend's one-Korean-string rule)
   against a served/derived variant, and pick. Cheapness and the pre-P4 deadline
   are legitimate weights.
2. **Does a `save_feedback` card belong on the start screen, and if so does it ask
   *about* leaving feedback or actually file one?** Clicking it has a write side
   effect no other card has.

Also settle, as part of the breakdown: **how many cards**, and **which capability
each card demonstrates**. The target is that clicking the cards one at a time
exercises every narratable agent capability — `search_events`, `get_event`,
`calculate`, `get_portfolio`, `get_contact`, and `save_feedback` if you keep it.
`security_check` is explicitly **not** a card candidate (`intent.md` says why).
You do not have to write the final Korean strings here — that is the card slice's
job — but you must record the capability→card mapping so the card slice is not
re-deciding the shape.

## How to cut the slices

- Selection is by `order`; give each slice a deliberate `--risk`, because `risk`
  picks the executor tier and is this phase's main cost lever. `low` → the `mid`
  tier, and only for a genuinely one-line/few-line edit or docs. **Anything that
  writes real code, or spans more than one file, is `high`.**
- Expect the two items to be **independent** and cuttable in either order; item 1
  is the harder one and the one the demo video shows most. Do not merge them into
  one slice — they have unrelated blast radii and unrelated verification.
- Item 1 (the chip re-cut) is cross-file React + CSS with a hydration constraint
  (every element inside `<p class=prose>` must stay phrasing content — a `<div>`
  is reparented by the parser) and three signed placements to hold. Rate it
  `high`. Consider whether the re-cut and the three-placement/two-surface
  browser fidelity verification want to be one slice or two; if you split, say
  in `phase.md` exactly what the second one inherits.
- Item 2 (the cards) is copy plus whatever your Q1/Q2 answers imply. Rate it on
  what it actually does: if it is `copy.ts` strings only it may be low-risk, but
  if a `save_feedback` card, a derived source, or `AskPage.tsx`/`AskWidget.tsx`
  changes come with it, it is `high`.
- **Consider a `research` slice only if you genuinely cannot cut past a point.**
  The bar: `--kind research --risk high`, findings-only, no product code,
  findings landed in `phase.md`, and a `P11.DECOMP2` after it. Given how fully
  `intent.md` root-causes both items, the expectation is that you do **not** need
  one — but if reading `Citation.tsx` against `InlineCitation.tsx` shows the
  re-cut is not the drop-in `intent.md` believes it is, cutting research + a
  `DECOMP2` is the right call, not guessing.
- Verification belongs inside the slices that make the change, in the
  `## Operator Runtime` runtime, through a real browser (Aside preferred; name the
  instrument actually used). Do not cut a separate "verify everything" slice —
  the `P11.REVIEW` slice already re-walks the product for the acceptance gate.
- Do **not** create `P11.REVIEW` (it exists) and do **not** run `accept-gate`,
  `start-slice`, `finish-slice`, `set-*-status`, `doc-new-version` or any commit.
  The orchestrator declares the acceptance gate right after this slice —
  `intent.md` already anticipates `--require`, and your breakdown should make it
  obvious why.

## What to write into `phase.md`

Edit, do not append. Specifically:

- `## Decisions` — the Q1 and Q2 answers with their reasons; the card count and
  the capability→card mapping; the shape chosen for the chip re-cut (one slice or
  two, and where the fidelity verification lands).
- `## Doc impact` — a one-line note per durable-truth change you can already
  foresee (do **not** run `doc-new-version`; the review consolidates). Likely
  candidates: `frontend.md` for the chip anatomy, `experience.md` for the start
  card set, `qa.md` for the stale 「5장」 regression entry.
- `## Operator Questions` — only genuine operator decisions, if any surface. Your
  two assigned questions are not among them.
- `## Notes for later slices` — the constraints each middle slice needs, tagged
  `**(from P11.DECOMP, for P11.Sn)**`: the phrasing-content/hydration rule, the
  three signed placements, the `.citationRow { display: contents }` case that is
  **not** broken, the ≤767 44px target rule, the "card sentence is the question
  sent" rule, and the runtime/instrument expectation.
- `## Now` — ≤ 15 lines, rewritten last, as the handoff to the first middle slice.
- Never touch the generated `## Slices` block.

## Validate

`python3 scripts/workflow.py validate` (run from the repo root
`/Users/sugang/projects/personal/Mijual`). No tests, no build — this slice writes
no code.

## Result

Write `works/phases/active/P11/slices/P11.DECOMP/result.md` **verdict block
first**. Keep the log of what you read, what you rejected, and why the breakdown
came out this way in `result.md`; keep what the *next* slice needs in `phase.md`.
Do not restate one in the other. Return the structured verdict with a one-line
`summary` suitable for the `## Slices` table.
