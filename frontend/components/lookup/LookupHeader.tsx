"use client";

import { useState, type FormEvent } from "react";
import Link from "next/link";
import { CraftPanel } from "@/components";
import { ROUTES } from "@/lib/routes";
import type { StockPage } from "@/lib/types";
import {
  BOARD_LABEL_KO,
  CORP_CODE_KO,
  HERO_SUB_KO,
  STOCKS_LABEL_KO,
  STOCK_CODE_KO,
  noMatchKo,
} from "./copy";
import { SearchRow } from "./SearchRow";
import styles from "./Lookup.module.css";

/**
 * This surface's two headers — **R11 §1–§2**, which split what R4 had as one.
 *
 * R4 put a crumb, an `h1` 「내 종목 조회」, the hero subline and a search row above
 * *every* state, resolved or not: ≈235px of the page explaining the page before
 * it said what the reader had actually found. R11's finding 1 is sharper still —
 * the resolved stock **was never named**: the input came back empty and 세기상사's
 * page carried the company's name nowhere at all.
 *
 * So the header is now two different objects:
 *
 * - **`/stocks`** keeps `LookupHeader` — the title, the subline and the 48px
 *   console row. This is the only place they render, because this is the only
 *   place a reader has not yet said which stock they mean.
 * - **`/stocks/{corp_code}`** gets `LookupIdentity` — one panel whose `h1` is the
 *   **종목명**, whose mono meta is the two codes, whose search row echoes the
 *   resolved name, and whose bottom rail is the 보유량 strip. 「내 종목 조회」
 *   survives as the rail's second label (`LookupRail`), demoted, never deleted.
 */

/** The crumb rail (R11 §1). On a result it carries the page's own name as a
 * label rather than a heading — `.here` is text, not a link, because this *is*
 * that page. */
export function LookupRail({ here = false }: { here?: boolean }) {
  return (
    <nav className={styles.rail}>
      <Link className={styles.crumb} href={ROUTES.board}>
        ← {BOARD_LABEL_KO}
      </Link>
      {here ? <span className={styles.here}>{STOCKS_LABEL_KO}</span> : null}
    </nav>
  );
}

/**
 * The entry page's header (R11 §1, Q-A = b) and its 검색 불일치 line.
 *
 * ## The sentence belongs to the query that was submitted
 *
 * R11's finding 9: the candidate panel faded in **over** a 「‘삼성’와 일치하는
 * 종목이 없습니다」 that was already about a query nobody was typing any more. The
 * rule is that the line lives exactly as long as the submitted query is what is
 * in the box — the first differing keystroke removes it, and the candidates open
 * into the space it leaves.
 *
 * `SearchRow` is **not** touched to do that: its Enter rule, its candidate panel
 * and its stylesheet are R9/P7's and locked. React's `onInput` is the native
 * `input` event, which bubbles, so this component simply listens on the wrapper
 * and compares. The row keeps owning its own value; this owns only the sentence.
 *
 * The particle in that sentence is `copy.ts`'s `josa` — 와/과 by the query's
 * final consonant, 「와/과」 for anything not Hangul (R11 §7, finding 10).
 */
export function LookupHeader({ query, missed }: { query?: string; missed?: boolean }) {
  const submitted = query ?? "";
  const [typedText, setTypedText] = useState(submitted);

  return (
    <div
      className={styles.entry}
      onInput={(event: FormEvent<HTMLDivElement>) => {
        const target = event.target as HTMLInputElement;
        if (target.name === "q") setTypedText(target.value);
      }}
    >
      <h1 className={styles.title}>{STOCKS_LABEL_KO}</h1>
      <p className={styles.sub}>{HERO_SUB_KO}</p>

      <SearchRow
        label={STOCKS_LABEL_KO}
        defaultValue={query}
        variant="surface"
        classNames={{
          form: styles.entrysearch,
          input: `mono ${styles.input}`,
          submit: styles.submit,
        }}
      />

      {missed && submitted !== "" && typedText === submitted ? (
        <p className={styles.noMatch} role="status">
          {noMatchKo(submitted)}
        </p>
      ) : null}
    </div>
  );
}

/**
 * The identity panel (R11 §2) — 「what am I looking at」, 「search again」 and
 * 「with how many shares」 in one block, because those are the three things a
 * result page owes a reader before any event.
 *
 * - `h1` is the **종목명**. `corp_name` is nullable in the contract, and the code
 *   stands in for it rather than a placeholder — a stock with no served name is
 *   still that `corp_code`, and inventing one would be inventing a fact.
 * - The mono meta is 「종목코드 {stock_code}」 **first when the API serves one**
 *   (계양전기 `012200`), then 「고유번호 {corp_code}」. The card also draws a third
 *   span 「DART 공시 기준」; `build-prompt.md` §2 — the governing contract — lists
 *   these two only, so that span is card filler and is not product copy
 *   (`phase.md` §"R11 landed spec", read-back observation 1).
 * - The search row carries `defaultValue = corp_name`: **never empty on a
 *   result.** An empty box was the one element that erased what had been looked
 *   up.
 * - `strip` is the 보유량 rail, and it is `null` on a stock where no number on the
 *   page changes with it (Q-C). Then the panel simply ends.
 */
export function LookupIdentity({
  stock,
  strip,
}: {
  stock: StockPage["stock"];
  strip?: React.ReactNode;
}) {
  const name = stock.corp_name ?? stock.corp_code;

  return (
    <CraftPanel>
      <div className={styles.idp}>
        <div className={styles.idbox}>
          <h1 className={styles.corp}>{name}</h1>
          <p className={styles.idmeta}>
            {stock.stock_code ? (
              <span>
                {STOCK_CODE_KO} {stock.stock_code}
              </span>
            ) : null}
            <span>
              {CORP_CODE_KO} {stock.corp_code}
            </span>
          </p>
        </div>

        <SearchRow
          label={STOCKS_LABEL_KO}
          defaultValue={stock.corp_name ?? undefined}
          variant="surface"
          classNames={{
            form: styles.idsearch,
            input: `mono ${styles.input}`,
            submit: styles.submit,
          }}
        />
      </div>

      {strip}
    </CraftPanel>
  );
}
