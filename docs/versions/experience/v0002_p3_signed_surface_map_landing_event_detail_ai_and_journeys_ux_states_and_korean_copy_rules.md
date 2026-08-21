---
doc_id: experience
version: v0002
created_at: 2026-08-21T23:56:00+09:00
source: P3.REVIEW
summary: P3 signed surface map: 관제 현황판 landing, 내 종목 조회, event detail, 내 포트폴리오, AI 질문 and 운영 관제 — journeys, UX states and Korean copy rules
previous: v0001_bootstrap
---

# Experience

## Status

**Signed, not built.** P3's seven design rounds fixed the surface map, the journeys and the UX states
below; the operator closed each round with literal signoff. The per-surface implementation contracts
are `docs/reference/design/rounds/<NN>-<slug>/output/build-prompt.md` — this doc is the map, they are
the spec. Read `docs/reference/design/SIGNOFF.md` for what supersedes what (see `frontend`).

**Product surface is Korean only.** The team's own language is English.

## Route / Screen Map

Concrete URL paths were left to the build; the surfaces and their names are signed.

| surface | round | entry | gated? |
|---|---|---|---|
| **관제 현황판** (landing) | R2 | root | no |
| **내 종목 조회** (search + 보유량 환산 + 놓친 돈) | R4 | nav slot 1, landing hero submit, detail link-out | no |
| **Event detail** — ① 유증 신주인수권 · ② CB 오버행 · ③ 매수청구권 | R3 | board row | no |
| **내 포트폴리오** (auth + holdings + D-day + 알림) | R5 | **account menu's first row**, not a nav link | **yes — the only login-gated surface** |
| **AI 질문** (grounded 해설 agent) | R6 | nav slot 3 (page), desktop bottom-right launcher (widget), detail preset strip | no |
| **운영 관제** (admin) | R7 | a separate path (e.g. `/ops`), **linked from nowhere in the reader chrome** | yes — separate operator credential |

- **Nav is three slots: 내 종목 조회 · 관제 현황판 · AI 질문.** 내 포트폴리오 is deliberately not a
  fourth link (operator revision at R5). Right side: 로그인 + the vocky `[의견]` trigger.
- **Global chrome (R2):** 52px nav (white ring wordmark), mobile top bar + sheet menu, footer with the
  provenance sentence, the gate-cost sentence (its only placement) and the disclaimer.
- **vocky** is the feedback inception point: chrome-level triggers only (nav `[의견]`, mobile sheet row,
  footer link), each a plain element carrying `data-vocky-trigger`. The widget UI is vocky's own —
  no floating button, and never restyle the widget.

## Core User Journeys

### 관제 현황판 — the market-wide board (R2)

- **Entry:** landing. Search-first hero (H1 내 종목 연결 + console search + a mono stat line), then the
  retrospective value card + the countdown/stats card, the 소멸주의보 strip, and the board.
- **One page**, not two: the retrospective (소멸 총액) and the live board share the landing — this
  closes the open question `product` v0002 carried.
- **Board:** urgency-interleaved with rights-type tabs (전체 / 유증 / CB / 매수청구), sorted D-day
  ascending across types. **A row carries exactly one governing countdown.**
- **Success state:** the user recognises their own stock and submits the hero search → 내 종목 조회.

### 내 종목 조회 — anonymous instant conversion (R4)

- **Entry:** nav, hero submit, or a detail page's "내 보유량으로 환산 →" (arrives with the stock
  preselected). **Anonymous, no login, ever.**
- **Steps:** search → resolve stock → enter 보유량 (**direct integer input + preset chips 100·500·
  1,000주** — mono, right-aligned, instant recompute; **no slider**) → read the result.
- **One page, two sections:** 진행 중인 권리 on top, **2026년 놓친 돈** below. No mode toggle.
- **No 기간 picker.** A fixed factual coverage line ("집계 범위 2026-01-01 ~ 오늘 (KST)") plus a
  boundary panel (① 2026-01-01부터 · ② 2025-06부터). Outside the coverage the answer is *unstated*,
  never counted as 0.
- **Memory is session-only:** sessionStorage with a restore chip ("이전 입력 {n}주") — never
  auto-filled, never server-side.
- **놓친 돈 semantics:** the full 배정 증서 value under the do-nothing condition, framed
  "청약도 매도도 하지 않았다면" with the disclaimer footnote. ①'s 배정 신주 = ⌊N × 배정비율⌋,
  matching `mijual.calc.allotted_shares`.
- **②/③ rows are deadline rows with context, never a won amount.**

### Event detail — the trust claim made visible (R3)

- **Anatomy (all types):** crumb → craft header panel (master `corp_name` + RightsChip + DART ↗ +
  governing DDay) → ①-only 환산 블록 → field sections, each with its own `Citation` → 정정 strip →
  provenance line.
- **Only `exposable` fields exist in the DOM.** A blocked field has no row and no marker.
- **① 환산 블록 shows per-unit upstream values only** plus a link-out to 내 종목 조회 — the detail page
  never renders anything R4's math could contradict.
- **② :** an API fact strip above the 본문 fields; a past opening is **진행 중, never 종료**;
  `option_schedule` renders the filer's `detail` string with the bracket dates only as an annotated
  caption; a sparse ② closes with one factual line, never placeholders.
- **③ :** the 2단계 절차 as numbered structure with its dependency sentence; governing deadline =
  반대의사 통지 마감. **매수예정가 is not rendered** — it is not in the exposure contract (added at the
  apply phase as backing work, then a design-fidelity slice).
- **CorrectionStory:** a version rail (only the current readable version is live), old→new `field_moves`
  verbatim, and a deleted passage rendered as "(정정 후 본문에서 삭제됨)".

### 내 포트폴리오 — the personalisation layer (R5)

- **Conversion, never a gate:** an offer panel below a computed 조회 result (dismissable, once per
  session) and a one-line link under a detail D-day block. No forced modals; the nav 로그인 slot is
  untouched; every anonymous surface stays anonymous.
- **Portfolio:** R4's signed input primitive reused. Row edit confirms by the action column swapping
  수정·삭제 → 저장·취소 (horizontal). Delete is instant with an 8s undo — no modal. No page 대제목: the
  header nav is the only location indicator.
- **Anonymous / sample editing persists in localStorage**; account migration is **offered, never
  automatic** (session-held R4 values likewise, via a carry-over row).
- **D-day list:** 다가오는 마감 (D ascending) / 지나간 마감 (recent first), with the anchor date stated
  ("기준 YYYY-MM-DD (KST)"). R4's money rules apply verbatim.
- **챙긴 돈 checkbox** on lapsed ① rows — the user's own claim, flipping the label 놓친 → 챙긴 and the
  color alert → live on the same 「추정」 amount. **Never mixed into disclosure data or aggregates.**
- **Judge sample portfolio (one click):** a fixed composition of four real pinned events — 계양전기
  500주 (① live) · 대동기어 300주 (②) · 한화솔루션 500주 (① lapsed) · 세기상사 100주 (③). Entered from
  the login page and the landing footer; the loaded state shows an inset banner, a nav 「샘플」 chip and
  a 샘플 종료 control replacing the login slot. **No fake identity**, and notification settings are
  hidden in sample mode because no address exists.

### AI 질문 — the grounded explanation agent (R6)

- **Not the default surface.** The product opens on the board; the agent is a deliberate affordance.
  Desktop: a bottom-right launcher opens an **in-place opaque widget 440×620** — no backdrop, no dim,
  the page layout untouched. Nav slot 3 opens the **dedicated page**; the widget closes and the same
  conversation continues (one sessionStorage thread). **Mobile has no widget and no launcher** — one
  full-width page.
- **Presets first:** a detail page carries a question strip generated **only from gate-passing fields**
  (a question that cannot be answered is never offered); free input is one step behind.
- **Scope:** opened from a detail → that event (header chip + × to clear); otherwise 전체 공시,
  including portfolio questions.
- **Tool calls are visible** — each renders as a mono fact row (`이벤트 검색 「…」 → 1건 · ② …`). Tools:
  `search_events` / `get_event` / `get_portfolio` / `save_feedback` / `get_contact`.
- **The agent never calculates** (handoff §3.6). Every number is a verified-contract value; a
  calculation request is redirected to 내 종목 조회 with a fixed sentence.
- **A sentence without a citation cannot exist in the stream.** Citations are numbered evidence chips
  that arrive with their claims (no placeholder chips), tapping opens the verbatim quote in place.

### 운영 관제 — the operator's read-only panel (R7)

- **Six sections, every one a full page** with the ops bar (tabs · live lock chip · KST clock ·
  logout) and a bottom status footer: **개요 · 게이트 대기열 · 정확도·비용 · 대화 로그 · 사용자 ·
  피드백**. `Access` (the pre-auth door) is the one chrome-less surface.
- **Fully read-only — there are no mutation endpoints.** No review/clear/approve/re-run buttons: no
  action may silently override a gate verdict. Exposure changes only through the pipeline CLI.
- **Honesty patterns:** a beat that did not run renders an alert-ink 「실행 기록 없음」 row (derived from
  the scheduled time — silence is never allowed to pass as success); the `judged_by` provenance block
  renders **above** the accuracy numbers; the cumulative quota bar is labeled as not-daily; ▷ cost
  markers are printed verbatim from pipeline output.
- **Suppression reason codes render as raw English codes** — no Korean was invented (§6.1); unknown
  codes render verbatim with no fallback copy.

## UX States

- **Empty:** 검색 불일치 and no-event stock get their own worded states; "아직 확정 전" is a
  **first-class state, not an empty state** — a live ① usually has no 확정발행가 yet, so it shows share
  counts and the `발행가 확정 전` chip instead of money.
- **Loading:** text-swap only, never spinners ("답변 준비 중…", a button's own label replaced and
  disabled). SSE streaming shows a 1s-step caret; complete fades the footer in; interrupted **keeps the
  partial answer** and offers 재시도.
- **Stale / freshness:** a 기준-timestamp chip plus, when stale, an inset notice. **The board never
  dims** — stale-never-dark.
- **Absence and blocking:** a gate-failed field is simply absent — no placeholder, no dash. On the
  D-day slot, absence is stated factually ("현재 버전 공시에 없음").
- **Product states that are features, not errors:** **철회** replaces the body with the cited
  withdrawal notice; **추후결정** is a badge with **no date at all**; **발행사 기재 불일치** shows both
  readings side by side; a corp_name mismatch is a quiet 본문-표기 annotation.
- **Refusal (AI 질문)** is a reason-first family in body ink, **never alert-colored**: ① the locked
  state fact with its own citation ② "…는 해설하지 않습니다" ③ where to go instead. Five categories
  only: 철회 · 확정 전 · 공시에 없음 · 검증 미통과 폴백 · 계산 요청.
- **Permission:** exactly one reader surface is gated (내 포트폴리오). The admin door fails uniformly
  in constant time and never says which field was wrong.

## Copy and Tone

- **Korean only, and copy is locked by default.** Strings come from
  `docs/reference/design/grounding/copy-inventory.md`, which is generated from the code that emits them
  at runtime. A round could propose a change only by naming the string and the reason in its handoff —
  R2, R3, R4 and R5 each did, and the operator signed those strings with the round.
- **「추정」 marks every estimate; a fact carries no mark.** (`▷` is retired from the UI and survives
  only in docs and pipeline output.)
- Chrome labels are Korean; codes, identifiers and raw pipeline output stay English mono.
- Say what is true rather than what is comfortable: "전환청구 진행 중" not "종료";
  「대화는 익명으로 저장됩니다 (품질 점검용)」 rather than a false "저장 이력 없음".

## Open Questions

- Carried to the apply phase: the **"정정 이력" button label** (still unnamed at the end of P3), the
  countdown cut-off instant (assumed 2026-09-04 24:00 KST — the real 접수 마감 시각 is TBC), the stale
  threshold in hours, and the **운영자 연락처 string** for `get_contact` (operator-provided, never
  invented).
- 매수예정가 (③) is designed-out until the extraction/exposure backing exists.
- The vocky observation view ships a `?`-columned frame with 「API shape 확정 대기」 until the API shape
  is settled at the apply phase.
