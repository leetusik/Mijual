"use client";

import { useEffect, useRef, useState } from "react";
import { ConversionOffer } from "@/components/auth";
import { convert, parseShares, readSessionHoldings, writeSessionHolding } from "@/lib/holding";
import type { BoardSummary, StockPage } from "@/lib/types";
import { MISSED_PROMPT_KO } from "./copy";
import { HoldingStrip } from "./HoldingStrip";
import { CoveragePanel, NoRights } from "./LookupEmpty";
import { LookupIdentity } from "./LookupHeader";
import { MissedMoney } from "./MissedMoney";
import { RightsSection } from "./RightsSection";
import styles from "./Lookup.module.css";

/**
 * One resolved stock: the identity panel and the two sections under it (R4-1 —
 * "one page, two sections … no mode toggle, no second view"), re-composed by
 * **R11 §§1–6**.
 *
 * ## Why one component owns the number
 *
 * The holding drives the ① cells *and* the 놓친 돈 figures, and R4's own failure
 * mode is "두 divergent readouts for the same number". So the count lives here,
 * once, and both sections receive it; the arithmetic is `lib/holding.ts`, also
 * once, shared with 보유 종목 (`P5.S8` note 1). **Nothing is debounced** — the
 * conversion is a multiplication, and R4 asks for instant recompute.
 *
 * ## Session memory (R4-6), and the one thing it must not do
 *
 * `sessionStorage` only, per issuer. On *this* stock the reader's own earlier
 * input is restored — it is the number they typed for this exact page, in this
 * session. On a **different** stock nothing is filled in: the last count is
 * offered as a chip ("이전 입력 {n}주") and the reader presses it, which is what
 * "never auto-fill silently" means. Nothing is sent anywhere: the API accepts no
 * holding count on any path, and there is no anonymous write endpoint to send one
 * to (`P5.S8` note 13).
 *
 * ## The two placement decisions R11 put here
 *
 * **The strip renders only where a number on this page changes with it** (Q-C) —
 * a live ① with its 배정 factors, or a 놓친 돈 row. On a ②-only stock (풍전약품) or
 * a no-rights stock (세기상사) it is absent, with no disabled control and no
 * sentence, which is why that decision needed no new copy.
 *
 * **The prompt renders once per page** (R11 §6): in the first live ① block's
 * `.chainfoot` when there is one, otherwise in 놓친 돈's head, and never once a
 * holding exists. It is a control, so it goes only where the input it focuses
 * exists — the strip's condition above is exactly the condition for a prompt.
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
  const sharesInput = useRef<HTMLInputElement>(null);
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
  const liveOffering = page.rights.rows.some(
    (row) => row.rights_type === "R1" && row.offering !== undefined,
  );
  // Q-C: a number on this page changes with the holding — or it does not, and
  // then there is nothing for a strip to drive.
  const showStrip = liveOffering || page.lapse.rows.length > 0;
  const prompt =
    showStrip && shares === null ? (
      <button
        type="button"
        className={styles.prompt}
        onClick={() => sharesInput.current?.focus()}
      >
        {MISSED_PROMPT_KO}
        <span className={styles.arw} aria-hidden="true">
          →
        </span>
      </button>
    ) : null;

  // R5-2 places its offer panel "값 계산 직후" — after a per-holding value has
  // rendered. That is asked of `lib/holding.ts`, the product's one multiplication
  // site, rather than answered a second way here: the same `convert()` the cells
  // and the 놓친 돈 rows already call, so the offer cannot appear beside numbers
  // that do not exist (an unpriced ① converts to `value: null` by construction).
  const valued =
    shares !== null &&
    [
      ...page.lapse.rows.map((row) => convert(row.lapse, shares).value),
      ...page.rights.rows.map((row) =>
        row.offering ? convert(row.offering, shares).value : null,
      ),
    ].some((value) => value !== null);

  return (
    <>
      <LookupIdentity
        stock={page.stock}
        strip={
          showStrip ? (
            <HoldingStrip
              digits={digits}
              restore={restore}
              inputRef={sharesInput}
              onChange={(next) => {
                setDigits(next);
                setRestore(null);
              }}
              onRestore={() => {
                if (restore !== null) setDigits(String(restore));
                setRestore(null);
              }}
            />
          ) : null
        }
      />

      {/* The heading is 「진행 중인 권리 — 0건」 on a no-rights stock too: the
          section is not dropped, it is answered — by `NoRights`, which speaks for
          both sections at once, so 놓친 돈 does not also open to say nothing. */}
      <RightsSection
        page={page}
        shares={shares}
        prompt={liveOffering ? prompt : undefined}
        fallback={<NoRights summary={summary} />}
      />

      {empty ? null : (
        <MissedMoney page={page} shares={shares} prompt={liveOffering ? undefined : prompt} />
      )}

      <CoveragePanel coverage={page.lapse.coverage} />

      {/* 전환 제안 (R5-2), last on the page and in normal flow: it never covers
          the results, it gates nothing, and it shows at most once per session. */}
      <ConversionOffer ready={valued} />
    </>
  );
}
