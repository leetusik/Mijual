# Phase P7: 실서비스 정상화 fix pass

_Intent: see [intent.md](intent.md)._

## Objective

P5/P6 shipped but the running product is broken or rough in 11 confirmed ways (nav cleanup, search typeahead, focus rings, board pagination + dead 펼치기 toggles, unreachable login, static countdowns, state-stomping auto-refresh, dead AI 질문 send, disorganized sample portfolio + inert 챙겼습니다 action, self-narrating implementation copy, missing AI 질문 widget). Fix all 11, verifying each fix against the signed P3 design (RESPECT THE DESIGN) and in a real browser. Runs before P4 Ship & Submit.

## Context

**The headline finding of `P7.DECOMP`: six of the eleven complaints are one bug, and it is not
in the product.** `next dev` refuses to serve two client chunks and the HMR socket to a browser
whose origin is not `localhost` — and the operator's own URL, the one `make stack-status`
prints, is `http://127.0.0.1:3000`. The page renders (it is server-rendered), **hydration never
completes**, so nothing on it is interactive and Next's own dev client reloads the tab on its
failed HMR reconnect. Everything the operator reported as "dead" is alive on
`http://localhost:3000` — measured, not assumed (§Findings, item RC-A).

That reframes the phase. Only five of the eleven are product changes; four of those five are
**operator overrides of the signed record**, which is what most of the design work here is.

## Decomposition

| slice | order | risk | covers (operator item #) | why it is cut this way |
|---|---|---|---|---|
| `P7.S1` | 1 | high | **4b, 6, 7, 8, 11** (+ the dev half of 5, 9) | One root cause (RC-A: Next dev-origin block). Fixing it makes six complaints evaporate; every later slice's browser verification depends on it, so it goes first. Must **re-verify each of those items on the operator's own origins** and report which are closed with no further code. |
| `P7.S2` | 2 | high | **5** (login) | RC-B: a different, origin-independent bug (`useAccount`'s StrictMode double-effect). One file, but real reasoning + a full 로그인/로그아웃 round trip to verify. |
| `P7.S3` | 3 | high | **4a** (board length) | The list-length half of item 4 is a real product change (386 rows rendered at once). Separate from S1's 펼치기 half because it needs a control and a copy decision. |
| `P7.S4` | 4 | high | **2** (typeahead) | The largest single piece: **needs a new API route** (no candidate endpoint exists, by an explicit product decision) *and* an unsigned UI element. Cohesive enough to stay one slice; big enough to be alone in it. |
| `P7.S5` | 5 | high | **3** (focus) | System-wide a11y treatment (`app/shell.css` + the search rows). Independent of every other item. |
| `P7.S6` | 6 | **low** | **1** (nav) | Verified to be exactly a `NAV_LINKS` entry removal and nothing else — the label constant is used independently elsewhere and `NAV_LINKS` is read only by `Nav.tsx`. The one `mid`-tier slice in the phase; this is the phase's cost lever. |
| `P7.S7` | 7 | high | **10** (self-narrating copy) | A sweep across several `copy.ts` files, and every hit needs the judgment "narration or trust claim?" — one of them is a signed privacy promise. |
| `P7.S8` | 8 | high | **9** (portfolio) | Layout fidelity + the 챙겼습니다 behaviour, both on the same surface. |
| `P7.S9` | 9 | high | **all 11** | The final real-browser sweep, the way `P5.S19`/`P6.S7` ran — but this time **in `next dev` as well as the production build, and on the operator's own origins**, which is the gap that let all of this ship. |
| `P7.REVIEW` | 9999 | high | — | Phase review; consolidates the Doc impact list below into doc versions. |

**No `co-work` slice and no `DECOMP2`** — the operator ruled out a new design round ("respect the
design, double check everything"). Every collision below is resolved *against the landed record*,
not by inventing a visual decision.

**Deliberately not cut:** a "landing liveness" slice for items 6/7. There is **no auto-refresh
feature in this app at all** (no `router.refresh()`, no polling, no `<meta refresh>` — grepped),
and the countdown's `setInterval` is correct. Both complaints are RC-A artifacts and close in S1.
If the operator still wants a *data* auto-refresh after S1, that is **new behaviour no round
specifies** — a deferred job, not a P7 fix (Open Questions Q5).

## Findings & Notes

### RC-A — `next dev` blocks the operator's own origin; six complaints are this one bug

**Seat:** `frontend/next.config.ts` (no `allowedDevOrigins`) + `Makefile` `web-up`
(`next dev -H 0.0.0.0`) and `stack-status` (prints `http://127.0.0.1:3000` and the Tailscale URL).

**Mechanism, read out of Next's own source**
(`frontend/node_modules/next/dist/server/lib/router-utils/block-cross-site-dev.js`):

```js
const allowedOrigins = ['**.localhost', 'localhost', ...allowedDevOrigins ?? []];
if (hostname) allowedOrigins.push(hostname);   // hostname = the -H value = "0.0.0.0"
```

So the allow-list is exactly `**.localhost`, `localhost`, `0.0.0.0`. **`127.0.0.1` is not on it**,
and neither is the Tailscale IP. Any request to a `/_next/*` internal asset (or the HMR
WebSocket) that carries an `Origin`/`Referer` from another host gets **403 + "Unauthorized"**.

**Measured in headless Chrome (CDP), same dev server, three origins:**

| | `localhost:3000` | `127.0.0.1:3000` | `100.77.164.42:3000` (Tailscale) |
|---|---|---|---|
| client chunks 403 | 0 | **2** | **2** |
| HMR WebSocket | connected | **handshake fails** | **handshake fails** |
| AI 질문 launcher in DOM | **1** | **0** | **0** |
| `position: fixed` nodes | 2 | 1 | 1 |
| countdown ticks over 2.5 s | **yes** | no | **no** |
| 펼치기 click → rows | 386 → **446** | — | **386 → 386 (dead)** |
| typed input after 30 s | **kept** | — | **page reloaded, value wiped** |
| board rows rendered | 386 | 386 | 386 |

The two blocked chunks are `_next/static/chunks/_03keo62._.js` and
`node_modules_next_0o9ro4l._.js`; the dev server logs `⚠ Blocked cross-origin request to Next.js
dev resource … from "127.0.0.1"` for each (see `var/stack/web.log`).

**What this closes, item by item:**

- **8 (AI 질문 send dead)** — not a product bug. On `localhost` a full turn streams end to end:
  tool rows (`이벤트 검색 「계양전기」 → 1건`, `이벤트 읽기`), the answer sentence, the verbatim
  citation, the API-tier citation, the footer (`근거 1건 · 20260724000546 · … KST`) and the
  three links. The agent, the SSE path and the store are all fine.
- **11 (no widget)** — the launcher is simply not mounted, because `AskSurface`'s `useDesktop()`
  runs in an effect that a broken hydration never reaches. **The ≤480px design rule is not the
  explanation** (operator confirmed: full-width desktop Chrome on this Mac).
- **4b (펼치기 does nothing)** — `Board.tsx`'s `Strip` toggle is correct and works on `localhost`
  (386 → 446 rows). Not a P6 regression.
- **6 (countdown static)** — `Countdown.tsx`'s `setInterval` is correct and ticks on `localhost`.
- **7 (auto reload stomps typing)** — there *is* no auto-refresh in the app. This is Next's own
  dev client reloading the tab after its HMR socket is rejected. Reproduced: typed `계양` into
  the hero input, waited 30 s, the document reloaded and the value was gone.
- **9's inert 챙겼습니다** and **5's dead login form** are the same dead hydration on that origin.

**For `P7.S1`:** the fix is `allowedDevOrigins` in `next.config.ts` (plus whatever the Makefile
should print/open). Note the Tailscale IP is not stable across machines — a wildcard or an env
seam is worth considering; `isCsrfOriginAllowed` supports `**.`-style patterns. **`next start`
does not do any of this** — the block is dev-only, which is exactly why `P5.S19` and `P6.S7`
never saw it.

### RC-B — item 5: the account slot can never answer in dev (StrictMode double-effect)

**Seat: `frontend/components/chrome/useAccount.ts:74-84`.**

```js
useEffect(() => {
  if (probedPath === pathname) return;   // module-level guard
  probedPath = pathname;
  let live = true;
  void fetchAuthState().then((next) => {
    if (live && probedPath === pathname) setAccountState(next);
  });
  return () => { live = false; };
}, [pathname]);
```

`next.config.ts` sets no `reactStrictMode`, and Next's `define-env.js:149-151` turns that into
`__NEXT_STRICT_MODE_APP = true` — **the App Router tree is wrapped in `React.StrictMode`**, which
double-invokes effects in development. Run 1 sets `probedPath`, starts the fetch, then its
cleanup sets `live = false`. Run 2 sees `probedPath === pathname` and **returns immediately**.
The only answer on the wire is therefore discarded, `state` stays `null` forever, and
`AccountSlot` renders an empty `<div>` (desktop, line 145) / `null` (sheet, line 210).

**Measured on `localhost:3000/` (a hydrating origin, fresh profile):** `로그인` anchors in the
document: **0**; app-issued `GET /api/auth/me`: **1**, status **200**; the slot's markup:
`<div class="AccountSlot-module__9OdIDG__slot"></div>`. So: the API is healthy, the session
plumbing is healthy — **the chrome simply never renders an entry to login.** That is the whole
of "no login exists". `/auth/login` itself renders correctly when typed as a URL (이메일 /
비밀번호 / 로그인 / 계정 만들기 / 비밀번호 재설정 / the PII inset / the sample entry all present).

Two things the fixing slice must know:

1. **`components/auth/useAuthState.ts` has the same shape but is NOT broken** — its guard is
   component state (`state !== null`), so StrictMode's second run *does* re-fetch and it
   self-heals. The defect is specific to the module-level `probedPath` + `live` pair. Do not
   "fix" the auth one.
2. **A loaded 샘플 outranks the account slot** (`AccountSlot.tsx:132`) — with
   `mijual.portfolio.sample` in `localStorage` the slot renders 샘플 chip + 샘플 종료 and never
   로그인, by R5-4's signed rule. Clear the sample before judging whether 로그인 is back.

### 의견 (vocky) — a third, separate cause, and it is an operator decision

The operator's verbatim list says "의견 doesn't work", and the confirmed intent folds it into
item 8 — but it is **not** the same bug. `components/chrome/VockyScript.tsx` renders **nothing**
when `NEXT_PUBLIC_VOCKY_SRC` is unset (it is unset; there is no `.env` in `frontend/` and the
repo-root `.env` carries only `DART_API_KEY` / `GEMINI_API_KEY`). The three signed
`data-vocky-trigger` elements then have nothing bound to them and clicking 의견 does nothing —
**which is the documented, deliberate state**: `frontend` v0004 Open Questions and `P5.S19`'s
catalogue item 17 both record that *vocky ships no embeddable widget script*.

**No slice may invent a script URL** (inventing a fact about someone else's system). This needs
the operator — see Open Questions Q1. It is deliberately **not** assigned to a slice.

### Item 1 — nav: verified to be a one-entry removal

`NAV_LINKS` (`frontend/components/chrome/copy.ts:55-59`) is read **only** by `Nav.tsx` (desktop
links, line 100; mobile sheet, line 145). `STOCKS_LABEL_KO` (line 50) is imported independently
by `components/lookup/LookupHeader.tsx` (the page H1), `components/ask/links.ts`,
`components/ask/copy.ts` and `components/lookup/copy.ts` — so removing the nav entry leaves the
constant in use and breaks no import. The 조회 surface stays reachable from the landing hero, the
R3 detail link-out and the agent's link row.

### Item 3 — focus: the blue box is the record's own token, and the geometry is exact

- `frontend/app/shell.css:107-111`: `:focus-visible { outline: 2px solid var(--focus-ring);
  outline-offset: 2px; }` — the only outline rule in the app.
- `--focus-ring: var(--r1)` in `public/foundations/tokens.css:29`, and `--r1` is the **① 유상증자
  rights hue**: `#2b5aa0` light, **`#8fb2e8` in the `.cosmos` scope** (measured in the browser).
  So the "annoying blue box" is not a UA default leaking — it is R1's own token, aliased to a
  rights colour.
- **The clipping is geometric and measured** on `/stocks` at 1440: input rect
  `x=184, w=472` → right edge **656**; the 조회 button rect starts at **656**. **Gap = 0.** A 2px
  outline at `outline-offset: 2px` therefore paints 4px *under* the adjacent button — exactly
  "its right side covered by 조회 box".

### Item 4a — board length

`GET /board` serves **386 ranked rows** (+ `open_now` 60, `tbd` 4; `counts.all` 488; 160 KB), and
`Board.tsx` renders every ranked row. R2 specifies the sort and the row anatomy but **no limit**
and no pagination control — `P5.S3` note 11 records "the design paginates nothing" as the reason
the whole board is one request. The operator's 60건 / 4건 quotes match `open_now` / `tbd` exactly.

### Item 2 — typeahead needs a backend route, and it collides with a stated product rule

There is **no suggestion endpoint**. `GET /stocks?q=` (`src/mijual/web/routers/stocks.py`)
resolves exactly one issuer or returns `{"query": …, "found": false}`, and both the module
docstring and `mijual.web.reads.resolve_corp` state the rule in as many words: *"never a
candidate list, because no signed surface renders one and a guess that opened a different
company's 놓친 돈 is the one defect class this product cannot ship."* `resolve_corp` is a
four-tier resolver (exact ticker → verbatim name → normalized name → **unique** normalized
prefix) that treats ambiguity as a miss. The corpus is ~614 `Corp` rows, so a prefix/substring
suggestion query is cheap.

### Item 9 — the 챙겼습니다 checkbox is faithfully built; the complaint is mostly RC-A

`components/portfolio/Deadlines.tsx:237-315` implements R5-8 literally: check → label 놓친 돈 →
**챙긴 돈**, same amount, 「추정」 kept, alert → live hue, caption swaps. It is a `<input
type="checkbox" onChange>` — dead on an un-hydrated origin, which is what the operator clicked.
The sample page's live content (measured) is 4 holdings, 2 upcoming deadlines, **3 past rows**,
two of which carry the 챙겼습니다 check and the `본인 표시 · 이 브라우저(localStorage)에` caption.

### Item 10 — the self-narrating copy, inventoried

Rendered strings (not comments) matching the pattern:

| file:line | constant | string |
|---|---|---|
| `components/portfolio/copy.ts:189` | `CLAIM_CAPTION_LOCAL_KO` | `본인 표시 · 이 브라우저(localStorage)에` ← the operator's literal example |
| `components/portfolio/copy.ts:188` | `CLAIM_CAPTION_ACCOUNT_KO` | `본인 표시 · 계정에 저장` |
| `components/portfolio/copy.ts:103` | `HOLDING_CAPTION_KO` | `계정에 저장 · 마감 알림의 기준` |
| `components/lookup/copy.ts:96` | `HOLDING_CAPTION_KO` | `브라우저 세션에만 저장 · 서버 전송 없음` |
| `components/ops/copy.ts:215` | `ANONYMOUS_PROMISE_KO` | `대화는 익명으로 저장됩니다 (품질 점검용)` (also rendered in the AI 질문 empty state) |

The sweep slice must re-run it rather than trust this table — it was cut from a keyword grep
(`localStorage|브라우저|세션|저장|본인 표시|서버 전송`) over `components/*/copy.ts` and the
`*.tsx` that render literals.

### Design-collision readings (recorded here so the slices inherit them, not re-argue them)

The framing is the operator's: *"respect the design, double check everything"* — **no new design
round**, so where an ask collides with the record the slice implements **what the record says**,
and where the operator is overriding the record it does **only** the override and restyles
nothing around it.

1. **Item 3 (focus) — the record has a floor here, and it stays.** `frontend` v0002/v0004 state
   "Focus ring: 2px `--focus-ring`" as the a11y floor, and R2 §vocky spells "focus = 2px
   `--focus-ring`" for the triggers. So "no selected focus on all the input boxes" cannot be
   read as *delete the outline rule*. **Reading: the defect is the treatment, not the
   existence.** The blue is a rights hue that means ① elsewhere in this product, and
   `outline-offset: 2px` is what pushes it under the zero-gap 조회 button. A record-faithful fix
   changes the *inputs'* focus treatment to something inside R2's own console-field idiom (its
   stated hairline `rgba(163,196,180,.4)`, brightened; or an inset ring that cannot overflow),
   keeps a visible **keyboard** indicator on every focusable element, and leaves the signed
   button/trigger focus state alone. Never leave an input with no keyboard-focus indicator at all.
2. **Item 1 (nav) — an explicit operator override, scoped to the slot.** R2 signs a three-slot
   nav and R5-6 explicitly *withdrew* a fourth link ("내 포트폴리오는 links가 아니라 계정 메뉴
   첫 행"); R4 and R6 only re-labelled slots. Removing 내 종목 조회 leaves a **two-slot** nav,
   which no round drew. `intent.md`'s clarification covers it. **Reading: remove the entry and
   nothing else** — no re-centring, no re-spacing, no new slot, and the label constant stays
   where other surfaces use it. Note the two P5 catalogue items that get *more* visible
   afterwards: the footer's locked positioning line still says **내 종목 연결** (#4) and the hero
   H1 says **내 종목 조회** where R2's literal says 내 종목 연결 (#12). Neither is P7's to rewrite.
3. **Item 4a (board length) — the record paginates nothing, so the control is new.** R2 draws no
   "더 보기" and inventing a Korean string is a design change. **Reading: reuse the record's own
   disclosure word (펼치기, already signed on both strips) rather than mint a new label**, keep
   the signed row anatomy and the whole-board tab counts unchanged (`counts` is always
   whole-board — 전체 must keep reading 488), and never drop a row from the corpus: this is a
   *display* limit, not a filter. Any new string the slice cannot avoid goes in Doc impact and
   into the review's operator questions.
4. **Item 2 (typeahead) — the override that needs the most care.** The "never a candidate list"
   rule exists to prevent *the system* silently opening the wrong company. A reader **choosing**
   from a list is the opposite of a silent guess. **Reading: the rule survives if the suggestion
   is a choice** — every candidate carries its 종목코드 and navigates by `corp_code` (the exact
   handle, `GET /stocks/{corp_code}`), never by re-running a fuzzy resolve; typing and submitting
   without choosing keeps today's four-tier `resolve_corp` behaviour, including 검색 불일치 on an
   ambiguous prefix. The dropdown is an unsigned element: build it in the surrounding signed
   idiom (radius 0, hairline border, `--surface-inset`/console-field colours, fade-only motion,
   mono for the 종목코드, sans for the name) and invent the **minimum** copy. The API doc's rule
   sentence changes, so this is a Doc impact line (`api`, and `product`/`experience` if the
   surface's promise moves).
5. **Item 9 (챙겼습니다) — R5-8 says re-label, not delete.** The signed post-gate addition is
   「금액 동일(「추정」 유지), alert → live, 라벨 놓친 돈 → 챙긴 돈, 캡션 본인 표시」 and
   "사용자 주장 표시 — 공시 데이터와 혼동 금지". **Reading: implement the record — the 놓친 돈
   *framing* leaves (label + alert hue), the row and its figure stay** — and make sure the change
   is actually visible once the page hydrates. If the operator still wants the entry to
   disappear, that is a new decision (Open Questions Q4), not a slice's call.
6. **Item 10 (self-narrating copy) — separate the narration from the promise.** Two of the hits
   are signed *trust* sentences, not implementation chatter: `브라우저 세션에만 저장 · 서버 전송
   없음` is R4's build-prompt §3 literal, and the whole anonymous-first boundary leans on it —
   `api.md` records that `GET /stocks` has **no `n` parameter** precisely so that sentence stays
   true. **Reading: strip the mechanism ("localStorage", "이 브라우저"), keep the promise
   ("서버 전송 없음", the AI 질문 anonymity line).** Anything the slice cannot cleanly classify
   goes to the operator as a review question rather than being deleted.

## Constraints

- **RESPECT THE DESIGN.** `docs/reference/design/` is read-only; a nit is an apply-time to-do,
  never a record edit. Read `SIGNOFF.md` before any `build-prompt.md`; the supersession chain is
  in `docs/current/frontend.md`. Where P7 overrides the record it does so **only** where
  `intent.md` says so, and restyles nothing around the override.
- **Inventing a Korean string is a design change.** Copy comes from the owning surface's
  `copy.ts` with a citation per entry. Where P7 must mint one (S3's list control, S4's dropdown),
  keep it minimal, cite it as a P7 operator override, and list it for the operator at review.
- **The operator's runtime is `next dev`, not `next start`.** `make stack-up` runs
  `next dev -H 0.0.0.0 -p 3000`; the operator browses `http://127.0.0.1:3000` on this Mac and the
  Tailscale URL from another device. **Every fix must be verified in `next dev` (React StrictMode
  double-invokes effects there) *and* in `next build && next start`, and on a non-`localhost`
  origin where it matters.** Verifying only the production build on `localhost` is exactly the
  gap that let all eleven of these ship (`P5.S19`, `P6.S7`).
- **A browser-probe FAIL is a hypothesis, not a finding** (`frontend` v0004) — re-measure with a
  scoped selector before believing one.
- **`npm run start` fails silently into its log with `EADDRINUSE`** if an older `next start` holds
  :3000, and the stale server then serves 500-ing CSS chunks. Kill the listener and confirm a CSS
  chunk returns 200 before believing a measurement. **Do not run `next build` against the same
  `.next` directory the dev server is using** — either stop the dev stack first or build on a
  separate port/dir, and leave the stack as you found it (`make stack-status`).
- **`MIJUAL_API_ORIGIN` is read at build time** by `next.config.ts`, so repointing the proxy
  locally means rebuilding.
- **Trust rules are untouched by this phase**: an estimate never renders untagged and a fact never
  carries the mark; no money before 확정발행가; ②/③ rows never carry a won amount; D-days are
  computed upstream in KST; 추후결정 never beside a date; a gate-failed field renders as nothing;
  a past ② is 진행 중, never 종료. No P7 fix may weaken one.
- **No `doc-new-version` in a fix slice.** A slice that changes durable truth appends a one-line
  note to *Doc impact* below; `P7.REVIEW` consolidates them on a pass.
- **Tests stay terse** (repo rule): the backend baseline is `.venv/bin/python -m pytest`
  (59 passed, ~1 s, no network, no model); the frontend has `npm run typecheck` and
  `npm run smoke` (`node --test lib/*.test.ts`) and **no test framework** — do not add one.
- **Korean-only product surface; English for work, notes and commits.**

## Doc impact

_One line per durable-truth change; `P7.REVIEW` consolidates these into doc versions._

- `frontend` — **the `P5.S19` browser-check note is incomplete and, as written, misleading.** It
  says to check over `localhost` rather than `127.0.0.1`; the real rule is that `next dev` bound
  to `0.0.0.0` serves its dev resources **only** to `localhost` unless `allowedDevOrigins` names
  the host, and that an un-hydrated page looks exactly like six separate product bugs. (Recorded
  by `P7.DECOMP`; the slice that fixes it should extend this line.)

## Open Questions

- **Q1 — 의견 (vocky) has nothing to bind to.** `NEXT_PUBLIC_VOCKY_SRC` is unset and vocky ships
  no embeddable widget script (`P5.S19` catalogue #17). The three signed triggers therefore do
  nothing, by design. **The operator must either supply the script URL / capture path, or decide
  that 의견 routes somewhere else** (the AI 질문 agent already has a 의견 tool that saves
  feedback — reusing it would be a product decision, not an implementation one). No slice owns
  this today, and no slice may invent a URL.
- **Q2 — how far does "no selected focus on all the input boxes" go?** The slices implement
  collision reading 1 (keep a keyboard-visible indicator, change the treatment). If the operator
  literally wants *zero* focus indication anywhere, that removes the record's a11y floor and
  needs their explicit call.
- **Q3 — how many firms is "some amount"?** The board serves 386 ranked rows. S3 must pick an
  initial count and a disclosure; the number is not in any record.
- **Q4 — should a 챙겼습니다 row disappear?** R5-8 signs re-label + hue change, same figure. If
  the operator wants the row gone from 지나간 마감, that supersedes a signed round.
- **Q5 — does the operator want live data refresh?** After S1 the countdown ticks and nothing
  stomps typing, but the board's data is still only as fresh as the last page load (the freshness
  chip states the 기준시각 — "stale, never dark"). A polling refresh is behaviour no round
  specifies; a deferred job if wanted.
- **Q6 — P5.S19 catalogue items P7 brushes against, none of them P7's to decide:** #4 the footer's
  locked 내 종목 연결 line and #12 the hero H1's name (both get more visible once the nav slot
  goes); #6 the sample's signed 4건 subline above five live D-day rows (S8 will see it while
  tidying); #10 `[근거]` + DART link under the mobile 44px floor; #1 the English 404 sentence —
  the one English string a reader can reach, adjacent to item 10's copy sweep but not in it.
