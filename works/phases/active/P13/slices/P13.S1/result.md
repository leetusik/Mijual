# Result — P13.S1 (implementation, `slice-executor-high`)

- **status**: `done`
- **summary**: Built the signup email-verification gate in the backend exactly to the contract in `phase.md` — `POST /auth/signup` now creates an unverified account, mails a single-use 6-digit code and opens no session; `POST /auth/verify` (password then code) verifies and logs in; login on an unverified account answers `verification_required`; `/auth/verify/resend` supersedes the live code under a 60-second cooldown; a completed password reset also verifies. Every account that exists today is verified by the shape of the new nullable column, proven on dev Postgres (`+1 columns`, then idempotent, `count(*) … IS NOT NULL = 0`), and the whole flow was smoke-tested with curl against the running dev API.
- **files_changed**:
  - `src/mijual/db/models.py`
  - `src/mijual/web/auth.py`
  - `src/mijual/web/routers/auth.py`
  - `src/mijual/mail.py`
  - `src/mijual/mailcopy.py`
  - `tests/test_web_auth.py`
  - `tests/test_web_portfolio.py`
  - `tests/test_web_ops.py`
  - `works/phases/active/P13/phase.md`
  - `works/phases/active/P13/slices/P13.S1/result.md`
- **validation**:
  - `.venv/bin/pytest` — **pass** (171 passed, 1 pre-existing StarletteDeprecationWarning). Run twice: once after the test edits, once at the end.
  - `.venv/bin/python -m mijual.db ensure` ×2 on dev Postgres — **pass**: `schema ok (+1 columns)` then `schema ok`; a later pair after the smoke read `schema ok` / `schema ok`.
  - `SELECT count(*) FROM account WHERE verification_pending_since IS NOT NULL` on dev Postgres — **0** over 2 accounts (the grandfathering).
  - curl smoke against `http://127.0.0.1:8010` after `make stack-down && make stack-up` — **pass**, 8 steps, bodies below.
  - `python3 scripts/workflow.py validate` — **pass** (`Workflow validation passed.`; the three warnings are pre-existing: `consolidation_owed=P4, P12`, `stale_docs=…`, `oversized_doc_sections=11`).
- **deviations**: three, all small and all recorded in `phase.md` — (1) the contract's `verification` block returns `expires_at` **absent, never `null`**, when no live code exists; (2) a code that is not six digits **counts against `attempts`** (the plan asked me to decide and say so); (3) one test beyond the plan's minimum list (재전송 past the cooldown). Details under *Deviations* below.
- **doc_impact**: six lines appended to `phase.md` — `api.md` (signup's new 201 and no cookie, login's second success shape, `verify` + `verify/resend`, the two new codes, absent-never-null), `backend.md` (the flow, the three constants, `issue_verification` as the only minting path, `start_session` now raising, the third mail kind), `security.md` (the mailbox gate, digest storage, the cap and the cooldown, grandfathering by column shape, the Account PII statement gaining one *state* column), `data.md` (table 20 `email_verification`; `account.verification_pending_since`), `architecture.md` (no Alembic; `ensure` adds the column, `create_all` the table; no data-migration step), `product.md` (계정 만들기 now requires the mailed code; existing accounts unaffected).

---

## The drafted Korean, verbatim

All four strings are in `src/mijual/mailcopy.py`, cited **`drafted P13 — approved literally at the P13 gate`**. The gate walkthrough must list them exactly as they read here — the operator approves them literally, and nothing else in this phase drafts mail copy.

Subject (`SIGNUP_VERIFICATION_SUBJECT`, rendered with `PRODUCT_NAME`):

```
[주주의관제탑] 가입 인증번호
```

Body, as rendered (a real code and a real expiry substituted):

```
가입 인증번호입니다. 아래 6자리 숫자를 입력해 주세요.

012345

이 번호는 2026-09-06 21:10 (KST)까지 사용할 수 있습니다.
요청하지 않으셨다면 이 메일을 무시해 주세요. 인증하지 않으면 계정은 사용되지 않습니다.
```

The four constants separately:

| constant | string |
|---|---|
| `SIGNUP_VERIFICATION_SUBJECT` | `[{product}] 가입 인증번호` |
| `SIGNUP_VERIFICATION_INTRO` | `가입 인증번호입니다. 아래 6자리 숫자를 입력해 주세요.` |
| `SIGNUP_VERIFICATION_EXPIRY` | `이 번호는 {expires_at}까지 사용할 수 있습니다.` |
| `SIGNUP_VERIFICATION_IGNORE` | `요청하지 않으셨다면 이 메일을 무시해 주세요. 인증하지 않으면 계정은 사용되지 않습니다.` |

Three properties of the body worth naming at the gate: the code sits **on its own line** with nothing else on it (that is the line a reader copies); the validity is stated in **KST** through the existing `kst_stamp`, so it reads `2026-09-06 21:10 (KST)` rather than an ISO instant; and the ignore line states what happens if the reader does nothing, which is true — an unverified account cannot log in, and a later 가입 re-takes the address. No won amount, no sentence in `data`, stdlib-only imports (this module runs inside a request handler and inside the worker alike).

Both structural docstring rules were rewritten to say **three** kinds deliberately, rather than being quietly outgrown: `mail.py`'s 「Two kinds, and there will not quietly be a third」 and `mailcopy.py`'s 「알림 외 메일 금지. Two kinds exist」. Each rewrite states the count in words and says why all three still satisfy `security`'s no-marketing policy: every one of them is a mail the reader themselves set in motion.

## Step 4 — the curl smoke, against the running dev API

`make stack-down && make stack-up` first, so the runtime serves this code (API pid 41464, `http://127.0.0.1:8010`, `var/stack/api.log`). Every call carried `X-Mijual-CSRF: 1`. Two throwaway addresses were used and **both were deleted at the end** (see *Cleanup*).

**1 — 가입 opens no session.**

```
POST /auth/signup  {"email":"p13-smoke@mijual.kr","password":"smoke-pass-8"}
→ HTTP/1.1 201 Created        (no Set-Cookie at all — the cookie jar stayed empty)
{"verification":{"email":"p13-smoke@mijual.kr","expires_at":"2026-09-06T00:22:06+09:00"}}
```

**The code, server-side only**, in `var/stack/api.log`:

```
[mail:signup_verification] to=p13-smoke@mijual.kr code=267092 expires_at=2026-09-06T00:22:06+09:00
```

`267092` appears in **no** response body in this whole transcript. That is the gate.

**2 — a wrong code, grant still live.**

```
POST /auth/verify  {"email":"p13-smoke@mijual.kr","password":"smoke-pass-8","code":"000000"}
→ HTTP/1.1 400 Bad Request
{"error":{"code":"verification_code_invalid","message":"verification code is wrong"}}
```

**3 — the right password on an unverified account: routed, not refused, and no second mail.**

```
POST /auth/login  {"email":"p13-smoke@mijual.kr","password":"smoke-pass-8"}
→ HTTP/1.1 200 OK             (no Set-Cookie)
{"verification_required":true,"verification":{"email":"p13-smoke@mijual.kr","expires_at":"2026-09-06T00:22:06+09:00"}}
```

Same `expires_at` as step 1: the live code was left alone, and `api.log` gained no second `[mail:signup_verification]` line for that address.

**4 — the right code opens the session.**

```
POST /auth/verify  {"email":"p13-smoke@mijual.kr","password":"smoke-pass-8","code":"267092"}
→ HTTP/1.1 200 OK
set-cookie: mj_session=ZUf9vJ4ckANFFII8ncXoBtMuLEQFThhU3hNczRUtYqc; HttpOnly; Max-Age=2592000; Path=/; SameSite=lax
{"account":{"email":"p13-smoke@mijual.kr","created_at":"2026-09-06T00:12:06+09:00"}}
```

**5 — `GET /auth/me` with that cookie.**

```
{"authenticated":true,"account":{"email":"p13-smoke@mijual.kr","created_at":"2026-09-06T00:12:06+09:00"}}
```

**6 — logging in again, now verified: the plain P5 shape.**

```
POST /auth/login  {"email":"p13-smoke@mijual.kr","password":"smoke-pass-8"}
→ HTTP/1.1 200 OK
{"account":{"email":"p13-smoke@mijual.kr","created_at":"2026-09-06T00:12:06+09:00"}}
```

**7 — 재전송 inside the cooldown (second throwaway, `p13-resend@mijual.kr`).**

```
POST /auth/verify/resend  {"email":"p13-resend@mijual.kr","password":"smoke-pass-8"}
→ HTTP/1.1 200 OK
{"resent":false,"verification":{"email":"p13-resend@mijual.kr","expires_at":"2026-09-06T00:22:29+09:00"}}
```

`grep -c "to=p13-resend@mijual.kr" var/stack/api.log` read **1 before and 1 after** — the cooldown really did stop a second mail rather than merely reporting that it had.

**8 — 재전송 with a wrong password is the login's answer, byte for byte.**

```
POST /auth/verify/resend  {"email":"p13-resend@mijual.kr","password":"not-the-one"}
→ HTTP/1.1 401 Unauthorized
{"error":{"code":"invalid_credentials","message":"email or password is wrong"}}
```

**Cleanup.** `DELETE /auth/account` with the session cookie removed the verified throwaway (`{"deleted":true,"authenticated":false}`); the unverified one has no session by construction and was deleted directly (`DELETE FROM account WHERE email LIKE 'p13-%@mijual.kr'`, 1 row). Dev Postgres is back to its 2 pre-existing accounts, `verification_pending_since IS NOT NULL` = **0**, and `email_verification` = **0 rows** — the FK cascade took the grants with the accounts, which is the cascade working.

**The one path the curl smoke does not cover is 재전송 *past* the cooldown**, because proving it live means waiting 60 seconds. It is covered instead by a test that back-dates the grant's `created_at` (see *Tests*), which asserts the stronger property anyway: the old code stops working, exactly one grant row survives, and the new code opens the session.

## Step 1 — the schema, on dev Postgres

```
$ .venv/bin/python -m mijual.db ensure
schema ok (+1 columns)
$ .venv/bin/python -m mijual.db ensure
schema ok
```

The new **table** arrived in the same first run from `create_all` (`ensure_columns` skips tables it did not find, so its `NOT NULL` / defaulted columns are fine); the new **column** arrived through `ensure_columns`' `ALTER TABLE`, which is the path SQLite alone would never have exercised. Read back from the live database:

```
accounts total: 2
unverified (NOT NULL): 0
email_verification exists: email_verification
columns: ['id', 'account_id', 'code_digest', 'created_at', 'expires_at', 'used_at', 'attempts']
```

`unverified = 0` is the whole grandfathering story: no backfill, no data step, no migration — every pre-existing row is verified because `NULL` means verified and `ensure_columns` can only add a column that is nullable and bare. S3 must capture this same count **on the box, before its test signup**; the note is in `phase.md`.

## What was built, and the judgment calls inside it

**`start_session` is the single enforcement point.** It raises `RuntimeError` on an account whose `verification_pending_since` is not `NULL`. No route can reach that state — login branches before it, `verify_code` and `confirm_reset` clear the column first — and that is the point: reaching it is a *programming* error (a future route that forgot the gate), so the loudest failure is the correct one. A new route cannot mint a session for an unproven mailbox by forgetting a check, because the check is not in the routes.

**`issue_verification(..., force=)` is the only thing that mints a code**, and the cooldown outranks its caller. `force=False` (login) *ensures* a code exists; `force=True` (가입, 재전송) *replaces* the live one; neither mails twice inside 60 seconds, and the cooldown's clock is the most recently issued row's `created_at` whether or not that row is still live. Putting the throttle below both callers rather than in them is what keeps a later caller from forgetting it — 재전송 and re-signup both take an address, and an unthrottled one aims this product at somebody else's mailbox.

**One liveness predicate, `live_verification()`**: unspent, unexpired, and under the attempt cap, looked up **by `account_id` and never by digest**. A digest lookup on a 6-digit space could match another account's row; the code is only meaningful *with* the address, which is also why `verify_code` checks the password first.

**Password before code, in `verify_code`.** It goes through `authenticate`, so a miss burns a scrypt hash and answers `invalid_credentials` byte-identically with 로그인. It closes the pending-signup race the decomposition named: a second 가입 on an unverified address replaces the password hash, so without this check a stranger could sit on a half-finished signup and wait for the mailbox's owner to type the code they were mailed.

**Two failure codes, and the fifth wrong attempt switches which one you get.** A wrong code against a live grant is `verification_code_invalid`; *no live grant at all* is `verification_code_expired` — and the attempt that reaches the cap answers with the state it just created, not the one it was in a moment ago, because the panel must point at 재전송 for exactly that reader.

**Already-verified is a login, never an error**, on both `verify` and `resend`. A correct password proves everything the code was asked to prove, and inventing a failure would only strand a reader who pressed 확인 twice or verified in another tab.

**Re-signup on an unverified address replaces the password hash** with whatever was just typed and answers the identical 201 the free-address branch does. It is safe precisely because the previous password was never proven either — no session has ever existed on that account. A **verified** address is still `409 email_taken`: that mailbox *has* been proven, and letting a stranger overwrite its hash would be an account takeover with an extra step.

**`signup` lost its `Response` parameter.** Not cosmetic: the route now cannot set a cookie, because it has nothing to set one from.

## Deviations from `plan.md`

1. **`expires_at` is absent, never `null`.** The contract fixed `{"email", "expires_at"}`, and one corner has neither a live code nor permission to mint one — the grant was killed by the attempt cap or spent, *and* the 60-second cooldown has not elapsed. Emitting `"expires_at": null` there would have contradicted the codebase's own "absent, never null" rule and would have had the panel count down to nothing, so the key is simply omitted; `email` is always present. No endpoint name, key or code changed, so the `## Decisions` API contract stands — I amended the three lines that state the shape to say so, since **S2 reads the notebook, not this file**, and must read `expires_at` optionally.
2. **A code that is not six digits counts against `attempts`** (the plan asked me to decide and say so). Any wrong value is simply not the code; exempting malformed input would add a branch whose only observable effect is a cheaper guess, and the panel gates an empty field before it ever posts. The field is `code: str = Field(max_length=16)` and is `strip()`ed, so a bad length is never a 422 with English `fields` — it is the ordinary structural code. Recorded in `## Decisions`.
3. **One test beyond the plan's minimum list**: 재전송 *past* the cooldown supersedes the live code (back-dating `created_at` rather than sleeping a minute). 재전송 is a real product control that the live smoke cannot reach cheaply, and this is the one path where a bug would leave two working keys in one mailbox — so it is core behaviour by the repo's own test rule, not surface.

Not deviations, but worth naming: `verification_payload(email, grant)` takes the **address** rather than the `Account` (it needs nothing else, and 재전송 has already authenticated, so it need not re-read the row); `resend_verification` returns `(resent, live_row)` as planned; and the shared test helper lives in `tests/test_web_auth.py` and is **imported** by the other two suites (`from test_web_auth import signup_and_verify`), which works under pytest's default prepend import mode with `testpaths = ["tests"]` — the plan allowed import or copy, and importing means the next change to the gate is one edit rather than three.

## One finding worth carrying: SQLite hands back naive datetimes

The first test run failed with `TypeError: can't subtract offset-naive and offset-aware datetimes` inside the cooldown check. `DateTime(timezone=True)` comes back **aware from Postgres and naive from SQLite**, and the test engine is SQLite — so a Python-side comparison against `utcnow()` blows up in the tests while working perfectly in the runtime that matters. (SQL-side comparisons like `expires_at > utcnow()` are unaffected, which is why the rest of the codebase had never met this.)

Fixed with a small `_stored_utc()` helper in `mijual.web.auth` that reads a naive stored value as UTC — the convention `mijual.web.clock.to_kst` already states for exactly this reason: naive datetimes here come from the database, never from a wall clock. It is applied where the cooldown reads `created_at`. Any future backend code that does Python arithmetic on a stored timestamp will meet the same trap; the docstring on `_stored_utc` says so.

## Tests

`tests/test_web_auth.py` grew the four cases the plan named plus the one extra, and exports `signup_and_verify(client)` / `last_code(client)` for the other two suites:

- **the gate is hard at 가입 and at 로그인, and the code is what opens it** — signup sets no cookie and returns no `account`; the code read from the outbox is six digits and appears in **no** response body; login with the right password returns `verification_required` with no cookie and mails nothing new; 재전송 inside the cooldown is `resent: false` and mails nothing; the code then opens the session, `verification_pending_since` is `NULL` and the grant's `used_at` is set;
- **five wrong codes kill the grant** — four `verification_code_invalid`, the fifth `verification_code_expired`, after which the genuinely mailed code is dead too, no cookie exists, the account is still unverified, and a wrong password on that route is `invalid_credentials` (401);
- **재전송 past the cooldown supersedes** (the extra case, above);
- **a reset completed on an unverified account verifies it** — session set, column cleared, and the new password logs in;
- the existing 중복 가입 case now distinguishes the two: a **verified** address is `409 email_taken` in any spelling, an **unverified** one is re-taken with the identical 201, keys and all (가입 여부 비노출 survives the gate).

`tests/test_web_portfolio.py` and `tests/test_web_ops.py` install a `ConsoleMailer(stream=outbox)` in their fixtures and route their signup-as-login shortcut through the one imported helper — three call sites, one helper, no assertion re-pointed per site.

**Step 5 — lint/format: none configured.** `pyproject.toml` declares no `ruff`/`black`/`flake8` (only `[tool.pytest.ini_options]`), and the `Makefile` has no lint target. Skipped, as the plan allows.

## Notebook

`phase.md` was edited, not appended to: the four `for P13.S1` notes are consumed and removed; four `## Decisions` lines were amended in place with what the implementation settled (the absent-`expires_at` rule, the malformed-code decision, resend's already-verified block, and the cooldown outranking `force` with `issue_verification` as the only minting path); six **Doc impact** lines were appended; three notes were added `for P13.S2` (the exact shapes as built, the log line and the double-확인/one-panel-state facts, the two live-behaviour traps) and one `for P13.S3` (the schema step and its unrepeatable evidence); `## Now` was rewritten last. Nothing in the generated `## Slices` block was touched.
