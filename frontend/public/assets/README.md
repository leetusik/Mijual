# Binary design assets — three kinds of provenance, and they are not interchangeable

This directory holds files with **three different provenance stories**, and the whole point of
this README is to say which story each file has. Confusing them is how a derivative gets treated
as untouchable, or an untouchable export gets "regenerated".

| provenance class | what it means | files |
|---|---|---|
| **A — design-project export** | produced outside this repo, in the Claude Design project **"Mijual Design System"**, and **not regenerable here**. Copied in byte-for-byte. A diff is a design change. | **none remain in this directory.** The four `mijual-*.png` were class A and were deleted by `P10.S2`; `fonts/PretendardVariable.woff2` and `../foundations/fonts.css` were class A and were deleted by `P10.S7`. All are recorded below. `../foundations/tokens.css` is still class A and is still frozen. |
| **B — operator delivery** | handed over directly by the operator, outside the design project. Landed byte-exact and never re-encoded. Also not regenerable here. | `juju2-logo-source.png`, `juju2-symbol-source.png` |
| **C — repo-generated derivative** | produced **in this repository** by one recorded ImageMagick command from a class-B file. **Regenerable here** — that is the trust: re-run the command and compare. | `juju2-wordmark-white.png`, `juju2-symbol-white.png`, and the three favicon tiles in `../../app/` |

## The brand mark (2026-08-31, `P10.S7`) — the second delivery

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
| `juju2-wordmark-white.png` | C | the wordmark trimmed to its ink and recoloured **white** — **the only image the chrome loads** | PNG 1292×371 sRGBA, 21,998 b |
| `juju2-symbol-white.png` | C | the symbol **cropped** to its real ink and recoloured white — the launcher paints it with a CSS `mask`, and the favicon tiles are composited from it | PNG 222×165 sRGBA, 3,232 b |

**There is no black variant, and that is deliberate.** The retired first mark had one for light
surfaces; nothing ever referenced it, R17 names no such variant, and the one mark that genuinely
needs to change colour — the symbol — is painted with `mask` + `currentColor` instead, so a single
asset serves every colour. Adding a second recolour now would be a file with no consumer.

### Exactly how the derivatives were produced

Run from this directory, ImageMagick **7.1.2-27 Q16-HDRI aarch64**. These are R17 §0's commands
verbatim, with the operator's filenames replaced by the landed class-B names (same bytes):

```sh
# wordmark — -trim gives exactly 1292x371+238+255
magick juju2-logo-source.png -trim +repage \
       -channel RGB +level-colors white,white +channel \
       -define png:color-type=6 juju2-wordmark-white.png

# symbol — NEVER -trim; crop the real ink explicitly (see the warning below)
magick juju2-symbol-source.png -crop 222x165+39+62 +repage \
       -channel RGB +level-colors white,white +channel \
       -define png:color-type=6 juju2-symbol-white.png
```

Nothing was resized, optimised, re-compressed, or had metadata stripped.

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
`69×15 at (1014,335)` (「탑」's ㅂ). Two counters, both punched through.

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
749d413f0543b276873f5a6814bc01d0a425f460bee51af216edc6aceb28eba6  juju2-wordmark-white.png
7946b99cc4b7c640af7b214a89efaeb965f53d729e0656c914a4b39093f4cc7c  juju2-symbol-white.png
```

**Those file hashes do not survive a re-run of the commands** — ImageMagick stamps a `png:tIME`
chunk, so re-deriving gives identical pixels in a different container. **To verify a *derivation*,
compare pixels, not bytes.** Never "fix" a mismatched file hash by re-deriving.

```
66d9354ba3587f9df3584532c9c9c2bee3894414202f974a53e82f681d7f8e1e  juju2-wordmark-white.png  (identify -format '%#')
37577b8751e8caaa52aa9c944c575dc7871ff6f22739b1e7c210ac116b9fedb7  juju2-symbol-white.png    (identify -format '%#')
```

`identify -format '%#'` is ImageMagick's own pixel signature; `magick f.png -depth 8 RGBA:- |
shasum -a 256` gives the same guarantee from raw bytes, and `compare -metric AE a.png b.png null:`
reporting `0` is the direct check.

### That the recolor changed colour and nothing else

Measured on the landed files, not asserted:

- both derivatives are `srgba 4.0`, 8-bit, alpha `Blend`;
- their **alpha channels are byte-identical to the source's**, which is the whole claim of an
  alpha-preserving recolor. `magick juju2-logo-source.png -trim +repage -alpha extract -depth 8
  gray:- | shasum -a 256` and the same on the derivative both give
  `296508ffbbfcfc0fcbcc67a58348ecf94a32f3989bdac9f049354323cc5d2fbe`; for the symbol (source cropped
  the same way) both give `5e6540eb2a39913f93157e9205009bb9b2d30d6cbdcd12681a774a0e54ef67fc`;
- the wordmark keeps **154 distinct alpha values** over 479,332 px — 78,212 non-transparent, 69,630
  fully opaque; the symbol keeps **112** over 36,630 px, 2,481 non-transparent;
- in both, **every** pixel is exactly `#FFFFFF` — transparent ones included (1 distinct RGB across
  the whole raster). That matters on cosmos: a renderer that filters without premultiplying can
  bleed transparent-pixel RGB into the edges on a hard downscale, and h27 from 371 is a 7.3 %
  downscale. White into white is invisible; the retired black variant's near-white transparent
  region was exactly the exposure that ruled it out for dark surfaces.

### Measured geometry — the numbers the chrome depends on

| | this mark | the retired first mark (`juju-wordmark-white.png`) |
|---|---|---|
| trimmed box | **1292×371** | 1213×319 |
| aspect | **3.4825 : 1** | 3.80 : 1 |
| glyph band | **1132×176**, box-bottom flush, starting at y=195 → **47.44 %** of box height | 1063×162 at y=157 → 50.8 % |
| ink coverage inside the band | **38.0 %** | 16.1 % |

The box is **not** filled evenly, and this is the fact every placement decision turns on:

- sparkle cluster: **222×165** at `x=1070, y=0` — 2,481 ink px, flush to the box's top **and** right;
- empty band: **30 rows**, `y=165..194`, zero ink;
- Korean glyphs 주주의관제탑: **1132×176** at `x=0, y=195` — 75,731 ink px, bottom-flush.

So a height-constrained placement gets a mark whose *legible* part is 47 % of the declared height,
sitting in its **bottom** half. **R17 answers that** (`docs/reference/design/rounds/17-brand-mark-launcher/`):
the chrome renders **nav h27 / footer h24** and lifts the image by the band's own offset —
`BAND_CENTRE` is at 76.28 % of box height, i.e. `INK_OFFSET = 0.2628 × H` above the box centre,
rounded to `translateY(-7px)` / `-6px`. `components/chrome/Wordmark.tsx` carries both numbers and
the offset; the earlier "is h19 still right?" question is **closed**.

The replacement is *proportionally shorter* in its band than the mark it retires (47.4 % against
50.8 %) but carries **2.4× the ink** in it. That density — not scale — is the answer to the
operator's "previous one was so thin".

## The favicon — shipped (R17 §2), and this section replaces the prohibition

The previous README said "**Still no favicon, and this mark does not become one**". That is
**retired by R17**, and it was retired the way the rule required: not by cropping something out of
the wordmark, but by the operator **delivering a square symbol export**. The standing rule below is
therefore *satisfied*, not relaxed.

Three tiles, all class C, all composited in this repo from `juju2-symbol-white.png`, and all shipped
through Next's `app/` file conventions so Next emits the `<link>` tags itself:

| file | tile | ink | sha256 / pixel signature |
|---|---|---|---|
| `../../app/icon.png` | 32×32 | 27×20 at +2+6 (84.4 %) | `1c11de45…` / `0e506ad7…` |
| `../../app/icon1.png` | 16×16 | downscale of the 32 raster | `89e57f1a…` / `331ac3d5…` |
| `../../app/apple-icon.png` | 180×180 | 151×112 at +14+34 (83.9 %) | `7f36b89e…` / `ba819f18…` |

Run from **`frontend/`** (one level up from this directory), not from here — the paths below are
repo-frontend-relative because the tiles land in `app/`:

```sh
# 84% ink-width rule, ink box centred on both axes, on an OPAQUE #0a1310 tile.
#   32px  -> 32 * 0.84 = 26.88 wide;  26.88 * 165/222 = 19.98 tall   (R17's "26.9 x 20.0")
#   180px -> 151.2 x 112.38
magick -size 32x32 xc:'#0a1310' \
       \( public/assets/juju2-symbol-white.png -resize 26.88x \) \
       -gravity center -composite -alpha off -depth 8 -define png:color-type=2 app/icon.png

magick -size 180x180 xc:'#0a1310' \
       \( public/assets/juju2-symbol-white.png -resize 151.2x \) \
       -gravity center -composite -alpha off -depth 8 -define png:color-type=2 app/apple-icon.png

# 16px is a DOWNSCALE OF THE 32 RASTER, not separate artwork (R17 §5: one artwork, one rule).
# -filter Box because at exactly 2:1 it is a plain 2x2 mean: the literal reduction, with no filter
# of its own. Lanczos (the default) rings — measured 36 pixels *darker than the tile*, a colour the
# design never specified — and Box also keeps the ink brightest (232 vs 214).
magick app/icon.png -filter Box -resize 16x16 -alpha off -depth 8 -define png:color-type=2 app/icon1.png
```

**The tile is opaque on purpose.** A transparent favicon vanishes on a light browser tab; `#0a1310`
is the cosmos `--paper`, so the icon carries its own surface.

**Two bounds R17 signed, and neither is a bug to fix:**

- the **single-star crop is explicitly not adopted** (`-crop 74x74+148+12`). One artwork, one rule —
  splitting the icon into two variants would set the precedent of picking a piece of the artwork;
- at 16px the five small dots are about **1.4px each** and read as soft dust. That is a **recorded
  limitation**, disclosed here rather than fixed by inventing a second icon.

Verified served, dev **and** production: `link[rel="icon"] sizes="32x32"`, `sizes="16x16"` and
`link[rel="apple-touch-icon"] sizes="180x180"` all present in the DOM. `P10.S5` proved their absence
the same way; this is the same check with the opposite result.

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
- **No image is substituted, generated or placeheld anywhere.** A slice that needs a missing asset
  renders the real file or nothing. This is what kept the favicon unshipped until the operator
  delivered a real symbol export — and it is why the favicon tiles are a *composite of that
  delivery*, not a crop invented out of the wordmark.
- **There is still no SVG wordmark.** The symbol has no SVG either: it is a PNG whose **alpha is the
  shape**, painted through a CSS `mask` over `currentColor`, which is how one asset serves every
  colour without a second file.
