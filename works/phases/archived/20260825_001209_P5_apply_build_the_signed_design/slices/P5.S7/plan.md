# Plan — P5.S7: Reader auth backend

## Context

Read `works/phases/active/P5/phase.md` (S1–S6/S20 findings binding — especially S1
note 4: `DbSession` is rollback-only, so **this slice adds the first committing
dependency**, and a GET must still never write) and the two governing documents:
`docs/current/security.md` (the R5-signed auth model — binding) and the R5
`build-prompt.md` (`rounds/05-account/output/`) for what the surfaces will demand of
this backend. DECOMP notes 5(b) and 6 apply: **no column that could later enable a
계정↔대화 join**, and the reset flow goes behind a **mailer seam with a dev/console
transport** (P4 plugs in the real transport).

## Deliverables

1. **Account model** — a new table via `create_all` (no Alembic): **email +
   password_hash and operational timestamps only**. No name, no phone, no flags, no
   admin bit (the admin door is a separate credential, S9), nothing joinable to a
   future conversation table. Email unique, case-normalized (record the normalization).
2. **Password hashing** — ≥8 chars is the *only* rule (structural check server-side;
   the Korean copy is the client's). Pick the hash: prefer a stdlib-only KDF
   (`hashlib.scrypt` with per-user salt and versioned parameters) unless you find a
   strong reason for a dependency; record the choice and the parameter-upgrade path.
   Plaintext never persists, never logs.
3. **Session** — cookie-based. Decide and record (they are named apply-phase decisions
   in `security.md` Open Questions): cookie name (must differ from the future ops
   cookie), httpOnly + SameSite (Lax unless you record why not) + secure-in-prod
   (config-driven — local dev is http), lifetime, and the mechanism (a signed token
   with the reader session signing key from `.env`/settings, or a server-side session
   table — pick one, record why; remember logout is immediate and account deletion
   must kill access). **CSRF**: decide and record a concrete posture for a
   cookie-authed JSON API (e.g. SameSite=Lax + a required custom header on
   state-changing routes); apply it to every POST/PUT/DELETE this slice adds.
4. **Endpoints** (committing dependency, error envelope, structural codes — no new
   Korean; the single-body-line failure copy lives client-side):
   - 계정 만들기 (signup): email + password → account + session. Duplicate email →
     structural error (the client renders 중복 가입).
   - 로그인: **failure never says which field was wrong** — one structural code for
     bad-email-or-password.
   - 로그아웃: immediate.
   - Me/session probe: who am I (the chrome's abbreviated-email menu needs the email).
   - Reset request: always the same response whether or not the email exists (가입
     여부 비노출); issues a single-use, expiring token through the **mailer seam**
     (an interface with a dev/console transport that logs/prints the reset link
     server-side; no real mail in P5). Reset confirm: token + new password.
   - 계정 삭제: wipes the row (email gone immediately — `security.md`), kills the
     session. Holdings cascade is S8's concern; design the FK so S8 can hang
     holdings off the account with delete-cascade.
5. **Tests** — terse, DB-free (in-memory SQLite + overrides, the established
   pattern): signup→login→me→logout; wrong-password and unknown-email produce the
   same structural error; duplicate signup; reset round-trip through the console
   transport; deletion removes the row and invalidates the session; a GET through
   `DbSession` still cannot write (existing guarantee untouched). Baseline 93 ≈ 1.2 s.

## Constraints

- Anonymous surfaces stay anonymous — nothing in this slice may gate an existing
  route; 내 포트폴리오 (S8) is the only gated surface, later.
- Secrets: the session signing key joins `Settings` (env/`.env`, masked repr, missing
  raises only on use — follow `mijual.config`'s existing pattern). Never invent a
  default secret in code for production paths; a dev fallback must be explicit and
  recorded.
- No rate limiting UI/copy; if you add attempt limiting, server-side only and terse.
- No email-sending dependency; the seam + console transport only.
- New deps: only if genuinely needed (hashing preference above); follow `pyproject`'s
  commented style.

## Validation

- `.venv/bin/python -m pytest` — green.
- Out-of-suite curl pass (live Postgres): signup, login, me, a state-changing call
  without the CSRF header refused, logout, reset request (console transport prints),
  reset confirm, login with new password, delete, login now fails. Stop the server.
- `python3 scripts/workflow.py validate`.

## Wrap-up

`result.md`; `phase.md` *Findings & Notes* (the recorded decisions: cookie/CSRF/hash/
session mechanism; the endpoint map + FK seam S8 builds on; what S15's surfaces get
structurally) and *Doc impact* (`security` — the implemented model + decided
open questions; `api`; `backend`; `data` — the account table; `qa`). Structured
verdict. No commits, no status transitions.
