# Result — P13.DECOMP

- **status:** done
- **summary:** Cut P13 into three bare middle slices — S1 backend, S2 frontend, S3 release + live proof — and seeded `phase.md` with the schema mechanism (NULL means verified, no Alembic), the `email_verification` grant's shape and numbers, the whole API contract, the three-kind mail rule, the copy route, and the release gates. Corrected `intent.md`'s Alembic assumption and found one gotcha the plan did not have: `/auth/signup` is a login shortcut in two test files besides `test_web_auth.py`.
- **files_changed:**
  - `works/phases/active/P13/phase.md`
  - `works/phases/active/P13/slices/P13.S1/slice.json` (created, bare folder)
  - `works/phases/active/P13/slices/P13.S2/slice.json` (created, bare folder)
  - `works/phases/active/P13/slices/P13.S3/slice.json` (created, bare folder)
  - `works/phases/active/P13/slices/P13.DECOMP/result.md`
- **validation:**
  - `python3 scripts/workflow.py validate` — **passed** (exit 0; three pre-existing warnings, none from this slice: `consolidation_owed=P4, P12`, `stale_docs=…`, `oversized_doc_sections=11`)
  - `python3 scripts/workflow.py next` — **passed**, `next_slice=P13.S1`
  - `ls -a` on each new slice folder — **passed**, each holds `slice.json` only (no pre-filled `plan.md`)
- **deviations:** none from the cut itself (three slices, orders 1/2/3, `--depends-on` chained, `REVIEW` left at 9999). Two plan recommendations were **decided rather than deferred**, as the plan asked: the resend cooldown is 60 s and re-signup honours it, and `POST /auth/verify/resend` answers `{"resent": <bool>, …}` instead of raising a cooldown error. One plan recommendation was **rejected after reading the code** — see finding 2.
- **doc_impact:** none. The decomposition settled no durable truth of its own; every durable-truth change in this phase is made by S1/S2/S3 and each of them appends its own note.

## What was verified in the tree before deciding

Every fact the plan handed me as established was checked, and all of them held:

1. **No Alembic anywhere** (`find` over the repo: zero hits; `src/mijual/db/` is `models.py` / `repository.py` / `schema_sync.py` / `session.py` / `__main__.py`). `intent.md` assumption 6 names an Alembic path that has never existed; corrected in `## Decisions` rather than in `intent.md`, which is immutable as captured.
2. **`schema_sync.ensure_columns` raises on any non-nullable or defaulted column** — read the guard directly (`src/mijual/db/schema_sync.py`): `if not column.nullable or column.default is not None or column.server_default: raise RuntimeError(...)`. It also **skips tables that do not yet exist** ("create_all's job, not ours"), which is what makes a brand-new `email_verification` table free to carry `NOT NULL` and defaulted columns of its own. `python -m mijual.db ensure` runs `create_all` then `ensure_columns`, in that order.
3. **`PasswordReset` is the grant to copy** (`src/mijual/db/models.py:849`), and `request_reset` / `confirm_reset` (`src/mijual/web/auth.py:411` / `:454`) carry the pattern: digest via `token_digest` under `session_pepper`, `expires_at`, `used_at`, supersede-on-repeat, one uniform failure code for expired/spent/never-existed.
4. **The mail seam is three files** as described: `mail.py`'s `PASSWORD_RESET` / `DEADLINE` constants and `render()`'s kind dispatch (which **raises** `MailError` on an unknown kind), `mailcopy.py`'s stdlib-only Korean strings with a citation per line. Both docstrings state the two-kind rule in the words the plan quoted. Log lines confirmed: `console mailer: %s to %s` (`mail.py:184`), `smtp mailer: sent %s` (`mail.py:318`).
5. **The auth surface** is as described — `routers/auth.py` transport-only, `web/auth.py` decisions-only, `signup` starting a session and setting the cookie on the spot (`routers/auth.py:84-87`), `reset/confirm` logging the reader in after proving mailbox control (the precedent `verify` will follow). Constants live at `auth.py:114-125` (`SESSION_LIFETIME`, `RESET_LIFETIME = 1h`, `RESET_PATH`, `_TOKEN_BYTES = 32`).
6. **Frontend**: `authErrorKo`'s `null`-for-unmapped rule (`copy.ts:158`), the R12 gating order and `noValidate` form, the single `role="status"` slot, `SIGNUP_INTRO_KO`'s now-false sentence (`copy.ts:65`), `lib/api.ts:205-222`'s four auth calls.
7. **Runtime and freeze**: `## Operator Runtime` in `docs/current/operations.md:285` gives `make stack-up`, 1280/390, the local production build recipe on port 3014, and the freeze **2026-09-07 11:00 → 2026-09-11 23:59 KST**. Its Aside sentence is stale exactly as the plan said — P12's notebook (`works/phases/active/P12/phase.md:42-45`) records the correction and that **P4 owes the note**, so P13 writes no note for it.
8. **`GET /ops/users` → `opsreads.reader_accounts`** exists and renders the 독자 계정 table (`routers/ops.py:283`), which is what makes the "should it mark unverified accounts?" question real rather than hypothetical.

## Findings the plan did not have

**1. `/auth/signup` is used as a login shortcut in two test files beyond `test_web_auth.py`.** The plan scoped the test breakage to `test_web_auth.py`'s signup-cookie case. It is wider:

- `tests/test_web_portfolio.py:158` — the `_login()` helper *is* a signup, and every portfolio test calls it;
- `tests/test_web_ops.py:107` — signs up, then asserts `GET /portfolio == 200` and `SESSION_COOKIE in client.cookies`;
- `tests/test_web_ops.py:175` — signs up, then reads the account out of `/ops/users`.

Under the hard gate all three lose their session. The fix is one signup-and-verify helper, not a re-pointed assertion per site; recorded as a note for S1.

**2. The code grant must *not* carry `PasswordReset`'s `UniqueConstraint` on the digest — the plan's "copy `PasswordReset`" would have shipped a latent 500.** A reset token is `secrets.token_urlsafe(32)` — 256 bits, addressed by itself, so a unique digest is free. A 6-digit code has 10^6 values and the digest is computed under one process-wide pepper, so two accounts holding the same live code produce the same digest and the constraint turns an ordinary birthday collision into an `IntegrityError` at issue time. Lookup is therefore **by `account_id`**, never by digest, and the code is only meaningful with the address. This is recorded as "difference 1" in `## Decisions`.

**3. `POST /auth/verify` taking `{email, password, code}` earns its third field twice over.** The plan justified it by the pending-signup race; the re-signup rule I settled (a re-signup **replaces** the password hash) makes that race concrete rather than theoretical, so the password check is load-bearing, not belt-and-braces. It also lets `verify` and `resend` answer `invalid_credentials` uniformly with `login`, so the code step needs no failure vocabulary of its own beyond the two code states.

**4. The cooldown has to sit on signup as well as on 재전송.** Guarding only `resend` would leave the signup form itself as an unauthenticated mail sender pointed at any address — re-signup on an unverified address is exactly the path assumption 3 opens. Both honour the same 60 s read off the live row's `created_at`, and both answer the identical 201/200 shape whether or not a mail actually went out, so nothing leaks and no timer copy is needed.

**5. `resent: false` as a state rather than an error.** A cooldown error would need a Korean line about a timer — copy nobody has signed and the operator would have to approve a countdown's wording. A boolean in a success body keeps it in the panel's existing soft-line vocabulary ("the code we already sent is still valid"), which is one drafted slot instead of a new failure class.

## Dead ends and roads not taken

- **`verified_at` / `verified: bool` on `account`** — rejected. Both need a backfill to grandfather existing rows, and this repo has no path that can run one; `ensure_columns` would refuse the column outright if it carried the default that would make the backfill unnecessary. The nullable, default-free `verification_pending_since` inverts the polarity so that *doing nothing* is the correct answer for every existing row.
- **A beat/janitor entry for stale unverified accounts** (assumption 3) — not built. Read literally, the assumption asks that an unverified account not block its address forever, and re-signup already delivers that at any age. Deleting old rows is housekeeping with no product-visible behaviour, so it is listed for the review as a `defer-job` candidate rather than made a slice.
- **A separate `/auth/verify` landing route** — never on the table (`intent.md` fixes the code-entry state on the same surface), but worth recording that the API shape assumes it: the code never travels in a URL, so there is nothing to land on.
- **A four-slice cut** (splitting the mail kind out of S1) — considered and dropped. `render()` raises on an unknown kind, so the constant, the branch and the two renderers cannot land separately from the endpoint that sends the message without leaving `main` in a state where a signup 500s at send time.

## Where the rest lives

The slice breakdown, the full API contract, the constants, the build inventory for S2, the operator questions and the notes tagged for each slice are in **`works/phases/active/P13/phase.md`** — written there, not restated here, because that is the file every later dispatch re-reads.
