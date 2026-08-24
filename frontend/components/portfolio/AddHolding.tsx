"use client";

import { useState } from "react";
import { CraftPanel } from "@/components";
import { lookupStock } from "@/lib/api";
import { parseShares } from "@/lib/holding";
import { SharesInput } from "./SharesInput";
import {
  ADD_SECTION_KO,
  KEEP_KO,
  SEARCH_PLACEHOLDER_KO,
  SEARCH_SUBMIT_KO,
  noMatchKo,
} from "./copy";
import styles from "./Portfolio.module.css";

/** An issuer this panel has resolved — the only way a holding names one. */
export type ResolvedStock = { corp_code: string; corp_name: string | null };

/**
 * 종목 추가 (R5 §Mobile: "종목 추가는 하단 패널"), and the `?add=` handshake.
 *
 * ## One resolver, and it is the product's own
 *
 * A holding is stored against a `corp_code` (`P5.S8` note 4 — validated on write,
 * deliberately not a foreign key), and the only thing that turns 종목명 or
 * 종목코드 into one is **`GET /stocks?q=`** (`P5.S4`'s four unique-or-decline
 * tiers). This panel calls it and nothing else: no candidate list, no near-miss,
 * no second matching rule. A miss is a *result*, so it renders R4's own signed
 * 검색 불일치 line rather than an error.
 *
 * ## The `?add=` link writes nothing
 *
 * R5-2's logged-in one-liner is "내 포트폴리오에 담기 →" and `P5.S15` made it a
 * **navigation** to `/portfolio?add={corp_code}` — a detail page has no 보유량 to
 * send and there is no anonymous write endpoint to send one to. The page resolves
 * that code server-side and hands it here as `preselect`, so the issuer arrives
 * already named and the reader only states a count. An `add=` that resolves to
 * nothing is simply absent — no error, and no invented "이 종목을 찾을 수 없습니다".
 *
 * ## A repeat 담기 goes to the row, not to a 409
 *
 * `P5.S8` note 3 refuses a duplicate (`holding_exists`) and its own note says R5
 * "wrote **no** line for '이미 담긴 종목' … the client, which holds the whole
 * list, should route a repeat 담기 to the row's inline 수정 rather than need one".
 * That is `onEditExisting`: the panel hands the issuer back to the list, which
 * opens that row's 수정. No copy is invented for a case the round does not draw.
 */
export function AddHolding({
  preselect,
  heldCorpCodes,
  busy,
  onAdd,
  onEditExisting,
}: {
  preselect: ResolvedStock | null;
  heldCorpCodes: ReadonlySet<string>;
  busy: boolean;
  onAdd: (stock: ResolvedStock, shares: number) => void;
  onEditExisting: (corpCode: string) => void;
}) {
  const [query, setQuery] = useState("");
  const [stock, setStock] = useState<ResolvedStock | null>(preselect);
  const [missed, setMissed] = useState<string | null>(null);
  const [digits, setDigits] = useState("");
  const [resolving, setResolving] = useState(false);

  const resolve = async () => {
    const text = query.trim();
    if (text === "" || resolving) return;
    setResolving(true);
    try {
      const result = await lookupStock(text);
      if (result.found) {
        setStock(result.stock);
        setMissed(null);
        if (heldCorpCodes.has(result.stock.corp_code)) onEditExisting(result.stock.corp_code);
      } else {
        setStock(null);
        setMissed(result.query);
      }
    } catch {
      // A failed resolution says nothing: the round writes no error line for this
      // surface, and the reader can press 조회 again.
      setStock(null);
    } finally {
      setResolving(false);
    }
  };

  const submit = () => {
    const shares = parseShares(digits);
    if (!stock || shares === null || busy) return;
    if (heldCorpCodes.has(stock.corp_code)) {
      onEditExisting(stock.corp_code);
      return;
    }
    onAdd(stock, shares);
    setStock(null);
    setQuery("");
    setDigits("");
  };

  return (
    <section className={styles.section}>
      {/* R13 renders the panel's name as this surface's own `// ` eyebrow, the
          same section title 다가오는 마감 and 지나간 마감 wear — the round's Home
          card puts 종목 추가 in exactly that slot, and the page still has no
          대제목 (R5 개정 ③). No copy moves: it is `ADD_SECTION_KO`. */}
      <h2 className={styles.eyebrow}>{`// ${ADD_SECTION_KO}`}</h2>

      <CraftPanel className={styles.add}>
        <div className={styles.search}>
          {/* Stamped by extensions before hydration — see `SearchRow.tsx`. */}
          <input
            suppressHydrationWarning
            className={styles.searchInput}
            type="text"
            value={query}
            placeholder={SEARCH_PLACEHOLDER_KO}
            autoComplete="off"
            onChange={(event) => setQuery(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter") {
                event.preventDefault();
                void resolve();
              }
            }}
          />
          <button
            type="button"
            className={styles.searchSubmit}
            disabled={resolving}
            onClick={() => void resolve()}
          >
            {SEARCH_SUBMIT_KO}
          </button>
        </div>

        {missed !== null ? <p className={styles.noMatch}>{noMatchKo(missed)}</p> : null}

        {stock ? (
          <>
            <p className={styles.addStock}>{stock.corp_name ?? stock.corp_code}</p>
            <SharesInput
              id="add-shares"
              digits={digits}
              disabled={busy}
              onChange={setDigits}
              onSubmit={submit}
            />
            <button
              type="button"
              className={styles.primary}
              disabled={busy || parseShares(digits) === null}
              onClick={submit}
            >
              {KEEP_KO}
            </button>
          </>
        ) : null}
      </CraftPanel>
    </section>
  );
}
