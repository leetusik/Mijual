# R12 result — Polish: Auth (로그인 · 계정 만들기 · 비밀번호 재설정) + 전환 제안

- Round **R12** · slice `P8.S10` · surface 5 of 8 · session 2026-08-24
- Handoff: `docs/reference/design/rounds/12-auth/handoff.md` (commit 05b2ca0)
- Cards (review group `⏳ P8.S10 · Account`): `account/Auth.html` · `account/Reset.html` ·
  `account/Offers.html` — geometry canon `account/r12-auth.css`, parts + copy `account/r12-parts.jsx`
- **토큰 변경 없음** (no new `foundations/tokens.css`)
- Supersedes the parts of R5 it touches (R5-1 auth panel, R5-2 conversion placements, R5-4 sample
  entry geometry); `account/Auth.html` replaces the R5 card at the same path.

## 1. Operator decisions as taken

| | Question | Taken |
|---|---|---|
| **Q-A** | Chrome's English validation bubble (P7 Q12) | **(b)** — `noValidate` + Korean lines in the existing error slot. **Two** lines, not one (below). The handoff's default (c) was rejected: on 계정 만들기 an empty/malformed address maps to `invalid_email`, which has **no signed Korean** (`authErrorKo` → `null`), so the reader would meet a submit that renders nothing at all. |
| **Q-B** | Return path after logging in from an offer | **Default kept** — every login lands on `/portfolio`; the origin is not carried (that is query plumbing = a feature). The offer copy is **not** extended to say where it leads: R5-2's locked body already states what saving does, so naming the destination would add a new sentence to a locked paragraph to say the same fact twice. |
| **Q-C** | A password rule up front | **Yes, one token** — 「8자 이상」, mono `text-xs`, on the 비밀번호 label row. **계정 만들기 + 재설정 페이지에만**; 로그인 has no rule line (there a short password is not a rule violation but a wrong password → 불일치). |
| **Q-D** | Page frame | **Rail** — 「← 관제 현황판」 as the 480px column's first row; the panel stays R5's centered panel. Reason is not consistency but the exit: an anonymous reader who arrived from an offer and decides against an account had no way out of this page. No new copy (the rail line is shared by every surface). |

## 2. The 13 findings — what changed

1. **재설정 disabled with no reason → the disabled state is retired.** The control stays live with an
   empty address; pressing it **moves focus to the 이메일 field** instead of posting. Same grammar as
   R11's 놓친 돈 prompt (a control that focuses the strip input) — the system already had a way to say
   "what I need" without a sentence. `disabled` now exists only while a request is in flight.
2. **No rule before the error → Q-C.** 「8자 이상」 on the label row (계정 만들기 · 재설정).
3. **Reset page context.** The page tells: what it is (`h1`), the rule, what failed, what 미주알
   receives (PII inset). It does **not** tell: the account's address (the link is the credential —
   re-printing the address widens the exposure surface), 가입 여부, or the link's remaining validity
   (no served value → not invented). New copy for `invalid_reset_token` (was a silent failed submit,
   recorded as a gap in `copy.ts`), plus a 「로그인」 line back to where a new link can be requested.
   Success is **not a screen**: sessions are revoked, a new one is issued, `/portfolio`.
4. **Validation bubble → Q-A (b).**
5. **Primary button geometry → full-width 48px at both breakpoints.** 160px + left-align retired.
   R4/R11's 조회 48px is a *row-mate* beside an input; this button is the form's last field under two
   stacked full-width inputs. Same height, different reason for the width.
6. **Sample sub orphan at 390** → `text-wrap: balance` + body-level `keep-all` + `max-width:34ch`.
7. **Page frame → Q-D (rail).**
8. **Breakpoint 480 → 767px**, one rule (R10 §0), with the same declarations scoped to `.m390`.
9. **The four states drawn** (both modes + reset): idle → 확인 중…(label swap + `disabled`, opacity
   .72, no spinner) → 오류(one body line, `--ink-1`) → 알림(same slot, `--ink-2`). One slot, one
   `role="status"`. `--alert` is never used on a failure. Focus-visible drawn: inputs 2px
   `--focus-ring` `offset:-1`, buttons/quiet links `offset:2`, rail the same; hover = colour only.
10. **로그아웃되었습니다 → above the `h1`**, its own inset band. The line under the form belongs to
    *this* form's answers; a receipt for an action taken elsewhere reads there as a response to a
    submit that never happened. **No timer** — the first keystroke, a submit, or navigation clears it.
11. **The conversion set as one ladder** (surface = rank): page numbers > offer **inset band** (no
    brackets, no glow, one 44px CTA, 닫기) > detail header's one-line text link (R10's secondary rank)
    > nav 로그인 (quietest, R8 untouched). `ConversionOffer`'s place on R11's page: **after the last
    data section (놓친 돈), before 집계 범위/프로비넌스** — not between data sections (breaks the
    board's rhythm and pushes 놓친 돈 below an offer), not at the very end (that is the provenance
    slot; an offer there reads as a footer banner). Post-login landing: Q-B.
12. **PII inset → deleted** (operator instruction, in session). 「미주알이 받는 것: 이메일 주소와
    비밀번호」 / 「저장하지 않는 것은 유출되지 않습니다」 are removed from **both** auth pages, which
    withdraws R5-1's 「PII 패널은 로그인 화면 상시 요소」 clause. The tier question the finding asked
    is closed by the removal; the `.pii*` rules stay in the canon unused, so a later round can
    restore the block without re-deciding its tier.
13. **Heading outline** — `h1` = mode name only (로그인 / 계정 만들기 / 비밀번호 재설정); intro `p`;
    PII `aside` (unheaded); sample entry unheaded `section`; error/notice one `p role="status"`; mode
    switch + 재설정 are `button` (neither navigates); rail is `nav`.

## 3. New copy — 4 strings, dated exception 2026-08-24

| String | Where | Reason |
|---|---|---|
| `8자 이상` | 비밀번호 label row (계정 만들기 · 재설정) | Q-C. Not a sentence — R5-1's own rule text ("비밀번호 8자 이상") as the field's constraint, so the 8자 error is no longer the first place the rule is stated. |
| `이메일과 비밀번호를 입력해 주세요.` | error slot, both modes | Q-A (b). With `noValidate` the browser's English bubble is gone; an empty field needs one Korean line. |
| `이메일 주소 형식이 올바르지 않습니다.` | error slot, both modes | Q-A (b). Also closes `copy.ts`'s recorded gap: `invalid_email` had no signed Korean. |
| `이 재설정 링크는 만료되었거나 이미 사용되었습니다 — 새 링크를 요청해 주세요.` | reset page error slot | finding 3. `invalid_reset_token` was a recorded gap — the submit failed silently. Same class as R10's Korean 404. It does not say **which** (expired vs spent) — that distinction is token state. |

No other string on these surfaces is new; everything else is transcribed from
`frontend/components/auth/copy.ts` (itself transcribed from the landed R5 record).

## 4. Departures from the handoff / earlier rounds (logged)

1. **Q-A returns two lines where the question said "one Korean line"** — 빈 입력 and 형식 오류 are
   different facts, and the second one closes a gap the code had already recorded.
2. **The handoff's Q-A default (c) was not taken** (reason in §1).
3. **`disabled` on 재설정 is retired, not re-labelled** — finding 1 asked how the affordance reads;
   the answer removes the state rather than explaining it.
4. **R5's 480px block is deleted, not raised** — `Auth.module.css`'s only media query goes.
5. **The primary's 160px min-width is deleted** — a signed measurement from R5, superseded here.
6. **The offer becomes an inset band** (was a `CraftPanel` in R5-2's implementation) — the hierarchy
   decision in finding 11 is a surface demotion, so the panel tier goes.
7. **Q-B taken as default *and* the copy left alone** — the handoff allowed the offer copy to say
   where it leads; the session declined (§1).
8. **The reset page carries no sample entry** — R5-1 fixes that entry to the 로그인 screen, and the
   reset page's reader already has an account.
9. **Success on the reset page is drawn as a statement, not a screen** — there is no completion
   surface to card, and inventing one would be inventing a state.

## 4b. Operator removals taken in session (2026-08-24)

Three copy blocks were struck by the operator after the cards went up. All three are **removals of
reassurance sentences**, not replacements — nothing was written to fill their place:

1. **The PII inset, both auth pages** (§2 finding 12). Withdraws R5-1's 상시 요소 clause.
2. **The offer band's two reassurance strings** — the body's trailing clause 「— 계정은 이메일과
   비밀번호뿐입니다.」 and the closing 「지금처럼 로그인 없이 계속 쓸 수 있습니다」. The body now reads
   「계정에 저장하면 마감이 다가올 때 이메일로 알립니다.」 The offer is still not a gate, and now only
   its behaviour says so (닫기 · once per session · the anonymous path unchanged) — which was already
   the structural guarantee; the sentence was the belt on top of it. R5-2's copy list loses two
   entries.
3. **The coverage boundary caption** 「놓친 돈은 집계 범위 안에서만 계산됩니다 · 2026년 이전의
   유상증자 기록은 집계에 없습니다」 — removed **on this card only**, via a local coverage block, so
   R11's landed `lookup/*` cards and `r11-parts.jsx` are untouched. If the removal is meant for the
   조회 surface itself it belongs in R11's record and `lookup/r11-parts.jsx` — say so and it moves.

## 5. Locks re-checked (all held except as noted in §4b)

Email + password only (no OAuth, no code login, no remember-me) · 8자 이상 and no other rule ·
가입 여부 비노출 (the same notice for any address) · login failure names no field · sample entry bottom-fixed on 로그인 · the anonymous path is
never blocked (no gate screen, no forced modal, nothing `position: fixed`) · `--alert` reserved for
소멸·마감 · mono for numbers only · square corners, hairline elevation · reduced-motion floor (this
surface animates nothing but a colour transition).
