/**
 * "Am I logged in?" — the **server** half.
 *
 * Split from `./session.ts` for a mechanical reason, not a stylistic one:
 * `next/headers` may not appear in a client bundle at all, and the client half is
 * imported by client components. Two modules keep both halves honest, and a
 * caller picks by where it runs.
 *
 * `P5.S10` note 13 states the rule this file implements: **a gated read from a
 * server component must forward the incoming `cookie` header itself** —
 * `credentials: "include"` is a browser concept and does nothing in Node, so
 * without this the API would answer `{authenticated: false}` for a reader who is
 * very much logged in.
 */

import { cookies } from "next/headers";
import { getAuthState } from "./api";
import { ANONYMOUS } from "./session";
import type { AuthState } from "./types";

/**
 * Who this request belongs to. **Never throws**: a service that is down is
 * answered as anonymous, because the surfaces that ask have an anonymous
 * rendering and none has an error one.
 *
 * Reading cookies opts the route into request-time rendering, which is what
 * every auth-dependent page wants anyway — a session state must never be a build
 * artifact.
 *
 * **A request carrying no cookie at all is answered without asking** (`P4.F10`).
 * This session lives in a cookie and nowhere else (`mj_session`, set by
 * `mijual.web.auth`), so a request with an empty `Cookie` header cannot be
 * authenticated and `GET /auth/me` could only answer `{authenticated: false}`.
 * The short-circuit names **no cookie**, deliberately: keying on the cookie's
 * *name* would duplicate a backend constant here, and a rename would then make
 * this read answer "anonymous" for readers who are very much logged in — the one
 * failure this whole line is built to avoid. Emptiness cannot go stale that way.
 * What it buys: `/events/{rcept_no}` now reads the session on every render, and
 * the crawler — 445 event pages, never a cookie — adds no API request at all.
 */
export async function readAuthState(): Promise<AuthState> {
  try {
    const cookie = (await cookies()).toString();
    if (!cookie) return ANONYMOUS;
    return await getAuthState({ headers: { cookie } });
  } catch {
    return ANONYMOUS;
  }
}
