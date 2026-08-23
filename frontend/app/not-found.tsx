import Link from "next/link";
import { ROUTES } from "@/lib/routes";
import { NOT_FOUND_BACK_KO, NOT_FOUND_LINE_KO, NOT_FOUND_TITLE_KO } from "@/components/event/copy";
import { RequestedPath } from "./RequestedPath";
import styles from "./not-found.module.css";

/**
 * The not-found surface (**R10 §8**, Q15 = b).
 *
 * The last English screen a Korean-only product could reach: until now an
 * unexposable filing — and any mistyped address — fell through to Next's own
 * "404 / This page could not be found." R3 wrote *state* copy and no 404 copy on
 * purpose, so R10 designed the page and signed its three Korean strings as its
 * dated copy exception.
 *
 * Two rules govern what it may say:
 *
 * **It gives no reason.** flagged · incomplete · `no_document` · a 실적보고서
 * rcept · a typo all render this one screen, and none of them is named. Why a
 * filing is not exposable is internal and the operator's panel is the only
 * surface that sees it (`states-and-trust.md` §4, D-14). Saying "this filing
 * exists but we are not showing it" would be exactly the leak the exposure
 * contract exists to prevent.
 *
 * **It echoes the address and nothing else about it.** The path is printed in
 * mono with no label, because the address is a fact the reader supplied; a label
 * would begin to interpret it.
 *
 * It renders inside the R8 chrome (this file is a child of the root layout), so
 * the nav wordmark is the second way back to the 관제 현황판 — the button is the
 * first. Next returns **404** for this file's response, both for a segment's own
 * `notFound()` and for an unmatched URL.
 */
export default function NotFound() {
  return (
    <main className={`content ${styles.nf}`}>
      <h1 className={styles.title}>{NOT_FOUND_TITLE_KO}</h1>
      <p className={styles.line}>{NOT_FOUND_LINE_KO}</p>
      <RequestedPath />
      <Link className={styles.back} href={ROUTES.board}>
        {NOT_FOUND_BACK_KO}
      </Link>
    </main>
  );
}
