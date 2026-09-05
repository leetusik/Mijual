# Result — P13.S2 (frontend: the 인증번호 state, the drafted Korean, the real-browser sweep)

- **status:** `done`
- **summary:** The auth panel gained its third mode: 계정 만들기 and 로그인 on an unverified account both land in a code-entry state on the same panel, the mailed 6-digit code verifies and lands on 보유 종목, and every new Korean string is drafted inside the R5/R12 vocabulary for the operator's literal approval. Swept live in Aside (`u2`) on the dev stack and a local production build at 1280 and 390 — and the sweep found that **S1's 5-attempt cap does not exist over HTTP** (the increment is rolled back with the error it raises), which is a backend defect this frontend slice deliberately did not fix.
- **files_changed:**
  - `frontend/components/auth/AuthPanel.tsx`
  - `frontend/components/auth/copy.ts`
  - `frontend/components/auth/Auth.module.css`
  - `frontend/lib/api.ts`
  - `frontend/lib/types.ts`
  - `frontend/lib/auth.test.ts`
  - `works/phases/active/P13/phase.md`
  - `works/phases/active/P13/slices/P13.S2/result.md`
  - `var/p13/code-state-1280.png`, `var/p13/code-state-390.png` (evidence, outside the slice folder)
- **validation:**
  - `cd frontend && npm run typecheck` — **pass** (no output; `tsc --noEmit` clean)
  - `cd frontend && npm run smoke` — **pass**, 23/23 (22 before, +1 new case pinning the two P13 codes)
  - Real browser, **Aside `aside repl --account u2`**, dev stack `http://127.0.0.1:3010` (API `:8010`) at 1280×800 and 390×844 — **pass**, 14 invocations, transcript below
  - Real browser, same instrument, **local production build** `node .next/standalone/server.js` on `http://127.0.0.1:3014` at 1280×800 and 390×844 — **pass**, dev and production agree on every measured value
  - `python3 scripts/workflow.py validate` — **pass** (pre-existing warnings only: `consolidation_owed=P4, P12`, `stale_docs=…`, `oversized_doc_sections=11`)
- **deviations:** three, all recorded below — (1) the plan's "the **5th** wrong code renders the 만료·시도 초과 line" **could not be observed**, because the cap is inert over HTTP (finding 1); the same line was proven live instead by letting the grant expire under the reader; (2) one file outside the plan's list, `frontend/lib/auth.test.ts`, gained one test case; (3) no `security.md` "Doc impact" line (the plan's condition — no security-relevant client behaviour changed).
- **doc_impact:** two lines appended to `phase.md` (`frontend.md`, `experience.md`) — quoted below.

---

## Finding 1 — the 5-attempt cap does not exist over HTTP (backend, S1, not fixed here)

**This is the sweep's most important result and it is not about the frontend.**

`verify_code` increments `grant.attempts`, flushes, and then **raises** `ApiError`
(`src/mijual/web/auth.py:791-797`). `get_write_session`
(`src/mijual/web/deps.py:123-128`) rolls the session back on *any* exception,
including a deliberately raised `ApiError` — which is exactly the behaviour its
docstring advertises ("a rejected signup leaves no half-written account behind").
So the increment is discarded together with the error it caused: **`attempts` is
never persisted, `VERIFICATION_MAX_ATTEMPTS` never bites, and a 6-digit code can
be guessed without limit for its full 10-minute life** (there is no cross-process
rate limiting either — that is still parked in P4).

Observed in the browser first: five wrong codes in the panel, all answering
불일치 where the fifth was contracted to answer 만료·시도 초과. Then isolated with
a throwaway HTTP probe (written to the scratchpad, run, and **deleted**; it
touched no product code):

```
signup 201
1 400 verification_code_invalid
2 400 verification_code_invalid
…
8 400 verification_code_invalid          ← eight, and still "wrong" rather than "dead"
```

and read back from dev Postgres immediately after the five browser attempts:

```
id | account_id | attempts | unspent | unexpired
 4 |         52 |        0 | t       | t
```

**Why the suite is blind to it.** `tests/test_web_auth.py`'s fixture overrides
`get_write_session` with a generator that yields one long-lived session and
commits, with **no rollback branch** (`tests/test_web_auth.py:57-63`). The same
`Session` object serves every request in a test, is never rolled back, and keeps
the dirty `attempts` value in its identity map, so
`test_five_wrong_codes_kill_the_grant_and_the_mailed_code_stops_working` passes
against behaviour production does not have. The test is not wrong about the
intent; the fixture is more forgiving than the runtime.

**Not fixed here, on purpose.** This slice's plan is explicit — *"Nothing in
`components/chrome`, `lib/session*.ts`, the reset panel, `/ops`, or the
backend"* — and a rollback-boundary change to the one write-session dependency
every mutating route shares is not a frontend edit. It is proposed as **`P13.F1`**
in `phase.md` (`## Now`, plus a note for `P13.REVIEW` and one for `P13.S3`), and
it gates the release: S1's own `security.md` "Doc impact" line claims *"a grant
dies at 5 wrong attempts"*, which is false as deployed, so shipping P13 before
the fix would ship a documented protection that is not there.

The panel needs **no change** when the fix lands: it already maps
`verification_code_expired` to its own line and points that reader at 재전송 — the
line was proven live (step 11 below), just not by the cap.

## The drafted Korean, verbatim

Every string is cited in code as `drafted P13 — approved literally at the P13
gate`. The mail's four are S1's and are unchanged; they are repeated in
`phase.md`'s note for `P13.REVIEW` so the walkthrough can carry all of them
together.

**Re-drafted (a signed R5 string, changed because it became false):**

| constant | before → after | why |
|---|---|---|
| `SIGNUP_INTRO_KO` | 「이메일과 비밀번호만으로 만듭니다 — **만들어지면 바로 로그인됩니다.**」 → 「이메일과 비밀번호만으로 만듭니다 — **인증번호를 메일로 보내 드립니다.**」 | 가입 opens no session at all now, so the promise after the em dash was false on the screen that makes it. R5's first clause is untouched and still exact: the panel really does collect only those two things — the code proves the address, it is not a third thing to remember. |

**New (`components/auth/copy.ts`, the `가입 인증` section):**

| constant | string | one line of reasoning |
|---|---|---|
| `VERIFY_KO` | 「이메일 인증」 | The other two modes title themselves with their submit verb; this one cannot, because a panel titled 「확인」 says nothing about what is confirmed. The title names the act, the field names the thing typed, the button names the press — three words, no overlap. |
| `VERIFY_INTRO_TEMPLATE_KO` | 「{email} 주소로 6자리 인증번호를 보냈습니다 — 10분 안에 입력해 주세요.」 | Names the **normalized** address the API returned (never what was typed) and states the window as a rule; 「주소로」 carries the address so the sentence stays grammatical after any ending. The *mail* carries the exact KST deadline — and `expires_at` can be absent from the response, so a countdown here could not even be drawn honestly. |
| `VERIFY_CODE_LABEL_KO` | 「인증번호」 | The mail's own word for the same thing — `mailcopy.py`'s 「같은 라벨의 두 번째 표기 금지」 read across two surfaces. |
| `VERIFY_SUBMIT_KO` | 「확인」 | 이메일 인증 is a step inside 가입/로그인, not a third thing a reader chooses, so the button says what pressing it does. `PENDING_KO` swaps in unchanged. |
| `RESEND_KO` | 「인증번호 재전송」 | Composed from two nouns exactly as `RESET_LINK_KO` composes 비밀번호 + 재설정, rather than written as a sentence. |
| `VERIFY_RESENT_KO` | 「인증번호를 다시 보냈습니다 — 메일함을 확인해 주세요.」 | `RESET_SENT_KO`'s grammar for the other mail: two mails, one sentence shape, the reader pointed at the mailbox either way. 알림 → soft. |
| `VERIFY_CODE_STILL_VALID_KO` | 「조금 전 보낸 인증번호가 아직 유효합니다 — 메일함을 확인해 주세요.」 | `resent: false` is the 60-second cooldown, a **state and not an error**, so it says the one useful thing and draws **no timer**: a countdown would make a non-event something to watch. |
| `ERR_CODE_FORMAT_KO` | 「인증번호 6자리를 입력해 주세요.」 | R12's gating grammar (빈 입력 answers in the slot, not in the browser's English). Unlike 이메일, empty and malformed are **not** two facts here — there is one shape and neither is it — so one line, stating the rule. It also keeps a slip from spending a server attempt. |
| `ERR_VERIFICATION_CODE_INVALID_KO` | 「인증번호가 일치하지 않습니다.」 | `ERR_INVALID_CREDENTIALS_KO`'s 「…일치하지 않습니다」 for the same kind of answer, and it never announces how many attempts are left — that would tell a guesser how much room they have. |
| `ERR_VERIFICATION_CODE_EXPIRED_KO` | 「이 인증번호는 더 이상 사용할 수 없습니다 — 인증번호 재전송을 눌러 새 번호를 받아 주세요.」 | `ERR_RESET_TOKEN_KO`'s shape **including its refusal to say which** of 만료 / 사용됨 / 시도 초과 happened (the grant's state stays unexposed), and it points at the one control that fixes all three, by that control's own label. |

**No constant for the way back.** It wears the origin mode's own name (계정 만들기
or 로그인) — the 전환 링크's rule applied to a return instead of a switch, so the
state costs no 취소 copy.

## What was built

- **`lib/types.ts`** — `Verification = { email: string; expires_at?: string }`, with the "absent, never null" rule stated where a reader of the type will meet it.
- **`lib/api.ts`** — `AuthResult` (`{account}` | `{verification_required?, verification}`) returned by both `signup` and `login`, narrowed by `"verification" in result` (**the key, never the status** — 가입 is a 201 and an unverified 로그인 a plain 200); new `verifySignup(email, password, code)` and `resendVerification(email, password)`. The CSRF header is untouched — `request` already sets it on every unsafe method.
- **`components/auth/AuthPanel.tsx`** — `mode: "login" | "signup" | "verify"` plus an `origin` the state remembers; `email` is replaced by the **normalized** address from the response and `password` is kept (the verify and resend calls need both); `code` resets on entry and the field takes focus from a `useEffect` on the transition, so both routes in get it without remembering to. One field (`id="auth-code"`, `type="text"`, `inputMode="numeric"`, `autoComplete="one-time-code"`, `maxLength=6`, string value), 확인 → `PENDING_KO` + disabled, the quiet row 재전송 + way back, both disabled while pending. Success reuses the existing 로그인됨 path unchanged (`router.push(ROUTES.portfolio); router.refresh()`), extracted into `landSignedIn()` because three paths now reach it.
- **`Auth.module.css`** — **one** new rule, `.code { font-variant-numeric: tabular-nums; }`. Nothing that touches geometry: the field measures 324×48 at 390 and the submit 48, identical to the other two modes (measured, below). Letter-spacing was considered and rejected — it would have made this field the only one on the surface with its own tracking.
- **`lib/auth.test.ts`** — one new case (see *Deviations*).
- The panel's header comment gained a P13 section (what the state is made of, why the password travels with the code, why it is not a route); R12's sections were not rewritten.

## The sweep — Aside `repl` on account `u2`, dev stack

Instrument: **Aside** (`aside repl --account u2 "<js>"`, profile 「claude2」), never
`u0`. The daemon was not running at the start of the slice and was started by
opening `/Applications/Aside.app`; `## Operator Runtime`'s sentence that Aside
does not run on this Mac is the stale one P12 recorded and P4 owes the correction
for. Tabs do not survive between invocations, so each step below is its own
invocation opening its own tab; profile cookies do persist, which is what let the
signed-in steps continue across calls. Codes were read from `var/stack/api.log`
(`[mail:signup_verification] to=… code=… expires_at=…`), never from a response
body. Throwaway addresses `p13-s2-{1,2,3,4}@mijual.test` (+ `p13-probe@…`), all
deleted — see *Cleanup*.

**1 — 가입 → the code state, 1280.** 계정 만들기 → `p13-s2-1@mijual.test` /
`sweep-pass-8` → 확인 state:

```
title 이메일 인증 · intro "p13-s2-1@mijual.test 주소로 6자리 인증번호를 보냈습니다 — 10분 안에 입력해 주세요."
labels ["auth-code=인증번호"] · field {type:text, inputMode:numeric, ac:one-time-code, max:6} · focused auth-code
submit 확인 (48px) · quiet ["인증번호 재전송","계정 만들기"] · panelW 432 · path /auth/login · scrollX 0
```

`GET /auth/me` → `{"authenticated":false}` and `document.cookie` empty: **no
session was opened** and the page did not navigate. The 계정 만들기 intro on the
way in read the re-drafted sentence.

**2 — the client gate spends no request.** In the state: 확인 with an empty field
→ 「인증번호 6자리를 입력해 주세요.」; 「123」 → the same line. Then one wrong
6-digit code → 「인증번호가 일치하지 않습니다.」 in `rgb(234,242,237)` (`--ink-1`,
not soft); then 재전송 inside the cooldown → 「조금 전 보낸 인증번호가 아직
유효합니다 …」 in `rgb(157,179,168)` (`--ink-2`, soft). The API log for that whole
invocation is **three requests**:

```
POST /auth/login 200 · POST /auth/verify 400 · POST /auth/verify/resend 200
```

— the two client-gated submits sent nothing, and the resend mailed nothing (no
new `[mail:signup_verification]` line).

**3 — 로그인 is the second route in.** Reloading `/auth/login` returned the idle
로그인 panel (state lost — expected and correct: the state lives in the component
and a URL for it would answer nothing), and 로그인 with the right password on the
still-unverified account landed straight back in the code state, quiet row
`["인증번호 재전송","로그인"]` — the way back now wearing 로그인, the origin it came
from.

**4 — the right code lands on 보유 종목.** `478106` from the log → `/portfolio`,
the chrome's account slot reading `p13-s2-1@mijual.test▾`, `/auth/me`
`{"authenticated":true,…}`. (`document.cookie` stays empty throughout — the
session cookie is `HttpOnly`, which is why `/auth/me` rather than `document.cookie`
is the evidence in both directions.)

**5 — 로그아웃 and P12.F5's reservation, untouched.** The account menu's 로그아웃 →
`/auth/login` with the band 「로그아웃되었습니다」, the one-hop channel consumed
(`sessionStorage["mijual.auth.flash"]` null) and the `data-mj-auth-flash` stamp
released. Then the reservation itself, measured: the key set, an init script
installed through `Page.addScriptToEvaluateOnNewDocument`, and the form's top
sampled every frame across the reload — **192 frames, one value, 298.52 px**, with
the stamp going `logout` → released and the band arriving. Nothing moves.

**6 — the R12 paths, unchanged.** Empty fields → 「이메일과 비밀번호를 입력해
주세요.」; `not-an-address` → 「이메일 주소 형식이 올바르지 않습니다.」; the right
address with a wrong password → 「이메일 또는 비밀번호가 일치하지 않습니다.」;
비밀번호 재설정 → 「재설정 링크를 보냈습니다 — 메일함을 확인해 주세요.」 (soft);
the sample entry 「샘플 포트폴리오로 둘러보기」 still under the panel. 로그인 with
the correct password on the now-**verified** account went straight to `/portfolio`
— a verified account never sees the code state.

**7 — the way back keeps the fields.** Second address, 가입 → code state → a line
on screen → 계정 만들기 (the way back): the panel returned to 계정 만들기 with
`p13-s2-2@mijual.test` and the password **still in the fields** and the line
cleared.

**8 — five wrong codes: the cap did not bite** (finding 1). All five answered
불일치, and dev Postgres read `attempts = 0`.

**9 — the dead-code line, proven live.** The 만료·시도 초과 branch was reached the
honest way instead: while the browser sat in the code state, an outside process
expired the grant (the 「메일을 너무 늦게 읽었다」 case, 10분 compressed to ~20 s),
then 확인 →

```
"이 인증번호는 더 이상 사용할 수 없습니다 — 인증번호 재전송을 눌러 새 번호를 받아 주세요."  soft=false  rgb(234,242,237)
```

**10 — 재전송 past the cooldown.** Pressing 인증번호 재전송 on that dead grant →
「인증번호를 다시 보냈습니다 — 메일함을 확인해 주세요.」 (soft) and a **new** line in
the log (`code=364585`, a fresh `expires_at`), and that code then verified and
landed on 보유 종목. Note for the record: routing in through 로그인 **mints a code
when none is live**, so the expired state cannot be reached by logging in again —
which is the design working, not a gap.

**11 — 390×844 (DPR 1, per P12's tiling note).** The code state fits: `docW 390 =
viewW 390` (no horizontal scroll), panel **358** and submit **48** — the same two
values 로그인 mode reports at 390 — field 324×48, `font-variant-numeric:
tabular-nums`, `letter-spacing: normal`. The intro wraps to two lines and the
quiet row stays on one.

Screenshots: `var/p13/code-state-1280.png`, `var/p13/code-state-390.png` (each the
only capture in its invocation; the repeated columns are the recorded emulated-tile
artefact — the leftmost tile is the page).

## The sweep — the local production build (`:3014`)

Built per `## Operator Runtime`'s recipe: `frontend/` copied aside (never into the
working tree's `.next`), `NEXT_PUBLIC_SITE_URL=https://jujutower.com
MIJUAL_API_ORIGIN=http://127.0.0.1:8010 npm run build`, `.next/static` + `public/`
staged into `.next/standalone/`, `node server.js` with `PORT=3014
HOSTNAME=127.0.0.1`. Build clean, 16 routes, no warning about the changed files.
Stopped at the end of the slice.

- **가입 → code state → 확인 → 보유 종목** at 1280: identical strings, identical
  state, `/auth/me` `false` before and `true` after, account slot
  `p13-s2-3@mijual.test▾`.
- **A wrong code** at 1280 → the same 불일치 line.
- **390**: panel **358**, field **324×48**, `tabular-nums`, `docW 390 = viewW 390`
  — every measured value equal to dev's.
- **로그아웃 band + the reservation** on the production build: band renders, and
  the form's top is **one value, 298.52 px across 192 frames** — the same number
  dev reported. Dev and production agree; only speed differs (P7's rule).
- One local-build fact worth knowing (below, for S3's benefit): **cookies ignore
  ports**, so the `mj_session` set on `127.0.0.1:3010` is sent to `127.0.0.1:3014`
  and `/auth/login` redirected to `/portfolio` on the first attempt. Sign out
  before sweeping a second local port.

## Deviations from `plan.md`

1. **The plan's "the 5th wrong code renders the 만료·시도 초과 line, not 불일치"
   could not be observed** — it is not true of the running product (finding 1).
   The line was proven live by expiring the grant under the reader instead, and
   the panel's mapping for both codes is additionally pinned in the smoke test.
   The backend fix is proposed as `P13.F1` and is **not** in this slice.
2. **One file outside the plan's Build list:** `frontend/lib/auth.test.ts` gained
   one case asserting that the two new structural codes map to their two
   *different* lines. The repo's rule is "core behaviour only", and this is the
   file that exists precisely because an unmapped code renders **no line** — the
   trap the notebook warned about twice. Three assertions, no fixtures.
3. **No `security.md` "Doc impact" line.** The plan makes it conditional on a
   security-relevant *client* behaviour changing beyond S1's note; none did. (The
   security-relevant thing this slice found is finding 1, which is the backend's
   and belongs to the slice that fixes it — S1's existing `security.md` line
   overstates the deployed truth until then, and `phase.md` now says so in
   `## Decisions` and in the note for `P13.REVIEW`.)

## Dead ends and things that cost time

- **`page.click("text=계정 만들기")` throws `Node is not an Element`** — the
  `text=` engine resolves to the text node. Every button press in this sweep went
  through a small `clickText()` helper doing
  `[...document.querySelectorAll('button')].find(b => b.textContent.trim() === name).click()`;
  React's synthetic handler fires from that dispatch. `page.fill(selector, value)`
  drives the controlled inputs correctly and was used for every field.
- **`page` is `null` before a tab exists**, so `page._sendToTarget(…)` must come
  *after* `openTab("about:blank")`; the device-metrics override then survives the
  subsequent `page.goto`.
- The first `aside repl` call failed with *"Aside daemon is not reachable"*; the
  app simply was not running. `open -a /Applications/Aside.app` and a few seconds
  of wait fixed it, with no account or profile change of any kind.

## Cleanup

- **Every account created is gone.** The three verified throwaways were deleted
  through `DELETE /auth/account` with their own cookies
  (`{"deleted":true,"authenticated":false}` each); the two unverified ones
  (`p13-s2-4`, `p13-probe`) were deleted directly in dev Postgres
  (`delete from account where email like 'p13-%@mijual.test'`, 2 rows). Dev
  Postgres is back to its two pre-existing accounts, both verified, and
  `email_verification` is **0 rows** — the FK cascade took the grants with the
  accounts.
- The HTTP probe script was deleted; it wrote no product code.
- The `:3014` server was stopped (the port no longer answers) and the copied
  build tree lives only in this session's scratchpad, outside the repo. The
  working tree's `frontend/.next` was never touched.
- The only files left outside the repo's source are the two screenshots under
  `var/p13/`, referenced above.
