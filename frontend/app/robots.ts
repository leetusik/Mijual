import type { MetadataRoute } from "next";
import { SITE_URL } from "@/lib/seo";

/**
 * `/robots.txt` (Next file convention).
 *
 * ## Cloudflare **prepends** its own block to this one
 *
 * Measured by `P4.S4` before any of this existed: `https://jujutower.com/robots.txt`
 * already answered **200 with 1,836 bytes** of Cloudflare-managed content-signals
 * — `Disallow: /` for `GPTBot`, `Google-Extended`, `meta-externalagent` and the
 * rest — while the **origin 404'd**. The managed block is not replaced by this
 * file; it is prepended to it. So the signals are deliberately **not duplicated
 * here** (two sources for one rule is how they drift), and the file that matters
 * is the *served* one, not this route's output — `P4.S6` re-reads it after the
 * deploy.
 *
 * ## The four disallowed prefixes, and one honest caveat about them
 *
 * `/api/` is the rewrite to FastAPI: a JSON contract, never a page.
 * `/ops`, `/auth/` and `/portfolio` are the product's non-reader surfaces, and
 * each **also** carries `robots: { index: false, follow: false }` on its own
 * segment (`P4.S5`). The caveat is real and recorded rather than papered over: a
 * `Disallow` stops the crawl, and a crawler that never fetches the page never
 * reads its `noindex` — so for `/portfolio`, which **is** linked from the reader
 * nav (보유 종목), a URL-only index entry remains possible. The disallow is still
 * the right primary control (these surfaces are gated or operator-only and cost a
 * full SSR + FastAPI round trip per crawl), and the meta tag is the belt to its
 * braces for anything that fetches anyway.
 *
 * ## `/ops` is a literal here, and that is the rule rather than an exception
 *
 * `components/ops/routes.ts` exists so that **no reader module can import an ops
 * path** (R7: 「reader chrome 어디에서도 링크 금지 — nav·푸터·계정 메뉴·sitemap」),
 * and the cheapest way to keep that true is structural. Importing `OPS_ROOT` here
 * would put an ops symbol one autocomplete away from `app/`'s shared surface, to
 * save six characters. This route and `app/ops/layout.tsx`'s `noindex` are the
 * only two places in the app that may name the path at all, and `app/sitemap.ts`
 * names it nowhere — R7 lists the sitemap by name.
 */
export default function robots(): MetadataRoute.Robots {
  return {
    rules: {
      userAgent: "*",
      allow: "/",
      disallow: ["/api/", "/ops", "/auth/", "/portfolio"],
    },
    sitemap: `${SITE_URL}/sitemap.xml`,
  };
}
