# P12.DECOMP — result

- **status:** done
- **summary:** Cut P12 into four middle slices as bare folders — `P12.S1` (dropdown caret fix, `fix`/high, order 1), `P12.R1` (flicker hunt, `research`/high, order 2), `P12.DECOMP2` (`decomposition`/high, order 3) and `P12.S2` (release, `implementation`/high, order 8) — and seeded every section of `phase.md` with the instrument, runtime, freeze, design and scope decisions plus per-slice notes.
- **files_changed:**
  - `works/phases/active/P12/phase.md`
  - `works/phases/active/P12/slices/P12.DECOMP/result.md`
  - `works/phases/active/P12/slices/P12.S1/slice.json` (new, bare)
  - `works/phases/active/P12/slices/P12.R1/slice.json` (new, bare)
  - `works/phases/active/P12/slices/P12.DECOMP2/slice.json` (new, bare)
  - `works/phases/active/P12/slices/P12.S2/slice.json` (new, bare)
- **validation:**
  - `python3 scripts/workflow.py validate` — PASS (`ok`, with the expected standing `oversized_doc_sections` warning and the `consolidation_owed=P4` advisory)
  - slice folders listed: `P12.DECOMP`, `P12.S1`, `P12.R1`, `P12.DECOMP2`, `P12.S2`, `P12.REVIEW`; each new folder holds only `slice.json` — PASS
  - generated `## Slices` table in `phase.md` shows all six rows in order — PASS
- **deviations:** none — the cut, the ratings, the orders and the `--depends-on` edges are exactly the four rows `plan.md` specified.
- **doc_impact:** none — this slice changed no durable truth. (The one stale fact it names, v0014's CDP prescription vs. Aside `--account u2`, is **P4's** owed note, recorded in `phase.md` § Decisions so no P12 slice writes a duplicate.)

## What I did

Read `plan.md` whole, then `intent.md` whole (the plan requires it), then the empty `phase.md`, `phase.json`, and — to check the breakdown against the code rather than against the plan's prose — `frontend/components/chrome/AccountSlot.tsx` (+ `.module.css`), the route inventory under `frontend/app/`, `frontend/lib/routes.ts`, the head of `works/phases/active/P4/slices/P4.S10/plan.md`, and `## Operator Runtime` in `docs/current/operations.md`.

Then created the four slices:

```
new-slice --phase P12 --slice P12.S1       --kind fix            --risk high --order 1
new-slice --phase P12 --slice P12.R1       --kind research       --risk high --order 2 --depends-on P12.S1
new-slice --phase P12 --slice P12.DECOMP2  --kind decomposition  --risk high --order 3 --depends-on P12.R1
new-slice --phase P12 --slice P12.S2       --kind implementation --risk high --order 8 --depends-on P12.DECOMP2
```

Bare folders only — no `plan.md` was written for any of them, no product code was touched, no state
command other than `new-slice` was run, nothing was committed.

## Why this cut, and what I verified before keeping it

The plan's four invariants (dropdown fix first as a plain `fix`, the hunt as `research`, a `DECOMP2`
after it, one release slice closing the middle) all survived contact with the code, so I made no
change to the cut. What I checked:

1. **The dropdown fix really is two files and a measurement, not a one-liner.** `AccountSlot.tsx`
   lines ~87-88 hold `const CARET_CLOSED = "▾"` / `CARET_OPEN = "▴"`, rendered at lines ~160-161
   inside `<span className={styles.caret}>`; `.caret` (`AccountSlot.module.css` 82-86) is
   `flex: none; font-size: var(--text-sm); line-height: 1`. Either candidate mechanism touches both
   the component and the stylesheet, and the fix is only *proved* by a before/after width
   measurement in a real browser in two runtimes, against an R8-signed reading. That is `high`, not
   `mid` — the recorded rating and the routing agree.
2. **The hunt genuinely cannot be pre-cut.** The user-facing route set is `/`, `/stocks`,
   `/stocks/[corp_code]`, `/portfolio`, `/portfolio/notifications`, `/ask`, `/events/[rcept_no]`,
   `/auth/login`, `/auth/reset` plus shared chrome — nine routes × two viewports × two runtimes ×
   several states each, and *which* of them flicker is unknown today. Naming fix slices now would be
   guessing, which is precisely the `research` → `DECOMP2` route the contract describes.
3. **One inventory correction worth recording:** `plan.md` and `intent.md` both list `/events` as a
   page. `find frontend/app -name page.tsx` shows **only** `frontend/app/events/[rcept_no]/page.tsx`
   — there is no `/events` index route. This is not a change to the cut (it is one route fewer inside
   `P12.R1`'s own scope), so I did not alter the slice table; I put the fact in `P12.R1`'s note
   instead, with the instruction to say so rather than skip silently if a live `rcept_no` cannot be
   reached. The two dynamic routes also need real ids pulled from the running dev API — `/stocks`
   resolves a query and `redirect(stockPath(result.stock.corp_code))`s onto the handle
   (`frontend/app/stocks/page.tsx` line 77).
4. **The chrome's breakpoints are `@media (max-width: 480px)`** in `Nav.module.css`,
   `Footer.module.css` and `Feedback.module.css` (plus P4.F11's ≤767px landing rule), so the hunt's
   resize sweep has concrete numbers to cross rather than "mobile".
5. **`## Operator Runtime` exists and is filled** (operations.md v0014, § *Operator Runtime* at line
   285 + § *Production* at 307) — no `needs_operator` halt for a missing manifest anywhere in this
   phase. Its one stale point (Aside's daemon / CDP prescription) is carried in `## Decisions` with
   the fallback rule and the "name what you used" obligation, and attributed to P4's owed note so
   P12 does not double-write it.

## `phase.md` — what I seeded

Every section the plan listed, around the untouched generated `## Slices` block:

- **`## Decisions`** — 12 lines: the shape of the phase and why `P12.S1` runs before the hunt;
  instrument (Aside `--account u2`, never `u0`, never `aside profile list`); v0014's one stale point
  + the CDP fallback rule; dev and production runtimes; the local production build recipe; the three
  viewport configurations; the deploy freeze; the R8 constraint on the dropdown; the P4.F7/F11
  landing constraint; `/ops/*` out of scope + production read-only; no test files; no design
  round / no OG work.
- **`## Notes for later slices`** — 10 notes, each tagged `**(from P12.DECOMP, for <slice>)**`:
  four for `P12.S1` (caret location + measured numbers cited from `intent.md`, the two candidate
  mechanisms and what must be proven, the untouched mobile sheet, account hygiene), four for
  `P12.R1` (page inventory with the dynamic-segment problem, the states to watch, what a finding must
  record, the landing constraint), one for `P12.DECOMP2` (one slice per independent cause, the risk
  rule, orders `3.x`, "a finding that changes nothing needs no slice"), one for `P12.S2` (the P4.S10
  precedent by path, the freeze, the four R7 assertions, the `pending`-for-push rule).
- **`## Doc impact`** and **`## Operator Questions`** — left as their template lines. Nothing durable
  changed here, and nothing in the decomposition needs an operator decision.
- **`## Now`** — 6 lines: the cut, `P12.S1` next with the two things it must know, the instrument and
  hygiene constraint, that no operator question is open, the freeze, and that the gate declaration
  (`accept-gate P12 --require`) is the orchestrator's next action.

Notebook size after the edit: 13,359 bytes — far under the ~400 KB budget.

## Consumed notes

None — `phase.md` was the empty template; this slice seeded it.
