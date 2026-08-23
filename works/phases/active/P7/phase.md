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

### RC-A closed — `P7.S1` measured, three origins, before and after

**The fix.** `frontend/next.config.ts` grows an `allowedDevOrigins` seam next to the existing API
seam: a static list (`127.0.0.1`, `[::1]`, `**.ts.net`) plus `MIJUAL_DEV_ORIGINS` (comma-separated
hosts) that `make web-up` fills from the same `tailscale ip -4` lookup `stack-status` prints. No
product code was touched.

**Why the tailnet IP is not in the static list.** Read out of 16.3.2's `isCsrfOriginAllowed`
(`next/dist/server/app-render/csrf-protection.js`) and exercised directly against that module: the
matcher compares **hosts only**, splitting on `.` and popping segments from the right, so
`**.ts.net` matches Tailscale MagicDNS names (`**` is legal only as the leftmost segment —
`100.**` is rejected), while an IPv4 literal can be matched only exactly or by whole-octet
wildcards. `100.64.*.*` matches `100.64.5.6` but **not** `100.77.164.42`, and the only pattern that
covers the tailnet, `100.*.*.*`, opens **all of 100.0.0.0/8** rather than Tailscale's
100.64.0.0/10. So the exact IP arrives through the env seam instead — verified still tight: with
the seam live, a `/_next/*` chunk fetched with `Origin: http://100.1.2.3:3000`,
`http://192.168.1.9:3000` or `http://evil.example.com` still gets **403**, while `127.0.0.1`, the
tailnet IP and a `*.ts.net` name get **200**.

**Measurements** (headless Chrome over CDP, `Emulation.setDeviceMetricsOverride` 1440×900, one dev
server, `/` unless noted). "before" = the original config restored on disk and the dev server
allowed to reload it, i.e. a genuine re-run of `P7.DECOMP`'s baseline in this session:

| | `localhost:3000` | `127.0.0.1:3000` | `100.77.164.42:3000` |
|---|---|---|---|
| `/_next/*` 403s — before | 0 | **2** | **2** |
| `/_next/*` 403s — **after** | 0 | **0** | **0** |
| HMR handshake — before | 101 | **none, 5 frame errors** | **none, 5 frame errors** |
| HMR handshake — **after** | 101 | **101** | **101** |
| AI 질문 launcher — before / after | 1 / 1 | **0 / 1** | **0 / 1** |
| `position: fixed` nodes — before / after | 2 / 2 | **1 / 2** | **1 / 2** |
| countdown ticks over 2.6 s — before / after | yes / yes | **no / yes** | **no / yes** |
| 펼치기 ① rows — before / after | 386→446 / 386→446 | **386→386 / 386→446** | **386→386 / 386→446** |
| 펼치기 ② rows — after | 446→450 | 446→450 | 446→450 |
| typed value after 150 s — before / after | kept / kept | **wiped at 40 s / kept** | wiped (DECOMP) / **kept** |

The two 403s are the same chunks every time — `_next/static/chunks/_03keo62._.js` and
`node_modules_next_0o9ro4l._.js`. `+60` and `+4` on the two strips match `open_now` 60 / `tbd` 4
exactly (useful for `P7.S3`).

**Item 7's reload takes ~40 s, not 30.** The first pass waited 30 s and saw the value survive on a
blocked origin — a near-miss false negative. A dedicated watcher on the un-fixed origin recorded
the top-frame navigation at **40 s** with the typed 계양 gone; after the fix all three origins hold
the value and the `window` marker for **150 s** with **0** navigations. Any later slice measuring
this must wait ≥60 s.

**Closed by this slice with no product code** (all measured on `127.0.0.1`, the operator's own
origin): **4b** 펼치기 (386→446, `aria-expanded` false→true), **6** countdown (ticks), **7** the
state-stomping reload (150 s, value kept, 0 navigations), **8** AI 질문 send (a full turn streamed:
`POST /api/ask` 200, 도구 행 「이벤트 검색 「계양전기」 → 1건 · ① 유상증자 · 20260724000546」 +
「이벤트 읽기」, the answer with four DART 원문 citations, 근거 footer), **11** the launcher (1 in
the DOM, 2 fixed nodes). The hydration halves of **5** and **9** are closed too: on
`/portfolio?sample=1` the 챙겼습니다 checkbox flips 놓친 돈 → **챙긴 돈** with the figure unchanged
(`679,575원` + 「추정」), and `/auth/login` round-trips — `POST /api/auth/login` → **401** and the
form renders 「이메일 또는 비밀번호가 일치하지 않습니다.」 (no account was created).

**Notes the later slices need:**

1. **The dev server reloads `next.config.ts` by itself** (`✓ Running next.config.ts took 14ms`), so
   a config edit goes live without a restart — but an **env** change does not. `MIJUAL_DEV_ORIGINS`
   only takes effect through `make web-up` (or `stack-down` + `stack-up`). This also means a config
   edit silently contaminates a "before" measurement taken after the edit.
2. **`P7.S2` (item 5): the login *form* is not broken** — it reaches the API and renders the signed
   error. What is missing is only the chrome's entry, which is RC-B. Also confirmed live: with a
   sample in `localStorage` the account slot renders 샘플 · 샘플 종료 and never 로그인 (R5-4's rule,
   `AccountSlot.tsx:132`) — my `/auth/login` probe shared a browser profile with the portfolio
   probe and hit exactly that. **Clear `mijual.portfolio.sample` before judging the slot.**
3. **`P7.S8` (item 9): the 챙겼습니다 behaviour is already correct**, so that half of the item is
   already done; what remains is the layout tidy — and the row's caption is item 10's literal
   example (「본인 표시 · 이 브라우저(localStorage)에」), which `P7.S7` owns.
4. **The production build was never affected and still is not.** `allowedDevOrigins` is read only
   by the dev router server (`router-server.js:207/336/669`, all behind `development`), and a
   `npm run build && next start -H 0.0.0.0 -p 3100` served **0** 403s, 1 launcher, ticking
   countdowns and working 펼치기 on **both** `127.0.0.1:3100` and the tailnet IP, with no HMR
   socket at all. That is the `P5.S19`/`P6.S7` gap in one line: **prod was always fine on every
   origin; dev was broken on every origin but `localhost`.**
5. **Reproducing the measurement.** Headless Chrome (`/Applications/Google Chrome.app/…`) with
   `--headless=new --remote-debugging-port=<p> --user-data-dir=<scratch>`, driven over raw CDP from
   Node 24 (global `WebSocket`); `Target.createTarget` + `Target.attachToTarget {flatten: true}`,
   then `Page`/`Runtime`/`Network`/`Log` enabled and `Emulation.setDeviceMetricsOverride`
   1440×900. Useful selectors: launcher `button[class*="launcher"]`, countdown
   `[class*="countdown"]`, 펼치기 = the `button`s whose text is exactly `펼치기`, board rows =
   `document.querySelectorAll('li').length`, composer `form[class*="composer"] input`. Type with
   `Input.insertText` (a controlled React input ignores a scripted `.value`). The scripts lived in
   session scratch and were not committed. The pre-fix dev log is kept at
   `var/stack/web.log.pre-p7s1` (gitignored) — 11 `Blocked cross-origin request` lines, all from
   the operator's own origins. The log since the restart has four, and all four are this slice's
   deliberate negative controls (`evil.example.com` ×2, `100.1.2.3`, `192.168.1.9`) — **none from
   `127.0.0.1` or the tailnet IP**.

### RC-B closed — `P7.S2`: the account slot answers, and the round trip works

**The fix is the removal of a cleanup flag**, one file
(`frontend/components/chrome/useAccount.ts`), no other product code:

```ts
useEffect(() => {
  if (probedPath === pathname) return;
  probedPath = pathname;
  void fetchAuthState().then((next) => {
    if (probedPath === pathname) setAccountState(next);   // no `live`
  });
}, [pathname]);
```

Two source facts make dropping `live` safe, both checked rather than assumed. (a) The state it
guarded is a **module** store that outlives every component, so an answer landing after a
subscriber unmounted is still the answer the next subscriber wants. (b) `lib/session.ts` shares the
**in-flight** probe, so StrictMode's two runs cost **one** request — and, less obviously, a stale
answer can never overwrite a newer one, because a second probe can only start after the first has
settled. The surviving `probedPath === pathname` check still drops an answer that lands after a
client-side navigation moved the reader.

**Measured on `127.0.0.1:3000` in `next dev`** (fresh profile, `mijual.portfolio.sample` cleared,
CDP at 1440×900 and 390×844):

| check on `/` | before | **after** | tailnet **after** |
|---|---|---|---|
| desktop slot markup | `<div class="…__slot"></div>` | **`<a class="…__login" href="/auth/login">로그인</a>`** | same |
| `a[href="/auth/login"]` in the document | **0** | **2** (desktop slot + sheet row) | **2** |
| mobile 390 sheet, opened | no 로그인 row | **로그인 present** | — |
| `GET /api/auth/me` per page load | 1, **discarded** | **1**, 200, **published** | **1**, 200 |

**The full round trip, one browser session, all client-side unless noted:** 로그인 clicked in the
chrome → `/auth/login` (0 document loads) → 계정 만들기 `POST /auth/signup` **201** → `router.push`
to `/portfolio` and the slot switches to the 축약 이메일 menu `p7s2…com` **with no reload** →
client-side nav to `/`, slot unchanged → menu rows 내 포트폴리오 / 알림 설정 / 로그아웃 → 로그아웃
**200**, fresh load, slot back to 로그인 + 「로그아웃되었습니다」 once → 로그인 again **200** →
알림 설정 → 계정 삭제 (arms, then `DELETE /auth/account` **200**) → lands `/`, slot 로그인 → the
same credentials now **401** 「이메일 또는 비밀번호가 일치하지 않습니다.」. **9 probes for 9 path
visits** — exactly one each. Production build (isolated copy, `next start` on :3100): 로그인
renders, 1 probe, 0 responses ≥ 400.

**Notes the later slices need:**

1. **StrictMode is on in `next dev` and it is the phase's second false-defect generator.** The
   pattern to distrust anywhere in this app: a **module-scope** guard claimed inside an effect plus
   a per-run cleanup flag = the work happens once and is thrown away, forever. `next start` runs
   the effect once and looks perfect. Any P7 slice adding an effect that writes to module state
   (S3's board control, S4's typeahead) should re-read this before trusting a dev measurement.
2. **`AccountSlot.tsx` needed nothing** — the probe fix alone makes it render, so R5's three
   renderings are intact. Re-verified while here: with `mijual.portfolio.sample` loaded the slot is
   still 샘플 + 샘플 종료 with **0** 로그인 anchors (R5-4 outranks, `AccountSlot.tsx:132`).
3. **`components/auth/useAuthState.ts` was left alone**, per the DECOMP note.
4. **Building without disturbing the dev server**: `next build` has **no `--dist-dir`** flag in
   16.3.2 (`distDir` is config-only), and Turbopack **panics on a symlinked `node_modules`**
   pointing outside the project root. A real copy of `frontend/` (sources + a copied
   `node_modules`, ~354 MB) into scratch builds and `next start`s cleanly, and leaves
   `make stack-status` untouched — cheaper than stopping and restarting the stack.
5. **Dev-DB leftovers that are not P7.S2's:** `account` still holds `s19-fidelity@example.com`
   (id 14) with one live `auth_session`, from `P5.S19`. `P7.S9` will meet it during its sweep;
   this slice's own throwaway (`p7s2-probe@example.com`) was deleted through the product's 계정
   삭제 and is verified gone.
6. **The one 4xx on a clean landing load is `/favicon.ico` 404** — pre-existing, in both the before
   and after runs. Nobody's item; worth not re-discovering.

### Item 4a closed — `P7.S3`: a 30-row display window, and zero new copy

**The change is two files in `components/landing/`** — `Board.tsx` (a `WINDOW_STEP = 30` constant, a
`shown` `useState`, `rows.slice(0, shown)`, a `selectTab()` that resets the window, and the
disclosure) and `Board.module.css` (one class, `.more`). No copy file, no API, no data, no other
component.

**Decision D-P7-1 — the number is 30, and a click adds 30.** No round names one: R2 draws the ranked
list with no length and no pagination control (`P5.S3` note 11, "the design paginates nothing"), so
this is an operator override of an unsigned gap. 30 is the horizon this same page already names in
the hero stat line (`30일 이내 마감`) and is short enough to read without the ② strip sliding off;
adding 30 per click rather than revealing all 386 is the whole of "some amount at a time" — a
reveal-everything button would put the page straight back where the operator found it.
**Open Question Q3 stays open until the operator confirms the number** (the review must put it to
them); nothing else about the board waits on that answer.

**Zero Korean strings were minted** — worth recording, because the DECOMP reading (#3) expected the
slice might have to mint one. The button is `EXPAND_KO` (펼치기) in the strips' own `styles.expand`
class, and beside it sits a mono `{count(hidden)}건` in `styles.stripCount` — the strips' exact
`60건` / `4건` idiom, carrying the exact same meaning it carries there (*what this click discloses*).
So the control says nothing the record has not already signed on this panel three times.

**Two shape decisions later slices should not re-argue.** (a) The control is deliberately **not** a
third pinned strip: `--surface-raised` + a hairline top is R2's marker for a *pinned* section, and a
third raised band between the rows and the ② strip would read as a section no round drew. It is one
`--space-5` line under the last dashed row, centred, carrying the strips' button verbatim. (b) The
button carries **no `aria-expanded`** — it is incremental, not two-state, so the attribute would sit
`false` forever and lie; the strips keep theirs.

**Measured on `127.0.0.1:3000` in `next dev`** (fresh profile, CDP at 1440×900 and 390×844; "before"
re-measured by restoring both files to `HEAD` and letting Fast Refresh reload, then restoring the
change):

| on `/`, 전체 tab | before | **after** |
|---|---|---|
| ranked rows rendered | **386** | **30** |
| the control | — | **`356건` + `펼치기`** (3 펼치기 buttons on the panel, was 2) |
| `<li>` in the served HTML | 395 | **39** |
| served HTML for `/` | 701,871 B | **369,151 B** (−47%) |
| document height 1440 / 390 | 17,730 / 30,806 px | **3,047 / 4,523 px** |
| tab counts | 488/50/422/16 | **488/50/422/16** |

Click-through: 30 → **60** (`326건`) → … → **386** in **12** clicks, then the control is **gone** and
only the two strips' 펼치기 remain. **0 network requests** across all 12 — it is entirely
client-side. Tabs: 유상증자 **14** rows and 매수청구 **10** rows show **no control at all** (nothing
to disclose, the same rule `Strip` keeps for a 0건 sentence); 전환사채 shows 30 + `332건`; every tab
switch resets the window and no tab count ever moves. Order preserved (first rows 계양전기 D-2 ·
라온텍 D-3 · 휴맥스 D-4). The strips are untouched: 30 → 90 (+60) → 94 (+4) → 30, the same `+60`/`+4`
`P7.S1` measured. The new button's computed border, radius, font, colour, background and width are
**identical** to the strip's, min-height 32px at 1440 and **44px** at 390, with **16px** between it
and the ② strip and no horizontal overflow at either width. Same results on the **Tailscale**
origin and in an **isolated production build** on `:3100` (build pass, 16 routes, port freed).

**Notes for later slices:**

1. **`P7.S9`'s sweep must count 30, not 386.** Any board row-count assertion inherited from
   `P5.S19` / `P7.S1` (386 → 446 → 450) now reads **30 → 90 → 94** at the first window. The 386 is
   still reachable — 12 펼치기 clicks — and the corpus is unchanged.
2. **No effect and no module state were added**, so `P7.S2`'s StrictMode trap could not apply here;
   `P7.S4`'s typeahead still has to worry about it.
3. **The dev server Fast-Refreshes a component edit in ~5 ms**, so a "before" measurement taken
   after an edit is contaminated the same way `P7.S1` found for `next.config.ts`. Restoring both
   files to `HEAD`, re-measuring and restoring the change costs about a minute and is worth it.
4. **`/favicon.ico` 404 remains the only 4xx on a clean landing load**, before and after, at 1440
   (not at 390) — still nobody's item.

### Item 2 closed — `P7.S4`: one search row, a chosen candidate, and the rule intact

**The reading held.** Collision reading #4 said the "never a candidate list" rule survives if the
suggestion is a *choice*, and the implementation is exactly that: a new read-only
**`GET /stocks/suggest?q=`** (≤ 8 candidates, `200` + `[]` for nothing, `q` is its only parameter)
feeds a listbox whose every option carries its 종목코드, and a chosen one navigates to
**`/stocks/{corp_code}`** — the exact handle, never a second fuzzy resolve. Submitting **without**
choosing is byte-for-byte yesterday's path: `?q=` → `resolve_corp`'s four unique-or-decline tiers
→ 307 onto the handle on a hit, R4's locked 검색 불일치 sentence on an ambiguous prefix. Both rows
still work with **JavaScript off** (measured with `Emulation.setScriptExecutionDisabled`: plain
`<form action="/stocks" method="get">`, no listbox).

**The two rows are now one component.** `components/lookup/SearchRow.tsx` (+ its module CSS) is
rendered by *both* the hero and `LookupHeader`, each passing its **own** form/input/button classes,
so R2's 560×52 row and R4's 48px row keep their signed geometry (measured unchanged, gap 0) and the
two surfaces cannot drift into two behaviours. `suggest_corps` sits beside `resolve_corp` in
`reads.py`; digits → `stock_code` prefix (+ the zero-padded exact), otherwise normalized-name
**prefix then substring**, tiers **unioned** — unlike `find_corps` (R6's agent tool), which stops
at the first tier that matches. **Invariant worth keeping:** every tier `resolve_corp` can hit is a
*prefix* hit in the suggestion list, so the row a bare submit would land on is always at the top.

**Zero Korean strings were minted** — the second slice in a row where the DECOMP reading expected
one might be needed (S3 was the first). A candidate is 회사명 (sans) + 종목코드 (mono); no heading;
an empty result renders **nothing**, because the submit already owns the 검색 불일치 sentence.

**Decision D-P7-2 — the hero's ring clip moved to `.orbits`, and it had to.** `.hero` carried
`overflow: hidden` to clip the two orbit rings (R2.1 §3: never shrink them). Measured at 1440, the
eight-option panel spans y 440→761 while the hero ends at **732**: its last option was clipped and
`elementFromPoint` there returned the Anchor craft panel below; at 390 it would have cut the list
in half. `.orbits` is `position: absolute; inset: 0` of the hero — **the same rectangle**, measured
identical afterwards (hero `[52,732,1440]` ≡ orbits `[52,732,1440]`) — so the rings are clipped by
the hero's own box exactly as the round says, while a panel hanging off the input can leave it.
Proof nothing else moved: `scrollWidth == viewport` at 390 **and** 1440 (the rings are 1251px
wide), and the document is **3,047 px** at 1440 / **4,523 px** at 390 — identical to `P7.S3`'s
numbers. **No other slice may reintroduce `overflow: hidden` on `.hero`.**

**Measured** (headless Chrome/CDP, fresh profile, `next dev` on `127.0.0.1`, **both `/` and
`/stocks`**, 1440×900 and 390×844; repeated once on the **Tailscale** origin and once against an
**isolated production build** on `:3100` — all four runs agree):

| check | result |
|---|---|
| suggest requests **on mount** | **0** — `typed` starts false, so StrictMode's double effect asks nothing |
| 4 chars @60 ms / @400 ms | **1** request / **4** requests (debounce ~150 ms, `AbortController` per keystroke) |
| clearing the box | **0** requests, list closed |
| `계양` / `에스` / `0122` | 1 (계양전기 012200) / **8** (7 prefix hits + 나노씨엠에스 substring) / 계양전기 + 삼미금속 |
| ↓ then Enter | `/stocks/01258020` — the handle — page rendered; a real mouse click → `/stocks/00102618` |
| `계양` + Enter **unchosen** | `/stocks?q=계양` → **307** → `/stocks/00102618` (unchanged) |
| `에스` + Enter **unchosen** | stays on `/stocks?q=에스` with ‘에스’와 일치하는 종목이 없습니다 (unchanged) |
| panel vs input | width equal, `dx=0`, `dy=0`, radius **0**, `border-top: 0`, options 44px@390 / 40px@1440, all hit-testable |
| panel ink | hero `rgb(10,19,16)` + `rgba(8,17,13,.72)` on `rgba(163,196,180,.4)`; /stocks the same base + `--surface-inset` on `--border-strong` |
| console | no errors, no warnings, **no hydration complaint** on `/`, `/stocks`, a miss page, a stock page |

**Notes later slices need:**

1. **`P7.S5` (focus): the input now sits inside `span.SearchRow.field`** (`position: relative;
   flex: 1 1 auto; min-width: 0`) — the panel's positioning context. Focus styling was **not**
   touched (`:focus-visible` still lands on the `input`), but an inset-ring approach now has a
   wrapper it can use, and must not assume the input is the form's direct child.
2. **A CDP Enter without `text: "\r"` fires no keypress**, so the form's implicit submission never
   happens and the product looks broken when it is not. `P7.S1`'s recipe needs that one addition;
   it cost a wrong reading here before it was caught.
3. **The live corpus is filing-derived: no 삼성전자/삼성전기.** The equivalent live ambiguous
   prefix is **`에스`** (7 prefix hits, `resolve_corp` miss); `계양` is the unique-prefix hit.
   `P7.S9`'s sweep should use those, not the plan's illustrative names.
4. **`.venv/bin/python -m pytest` is 139 now** (138 at this slice's start). The phase's stated
   "59" baseline is stale — it predates P5/P6's web and agent suites.
5. The isolated production build (`P7.S2`'s copy-to-scratch method) still works unchanged, and
   `MIJUAL_API_ORIGIN=http://127.0.0.1:8000` at build time is enough to point it at the dev API.

### Item 3 closed — `P7.S5`: the ring off the text fields, the fields' own hairline in its place

**Two CSS files, ~55 lines, no DOM and no token touched.** `app/shell.css` grows one rule beside the
signed `:focus-visible` ring — text-entry controls get `outline: none` and
`border-color: var(--field-focus-border, var(--ink-2))` on `:focus` — and `Hero.module.css` `.input`
sets the one hook (`--field-focus-border: rgba(163, 196, 180, 1)`), because the hero's dark console
field is the only field in the product not on the shared `--border-strong` hairline.

**Decision D-P7-3 — the a11y floor moved treatment, not existence, and the numbers say it holds.**
Collision reading #1 is implemented literally: the ring stays the floor for every non-text
focusable, and a text field indicates focus by brightening its own hairline. Rendered-pixel contrast
of the state change (2× screenshots, blurred vs focused): hero **4.01:1**, `/stocks` **3.40:1**,
`/auth/login` **3.30:1**; focused hairline against the field interior 10.12 / 7.05 / 6.76. All clear
3:1 both ways. **The plan's illustrative `rgba(163,196,180,.8)` for the hero would have measured
2.63:1** — under the bar — so the hero uses the same R2 console colour at full opacity instead. One
number, same hue, same declaration.

**Three implementation facts a later slice must not undo.**

1. **The rule is `:focus`, not `:focus-visible`.** Browsers match `:focus-visible` on a text input
   for a plain **mouse click** (that is why the operator saw the box on every click), but a
   *programmatic* focus may not match it — `/portfolio` 수정 autofocuses `SharesInput`, measured. One
   `:focus` rule covers click, Tab and `.focus()`; the ring above is the app's only outline, so
   nothing else is affected.
2. **The specificity is (0,1,1) on purpose, and it cannot be lowered.** Every field paints its
   hairline from a CSS-module class at (0,1,0) (`border: 1px solid …`), so a `:where()`-flattened
   (0,0,0) rule would lose the `border-color` **and** tie-and-lose the `outline: none` against the
   (0,1,0) `:focus-visible` ring. `:where()` is used only to flatten the type list. Re-grepped: no
   module sets a focus style today, so nothing is being overridden.
3. **The selector is an allow-list of text-entry types**, not a `:not(checkbox):not(radio)`
   deny-list, so a future `submit`/`file`/`range`/`color` input keeps the ring by default rather than
   silently losing its indicator. Verified by injecting elements with a (0,1,0) class border into a
   live page: `select`, `textarea` and a typeless `input` take the border treatment; `checkbox`,
   `radio`, `submit` and `range` keep `solid 2px rgb(143,178,232)`.

**Measured** (headless Chrome/CDP, fresh profile, `next dev` on **`127.0.0.1`**, 1440×900 and
390×844, mouse click **and** keyboard Tab on every field; repeated on the **Tailscale** origin and
against an **isolated production build** on `:3100` — all four runs agree). Eleven fields across
`/`, `/stocks`, `/stocks/{corp_code}`, `/auth/login`, the AI 질문 widget, `/ask`, the `/ops` door,
`/portfolio?sample=1`, `/portfolio` and `/portfolio/notifications`: focused `outline-style` **none**
everywhere, blurred `rgba(163,196,180,.32|.4|.15)` → focused `rgb(157,179,168)` (`--ink-2`) or
`rgb(163,196,180)` (hero). Before, all eleven wore `solid 2px rgb(143,178,232) @2px` — `--focus-ring`
→ `--r1`, the ① 유상증자 hue.

**The zero-gap rows are fixed at the source.** Input right edge = 조회 left edge = **924** (`/`
@1440) and **656** (`/stocks` @1440), gap **0** before *and* after — the button did not move and no
gap was added, per plan. With `outline: none` the entire focus treatment now lives inside the input's
border box, so there is nothing left that *can* paint under the button. The hero's focused hairline
is three-sided (`border-right: none`), which is the signed geometry.

**Ring keepers re-verified, before and after, 1440 and 390:** wordmark, all three nav links, 샘플 chip,
샘플 종료, the `[의견]` vocky trigger, the 조회 submit, all four board tabs, every 펼치기 (both strips
*and* `P7.S3`'s window control), the AI 질문 launcher, board row links, and the 챙겼습니다 checkbox —
all still `solid 2px rgb(143,178,232) @2px`. **The one difference in the whole 14-stop tab order is
the single `input[type=text]` stop.**

**Notes later slices need:**

1. **`P7.S4`'s listbox was not touched and still measures identically** (`dx=0 dy=0`, width delta 0,
   `border-top: 0`, radius 0). One observation for `P7.S9`/the review, deliberately left alone: with
   the panel open, the focused input's hairline is now brighter than the panel's own
   `--candidate-border` side edges, so the seam is visible at 2×. In the 2× screenshots it reads
   correctly — the field is the active thing, the panel hangs off it — and the plan forbade touching
   `SearchRow.module.css`. If the operator ever wants them matched, the change is one line there,
   not here.
2. **The ask composer is an `<input type="text">`, not a textarea** (`components/ask/Composer.tsx:49`).
   The app renders **no** `<textarea>` anywhere. Any doc or plan wording that says "composer textarea"
   is wrong.
3. **`/ops`'s inner filter fields cannot be reached in this environment** — no ops credential is
   configured, and R7's signed door answers one `401` for an unconfigured credential exactly as it
   does for a wrong one. They share one declaration block with the door field, which *was* measured
   live. Any slice needing `/ops` interiors has to raise the credential with the operator first.
4. **A throwaway account is the only way to reach `AddHolding` and `NotificationsView` fields**
   (`mode === "account"`; `/portfolio/notifications` redirects to `/auth/login` otherwise), and the
   email field there appears only after 변경. Note the flow trap: on `/auth/login` the quiet row's
   **계정 만들기 is the mode switch**, and the form's submit button then carries the same label — a
   probe that clicks the first matching element switches mode and submits nothing. This slice's
   throwaways were deleted through 계정 삭제 and verified gone: `account` holds exactly
   `s19-fidelity@example.com` (id 14), the P5.S19 leftover `P7.S2` recorded.
5. **`--field-focus-border` is the hook for any future field** whose hairline is not
   `--border-strong`/`--border-soft`: set it on the field's own class, not on a wrapper, and keep it
   inside that field's colour family.
6. **Open Question Q2 is untouched by this slice.** The keyboard indicator survives by design; if the
   operator meant *zero* indication, that is theirs to say.

### Item 1 closed — `P7.S6`: the nav entry removed, verified by served-HTML count

**Exactly the edit the DECOMP predicted, nothing else.** `frontend/components/chrome/copy.ts`:
removed `{ label: STOCKS_LABEL_KO, href: ROUTES.stocks }` from `NAV_LINKS` (now two entries:
관제 현황판 · AI 질문) and rewrote the doc comment above it to state the current shape and cite the
P7 override; `Nav.tsx`, `Nav.module.css`, the footer, and no label were touched. `STOCKS_LABEL_KO`
stays exported and in use (`LookupHeader.tsx`, `ask/links.ts`, `ask/copy.ts` and `lookup/copy.ts`
re-exports) and `ROUTES` stays imported in `copy.ts` (its remaining two `NAV_LINKS` entries still
reference `ROUTES.board`/`ROUTES.ask`), so nothing became unused.

**Served-HTML counts on `GET /` confirm it precisely.** `내 종목 조회` occurrences: **6 → 4**; the
two removed are exactly the desktop nav link and the mobile-sheet row (matched against
`Nav-module__…__link`/`…__sheetRow` classes before the edit). The 4 remaining are all off-nav and
untouched: the hero `<h1>`, the hero search `aria-label`, and their two RSC-flight-payload
duplicates. `href="/stocks"` occurrences: **2 → 0**. `GET /stocks` still **200**s with its own
`<h1>내 종목 조회</h1>` intact — the surface stays reachable, only the nav entry is gone. **Gotcha
worth recording for later slices:** a plain `grep -c` on this app's served HTML undercounts,
because Next serves the whole document as one line — `grep -c` counts *matching lines* (always 1
if every hit is on that one line), not occurrences; use `grep -o pattern | wc -l` instead. Because
the same `NAV_LINKS` array feeds both the desktop `<nav>` and the mobile sheet (one `.map` each,
CSS handles the breakpoint), the single served-HTML check above covers both the 1440 nav and the
390 sheet rows — no CDP session was needed for a one-entry removal. `npm run typecheck` and
`python3 scripts/workflow.py validate` both pass. See `P7.S6/result.md` for the full diff and
counts table.

### Item 10 closed — `P7.S7`: two strings trimmed, and the sweep says there are no others

**The DECOMP table was right about the hits and wrong about the size of the job — in the reader's
favour.** A comment-aware sweep of **346 Hangul string literals** (a real tokenizer over
`frontend/app`, `components`, `lib`, so doc comments and docstrings are excluded rather than
grepped around), plus JSX bare text, every `aria-label`/`title`/`placeholder`/`alt` (all of them
read a `copy.ts` constant), the document metadata, and the Korean the **backend** composes for
readers (`src/mijual/agent/copy.py`), found **exactly the two strings the plan had already
decided** and no third instance of the pattern. The product narrates itself in two captions, not
everywhere.

**What changed:** `CLAIM_CAPTION_LOCAL_KO` → 「본인 표시」 (`components/portfolio/copy.ts:195`) and
`components/lookup/copy.ts:101`'s `HOLDING_CAPTION_KO` → 「서버 전송 없음」 — reading #6 applied
literally: the mechanism clause goes, the promise stays **verbatim**, and no Korean was minted.
Three comments elsewhere claimed the old caption is what renders (`HoldingStrip.tsx`,
`lib/holding.ts`, and **`src/mijual/web/routers/stocks.py`**, whose "no holding count is ever
received here" rationale quoted the caption whole); all three now quote what renders and cite the
P7 trim, keeping the round citation.

**Measured, with a control.** In `next dev` on `127.0.0.1` and on the tailnet, and in an isolated
production build served on :3100, `document.body.innerText` / the served HTML of `/`, `/stocks`, a
stock page, `/portfolio?sample=1`, `/auth/login` and `/ask` contain **zero** occurrences of
`localStorage`, `sessionStorage`, `브라우저 세션`, `이 브라우저` — and zero of the bare word
`브라우저`. The control matters more than the zeros: with the two constants temporarily reverted the
same probe read `localStorage` 2 / `이 브라우저` 2 on the sample and `브라우저 세션` 1 on the stock
page, so the zeros are a measurement rather than a probe that cannot see. The old strings survive in
the build **only inside `.js.map` source maps** (the kept round citations); no emitted `.js` carries
them.

**The judgment that actually took the time — and what is now the operator's.** Four reader-visible
strings speak developer vocabulary but are *promises*, so reading #6 keeps them and they go to the
review as questions instead: `API_TIER_KO` 「DART 공시 API 수치 — 원문 스팬 없음, 접수번호가 인용
핸들」 (`ask/copy.ts:118`) and `SPARSE_CLOSING_KO` 「… 위 값은 DART 공시 API 기준입니다」
(`event/copy.ts:134`) — both explain *why a fact has no verbatim quote*, which is the trust story,
not chatter; `GATE_COST_TAIL_KO` 「… 게이트를 통과하지 못해 총액에서 제외했습니다」
(`chrome/copy.ts:156`) — internal machinery vocabulary in the footer, but also the product's one
disclosure of a number it excluded on purpose; and `carryOverKo` 「… 이 세션에 남아 있습니다」
(`portfolio/copy.ts:135`) — `세션` is on the sweep's keyword list, yet it is the only word telling
the reader the value is temporary. None can be trimmed without either destroying the promise or
minting a new sentence, which is a copy decision. **Two useful contrasts for anyone rewriting them
later:** `auth/copy.ts:162` 「이 보유량은 탭을 닫으면 사라집니다」 already says a storage fact as a
*consequence* — it is the shape item 10 wants — and `/ops` (≈30 strings like 「렌더 가능 필드」,
「세션 해시」, 「API shape 확정 대기」) is operator-facing behind its own login and is out of scope by
rule, not by oversight.

**Gotcha for later slices:** `next dev`'s Fast Refresh picks up a `copy.ts` constant change without
a reload, so a revert/measure/restore control costs seconds — but the sample portfolio must be
entered by **clicking the product's own 샘플 포트폴리오로 둘러보기 link** (or `?sample=1`), and both
its 챙겼습니다 captions live on **past ① rows only**, two of them today.

### Item 9 closed — `P7.S8`: five measured layout slips, and the flip proven in both modes

**"Not organized" was not a design objection — it was five implementation slips against the
record, none of them visible in the source and all of them measurable in a browser.** One file
changed (`components/portfolio/Portfolio.module.css`); no markup, no copy, no token, no colour.

| # | what was off (measured, 1440 / 768 / 390) | fix |
|---|---|---|
| D1 | `.holdingHead` and `.holdingRow` are **two grids sharing one track list** (`1.4fr 1fr 1.6fr auto`). The head's 4th cell is an empty `<span/>`, so its `auto` track resolved to **0px** and the rows' to **53.5px**, and the three `fr` tracks split a different leftover in each. Column labels sat **18.7px** (보유량) / **32.1px** (진행 중인 권리) right of their own cells, at 1440 **and** 768 | fourth track becomes fixed `--holding-actions: var(--space-16)` → **0.0px** offset everywhere |
| D1b | side effect: the 53.5px 수정·삭제 pair then sat 10.5px short of the content edge it used to touch | `justify-self: end` on `.holdingRow .actions`, inside the ≥480 rule only |
| D2 | `.rows` had `gap: --space-3` **on top of** each row's `padding: --space-4 0` + `border-top`: the hairline sat **28px** below the previous row's ink and **16px** above its own (24/12 at 390) — belonging to neither row, while `.holdings` on the same page is symmetric | drop the gap; the hairline **is** the separator (R2 §Board: "9px v-pad, dashed separators") → **16/16**, **12/12** at 390 |
| D3 | `.lapsed { align-items: center }` over children **23.3 / 44 / 66.6px** tall: money line, 상세 link and 챙겼습니다 check started at three different y — a **21.7px** spread | `align-items: flex-start` + `min-height: 44px; align-content: center` on `.lapsedLine` → one origin, three texts on one 44px band |
| D4 | the `// ` eyebrow rendered at **12px / no tracking** here while `lookup`, `event` and `landing/Anchor` all render **11px + 0.08em** — R2's literal is "mono 11 `--ink-3` eyebrow", R3's is "eyebrow mono, tracked" | `--text-xs` + `letter-spacing: 0.08em` |

Document height fell 1572→1533 (1440), 1613→1574 (768), 2407→2367 (390). Overflow, clipped-text,
radius and non-token-spacing audits over the whole surface: clean at all three widths, before and
after (the only non-token values are `pastChip`'s signed 2px chip padding and the UA checkbox
margin).

**The 챙겼습니다 flip was already correct and is now proven.** All four R5-8 consequences fire —
label 놓친 돈 → **챙긴 돈**, `679,575원` unchanged, 「추정」 kept, and `--alert` `rgb(224,87,63)` →
`--live` `rgb(95,208,165)` on **both** the label and the value — with **zero layout shift**
(`.lapsed` y/h and the document height identical before and after the click, in both modes).
샘플/익명 persists in `localStorage` (`claims:["20260730000366"]`); the **account path was
exercised end to end** with a throwaway account created and deleted through the product:
`PUT /api/portfolio/claims/{rcept_no}` → **200** → `GET /api/portfolio` → 200 → the flip survives a
full reload in the server-rendered HTML, caption 「본인 표시 · 계정에 저장」. DB clean afterwards
(`lapse_claim` 0, `holding` 0, the only `account` row is P5.S19's `s19-fidelity@example.com`).
Keyboard: the checkbox is the **16th** Tab stop and wears S5's preserved `2px solid rgb(143,178,232)`
@2px ring with `:focus-visible` true; Space flips it. Everything above measured in `next dev` on
`127.0.0.1` **and** the tailnet `100.77.164.42`, and reproduced number-for-number in an isolated
production build on `:3100`.

**Gotchas worth carrying:**

1. **Two CSS-module grids that share a track list do not necessarily resolve the same track
   list.** An `auto` (or `max-content`) track is sized by *that element's* content, so a header row
   with an empty cell and a data row with a filled one produce different `fr` leftovers — every
   column silently drifts. If a header must align with its rows, every non-`fr` track has to be
   content-independent. This is D1, and it is invisible in the source: both elements name the same
   `grid-template-columns`.
2. **A `gap` on a list whose rows already carry a `border` + padding double-counts the rhythm** and
   detaches the rule from both neighbours. `.holdings` (gapless, per-row border) and `.rows`
   (gapped, per-row border) sat on the same page doing it two different ways.
3. **`.focus()` from a probe does not match `:focus-visible`** — only a real Tab does. A focus
   measurement taken programmatically will report "no ring" on an element that has one.
4. **`P5.S19` catalogue #6 confirmed by measurement, not fixed:** `GET /portfolio/sample` serves
   `holdings 4 · upcoming 2 · past 3` = **five** D-day rows, because **대동기어 carries two events**
   (upcoming ② D-62 *and* past ① 소멸 D+46, 446,720원) while R5's composition table pins one filing
   per holding and the entry subline says 「실제 공시 **4건**」. No row was hidden.

**Five record-silent items went to the operator instead of being invented** — Q8 below. The
biggest of them (Q-A) is the one remaining "not organized" symptom: at 1440 the five D-day rows'
right-hand blocks begin at x = 1035.5 / 1090.3 / 945.6 / 945.7 / 953.2 — a **144.7px ragged edge**
with 584.6–761.3px of empty middle — because `.rowHead` is `justify-content: space-between` and R5
states the row's parts but no geometry. R2's board pins a fixed grid for exactly this reason; the
call is the operator's.


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

- `frontend` — **the `P5.S19` browser-check note (`docs/current/frontend.md:313`) is incomplete
  and, as written, misleading.** It says to check over `localhost` rather than `127.0.0.1`; the
  real rule is that `next dev` bound to `0.0.0.0` serves its dev resources **only** to `localhost`
  unless `allowedDevOrigins` names the host, and that an un-hydrated page looks exactly like six
  separate product bugs. (Recorded by `P7.DECOMP`.) **`P7.S1` fixed the cause, so the note now
  inverts:** `frontend/next.config.ts` carries an `allowedDevOrigins` seam (`127.0.0.1`, `[::1]`,
  `**.ts.net`, plus `MIJUAL_DEV_ORIGINS` — comma-separated hosts, filled by `make web-up` from
  `tailscale ip -4`), and the rule for every future browser check is **verify on `127.0.0.1` and
  the Tailscale origin — the operator's own — not on `localhost`**, because `localhost` is the one
  origin that was never able to show this class of defect. Worth recording with it: Next's matcher
  (`isCsrfOriginAllowed`) is host-only and segment-wildcarded, so an IPv4 literal can be named only
  exactly or by whole-octet wildcards (`100.*.*.*` would open all of 100.0.0.0/8, not Tailscale's
  100.64.0.0/10) — hence the env seam; and the dev server **auto-restarts on a `next.config.ts`
  edit** but not on an env change.
- `operations` — a new operator-facing environment variable, `MIJUAL_DEV_ORIGINS` (frontend,
  dev-only): comma-separated extra hosts appended to `allowedDevOrigins`; `make web-up` fills it
  from `tailscale ip -4`, and anyone starting `next dev` by hand must set it or the Tailscale
  origin silently stops hydrating. It belongs in the Environment Variables table beside
  `MIJUAL_API_ORIGIN`. (The operations doc today describes no dev stack / `Makefile` at all —
  `P7.REVIEW` may decide whether that gap is worth closing.)
- `frontend` — a dev-time trap for the Gotchas list, beside the `localhost`/`127.0.0.1` and
  `EADDRINUSE` entries: **the App Router tree is wrapped in `React.StrictMode` under `next dev`**
  (`next.config.ts` sets no `reactStrictMode`, and Next's `define-env.js` turns that into
  `__NEXT_STRICT_MODE_APP = true`), so every effect runs twice. A **module-scope** guard claimed
  inside an effect plus a per-effect-run cleanup flag therefore does its work once and discards the
  result **forever** — the shape that made the chrome's account slot render nothing at all in dev
  while `next start` was perfect (`P7.S2`, item 5). Recorded with it: a module store has no unmount
  hazard for a cleanup flag to protect against, and `lib/session.ts` shares the in-flight probe, so
  the double invocation costs one request. (Recorded by `P7.S2`; the doc does not describe
  `useAccount` itself, so this is the trap, not an API change.)
- `frontend` — **the landing board no longer renders every ranked row.** It shows **30 at a time**
  and discloses the next 30 through the signed 펼치기 hairline button (`EXPAND_KO`, the strips' own
  `.expand`) with a mono remaining-count in the strips' `N건` idiom; **zero new Korean copy**. It is
  a **display window, never a filter**: the served corpus, the ranked order and the whole-board
  `counts` are unchanged (전체 still reads 488), and a tab switch resets the window to the first 30.
  This is a **P7 operator override** of an unsigned gap — R2 specifies the sort, the row anatomy and
  the two strips but **no list length and no pagination control**, so `P5.S3` note 11's "the design
  paginates nothing" no longer describes the rendered page and should be recorded as superseded
  *for the rendering*, not for the API (the board is still one request). Measured effect: the served
  HTML for `/` drops **701.9 KB → 369.2 KB** and the document from 17,730 px to 3,047 px at 1440.
  The initial count (**30**, +30 per click) is `P7.S3`'s decision D-P7-1 and awaits operator
  confirmation (Q3). (Recorded by `P7.S3`.)
- `experience` — the 관제 현황판 §Board bullet describes the board as urgency-interleaved with tabs
  and a D-day-ascending sort; it should now also say the reader sees **30 rows at a time** and
  presses 펼치기 for the next 30 — reading the whole list is a deliberate act, not the default. The
  two pinned strips are unchanged. `product.md` was checked and needs nothing: it states the corpus
  (488 exposable events) and the board's states, never a claim that every row is rendered.
  (Recorded by `P7.S3`; the review may fold this into the `frontend` line if it prefers one.)

- `api` — **a new read-only route: `GET /stocks/suggest?q=<종목명|종목코드>`** →
  `{"query", "candidates": [{corp_code, corp_name, stock_code}, …]}`, **at most 8**, `200` with an
  empty list when nothing matches (never 404), `q` its **only** parameter (so the "no holding count
  is ever received here" promise still holds). Matching is `reads.suggest_corps`: all-digit →
  `stock_code` prefix + the zero-padded exact; otherwise normalized-name **prefix then substring**,
  tiers unioned, alphabetical inside each group. With it, the §내 종목 조회 rule sentence changes:
  today's doc says a miss "names no reason, candidate or near-miss" — **the miss payload still names
  none, and the resolver still never guesses on submit; candidates now exist on their own route,
  before the submit, as the reader's own choice, and a chosen one travels as the exact handle
  `/stocks/{corp_code}`**. Worth recording beside it: the route must stay **declared before**
  `GET /stocks/{corp_code}`, or the handle route swallows `suggest` as a `corp_code`. (Recorded by
  `P7.S4`.)
- `frontend` — **the two search rows are one component.** `components/lookup/SearchRow.tsx` is
  rendered by both the landing hero and R4's `LookupHeader`, each passing its own form/input/button
  classes, so the signed geometry stays each surface's own while the behaviour is shared: a WAI-ARIA
  combobox (`role="combobox"` + `aria-expanded`/`aria-controls`/`aria-activedescendant`, options
  `role="option"`), ~150 ms debounce, an `AbortController` per keystroke, **no request on mount or
  for an empty box**, ↑/↓ to move, **Enter on a highlighted option → `router.push(stockPath(corp_code))`**,
  Enter with nothing highlighted → the unchanged native GET submit, Esc/blur to close, nothing
  pre-highlighted. The panel is an **unsigned element built in the signed idiom** (radius 0,
  hairline, the surrounding console field's own colours composited over `--paper` so a floating
  panel is opaque, fade-only motion, 44px options at 390) and it mints **zero Korean copy**. Two
  traps to record with it: the hero's ring clip now lives on `.orbits` rather than `.hero`
  (identical rectangle — a panel hanging off the input would otherwise be cut at the hero's bottom
  edge, measured), and a **CDP Enter without `text: "\r"` fires no keypress**, so a browser probe
  can report a working GET form as broken. (Recorded by `P7.S4`.)
- `experience` — the promise bullet "**A search miss names no reason, candidate or near-miss**" is
  now half of the truth and should be split: the **miss** still names no reason and no near-miss,
  and the resolver still never picks between two companies — but while the reader is **typing**,
  내 종목 조회 offers up to eight candidates, each with its 종목코드, and a chosen one opens by the
  exact handle. The defect class the rule guards against is *the system* opening the wrong
  company's 놓친 돈; a reader choosing from a list is the opposite of that. (Recorded by `P7.S4`;
  `product.md` was checked and needs nothing — it states no search-resolution promise.)

- `frontend` — **focus indication is no longer one treatment for everything.** The a11y floor
  "Focus ring: 2px `--focus-ring`" (v0002/v0004) still governs every button, link, tab, chip,
  checkbox, radio and the R2 §vocky triggers — unchanged, same token, same 2px, same 2px offset —
  but **a text-entry control (`input` of a text-entry type, `textarea`, `select`) now indicates
  focus with `outline: none` plus an in-idiom `border-color` change**, `var(--field-focus-border,
  var(--ink-2))`, set in `app/shell.css`; `Hero.module.css` `.input` is the only module that sets
  the hook (`rgba(163,196,180,1)`, R2 §Cosmos's own console colour at full strength). Why it had to
  change: `--focus-ring` aliases `--r1`, the ① 유상증자 rights hue, browsers match `:focus-visible`
  on a text input for a plain **mouse click**, and on both 조회 rows the input's right edge touches
  its button (**gap 0**, measured), so a 2px ring at `outline-offset: 2px` painted 4px *under* the
  button — the operator's item 3. Record with it: the rule is `:focus` (a programmatic focus may not
  match `:focus-visible`), it sits at specificity **(0,1,1)** because every field's hairline comes
  from a (0,1,0) CSS-module class and a `:where()`-flattened rule would lose, and it names the
  text-entry types rather than excluding checkbox/radio so a future input type keeps the ring by
  default. Measured state-change contrast 3.30–4.01:1 and 6.8–10.1:1 against the field interior, in
  `next dev` on `127.0.0.1` and the tailnet, at 1440 and 390, and in an isolated production build.
  This is a **P7 operator override** of the record's single-treatment reading, not a removal of the
  floor — Open Question **Q2** (does the operator want *zero* indication?) is still open. Two facts
  worth recording beside it: the app renders **no `<textarea>`** — the ask composer is an
  `<input type="text">` — and `P7.S4`'s candidate panel keeps its own `--candidate-border`, so with
  the listbox open the focused input's hairline is brighter than the panel's side edges by design.
  (Recorded by `P7.S5`.)

- `frontend` — **the nav is now two slots, not three: 관제 현황판 · AI 질문.** `NAV_LINKS`
  (`components/chrome/copy.ts`) no longer carries a 내 종목 조회 entry / `/stocks` — an explicit
  **P7 operator override** of R2's signed three-slot nav (item 1), scoped to the slot alone: no
  re-centring, no re-spacing, no new slot, no other label touched. The 내 종목 조회 surface stays
  reachable — the landing hero's own search *is* it, plus R3's detail link-out and the AI 질문
  link row — and the label constant (`STOCKS_LABEL_KO`) stays exported and in use by
  `LookupHeader.tsx` / `ask/links.ts` / `ask/copy.ts` / `lookup/copy.ts`, so no import broke.
  Any current-doc language describing the nav as three links (e.g. `frontend`'s v0002/R2
  supersession-table framing) should be updated to two. **For the review, not this slice:** two
  P5 catalogue items are now *more* visible with the distraction gone — the footer's locked
  positioning line still literally says **내 종목 연결** (`P5.S19` catalogue #4) and the hero
  `<h1>` says **내 종목 조회** where R2's own literal was 내 종목 연결 (catalogue #12); neither is
  P7.S6's to rewrite. (Recorded by `P7.S6`; see `P7.S6/result.md` for the diff and the
  before/after served-HTML counts — 6→4 for `내 종목 조회`, 2→0 for `href="/stocks"` on `/`.)

- `frontend` — **two reader captions no longer narrate storage** (operator item 10). The 조회
  보유량 caption is now 「서버 전송 없음」 (`components/lookup/copy.ts`) and the 샘플/익명 챙겼습니다
  caption is now 「본인 표시」 (`components/portfolio/copy.ts`); the account caption 「본인 표시 ·
  계정에 저장」 and 「계정에 저장 · 마감 알림의 기준」 are unchanged, because where a mark or a count
  lives *for the reader* is their own fact. The 조회 one is a **P7 operator override of a signed
  literal**: R4 §3 writes 「브라우저 세션에만 저장 · 서버 전송 없음」 and P7 keeps only the promise
  half — **the promise itself is verbatim and no Korean was minted**. Nothing else moved: the
  storage is still sessionStorage/localStorage exactly as `security` describes it, and the API still
  has no `n` parameter, so every sentence in `security`/`experience` about client persistence stays
  true — what changed is only that the surface no longer *says* it. Worth recording with it: after
  the sweep **no string a reader can see contains `localStorage`, `sessionStorage`, `브라우저 세션`,
  `이 브라우저`, or the bare word `브라우저`** — verified in `next dev` on `127.0.0.1` and the
  tailnet and in an isolated production build, with a revert/re-measure control proving the probe
  sees the strings when they are there. (Recorded by `P7.S7`; the full inventory and the four
  strings left for the operator are in `P7.S7/result.md`.)
- `experience` — the 내 종목 조회 bullet "**Memory is session-only:** sessionStorage with a restore
  chip" still describes the implementation correctly, but the surface's *stated* promise is now
  narrower: the page tells the reader only 「서버 전송 없음」 and no longer tells them where the
  number is kept. If the review wants the doc to describe what the reader is told (it currently
  reads as if the session rule were on-screen copy), this is the sentence to re-word; the R4 literal
  itself belongs to the read-only design record and is untouched. (Recorded by `P7.S7`;
  `product.md` and `security.md` were checked and need nothing — neither quotes either caption, and
  no `docs/current/*.md` contains 「서버 전송 없음」, 「본인 표시」 or either before-string.)

- `frontend` — **the 내 포트폴리오 surface's layout primitives, corrected to the ones the rest of the
  product already uses** (operator item 9, `P7.S8`). Three durable rules and one trap:
  **(1)** the `// ` section eyebrow is **`--text-xs` (11px) + `letter-spacing: 0.08em`** — R2's own
  literal "mono 11 `--ink-3` eyebrow", R3's "tracked", and what `lookup`/`event`/`landing/Anchor`
  already render; the portfolio was the one surface rendering it at 12px untracked.
  **(2)** a hairline-separated row list carries **no `gap`** — the `border` *is* the separator, the
  way `.holdings` and R2's board rows ("9px v-pad, dashed `--border-soft` separators") do it; a gap
  on top of the rows' own padding puts the rule 28px from one neighbour and 16px from the other.
  **(3)** where a row's money statement sits beside 44px affordances, all of them align to **one
  44px band** (`align-items: flex-start` + `min-height: 44px` on the statement), not to each
  other's centres — centring boxes of 23.3/44/66.6px gave three different origins.
  **(4)** the trap, for the Gotchas list beside the `localhost`/`127.0.0.1` and StrictMode entries:
  **two CSS-module grids that name the same `grid-template-columns` can resolve different columns.**
  An `auto`/`max-content` track is sized by *its own* element's content, so a header row with an
  empty action cell and a data row with a filled one produce different `fr` leftovers — measured
  here as 18.7px / 32.1px of silent column drift, invisible in the source. A header that must align
  with its rows needs every non-`fr` track content-independent.
  Verified at 1440 / 768 / 390 in `next dev` on `127.0.0.1` and the tailnet, and reproduced
  number-for-number in an isolated production build. (Recorded by `P7.S8`; the full deviation table
  is in `P7.S8/result.md`.)
- `experience` — the 챙긴 돈 bullet ("flipping the label 놓친 → 챙긴 and the color alert → live on
  the same 「추정」 amount") is now **measured true on the running product in both modes**, and two
  facts are worth stating with it: the hue flips on **both** the label and the value, and the
  change is **shift-free** (the row's box and the document height are identical before and after).
  The account path is `PUT /portfolio/claims/{rcept_no}` followed by a re-read of `GET /portfolio`,
  so a claimed row survives a reload server-side; the 샘플/익명 path keeps the mark in
  `localStorage` under `mijual.portfolio.sample`. Nothing in the doc is *wrong* — this is the
  bullet to enrich if the review wants the promise stated as verified behaviour rather than as a
  design intent. (Recorded by `P7.S8`; `product.md` was checked and needs nothing — it states no
  portfolio layout or claim-persistence rule.)

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
- **Q3 — how many firms is "some amount"?** The board serves 386 ranked rows and the number is in
  no record. **`P7.S3` chose 30, with each 펼치기 click adding 30** (decision D-P7-1: 30 is the
  horizon the hero's own stat line names, and chunking keeps the page scannable, which is the ask).
  It is live and measured; **the operator has still not confirmed the number**, so the review must
  put it to them. Changing it is a one-constant edit (`WINDOW_STEP` in `Board.tsx`).
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
- **Q7 — four reader-visible strings speak developer vocabulary, but each one is a promise
  (`P7.S7`, item 10).** The sweep kept them under reading #6 and left them to the operator, because
  none can be trimmed without either destroying the promise or minting a new Korean sentence:
  ① `API_TIER_KO` 「DART 공시 API 수치 — 원문 스팬 없음, 접수번호가 인용 핸들」 (`ask/copy.ts:118`)
  and ② `SPARSE_CLOSING_KO` 「… 위 값은 DART 공시 API 기준입니다」 (`event/copy.ts:134`), which both
  explain **why a fact carries no verbatim quote**; ③ `GATE_COST_TAIL_KO` 「… 게이트를 통과하지 못해
  총액에서 제외했습니다」 (`chrome/copy.ts:156`), machinery vocabulary in the footer that is also the
  product's one disclosure of a deliberately excluded number; ④ `carryOverKo` 「… 이 세션에 남아
  있습니다」 (`portfolio/copy.ts:135`), where 세션 is also the only word conveying impermanence. A
  fifth, smaller one: with the sample caption now 「본인 표시」, should the account caption drop to
  「본인 표시」 too, or keep 「· 계정에 저장」 (`P7.S7` kept it, per plan)? Re-saying any of ①–④ in
  reader language is a copy decision, not an implementation one.
- **Q8 — five record-silent portfolio items `P7.S8` refused to invent** (item 9). **(A)** the
  D-day rows' right-hand block has a **144.7px ragged left edge** and 584.6–761.3px of empty middle
  at 1440 (232.6–409.3px at 768) because `.rowHead` is `justify-content: space-between`; R5 names
  the row's parts and no geometry, while **R2's board pins a fixed grid (`86px 1fr 300px 230px
  96px`)** for exactly this reason — adopting a board-style column grid here is probably what
  "organized" means at desktop width, but it is a geometry decision no round made for this surface.
  **(B)** 지나간 마감 states no 「기준 YYYY-MM-DD (KST)」 line; `P5.S8` read R5's sentence as
  page-level and states it once on the counting-down section, the S8 plan read it as per-section —
  the string already exists either way, so no Korean is at stake. **(C)** 한화솔루션 and 세기상사
  render an **empty 진행 중인 권리 cell** (both hold only past rights, and R5 signs no empty-cell
  sentence) — a visible hole in two of four rows at ≥480. **(D)** a **챙긴 돈 row still links
  「놓친 돈 상세 →」** — R5-8's checked-state delta is exactly four items and the link is not one of
  them, and the link's target section is literally named 「2026년 놓친 돈」, so changing it mints
  Korean. **(E)** the **본인 표시 caption renders whether or not the box is checked**; R5-8 phrases
  all four consequences as following 체크, so it can be read as "the caption appears on check" —
  `P7.S8` left it alone because making it conditional adds a **22.6px layout shift** on click,
  which its plan forbids. None of these was changed; all five need the operator, and (A) is the
  one that still answers the original "not organized".
