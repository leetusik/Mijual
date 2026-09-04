# P12.F9 — result

- **status:** done
- **summary:** IBM Plex Mono now has hand-declared, **measured** metric-matched local fallback faces
  (`adjustFontFallback: false` + `plexMono Fallback Apple` / `Windows` / `Arial` in `app/shell.css`),
  and Next's generated `local(Arial)` face at `size-adjust: 131.49%` — a **proportional** face behind
  a monospace one, still live on production today — is gone. On the cold 412×915 / DPR 2.625 / 4× CPU
  / ≈1.6 Mbps profile the per-element mono width delta across the Plex swap falls from **17.61 px
  (`/stocks/00547510`), 24.88 (`/events`), 13.70 (`/portfolio`), 12.69 (`/`)** to **0.047 / 0.078 /
  0.016 / 0.047 px** with **CLS 0** and **no `layout-shift` entry near either Plex file's
  `responseEnd`**; the warm, loaded rendering is **byte-identical** to HEAD (rect diff 0 moved /
  max 0.000 px on 4 routes × 2 viewports; `magick compare -metric AE` **0** on 8 captures with a
  live positive control). `preload: false` and `display: "swap"` untouched, no font file added,
  no network cost.
- **files_changed:** `frontend/app/fonts.ts`, `frontend/app/shell.css`,
  `works/phases/active/P12/phase.md`, `works/phases/active/P12/slices/P12.F9/result.md`
- **validation:**
  - `cd frontend && npm run typecheck` (`tsc --noEmit`) → **clean**
  - `npm run smoke` → **22/22 pass**
  - `npx next build` in a fresh copy outside the repo (`NEXT_PUBLIC_SITE_URL=https://jujutower.com`)
    → **exit 0, zero warnings**; built CSS greps: `font-family:plexMono Fallback;src:local(Arial)`
    **count 0**, the three hand families present with the derived numbers, 5 `unicode-range`
    declarations, emitted `--font-plex-mono` leading with them (§2, §6)
  - HEAD control build on **:3015** beside the fixed build on **:3014**, plus dev **:3010**
    (the generated Arial face is gone there too — §6)
  - fit sweep, 6 routes × 6 candidates + a loaded-vs-loaded noise control, rect of every `body *`
    (§3) → **0 moved at 99.66 %, both neighbours move**
  - cold-cache sweep, 4 routes × 2 builds × **3 loads**, fresh tab and cleared cache per load,
    medians (identical across all 3 runs of every cell) (§4)
  - warm rect equality + swap-window rect equality, 4 routes × {1280, 390} × 2 builds (§5)
  - `magick compare -metric AE`, 8 comparisons + 2 positive controls + 3 noise floors (§5)
  - console/hydration capture with a live `__probe_live__` shim on every measured load (§6)
  - `python3 scripts/workflow.py validate` → **passed** (pre-existing warnings only)
- **deviations:** five, all recorded below — (1) **three fallback families, not two, and a
  `unicode-range` on the matched ones**, because measurement showed the two-family shape would have
  changed the *resting* product (§2.4); (2) the fit ran by injecting candidates over the unchanged
  HEAD build, then the derived number was baked and re-measured for real (P4.F5's own deviation 1);
  (3) the warm AE captures at 390 use **DPR 1**, because a DPR-2 emulated tile does not fit the
  window (§5); (4) the Windows face declares two weight blocks though Consolas is unmeasurable here —
  `size-adjust` still **100 %**, no width claim; (5) the optional production re-measurement was done
  as a single read-only `curl` of the served CSS instead of a browser load (§7).
- **doc_impact:** two lines appended to `phase.md` — `frontend.md` (the two matched faces, the
  method applied to the mono face, the generated Arial face removed and re-declared behind a
  `unicode-range`, cold-cache mono reflow 0) and `qa.md` (the landing screenshot noise floor and the
  DPR-2 emulated-tile clip).
- **doc_versions:** n/a (not a review slice — versioning is deferred to a docs phase)
- **review_verdict:** n/a
- **walkthrough:** none
- **explain:** n/a
- **operator_need:** none. **Q2 is answered by this fix** and needs no operator decision: the
  `P4.F5` route was taken, `preload: false` was **not** reversed, and the reflow is gone — the
  review routes Q2 as answered.

---

## 1. Instrument, runtime, and what the "before" is

**Instrument: Aside, `aside repl --account u2`** (profile 「claude2」), never `u0`. CDP through
`page._sendToTarget`, one route per invocation, a fresh tab per cold load, probes installed with
`Page.addScriptToEvaluateOnNewDocument` before `goto` — the seam in `phase.md` `## Decisions`, used
unchanged. `magick` for the AE comparisons, `uvx --from fonttools --with brotli python …` for the
font-table reads (a tool run, never a project dependency).

**Runtime:** the local production build (`node .next/standalone/server.js`) on **:3014**, a **HEAD
control build** on **:3015** built from `git show HEAD:frontend/{app/fonts.ts,app/shell.css}` into a
second copy (F1's note (a): never a `git stash` sweep against `next dev`), and the operator's dev
stack on **:3010**. Production (`a74c58a`) was read once, read-only, with `curl`.

**The before is measured, not quoted.** The HEAD control on 3015 reproduces `P12.R1`'s numbers to
the pixel: `Lookup__cval` 「0.0863800841」 **97.2 → 113.53** (Δ16.328), `DDay__date`
**92.42 → 106.13** (13.703), 「20%」 **27 → 39.48**, `DDay__label` **30.61 → 36.02**, with
`IBMPlexMono_Regular` 567→1097 ms and `SemiBold` 572→1272 ms and `NotoSansKR` 177→3030 ms. That is
what makes the two columns in §4 comparable.

## 2. The metrics, measured two ways — and the fact that changed the design

### 2.1 From the font tables (fontTools)

| face | upem | hhea asc / desc / gap | advance, every glyph | in em |
|---|---|---|---|---|
| **IBM Plex Mono** Regular **and** Medium **and** SemiBold (our subsets) | 1000 | **1025 / −275 / 0** | **600**, one value across all three weights and all 211 codepoints | **0.600000** |
| **Menlo** Regular / Bold | 2048 | 1901 / −483 / 0 | **1233**, one value over 210 of those 211 | **0.6020508** |
| `.SF NS Mono` (`SFNSMono.ttf`, wght axis 295–900) | 2048 | 1980 / −432 / 0 | 1266 | 0.6181641 |
| Courier · Courier New · Andale Mono | 2048 | — | 1229 | 0.6000977 |
| PT Mono | 1000 | 885 / −235 / 0 | 600 | 0.600000 |
| Consolas | — | — | **not on this machine** | — |

The three Plex subsets have **identical cmaps** (211 codepoints: ASCII + Latin-1 + a punctuation
set) and one advance each, so one number serves every weight and every string. Menlo lacks exactly
one of those codepoints, **U+2044 ⁄**, which the product never renders.

### 2.2 In Chrome (laid-out rects, 10 digits at 100 px, on the running build)

| family requested | 400 | 500 | 600 | 700 |
|---|---|---|---|---|
| `plexMono` (loaded) | 600.0 | (600.0, tables) | **600.0** | **600.0** — 700 is *synthesised* from 600 and the advance does not move |
| `local("Menlo-Regular")` declared 400/500/600/700 | 602.0625 | 602.0625 | 602.0625 | 602.0625 |
| `local("Menlo-Bold")` declared 600 900 | — | 602.0625 | 602.0625 | 602.0625 |

602.0625 / 10 = 60.20625 px = the table's 1233/2048 to sub-pixel rounding. **Synthesised bold changes
the advance in neither face**, so the weight mapping is free of layout risk (P4.F5's finding, re-proved
here for a monospace pair).

### 2.3 The four divisions

```
size-adjust      = (600/1000) / (1233/2048) = 0.6 / 0.60205078 =  99.66 %
ascent-override  = (1025/1000) / 0.9966                        = 102.85 %
descent-override = ( 275/1000) / 0.9966                        =  27.59 %
line-gap-override                                              =   0 %
```

Windows: `size-adjust: 100 %` with Plex's own `102.5 % / 27.5 % / 0 %`, because **Consolas is not on
this machine** and measures identically to a deliberately bogus family — Malgun's treatment, ruling 3.
(The number a measurement would test is 0.6 ÷ 1126/2048 = 109.13 %; it is not claimed here.)

### 2.4 Two measurements that changed the design

**(a) The face is Menlo, and `local()` cannot reach SF Mono.** With the webfont blocked, CDP
`CSS.getPlatformFontsForNode` on a span carrying the product's own generic tail:

| requested | platform font Chrome painted |
|---|---|
| `ui-monospace` | **Apple SD Gothic Neo** — i.e. *nothing*: Chrome does not implement this generic |
| `SFMono-Regular` | Apple SD Gothic Neo (nothing) |
| `"SF Mono"` | Apple SD Gothic Neo (nothing) |
| `Consolas` | Apple SD Gothic Neo (nothing) |
| `monospace` | **Menlo-Regular** |
| the full shipped tail | **Menlo-Regular** |

and the `local()` probe (21 candidates, `document.fonts.load()` + a bogus control that fails
identically):

| `local(...)` | resolves? |
|---|---|
| `Menlo-Regular`, `Menlo Regular`, `Menlo-Bold`, `Menlo Bold` | **yes** → Menlo, 602.05 px |
| `Menlo` (the bare family) | **no** — `NetworkError`, measures as the bogus control |
| `.SFNSMono-Regular`, `.SF NS Mono`, `.SF NS Mono Regular`, `.SFNSMono-Semibold`, `SFMono-Regular`, `SF Mono` | **no**, all six |
| `Consolas`, `Consolas Bold` | no (absent on macOS) |
| `Courier`, `CourierNewPSMT`, `PTMono-Regular`, `AndaleMono` | yes (present, but not what Chrome picks) |
| `NoSuchFaceZZQQ_bogus_control` | no — the control |

So **no SF Mono face is declared**: it ships as the hidden `.SF NS Mono` and is unreachable. P4.F5's
rule — `local()` matches a full name or a PostScript name, never a family name — is re-proved
(`local("Menlo")` fails, `local("Menlo Regular")` resolves) and, incidentally, explains why Next's own
`local(Arial)` works: **"Arial" is Arial Regular's full name.**

**(b) The plan's two-family shape would have changed the resting product — so there are three.**
Our Plex subsets are **Latin-only**, and the product renders two characters outside them inside
`.mono` elements: **`←`** (the `Lookup__crumb` / `Event__crumb` 관제 현황판 breadcrumb) and **`→`**
(`Lookup__arw`). Those never painted in Plex at all — warm *and* cold they paint in the generated
**ArialMT** face at 131.49 %, measured: `Lookup__arw` is **15.781 px**. Menlo covers both, so a
plain metric-matched Apple family would have taken them over and shrunk that arrow to **7.234 px** —
a visible change to a signed surface **at rest**, which this phase's shared bar forbids and which is
the operator's call, not mine (the R1 F11 / Q7 / Q8 / Q9 precedent). The shape that fixes the reflow
and changes nothing at rest:

1. `"plexMono Fallback Apple"` (Menlo, 400 / 500 / 600 900) and `"plexMono Fallback Windows"`
   (Consolas), **both restricted by `unicode-range` to exactly the subsets' 211 codepoints**;
2. `"plexMono Fallback Arial"` — Next's generated face re-declared by hand, verbatim
   (`src: local(Arial)`, `77.95 % / 20.91 % / 0 % / 131.49 %`) — **behind** them, so it only ever
   sees a character the subset lacks, which is exactly what it serves today.

Result: a character Plex has → Menlo at Plex's own advance (the fix); a character Plex lacks → the
same Arial face as today, in both states (no motion at all, and no resting change). Hangul inside a
`.mono` element is unaffected either way — it resolves to Apple SD Gothic Neo through the system
cascade before and after (measured).

## 3. Fitting the number against the real thing, before baking it

HEAD build on :3015, **412 × 915 @ DPR 2.625**, candidate CSS injected over the unchanged build,
bounding rect of every visible `body *` compared against the same page **with Plex loaded** (same
DOM, same data, same tab — so the only variable is the face). `moved` = rects differing > 0.5 px.

| candidate | `/` | `/stocks` | `/stocks/00547510` | `/portfolio` | `/ask` | `/events/…329` | `/stocks/00547510` @1280 |
|---|---|---|---|---|---|---|---|
| **today** (Arial @131.49 %) | **144** / 170.99 px | 3 / 12.30 | **57** / 19.00 (doc +19 px) | **75** / 13.70 | 1 / 12.30 | **39** / 24.88 | **29** / 17.61 |
| 97.00 % | 139 / 3.67 | 2 / 2.28 | 21 / 4.03 | 75 / 2.45 | 1 / 2.28 | 30 / 4.64 | 26 / 4.22 |
| 99.00 % | 16 / 0.91 | 1 / 0.56 | 10 / 0.99 | 11 / 0.61 | 1 / 0.56 | 25 / 1.19 | 14 / 1.03 |
| **99.66 %** | **0** / 0.235 | **0** / 0.016 | **0** / 0.047 | **0** / 0.141 | **0** / 0.015 | **0** / 0.078 | **0** / 0.047 |
| 100.00 % | 0 / 0.469 | 0 / 0.297 | **2** / 0.531 | 0 / 0.312 | 0 / 0.297 | **3** / 0.609 | **5** / 0.547 |
| 102.00 % | 130 / 3.14 | 1 / 1.94 | 20 / 3.44 | 75 / 2.08 | 1 / 1.94 | 30 / 4.20 | 23 / 3.58 |
| **noise** (loaded vs loaded) | 0 / 0.000 | 0 / 0.000 | 0 / 0.000 | 0 / 0.000 | 0 / 0.000 | 0 / 0.000 | 0 / 0.000 |

**99.66 % — the value the font tables give — is the value the browser agrees with**, on seven route ×
viewport cells, with a 0.000 px noise floor and both neighbours moving. 100 % (the number you would
pick if you assumed "monospace is monospace") misses on three of the seven.

## 4. Cold cache, before and after — the point of the slice

Local production builds, **412 × 915 @ DPR 2.625, 4× CPU, 150 ms / ≈1.6 Mbps, cache cleared, a fresh
tab per load, 3 loads per cell**. Every mono element on the page (selected by *computed* font-family,
re-scanned every 500 ms) sampled every animation frame; the metric is **max − min width per element
over the whole load**, i.e. exactly the motion R1 measured. All three runs of every cell returned
identical numbers, so the medians below are also the min and the max.

| route | mono elements | HEAD (:3015) worst element | fixed (:3014) | HEAD CLS | fixed CLS | `layout-shift` near a Plex `responseEnd` |
|---|---|---|---|---|---|---|
| `/` | 80 | **12.688 px** — 「718.1억원」 200.27 → 212.95 | **0.047 px** | 0.00126 | **0** | HEAD 2 entries · fixed **none** |
| `/stocks/00547510` | 27 | **17.609 px** — 「접수번호 20260806000329」 137.08 → 154.69 | **0.047 px** | 0.00184 | **0** | HEAD 2 · fixed **none** |
| `/portfolio` | 38 | **13.703 px** — `DDay__date` 92.42 → 106.13 | **0.016 px** | 0 (`hadRecentInput`) | **0** | HEAD 2 · fixed **none** |
| `/events/20260806000329` | 33 | **24.875 px** — 「DART 원문 20260806000329」 164.27 → 189.14 | **0.078 px** | 0.00132 | **0** | HEAD 3 · fixed **none** |

R1's named elements, on the HEAD control and then fixed: `Lookup__cval` 「0.0863800841」
**97.20 → 113.53** ⇒ **97.17 → 97.20 (0.031)**; `DDay__date` **92.42 → 106.13** ⇒ **0.016**;
`Lookup__cval` 「20%」 **27 → 39.48** ⇒ 0; `DDay__label` **30.61 → 36.02** ⇒ **0.016**;
`Portfolio__missedValue` 「679,575원」 **86.11 → 95.50** ⇒ 0. The 0.016–0.078 px residuals are
sub-pixel raster rounding of the same string, not motion: **the largest anywhere is 0.078 px**, well
inside the plan's 0.25 px bar.

Resource timing was the same on both builds (`IBMPlexMono_Regular` ~590 → ~1270 ms,
`SemiBold` → ~1370, `Medium` → ~1450 on the event page, `NotoSansKR` 291 kB → ~3000 ms), so the
comparison is like for like, and **`P4.F5` still holds**: Noto lands 1.7 s later than Plex and moves
nothing on either build.

## 5. RESPECT THE DESIGN — the warm page did not move a pixel

**Rect equality, fixed vs HEAD, fonts loaded** (every visible `body *`, star field and countdown
filtered), and the same probe used to see the **swap window** on each build (webfont blocked in a
fresh tab, cache cleared):

| route | vp | warm fixed vs HEAD | swap window, **fixed** | swap window, **HEAD** (the control) |
|---|---|---|---|---|
| `/` | 1280 | 0 moved / max **0.000** (328 el) | 0 / 0.234 | **286** / 23.25, doc 2217 → 2226 |
| `/` | 390 | 0 / **0.000** (331) | 0 / 0.235 | **144** / 12.69 |
| `/stocks/00547510` | 1280 | 0 / **0.000** (126) | 0 / 0.047 | **29** / 17.61 |
| `/stocks/00547510` | 390 | 0 / **0.000** (115) | 0 / 0.047 | **22** / 17.61 |
| `/portfolio` | 1280 | 0 / **0.000** (209) | 0 / 0.141 | **57** / 16.45 |
| `/portfolio` | 390 | 0 / **0.000** (195) | 0 / 0.141 | **128** / 112.00, doc 2257 → 2320 |
| `/events/…329` | 1280 | 0 / **0.000** (153) | 0 / 0.078 | **43** / 24.88 |
| `/events/…329` | 390 | 0 / **0.000** (141) | 0 / 0.078 | **39** / 24.88 |

Zero missing keys in every cell — nothing appears or disappears either.

**Screenshot equivalence** (`magick compare -metric AE`), viewport captures at the fold, animations
and the ticking countdown frozen, cropped to the emulated tile minus the macOS overlay-scrollbar
strip (1270 × 800 and 383 × 844):

| capture | AE (fixed vs HEAD) |
|---|---|
| `/stocks/00547510` @1280 · @390 | **0** · **0** |
| `/portfolio` @1280 · @390 | **0** · **0** |
| `/events/20260806000329` @1280 · @390 | **0** · **0** |
| `/` @1280 · @390, star field masked | **0** · **0** |
| *noise floor* — `/` fixed vs fixed, masked | **0** · **0** |
| *positive control* — fixed **loaded** vs fixed **webfont-blocked**, `/stocks/00547510` | **32,478,400** @1280 · **27,372,000** @390 |

The landing needed the mask and that is itself a measurement: **unmasked, two captures of the
same build differ by 50,800 px @1280 and 105,798 px @390** — the Cosmos star field alone (R1's idle
noise floor, now shown to bite screenshots as well as rect diffs). With
`[class*="Cosmos-module"], [class*="orbiter"], [class*="streak"] { visibility: hidden }` the
same-build floor is 0, and so is fixed vs HEAD.

**The swap window, seen.** The positive-control capture *is* that frame: the fixed build with Plex
blocked, at the throttled profile. Its diff against the loaded frame trims to
**891 × 698 at (184, 76)** @1280 and **341 × 586 at (16, 76)** @390 — the content column, and nothing
outside it: **glyph shapes differ (Menlo instead of Plex), geometry does not** (the rect table above
says 0 moved for the same pair). On HEAD the same pair moves 22–286 elements.

## 6. The built artefact, the console, and dev

**Built CSS** (`.next/static/chunks/*.css` of the fixed build copy) — the generated face is gone and
the three hand families are in its place:

```
@font-face{font-family:plexMono Fallback Apple;src:local(Menlo-Regular),local(Menlo Regular);font-weight:400;…;size-adjust:99.66%;ascent-override:102.85%;descent-override:27.59%;line-gap-override:0%;unicode-range:U+20-7E,U+A0-FF,U+2013-2014,…,U+20A9,U+20AC}
… (500, and 600 900 on Menlo-Bold) …
@font-face{font-family:plexMono Fallback Windows;src:local(Consolas);font-weight:100 500;…;size-adjust:100%;ascent-override:102.5%;descent-override:27.5%;…}
@font-face{font-family:plexMono Fallback Arial;src:local(Arial);ascent-override:77.95%;descent-override:20.91%;line-gap-override:0%;size-adjust:131.49%}
--font-plex-mono:"plexMono", plexMono Fallback Apple, plexMono Fallback Windows, plexMono Fallback Arial, ui-monospace, SFMono-Regular, SF Mono, Consolas, monospace
```

`grep -c "plexMono Fallback;"` (the generated face) → **0**, in the built CSS **and** in what dev
:3010 serves; `local(Arial)` appears exactly once, and it is ours. Nothing else in the bundle
changed: `notoSansKr`'s four Apple / two Noto / two Malgun faces are byte-identical, and no font
binary was added — the two files are the whole diff.

**Live face status on the running fixed build** (all four routes): `plexMono Fallback Apple`
400 / 600 900 **loaded**, `Windows` **error** (Consolas absent — the expected and harmless state,
identical in kind to Malgun's), `Arial` **loaded**.

**Console:** the F6 shim installed before navigation and proven live on every load. On the fixed
production build, all four routes: `["error: __probe_live__"]` — **nothing else, no hydration
warning**. On dev :3010 the shim plus React's own DevTools notice and `[HMR] connected`, nothing more.

**Dev runtime (:3010, the operator's own):** the new stack is live, `Lookup__cval` measures
**97.203 px** (Plex), and the `→` still measures **15.781 px in ArialMT** — the resting-identity
claim of §2.4(b), checked in the runtime the operator actually browses.

## 7. Production, and what was left running

**Production is read-only and stayed that way.** One `GET` of `https://jujutower.com/stocks/00547510`
and of the CSS chunk it names, with `curl` — no browser session, no account, no writes. It still
serves
`@font-face{font-family:plexMono Fallback;src:local(Arial);…;size-adjust:131.49%}`, i.e. **the defect
is live on `a74c58a` today**, exactly as `P12.R1` reported; no browser re-measurement was needed
because the HEAD control on :3015 reproduces R1's production deltas to the pixel (§1).

**Everything started was stopped.** `node server.js` on **:3014** (pid 14181) and **:3015**
(pid 13109) are killed and both ports answer nothing. The operator's dev stack was never restarted
and is **as found** (same `api` pid 60158, same `web` pid 61423, `make stack-status` identical to the
run's first line). Both build copies live in the session scratchpad outside the repo; no font binary,
no test file, nothing committed, and no workflow state command other than `validate`.

## 8. What this leaves open

- **Windows is still unclosed**, exactly as `P4.F5` left Malgun: `plexMono Fallback Windows` matches
  Consolas' vertical metrics and claims **no width** (`size-adjust: 100 %`). A Windows machine would
  close it with one measurement, and the arithmetic to test is in §2.3.
- **`U+2044 ⁄`** is the one subset codepoint Menlo lacks; it would fall to the Arial face in the swap
  window, as it does today. The product does not render it.
- **Nothing for `P12.S2`**: two frontend files, no new file, no env var, no font binary, no server
  involvement, no bytes on the wire (the faces are `local()`), and the served HTML is unchanged.
