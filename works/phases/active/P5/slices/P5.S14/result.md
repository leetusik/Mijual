# Result — P5.S14: 내 종목 조회 (R4)

`S11`'s bare `/stocks` shell is replaced by R4's surface, over live `/stocks?q=…`
and `/stocks/{corp_code}`. **0 new dependencies, no primitive / token / chrome /
landing / event file touched, the Python suite untouched at 113, and no Korean
invented** — every string is transcribed with a citation in
`frontend/components/lookup/copy.ts` or re-exported from the surface that already
owns it.

The one thing this slice adds that is not a page: **`frontend/lib/holding.ts`, the
product's single N주 multiplication site**, which `P5.S16` imports rather than
re-implements.

## What landed

| path | what |
|---|---|
| `frontend/lib/holding.ts` | ⌊N × 배정비율⌋ · 초과청약 한도 · 환산액 · Σ, all exact `BigInt` decimal math; the sessionStorage convention |
| `frontend/lib/holding.test.ts` | 3 `node:test` cases (flooring · the R4 worked example · the no-money branch) |
| `frontend/components/lookup/` | `copy.ts` · `LookupHeader` · `HoldingStrip` · `Conversion` · `RightsSection` · `MissedMoney` · `LookupEmpty` · `StockView` · one CSS module · `index.ts` |
| `frontend/app/stocks/page.tsx` | the search state (rewritten from the shell) |
| `frontend/app/stocks/[corp_code]/page.tsx` | a resolved stock — the handle `P5.S13`'s 환산 CTA links |
| `frontend/lib/types.ts` | `LapseBreakdownRow` — the 놓친 돈 row's served shape (`warrant_trading_period`, `issuer_disagreement`), so no call site casts |

## Validation

| command | outcome |
|---|---|
| `cd frontend && npm run build` | **pass** — 6 routes, `/stocks` and `/stocks/[corp_code]` both `ƒ` (request-time) |
| `cd frontend && npm run typecheck` | **pass** (`tsc --noEmit`, clean) |
| `cd frontend && npm run smoke` | **pass** — 6 cases, ~79 ms (3 pre-existing + 3 new) |
| `.venv/bin/python -m pytest` | **113 passed**, 2.52 s — untouched, no Python file edited |
| `python3 scripts/workflow.py validate` | **pass** |

### Headless-Chrome pass (localhost:3000 over `npm run start`, live API on :8000)

**43 checks, all PASS**, over 15 navigations on 9 real issuers × 2 viewports.
Screenshots in the session scratch dir (`shots/01…12`). A second pass in
`next dev` reproduced the redirect, the comma grouping and a clean console.

- **Resolution** — `계양전기` (name) and `012200` (종목코드) both land on
  `/stocks/00102618`; a miss renders the locked
  `‘없는회사이름’와 일치하는 종목이 없습니다 — 종목명 또는 종목코드로 다시 검색해
  주세요.` and keeps the query in the box.
- **Unpriced ①** — 계양전기 shows `발행가 확정 전` + `확정 예정 2026-09-01 — 확정 후
  증서 이론가치와 금액을 환산합니다`, 배정 신주 **115주**, 초과청약 한도 **+23주**,
  the caption `= 500주 × 0.2314082845 · 1주 미만 버림`, and **no `원` anywhere on
  the page body**.
- **The one true cross-check** — 한화솔루션 500주 reproduces R4's own card
  client-side: **679,575원** (하한 **545,181원**), 배정 **123주 × 5,525원**,
  소멸 계산 `발행 − 청약 = 소멸 3,734,925주 (8.86%)` + **206.4억원**, the calc
  footer `배정 123주 = 500주 × 배정비율 0.2465120994 (1주 미만 버림) · …`, and the
  disclaimer footnote. 1,000주 gives exactly 2× (246주 · 1,359,150원).
- **대한광통신 두 readings** — 발행사 기재 불일치 badge + **2,117,937주** (cited)
  beside the derived **2,083,302주** with its two cited inputs (발행 23,465,365 ·
  청약 21,382,063), unreconciled, plus R3's header and footer sentences.
- **Restore chip** — 500 on 한화솔루션, then 대한광통신 offers `이전 입력 500주`
  with the field **empty**; pressing it fills. Returning to a stock already typed
  into restores **its own** count and offers **no** chip. `sessionStorage` holds
  `{"v":1,"entries":{…3 issuers…},"last":{…}}`; nothing is sent anywhere.
- **②/③** — 유티아이's four ② rows carry 오버행 · 전환 시 주식수 · 전환가액 and no
  환산액; the D+46 row reads **진행 중** in live green and the word 종료 appears
  nowhere. 휴맥스's live ③ (D-5) carries the 2단계 dependency line, **no
  매수예정가** and **no won amount**.
- **Empty states** — 고려아연 renders the locked no-event line + 감시 대상 3종 +
  감시 중 **488건** + the coverage boundary (유증 2026-01-01부터 · CB
  2025-06-01부터).
- **Degraded row** — 한솔테크닉스 (lapse hanging off a *flagged* event) keeps its
  소멸 계산 and loses the 매매기간 line, the `[근거]` and the link, as `P5.S4`
  note 6 specifies.
- **Mobile 390×844** — no horizontal overflow, every target on this surface
  ≥44px, the grid head not drawn (label/value lines instead), **zero
  `position: fixed`** elements, no accordions.
- **Console** — clean except Next prefetching the chrome's `/auth/login`, whose
  page `P5.S15` has not built; measured identically on `/` and on an event detail
  page, so it is chrome-wide and pre-existing (see *Observations* 4).

## Decisions this slice made (all recorded in `phase.md`)

1. **Two routes, and the search redirects onto the handle.** `?q=` resolves
   server-side and `redirect()`s to `/stocks/{corp_code}`; a miss stays put. The
   param is **`q`**, the name S12's hero form and the API already use.
2. **One math seam, in `lib/`.** `lib/holding.ts` — `BigInt` over the digits,
   never `Number()`. `convert()` returns `value: null` when the factors carry no
   `unit_value`, so **money before 확정발행가 is unconstructable**, not merely
   unrendered — the same shape `mijual.present` uses server-side.
3. **sessionStorage key `mijual.lookup.holdings`**, one JSON object
   `{v, entries: {corp_code: shares}, last: {corp_code, shares}}`. Per-issuer, so
   `P5.S16`'s 세션 이월 제안 can read the whole session in one go.
4. **No holding ⇒ no derived number.** An empty field is not a zero: the ① row
   states its factors, and the 놓친 돈 headline (frame line + total) appears only
   once a count exists. Printing `0원` under "청약도 매도도 하지 않았다면" would be
   a claim about a holding the reader never described.
5. **The coverage caption's start is served, its end is the record's word.**
   `집계 범위 {coverage.start} ~ 오늘 (KST)` — `coverage.end` *is* today KST, and
   `오늘` is R4's own literal.
6. **The boundary panel renders rights-type chips, not ①②.** R1's revision
   removed ①②③ from the UI; `components/event/copy.ts` already records the same
   reading for ③'s 1단계/2단계. Both dates come off the wire (the record writes
   "2025-06부터"; the payload says `2025-06-01`, and the payload governs).
7. **②'s 전환가액 stays.** R4 §② names it in the dilution context while its hard
   rules say "②/③ rows with won amounts — never". The rule is about the
   **per-holding** conversion: R5 later calls this very strip ②'s substitute for
   it ("금액 = R4 계약 그대로", `P5.S8` note 6). No holding is multiplied on an
   ②/③ row, and ③ carries no 매수예정가 at all (it is not in `STOCK_FIELDS`).
8. **The calc footer is per row.** R4 writes one footer under a one-offering
   breakdown; offerings of one stock do not share a 배정비율, so one footer for
   several rows would print one row's factor as if it covered the others.
9. **The 놓친 돈 row's citation is the 매매기간 quote only** (R4: "one `Citation`
   per row"). The 소멸 계산 cell prints 발행/청약 as *words* and only the 소멸
   count as a number, so **D4 is not re-triggered**: no summed 실적보고서 figure
   carries a chip on this surface.

## Deviations from `plan.md`

- **The plan's "never a won amount" for ②/③** is implemented as *never a
  per-holding won amount*; 전환가액 renders because R4 §② names it (decision 7).
- **The 진행 중인 권리 zero state** got the factual line `청약 {date} 종료` from
  `LookupMobile.html`, which the plan does not list. Dropping it would have left
  a signed card state unbuilt.
- Nothing else: every deliverable 1–10 landed as written.

## Observations (no fix attempted)

1. **D2's second check — the trigger did NOT fire.** 코이즈 has two exposable ①
   events (1195 · 1264) sharing version `20260122000058`, but only ev1195 carries
   a 증권발행실적보고서 (`20260129000503`). The breakdown is keyed on the
   실적보고서, which is unique, so the page shows **exactly one** offering row and
   `totals.offerings: 1` — 1,000주 → 944,495원, no double count. Verified in the
   DOM (one `[role=row]` under the head) and in the payload. Nothing was
   de-duplicated. `P5.S19` still holds the board half of the check.
2. **The `P5.S4` note-8 gap is now visible, and it is a design question.** An ①
   whose 청약 has closed but whose 실적보고서 has not been filed is in **neither**
   section, so its stock renders the *no-event* empty state — "이 종목에는 진행
   중이거나 2026년에 소멸된 권리가 없습니다". Live today: **센서뷰 (01593668)** and
   **클로봇 (01784914)**, both with a 확정발행가-priced ① whose 청약 closed
   **2026-08-14**, eight days ago. The sentence is what the contract serves and
   nothing was invented for them, but for a reader who held either last week it is
   not true. `pending` cannot be reused (its 청약 is over) and a 놓친 돈 row would
   be an invented figure. **`P5.S19`/the operator decide** whether a state gets
   signed for it.
3. **`P5.S4` note 5 confirmed on the surface: no live ① in the corpus has a
   확정발행가**, so the 환산액 path is exercised only through 놓친 돈 rows today.
   It is built and proven anyway — the 한화솔루션 cross-check runs the identical
   `convert()` call an ① row makes, and 센서뷰/클로봇 show the corpus *does*
   produce priced ①s; theirs are simply past.
4. **Chrome-wide, pre-existing: `/auth/login` 404s in the console** on every page
   (measured on `/`, `/events/{rcept_no}` and here) because Next prefetches the
   nav's 로그인 link and `P5.S15` has not built the page. Not this surface's, and
   it disappears when S15 lands.
5. **`P5.S19` fidelity item, unchanged by this slice:** the shared `Citation`
   primitive's `[근거]` chip is 14px tall and the DART link inside its panel 17px
   at 390px — below the mobile 44px floor, identical on R3's detail page. The
   primitive was not touched (a variation belongs in it with a named prop and a
   citation, never as a local restyle).
6. `next-env.d.ts` flips between `.next/types` and `.next/dev/types` depending on
   whether `next build` or `next dev` ran last. It is the framework's own
   "should not be edited" file; the tree was left in the `next build` form it was
   committed in.

## Doc impact

Appended to `phase.md`'s *Doc impact* list: **`frontend`** (the surface, the
shared math seam, the session convention, the two routes), **`experience`** (what
this surface states and refuses to state) and **`qa`** (the frontend check now
covers 조회; the browser pass and its measured invariants). No doc version was
created — versioning is `P5.REVIEW`'s.
