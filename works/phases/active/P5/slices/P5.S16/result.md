# Result — P5.S16: 내 포트폴리오 (R5-3 … R5-8)

내 포트폴리오 is live at `/portfolio`, in both of its signed modes (계정 / 샘플), plus
알림 설정 at `/portfolio/notifications` and the logged-in chrome swap. It is the
product's only gated surface, and the gate is the API's own 401 rather than a second
rule. Everything below was measured on the live stack (FastAPI + `npm run start`,
plus a `next dev` pass) in a real headless Chrome over `http://localhost:3000`.

## What landed

| File | Role |
| --- | --- |
| `frontend/app/portfolio/page.tsx` | the route: gate (401 → `/auth/login`), `?sample=1` mode, `?add=` server-side resolution |
| `frontend/app/portfolio/notifications/page.tsx` | 알림 설정 — same gate, `GET /portfolio/notifications` |
| `frontend/components/portfolio/Portfolio.tsx` | the client orchestrator: two modes/one rendering, mutations, 8초 되돌리기, the two offers |
| `frontend/components/portfolio/Holdings.tsx` | 보유 종목 rows, inline 보유량 edit (개정 ④ column swap), the undo row |
| `frontend/components/portfolio/SharesInput.tsx` | R4's own 보유량 field with the caption swapped (`계정에 저장 · 마감 알림의 기준`) |
| `frontend/components/portfolio/AddHolding.tsx` | 종목 추가 + the `?add=` handshake + the repeat-담기 routing |
| `frontend/components/portfolio/Deadlines.tsx` | 다가오는/지나간 마감, the served 기준 line, 놓친 돈/챙긴 돈 |
| `frontend/components/portfolio/CarryOver.tsx` | 세션 이월 (R5-3) and 계정 이전 (R5-4) — one inset row, two variants |
| `frontend/components/portfolio/NotificationsView.tsx` | 수신 주소 · 시점 칩 · KakaoTalk(예정) · 로그아웃 · 계정 삭제 |
| `frontend/components/portfolio/SampleBanner.tsx` | the signed 샘플 banner |
| `frontend/components/portfolio/copy.ts` | every Korean string on this surface, each cited to R5's build prompt / result.md |
| `frontend/components/portfolio/Portfolio.module.css` | the surface's styles (tokens only; ≥480px table form, ≤480px single column) |
| `frontend/lib/sample.ts` | the 샘플 store (localStorage + `useSyncExternalStore`), shared by surface and chrome |
| `frontend/lib/account.ts` (+ `account.test.ts`) | `abbreviateEmail` — the nav's 축약 이메일 |
| `frontend/components/chrome/useAccount.ts` | one shared `GET /auth/me` probe for the chrome slot |
| `frontend/components/chrome/AccountSlot.tsx` (+ `.module.css`, `copy.ts`) | the slot's three renderings — 로그인 / 계정 메뉴 / 「샘플」 + 샘플 종료 |
| `frontend/lib/routes.ts`, `frontend/lib/session.ts` | `notifications` route entry; in-flight dedupe for the auth probe |
| `frontend/components/lookup/{RightsSection,index}.ts(x)` | export 조회's `Conversion` / `Dilution` so this surface renders the **same** components |

## The surface, deliverable by deliverable

1. **Gate.** `page.tsx` asks `GET /portfolio` with the incoming cookie forwarded
   (S10 note 13); a `401 unauthenticated` `redirect`s to `/auth/login`, anything else
   throws. One request, one authority — the page's idea of "logged in" cannot differ
   from the service's. Measured: `/portfolio` and `/portfolio/notifications` redirect
   anonymously; `/`, `/stocks`, `/ask`, `/events/{rcept_no}` still answer 200 with no
   cookie. **No page 대제목** (개정 ③) — the layer is named only in the account menu.
2. **Holdings.** Rows are 종목 / 보유량 / 진행 중인 권리 요약 / actions. 수정 swaps the
   action column to 저장·취소 **in place, horizontally** (measured: same `top`, ±0 px),
   and the 보유량 cell becomes R4's `SharesInput` (mono, `inputMode="numeric"`, comma
   groups, 100/500/1,000주 chips) with the caption swapped. The 진행 중인 권리 chip is
   the server's already-serialized countdown (`holding.rights.next`), so the row and
   the D-day section below it cannot disagree. 삭제 is real immediately
   (`DELETE /portfolio/holdings/{id}`) and the 되돌리기 window is the client's: the
   issuer + count live in memory for 8 s and 되돌리기 re-adds them through the ordinary
   `POST` (a restored row is therefore a **new** holding, last in the served order, and
   a 챙긴 돈 mark is untouched either way because it is keyed on the 실적보고서).
3. **Empty state + 세션 이월 (R5-3).** The signed empty copy, and — when S14's
   `mijual.lookup.holdings` holds something the account does not — the inset row
   "조회에서 입력한 {종목} {n}주가 이 세션에 남아 있습니다" with 담기 / 담지 않기.
   Never automatic; 담지 않기 sets a **session** flag and keeps the browser's value.
4. **D-day 목록.** Two sections in the server's order, the served anchor line
   ("기준 YYYY-MM-DD (KST)"), and every amount through `lib/holding.ts`. ①priced →
   tagged 금액; ①unpriced → 배정 신주 counts + 발행가 확정 전 + 확정 예정일, no 원;
   ② renders 조회's **own** `Dilution` component and ③ its 2단계 dependency line — no
   per-holding money in either. Past rows carry the faint `기간 지남 · D+n` /
   `통지 마감 지남 · D+n` chip (measured `rgb(109, 131, 120)`, never `--alert`) and past
   ① 소멸 rows carry the holding-basis figure + "놓친 돈 상세 →".
5. **챙긴 돈 (R5-8).** The checkbox "청약·매도로 챙겼습니다" on past ① 소멸 rows;
   checked flips the label 놓친 돈 → 챙긴 돈 and the ink `--alert` → `--live` on the
   **same** figure (measured `rgb(224, 87, 63)` → `rgb(95, 208, 165)`, 679,575원 both
   sides). Authenticated it is `PUT/DELETE /portfolio/claims/{rcept_no}` (key = the
   증권발행실적보고서's own `rcept_no`, verified 14 digits in the store); in sample mode
   it is the browser's, with the caption saying so. It reaches no aggregate — there is
   no 합계/총액 anywhere in `main`.
6. **알림 설정** at `/portfolio/notifications`, reached from the account menu. 수신 주소
   is the account email with a 변경 affordance (in-place 저장·취소); the 시점 칩 are a
   multiselect over the API's `lead_days` (default served 7일 전 + 1일 전, verified), and
   **an empty selection is saved as `[]`** — the round's only off switch, so it does not
   fall back to the default. The KakaoTalk row is a label + 「예정」 + the signed sentence
   and renders **no** control at all (verified: zero `button`/`input`/`select`/`a` in the
   row) — structural, since S8 built no server field for it. 로그아웃 and 계정 삭제 live
   here, and the whole view is absent in sample mode.
7. **샘플 모드 (R5-4).** `?sample=1` loads the anonymous `GET /portfolio/sample` — the
   four pinned issuers and **five** D-day rows (S8 note 14: 대동기어 also holds a lapsed
   ①; live data governs the record's table of four). The reader's edits are the
   browser's (`localStorage`), the rows/factors/D-days stay the server's, and no
   anonymous write is attempted. The banner is verbatim; the nav slot becomes 「샘플」 +
   샘플 종료; 종료 wipes the store and returns to the anonymous landing. No email, no
   account fact, no 알림 anywhere in the mode (verified: no `@` on the page).
8. **Logged-in chrome.** `AccountSlot` has exactly three renderings — R2's 로그인 link
   untouched, the 축약 이메일 menu (`p5s16.b@mijual.test` → `p5s1…test`, mono) with
   내 포트폴리오 / 알림 설정 / 로그아웃, and the 샘플 pair, which outranks both. The mobile
   sheet gets the divider + 내 포트폴리오 (email alongside) / 알림 설정 / 로그아웃. The
   three nav destinations, the 52 px bar, the active underline, the 의견 slot and the
   whole footer are untouched. 로그아웃 is immediate, dialog-free, and leaves through a
   **fresh document load** (`window.location.assign`) so no gated payload survives in a
   client cache and Back cannot restore a signed-in surface; the one-time
   "로그아웃되었습니다" travels through S15's `sessionStorage` flash and rendered exactly
   once (verified: 1 occurrence, gone after a reload).
9. **Mobile ≤480 px.** Single column, `지나간 마감` collapsed to a summary row (the second
   date line hides; the chip already carries `D+n`), 종목 추가 as the bottom panel. At
   390×844: horizontal overflow **0 px**, `position: fixed` elements **0**, every tap
   target ≥44 px (the 챙긴 돈 checkbox is the native 16 px box inside a 194×44 label —
   the label is what a tap activates).

## Storage keys (S19 will inspect these)

| Key | Store | Owner | Contents |
| --- | --- | --- | --- |
| `mijual.lookup.holdings` | sessionStorage | S14 (read only here) | 조회's per-tab 보유량 |
| `mijual.auth.flash` | sessionStorage | S15 (written here) | the one-time 로그아웃 message kind |
| `mijual.portfolio.sample` | **localStorage** | this slice | `{v:1, holdings:[{corp_code, shares}], claims:[rcept_no]}` — the sample's own edits and marks |
| `mijual.portfolio.carry` | sessionStorage | this slice | 세션 이월 제안을 이 탭에서 거절함 |
| `mijual.portfolio.migrate` | sessionStorage | this slice | 계정 이전 제안을 이 탭에서 거절함 |

Both dismissals are **flags, not deletions**: declining keeps the browser's value and a
new session may ask again. Nothing anonymous reaches the server.

## The bug this slice found and fixed — an inline `[]` that froze the App Router

Worth recording in full, because the symptom pointed at the framework and the cause was
one character of ours.

`Portfolio` passed `sampleCorpCodes: sample?.holdings ?? []` into `useCarryOffer`. That
inline `[]` is a new identity on every render; it feeds a `useMemo`, whose result feeds
an effect's dependency list, and that effect called `setEntries([])` — another new array.
So: render → memo recomputes → effect re-runs → state "changes" → render, forever.

React logged nothing (the loop runs through passive effects, not nested sync updates) and
the page looked fine. What broke was everything that needs a React transition to finish:

- **`router.refresh()` never committed.** The RSC refetch went out (`RSC: 1`, state tree
  marked `refetch`), the server re-read the API and answered 200 with the *new* numbers
  (verified by replaying the identical request byte-for-byte), and the tree kept the old
  payload — including a server-rendered probe value placed outside the component.
- **Every client navigation away from `/portfolio` did nothing** — the nav links and the
  account menu alike, at any wait, with a real dispatched mouse click landing on the
  right element and `preventDefault()` observed. CDP showed why: the navigation's RSC
  response arrived and was then **`net::ERR_ABORTED`** — the next render interrupted the
  transition, and the router aborted its own fetch.
- Measured before the fix: `/portfolio → /` 0/4 committed, `/ask → /`, `/ → /ask`,
  `/ → /stocks` 12/12 committed. After the fix: `/portfolio → /` 4/4 and the account menu
  3/3, and the same suites went green.

The fix is two shared frozen empties (`NO_HOLDINGS`, `NO_ENTRIES`) plus an
identity-preserving functional `setEntries`, all commented at the definition site so the
next reader does not re-derive it. **This is the general trap for this codebase:** an
inline `[]`/`{}` that reaches a dependency list of an effect that sets state will not warn
— it will quietly stop the App Router.

The surface's own re-read is deliberate and independent of it: an account write is
followed by `getPortfolio()` from this client, and the whole served payload replaces the
one in state. Same endpoint the page reads, one authority, no re-composition here — and
cheaper than a `router.refresh()`, which in Next 16 also re-prefetches every in-viewport
`<Link>` (vercel/next.js#93210). Measured: an edit is on screen ~0.1 s after the write,
and navigating away and back (client navigation **and** the Back button) shows the same
value from a fresh server render.

## Decisions worth knowing (recorded rather than discovered later)

- **A repeat 담기 opens the row's 수정** instead of surfacing S8's `holding_exists` 409 —
  R5 wrote no "이미 담긴 종목" line, and the client holds the whole list, so no Korean was
  invented. Verified from both entrances: the panel's own 조회, and the `?add=` link.
- **계정 삭제 arms in place.** R5 signs "즉시" and forbids gate screens and forced modals,
  so the confirm is the round's own vocabulary: the action column becomes 계정 삭제 · 취소
  (the same horizontal swap 개정 ④ signs for a row) and the second press deletes. No new
  copy, no overlay, no irreversible act on one stray click.
- **로그아웃 · 계정 삭제 · 샘플 종료 all leave through `window.location.assign`.** Besides
  the cache-hygiene argument, a `router.push()` from these controls is dropped in a real
  browser: the control unmounts in the same commit (measured before the loop fix, and the
  reason stands on its own).
- **종목 추가 is an account affordance and is not offered in 샘플 모드.** R5-4 signs the
  sample as a fixed composition that is *editable* and endable; adding an arbitrary issuer
  would need this client to compose that issuer's rows and place them into 다가오는/지나간
  itself — a second composition site for the placement rules S8 owns (a past ③ appears in
  no 조회 payload at all). Recorded for S19/REVIEW rather than improvised.
- **The chrome probes the session once per pathname** through a module-level store
  (`useAccount`) and `lib/session.ts` now de-dupes in-flight `GET /auth/me` calls, so the
  slot, the offers and the auth pages share one answer. The slot renders **nothing** until
  the probe answers — showing 로그인 for a frame to a signed-in reader is the wrong half of
  R5's 가짜 사용자 정체성 rule.
- **조회 and 포트폴리오 render the same components** for ② and ③ (`Conversion`, `Dilution`
  exported from `components/lookup`), so "수치 불일치 금지" holds structurally rather than
  by discipline.

## Deviations from `plan.md`

- **None in scope or behaviour.** Three notes:
  1. The plan expected 세션 이월 to arrive from 조회; it does, and the same inset row also
     carries R5-4's 계정 이전 variant, because both are "an offer, never automatic" with
     different sources. One component, two variants.
  2. `?add=`'s origin is the **event detail** page's one-liner (S15's `DeadlineOffer`,
     rendered only where the deadline is still ahead), not the stock page — the plan said
     "the detail 담기 link", which is what that is.
  3. Two changes outside `components/portfolio/` were needed and are within the plan's
     seams: the `AccountSlot` swap (deliverable 8) and exporting 조회's two rights
     components so this surface can render them instead of re-implementing them. No
     primitive, token, `Nav`, `Footer` or stylesheet of theirs was touched.

## Validation

| Command / pass | Outcome |
| --- | --- |
| `npm run typecheck` | pass |
| `npm run build` | pass — 10 routes; `/portfolio` and `/portfolio/notifications` both `ƒ` |
| `npm run smoke` | **9** `node:test` cases pass (~105 ms) — 8 inherited + the new `abbreviateEmail` case; still no jest/vitest/jsdom |
| `.venv/bin/python -m pytest` | **113 passed**, untouched |
| headless Chrome, `npm run start` + uvicorn — 샘플 모드 suite | 23/23 |
| … 계정 A (signup → 세션 이월 → 종목 추가 ×3 → rows/D-day → 조회 cross-check → inline edit → 삭제+되돌리기 → 챙긴 돈) | 29/29 |
| … 계정 B (계정 메뉴 → `?add=` handshake → repeat 담기 → 삭제 확정 → 계정 이전) | 22/22 |
| … 계정 C (알림 설정 → 수신 주소 변경 → 계정 삭제 arming → mobile 390×844 → 로그아웃 → gate → re-login → 계정 삭제) | 33/33 |
| `next dev` smoke (gate · sample render · local edit persisted · client navigation) | pass |
| `python3 scripts/workflow.py validate` | pass |

Three assertions in the scripts were wrong and were corrected before the final run, all
re-measured by hand first: the ②/③ "no money" check flagged `전환가액 15,552원`, which is
R4's signed **per-share** dilution context (the money test is the 보유량-기준 column, not
the character 원); the "no total" check read `document.body.innerText`, which picked up the
**footer's** market-wide gate sentence ("…총액에서 제외했습니다") — `main` has none; and the
tap-target check measured the native checkbox instead of its enclosing 44 px label.

Test data: all four suites ran against `%@mijual.test` accounts, and the last one deletes
its account through the product's own 계정 삭제. Final state — `account`, `auth_session`,
`password_reset`, `holding`, `lapse_claim`, `notification_pref` all **0**. uvicorn, Next
(dev and start) and headless Chrome were all stopped afterwards.

### Numbers measured on the live surface

- 한화솔루션 500주 → **679,575원** on 포트폴리오 **and** on 조회 for the same holding; 1,000주
  → 1,359,150원 (the one multiplication site, floored on the exact digits).
- 대동기어 300주 → 446,720원 추정; 계양전기's unpriced ① prints 배정 신주 counts and
  **발행가 확정 전**, no 원; 대동기어's ② prints 오버행 6.68% · 전환 시 주식수 643,004주 ·
  전환가액 15,552원 and no holding-basis money; 세기상사's ③ prints only the 2단계 sentence.
- Sample: 4 issuers, **5** D-day rows, claim key `20260730000366` (14 digits).

## Gaps and readings flagged (S17 / S19 / `P5.REVIEW`)

1. **계정 이전 label.** `MIGRATE_LABEL_KO = "계정 이전"` is composed from R5-4's own phrase
   ("샘플 → 계정 이전 제안") rather than quoted from a signed line, because the round writes
   the offer's *body* but no heading for it. Flagged for S19's copy inspection.
2. **샘플 모드 has no 종목 추가** (reasoning above) — a deliberate reading of R5-4, worth a
   confirm at the review.
3. **수신 주소 변경 takes no password** — the existing open question from S8 note 10 is now
   visible on a surface; nothing new was decided here.
4. The **footer's 49.2억원 gate sentence** is the only 총액 wording a reader sees on this
   surface; it is chrome from S11 and its open question stands unchanged.
