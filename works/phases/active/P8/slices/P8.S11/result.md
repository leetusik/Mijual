# P8.S11 — R12 applied: auth (로그인 · 계정 만들기 · 비밀번호 재설정) + the conversion moments

The signed R12 round is built. Ten files changed, one deleted, one added. The auth surface is a
different object from the one R5 left: a 480px column whose first row is 「← 관제 현황판」, a panel
that no longer argues about PII, a form the browser has stopped speaking English on, and a 전환 제안
that has been demoted from a craft panel to an inset band and moved to the one place on the 조회 page
that is both 「값 계산 직후」 and 「결과를 가리지 않음」.

Everything below was measured in the operator's runtime, not inferred: `make stack-up` / `next dev`
at **`http://127.0.0.1:3000`** and at the tailnet origin **`http://100.77.164.42:3000`**, and again
against a **production build** served from a scratch copy on `:3100`, at 1456 / 768 / 767 / 600 /
481 / 390.

---

## 1. What changed, file by file

**`frontend/components/auth/copy.ts`** — R12's four new constants (`PASSWORD_RULE_KO` 「8자 이상」,
`ERR_FIELDS_REQUIRED_KO`, `ERR_INVALID_EMAIL_KO`, `ERR_RESET_TOKEN_KO`), the two new `authErrorKo`
mappings (`invalid_email`, `invalid_reset_token`) and that function's rewritten header note — two of
its three recorded gaps are closed, `csrf_required` and transport failures stay unmapped by design.
Deleted: `PII_RECEIVES_KO`, `PII_NOT_STORED_KO`, `CONVERT_STAY_KO`. Shortened: `CONVERT_BODY_KO` →
「계정에 저장하면 마감이 다가올 때 이메일로 알립니다.」 The section where the two PII constants stood
now carries the **withdrawal of R5-1's 상시 요소 clause** in prose, so the next reader of this file
finds the decision rather than a hole.

**`frontend/components/auth/Auth.module.css`** — rewritten from R12's geometry canon
(`output/account/r12-auth.css`), declaration by declaration, onto the module's class names. R5's
`@media (min-width: 480px)` block is gone; the file now has **exactly one** media query and it is
`max-width: 767px`. New: `.rail`/`.crumb`, `.head`, `.flash`, `.labelRow`, `.rule`, `.line`/`.soft`,
focus-visible rules for every control. Retired with their elements: `.pii`, `.piiLine`,
`.offerStay`, `.error`/`.notice` (one slot now), the 160px `min-width` and `align-self: flex-start`
on the primary.

**`frontend/components/auth/AuthRail.tsx`** (new) — 「← 관제 현황판」 as the column's first row, on
both auth pages. No new Korean: `BOARD_LABEL_KO` is the chrome's own noun, rendered with the same
`← ` the detail crumb and `LookupRail` already use. Internal to this folder, not exported.

**`frontend/components/auth/AuthPanel.tsx`** — `noValidate`; `required`/`pattern` removed (`type`
and `autoComplete` kept); client gating in the signed order; 「8자 이상」 on the 비밀번호 label row in
signup mode only; 재설정 never disabled for an empty address (it focuses the email field and sends
nothing); one `p role="status"` slot with `soft` for notices; the 로그아웃 flash as a band **above**
the `h1`, cleared by the first field change, by a submit or by navigation, with no timer; the quiet
row disabled while a request is in flight; `PiiInset` gone from the tree.

**`frontend/components/auth/ResetConfirmPanel.tsx`** — rail, the shared panel, one 비밀번호 field
with the rule, no 이메일 field, no sample entry; the client 8자 check before the round trip;
`invalid_reset_token` → `ERR_RESET_TOKEN_KO` plus a quiet 「로그인」 → `/auth/login` **in that state
only**; success unchanged (sessions revoked, new session, `/portfolio`, no completion screen); no
`?token` still redirects.

**`frontend/components/auth/ConversionOffer.tsx`** — the `CraftPanel` wrapper dropped for the inset
band (`div.offer`): head row = session lead + 닫기, one body line, one CTA. The stay line is gone.
Every condition is untouched — anonymous only, `ready` asked of `lib/holding.ts`'s own `convert()`,
one `sessionStorage` flag per session, dismissible, dismissal leaves nothing.

**`frontend/components/auth/index.ts`** — the `PiiInset` export removed (and why).

**`frontend/components/auth/PiiInset.tsx`** — deleted.

**`frontend/components/lookup/StockView.tsx`** — the band moved from last-on-the-page to **after the
last data section and before 집계 범위 + the provenance line**. One JSX move plus the reason, in the
comment; nothing else on the lookup surface was touched.

**`frontend/lib/auth.test.ts`** — the existing four-case suite, updated rather than grown: the two
codes R12 signed move from the "renders no line" case into the "signed line" case. Still no
framework, still terse (16/16).

**`docs/reference/design/grounding/copy-inventory.md`** — the hand-registered R12 tail: 4 new
strings with their reasons, 3 deletions, the shortened body line, the two `authErrorKo` closures,
the reused-not-new list, the supersessions, and the explicit note that `COVERAGE_BOUNDARY_KO` stays
on the lookup surface (P8 Q39 default (a)).

`DeadlineOffer.tsx`, `SampleEntry.tsx`, `useAuthState.ts`, `app/auth/login/page.tsx`,
`app/auth/reset/page.tsx`, the nav, `lib/session*.ts`, `lib/api.ts`, every auth API route and the
whole backend are **untouched** — verified by diff and, for the two offers and the nav, by
measurement below.

---

## 2. Regression checklist — build-prompt §6, items 1–12

Every row was walked at both dev origins **and** in the production build unless noted; results were
identical in all three.

| # | Claim | Measured |
|---|---|---|
| 1 | one media query, `max-width: 767px` | `grep -c "@media"` → **1** rule (the other two hits are comment text). At 768 the column is 480px / panel 24px; at 767 it is full-width / panel 20px 16px. One boundary. |
| 2 | primary `width:100%; height:48px` everywhere | 1456/768 → **382×48**; 767 → 701×48; 600 → 534×48; 481 → 415×48; 390 → 324×48. `align-self: auto`, `min-width: auto` at every width. |
| 3 | empty submit answers in Korean on all three forms; no `required`/`pattern` | 로그인 → 「이메일과 비밀번호를 입력해 주세요.」 · 계정 만들기 → same · 재설정 페이지 → 「비밀번호는 8자 이상이어야 합니다.」 **0** `/api/auth/*` requests in each case, `input.validationMessage` empty, no bubble. `required: false` / `pattern: null` on all three inputs. A malformed address → 「이메일 주소 형식이 올바르지 않습니다.」, also 0 requests. |
| 4 | 재설정 alive with an empty address | Clicking it with the field empty moves focus to `#auth-email` (`document.activeElement` = `auth-email`), renders **no** line and fires **0** requests. With an address: `POST /api/auth/reset/request` + the notice. `disabled` **only** while pending (held the POST open with `Fetch.requestPaused`: both quiet buttons `disabled`, ink-3, `text-decoration-color` = `--border-soft`). |
| 5 | 「8자 이상」 on 계정 만들기 + 재설정, not on 로그인 | signup: **1** occurrence, IBM Plex Mono 11px `--ink-3`; reset page: 1; 로그인: **0**, and it disappears again on the mode switch back. |
| 6 | 로그아웃되었습니다 above the `h1`, once, cleared by the first keystroke | y **169** vs `h1` y **226** (`bottom <= h1.top`), count **1**, `role="status"`, `--surface-inset` + 1px `--border-soft`, `10px 14px`, `text-sm`, `--ink-1`. First keystroke → gone; a submit → gone; **9 s untouched → still there** (no timer). Reached both synthetically and through the real path: 로그아웃 from the account menu lands on `/auth/login` **with the band**. |
| 7 | errors ink-1 / notices ink-2, no `--alert`, no field-border change | error `rgb(234,242,237)` = `--ink-1`; notice `rgb(157,179,168)` = `--ink-2`. `grep alert components/auth/*` → nothing; scanning every element under `main` for `--alert` (`#e0573f`) in colour/background/border → **0 hits**. Input border `rgba(163,196,180,.32)` 1px **identical before and after** a failure. |
| 8 | focus-visible on all ten controls | Real `Tab` key events. Login: rail (offset **2**) · email (**−1**) · password (**−1**) · primary (2) · 전환 링크 (2) · 재설정 (2) · sample link (2). Reset page: rail · field (−1) · primary (2). Offer band: 닫기 (2) · CTA (2). All `2px solid rgb(143,178,232)`, all `:focus-visible` true. |
| 9 | rail on both pages, sample on 로그인 only, no PII inset | rail 「← 관제 현황판」 on both; sample section on the login route in **both** modes and absent on the reset page; 「미주알이 받는 것」/「저장하지 않는 것은」 → **0** occurrences product-wide; `PiiInset.tsx` deleted and its export removed. |
| 10 | at 390 the sample sub does not orphan 「번.」 | Two lines at 390/600/1456: 「가입 없이, 실제 공시 4건으로 구성된」 / 「예시 포트폴리오를 엽니다 — 클릭 한 번.」 `text-wrap: balance`, `max-width: 243px` (= 34ch). See §3 for the one declaration this needed. |
| 11 | the band is three things, in the right place | Children: `.offerHead` (lead + 닫기) · `.offerBody` · `.offerCta` — **no** stay line, **0** bracket nodes, `box-shadow: none`, `--surface-inset` + 1px `--border-soft`, `16px 20px` (≤767: `14px 16px`), body `max-width: 443px` (62ch), CTA 44px `--live-solid` `#fff` `justify-self: start` (≤767 full width, centered), 닫기 44×44 at `-11px -10px -11px 0`. Placement index **4** of 7: rail · identity · 진행 중인 권리 · 놓친 돈 · **밴드** · 집계 범위 · provenance. 닫기 → the block is gone and **nothing** stands in its place; the session flag is set; a second stock in the same session does not ask again. Signed in: the band never renders and the flag is not even claimed. |
| 12 | DeadlineOffer silent until the session is known; exact labels; login lands `/portfolio` | Holding `/api/auth/me` open: **no** offer link renders at all. Released → anonymous 「이 마감 알림 받기 →」 → `/auth/login`, 32px desktop, ink-2, underline (R10 geometry, untouched). Signed in → 「보유 종목에 담기 →」 → `/portfolio?add=00102618`. 계정 만들기 → `/portfolio`; 로그인 → `/portfolio`; `/auth/login` with a session → `/portfolio`. |

**How the signed-in half was reached.** A temporary account (`p8s11-temp@example.com`) was created
**through the product's own 계정 만들기**, used for the signed-in rows above and for the real
로그아웃 → flash path, then deleted from the dev database with its session
(`auth_session` 1, `holding`/`lapse_claim`/`password_reset` 0). The `account` table is back to the
two rows it held before this slice — `s19-fidelity@example.com` (id 14, P7 Q13's leftover, left in
place deliberately) and the operator's own — and `auth_session` is back to **3**.

---

## 3. The one declaration the canon states elsewhere, and why it is here

R12's canon puts `word-break: keep-all` on the **body** of its card harness, and the `.assub` rule's
own comment leans on it: 「keep-all은 body에서 이미 걸리고, balance가 마지막 줄을 끌어올린다」. In the
product that property is **not** global — R9 scoped it to the landing and R10 to the detail page, and
`app/shell.css` has none — so the auth surface was `word-break: normal` and the orphan fix the round
designed did not have the ground it was drawn on. Measured without it at 390: 「구성된 **예 / 시**
포트폴리오」 — a break *inside* an 어절, which is the defect keep-all exists to prevent. It is now on
`.page`, scoped exactly the way the two earlier rounds scoped theirs, and the line breaks between
어절 with 「클릭 한 번.」 ending the second line.

The canon's other body declarations (`padding`, the radial-gradient background, `font-family`,
`color`) are the harness reproducing the app shell and were **not** copied. `text-wrap: pretty` was
not copied either: no product surface carries it, R12's contract does not mention it, and `.sampleSub`
already gets `balance` explicitly — adding it would change wrapping across the surface for no signed
reason.

---

## 4. Departures from the record

**None in geometry, copy or behaviour.** Two readings are recorded here rather than left implicit:

1. **The reset page's 「로그인」 is an `<a>`, not a `<button>`.** The card draws it as `button.aq`
   because a card has nowhere to navigate to; build-prompt §3 says 「로그인」 **→ `/auth/login`**, and
   the round's own headings note gives the rule the login panel's two controls follow — 전환 링크와
   재설정은 `button`(**둘 다 이동하지 않는다**). This one does navigate, so it is a link wearing
   `.quiet`. Identical treatment, identical 44px, identical focus ring.
2. **The 「로그인」 row is bound to the expired answer, not to a separate flag.** First cut kept two
   states and the row survived a later 8자 미만 — a way out offered for a state the reader was no
   longer in. It is one value now (`{line, expired}`), so the sentence and the exit can never
   disagree. Caught in the browser, fixed, re-measured (`short_after_expired` → line only, no row).

Two consequences of the signed declarations, noted because they differ from a card's own picture:

- The sample subline renders on **two** lines where the card's note says three. Every declaration is
  the canon's (`balance`, `34ch` → 243px at `text-sm`); the count is what Pretendard does with them
  at that width. The defect the round named — the orphan — is gone.
- The **P7 focus split still owns a mouse click** into an auth field: R12 signs `:focus-visible`
  (keyboard) and `app/shell.css`'s (0,1,1) rule fires on plain `:focus`, so a mouse click gets that
  rule's border-colour change rather than the ring. R12 draws no mouse-focus state, so nothing was
  invented; the module's `.input:focus-visible` at (0,2,0) wins wherever both apply. → **Q40**.

---

## 5. Validation

| Command | Result |
| --- | --- |
| `cd frontend && npm run typecheck` | pass (clean) |
| `cd frontend && npm run smoke` | pass — **16/16** |
| `npm run build` (scratch production copy, `cp -Rc node_modules`) | pass — green; every §6 row re-walked against it on `:3100` |
| `.venv/bin/python -m pytest` | pass — **142 passed** |
| `python3 scripts/workflow.py validate` | pass — "Workflow validation passed." |

`frontend/next-env.d.ts` is **untouched**: the build ran in a scratch copy, per `P8.S7`'s note.

**Whole `## Regression Checklist` re-run** (the qa doc's list plus the P8 lines accumulated in
`phase.md`'s `## Doc impact`), in dev at 1456 and 390:

- 크롬 — nav exactly two links (AI 질문 · 보유 종목), **0** `data-vocky-trigger`, no `[의견]` chip,
  no 샘플 chip, footer **0** mono nodes; ≤480 메뉴 opens as an overlay with a backdrop that does
  **not** push the page (`scrollHeight` unchanged), `body` locked while open and released after Esc;
  at 390 「AI 질문」 is **not** orphaned on its own footer line, `overflowX` 0.
- 관제 현황판 — 15 ranked rows + 「15건 더 보기」 + 「남은 371건」; the countdown card's three stats,
  「읽은 실적보고서」 absent.
- 상세 — **one** craft panel, 5 citation triggers, 「종료」 **0** occurrences, **0** accessible names
  containing 「//」; 「[근거]」 opens an `position: absolute` popover, the rows behind it **do not
  move**, and it stays fully inside the viewport.
- 404 — `/events/<nonexistent>` → status **404** with the Korean not-found, no English screen.
- 조회 — `/stocks` entry states 감시 대상 + 감시 중 + 집계 범위 + provenance; a resolved stock's `h1`
  is the 종목명 and 「내 종목 조회」 appears **once**; `/stocks?q=삼성` → 「‘삼성’**과** 일치하는
  종목이 없습니다」; the page's section order is unchanged apart from the band's new slot.
- 보유 종목 — signed out, `/portfolio` renders the sample (no redirect).
- AI 질문 — `/ask` composer + rail render; the thread store still persists under its one
  `sessionStorage` key.
- Zero console errors or warnings across the whole sweep, on both origins and in production.

Backend/CLI lines (`gates run`, `estimate report`, `scheduler once --offline`, `extract recheck`, the
exposure invariant, the four AST scans + the anonymity scan) are covered by the green `pytest` run
and were **not** re-run separately: this slice changes presentation, client gating and copy only —
no payload, no route, no gate, no schema.

---

## 6. Raised for the operator

**Q40** (new, appended to `phase.md`'s `## Operator Questions`) — the auth fields now answer a
*keyboard* focus with R12's ring and a *mouse* click with P7's border-colour change. Both are signed,
by different rounds, and R12 drew no mouse state. Nothing was invented; the operator decides whether
the two should be one.

Q39 (does the coverage-caption removal extend to the lookup surface) stays open and was honoured at
its default: `COVERAGE_BOUNDARY_KO` and every lookup string are untouched.
