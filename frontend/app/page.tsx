import {
  Citation,
  CraftPanel,
  DDay,
  EstimateMarker,
  LapseAlert,
  RightsChip,
  StateBadge,
  lapseNumeralClass,
} from "@/components";
import styles from "./page.module.css";

/**
 * The foundation proof page — **`P5.S12` (landing 관제 현황판) replaces it.**
 *
 * `P5.S10` builds no page surface: the landing, the detail pages and 내 종목 조회
 * are S12–S14. What this route does is prove that the foundation renders end to
 * end — the cosmos root, the vendored tokens, the content column, a craft panel
 * and each trust primitive — so `next build` fails here rather than three slices
 * later. It is the slice's smoke check, drawn rather than asserted.
 *
 * **Every string on it is verbatim from the landed record**, and none is composed
 * into a surface: the quote and its span are `grounding/samples/r1-live-healthy.json`
 * (계양전기 `20260724000546`), the headline figure is `headline-numbers.md`, and the
 * 소멸주의보 body is that file's 발표용 문장 4 as printed. The pack is dated
 * 2026-08-20, so these are **fixed sample values, not live data** — the real
 * numbers arrive from `/board/summary` when S12 builds the page.
 */
export default function FoundationProof() {
  return (
    <main className={`content ${styles.main}`}>
      <CraftPanel className={styles.row}>
        <RightsChip rightsType="R1" />
        <RightsChip rightsType="R2" />
        <RightsChip rightsType="R3" compact />

        <EstimateMarker estimated={true}>
          <span className="mono">718.1억원</span>
        </EstimateMarker>
        <EstimateMarker estimated={false}>
          <span className="mono">22,100원</span>
        </EstimateMarker>

        <DDay dday="D-5" days={5} date="2026-08-25" />
        <DDay dday="D-DAY" days={0} date="2026-08-20" />
        <DDay dday="D+41" days={-41} showDate={false} />

        <StateBadge kind="tbd" />
        <StateBadge kind="mismatch" />

        <Citation
          label="신주인수권증서 상장·매매기간"
          rceptNo="20260724000546"
          quote="3) 신주인수권증서 상장예정기간 : 2026년 08월 19일~ 2026년 08월 25일"
          span={[30615, 30663]}
        />
      </CraftPanel>

      <LapseAlert>
        지금도 <span className={`mono ${lapseNumeralClass}`}>15건</span>의 신주인수권이 소멸을
        앞두고 있습니다 (가장 빠른 청약 마감{" "}
        <span className={`mono ${lapseNumeralClass}`}>2026-09-04</span>, 계양전기).
      </LapseAlert>
    </main>
  );
}
