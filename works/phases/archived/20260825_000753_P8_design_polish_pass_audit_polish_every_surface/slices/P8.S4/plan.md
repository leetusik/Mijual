# Plan — P8.S4: R9 design polish — surface 2: landing 관제 현황판 + board

Orchestrator plan, written inline (auto mode) on 2026-08-23. Kind `co-work`, risk `high`. **Run inline by the orchestrator on the main thread — never dispatched.** No implementation code in this slice.

## Surface (from `phase.md` § Surface 2)

Route `/` — `frontend/app/page.tsx`; `frontend/components/landing/` (`Hero`, `Cosmos`, `Anchor`, `Countdown`, `EstimateValue`, `Board`, `BoardRow`, `LapseNotice`, `copy.ts`); the hero's search row is the shared `components/lookup/SearchRow.tsx` (also surface 4). Designed by R2/R2.1 + R3's board strip; overrides in force: P7 30-row display window (`WINDOW_STEP = 30`, 펼치기), P7 typeahead on the hero row, P7 ring clip on `.orbits`; **R8 (just applied)** removed the "샘플로 열어보기 →" link + empty band and re-cut the chrome around it.

## Steps

1. **Walk first** — operator runtime (`## Operator Runtime`: dev stack up, `http://127.0.0.1:3000` in Chrome desktop + tailnet, 390px mobile; production build if behaviour could differ). Polish inventory item 2: hero H1 + subtitle + console search (type-and-wait: debounce, ↑/↓, Enter-on-highlight vs plain submit, Esc/blur, no request on mount) + the mono stat line; starfield/orbit rings + reduced-motion; both anchor cards (retrospective value card, countdown/stats card) — **watch the countdown tick for a real interval**; 소멸주의보 strip; freshness 기준시각 chip + stale notice; the four board tabs with whole-board counts, row anatomy (RightsChip / corp / ↗ / key date / StateBadge / DDay), the 30-row window + 펼치기 and its reset on tab switch, the ② 진행 중 strip + 추후결정 strip toggles; row click → event detail; JS-off submit; two-line mobile rows; the R8 chrome as it now sits on the landing. Control by control; URLs + screenshots; first-time-user judgment, not vs the record.
2. **Ask** — set `pending`, report findings + the inherited items for this surface (P7 Q3 board window size, Q5 live data refresh, Q6 #12 hero H1 name, Q9/Q10/Q11 where they touch the landing; P8 Q5 relocation of the gate-cost / disclaimer sentences — the landing bottom is the session's proposed home), ask *what's wrong and how should it be fixed?* STOP.
3. **Handoff** (resume) — `docs/reference/design/rounds/09-landing-board/handoff.md` per design-cowork (scope checklist from the answers, locked vs in-play with any copy exception named + dated, real paths, card set under `⏳ P8.S4 · Landing` with named paths, record + contract); commit; `pending`; STOP.
4. **Read back** (resume) — DesignSync `list_files`, concreteness check, land as-is under `rounds/09-landing-board/output/`, spec into `phase.md`, SIGNOFF entry, regroup, `finish-slice`, commit.

## Don't

No visual decisions of my own, no code, no edits to the record, no dispatching, no `plan.md` for `P8.S5`.
