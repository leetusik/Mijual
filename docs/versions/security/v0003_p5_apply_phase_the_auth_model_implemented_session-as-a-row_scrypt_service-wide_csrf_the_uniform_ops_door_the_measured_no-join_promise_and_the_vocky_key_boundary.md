---
doc_id: security
version: v0003
created_at: 2026-08-22T18:09:31+09:00
source: P5.REVIEW
summary: P5 apply phase: the auth model implemented — session-as-a-row, scrypt, service-wide CSRF, the uniform ops door, the measured no-join promise and the vocky key boundary
previous: v0002_security_model_decided_in_the_p3_design_email_password_reader_auth_with_minimal_pii_the_separate_admin_door_read-only_ops_surfaces_and_the_anonymity_promise_for_conversation_storage
---

# Security

## Status

**Decided at the P3 design gates and implemented in P5.** The model below is signed *and* built:
reader auth, the portfolio gate, the operator door and the anonymity boundaries all exist in code and
were verified against live Postgres. Anything still marked open is either a **deploy** decision (P4)
or a **design** decision the operator owns. The signed contracts remain
`docs/reference/design/rounds/{05-account,06-explain,07-admin}/output/build-prompt.md`.

The pipeline-side secret handling from P1/P2 (a gitignored `.env`, `GEMINI_API_KEY` reaching only the
SDK, no key in any artifact) stands unchanged. **P5 added no new dependency** — session handling,
hashing, mail and the outbound vocky read are all stdlib.

## Auth Model

### Reader accounts (R5)

- **Identity: email + password.** The design session proposed a code-based flow; the operator revised
  it to email+password, and that revision is what was signed.
- **Password rule: ≥8 characters, and no other rule.** Reset is an emailed link.
- **Login and 계정 만들기 are one panel** with a switch link. Failure copy is a single body line
  (불일치 / 중복 가입 / 8자 미만); **a login error never says which field was wrong.**
- **Session:** logout is immediate with no confirmation dialog and a single "로그아웃되었습니다"
  message. **The four apply-phase questions are now answered in code:**
  - **The session is a row, not a signed cookie.** `auth_session` holds a **digest** of the token,
    never the token; 로그아웃 deletes the row and 계정 삭제 cascades. A cookie is worthless the
    instant its row is gone (verified live). A stateless cookie would have needed a revocation list —
    i.e. this table — and would have saved no query, because an authenticated request loads the
    account anyway.
  - **Cookie `mj_session`**: `HttpOnly` · `SameSite=Lax` · `Path=/` · `Secure` from
    `MIJUAL_COOKIE_SECURE` · **30 days absolute, never extended on a read**. A sliding window would
    have to write during `GET /auth/me`, and a GET may not write; renewal happens at the next login,
    which is already a write.
  - **CSRF is service-wide middleware**, not a per-route dependency: every `POST`/`PUT`/`PATCH`/
    `DELETE` must carry **`X-Mijual-CSRF`** (any non-empty value) or it is refused `403
    csrf_required` **before the route runs**. A cross-origin page cannot set a custom header without a
    preflight this service does not grant — and the frontend reaches the API through a **same-origin
    proxy**, so there is no cross origin at all. Nothing has to be minted, stored or rotated.
  - **Password storage: stdlib `hashlib.scrypt`, `n=2**14, r=8, p=1`** (~25 ms/hash) — the largest
    `n` that fits OpenSSL's **default `maxmem`**, because a parameter that only works with a private
    knob turned up is a login endpoint one deployment away from raising. Hashes carry their own
    parameters, so an upgrade bumps a constant and `needs_rehash` re-hashes each account at its next
    successful login — never a mass reset, never a locked-out reader.
  - **`MIJUAL_SESSION_SECRET` peppers, it does not sign** (HMAC-SHA256 over the token): a stolen
    database dump holds nothing replayable as a cookie or a reset link, and rotating the key logs
    every reader *and* operator out — the lever you want in that hour.
  - The ops cookie is **`mj_ops`**, reserved up front so the two can never collide.
- **Two prohibitions are structural, and were verified live.** A login failure is **one code for a
  wrong password and for an address with no account**, *and* the miss path burns a scrypt
  verification against a dummy hash so the two do not differ in timing. A reset request answers
  identically for a known and an unknown address, and the link **never appears in an HTTP response** —
  only in the server's own log (verified end to end).
- **A password reset revokes every existing session** and then issues a fresh one; a repeated
  재설정 request **supersedes** the previous unused grant rather than leaving a second live key in the
  mailbox.
- **Exactly one gated surface: 내 포트폴리오.** Every other reader surface stays anonymous, including
  AI 질문. No feature is withheld behind an account except personal holdings and their notifications.
  Verified: `/board`, `/board/summary`, `/stocks` and every event page still answer 200 uncookied, and
  `/portfolio*` is the only redirect to 로그인 in the app.

### The admin door (R7 §6.4)

- **A separate credential — 운영자 ID + 비밀번호 — with no join to the reader account table and no
  admin flag on a reader row.** Credentials are issued and rotated in the deployment environment
  (env/secret), so there is **no signup and no reset UI**.
- **Uniform, constant-time failure**: 「자격증명이 올바르지 않습니다」 for every cause; never disclose
  which field was wrong or whether an operator exists. **Implemented, and it is uniform for three
  causes, not two** — unknown ID, wrong password, and *no credential configured* return
  byte-identical 401 bodies (verified with `==` on the raw content). The ID goes through
  `hmac.compare_digest`, **both checks are always evaluated** (a short-circuit would leak "the ID
  exists" in the timing the uniform body exists to hide), and every path spends exactly one scrypt
  verification. Attempt limiting is a server concern with no UI copy, and it stays **P4**'s because
  it needs cross-process state.
- **The door is a credential with no row.** `MIJUAL_OPS_ID` / `MIJUAL_OPS_PASSWORD` from the
  environment, masked in `Settings.__repr__`; **no operator account, no admin flag, no signup, no
  reset**, and `ops_session` carries **no `account_id`, no FK and no operator identifier at all**.
  Cookie `mj_ops`, **12 hours absolute, never extended on a read** — a working day, deliberately not
  the reader's 30, because an operator console should not still be open the next morning. Expiry
  answers `401 ops_unauthenticated`.
- **The panel lives on a separate path (e.g. `/ops`) and is linked from nowhere** in the reader
  chrome — not nav, not footer, not the account menu, not the sitemap. Session expiry returns to the
  door and restores the tab afterwards. **Measured, not asserted:** six reader surfaces contain no
  `/ops` href **and no `/ops` substring at all** (the ops path map deliberately lives in the ops
  module, not in the shared route module, so no reader-chrome file can import one); a reader
  `mj_session` opens nothing; and the door renders **in place at the requested URL** with no
  `?next=` and nothing stored, so the operator returns to the tab they were on.

## Authorization Rules

| resource | who can do what |
|---|---|
| board, event detail, 내 종목 조회, 놓친 돈, AI 질문 | anyone, anonymously; no login gate, no signup prompt that blocks |
| 내 포트폴리오 (holdings, D-day list, notifications) | the authenticated owner only |
| 운영 관제 (all six sections) | an authenticated operator, **read-only** |
| exposure state (what the product shows) | **nobody through the UI** — only the pipeline CLI |

- **The admin panel has no mutation endpoints at all** (§6.5). There is no review / clear / approve /
  re-run button, and the queues carry no status bits. This is a security property, not a convenience
  choice: **no action may silently override a deterministic gate verdict** (handoff §3.6). The
  guarantee that a field failing its gate is never shown would be worth nothing if an operator could
  click it away. **Now structural:** of the thirteen `/ops` routes, eleven are `GET` and the only two
  unsafe methods are login and logout, which touch nothing but the operator's own session row — a
  test asserts the documented OpenAPI surface carries no other unsafe method under `/ops`. 행 검사 is
  a plain GET whose state lives in the URL, and no tab carries an action control.
- **A stranger's row is a 404, not a 403.** Every holding lookup carries `account_id` in its `WHERE`,
  so a row belonging to somebody else is indistinguishable from one that does not exist. A 403 would
  confirm that it does.
- **Suppression reason codes are rendered as raw English codes.** No Korean copy was invented for
  them; unknown codes render verbatim with no fallback string. A reader payload carries **no** gate
  reason at all — why a field is missing is operator truth.

## Secret Handling

- Application secrets stay in the gitignored `.env` / deployment secret store: `GEMINI_API_KEY`,
  `DATABASE_URL`, the OpenDART key, the **operator credential**, the reader session key
  (`MIJUAL_SESSION_SECRET`), and — new from P5 — **`MIJUAL_VOCKY_API_KEY`**.
- Password storage is a **hash only**; the plaintext never persists.
- **The vocky key boundary.** A `vk_`-prefixed key in `Authorization: Bearer`, held **only** by the
  backend and never by the browser: masked in `Settings.__repr__`, raising only on use, never logged,
  never in a URL. Three findings belong here: vocky has **no read-scoped credential** (the same key
  can write), so read-only is enforced Mijual-side by issuing `GET` and nothing else *and* by a test
  that lets **only `web/vocky.py` import an HTTP client**; **redirects are refused**, because
  `urllib` re-sends `Authorization` to the redirect target and a redirected base URL would hand the
  key to whatever answered (a non-`http(s)` scheme is refused for the same class of reason); and
  vocky's error body is **never echoed** onto the panel.
- Binary design assets and the design project itself are outside the repo; nothing about them is a
  secret, but no credential may be embedded in a card or a handoff.

## Customer Data Boundaries

- **Stored PII for a reader account is exactly: email + password hash** (+ created/updated
  timestamps). Nothing else — no name, no phone, no brokerage link, no market identity, **no admin
  flag**, no activity trail, and no column that could join an account to a conversation. The PII
  statement is a **permanent inset panel on the auth screen** (both auth pages), not a link to a
  policy page.
- **Account deletion wipes the email immediately**, and the cascade takes sessions, reset grants,
  holdings, claims and preferences with it (verified in Postgres: all six reader tables back to 0).
- **Anonymous state never reaches the server, and that is now structural: there is no anonymous write
  endpoint at all.** 조회 holdings live in sessionStorage (`mijual.lookup.holdings`); the sample
  portfolio's edits and 챙긴 돈 marks live in localStorage (`mijual.portfolio.sample`); the two
  "offer declined" flags live in sessionStorage. Migration into an account is **offered, never
  automatic** — when the reader accepts, the browser makes ordinary *authenticated* writes; when they
  decline, nothing is sent. The sample carries **no account fact**: no address, no 알림 설정, no
  `claimed` key, no fake identity (verified: `claimed` and `@` appear nowhere in the sample body).
- **A 챙긴 돈 mark is a user assertion, and it is quarantined by design.** The table stores account +
  filing number + timestamp and **no amount**, and **the payload has no total anywhere** — so "집계·
  통계에 미반영" is structural rather than careful. `claimed` is **absent, never `false`**, when
  nobody is logged in, because a server-side `false` would be the product asserting something about a
  person it has no account for.
- **Leaving a session is a full document load.** 로그아웃, 계정 삭제 and 샘플 종료 all navigate rather
  than route, so no gated payload survives in a client cache and Back cannot restore a signed-in
  surface.
- **The reader's minimal-disclosure rule reaches the ops panel too:** 사용자 shows a **count** of
  portfolio holdings and never their contents, the two tables on that tab are two independent reads
  that are **never joined**, and R7's 샘플 로드 여부 column renders as an **absent fact** rather than
  asserting `false` (see Open Questions).
- **AI 질문 conversations are stored server-side and are genuinely anonymous** (operator revision R6-6):
  - **the 계정 ↔ 대화 join is absent at the schema level** — the two tables have no relation, which is
    what makes the promise structural rather than procedural;
  - the operator's log viewer stores and shows **no account, email, IP or user-agent column**;
  - `save_feedback`'s reply email is optional and explicitly voluntary;
  - the vocky feedback view and the agent conversation queue stay separate surfaces because they carry
    different privacy contracts — cross-links only.
- **The UI copy must match the storage reality.** 「대화는 익명으로 저장됩니다 (품질 점검용)」 is
  required; "저장 이력 없음" or "탭을 닫으면 사라집니다" are forbidden — screen persistence
  (sessionStorage) must never be described as deletion.
- **Notifications: email only.** The KakaoTalk row is visible with a 「예정」 chip and **no control**.
  **No marketing or digest mail, ever** — only the deadline notifications the user configured. In
  sample-portfolio mode notification settings are hidden, because no address exists.

## Rate Limits / Abuse Cases

- **AI 질문 is unlimited and anonymous** (operator revision): there is no quota, and therefore **no
  quota display anywhere** — a limit that is not enforced must not be implied. If rate limiting becomes
  necessary it is an operations decision with **no UI copy**.
- Admin login attempt limiting: server-side, no UI copy.
- The agent's tool surface is the abuse boundary worth watching: `search_events` / `get_event` /
  `get_portfolio` / `save_feedback` / `get_contact` are the whole set, they are read-only except
  `save_feedback`, and `get_portfolio` must resolve only the caller's own session/account.

## Security Checklist

- [x] No secrets committed (P1/P2 practice unchanged; P5 added no key to the repo — the ops
      credential and the vocky key are environment-only, and the operator's `.env` was never opened
      by any slice)
- [x] Auth rules documented — reader (R5) and operator (R7 §6.4), signed
- [x] Sensitive data paths documented — PII set, anonymous storage boundaries, the schema-level
      no-join promise
- [x] **Implemented: password hashing (scrypt, versioned parameters), session cookies (row-backed,
      peppered digests, `mj_session` / `mj_ops`), the three-way constant-time admin failure, and the
      no-join schema** — the last one trivially, because P5 creates no conversation table at all
- [x] **Verified that no reader-chrome surface links the ops path** — six reader surfaces contain no
      `/ops` substring, measured in a real browser
- [x] Service-wide CSRF on every unsafe method, enforced before the route runs
- [ ] **P4:** set `MIJUAL_COOKIE_SECURE` and `MIJUAL_SESSION_SECRET`, implement the real `Mailer`,
      add login attempt limiting (needs cross-process state), and issue/rotate the operator
      credential and the vocky key

## Open Questions

- **Re-authentication for 수신 주소 변경** — *the one consequence worth an operator's eye*.
  `PATCH /auth/account` accepts a live session as authority and asks for no password, matching R5's
  Notify card (a 변경 affordance with no password field) and the 계정 삭제 precedent, which is
  strictly more destructive and also takes none. The honest consequence: **a stolen live session can
  move the address, i.e. escalate read access into a permanent takeover.** Adding a password prompt
  would be **inventing a control the signed round does not have**, so this is an operator/design
  call, not an implementation one. Mitigations already in place: changing the address revokes any
  outstanding unused reset grant (a grant issued *to an address* that is no longer this account's
  must not stay live), while sessions are deliberately not revoked, since the reader is the one doing
  it.
- **R7's 샘플 로드 여부 column has no backing fact.** The sample is anonymous end to end and there is
  no anonymous write endpoint, so nothing server-side ever learns that a reader loaded it. The
  payload carries **no `sample_loaded` key** rather than an invented `false`, and the column is
  data-driven — it appears iff a served row carries the key, so today there is no column and no
  placeheld cell, and building the backing later needs no frontend change. Building it would mean a
  holding-provenance column plus a client-visible parameter: a change to a signed contract *and* a
  new behavioural fact about a reader, which minimal disclosure argues against. **Operator/design
  call.**
- The concrete admin route and how the operator credential is issued and rotated are **deploy**
  decisions (P4). `/ops` is the local choice, matching R7's own example.
- The **운영자 연락처 string** the agent hands out via `get_contact` is operator-provided; it must never
  be invented, and it is the one operator-identifying string the product will publish. **P6's.**
- **Expired session rows are never pruned.** `auth_session` and `ops_session` are checked against
  `expires_at`, so an expired row grants nothing — but nothing deletes it either, and the tables grow
  monotonically. A reaper (or a partial index) is a **P4** operations item, not a correctness one.
- ~~The vocky observation API's auth model~~ — **settled in P5**: a `vk_` key in
  `Authorization: Bearer`, project- or org-scoped, backend-only. The residual finding is that vocky
  offers **no read-scoped credential**, so the key Mijual holds *could* write and read-only is
  enforced on this side (see Secret Handling).
