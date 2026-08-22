"use client";

import { usePathname } from "next/navigation";
import { useEffect, useSyncExternalStore } from "react";
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
  const value = useSyncExternalStore(subscribe, snapshot, () => null);

  useEffect(() => {
    if (probedPath === pathname) return;
    probedPath = pathname;
    void fetchAuthState().then((next) => {
      if (probedPath === pathname) setAccountState(next);
    });
  }, [pathname]);

  return value;
}
