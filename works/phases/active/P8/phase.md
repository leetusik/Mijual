# Phase P8: Design polish pass — audit & polish every surface

_Intent: see [intent.md](intent.md)._

## Objective

Audit and polish the whole 미주알 product surface by surface — no new features. For each surface: the orchestrator walks it in the operator's runtime, reports what is dead/confusing/off, and asks the operator what's wrong; the operator answers how it should be fixed; a Claude Design round (design-cowork, one handoff + pending gate per surface) polishes it; an apply slice implements that signed round faithfully (RESPECT THE DESIGN) and verifies it in the operator's runtime — then the next surface. Opens with a small fix slice for the AskWidget t1 duplicate-key bug.

## Context

### The rhythm, in one place

Per surface, three steps, and the phase repeats them eight times:

1. **Walk, then ask** (the `co-work` slice's first half). The orchestrator opens the surface **in the
   operator's runtime** — `make stack-up`, `http://127.0.0.1:3000` in Chrome desktop on this Mac plus
   the tailnet URL from `make stack-status`, `next dev`; the production build additionally when
   behaviour could differ (`## Operator Runtime`, `docs/current/operations.md`) — and lists what it
   finds **as a first-time user**: dead/no-op controls, confusing bits, copy, interaction states,
   liveness over time, the mobile viewport. URLs and screenshots, not adjectives. Then the slice goes
   `pending` and asks the operator *"what's wrong, and how should it be fixed?"*.
2. **Design round** (the same slice's second half). The operator's answers become the round's
   `handoff.md` as **direction / labelled REFERENCE data** — Claude Design + the operator still make
   every visual decision. One `co-work` slice = one round = one handoff + one `pending` gate +
   read-back (DesignSync, main thread only) + land as-is + SIGNOFF + regroup.
3. **Apply** (the paired `implementation` slice, dispatched to `slice-executor-high`). Its `plan.md`
   is written **only after that round's SIGNOFF**, from the landed `build-prompt.md`. RESPECT THE
   DESIGN; fidelity **and** functional sweep in the operator's runtime and the production build;
   re-run the qa doc's whole `## Regression Checklist`; append Doc impact + Operator Questions here.

### Surface map — the eight surfaces, with real paths

Every path below was verified to exist at decomposition time. This is what each walk and each handoff
cites; a round names its surface's files rather than re-deriving them.

**Surface 1 — foundations/tokens + global chrome** (R8 · `P8.S2` → `P8.S3`)

- Tokens/type: `frontend/public/foundations/tokens.css` (62 lines) and `fonts.css`, linked as static
  files by `frontend/app/layout.tsx` together with the hoisted IBM Plex Mono CDN link;
  `frontend/app/shell.css` (global element rules, incl. P7's text-field focus rule).
- Chrome: `frontend/components/chrome/` — `SiteChrome.tsx`, `Nav.tsx`, `Footer.tsx`,
  `AccountSlot.tsx` + `useAccount.ts`, `Wordmark.tsx`, `VockyTrigger.tsx`, `VockyScript.tsx`,
  `copy.ts`, `index.ts`, and five `.module.css`.
- **The shared trust primitives live here too** — `frontend/components/{Citation,DDay,StateBadge,
  RightsChip,CraftPanel,EstimateMarker,LapseAlert}.tsx` + their `.module.css`, plus
  `frontend/lib/{copy,format,motion,routes}.ts`. Each is rendered by five to eight of the other
  surfaces (map under *Findings*), so **surface 1 is the round with the widest blast radius**.
- Designed by **R1** (`docs/reference/design/rounds/01-brand-foundations`, incl. its `tokens.css` +
  `fonts.css`) and **R2/R2.1** (`rounds/02-landing-chrome`, chrome + the `.cosmos` remap).
- Later overrides in force: **P7 nav 3 slots → 2** (관제 현황판 · AI 질문; `chrome/copy.ts`
  `NAV_LINKS`), **P7 focus split** (buttons/links/tabs/chips keep the signed 2px `--focus-ring`;
  text-entry controls get `outline: none` + their own brightened hairline via
  `--field-focus-border`, `app/shell.css`), and **P6** mounting the AI 질문 provider + launcher in
  the persistent client layout.

**Surface 2 — landing 관제 현황판 + board** (R9 · `P8.S4` → `P8.S5`)

- Route `/` — `frontend/app/page.tsx` + `app/page.module.css`.
- `frontend/components/landing/` — `Hero`, `Cosmos`, `Anchor`, `Countdown`, `EstimateValue`, `Board`,
  `BoardRow`, `LapseNotice`, `copy.ts` + six `.module.css`; the hero's search row is the **shared**
  `components/lookup/SearchRow.tsx` (also surface 4).
- Designed by **R2/R2.1** plus R3's board strip.
- Overrides: **P7 30-row display window** (`Board.tsx` `WINDOW_STEP = 30`, disclosed through the
  record's own 펼치기; a *display* window, never a filter — whole-board `counts` stay 488/50/422/16),
  **P7 typeahead** on the hero row, and **P7's ring clip moved to `.orbits`** — no later slice may
  put `overflow: hidden` back on `.hero`.

**Surface 3 — event detail ①②③ + trust states** (R10 · `P8.S6` → `P8.S7`)

- Route `/events/[rcept_no]` — `frontend/app/events/[rcept_no]/page.tsx`.
- `frontend/components/event/` — `EventDetail`, `Header`, `Fields`, `Offering`, `Convertible`,
  `Withdrawn`, `Corrections`, `fieldOrder.ts`, `copy.ts`, `Event.module.css`. Renders the shared
  `Citation` / `StateBadge` / `DDay` / `RightsChip` / `CraftPanel` / `EstimateMarker`.
- **Also hosts the AI 질문 질문 스트립** (`components/ask/QuestionStrip.tsx` + `Strip.module.css`),
  whose chip order comes from this surface's `event/fieldOrder.ts` — shared with surface 7.
- Designed by **R3**. The non-happy states are the product: 철회 · 추후결정 · 발행사 기재 불일치 ·
  정정 이력 · gate-blocked fields simply absent.

**Surface 4 — 내 종목 조회 + 놓친 돈 조회기** (R11 · `P8.S8` → `P8.S9`)

- Routes `/stocks`, `/stocks/[corp_code]`.
- `frontend/components/lookup/` — `LookupHeader`, `SearchRow` (+ `SearchRow.module.css`, **shared**
  with the landing hero), `StockView`, `HoldingStrip`, `Conversion`, `MissedMoney`, `RightsSection`,
  `LookupEmpty`, `copy.ts`, `Lookup.module.css`. Money is `frontend/lib/holding.ts` (exact `BigInt`,
  `value: null` before 확정발행가) — the same module 포트폴리오 imports.
- Designed by **R4**. Overrides: **P7 candidate panel** (a reader *choosing* a 종목코드, never a
  silent resolve; unchosen submits keep the four-tier `resolve_corp` behaviour and 검색 불일치) and
  the 보유량 caption trimmed to 「서버 전송 없음」.

**Surface 5 — auth (로그인 · 비밀번호 재설정)** (R12 · `P8.S10` → `P8.S11`)

- Routes `/auth/login`, `/auth/reset` (the emailed link lands with `?token=…`).
- `frontend/components/auth/` — `AuthPanel`, `ResetConfirmPanel`, `PiiInset`, `ConversionOffer`,
  `DeadlineOffer`, `SampleEntry`, `useAuthState.ts`, `copy.ts`, `Auth.module.css`; session plumbing
  in `frontend/lib/session.ts` / `session.server.ts` (tested by `lib/auth.test.ts`).
- Designed by **R5** (R5-1/R5-2): one panel, two modes, four states, the permanent PII inset.

**Surface 6 — 내 포트폴리오 + 알림 설정** (R13 · `P8.S12` → `P8.S13`)

- Routes `/portfolio` (**the only login-gated reader route**; 샘플 모드 at `?sample=1`) and
  `/portfolio/notifications`.
- `frontend/components/portfolio/` — `Portfolio`, `Holdings`, `Deadlines`, `AddHolding`,
  `SharesInput`, `CarryOver`, `SampleBanner`, `NotificationsView`, `copy.ts`,
  `Portfolio.module.css`.
- Designed by **R5** (R5-3…R5-8). Overrides: **P7's five layout-primitive corrections** (mono-11
  tracked eyebrow, no `gap` on hairline-separated rows, one 44px alignment band, content-independent
  header tracks) and the 챙겼습니다 caption 「본인 표시」.
- **Still open from P7 (Q8-A): the D-day rows' 144.7px ragged left edge / 584.6–761.3px empty middle
  at 1440** — the one remaining "not organized" symptom, deliberately not invented because R5 states
  no geometry. This surface's round is where it finally gets designed.

**Surface 7 — AI 질문 (런처 · 위젯 · `/ask` · 질문 스트립)** (R14 · `P8.S14` → `P8.S15`)

- Route `/ask` (`frontend/app/ask/page.tsx`), the chrome-mounted launcher + widget on every reader
  route **except** `/ask`, `/ops` and ≤480px, and the event-detail strip.
- `frontend/components/ask/` — `AskProvider`, `AskSurface`, `AskLauncher`, `AskWidget`, `AskPage`,
  `AskPageScope`, `Composer`, `Answer`, `InlineCitation`, `QuestionStrip`, `useAsk.ts`, `copy.ts`,
  `links.ts`, `presets.ts` + four `.module.css`. The conversation store is **`frontend/lib/ask.ts`**
  (module-scoped, no React import; `lib/ask.test.ts` covers it), SSE decoding is `lib/api.ts`.
- Designed by **R6**. `P8.S1` fixes this surface's `t1` duplicate-key bug **before** its round runs.

**Surface 8 — 운영 관제 admin `/ops`** (R15 · `P8.S16` → `P8.S17`)

- Routes `/ops` and its six tabs — `/ops`, `/ops/gates`, `/ops/accuracy`, `/ops/conversations`,
  `/ops/users`, `/ops/feedback` (`OPS_ROUTES`, `components/ops/routes.ts`); `app/ops/layout.tsx`.
- `frontend/components/ops/` — `OpsChrome`, `OpsTabs`, `OpsClock`, `Door`, `LockChip`,
  `LogoutButton`, `RowInspect`, `Overview`, `GateQueue`, `Accuracy`, `Conversations`, `Users`,
  `Feedback`, `Vocky`, `atoms.tsx`, `copy.ts`, `log.ts`, `server.ts`, `Ops.module.css`.
- Designed by **R7**. **Desktop-only by explicit operator decision** — the one surface exempt from
  mobile-first (no mobile layout, no media queries, a fixed min-width is allowed); read-only behind
  its own door, linked from nowhere in the reader chrome.

### Polish inventory — what each walk must cover

Derived from P3's **Design Inventory** (`works/phases/active/P3/phase.md` §Design Inventory) and the
qa doc's `## Regression Checklist` — **what to audit, not how to fix it**. Two items are
cross-cutting and belong to every round (P3 inventory 11 + 12), never to a slice of their own:
**Korean-only copy with a citation per string**, and **mobile-first behaviour** at the manifest's
mobile viewport.

1. **Foundations + chrome** — the token set as actually rendered under `.cosmos` (surfaces, borders,
   ink, brand, rights hues ①②③, urgency, type scale, 4px spacing, radius 0, no shadows, fades-only
   motion); Pretendard drawing Korean prose and IBM Plex Mono on every numeral (Korean prose never
   mono); the 52px bar, wordmark, the two nav slots, 로그인 / account slot, the `[의견]` trigger; the
   ≤480 top bar + sheet menu (rows ≥48px); the footer's provenance sentence, gate-cost sentence and
   disclaimer; **both halves of the P7 focus split on every focusable**; the reduced-motion floor;
   the three `data-vocky-trigger` elements (all no-op today — see Operator Questions).
2. **Landing** — hero H1 + console search + the mono stat line; starfield/orbit rings (generated once,
   deterministically) and their reduced-motion behaviour; both anchor cards; the countdown **watched
   ticking for a real interval**; 소멸주의보; the four board tabs with whole-board counts, the row
   anatomy (DDay/StateBadge/RightsChip), the 30-row window + 펼치기 and its reset on tab switch, the
   freshness 기준시각 chip; the search row **typed into and waited on** (debounce, ↑/↓,
   Enter-on-highlight vs. plain submit, Esc/blur, no request on mount); JS-off submit; two-line
   mobile rows.
3. **Event detail** — the ①②③ field rows in `fieldOrder`; the citation affordance (인용 원문 + span +
   `rcept_no` → DART 원문) and its ≥44px mobile hit; ▷ 추정 vs. fact; every trust state above; the
   질문 스트립 chips (order shared with the fields); the link-out to 조회; 정정 이력's "your D-day
   moved" story.
4. **조회** — search entry and the four-tier resolution incl. 검색 불일치; the candidate panel as a
   *choice*; 보유량 input → 환산 readout, `value: null` before 확정발행가; 놓친 돈 per-offering
   breakdown and its zero-result state; the 「서버 전송 없음」 caption; single-column mobile.
5. **Auth** — the panel's two modes and four states; validation, error and success copy (Chrome's own
   English validation bubble is a known gap, P7 Q12); the permanent PII inset; reset request →
   emailed link → `/auth/reset?token=…`; the conversion moments from the anonymous surfaces
   (`ConversionOffer` / `DeadlineOffer` / `SampleEntry`); 로그아웃; the whole keyboard path.
6. **포트폴리오** — the gated redirect when signed out; 샘플 모드 + `SampleBanner` + carry-over;
   holding add / edit (`SharesInput` autofocus) / delete; the D-day list's ordering and **its
   geometry** (P7 Q8-A); the empty 진행 중인 권리 cell (Q8-C); 지나간 마감 and the 챙겼습니다 flip
   (Q8-D/E); 알림 설정.
7. **AI 질문** — the launcher mark (hover scale, the sanctioned ambient motion, reduced-motion
   stopping *all* of it); widget open/close/scope vs. the page's ambient scope; the frameless `/ask`
   with its 340px rail; the composer **typed into and waited on**; streaming text, numbered chips,
   tool rows, footer; 중지 → 중단 → 재시도; the refusal states; the 의견 confirmation; **a reload
   with a restored thread** (this surface's `t1` bug); ≤480 = the page only, no launcher anywhere.
8. **운영 관제** — the door, login and logout; the six tabs and their density; `OpsClock` liveness;
   the gate queue rows + `RowInspect`; the accuracy report; 대화 로그 filtered by session and back;
   사용자; 의견; that it stays **read-only** (no unsafe method beyond login/logout); desktop-only, so
   no mobile expectation is a defect here.

## Decomposition

**17 middle slices, cut exactly as `intent.md` and `P8.DECOMP/plan.md` specify — a deliberate
operator override of the standard mixed-phase shape. There is no `P8.DECOMP2`.**

| slice | kind | risk | order | covers | depends on |
|---|---|---|---|---|---|
| `P8.S1` | fix | high | 1 | AskWidget `t1` duplicate-key bug (root cause verified below) | — |
| `P8.S2` | co-work | high | 2 | **R8** — surface 1: foundations/tokens + global chrome | — |
| `P8.S3` | implementation | high | 3 | apply R8 | `P8.S2` |
| `P8.S4` | co-work | high | 4 | **R9** — surface 2: landing 관제 현황판 + board | — |
| `P8.S5` | implementation | high | 5 | apply R9 | `P8.S4` |
| `P8.S6` | co-work | high | 6 | **R10** — surface 3: event detail ①②③ + trust states | — |
| `P8.S7` | implementation | high | 7 | apply R10 | `P8.S6` |
| `P8.S8` | co-work | high | 8 | **R11** — surface 4: 내 종목 조회 + 놓친 돈 조회기 | — |
| `P8.S9` | implementation | high | 9 | apply R11 | `P8.S8` |
| `P8.S10` | co-work | high | 10 | **R12** — surface 5: auth (로그인 · 재설정) | — |
| `P8.S11` | implementation | high | 11 | apply R12 | `P8.S10` |
| `P8.S12` | co-work | high | 12 | **R13** — surface 6: 내 포트폴리오 + 알림 설정 | — |
| `P8.S13` | implementation | high | 13 | apply R13 | `P8.S12` |
| `P8.S14` | co-work | high | 14 | **R14** — surface 7: AI 질문 (런처 · 위젯 · `/ask` · 스트립) | — |
| `P8.S15` | implementation | high | 15 | apply R14 | `P8.S14` |
| `P8.S16` | co-work | high | 16 | **R15** — surface 8: 운영 관제 admin `/ops` | — |
| `P8.S17` | implementation | high | 17 | apply R15 | `P8.S16` |
| `P8.REVIEW` | review | high | 9999 | phase review (already existed) | — |

### Rationale

- **Why no `DECOMP2`, although `design-cowork` normally requires one.** The two-pass rule exists
  because a design decides *what gets built*, so build slices cannot be known before the gate. Here
  the operator fixed the pairing itself: **each round has exactly one apply slice, its own, cut in
  advance and planned only after that round's SIGNOFF**. The unknown is the *content* of each apply
  slice, and content is what `plan.md` carries — written after the gate, never here. Nothing is
  pre-planned past a design gate, which is the invariant the rule protects. `intent.md` records the
  override verbatim ("design part a slice -> apply part a slice -> design part b slice -> so on").
- **The surface order is `intent.md`'s, unchanged**, and it is already the right one: it reproduces
  P3's own R1→R7 dependency direction. Foundations/tokens and the shared trust primitives are what
  every other surface composes, so they are decided first; the chrome rides with them because it is
  decided *by* placing it on a real surface (R2's own reason); landing → detail → 조회 follows the
  reader's path through the product; auth exists to serve 포트폴리오, so it precedes it; AI 질문 sits
  after the surfaces it cites; `/ops` is last because it is isolated, desktop-only and reader-invisible,
  so nothing else waits on it.
- **Eight surfaces exactly** — the operator's explicit choice. No round may be added, merged or split
  here. Whatever a landed round re-shapes goes in at a **fractional order** (`P8.S4.5`, …), cut by
  the orchestrator at that time.
- **Every slice is `--risk high`.** A `co-work` slice is never `low` (`design-cowork`, and the tier
  is main-thread-only anyway); every apply slice writes real cross-file code plus a fidelity +
  functional sweep in two runtimes; and `P8.S1` is not a one-liner either — the fix has to survive a
  restored-session repro in the operator's runtime and keep `lib/ask.test.ts` honest.
- **Rounds are numbered R8–R15**, continuing the record's R1–R7, and land in
  `docs/reference/design/rounds/08-…` … `15-…` beside `01-…`–`07-…`, in the **same** Claude Design
  project ("Mijual Design System"); `SIGNOFF.md` keeps accumulating. Suggested slugs (the round's own
  slice may refine): `08-polish-foundations-chrome`, `09-polish-landing`, `10-polish-event-detail`,
  `11-polish-lookup`, `12-polish-auth`, `13-polish-portfolio`, `14-polish-ask`, `15-polish-admin`.
- **All 17 folders are bare** — only `slice.json`. No `plan.md` is pre-filled, by anyone, ever; each
  is written by the orchestrator at that slice's own turn.
- `depends_on` is set on each apply slice → its round (advisory; `order` is what selects).

### What each kind of slice does

- **Design slice (`co-work`) — orchestrator-run inline, NEVER dispatched** (an executor has no
  `DesignSync`). Walk the surface in the operator's runtime and report findings as a first-time user
  → `pending`, ask the operator "what's wrong and how should it be fixed?" → write
  `docs/reference/design/rounds/<NN>-<slug>/handoff.md` with the operator's answers as **labelled
  REFERENCE direction**, the scope checklist, locked-vs-in-play, real paths/real data, the
  required-output manifest **including the `@dsCard` card set with the round's address on the group
  names** → `pending` while the operator designs → read back with `DesignSync` (`list_files` first),
  concreteness check, land AS-IS, write the SIGNOFF (operator's literal words, what supersedes what,
  token delta), regroup to retire the address. **No implementation code, ever.**
- **Apply slice (`implementation`) — `slice-executor-high`.** Planned from the landed
  `build-prompt.md` **after** SIGNOFF. Implements under **RESPECT THE DESIGN** (never drop, simplify,
  restyle or "improve" a designed element; build the backing if the design implies it). Then the
  **two mandatory yardsticks**: matches the record, *and* works as a product (every visible control
  does something; focus/hover/keyboard incl. browser defaults; liveness watched over a real interval;
  type-and-wait on anything live) — in the operator's runtime **and** the production build when they
  differ, at every viewport the manifest names. Re-runs the **whole** `## Regression Checklist`.
  Anything the record never settled is **catalogued on `## Operator Questions` below, never
  invented**; Doc impact goes on the running list, and only the review versions docs.
- **`P8.S1` (`fix`)** — the `t1` collision, below.

## Findings & Notes

### `t1` root cause — verified read-only at decomposition (2026-08-23)

Confirmed exactly as `intent.md` states, and it is worse than a React warning:

- `frontend/lib/ask.ts:252` — `let counter = 0;` at **module scope**, and `nextId()` (253–255)
  returns `` `t${counter}` ``. The module is re-evaluated on every full page load, so the counter
  restarts at 0.
- `hydrate()` (`ask.ts:438`) reads the `sessionStorage` thread through `readThread()` (207) and
  installs the restored turns — **already named `t1`, `t2`, …** — **without advancing `counter`**.
  It is called from `useAsk.ts:62` in an effect (idempotent, so StrictMode's double-effect is not the
  cause).
- So after a reload with a restored thread, the first `ask()` (`ask.ts:471`, `id: nextId()`) mints
  **`t1` again** → two `<div key={turn.id}>` with the same key in `AskWidget.tsx:96` and, identically,
  `AskPage.tsx:99`.
- **The id is not only a React key.** `patchTurn(id, …)` (`ask.ts:285`) rewrites **every** turn whose
  id matches, `history(exceptId)` (298) filters by it, and `retry(turnId)` (485) `find`s the **first**
  match. A collision therefore streams one answer into two turns and retries the wrong one — a real
  data bug, not just a console warning.
- Candidate directions for `P8.S1`'s planner (its call, not decided here): **(a)** seed `counter`
  from the restored turns at hydrate (e.g. max numeric suffix) — smallest change, keeps ids readable
  and testable, but leaves ids re-derivable and still per-module; **(b)** make ids collision-free at
  the source (`crypto.randomUUID()`, or a session-unique prefix) — no ordering assumption at all, but
  changes what is written into `sessionStorage`, so a **thread persisted by the old build must still
  hydrate** (there is no version bump: `Persisted.v` is `1` and `readThread` rejects anything else).
  Either way the fix must survive the **restored-session repro**: ask a question, reload, ask again.
- `frontend/lib/ask.test.ts` exists (four cases, no framework, run by `cd frontend && npm run smoke`
  → `node --test "lib/*.test.ts"`); `createAskStore` is exported, so a hydrate-then-ask case is cheap.
  Keep it terse — the repo rule is minimal high-value cases.

### Shared components — a polish in one round lands on other surfaces

Measured by usage site, not by memory. **Every one of these is decided in R8 (surface 1) and rendered
by the later surfaces**, so R8's blast radius is the whole product and every later round must be told
what R8 already fixed:

| primitive | rendered by |
|---|---|
| `CraftPanel` | landing (Anchor, Board), event (Header, Offering), lookup (LookupEmpty, HoldingStrip, RightsSection), auth (AuthPanel, ResetConfirmPanel, ConversionOffer), ask (AskPage), portfolio (NotificationsView, AddHolding), `LapseAlert` |
| `StateBadge` | landing (BoardRow), event (Header, Fields, Offering, Withdrawn), lookup (MissedMoney, RightsSection), portfolio (Deadlines, Holdings) |
| `EstimateMarker` (▷ 추정) | landing (EstimateValue), lookup (MissedMoney, Conversion, RightsSection), event (Offering, Convertible), portfolio (Deadlines), **chrome Footer** |
| `RightsChip` | landing (BoardRow), event (Header), lookup (RightsSection, LookupEmpty), portfolio (Deadlines, Holdings) |
| `DDay` | landing (BoardRow), event (Header), lookup (RightsSection), portfolio (Deadlines, Holdings) |
| `Citation` | event (Fields, Offering, Withdrawn, Corrections), lookup (Conversion, MissedMoney) — `InlineCitation` is the ask surface's own |
| `LapseAlert` | landing (LapseNotice) |

Two more cross-surface bindings: **`lookup/SearchRow.tsx` is one component rendered by both the
landing hero and `/stocks`** (each passing its own classes, so the two signed geometries survive while
the behaviour cannot fork) — a change to it in R9 or R11 hits the other surface; and
**`ask/QuestionStrip.tsx` lives on event detail** while its chip order comes from
`event/fieldOrder.ts`, so R10 and R14 overlap by design. `frontend/lib/holding.ts` is the single
multiplication site shared by 조회 and 포트폴리오 — 조회 and 포트폴리오 cannot be allowed to disagree
about a number.

### `tokens.css` is a landed design artifact, not a source file

`frontend/public/foundations/tokens.css` is **R2's landed `tokens.css` plus a five-line provenance
header and nothing else** (verified by diff: `0a1,5`, 57 → 62 lines). So **a token change in R8 is a
new `tokens.css` produced by the round and re-vendored the same way** — never a hand edit here and
never an edit to the record. Same for `fonts.css` (whose `@import` position bug is already handled by
hoisting the CDN link in `layout.tsx`, an apply-time to-do against a landed nit — do not "fix" the
vendored file).

### P7's open operator questions map onto P8's surfaces

P7 passed with **13 operator decisions routed to the operator and not yet answered**
(`works/phases/active/P7/phase.md` §Open Questions, Q1–Q13). They are precisely "the record never
settled this" items, which is what a polish round is for. **Each surface's walk should hand the
operator its inherited items alongside the walk's own findings** (see Operator Questions Q1):

| P7 question | surface / round |
|---|---|
| Q1 vocky has nothing to bind to; the three triggers are dead | 1 · R8 |
| Q2 how far "no selected focus" goes; Q9 five controls with no hover; Q10 focused hairline vs. panel edge; Q11 two different "mobile" boundaries (481px) | 1 · R8 (Q9/Q10/Q11 also touch 2 and 5) |
| Q3 is 30 the right board window? (one constant, `WINDOW_STEP`) ; Q5 live data refresh / polling | 2 · R9 |
| Q6 #4 the footer's 내 종목 연결 line, #12 the hero H1's name, #1 the English 404 | 1 · R8 (404: see Operator Questions Q3), 2 · R9 |
| Q6 #10 `[근거]` + DART link under the 44px mobile floor | 3 · R10 |
| Q7 ①–④ the four developer-vocabulary strings that are each a promise | 3 · R10 (② `SPARSE_CLOSING_KO`), 1 · R8 (③ `GATE_COST_TAIL_KO`), 6 · R13 (④ `carryOverKo`), 7 · R14 (① `API_TIER_KO`) |
| Q4 should a 챙겼습니다 row disappear?; Q8 A–E (row geometry, 기준 line placement, empty 진행 중인 권리 cell, 놓친 돈 상세 link on a checked row, caption visibility); Q6 #6 the sample's 4건 subline | 6 · R13 |
| Q12 Chrome's English validation bubble | 5 · R12 |
| Q13 the leftover `s19-fidelity@example.com` dev account | not a design item — operator housekeeping |

### Other facts a later slice will want

- **The design record is read-only.** Never edit anything under `docs/reference/design/rounds/*/output/`.
  Nits found while applying are apply-time to-dos in code or entries on `## Operator Questions`.
- **`SIGNOFF.md` decides precedence**: later rounds supersede earlier ones. R8–R15 will supersede
  parts of R1–R7 — so an apply slice reads `SIGNOFF.md` **first**, then its own round.
- **Zero Korean may be minted.** Every string enters through a surface's own `copy.ts` with a
  citation; inventing a Korean string is a design change and belongs to a round, not to an apply
  slice (`frontend/lib/copy.ts` holds only the shared primitives' strings).
- **`/ops` has no mobile layout on purpose**, and the reader chrome links to it from nowhere.
- **The 404 page is Next.js's default** (no `app/not-found.tsx` exists) — which is where P7 Q6 #1's
  English sentence comes from.
- The account slot's dev behaviour was P7's RC-B (StrictMode double-effect); the chrome walk in R8
  will exercise it again in `next dev`, which is the operator's own mode.
- Verification floor and probe traps are recorded in `docs/current/frontend.md`; the completion rule
  is in `docs/current/qa.md`. Both are worth re-reading before the first browser claim.

### `P8.S1` — the `t1` collision is fixed, and what it taught the ask surface (2026-08-23)

- **Fix shipped:** `nextId()` in `frontend/lib/ask.ts` now mints `` `t${SESSION_TAG}-${counter}` ``,
  where `SESSION_TAG` is 8 random chars computed **once per module evaluation = once per page load**.
  Nothing else in the store moved — `Persisted.v` stays `1`, `readThread`/`writeThread`/`settle`/
  `hydrate` are untouched, and a thread persisted with legacy `t1`, `t2` still hydrates (verified in a
  browser against a real `t1` thread). Measured before/after with the same harness on `127.0.0.1:3000`:
  **before** `ids ["t1","t1"]` + **9** duplicate-key messages; **after** two distinct ids, **0**.
- **`crypto.randomUUID` is secure-context only, and the operator's tailnet URL is not a secure
  context.** Measured: `http://127.0.0.1:3000` → `isSecureContext true`, `randomUUID function`;
  `http://100.77.164.42:3000` → `isSecureContext false`, **`randomUUID undefined`**, `getRandomValues`
  present. **Any later slice that reaches for `crypto.randomUUID`, `crypto.subtle`, geolocation,
  clipboard, service workers or notifications will find them missing on the operator's second access
  path** — and the manifest says both paths count. Prefer an API that works in both, or measure the
  fallback branch, because the tailnet is the branch that gets tested least.
- **A turn id is a lookup key, not only a React key** — `patchTurn` rewrites *every* match,
  `history(exceptId)` filters by it, `retry` takes the *first*. R14/`P8.S15` must keep any new
  minting/dedupe path pointing at exactly one turn. Verified functionally: 중지 → 재시도 on the newer
  turn re-streams that turn and leaves the older turn's answer byte-identical, in dev and in a
  production build.
- **React ships no duplicate-key warning in production**, so this whole bug class is invisible in
  `npm run start`: the only symptom there is turns silently duplicated or omitted. The production build
  was checked for that reason, not out of habit.
- **`GET /favicon.ico` → 404 on every reader page**, in both runtimes and on both origins (the repo
  ships no favicon). Pre-existing, unrelated to this slice — **an item for R8's chrome walk (surface 1)**,
  where it is the only console noise a first-time user's devtools shows.
- **`npm run build` rewrites the tracked `frontend/next-env.d.ts`** in place
  (`.next/dev/types/*` → `.next/types/*`), and `next dev` writes it back. Restore it with
  `git checkout -- frontend/next-env.d.ts` after building in the repo, or build in a copy the way
  `P7.S9` did. It is not a change any slice means to commit.
- The dev stack was left exactly as found (api pid 25177, web pid 13009, both answering `200`); the
  temporary `:3100` production server used for the prod check is stopped.

### R8 walk — surface 1 (foundations + chrome), 2026-08-23, operator runtime

Walked by the orchestrator in Chrome desktop at `http://127.0.0.1:3000` (signed in) and
`http://100.77.164.42:3000` (tailnet, signed out), plus a 390px mobile frame, `next dev`. First-time-user
findings, **not** judged against the record; the operator's answers at the `pending` gate decide what R8's
handoff carries.

1. **Three dead 의견 triggers** — header `[의견]`, footer `의견 보내기`, mobile-sheet `의견 보내기`: click → nothing
   (no vocky script loaded; `NEXT_PUBLIC_VOCKY_SRC` unset). Operator Questions Q2 / P7 Q1.
2. **No favicon** (0 `<link rel=icon>`, `/favicon.ico` 404 — generic tab globe), `<title>` is "미주알" on every
   route incl. 404, no `meta description` / `theme-color`.
3. **404 = Next.js default**: "404 / This page could not be found." in English; on desktop a white page on which the
   dark-theme wordmark disappears and nav/[의견] ghost; no footer. Operator Questions Q3 / P7 Q6#1.
4. **Footer typography/copy**: the tagline ("시장 전체의 소멸 임박 권리를 감시하는 관제 서비스 + 내 종목 연결") and the
   bottom row are IBM Plex Mono at 11px — Korean prose in the numeral font; the gate-cost sentence ("49.2억원 [추정]은
   할인율 인용이 게이트를 통과하지 못해 총액에서 제외했습니다") lacks a final period and reads as developer vocabulary
   (P7 Q7③, Q6#4); footer wordmark is not a link (header one is).
5. **No hover state** on the inactive nav slot ("AI 질문") or on `[의견]` — nothing changes under the pointer (P7 Q9).
6. **Account slot**: a truncated email ("swan…com") as a button with no menu affordance; the dropdown (내 포트폴리오 /
   알림 설정 / 로그아웃) hangs from the middle of the slot, aligned to neither the email nor `[의견]`. Esc closes it
   and restores focus (works).
7. **Focus**: buttons/links get the 2px `--focus-ring` (#8fb2e8, offset 2px) — on the hairline-bordered `[의견]` it
   reads as a double frame; the search field gets the brightened hairline, which stops at the 조회 button edge
   (P7 Q2/Q10).
8. **Mobile 390px**: `메뉴` opens an inline list that pushes the page down (no sheet/overlay, no backdrop), label stays
   "메뉴" (aria-expanded flips, no 닫기); rows 48px. Footer bottom row wraps with "AI 질문" orphaned on its own line;
   Next's dev badge covers "© 미주알" (dev only). Launcher absent ≤480 (by record).
9. **~120px empty band** between "내 포트폴리오는 어떻게 보이나 — 샘플로 열어보기 →" and the footer (desktop + mobile).
10. **Motion**: 252 animations running at rest on the landing (starfield drift/twinkle/shoot, orbit, countdown colon
    blink, launcher ring drift/band spin); one solid-dark frame during a fast scroll. Reduced-motion not testable
    from the walk harness — left for the apply slice's sweep.
11. No skip link (landmarks header/nav/main/aside/footer exist); header wordmark links to `/`.
12. Hydration/account slot fine on both origins in `next dev`; board/hero not walked here (surface 2).

Screenshots: session scratch `p8s2/r8-walk-desktop-landing-chrome.jpg`, `p8s2/r8-walk-mobile-footer-and-404.jpg`.

### R8 interview — operator answers (2026-08-23, `P8.S2` gate 1)

Recorded verbatim-in-substance beside the walk items; the handoff
`docs/reference/design/rounds/08-foundations-chrome/handoff.md` carries them as direction.

| walk item | operator answer | handoff effect |
|---|---|---|
| 1 dead 의견 | "the 의견 will be shown at the footer, and the stacked menu. not the bare nav. and you should connect vocky service … we should make feedback send design. no agent mcp linked yet." Key supplied out-of-band → `.env` `VOCKY_API_KEY` (project `mijual`, same key dev + prod), **never in the repo or the record** | nav `[의견]` dropped; footer + sheet stay; 미주알 designs its own feedback-send surface; server-side forward to vocky `POST /api/feedback` |
| 2 favicon | "leave the favicon for now. defer." | deferred job (orchestrator files at review / now) |
| 3 404 | "well, make 404 default." — read as: keep Next's default 404 | out of round; P8 Q3 answered |
| 4 footer | "remove the text and keep it simple and clean" | footer prose removed; minimal footer in play |
| 5 hover | "nav 의견 will be dropped, and current hover interaction of ai 질문 is enough" | no hover work; P7 Q9 answered for this surface |
| 6 account slot | "show the full email. and random genereated icon for the account. we could give a frame for the show that the email and the icon interaction possible" | full email + identicon + frame; supersedes R5 축약 이메일 |
| 7 focus | "." | unchanged |
| 8 mobile sheet/footer wrap | "you fix it as you want." | in play for Claude Design |
| 9 empty band / sample link | "we gonna add a secion for the portfolio. '포트폴리오' -> with no signin, just sample, with a sign, then show the user's portfolio. but i'm not sure we can call it 'portfolio'. you suggest if better term" | nav third slot → `/portfolio` (sample signed out, own signed in); label posed back (handoff §6 Q1) |
| 10 motion | "motion is fine so far" | unchanged |

**Operator Questions routing from this gate:** Q2 answered (above); Q3 answered (404 stays default); Q4 answered
for R8 — copy is in play **only** for the new feedback-send surface and the holdings-slot label, dated 2026-08-23;
Q1 answered in practice (inherited items were decided inside the round: P7 Q1, Q2, Q9, Q6#1, Q6#4, Q7③ closed by the
answers above; P7 Q10/Q11 untouched and still open).

### R8 landed spec — read back 2026-08-23 (`P8.S2` gate 2), awaiting literal signoff

Landed as-is under `docs/reference/design/rounds/08-foundations-chrome/output/` (`result.md`,
`build-prompt.md`, `Identicon.prompt.md`); cards stay in the Claude Design project (7 cards,
`⏳ P8.S2 · Chrome` ×6 + `⏳ P8.S2 · Components` ×1, manifest compiled). **Token delta: none** (remote
`foundations/tokens.css` byte-equal to the vendored R2 file minus its provenance header). What `P8.S3` builds:

- **Nav = AI 질문 · 보유 종목** (two links; 관제 현황판 link removed — the ring wordmark is that destination;
  no active underline on `/`); `[의견]` chip gone; R5-4 샘플 chip + 샘플 종료 retired (account slot has two
  states: anonymous / signed-in). Landing's "샘플로 열어보기 →" link + empty band removed.
- **AccountSlot**: full email (mono 12, 280px max, ellipsis + title) + 20px Identicon + hairline frame + ▾;
  menu right-aligned to the frame, opaque `#0e1a15`, rows **알림 설정 / 로그아웃** only.
- **NavMobile**: overlay sheet (no content push) + backdrop rgba(10,19,16,.72), bar button → × when open
  (aria-label stays 메뉴), rows AI 질문 / 보유 종목 → account block (28px identicon + email, 알림 설정,
  로그아웃 | 로그인) → 의견 보내기.
- **Footer**: prose removed (positioning, provenance, gate-cost, disclaimer); keeps wordmark h17 · 자료:
  금융감독원 DART 전자공시 · © 미주알 · 의견 보내기 · AI 질문, one row, Pretendard (no mono), 390px 3-row
  stack.
- **의견 보내기 surface (new, 미주알-owned)**: desktop 380px panel anchored above the footer entry, mobile
  full-width bottom sheet + backdrop; 6 states (idle-disabled / typing / sending-no-spinner / sent-202 with
  접수 번호 / failed-no-alert-colour + retry + kept input / closed); no contact field; 15 new Korean strings
  (build-prompt §7) enter `chrome/copy.ts` with R8 citation + `grounding/copy-inventory.md`. Browser →
  same-origin `POST /api/feedback {message}` → server → vocky `POST /api/feedback` with `source.product
  "mijual"`, `recorded_by "human"`, `channel web|mobile`, `target_type "surface"`, `session_id?`; key only in
  server `.env` (`VOCKY_API_KEY`, `VOCKY_API_BASE`); 401 = no retry.
- **Identicon** component (FNV-1a → hue ∈ {--r1,--r2,--r3,--live}, 5×5 mirrored grid, sizes 20/28/40,
  never --alert/--brand). Delete `VockyTrigger.tsx`(+css), `VockyScript.tsx`, `data-vocky-trigger`.

**Departures the record flags for the operator (result.md §6):** (1) the gate-cost and disclaimer
sentences leave the product entirely — the session proposes relocating them (landing bottom or an 이용 안내)
in a later surface round; (2) footer mono → Pretendard; (3) × glyph instead of a 닫기 string; (4) opaque
`#0e1a15` literal (candidate `--surface-opaque` token later); (5) 샘플 chip/종료 retired; (6) no alert colour
on failure; (7) identicon seed source = apply-time data decision.

### `P8.S3` — R8 applied: what the next surfaces inherit (2026-08-23)

**The chrome R8 signed is built and verified in the operator's runtime** (dev on `127.0.0.1:3000`
and the tailnet, plus a production build; 1440 / 768 / 481 / 480 / 390). Full evidence in
`slices/P8.S3/result.md`. What later rounds and apply slices need to know:

1. **vocky is behind Cloudflare, and it bans `Python-urllib`.** Measured 2026-08-23: the default UA
   gets **403 `error 1010 browser_signature_banned`** on every vocky path; the same request with a
   `User-Agent` gets 200/202. This had been **silently breaking the P5.S18 observation read** — the
   `/ops/feedback` tab was reporting 「unreachable」 for an unknown period. `mijual.web.vocky.USER_AGENT`
   now rides on both calls and the tab serves rows again (3, the test sends below). **R15 / `P8.S17`
   should walk that tab knowing it only just came back to life.** Anything else this repo ever calls
   over `urllib` against a Cloudflare-fronted host will hit the same wall.
2. **The 의견 surface is reusable and it is the chrome's.** `components/chrome/Feedback.tsx` exports
   `FeedbackDialog` (controlled: `channel`, `variant: "anchored" | "sheet"`, `onClose`,
   `returnFocusTo`) and `FeedbackEntry` (the footer's button + its anchored panel). A surface that
   wants its own 의견 entry mounts `FeedbackDialog` **outside** any container that can be
   `display: none`, passes the entry's ref for focus return, and gets the six states for free. The
   API is `sendFeedback(message, channel, {session, signal})` in `lib/api.ts`; failures branch on
   `code` via `FEEDBACK_NO_RETRY_CODES`.
3. **Body-scroll locks must go through `lib/scrollLock.ts`.** Two overlays now overlap on the same
   screen (the menu sheet and the 의견 bottom sheet) and a naive save/restore leaves the page locked
   after both close — measured, then fixed with a counted lock. Any future overlay that locks the
   page (a modal on 조회, a mobile filter panel) uses the same helper or reintroduces the bug.
4. **`Identicon` is a shared component with a pure core.** `lib/identicon.ts` (`identicon(seed)` →
   `{hue, cells}`) is the algorithm R8 pinned "so the mark matches across web and any later surface";
   `components/Identicon.tsx` only paints it, at 20 / 28 / 40. **R13 (`/portfolio` + 알림 설정) is the
   surface the record names for the 40px size** ("account surface") — use the component, do not
   re-derive the hash. Seed = the account email today (Q6's default).
5. **`/portfolio` no longer redirects.** An anonymous visit renders the sample (`SampleBanner`,
   `lib/sample.ts` unchanged); the account's own rows are still gated by the API's 401. **R13's walk
   will meet the surface in that state** — and the account menu no longer carries a 내 포트폴리오
   row, so the 2층's only chrome entry is the nav's 보유 종목.
6. **The footer's four sentences exist only in `copy.ts` now** (`POSITIONING_KO`, `PROVENANCE_KO`,
   `GATE_COST_*`, `DISCLAIMER_KO`), unrendered, waiting on Q5. A round that decides to relocate them
   should re-use the constants rather than transcribe them again.
7. **Three clearly-marked test rows are in the operator's vocky project** (`P8.S3 검증 …`,
   `request_id` `abc458cd…`, one un-captured, `b0071a6a…`). They are the only rows there. Deleting
   them is an outward write nothing sanctioned, so they were left — see Operator Questions.
8. **The favicon 404 is still the only console noise** on every reader page, in both runtimes and on
   both origins (deferred D5, operator-decided at the R8 gate).
9. **`npm run smoke` globs `lib/*.test.ts` only** — a component's testable core belongs in `lib/`
   (that is why `lib/identicon.ts` exists), or the test never runs.
10. **`copy-inventory.md` is generated and now carries a hand-written tail.** R8's build-prompt §7
    requires registering new surface copy there, but `scripts/export_design_grounding.py` builds the
    file from the Python side only and would drop the section. It is appended under a comment saying
    so; **a regeneration must re-append it** (or the exporter must learn to read the frontend's
    `copy.ts` files — an engineering question, not a design one).

### R9 walk — surface 2 (landing 관제 현황판 + board), 2026-08-23, operator runtime

Walked by the orchestrator in Chrome desktop at `http://127.0.0.1:3000/` (signed in) and
`http://100.77.164.42:3000/` (tailnet, signed out — same render), plus a 390px mobile frame, `next dev`.
Production build not re-run (everything here is client-side behaviour identical in both modes). Fresh
console after reload: 0 errors, 0 warnings on both origins. First-time-user findings, **not** judged
against the record; the operator's answers at the `pending` gate decide what R9's handoff carries.
Screenshots: session scratch `p8s4/r9-walk-desktop-board.jpg`, `p8s4/r9-walk-mobile-390.png`.

**Works as a first-time user expects (verified, no finding):** hero typeahead — no request on mount, type
「계양」/「삼성」 → candidates after the debounce (name + mono 종목코드), ↑/↓ highlights and wraps, Enter on a
highlight → `/stocks/<corp_code>` (계양전기 → `/stocks/00102618`), Esc closes and keeps the text, plain
Enter → `/stocks?q=…` (JS-off path: `<form action="/stocks" method="get">`); the countdown **ticks** over a
real interval (07 15 39 → 07 15 37 → … 07:10:40 minutes later, colons blink); the 30-row window, 펼치기
(+30), tab switch resets the window and keeps the scroll position; `↗` = DART 원문 (`noreferrer`,
aria-label 「계양전기 DART 원문」); freshness chip 「기준 2026-08-23 16:25 KST」, no stale notice; R8 chrome
sits correctly on the landing (two nav links, account frame + identicon, minimal footer, 의견 보내기 opens);
mobile 390px — two-line rows, abbreviated tabs (전체 488 / 유증 50 / CB 422 / 매수청구 16), cards stack, footer
stacks.

1. **Row click target is only the corp name.** `li.row` is inert (`cursor: auto`, no hover rule in any
   stylesheet); the only link in a row is `a.corp` (plus `↗` to DART). Clicking the key-date / D-day area
   of 계양전기's row did nothing. A first-time user reads the whole row as one item and expects the row to
   open the event. (Touches P7 Q9 — hover silence — the board rows have no hover state at all.)
2. **The board's numbers don't add up for a reader.** Tab 「전체 488」 and the countdown card say 488, but the
   list beneath shows 30 rows + a footer 「356건 펼치기」, then 진행 중 60건 + 추후결정 4건 → 420, and 68 are
   nowhere. Tab 「유상증자 신주인수권 50」 shows 14 rows + 2 추후결정 = 16. The tab counts are whole-board
   counts (R3), the rows are the countdown subset — nothing on the surface says so.
3. **「356건 펼치기」 is a remaining-count, not a total, and nothing says how many are shown.** After one
   펼치기 it reads 「326건 펼치기」 (30 → 60 rows). Reader can't tell whether 356 is the total, the remainder,
   or the window. (Inherits P7 Q3 — is 30 the right `WINDOW_STEP`.)
4. **The two strip 펼치기 buttons never change label** — after expanding 진행 중 (60 rows) or 추후결정 (2–4
   rows) the button still reads 「펼치기」; there is no 접기 and the only way back is a tab switch.
5. **Expanded strip rows don't align with the board's columns** — chip/corp/label columns sit ~14px
   further right than the board rows above (338 vs 324, 408 vs 394, 620 vs 634), so the expanded strip
   reads as a different table. 추후결정 rows show the key-date label 「신주인수권증서 매매 마감」 with **no
   date** beside it, then 「발행가 확정 전」 + 「추후결정」 — the empty date slot reads like a missing value.
6. **CB rows leave the right-middle of the row empty** — ~450px between 「전환청구 개시 2026-08-26」 and
   `D-3` on every CB row (422 of 488), because the 청약 + 발행가 cell exists only for 유증. At 1512px the
   board is mostly whitespace.
7. **D-day three-tier colouring has no legend** — D-2…D-6 alert red, D-9…D-27 white, D-37+ dim grey. The
   thresholds are invisible; first-time reading: "why is D-9 white but D-6 red?"
8. **소멸주의보 names 퓨쳐켐 as 「가장 빠른 청약 마감 2026-09-04」 while the board's first D-2 row is 계양전기**
   (three rows tie on 2026-09-04; the strip picks one, the board orders another). Minor, but the two
   disagree one screen apart.
9. **Countdown card row 「읽은 실적보고서 69건」** — no first-time user knows what an 읽은 실적보고서 is or why it
   sits next to 소멸 앞둔 신주인수권; the other three stats explain themselves.
10. **Mobile 390 line breaks**: hero subtitle wraps with a one-syllable orphan (「…조회합니 / 다」); the
    소멸주의보 strip breaks the mono date across lines (「2026-09- / 04」); the 진행 중 strip's 펼치기 drops
    under its sentence as a lone 32px button.
11. **Plain-Enter search with a prefix contradicts the typeahead.** Typing 「삼성」 shows 삼성에스디에스 /
    삼성제약 as candidates, but plain Enter lands on `/stocks?q=삼성` → 「'삼성'와 일치하는 종목이 없습니다」 —
    the candidates it just offered are gone, and the particle is wrong (삼성 → 「삼성과」). Surface 4 owns the
    page, but the entry is the hero.
12. **Typeahead panel covers the hero's mono stat line** (one candidate hides 「…감시 중 488건 · 30일 이내 마감
    32건」 partially) — expected for an overlay, noting it as the only overlap on the hero.
13. **Hover / focus on the four board tabs** — no hover change (P7 Q9); the tabs are `<button aria-pressed>`
    without `role="tab"` / tablist semantics; fine for a reader, noted for the record.

Inherited items for this surface, to decide at this gate alongside the above: **P7 Q3** (30-row window),
**P7 Q5** (live data refresh / polling — a deferred job if wanted), **P7 Q6 #12** (the hero H1's name 「내
종목 조회」 on a page whose board is the 관제 현황판 — the wordmark link is labelled 관제 현황판 and the
`/stocks` back-link reads 「← 관제 현황판」), **P7 Q9/Q10/Q11** where they touch the board (tabs hover, focused
hairline vs candidate panel edge, the 481px boundary between SearchRow and Board), and **P8 Q5** (the
gate-cost / disclaimer sentences R8 removed from the footer — the landing bottom is the proposed home).

### R9 interview — operator answers (2026-08-23, `P8.S4` gate 1)

Operator answered the inherited items first, then accepted the orchestrator's proposed default
for the 13 walk findings ("all go into R9 as fix — Claude Design decides how") with one
exception. Verbatim, then the reading the handoff carries:

| item | operator (verbatim) | reading → R9 handoff |
|---|---|---|
| P7 Q3 board window | "q3: 15" | `WINDOW_STEP` 30 → **15**, 펼치기 +15; design for a 15-row first screen |
| P7 Q5 live refresh | "q5: refresh" | **auto-refresh** the board data while the page is open (orchestrator's stated assumption: automatic, not a manual control — unchallenged); the visible behaviour is R9's, the interval/fetch is `P8.S5`'s; a build item, not a deferred job |
| P7 Q6 #12 hero H1 | "q6 #12: its intended." | 「내 종목 조회」 stays — locked |
| P7 Q9/Q10/Q11 | "q9-11 :idk" | left to the session — decide or explicitly leave, log which |
| P8 Q5 gate-cost / disclaimer | "p8 q5: drop." | **dropped, not relocated**; `P8.S5` deletes the constants; Q5 answered |
| walk 1–8, 10–13 | (default accepted) | fix — Claude Design decides how; 12 = leave; 11's `/stocks` side → R11 |
| walk 9 읽은 실적보고서 | "9. drop." | the countdown card loses the stat; card re-cut to three |

Handoff written: `docs/reference/design/rounds/09-landing-board/handoff.md`. Copy in play this
round, dated 2026-08-23: count/shown/remaining labels, 접기, any refresh-state label.

### R9 landed spec — read back 2026-08-23 (`P8.S4` gate 2) — SIGNED OFF 2026-08-23 ("sign off"); SIGNOFF.md R9 entry, cards regrouped to `Landing` / `Components`

Read back with DesignSync from "Mijual Design System" and landed **as-is** under
`docs/reference/design/rounds/09-landing-board/output/` — `result.md`, `build-prompt.md`, cards
`landing/{Board,BoardRow,BoardStrips,Anchors,HeroSearch,Refresh}.html` + `components/DDayTiers.html`
(groups `⏳ P8.S4 · Landing` / `⏳ P8.S4 · Components`), the shared geometry source `landing/r9-board.css`
(the column-plan contract) + row data `landing/r9-rows.jsx`, and the R9-session revision of
`chrome/AccountSlot.html` (see "outside the round" below). **No token change.** Concreteness check: every
decision carries geometry, state, and copy; nothing to send back.

What R9 decided (headline; `result.md` §1–§3 is the record):

- **Window 15/+15** (operator q3); footer re-cut to `{step}건 더 보기` + `남은 {n}건` + `처음 15건으로 접기`.
- **Row column plan** `76 · corp minmax(180,1fr) · 240 · 190 · 96` (no-extras panels `76 · 1fr · 300 · 96`),
  extras column decided **per panel (tab)**, fixed value columns, D-day flush right in its R2 slot,
  `min-height 44px`; tablet `72 · 1fr · 200 · 170 · 96`; 390 two-line row as R2. Walk 6's gap closes by not
  rendering an empty extras column.
- **Whole-row click = stretched link** on the corp anchor (`↗` stays DART, `z-index:1`); hover raised +
  corp underline, focus-within ring, press inset; changed-row edge `inset 2px 0 0 --live`.
- **Meta line** under the tabs — 「탭 숫자는 감시 중 전체 건수입니다 · 아래 목록은 카운트다운 {ranked}건 중 {shown}건」
  + the **D-day legend** (D-DAY · D-7 이내 · D-30 이내 · 30일 초과; R1 ladder kept, no simplification).
- **Strips**: `펼치기` ↔ `접기` (+`aria-expanded`); expanded rows on the board grid at the 24px start line;
  dateless row = label only in the key-date cell, 「추후결정」 in the D-day cell; 390 full-width 44px button.
- **Countdown card → three stats** in label-left/value-right rows (읽은 실적보고서 dropped, operator 9);
  **소멸주의보 tie rule** — `{n}개 종목` replaces the corp when several share the earliest 청약 마감, same in the
  countdown caption (needs `next_lapse.tie_count` or equivalent from `/board/summary`; until then the corp).
- **Auto-refresh visible contract** — chip-only surface (`갱신됨` beside a new 기준시각, persists to the next
  refresh), no spinner/button/text, changed rows edged, tab/window/strips/scroll/focus survive, hidden-tab
  pause, silent failure, stale = R2 handling, reduced-motion = no fade; interval is apply's (design assumes 60s).
- **Hero plain Enter** — 4-step rule (no highlight → Enter selects the first candidate; highlighted → go; exact
  match → go on first Enter; no candidates → `GET /stocks?q=`); 390 `word-break: keep-all` + subtitle
  `text-wrap: balance`, all mono values `nowrap`.
- **P7 Q9** tabs hover = `--ink-1` + 2px `--border-strong` underline (role="tab" not introduced); **P7 Q10**
  closed as no-change; **P7 Q11** board controls 36px (≥768) / 44px (≤767), the 481px seam retired.
- **Copy in play, dated 2026-08-23 — 14 new constants** (`build-prompt.md` §9: `TAB_NOTE_KO`, `shownLine`,
  `moreKo`, `remainingKo`, `collapseToFirstKo`, `COLLAPSE_KO`, `REFRESHED_KO`, four `LEGEND_*_KO`,
  `tieCountKo`); deletions `STAT_REPORTS_KO` + the gate-cost/disclaimer constants (P8 Q5).

Outside the round (recorded, not applied by `P8.S5`): the operator asked the session to add a **「의견 보내기」
row to the account menu** (알림 설정 / 의견 보내기 / 로그아웃) — `chrome/AccountSlot.html` revised in the
project and landed beside R9's output; `build-prompt.md` §12 names it for "the next chrome slice". No new
copy (`FEEDBACK_OPEN_KO`). Routed as Operator Question Q12 below.

### `P8.S5` — R9 applied: what the landing now is, and what the next surfaces inherit (2026-08-23)

**R9 is built as signed and verified in the operator's runtime** — `next dev` on `127.0.0.1:3000` and
the tailnet, **plus a production build** on `:3100`; 1512 / 1280 / 1119 / 1024 / 802 / 768 / 767 / 481 /
390. Every §11 box passes. Full evidence in `slices/P8.S5/result.md`. What later rounds and apply
slices need to know:

1. **The board's geometry is now `r9-board.css` ported into `Board.module.css`, and the one rule that
   holds it together is that *every row is its own grid container*.** A track that sizes to content
   (`auto`) therefore resolves per row and the columns stop lining up — walk finding 5's misalignment.
   So value columns are fixed widths, only 회사 flexes, and `data-extras` is a **panel-level**
   attribute on the `<ol>` (the tab's ranked rows **and** both strips), never per row. Measured: the
   D-day right edge is identical for every row of a panel at every one of the nine widths.
   `minmax(0, N)` (R9's numbers with a shrink floor) rather than a bare `N` is deliberate — bare fixed
   widths overflow the padded panel below ~802px, which is `P5.S19`'s measured 41px scrollbar bug.
2. **The refresh hook is reusable in shape, and it lives inside `Board` on purpose.** `page.tsx` keeps
   its server fetch as the first render, the client re-reads only `/board` (`getBoard()` through the
   same-origin rewrite) every **60 s** (`REFRESH_INTERVAL_MS`, one constant, Q10's assumption), and
   the pattern any later live surface should copy is: compare the **served** `as_of` and do nothing at
   all when it has not moved; keep the reader's state (tab / window / disclosure / scroll / focus) in
   component state and never rebuild it from the payload; key rows by a **served id** so the DOM
   survives; pause on `document.hidden` and read once on becoming visible; fail silently. A surface
   that remounts the countdown fails the "seconds do not jump" test — the tick is a sibling of the
   refresh, not a child of it.
3. **`next_lapse.tie_count` now ships** (`/board/summary`, derived from the ordered pending list, added
   only when `next_lapse` exists). Live value today is **3** — the three-way 2026-09-04 tie the walk
   found — and the 소멸주의보 says 「3개 종목」 instead of naming 퓨쳐켐. Any surface that names "the
   soonest" of a tied set should say the count rather than pick one; the field is there now.
4. **`SearchRow`'s Enter rule is R9's and R11 must keep it**: no candidates → the plain GET submit
   (the JS-off path); a highlight → go; an **exact** 종목명/종목코드 → go on the first Enter; otherwise
   Enter **selects the first candidate** and navigates nowhere. It is one shared component with
   `/stocks`, so R11 changes the *page*, not this rule.
5. **R2's 「a 접기 label is copy nobody signed」 is dead** — R9 signed 접기, and the same reasoning
   (a label that reads the state, with `aria-expanded` agreeing rather than standing in) now applies
   to the board's window footer. The chrome's 메뉴 button still carries R2's original rule; a later
   chrome round can revisit it, but nothing in R9 did.
6. **P8 Q5 is executed, not deferred**: `POSITIONING_KO`, `PROVENANCE_KO`, `GATE_COST_*` and
   `DISCLAIMER_KO` are **deleted** from `components/chrome/copy.ts` (nothing imported them). The
   same-named constants in `lookup/copy.ts` and `event/copy.ts` are those surfaces' own, still
   rendered, untouched. The sentences survive in the design record; they are simply not in the product.
7. **`copy-inventory.md` now carries two hand-written tails** (R8's and R9's), and both say so: the
   exporter builds the file from the Python side only, so **a regeneration drops them and they must be
   re-appended** (or the exporter must learn to read the frontend's `copy.ts` files — still an
   engineering question, not a design one).
8. **Landing prose is `word-break: keep-all` from `<main>` down** (`app/page.module.css` `.landing`),
   the hero subtitle is `text-wrap: balance`, and every mono value on the surface is `nowrap`. The
   other surfaces are **not** covered — a later round that wants Korean line breaking fixed on event
   detail / 조회 / 포트폴리오 has to say so, and can then decide whether the rule belongs in
   `app/shell.css` for everyone.
9. **The API runs without `--reload`**, so a change under `src/mijual/**` needs a restart before the
   browser can see it: api pid 65992 → **3182** (web 13009 untouched). Same trap `P8.S3` hit.
10. **The favicon 404 is still the only console noise** on the landing, in both runtimes and on both
    origins (deferred D5). 0 page exceptions, 0 React warnings anywhere in this slice's runs.


### R10 walk — surface 3 (event detail ①②③ + trust states), 2026-08-23, operator runtime

Walked in `next dev` on `127.0.0.1:3000`, Chrome desktop 1456px + 390px (same-origin iframe), while
`P8.S5` ran (read-only). Pages: ① 계양전기 `20260724000546` · 한화솔루션 `20260720000067` · 경남제약
`20260623000409` (추후결정) · 썸에이지 `20260805000454` (철회) · ② 대동기어 `20251016000315` · 풍전약품
`20250930000508` · ③ 세기상사 `20260713000345` (+ superseded `20260623000277`) · 아시아나항공
`20260713000482`. Non-exposable by contract → 404: 한솔테크닉스 `20260709000212` (flagged), 파이온엑스
`20260722000285` (incomplete), 대한광통신 `20260306000600` (실적보고서 rcept). Console clean on every
exposable page. No horizontal overflow at 390. Handoff: `docs/reference/design/rounds/10-event-detail/handoff.md`.

Findings (first-time-user eyes; R3-deliberate items marked):

1. **환산 블록 broken at 390** — chain cells stack but the `→` connectors remain: an arrow floats after
   「발행가 확정 전」, another hangs before 「배정비율」; 한화솔루션 crams 「→ 증서 1주 이론가치 5,525원 추정 →
   배정비율 0.2465120994」 onto one line.
2. **`[근거]` 32×15 and rcept mono links 92×17 on mobile** — under R3 §Mobile's own ≥44px floor (P7 Q6 #10
   confirmed, measured). No open/closed state on the trigger when the quote panel is open.
3. **「정정 이력」 reads no state** — label unchanged while the rail + diff are open below (the strip-toggle
   problem R9 fixed on the board).
4. **Diff table at 390** — 정정 전/정정 후 two squeezed columns; mono dates split 「2026-07- / 06」.
5. **Header meta at 390** — 「접수번호 … · 최초 공시 …」 then 「· 정정 반영」 alone with a dangling 「·」.
6. **Closed ① window has no state word** — 계양전기 shows 「거래 가능 · 마감 D-2」 (live); 한화솔루션 D+44 shows
   only bare dates, while ③ rows wear 「기한 지남」 chips. Inconsistent closed-window rule.
7. **Chain arrows read as flow**, are separators; 할인율 cites `[근거]`, 배정비율 has none.
8. **② fact strip cites as a whole** (one rcept ↗ under six API values) vs per-field `[근거]` below — the
   API-tier vs 본문 provenance difference is not legible; 「보호예수 / 전매제한 해제일」 stacks a date and a
   sentence.
9. **철회 page evidence line** runs on: 「정정사항  유상증자 결정  유상증자 결정 → 유상증자 철회」 + lone `[근거]`.
10. **Field-absent ③ (아시아나)** — 「현재 버전 공시에 없음」 as plain text in the countdown slot, no badge; the
    page is one field + the 정정 band. (R3 literal locked; presentation open.)
11. **Two link-outs, two affordances** — 「내 포트폴리오에 담기 →」 text link (header, R5-2 → `/portfolio?add=`)
    vs 「내 보유량으로 환산 →」 outlined button (→ `/stocks/{corp}`). Hierarchy to confirm.
12. **Section eyebrows `// 일정` `// 발행 조건` are not headings** — no h2/h3 below the h1 (a11y outline).
13. **질문 스트립** — placement/hit height only; its design is surface 7.
14. **390 header stack** — countdown → 담기 → 「DART 원문 ↗」 (44px full-width) → strip → 환산; R3's stack
    with R5-2's line inserted; confirm.
15. *(R3-deliberate)* **404 page is the Next.js default** — English 「404 / This page could not be found.」,
    faded nav, empty account frame — R3 wrote state copy and no 404 copy (`page.tsx` comment). → Q15.
16. *(R3-deliberate)* **배정비율 to 10 decimals** (`0.2314082845`) — §6-1 "full 10 decimals". → Q16.
17. *(R3-deliberate)* **Superseded URL** `/events/20260623000277` silently renders the current version
    (header 접수번호 `20260713000345`, rail marks 07-13). → Q17.
18. Sparse ② closing line (`SPARSE_CLOSING_KO`) renders only for ② with 0 본문 fields (e.g. 라온텍
    `20250818000222`) — P7 Q7 item; not seen broken, listed for the session's sparse-② card.

Interview default (as at R9): every finding → fix, Claude Design decides how; Q15–Q18 are the
operator's. The handoff carries the orchestrator's defaults (Q15 design a Korean not-found, no reason
why; Q16 keep the value, presentation in play; Q17 leave, log; Q18 literals stay).


### `P8.S5.5` — the account menu's 의견 row, and one lock it uncovered (2026-08-23)

R9 build-prompt **§12** (an operator instruction given inside the R9 session, drawn in
`chrome/AccountSlot.html`) is executed, closing **Q12**: the desktop account menu is
**알림 설정 / 의견 보내기 / 로그아웃**, and the new row opens R8's own `FeedbackDialog` — no new
surface, no new copy, no restyle. Verified signed-in on `127.0.0.1:3000`, the tailnet origin and a
production build. Evidence in `slices/P8.S5.5/result.md`. What later chrome work needs to know:

1. **`FeedbackDialog` now takes `placement?: "above" | "below"`, defaulting to `above`.** R8's anchored
   panel hangs *above* its entry (`.asPanel { bottom: calc(100% + 10px) }`) because the only entry it
   drew was the footer. A future entry point in the **top bar** must pass `placement="below"` (the
   mirror rule `.asPanel.asPanelBelow`, `top: calc(100% + 10px)`, gated `@media (min-width: 481px)`);
   the footer and the nav sheet pass nothing and are unchanged. The override wins **by specificity,
   not source order** (`.asPanel.asPanelBelow`) — the convention `Nav.module.css` states for
   `.sheet.sheetOpen`, and the reason the rule lives in `Feedback.module.css` rather than reaching
   across CSS-module files.
2. **An overlay mounted inside `.utility` disappears at ≤480 — and its body-scroll lock does not.**
   Measured at 400px before the fix: the account panel was in the DOM with `offsetParent === null`,
   a zero-size rect and `body { overflow: hidden }`, i.e. an unscrollable page with nothing on screen
   to close. `AccountSlotDesktop` now closes the panel when `(max-width: 480px)` matches. Any future
   overlay hung off a **breakpoint-hidden** container needs the same close, on top of `P8.S3` note 3's
   counted lock.
3. **Two 의견 panels can be open at once** (footer's + the account menu's = 2 `[role=dialog]`; Esc
   closes both). Each entry point owns its own state and the record never asked for a single-owner
   rule, so nothing was invented — see **Q19**.
4. **The 의견 send was deliberately not re-exercised** from the new entry: it is R8's path, proven end
   to end by `P8.S3`, and another send would add another row to the operator's real vocky project
   (Q9). The new row hands `FeedbackDialog` the footer's exact props (`channel="web"`).
5. **A signed-in browser check costs nothing durable.** The recipe `P8.S3` used still works and is now
   scripted: create a throwaway account through 계정 만들기, do the checks, delete it through
   알림 설정 → 계정 삭제 in the same run. If a run dies mid-way, the orphan can still be removed through
   the product — 재설정 요청 puts the link in `var/stack/api.log` (`ConsoleMailer`), and the reset lands
   already signed in. The database was left exactly as found (accounts 14 and 25 only).

### R10 landed spec — read back 2026-08-24 (`P8.S6` gate 2) — SIGNED OFF 2026-08-24 ("sign off"); SIGNOFF.md R10 entry, cards regrouped to `Detail` / `Components`

Read back with `DesignSync` from the "Mijual Design System" project and landed **as-is** under
`docs/reference/design/rounds/10-event-detail/output/`: `result.md`, `build-prompt.md`,
`detail/{Header,Offering,Convertible,Procedure,Fields,Corrections,States}.html`, `detail/r10-detail.css`
(geometry source of truth), `detail/r10-parts.jsx` (shared parts + walked real rows),
`components/Citation.{html,jsx,d.ts,prompt.md}` (the component re-cut). 8 cards under
`⏳ P8.S6 · Detail` / `⏳ P8.S6 · Components`; manifest in sync; **token delta none**.

What the session decided (binding once signed — RESPECT THE DESIGN in `P8.S7`):

- Walk 1–14 all fixed (see `result.md` §2): 환산 chain = hairline instrument cells, **no arrows**
  (desktop column-flow / ≤767px row-flow, label-left value-right, 44px cells); `[근거]` word kept,
  hit 32px desktop / **44px ≤767px**, open state on the trigger (`--live-tint` + `aria-expanded`);
  「정정 이력」 ↔ **「접기」** + ×; 정정 전/후 and 철회 정정사항 = **two tagged sides** (arrow column
  retired); header meta `nowrap` items + `::before` separators, ≤767px separators off + 「정정 반영」
  chip; closed window = **「기한 지남」** chip (① closed · ③ steps), ② past-open stays 「진행 중」, ②
  pre-open wordless; ② fact strip = own frame + mono source row `DART 공시 API · {rcept} ↗`, grid
  fixed 3×2 (390: 1×6), two-part values = value line + reason line; field-absent = **dashed-frame
  chip**; hierarchy 환산 = primary (44px hairline button) / 담기 = secondary (underlined text link,
  only while `days >= 0`); eyebrows `h2` with `//` via `::before`, step titles `h3`, band sentence
  `h2`; 질문 스트립 placement only (36/44px); 390 stack = chip·corp·(본문 표기)·meta → label → D-day
  → window → 담기 → **DART 원문 full-width 44px (`order:9`)** → strip → body.
- Four in-session operator directions (result.md 2-b / 2-c / 4-b / §4): **citation popover** —
  the quote opens as an overlay (opaque `#0e1a15`, 2px `--live` left edge, absolute under the
  trigger; close = × · outside click · Esc; rows never move); **citation density** — `[근거]` only
  where the on-screen value differs from the filing's words (extracted dates/figures/ratios, derived
  inputs); rows that carry the filer's sentence 1:1 get no chip and the section closes with one mono
  `DART 원문 {rcept} ↗` line (`.secsrc`, 32/44px) — mandatory for any section with zero chips;
  **「보유 종목에 담기 →」** replaces R5-2's 「내 포트폴리오에 담기 →」 (「포트폴리오」 banned, matches the nav
  label); **header size uniformity** — `min-height:136px` desktop / `248px` ≤767px +
  `align-content:space-between`, four states same height.
- §2b decisions taken at the defaults: **Q15 = (b)** Korean Mijual not-found (`app/not-found.tsx`,
  status 404, R8 chrome, no reason, path echoed in mono without a label); **Q16** 배정비율 full 10
  decimals, presentation only (`text-base` + `tabular-nums` + `nowrap`); **Q17** superseded-version
  URL stays silent (logged as decided); **Q18** absence literals confirmed verbatim.
- New copy (dated exception 2026-08-23): `not_found.title` 「이 주소에 해당하는 공시가 없습니다」 ·
  `not_found.line` 「관제 현황판에서 감시 중인 공시를 확인하실 수 있습니다.」 · `not_found.back` 「관제
  현황판으로 →」 · `offer.add` 「보유 종목에 담기 →」. Everything else reuses locked strings (「기한 지남」,
  「접기」, 「DART 공시 API」, 「정정사항」).
- Departures logged in `result.md` §5 (10): arrows retired, ② source row, grid fixed, diff arrow
  column retired, ③ dependency sentence trimmed, Citation self-injects CSS (`<style id="mj-cite-css">`),
  re-cut propagates to every Citation user (lookup · ask · corrections), rail rows = the two walked
  versions only, 한화솔루션 price quote is illustrative (render payload `quote` verbatim, never hardcode),
  per-row `[근거]` retired.
- Supersedes (once signed): R3 §3 chain arrows, §4 per-field citation, §CorrectionStory arrow column,
  §Mobile stack (now with R5-2's line and DART at `order:9`), R3 fact-strip grid; R5-2 담기 label.
  Regression checklist `build-prompt.md` §10 (0–9) seeds the phase's qa additions.

Read-back observations (record, not fixes — RESPECT THE DESIGN):
1. `components/Citation.html`'s note still says 「인용 패널 — R3 그대로 (inset … 최대 180px 스크롤)」 while
   `Citation.jsx` + `build-prompt.md` §6 + `result.md` 2-c specify the **popover** (200px scroll). The
   JSX and the build prompt are the contract; the card's prose lags by one in-session revision.
2. `Procedure.html`'s 390 label says 「단계 번호 열 34px」; `r10-detail.css` says 60px ≤767px. CSS wins.
3. `readme.md` says 「회귀 체크리스트 8항」; the landed `build-prompt.md` §10 has ten (0–9). Ten it is.
4. `result.md` §1 names `components/Citation.jsx` as changed — landed beside the card with its `.d.ts`
   and `.prompt.md` (unchanged API) so the apply slice has the full component.

Routing: Q15–Q18 are answered by the session (defaults adopted) — route as **decided** at the review.
Q19 (two 의견 panels at once) stays open. Q14 stays open.


### `P8.S7` — R10 applied: what the event detail is now, and what the next surfaces inherit (2026-08-24)

The signed R10 record is built. Eleven files changed (three new), and the detail surface is a
different object from the one R3 left: **one craft panel** from the header to the provenance line,
with hairline rules between the sections instead of five stacked panels. The 질문 스트립 is inside
that panel, attached to the header's bottom edge.

What later surfaces inherit — these are shared, not local to `/events`:

1. **The `[근거]` affordance is an overlay popover now, everywhere.** `components/Citation.tsx` was
   re-cut: trigger `min-height` **32px desktop / 44px ≤767px** (made with padding + equal negative
   margin, so no row moves), open state on the trigger (`--live-tint` + `aria-expanded`), and the
   quote opens **over** the page — `position:absolute`, opaque `#0e1a15`, 2px `--live` left edge,
   `max-height:200px` scroll, `×` + outside click + Esc, focus returned to the trigger on the two
   keyboard-ish closes. Measured on 조회 as well as 상세: **the rows behind it do not move** (that is
   the whole point of the re-cut). Every existing caller keeps its API (`rceptNo · quote · span ·
   parts · label`); the ask surface's numbered `InlineCitation` is R6-4's own component and was not
   touched.
   - **One thing the record could not know:** R10 anchors the popover to the trigger (`left:0`
     desktop, `right:0` ≤767px). On the round's card that is always in view; on a real page a chip
     sits wherever its value ends, and at 390 a mid-row chip opened the 340px popover at **left −90px**
     — the first characters of every line clipped. The component now slides the panel back inside the
     viewport (a ref callback measures on mount, and a resize listener re-measures while it is open);
     nothing approved changes, only the horizontal offset, and only when it would otherwise be cut.
     Verified at 390/481/768/1440 on both origins and in the production build: every popover fully in
     view, page overflow 0.
2. **Citation *placement* is data, not markup.** `components/event/fieldOrder.ts#fieldCites(key, hasQuote)`
   holds R10's density rule: a chip only where the on-screen value differs from the filing's words, so
   the five verbatim fields (`issue_price_formula`, `subscription_agents`, `refixing_terms`,
   `option_schedule`, `dissent_notice_procedure`) carry none. A section of verbatim rows closes with a
   single mono **`.secsrc`** line — `DART 원문 {rcept} ↗` — and that is the pattern any later surface
   with prose rows should copy: one source line per section beats one chip per row, at no cost in
   provenance.
3. **「기한 지남」 is the one closed-window word** (① closed window · ③ past step chips), **「종료」 exists
   nowhere in the product** (measured: 0 occurrences on all eight sample pages, both modes), and ②
   never wears a closed chip at all. ②'s past-open state renders 「진행 중」 in `--live` beside the
   dates — see the note on corpus reachability below.
4. **미주알 owns its 404.** `app/not-found.tsx` (+ `RequestedPath.tsx`, `not-found.module.css`) renders
   the Korean not-found for **every** unmatched URL and every `notFound()` — verified status **404**
   for a nonexistent rcept, for the three non-exposable ones (flagged / incomplete / 실적보고서 rcept)
   and for an unmatched path, in dev on both origins and in the production build. It gives **no
   reason** (D-14) and echoes the requested path in mono with no label. The last English screen a
   Korean-only reader could reach is gone.
5. **An eyebrow's `//` must not reach the accessible name.** R10 draws it with `::before` — and Chrome
   puts generated content **into** the accessible name, so an unnamed `h2` reads as 「// 발행 조건」.
   The detail eyebrows now carry `aria-label` with their own words (measured through the CDP
   accessibility tree: `2단계 절차`, `발행 조건`, `일정`). **The other surfaces still leak it**: 조회 and
   보유 종목 render `// {title}` as literal text (`// 진행 중인 권리`, `// 2026년 놓친 돈`), which no
   `aria-label` can fix without changing their markup — see Q21.
6. **A ③ page whose `dissent_notice_procedure` is missing states the absence in a field row**, not by
   dropping a section: `반대의사 통지 접수기간` + the dashed `.absent` chip, the same frame the countdown
   slot wears. That is R10 §10 box 6 and the `Procedure.html` 아시아나 case; it is **not** a placeholder
   (no fabricated value, no reason, and no row for any other missing field).
7. **The ≤767 stack is `display:contents` + `order`** on the header (chip · corp · meta → label →
   D-day → window → 담기 → `DART 원문` as a full-width 44px hairline button at `order:9`), and the
   chain/diff grids switch to row flow with 44px cells. Every interactive target on the detail surface
   measures **≥44px at 390** — including the ② fact strip's source link, whose 44px the round states in
   §3 prose while its own stylesheet leaves it at the desktop 32px (prose won; see `result.md`).
8. **The 담기 label is 「보유 종목에 담기 →」** (`auth/copy.ts#PORTFOLIO_ADD_KO`), superseding R5-2's
   「내 포트폴리오에 담기 →」 to match the R8 nav noun. The `days >= 0` gate is unchanged, so the line is
   absent on a past deadline — which is also why the 열림 header is ~20px taller than the other three
   states (Q20).

Two states could not be reached with today's data, and both were verified another way:

- **② past-open 「진행 중」** — all **386** R2 events in the corpus are `window_state: "upcoming"` on
  2026-08-24, so the branch is unreachable through the product. Verified in a real browser against a
  scratch proxy that moved one event's window into the past (nothing in the repo, the dev server or
  the database was touched): 「진행 중」 in `--live`, dates kept, no chip, 「종료」 count 0, 담기 line
  correctly absent. The rule itself lives in `Header.tsx#WindowLine` and matches §1's table.
- **Multi-part citations (`parts`)** — **0 of 386** served events carry a figure with `parts`, so the
  branch that renders each addend separately (P5.S20's contract, D4's defect) is unexercised in the
  product. The popover renders them as separate `.quote .part` passages with a dashed separator; the
  code path is unchanged from P5.S20 apart from its new container.

Two operating notes for whoever verifies next:

- **Never `next build` against the dev server's `.next`.** Copy `frontend/` to scratch — and copy
  `node_modules` with `cp -Rc` (an APFS clone, ~8s), **not** a symlink: Turbopack refuses a
  `node_modules` symlink that points outside the project root ("Symlink [project]/node_modules is
  invalid") and the build dies with a panic log.
- The production copy's server takes `MIJUAL_API_ORIGIN`, which is how the stubbed ② above was run.

## Doc impact

_Running list — one line per durable-truth change, consolidated into doc versions by `P8.REVIEW` (not
in parallel mode, so consolidation happens at the review)._

- `P8.DECOMP`: none — this slice wrote no code and no docs.
- `P8.S1`: **qa** — `## Regression Checklist` gains `- [ ] AI 질문: ask → reload → ask again renders two distinct turns, no duplicate-key warning, 재시도 hits the right turn (P8)`. No other durable truth moved: `lib/ask.ts`'s persisted shape (`Persisted.v === 1`, legacy `t1…` ids still hydrate) is unchanged, so `frontend` needs no new version for this slice.
- `P8.S3`: **frontend** — R8 supersedes the chrome. Nav = **two** destinations (AI 질문 · 보유 종목; 관제 현황판 is the ring wordmark, so the landing has no active underline) and the `[의견]` chip is gone; the account slot is a hairline frame with the **full email** + a 20px `Identicon` + ▾, its menu right-aligned/opaque with **two** rows (알림 설정 / 로그아웃); R5-4's 샘플 chip + 샘플 종료 are retired (the slot has two states); the ≤480 sheet is an **overlay + backdrop** that never pushes the page, with a counted body-scroll lock (`lib/scrollLock.ts`); the footer is one hairline / one row / **no mono** with the four prose sentences removed; a new 미주알-owned **의견 보내기** surface (`components/chrome/Feedback.tsx`, six states) replaces the vocky script seam — `VockyTrigger`, `VockyScript`, every `data-vocky-trigger` and `NEXT_PUBLIC_VOCKY_SRC` are **deleted**; new shared component `Identicon` (+ `lib/identicon.ts`); `lib/account.ts`'s `abbreviateEmail` retired with its test. Add supersession rows for R5 §Chrome 개정 ⑤ and R5-4.
- `P8.S3`: **frontend** — **`/portfolio` signed out renders the sample instead of redirecting to 로그인** (R8 §1). The gate is unchanged (still the API's 401), but the app's only `redirect(ROUTES.login)` is gone, so 「the only login-gated surface」 needs restating: the *account's* rows are still gated, the route is not.
- `P8.S3`: **api** — new **`POST /feedback`** (write-only, outward): body `{message, channel?: web|mobile, session_id?}`, **202 `{request_id, accepted_at}`** on vocky's 202, `400 feedback_empty`, `502 feedback_rejected` (`retryable:false`), `503 feedback_unavailable` (`retryable:true`) / `503 feedback_unconfigured`. It stores nothing on this side and is deliberately **not** merged with the agent's `save_feedback` queue. `GET /ops/vocky` is therefore no longer "the one read that leaves this service" — there are now one read and one write, both in `mijual/web/vocky.py`.
- `P8.S3`: **architecture** — `mijual.web`'s outbound row changes from "the one outbound vocky read" to "one outbound vocky read + one outbound vocky capture", still in the single module the AST scan allows (`vocky.py`); no new dependency (stdlib `urllib`), no new layer.
- `P8.S3`: **security** — the vocky key boundary now covers a **capture** path as well as the read: same `vk_` key, server-only, masked repr, header-not-URL, no redirects, nothing logged (not the key, not the reader's message). New fact to state: a reader's free text now leaves the system by design — the surface has **no contact field**, sends no email/account/IP, and says so in its own copy (「연락처를 받지 않으므로…」); the only correlation handle forwarded is the anonymous AI 질문 tab id **when one already exists**.
- `P8.S3`: **operations** — the env table's `MIJUAL_VOCKY_API_BASE` / `MIJUAL_VOCKY_API_KEY` row now serves **both** the observation read and the 의견 send (a reader-facing path, so an unset key degrades a *reader* surface, not only the ops tab); **`NEXT_PUBLIC_VOCKY_SRC` is retired** (no vocky script is loaded anywhere). **New deploy-critical fact:** vocky sits behind Cloudflare, which bans `Python-urllib/3.x` by browser signature — both calls must send a `User-Agent` (`mijual.web.vocky.USER_AGENT`), measured 403 `error 1010` without it and 200/202 with it.
- `P8.S3`: **data** — the env table's vocky row ("the vocky observation read") now covers read **and** capture; no schema change, no new table, no row written on this side by the 의견 path.
- `P8.S3`: **experience** — the chrome section: nav slots (two, both destinations), the account slot's new shape, the mobile sheet's overlay + backdrop, the footer's re-cut, and **the vocky paragraph is obsolete** (no `data-vocky-trigger`, no external widget — 미주알 owns the screen); 내 포트폴리오's "entry = account menu's first row" becomes a nav slot, and its gated column becomes "the account's rows are gated; the route answers with the sample".
- `P8.S3`: **product** — 「A judge or a reader can end the sample from anywhere — the 「샘플」 chip and 샘플 종료」 is no longer true: R8 retired both, and 로그인 여부 is the state. The sample is now reached by 보유 종목 without a session (and still by `?sample=1`).
- `P8.S3`: **qa** — `## Regression Checklist` gains this phase's chrome lines (below), and two counts move: `pytest` **139 → 142** and `npm run smoke` **15/15 → 16/16**.
  - `- [ ] 크롬: nav has exactly two links (AI 질문 · 보유 종목), no [의견] chip, no 샘플 chip, no data-vocky-trigger in the DOM (P8)`
  - `- [ ] 보유 종목: signed out renders the sample portfolio with its banner, signed in renders the account's own (P8)`
  - `- [ ] 의견 보내기: empty input disables 보내기, sending shows no spinner, failure uses no --alert colour, a 202 shows the 접수 번호 (P8)`
  - `- [ ] ≤480 sheet: overlays without pushing the page, closes on backdrop/Esc/×, body scroll released afterwards (P8)`
  - `- [ ] 푸터: no mono anywhere, one row, and at 390px 「AI 질문」 is not orphaned on its own line (P8)`
  - `- [ ] no vocky value in the client bundle: grep .next/static for vk_ / vocky / the key prefix (P8)`

- `P8.S5`: **frontend** — R9 supersedes the landing board and anchors. The window is **15/+15** (P7 Q3 closed by the operator's "q3: 15") with the footer re-cut to 「{step}건 더 보기」 + 「남은 {n}건」 + 「처음 {step}건으로 접기」 and **no controls at all** when nothing is hidden; the row column plan is `76 · corp minmax(180,1fr) · 240 · 190 · 96` (no-extras panels `76 · 1fr · 300 · 96`, decided **per panel**, ≤1119 `72 · 1fr · 200 · 170 · 96`, ≤767 R2's two-line row), values fixed-width with `minmax(0,N)` floors, rows `min-height:44px` centred; **the whole row is the click target** (stretched link on the corp anchor, `↗` above it) with hover / `:focus-within` / press states and a `--live` edge + per-value fade on refreshed rows; a **meta line** + the four-step **D-day legend** sit under the tabs (tabs gain hover per P7 Q9); strips are 펼치기 ↔ **접기** with rows on the board grid and dateless rows rendering the label only; the countdown card is **three stats** (`performance_reports` no longer rendered); 소멸주의보 says 「N개 종목」 on a tie; **board auto-refresh** exists as a client behaviour with a stated visible contract (chip-only 갱신됨, no spinner/button/text, changed-row edge, tab/window/strips/scroll/focus survive, hidden-tab pause, silent failure, stale = R2, reduced-motion = no fade) at a **60 s** interval; the hero's Enter rule is R9's four-step rule in the shared `SearchRow`; board control heights are **36px (≥768) / 44px (≤767)** and the 481px seam is retired; landing prose is `word-break: keep-all` with a balanced hero subtitle and `nowrap` mono values. Copy: **14 new constants** in `components/landing/copy.ts` (§9's table) and the deletions `STAT_REPORTS_KO` + `POSITIONING_KO` / `PROVENANCE_KO` / `GATE_COST_VALUE_KO` / `GATE_COST_TAIL_KO` / `DISCLAIMER_KO` (**P8 Q5 = drop, no relocation**). Add supersession rows for R2 §Board (columns, window, footer, tabs hover, control heights), R3 §board strip (fixed 펼치기 label; dateless row) and R2 §Anchors (2×2 stats; 소멸주의보 `{corp}`).
- `P8.S5`: **api** — `GET /board/summary`'s `next_lapse` gains **`tie_count`**: how many ① offerings share that earliest 청약 마감 (1 when only the named one does; today **3**). Derived from the same ordered pending list `lapse_pending` counts, so the strip and the board can never disagree; the key is present only when `next_lapse` is.
- `P8.S5`: **qa** — `## Regression Checklist` gains this surface's lines (below). No count moves: `pytest` **142** and `npm run smoke` **16/16** are the numbers `P8.S3`'s lines already correct.
  - `- [ ] 관제 현황판: the first screen shows 15 ranked rows + 「15건 더 보기」 + 「남은 N건」; one click → 30 + 「처음 15건으로 접기」; a tab switch resets the window (P8)`
  - `- [ ] 보드 행: clicking anywhere on a row opens the event detail, 「↗」 still opens DART, Tab draws the focus ring around the row (P8)`
  - `- [ ] 보드 열: every row's D-day is flush with the panel's right edge and the expanded strip rows share the board rows' x-coordinates, at 1512 / 1119 / 768 / 390 (P8)`
  - `- [ ] 스트립: 펼치기 ↔ 접기 with aria-expanded, and a 추후결정 row shows the label with no date and no dash, 「추후결정」 in the D-day cell (P8)`
  - `- [ ] 카운트다운 카드: three stats, and 「읽은 실적보고서」 is absent from the DOM (P8)`
  - `- [ ] 소멸주의보: on a tied 청약 마감 the sentence says 「N개 종목」 instead of a company name, and matches /board/summary's next_lapse.tie_count (P8)`
  - `- [ ] 자동 갱신: leave the landing open for two intervals — no spinner, no layout move; a new 기준시각 shows 「갱신됨」 + a --live edge on the changed rows, an unchanged one shows nothing; the tab, window, expanded strips and scroll survive and the countdown does not jump (P8)`
  - `- [ ] 히어로 Enter: 「삼성」 + Enter selects the first candidate without navigating, a second Enter goes; an exact name goes on the first Enter; with no candidates it still submits GET /stocks?q= (P8)`
  - `- [ ] 390px 랜딩: the hero subtitle breaks between 어절 with no one-syllable orphan, no mono date splits across lines, and the strip button is a full-width 44px control under its sentence (P8)`
- `P8.S5`: **experience** — the landing section: the board's window is 15/+15 and its footer names three things; the numbers on the surface are now *explained* (tab = whole board, list = countdown's ranked subset) with a visible D-day ladder; a row is a single click target; the strips say 접기 when open; the countdown card carries three stats, not four; and the page **refreshes itself while it is open**, with the 기준시각 chip as the only place that says so.
- `P8.S5`: **product** — 「the board shows 30 rows at a time」 is no longer true (15), and the landing is no longer a static render: the 관제 현황판 keeps itself current while a reader watches it, without asking them to reload. The 소멸주의보 headline names a count instead of one company when several offerings close on the same day.
- `P8.S5.5`: **frontend** — the desktop **account menu is three rows** — 알림 설정 / **의견 보내기** / 로그아웃 — executing R9 build-prompt §12 (the operator instruction given inside the R9 session; card `chrome/AccountSlot.html`) and closing P8 Q12. The new row is the **third entry point** to R8's own 의견 surface (footer · 모바일 시트 · 계정 메뉴): existing label `VOCKY_ROW_KO`, no new copy, no new surface, R8's panel with its six states unchanged. `FeedbackDialog` gains one additive prop, `placement?: "above" | "below"` (default `above`, so the footer and the nav sheet are untouched) — the account menu's entry is in the top bar, so its panel hangs **below** the frame, right edges aligned, same 10px offset (`.asPanel.asPanelBelow`, ≥481 only). `P8.S3`'s "the account slot's menu has **two** rows (알림 설정 / 로그아웃)" and "the 의견 진입점 is the footer button and the mobile sheet row — two places" are both superseded by three.

- `P8.S7`: **frontend** — R10 supersedes the event detail surface. The page is **one `CraftPanel`** (header → 질문 스트립 → body → 정정 밴드 → provenance, hairline rules between sections, no stacked panels); the header is a `minmax(0,1fr) auto` grid with `min-height:136px` (≤767px **248px** + `align-content:space-between`, one column via `display:contents` + `order`, `DART 원문` as a full-width 44px hairline button at `order:9`), its meta items `nowrap` with `::before` separators (≤767px separators off, 「정정 반영」 a hairline chip), and its countdown slot has **three forms** — `DDay` · `StateBadge kind="tbd"` · the dashed `.absent` chip (dotted vs solid is the contract). Window states: ① open `거래 가능 · 마감 D-n`, ① closed **「기한 지남」**, ② past-open 「진행 중」, ② pre-open dates only, **「종료」 nowhere**. ① 환산 chain is hairline instrument cells with **no arrows** (desktop column-flow / ≤767px row-flow, 44px cells) closed by the 환산 button; ② is a fixed 3×2 fact frame (390: 1×6) + a mono source row `DART 공시 API · {rcept} ↗` and no `[근거]` in the strip; ③ gains a **2단계 절차** block (`h2` + 68px number pills + `h3` step titles + 「기한 지남」 chips + the one dependency sentence), with 통지 방법/접수처 as rows in 발행 조건. Field rows are `220px` label + value with the citation **inside** the value, and R10's density rule lives in `event/fieldOrder.ts#fieldCites` (five verbatim fields carry no chip; the section closes with one `.secsrc` source line). 정정 전/후 and 철회 정정사항 are **two tagged sides** (the arrow column is retired). **`components/Citation.tsx` is re-cut for every surface**: 32px/44px trigger, open state on the trigger, and an **overlay popover** (opaque `#0e1a15`, 2px `--live` left edge, `max-height:200px` scroll, `×`/outside/Esc, focus returned) that leaves the rows where they are — plus a viewport clamp the record could not draw (a chip near a viewport edge would otherwise open the panel off-screen; measured −90px at 390). Eyebrow `h2`s carry `aria-label` because Chrome puts `::before` content into the accessible name. New: **`app/not-found.tsx`** + `RequestedPath.tsx` + `not-found.module.css` (Korean 404 for every unmatched URL and every `notFound()`, status 404, no reason, path echoed in mono). Add supersession rows for R3 §detail (stacked panels, inline citation panel, arrow chain, 「항목 · 정정 전 · → · 정정 후」 line) and R5-2 (담기 label).
- `P8.S7`: **product** — 「the last English screen a Korean-only reader can reach is Next's 404」 is no longer true: a non-exposable filing, a mistyped address and an unmatched path all render 미주알's own Korean not-found, which **still says no reason why**. On a ③ page whose 반대의사 통지 절차 is not in the current version, the product now **states the absence in a field row** (the same dashed chip the countdown slot wears) instead of quietly dropping the section — an absence is a fact about the filing, not an empty place.
- `P8.S7`: **experience** — the detail section: one panel per event rather than five; evidence opens **over** the page so a reader scanning values never loses their place; a section of the filing's own words is closed by one source link instead of a chip per row; 「기한 지남」 is the single word for a closed window (and 「종료」 exists nowhere); the 담기 line is 「보유 종목에 담기 →」 and appears only while a deadline is still ahead; every target on the surface is ≥44px at 390.
- `P8.S7`: **qa** — `## Regression Checklist` gains R10's own boxes (below). No count moves: `pytest` **142**, `npm run smoke` **16/16**, `npm run build` green.
  - `- [ ] 상세 헤더: the four states (열림 · 닫힘 · 추후결정 · 부재) never render below 136px desktop / 248px at 390, and 「종료」 appears on no page (P8)`
  - `- [ ] 상세 390: no orphan 「→」/「·」 in the chain, diff or meta lines, and every citation trigger / rcept link / button measures ≥44px (P8)`
  - `- [ ] 인용: 「[근거]」 opens an overlay popover — the rows behind it do not move — and closes on ×, an outside click and Esc, with focus back on the trigger; at 390 the panel stays fully inside the viewport (P8)`
  - `- [ ] 섹션 밀도: no section repeats 「[근거]」 on every row, and a verbatim-only section closes with one 「DART 원문 {rcept} ↗」 line (P8)`
  - `- [ ] 정정 이력: the button flips to 「접기 ×」 with aria-expanded and a changed surface, and the diff renders two tagged sides (정정 전/정정 후) with no arrow column (P8)`
  - `- [ ] 아시아나 ③: two dashed 「현재 버전 공시에 없음」 chips (countdown slot + field row), no placeholder for any other field, and no reason given (P8)`
  - `- [ ] 개요: the screen-reader outline shows the h2 eyebrows and the ③ step h3s, and no accessible name contains 「//」 (P8)`
  - `- [ ] 404: /events/<nonexistent> and any unmatched path return status 404 with the Korean not-found, the requested path echoed, and no reason (P8)`
  - `- [ ] mono: no date or figure splits across lines at 1512 / 1440 / 1280 / 768 / 767 / 481 / 390 (P8)`
- `P8.S7`: **copy** (`docs/reference/design/grounding/copy-inventory.md`, hand-registered tail — **not** a versioned doc) — four new strings (`NOT_FOUND_TITLE_KO` · `NOT_FOUND_LINE_KO` · `NOT_FOUND_BACK_KO` · `NOTICE_WINDOW_KO`), one supersession (`PORTFOLIO_ADD_KO` 「보유 종목에 담기 →」 replaces R5-2's 「내 포트폴리오에 담기 →」), and the reuse notes for `FACT_SOURCE_KO` · `SECTION_PROCEDURE_KO` · `DART_LINK_KO`/`dartSourceLabelKo` · `CLOSE_KO`/`CLOSE_GLYPH`. 「현재 버전 공시에 없음」 and 「추후결정」 stay verbatim — only their presentation moved.

- `P8.S9`: **frontend** — R11 supersedes the whole 내 종목 조회 / 놓친 돈 surface. A resolved stock opens with an **identity panel** (`h1` = 종목명, `.idmeta` 종목코드 → 고유번호, the shared `SearchRow` pre-filled with the name) and the crumb rail carries 「내 종목 조회」 as a label, so the words appear once per page and the entry hero's subline never follows a reader onto a result; the **보유량 strip is conditional** (Q-C — inside the identity panel, rendered only when a live ① `offering` or a 놓친 돈 row exists, with no disabled control and no sentence where it is hidden); ① panels are **the deadline** (`h3` = `countdown.label_ko`, chip/접수번호/공시 demoted to `.rmeta`, R10's three countdown forms kept) closed by a hairline 환산 chain; **every ② row of a stock is one table** at the first ② row's rank with a per-table `.ctsrc` source line, `⋯` (`.ctmiss`) for an unserved fact and `data-l` → `::before` column labels at ≤767; ③ gains R10's **2단계 절차** block; 놓친 돈 renders a **total only at ≥2 offerings with a holding** (one offering prints its figure once, in the row) with **one `.calcfoot` per row**; 「상세 보기 →」 is the **only** affordance out of a row and the 놓친 돈 prompt renders **once per page** (first live ① chain foot, else the 놓친 돈 head, never with a holding); `/stocks` with no query renders 감시 대상 3종 + 감시 중 {n}건 + the 집계 범위 section (Q-A = b, no redirect); 집계 범위 is now an `h2` section and the strip has a real `label`, so no block on the surface is unnamed and no accessible name contains `//`. **One breakpoint at 767px — R4's 480px seam is retired.** `Conversion`/`Dilution` stay byte-identical for `/portfolio`; the new `ConversionChain`/`ConvertibleTable` are built beside them. Add supersession rows for R4 §1 (the page had no stock identity), R4 §strip (unconditional own panel), R4 §2 (panel titles / per-row ② panels), R5 §놓친 돈 (unconditional total, rcept-as-link) and R4's 480px breakpoint.
- `P8.S9`: **frontend** — **a shared class and a module class on one element are ordered differently in `next dev` and in the production bundle.** `<main class="content page narrow">` measured R11's 960/620px in dev and **1120px in production**, because `app/shell.css`'s `.content { max-width: var(--bp-lg) }` landed last there. The surface states its two widths at doubled-class specificity (`.page.page` / `.narrow.narrow`) so neither order can win. Durable rule for every later surface: a module width that must beat a shared layout class is stated at a specificity that does not depend on stylesheet order, and any width claim is measured in a production build, not only in `next dev`.
- `P8.S9`: **product** — 「a resolved stock page never names the stock」 is no longer true: the result page's `h1` **is** the 종목명, with 종목코드/고유번호 under it and the search box echoing the name — 세기상사's page, which carried no company name at all, now identifies itself. And **`/stocks` with no query is no longer a void**: it states what the product watches (3종), how much of it (감시 중 {n}건) and the 집계 범위 boundary, out of elements other surfaces already signed.
- `P8.S9`: **experience** — the 조회 section: one page still, but the reader is told which stock they are on before any number appears; the 보유량 field exists only where a number on the page moves with it; a stock's 전환사채 rows read as one table instead of one panel each; a 놓친 돈 total appears only when there is more than one offering to total; and the page offers exactly one way out of a row (상세 보기 →).
- `P8.S9`: **qa** — `## Regression Checklist` gains R11's boxes (below). No count moves: `pytest` **142**, `npm run smoke` **16/16**, `npm run build` green.
  - `- [ ] 조회 정체성: a resolved stock's h1 is the 종목명 with 종목코드/고유번호 under it, the search box echoes the name, and 「내 종목 조회」 appears exactly once on the page (P8)`
  - `- [ ] 보유량 스트립: present on a stock with a live ① or a 놓친 돈 row, absent on a ②-only stock (풍전약품) and a no-rights stock (세기상사) — with no disabled control and no explanatory sentence (P8)`
  - `- [ ] ② 표: every 전환사채 row of one stock renders in a single table with one 「DART 공시 API — … | N건」 source line, the corp name printed once, and an unserved fact shown as 「⋯」 (never 0) (P8)`
  - `- [ ] ③ 절차: 아시아나's 2단계 절차 block shows two numbered steps — dated windows when served, otherwise the dashed 「현재 버전 공시에 없음」 chip — and the two notations never mix in one block (P8)`
  - `- [ ] 놓친 돈 합계: a 1건 stock prints its figure once in the row with no total above it; a ≥2건 stock prints the total only after a holding is entered; each row carries its own 배정비율 line (P8)`
  - `- [ ] 조회 출구: 「상세 보기 →」 is the only link out of a 놓친 돈 row, and the 놓친 돈 prompt appears once per page and disappears once a holding exists (P8)`
  - `- [ ] 검색 불일치: /stocks?q=삼성 renders 「‘삼성’과 일치하는 종목이 없습니다」 with the correct 과/와 particle, and the first differing keystroke removes the line (P8)`
  - `- [ ] 빈 /stocks: with no query the page shows 감시 대상 3종 + 감시 중 N건 + the 집계 범위 section, and never a placeholder count when /board/summary fails (P8)`
  - `- [ ] 조회 390: no interactive target under 44px on any stock page or the entry, no horizontal overflow, and 767→768 is the only breakpoint on the surface (P8)`
  - `- [ ] 조회 신뢰: 계양전기 (발행가 확정 전) shows no 원 amount before or after a holding is entered while share counts still convert, no untagged 원 anywhere, and typing a holding fires no request carrying the number (P8)`
  - `- [ ] 프로덕션 폭: /stocks and /stocks/{corp_code} measure 960px / 620px in a production build, not only in next dev (P8)`
- `P8.S9`: **copy** (`docs/reference/design/grounding/copy-inventory.md`, hand-registered tail — **not** a versioned doc) — R11's one new sentence (`MISSED_PROMPT_KO`), the gate-signed `.mmcap` caption (Q28 = a), and the label-tier strings the build prompt and cards print (보유 · 배정비율 (1주당) · 초과청약 비율 · 공시 · 소멸 계산 (시장 전체) · 종목코드 · 고유번호 · 접수 · 집계 범위). Two constants are **derived, not typed** — `TRADING_OPEN_KO` from `tradingOpenKo()`'s head and `NO_SCHEDULE_KO` from the tail of R3's locked 「카운트다운 없음 — 일정이 공시상 미정」 — so neither can drift. `noMatchKo` gains the build-prompt §7 josa rule (non-Hangul → 「와/과」). Supersessions: the `h1` moves from 내 종목 조회 to the 종목명, per-② panel titles retire, rcept-as-link retires, and R4's 480px breakpoint retires.

### R11 walk — surface 4 (내 종목 조회 + 놓친 돈 조회기), 2026-08-24, operator runtime

Walked by the orchestrator at `http://127.0.0.1:3000` (Chrome desktop 1456px + 390px same-origin
iframes) **while `P8.S7` was still running** — the operator asked for the R11 handoff in parallel, so
the handoff was written and pushed first (`f362f54`, handoff file only) and this record follows S7's
close. Pages: `/stocks` · `/stocks?q=삼성` (no match; then typing 「계양」 for the candidate panel) ·
계양전기 `00102618` · 한화솔루션 `00162461` · 풍전약품 `01110474` · 세기상사 `00133618` · 아시아나항공
`00138792` (API only — the dev server was mid-rebuild on S7's `Citation` edit at that moment; the
iframe for `/stocks?q=삼성` also hit the Next error overlay once — executor transients, not findings).
Handoff: `docs/reference/design/rounds/11-lookup/handoff.md`. Default for every item: fix, Claude
Design decides how.

1. **The resolved stock is never named** — `/stocks/[corp_code]` renders `LookupHeader` with no
   query: empty input, no stock line; 종목명/종목코드 only inside the event panels' titles. On
   세기상사 (no rights) the company name is nowhere on the page. → Q-B.
2. **Header weight above every result** — crumb + h1 + hero subline + search repeat; content starts
   ~215px down at 390, ~235px on desktop.
3. **보유량 strip on stocks where it changes nothing** — ②-only 풍전약품, no-rights 세기상사. → Q-C.
4. **놓친 돈 before a holding** (한화솔루션): coverage caption + 3-column breakdown, no headline, no
   conditional frame, no prompt; with 500주 the 679,575원 prints twice (headline + 500주 기준 column)
   on a single-offering stock. → Q-E.
5. **Breakdown row has no labelled route to the event** — only the mono 접수번호 `metaLink` + `[근거]`;
   the 진행 중 panels have 「상세 보기 →」.
6. **Every panel title is the corp name on a single-corp page** — 풍전약품 ×3 identical titles.
7. **② panels** — three bare facts, half-empty right column, ~170px each, three = 600px.
8. **③ panel never drawn** (R4 "pin a sample") — 아시아나 `20260713000482`, 반대의사 통지 마감 with
   `dday: null` → StateBadge 추후결정 + dependency line. Real sample now; draw it.
9. **Candidate panel on this page** — opaque (`rgb(10,19,16)`, z 20, `transition: all`), but it fades
   in over the **stale 검색 불일치 sentence** and over the provenance line.
10. **「‘삼성’와」 particle** — 와/과 by final consonant (R9 walk 11, routed here).
11. **Empty `/stocks`** — crumb, title, subline, search, provenance line, void. → Q-A.
12. **Heading semantics** — `// ` is literal text inside the h2 names (Q21 — fold here); the 보유량
    strip and the coverage boundary panel have no heading.
13. **Breakpoint mismatch** — `Lookup.module.css` `@media (min-width: 480px)` vs `SearchRow` 768 /
    R10 §0 single 767; 481–767 is desktop-laid.
14. **390 measured** — chips 87/101×44, holding input 260×44, search 238×48 + 조회 88×48, 「상세 보기 →」
    292×44, crumb 74×44, `[근거]` 48×44 (post-R10) — the 44px floor is met; the restore chip wraps to
    its own full-width row; page heights 한화솔루션 1,723px / 풍전약품 2,075px.
15. **Desktop rhythm** — 배정비율 line hangs alone pre-holding; selected preset chip (live text +
    border) vs dashed restore chip = two chip grammars in one row; 「서버 전송 없음」 as a 10px caption.

Not walked: the anonymous `ConversionOffer` (R12's), 481–767 widths, the production build. Operator
decisions routed to the handoff §2b as Q-A–E = **Q23–Q27** below.

### R11 landed spec — read back 2026-08-24 (`P8.S8` gate 2) — SIGNED OFF 2026-08-24 ("sign off"); SIGNOFF.md R11 entry, cards regrouped to `Lookup`

Read back with DesignSync from "Mijual Design System" and **landed as-is** under
`docs/reference/design/rounds/11-lookup/output/`: `result.md`, `build-prompt.md`,
`lookup/r11-lookup.css` (geometry canon), `lookup/r11-parts.jsx` (structure + samples), and the six
cards `lookup/{Entry,Result,Rights,MissedMoney,Empty,Mobile}.html` (line-1 `@dsCard group="⏳ P8.S8 ·
Lookup"`). Token delta **none**. No readme change landed (the repo keeps the record, not the pane's
index).

**Binding decisions (the apply slice builds these, RESPECT THE DESIGN):**

1. **Result page: h1 = 종목명**, mono meta 「종목코드 {stock_code}」 (first, when served — the API
   does serve it, e.g. 계양전기 `012200`) · 「고유번호 {corp_code}」; the `SearchRow` on a result carries
   `defaultValue = corp_name` (never empty); the h1 「내 종목 조회」 + hero subline render **only on
   `/stocks`**; on a result 「내 종목 조회」 survives as the rail's second label (`.rail .here`).
2. **Identity panel** (`.idp` grid `minmax(0,1fr) minmax(300px,400px)`) with the 보유량 strip as its
   bottom rail (`.strip`, `--surface-raised`, `border-top`), rendered **only** when a live ① row or a
   lapse row exists (Q-C) — absent on ②-only / no-rights stocks, no placeholder.
3. **Chip grammar**: solid hairline preset chips (selected = `--surface-inset` + `--ink-1` + `--ink-2`
   border, 36px desktop / 44px mobile, `aria-pressed`), dashed restore chip; 「서버 전송 없음」 as mono
   `text-xs` (`.stripcap`, `margin-left:auto`), not a 10px caption.
4. **Rights panels**: corp name never repeated; left = RightsChip + `.rmeta` (접수번호 · {filed} 공시 ·
   정정 반영), right = **`h3.whenlab` = `countdown.label_ko`** → `DDay` / `StateBadge tbd` → `.win`.
   ① = R10 §2 instrument cells (`.chain`): with holding 보유 · 배정비율 (1주당) · 배정 신주 (+ caption
   cell line) · 초과청약 한도; without holding **two cells** 배정비율 (1주당) · 초과청약 비율 {pct};
   `.chainfoot` = 발행가 확정 전 chip + sentence (or R4's 환산액 line when priced) + the prompt (no
   holding only); `.rowline` 구주주 청약 · 일반공모 windows; 예정발행가 never. ② = **one table per
   type** (`.ctrow` grid `minmax(0,1.1fr) .8fr .9fr .62fr minmax(0,1.25fr) auto`: 공시일+접수번호 ·
   전환가액 · 전환 시 주식수 · 오버행 · 개시일+DDay · 상세 보기 →; unserved values as `.ctmiss` `⋯`, never
   0/dash; `.ctsrc` 「DART 공시 API — 전환가액 · 전환 시 주식수 · 오버행」 + `{n}건`; no per-cell
   `[근거]`; past opening = 「진행 중」). ③ = R10 §4 steps (68px pills, `h4` titles, past step +
   「기한 지남」, missing window = dashed `.absent` 「현재 버전 공시에 없음」, dependency line) with
   `dday: null` → `StateBadge tbd` + 「일정이 공시상 미정」. 0건 = `.closed` 「청약 {date} 종료」.
5. **One event affordance**: 「상세 보기 →」 (`.golink`, underline, 32/44px) — ① panel foot, ② row
   end, 놓친 돈 row under the title; **접수번호 is never a link** (MissedMoney's `metaLink` goes).
6. **놓친 돈**: `.mmhead` frame → prompt (no holding) → `.mmcap`; **total only when `lapse.rows.length
   >= 2`**; single offering → the row's `{n}주 기준` cell is the headline (`.big` text-2xl alert 「추정」 +
   하한 line + caption); no holding → last column header 「보유 주식 수」 and a dashed `.bslot`
   (44px), never 0원/dash; `[근거]` inside the 증서 매매기간 cell (third element of `.bwin`), no
   row-spanning citation line; `.calcfoot` only with a holding; `.disc` R4 disclaimer.
7. **Prompt** = the round's **only new string** (dated exception 2026-08-24, Q-E): 「보유 주식 수를
   입력하면 내 보유량 기준으로 환산합니다」 — a `<button>` 1px dashed `--border-strong`, 44px, + mono `→`,
   focuses the strip input, **once per page** (① `.chainfoot` if a live ① exists, else `.mmhead`),
   gone once a holding is entered. Register in `copy-inventory.md` as a `lookup` entry.
8. **Entry `/stocks` (Q-A = b)**: `.page.narrow` 620px, h1 「내 종목 조회」 + subline + 48px search →
   (no-match line) → `WatchPanel` (감시 대상 3종 + 「감시 중 {n}건」) → `h2 집계 범위` panel → provenance;
   no redirect, no new copy. **No-match line belongs to the submitted query**: removed on the first
   keystroke that differs (`missed && query === currentInput`); particle 와/과 by final consonant,
   non-Hangul → 「와/과」 — `noMatchKo` only, sentence body locked.
9. **Headings**: result h1 종목명 → h2 진행 중인 권리 — N건 → h3 마감 라벨 → h2 2026년 놓친 돈 → h2 집계
   범위; entry h1 → h2 집계 범위; `//` via `.eyebrow::before`; strip `label[for]`.
10. **One breakpoint, 767px** — `Lookup.module.css`'s 480px queries migrate; ≤767 rules per
    `r11-lookup.css` (identity one column, presets 3-col 44px grid, restore chip full-width own row,
    `.rid`/`.rwhen` `display:contents` → label + D-day on one row, cells as label/value 44px rows, ②
    rows → cards with the 개시일+DDay at row-1 right and `data-l` labels, 놓친 돈 row → card with the
    내 기준 block last); target heights 한화솔루션 ≈1,250px / 풍전약품 ≈1,150px.
11. Regression checklist §10 items 0–12 verified on both origins + production build, 390.

**Read-back observations (for the apply slice, not changes to the record):**

- `Identity`'s `.idmeta` in the cards shows a second span 「DART 공시 기준」; `build-prompt.md` §2 (the
  contract) specifies 「종목코드 {code}」 · 「고유번호 {corp_code}」 only and `result.md` §4 lists a single
  new string — the apply slice follows §2 and treats 「DART 공시 기준」 as card filler, not product copy.
- `.mmcap` 「유상증자 {n}건 · 집계 범위 {start} ~ 오늘 (KST) · 시장 가격 미사용 — 소멸된 증서의 이론가치
  환산」 is a composite whose tail is not in `copy.ts`; `result.md` §4 does not list it as new copy.
  The signoff should say whether this caption is signed as written (then register it) or composed
  from `coverageCaptionKo` + existing words only — **operator decision at signoff** (Q28).
- `.rowline` (구주주 청약 · 일반공모 windows) and the ③ step windows depend on what `StockPage.rights.rows`
  carries; the apply slice renders them from served fields only and omits what is not served (no new
  payload — no new features). ② 전환 시 주식수 comes from `convertible_api_facts`.
- 「일정이 공시상 미정」 under a `tbd` badge is the tail half of R3's locked 「카운트다운 없음 — 일정이
  공시상 미정」; the apply slice reuses the existing constant's wording.
- The ② table's 「진행 중」 past-opening state is unreachable in today's corpus (P8 Q22) — verify by
  code as in `P8.S7`.
- Q23–Q27 are answered by the session (Q-A b · Q-B yes · Q-C hide · Q-D keep the rule · Q-E one
  prompt string); marked below.

### `P8.S9` — R11 applied: what 조회 is now, and what the next surfaces inherit (2026-08-24)

Full record in `slices/P8.S9/result.md`. The short version:

**The surface.** `Lookup.module.css` is the round's `geometry-canon.css` ported onto module class
names **mobile-first** (base = the canon's ≤767 block, `@media (min-width: 768px)` = desktop), so
R11's single 767px breakpoint is structural rather than a rule that happens to fire. A resolved
stock is: identity panel (`h1` 종목명 · 종목코드/고유번호 · the pre-filled `SearchRow` · the
conditional 보유량 rail) → 진행 중인 권리 (panels whose `h3` **is** the deadline; one table for all
of a stock's ②; R10's 2단계 절차 for ③) → 놓친 돈 (total only at ≥2건 with a holding; one
`.calcfoot` per row; 「상세 보기 →」 the only way out of a row) → `h2 집계 범위` → provenance. The
prompt sentence renders **once per page** and only where the input it focuses exists. `/stocks`
with no query is the same watch panel a no-rights stock shows, plus the boundary section.

**Three things later surfaces inherit.**

1. **R12 (auth) is unmoved.** `ConversionOffer` still renders last in normal flow on a stock page
   and is still gated on `lib/holding.ts`'s own `convert()` returning a non-null value — "값 계산
   직후" is asked of the one multiplication site, not answered a second way in the view, so an
   unpriced ① cannot produce an offer beside numbers that do not exist.
2. **Specificity, not stylesheet order, holds a module width against a shared layout class.**
   `<main class="content page narrow">` measured 960/620px in `next dev` and **1120px in the
   production bundle**, where `app/shell.css`'s `.content { max-width: var(--bp-lg) }` landed last.
   Fixed with `.page.page` / `.narrow.narrow`. Any later surface that puts a module width on an
   element already carrying `content` (or any shared layout class) must do the same — and **must
   measure it in a production build**, because `next dev` cannot show this bug class at all. A
   63-class × 5-page × 3-width computed-style diff after the fix showed no dev/production
   differences.
3. **A read-only scratch proxy is the way to walk states the corpus cannot reach.** Rewriting the
   upstream JSON in flight and pointing the scratch production copy at it with `MIJUAL_API_ORIGIN`
   reached five otherwise-unreachable branches (② past-open 「진행 중」, ① 「기한 지남」, dated ③
   steps, ≥2-offering `.total`, unserved ② facts `⋯`) without touching the repo, the dev server or
   the database. Today's corpus: **32 lapse reports across 32 distinct corps, 0 with ≥2**, and every
   ② row serves all three facts — so R11's total rule and its `⋯` cell are stub-verified, the same
   treatment `P8.S7` gave the ② past-open state (Q22).

**What the route does not serve** (evidence for Q29–Q32, cross-checked in `src/mijual/web/reads.py`):
`offering.subscription` is typed `unknown` and read by no surface, there is no `subscription_agents`
field and no 일반공모 window, so `.rowline` is omitted; 아시아나's R3 row arrives with `fields: {}`,
so both ③ steps show the dashed chip; `_lapse_row` composes no 결의일, so `.bofftitle` is 「유상증자」
alone; `lapse.coverage` rides `GET /stocks/{corp_code}` only, so the entry page states the boundary
without dating it. **No payload was extended** — R11 is polish.

**Card sample data is not contract.** 「매매기간」/「행사기간」 prefixes on `.win` and the third
`.idmeta` span 「DART 공시 기준」 appear in the cards but not in build-prompt §2, so they are omitted;
the build prompt governs and the card illustrates. Same reading for `r11-parts.jsx`'s extra josa
branch — build-prompt §7's rule is what shipped.

**Verified** at `http://127.0.0.1:3000` **and** `http://100.77.164.42:3000` in `next dev`, and again
against a production build served on `:3100`, at 1456 / ~600 / 390 — build-prompt §10 boxes 0–12,
all green: `h1` = 종목명 on all five stocks, one ② table with 0 `⋯` in real data, ③ two dashed
chips, citation as the third child of `.bwin` with the popover fully in view at 390, 679,575원
printed once with no total, no strip on 풍전/세기, the 과/와 particle, `headSlash: 0` matching R10's
baseline, **zero** sub-44px targets at 390, one breakpoint, and no 원 amount on 계양전기 before
확정발행가. Heights at 390 fell 8.8% (한화) and 15.5% (풍전) but do **not** reach the record's
≈1,250/≈1,150 — the canon's own `.ctrow` measures 252px against the product's 273px in a `file://`
harness, so the residual is the signed geometry, not the build (Q34).

**Gates:** `npm run typecheck` clean · `npm run smoke` 16/16 · `npm run build` green · `pytest` 142
passed · `workflow validate` clean · the whole `## Regression Checklist` re-run, not only R11's
lines. `/portfolio` and the landing are unaffected.


### R12 walk — surface 5 (auth — 로그인 · 계정 만들기 · 비밀번호 재설정 + conversion moments), 2026-08-24, operator runtime

Walked by the orchestrator at `http://127.0.0.1:3000` **while `P8.S9` was running** (the operator asked
for the R12 handoff in parallel; handoff pushed first as `05b2ca0`, this record follows S9's close).
The operator's Chrome is logged in and `/auth/login` redirects to `/portfolio`, so the anonymous
panels were captured from the server render without a session and viewed at desktop 1456px + 390px;
the pending / error / notice states, the anonymous `ConversionOffer` / `DeadlineOffer` / nav 로그인 and
로그아웃 → 「로그아웃되었습니다」 were **not walked** (credentials or a logged-out session needed) — read
from code. Handoff: `docs/reference/design/rounds/12-auth/handoff.md`. Default for every item: fix,
Claude Design decides how.

1. **「비밀번호 재설정」 is disabled with no reason** until an address is typed — grey text, nothing on
   click; a reader who forgot their password reads a dead link.
2. **No password rule before the error** — 「8자 이상」 appears only as an error after submit (계정
   만들기 and the reset page). → Q-C.
3. **Reset page context** — `/auth/reset?token=…` names no account and no state for a bad/expired
   token beyond the API's error line (가입 여부 비노출 stays).
4. **Chrome's English validation bubble** (P7 Q12, routed here) — `required` + `type=email`. → Q-A.
5. **Primary button** 160px min-width, left-aligned under full-width inputs on desktop (full-width
   at 390); R4/R11 조회 is 48px full-row, R10 환산 44px.
6. **Sample-entry sub wraps with an orphan** at 390 (「…클릭 한 / 번.」).
7. **Page composition** — 440px panel centered, no rail/crumb (every other surface has 「← 관제
   현황판」); sample entry under a hairline. → Q-D.
8. **Breakpoint** — `Auth.module.css` switches at 480px; R10/R11 settled on 767.
9. **States** — idle / 확인 중… / error / notice, focus-visible, hover, disabled primary: to be drawn.
10. **로그아웃 → 「로그아웃되었습니다」** — placement/duration not walked.
11. **Conversion moments as a set** — `ConversionOffer` (now on R11's lookup page), `DeadlineOffer`
    (R10 header, `days >= 0`), nav 로그인 — hierarchy, and the post-login landing (always
    `/portfolio`; the origin is not carried). → Q-B.
12. **PII inset** tier/voice next to R11's caption tier.
13. **Headings** — h1 = mode label; PII `aside`; sample `section` unheaded.

Operator decisions routed to the handoff §2b as Q-A–D = **Q35–Q38** below.

## Operator Questions

_Questions only the operator can answer; every entry is routed at the review -- folded into the acceptance walkthrough (`accept-gate --open`) or filed with `defer-job`. An unrouted entry is a review finding._

- **Q1 — inherited P7 decisions: answer them inside each surface's round, or up front?** P7 left 13
  operator decisions unanswered (table above). This decomposition assumes **each surface's design
  slice hands the operator its inherited items together with the walk's own findings**, so they are
  decided where they are visible. If the operator would rather settle some of them before any round
  starts (Q3's board window is one constant; Q13 is housekeeping), say so at the first `pending`.
- **Q2 — 의견 (vocky) still has nothing to bind to.** _Answered at the R8 gate (see §R8 interview)._ `NEXT_PUBLIC_VOCKY_SRC` is unset and vocky ships
  no embeddable script, so all three signed chrome triggers are dead controls. R8's walk will meet
  them, and **no slice may invent a URL**: the operator must supply the script/capture path, or decide
  that 의견 routes elsewhere (the AI 질문 agent already has a 의견 tool). Until then surface 1 cannot
  honestly claim "every visible control does something".
- **Q3 — does chrome polish include the 404 page?** _Answered at the R8 gate: stays default._ It is Next.js's default page, it carries the one
  English sentence a Korean-only reader can reach, and it belongs to no signed round. Folding it into
  R8 means designing a page the record never drew (still polish, not a feature); leaving it means the
  English sentence ships. Operator's call at R8's handoff.
- **Q4 — is copy in play this pass?** _Answered for R8 at its gate: per round, named + dated._ `design-cowork` locks copy by default and the whole product
  leans on it ("inventing a Korean string is a design change"), but "audit and polish the whole
  thing" plus P7 Q7's four developer-vocabulary strings suggests some rounds need copy explicitly
  **in play, named and dated in that round's handoff**. Blanket answer, or per round?

- **Q5 — gate-cost + disclaimer sentences: relocate or drop?** _Answered at the R9 gate (2026-08-23): "drop." — `P8.S5` deletes the constants; no relocation._ R8 removes the footer prose on the operator's
  instruction; the footer was the last placement of 「게이트 비용」 and the only placement of the 면책 문장.
  The session proposes relocating both (landing bottom / 이용 안내) in a later round. Operator decides; until
  then `P8.S3` deletes the markup but may keep the constants (build-prompt §4 note).
- **Q6 — identicon seed: hashed email or a stored per-account seed?** Visual identical; data choice for
  `P8.S3` (default: hashed email unless the operator prefers a stored seed). _`P8.S3` shipped the default — the mark is derived from the account email (`seed.trim().toLowerCase()`); a stored per-account seed would change nothing visible. Still the operator's to confirm._

- **Q7 — does the 의견 textarea wear the focus ring, or the P7 field hairline?** R8's build-prompt §6
  gives the textarea 「포커스 2px `--focus-ring`」, while §9 lists 「P7 포커스 분리」 among the round's
  invariants — and P7's operator override is exactly that text-entry controls do **not** wear the
  ring. Both cannot hold on a `<textarea>`. `P8.S3` kept the invariant (`outline: none` + the field's
  own brightened hairline, like every other field in the product) and did not restyle it. If the
  operator wants the ring on this one field, it is one rule. (Same family as P7 Q2/Q10, still open.)
- **Q8 — should the account menu close when one of its rows navigates?** Click 알림 설정 and the menu
  is still open on the new page (Esc or a click outside closes it). This is R5 behaviour that R8 did
  not change: §2 lists the closes as 「Esc / 외부 클릭」 only, while the mobile sheet beside it gets an
  explicit 「경로 변경 닫힘」. Left as the record has it rather than invented; it is one effect if the
  operator wants the sheet's behaviour here too.
- **Q9 — delete `P8.S3`'s three test rows from vocky?** Verifying the 의견 send end to end put three
  clearly-marked rows (`P8.S3 검증 …`) into the operator's real vocky project, which had none. They
  are visible on `/ops/feedback`. Removing a row from vocky is an outward write no design or plan
  sanctioned, so they were left in place — the operator can delete them there, or keep them as the
  first proof the path works.

- **Q10 — board auto-refresh interval.** R9 designed the visible contract and left the value to apply with a
  stated assumption of **60 s** (기준시각 is minute-granular). `P8.S5` will use 60 s unless the operator names
  another value or wants it tied to the backend's actual refresh cadence.
- **Q11 — 동시 마감 tie count needs an API field.** R9's 소멸주의보 / countdown caption say 「N개 종목」 when
  several ① events share the earliest 청약 마감. `/board/summary` does not carry that count today;
  `P8.S5` adds `next_lapse.tie_count` (or renders the corp name until it exists — the design forbids guessing).
  Operator to confirm the API addition is acceptable in a polish phase (it is derived from data already served).
- **Q12 — 「의견 보내기」 row in the account menu (operator instruction given inside the R9 design session).**
  Not in R9's apply scope by the session's own note (`build-prompt.md` §12). Needs a home: a small `fix`/
  implementation slice in P8 after `P8.S5` (one menu row wired to the existing Feedback panel), or a deferred
  job. Orchestrator's default if unanswered: insert `P8.S5.5` (risk low → mid tier) right after the R9 apply.
  _Executed as `P8.S5.5` (2026-08-23): the row is built and verified — 알림 설정 / 의견 보내기 / 로그아웃, opening
  R8's own panel. Nothing is left to decide here; the review routes this as **done**, not as a question._
- **Q13 — grounding snapshot refresh.** R9 could draw only the events the grounding pack names (13 of 15
  ranked rows, 1 of 4 추후결정, 4 진행 중). The session asks that the next `board-snapshot.md` regeneration
  include the top 진행 중 rows and all 추후결정 names so later rounds render the strips with real data.
  Housekeeping for the operator / a later slice; no design consequence.

- **Q14 — the countdown card's caption and label.** R9's `Anchors.html` draws 「가장 빠른 소멸까지」 above the
  countdown and 「청약 마감 2026-09-04 (KST) · 3개 종목」 under it, and §6 says the tie rule applies to that
  caption too — but the product's countdown has **never** had either string, §6 also says 「카운트다운 자체
  불변」, and neither string is among §9's fourteen. `P8.S5` therefore built the tie rule where a corp is
  actually printed (소멸주의보) and **did not mint the caption**. The operator (or a later round) decides:
  add the label + caption as new copy, or leave the countdown wordless as it is today.

- **Q15 — _(answered in the R10 session, 2026-08-24 — see §"R10 landed spec")_ — the event 404 surface (R10, finding 15).** Non-exposable rcepts render Next.js' English default page by
  R3's deliberate "no 404 copy" choice. Keep the framework page, or design a Korean Mijual not-found that still
  says **no reason why** (D-14)? Orchestrator default: design it in R10.
- **Q16 — _(answered in the R10 session, 2026-08-24 — see §"R10 landed spec")_ — 배정비율 printed to 10 decimals (R10, finding 16).** R3 §6-1 literal. Keep the full value (default) and let
  R10 set its presentation, or round?
- **Q17 — _(answered in the R10 session, 2026-08-24 — see §"R10 landed spec")_ — superseded-version URL (R10, finding 17).** `/events/<old rcept>` renders the current version silently. Leave
  (default, log as decided) or add a one-line notice?
- **Q18 — _(answered in the R10 session, 2026-08-24 — see §"R10 landed spec")_ — locked R3 absence literals (R10, finding 10).** 「현재 버전 공시에 없음」 / 「카운트다운 없음 — 일정이 공시상
  미정」 stay verbatim; only presentation moves in R10. Confirm.

- **Q19 — may two 의견 panels be open at once?** Measured in `P8.S5.5`: open the footer's 의견 패널, scroll
  up, open the account menu and click 의견 보내기 → **two** `[role="dialog"]` panels on screen at the same
  time (Esc closes both; each entry point owns its own state). R8 drew one entry point and R9 §12 added a
  third without saying anything about mutual exclusion, so nothing was invented. Default if unanswered:
  leave it — a later chrome round decides whether opening one 의견 진입점 closes the others (it is the same
  question for the ≤480 sheet row, and the fix would be one shared owner in the chrome, not three local ones).

- **Q20 — should the 열림 header be the same height as the other three, or is the floor enough?**
  R10 §1 says the four states 「같은 높이를 차지한다」 and gives `min-height:136px` (≤767px `248px`) —
  a **floor**, which is what the round's own stylesheet contains. Measured after the build: 닫힘 ·
  추후결정 · 부재 · 철회 all sit exactly on the floor (136 / 248), and **열림 is 156.6 / 308.5**,
  because that state alone renders the 담기 line (its gate is `days >= 0`, R5-2's, unchanged). `P8.S7`
  built the record literally — a fixed height would have to either clip the 담기 line or bake 20px of
  empty space into the other four. Operator's call: (a) leave it (the floor is the rule, current), or
  (b) make 136/248 a fixed height with the 담기 line inside it, which a later round would draw.
- **Q21 — the `//` eyebrow leaks into the accessible name on the other surfaces.** R10 §12 requires the
  eyebrow's `//` to be CSS-drawn so the accessible name is 「일정」, and `P8.S7` did that for the detail
  surface (Chrome puts `::before` content into the name, so the headings now carry an `aria-label`).
  But 조회 and 보유 종목 print `// {title}` as **literal text** (`// 진행 중인 권리`, `// 2026년 놓친 돈`),
  from earlier rounds, so a screen reader reads the slashes there. Fixing it is a two-line change per
  surface — but those eyebrows belong to signed rounds, so: fold it into each surface's own R11+ round
  (default), or file it as one small cross-surface job now?
- **Q22 — two states cannot be seen in the product with today's corpus.** ②'s past-open 「진행 중」
  (**386/386** R2 events are `upcoming` on 2026-08-24) and multi-part citations (**0/386** figures carry
  `parts`). `P8.S7` verified the first in a real browser against a scratch proxy and the second by code
  reading; neither can be checked on the acceptance walkthrough. Does the operator want a seeded
  fixture (a corpus row or a dev-only payload switch) so trust-critical states like 「종료 금지」 can be
  *seen*, or is a stubbed verification recorded in `result.md` enough (default)?
- **Q23 (R11 Q-A) — empty `/stocks`.** With no query the page is title + search + provenance and
  nothing else. (a) keep it bare, (b) give it the already-signed context (감시 대상 3종 · 감시 중 count ·
  coverage boundary panel — no new copy), (c) redirect to the landing hero. Default **(b)**. Taken at
  the R11 gate or in the session.
- **Q24 (R11 Q-B) — stock identity on a result.** Show 종목명 + 종목코드 at the top of a resolved stock
  (today nothing names it; 세기상사's page has no company name at all). Default **yes**, form decided
  in the session.
- **Q25 (R11 Q-C) — the 보유량 strip on stocks with no ① row** (②-only, no rights). Hide, demote, or
  keep with a factual line (a sentence = the round's dated copy exception). Default: session decides.
- **Q26 (R11 Q-D) — a past ②/③ leaves no trace on a stock.** 세기상사's ③ windows passed; the page is
  the NoRights card, because 놓친 돈 is ①-only (R4-4) and a ③ is never money. Keep the rule (default;
  log as decided) or add a factual closed line the way ① leaves 「청약 {date} 종료」.
- **Q27 (R11 Q-E) — 놓친 돈 before a holding is entered.** Layout only (default — the session decides
  whether a prompt sentence is needed; if so, dated exception) or an explicit prompt.
- **Q23–Q27 — answered in the R11 session (2026-08-24, `result.md` §3):** Q23 = (b) signed context,
  no redirect · Q24 = yes, h1 종목명 + 종목코드/고유번호 meta + the input echoes the name · Q25 = hide
  the strip on non-① stocks (no sentence) · Q26 = keep the R4 rule, logged as decided · Q27 = layout +
  **one** prompt string (dated exception). Pending the operator's literal signoff.
- **Q28 (R11 read-back) — is the `.mmcap` caption signed copy?** The landed cards/contract render
  「유상증자 {n}건 · 집계 범위 {start} ~ 오늘 (KST) · 시장 가격 미사용 — 소멸된 증서의 이론가치 환산」
  under the 놓친 돈 frame; `result.md` §4 lists only the prompt as new copy. (a) sign it as written →
  register in `copy-inventory.md` and `copy.ts`; (b) compose only from `coverageCaptionKo` + the
  existing 「유상증자 {n}건」 count, dropping the unregistered tail. Default at signoff: **(a)** if the
  signoff covers the cards as landed. **Answered 2026-08-24: (a)** — the signoff covered the cards as
  landed; the apply slice registers the caption as signed copy (SIGNOFF.md R11).
- **Q29 (`P8.S9`) — ① 구주주 청약 · 일반공모 windows are drawn but not served.** R11 §2's `.rowline`
  prints the two subscription windows; the stock route serves no `subscription_agents` field and no
  일반공모 window, and `offering.subscription` is typed `unknown` and read by no surface. The apply
  slice **omitted the line** (the signed read-back says "rendered from served fields only … no new
  payload"). (a) leave it omitted and drop `.rowline` from the record at the next round; (b) extend
  `GET /stocks/{corp_code}` in a later phase so the designed line can render. Default **(a)**.
- **Q30 (`P8.S9`) — ③ step windows are `fields: {}` on this route.** 아시아나's 2단계 절차 renders
  with two dashed 「현재 버전 공시에 없음」 chips, because the only ③ in the corpus arrives with no
  fields on `/stocks/{corp_code}` (the same filing **does** carry them on the event detail route).
  (a) accept the dashed form as the honest state here; (b) file a job to carry the ③ procedure
  fields onto the stock route so 조회 and 상세 agree. The dated form is browser-verified via a
  read-only stub, so (b) is presentation-ready. Default **(a)** + a deferred job for (b).
- **Q31 (`P8.S9`) — `.bofftitle` has no 결의일 to print.** The card prints 「2026-03-26 결정
  유상증자」; `_lapse_row` composes no 결의일, and reintroducing the corp name is exactly the
  repetition R11 §5 removed. Rendered as 「유상증자」 alone. (a) keep it; (b) carry the 결의일 onto the
  lapse row later so the designed title can render in full. Default **(a)**.
- **Q32 (`P8.S9`) — 집계 범위 on the entry page has no dates to state.** `lapse.coverage` rides
  `GET /stocks/{corp_code}` only and `/board/summary` carries none, so `/stocks` renders the
  boundary **sentence** with no dated rows. (a) keep the undated sentence; (b) serve the coverage
  dates on a stockless read so the entry page can date its own boundary. Default **(a)**.
- **Q33 (`P8.S9`) — the label-tier R11 strings, registered under the Q28 precedent.** 보유 · 배정비율
  (1주당) · 초과청약 비율 · 공시 · 소멸 계산 (시장 전체) · 종목코드 · 고유번호 · 접수 appear in
  build-prompt §2/§4/§5 and in the landed cards, but the round's `result.md` §4 lists only the prompt
  sentence as new copy. They were registered in `copy.ts` + the `copy-inventory.md` R11 tail on the
  same reasoning that answered Q28 (the gate signed the cards **as landed**). Confirm that reading,
  or name any label to be reworded. Default: **confirm**.
- **Q34 (`P8.S9`) — 390px heights fall short of the record's targets, and the canon is why.** R11
  targets ≈1,250 (한화) / ≈1,150 (풍전); the built pages measure 1,572 / 1,754 — real reductions of
  8.8% / 15.5%, but not the numbers. Measured against the canon itself in a `file://` harness, the
  canon's own `.ctrow` is 252px at 390 where the product's is 273px, with the same
  `.ctwhen`-above-`.ctfiled` stagger — i.e. the shortfall is the signed geometry's own height, not a
  fidelity defect. (a) accept the built heights as faithful; (b) open a follow-up density round for
  the ② row and the 놓친 돈 breakdown at 390. Default **(a)** + a deferred job for (b).

- **Q35 (R12 Q-A) — the English validation bubble (P7 Q12).** (a) keep the browser's native messages,
  (b) `noValidate` + one Korean line in the error slot (dated exception), (c) `noValidate` and let the
  existing Korean API errors answer. Default **(c)** if the session agrees they cover it; else (b).
- **Q36 (R12 Q-B) — where login from an offer lands.** Today always `/portfolio`; carrying the origin
  is feature-ish. Default: **keep `/portfolio`; the offer copy may say where it leads**.
- **Q37 (R12 Q-C) — a password rule stated up front** (「8자 이상」 hint) — new copy or error-only.
  Default: session decides; if a hint, one string (dated exception).
- **Q38 (R12 Q-D) — page frame on the auth pages** — a 「← 관제 현황판」 rail like every other surface,
  or R5's bare centered panel. Default: session decides (no new copy either way).

## Constraints

- **No new features.** Polish only — every round's handoff says so, and an apply slice that finds
  itself building capability has left the phase's scope.
- **RESPECT THE DESIGN.** Never drop, simplify, restyle or "improve" a designed element; where a value
  is unspecified pick the option closest to the designed intent, never a plainer fallback. Polish
  rounds R8–R15 **supersede** parts of R1–R7 — precedence is `SIGNOFF.md`'s, read it first — but an
  apply slice never restyles anything the round did not sign, and a design gap is **catalogued on
  `## Operator Questions`, never invented or silently fixed**.
- **The design record is read-only**; `docs/reference/design/rounds/*/output/**` is never edited. The
  vendored `tokens.css` / `fonts.css` are landed artifacts, not source.
- **Korean-only product surface, zero Korean minted** outside a signed round; every string enters
  through a surface's `copy.ts` with a citation.
- **Every browser claim is made in the operator's runtime** — `## Operator Runtime` in
  `docs/current/operations.md`: `make stack-up`, `http://127.0.0.1:3000` in Chrome desktop plus the
  tailnet URL, `next dev`, mobile viewport for every surface — **and additionally in the production
  build** (`cd frontend && npm run build && npm run start`) when the two could differ. If that
  section ever goes absent or `UNFILLED`, a slice stops and asks rather than assuming.
- **`co-work` slices are run inline by the orchestrator and never dispatched** (no `DesignSync` in an
  executor), and they never write implementation code. An apply slice's `plan.md` is written **only
  after** its round's SIGNOFF.
- **Docs are versioned once, at `P8.REVIEW`.** Slices append to `## Doc impact` above; nobody runs
  `doc-new-version` before the review, and `docs/current/*.md` is never hand-edited.
- **The phase's acceptance gate is expected `required`** — P8 changes operator-visible surfaces
  everywhere. The orchestrator declares it right after this slice; executors never run `accept-gate`.
- **Regression floor for every apply slice:** `pytest` green (139), `workflow validate` clean,
  `cd frontend && npm run build && npm run typecheck && npm run smoke` green (15/15), and the whole
  `## Regression Checklist` re-run — not only this phase's lines.

## Open Questions

- Tracked as **`## Operator Questions`** above (Q1–Q4 at decomposition), which is the list the review
  must route. Nothing else is open at cut time.
