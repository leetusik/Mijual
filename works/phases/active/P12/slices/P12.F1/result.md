# P12.F1 — result

- **status:** done
- **summary:** The chrome's account state is now seeded by the server: `RootLayout` reads
  `readAuthState()` beside the contact and passes it through `SiteChrome`'s
  `InitialAccountContext` into `useAccount()`, which reads it as its server snapshot and seeds the
  module store **client-side only**. The 로그인 link (signed out) and the account frame + email
  (signed in) are in the first painted HTML on 10/10 reader routes in dev and in a fresh local
  production build — measured with the hunt's own probe, they now land **15–60 ms before FCP**
  where the control lands them **7–257 ms after** it. Resting layout is pixel-identical
  (`AE = 0`), later client-side navigations still re-probe per path, and an anonymous reader costs
  zero extra API requests.
- **files_changed:**
  - `/Users/sugang/projects/personal/Mijual/frontend/app/layout.tsx`
  - `/Users/sugang/projects/personal/Mijual/frontend/components/chrome/SiteChrome.tsx`
  - `/Users/sugang/projects/personal/Mijual/frontend/components/chrome/useAccount.ts`
  - `/Users/sugang/projects/personal/Mijual/works/phases/active/P12/phase.md`
  - `/Users/sugang/projects/personal/Mijual/works/phases/active/P12/slices/P12.F1/result.md`
- **validation:**
  - `cd frontend && npm run typecheck` — pass (twice: after the edit, and again at the end)
  - `cd frontend && npm run smoke` — pass, 22/22
  - `NEXT_PUBLIC_SITE_URL=… MIJUAL_API_ORIGIN=… npm run build` in a fresh copy — pass, exit 0, **0
    warnings**, route table byte-identical to the HEAD control build (every page route `ƒ` dynamic)
  - four markup greps (dev + local production build × anonymous + signed-in) — pass
  - Aside `--account u2` before/after sweeps, 10 routes × {dev, production build} × {signed out,
    signed in}, 1280, plus 390 signed in — pass (table below)
  - resting-layout screenshots, signed out and signed in, HEAD build vs fixed build — `AE = 0`
  - downstream: client-side navigation, 로그아웃, 계정 삭제, stale cookie — pass
  - `python3 scripts/workflow.py validate` — **Workflow validation passed** (three pre-existing
    warnings: P4's `consolidation_owed` / `stale_docs=product`, and `oversized_doc_sections`)
- **deviations:** two, both in *how* the "before" was obtained, neither in the change itself — see
  *Deviations* below.
- **doc_impact:** two lines appended to `phase.md` (`frontend.md`, `security.md`) — quoted in the
  verdict at the end of this file.

---

## What changed

Ruling 1 of `phase.md`, implemented exactly: the `P4.F10` route lifted from one page to the chrome.

1. **`app/layout.tsx`** — `readAuthState()` runs in `Promise.all` beside `getSiteContact(...)`, and
   the result goes to `<SiteChrome contact={contact} initialAccount={auth}>`. The comment block
   records the measured reason, the request cost, and why the route table cannot move.
2. **`components/chrome/SiteChrome.tsx`** — a new optional `initialAccount?: AuthState | null`,
   provided to the reader tree through `InitialAccountContext` (React 19 `<Context value>` form,
   the same shape `AskProvider` already uses). `/ops` returns `children` untouched, so it provides
   nothing and the hook there behaves as before.
3. **`components/chrome/useAccount.ts`** — exports `InitialAccountContext`; `useAccount()` reads it
   as `initial` and:
   - `useSyncExternalStore(subscribe, () => snapshot() ?? initial, () => initial)` — the server
     render and the hydrating render both return `initial`, so hydration matches;
   - seeds the module store in a **client-only lazy `useState` initializer**
     (`typeof window === "undefined"` returns early), setting `state = initial` and
     `probedPath = pathname` once, idempotently — StrictMode's second pass finds `state !== null`.
   The header carries the whole seam, including *why the server must never write the module store*
   (module scope is shared across concurrent requests in one Node process).

Nothing visual changed and no CSS, `AccountSlot.tsx` rendering or `Nav.tsx` layout was touched.

## The numbers

Probe: the R1 seam — `Page.addScriptToEvaluateOnNewDocument` installed before `goto`, a
`MutationObserver` on `document` (never on `documentElement`), FCP from a buffered `paint`
observer, CLS from a buffered `layout-shift` observer, one route per `page.evaluate` argument.
`delta` = (time the `a.login` / `button.frame` node entered the DOM) − FCP, in ms. **Negative is
the fix**: the element exists before the first contentful paint.

### Signed out, 1280

| Route | dev after | dev before (HEAD) | prod-build after | R1's "before" |
|---|---|---|---|---|
| `/` | **−58.1** (fcp 312) | +256.8 (fcp 288) | **−60.3** (fcp 224) | +293 dev |
| `/stocks` | **−20.9** | +27.9 | **−27.4** | +46 |
| `/stocks?q=zzz` | **−16.2** | +25.6 | **−17.3** | +69 |
| `/stocks/00547510` | **−24.4** | +32.1 | **−21.3** | +49 |
| `/portfolio` | **−28.5** | +37.3 | **−20.9** | +52 |
| `/portfolio/notifications` | **−52.7** | +26.4 | **−56.1** | +46 |
| `/ask` | **−15.2** | +20.0 | **−17.7** | +70 |
| `/events/20260806000329` | **−32.3** | +26.1 | **−37.6** | +51 |
| `/auth/login` | **−26.8** | +26.9 | **−21.0** | +56 |
| `/auth/reset` | **−16.3** | +30.1 | **−16.0** | +73 |

10/10 routes, both runtimes. The link's rect is `[1138.73, 15.03, 37.27, 20.92]` in every reading,
before and after (R1's 37.27 px link). CLS is unchanged route by route: 0 everywhere except the
landing's 0.00045 and the event page's 0.00002 — **identical in the control**.

### Signed in, 1280 (throwaway account, dev)

| Route | dev after | prod-build after | prod-build before (HEAD build) |
|---|---|---|---|
| `/` | **−56.5** | **−55.4** | +96.2 |
| `/stocks` | **−19.0** | **−21.9** | +10.9 |
| `/stocks?q=zzz` | **−17.5** | **−27.2** | +8.9 |
| `/stocks/00547510` | **−23.9** | **−30.9** | +11.4 |
| `/portfolio` | **−18.1** | **−22.7** | +14.4 |
| `/portfolio/notifications` | **−45.9** | **−38.0** | +32.7 |
| `/ask` | **−21.1** | **−27.4** | +9.2 |
| `/events/20260806000329` | **−43.9** | **−38.4** | +7.8 |
| `/auth/login` → `/portfolio` | **−16.8** | **−26.6** | +6.6 |
| `/auth/reset` → `/portfolio` | **−33.8** | **−27.3** | +7.5 |

The frame's rect is `[914.72, 9.5, 261.28, 32]` in **every** reading on both sides — P12.S1's number,
unmoved. A signed-in reader on `/auth/login` or `/auth/reset` is client-redirected to `/portfolio`
(confirmed by reading `location.pathname` at the end of each run), which is why those two rows
report the portfolio's numbers on both sides.

Dev "before", signed in, was taken as a single-navigation diagnostic rather than a sweep (see
*Deviations*): `/stocks`, fcp 268 ms, frame inserted at **321.8 ms (+53.8)**, with
`GET /auth/me` on the wire 310 → 320 ms. That is R1's +37 ms finding reproduced.

### 390, signed in

`/stocks`: the frame node is in the HTML **102.3 ms before FCP**, CLS 0, and its rect is `0×0` —
the desktop slot is `display: none` below 481 exactly as before. Opening the sheet shows the
identity row rendered from the same seeded store: `identityRow` `[0, 148, 390, 54]` with the email,
then 알림 설정 `[0, 202, 390, 48]` and 로그아웃 `[0, 250, 390, 48]`.

## The markup is the proof of mechanism — the four greps

| Request | classes in the served HTML | email |
|---|---|---|
| `curl http://127.0.0.1:3010/` (no cookie) | `…__login`, `…__loginRow` | — |
| `curl http://127.0.0.1:3014/` (no cookie, production build) | `…__login`, `…__loginRow` | — |
| `curl -H "Cookie: mj_session=…" …:3010/` | `…__slot`, `…__frame`, `…__email`, `…__caret`, `…__identityRow`, `…__sheetEmail`, `…__loginRow`, `…__sheetAction` | 4 occurrences |
| `curl -H "Cookie: mj_session=…" …:3014/` | the same eight | 4 occurrences |

**Controls.** At HEAD the same four requests return exactly one class — `…__slot`, the empty div —
and **zero** email occurrences, in dev and on a HEAD production build served on 3015.

**No cross-reader bleed, and the anonymous reader pays nothing.** Nine interleaved renders of
`/stocks` on the production build (signed-in, anonymous, anonymous ×3 rounds): the signed-in
response carried the email 4 times every round, both anonymous responses carried it 0 times and the
로그인 link instead, and `var/stack/api.log` grew by exactly **3** `/auth/me` requests — one per
signed-in render, **none** for the six anonymous ones (the `P4.F10` no-cookie short-circuit).

## Resting layout — `AE = 0`

Full-window PNGs of `/stocks` settled (2.5 s), HEAD production build (3015) vs fixed production
build (3014), same browser, same window:

- signed in: `compare -metric AE` → **0** (files byte-identical, md5 `cd03f437…`)
- signed out: **0** (md5-identical)
- positive control, same pipeline: `/ask` vs `/stocks` → `AE = 1.0114e+09`; signed-out vs signed-in
  `/stocks` → `AE = 5.28731e+07`. So the zero is a measured zero, not a stuck instrument.

One instrument seam worth recording: `Emulation.setDeviceMetricsOverride` sets the layout viewport,
but `page.screenshot()` still returns the **real window** surface — these PNGs are 1440 px wide, not
1280. The 1280 evidence is the rect equality above, which comes from the metric-overridden probe.

## Nothing regressed downstream

- **Client-side navigation** `/` → `/ask` → `/portfolio` → `/` (real nav clicks, 144 rect samples at
  60 ms): **one distinct slot rect**, `frame[914.72, 9.5, 261.28, 32]`, and the slot is **never**
  absent — R1's refuted sub-claim still holds. `GET /auth/me` fired **3** times (2794 / 4927 /
  7265 ms): once per client-side navigation and **zero at boot**. That is the whole design — the
  server's answer replaces the boot probe and changes nothing after it.
- **로그아웃** from the menu → `http://127.0.0.1:3010/auth/login`, signed out (`…__login` 로그인),
  and the 로그아웃되었습니다 flash renders once. Its post-paint arrival is R1 F4 / `P12.F5`'s
  business and was deliberately not touched.
- **계정 삭제** (`/portfolio/notifications` → confirm) → lands on `/`, signed out, 로그인 link
  rendered. `POST /auth/login` with the deleted credentials answers **401**: the account is gone.
- **Stale cookie** (the session ended by 로그아웃, cookie value replayed): `GET /stocks` answers
  **200** with the anonymous 로그인 link and no email, on dev and on the production build. Never an
  error — `readAuthState()` treats it as anonymous.
- **`/ops`** still answers 200 and its HTML contains **no** `AccountSlot` markup at all.

## Privacy / caching

The signed-in reader's own email is now in their HTML. Checked, and **nothing changed**:

- production build, signed-in `GET /`:
  `Cache-Control: private, no-cache, no-store, max-age=0, must-revalidate` — shared caching is
  forbidden. The **HEAD build returns the identical header**, so this is Next's dynamic-render
  default, not something this slice introduced or must maintain.
- `deploy/edge/jujutower.conf` declares **no `proxy_cache_path` and no `proxy_cache` zone** — the
  only `proxy_cache off` is the `location = /api/ask` SSE block. The edge caches no HTML.
- `deploy/runbook.md`'s "caches for 10 minutes" is the app's own `next: { revalidate: 600 }` on the
  **contact** fetch (public data). The session read passes no `cache`/`next` option and is
  uncached — proved by the nine-render interleave above.

Nothing worth a new rule; the Doc impact line records the fact rather than a change.

## Deviations from `plan.md`

1. **The signed-in "before" numbers come from the HEAD production build (3015), not from a
   `git stash` sweep in dev.** I ran the stash sweep first and it returned ten *negative* deltas —
   i.e. it claimed HEAD already rendered the frame before FCP, which contradicts R1, contradicts the
   HEAD markup (empty slot), and is therefore wrong. A single-navigation diagnostic taken in the
   same stashed state on `/stocks` gave the correct +53.8 ms with `/auth/me` at 310–320 ms, so the
   fault is in running a 10-route sweep against `next dev` seconds after a `git stash` — the dev
   server kept serving already-compiled output for routes it had compiled during the "after" sweep.
   I discarded that sweep and built the control instead: a **second production build from HEAD**
   (the same three files taken from `git show HEAD:…`) served on port 3015, which has no
   recompilation seam at all. The signed-**out** dev stash control was kept: its numbers
   (+20 … +257) match R1's fingerprint and are internally consistent.
2. **The throwaway account's cookie was read over CDP (`Network.getCookies`), not from
   `document.cookie`.** `mj_session` is `HttpOnly`, so `document.cookie` cannot see it. The account
   itself was created through the signup form in Aside, as the plan requires, and deleted through
   계정 삭제.

Not a deviation, but worth naming: a difference I saw between the two production builds on
signed-in `/portfolio` (CLS 0.05419 on 3014, 0 on 3015) is **not** attributable to this change. The
band is F3's 195.28 px 계정 이전 carry-over, and it renders only when the origin's `localStorage`
holds `mijual.portfolio.sample`. Storage is **port-scoped**: 3010 and 3014 carry that key from
earlier sample-mode visits, the freshly-used 3015 does not. Verified by reading `localStorage` on
all three origins.

## Instrument

**Aside `repl` over Bash, `aside repl --account u2`** (profile 「claude2」) — never `u0`, never
`aside account use`. Every invocation opened its own tab (tabs do not survive between CLI calls) and
did its whole job in one script. Confirmations of the phase's recorded seam, plus three new edges:

- top-level `await` works, but a top-level `return` makes the whole script fail to parse with a
  misleading *"await is only valid in async functions"* — use `console.log`, never `return`;
- `page.getByRole({name: "계정 만들기"})` fails on Korean names (`Role selector not found:
  role:button[name*=%EA%B3%84%EC%A0%95…]`) — click by `textContent` in `page.evaluate` instead;
- `page.screenshot()` captures the real window, ignoring `setDeviceMetricsOverride` (above). It is
  fresh, though: the positive control proves it.

There is no `page.waitForTimeout`; `await new Promise(r => setTimeout(r, ms))` is the wait.

## Hygiene

Throwaway account `p12f1+1788457732@example.com` created through the signup form and deleted through
계정 삭제 (login now 401). **Production was never touched** — every run was `127.0.0.1`.
`NEXT_PUBLIC_VOCKY_SRC` unset. Both scratch servers (3014 fixed build, 3015 HEAD control build)
stopped and their ports confirmed closed. The dev stack is exactly as found (`make stack-status`:
postgres up, api pid 60158, web pid 61423). The two build copies live under the session scratchpad,
outside the repo; nothing was built into the working tree's `.next`.

## Notebook

`phase.md` edited per the plan: one `## Decisions` line (the chrome's account state is
server-seeded, with the never-write-on-server rule and the measured after-numbers), two
`## Doc impact` lines, two `## Notes for later slices` entries (one for `P12.F2` on how the context
is provided, one for `P12.S2` on the new per-signed-in-render API request) plus one measurement
note for the remaining fix slices, and a rewritten `## Now`. The shared bar note
`**(from P12.DECOMP2, for P12.F1 … P12.F9)**` was left in place — eight slices still need it.
