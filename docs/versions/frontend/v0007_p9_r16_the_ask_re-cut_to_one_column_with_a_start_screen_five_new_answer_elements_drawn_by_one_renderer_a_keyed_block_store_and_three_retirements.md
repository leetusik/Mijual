---
doc_id: frontend
version: v0007
created_at: 2026-08-25T08:57:45+09:00
source: P9.REVIEW
summary: P9 / R16 — the /ask re-cut to one column with a start screen, five new answer elements drawn by one renderer, a keyed block store, and three retirements
previous: v0006_p8_design_polish_pass_r8-r14_supersede_every_reader_surface_one_767_breakpoint_the_overlay_citation_the_404_the_surface_replacing_the_vocky_seam
---

# Frontend

## Status

**The design is signed and it is built.** Seven Claude Design rounds (R1–R7), each closed by the
operator's literal signoff, are now a running Next.js app: chrome plus eight signed reader surfaces
plus the six-tab operator console (P5), plus **the AI 질문 launcher, widget, dedicated page, mobile
page and question strip (P6)** — every one verified in a real browser against its round's own
contract. This doc records both the durable design truth those rounds fixed **and** the
implementation truth the two build phases established. **P7 (실서비스 정상화 fix pass) then made the
built product actually work on the operator's own machine** — and its headline finding is a frontend
fact, not a product one: six of the eleven things the operator reported as broken were one dev-server
origin block (below), not six defects. Deployment remains **P4**'s.

**P9 (스마트 어시스턴트, R16) then re-cut the AI 질문 surface and nothing else.** No file outside
`components/ask/` and `lib/ask*.ts` changed (plus one six-value list in `components/ops/copy.ts`), so
every P8 surface below stands untouched. R16 supersedes the `/ask` page's two-column shape and gives
the answer four new elements; the details are in *The AI 질문 surfaces* below, and the whole record
is at `docs/reference/design/rounds/16-smart-assistant/`.

**P8 (디자인 폴리시 패스) then polished every reader surface, round by round — R8–R14, seven more
signed rounds, no new features.** Surface 8 (운영 관제 `/ops`, R15) was **cancelled by operator
decision** and ships in its R7 + P5/P7 state. What P8 changed structurally, once, for the whole
product:

- **One breakpoint: 767px.** R4's, R5's and R6's 480/481 seams are all retired. `Auth.module.css`,
  `Portfolio.module.css`, `Ask.module.css` and `AskPage.module.css` each carry **exactly one** media
  query, and `Lookup.module.css` is written mobile-first with a single `min-width: 768px` block. On
  the AI 질문 surface the line is an **existence** line, not a layout one: `DESKTOP_QUERY` is
  `(min-width: 768px)` and `AskSurface` returns `null` below it, so at ≤767 there is no launcher and
  no widget in the DOM at all.
- **`components/Citation.tsx` is an overlay popover on every surface** — 32px trigger desktop / 44px
  ≤767, opaque `#0e1a15` panel with a 2px `--live` left edge, `max-height: 200px`, `×` / outside
  click / Esc with focus returned, and a viewport clamp the record could not draw (a chip near an
  edge would otherwise open the panel off-screen; measured −90px at 390). **The rows behind it do not
  move.**
- **미주알 owns its 404.** `app/not-found.tsx` + `RequestedPath.tsx` render the Korean not-found for
  every unmatched URL and every `notFound()`, status 404, path echoed in mono, **no reason given**.
- **The vocky script seam is gone.** `VockyTrigger`, `VockyScript`, every `data-vocky-trigger` and
  `NEXT_PUBLIC_VOCKY_SRC` are deleted; `components/chrome/Feedback.tsx` is 미주알's own 의견 surface
  (six states, three entry points: footer · 모바일 시트 · 계정 메뉴). New shared `Identicon` (+
  `lib/identicon.ts`) and `lib/scrollLock.ts` (counted body-scroll lock — two overlays can now be on
  one screen, and a naive save/restore leaves the page locked).
- **A module width that must beat a shared layout class is stated at doubled specificity**
  (`.page.page` / `.narrow.narrow`), and **any width claim is measured in a production build**. A
  shared class and a module class on one element are ordered differently in `next dev` and in the
  production bundle: `<main class="content page narrow">` measured 960/620px in dev and **1120px in
  production** because `app/shell.css`'s `.content` landed last there. `next dev` cannot show this
  bug class at all.
- **`word-break: keep-all` is per-surface**, and rounds assume it — it is on the landing (R9), the
  detail page (R10), the auth column (R12) and 보유 종목 (R13), and **nowhere global**. `/stocks` is
  still `word-break: normal`.
- **`/portfolio` no longer redirects when signed out** — it renders the sample. The gate is unchanged
  (still the API's 401); the *account's rows* are gated, the route is not.
- **A turn id is a lookup key, not only a React key.** `nextId()` mints `` `t${SESSION_TAG}-${n}` ``
  with an 8-char tag computed once per module evaluation, so a restored `sessionStorage` thread can
  never collide with a fresh turn. `Persisted.v` stays `1` and legacy `t1…` ids still hydrate.
  React ships **no** duplicate-key warning in production, so this whole bug class is invisible in
  `npm run start` — the symptom there is turns silently duplicated or omitted.
- **`crypto.randomUUID` is secure-context only, and the operator's tailnet origin is not a secure
  context** (measured: `127.0.0.1` → `isSecureContext true`; `100.77.164.42:3000` → `false`,
  `randomUUID undefined`, `getRandomValues` present). Any API gated on a secure context — `subtle`,
  geolocation, clipboard, service workers, notifications — is missing on the operator's second access
  path, which is the branch that gets tested least.
- **CSS-module misses are silent in TypeScript.** `styles` is an index signature, so a referenced
  class the module never defines renders `class="undefined"` with no styling and no error (two were
  shipping in `Holdings.tsx`). Grep `styles.X` against the module's `.X` selectors at the end of an
  apply slice.

The build ran under **RESPECT THE DESIGN**, and it held across both phases: **not one landed record
was edited**. The single write into `docs/reference/design/` in all of P5 was the R7 §6.3 vocky
subsection the round itself delegated to the build — **59 lines added, 0 changed** — and **P6 wrote
nothing there at all** (verified: no file under `docs/reference/design/` differs across the whole
phase). Every nit found while building is either a faithful-implementation fix in code or an operator
question, never a record edit. **P7 held the same line under explicit operator overrides**: it wrote
nothing into `docs/reference/design/` either, minted **zero** Korean strings for its two unsigned
elements (the candidate panel and the board's window control both reuse signed copy), and trimmed
exactly two existing strings — each one an override `intent.md` authorises, scoped to the override and
restyling nothing around it.

## Where the design lives — read this before building anything

```
docs/reference/design/
├── README.md                       # the tree + the rules that hold across rounds
├── grounding/                      # P3.S1 — the real-content pack every round was designed against
│   └── README.md                   #   board counts, headline numbers, Korean copy, 11 pinned samples
├── rounds/<NN>-<slug>/
│   ├── handoff.md                  # OUT — what the round had to cover, questions posed back
│   └── output/                     # IN  — returned by Claude Design; READ-ONLY once landed
│       ├── result.md               #   what was designed; every departure logged
│       ├── build-prompt.md         #   the implementation contract — build from this
│       └── tokens.css / fonts.css  #   R1 and R2 only
└── SIGNOFF.md                      # the operator's literal approvals, and what supersedes what
```

**The record is read-only.** Nits found later are apply-time to-dos, never edits to the landed files.
**The cards stay in the Claude Design project** ("Mijual Design System") — they were never copied into
the repo, so `build-prompt.md` plus this doc set is the whole source of truth a build executor gets.

### Read `SIGNOFF.md` first — later rounds supersede earlier ones

A round's landed record is immutable history, so an earlier `build-prompt.md` can state a decision a
later round overturned. The chain, in force at the end of P3:

| superseded | by | what changed |
|---|---|---|
| R1 "light theme only" | **R2.1** | app surfaces run **cosmos-dark**; light `:root` remains for light/print |
| R1/R2/R3 `▷` estimate marker in UI | **R2 gate ruling, executed in R3** | the bordered **「추정」** tag is the system-wide estimate mark; `▷` is retired from the UI (docs and pipeline keep `▷` internally) |
| R1 "no favicon-scale symbol mark" gap | **R2** | ring logo assets (`mijual-logo-ring-{charcoal,white}.png`) |
| R1 lockup "MIJUAL + 한글 미주알 병기" | **R1 revision (operator)** | English wordmark **alone** |
| R2 nav label 내 종목 연결 | **R4** | **내 종목 조회** |
| R2 nav label 해설 | **R6** | **AI 질문** |
| R6 widget 380×560 | **R6 revision ⑥** | **440×620** |
| R5 §Chrome 개정 ⑤ + R5-4 (샘플 chip, 샘플 종료) | **R8** | account slot is a hairline frame with the full email + a 20px `Identicon` + ▾; its menu has **two** states and (with R9 §12) **three** rows — 알림 설정 · 의견 보내기 · 로그아웃 |
| R2 §Board (columns, 30-row window, footer, tabs hover, control heights) | **R9** | **15/+15** window with a three-part footer; fixed value columns with `minmax(0,N)` floors; 36px ≥768 / 44px ≤767 |
| R3 §board strip (fixed 펼치기 label; dateless row) · R2 §Anchors (2×2 stats; 소멸주의보 `{corp}`) | **R9** | 펼치기 ↔ **접기**; three stats; 「N개 종목」 on a tie |
| R3 §detail (five stacked panels, inline citation panel, arrow chain, 「항목 · 정정 전 · → · 정정 후」) | **R10** | **one** CraftPanel; overlay popover; hairline instrument cells; two tagged diff sides |
| R4 §1 · §strip · §2 · §놓친 돈 · R4's 480px breakpoint | **R11** | identity panel with the 종목명 as `h1`; conditional 보유량 strip; one ② table per stock; total only at ≥2 offerings |
| R5-1 (PII 상시 요소, 재설정 disabled, error/notice slots, 480px, 160px primary) · R5-2 (offer as panel + stay line) | **R12** | `PiiInset` deleted; 재설정 focuses instead of greying out; one `p role="status"`; 100%×48px primary; the offer is an inset band |
| R5 §Portfolio · §D-day 목록 · §알림 · §Mobile | **R13** | four content-independent D-day tracks; holdings/rights track sets; a framed 알림 설정 with a rail and an `h1` |
| R6 §Surfaces · §Mobile · §인라인 인용 (API-tier) · R3's API-tier sentence | **R14** | the 767 existence boundary; 「보내기」; signed preset questions behind served labels; 근거 N = chip count; `API_TIER_KO` retired |
| R5-2 「내 포트폴리오에 담기 →」 | **R10** | **「보유 종목에 담기 →」** |

## Stack — as built

- **Framework:** Next.js **16.3.2** (App Router, Turbopack) on React **19.2.8** + TypeScript
  **5.9.3**, over the FastAPI backend. **No UI library, no CSS framework, no test framework, no
  linter** — the design system *is* `tokens.css`, and a framework theme would be a second source of
  truth for decisions R1 already made. **P6 added the first SSE consumer** and still added no
  dependency: `decodeSse` is a pure buffer-in/frames-out function over `fetch`, no `EventSource` (it
  cannot POST or send the CSRF header) and no client library.
- **Styling:** `public/foundations/tokens.css` + `fonts.css`, **vendored byte-verbatim** from the
  landed records (diffed identical, only a provenance header prepended) and **served as static files,
  not bundled**. The directory mirrors the design project's own `foundations/` + `assets/`, so
  `fonts.css`'s relative font URL resolves **unchanged**. **They are read-only: a change in either
  file is a design change.**
- **Component system:** Claude Design's React reference implementations stay in the design project;
  the repo's `components/` are faithful implementations of that spec, not a dependency.
- **Data fetching:** a typed `fetch` wrapper (`lib/api.ts`), one function per route, paths hard-coded.
  No client library, no global state manager — the served payload *is* the state. **The one exception
  is the AI 질문 thread**, which is a conversation rather than a payload; it lives in a module-scoped
  store (below) because the record requires it to survive navigation mid-stream.
- **Rendering:** per surface, and every data-bearing route is **request-time** (`connection()`,
  Next 16's replacement for the removed `dynamic` segment config), because every number on the page
  must be live.
- **The frontend reaches the API through a same-origin rewrite** (`next.config.ts` proxies `/api/*`
  → `MIJUAL_API_ORIGIN`), so there is no cross origin, no CORS and no `SameSite=None`.

### Where things live

| you need | use |
|---|---|
| a trust primitive | `@/components` — the seven R1/R2 primitives |
| to call the API | `@/lib/api` |
| a payload type | `@/lib/types` |
| a route path | `@/lib/routes` — one module, one statement per path (the **ops** map deliberately lives in `components/ops/routes.ts` instead, so no reader module can import an `/ops` href) |
| a Korean string | the owning surface's own `copy.ts`, **every entry carrying its source** |
| ⌊N × 배정비율⌋ × 증서 1주 이론가치 | **`@/lib/holding`** — the product's **one** multiplication site |
| a won/count/ratio rendered | `@/lib/format` — `won()` mirrors `mijual.estimate.won` branch for branch |
| "am I logged in" | `@/lib/session` (client) · `@/lib/session.server` (forwards the request's cookie) |
| "is motion reduced" in JS | `@/lib/motion` |
| the AI 질문 conversation | **`@/lib/ask`** — the module-scoped store; views subscribe, they never own it |
| to stream a turn | `@/lib/api`'s `streamAsk` + `decodeSse` |

## Tokens and theming

- **Light `:root`** — 66 custom properties: surfaces (`--paper #f2f3f2`, card `#fff`,
  `--surface-raised #fafbfa`, `--surface-inset #eef0ee`), borders (`--border-strong #c9cec9`,
  `--border-soft #e3e6e3`), ink (`#15201d / #5a655f / #8b948e`), brand, semantics, rights hues,
  urgency scale, type, spacing, radius, motion, breakpoints.
- **`.cosmos` dark scope (R2.1)** — `class="cosmos"` on the page root remaps 29 tokens and adds
  `--panel-bracket`, `--panel-glow`, `--live-solid`, so every R1 component renders correctly
  unchanged. **App surfaces use it; light `:root` stays for light/print contexts** (the R5 email mock
  is deliberately off-token, hardcoding light values as an external surface).
- **Color semantics are load-bearing, not decoration:**
  - brand charcoal `--brand #1f2926` is **identity only** — the wordmark carries no data color.
  - `--live #0d5c48` = 살아있는 가치 — estimates, `[근거]` citations, live counts.
  - `--alert #c53030` = **expiring / lost only** — ≤7d urgency, D-DAY fill, 소멸주의보,
    발행사 기재 불일치. **Red never encodes price movement** (a deliberate break with 국내증시 관례).
  - rights-type hues, tinted chips only, label-only (no ①②③ numbering in UI):
    ① `#2b5aa0` · ② `#96610f` · ③ `#6d3a5d`.

## Type, shape, motion

- **Pretendard Variable** for Korean UI; **IBM Plex Mono for every numeral** (금액·주수·%·dates·
  D-day·rcept_no) at ~0.95em of the surrounding sans. **Korean prose is never mono.**
- Sizes 11/12/13.5/15/17/20/24/32/44; body 13.5/1.55; display ≥24 at `-0.02em`, weight 700.
- 4px spacing scale (4·8·12·16·20·24·32·48·64). **Radius 0 everywhere. No shadows** — hairline
  borders carry elevation (the cosmos scope adds a top-edge glow + 9px corner brackets on craft panels).
- Motion: **fades only**, 120/200/320ms, one ease `cubic-bezier(.2,0,.2,1)`; countdown colon blinks
  `1s step-end`. `prefers-reduced-motion`: ticks freeze, fades become cuts, starfield/orbit/shooting
  stars stop or hide.
- **One sanctioned ambient-motion exception:** the AI 질문 launcher mark (22px Saturn, rotating band
  4.5s, ring split front/back on one 14s drift). Brand launcher only — **never on a data surface**.
  **Built and verified in P6**, with two rules worth restating because the round already paid for
  one of them: the ring is **two half-boxes sharing a single drift animation**, one clipped in front
  of the planet and one behind, so it reads as one ring passing through a sphere — a single ring laid
  on one side reads as a flat sticker, which was the original bug. And `prefers-reduced-motion` must
  stop the band, the drift, the transitions **and the hover scale**; the shared freeze convention
  cannot express the last two, so the launcher's own stylesheet adds them. Measured: the data
  surfaces carry the launcher's three animations and nothing else, and `/ask` carries none.
- **The SSE states use text replacement plus one blinking caret** and nothing more. No spinner, no
  typing dots, no bubble slide — the caret is the only new tick, and it freezes with everything else.

## Component conventions

- **Trust primitives (R1, `components/`)** — every surface composes these, none re-invents them:
  - `EstimateMarker` — the bordered **「추정」** tag beside a value; inherits size, never sets its own.
    **An estimate never renders untagged; a fact never carries the mark.**
  - `Citation` — per-field `[근거]` chip → inset panel with the verbatim quote (pre-wrap, scroll >180px)
    + link `https://dart.fss.or.kr/dsaf001/main.do?rcpNo={rcept_no}`. In AI 질문 the same primitive
    appears as **numbered evidence chips** (same source → same number).
  - `StateBadge` — 추후결정 (chip, **never with a date**), 철회 (full-width notice replacing the card
    body, locked copy per rights type), 발행사 기재 불일치 (alert-tint chip). **A gate-failed field or
    event renders as nothing** — no placeholder, no dash, no row.
  - `DDay` — mono 600 at one fixed size; **urgency changes color only, never size**: >30d `--ink-2` →
    ≤30d `--ink-1` → ≤7d `--alert` → D-DAY white on `--alert`; D+N unfilled.
  - `RightsChip` — label only, type tint background; `compact` = 유증 / CB / 매수청구.
  - **소멸주의보 strip** — the confirmed sub-brand element; craft panel, alert border, 10px hazard
    stripe on the left edge, filled 소멸주의보 badge.
- **Craft panel** (cosmos scope) = translucent dark card + 1px `--border-strong` + top-edge
  `--panel-glow` + 9px corner brackets. Used for the value card, countdown/stats card, 소멸주의보 and
  the board. The **ops variant (R7) strips all ornament**: opaque flat `#0e1a15` panels, no
  starfield/glow/brackets.
- Dates and D-days are **computed upstream in KST and delivered as absolute timestamps** — the browser
  only diffs against them and never derives a date. An instant is **sliced, never `Date`-parsed**, so
  a reader's timezone cannot move a KST stamp.

### What the implementation added to these conventions

- **`EstimateMarker` refuses an untagged estimate the way the server refuses to construct one**:
  `estimated` is a required prop with no default plus a runtime guard. Surfaces pass
  `figure.estimated` straight through — never a literal, never omitted.
- **`Citation` handles exactly the contract's three states and no fourth**: one `quote` → one panel;
  `parts` → **every addend rendered verbatim and separately** (never joined — the sum is printed in
  the filing nowhere, so a joined quote would fabricate a sentence); neither → **no chip at all**. It
  accepts a `span` it deliberately does not render: offsets are internal, like reason codes.
- **The estimate tag renders `추정`, not `「추정」`.** The 「」 are the documents' own quoting notation
  (they also wrap 「예정」, 「진행 중」 and whole sentences that cannot contain them), and the mark is
  specified as a *bordered* tag — the border is the enclosure. `[근거]` is the opposite case: written
  in square brackets every time and carrying only a dotted underline, so **its brackets are
  rendered**.
- **A past `D+n` is faint, never alert.** R1 only said "unfilled"; R3, R4 and R5 all settle the
  colour, and this is also what keeps an open ② from reading as 종료.
- **Primitives are extended by named, record-cited props — never by a local restyle.** The one case:
  `EstimateMarker size="landing"` renders R2's literal 10px in the footer sentence, because
  `0.56em` of a 12px line is 6.72px and an estimate mark nobody can read is close to an untagged
  estimate.
- **`.mono`'s size is a zero-specificity default.** A global `.mono {font-size: .95em}` and a
  CSS-module class are both specificity **(0,1,0)**, so source order silently flattened **23
  surface-stated sizes to one 12.825px**. The rule is now split: `.mono` keeps family +
  tabular-nums, and **`:where(.mono) {font-size: .95em}`** makes R1's ratio a default a stated size
  beats. **The durable rule: R1's "mono ≈0.95em of the surrounding sans" is a default *relationship*,
  and a size the record states for a surface governs over it.** Do not merge those two rules back
  together.
- **The reduced-motion convention is fixed once:** `data-motion="tick"` **freezes**,
  `data-motion="ambient"` **hides**, everything else is a fade that becomes a cut. The JS half
  (`useReducedMotion()`) is required wherever an interval must actually stop — CSS cannot stop a
  `setInterval`.
- **The ops idiom is a module, not a style opinion.** `components/ops/` states it once — opaque
  `#0e1a15` **as a local custom property, never added to the read-only token file**, 1px
  `--border-strong`, zero ornament, `min-width: 1180px` and **not one media query** — and exports the
  primitives every tab is built from. `CraftPanel` has no ornament-free variant and is not used
  there at all: R7's idiom strips exactly what that component adds, so it is a *different* panel.

## Surfaces, as built

| route | round | notes |
|---|---|---|
| `/` 관제 현황판 | R2/R2.1 + R3's board strip | cosmos backdrop (starfield generated **once, deterministically** — `Math.random()` would be a hydration mismatch every load), hero with the orbit rings, both anchor cards, 소멸주의보, the board with tabs/strips — **since P7 the ranked list is a 30-row display window** (below) |
| `/events/{rcept_no}` | R3 | all three rights types and every state the round draws: 철회 · 추후결정 · 기재 불일치 · 정정 이력 |
| `/stocks` · `/stocks/{corp_code}` | R4 | search redirects onto the corp_code handle; a miss stays put with the locked 검색 불일치 line; **since P7 the row also suggests candidates while the reader types** (below) |
| `/auth/login` · `/auth/reset` | R5-1/R5-2 | one panel, two modes, four states, the permanent PII inset |
| `/portfolio` · `/portfolio/notifications` | R5-3…R5-8 | the only gated route, plus 샘플 모드 at `?sample=1` |
| `/ops` + six tabs | R7 | desktop-only, read-only, behind the door |
| `/ask` | R6 | **P6**: a frameless chat directly on the page with a 340px right rail as its only panel and **no launcher**; ≤480px it is the whole AI 질문 surface |
| the launcher + widget | R6 | **P6**: chrome-level, mounted once, rendered on every reader route **except** `/ask`, `/ops` and ≤480px |
| the 질문 스트립 | R6 | **P6**: on event detail, preset chips from that event's gate-passing fields |

**The chrome** (R2) wraps every route: the 52px transparent bar with its nav slots — R2 signs **three**,
rendering their *superseded* labels (내 종목 조회 · 관제 현황판 · **AI 질문**), but **since P7 the bar
renders two: 관제 현황판 · AI 질문** (below) — the ≤480px sheet menu, the
white-on-dark footer, the vocky script seam and its three `data-vocky-trigger` elements — **and, since
P6, the AI 질문 provider plus the launcher/widget surface**, mounted once in the persistent client
layout so a turn survives navigation. R2 still forbids a floating button, and the launcher is the one
sanctioned occupant of that corner: measured across six reader pages, it is the **only**
`position: fixed` node, and there is none at all on `/ask` or below 481px.

**The wordmark is the delivered `mijual-logo-ring-white.png` rendered height-constrained through a
plain `<img>` — never `next/image`**, which would ship a re-compressed derivative of an asset that is
never re-encoded. The five binary assets (two wordmark PNGs, two ring logos, `PretendardVariable.woff2`)
are in the repo byte-for-byte and checksummed; **replacing one means a new export from the design
project, never a local edit**. Pretendard is verified *drawing* Korean prose in a real browser, not
merely 200-ing.

**One multiplication site, and it is structural.** `lib/holding.ts` does ⌊N × 배정비율⌋ × 증서
1주 이론가치 in exact `BigInt` decimal arithmetic — **no `Number()` on money or a ratio, ever** — and
returns **`value: null`** when the factors carry no `unit_value`, so money before 확정발행가 is
*unconstructable* rather than merely unrendered. 조회 and 포트폴리오 both import it, which is why they
cannot disagree (verified: 한화솔루션 500주 → 679,575원 on both).

**Korean strings enter the frontend in exactly one way: a surface's own `copy.ts`, with a citation
per entry.** A string with no citation does not belong in the frontend, and **inventing a Korean
string is a design change**.

### What P7 changed — the fix pass, surface by surface

Five of the eleven operator complaints were product changes; **four of those five are operator
overrides of the signed record**, each authorised by the phase's `intent.md` and scoped to the
override itself.

- **The nav is two slots, not three: 관제 현황판 · AI 질문.** `NAV_LINKS`
  (`components/chrome/copy.ts`) no longer carries the 내 종목 조회 entry / `/stocks`. R2 signs three
  slots and R5-6 explicitly *withdrew* a fourth, so a two-slot bar is a shape no round drew — it is a
  **P7 operator override**, scoped to the slot alone: no re-centring, no re-spacing, no new slot, no
  label rewritten. The surface stays reachable (the landing hero's own search *is* it, plus R3's
  detail link-out and the agent's link row), and `STOCKS_LABEL_KO` stays exported and in use by
  `LookupHeader`, `ask/links.ts`, `ask/copy.ts` and `lookup/copy.ts`. The same array feeds the desktop
  `<nav>` and the ≤480 sheet, so both dropped the row together (measured on the served HTML: `내 종목
  조회` 6 → 4 occurrences, `href="/stocks"` 2 → 0).
- **The landing board renders 30 ranked rows at a time.** `Board.tsx` keeps a `WINDOW_STEP = 30`
  window and discloses the next 30 through the record's **own** 펼치기 button (`EXPAND_KO`, the
  strips' `.expand` class) with a mono remaining-count in the strips' `N건` idiom — **zero new Korean
  copy**. It is a **display window, never a filter**: the served corpus, the ranked order and the
  whole-board `counts` are untouched (전체 still reads 488), a tab switch resets the window, and 12
  clicks still reach all 386. R2 specifies the sort, the row anatomy and the two strips but **no list
  length and no pagination control**, so P5.S3's note that "the design paginates nothing" **no longer
  describes the rendered page** — it still describes the API (the board is one request; expanding
  issues zero). Measured: the served HTML for `/` drops **701.9 KB → 369.2 KB** and the document from
  17,730 px to 3,047 px at 1440. The control is deliberately **not** a third pinned strip
  (`--surface-raised` + a hairline top is R2's marker for a *pinned* section) and carries **no
  `aria-expanded`** — it is incremental, not two-state, so the attribute would sit `false` and lie.
  The number 30 is a stated default awaiting the operator (`decisions`, D-24).
- **The two search rows are one component.** `components/lookup/SearchRow.tsx` is rendered by both
  the landing hero and R4's `LookupHeader`, each passing its **own** form/input/button classes — so
  R2's 560×52 row and R4's 48px row keep their signed geometry while the behaviour cannot drift into
  two behaviours. It is a WAI-ARIA combobox (`role="combobox"` + `aria-expanded`/`aria-controls`/
  `aria-activedescendant`, options `role="option"`) over `GET /stocks/suggest`: ~150 ms debounce, an
  `AbortController` per keystroke, **no request on mount or for an empty box**, ↑/↓ to move, Enter on
  a highlighted option → `router.push(stockPath(corp_code))`, Enter with nothing highlighted → the
  unchanged native GET submit, Esc/blur to close, nothing pre-highlighted. With JavaScript off both
  rows are still a plain `<form action="/stocks" method="get">` with no listbox. The panel is an
  **unsigned element built in the signed idiom** — radius 0, hairline border, the surrounding console
  field's own colours composited over `--paper` so a floating panel is opaque, fade-only motion, 종목코드
  in mono beside the name in sans, 44px options at 390 — and it mints **zero** Korean copy (an empty
  result renders nothing at all, because the submit already owns the 검색 불일치 sentence).
- **The hero's ring clip lives on `.orbits`, not `.hero`.** `.hero`'s `overflow: hidden` clipped the
  candidate panel (measured at 1440: the eight-option panel spans y 440→761 while the hero ends at
  732). `.orbits` is `position: absolute; inset: 0` of the hero — the **same rectangle**, measured
  identical after the move — so the rings are still clipped by the hero's own box exactly as R2.1 §3
  requires, while a panel hanging off the input can leave it. **No later slice may reintroduce
  `overflow: hidden` on `.hero`.**
- **Two reader captions no longer narrate storage** (`components/lookup/copy.ts`,
  `components/portfolio/copy.ts`): the 조회 보유량 caption is now 「서버 전송 없음」 and the 샘플/익명
  챙겼습니다 caption is 「본인 표시」. The rule the sweep applied: **strip the mechanism, keep the
  promise** — 「서버 전송 없음」 is R4 §3's literal kept **verbatim**, and no Korean was minted. The
  account captions 「본인 표시 · 계정에 저장」 and 「계정에 저장 · 마감 알림의 기준」 are unchanged,
  because where a mark or a count lives *for the reader* is their own fact. A comment-aware sweep of
  **346 Hangul string literals** (a real tokenizer, so doc comments are excluded rather than grepped
  around) plus JSX bare text, every `aria-label`/`title`/`placeholder`/`alt`, the document metadata
  and the Korean the backend composes found **exactly these two** and no third instance of the
  pattern. Verified with a revert-and-re-measure control: **no string a reader can see contains
  `localStorage`, `sessionStorage`, `브라우저 세션`, `이 브라우저`, or the bare word `브라우저`** —
  and the storage itself is unchanged, so every sentence in `security` about client persistence stays
  true. What changed is only that the surface no longer *says* it.
- **The 내 포트폴리오 surface's layout primitives, corrected to the ones the rest of the product
  already uses.** "Not organized" resolved to five measured slips against the record, all in
  `Portfolio.module.css`, none visible in the source: **(1)** the `// ` section eyebrow is
  **`--text-xs` (11px) + `letter-spacing: 0.08em`** — R2's "mono 11 `--ink-3` eyebrow", R3's
  "tracked", and what `lookup`/`event`/`landing/Anchor` already render; the portfolio was the one
  surface at 12px untracked. **(2)** a hairline-separated row list carries **no `gap`** — the
  `border` *is* the separator (R2 §Board: "9px v-pad, dashed separators"); a gap on top of the rows'
  own padding put the rule 28px from one neighbour and 16px from the other. **(3)** where a row's
  money statement sits beside 44px affordances, all of them align to **one 44px band**
  (`align-items: flex-start` + `min-height: 44px`), not to each other's centres — centring boxes of
  23.3/44/66.6px gave three different origins. **(4)** a header grid that must align with its rows
  needs every non-`fr` track content-independent (the trap below).
- **Focus indication is no longer one treatment for everything** — see §Accessibility.

### The AI 질문 surfaces (P6, re-cut by P9 / R16)

- **The conversation store is module-scoped, and that is the architecture — not a shortcut.** R6
  requires 「스트리밍 중 이동/전환에도 끊김 없음」, which rules out owning the fetch in a page
  component: a page unmounts on navigation and would take the stream with it. So the thread lives in
  `lib/ask.ts` (**no React import at all**), a provider mounted once in the client half of the
  persistent root layout hands it out through context, and views subscribe with
  `useSyncExternalStore`. The provider holds **no state**, so a frame arriving mid-stream re-renders
  the subscribed views and never the page.
- **One store, two views.** The widget and the `/ask` page are both views over the same store. **Do
  not build a second store and do not lift conversation state into a page** — the page arrives by
  calling the store's `close()`, which is 「위젯이 열려 있으면 닫고 리다이렉트」 for the nav slot, the
  footer link, the widget's external-link and a typed URL alike, and touches no turn.
- **Client persistence is one `sessionStorage` key, and `open` is deliberately not part of it** — a
  widget that reopened itself on reload would be unsigned behaviour. A restored in-flight turn is
  settled to the 중단 state, because the fetch died with the page. **Never `localStorage`** (that is
  R5's 샘플 포트폴리오 rule, a different surface with different signed rules) and never a cookie.
- **Scope has two setters, and the difference matters.** A page's *ambient* scope is applied when the
  surface opens and never overrides a 범위 the reader chose; pressing a preset chip *is* the reader
  choosing, so the strip uses the other one. The ambient binding is set on mount and cleared in the
  effect's cleanup, keyed by value rather than object identity — React runs a removed subtree's
  cleanup before the new subtree's effects, so navigating between two events lands on the second one,
  and a lost race would leave 전체 공시 rather than someone else's event.
- **The stream client is a pure function plus a fetch.** `decodeSse` is buffer-in / frames-out, which
  is why it can be tested against the real wire bytes: the actual SSE output of a scripted turn, fed
  back **in 3-byte chunks** (splitting frames *and* multi-byte Korean), reproduces the chips, the tool
  rows, the API-tier citation and the footer exactly. The endpoint path is hard-coded in `lib/api.ts`
  with every other path, and the CSRF header is set there once for all call sites.
- **The agent's own words are rendered verbatim from the wire and never restated on this side** —
  the tool fact rows, the refusal sentences and (since P9) the 진행 표시 sentence arrive as strings
  and are printed as strings. That is why `components/ask/copy.ts` holds **no status strings**: the
  five signed phrases are composed server-side and travel on the `status` frame with a machine-readable
  `phase` beside them. Everything else the surface says is transcribed into `copy.ts` with its
  provenance, and the unsigned *slots* reuse the nearest signed words rather than inventing any.
- **Pre-stream failures render the signed 중단 row and nothing else.** A rate limit, an invalid
  question or a dead service ends the turn with no blocks, one inset row and 재시도 — **no code, no
  English, no invented sentence, and no quota copy**, so a limit that is not shown is never implied.
  The same state renders a reader's 중지, a stream cut without a terminal, and a typed error, because
  the record writes exactly one sentence for 중단/오류.
- **The 의견 confirmation is printed by the surface, not the agent.** The tool returns a saved flag
  and its own fact row; the surface prints the signed confirmation off that row's success. A failed
  save adds nothing, because the row already *is* the retry line.
- **Nothing new is `position: fixed`** except the launcher and the widget, and both are
  right/bottom-anchored so neither can widen the document. The mobile input bar is
  `position: sticky`, and there is **no auto-scroll on the page** (the widget scrolls its own box;
  scrolling the document under a reader is the ambient motion R1 keeps off data surfaces).
- **Field order is one list, not two.** The detail page's row order and the preset chip order come
  from the same exported module, so a reordering cannot make them disagree.

**What R16 (P9) changed on these surfaces.** Same store, same two views, same rules above — the
answer got richer and the page got simpler.

- **`/ask` is one `max-width: 760px` column.** The 340 rail and its two-column grid are **deleted**.
  An empty page is the **start screen**, vertically centred (`min-height 560px`, 420 at ≤767): a
  greeting heading → the D1 intro → a composer with **no wrapping frame and no divider** (the input's
  own 1px only) → **four** question cards in two columns (one at ≤767), each of which sends its own
  sentence **verbatim** when pressed. A thread turns the page into 스레드 + a bottom-sticky composer
  with **「새 대화」** sticky at the column's top right — and 「새 대화」 exists **only when a thread
  does**, because there is nothing to empty otherwise. It is a store action: it empties the turns
  **and the `sessionStorage` copy of them**, aborts a turn in flight, and keeps the 범위 and the
  session handle. **No history list, no titles, no restore** — R6's ban stands.
- **Three retirements landed with their call sites**: the **범위 칩 and its ×** (the widget header is
  now exactly two icons; the store's `scope` stays and still scopes a widget opened from an event
  detail — it is simply never drawn), the **익명 줄** on both surfaces, and **「다시 질문」** (a
  completed footer ends at 이벤트 상세; 재시도 stays on interrupted turns alone).
- **The answer has a computed child order, not an assumed one**: 도구 흐름 → 구조화 블록 (the server's
  own order) → 프로즈 → 링크 → 진행 표시/끝맺음 → 푸터, one 12px gap, blocks always full width and never
  side by side. A pure, React-free splitter computes it from the store's arrival order, so it is unit
  tested; the renderer decides placement.
- **Five elements, one renderer, both views** (`components/ask/Answer.tsx` — **do not fork the widget
  and the page**): **StatusLine** (one transient line, 2px **dashed** left border against the tool
  row's solid — 실선 = 남는 사실, 점선 = 지나가는 상태 — `role="status"`, **no animation**; the
  spinner/typing-dot ban is not superseded); **ToolTrace** (flat at ≤3 rows or while the turn is live,
  folded to 「도구 N번 · 공시 M건 읽음」 + 자세히 at ≥4 once it settles — a *default*, never a stored
  memory, so a re-mounted trace folds again); **DataBlock** (three columns `minmax(0,40%) minmax(0,1fr)
  auto`, 36 % at ≤767, the **value cell alone** scrolls and the third column never scrolls out of
  view, 6-row fold, `margin-inline: -12px` at ≤767, and **no 3-column table anywhere**);
  **CalcBlock** (`--border-strong`, the `--live` mode word + the operation's name, inputs reusing the
  data-row schema, a 식 line, one slot that carries 계산 중 → 결과 → 오류 so the block does not jump,
  and **no alert colour or icon** on an error); and the **three-marker family** 추정 · 계산 · 미확인,
  all three wearing `EstimateMarker`'s **own** tag class so there is one geometry rather than a copy
  of its numbers, colour per family, `kind` with no default.
- **The 인용 칩 is the same component in three places** (프로즈 · 데이터 행 값 · 계산 입력) and gains
  only a *placement*. In a row the chip holds the fixed third column and its 인용 블록 opens **under
  the row, across the block** — measured necessity, not preference: with the panel inside that column
  the `auto` track grows toward the quote's max-content and the value column collapses to **zero**.
- **The store reduces by key, not by push.** A block wearing a `block_id` replaces the one already
  wearing it **at its own index** — replacing rather than remove-and-push, because a 도구 행 can arrive
  *between* a calculation's `pending` and `done` and a re-push would sail the settled block past it.
  A block with no id appends exactly as before. The transient 진행 표시 line is one live block dropped
  at the first prose block, at **every** terminal and on both terminal-less paths (a cut stream, the
  catch that carries 중지), and is **never** written to `sessionStorage` — filtered on
  `persistent === false` at both the write-through and the read-back, so a tab reloaded mid-turn never
  restores a progress line for a turn that stopped progressing.
- **소진 and 연결 끊김 are told apart by the terminal's `reason`, and nothing else.** Both are
  `aborted`; a budget reason draws dimmed prose + a folded 도구 흐름 and **nothing else** (no inset, no
  button, no new string), while R14's 「연결이 끊겼습니다」 inset + 재시도 stays for a disconnect, a
  중지 and a thread restored mid-turn.
- **근거 N건 is still the chip count**, and a calculation's **result** is never counted — a
  calculation **input**'s chip is, because it is a filing value the reader saw. Verified live: three
  distinct chips (one data row, two calc inputs, one of them reused in prose) and a footer reading
  근거 3건.
- **Known limit of the shipped 데이터 블록, measured across the whole 386-event corpus:** 372 filings
  produce **no block at all** and 14 produce **exactly one row** (always 신주인수권증서 상장·매매기간),
  with a longest value of 23 characters. Every gate-passing field's value is a composite dict, and the
  server may not spell one as a row without inventing a format the detail page already owns. So the
  6-row fold and the value-cell scroll have **no producer in the product** today. Recorded as an open
  operator question, not worked around.

## Accessibility / responsive rules

- **Mobile-first, breakpoints 480 / 768 / 1120**, content column max-width 1120px (card content ≈620px).
  Mobile hit targets ≥44px (sheet rows ≥48px).
- Mobile variants are designed per surface: sheet menu instead of nav links, two-line board rows,
  single-column lookup, and **AI 질문 as a full-width page with no widget or launcher on mobile**.
- **The admin panel (R7) is desktop-only by explicit operator decision** — no mobile layout and no
  media queries; a fixed min-width is allowed. It is the one surface exempt from mobile-first.
- Reduced motion is a floor, not an option (above). Focus ring: 2px `--focus-ring` — **on every
  focusable except a text-entry control**, since P7 (below).
- **Focus indication is split, and both halves are the a11y floor.** Every button, link, tab, chip,
  checkbox, radio and R2 §vocky trigger keeps the signed **2px `--focus-ring` at `outline-offset: 2px`**,
  unchanged. A **text-entry control** (`input` of a text-entry type, `textarea`, `select`) instead gets
  `outline: none` and brightens **its own hairline** on focus
  (`border-color: var(--field-focus-border, var(--ink-2))`, one rule in `app/shell.css`; the hero's
  dark console field sets the one hook, `--field-focus-border: rgba(163,196,180,1)`, because it is the
  only field not on the shared `--border-strong`). This is an authorised **P7 operator override** of
  the *treatment*, never of the *existence*: `--focus-ring` aliases `--r1`, the ① 유상증자 hue, and at
  `outline-offset: 2px` it painted 4px **under** the adjacent 조회 button, whose left edge is the
  input's right edge exactly (gap **0**, measured at 924.1 on `/` and 656 on `/stocks`, before and
  after — the button did not move). With `outline: none` the whole treatment lives inside the input's
  border box, so nothing can paint under the button. Measured state-change contrast of the rendered
  pixels: hero **4.01:1**, `/stocks` **3.40:1**, `/auth/login` **3.30:1**; focused hairline against
  the field interior 10.12 / 7.05 / 6.76 — all clear 3:1 both ways. **Never leave a text field with no
  keyboard-focus indicator at all.** Three implementation facts not to undo: the rule is **`:focus`,
  not `:focus-visible`** (a browser matches `:focus-visible` on a text input for a plain mouse click,
  but a *programmatic* focus may not — `/portfolio` 수정 autofocuses `SharesInput`); its specificity is
  **(0,1,1) on purpose** (every field paints its hairline from a (0,1,0) module class, so a
  `:where()`-flattened rule would lose both the `border-color` and the `outline: none` tie); and the
  selector is an **allow-list of text-entry types**, not a `:not(checkbox):not(radio)` deny-list, so a
  future `submit`/`file`/`range`/`color` input keeps the ring by default rather than silently losing
  its indicator. `--field-focus-border` is the hook for any future field whose hairline is not
  `--border-strong`/`--border-soft`: set it on the field's own class, inside that field's colour family.

## Engineering traps this build paid for

- **An inline `[]` or `{}` reaching an effect's dependency list will freeze the App Router.** Two
  fresh identities per render → render → effect → state → render, forever. **React warns nothing**
  (passive effects, not nested sync updates) and the page looks fine; what breaks is anything needing
  a transition to finish — `router.refresh()` fetches and never commits, and **every client
  navigation away from the page silently does nothing**. Shared frozen empties are the convention
  here. If a link or a refresh in this app ever "does nothing", look for that, not at Next.
- **A collapsed `Citation` still occupies its quote's width**, because the panel is a child of the
  same element and `max-content` includes a 300-character quote. Field rows give the chip its own
  grid area and the 환산 chain caps a step at 340px with its arrows as **real flex items** — an
  absolutely positioned arrow lands outside the container the moment the chain wraps.
- **⚠ Browser-check on `127.0.0.1` and the Tailscale origin — the operator's own — never on
  `localhost`.** This rule is the **inverse** of what this doc said before P7, and the inversion cost
  a whole fix phase. Next 16's dev-origin protection 403s two client chunks (and rejects the HMR
  socket) for any host not on its allow-list, so **hydration never completes**: the page renders
  (it is server-rendered) but nothing on it is interactive, and Next's own dev client then **reloads
  the tab** ~40 s later on its failed HMR reconnect, wiping whatever the reader was typing. `curl`
  gets 200 for the same URLs. The allow-list is built as `['**.localhost', 'localhost',
  ...allowedDevOrigins, hostname]` where `hostname` is the `-H` value, so `next dev -H 0.0.0.0`
  allows `localhost` and `0.0.0.0` and **not `127.0.0.1`** — the very URL `make stack-status` prints.
  Six separate operator complaints (dead 펼치기 toggles, a frozen countdown, a page that reloaded
  while typing, an AI 질문 composer that sent nothing, a missing launcher, an inert 챙겼습니다
  checkbox) were this one block. **`next start` does none of it** — the protection is dev-only, which
  is exactly why a production-build-on-`localhost` fidelity pass could never see it. `localhost` is
  the one origin that cannot show this defect class, so it is the one origin a check may not rely on.
  - **The seam:** `frontend/next.config.ts` carries `allowedDevOrigins` — a static list (`127.0.0.1`,
    `[::1]`, `**.ts.net`) plus **`MIJUAL_DEV_ORIGINS`**, comma-separated hosts, which `make web-up`
    fills from `tailscale ip -4`. Starting `next dev` any other way means setting that variable
    yourself or the Tailscale origin silently stops hydrating (`operations`, Environment Variables).
  - **Why the tailnet IP is not in the static list:** Next's `isCsrfOriginAllowed` compares **hosts
    only**, splitting on `.` and popping segments from the right, and `**` is legal only as the
    leftmost segment. So `**.ts.net` matches MagicDNS names, but an IPv4 literal can be matched only
    exactly or by whole-octet wildcards — and the only pattern covering the tailnet, `100.*.*.*`,
    would open all of 100.0.0.0/8 rather than Tailscale's 100.64.0.0/10. Verified still tight with
    the seam live: a `/_next/*` chunk fetched with `Origin: http://100.1.2.3:3000`,
    `http://192.168.1.9:3000` or `http://evil.example.com` still gets **403**.
  - The dev server **auto-reloads `next.config.ts`** (so a config edit goes live without a restart —
    and silently contaminates any "before" measurement taken after it), but **not** an env change:
    `MIJUAL_DEV_ORIGINS` needs `make web-up` (or `stack-down` + `stack-up`).
- **⚠ The App Router tree is wrapped in `React.StrictMode` under `next dev`** — `next.config.ts` sets
  no `reactStrictMode`, and Next's `define-env.js` turns that into `__NEXT_STRICT_MODE_APP = true` —
  so every effect runs **twice**. The shape to distrust: a **module-scope** guard claimed inside an
  effect plus a per-effect-run cleanup flag. Run 1 claims the guard, starts the work and its cleanup
  sets `live = false`; run 2 sees the guard taken and returns; the only answer on the wire is
  discarded **forever**. That is exactly why the chrome's account slot rendered an empty `<div>` in
  dev — one healthy `GET /api/auth/me` 200 per load, thrown away, so **the product looked like it had
  no login at all** — while `next start` runs the effect once and is perfect. Two facts make the fix
  (drop the cleanup flag) safe rather than lucky: the state it guarded is a **module store** that
  outlives every component, so an answer landing after a subscriber unmounted is still the answer the
  next subscriber wants; and `lib/session.ts` shares the **in-flight** probe, so the double
  invocation costs one request and a stale answer can never overwrite a newer one. Note the
  near-miss: `components/auth/useAuthState.ts` has the same shape but guards on **component** state,
  so StrictMode's second run re-fetches and it self-heals — do not "fix" that one.
- **⚠ Two CSS-module grids that name the same `grid-template-columns` can resolve different
  columns.** An `auto`/`max-content` track is sized by *its own* element's content, so a header row
  with an empty action cell and a data row with a filled one produce different `fr` leftovers — every
  column silently drifts (measured on 내 포트폴리오: 18.7px and 32.1px of label offset, at 1440 **and**
  768, invisible in the source because both elements name the same track list). A header that must
  align with its rows needs **every non-`fr` track content-independent**.
- **`npm run start` fails silently into its log with `EADDRINUSE`** if an older `next start` holds
  :3000, and the stale server then serves a manifest whose CSS chunks 500 — which looks exactly like
  "my fix did nothing". Kill the listener and confirm a CSS chunk returns 200 before believing any
  measurement.
- **Flattened-`innerText` proximity checks yield confident false failures.** Re-measure with a scoped
  selector before believing one. **P6 hit five more of the same class** — an `nth-child` selector
  matching a ring instead of a close glyph, a transparent overlay winning `elementsFromPoint`, a
  transform read mid-transition, a sticky bar measured on the wrong wrapper — each of which passed on
  re-measurement. The rule generalises: **a browser-probe FAIL is a hypothesis, not a finding.**
  **P7 produced nine more and not one survived a scoped re-measurement** — three of them harness bugs
  worth naming, because each makes a working product look broken: **(a)** a CDP
  `Input.dispatchKeyEvent` `keyDown` carrying `text` **already generates the keypress**, so
  dispatching a separate `type: "char"` afterwards fires a second one that the handler's
  `preventDefault()` on the keydown cannot suppress — it turned a working typeahead into a native GET
  form submit; conversely an Enter dispatched **without** `text: "\r"` fires no keypress at all, so
  the form's implicit submission never happens. Put the text on the `keyDown` and nowhere else.
  **(b)** a click at a coordinate **below the viewport hits nothing, silently** — every probe click
  must `scrollIntoView` first, and a viewport-relative rectangle read after that scroll then looks
  like a layout shift (compare `rect.y + scrollY`, not `rect.y`). **(c)** a control list must be
  **keyed, never indexed**: one click can add or remove controls (entering 샘플 mode adds two header
  controls; a 삭제 removes rows) and shift every later index.
- **Two Next behaviours exist only in the production build, and neither is configured by this app.**
  **(1) `<Link>` viewport prefetching is production-only** — revealing all 386 board rows through
  펼치기 issues **0** requests in dev and **366** `GET /events/{rcept_no}?_rsc=` 200s in prod. At
  *first paint* both runtimes issue 0 and render the same 30 rows, so the display window made the
  default landing cheaper in production too; the 366 is the cost of twelve deliberate clicks.
  **(2) `next dev` mounts a `NEXTJS-PORTAL` dev-overlay element that is one extra focus stop** —
  every dev surface measures exactly one invisible tab stop and every production surface zero, so an
  a11y focus audit run only in dev will always report one phantom.
- **The verification floor, established by P7 and exercised end to end.** A browser check is complete
  only when it runs **(a)** in `next dev` on the operator's own origins — `127.0.0.1` **and** the
  Tailscale host — **and** in a `next build && next start` production build; **(b)** at 1440 / 768 /
  **481 / 480** / 390, because the widget's signed boundary sits between the middle two; and **(c)**
  along the *functional* dimensions a fidelity pass alone never covers — every visible control clicked
  once and its effect recorded, the whole keyboard path walked for traps and invisible stops, liveness
  held for **≥60 s** (countdown) and **≥120 s** (typing; the dev reload lands at ~40 s, so a 30 s wait
  is a false negative), and **every difference between the two runtimes written down**. That last
  dimension is precisely the class of defect that let eleven reader-visible problems ship.
- **Build without disturbing the dev server by copying, not by stopping.** `next build` has **no
  `--dist-dir`** flag in 16.3.2 (`distDir` is config-only) and Turbopack **panics on a symlinked
  `node_modules`** pointing outside the project root, so the recipe is a real copy of `frontend/`
  (sources + `node_modules`, ~350 MB, a few seconds) into scratch, built and `next start`ed on
  another port. The running dev server and its `.next` are never touched and `make stack-status` is
  left exactly as found. **Never run `next build` against the `.next` the dev server is using.**
- **⚠ A dev proxy will gzip an event stream, and gzip buffers.** Next's router compresses whatever it
  forwards, `text/event-stream` included, so the reader saw the entire answer paint in one burst
  after a multi-second wait. **`curl` will not reproduce it** — curl sends no `Accept-Encoding` by
  default and a browser sends `gzip`. The fix is server-side (`Cache-Control: … no-transform`), not a
  client change; the lesson is to time the **wire** with `curl --compressed` and the **reader** with a
  `MutationObserver`.
- **⚠ A `Response.clone()` tee installed to capture raw SSE bytes buffers, and therefore lies.** It
  reported one 2 KB chunk where the wire had seven frames spread over seconds — which would have
  hidden the bug above entirely. Never time a stream through a tee.
- **`MIJUAL_API_ORIGIN` is read by `next.config.ts` at *build* time**, so `next start` serves whatever
  origin was set during `npm run build`. Rebuilding is part of repointing the proxy locally, and it is
  a real deploy note for P4.
- `lib/session.server.ts` may not import a module whose graph contains a React hook (`next/headers`
  and `useState` cannot meet) — keep the client/server session split.

## Open Questions

- ~~Concrete route paths~~ — **decided** (see Surfaces). Only the admin surface was constrained, and
  it stays at `/ops`, linked from nowhere in the reader chrome (measured).
- ~~Data fetching, state management, rendering strategy~~ — **decided**: a typed `fetch` wrapper, no
  state library, request-time rendering on every data-bearing route.
- ~~Binary assets~~ — **closed 2026-08-22** by the operator's export; all five are in the repo
  byte-for-byte and checksummed. There is still **no SVG wordmark and no favicon** — the ring PNG is
  2178×346 and re-encoding a delivered asset is not an implementation call.
- ~~The vocky observation API shape~~ — **decided in P5** and written back into the R7 record's own
  §6.3 section. But **vocky ships no embeddable widget script**, so the three signed triggers have
  nothing to bind to and `NEXT_PUBLIC_VOCKY_SRC` has no value to set today. Nothing was dropped and
  nothing was built for it: the widget UI is vocky's own (operator call). **P7 re-measured this across
  seven surfaces in both runtimes: the three `data-vocky-trigger` elements are the *only* genuinely
  inert controls in the whole product.** Everything else the operator called dead was the dev-origin
  block. No slice may invent a script URL — that is inventing a fact about someone else's system.
- **Copy the record does not contain** — each needs a signed decision, and none was invented: the
  not-found page's English sentence (the copy inventory holds no Korean 404 string); an expired
  재설정 link states nothing (`invalid_reset_token` is not one of R5's three signed lines); the vocky
  view's 「API shape 확정 대기」 now reads half a step stale; the footer's locked positioning sentence
  still says **내 종목 연결** while the hero H1 says 내 종목 조회 (R4's supersession is scoped to the
  nav label, and rewriting locked copy is a design change) — **P7 made this one and the hero H1 more
  visible, not less, by removing the nav slot that used to carry the label**, and left both alone; five **composed** labels (`비밀번호 재설정`,
  `이메일`, `비밀번호`, `계정 이전`, `© 미주알`); and the sample's signed **4건** subline above **five**
  live D-day rows.
- **Type and layout questions only the cards can settle:** Korean glyphs inside `--font-mono`
  elements fall to the OS Korean face, because the token stack carries no Hangul — every such element
  is one the record *draws in mono*, and R1's rule is "Korean **prose** never mono", which holds, so
  changing it means editing the landed `tokens.css`; `[근거]` (14px) and its DART link (17px) sit
  under the mobile 44px floor inside a signed row anatomy; the ① 환산 chain's 할인율 step fills its
  340px citation cap; the hero H1 renders 내 종목 조회 where R2's literal says 내 종목 연결; the PII
  inset renders 2 lines where R5's copy list says 3행; the 메뉴 button's hairline is this build's
  reading of "button"; and two signed R4 sentences render their dates in sans while the boundary
  panel renders its in mono.
- **The footer's 49.2억원 is a dated-pack figure, not a served one.** The presentation contract
  carries no gate-cost number and deriving one needs a module a request path may not import, so
  making it live is **backing work** (a persisted precomputation + a summary key) — a deferred job or
  a later fix slice, not a rendering change.
