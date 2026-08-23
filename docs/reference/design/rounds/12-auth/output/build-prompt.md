# R12 build-prompt — implementation contract (apply slice `P8.S11`)

Surfaces: `/auth/login`, `/auth/reset`, and the three conversion moments. Cards:
`account/Auth.html` · `account/Reset.html` · `account/Offers.html`. Geometry canon:
`account/r12-auth.css` (tokens only — copy declarations, do not re-derive). Copy + parts:
`account/r12-parts.jsx`. **No token change.**

## 0. Common rules

- **One breakpoint: 767px.** Delete the `@media (min-width: 480px)` block at the tail of
  `Auth.module.css`; everything mobile-side goes in `@media (max-width: 767px)`.
- Square corners, hairline borders, no shadow beyond the craft panel's own glow. Nothing
  `position: fixed`. No spinner anywhere on these surfaces.
- `--alert` is never used on this layer (failures render in `--ink-1`).
- Touch floor 44px; the two form controls are 48px.

## 1. `/auth/login` — page frame + panel

```
column        max-width 480px, centered, grid gap var(--space-4)   [.acol]
 ├ rail       nav > a 「← 관제 현황판」, mono text-sm, ink-2, min-height 44px, hover → --live
 ├ panel      CraftPanel, padding 24px (≤767: 20px 16px), inner grid gap var(--space-4)
 │   ├ flash?  로그아웃되었습니다 — surface-inset + border-soft, 10px 14px, text-sm ink-1
 │   ├ head    h1 (text-2xl/700/tracking-tight) + intro p (text-base ink-2)
 │   ├ form    grid gap 12px, noValidate
 │   │   ├ field  label row [label text-sm ink-2 | rule mono text-xs ink-3] + input
 │   │   │        input: 48px, surface-inset, 1px border-strong, text-md, padding-inline 14px
 │   │   ├ field  비밀번호 (rule 「8자 이상」 on 계정 만들기 only)
 │   │   └ submit 48px, width:100%, margin-top 4px, --live-solid, #fff, 600, text-md
 │   ├ line?   one p role="status": error → ink-1, notice → ink-2, text-base
 │   └ quiet   flex wrap, gap 0 20px; each button min-height 44px, text-sm ink-2, underline
 │             offset 3px; hover → ink-1; disabled → ink-3 + border-soft underline colour
 │
 │   (no PII inset — the 「미주알이 받는 것 …」 / 「저장하지 않는 것은 …」 lines are DELETED by
 │    operator instruction: drop PiiInset from both auth pages, remove the two constants
 │    from copy.ts, and withdraw the R5-1 상시 요소 assertion in its docstring)
 └ sample     section, border-top 1px border-soft, padding-top 16px;
              a text-base ink-1 underline min-height 44px + p text-sm ink-3
              text-wrap:balance; max-width 34ch
```

Focus: inputs `outline:2px solid var(--focus-ring); outline-offset:-1px`; buttons, quiet links and
the rail `outline-offset:2px`. Hover is colour only.

## 2. States

| State | What renders |
|---|---|
| idle | as above; no line |
| 확인 중… | submit label ← `PENDING_KO`, `disabled`, `opacity:.72`, `cursor:default`; quiet row buttons `disabled`; **no spinner, no overlay** |
| 오류 | one line under the form, `--ink-1`; never beside a field; login errors name no field |
| 알림 | same slot, `--ink-2` (재설정 보냈습니다 · 로그아웃되었습니다 is the *flash* band, see below) |

**Client-side gating, in this order** (`noValidate`, so the browser says nothing):

1. `email.trim() === "" || password === ""` → `이메일과 비밀번호를 입력해 주세요.` **(new)**
2. `!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email.trim())` → `이메일 주소 형식이 올바르지 않습니다.` **(new)**
3. `signup && password.length < 8` → `ERR_PASSWORD_TOO_SHORT_KO` (unchanged)
4. otherwise POST; `ApiError` → `authErrorKo(code)`; an unmapped code still renders no line.

Remove `required` and `pattern` from the inputs (they exist only to trigger the browser's own
messages); keep `type="email"` / `type="password"` and `autoComplete`.

**로그아웃 flash**: renders as the band **above the `h1`**, not in the line slot. Cleared by the
first change of either field, by a submit, or by navigation. No timer, no fade-out.

**재설정 trigger**: never `disabled` for an empty address. `onReset()` → if
`email.trim() === ""`, `emailRef.current?.focus()` and return (no request, no line); else post and
render `RESET_SENT_KO` in the notice slot. `disabled` only while `pending`.

## 3. `/auth/reset?token=…`

Same column, rail, panel, states (no PII inset). One field (비밀번호, rule 「8자 이상」), submit label =
`RESET_LINK_KO`. **No 이메일 field, no sample entry.**

- `password.length < 8` → `ERR_PASSWORD_TOO_SHORT_KO` (client, before the round trip).
- `invalid_reset_token` → `이 재설정 링크는 만료되었거나 이미 사용되었습니다 — 새 링크를 요청해 주세요.`
  **(new)** and, in that state only, one quiet-row button 「로그인」 → `/auth/login`.
- Success: sessions revoked, new session, `router.push(/portfolio)`. **No completion screen.**
- No `?token` → redirect to `/auth/login` (unchanged). Never state that a link *is* valid at render.

## 4. Conversion moments

**Hierarchy (surface = rank):** page numbers → offer band → detail one-liner → nav 로그인.

- **`ConversionOffer`** — drop `CraftPanel`; render the band: `surface-inset` + 1px `border-soft`,
  padding 16px 20px (≤767: 14px 16px), grid gap 8px. Head row = lead (text-base 600 ink-1) +
  `닫기` (44×44 min, text-sm ink-3, negative margin so the row keeps its 8px rhythm). Body text-sm
  ink-2 max-width 62ch. CTA: 44px, `--live-solid`, #fff 600 text-base, padding-inline 20px,
  `justify-self:start` (≤767 full width, centered). **No stay line** (deleted, see §5).
  **Placement on `/stocks/{corp}`**: after the last data section (놓친 돈 / the ① block if that is
  the last), **before** 집계 범위 and the provenance line. Conditions unchanged: anonymous only,
  `ready` (a per-holding value has rendered), one `sessionStorage` flag per session, dismissible.
- **`DeadlineOffer`** — unchanged component, R10's `.offer` geometry (text-sm ink-2 underline, 32px /
  44px ≤767, order 8 in the 390 stack). Renders nothing until the session is known; anonymous
  `이 마감 알림 받기 →` → `/auth/login`; signed in `보유 종목에 담기 →` → `/portfolio?add=…`; the
  caller's `days >= 0` gate stays.
- **nav 로그인** — untouched (R8).
- **Post-login landing**: `/portfolio` for every login, origin not carried. No new query params, no
  copy change to the offer.

## 5. Copy table (only these four are new; everything else is `copy.ts` as-is)

| Constant to add | Value |
|---|---|
| `PASSWORD_RULE_KO` | `8자 이상` |
| `ERR_FIELDS_REQUIRED_KO` | `이메일과 비밀번호를 입력해 주세요.` |
| `ERR_INVALID_EMAIL_KO` | `이메일 주소 형식이 올바르지 않습니다.` |
| `ERR_RESET_TOKEN_KO` | `이 재설정 링크는 만료되었거나 이미 사용되었습니다 — 새 링크를 요청해 주세요.` |

**Strings to DELETE (operator instruction, 2026-08-24)** — remove the constants and every render:
`PII_RECEIVES_KO`, `PII_NOT_STORED_KO` (and `PiiInset.tsx` itself), `CONVERT_STAY_KO`, and the
trailing clause of `CONVERT_BODY_KO` → `계정에 저장하면 마감이 다가올 때 이메일로 알립니다.`
The coverage-boundary caption on `/stocks/{corp}` (`COVERAGE_BOUNDARY_KO`) is struck **on the R12
card only** — do not remove it from the lookup surface unless R11's record is updated to match.

Map `invalid_email` → `ERR_INVALID_EMAIL_KO` and `invalid_reset_token` → `ERR_RESET_TOKEN_KO` in
`authErrorKo`, and update that function's header note (two of its three recorded gaps are now
closed; `csrf_required` and transport failures stay unmapped by design).

## 6. Regression checklist

1. `Auth.module.css` has exactly one media query and it is `max-width: 767px`.
2. The primary is `width:100%; height:48px` at every viewport; no `min-width:160px`, no
   `align-self:flex-start` on `.submit`.
3. Submitting an empty form on **both** modes and on the reset page produces a Korean line — no
   browser bubble, no silent submit. No `required`/`pattern` left on any auth input.
4. 「비밀번호 재설정」 is focusable and clickable with an empty address, and clicking it focuses the
   email input without a request; it is `disabled` only while pending.
5. 「8자 이상」 appears on 계정 만들기 and the reset page, and **not** on 로그인.
6. 로그아웃되었습니다 appears above the `h1`, once, and is cleared by the first keystroke.
7. Error lines use `--ink-1` / notices `--ink-2`; no `--alert` anywhere in the auth layer; no field
   border changes on failure.
8. Focus-visible is present on both inputs, the primary, both quiet buttons, the rail, the sample
   link, the offer CTA and 닫기.
9. The rail 「← 관제 현황판」 is on both auth pages; the sample entry is on 로그인 only; **no PII
   inset renders on either page** and `PiiInset` is gone from the tree.
10. At 390 the sample sub does not leave 「번.」 alone on its own line.
11. The offer band carries exactly three things: the session line, 닫기, one body line and the CTA —
    no closing reassurance line. `ConversionOffer` renders as an inset band (no brackets/glow), after 놓친 돈 and before 집계 범위,
    anonymous only, once per session, and dismissing it leaves nothing in its place.
12. `DeadlineOffer` renders nothing while the session is unknown; both labels are R10/R5-2's exact
    strings; every login lands on `/portfolio`.
