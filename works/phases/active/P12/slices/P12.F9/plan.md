# P12.F9 — Family C: metric-matched local fallback faces for IBM Plex Mono — the P4.F5 route applied to the mono face (R1 F5)

`kind: fix`, `risk: high` → `slice-executor-high`. Written 2026-09-04 by the orchestrator in `auto`
mode, after `P12.F8` (`f3ad1a9`). **Family C**, `DECOMP2`'s ruling 3, and the one finding in this
phase that is **live on production today** at every cold mobile load.

## Read first

- `phase.md`: `## Decisions` — **ruling 3** (the remedy, and what it must not touch: `preload:
  false`, `display: swap`; Windows at `size-adjust: 100%` unless measurable), the line 「the site's
  remaining cold-cache font reflow is entirely IBM Plex Mono」, the viewports line (the **412×915 @
  DPR 2.625 / 4× CPU / ≈1.6 Mbps / 150 ms cold-cache profile** is the only one in which this defect
  is observable), the instrument seam with F6's screenshot traps and F7's instrument facts, the
  build recipe; the shared bar (keep it); F1's seams note; **Q2** under `## Operator Questions`
  (this slice answers it — the review routes it).
- The finding, from the R1-era notebook:
  `git show 8519f45:works/phases/active/P12/phase.md | grep -n "F5 (rank"` — measured on the local
  production build **and on `https://jujutower.com` with identical deltas**: `IBMPlexMono_Regular_subset`
  (12 kB, 574 → 1,075 ms) then `SemiBold` (13 kB, 578 → 1,245 ms) each reflow every mono numeral
  horizontally — `/stocks/00547510` `DDay__dday` **106.13 → 92.42** (x +13.70), `Lookup__cval`
  「0.0863800841」 **113.53 → 97.20** (+16.33), 「20%」 39.48 → 27.00, `DDay__label` 36.02 → 30.61;
  `/portfolio` `rowWhen` / `holdingDDay` 106.13 → 92.42, `sharesValue` 「300주」 42.31 → 36.70; `/`
  `statValue` 「445건」 50.41 → 43.06. CLS reads 0.0005–0.00184 because the motion is horizontal
  inside the line box — **the px deltas, not the CLS, are the evidence.** `NotoSansKR_subset`
  (284 kB, landing at 2,973 ms) moves nothing: `P4.F5` holds.
- **The cause, read from the served CSS (orchestrator, dev 3010, 2026-09-04):** `next/font/local`
  emits a generated fallback for the mono face today —
  `@font-face { font-family: plexMono Fallback; src: local(Arial); ascent-override: 77.95%;
  descent-override: 20.91%; line-gap-override: 0.0%; size-adjust: 131.49%; }` —
  **Arial, a proportional face, scaled to 131.49 %.** That is why the cold paint is *wider* than
  Plex (106.13 / 92.42 = ×1.148) and why no number could ever fit it: a proportional face cannot be
  metric-matched to a monospace one string by string. It is exactly Noto's pre-`P4.F5` state, one
  face over. A monospace fallback has **one advance for every glyph**, so one `size-adjust` matches
  every string exactly — which is what makes ruling 3 a complete fix rather than a compromise.
- The precedent, by path — read it whole, it is the method: `works/phases/active/P4/slices/P4.F5/result.md`
  (§ 2 the metrics measured two ways — fontTools table reads via `uvx --from fonttools --with brotli
  python …`, a tool run, never a project dependency — and Chrome `TextMetrics` at 100 px; the two
  facts that changed the design: **`local()` matches a PostScript or full name, never a family
  name**, proven with `document.fonts.load()` against a deliberately bogus control, and synthesised
  bold not changing advance; § 3 the **fit** — every route rendered webfont-loaded vs webfont-blocked
  + candidate face, rect of every `body *` compared, until 0 moved; § 4 the cold-cache sweep, 3
  loads per cell, medians; § 5 the loaded-font `AE = 0`). Its scratchpad scripts are gone with that
  session — rewrite what you need; `r1_cdp.py`-style CDP goes through Aside now.
- The code: `app/fonts.ts` ~L80–98 (`plexMono = localFont({ src: [Regular 400, Medium 500,
  SemiBold 600], display: "swap", preload: false, variable: "--font-plex-mono", fallback:
  ["ui-monospace", "SFMono-Regular", "SF Mono", "Consolas", "monospace"] })` — **no
  `adjustFontFallback`**, hence the Arial face) and its Noto block above it (the shape to copy:
  `adjustFontFallback: false` + a fallback list whose first entries are the hand-declared families);
  `app/shell.css` ~L85–230 (the three Noto fallback families with their measured overrides and the
  comment that derives every number — the block this slice extends), ~L48–84 (`html:root
  --font-mono: var(--font-plex-mono), "IBM Plex Mono", ui-monospace, …` — leave it; the hand faces
  ride inside `--font-plex-mono`'s own stack, which is what `next/font` emits), ~L263–275 (`.mono`
  and `:where(.mono) { font-size: 0.95em }` — untouched). The three woff2 subsets under
  `app/fonts/`; `scripts/subset_plex_mono.sh` regenerates them (do not run it).
- On this Mac: `/System/Library/Fonts/SFNSMono.ttf` (SF Mono, a system face whose `local()` name
  must be **probed** — the family name will not resolve, and a hidden system face may need its
  PostScript name), `Menlo.ttc` (`Menlo-Regular` / `Menlo-Bold`), `Courier.ttc`.

## The change

1. **Find the face Chrome actually paints in.** With the webfont blocked (`Network.setBlockedURLs
   ["*IBMPlexMono*"]`), on a mono element, CDP `CSS.getPlatformFontsForNode` → the platform face
   `ui-monospace` resolves to in Chrome on macOS **after** the Arial face is gone (do this on a
   build with `adjustFontFallback: false` and the generic list, or by injecting the stack). That
   face — and Menlo if it is not the same one — is what the macOS family metric-matches. Record
   what `local()` name resolves for it (`document.fonts.load` + the bogus control, P4.F5 § 2).
2. **Read the metrics from the tables**, fontTools tool run: for the shipped Plex Mono subsets
   (`upem`, `hhea` ascent / descent / lineGap, the `hmtx` advance — one value; check it is one
   value across the three weights and across digits, Latin, `%`, `-`, `.`, and the space) and for
   each macOS fallback face (the same fields; SF Mono's weights 400 / 500 / 600 if it carries
   them, Menlo's 400 / 700). Confirm in Chrome with `TextMetrics` at 100 px (advance per glyph and
   `fontBoundingBoxAscent/Descent`), as P4.F5 did. Then the four divisions:
   `size-adjust = PlexAdvance / FallbackAdvance`, `ascent-override = (PlexAsc/upem) / size-adjust`,
   `descent-override = (PlexDesc/upem) / size-adjust`, `line-gap-override: 0%`. Windows: **Consolas
   is not on this machine** — vertical overrides from Plex's own metrics at `size-adjust: 100%`
   (Malgun's treatment; ruling 3), and say so in the CSS comment.
3. **Declare the faces in `app/shell.css`**, directly under the Noto block, in the same voice: a
   comment that states every number is measured and shows the divisions; `@font-face` for
   `"plexMono Fallback Apple"` (400 / 500 / 600 — real faces where SF Mono or Menlo has them,
   the nearest real face otherwise, `src` naming PostScript and full names, never the family) and
   `"plexMono Fallback Windows"` (`local("Consolas")` + `local("Consolas Bold")` at 700 if you
   declare a bold; Plex ships no 700, so 600 is the top — match what the product sets). No
   `Courier` face unless step 1 says Chrome falls to it.
4. **`app/fonts.ts`**: `plexMono` gains `adjustFontFallback: false` and its `fallback` list becomes
   `["plexMono Fallback Apple", "plexMono Fallback Windows", "ui-monospace", "SFMono-Regular",
   "SF Mono", "Consolas", "monospace"]`; **`preload: false` and `display: "swap"` untouched**
   (ruling 3). Extend the file's P4.F5 comment with one paragraph for the mono face (the Arial
   131.49 % fact, and why a mono fallback is an exact match).
5. **Fit against the real thing before you bake it** (P4.F5 § 3): on the local production build
   at the throttled profile, every public route (`/`, `/stocks`, `/stocks/00547510`,
   `/portfolio` anonymous, `/ask`, `/events/20260806000329`) rendered webfont-loaded vs
   webfont-blocked with the candidate face — rect of every `body *`, `moved > 0.5 px` must be **0**
   with the derived number, and show one neighbour value on each side missing (the table shape
   P4.F5 published), so the shipped number is the derived one and the browser agrees.
6. Nothing else: no font file added or regenerated, no change to `--font-mono`'s tail, no `.mono`
   change, no preload, no test file.

## Verification (the shared bar, applied — plus the cold-cache profile, which is the point)

- `cd frontend && npm run typecheck`, `npm run smoke`; `npm run build` in a fresh copy outside the
  repo (no warnings) — and **grep the built CSS**: no `plexMono Fallback` `local(Arial)` face
  remains, the two hand families are present with the numbers you derived. HEAD control build
  on 3015 beside the fixed build on 3014, plus dev 3010 (dev serves the same `next/font` CSS —
  check the Arial face is gone there too).
- **The cold-cache sweep**, Aside `--account u2`, **412×915 @ DPR 2.625, 4× CPU, 150 ms /
  ≈1.6 Mbps, cache cleared, a fresh tab per load, 3 loads per cell, medians**, on the four routes
  R1 measured (`/`, `/stocks/00547510`, `/portfolio` anonymous, `/events/20260806000329`), fixed
  vs HEAD: R1's probe — resource timing for the two Plex files, a rect sample of every `.mono`
  element (and R1's named ones: `DDay__dday`, `Lookup__cval`, `DDay__label`, `rowWhen` /
  `holdingDDay`, `sharesValue`, `statValue`) at each `document.fonts` load event and at settle.
  Pass = HEAD reproduces R1's deltas (the control: 106.13 → 92.42 etc.), the fixed build's
  per-element width delta across the Plex swap is **0 (≤ 0.25 px sub-pixel drift, say the max)**
  on every route, and no `layout-shift` entry lands near either Plex file's `responseEnd`.
- **Warm rendering `AE = 0`** vs HEAD, fonts loaded, **1280 and 390**, on those four routes with
  a positive control (F6's traps: one capture per invocation, no `fullPage` under emulation,
  scrollbar strip excluded) — the loaded webfont must not move a pixel; the fallback faces only
  exist in the swap window.
- **The swap window itself, seen:** one paused-frame capture per route at the throttled profile
  before the Plex files land (block them for the shot) on the fixed build — numerals in the
  fallback face at Plex's exact widths — and the same frame after; name the diff box (glyph
  shapes differ, geometry does not).
- **Production, read-only, as the "before":** R1's numbers stand; one re-measurement of
  `/stocks/00547510` on `https://jujutower.com` at the profile is optional and must write nothing.
- **Console / hydration:** the F6 shim, proven live, on every measured load — nothing on the
  production build.
- Hygiene: production read-only; 3014/3015 stopped; `make stack-status` as found; no font
  binaries added to the repo.
- `python3 scripts/workflow.py validate`.

## Notebook when you finish

- `## Decisions`: one line — the mono fallback faces (the faces, the measured numbers with their
  divisions, `adjustFontFallback: false`, the Arial 131.49 % face gone, the cold-cache
  after-numbers, Windows unclosed at 100 %).
- `## Operator Questions`: **Q2 is answered by this fix** — do not edit Q2 (append-only); say so
  in `## Now` so the review routes it as answered.
- `## Doc impact`: `frontend.md` — Type (the two faces, the P4.F5 method applied to the mono face,
  the generated Arial face removed, cold-cache mono reflow 0) (P12.F9); and `qa.md` only if the
  cold-cache sweep gains a mono line worth the checklist.
- `## Notes for later slices`: **add `(from P12.F9, for P12.S2)` only if the release needs
  something** — no font file is added, so probably nothing. Do not touch the shared bar, F1's
  seams note, or the `for P12.REVIEW` / `for P12.S2` notes.
- `## Now` (≤ 15 lines): F9 landed with numbers; every fix slice done; **`P12.S2` next** (the
  release — the orchestrator checks `origin/main` first); freeze date; production on `a74c58a`.

`result.md`, verdict block first: the metrics table (both ways), the fit table, the cold-cache
before/after table per route, the warm `AE = 0` line with its control, deviations.

## Do not

- preload the mono face, change `display`, add or regenerate a font file, name a bare family in
  `local()`, put an unadjusted face ahead of the hand ones, touch `--font-mono`'s tail or `.mono`,
  add a test file, commit, run any workflow state command, write on production, or drive Aside `u0`.
