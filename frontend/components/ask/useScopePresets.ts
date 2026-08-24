"use client";

import { useEffect, useState } from "react";
import { getEvent } from "@/lib/api";
import type { AskScope } from "@/lib/ask";
import { presetsFor, type AskPreset } from "./presets";

/**
 * The 범위 event's gate-passing fields, read the same way the detail page reads
 * them — so a preset chip on `/ask`, one in the widget and one on
 * `/events/{rcept_no}` are generated from one payload by one rule (`presets.ts`).
 *
 * `GET /events/{rcept_no}` is the surface's own contract call, anonymous and
 * read-only, and its `fields` map already holds **only** what the gate passed. A
 * failure or an abort yields **no chips** rather than a message: R6 writes no copy
 * for a preset row that could not be built, and the composer below is the surface
 * either way. A 철회 event yields none either — 「답할 수 없는 질문은 프리셋으로
 * 제안하지 않음」, and 철회 is the refusal family the agent would answer with.
 *
 * It lives in its own module because **two** views now use it: `AskPage` (where it
 * has always been) and, since **R14 finding 8**, the widget's empty scoped thread.
 * One hook rather than two copies is what keeps a chip identical wherever it is
 * pressed.
 */
export function useScopePresets(scope: AskScope | null): AskPreset[] {
  const [presets, setPresets] = useState<AskPreset[]>([]);
  const rceptNo = scope?.rcept_no ?? null;

  useEffect(() => {
    setPresets([]);
    if (!rceptNo) return;
    const controller = new AbortController();
    getEvent(rceptNo, { signal: controller.signal })
      .then((detail) => {
        if (controller.signal.aborted) return;
        setPresets(detail.state === "withdrawn" ? [] : presetsFor(detail.fields));
      })
      .catch(() => undefined);
    return () => controller.abort();
  }, [rceptNo]);

  return presets;
}
