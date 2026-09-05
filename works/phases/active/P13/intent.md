# Intent — P13

- Captured at: 2026-09-05T23:47:04+09:00
- Origin: operator

## Original Input (verbatim)

> 1. Email confirmation required when registration

## Confirmed Intent (refined + clarified)

Registration requires proving control of the email address, with a **6-digit code**, as a **hard gate**:

- `POST /auth/signup` creates the account **unverified**, mails a single-use 6-digit code to the
  address, and **opens no session** (today it starts a session and sets the cookie on the spot).
- The auth panel switches to a **code-entry state on the same surface** — no verify landing route.
  Entering the right code verifies the account and logs the reader in (the session starts there,
  the way `reset/confirm` already logs the reader in after proving mailbox control).
- Logging in with the **correct password on an unverified account** routes to the same code step
  with a **재전송** option instead of opening a session. This fires only after a correct password, so
  it discloses nothing a correct password does not already prove; the login failure line itself
  stays one code for wrong password / unknown address, as R5 requires.
- **Existing production accounts are grandfathered**: the migration marks every account that exists
  at upgrade time as verified. Only new signups go through the code.
- **No design round.** The phase drafts the new states and their Korean copy inside the signed
  R5/R12 auth vocabulary (one line-slot for every answer, body ink never `--alert`, the button's own
  text swapped and disabled while 확인 중, no modal or overlay) and the operator approves the exact
  strings at the acceptance gate. Same shape as P12.
- The verification mail is **proven live on production** at the end of the phase (a real code
  through the P4 SMTP transport), the way the reset mail was proven in P4.
- The acceptance gate is `--require`: the auth surface changes visibly.

### Recorded assumptions (operator-confirmed on 2026-09-05; override in a slice note if wrong)

1. **Code lifetime is short, about 10 minutes.** 재전송 issues a fresh code that **supersedes** the
   previous unused one — the same rule the password-reset grant follows.
2. **A 6-digit code is brute-forceable, so each code allows a handful of wrong attempts and then
   dies**; the reader must request a new one. This is a counter on the grant row, **not** the
   cross-process login rate limiting parked in P4.
3. **An unverified account does not block its address forever.** Signing up again with the same
   address inside the window re-sends a code (rather than answering 중복 가입), and stale unverified
   accounts expire.
4. **A password reset completed on an unverified account also marks it verified** — the reader just
   proved mailbox control.
5. **`mijual.mailcopy`'s structural "알림 외 메일 금지 — two kinds exist" rule becomes three kinds**
   (deadline alert · password reset · signup verification), stated deliberately in that module's
   docstring, never slipped in.
6. Migration + model change follow the existing Alembic path; the `account` row gains the verified
   fact, and the code grant gets its own table beside `password_reset` (or an equivalent the DECOMP
   decides), with the digest-not-token storage rule the reset grant already keeps.

### Out of scope

- Any change to the operator door (`/ops`), which has no signup.
- Verifying existing accounts at next login (explicitly declined — grandfathered instead).
- Soft gating (letting an unverified reader in and locking only 내 포트폴리오 or the D-day mail) —
  declined; the gate is hard.
- A design round or mockup for the new panel states.

## Clarifications Resolved

- Q: What exactly should the confirmation gate — hard (no session until confirmed), soft (session
  now, 내 포트폴리오 locked until confirmed), or mail-only (only the D-day mail waits)? —
  A: **hard gate, but sending a 6-digit code** (not an emailed link).
- Q: What happens to the reader accounts already on production (jujutower.com)? —
  A: **Grandfather them** — marked verified at migration time; only new signups go through the code.
- Q: The change adds visible states to the signed auth panel — design round (`paired` /
  `build-after`) or fix it directly? — A: **No design round**; the phase extends the existing auth
  vocabulary and the operator approves the strings at the acceptance gate.
- Q: The request starts with "1." — first of several items? — A: **Only this one for now.**
- Q: Confirm the phase as proposed (name, objective, six assumptions)? — A: **Confirmed, create P13.**

## Notes

- Context found at intake: the real SMTP mailer is proven live on production (P4.S2 / P4.S4, a real
  reset mail through `mail.privateemail.com:587`); the single-use emailed-grant pattern already
  exists in `password_reset` (digest storage, expiry, supersede-on-repeat, every session revoked);
  `frontend/components/auth/AuthPanel.tsx` holds the login/signup panel and pushes to
  `ROUTES.portfolio` after a successful signup. The auth surface's signed rules live in
  `docs/current/security.md` § *Auth Model* and `docs/current/experience.md` (인증 bullets).
- `docs/current/security.md` and `frontend`/`qa`/`operations` are flagged **STALE** by
  `workflow.py docs` (unconsolidated P12/P4 notes) — read them as evidence to check against
  `docs-debt`, not as current truth.
