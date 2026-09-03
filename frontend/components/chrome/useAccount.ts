"use client";

import { usePathname } from "next/navigation";
import { createContext, useContext, useEffect, useState, useSyncExternalStore } from "react";
import { fetchAuthState } from "@/lib/session";
import type { AuthState } from "@/lib/types";

/**
 * "Does this browser have an account?" — the chrome's own question, asked once.
 *
 * `P5.S15` note 9 left this decision here: "**If `P5.S16` decides the chrome
 * should probe once per page load for the account menu, that probe should
 * replace this one rather than sit beside it**; both read `lib/session.ts`."
 * This module is that decision, and it is a store rather than a hook per
 * component for one concrete reason: the desktop slot and the mobile sheet row
 * are two components rendering the *same* fact, and 로그아웃 happens in one of
 * them — with two independent `useAuthState()` instances the sheet would keep
 * showing an account that no longer exists.
 *
 * ## What it costs, and why the chrome pays it at all
 *
 * R5 replaces the nav's 로그인 slot with the 축약 이메일 메뉴 for a reader who has
 * a session, so the chrome — which `P5.S11` deliberately built to call no
 * endpoint at all — now has to know. `GET /auth/me` answers 200 either way
 * (anonymous is a result, not a 401 — `P5.S7` note 13) and gates nothing, and
 * `fetchAuthState()` shares one in-flight request, so a page whose surface also
 * asks (R5-2's offer panel, the detail one-liner) makes **one** probe between
 * them rather than two.
 *
 * The probe is per **path**, not per mount: a session can begin on `/auth/login`
 * and end anywhere, and the chrome outlives a client-side navigation, so a store
 * that answered once at boot would show a stale slot for the rest of the visit.
 * That covers every mutation this app performs itself: 로그인 lands on a new path
 * (`AuthPanel` pushes 내 포트폴리오), 로그아웃 and 계정 삭제 leave through a fresh
 * document load, which resets this module outright — and 수신 주소 변경, the one
 * mutation that changes the slot's own text without moving the reader, publishes
 * through `setAccountState` so the slot never waits for a navigation to tell the
 * truth.
 *
 * **Nothing is cached across a probe**: `null` means *not answered yet* and is
 * deliberately distinct from `{authenticated: false}` (the convention
 * `components/auth/useAuthState.ts` set), so the slot renders neither state until
 * it knows rather than flashing 로그인 at a reader who is logged in.
 *
 * ## Why the probe carries no `live` cleanup flag (`P7.S2`)
 *
 * It used to, and in `next dev` that made the slot unanswerable — the whole of
 * the operator's "no login exists". React StrictMode double-invokes effects in
 * development, so run 1 claimed `probedPath`, started the probe, and then had its
 * cleanup set `live = false`; run 2 returned early on the claim run 1 had just
 * made. The one answer on the wire was discarded, `state` stayed `null` forever,
 * and `AccountSlot` rendered an empty slot for the entire visit. `next start`
 * invokes the effect once and was always fine, which is why it shipped.
 *
 * A cleanup flag is the wrong instrument here regardless of StrictMode: the state
 * it guards is a **module** store that outlives every component, so an answer
 * landing after a subscriber unmounted is still the answer the next subscriber
 * wants — there is no unmount hazard to protect against. The guard that does the
 * real work is `probedPath === pathname` at resolve time, which drops an answer
 * that lands after a client-side navigation moved the reader. And two effect runs
 * cost one request, not two: `lib/session.ts` shares the in-flight probe.
 */

/**
 * ## The server already knows, and now it says so (`P12.F1`)
 *
 * Everything above describes a store that learns the answer **after** the browser
 * has painted. `P12.R1` measured what that costs: the 로그인 link (37.27 px) or the
 * account frame (261.28 px) is inserted into the nav **+45 to +293 ms after first
 * contentful paint** in dev and **+3 to +165 ms** on the production build, on
 * 10/10 reader routes — a pop-in on every single desktop load (CLS 0: the nav's
 * right group grows leftward from a pinned right edge, so nothing else moves).
 *
 * The remedy is the route `P4.F10` already took on `/events/{rcept_no}`, lifted to
 * the layout: `app/layout.tsx` is an `async` server component that already awaits
 * the 운영자 연락처, `lib/session.server.ts` `readAuthState()` forwards the
 * request's own cookie and never throws, so the layout resolves the session there
 * and hands it down through `SiteChrome` into `InitialAccountContext`. **Nothing
 * about the reading changed** — neither state is shown before the session is
 * known; it is simply known earlier, and by the half of the app that can know it
 * first. `AccountSlot.tsx`'s "renders nothing until the probe answers" is still
 * literally true, the answer just arrives with the HTML.
 *
 * ### The seam: the server must never write this store
 *
 * `state` and `probedPath` are **module** scope, and a Node process serves every
 * concurrent request out of one module registry — a server render that wrote them
 * would leak one reader's session into another reader's page, which is the worst
 * bug this file could possibly have. So the server only ever *reads* `initial`:
 *
 * - `getServerSnapshot` is `() => initial` — the server render and the hydrating
 *   client render both return the context value, so the markup carries the right
 *   slot and hydration matches.
 * - `getSnapshot` is `() => state ?? initial` — after the seed the two are the same
 *   reference, so the value never changes identity across that boundary.
 * - the seed itself is a **client-only, idempotent, once-per-store** write in a
 *   lazy `useState` initializer, guarded by `typeof window !== "undefined"`. It
 *   runs before the boot effect can and marks `probedPath = pathname`, which is
 *   what skips the boot probe for the initial path. StrictMode's double invocation
 *   is harmless because the second pass finds `state !== null` and does nothing —
 *   the lesson `P7.S2` learned above, applied to a different hook.
 *
 * Everything downstream is untouched: every **later** client-side navigation
 * re-probes exactly as before (`probedPath !== pathname`), and `setAccountState`
 * still publishes 로그아웃 / 계정 삭제 / 수신 주소 변경 — a client answer always
 * wins over the server's, because after the first `setAccountState` `state` is
 * non-null and `initial` is never consulted again. A host that provides no
 * context — `/ops`, or any other tree — leaves `initial` at `null` and the hook
 * behaves byte-for-byte as it did before this note.
 */

/**
 * The session as the **server** resolved it for this request, or `null` when no
 * host resolved one. Provided by `SiteChrome`; read by `useAccount()` only.
 *
 * It is a context rather than a prop threaded through `Nav.tsx` because the two
 * consumers (`AccountSlotDesktop`, `AccountSlotSheet`) are two levels down inside
 * the nav, and neither the nav nor the sheet has any use for the value itself.
 */
export const InitialAccountContext = createContext<AuthState | null>(null);

let state: AuthState | null = null;
let probedPath: string | null = null;
const listeners = new Set<() => void>();

function emit(): void {
  for (const listener of listeners) listener();
}

function subscribe(listener: () => void): () => void {
  listeners.add(listener);
  return () => {
    listeners.delete(listener);
  };
}

function snapshot(): AuthState | null {
  return state;
}

/** Publish a session change this app just made — a 로그인, a 로그아웃, a
 * 계정 삭제. The slot updates without waiting for a probe it already knows the
 * answer to. */
export function setAccountState(next: AuthState | null): void {
  state = next;
  emit();
}

export function useAccount(): AuthState | null {
  const pathname = usePathname();
  const initial = useContext(InitialAccountContext);

  // The seed (`P12.F1`). A lazy `useState` initializer is the earliest point in a
  // render that runs **once per mount and never on a re-render**, and the
  // `typeof window` guard is what keeps it off the server entirely — see the seam
  // note above. The returned state is deliberately unused: this call is here for
  // its timing, not its value.
  useState(() => {
    if (typeof window === "undefined") return null;
    if (state === null && initial !== null) {
      state = initial;
      probedPath = pathname;
    }
    return null;
  });

  const value = useSyncExternalStore(
    subscribe,
    () => snapshot() ?? initial,
    () => initial,
  );

  useEffect(() => {
    if (probedPath === pathname) return;
    probedPath = pathname;
    void fetchAuthState().then((next) => {
      if (probedPath === pathname) setAccountState(next);
    });
  }, [pathname]);

  return value;
}
