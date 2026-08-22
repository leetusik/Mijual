# Binary design assets — delivered by the operator, **exported from the design project**

These five files are the brand binaries from the Claude Design project **"Mijual Design
System"**. They are not produced by any code in this repository and are **not
regenerable here**: an invented wordmark is a design violation. They were exported by the
operator on **2026-08-22** and copied in **byte-for-byte** by `P5.S10` — not re-encoded,
not resized, not optimised, no metadata stripped.

## What is here

| file | what it is | format |
|---|---|---|
| `fonts/PretendardVariable.woff2` | Pretendard Variable, the Korean UI face — self-hosted per R1, referenced by `../foundations/fonts.css` | WOFF2 (TrueType outlines), variable `wght 45–920`, 2,057,688 b |
| `mijual-wordmark-charcoal.png` | the English wordmark, brand charcoal `#1f2926` (R1 revision 3) | PNG 1788×324 RGBA, 42,403 b |
| `mijual-wordmark-white.png` | the reversed **white** wordmark (R1 revision 1, same shape) — **this is the file the cosmos-dark surfaces use** | PNG 1788×324 RGBA, 37,242 b |
| `mijual-logo-ring-charcoal.png` | ring logo (R2 — closes R1's missing symbol-mark gap) | PNG 2178×346 RGBA, 76,558 b |
| `mijual-logo-ring-white.png` | ring logo, reversed — what the cosmos nav and footer use (R2) | PNG 2178×346 RGBA, 64,605 b |

`sha256`, so a later slice can prove a file was not re-encoded:

```
9599f12fd42fc0bce1cd50b47a0c022e108d7aa64dd0d1bb0ed44f3282d900b4  fonts/PretendardVariable.woff2
2119682f08054cc0fc83fbe57e82949c57b14ca4d02d767e8de924ad2fb3d25c  mijual-wordmark-charcoal.png
8725c50119793e0bc16f9757a6c5dc69715dc20ce47f022f2eeb031d8ca78807  mijual-wordmark-white.png
454a07c0d87d22461f24a38f8bbb496ada730787ec3b96cbf6cb5676c1852b68  mijual-logo-ring-charcoal.png
7bef551a983b4e73ca4a56c07fd27bea3fc79ea3f241a545b609b8efe875ff4b  mijual-logo-ring-white.png
```

## The white wordmark's filename — the open question is closed

The landed R1 record names only `assets/mijual-wordmark-charcoal.png` and *describes* a
reversed white version without naming its file. The export answers it:
**`mijual-wordmark-white.png`**, same 1788×324 shape as the charcoal one. `P5.S11` wires
that exact name — no guessing, no second candidate.

## Rules that still hold

- **Do not edit, re-export, downscale or re-compress these files.** They are the design
  project's own output; a diff here is a design change. Replacing one means a new export
  from the design project, not a local edit.
- **No image is substituted, generated or placeheld anywhere.** If a future asset (e.g. a
  favicon-scale mark) is missing, the slice that needs it renders the real file or
  nothing. There is still **no SVG wordmark** and no favicon-scale mark beyond the ring
  logo — R1 disclosed that gap and R2 closed only the ring half of it.
- Both wordmark variants and both ring variants ship: the charcoal pair is for light
  surfaces, the white pair for the cosmos-dark chrome. Neither is dead weight and neither
  substitutes for the other.

## How the font is reached

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
