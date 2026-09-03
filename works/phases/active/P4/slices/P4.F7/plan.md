# P4.F7 — Cut the landing starfield's continuous main-thread cost with the same visual effect

`kind: fix`, `risk: high`, `slice-executor-high`. Cut on the operator's answer to the gate
walkthrough's item 3n, 2026-09-03, verbatim: **「find best way to reduce starfield cost. same effect
only reduce the cost.」** Read that as two hard constraints: (1) **the field looks and moves exactly
as it does today** — same 240/160 stars at the same positions, sizes and base alphas, the same
2.5–6.5 s twinkle per star with the same delays, the same 80 s drift, the same five/three shooting
stars — R2/R2.1 signed all of it and the operator chose *not* to change the design; (2) among the
ways that satisfy (1), pick the one that removes the most cost, measured, not argued. Frontend only,
**no deploy in this slice** (`P4.S10` releases it; the freeze opens 2026-09-07 11:00 KST, so this
slice should finish today).

## The cost, as measured (`P4.R1` § 7 — do not re-derive the baseline, re-measure it once as your before)

`Performance.getMetrics` deltas over a 70 s idle window on production: `/` **7,203 ms
RecalcStyleDuration / 16,584 ms TaskDuration** desktop (5,884 / 13,100 at 390 with 4× CPU), while
every Cosmos-free route is 0 ms — ≈ 24 % of a core for as long as the tab is open. R1's isolation
(CSS injected into a throwaway tab, 40 s desktop): as shipped 4,025 / 9,280; all Cosmos animations
off 592 / 3,855; **twinkle keyframes rewritten without `var()` 3,198 / 8,992**; stars hidden with
drift + shooters left running 709 / 3,685. So the floor to aim at is the "stars hidden" line, and
R1's one experiment says removing the `var()` alone is not enough — but it did not establish
**why** 240 `opacity` animations run on the main thread at all. That is the first thing to find out.

## The implementation today

`frontend/components/landing/Cosmos.tsx` (deterministic `mulberry32` field: `STARS[]` with `x, y,
size, opacity, duration, delay`; `SHOOTERS[]`; each star a `<span class=star>` with inline `left/
top/width/height/animationDuration/animationDelay` and `--star-opacity`) and
`frontend/components/landing/Cosmos.module.css` (`.field` drifts by `translate3d` over 80 s; `.star`
has `opacity: var(--star-opacity)` and `animation-name: twinkle`, whose keyframes are `opacity:
var(--star-opacity)` → `calc(var(--star-opacity) * 0.28)` with `ease-in-out`; `≤480px` hides
`.star:nth-child(n+161)` and the fourth/fifth shooter; `prefers-reduced-motion` freezes the
twinkle). The backdrop slot is `app/shell.css` `.backdrop` (`position: fixed; inset: 0; z-index:
-1`) and the file's header explains why **no ancestor may gain `transform`, `filter` or
`contain`**. The signed wording is quoted in the component's header and lives in
`docs/reference/design/rounds/02-landing-chrome/output/result.md` (item 1).

## Do

1. **Diagnose before changing anything.** In real headful Chrome over CDP (throwaway profile,
   fresh port; never the operator's profile) against the **local production build** (a copy of
   `frontend/`, `NEXT_PUBLIC_SITE_URL=https://jujutower.com npm run build`, `node
   .next/standalone/server.js` on **:3014** with `.next/static` + `public/` staged, dev API on
   8010; the operator's 3010/8010 stay up), record a short trace of the idle landing with the
   `blink.animations` + `devtools.timeline` categories (`Tracing.start` / `Tracing.end` over CDP,
   or the `--trace-startup` route — your call) and read whether the 240 twinkle animations are
   **composited or main-thread** and, if main-thread, the `compositeFailed` / unsupported-property
   reason Chrome records. The `var()` in the keyframes is the obvious suspect (a keyframe that
   resolves a custom property is not compositable), but R1's rewrite recovered only 20 %, so
   confirm the real reason — layer count, `will-change` absence, the element size, the animated
   `.field` parent, whatever the trace says — and write it down. This is the finding the fix rests on.
2. **Candidate A — make the twinkle compositor-only with identical output.** Keep the 240 DOM stars.
   Move each star's base alpha out of the animated property and into its paint — `background:
   rgba(255, 255, 255, <opacity>)` (or the same via a custom property that is **not** animated) —
   and animate `opacity` between two **constants** (`1` → `0.28`, `ease-in-out`, the star's own
   duration and delay). Alpha composes multiplicatively for one solid element over the page, so the
   painted result is the same at every instant: base × twinkle. Promote the stars deliberately
   (`will-change: opacity` on `.star`) and re-check the trace: every twinkle composited, `compositeFailed` 0.
   Keep the `≤480px` rule and the reduced-motion block working exactly as today (the frozen state is
   the base alpha — verify it still is). Nothing on any ancestor changes.
3. **Measure A** like R1: 70 s idle after load, `Performance.getMetrics` deltas (RecalcStyle,
   Layout, Script, Task) at 1280 unthrottled and at 390 with 4× CPU, three runs each, before
   (as shipped) and after; **plus** total process CPU — sample the renderer *and* GPU process with
   `ps -o %cpu` (or `top -l`) every 5 s over the same window — because a composited animation moves
   work to the compositor/GPU rather than deleting it, and "reduce the cost" means the whole
   machine's cost, not one thread's. Report all of it in one table.
4. **Candidate B — only if A leaves the total materially above the "stars hidden" floor** (say,
   more than a third of the way back up): a `<canvas>` renderer that reproduces the field
   **from the same `STARS[]` numbers** — same positions in percent of the drifting field, same
   sizes, same base alphas, the same per-star `ease-in-out` (`cubic-bezier(0.42, 0, 0.58, 1)`)
   twinkle with the same durations and delays, drawn with `requestAnimationFrame` (which stops in a
   hidden tab), DPR-aware, the 80 s drift kept as the CSS transform on the canvas element, the
   shooting stars left as they are, the mobile 160 cut kept, reduced motion drawing the frozen frame
   once. Server render must stay hydration-safe (the canvas is painted on the client; the server
   ships the element, not 240 spans — say what that does to the 44 KB of starfield markup R1 counted).
   B is allowed only if the paused-frame comparison in step 5 shows it indistinguishable; report the
   AE numbers honestly and prefer A when A already reaches the floor.
5. **Prove "same effect".** Pause every animation at fixed instants and compare frames before and
   after: `document.getAnimations().forEach(a => { a.pause(); a.currentTime = T })` for **T = 0 s,
   1.3 s, 3.7 s, 41 s** (mid-drift), at **1280 and 390**, screenshots of the full viewport, `magick
   compare -metric AE` — for A the animation graph is identical, so expect **0**; for B state the
   threshold you accept and why. Also confirm the reduced-motion rendering (emulate
   `prefers-reduced-motion: reduce`) is byte-identical to today's, and that the `≤480px` field still
   shows 160 stars and 3 shooters.
6. **Do not**: reduce the count, change any star's parameters, drop the drift, slow the twinkle,
   group stars into shared phases, add `contain`/`transform`/`filter` to an ancestor, or touch any
   other component. Any of those is a design change the operator declined.
7. **No test file** (verified live). `npm run typecheck`, `npm run smoke` (22), `npm run build` clean.
8. **`phase.md`**: `## Decisions` — the diagnosis (why the animations ran on the main thread), the
   chosen mechanism, the measured before/after (main thread and total CPU), the frame equivalence;
   `## Doc impact` — `frontend` (Cosmos: how the twinkle is composited now, the `will-change`, what a
   future edit must keep); mark the starfield `## Operator Questions` entry **ANSWERED (operator
   2026-09-03: same effect, reduce the cost) — DONE by P4.F7** with the outcome in one line; drop the
   `for the fix slices` item 4 in place; rewrite `## Now` (≤ 15 lines): F7 done and **not yet
   deployed**, `P4.S10` next (release, needs the operator's push; before 2026-09-07 11:00 KST), then
   the re-review (dispatch 3) and the gate; keep the gate line.
9. **`result.md`** verdict-block-first: the trace finding, the measurement table, the frame
   comparison, deviations.

## Hard rules

Frontend files only (`frontend/components/landing/Cosmos.tsx`, `Cosmos.module.css`; nothing else
unless the diagnosis forces it — say what); no deploy, nothing on the box, production read-only
(you may load production `/` for the before measurement); never the operator's Chrome profile; keep
3010/8010 up; stop every server/browser you start; the repo is public — no secret values; no
`git commit`/`push`; no workflow state commands other than `python3 scripts/workflow.py validate`;
`uv run` without `--with`. **RESPECT THE DESIGN** as the operator restated it: same effect.

## Validate

Trace shows the twinkle composited (or B's rAF loop) with the reason recorded; the 70 s table
(RecalcStyle/Task + process CPU) before/after at 1280 and 390; paused-frame `AE` at four instants ×
two viewports; reduced-motion and ≤480px unchanged; typecheck/smoke/build clean; `python3
scripts/workflow.py validate`; `git diff --stat` → the two Cosmos files, `phase.md`, this slice's
`result.md`.
