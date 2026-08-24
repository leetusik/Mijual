import { SAMPLE_BANNER_KO } from "./copy";
import styles from "./Portfolio.module.css";

/**
 * The 샘플 포트폴리오 banner (R5-4).
 *
 * > 로드 상태: **2층 표면에 inset 배너("구성 예시" 문구)** + nav 「샘플」 칩 +
 * > 샘플 종료 (로그인 슬롯 대체 — 메뉴 자리). **가짜 이메일·알림 이력 렌더 금지**;
 * > 샘플에서 알림 설정 숨김.
 *
 * An inset band at the top of the surface, and nothing more. **R8 retired the
 * nav's 「샘플」 chip and R13 (Q-D) withdrew R5-4's 샘플 종료 clause outright** —
 * `clearSample()` runs only on 계정 이전 now — so this line is the *only* thing in
 * the product that says a portfolio is a sample, and it is stated rather than
 * offered: no controls, no brackets. The known consequence is recorded rather
 * than dressed up: a row deleted from a sample does not come back in that
 * browser. The mode's other two rules are structural rather than drawn — the
 * payload carries no account fact at all (`P5.S8` note 8: no address, no 알림
 * 설정, no `claimed` key), and the account menu that would link 알림 설정 is not
 * rendered while a sample is loaded.
 *
 * **R13 §4b revised the first two words** of the sentence itself: 샘플 **보유
 * 종목** — a reader surface never says 「포트폴리오」 (see `copy.ts`).
 */
export function SampleBanner() {
  return <p className={styles.banner}>{SAMPLE_BANNER_KO}</p>;
}
