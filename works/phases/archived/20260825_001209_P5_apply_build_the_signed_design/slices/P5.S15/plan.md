# Plan — P5.S15: Auth surfaces (R5-1 / R5-2)

## Context

Read `works/phases/active/P5/phase.md` in full — binding here: S7 (the `/auth/*`
endpoints, structural error codes, the CSRF header, session cookie semantics), S8
(`/portfolio/sample` exists; the sample-entry links this slice renders), S10–S14
(primitives, chrome — `AccountSlot` links 로그인 → `/auth/login` — copy convention,
route map). Design chain: `frontend.md` supersessions → `SIGNOFF.md` (R5) → R5
`build-prompt.md` §Auth (R5-1) + §Conversion (R5-2) + the `result.md` *Proposed
copy* block (the signed auth-계열 strings — the copy inventory has no auth strings,
so the round record is their source; transcribe verbatim with citations) →
`docs/current/security.md`. **RESPECT THE DESIGN.**

Scope: the auth *surfaces* and the two conversion touchpoints. The 내 포트폴리오
surface itself, the account menu, and sample *mode* are `P5.S16`'s.

## Deliverables

1. **`/auth/login` — one panel, two modes** (로그인 / 계정 만들기) with the 전환
   link; fields email + password (≥8자 client hint per the signed copy — the rule
   itself is server-enforced); states exactly per R5-1: idle → **확인 중** (button
   text swaps + disabled, **no spinner**) → 오류 (one body line: 불일치 / 중복 가입
   / 8자 미만 — the login error never names a field; map S7's structural codes to
   the signed lines) → logged-in. On success: route to 내 포트폴리오 (S16's route —
   pick/record the path now, e.g. `/portfolio`; S16 builds the page; decide what an
   already-authenticated visit to `/auth/login` does and record it). 로그아웃 is
   immediate elsewhere (chrome/S16), but the "로그아웃되었습니다" one-time message
   belongs to whoever triggers it — record where it renders (R5 copy exists for it).
2. **The PII inset** — the permanent panel on the auth screen (three-line signed
   copy: "미주알이 받는 것: 이메일 주소와 비밀번호" + "저장하지 않는 것은 유출되지
   않습니다" + per the record) — always visible, both modes.
3. **재설정 flow** — request from the login panel (이메일 링크; the response is the
   signed "재설정 링크를 보냈습니다 — 메일함을 확인해 주세요." **regardless of
   membership** — S7's endpoint is already uniform); and the confirm surface the
   emailed link lands on (`/auth/reset/[token]` or similar — record): new password +
   submit → S7's confirm endpoint → logged-in or the structural error. The round
   record specs no dedicated confirm-page copy — compose it **only** from signed
   strings (the 8자 rule line, field labels, button verbs already in the record);
   if a needed sentence genuinely has no source, leave the surface structurally
   complete without it and flag it for `P5.S19` rather than inventing Korean.
4. **Sample entry links** — the two signed placements: login page bottom
   ("샘플 포트폴리오로 둘러보기" + its subline) and the landing footer line
   ("내 포트폴리오는 어떻게 보이나 — 샘플로 열어보기 →"). Both route to the sample
   experience (S16's mode — record the target route/param; the link may point at
   the portfolio route with a sample flag S16 implements; a dead link is not
   acceptable, so coordinate: render the links, and if the target page is S16's,
   the links land on the portfolio route which S16 fills — note the dependency in
   phase.md so S16 wires the mode).
5. **Conversion offers (R5-2)** — ① the offer panel below 조회 results: shown
   **after a value计算 renders** (sessionStorage flag, once per session,
   dismissible, never covers results; the signed copy incl. "이 보유량은 탭을 닫으면
   사라집니다" + "저장하고 알림 받기" + "지금처럼 로그인 없이 계속 쓸 수 있습니다");
   ② the one-line link under a detail page's D-day: "이 마감 알림 받기 →"
   (logged-in → "내 포트폴리오에 담기 →" — the logged-in swap may target S16's
   endpoint-backed flow; render the link states this slice can honestly support
   and record what S16 completes). Neither touchpoint gates anything; the nav
   로그인 stays quiet (no highlighting).
6. **Session awareness** — a client/server helper for "am I logged in" (S7's `me`
   endpoint; server components forward cookies — S10 note 13). The chrome's
   `AccountSlot` swap to the abbreviated-email menu is S16's; do not build it here,
   but leave the session helper where both can use it (record where).

## Constraints

- Copy verbatim from the R5 record with citations; structural codes → signed lines
  in one mapping module. **No invented Korean** (the reset-confirm rule above).
- All mutations through the typed client (CSRF header, `credentials: include`).
- 확인 중 = text swap + disabled only. No modals anywhere. Anonymous surfaces
  untouched — nothing new gates.
- Primitives/tokens/chrome untouched (except: the conversion touchpoints live on
  S14's 조회 page and S13's detail page — edit those surfaces minimally and record
  exactly what changed in them).
- No new dependencies.

## Validation

- `npm run build` + `typecheck` + `smoke` (add a terse case if the code-→copy
  mapping is testable without a browser); Python 113 untouched.
- Dev + headless-Chrome pass (localhost, live API + Postgres): signup → 확인 중
  state visible → logged-in redirect; logout message; wrong-password and
  unknown-email render the **same** line; duplicate signup line; 8자 미만 line;
  reset request → uniform message + console-transport link → confirm page → new
  password works; PII inset present in both modes; sample links present and
  routed; the 조회 offer appears once after a conversion, dismisses, stays gone
  this session, never gates; the detail one-liner in both auth states; nav 로그인
  unchanged. Mobile 390×844. Clean up test accounts; stop everything.
- `python3 scripts/workflow.py validate`.

## Wrap-up

`result.md`; `phase.md` *Findings & Notes* (the portfolio route decision, session
helper location, what S16 must complete: account menu, sample mode target, the
담기 flow) and *Doc impact* (`frontend`, `experience`, `security` — the auth UX as
implemented; `qa`). Structured verdict. No commits, no status transitions.
