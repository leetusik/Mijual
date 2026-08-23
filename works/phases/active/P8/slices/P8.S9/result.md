# `P8.S9` — R11 applied: 내 종목 조회 + 놓친 돈 조회기

**Slice:** apply the signed R11 record onto surface 4 (`/stocks`, `/stocks/{corp_code}`).
**Ran:** 2026-08-24. **Verdict:** done — every §10 box walked in the operator's runtime and in a
production build; five design gaps catalogued as operator questions (Q29–Q34), none invented.

Source of truth read, in the plan's order: `docs/reference/design/rounds/11-lookup/output/**`
(`result.md`, `build-prompt.md`, `geometry-canon.css`, `r11-parts.jsx`, the `Lookup` cards),
`SIGNOFF.md`'s R11 entry, then `phase.md` §"R11 walk" / §"R11 landed spec" / §"`P8.S7` — R10
applied", then the code. Nothing under `docs/reference/design/rounds/**` or `docs/current/**` was
edited.

---

## 1. What the surface is now

**One geometry, ported.** `Lookup.module.css` is rewritten from the round's `geometry-canon.css`
onto module class names, **mobile-first**: the base block is the canon's ≤767 rules and
`@media (min-width: 768px)` is the desktop block. R11 signs **one** breakpoint at 767px; R4's 480px
seam is retired, so no rule on this surface fires between 390 and 767.

**§1 identity.** A resolved stock opens with a `CraftPanel` whose `h1` is the **종목명** (Q-B), a
`.idmeta` line of 종목코드 (when served) then 고유번호, and the existing `SearchRow` pre-filled with
the corp name. `LookupRail` renders the crumb plus 「내 종목 조회」 as a plain `.here` label — the
words appear exactly **once** per page, and the entry page's hero subline does not follow a reader
onto a result. The entry page (`/stocks`) keeps its `h1`/subline and gains the two things it can
honestly say with no stock named (Q-A = b): `WatchPanel` (감시 대상 3종 + 감시 중 {n}건, from
`/board/summary`, absent rather than zeroed if the call fails) and the 집계 범위 section.

**§1 strip (Q-C).** `HoldingStrip` is no longer its own panel — it is a flat rail inside the
identity panel, and it renders **only where a number on the page moves with it**: a live ① with
`offering`, or at least one 놓친 돈 row. On 풍전약품 (②-only) and 세기상사 (no rights) there is no
strip, no disabled control and no sentence.

**§2 rights.** Panels are **the deadline**: `h3` is `countdown.label_ko`, the chip + 접수번호 + 공시
sit in `.rmeta`, and the countdown slot keeps R10's three forms (`DDay` · `StateBadge kind="tbd"` ·
the dashed `.absent` chip). Every ② row of a stock is grouped into **one** table (`ConvertibleTable`)
placed at the first ② row's rank, with a per-table `.ctsrc` source line; an unserved fact prints
`⋯` (`.ctmiss`) with the column label carried on `data-l` and shown by `::before` at ≤767. ③ gains
the **2단계 절차** block (number pills, `h4` step titles, windows or the dashed 「현재 버전 공시에
없음」 chip, the dependency sentence). A closed ① leaves one `.closed` line; 0건 renders `NoRights`.

**§5 놓친 돈.** The total is rendered **only when the stock has ≥2 offerings and a holding is
entered** — one offering shows its own figure once, in the row (`.big`), and nothing above it.
Each row is 공시 identity + window + the two-line 소멸 계산 + the reader's own slot; each row
carries its **own** `.calcfoot` 배정비율 line. `.disc` closes the panel.

**§6 one affordance.** 「상세 보기 →」 is the only link out of a row. The 놓친 돈 prompt
(`MISSED_PROMPT_KO`, the round's single new sentence) renders **once per page** — in the first live
① chain's foot when there is one, otherwise in the 놓친 돈 head — and never once a holding exists;
pressing it focuses the strip's input.

**§8 outline.** Both previously unnamed blocks now have headings: 집계 범위 is an `h2` section and
the strip has a real `label`. Eyebrow `h2`s carry `aria-label` (R10's rule: Chrome folds `::before`
content into the accessible name), so **no accessible name on this surface contains `//`**.

**Copy.** Every string enters through `components/lookup/copy.ts`. One genuinely new sentence
(`MISSED_PROMPT_KO`), the gate-signed `.mmcap` caption (Q28 = a), and a set of **label-tier** strings
the build prompt and cards print (보유 · 배정비율 (1주당) · 초과청약 비율 · 공시 · 소멸 계산 (시장
전체) · 종목코드 · 고유번호 · 접수). Two constants are **derived**, not typed: `TRADING_OPEN_KO` is
`tradingOpenKo("")`'s head and `NO_SCHEDULE_KO` is the tail half of R3's locked 「카운트다운 없음 —
일정이 공시상 미정」, so neither can drift from the string it came from. `noMatchKo` gained the
build-prompt §7 josa rule (`(code − 0xAC00) % 28 !== 0 ? '과' : '와'`; non-Hangul → 「와/과」).

**What later surfaces inherit.** R12 (auth) is unaffected in placement: `ConversionOffer` still
renders last in normal flow and is still gated on `lib/holding.ts`'s own `convert()` returning a
non-null value, so it cannot appear beside numbers that do not exist. `Conversion` and `Dilution`
are byte-identical for `/portfolio`; the new `ConversionChain` / `ConvertibleTable` are built beside
them, and every R4/R5 class `/portfolio` still uses survives in the rewritten stylesheet.

---

## 2. What the stock route serves — and does not

Read from the live payload, and cross-checked against `src/mijual/web/reads.py`. This is the
evidence behind the readings in §3.

| The record draws | The route serves | Rendered as |
| --- | --- | --- |
| ① `.rowline` 구주주 청약 · 일반공모 windows | `offering.subscription` exists but is typed `unknown`, read by no surface; there is no `subscription_agents` field and no 일반공모 window | **omitted** (Q29) |
| ③ step windows (통지 기간 / 청구 기간) | 아시아나's R3 row arrives with `fields: {}` on this route | both steps show the dashed 「현재 버전 공시에 없음」 chip (Q30) |
| `.bofftitle` 「2026-03-26 결정 유상증자」 | `_lapse_row` composes no 결의일 for the lapse row | 「유상증자」 alone (Q31) |
| entry-page 집계 범위 dates | `lapse.coverage` rides `GET /stocks/{corp_code}` only; `/board/summary` has none | boundary sentence, **no dated rows** (Q32) |
| ② 전환가액 / 전환 시 주식수 / 오버행 | all three served for every ② row in today's corpus | 0 `⋯` cells in production data (stub-verified, §4 box 2) |

---

## 3. Readings and deviations, each with its reason

1. **`.rowline` omitted.** The signed read-back itself says "the apply slice renders them from
   served fields only and omits what is not served (no new payload)". Rendering the two labels would
   have meant minting unregistered copy over a field no surface reads. → **Q29**.
2. **③ steps render dashed, not dated.** Not a defect: `fields: {}` is what the route serves for the
   only ③ in the corpus. The **dated** form was verified through a read-only scratch proxy (§4) so
   the branch is browser-verified, not code-read. → **Q30**.
3. **`.bofftitle` = 「유상증자」.** Inventing a 결의일 is a fact the product does not have, and
   reintroducing the corp name is the exact repetition R11 §5 removed. → **Q31**.
4. **Entry-page coverage renders the sentence without dates.** A date this page was never given is
   not a fact. → **Q32**.
5. **Label-tier strings registered under the Q28 precedent.** They are in build-prompt §2/§4/§5 and
   in the landed cards but not in the round's `result.md` §4 "one new string" list. The gate answered
   Q28 by signing the cards **as landed**; the same reasoning covers these. Flagged rather than
   assumed. → **Q33**.
6. **Card sample data not treated as contract.** 「매매기간」/「행사기간」 prefixes on `.win` and the
   third `.idmeta` span 「DART 공시 기준」 appear in the cards but not in the build prompt; the build
   prompt governs, so they are omitted. 「거래 가능」 is taken from `tradingOpenKo`'s own head, which
   is what the card prints.
7. **`.calcfoot` per row, not once per panel.** The card's single foot is the single-offering case;
   P5 established that two offerings of one stock do not share a 배정비율, so one foot per row is
   the reading that keeps the arithmetic honest.
8. **`.zero` no longer repeats the coverage caption** (R11's `Zero` card is two lines and the new
   `h2 집계 범위` section carries the boundary); in the non-zero state `pendingLapseKo` moved to the
   `.mmcap` caption tier, where the round places it.
9. **`josa` follows build-prompt §7 and the plan**, not `r11-parts.jsx`'s extra branch — the prompt
   is the contract and the parts file is illustration.
10. **`.page` / `.narrow` are stated at doubled-class specificity.** Not a style choice — see §5.
11. **The no-match line's lifetime is owned by `LookupHeader`**, which listens to the bubbling
    native `input` event on its wrapper. `SearchRow.tsx` is on the do-not-touch list and was not
    modified; this is how the sentence disappears on the first differing keystroke without it.

No other deviation. No new feature, no new payload, no backend change, no new endpoint.

---

## 4. Verification — build-prompt §10, boxes 0–12

**Runtime.** `## Operator Runtime` in `docs/current/operations.md`: stack via `make stack-up`,
`next dev`, Chrome desktop at `http://127.0.0.1:3000` **and** the tailnet origin
`http://100.77.164.42:3000`, plus mobile viewports. Every box below was walked at **both** origins
and again against a **production build** (`npm run build` on a scratch copy — `cp -Rc` for
`node_modules`, per `P8.S7`'s note — served with `next start -p 3100`). Widths: 1456 desktop, 390
mobile, and a ~600px check. Results were identical at all three unless stated.

| Box | Claim | Measured |
| --- | --- | --- |
| 0 | identity present, no duplicate title | `h1` = 종목명 on all five stocks incl. 세기상사; the input echoes the name; 「내 종목 조회」 appears **once** (the rail); no hero subline on a result |
| 1 | 종목코드 · 고유번호 meta | both served stocks show 종목코드 first, then 고유번호; unserved 종목코드 simply absent |
| 2 | ② is one table | 풍전약품: **1** panel, **1** table, 3 rows + head + `.ctsrc`「DART 공시 API — 전환가액 · 전환 시 주식수 · 오버행 | 3건」; 「풍전약품」 printed once; no strip; no prompt; **0** `.ctmiss` |
| 3 | ③ 2단계 절차 | 아시아나: solid `StateBadge 추후결정` + 「일정이 공시상 미정」 + two dashed chips (`borderTopStyle: dashed`) + the dependency line; outline h1/h2/h3/h4×2 |
| 4 | citation is the third child of `.bwin` | true on every row; no row-spanning citation; popover opens fully in view at 1456 (x 538→918) and 390 (x 8→348); rows do not move; trigger 32/44px; `aria-expanded=true` |
| 5 | one figure per row, no total at 1건 | 한화솔루션 500주 → `679,575원` printed **once**, 하한 `545,181원`, cap 「배정 123주 × 「추정」5,525원」, **no** `.total`; cleared → prompt returns, dashed `.bslot` 208×44, header 「보유 주식 수」 |
| 5b | total at ≥2건 (stubbed — unreachable in the corpus, see §6) | duplicated lapse row → `.total` `1,359,150원추정 | 하한 1,090,362원추정` at 32px, `.big` **false** on both rows, `679,575원` twice, `.mmcap` 「유상증자 2건 …」, 2 `.calcfoot`, 0 untagged 원 |
| 6 | no strip where nothing moves | absent on 풍전약품 and 세기상사 |
| 7 | no-match sentence | `/stocks?q=삼성` → 「‘삼성’과 일치하는 종목이 없습니다 — …」; first differing keystroke removes the line and the candidate list opens (계양전기 012200) |
| 8 | entry page | 감시 대상 3종 + 감시 중 488건 + `h2 집계 범위` + provenance; `h1` 내 종목 조회 + subline |
| 9 | a11y | `headSlash: 0` on all six pages — identical to the `/events/…` R10 baseline; `role="status"` on the no-match line; presets carry `aria-pressed`; textbox name 「보유 주식 수」 |
| 10 | 390px targets | **zero** interactive targets under 44px on any page or the entry; `overflowX` 0 everywhere; presets 104×44 in a 3-col grid, restore 324×44 on its own row, `.stripcap` own row, input 240×44, entry input/submit 48px |
| 11 | one breakpoint | 481 / 600 / 767 all render the one-column breakdown, `.bhead`/`.cthead` `display:none`, `.idp` single column, presets grid, golink 44px; 768 is desktop. **One** boundary |
| 12 | trust | no untagged 원 amount anywhere; 계양전기 (발행가 확정 전) shows **zero** 원 amounts before or after entering 500주 while share counts still convert; typing a holding fires exactly **one** request (`GET /api/auth/me`, R5-2's `ConversionOffer`) and it carries no number |

**Stubbed states** (read-only scratch proxy on 127.0.0.1, upstream JSON rewritten in flight —
nothing in the repo, the dev server or the database was touched; `MIJUAL_API_ORIGIN` pointed the
scratch production copy at it):

- ② past-open → 「진행 중」 in `--live` `rgb(95,208,165)`, dates kept, 「종료」 count **0**
- ① closed → 「기한 지남」 chip
- ③ dated → two steps with real windows, both `.pastStep` + 「기한 지남」, **no** dashed chips (the
  two notations never mix)
- ≥2 offerings → the `.total` row above (box 5b)
- ② unserved facts → `.ctmiss` `⋯` at `rgb(109,131,120)` with `data-l=전환가액` / `data-l=전환 시
  주식수`; at 390 the labels come back as `::before` content; **no** `0원`/`0주`/`0%` anywhere

**Heights at 390** (document, chrome = 52px header + 155px footer): 계양전기 1,469 · 한화솔루션
1,572 · 풍전약품 1,754 · 아시아나 1,608 · 세기상사 940. Against the walk's own baselines that is
한화 1,723 → **−8.8%** and 풍전 2,075 → **−15.5%**, but the record's ≈1,250 / ≈1,150 targets are
**not** met. Cross-checked against the canon itself in a `file://` harness: the canon's own `.ctrow`
at 390 is **252px** where the product's is 273px, with the same `.ctwhen`-above-`.ctfiled` stagger —
i.e. the residual height is the canon's geometry, not a build defect. → **Q34**.

**Neighbours.** `/portfolio` is unaffected (it uses only preserved shared classes; no overflow at
1456 or 390) and the landing hero is unchanged.

---

## 5. The one thing that only a production build showed

`<main>` on both routes carries the shared `content` class **and** the module's `page`/`narrow`.
In `next dev` the module stylesheet landed last and the two routes measured R11's 960px / 620px. In
the **production bundle the order flips**: `app/shell.css`'s `.content { max-width: var(--bp-lg) }`
landed last and both routes rendered at **1120px** — the whole surface silently wider than the round
signed, on exactly the build the operator would deploy.

Fixed by stating R11's two widths at a specificity neither order can outrank:

```css
.page.page { max-width: 960px; }
.narrow.narrow { max-width: 620px; }
```

Re-measured after a fresh production build: 960 / 620 at both `:3000` and `:3100`. Then a computed-
style diff of **63 classes × 5 pages × 3 widths** across dev and production: **no differences**.

This is the concrete argument for the plan's "additionally in the production build" clause — the bug
class is invisible in `next dev` by construction.

---

## 6. Corpus limits worth recording

`lapse` today: **32 reports across 32 distinct corps — 0 corps with ≥2**. R11 §5's total rule is
therefore unreachable in production data, as is `.ctmiss` (every ② row serves all three facts).
Both were exercised through the scratch proxy above and are recorded here as stub-verified, the same
treatment `P8.S7` gave the ② past-open state (P8 Q22).

---

## 7. Validation

| Command | Result |
| --- | --- |
| `cd frontend && npm run typecheck` | pass (clean) |
| `cd frontend && npm run smoke` | pass — **16/16** |
| `npm run build` (scratch production copy) | pass — green, and the copy is what boxes 0–12 were re-walked against |
| `.venv/bin/python -m pytest` | pass — **142 passed** |
| `python3 scripts/workflow.py validate` | pass — "Workflow validation passed." |

Full `## Regression Checklist` re-run alongside the boxes above: chrome (two nav links, no vocky
node), 보유 종목 signed-out sample, 의견 보내기 states, ≤480 sheet, footer at 390, landing board
window/rows/columns/strips/countdown/소멸주의보/auto-refresh/hero Enter, event detail header states,
citation popover, section density, 정정 이력, 아시아나 ③, 404 — all still green on this commit.

No test files were added: the surface's guarantees are geometric and were measured directly, and the
existing smoke suite already covers the routes' status codes.

---

## 8. Files changed

- `frontend/components/lookup/copy.ts` — R11 strings, the josa rule, the two derived constants, the
  `splitAround` parts helper
- `frontend/components/lookup/Lookup.module.css` — the canon, ported mobile-first
- `frontend/components/lookup/LookupHeader.tsx` — `LookupRail` / `LookupHeader` / `LookupIdentity`
- `frontend/components/lookup/HoldingStrip.tsx` — flat rail, labelled input, presets, restore
- `frontend/components/lookup/Conversion.tsx` — new `ConversionChain` beside the untouched `Conversion`
- `frontend/components/lookup/RightsSection.tsx` — panel-as-deadline, `ConvertibleTable`, `Procedure`
- `frontend/components/lookup/MissedMoney.tsx` — total rule, per-row `.calcfoot`, one affordance
- `frontend/components/lookup/LookupEmpty.tsx` — `WatchPanel` / `NoRights` / `CoveragePanel`
- `frontend/components/lookup/StockView.tsx` — holding ownership, `showStrip`, the single prompt
- `frontend/components/lookup/index.ts` — exports
- `frontend/app/stocks/page.tsx` — entry-page composition + `/board/summary`
- `frontend/app/stocks/[corp_code]/page.tsx` — rail instead of the header block
- `docs/reference/design/grounding/copy-inventory.md` — the hand-registered R11 tail

Untouched, as required: `SearchRow.*`, `components/Citation.*`, every `components/event/*`,
`lib/types.ts`, `lib/api.ts`, `lib/holding.ts`'s math, the backend, `docs/reference/design/rounds/**`,
`docs/current/**`.

---

## 9. Raised for the operator

Q29 (`.rowline`) · Q30 (③ step windows) · Q31 (`.bofftitle` 결의일) · Q32 (entry-page coverage dates)
· Q33 (label-tier strings on the Q28 precedent) · Q34 (390 heights vs the record's targets) — all
appended to `phase.md`'s `## Operator Questions`, none decided here.
