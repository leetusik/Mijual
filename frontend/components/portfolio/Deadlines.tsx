"use client";

import Link from "next/link";
import { DDay, EstimateMarker, RightsChip, StateBadge } from "@/components";
import { Conversion, Dilution } from "@/components/lookup";
import { perHoldingColumnKo } from "@/components/lookup/copy";
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
 * D-day 목록 — 내 포트폴리오's home view (R5 §D-day 목록).
 *
 * > 섹션 2개: 다가오는 마감(D-day 오름차순) · 지나간 마감(최근순). 앵커 날짜 명기
 * > ("기준 YYYY-MM-DD (KST)"), **모든 D-day는 상류 계산값 — 브라우저 계산 금지**.
 * > Per-type governing anchor: ① 증서 매매 마감 · ② 전환청구 개시 · ③ 반대의사
 * > 통지 마감.
 * > 금액 = R4 계약 그대로: ① 확정발행가 있음 → 「추정」 금액; 확정 전 → 주수 +
 * > `발행가 확정 전` 칩 + 확정 예정일; ②/③ → 금액 절대 없음. **내 종목 조회와 수치
 * > 불일치 금지 (같은 contract 소스).**
 *
 * ## How "수치 불일치 금지" is kept structurally rather than carefully
 *
 * Both sections are served (`P5.S8`'s `upcoming` / `past` — the placement rule,
 * the ordering and every anchor are the server's), every D-day is the payload's
 * own `countdown`, and the two type blocks are **the components 조회 renders**:
 * `Conversion` for ① and `Dilution` for ②, imported from `components/lookup`
 * rather than re-drawn here. So a number cannot differ between the surfaces —
 * there is one composition (`reads._rights_row`), one multiplication site
 * (`lib/holding.ts`) and now one rendering.
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
  return (
    <>
      <Section
        title={UPCOMING_SECTION_KO}
        reference={reference}
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
        reference={null}
        rows={past}
        past
        sharesOf={sharesOf}
        claimedOf={claimedOf}
        onClaim={onClaim}
        claimCaption={claimCaption}
        busy={busy}
      />
    </>
  );
}

function Section({
  title,
  reference,
  rows,
  past,
  sharesOf,
  claimedOf,
  onClaim,
  claimCaption,
  busy,
}: {
  title: string;
  /** The anchor line R5 requires, stated once — on the section that counts down. */
  reference: string | null;
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
    <section className={past ? `${styles.section} ${styles.pastSection}` : styles.section}>
      <h2 className={styles.eyebrow}>{`// ${title}`}</h2>
      {reference ? <p className={`mono ${styles.reference}`}>{referenceKo(reference)}</p> : null}

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
      <div className={styles.rowHead}>
        <div className={styles.rowIdentity}>
          <RightsChip rightsType={row.rights_type} />
          <p className={styles.rowName}>{row.corp_name ?? row.corp_code}</p>
        </div>

        <div className={styles.rowWhen}>
          <p className={styles.whenLabel}>{countdown.label_ko}</p>
          {past ? (
            <>
              {/* 지나간 행: the inset chip, faint and never alert-coloured — the
                  deadline is history, not a loss (R5: "alert 색 금지"). ③'s chip
                  is the round's own second literal. */}
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
      </div>

      {/* ① — R4's own block, rendered by R4's own component: the price state, the
          배정 신주, and the 환산액 only where 확정발행가 exists. */}
      {row.rights_type === "R1" && !past && row.offering ? (
        <Conversion
          factors={row.offering}
          shares={shares}
          finalPriceDate={row.offering.final_price_date}
          confirmedPrice={row.offering.confirmed_price}
        />
      ) : null}

      {/* ② — 희석 컨텍스트, the substitute R5 names for a per-holding amount. */}
      {row.rights_type === "R2" && row.convertible ? <Dilution view={row.convertible} /> : null}

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
    <div className={styles.lapsed}>
      {conversion.value !== null && shares !== null ? (
        <p className={styles.lapsedLine}>
          <span className={checked ? styles.claimedLabel : styles.missedLabel}>
            {checked ? CLAIMED_LABEL_KO : MISSED_LABEL_KO}
          </span>
          <span className={styles.basis}>{perHoldingColumnKo(count(shares))}</span>
          <EstimateMarker estimated={conversion.valueEstimated}>
            <span className={`mono ${checked ? styles.claimedValue : styles.missedValue}`}>
              {won(conversion.value)}
            </span>
          </EstimateMarker>
        </p>
      ) : null}

      <Link className={styles.detailLink} href={stockPath(row.corp_code)}>
        {MISSED_DETAIL_KO}
      </Link>

      {/* The check exists only where the mark has a key: the 증권발행실적보고서's
          own `rcept_no` (`P5.S8` note 7), which is also what an anonymous mark in
          this browser addresses. */}
      {reportNo ? (
        <div className={styles.claim}>
          <label className={styles.claimLabel}>
            <input
              type="checkbox"
              className={styles.claimBox}
              checked={checked}
              disabled={busy}
              onChange={(event) => onClaim(row, event.target.checked)}
            />
            {CLAIM_CHECK_KO}
          </label>
          <p className={styles.caption}>
            {claimCaption === "account" ? CLAIM_CAPTION_ACCOUNT_KO : CLAIM_CAPTION_LOCAL_KO}
          </p>
        </div>
      ) : null}
    </div>
  );
}
