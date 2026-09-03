# P12.DECOMP — decompose "Flicker polish"

`kind: decomposition`, `risk: high` → `slice-executor-high` (by kind). Bare folders only, never a
`plan.md` for another slice, no product code. Written 2026-09-03 22:xx KST by the orchestrator in
`auto` mode.

## Context

P12 is `planned` and undecomposed: only `P12.DECOMP` and `P12.REVIEW` exist and `phase.md` is the
empty template. The operator's intent is confirmed and recorded in
`works/phases/active/P12/intent.md` — read it whole before cutting anything; it carries the
measured numbers, the dropped OG item, and the clarifications. In one line each:

1. **The signed-in account dropdown jumps in width on toggle.** `AccountSlotDesktop`
   (`frontend/components/chrome/AccountSlot.tsx`, styles in `AccountSlot.module.css`) swaps
   `▾` (closed) for `▴` (open) in a `flex: none` span; in `notoSansKr` at 12px the glyphs advance
   5.67px vs 11.05px, so the frame goes **239.67px → 245.05px (+5.38px)**, right edge anchored,
   the whole control's left edge sliding on every toggle. Height stays 32px. Nothing else in the
   frame changes. The fix must keep the R8-signed reading (hairline frame + ▾/▴ caret + hover) and
   only stop the jump — no restyle. The operator said "skip the design round, fix it directly in
   the phase": an ordinary `fix` slice, no `co-work`, no handoff, no mockup gate.
2. **Hunt for every other visible flicker and fix what is found**, across every user-facing page —
   landing `/`, `/stocks` and `/stocks/[corp_code]`, `/portfolio` and `/portfolio/notifications`,
   `/ask`, `/events` and `/events/[rcept_no]`, `/auth/login` and `/auth/reset`, and the shared
   chrome (nav, account slot, footer, launcher) — desktop **and** mobile, in the dev runtime **and**
   the production build. "Flicker" = anything that visibly jumps, resizes, re-paints or pops in
   after first paint: layout shift on load or state change, hover/open states that move their
   neighbours, content rendered twice, icons or fonts swapping after paint. Watched over time in a
   real browser, not one static pass. `/ops/*` is operator-facing, not user-facing: **out of scope**.

Nothing about the OG image, KakaoTalk, or a design round is in this phase (intent.md, "Dropped").

## Facts the breakdown rests on (verified by the orchestrator, 2026-09-03)

- **Instrument: Aside, agent account `u2` (profile 「claude2」), `aside repl --account u2 "<js>"`.**
  `aside account list` on this Mac shows `u0` (the operator's Google account — never driven),
  `u1`, `u2`. **The `## Operator Runtime` manifest in `docs/current/operations.md` (v0014) is stale
  on this one point**: it still says "Aside's daemon does not run on this Mac and there is no agent
  Aside account" and prescribes headful Chrome over CDP. That stopped being true on 2026-09-03
  evening (operator, verbatim in `works/phases/active/P4/phase.md` line ~622: 「yo use claude 2 in
  aside browser for qa and stuff … I meant claude2 profile」); P4 already owes the Doc impact note
  that corrects v0014. Chrome-over-CDP on a throwaway profile remains the fallback **only** if Aside
  is genuinely unavailable in a slice, and the slice must say which it used. The invocation, the
  two-line re-attach preamble (`listBrowserTabs()` → `attachBrowserTab()`) and the surface's sharp
  edges are in `.claude/skills/design-cowork/SKILL.md` from line ~425. Do not run
  `aside profile list` (not a command; it hangs the shell).
- **Runtime and access path — everything else in that manifest stands:** dev is `make stack-up` →
  `http://127.0.0.1:3010` (`next dev`, StrictMode), logs `var/stack/{api,web}.log`; production is
  `https://jujutower.com` (Cloudflare → `edge-nginx` → `mijual-web`, a standalone production Next
  build); a **local production build** for anything attributed without the edge is a copy of
  `frontend/` built with `NEXT_PUBLIC_SITE_URL=https://jujutower.com` and served with
  `node .next/standalone/server.js` on a spare port such as 3014 (never build into the working
  tree's `.next`; Next 16 refuses `next start` under `output: "standalone"`). Viewports: **1280**
  desktop and **390** mobile, plus **412×915 @ DPR 2.625, 4× CPU, ≈1.6 Mbps / 150 ms** for
  cold-cache work — the only way a font swap or a cold-cache layout shift is observable at all.
- **Deploy freeze: 2026-09-07 11:00 → 2026-09-11 23:59 KST** (`deploy/runbook.md` line 32). Today
  is 2026-09-03 (Thu, evening). Production serves `a74c58a` (P4.S10, released 19:47 KST today).
  Nothing from P12 may deploy inside the freeze; a release that misses 09-07 11:00 waits for
  09-12 and says so. The frontend-only deploy precedent is `works/phases/active/P4/slices/P4.S10/`
  (`plan.md` for the launch line and preconditions, `result.md` for what "verified on production"
  looked like); it stopped `pending` for the operator's push of `main` before dispatch.
- **Landing constraint (RESPECT THE DESIGN, and do not double-fix):** `P4.F7` and `P4.F11` just
  re-expressed the landing's starfield twinkle and Hero orbiter for idle cost, with the star field
  proven byte-identical (`AE = 0`). Any P12 slice that touches `frontend/components/landing/`
  reads `works/phases/active/P4/slices/P4.F7/result.md` and `P4.F11/result.md` first and inherits
  their constraint: the landing looks and moves exactly as it does today.
- **Signed-in state for the dropdown needs an account.** Hygiene rule (`docs/current/qa.md`
  § *Real-browser verification*, "Hygiene rule for a browser pass"): create test accounts through the
  product, delete them through the product's own 계정 삭제 before the slice ends, never open the
  operator's `.env`, leave `NEXT_PUBLIC_VOCKY_SRC` unset, leave the dev stack as found
  (`make stack-status`). Production is **read-only** for every P12 slice — no signup, no writes there.
- **Tests:** the repo's rule is tests only for core behaviour. Nothing in P12 earns a test file;
  every check is live (`npm run typecheck`, `npm run smoke`, a production build in a copy, the
  real-browser pass). No slice adds a test.

## Slice cut to create

The hunt is the reason this phase cannot be cut past one point: what flickers is unknown until a
real browser has watched every page, so the fix slices after it cannot be named now. That is the
`research` → `DECOMP2` route, exactly as the contract describes it. The dropdown fix is certain
and already measured, so it goes first and lands as its own commit before the hunt runs (the hunt
then sees the fixed nav and does not re-report it).

| Slice | Name | Kind | Risk | Order | Why this rating |
|---|---|---|---|---|---|
| `P12.S1` | Account dropdown: one caret box in both states — stop the +5.38px width jump, keep the R8 ▾/▴ reading | `fix` | `high` | 1 | Two files (`AccountSlot.tsx` + `.module.css`), a real-browser measurement before/after in Aside, a signed design to respect — not a `mid`-tier edit |
| `P12.R1` | Research: flicker hunt — every user-facing page, 1280 + 390, dev + local production build, watched over time; findings ranked and located in `phase.md` | `research` | `high` | 2 | By kind; its findings decide the rest of the phase |
| `P12.DECOMP2` | Second decomposition: cut the fix slices from `P12.R1`'s findings | `decomposition` | `high` | 3 | By kind; never pre-planned — its plan depends on findings nobody has yet |
| `P12.S2` | Release P12 to production — frontend-only deploy before the 2026-09-07 11:00 KST freeze (or after 09-11 23:59, with the operator's say-so) | `implementation` | `high` | 8 | ssh deploy on the Oracle box, no-harm assertions, production verification through Cloudflare |

`P12.DECOMP2` inserts the fix slices at fractional orders between 3 and 8 (`3.1`, `3.2`, …) so
the release stays last before `P12.REVIEW` (order 9999). Use `--depends-on` where it documents a
real dependency (`P12.DECOMP2` on `P12.R1`; `P12.S2` on `P12.DECOMP2`); it is advisory. If, on
reading the code and the intent, you judge a different cut is right — e.g. a second research pass
is obviously needed, or the release should be split — make the change and record why in
`phase.md`'s `## Decisions`; but keep the four invariants: the dropdown fix is a plain `fix` slice
first, the hunt is a `research` slice, a `DECOMP2` follows it, and one release slice closes the
middle before the review. Never cut a `co-work` slice: the operator declined a design round.

Commands (the only workflow commands you may run):

```
python3 scripts/workflow.py new-slice --phase P12 --slice P12.S1 --name "…" --kind fix --risk high --order 1
python3 scripts/workflow.py new-slice --phase P12 --slice P12.R1 --name "…" --kind research --risk high --order 2 --depends-on P12.S1
python3 scripts/workflow.py new-slice --phase P12 --slice P12.DECOMP2 --name "…" --kind decomposition --risk high --order 3 --depends-on P12.R1
python3 scripts/workflow.py new-slice --phase P12 --slice P12.S2 --name "…" --kind implementation --risk high --order 8 --depends-on P12.DECOMP2
```

## What `phase.md` must carry when you are done

Seed every section of the empty notebook — this is the file every later P12 dispatch reads first,
and its executors' contexts die with their slices. Never touch the generated `## Slices` block.

- **`## Decisions`** — one line each, replaceable later:
  - instrument = Aside `--account u2` (claude2); v0014's CDP prescription is stale and P4 owes the
    correcting Doc impact note; CDP is the fallback only, and a slice names what it used;
  - runtime + viewports + the local production build recipe (as above);
  - the freeze rule for the release and the 09-12 fallback;
  - the dropdown fix respects R8 (frame + caret + hover unchanged in reading; only the jump goes);
  - the landing inherits P4.F7/F11's byte-identical constraint;
  - `/ops/*` out of scope; production read-only for P12;
  - no test files in this phase (live verification only).
- **`## Notes for later slices`**, each tagged `**(from P12.DECOMP, for <slice>)**`:
  - for `P12.S1`: where the caret lives and the measured numbers (from intent.md § Notes — cite,
    do not re-measure), the two candidate mechanisms (one glyph flipped by a layout-neutral
    `transform`, or a fixed-width centred caret box — the slice picks and verifies the frame is
    pixel-equal in width across the toggle at 1280 in dev **and** in the local production build),
    the account-hygiene rule, and that the mobile sheet has no caret and is untouched;
  - for `P12.R1`: the page list above with each route's dynamic segments needing a real id (a
    `corp_code`, a `rcept_no` — read `frontend/app/**/page.tsx` to see how each page gets its
    data), the states to watch per page (first paint → hydration, signed-out and signed-in, hover /
    open / focus on every control, a cold-cache throttled mobile load per route for font swap and
    CLS, a timed idle window on the pages that animate, resize across the ≤480 / ≤767 breakpoints
    the chrome uses), what a finding must record (route, viewport, runtime, the element, what moved
    and by how many px or which paint, a reproduction, and a proposed fix + risk so `DECOMP2` can
    cut from it), and the landing constraint;
  - for `P12.DECOMP2`: cut one fix slice per independent flicker cause (a shared root cause is one
    slice), `risk: low` only for a genuinely one-line/few-line single-file edit, orders `3.x`, and
    a `P12.R1` finding that changes nothing needs no slice;
  - for `P12.S2`: the P4.S10 precedent by path, the freeze, the four R7 no-harm assertions, and that
    it stops `pending` for the operator's push of `main` if `origin/main` is behind.
- **`## Operator Questions`** — append only what genuinely needs the operator; I expect none here.
- **`## Doc impact`** — nothing durable changes in this slice; leave it as the template line, or
  add nothing.
- **`## Now`** (≤ 15 lines, last): decomposition done, `P12.S1` next and what it must know in two
  lines, the freeze date, and that the gate is declared `--require` by the orchestrator.

## Do not

- write or edit any product code, any `plan.md`, or anything under `docs/`;
- run `accept-gate` (the orchestrator declares `accept-gate P12 --require` right after
  `finish-slice`), `start-slice`, `finish-slice`, `set-*-status`, or commit;
- cut a `co-work` slice or anything OG/Kakao-related;
- read P4's whole notebook — only the lines cited above, and the two result heads if you need them.

## Validation

- `python3 scripts/workflow.py validate` — passes (the standing `oversized_doc_sections` warning
  and the `consolidation_owed=P4` advisory are expected and not yours).
- `python3 scripts/workflow.py next` shows `current_slice=P12.S1` after this slice is finished
  (the orchestrator checks this).
- `works/phases/active/P12/slices/` holds `P12.DECOMP`, `P12.S1`, `P12.R1`, `P12.DECOMP2`, `P12.S2`,
  `P12.REVIEW`, each new folder holding only `slice.json`.

## Return

The structured verdict, `result.md` first with the same block at its head, `summary` worth quoting
as this slice's outcome line.
