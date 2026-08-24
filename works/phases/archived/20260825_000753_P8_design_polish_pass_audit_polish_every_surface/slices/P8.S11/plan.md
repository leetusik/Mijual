# P8.S11 — Apply R12: auth (로그인 · 계정 만들기 · 비밀번호 재설정) + conversion moments

Faithfully implement the **signed R12 round** on the running product. RESPECT THE DESIGN — never
drop, simplify, restyle, or "improve" a signed element. The contract is
`docs/reference/design/rounds/12-auth/output/build-prompt.md` (§0–§6); the geometry canon is
`output/account/r12-auth.css` (copy declarations, do not re-derive); copy + structure reference is
`output/account/r12-parts.jsx` and the three cards. Decisions and context: `phase.md`
§"R12 landed spec — SIGNED OFF 2026-08-24" (binding decisions 1–13) and the SIGNOFF.md R12 entry.

## Files (survey, verify at start)

- `frontend/components/auth/`: `AuthPanel.tsx`, `ResetConfirmPanel.tsx`, `Auth.module.css`,
  `copy.ts`, `PiiInset.tsx` (DELETE), `ConversionOffer.tsx`, `DeadlineOffer.tsx` (do not touch
  behaviour/labels), `SampleEntry.tsx`, `useAuthState.ts`, `index.ts`
- `frontend/app/auth/login/`, `frontend/app/auth/reset/`
- `frontend/components/lookup/StockView.tsx` — ConversionOffer placement only (band lives in the
  auth component; StockView decides where it renders)
- `docs/reference/design/copy-inventory.md` — R12 tail (new/changed/deleted strings)

## Build order

1. **copy.ts** — add `PASSWORD_RULE_KO` 「8자 이상」, `ERR_FIELDS_REQUIRED_KO` 「이메일과 비밀번호를
   입력해 주세요.」, `ERR_INVALID_EMAIL_KO` 「이메일 주소 형식이 올바르지 않습니다.」,
   `ERR_RESET_TOKEN_KO` 「이 재설정 링크는 만료되었거나 이미 사용되었습니다 — 새 링크를 요청해
   주세요.」. Map `invalid_email` / `invalid_reset_token` in `authErrorKo`; update its header note
   (two of three recorded gaps closed; `csrf_required` + transport stay unmapped by design).
   DELETE `PII_RECEIVES_KO`, `PII_NOT_STORED_KO`, `CONVERT_STAY_KO`; `CONVERT_BODY_KO` → 「계정에
   저장하면 마감이 다가올 때 이메일로 알립니다.」 Note the R5-1 상시 요소 withdrawal where the PII
   docstring asserted it. **`COVERAGE_BOUNDARY_KO` and the lookup surface stay untouched** (P8 Q39
   default: caption keeps rendering on /stocks pages).
2. **AuthPanel** (both modes) — `noValidate`; remove `required`/`pattern` (keep `type`,
   `autoComplete`); client gating in the signed order (empty → fields-required; regex
   `/^[^@\s]+@[^@\s]+\.[^@\s]+$/` on trimmed email → invalid-email; signup && len<8 → short; else
   POST). 「8자 이상」 via `.arule`-equivalent on the 비밀번호 label row **in signup mode only**.
   재설정 trigger: never disabled for an empty address — `email.trim()===''` → focus the email
   input and return (no request, no line); disabled only while pending. One `p role="status"` slot:
   error ink-1 / notice ink-2. 로그아웃되었습니다 → flash band **above the h1** (`.flash`
   geometry), cleared by first field change, submit, or navigation; no timer. Remove PiiInset from
   the tree (and delete `PiiInset.tsx` + its export). Sample entry: 로그인 only (unchanged rule);
   sub gets `text-wrap:balance; max-width:34ch`.
3. **Auth.module.css** — delete the `@media (min-width:480px)` block (lines ~323–331); fold what
   mobile needs into `@media (max-width:767px)`; primary `width:100%; height:48px` at every
   viewport (no `min-width:160px`, no `align-self:flex-start`); label row = flex baseline
   space-between with the mono text-xs rule token; rail 「← 관제 현황판」 as the column's first row
   (nav > a, mono text-sm, ink-2, min-height 44px, hover → --live); flash band; focus-visible per
   canon (inputs 2px --focus-ring offset −1; buttons/quiet/rail offset 2; hover = colour only).
   Follow r12-auth.css values; module widths on shared-class elements at order-independent
   specificity if the S9 lesson applies.
4. **ResetConfirmPanel / app/auth/reset** — one 비밀번호 field + 「8자 이상」 rule; NO 이메일 field,
   NO sample entry; rail present; client len<8 check before the round trip; `invalid_reset_token` →
   `ERR_RESET_TOKEN_KO` + quiet 「로그인」 → `/auth/login` rendered **only** in that state; success:
   existing behaviour (sessions revoked, new session) then `/portfolio`, no completion screen; no
   `?token` → redirect (unchanged).
5. **ConversionOffer** — drop the CraftPanel wrapper; render the inset band per canon (`.aoffer`
   geometry: surface-inset + 1px border-soft, 16/20 padding, head row = session lead + 닫기 44×44
   negative-margin, one body line max 62ch, CTA 44px --live-solid, justify-self start / full-width
   centered ≤767). No stay line. In `StockView.tsx`, place it **after the last data section
   (놓친 돈, or the rights block when it is last), before 집계 범위 and the provenance line**.
   Conditions unchanged: anonymous only, after a per-holding value rendered, once per session
   (existing sessionStorage flag), dismissible, dismissal leaves nothing.
6. **DeadlineOffer + nav** — verify untouched (labels exact, renders nothing until session known,
   `days >= 0` gate, R10 geometry; nav 로그인 = R8). Do not edit unless a regression check fails.
7. **copy-inventory.md** — R12 tail: 4 new constants, 3 deletions, 1 body change, the two
   `authErrorKo` mappings, R5-1 withdrawal note.

## Don'ts

- No token changes; no new deps; no `--alert` in the auth layer; nothing `position:fixed`; no
  spinner. No SearchRow/Citation/event-component changes. Do not touch `COVERAGE_BOUNDARY_KO` or
  any lookup copy (Q39 default). Do not change auth API routes, session logic, or CSRF handling —
  this is presentation + client gating + copy only. Korean-only reader-visible text.

## Verification (operator runtime manifest — operations doc)

- Dev on `http://127.0.0.1:3000` **and** the tailnet origin; production build when behaviour may
  differ (this slice deletes a media query and changes form semantics → **do** run the prod build
  per the S9 scratch-copy recipe if dev/prod could diverge). 390px via the iframe harness or
  devtools; also ~600px (the retired 480–767 window).
- Run the signed regression checklist build-prompt §6 items 1–12 and record each result in
  `result.md`. Key functional checks: empty submit on 로그인/계정 만들기/재설정 → Korean line, no
  browser bubble; 재설정 click with empty address → focus, no request (network tab); flash band
  clears on first keystroke; offer band on an anonymous `/stocks/{corp}` with a holding set —
  placement, 닫기, session flag; logged-in and anonymous DeadlineOffer labels; login lands
  `/portfolio`.
- `cd frontend && npx tsc --noEmit` (or the repo's check) + a clean `next build`.
- Tests: lightweight — extend an existing small suite only if one already covers auth gating;
  otherwise verify by running the product (workspace rule: minimal high-value cases only).

## Notes & return

- Append to `phase.md`: durable cross-slice notes (§"P8.S11 — R12 applied"), any new operator
  questions to `## Operator Questions` (numbered after Q39), Doc impact one-liners (design-record
  pointer moves, copy-inventory tail, R5-1 withdrawal).
- Write `result.md` from scratch: what changed per file, checklist outcomes, browser evidence
  (origins + viewports + prod), departures if any (there should be none — escalate to a question
  instead of improvising).
- Return verdict `done` only with the checklist green in the operator runtime; `needs_operator` if
  the manifest runtime cannot be reached; never commit or transition state.
