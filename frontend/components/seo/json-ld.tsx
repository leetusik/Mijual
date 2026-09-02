import { SITE_DESCRIPTION_KO, SITE_NAME, SITE_URL } from "@/lib/seo";
import type { SiteContact } from "@/lib/types";

/**
 * The site's structured data — one inline `application/ld+json` `@graph`
 * carrying `Organization` + `WebSite`, rendered site-wide from the root layout.
 *
 * ## Inline, and that is a security property rather than a convenience
 *
 * `security.md` carries a **measured** signed property: no page of this product
 * contacts a third-party origin. It is why Cloudflare Web Analytics stays off
 * (P4 `## Decisions` — its `beacon.min.js` comes from
 * `static.cloudflareinsights.com`) and why the fonts were pulled off the Google
 * CDN in P10.S7. Structured data is the usual place a site quietly acquires a
 * `<script src>`; this one is a string this server renders, so the property
 * survives SEO intact. The edge's CSP is `upgrade-insecure-requests` only — no
 * `script-src` — so nothing here needs a nonce today, and the day one is added
 * this is the element it must cover.
 *
 * ## What it claims, and what it deliberately does not
 *
 * Every value comes from `lib/seo.ts` (the one typed source) or from the
 * **already-fetched** `GET /site/contact` the footer publishes on every page —
 * `email` and `phone`, and each only when the operator has actually set one.
 * Nothing here fetches, and nothing here is a new disclosure: the two contact
 * fields are the same two the footer prints in the visible page, three lines
 * further down. `null` is a state, so a product with no contact string simply
 * emits an Organization without contact keys.
 *
 * There is **no `sameAs`**, no address and no legal entity: this product
 * publishes none of them anywhere, and structured data is not the place to
 * start. A claim a reader cannot see on the page is a claim nobody signed.
 *
 * The two `@id`s are the conventional fragment addresses on the site's own
 * origin, so `publisher` is a reference rather than a second copy of the
 * organization.
 */
export function JsonLd({ contact }: { contact: SiteContact | null }) {
  const graph = [
    {
      "@type": "Organization",
      "@id": `${SITE_URL}/#organization`,
      name: SITE_NAME,
      url: SITE_URL,
      // The 180px launcher tile: the product's own mark in `#2b8e6c`, the ink
      // colour R18 chose precisely so one asset reads on a light surface and a
      // dark one (4.05 / 3.98). The white wordmark would be invisible wherever a
      // consumer paints a logo on white.
      logo: `${SITE_URL}/apple-icon.png`,
      description: SITE_DESCRIPTION_KO,
      ...(contact?.email ? { email: contact.email } : {}),
      ...(contact?.phone ? { telephone: contact.phone } : {}),
    },
    {
      "@type": "WebSite",
      "@id": `${SITE_URL}/#website`,
      url: SITE_URL,
      name: SITE_NAME,
      description: SITE_DESCRIPTION_KO,
      inLanguage: "ko-KR",
      publisher: { "@id": `${SITE_URL}/#organization` },
    },
  ];

  const data = { "@context": "https://schema.org", "@graph": graph };

  return (
    <script
      type="application/ld+json"
      // JSON.stringify escapes nothing HTML-significant on its own, and every
      // value here is either a literal from `lib/seo.ts` or an operator-set
      // contact string. `</script>` inside a JSON string is the one sequence that
      // would break out of the element, so it is escaped rather than trusted.
      dangerouslySetInnerHTML={{ __html: JSON.stringify(data).replace(/</g, "\\u003c") }}
    />
  );
}
