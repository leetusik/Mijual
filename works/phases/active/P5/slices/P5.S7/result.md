# Result — P5.S7: Reader auth backend

Reader accounts exist: **email + password hash and nothing else**, scrypt from the
standard library, a **server-side session row** behind an `HttpOnly`/`SameSite=Lax`
cookie, a required CSRF header on every unsafe method service-wide, and a reset flow
behind a **mailer seam with a console transport**. **No new dependency** (`pyproject`
untouched), no OpenDART request, no model call, and **no existing route gated** —
anonymous surfaces stayed anonymous (`/board`, `/board/summary`, `/stocks` all still
answer 200 with no cookie).

## What landed

| file | what |
|---|---|
| `src/mijual/db/models.py` | `Account` · `AuthSession` · `PasswordReset` (+ `__all__`) |
| `src/mijual/web/passwords.py` | scrypt hashing, parameters carried inside the hash |
| `src/mijual/web/auth.py` | the service layer: normalization, sessions, reset, the FastAPI gates |
| `src/mijual/web/csrf.py` | the required unsafe-method header, service-wide |
| `src/mijual/web/routers/auth.py` | the seven endpoints (transport only) |
| `src/mijual/mail.py` | the mailer seam + `ConsoleMailer` |
| `src/mijual/web/deps.py` | `WriteSession` — the first committing dependency |
| `src/mijual/config.py` | `session_secret` · `cookie_secure` · `app_base_url` |
| `src/mijual/web/app.py`, `web/__init__.py` | wiring + the layer's own description |
| `tests/test_web_auth.py` | six terse DB-free cases |

## The endpoint map

| route | answer |
|---|---|
| `POST /auth/signup` | `201 {account:{email,created_at}}` + session cookie · duplicate → `409 email_taken` · short → `400 password_too_short` |
| `POST /auth/login` | `200 {account}` + cookie · any failure → `401 invalid_credentials`, **one code for both causes** |
| `POST /auth/logout` | `200 {authenticated:false}`, row deleted, cookie cleared, idempotent |
| `GET /auth/me` | `200 {authenticated:false}` or `{authenticated:true, account}` — **anonymous is a result, not a 401** |
| `POST /auth/reset/request` | `200 {requested:true}` **always**; the link goes only to the mailer |
| `POST /auth/reset/confirm` | `200 {account}` + a fresh cookie · spent/expired/unknown → `400 invalid_reset_token` |
| `DELETE /auth/account` | `200 {deleted:true,authenticated:false}`; no session → `401 unauthenticated` |

Every unsafe method additionally answers `403 csrf_required` without the
`X-Mijual-CSRF` header — checked before the route runs.

## Decisions recorded (the ones `security` left open)

- **Session = a row, not a signed cookie.** Logout is immediate and 계정 삭제 must kill
  access now; both are one delete. A stateless token would need a revocation list — i.e.
  this table — and would save no query, because the request path loads the account anyway.
- **Cookie `mj_session`** (ops door reserved as `mj_ops`, `auth.OPS_COOKIE`), `HttpOnly` ·
  `SameSite=Lax` · `Path=/` · `Secure` from `MIJUAL_COOKIE_SECURE` (off locally — a
  `Secure` cookie on plain http silently never arrives; **P4 must set it**).
- **Lifetime 30 days, absolute, never extended on a read** — a sliding window would have
  to write on a `GET`, and this service is now built so a `GET` structurally cannot.
- **CSRF = `SameSite=Lax` + a required custom header**, enforced service-wide by
  middleware rather than per route, so `P5.S8`'s mutations inherit it.
- **scrypt `n=2**14, r=8, p=1`** — stdlib, ~25 ms/hash measured, and the largest `n` that
  fits OpenSSL's default `maxmem` (`2**15` raises "memory limit exceeded"). Stored as
  `scrypt$n=16384,r=8,p=1$salt$key`, so the upgrade path is: bump `CURRENT`, and
  `needs_rehash` rehashes at the next successful login.
- **The token digest is keyed** with `MIJUAL_SESSION_SECRET` (HMAC-SHA256) — that is the
  "reader session signing key" `security` names, used to pepper rather than to sign. Unset
  = development, unkeyed, one log warning; `Settings.require_session_secret()` exists for
  P4 to fail a deployment instead.
- **Email normalization: NFKC + strip + case-fold the whole address**, plus-tags kept;
  only the normalized spelling is stored.
- **The mailer carries data, not copy** (`kind` + `data`), because writing a Korean
  subject line in P5 would be inventing product copy. P4 renders R5's signed mail.

## Validation

| command | outcome |
|---|---|
| `.venv/bin/python -m pytest` | **99 passed, ~1.6 s** (93 before; +6 cases), no network, no model, no DB |
| `python3 scripts/workflow.py validate` | `Workflow validation passed.` |
| out-of-suite curl pass, live Postgres (`uvicorn … --port 8077`, `MIJUAL_SESSION_SECRET` set) | all 15 steps as expected; **server stopped, corpus untouched, `accounts/sessions/resets = 0/0/0` afterwards** |

The curl pass, in order: signup **without** the header → `403 csrf_required` and **no row
written** · signup → 201 + `Set-Cookie: mj_session=…; HttpOnly; Max-Age=2592000; Path=/;
SameSite=lax` · `/auth/me` → the account · duplicate (different case) → `409` · wrong
password and unknown email → **byte-identical `401` bodies** · login (`CURL.READER@…`
resolves) · logout → `/auth/me` anonymous · reset request for a known **and** an unknown
address → identical `200 {"requested":true}`, with the link printed **server-side only**
(`[mail:password_reset] to=… url=http://localhost:3000/auth/reset?token=… expires_at=…`,
absent from both HTTP responses) · reset confirm → 200 + new cookie · same token again →
`400 invalid_reset_token` · old password `401`, new password 200 · `DELETE /auth/account`
→ row gone, and its reset row gone with it (cascade verified in Postgres) · login after
deletion → `401` · `/board/summary`, `/board`, `/stocks?q=한화솔루션` → 200, uncookied.

Stored shape confirmed in Postgres: `password_hash` = `scrypt$n=16384,r=8,p=1$…` (92
chars), `auth_session.token_digest` ≠ the cookie value.

The three tables were created with the sanctioned no-Alembic path:

```
.venv/bin/python -c "from mijual.db.models import Base; from mijual.db.schema_sync import ensure_columns; \
from mijual.db.session import create_all, make_engine; e=make_engine(); create_all(e); ensure_columns(e, Base)"
# new tables: ['account', 'auth_session', 'password_reset'] · added columns: []
```

The serving process still creates no schema at startup (it must answer while Postgres is
down), so this — or any pipeline entry point, which all run `create_all` — is how the
tables land in a deployment. Noted for P4.

## Deviations from `plan.md`

1. **The session signing key peppers a digest; it does not sign a cookie.** The plan
   offered both mechanisms and required the key to reach `Settings` "missing raises only
   on use". The server-side table won on immediacy, so the key has no signing job — it
   keys the stored token digest instead (a database dump then holds nothing replayable).
   Consequently **missing does not raise**: it degrades to unkeyed SHA-256 with a single
   log warning, because local dev must run without a secret. `require_session_secret()`
   is there, unused by P5, for a P4 deployment that would rather fail than start unkeyed.
2. **CSRF is enforced service-wide, not only on the routes this slice adds.** The plan
   said "apply it to every POST/PUT/DELETE this slice adds"; a guard each new route must
   remember is a guard a later slice forgets, so it is middleware. Strictly wider than
   asked, and it will apply to `P5.S8`/`P5.S9`'s mutations too.
3. **No attempt limiting was added** (the plan allowed it, server-side only). It is an
   operations decision `security` already says has no UI copy, and it needs shared state
   (Redis) that P4 owns; the enumeration-and-timing half of the threat is handled here
   instead (one failure code, and a burnt scrypt verification on the miss path).
4. **One extra structural guard**: `get_write_session` refuses a safe HTTP method
   outright, so "a GET never writes" survived the arrival of writes as a property of the
   wiring rather than a convention.

## Notes for the next slices

- `P5.S8`: hang holdings/preferences/챙긴 돈 off `account.id` with `ondelete="CASCADE"`
  **and** an ORM `cascade="all, delete-orphan"` (SQLite does not enforce FKs, so both
  halves are needed); gate with `auth.ReadAccount` / `auth.WriteAccount`; take
  `WriteSession` on mutations; every mutation needs the CSRF header. R7's 샘플 로드 여부
  and 알림 설정 belong on **your** table — `account` stays email + hash.
- `P5.S9`: the ops door is a separate credential with its own cookie (`mj_ops`), no admin
  flag on `account`, and its login POST also needs the CSRF header.
- `P5.S15`: the client sends `X-Mijual-CSRF: 1` on every unsafe request, renders the
  single Korean body line from the structural `code`, and owns the reset page at
  `MIJUAL_APP_BASE_URL` + `/auth/reset?token=…`.
