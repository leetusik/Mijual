import { cookies } from "next/headers";
import { ApiError, getOpsSession, type RequestInitLike } from "@/lib/api";

/**
 * The server half of 운영 관제's reads.
 *
 * Two mechanical facts drive everything here. **A gated read from a server
 * component must forward the incoming request's own `cookie` header** —
 * `credentials: "include"` is a browser concept and does nothing in Node
 * (`P5.S10` note 13) — and reading cookies is what opts every ops route into
 * request-time rendering, which is exactly right for a console whose whole
 * content is "what is true right now".
 */

/** This request's cookies, for the service. `mj_ops` is among them or the read
 * comes back 401. */
export async function opsHeaders(): Promise<{ cookie: string } | undefined> {
  const cookie = (await cookies()).toString();
  return cookie ? { cookie } : undefined;
}

/**
 * Is this an authenticated operator? **Never throws** — a service that is down
 * answers the same as a missing cookie, and the door is the honest surface for
 * both: it is the only thing an operator can act on from here.
 */
export async function opsAuthenticated(): Promise<boolean> {
  try {
    const state = await getOpsSession({ headers: await opsHeaders() });
    return state.authenticated;
  } catch {
    return false;
  }
}

/**
 * One tab's read, tolerating the one failure that has a designed answer.
 *
 * The layout has already checked the session, so a `401 ops_unauthenticated`
 * here means it expired in the moment between the two reads — the panel's own
 * 12-hour boundary landing mid-request. That returns `null` and the page renders
 * the door in place, which is where the operator has to go anyway. Every other
 * failure propagates: an ops console that quietly renders an empty panel when
 * its service is broken would be lying about the pipeline.
 */
export async function opsRead<T>(
  read: (init?: RequestInitLike) => Promise<T>,
): Promise<T | null> {
  try {
    return await read({ headers: await opsHeaders() });
  } catch (error) {
    if (error instanceof ApiError && error.status === 401) return null;
    throw error;
  }
}
