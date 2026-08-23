import Link from "next/link";
import { samplePath } from "@/lib/routes";
import { SAMPLE_ENTRY_KO, SAMPLE_ENTRY_SUB_KO } from "./copy";
import styles from "./Auth.module.css";

/**
 * 샘플 포트폴리오's two signed entries (R5-4).
 *
 * > 진입: 로그인 페이지 하단 + 랜딩 푸터. 원클릭, 가입 없음.
 *
 * Both go to `samplePath()` — `/portfolio?sample=1`, the layer's own route with
 * the mode as a query, because R5 draws the sample as a **loaded state of 내
 * 포트폴리오** (inset 배너 + nav 「샘플」 칩 + 샘플 종료), not as a separate
 * surface. **`P5.S16` implements the mode**; the anonymous endpoint it reads
 * (`GET /portfolio/sample`) already exists and needs no account.
 *
 * **R8 removed the landing placement** (build-prompt §1) — the nav's 보유 종목
 * slot opens the same sample for an anonymous reader, so the line at the foot of
 * the landing said the same thing twice. What is left is R5-4's first placement,
 * the 로그인 page's own bottom entry, which R8 does not touch.
 *
 * It is not conditional. R5-4 places it unconditionally, the sample is anonymous
 * end to end, and a judge must reach it "without hunting" (the round's handoff
 * §4) — so nothing about a session hides it.
 */
export function SampleEntry() {
  return (
    <section className={styles.sample}>
      <Link className={styles.sampleLink} href={samplePath()}>
        {SAMPLE_ENTRY_KO}
      </Link>
      <p className={styles.sampleSub}>{SAMPLE_ENTRY_SUB_KO}</p>
    </section>
  );
}
