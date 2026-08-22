import Link from "next/link";
import { ROUTES } from "@/lib/routes";
import {
  BOARD_LABEL_KO,
  HERO_SUB_KO,
  SEARCH_PLACEHOLDER_KO,
  SEARCH_SUBMIT_KO,
  STOCKS_LABEL_KO,
  noMatchKo,
} from "./copy";
import styles from "./Lookup.module.css";

/**
 * The surface's header and its search row (R4 §Page anatomy 1–2).
 *
 * > 1. **Header**: title 내 종목 조회 + subline (hero copy) + crumb "← 관제
 * >    현황판".
 * > 2. **Search row**: input (hero placeholder "종목명 또는 종목코드 — 예:
 * >    계양전기") + 조회 button (`--live-solid`). Name/ticker resolution
 * >    server-side.
 *
 * ## The form is a plain GET, and the resolution is the server's
 *
 * Same seam the landing hero already posts through (`P5.S12`): `method="get"` to
 * `/stocks` with the API's own `q` parameter, so one vocabulary covers the page
 * path, the contract path and the hero — and so the product's entry point works
 * before any JavaScript does. Matching is `reads.resolve_corp`'s four
 * unique-or-decline tiers (종목코드 → 회사명 → normalized 회사명 → unique
 * normalized prefix); the browser guesses nothing.
 *
 * A miss renders R4's own locked sentence **on this page** rather than an error
 * state: `?q=` that resolves nothing is a `200 {found: false}` result (`P5.S4`
 * note 1), and the typed query stays in the box so it can be edited rather than
 * retyped.
 */
export function LookupHeader({ query, missed }: { query?: string; missed?: boolean }) {
  return (
    <header className={styles.header}>
      <Link className={`mono ${styles.crumb}`} href={ROUTES.board}>
        ← {BOARD_LABEL_KO}
      </Link>

      <h1 className={styles.title}>{STOCKS_LABEL_KO}</h1>
      <p className={styles.sub}>{HERO_SUB_KO}</p>

      <form className={styles.search} action={ROUTES.stocks} method="get" role="search">
        <input
          className={`mono ${styles.input}`}
          type="text"
          name="q"
          defaultValue={query}
          aria-label={STOCKS_LABEL_KO}
          placeholder={SEARCH_PLACEHOLDER_KO}
          autoComplete="off"
        />
        <button className={styles.submit} type="submit">
          {SEARCH_SUBMIT_KO}
        </button>
      </form>

      {missed && query ? (
        <p className={styles.noMatch} role="status">
          {noMatchKo(query)}
        </p>
      ) : null}
    </header>
  );
}
