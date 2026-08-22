"use client";

import { useEffect, useState } from "react";
import { parseShares, readSessionHoldings, writeSessionHolding } from "@/lib/holding";
import type { BoardSummary, StockPage } from "@/lib/types";
import { HoldingStrip } from "./HoldingStrip";
import { CoveragePanel, NoRights } from "./LookupEmpty";
import { MissedMoney } from "./MissedMoney";
import { RightsSection } from "./RightsSection";
import styles from "./Lookup.module.css";

/**
 * One resolved stock: the 보유량 strip and the two sections under it (R4
 * decision R4-1 — "one page, two sections … no mode toggle, no second view").
 *
 * ## Why one component owns the number
 *
 * The holding drives the ① rows *and* the 놓친 돈 total, and R4's own failure
 * mode is "두 divergent readouts for the same number". So the count lives here,
 * once, and both sections receive it; the arithmetic is `lib/holding.ts`, also
 * once, shared with 내 포트폴리오 (`P5.S8` note 1). **Nothing is debounced** —
 * the conversion is a multiplication, and R4 asks for instant recompute.
 *
 * ## Session memory (decision R4-6), and the one thing it must not do
 *
 * `sessionStorage` only, per issuer, keyed by `lib/holding.ts`'s `SESSION_KEY`
 * (`P5.S16` reads the same object for R5-3's 세션 이월 제안). On *this* stock the
 * reader's own earlier input is restored — it is the number they typed for this
 * exact page, in this session. On a **different** stock nothing is filled in:
 * the last count is offered as a chip ("이전 입력 {n}주") and the reader presses
 * it, which is what "never auto-fill silently" means.
 *
 * Nothing is sent anywhere: the API accepts no holding count on any path, and
 * there is no anonymous write endpoint to send one to (`P5.S8` note 13).
 */
export function StockView({
  page,
  summary,
}: {
  page: StockPage;
  summary?: BoardSummary | null;
}) {
  const corpCode = page.stock.corp_code;
  const [digits, setDigits] = useState("");
  const [restore, setRestore] = useState<number | null>(null);
  const [ready, setReady] = useState(false);
  const shares = parseShares(digits);

  // Read the session once, on mount. The page is keyed by `corp_code`, so a
  // different stock is a different component instance and this cannot run with
  // another issuer's number in state.
  useEffect(() => {
    const memory = readSessionHoldings();
    const own = memory.entries[corpCode];
    if (own !== undefined) {
      setDigits(String(own));
    } else if (memory.last && memory.last.corp_code !== corpCode) {
      setRestore(memory.last.shares);
    }
    setReady(true);
  }, [corpCode]);

  useEffect(() => {
    if (!ready) return;
    writeSessionHolding(corpCode, shares);
  }, [ready, corpCode, shares]);

  const empty = page.rights.count === 0 && page.lapse.totals.offerings === 0;

  return (
    <div className={styles.stock}>
      <HoldingStrip
        digits={digits}
        restore={restore}
        onChange={(next) => {
          setDigits(next);
          setRestore(null);
        }}
        onRestore={() => {
          if (restore !== null) setDigits(String(restore));
          setRestore(null);
        }}
      />

      {empty ? (
        <NoRights summary={summary} />
      ) : (
        <>
          <RightsSection page={page} shares={shares} />
          <MissedMoney page={page} shares={shares} />
        </>
      )}

      <CoveragePanel coverage={page.lapse.coverage} />
    </div>
  );
}
