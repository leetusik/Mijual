# Plan — P10.REVIEW · phase review (round 2)

`kind: review` · `risk: high` · **this is a re-review.** The slice already ran once, passed, opened
the acceptance gate — and the operator **did not clear it**. Round 2 then landed `P10.S6` (the R17
design round) and `P10.S7` (the apply slice). Your `result.md` from round 1 is still on disk;
**rewrite it for round 2**, keeping round 1's verdict legible as history.

## What changed since your last pass

- Round 1's ten doc versions are **already consolidated and must not be re-versioned.**
- `P10.S6` — design round R17. Record: `docs/reference/design/rounds/17-brand-mark-launcher/output/`.
  **The mockup was waived by the operator**, so nothing was ever put in front of them running;
  `SIGNOFF.md` § R17 says so plainly and defers the card regroup to the acceptance gate. **Do not
  perform the regroup** — it is the orchestrator's, and only after the gate clears.
- `P10.S7` — applied R17 plus four operator-directed items in one slice, eight blocks.
- **The runtime moved.** Commit `c8606d0` put the stack on **3010 / 8010 / 5434**, so `make stack-up`
  now works and the old 5433 `!override` recipe is obsolete. Round 1's walkthrough (still on
  `phase.json`) is stale — **your new walkthrough must not repeat it.**

## 1. Validate the phase as a whole

Every slice's validation together, not slice by slice: `npm run typecheck`, `npm run build`,
`npm run smoke`, `pytest`, and `python3 scripts/workflow.py validate`. Then the phase's own gates as
round 1 ran them (`gates run` twice byte-identical, `estimate report` twice byte-identical,
`scheduler --offline`, `extract recheck`, `evalset refresh-recall`, the exposure invariant, the
secret scan) — round 2 touched only the frontend and should not have moved any of them, which is
exactly why re-running them is the check.

## 2. Verify the two corrections `P10.S7` made to the signed record

`P10.S7` corrected R17 twice at apply time **without editing the record**, which is the right
handling — but a slice correcting a signed value is precisely what a review exists to check.

1. **The footer reservation shipped at 108px where R17's code block signed 84px.** R17 §1 states
   *both* `92px` (prose) and `84px` (code). Confirm from the product files that `.inner` **is**
   `.content` (`Footer.tsx` renders `className={`content ${styles.inner}`}`), so
   `padding-inline-end` **replaces** `.content`'s 24px rather than adding to it, making the floor
   `24 + 68 = 92` and not `68`. Then confirm in a browser that 의견 보내기 is actually clickable and
   opens its panel at **768, 1024, 1120, 1255 and 1280** — hit-test the point, do not eyeball it.
   *(The orchestrator independently reproduced this arithmetic; verify it in the running product.)*
2. **The claim that R17's absolute nav numbers are 0.5px high** (border-box vs content-box) while
   the *relationship* holds. Re-measure rather than accepting it.

## 3. Fidelity to R17 — RESPECT THE DESIGN

Against `output/build-prompt.md` and `output/result.md`, check that **nothing signed was dropped,
simplified or "improved"**: the two wordmark heights and their ink offsets; the launcher's full
state table (rest / hover / active / focus-visible / open / reduced-motion); **that the hover colour
change deliberately survives `prefers-reduced-motion`** and was not "tidied" into that block; that
no animation remains anywhere in the launcher; the symbol's 84% ink rule and its two colours; the
favicon's opaque tile at all three sizes; and that the frozen `foundations/tokens.css` was **not**
edited (the override belongs in `app/shell.css`).

Also verify the two class-C derivations by the README's own rule — **pixel signature, never file
sha256** — and specifically that the wordmark derivative has **0 opaque near-white pixels** and the
symbol derivative re-trims to exactly `222x165+0+0`. Those two guards exist because the operator's
delivered files each carried a defect that is invisible except in the shipped variant.

## 4. The gate stages — this phase's gate is `required: true`

**Open the running product yourself.** Do not pass on `P10.S5`'s or `P10.S7`'s reports, however
thorough they read.

- **Runtime:** `docs/current/operations.md` § Operator Runtime. `make stack-up`, dev at
  **`http://127.0.0.1:3010`**, API at **8010**; **and additionally the production build**
  (`npm run build && npm run start`). Desktop **1280** and mobile **390**. `/ops` needs throwaway
  `MIJUAL_OPS_ID` / `MIJUAL_OPS_PASSWORD` or you will only ever see the door — and **restore the
  stack to how you found it** afterwards.
- **Spot-check the phase's headline claims yourself:** the mark painted at its new size on both
  chrome surfaces, both document titles, the favicon actually served (`link[rel*=icon]` present in
  **both** runtimes — round 1 proved its absence the same way), the 실권주 line, `/docs`, the retired
  binaries 404, no old name on any reader page, and the live agent naming itself correctly.
- **The functional sweep — mandatory here, because `P10.S7` shipped real wiring.** Every visible
  control does something observable; interaction states including browser defaults the record never
  drew; liveness over time; and **type into it and wait** on anything implying live behaviour. The
  launcher and the footer button are the obvious ones, but go control by control.
- **Walk it once with fresh eyes as a first-time user** and report everything dead, confusing or
  annoying — explicitly **not** judged against the design record. Those findings go into the
  walkthrough, never into silent fixes.
- **Re-run the whole cumulative `## Regression Checklist`** in the qa doc — every earlier phase's
  headline behaviours, not just this phase's surfaces — then append this phase's lines. `P10.S7`
  drafted them in `slices/P10.S7/result.md` §11.
- Confirm **no orphaned design routes** exist. The mockup was waived, so there should be none at
  all; if you find one, that is a finding.

## 5. Route every `## Operator Questions` entry

An unrouted entry blocks the pass. The notebook's list carries three **closed** by round 2, three
**still routed to deferred jobs** (verify each is actually filed — `workflow.py deferred` reports 23
open), and one **new**:

- **The Korean subset's Hangul coverage** — `P10.S7` adopted **(b) KS X 1001, 291,072 B** over
  (a) 94,604 B (company names fall back to the OS face) and (c) the full block at 1,022,828 B. This
  is a **deliberate adaptation away from changple_web**, whose product has no dynamic Korean. It is
  a real decision with a real cost, so **fold it into the walkthrough as a decision for the
  operator**, with the three numbers and the one-variable flip to (c).

## 6. Docs — consolidate round 2 only, and only on a pass

`P10.S7` appended **eight** `## Doc impact` lines. Consolidate **those** into new doc versions with
`doc-new-version --source P10.REVIEW`. **Round 1's fifteen lines are already versioned** — the
notebook compresses them to a pointer saying so. Re-versioning them would be a real error.

Docs only, never source. Not in parallel mode, so consolidation happens here on a pass.

## 7. What you return

- `review_verdict`: `pass` | `changes_requested` | `blocked`, with numbered findings and proposed
  fix slices if not a pass. **A non-pass stops you before §6** — complete validation and judgment
  first so the orchestrator gets the whole picture in one cycle, then return without doing
  pass-only work.
- On a **pass**, a concrete **`walkthrough`**: the run command, the URLs, what to click, at which
  viewports, in the operator's runtime — plus the live decisions listed above. Write it for someone
  who has already been through one failed gate on this phase: say what is *new* since round 1 and
  what you are *not* asking them to re-test.
- `explain: not written — run /explain for this phase` — fixed pointer; explaining is separate.

**Do not** run `accept-gate`, `review-phase`, `finish-slice` or any commit. The orchestrator owns
every state transition. **Do not** perform the R17 card regroup.

## A standing bias for this review

Two rounds of this phase have now shipped work that *looked* right and was not — a filled counter
visible only in the variant the product uses, ghost ink `-trim` preserves, a dead button under the
launcher, and a signed 84px that left 8px of that button still covered. Every one was caught by
measuring in a browser rather than reading source. **Weight your effort accordingly.**
