# Plan — P10.REVIEW · phase review (round 4)

`kind: review` · `risk: high` · **fourth pass.** Round 1 passed and the gate cleared into round 2;
round 2 passed and the operator ran a design session instead of clearing (R18); round 3 applied R18
and passed, and the operator **walked the gate and rejected it** — the wordmark's glyphs sat below
the nav links beside them. `P10.F3` is the answer to that. Your round-3 `result.md` is on disk;
**rewrite it for round 4**, keeping the earlier verdicts legible as history.

## What changed since your last pass — and it is one constant

`git diff` from round 3 is **`frontend/components/chrome/Wordmark.tsx`**: `INK_OFFSET_PX`
`{27: 7, 24: 6}` → `{27: 8, 24: 6}`, plus the doc comment that derives it. Nothing else in the
product moved. The operator superseded R17's `INK_OFFSET 0.2628·H` at their own gate — R18 had
explicitly re-confirmed that value, so this is a **supersession by the design authority**, not a
correction of a mistake, and it is recorded as such.

**Round 4 owes three `## Doc impact` entries.** Rounds 1 (10 versions), 2 (8) and 3 (4) are already
consolidated and **re-versioning them is a real error.**

The gate is **reset** (`requested_at=none`), still `required: true`.

## 0. Size the effort deliberately, and say where you spent it

One constant changed. A fourth exhaustive 56-page-view sweep would mostly re-prove what round 3
proved against an unchanged tree. So: **the adversarial attention goes to §2 and §3** — `P10.F3`'s
claim, and the question the operator actually asked with their eyes — and §4's product walk is a
**confirmatory** pass at reduced breadth.

**Reduce breadth explicitly, never silently.** Whatever you do not re-run, name it and say why; a
review that quietly covers less than it appears to is the failure mode this phase has now shipped
four times in another form. §1 and §4's checklist and functional sweep are **not** reducible — they
are the contract.

## 1. Validate the phase as a whole

Everything together, as in rounds 2 and 3: `npm run typecheck`, `npm run build`, `npm run smoke`,
`pytest`, `python3 scripts/workflow.py validate`, then the phase gates (`gates run` twice
byte-identical, `estimate report` twice, `scheduler --offline`, `extract recheck`,
`evalset refresh-recall`, the exposure invariant, the secret scan). Round 4 touched one frontend
constant, so none of them should have moved — which is exactly why you re-run them.

## 2. `P10.F3` — verify it, do not accept it

Its `result.md` is a report, not evidence. Four things carry the whole slice, and each can be wrong
in a way that puts the mark back where the operator rejected it.

1. **The chosen law's load-bearing fact.** F3 found the plan's premise — «Hangul carries essentially
   no descender» — **false for the rendered type**: it measured **1.02–1.16px** of ink below the
   alphabetic baseline at 13.5px, and therefore implemented "shared baseline" as *Hangul block bottom
   to Hangul block bottom*. If that measurement is wrong the adopted offset is wrong. **Re-measure it
   yourself, by your own method**, and say whether you reproduce it.
2. **Which face is actually rendering.** F3's prose names **Noto Sans KR**; this phase's docs
   describe the chrome's Korean as **Pretendard** (`/ops`'s mark is signed "Pretendard 600") and
   `P10.S7` shipped a self-hosted **Noto Sans KR** subset. Read the *computed* `font-family` and the
   face Chrome actually resolved for 「AI 질문」 in both runtimes. If the docs and the product
   disagree about the name of the face, **that is a durable-truth error of its own** — a finding, and
   a doc-impact entry, not a footnote.
3. **The number, independently.** Re-measure the band's ink bottom against the neighbouring Hangul's,
   your own way, dev **and** production, **1280 and 390**. F3 claims band bottom **31.00** vs labels
   **30.95–31.19**, footer `-6` at **+0.28px**, top clearance **4.00px**. And apply this phase's
   standing rule to your own check: **what input makes it report failure?** F3 says its check reports
   **5/5 FAIL, worst 1.0531**, when the mark is repainted at `-7`. Reproduce that negative control.
   A check that passes on the rejected placement has checked nothing.
4. **390 is where the shipped check abstains.** At ≤480 the links are hidden and the mark's only
   neighbour is the **메뉴** button; F3 reports it (**0.125px**, was 1.125) but deliberately does
   **not** judge it, because its two methods disagree there by 0.52px. So at the one viewport where
   the check is silent, **use your eyes**: screenshot the 390 bar at high zoom and say whether the
   mark and 메뉴 read as one line.

**And then stop measuring and look.** The operator's complaint was visual and a 0.5px tolerance is
not the same claim as *"it reads as one line."* Screenshot the nav and the footer at ≥8× at 1280,
and the nav at 390, and judge them as a reader. If the numbers pass and it still reads wrong, the
numbers are the thing that is wrong.

## 3. The finding `P10.F3` raised and did not decide

**The bar's own type is not on one line with itself.** `.utility`'s 「로그인」 is centred in the full
51px box while `.link` stretches with a 2px transparent bottom border, so its cell is centred in
49px — F3 measures the 로그인 ink bottom at **31.75** against the links' **31.13**. Pre-existing
since R2/R8, and untouched by this phase. But it is now load-bearing: F3 aligned the mark to the
**links**, which is the operator's own stated reference, so the mark sits **0.75px above** 로그인
where it used to sit 0.25px below.

Verify the measurement, then treat it as §5 requires — it is the phase's one **unrouted** operator
question and an unrouted entry blocks the pass.

## 4. The gate stages — `required: true`

**Open the running product yourself.** Do not pass on `P10.F3`'s report.

- **Runtime:** `docs/current/operations.md` § Operator Runtime. `make stack-up`, dev
  **`http://127.0.0.1:3010`**, **and the production build**. **1280** and **390**. `/ops` needs
  throwaway `MIJUAL_OPS_ID` / `MIJUAL_OPS_PASSWORD` as environment variables on the API process —
  **never open `.env`** — and **restore the stack afterwards**.
- **Instrument:** Aside if it runs here; it did not for any slice in this phase, and all of them
  drove real Chrome over CDP. Either is fine — **name what you actually used** and never claim a run
  you did not make.
- **Spot-check the phase's headline claims yourself**, rounds 1–3 included, at the breadth §0 lets
  you set: both document titles, no old name on any reader page, the 실권주 line, `/docs`, the live
  agent naming itself, the favicon `<link>`s in both runtimes, the retired binaries 404, 의견 보내기
  opening its panel, the mark reading **joined**, and F2's active tab not shoving its siblings.
- **The functional sweep — mandatory, not reducible.** Every visible control does something
  observable; interaction states including browser defaults; liveness over time; type into it and
  wait on anything implying live behaviour. Round 3 swept 119 controls with zero dead.
- **Walk it once with fresh eyes as a first-time user** — everything dead, confusing or annoying,
  explicitly **not** judged against the design record. Round 3 carried eight standing findings from
  round 2 (its `result.md` §6); say which still stand, and add what is new. These go into the
  walkthrough, **never** into silent fixes.
- **Re-run the whole cumulative `## Regression Checklist`** in the qa doc, append round 4's line, and
  **correct the one round 4 falsified** — 「세로 기하는 움직이지 않았다」 asserts
  `INK_OFFSET_PX = {27: 7, 24: 6}` and the 25.60 band centre, and is now wrong. F3's doc-impact note
  proposes the replacement; make sure whatever ships **can fail**.

## 5. Route every `## Operator Questions` entry

An unrouted entry blocks the pass. Round 3 routed and executed nine. Since then:

- **`.utility`'s 로그인 line (`P10.F3`) — UNROUTED, and it is new.** Fold it into the walkthrough
  with F3's numbers and yours (bring `.utility` onto the links' line, or leave it), **or** file it
  with `defer-job` — list it for the orchestrator either way. Note honestly that the mark's new
  position made a pre-existing 0.6px discrepancy visible rather than creating it.
- **The landing board's tab strip** — a third instance of the shove defect, measured **0px at 1280**
  and **0.42px on `CB` at 390**, deliberately not fixed. Round 3 routed it **to the gate
  walkthrough** and the operator did not answer it (they reported the wordmark instead). It is still
  open: carry it forward, unchanged.
- **Korean coverage** — still open, unchanged: (a) 94,604 B / **(b) 291,072 B adopted** / (c)
  1,022,828 B; `HANGUL_COVERAGE=full` flips it. Carry it into the walkthrough verbatim.

## 6. Docs — consolidate round 4 only, and only on a pass

Round 4's **three** `## Doc impact` entries → `doc-new-version --source P10.REVIEW`. They name
`frontend.md`, `qa.md` and `decisions.md`, and F3 wrote the proposed wording out in
`slices/P10.F3/result.md` §7 — use it as input, not as a transcript; you are the one who verified it.
If §2.2 turns up the font-face naming error, that is a fourth entry and it is yours to add.

**Rounds 1, 2 and 3 are already versioned** — re-versioning them is a real error. Docs only, never
source. Not in parallel mode, so consolidation happens here.

## 7. What you return

- `review_verdict`: `pass` | `changes_requested` | `blocked`, with numbered findings and proposed fix
  slices if not a pass. **A non-pass stops you before §6** — complete validation and judgment first,
  so the orchestrator gets the whole picture in one cycle.
- On a **pass**, a concrete **`walkthrough`** — the run command, URLs, what to click, at which
  viewports. This is the operator's **fourth** gate on one phase; write it accordingly. **Lead with
  the thing they rejected** — the wordmark beside the nav links, at 1280 and at 390 — and say plainly
  what you are *not* asking them to re-test. It must also carry:
  1. the **로그인 line** decision, if you routed it to the walkthrough rather than to a job — and be
     honest that aligning to the links is what exposed it;
  2. the **Korean-coverage** decision, all three numbers;
  3. the **landing board** decision, still unanswered from round 3;
  4. **look at the real browser tab, light and dark** — no process on this machine can photograph the
     OS tab strip (no Screen Recording permission), so the favicon rests on served bytes plus a 16
     CSS px paint. It is the one claim in the phase resting on inference rather than sight, and it
     has now been carried unanswered through two gates. Say that plainly.
- `explain: not written — run /explain for this phase` — fixed pointer.

**Do not** run `accept-gate`, `review-phase`, `finish-slice`, or any commit; the orchestrator owns
every transition. **Do not** perform the R17/R18 card regroup — it waits for the gate to clear.

## A standing bias for this review

Four defects in this phase were **checks that could not fail** — a guard over an all-white image, an
aspect nobody divided, a pixel read from transparent canvas, an unscoped copy of a scoped check. The
fifth was different in kind and is the one that reached the operator: **R17's alignment check
verified the mark against the wrong reference.** It could fail, and it passed, because it was
measuring the wrong thing. So ask both questions of everything you verify: *what input would make
this report failure* — and *is it pointed at what the operator is actually looking at?*
