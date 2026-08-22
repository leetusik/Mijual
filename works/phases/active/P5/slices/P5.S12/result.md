# Result — P5.S12: Landing 관제 현황판 (R2/R2.1 + R3's board strip)

The landing is built and every number on it is **live from `/board/summary` and `/board`**:
cosmos backdrop (starfield · glows · shooting stars · hero orbits), search-first hero,
the two retrospective anchor panels, the ticking 소멸 countdown, the 소멸주의보 placard and
the board with its tabs, rows, freshness treatment and the two pinned strips. S10's
foundation proof — and with it the dated 2026-08-20 pack numbers — is gone.

**0 new dependencies. No primitive, token or chrome file was touched. The Python suite is
untouched at 113** (this slice edited no Python file). **No Korean string was invented**:
every string is transcribed with its source in `frontend/components/landing/copy.ts`.

## What landed

| file | what it is |
|---|---|
| `frontend/app/page.tsx` | the landing: `connection()` + one `Promise.all` over the two reads, then the five sections |
| `frontend/app/page.module.css` | the page stack (the hero is full-bleed; everything else in the 1120px column) |
| `frontend/components/landing/copy.ts` | every Korean string this surface renders, each with its citation |
| `frontend/components/landing/Cosmos.tsx` (+ `.module.css`) | the `.backdrop` slot: 240/160 stars, two glows, 5/3 shooting stars |
| `frontend/components/landing/Hero.tsx` (+ `.module.css`) | H1 · sub · console search row (GET → `/stocks?q=`) · mono stat line · the hero-only orbit rings |
| `frontend/components/landing/Anchor.tsx` (+ `.module.css`) | the value card and the countdown/stats card, 1fr / 340px |
| `frontend/components/landing/Countdown.tsx` (+ `.module.css`) | `{d}일 HH:MM:SS`, blinking colons, **interval stopped** under reduced motion |
| `frontend/components/landing/LapseNotice.tsx` | 발표용 문장 4 with live numbers, inside the `LapseAlert` placard |
| `frontend/components/landing/Board.tsx` (+ `Board.module.css`) | header · freshness · stale notice · tabs · rows · the ② and 추후결정 strips |
| `frontend/components/landing/BoardRow.tsx` | R2's row anatomy — used by the board **and** by both expanded strips |
| `frontend/components/landing/EstimateValue.tsx` (+ `.module.css`) | the landing's estimate-tag context (R2's 10px tag over a value of any size) |
| `frontend/components/landing/index.ts` | the landing barrel |
| `frontend/lib/format.ts` | **new, shared**: `won` · `count` · `percent` · `kstStamp` — exact decimal-string arithmetic, no float |
| `frontend/lib/routes.ts` | edited: `eventPath(rceptNo)` added (the module's own rule — later slices *add* entries) |

## Validation

| command | outcome |
|---|---|
| `cd frontend && npm run build` | **pass** — `/` is `ƒ (Dynamic)`, the other three routes still prerender; no API needed at build |
| `cd frontend && npm run typecheck` | **pass** |
| `cd frontend && npm run smoke` | **pass** — 3 cases, ~86 ms |
| `.venv/bin/python -m pytest` | **pass** — **113**, unchanged, ~2.5 s, no network/model |
| `python3 scripts/workflow.py validate` | **pass** |
| dev + prod browser pass (headless Chrome over CDP, `http://localhost:3000` and `:3100`) | **pass** — below |

### The browser pass (2026-08-22, live corpus)

Run against `uvicorn` on 8000 with `npm run dev` **and** re-run against
`npm run build && npm run start` (S11 note 12's second opinion). **The production run's
console is completely empty** — no hydration warning anywhere, which is the check the
deterministic starfield exists for.

| check | result |
|---|---|
| hero stat line vs `/board/summary` | `718.1억원`「추정」 · 감시 중 **488**건 · 30일 이내 마감 **33**건 — exactly the served `lapsed_value` / `watching` / `within_30d` |
| the two anchor cards agree | value card 718.1억원 + 밴드 하한 548.7억원 + 365,527,824주 / 14.0%; stats card 488 · 33 · 15 · 69 — one summary object, so no second readout exists |
| countdown against the served target | ticks 1 Hz, and the browser's own diff against `next_lapse.target` (`2026-09-05T00:00:00+09:00`) is **0 s off** the rendered `13일 HH:MM:SS`; colon animation `blink 1s` |
| countdown under reduced motion | value **identical after 3 s** (interval never runs), colon `animation-name: none` |
| starfield / shooting stars / orbit under reduced motion | twinkle `none` (star keeps its base opacity), drift `none`, orbit `none` at `offset-distance: 0`, shooting-star layer `display: none` |
| board counts vs tabs | 전체 **488** · 유증 **50** · CB **422** · 매수청구 **16** = `counts` verbatim; filtering to CB leaves 365 rows, all R2; to 유증 leaves 14; back to 전체 leaves 389 |
| a ① unpriced row | 계양전기 `유증 · 신주인수권증서 매매 마감 2026-08-25 · 청약 2026-09-04 · 발행가 확정 전 · D-3` — and **no `원` amount anywhere on the page** (regex over the rendered text: none) |
| ② 진행 중 strip | "전환청구 **진행 중** — … 전환사채 **57건**" = `open_now.count`; 펼치기 opens **57** rows, first is 삼성제약 **D+1** rendered faint, never 종료 |
| 추후결정 strip | "일정 추후결정 — 카운트다운 없이 감시 중인 이벤트 **4건**" = `tbd.count`; 펼치기 opens 4 rows, each `StateBadge 추후결정`, **no date anywhere on them**, each linking to `/events/{rcept_no}` |
| freshness chip | `기준 2026-08-22 04:14 KST`, IBM Plex Mono 11px `--ink-3` = the served `freshness.as_of` |
| stale treatment | re-run with `MIJUAL_STALE_AFTER_HOURS=1`: chip flips to alert-tint + `· 7시간 전 데이터`, the inset notice appears above the tabs, **and the rows render identically** — content never dims |
| R2's row measurements | grid `86px 262px(1fr) 300px 230px 96px`, 9px v-pad, `dashed 1px --border-soft`, DDay flush right, ↗ mono 11 `--ink-3`, ②/③ extras cell **genuinely empty** |
| rings | 980×280 and 1200×360 at full size, rotated −14°, box **72 → 712** with the nav ending at 52 and the first panel starting at 732 — fully clear of both |
| 390×844 | H1 34px, controls 48px, **160** stars / **3** shooting stars, compact tabs (전체/유증/CB/매수청구) at a 44px hit, two-line rows at 11px v-pad, **no horizontal overflow** |
| chrome invariants | exactly **one** `position: fixed` element on the page (the backdrop) — the bottom-right corner stays clear for P6 |
| the hero's submit | `method=get action=/stocks name=q` → `/stocks?q=%EA%B3%84%EC%96%91%EC%A0%84%EA%B8%B0`, and that route answers 200 |

Screenshots (desktop 1440 and 390×844) were taken at each step and inspected; they are
session artifacts, not repo files.

## Decisions and readings, each with its grounding

1. **The H1 renders 내 종목 조회, not R2's literal 내 종목 연결.** R2 says of this block "This
   IS the 내 종목 연결 surface … submit goes to R4's 조회", and R4 then *named the surface*:
   its signoff records "the surface name **내 종목 조회**" and its build prompt opens "Surface
   name 내 종목 조회 (R4-5) … The landing hero submits here". The supersession table carries
   the same row. It is a **name for a destination**, not locked prose, and R2's literal would
   print two names for one surface on a page whose nav — one line above — already says 내 종목
   조회. The retired wording survives only in the footer's **locked positioning sentence**,
   which `P5.S11` transcribed verbatim for the opposite reason. Recorded for `P5.S19`.
2. **The ① extras date is the 구주주 청약 window's 마감** (`subscription_end`), which `P5.S3`
   note 10 left to this slice. Every other 청약 date this product prints is the closing one
   (발표용 문장 4's "가장 빠른 청약 마감", the report's 청약종료 column, `next_lapse.date`), and
   the 소멸주의보 strip on this same page prints 2026-09-04 for these same offerings — two
   different 청약 dates for 계양전기 on one page would be the page contradicting itself.
3. **The corp name links to `/events/{rcept_no}`; the `↗` keeps DART.** R2 gives the row only
   the `↗` link, but R3's detail page opens with the crumb "← 관제 현황판" and its 추후결정
   strip says "expanded rows link to detail" — the board is where a reader comes from. Only
   an href is added; the name keeps its 600 weight and the `↗` keeps its job. **The detail
   page is `P5.S13`'s** and does not exist yet: the link 404s today, deliberately, exactly as
   `P5.S11` left `/auth/login`.
4. **The hero got a `min-height` so the rings fit.** R2.1's instruction is an outcome — "never
   shrink them — give the hero vertical room instead, so rings clear the nav line and the
   panels below" — and the stated 110/160px padding alone does not produce it: rotated −14°
   the outer ring occupies ≈640px of height against a 508px hero. The padding is unchanged and
   a 680px floor was added with the content centred inside it. Consequence worth a reviewer's
   eye: the anchor panels now start ~730px down, so on a short viewport the "live layer above
   the fold" phrasing in base-R2's decision 1 is tighter than it was — R2.1 governs the base
   record where they conflict, and the ring rule is what the *build prompt* states.
5. **The estimate tag renders at 9.52px, from a 17px marker context.** R2 asks for a "bordered
   sans **10px** 「추정」 tag" on landing surfaces; the primitive sizes it `0.56em` of its
   context and R1 forbids it to set its own size. So the surface supplies the context
   (`--text-lg`, the closest token to the ~17.9px at which the two readings agree) through
   `EstimateValue`, and the value keeps its own size — 46px on the value card, the line's size
   in the hero and band lines. **The primitive is untouched**; `P5.S11`'s footer tag stays at
   6.72px for the opposite reason. Both are `P5.S19`'s to check against the cards.
6. **The strips state the count that is in view.** `/board` serves `count` (this response) and
   `total` (the whole board), and the client filter reproduces `count`. On 전체 and CB the ②
   strip therefore reads 57건 = `open_now.count`; on 유증/매수청구 it has no rows and **does not
   render** (a strip reading 0건 is a sentence about nothing). The 추후결정 strip likewise reads
   2건 on the 유증 tab, which is what that tab holds.
7. **펼치기 keeps its label while the strip is open**, with `aria-expanded` carrying the state —
   the decision `components/chrome/copy.ts` already records for the 메뉴 button, and for the
   same reason: a 접기 label is copy nobody signed.
8. **The tabs filter the served list in the browser.** `?rights=` exists and does exactly this,
   but the whole board is one 160 KB request (`P5.S3` note 11) and `counts` is whole-board
   either way, so filtering costs no request and cannot show two tabs from two corpora. 전체
   reads 488 while 450 rows are on the page: the 38 past ①/③ are not on the landing by design.
9. **No countdown caption was invented.** R2's countdown/stats card is "countdown + 2×2 live
   stats"; the four stat labels are the round's own, and the card gets no eyebrow because the
   record gives it none. What the countdown counts down to is stated by the 소멸주의보 placard
   directly below it, in the report's own sentence.
10. **The stars are deterministic.** `mulberry32` with a fixed seed, evaluated **once at module
    scope**, so the server render and the client's hydration see the same 240 stars — a
    `Math.random()` field is a hydration mismatch on every load. The mobile field is the first
    160 of the same list (`:nth-child(n+161)` hides the tail ≤480px), so one list serves both
    counts. The glow alphas and the ring hairline alphas are the build's reading: the record
    states the geometry and the counts, and the *hue* is the `--live` token's.
11. **Two figures the summary does not carry produce no phrase at all** — not a zero, not a
    dash. `lapsed_value`, the band edge, the fact sentence's two numbers and the whole
    소멸주의보 strip are each rendered only when the payload carries them, and the countdown is
    rendered only when `next_lapse.target` is served (it is: `2026-09-05T00:00:00+09:00`).

## D2 check (DECOMP note 2) — **the trigger has not fired**

Measured against the live board (450 rendered rows: 389 ranked + 57 ② 진행 중 + 4 추후결정):

- **No two rows share an `rcept_no`.** Zero duplicates across all 450.
- The two known `hint_duplicate` filings are **not visible as duplicate rows**:
  - 코이즈 `20260122000058` sits on events 1195 *and* 1264, both exposable ① — but **neither is
    on the landing**: their 청약 closed 2026-01-27, and past ① rows belong to 조회 and the
    retrospective, not here.
  - 사토시홀딩스 `20251219000402` sits on events 941 (`reattached`) and 942 (`duplicate`), and
    **both are on the landing** — but they are two *different* bonds by their own filings:
    941's original is `20250623000222` (2025-06-23, 전환청구 개시 2026-07-21, in the ② strip at
    D+32) and 942's is `20251215000366` (2025-12-15, 개시 2026-12-23, a ranked row at D-123).
    A reader sees two CB rows with different filing numbers and different dates; the shared
    정정 is an internal pairing artifact, not a duplicated row.
- The one pair that *looks* duplicated is **제이스코홀딩스** — events 479/480, same corp, same
  type, same 전환청구 개시 2026-07-22 — but they carry **different `rcept_no`**
  (`20260714000457` / `20260714000466`): two CB tranches filed the same day. Two truthful rows.

Nothing was de-duplicated, `DISTINCT`-ed or filtered. Promotion of D2 stays the orchestrator's
call; `P5.S14` and `P5.S19` still carry the same check (a per-stock 놓친 돈 total that
double-counts one offering is the other half of the trigger).

## Deviations from `plan.md`

- **Deliverable 2's H1 question is answered as 내 종목 조회** (decision 1) — the plan asked for
  the reading and the record; this is it.
- **The hero carries a `min-height` the plan does not mention** (decision 4). The plan says
  "fully clear of nav and first panel (110/160px hero padding desktop); never shrink the
  rings"; the padding alone does not clear them, so the room was grown rather than the rings
  shrunk, which is what R2.1 instructs.
- Nothing else. No primitive, token or chrome file was touched; no page was stubbed;
  `lib/routes.ts` gained one function under the module's own "later slices add entries" rule.

## What `P5.S13` / `P5.S14` inherit

- **`frontend/lib/format.ts`** — `won()` mirrors `mijual.estimate.won` branch for branch
  (조원 2dp / 억원 1dp / 원 0dp, round-half-even) on **exact decimal strings**; `count()`,
  `percent()` (the pipeline's `f"{rate:.1%}"`) and `kstStamp()` (slices an instant, never
  `Date`-parses it). **Use these; never `Number()` a money or ratio string.**
- **`BoardRow` is R2's board anatomy** and is shared by the board and both strips. R4's
  진행 중인 권리 rows are *panels*, not this grid (R4 §4) — `P5.S14` should not force this
  component onto them.
- **`EstimateValue`** is how a surface gets R2's 10px tag over a value of any size, without
  touching the primitive.
- **`eventPath(rceptNo)`** in `lib/routes.ts` — `P5.S13` builds what it points at.
- The countdown pattern for any live tick: SSR the first value, `suppressHydrationWarning` on
  the text nodes, `useReducedMotion()` to **stop the interval** (not just the animation).
