# Design Handoff — Round 10: Polish — Event Detail ①②③ + Trust States

- Round: **R10** (P8 polish pass, surface 3 of 8) · slice `P8.S6` · written 2026-08-23
- Status: OUT — awaiting the design session (Claude Design + operator)
- Repo: `leetusik/Mijual` via Connect GitHub (main branch, pushed at handoff commit)
- Builds on: **R3 (event detail ①②③ + trust states + CorrectionStory), R4 §환산 link-out, R5-2
  (「내 포트폴리오에 담기 →」 under the D-day), R6 (질문 스트립 — surface 7's, placement only here),
  R8 (chrome), R9 (landing — the board rows that link here)** as signed, plus the P7 operator
  overrides in `docs/reference/design/SIGNOFF.md`. Those rounds are **locked context** except
  where this handoff explicitly opens them; R10 is a **polish round — no new features** — and, per
  `SIGNOFF.md` precedence, what R10 signs supersedes the parts of R3 it touches.

## 1. Product context

`/events/{rcept_no}` is the page a board row opens: crumb 「← 관제 현황판」, the craft header panel
(RightsChip · corp name · 「DART 원문 ↗」 · mono meta 접수번호 · 최초 공시 · 정정 반영 | governing label
· DDay · window line · 「내 포트폴리오에 담기 →」), the 질문 스트립 (5 field chips + 「직접 질문 입력 →」),
then per type: ① the 환산 블록 (발행가/할인율/이론가치/배정비율 chain + 「내 보유량으로 환산 →」, post-결과
청약 결과 inset), ② the API fact strip (전환가액 · 오버행 · 전환 시 주식수 · 권면총액 · 발행방법 · 만기 +
rcept link) and 콜·풋 option cards, ③ the 2단계 절차 (1단계 반대의사 통지 / 2단계 매수청구 행사 + 「기한
지남」 chips); then `// 일정` `// 발행 조건` field sections (220px label · value · `[근거]` citation
that opens the verbatim quote + rcept link), the 정정공시 반영 band + 「정정 이력」 → version rail +
정정 전/후 diff, and the mono provenance line. State pages: 철회 (notice card + 정정사항 line +
[근거]), 추후결정 (StateBadge in the countdown slot + 「카운트다운 없음 — 일정이 공시상 미정」), field
absent (③ 아시아나: 「현재 버전 공시에 없음」). Non-exposable events (flagged / incomplete / 실적보고서
rcepts) are a **404 by contract** — today the framework's default page.

The orchestrator walked the surface on 2026-08-23 in the operator's runtime (127.0.0.1:3000, Chrome
desktop 1456px + 390px; pages: ① 계양전기 `20260724000546` · 한화솔루션 `20260720000067` · 경남제약
`20260623000409` 추후결정 · 썸에이지 `20260805000454` 철회 · ② 대동기어 `20251016000315` · 풍전약품
`20250930000508` · ③ 세기상사 `20260713000345` (+ superseded `20260623000277`) · 아시아나항공
`20260713000482`; sparse ② 라온텍 `20250818000222`). Findings are recorded in
`works/phases/active/P8/phase.md` §"R10 walk — surface 3". The operator's gate answers are
**direction** (what to fix) and **REFERENCE — data, not a proposal** for how. Claude Design + the
operator decide how it looks.

## 2. Scope checklist — what this round must cover

Default from the P8 rhythm (as at R9): **every walk finding → fix, Claude Design decides how**,
except where §2b names an operator decision. Walk findings (desktop + 390):

- [ ] **1 · 환산 블록 at 390px is broken** — the chain cells stack but the `→` connectors stay: an
      arrow floats after 「발행가 확정 전」, another hangs at the left edge before 「배정비율」, and on
      한화솔루션 「→ 증서 1주 이론가치 5,525원 추정 → 배정비율 0.2465120994」 crams onto one line. Design
      the chain for one column (how a per-unit chain reads vertically; whether arrows survive).
- [ ] **2 · `[근거]` and the rcept mono links are 32×15 / 92×17 on mobile** — R3 §Mobile says hit
      targets ≥44px and P7 Q6 #10 carried it; today every citation affordance misses the floor.
      Also decide the `[근거]` affordance itself: mono bracketed link vs a chip/button, and how the
      opened quote panel closes (today: click again; no visible state on the trigger).
- [ ] **3 · 「정정 이력」 reads no state** — the same closed-label problem R9 fixed on the board
      strips: the button keeps its label while the rail + diff are open below; no 접기 / open state.
- [ ] **4 · The diff table at 390** — 정정 전 / 정정 후 as two squeezed columns; mono dates split
      (「2026-07- / 06」). Unbreakable dates; a one-column or stacked before/after reading.
- [ ] **5 · Header meta line at 390** — 「접수번호 … · 최초 공시 … / · 정정 반영」 wraps with a dangling
      「·」 on its own line. Wrap rule for the three meta items.
- [ ] **6 · Window state on the ① header** — 계양전기 shows 「2026-08-19 ~ 2026-08-25 거래 가능 · 마감
      D-2」 (live) but a closed ① window (한화솔루션 D+44) shows only the bare dates — no state word
      — while ③ rows carry 「기한 지남」 chips. One rule for "this window is closed" across the header
      and the rows.
- [ ] **7 · 환산 블록 chain cells** — on desktop the `→` between 발행가 · 할인율 · (이론가치) · 배정비율
      reads as a flow but is a separator; 할인율 has `[근거]`, 배정비율 has none. Decide the chain's
      visual grammar and which cells cite.
- [ ] **8 · ② fact strip cites as a whole** — six API values with one rcept ↗ under the strip, no
      per-value `[근거]` (API-tier facts, not 본문 quotes — R3). Make the provenance difference
      legible: the strip is DART API data, the rows below are 본문 quotes. Also 「보호예수 / 전매제한
      해제일」 shows a date **and** a sentence stacked — decide the two-part value's reading.
- [ ] **9 · 철회 page** — notice card, then one line 「정정사항  유상증자 결정  유상증자 결정 → 유상증자
      철회」 + a lone `[근거]`: label, old value, arrow, new value on one line read as a run-on. Set the
      정정사항 evidence line.
- [ ] **10 · Field-absent ③ (아시아나)** — countdown slot 「반대의사 통지 마감 / 현재 버전 공시에 없음」
      as plain text, no badge, the page is one field + the 정정 band. Make the absence read as a
      state (the R3 literal is locked — its presentation is in play).
- [ ] **11 · Two destination links, two affordances** — 「내 포트폴리오에 담기 →」 (text link, header,
      R5-2; → `/portfolio?add=…`) vs 「내 보유량으로 환산 →」 (outlined button under the chain, R3/R4;
      → `/stocks/{corp}`). Confirm or re-rank the hierarchy (which is primary on ①) — both stay.
- [ ] **12 · Section eyebrows `// 일정` `// 발행 조건` are not headings** — the page has no h2/h3
      landmarks below the h1 (screen-reader outline; same as the board before R9). Heading semantics
      without changing the mono eyebrow look.
- [ ] **13 · 질문 스트립 placement/hit height** on this page (36px chips at desktop, 44px at 390?) —
      **placement and alignment only**; the strip's own design is **surface 7 / R14**. Note, don't
      redesign.
- [ ] **14 · 390 ordering in the header** — countdown → 「내 포트폴리오에 담기 →」 → 「DART 원문 ↗」
      (44px full-width) → 질문 스트립 → 환산; confirm the R3 mobile stack with R5-2's line inserted.
- [ ] **Cards refreshed for everything above, desktop (1512/1280) and 390px mobile.**

### 2b. Operator decisions (take at the gate or in the session — each is R3-deliberate today)

- **Q-A · The 404 page.** Non-exposable rcepts render Next.js' default 「404 / This page could not
  be found.」 (English, faded nav, empty account frame) because R3 wrote *state* copy and no 404
  copy (`frontend/app/events/[rcept_no]/page.tsx` comment). Options: (a) keep the framework page
  (status quo), (b) design a Mijual not-found surface — Korean, chrome-wearing, **no reason why**
  (the reason is internal, D-14). The orchestrator's default: **(b), in this round** — it is the
  only English screen a reader can reach. Also covers any mistyped `/events/…` URL.
- **Q-B · 배정비율 printed to 10 decimals** (`0.2314082845`) — R3 decision §6-1 "printed to its
  full 10 decimals". Keep (fact, not rounded) or present (e.g. mono, smaller, with the whole value
  reachable). Default: **keep the full value; presentation in play**.
- **Q-C · Superseded-version URL** (`/events/20260623000277` → renders the current version, rail
  marks 07-13 「현재 읽는 버전」, URL unchanged). Keep silent (status quo) or say 「이전 버전 접수번호로
  열었습니다 — 현재 버전을 표시합니다」-style. Default: **leave; log as decided**.
- **Q-D · 「현재 버전 공시에 없음」 / 「카운트다운 없음 — 일정이 공시상 미정」** literals stay (locked R3
  copy); only their presentation (finding 10) is in play. Confirm.

**Explicitly NOT in this round:** the 질문 스트립's design and copy (surface 7); `/stocks` (R11);
the DeadlineOffer's anonymous state (auth, R12); any new field, value, or data (e.g. 매수예정가 is
already shipped, nothing else is added); any change to what the contract exposes (404 stays a 404).

Cross-cutting (every round): Korean-only surface; mobile-first; a11y/reduced-motion floor; no new
features.

## 3. Locked vs. in play

**Locked:** R1 tokens/type/spacing/motion/square-hairline system and the `.cosmos` scope; R3 page
anatomy (crumb · craft header · 환산 블록/fact strip/2단계 절차 · field sections with per-field
citation · 정정 strip + CorrectionStory · provenance line) and every R3 hard rule (no estimate without
「추정」, no date beside 추후결정, no placeholder for a gated field, verbatim quotes, upstream KST
D-days, never 종료 on a past ② date, no page explaining why an event is not exposed); R3/R6 product
copy incl. the literals in §2b-D; R5-2's 담기 line existence; R8 chrome; the 질문 스트립.

**In play:** everything in §2 — the 환산 chain's grammar (desktop + one-column), citation
affordance + open/close states + hit sizes, 정정 이력 states, the diff table at 390, header meta
wraps and the closed-window rule, ② provenance legibility, 철회 evidence line, absent-state
presentation, link hierarchy, heading semantics, the 390 stack order, and the 404 surface if Q-A
says so (**Korean copy in play only there — the dated exception of this round, 2026-08-23** — and
for any state word finding 6 needs, e.g. 「지남」). A token change, if any, is a **new
`foundations/tokens.css` from the session** — the repo's copy is re-vendored, never hand-edited.

## 4. Where to look — real paths, real data shapes

- **Page as built:** `frontend/app/events/[rcept_no]/page.tsx` (request-time fetch, `notFound()`
  on the API 404), `frontend/components/event/` — `EventDetail.tsx` (composition; sparse-② closing
  line), `Header.tsx` (craft panel, DDay, window line, `DeadlineOffer`), `Offering.tsx` (① chain +
  청약 결과 inset, `stockPath`), `Convertible.tsx` (② fact strip + option cards), `Fields.tsx` +
  `fieldOrder.ts` (sections, rows, `Citation`), `Withdrawn.tsx`, `Corrections.tsx` (band, version
  rail, diff), `copy.ts` (every string with its citation), `Event.module.css`; shared `Citation`,
  `DDay`, `StateBadge`, `RightsChip`, `EstimateMarker`, `CraftPanel` in `frontend/components/`;
  `frontend/components/auth/DeadlineOffer.tsx` (담기 line); `frontend/components/ask/QuestionStrip.tsx`
  (surface 7). No `app/not-found.tsx` exists.
- **Backend shapes:** `GET /events/{rcept_no}` — `frontend/lib/types.ts` `EventDetail` (countdown
  {label_ko, date, dday, days, window, window_state, reference}, fields {display, estimated,
  korean_name, value, quote, span, rcept_no}, corrections/versions, convertible, offering).
- **Landed records:** `docs/reference/design/rounds/03-event-detail/output/` (R3 anatomy, type
  rules, state pages, CorrectionStory, mobile), `rounds/04-lookup/output/` (환산 link-out),
  `rounds/05-account/output/` (R5-2 담기 line), `rounds/06-explain/output/` (질문 스트립),
  `rounds/08-foundations-chrome/output/`, `rounds/09-landing-board/output/` (the strip-toggle
  state pattern, DDay tiers). Overrides: `docs/reference/design/SIGNOFF.md`.
- **Walk findings + operator answers:** `works/phases/active/P8/phase.md` §"R10 walk — surface 3"
  and §"R10 interview — operator answers".
- **Samples:** `docs/reference/design/grounding/sample-events.md` (the rcept_nos above, incl. the
  404-by-contract trio: 한솔테크닉스 flagged `20260709000212`, 파이온엑스 incomplete `20260722000285`,
  대한광통신 실적보고서 `20260306000600`).

Missing real content → ask for it; do not invent it.

## 5. Required outputs (a round is incomplete without all three)

1. **The card set** — line-1 `@dsCard` markers, review-time groups **`⏳ P8.S6 · Detail`** and
   **`⏳ P8.S6 · Components`**, one card per reviewable unit. Required card paths:
   - `detail/Header.html` — craft header ①②③: open window (live), closed window (state word),
     추후결정, absent; meta-line wrap at 390; 담기 + DART order at 390
   - `detail/Offering.html` — the ① 환산 chain desktop + one-column 390, 발행가 확정 전 variant,
     청약 결과 inset, citation placement, the two link-outs' hierarchy
   - `detail/Convertible.html` — ② fact strip provenance + 콜·풋 cards + two-part values, sparse ②
   - `detail/Procedure.html` — ③ 2단계 절차 incl. past steps, 아시아나 absent state
   - `detail/Fields.html` — field rows with the citation affordance (idle / hover / focus / open
     quote panel), heading semantics, 390 stack
   - `detail/Corrections.html` — 정정 band + 「정정 이력」 closed/open states, version rail, diff at
     desktop and 390
   - `detail/States.html` — 철회 page with the evidence line; 404 surface if Q-A = (b)
   - `components/Citation.html` — the `[근거]` affordance re-cut (if it changes) at ≥44px mobile
   - `foundations/tokens.css` — **only if tokens change**

2. **A record of what was designed** — `result.md` (what changed vs R3, every departure, the Q-A–D
   decisions as taken, any copy string added with its citation).

3. **An implementation contract** — `build-prompt.md` (geometry, states, copy table, mobile rules,
   the 404 surface if any). If the session produces Claude Design's own handoff bundle, that **is**
   the record and the contract — land as-is.

**Definition of done: the cards appear in the Design System pane** under the `⏳ P8.S6 · …`
groups, and the record + contract exist.

## 6. Open questions — posed to the session, not answered here

1. How a per-unit chain reads in one column (arrows or no arrows; what 「확정 전」 looks like).
2. The citation affordance: keep the mono `[근거]` word, or a chip — and its open state.
3. The closed-window state word on the ① header (and whether ② past-opening stays wordless —
   never 종료).
4. Whether ② API facts need a per-value provenance mark or one strip-level statement.
5. The 404 surface (Q-A) — if designed: what a reader is told, and not told.

## 7. Operator setup + definition of done

Same project ("Mijual Design System"), Connect GitHub already in place — pull latest `main` in
the session so it sees this handoff, the walk findings and the landed R1–R9 records. When the
cards are up and the record + contract exist, tell the orchestrator to resume; read-back, landing,
SIGNOFF, and the regroup (retiring the `⏳ P8.S6 ·` address) follow. Approval must be literal.
Then `P8.S7` applies R10 from the landed `build-prompt.md`.
