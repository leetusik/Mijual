"use client";

import { useId, useState } from "react";
import { Citation } from "@/components";
import { dartUrl, getCorrections } from "@/lib/api";
import type { CorrectionStory, EventDetail } from "@/lib/types";
import { FieldValue } from "./Fields";
import { CLOSE_GLYPH } from "@/lib/copy";
import {
  COLLAPSE_KO,
  CORRECTION_HISTORY_KO,
  CURRENT_VERSION_KO,
  MOVE_AFTER_KO,
  MOVE_BEFORE_KO,
  MOVE_DELETED_KO,
  correctionStripKo,
} from "./copy";
import styles from "./Event.module.css";

/**
 * The 정정 밴드 and the CorrectionStory it opens (R3 §Page anatomy 5,
 * §CorrectionStory view, re-cut by **R10 §7**).
 *
 * > **정정 strip** (footer, `--surface-raised`): "정정공시 반영 — 최근:
 * > {interpretation.summary key figures} · {schedule_impact}" + "정정 이력"
 * > button → CorrectionStory view.
 *
 * ## Why the view is in place rather than a route
 *
 * R3 calls it a *view* opened by a button, and the button is the only navigation
 * the round draws. A route would need its own way back, and the only crumb this
 * product owns says "← 관제 현황판" — which is the board, not this event. So the
 * story opens under the band and the reader keeps the card they came from.
 *
 * ## R10: the trigger reads its own state
 *
 * The label used to stay 「정정 이력」 while the rail and the diff were open below
 * it (walk finding 3) — the same defect R9 fixed on the board's strips. It now
 * flips to **「접기」** + `×` and holds the inset surface while its panel is open,
 * so `aria-expanded` **agrees with** the label instead of standing in for it.
 * R3's note that "a 접기 label is copy nobody signed" is superseded: R9 signed
 * that word and R10 re-uses it here.
 *
 * The band sentence is an `h2` (§5), and the diff below drops its arrow column
 * for the **two tagged sides** this surface now uses wherever a value moved (§7,
 * and the 철회 evidence with it).
 *
 * The rail is a second request (`GET /events/{rcept_no}/corrections`), made on
 * first open: the version list, the field moves and the interpretation are a
 * different reading from the card's, and the card should not pay for them.
 */
export function Corrections({ detail }: { detail: EventDetail }) {
  const teaser = detail.corrections;
  const panelId = useId();
  const [open, setOpen] = useState(false);
  const [story, setStory] = useState<CorrectionStory | null>(null);
  const [loading, setLoading] = useState(false);

  if (!teaser?.corrected || !detail.rcept_no) return null;
  const rceptNo = detail.rcept_no;

  async function toggle() {
    const next = !open;
    setOpen(next);
    if (!next || story || loading) return;
    setLoading(true);
    try {
      setStory(await getCorrections(rceptNo));
    } catch {
      // No copy exists for a failed read of this view, and inventing a Korean
      // error line would be a design change — the product writes *state* copy,
      // not error copy (`P5.S1` note 1). The panel stays empty and the button
      // can be pressed again.
      setStory(null);
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className={styles.correctionStrip}>
      <div className={styles.correctionHead}>
        <h2 className={styles.correctionTeaser}>
          {correctionStripKo.title}
          {/* A corrected filing whose interpretation has no summary still says
              that it was corrected; the "최근:" clause is dropped rather than
              opened onto nothing. */}
          {teaser.summary ? (
            <>
              {" "}
              {correctionStripKo.recent}
              <span>{teaser.summary}</span>
              {teaser.schedule_impact ? (
                <>
                  {correctionStripKo.join}
                  <span className={styles.scheduleImpact}>{teaser.schedule_impact}</span>
                </>
              ) : null}
            </>
          ) : null}
        </h2>
        {/* P12.F6 (R1 F12): 「정정 이력」 and 「접기 ×」 are two labels in one slot, and
            the box used to be 10.83px narrower while open. `data-label` carries the
            wider resting label into a hidden `::after` twin that shares the button's
            single grid cell (`Nav.module.css`'s technique, R18 §② 폭 예약), so the box
            is as wide as the resting state in both. Same strings, same copy, same
            `aria-expanded` / `aria-controls`; the twin is `visibility: hidden` at
            height 0, so it is in no accessible name and no hit test. */}
        <button
          type="button"
          className={styles.historyButton}
          data-label={CORRECTION_HISTORY_KO}
          aria-expanded={open}
          aria-controls={panelId}
          onClick={toggle}
        >
          <span className={styles.historyLabel}>
            {open ? COLLAPSE_KO : CORRECTION_HISTORY_KO}
            {open ? (
              <span aria-hidden="true" className={styles.historyMark}>
                {CLOSE_GLYPH}
              </span>
            ) : null}
          </span>
        </button>
      </div>

      <div id={panelId} hidden={!open}>
        {story ? <Story story={story} koreanNames={koreanNames(detail)} /> : null}
      </div>
    </section>
  );
}

/** The field labels this page already holds, so the story's rows can be named
 * without the frontend keeping a field-name table (`P5.S10` note 11). A field
 * the current version no longer serves — the deleted-passage case — has no
 * served label anywhere, and its row is rendered without one rather than with a
 * raw English key. */
function koreanNames(detail: EventDetail): Record<string, string> {
  const names: Record<string, string> = {};
  for (const field of Object.values(detail.fields)) {
    if (field.korean_name) names[field.field_key] = field.korean_name;
  }
  return names;
}

/**
 * The CorrectionStory itself.
 *
 * > Version rail: chronological rows (date · correction_kind · rcept_no ↗); only
 * > `is_current_readable` gets the filled marker + live badge "현재 읽는 버전";
 * > superseded rows may carry the locked reason string as a grey annotation.
 * > **Verdicts never cross versions.** Field moves: 정정 전 / → / 정정 후 columns
 * > from `field_moves` verbatim; `new: null` renders "(정정 후 본문에서 삭제됨)".
 * > Summary = `interpretation.summary` verbatim + bolded `schedule_impact`.
 *
 * Two readings, both recorded in `phase.md`:
 *
 * - **The superseded-row annotation has no data to render.** It would be the
 *   gate's reason for that version ("이전 버전이라 최신 API 값과 대조할 수
 *   없습니다"), and the reader contract carries **no gate reason code at all** —
 *   why a value is missing is internal, and the operator's panel is the only
 *   surface that sees it (`states-and-trust.md` §4, D-14). R3 says "may carry",
 *   so the rows carry none.
 * - **The original row shows no kind.** `correction_kind` is Korean for every
 *   correction (기재정정 · 첨부정정) and the English token `original` for the
 *   first filing; printing that token on a Korean reader surface would be worse
 *   than the truth the rail already shows, which is that the earliest row is the
 *   one with no 정정 on it.
 *
 * An event with **no readable 본문 at all** marks *no* row as the current
 * readable version — 239 of the 422 exposable ② events have none, and the card
 * renders from the API strip. The rail states that honestly by filling nothing.
 */
function Story({
  story,
  koreanNames,
}: {
  story: CorrectionStory;
  koreanNames: Record<string, string>;
}) {
  const interpretation = (story.interpretation ?? {}) as {
    summary?: unknown;
    schedule_impact?: unknown;
  };
  const summary = typeof interpretation.summary === "string" ? interpretation.summary : undefined;
  const impact =
    typeof interpretation.schedule_impact === "string" ? interpretation.schedule_impact : undefined;
  const moves = story.field_moves ?? [];

  return (
    <div className={styles.story}>
      <ol className={styles.rail}>
        {story.versions.map((version) => (
          <li
            key={version.rcept_no}
            className={version.is_current_readable ? `${styles.railRow} ${styles.railCurrent}` : styles.railRow}
          >
            <span aria-hidden="true" className={styles.railMarker} />
            <span className={`mono ${styles.railDate}`}>{version.rcept_dt}</span>
            <span className={styles.railKind}>
              {version.correction_kind === "original" ? null : version.correction_kind}
            </span>
            <a
              className={`mono ${styles.railLink}`}
              href={dartUrl(version.rcept_no)}
              target="_blank"
              rel="noreferrer"
            >
              {version.rcept_no} ↗
            </a>
            {version.is_current_readable ? (
              <span className={styles.railBadge}>{CURRENT_VERSION_KO}</span>
            ) : null}
          </li>
        ))}
      </ol>

      {moves.length > 0 ? (
        <div className={styles.moves}>
          {moves.map((move, index) => {
            const fieldKey = typeof move.field_key === "string" ? move.field_key : "";
            const label = koreanNames[fieldKey];
            return (
              <div key={`${index}-${fieldKey}`} className={styles.move}>
                {label ? <p className={styles.moveLabel}>{label}</p> : null}
                {/* Two tagged sides, no arrow column (R10 §7 · walk findings 4
                    and 9): the tags say the direction, so nothing has to be
                    squeezed into three columns at 390px — the sides stack and
                    the same markup serves both widths. */}
                <div className={styles.movePair}>
                  <div className={styles.moveSide}>
                    <p className={styles.moveTag}>{MOVE_BEFORE_KO}</p>
                    <div className={styles.moveValue}>
                      <FieldValue fieldKey={fieldKey} value={move.old} moved />
                    </div>
                  </div>
                  <div className={`${styles.moveSide} ${styles.moveAfter}`}>
                    <p className={styles.moveTag}>{MOVE_AFTER_KO}</p>
                    {move.new === null || move.new === undefined ? (
                      <p className={styles.moveDeleted}>{MOVE_DELETED_KO}</p>
                    ) : (
                      <div className={styles.moveValue}>
                        <FieldValue fieldKey={fieldKey} value={move.new} moved />
                      </div>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      ) : null}

      {summary ? (
        <p className={styles.storySummary}>
          <span>{summary}</span>
          {impact ? <strong className={styles.scheduleImpact}> {impact}</strong> : null}
          <Citation
            rceptNo={story.rcept_no}
            quote={story.quote}
            span={story.span}
            label={CORRECTION_HISTORY_KO}
          />
        </p>
      ) : null}
    </div>
  );
}
