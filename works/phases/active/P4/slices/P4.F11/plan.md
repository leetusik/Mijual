# P4.F11 — Landing idle cost: the Hero orbiter as a composited transform, and the star twinkle without iteration events (same effect)

`kind: fix`, `risk: high`, `slice-executor-high`. Cut on the operator's answer of 2026-09-03 to the
two questions `P4.F7` filed, verbatim: **「both do as your recommendations. cost saving first.」** The
recommendations were: **yes** to re-expressing the Hero orbiter as a composited `transform`
animation; **no** to the canvas starfield (a starless first paint is not 「same effect」). "Cost
saving first" means this slice runs **before** the release: `P4.S10` (pending on the operator's
push) ships `P4.F7` and this slice together. The standing constraint from `P4.F7` is unchanged —
**the landing looks and moves exactly as it does today** — and the goal is the measured floor `P4.F7`
found: with the stars hidden *and* the orbiter's animation off the landing runs **~20
`UpdateLayoutTree` per 8 s** instead of ~480. Frontend only, no deploy here. The freeze opens
2026-09-07 11:00 KST; finish today.

## What `P4.F7` established (`slices/P4.F7/result.md` § 2–3 and § 7 — cite, do not re-derive)

- The 240 twinkles are **already composited**; the trace's single `compositeFailed` animation is
  the **Hero orbiter** (`unsupportedProperties: ["offset-distance"]`).
- The main thread produces a frame on **every display frame** for two independent reasons, and
  either alone is enough: (1) the orbiter's `offset-distance` animation is not compositable; (2) the
  240 CSS twinkles with all-distinct durations dispatch **≈61 `animationiteration` events/s** (487
  counted in 8 s), and React registers a delegated `animationiteration` listener on the root, so
  Blink must dispatch every one. Inside each such frame every running animation is re-resolved.
- Measured (8 s, 1280): as shipped ≈480 `UpdateLayoutTree`; stars hidden, orbiter running **481**;
  stars running, orbiter off **475**; **both off 20 / 3.1 ms**. That last line is the target.
- `P4.F7`'s harness (order-alternating A/B on :3014/:3015/:3016, 70 s `Performance.getMetrics`
  windows, `SystemInfo.getProcessInfo` + `ps` for renderer/GPU CPU, paused-frame `AE`, the
  `blink.animations` trace read) is cited by scratchpad path in its `result.md` § 8 — reuse it.
  This Mac's ProMotion refresh drifts (60/120/180 Hz), which is why variants must be interleaved.

## The orbiter today

`frontend/components/landing/Hero.tsx:54` — `<span className={styles.orbiter} data-motion="tick" />`
inside `.track`, a zero-size box at the centre of the two hero ellipses (`Hero.module.css` ~line
84: `left: 50%; top: 50%; width: 0; height: 0`). `.orbiter` (~line 94): a 5 px `--live` disc with
`offset-path: path("M -490 0 A 490 140 0 1 0 490 0 A 490 140 0 1 0 -490 0")`, `offset-rotate:
0deg`, `animation: orbit 26s linear infinite` over `offset-distance: 0% → 100%`. So the motion is
**constant speed along the arc length** of the 980×280 ellipse, starting at (−490, 0), in the
direction the two `A … 0 1 0 …` arcs give. R2 signed 「orbiting star on offset-path, 26s」 — the
*look* (a star riding the ring at constant speed, one lap per 26 s) is what must survive; the CSS
property is an implementation detail. The shell's `[data-motion="tick"] { animation: none }` rule
must keep freezing it under reduced motion.

## Do — part 1: the orbiter (the bigger lever)

1. Replace the motion-path animation with a **composited `transform` animation** on the same
   element: `@keyframes orbit` whose stops are `transform: translate3d(x, y, 0)` samples of the
   same ellipse, in the same direction from the same start point, placed at percentages
   **proportional to arc length** (so the star's speed stays constant along the arc, as
   `offset-distance` makes it today — do **not** use constant angular speed or a scaled rotating
   circle: both change the speed profile visibly). Choose the samples so that the **maximum
   deviation from the true ellipse is ≤ 0.25 px** everywhere — the tips of the major axis have a
   curvature radius of only ry²/rx = 40 px, so uniform sampling needs many more stops than the flat
   sides do; place them adaptively (dense at the tips, sparse on the sides) and round coordinates to
   0.1 px, so the keyframe block stays small. Report the stop count and the CSS bytes it adds to
   the landing (raw and gzip). Keep the element, its size, colour, `data-motion="tick"`, and the
   `linear` 26 s infinite timing; `translate3d`/`will-change: transform` so it composites (confirm in
   the trace: **zero** `compositeFailed` animations on the landing afterwards).
2. Generate the stops with a **recorded, deterministic script** (a small Python file under
   `frontend/scripts/`, in the register of the existing subset scripts — it is the provenance of
   numbers a reader cannot derive by eye; a comment at the top of the keyframe block names the
   script and its output size). No `Math.random`, no hand-typed coordinates.
3. Prove the motion is the same: at **≥ 12 instants** across one lap (T = 0, 2.17, 4.33, … 26 s and
   a few odd values like 1.3 s and 41 s), pause the animations (`document.getAnimations()` →
   `pause()` + `currentTime`) on the old build and the new one and read the orbiter's
   `getBoundingClientRect()` centre — the difference must be ≤ 0.25 px at every instant, at 1280
   **and** at 390 (check first whether the hero ellipses/orbiter render at 390 at all; if hidden
   there, say so). Screenshots at three of those instants: `AE` must be confined to the orbiter's
   own disc (a few anti-aliased pixels), everything else 0.

## Do — part 2: the star twinkle without the iteration events

4. The twinkle must keep painting from the **server-rendered first paint** (that is why the canvas
   was refused), keep every star's parameters, and stop dispatching `animationiteration` to
   React. Two mechanisms, test in this order and take the first that works, measured:
   - **(a) Declarative shadow DOM around the field.** If the star field's DOM sits in a shadow tree,
     CSS animation events (which are *not* composed) never reach React's root listener, and the
     browser paints the shadow tree at parse time, before any JS. Test whether this app's React
     server render can emit `<div><template shadowrootmode="open">…</template></div>` for the field
     without a hydration mismatch (e.g. via a server component that renders the template markup
     as a raw string with `dangerouslySetInnerHTML`, which React does not reconcile inside) and
     whether the twinkle/drift/≤480px/reduced-motion rules still apply — the shell's
     `[data-motion]` selectors and the module's CSS do **not** cross a shadow boundary, so the
     field's stylesheet (keyframes, the `≤480px` cut, the `prefers-reduced-motion` freeze) must
     travel inside the template as a `<style>`; `--live` and the other custom properties inherit
     through. Count `animationiteration` events at the document in the trace: must be **0**.
     Time-box the feasibility test; if React or Next cannot carry it cleanly, drop it and say why.
   - **(b) Hand the twinkle to the Web Animations API after hydration.** CSS keeps painting and
     animating from first paint exactly as `P4.F7` left it; on mount, for each star read its CSS
     animation's `currentTime` from `getAnimations()`, start an equivalent
     `element.animate([{opacity: 1}, {opacity: 0.28}, {opacity: 1}], {duration, delay, iterations:
     Infinity, easing: "ease-in-out"})` (on the pseudo-element target via `pseudoElement:
     "::before"`, or move the twinkle back onto the element for this — whichever composites and
     keeps `AE = 0`) at the **same `currentTime`**, then switch the CSS animation off (a class that
     sets `animation: none` on the pseudo-element) — phase-continuous, no visible step. WAAPI
     animations dispatch no CSS `animationiteration` events. Reduced motion: `useReducedMotion()`
     from `lib/motion.ts` → start nothing and leave the shell's freeze in force. Report the one-off
     mount cost (240 `animate()` calls) and confirm the twinkles stay composited (trace) and that
     `getAnimations()` still pauses them for the frame comparison.
   Whichever mechanism ships, the field must still show 240/160 stars at the same positions, sizes
   and alphas, the same durations/delays, the 80 s drift, and freeze correctly under reduced motion.
5. Prove it: paused-frame `AE = 0` against the `P4.F7` build at T = 0, 1.3, 3.7, 41 s × 1280/390 (as
   F7 did), reduced motion identical, ≤480px counts unchanged; and the trace shows **0
   `animationiteration` dispatches** and **0 `compositeFailed`**.

## Do — part 3: measure the whole thing

6. Three interleaved 70 s idle runs × {1280 unthrottled, 390 with 4× CPU} × {F7 build, this build}:
   `Performance.getMetrics` deltas (RecalcStyle, Layout, Script, Task), `UpdateLayoutTree` count per
   8 s from a trace, renderer + GPU process CPU sampled over the window, and the main-thread frame
   rate at idle. The number the operator asked for is **total machine cost**; report main-thread
   and total side by side, honestly, against F7's floor (20 per 8 s). If part 2 could not be made
   to work, ship part 1 alone and say what the stars still cost.
7. Also check the landing still behaves: tabs, 「15건 더 보기」, hero search, the 60 s refresh with
   `visibilitychange` — one drive-through on the build, no console errors; and `npm run
   typecheck`, `npm run smoke` (22), `npm run build` (in a **copy** of `frontend/`, never
   `frontend/.next`; serve with `node .next/standalone/server.js`; the operator's 3010/8010 stay up).
8. **No test file.** **`phase.md`**: `## Decisions` — the orbiter's new form (stop count, max
   deviation, CSS bytes), the star mechanism chosen and why the other was dropped, the measured
   before/after (main thread, frames/s, total CPU); mark the two `P4.F7` `## Operator Questions`
   **ANSWERED (operator 2026-09-03: 「both do as your recommendations. cost saving first.」) —
   orbiter DONE by P4.F11, canvas DECLINED**; `## Doc impact` — `frontend` (Hero: the orbit is a
   generated transform keyframe block, the script, the ≤ 0.25 px rule; Cosmos: how the twinkle
   avoids iteration events, what a future edit must keep; the landing's idle-cost numbers as the
   new baseline) and `qa` (a regression line: the landing's trace shows 0 `compositeFailed`, 0
   `animationiteration`, and idle `UpdateLayoutTree` ≤ ~30 per 8 s); rewrite `## Now` (≤ 15 lines):
   F7 + F11 done and **not yet deployed**, `P4.S10` next (release of both, needs the operator's push,
   before 2026-09-07 11:00 KST), then the re-review (dispatch 3) and the gate.
9. **`result.md`** verdict-block-first: the stop count/deviation table, the mechanism chosen for the
   stars with the feasibility notes on the other, the measurement table, the frame comparison,
   deviations.

## Hard rules

Frontend files only (`Hero.module.css`, `Hero.tsx` only if a wrapper is unavoidable,
`Cosmos.tsx`, `Cosmos.module.css`, a new small script under `frontend/scripts/`); **no deploy,
nothing on the box, production read-only** (loading production `/` for a comparison is fine);
never the operator's Chrome profile; keep 3010/8010 up; stop every server/browser you start; the
repo is public — no secret values; no `git commit`/`push`; no workflow state commands other than
`python3 scripts/workflow.py validate`; `uv run` without `--with`; no new dependencies. **Same
effect** is the operator's standing constraint: never change a count, a parameter, a speed profile
or what is on screen at first paint.

## Validate

Trace: 0 `compositeFailed`, 0 `animationiteration` (or the honest number if part 2 shipped
partially), `UpdateLayoutTree` per 8 s reported against 20; the 70 s table; the orbiter deviation
table (≤ 0.25 px at ≥ 12 instants, both viewports); paused-frame `AE = 0` for the stars; reduced
motion and ≤480px unchanged; typecheck/smoke/build clean; `python3 scripts/workflow.py validate`;
`git diff --stat` → the frontend files named, `phase.md`, this slice's `result.md`.

## Addendum — operator instructions received mid-slice (relayed to the executor as they arrived, 2026-09-03)

1. 「in the mobile, just remove the orbit is fine.」 → at the hero's mobile breakpoint the orbiting
   star is removed, not re-expressed.
2. 「not only the start but the orbit itself also」 → the whole orbit block (star **and** both ellipse
   rings) is removed on mobile; the hero's surrounding layout must not shift. Desktop unchanged from
   the plan above. Both lines are recorded verbatim in `phase.md` `## Decisions` by the executor.
