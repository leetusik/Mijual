import Link from "next/link";
import { BOARD_LABEL_KO } from "@/components/chrome/copy";
import { ROUTES } from "@/lib/routes";
import styles from "./Auth.module.css";

/**
 * 「← 관제 현황판」 — the auth column's first row (R12 Q-D = 레일).
 *
 * The operator chose the rail over R5's bare centered panel, and the round gives
 * the reason as an escape route rather than as consistency: an anonymous reader
 * who followed a 전환 제안 here and then decided **not** to make an account had
 * nowhere to go — every other surface in the product carries this line, and this
 * one was the single dead end. It is the column's first row, not a full-width
 * bar: the panel stays exactly where R5 centred it.
 *
 * No new copy either way — `BOARD_LABEL_KO` is the chrome's own noun, rendered
 * with the same `← ` the event detail crumb and `LookupRail` already use.
 */
export function AuthRail() {
  return (
    <nav className={styles.rail}>
      <Link className={styles.crumb} href={ROUTES.board}>
        ← {BOARD_LABEL_KO}
      </Link>
    </nav>
  );
}
