import Link from "next/link";
import { ROUTES } from "@/lib/routes";
import { ASK_LABEL_KO, COPYRIGHT_KO, SOURCE_KO } from "./copy";
import { FeedbackEntry } from "./Feedback";
import { Wordmark } from "./Wordmark";
import styles from "./Footer.module.css";

/**
 * The global footer — R2 §Page shell, **re-cut by R8 §4** (SIGNOFF: R8
 * supersedes R2's footer content and type).
 *
 * ```
 * <footer>            border-top: 1px solid rgba(255,255,255,.14); padding-block: var(--space-6)
 *   <div class=in>    flex, space-between, gap var(--space-6), wrap
 *     <div class=id>  워드마크 h17 + "자료: 금융감독원 DART 전자공시 · © 미주알"
 *     <div class=acts> [의견 보내기 버튼] [AI 질문 링크]
 * ```
 *
 * The operator's instruction was "remove the text and keep it simple and clean",
 * and the round executed it as a deletion of **four sentences** — the positioning
 * line, the provenance sentence, the gate-cost sentence (with its `EstimateMarker`)
 * and the disclaimer — plus the separate mono bottom row. What is left is one
 * hairline, one row, and no numerals at all, which is why the type is Pretendard:
 * "mono는 숫자 전용(R1)이고 남은 줄에는 숫자가 없다" (result.md §2-14).
 *
 * **The five deleted constants still exist** in `./copy.ts`, unrendered. R8's own
 * record asks the operator where the gate-cost and 면책 sentences should go
 * instead (result.md §6-1, open as P8 Operator Question Q5) and makes deleting
 * the strings conditional on that answer; deleting the markup is what the round
 * signs, and this file is that deletion.
 *
 * 의견 보내기 is no longer a `data-vocky-trigger` — it is the entry point for
 * 미주알's own surface (`Feedback.tsx`), which anchors its 380px panel to this
 * button on desktop and becomes a bottom sheet at ≤480.
 */
export function SiteFooter() {
  return (
    <footer className={styles.footer}>
      <div className={`content ${styles.inner}`}>
        <div className={styles.identity}>
          <Wordmark height={17} />
          <p className={styles.source}>
            {SOURCE_KO}
            <span aria-hidden="true" className={styles.dot}>
              ·
            </span>
            {COPYRIGHT_KO}
          </p>
        </div>

        <div className={styles.actions}>
          <FeedbackEntry className={styles.action} />
          <Link href={ROUTES.ask} className={styles.action}>
            {ASK_LABEL_KO}
          </Link>
        </div>
      </div>
    </footer>
  );
}
