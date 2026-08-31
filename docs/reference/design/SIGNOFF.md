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

## R12 — Polish: Auth (로그인 · 계정 만들기 · 비밀번호 재설정) + 전환 제안 (`P8.S10`, round `12-auth`)

- Closed: 2026-08-24
- Authorization (operator's literal words): **"sign off"** — given in the orchestrator session
  against this summary: **Q-A = (b)** `noValidate` + Korean — **two** lines 「이메일과 비밀번호를
  입력해 주세요.」 / 「이메일 주소 형식이 올바르지 않습니다.」 (default (c) rejected: `invalid_email`
  has no signed Korean, so 계정 만들기's empty submit would render nothing); **Q-B** = every login
  lands `/portfolio`, origin not carried, offer copy not extended; **Q-C** = one token 「8자 이상」
  mono `text-xs` on the 비밀번호 label row, **계정 만들기 + 재설정 only** (never 로그인); **Q-D** =
  rail 「← 관제 현황판」 as the 480px column's first row on both auth pages, panel stays R5's
  centered panel. 재설정 is **never disabled for an empty address** — clicking focuses the 이메일
  field (R11's prompt→focus grammar); `disabled` only while pending. Primary button **full-width
  48px at every viewport** (R5's 160px min-width + left-align retired). **One breakpoint 767px**
  (R5's 480px block retired). Four states drawn: 확인 중… = label swap + disabled + opacity .72 (no
  spinner) · error `--ink-1` · notice `--ink-2`, one `p role="status"` slot, `--alert` never on
  this layer; focus-visible inputs offset −1, buttons/quiet/rail offset 2, hover = colour only.
  로그아웃되었습니다 = flash band **above the h1**, no timer (first keystroke/submit/navigation
  clears it). Reset page: one 비밀번호 field + rule, **no 이메일 field, no sample entry**;
  `invalid_reset_token` → 「이 재설정 링크는 만료되었거나 이미 사용되었습니다 — 새 링크를 요청해
  주세요.」 + quiet 「로그인」 in that state only; success = sessions revoked, new session,
  `/portfolio`, **no completion screen**; no `?token` → redirect (unchanged). Conversion ladder
  (surface = rank): page numbers > **`ConversionOffer` as an inset band** (CraftPanel dropped; 닫기
  44×44, CTA 44px; placed after the last data section, **before 집계 범위/프로비넌스**) >
  `DeadlineOffer` one-line link (R10, untouched, renders nothing until session known) > nav 로그인
  (R8, untouched). **Four new Korean strings** (dated copy exception 2026-08-24): `PASSWORD_RULE_KO`
  「8자 이상」, `ERR_FIELDS_REQUIRED_KO`, `ERR_INVALID_EMAIL_KO`, `ERR_RESET_TOKEN_KO` — the latter
  two map `invalid_email` / `invalid_reset_token` in `authErrorKo`. **Operator removals taken in
  session**: the PII inset on both auth pages (`PII_RECEIVES_KO`, `PII_NOT_STORED_KO`,
  `PiiInset.tsx` — withdraws R5-1's 「PII 패널은 로그인 화면 상시 요소」 clause), `CONVERT_STAY_KO`,
  and `CONVERT_BODY_KO`'s trailing clause → 「계정에 저장하면 마감이 다가올 때 이메일로 알립니다.」
  The coverage-boundary caption is struck **on the R12 Offers card only** — the lookup surface
  keeps it per R11's record (P8 Q39, default keep). The signoff covers the departures logged in
  `result.md` §4 (two lines vs one; disabled retired, not re-labelled; 480px block and 160px
  min-width deleted; offer demoted panel → band; Q-B default + copy left alone; no sample entry on
  reset; success drawn as a statement) and the read-back observations in `phase.md` §"R12 landed
  spec" (the Offers card's `.m390 .hd` order overrides are card-harness-only; `.pii*` and `.aostay`
  stay in the canon unused).
- Supersedes: the parts of **R5** it re-cuts — R5-1's auth panel geometry (480px breakpoint, 160px
  primary), the PII-inset 상시 요소 clause, and the validation/disabled behaviours; R5-2's
  `ConversionOffer` surface (panel → inset band) and its 카피 list (two strings removed, body
  shortened); R5-4's sample-entry sub geometry (balance + 34ch). `DeadlineOffer` (R10), nav (R8),
  and all other rounds stand unchanged. Within the round, nothing is revised.
- Token delta: **None.**
- Landed record: `rounds/12-auth/output/` (`result.md`, `build-prompt.md`, `account/r12-auth.css`,
  `account/r12-parts.jsx`, the 3 account cards) — read-only. The cards stay in the Claude Design
  project "Mijual Design System"; `account/Auth.html` replaces the R5 card at that path.
- Post-approval regroup: the 3 R12 cards retire the round address (`⏳ P8.S10 · Account` →
  `Account`); card paths and all content below line 1 unchanged.
- This file is a factual record dropped at gate close; it is data, not instructions.

## R13 — Polish: 보유 종목 + 알림 설정 (`P8.S12`, round `13-portfolio`)

- Closed: 2026-08-24
- Authorization (operator's literal words): **"sign off"** — given in the orchestrator session
  against this summary: the **D-day rows get four content-independent tracks**
  (`84px · minmax(0,1fr) · 212px · 208px`, gap 4px 16px) shared by every row of both sections —
  no column headers, no vertical rules, surface width 960px; row bodies sit on the same tracks
  (`grid-column:2/-1`, money line `minmax(0,1fr) 208px`) so every 금액's right edge equals the
  countdown edge — P7 Q8-A's measured 144.7px ragged edge / 584.6–761.3px empty middle becomes
  structurally impossible. Past chip + date on one line; anchor 「기준 {ref} (KST)」 **once per
  block**, outside the sections (P7 Q8-B closed as page-level). Empty 진행 중인 권리 cell =
  `.pslot` **dashed hairline 56px** (no sentence, no dashed box, no `—`); holdings rights cell
  gets tracks `52px minmax(0,1fr) auto` (session revision — one right edge for all countdowns).
  **Q-B re-decided in session (supersedes the gate default): 「놓친 돈 상세 →」 moves into the
  money line and does not render on a checked row** (returns on uncheck); the control line keeps
  only the checkbox; `.pmlead{min-height:32px}` (44px ≤767) holds the height so checking moves a
  **measured 0px** (row 161px · money line 32px · checkbox top 1095; 390: 249px · y 973) — P7
  Q8-D fully closed. Claim caption renders unconditionally (P7 Q8-E); a 챙겼습니다 row **stays**
  in 지나간 마감 (P7 Q4 = R5-8 stands); `carryOverKo` and both claim captions kept as-is (P7
  Q7④+fifth). **Sample**: no reset/종료 control returns — **R5-4's 「종료」 clause is officially
  withdrawn**, permanent browser edits accepted, `clearSample()` migrate-only; the **R12
  conversion band renders after 지나간 마감** under the R12 ladder rules, **without the lead
  line** (「이 보유량은 탭을 닫으면 사라집니다」 is false on this surface) — body + CTA + 닫기,
  session-once, dismissible. **알림 설정**: rail 「← 보유 종목」 + `h2`→`h1` promotion; row grid
  `104px minmax(0,1fr) auto`; the R12-inherited `invalid_email` line is **wanted** (body-ink one
  line, no `--alert`); chips `aria-pressed`, an empty selection is a valid setting; KakaoTalk
  row keeps no control; **계정 삭제 arms in place and its signed sentence renders only when
  armed** (withdraws R5's 상시 clause); 로그아웃·계정 삭제·취소 share one `.pact.wide` box.
  **Terminology (session revision): reader surfaces never say 「포트폴리오」** — the layer is
  보유 종목; `EMPTY_TITLE_KO` → 「보유 종목이 비어 있습니다」, `SAMPLE_BANNER_KO` → 「샘플 보유
  종목 — …」 (operator revision of R5 strings; routes/paths/component names unchanged). **Both
  480px media blocks are retired** for the single 767px boundary. **New Korean 0건** — two
  compositions of existing tokens only (rail `← ` + `PORTFOLIO_LABEL_KO`, `「」` +
  `PLANNED_CHIP_KO`); the login page's 「실제 공시 4건」 stays (a filing count, not a row count).
  The signoff covers the departures logged in `result.md` (the Sample card borrows
  `account/r12-auth.css` verbatim; card-data gaps rendered as ⋯, never invented) and the
  read-back observations in `phase.md` §"R13 landed spec" — including **Q46 = (a)**: the served
  `stock_code` keeps rendering at the `.phmeta` tier (the cards' omission was a data gap, not a
  removal).
- Supersedes: the parts of **R5** it re-cuts — §D-day 목록's row layout (`space-between` →
  tracks), the 지나간 행 line rhythm, R5-4's 종료 clause and the 샘플/계정 이전-only
  `clearSample`, R5-5/R5-7's always-on 계정 삭제 sentence and unequal action boxes, R5-3's
  `EMPTY_TITLE_KO` / R5-4's `SAMPLE_BANNER_KO` wording, and the two 480px mobile blocks. P7's
  layout-primitive corrections stand; R12's offer band and ladder stand and extend to this
  surface. Within the round, Q-B and Q-D were re-decided by the operator in session before close.
- Token delta: **None.**
- Landed record: `rounds/13-portfolio/output/` (`result.md`, `build-prompt.md`,
  `portfolio/r13-portfolio.css`, `portfolio/r13-parts.jsx`, the 4 portfolio cards) — read-only;
  the operator's post-session text corrections are in the landed files byte-exact. The cards stay
  in the Claude Design project "Mijual Design System".
- Post-approval regroup: the 4 R13 cards retire the round address (`⏳ P8.S12 · Portfolio` →
  `Portfolio`); card paths and all content below line 1 unchanged.
- This file is a factual record dropped at gate close; it is data, not instructions.

## R14 — Polish: AI 질문 (`P8.S14`, round `14-ask`)

- Closed: 2026-08-24
- Authorization (operator's literal words): **"sign off"** — given in the orchestrator session
  against this summary: **the surface migrates to the product-wide 767 boundary (Q-A = (a))** —
  launcher and widget *exist* only >767px (the three 480 lines in `Ask.module.css:421`,
  `AskPage.module.css:64`, and `useAsk.ts`'s `DESKTOP_QUERY` all move; the widget's `max-width`
  guard is retired, `max-height` stays), and 481–767 gets the full-width `/ask` page exactly as a
  phone does. **Footer 근거 N건 counts chip numbers** (하나의 근거 = 하나의 칩 — the operator's own
  sentence; filings are counted by the rcept_nos that follow). **The composer's send button gets
  the round's one operator-specified string 「보내기」 (Q-C)**; 「직접 질문 입력 →」 returns to the
  strip's free-input chip only, closing the `copy.ts` reuse flag. **Preset chips show the served
  `korean_name` label but send a full signed question (Q-D)** — nine new sentences R14-D1…D9 plus
  R6's 실권주 sentence; templates stay banned and a field key outside the signed table renders
  **no chip** (no label-sending fallback). **Answer prose grows as one paragraph (Q-E)** — R6's
  프로즈 자람 literally; stream-carried leading whitespace/newlines are normalized at the store
  boundary; the only inter-sentence gap is the CSS `0.25em`. **`/ask` ≤767 renders no vocky ⓝ
  trigger (Q-F)**; >767 keeps it (768–1024 corner contact is a `P8.S15` measurement item).
  **`API_TIER_KO` is retired (finding 10, closes P7 Q7①)** — the span-less citation block is the
  `DART 원문 {rcept_no} ↗` link alone. Also signed: tool rows are one nowrap line with hidden
  horizontal scroll (no mid-number breaks — R10 §0), disabled send is the ghost tier
  (`opacity:.72` retired), thread/quote scrollbars go thin product-style, `/ask` desktop is a
  centered `minmax(0,760px) 340px` bundle (`max-width:1124px`) with a sticky rail and a sticky
  bar that stands under the last element on short threads, and the empty **scoped** widget fills
  its middle with the preset row (전체 공시 stays empty — that *is* the state; no empty-state copy
  was minted).
- Copy: **신규 10건** (「보내기」 + the nine R14-D1…D9 preset questions), all dated and reasoned in
  `result.md` §Copy; **회수 2건** — `API_TIER_KO`, and `ASK_SUBMIT_KO`'s composer use (the
  constant survives on the strip's free chip). Chip labels are the server's `korean_name`
  throughout — the record writes none of them.
- Supersedes: the parts of **R6** it re-cuts — the 480/481 existence boundary (§Surfaces /
  §Mobile now read at 767), the composer idle label as send, `label`-as-question presets, and
  **R3's** API-tier block sentence. Everything else R6 signed stands verbatim: 440×620 · #0e1a15 ·
  28px header icons · tool-row verbatim printing · caret 7×15 1s step · footer fade · the single
  중단 sentence · fades-only motion · the launcher mark (개정 ⑤/⑧) untouched — only its existence
  condition moves.
- Token delta: **None.**
- Landed record: `rounds/14-ask/output/` (`result.md`, `build-prompt.md`, `ask/r14-ask.css`,
  `ask/r14-parts.jsx`, the 5 ask cards) — read-only. The cards stay in the Claude Design project
  "Mijual Design System".
- Post-approval regroup: the 5 R14 cards retire the round address (`⏳ P8.S14 · Ask` → `Ask`);
  card paths and all content below line 1 unchanged.
- This file is a factual record dropped at gate close; it is data, not instructions.

## R16 — Smart Mijual Assistant: 통합 어시스턴트 + 구조화 채팅 표면 (`P9.S2`, round `16-smart-assistant`)

- Date: 2026-08-25
- Authorization (operator's literal words): **"done"** — given in the orchestrator session on
  completing the R16 Claude Design session, whose decision record (`output/result.md`) carries the
  operator's in-session answers Q-A…Q-E and the session revisions (D1 intro re-cut, D2/D4 abandoned
  in-session, D11 re-cut to four cards). Summary signed against: **Q-A 공시 사실 해설로 한정** (범위
  밖 일반 투자 질문은 거절 가족이 아닌 한 줄 응답) · **Q-B P16 클레임 단위** (「미확인」 마커; 턴
  단위 교체 게이트 불채택) · **Q-C 여섯 번째 거절 가족 「보안」 신설** · **Q-D 카테고리 + 200자
  발췌 + session_hash, 로그 전용** · **Q-E 남용 백스톱 추가하지 않음**. New surface: 계산 블록
  (입력·식·결과, 입력마다 자기 칩) · 데이터 행 (라벨/값 쌍 + 값 칸 스크롤) · 진행 표시 5구
  (transient, 점선, 무애니메이션) · 도구 흐름 접힘 (4행+, 완료 시) · 마커 3종 (추정·계산·미확인).
  `/ask`는 340 레일을 폐기하고 단일 채팅 열 + 시작 화면 (D9 인사 · D1 인트로 · 질문 카드 4장 ·
  새 대화는 스레드가 있을 때만)이 된다; 범위 칩과 익명 줄은 표면에서 퇴장한다.
- Copy: **신규 8건 + 진행 5구 + 계산/데이터/흐름 어휘** (D1 · D3 · D5 · D6 · D7 · D8 · D9 · D10 ·
  D11), all dated and reasoned in `result.md` §2; **은퇴 3건** — 「계산 요청」 가족 문장, 「검증
  미통과 폴백」 + `REFUSAL_FALLBACK`, R14의 「다시 질문」 (+ 익명 줄과 범위 칩 카피가 표면에서
  퇴장, D2 레일 약속 줄은 대체 없이 초월).
- Supersedes: `AGENT_INTRO_KO` (R6) → D1 · R6 하드 룰 「에이전트 계산 금지」 → 감사 가능한 계산기
  (브라우저 계산 금지는 유지) · R6-7 다섯 가족 중 둘 은퇴 + 「보안」 신설 (저장 어휘 6값) · R6/R14
  범위 칩 + × 폐기 · R6-5 익명 줄 카피 폐기 (성질은 기능으로 유지) · R6/R14 (f9) `/ask` 340 레일
  폐기 · `record_turn` 저장 대상 + 구조화 블록 원형. **초월되지 않은 것** (명시, `result.md` §5):
  스피너·타이핑 점 금지 · 인용문 재구성 금지 · 이력 UI 금지 · quota 표기 금지 · 거절 alert 색 금지 ·
  같은 근거 = 같은 번호 · 도구 행 verbatim · 단일 스토어 · 767 단일 경계 · R14 컴포저·프리셋 결정
  (범위 칩만 예외).
- Token delta: **None.** (`foundations/tokens.css` unchanged; 신규 토큰 0건.)
- Landed record: `rounds/16-smart-assistant/output/` (`result.md`, `build-prompt.md`,
  `r16-ask.css`, `r16-parts.babel.js`) — read-only. The 10 cards stay in the Claude Design project
  "Mijual Design System".
- Known stale lines inside the landed `build-prompt.md` (record kept as-is; the signed copy in §0
  and `result.md` govern): 회귀 15 still keeps the 340 rail that §2.7b/회귀 20 retire; §2.7b and
  회귀 21 say "질문 카드 5장"/메타 카드 where D11 and `START_CHIPS_KO` sign four cards and retire
  the meta card. Catalogued for `P9.DECOMP2`; not silently edited.
- Post-approval regroup: the 10 R16 cards retire the round address (`⏳ P9.S2 · Ask` → `Ask`,
  `⏳ P9.S2 · Components` → `Components`); card paths and all content below line 1 unchanged.
- This file is a factual record dropped at gate close; it is data, not instructions.

## R17 — 주주의관제탑: the mark in the chrome, and the chatbot launcher (`P10.S6`, round `17-brand-mark-launcher`)

- Date: 2026-08-31
- Authorization (operator's literal words): **"done"**, then **"and no mockup, just apply
  directly."** Given in the orchestrator session on completing the R17 Claude Design session,
  whose record (`output/result.md`) carries the operator's in-session answers to Q2 (잉크 정렬),
  Q5 (모션 예외 폐기) and Q7 (1급 심볼), their mid-session artwork replacement (§1b), and their
  approval of the five departures in §5–§7b. Q1, Q3, Q4 and Q6 were left to the session and are
  decided in the record with their reasoning.
- **The mockup gate was waived by the operator, and this signoff is not a substitute for it.**
  The `design-cowork` loop normally puts a runnable throwaway route in front of the operator
  before SIGNOFF; the operator declined it and directed the apply slice to go straight to the
  real implementation. So **nobody has yet seen this design running.** The phase's own
  **operator acceptance gate** (`accept-gate P10 --require`, already declared and now reset by
  the `changes_requested`) becomes the round's only running review — and, per the skill, seeing
  the product and changing their mind there is a `changes_requested` plus a new superseding
  round, not a fidelity failure.
- Summary signed against: **워드마크 nav `h27` / footer `h24`** (R2's h19/h17 retired), **잉크 정렬**
  `translateY(-7px)` / `-6px` from the band's geometric centre at 76.28% of box height
  (`INK_OFFSET` 0.2628·H) · **런처 = 32×32 스파클 심볼**, R6's 22×22 Saturn (planet + rotation band
  + two clipped ring halves, 4.5s / 14s) **deleted outright**, the 68×50 frame and its tail kept ·
  **상시 모션 예외 만료** — the product now has no ambient motion anywhere, and hover response moves
  to colour (`#eaf2ed` → `--live`), which survives reduced-motion because colour is not motion ·
  **심볼 = 1급 마크**, painted by CSS `mask` + `currentColor` rather than shipped as a coloured
  `<img>`, ink box **222×165**, ink width **84%** of a square box, centred on both axes ·
  **파비콘 16/32/180** on an opaque `#0a1310` tile — the "no favicon, and this mark does not become
  one" section of `frontend/public/assets/README.md` is retired.
- Copy: **신규 0건.** No string was added, removed or reworded by this round.
- Supersedes: **R2 §Page shell** (wordmark heights and box-centred placement) · **R6 §런처 마크**
  (the Saturn, its two animations, and the operator note granting the product's one ambient-motion
  exception) · **R6** the open-state × colour `#dfe9e4` → `#eaf2ed` · **`assets/README.md`**'s
  favicon prohibition. **초월되지 않은 것:** all of R8's chrome structure (52px bar, two
  destinations, account slot, mobile sheet, the single footer row and its order) · R14's launcher
  existence boundary (desktop only, never `/ask`, never ops, `z-index:30`) · all copy · the a11y
  floor · `foundations/tokens.css`.
- Token delta: **None.** (`foundations/tokens.css` unchanged; the cards override `--font-sans`
  inside themselves only, to stand in the Noto Sans KR that `P10.S7` will actually ship.)
- **Two defects in the operator's own delivered files, both caught by this round and both
  independently re-verified by the orchestrator before landing:**
  1. **`juju2.png`의 「의」 카운터가 뚫려 있지 않았다** — 2,864 opaque near-white pixels inside the
     ㅇ. The alpha-preserving white recolor keeps opaque pixels opaque, so the counter would render
     as a solid white blob — **visible only in the white variant, which is the only one the product
     uses.** The operator resent the artwork as `juju2_2.png`. *(Re-verified 2026-08-31: the
     `juju2.png` now on disk is byte-different from the one this phase started with and is
     **pixel-identical** to `juju2_2.png` — `compare -metric AE` = 0, same `identify %#` signature —
     so the operator fixed both copies. The derivation guard stands regardless: the derivative's
     opaque near-white pixel count must be **0**.)*
  2. **`favicon_and_chatbot_widget.png`에 유령 잉크가 있다** — two low-alpha fragments at the
     bottom-left, which is why `-trim` reports 261×216 instead of the real ink's **222×165**.
     `-trim` preserves them (alpha > 0) and the white recolor turns them into visible smudges on
     the cosmos surface. The signed derivation therefore **crops explicitly**
     (`-crop 222x165+39+62`) and never trims. *(Re-verified: `-trim` → 261×216+0+62; the crop
     re-trims to 222×165+0+0, tight; ink = 2,481 px, matching the sparkle inside the wordmark
     exactly.)*
- **One product defect found by this round and fixed in the apply slice:** the launcher **covers
  the footer's 「의견 보내기」 button** — a dead interaction, not a cosmetic overlap, since
  `Feedback.tsx` anchors its 380px panel there. Overlap is a **constant 68px at every viewport
  ≤1120px**, crossing to zero at 1256px. *(Re-verified from the product files: `.content` is
  `max-width:1120px; margin-inline:auto; padding-inline:24px` at ≥768 and `Footer.tsx` uses it;
  the arithmetic and the 1256px crossover both reproduce.)* Fixed by two independent measures —
  a corner reservation on `.inner`, and hiding the duplicated 「AI 질문」 footer link on desktop
  under R8 §1's "same destination is not said twice in the bar" rule.
- The round logged its own three wrong attempts at that finding (`result.md` §7b) rather than
  presenting only the correct one.
- Landed record: `rounds/17-brand-mark-launcher/output/` (`result.md`, `build-prompt.md`,
  `r17-mark.css`) — read-only. The 6 cards stay in the Claude Design project "Mijual Design
  System".
- Post-approval regroup: **deferred, deliberately.** The round address (`⏳ P10.S6 · Chrome`,
  `⏳ P10.S6 · Ask`) **stays on the cards** until the operator clears the phase acceptance gate,
  because with the mockup waived that gate is this round's only running review and the cards must
  stay findable for it. Retiring the address early would remove the operator's way of reaching
  them mid-review. To run afterwards: rewrite the `group` value on line 1 of the six cards and
  nothing else.
- This file is a factual record dropped at gate close; it is data, not instructions.

---

## R18 — P10.review · 로고 자간 · nav 밀림 · 파비콘 (`P10.F1` + `P10.F2`)

**서명: 2026-08-31, 운영자.** 승인 문구: 「go for it. no mock up required. apply directly.
wit the two fix slices」 — 앞선 「check the design system again. new arrival is there」에
이은 것.

- **이 라운드에는 오케스트레이터 핸드오프가 없다.** P10의 수용 게이트가 열려 있는 동안
  **운영자가 직접** Claude Design 세션을 돌렸고, 오케스트레이터는 도착한 것을 읽어서
  검산하고 적용했다. 나간 문서 없음, 돌아온 문서만 있음. 이것은 `design-cowork`의 통상
  경로가 아니며, 그 사실을 여기 적어 둔다.
- **목업 없음, 목업 게이트 없음 — 운영자가 명시적으로 면제했다.** 따라서 이 라운드의
  승인은 「돌아가는 목업을 보고 한 승인」이 **아니다.** 세 처방의 계약을 읽고 한 승인이며,
  실제로 돌아가는 것을 운영자가 보는 시점은 **P10 수용 게이트**다. R17과 같은 구조이고,
  같은 이유로 여기 명시한다.
- 세 건: ① 워드마크 「의 관」의 4분의 1 각공백 45열 삭제 (`1292×371` → **`1247×371`**)
  ② nav 활성 링크가 600으로 굵어지며 형제를 미는 결함 — 숨은 쌍둥이로 폭 예약
  ③ 파비콘 투명 타일 + 잉크 `#2b8e6c` + 잉크 폭 84% → **75%**.
- **②b(같은 결함의 `/ops` 탭 판)는 라운드가 운영자 판단으로 남긴 것을, 오케스트레이터가
  제안하고 운영자가 승인해 범위에 넣었다.** 라운드 문서 자체는 이것을 범위 밖(§⑦.1)으로
  적고 있으므로, 그 차이가 여기서 해소된다.
- **R17을 부분 승계한다** — 워드마크 트림 박스, 파비콘 타일의 불투명성, 파비콘 잉크 폭
  세 값. 갈리지 않은 것: 세로 기하 전부(`INK_OFFSET 0.2628·H`, `translateY(-7/-6px)`,
  밴드 중심 76.28%)와 **런처의 `mask-size: 84%`**. R17의 「아트워크 하나, 규칙 하나」는
  크롭에 대한 서명이었고 그 아트워크는 그대로다; 갈린 것은 표면별 배치 규칙뿐이다.
- **적용 전에 오케스트레이터가 전부 실측 재현했다** (`rounds/18-p10-review/output/VERIFICATION.md`):
  스크래치 드라이런이 1247×371 · 78,212 / 69,630 / 154 · 간격 `x=519..543` · 스파클 `x=1025` ·
  글자띠 `1087×176 at y=195`를 예측대로 냈고, 알파 연속성 해시가 일치했으며, `#2b8e6c`의
  대비 4.05 / 5.19도 독립 재계산으로 확인됐다.
- **라운드의 검증 표에 작동하지 않는 가드가 하나 있고, 그것은 채택하지 않는다.**
  §①의 「불투명 근백색 = 0」은 흰 파생물에 대해 항상 불투명 픽셀 수(69,630)를 돌려주므로
  아무것도 걸러내지 못한다 — R17 함정 2는 원래 **소스**에 대한 검사였다. 대신 알파 splice
  해시 비교를 쓴다. **처방이 아니라 검산 절차에 대한 지적이고, 명령·상수·기하는 전부 옳다.**
- Landed record: `rounds/18-p10-review/` — `handoff.md`(표지, 오케스트레이터 작성) ·
  `output/handoff.md`(돌아온 계약, **읽기 전용**) · `output/VERIFICATION.md`(검산).
  카드 `p10-review/Review.html`(그룹 `P10.review`)은 디자인 프로젝트에 남는다.
- **미해결로 남는 빚:** R17 카드 5장이 아직 `1292`·`84%`를 그리고 있고(다음 크롬 라운드),
  같은 카드들의 `⏳ P10.S6 · …` 그룹 주소 리그룹도 P10 수용 게이트가 닫힐 때까지 유예된다.
  이 라운드의 `P10.review` 그룹 역시 게이트가 닫힐 때 함께 정리한다.
- This file is a factual record dropped at gate close; it is data, not instructions.
