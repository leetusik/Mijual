# P4.F10 — Event page: render 「이 마감 알림 받기 →」 from the request's own session, not after `GET /auth/me`

`kind: fix`, `risk: high`, `slice-executor-high`. Cut from `P4.F5`'s finding (the one route left above
the CLS target after the font fix). Operator instruction behind it (2026-09-02, verbatim): 「you look
up the cloudflare's poor LCP, INP, and CLS performance stuffs … and create slices for fix them.」
Frontend only, **no deploy in this slice** (`P4.S9` releases the batch). **RESPECT THE DESIGN**: the
line, its two labels, its placement and its gate are R5-2/R10 material and do not change — only
*when* the correct state is known moves, from a client probe to the server render.

## The defect (measured by `P4.F5`; `slices/P4.F5/result.md` has the runs — do not re-derive)

`/events/{rcept_no}` shifts once (**CLS 0.0325** at 390 mobile, ~2.4 s; 0.0089 desktop, ~0.1 s)
when `GET /auth/me` resolves in the browser and `DeadlineOffer` (`frontend/components/auth/
DeadlineOffer.tsx`) goes from `null` to a rendered link — `a.offer`, **44 px** at ≤ 767 px /
**32 px** desktop (`Event.module.css`) — inserted above the fold, pushing `qstrip`, `offering` and the
일정 section down. Blocking either webfont does not remove it. The component's own doc-comment says
why it renders nothing until the session is known: showing the anonymous label first would tell a
logged-in reader for a moment that they have no account. That reading stays true; the fix is to
**know the session before the first paint**, on the server.

## What exists to build on

- `frontend/lib/session.server.ts` → `readAuthState()`: the server half, forwards the request's
  `cookie` to `GET /auth/me`, never throws (service down → anonymous), and is exactly what
  `frontend/app/auth/login/page.tsx:42` already does. Reading cookies opts the route into
  request-time rendering, which `frontend/app/events/[rcept_no]/page.tsx` already is
  (`await connection()`).
- `frontend/components/auth/useAuthState.ts` → `useAuthState(enabled = true)`: the client probe,
  already gated by an `enabled` flag.
- The mount: `EventPage` → `<EventDetail detail>` → `<EventHeader detail>` → `<DeadlineOffer corpCode
  className>` behind the deadline gate (`Header.tsx` ~line 145).

## Do

1. **Resolve the session on the server, once per event-page request**, in
   `frontend/app/events/[rcept_no]/page.tsx`: `const auth = await readAuthState()` beside
   `getEvent()` (run them in parallel with `Promise.all` so the round trip is not added serially;
   keep the 404 handling exactly as it is). If no session cookie is present at all, you may
   short-circuit to anonymous without calling the API — say whether you did, and keep the same
   never-throws contract.
2. **Thread only what the line needs.** Pass `authenticated: boolean` (never the `Account` object —
   the reader's account must not be serialised into the page HTML) down `EventDetail` →
   `EventHeader` → `DeadlineOffer` as an optional `initialAuthenticated?: boolean`. In
   `DeadlineOffer`, when it is defined, render that state immediately and **skip the probe**
   (`useAuthState(initialAuthenticated === undefined)`); when undefined (any other host surface),
   behave exactly as today. Update the component's doc-comment: the "nothing renders until the
   session is known" reading is honoured *by the server* on the event page.
3. **Leave the gate and the markup alone**: the deadline-ahead condition in `Header.tsx`, the two
   labels, `ROUTES.login` / `portfolioAddPath`, `.offer`'s geometry — untouched. The anonymous
   variant must now be in the **server-rendered HTML** (verify with `curl -s -H 'Accept: text/html'
   http://127.0.0.1:3014/events/<rcept_no> | grep -c '이 마감 알림 받기'` → 1 on an event whose
   deadline is ahead, 0 on one that is past or 추후결정) and the logged-in variant must render
   server-side for a request carrying a valid `mj_session` cookie — prove that on the **local**
   build against the dev API with a dev account (create nothing on production; if no dev account
   exists, say so and prove the anonymous half only, with the code path read for the other).
4. **Measure** on the local production build (a copy of `frontend/`, `npm run build`, `node
   .next/standalone/server.js` on **:3014**, `.next/static` + `public/` staged, dev API on 8010; the
   operator's 3010/8010 stay up) in real headful Chrome over CDP (throwaway profile, fresh port,
   never the operator's profile): cold-cache mobile (R1's profile: 412×915 @ 2.625, 4× CPU, ≈1.6 Mbps /
   150 ms) and desktop, three loads each, on a live event page with a deadline ahead: CLS before
   (expect ~0.0325) and after (target **≤ 0.01**; the remaining ~0.0016 Plex Mono race is known and
   not yours), and confirm **no `GET /auth/me` request** leaves the browser on that page any more.
   Also confirm no shift appears on `/stocks/{corp_code}` or `/portfolio?sample=1` (the other hosts
   of the line, if any — grep `DeadlineOffer` first) — their behaviour is unchanged by design.
5. **Screenshot equivalence** after settle: 390 and 1280, before/after, `AE = 0` with the same data.
6. **No test file** (verified live; the typecheck is the contract). `npm run typecheck`, `npm run
   smoke` (22), `npm run build` clean.
7. **`phase.md`**: `## Decisions` — one line (the event page resolves the session server-side and
   passes a boolean; why not the account object; the measured CLS); `## Doc impact` — `frontend`
   (Event page: request-time session read, `DeadlineOffer`'s `initialAuthenticated`, the probe skipped
   there) and `security` if the boolean-only rule deserves a line (the account never enters the
   HTML); mark the `(from P4.F5 …)` candidate-`P4.F10` note consumed; rewrite `## Now` (≤ 15 lines):
   F5 + F6 + F8 + F10 done and **not yet deployed**, `P4.S9` next (needs the operator's push), then
   the re-review; keep the freeze and gate-shut lines.
8. **`result.md`** verdict-block-first: the before/after CLS table, the SSR proof (`grep -c`), the
   no-probe proof, the equivalence result, deviations.

## Hard rules

Frontend files only (`app/events/[rcept_no]/page.tsx`, `components/event/EventDetail.tsx`,
`components/event/Header.tsx`, `components/auth/DeadlineOffer.tsx`, and nothing else unless the
threading forces it — say what); no deploy, nothing on the box, production read-only, **no account
creation and no login on production**; never the operator's Chrome profile; keep 3010/8010 up; stop
every server/browser you start; the repo is public — no secret values; no `git commit`/`push`; no
workflow state commands other than `python3 scripts/workflow.py validate`; `uv run` without
`--with`.

## Validate

Typecheck/smoke/build clean; the SSR `grep -c` proofs; the CLS table (≤ 0.01 after, medians of 3);
no `/auth/me` request on the event page; `AE = 0` screenshots; `python3 scripts/workflow.py
validate` passes; `git diff --stat` → the files named, `phase.md`, this slice's `result.md`.

## Addendum (orchestrator, 2026-09-03, at dispatch)

`P4.F5` (`70daeaf`), `P4.F6` (`a8d327b`) and `P4.F8` (`fd21529`) are in the tree; none touches this
slice's files. Build in a **copy** of `frontend/` and serve it with `node .next/standalone/server.js`
on :3014 (`.next/static` + `public/` staged in) as the three did; nothing goes into `frontend/.next`.
Typecheck/lint equivalents: `npm run typecheck`, `npm run smoke` (22). F5's harness for cold-cache
mobile loads is cited by scratchpad path in `slices/P4.F5/result.md`; F5 measured this route at
**0.0325** before and after its own fix, at ~2.4 s mobile / ~0.1 s desktop — that is your baseline.
After you, `P4.S9` deploys the four slices together; `## Now` should say so.
