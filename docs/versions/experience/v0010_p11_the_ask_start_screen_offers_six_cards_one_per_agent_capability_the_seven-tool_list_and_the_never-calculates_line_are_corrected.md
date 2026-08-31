---
doc_id: experience
version: v0010
created_at: 2026-08-31T16:13:41+09:00
source: P11.REVIEW
summary: P11: the /ask start screen offers six cards, one per agent capability; the seven-tool list and the never-calculates line are corrected
previous: v0009_p10_round_2_r6_s_launcher_motion_exception_expired_the_launcher_is_a_32px_sparkle_with_zero_animations_and_a_colour_hover_that_survives_reduced_motion_and_the_footer_s_corner_reservation_makes_clickable_at_every_desktop_width
---

# Experience

## Status

**Signed in P3, built in P5 and P6.** The surface map, the journeys and the UX states below were
fixed by seven design rounds and closed by the operator's literal signoff; P5 implemented every one
of them except the AI 질문 agent, and **P6 implemented that** — then verified it against the record
in a real browser at 1440 · 768 · 481 · 480 · 390 with a live agent. **P7 (실서비스 정상화) changed
five things a reader can see** — every one an override this doc now records inline, marked **(P7)** —
and re-verified all eleven of the operator's complaints on the operator's own origins in `next dev`
*and* in a production build. The per-surface contracts remain
`docs/reference/design/rounds/<NN>-<slug>/output/build-prompt.md` — this doc is the map, they are the
spec. Read `docs/reference/design/SIGNOFF.md` for what supersedes what (see `frontend`).

**P8 (디자인 폴리시 패스) re-cut every reader surface, one signed round per surface (R8–R14), with no
new features.** Surface 8 (운영 관제) was cancelled by the operator and is unchanged. What a reader
meets that they did not before:

- **Chrome.** Two nav destinations (AI 질문 · 보유 종목) — 관제 현황판 *is* the wordmark, so the
  landing carries no active underline; the `[의견]` chip is gone. The account slot is a hairline frame
  with the **full email** + a 20px identicon + ▾, and its menu is three rows: 알림 설정 · **의견
  보내기** · 로그아웃. The ≤480 menu is an **overlay with a backdrop** that never pushes the page
  (Esc / backdrop / × close it; the body scroll lock is counted, because two overlays can now be on
  one screen). The footer is one hairline, one row, no mono — the four prose sentences are gone, and
  the gate-cost and 면책 sentences are **dropped, not relocated**. 의견 보내기 is the product's own screen
  with six states and **three** entry points (footer · 모바일 시트 · 계정 메뉴); it has no contact
  field and says so.
- **관제 현황판.** The board's window is **15 / +15**, and its footer names three things —
  「15건 더 보기」 · 「남은 N건」 · 「처음 15건으로 접기」 — with **no controls at all** when nothing is
  hidden. The numbers on the surface are now *explained* (tab = whole board, list = the countdown's
  ranked subset) with a visible four-step D-day ladder. A row is a **single click target**; a strip
  says 접기 when open; the countdown card carries **three** stats, not four; and the 소멸주의보 says
  「N개 종목」 instead of picking one company out of a tied 청약 마감. **The page refreshes itself
  while it is open** — every 60 s, with the 기준시각 chip as the only place that says so: no spinner,
  no button, no layout move, and nothing at all when the served `as_of` has not moved.
- **Event detail.** One panel per event instead of five. Evidence opens **over** the page, so a reader
  scanning values never loses their place. A section of the filing's own words is closed by one source
  line instead of a chip per row. 「기한 지남」 is the single word for a closed window and **「종료」
  exists nowhere**. The 담기 line is 「보유 종목에 담기 →」 and appears only while a deadline is still
  ahead. Every target on the surface is ≥44px at 390. An absence is stated in a field row (the dashed
  「현재 버전 공시에 없음」 chip) rather than dropping the section.
- **조회.** The reader is told **which stock they are on** before any number appears — the `h1` is the
  종목명, with 종목코드/고유번호 under it and the search box echoing the name. The 보유량 field exists
  only where a number on the page moves with it. A stock's 전환사채 rows read as **one table** instead
  of one panel each. A 놓친 돈 total appears only when there is more than one offering to total. The
  page offers exactly **one** way out of a row (상세 보기 →). `/stocks` with no query states what the
  product watches instead of being a void.
- **인증.** Two pages that are no longer the product's one dead end (the rail is an exit). The
  password rule is stated **before** the reader spends a submit on it. 재설정 with an empty address
  **points at the field it needs** instead of greying out. One line-slot answers every failure, in
  body ink — the browser's English validation bubble is gone. The logout receipt sits **above** the
  title rather than where this form's answers stand. The 전환 제안 is an inset band after the numbers
  it answers, with no closing reassurance line.
- **보유 종목** (the layer is never called 「포트폴리오」 on a reader surface). Both D-day sections share
  **one** set of four edges and **one** anchor line. 「놓친 돈 상세 →」 stands inside the money line and
  is absent on a checked row, returning on uncheck, with a **measured 0px** shift. An empty 진행 중인
  권리 cell is a dashed rule, not a sentence. The delete confirm is an in-place column swap with an
  8-second undo row. **알림 설정 is no longer a frameless page**: it has a title and a way out, and
  the 계정 삭제 consequence is stated **only while armed**.
- **AI 질문.** 「보내기」 is the composer's idle word; a send that cannot be pressed is a ghost, not a
  dimmed solid. An answer grows as **one paragraph**. 「근거 N건」 counts the numbers on the screen
  (하나의 근거 = 하나의 칩). A preset chip **shows the served field name and sends a signed question**,
  so the thread no longer shows noun-phrase questions. A span-less citation is its DART link alone.
  A 접수번호 in a 도구 행 never breaks mid-number — it scrolls. **Below 768 there is no launcher and
  no widget at all**: every window under the line gets the same full-width `/ask` a phone gets.

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
| **AI 질문** (grounded 해설 agent) | R6 | nav slot 3 + footer bottom row → **`/ask`**, desktop bottom-right launcher (widget), detail preset strip, widget header's external-link | no |
| **운영 관제** (admin) | R7 | a separate path (e.g. `/ops`), **linked from nowhere in the reader chrome** | yes — separate operator credential |

- **Nav is two slots since P7: 관제 현황판 · AI 질문.** R2 signs three (내 종목 조회 · 관제 현황판 ·
  AI 질문) and 내 포트폴리오 is deliberately not a fourth link (operator revision at R5); **(P7)** an
  explicit operator override removed the 내 종목 조회 slot — that surface lives on the landing hero's
  own search, R3's detail link-out and the agent's link row, and is still reachable at `/stocks`. The
  override is scoped to the slot: nothing was re-centred, re-spaced or re-labelled. Right side:
  로그인 + the vocky `[의견]` trigger.
- **Global chrome (R2):** 52px nav (white wordmark — R2's asset was the ring, retired in P10), mobile top bar + sheet menu, footer with the
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
- **(P7) The reader sees 30 rows at a time and presses 펼치기 for the next 30** — reading the whole
  ranked list is a deliberate act, not the default. It is a **display window, never a filter**: the
  tab counts stay whole-board (전체 still reads 488), the ranked order is untouched, a tab switch
  resets the window, and the control disappears once nothing is left to disclose. The two pinned
  strips (전환청구 진행 중 · 일정 추후결정) are unchanged and their own 펼치기 still works.
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
- **(P7) While the reader types, the row offers up to eight candidates**, each carrying its 종목코드,
  and a chosen one opens that company by its exact handle. Nothing is pre-highlighted, an empty box
  asks nothing, and choosing is always the reader's act — see the split miss rule under *What the
  built surfaces refuse to state*.
- **Memory is session-only:** sessionStorage with a restore chip ("이전 입력 {n}주") — never
  auto-filled, never server-side. **(P7) The page no longer *says* so**: the 보유량 caption reads
  「서버 전송 없음」 and no longer names where the number is kept. The promise is unchanged and
  verbatim; only the mechanism clause is gone (`frontend`, `security`).
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
  **(P7) Measured on the running product in both modes**, because the operator reported it as inert
  (it was the un-hydrated origin, not the checkbox): the hue flips on **both** the label and the
  value, the figure and its 「추정」 are unchanged (679,575원), and the change is **shift-free** — the
  row's box and the document height are identical before and after the click. The account path is
  `PUT /portfolio/claims/{rcept_no}` followed by a re-read of `GET /portfolio`, so a claimed row
  survives a reload server-side; the 샘플/익명 path keeps the mark in `localStorage`. Whether a
  claimed row should *disappear* from 지나간 마감 is an open operator call — R5-8 signs a re-label,
  not a removal (`decisions`).
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
  `search_events` / `get_event` / `get_portfolio` / `save_feedback` / `get_contact` / **`calculate`**
  / **`security_check`** — **seven**, not five (the list was two short from P9 until P11 corrected it;
  `security_check` is never narrated and ends a turn with a fixed Korean sentence).
- ~~**The agent never calculates** (handoff §3.6); a calculation request is redirected to 내 종목 조회
  with a fixed sentence.~~ **Superseded by R16's auditable calculator (P9), corrected here at P11.**
  The agent *does* calculate, through one server-run tool whose inputs, 식 and result the reader sees
  in a 검증된 계산 block; what has not changed is that no number is invented — every input is a
  verified-contract value or the reader's own, and the result carries a 「계산」 marker.
- **A sentence without a citation cannot exist in the stream.** Citations are numbered evidence chips
  that arrive with their claims (no placeholder chips), tapping opens the verbatim quote — since P11
  in an **overlay popover** under the chip (under the row, block-wide, in a 데이터 행 / 계산 입력)
  rather than in a panel that pushes the flow.
- **The start screen offers six question cards, one per agent capability** (P11, superseding R16
  D11's 「4장」 by operator instruction — the count was freed, the layout was not). Pressing them one
  at a time demonstrates the whole product: `search_events` (「HLB 전환사채 공시가 몇 건이나 있나요?」)
  · `get_event` (「접수번호 20260730000215 공시에는 무슨 내용이 있나요?」 — a bare 접수번호 is the only
  shape that isolates the reading tool, and pasting a number is a real reader's move) · `calculate`
  (「에코프로비엠 유상증자, 1,000주 보유 시 배정 신주는 몇 주인가요?」 — the 1,000주 is the reader's own
  input and shows as 「입력」) · `get_portfolio` (샘플 포트폴리오, answered 「구성 예시」) ·
  `save_feedback` (a **first-person opinion**, so nothing is filed behind the reader's back — this is
  the one card with a side effect: it writes a real 운영자 검토 대기열 row) · `get_contact` (answered
  honestly 「연락처 미설정」 when `MIJUAL_OPERATOR_CONTACT` is unset — the product never invents one).
  `security_check` is deliberately not a card. The cards stay hard-coded Korean strings in
  `components/ask/copy.ts`, the card's sentence **is** the question sent, and the companies are chosen
  from the live corpus (three of R16's original four had gone dead as their filings aged — the aging
  of a hard-coded set is a known cost, carried in the copy rather than in an endpoint).
- **The agent's numerals read like the rest of the product** — 「예정발행가액은 **3,200원**입니다」,
  not `3200원`. The quote block under the chip still shows the filing's own spelling, whatever it is,
  because that text is 공시 원문 and is never reconstructed.

**As built and measured (P6).** Everything above shipped; what follows is what the build settled.

- ~~**The launcher is the product's one sanctioned motion exception, and it reads as a sphere**
  (22×22 Saturn, spinning band, two-half ring on one drift).~~ **Retired at R17 (P10).** The 68×50
  frame and its tail stay; the mark is now a **32×32 sparkle painted by CSS `mask` +
  `currentColor`** from the operator's own symbol export — one asset, every colour — and it carries
  **zero animations in every state**, measured with `getAnimations()` in rest, hover, active,
  focus-visible, open and reduced-motion alike. Hover keeps the 1.35× scale and now also changes
  **colour** (`#eaf2ed` → `--live`), the frame and the tail moving together; active is 1.15×; the
  keyboard gets its own `focus-visible` outline (`2px --focus-ring`, offset 2) plus the same colour,
  which R6 had deferred. **The colour change is deliberately kept under `prefers-reduced-motion`** —
  colour is not motion, and with the ambient animation gone it is the only hover response left.
- **"No ambient motion anywhere" is not what expired — R6's *launcher* exception is.** The product
  still moves where R2 signed it to: the cosmos backdrop (`drift` 80s, `twinkle`, `shoot`), the
  hero's 26s `orbit`, and the streaming caret. Under `prefers-reduced-motion` the whole document
  reports **zero** animations.
- **Opening the widget changes no page.** The landing's layout is byte-identical before and after —
  the widget is opaque, fixed, and has **no backdrop and no dim**. The launcher sits behind it, which
  is how 「런처는 열리면 숨음」 and the launcher's own open state are both honoured.
- **Four SSE states, all text — no spinner, no typing dots.** idle → 「답변 준비 중…」 (the button's
  text is replaced and it disables) → streaming (prose grows beside a blinking 7×15 caret, and the
  button becomes 「중지」) → complete (the footer fades in) → 중단/오류 (the partial answer **stays**,
  dimmed, under one inset row and 재시도). One sentence covers every way a turn can break — a reader's
  중지, a dropped stream, a typed error, a pre-stream refusal — because the record writes exactly one.
  **No alert colour appears anywhere in the agent surface.**
- **Streaming actually streams, and it took a header to prove it.** Verified in a real browser: first
  tool row at 5.5 s, second at 8.7 s, first sentence at 11.0 s, with 중지 pressable throughout.
  Before the fix the reader waited through the whole turn and then got everything at once, because
  the dev-server proxy was gzipping the event stream.
- **The conversation follows the reader.** Widget → page mid-answer keeps the same turn streaming on
  the page; back-navigation from the page returns to the event the reader came from with the
  conversation intact; the thread lives in one `sessionStorage` key and nothing else.
- **The question strip's chips are the disclosure's own words.** Each chip's text is the served
  Korean field name, in the page's own field order, and the chip's text *is* the question sent — no
  sentence template was invented (a generated 「{label}은 어떻게 되나요?」 would be invented copy and
  wrong Korean for most labels). The one exception is a question the record itself wrote. A **철회**
  event offers no presets, because there are no field rows and 철회 is the family the agent would
  answer with anyway.
- **Pressing a chip is the reader choosing a 범위**, so it overrides the page's ambient scope; the
  reader's own 범위 choice is never overridden by navigating. Clearing it returns to 전체 공시, and
  reopening keeps that choice.
- **The dedicated page is frameless, with the rail as its only panel** — chat directly on the page,
  a 340px right rail carrying the 범위 chip, the verification line, the agent intro and the
  session/storage line, and **no launcher rendered**. The **480/481 boundary is exact**: at 481 the
  widget and launcher exist, at 480 and below neither does and the page is the whole surface, with a
  sticky 44px input bar, 44px targets, the tool rows kept, and citation blocks full width under a
  180px cap.
- **The 의견 path is one row and one line.** Saving an opinion prints the tool's own row plus the
  signed confirmation — and *only* that. A feedback turn has no data to verify, so it must never end
  in a 검증 미통과 refusal contradicting the save it just made.

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
- **A search miss names no reason, candidate or near-miss** — and **(P7) that is now half the rule,
  because it is about the *miss*, not about typing.** The submit path is unchanged: it resolves
  unique-or-decline, **never picks between two companies**, and a miss states only R4's locked
  검색 불일치 sentence. What changed is that *while the reader types*, 내 종목 조회 offers candidates
  and a chosen one opens by the exact handle. The defect class the rule guards against is **the
  system** silently opening a different company's 놓친 돈; a reader choosing from a list is the
  opposite of that. A non-renderable event 404s **without
  explaining itself**; a 철회 page renders **0 field rows and no countdown**; the 발행사 기재 불일치
  block shows both readings, cites each, and **never reconciles them**.
- **A staleness notice never dims the rows** — the chip flips, an inset notice appears, and the
  content renders identically.
- **The bottom-right corner belongs to the launcher and nothing else.** P5 kept it clear; P6 filled
  it, and it is still the **only** `position: fixed` node on a reader surface (none at all on `/ask`
  or below 481px). **But the footer's action row reaches into that corner**, and until P10 the
  launcher sat on top of 「의견 보내기」 — a *dead interaction*, not a cosmetic overlap, because the
  feedback panel anchors on that button. R17 fixed it from both sides: the desktop footer's
  duplicated 「AI 질문」 link is hidden at ≥768 (the same destination is not said twice), and the
  footer reserves the corner between 768 and 1255. Measured with a five-point hit test and a real
  click at 768 / 1024 / 1120 / 1255 / 1256 / 1280 in dev and in a production build: the button
  answers at every point at every width and its 380px panel opens fully inside the viewport. At
  **≤767 the 「AI 질문」 link stays**, because the launcher does not render there and it is that
  destination's only footer entry. No element of the third-party feedback widget exists anywhere, so the signed
  no-corner-collision rule holds by construction. **Zero horizontal overflow** at 390px on every
  touched page — including one with a rendered answer and an open citation block — with every named
  tap target ≥44px.
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
- ~~**No 질문 스트립 on the event detail page**~~ — **landed in P6**, along with the real `/ask` page
  that replaced P5's shell. The phase boundary closed exactly where it was drawn.
- **The rail's *contents* are a build decision, flagged as such.** The record fixes the page's rail
  width and says the rail is the only panel; it writes nothing about what is inside it. The build put
  the four signed things this surface has (the 범위 chip with its clear ×, the verification line, the
  agent intro, the session/storage line) and nothing else, and the page's thread renders no second
  intro so nothing is said twice.
- **Two unsigned *slots* reuse the nearest signed words** rather than inventing any: the composer's
  idle button and the question field's accessible name. The phase rule held throughout — every other
  string is transcribed with its provenance, and the agent's own words (the tool rows, the five
  refusal sentences) are rendered **verbatim from the wire**, never restated on the client.
- **The mobile menu keeps AI 질문 in the third slot**, matching the nav it mirrors. The record
  contradicts itself here — one section states the position by ordinal, another mentions the menu's
  first row inside a list of touch-target constraints — and the constraint that section actually
  carries is met. Reordering signed chrome on the weaker reading would have made the sheet disagree
  with the nav; it is one line either way and the record's owner decides.

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
- **The 운영자 연락처 string** for `get_contact` stays operator-provided and never invented. P6 built
  the honest-unset behaviour; only the value is outstanding (**P4/deploy**).
- **「필드로 이동」, the answer footer's third context link, is signed but not rendered.** It needs a
  link kind the wire does not have, a per-field anchor the detail page does not have, and a rule the
  record does not write for which field an answer citing several should point at. Nothing was
  invented and nothing was relabelled — **draw it or strike it** is the operator's call, and it is
  tied to the next item.
- **The answer footer's link row is dense.** Up to seven links on three lines, with 「이벤트 상세」
  repeated, because the links come from what the turn *read* while the footer names what the answer
  *cited*. Capping it, restricting it to the 근거, or labelling per filing are all design choices.
- **Does a refusal get a footer?** It currently shows `근거 0건 · {시각}` + 다시 질문 beneath the
  signed three parts. The line is honest and the 갈 곳 links render once, not twice — but the record
  signs the footer under an answer and gives a refusal its own anatomy.
- ~~The agent prints raw contract numerals~~ — **closed by operator disposition** (2026-08-23):
  agent prose now reads `3,200원` like every other surface. The seam is the one the catalogue
  suggested — the tool contract hands the model the reader's spelling beside the exact value, and
  the citation gate respells a sentence *after* it has passed every check — so no number is ever
  transformed and every verbatim quote stays byte-exact.
- **The ops 대화 로그 and 익명 세션 tables print raw ISO instants** while a sibling table on the same
  tab prints a friendlier KST format — because that panel quotes its source by design (a P5 rule).
  The values are correct KST either way; which convention these columns follow is a decision.
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
