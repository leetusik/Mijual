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

## Doc impact

_Running list — one line per durable-truth change, consolidated into doc versions by `P8.REVIEW` (not
in parallel mode, so consolidation happens at the review)._

- `P8.DECOMP`: none — this slice wrote no code and no docs.
- `P8.S1`: **qa** — `## Regression Checklist` gains `- [ ] AI 질문: ask → reload → ask again renders two distinct turns, no duplicate-key warning, 재시도 hits the right turn (P8)`. No other durable truth moved: `lib/ask.ts`'s persisted shape (`Persisted.v === 1`, legacy `t1…` ids still hydrate) is unchanged, so `frontend` needs no new version for this slice.

## Operator Questions

_Questions only the operator can answer; every entry is routed at the review -- folded into the acceptance walkthrough (`accept-gate --open`) or filed with `defer-job`. An unrouted entry is a review finding._

- **Q1 — inherited P7 decisions: answer them inside each surface's round, or up front?** P7 left 13
  operator decisions unanswered (table above). This decomposition assumes **each surface's design
  slice hands the operator its inherited items together with the walk's own findings**, so they are
  decided where they are visible. If the operator would rather settle some of them before any round
  starts (Q3's board window is one constant; Q13 is housekeeping), say so at the first `pending`.
- **Q2 — 의견 (vocky) still has nothing to bind to.** `NEXT_PUBLIC_VOCKY_SRC` is unset and vocky ships
  no embeddable script, so all three signed chrome triggers are dead controls. R8's walk will meet
  them, and **no slice may invent a URL**: the operator must supply the script/capture path, or decide
  that 의견 routes elsewhere (the AI 질문 agent already has a 의견 tool). Until then surface 1 cannot
  honestly claim "every visible control does something".
- **Q3 — does chrome polish include the 404 page?** It is Next.js's default page, it carries the one
  English sentence a Korean-only reader can reach, and it belongs to no signed round. Folding it into
  R8 means designing a page the record never drew (still polish, not a feature); leaving it means the
  English sentence ships. Operator's call at R8's handoff.
- **Q4 — is copy in play this pass?** `design-cowork` locks copy by default and the whole product
  leans on it ("inventing a Korean string is a design change"), but "audit and polish the whole
  thing" plus P7 Q7's four developer-vocabulary strings suggests some rounds need copy explicitly
  **in play, named and dated in that round's handoff**. Blanket answer, or per round?

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
