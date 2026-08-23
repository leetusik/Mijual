# Design Handoff — Round 11: Polish — 내 종목 조회 + 놓친 돈 조회기

- Round: **R11** (P8 polish pass, surface 4 of 8) · slice `P8.S8` · written 2026-08-24
- Status: OUT — awaiting the design session (Claude Design + operator)
- Repo: `leetusik/Mijual` via Connect GitHub (main branch, pushed at handoff commit)
- Builds on: **R4 (내 종목 조회 — search + 보유량 환산 + 놓친 돈, `rounds/04-lookup/`), R3 (the
  ①②③ vocabulary and labels this page re-exports), R5-2 (`ConversionOffer` "값 계산 직후" —
  auth's, placement only here), R8 (chrome), R9 (the hero `SearchRow` + P7 candidate panel —
  one shared component with this page), R10 (the `[근거]` re-cut + citation density rule —
  applies here as-is)** as signed, plus the P7 operator overrides in
  `docs/reference/design/SIGNOFF.md` (candidate panel = the reader chooses a 종목; 보유량 caption
  trimmed to 「서버 전송 없음」). Those rounds are **locked context** except where this handoff
  explicitly opens them; R11 is a **polish round — no new features** — and, per `SIGNOFF.md`
  precedence, what R11 signs supersedes the parts of R4 it touches.

## 1. Product context

`/stocks` (entry / 검색 불일치) and `/stocks/{corp_code}` (a resolved stock). The page as built:
crumb 「← 관제 현황판」 → h1 「내 종목 조회」 → hero subline → `SearchRow` (input + 조회, P7
candidate panel) → on a resolved stock: the 보유량 strip (craft panel: 「보유 주식 수」 · mono
integer input · 주 · 100/500/1,000주 preset chips · 「이전 입력 {n}주」 restore chip · 「서버 전송
없음」) → `// 진행 중인 권리 — N건` (one craft panel per live event: RightsChip · corp name ·
접수번호 · right: governing label + DDay + window line; ① adds 발행가 확정 전 chip / 배정비율 or
배정 신주 + 초과청약 한도 + caption / 환산액 when priced; ② adds 오버행 · 전환 시 주식수 · 전환가액;
③ adds the 2단계 dependency line; 「상세 보기 →」) → `// 2026년 놓친 돈` (zero state + pending line
+ coverage caption, or the conditional frame + 「추정」 total + 하한 + the 4-column breakdown
유상증자 / 증서 매매기간 / 소멸 계산 / N주 기준 + calc footer + disclaimer) → coverage boundary
panel (유증 2026-01-01부터 · CB 2025-06-01부터 + sentence) → mono provenance line. A stock with
nothing: the NoRights card (감시 대상 3종 + 감시 중 488건) + the boundary panel. No match:
「‘{q}’와 일치하는 종목이 없습니다 — …」 under the input.

The orchestrator walked the surface on 2026-08-24 in the operator's runtime (127.0.0.1:3000,
Chrome desktop 1456px + 390px; pages: `/stocks` · `/stocks?q=삼성` (no match, then typing 「계양」
for the candidate panel) · 계양전기 `00102618` (① live D-1, 발행가 확정 전, zero 놓친 돈, with and
without 500주) · 한화솔루션 `00162461` (0건 + 「청약 2026-07-23 종료」, 놓친 돈 679,575원 on 500주,
the 「이전 입력 500주」 chip) · 풍전약품 `01110474` (three ② panels) · 세기상사 `00133618` (NoRights —
its ③ windows have passed) · 아시아나항공 `00138792` (② + ③ with `dday: null` — read from the
API while the dev server was mid-rebuild). Findings below; the full list will also be recorded
in `works/phases/active/P8/phase.md` §"R11 walk — surface 4" when the running apply slice
returns. The operator's gate answers are **direction** (what to fix) and **REFERENCE — data, not a
proposal** for how. Claude Design + the operator decide how it looks.

## 2. Scope checklist — what this round must cover

Default from the P8 rhythm (as at R9/R10): **every walk finding → fix, Claude Design decides
how**, except where §2b names an operator decision. Walk findings (desktop + 390):

- [ ] **1 · The resolved stock is never named.** `/stocks/{corp_code}` renders the header with
      an **empty** search input and no stock line; 종목명/종목코드 appear only inside the event
      panels' titles. On 세기상사 (no rights) the company name is **nowhere on the page** — a
      first-time user cannot confirm what they are looking at. Give the result a stock identity
      (name · 종목코드, whatever the session decides; the input may also echo it).
- [ ] **2 · Header weight above every result** — crumb + h1 「내 종목 조회」 + the hero subline
      + search row repeat on every stock page; at 390 the result starts ~215px down, on desktop
      ~235px. Decide what the page-level header is once a stock is resolved (the title/subline
      copy is R4-locked; its presence/size on a result page is in play).
- [ ] **3 · The 보유량 strip on stocks where it changes nothing** — ②-only 풍전약품 and
      no-rights 세기상사 show the full strip; typing a number produces no visible effect anywhere.
      When and where the strip appears (R4-1 "one page, two sections" stays).
- [ ] **4 · 놓친 돈 before a holding is entered** (한화솔루션): the section opens with only the
      coverage caption and a 3-column breakdown — no headline, no conditional frame, nothing says
      「보유 주식 수를 넣으면 …」. After 500주: the 679,575원 headline **and** the same 679,575원 in
      the 500주 기준 column (single-offering stock) — the number appears twice. Design the two
      states (no holding / holding) and the single-offering case.
- [ ] **5 · The breakdown row has no labelled route to the event page** — only the mono
      접수번호 (a link nobody reads as one) and `[근거]`; the 진행 중 panels carry 「상세 보기 →」.
      One affordance rule for "open this event" on both sections.
- [ ] **6 · Every panel's title is the corp name, on a page that is already one corp** — 풍전약품
      shows three panels titled 「풍전약품」 ×3, distinguishable only by rcept and dates. What a
      panel's title carries on a single-stock page (R4 §4 "RightsChip + 종목/건 title" is in play).
- [ ] **7 · ② panels** — 오버행 / 전환 시 주식수 / 전환가액 as three bare facts, a half-empty right
      column (D-day + window), ~170px each; three of them = 600px of near-identical panels.
      The ② row's reading for a holder who has nothing to exercise (R4-4: context, never money).
- [ ] **8 · ③ row drawn for the first time** — R4 specified ②/③ rows but drew none ("pin a
      sample"); 아시아나항공 `20260713000482` is the sample now: 반대의사 통지 마감 with `dday:
      null` (→ StateBadge 추후결정 in the D-day slot) + the 2단계 dependency line. Draw it, in
      both the live (세기상사-shaped, dated) and the dateless form.
- [ ] **9 · Candidate panel on this page** — opaque and correct, but it fades in **over the stale
      검색 불일치 sentence** (the no-match line for the previous query stays under the panel while
      candidates for the new one are shown) and over the provenance line. Decide what the
      no-match line does once the reader types again.
- [ ] **10 · 검색 불일치 particle** — 「‘삼성’와 일치하는」 → 와/과 by the final consonant (R9 walk
      11, routed here). Copy mechanics of a signed sentence, not new copy.
- [ ] **11 · Empty `/stocks` (no query)** — crumb, title, subline, search, provenance line and a
      void. (§2b Q-A.)
- [ ] **12 · Heading semantics** — the `// ` eyebrow is inside the h2's accessible name (R10
      moved it to `::before` on the detail page — same fix here); the 보유량 strip and the
      coverage boundary panel have no heading. Outline today: h1 내 종목 조회 → h2 // 진행 중인
      권리 → h2 // 2026년 놓친 돈.
- [ ] **13 · Breakpoints** — `Lookup.module.css` switches at **480px** (R4 §Mobile "≤480px") while
      `SearchRow` and R9/R10 settled on the single **767px** boundary; between 481 and 767 the page
      is desktop-laid (4-column breakdown, 220px label grid) on a ~600px screen. One breakpoint
      rule for the surface (R10 §0 common rules are the reference).
- [ ] **14 · 390 stack** — measured: chips 87/101×44, input 260×44, search 238×48 + 조회 88×48,
      「상세 보기 →」 292×44, crumb 74×44, `[근거]` 48×44 (post-R10) — the 44px floor is met. The
      「이전 입력 500주」 chip wraps to its own full-width row; a breakdown row as label/value lines
      runs ~600px per offering; the 한화솔루션 page is 1,723px, 풍전약품 2,075px. Confirm or tighten
      the mobile composition (R4 `lookup/LookupMobile.html` is the base).
- [ ] **15 · Desktop rhythm** — the ① panel with no holding leaves the 배정비율 line hanging alone
      under the chip; chip selected state (live text + border) vs the dashed restore chip — two
      chip grammars in one row; 「서버 전송 없음」 as a 10px caption under the chips. Confirm.
- [ ] **Cards refreshed for everything above, desktop (1512/1280) and 390px mobile.**

### 2b. Operator decisions (take at the gate or in the session — each is R4-deliberate today)

- **Q-A · Empty `/stocks`.** With no query it is title + search + provenance and nothing else.
  Options: (a) keep a bare entry page, (b) give it the already-signed context (감시 대상 3종 ·
  감시 중 count · coverage boundary panel — no new copy), (c) redirect to the landing hero.
  Orchestrator's default: **(b)** — the hero already is the entry; this page should at least say
  what it looks up.
- **Q-B · Stock identity on a result** (finding 1). Default: **yes — name + 종목코드 at the top
  of the result**; the session decides the form. (R4's card showed the query in the input; the
  build cleared it on the resolved route.)
- **Q-C · 보유량 strip on non-① stocks** (finding 3). Default: **the session decides** — hide,
  demote, or keep with a factual line; if a sentence is needed it is this round's dated copy
  exception.
- **Q-D · A past ②/③ on a stock leaves no trace** — 세기상사 had a 주식매수청구권 event in 2026
  whose windows passed; the page is the NoRights card (「이 종목에는 진행 중이거나 2026년에 소멸된
  권리가 없습니다」) because 놓친 돈 is ①-only by rule (R4-4) and a ③ is never money. Keep the
  rule (status quo) or add a factual closed line the way ① leaves 「청약 {date} 종료」. Default:
  **keep the rule; log as decided** — a reader who searches 세기상사 today is told the truth.
- **Q-E · 놓친 돈 with no holding** (finding 4). Default: **layout only** — the session decides
  whether a prompt sentence is needed at all; if one is, dated exception.

**Explicitly NOT in this round:** `SearchRow`'s Enter rule and candidate panel design (R9/P7 —
one shared component; this page only decides what happens *around* it); the `ConversionOffer`
(R5-2 / auth, R12 — placement "값 계산 직후" only); the `[근거]` affordance (R10, landing now);
any new field, value or math (no 매수예정가, no ② money, no market prices); the API (`GET
/stocks?q=`, `GET /stocks/{corp_code}`, `GET /stocks/suggest?q=` — unchanged).

Cross-cutting (every round): Korean-only surface; mobile-first; a11y/reduced-motion floor; no new
features.

## 3. Locked vs. in play

**Locked:** R1 tokens/type/spacing/motion/square-hairline system and the `.cosmos` scope; R4's
five decisions (one page two sections · direct input + preset chips, no slider · no 기간 input ·
②/③ rows never money · session memory, browser only, restore chip is an offer); every R4 hard
rule (no estimate without 「추정」, no money before 확정발행가, outside coverage unstated, D-days
upstream KST, a past ② opening never 종료, holding value never sent); R4 + P7 copy as signed (incl.
「서버 전송 없음」); R3's shared labels; R8 chrome; R9's SearchRow; R10's Citation.

**In play:** everything in §2 — stock identity, the header on a result, the strip's presence
per stock type, 놓친 돈's two states and the single-offering reading, the event-link affordance,
panel titles on a single-stock page, ② and ③ panel reading, the no-match line's behaviour under
the candidate panel, the particle, the empty entry page, heading semantics, the breakpoint, the
390 composition, desktop rhythm. New Korean copy **only** where §2b opens it — **the dated
exception of this round, 2026-08-24** — and every such string must be listed in `result.md` with
its reason. A token change, if any, is a **new `foundations/tokens.css` from the session** — the
repo's copy is re-vendored, never hand-edited.

## 4. Where to look — real paths, real data shapes

- **Page as built:** `frontend/app/stocks/page.tsx` (entry + no-match; `found` → redirect to
  `/stocks/{corp_code}`), `frontend/app/stocks/[corp_code]/page.tsx`,
  `frontend/components/lookup/` — `LookupHeader.tsx` (crumb · h1 · subline · `SearchRow` · no-match
  line), `SearchRow.tsx` + `SearchRow.module.css` (**shared with the landing hero** — R9/P7),
  `StockView.tsx` (one holding, two sections, session memory), `HoldingStrip.tsx`,
  `RightsSection.tsx` (①/②/③ panels), `MissedMoney.tsx` (total, breakdown, calc footer,
  disclaimer), `LookupEmpty.tsx` (NoRights, CoveragePanel), `copy.ts` (every string with its
  citation — read it before proposing any), `Lookup.module.css`. Money: `frontend/lib/holding.ts`.
  Shared primitives `CraftPanel`, `RightsChip`, `DDay`, `StateBadge`, `EstimateMarker`, `Citation`
  in `frontend/components/`.
- **Backend shapes:** `frontend/lib/types.ts` `StockPage` (`stock {corp_code, corp_name,
  stock_code}`, `rights {count, rows[]}` with `rights_type R1|R2|R3`, `countdown {label_ko, date,
  dday, days, window…}`, `lapse {coverage {start, end, convertible_start}, totals, rows[]}`),
  `StockLookup`, `StockSuggestions`; `lib/api.ts` `lookupStock` / `getStock` / suggestions.
- **Landed records:** `docs/reference/design/rounds/04-lookup/output/` (R4 `result.md` +
  `build-prompt.md` — the contract this page was built from; its five cards), `rounds/09-landing-
  board/output/` (SearchRow/candidate panel as signed, 390 rules), `rounds/10-event-detail/
  output/` (`build-prompt.md` §0 common rules — keep-all, nowrap mono, single 767 breakpoint,
  32/44 hits — and `components/Citation`). Overrides: `docs/reference/design/SIGNOFF.md`.
- **Grounding:** `docs/reference/design/grounding/sample-events.md` (계양전기 · 한화솔루션 money
  chain), `copy-inventory.md`, `states-and-trust.md`, `ui-traps.md`.
- **Live samples to read through the API (`GET /stocks?q=`):** 계양전기 `00102618` (① D-1,
  배정비율 0.2314082845, 발행가 확정 전, zero 놓친 돈 + pending line 2026-09-04) · 한화솔루션
  `00162461` (0건 + 「청약 2026-07-23 종료」; lapse row rcept `20260720000067`, 확정발행가 22,100원,
  매매기간 2026-07-06 ~ 07-10 기간 지남 D+45, 소멸 3,734,925주 8.86%, 206.4억원 추정; 500주 →
  배정 123주 × 5,525원 = 679,575원, 하한 545,181원) · 풍전약품 `01110474` (② ×3: `20250905000550`
  D-22 오버행 8.03% · `20250930000508` D-39 4.29% · `20260610000611` D-298 6.79%) · 대동기어
  `00109310` (② single, D-61) · 아시아나항공 `00138792` (② `20251104000252` D-81 + ③
  `20260713000482` dday null) · 세기상사 `00133618` (nothing live, nothing in coverage) · no match:
  삼성전자 / 삼성.

Missing real content → ask for it; do not invent it.

## 5. Required outputs (a round is incomplete without all three)

1. **The card set** — line-1 `@dsCard` markers, review-time group **`⏳ P8.S8 · Lookup`**, one
   card per reviewable unit. Required card paths:
   - `lookup/Entry.html` — empty `/stocks` (Q-A as decided), 검색 불일치 (particle fixed), the
     candidate panel open on this page over whatever sits beneath it; 390
   - `lookup/Result.html` — a resolved stock top to bottom on 계양전기: stock identity, header
     on a result, 보유량 strip (empty · typed · preset selected · restore chip), the ① panel
     without and with a holding, zero 놓친 돈 + pending line, boundary panel, provenance
   - `lookup/Rights.html` — the panel grammar on a single-stock page: ① live, ② (풍전약품 ×3 —
     what tells them apart), ③ dated and dateless (아시아나), 0건 + 「청약 {date} 종료」; the
     event-link affordance
   - `lookup/MissedMoney.html` — 한화솔루션: no holding / 500주 (single-offering reading,
     headline vs row), breakdown row + link affordance + `[근거]` (R10 component as landed),
     calc footer, disclaimer
   - `lookup/Empty.html` — NoRights (세기상사 — with its identity), Q-D as decided, coverage
     boundary
   - `lookup/Mobile.html` — 390 for Entry / Result / Rights / MissedMoney / Empty, on the
     surface's one breakpoint
   - `foundations/tokens.css` — **only if tokens change**

2. **A record of what was designed** — `result.md` (what changed vs R4, every departure, the
   Q-A–E decisions as taken, any copy string added with its reason and citation).

3. **An implementation contract** — `build-prompt.md` (geometry, states, copy table, mobile
   rules, the breakpoint, a regression checklist for the apply slice to verify). If the session
   produces Claude Design's own handoff bundle, that **is** the record and the contract — land
   as-is.

**Definition of done: the cards appear in the Design System pane** under the `⏳ P8.S8 · Lookup`
group, and the record + contract exist.

## 6. Open questions — posed to the session, not answered here

1. What a resolved stock's identity looks like on this page, and what the page header becomes
   once a stock is resolved.
2. Whether the 보유량 strip has a place on a stock with no ① row.
3. How 놓친 돈 reads before a number is typed, and how a single-offering stock avoids printing
   the same won figure twice.
4. What distinguishes three ② panels of one issuer, and what a ③ panel looks like (first time
   drawn).
5. One breakpoint for the surface, and the resulting 481–767 layout.

## 7. Operator setup + definition of done

Same project ("Mijual Design System"), Connect GitHub already in place — pull latest `main` in
the session so it sees this handoff and the landed R1–R10 records. When the cards are up and the
record + contract exist, tell the orchestrator to resume; read-back, landing, SIGNOFF, and the
regroup (retiring the `⏳ P8.S8 ·` address) follow. Approval must be literal. Then `P8.S9`
applies R11 from the landed `build-prompt.md`.
