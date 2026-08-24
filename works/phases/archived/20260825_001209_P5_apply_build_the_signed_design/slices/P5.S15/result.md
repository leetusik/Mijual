# Result — P5.S15: Auth surfaces + conversion offers + sample entry (R5-1 / R5-2 / R5-4)

`/auth/login` and `/auth/reset` exist, R5-2's two conversion touchpoints are mounted on the
surfaces the round places them on, and both signed sample entries are rendered. **0 new
dependencies, no primitive / token / chrome file touched, no Python file edited (suite
untouched at 113), and no Korean invented** — every string is transcribed with a citation in
`frontend/components/auth/copy.ts`.

The two things this slice adds that are not a page: **`lib/session.ts` + `lib/session.server.ts`**
(the "am I logged in" seam both halves of the app share, which `P5.S16` inherits rather than
re-writes) and **`authErrorKo`**, the one module that turns `P5.S7`'s structural codes into
R5's three signed body lines — and refuses to turn anything else into Korean.

## What landed

| path | what |
|---|---|
| `frontend/components/auth/copy.ts` | every R5 auth / conversion / sample string, one citation each, plus `authErrorKo` |
| `frontend/components/auth/AuthPanel.tsx` | 로그인 · 계정 만들기 in **one panel** with the 전환 링크, the four states, the 재설정 request |
| `frontend/components/auth/ResetConfirmPanel.tsx` | the page the emailed link lands on (new password → logged in) |
| `frontend/components/auth/PiiInset.tsx` | R5-1's permanent PII panel — both modes, both auth pages |
| `frontend/components/auth/SampleEntry.tsx` | the two signed entries (로그인 page bottom · landing footer line) |
| `frontend/components/auth/ConversionOffer.tsx` | R5-2 ① — the offer panel under 조회's results |
| `frontend/components/auth/DeadlineOffer.tsx` | R5-2 ② — the one-line link under a detail D-day, both states |
| `frontend/components/auth/useAuthState.ts` | the client hook both touchpoints use (lazy, `null` until answered) |
| `frontend/components/auth/Auth.module.css` · `index.ts` | one CSS module, one barrel |
| `frontend/app/auth/login/page.tsx` | the route; an **authenticated** visit redirects to 내 포트폴리오 |
| `frontend/app/auth/reset/page.tsx` | `?token=` (the backend's own link shape); **no token ⇒ redirect**, never a page |
| `frontend/lib/session.ts` · `lib/session.server.ts` | the session seam + the one-time 로그아웃 flash channel |
| `frontend/lib/auth.test.ts` | 2 `node:test` cases — the three signed lines, and that nothing else gets one |
| `frontend/lib/routes.ts` | **+`portfolio` · `reset` · `samplePath()` · `portfolioAddPath()`** (edited) |
| `frontend/components/lookup/StockView.tsx` | **+3 lines**: `valued` (via `convert()`) and `<ConversionOffer ready>` last (edited) |
| `frontend/components/event/Header.tsx` | **+1 element**: `<DeadlineOffer>` under the D-day, gated on `days >= 0` (edited) |
| `frontend/app/page.tsx` | **+1 element**: `<SampleEntry variant="landing" />` at the foot of the landing stack (edited) |

Exactly what changed in the three surfaces this slice does not own is listed above — no other
line of `P5.S12`/`P5.S13`/`P5.S14` moved, and `components/chrome/` (`AccountSlot` included) was
not touched at all.

## Validation

| command | outcome |
|---|---|
| `cd frontend && npm run build` | **pass** — 8 routes; `/auth/login` and `/auth/reset` both `ƒ` (request-time) |
| `cd frontend && npm run typecheck` | **pass** (`tsc --noEmit`, clean) |
| `cd frontend && npm run smoke` | **pass** — **6 → 8** `node:test` cases, ~85 ms, still no jest/vitest/jsdom |
| `.venv/bin/python -m pytest` | **113 passed**, 2.44 s — untouched, no Python file edited |
| `python3 scripts/workflow.py validate` | **pass** |

### Headless-Chrome pass (localhost:3000, live API on :8000, live Postgres)

**Three runs, 76 of 80 checks pass**, and each of the four is an over-strict assertion of mine
rather than a defect — every one was re-measured and is written out below. Screenshots in the
session scratch dir (`shots/auth-390.png`, `shots/offer-390.png`).

**Run 1 — the panel, its four states, 재설정 (33/34).**

- **idle** — 로그인 renders its title, R5's own intro line, the **PII inset (both signed
  lines)**, the 전환 링크 named 계정 만들기, and the sample entry + subline at the bottom.
  **Zero `position: fixed`** elements; the nav's three labels and its quiet 로그인 slot are
  byte-unchanged.
- **전환** — 계정 만들기 swaps the intro; the PII inset stays; 재설정 is absent (it is a
  로그인 affordance) and is **disabled** with no address in the field.
- **8자 미만** — the signed line renders **without spending a request** (measured: the
  `/api/auth/*` count did not move).
- **확인 중** — measured under 700 ms emulated latency: the submit button's own text becomes
  `확인 중…` and `disabled` is `true`. **No spinner element exists on the panel.**
- **로그인됨** — 가입 routes to `/portfolio` and `GET /auth/me` answers
  `{"authenticated":true,…}`; a later **authenticated visit to `/auth/login` redirects** to the
  same place.
- **불일치 is one line for both causes** — a wrong password and an unknown address produce the
  *identical* string, compared with `==` in the browser:
  `이메일 또는 비밀번호가 일치하지 않습니다.` **중복 가입** renders its own line.
- **재설정 is uniform** — a known and an unknown address both answer
  `재설정 링크를 보냈습니다 — 메일함을 확인해 주세요.`, and the link appeared **only in the
  server log** (`[mail:password_reset] … url=http://localhost:3000/auth/reset?token=…`).
  Following it: the confirm page renders from signed strings only, the **token is never
  rendered on the page**, 8자 미만 gets the same signed line, a valid password lands
  **logged in on `/portfolio`**, the old password is then refused with 불일치, and the **spent
  link** leaves the page stating nothing (the recorded gap below).
- **로그아웃되었습니다** renders once from the flash channel and is gone on the next load.

**Run 2 — the two touchpoints, the sample entries, 390×844 (34/37).**

- **No value ⇒ no offer, and no probe.** On 계양전기 (unpriced ①) with 500주 typed, the offer
  does not appear **and no `GET /auth/me` was requested at all**.
- **값 계산 직후 ⇒ the offer.** On 한화솔루션 with 500주 the page shows **679,575원** and the
  panel renders its four signed lines with `저장하고 알림 받기 → /auth/login`. It is the
  **last block of the stock view**, in normal flow, and sits **below** the total (measured
  rects). `닫기` removes it and the results are untouched; the flag
  `sessionStorage["mijual.convert.offer"] = "1"` keeps it from returning on a reload **or on
  another stock** in the same session. The nav's 로그인 stays `rgba(255,255,255,.68)` at
  weight 400 — no highlighting.
- **Anonymous only.** Logged in, with the flag cleared, the offer does not render.
- **The detail one-liner, both states.** Logged in: `내 포트폴리오에 담기 →` →
  `/portfolio?add=00102618`. Anonymous: `이 마감 알림 받기 →` → `/auth/login`, positioned
  **under the D-day**. Never both at once. A **past anchor (D+43)**, a **추후결정** event and a
  **철회** page carry neither (and the 철회 notice still renders).
- **The two sample entries.** The landing's line
  `내 포트폴리오는 어떻게 보이나 — 샘플로 열어보기 →` → `/portfolio?sample=1`, and it is **not
  in the global footer** (asserted against `footer a[href="/portfolio?sample=1"]`); the 로그인
  page's entry points at the same mode.
- **390×844** — auth panel: **no horizontal overflow**, every `main` target **≥44px**, zero
  fixed elements; 조회 with the offer: no horizontal overflow.

**Run 3 — the `next dev` second opinion (8/9).** The panel renders, **hydration completes**
(the 전환 링크 works), the 조회 offer appears beside the unchanged 679,575원, and there is **no
hydration warning**. Also measured here: `a@b` — an address `type="email"` accepts but the
service's own regex rejects — **cannot be submitted at all** (`checkValidity()` false, zero
`/api/auth/*` requests), so `invalid_email`, which has no signed Korean, is unreachable.

**The four non-passes, re-measured:**

1. *"no 원 amount"* on the unpriced ① — my grep matched the **footer's own** `DART 공시 원문`.
   Re-measured with a digits-then-원 pattern: **no money anywhere** on the page. `P5.S14`'s
   finding stands.
2. *"the offer is `position: static`"* — it is `relative`, which is **`CraftPanel`'s own
   idiom** (its corner brackets are absolutely positioned children, so the panel establishes a
   containing block). The 보유량 strip beside it measures identically. What matters was
   measured directly: `position` is neither `fixed` nor `absolute`, the page has **zero** fixed
   elements, and the panel is the last child in flow.
3. *"console clean"* (run 2) — the only entry was `/favicon.ico` **404**, which `curl` confirms
   is app-wide and pre-existing (there is no favicon asset in the repo; `frontend.md` records
   the gap). The `/portfolio` 404s are `P5.S16`'s route, and the one 401 is the deliberate
   wrong-password check.
4. *"console clean"* (run 3, dev) — React DevTools' suggestion and `[HMR] connected`.

One further console entry worth recording rather than hiding: on the **reset confirm page**
Chrome logs a `verbose` hint, *"Password forms should have (optionally hidden) username fields
for accessibility"*. It is not an error, and the honest fix is unavailable: the token identifies
the account **server-side only**, so this page does not know the address and cannot state one.
Recorded for `P5.S19`.

**Cleanup.** The test account and its reset grant were deleted through the ORM cascade;
`account / auth_session / password_reset / holding / lapse_claim / notification_pref` are all
back to **0**. `next dev`, `next start` and `uvicorn` were stopped.

## Decisions and readings, with their reasons

1. **The route the panel logs into: `/portfolio`.** The API's own noun for the layer
   (`GET /portfolio`), the same page-path-equals-contract-path rule `/stocks` follows. `P5.S16`
   builds the page, so **a successful login currently lands on a 404 inside the correct
   chrome** — the same deliberate choice `lib/routes.ts` already recorded for `login` and
   `eventPath` before their own slices, and the alternative (a stand-in page) would read as a
   dropped design element.
2. **An authenticated visit to `/auth/login` redirects to `/portfolio`.** R5 draws four auth
   states and the fourth — 로그인됨 — *is* the 2층; there is no signed logged-in variant of the
   auth screen, so rendering one would mean inventing both copy ("이미 로그인되어 있습니다") and
   a control. The redirect is server-side, over the request's own forwarded cookie.
3. **The sample entries point at `/portfolio?sample=1`; 담기 at `/portfolio?add={corp_code}`.**
   R5-4 draws the sample as a **loaded state of 내 포트폴리오** (inset 배너 + nav 「샘플」 칩 +
   샘플 종료), which is a mode, so it is a query on the layer's own route rather than a second
   surface; `GET /portfolio/sample` already serves it anonymously. `?add=` names the issuer
   because a 담기 needs a 보유량 the detail page never asks for — following a link **writes
   nothing**, and R5's own 종목 추가 panel collects the count. **`P5.S16` implements both.**
4. **The reset link's shape was not this slice's to choose.** `mijual.web.auth.RESET_PATH`
   already mails `{MIJUAL_APP_BASE_URL}/auth/reset?token=…`, so the page reads `?token=`, not a
   `[token]` path segment as the plan's example suggested. A visit **without** a token
   redirects to the panel: the token *is* the credential, R5 signs no copy for a reset page
   without one, and a redirect writes no Korean where a "링크가 올바르지 않습니다" page would.
5. **The session seam: two modules and a hook.** `lib/session.ts` (browser `fetchAuthState`,
   never throws, degrades to anonymous) · `lib/session.server.ts` (`readAuthState`, forwards
   the incoming `cookie` header — `P5.S10` note 13) · `components/auth/useAuthState.ts` (the
   hook; `null` means *not answered yet*, deliberately distinct from `{authenticated:false}`,
   so a two-state element renders **neither** until it knows). The split is mechanical:
   `next/headers` may not enter a client bundle, and a server module whose graph contains a
   React hook fails the build (it did, once).
6. **The 로그아웃 message travels as a *kind*, not a sentence.** `writeFlash("logout")` /
   `readFlashOnce()` over `sessionStorage["mijual.auth.flash"]`; the Korean stays in the cited
   copy module, and "1회 표시" is structural because the read consumes it. **`P5.S16` owns the
   writer** — 로그아웃 lives in the account menu it builds — and the auth panel is where this
   slice renders it, being the anonymous surface a 로그아웃 most obviously returns to.
7. **`authErrorKo` maps exactly three codes.** 불일치 / 중복 가입 / 8자 미만, and `null` for
   everything else — no fallback phrase, ever. The two codes that would otherwise be silent are
   held off structurally instead: `invalid_email` by the email field carrying the **service's
   own regex** as its `pattern` (verified unsubmittable), and `csrf_required` by `lib/api.ts`
   setting the header on every mutation. The remaining one is a real gap, below.
8. **The 8자 rule is checked client-side on 계정 만들기 and on the reset confirm — never on
   로그인.** On a login a short password is not a rule violation but a wrong password, and R5's
   line for that is 불일치; checking it there would have leaked "no account has this password
   shape" and contradicted the round. Where it does apply, the client states **the same signed
   sentence** the server's `password_too_short` maps to, one round trip sooner.
9. **The error line renders in body ink, never `--alert`.** `--alert` means expiring/lost and
   nothing else (`frontend.md`: "Red never encodes price movement"), so a red login error would
   spend the one hue this product reserves for a deadline. R5 says "오류(**본문** 한 줄)".
10. **The 조회 offer is anonymous-only, and lazy.** Its own body is "계정에 저장하면 …", so
    showing it to a reader who has an account would assert a state they are not in (R5's hard
    rule: 가짜 사용자 정체성 금지). R5-2 writes no logged-in variant of *this* panel — the
    logged-in swap it signs is the detail one-liner — so this is a **reading**, recorded for
    `P5.S19`. The session is probed only when the panel would otherwise render, so a 조회 page
    with no holding makes no request.
11. **"값 계산 직후" is asked of `lib/holding.ts`**, the product's one multiplication site — the
    same `convert()` the rows already call — so the offer cannot appear beside numbers that do
    not exist (an unpriced ① converts to `value: null` by construction). No second arithmetic
    was written.
12. **The detail one-liner is gated on a deadline still ahead** (`countdown.days >= 0`).
    "이 마감 알림 받기" under an anchor already behind the reference day would promise an alert
    nothing can send (the 시점 칩 are 7/3/1/0 days *before* a deadline), and a 추후결정 event has
    no 마감 at all. R5-2 places the line "상세 D-day 아래" without qualifying it, so the gate is
    a reading — recorded for `P5.S19`.
13. **The PII inset renders two lines, not three.** R5's copy list says "PII 패널 3행" while
    R5-1 quotes exactly two sentences; the third row is on the card, which stays in the Claude
    Design project. Nothing was invented to make up the count.
14. **`비밀번호 재설정` is composed, not written.** The record names the mechanism ("재설정 =
    이메일 링크") and never labels its control, so the trigger (and the confirm page's title and
    verb) compose the round's own two nouns — the same class of move `components/chrome/copy.ts`
    made for `© 미주알`, flagged the same way.

## Open items this slice hands on

- **⚠ `invalid_reset_token` has no signed line.** An expired or already-spent link leaves the
  confirm page idle and **states nothing**. R5 signs three error cases and this is not one of
  them; the plan's own instruction was to leave the surface structurally complete rather than
  invent Korean. A reader can request a fresh link from the panel. **Operator/`P5.S19` call.**
- **The browser states its own refusal in its own language.** The email `pattern` guard makes
  `invalid_email` unreachable, and Chrome on this machine reported *"Please match the requested
  format."* — a UA string, the same class as the framework's English 404 (`P5.S13` note 4).
- **The sample subline says 4건; the live sample renders 5 rows** (`P5.S8` note 14 — 대동기어
  also holds an exposable ① that lapsed). The sentence describes the *composition*, which is
  still four pinned disclosures, and it is signed copy: transcribed verbatim. `P5.S16`/`P5.S19`
  will see the difference on the page.
- **Every event detail page now makes one `GET /auth/me`.** It is what renders the signed
  two-state line, it answers 200 either way, and it gates nothing — but if `P5.S16` decides the
  chrome should probe once per page load for the account menu, that probe should replace this
  one rather than sit beside it. Both would read `lib/session.ts`.
- **Chrome's password-form a11y hint on `/auth/reset`** (no username field can honestly be
  supplied — the page does not know the address).
