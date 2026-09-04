import localFont from "next/font/local";

/**
 * The two self-hosted faces, delivered by `next/font/local`.
 *
 * Adopted from `~/projects/personal/changple_web/src/app/fonts.ts` at the operator's instruction
 * ("research changple_web's case for the korean font. use same with it"), which is why the shape,
 * the fallback stacks, the `display`/`preload` split and the subsetting scripts are theirs. What
 * this replaces:
 *
 * - **Pretendard Variable**, self-hosted per R1 as a **2,057,688-byte** un-subset woff2 reached
 *   through the vendored `public/foundations/fonts.css`. Both are retired by P10 (the file and the
 *   binary are recorded in `public/assets/README.md` the way the four `mijual-*.png` are).
 * - **IBM Plex Mono from the Google Fonts CDN** — an `@import` the R1 record wrote inside
 *   `fonts.css` in a position where CSS drops it, which `layout.tsx` had been re-linking by hand.
 *   Self-hosting removes a third-party origin from every page load.
 *
 * Shipped payload: **291,072 B** Korean + **39,408 B** mono = 330,480 B, against 2,057,688 B and a
 * cross-origin stylesheet before. `scripts/subset_noto_sans_kr.sh` carries the coverage measurement
 * that chose the Korean number, which is the one place this repo deliberately departs from
 * changple_web: Mijual renders **dynamic DART company names** everywhere, so its subset has to
 * cover text that does not exist at build time.
 *
 * **`foundations/tokens.css` is not edited.** It is frozen R8 material and still defines
 * `--font-sans` / `--font-mono` as Pretendard and CDN Plex Mono; `app/shell.css` overrides those two
 * variables to point here. Application code overriding a vendored token is exactly what R17 did
 * inside its own cards, and it recorded the token as **not** superseded.
 */

/**
 * Noto Sans KR, self-hosted, subset — the product's body face and the one every Korean string
 * renders in. Regenerate with `scripts/subset_noto_sans_kr.sh`.
 *
 * changple_web chose this face over Pretendard deliberately, for "cleaner heavy-weight (700/900)
 * Korean rendering", and the operator's instruction was to use the same. The full `wght 100 900`
 * axis is kept: measured on this source, instancing it down to 400–700 does not shrink the file
 * (1,053,156 B vs 1,022,828 B on the full-block subset — very slightly *larger*), so the axis is
 * free and the weights R1 signed all stay reachable.
 *
 * `preload: true` — this is the face every visible glyph on every surface needs.
 *
 * ── `adjustFontFallback: false`, and why Next's generated fallback could not work (P4.F5) ────────
 *
 * Left at its default, `next/font/local` generates a second `@font-face` — `notoSansKr Fallback`,
 * `src: local(Arial)`, `size-adjust: 98.63%`, `ascent-override: 117.61%` — and **Arial carries no
 * Hangul**. So on a cold cache every Korean glyph painted in whatever came *next* in this array
 * with no metric override at all, and the whole document re-wrapped when the 291,072-byte subset
 * landed 3 s later. Measured in `P4.R1`: mobile CLS `/` 0.095, `/stocks` 0.138, `/ask` 0.089, and
 * 0.000 on every route with the font blocked. Preloading was measured and does nothing — the
 * request already starts at ~400 ms; the 3 s is transfer.
 *
 * The three families below are declared by hand in `app/shell.css` with **measured** overrides
 * (one per platform face: Apple SD Gothic Neo, Noto Sans CJK KR, Malgun Gothic) and sit **ahead of
 * `system-ui`** so they are what a cold visit paints in. `font-display` stays `swap`: the product's
 * face is still Noto Sans KR and it still swaps in — it just no longer moves anything when it does.
 * Do not put a bare "Apple SD Gothic Neo" / "Malgun Gothic" in front of them; that is the
 * unadjusted face this fix exists to stop using.
 */
export const notoSansKr = localFont({
  src: "./fonts/NotoSansKR.subset.woff2",
  weight: "100 900",
  style: "normal",
  display: "swap",
  preload: true,
  variable: "--font-noto-sans-kr",
  adjustFontFallback: false,
  fallback: [
    "notoSansKr Fallback Apple",
    "notoSansKr Fallback Noto",
    "notoSansKr Fallback Malgun",
    "system-ui",
    "-apple-system",
    "sans-serif",
  ],
});

/**
 * IBM Plex Mono, self-hosted, Latin-only subsets — R1's numeral face. Regenerate with
 * `scripts/subset_plex_mono.sh`.
 *
 * Three static faces rather than one variable woff2: google/fonts ships no variable Plex Mono at
 * the pinned commit. The three weights are **400 / 500 / 600**, exactly the set the retired CDN
 * request asked for (`…IBM+Plex+Mono:wght@400;500;600`), so no weight R1 signed is silently lost.
 *
 * `preload: false` — mono is numerals and chips, not the body face, and it must not compete with
 * the Korean subset for the critical font budget. **Unchanged by `P12.F9`**, and so is
 * `display: "swap"`: the fix below costs no network at all.
 *
 * ── `adjustFontFallback: false`, and why Arial could not work here either (P12.F9) ───────────────
 *
 * Left at its default, `next/font/local` generated `plexMono Fallback` — `src: local(Arial)`,
 * `size-adjust: 131.49%` — and **Arial is proportional**. There is no single number that maps a
 * proportional face onto a monospace one, so every numeral painted ~15 % too wide until the 12 kB
 * Regular and 13 kB SemiBold subsets landed and re-flowed it: 「0.0863800841」 **113.53 → 97.20 px**
 * on a cold mobile load, measured by `P12.R1` on the production build *and* on jujutower.com. It was
 * Noto's pre-`P4.F5` state, one face over — and the remedy is the same one, with one difference in
 * its favour: a **monospace** fallback has one advance for every glyph, so a single `size-adjust`
 * matches every string exactly rather than on average.
 *
 * The faces below are declared by hand in `app/shell.css` with **measured** overrides (Menlo, which
 * is what Chrome actually paints this stack in — `ui-monospace` / `SFMono-Regular` / `"SF Mono"`
 * resolve to nothing there, and SF Mono is unreachable through `local()`; plus Consolas for
 * Windows, vertical metrics only). They are restricted by `unicode-range` to our Latin-only
 * subsets' own coverage, and `"plexMono Fallback Arial"` re-declares Next's generated face verbatim
 * behind them, so the `←` and `→` that only ever painted in Arial still do. Read that block before
 * changing anything here. Do not put a bare `ui-monospace` / `Consolas` in front of them; that is
 * the unadjusted face this fix exists to stop using.
 */
export const plexMono = localFont({
  src: [
    { path: "./fonts/IBMPlexMono-Regular.subset.woff2", weight: "400", style: "normal" },
    { path: "./fonts/IBMPlexMono-Medium.subset.woff2", weight: "500", style: "normal" },
    { path: "./fonts/IBMPlexMono-SemiBold.subset.woff2", weight: "600", style: "normal" },
  ],
  display: "swap",
  preload: false,
  variable: "--font-plex-mono",
  adjustFontFallback: false,
  fallback: [
    "plexMono Fallback Apple",
    "plexMono Fallback Windows",
    "plexMono Fallback Arial",
    "ui-monospace",
    "SFMono-Regular",
    "SF Mono",
    "Consolas",
    "monospace",
  ],
});
