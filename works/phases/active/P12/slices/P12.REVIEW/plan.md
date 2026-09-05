# P12.REVIEW — review of P12 "Flicker polish" (gated: `acceptance.required: true`, never opened) — dispatch 1

You are `slice-executor-high` executing the phase review. The contract is
`.claude/skills/review-phase/SKILL.md` — read it first and follow it to the letter; this plan adds
the P12-specific facts, order, budgets and hard rules. You are not the last word: on a `pass` you
return a **`walkthrough`** and the orchestrator opens the operator acceptance gate. You never run
`accept-gate`, `defer-job`, `review-phase`, `docs-consolidated`, `git commit` or `git push`.
Written 2026-09-04 by the orchestrator in `auto` mode, after `P12.S2` (`004d936`).

## What P12 set out to do (judge against this)

`works/phases/active/P12/intent.md`, confirmed 2026-09-04: (1) the signed-in account dropdown's
caret width jump fixed as a plain `fix` slice, **respecting the R8-signed frame + caret + hover**;
(2) **hunt and fix every other visible flicker** across every user-facing page (`/`, `/stocks`,
`/stocks/[corp_code]`, `/portfolio`, `/portfolio/notifications`, `/ask`, `/events/[rcept_no]`,
`/auth/login`, `/auth/reset`, the shared chrome), desktop and mobile, in the operator's dev runtime
**and** the production build. No OG-image / Kakao work, no design round, sequential. `/ops/*` is
out of scope. The operator's words: 「skip the design round, fix it directly in the phase」 — so
**RESPECT THE DESIGN** bounds every fix: resting layouts pixel-identical, motion removed, nothing
restyled.

Fifteen slices are `done`: `P12.DECOMP`, `P12.S1`, `P12.R1`, `P12.DECOMP2`, `P12.F1`, `P12.F2`,
`P12.F3`, `P12.F4`, `P12.F10`, `P12.F5`, `P12.F6`, `P12.F7`, `P12.F8`, `P12.F9`, `P12.S2`. R1 found
**14 findings (F1–F14)** in four root-cause families; DECOMP2 cut nine fix slices and recorded four
no-slice verdicts (R1 F11/Q3, F13, F14/Q5, Q4); F3 found one more (cut as `P12.F10`); F6 and F7
turned three Family-B findings (R1 F8, F10, and F9's send button) into **Q7, Q8, Q9** because every
fix changed a signed resting layout. Production runs `origin/main` = **`004d936`** (released by
`P12.S2` 2026-09-04 15:13 KST; rollback point `mijual-web:previous` = `a9195a0c0689`, the `a74c58a` image). Today is 2026-09-04 (KST). The deploy freeze
opens **2026-09-07 11:00 KST**.

## Read (in this order, just in time)

1. `CLAUDE.md`; `.claude/skills/review-phase/SKILL.md`.
2. `python3 scripts/workflow.py next`; `works/phases/active/P12/phase.json` (`acceptance.required:
   true`, never opened).
3. `works/phases/active/P12/intent.md`; `works/phases/active/P12/phase.md` **whole**: `## Decisions`
   (one line per landed fix with its numbers; the seam contract; the instrument seam with every
   trap F3–F9 added; the F6 precondition ruling; the four no-slice verdicts; the runtime and
   freeze lines), `## Doc impact` (append-only, **19 lines** — 11 `frontend`, 5 `qa`, 2 `security`, 1
   `operations`; **this is the list you verify**), `## Operator Questions` (**Q1–Q9**), `## Notes for later slices` (the
   shared bar; F1's measurement seams; **the three notes tagged `for P12.REVIEW`** — F4's 놓친 돈
   revisit shift, F10's two sample residuals, S2's release facts + F4 residual — written for you), `## Now`.
4. Every slice's `slice.json` and `result.md`, **head-first** (verdict block), whole where the detail
   matters. `P12.R1/result.md` is the hunt's method and inventory; the R1-era finding list with
   numbers is in git (`git show 8519f45:works/phases/active/P12/phase.md`, the `for P12.DECOMP2`
   notes) — DECOMP2 consumed it, so read it there when you need a "before".
5. `docs/current/operations.md` `## Operator Runtime` (**v0014** — see *Runtime* below: it is stale
   on the instrument and current on everything else); `docs/current/qa.md` `## Regression Checklist`
   (**146 `- [ ]` lines** through the P4 production block) — read it whole, you re-run all of it.
   Other `docs/current/` sections **only** where a `## Doc impact` line names them, and only to
   judge; every doc P12 touched is behind the code **by design** (the docs-phase deferral).

## Hard rules (all of them, no exceptions)

- **Production no-harm and read-only.** You may **read** production: HTTPS GETs against
  `https://jujutower.com`, browser loads, `ssh oracle-cloud` for read-only inspection (`docker
  compose -f compose.prod.yml ps/logs`, `docker inspect`, `git rev-parse`), and at most **one**
  `POST /api/ask` turn (one model call). You may **not**: deploy, rebuild, restart or stop any
  container; touch `edge-nginx` (baseline `StartedAt 2026-07-02T19:22:12.325478595Z` — assert,
  never change); edit anything under `/home/opc`; **create an account, log in, send feedback (it
  forwards to vocky — a write), or write anything on production**. Signed-in states are exercised
  **on dev only**, with a throwaway account created and deleted through the product (계정 삭제 on
  `/portfolio/notifications`). If the harness denies anything, record it and do not work around it.
- **Deploy freeze** 2026-09-07 11:00 → 09-11 23:59 KST. Nothing in this slice deploys. A fix slice
  you propose that changes product code must say whether it needs a deploy before 09-07 11:00 KST
  or waits for 09-12.
- **Secrets.** Never print, quote or store a secret value (`.env.prod`, the `/ops` credential, any
  token). The repo `leetusik/Mijual` is **public**: `result.md`, `phase.md`, the walkthrough and the
  doc sections are published the moment they are committed.
- **Browser instrument: Aside on the agent account `u2` (profile 「claude2」)** — every invocation
  `aside repl --account u2 "<js>"`; **never `u0`** (the operator's Google account), never `aside
  account use`, never `aside profile list` (hangs the shell). The measurement seam and its traps are
  in `## Decisions` (CDP via `page._sendToTarget`; init scripts before `goto` with the observer on
  `document`; one `evaluate` argument; ~80 s per invocation, one route per invocation; tabs die
  between invocations, cookies persist; scripts are modules — end with `console.log`, never a
  top-level `return`; no `page.waitForTimeout`; screenshots resolve inside the session dir; **one
  `page.screenshot()` per invocation, never `{fullPage: true}` under an emulated viewport, exclude
  the scrollbar strip, mask the landing's star field; `page.console.logs()` captures nothing — use
  the `Page.addScriptToEvaluateOnNewDocument` shim proven live with an injected `console.error`;
  a DPR-2 tile does not fit the capture window — DPR 1 at 390 for `AE` work; a rect key indexes
  visible elements only; treat CLS as corroboration and rects as evidence; a control for every
  zero**). Viewports **1280** and **390**, plus **412×915 @ DPR 2.625 / 4× CPU / ≈1.6 Mbps /
  150 ms** for the cold-cache lines, plus any width a checklist line names. Say in `result.md` which
  instrument you used; never report a walk you did not make. Chrome-over-CDP on a throwaway profile
  is the fallback **only** if Aside is genuinely unavailable — say so if you fall back.
- **Model-call budget.** Checklist lines on the AI 질문 surface need real turns. Cap: **6** turns on
  the dev stack, **1** on production. Prefer the cheap greeting / 범위 밖 lines; reuse one answered
  thread. State the count spent.
- **No source code edits, no fixes, no `docs/current` hand-edits, no `docs/versions` patches.** The
  only files you write: `result.md`, `phase.md`, and — on a pass only — the named sections via
  `doc-new-version`. Notebook-only findings are the one thing you may close yourself (Stage B).
- **`uv` discipline.** `uv run pytest`, `python3 scripts/…`; never `uv run --with …`.
- Leave the machine as you found it: the operator's dev stack **up** (`make stack-status` as found),
  every server you started stopped (pids recorded), no stray build copies serving.

## Runtime: three environments, and what runs where

| environment | how | what runs there |
|---|---|---|
| **dev** | the operator's stack: `make stack-up` → API `127.0.0.1:8010` + `next dev` on `127.0.0.1:3010` (StrictMode). Confirm it is serving the current tree (`curl -s 127.0.0.1:3010/` returns 200 and the served HTML carries the head mirror script). | every checklist line; every **signed-in** line (throwaway account); the per-fix reproductions that need storage seeded on this origin (storage is port-scoped — F1's note). |
| **production build** on **3014** | a **copy** of `frontend/` outside the repo (never build into `frontend/.next`), `NEXT_PUBLIC_SITE_URL=https://jujutower.com MIJUAL_API_ORIGIN=http://127.0.0.1:8010 npm run build`, stage `.next/static` + `public/` into `.next/standalone/`, `node .next/standalone/server.js`, against the dev API. | the lines where dev and production could differ (hydration, StrictMode double effects, first paint timing); the `AE` comparisons against production. |
| **production** `https://jujutower.com` (`004d936`) | read-only, one model call max, no account, no login, no feedback send. | every anonymous/read-only line + this phase's headline claims (Stage C). Account-bound lines → **operator-only walkthrough items**, never silently skipped. |

`## Operator Runtime` v0014 is **present and filled** → no `needs_operator` halt. It is stale on
exactly one point — it still says Aside's daemon does not run here and prescribes Chrome over CDP;
since 2026-09-03 evening the operator's instruction is 「use claude 2 in aside browser for qa」 and
every P12 slice ran Aside `--account u2` (the P4 review's third dispatch recorded the account; the
qa doc's P11 block already records Aside installed). Everything else in the manifest stands.

## Stage A — validate all slices together

Re-run each slice's validation from its verdict block (`plan.md` as fallback), collapsed into one
run of each; record every command and its outcome in `result.md`:

- `uv run pytest -q` → **167** (unchanged by P12 — the phase touched `frontend/` only; confirm
  `git diff --stat a74c58a..004d936 -- src deploy compose.prod.yml` is empty). `uv lock --check`.
- `cd <frontend copy> && npm run build && npm run typecheck && npm run smoke` green (22/22); the
  build needs `NEXT_PUBLIC_SITE_URL`. **Grep the built CSS**: the three `plexMono Fallback`
  families present with F9's numbers (Menlo `size-adjust: 99.66%`, `ascent-override: 102.85%`,
  `descent-override: 27.59%`), the `unicode-range` on the two matched ones, and the **generated**
  `font-family:plexMono Fallback;src:local(Arial);…size-adjust:131.49%` face **gone from the front
  of the stack** — `local(Arial)` and `131.49%` still appear exactly **once**, as the third family
  `plexMono Fallback Arial` that F9 re-declares verbatim *behind* the matched ones so the ← / →
  arrows do not change at rest (S2's correction of its own plan's wording); the `notoSansKr
  Fallback` faces still there (P4.F5 holds).
- `make smoke-prod` → **17/17** (a red `www` line from this Mac is MagicDNS — re-check with
  `--resolve`, count as a known local false FAIL; any other red line is a finding).
- `python3 scripts/workflow.py validate` (the `consolidation_owed=P4`, `stale_docs=product` and
  `oversized_doc_sections` warnings are pre-existing).
- On the box (read-only): six services up + `mijual-schema` exited 0; `edge-nginx` `StartedAt`
  unchanged; `/home/opc/Mijual` at `004d936`; `mijual-web:previous` is the `a74c58a` image
  (`P12.S2`'s image table — cite it, re-read the tags).
- **Each fix's headline number, re-measured once by you** (dev or the production build, whichever
  the slice measured — say which), with its control: S1 the frame `[914.72, 9.5, 261.28, 32]` in
  both states (signed in, dev); F1 the account slot in the served HTML of `/` and no post-paint
  insert; F2 the launcher in the first paint at 1280 and **absent from the DOM** ≤767 after
  hydration; F3 the carry-over slot (signed in, sample seeded) and the offer band (anonymous)
  moving 0 px; F4 `/stocks/00547510` with a remembered holding, 0 px; F10 an edited sample's removed
  row never painting; F5 the logout landing, form 0 px; F6 the 정정 이력 button one rect; F7 the
  feedback dialog one rect editing → sending → sent (dev — a send lands in vocky's project through
  the dev API, R1/F7 did the same; **not on production**); F8 the search-miss keystroke, 0 moved;
  F9 the cold-cache mono delta ≤ 0.1 px on `/stocks/00547510`. Cite each slice's tables beside
  yours; where your reading disagrees, that is a finding.

## Stage B — judgment, cross-check, doc-impact coverage

- Did every slice meet its brief and plan? Are deviations explained in each `result.md`? Judge in
  particular: **R1**'s method (the false clean zero it caught, the Latin-label control for H9, the
  instrument artefact for Space); **DECOMP2**'s three rulings and four no-slice verdicts (are they
  argued from the code, and do they hold?); **F1**'s `cache()` memoisation of `readAuthState` and
  the module store never written on the server; **F2**'s CSS guard versus the signed 「not rendered」
  rule; **F3**'s pre-hydration mirror seam (is the header contract in `PreHydration.tsx` complete
  for all five attributes? does every user release its stamp? is 「Anonymous state never reaches the
  server」 intact — grep the seam and the fixes for any cookie/query/header mirror); **F4**'s desktop
  column pinning; **F10**'s per-section rule and first-visible-row border; **F5**'s
  `flashResolved` release (the stamp-set-but-key-gone case); **F6**'s precondition ruling and the
  two questions it raised instead of fixes (is the ruling consistent with DECOMP2's F11 verdict? —
  say so either way); **F7**'s runtime pin (is a JS-measured `min-height` acceptable where the rest
  of the phase reserved from CSS? the failed body's growth; 닫기's measured unmount); **F8**'s
  `visibility: hidden` and the AX-tree proof; **F9**'s three-family shape with `unicode-range` (the
  ← / → arrows painting in Arial at rest — was preserving that right under RESPECT THE DESIGN, and is
  the generated face re-declared verbatim?), the Menlo-only macOS family (SF Mono unreachable
  through `local()`), Windows unclosed at 100 %; **S2**'s release (timed against the pipeline
  windows, the assertions identical, the production proofs).
- **Cross-check the notebook against the logs**: a decision or constraint recorded in any
  `result.md` that appears nowhere in `phase.md` is a finding; so is a durable-truth change a log
  describes with no `## Doc impact` line. Candidates to check explicitly: the seam's attribute
  contract and `clearMirror`'s `data-mj-` prefix (frontend); the security line (security — one for
  F3; does F10/F5 need its own, or does F3's cover the principle?); the instrument traps (qa — F6,
  F7, F9 each wrote one; do they overlap or contradict?); F6's precondition (frontend); F7's pin;
  F9's numbers and the `unicode-range` shape (frontend); the release (operations + qa from S2); the
  `## Operator Runtime` staleness (P4 owes that note — confirm it is on P4's list, not silently
  missing everywhere); `useDesktop(initial)`'s new signature; `lib/session.server.ts` `cache()`;
  the caret's `transform-origin`; the load-sweep numbers as the new baseline (qa).
- **Notebook-only findings you close yourself** (append to `phase.md`, tag `(P12.REVIEW)`, report
  as closed). Product/code/deploy findings become numbered findings with a proposed fix slice
  (`P12.F11`, …) and `changes_requested`.
- Orphaned design routes: none expected (no design round) — confirm (`app/**/mock*`).
- **The nine `## Operator Questions` + the three review notes** — build the routing table (Stage D
  consumes it): each entry is **walkthrough decision** / **deferred job (title / reason / trigger)** /
  **answered — nothing outstanding**. Nothing is filed yet for P12 (the last deferred id is **D46**;
  new ones are yours to list, the orchestrator files them). Starting points, yours to confirm from
  the product: **Q1** and **Q2** are answered by F1 and F9 (a one-line confirmation each at the
  gate); **Q3** (board re-rank + the 갱신됨 chip, R1 F11) — a product decision, walkthrough;
  **Q4** (launcher hover scale) — walkthrough, one line; **Q5** (`scrollbar-gutter`, unverifiable
  here) — deferred job candidate, trigger: a Windows/Linux reader or "always show scroll bars";
  **Q6** (widget close leaves focus on `<body>`, pre-existing) — walkthrough or deferred; **Q7 + Q9**
  — one decision (may a send button's resting box be as wide as its widest label?), walkthrough;
  **Q8** (auth panel intro reservation) — walkthrough; **F4's 놓친 돈 revisit shift** (52 px, CLS
  0.01006, identical on HEAD) — deferred job candidate (a fix like F10) or a decision to accept;
  **F10's two residuals** (the ≤767 override re-wrap identical on HEAD; the all-issuers-removed
  panel swap 33.5 → 106.44 px, HEAD worse) — deferred or accept; **S2's F4 residual** (inside the
  ① 환산 row's reserved box the cells settle into their final columns one frame after the first
  sampled frame on production — no `layout-shift` entry at 1280; read the note for the 390 half)
  — judge it yourself on production: a one-frame paint-boundary settle inside a reserved box, or a
  visible flicker; route accordingly.

## Stage C — gate stages 1–4 (the phase is gated)

1. **Manifest** — present and filled (stale on the instrument only; not a halt). No `needs_operator`.
2. **Spot-check the headline claims yourself on `https://jujutower.com`** (`004d936`), 1280 and
   390, anonymous: `/` — the 로그인 link and the AI 질문 launcher in the **first painted HTML** with
   no post-paint pop-in (R1's production numbers as the before: pop-ins 3–165 ms after FCP), CLS 0
   with the star field filtered; `/stocks?q=zzz` + one keystroke — nothing below moves;
   `/stocks/00547510` with `sessionStorage["mijual.lookup.holdings"]` seeded for that code — the
   with-holding row from the first frame; `/portfolio` with `mijual.portfolio.sample` carrying one
   removed code — the row never paints, and the 전환 제안 band is in the served HTML; the head mirror
   script in `<head>` of every route; `/events/20260806000329` — the 정정 이력 button one rect across
   the toggle; the feedback dialog from the footer at 1280 and 390 — **editing state only** (no
   send); a **cold-cache mobile load** at the throttled profile of `/stocks/00547510` — the mono
   numerals do not move when Plex lands (say what you saw; F9's and S2's tables carry the decimals);
   the served CSS: the three mono fallback families, the `.flashSlot` rule, the twin, `.noMatchStale`;
   the caret: the 로그인 link only (anonymous) — the signed-in frame is a dev check (Stage A). One
   `/api/ask` turn on production is allowed — spend it on the P11 checklist lines that need
   production, not here.
3. **Fresh-eyes walkthrough** as a first-time Korean reader on production at both viewports: land →
   search a company → open an event → toggle 정정 이력 → read a `[근거]` → try the sample portfolio
   (remove an issuer, reload) → open the feedback dialog and close it → `/ask` one question (the one
   production model call — combine with Stage 4) → the login page (do not submit) → 404. Report
   everything dead, confusing or annoying, **not** judged against the design record. These go into
   the walkthrough as decisions, never into fixes. Watch especially for anything this phase's
   reservations left visible: a blank box where a sentence was (F8), a taller sent panel (F7), a
   reserved gap that never fills.
4. **Re-run the whole `## Regression Checklist`** — all **146** lines, per *Runtime* above; results as
   a table in `result.md` (line → dev / prod-build / production, one-word result, a note where not a
   clean pass; a line whose precondition no longer exists is recorded as such with what you checked
   instead). Account-bound lines run on dev with the throwaway account; production-only lines on
   production. Then compose the **P12 block** to append, in the shipped shape
   `- [ ] <surface>: <one observable>`, one line per fix at most (the caret frame one width; the
   chrome in the first paint; the mirror seam's four uses moving 0 px with the attribute names; the
   정정 이력 button one width; the feedback dialog one height; the search-miss box; the cold-cache mono
   swap ≤ 0.1 px; the load sweep's no-pop-in line) plus the instrument note the P4 block's shape
   uses — with the counts and the runtime you ran them in.

## Stage D — route every operator question; build the walkthrough

Every one of the nine questions and the three review notes lands in exactly one of: walkthrough
decision / deferred job (title · reason · trigger — the orchestrator files it) / answered. Write the
routing table into `result.md`. Then write the **walkthrough** — the script the operator runs.
Constraints: English prose, Korean product strings verbatim; **≤ ~80 lines**; no secret values;
numbered so the operator can reply "1 ok, 3c change X". Shape:

0. **Already verified by the reviewer today** — one paragraph: what you measured on production and
   dev, with the headline numbers (pop-ins gone, 0 px per fix, cold mono ≤ 0.1 px, `make smoke-prod`
   17/17, the box's assertions unchanged).
1. **Open it and look (≈10 min)** — per fix, what to open and what to watch, at desktop and on a
   phone: `/` (nothing pops in at the top right or bottom right), `/stocks?q=zzz` then type, 툴젠
   `00547510` with a 보유량 entered then revisit, `/portfolio?sample=1` remove one then reload,
   `/events/20260806000329` 정정 이력, the footer's 의견 보내기 (open, type, **send if they wish** — it
   lands in vocky), `/auth/login` → 계정 만들기 → back (the panel re-flows once — Q8), `/ask` a
   question and watch the composer (Q7); optional DevTools slow-4G reload of 툴젠 at a phone width to
   see the numerals not move when the mono font lands.
2. **Operator-only checks** — the signed-in flows an agent may not run on production: sign in (their
   account) and confirm the account frame is in the first paint with no 로그인 flash (F1) and the
   caret flips without the frame changing width (S1); visit `/portfolio?sample=1`, edit, then sign
   in → the 계정 이전 band does not push the page down (F3); 로그아웃 from the menu → 「로그아웃되었습니다」
   above the form with the form not moving (F5); the 계정 삭제 confirm (R1 F13, accepted as is).
3. **Decisions, to take literally** — Q3 through Q9 and the residuals, each one line: what it is,
   where the exact numbers are (`phase.md` § `## Operator Questions`), accept / change; Q7 + Q9 as
   one line; Q1 and Q2 as confirmations of what shipped.
4. **Deferred jobs** — the new ones the orchestrator will file (title · reason · trigger), so the
   operator sees them here too.
5. **How to clear**: `python3 scripts/workflow.py accept-gate P12 --clear --note "..."`, or report
   failures in the reply.

Put the walkthrough in `result.md` under a heading that is **exactly** `## Walkthrough`, followed by
a blank line, ending at the next `## ` heading (the orchestrator extracts it mechanically for
`accept-gate --open --walkthrough`). Also return it in the structured verdict.

## Pass-only writes (only after the verdict is settled as `pass`)

(a) Verify the `## Doc impact` list covers every durable-truth change (Stage B), and report
`doc_versions: none — deferred to a docs phase` for consolidation.
(b) The named sections, each through the engine and nothing else in those docs:
- `python3 scripts/workflow.py doc-new-version --doc qa --summary "P12: the flicker-polish regression block" --source P12.REVIEW`
  → edit **only** `## Regression Checklist` in the returned `edit_path`: append the P12 block
  (Stage C-4) after the P4 production block; nothing else in the section changes.
- `## Operator Runtime` in `operations` **v0014** is stale on the instrument. **Correct it through
  the carve-out** — `doc-new-version --doc operations --summary "P12: Operator Runtime — Aside on the agent account u2 is the instrument" --source P12.REVIEW`,
  editing **only** that section's instrument paragraph (Aside `--account u2`, profile 「claude2」,
  `aside repl` over Bash, never `u0`, the seam pointer to the qa doc; Chrome-over-CDP demoted to the
  fallback when Aside is genuinely unavailable) — unless you judge the stale paragraph better left
  for the docs phase that consolidates P4's owed note; say which you did and why.
- `python3 scripts/workflow.py rebuild-docs`, then `python3 scripts/workflow.py validate`.
On `changes_requested` or `blocked`: **none of (a)/(b)** — stop and hand back.

## `phase.md` duties (every verdict)

Edit the notebook under its budget: consume (drop) the `## Notes for later slices` blocks tagged
`for P12.REVIEW` and the `for P12.F1 … F9` / `for P12.S2` notes whose content now lives in the
walkthrough or `result.md`; keep any note a docs phase will still need and retag it `for the docs
phase`; append your Doc impact / Operator Questions lines only if you add any; never touch the
generated `## Slices` block; rewrite `## Now` (≤ 15 lines) as the handoff: the verdict, the gate
state the orchestrator is about to open, the operator's next action, the freeze date, the
docs-phase debt (P12's Doc impact list joins P4's).

## Return

The structured verdict block, `result.md` first (verdict block at the head, then: validation table,
the per-line regression table, findings numbered, the routing table, `## Walkthrough`, deviations,
instrument used, model calls spent, dev-DB / vocky rows created, machine state left).
`explain: not written — run /explain for this phase` on every verdict.

- `pass` → `walkthrough` filled; deferred jobs to file listed (title/reason/trigger) in the return
  **and** in `result.md`.
- `changes_requested` → numbered findings + proposed fix slices (`P12.F11`…), no pass-only step run,
  and say which findings force a deploy before the freeze.
- `blocked` → the blocker and the input needed. Do **not** use `blocked` for running out of room.

**Partial-return protocol.** If you cannot finish in this context, stop at a clean boundary: write
`result.md` with a `## Progress` section (what is validated with results, what remains, the exact
next step, the machine state you left — servers up, account existing) and return `status: done`
with `review_verdict: n/a — partial, resume at <stage/step>`. The orchestrator re-dispatches you
from `## Progress`; the final dispatch rewrites the verdict block. Never form a verdict from a
partial picture.
