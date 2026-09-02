# Binary design assets — three kinds of provenance, and they are not interchangeable

This directory holds files with **three different provenance stories**, and the whole point of
this README is to say which story each file has. Confusing them is how a derivative gets treated
as untouchable, or an untouchable export gets "regenerated".

| provenance class | what it means | files |
|---|---|---|
| **A — design-project export** | produced outside this repo, in the Claude Design project **"Mijual Design System"**, and **not regenerable here**. Copied in byte-for-byte. A diff is a design change. | **none remain in this directory.** The four `mijual-*.png` were class A and were deleted by `P10.S2`; `fonts/PretendardVariable.woff2` and `../foundations/fonts.css` were class A and were deleted by `P10.S7`. All are recorded below. `../foundations/tokens.css` is still class A and is still frozen. |
| **B — operator delivery** | handed over directly by the operator, outside the design project. Landed byte-exact and never re-encoded. Also not regenerable here. | `juju2-logo-source.png`, `juju2-symbol-source.png` |
| **C — repo-generated derivative** | produced **in this repository** by one recorded ImageMagick command from a class-B file — or, once (the share card), from another class-C file. **Regenerable here** — that is the trust: re-run the command and compare. | `juju2-wordmark-white.png`, `juju2-symbol-white.png`, the three favicon tiles in `../../app/`, (`P4.S5`) `../../app/opengraph-image.png` + `juju2-icon-192.png` + `juju2-icon-512.png`, and (`P4.F8`) `juju2-wordmark-white-273-73c23508.png` — **the file the chrome actually loads** |

## The brand mark (2026-08-31, `P10.S7`; re-derived by `P10.F1` for R18) — the second delivery

The operator delivered two files directly — **not** exports from the Claude Design project, so the
"byte-for-byte from the design project" rule does not describe them or their derivatives. Both
originals live outside the repository and will not survive, so both are landed here unreferenced:
the immutable ancestors every other brand file is derived from.

**What the mark is:** the Korean wordmark **주주의관제탑** with a small **sparkle cluster at the
upper right**, on transparency. It has **no ring** and no latin lettering. Any code, comment or doc
reasoning about "the MIJUAL wordmark with its orbital ring" is describing a mark that no longer
exists.

**What the symbol is:** that same sparkle cluster, delivered on its own as a square export. R17
made it a **first-class mark** — one star and five dots, ink box **222×165** — and it is the
launcher's mark and the favicon. It is the same cluster at the same scale as the one inside the
wordmark: both measure **2,481 ink pixels**, which is how we know it was not redrawn.

| file | class | what it is | format |
|---|---|---|---|
| `juju2-logo-source.png` | B | the operator's wordmark delivery, byte-exact and **unreferenced** — kept only as the ancestor | PNG 1614×1076 sRGBA, 239,858 b |
| `juju2-symbol-source.png` | B | the operator's symbol delivery, byte-exact and **unreferenced** — same role | PNG 278×278 sRGBA, 31,674 b |
| `juju2-wordmark-white.png` | C | the wordmark trimmed to its ink, recoloured **white**, and **spliced** to drop the quarter-em space inside it (R18) — the **master**, and every other wordmark file's ancestor. It was 「the only image the chrome loads」 until `P4.F8`; the chrome now loads the display-size derivative below, and this file is not requested by any page | PNG 1247×371 sRGBA, 21,920 b |
| `juju2-wordmark-white-273-73c23508.png` | C | **what the chrome loads since `P4.F8`** — the master resized to 3× its largest render, name-versioned by its own pixel signature. Same mark, same place, same size on screen; 6,405 bytes instead of 21,920 | PNG 273×81 sRGBA, 6,405 b |
| `juju2-symbol-white.png` | C | the symbol **cropped** to its real ink and recoloured white — the launcher paints it with a CSS `mask`, and the favicon tiles are composited from it | PNG 222×165 sRGBA, 3,232 b |

**There is no black variant, and that is deliberate.** The retired first mark had one for light
surfaces; nothing ever referenced it, R17 names no such variant, and the one mark that genuinely
needs to change colour — the symbol — is painted with `mask` + `currentColor` instead, so a single
asset serves every colour. Adding a second recolour now would be a file with no consumer.

### Exactly how the derivatives were produced

Run from this directory, ImageMagick **7.1.2-27 Q16-HDRI aarch64**. The symbol's command is R17
§0's verbatim (with the operator's filenames replaced by the landed class-B names — same bytes); the
wordmark's is R17 §0's plus the R18 splice stage, which is the only change either has had:

```sh
# wordmark — -trim gives exactly 1292x371+238+255, then the splice drops 45 columns
magick juju2-logo-source.png -trim +repage \
       -channel RGB +level-colors white,white +channel \
       \( -clone 0 -crop 530x371+0+0 +repage \) \
       \( -clone 0 -crop 717x371+575+0 +repage \) \
       -delete 0 +append +repage \
       -define png:color-type=6 juju2-wordmark-white.png

# symbol — NEVER -trim; crop the real ink explicitly (see the warning below)
magick juju2-symbol-source.png -crop 222x165+39+62 +repage \
       -channel RGB +level-colors white,white +channel \
       -define png:color-type=6 juju2-symbol-white.png
```

Nothing was resized, optimised, re-compressed, or had metadata stripped. `530 + 717 = 1247`;
`575 = 530 + 45`.

**Why 45 columns, and why cutting them is safe** (R18 §①, `docs/reference/design/rounds/18-p10-review/`).
The artwork spelled the name with a **quarter-em space between 「의」 and 「관」** — the operator saw it
as 「주주의 관제탑」. It is measurable, not a matter of taste: the mark's Hangul **advance width** is
**183.0px** (the ink-centre distance between the two identical 주 glyphs), and 의→관 measures
**228.5px** — an excess of **45.5px = 0.249em**, and 관·제·탑 all carry the same `+40..+56px` offset
against a 183 grid, so it is one shifted space rather than one bad kerning pair. The cut is a splice,
not a resize: `x=519..588` (**70 columns**) has **zero alpha at every one of the 371 rows**, and the
command removes `x=530..574` from strictly inside that band — 11 columns of clearance on the left,
14 on the right. The sparkle cluster starts at `x≥1070` in the old raster, so nothing it owns is
touched (its own box is `x=1070..1291` in the old raster, all of it above the glyph band).
Everything right of the cut simply moves 45px left, which is why the mark stays flush to the box's
top and right. −40 was rejected (the gap still reads as a space at 30px) and −52 (18px,
tighter than the 19px between 주 and 주, so 「의관」 would collide).

### Four traps, all of them real, all of them silent

**1. `-trim` on the symbol keeps ghost ink.** The delivered file carries two low-alpha fragments at
the bottom left — `(52,257) 24×21 mean alpha 19` and `(0,265) 24×13 mean alpha 35`, **89 px
together**. Because their alpha is greater than zero, `-trim` preserves them and reports
**261×216**; the white recolor then turns them into visible 7–14 % white smudges in the bottom-left
of every favicon and of the launcher, on the cosmos surface. The crop removes them by construction.
Verified on the landed file: the crop **re-trims to `222x165+0+0`** — tight, nothing left over — and
`2,570 − 2,481 = 89`, exactly the two fragments. **`261×216` is a measurement of the ghosts and must
not appear anywhere.**

**2. The wordmark's 「의」 counter can be filled, and it only breaks in white.** The operator's first
delivery (`juju2.png`) had **2,864 opaque near-white pixels** inside 「의」's ㅇ. An alpha-preserving
recolor keeps opaque pixels opaque, so on cosmos the ㅇ renders as a **solid white blob** — while the
*black* variant looks perfectly fine, because it is white-on-white there. The adopted source
(`juju2_2.png` → `juju2-logo-source.png`) has **0**. Re-check after any re-derivation:

```sh
# must print 0. Anything else means the wrong source file was used.
magick juju2-logo-source.png -trim +repage -depth 8 RGBA:- | python3 -c "
import sys; b=sys.stdin.buffer.read()
print(sum(1 for i in range(0,len(b),4) if b[i+3]==255 and min(b[i:i+3])>=240))"
```

A second, independent check on the derivative itself: flood-filling the transparent region from the
border leaves **2,845 enclosed pixels in two islands** — `50×46 at (402,226)` (「의」's ㅇ) and
`69×15 at (969,335)` (「탑」's ㅂ). Two counters, both punched through. The second island's `x`
**moved 45 left** with the R18 splice (it was `(1014,335)`); the first is left of the cut and did not
move.

Run it as a before/after guard on the *derivative*, which is the form R18 needs — a re-derivation
must leave both islands exactly as they were:

```sh
# 481 and 15. Both counts are of the ENCLOSED islands' bounding boxes, which clip a few
# border ink pixels — that is why they are not 0, and why only their CONSTANCY matters.
magick juju2-wordmark-white.png -crop 50x46+402+226 +repage -alpha extract -threshold 0 \
       -format '%[fx:int(w*h*mean+0.5)]\n' info:
magick juju2-wordmark-white.png -crop 69x15+969+335 +repage -alpha extract -threshold 0 \
       -format '%[fx:int(w*h*mean+0.5)]\n' info:
```

**Do not replace this with an "opaque near-white pixels = 0" count over the whole derivative.** On an
all-white mark that expression is just the opaque-pixel count (69,630) and can never be 0, so it
filters nothing. The check above is scoped to the *source's* counter region for exactly that reason,
and these two islands are its derivative-side counterpart.

**3. `+level-colors` without the `-channel RGB … +channel` guard destroys the artwork.** It
flattens the alpha channel and yields an opaque white rectangle (verified: `Grayscale Gray`, one
distinct alpha value) — while still producing a correctly-sized PNG that looks fine in a file
listing. The shape of these marks is carried **entirely by alpha**. `-fill white -colorize 100` is
the other safe form and gives pixel-identical output.

**4. Without `-define png:color-type=6` you silently get GrayscaleAlpha.** ImageMagick notices every
RGB channel is now equal and changes the storage type. Pixel-identical, a few KB smaller, and a
different colour type from everything else here. The explicit directive keeps both derivatives
sRGBA and directly comparable.

### Checksums

`sha256` of the files as they sit here — re-hash to prove a file was not touched in-repo:

```
393361d7dd49ab0687e6925d8f93bf28f9cab7be3e21f4110a4ae76fc36f3450  juju2-logo-source.png
1c44ca4023c2980949e04e5b5e2a5c31ac1c06f924d0dd9c6890192d563e6f3c  juju2-symbol-source.png
539dce785cef599cb8d9e533f67df45d9525af2be2fff27ec639b6ea4b3f8fd2  juju2-wordmark-white.png
7946b99cc4b7c640af7b214a89efaeb965f53d729e0656c914a4b39093f4cc7c  juju2-symbol-white.png
f12828c32a82c0e2d307dcd3c01b6938388fa77e02cac60452a698e2e7252e06  ../../app/icon.png
54ff6da3f1a1c9657721668870f97ab5f991eecddc0a55afd552910b0bac92d2  ../../app/icon1.png
72fc30fb3066a692b4c63b04a13809bca35c5f53d707248127bd8cfa4f0be418  ../../app/apple-icon.png
```

The two class-B originals and `juju2-symbol-white.png` are **unchanged by R18** and still carry the
hashes `P10.S7` recorded. The wordmark and all three tiles were re-derived, so their hashes and
signatures below are re-measured, never carried over.

**Those file hashes do not survive a re-run of the commands** — ImageMagick stamps a `png:tIME`
chunk, so re-deriving gives identical pixels in a different container. **To verify a *derivation*,
compare pixels, not bytes.** Never "fix" a mismatched file hash by re-deriving.

```
bc1bfd6ccc096b8272b0a3a36e0d246116fc4be76850beadcd7d8d0d3632a891  juju2-wordmark-white.png  (identify -format '%#')
37577b8751e8caaa52aa9c944c575dc7871ff6f22739b1e7c210ac116b9fedb7  juju2-symbol-white.png    (identify -format '%#')
07aa766bb20d1a804b7382a5aca17d76b22374eaa43c9e674d277600f59b9794  ../../app/icon.png        (identify -format '%#')
c57c675a66d45295b0b91aab0367e63a07d0871c6d2fd4af230cec12ed5c6166  ../../app/icon1.png       (identify -format '%#')
9d8c0e0083cc7245a2889cee7cd7958993c9f6d1d81020e28f9282c2bab02962  ../../app/apple-icon.png  (identify -format '%#')
```

All four R18 derivatives were re-run into a scratch directory from the commands above and compared:
**pixel signature identical and `compare -metric AE` = 0** on every one, which is what "regenerable
here" is supposed to mean. File sizes as they sit here: wordmark **21,920 b** (was 21,998), `icon.png`
**684 b**, `icon1.png` **476 b**, `apple-icon.png` **2,799 b** — the tiles shrank because a
transparent PNG stores no background.

`identify -format '%#'` is ImageMagick's own pixel signature; `magick f.png -depth 8 RGBA:- |
shasum -a 256` gives the same guarantee from raw bytes, and `compare -metric AE a.png b.png null:`
reporting `0` is the direct check.

### That the recolor changed colour, and the splice changed nothing else

Measured on the landed files, not asserted:

- both derivatives are `srgba 4.0`, 8-bit, alpha `Blend`;
- **the wordmark's alpha channel is a pure splice of the source's alpha.** Byte-identity with the
  source trim no longer holds — 45 columns are gone — so the check is: apply the *same two crops* to
  the source trim, `+append` them, and compare that alpha against the derivative's. Both give
  `d90e982748259b5356373cb82b5fb9fc20678947eb6df1994554b56ae895df79`:

  ```sh
  magick juju2-logo-source.png -trim +repage \
    \( -clone 0 -crop 530x371+0+0 +repage \) \( -clone 0 -crop 717x371+575+0 +repage \) \
    -delete 0 +append +repage -alpha extract -depth 8 gray:- | shasum -a 256
  magick juju2-wordmark-white.png -alpha extract -depth 8 gray:- | shasum -a 256   # must match
  ```

  That equality is the *proof* of the line below: the shape of this mark is carried entirely by
  alpha, so an alpha channel that is exactly the source's minus 45 fully-transparent columns means
  **cutting those columns did not change one pixel of ink**. For the symbol (untouched by R18) the
  original byte-identity claim still holds: source cropped the same way and the derivative both give
  `5e6540eb2a39913f93157e9205009bb9b2d30d6cbdcd12681a774a0e54ef67fc`;
- the ink statistics are therefore **identical before and after the splice**: the wordmark keeps
  **154 distinct alpha values**, **78,212** non-transparent and **69,630** fully opaque px — now over
  462,637 px of raster instead of 479,332, which is the only number that moved. The symbol keeps
  **112** over 36,630 px, 2,481 non-transparent;
- in both, **every** pixel is exactly `#FFFFFF` — transparent ones included (1 distinct RGB across
  the whole raster). That matters on cosmos: a renderer that filters without premultiplying can
  bleed transparent-pixel RGB into the edges on a hard downscale, and h27 from 371 is a 7.3 %
  downscale. White into white is invisible; the retired black variant's near-white transparent
  region was exactly the exposure that ruled it out for dark surfaces.

### Measured geometry — the numbers the chrome depends on

These are the **post-R18** numbers: the splice took 45 columns out of the width and **nothing else**,
so every vertical figure below is the same one R17 measured.

| | this mark (R18) | before R18 | the retired first mark (`juju-wordmark-white.png`) |
|---|---|---|---|
| trimmed box | **1247×371** | 1292×371 | 1213×319 |
| aspect | **3.3612 : 1** | 3.4825 : 1 | 3.80 : 1 |
| glyph band | **1087×176**, box-bottom flush, starting at y=195 → **47.44 %** of box height | 1132×176, same y | 1063×162 at y=157 → 50.8 % |
| ink coverage inside the band | **39.6 %** | 38.0 % | 16.1 % |

The box is **not** filled evenly, and this is the fact every placement decision turns on:

- sparkle cluster: **222×165** at `x=1025, y=0` — 2,481 ink px, still flush to the box's top **and**
  right (`1025 + 222 = 1247`); it moved 45px left with everything else right of the cut;
- empty band: **30 rows**, `y=165..194`, zero ink;
- Korean glyphs 주주의관제탑: **1087×176** at `x=0, y=195` — 75,731 ink px, bottom-flush. The ink
  count is unchanged and the band is 45px narrower, which is the whole of the density move
  (38.0 % → 39.6 %);
- 의\|관 ink gap: **25px**, `x=519..543` — was 70px. The advance-width grid says a Hangul step here
  is 183.0px, so this is now a normal inter-syllable gap (주\|주 is 19px).

So a height-constrained placement gets a mark whose *legible* part is 47 % of the declared height,
sitting in its **bottom** half. **R17 answers that** (`docs/reference/design/rounds/17-brand-mark-launcher/`):
the chrome renders **nav h27 / footer h24** and lifts the image by the band's own offset —
`BAND_CENTRE` is at 76.28 % of box height, i.e. `INK_OFFSET = 0.2628 × H` above the box centre,
rounded to `translateY(-7px)` / `-6px`. `components/chrome/Wordmark.tsx` carries both numbers and
the offset; the earlier "is h19 still right?" question is **closed**.

**R18 changed none of that.** `BAND_CENTRE 76.28 %`, `INK_OFFSET = 0.2628 × H` and both
`translateY` values are vertical, the splice was horizontal, and 47.44 % is a ratio of two unchanged
heights. The only figure that follows the new width is the **rendered width**: nav h27 goes
**94.03 → 90.75px**, footer h24 **83.58 → 80.67px**. Neither has a layout consequence — `.brand` is
`flex:none` and no rule fixes a width.

*(R18's own §① states the aspect as 3.3603 and the widths as 90.7 / 80.6. `1247 / 371 = 3.36119`,
`× 27 = 90.752`, `× 24 = 80.668` — the round's three figures all follow from one arithmetic slip in
the aspect. `P10.F1` read the widths out of the running document instead: Chrome reports
`getBoundingClientRect()` **90.75 × 27** in the nav and **80.66 × 24** in the footer, in dev and in
the production build, at 1280 and 390. The measured values are used here; the design record is not
edited. Same treatment `P10.S7` gave R17's two arithmetic errors.)*

The replacement is *proportionally shorter* in its band than the mark it retires (47.4 % against
50.8 %) but carries **2.4× the ink** in it. That density — not scale — is the answer to the
operator's "previous one was so thin".

## The favicon — shipped (R17 §2), re-cut transparent (R18 §③), and no longer prohibited

The previous README said "**Still no favicon, and this mark does not become one**". That is
**retired by R17**, and it was retired the way the rule required: not by cropping something out of
the wordmark, but by the operator **delivering a square symbol export**. The standing rule below is
therefore *satisfied*, not relaxed.

**R18 (`P10.review`) re-cut all three.** They are now **transparent** tiles carrying **one ink
colour**, at **75 %** ink width instead of R17's 84 %. R17's own line — one artwork, one rule, 16 a
downscale of the 32 raster, nothing cropped out of the wordmark — is untouched; what changed is the
placement rule and the ink colour.

Three tiles, all class C, all composited in this repo from `juju2-symbol-white.png`, and all shipped
through Next's `app/` file conventions so Next emits the `<link>` tags itself:

| file | tile | ink | sha256 / pixel signature |
|---|---|---|---|
| `../../app/icon.png` | 32×32, transparent | **24×18 at +4+7** (75.0 %) | `f12828c3…` / `07aa766b…` |
| `../../app/icon1.png` | 16×16, transparent | downscale of the 32 raster (12×10 at +2+3) | `54ff6da3…` / `c57c675a…` |
| `../../app/apple-icon.png` | 180×180, transparent | **134×100 at +23+40** (74.4 %) | `72fc30fb…` / `9d8c0e00…` |

Run from **`frontend/`** (one level up from this directory), not from here — the paths below are
repo-frontend-relative because the tiles land in `app/`:

```sh
# Transparent tile. Ink = the symbol recoloured to #2b8e6c, then given an exact integer
# width, composited dead-centre on both axes.
#   32px  -> 24 wide (75.0%);  24 * 165/222 = 17.8 -> 18 tall;  margins 4/4 and 7/7
#   180px -> 134 wide (74.4%); 134 * 165/222 = 99.6 -> 100 tall; margins 23/23 and 40/40
magick -size 32x32 xc:none \
       \( public/assets/juju2-symbol-white.png \
          -channel RGB +level-colors '#2b8e6c','#2b8e6c' +channel \
          -resize 24x \) \
       -gravity center -composite -depth 8 -define png:color-type=6 app/icon.png

magick -size 180x180 xc:none \
       \( public/assets/juju2-symbol-white.png \
          -channel RGB +level-colors '#2b8e6c','#2b8e6c' +channel \
          -resize 134x \) \
       -gravity center -composite -depth 8 -define png:color-type=6 app/apple-icon.png

# 16px is a DOWNSCALE OF THE 32 RASTER, not separate artwork (R17 §5: one artwork, one rule).
# -filter Box because at exactly 2:1 it is a plain 2x2 mean: the literal reduction, with no filter
# of its own. Lanczos (the default) rings — on the old opaque tile that measured 36 pixels *darker
# than the tile*, a colour the design never specified; on a transparent tile it would invent
# colours at the ink edge instead.
magick app/icon.png -filter Box -resize 16x16 -depth 8 -define png:color-type=6 app/icon1.png
```

**Three silent traps in those three commands** — all of them produce a normal-looking PNG of the
right size:

1. **`-alpha off` must not be there.** It, not `xc:'#0a1310'`, is what actually made the old tiles
   opaque: it flattens transparency to black. R17's commands carried it, which is why this diff
   looks like a colour change and is really a flag removal.
2. **`png:color-type=6`, never `2`.** Type 2 is RGB with no alpha; ask for transparency while
   leaving `2` in place and ImageMagick quietly composites a background instead of telling you.
3. **Recolour *before* resize.** Doing it in that order means every pixel of the ink layer — the
   transparent ones included — is exactly `#2b8e6c` going into the downscale, so a renderer that
   filters without premultiplying cannot bleed a foreign colour into the edge. It is the green
   version of the same reason the white derivatives are white everywhere.

Verify (run from `frontend/`):

```sh
identify -format '%f %wx%h %[channels] %[opaque]\n' app/icon.png app/icon1.png app/apple-icon.png
# 32x32 / 16x16 / 180x180, all srgba, all opaque=false

# ink box AND its offsets — NO +repage here, or the offsets reset to +0+0
magick app/icon.png -trim -format '%wx%h%O\n' info:         # 24x18+4+7
magick app/apple-icon.png -trim -format '%wx%h%O\n' info:   # 134x100+23+40

# every visible pixel is exactly #2b8e6c — this is the colour check that works.
# (R18 §③ prints '%[fx:int(255*u.r)]' instead, but that reads pixel (0,0), which is
#  transparent canvas on all three tiles and always answers 0,0,0.)
magick app/icon.png -depth 8 RGBA:- | python3 -c "
import sys; b=sys.stdin.buffer.read()
px=[tuple(b[i:i+4]) for i in range(0,len(b),4)]
print(sum(1 for p in px if p[3]>0 and p[:3]!=(43,142,108)))"   # 0
```

**The tile is transparent on purpose — and the old opaque rule was not wrong, its premise was.**
R17 said a transparent favicon vanishes on a light browser tab, and that is true *of white ink*.
The background was carrying the contrast for an ink colour that had none. Unpin the ink from white
and the background stops being necessary: **`#2b8e6c`** (`oklch(0.58 0.105 166)`) sits between the
design system's two `--live` greens on the same hue axis and reads on both sides —

| surface | contrast |
|---|---|
| white tab | **4.05** |
| Chrome light tab `#f1f3f4` | 3.64 |
| Chrome dark tab `#202124` | **3.98** |
| cosmos `#0a1310` | 4.66 |
| pure black | 5.19 |

— 4.05 against white and 3.98 against a dark tab, which is the point: it leans neither way, so one
tile serves every context and there is **no separate opaque `apple-touch-icon`**. iOS composites the
transparent tile on black or white, and both of those numbers are in the table. `#2b8e6c` is an
ImageMagick **literal**, not a token: `../foundations/tokens.css` stays frozen.

**Why 75 % and not 84 %.** The ink box is 222×165 — **4:3** — and the tile is square, so preserving
the aspect always leaves more vertical margin than horizontal, and the horizontal margin is the one
that decides. At 84 % a 32px tile had **2.5px** of side margin (landing at +2), and the left sparkle
is **flush to `x=0`** of the ink box, so 2px was the entire gap between artwork and tile edge — the
"stuck to the border" the operator saw. 75 % gives **4px** at 32 and **23px** at 180 (from 14). 78 %
was measured too and rejected: 3.5px is indistinguishable from the state being fixed.

**`Launcher.module.css` keeps `mask-size: 84% auto`, and that divergence is deliberate.** The
launcher paints the same artwork inside a 68×50 frame this product draws itself, never adjacent to
another site's tab text. R17's "one artwork, one rule" was signed about the **crop**, and the crop is
unchanged; a placement rule may differ per surface, and here it does. Do not "harmonise" the two.

**Two bounds R17 signed, and neither is a bug to fix:**

- the **single-star crop is explicitly not adopted** (`-crop 74x74+148+12`). One artwork, one rule —
  splitting the icon into two variants would set the precedent of picking a piece of the artwork;
- at 16px the five small dots are about **1.2px each** (1.4px before R18, scaled by 75/84) and read
  as soft dust. That is a **recorded limitation**, disclosed here rather than fixed by
  inventing a second icon, and R18 §⑦.3 keeps it closed: reopening it needs an operator instruction.

Verified served, dev **and** production: `link[rel="icon"] sizes="32x32"`, `sizes="16x16"` and
`link[rel="apple-touch-icon"] sizes="180x180"` all present in the DOM. `P10.S5` proved their absence
the same way; this is the same check with the opposite result.

**A transparent tile needs one check more than a tag count** — the whole change is that there is no
longer a square carrying the contrast, so `P10.F1` re-fetched the three hashed URLs the DOM actually
names (`sha256` identical to the files here, dev and production) and had Chrome paint each of them
at the tab strip's **16 CSS px** on four backgrounds. It reads on every one; the peak per-pixel
contrast is **2.94** against a white tab, **2.71** on Chrome light `#f1f3f4`, **3.02** on Chrome dark
`#202124` and **3.38** on cosmos — *below* the flat colour's 4.05/3.98 because a 16px downscale of a
five-dot cluster leaves almost no fully opaque pixel (1 of 84 in `icon.png`, 0 of 37 in `icon1.png`).
That softness is the same recorded limitation as the 1.2px dots, seen from the contrast side.

## The share card and the two large manifest tiles — three class-C derivatives (`P4.S5`, 2026-09-02)

`P4.S5` gave the site its SEO surface, and three of those pieces are **images**. All three are
class C: produced in this repository by **one recorded ImageMagick command each**, from the class-C
marks above, with no artwork drawn, cropped or invented. Same ImageMagick as everything else on this
page — **7.1.2-27 Q16-HDRI aarch64**.

| file | class | what it is | format |
|---|---|---|---|
| `../../app/opengraph-image.png` | C | the **share card** — the white wordmark centred on the cosmos paper `#0a1310`, served at `/opengraph-image.png` and named by every page's `og:image` / `twitter:image` | PNG 1200×630 sRGBA **opaque**, 32,679 b |
| `juju2-icon-192.png` | C | the 192 manifest tile — the symbol in `#2b8e6c` on transparency, same recipe as the favicons | PNG 192×192 sRGBA, 3,037 b |
| `juju2-icon-512.png` | C | the 512 manifest tile — the same, one size up | PNG 512×512 sRGBA, 11,095 b |

**The share card is a *composition*, not a new mark.** It places `juju2-wordmark-white.png`
unmodified — no recolour, no crop, no trim — on a rectangle of the design system's own dark paper.
Nothing was drawn on it and **no text was set**: the only glyphs on the card are the wordmark's own
raster. That is what keeps it inside this directory's rule rather than beside it.

### Exactly how the three were produced

Run from **`frontend/`** (one level up from this directory), like the favicon commands above — the
share card lands in `app/`, the two tiles here:

```sh
# Share card. 1200x630 is the Open Graph 1.91:1 box. The wordmark is scaled to 720 wide
# (60% of the card) and composited dead-centre on both axes:
#   720 * 371/1247 = 214.2 -> 214 tall;  margins 240/240 horizontal and 208/208 vertical.
# The canvas is OPAQUE (xc:'#0a1310'), so the result has a uniform alpha of 255 — a share
# card is composited by someone else's UI and must not rely on transparency.
magick -size 1200x630 xc:'#0a1310' \
       \( public/assets/juju2-wordmark-white.png -resize 720x \) \
       -gravity center -composite -depth 8 -define png:color-type=6 app/opengraph-image.png

# The two large manifest tiles. Identical to the favicon recipe above — recolour to #2b8e6c
# BEFORE the resize, transparent canvas, composite centred — at the two PWA sizes, with the
# ink at the same 75% width R18 signed:
#   192 -> 144 wide (75.0%); 144 * 165/222 = 107.0 -> 107 tall; margins 24/24 and 42/43
#   512 -> 384 wide (75.0%); 384 * 165/222 = 285.4 -> 285 tall; margins 64/64 and 113/114
magick -size 192x192 xc:none \
       \( public/assets/juju2-symbol-white.png \
          -channel RGB +level-colors '#2b8e6c','#2b8e6c' +channel \
          -resize 144x \) \
       -gravity center -composite -depth 8 -define png:color-type=6 public/assets/juju2-icon-192.png

magick -size 512x512 xc:none \
       \( public/assets/juju2-symbol-white.png \
          -channel RGB +level-colors '#2b8e6c','#2b8e6c' +channel \
          -resize 384x \) \
       -gravity center -composite -depth 8 -define png:color-type=6 public/assets/juju2-icon-512.png
```

**The favicon section's four traps all still apply**, and the two tile commands inherit every one of
them: no `-alpha off` (it is what makes a tile opaque, not the canvas colour), `png:color-type=6`
never `2`, and **recolour before resize** so no foreign colour can bleed into the ink edge. The
share card is the one file here that *is* opaque, and it is opaque because its canvas is a solid
colour — still no `-alpha off` anywhere.

### Verify (run from `frontend/`)

```sh
identify -format '%f %wx%h %[channels] opaque=%[opaque]\n' \
  app/opengraph-image.png public/assets/juju2-icon-192.png public/assets/juju2-icon-512.png
# 1200x630 srgba opaque=true / 192x192 srgba opaque=false / 512x512 srgba opaque=false

# the composited artwork's box and offsets — NO +repage, or the offsets reset to +0+0
magick app/opengraph-image.png -trim -format '%wx%h%O\n' info:              # 720x214+240+208
magick public/assets/juju2-icon-192.png -trim -format '%wx%h%O\n' info:     # 144x107+24+42
magick public/assets/juju2-icon-512.png -trim -format '%wx%h%O\n' info:     # 384x285+64+113

# the share card carries exactly two colours and one alpha value: 20,211 pure-white ink px,
# 723,582 paper px, 756,000 total, 1 distinct alpha.
magick app/opengraph-image.png -depth 8 RGBA:- | python3 -c "
import sys; b=sys.stdin.buffer.read()
px=[tuple(b[i:i+4]) for i in range(0,len(b),4)]
print(len({p[3] for p in px}), sum(1 for p in px if p[:3]==(255,255,255)), sum(1 for p in px if p[:3]==(10,19,16)))"

# every visible pixel of both tiles is exactly #2b8e6c — the favicon section's colour check
magick public/assets/juju2-icon-512.png -depth 8 RGBA:- | python3 -c "
import sys; b=sys.stdin.buffer.read()
px=[tuple(b[i:i+4]) for i in range(0,len(b),4)]
print(sum(1 for p in px if p[3]>0 and p[:3]!=(43,142,108)))"   # 0
```

### Checksums

```
de6d4b2ddaeece55e42fa4895ade9cf2ebdd5f66e0e5eea5ad3de03ca098737c  ../../app/opengraph-image.png
e35635697c32280545fa6797baac79c08d15982f3415feca2dadea10c696b94c  juju2-icon-192.png
053d7b696aa2975802bb26a93a6017378ee936e217737bfeed3d18342b21723b  juju2-icon-512.png
```

Pixel signatures (`identify -format '%#'`) — the form that **survives** a re-derivation, because
ImageMagick stamps a `png:tIME` chunk and the file hashes above do not:

```
c867309ebe662f57cc0069857472ae07e7b829e10433231eb68f4ec83195961a  ../../app/opengraph-image.png
9da19a30a9e4bb4d6a40646ae31eb7c2df697f6fbc3494824ddbb44d99233ae1  juju2-icon-192.png
ed3c23a25a8ceb07e780b1311f53e1cc062d6027466d8dcd23882aab64415dcb  juju2-icon-512.png
```

**The share card is a gate item.** It is the first image of this product a stranger sees — a link
preview in KakaoTalk, X or Slack — and nothing in the signed design record specifies one, so it is a
*proposal* on the same footing as `P4.S5`'s Korean meta copy: the operator accepts or rejects it at
the P4 acceptance gate. Rejecting it is one file and one command; there is nothing else to unwind.

## The display-size wordmark — the file the chrome loads (`P4.F8`, 2026-09-03)

`juju2-wordmark-white.png` is **1247×371 / 21,920 b** and the chrome paints it at **91×27** (nav)
and **80.88×24** (footer) — at most **273×81 device px** on a DPR-3 phone. So every cold page load,
on every route, downloaded 21,920 bytes to draw 22,113 pixels; Lighthouse flagged exactly this file
(`uses-responsive-images`). `P4.F8` ships a **class-C derivative of the class-C master** — the same
move `P4.S5`'s share card made from the same file — at **3× the largest render**:

| file | class | what it is | format |
|---|---|---|---|
| `juju2-wordmark-white-273-73c23508.png` | C | the master at display size — `WORDMARK_WHITE` in `../../components/chrome/copy.ts` | PNG 273×81 sRGBA, **6,405 b** (−15,515 b, −70.8 %) |

**The name carries the first eight hex of the file's own pixel signature, and that is load-bearing.**
`../../next.config.ts` serves this one path `Cache-Control: public, max-age=31536000, immutable`,
and an `immutable` response cannot be recalled — a Cloudflare purge reaches the edge, never a browser
that was told not to ask for a year. Only a name that changes with its pixels can carry that header
honestly, so **re-deriving this file into different pixels renames it**, in three places at once:
here, `copy.ts`, and `next.config.ts`. Every *other* name under `/assets/` and `/foundations/` is
fixed and gets one week instead — see the header block in `next.config.ts`.

### Exactly how it was produced

Run from **`frontend/`** (one level up), same ImageMagick as everything else here —
**7.1.2-27 Q16-HDRI aarch64**:

```sh
# 3x the largest render: the nav paints 91 CSS px wide, so 273 device px at DPR 3.
# -resize 273x keeps the master's ratio: 273 * 371/1247 = 81.2 -> 81 tall.
magick public/assets/juju2-wordmark-white.png -filter Lanczos -resize 273x \
       -channel RGB +level-colors white,white +channel \
       -strip -depth 8 -quality 95 -define png:color-type=6 \
       public/assets/juju2-wordmark-white-273-73c23508.png
```

Nothing was cropped, re-drawn, re-coloured or re-composed: this is the master, scaled, and the
filename's hash is read off the result (`identify -format '%#'`, first eight hex).

**Why each flag, all four measured rather than assumed:**

- **`-filter Lanczos` — because the default here is *not* Lanczos.** ImageMagick picks Mitchell for
  an image with an alpha channel, and it is not a small difference: the unspecified form is
  pixel-identical to `-filter Mitchell` (`compare -metric AE` = 0) and visibly different from this
  one. Lanczos is the sharper of the two and the one that keeps the glyph band's ink weight, which
  is the property R18 was re-cut for (「previous one was so thin」).
- **`-channel RGB +level-colors white,white +channel` — the resize breaks this directory's own
  white-everywhere invariant, and this puts it back.** Measured on the unguarded output: the
  transparent region comes back **RGB (0,0,0)** on 13,516 px (plus one stray `#767676`), where the
  master is `#FFFFFF` on *every* pixel, transparent ones included. That invariant is not decoration —
  it is the reason a hard downscale of this mark cannot bleed a dark halo into the ink edge. With the
  guard the file is back to **1 distinct RGB**, and its alpha channel is **bit-identical** to the
  unguarded resize, so the guard changed no visible pixel (`compare -metric AE` = 0).
- **`-strip` — and it buys something no other file on this page has.** It drops the `png:tIME`
  chunk, so **this derivation is byte-reproducible**: two runs a second apart give the same sha256.
  The rule elsewhere in this README (「verify a derivation by pixel signature, never by file hash」)
  still governs — it is what a future ImageMagick's different zlib output would need — but here the
  file hash happens to reproduce too, and the verify block below shows both.
- **`-quality 95` — lossless, and worth 377 bytes.** It is zlib level 9 with adaptive PNG filtering;
  the pixels are identical to the unspecified form (`AE` 0, same pixel signature) and the file is
  6,405 b instead of 6,782 b.

### The geometry, and the one number that moved

| | display-size file | the master |
|---|---|---|
| box | **273×81** | 1247×371 |
| aspect | **3.3704 : 1** | 3.3612 : 1 |
| trim | `273x81+0+0` — ink flush on all four sides | `1247x371+0+0` |
| non-transparent px | **5,713** of 22,113 | 78,212 of 462,637 |
| fully opaque px | **1,577** | 69,630 |
| distinct alpha / RGB values | **255 / 1** | 154 / 1 |

**Nothing vertical moved, which is what `Wordmark.tsx`'s two `INK_OFFSET_PX` values depend on.** The
glyph band is still bottom-flush and the sparkle cluster still flush to the top and right; the band's
own edge lands at row **42.57 of 81**, exactly the master's 195/371 = 52.56 %, split across rows 42
and 43 by antialiasing.

**An integer raster cannot hold both aspects, so the rendered *width* moves by a quarter of a
pixel.** 273/81 is 3.3704 against the master's 3.3612, so Chrome reports **91.000 × 27** in the nav
(was 90.750) and **80.883 × 24** in the footer (was 80.664) — **+0.250 / +0.219 px**, measured at
1280 and 390 and at DPR 1, 2 and 3. `.brand` is `flex:none` with no fixed width and the mark is
flush-left in both surfaces, so nothing reflows and no ink moves left, up or down. Measured
consequence in the rendered pixels (`P4.F8`, real Chrome, `/stocks`): the ink bounding box is
**identical** in the nav at DPR 1/2/3 and in the footer at DPR 1, and the footer's **right** edge —
the outermost sparkle dot — sits **one device pixel** further right at DPR 2 and 3. Left, top and
bottom are identical everywhere.

**Lanczos rings, and the ring is invisible.** The master's 30 fully-transparent rows between the
cluster and the band become one fully-transparent row plus faint overshoot in the rest: **peak alpha
4/255 (1.6 %)**, against 255 for the ink it borders.

### Verify (run from `frontend/`)

```sh
identify -format '%f %wx%h %[channels] opaque=%[opaque] %B bytes\n' \
  public/assets/juju2-wordmark-white-273-73c23508.png
# juju2-wordmark-white-273-73c23508.png 273x81 srgba 4.0 opaque=False 6405 bytes

magick public/assets/juju2-wordmark-white-273-73c23508.png -trim -format '%wx%h%O\n' info:
# 273x81+0+0 — the ink is flush on all four sides, exactly as the master is

# re-derive into a scratch file and compare PIXELS (the rule), then bytes (a bonus of -strip)
magick public/assets/juju2-wordmark-white.png -filter Lanczos -resize 273x \
       -channel RGB +level-colors white,white +channel \
       -strip -depth 8 -quality 95 -define png:color-type=6 /tmp/w273.png
compare -metric AE public/assets/juju2-wordmark-white-273-73c23508.png /tmp/w273.png null:   # 0
shasum -a 256 /tmp/w273.png          # ae29fe47… — identical, because -strip drops png:tIME
identify -format '%#\n' /tmp/w273.png # 73c23508… — the first eight hex ARE the filename

# one distinct RGB (#FFFFFF everywhere, transparent pixels included), 255 alphas, and the ink counts
magick public/assets/juju2-wordmark-white-273-73c23508.png -depth 8 RGBA:- | python3 -c "
import sys; b=sys.stdin.buffer.read()
px=[tuple(b[i:i+4]) for i in range(0,len(b),4)]
print(len({p[:3] for p in px}), len({p[3] for p in px}),
      sum(1 for p in px if p[3]>0), sum(1 for p in px if p[3]==255))"   # 1 255 5713 1577
```

### Checksums

```
ae29fe47fe3f716e44547b49e84e47a7ea7551b1a73a32560c4b178dcd3f8d98  juju2-wordmark-white-273-73c23508.png
```

Pixel signature (`identify -format '%#'`) — **and the source of the eight hex in the filename**:

```
73c235084d3f0f539568b95a0a4c020d7b1913d1188902b5c178b35cb24c5728  juju2-wordmark-white-273-73c23508.png
```

**The master stays.** `juju2-wordmark-white.png` is the ancestor of the share card, of this file and
of anything else the mark is ever cut into, and this README's whole proof chain runs through it. It
is simply not requested by a page any more — measured on the local production build, `/`, `/stocks`
and `/ask` fetch exactly `juju2-wordmark-white-273-73c23508.png` (and the launcher's
`juju2-symbol-white.png`) out of this directory, and nothing else.

## Retired and **deleted** — what left, and why nothing loads it

Class A and class B files are *not regenerable here*, so these tables are the only in-repo record of
what they were. The bytes live on in git history; the hashes make a restore provably byte-exact.

### The first 주주의관제탑 mark — three files (`P10.S7`, 2026-08-31)

Landed by `P10.S1` on 2026-08-30 and **superseded five days later by the operator's own second
delivery** — "previous one was so thin". Not wrong, just replaced. Deleted **in the same change that
repointed `chrome/copy.ts`** at the new mark, exactly as `P10.S2` did with the `mijual-*` set,
because the white one was the only image the app loaded and deleting it earlier would leave every
page rendering a broken image.

| file (deleted) | class | what it was | format |
|---|---|---|---|
| `juju-logo-source.png` | B | the operator's first delivery | PNG 2560×1440 sRGBA, 235,823 b |
| `juju-wordmark-black.png` | C | trimmed to ink, black — light surfaces only, never referenced | PNG 1213×319 sRGBA, 200,331 b |
| `juju-wordmark-white.png` | C | the same shape white — the mark the chrome loaded until now | PNG 1213×319 sRGBA, 25,674 b |

```
a22c9c4478e1a04a43022bf7c220d72581f62fade03072b053c20fd012ad8477  juju-logo-source.png
ecfe4e397cd1730191d224db8889a1b5cfd76b1fa5bf81da2019d7c0931cab70  juju-wordmark-black.png
73b4005f9a192bff7595aed5e789a9f0a7aa9cdc3dff2ffe2d12c27c22883283  juju-wordmark-white.png
```

### The two class-A font files (`P10.S7`, 2026-08-31)

**Operator-directed supersession, not an agent's judgement:** *"research changple_web's case for the
korean font. use same with it."* Both are replaced by self-hosted `next/font/local` subsets in
`../../app/fonts/`, generated by `../../scripts/subset_noto_sans_kr.sh` and
`../../scripts/subset_plex_mono.sh`.

| file (deleted) | class | what it was | format |
|---|---|---|---|
| `fonts/PretendardVariable.woff2` | A | Pretendard Variable, the Korean UI face — self-hosted per R1, exported by the operator 2026-08-22, copied in byte-for-byte by `P5.S10` | WOFF2, variable `wght 45–920`, **2,057,688 b** |
| `../foundations/fonts.css` | A | the R1 export marked *"VENDORED — do not edit"* that reached it, and that `@import`ed IBM Plex Mono from the **Google Fonts CDN** | CSS, 886 b |

```
9599f12fd42fc0bce1cd50b47a0c022e108d7aa64dd0d1bb0ed44f3282d900b4  fonts/PretendardVariable.woff2
bf897fb827f23f5411eb87ca3ebee985891dd9b12dfd138b1cf21283e69f4436  ../foundations/fonts.css
```

**Nothing loads either any more.** `app/layout.tsx` links only `/foundations/tokens.css`; the
`<link>` to the Plex Mono CDN went with `fonts.css`, and it only ever existed because the landed
record put its `@import` after an `@font-face`, where CSS drops it. What ships instead:

| file | bytes |
|---|---|
| `../../app/fonts/NotoSansKR.subset.woff2` | 291,072 |
| `../../app/fonts/IBMPlexMono-Regular.subset.woff2` | 12,712 |
| `../../app/fonts/IBMPlexMono-Medium.subset.woff2` | 13,012 |
| `../../app/fonts/IBMPlexMono-SemiBold.subset.woff2` | 13,684 |
| **total** | **330,480** — against 2,057,688 b **and** a cross-origin stylesheet before |

Both OFL-1.1 attribution files ship beside the fonts (`NotoSansKR-OFL.txt`, `IBMPlexMono-OFL.txt`).
`../foundations/tokens.css` is **not** edited — it is still frozen R8 material and still names
Pretendard; `app/shell.css` overrides `--font-sans` / `--font-mono` in application code instead.

### The four `mijual-*` files (`P10.S2`, 2026-08-30)

`mijual-wordmark-{charcoal,white}.png` and `mijual-logo-ring-{charcoal,white}.png` were the old
English MIJUAL brand (class A, R1/R2 design-project exports, landed by `P5.S10`), retired by the
주주의관제탑 rebrand.

| file (deleted) | what it was | format |
|---|---|---|
| `mijual-wordmark-charcoal.png` | the English wordmark, brand charcoal `#1f2926` (R1 rev 3) | PNG 1788×324 RGBA, 42,403 b |
| `mijual-wordmark-white.png` | the reversed white wordmark (R1 rev 1) — already unreferenced | PNG 1788×324 RGBA, 37,242 b |
| `mijual-logo-ring-charcoal.png` | ring logo (R2 — closed R1's missing symbol-mark gap) | PNG 2178×346 RGBA, 76,558 b |
| `mijual-logo-ring-white.png` | ring logo reversed — the last image that brand loaded (R2) | PNG 2178×346 RGBA, 64,605 b |

```
2119682f08054cc0fc83fbe57e82949c57b14ca4d02d767e8de924ad2fb3d25c  mijual-wordmark-charcoal.png
8725c50119793e0bc16f9757a6c5dc69715dc20ce47f022f2eeb031d8ca78807  mijual-wordmark-white.png
454a07c0d87d22461f24a38f8bbb496ada730787ec3b96cbf6cb5676c1852b68  mijual-logo-ring-charcoal.png
7bef551a983b4e73ca4a56c07fd27bea3fc79ea3f241a545b609b8efe875ff4b  mijual-logo-ring-white.png
```

**Every deleted filename above still appears in prose** — this record, the design rounds under
`docs/reference/design/` (never edited), the generated `docs/current/` snapshots, and doc comments
that say what a thing replaced. A `grep` hit is expected and is **never** a live reference; a hit
**inside a code path** would be the regression.

## Rules

- **Class A and class B files are never edited here.** No re-export, downscale or re-compression.
  Replacing a class-A file means a new export from the design project; replacing a class-B file
  means a new delivery from the operator.
- **Class C files are regenerated, never hand-edited.** Change the recorded command, re-run it, and
  update the command, the file hash *and* the pixel signature in this README together.
- **Verify a derivation by pixel signature, never by file hash.** Re-deriving changes the container,
  not the pixels.
- **A file served `immutable` carries its own pixel signature in its name.** `P4.F8` gives
  `/assets/*` and `/foundations/*` real cache lifetimes, and the year-long, unrecallable one is
  allowed **only** on a name that changes when the pixels do — today exactly
  `juju2-wordmark-white-273-73c23508.png`. Re-derive such a file and it is renamed here, in the
  component that references it and in `../../next.config.ts`, together. Every fixed name gets a week.
- **No image is substituted, generated or placeheld anywhere.** A slice that needs a missing asset
  renders the real file or nothing. This is what kept the favicon unshipped until the operator
  delivered a real symbol export — and it is why the favicon tiles are a *composite of that
  delivery*, not a crop invented out of the wordmark.
- **There is still no SVG wordmark.** The symbol has no SVG either: it is a PNG whose **alpha is the
  shape**, painted through a CSS `mask` over `currentColor`, which is how one asset serves every
  colour without a second file.
