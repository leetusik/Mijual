# P4.F5 — Korean-capable font fallback metrics: kill the cold-cache layout shift

`kind: fix`, `risk: high`, `slice-executor-high`. Cut from `P4.R1`'s ranked list (item 1, the one
real Core Web Vitals defect the research found). Operator instruction behind it (2026-09-02,
verbatim): 「you look up the cloudflare's poor LCP, INP, and CLS performance stuffs … and create
slices for fix them.」 Frontend only. **No deploy in this slice** — `P4.S9` releases F5 + F6 + F8
together, so this slice ends with the change verified on a **local production build**.

## The defect, as measured (do not re-derive; `slices/P4.R1/result.md` § 2 has the raw runs)

On a cold cache at the mobile profile (412×915, DPR 2.625, 4× CPU, ≈1.6 Mbps / 150 ms RTT) every
route shifts once, and the timestamp of that shift tracks `NotoSansKR_subset….woff2`'s `responseEnd`
to within ~30 ms: `/` CLS **0.095**, `/stocks` **0.138**, `/ask` **0.089**, a live event page
**0.033** (desktop: ≤ 0.011, because the font lands before first paint). Blocking that one URL gives
**0.000** on every route. The mechanism is in the served CSS:

```
@font-face{font-family:notoSansKr;src:url(…NotoSansKR_subset….woff2);font-display:swap;font-weight:100 900}
@font-face{font-family:notoSansKr Fallback;src:local(Arial);ascent-override:117.61%;descent-override:29.2%;line-gap-override:0.0%;size-adjust:98.63%}
```

`next/font/local`'s generated metric-matched fallback is `local(Arial)`. **Arial has no Hangul**, so
every Korean glyph paints in the next family of the stack (`system-ui` → Apple SD Gothic Neo on
macOS/iOS, Malgun Gothic on Windows, Noto Sans CJK KR on Android/Linux) with **no metric override at
all**; when the 291,072 B subset arrives the whole document re-wraps. The shift sources are whole
bands (`footer`, `section.Lookup…`, `span.RightsChip…`, `section.Event…facts`), i.e. a document-wide
reflow, not a missing `width`/`height` anywhere.

**Two things R1 measured so nobody spends this slice on them:** `<link rel=preload>` for the font
changes nothing (the request already starts at ~400 ms; the 3 s is transfer), and `Countdown`'s tick
costs nothing. And one thing this slice must **not** decide: `font-display: optional` would also give
CLS 0, at the price of a first visit rendered entirely in the system face — that is a **design**
choice (R1/R2 signed Noto Sans KR as the product's face), not yours; if the metric route cannot get
below the target, return `needs_operator` with the numbers and let the operator choose.

## Do

1. **Replace the Arial fallback with Korean-capable metric-matched fallback faces.** In
   `frontend/app/fonts.ts` set `adjustFontFallback: false` on `notoSansKr` (Next 16.3 accepts
   `'Arial' | 'Times New Roman' | false`) so the useless `notoSansKr Fallback` face is no longer
   generated, and declare your own faces in `frontend/app/shell.css` next to the `html:root` token
   block — one `@font-face` per platform face, each with **measured** `size-adjust`,
   `ascent-override`, `descent-override`, `line-gap-override`:
   - `local("Apple SD Gothic Neo")` (macOS / iOS — the operator's runtime and most Korean phones'
     Safari; the lab can verify this one first-hand);
   - `local("Malgun Gothic")` (Windows; metrics from the face's published values or a Windows
     measurement if one is at hand — otherwise carry Apple's numbers and **say so**);
   - `local("Noto Sans CJK KR")` / `local("Noto Sans KR")` (Android / Linux; same caveat).
   Give each family a distinct name (e.g. `"Noto Sans KR Fallback Apple"`), and put them **ahead
   of `system-ui`** in `fonts.ts`'s `fallback` array so the variable Next emits (`--font-noto-sans-kr`)
   carries them; then mirror the same order in `shell.css`'s `--font-sans` literal tail (it lists
   `"Noto Sans KR", system-ui, -apple-system, "Apple SD Gothic Neo", "Malgun Gothic", sans-serif`
   today — the bare `"Apple SD Gothic Neo"` entry after `system-ui` becomes redundant; keep the tail
   coherent). Read the built CSS (`.next/static/css/*.css` in your build copy) and confirm the
   emitted stack is what you intend before measuring.
   **Weights matter:** the site uses 400 / 500 / 600 / 700 (the hero `h1` is 700 at 34 px mobile /
   52 px desktop). A single-weight `local()` face makes the browser synthesize bold and the
   synthesized widths differ from the real bold; if the measurement shows that, declare per-weight
   faces (`font-weight: 700; src: local("AppleSDGothicNeo-Bold")`, etc.) rather than accept the
   residual. Plex Mono keeps its generated fallback unless your measurement shows numerals shifting
   (R1 attributed **every** shift to the Korean face).
2. **Measure the overrides, do not guess them.** Two acceptable methods, your pick:
   - *In the browser* (matches what Chrome actually renders): in the CDP session, render the same
     Korean sample — the hero title, a board row's company name + chip, the lookup caption, a footer
     line — once in `notoSansKr` (font loaded) and once in the candidate local face, read
     `getBoundingClientRect()` widths and `TextMetrics.fontBoundingBoxAscent/Descent` from a canvas
     `measureText`, and derive `size-adjust = width_noto / width_fallback`,
     `ascent-override = (ascent_noto / em) / size-adjust`, likewise descent, `line-gap-override: 0%`.
   - *From the font tables*: `uvx --from fonttools python -c …` (a tool run, **not** `uv run --with`,
     and no new project dependency) reading `hhea`/`OS/2` and average Hangul advance from
     `frontend/app/fonts/NotoSansKR.subset.woff2` and `/System/Library/Fonts/AppleSDGothicNeo.ttc`.
   Either way, **then iterate against the real thing**: cold-cache loads at the mobile profile with
   `PerformanceObserver` on `layout-shift` (R1's harness — `scratchpad/r1_cdp.py`, the load runner
   and the JSONL it wrote are cited by path in `slices/P4.R1/result.md` § method; reuse them). The
   target is **CLS ≤ 0.01 on `/`, `/stocks`, `/ask` and a live `/events/{rcept_no}`**, three cold
   loads each, medians, against the **local production build** (a copy of `frontend/` as R1 did —
   `scratchpad/r1fe` or a fresh copy — built with `NEXT_PUBLIC_SITE_URL=https://jujutower.com npm run
   build`, served by `node .next/standalone/server.js` on **:3014** with `.next/static` and `public/`
   staged in, against the dev API on 8010; never `next start`, which Next 16 refuses under
   `output: "standalone"`; the operator's dev stack on 3010/8010 stays up). Report before/after per
   route, and the residual shift sources if any. Emulated throttling is what makes the swap fire
   after first paint, so keep the profile exactly R1's; also run the desktop profile once per route
   to show nothing regressed there (it was ≤ 0.011).
3. **Screenshot equivalence after the swap.** Once the webfont has loaded the page must look
   identical to today: capture `/` and `/stocks` at 390 and 1280 on the build copy before and after
   your change (both with the font loaded) and compare (pixel diff — `magick compare -metric AE`, or
   a CDP screenshot byte compare); the only acceptable difference is none. The fallback faces change
   what a reader sees **only during the swap window** (a metric-matched system face instead of an
   unmatched one), which is not a signed visual.
4. **Instrument**: real Google Chrome over CDP, headful, throwaway profile in the scratchpad, fresh
   port (`open -na "Google Chrome" --args --remote-debugging-port=<p> --user-data-dir=<dir>`; a
   `nohup` launch is headless and does not count; never the operator's profile). Cold cache per
   load: `Network.clearBrowserCache` + a fresh tab, or a fresh profile. Name the instrument, ports,
   sample counts in `result.md`; stop every browser and server you start (record pids).
5. **No test file** — this is exactly the visual/cosmetic surface the contract says is verified
   live. `npm run lint` and `npx tsc --noEmit` (or the repo's equivalent — check `package.json`
   scripts) must stay clean; `npm run build` must succeed in the copy.
6. **`phase.md`**: `## Decisions` — one line: the Korean fallback faces are metric-matched to Noto
   Sans KR (which faces, the measured numbers, the verified CLS), `font-display` stays `swap`;
   `## Doc impact` — `frontend` (Fonts: `adjustFontFallback: false`, the hand-declared fallback
   faces in `shell.css` and why Arial could not work; how to re-measure if the subset is
   regenerated) and `qa` (the regression line: cold-cache mobile CLS ≤ 0.01 on the four routes, and
   the method — a `*/*` fetch cannot see any of this); consume the `(from P4.R1, for the fix slices)`
   item 1 by marking it done in place (leave items 2–5 for their slices); rewrite `## Now` (≤ 15
   lines): F5 done and **not yet deployed**, `P4.F6` next, then `P4.F8`, then `P4.S9` (the batched
   frontend-only release, before **2026-09-07 11:00 KST**, aim 09-05), then the re-review; keep the
   gate-shut line.
7. **`result.md`** verdict-block-first: the measured metrics per face, the before/after CLS table,
   the screenshot equivalence result, the built-CSS excerpt showing the emitted stack (no secrets
   exist here), deviations. If the target cannot be reached on some route, say which, with the
   residual sources, and return `needs_operator` only if the remaining lever is the design choice
   above.

## Hard rules

Frontend files only (`frontend/app/fonts.ts`, `frontend/app/shell.css`, nothing else unless a
literal stack elsewhere must mirror the change — grep for `Apple SD Gothic Neo` and `--font-sans`
first and say what you found); **no deploy, nothing on the box, production read-only** (you may
load production pages to compare the shipped CSS, nothing more); never the operator's Chrome
profile; keep 3010/8010 up; the repo is public — no secret values; no `git commit`/`push`; no
workflow state commands other than `python3 scripts/workflow.py validate`; `uv run` without
`--with`. **RESPECT THE DESIGN**: the loaded-font rendering must not change by a pixel.

## Validate

`npm run build` in the copy succeeds; lint/typecheck clean; the CLS table shows ≤ 0.01 on the four
routes at the mobile profile (medians of 3) and no desktop regression; screenshot equivalence holds;
`python3 scripts/workflow.py validate` passes; `git diff --stat` → the two frontend files (plus any
mirrored literal), `phase.md`, this slice's `result.md`.
