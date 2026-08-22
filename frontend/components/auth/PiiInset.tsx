import { PII_NOT_STORED_KO, PII_RECEIVES_KO } from "./copy";
import styles from "./Auth.module.css";

/**
 * The PII inset — R5-1's **permanent** element on the auth screen.
 *
 * > PII 패널은 로그인 화면 상시 요소 (inset)
 *
 * and its content, from the same revision:
 *
 * > PII 패널 유지: "미주알이 받는 것: 이메일 주소와 비밀번호" + "저장하지 않는
 * > 것은 유출되지 않습니다"
 *
 * `security` states the same thing as a boundary rather than as copy: "The PII
 * statement is a **permanent inset panel on the auth screen**, not a link to a
 * policy page." So it renders in both modes, it is never behind a disclosure, and
 * it is not a link.
 *
 * Both sentences are true by construction rather than by promise: `P5.S7`'s
 * `account` table is `id · email · password_hash · created_at · updated_at` and
 * nothing else — no name, no phone, no admin flag, no activity trail.
 *
 * ⚠ R5's copy list writes "PII 패널 **3행**" while the revision quotes two
 * sentences; the third row is on the card, which stays in the Claude Design
 * project. Two signed lines render and no third is invented — flagged for
 * `P5.S19` to check against the card.
 */
export function PiiInset() {
  return (
    <aside className={styles.pii}>
      <p className={styles.piiLine}>{PII_RECEIVES_KO}</p>
      <p className={styles.piiLine}>{PII_NOT_STORED_KO}</p>
    </aside>
  );
}
