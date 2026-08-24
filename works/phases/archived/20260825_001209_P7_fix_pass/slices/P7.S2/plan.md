# Plan — P7.S2: login reachable — the chrome account slot answers in dev

## Why

Operator item 5: "login should be exists … not even seen in the web". `P7.DECOMP` (phase.md →
"RC-B") found the seat: `frontend/components/chrome/useAccount.ts:74-84`. The probe effect guards
on a **module-level** `probedPath` and discards its result under a per-effect-run `live` flag.
Under React StrictMode (`next dev` — `reactStrictMode` is on by default for the App Router) the
effect runs twice: run 1 sets `probedPath`, starts `fetchAuthState()`, then its cleanup sets
`live = false`; run 2 returns immediately because `probedPath === pathname`. The only answer on the
wire is thrown away, the store stays `null` ("not answered yet"), and `AccountSlot` renders an
empty `<div>` on desktop / `null` in the mobile sheet — so the chrome never shows 로그인 (nor the
account menu for a logged-in reader) in dev. In `next start` the effect runs once and it works,
which is why P5.S19 passed. `P7.S1` has now made `127.0.0.1` / Tailscale hydrate, so the bug is
reproducible in the operator's own browser.

## The fix (one file, small, but reason it through)

`useAccount.ts`: the store is module-level and outlives every component, so there is **no
unmount hazard** that `live` would protect against — publishing a probe result into the shared
store after a subscriber unmounts is correct (the next subscriber wants it). Remove the `live`
flag and keep the `probedPath === pathname` check at resolve time (it still protects against a
stale answer landing after a client-side navigation changed the path). Something like:

```ts
useEffect(() => {
  if (probedPath === pathname) return;
  probedPath = pathname;
  void fetchAuthState().then((next) => {
    if (probedPath === pathname) setAccountState(next);
  });
}, [pathname]);
```

Consider the edge the comment block documents — a session can begin on `/auth/login` and end
anywhere; 로그인/로그아웃/계정 삭제 publish via `setAccountState` — and make sure nothing there
regresses. Update the doc comment to explain the StrictMode reasoning in one short paragraph
(why `live` is wrong for a module store; cite `P7.S2`). **Do not touch
`components/auth/useAuthState.ts`** — its guard is component state and self-heals (DECOMP note).
Do not restyle the slot; do not change `AccountSlot.tsx` unless the probe fix alone demonstrably
cannot make it render (then explain exactly why in result.md).

## Verify — in the operator's runtime

The dev stack is up (`make stack-status`; web on `next dev -H 0.0.0.0`, S1's origin seam live).
`next dev` picks up the component edit via Fast Refresh; confirm in `var/stack/web.log` that it
recompiled, or do a hard reload. Headless Chrome over CDP (same approach as `P7.S1`/DECOMP
`result.md`), **fresh profile each run, on `http://127.0.0.1:3000`** (and the Tailscale URL once):

1. **Clear `mijual.portfolio.sample` first** — a loaded 샘플 makes the slot show 샘플 / 샘플 종료
   instead of 로그인 by R5-4's signed rule (P7.S1 note).
2. `/` at 1440: the desktop nav account slot renders a **로그인** entry (count `a[href="/auth/login"]`
   or the slot's text) — expected **≥1**, was 0. Also at 390 wide: open the mobile sheet and
   confirm its account row shows 로그인.
3. Exactly **one** `GET /api/auth/me` per page load (StrictMode must not double-fetch through
   the shared in-flight request — count network requests).
4. Full round trip: create a throwaway account through the product's own 계정 만들기 flow (or
   log in with one you create via the API), confirm the slot switches to the 축약 이메일 account
   menu without a reload, navigate client-side to another page (slot still correct), 로그아웃 from
   the menu → slot shows 로그인 again, then **delete the account** (계정 삭제 in the product, or
   the API) so no test data is left behind. Note what email you used and that it is gone.
5. Production build still fine: `npm run build && npm run start -p 3100` (never touch the dev
   server's `.next` — stop web first and restart with `make web-up` after, or read phase.md
   Constraints on the EADDRINUSE trap), check 로그인 renders on `127.0.0.1:3100`, then kill it.
   Leave the dev stack (postgres + api + web) running; `make stack-status` at the end.
6. `cd frontend && npm run typecheck && npm run smoke`; `python3 scripts/workflow.py validate`.

## Record

`result.md` (commands + outcomes, the before/after counts, deviations). Append a short Findings
note to `phase.md` (item 5 closed; anything the later slices should know). Doc impact: if
`docs/current/frontend.md` describes the account probe ("asked once per path" / `useAccount`)
in a way that is now wrong, add a one-line `frontend` Doc impact entry; otherwise none. No
`doc-new-version`, no commits, no state transitions.

## Out of scope

Everything else in P7. No nav changes (S6), no copy changes (S7), no focus work (S5).
