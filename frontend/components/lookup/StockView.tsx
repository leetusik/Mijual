"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { ConversionOffer } from "@/components/auth";
import { InlineScript, clearMirror, jsonLiteral } from "@/components/chrome";
import {
  SESSION_KEY,
  convert,
  parseShares,
  readSessionHoldings,
  writeSessionHolding,
} from "@/lib/holding";
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

  // The reservation below is a **pre-hydration device** (`P12.F3`'s seam, second
  // use): it holds the ① row's with-holding geometry while the effect above is
  // still on its way. `ready` flips in the same commit that renders the holding,
  // so by the time this runs the cells are already in the DOM at their own
  // height and dropping the stamp moves nothing — and it must not run any
  // earlier, because a released reservation is a box that collapses. Dropping it
  // *then* is what a reader who clears the field depends on: the row goes back
  // to two cells and the prompt comes back, with no reserved 35 px left behind.
  useEffect(() => {
    if (ready) clearMirror("lookup-holding");
  }, [ready]);

  /** The mirror's page-level half. It needs this page's own `corp_code` — the
   * session remembers a count **per issuer** — which is why it is here beside the
   * row and not in the `<head>` script that carries the page-independent facts. */
  const reservation = useMemo(() => holdingReservationCode(corpCode), [corpCode]);

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

      {/* Parser-blocking, and **above everything it reserves**: it runs while the
          parser is still over the ① panels, so the with-holding geometry is
          selected before the row is laid out, let alone painted. It reads one
          named session key, in this browser and only this browser, and stamps
          `data-mj-lookup-holding` on `<html>` — nothing is written, nothing is
          sent (`security.md`'s 「anonymous state never reaches the server」 is why
          there is no cookie here). What used to be *inserted* into a painted page
          — three cells, +35 px at 1280 and +111 px at 390 — is now *filled* into
          a row that is already the right size. */}
      <InlineScript code={reservation} />

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

      {/* 전환 제안 (R5-2) — **after the last data section, before 집계 범위 and
          the provenance line** (R12 §4). 「값 계산 직후」 and 「결과를 가리지
          않음」 are both true only here: between the data sections the band would
          push 놓친 돈 below an offer, and at the very end of the page it would sit
          in the provenance's own place and read as a footer banner. Still normal
          flow, still anonymous-only, still once per session, still dismissible. */}
      <ConversionOffer ready={valued} />

      <CoveragePanel coverage={page.lapse.coverage} />
    </>
  );
}

/**
 * 조회's half of the **pre-hydration mirror** (`P12.F4`, the seam in
 * `components/chrome/PreHydration.tsx`).
 *
 * The server renders the no-holding row because the count is the browser's alone
 * — `sessionStorage`, per issuer, never sent anywhere (R4-6). So the browser
 * reads its own memory 20 lines before that row is parsed and says only *whether*
 * this stock has one; `Lookup.module.css` holds the with-holding geometry from
 * the stamp, and the effect above then fills a box that does not move.
 *
 * It answers exactly the question {@link readSessionHoldings} answers, by the
 * same rules — one key, JSON or nothing, a positive safe integer under this
 * page's own `corp_code` — because the two must agree: a stamp React does not
 * honour would be a reserved gap, and a missing stamp is the shift this fixes.
 * The **count** is deliberately not stamped: no rule reads it (the reserved
 * height follows from the served factors, which the row already carries), and a
 * number on `<html>` would be this reader's own holding written into the
 * document for no purpose.
 */
function holdingReservationCode(corpCode: string): string {
  return (
    `(function(){try{` +
    `var raw=null;try{raw=sessionStorage.getItem(${jsonLiteral(SESSION_KEY)})}catch(e){return}` +
    `if(!raw)return;var v=null;try{v=JSON.parse(raw)}catch(e){return}` +
    `if(!v||typeof v!=="object")return;var en=v.entries;` +
    `if(!en||typeof en!=="object")return;var n=en[${jsonLiteral(corpCode)}];` +
    `if(typeof n!=="number"||!Number.isSafeInteger(n)||n<=0)return;` +
    `document.documentElement.setAttribute("data-mj-lookup-holding","")` +
    `}catch(e){}})();`
  );
}
