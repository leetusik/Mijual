import type { MetadataRoute } from "next";
import {
  BACKGROUND_COLOR,
  SITE_DESCRIPTION_KO,
  SITE_NAME,
  THEME_COLOR,
} from "@/lib/seo";

/**
 * `/manifest.webmanifest` (Next file convention).
 *
 * Colours are the **cosmos** `--paper` (`#0a1310`) in both slots, because
 * `app/layout.tsx` puts `class="cosmos"` on `<html>` unconditionally — there is
 * no light surface of this product for a light manifest to describe. `lib/seo.ts`
 * holds both literals and says why they are literals rather than token reads.
 *
 * `lang: "ko"` and `dir: "ltr"`: Korean-only product surface, stated rather than
 * inferred.
 *
 * ## The icon set is five files and every one of them already existed or is a
 * recorded derivative
 *
 * The three `app/` tiles are R17/R18's — Next serves them at `/icon.png` (32),
 * `/icon1.png` (16) and `/apple-icon.png` (180), and it emits their `<link>` tags
 * itself from the file conventions; naming them here as well costs nothing and
 * gives an installer the small sizes. The two large ones, 192 and 512, are new
 * files and therefore **class-C derivatives produced by one recorded ImageMagick
 * command each** from `juju2-symbol-white.png` — the same recipe, the same
 * `#2b8e6c` ink and the same 75 % placement rule R18 signed for the favicons,
 * with the geometry recomputed for the two sizes. Both commands, their measured
 * ink boxes and their signatures are in `public/assets/README.md`.
 *
 * They are transparent for R18's own reason: the ink colour, not a background,
 * carries the contrast (4.05 on white, 3.98 on a dark tab), so one asset serves
 * whatever surface an OS composites a home-screen icon onto.
 */
export default function manifest(): MetadataRoute.Manifest {
  return {
    name: SITE_NAME,
    short_name: SITE_NAME,
    description: SITE_DESCRIPTION_KO,
    lang: "ko",
    dir: "ltr",
    start_url: "/",
    display: "standalone",
    background_color: BACKGROUND_COLOR,
    theme_color: THEME_COLOR,
    icons: [
      { src: "/icon1.png", sizes: "16x16", type: "image/png" },
      { src: "/icon.png", sizes: "32x32", type: "image/png" },
      { src: "/apple-icon.png", sizes: "180x180", type: "image/png" },
      { src: "/assets/juju2-icon-192.png", sizes: "192x192", type: "image/png" },
      { src: "/assets/juju2-icon-512.png", sizes: "512x512", type: "image/png" },
    ],
  };
}
