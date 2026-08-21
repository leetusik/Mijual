# Plan — P3.S6: Design round R5 — 개인화 2층: auth + portfolio + D-day + sample load (co-work)

## Shape

`co-work` slice, inline, two legs like S2–S5: **handoff leg** — write
`docs/reference/design/rounds/05-account/handoff.md`, commit, push (the slice's one push),
`set-slice-status P3.S6 pending`, STOP. **Read-back leg** — list_files → verify cards →
concreteness check → land under `rounds/05-account/output/` → phase.md append → signoff →
SIGNOFF append → pure regroup (`⏳ P3.S6 · Account`) → finish-slice → commit.

## Round scope (inventory items 7 + 8)

The personal layer over the anonymous experience:

- **Auth surfaces** — 가입 / 로그인 / 세션 / 로그아웃, minimal-PII framing, and the
  **conversion moment** from anonymous use (R4's 조회 keeps holdings session-only; the 2층
  is what makes them persistent + notified).
- **Portfolio** — manual holding registration and editing (종목 + 보유량; the only real
  personal input in the product).
- **Personal D-day list** — the user's own events ordered by urgency, per-type governing
  anchors (①: 증서 매매 마감, ②: 전환청구 개시, ③: 반대의사 통지 마감).
- **Notification settings** — email first, KakaoTalk later.
- **Judge-facing sample-portfolio one-click load** — instant demo of the 2층 without
  signup friction.

## Notes

- **Finding 8 governs grounding**: no user-side data exists — no account, no portfolio,
  no notification history. Real content = real corpus stocks/events composing a sample
  portfolio (계양전기 live ①, 한화솔루션 lapsed ①, plus ②/③ pinned samples); user
  identity/notification history must never be fabricated as if real — a sample portfolio
  is labeled as the sample.
- R4 signed decisions binding: anonymous holding input is session-only with restore chip;
  surface name 내 종목 조회. The conversion pitch is "저장 + 알림" — persistence and
  deadline notifications are the 2층's whole value.
- Required cards under `⏳ P3.S6 · Account`: auth flow (가입/로그인 + states), portfolio
  registration/editing, personal D-day list, notification settings, sample-load entry,
  mobile.
- Open questions posed to the session: what 가입 collects (minimal PII — email-only?),
  where the conversion moment lives (조회 result? nav?), sample-portfolio composition +
  entry placement (judge-visible), KakaoTalk-later presentation, the personal layer's
  Korean name/nav label, logged-in vs anonymous chrome difference.
