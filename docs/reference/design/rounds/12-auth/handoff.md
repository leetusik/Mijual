# Design Handoff — Round 12: Polish — Auth (로그인 · 계정 만들기 · 비밀번호 재설정) + conversion moments

- Round: **R12** (P8 polish pass, surface 5 of 8) · slice `P8.S10` · written 2026-08-24
- Status: OUT — awaiting the design session (Claude Design + operator)
- Repo: `leetusik/Mijual` via Connect GitHub (main branch, pushed at handoff commit)
- Builds on: **R5 (R5-1 auth = email + password, one panel / two modes / four states, the permanent
  PII inset; R5-2 the conversion moments — `ConversionOffer` after the first per-holding value,
  `DeadlineOffer` under the detail D-day, the quiet nav 로그인; R5-4 sample entry; R5-8 챙겼습니다),
  R8 (chrome: the account slot, 로그인 link, the sample's 로그인 여부 state — 샘플 chip/종료 retired),
  R10 (the 담기 label 「보유 종목에 담기 →」), R11 (the lookup surface the offer sits on)** as signed,
  plus the P7/P8 operator overrides in `SIGNOFF.md`. Those rounds are **locked context** except where
  this handoff explicitly opens them; R12 is a **polish round — no new features** — and what it signs
  supersedes the parts of R5 it touches.

## 1. Product context

`/auth/login` — one craft panel, two modes (로그인 / 계정 만들기, switched by a quiet link whose label
is the other mode's name), fields 이메일 · 비밀번호 (48px), the primary button (label = mode; 「확인 중…」
while pending, disabled, no spinner), one error/notice line under the form (never beside a field:
불일치 / 중복 가입 / 8자 미만 / 「재설정 링크를 보냈습니다 — 메일함을 확인해 주세요.」), the quiet row
(계정 만들기 | 비밀번호 재설정 — the latter disabled until an address is typed, and answering 보냈습니다
for any address by design), the **permanent PII inset** (「미주알이 받는 것: 이메일 주소와 비밀번호」 /
「저장하지 않는 것은 유출되지 않습니다」), and below the panel the sample entry (「샘플 포트폴리오로
둘러보기」 + sub). Logged-in → redirect to `/portfolio`. `/auth/reset?token=…` — the emailed link:
h1 「비밀번호 재설정」, one 비밀번호 field, the button, the PII inset; no token → redirect to login.
Conversion moments (R5-2, all anonymous-only): `ConversionOffer` panel on `/stocks/{corp}` after the
first per-holding value (sessionStorage once-per-session, 「닫기」, CTA 「저장하고 알림 받기」 →
`/auth/login`, 「지금처럼 로그인 없이 계속 쓸 수 있습니다」), `DeadlineOffer` on the event header
(「이 마감 알림 받기 →」 → `/auth/login`; logged in → 「보유 종목에 담기 →」), the nav 로그인 link (R8).

The orchestrator walked the surface on 2026-08-24 in the operator's runtime — **the anonymous
panel via the server-rendered page captured without a session** (the operator's Chrome is logged in
and `/auth/login` redirects; logging the operator out was not done without their say-so), desktop
1456px + 390px. Not walked: the pending / error / notice states (reachable only by submitting
credentials — read from code), the anonymous conversion moments on `/stocks` and `/events`, the
nav 로그인 link, 로그아웃 → 「로그아웃되었습니다」. Findings below; the operator's gate answers are
**direction** and **REFERENCE — data, not a proposal**. Claude Design + the operator decide how.

## 2. Scope checklist — what this round must cover

Default from the P8 rhythm: **every walk finding → fix, Claude Design decides how**, except where
§2b names an operator decision.

- [ ] **1 · 「비밀번호 재설정」 is disabled with no reason** until an address is typed (grey text, no
      hint, nothing happens on click) — a first-time user who forgot their password reads a dead
      link. How the affordance reads before and after the address exists.
- [ ] **2 · No password rule before the error** — 계정 만들기 and the reset page say 「8자 이상」 only
      as an error after submit (R5-1: 8자 이상, no other rule). Whether a rule is stated up front
      (new copy → §2b Q-C) or the error stays the only place.
- [ ] **3 · Reset page context** — `/auth/reset?token=…` names no account and no state for a bad or
      expired token beyond the API's error line; confirm what the reader is told (and not told —
      가입 여부 비노출 stays).
- [ ] **4 · Chrome's English validation bubble (P7 Q12, routed here)** — `required` + `type=email`
      produce the browser's own English messages in a Korean-only surface. §2b Q-A.
- [ ] **5 · Primary button geometry** — 160px min-width, left-aligned under full-width inputs on
      desktop (full-width at 390). Confirm or re-cut against the other surfaces' primary (R4/R11
      조회 48px, R10 환산 44px).
- [ ] **6 · Sample entry sub wraps with an orphan** at 390 (「…클릭 한 / 번.」) — keep-all / balance.
- [ ] **7 · Page composition** — the 440px panel floats centered with no rail/crumb (every other
      surface carries 「← 관제 현황판」); the sample entry hangs below a hairline. Confirm the page
      frame (§2b Q-D).
- [ ] **8 · Breakpoint** — `Auth.module.css` switches at 480px; R10/R11 settled on the single 767px
      boundary. One rule (R10 §0 common rules).
- [ ] **9 · States** — idle / 확인 중… / error line / notice line: confirm the four states' look on
      both modes and the reset page, incl. focus-visible on inputs and the quiet links, hover on
      the quiet row, the disabled primary (`disabled` + label swap) — drawn, since they cannot be
      walked without credentials.
- [ ] **10 · 로그아웃 → 「로그아웃되었습니다」** — where the notice lands and for how long (not walked).
- [ ] **11 · Conversion moments as a set** — `ConversionOffer` (after the first value on R11's new
      lookup page: placement under the identity panel / 놓친 돈? R5-2 says 값 계산 직후), `DeadlineOffer`
      (R10 header, 「이 마감 알림 받기 →」 only while `days >= 0`), nav 로그인 (R8): one hierarchy, and
      **where the reader lands after logging in from an offer** (today: `/portfolio`, the stock or
      deadline they came from is not carried — §2b Q-B).
- [ ] **12 · PII inset** — two lines in an inset; confirm tier/voice next to the R11 caption tier
      (「서버 전송 없음」 moved to mono `text-xs`).
- [ ] **13 · Heading semantics** — h1 = mode label (로그인 / 계정 만들기 / 비밀번호 재설정); PII `aside`;
      sample entry `section` unheaded. Confirm outline.
- [ ] **Cards refreshed for everything above, desktop (1512/1280) and 390px.**

### 2b. Operator decisions (take at the gate or in the session)

- **Q-A · The English validation bubble (P7 Q12).** (a) keep the browser's native messages (they
  follow the reader's browser language; zero copy), (b) `noValidate` + one Korean line in the
  existing error slot (new copy — dated exception), (c) `noValidate` and let the API's existing
  Korean errors answer (empty field → the server's 불일치 line; no new copy, but a less precise
  message). Default: **(c)** if the session agrees the existing lines cover it; else (b).
- **Q-B · Return path after logging in from an offer.** Today every login lands on `/portfolio`.
  Carrying the origin (back to the stock with the value, or to the event) is arguably a feature;
  stating it honestly in the offer copy is polish. Default: **keep `/portfolio`; the offer copy may
  say where it leads** — no new query plumbing unless the operator calls it polish.
- **Q-C · A password rule stated up front** (「8자 이상」 as a hint under the field) — new copy
  (dated exception) or keep error-only. Default: **session decides**; if a hint, one string.
- **Q-D · Page frame** — a rail/crumb (「← 관제 현황판」) on the auth pages like every other surface,
  or the bare centered panel as R5 drew it. Default: **session decides** (no new copy either way).

**Explicitly NOT in this round:** the auth mechanics and endpoints (email+password, reset by link,
8-char rule, 가입 여부 비노출, session cookie), the account menu (R8/P8.S5.5), `/portfolio` and
알림 설정 (R13), the sample portfolio contents (R13), any new field or flow (no OAuth, no code
login, no "remember me").

Cross-cutting (every round): Korean-only surface; mobile-first; a11y/reduced-motion floor; no new
features.

## 3. Locked vs. in play

**Locked:** R1 tokens/type/spacing/motion/square-hairline system and `.cosmos`; R5-1's mechanics
and its copy (intro lines, labels, the five error/notice strings, PII inset lines, 「확인 중…」,
「로그아웃되었습니다」); R5-2's existence of the three conversion moments and their copy; R5-4's
sample entry copy; R8 chrome; R10's 담기 label; the anonymous path never blocked, no gate screen,
no forced modal.

**In play:** everything in §2 — the disabled-reset affordance, rule-before-error (Q-C), reset page
context, the validation bubble (Q-A), primary geometry, 390 wraps, page frame (Q-D), breakpoint,
the drawn four states + focus/hover, 로그아웃 notice placement, the conversion set's hierarchy and
post-login landing (Q-B), PII inset tier, heading outline. New Korean copy only where §2b opens it
(dated exception 2026-08-24), each string listed in `result.md` with its reason. Token change, if
any, = a new `foundations/tokens.css` from the session.

## 4. Where to look — real paths, real data shapes

- **Page as built:** `frontend/app/auth/login/page.tsx` (redirects when authenticated),
  `frontend/app/auth/reset/page.tsx` (no token → login), `frontend/components/auth/` — `AuthPanel.tsx`
  (modes, states, quiet row, `onReset`), `ResetConfirmPanel.tsx`, `PiiInset.tsx`, `SampleEntry.tsx`,
  `ConversionOffer.tsx` (sessionStorage once, `eligible`), `DeadlineOffer.tsx` (`auth === null` →
  nothing; anonymous → 「이 마감 알림 받기 →」), `useAuthState.ts`, `copy.ts` (every string with its
  citation), `Auth.module.css` (480px block at the tail); `frontend/components/chrome/AccountSlot.tsx`
  (the anonymous 로그인 link, desktop + mobile rows); `frontend/lib/session.ts` / `session.server.ts`;
  `frontend/lib/api.ts` (`login`, `signup`, `requestPasswordReset`, `confirmPasswordReset` — names as
  in the file), `authErrorKo` in `auth/copy.ts`.
- **Landed records:** `docs/reference/design/rounds/05-account/output/` (R5 `result.md` §6 decisions
  R5-1/R5-2/R5-4, `build-prompt.md` §Auth / §Conversion / §Sample), `rounds/08-foundations-chrome/
  output/` (account slot, 로그인 link, the retired 샘플 chip), `rounds/10-event-detail/output/`
  (DeadlineOffer placement under the D-day, §1), `rounds/11-lookup/output/` (the page the
  ConversionOffer now sits on). Overrides: `docs/reference/design/SIGNOFF.md` (R5, R8, R10, R11).
- **Walk findings + answers:** `works/phases/active/P8/phase.md` §"R12 walk — surface 5" (recorded
  when the running apply slice P8.S9 returns; the handoff is pushed first) and its `## Operator Questions` routing (P7 Q12 → here).
- **Grounding:** `docs/reference/design/grounding/copy-inventory.md` (auth strings registered by R5),
  `states-and-trust.md`.

Missing real content → ask for it; do not invent it.

## 5. Required outputs (a round is incomplete without all three)

1. **The card set** — line-1 `@dsCard` markers, review-time group **`⏳ P8.S10 · Account`**:
   - `account/Auth.html` — 로그인 / 계정 만들기, the four states (idle · 확인 중… · error · notice),
     the quiet row incl. the reset affordance before/after an address, focus/hover, PII inset,
     sample entry, page frame (Q-D), desktop + 390
   - `account/Reset.html` — the token page: idle · pending · error (bad/expired token, 8자 미만) ·
     done; 390
   - `account/Offers.html` — the conversion set: `ConversionOffer` on the R11 lookup page (placement
     + states: shown / 닫기), `DeadlineOffer` on the R10 header (anonymous vs logged-in), nav 로그인;
     the post-login landing as decided (Q-B); 390
   - `foundations/tokens.css` — **only if tokens change**

2. **A record** — `result.md` (what changed vs R5, departures, Q-A–D as taken, any new string with
   its reason).

3. **An implementation contract** — `build-prompt.md` (geometry, states, copy table, breakpoint, a
   regression checklist for the apply slice).

**Definition of done: the cards appear in the Design System pane** under `⏳ P8.S10 · Account`, and
the record + contract exist.

## 6. Open questions — posed to the session, not answered here

1. How a disabled 「비밀번호 재설정」 tells the reader what it needs.
2. Whether a password rule belongs before the error.
3. The four states drawn, incl. focus-visible, on a surface whose states can only be seen by
   submitting.
4. The conversion set's hierarchy on the new lookup page and the detail header.
5. One breakpoint, one page frame.

## 7. Operator setup + definition of done

Same project ("Mijual Design System"), Connect GitHub — pull latest `main`. When the cards are up
and the record + contract exist, tell the orchestrator to resume; read-back, landing, SIGNOFF, and
the regroup (retiring `⏳ P8.S10 ·`) follow. Approval must be literal. Then `P8.S11` applies R12.
