import type { Metadata, Viewport } from "next";
import type { ReactNode } from "react";
import { SiteChrome } from "@/components/chrome";
import { notoSansKr, plexMono } from "./fonts";
import "./shell.css";

/**
 * The root layout: the cosmos page root, the Korean document language, the two
 * self-hosted faces, and the vendored token sheet.
 *
 * `tokens.css` is still served as a static file from `public/foundations/` rather
 * than imported through the bundler: it must stay byte-verbatim (R8 signed it
 * that way, Token delta: None), which rules out the bundler rewriting anything
 * inside it.
 *
 * **`fonts.css` is gone** (P10.S7). It was the other vendored foundation — a
 * class-A R1 export marked "do not edit" — and it did two things this app no
 * longer wants: it `@font-face`d a **2,057,688-byte** un-subset Pretendard
 * Variable, and it `@import`ed IBM Plex Mono from the Google Fonts CDN. Both are
 * replaced by `next/font/local` subsets in `./fonts.ts` at 330,480 B total and no
 * third-party origin. The retirement is operator-directed (research changple_web,
 * use the same) and recorded in `public/assets/README.md` with the sha256 of what
 * left, exactly the way the four retired `mijual-*.png` are recorded.
 *
 * The hand-written `<link>` to the Plex Mono CDN went with it. It existed only
 * because the landed `fonts.css` put its `@import` *after* an `@font-face`, where
 * CSS drops it — an apply-time workaround against a landed nit, and the nit's file
 * is now retired, so the workaround has nothing left to work around.
 */
export const metadata: Metadata = {
  // The product's own name, unspaced (`docs/current/product.md`; P10 renamed it).
  // No tagline, no description: the signed design writes no document-level copy,
  // and inventing a Korean sentence would be a design change.
  //
  // **No `icons` key, and that is not the old gap.** The favicon question the
  // assets README held open ("this mark does not become one") was answered at the
  // P10 gate: the operator delivered a square symbol export, R17 §2 made the
  // sparkle a first-class mark and specified the tiles — an opaque `#0a1310`
  // square, the white symbol at the 84% ink-width rule, sizes 16 / 32 / 180 with
  // 16 a downscale of the 32 raster rather than separate artwork. Nothing was
  // cropped out of the wordmark, so the README's "no image is substituted,
  // generated or placeheld" rule is *satisfied*, not relaxed.
  //
  // The tiles ship as Next `app/` file conventions — `app/icon.png` (32),
  // `app/icon1.png` (16), `app/apple-icon.png` (180) — so Next emits the `<link
  // rel="icon">` / `<link rel="apple-touch-icon">` tags itself, with hashed URLs
  // and correct `sizes`. Hand-written tags here would be a second source of truth
  // for the same files.
  title: "주주의관제탑",
};

export const viewport: Viewport = {
  // Mobile-first (R1: breakpoints 480 / 768 / 1120). No `maximum-scale` and no
  // `user-scalable=no` — pinch zoom stays available.
  width: "device-width",
  initialScale: 1,
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    // Korean-only product surface. `class="cosmos"` on the page root is R2.1's
    // own mechanism: it remaps every token so the R1 components render correctly
    // unchanged, and `shell.css` sets `color: var(--ink-1)` on it as specified.
    // The two font variables are declared here, on <html>, so `app/shell.css` can
    // point the vendored `--font-sans` / `--font-mono` tokens at them without
    // editing the frozen `foundations/tokens.css`.
    <html lang="ko" className={`cosmos ${notoSansKr.variable} ${plexMono.variable}`}>
      <head>
        <link rel="stylesheet" href="/foundations/tokens.css" />
      </head>
      {/* R2 designs the landing *and* the global chrome every later surface
          lives in, so the nav/footer/mobile sheet wrap every route from here —
          one nav, one footer, and vocky's script loaded once for the whole app
          (`components/chrome/`). A page still renders its own `<main>`. */}
      <body>
        <SiteChrome>{children}</SiteChrome>
      </body>
    </html>
  );
}
