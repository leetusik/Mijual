"use client";

import { useEffect, useState } from "react";
import { fetchAuthState } from "@/lib/session";
import type { AuthState } from "@/lib/types";

/**
 * The session, for a client component that renders differently either way.
 *
 * It lives here rather than in `lib/session.ts` for a mechanical reason: that
 * module is also read by `lib/session.server.ts`, and a server module whose graph
 * contains a React hook fails the build. The data helpers are shared; the hook is
 * the client's.
 *
 * `enabled` is the laziness R5-2's offer panel needs: the probe fires only once
 * the caller has decided the element would render at all, so a 조회 page with no
 * holding typed into it makes no request. `null` means **not answered yet** and is
 * deliberately distinct from `{authenticated: false}` — a caller that renders one
 * of two states must render *neither* until it knows, or it tells a logged-in
 * reader for a moment that they have no account.
 */
export function useAuthState(enabled = true): AuthState | null {
  const [state, setState] = useState<AuthState | null>(null);

  useEffect(() => {
    if (!enabled || state !== null) return;
    let live = true;
    void fetchAuthState().then((next) => {
      if (live) setState(next);
    });
    return () => {
      live = false;
    };
  }, [enabled, state]);

  return enabled ? state : null;
}
