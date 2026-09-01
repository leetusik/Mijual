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
};

export default nextConfig;
