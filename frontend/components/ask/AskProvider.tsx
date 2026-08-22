"use client";

import type { ReactNode } from "react";
import { askStore } from "@/lib/ask";
import { AskContext, useHydrateAsk } from "./useAsk";

/**
 * The conversation store, mounted **once** in the app's persistent layout.
 *
 * `SiteChrome` renders it around the whole reader tree (nav, page, footer,
 * launcher, widget), which is what makes the widget and `P6.S6`'s `/ask` page two
 * views over one thread rather than two conversations. It provides a **stable**
 * value and holds no state, so wrapping every page in it costs a page nothing:
 * a `text` frame arriving mid-stream re-renders the subscribers and never this.
 *
 * It also does the one thing that must happen exactly once — reading the thread
 * back out of `sessionStorage` (R6-5/6: session-scoped, never `localStorage`).
 */
export function AskProvider({ children }: { children: ReactNode }) {
  useHydrateAsk();
  return <AskContext value={askStore}>{children}</AskContext>;
}
