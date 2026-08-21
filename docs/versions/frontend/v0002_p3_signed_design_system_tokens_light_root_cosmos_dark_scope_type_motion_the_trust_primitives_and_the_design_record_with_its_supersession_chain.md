---
doc_id: frontend
version: v0002
created_at: 2026-08-21T23:55:00+09:00
source: P3.REVIEW
summary: P3 signed design system: tokens (light root + cosmos dark scope), type, motion, the trust primitives, and the design record with its supersession chain
previous: v0001_bootstrap
---

# Frontend

## Status

**No frontend code exists yet — but the design does, and it is signed.** P3 was a design-only
phase: seven Claude Design rounds (R1–R7), each closed by the operator's literal signoff. This doc
records the durable frontend truth those rounds fixed. The build is the **apply phase** (P5 for
everything except the AI 질문 agent; P6 for the agent), and it builds under **RESPECT THE DESIGN**:
nothing approved may be dropped, simplified, restyled or "improved".

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

## Stack

- **Framework:** Next.js (frontend) over a FastAPI backend. **SSE is used only for AI 질문 streaming.**
- **Styling:** `foundations/tokens.css` (landed at `rounds/01-brand-foundations/output/tokens.css`,
  extended at `rounds/02-landing-chrome/output/tokens.css`) — CSS custom properties, no framework
  theme. `fonts.css` carries the font imports.
- **Component system:** Claude Design authored React reference implementations
  (`components/*.jsx` + `.d.ts` + `.prompt.md`) inside the design project. They are a faithful spec
  for the Next.js build, not a package the repo depends on.
- **State management / data fetching:** not decided in P3 — an apply-phase choice.

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
  only diffs against them and never derives a date.

## Accessibility / responsive rules

- **Mobile-first, breakpoints 480 / 768 / 1120**, content column max-width 1120px (card content ≈620px).
  Mobile hit targets ≥44px (sheet rows ≥48px).
- Mobile variants are designed per surface: sheet menu instead of nav links, two-line board rows,
  single-column lookup, and **AI 질문 as a full-width page with no widget or launcher on mobile**.
- **The admin panel (R7) is desktop-only by explicit operator decision** — no mobile layout and no
  media queries; a fixed min-width is allowed. It is the one surface exempt from mobile-first.
- Reduced motion is a floor, not an option (above). Focus ring: 2px `--focus-ring`.

## Open Questions

- Concrete route paths were left to the build (only the admin surface is constrained: a **separate
  path, e.g. `/ops`, linked from nowhere in the reader chrome**).
- Data fetching, state management, and the Next.js rendering strategy per surface.
- Binary assets (wordmark PNGs, ring logo, `PretendardVariable.woff2`) live in the Claude Design
  project, **not in the repo** — the apply phase must fetch them. No SVG wordmark exists.
- The vocky **observation** API shape is delegated to the apply phase (R7 §6.3); the vocky **widget**
  is vocky's own script and UI — style the trigger, never the widget.
