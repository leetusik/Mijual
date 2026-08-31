# Plan — P10.REVIEW · phase review (round 3)

`kind: review` · `risk: high` · **third pass.** Round 1 passed and the gate was cleared into round 2;
round 2 passed and the operator **did not clear the gate** — they ran a design session instead.
Round 3 applied what came back. Your `result.md` from round 2 is on disk; **rewrite it for round 3**,
keeping the earlier verdicts legible as history.

## What changed since your last pass

- **R18 (`P10.review`) landed** — `docs/reference/design/rounds/18-p10-review/`. Read all three:
  `handoff.md` (the orchestrator's cover note — what R18 supersedes from R17), `output/handoff.md`
  (the returned contract, **read-only**), `output/VERIFICATION.md` (the orchestrator's pre-apply
  re-measurement). **The operator ran this session themselves**, so there is no outgoing handoff, and
  **the mockup was waived again** — nobody has seen R18 running except the two fix slices.
- **`P10.F1`** applied §①③④ — the wordmark to 1247×371, three transparent `#2b8e6c` favicon tiles at
  75%, seven README sections.
- **`P10.F2`** applied §②②b — nav and `/ops` active tabs reserve their 600 width.
- **Round 2's 8 doc versions are already consolidated and must not be re-versioned.** Round 1's ten
  likewise. **Only round 3's four `## Doc impact` entries** are yours.
- The gate is **reset** (`requested_at=none`), still `required: true`.

## 1. Validate the phase as a whole

Everything together, as in round 2: `npm run typecheck`, `npm run build`, `npm run smoke`, `pytest`,
`python3 scripts/workflow.py validate`, then the phase gates (`gates run` twice byte-identical,
`estimate report` twice, `scheduler --offline`, `extract recheck`, `evalset refresh-recall`, the
exposure invariant, the secret scan). Round 3 touched only frontend chrome and two binaries, so none
of them should have moved — which is exactly why you re-run them.

## 2. Five signed values in this phase turned out wrong. Check the corrections, not the claims.

R17 shipped three (a filled counter, ghost ink `-trim` preserves, an 84px reservation that left 8px
of the button covered) and **R18 shipped three broken verification procedures** that `P10.F1` caught.
That is the phase's defining pattern and it should shape where you spend effort.

Re-measure, do not accept:

1. **The wordmark.** 1247×371; ink statistics **78,212 / 69,630 / 154 unchanged** from the 1292 file;
   the two counter islands `50×46+402+226` → 481 and `69×15+969+335` → 15; the alpha-splice hash.
   **The 45 cut columns must have been dead** — verify the band `x=519..588` was zero-alpha over the
   full height in the pre-change file (it is in git).
2. **`P10.F1`'s correction of R18's aspect.** R18 signs `3.3603` and widths `90.7 / 80.6`; F1 wrote
   **3.3612 / 90.75 / 80.67**. `1247/371` decides it. Confirm Chrome agrees in both runtimes.
3. **`P10.F1`'s three replaced procedures actually work** — i.e. each can *fail*. Run the README's
   new ink check against a deliberately wrong file and confirm it reports non-zero. A guard that
   passes on bad input is the thing this phase keeps shipping.
4. **The vertical geometry did not move.** `INK_OFFSET_PX`, both `translateY` values, band centre
   **25.60** at h27. R18 changed only the horizontal.
5. **`P10.F2`'s `left`-array equality**, and that it could have failed: the pre-change arrays
   differed (279.484375 vs 278.78125). Re-measure after, on all five nav routes and all six `/ops`
   tabs, dev **and** production.
6. **`P10.F2`'s accessibility claim, independently.** Dump the AX tree: each nav link and each `/ops`
   tab reads its label **once**. The twin is generated content, and `visibility: hidden` is the only
   thing keeping it out — F2 proved that with an `opacity: 0` negative control. Reproduce it.
7. **`P10.F2`'s one deviation** — `white-space: nowrap` is on the nav's `.link` but deliberately
   **not** on `/ops`'s `.tab`. Verify at **390** that the `/ops` tab row still wraps and does not
   overflow, and that its values are unchanged from before the slice.

## 3. Fidelity to R18 — RESPECT THE DESIGN

Against `output/handoff.md`: every prescription present and nothing dropped, simplified or
"improved". Specifically the **75% favicon / 84% launcher divergence is deliberate** — confirm the
launcher still masks at 84% and was not "made consistent"; the **mobile sheet and the landing board
are deliberately outside** F2's rule; `tokens.css` is untouched; **no new or deleted copy**; and the
design records under `docs/reference/design/rounds/**` were **not edited** by either fix slice.

Also confirm **no orphaned design routes** — R18's mockup was waived, so there should be none.

## 4. The gate stages — `required: true`

**Open the running product yourself.** Do not pass on F1's or F2's reports.

- **Runtime:** `docs/current/operations.md` § Operator Runtime. `make stack-up`, dev
  **`http://127.0.0.1:3010`**, **and the production build**. **1280** and **390**. `/ops` needs
  throwaway `MIJUAL_OPS_ID` / `MIJUAL_OPS_PASSWORD` as environment variables on the API process —
  **never open `.env`** — and **restore the stack afterwards**.
- **Instrument:** Aside if it runs here; neither fix slice could, and both drove real Chrome over
  CDP. Either is fine — **name what you actually used** and never claim a run you did not make.
- **Spot-check the phase's headline claims yourself**, round 1's and round 2's included: both
  document titles, no old name on any reader page, the 실권주 line, `/docs`, the live agent naming
  itself, the favicon `<link>`s in both runtimes, the retired binaries 404, 의견 보내기 opening its
  panel, and the mark now reading **joined** in nav and footer.
- **The functional sweep — mandatory.** Every visible control does something observable; interaction
  states including browser defaults; liveness over time; type into it and wait on anything implying
  live behaviour. Round 2 swept 99 controls with zero dead; the surfaces changed since are the nav,
  the `/ops` tab row and the two binaries, but sweep the product, not the diff.
- **Walk it once with fresh eyes as a first-time user** — everything dead, confusing or annoying,
  explicitly **not** judged against the design record. Round 2's nine findings are in your own
  round-2 `result.md` §6; say which still stand, and add what is new.
- **Re-run the whole cumulative `## Regression Checklist`** in the qa doc, then append round 3's
  lines and **correct the ones round 3 falsified** (the checklist still quotes `1292x371` and the
  opaque 84% tile — `P10.F1`'s doc-impact note names both).

## 5. Route every `## Operator Questions` entry

An unrouted entry blocks the pass. Three are new or changed since your last pass:

- **The landing board's tab strip** — a third instance of the shove defect, deliberately not fixed
  (three children per tab; the twin does not transfer). `P10.F2` measured it: **zero shift at 1280**,
  **0.42px on `CB` at 390**. → this is an **operator decision** (its own design round, or a deferred
  job). Fold it into the walkthrough with the numbers, or file it — but route it.
- **R18 §②b** (`/ops` tabs) — already **CLOSED**, applied by `P10.F2`. Note that R18's own §⑦.1
  still files it as out of scope; the operator's approval is what moved it. Confirm the record says so.
- **Korean coverage** — still open, unchanged: (a) 94,604 B / **(b) 291,072 B adopted** / (c)
  1,022,828 B, `HANGUL_COVERAGE=full` flips it. Carry it into the walkthrough verbatim.

## 6. Docs — consolidate round 3 only, and only on a pass

Round 3's **four** `## Doc impact` entries → `doc-new-version --source P10.REVIEW`. `frontend.md`,
`qa.md` and `decisions.md` are named there. **Rounds 1 and 2 are already versioned** — re-versioning
them is a real error. Docs only, never source. Not in parallel mode, so consolidation happens here.

## 7. What you return

- `review_verdict`: `pass` | `changes_requested` | `blocked`, with numbered findings and proposed fix
  slices if not a pass. **A non-pass stops you before §6.**
- On a **pass**, a concrete **`walkthrough`** — the run command, URLs, what to click, at which
  viewports. Write it for someone who has now been through **two** gates on this phase: say what is
  **new in round 3** and what you are **not** asking them to re-test. It must carry three things:
  1. the **Korean-coverage** decision, with all three numbers;
  2. **look at the real browser tab, light and dark** — `P10.F1` could not photograph the OS tab
     strip (no Screen Recording permission) and proved the tile from served bytes plus a 16 CSS px
     paint instead, so this is the one claim in the phase resting on inference rather than sight.
     Say that plainly;
  3. the **landing board** decision, if you routed it to the walkthrough rather than to a job.
- `explain: not written — run /explain for this phase` — fixed pointer.

**Do not** run `accept-gate`, `review-phase`, `finish-slice`, or any commit; the orchestrator owns
every transition. **Do not** perform the R17/R18 card regroup — it waits for the gate to clear.

## A standing bias for this review

Three of the last five defects in this phase were **checks that could not fail** — a guard over an
all-white image, an aspect nobody divided, a pixel read from transparent canvas. When you verify
something, ask what input would make your check report failure. If there is none, you have not
checked anything.
