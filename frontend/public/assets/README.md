# Binary design assets — two kinds of provenance, and they are not interchangeable

This directory now holds files with **two different provenance stories**, and the whole
point of this README is to say which story each file has. Confusing them is how a
derivative gets treated as untouchable, or an untouchable export gets "regenerated".

| provenance class | what it means | files |
|---|---|---|
| **A — design-project export** | produced outside this repo, in the Claude Design project **"Mijual Design System"**, and **not regenerable here**. Copied in byte-for-byte. A diff is a design change. | `fonts/PretendardVariable.woff2` (the four `mijual-*.png` were class A too, and were deleted by `P10.S2` — see the retirement record below) |
| **B — operator delivery** | handed over directly by the operator, outside the design project. Landed byte-exact and never re-encoded. Also not regenerable here. | `juju-logo-source.png` |
| **C — repo-generated derivative** | produced **in this repository** by one recorded ImageMagick command from a class-B file. **Regenerable here** — that is the trust: re-run the command and compare. | `juju-wordmark-black.png`, `juju-wordmark-white.png` |

## The brand mark (2026-08-30, `P10.S1`)

The operator delivered `~/Downloads/juju_logo_no_back.png` directly — **not** an export
from the Claude Design project, so the "byte-for-byte from the design project" rule below
does **not** describe it or its derivatives. That original lives outside the repository and
will not survive, so it is landed here unreferenced as `juju-logo-source.png`: the
immutable ancestor every other brand file is derived from.

**What the mark is:** the Korean wordmark **주주의관제탑** with a small **sparkle cluster at
the upper right**, on transparency. It has **no ring** and no latin lettering. Any code,
comment or doc reasoning about "the MIJUAL wordmark with its orbital ring" is describing a
mark that no longer exists.

| file | class | what it is | format |
|---|---|---|---|
| `juju-logo-source.png` | B | the operator's delivery, byte-exact and **unreferenced** — kept only as the ancestor | PNG 2560×1440 sRGBA, 235,823 b |
| `juju-wordmark-black.png` | C | the mark trimmed to its ink, **black** — for light surfaces only | PNG 1213×319 sRGBA, 200,331 b |
| `juju-wordmark-white.png` | C | the same shape recoloured **white** — **this is the file the cosmos-dark chrome uses** | PNG 1213×319 sRGBA, 25,674 b |

### Exactly how the derivatives were produced

Run from this directory, ImageMagick **7.1.2-27 Q16-HDRI aarch64**:

```sh
magick juju-logo-source.png -trim +repage juju-wordmark-black.png

magick juju-logo-source.png -trim +repage \
       -channel RGB +level-colors white,white +channel \
       -define png:color-type=6 juju-wordmark-white.png
```

That is the whole of it. Nothing was resized, optimised, re-compressed, or had metadata
stripped.

**The white recolor has a trap in it.** `+level-colors white,white` *without* the
`-channel RGB … +channel` guard flattens the alpha channel and yields an opaque white
rectangle (verified: `Grayscale Gray`, 1 distinct alpha value). The shape of this mark is
carried **entirely by alpha**, so that command destroys the artwork while still producing a
1213×319 PNG that looks fine in a file listing. `-fill white -colorize 100` is the other
safe form and gives pixel-identical output. `-define png:color-type=6` is not cosmetic
either: without it ImageMagick notices every RGB is now equal and silently writes a
**GrayscaleAlpha** PNG. Pixel-identical (verified `compare -metric AE` = 0), 4.6 KB smaller,
but it stores the mark as a different colour type than its black sibling; the explicit
directive keeps both variants sRGBA and directly comparable.

### Checksums

`sha256` of the files as they sit here — re-hash to prove a file was not touched in-repo:

```
a22c9c4478e1a04a43022bf7c220d72581f62fade03072b053c20fd012ad8477  juju-logo-source.png
ecfe4e397cd1730191d224db8889a1b5cfd76b1fa5bf81da2019d7c0931cab70  juju-wordmark-black.png
73b4005f9a192bff7595aed5e789a9f0a7aa9cdc3dff2ffe2d12c27c22883283  juju-wordmark-white.png
```

**Those file hashes do not survive a re-run of the commands** — ImageMagick stamps a
`png:tIME` chunk, so re-deriving gives identical pixels in a different container. To verify
a *derivation*, compare pixels, not bytes:

```
c1caf123e4f302f9d6c21b3b859454364a12865afa9a1362764b916b9494ac58  juju-wordmark-black.png   (identify -format '%#')
b8e8aeda2296a7519b58731c473ec7ac35644f1fb2f8cab494510a4cb5e827c4  juju-wordmark-white.png   (identify -format '%#')
```

`identify -format '%#'` is ImageMagick's own pixel signature; `magick f.png -depth 8 RGBA:- |
shasum -a 256` gives the same guarantee from raw bytes, and `compare -metric AE a.png b.png
null:` reporting `0` is the direct check.

### That the recolor changed colour and nothing else

Measured on the landed files, not asserted:

- both are **1213×319, `srgba 4.0`, 8-bit, alpha `Blend`**;
- both carry **42 distinct alpha values** — unchanged from the source;
- their **alpha channels are byte-identical**: `magick f.png -alpha extract -depth 8 gray:-
  | shasum -a 256` → `67d54de6bcdb2c5a85bd6d9f96c5ebf5af46594ff307af6bbc4551fd839ac020` for
  both, and `compare -metric AE -channel A` reports `0`;
- of the 386,947 pixels, **7,488 are fully opaque, 22,956 partial-alpha, 356,503
  transparent** — the same three counts in both files;
- in the white variant **every** pixel is exactly `#FFFFFF` (1 distinct RGB per alpha
  bucket), so all 30,444 non-transparent pixels are pure white.

### Measured geometry — the numbers the chrome depends on

| | new mark | retired ring (`mijual-logo-ring-white.png`) |
|---|---|---|
| trimmed box | **1213×319** | 2178×346 |
| aspect | **3.80 : 1** | 6.29 : 1 |
| ink height as % of box | **50.8%** (Korean glyphs) | 75.7% |

The box is **not** filled evenly. The sparkle cluster sits alone in the top half and the
Korean glyphs in the bottom half, with a **22-row empty band** between them:

- sparkle cluster: **184×135** at `x=1029, y=0` — 1,426 non-transparent px, upper right only;
- empty band: `y=135..156`;
- Korean glyphs 주주의관제탑: **1063×162** at `x=0, y=157` — 29,018 non-transparent px,
  **50.8%** of the box height.

So a height-constrained placement gets a mark whose *legible* part is barely half the
declared height. At the chrome's current signed heights: nav `h=19` renders a 72×19 box with
a **9.7px** Korean band; footer `h=17` renders 65×17 with an **8.6px** band. The retired ring
put **14.4px** of ink into the same 19px. **This is an open question for the operator, not a
decision for a slice** — the phase notebook carries it.

(`P10.DECOMP` recorded the glyph band as `946×161 at y=158`. `P10.S1` re-measured it twice —
by pixel enumeration and by `magick -crop … -trim` — and both give **1063×162 at y=157**. The
height, and therefore the legibility arithmetic, is unchanged; the width was understated.)

### Why both a black and a white variant, and where each may go

Only the **white** one has a consumer, exactly as only the white ring did before. The black
is for light surfaces and **must never reach the cosmos-dark chrome**:

- in `juju-wordmark-black.png` the 356,503 fully-transparent pixels carry **near-white RGB**
  (up to `#FFFFFF`; 54,980 of them exactly white) inherited from the operator's canvas. They
  are invisible when composited, but a renderer that filters without premultiplying can bleed
  them into the edges on a hard downscale — and h19 from 319 is a 6% downscale. On a light
  surface that bleed is white-on-white and harmless; on the cosmos chrome it would fringe.
- the white variant has no such exposure at all: **every** pixel is `#FFFFFF`, transparent
  ones included, so any bleed is white into white.

(The mark's opaque ink is essentially pure black — 19 distinct RGB values, all within
`(2,2,2)`, 4,649 of the 7,488 exactly `#000000`. The partial-alpha edge pixels are dark too,
max R `40`. The near-white RGB is in the fully-transparent region, not the antialiased edge.)

## Still no favicon, and this mark does not become one

There is **no favicon of any kind** — no `app/icon.*`, no `favicon.ico` — and this mark does
not reduce to one. A favicon box is square; fitting a 3.80:1 mark into 32×32 by width leaves
the artwork **8.4px tall**, of which the Korean band is **4.3px** and each of the six
syllables 주 주 의 관 제 탑 about **4.7px wide**. That is not small text, it is mush.

The retired ring logo closed the "missing symbol mark" gap that R1 disclosed. **That gap is
open again**, and this is where it is disclosed, exactly as the old README disclosed it.
Closing it needs an operator decision — ship no favicon, receive a square symbol export, or
authorise cropping the sparkle cluster out as a symbol — and until then the rule below holds
without exception.

## The four `mijual-*` files are retired and **deleted** (`P10.S2`, 2026-08-30)

`mijual-wordmark-{charcoal,white}.png` and `mijual-logo-ring-{charcoal,white}.png` were the
old English MIJUAL brand (class A, R1/R2 design-project exports, landed by `P5.S10`). They
are **retired by the 주주의관제탑 rebrand** and `P10.S2` deleted them from this directory, in
the same commit that repointed `chrome/copy.ts` at the new mark — the white ring was the one
image the app still loaded, so deleting it any earlier would have left the nav and footer
rendering a broken image on every page.

**They are gone from the working tree, on purpose.** Nothing loads them any more: no `src`,
no `url()`, no template. Every remaining mention of a `mijual-*.png` filename in this
repository is **historical prose** — this record, the geometry comparison above, the doc
comment in `components/chrome/copy.ts` that says what the mark replaced, the generated
`docs/current/frontend.md` snapshot, and the immutable design-round record under
`docs/reference/design/` (R1, R8, R12), which is never edited. So a `grep` hit is expected
and is never a live reference; a hit **inside a code path** would be the regression.

Class A files are *not regenerable here*, so this is the only in-repo record of what they
were. The bytes live on in git history (before `P10.S2`); this table is their identity:

| file (deleted) | what it was | format |
|---|---|---|
| `mijual-wordmark-charcoal.png` | the English wordmark, brand charcoal `#1f2926` (R1 rev 3) | PNG 1788×324 RGBA, 42,403 b |
| `mijual-wordmark-white.png` | the reversed white wordmark (R1 rev 1) — already unreferenced | PNG 1788×324 RGBA, 37,242 b |
| `mijual-logo-ring-charcoal.png` | ring logo (R2 — closed R1's missing symbol-mark gap) | PNG 2178×346 RGBA, 76,558 b |
| `mijual-logo-ring-white.png` | ring logo reversed — the last image the app loaded (R2) | PNG 2178×346 RGBA, 64,605 b |

sha256 as landed by `P5.S10`, so a restore from git history can be proven byte-exact:

```
2119682f08054cc0fc83fbe57e82949c57b14ca4d02d767e8de924ad2fb3d25c  mijual-wordmark-charcoal.png
8725c50119793e0bc16f9757a6c5dc69715dc20ce47f022f2eeb031d8ca78807  mijual-wordmark-white.png
454a07c0d87d22461f24a38f8bbb496ada730787ec3b96cbf6cb5676c1852b68  mijual-logo-ring-charcoal.png
7bef551a983b4e73ca4a56c07fd27bea3fc79ea3f241a545b609b8efe875ff4b  mijual-logo-ring-white.png
```

## The font — unchanged, still a design-project export

| file | what it is | format |
|---|---|---|
| `fonts/PretendardVariable.woff2` | Pretendard Variable, the Korean UI face — self-hosted per R1, referenced by `../foundations/fonts.css` | WOFF2 (TrueType outlines), variable `wght 45–920`, 2,057,688 b |

```
9599f12fd42fc0bce1cd50b47a0c022e108d7aa64dd0d1bb0ed44f3282d900b4  fonts/PretendardVariable.woff2
```

Exported by the operator on **2026-08-22** and copied in **byte-for-byte** by `P5.S10` — not
re-encoded, not resized, not optimised, no metadata stripped. The rebrand does not touch it.

### How the font is reached

`../foundations/fonts.css` declares
`src: url("../assets/fonts/PretendardVariable.woff2") format("woff2-variations")` and is
served from `/foundations/fonts.css`, so the browser resolves
`/assets/fonts/PretendardVariable.woff2` — the landed record's relative path, unedited,
because this directory layout mirrors the design project's own `foundations/` + `assets/`.

Verified in a real headless Chrome (`P5.S10`, 2026-08-22): the face reports
`status: "loaded"`, `document.fonts.check('400 16px "Pretendard Variable"')` is `true`,
and Blink draws Korean prose with the platform font **Pretendard Variable** — no longer
the `-apple-system` fallback. IBM Plex Mono is unaffected; it still comes from the Google
Fonts CDN.

## Rules

- **Class A and class B files are never edited here.** No re-export, downscale or
  re-compression. Replacing a class-A file means a new export from the design project;
  replacing `juju-logo-source.png` means a new delivery from the operator.
- **Class C files are regenerated, never hand-edited.** Change the recorded command, re-run
  it, and update the command, the file hash *and* the pixel signature in this README together.
- **No image is substituted, generated or placeheld anywhere.** A slice that needs a missing
  asset renders the real file or nothing. This still binds the favicon: it is not invented,
  not approximated, and not cropped out of the wordmark without the operator saying so.
- **There is still no SVG wordmark**, and no symbol mark of any kind.
