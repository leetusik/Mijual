import type { Metadata, Viewport } from "next";
import type { ReactNode } from "react";
import { SiteChrome } from "@/components/chrome";
import { JsonLd } from "@/components/seo/json-ld";
import { getSiteContact } from "@/lib/api";
import {
  GOOGLE_SITE_VERIFICATION,
  NAVER_SITE_VERIFICATION,
  OG_IMAGE,
  SITE_DESCRIPTION_KO,
  SITE_NAME,
  SITE_URL,
  THEME_COLOR,
  TITLE_DEFAULT,
  TITLE_TEMPLATE,
} from "@/lib/seo";
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
  //
  // **This block used to say "no tagline, no description", and that is no longer
  // the rule.** It was true of every slice before this one: the signed design
  // record writes no document-level copy, so inventing a Korean sentence here
  // would have been a design change made in an implementation slice. What changed
  // is not the constraint but the *route* — `P4.DECOMP` settled that a phase may
  // **draft** this copy and the operator **approves the exact strings literally at
  // the P4 acceptance gate**, which is a decision the operator takes on the
  // running product rather than one an executor takes alone. It is the same
  // ruling `src/mijual/mailcopy.py` ships the D-day mail's copy under.
  //
  // So none of the Korean below is written here. Every string, with its
  // provenance line — transcribed from a signed round, or drafted by `P4.S5` and
  // derived from one — lives in **`lib/seo.ts`**, the single typed source this
  // file, `app/robots.ts`, `app/sitemap.ts`, `app/manifest.ts`,
  // `components/seo/json-ld.tsx` and both `generateMetadata` routes all read.
  //
  // **`alternates` is deliberately absent from this object.** `alternates` is
  // inherited *as a whole* by every child segment, so an `alternates: { canonical:
  // "/" }` here would make every route that does not set its own claim the home
  // page as its canonical — the single most damaging thing a metadata block can
  // do, and invisible in review because the tag looks correct on `/`. Canonicals
  // are set **per indexable route** instead (the three static pages and the two
  // `generateMetadata` routes).
  //
  // **No `icons` key, and that is not the old gap.** The favicon question the
  // assets README held open ("this mark does not become one") was answered at the
  // P10 gate: the operator delivered a square symbol export, R17 §2 made the
  // sparkle a first-class mark and specified the tiles, sizes 16 / 32 / 180 with
  // 16 a downscale of the 32 raster rather than separate artwork. Nothing was
  // cropped out of the wordmark, so the README's "no image is substituted,
  // generated or placeheld" rule is *satisfied*, not relaxed.
  //
  // **`P10.review` (R18 §③) re-cut the tiles and superseded two of R17's
  // numbers.** They are no longer an opaque `#0a1310` square carrying white ink:
  // the tile is **transparent** and the ink is a single literal `#2b8e6c`, chosen
  // to read on a light tab (4.05) and a dark one (3.98) without leaning either
  // way — which is what makes the background unnecessary. And the ink width is
  // **75%** here, not R17's 84%: at 84% a 32px tile left only 2px between the
  // left sparkle and the tile edge. **The launcher keeps 84%** — same artwork,
  // different surface, deliberately divergent placement rules
  // (`components/ask/Launcher.module.css`). `#2b8e6c` is an ImageMagick literal
  // for compositing, not a token: `public/foundations/tokens.css` stays frozen.
  //
  // The tiles ship as Next `app/` file conventions — `app/icon.png` (32),
  // `app/icon1.png` (16), `app/apple-icon.png` (180) — so Next emits the `<link
  // rel="icon">` / `<link rel="apple-touch-icon">` tags itself, with hashed URLs
  // and correct `sizes`. Hand-written tags here would be a second source of truth
  // for the same files. `manifest.ts` is the same arrangement — a file convention
  // whose `<link rel="manifest">` Next emits itself.
  //
  // `app/opengraph-image.png` is the one **exception**, and `lib/seo.ts` measured
  // why: a file-convention image attaches to its own segment only, so left
  // implicit it reached `/` and no other route. The file still serves the image;
  // its tags are declared below and in `routeMetadata`, from one `OG_IMAGE`.
  metadataBase: new URL(SITE_URL),
  title: { default: TITLE_DEFAULT, template: TITLE_TEMPLATE },
  description: SITE_DESCRIPTION_KO,
  applicationName: SITE_NAME,
  openGraph: {
    type: "website",
    locale: "ko_KR",
    url: "/",
    siteName: SITE_NAME,
    title: TITLE_DEFAULT,
    description: SITE_DESCRIPTION_KO,
    images: [OG_IMAGE],
  },
  // `images` is stated rather than left to the `app/opengraph-image.png` file
  // convention, and `lib/seo.ts` explains why at length: the convention attaches
  // the image to **this segment only**, while a child that sets `openGraph`
  // replaces the whole object — so left implicit, `/` had a share card and every
  // other route had none (measured on the production build, `P4.S5`).
  twitter: {
    card: "summary_large_image",
    title: TITLE_DEFAULT,
    description: SITE_DESCRIPTION_KO,
    images: [OG_IMAGE],
  },
  // The product's default posture. The four non-reader surfaces override it with
  // `index: false, follow: false` on their own segments; `app/robots.ts` disallows
  // the same four prefixes.
  robots: { index: true, follow: true },
  // Search-engine ownership, HTML-tag method, and **each token is spread in only
  // when set** — an unset *or* empty value must render no tag at all, never a
  // blank `content=""`. Google's property is a DNS-TXT domain property held at
  // Cloudflare and needs nothing here; Naver Search Advisor is the one that would
  // need a token, and whether to register is an open operator question. Both are
  // build args (`NEXT_PUBLIC_*`), so adding one is a rebuild.
  verification: {
    ...(GOOGLE_SITE_VERIFICATION ? { google: GOOGLE_SITE_VERIFICATION } : {}),
    ...(NAVER_SITE_VERIFICATION
      ? { other: { "naver-site-verification": NAVER_SITE_VERIFICATION } }
      : {}),
  },
};

export const viewport: Viewport = {
  // Mobile-first (R1: breakpoints 480 / 768 / 1120). No `maximum-scale` and no
  // `user-scalable=no` — pinch zoom stays available.
  width: "device-width",
  initialScale: 1,
  // The cosmos `--paper`. `<html class="cosmos">` below is unconditional, so the
  // browser chrome around the page matches the page in every context; D5 named
  // the missing theme-color and this is it. One value, no `media` variants,
  // because there is no light surface of this product to switch to.
  themeColor: THEME_COLOR,
};

/** How long a served 운영자 연락처 stays good. The value changes almost never and
 * the footer renders on **every** page, so a fetch per render would be waste; ten
 * minutes is the cost of changing it, which is the right thing to be slow. */
const CONTACT_REVALIDATE_S = 600;

/** And how long a page waits for it. The footer is chrome: it must draw whether
 * or not the API answers, so a hanging service costs the contact line and nothing
 * else (`P11.F1` learned the same lesson on the start cards). */
const CONTACT_TIMEOUT_MS = 2000;

export default async function RootLayout({ children }: { children: ReactNode }) {
  // **The 운영자 연락처 is read here, not in the footer** (`P11.F2`). `SiteChrome`
  // is a client component — it branches on the pathname — so everything below it,
  // `SiteFooter` included, is client code and cannot read the API on the server.
  // This layout is the nearest server component, and it is also the only place
  // the read happens once for every route rather than once per page.
  //
  // The setting itself (`MIJUAL_OPERATOR_CONTACT`) belongs to the API and the
  // Next process cannot see it: `make web-up` passes only `MIJUAL_DEV_ORIGINS`
  // and there is no `frontend/.env`. Serving it keeps one source of truth for a
  // string the AI 질문 agent also hands out.
  //
  // A failure is `null`, and `null` is a rendered state: the footer simply
  // carries no contact line. Nothing here throws and nothing renders a spinner.
  const contact = await getSiteContact({
    next: { revalidate: CONTACT_REVALIDATE_S },
    signal: AbortSignal.timeout(CONTACT_TIMEOUT_MS),
  }).catch(() => null);

  return (
    // Korean-only product surface. `class="cosmos"` on the page root is R2.1's
    // own mechanism: it remaps every token so the R1 components render correctly
    // unchanged, and `shell.css` sets `color: var(--ink-1)` on it as specified.
    // The two font variables are declared here, on <html>, so `app/shell.css` can
    // point the vendored `--font-sans` / `--font-mono` tokens at them without
    // editing the frozen `foundations/tokens.css`.
    //
    // **`suppressHydrationWarning` is scoped to this element and deliberate**
    // (`P11.F3`). Chrome writes `__gchrome_remoteframetoken="…"` onto
    // `<html>` after the document is parsed and before React hydrates, so the
    // client element carries an attribute the server never rendered and React
    // reports an attribute mismatch on every load. No server change can prevent
    // it — the browser, not this app, adds the attribute — and the operator met
    // it as a dev-overlay error on mobile.
    //
    // Know the cost. The flag covers **this element only**: its own attributes
    // and its direct text, never its descendants. So it also hides a *genuine*
    // `<html>`-level mismatch — the `lang` or the two font variables above
    // changing between server and client — which is an accepted trade because
    // all three are literals with no runtime input. Everything below `<html>`
    // still reports normally, and that is the point: `P11.F3` found a real text
    // mismatch one level down in the same pass (`app/not-found.tsx`, D34's
    // signature) and it was findable only because nothing below `<html>` is
    // suppressed. Do **not** copy this flag onto `<body>` or `SiteChrome` —
    // that would blind exactly the subtree the next such fault will show up in.
    <html
      lang="ko"
      className={`cosmos ${notoSansKr.variable} ${plexMono.variable}`}
      suppressHydrationWarning
    >
      <head>
        <link rel="stylesheet" href="/foundations/tokens.css" />
        {/* Organization + WebSite structured data, **inline** — the one shape of
            structured data that does not cost this product its measured
            no-third-party-origin property. It reads the 운영자 연락처 already
            fetched below rather than fetching anything of its own. */}
        <JsonLd contact={contact} />
      </head>
      {/* R2 designs the landing *and* the global chrome every later surface
          lives in, so the nav/footer/mobile sheet wrap every route from here —
          one nav, one footer, and vocky's script loaded once for the whole app
          (`components/chrome/`). A page still renders its own `<main>`. */}
      <body>
        <SiteChrome contact={contact}>{children}</SiteChrome>
      </body>
    </html>
  );
}
