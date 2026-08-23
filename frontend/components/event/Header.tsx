import { DDay, RightsChip, StateBadge } from "@/components";
import { DeadlineOffer } from "@/components/auth";
import { dartUrl } from "@/lib/api";
import type { EventDetail } from "@/lib/types";
import {
  CONVERSION_OPEN_KO,
  CORRECTED_KO,
  DART_LINK_KO,
  FIELD_ABSENT_KO,
  FIRST_FILED_KO,
  NO_COUNTDOWN_KO,
  PAST_STEP_KO,
  RCEPT_NO_KO,
  identityLineKo,
  tradingOpenKo,
} from "./copy";
import styles from "./Event.module.css";

/**
 * The detail page's header (R3 §Page anatomy 2, re-cut by **R10 §1**).
 *
 * > 좌: RightsChip → `h1` 회사명 + `DART 원문 ↗` → 본문 표기 줄(조건부) → 메타
 * > 줄. 우(`.cd`): 라벨 → DDay / StateBadge / 부재 칩 → 창 줄 → 담기 링크.
 *
 * ## What R10 changed, and why each one was a defect
 *
 * **One size in every state** (`min-height: 136px` / 248px ≤767px, an in-session
 * operator direction): the header used to grow and shrink with what it had to
 * say, so moving between events re-laid the body out under the reader. A state
 * with little to say now spreads its rows instead of leaving a hole.
 *
 * **The meta line cannot orphan a separator**: each item is `nowrap` and the
 * `·` is glued to the item that *follows* it, so a wrap takes the dot with it.
 * At ≤767px the separators are off entirely and 접수번호 takes its own line.
 *
 * **A closed window says so.** 「기한 지남」 — ③'s own step chip, not new copy —
 * now marks a closed ① window too, which used to render as bare dates beside a
 * D+44 (walk finding 6). ② is exempt on purpose: its 전환청구 window *opens*, so
 * a past opening is 「진행 중」 and **never 종료** (`ui-traps.md` #5).
 *
 * **Absence is drawn, not written into a sentence**: 「현재 버전 공시에 없음」 is
 * a **dashed** chip and 추후결정 is a solid `StateBadge`. The dashed/solid
 * difference is the contract — one says the filing does not carry the field, the
 * other says the filing answered 추후결정 — and neither says why (D-14).
 *
 * ## The three things this component still refuses to do
 *
 * **It computes no date and no D-day.** `countdown.dday`, `days`, `date`,
 * `window` and `reference` all arrive computed in KST (D-10).
 *
 * **It never fills an empty countdown slot.** `countdown.date === null` has two
 * different causes — the governing field is served and says 추후결정, or it is
 * absent from the payload altogether — and each gets its own mark, read from
 * `countdown.source`, whose first segment names the field it would have come
 * from.
 *
 * **It never silently corrects the company's name** (`ui-traps.md` #3).
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
  const hasDDay = Boolean(countdown.date) && countdown.dday !== null && countdown.days !== null;

  return (
    <header className={styles.hd}>
      <div className={styles.hid}>
        <div className={styles.hchip}>
          <RightsChip rightsType={detail.rights_type} />
        </div>

        <div className={styles.corpline}>
          <h1 className={styles.corp}>{name}</h1>
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
        </div>

        {detail.corp_name_agrees_with_body === false && detail.corp_name_in_body ? (
          <p className={styles.idnote}>{identityLineKo(detail.corp_name_in_body)}</p>
        ) : null}

        <p className={styles.meta}>
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
          {versions > 1 ? <span className={styles.corr}>{CORRECTED_KO}</span> : null}
        </p>
      </div>

      {withdrawn ? null : (
        <div className={styles.cd}>
          <p className={styles.cdlab}>{countdown.label_ko}</p>

          <div className={styles.ddayslot}>
            {hasDDay ? (
              <DDay
                dday={countdown.dday as string}
                days={countdown.days as number}
                date={countdown.date}
              />
            ) : isTbd ? (
              <StateBadge kind="tbd" />
            ) : (
              <span className={styles.absent}>{FIELD_ABSENT_KO}</span>
            )}
          </div>

          {/* 추후결정's own sentence — the badge says the state, this says what
              follows from it. Never a date beside either (`ui-traps.md` #4). */}
          {!hasDDay && isTbd ? <p className={styles.win}>{NO_COUNTDOWN_KO}</p> : null}

          <WindowLine detail={detail} />

          {/* R5-2's second conversion touchpoint, relabelled by R10 to 「보유
              종목에 담기 →」. It is gated on a deadline that is still ahead —
              "이 마감 알림 받기" under an anchor already behind the reference day
              would promise an alert nothing can send (the 시점 칩 are 7/3/1/0
              days *before* a deadline), and a 추후결정 event has no 마감 to be
              alerted about at all. The gate is this build's reading; the line
              itself is signed, and R10 confirms it ("담기 줄은 마감이 아직 남은
              건에만"). */}
          {countdown.date && countdown.days !== null && countdown.days >= 0 ? (
            <DeadlineOffer corpCode={detail.corp_code} className={styles.offer} />
          ) : null}
        </div>
      )}
    </header>
  );
}

/**
 * The mono window/state line under the countdown (R10 §1's table).
 *
 * The window is two served calendar days and is printed as it is — **the dates
 * are never dropped**, in any state; the state word tells the reader how to read
 * them, it does not replace them. The word itself is per rights type, because
 * "지남" does not mean the same thing in each (`ui-traps.md` #5):
 *
 * | | |
 * |---|---|
 * | ① open | 「거래 가능 · 마감 D-n」, live |
 * | ① closed · ③ closed | 「기한 지남」, the same chip ③'s steps wear |
 * | ② past opening | 「진행 중」, live — **never 종료** |
 * | ② before opening | nothing: there is nothing to say yet |
 */
function WindowLine({ detail }: { detail: EventDetail }) {
  const [start, end] = detail.countdown.window;
  const state = detail.countdown.window_state;
  const dday = detail.countdown.dday;
  const type = detail.rights_type;

  const phrase =
    state === "open" && type === "R1" && dday
      ? tradingOpenKo(dday)
      : state === "open" && type === "R2"
        ? CONVERSION_OPEN_KO
        : null;
  // ②'s window is not the kind that closes, so it never wears the chip.
  const past = state === "closed" && type !== "R2";

  if (!start && !end && !phrase && !past) return null;

  return (
    <p className={styles.win}>
      {start && end ? (
        <span className="mono">
          {start} ~ {end}
        </span>
      ) : null}
      {phrase ? <span className={styles.live}>{phrase}</span> : null}
      {past ? <span className={styles.past}>{PAST_STEP_KO}</span> : null}
    </p>
  );
}
