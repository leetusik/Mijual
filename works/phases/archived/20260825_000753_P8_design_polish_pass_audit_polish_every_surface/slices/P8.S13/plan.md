# P8.S13 — Apply R13: 보유 종목 (/portfolio) + 알림 설정 (/portfolio/notifications)

Faithfully implement the **signed R13 round**. RESPECT THE DESIGN — never drop, simplify,
restyle, or "improve" a signed element. The contract is
`docs/reference/design/rounds/13-portfolio/output/build-prompt.md` (§0–§6); the geometry canon
is `output/portfolio/r13-portfolio.css` (copy declarations, do not re-derive); parts/strings
`output/portfolio/r13-parts.jsx` and the four cards. Context: `phase.md` §"R13 landed spec —
SIGNED OFF 2026-08-24" (binding decisions 1–8 + observations) and the SIGNOFF.md R13 entry.

## Files

- `frontend/components/portfolio/`: `Portfolio.module.css` (the bulk), `Deadlines.tsx`,
  `Holdings.tsx`, `NotificationsView.tsx`, `Portfolio.tsx`, `AddHolding.tsx`, `SharesInput.tsx`,
  `CarryOver.tsx`, `SampleBanner.tsx`, `copy.ts`
- `frontend/app/portfolio/notifications/page.tsx` (rail + h1 frame if the frame lives there)
- `docs/reference/design/grounding/copy-inventory.md` — R13 tail (2 revised strings, 0 new)

## Build order

1. **copy.ts (operator revision of R5 strings, 신규 0건):** `EMPTY_TITLE_KO` → 「보유 종목이
   비어 있습니다」, `SAMPLE_BANNER_KO` → 「샘플 보유 종목 — 구성 예시입니다. 종목·공시·마감은
   실제, 계정·보유량은 예시입니다.」 Update their docstrings (operator revision 2026-08-24, R13:
   reader surfaces never say 「포트폴리오」 — the layer name is 보유 종목). No other string
   changes; the notifications rail composes `← ` + `PORTFOLIO_LABEL_KO` (already 보유 종목).
2. **D-day rows (`Deadlines.tsx` + module css) — the slice's core.** Remove `.rowHead`'s
   `space-between`; one grid per row: `84px minmax(0,1fr) 212px 208px; gap:4px 16px`,
   `align-items:baseline` — chip col 1, 종목명 col 2, 지배 라벨 col 3, countdown col 4
   (`justify-self:end`). Past rows: inset chip + mono date on **one line** in col 4. Row bodies
   (① Conversion cell block, ② Dilution, ③ dependency sentence, lapse money) span
   `grid-column:2/-1`; the money line is its own grid `minmax(0,1fr) 208px` so the value's right
   edge equals the countdown edge. Anchor 「기준 {reference} (KST)」 rendered **once for the
   block**, outside/above the two sections (page-level; remove the per-section placement).
   No column headers, no vertical rules; section titles stay `//` eyebrows. Row padding/gap per
   canon (`.pdrow` 14px 20px, past row-gap tightened).
   **Q-B (session re-decision):** 「놓친 돈 상세 →」 renders **inside the money lead line**
   (after label + basis, `.pmlead` grammar) and **not when checked** (returns on uncheck); the
   control line keeps only the checkbox; lead line `min-height:32px` (44px ≤767) — verify a
   **measured 0px** shift on check/uncheck. Claim caption always renders. ①/② blocks keep using
   lookup's `Conversion`/`Dilution` (one composition — do not fork them; wrap for the column
   placement only).
3. **Holdings (`Holdings.tsx` + css):** row tracks `minmax(0,1.15fr) 132px minmax(0,1.5fr)
   152px` (header row kept, mono 10); rights cell its own tracks `52px minmax(0,1fr) auto`
   with countdown/date right-aligned to the cell edge; **empty rights cell = dashed hairline
   56px** (`aria-hidden`, no sentence/box/`—`); inline edit + horizontal action swap and the 8s
   undo inset row unchanged in behaviour, restyled per canon (`.pact` 32px bordered mono
   buttons, hover inset). **Q46 = (a): keep rendering the served `stock_code`** as the mono meta
   under the name (`.phmeta` tier) — the cards' omission was a data gap.
4. **알림 설정 (`NotificationsView.tsx` + page):** rail 「← 보유 종목」 (min-height 44px, mono,
   → `/portfolio`) as the 620px column's first row; `h2` → **`h1`** (one h1 on the page); row
   grid `104px minmax(0,1fr) auto`; error line = `authErrorKo` unchanged (body ink, no field
   border change); chips keep `aria-pressed` multiselect + empty-valid; KakaoTalk row: label +
   「예정」 chip + sentence, chip per `.pplanned` (the 「」 enclosure convention stays as today);
   **계정 삭제 sentence renders only while armed** (remove the permanent caption; render
   `.pnfoot` when armed, before the destructive second press); 로그아웃 · 계정 삭제 · 취소 all
   `.pact.wide` (104px min-width, centered). No behaviour changes to logout/delete flows.
5. **Sample mode (`Portfolio.tsx`):** unchanged behaviours (no 종목 추가, no holdings caption,
   caption 「본인 표시」, **no reset/종료 control** — do not add one); **render the R12
   `ConversionOffer` band after 지나간 마감** for the anonymous sample surface — reuse the
   existing `ConversionOffer` component **without its lead line** on this surface (the lead is
   false here; body + CTA + 닫기 only — make the lead optional via a prop rather than deleting
   R12's usage on /stocks), anonymous only, session-once (its own sessionStorage flag is fine to
   share or scope — keep the existing flag semantics), dismissible, never above the numbers.
6. **css cleanup:** delete both `@media (min-width:480px)` and `@media (max-width:480px)` blocks;
   everything mobile goes in one `@media (max-width:767px)` per canon (holdings card grammar,
   D-day two-column with right-edge alignment, notifications stack, 44px floors). Keep module
   widths at order-independent specificity where a shared class is involved (S9 lesson).
7. **copy-inventory.md** — R13 tail: 2 revised strings, 0 new, the two compositions, R5-4 종료
   withdrawal + R5 상시-sentence withdrawal notes.

## Don'ts

- No token changes; no new Korean beyond the two signed revisions; no browser date math; no
  anonymous writes; no modal/overlay/`position:fixed`; no changes to `lib/holding.ts`,
  lookup components' internals, event components, chrome/nav, or auth surfaces (except the
  optional-lead prop on `ConversionOffer`, which must leave the /stocks rendering identical).
  Do not add a sample reset. Do not touch the login page's 「실제 공시 4건」.

## Verification (operator runtime manifest — operations doc)

- Dev `http://127.0.0.1:3000` **and** tailnet origin; production build (scratch copy, `:3100`) —
  this slice deletes media queries and reshapes grids, so run it; widths 1440/1280/768/767/600/390.
- Run build-prompt **§6 items 1–13** and record each. Key measurements: (a) all rows of both
  sections share the same 4 edges at 1440; (b) money right edge == countdown right edge; (c) the
  ragged-left/empty-middle metrics are gone; (d) check/uncheck moves 0px (desktop + 390);
  (e) zero 480px media queries; (f) 「포트폴리오」 0건 in reader-visible text (grep rendered
  surfaces + copy modules); (g) delete-sentence renders only armed; (h) sample band appears after
  지나간 마감, dismiss leaves nothing, anonymous only.
- Account-mode states (edit/undo/carry/migrate/notifications) were not browser-walked in the
  round — verify them for real here: use a temporary account created through the product's own
  계정 만들기 and delete it afterwards (the S11 pattern); never touch the operator's session.
- `cd frontend && npm run typecheck` + smoke; `python -m pytest` untouched-backend sanity;
  `python3 scripts/workflow.py validate`.

## Notes & return

- Append durable notes to `phase.md` (§"P8.S13 — R13 applied"), new operator questions numbered
  after **Q46**, Doc impact one-liners (frontend/product/experience/qa/copy — incl. the R5
  withdrawals). Write `result.md` from scratch with per-file changes, §6 outcomes, measurements,
  browser evidence (origins/viewports/prod). No departures — escalate as a question instead of
  improvising. Return `done` only with §6 green in the operator runtime; never commit or
  transition state.
