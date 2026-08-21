---
doc_id: security
version: v0002
created_at: 2026-08-21T23:58:00+09:00
source: P3.REVIEW
summary: Security model decided in the P3 design: email+password reader auth with minimal PII, the separate admin door, read-only ops surfaces and the anonymity promise for conversation storage
previous: v0001_bootstrap
---

# Security

## Status

**Decided at the P3 design gates, not yet implemented.** No auth code, no HTTP layer and no session
handling exist — P3 was design-only. What follows is operator-signed and binding on the apply phase
(R5 = reader auth, R6 = anonymity, R7 §6.4 = the admin door). The contracts are
`docs/reference/design/rounds/{05-account,06-explain,07-admin}/output/build-prompt.md`.

The pipeline-side secret handling from P1/P2 (a gitignored `.env`, `GEMINI_API_KEY` reaching only the
SDK, no key in any artifact) stands unchanged.

## Auth Model

### Reader accounts (R5)

- **Identity: email + password.** The design session proposed a code-based flow; the operator revised
  it to email+password, and that revision is what was signed.
- **Password rule: ≥8 characters, and no other rule.** Reset is an emailed link.
- **Login and 계정 만들기 are one panel** with a switch link. Failure copy is a single body line
  (불일치 / 중복 가입 / 8자 미만); **a login error never says which field was wrong.**
- **Session:** logout is immediate with no confirmation dialog and a single "로그아웃되었습니다"
  message. Cookie flags and lifetime are apply-phase decisions; the ops cookie must be httpOnly,
  secure and **differently named** from the reader session.
- **Exactly one gated surface: 내 포트폴리오.** Every other reader surface stays anonymous, including
  AI 질문. No feature is withheld behind an account except personal holdings and their notifications.

### The admin door (R7 §6.4)

- **A separate credential — 운영자 ID + 비밀번호 — with no join to the reader account table and no
  admin flag on a reader row.** Credentials are issued and rotated in the deployment environment
  (env/secret), so there is **no signup and no reset UI**.
- **Uniform, constant-time failure**: 「자격증명이 올바르지 않습니다」 for every cause; never disclose
  which field was wrong or whether an operator exists. Attempt limiting is a server concern with no UI
  copy.
- **The panel lives on a separate path (e.g. `/ops`) and is linked from nowhere** in the reader
  chrome — not nav, not footer, not the account menu, not the sitemap. Session expiry returns to the
  door and restores the tab afterwards.

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
  click it away.
- **Suppression reason codes are rendered as raw English codes.** No Korean copy was invented for
  them; unknown codes render verbatim with no fallback string.

## Secret Handling

- Application secrets stay in the gitignored `.env` / deployment secret store: `GEMINI_API_KEY`,
  `DATABASE_URL`, the OpenDART key, and — new from P3 — the **operator credential** and the reader
  session signing key.
- Password storage is a **hash only**; the plaintext never persists.
- Binary design assets and the design project itself are outside the repo; nothing about them is a
  secret, but no credential may be embedded in a card or a handoff.

## Customer Data Boundaries

- **Stored PII for a reader account is exactly: email + password hash.** Nothing else — no name, no
  phone, no brokerage link, no market identity. The PII statement is a **permanent inset panel on the
  auth screen**, not a link to a policy page.
- **Account deletion wipes the email immediately.**
- **Anonymous state never reaches the server.** 조회 holdings live in sessionStorage; anonymous and
  sample portfolio edits live in localStorage. Migration into an account is **offered, never
  automatic** — no silent server-side capture of an anonymous user's holdings.
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

- [x] No secrets committed (P1/P2 practice unchanged; nothing new introduced by P3)
- [x] Auth rules documented — reader (R5) and operator (R7 §6.4), signed
- [x] Sensitive data paths documented — PII set, anonymous storage boundaries, the schema-level
      no-join promise
- [ ] Implement: password hashing, session cookies, constant-time admin failure, the no-join schema
- [ ] Verify at the apply phase that no reader-chrome surface links the ops path

## Open Questions

- Session lifetime, cookie names/flags, and CSRF handling — apply-phase decisions.
- The concrete admin route and how the operator credential is issued and rotated are **deploy**
  decisions (P4).
- The **운영자 연락처 string** the agent hands out via `get_contact` is operator-provided; it must never
  be invented, and it is the one operator-identifying string the product will publish.
- The vocky observation API's auth model is unknown until its shape is settled at the apply phase.
