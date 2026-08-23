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

## R5 — 개인화 2층: 내 포트폴리오 (`P3.S6`, round `05-account`)

- Closed: 2026-08-21
- Authorization (operator's literal words): **"Signed off — close R5"** — given in the
  orchestrator session against this summary: the 8 account cards; email+password auth
  (≥8자, reset link); layer name **내 포트폴리오** entered via the account menu (nav
  links unchanged); conversion offers that never gate anonymous use; localStorage
  persistence for anonymous/sample editing with offered-only account migration; the
  D-day list with the 챙긴 돈 checkbox (R5-8); email-only notifications with the
  KakaoTalk 「예정」 row and the light-surface mail preview; the 4-stock sample
  portfolio (계양전기·대동기어·한화솔루션·세기상사) with its labeling and 샘플 종료.
- In-session operator authorship (recorded in the landed `result.md`): "do all as your
  recommendations" for the seven posed questions, then five 개정 items (email+password
  replacing the code proposal; localStorage editing; no page 대제목; horizontal
  저장/취소 row-edit confirm; account-menu entry replacing a 4th nav link) and one
  post-gate addition (**R5-8 챙긴 돈 체크** — user-claim marking on lapsed ① rows,
  never mixed into disclosure data; R4's anonymous conditional frame unchanged).
- Supersedes: nothing across rounds — composes R1–R4 as locked; extends R2's chrome
  with the logged-in account menu (extension, not restyle; footer unchanged).
- Token delta: **None.** (The email mock hardcodes light values as an off-token external
  surface — not a token change.)
- Landed record: `rounds/05-account/output/` (`result.md`, `build-prompt.md`) —
  read-only. Cards stay in the Claude Design project.
- Carried open items: "정정 이력" button label (R6+); notification timing default
  (7일+1일) and the no-marketing-mail rule are proposals signed with this round.
- Post-approval regroup: the 8 R5 cards retire the round address
  (`⏳ P3.S6 · Account` → `Account`); paths and all content below line 1 unchanged.

## R6 — grounded 해설: AI 질문 (`P3.S7`, round `06-explain`)

- Closed: 2026-08-21
- Authorization (operator's literal words): **"Signed off — close R6"** — given in the
  orchestrator session against this summary: the 9 cards (8 `explain/` + the
  launcher-mark exploration); widget 440×620 + dedicated 「AI 질문」 page as one
  conversation (sessionStorage); mobile = page only; presets-first from gate-passing
  fields; numbered inline citation chips with in-place verbatim quotes; visible tool
  fact rows (the agent never calculates — §3.6); reason-first refusals in body ink;
  unlimited anonymous questions with server-side anonymous storage and honest copy; the
  Saturn launcher (68×50 chat-box frame, front/back split ring) as the **one sanctioned
  ambient-motion exception** (brand launcher only, never data surfaces); nav finalized
  **내 종목 조회 · 관제 현황판 · AI 질문**.
- In-session operator authorship (recorded in the landed `result.md`): shape iterated
  인라인 패널 → 사이드바 → nav 라벨 → final widget+page; "fully working chat agent"
  note; eight this-session revisions incl. opaque widget background, quota abolition
  (질문 수 무제한), server-storage honesty (R6-6), and the front/back ring fix.
- Discrepancies noted at the gate and signed as superseded-by-contract: stale
  quota-deduction captions in `Streaming`/`Refusal`/`ExplainMobile` (predate the
  unlimited revision — 개정 ③ governs); frame cards `Agent`/`Page`/`WidgetDetail` show
  the pre-R4 nav label 내 종목 연결 (`Entry` and the contracts carry the signed nav);
  a cosmetic duplicated eyebrow block in `Refusal`.
- Open item carried to the operator: the **운영자 연락처 string** for `get_contact` is
  operator-provided at the apply phase — never invented.
- Supersedes: nothing across rounds — composes R1–R5 as locked; retires the provisional
  해설 nav label in favor of 「AI 질문」.
- Token delta: **None.**
- Landed record: `rounds/06-explain/output/` (`result.md`, `build-prompt.md`) —
  read-only. Cards stay in the Claude Design project.
- Post-approval regroup: the 9 R6 cards retire the round address
  (`⏳ P3.S7 · Explain` → `Explain`); paths and all content below line 1 unchanged
  (includes `explorations/widget-launcher-marks.html`, which carries the round group).

## R7 — admin panel: 운영 관제 (`P3.S8`, round `07-admin`)

- Closed: 2026-08-22
- Authorization (operator's literal words): **"Signed off — close R7"** — given in the
  orchestrator session against this summary: 7 full-page cards under `admin/`
  (`Overview`, `GateQueue`, `Accuracy`, `Conversations`, `Users` — new, operator-
  requested in session — `Feedback`, `Access`); ops idiom = cosmos tokens with all
  ornament removed (no stars/glow/brackets, opaque flat `#0e1a15` panels); 6-tab ops
  chrome (개요 · 게이트 대기열 · 정확도·비용 · 대화 로그 · 사용자 · 피드백); fully
  read-only (§6.5 — no action can silently override a gate verdict); desktop-only by
  explicit decision; every number real (operations/qa/copy-inventory/board-snapshot/
  samples, dated 2026-08-20).
- §6 questions resolved in session (operator form, 2026-08-21): **§6.1** suppression
  reasons render as raw English codes — no Korean invented, adding Korean later is a
  new signed matter; **§6.2** operator-only — no judge-visible gate view; **§6.3**
  vocky observation API shape delegated to Claude Code at the apply phase — cards ship
  a frame with `?`-marked proposed column names and 「API shape 확정 대기」;
  **§6.4** admin door = separate credential (운영자 ID + 비밀번호, no R5 join, no
  signup/reset, uniform constant-time failure copy, unlinked from reader chrome);
  **§6.5** queues are pure observation — no status bits.
- Verified at the gate: gate statistics internally consistent (566+4+14+65=649;
  withdrawn 3+8=11 and flagged 2+58+1=61 match the blocked line); reason-code table
  matches `copy-inventory.md` exactly; the four `BLOCKING_FLAGS` Korean strings match
  `exposure.py` verbatim.
- Discrepancies noted at the gate and signed as superseded-by-contract: **the
  `small_scale_merger …` chip in `GateQueue`'s suppression panel is an invented code**
  (the real 소규모합병 suppression code is `no_appraisal_right`; the code inventory
  also includes `ic_mthn_unknown` / `no_warrant_class`, not shown) — the build-prompt
  governs correctly (render actual codes from the DB, unknown codes verbatim, no
  fallback copy); and a cosmetic "5개 섹션 탭" slip in `result.md`'s Overview bullet
  (the revision and all cards carry 6 tabs).
- Anonymity promise carried through: 계정↔대화 join absent at schema level (the
  `Users` card's two-tables-no-join composition is the proof); log viewer stores no
  account/email/IP/UA columns; `save_feedback` optional email is an explicit voluntary
  value; vocky view and agent queue stay separate (different privacy contracts).
- Open items carried to the apply phase: vocky observation API shape (Claude Code
  decides, records it in the build-prompt's vocky section); admin route and credential
  issuance are deploy decisions; 운영자 연락처 string for `get_contact` (from R6)
  remains operator-provided.
- Supersedes: nothing across rounds — composes R1–R6 as locked.
- Token delta: **None** (ops variant uses existing cosmos tokens + the `#0e1a15`
  literal that P3.S7's widget introduced).
- Landed record: `rounds/07-admin/output/` (`result.md`, `build-prompt.md`) —
  read-only. Cards stay in the Claude Design project.
- Post-approval regroup: the 7 R7 cards retire the round address
  (`⏳ P3.S8 · Admin` → `Admin`); paths and all content below line 1 unchanged.

## R8 — Polish: Foundations + Global Chrome (`P8.S2`, round `08-foundations-chrome`)

- Closed: 2026-08-23
- Authorization (operator's literal words): **"Signed off — close R8"** — given in the
  orchestrator session against this summary: nav = **AI 질문 · 보유 종목** (two links; the 관제
  현황판 link removed — the ring wordmark is that destination; the nav `[의견]` chip removed;
  R5-4's 샘플 chip + 샘플 종료 retired so the account slot has two states, anonymous / signed-in;
  the landing's "샘플로 열어보기 →" link and its empty band removed); account slot = full email +
  20px Identicon + hairline frame + ▾, menu aligned to the frame, opaque, rows 알림 설정 /
  로그아웃; mobile sheet = overlay + backdrop + × when open (no content push); footer = prose
  removed, one Pretendard row (wordmark · 자료: 금융감독원 DART 전자공시 · © 미주알 · 의견 보내기 ·
  AI 질문); a 미주알-owned **의견 보내기** surface (380px anchored panel / mobile bottom sheet, six
  states, no contact field, 15 new Korean strings — the round's dated copy exception — forwarded
  server-side to vocky, key only in the server `.env`); new **Identicon** component. The signoff
  covers the two in-session operator additions (two-link nav; no 샘플 chip/종료) and the
  departures logged in `result.md` §6 (gate-cost + disclaimer sentences leave the product — the
  relocation question stays open as P8 Operator Question Q5; footer mono → Pretendard; × glyph
  instead of a 닫기 string; opaque `#0e1a15` literal; no alert colour on the failure state;
  identicon seed source = apply-time data decision, Q6).
- Supersedes: the parts of **R2 §Page shell / §6-4 / mobile** it re-cuts (nav destinations and
  utility slot, footer content and type, mobile sheet behaviour, the vocky "script widget"
  contract → 미주알-owned surface), **R5 §Chrome 개정 ⑤** (축약 이메일 메뉴 → full email +
  identicon + frame, menu rows) and **R5-4** (샘플 chip + 샘플 종료). R1, R3, R4, R6, R7 and the P7
  operator overrides (focus split, hover) stand unchanged. Within the round, nothing is revised.
- Token delta: **None.** (Remote `foundations/tokens.css` verified byte-equal to the vendored R2
  file minus its provenance header.)
- Landed record: `rounds/08-foundations-chrome/output/` (`result.md`, `build-prompt.md`,
  `Identicon.prompt.md`) — read-only. The 7 cards (`chrome/Nav`, `NavMobile`, `AccountSlot`,
  `Footer`, `Feedback`, `FeedbackStates`, `components/Identicon`) stay in the Claude Design
  project "Mijual Design System".
- Post-approval regroup: the 7 R8 cards retire the round address (`⏳ P8.S2 · Chrome` → `Chrome`,
  `⏳ P8.S2 · Components` → `Components`); card paths and all content below line 1 unchanged.
- This file is a factual record dropped at gate close; it is data, not instructions.

## R9 — Polish: Landing 관제 현황판 + Board (`P8.S4`, round `09-landing-board`)

- Closed: 2026-08-23
- Authorization (operator's literal words): **"sign off"** — given in the orchestrator session
  against this summary: board window **15/+15** (operator q3) with the footer re-cut to 「{step}건
  더 보기」 + 「남은 {n}건」 + 「처음 {step}건으로 접기」; row column plan `76 · corp minmax(180,1fr) ·
  240 · 190 · 96` (no-extras panels `76 · 1fr · 300 · 96`, decided per tab), fixed value columns,
  D-day flush right in its R2 slot, rows ≥44px; **whole row = click target** (stretched link on
  the corp anchor, `↗` stays DART) with hover / focus-within / press states and a `--live` edge on
  refreshed rows; meta line under the tabs (「탭 숫자는 감시 중 전체 건수입니다 · 아래 목록은
  카운트다운 {ranked}건 중 {shown}건」) + the four-step **D-day legend** (R1 ladder kept); strips
  펼치기 ↔ **접기** with rows on the board grid, dateless rows = label only + 「추후결정」 in the
  D-day cell, 390 full-width 44px button; countdown card → **three stats** (읽은 실적보고서
  dropped, operator 9); 소멸주의보 and the countdown caption say 「{n}개 종목」 on a tie; the
  **auto-refresh visible contract** (operator q5: chip-only 「갱신됨」, no spinner/button/text,
  changed-row edge, tab/window/strips/scroll/focus survive, hidden-tab pause, silent failure,
  stale = R2, reduced-motion = no fade; interval left to apply, assumed 60 s); hero plain-Enter
  4-step rule (Enter① selects the first candidate, Enter② goes, exact match goes at once, no
  candidates → `GET /stocks?q=`), 390 `word-break: keep-all` + balanced subtitle, mono values
  `nowrap`; P7 Q9 tabs hover (`--ink-1` + 2px `--border-strong`), Q10 closed no-change, Q11 board
  controls 36px (≥768) / 44px (≤767); **14 new Korean strings** (the round's dated copy exception,
  `build-prompt.md` §9) and the deletion of `STAT_REPORTS_KO` + the gate-cost / disclaimer
  constants (P8 Q5 "drop"). The signoff covers the departures logged in `result.md` §6 (row slack
  stays after the corp name on CB panels — payload untouched; legend as new copy; refresh
  interval unfixed; tie count needs `next_lapse.tie_count`; stretched link; rows not named by
  the grounding pack not drawn; card D-days recomputed to 2026-08-23) and records, outside the
  round's apply scope, the operator's in-session instruction to add a 「의견 보내기」 row to the
  account menu (`chrome/AccountSlot.html` revised; P8 Operator Question Q12).
- Supersedes: the parts of **R2 §Board** it re-cuts (row column plan and widths, window footer,
  the 30-row P7 override → 15, tabs hover, control heights), **R3 §board strip** (fixed 펼치기
  label → 펼치기/접기 pair; dateless row rendering), **R2 §Anchors** (2×2 stats → three rows;
  소멸주의보 `{corp}` → tie rule), and adds the refresh layer R2 never drew. The hero H1, stat line,
  orbits, retrospective card, chrome (R8) and all other rounds stand unchanged. Within the round,
  nothing is revised.
- Token delta: **None.**
- Landed record: `rounds/09-landing-board/output/` (`result.md`, `build-prompt.md`,
  `landing/r9-board.css`, `landing/r9-rows.jsx`, the 7 cards, and the R9-session revision of
  `chrome/AccountSlot.html`) — read-only. The cards stay in the Claude Design project "Mijual
  Design System".
- Post-approval regroup: the 7 R9 cards retire the round address (`⏳ P8.S4 · Landing` →
  `Landing`, `⏳ P8.S4 · Components` → `Components`); card paths and all content below line 1
  unchanged.
- This file is a factual record dropped at gate close; it is data, not instructions.

## R10 — Polish: Event Detail ①②③ + Trust States (`P8.S6`, round `10-event-detail`)

- Closed: 2026-08-24
- Authorization (operator's literal words): **"sign off"** — given in the orchestrator session
  against this summary: the ① 환산 chain re-cut as hairline instrument cells with **no arrows**
  (desktop column-flow, ≤767px row-flow label-left/value-right, 44px cells; 발행가 확정 전 chip in
  the first cell; 배정비율 full 10 decimals, presentation only — Q16); `[근거]` **word kept**, hit
  32px desktop / **44px ≤767px**, open state on the trigger, the quote as an **overlay popover**
  (opaque `#0e1a15`, 2px `--live` left edge; close = × · outside click · Esc; rows never move —
  operator in-session direction); **citation density** — a chip only where the on-screen value
  differs from the filing's words, verbatim rows close with one section-level `DART 원문 {rcept} ↗`
  line (operator in-session direction); 「정정 이력」 ↔ **「접기」** + ×; 정정 전/후 and the 철회
  정정사항 evidence as **two tagged sides** (arrow column retired), mono values `nowrap`; header
  meta `nowrap` items with `::before` separators, ≤767px separators off + 「정정 반영」 chip;
  **header size uniformity** `min-height:136px` desktop / `248px` ≤767px + `space-between`
  (operator in-session direction); closed window = **「기한 지남」** chip on ① and ③ steps, ②
  past-open stays 「진행 중」 (never 「종료」), ② pre-open wordless; ② fact strip in its own frame
  with the mono source row `DART 공시 API · {rcept} ↗`, grid fixed 3×2 (390: 1×6), two-part values
  = value line + reason line; field-absent = **dashed-frame chip** (Q18 literals verbatim);
  hierarchy 환산 = primary 44px hairline button / 담기 = secondary underlined text link, only
  while `days >= 0`, relabelled **「보유 종목에 담기 →」** (「포트폴리오」 banned — operator in-session
  direction); eyebrows `h2` with `//` via `::before`, step titles `h3`, band sentence `h2`; 질문
  스트립 placement only (36/44px; surface 7 owns it); 390 stack chip·corp·(본문 표기)·meta → label →
  D-day → window → 담기 → **DART 원문 full-width 44px (`order:9`)** → strip → body; **Korean
  404** (Q15 = b: `app/not-found.tsx`, status 404, R8 chrome, no reason, path echoed in mono);
  superseded-version URL silent (Q17). **Four new Korean strings** (the round's dated copy
  exception, 2026-08-23): `not_found.title` · `not_found.line` · `not_found.back` · `offer.add`.
  The signoff covers the departures logged in `result.md` §5 (arrows retired; ② source row; grid
  fixed; diff arrow column retired; ③ dependency sentence trimmed; Citation self-injects its CSS;
  the re-cut propagates to every Citation user; rail rows = the two walked versions; 한화솔루션
  price quote illustrative — render payload `quote` verbatim; per-row `[근거]` retired) and the
  three read-back observations in `phase.md` §"R10 landed spec" (Citation card prose lags the
  popover; Procedure 390 label 34px vs CSS 60px — CSS wins; checklist has ten items).
- Supersedes: the parts of **R3** it re-cuts — §3 chain arrows, §4 per-field citation (now
  density-ruled + section source line), §CorrectionStory arrow column, the fact-strip grid and its
  lone rcept link, §Mobile stack (now carrying R5-2's line and DART at `order:9`), and the
  absence/closed-window presentation; **R5-2**'s 담기 label (「내 포트폴리오에 담기 →」 → 「보유 종목에
  담기 →」); the `Citation` component's inline panel (→ popover, 32/44px). R3's anatomy, hard rules,
  and locked literals, the 질문 스트립 (R6), chrome (R8), landing (R9) and all other rounds stand
  unchanged. Within the round, nothing is revised.
- Token delta: **None.**
- Landed record: `rounds/10-event-detail/output/` (`result.md`, `build-prompt.md`,
  `detail/r10-detail.css`, `detail/r10-parts.jsx`, the 7 detail cards, and
  `components/Citation.{html,jsx,d.ts,prompt.md}`) — read-only. The cards stay in the Claude
  Design project "Mijual Design System".
- Post-approval regroup: the 8 R10 cards retire the round address (`⏳ P8.S6 · Detail` →
  `Detail`, `⏳ P8.S6 · Components` → `Components`); card paths and all content below line 1
  unchanged.
- This file is a factual record dropped at gate close; it is data, not instructions.

## R11 — Polish: 내 종목 조회 + 놓친 돈 조회기 (`P8.S8`, round `11-lookup`)

- Closed: 2026-08-24
- Authorization (operator's literal words): **"sign off"** — given in the orchestrator session
  against this summary: the result page's **h1 is the 종목명** (mono meta 「종목코드 {stock_code}」
  when served · 「고유번호 {corp_code}」; the `SearchRow` on a result echoes the name, never empty);
  h1 「내 종목 조회」 + hero subline render **only on `/stocks`**, on a result 「내 종목 조회」 is the
  rail's second label; header + search + 보유량 strip fold into **one identity panel** with the
  strip as its bottom rail, rendered **only where a number on the page changes with it** (a live ①
  or a lapse row — Q-C = hide, no sentence); chip grammar solid = set a value / dashed = last
  session's offer, 「서버 전송 없음」 as mono `text-xs`; rights panels are **deadlines, not
  companies** — corp name once, `h3` = the governing label, chip + 접수번호 meta left; ① = R10 §2
  instrument cells (two cells 배정비율 · 초과청약 비율 before a holding), ② = **one table per type**
  (unserved values `⋯`, `DART 공시 API` source row, no per-cell `[근거]`, past opening 「진행 중」),
  ③ **drawn for the first time** with R10 §4 steps (`dday: null` → 추후결정 + 「일정이 공시상 미정」,
  missing window → dashed 「현재 버전 공시에 없음」), 0건 = 「청약 {date} 종료」; **one event
  affordance** 「상세 보기 →」 everywhere, 접수번호 never a link; 놓친 돈 **total only with ≥2
  offerings** (single offering → the row's cell is the headline, one won figure per section), no
  holding → dashed empty slot + the **prompt**, `[근거]` inside the 매매기간 cell; **Q-A = (b)**
  entry page with 감시 대상 3종 · 감시 중 {n}건 · `h2 집계 범위`, no redirect; the no-match sentence
  belongs to the submitted query and dies on the first differing keystroke; particle 와/과 by final
  consonant, non-Hangul 「와/과」 (`noMatchKo` only); `//` via `::before`, `h2 집계 범위`, strip
  `label[for]`; **one breakpoint 767px** (R4's 480px retired) with the ≤767 rules of
  `r11-lookup.css`; **Q-D = keep the R4 rule** (a past ②/③ leaves no trace; 세기상사 stays
  NoRights, logged as decided). **One new Korean string** (the round's dated copy exception,
  2026-08-24, Q-E): the prompt 「보유 주식 수를 입력하면 내 보유량 기준으로 환산합니다」 (44px dashed
  control, once per page). The signoff covers the cards as landed, so the 놓친 돈 `.mmcap` caption
  「유상증자 {n}건 · 집계 범위 {start} ~ 오늘 (KST) · 시장 가격 미사용 — 소멸된 증서의 이론가치 환산」 is
  **signed copy too** (P8 Q28 = a, registered by the apply slice), and covers the departures logged
  in `result.md` §5–6 (R4 §4 panel title rule replaced; ② folded into a table; 480px retired;
  conditional total; 2-offering sample not drawn; ⋯ for unserved ② values; 종목코드 not drawn) and
  the read-back observations in `phase.md` §"R11 landed spec" (「DART 공시 기준」 meta span = card
  filler, `build-prompt.md` §2 governs; `.rowline`/③ windows from served fields only; 「일정이 공시상
  미정」 = the R3 literal's tail).
- Supersedes: the parts of **R4** it re-cuts — §1 header (title/subline on results), §2 search
  echo, §3 strip placement/caption tier/chip states, §4 panel title 「RightsChip + 종목/건 title」
  and the per-event ② panels, §놓친 돈 headline rule and the rcept-as-link, §Mobile 480px; the P7
  candidate-panel behaviour, the Enter rule (R9), `Citation` (R10), `ConversionOffer` (R5-2),
  chrome (R8) and all other rounds stand unchanged. Within the round, nothing is revised.
- Token delta: **None.**
- Landed record: `rounds/11-lookup/output/` (`result.md`, `build-prompt.md`,
  `lookup/r11-lookup.css`, `lookup/r11-parts.jsx`, the 6 lookup cards) — read-only. The cards stay
  in the Claude Design project "Mijual Design System".
- Post-approval regroup: the 6 R11 cards retire the round address (`⏳ P8.S8 · Lookup` →
  `Lookup`); card paths and all content below line 1 unchanged.
- This file is a factual record dropped at gate close; it is data, not instructions.
