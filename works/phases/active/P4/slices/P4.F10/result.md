# P4.F10 — result

- **status:** done
- **summary:** `/events/{rcept_no}` now resolves the reader's session on the **server**
  (`readAuthState()` in `Promise.all` beside `getEvent()`) and threads a bare
  `initialAuthenticated: boolean` down `EventDetail` → `EventHeader` → `DeadlineOffer`, which renders
  the correct one of R5-2's two labels in the server HTML and skips its client probe there. Cold-cache
  mobile CLS on that route falls **0.0328 → 0.0003** (desktop 0.0106 → 0.0017, all of it F5's known
  Plex Mono race), the settled rendering is **pixel-identical** (`AE = 0`), and every other host
  surface is untouched. `readAuthState()` also short-circuits a request carrying **no cookie at all**
  to anonymous, so the added server read costs an anonymous reader — and a crawler — no API call.
- **files_changed:** `frontend/app/events/[rcept_no]/page.tsx`,
  `frontend/components/event/EventDetail.tsx`, `frontend/components/event/Header.tsx`,
  `frontend/components/auth/DeadlineOffer.tsx`, `frontend/lib/session.server.ts`,
  `works/phases/active/P4/phase.md`, `works/phases/active/P4/slices/P4.F10/result.md`
- **validation:** `npm run typecheck` (`tsc --noEmit`) → **clean**; `npm run smoke` → **22/22**;
  `npm run build` in the build copy → **exit 0** (`✓ Compiled successfully`, TypeScript finished, 21
  static pages); SSR `grep -c` proofs on the served HTML, all six as specified (table §2);
  before/after cold-cache CLS sweep, 3 routes × 2 profiles × 3 loads each on two real builds
  (table §3); `*/auth/me*` blocked → the correct line is still at first paint (§4); server-side
  `/auth/me` call counting in `var/stack/api.log` (§5); TTFB 20 + 20 paired requests (§5);
  `magick compare -metric AE` = **0** on 4 settled screenshots (§6); no console error or hydration
  warning on 4 loads (§7); `python3 scripts/workflow.py validate` → **passed** (pre-existing
  `oversized_doc_sections` warning only); `git diff --stat` → the five frontend files, `phase.md`,
  this file (plus the generated `works/` files `start-slice` already touched).
- **deviations:** three, all recorded below — (1) **the plan's "no `GET /auth/me` request leaves the
  browser on that page" could not be met inside this slice's file scope, and should not be:** that
  request is the **chrome's** (`components/chrome/useAccount.ts`, fired on every route), and
  `lib/session.ts` already shared it in flight with the offer line, so the page always made exactly
  **one** probe and still does — the defect was the *insertion*, not the request. Proved instead, and
  more strongly, by blocking `*/auth/me*` outright: the correct line is in the DOM at first paint
  regardless (§4). (2) **A fifth file, `frontend/lib/session.server.ts`**, for the no-cookie
  short-circuit the plan invited (§5 says what it buys and why it keys on emptiness, not on the
  cookie's name). (3) **The logged-in half was proved with a throwaway account created on the DEV
  database** (`POST /auth/signup`) and **deleted** afterwards through `DELETE /auth/account`; nothing
  was created on production, and the account's password never left a 600 scratchpad file that is now
  removed.
- **doc_impact:** three lines appended to `phase.md` — `frontend` (the event page's request-time
  session read, `DeadlineOffer`'s `initialAuthenticated`, the probe skipped there, and
  `readAuthState`'s no-cookie short-circuit), `security` (a server-resolved session travels as the
  one bit the surface needs — the account never enters the HTML; the page's response is already
  `private, no-store`), and `qa` (the regression line: the line is in the **server** HTML on an event
  whose deadline is ahead, the logged-in variant replaces it for a cookie-carrying request, 0 on a
  past or 추후결정 event, and cold-cache mobile CLS ≤ 0.01 on that route).
- **doc_versions:** n/a (not a review slice — versioning is deferred to a docs phase)
- **review_verdict:** n/a
- **walkthrough:** none
- **explain:** n/a
- **operator_need:** none. One item is worth a line in the P4 gate walkthrough because only the
  operator can see it: **signed in**, an event page whose deadline is still ahead must show
  「보유 종목에 담기 →」 with no flicker of the anonymous label.

---

## 1. What changed

Five files, no new file, no test file (verified live, per the contract), no copy string added or
moved, no CSS touched.

| file | change |
|---|---|
| `app/events/[rcept_no]/page.tsx` | `const [detail, auth] = await Promise.all([getEvent(rceptNo), readAuthState()])` — the 404 branch is byte-for-byte the one that was there; renders `<EventDetail detail initialAuthenticated={auth.authenticated} />` |
| `components/event/EventDetail.tsx` | optional `initialAuthenticated?: boolean` prop, passed straight to `<EventHeader>` |
| `components/event/Header.tsx` | same prop, passed to `<DeadlineOffer>`; **the deadline-ahead gate, the two labels, `.offer` and the markup around it are untouched** |
| `components/auth/DeadlineOffer.tsx` | `useAuthState(initialAuthenticated === undefined)` — the probe is switched **off**, not ignored, when the server answered; `initialAuthenticated ?? (probed?.authenticated)`, with `null` (= not known) still rendering nothing |
| `lib/session.server.ts` | `readAuthState()` returns `ANONYMOUS` without calling the API when the request carries **no cookie at all** |

`DeadlineOffer`'s doc-comment now records that its "nothing renders until the session is known"
reading is **honoured by the server** on the event page — the reading did not change, the answer
simply exists earlier. Every other host passes nothing, keeps the probe, and behaves exactly as
before; `grep -rn DeadlineOffer` finds exactly one mount (`components/event/Header.tsx:145`), and
`ConversionOffer` — the other `useAuthState` caller, on 종목 조회 — was not touched.

**RESPECT THE DESIGN.** R5-2/R10's line, its two labels, its placement, its 44 px (≤767) / 32 px
geometry and its deadline-ahead gate are unchanged. The only thing that moved is *when* the correct
state is known.

## 2. The line is now in the server HTML (`curl` + `grep -c`)

Local production build on :3014, against the dev API on 8010. `이 마감 알림 받기` = anonymous,
`보유 종목에 담기` = logged in.

| request | event | before | after |
|---|---|---|---|
| anonymous, deadline ahead | `20260806000329` 툴젠 D-4 | 0 / 0 | **1** / 0 |
| session cookie, same event | `20260806000329` | 0 / 0 | 0 / **1** |
| anonymous, deadline past | `20260724000546` 계양전기 D+9 | 0 / 0 | 0 / 0 |
| session cookie, deadline past | `20260724000546` | 0 / 0 | 0 / 0 |
| anonymous, 추후결정 | `20260623000409` 경남제약 | 0 / 0 | 0 / 0 |
| session cookie, 추후결정 | `20260623000409` | 0 / 0 | 0 / 0 |

The hrefs are the signed ones and are built server-side: `href="/auth/login"` anonymous,
`href="/portfolio?add=00547510"` logged in. **The account never enters the HTML**: grepping a
logged-in render for the test account's address returns **0**. The page's own response header is
unchanged and already private — `Cache-Control: private, no-cache, no-store, max-age=0,
must-revalidate` — so the two variants cannot be cross-served by a shared cache.

## 3. Cold-cache CLS — two real builds, same instrument

Both columns are full `npm run build` + `node .next/standalone/server.js` on **:3014** (`.next/static`
and `public/` staged in), the *before* column built from `HEAD`'s five files and the *after* column
from the working tree. Real Google **Chrome 152.0.7977.65**, headful, throwaway profile
(`scratchpad/chrome-f10`), CDP port **9392**, fresh tab and cleared cache per load.
Mobile = 412 × 915 @ DPR 2.625, 4× CPU, 150 ms / 1.6 Mbps; desktop = 1280 × 800 unthrottled.
**3 loads per cell, medians.**

| route | mobile before | mobile after | desktop before | desktop after |
|---|---|---|---|---|
| `/events/20260806000329` | **0.0328** | **0.0003** | **0.0106** | **0.0017** |
| `/stocks/00547510` | 0.0002 | 0.0002 | 0.0000 | 0.0000 |
| `/portfolio?sample=1` | 0.0000 | 0.0000 | 0.0000 | 0.0000 † |

The before column reproduces `P4.F5`'s 0.0325/0.0328 and 0.0089–0.0106 exactly, which is what makes
the two columns comparable. Before, every mobile run reported one shift entry —
`(2363 ms, 0.0325, Event-module__offering)`, landing ~5 ms after `GET /auth/me`'s `responseEnd` at
~2358 ms. After, **no shift entry of any size is recorded on that route at all** and the residual
0.0003 is a single sub-0.001 entry early in the load.

The desktop **0.0017** is `P4.F5`'s already-attributed Plex Mono swap (it proved it by blocking
`*IBMPlexMono*`), not this line: it appears in 2 of 3 runs and the third reads 0.0000, exactly the
race F5 described. Not mine, and 6× under the target.

† `/portfolio?sample=1` desktop showed 0.0004 in 2 of the 3 after-runs and 0.0000 before, so it was
re-run **5 more times**: `[0.0004, 0, 0.0004, 0, 0]`, **median 0.0000**. It is an intermittent
sub-0.001 client race on that surface, below the 0.002 threshold at which the harness even names a
shift source — and no code on that route changed (the sample page does not mount `DeadlineOffer` and
does not call `readAuthState`).

## 4. The proof that the state no longer waits on the browser

With `Network.setBlockedURLs(["*/auth/me*"])` — the probe cannot resolve at all — the after build,
sampled at 1.2 s (mobile) / 0.35 s (desktop), long before any probe could have answered:

```
prof=mobile  block=True  CLS=0.0003  auth/me requests=[(2199 ms, 0 bytes → blocked)]
  early:   [{'txt': '이 마감 알림 받기 →', 'href': '/auth/login', 'h': 44}]
  settled: [{'txt': '이 마감 알림 받기 →', 'href': '/auth/login', 'h': 44}]
prof=desktop block=True  CLS=0.0017  ... 'h': 32
```

Same page, same viewports, cookie set through CDP (`Network.setCookie`, `mj_session`), probe **not**
blocked — the server-rendered logged-in variant, present at 1.2 s and unchanged at 9 s:

```
prof=mobile  logged_in=True   CLS=0.0003
  early:   [{'txt': '보유 종목에 담기 →', 'href': '/portfolio?add=00547510', 'h': 44}]
prof=desktop logged_in=True   CLS=0.0017   ... 'h': 32
prof=mobile  logged_in=False  CLS=0.0003   → '이 마감 알림 받기 →', '/auth/login'
```

**Why one `GET /auth/me` still leaves the browser** (the plan's fourth proof, and the first
deviation): it is the **chrome's** probe — `components/chrome/useAccount.ts`, once per path, for the
nav's 로그인 / 축약 이메일 slot — and the sweeps show the identical single request on `/stocks` and
`/portfolio?sample=1`, which do not mount `DeadlineOffer` at all. `lib/session.ts` has always shared
that request in flight with the offer line, so the event page made exactly **one** probe before this
slice and makes exactly one now: **the request count never was the defect, the insertion was.**
Removing it entirely means an auth read in the root layout on every route — a different slice with a
different blast radius, and not something to do quietly inside a CLS fix.

## 5. What the added server read costs (nothing, measurably)

`readAuthState()` short-circuits a request with an empty `Cookie` header to anonymous without calling
the API. Measured against the dev API's own access log (`var/stack/api.log`):

| 3 renders of `/events/20260806000329` | `GET /auth/me` lines added |
|---|---|
| anonymous (no cookie) | **0** |
| carrying a session cookie | **3** |

TTFB of the same page, 20 requests each, local production build: **13.1 ms** anonymous vs **13.0 ms**
with a session (medians; min/max 8.5–17.7 and 9.9–14.1). The read is in `Promise.all` with
`getEvent`, so even when it does fire it is not added serially.

The short-circuit keys on **emptiness, never on the cookie's name**. Naming `mj_session` in the
frontend would duplicate a backend constant here, and a rename would then make this read answer
"anonymous" for readers who are logged in — the precise failure `DeadlineOffer`'s doc-comment exists
to prevent. Emptiness cannot go stale that way: this session lives in a cookie and nowhere else, so a
request with no cookies cannot be authenticated.

## 6. RESPECT THE DESIGN — the settled rendering did not move a pixel

Full-page screenshots of both builds, font loaded, with CSS animation/transition and the ticking
countdown frozen (`P4.F5`'s control, whose noise floor is `AE = 0` for two shots of one build):

| capture | dimensions | `magick compare -metric AE` |
|---|---|---|
| `/events/20260806000329` at 390 | 780 × 4394 | **0** |
| `/events/20260806000329` at 1280 | 1280 × 1465 | **0** |
| `/stocks/00547510` at 390 | 780 × 3126 | **0** |
| `/stocks/00547510` at 1280 | 1280 × 1095 | **0** |

Identical document heights, identical pixels. The reader sees a different page only in the **first
2.4 seconds**, where the line is now already there instead of arriving.

## 7. Hydration and console

`console.error` / `console.warn` / `window.onerror` captured from document start on four loads —
event page anonymous, event page with a session, `/stocks/00547510`, `/portfolio?sample=1` — and
every one returned `[]`. The server HTML and the first client render agree in both states (the
component reads the same boolean the server rendered from), so there is no mismatch to warn about.

## 8. Where it was verified, and what was left running

- **Runtime.** `## Operator Runtime` (operations doc) records the dev stack on 3010/8010 and — via
  `P4.S4`'s owed Doc-impact line — production as a standalone build behind Cloudflare. This slice
  ships nothing, so the target was the **local production build** on :3014, the same
  `node .next/standalone/server.js` path the box runs, exactly as `P4.R1`/`P4.F5`/`P4.F6`/`P4.F8`
  used. The change was additionally read in the operator's own **dev runtime** (`next dev` on 3010,
  one read-only GET): the served HTML there carries the line too (`grep -c` → 1, status 200).
- **Instrument.** Real Google Chrome 152 over the DevTools protocol, headful, launched through
  LaunchServices with a **throwaway profile** (`scratchpad/chrome-f10`) on port **9392** — never the
  operator's profile. **Aside was not used and is not installed on this Mac** (no daemon, no agent
  account); this is the fallback instrument `## Operator Runtime` names.
- **Everything started was stopped.** `node server.js` on :3014 — pids **68576** (before build) and
  **69291** (after build), both killed, port free. Chrome closed with `Browser.close`; :9392 answers
  nothing and no process matches `remote-debugging-port=9392`. The operator's stack was never touched
  and answers **3010 → 200** and **8010 /health → 200** after the run.
- **The one write anywhere: a throwaway DEV account**, `f10-probe@example.invalid`, created through
  `POST /auth/signup` (with the app's own `X-Mijual-CSRF` header) and removed through
  `DELETE /auth/account` → `{"deleted": true}`, which hard-deletes the row and cascades its sessions;
  its cookie afterwards reads `{"authenticated": false}` and the page renders the anonymous line
  again. The password was generated into a 600 scratchpad file that has been deleted, and appears in
  no transcript, log or file here. **Nothing on the box, no deploy, production read-only — not a
  single production request was made in this slice.** No secret value appears anywhere in this file.

## 9. Artefacts (all outside the repo, in the session scratchpad)

`f10_build.sh` / `f10_serve.sh` (+ `f10_build_{before,after}.log`, `f10_web3014_{before,after}.log|pid`),
`f10_cls.py` + `f10_cls_{before,after,after2}.jsonl` (the cold-load sweeps, `/auth/me` requests
recorded per load), `f10_blocked.py` (the blocked-probe proof), `f10_loggedin.py` (the cookie'd
render at both viewports), `f10_console.py` (hydration/console capture), `f10_shot.py` +
`f10_{before,after}_{event,stock}_{390,1280}.png` and the four `f10_diff_*.png`, and `r1fe/` —
`P4.R1`'s build copy, rebuilt twice on this slice's sources. `r1_cdp.py` (R1's CDP client, profiles
and observers) was reused unchanged. Nothing was written into the repository except the five frontend
files, `phase.md` and this file.
