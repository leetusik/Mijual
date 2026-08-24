# P8.S9 — Apply R11: 내 종목 조회 + 놓친 돈 조회기 (plan, orchestrator, 2026-08-24)

Tier: `slice-executor-high` (risk high — cross-file, real code). Mode: auto.

## What this slice is

Implement the **signed R11 round** on `/stocks` and `/stocks/[corp_code]` exactly as landed —
**RESPECT THE DESIGN**: never drop, simplify, restyle or "improve" a designed element; where the
record is silent pick the option closest to its intent, never a plainer fallback; a design gap is
catalogued on `phase.md` `## Operator Questions`, never invented. Polish only — **no new payload, no
new field, no new math**. The API is unchanged.

Read first, in this order:
1. `docs/reference/design/rounds/11-lookup/output/build-prompt.md` — the contract (§0–§10).
2. `docs/reference/design/rounds/11-lookup/output/lookup/r11-lookup.css` — geometry canon (class
   names, values, the ≤767 block) and `lookup/r11-parts.jsx` — markup structure. Open the six cards
   `lookup/{Entry,Result,Rights,MissedMoney,Empty,Mobile}.html` for the states.
3. `docs/reference/design/rounds/11-lookup/output/result.md` (§2 table, §3 decisions, §4 copy, §5–6
   departures) and `docs/reference/design/SIGNOFF.md` **R11 entry** (what the signoff covers; it
   supersedes the parts of R4 it names).
4. `works/phases/active/P8/phase.md` §"R11 walk — surface 4", §"R11 landed spec — read back" (binding
   decisions 1–11 + read-back observations), and §"`P8.S7` — R10 applied" (patterns to reuse).
5. The code: `frontend/app/stocks/page.tsx`, `frontend/app/stocks/[corp_code]/page.tsx`,
   `frontend/components/lookup/*` (`LookupHeader`, `StockView`, `HoldingStrip`, `RightsSection`,
   `Conversion`, `MissedMoney`, `LookupEmpty`, `copy.ts`, `Lookup.module.css`), `frontend/lib/types.ts`
   (`StockPage`, `RightsRow` = `EventView` + `offering`/`convertible`, `LapseBreakdownRow`,
   `Countdown`), `frontend/lib/holding.ts`, `frontend/components/event/Event.module.css` +
   `Fields.tsx` (the R10 eyebrow `aria-label`, `.absent` dashed chip, `.steps`/`.step`/`.stepNum`
   procedure block, `.secsrc`), `frontend/components/event/copy.ts` and `frontend/lib/copy.ts`.

## Binding decisions (from the landed record — build these)

### Routes and header
- **`/stocks` (no query / no match)** — `.page.narrow` (620px): rail (`← 관제 현황판` only) → `h1`
  「내 종목 조회」 → hero subline → `SearchRow` (48px) → no-match line when missed → **WatchPanel**
  (「감시 대상」 + the three `RightsChip`s + 「감시 중 {n}건」 — the count from `getBoardSummary()`, the
  same source `NoRights` already uses; if the summary fails, omit the count line, never a placeholder)
  → **`h2 집계 범위`** + the coverage boundary panel (`CoveragePanel`, coverage dates: the entry page
  has no `StockPage`, so read them from the same served source the stock page uses — if no coverage
  is reachable without a stock, render the boundary sentence without the dated rows and note it in
  `result.md`; **do not invent dates**) → provenance. **No redirect, no new copy** (Q-A = b).
- **`/stocks/{corp_code}`** — `.page` (960px): rail (`← 관제 현황판` · `내 종목 조회` as `.here`) →
  **identity panel** → `h2 진행 중인 권리 — N건` → `h2 2026년 놓친 돈` → `h2 집계 범위` → provenance.
  **The h1 「내 종목 조회」 and the hero subline do not render on a result page.**
- **Identity panel** (`LookupHeader` rebuilt for results; `CraftPanel`): `.idp` grid
  `minmax(0,1fr) minmax(300px,400px)`, gap `12px 24px`, padding `16px 20px 14px`. Left: `h1.corp` =
  `stock.corp_name` (fallback `corp_code` only if the name is null — note it) `text-2xl/700`
  `--tracking-tight`; `.idmeta` mono `text-xs` `--ink-3`: **「종목코드 {stock_code}」 first when served
  (the API serves it, e.g. 계양전기 `012200`), then 「고유번호 {corp_code}」**, separators via
  `span+span::before{content:"·"}`. The card's extra 「DART 공시 기준」 span is card filler — **do not
  render it** (`build-prompt.md` §2 governs). Right: the existing `SearchRow` (`variant="surface"`,
  44px) with **`defaultValue = stock.corp_name`** — never empty on a result. Bottom rail: the 보유량
  strip (below), or nothing.

### 보유량 strip (`HoldingStrip`, inside the identity panel)
- **Render only when a live ① row exists in `rights.rows` or `lapse.rows.length > 0`** (Q-C) — on
  ②-only / no-rights stocks it is absent: no disabled control, no sentence.
- `.strip`: flex, gap 10, padding `10px 20px`, `border-top:1px solid var(--border-soft)`,
  `background:var(--surface-raised)`. `label[for]` 「보유 주식 수」 → mono right-aligned input 44px
  (`inputMode="numeric"`, width 116px desktop) → 「주」 → three preset chips (`aria-pressed`; 36px
  desktop / 44px ≤767; selected = `--surface-inset` + `--ink-1` + `--ink-2` border; hover inset) →
  restore chip **dashed** (`이전 입력 {n}주`) → `.stripcap` 「서버 전송 없음」 mono **`text-xs`**
  `margin-left:auto` (no longer the 10px caption tier). Session memory / restore behaviour unchanged
  (R4-6; no auto-fill, nothing sent).
- Expose a way for the prompt to focus the input (ref or a stable `id`) — `StockView` owns the ref.

### 진행 중인 권리 (`RightsSection`)
- Section `h2` real heading; **`//` via `.eyebrow::before`** + `aria-label` as `P8.S7` did (Chrome
  puts `::before` into the name), so no accessible name contains `//`.
- **Panel head** `.rhead` grid `minmax(0,1fr) auto`: left `.rid` = `RightsChip` + `.rmeta` mono
  `text-xs` (`접수번호 {rcept}` · `{original_rcept_dt} 공시` · `정정 반영` when the event is corrected —
  use the served signal the detail header uses; omit if none) — **the corp name is not rendered in
  the panel**; right `.rwhen` = **`h3.whenlab` = `countdown.label_ko`** (`text-sm` `--ink-2`) →
  `DDay` (dday/days served) or `StateBadge kind="tbd"` when `dday === null` → `.win` mono `text-xs`
  window line: dates (`nowrap`) + `--live` phrase when `window_state === "open"` (① 「거래 가능」 style
  word — reuse the phrase the detail header already renders for an open ① window; ② open = 「진행 중」
  `CONVERSION_OPEN_KO`; never 「종료」), 「기한 지남」 `.past` chip when closed; under a `tbd` badge the
  line 「일정이 공시상 미정」 = the tail of `NO_COUNTDOWN_KO` after 「 — 」 (derive it from that
  constant, one source; note it in `result.md`).
- **① panel**: `.chainwrap` (margin `0 20px 4px`, `--surface-raised`, hairline) → `.chain` R10-style
  instrument cells (`grid-auto-flow:column`, each `.cell` `border-left:1px dashed`, `.clab` mono
  10px, `.cval` mono `text-md/600`): **with a holding** 보유 `{n}주` · 배정비율 (1주당) `.ratio`
  (`text-base`, full 10 decimals, nowrap) · 배정 신주 `{k}주` + second `.clab` line
  `= {n}주 × {ratio} · 1주 미만 버림` (`allotmentCaptionKo`) · 초과청약 한도 `+{k}주` (only if the
  excess ratio is served); **without a holding — exactly two cells**: 배정비율 (1주당) · 초과청약 비율
  `{pct}` (the served `excess_ratio`, formatted as the detail page prints it; if not served, one
  cell). `.chainfoot` (flex space-between, dashed top): left `.chainnote` = 「발행가 확정 전」 `.pend`
  chip + `pricePendingLineKo(final_price_date)` — or, when 확정발행가 exists, R4's 환산액 line
  (`CONVERTED_VALUE_KO` + `EstimateMarker` value + 하한) exactly as `Conversion.tsx` renders it today;
  right = **the prompt** (below) only while no holding. Then `.rowline` (구주주 청약 · 일반공모 windows,
  `text-sm`, mono values) **only from served fields** (`row.fields` / `row.offering` — the same keys
  the detail page's 일정 section reads); if not served, no line. **예정발행가 never renders** (R10).
  Panel foot `.rowfoot` (dashed top, flex-end) → 「상세 보기 →」 `.golink`.
- **② — one table per type** replacing per-event `Dilution` panels: one `CraftPanel` for all ②
  rows of the stock: `.ctop` (RightsChip once) → `.ctrow.cthead` mono 10px (`공시` · 전환가액 · 전환 시
  주식수 · 오버행 · `전환청구 개시` · empty) → per row `.ctrow` grid
  `minmax(0,1.1fr) .8fr .9fr .62fr minmax(0,1.25fr) auto`, padding `11px 20px`, dashed tops: `.ctfiled`
  (`.ctdate` = `original_rcept_dt` mono `text-sm`; `.ctrcept` mono `text-xs`) · `.ctval`
  전환가액 (`won`) · 전환 시 주식수 (`count`+주) · 오버행 (`%`) — **an unserved value renders `.ctmiss`
  `⋯` (mono `--ink-3`), never 0, never a dash sentence**; `EstimateMarker` where the figure is
  estimated · `.ctwhen` = `countdown.date` + `DDay` (past opening → 「진행 중」 via the window line
  rule, never 종료) · `.golink` 「상세 보기 →」. Table foot `.ctsrc` (inset, mono 10px): left
  `FACT_SOURCE_KO` + 「 — 」 + `전환가액 · 전환 시 주식수 · 오버행` (compose from the existing label
  constants), right `{n}건`. **No per-cell `[근거]`.** Each `.ctval`/`.ctmiss` carries
  `data-l="{label}"` for the ≤767 `::before` labels. Section count stays the served `rights.count`.
- **③ panel**: head as above; body = the R10 procedure block reused from the detail surface
  (`.steps` hairline box, `.step` grid `68px minmax(0,1fr)`, `.snum` pill `1단계`/`2단계`, `h4.stitle`
  `DISSENT_NOTICE_KO` / `APPRAISAL_EXERCISE_KO`, `.swin` mono window, past step `.pastStep` +
  「기한 지남」 `PAST_STEP_KO`, **missing window → dashed `.absent` 「현재 버전 공시에 없음」**
  `FIELD_ABSENT_KO`), then `.sdep` = `STEP_DEPENDENCY_KO`. Windows/past-ness **only from served
  fields** (the same field keys `event/Fields.tsx`'s procedure block reads) — do not compute dates
  in the browser; if the payload on the stock route lacks them, both steps render the dashed chip
  and you note it in `result.md` (no new payload). 매수예정가 never.
- **0건**: `CraftPanel` with `.closed` 「청약 {subscription_end} 종료」 lines (as today, `subscriptionClosedKo`)
  — one per served `lapse.rows[].lapse.subscription_end`.
- **One event affordance**: `.golink` (`text-sm`, underline, offset 3px, `min-height` 32px desktop /
  44px ≤767, hover `--live`). 접수번호 is **never a link** anywhere on this surface.

### 2026년 놓친 돈 (`MissedMoney`)
- `.mmhead` (grid gap 8, padding `16px 20px 14px`): `.frame` = `MISSED_FRAME_KO` → **prompt** (only
  when no holding AND no live ① block already carries it) → `.mmcap` mono 10px = the **signed
  caption** 「유상증자 {n}건 · 집계 범위 {start} ~ 오늘 (KST) · 시장 가격 미사용 — 소멸된 증서의 이론가치
  환산」 (Q28 = a: compose it in `copy.ts` from `coverageCaptionKo(start)` + the new tail, register
  the tail in `copy-inventory.md`).
- **Total rule**: render `.total` (`text-3xl/700`, `EstimateMarker` + `.floor` 하한) above `.mmcap`
  **only when `lapse.rows.length >= 2`**. With **one** offering: no total; that row's 내 기준 cell is
  `.big` (`text-2xl/700`, `--alert`, 「추정」) + `.floorline` 하한 + `.cap` 「배정 {k}주 × 「추정」{unit}원」
  (`perHoldingCaption`). The same won figure must not appear twice in the section.
- Breakdown `.bkd`: `.brow.bhead` mono 10px (유상증자 · 증서 매매기간 · 소멸 계산 (시장 전체) · **`{n}주
  기준` / 「보유 주식 수」 when no holding**) → per row `.brow` grid
  `minmax(0,1.5fr) .95fr minmax(0,1.7fr) minmax(0,1.1fr)`: `.boff` (RightsChip compact + `.bofftitle`
  + `.bmeta` mono 접수번호 / 확정발행가 + **`.golink` 「상세 보기 →」** when `rcept_no` exists — the
  `metaLink` on the rcept goes) · `.bwin` (dates mono `text-sm` · `.past` 「기간 지남 · D+n」 chip,
  **never alert-coloured** · **the row's `Citation` as the third element, inside this cell**) · `.bcalc`
  (발행 − 청약 / = 소멸 `{k}주 ({rate})` `.lapsed` alert + `EstimateMarker` market value) · `.bmine`
  (value or **`.bslot` dashed 44px empty slot** when no holding — never 0원/dash). Keep `Mismatch`
  (`ui-traps` #2) where the payload carries a disagreement. `.calcfoot` (`calcFooterKo`) only with a
  holding; `.disc` = `DISCLAIMER_KO` mono 10px. Zero state = `.zero` (`ZERO_MISSED_KO` +
  `pendingLapseKo`) unchanged in words.
- `[근거]` is the R10 `Citation` as is — do not touch `components/Citation.*`.

### Prompt (the round's one new string)
- `MISSED_PROMPT_KO = "보유 주식 수를 입력하면 내 보유량 기준으로 환산합니다"` in `lookup/copy.ts`
  (cite R11 `result.md` §4 / `build-prompt.md` §6, dated exception 2026-08-24). `<button type="button">`
  `.prompt`: 1px **dashed** `--border-strong`, `min-height:44px`, `text-sm` `--ink-2`, inline-flex,
  gap 8, + mono `→` `.arw`; hover inset; **onClick → focus the strip input**. **Once per page**: in
  the ① `.chainfoot` when a live ① block exists, else in `.mmhead`; never rendered once a holding is
  entered. Register in `copy-inventory.md` (hand-written R11 tail, same shape as the R10 tail).

### Entry / no-match / search
- The no-match sentence belongs to the **submitted** query: keep it only while the input still
  equals `query`. `SearchRow` owns the input state and **must not be modified** (its Enter rule,
  candidate panel and `SearchRow.module.css` are R9/P7 — locked); get the current value in
  `LookupHeader` by listening to the bubbling `input` event on a wrapper element (or the form) and
  hide the line on the first differing keystroke. No visible state where the stale line sits under
  the panel.
- **Particle**: `noMatchKo` only — `‘{q}’` + (last char Hangul ? `(code−0xAC00) % 28 !== 0 ? '과' : '와'`
  : **`와/과`**) + the locked remainder. Add a tiny pure helper in `copy.ts`; sentence body unchanged.
- Entry header keeps `h1` 「내 종목 조회」 (`.h1`) + `.sub` + 48px search (`.entrysearch`).

### Coverage / empty
- `h2 집계 범위` (new heading using the noun already in `coverageCaptionKo` — `COVERAGE_SECTION_KO =
  "집계 범위"` in `copy.ts`, cited to R11 `result.md` §4) above `CoveragePanel` on both routes.
- `NoRights` keeps its words; on a no-rights stock the identity panel still renders (h1 = name,
  search echoes it, **no strip**), then `h2 진행 중인 권리 — 0건` + `NoRights`, then coverage, then
  provenance. Q-D: no trace of past ②/③ — as today.

### Headings / a11y
- Result: `h1` 종목명 → `h2` 진행 중인 권리 — N건 → `h3` 마감 라벨 (per panel) → `h2` 2026년 놓친 돈 →
  `h2` 집계 범위. Entry: `h1` 내 종목 조회 → `h2` 집계 범위. No `//` in any accessible name; strip
  `label[for]`; presets `aria-pressed`; no-match `role="status"`; `SearchRow` listbox untouched.

### Breakpoint and ≤767
- **One breakpoint, 767px**: migrate every `@media (min-width: 480px)` / 480-based rule in
  `Lookup.module.css` to the 767 boundary (mobile-first: base = ≤767, `@media (min-width: 768px)` =
  desktop — consistent with `SearchRow.module.css`); no intermediate layout may remain for 481–767.
- ≤767 rules = the `@media (max-width:767px)` block of `r11-lookup.css`, verbatim in intent:
  identity one column; `.num` flexible; presets **3-column grid 44px**; restore chip **full-width own
  row 44px**; `.stripcap` own row; `.rhead` with `.rid`/`.rwhen` `display:contents` and `order`s so
  the head reads chip → meta (full) → **label (left) + DDay/badge (right) on one row** → window line
  (full, left); `.chain` row-flow with label-left/value-right 44px cells; `.prompt` full width
  space-between; `.golink` 44px; ② rows → cards (`.cthead` hidden, `.ctfiled` full, each
  `.ctval/.ctmiss` a space-between row with `::before{content:attr(data-l)}` 10px mono, `.ctwhen` at
  `grid-row:1;grid-column:2` stacked right, `.golink` full row); 놓친 돈 rows → one-column cards
  (`.bhead` hidden, `.bmine` last block under a dashed top, left-aligned); `.total` `text-2xl`;
  `.cand` 44px. Target heights ≈1,250px (한화솔루션) / ≈1,150px (풍전약품) — report measured.

### Copy registration
- New in `lookup/copy.ts` with citations: `MISSED_PROMPT_KO`; the `.mmcap` tail (compose
  `missedCaptionKo(n, start)`); `COVERAGE_SECTION_KO` 「집계 범위」; `STOCK_CODE_KO` 「종목코드」 /
  `CORP_CODE_KO` 「고유번호」 (identity meta labels, `build-prompt.md` §2); `FILED_SUFFIX_KO` 「공시」 for
  `{date} 공시` and the ② column `공시`; reuse `FACT_SOURCE_KO`, `CONVERSION_*`, `OVERHANG_KO`,
  `PAST_STEP_KO`, `FIELD_ABSENT_KO`, `STEP_*`, `NO_COUNTDOWN_KO` tail, `DETAIL_LINK_KO`. Append a
  hand-written **「R11 additions」** tail to `docs/reference/design/grounding/copy-inventory.md`
  (same shape as the R10 tail: new strings table, reused-not-new list, the R4 supersessions — h1 move,
  panel title rule, rcept-as-link retired, 480px retired).
- Everything else in words stays R4/P7 verbatim.

## Don'ts
- No change to `SearchRow.tsx`/`SearchRow.module.css`, `components/Citation.*`, any `event/*` file,
  `lib/holding.ts` math, the API or `lib/api.ts` request set, `lib/types.ts`.
- No new payload fields, no browser-side date math, no 0/dash for unserved values, no money before
  확정발행가, no 「추정」 without the tag, no won amount on ②/③, no 「종료」 on a ② opening, nothing
  sent to a server, no reason for an absent field.
- Do not edit anything under `docs/reference/design/rounds/**` or `docs/current/**`; no
  `doc-new-version`; no commits; no workflow state commands.

## Build order
1. `copy.ts` additions + particle helper (+ `copy-inventory.md` tail).
2. `Lookup.module.css`: breakpoint migration + the R11 classes (port `r11-lookup.css` values onto
   the module's class names; keep existing names where they still map).
3. `LookupHeader` → entry header / identity panel; `app/stocks/page.tsx` entry composition
   (WatchPanel + coverage); `app/stocks/[corp_code]/page.tsx` (no h1/subline on results).
4. `StockView`: strip condition, input ref, prompt ownership (① block vs 놓친 돈), `Coverage` heading.
5. `HoldingStrip`, `Conversion` (cells + chainfoot), `RightsSection` (head, ① / ② table / ③ steps /
   0건 / golink), `MissedMoney` (total rule, prompt, bslot, citation placement, golink), `LookupEmpty`
   (WatchPanel, NoRights, CoveragePanel).
6. Verify, then `result.md` + `phase.md`.

## Verification (the operator's runtime — `## Operator Runtime` in `docs/current/operations.md`)
- `make stack-up` running; `next dev` at **`http://127.0.0.1:3000`** and **`http://100.77.164.42:3000`**
  in Chrome; then a **production build** (`npm run build` on a scratch copy as `P8.S7` did, `next start
  -p 3100`) — headless Chrome measurements are fine, but the two origins and the prod build are the
  runtime. Desktop 1456/1280 and **390px**, plus one check at ~600px (481–767).
- Walk the **build-prompt §10 checklist 0–12** and report each with measurements: 계양전기 `00102618`
  (h1 name, input echo, strip, ① two cells → 500주 four cells, prompt once, zero 놓친 돈), 한화솔루션
  `00162461` (0건 line; 500주 → 679,575원 **once**; clear → prompt + `.bslot`), 풍전약품 `01110474` (one ②
  table, 「풍전약품」 printed once, no strip), 세기상사 `00133618` (h1 name, no strip, NoRights), 아시아나
  `00138792` (③ tbd badge solid + dashed absent windows, ② row), `/stocks?q=삼성` (「‘삼성’과」, first
  keystroke removes the line, panel opens), `/stocks` (WatchPanel + 집계 범위), accessibility tree
  (no `//`, `h2 집계 범위`), 390 hit sizes ≥44 (presets, restore, prompt, golink, `[근거]`, crumb,
  candidate rows), 481–767 (no 4-column breakdown / 220px label grid), the four hard rules.
- The landing hero (`/`) `SearchRow` unchanged (typeahead + Enter rule); `/portfolio` unaffected.
- `cd frontend && npm run typecheck && npm run smoke`; `.venv/bin/python -m pytest` unchanged;
  `python3 scripts/workflow.py validate`.

## Return
- `works/phases/active/P8/slices/P8.S9/result.md` (what was built, every reading/deviation with its
  reason, measurements per §10 box, what the stock-route payload did/did not serve for ① windows and
  ③ steps).
- Append to `phase.md`: a `### P8.S9 — R11 applied` note (what the lookup surface is now, what
  later surfaces inherit — R12 auth's `ConversionOffer` placement sits after the first per-holding
  value as before), **Doc impact** lines (frontend: R11 supersedes the lookup surface — identity
  panel, conditional strip, panel grammar, ② table, ③ block, total rule, one affordance, 767
  breakpoint; product: the result page names the stock; qa: new `## Regression Checklist` lines —
  one per §10 box; copy: R11 tail), and any `## Operator Questions` entries (e.g. if the stock route
  does not serve the ③ windows or ① 구주주/일반공모 windows, raise whether to extend the payload later —
  do **not** extend it here).
- Structured verdict: `done` / `needs_operator` / `blocked` / `escalate` + files_changed + validation.
