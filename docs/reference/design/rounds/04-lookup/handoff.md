# Design Handoff — Round 4: 종목 조회 — 검색 + 보유량 환산 + 놓친 돈

- Round: **R4 of 7** · slice `P3.S5` · written 2026-08-21
- Status: OUT — awaiting the design session (Claude Design + operator)
- Repo: `leetusik/Mijual` via Connect GitHub (main, pushed at handoff commit)
- Builds on: **R1–R3 signed designs** (locked context — cosmos theme, craft panels,
  chrome, trust primitives, 「추정」 mark, detail-page contracts). Changing any of them is a
  new superseding round.

## 1. Product context

This is the surface the landing hero submits to (R2: the hero IS the 내 종목 연결 entry —
search field + 조회 button) and the surface R3's detail pages link out to ("내 보유량으로
환산 →"). It answers the judge-hook question from the confirmed 겉면 설계: *"이 종목,
500주 보유였다면 지금 얼마가 걸려 있고 언제까지 뭘 해야 하나 — 그리고 올해 얼마를
놓쳤나."* Anonymous, no login, instant. **This surface owns all N주 math display** (R3
decision: detail pages show per-unit values only, so nothing here may be contradicted
elsewhere — and vice versa).

Two jobs on one data spine:
1. **진행 중** — the stock's live rights (deadlines + per-holding conversion where the
   money chain exists).
2. **놓친 돈** — the stock's 2026 retroactive lapsed value for a given holding
   (the "poke your own stock" hook for judges).

## 2. Scope checklist — what this round must cover

- [ ] **Search → per-stock result page**: ticker/name resolution, the result composition
      for a stock with live events, past events, both, or neither.
- [ ] **보유량 input** — the holding-quantity primitive ("500주") and how the page reacts
      instantly (the classic pattern is a slider + direct input; what it actually is, is
      this session's call). No login, no persistence implied.
- [ ] **Per-holding conversion readout (①)** — the money chain composed per R3:
      배정비율 × N주 → 배정 신주 → (확정발행가 존재 시) 증서 이론가치 × 증서 수 =
      「추정」원 net of nothing invented; plus 초과청약 cap where present. Before 확정발행가:
      **no money number at all** — `발행가 확정 전` + dates is the whole answer.
- [ ] **놓친 돈 조회기** — 종목 + 보유량 (+ 기간, shape in play) → total 「추정」 missed
      value + **per-offering breakdown rows** (offering, dates, 소멸 증서 계산, per-holding
      「추정」 value each), zero-result state ("이 종목은 올해 놓친 권리가 없습니다" family —
      exact copy in play as chrome copy, logged for sign-off).
- [ ] **Deadline framing** — every live row carries its governing DDay (upstream KST);
      missed rows are history-styled (faint, D+), consistent with R2/R3's 지남 rules.
- [ ] **States**: stock with no events at all; ① live but pre-확정발행가; **data-coverage
      boundary** — the corpus starts at 2026 for ① (pre-2026 depth arrives later via a
      backfill), so a lookback must say what period it actually covers, factually, without
      apologizing.
- [ ] **②/③ per-holding presentation** — open question below; the data facts are in §4.
- [ ] **Surface naming** — this round names the surface (the nav label 내 종목 연결 and
      R3's "내 보유량으로 환산 →" are provisional pending it). Naming is chrome copy —
      logged for sign-off.
- [ ] Desktop + mobile compositions.

Cross-cutting: Korean-only; copy from `copy-inventory.md` (new strings logged as proposed
chrome copy); 「추정」 on every estimate, never on a fact; mobile-first; a11y floor;
urgency color-never-size.

## 3. Locked vs. in play

**Locked:** R1–R3 signed systems; the calculation semantics (§4 — deterministic
`mijual.calc`, no price feed, nothing computed in the browser except composing
upstream-provided numbers); 발행가 확정 전 = no money number; coverage boundary is factual;
data contracts; Korean-only surface.

**In play:** everything visual and compositional — the input primitive (slider or not),
result layout, one-page-with-modes vs separate 진행 중/놓친 돈 views, breakdown density,
기간 input shape, ②/③ presentation, empty/boundary state expression, surface naming, the
mobile pattern.

## 4. Where to look — real content, never lorem

- `docs/reference/design/grounding/samples/r1-money-chain.json` — 한화솔루션: the complete
  ① chain (확정발행가 22,100 → 증서가치 「추정」5,525원 → 배정비율 0.2465120994 → 소멸
  8.86% = 「추정」206.4억원, 하한 165.5억원). A 500주 holder of this stock is the worked
  example: 500 × 0.2465120994 = 123주 배정 → the per-holding numbers follow.
- `samples/r1-live-healthy.json` / `r1-tbd-schedule.json` — live ① pre-확정발행가
  (계양전기: dates real, money absent).
- `grounding/board-snapshot.md` — per-type counts and urgency; `headline-numbers.md` —
  the aggregate framing conventions.
- R3 landed record `rounds/03-event-detail/output/build-prompt.md` — the per-unit values
  detail shows; this surface must compose, not contradict, them.
- **Calculation facts (locked):** deterministic functions exist for 배정 신주
  (`allotted_shares`), 초과청약 한도, 증서 이론가치(+하한), 소멸가치. **No market price
  feed** — every won amount is disclosure-derived and 「추정」-tagged. **②**: overhang is
  dilution surveillance — there is no per-holding money conversion for a stockholder
  (nothing to exercise); what a ② row can offer is deadlines + dilution context. **③**:
  매수예정가 is not in the data contract yet (added at the apply phase per the R3 gate),
  so a ③ row today has deadlines + procedure, no money.
- **Coverage fact (locked):** ① corpus = 2026 YTD (backfilled ② reaches 2025-06);
  pre-2026 ① history is a deferred backfill (D3). The 놓친 돈 lookback must state its real
  coverage window.

Missing real content → ask; never invent.

## 5. Required outputs (a round is incomplete without all three)

1. **Card set** — line-1 `@dsCard` markers, review-time group `⏳ P3.S5 · Lookup`:

   - `lookup/Lookup.html` — per-stock result: live rights + missed money, desktop
   - `lookup/HoldingInput.html` — the holding-quantity primitive + instant conversion
     readout, its states (empty, typing, result, pre-확정발행가)
   - `lookup/MissedMoney.html` — 놓친 돈 total + per-offering breakdown
   - `lookup/LookupEmpty.html` — no-event stock + coverage-boundary states
   - `lookup/LookupMobile.html` — the result at 390px

   Split further freely; never a monolith.

2. **Record of what was designed** — refresh `handoff-output/result.md` (R1–R3 copies are
   landed in the repo); log every departure and all proposed copy.

3. **Implementation contract** — refresh `handoff-output/build-prompt.md`; state the token
   delta explicitly (none expected, but say so).

**Definition of done: the cards appear in the pane** under `⏳ P3.S5 · Lookup` and the
refreshed record + contract exist.

## 6. Open questions — posed to the session, not answered here

1. One result page with 진행 중 / 놓친 돈 as sections or modes — or two distinct views?
2. What is the 기간 input for 놓친 돈 — fixed "2026년" (matching real coverage), a range
   picker, or nothing until more history exists?
3. What do ② and ③ rows offer in a per-holding context, given ② has no exercisable money
   and ③ has no 매수예정가 yet — deadlines-only rows, dilution context for ②, or exclusion
   from this surface with a pointer to detail?
4. What is this surface's user-facing Korean name (feeds the nav label and R3's link-out
   label)?
5. Is the holding input remembered across stocks within a session (a UX decision — no
   account exists; nothing may be persisted server-side)?

## 7. Operator setup + definition of done

Same project; pull latest `main` in the session first (this handoff + R1–R3 landed
records). When the cards are up and the record/contract refreshed, tell the orchestrator
to resume. Approval must be literal.
