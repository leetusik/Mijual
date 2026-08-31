# Result — P11.DECOMP (decompose phase)

- **status:** done
- **summary:** Cut P11 into two independent `implementation / high` slices — P11.S1 (re-cut the ask
  citation chip onto `Citation.tsx`'s R10 conditional-mount popover anatomy) and P11.S2 (rebuild the
  `/ask` start cards as six, one per agent capability) — as bare folders, and answered both questions
  `intent.md` left open in `phase.md`.
- **files_changed:**
  - `works/phases/active/P11/slices/P11.S1/slice.json` (created by `new-slice`)
  - `works/phases/active/P11/slices/P11.S2/slice.json` (created by `new-slice`)
  - `works/phases/active/P11/phase.md`
  - `works/phases/active/P11/slices/P11.DECOMP/result.md`
- **validation:** `python3 scripts/workflow.py validate` → passed (exit 0).
- **deviations:** none. No `research` slice and no `P11.DECOMP2` were cut — see §2.
- **doc_impact:** three foreseen notes appended to `phase.md` `## Doc impact` (frontend.md chip
  anatomy; experience.md start-card set **plus its stale five-tool / 「never calculates」 lines**;
  qa.md regression entries 403 and 384/410). No `doc-new-version` run.
- **doc_versions:** n/a (not a review slice).
- **review_verdict:** n/a.

Everything the next slices need is in `works/phases/active/P11/phase.md` (`## Decisions`,
`## Doc impact`, `## Operator Questions`, `## Notes for later slices`, `## Now`) and is not restated
here. This file is the log of how the breakdown was reached.

## 1. What was read

`plan.md`, `intent.md`, `phase.json`; `docs/current/frontend.md` (the one-Korean-string rule, ~L465),
`docs/current/experience.md` §AI 질문 (L193–212), `docs/current/qa.md` `## Regression Checklist`
(L384, L396, L403, L410), `docs/current/operations.md` `## Operator Runtime`; the code both items land
in (`components/ask/InlineCitation.tsx`, `Ask.module.css` L195–360, `Blocks.module.css` L120–170,
`Answer.tsx`, `DataBlock.tsx`, `CalcBlock.tsx`, `ValueMarker.tsx`, `copy.ts` L306–323, `AskPage.tsx`)
and the pattern to copy (`components/Citation.tsx` + `Citation.module.css`, whole); the agent side
read-only (`src/mijual/agent/declarations.py` tool descriptions, `agent/tools.py` `get_portfolio` /
`save_feedback` / `get_contact` / `TOOL_NAMES`); and R16's landed record for the card decision
(`docs/reference/design/rounds/16-smart-assistant/output/result.md` §D11,
`r16-parts.babel.js` L142–157, `SIGNOFF.md` L545–580).

## 2. Why no `research` slice and no `DECOMP2`

The bar in `plan.md` was "cut research only if `Citation.tsx` read against `InlineCitation.tsx` shows
the re-cut is not the drop-in `intent.md` believes it is". It is the drop-in: `Citation.tsx` already
ships conditional mount, `.wrap { position: relative; display: inline-block }`, the three closes, and
a `fit()` that clamps the popover horizontally into the viewport — all phrasing content, for the same
reason. The one thing that does **not** transfer mechanically is the `place="row"` case, because
`.citationRow { display: contents }` generates no box and therefore cannot be a positioning context.
That was answerable from the CSS in front of me rather than by experiment: `.row`
(`Blocks.module.css` L131) takes `position: relative`, the popover anchors to the row, and R16 §2.6's
「행 아래, 블록 전폭」 geometry survives — while the collapse R16 measured (a panel inside the fixed third
column driving the `auto` track to the quote's max-content and squeezing the value column to zero)
becomes structurally impossible, since an absolutely positioned box sizes no grid track. Decided in
`phase.md`, implemented by P11.S1. Nothing else in the phase depends on something unlearned, so a
second decomposition pass would have nothing to cut from.

## 3. Options weighed and rejected

- **Splitting item 1 into re-cut + fidelity sweep.** Rejected: the matrix verifies the change the same
  slice makes, and a second executor finding a defect could only fix it by writing the same code —
  i.e. a code slice with a different name. `P11.REVIEW` re-walks the product for the acceptance gate,
  which is where an independent pair of eyes belongs.
- **Merging the two items.** Rejected per `plan.md`, and independently right: unrelated files,
  unrelated failure modes, unrelated verification.
- **A served / data-derived card set (Q1).** Rejected on cost and on surface risk: an endpoint plus a
  loading and failure state on the one screen that must never look empty, for nothing the reader sees,
  in a phase due before P4. The aging concern is real, so it is answered inside the copy (companies
  confirmed live at P11.S2) and flagged for `defer-job` at the review.
- **Company-free, evergreen card sentences.** This was my first instinct against aging and it is
  **blocked by the signed record**: R16 D11 states 「범위가 항상 전체 공시이므로 모든 첫 질문은 회사(또는
  접수번호)를 담는다」. Under RESPECT THE DESIGN the operator authorized the copy and the count, not that
  rule. So the three 공시 cards name companies (three different ones, three different 권리 가족, per
  D11's other set rule) and only the three non-공시 cards (포트폴리오 · 연락처 · 의견) carry none — their
  tools take no filing argument, so the rule's purpose is untouched.
- **A 의견 card that asks *about* feedback instead of filing one (Q2).** Rejected: `save_feedback`'s own
  declaration fires it only on an actual opinion, so such a card routes to `get_contact` and the
  capability stays invisible — the exact defect this phase exists to close.

## 4. Findings

1. **`D11` is R16's design-decision id, not deferred job D11.** `works/deferred/open/D11` is
   "Serve the 집계 범위 dates on a stockless read (Q32b)" and has nothing to do with cards; the 「4장」
   comes from `rounds/16-smart-assistant/output/result.md` §D11. `intent.md`'s reference is correct in
   substance and easy to misread — recorded in `phase.md` so P11.S2 does not chase the wrong D11.
2. **`plan.md` expected the stale 「5장」 in `qa.md`; it is not there.** The current checklist entry
   (qa.md L403) already reads 「질문 카드 **4장**」 and is accurate. The stale 「5장」/메타 카드 lines live in
   R16's landed `build-prompt.md` §2.7b and 회귀 21, catalogued as known-stale in `SIGNOFF.md` L575–577
   — an **immutable record**, not to be edited. What P11 changes is qa.md L403's count, at the review.
3. **`docs/current/experience.md` §AI 질문 is stale from P9**: L205 lists five tools and L206 says
   「The agent never calculates」, both superseded by R16's auditable calculator and the seven-tool
   registry (`agent/tools.py` `TOOL_NAMES`). The card work rewrites that same paragraph's neighbourhood,
   so the correction is folded into the same doc version rather than filed separately.
4. **`MIJUAL_OPERATOR_CONTACT` is unset in the repo `.env`**, so a 연락처 card answers the honest-unset
   line today. That is the product behaving correctly, and the only genuine operator decision this
   breakdown surfaced — on `## Operator Questions`.
5. **Server-side numbering confirmed out of scope**, as `plan.md` required me to say either way: the
   defect is entirely in `Ask.module.css` L261–280's always-mounted `display: grid` panel, and nothing
   in `agent/citations.py` / `agent/events.py` participates.
6. **Widget clipping is the non-obvious risk of the re-cut**: `.thread { overflow-y: auto }` at 440×620
   can clip a popover opened on the last answer, and `Citation.tsx`'s `fit()` clamps horizontally only.
   Noted for P11.S1 rather than solved here.

## 5. Commands

```
python3 scripts/workflow.py new-slice --phase P11 --slice P11.S1 --name "Re-cut the ask citation chip onto the R10 popover anatomy" --kind implementation --risk high --order 1
python3 scripts/workflow.py new-slice --phase P11 --slice P11.S2 --name "Rebuild the /ask start cards to demonstrate every agent capability" --kind implementation --risk high --order 2
python3 scripts/workflow.py validate      # Workflow validation passed.
```

Both new folders hold `slice.json` only — no `plan.md` was pre-filled. `phase.md` is 157 lines /
12.3 KB, inside the 200-line / 16 KB budget. No commit, no status transition, no `accept-gate`, no
product code.
