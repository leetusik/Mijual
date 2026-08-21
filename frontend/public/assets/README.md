# Binary design assets — expected here, **not in this repository**

The wordmark PNGs, the ring logo PNGs and `PretendardVariable.woff2` live in the Claude
Design project **"Mijual Design System"**, never in this repo. `docs/current/frontend.md`
(Open Questions) and `P5`'s phase notes both record this, and `P5.S10` verified it again:
nothing matching `*wordmark*`, `*ring*.png`, `*Pretendard*` or `*.woff2` exists anywhere in
the checkout.

**They cannot be created here.** An invented wordmark is a design violation; an empty slot
with the right path wired is honest. So the paths below are already referenced by the code
and by `public/foundations/fonts.css`, and the files are simply absent until the operator
exports them out of the design project into this directory.

## What to export, and where to drop it

| file | what it is | drop at |
|---|---|---|
| `PretendardVariable.woff2` | Pretendard Variable, the Korean UI face (self-hosted; R1) | `frontend/public/assets/fonts/PretendardVariable.woff2` |
| `mijual-wordmark-charcoal.png` | the English wordmark, brand charcoal `#1f2926` (R1 revision 3) | `frontend/public/assets/mijual-wordmark-charcoal.png` |
| the reversed **white** wordmark | R1 revision 1 generated a reversed white version from the same shape; the landed record names only the charcoal file, so **export it under whatever name the design project gives it** and `P5.S11` wires that exact name | `frontend/public/assets/` |
| `mijual-logo-ring-charcoal.png` | ring logo (R2 — closes R1's missing symbol-mark gap) | `frontend/public/assets/mijual-logo-ring-charcoal.png` |
| `mijual-logo-ring-white.png` | ring logo, reversed — what the cosmos nav and footer use (R2) | `frontend/public/assets/mijual-logo-ring-white.png` |

There is **no SVG wordmark** and no favicon-scale mark beyond the ring logo — R1 disclosed
that gap and R2 closed only the ring half of it.

## What happens while they are missing

- `fonts.css`'s `@font-face` 404s and Pretendard falls back down its own stack
  (`Pretendard` → `-apple-system` → `Malgun Gothic` → `sans-serif`). `font-display: swap`
  means nothing blocks; the page renders in the fallback face.
- IBM Plex Mono is unaffected — it comes from the Google Fonts CDN, not from here.
- No image is substituted, generated or placeheld anywhere. `P5.S11` (global chrome) is the
  slice that renders the ring wordmark, and it renders the real file or nothing.

`fonts.css` reaches the font as `../assets/fonts/PretendardVariable.woff2`, resolved from
`/foundations/fonts.css` — i.e. exactly the relative path the landed record was written
with, because this directory layout mirrors the design project's own `foundations/` +
`assets/`. Nothing in that file was edited.
