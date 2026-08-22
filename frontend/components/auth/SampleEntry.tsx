import Link from "next/link";
import { samplePath } from "@/lib/routes";
import { SAMPLE_ENTRY_KO, SAMPLE_ENTRY_SUB_KO, SAMPLE_LANDING_KO } from "./copy";
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
 * The landing variant is the round's own second placement. It sits at the foot of
 * the landing **page**, not in the global footer: R5's chrome section says
 * "Footer 불변" and its signoff records the round as extending only the account
 * slot, so this is a landing/sample element rather than chrome (`P5.S11` note 11
 * reached the same reading and left it here).
 *
 * Neither entry is conditional. R5-4 places them unconditionally, the sample is
 * anonymous end to end, and a judge must reach it "without hunting" (the round's
 * handoff §4) — so nothing about a session hides them.
 */
export function SampleEntry({ variant = "auth" }: { variant?: "auth" | "landing" }) {
  if (variant === "landing") {
    return (
      <Link className={styles.landingSample} href={samplePath()}>
        {SAMPLE_LANDING_KO}
      </Link>
    );
  }

  return (
    <section className={styles.sample}>
      <Link className={styles.sampleLink} href={samplePath()}>
        {SAMPLE_ENTRY_KO}
      </Link>
      <p className={styles.sampleSub}>{SAMPLE_ENTRY_SUB_KO}</p>
    </section>
  );
}
