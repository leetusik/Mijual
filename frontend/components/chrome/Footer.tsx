import Link from "next/link";
import { EstimateMarker } from "@/components";
import { ROUTES } from "@/lib/routes";
import {
  ASK_LABEL_KO,
  COPYRIGHT_KO,
  DISCLAIMER_KO,
  GATE_COST_TAIL_KO,
  GATE_COST_VALUE_KO,
  POSITIONING_KO,
  PROVENANCE_KO,
  SOURCE_KO,
  VOCKY_ROW_KO,
} from "./copy";
import { VockyTrigger } from "./VockyTrigger";
import { Wordmark } from "./Wordmark";
import styles from "./Footer.module.css";

/**
 * The global footer — R2 §Page shell, verbatim:
 *
 * > **Footer**: white-on-dark, 1px `rgba(255,255,255,.14)` top. Left col: white
 * > ring wordmark (h 17) + positioning line (mono 11, `rgba(255,255,255,.45)`).
 * > Right col, 12px `rgba(255,255,255,.72)`: ① provenance sentence "모든 수치는
 * > DART 공시에서만 나왔고, 추정치는 [추정] 표시로 구분했습니다." (re-cut, needs
 * > sign-off), ② gate-cost sentence (추정-tagged 49.2억원 — its only remaining
 * > placement), ③ disclaimer. Bottom hairline row: © · 자료: 금융감독원 DART
 * > 전자공시 | 의견 보내기 · 해설 (mono 11).
 *
 * All three sentences and the bottom row's chrome copy were **signed at the R2
 * gate** ("the round's new chrome copy … and the footer provenance re-cut"), so
 * the "needs sign-off" note is closed. Their text lives in `./copy.ts` with a
 * citation each; two readings of the record are executed here:
 *
 * - the bottom row's 해설 renders **AI 질문** — R6 retired that label and the
 *   supersession table governs a landed record (`P5.DECOMP` note 7);
 * - the gate-cost sentence's `▷` is gone and 49.2억원 carries the **추정 tag**,
 *   which is the same ruling (`▷` retires from the UI) and what the build prompt
 *   itself asks for ("추정-tagged 49.2억원").
 *
 * R5 leaves this surface alone on purpose — "footer unchanged" — so the
 * logged-in chrome changes nothing here. The one later addition the record does
 * put in a footer is R5-4's 샘플 포트폴리오 entry ("진입: 로그인 페이지 하단 +
 * 랜딩 푸터"), which belongs to the **landing** and to the slice that builds the
 * sample (`P5.S15`/`P5.S16`) — not to this global chrome.
 */
export function SiteFooter() {
  return (
    <footer className={styles.footer}>
      <div className={`content ${styles.inner}`}>
        <div className={styles.identity}>
          <Wordmark height={17} />
          <p className={styles.positioning}>{POSITIONING_KO}</p>
        </div>

        <div className={styles.sentences}>
          <p>{PROVENANCE_KO}</p>
          <p>
            {/* The value is derived (it is the gap between the ▷ upper bound and
                the published total), so it is tagged — `estimated` is passed as
                the literal `true` here because this figure comes from the landed
                pack rather than from a payload: `/board/summary` serves no
                gate-cost figure, and the contract will not invent one. See the
                note in `P5.S11`'s `result.md`. */}
            {/* `size="landing"` renders the tag at R2's own 10px literal
                ("Estimate mark (landing surfaces): a bordered sans 10px 「추정」
                tag beside the value"). Inheriting 0.56em from this 12px
                sentence gave 6.72px — the nit `P5.S11` note 9 flagged for
                `P5.S19`, fixed in the primitive with its citation rather than
                by restyling here or resizing the signed sentence. */}
            <EstimateMarker estimated={true} size="landing">
              <span className="mono">{GATE_COST_VALUE_KO}</span>
            </EstimateMarker>
            {GATE_COST_TAIL_KO}
          </p>
          <p>{DISCLAIMER_KO}</p>
        </div>
      </div>

      <div className={`content ${styles.bottom}`}>
        <span>{COPYRIGHT_KO}</span>
        <span aria-hidden="true" className={styles.dot}>
          ·
        </span>
        <span>{SOURCE_KO}</span>
        <span aria-hidden="true" className={styles.pipe}>
          |
        </span>
        <VockyTrigger surface="footer">{VOCKY_ROW_KO}</VockyTrigger>
        <span aria-hidden="true" className={styles.dot}>
          ·
        </span>
        <Link href={ROUTES.ask} className={styles.bottomLink}>
          {ASK_LABEL_KO}
        </Link>
      </div>
    </footer>
  );
}
