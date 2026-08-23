# R13 handoff — Polish: 내 포트폴리오 + 알림 설정 (surface 6 of 8)

- Round **R13** · slice `P8.S12` (co-work) · apply slice `P8.S13`
- Claude Design project: **"Mijual Design System"** (reads this repository via GitHub)
- Review group for new cards: **`⏳ P8.S12 · Portfolio`**
- **Token freeze**: `foundations/tokens.css` is signed (R8). This round changes no token.
- Common rules: **R10 §0 adopted as-is** (keep-all, nowrap mono, tabular-nums, border-box, single
  767px breakpoint, hit floors 32px desktop / 44px ≤767) — R11/R12 already build on it.

**Walk provenance (read this first):** the Chrome bridge was down at walk time, so this walk is
(a) the **rendered SSR markup** of the live surface at `http://127.0.0.1:3000/portfolio`
(anonymous = 샘플 모드, real payload, real copy), (b) the module source + CSS, and (c) **P7's
browser-measured geometry** (`works/phases/active/P7/phase.md` Q8, measured at 1440/768/390).
Account-only states (carry-over, migrate offer, 알림 설정, row edit/undo, 계정 삭제 arming) were
read from code, not walked — the cards must draw them from the states listed in §2, and `P8.S13`
verifies everything in the real operator runtime.

## 1. Product context

Routes: `/portfolio` (signed-in → the account's rows; **anonymous → the same surface in 샘플 모드**,
R8 — no redirect, no gate) and `/portfolio/notifications` (gated, 401 → `/auth/login`).
Components: `frontend/components/portfolio/` — `Portfolio` (orchestration + offers), `Holdings`
(table + inline edit + 8s undo), `Deadlines` (다가오는/지나간 rows, reusing lookup's `Conversion`/
`Dilution`), `AddHolding`, `SharesInput` (R4 primitive, caption swapped), `CarryOver` (R5-3 session
carry + R5-4 migrate offer), `SampleBanner`, `NotificationsView`, `copy.ts`, `Portfolio.module.css`.

Designed by **R5** (R5-3…R5-8), re-cut in part by **R8** (nav slot 보유 종목; 「샘플」 chip + 샘플
종료 retired from chrome; anonymous = sample). **P7 already did a fidelity pass** (mono-11 tracked
eyebrow, hairline row rhythm, one 44px lapsed band, content-independent header tracks, caption
「본인 표시」) — those corrections are landed truth, not findings.

Live sample payload (fixed composition, live corpus): 계양전기 500주 (① D-1 매매 마감, 발행가 확정
전), 대동기어 300주 (② D-61 전환청구 개시 + past ① D+47 소멸 446,720원), 한화솔루션 500주 (past ①
D+45 소멸 679,575원), 세기상사 100주 (past ③ D+49 통지 마감 지남). 2 upcoming + 3 past rows.

No page 대제목, by signed revision (R5 개정 ③): the surface opens with content; the nav slot is the
location marker. `/portfolio/notifications` renders one CraftPanel with `h2` 「마감 임박 이메일」.

## 2. The walk — 14 findings

1. **The D-day rows' desktop geometry is still the un-designed thing (P7 Q8-A — the headline).**
   `.rowHead` is `justify-content: space-between`: at 1440 the right-hand block has a **144.7px
   ragged left edge** and **584.6–761.3px of empty middle** (232.6–409.3px at 768). R5 names the
   row's parts and no geometry; R2's board pins a fixed grid (`86px 1fr 300px 230px 96px`) for
   exactly this reason. The decomposition marked this "the one remaining 'not organized' symptom" —
   this round is where it finally gets designed.
2. **Two of four holding rows render an empty 진행 중인 권리 cell** (P7 Q8-C): 한화솔루션 and
   세기상사 hold only past rights, so at ≥480 the third column is a visible hole. R5 signs no
   empty-cell sentence; the walk's question is what the *cell* should be, not what Korean to mint.
3. **지나간 마감 has no 「기준 YYYY-MM-DD (KST)」 line** (P7 Q8-B) — `P5.S8` read R5's anchor
   sentence as page-level (stated once, on the counting-down section); the S8 plan read it as
   per-section. The string exists; only placement is open.
4. **A 챙긴 돈 row still links 「놓친 돈 상세 →」** (P7 Q8-D) — R5-8's checked-state delta is four
   items and the link is not one; the target section is literally named 「2026년 놓친 돈」.
5. **The 「본인 표시」 caption renders whether or not the box is checked** (P7 Q8-E) — R5-8 phrases
   the caption as one of 체크's consequences; making it conditional adds a 22.6px shift on click.
6. **Should a 챙겼습니다 row disappear from 지나간 마감?** (P7 Q4) — R5-8 signs re-label + hue,
   same figure, same row. Removing the row would supersede a signed round.
7. **Sample edits are permanent and the signed 종료 no longer exists anywhere.** `lib/sample.ts`
   seeds localStorage from the served composition once, then the browser copy is authoritative;
   R5-4's 「종료: 샘플·브라우저 저장분 삭제 후 로드 전 상태 복귀」 lived in the chrome slot that
   **R8 retired** (`clearSample()` now runs only on account migration). A first-time reader who
   deletes 계양전기 in the sample can never get it back in that browser. The signed behaviour is
   orphaned — some control (reset/restore) has no home.
8. **The anonymous sample surface makes no conversion offer.** R12 just built the offer ladder
   (numbers > inset band > one-line link > nav 로그인), and the sample portfolio — the surface an
   anonymous reader lands on from the nav — carries only the banner. Whether the R12 band belongs
   here (and where) is a placement decision the ladder grammar already knows how to answer.
9. **The login page's sample subline says 「실제 공시 4건」 while the surface shows 5 D-day rows**
   (P7 Q6#6) — 4 pinned filings produce 2 upcoming + 3 past rows. The string is R5's, re-landed
   by R12 (`A_SAMPLE_SUB`); the mismatch reads as a miscount to a reader who counts.
10. **`carryOverKo` speaks developer vocabulary** (P7 Q7④): 「조회에서 입력한 {종목} {n}주가 이
    세션에 남아 있습니다」 — 세션 is also the only word conveying impermanence. And its sibling
    (Q7's fifth): sample caption is now 「본인 표시」; should the account caption keep
    「· 계정에 저장」 or match?
11. **This surface still switches at 480px, twice** — `Portfolio.module.css` has
    `@media (min-width:480px)` (the holdings grid) and `@media (max-width:480px)` (past-row
    summary), while R10 §0 settled the product on **one 767px boundary** and R11/R12 retired their
    480s. In the 481–767 window the four-column holdings table and the desktop row layout stand on
    a ~600px screen.
12. **`/portfolio/notifications` has no `h1` and no way back but the nav.** The page renders one
    panel with an `h2`; R12 just gave the auth pages a rail (「← 관제 현황판」) for exactly the
    dead-end reason. Heading outline and the frame are both open here.
13. **The 수신 주소 변경 error line inherits R12.** `NotificationsView` renders
    `authErrorKo(code)`; before R12 `invalid_email` mapped to nothing (a silent failure), after
    `P8.S11` it maps to 「이메일 주소 형식이 올바르지 않습니다.」 — the card should draw the error
    state with the now-real line, and the round should say whether that inheritance is wanted here.
14. **States that exist but were not walkable, to be drawn explicitly:** row edit (액션 열
    수정·삭제 → 저장·취소, 가로 배치) · 8초 되돌리기 inset row (undo lands the restored row last)
    · empty account portfolio (「포트폴리오가 비어 있습니다」) · R5-3 session-carry inset row
    (담기/담지 않기) · R5-4 migrate offer (label 계정 이전, list, two controls) · `?add=`
    preselect in 종목 추가 · repeat 담기 → opens the existing row's 수정 · 알림 설정 chips
    (aria-pressed multiselect, empty = a setting) · KakaoTalk 라벨 + 「예정」 칩, no control ·
    계정 삭제 arm-in-place (계정 삭제 → 계정 삭제·취소, second press deletes) · busy/disabled.

### 2b. Operator decisions (take at the gate or in the session)

- **Q-A (P7 Q4)** — a 챙겼습니다 row: stays in 지나간 마감 re-labelled (signed R5-8), or
  disappears? Default: **stays**.
- **Q-B (P7 Q8-D)** — 「놓친 돈 상세 →」 on a checked row: keep (default) or change/remove (mints
  or moves Korean).
- **Q-C (P7 Q7④ + fifth)** — `carryOverKo`'s 세션 wording: keep the promise as-is (default) or
  re-say in reader language (one new sentence, dated exception); account caption keep
  「본인 표시 · 계정에 저장」 (default) or drop to 「본인 표시」.
- **Q-D (finding 7)** — does a sample reset/종료 control return (R5-4's orphaned 종료 needs a new
  home — this surface is the natural one), or are permanent browser edits accepted? Default:
  **session decides the home; the behaviour returns**.
- **Q-E (finding 8)** — does the R12 conversion band render on the anonymous sample portfolio?
  Default: **session decides placement under the R12 ladder rules** (no gate, dismissible, once
  per session, never above the numbers).

## 3. Locked vs. in play

**Locked (RESPECT THE DESIGN / structural):** all D-days are upstream values — no browser date
math; 수치 불일치 금지 — ①/② blocks are lookup's own `Conversion`/`Dilution`, one multiplication
site (`lib/holding.ts`); no anonymous write ever (offers, never transfers; 담지 않기 keeps the
browser's value); 삭제 = 즉시 + 8초 되돌리기, 모달·게이트·오버레이 금지 (전 표면); KakaoTalk row
has no interactive control (no server field exists); ②/③ carry no money; past rows never
`--alert`; 「추정」 marker semantics; R5-8 check = re-label + hue only, same figure, no aggregate;
sample renders no account fact (no address, no 알림 설정 entry); `?add=` writes nothing; no page
대제목 on `/portfolio` (R5 개정 ③); chrome/nav/account-menu are R8/R9 signed — out of round;
Korean-only reader surface; square corners, hairline elevation, reduced-motion floor.

**In play (this round's subject):** the D-day row's desktop geometry (finding 1 — the headline);
the holdings table's empty-cell answer, column rhythm and breakpoint; 지나간 마감's anchor-line
placement; the checked row's look; the sample surface's reset + conversion moments; the
notifications page's frame, heading and states; the two offers' (carry/migrate) surface tier —
R12's band grammar is available; every state in finding 14; the 480→767 consolidation.

## 4. Where to look — real paths, real data shapes

- Surface: `frontend/components/portfolio/*` (paths in §1), pages `frontend/app/portfolio/page.tsx`
  and `frontend/app/portfolio/notifications/page.tsx`.
- Copy: `frontend/components/portfolio/copy.ts` — every string + provenance; re-exports from
  lookup/event/chrome copy. New Korean = dated exception, logged in result.md.
- Payloads: `GET /portfolio` (account) / `GET /portfolio/sample` (anonymous) — `reference`,
  `holdings[]` (`corp_code`, `shares`, `corp_name`, `stock_code`, `rights.next` = pre-serialized
  countdown), `upcoming[]`/`past[]` = `RightsRow` (countdown, offering/convertible, `lapse` with
  `performance_rcept_no` on claimable ① rows). `GET /portfolio/notifications` — `address`,
  `lead_days` (choices 7/3/1/0, default 7+1).
- Signed record: `rounds/05-account/output/` (R5-3…R5-8), P7 corrections in
  `works/phases/active/P7/phase.md` (Q4, Q7, Q8 verbatim), R12's ladder in `rounds/12-auth/output/`
  (`account/r12-auth.css` `.aoffer`, Offers card), R11's table/card grammar in
  `rounds/11-lookup/output/` (② table → 390 cards, `.golink`, prompt→focus).

## 5. Required outputs (a round is incomplete without all of them)

Cards in group **`⏳ P8.S12 · Portfolio`**: **`portfolio/Home.html`** (account mode: holdings
table + both D-day sections at the real payload, edit/undo/empty/carry/migrate states),
**`portfolio/Sample.html`** (sample mode: banner, Q-D reset home, Q-E offer placement),
**`portfolio/Notifications.html`** (frame + all states incl. the R12-inherited error line, 계정
삭제 arming), **`portfolio/Mobile.html`** (390 — one 767px boundary, 44px floors). Plus
**`portfolio/r13-portfolio.css`** (geometry canon, tokens only) and **`portfolio/r13-parts.jsx`**
(parts + every string), **`result.md`** (decisions, departures, new-copy table with reasons),
**`build-prompt.md`** (implementation contract for `P8.S13`, §0 common rules, regression
checklist). No readme changes; cards stay in the project.

## 6. Open questions — posed to the session, not answered here

How the D-day row earns "organized" at 1440 without a false table (finding 1); what an empty
rights cell says without minting copy (2); whether the anchor line is page-level or per-section
(3); where 종료/reset lives so the sample stays honest (7, Q-D); whether the sample surface joins
the conversion ladder (8, Q-E); how the notifications page stops being frameless (12).

## 7. Operator setup + definition of done

Operator runs the Claude Design session against this handoff (project reads the repo — this file
is pushed). Done when: the six outputs exist under `⏳ P8.S12 · Portfolio` + `portfolio/`, every
§2 finding is either designed or explicitly declined in result.md, §2b decisions are recorded as
taken, no token changed, and the operator says the round is done in this session. Then the
orchestrator reads back with DesignSync, lands everything as-is under
`rounds/13-portfolio/output/`, and waits for the operator's literal signoff before `P8.S13`.
