# P4.F7 — result

- **status**: `done`
- **summary**: Diagnosed the landing starfield's idle cost in a Chrome trace — the 240 twinkles are
  *already composited*; what costs is that the page produces a main-thread frame on every display
  frame (the Hero orbiter's uncompositable `offset-distance` plus ≈61 `animationiteration` events a
  second) and Blink re-resolves every animation's style inside each one, at ~4.7 µs per star because
  the keyframes resolve `var()`. Moved the twinkle to `.star::before` with literal `1 → 0.28`
  keyframes: **picture byte-identical (`AE = 0`)**, document 2,413 B smaller, idle style
  recalculation **−21 % at 1280 / −31 % at 390 + 4× CPU**, total machine CPU unchanged. The plan's
  candidate A was measured and **rejected** (+17 % total Chrome CPU); the canvas (candidate B) was
  measured and routed to the operator (it cannot paint before hydration).
- **files_changed**:
  - `/Users/sugang/projects/personal/Mijual/frontend/components/landing/Cosmos.tsx`
  - `/Users/sugang/projects/personal/Mijual/frontend/components/landing/Cosmos.module.css`
  - `/Users/sugang/projects/personal/Mijual/works/phases/active/P4/phase.md`
  - `/Users/sugang/projects/personal/Mijual/works/phases/active/P4/slices/P4.F7/result.md`
- **validation**
  | command / check | result |
  |---|---|
  | `cd frontend && npm run typecheck` | PASS (`tsc --noEmit`, exit 0) |
  | `cd frontend && npm run smoke` | PASS — **22/22**, 0 fail |
  | `npm run build` (scratchpad copy `f7c6/`, not the repo) | PASS — `✓ Compiled successfully`, TypeScript clean, standalone output |
  | `python3 scripts/workflow.py validate` | PASS (`Workflow validation passed.`; the standing `oversized_doc_sections` warning only) |
  | paused-frame `AE`, star field, T = 0 / 1.3 / 3.7 / 41 s × 1280 / 390 | **0 on all eight**, control **0** |
  | paused-frame `AE`, emulated `prefers-reduced-motion: reduce`, 1280 / 390 | **0 / 0**, control **0** |
  | rendered star / shooter counts, 1280 and 390 | 240 + 5 and 160 + 3 — unchanged |
  | `document.getAnimations().length`, DOM nodes | 247 / 165 and 686 / 682 — unchanged |
  | trace: animations reporting `compositeFailed` after the change | still exactly **1**, the Hero orbiter (`offset-distance`) |
  | 70 s idle × 3 interleaved runs × 2 viewports, `Performance.getMetrics` + `SystemInfo.getProcessInfo` + `ps` | table below |
  | landing document bytes (local production build) | 283,385 → **280,972** raw; gzip 40,527 → 40,529 |
  | `git diff --stat` (product) | the two Cosmos files only |
- **deviations**: three, all measurement-driven — the plan's candidate A was implemented, measured,
  and **rejected**; candidate B was prototyped, measured, and **not shipped**; a third mechanism
  (the one that shipped) was found and taken. Detail in *§ Deviations*.
- **doc_impact**: one line appended to `phase.md`'s `## Doc impact` — `frontend` — Cosmos: the
  twinkle now lives on `.star::before` with one shared literal `@keyframes`, `.star` keeps only its
  static `opacity: var(--star-opacity)`, per-star timing travels as `--star-duration` /
  `--star-delay`; **a per-star value may live in the element or in the paint, never inside a
  keyframe's `var()`/`calc()`**; and the landing's twinkles are composited — the cost is the page's
  forced 60 Hz main frame.
- **doc_versions**: n/a (not a review slice) — deferred to a docs phase
- **review_verdict**: n/a
- **walkthrough**: none
- **explain**: n/a
- **operator_need**: none to finish this slice. Two decisions are **routed** to the gate in
  `phase.md`'s `## Operator Questions` (the canvas field; the Hero orbiter), and the change is
  **not deployed** — `P4.S10` releases it, before 2026-09-07 11:00 KST.

---

## 1. Instrument, targets, and what was never touched

**Instrument.** Real **Google Chrome 152.0.7977.65**, headful, launched through a throwaway profile
on a fresh port (`--remote-debugging-port=9361 --user-data-dir=<scratchpad>/f7prof`), driven over the
DevTools protocol from `scratchpad/f7_cdp.py` — the same fallback instrument `## Operator Runtime`
records and `P4.R1` used, because **Aside's daemon does not run on this Mac and there is no agent
Aside account**. Every browser was closed with `Browser.close`; port 9361 is free and no process from
that profile survives.

**Targets.** Four **local production builds**, each a copy of `frontend/` built with
`NEXT_PUBLIC_SITE_URL=https://jujutower.com MIJUAL_API_ORIGIN=http://127.0.0.1:8010 npm run build`
and served by `node .next/standalone/server.js` with `.next/static` + `public/` staged:

| port | tree | what it is |
|---|---|---|
| 3014 | `f7be` | **as shipped** (repo `HEAD`, `64ccf6d`) |
| 3015 | `f7af` → `f7c3` → `f7c6` | the successive candidates (last = what shipped) |
| 3016 | `f7af2` | candidate A's second form (custom property kept in the paint) |

The build ran in **copies** of `frontend/`, never in the repo, because `next build` and the
operator's running `next dev` share `frontend/.next`. Every server was stopped; 3014/3015/3016 are
free. **The operator's stack answered 200 on 3010 and 8010 before and after.**

**Never touched:** production (not one request — the whole slice ran against local builds), the
Oracle box, any deploy, any workflow state command other than `validate`, any `git commit`/`push`,
`uv run --with`. **No secret value appears anywhere in this slice.**

---

## 2. The diagnosis — the premise was wrong, and that is the finding

The plan asked *why* the 240 twinkle animations run on the main thread. **They do not.** Three
independent measurements say so.

**(a) The trace names one failure, and it is not a star.** `Tracing.start` with
`blink.animations,devtools.timeline,disabled-by-default-devtools.timeline` over a load + idle window:
495 `Animation` events, 240 of them `Cosmos-module__…__twinkle`, and **exactly one** carries a
compositing failure —

```
{"name":"Animation","cat":"blink.animations,devtools.timeline,benchmark,rail","ph":"n",
 "args":{"data":{"compositeFailed":8352,"unsupportedProperties":["offset-distance"]}}}
```

— the **Hero `.orbiter`** (`animation: orbit 26s linear infinite` over
`offset-path: path(…)`), whose animated property Chrome cannot composite. No twinkle reports one.

**(b) Blocking the renderer's main thread does not stop the twinkle.** A `setTimeout` busy loop held
the main thread for 2.5 s (proved: a trivial `Runtime.evaluate` fired 400 ms into the block took
**2,303 ms** to return). Two `Page.captureScreenshot`s taken *during* the block, with only the
backdrop visible, differ (`RMSE 0.0065`; the same test on the shipped build after the change gives
`0.0093`). **The stars keep twinkling with no main thread. They are compositor-driven.**

**(c) So the cost is the per-frame style update, and the frames are forced by two things.** In an
8 s idle window at 1280 the trace shows **480 `UpdateLayoutTree`** — exactly 60 a second, one per
display frame — and **12 `Paint`** events totalling 1.1 ms. Nothing is repainting; the main thread
is re-resolving style. Injecting CSS into a throwaway tab isolates the two drivers:

| what is running | `UpdateLayoutTree` in 8 s | of which, cost |
|---|---|---|
| as shipped | 480 | 624.7 ms |
| stars hidden, orbiter running | 481 | 79.8 ms |
| stars running, orbiter's animation off | 475 | 751.7 ms |
| **stars hidden AND orbiter off** | **20** | **3.1 ms** |

Either one alone keeps the main thread producing a frame 60 times a second. The orbiter does it
because it is not compositable. The stars do it because **240 CSS animations with all-distinct
durations dispatch ≈61 `animationiteration` events a second** — counted directly in the trace
(`EventDispatch`, `data.type`): **487 in 8 s**, and React registers a delegated `animationiteration`
listener on the root container, so Blink must dispatch every one of them.

**(d) And inside each of those frames, every running animation is re-resolved.** That is
240 style resolutions per frame — measured at **≈4.7 µs per star per frame** as shipped. A synthetic
control page (240 identical spans, no React, nothing else animating) produces only ~12 main frames a
second and ~0.6 µs per star per frame with literal keyframes, and **zero** frames with one star or
with the drift alone. The difference between 4.7 µs and ~2 µs is the **`var()`**: a keyframe whose
value is `opacity: var(--star-opacity)` / `calc(var(--star-opacity) * 0.28)` cannot be served from
Blink's base-computed-style cache, so the whole declaration set is re-resolved per element per frame.

**That is the lever this slice could take without touching anything else**, and it is the one that
shipped. `P4.R1`'s own injection measured its size correctly (4,025 → 3,198 ms, −21 %); what R1 could
not see is *why*, which is what made the safe form findable.

---

## 3. What shipped

`.star` is now **nothing but its own alpha**, and the twinkle is on its pseudo-element:

```css
.star { position: absolute; opacity: var(--star-opacity); }

.star::before {
  content: ""; position: absolute; inset: 0; background: #ffffff;
  animation-name: twinkle; animation-timing-function: ease-in-out;
  animation-iteration-count: infinite;
  animation-duration: var(--star-duration);
  animation-delay: var(--star-delay);
}

@keyframes twinkle { 0%, 100% { opacity: 1; } 50% { opacity: 0.28; } }
```

`Cosmos.tsx` writes `--star-opacity`, `--star-duration`, `--star-delay` inline instead of
`--star-opacity` + `animation-duration` + `animation-delay`. Nothing else changed: same 240/160
stars, same positions, sizes, base alphas, durations, delays, same `ease-in-out`, same 80 s drift,
same five/three shooters, same `≤480px` rule, same reduced-motion freeze (now on `.star::before`,
because the shell's `[data-motion="tick"]` rule reaches an element and its own pseudo-elements, not a
grandchild's).

**Why it is exactly the same picture, not approximately.** Alpha composes multiplicatively for one
solid element over the page: before, one layer at `opacity = a·f(t)`; after, a pseudo-element at
`opacity = f(t)` inside a parent at `opacity = a`. Both paint `a·f(t)` white. The keyframe values
`1` and `0.28` are the *ratios* the old `calc(var(--star-opacity) * 0.28)` computed, so `f(t)` is
identical, not merely close. Measured, not assumed — § 5.

**Why the per-star timing moved into custom properties.** `animation-duration`/`-delay` set inline on
`.star` do not reach `.star::before`. Read through `var()` **on a property that is not animated**,
they are resolved once into the cached base style — which is the whole distinction this slice found,
and the reason this is cheap while a `var()` *inside* a keyframe is not.

---

## 4. The measurement table

70 s idle after load, `Performance.getMetrics` deltas + `SystemInfo.getProcessInfo` cpuTime deltas
across **every** Chrome process + `ps -o %cpu` sampled every 5 s. Three runs per cell, order
**reversed on the middle run** so a position effect cannot masquerade as a result. `fps` is a 2 s
`requestAnimationFrame` sample taken just before each window (60.1–60.4 everywhere).

### 1280 × 800, unthrottled

| run | variant | RecalcStyle | Layout | Script | Task | renderer CPU | GPU CPU | **total Chrome CPU** | `ps` mean |
|---|---|---|---|---|---|---|---|---|---|
| 0 | before | 5.867 s | 0.017 | 0.168 | 13.042 s | 20.42 s | 8.91 s | 29.43 s (41.6 % of a core) | 40.7 % |
| 0 | **after** | **4.755 s** | 0.018 | 0.188 | 13.737 s | 23.38 s | 10.79 s | 34.34 s | 48.7 % |
| 1 | before | 6.212 s | | 0.192 | 13.991 s | 22.53 s | 11.10 s | 33.70 s | 47.9 % |
| 1 | **after** | **4.748 s** | | 0.197 | 13.629 s | 23.37 s | 11.19 s | 34.62 s | 47.9 % |
| 2 | before | 5.842 s | | 0.166 | 13.032 s | 20.41 s | 8.97 s | 29.43 s | 40.4 % |
| 2 | **after** | **4.332 s** | | 0.170 | 12.346 s | 20.26 s | 8.79 s | 29.10 s | 39.6 % |
| — | floor (stars hidden) | 1.069 s | 0.034 | 0.040 | 5.121 s | 10.39 s | 11.09 s | 21.59 s (30.5 %) | 29.4 % |

**RecalcStyle −19.0 / −23.6 / −25.8 % (median −21 %).** Task: +5.3 / −2.6 / −5.3 % — no movement.
**Total CPU: +16.7 / +2.7 / −1.1 %** — and the +16.7 % pair is the one where *before* ran first in a
cold session; the shipped build itself measures 29.4 s in that position and 33.7 s in the other, a
band wider than the effect. Honest reading: **total machine CPU is unchanged at 1280.**

### 390 × 844 @ DPR 3, 4× CPU throttling

| run | variant | RecalcStyle | Task | renderer CPU | GPU CPU | total Chrome CPU | `ps` mean |
|---|---|---|---|---|---|---|---|
| 0 | before | 5.069 s | 10.658 s | 58.84 s | 2.51 s | 61.38 s (87.1 %) | 86.2 % |
| 0 | **after** | **3.526 s** | **9.968 s** | 58.77 s | 2.50 s | 61.30 s | 85.9 % |
| 1 | before | 5.107 s | 10.657 s | 58.84 s | 2.51 s | 61.37 s | 86.3 % |
| 1 | **after** | **3.474 s** | **9.779 s** | 58.75 s | 2.40 s | 61.18 s | 85.6 % |
| 2 | before | 4.983 s | 10.583 s | 58.80 s | 2.49 s | 61.31 s | 86.1 % |
| 2 | **after** | **3.458 s** | **9.687 s** | 58.75 s | 2.37 s | 61.14 s | 86.1 % |
| — | floor (stars hidden) | 0.142 s | 1.025 s | 55.08 s | 0.92 s | 56.02 s (79.5 %) | 79.2 % |

**RecalcStyle −30.4 / −32.0 / −30.6 %. Task −6.5 / −8.2 / −8.5 %. Total CPU −0.1 / −0.3 / −0.3 %.**
Rock steady, three for three, in both orderings.

### The honest headline

The change removes **a fifth to a third of the landing's idle style recalculation** and leaves the
machine's total load where it was. `P4.R1`'s 「7,203 ms of style recalculation per 70 s」 becomes
**~5,700 ms** desktop and **~3,500 ms** at 390 + 4×. It does **not** deliver the 「~24 % of a core」
back — nothing inside `Cosmos.module.css` can, and § 6 says what can.

### Payload

| | raw | gzip |
|---|---|---|
| before | 283,385 B | 40,527 B |
| **after** | **280,972 B (−2,413)** | 40,529 B (+2) |

---

## 5. "Same effect", proved

`document.getAnimations().forEach(a => { a.pause(); a.currentTime = T })` at **T = 0, 1.3, 3.7 and
41 s** (mid-drift), full-viewport `Page.captureScreenshot(fromSurface)`, `magick compare -metric AE`.
A **before-vs-before control** (a second load of the unchanged build) ran through the identical path
at every instant.

| viewport | T = 0 | T = 1.3 | T = 3.7 | T = 41 | control |
|---|---|---|---|---|---|
| 1280 × 800 | **0** | **0** | **0** | **0** | 0 |
| 390 × 844 @ 3 | **0** | **0** | **0** | **0** | 0 |
| `prefers-reduced-motion: reduce` | **0** (1280) | | **0** (390) | | 0 |

Those frames render **only the star field** (the rest of the page and the shooters hidden by injected
`visibility`), which is what makes the comparison decisive: with live content in frame the countdown
text, the 기준시각 and the board differ between any two loads, and the before-vs-before control comes
out the same order of magnitude as any candidate — measured, and reported here rather than dressed
up as a result:

| viewport | T | after vs before | **control** (before vs before) |
|---|---|---|---|
| 1280 | 0 | 1.159e7 | 1.136e7 |
| 1280 | 3.7 | 9.675e6 | 9.444e6 |
| 390 | 1.3 | 7.570e7 | 7.367e7 |
| 390 | 3.7 | 1.141e8 | 1.120e8 |

Structure, checked directly rather than inferred: **240 stars + 5 shooters at 1280, 160 + 3 at 390**
(so the `≤480px` rule still cuts exactly the tail it did); **247 / 165 running animations**; **686 /
682 DOM nodes** — all identical before and after. A sample star's computed style after the change:
element `opacity: 0.778` (its base alpha, static), `background-color: rgba(0,0,0,0)`; pseudo-element
`background-color: rgb(255,255,255)`, `animation-name: …twinkle`, `animation-duration: 3.145s`,
`animation-delay: 5.159s`.

*(`AE` here is ImageMagick 7's quantum-scaled absolute error: a single pixel differing at full range
reads 65535, so `AE = 0` means byte-identical.)*

---

## 6. Deviations — the two shapes the plan named, measured and rejected

### Candidate A (the plan's step 2) was built, measured, and rejected: **+17 % total Chrome CPU**

Implemented exactly as specified — base alpha into the paint
(`background-color: rgba(255,255,255,<opacity>)`), `opacity` animating between the constants
`1 → 0.28` — and built twice, as two independent trees: `f7af` (alpha written inline as `rgba()`)
and `f7af2` (alpha kept in `--star-opacity` and read by `background-color`, so the markup stays
byte-identical). Both were served and measured against the shipped build over 70 s idle windows,
3 runs each:

| 1280, per 70 s | RecalcStyle | Task | renderer | **GPU** | **total** |
|---|---|---|---|---|---|
| before | 6.406 s | 14.205 s | 22.81 s | 10.35 s | 33.22 s |
| candidate A, inline `rgba()` | 4.431 s | 13.332 s | 25.14 s | **16.30 s** | **41.57 s (+25 %)** |
| candidate A, `var()` in the paint | 4.521 s | 13.355 s | 25.21 s | **16.57 s** | **41.83 s (+26 %)** |

Reproduced in a second, order-alternating battery (40 s windows, medians of 3): total
**19.39 → 22.62 s (+17 %)**, GPU 6.31 → 8.14 s. **The style-recalculation win is real and the
machine pays more for it**: making a star's layer contents translucent (they were opaque white with
the alpha in the layer's own `opacity`) costs more in the compositor and GPU than it saves on the
main thread, and the trace shows the `Layerize` phase rising with it (128 → 154–172 ms per 8 s).
The operator asked to *reduce the cost*; a change that raises total CPU is not that, so it did not
ship. Its rendering, for the record, was very nearly identical but **not** identical — the star
field's paused frames came out at 0.8–1.0 pixel-equivalents of absolute error at 1280 (224–605
pixels differing by 1–2 levels out of 255), because the base alpha is quantised in the paint as well
as in the layer.

### Candidate B (canvas) was prototyped and measured — a real win, and **not shipped**

A `requestAnimationFrame` canvas renderer reading the same `STARS[]` numbers (same percentage
positions, sizes, base alphas, and the same `cubic-bezier(0.42,0,0.58,1)` per half-cycle from a
1024-entry LUT), drawn over the same drifting `.field`, measured in the same alternating harness:

| 1280, 40 s idle, medians of 3 | RecalcStyle | Task | renderer | GPU | total |
|---|---|---|---|---|---|
| shipped | 3.595 s | 8.077 s | 13.04 s | 6.31 s | 19.39 s |
| **canvas** | **0.590 s (−84 %)** | **3.706 s (−54 %)** | **6.79 s (−48 %)** | 8.24 s (+31 %) | **14.85 s (−23 %)** |
| floor (no stars) | 0.622 s | 2.937 s | 5.92 s | 6.43 s | 12.38 s |

At 390 + 4×: total **34.87 → 32.78 s (−6 %)** against a floor of 31.85 s. It also removes the
44 kB of starfield markup `P4.R1` counted.

**It did not ship because it fails the plan's constraint (1), and constraint (1) is the hard one.**
A canvas is painted on the client, so the backdrop would be **starless from first paint until the
landing's JS hydrates** — a few hundred ms on a cold phone — which is a change to 「same effect」 at
load, on a design element R2/R2.1 signed and the operator explicitly declined to change. Its
rasterisation is also not provably pixel-identical (Skia `fillRect` at fractional coordinates versus
a composited, device-pixel-snapped CSS box). Both are fixable — the spans can be server-rendered and
swapped out after the canvas's first frame — but that is a re-implementation of a signed component,
not a fix slice, and it is **routed to the operator** in `phase.md` with these numbers.

### A third mechanism was found, and it is what shipped

Neither shape in the plan satisfies both constraints, so the search continued through five more
mechanisms, each screened in the same order-alternating harness at 1280 (40 s windows, medians of 3).
All of them get the `var()` out of the keyframes; they differ in what they cost elsewhere:

| mechanism | RecalcStyle | total CPU | payload | picture |
|---|---|---|---|---|
| shipped (baseline) | 3.34–3.60 s | — | — | — |
| `@property --star-opacity` registration only | 3.61 s | ±0 | ±0 | identical |
| candidate A (translucent paint) | 2.39 s | **+17 %** | +233 B gzip | ~1 px-equiv |
| `filter: opacity()` on the star | 2.38 s | +15 % | ±0 | not measured |
| per-star literal `@keyframes` | 2.47 s | ±0 | **+43 kB raw / +6 kB gzip** | identical |
| **`.star::before` + literal keyframes (shipped)** | **2.56 s** | **±0** | **−2.4 kB raw** | **`AE = 0`** |

The per-star-`@keyframes` form is the most obvious one and was fully built and served before being
dropped: 240 distinct number pairs do not compress, so the landing document went **283,385 →
326,379 B** and the wire cost **40,529 → 46,493 B** — more than undoing all of `P4.F6`.
The pseudo-element form gets the same win for **nothing**.

### Smaller deviations

- **`npm run build` was run in scratchpad copies, not in the repo** — `next build` and the
  operator's running `next dev` share `frontend/.next`, and the plan forbids disturbing 3010.
- **Ports 3015 and 3016 were used alongside 3014.** The plan names 3014; a second and third origin
  were needed to serve two builds at once, because this Mac's display refresh drifts between 60,
  120 and 180 Hz under ProMotion and every per-window total scales with it — variants have to be
  interleaved inside one session, and the final 70 s battery reports its `fps` sample per row so the
  reader can see the rate was 60 Hz throughout.
- **`will-change: opacity` was not added** (the plan's step 2 asks for it). It is unnecessary — the
  animations are already composited — and it measured neutral-to-worse in every battery it appeared
  in (e.g. 307.2 → 338.4 ms of `UpdateLayoutTree` per 8 s in one screen).
- **The measured build `f7c6` and the final tree differ only in comment text.** After the last
  battery, two in-code comments were corrected to carry the real-build numbers instead of the
  screening ones; both are a JSDoc block and a CSS comment, neither survives the production build.
  `typecheck` (PASS) and `smoke` (**22/22**) were re-run on the final tree.
- **Production was never loaded.** The plan permits a production read for the "before"; it was not
  needed, because the before is the same build served locally and the comparison must be like for
  like.

---

## 7. What this leaves on the table, and for whom

Removing the stars entirely is the floor: **29.4 → 21.5 s of total Chrome CPU per 70 s at 1280
(−27 %)**, and **61.4 → 56.0 s at 390 + 4× (−9 %)**. This slice captured none of that and could not:
the residue is the compositing of 240 layers on every frame, plus the page's forced 60 Hz main frame.
Two levers reach it, both changing signed R2 material and both now in `phase.md`'s
`## Operator Questions`:

1. **The canvas field** — the numbers in § 6, at the price of a starless backdrop until hydration.
2. **The Hero orbiter** — `offset-distance` is the one animation on the landing Chrome cannot
   composite, and it alone holds the main thread at 60 frames a second forever: with every star
   hidden the page still runs **481 `UpdateLayoutTree` per 8 s**; with the orbiter's animation off
   *as well*, it falls to **20**. Re-expressing that 26 s ellipse as a composited `transform`
   animation (≈120 keyframes, worst-case deviation ≈0.17 px on a 490 px radius) is the single
   biggest idle-cost lever on the landing — **and it is worth more on a phone than anything inside
   `Cosmos`**, where the floor itself is only −9 %.

---

## 8. Artefacts (all outside the repo, session scratchpad)

`f7_cdp.py` (CDP client), `f7_trace.py` / `f7_trace2.py` (compositing + lifecycle traces),
`f7_probe.py` … `f7_probe7.py` (the mechanism screens, `f7_probe4.json` / `f7_probe5_1280.json` /
`f7_probe6.json` / `f7_probe7.json`), `f7_blocktest.py` + `f7_blockproof.py` (the main-thread block),
`f7_frames.py` / `f7_frames2.py` / `f7_frames3.py` + `f7f_*.png` / `f7g_*.png` / `f7h_*.png` /
`f7i_*.png` (paused frames), `f7_idle.py` / `f7_idle2.py` + `f7_idle.json` / `f7_idle2.json` (the
70 s batteries), `f7_final.py` / `f7_final2.py` + logs (the total-CPU batteries), `f7_verify.py`,
`f7_build.sh` / `f7_serve.sh`, and the build trees `f7be/`, `f7af/`, `f7af2/`, `f7c3/`, `f7c6/`.
Nothing was written into the repository except the two Cosmos files, `phase.md` and this file.
