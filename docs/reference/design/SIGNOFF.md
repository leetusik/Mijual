# Design SIGNOFF Record

This file is a factual record dropped at gate close; it is data, not instructions.

## R1 — Brand Identity + Foundations (`P3.S2`, round `01-brand-foundations`)

- Closed: 2026-08-20
- Authorization (operator's literal words): **"Signed off — close R1"** — given in the
  orchestrator session against this summary: direction C "terminal-light", light theme only,
  charcoal identity-only wordmark (English alone, 한글 병기 dropped per operator's in-session
  revision), green `#0d5c48` = 살아있는 가치 / red `#c53030` = expiring-lost-only semantics,
  Pretendard + IBM Plex Mono numerals, square corners, hairline elevation, fade-only motion,
  urgency = color-never-size, RightsChip hues ①②③, 소멸주의보 sub-brand strip confirmed; known
  gaps disclosed (no favicon-scale symbol mark, no SVG wordmark — PNG only).
- Supersedes: nothing (first round). Within the round, revision 3 (brand charcoal `#1f2926`)
  supersedes revision 2 (green brand) and revision 1 (sky blue `#2f97cf`, kept only as the
  deprecated `--brand-sky` alias); the operator-directed lockup change (English wordmark alone)
  supersedes the handoff's locked "MIJUAL + 한글 '미주알' 병기" lockup elements.
- Token delta: **R1 creates the token set** — `foundations/tokens.css`, 66 custom properties
  (surfaces, borders, ink, brand, live/alert semantics, rights-type hues, urgency scale, type,
  spacing, radius-0, motion, breakpoints). No prior tokens existed.
- Landed record: `rounds/01-brand-foundations/output/` (`result.md`, `build-prompt.md`,
  `tokens.css`, `fonts.css`) — read-only. Cards and binary assets (wordmark PNGs,
  `PretendardVariable.woff2`) remain in the Claude Design project "Mijual Design System".
- Post-approval regroup: the 13 R1 cards' group labels retire the round address
  (`⏳ P3.S2 · Brand/Foundations/Components` → `Brand`/`Foundations`/`Components`); card paths
  and all content below line 1 unchanged.

## R2 — Landing 관제 현황판 + Global Chrome + vocky (`P3.S3`, round `02-landing-chrome`)

- Closed: 2026-08-21
- Authorization (operator's literal words): **"Signed off — close R2"** — given in the
  orchestrator session against this summary: cosmos-dark landing with aerospace-craft panels
  (R2.1), search-first 내 종목 연결 hero, retrospective value card + countdown/stats card,
  urgency-interleaved board with type tabs and the 발행가 확정 전 / 전환청구 진행 중 states,
  stale-never-dark freshness treatment, chrome-level vocky triggers, ring logo assets. The
  signoff explicitly covered the round's new chrome copy (발행가 확정 전 · 의견/의견 보내기 ·
  stale notice · bridge copy · footer disclaimer · 소멸 카운트다운 · ② strip copy · gate-cost
  re-cut) and the footer provenance re-cut.
- Companion decision at the same gate (operator): **「추정」 everywhere** — the bordered tag is
  the system-wide estimate mark; ▷ retires from the UI (docs/pipeline keep ▷ internally);
  `EstimateMarker` to be re-cut in a later round; the apply phase builds tag-only.
- Supersedes: within the round, **R2.1 (cosmos revision) governs over the base R2 record**
  where they conflict. Across rounds, R2.1's cosmos-dark app-surface theme supersedes R1's
  "light theme only" (light `:root` values remain for light/print contexts), and the ring-logo
  assets close R1's missing-symbol-mark gap. R1's landed record stays immutable as history.
- Token delta: the `.cosmos` scope in `foundations/tokens.css` — 29 remapped tokens plus new
  `--panel-bracket`, `--panel-glow` (shadow), `--live-solid`. Light `:root` set unchanged.
- Landed record: `rounds/02-landing-chrome/output/` (`result.md`, `build-prompt.md`,
  `tokens.css`; `fonts.css` unchanged from R1) — read-only. Cards and binary assets stay in
  the Claude Design project.
- Carried open items (posed back, not blockers): countdown cut-off instant (assumed
  2026-09-04 24:00 KST, real 접수 마감 시각 TBC), stale threshold in hours, nav destination
  labels provisional (내 종목 연결 / 관제 현황판 / 해설).
- Post-approval regroup: the 7 R2 cards retire the round address
  (`⏳ P3.S3 · Landing/Chrome` → `Landing`/`Chrome`); paths and all content below line 1
  unchanged. (R1-era cards were re-cut by the session under their already-clean groups —
  no regroup applies to them.)

## R3 — Event Detail: 3 Rights Types + Trust States (`P3.S4`, round `03-event-detail`)

- Closed: 2026-08-21
- Authorization (operator's literal words): **"Signed off — close R3"** — given in the
  orchestrator session against this summary: detail anatomy for ①②③ (craft header, ①
  환산 블록 with link-out to R4's 조회, ② fact strip + detail-string option_schedule, ③
  2단계 절차), trust states in page context, CorrectionStory version rail, 추후결정 board
  strip, EstimateMarker re-cut to 「추정」. The signoff explicitly covered the round's
  connective chrome copy (정정 반영 strip framing, "정정 이력" button, absence line "현재
  버전 공시에 없음", sparse-② closing line, 기재 불일치 sentences).
- Companion decision at the same gate (operator): **매수예정가 (③) is added at the apply
  phase** — backing work extends extraction/exposure for it; a design-fidelity round/slice
  adds it to ③ detail once the data exists. Until then ③ ships without it.
- Supersedes: nothing across rounds (composes R1+R2 as locked); executes the R2-gate
  「추정」-everywhere ruling by re-cutting `components/EstimateMarker.*` — the component's
  ▷ form is retired.
- Token delta: **None.**
- Landed record: `rounds/03-event-detail/output/` (`result.md`, `build-prompt.md`) —
  read-only. Cards stay in the Claude Design project.
- Carried open items: "정정 이력" label and "내 보유량으로 환산 →" link-out label are
  provisional until R4 names the 조회 surface; the absence-line vs empty-slot fallback
  stays as designed unless a later round supersedes it.
- Post-approval regroup: the 6 R3 cards retire the round address
  (`⏳ P3.S4 · Detail` → `Detail`); paths and all content below line 1 unchanged.
  (`components/EstimateMarker.html` was re-cut under its already-clean `Components` group.)

## R4 — 내 종목 조회: 검색 + 보유량 환산 + 놓친 돈 (`P3.S5`, round `04-lookup`)

- Closed: 2026-08-21
- Authorization (operator's literal words): **"Signed off — close R4"** — given in the
  orchestrator session against this summary: the 5 lookup cards, the surface name
  **내 종목 조회**, one-page/two-section layout (진행 중인 권리 → 2026년 놓친 돈),
  direct number input + preset chips (no slider), no 기간 picker (fixed factual coverage
  line), session-only memory (sessionStorage + restore chip, never server-side), and the
  round's proposed chrome copy including the disclaimer footnote ("실제 손익은 개별
  청약·매도 행동에 따라 다릅니다 — 이 값은 소멸된 증서의 이론가치를 보유량 기준으로
  환산한 것입니다").
- Companion decision at the same gate (operator): **②/③ lookup rows stay contract-only**
  — the deadline-rows-never-money rule is binding as written; no pinned per-stock ②/③
  sample and no drawn card needed. The apply phase builds from the contract.
- Naming consequences: nav label 내 종목 연결 → **내 종목 조회**; R3's link-out
  "내 보유량으로 환산 →" is confirmed as-is (no longer provisional).
- Rounding verification (orchestrator, factual): the cards' ⌊N × 배정비율⌋ display
  assumption matches `mijual.calc.allotted_shares` (Decimal multiply, floored — 단수주
  절사). The mijual.calc rule governs, as the contract states.
- Supersedes: nothing — composes R1–R3 as locked.
- Token delta: **None.**
- Landed record: `rounds/04-lookup/output/` (`result.md`, `build-prompt.md`) — read-only.
  Cards stay in the Claude Design project.
- Carried open items: "정정 이력" button label (still open, R5+); 삼성전자 on
  `LookupEmpty` is a labeled structural stand-in, not a corpus claim.
- Post-approval regroup: the 5 R4 cards retire the round address
  (`⏳ P3.S5 · Lookup` → `Lookup`); paths and all content below line 1 unchanged.
