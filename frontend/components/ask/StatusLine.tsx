import styles from "./Blocks.module.css";

/**
 * 진행 표시 — the one transient line (R16 §2.1).
 *
 * > 한 줄. mono `--text-xs` ink-3. 왼쪽 테두리 **2px dashed `--border-soft`** +
 * > `padding-left 8px`. (도구 행은 2px **solid** — 실선 = 남는 사실, 점선 =
 * > 지나가는 상태.) `nowrap` + 가로 스크롤(스크롤바 숨김). `role="status"`. 자리:
 * > 답변 상자의 **마지막** 자식(푸터·끝맺음 앞). 항상 1개. phase가 바뀌면 텍스트만
 * > 교체. 첫 `TextEvent`가 오면 제거. **애니메이션 금지** (스피너·점·페이드 없음).
 *
 * Three of those sentences are already true before this component runs, and that
 * is deliberate: 「항상 1개」 is the store's keyed reduce on the constant
 * `block_id` `"status"` (`P9.S3` note 2 / `P9.S8` note 1), 「제거」 is the store
 * dropping it at the first prose block and at every terminal (`P9.S8` note 3),
 * and the sentence itself is the **server's** (`mijual.agent.copy.STATUS_KO`) —
 * rendered verbatim like a 도구 행, which is why `components/ask/copy.ts` holds no
 * status strings. So all this file does is draw one line in one place, and 「phase가
 * 바뀌면 텍스트만 교체」 falls out of React updating the same element's text.
 *
 * **No animation of any kind.** R6's 스피너·타이핑 점 금지 is not superseded by
 * this element — it is the element that replaces them.
 */
export function StatusLine({ text }: { text: string }) {
  return (
    <p className={styles.status} role="status">
      {text}
    </p>
  );
}
