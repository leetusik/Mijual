import { LapseAlert, lapseNumeralClass } from "@/components";
import { count } from "@/lib/format";
import type { BoardSummary } from "@/lib/types";
import { lapseSentence } from "./copy";

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
 * The live tie-break names **퓨쳐켐** where the landed R2 card shows 계양전기:
 * three offerings share 청약 마감 2026-09-04 and the API orders by (마감일,
 * 접수번호) rather than by whatever row the pipeline's `min()` happened to pick
 * (`P5.S3` note 9). The round asks for live numbers by contract, so live data
 * governs — this is data, not a design deviation.
 *
 * With no `next_lapse` there is no sentence and therefore no strip: 발표용 문장 4
 * states a count, a date and a company, and a strip that cannot state them would
 * be a placard with a hole in it.
 */
export function LapseNotice({ summary }: { summary: BoardSummary }) {
  const next = summary.next_lapse;
  if (!next?.date || !next.corp_name || summary.lapse_pending <= 0) return null;

  return (
    <LapseAlert>
      {lapseSentence.before}
      <span className={`mono ${lapseNumeralClass}`}>{count(summary.lapse_pending)}건</span>
      {lapseSentence.middle}
      <span className={`mono ${lapseNumeralClass}`}>{next.date}</span>
      {lapseSentence.join}
      {next.corp_name}
      {lapseSentence.after}
    </LapseAlert>
  );
}
