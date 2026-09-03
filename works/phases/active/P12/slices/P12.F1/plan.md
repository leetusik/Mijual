# P12.F1 — Chrome first paint I: the server seeds the account state (R1 F1, account half)

`kind: fix`, `risk: high` → `slice-executor-high`. Written 2026-09-04 by the orchestrator in `auto`
mode, after `P12.DECOMP2` (`f7d6619`). Closes the account half of the hunt's rank-1 finding.

## Read first

- `phase.md`: `## Decisions` — **Ruling 1** (this slice's mechanism, in full), the instrument seam,
  the runtime and build recipe; the shared note `**(from P12.DECOMP2, for P12.F1 … P12.F9)**` —
  the bar this slice meets (do **not** remove it; eight slices still need it).
- `slices/P12.R1/result.md` § F1 — the "before" numbers: `a.AccountSlot-module__login`
  (signed-out) / `button.AccountSlot-module__frame` (signed-in) inserted **+45 to +293 ms after
  FCP** in dev, **+3 to +165 ms** on the production build, 10/10 routes, CLS 0 (a pop-in, not a
  shift — the nav's right group grows leftward from a pinned right edge at 1176). And the refuted
  sub-claim: the store **keeps** its answer across client-side navigation (the slot never blanks
  mid-visit); only the boot gap is the defect.
- The code: `frontend/app/layout.tsx` (the `async` root layout, `getSiteContact` in it),
  `frontend/components/chrome/SiteChrome.tsx` (client, takes `contact`), `useAccount.ts` (the
  module store + `useSyncExternalStore(subscribe, snapshot, () => null)` + the per-path probe),
  `AccountSlot.tsx` (renders `<div class=slot/>` while `account === null` — do not touch this
  file's rendering), `Nav.tsx` (mounts `AccountSlotDesktop` / `AccountSlotSheet`),
  `frontend/lib/session.server.ts` (`readAuthState()`: cookie-forwarded, never throws, **no
  request at all without a cookie**), `lib/session.ts` (`fetchAuthState`, `setAccountState`
  consumers), `lib/api.ts` `request()` (a server `fetch` with no `cache`/`next` option → uncached),
  and `components/auth/DeadlineOffer.tsx` + `app/events/[rcept_no]/page.tsx` (the P4.F10 precedent).

## The change

1. **`app/layout.tsx`** — read the session beside the contact:
   `const [contact, auth] = await Promise.all([getSiteContact(...).catch(() => null), readAuthState()])`
   and pass it: `<SiteChrome contact={contact} initialAccount={auth}>`. Anonymous readers (no
   cookie) cost **zero** extra requests; a signed-in reader pays one server-side `GET /auth/me`
   per page render, which replaces the client's boot probe rather than adding to it. Reading
   `cookies()` keeps every route request-time, which they already are (nothing is prerendered,
   `frontend` doc v0014 / P11.F3) — confirm `npm run build` still reports every route dynamic.
2. **`SiteChrome.tsx`** — accept `initialAccount?: AuthState | null` and provide it to the tree
   through a React context (the slots are two levels down in `Nav.tsx`; a context beats threading
   a prop through the nav). `/ops` returns children untouched as today.
3. **`useAccount.ts`** — the store learns its initial value **without ever writing the module
   store on the server**. Module-level `state` / `probedPath` are shared across every concurrent
   request in the Node process, so the server must only *read* the context value:
   `useSyncExternalStore(subscribe, () => state ?? initial, () => initial)` — server render and
   the hydrating client render both return `initial`, so the markup carries the right slot and
   hydration matches. On the client, seed once, idempotently, before the boot effect can run:
   `if (state === null && initial != null) { state = initial; probedPath = pathname; }` in a
   client-only lazy initializer (`useState(() => …)` guarded by `typeof window !== "undefined"`,
   or an equivalent that StrictMode's double render cannot break — remember `P7.S2`'s lesson in
   this file's own header). `probedPath = pathname` is what skips the boot probe for the initial
   path; every later client-side navigation re-probes exactly as today, and `setAccountState`
   (로그아웃, 계정 삭제, 수신 주소 변경) is unchanged. When no `initialAccount` is provided
   (`/ops`, or any host that does not pass one) the hook behaves byte-for-byte as before.
4. Comments: extend `useAccount.ts`'s header with the seam (why the server never writes the
   store; why `initial` is the server snapshot) and `layout.tsx`'s with the read, both pointing at
   `P12.F1` and `P4.F10`. `AccountSlot.tsx`'s "renders nothing until the probe answers" remains
   true and needs no edit — the answer simply arrives with the HTML.

Nothing visual changes: the signed-out link and the signed-in frame render exactly as today, just
in the first paint. **RESPECT THE DESIGN** — no skeleton, no reserved box, no restyle.

## Verification (the shared bar, applied)

- `cd frontend && npm run typecheck`, `npm run smoke`.
- **The markup is the proof of mechanism:** `curl -s http://127.0.0.1:3010/` (no cookie) must
  contain the 로그인 link inside the nav; the same request with the throwaway account's `mj_session`
  cookie (copy it from the Aside profile's `document.cookie` after signing in, or from the signup
  response's `Set-Cookie`) must contain the account frame with the email. Repeat both on the
  local production build. Record the four greps.
- **Before/after with the hunt's probe**, Aside `--account u2`: the R1 late-insert timeline
  (`Page.addScriptToEvaluateOnNewDocument` before `goto`, `MutationObserver` on `document`,
  `first-contentful-paint` from `performance`) on **all 10 routes** at 1280 in dev, signed-out and
  signed-in, then the same on a **fresh** local production build — the slot's element must be
  present at (or before) FCP, never inserted after it; keep the R1 numbers beside yours. One
  route at 390 signed-in (the sheet's identity row comes from the same store).
- **Nothing regressed downstream:** 로그아웃 from the menu lands on `/auth/login` signed out (the
  flash line is R1 F4 / `P12.F5`'s business — do not fix it here); 계정 삭제 leaves signed out;
  client-side navigation `/` → `/ask` → `/portfolio` → `/` keeps one slot rect (the R1 sub-claim)
  and still issues its per-path `GET /auth/me` (network log); a stale cookie (delete the account
  in one tab, load a page in another) renders the anonymous link, never an error.
- **Resting-layout proof:** paired screenshots of the nav at 1280, signed-out and signed-in,
  before (HEAD, `git stash` or the R1 captures) and after — `AE = 0` on the settled state; the
  frame's rect stays `[914.72, 9.5, 261.28, 32]` (P12.S1's number) for the same email length.
- **Privacy / caching check:** the email now appears in the HTML of a signed-in reader's page.
  Show the HTML response headers for a signed-in request on the local production build
  (`cache-control` must not allow shared caching), and read `deploy/` (the edge vhost + runbook)
  for any HTML caching rule at the edge; record what you find. No change expected — report it.
- `npm run build` in the copy: every route still dynamic; no new warnings.
- Hygiene: throwaway account created through the signup form and deleted through 계정 삭제;
  `NEXT_PUBLIC_VOCKY_SRC` unset; production read-only; 3014 stopped; `make stack-status` as found.
- `python3 scripts/workflow.py validate`.

## Notebook when you finish

- `## Decisions`: one line — the chrome's account state is server-seeded (files, the
  never-write-on-server rule, the boot probe skipped, later navigations unchanged), with the
  measured after-numbers (slot present at FCP on 10/10 routes, both runtimes).
- `## Doc impact`: `frontend.md` — the chrome's account slot is now server-seeded (the P4.F10
  route generalised to the layout: `readAuthState()` in `RootLayout`, `initialAccount` through
  `SiteChrome`, `useAccount`'s server snapshot), and the rule that the module store is never
  written on the server. Add `security.md` only if the caching check found something worth
  recording; otherwise one line saying the signed-in HTML carries the reader's own email under
  `cache-control` that forbids shared caching.
- `## Notes for later slices`: a `**(from P12.F1, for P12.F2)**` line only if the launcher slice
  needs something you learned (e.g. how the context is provided, so it can reuse it); a
  `**(from P12.F1, for P12.S2)**` line only if the release needs to know something (a new server
  → API request per signed-in page render is worth one line for the box's API load, if any).
  Do not touch the shared bar note.
- `## Now` (≤ 15 lines): F1 landed with the numbers; `P12.F2` next; freeze date; production on
  `a74c58a`.

`result.md`, verdict block first, with the before/after table per route.

## Do not

- touch `AccountSlot.tsx`'s rendering, `Nav.tsx`'s layout, or any CSS; add a skeleton or a
  reserved box; write the module store on the server; add a test file; commit; run any workflow
  state command; sign in or write on production.
