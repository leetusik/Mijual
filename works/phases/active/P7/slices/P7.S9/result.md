# Result — P7.S9: fidelity sweep, all 11 items, dev + production build, on the operator's own origins

**Outcome: every one of the 11 operator items verified on all three origins in both runtimes; no code
was changed, because nothing needed changing.** Every probe FAIL this sweep produced — nine of them —
was re-measured with a scoped selector and turned out to be the probe, a known/deliberate state, or
correct behaviour. The phase's own record now has an independent second measurement of the numbers
`P7.S1`–`S8` reported, taken by a harness written from scratch for this slice.

---

## 1. What actually ran

| | |
|---|---|
| Runtime A — **the operator's dev stack** | `make stack-up` untouched and left up: `next dev -H 0.0.0.0 -p 3000`, React StrictMode on, api pid 25177, postgres up 3 days |
| Runtime B — **an isolated production build** | `rsync` copy of `frontend/` (sources + real `node_modules`, no `.next`) into session scratch, `MIJUAL_API_ORIGIN=http://127.0.0.1:8000 npm run build` (16 routes, exit 0) → `next start -H 0.0.0.0 -p 3100`. The dev server's `.next` was never touched; `:3100` is freed at the end |
| Origins | **`127.0.0.1`** (the operator's own), **`100.77.164.42`** (Tailscale, what `stack-status` prints), **`localhost`** (the control — the one origin that could never show P7's defect class) |
| Widths | **1440 · 768 · 481 · 480 · 390** |
| Driver | headless Chrome over raw CDP from Node 24, **fresh browser profile per run**, storage cleared between controls |
| Volume | **~553 scripted Stage-1 checks** across five origin × runtime combinations, **348 control clicks** in the Stage-2 functional sweep, 27 Stage-3 smoke checks, **54 screenshots**, **2** live agent turns |
| Screenshots + raw logs | `/private/tmp/claude-502/-Users-sugang-projects-personal-Mijual/4321eab8-d896-4fa7-82c2-506bc1cadf44/scratchpad/p7s9/` (`shots/`, `out-*.txt`) — session scratch, nothing written into the repo |

Live corpus at sweep time: `GET /board` = **386** ranked rows, `counts` **488 / 50 / 422 / 16**,
`open_now` **60**, `tbd` **4**, `freshness.as_of` 2026-08-22T04:14+09:00 (**stale**, 30 h, reference
2026-08-23). Identical to what `P7.S1`/`S3` measured — the corpus did not move under the phase.

**Two harness bugs found and fixed inside this slice, worth carrying** (both would have reported a
working product as broken, which is exactly the `frontend` v0004 rule this plan invokes):

1. **A CDP `Input.dispatchKeyEvent` `keyDown` that carries `text` already generates the keypress.**
   Dispatching a separate `type: "char"` event as well fires a **second** keypress that
   `preventDefault()` on the keydown cannot suppress — so ↓+Enter on a typeahead candidate submitted
   the native GET form instead of choosing, and the typeahead looked broken. `P7.S4`'s note ("an
   Enter without `text: \"\\r\"` fires no keypress") is right but only half the recipe: send the text
   **on the keyDown and nowhere else**.
2. **A `clickAt` at a coordinate below the viewport hits nothing, silently.** The 챙겼습니다 row sits
   at y≈925 in a 900px viewport and the board's window control walks down the page as rows appear;
   both read as dead controls until the probe scrolls first. Every click in this sweep goes through a
   `scrollIntoView` first.

---

## 2. Stage 1 — the 11 items, three origins × two runtimes

`dev127` = `next dev` on `http://127.0.0.1:3000` · `devTS` = `next dev` on `http://100.77.164.42:3000`
· `devLH` = `next dev` on `http://localhost:3000` (control) · `prod127` / `prodTS` = the production
build on `:3100`.

| # | item | check (measured) | dev127 | devTS | devLH | prod127 | prodTS |
|---|---|---|---|---|---|---|---|
| **1** | nav | desktop `nav[class*=links]` = **2 slots**, 관제 현황판→`/` · AI 질문→`/ask`; `header a[href="/stocks"]` = **0** | ✓ | ✓ | ✓ | ✓ | ✓ |
| 1 | nav | 390 sheet opened: **관제 현황판 · AI 질문 · 로그인 · 의견 보내기** (2 destinations + the account row) | ✓ | ✓ | ✓ | ✓ | ✓ |
| 1 | nav | 조회 still reachable: hero `form[role=search][action="/stocks"]` present; R3 detail links out to `/stocks/00102618`; the agent's link row carries 내 종목 조회 | ✓ | ✓ | ✓ | ✓ | ✓ |
| **2** | typeahead | suggest requests **on mount = 0** on `/` and `/stocks` | ✓ | ✓ | ✓ | ✓ | ✓ |
| 2 | typeahead | one debounced burst `계양` → **1** request → **1** candidate `계양전기 / 012200` | ✓ | ✓ | ✓ | ✓ | ✓ |
| 2 | typeahead | every candidate carries its 종목코드; panel `dx=0 dw=0 dy=0`, `radius 0px`, `border-top: 0` | ✓ | ✓ | ✓ | ✓ | ✓ |
| 2 | typeahead | ↓ then Enter → **`/stocks/01258020`** (the handle, not a re-resolve) | ✓ | ✓ | ✓ | ✓ | ✓ |
| 2 | typeahead | Esc closes (`ul[role=listbox]` count 1→0) | ✓ | ✓ | ✓ | ✓ | ✓ |
| 2 | typeahead | 390 option height **44px**; a real mouse click on one → `/stocks/00102618` | ✓ | ✓ | ✓ | ✓ | ✓ |
| 2 | typeahead | unchosen Enter unchanged: `계양` → `/stocks/00102618`; `에스` (**8** candidates) → 「‘에스’와 일치하는 종목이 없습니다 — 종목명 또는 종목코드로 다시 검색해 주세요.」 | ✓ | ✓ | ✓ | ✓ | ✓ |
| 2 | typeahead | served HTML: plain `<form action="/stocks" method="get">`, **no** `role="listbox"` (JS-off path intact) | ✓ | ✓ | ✓ | ✓ | ✓ |
| **3** | focus | 12 text fields over `/`, `/stocks`, a stock page, `/auth/login`, the ask composer, and `/portfolio` 수정: **`outline-style: none`** on every one, by click **and** by Tab | ✓ | ✓ | ✓ | ✓ | ✓ |
| 3 | focus | border colour changes on focus: hero `rgba(163,196,180,.4)`→**`rgb(163,196,180)`**; every other field `rgba(163,196,180,.32\|.15)`→**`rgb(157,179,168)`** (`--ink-2`) | ✓ | ✓ | ✓ | ✓ | ✓ |
| 3 | focus | zero-gap rows: input right edge = 조회 left edge, **924.1** on `/` and **656** on `/stocks`/stock page — **gap 0**, and nothing can paint under the button now that the treatment is inside the border box | ✓ | ✓ | ✓ | ✓ | ✓ |
| 3 | focus | ring keepers by **real Tab**: links, nav, chips, 조회, all four board tabs, **all three 펼치기** (stops #73/74/75) and the **챙겼습니다 checkbox** (stops #16/18) → `solid 2px rgb(143,178,232) @2px`, `:focus-visible` true | ✓ | ✓ | ✓ | ✓ | ✓ |
| 3 | focus | `/portfolio` 수정 autofocus (the programmatic case): `outline none`, border `rgb(157,179,168)`, `:focus-visible` **true**, value `500` | ✓ | ✓ | ✓ | ✓ | ✓ |
| **4** | board | **30** ranked rows initially; control reads **`356건 펼치기`** | ✓ | ✓ | ✓ | ✓ | ✓ |
| 4 | board | **12** clicks → **386** rows, then the control **disappears** (`p[class*=more]` count 0) | ✓ | ✓ | ✓ | ✓ | ✓ |
| 4 | board | requests during the whole expansion: **0** in dev — **366 RSC prefetches in prod** (see §5, dev-vs-prod) | ✓ | ✓ | ✓ | ⚠ | ⚠ |
| 4 | board | tab switch resets the window (유증 14 rows → back to 전체 **30**); whole-board counts **488/50/422/16 unchanged** after paging | ✓ | ✓ | ✓ | ✓ | ✓ |
| 4 | board | both strips: **30 → 90 (+60) → 94 (+4) → 30**, `aria-expanded` false→true→false on both | ✓ | ✓ | ✓ | ✓ | ✓ |
| **5** | login | sample cleared → `a[href="/auth/login"]` = **2** (desktop slot + sheet row) on `/`, `/stocks`, `/ask`; 390 sheet shows 로그인 | ✓ | ✓ | ✓ | ✓ | ✓ |
| 5 | login | **exactly one** `GET /api/auth/me` per page load, status 200 | ✓ | ✓ | ✓ | ✓ | ✓ |
| 5 | login | full round trip (one run, dev 127.0.0.1) — see §3 | ✓ | — | — | — | — |
| **6** | countdown | digits at t0 / t+30 / t+60 all different, no reload, window marker kept: dev `12일 14:16:59 → 14:16:29 → 14:15:59`, prod `14:13:27 → 14:12:57 → 14:12:27`, tailnet `13:44:00 → 13:43:30 → 13:43:00` — 30 s per interval, **60 s of live ticking** | ✓ | ✓ | ✓ | ✓ | ✓ |
| **7** | no stomping | typed `계양`, waited **130 s**: value **kept**, `window` marker alive, **0** top-frame navigations, **0** `/_next/*` 403s | ✓ | ✓ | ✓ | ✓ | ✓ |
| 7 | no stomping | HMR websocket handshake **101** in dev on every origin; **no socket at all** in prod (correct) | ✓ | ✓ | ✓ | n/a | n/a |
| **8** | AI 질문 | one live turn each in dev (127.0.0.1) and prod — see §4 | ✓ | — | — | ✓ | — |
| **9** | portfolio | document height **1533 / 1574 / 2367** at 1440 / 768 / 390 — S8's "after" numbers reproduced exactly | ✓ | ✓ | ✓ | ✓ | ✓ |
| 9 | portfolio | D1: head↔row labelled columns at x **184/536/792** (1440) and **24/252.8/420.8** (768) → offset **0.0px**; at 390 the header is `display:none` (R5 §Mobile single column) | ✓ | ✓ | ✓ | ✓ | ✓ |
| 9 | portfolio | D1b: 수정·삭제 pair right edge **1256** / **744** / **374** = the content column's right edge | ✓ | ✓ | ✓ | ✓ | ✓ |
| 9 | portfolio | D2: `.rows` `row-gap: normal`, each row `border-top 1px` + padding **16/16** (1440, 768) and **12/12** (390) | ✓ | ✓ | ✓ | ✓ | ✓ |
| 9 | portfolio | D3: the three `.lapsed` children share one origin — y **924.8** (1440) / **947.2** (768); at 390 the check wraps to its own line (1461.9 / 1517.9), which is §Mobile | ✓ | ✓ | ✓ | ✓ | ✓ |
| 9 | portfolio | D4: `// ` eyebrow **11px + 0.88px (0.08em)** tracking at all three widths | ✓ | ✓ | ✓ | ✓ | ✓ |
| 9 | portfolio | 챙겼습니다 flip: 놓친 돈 `rgb(224,87,63)` → **챙긴 돈 `rgb(95,208,165)`**, **679,575원 unchanged**, 「추정」 kept, caption 「본인 표시」 | ✓ | ✓ | ✓ | ✓ | ✓ |
| 9 | portfolio | flip is **shift-free** (document height 1533→1533, `.lapsed` document-relative y and height identical) and **persists across a full reload** (`localStorage` `claims`) | ✓ | ✓ | ✓ | ✓ | ✓ |
| **10** | copy | `document.body.innerText` on `/`, `/stocks`, `/stocks/00102618`, an event detail, `/portfolio?sample=1`, `/auth/login`, `/ask`: **0** occurrences of `localStorage`, `sessionStorage`, `브라우저 세션`, `이 브라우저`, and **0** of the bare word `브라우저` | ✓ | ✓ | ✓ | ✓ | ✓ |
| 10 | copy | captions read exactly 「**본인 표시**」 (portfolio, both instances) and 「**서버 전송 없음**」 (조회 HoldingStrip) | ✓ | ✓ | ✓ | ✓ | ✓ |
| **11** | widget | launcher in DOM at **1440 ✓ / 481 ✓ / 480 ✗ / 390 ✗**; `position: fixed` nodes 2 above the boundary, 1 below — the signed ≤480 rule, on every origin | ✓ | ✓ | ✓ | ✓ | ✓ |
| 11 | widget | opened: 440×620 at 1440/768, **433×620 at 481** (x=24) — fits the viewport in both axes, no document overflow | ✓ | ✓ | ✓ | ✓ | ✓ |

Run totals, verbatim from the harness: **dev127 113 pass / 0 fail · devTS 114 / 0 · devLH 106 / 0 ·
prod127 113 / 0 · prodTS 105 / 1** — the single prod "fail" is the board-expansion request count,
which is Next's own production `<Link>` prefetching and is written up in §5 rather than counted as a
defect.

---

## 3. Item 5 — the full account round trip (one run, `next dev` on 127.0.0.1)

Throwaway `p7s9-probe@example.com`, created and destroyed through the product's own screens.

| step | measured |
|---|---|
| landing, sample cleared | slot renders `로그인 [의견]`, 1 `GET /api/auth/me` |
| 로그인 clicked in the chrome | → `/auth/login`, **0 document loads** (client-side) |
| the quiet row's **계정 만들기** | mode switch; the form's submit label becomes 계정 만들기 (the trap `P7.S5` note 4 recorded — the two controls share a label) |
| 계정 만들기 submitted | `POST /api/auth/signup` **201** → push to `/portfolio`, slot becomes `p7s9…com` **with no reload** |
| client-side nav to `/` | slot unchanged |
| account menu | rows: `p7s9…com · 내 포트폴리오 · 알림 설정 · 로그아웃` |
| 로그아웃 | `POST /api/auth/logout` **200** → `/auth/login`, slot back to 로그인 |
| 로그인 again | `POST /api/auth/login` **200** → `/portfolio`, slot `p7s9…com` |
| 알림 설정 → 계정 삭제 (arms, then confirms) | `DELETE /api/auth/account` **200** → lands `/`, slot 로그인 |
| the same credentials again | `POST /api/auth/login` **401** + 「이메일 또는 비밀번호가 일치하지 않습니다.」 |

**10 `GET /api/auth/me` across 11 path visits, all 200.** Console exceptions **0**. The only 4xx on
the whole run other than the deliberate 401 is `/favicon.ico` **404** (pre-existing, `P7.S2` note 6).
**DB verified clean afterwards**: `account` holds exactly one row, `s19-fidelity@example.com` (id 14,
P5.S19's residue — catalogued below, deliberately not deleted); `holding` 0, `lapse_claim` 0.

---

## 4. Item 8 — two live agent turns, and the ▷ ledger

Both opened the widget from the launcher at 1440 and sent through the composer.

| | dev, `127.0.0.1:3000` | prod, `127.0.0.1:3100` |
|---|---|---|
| question | 계양전기 유상증자 일정 알려줘 | 계양전기 신주인수권증서 상장예정기간 언제야 |
| widget on open | 440×620 at x=976, y=256, intro + 완전 익명 line | identical |
| composer state machine | idle 「직접 질문 입력 →」 → **「답변 준비 중…」** → **「중지」** → idle | identical |
| frames | 1 s intro · 2 s 도구 행 「이벤트 검색 「계양전기」 → 1건 · ① 유상증자 · 20260724000546」 · 3 s 「이벤트 읽기」 · 6 s answer | 1 s · 2 s (both tool rows) · 3 s answer |
| longest inter-frame gap | **3.0 s** | **1.0 s** |
| anatomy | 2 tool rows, verbatim 「」 citation, footer **`근거 1건 · 20260724000546 · 2026-08-23 09:52 KST`**, 5 DART 원문 links + `이벤트 상세` + `내 종목 조회` link rows, 다시 질문 | same shape, 3 DART links |
| `POST /api/ask` | **200** | **200** |
| SSE headers (prod, captured) | — | `content-type: text/event-stream; charset=utf-8` · `cache-control: **no-store, no-transform**` · `x-accel-buffering: no` · `transfer-encoding: chunked` · **no `content-encoding`** |
| console errors | 0 | 0 |

**P6.S7's fix 1 holds through the production Next router**: no `content-encoding`, `no-transform`
present, and the turn painted incrementally in both runtimes rather than in one burst.

▷ **agent turn done · answer · rounds 3 · tools 2 · blocked 0 · calls 3 (0 failed) · tokens
14,065 + 0 + 246 = 14,311 · thinking LOW · $0.0115 estimated** (dev)
▷ **agent turn done · answer · rounds 3 · tools 2 · blocked 0 · calls 3 (0 failed) · tokens
14,086 + 0 + 171 = 14,257 · thinking LOW · $0.0112 estimated** (prod)
▷ **pass total ≈ $0.0227 estimated on 2 turns, 6 calls, 28,568 tokens — never billed.**

---

## 5. Stage 2 — the functional sweep P5/P6 never ran

### (a) every visible control does something observable

Seven surfaces, **174 visible controls per runtime**, each clicked once from a **fresh page with
cleared storage** and located by a stable key rather than an index (see the harness note in §1 — the
first pass used indices and the 샘플 chip appearing mid-sweep shifted every later one, which
manufactured six phantom mis-clicks).

| surface | controls | controls with no observable effect |
|---|---|---|
| 관제 현황판 `/` | 77 | **0** |
| 내 종목 조회 `/stocks` | 10 | 2 — both vocky triggers |
| 종목 상세 `/stocks/00102618` | 14 | 2 — both vocky triggers |
| 이벤트 상세 `/events/…` | 31 | 2 vocky + 6 probe artefacts (below) |
| 내 포트폴리오(샘플) | 21 | 2 — both vocky triggers |
| 로그인 `/auth/login` | 13 | 2 vocky + 2 correct-behaviour (below) |
| AI 질문 `/ask` | 8 | 2 vocky + 1 correct-behaviour (below) |

Everything else did something and the effect was recorded: navigation, `aria-expanded` /
`aria-pressed` / `checked` flips, node-count changes, panel open, or **a new browser tab** — the 30
board `DART 원문 ↗` links and the event page's own `DART 원문 ↗` each opened exactly **1 new tab**.

**The eight non-vocky no-ops, re-measured:**

| what | verdict |
|---|---|
| 6 × `A "20260724000546"` inside the event page's `[근거]` popovers | **probe artefact.** `Citation.module.css` collapses a closed popover with `grid-template-rows: 0fr` + `.clip { overflow: hidden }` (and `opacity: 0`), so the anchor still has a 92×17 rect but is not hit-testable — `elementFromPoint` at its centre returns the row above it. **Open one `[근거]` and the anchor becomes hit-testable and opens a new tab.** Measured: 6 anchors, 1 hit-testable with one popover open, click → 1 new tab |
| `/auth/login` submit 로그인 with an empty form | **correct.** Both fields are `required`; `checkValidity()` false, the UA blocks submission, focus moves to the field, **0 requests**. Filled with credentials → 1 request and the signed 「이메일 또는 비밀번호가 일치하지 않습니다.」 |
| `/auth/login` **비밀번호 재설정** | **correct, and deliberate.** `disabled={pending \|\| email.trim() === ""}` with the reason in the source ("the endpoint answers 보냈습니다 for anything and would say it about nothing"). Disabled state is drawn: `--ink-3` + `cursor: default`; with an address typed it becomes `--ink-2` + `cursor: pointer`, and clicking it issues 1 request and renders 「재설정 링크를 보냈습니다 — 메일함을 확인해 주세요.」 |
| `/ask` composer submit with an empty box | **correct.** `disabled: true` when empty, `false` after one keystroke |
| the three `[의견]` / `의견 보내기` vocky triggers | **known and deliberate — Open Question Q1.** 3 `[data-vocky-trigger]` elements in the document, **0** vocky `<script src>` (`NEXT_PUBLIC_VOCKY_SRC` unset). Nothing to bind to. Not P7's to fix; no slice may invent a script URL |

### (b) interaction states — keyboard path and hover

No **keyboard trap** on any surface in either runtime, and **no invisible focus stop**:

- The event page has **11 focusable elements inside an `opacity: 0` / collapsed ancestor** (the
  `display:none` mobile sheet's five, and the six citation anchors) — and **the real tab order
  contains none of them**: 26 stops, 0 invisible. The `overflow: hidden` zero-height clip takes them
  out of sequential focus navigation. Measured by walking Tab, not inferred.
- The **only** dev-vs-prod difference in the keyboard path: every dev surface reports exactly **one**
  extra invisible stop, `NEXTJS-PORTAL` — Next's own dev-overlay web component. Prod has **0**
  invisible stops on all seven surfaces.
- Text fields indicate focus with the border (`P7.S5`); everything else with the 2px ring. Consistent
  on all 14 surfaces × runtimes.
- The active nav slot carries `aria-current="page"` + weight 600 in both runtimes, so a nav link to
  the page you are already on is a signposted no-op rather than a dead control.
- **Hover**, first 8 controls per surface: links, nav slots, vocky triggers, 샘플 종료, 수정, 삭제,
  the board rows' 회사명 and `↗`, the 펼치기 controls and the R6 launcher all change. Five do not —
  the four **board tabs**, the **lookup/stock 조회 submit**, the **auth 로그인 submit**, the **ask
  send button**, and the **샘플 chip**. Checked against the record before judging: the design record
  specifies hover in exactly two places (R6 §117 the launcher mark, R2 §vocky the trigger) and R2
  §Tabs draws the tabs' *active* state and hit size and **no hover**. So this is record silence, not
  a slip → catalogued (§7 item 8), not fixed. Both specified hovers verified live: the vocky trigger
  changes, and the **launcher frame stays [68,50] while the mark goes `none` → `matrix(1.35,…)`**.

### (c) liveness over time

Countdown ticked 62 s (`12일 13:38:31` → `13:37:29`); the **D-days did not move** in that minute,
which is correct — they are KST day counts computed upstream; the freshness line stayed
`기준 2026-08-22 04:14 KST · 30시간 전 데이터`; **0** unrequested navigations. Typing survived 130 s
(item 7).

### (d) dev-vs-prod differences — the P7 failure class, deliberately hunted

Three, all benign, none a product defect:

1. **Board expansion requests: dev 0, prod 366.** All are `GET /events/{rcept_no}?_rsc=…` **200** —
   Next's `<Link>` viewport prefetching, which is **production-only** (dev disables it). Nothing in
   the app sets `prefetch`; this is the framework default and predates P7. At **first paint** both
   runtimes issue **0** event prefetches and render 30 rows (docH 3047 @1440 / 4523 @390, identical
   in dev and prod) — so `P7.S3`'s window actually made this dramatically cheaper: the default page
   now prefetches nothing, and 366 is the cost only of a reader who clicks 펼치기 twelve times.
2. **One extra invisible tab stop in dev** — `NEXTJS-PORTAL`, Next's dev overlay (see (b)).
3. **A nav self-link on `/ask`**: dev issues 2 RSC requests and prod issues none, because the prod
   router already has the payload. Neither navigates, which is the correct outcome; only the wire
   traffic differs.

No product behaviour differed between the two runtimes anywhere else — the phase's whole reason for
existing is closed by measurement rather than assertion.

---

## 6. Stage 3 — cumulative headline smoke (the P7-touched surfaces)

27 checks; every one verified. Nothing regressed.

| check | measured |
|---|---|
| **horizontal overflow** — 7 surfaces × 1440/768/481/480/390 (35 combinations) | **none**, `scrollWidth == innerWidth` everywhere |
| **console errors / hydration warnings** — same 35 combinations | **none.** The only console entry anywhere is `/favicon.ico` 404 (pre-existing, `P7.S2` note 6) |
| **`.mono` split rule** (`P5.S19` fix 1) | 52 `.mono` elements on the landing render **six** distinct sizes — 43.7 / 16.15 / 14.25 / 12.825 / 11.4 / **11px** — not one flattened 12.825. Board tab counts **11px**, R2's literal |
| **D-day integrity** | all **30** rendered board D-days and company names identical to the served `countdown.dday`, in order |
| **추후결정 never beside a date** | 4 `tbd` rows, **0** carry a date or a D-day |
| **a past ② is 진행 중, never 종료** | 60 rows in the 전환청구 진행 중 strip, **0** say 종료 (sample: `CB \| 트리니티항공 \| ↗ \| 전환청구 개시 \| 2026-08-22 \| D+1`) |
| **②/③ rows carry no per-holding won** | 2 portfolio D-day rows, **0** violations |
| **estimate/fact marking** | 679,575원 and 446,720원 both sit with 「추정」; **15,552원 is untagged and must be** — it is 대동기어's filed `conversion_price`, served with `estimated: false`. A fact never carries the mark |
| **gate-failed field disclosed, not placeheld** | 「49.2억원추정은 할인율 인용이 게이트를 통과하지 못해 총액에서 제외했습니다」 |
| **조회 ↔ 포트폴리오 agree to the won** | 한화솔루션 500주 → **679,575원추정** on `/portfolio?sample=1` **and** on `/stocks/00162461` with the 500주 preset |
| **R2 §Tabs contract** | counts mono **11px**; active = weight **600** + **2px `rgb(234,242,237)`** (`--ink-1`) bottom rule, inactive transparent; **44px** hit at every width; full labels ≥481, compact labels at 390, wrapper `overflow-x: auto` |
| **R2 §Freshness, stale (live right now)** | mono **11px**, `rgb(224,87,63)` on `rgba(224,87,63,.15)` = `--alert` on `--alert-tint`, suffix `· 30시간 전 데이터`; inset notice with a **2px `--alert`** left rule sits **above the tabs**; **board opacity 1 — never dimmed** |
| **R6 §117 launcher hover** | frame fixed `[68,50]`, mark `none` → `matrix(1.35, 0, 0, 1.35, 0, 0)` |
| **P7-new elements across widths** | window control `356건 펼치기` at all five widths, min-height **32px ≥481 / 44px ≤480**, **16px** to the ② strip everywhere; typeahead panel `dx/dw/dy = 0/0/0`, 8 options, **40px ≥768 / 44px ≤767**, hit-testable and inside the viewport at every width |

---

## 7. OPERATOR CATALOGUE — every decision this phase accumulated

**This is the list the review must put in front of the operator.** Nothing here was changed by any
slice; each carries the default the phase implemented.

| # | question | what is live today | why it is the operator's |
|---|---|---|---|
| **1** | **Q1 — 의견 (vocky) has nothing to bind to.** | 3 `[data-vocky-trigger]` elements render on every surface, **0** vocky scripts load (`NEXT_PUBLIC_VOCKY_SRC` unset). Clicking any of them does nothing — **the only genuinely inert controls in the product**, re-measured on every surface in both runtimes this sweep | vocky ships no embeddable widget script (`P5.S19` catalogue #17). The operator must supply a script URL / capture path, or decide 의견 routes elsewhere (the agent already has a 의견 tool). **No slice may invent a URL** |
| **2** | **Q2 — how far does "no selected focus on all the input boxes" go?** | Collision reading #1: ring removed from text fields (`outline: none`), replaced by the field's own brightened hairline; the 2px ring stays on every button/link/tab/chip/checkbox. Measured contrast 3.30–4.01:1 | If the operator meant *zero* indication anywhere, that removes the record's a11y floor and needs their explicit call |
| **3** | **Q3 — how many firms is "some amount"?** | **30 initially, +30 per 펼치기 click** (D-P7-1), 12 clicks to reach all 386, control then disappears. Verified on all five origin/runtime combinations | No round names a number. A one-constant edit (`WINDOW_STEP` in `Board.tsx`) if the operator wants a different one |
| **4** | **Q4 — should a 챙겼습니다 row disappear?** | R5-8 implemented literally: label 놓친 돈 → **챙긴 돈**, hue `--alert` → `--live` on both label and value, **same figure** 679,575원, 「추정」 kept, **zero layout shift**, persists across reload | Removing the row supersedes a signed round |
| **5** | **Q5 — does the operator want live *data* refresh?** | Countdowns tick and nothing stomps typing, but board data is only as fresh as the last load. Right now the page correctly shows the stale state: 「기준 2026-08-22 04:14 KST · 30시간 전 데이터」 + the inset notice, board **never dimmed** | A polling refresh is behaviour no round specifies — a deferred job if wanted |
| **6** | **Q6 — the P5.S19 catalogue items P7 brushed.** | **#4** the footer's locked positioning line still reads 내 종목 **연결** and **#12** the hero `<h1>` reads 내 종목 **조회** — both now more visible with the nav slot gone (both confirmed rendering this sweep). **#6** the sample's 「실제 공시 **4건**」 subline above **five** live D-day rows — confirmed again: 대동기어 carries two events. **#10** `[근거]` + DART link under the 44px mobile floor. **#1** the English 404 sentence | None is P7's to rewrite |
| **7** | **Q7 — four reader-visible strings speak developer vocabulary but are promises.** | `API_TIER_KO`, `SPARSE_CLOSING_KO`, `GATE_COST_TAIL_KO`, `carryOverKo` — all still render (the gate tail was read live on both `/stocks/{code}` and `/portfolio`). Plus: with the sample caption now 「본인 표시」, should the **account** caption drop 「· 계정에 저장」 too? | Re-saying any of them in reader language is a copy decision, not an implementation one |
| **8** | **NEW — five interactive controls have no hover state, and the record is silent.** | The four **board tabs**, the **lookup/stock 조회 submit**, the **auth 로그인 submit**, the **ask send** button and the **샘플 chip** show no colour/border/opacity/transform change on hover. On the *same board panel*, 회사명, `↗` and 펼치기 all do. R2 §Tabs draws the tabs' active state, count size and 44px hit and **no hover**; the record specifies hover only for the R6 launcher mark and the R2 vocky trigger (both verified working) | Adding a hover treatment is a visual decision. Every one of these controls has its 2px focus ring and works on click — this is affordance polish, not a defect |
| **9** | **NEW — the focused input's hairline is brighter than the open candidate panel's side edges** (`P7.S5` note 1, now measured). | Hero: input `rgb(163,196,180)` vs panel sides `rgba(163,196,180,.4)`. `/stocks`: input `rgb(157,179,168)` vs panel sides `rgba(163,196,180,.32)`. Same hue, different alpha; panel `border-top: 0`, radius 0 | Matching them is one line in `SearchRow.module.css` — a visual decision, and `P7.S5`'s plan forbade touching that file |
| **10** | **NEW — two components draw the "mobile" boundary at different widths.** | `SearchRow` options are 44px below **768** and 40px above (`R4 §Mobile's touch floor; 40 from the tablet breakpoint`); the board's 펼치기 is 32px above **480** and 44px below. So at 481 a candidate row is 44px while the 펼치기 beside it is 32px | Both clear the 44px floor where R5 §Mobile applies (≤480). Aligning them is a geometry decision no round made |
| **11** | **NEW — the browser's own form validation speaks English.** | Submitting `/auth/login` empty produces Chrome's native bubble 「Please fill out this field.」 and blocks the request. It is UA chrome, locale-driven, not our copy — but on a Korean-only product surface a reader can reach it | Same class as `P5.S19` catalogue #1 (the English 404 sentence). Suppressing it means owning the validation copy, which is new Korean |
| **12** | **Q8 (`P7.S8`) — five record-silent portfolio items, all confirmed still live.** | **(A)** the D-day rows' **144.7px ragged left edge** at 1440 from `justify-content: space-between` — the one remaining "not organized" symptom; **(B)** 지나간 마감 states no 「기준 … (KST)」 line (the counting-down section does: 「기준 2026-08-23 (KST)」, read live); **(C)** 한화솔루션 and 세기상사 render an **empty 진행 중인 권리 cell** (confirmed in the live holding rows this sweep); **(D)** a 챙긴 돈 row still links 「놓친 돈 상세 →」; **(E)** the 「본인 표시」 caption renders checked or not | (A) is a geometry decision R5 never made; (D)/(E) would mint Korean or add a 22.6px click-time shift |
| **13** | **`s19-fidelity@example.com` (account id 14) is still in the dev database**, with one live `auth_session`, from `P5.S19` | Left in place as the plan instructed. This slice's own throwaway (`p7s9-probe@example.com`) was created and deleted through the product and is verified gone; `holding` and `lapse_claim` are both 0 | Deleting someone else's leftover row is the operator's call |

---

## 8. Stage 4 — disposition of every `S9` mention in `phase.md`

| line | what it asked | disposition |
|---|---|---|
| 34 | the decomposition row: the final sweep, in dev **and** prod, on the operator's own origins | **done** — 5 origin × runtime combinations, ~553 Stage-1 checks |
| 430 | `P7.S9` will meet `s19-fidelity@example.com` (id 14) during its sweep | **met and catalogued** (§7 #13), not deleted, per plan. DB re-verified after this slice's own throwaway was destroyed |
| 491 | the sweep must count **30, not 386** | **applied** — 30 at first paint on every origin, 386 only after 12 clicks; strips 30 → 90 → 94 → 30 |
| 566 | use the live corpus's `에스` / `계양`, not the plan's illustrative names | **applied** — `에스` 8 candidates + resolver miss, `계양` unique-prefix hit |
| 631 | the focused-input hairline vs candidate-panel seam, deliberately left alone | **measured and catalogued** (§7 #9) — not fixed, per `P7.S5`'s plan |

---

## 9. Fixes

**None. No file in the repository was changed by this slice.**

Nine probe FAILs were produced and every one was re-measured before being believed; not one survived
as a product defect:

| probe FAIL | resolution |
|---|---|
| "nav slots @1440 = 4" | probe: the mobile sheet's rows are in the same document; scoped to `nav[class*=links]` → 2 |
| "↓+Enter → `/stocks`" (both surfaces) | **harness bug** — a duplicate CDP keypress bypassed React's `preventDefault` (§1) |
| "12 펼치기 clicks → 30 rows" | **harness bug** — clicking below the fold (§1) |
| "챙겼습니다 flip did nothing" / "did not persist" | same harness bug — the row sits at y≈925 in a 900px viewport |
| "head↔row column offset −10.5px" | probe: the 4th track holds an empty `<span/>` in the head and the `justify-self: end` action pair in the row — D1b's own geometry. The three labelled columns are 0.0px |
| "head↔row offset −16px @390" | probe: at ≤480 the header is `display: none` (R5 §Mobile single column) |
| "flip caused a layout shift" | probe: `scrollIntoView` moved the viewport; document-relative geometry is identical |
| "landing console error" | probe: it is the `/favicon.ico` 404, filtered by text instead of by URL |
| "portfolio money figure untagged" | correct behaviour: 15,552원 is a served `conversion_price` with `estimated: false` — a fact must not carry the mark |
| "조회 ↔ 포트폴리오 disagree" | probe: the regex grabbed 대동기어's 전환가액. Both surfaces read **679,575원** for 한화솔루션 500주 |
| "8 controls do nothing" | 6 are collapsed-popover anchors (work once the popover opens), 2 are correct disabled/validation states; the 3 vocky triggers are Q1 |

---

## 10. Validation

| command | outcome |
|---|---|
| `cd frontend && npm run typecheck` | **pass** (exit 0) |
| `cd frontend && npm run smoke` | **pass** — 15 tests, 15 pass, 0 fail |
| `.venv/bin/python -m pytest` | **pass** — **139 passed**, 1 warning, 3.36 s (the phase's "59" baseline is stale, per `P7.S4` note 4) |
| the CDP check table | **pass** — §2/§5/§6; ~553 Stage-1 checks, 348 functional-sweep clicks, 27 smoke checks, 0 defects |
| `grep -c "Blocked cross-origin" var/stack/web.log` | **4** — unchanged, and all four are `P7.S1`'s deliberate negative controls (`evil.example.com` ×2, `100.1.2.3`, `192.168.1.9`). **Zero from `127.0.0.1` or the tailnet across this entire sweep** |
| `make stack-status` | **stack left up** — postgres up, api pid 25177, web pid 13009, `http://127.0.0.1:3000` + `http://100.77.164.42:3000` |
| `:3100` | **freed** — the isolated `next start` killed, nothing listening |
| `python3 scripts/workflow.py validate` | **Workflow validation passed** |

---

## 11. Deviations from `plan.md`

1. **No code was changed**, so the plan's "every code nit you fix" section is empty. That is the
   measurement, not a shortcut: the sweep produced nine FAILs and every one dissolved under a scoped
   re-measurement (§9). The things that could be improved are visual decisions, and they went to the
   operator catalogue (§7 items 8–11) rather than being invented in an executor.
2. **The plan's item-4 idiom "30 → 90 → 94 → 30" was re-measured rather than assumed** and came back
   identical, as did the whole-board counts (488/50/422/16) and the 386-row corpus.
3. **Item 3's `/portfolio` (sample) text field** does not exist until 수정 is pressed — the sample
   surface renders **0** text fields. The field was reached through the product's own 수정 and
   measured there (it is also `P7.S5`'s programmatic-focus case, and it passes).
4. **Item 10 added `/stocks/{corp_code}`** to the plan's page list: 「서버 전송 없음」 renders on the
   `HoldingStrip` of a stock page, not on `/stocks` itself, so checking only the plan's six pages
   would have reported the caption as "not rendered" rather than verifying it.
5. **The prod board-expansion request count (366) is reported as a dev-vs-prod difference rather
   than a failure** (§5(d)) — it is Next's production-only `<Link>` prefetching, it predates P7, and
   at first paint both runtimes issue zero.
6. Two live agent turns exactly, the plan's cap.
