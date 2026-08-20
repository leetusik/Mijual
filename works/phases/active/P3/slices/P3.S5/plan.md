# Plan — P3.S5: Design round R4 — 종목 조회: 검색 + 보유량 환산 + 놓친 돈 (co-work)

## Shape

`co-work` slice, inline, two legs like S2–S4: **handoff leg** — write
`docs/reference/design/rounds/04-lookup/handoff.md`, commit, push (the slice's one push),
`set-slice-status P3.S5 pending`, STOP. **Read-back leg** — list_files → verify cards →
concreteness check → land under `rounds/04-lookup/output/` → phase.md append → signoff →
SIGNOFF append → pure regroup (`⏳ P3.S5 · Lookup`) → finish-slice → commit.

## Round scope (inventory items 5 + 6)

The 조회 surface the R2 hero submits to and R3's "내 보유량으로 환산 →" links to. It owns
ALL N주 math display (R3 decision: detail never shows what 조회 could contradict):

- 종목 검색 → per-stock result: live rights + retroactive missed rights for that stock.
- 보유량 input (the "500주 보유였다면 …" instant conversion) — anonymous, no login.
- 놓친 돈 조회기: 종목 + 보유량 (+ 기간) → retroactive lapsed value with per-offering
  breakdown, all 「추정」-tagged, zero-result state, "poke your own stock" hook.
- States: no-event stock, ① before 확정발행가 (no money number — 아직 확정 전),
  data-coverage boundary (corpus starts 2026 for ①; pre-2026 depth is deferred job D3 at
  the apply phase).
- Naming: this round names the surface (nav label "내 종목 연결" and R3's link-out label
  are provisional pending it).

## Notes

- Data facts to state in the handoff: `calc.py` provides allotted_shares /
  excess_subscription_cap / warrant_intrinsic_value(_floor) / lapsed_warrant_value; no
  price feed — everything disclosure-derived; ② has no per-holding money conversion
  (overhang = dilution watch), ③ has no 매수예정가 until the apply-phase backing lands —
  what ②/③ rows show per-holding is a design question posed back.
- Required cards under `⏳ P3.S5 · Lookup`: lookup/Lookup.html (per-stock result, live +
  missed), lookup/HoldingInput.html (quantity input primitive + conversion readout),
  lookup/MissedMoney.html (놓친 돈 breakdown), lookup/LookupEmpty.html (no-event +
  coverage-boundary states), lookup/LookupMobile.html.
- Open questions: one page with modes vs two pages; 기간 input shape; ②/③ per-holding
  presentation; surface naming (feeds nav label).
