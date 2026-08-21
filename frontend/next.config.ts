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
const API_ORIGIN = process.env.MIJUAL_API_ORIGIN ?? "http://localhost:8000";

const nextConfig: NextConfig = {
  async rewrites() {
    return [{ source: "/api/:path*", destination: `${API_ORIGIN}/:path*` }];
  },
};

export default nextConfig;
