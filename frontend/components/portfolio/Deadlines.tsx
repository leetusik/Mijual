"use client";

import Link from "next/link";
import { CraftPanel, DDay, EstimateMarker, RightsChip, StateBadge } from "@/components";
import { Conversion, Dilution } from "@/components/lookup";
import { perHoldingCaption, perHoldingColumnKo } from "@/components/lookup/copy";
import { count, won } from "@/lib/format";
import { convert } from "@/lib/holding";
import { stockPath } from "@/lib/routes";
import type { RightsRow } from "@/lib/types";
import {
  CLAIMED_LABEL_KO,
  CLAIM_CAPTION_ACCOUNT_KO,
  CLAIM_CAPTION_LOCAL_KO,
  CLAIM_CHECK_KO,
  MISSED_DETAIL_KO,
  MISSED_LABEL_KO,
  PAST_SECTION_KO,
  STEP_DEPENDENCY_KO,
  UPCOMING_SECTION_KO,
  pastNoticeChipKo,
  pastPeriodChipKo,
  referenceKo,
} from "./copy";
import styles from "./Portfolio.module.css";

/**
 * D-day 목록 — 보유 종목's home view (R5 §D-day 목록, **re-cut by R13 §1**).
 *
 * > 섹션 2개: 다가오는 마감(D-day 오름차순) · 지나간 마감(최근순). 앵커 날짜 명기
 * > ("기준 YYYY-MM-DD (KST)"), **모든 D-day는 상류 계산값 — 브라우저 계산 금지**.
 * > Per-type governing anchor: ① 증서 매매 마감 · ② 전환청구 개시 · ③ 반대의사
 * > 통지 마감.
 * > 금액 = R4 계약 그대로: ① 확정발행가 있음 → 「추정」 금액; 확정 전 → 주수 +
 * > `발행가 확정 전` 칩 + 확정 예정일; ②/③ → 금액 절대 없음. **내 종목 조회와 수치
 * > 불일치 금지 (같은 contract 소스).**
 *
 * ## R13: the row is four tracks, and the body lands on them
 *
 * R5 drew the row head as a `space-between` flex, which is a geometry only its
 * own content can decide: at 1440 the right-hand block's left edge was ragged by
 * 144.7px down the list and the middle of the page was 584.6–761.3px of nothing
 * (P7 Q8-A, measured). R13 §1 replaces it with **four content-independent
 * tracks** shared by every row of *both* sections —
 *
 *     [칩 84px] [종목 minmax(0,1fr)] [지배 라벨 212px] [카운트다운 208px]
 *
 * — no column headers and no vertical rules, because a D-day row is a deadline
 * with a body, not a record. The row's **body** then lands on those same tracks:
 * every block starts at column 2 and every 소멸 금액 ends in column 4, so the money
 * reads down the same right edge as the countdown it belongs to.
 *
 * Three consequences worth stating, each a signed decision rather than a detail:
 *
 * - **The anchor is the page's, not a section's** (finding 3). Every D-day in the
 *   payload — the 지나간 ones too — was computed against the one served
 *   `reference`, so 「기준 … (KST)」 stands **once above the block**, outside both
 *   sections. Under 다가오는 마감 it read as that section's property; on both it
 *   would have implied two anchors.
 * - **A 지나간 row's chip and date are one line** (§1). Stacked, they left a half
 *   line of hole under the 지배 라벨; the 208px last track is sized so the longest
 *   chip (「통지 마감 지남 · D+n」) and the date fit side by side.
 * - **The 「놓친 돈 상세 →」 link lives in the money line** (Q-B, R13 session
 *   revision) and a checked row does not render it at all. See `LapsedMoney`.
 *
 * ## How "수치 불일치 금지" is kept structurally rather than carefully
 *
 * Both sections are served (`P5.S8`'s `upcoming` / `past` — the placement rule,
 * the ordering and every anchor are the server's), every D-day is the payload's
 * own `countdown`, and the two type blocks are **the components 조회 renders**:
 * `Conversion` for ① and `Dilution` for ②, imported from `components/lookup`
 * rather than re-drawn here. So a number cannot differ between the surfaces —
 * there is one composition (`reads._rights_row`), one multiplication site
 * (`lib/holding.ts`) and one rendering. R13 gives those blocks the row's column
 * placement (`.rowBody`) and nothing else: the canon's own cell mimic is a card
 * harness, and forking it here would be the second composition site this product
 * has spent two rounds not having.
 *
 * ③ carries the 2단계 dependency line and no money, ② carries R4's three dilution
 * facts and no per-holding amount, and neither can carry a won figure by
 * construction — `OfferingInputs` is ①'s shape and the portfolio row does not
 * load `appraisal_price` at all (`P5.S8` note 6).
 */
export function Deadlines({
  reference,
  upcoming,
  past,
  sharesOf,
  claimedOf,
  onClaim,
  claimCaption,
  busy,
}: {
  reference: string;
  upcoming: RightsRow[];
  past: RightsRow[];
  sharesOf: (row: RightsRow) => number | null;
  /** `null` where the mark does not apply to this row. */
  claimedOf: (row: RightsRow) => boolean | null;
  onClaim: (row: RightsRow, claimed: boolean) => void;
  claimCaption: "account" | "local";
  busy: boolean;
}) {
  // No rows at all — a sample the reader has emptied, or an account with no
  // deadlines — states nothing, anchor included: an anchor with nothing under it
  // would be a date about no deadline.
  if (upcoming.length === 0 && past.length === 0) return null;

  return (
    <div className={styles.deadlines}>
      <p className={`mono ${styles.reference}`}>{referenceKo(reference)}</p>

      <Section
        title={UPCOMING_SECTION_KO}
        rows={upcoming}
        past={false}
        sharesOf={sharesOf}
        claimedOf={claimedOf}
        onClaim={onClaim}
        claimCaption={claimCaption}
        busy={busy}
      />
      <Section
        title={PAST_SECTION_KO}
        rows={past}
        past
        sharesOf={sharesOf}
        claimedOf={claimedOf}
        onClaim={onClaim}
        claimCaption={claimCaption}
        busy={busy}
      />
    </div>
  );
}

function Section({
  title,
  rows,
  past,
  sharesOf,
  claimedOf,
  onClaim,
  claimCaption,
  busy,
}: {
  title: string;
  rows: RightsRow[];
  past: boolean;
  sharesOf: (row: RightsRow) => number | null;
  claimedOf: (row: RightsRow) => boolean | null;
  onClaim: (row: RightsRow, claimed: boolean) => void;
  claimCaption: "account" | "local";
  busy: boolean;
}) {
  // A section with no rows states nothing: R5 signs no empty-section sentence,
  // and "0건" would be a phrase about nothing (the landing's own rule for its
  // strips, `P5.S12` note 6).
  if (rows.length === 0) return null;

  return (
    <section className={styles.section}>
      <h2 className={styles.eyebrow}>{`// ${title}`}</h2>

      <CraftPanel>
        <ul className={styles.rows}>
          {rows.map((row) => (
            <DeadlineRow
              key={`${row.event_id}`}
              row={row}
              past={past}
              shares={sharesOf(row)}
              claimed={claimedOf(row)}
              onClaim={onClaim}
              claimCaption={claimCaption}
              busy={busy}
            />
          ))}
        </ul>
      </CraftPanel>
    </section>
  );
}

function DeadlineRow({
  row,
  past,
  shares,
  claimed,
  onClaim,
  claimCaption,
  busy,
}: {
  row: RightsRow;
  past: boolean;
  shares: number | null;
  claimed: boolean | null;
  onClaim: (row: RightsRow, claimed: boolean) => void;
  claimCaption: "account" | "local";
  busy: boolean;
}) {
  const countdown = row.countdown;
  const dated = countdown.dday !== null && countdown.days !== null;

  return (
    <li className={styles.row}>
      <span className={styles.rowChip}>
        <RightsChip rightsType={row.rights_type} compact />
      </span>

      <p className={styles.rowName}>{row.corp_name ?? row.corp_code}</p>

      <p className={styles.rowLabel}>{countdown.label_ko}</p>

      <div className={styles.rowWhen}>
        {past ? (
          <>
            {/* 지나간 행: the inset chip, faint and never alert-coloured — the
                deadline is history, not a loss (R5: "alert 색 금지"). ③'s chip
                is the round's own second literal. R13 §1 puts the chip and the
                date on **one line**: stacked, they left a half line of hole
                under the 지배 라벨 beside them. */}
            {dated ? (
              <span className={styles.pastChip}>
                {row.rights_type === "R3"
                  ? pastNoticeChipKo(countdown.dday as string)
                  : pastPeriodChipKo(countdown.dday as string)}
              </span>
            ) : null}
            {countdown.date ? (
              <p className={`mono ${styles.pastDate}`}>{countdown.date}</p>
            ) : null}
          </>
        ) : dated ? (
          <DDay dday={countdown.dday as string} days={countdown.days as number} date={countdown.date} />
        ) : (
          <StateBadge kind="tbd" />
        )}
      </div>

      {/* ① — R4's own block, rendered by R4's own component: the price state, the
          배정 신주, and the 환산액 only where 확정발행가 exists. The wrapper is the
          row's column placement (열 2 → 마지막 트랙) and nothing else. */}
      {row.rights_type === "R1" && !past && row.offering ? (
        <div className={styles.rowBody}>
          <Conversion
            factors={row.offering}
            shares={shares}
            finalPriceDate={row.offering.final_price_date}
            confirmedPrice={row.offering.confirmed_price}
          />
        </div>
      ) : null}

      {/* ② — 희석 컨텍스트, the substitute R5 names for a per-holding amount. */}
      {row.rights_type === "R2" && row.convertible ? (
        <div className={styles.rowBody}>
          <Dilution view={row.convertible} />
        </div>
      ) : null}

      {/* ③ — the 2단계 dependency line, and nothing a holder could mistake for a
          payout (R4 §②/③, restated by R5 as "③ 2단계 의존 문장"). */}
      {row.rights_type === "R3" ? <p className={styles.dependency}>{STEP_DEPENDENCY_KO}</p> : null}

      {past && row.rights_type === "R1" && row.lapse ? (
        <LapsedMoney
          row={row}
          shares={shares}
          claimed={claimed}
          onClaim={onClaim}
          claimCaption={claimCaption}
          busy={busy}
        />
      ) : null}
    </li>
  );
}

/**
 * A past ① 소멸 row's money, and R5-8's 챙긴 돈 체크 on it.
 *
 * > 지나간 행 … ① 소멸 행은 500주 기준 「추정」 금액 + "놓친 돈 상세 →" 링크(조회
 * > breakdown으로).
 * > **챙긴 돈 체크 (R5-8)**: 체크박스 "청약·매도로 챙겼습니다". 체크 → 라벨
 * > 놓친 돈 → 챙긴 돈, 금액 동일(「추정」 유지), alert → live, 캡션 "본인 표시 ·
 * > 계정에 저장". 사용자 주장 표시 — 공시 데이터와 혼동 금지(집계·통계에 미반영).
 *
 * The amount is `lib/holding.ts`'s conversion of **this holding's** count against
 * the served 소멸 factors — the same call 조회's breakdown row makes, so the two
 * surfaces print the same number for the same holding — and the check changes
 * nothing about it: same figure, same 「추정」 tag, a different label and a
 * different hue. It reaches no total anywhere, because this payload has none
 * (`P5.S8` note 7: the mark stores no amount and the surface serves no aggregate
 * for it to enter).
 *
 * ## R13 §1 / Q-B — three lines, and why each keeps its height
 *
 * The block is the row's own money grid (`minmax(0,1fr) 208px`), so the value's
 * right edge is the countdown's right edge, exactly.
 *
 * - **The lead line** carries 놓친 돈/챙긴 돈, the 주 basis and — this is Q-B's
 *   session revision — 「놓친 돈 상세 →」 itself. A **checked** row renders no
 *   link: it is saying this is no longer 놓친 돈, so the link that calls 놓친 돈
 *   has nothing to point at. Unchecking brings it back.
 * - **The line keeps the link's height whether or not the link is there**
 *   (`.lapsedLine` `min-height`, 32px desktop / 44px ≤767). A conditional render
 *   that collapses a line is a flicker; the measurement this round asks for is a
 *   **0px** move on check.
 * - **The caption is not conditional** (finding 5). 본인 표시 is the checkbox's own
 *   rule about what the mark is, not a result of ticking it; rendering it only
 *   when checked moved 22.6px on every click.
 */
function LapsedMoney({
  row,
  shares,
  claimed,
  onClaim,
  claimCaption,
  busy,
}: {
  row: RightsRow;
  shares: number | null;
  claimed: boolean | null;
  onClaim: (row: RightsRow, claimed: boolean) => void;
  claimCaption: "account" | "local";
  busy: boolean;
}) {
  const lapse = row.lapse;
  if (!lapse) return null;

  const conversion = convert(lapse, shares);
  const checked = claimed === true;
  const reportNo = lapse.performance_rcept_no;

  return (
    <>
      {conversion.value !== null && shares !== null ? (
        <div className={styles.lapsed}>
          <p className={styles.lapsedLine}>
            <span className={checked ? styles.claimedLabel : styles.missedLabel}>
              {checked ? CLAIMED_LABEL_KO : MISSED_LABEL_KO}
            </span>
            <span className={styles.basis}>{perHoldingColumnKo(count(shares))}</span>
            {checked ? null : (
              <Link className={styles.detailLink} href={stockPath(row.corp_code)}>
                {MISSED_DETAIL_KO}
              </Link>
            )}
          </p>

          <span className={styles.lapsedValue}>
            <EstimateMarker estimated={conversion.valueEstimated}>
              <span className={`mono ${checked ? styles.claimedValue : styles.missedValue}`}>
                {won(conversion.value)}
              </span>
            </EstimateMarker>
          </span>

          {/* 「배정 {k}주 × 「추정」{unit}원」 — the amount's own composition, and
              **조회's**: `perHoldingCaption` is R4's signed caption, rendered here
              exactly as `MissedMoney` renders it (the 「추정」 tag before the
              number, the 원 inside the marker so it cannot land between figure
              and unit). Nothing is minted: this is the same three parts, the same
              two served values. The R13 cards omit it on one row only because the
              design walk's payload lacked that row's factors. */}
          {conversion.allotted !== null && lapse.unit_value ? (
            <p className={styles.caption}>
              {perHoldingCaption.before}
              {count(conversion.allotted)}
              {perHoldingCaption.between}
              <EstimateMarker estimated={lapse.unit_value.estimated}>
                {count(lapse.unit_value.value)}
                {perHoldingCaption.after}
              </EstimateMarker>
            </p>
          ) : null}
        </div>
      ) : null}

      {/* The check exists only where the mark has a key: the 증권발행실적보고서's
          own `rcept_no` (`P5.S8` note 7), which is also what an anonymous mark in
          this browser addresses. The control line carries the checkbox and
          nothing else — Q-B moved the link up into the money line. */}
      {reportNo ? (
        <>
          <div className={styles.claim}>
            <label className={styles.claimLabel}>
              {/* Stamped by extensions before hydration — see `SearchRow.tsx`. */}
              <input
                suppressHydrationWarning
                type="checkbox"
                className={styles.claimBox}
                checked={checked}
                disabled={busy}
                onChange={(event) => onClaim(row, event.target.checked)}
              />
              {CLAIM_CHECK_KO}
            </label>
          </div>
          <p className={`${styles.caption} ${styles.claimCaption}`}>
            {claimCaption === "account" ? CLAIM_CAPTION_ACCOUNT_KO : CLAIM_CAPTION_LOCAL_KO}
          </p>
        </>
      ) : null}
    </>
  );
}
