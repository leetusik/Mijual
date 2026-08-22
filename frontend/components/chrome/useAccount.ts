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
 * Every mutation this app performs itself (로그인 · 로그아웃 · 계정 삭제) also
 * publishes through `setAccountState`, so the slot never waits for a navigation
 * to tell the truth.
 *
 * **Nothing is cached across a probe**: `null` means *not answered yet* and is
 * deliberately distinct from `{authenticated: false}` (the convention
 * `components/auth/useAuthState.ts` set), so the slot renders neither state until
 * it knows rather than flashing 로그인 at a reader who is logged in.
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
    let live = true;
    void fetchAuthState().then((next) => {
      if (live && probedPath === pathname) setAccountState(next);
    });
    return () => {
      live = false;
    };
  }, [pathname]);

  return value;
}
