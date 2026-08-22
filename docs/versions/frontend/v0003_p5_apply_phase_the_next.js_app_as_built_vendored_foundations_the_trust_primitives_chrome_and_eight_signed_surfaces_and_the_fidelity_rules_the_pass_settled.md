---
doc_id: frontend
version: v0003
created_at: 2026-08-22T18:14:22+09:00
source: P5.REVIEW
summary: P5 apply phase: the Next.js app as built — vendored foundations, the trust primitives, chrome and eight signed surfaces, and the fidelity rules the pass settled
previous: v0002_p3_signed_design_system_tokens_light_root_cosmos_dark_scope_type_motion_the_trust_primitives_and_the_design_record_with_its_supersession_chain
---

# Frontend

## Status

**The design is signed and P5 built it.** Seven Claude Design rounds (R1–R7), each closed by the
operator's literal signoff, are now a running Next.js app: chrome plus eight signed reader surfaces
plus the six-tab operator console, verified in a real browser against each round's own contract. This
doc records both the durable design truth those rounds fixed **and** the implementation truth P5
established. The AI 질문 agent surfaces remain **P6**'s; deployment remains **P4**'s.

The build ran under **RESPECT THE DESIGN**, and it held: **not one landed record was edited**. The
single write into `docs/reference/design/` in all of P5 was the R7 §6.3 vocky subsection the round
itself delegated to the build — **59 lines added, 0 changed**. Every nit found while building is
either a faithful-implementation fix in code or an operator question, never a record edit.

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

## Stack — as built

- **Framework:** Next.js **16.3.2** (App Router, Turbopack) on React **19.2.8** + TypeScript
  **5.9.3**, over the FastAPI backend. **No UI library, no CSS framework, no test framework, no
  linter** — the design system *is* `tokens.css`, and a framework theme would be a second source of
  truth for decisions R1 already made. SSE remains reserved for AI 질문 streaming (P6).
- **Styling:** `public/foundations/tokens.css` + `fonts.css`, **vendored byte-verbatim** from the
  landed records (diffed identical, only a provenance header prepended) and **served as static files,
  not bundled**. The directory mirrors the design project's own `foundations/` + `assets/`, so
  `fonts.css`'s relative font URL resolves **unchanged**. **They are read-only: a change in either
  file is a design change.**
- **Component system:** Claude Design's React reference implementations stay in the design project;
  the repo's `components/` are faithful implementations of that spec, not a dependency.
- **Data fetching:** a typed `fetch` wrapper (`lib/api.ts`), one function per route, paths hard-coded.
  No client library, no global state manager — the served payload *is* the state.
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
| `/` 관제 현황판 | R2/R2.1 + R3's board strip | cosmos backdrop (starfield generated **once, deterministically** — `Math.random()` would be a hydration mismatch every load), hero with the orbit rings, both anchor cards, 소멸주의보, the board with tabs/strips |
| `/events/{rcept_no}` | R3 | all three rights types and every state the round draws: 철회 · 추후결정 · 기재 불일치 · 정정 이력 |
| `/stocks` · `/stocks/{corp_code}` | R4 | search redirects onto the corp_code handle; a miss stays put with the locked 검색 불일치 line |
| `/auth/login` · `/auth/reset` | R5-1/R5-2 | one panel, two modes, four states, the permanent PII inset |
| `/portfolio` · `/portfolio/notifications` | R5-3…R5-8 | the only gated route, plus 샘플 모드 at `?sample=1` |
| `/ops` + six tabs | R7 | desktop-only, read-only, behind the door |
| `/ask` | — | **a bare shell: chrome only, no copy, no placeholder.** P6 replaces it |

**The chrome** (R2) wraps every route: the 52px transparent bar with the three signed slots rendering
their *superseded* labels (내 종목 조회 · 관제 현황판 · **AI 질문**), the ≤480px sheet menu, the
white-on-dark footer, the vocky script seam and its three `data-vocky-trigger` elements. **Nothing in
the chrome is `position: fixed`** and every surface measures **zero fixed elements** — R2 forbids a
floating button and P6's launcher needs that corner.

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

## Accessibility / responsive rules

- **Mobile-first, breakpoints 480 / 768 / 1120**, content column max-width 1120px (card content ≈620px).
  Mobile hit targets ≥44px (sheet rows ≥48px).
- Mobile variants are designed per surface: sheet menu instead of nav links, two-line board rows,
  single-column lookup, and **AI 질문 as a full-width page with no widget or launcher on mobile**.
- **The admin panel (R7) is desktop-only by explicit operator decision** — no mobile layout and no
  media queries; a fixed min-width is allowed. It is the one surface exempt from mobile-first.
- Reduced motion is a floor, not an option (above). Focus ring: 2px `--focus-ring`.

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
- **Browser-check over `http://localhost:3000`, never `127.0.0.1`.** Next 16's dev-origin protection
  403s two client chunks for a foreign host, so **hydration never completes** and the check silently
  measures an un-hydrated page — while `curl` gets 200 for the same URLs.
- **`npm run start` fails silently into its log with `EADDRINUSE`** if an older `next start` holds
  :3000, and the stale server then serves a manifest whose CSS chunks 500 — which looks exactly like
  "my fix did nothing". Kill the listener and confirm a CSS chunk returns 200 before believing any
  measurement.
- **Flattened-`innerText` proximity checks yield confident false failures.** Re-measure with a scoped
  selector before believing one.
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
  nothing was built for it: the widget UI is vocky's own (operator call).
- **Copy the record does not contain** — each needs a signed decision, and none was invented: the
  not-found page's English sentence (the copy inventory holds no Korean 404 string); an expired
  재설정 link states nothing (`invalid_reset_token` is not one of R5's three signed lines); the vocky
  view's 「API shape 확정 대기」 now reads half a step stale; the footer's locked positioning sentence
  still says **내 종목 연결** while the nav says 내 종목 조회 (R4's supersession is scoped to the nav
  label, and rewriting locked copy is a design change); five **composed** labels (`비밀번호 재설정`,
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
