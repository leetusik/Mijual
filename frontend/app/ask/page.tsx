import type { Metadata } from "next";
import { connection } from "next/server";
import { AskPage } from "@/components/ask";
import { startChips } from "@/components/ask/copy";
import { getAskStartCards } from "@/lib/api";
import { ROUTES } from "@/lib/routes";
import { ASK_TITLE_KO, routeMetadata, SITE_DESCRIPTION_KO } from "@/lib/seo";

/** How long the start screen waits for its cards before drawing the static set.
 * The empty state is the product's flagship surface: a reader looking at a blank
 * page while a fetch hangs is worse than a reader looking at four sentences that
 * were true this morning. */
const CARDS_TIMEOUT_MS = 2500;

/**
 * `/ask` — **AI 질문**, R6's dedicated page.
 *
 * P5 shipped this route as a bare shell and said so in the file it left behind
 * ("P6 replaces this file"): the nav's third slot and the footer's bottom row
 * were signed, so the route had to exist, while everything R6 designs behind it
 * belonged to this phase. `P6.S6` replaced it whole.
 *
 * The surface itself is `components/ask/AskPage.tsx` — a client component,
 * because it is the second **view** over the module-scoped conversation store
 * (`lib/ask.ts`) that keeps a turn streaming while the reader walks between the
 * widget and this page.
 *
 * ## This file is the start screen's data boundary (`P11.F1`)
 *
 * It used to say, in so many words, that it stayed "a plain route entry: no data
 * loading, no layout and no copy of its own". That was a real decision and it is
 * **superseded**, by the operator's report at P11's acceptance gate: 「the HLB,
 * 에코프로비엠 default is fine but when they are outdated, what happen? we should
 * make them to be real time catch. not fixed.」 A start card that names a company
 * whose filing has aged out of the corpus is a dead question on the first screen
 * a reader meets, so the two company-bearing cards are resolved **per request**
 * from the live corpus (`GET /ask/start-cards`) and only their wording stays in
 * `copy.ts`. Something has to do that read, and a client fetch would make the one
 * screen that must never look empty start empty.
 *
 * Three properties this boundary has to keep, in the order they can break:
 *
 * 1. **Per request, not per build.** `connection()` marks the page as request-time
 *    rendering — without it Next renders `/ask` once at build time and serves
 *    day-old companies from a static shell, which is the very defect this slice
 *    fixes. `cache: "no-store"` says the same thing to the fetch itself, and both
 *    are verified in the **production** build, where a static render is what
 *    `next build` prints in its route table.
 * 2. **Never a blank grid.** Any failure — the API down, slow, or a corpus with
 *    no answerable company — falls back to `START_CHIPS_KO`'s static four
 *    (`startChips` falls back per card, so one empty slot costs one card). The
 *    timeout is part of that: a hanging API must degrade, not stall the page.
 * 3. **No Korean crosses the wire.** The endpoint returns companies; the
 *    sentences are templates in `copy.ts`, where every Korean string this product
 *    renders lives.
 */
/** The surface's own signed name (`ASK_LABEL_KO`, R6 — which retired the
 * provisional 해설) and its canonical. The description is the site's: the page's
 * own content is a reader's conversation, which is neither indexable nor
 * describable in advance. */
export const metadata: Metadata = routeMetadata({
  title: ASK_TITLE_KO,
  description: SITE_DESCRIPTION_KO,
  path: ROUTES.ask,
});

export default async function AskRoute() {
  await connection();

  const picks = await getAskStartCards({
    cache: "no-store",
    signal: AbortSignal.timeout(CARDS_TIMEOUT_MS),
  }).catch(() => null);

  return (
    <AskPage
      cards={startChips({
        search: picks?.search_events?.corp_name,
        calculate: picks?.calculate?.corp_name,
      })}
    />
  );
}
