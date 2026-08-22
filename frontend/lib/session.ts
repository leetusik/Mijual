/**
 * "Am I logged in?" — the browser half, and the one-time message channel.
 *
 * `P5.S7` made anonymity a **result, not a 401**: `GET /auth/me` answers
 * `{"authenticated": false}` for a visitor with no cookie, so any surface can ask
 * without filling a console with errors. What that leaves to the frontend is
 * *where* to ask from, and this module is the answer for client components.
 * Server components use `./session.server.ts` instead — `credentials` is a
 * browser concept and does nothing in Node, so a server read has to forward the
 * incoming `cookie` header itself (`P5.S10` note 13).
 *
 * ## Who reads this, and why it is not read by everything
 *
 * `P5.S15` needs the session in exactly two places, both of them **client**
 * surfaces that swap one line: R5-2's 조회 offer panel (shown only to a reader
 * who has no account to save into) and R5-2's detail one-liner ("이 마감 알림
 * 받기 →" ↔ "내 포트폴리오에 담기 →"). Both ask lazily through
 * `components/auth/useAuthState.ts` — only once the element would otherwise
 * render — so no anonymous surface pays for a session probe it does not use. The
 * chrome still asks for nothing at all (`P5.S11` note: "the chrome calls no
 * endpoint"); **`P5.S16`'s account menu is the slice that decides whether the
 * whole app probes once per page load**, and it should use these modules rather
 * than write a third.
 *
 * This file itself imports **no React**: `lib/session.server.ts` reads it, and a
 * server module that pulls a hook into its graph fails the build. The hook lives
 * beside the components that call it.
 *
 * Nothing here caches. A session can end in another tab (로그아웃 deletes the
 * row, so a cookie is worthless the instant it is gone — `P5.S7` note 1), and a
 * stale "logged in" would render the wrong line rather than a slow one.
 */

import { getAuthState } from "./api";
import type { AuthState } from "./types";

/** The state a visitor with no cookie is in, and the fallback for a probe that
 * could not complete: the product's surfaces are anonymous by default, so a
 * failed probe must degrade to anonymous, never to "logged in". */
export const ANONYMOUS: AuthState = { authenticated: false };

/**
 * Ask the API who this browser is. **Never throws** — a network failure or a
 * service that is down is answered as anonymous, because every surface that asks
 * has an anonymous rendering and none of them has an error one.
 */
export async function fetchAuthState(): Promise<AuthState> {
  try {
    return await getAuthState();
  } catch {
    return ANONYMOUS;
  }
}

// ---------------------------------------------------------------------------
// The one-time message channel (R5-1: "로그아웃되었습니다" 1회 표시)
// ---------------------------------------------------------------------------

/**
 * R5-1 signs 로그아웃 as "즉시, 확인 다이얼로그 없음, '로그아웃되었습니다' **1회
 * 표시**" — a message that outlives the click that caused it (the reader leaves
 * the gated surface at the same moment) and must not survive a reload.
 * `sessionStorage` is exactly that lifetime, and it is where the product already
 * keeps a fact that belongs to this tab and to nobody's server (R4's holdings,
 * `lib/holding.ts`).
 *
 * The channel carries a **kind, not a sentence**: the Korean lives in
 * `components/auth/copy.ts` with its citation, and a message written into storage
 * would be signed copy sitting in a place nothing cites.
 *
 * **`P5.S16` owns the writer.** 로그아웃 lives in the account menu it builds; it
 * calls `writeFlash("logout")` and sends the reader to an anonymous surface, and
 * whichever surface it lands on reads the flash once. `P5.S15` renders it on the
 * auth panel because that is the anonymous surface a 로그아웃 most obviously
 * returns to; if S16 lands somewhere else, it reads the same channel there.
 */
export type FlashKind = "logout";

const FLASH_KEY = "mijual.auth.flash";

export function writeFlash(kind: FlashKind): void {
  try {
    window.sessionStorage.setItem(FLASH_KEY, kind);
  } catch {
    // A browser with storage denied loses the message. It is a courtesy line,
    // never a fact the reader needs, so it fails silently rather than throwing
    // inside a logout.
  }
}

/** Read **and clear** — "1회 표시" is the specification, so the read is the
 * consumption. Returns `null` when there is nothing to show. */
export function readFlashOnce(): FlashKind | null {
  try {
    const raw = window.sessionStorage.getItem(FLASH_KEY);
    if (raw === null) return null;
    window.sessionStorage.removeItem(FLASH_KEY);
    return raw === "logout" ? "logout" : null;
  } catch {
    return null;
  }
}
