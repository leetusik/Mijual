# Plan — P11.REVIEW (phase review — THIRD PASS)

Kind `review`, risk `high`, executed by `slice-executor-high`.

**Third pass.** Pass 1 passed → the operator rejected at the gate (cards, contact)
→ `P11.F1`/`P11.F2`. Pass 2 passed → the operator rejected again (a hydration
warning on mobile) → `P11.F3`. Your own `result.md` from pass 2 is in this folder;
read it as history, then rewrite it for this pass.

The gate is `required: true` and currently **reset**. A passing verdict returns a
**`walkthrough`** and does not close the phase. Not parallel mode, so a pass
**does** consolidate docs.

## Do this first: the notebook is over budget

`phase.md` is **190 lines / 16,617 bytes** against 200 / 16,384 — `validate`
warns today. Compress it before you add anything. The phase is closing: nearly
every note is consumed, superseded decisions collapse to what is true now, and
all the detail is in six `result.md` files and in git. Getting it under budget is
part of this slice's job, not a nicety.

## What changed since pass 2

`P11.F3` only. Read its `result.md` in full. Two faults, deliberately kept apart:

1. **Chrome's `__gchrome_remoteframetoken`** injected on `<html>` before
   hydration — not a product defect. Silenced by a `suppressHydrationWarning`
   **scoped to `<html>`**. The scope was proved, not assumed: with the flag in
   place the same injection aimed at `<body>` still fires, and a planted deep text
   mismatch still throws #418 in a production build. **Check that reasoning
   holds** — a suppression that quietly hides more than it claims is exactly the
   kind of thing a review exists to catch.
2. **The real one.** `/_not-found` was the single statically prerendered route
   while `app/RequestedPath.tsx` renders `usePathname()`, so the build baked the
   literal `/_not-found` into the artifact and **every production reader hitting
   an unknown URL was shown that as their own address**, then React threw
   #418(text). `await connection()` in `app/not-found.tsx` makes it request-time.
   The plan's original suspect (the root layout's cached contact read) was
   **exonerated** over 19,720 documents across a fetch and an ISR revalidation.

Verify the fix yourself in a **production build** — this bug was invisible in dev,
which is the whole reason it survived two reviews. Hit several unknown URLs and
confirm the reader's own address is echoed, on the first paint, with no #418.

## Validate the phase as a whole

`.venv/bin/python -m pytest` (158 expected), `cd frontend && npm run typecheck &&
npm run build && npm run smoke`, `python3 scripts/workflow.py validate`. In the
build's route table expect **19 `ƒ`, nothing prerendered** — F3 changed the route
kinds, which supersedes F2's 「route kinds unchanged」 line. Cross-check `phase.md`
against all six slices' `result.md`.

## Open the running product yourself

Manifest runtime (`make stack-up`, `http://127.0.0.1:3010`, Chrome desktop **and**
390) **and** the production build. Never pass on the slices' reports alone:

- **The original defect stays fixed** — a sentence on 2+ 근거 renders on one line,
  chips side by side, three placements, page and widget. Two fix slices have
  landed since anyone last looked at this; confirm it.
- **Four cards**, two naming today's companies, resolved per request; the fallback
  still draws four cards with the API stopped.
- **The contact** in the agent answer and the footer, several routes.
- **The 404s**, in production, per above.
- Then **walk it once with fresh eyes** and report what is dead, confusing or
  annoying — to the operator in the walkthrough, never into silent fixes.

**Re-run the whole cumulative `## Regression Checklist`** and re-cut this phase's
rows to the product as it now is, including F3's 404 check.

## Consolidate the docs — pass path only

Pass 2 created `frontend v0013` · `experience v0011` · `qa v0014` ·
`operations v0013` · `backend v0008` · `security v0009`. `P11.F3` supersedes parts
of at least **`frontend`** (the scoped `<html>` suppression; `not-found.tsx` is
request-time; nothing is prerendered; and the standing rule F3 draws — **no
prerenderable tree renders a request-dependent client value**) and **`qa`** (an
unknown URL in the production build echoes the reader's address, no #418). Create
**new** versions superseding them from `phase.md`'s `## Doc impact`; never patch a
file under `docs/versions/`. Then `rebuild-docs`. Docs only, never source.

## Route the open questions

Re-route for **this** gate. Still genuinely open:

1. **The 인용 칩's ≤767 target** (14 × 16px, not R16's stated 44px) — carried
   through two gates unanswered. Carry it again; do not quietly drop it.
2. **`/ops/feedback`'s rows** — ids 1–3 genuine reader feedback, ids 4–8 from
   verification and the operator's own walks. The 의견 card is gone so no new ones
   can appear. Clear or keep?
3. **The operator's real email and phone are in tracked files** (a test pins them,
   the notebook records them) — filed as **D33**, and posed at the last gate as a
   decision. Carry it.

Already settled, do not re-raise: the contact string (landed, F2), the six-card
set (superseded, F1), `save_feedback` being undemonstrated (operator accepted).
**D28** promoted, **D29** dropped, **D34** dropped at F3 (cause found and fixed;
its lone sighting recorded no URL, so re-file on a third). **D30** (footer 「AI
질문」 link 40 × 44 at 390), **D31** (phone wraps mid-number at 600–620px),
**D32** (landing 500s in English with the API down), **D33**, **D35**
(dynamic-segment 404s draw client-only with an empty first paint) are open and
are **not** this phase's work. List anything new for the orchestrator to file.

## If the verdict is not a pass

Stop before consolidation; complete validation and judgment first, then return
numbered findings and proposed fix slices.

## Return

`review_verdict`, the **`walkthrough`**, the deferred jobs to file, and
`explain: not written — run /explain for this phase`. Do **not** run
`review-phase`, `accept-gate`, `finish-slice` or any commit.
