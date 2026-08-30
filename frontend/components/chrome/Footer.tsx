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
 *     <div class=id>  워드마크 h24 + "자료: 금융감독원 DART 전자공시 · © 미주알"
 *     <div class=acts> [의견 보내기 버튼] [AI 질문 링크 — 데스크톱 숨김, R17]
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
 *
 * **R17 found that the AI 질문 launcher was sitting on this row** — a constant
 * 68px of overlap at every viewport ≤1120px, crossing to zero only at 1256px.
 * Because `Feedback.tsx` anchors its panel to the 의견 보내기 button, a covered
 * button is a **dead interaction**, not a cosmetic overlap. The round signs two
 * independent fixes and neither replaces the other:
 *
 * 1. a **corner reservation** on `.inner` (`Footer.module.css`), so whatever ends
 *    the row clears the launcher — `.actions` is the end of a `space-between`
 *    row, so hiding one item only hands the covered position to the next one;
 * 2. **hiding the duplicated 「AI 질문」 link on desktop** — R8 §1's "같은 목적지를
 *    바에서 두 번 말하지 않는다", applied to a destination that desktop said
 *    three times (nav, footer, launcher). **≤767px keeps the link**: the launcher
 *    does not render there, so this is that destination's only footer entry.
 *
 * Structure, content and order are unchanged — only spacing and one desktop-only
 * visibility rule. The link keeps its place in the DOM at every width.
 */
export function SiteFooter() {
  return (
    <footer className={styles.footer}>
      <div className={`content ${styles.inner}`}>
        <div className={styles.identity}>
          <Wordmark height={24} />
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
          <Link href={ROUTES.ask} className={`${styles.action} ${styles.actionAsk}`}>
            {ASK_LABEL_KO}
          </Link>
        </div>
      </div>
    </footer>
  );
}
