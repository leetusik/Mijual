# P8.S13 — R13 applied: 보유 종목 (`/portfolio`, 계정 · 샘플) + 알림 설정 (`/portfolio/notifications`)

The signed R13 round is built. Twelve files changed, none added, none deleted. The D-day list is a
different object from the one R5 left: five rows across two sections that share **one** set of four
edges, a 소멸 금액 whose right edge is the countdown's right edge, one anchor line for the page, and
a 「놓친 돈 상세 →」 that leaves and returns on a check without moving anything by a single pixel.
알림 설정 has a frame for the first time — a rail, an `h1`, three actions in one column — and 계정
삭제 no longer explains itself to readers who never asked.

Everything below was **measured in the operator's runtime**, not inferred: `make stack-up` /
`next dev` at **`http://127.0.0.1:3000`** and at the tailnet origin **`http://100.77.164.42:3000`**,
and again against a **production build** (`next build && next start`) served from a scratch copy on
**`:3100`**, at 1440 / 1280 / 768 / 767 / 600 / 390. The browser is the operator's own Chrome
(151.0.7922.174) driven headless over CDP from an isolated profile — same Blink, same CSS engine,
scriptable measurement; every number in this file is a `getBoundingClientRect()` or a
`getComputedStyle()` from that browser.

**No departures from the design record.** Three deltas between the record and what the product now
renders are catalogued as **Q47–Q49** in `phase.md` rather than resolved here.

---

## 1. What changed, file by file

**`frontend/components/portfolio/copy.ts`** — the round's **two** operator revisions and nothing
else: `EMPTY_TITLE_KO` → 「보유 종목이 비어 있습니다」, `SAMPLE_BANNER_KO` → 「샘플 보유 종목 — …」
(§4b: 독자 표면에서 「포트폴리오」를 쓰지 않는다). Their docstrings now carry the revision and its
date. Two more docstrings record decisions that changed a *placement*, not a string:
`MISSED_DETAIL_KO` (Q-B — inside the money line, absent on a checked row) and
`DELETE_ACCOUNT_NOTE_KO` (armed-only, withdrawing R5's 상시 clause). The re-export block now brings
in **`HOLDINGS_LABEL_KO`** instead of `PORTFOLIO_LABEL_KO` — see §5.

**`frontend/components/portfolio/Portfolio.module.css`** — rewritten from the round's geometry canon
(`output/portfolio/r13-portfolio.css`), declaration by declaration, onto this module's class names.
R5's **two** 480px blocks are gone; the file now has **exactly one** media query and it is
`max-width: 767px`. New: `.holdingStock` / `.holdingEdit` / `.holdingInput` / `.holdingDDay` /
`.rightsSlot` / `.rowChip` / `.rowLabel` / `.rowBody` / `.lapsedValue` / `.claimCaption` /
`.deadlines` / `.notifyColumn` / `.rail` / `.crumb` / `.notifyFoot` / `.actionPrimary` / `.wide` /
`.narrow`, plus focus-visible rules for every control. Retired with their elements: `.rowHead` /
`.rowIdentity` / `.rowWhen`'s flex form, `.addTitle`, `.chipOn`, `.holdings`'s top rule, the
`--holding-actions` custom property. `.page` gains `word-break: keep-all` (R13 §0; `P8.S11` note 4's
per-surface rule — the module declared none and this product has none globally).

**`frontend/components/portfolio/Deadlines.tsx`** — the slice's core. `.rowHead` is gone: the row is
one grid, the anchor is rendered once for the block outside both sections, the chip is `compact` (the
84px track is sized for 유증 / CB / 매수청구), the past chip and date are one line, the row bodies are
wrapped in `.rowBody` for their column placement, and `LapsedMoney` is re-cut into the canon's three
grid children (money block → control line → caption). The whole component returns `null` when both
sections are empty, so an anchor never stands over nothing.

**`frontend/components/portfolio/Holdings.tsx`** — the list is inside a `CraftPanel`; the header row
and the data rows are **one** grid class, so the labels sit over the cells they name; the rights cell
has its own three tracks and an empty one is a 56px dashed hairline (`aria-hidden`); the inline edit
is the cell's own 36px field rather than the full R4 primitive (see §5); the actions are the canon's
bordered mono buttons. `styles.holdingStock` and `styles.holdingShares` were referenced here and
**defined nowhere** before this slice — two `class="undefined"` attributes in the shipped product;
the first is now a real class, the second no longer exists.

**`frontend/components/portfolio/NotificationsView.tsx`** — the column is `.notifyColumn`, whose
first row is the rail 「← 보유 종목」; `h2` → **`h1`**; the rows are the canon's three tracks; the
error line moved **inside** the address row (`grid-column: 1/-1`); the chips dropped `.chipOn` for
the canon's `[aria-pressed="true"]`; 로그아웃 · 계정 삭제 · 취소 are `.wide` (104px); the delete
sentence renders **only while armed**. No behaviour changed — same requests, same handlers.

**`frontend/app/portfolio/notifications/page.tsx`** — `styles.narrow` added to the `<main>`; the
620px column is stated at (0,2,0) so the shared `content` width cannot outrank it in either bundle
order.

**`frontend/components/portfolio/Portfolio.tsx`** — the empty state is inside a `CraftPanel`; the
sample surface renders R12's `ConversionOffer` **after 지나간 마감**, without its lead line.

**`frontend/components/auth/ConversionOffer.tsx`** — one new optional prop, `lead` (default `true`).
With it, `/stocks` renders byte-identically to what R12 signed (verified — see §4h); without it, the
body takes the head row beside 닫기 and the band is body + CTA + 닫기, which is what the round's
Sample card draws.

**`frontend/components/portfolio/AddHolding.tsx`** — the panel's title becomes this surface's own
`// ` eyebrow (the round's Home card puts 종목 추가 in exactly that slot, beside 다가오는 마감 and
지나간 마감); the panel keeps its resolver and its behaviour.

**`frontend/components/portfolio/{CarryOver,SampleBanner,SharesInput}.tsx`** — 담기 takes
`.actionPrimary`; two docstrings record what R13 decided (Q-D's withdrawal of 종료; `SharesInput` now
has one caller).

**`docs/reference/design/grounding/copy-inventory.md`** — the R13 tail: 0 new, 2 revised, 2 composed,
2 withdrawn clauses, the moved link, the superseded R5 geometry, and the one place §4b's word rule
collides with R12's signed auth copy (Q47).

---

## 2. The measurements the round asked for (build-prompt §1, 회귀 a–c)

All at **1440**, dev, sample mode (account mode measured identically — §3):

| | measured |
|---|---|
| **(a) every row of both sections shares the same four edges** | chip left **285** · 종목 left **385** · 지배 라벨 left **719** · countdown right **1155** — identical on all five rows (2 upcoming + 3 past). The ragged left edge P7 measured at **144.7px** is **0px**. |
| **(b) 금액 right edge == countdown right edge** | both **1155**. At 1280 both 1075; at 768 both 723; at 767 both 734; at 600 both 567; at 390 both 357. |
| **(c) the empty middle is gone** | the 584.6–761.3px hole is now the **종목 column**, 385 → 719 (334px of name track). Surface width **960px** (`.page.page`), row body 385 → 1155. |
| row body placement | `.rowBody` / `.dependency` / `.lapsed` / `.claim` / `.claimCaption` all start at **385** (열 2) and end at **1155** (마지막 트랙). |
| past chip + date on one line | chip top **839.7** / date top **841.7** — one line, baseline-aligned. Row `row-gap: 4px`, padding `14px 20px`. |
| anchor | exactly **1** `.reference` element, 「기준 2026-08-24 (KST)」, outside both sections. |
| holdings tracks | 종목 285→518.5 · 보유량 534.5→666.5 · 권리 682.5→987 · 액션 1003→1155 — **the header row's four cells land on exactly the same four tracks** (P7.S8's 18.7px / 32.1px header offsets are 0). |
| empty rights cell | 56px × 1px dashed hairline at 682.5, `aria-hidden`, on both rows that have no live right. |

---

## 3. build-prompt §6 — the 13 regression items

| # | item | outcome |
|---|---|---|
| 1 | 신규 한국어 0건 | **green.** The whole frontend diff adds exactly two Korean string literals and both are the operator's revisions of existing R5 constants (`git diff` on `copy.ts`: `EMPTY_TITLE_KO`, `SAMPLE_BANNER_KO`). Zero Korean literals added in any `.tsx`. |
| 2 | 모든 D-day는 상류 값 — 브라우저 날짜 계산 0건 | **green.** No `new Date` / `Date.now` anywhere under `components/portfolio/`; every `dday` / `days` / `date` rendered is the payload's `countdown`. |
| 3 | 조회 ↔ 보유 종목 금액 동일 | **green, measured on both surfaces.** 한화솔루션 500주 → **679,575원추정** on `/portfolio` and **679,575원추정** on `/stocks/00162461`; 하한 545,181원 and the 배정 123주 × 5,525원 caption agree too. One `convert()`. |
| 4 | 지나간 행에 `--alert` 칩 없음 | **green.** `--alert` = `#e0573f` = `rgb(224,87,63)` appears on exactly two elements per row — the 놓친 돈 label and its value. Past chips are `rgb(157,179,168)` (`--ink-2`) on `--surface-inset`; past dates `--ink-3`. |
| 5 | 체크 = 라벨+색만; 캡션 조건부 아님 | **green.** 놓친 돈 → 챙긴 돈, `--alert` → `--live`; value text unchanged (`679,575원추정` before and after); the 본인 표시 caption is present in all three states at an unchanged y. |
| 5b | 링크는 금액 줄 안 · 체크 시 미렌더 · 이동 **0px** | **green, measured.** Link count 2 → **1** → 2 on check/uncheck. Every y is identical to two decimals across the three states, at **1440** (`leads 927.44 / 1091.69`, `docH 1485`) and at **390** (`leads 1465.22 / 1721.91`, `docH 2293`) — **0.00px**. `.lapsedLine` is 32px at ≥768 and 44px at ≤767. Verified in both sample and account mode. |
| 6 | 익명 쓰기 0건 | **green.** With CDP network capture on the anonymous sample: editing and deleting a holding produced **zero** requests of any method (not one GET). 담지 않기 / dismissal leave the browser's values in place. |
| 7 | 모달·오버레이·게이트 0건, `position:fixed` 0건 | **green.** Zero `position: fixed` inside `<main>`, zero `<dialog>` / `[role=dialog]` / `[aria-modal]`, on `/portfolio` and `/portfolio/notifications`, dev **and** production. The only page-level fixed element is R6's AI 질문 launcher, which is chrome on every page and untouched (absent ≤480 by its own round's rule). The 12 `position: absolute` elements in `<main>` are the CraftPanels' corner brackets. |
| 8 | `/portfolio`에 대제목 없음 · `/portfolio/notifications`에 `h1` 하나 | **green.** `/portfolio`: `h1` count **0**, `h2` = the three `// ` eyebrows. `/portfolio/notifications`: `h1` = **["마감 임박 이메일"]**, `h2` count **0**. |
| 9 | 480px 미디어 쿼리 0건 · ≤767 히트 ≥44px | **green.** Source: one `@media (max-width: 767px)`. **Built production CSS**: every `@media (…480px)` block in the bundle was attributed to its module — Ask · Board · Cosmos · Feedback · Footer · Nav; **zero** carry a `Portfolio-module` class. Hits at 390/767: `.action` 44 · `.claimLabel` 44 · `.detailLink` 44 · `.preset` 44 · `.chip` 44 · 닫기 44 · CTA 44; at 768/1440 the same controls are 32 (R10 §0's desktop floor). The only sub-44 element is the 15×15 `<input type=checkbox>` **inside** the 44px `<label>` that is the actual target — the canon's own `.pclaimlab input` size. |
| 10 | 지나간 행 순서: 링크는 금액 줄, 체크박스는 아래 줄, 캡션은 그 밑 · row-gap 4px | **green.** Past ① row children by top: chip 840.7 / name 837.7 / label 840.7 / when 839.7 → **money 867** (link inside it at x 498.2) → **checkbox line 921** → **caption 957**. `row-gap: 4px`. |
| 11 | 독자 표면에 「포트폴리오」 0건 | **green on this round's surfaces.** `document.body.innerText.includes('포트폴리오')` is `false` on `/portfolio` (sample **and** account) and on `/portfolio/notifications`, dev · tailnet · production. Source grep: the word survives in `components/auth/copy.ts` (R12's signed 샘플 포트폴리오로 둘러보기 + its sub-line, the login page — **Q47**), in `components/ops/copy.ts` (operator console, not a reader surface) and as `chrome/copy.ts`'s `PORTFOLIO_LABEL_KO`, which the chrome renders nowhere and this surface no longer re-exports. |
| 12 | 계정 삭제 문장은 무장 전 0건 | **green.** `body.innerText.includes('계정을 삭제하면')` = **false** before the first press, **true** after it, **false** again after 취소. Verified in dev and in the production build. |
| 13 | 로그인 페이지 「실제 공시 4건」 그대로 | **green, confirm only.** Rendered verbatim: 「가입 없이, 실제 공시 4건으로 구성된 예시 포트폴리오를 엽니다 — 클릭 한 번.」 |

---

## 4. The behaviours the round did not browser-walk, walked here for real

The R13 walk had no browser (the Chrome bridge was down) and read account-mode states from code.
Every one of them was exercised in the running product, on a **temporary account created through the
product's own 계정 만들기** and deleted through the product's own 계정 삭제 afterwards. The operator's
session was never touched.

- **(a) 계정 이전 (R5-4)** — a browser holding a sample, then signed in: the inset band lists the four
  issuers, 담기 issues four ordinary authenticated `POST`s and ends the sample (`clearSample`), and the
  four rows arrive in the server's `created_at` order. 담지 않기 dismisses and keeps the browser's value.
- **(b) 인라인 편집** — 수정 turns **only** the 보유량 cell into a field (measured 534.5 → 666.5 — the
  보유량 track exactly, 36px tall) and the action column swaps 수정·삭제 → 저장·취소 **horizontally**.
  750 typed, 저장 → the row reads 750주 and the ① block below recomputes off the served ratio
  (`= 750주 × 0.2314082845 · 1주 미만 버림`). At 390 the field is 132px and both actions are 44px.
- **(c) 삭제 + 8초 되돌리기** — the row goes at once, the inset row 「세기상사 100주 되돌리기」 takes its
  place, and 되돌리기 re-adds it **at the end** of the list (a new holding, `created_at` order) — no
  toast, no modal, no overlay.
- **(d) 챙긴 돈 체크, account mode** — persists through `PUT`, caption 「본인 표시 · 계정에 저장」
  (sample: 「본인 표시」), 0.00px shift, link out and back.
- **(e) 종목 추가** — resolve → R4's signed 검색 불일치 line for a miss; the `?add=` path and the
  repeat-담기 → row-edit handshake are unchanged code.
- **(f) 알림 설정** — rail → `/portfolio`; label track **104px**; 변경 · 로그아웃 · 계정 삭제 share the
  right edge **981**; 로그아웃 / 계정 삭제 / 취소 are all **104 × 32** (44 at ≤767); chips are
  `aria-pressed` multiselect and **clearing every chip is a stored setting** (all four `false` after
  the round-trip — no fallback to the default); a malformed address answers with R12's inherited
  `invalid_email` line in **`--ink-1`** (`rgb(234,242,237)`) with the field border **unchanged**
  (`rgba(163,196,180,.32)`); KakaoTalk is label + note + 「예정」 with no interactive control.
- **(g) 계정 삭제** — arm in place, sentence appears, second press deletes; the reader lands on the
  landing with the nav's 로그인 slot back. `account`, `auth_session`, `holding`, `lapse_claim` and
  `notification_pref` are back at their exact pre-slice counts (2 / 3 / 1 / 0 / 0) — checked after
  **each** of the three temporary accounts this slice created and removed.
- **(h) 샘플 전환 밴드 (Q-E)** — renders **after 지나간 마감** (band top 1247.1, past section bottom
  1227.1), body + 닫기 + CTA with **no lead line**, once per session (`mijual.convert.offer`), gone
  from the DOM entirely on 닫기 (0 elements, nothing in its place), and **not rendered at all** for the
  signed-in reader. `/stocks` is unchanged: lead 「이 보유량은 탭을 닫으면 사라집니다」 + 닫기 in the
  head, then body, then CTA — three children, R12's signed shape.

---

## 5. Three readings, recorded rather than left implicit

1. **The notifications rail renders `HOLDINGS_LABEL_KO`, not `PORTFOLIO_LABEL_KO`.** The plan and
   build-prompt §4b both say the rail composes `← ` + `PORTFOLIO_LABEL_KO` and parenthesise that the
   label is already 보유 종목. In this product it is not: `PORTFOLIO_LABEL_KO` is R5's account-menu
   label 「내 포트폴리오」 and `HOLDINGS_LABEL_KO` is R8's nav word 「보유 종목」 — the exact string the
   round requires, on the exact destination the rail points at. Using it satisfies §4b and item 11
   without re-writing an R5 string the session did not list among its two revisions. R5's constant
   stays exported from the chrome (which renders it nowhere); this surface simply stopped
   re-exporting it.
2. **The row's inline edit is the cell's own field, not the whole R4 primitive.** §2 says 「보유량
   셀만 입력으로」 and the canon draws `.pedit` = a 36px right-aligned mono input (+ the account
   caption). The label, the 주 suffix and the 100/500/1,000주 preset chips stay in 종목 추가, where a
   reader states a count for the first time — inside a 132px table cell they were the reason that
   cell could not hold a track. Every behaviour R4 signed survives (digits only, comma-grouped
   display, Enter confirms) and `HOLDING_LABEL_KO` becomes the field's `aria-label`. **One
   consequence, measured:** in account mode the caption under the field grows the row 64 → 97px while
   editing. The canon's own markup does the same (its `.pedit` stacks input + caption inside an
   `align-items: center` row), so this is the signed shape rather than a port artifact — noted
   because the canon's comment says 「행은 안 움직인다」.
3. **`.search { max-width: 480px }` survives and is not a breakpoint.** It is the console row's own
   width (R2's shape, reused by R4 and this panel). §5/§6-9 retire the two 480px **media queries**,
   both of which are gone; this is a property on one element and any grep for `480` in the module
   will find it.

---

## 6. Gates

| gate | result |
|---|---|
| `cd frontend && npm run typecheck` | clean |
| `cd frontend && npm run smoke` | **16/16** |
| `cd frontend && npm run build` (scratch copy, `next-env.d.ts` untouched) | green — 16 routes |
| `python -m pytest` | **142 passed** (unchanged; no backend file touched) |
| `python3 scripts/workflow.py validate` | passed |
| console errors / warnings, all origins | **0 errors.** The only warning at any width is Next's own dev preload notice for `app_not-found_module_*.css`, present before this slice and on every route. |
| `overflowX` at 1440 / 1280 / 768 / 767 / 600 / 390, both routes, dev · tailnet · production | **0** everywhere |

---

## 7. Doc impact appended to `phase.md`

- `frontend` — 보유 종목 + 알림 설정 rebuilt on R13's canon: one 767 boundary (both 480 blocks
  deleted), four content-independent D-day tracks with the row body on 열 2/-1, holdings + rights-cell
  tracks with a dashed-hairline empty cell, the money line's `min-height` contract, the notifications
  frame (rail + `h1` + 104px label track + `.wide` actions), `ConversionOffer`'s `lead` prop.
- `product` — the anonymous sample surface now carries the product's one conversion offer (after
  지나간 마감, no lead line); no sample reset exists and none is coming (R5-4's 종료 withdrawn); 계정
  삭제 explains itself only when armed; the layer is called **보유 종목** on every reader surface.
- `experience` — 「놓친 돈 상세 →」 lives in the money line and leaves a checked row with a measured 0px
  shift; the caption is unconditional; an empty 진행 중인 권리 cell is a dashed rule, never a sentence.
- `qa` — the `## Regression Checklist` gains this phase's 보유 종목 / 알림 설정 lines (the review
  appends them); build-prompt §6 items 1–13 are the surface's own regression list.
- `copy` (`docs/reference/design/grounding/copy-inventory.md`, edited in place as the grounding pack
  requires) — R13 tail: 0 new, 2 revised, 2 composed, 2 R5 clauses withdrawn.

## 8. New operator questions

**Q47 · Q48 · Q49** are appended to `phase.md`'s `## Operator Questions`: the auth surface's two
「포트폴리오」 strings that §4b's rule now collides with; the canon's `.pdcells` body grammar that the
①/② blocks do not use (the plan directs the wrap-only port, and adopting the cells means
`ConversionChain` for ① and a *new* rendering for ②); and a backend concurrency defect this slice's
scripted walk uncovered in `PUT /portfolio/notifications` (two in-flight saves → `UniqueViolation`
→ 500). None is reachable by a human hand today, none is this slice's to decide, and none was
invented into the surface.
