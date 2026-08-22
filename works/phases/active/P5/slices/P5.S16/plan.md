# Plan — P5.S16: 내 포트폴리오 (R5-3 … R5-8)

## Context

Read `works/phases/active/P5/phase.md` in full — binding here: S8 (the nine
`/portfolio`/`sample`/`claim`/`notification` routes and their contract statements:
factors-not-products, the five-row sample, duplicate 409, 404-not-403), S14
(`lib/holding.ts` — **the** N주 multiplication site, and the sessionStorage
convention its 보유량 strip writes), S15 (the session seam
`lib/session*`/`useAuthState`, the `/portfolio` · `?sample=1` · `?add=` route
entries, the conversion touchpoints that point here), S10–S13 (primitives, chrome —
`AccountSlot` is the swap seam — copy convention). Design chain: `frontend.md` →
`SIGNOFF.md` (R5, incl. the post-gate R5-8 챙긴 돈 revision) → R5 `build-prompt.md`
§§Portfolio · D-day 목록 · 알림 · 샘플 · Chrome(logged-in) · Mobile + `result.md`
(the signed copy block and the sample composition table). **RESPECT THE DESIGN.**

This is the product's only gated surface. Anonymous/sample edits are
**localStorage, client-side** (R5: 로그인 없이 재방문에도 유지); server holdings are
the authenticated account's.

## Deliverables — `/portfolio` (the route S15 already targets)

1. **The page + gate** — authenticated: server-side load through S8's `/portfolio`
   (cookie-forwarding per S10 note 13). Anonymous, not in sample mode: the login
   gate (route to `/auth/login`; record the exact behavior — R5 gates only this
   surface). **No 「내 포트폴리오」 page title** — the header nav is the only
   location indicator (signed revision ③).
2. **Holdings section** — rows: 종목 / 보유량 (inline edit: input; confirm swaps
   the action column 수정·삭제 → 저장·취소, horizontal — revision ④) / 진행 중인
   권리 요약 (RightsChip + governing label + `D-n · date`) / actions. Input reuses
   the R4 primitives (mono right-aligned, `inputMode="numeric"`, comma groups,
   preset chips 100/500/1,000주) with the caption swapped to "계정에 저장 · 마감
   알림의 기준". 삭제 = immediate + 8초 되돌리기, no modal (implement the undo
   client-side against S8's endpoints; record how). Add-종목 flow: resolution via
   `/stocks?q=` (S8 deviation 2 — the one resolver); the `?add=` param from the
   detail 담기 link pre-fills it (record the handshake).
3. **Empty state + 세션 이월 제안 (R5-3)** — the signed empty copy; when
   S14's sessionStorage value exists, the inset row ("조회에서 입력한 {종목}
   {n}주가 이 세션에 남아 있습니다") + 담기/담지 않기 — never auto-saved; 담지
   않기 keeps the session value.
4. **D-day 목록 (the home view)** — two sections: 다가오는 마감 (D-day ascending) ·
   지나간 마감 (recent first), anchor date stated ("기준 YYYY-MM-DD (KST)" — the
   served reference), per-type governing anchors, everything upstream-computed.
   Amounts exactly per the R4 contract through `lib/holding.ts` (no second
   multiplication site): ① priced → tagged 금액; unpriced → 주수 + chip + 확정
   예정일; ②/③ → no per-holding money (② dilution context, ③ 2단계 문장). Past
   rows: inset chip `기간 지남 · D+n` / `통지 마감 지남 · D+n`, never alert. Past ①
   소멸 rows: the holding-basis tagged 금액 + "놓친 돈 상세 →" link (to
   `/stocks/{corp_code}`).
5. **챙긴 돈 체크 (R5-8)** — on past ① 소멸 rows: the checkbox "청약·매도로
   챙겼습니다"; checked → label 놓친 돈 → 챙긴 돈, same tagged amount, alert →
   live, caption "본인 표시 · 계정에 저장". Authenticated: S8's claim endpoints
   (key = the 실적보고서 rcept_no — S8 note 2). Sample/anonymous: localStorage
   ("이 브라우저(localStorage)에"). Never touches any aggregate; R4's conditional
   frame on 조회 is untouched.
6. **알림 설정** — its own view/section (record the route — the account menu links
   it): 수신 주소 (= the account email; 변경 via S8's `PATCH /auth/account`) · 시점
   칩 multiselect 7일/3일/1일/당일 (default 7일+1일 from S8's first-read defaults;
   empty selection allowed = no mail) · the KakaoTalk row — label + 「예정」 chip +
   "준비되면 이 자리에서 켤 수 있습니다", **no interactive control** · 로그아웃 ·
   계정 삭제 (immediate email wipe — S7's endpoint; the signed deletion sentence;
   no modal — decide the confirm interaction faithfully to "즉시", record it).
   Hidden entirely in sample mode.
7. **샘플 모드 (R5-4)** — entered via the S15 links (`?sample=1`): loads S8's
   anonymous `/portfolio/sample` (the five served rows — the record's table says 4;
   S8 note: 대동기어 also holds a lapsed ① — live data governs, record it),
   editable with **localStorage persistence** (survives revisits, no login);
   the inset banner ("샘플 포트폴리오 — 구성 예시입니다. …"), nav 「샘플」 chip +
   샘플 종료 replacing the 로그인 slot (via `AccountSlot` — this slice implements
   the swap), 종료 = wipe sample localStorage + return to pre-load state. No fake
   email, no 알림 anywhere in sample. On login with local edits: the 이전 제안
   (offer, never automatic — R5-3's pattern; record the flow).
8. **Logged-in chrome (R5 §Chrome)** — implement the `AccountSlot` swap: 로그인 →
   the abbreviated-email menu (mono, first 4 chars + … + domain end): 내 포트폴리오
   / 알림 설정 / 로그아웃 (immediate + the one-time "로그아웃되었습니다" — S15
   recorded where it renders; wire it). Mobile sheet: the divider + account rows
   (내 포트폴리오 with email alongside / 알림 설정 / 로그아웃). Desktop links and
   footer unchanged.
9. **Mobile ≤480px** — single column, ≥44px targets, no accordions; 지나간 마감 as
   summary rows (chip + one line); 종목 추가 as the bottom panel.

## Constraints

- Copy verbatim + cited (R5 build prompt + result.md); no invented Korean — if the
  계정 삭제 confirm or 이전 제안 needs a sentence with no source, use the signed
  ones only and flag any true gap for `P5.S19`.
- One math site (`lib/holding.ts`), one resolver (`/stocks?q=`), no second
  implementation of anything S8/S14 own. 조회 and 포트폴리오 may not disagree on a
  number — same factors, same code.
- localStorage/sessionStorage keys: follow/extend S14's convention; record every
  key (S19 will inspect them).
- Primitives/tokens untouched; chrome edits limited to the `AccountSlot` seam +
  mobile sheet account rows; no new dependencies.

## Validation

- `npm run build` + `typecheck` + `smoke` (terse new cases where DOM-free logic
  allows — e.g. the abbreviated-email formatter); Python 113 untouched.
- Dev + headless-Chrome pass (localhost, live stack): signup → empty state → 세션
  이월 (set a 조회 value first) → add the four record holdings → rows + D-day
  sections (한화솔루션 past-① 금액 consistent with 조회's at the same 주수 — the
  cross-check) → inline edit (저장·취소 swap) → delete + 8초 undo → 챙긴 돈 check
  (label/color flip, persists on reload) → 알림 설정 (chips default 7일+1일, empty
  allowed, KakaoTalk no control, 수신 주소 변경) → 로그아웃 (immediate + the
  message once) → sample mode anonymous (5 rows, banner, nav chip, edit persists
  across reload, 알림 hidden, 종료 wipes) → login-with-local-edits 이전 제안
  (offered, not automatic) → the account menu abbreviation → mobile 390×844.
  Delete test accounts; stop everything.
- `python3 scripts/workflow.py validate`.

## Wrap-up

`result.md`; `phase.md` *Findings & Notes* (storage keys, the AccountSlot/menu
implementation, flows S17/S19 need) and *Doc impact* (`frontend`, `experience`,
`security` — the gate + sample honesty; `qa`). Structured verdict. No commits, no
status transitions.
