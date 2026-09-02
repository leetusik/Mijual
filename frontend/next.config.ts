import type { NextConfig } from "next";

/**
 * The API seam.
 *
 * Every call the browser makes goes to **this app's own origin** under `/api/…`,
 * and a Next rewrite forwards it to the FastAPI service (`P5.S1`–`P5.S9`). That is
 * a deliberate decision, not a dev convenience:
 *
 * - **No CORS.** `P5.S1` note 7 left "the CORS/origin question" to this slice, and
 *   the answer is that there is no cross origin: the FastAPI service still
 *   configures no CORS middleware and grants no preflight. `P5.S7`'s CSRF design
 *   depends on exactly that — a cross-origin page cannot set `X-Mijual-CSRF`
 *   without a preflight this service does not grant — so introducing CORS here
 *   would have weakened a landed security decision to save a proxy line.
 * - **The session cookie just works.** `mj_session` is `HttpOnly` · `SameSite=Lax`
 *   · `Path=/`; arriving through a same-origin rewrite it is stored for this app's
 *   origin and returned on every `/api/…` call, with no `SameSite=None` and no
 *   `Secure`-on-http trap (`P5.S7` note 2).
 *
 * `MIJUAL_API_ORIGIN` moves the upstream without a code change (P4 points it at
 * the deployed service, or replaces the rewrite with an edge route entirely).
 */
const API_ORIGIN = process.env.MIJUAL_API_ORIGIN ?? "http://localhost:8010";

/**
 * The dev-origin seam (`P7.S1`).
 *
 * `next dev` serves its own dev resources (`/_next/*`, the HMR socket) only to a
 * tiny allow-list of hosts — Next builds it as `['**.localhost', 'localhost',
 * ...allowedDevOrigins, <the -H hostname>]` and 403s everything else
 * (`next/dist/server/lib/router-utils/block-cross-site-dev.js`). `make stack-up`
 * runs `next dev -H 0.0.0.0`, so before this seam existed the list was exactly
 * `**.localhost` / `localhost` / `0.0.0.0` — and the URL the operator actually
 * opens, `http://127.0.0.1:3000`, was not on it: two client chunks 403'd, the HMR
 * handshake was rejected, **hydration never completed**, and Next's dev client
 * reloaded the tab on its failed reconnect. Six P7 complaints (items 4b, 6, 7, 8,
 * 11) were that one blocked origin, not product defects.
 *
 * The matcher (`isCsrfOriginAllowed`) compares hosts only, segment by segment, so
 * `**.ts.net` covers Tailscale MagicDNS names exactly — but an IPv4 literal can be
 * matched only exactly or by whole-octet wildcards, and `100.*.*.*` would open all
 * of 100.0.0.0/8 rather than Tailscale's 100.64.0.0/10 (verified against 16.3.2's
 * source). So the tailnet address arrives through `MIJUAL_DEV_ORIGINS`
 * (comma-separated hosts), which `make web-up` fills from `tailscale ip -4`; run
 * the dev server by hand and you can set it yourself. This is **dev-only** —
 * `allowedDevOrigins` is read exclusively by the dev router server, so
 * `next build && next start` behaves identically with or without it.
 */
const DEV_ORIGINS = [
  "127.0.0.1",
  // Inert while the server binds `-H 0.0.0.0` (v4 only); correct the day it binds v6.
  "[::1]",
  // Tailscale MagicDNS names. The tailnet *IP* cannot be expressed here — see above.
  "**.ts.net",
  ...(process.env.MIJUAL_DEV_ORIGINS ?? "")
    .split(",")
    .map((host) => host.trim())
    .filter(Boolean),
];

/**
 * How long a reader's browser may keep what we serve out of `public/` (`P4.F8`).
 *
 * Next sets **no** `Cache-Control` on `public/` at all. Hashed `/_next/static/*`
 * gets `public, max-age=31536000, immutable` from the framework, and everything
 * else falls through to whatever the CDN in front decides. Measured on production
 * before this slice: `/assets/*` and `/foundations/*` came back
 * `public, max-age=14400` with `cf-cache-status: REVALIDATED` — that is
 * **Cloudflare's default browser TTL**, not a number this repo chose, and under it
 * every returning reader re-validates the brand mark, the launcher's symbol mask
 * and the frozen token sheet every four hours.
 *
 * Two rules, and the split between them is the whole decision:
 *
 * - **A year + `immutable` goes only on a name that changes with its bytes.**
 *   `juju2-wordmark-white-273-73c23508.png` carries the first eight hex of its own
 *   pixel signature (`public/assets/README.md` records the command and the rule),
 *   so re-deriving it into different pixels *renames* it. That matters because an
 *   `immutable` response cannot be recalled: a Cloudflare purge reaches the edge,
 *   never a browser cache that was told not to ask for a year.
 * - **Every other name under `/assets/*` and `/foundations/*` gets one week**,
 *   with a day of `stale-while-revalidate`. `juju2-symbol-white.png` (the
 *   launcher's CSS mask), the two manifest tiles and `foundations/tokens.css` are
 *   *fixed* names whose bytes can change under the same URL, so a year would be a
 *   promise this repo cannot keep. One week still removes ~42 revalidations a
 *   fortnight per reader, and the recovery for an urgent change stays honest:
 *   rename the file, or purge at Cloudflare and accept that browsers hold the old
 *   copy for up to a week.
 *
 * **Order is load-bearing.** Next applies every matching entry in order and a
 * later one overwrites the same header name, so the exact-path `immutable` rule
 * sits *after* the directory rule that would otherwise cap it at a week. Verified
 * with `curl -sI` against the local production build, per path, including that
 * `/_next/static/*` is unchanged. Cloudflare honours an origin `Cache-Control`,
 * so these are also the numbers the edge and the reader get once `P4.S9` ships.
 */
const PUBLIC_DIR_CACHE = "public, max-age=604800, stale-while-revalidate=86400";
const IMMUTABLE_CACHE = "public, max-age=31536000, immutable";

/** Every file under `public/` whose *name* changes when its bytes do — the only
 * kind of name the rule above may serve `immutable`. Adding one means adding it
 * here and to the component that references it, together. */
const NAME_VERSIONED_PUBLIC_FILES = ["/assets/juju2-wordmark-white-273-73c23508.png"];

const nextConfig: NextConfig = {
  // P4.S1 — the deploy ships this app as a container, and `standalone` is what
  // makes that image small and self-contained: `next build` traces the server's
  // real node_modules closure into `.next/standalone` (see frontend/Dockerfile).
  // `next dev` ignores the key entirely, so the operator's dev runtime is unchanged.
  output: "standalone",
  allowedDevOrigins: DEV_ORIGINS,
  async rewrites() {
    return [{ source: "/api/:path*", destination: `${API_ORIGIN}/:path*` }];
  },
  async headers() {
    return [
      { source: "/assets/:path*", headers: [{ key: "Cache-Control", value: PUBLIC_DIR_CACHE }] },
      { source: "/foundations/:path*", headers: [{ key: "Cache-Control", value: PUBLIC_DIR_CACHE }] },
      // Last, deliberately — see the block above: this overwrites the week.
      ...NAME_VERSIONED_PUBLIC_FILES.map((source) => ({
        source,
        headers: [{ key: "Cache-Control", value: IMMUTABLE_CACHE }],
      })),
    ];
  },
};

export default nextConfig;
