"use client";

import { useEffect } from "react";
import type { AskScope } from "@/lib/ask";
import { useAskStore } from "./useAsk";

/**
 * A page's **ambient** 범위 — 「이벤트 상세에서 열면 범위 = 그 이벤트 … 그 외 =
 * 전체 공시」 (R6 §범위 모델).
 *
 * Rendered by the event detail page and by no one else, so the rule reads as one
 * sentence: *an event detail page states its own event; everywhere else the
 * ambient 범위 is null, which is 전체 공시.*
 *
 * ## The lifecycle, decided here
 *
 * - **Set on mount**, cleared on unmount — the effect's own cleanup, so leaving
 *   the page (a link, the back button, a soft navigation to another event) takes
 *   the ambient 범위 with it. React runs a removed subtree's cleanup before the
 *   new subtree's effects in the same commit, so walking from event A to event B
 *   lands on B's scope rather than on null; a race that did leave null behind
 *   would be the harmless side (전체 공시), never someone else's event.
 * - **Keyed by the scope's own values**, not by object identity: a server
 *   component hands a fresh object down on every render and an identity-keyed
 *   effect would re-run for nothing.
 * - **It never overrides the reader.** `setPageScope` is applied by the store
 *   only at `open()` and only while the reader has not chosen a 범위 themselves
 *   (`scopeChosen`) — 「×로 전체 공시로 해제」 has to stick, and a 질문 스트립 chip
 *   calls `setScope`, which is a choice. This component therefore cannot change a
 *   conversation that is already scoped, and calls nothing on the running turn.
 *
 * It renders nothing — and since **R16 no surface draws the 범위 at all** (§0
 * 폐기 ①: the header chip, its × and the page's rail are retired), what it states
 * is now visible only in what the widget *does*: opening it on an event detail
 * asks in that filing's 범위 and shows that filing's 질문 스트립 (회귀 19). The
 * state stays deliberately — 「`scope` 상태 자체는 서버·스토어에서 제거하지 않아도
 * 되지만 표면에 그리지 않는다」 — so this component is unchanged by that
 * retirement.
 */
export function AskPageScope({ scope }: { scope: AskScope }) {
  const store = useAskStore();
  const { rcept_no: rceptNo, name } = scope;

  useEffect(() => {
    store.setPageScope({ rcept_no: rceptNo, name });
    return () => store.setPageScope(null);
  }, [store, rceptNo, name]);

  return null;
}
