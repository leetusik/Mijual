# R3 Round Record — Event Detail: 3 Rights Types + Trust States (`P3.S4`, round `03-event-detail`)

Designed 2026-08-21 in the Claude Design project "Mijual Design System", against
`rounds/03-event-detail/handoff.md` + the grounding pack (11 pinned samples). Builds on the
signed R1+R2 systems (cosmos-dark R2.1 governs); no locked context was changed.

## What was designed

### Card set (`⏳ P3.S4 · Detail`)

- **detail/EventR1.html** — ① 계양전기 (20260724000546, D-5 live) full detail: header
  anatomy (RightsChip · corp name · DART ↗ · rcept_no · governing D-day + window), 환산
  블록 with 발행가-확정-전 state, field sections 일정/발행 조건 with per-field [근거],
  청약 취급처 4-row table, 정정 반영 strip, provenance
  footer. Below: the completed 환산 블록 on 한화솔루션 (확정발행가 22,100원 → 「추정」5,525원
  → 배정비율 → 소멸 3,734,925주 8.86% = 「추정」206.4억원, 하한 165.5억원).
- **detail/EventR2.html** — ② 대동기어 (D-65 upcoming): API-tier fact strip on top
  (전환가액 · 오버행 · 권면총액 · 발행방법/만기), 본문 fields below rendered as the filer's
  `detail` strings 1:1 — option_schedule as 풋/콜 blocks whose bracket dates appear only as
  a caption marked "연속 기간 아님" (ui-traps §1: never a window, never a bar). Below: the
  sparse-② composition — same anatomy with zero 본문 fields, closed by one factual line
  ("공시 본문에서 확인된 추가 조건이 없습니다"), no empty sections, no apology.
- **detail/EventR3.html** — ③ 세기상사 (D+45, history): the 2단계 절차 as structure
  (numbered steps, windows, dependency line "1단계를 놓치면 2단계 권리 자체가 소멸"),
  통지 방법/접수처 rows, 정정 strip. Past deadline = faint D+, "기한 지남" — never 종료-colored.
- **detail/EventStates.html** — the trust states in page context: 철회 (썸에이지 — notice
  replaces the body + one cited 정정사항 quote), 추후결정 (경남제약 — badge where the date
  would be, D-day slot replaced, healthy fields render on), 발행사 기재 불일치 (대한광통신 —
  both readings side by side, each with its own citation, total-uses-발행−청약 note),
  absence (아시아나항공 — the blocked row simply isn't there; header D-day slot carries a
  factual sentence about the filing, never the gate), corp_name mismatch (풍전약품 /
  에스씨엠생명과학 — see decision 3), and the 추후결정 board strip (decision 4).
- **detail/CorrectionStory.html** — the 정정 narrative: 세기상사 version rail (4 versions,
  current-readable marked live, superseded row annotated with the locked reason string),
  old→new field moves from `field_moves` verbatim, `interpretation.summary` verbatim; then
  the two extremes of "D-day moved": 아시아나 (correction deleted the passage — absence
  with a history) and 썸에이지 (correction withdrew the decision itself).
- **detail/EventMobile.html** — ① 계양전기 at 390px: header stack → countdown box → DART
  link (44px) → 환산 블록 → all fields exposed (no accordion — the trust surface doesn't
  fold), [근거] right-aligned on the label row.

### EstimateMarker re-cut (system-wide 「추정」)

`components/EstimateMarker.{jsx,html,prompt.md}` re-cut to the bordered 「추정」 tag
(value first, trailing tag at 0.56em of context, border from currentColor at 42%).
▷ is retired from the UI everywhere; it survives only in docs/pipeline. `.d.ts` unchanged
(`value`, `color` — same API).

## Session decisions (§6, delegated by operator to the session)

1. **환산 블록: 절충.** Detail carries per-unit upstream values only (확정/예정발행가,
   할인율, 배정비율 at full 10-decimal precision, 「추정」증서 1주 이론가치 where 확정발행가
   exists) plus a "내 보유량으로 환산 →" link-out. N주 input/slider stays in 조회 (R4) —
   detail shows nothing R4's math could later contradict.
2. **② 캘린더: 중간 깊이.** Governing API facts pinned at top; 본문 조건 render the filer's
   `detail` strings 1:1 with bracket dates as annotated captions. No derived table, no
   기간 bars, no 더보기 hiding — three fields don't need folding.
3. **표시명: master `corp_name` 단독.** When `corp_name_agrees_with_body` is false (suffix
   differences excluded upstream), one quiet annotation line under the header: "공시 본문
   표기: … — 원문에는 이 이름으로 기재되어 있습니다", so the tap to 원문 survives. Numbers
   are unaffected and render normally.
4. **추후결정 4건: 관제 현황판 하단 접힌 strip** — same pattern as the ② 진행 중 strip
   ("일정 추후결정 — 카운트다운 없이 감시 중인 이벤트 4건 · 펼치기"); not ranked, rows
   link to their detail pages.

## Departures / notes

- **매수예정가 (③) is not rendered**: it does not exist in the `EventExposure`/`FieldView`
  contract or any pinned sample. Not in the contract → not drawn; posed back (add to the
  contract or drop from future scope).
- **Sparse-② composition uses 대동기어's real API facts as a structural stand-in** (labeled
  as such on the card): the corpus's typical sparse-but-exposable ② isn't among the pinned
  samples (r2-incomplete-api is non-exposable). No values were invented — same event, 본문
  fields omitted to show the layout rule.
- The absent-field detail (아시아나) shows a factual D-day-slot line "현재 버전 공시에 없음"
  — a statement about the filing, not the gate. If this reads as over-explaining, the
  fallback is an empty slot; flagged for the gate.
- 정정 반영 strip copy ("정정공시 반영 — 최근: …") composes locked `interpretation.summary` /
  `schedule_impact` values with minimal connective framing; the connective words are new
  chrome copy for sign-off.

## Token delta

**None.** R3 introduces no new tokens and no `.cosmos` changes; all cards compose existing
R1/R2 tokens (`--panel-bracket`, `--panel-glow`, urgency scale, rights hues, surfaces).

## Open items posed back

- 매수예정가: contract addition or scope drop (above).
- "정정 이력" as the button label for the CorrectionStory view — naming for sign-off.
- The 환산 link-out label "내 보유량으로 환산 →" is provisional until R4 names the 조회 surface.
