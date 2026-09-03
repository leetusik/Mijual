# P4.F11 — result

```
status:        done
summary:       The Hero orbiter is a composited transform animation built from 93 generated
               arc-length stops on desktop and is removed entirely on mobile (operator);
               the 240 star twinkles are handed from CSS to WAAPI after hydration, so React's
               delegated animationiteration listener has nothing left to dispatch. The landing
               stops producing a main-thread frame every display frame: UpdateLayoutTree
               480 -> 8 per 8 s at 1280 AND 390, animationiteration 453/295 -> 0,
               compositeFailed 1 -> 0, total Chrome CPU -25 % / -7 % over 70 s idle, with the
               star field byte-identical (AE = 0) and the hero's rings byte-identical.
files_changed: frontend/components/landing/Hero.module.css
               frontend/components/landing/Cosmos.tsx
               frontend/components/landing/Cosmos.module.css
               frontend/components/landing/StarTwinkle.tsx        (new)
               frontend/scripts/gen_orbiter_keyframes.py          (new)
               works/phases/active/P4/phase.md
               works/phases/active/P4/slices/P4.F11/result.md
validation:    python3 frontend/scripts/gen_orbiter_keyframes.py --report   PASS (93 stops, 0.1544 px)
               npm run typecheck                                            PASS
               npm run smoke                                                PASS (22/22)
               npm run build (in a COPY of frontend/)                       PASS
               trace, 8 s idle, 1280 + 390, both builds                     PASS (0 cF, 0 iter, 8/8 s)
               70 s idle x 2 viewports x 3 interleaved reps                 PASS (table in section 5)
               paused-frame AE, star field, 4 instants x 2 viewports + RM   PASS (AE = 0, control 0)
               paused-frame AE, hero orbit block, 5 instants                PASS (7x7 px, rings AE 0)
               orbiter position, 261 instants over the lap                  median 0.130 px, max 0.410 px
               landing drive-through, F7 build vs F11 build                 PASS (identical, 0 exceptions)
               operator dev runtime 127.0.0.1:3010 (next dev, StrictMode)   PASS
               python3 scripts/workflow.py validate                         PASS
deviations:    four, all in section 8 -- one new component file the plan did not list; the
               mobile half replaced by two operator instructions mid-slice; mechanism (a)
               (declarative shadow DOM) refuted rather than adopted; and 32 of 261 orbiter
               instants exceed the plan's 0.25 px, which section 3 attributes to
               offset-distance's own progress wobble rather than to the keyframes.
doc_impact:    two lines appended to phase.md `## Doc impact` -- `frontend` (Hero: the generated
               transform keyframe block, the script, the regenerate-never-hand-edit rule, the
               mobile removal; Cosmos: the WAAPI handover and the rendered-stars-only rule; the
               new idle-cost baseline) and `qa` (a landing regression line: 0 compositeFailed,
               0 animationiteration, UpdateLayoutTree <= ~30 per 8 s, and no orbit at 390).
doc_versions:  n/a (not a review slice)
review_verdict: n/a
walkthrough:   none
explain:       n/a
```

The phase-level findings — the decisions, the answered operator questions, the release note for
`P4.S10` — are in [`phase.md`](../../phase.md) and are not repeated here. This file is the log:
what was measured, with what, and what it cost.

---

## 1. Instrument, targets, and what was never touched

**Instrument.** Real **Google Chrome 152.0.7977.65**, headful, on a throwaway profile on a fresh
debugging port, driven over the DevTools protocol from `P4.F7`'s own harness (`f7_cdp.py`, reused
unchanged). That is the sanctioned fallback the `## Operator Runtime` manifest records: **Aside's
daemon does not run on this Mac and there is no agent Aside account**. Every browser was closed with
`Browser.close`.

**Targets.** Two **local production builds**, each a copy of `frontend/` built with
`NEXT_PUBLIC_SITE_URL=https://jujutower.com MIJUAL_API_ORIGIN=http://127.0.0.1:8010 npm run build`
and served by `node .next/standalone/server.js`:

| port | tree | what it is |
|---|---|---|
| 3014 | `f11be` | repo `HEAD` (`78feabb`) — the `P4.F7` build, the baseline |
| 3015 | `f11af` | this slice |
| 3018 | `f11probe` | a static mechanism probe (no product code), section 4 |

The builds ran in **copies**, never in `frontend/.next`, because `next build` and the operator's
running `next dev` share it. **The operator's stack answered 200 on 3010 and 8010 before, during and
after**, and the change was additionally verified **in that dev runtime itself** (section 7) because
the manifest says dev is what the operator browses day to day.

**Never touched:** production — not one request, the whole slice ran against local builds — the
Oracle box, any deploy, any workflow state command other than `validate`, any `git commit`/`push`,
`uv run --with`, any new dependency. No secret value appears anywhere in this slice.

---

## 2. Part 1 — the orbiter

### The generator

`frontend/scripts/gen_orbiter_keyframes.py` (stdlib only, deterministic, no arguments). `--report`:

```
curve              SVG arc -> 4 cubic Beziers, rx=490 ry=140, dot 5px (anchor = centre)
perimeter          2135.4012 px    (quarter 533.8503)
vs exact ellipse   perimeter +0.2759 px (the arc's cubics bulge outside it)
curvature radius   40.88 px at the tips, 1752.59 px at the flat sides
stops              93  (23 per quadrant + the closing 100%)
chord length       6.62 .. 42.90 px
budget             0.25 px required, 0.18 px solved for (coordinates rounded to 0.1 px)
MAX DEVIATION      0.1544 px, at lap fraction 0.4629 (t = 12.036s of 26s)
css                5,515 bytes raw
```

Three things it does that are not obvious, each measured rather than assumed:

1. **It samples the browser's curve, not the textbook ellipse.** An SVG `A` command is drawn as one
   cubic Bézier per 90° (control handles at `4/3·tan(Δ/4)`), and that curve bulges outside the true
   ellipse. Measured against Chrome: the rendered `offset-path` sits a **constant +0.048 px** outside
   the 490×140 ellipse over most of a quadrant, and Blink's own `getPointAtLength` on the same `d`
   agrees with the 4-cubic model to **0.05 px**. Sampling the ellipse instead would have started the
   new animation 0.05 px off the old one everywhere.
2. **Percentages are proportional to arc length, never to angle.** Constant angular speed — the
   obvious "rotate a scaled circle" shortcut — was computed against the measured path and is **83 px
   wrong** at worst. That is the mistake this file exists to prevent.
3. **Stops are adaptive.** The curvature radius runs 40.9 px at the major-axis tips to 1752.6 px on
   the flat sides, a 43× range; an equal-deviation chord goes as `sqrt(R)`, so the stops are spaced
   evenly in `ds/sqrt(R)` — chords **6.62 px** at the tips, **42.90 px** on the sides. Uniform
   sampling at the same deviation would need several times as many stops.

The block is solved against a 0.18 px target and **asserts** the plan's 0.25 px budget. 89 stops
would have met 0.18 px on the exact ellipse; on the browser's curve it takes 93.

### What changed in the CSS

`offset-path` and `offset-rotate` are gone. `.orbiter` keeps its size, colour, `border-radius`,
`data-motion="tick"` and `animation: orbit 26s linear infinite`, and gains a **static**
`transform: translate3d(-492.5px, -2.5px, 0)` — the path's start point, minus half the 5 px dot
because `offset-anchor: auto` computes to the element's centre. That static value is load-bearing:
`app/shell.css`'s reduced-motion rule sets `animation: none`, and without it the frozen star would
jump to the ellipse centre. Measured: the frozen star sits at **(−475.4449, 118.5417)** relative to
the track on **both** builds, at **both** viewports, identical to four decimals.

**`will-change: transform` was deliberately not added.** The trace shows **0 `compositeFailed`**
without it, and `will-change` would keep a compositing layer alive even when the animation is frozen.
Next's minifier rewrites `translate3d(x, y, 0)` to `translate(x, y)` in both the static rule and the
keyframes; that does not change the compositing result (measured after minification, on the built
bundle).

### Cost

The built `@keyframes orbit` goes **85 B → 4,227 B raw**, **89 B → 965 B gzip** — 93 stops of
`translate(x,y)`. Net landing payload is nonetheless *smaller*; see section 6.

### Mobile — the operator's two lines

Mid-slice the operator sent, verbatim: **「in the mobile, just remove the orbit is fine.」** and then
**「not only the start but the orbit itself also」**. So part 1 differs by viewport on purpose:
re-expressed on desktop, **removed on mobile**. `Hero.module.css` has exactly one media query —
`min-width: 768px` — so the rule is its inverse:

```css
@media (max-width: 767px) { .orbits { display: none; } }
```

`.orbits` is `position: absolute; inset: 0` decoration, so **nothing in the hero moves**, and that
was checked rather than argued. At 390, F7 build vs F11 build:

| | F7 | F11 |
|---|---|---|
| `.orbits` computed `display` | `block` | **`none`** |
| orbit ink painted (orbit block isolated, 1170×2532 device px) | 14,498–14,644 px, 87–126 colours | **0 px, 1 colour** |
| `document.getAnimations().length` | 165 | **164** (the orbit animation does not exist) |
| `h1` / `form` / `stats` / `.inner` / hero box | — | **identical to the pixel** |
| `document.documentElement.scrollHeight` | 2826 | **2826** |

`display: none` is what stops the animation: an element that is not rendered runs no CSS animation,
which is why the animation count drops rather than merely the paint.

---

## 3. The orbiter's motion, proved — and the one place the plan's bar is missed

Both builds, all animations paused, the orbit animation's `currentTime` set explicitly, the
orbiter's `getBoundingClientRect()` centre read relative to its `.track` parent.

**18 named instants across a lap, at 1280 and at 390** (identical at both, because the track is at
the same place in the hero either side of the breakpoint — this table is the desktop one; at 390 the
F11 orbiter does not exist at all, which is section 2's table instead):

| t (s) | 0 | 1.3 | 2.167 | 3.25 | 4.333 | 6.5 | 7.9 | 8.667 | 10.833 |
|---|---|---|---|---|---|---|---|---|---|
| Δ px | 0.0000 | 0.0662 | 0.2116 | 0.1219 | 0.0974 | 0.0483 | 0.1510 | 0.0975 | 0.2114 |

| t (s) | 13 | 15 | 15.167 | 17.333 | 19.5 | 21.667 | 23.833 | 25.9 | 41 |
|---|---|---|---|---|---|---|---|---|---|
| Δ px | 0.0001 | **0.4104** | 0.2117 | 0.0974 | 0.0483 | 0.0975 | 0.2112 | 0.0620 | **0.4104** |

**And densely — 261 instants, every 0.1 s over the whole 26 s lap:** median **0.1295 px**, mean
0.1475, max **0.4104 px**; **229 of 261 instants are within the plan's 0.25 px and 32 are not**
(24 over 0.30, 4 over 0.40).

Decomposed against the path's own tangent, the miss is not the keyframes:

| component | max | median | what it is |
|---|---|---|---|
| **normal** (the shape of the ring) | 0.1755 px | 0.1045 px | the keyframe chords — the script's own error |
| **tangential** (where along the ring) | 0.3931 px | 0.0626 px | **4.8 ms** at the star's 82.1 px/s |

The tangential component is `offset-distance`'s own progress mapping, not mine, and it was isolated
directly. Sampling Chrome's `offset-path` at 401 positions and comparing against two independent
constant-arc-speed models — an exact ellipse and the 4-cubic Bézier decomposition, computed to
double precision — gives **max 0.43 px** and **0.39 px** respectively, and the residual is *not
smooth*: it jumps between neighbouring samples inside a quadrant and returns to zero at every
quadrant boundary. That is the signature of a flattening approximation inside Blink's own path
measure (Blink's `getPointAtLength` on the same `d` disagrees with `offset-path` by up to 0.21 px
for the same reason). Reproducing it in a keyframe block is not possible without reproducing Skia's
subdivision bit for bit; three models were tried (Skia-style dyadic flattening at seven tolerances,
2 and 4 cubics per lap, linear-in-t) and none got below 0.33 px.

So the honest statement, and the one `phase.md` carries: **the new animation is within 0.18 px of a
true constant-arc-speed traversal of the designed curve; today's build is up to 0.43 px from the same
traversal; the difference between the two builds is up to 0.41 px, of which at most 0.18 px is the
new keyframes.** At 82 px/s on a 5 px dot riding a 980 px ring, the whole thing is 4.8 ms of timing.
The screenshot evidence below says the same thing in pixels.

---

## 4. Part 2 — the twinkle, and the mechanism that did not work

The plan named two mechanisms and asked for the first that works. **(a) declarative shadow DOM was
built and refuted**; **(b) the WAAPI handover shipped.** The refutation is worth more than the
attempt, so it is recorded in `phase.md` too.

A static probe page (`3018`, no product code): 240 stars with the shipped `.star::before` twinkle,
one document-level `animationiteration` listener standing in for React's delegated one, four
variants, 8 s idle trace each at 1280:

| variant | `UpdateLayoutTree` / 8 s | `animationiteration` dispatched | counted at `document` | counted inside the shadow tree |
|---|---|---|---|---|
| light DOM (as shipped) | 467 | 376 | 395 | — |
| **stars inside an open shadow root** | **469** | **370** | **0** | **393** |
| light DOM, no listener at all | 131 | 0 | 0 | — |
| **WAAPI handover** | **134** | **0** | 0 | — |

The shadow-DOM reasoning is right as far as it goes — CSS animation events are not composed, so they
never reached the document listener (`0`) — and it buys **nothing**, because Blink gates *creating*
the event on a **document-level listener-type flag** that any listener in the document sets. The
events simply fired inside the shadow tree instead, at the same cost. Nothing about React or Next was
the obstacle; the idea is wrong at the engine level, so no time was spent on hydration.

### What shipped

`components/landing/StarTwinkle.tsx`, a client component that renders `null`. CSS still paints and
animates the field from the **server-rendered first paint** — that is why a canvas was declined and
it is equally why this is a *handover* and not a JS-rendered field. On mount, for each rendered star
it reads the phase its CSS animation had reached, creates the equivalent WAAPI animation on the
pseudo-element, and only then switches the CSS one off:

```ts
star.animate(
  [{ opacity: 1, easing: "ease-in-out" }, { opacity: 0.28, easing: "ease-in-out" }, { opacity: 1 }],
  { duration, delay, iterations: Infinity, easing: "linear", pseudoElement: "::before" },
);
```

`ease-in-out` is **per segment** in CSS, so it belongs on the keyframes and not on the effect's own
`easing` — putting it on the effect would have changed the curve. `duration` and `delay` come from
`getComputedStyle(star, "::before")`, so the per-star numbers stay the file's single source.

Four rules the implementation obeys, three of them found by measurement:

- **Only rendered stars are handed over.** The `≤480px` cut hides the last 80 with `display: none`; a
  CSS animation on such an element does not run, but a WAAPI one does — and **cannot be composited**.
  The first build handed all 240 over and put the forced 60 Hz frame straight back at 390: **480
  `UpdateLayoutTree` per 8 s and 80 animations reporting `compositeFailed`**, against **8** and **0**
  once hidden stars are skipped. This is the slice's one genuine near-miss and it was caught by the
  trace, not by reading.
- **A debounced `resize` re-sync** adds and cancels only what crossed that cut, so every other star
  keeps its phase.
- **Reduced motion hands everything back** and lets `Cosmos.module.css`'s own freeze stand; the media
  query is watched, so flipping the preference either way still works. Measured: `getAnimations()`
  returns **0** under emulated `prefers-reduced-motion` on both builds and both viewports.
- **Every failure path leaves the CSS twinkle untouched** — no `Element.animate`, no pseudo-element
  target (the `animate()` call is in a `try`), an unreadable duration. A browser that cannot do the
  handover simply keeps today's behaviour.

---

## 5. The measurement

### Trace, 8 s idle window, load traced separately so every `Animation` event is seen

| | 1280 F7 | 1280 F11 | 390 F7 | 390 F11 |
|---|---|---|---|---|
| `UpdateLayoutTree` / 8 s | 480 (261.8 ms) | **8 (5.1 ms)** | 480 (432.4 ms) | **8 (16.2 ms)** |
| `animationiteration` dispatched | 453 | **0** | 295 | **0** |
| `compositeFailed` animations | 1 (`offset-distance`) | **0** | 1 (`offset-distance`) | **0** |
| `Paint` | 16 | 16 | 16 | 16 |
| running animations | 247 | 247 | 165 | **164** |
| rendered stars / shooters | 240 / 5 | 240 / 5 | 160 / 3 | 160 / 3 |

**8 per 8 s is below `P4.F7`'s measured floor of 20** (stars hidden *and* orbiter off): what is left
iterating is the 80 s drift and the three-to-five shooters, ~0.4 events a second. The plan asked for
0 `animationiteration`, and the honest number is 0 — the residual frames are the shooters' and the
drift's own iteration boundaries, which are not star twinkles and were never in scope.

### 70 s idle windows, medians of 3 interleaved runs (order alternates each rep)

| | 1280 unthrottled F7 | F11 | 390 + 4× CPU F7 | F11 |
|---|---|---|---|---|
| style recalculation | 4.209 s | **0.417 s (−90 %)** | 3.707 s | **0.152 s (−96 %)** |
| recalc count | 4,200 | **207 (−95 %)** | 4,200 | **125 (−97 %)** |
| layout | 0.016 s | 0.031 s | 0.030 s | 0.033 s |
| script | 0.172 s | 0.038 s | 0.129 s | 0.025 s |
| main-thread task | 12.444 s | **1.196 s (−90 %)** | 10.411 s | **0.485 s (−95 %)** |
| renderer process CPU | 21.14 s | **9.63 s (−54 %)** | 58.54 s | **54.86 s (−6 %)** |
| GPU process CPU | 9.38 s | 13.35 s (**+42 %**) | 2.64 s | 2.13 s (−19 %) |
| **TOTAL Chrome CPU** | **30.58 s** | **23.04 s (−25 %)** | **61.20 s** | **57.00 s (−7 %)** |

Two readings that belong beside the table rather than under it.

**The GPU process takes back a third of what the renderer saved at 1280** (+3.97 s against −11.51 s).
With no main-thread frame to wait for, the compositor is free to run at the display's own rate — this
Mac's panel is variable-refresh, which is also why the variants have to be interleaved. The net is
still −25 %, and this is the **first** change in this thread to move total machine CPU at all:
`P4.F7` bought main-thread style time and explicitly did not move the machine.

**The phone's remaining 57 s is compositing 160 star layers, not style.** `P4.F7` measured the
stars-removed floor at 56.0 s per 70 s at 390 + 4× — F11 lands **within 2 %** of it while keeping
every star. At 1280 the floor was 21.5 s and F11 is 23.04 s, within 7 %. **There is no third free
lever left inside `Cosmos`**; the next one would cost stars.

---

## 6. Payload

Landing route, F7 build → F11 build, from the served bytes:

| | raw | gzip |
|---|---|---|
| document | 280,972 → 281,293 (**+321**) | 38,333 → 38,388 (+55) |
| CSS (4 chunks) | 128,882 → 114,416 (**−14,466**) | 17,983 → 17,143 (−840) |
| JS (12 chunks) | 650,615 → 652,040 (**+1,425**) | 202,261 → 202,834 (+573) |
| `@keyframes orbit` alone | 85 → 4,227 (**+4,142**) | 89 → 965 (+876) |

The CSS *fell* by more than the keyframes added, and the reason is worth knowing before someone
credits this slice with it: adding one client component to the landing tree regrouped Next's CSS
chunks, and the landing no longer downloads `Portfolio.module`'s 18.7 kB. That is a chunking side
effect, so it was checked rather than enjoyed — every route was scanned for CSS-module class names
with no matching rule in the CSS it loads:

```
/                      3014: 129 classes, missing 0 | 3015: 129 classes, missing 0
/stocks                3014:  61 classes, missing 0 | 3015:  61 classes, missing 0
/ask                   3014:  45 classes, missing 0 | 3015:  45 classes, missing 0
/portfolio?sample=1    3014:  95 classes, missing 0 | 3015:  95 classes, missing 0
/events/20250902000288 3014:  80 classes, missing 0 | 3015:  80 classes, missing 0
/ops                   3014:  13 classes, missing 0 | 3015:  13 classes, missing 0
```

`/portfolio` now loads 5 chunks instead of 4 and still gets its own CSS.

---

## 7. "Same effect", proved

**Star field alone** (everything else `visibility: hidden`), all animations paused at the same
`currentTime`, `compare -metric AE`:

| | T = 0 | 1.3 s | 3.7 s | 41 s | reduced motion |
|---|---|---|---|---|---|
| 1280, F7 vs F11 | **0** | **0** | **0** | **0** | **0** |
| 1280, F7 vs F7 (control) | 0 | 0 | 0 | 0 | 0 |
| 390, F7 vs F11 | **0** | **0** | **0** | **0** | **0** |
| 390, F7 vs F7 (control) | 0 | 0 | 0 | 0 | 0 |

Ten `AE = 0` comparisons with the control at 0 on every one, so the harness is exact and the twinkle
handover changes not one byte of the picture.

**Hero orbit block alone**, 1280, paused, exact per-pixel diff:

| t (s) | 0 | 2.0 | 7.9 | 15.0 | 21.0 |
|---|---|---|---|---|---|
| differing pixels | 32 | 31 | 30 | 31 | 31 |
| bounding box | 7×7 | 7×7 | 7×7 | 7×7 | 7×7 |
| max channel delta | 35 | 67 | 42 | 68 | 40 |

Every difference on the whole 1280×800 block is inside **one 7×7 px box** — the orbiter's own disc
(a 5 px circle whose bounding box is 6.06 px after the stage's −14° rotation, plus antialiasing).
**Both ellipse rings are byte-identical at every instant**, and the F7-vs-F7 control is `AE = 0`. The
disc differs even at T = 0, where the position is identical to four decimals: the orbiter is now on
its own composited layer and rasterises its antialiasing slightly differently. The plan allowed
exactly this ("a few anti-aliased pixels").

**Behaviour**, F7 build and F11 build driven identically at 1280:

| | F7 | F11 |
|---|---|---|
| stars / shooters / animations | 240 / 5 / 247 | 240 / 5 / 247 |
| board tabs | 전체 445 · 유증 12 · CB 422 · 매수청구 11 | identical |
| rows per tab | 16 / 11 / 16 / 10 | 16 / 11 / 16 / 10 |
| 「15건 더 보기」 | 16 → 31 rows | 16 → 31 rows |
| hero search typeahead | 삼성에스디에스 018260 · 삼성제약 001360 | identical |
| hero search submit | `/stocks?q=005930`, `내 종목 조회 \| 주주의관제탑` | identical |
| 60 s refresh, `visibilitychange` | — | 3 `/api/board` fetches in 70 s, none while hidden |
| exceptions | 0 | 0 |
| console warnings | 1 (pre-existing CSS preload) | the same 1, same chunk |

**The operator's own runtime** — `next dev` on `127.0.0.1:3010`, React StrictMode, Fast Refresh, the
working tree with these edits — was checked too, because the manifest says that is what the operator
browses day to day and StrictMode runs the effect twice:

```
dev 1280: stars 240, orbits block, twinkle waapi, 247 animations (240 WAAPI)
          UpdateLayoutTree 12/8s, animationiteration 1, exceptions 0, errors []
dev  390: stars 160, orbits none,  twinkle waapi, 164 animations (160 WAAPI)
          UpdateLayoutTree  8/8s, animationiteration 0, exceptions 0, errors []
```

---

## 8. Deviations from `plan.md`

1. **One new product file the plan's file list did not name:**
   `frontend/components/landing/StarTwinkle.tsx`. `Cosmos.tsx` is a server component and `"use
   client"` is per module, so the handover cannot live in it; the alternative — making the whole
   starfield a client component — would have moved 44 kB of markup out of the RSC flight and changed
   hydration cost on the landing, a much larger blast radius than the slice asked for. The new file
   renders `null` and adds **+1,425 B raw / +573 B gzip** of JS.
2. **The mobile half of part 1 was replaced by two operator instructions mid-slice**
   (「in the mobile, just remove the orbit is fine.」, then 「not only the start but the orbit itself
   also」). Desktop is exactly what the plan specified; on `max-width: 767px` the whole orbit block —
   star and both rings — is `display: none`, so the plan's "≥ 12 paused instants at 390" became
   "no orbit element, no orbit animation, no orbit ink, and a hero whose geometry did not move"
   (section 2). Both lines are recorded verbatim in `phase.md` `## Decisions`.
3. **Mechanism (a) was refuted, not adopted** (section 4). The plan said take the first that works;
   the shadow-DOM route does not work for a reason that is about Blink, not about React, so it was
   measured, written down and dropped.
4. **32 of 261 orbiter instants exceed the plan's ≤ 0.25 px**, max 0.4104 px (section 3). The
   keyframes' own contribution is ≤ 0.18 px script-proved and ≤ 0.176 px measured in the normal
   direction; the rest is `offset-distance`'s own progress wobble against constant arc speed, which
   three independent models put at 0.33–0.43 px and which cannot be reproduced in keyframes. Stated
   rather than papered over: **the bar as written is not reachable**, and what is reachable — a
   motion closer to the designed curve than today's, differing by at most 4.8 ms of timing and by
   30 pixels of antialiasing inside the star's own disc — is what shipped.

Not a deviation, but worth naming: **no test file was written** (the plan says none, and this is
cosmetic/animation surface verified live), and **nothing was deployed** — `P4.S10` releases `P4.F7`
and `P4.F11` together.

---

## 9. Artefacts (all outside the repo, session scratchpad)

`f11_geom.py` / `f11_geom_be.json` (the anchor and rotation probe), `f11_path.py` / `f11_path.json`
(401 samples of Chrome's own `offset-path` and `getPointAtLength`), `f11_orbit.py` /
`f11_orbit.json` and `f11_orbit_dense.py` / `f11_orbit_dense.json` (the 18- and 261-instant position
tables), `f11probe/index.html` + `f11_mech.py` (the four-variant mechanism probe), `f11_trace.py`
(compositing and iteration counts), `f11_idle.py` / `f11_idle.log` / `f11_idle.json` (the 70 s
batteries), `f11_frames.py` and `f11_orbitshots.py` + `f11shots/` (the paused frames),
`f11_drive.py` / `f11_drive2.py` (the drive-throughs), `f11_dev.py` (the operator's dev runtime), and
the build trees `f11be/` and `f11af/` with their build logs. All servers (3014, 3015, 3018) and every
browser started by this slice were stopped; the operator's 3010/8010 were never touched.
