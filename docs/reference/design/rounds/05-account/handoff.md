# Design Handoff — Round 5: 개인화 2층 — 가입 · 포트폴리오 · D-day · 샘플 불러오기

- Round: **R5 of 7** · slice `P3.S6` · written 2026-08-21
- Status: OUT — awaiting the design session (Claude Design + operator)
- Repo: `leetusik/Mijual` via Connect GitHub (main, pushed at handoff commit)
- Builds on: **R1–R4 signed designs** (locked — cosmos theme, craft panels, chrome, trust
  primitives, 「추정」 mark, detail contracts, and R4's 내 종목 조회 with session-only
  holding memory). Changing any of them is a new superseding round.

## 1. Product context

Everything designed so far is anonymous. This round designs the **2층**: an account that
makes the anonymous experience persistent — the operator's confirmed intent names auth as
required ("auth related required"). The conversion pitch writes itself from R4's signed
constraint: the 조회 surface remembers a holding **only for the browser session** ("탭을
닫으면 사라집니다"). The 2층 is where that stops being true: 저장된 포트폴리오 + 마감
알림. Design the moment where an anonymous user meets that offer, and everything behind it.

The **judge-facing sample portfolio** is a first-class requirement, not a demo hack: a
challenge judge must experience the personal layer in one click, without signup friction.

## 2. Scope checklist — what this round must cover

- [ ] **Auth surfaces** — 가입, 로그인, logged-in session state, 로그아웃, error/loading
      states. **Minimal-PII framing**: the product needs an address to notify and nothing
      else; make the frugality visible (the same trust posture as "서버 전송 없음" in R4).
- [ ] **The conversion moment** — where and how the anonymous experience offers the 2층
      (on the 조회 result? on the D-day-bearing surfaces? in the nav?). It must never
      block the anonymous path — R2–R4's surfaces work without an account, full stop.
- [ ] **Portfolio registration & editing** — add a stock + 보유량 (the same input
      primitive R4 signed — reuse, don't redesign), edit, remove, and the empty portfolio
      state. Includes what happens to a session-held R4 input on signup (carry it over?).
- [ ] **Personal D-day list** — the user's own events ordered by urgency, per-type
      governing anchors (①: 증서 매매 마감, ②: 전환청구 개시, ③: 반대의사 통지 마감),
      urgency styled color-never-size per the locked system; per-holding money where the
      chain exists (① with 확정발행가 — same rules as R4, this list must not contradict
      내 종목 조회).
- [ ] **Notification settings** — email now; **KakaoTalk later** (how "later" is shown
      honestly — no dead controls pretending to work).
- [ ] **Sample-portfolio one-click** — entry placement (judge-visible without hunting),
      what it loads, and how the loaded state is labeled as the sample rather than a real
      account. Composition below (§4).
- [ ] **Logged-in chrome** — what changes in nav/footer when a session exists (R2's
      chrome is signed; this round may *extend* it for the logged-in state, never restyle
      it).
- [ ] **Naming** — the personal layer's Korean name + nav label (the nav slot next to
      내 종목 조회 / 관제 현황판 / 해설 — all still provisional except 내 종목 조회).
- [ ] Desktop + mobile compositions.

Cross-cutting: Korean-only; copy from `copy-inventory.md`, new strings logged as proposed
chrome copy; 「추정」 on every estimate; mobile-first; a11y floor; fade-only motion.

## 3. Locked vs. in play

**Locked:** R1–R4 signed systems (including R4's holding-input primitive and its
session-only semantics for anonymous use); the D-day/urgency/money display rules;
Korean-only surface; anonymous surfaces never gated behind auth; no real user data exists
(§4); notification channels: email first, KakaoTalk later.

**In play:** everything visual and compositional — the auth flow shape and what 가입
collects, the conversion moment's placement and copy, portfolio page layout, D-day list
composition, notification-settings presentation, sample-load entry and labeling,
logged-in chrome state, the layer's name, the mobile pattern.

## 4. Where to look — real content, never lorem

**Finding 8 (phase notebook) governs this round**: no user-side data exists — no account,
no portfolio, no notification history. What IS real: the corpus events. So:

- **The sample portfolio is composed of pinned real stocks** — e.g. 계양전기 (live ①,
  D-5 증서 매매 마감 2026-08-25, pre-확정발행가 — `samples/r1-live-healthy.json`),
  한화솔루션 (lapsed ① — the R4 money chain, `samples/r1-money-chain.json`), plus ②/③
  from the pinned set (`samples/r2-option-schedule.json`, `samples/r1-lapse-mismatch.json`,
  the ③ samples) — see `grounding/sample-events.md` and `board-snapshot.md` for their real
  dates and per-type anchors. Real events, real deadlines, labeled as the sample portfolio.
- **User identity is never faked as real**: no invented emails presented as accounts, no
  fabricated notification history rows. A settings mock may show the field shapes; state
  labels ("구성 예시") where identity appears, as `LookupEmpty` did for 삼성전자.
- D-day list money rules: R4's landed contract (`rounds/04-lookup/output/build-prompt.md`)
  — ① with 확정발행가 gets 「추정」 amounts, pre-확정 gets shares only, ②/③ never money.
- Copy: `grounding/copy-inventory.md`; trust posture: `grounding/states-and-trust.md`.

Missing real content → ask; never invent.

## 5. Required outputs (a round is incomplete without all three)

1. **Card set** — line-1 `@dsCard` markers, review-time group `⏳ P3.S6 · Account`:

   - `account/Auth.html` — 가입 + 로그인 + their states, minimal-PII framing
   - `account/Convert.html` — the conversion moment(s) in context (anonymous → offer)
   - `account/Portfolio.html` — registration/editing + empty state
   - `account/DDayList.html` — the personal D-day list on the sample portfolio
   - `account/Notify.html` — notification settings (email now, KakaoTalk honestly later)
   - `account/SampleLoad.html` — the judge one-click entry + loaded/labeled state
   - `account/AccountMobile.html` — the 2층 at 390px

   Split further freely; never a monolith.

2. **Record of what was designed** — refresh `handoff-output/result.md`; log every
   departure and all proposed copy.

3. **Implementation contract** — refresh `handoff-output/build-prompt.md`; state the
   token delta explicitly (none expected, but say so).

**Definition of done: the cards appear in the pane** under `⏳ P3.S6 · Account` and the
refreshed record + contract exist.

## 6. Open questions — posed to the session, not answered here

1. What does 가입 collect — email-only (magic link / code), or email + password? (The
   auth mechanism is apply-phase backing; what's being decided is the *surface* and its
   PII posture.)
2. Where does the conversion moment live — 조회 result after a computed value, the nav,
   both? What is its copy?
3. On signup, does a session-held R4 holding carry into the new portfolio (offered, not
   silent)?
4. Sample-portfolio composition (which pinned stocks) and entry placement — landing? the
   로그인 page? How is the sample state labeled and exited?
5. How is KakaoTalk-later presented — absent, or visible-but-labeled (예정)?
6. What is the personal layer's Korean name / nav label?
7. Do notification emails have a designed surface in this round (a preview of what the
   user receives), or is that apply-phase?

## 7. Operator setup + definition of done

Same project; pull latest `main` in the session first (this handoff + R1–R4 landed
records). When the cards are up and the record/contract refreshed, tell the orchestrator
to resume. Approval must be literal.
