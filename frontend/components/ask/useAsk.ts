"use client";

import { createContext, useContext, useEffect, useState, useSyncExternalStore } from "react";
import { askStore, type AskState, type AskStore } from "@/lib/ask";

/**
 * The React half of the conversation store — a context at the **persistent
 * layout** level, and a subscription per view.
 *
 * R6 requires that a turn keep streaming while the reader moves from the widget
 * to `/ask` (「스트리밍 중 이동/전환에도 끊김 없음」). Navigation unmounts a page,
 * so the fetch cannot belong to one: the thread lives in `lib/ask.ts` in module
 * scope and this file only *hands it out*. `AskProvider` therefore holds **no
 * state of its own** and never re-renders its children — a frame arriving on the
 * wire re-renders the views that subscribed, and nothing else in the app.
 *
 * The context exists so there is exactly one documented way in: `P6.S6`'s page
 * calls `useAskState()` / `useAskStore()` like the widget does, and no surface
 * constructs a second store.
 */
export const AskContext = createContext<AskStore>(askStore);

export function useAskStore(): AskStore {
  return useContext(AskContext);
}

export function useAskState(): AskState {
  const store = useAskStore();
  return useSyncExternalStore(store.subscribe, store.getSnapshot, store.getServerSnapshot);
}

/**
 * 「위젯·런처 없음」 below the surface's breakpoint (R6 §Surfaces / §Mobile) — as a
 * **render** decision, not a `display: none`.
 *
 * **R14 Q-A moved that line onto the product's single 767**, so the desktop
 * surface starts at **768px**: R1's own narrower breakpoint survived here longer
 * than anywhere else (R10 §0 settled the 767 line and R13 deleted the last block
 * still drawn at the old one), and here the line is not layout — it decides
 * whether the widget and the launcher **exist**. Every window between the old line
 * and 767 used to receive a launcher and a squeezed widget; each now receives the
 * same full-width `/ask` page a phone does. `Ask.module.css` and `AskPage.module.css` draw the
 * same 767/768 line, and `AskSurface` is where it becomes a render.
 *
 * Server-rendered as `false` and corrected on mount, the same shape
 * `lib/motion.ts`'s `useReducedMotion` uses and for the same reason: a media
 * query is a client fact, and prerendering the wrong side of it would flash a
 * launcher onto a phone.
 */
export const DESKTOP_QUERY = "(min-width: 768px)";

export function useDesktop(): boolean {
  const [desktop, setDesktop] = useState(false);

  useEffect(() => {
    const media = window.matchMedia(DESKTOP_QUERY);
    const sync = () => setDesktop(media.matches);
    sync();
    media.addEventListener("change", sync);
    return () => media.removeEventListener("change", sync);
  }, []);

  return desktop;
}

/** Read sessionStorage once for the whole app. Mounted by `AskProvider`. */
export function useHydrateAsk(): void {
  const store = useAskStore();
  useEffect(() => {
    store.hydrate();
  }, [store]);
}
