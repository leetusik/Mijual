# Result — P10.S1 (brand binaries: land the mark, derive the white variant, rewrite the assets README)

- **status**: done
- **summary**: Landed the operator's PNG byte-exact as `juju-logo-source.png`, derived
  `juju-wordmark-black.png` (`-trim +repage`) and `juju-wordmark-white.png`
  (`-trim +repage -channel RGB +level-colors white,white +channel -define png:color-type=6`),
  and rewrote `frontend/public/assets/README.md` around three provenance classes. All four
  alpha proofs passed; the four `mijual-*` binaries are untouched, as instructed.
- **files_changed**:
  - `frontend/public/assets/juju-logo-source.png` (new, 235,823 b)
  - `frontend/public/assets/juju-wordmark-black.png` (new, 200,331 b)
  - `frontend/public/assets/juju-wordmark-white.png` (new, 25,674 b)
  - `frontend/public/assets/README.md` (rewritten)
  - `works/phases/active/P10/phase.md` (edited)
  - `works/phases/active/P10/slices/P10.S1/result.md` (this file)
- **validation**: all passed — see *Validation* below
  - `shasum -a 256` + `cmp` on the landed source vs the operator's file — **pass**
  - `identify` dimensions / RGBA / alpha — **pass**
  - distinct-alpha-value count preserved (42 ↔ 42) — **pass**
  - non-transparent RGB is `#FFFFFF` (white) / near-`#000000` (black) — **pass**
  - alpha channels byte-identical between the variants — **pass**
  - `python3 scripts/workflow.py validate` — **pass** (2 pre-existing P9 warnings, unrelated)
  - `cd frontend && npm run typecheck` (`tsc --noEmit`) — **pass**, clean
  - four `mijual-*.png` still present — **pass** (4/4)
- **deviations**: three, all deliberate and all recorded below (§Deviations) — the `-define
  png:color-type=6` addition to the plan's recolor command; two of the plan's stated geometry
  numbers corrected by measurement; the plan's "so a later slice can re-run the command and
  prove the file was not touched" turned out to be false as written and is documented honestly.
- **doc_impact**: two lines appended to `phase.md`
  - `frontend.md`: brand binaries replaced — the R2 ring wordmark retires for
    `juju-wordmark-white.png` (1213x319, 3.80:1), the assets README now records three
    provenance classes and verifies derivations by pixel signature rather than file sha256 (P10.S1)
  - `product.md`: the symbol mark / favicon gap that R2 closed is **open again** — the new mark
    is a Korean wordmark with a sparkle cluster and no ring, and it does not reduce to 32px (P10.S1)

---

## What landed

Three files in `frontend/public/assets/`, nothing wired, no TypeScript touched.

```
a22c9c4478e1a04a43022bf7c220d72581f62fade03072b053c20fd012ad8477  juju-logo-source.png      235,823 b  2560x1440 srgba
ecfe4e397cd1730191d224db8889a1b5cfd76b1fa5bf81da2019d7c0931cab70  juju-wordmark-black.png   200,331 b  1213x319  srgba
73b4005f9a192bff7595aed5e789a9f0a7aa9cdc3dff2ffe2d12c27c22883283  juju-wordmark-white.png    25,674 b  1213x319  srgba
```

The plan's filenames were kept as given. No concrete reason emerged to change them; `juju-`
echoes the operator's own delivery, `mijual-` is retired, and neither derivative is a ring.

## The exact commands I ran

Not the ones I meant to run — these, verbatim, from `frontend/public/assets/`, ImageMagick
**7.1.2-27 Q16-HDRI aarch64**:

```sh
cp ~/Downloads/juju_logo_no_back.png frontend/public/assets/juju-logo-source.png

magick juju-logo-source.png -trim +repage juju-wordmark-black.png

magick juju-logo-source.png -trim +repage \
       -channel RGB +level-colors white,white +channel \
       -define png:color-type=6 juju-wordmark-white.png
```

I derived from the **landed in-repo copy**, not from `~/Downloads/`, so the recorded commands
are re-runnable by a later slice after the operator's `~/Downloads/` is gone. The landed copy
is byte-identical to the original (proved below), so this changes nothing about the pixels.

## Validation, with output

### 1. The source landed byte-exact

```
$ shasum -a 256 ~/Downloads/juju_logo_no_back.png
a22c9c4478e1a04a43022bf7c220d72581f62fade03072b053c20fd012ad8477  /Users/sugang/Downloads/juju_logo_no_back.png

$ shasum -a 256 frontend/public/assets/juju-logo-source.png
a22c9c4478e1a04a43022bf7c220d72581f62fade03072b053c20fd012ad8477  frontend/public/assets/juju-logo-source.png

$ cmp ~/Downloads/juju_logo_no_back.png frontend/public/assets/juju-logo-source.png && echo "BYTE-IDENTICAL: yes"
BYTE-IDENTICAL: yes
```

Matches the plan's expected hash and its 235,823-byte count exactly.

### 2. `identify` — RGBA, alpha channel, 1213×319

```
$ identify juju-wordmark-black.png juju-wordmark-white.png
juju-wordmark-black.png PNG 1213x319 1213x319+0+0 8-bit sRGB 200331B
juju-wordmark-white.png PNG 1213x319 1213x319+0+0 8-bit sRGB  25674B

$ identify -format '%f  %wx%h  channels=%[channels]  colorspace=%[colorspace]  alpha=%A  depth=%[depth]\n' juju-wordmark-black.png juju-wordmark-white.png
juju-wordmark-black.png  1213x319  channels=srgba 4.0  colorspace=sRGB  alpha=Blend  depth=8
juju-wordmark-white.png  1213x319  channels=srgba 4.0  colorspace=sRGB  alpha=Blend  depth=8
```

### 3. Distinct alpha values preserved

```
$ magick juju-wordmark-black.png -alpha extract -format %k info:
42
$ magick juju-wordmark-white.png -alpha extract -format %k info:
42
```

42 ↔ 42, matching the source's 42 recorded in `phase.md` `## Decisions`.

### 4. Every non-transparent pixel's RGB

Full pixel enumeration (`magick f.png -depth 8 txt:-`), bucketed by alpha:

```
### juju-wordmark-black.png
  opaque(a=255)     count=7488    distinctRGB=19     R:[0..2]     pure#000000=4649
  partial(0<a<255)  count=22956   distinctRGB=648    R:[0..40]    pure#000000=0
  transparent(a=0)  count=356503  distinctRGB=3419   R:[36..255]  pure#FFFFFF=54980
  TOTAL=386947  distinct alpha values=42

### juju-wordmark-white.png
  opaque(a=255)     count=7488    distinctRGB=1      R:[255..255]  pure#FFFFFF=7488
  partial(0<a<255)  count=22956   distinctRGB=1      R:[255..255]  pure#FFFFFF=22956
  transparent(a=0)  count=356503  distinctRGB=1      R:[255..255]  pure#FFFFFF=356503
  TOTAL=386947  distinct alpha values=42
```

- **White**: all 30,444 non-transparent pixels are exactly `#FFFFFF` (`distinctRGB=1` in every
  bucket). Check passes unambiguously.
- **Black**: the opaque ink is `#000000`-ish — 19 distinct RGB values, all within `(2,2,2)`,
  4,649 of the 7,488 exactly `#000000`. Partial-alpha edges are dark too (max R `40`).
- The three bucket counts reproduce `P10.DECOMP`'s hand-measured 7,488 / 22,956 / 356,503
  exactly, in both files — independent confirmation that the trim did not move anything.

### 5. Identical alpha channels (the strongest check)

```
$ magick juju-wordmark-black.png -alpha extract -depth 8 gray:- | shasum -a 256
67d54de6bcdb2c5a85bd6d9f96c5ebf5af46594ff307af6bbc4551fd839ac020  -
$ magick juju-wordmark-white.png -alpha extract -depth 8 gray:- | shasum -a 256
67d54de6bcdb2c5a85bd6d9f96c5ebf5af46594ff307af6bbc4551fd839ac020  -

$ magick compare -metric AE -channel A juju-wordmark-black.png juju-wordmark-white.png null:
0 (0)
```

Byte-identical alpha, and `AE` `0` on the alpha channel. The recolor changed colour and
nothing else.

(Caution for later slices: `-alpha extract` to a **PNG** and hashing *that* gives different
hashes for the two files — `ac82a641…` vs `b27aaca6…` — even though `compare -metric AE` on
those same PNGs is `0`. That is the `png:tIME` stamp, not a pixel difference. Hash the raw
`gray:-` stream, as above.)

### 6. Workflow and build

```
$ python3 scripts/workflow.py validate
warning: slice P9.S1 has unknown kind 'research'; ...
warning: slice P9.S1B has unknown kind 'research'; ...
Workflow validation passed.

$ cd frontend && npm run typecheck
> mijual-frontend@0.1.0 typecheck
> tsc --noEmit
                      # clean, no diagnostics
```

Both P9 warnings pre-date this slice (`P9.S1`/`P9.S1B` carry a legacy `research` kind) and are
untouched by it.

### 7. The four `mijual-*` binaries are still present

```
$ ls frontend/public/assets/mijual-*.png | wc -l
       4
mijual-logo-ring-charcoal.png  mijual-logo-ring-white.png
mijual-wordmark-charcoal.png   mijual-wordmark-white.png
```

Confirmed by `git status`: no deletions staged or unstaged.

## Deviations

### D1 — I added `-define png:color-type=6` to the plan's recolor command

**Both** alpha-preserving forms the plan offered write a **GrayscaleAlpha** PNG, not RGBA:

```
alt-colorize.png (-fill white -colorize 100)                  graya 2.0  GrayscaleAlpha  Gray  21021 b  alpha=42
juju-wordmark-white.png (-channel RGB +level-colors … )       graya 2.0  GrayscaleAlpha  Gray  21021 b  alpha=42
```

ImageMagick sees that every RGB is now equal and silently reduces the colour type on write.
That is lossless, but it fails the plan's own check #1 ("`identify` reports RGBA with an alpha
channel") and would store the white mark as a different colour type from its black sibling,
making the alpha comparison in check #4 less direct.

`-define png:color-type=6` forces RGBA storage. It is **not** a re-encode or an optimisation —
it *suppresses* an automatic conversion. Proved pixel-neutral before adopting it:

```
$ compare -metric AE alt-colorize.png alt-ct6.png null:
0 (0)
```

Cost: 25,674 b instead of 21,021 b. I judged the explicit RGBA worth 4.6 KB. If the phase
review disagrees, re-running without the `-define` is a one-line change and pixel-identical.

Also noted while testing: the plan's two forms are pixel-identical but **not byte-identical to
each other** (`769d85de…` vs `7172ab51…`, both 21,021 b) — again `png:tIME`, not pixels.

### D2 — the plan's geometry numbers are wrong in the width, right in the height

The plan asked the README to state "the ink bbox is 946×161 at y=158 … 50.5% of the box
height". I measured it **twice, by independent methods**, and both disagree on the width:

```
$ magick juju-wordmark-black.png -crop 1213x162+0+157 +repage -trim -format '%wx%h offset=%X%Y\n' info:
1063x162  offset=+0+0                       # ImageMagick's own trim

# full pixel enumeration, alpha>0, rows below the blank band:
korean glyphs  : 29018 px  bbox x[0..1062] y[157..318] = 1063x162   (50.8% of 319)
sparkle cluster:  1426 px  bbox x[1029..1212] y[0..134] = 184x135
```

Measured: **1063×162 at (0,157)**, i.e. **50.8%**, not 946×161 at y=158 / 50.5%. The vertical
profile shows a clean 22-row empty band at `y=135..156` separating the sparkle from the glyphs,
so the boundary is unambiguous.

**The legibility arithmetic is unaffected** — 50.8% vs 50.5% gives 9.7px vs ~9.6px at h19 and
8.6px at h17 — so the operator question in `phase.md` stands exactly as written and I did not
touch it. The **width** understatement is material for layout, though: the nav mark goes from
the ring's 120×19 to 72×19, ~40% narrower. That is handed to S2 in its note, as a thing to look
at rather than a new operator question (S2 sees it painted; I only have arithmetic).

The README records the measured numbers and states the discrepancy explicitly rather than
silently overwriting `DECOMP`'s.

### D3 — "re-run the command and prove the file was not touched" is not true as stated

The plan wanted per-file sha256 recorded "so a later slice can re-run the command and prove the
file was not touched since". Re-running the exact commands produces **different file hashes**:

```
$ shasum -a 256 juju-wordmark-black.png  <re-derived copy>
ecfe4e397cd1730191d224db8889a1b5cfd76b1fa5bf81da2019d7c0931cab70  juju-wordmark-black.png
2ff40afcb993eaac2c0eb41194bf3b5547c467c5c453dfc8a1c460e8909d3160  repro-black.png

$ compare -metric AE juju-wordmark-black.png repro-black.png null:
0 (0)

$ identify -verbose juju-wordmark-black.png | grep -E "png:tIME|signature"
    png:tIME: 2026-08-29T16:13:12Z
    signature: c1caf123e4f302f9d6c21b3b859454364a12865afa9a1362764b916b9494ac58
$ identify -verbose repro-black.png | grep -E "png:tIME|signature"
    png:tIME: 2026-08-29T16:17:38Z
    signature: c1caf123e4f302f9d6c21b3b859454364a12865afa9a1362764b916b9494ac58
```

Identical pixels, different container. The plan also forbids stripping metadata, so I could not
make the file hash reproducible even if I wanted to — the two instructions are in tension and I
resolved it in favour of the no-stripping rule.

The README therefore records **two** hashes per derivative and says what each proves:

- **file sha256** — the landed file was not touched *in this repository*;
- **`identify -format '%#'` pixel signature** — the *derivation* is reproducible
  (`c1caf123…` black, `b8e8aeda…` white). `magick f.png -depth 8 RGBA:- | shasum -a 256` and
  `compare -metric AE` give the same guarantee.

A later slice that re-derives and finds a file-hash mismatch must **not** "fix" it by
overwriting; this is now a `## Decisions` line in `phase.md`.

## The README rewrite

`frontend/public/assets/README.md` was rewritten, not patched. Its old frame — "these five
files are exported from the design project, not regenerable here, do not edit or re-export" —
is false for everything this slice landed, and copy-pasting it would have made the repo assert
a provenance it cannot back. The new frame is **three provenance classes** stated up front:

- **A — design-project export**: the font, and the four retired `mijual-*` PNGs. Untouchable,
  not regenerable here. Old rules carried across verbatim.
- **B — operator delivery**: `juju-logo-source.png`. Landed byte-exact, also not regenerable
  here, but it never came from the design project and the README no longer pretends it did.
- **C — repo-generated derivative**: the two wordmarks. Regenerable — and *that* is their form
  of trust, a different one from A and B.

Also in there, per the plan: the exact commands and the ImageMagick version; both hash kinds;
the alpha-flattening trap written down so the next person does not step in it; the measured
geometry table with the h19/h17 arithmetic; the reopened symbol-mark gap; the favicon evidence;
the four `mijual-*` rows with a note that **S2** deletes them; and the font section, its row,
its sha256 (`9599f12f…`, re-verified unchanged) and its "how the font is reached" section
carried across untouched.

The favicon disclosure is now evidence-backed rather than asserted: a favicon box is square,
and fitting a 3.80:1 mark into 32×32 by width leaves the artwork 8.4px tall, of which the
Korean band is 4.3px and each of the six syllables ~4.7px wide. I did **not** create a favicon
or crop one, per the plan and the README's own standing rule.

## Things I deliberately did not do

- **Did not delete the four `mijual-*.png`.** Per the plan's override. Confirmed by grep that
  `frontend/components/chrome/copy.ts:32` (`RING_WORDMARK_WHITE = "/assets/mijual-logo-ring-white.png"`)
  is their **only** live consumer — the other three are already dead weight — so deleting them
  before S2 rewires would have shipped a broken nav and footer image on every page.
- **Did not wire anything, and touched no TypeScript, CSS or config.** `npm run typecheck` is
  the cheap proof.
- **Did not decide whether the mark reads at h19/h17.** Arithmetic is in the README and the S2
  note; the judgement is S2's to report and the operator's to make at the gate.
- **Did not add an operator question.** Everything I found either confirms an existing one (the
  chrome heights) or is a fact for S2, not a decision for the operator.

## Two small things for whoever comes next

1. **`P10.S1`'s own `slice.json` name still reads "… retire the mijual-* set"**, which is no
   longer what this slice did — it shows in the generated `## Slices` table. I did not edit it
   (engine/orchestrator state, and the plan's override is recorded in `phase.md` anyway). The
   orchestrator may want to correct the name or let the `--outcome` line carry the correction.
2. **`juju-logo-source.png` and `juju-wordmark-black.png` are unreferenced but publicly served**
   — everything under `public/` gets a URL, so `/assets/juju-logo-source.png` is fetchable. Both
   are the operator's own brand art, nothing sensitive, and neither is ever requested by the
   app, so this costs deploy size (~436 KB) and nothing else. Recorded because "unreferenced"
   and "unreachable" are not the same thing.

## Notes recorded in `phase.md` (not repeated here)

- `## Decisions`: the settled recolor command; the three provenance classes; derivations are
  verified by pixel signature, not file sha256; and the **corrected mechanism** for why the
  black variant must stay off the cosmos chrome (it is the fully-transparent pixels that carry
  near-white RGB, not the partial-alpha edge — the conclusion was right, the reason was not).
- `## Doc impact`: the two lines quoted in the verdict block above.
- `## Notes for later slices`: the consumed `(from P10.DECOMP, for P10.S1)` note removed; a new
  `(from P10.S1, for P10.S2)` note added with the filenames, the natural pair `{1213, 319}`, the
  retirement handoff and why it is same-commit, the measured geometry, the h19/h17 arithmetic,
  the ~40% narrower nav mark, and the false provenance sentence in `Wordmark.tsx`'s header.
- `## Now` rewritten. Notebook is **188 lines / 15,420 b** against the 200 / 16,384 budget; I
  compressed `## Decomposition`'s "why this shape" prose (fully preserved in
  `slices/P10.DECOMP/result.md`) and corrected its now-stale S1/S2 ownership rows to buy S2 room.
