# Plan — P8.S7 · Apply R10 — event detail ①②③ + trust states (surface 3 of 8)

## What this slice is

Implement the **signed R10 design** (SIGNOFF.md R10, closed 2026-08-24, authorization "sign off")
faithfully on the event detail surface. **RESPECT THE DESIGN**: build exactly what the landed record
says — never drop, simplify, restyle, or "improve" an approved element; where the record is silent,
read the three in order and log the reading in `result.md`:

1. `docs/reference/design/rounds/10-event-detail/output/build-prompt.md` — the implementation
   contract (§0 common rules · §1 header · §2 ① chain · §3 ② strip · §4 ③ steps · §5 field rows,
   headings, **citation density** · §6 Citation popover · §7 corrections · §8 **404** · §9 question
   strip placement · §10 regression checklist 0–9).
2. `…/output/detail/r10-detail.css` — geometry source of truth (port it; the cards render nothing
   outside it) and `…/output/detail/r10-parts.jsx` — structure (component anatomy, real rows).
3. `…/output/components/Citation.jsx` — the Citation re-cut (popover, hit sizes, open state) and the
   7 cards `…/output/detail/{Header,Offering,Convertible,Procedure,Fields,Corrections,States}.html` +
   `…/output/components/Citation.html` for states and notes. `result.md` §2/§5 for intent and the
   logged departures. `docs/reference/design/SIGNOFF.md` R10 entry for what supersedes what.

Read first: `CLAUDE.md`, `works/phases/active/P8/phase.md` (§"R10 walk", §"R10 landed spec",
§"`P8.S5` — R9 applied" for the patterns the landing now uses — stretched links, `접기`, 44px rows —
and the `## Operator Questions` list), `intent.md`, `docs/current/frontend.md` (R3 event detail
section + trust rules), `docs/current/qa.md` (`## Regression Checklist`),
`docs/reference/design/grounding/copy-inventory.md` (tail sections — the hand-registered pattern you
will extend).

Read-back observations already logged (phase.md) and how to treat them: the Citation **card's prose**
still describes R3's inline panel — the **JSX + build-prompt §6 (popover)** govern; Procedure's 390
label says 34px — **CSS (60px ≤767px)** governs; the checklist is ten items (0–9).

## Operator runtime (verify here — not only in your own convenience runtime)

`docs/current/operations.md` `## Operator Runtime`: `make stack-up` dev stack — API on
`127.0.0.1:8000` (no `--reload`: restart it if you touch `src/` — you should not need to), `next dev`
on `http://127.0.0.1:3000` (Chrome desktop on this Mac) **and** the tailnet origin
`http://100.77.164.42:3000`; plus a **production build** (`cd frontend && npm run build && npx next
start -p 3100`, stop it after) because §6/§8 behaviour (popover, not-found) can differ between dev and
prod. Desktop 1512/1280 and **390** (≤767px rules). Never print `.env`, never type credentials, never
put the vocky key anywhere. Walk pages: ① 계양전기 `20260724000546` · 한화솔루션 `20260720000067`
(closed window + 청약 결과) · 경남제약 `20260623000409` (추후결정) · 썸에이지 `20260805000454` (철회) · ②
대동기어 `20251016000315` · 풍전약품 `20250930000508` · 라온텍 `20250818000222` (sparse ②) · ③ 세기상사
`20260713000345` (+ `20260623000277`) · 아시아나항공 `20260713000482` (absent) · 404: `/events/20260709000212`,
`/events/2026070900021`, and a mistyped `/events/abc`.

## Binding decisions (from the signed record — do not re-decide)

- **No new features, no payload/field/calculation changes.** Everything is presentation, state, geometry, copy.
- **Citation (§6)** — keep the mono `[근거]` word (`CITATION_CHIP_KO`); hit **32px desktop / 44px ≤767px**
  via padding + equal negative margin (row rhythm unchanged); hover `--live-tint` + no underline;
  focus-visible 2px `--focus-ring`; open = `--live-tint` fill + `aria-expanded="true"`; the quote is an
  **overlay popover** (absolute, `top:calc(100% + 6px)`, 380px / mobile `calc(100vw - 44px)` max 340px,
  opaque `#0e1a15`, 1px `--border-strong`, 2px `--live` left edge, `--panel-glow`, quote `pre-wrap`
  `max-height:200px` scroll, `×` 28px / 44px mobile top-right, bottom link **`DART 원문 {rcept} ↗`**
  32px / mobile full-width 44px hairline row). Close = × · outside click · Esc. Rows never move. Props
  unchanged. Multi-part quotes (`parts`, P5.S20): render every part verbatim and separately **inside the
  popover** (R10 is silent on parts; keep the P5.S20 rule — log the reading). Keep `inert`/a11y
  semantics equivalent (popover `role="dialog"` per the JSX; the chip keeps `aria-controls`/label).
  Media query needed → do it in `Citation.module.css` (CSS module is the repo's idiom; the JSX's
  self-injected `<style>` is the card-world equivalent — build-prompt §6 allows "CSS 모듈로 이관").
  This re-cut **propagates** to every Citation user (`lookup/Conversion.tsx`, `lookup/MissedMoney.tsx`,
  event fields/offering/corrections/withdrawn, and `ask/InlineCitation.tsx` if it wraps `Citation`) —
  verify those surfaces still work; do not redesign them.
- **Citation density (§5, operator direction)** — `[근거]` only where the on-screen value differs from
  the filing's words: 매매기간 / 상장·매매기간, 초과청약 비율, 확정발행가, 할인율, 보호예수 해제일, 청약 결과
  수치, 정정 요약, 철회 근거 → chip. Rows whose value **is** the filer's sentence 1:1 — 발행가액
  산정방법, 청약 취급처 표, 리픽싱 조건, 콜·풋 스케줄, 통지 방법 · 접수처 — **no chip**. Implement as a
  declarative set of field keys in `fieldOrder.ts` (map the Korean names above to the payload keys via
  `copy-inventory.md` / `fieldOrder.ts`; when a key is not in either list, default to **chip if the
  payload carries a quote** and log it). **Every section closes with `.secsrc`** — one mono line
  `DART 원문 {rcept_no} ↗` (right-aligned desktop, left ≤767px, 32/44px) — mandatory where a section has
  zero chips; the cards render it on every section, so render it on every section. The provenance
  sentence at the page foot stays verbatim.
- **Header (§1)** — grid `minmax(0,1fr) auto`, gap `14px 24px`, padding `18px 20px 14px`,
  **`min-height:136px`** desktop (`align-content:start`), **`248px` ≤767px** (`space-between`); meta line
  items `nowrap`, separators as `span+span:not(.corr)::before{content:"·"}`, 「정정 반영」 = `.corr`
  hairline chip, ≤767px first span full-row + separators off; window-state table: ① open `거래 가능 ·
  마감 D-n` (`--live`), ① closed **「기한 지남」** chip (reuse `PAST_STEP_KO`, `.past` style), ② past-open
  `진행 중`, ② pre-open nothing, ③ steps keep their chips; dates always rendered; countdown slot: DDay /
  `StateBadge tbd` + `NO_COUNTDOWN_KO` / **dashed chip** `.absent` with `FIELD_ABSENT_KO`; 담기 line:
  **「보유 종목에 담기 →」** — change the R5-2 constant's value in `frontend/components/auth/copy.ts`
  (`PORTFOLIO_ADD_KO`, cite R10 / SIGNOFF; rename only if it is trivially safe), keep the `days >= 0`
  gate, 44px ≤767px; ≤767px stack via `display:contents` + `order` exactly as `r10-detail.css` (DART
  `order:9`, full-width 44px hairline, `--ink-1`).
- **Question strip (§9)** — attach to the header panel's bottom (`border-top:1px solid --border-soft`,
  padding `10px 20px` / 16px mobile, horizontal scroll, scrollbar hidden, chips `min-height` 36px /
  44px mobile, last 「직접 질문 입력 →」 `--border-strong` + `--ink-1`). **Placement only** — no change to
  the strip's own copy/design beyond those container/height rules (wrap it or pass an additive class;
  do not restyle `components/ask/QuestionStrip.tsx` internals).
- **① chain (§2)** — delete the arrows (`styles.chainArrow`); ruled cells (`grid-auto-flow:column`,
  dashed left rules; ≤767px `row` flow, cell = label-left/value-right, dashed top, 44px); 확정 전 first
  cell **no label** (chip + `확정 예정 {date}`), 예정발행가 still never rendered; 이론가치 = `EstimateMarker`
  **no citation**; 배정비율 full value, `.ratio` (text-base, nowrap) **no citation**; 확정발행가/할인율 cite
  when a quote exists; `.chainfoot` dashed top with the **환산 button** (1px `--border-strong`, 44px,
  hover inset, focus ring; full-width ≤767px). The card's foot sentence 「확정 후 증서 1주 이론가치를
  제공합니다」 is **not** product copy (not in result.md §4) — render **no** note sentence unless an
  existing constant already says it; log. 청약 결과 inset and the 기재 불일치 block stay R3.
- **② strip (§3)** — grid **fixed 3×2** (`repeat(3,minmax(0,1fr))`; ≤767px 1×6), frame + dashed
  inner rules, 「전환 시 주식수」 as its **own cell** (it already is a cell — keep it one, no sub-text),
  **source row** `.fsrc` under the frame: left `DART 공시 API` (new constant e.g. `FACT_SOURCE_KO` —
  an excerpt of `SPARSE_CLOSING_KO`, cite R10 result.md §2-8/§4), right `{rcept_no} ↗` 32/44px; no
  `[근거]` in the strip; 보호예수 two-part value = value line + `.sub` reason line (no em-dash join);
  option cards unchanged except bracket dates `nowrap`; sparse ② = strip + source row + `SPARSE_CLOSING_KO`.
- **③ steps (§4)** — `68px minmax(0,1fr)` (60px ≤767px), number pills 24px hairline mono, **`h3`**
  step titles, windows mono `nowrap`, past steps dimmed + `PAST_STEP_KO` chip, `STEP_DEPENDENCY_KO` only.
- **Headings (§5)** — section eyebrows become **`h2`** with `//` drawn by `::before` (accessible name
  「일정」); 2단계 절차 eyebrow `h2`; correction band sentence `h2`. Page outline: h1 corp → h2s.
- **Corrections (§7)** — band `--surface-raised`, button `.hist` 36px (44px full-width mobile), label
  **`정정 이력` ↔ `접기`** (reuse R9's `COLLAPSE_KO` from `landing/copy.ts` — import it or mirror it in
  `event/copy.ts` with the citation) + `×` mark while open, open surface `--surface-inset` +
  `--ink-2` border, `aria-expanded`/`aria-controls` kept, lazy first-open fetch kept; rail rows
  `min-height:44px` with the rcept link filling the row, current marker + 「현재 읽는 버전」 badge, ≤767px
  3-column collapse; **field moves: arrow column deleted** — each move = label + `.mpair` two tagged
  sides (`MOVE_BEFORE_KO` / `MOVE_AFTER_KO` mono tags, after-side `--surface-raised` + `--ink-1` 600,
  `MOVE_DELETED_KO` in the after side), ≤767px stacked; summary verbatim + bold `schedule_impact` + `[근거]`.
  Superseded-version URL: no redirect, no notice (Q17).
- **철회 (States card)** — notice + locked sentence unchanged; evidence block = head line (`정정사항`
  tag + item name + `[근거]`) then `.mpair` 정정 전 / 정정 후 (same grammar as corrections); 390 stacked.
- **404 (§8)** — **new `frontend/app/not-found.tsx`**: renders inside the R8 chrome (root layout),
  status 404 preserved (`notFound()` in `app/events/[rcept_no]/page.tsx` falls through to it — keep
  that file's comment truthful: update its "framework's own not-found" paragraph to point at the R10
  surface), content in order: `h1` 「이 주소에 해당하는 공시가 없습니다」 · 「관제 현황판에서 감시 중인 공시를
  확인하실 수 있습니다.」 · the requested path in mono (`--surface-inset`, `padding:6px 10px`,
  `word-break:break-all`, **no label** — a small client component with `usePathname()` is fine) · button
  「관제 현황판으로 →」 (1px `--border-strong`, 44px, full-width mobile) → `/`. Never a reason, never a
  distinction flagged/incomplete/report/typo. Three new constants (`NOT_FOUND_TITLE_KO`, `NOT_FOUND_LINE_KO`,
  `NOT_FOUND_BACK_KO`) in `frontend/lib/copy.ts` or `components/event/copy.ts` — your call, cite R10.
- **Common (§0)** — `word-break:keep-all` on this surface, every mono value `nowrap`, `tabular-nums`,
  `box-sizing:border-box`, one breakpoint **767px** for this surface's mobile rules, no new motion.
- **Tokens: none.** Do not touch `foundations/tokens.css` or `app/shell.css` tokens.

## Build order

1. `frontend/components/Citation.tsx` + `Citation.module.css` (popover + hits + open state).
2. `frontend/components/event/Event.module.css` — port `r10-detail.css` geometry (header, chain,
   strip, steps, rows, secsrc, band/rail/moves, notice/evid, 404 classes if colocated, ≤767px block).
3. `Header.tsx` (meta/state table/absent chip/stack), `EventDetail.tsx` (strip attached to the header
   panel; heading structure), `Offering.tsx`, `Convertible.tsx`, `Fields.tsx` + `fieldOrder.ts`
   (density set, h2/h3, secsrc, two-part values), `Corrections.tsx`, `Withdrawn.tsx`, `auth/copy.ts`
   (담기 label), `event/copy.ts` (new constants with citations), `app/not-found.tsx` (+ page.tsx comment).
4. `docs/reference/design/grounding/copy-inventory.md` — append a hand-registered **「R10 additions」**
   tail: the four new strings (`not_found.title/line/back`, `offer.add` superseding R5-2's label) and
   `FACT_SOURCE_KO` as a reuse note; `phase.md` `## Doc impact` lines: **frontend** (R10 supersedes R3
   chain/citation/diff/strip/mobile-stack + R5-2 label + Citation popover + 404 surface), **qa** (append
   build-prompt §10 items 0–9 to `## Regression Checklist`), **product/experience** (Korean not-found; one
   `[근거]` per extracted value, section source lines), **copy** (4 strings).
5. Verify (below), write `result.md`, append durable notes to `phase.md` (what later surfaces inherit:
   the Citation popover now everywhere, `.secsrc` pattern, 「기한 지남」 rule, 404 surface).

## Verify — every box, in the operator runtime

- `cd frontend && npm run typecheck` · `npm run smoke` · `npm run build` (restore `next-env.d.ts` if the
  build rewrites it) · `.venv/bin/python -m pytest` (floor) · `python3 scripts/workflow.py validate`.
- build-prompt **§10, 0–9**, measured (DevTools/CDP) in `next dev` on **both origins** and once in the
  production build, desktop + 390: header height equal across the four states (136 / 248 floors);
  no orphan `→`/`·` at 390; every citation trigger / rcept link / button ≥44px at 390; no section with
  per-row chips where the rule says none and every verbatim-only section closes with `.secsrc`;
  「정정 이력」→「접기」 + surface change; 「기한 지남」 on closed ① (한화솔루션), 「진행 중」 on past-open ②,
  「종료」 nowhere; 아시아나 two dashed chips, no placeholder, no reason; outline has h2s, names without
  `//`; `/events/<nonexistent>` → Korean 404 with status **404** (check the response code, not just the
  render), path echoed, button → `/`; no mono date/figure splits at any width.
- Popover: opens under the trigger, rows do not move, × / outside click / Esc close, focus handling
  sane, DART link 44px full-width at 390; multi-part quote (find one via the API: a Figure with `parts`)
  renders each part. Regression on other Citation users: `/stocks/00102618` (lookup conversion + 놓친 돈)
  and an ask answer with inline citations still work.
- Question strip attached to the header bottom, chips 36/44px, horizontal scroll, surface-7 copy untouched.
- Console: 0 errors (favicon 404 = D5 known). 0 document horizontal overflow at 390.

## Don'ts

No new data/fields/API; no redesign of QuestionStrip internals, lookup, ask, portfolio; no change to
R8 chrome; no edits under `docs/reference/design/rounds/**` or `docs/versions/**`; no `doc-new-version`;
no commits/state transitions. Return `done` with `files_changed`, the readings you logged, and the
Doc impact lines; `needs_operator` if the manifest runtime is unreachable; never silently narrow.
