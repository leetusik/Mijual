import { LapseAlert, lapseNumeralClass } from "@/components";
import { count } from "@/lib/format";
import type { BoardSummary } from "@/lib/types";
import { lapseSentence, tieCountKo } from "./copy";
import styles from "./LapseNotice.module.css";

/**
 * The 소멸주의보 strip (R2 §소멸주의보 strip), full content-width between the
 * anchor panels and the board.
 *
 * > Craft panel with `--alert` border + **10px hazard stripe on the left edge**
 * > (repeating −45° `--alert` stripes, 5px on / 5px off); filled alert badge
 * > 소멸주의보. Body = 발표용 문장 4 **with live numbers** (15건 / 2026-09-04 /
 * > 계양전기) in mono `--alert` 600.
 *
 * The placard, the stripe and the badge are `LapseAlert`'s (R1's confirmed
 * sub-brand element in R2's craft form); this file supplies only the body, and
 * the body is the report's own sentence with today's figures from the **same**
 * `/board/summary` the stats card reads.
 *
 * ## The tie rule (R9 §6, walk finding 8)
 *
 * Three offerings share 청약 마감 2026-09-04, so the strip named one of them
 * (퓨쳐켐, by the API's `(마감일, 접수번호)` order) while the board's own first
 * D-2 row was another (계양전기) — two statements one screen apart that looked
 * like a contradiction. R9's answer is **not** a second sort order but saying
 * what is true: with several offerings tied, the sentence's `{corp}` slot counts
 * them (`tieCountKo` → 「3개 종목」) instead of naming one. The sentence's shape
 * and its words are R2's, unchanged; only the slot's content moved, and only when
 * the served `next_lapse.tie_count` says so — the screen never guesses a tie.
 *
 * With no `next_lapse` there is no sentence and therefore no strip: 발표용 문장 4
 * states a count, a date and a company, and a strip that cannot state them would
 * be a placard with a hole in it.
 */
export function LapseNotice({ summary }: { summary: BoardSummary }) {
  const next = summary.next_lapse;
  if (!next?.date || !next.corp_name || summary.lapse_pending <= 0) return null;
  const tied = (next.tie_count ?? 1) > 1;

  return (
    <LapseAlert>
      {lapseSentence.before}
      <span className={`mono ${lapseNumeralClass}`}>{count(summary.lapse_pending)}건</span>
      {lapseSentence.middle}
      <span className={`mono ${lapseNumeralClass}`}>{next.date}</span>
      {lapseSentence.join}
      {tied ? (
        <span className={styles.tie}>{tieCountKo(count(next.tie_count as number))}</span>
      ) : (
        next.corp_name
      )}
      {lapseSentence.after}
    </LapseAlert>
  );
}
