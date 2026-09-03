# P12.DECOMP2 — cut the fix slices from the hunt's findings

`kind: decomposition`, `risk: high` → `slice-executor-high` (by kind). Bare folders only — never a
`plan.md` for another slice — and no product code. Written 2026-09-04 by the orchestrator in `auto`
mode, after `P12.R1` landed (`8519f45`).

## Read first

- `phase.md` whole. `## Decisions` carries the four root-cause families and the instrument seam;
  `## Notes for later slices` carries the ranked **F1–F14** tagged `for P12.DECOMP2`, the
  "refuted or clean" summary, DECOMP's "how to cut" note, and the `for P12.S2` release note;
  `## Operator Questions` carries **Q1–Q5**. Consume the `for P12.DECOMP2` notes when you finish
  (the finding detail stays in `slices/P12.R1/result.md` by path; each cut slice's `plan.md` will
  be written from there at its turn), and leave the `for P12.S2` note alone.
- `slices/P12.R1/result.md` where a finding's numbers, reproduction or control matter to the cut.
- The code each family touches, enough to judge slice boundaries and risk — not to fix anything.

## Two orchestrator rulings that change the cut (read before deciding anything)

The hunt filed F1 and F5 as "blocked on Q1 / Q2". I read the code and both have a remedy that
touches no signed design decision, so **both are cut in this pass**; Q1 and Q2 stay on the
`## Operator Questions` list and are routed at the review as questions the fixes already answered
(the walkthrough shows the operator the outcome). Record both rulings in `## Decisions`.

1. **F1, the account half — the P4.F10 route, applied to the chrome.** `app/layout.tsx` is already
   an `async` server component that awaits `getSiteContact(...)`; `lib/session.server.ts`
   `readAuthState()` forwards the request's own cookie, **never throws**, and **short-circuits with
   no request at all for a reader carrying no cookie**. `components/auth/DeadlineOffer.tsx`
   documents the reading this honours: 「neither state is shown before the session is known — it
   is simply known earlier, and by the half of the app that can know it first」. So the layout
   reads the session in `Promise.all` beside the contact, passes the initial `AuthState` through
   `SiteChrome` to seed the `useAccount` module store (`components/chrome/useAccount.ts`) before
   first render — server snapshot = the seeded value, `probedPath` marked answered for the initial
   path so the boot probe is skipped — and the 로그인 link or the account frame is **in the first
   painted HTML**. No 로그인 flashes at a signed-in reader (R5's rule holds, earlier), no empty
   slot, no skeleton. Everything downstream of `setAccountState` (로그아웃, 계정 삭제, 수신 주소
   변경) is unchanged. The event page passed a boolean to avoid serialising an email into a page
   with no use for it; the chrome *renders* the email, so the serialised `AuthState` is the point,
   and every page is request-time already (nothing is prerendered — `frontend` doc v0014).
2. **F1, the launcher half — in the first paint, still not rendered ≤767 after hydration.**
   `components/ask/AskSurface.tsx` returns `null` until `useDesktop()` (initial `false`, flipped in
   an effect) says ≥768, which is why the launcher pops in on every desktop load. The signed rule
   is 「≤767px: nothing — not hidden, not rendered」, argued from tab order and from "a launcher not
   painted would still open a widget". A `display: none` element is in no tab order and cannot be
   activated, so the fix keeps the rule's substance and removes the pop-in: render the launcher on
   the server (`useDesktop` initial `true`, or a `useSyncExternalStore` over the media query whose
   server snapshot is `true`), guard it with the `(max-width: 767px) { display: none }` media
   query for the pre-hydration window, and let the existing effect **unmount** it ≤767 after
   hydration exactly as today. No hydration mismatch (server and first client render agree), no
   visual change at any width, no new element.
3. **F5 — the P4.F5 route for IBM Plex Mono, which reverses no recorded decision.**
   `app/fonts.ts` gives `plexMono` `preload: false` for a stated reason (the critical font budget)
   and `fallback: ["ui-monospace","SFMono-Regular","SF Mono","Consolas","monospace"]` with no
   metric overrides. The remedy is the one `P4.F5` already applied to Noto: hand-declared
   `@font-face` fallback faces in `app/shell.css` (`local("SFMono-Regular")` / `local("Menlo")` on
   macOS, `local("Consolas")` on Windows) with **measured** `size-adjust` / `ascent-override` /
   `descent-override`, `adjustFontFallback: false`, and the fallback list pointing at them — zero
   network cost, `preload: false` untouched, `display: swap` untouched. Windows stays at
   `size-adjust: 100%` unless measurable, exactly as Noto's Malgun face does. Q2's *preload*
   alternative is **not** taken.

**Q3, Q4 and Q5 are product decisions and stay questions**: no slice for the board's re-rank
behaviour (Q3), none for the launcher hover scale (Q4), none for `scrollbar-gutter` (Q5 / F14 —
unverifiable here, so it would ship blind). **F13 gets no slice** (a deliberate destructive-action
confirm, 28 px, `hadRecentInput`-adjacent by nature). Say all four "no slice" verdicts in
`## Decisions` so the review does not read them as omissions.

## The cut I expect (adjust on evidence; keep the invariants at the end)

Orders `3.1`, `3.2`, … so `P12.S2` (order 8) stays last before `P12.REVIEW`. Every slice below
writes real code across files and verifies in a real browser, so every one is `--kind fix
--risk high`. Name each slice with the R1 finding ids it closes, so the review can map findings
to slices without reading plans (the slice ids `P12.F<n>` and the hunt's finding ids `F<n>` are
different namespaces — write "R1 F3" when you mean the finding).

| Order | Slice | Closes | What it is |
|---|---|---|---|
| 3.1 | `P12.F1` | R1 F1 (account half) | Chrome first paint I — the server seeds the account state through `layout.tsx` → `SiteChrome` → `useAccount` (ruling 1). Files: `app/layout.tsx`, `components/chrome/SiteChrome.tsx`, `components/chrome/useAccount.ts` (+ `Nav.tsx` only if the prop must pass through it). |
| 3.2 | `P12.F2` | R1 F1 (launcher half) | Chrome first paint II — the launcher rendered on the server with a ≤767 CSS guard and the existing post-hydration unmount (ruling 2). Files: `components/ask/AskSurface.tsx`, `useAsk.ts` (`useDesktop`), `Launcher.module.css`. |
| 3.3 | `P12.F3` | R1 F2, F6 | `/portfolio`'s two late bands — the signed-in 계정 이전 carry-over (215.28 px, CLS 0.061, the worst shift found) and the anonymous conversion offer (110–130 px, up to 2.2 s late). Same page, same family; the slice picks per band between "the server knows" (a cookie mirror of the client-only fact, or the session) and "reserve the box", and must leave the no-band resting layout pixel-identical. |
| 3.4 | `P12.F4` | R1 F3 | `/stocks/[corp_code]` revisit — the three holding cells inserted from `sessionStorage` after paint (CLS 0.048, identical in both runtimes). Same choice as above, made for the lookup chain row. |
| 3.5 | `P12.F5` | R1 F4 | The logout flash on `/auth/login` (56.6 px) — carry the flash through the redirect so the server renders the line (`/auth/login/page.tsx` is a server component), or reserve its height. |
| 3.6 | `P12.F6` | R1 F8, F10, F12 | Family B, one technique — the `Nav.module.css` ghost (`::after { content: attr(data-label); visibility: hidden; height: 0 }`) reserving the widest label: the ask composer's three-state send button (131 px input swing), the auth panel's 로그인 ↔ 계정 만들기 intro/rule/link (21.37 px), the 정정 이력 ↔ 접기 button (10.83 px). Three components, one CSS idea; if a plan at its turn finds it too wide to verify in one dispatch, the orchestrator splits it then. |
| 3.7 | `P12.F7` | R1 F9 | The feedback dialog's three heights and the ≤480 sheet's jumping top edge (75–91 px) — one body height across editing / sending / sent / failed, 닫기 kept mounted-but-disabled while sending. Family B + D, its own slice because it is a dialog with a state machine and a mobile variant. |
| 3.8 | `P12.F8` | R1 F7 | `/stocks?q=<miss>` — the no-match line collapsing on the first keystroke (30.6 px): keep its box while the field is re-typed. Family D. |
| 3.9 | `P12.F9` | R1 F5 | Family C — metric-matched local fallback faces for IBM Plex Mono (ruling 3): measure `size-adjust` for the macOS mono fallback(s) the way `P4.F5` did for Apple SD Gothic Neo, declare the faces in `app/shell.css`, point `plexMono`'s fallback list at them, prove the cold-cache mono reflow gone at the throttled mobile profile on the local production build, and prove warm rendering pixel-identical (`AE = 0`). |

**R1 F11 (the board's 갱신됨 chip, 52.55 px on a real refresh) is your judgment call**, and the
default is **no slice**: `components/landing/Board.tsx` sits under the P4.F7/F11 landing
constraint (the landing looks and moves exactly as today), the ghost technique would move the
freshness stamp 52 px left **in the resting state** (a visible change to a signed header), and a
real refresh only fires when `as_of` moves (twice-daily pipelines, never during the 78 s window
the hunt watched). Cut it only if reading `Board.tsx` / `Board.module.css` shows a mechanism that
leaves the resting layout byte-identical (the chip overlaying rather than pushing, for example);
otherwise record "no slice — Q3 carries it" in `## Decisions`.

Invariants whatever you adjust: one slice per **independent cause**, never one per page; every
slice `--kind fix --risk high` (nothing here is a one-line edit — `risk: low` would route it to
the `mid` tier); orders in `3.x`; `P12.S2` stays at 8; F13 and F14 uncut; no `co-work` slice;
bare folders only.

```
python3 scripts/workflow.py new-slice --phase P12 --slice P12.F1 --name "…" --kind fix --risk high --order 3.1 --depends-on P12.R1
…
```

## What every fix slice will be held to (write it once, in `phase.md`, so each plan can cite it)

Put one note tagged `**(from P12.DECOMP2, for P12.F1 … P12.F9)**` — a single shared note, not
nine copies — stating the bar every fix slice meets:

- **RESPECT THE DESIGN:** the resting layout of every affected surface is pixel-identical before
  and after in the state where the fixed element is absent, and the element itself renders exactly
  as today once present — the fix removes the *motion*, never restyles, drops, or "improves" the
  element. Screenshot `AE = 0` on the resting state is the proof, per the P4 precedent.
- **Measured before and after with the hunt's own instrument**, in Aside `--account u2`, in dev
  **and** the local production build (the recipe in `## Decisions`; S1's build at the scratchpad
  path is stale once any fix lands — rebuild in a fresh copy outside the repo), at 1280 and 390 —
  and at the throttled 412×915 cold-cache profile for anything font- or load-related. The
  measurement seam (`page._sendToTarget`, `observe(document)`, one `evaluate` argument, one route
  per invocation, the insertion-robust rect key, the landing's Cosmos noise floor) is in
  `## Decisions`; the finding's own numbers in `slices/P12.R1/result.md` are the "before".
- **A control for every zero**, as the hunt did.
- `npm run typecheck`, `npm run smoke`, a production build in a copy; **no test files**.
- Signed-in states through a throwaway account created and deleted through the product;
  production read-only; the dev stack left as found.
- Each slice appends its own `## Doc impact` line (`frontend` at least) and a
  `**(from P12.F<n>, for P12.S2)**` note only if the release needs to know something
  (a non-frontend file touched, a build-time env var, a font file added — otherwise nothing).

## Notebook (`phase.md`) when you finish

- `## Decisions`: the three rulings above (F1 ×2, F5) in your words with the file-level
  mechanism; the "no slice" verdicts (F13, F14, and F11 unless cut) with their reasons; the final
  cut as a table (slice → R1 findings → files) so the review can map findings to slices.
- `## Notes for later slices`: remove the `for P12.DECOMP2` notes (all of them, including the
  "refuted or clean" summary — it is in R1's `result.md`); add the one shared bar above; add
  nothing per slice beyond what a plan cannot get from `R1/result.md` by path.
- `## Operator Questions`: append nothing unless the cut raises a genuinely new question; do not
  edit Q1–Q5 (append-only), but the `## Decisions` lines say how Q1 and Q2 were resolved.
- `## Now` (≤ 15 lines): the cut, `P12.F1` next, the freeze date (2026-09-07 11:00 KST; production
  on `a74c58a`), and that nine fix slices plus the release must land before it or the release waits
  for 09-12.

`result.md`, verdict block first; `python3 scripts/workflow.py validate` passes; `next` will show
`P12.F1` once the orchestrator finishes this slice.

## Do not

- write or edit product code, any `plan.md`, or anything under `docs/`; commit; run any workflow
  state command other than `new-slice`;
- cut a `co-work` slice, an OG/Kakao slice, or a slice for F13 / F14 / the Q3–Q5 decisions;
- rate anything `low`.
