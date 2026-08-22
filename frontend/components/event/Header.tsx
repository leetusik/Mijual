import { CraftPanel, DDay, RightsChip, StateBadge } from "@/components";
import { dartUrl } from "@/lib/api";
import type { EventDetail } from "@/lib/types";
import {
  CONVERSION_OPEN_KO,
  CORRECTED_KO,
  DART_LINK_KO,
  FIELD_ABSENT_KO,
  FIRST_FILED_KO,
  NO_COUNTDOWN_KO,
  RCEPT_NO_KO,
  identityLineKo,
  tradingOpenKo,
} from "./copy";
import styles from "./Event.module.css";

/**
 * The detail page's header panel (R3 §Page anatomy 2).
 *
 * > **Header panel** (craft panel): left: `RightsChip type` → corp name
 * > (text-2xl bold) + "DART 원문 ↗" (mono link) → mono meta line (접수번호 ·
 * > 최초 공시 `original_rcept_dt` · 정정 반영 when versions > 1). right:
 * > governing label (`countdown.label_ko`) → `DDay` (upstream-computed label +
 * > date) → mono window/state line.
 *
 * ## The three things this component refuses to do
 *
 * **It computes no date and no D-day.** `countdown.dday`, `days`, `date`,
 * `window` and `reference` all arrive computed in KST (D-10); the only date
 * arithmetic anywhere on this surface is a string comparison of two served ISO
 * days against the served `reference`, and it lives in ③'s step block, not here.
 *
 * **It never fills an empty countdown slot.** `countdown.date === null` has two
 * different causes and R3 gives each its own line: the governing field is served
 * and says 추후결정 (→ `StateBadge tbd` + "카운트다운 없음 — 일정이 공시상
 * 미정", and **never a date beside it** — `ui-traps.md` #4), or the governing
 * field is absent from the payload altogether (→ "현재 버전 공시에 없음", a
 * statement about the *filing*, never about the gate). Which one holds is read
 * from `countdown.source`, whose first segment names the field the countdown
 * would have come from.
 *
 * **It never silently corrects the company's name.** The card shows the DART
 * master `corp_name`; when the 본문 prints another one the difference is stated
 * under it in the round's own sentence (`ui-traps.md` #3), so a reader who taps
 * through to a differently-named 원문 is not surprised.
 *
 * A **withdrawn** event gets no countdown side at all: "no fields, no countdown,
 * no old dates" is R3's rule and `P5.S3` already empties the payload to match.
 */
export function EventHeader({ detail }: { detail: EventDetail }) {
  const countdown = detail.countdown;
  const name = detail.corp_name ?? detail.corp_code;
  const withdrawn = detail.state === "withdrawn";
  const versions = detail.corrections?.versions ?? 0;
  const sourceField = countdown.source.split(".")[0];
  // 추후결정 is a served answer; an absent field is a fact about the filing.
  const isTbd = detail.fields[sourceField]?.display === "추후결정";

  return (
    <CraftPanel as="header" className={styles.header}>
      <div className={styles.identity}>
        <RightsChip rightsType={detail.rights_type} />
        <h1 className={styles.corp}>{name}</h1>
        {detail.corp_name_agrees_with_body === false && detail.corp_name_in_body ? (
          <p className={styles.identityNote}>{identityLineKo(detail.corp_name_in_body)}</p>
        ) : null}
      </div>

      {detail.rcept_no ? (
        <a
          className={styles.dart}
          href={dartUrl(detail.rcept_no)}
          target="_blank"
          rel="noreferrer"
        >
          {DART_LINK_KO} ↗
        </a>
      ) : null}

      <p className={`mono ${styles.meta}`}>
        {detail.rcept_no ? (
          <span>
            {RCEPT_NO_KO} {detail.rcept_no}
          </span>
        ) : null}
        {detail.original_rcept_dt ? (
          <span>
            {FIRST_FILED_KO} {detail.original_rcept_dt}
          </span>
        ) : null}
        {versions > 1 ? <span>{CORRECTED_KO}</span> : null}
      </p>

      {withdrawn ? null : (
        <div className={styles.countdown}>
          <p className={styles.countdownLabel}>{countdown.label_ko}</p>

          {countdown.date && countdown.dday !== null && countdown.days !== null ? (
            <DDay
              className={styles.dday}
              dday={countdown.dday}
              days={countdown.days}
              date={countdown.date}
            />
          ) : (
            <div className={styles.noCountdown}>
              {isTbd ? <StateBadge kind="tbd" /> : null}
              <p className={styles.noCountdownLine}>{isTbd ? NO_COUNTDOWN_KO : FIELD_ABSENT_KO}</p>
            </div>
          )}

          <WindowLine detail={detail} />
        </div>
      )}
    </CraftPanel>
  );
}

/**
 * The mono window/state line under the countdown.
 *
 * The window is two served calendar days and is printed as it is. The *state*
 * phrase beside it is per rights type, because "지남" does not mean the same
 * thing in each (`ui-traps.md` #5): an ① whose 매매기간 is open can still be
 * traded ("거래 가능 · 마감 D-n", live green), an ② whose 전환청구 개시일 has
 * passed is **진행 중** — never 종료 — and ③'s two deadlines carry their own
 * 기한 지남 chips inside the step block rather than a phrase here.
 */
function WindowLine({ detail }: { detail: EventDetail }) {
  const [start, end] = detail.countdown.window;
  const open = detail.countdown.window_state === "open";
  const dday = detail.countdown.dday;

  const phrase =
    open && detail.rights_type === "R1" && dday
      ? tradingOpenKo(dday)
      : open && detail.rights_type === "R2"
        ? CONVERSION_OPEN_KO
        : null;

  if (!start && !end && !phrase) return null;

  return (
    <p className={styles.windowLine}>
      {start && end ? (
        <span className="mono">
          {start} ~ {end}
        </span>
      ) : null}
      {phrase ? <span className={styles.live}>{phrase}</span> : null}
    </p>
  );
}
