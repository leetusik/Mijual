import { AskPage } from "@/components/ask";

/**
 * `/ask` — **AI 질문**, R6's dedicated page.
 *
 * P5 shipped this route as a bare shell and said so in the file it left behind
 * ("P6 replaces this file"): the nav's third slot and the footer's bottom row
 * were signed, so the route had to exist, while everything R6 designs behind it
 * belonged to this phase. `P6.S6` replaces it whole.
 *
 * The surface itself is `components/ask/AskPage.tsx` — a client component,
 * because it is the second **view** over the module-scoped conversation store
 * (`lib/ask.ts`) that keeps a turn streaming while the reader walks between the
 * widget and this page. This file stays a plain route entry: no data loading, no
 * layout and no copy of its own.
 */
export default function AskRoute() {
  return <AskPage />;
}
