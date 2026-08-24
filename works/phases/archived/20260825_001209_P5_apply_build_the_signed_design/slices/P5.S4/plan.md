# Plan — P5.S4: 내 종목 조회 endpoints

## Context

Read `works/phases/active/P5/phase.md` first — S1/S2/S3 findings are binding, and S3's
"What P5.S4/S9/S10+ inherit" table names your tools (`mijual.web.reads`,
`mijual.present.*`, the persisted `offering_input` table and `performance_report.lapse`
column, `mijual.db.repository`). Design contract: `docs/current/frontend.md` →
`SIGNOFF.md` → R4 `build-prompt.md` (`rounds/04-lookup/output/`), with R2/R3 for shared
board-row/DDay conventions and `grounding/` for rules and copy. The surface is
anonymous — no login, and **a holding count never reaches the server** (R4 hard rule):
these endpoints return **factors, not products**; the client composes the N주 math.

## Deliverables — routers under `mijual.web.routers` (route shapes your call; record them)

1. **Stock resolution** — one query endpoint taking 종목명 or 종목코드; resolution is
   server-side against `Corp` (`corp_name`, `stock_code`). Exact 종목코드 match and
   name match (decide and record matching semantics — at minimum exact name and code;
   prefix/contains matching is your call, but never fuzzy-guess a different company).
   No match → a result the client can render the locked no-match copy from (the Korean
   string is R4's and lives client-side; the payload signals not-found structurally).
   Only corps that actually have events in the corpus are resolvable (the corpus is
   the universe — record how you handle a known 종목코드 with no events: R4 has a
   distinct "no-event stock" empty state, so distinguish *unknown stock* from *stock
   with no rights*; the no-event payload carries what that empty state needs — 감시 중
   count is already in `/board/summary`, don't duplicate derivations).
2. **A stock's live rights (진행 중인 권리)** — the corp's renderable events, most
   urgent first (upcoming D-day ascending; ② 진행 중 belongs here too — decide ordering
   between open-window and upcoming, record it): per row what R4 names — RightsChip
   type, title/corp, `rcept_no`, governing label + upstream DDay + window state. Reuse
   `present.board_row`/`EventView`; do not invent a new row shape if the existing one
   serves.
3. **2026 놓친 돈 breakdown for the stock** — from the **persisted** mappings only
   (`OfferingInput.inputs`, `PerformanceReport.lapse` → `present.offering_inputs` /
   `present.lapse_result`); the fixed coverage boundary (① from 2026-01-01, ② strip
   context from 2025-06; "outside coverage is unstated, never counted as 0" — no
   figure, no zero, for anything outside). Per-offering row payload: offering identity
   + `rcept_no` + 확정발행가, 매매기간 (+ the past-window D+n comes from upstream —
   serve what's needed), 발행 − 청약 = 소멸 shares + rate, market-wide per-offering
   소멸가치 + 하한 (estimates, tagged by the contract), and the **per-holding factors**:
   배정비율 (full 10 decimals, string), unit_value, unit_value_floor, 초과청약 ratio
   where passed, `final_price_date` when 확정발행가 is null. Total headline + band =
   Σ over this stock's in-coverage offerings — derive once server-side as the stock's
   totals (market-wide, still no holdings), let the client scale per-holding from the
   factors. Citation policy: the 매매기간 quote (single-span 본문 field) attaches per
   row; **S3's interim `_cited_count` guard governs summed 실적보고서 figures — do not
   re-attach one-addend quotes** (D4's proper fix is `P5.S20`, ordered later).
   Pending-① note input: `subscription_end` for the "청약 종료 후 집계" line when a
   live ① exists and 놓친 돈 is zero/absent.

## Constraints

- All numbers through `mijual.present`; nothing re-derived in a router; `payload()`
  everywhere; absent-key-not-null; English snake_case keys; exact-decimal strings.
- SQL-filter on persisted columns; batch like `load_board` does (no per-row
  `event_exposure` loading loops); no spending-module import (AST scan + the
  import-graph facts in S3 note 1).
- No new Korean strings server-side (R4's copy is the client's; if a string must be
  served, it must already exist in the product).
- 404-not-explained holds: an unresolvable stock is structurally not-found, never a
  reason-code leak.
- Tests: extend the DB-free pattern of `tests/test_web_board.py` (in-memory SQLite +
  `get_session` override), terse — resolution hit/miss, a live-rights ordering case,
  a breakdown case with 확정발행가 null (no money keys at all), a no-event stock.
  Baseline 83 ≈ 1 s.

## Validation

- `.venv/bin/python -m pytest` — full suite green.
- Out-of-suite curl pass against live Postgres (:5433): resolve 계양전기 by name and
  by 종목코드; its live rights; a 놓친 돈 breakdown for a stock with lapsed offerings
  (한화솔루션 or 에스에너지 — check totals against `grounding/headline-numbers.md`
  shapes, drift in values OK); a no-match query; a no-event stock. Stop the server.
- `python3 scripts/workflow.py validate`.

## Wrap-up

`result.md`; phase.md *Findings & Notes* (route map for S10/S14 + recorded decisions)
and *Doc impact* (`api`, `backend`; `data` only if you persist anything new — you
shouldn't need to). Structured verdict. No commits, no status transitions.
