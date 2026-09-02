# P4.F8 — result

- **status:** done
- **summary:** The chrome loads a **display-size wordmark**: one recorded class-C ImageMagick
  command turns the 1247×371 / 21,920 b master into `juju2-wordmark-white-273-73c23508.png`
  (**273×81, 6,405 b — −15,515 b, −70.8 %**, on every cold load of every route), named by the first
  eight hex of its own **pixel signature** so the name changes when the pixels do. `next.config.ts`
  now gives `public/` cache lifetimes it never had: a year + `immutable` on that one name-versioned
  path, **one week + `stale-while-revalidate=86400`** on every fixed name under `/assets/*` and
  `/foundations/*` (production served both at Cloudflare's default `max-age=14400`, because Next
  sends no `Cache-Control` for `public/` at all). **The mark does not move**: measured in real
  headful Chrome 152 over CDP on a local production build at 1280 and 390 × DPR 1/2/3, `x`, `y`,
  `height` and both `translateY` offsets are identical, the rendered *width* grows **+0.250 px**
  (nav) / **+0.219 px** (footer) because an integer raster cannot hold both aspect ratios, and the
  rendered ink bounding box is identical everywhere except the footer's outermost sparkle dot, which
  sits **one device pixel** further right at DPR 2 and 3. The new raster measures **crisper, not
  softer** at DPR 3.
- **files_changed:** `frontend/public/assets/juju2-wordmark-white-273-73c23508.png` (new),
  `frontend/public/assets/README.md`, `frontend/components/chrome/copy.ts`,
  `frontend/components/chrome/Wordmark.tsx` (comment only), `frontend/next.config.ts`,
  `works/phases/active/P4/phase.md`, `works/phases/active/P4/slices/P4.F8/result.md`
- **validation:** `magick identify` → `273x81 srgba 4.0 opaque=False 6405 bytes`, trim
  `273x81+0+0`; the README's verify block re-derives the file into a scratch path with
  **`compare -metric AE` = 0**, the same pixel signature `73c23508…` **and** (because `-strip` drops
  `png:tIME`) the same sha256 `ae29fe47…`; `curl -sI` on the local production build returns the
  intended `Cache-Control` **per path** (table below) with `/_next/static/*` unchanged and exactly
  one `Cache-Control` header on each; 12 before/after screenshot pairs (2 viewports × 3 DPRs × nav
  and footer) with ink-box and per-pixel analysis; the wordmark request on `/`, `/stocks` and `/ask`
  is the new file and nothing else under `/assets/` but the launcher's symbol; `npm run typecheck`
  → clean; `npm run smoke` → **22/22**; `npm run build` in a scratch copy → **exit 0**;
  `python3 scripts/workflow.py validate` → **passed** (pre-existing `oversized_doc_sections`
  warning only); `git diff --stat` → the five frontend paths + `phase.md` + this file (plus the
  generated `works/` files `start-slice` already touched). **No deploy, nothing on the box,
  production never contacted; the operator's 3010/8010 stack answered 200 before and after and was
  never touched.**
- **deviations:** eight, each with its reason in § *Deviations* below — (1) the file is **6,405 b**,
  not the plan's expected 3–5 KB, and **no** palette tool was added; (2) two flags the plan did not
  name were added and both are *measured* (`+level-colors white,white` restores this directory's
  white-everywhere invariant, `-quality 95` is 377 b of lossless container); (3) the name carries a
  **pixel-signature** hash rather than the bare `-273` the plan offered first; (4) `Wordmark.tsx`
  got a **comment-only** edit (two paragraphs had become false); (5) before/after was produced by a
  DOM swap inside **one** build rather than two builds; (6) the first screenshot pass was
  **discarded** — a CDP trap double-scaled it; (7) the footer's ink box **does** move one device
  pixel on its right edge at DPR 2/3, against the plan's 「must not move by a pixel」; (8) the
  master is **21,920 b**, so the saving is 15,515 b and not the R1 note's 「~20 KB」.
- **doc_impact:** three lines appended to `phase.md` — `frontend` (the new class-C derivative + its
  README record + `WORDMARK_NATURAL` 273×81 + the new `headers()` block), `operations` (a reader's
  browser now caches `/assets/*` and `/foundations/*` for a week; what to do when a fixed-name asset
  must change urgently), and `qa` (the `## Regression Checklist` P10 rebrand line asserts the old
  src, natural size and both rendered widths, and is false in four places once `P4.S9` ships).
- **doc_versions:** n/a — deferred to a docs phase (this is not a review slice).
- **review_verdict:** n/a
- **walkthrough:** none
- **explain:** n/a

---

## Instrument, runtime, and what was not touched

**Instrument.** Real **Google Chrome 152.0.7977.65**, headful, launched through LaunchServices with
a **throwaway profile** and a fresh port — `open -na "Google Chrome" --args
--remote-debugging-port=9362 --user-data-dir=<scratchpad>/f8prof2 …` — driven over the DevTools
protocol by `scratchpad/f8_cdp.mjs`, a dependency-free driver on node 24's global `WebSocket`. This
is the fallback instrument `## Operator Runtime` records: **Aside is not installed on this Mac and
no agent Aside account exists**, so it was not used and nothing was registered. Both browsers this
slice launched were closed with `Browser.close`; the operator's own Chrome profile was never opened.

**Runtime.** The **local production build**, as `P4.R1`/`P4.F5`/`P4.F6` did it and for the same
reason (production is read-only in this slice): `frontend/` copied to `scratchpad/f8fe`, built with
`NEXT_PUBLIC_SITE_URL=https://jujutower.com MIJUAL_API_ORIGIN=http://127.0.0.1:8010 npm run build`,
`public/` and `.next/static` staged into `.next/standalone`, served by `node
.next/standalone/server.js` on **:3014** against the dev API on 8010. Next 16 refuses `next start`
under `output: "standalone"`, so this is also what the box runs. The repo tree was never built into
(`frontend/.next` is still the dev server's). Server and browsers are stopped; :3014 and both CDP
ports are free.

**Not touched:** production, the box, the operator's dev stack (3010/8010 answered 200 before and
after), `frontend/.next`, and any file outside the five frontend paths + `phase.md` + this file.

## 1. The derivative

```sh
magick public/assets/juju2-wordmark-white.png -filter Lanczos -resize 273x \
       -channel RGB +level-colors white,white +channel \
       -strip -depth 8 -quality 95 -define png:color-type=6 \
       public/assets/juju2-wordmark-white-273-73c23508.png
```

**273 wide because that is 3× the largest render** — the nav paints 91 CSS px, so 273 device px on a
DPR-3 phone, and `273 × 371/1247 = 81.2 → 81`. Source: the class-**C** master rather than the class-B
delivery, deliberately — the master is the mark **as R18 signed it** (trimmed, recoloured, spliced),
so deriving from it is one step and reproduces the signed artwork exactly; going back to
`juju2-logo-source.png` would mean re-running the trim/recolour/splice and re-proving them. This is
the same class-C-from-class-C move `P4.S5`'s share card made from the same file.

| | value |
|---|---|
| geometry | `273x81`, `srgba 4.0`, 8-bit, `opaque=False`, trim `273x81+0+0` |
| size | **6,405 b** (master 21,920 b) — **−15,515 b, −70.8 %** |
| sha256 | `ae29fe47fe3f716e44547b49e84e47a7ea7551b1a73a32560c4b178dcd3f8d98` |
| pixel signature | `73c235084d3f0f539568b95a0a4c020d7b1913d1188902b5c178b35cb24c5728` |
| ink | 5,713 non-transparent px of 22,113, 1,577 fully opaque, **255** distinct alphas, **1** distinct RGB |

**Four flags, four measurements** (all four are in the README, in its own style):

1. **`-filter Lanczos`, because the default is not Lanczos.** ImageMagick picks **Mitchell** for an
   image with an alpha channel: an unspecified `-resize 273x` is `compare -metric AE` **0** against
   an explicit `-filter Mitchell` and visibly different from Lanczos (5,917 b vs 7,188 b unguarded).
   Lanczos is the sharper of the two and keeps the glyph band's ink weight — the property R18 was
   re-cut for (「previous one was so thin」).
2. **The white guard is not cosmetic.** Without `-channel RGB +level-colors white,white +channel`
   the resize returns the transparent region as **RGB (0,0,0)** on 13,516 px (plus one `#767676`),
   breaking this directory's recorded 「every pixel is exactly `#FFFFFF`, transparent ones included」
   invariant — which exists precisely so a hard downscale cannot bleed dark into the ink edge. With
   it: **1 distinct RGB**, and the alpha channel is **bit-identical** to the unguarded output
   (`sha256` of `-alpha extract` equal), so the guard changed no visible pixel.
3. **`-strip` makes this derivation byte-reproducible** — a first in this directory, where
   `png:tIME` normally kills the file hash. Two runs a second apart: identical sha256. The README's
   rule (verify by pixel signature) still governs; the file hash is a bonus, and the verify block
   shows both.
4. **`-quality 95` is lossless and worth 377 b** (6,405 vs 6,782): zlib level 9 + adaptive PNG
   filtering, `AE` 0 and the same pixel signature.

**The Lanczos ring is invisible.** The master's 30 fully-transparent rows between the sparkle cluster
and the glyph band become one fully-transparent row plus overshoot at **peak alpha 4/255 (1.6 %)**,
against 255 for the ink beside it. The band's own edge lands at row **42.57 of 81** — exactly the
master's `195/371 = 52.56 %`.

## 2. The swap, and the geometry in a real browser

`WORDMARK_WHITE` now points at the new file and `WORDMARK_NATURAL` is `{width: 273, height: 81}`.
`INK_OFFSET_PX` (`27 → 8`, `24 → 6`) is **untouched** and still correct: the offsets are vertical,
the band is still bottom-flush and still 47.4 % of the box, and both heights are unchanged.

Measured on `/stocks` (no starfield, so the crops are noise-free), every animation and transition
frozen by injected CSS, `document.fonts.ready` awaited and `img.decode()` awaited on both variants:

| surface | before (`…white.png`, natural 1247×371) | after (`…-273-73c23508.png`, natural 273×81) |
|---|---|---|
| nav h27 | `x=104/16, y=4`, **90.750 × 27**, `translateY(-8px)` | `x=104/16, y=4`, **91.000 × 27**, `translateY(-8px)` |
| footer h24 | `x=104/16, y=846/674.055`, **80.664 × 24**, `translateY(-6px)` | same `x`/`y`, **80.883 × 24**, `translateY(-6px)` |

Identical at **1280 and 390** and at **DPR 1, 2 and 3** — twelve readings, the same two numbers.
`x`, `y` and `height` never move; the width grows **+0.250 / +0.219 px** because `273/81 = 3.3704`
against the master's `3.3612` and no integer raster holds both. `.brand` is `flex:none` with no
fixed width and the mark is flush-left in both surfaces, so nothing reflows.

**In the rendered pixels** (crop = the mark's own rect + 4 px of padding, captured at
`deviceScaleFactor` and `clip.scale = 1`; ink box = every pixel more than 8/255 from the modal
background, in device px):

| viewport | DPR | surface | ink box after / before | Δ | pixels differing / total | max Δ | mean Δ | mean \|∂x\| after / before |
|---|---|---|---|---|---|---|---|---|
| 1280 | 1 | nav | `(4,4,94,30)` / `(4,4,94,30)` | **0,0,0,0** | 975/4,017 | 119 | 3.81 | **15.00 / 14.69** |
| 1280 | 1 | footer | `(4,4,84,27)` / `(4,4,84,27)` | **0,0,0,0** | 821/3,348 | 129 | 5.73 | **15.09 / 14.60** |
| 1280 | 2 | nav | `(8,8,189,61)` / `(8,8,189,61)` | **0,0,0,0** | 3,313/16,068 | 70 | 1.81 | 8.40 / 8.40 |
| 1280 | 2 | footer | `(8,8,169,55)` / `(8,8,168,55)` | 0,0,**+1**,0 | 2,658/13,392 | 215 | 5.43 | 8.89 / 8.94 |
| 1280 | 3 | nav | `(12,12,284,92)` / `(12,12,284,92)` | **0,0,0,0** | 5,019/36,153 | 75 | 1.30 | **5.98 / 5.73** |
| 1280 | 3 | footer | `(12,12,254,83)` / `(12,12,253,83)` | 0,0,**+1**,0 | 5,386/30,132 | 242 | 5.95 | 6.13 / 6.10 |

390 reproduces all six rows to within 4 differing pixels (the mark is placed with no viewport
branch, so this is the expected result and it is why both viewports are reported together).

**What that says.** The ink's **left, top and bottom edges never move, anywhere.** The nav's right
edge never moves either. The footer's right edge — the outermost dot of the sparkle cluster — lands
one device pixel further right at DPR 2 and 3, which is the +0.219 px wider render plus a sharper
edge crossing the threshold; at DPR 1 it does not move at all. The per-pixel differences are
antialiasing: ~24 % of the crop's pixels at DPR 1, falling to **14 % (nav) / 18 % (footer)** at
DPR 3 as the source approaches 1:1 with the device grid. The **mean absolute horizontal gradient** —
a crispness proxy — is **higher** for the new file in four of the six rows, exactly equal in one
(DPR 2 nav) and 0.6 % lower in one (DPR 2 footer), so the plan's
「must not look softer at DPR 3」 is met with a number: 5.98 vs 5.73 on the nav at DPR 3. Eyeballed
at 4× on both surfaces at DPR 1 and DPR 3: same glyphs, same star, same five dots, same positions;
the new raster is very slightly brighter-edged.

**Requests.** On `/`, `/stocks` and `/ask` the only `/assets/` requests are
`juju2-wordmark-white-273-73c23508.png` (200, `content-length: 6405`) and, where the launcher
renders, `juju2-symbol-white.png`. The master is not fetched by any page.

## 3. Cache headers, per path, on the local production build

`curl -sI http://127.0.0.1:3014<path>`:

| path | `Cache-Control` | was |
|---|---|---|
| `/assets/juju2-wordmark-white-273-73c23508.png` | **`public, max-age=31536000, immutable`** | (did not exist) |
| `/assets/juju2-wordmark-white.png` | `public, max-age=604800, stale-while-revalidate=86400` | Cloudflare default `max-age=14400` |
| `/assets/juju2-symbol-white.png` | `public, max-age=604800, stale-while-revalidate=86400` | `max-age=14400` |
| `/assets/juju2-icon-192.png`, `/assets/juju2-icon-512.png` | `public, max-age=604800, stale-while-revalidate=86400` | `max-age=14400` |
| `/foundations/tokens.css` | `public, max-age=604800, stale-while-revalidate=86400` | `max-age=14400` |
| `/_next/static/chunks/*` | `public, max-age=31536000, immutable` | unchanged (framework) |

Exactly **one** `Cache-Control` header on each response: Next applies every matching entry in order
and a later one overwrites the same header name, which is why the exact-path `immutable` rule is
listed **last** and why the block says so in a comment. The two 192/512 tiles are referenced by
**fixed** name from `app/manifest.ts`, so they are *not* in the immutable set — the plan asked that
this be checked, and it was.

Two `Cache-Control`s in the build are **not** this slice's and were left alone:
`/opengraph-image.png` and `/icon.png` answer `public, max-age=0, must-revalidate` because they are
Next **metadata routes**, not `public/` files.

## 4. What this slice does not do

- **No Core Web Vitals metric moves.** The wordmark is never the LCP element (`P4.R1`: LCP is text
  on all 72 loads), it is not render-blocking, and it does not shift layout. The gain is 15,515 b
  off every cold page load on every route, plus the end of a 4-hourly revalidation of five static
  files.
- **Nothing is deployed.** `P4.S9` releases F5 + F6 + F8 (+ F10) together, before the
  2026-09-07 11:00 KST freeze.
- **No test file**, per the contract: this is verified live, in a browser, on a production build.

## Deviations

1. **Size: 6,405 b, not the plan's expected 3–5 KB.** No palette reduction was attempted and **no
   tool was added** (the plan's own instruction). The three lossless levers available were used and
   measured — `-quality 95` (−377 b) and the white guard (−377 b more, by making the transparent
   region uniform) — and 6,405 b for 22,113 px of 255-level alpha is where a lossless RGBA PNG lands.
2. **Two flags the plan did not name.** `-channel RGB +level-colors white,white +channel` and
   `-quality 95`. Neither is a judgment call: both are measured above, and the first *restores* a
   property this directory already records rather than introducing one.
3. **The name carries a pixel-signature hash.** The plan offered `juju2-wordmark-white-273.png`
   **or** a content-hash suffix; the hash was chosen because step 3 puts a **year of `immutable`** on
   this path, and `-273` alone would not change if the mark were ever re-cut. The **pixel** signature
   was preferred over the file sha256 for the same reason the README prefers it everywhere: it
   changes when what the reader sees changes, and survives a future ImageMagick writing a different
   container.
4. **`Wordmark.tsx` was edited — comment only, no code.** The plan permits touching it 「only if the
   offsets demand it」 and the offsets did not. But two of its paragraphs asserted 「the intrinsic
   1247×371 (3.3612:1) travels as the `width`/`height` attributes」 and 「never re-encoded」 without
   qualification, and both became false the moment `copy.ts` changed. A false comment in the one file
   a reader consults about this mark is a real cost, so both paragraphs were corrected in place and
   the change is recorded here.
5. **Before/after came from one build, by DOM swap.** Both files ship in `public/`, so the 「before」
   variant is produced by setting `src` + `width` + `height` back to the master and awaiting
   `decode()` in the same tab, same paint, same fonts, same layout. Two builds would have introduced
   a second variable for nothing; the swap isolates exactly the bytes under test.
6. **The first screenshot pass was discarded.** `Page.captureScreenshot`'s `clip.scale` multiplies
   `Emulation.setDeviceMetricsOverride`'s `deviceScaleFactor` rather than replacing it, so
   `scale: dpr` at `dsf: dpr` rasterises at **dpr²** — the 「DPR 3」 crops came back 9× (a 103 CSS px
   clip as 927 px) and would have drawn a 273 px source at nine times its size, inventing a softness
   no real device sees. Re-run with `scale: 1`; the trap is commented in the driver.
7. **The footer's ink box moves one device pixel** on its **right** edge at DPR 2 and 3, against the
   plan's 「the bounding box of the ink must not move by a pixel」. It is reported rather than papered
   over: it is 0.5 / 0.33 **CSS** px, it is the outermost sparkle dot's antialiased edge, it follows
   arithmetically from a rendered width that is 0.219 px wider, and left/top/bottom and the entire
   nav are pixel-identical at every DPR. Removing it would mean giving the file a non-integer width.
8. **The master is 21,920 b.** The `(from P4.R1, …)` note said 22,408 and 「~20 KB」; the file on disk
   is 21,920 and the saving is **15,515 b**. Corrected in the note itself and in `## Decisions`, the
   way `P4.F6` corrected R1's payload estimate.

## Artefacts (all outside the repo, session scratchpad)

`f8_cdp.mjs` (the CDP driver), `f8fe/` (the built copy), `f8shots2/` (the 24 accepted crops +
`f8_cdp.json`), `f8shots/` (the discarded double-scaled pass, kept only as the evidence for
deviation 6), `cmp_{nav,footer}_dpr{1,3}.png` (the 4× eyeball composites), `f8_build.log`,
`f8_web3014.log`, `f8/` (the derivation experiments: filter, guard, quality and reproducibility
comparisons). Nothing was written into the repository except the five frontend paths, `phase.md`
and this file.
