import type { Metadata, Viewport } from "next";
import type { ReactNode } from "react";
import "./shell.css";

/**
 * The root layout: the cosmos page root, the Korean document language, and the
 * two vendored foundation stylesheets.
 *
 * The foundations are served as static files from `public/foundations/` rather
 * than imported through the bundler, for two reasons that both come from the
 * design record: `fonts.css` reaches Pretendard at `../assets/fonts/…`, which
 * resolves correctly only when the CSS is served from a URL that mirrors the
 * design project's own `foundations/` + `assets/` layout — so the landed file
 * needed no path edit at all — and the file must stay byte-verbatim, which rules
 * out the bundler rewriting its `url()` (and failing the build outright while the
 * binary is still missing).
 */
export const metadata: Metadata = {
  // The product's own name (`docs/current/product.md`). No tagline, no
  // description: the signed design writes no document-level copy, and inventing
  // a Korean sentence would be a design change.
  title: "미주알",
};

export const viewport: Viewport = {
  // Mobile-first (R1: breakpoints 480 / 768 / 1120). No `maximum-scale` and no
  // `user-scalable=no` — pinch zoom stays available.
  width: "device-width",
  initialScale: 1,
};

/**
 * The IBM Plex Mono CDN stylesheet, hoisted out of `fonts.css`.
 *
 * The landed `fonts.css` places its `@import url(…IBM+Plex+Mono…)` **after** the
 * `@font-face` block, and a CSS `@import` that does not precede every other rule
 * is invalid and dropped by every browser — so the mono face the design puts on
 * every numeral would silently never load. The record is read-only, so the file
 * is vendored exactly as it landed and the same URL is linked here instead: the
 * mechanism the round chose (Google Fonts CDN), in a position where it applies.
 * This is an apply-time to-do against a landed nit, never an edit to the record.
 */
const IBM_PLEX_MONO =
  "https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&display=swap";

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    // Korean-only product surface. `class="cosmos"` on the page root is R2.1's
    // own mechanism: it remaps every token so the R1 components render correctly
    // unchanged, and `shell.css` sets `color: var(--ink-1)` on it as specified.
    <html lang="ko" className="cosmos">
      <head>
        <link rel="stylesheet" href="/foundations/tokens.css" />
        <link rel="stylesheet" href="/foundations/fonts.css" />
        <link rel="stylesheet" href={IBM_PLEX_MONO} />
      </head>
      <body>{children}</body>
    </html>
  );
}
