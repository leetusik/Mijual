---
doc_id: experience
version: v0003
created_at: 2026-08-22T18:16:30+09:00
source: P5.REVIEW
summary: P5 apply phase: the signed journeys as built, and what each surface refuses to state — verified in a real browser
previous: v0002_p3_signed_surface_map_landing_event_detail_ai_and_journeys_ux_states_and_korean_copy_rules
---

# Experience

## Status

**Signed in P3, built in P5.** The surface map, the journeys and the UX states below were fixed by
seven design rounds and closed by the operator's literal signoff; P5 implemented every one of them
except the AI 질문 agent (P6). The per-surface contracts remain
`docs/reference/design/rounds/<NN>-<slug>/output/build-prompt.md` — this doc is the map, they are the
spec. Read `docs/reference/design/SIGNOFF.md` for what supersedes what (see `frontend`).

**Product surface is Korean only.** The team's own language is English.

**Everything below marked "refuses to state" was measured in a real browser, not asserted.** The
fidelity pass drove ~230 checks across 11 stages at 1440 / 768 / 390 plus the intermediate widths;
the trust rules are the part of this doc that a reader's trust actually rests on, so they were
measured against the *served* payload rather than eyeballed.

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

### What the built surfaces refuse to state (measured)

The negative space is the product. Each of these was verified against the served payload:

- **No untagged estimate and no tagged fact**, anywhere, on any surface.
- **No money before 확정발행가** — on the detail page, in 조회, in the portfolio, or in mail. An
  unpriced ① shows the `발행가 확정 전` chip and the due date, while 배정 신주 and 초과청약 한도 still
  compute, because share counts are constructable and won amounts are not.
- **No per-holding won amount on a ②/③ row.** ② carries R4's three dilution facts (오버행 % · 전환 시
  주식수 · 전환가액 — the per-*share* context R5 calls ②'s substitute) and ③ the 2단계 dependency
  line. When testing this rule, test for the 보유량-기준 column, not for the character 원.
- **No holding ⇒ no derived number.** An empty field is not a zero: the 놓친 돈 headline appears only
  once a count exists, because "0원" under "청약도 매도도 하지 않았다면" would be a claim about a
  holding the reader never described.
- **40 board D-days byte-identical to the served `countdown.dday`**, and the landing countdown **0 s
  off** the served absolute instant — the browser only diffs.
- **A past ② reads 진행 중 and the word 종료 appears nowhere**; a 추후결정 row carries **no date
  anywhere near it**; a gate-blocked field is **absent**, never placeheld.
- **조회 and 포트폴리오 agree to the won** (한화솔루션 500주 = 679,575원 on both), because they share
  one multiplication site and one composition function.
- **A search miss names no reason, candidate or near-miss**; a non-renderable event 404s **without
  explaining itself**; a 철회 page renders **0 field rows and no countdown**; the 발행사 기재 불일치
  block shows both readings, cites each, and **never reconciles them**.
- **A staleness notice never dims the rows** — the chip flips, an inset notice appears, and the
  content renders identically.
- **Zero `position: fixed` elements** on every reader surface (P6's launcher corner stays clear), and
  **zero horizontal overflow** at 390px with every named tap target ≥44px.
- **The sample carries no account fact** — no email, no 알림 설정, no `claimed` key, no fake identity.
- **The ops panel is linked from nowhere**: six reader surfaces contain no `/ops` substring at all.

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

## Behaviours the build decided, within the signed vocabulary

Each of these was a gap the record left, resolved from the round's *own* nouns rather than by
inventing copy — recorded so a later surface follows the same reading:

- **An offer is an offer.** 세션 이월 and 계정 이전 are inset rows with 담기 / 담지 않기, never
  automatic; declining is a per-tab **flag, never a deletion**, so the browser keeps its value and a
  new session may ask again.
- **계정 삭제 arms in place** (the action column becomes 계정 삭제 · 취소, the round's own horizontal
  swap), because "즉시" plus "게이트 화면·강제 모달 금지" leaves no room for a dialog.
- **A repeat 담기 opens that row's 수정** instead of surfacing an error the round wrote no words for.
- **An authenticated visit to the 로그인 page redirects to 내 포트폴리오** — R5's fourth auth state
  *is* the 2층, and rendering a logged-in variant of the auth screen would mean inventing both a
  sentence and a control.
- **The error vocabulary is exactly three codes wide** (불일치 · 중복 가입 · 8자 미만); everything
  else renders **no line at all**, so an unsigned failure is never given words. Two otherwise-silent
  codes are held off *structurally* instead: the email input carries the service's own regex as its
  `pattern`, and CSRF is handled in the client.
- **An error line is body ink, never `--alert`** — that hue means expiring/lost, and an auth error
  may not spend the one colour reserved for a deadline.
- **확인 중 is the button's own text replaced and disabled** — no spinner element exists on the auth
  layer, and nothing anywhere on it is a modal or an overlay.
- **The conversion offer appears only after a per-holding value has rendered**, once per session,
  dismissible, in normal flow at the end of the page — and **not to a reader who already has an
  account**, because offering an account to an account holder is the 가짜 사용자 정체성 the round
  forbids. The detail one-liner is gated on the deadline still being ahead, because an alert for a
  passed anchor promises something nothing can send.
- **매수예정가 (③) now renders** as an ordinary field row under 발행 조건 — the backing landed
  (`appraisal_price`), superseding R3's "not rendered" line, and using the signed row anatomy rather
  than a new layout.
- **The CorrectionStory is an in-place disclosure, not a route**, because a route needs its own way
  back and the product's only crumb points at the board.
- **No 질문 스트립 on the event detail page.** R6's preset-chip strip is an agent entry point and
  belongs to P6 — a **phase boundary, not a dropped design element**. Likewise `/ask` ships as a bare
  shell with no invented copy and no fake chat, and the nav/footer slots render **AI 질문** (R6's
  superseded label), so nothing signed was dropped.

## Open Questions

- **The "정정 이력" button label** exited P3 unresolved and is still open; the detail page renders
  R3's literal and is now its second site.
- ~~The countdown cut-off instant~~ and ~~the stale threshold~~ — **stated defaults landed** (end of
  the 청약 day; 18 hours), both overridable per deployment with no code change. The operator may
  still choose other numbers.
- ~~매수예정가 (③) is designed-out~~ — **closed**: the backing exists and 12 of the 16 exposable ③
  events render it with a verbatim citation; the other 4 render **no row at all**.
- ~~The vocky observation view ships a `?`-columned frame~~ — **closed**: the shape is decided and the
  table renders the real column names. Its 연결 전 state keeps the signed 「API shape 확정 대기」
  sentence even though what it now waits for is the credential (see below).
- **The 운영자 연락처 string** for `get_contact` stays operator-provided and never invented — **P6's**.
- **Copy the record does not contain, none of it invented** (the full catalogue lives in
  `works/phases/active/P5/slices/P5.S19/result.md` §4): the not-found page's English sentence; an
  expired 재설정 link stating nothing; the half-stale 「API shape 확정 대기」; the footer's locked
  positioning sentence still saying 내 종목 연결; five composed labels; and the sample's signed 4건
  subline above five live D-day rows.
- **Two states the design never drew.** An ① whose 청약 has closed but whose 증권발행실적보고서 has not
  been filed falls into **neither** 조회 section, so its stock renders the no-event empty state
  (live: 센서뷰, 클로봇) — `pending` would render the wrong copy and a 놓친 돈 row would be a figure
  nobody filed. And R7's **샘플 로드 여부** column has no backing fact, so it renders as an honest
  absent. Both are design calls, not implementation ones.
