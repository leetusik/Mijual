# R4 Round Record — 종목 조회: 검색 + 보유량 환산 + 놓친 돈 (`P3.S5`, round `04-lookup`)

Designed 2026-08-21 in the Claude Design project "Mijual Design System", against
`rounds/04-lookup/handoff.md` + grounding (r1-money-chain, r1-live-healthy, board-snapshot,
copy-inventory) and the R3 landed contract. Builds on signed R1–R3; no locked context changed.

## What was designed

### Card set (`⏳ P3.S5 · Lookup`)

- **lookup/Lookup.html** — the full desktop result on 계양전기 (live ①, pre-확정발행가):
  search row (hero copy reused) → 보유량 strip (direct input + 100·500·1,000주 preset chips,
  instant recompute) → 진행 중인 권리 section (governing D-5, per-holding chain 보유 →
  배정비율 → 배정 신주 115주 → 초과청약 한도 +23주, `발행가 확정 전` chip — **no money
  number**, 확정 예정 2026-09-01) → 2026년 놓친 돈 section in its honest zero state
  (집계는 청약 종료 2026-09-04 후) → provenance.
- **lookup/HoldingInput.html** — the input primitive and its states: empty; live interactive
  demo on 한화솔루션 (type any N → 배정 신주 = ⌊N × 0.2465120994⌋ → 「추정」증서가치 환산,
  500주 → 123주 → 「추정」679,575원, 하한 「추정」545,181원); pre-확정발행가 (계양전기 —
  주수만); session-restore chip ("이전 입력 500주").
- **lookup/MissedMoney.html** — 놓친 돈 조회기 on 한화솔루션 500주: total 「추정」679,575원
  (하한 545,181원) under the conditional frame "청약도 매도도 하지 않았다면"; per-offering
  breakdown row (offering + rcept_no, 매매기간 07-06~07-10 faint `기간 지남 · D+41`, 소멸
  계산 발행−청약 = 3,734,925주 8.86% · 「추정」206.4억원, 500주 기준 「추정」679,575원) with
  [근거] citation; the calc line (배정 = ⌊500 × 배정비율⌋, 이론가치 산식); zero-state strip.
- **lookup/LookupEmpty.html** — 검색 불일치; 권리 없는 종목 (감시 대상 3종 + 감시 중 488건
  context); 집계 범위 경계 stated factually (① 2026-01-01부터 · ② 2025-06부터 · "2026년
  이전의 유상증자 기록은 집계에 없습니다") — no apology, no zero-counting outside coverage.
- **lookup/LookupMobile.html** — 한화솔루션 @390px: top bar → search → 보유량 (44px
  targets, full-width chips) → 진행 중 0건 (factual line: 청약 2026-07-23 종료) → 놓친 돈
  total + stacked breakdown → coverage + provenance.

Desktop card (계양전기: live + zero-missed) and mobile card (한화솔루션: no-live + missed)
deliberately show the two complementary result compositions.

## Session decisions (§6 — operator delegated all five to the session)

1. **One page, two sections** (진행 중 on top, 놓친 돈 below) — no mode toggle, no second view.
2. **보유량 input = direct number input + preset chips** (100·500·1,000주), mono,
   right-aligned, instant recompute. No slider — holdings are exact integers.
3. **기간 input: none.** A fixed factual coverage line ("집계 범위 2026-01-01 ~ 오늘 (KST)")
   states what the lookback actually covers; a picker with one valid value is a trap.
4. **②/③ rows included as deadline rows with context** — ② carries dilution context
   (오버행 %, 전환청구 개시), ③ carries procedure + 통지 마감; neither carries money
   (② has nothing exercisable; ③'s 매수예정가 is not in the contract). Clearly separated
   from ① money rows. (No pinned per-stock ②/③ sample exists — the rule is stated in the
   contract; the cards show ① compositions only. Flagged below.)
5. **Surface name: 내 종목 조회.** Nav label 내 종목 연결 → 내 종목 조회; R3's link-out
   label "내 보유량으로 환산 →" stays valid as-is.
6. **Session memory: remember within the browser session only** — quiet restore chip
   "이전 입력 500주", caption "브라우저 세션에만 저장 · 서버 전송 없음". Nothing server-side.

## Proposed chrome copy (new strings, for sign-off)

- 내 종목 조회 (surface name / nav label)
- 보유 주식 수 (input label) · 브라우저 세션에만 저장 · 서버 전송 없음
- Section headers: 진행 중인 권리 / 2026년 놓친 돈
- 확정 후 증서 이론가치와 금액을 환산합니다 (발행가 확정 전 companion line)
- 청약도 매도도 하지 않았다면 (conditional frame — derived from locked terminology
  "행사도 매도도 되지 않고 사라진")
- 이 종목은 2026년 집계 범위에서 놓친 권리가 없습니다 (zero state, handoff family)
- 진행 중인 건의 소멸 여부는 청약 종료({date}) 후 집계됩니다
- ‘{query}’와 일치하는 종목이 없습니다 — 종목명 또는 종목코드로 다시 검색해 주세요
- 이 종목에는 진행 중이거나 2026년에 소멸된 권리가 없습니다
- 놓친 돈은 집계 범위 안에서만 계산됩니다 · 2026년 이전의 유상증자 기록은 집계에 없습니다
- 실제 손익은 개별 청약·매도 행동에 따라 다릅니다 — 이 값은 소멸된 증서의 이론가치를
  보유량 기준으로 환산한 것입니다 (disclaimer footnote)

## Departures / notes

- **Worked example math** (composition of upstream values only): 한화솔루션 500주 ×
  0.2465120994 = 123주 (1주 미만 버림) → 123 × 「추정」5,525원 = 「추정」679,575원, 하한
  123 × 4,432.367726… = 「추정」545,181원, 초과청약 한도 ⌊123 × 0.2⌋ = +24주. 계양전기
  500 × 0.2314082845 = 115주, +23주. **Floor rounding is a display assumption** —
  `mijual.calc.allotted_shares` governs; if it rounds differently the display follows it.
- **Per-holding 놓친 돈 semantics**: the number is the full 배정 증서 value under the
  do-nothing condition ("청약도 매도도 하지 않았다면"), not a claim the user lost it —
  hence the conditional frame + disclaimer footnote. Flagged for the gate.
- **No-event stock name "삼성전자" is a structural stand-in** (labeled on the card) —
  no pinned sample exists for a no-event corp; no corpus claim is made.
- **②/③ per-stock rows are specified but not drawn**: no pinned sample gives one stock's
  ②/③ in a lookup context. The contract states the row rule; drawing them needs a real
  sample (posed back — pin one if wanted as a card).
- 진행 중 카운트: the desktop card's "1건" and mobile's "0건" are per-stock facts from the
  pinned samples, not board counts.

## Token delta

**None.** All five cards compose existing R1/R2 tokens; no `.cosmos` changes.

## Open items posed back

- Pin a per-stock ②/③ lookup sample if those rows should exist as drawn cards.
- 배정 신주 rounding rule confirmation (floor assumed).
- The disclaimer footnote wording (compliance-adjacent — worth the operator's read).
