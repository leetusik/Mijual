# R2 Round Record — Landing 관제 현황판 + Global Chrome + vocky

- Session: Claude Design + operator, 2026-08-21 · slice P3.S3 · builds on R1 (locked)
- Operator answered all six open questions "do as your recommendations" — the six below are **session decisions, revisitable**.

## Session decisions (the handoff's §6 + two composition calls)

1. **Retrospective vs live (§6-1): one page.** Hero anchor = the retrospective ▷ 718.1억원 (the only big money number the corpus can currently claim — the most-urgent live rows have no ▷ value by construction), with band 하한 ▷ 548.7억원 shown beside it. The live layer (stat panel + ticking countdown + 소멸주의보 + board) sits directly beneath, above the fold. No separate retrospective page in R2.
2. **Board ordering (§6-2): urgency-interleaved, type-filter tabs** (전체 · 유상증자 신주인수권 · 전환사채 오버행 · 주식매수청구권, counts in mono; 전체 default). Survives the 50/422/16 imbalance without letting ② bury ①.
3. **② calendar (§6-3): deferred to R3 detail.** A board row carries exactly one governing countdown (①매매 마감 / ②전환청구 개시 / ③반대의사 통지 마감); 보호예수 해제 etc. are detail-page fields.
4. **vocky trigger (§6-4): chrome-level but not floating.** Nav utility slot `[의견]` (desktop) + sheet-menu row (mobile) + quiet footer link 의견 보내기. No floating corner button — it would fight the control-room density. Contract: plain elements with `data-vocky-trigger`; vocky's script binds and opens its own UI (never styled/overridden here); admin observation of collected feedback is R7.
5. **Mobile nav: top bar (52px) + sheet menu** (rows ≥48px). No bottom tab bar until R3+ adds surfaces.
6. **지남 rows, per type (ui-traps §5):** ② past-opening rows appear as a `전환청구 진행 중 — 56건` strip pinned under the board (never "종료"; 진행 중 in `--live` green), collapsed by default with 펼치기. Past ① (lapsed) and ③ (passed) do **not** appear on the landing — they belong to 종목 조회 (R4) and the retrospective table.

## The 확정발행가-not-yet state

First-class, per handoff: ① rows before price fixing show an inset sans chip **`발행가 확정 전`** (surface-inset, same primitive family as 추후결정 but a distinct string — it is a known-later fact, not a TBD schedule) beside the real 청약 date. Never a dash, never an empty value cell.

## Freshness (stale-never-dark)

- Board header always carries `기준 YYYY-MM-DD HH:MM KST` in mono `--ink-3`.
- Stale state: the chip flips to alert-tint + rust text (`… · N시간 전 데이터`) and an inset notice with 2px rust left rule appears above the tabs: "데이터가 갱신되지 않고 있습니다. 아래 값은 기준 시각의 공시 기준이며, 그 이후의 정정공시는 반영 전일 수 있습니다." The board itself renders fully — data never dims, never skeletons.
- Threshold for "stale" (hours?) is an implementation input — posed back.

## Countdown

Hero ticker counts to the earliest true 소멸 moment: 계양전기 청약 마감 2026-09-04 (발표용 문장 4). Mono, rust, colon blink 1s step-end, `prefers-reduced-motion` freezes it. **Assumption posed back:** cut-off instant is 2026-09-04 24:00 KST — the real 접수 마감 시각 (증권사 영업시간) needs confirming. Board D-days remain upstream-computed KST; the ticker is presentation over a fixed KST instant only.

## Copy — proposed additions (chrome copy, not in copy-inventory; needs sign-off)

- `발행가 확정 전` (board chip) · 의견 / 의견 보내기 (vocky trigger) · stale notice sentence (above) · bridge copy "내 종목 연결 / 종목명으로 놓친 권리와 진행 중인 권리를 조회합니다" · footer disclaimer "미주알은 투자 자문·권유를 제공하지 않습니다. 모든 정보는 DART 공시 원문 확인을 전제로 제공됩니다." · board title 소멸 카운트다운 · strip copy "전환청구 진행 중 — 개시일이 지나 지금 전환할 수 있는 전환사채 56건".
- Hero re-cut stays within 발표용 문장 numbers/markers; sentences 1·2·4 used near-verbatim; gate sentence re-cut as "▷ 49.2억원은 할인율 인용이 게이트를 통과하지 못해 총액에서 제외했습니다".

## Naming gaps posed back

- Nav destination labels are **provisional**: 관제 현황판 / 종목 조회 (조회기·R4) / 해설 (R6) / 로그인 (2층). Operator to confirm user-facing Korean names — none exist in product.md as UI labels.

## Departures from the handoff

- None structural. All seven required card paths delivered; no extra components added; no token delta (R1's 66 tokens sufficed — zero additions to `foundations/tokens.css`).
- Demo timestamps in freshness treatments (18:00 / 09:00) are illustrative, not measured.

## Grounding used (all real, none invented)

`board-snapshot.md` (488/50/422/16 counts, top rows per type, 56 open-② count, 34 ≤30d), `headline-numbers.md` (▷718.1 / ▷548.7 / 51,253,956주 / 14.02% / ▷206.4 한화솔루션 / ▷49.2 gate cost / 15건 / 69건 / ① 청약 dates), `copy-inventory.md`, `states-and-trust.md`, `ui-traps.md` (§5 drove decision 6).

## R2.1 — Cosmos revision (same session, operator-directed)

Live iteration after the R2 record above; where they conflict, R2.1 governs.

1. **Theme pivot for app surfaces: cosmos-dark.** The landing (desktop + mobile) runs one continuous full-page starfield with root-level green radial glows and shooting stars staggered down the page. Implemented as the `.cosmos` token scope in `foundations/tokens.css` — every surface/ink/border/semantic/rights/urgency token remaps, so R1 components (RightsChip, DDay, EstimateMarker) adapt unchanged. Chrome cards (Nav/Footer/Feedback) re-cut on cosmos with the white ring wordmark.
2. **Cards become aerospace-craft panels**: translucent dark surface (`--surface-card` cosmos), luminous hairline + top-edge glow (`--panel-glow`), 9px corner brackets (`--panel-bracket`). 소멸주의보 is a hazard placard — alert border + 10px striped left edge (repeating −45° alert stripes).
3. **Hero recomposed, search-first (내 종목 연결)**: center logo and the `//` eyebrow removed — the nav carries the mark; H1 → search row (dark console input + `--live-solid` 조회) → mono stat line. Orbit ellipses stay **full-size and hero-only** (operator: never shrink them — give the hero vertical room instead, so rings clear the nav line and the panels below).
4. **Retrospective anchor moved off the hero** into its own craft value card beside the countdown/stats card (1fr / 340px, 20px gap). The gate-cost sentence (▷49.2억원) was removed from the card — it survives only in the footer fine print.
5. **Estimate mark on landing surfaces: ▷ → bordered mono 「추정」 tag** beside the value (10px sans, `#5fd0a5` hairline). Footer provenance re-cut to "…추정치는 [추정] 표시로 구분했습니다" — **locked-copy change, needs operator sign-off**. `EstimateMarker` and the Headline card still carry ▷ pending a system-wide decision.
6. **Token delta now exists** (supersedes "zero additions" above): the `.cosmos` scope (~29 remapped tokens) + `--panel-bracket`, `--panel-glow` (shadow), `--live-solid`.
7. Nav destination labels iterated to **내 종목 연결 / 관제 현황판 / 해설** (still provisional, still posed back).
8. **All card groups matched to the new look**: Brand (white-primary logo lockup on cosmos, 소멸주의보 as hazard placard), Components (all specimen cards on `.cosmos`; EstimateMarker card notes the 「추정」-tag direction), Foundations (color cards show cosmos scope values + craft tokens, craft-panel elevation demo, cosmos ambient motion documented, [추정] type specimen), plus a cosmos project thumbnail. Light `:root` values remain for light/print contexts.
