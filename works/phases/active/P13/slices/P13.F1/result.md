# Result — P13.F1 (fix: make the 5-attempt cap real over HTTP)

- **status:** `done`
- **summary:** The wrong-code branch of `verify_code` now commits the failed attempt before the `ApiError` travels, so the increment survives `get_write_session`'s rollback-on-exception and `VERIFICATION_MAX_ATTEMPTS` finally bites: measured live over HTTP, five wrong codes answered 불일치 · 불일치 · 불일치 · 불일치 · **만료**, the row read `attempts = 5`, and the genuinely mailed code was dead with it. The three test fixtures that override the write session now roll back on exception exactly as the runtime does, which is what makes the existing cap test able to see this class of bug at all — it failed first with the honest fixture alone, and passes on the fix.
- **files_changed:**
  - `src/mijual/web/auth.py`
  - `tests/test_web_auth.py`
  - `tests/test_web_portfolio.py`
  - `tests/test_web_ops.py`
  - `works/phases/active/P13/phase.md`
  - `works/phases/active/P13/slices/P13.F1/result.md`
- **validation:**
  - `.venv/bin/pytest -q tests/test_web_auth.py::test_five_wrong_codes_kill_the_grant_and_the_mailed_code_stops_working` with **only the fixture fixed** — **RED, as required** (the recorded regression run; assertion quoted below)
  - `.venv/bin/pytest -q` — **pass**, `171 passed, 1 warning in 4.43s`
  - Live over HTTP on the restarted dev stack (`make stack-down && make stack-up`, API pid **41464 → 46137** on `127.0.0.1:8010`) — **pass**, every body recorded below: 5 wrong codes → the 5th is `verification_code_expired`, dev Postgres reads `attempts = 5`, the real mailed code then also answers `verification_code_expired`, `resend` inside the cooldown answers `{"resent": false}` with no `expires_at`, and past a back-dated cooldown answers `{"resent": true}` with a fresh code that verifies and opens a session
  - `python3 scripts/workflow.py validate` — **pass** (pre-existing warnings only: `consolidation_owed=P4, P12`, `stale_docs=…`, `oversized_doc_sections=11`)
  - Throwaway account `p13-f1@mijual.test` **deleted** through `DELETE /auth/account`; `account` and `email_verification` both read 0 rows for it afterwards
- **deviations:** none. (The plan's option to keep the service layer commit-free by answering the 400 from the route was considered and **not** taken — see *Why the commit and not the route* below.)
- **doc_impact:** three lines appended to `phase.md` — `backend.md`, `security.md`, `qa.md`; quoted at the end of this file.

---

## 1. The red run — the fixture alone, before any change to `verify_code`

`tests/test_web_auth.py`'s `_write()` override was changed first, to mirror
`get_write_session` (commit on a normal return, **roll back on any exception**,
re-raise; no `close()`, because one long-lived session serves the whole test).
With `verify_code` still untouched, the existing cap test failed exactly where
production fails:

```
    killed = submit(wrong)
>   assert killed.json()["error"]["code"] == "verification_code_expired"
E   AssertionError: assert 'verification_code_invalid' == 'verification_code_expired'
E     - verification_code_expired
E     + verification_code_invalid
tests/test_web_auth.py:247: AssertionError
```

That is the whole of S2's finding reproduced in the suite: the fifth wrong code
still answers "wrong" because attempts 1–4 were each rolled back with the 400
they caused, so the counter is perpetually at 1. The test was never wrong about
the intent; the fixture was more forgiving than the runtime.

## 2. The fix — the failed attempt is the write of record

`src/mijual/web/auth.py`, `verify_code`'s wrong-code branch:

```python
        grant.attempts += 1
        db.flush()
        # Read the counter **before** the commit: the test factory expires
        # instances on commit, so comparing afterwards would reload the row for
        # no reason (and, in the fixture's one-session world, at a moment the
        # value is no longer in the identity map).
        reached_cap = grant.attempts >= VERIFICATION_MAX_ATTEMPTS
        db.commit()
        if reached_cap:
            raise ApiError("verification_code_expired", "no live verification code")
        raise ApiError("verification_code_invalid", "verification code is wrong")
```

The `reached_cap` local is not a style choice: the app's own factory sets
`expire_on_commit=False`, but the tests build a plain `sessionmaker(bind=engine)`
(expire-on-commit **on**), so reading `grant.attempts` after the commit would
reload the row in one runtime and not the other. Capturing it first makes the
branch read identically everywhere.

The function's docstring now carries the reasoning as a named exception —
paraphrased: this is the one place the service layer commits;
`get_write_session` rolling back on any exception is right for every other 4xx
here (a rejected 가입 must leave no half-written account behind) and wrong for a
counter whose whole job is to make failures expensive, the same way a failed
login counter anywhere must persist through the 401 it produces. After the raise
the dependency's `rollback()` and `close()` run against a **fresh** transaction
holding nothing, so they are harmless — the commit ended the transaction the
increment lived in.

**Nothing rides along on that commit.** The route (`POST /auth/verify`) performs
no write before this call, and the only write `authenticate` can leave pending is
a password-hash upgrade on a **correct** password — a write that deserved to
survive anyway and previously did not.

### Why the commit and not the route

The plan allowed a commit-free shape (the route returning the 400 envelope on a
normal return so the dependency commits). Rejected: `ApiError` is raised by
`create_account`, `change_email`, `authenticate`, `confirm_reset` and the
`live_verification` miss inside this same function, so the "answer normally"
shape would have to travel back through `verify_code`'s return type — a second
error channel in the one module whose docstring insists there is exactly one —
and the byte-identical envelope guarantee would then rest on the route
reconstructing what `errors.py` builds. One commit, in one branch, with the
reason written down, is the smaller change and the one the plan calls the fix.

## 3. The write-path audit — every `raise ApiError` after a write in `mijual/web/auth.py`

Each one checked for the same trap. **None of them has it**; nothing else was
changed.

| site | verdict |
|---|---|
| `create_account` — `email_taken` on a **verified** address (409) | Raised **before** any write (the lookup precedes it). Correct. |
| `create_account` — `IntegrityError` on the concurrent-signup race | Explicitly `db.rollback()`s *itself*, then raises. The half-added `Account` **must** be discarded. Correct. |
| `create_account` — the unverified re-take branch (hash + `verification_pending_since` rewritten) | Returns normally; the dependency commits it. Correct. |
| `change_email` — `email_taken` on a taken address | Raised before the write. Correct. |
| `change_email` — `IntegrityError` after `account.email = …` + the reset-grant delete | Rolls back itself, then raises: a failed 주소 변경 must not delete the outstanding reset grants. Correct — the discard is the point. |
| `authenticate` — `invalid_credentials` | Raised before its only write (the `needs_rehash` upgrade happens only *after* a successful verify). Correct. |
| `confirm_reset` — `invalid_reset_token` | Raised before any write; the grant lookup precedes it. Correct. |
| `issue_verification` — the resend cooldown | **Raises nothing.** `(False, live)` is a normal return, so the surrounding writes commit. Correct — and it is why `resent: false` is a state rather than an error. |
| `resend_verification` | Raises only through `authenticate`, i.e. before any write of its own. Correct. |
| `start_session` — `RuntimeError` on an unverified account | The guard is the function's first statement, before the dead-session sweep and the `add`. Correct. |
| `read_account` / `write_account` — `unauthenticated` | Raised before any write. Correct. |
| `verify_code` — the wrong-code branch | **This was the bug.** Fixed above. |
| `_validated_email` / `_validated_password` | Pure validators, no session. Correct. |

## 4. The fixtures

All three write-session overrides had the yield-then-commit form and all three
now mirror `get_write_session`. `test_web_auth.py`'s is the one that matters for
this bug; `test_web_portfolio.py` and `test_web_ops.py` run signup + verify
through the shared helper, so a forgiving fixture there would let the same class
of bug pass unnoticed in a second and third file.

One override was deliberately **left alone**: `tests/test_web_ops.py:103`
(`closed.dependency_overrides[get_write_session] = lambda: client.db`) is a plain
lambda for a 401-path app with no credential configured — it never commits and
never yields, so there is no rollback boundary to mirror.

**No new test file, and the cap test was not extended:** it already asserts the
5th answer is `verification_code_expired`, that the previously-mailed code stops
working, that no cookie was minted, and that the account is still unverified. The
fixture is what makes those assertions mean something.

## 5. Live over HTTP — the dev stack, restarted

`make stack-down && make stack-up`; `make stack-status` showed the new pid
(**46137**, previously 41464) on `http://127.0.0.1:8010`. Every request carried
`X-Mijual-CSRF: 1`.

```
POST /auth/signup   {"email":"p13-f1@mijual.test","password":"f1-secret-8"}
  201 {"verification":{"email":"p13-f1@mijual.test","expires_at":"2026-09-06T00:58:03+09:00"}}
  var/stack/api.log: [mail:signup_verification] to=p13-f1@mijual.test code=522870

POST /auth/verify   code="000000"  ×5
  1  400 {"error":{"code":"verification_code_invalid","message":"verification code is wrong"}}
  2  400 {"error":{"code":"verification_code_invalid",…}}
  3  400 {"error":{"code":"verification_code_invalid",…}}
  4  400 {"error":{"code":"verification_code_invalid",…}}
  5  400 {"error":{"code":"verification_code_expired","message":"no live verification code"}}   ← the cap
```

Dev Postgres, immediately after — the measurement S2 could not obtain:

```
 id | account_id | attempts | used_at |          expires_at           | email              | verified
 10 |         56 |        5 |         | 2026-09-05 15:58:03.727434+00 | p13-f1@mijual.test | f
```

`attempts = 5`, persisted, on a row that is 4 minutes from its natural expiry.
Then the code that was really mailed:

```
POST /auth/verify   code="522870"   (the genuine code from the log)
  400 {"error":{"code":"verification_code_expired","message":"no live verification code"}}
```

Dead with the grant — a guesser cannot burn the cap and then have the mailbox
owner's own code work.

```
POST /auth/verify/resend        (inside the 60 s cooldown)
  200 {"resent":false,"verification":{"email":"p13-f1@mijual.test"}}
```

`resent: false`, and `expires_at` **absent, never null** — the contract's rule,
here in the one corner that reaches it: the cap killed the grant *and* the
cooldown forbids a new one. The dead grant is not resurrected by a cooldown
answer. Then, with that row's `created_at` back-dated 61 seconds in dev Postgres:

```
POST /auth/verify/resend
  200 {"resent":true,"verification":{"email":"p13-f1@mijual.test","expires_at":"2026-09-06T00:58:40+09:00"}}
  var/stack/api.log: [mail:signup_verification] to=p13-f1@mijual.test code=268414

POST /auth/verify   code="268414"
  200 {"account":{"email":"p13-f1@mijual.test","created_at":"2026-09-06T00:48:03+09:00"}}   + mj_session cookie
```

and the rows afterwards: the exhausted grant **10 is gone** (superseded — the
resend deletes every unused row for the account, cap-killed ones included), the
fresh grant 11 reads `attempts = 0, spent = t`, and the account reads
`verified = t`. So the cap is a dead end for a guesser and never for the mailbox's
owner: wait out the cooldown, press 재전송, type the new number.

**Cleanup:** `DELETE /auth/account` with the session cookie →
`{"deleted":true,"authenticated":false}`; `account` and `email_verification` both
read **0** rows for the address afterwards.

### One coherence gap this slice made reachable (copy, not code — for the gate)

Before F1 the cap could never fire, so this corner did not exist. Now it does: a
reader who exhausts the five attempts sees 「이 인증번호는 더 이상 사용할 수
없습니다 — 인증번호 재전송을 눌러 새 번호를 받아 주세요.」 and, pressing 재전송
inside the first 60 seconds, is answered `resent: false`, which the panel renders
as 「조금 전 보낸 인증번호가 아직 유효합니다」 — a sentence that contradicts the
line above it and is, in this one branch, untrue: that code is dead, not still
valid. The flow still terminates correctly (wait out the remainder, press 재전송,
get a live code), and no backend behaviour is wrong — `issue_verification`'s
cooldown outranking every caller is exactly the anti-mail-bomb property S1
decided. It is a **drafted-copy** question, which is the operator's at the gate,
so it went on `## Operator Questions` rather than into a silent edit here.

## 6. What went to `phase.md`

- `## Decisions` — the attempt-counter line's "⚠ Corrected by P13.S2" clause replaced with the landed truth (superseded in place, not stacked).
- `## Notes for later slices` — the two S2 notes describing the defect consumed: the `for P13.REVIEW` cap-finding note removed entirely, and item (1) of the `for P13.S3` note dropped with the remaining two rewritten as a two-item note.
- `## Operator Questions` — one line under the S2 entry recording that the release-waits-for-F1 question is answered (it waited; it landed), plus the new copy question above.
- `## Doc impact` — appended:
  - `backend.md: verify_code's wrong-code branch **commits** before it raises — the one place mijual.web.auth commits, because the failed attempt is the write of record and get_write_session rolls back on any exception; the cap boolean is read before the commit (the test factory expires on commit); every other raise-after-write in the module was audited and intends its discard; the three test write-session overrides now mirror get_write_session (commit on return, roll back on exception) so the suite can see this class of bug (P13.F1)`
  - `security.md: amends P13.S1's claim — the 5-attempt cap was **inert between S1 and F1** (the increment was rolled back with the 400 it raised, so a 6-digit code was guessable without limit for its 10-minute life) and is **real from F1**: measured over HTTP, five wrong codes end the grant, the fifth answers verification_code_expired and the genuinely mailed code dies with it (P13.F1)`
  - `qa.md: regression — five wrong codes over HTTP kill the grant (answers 1–4 verification_code_invalid, the 5th verification_code_expired, the mailed code then also expired, the row reads attempts = 5); a fixture that commits without rolling back on exception cannot see it (P13.F1)`
- `## Now` — rewritten (the cap is real, S3 is unblocked on this count, the two release gates and the freeze still stand).
