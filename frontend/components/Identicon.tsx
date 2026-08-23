import { IDENTICON_LABEL_KO } from "@/lib/copy";
import { type IdenticonSize, identicon } from "@/lib/identicon";
import styles from "./Identicon.module.css";

/**
 * 계정 아이디콘 — R8's generated account mark (build-prompt §5,
 * `Identicon.prompt.md`).
 *
 * > The account slot's generated mark. Introduced in R8 to replace the 축약
 * > 이메일 as the slot's identity: the reader sees their **full email** plus a
 * > mark that is theirs and nobody else's.
 *
 * The arithmetic is `lib/identicon.ts` (pure, tested); this component only
 * paints it, and paints it the way R1's system paints everything — square cells
 * in a square hairline frame, no radius, no gradient, no shadow.
 *
 * Three rules the record states out loud and this file obeys:
 *
 * 1. **Only the four data hues.** `--alert` is reserved for 소멸/기한 and
 *    `--brand` is the mark that carries no data colour, so neither can be drawn
 *    by a decoration. The hue arrives as a **token name** and is resolved through
 *    `var()`, so the cosmos scope remaps it like every other component.
 * 2. **It is decoration for recognition, not data** — `role="img"` with a label,
 *    and it never replaces the email (both slots render the address beside it).
 * 3. **20 / 28 / 40 only** ("size/5가 정수"). The size is the *cell grid's* box:
 *    the 1px hairline sits outside it (`box-sizing: content-box`), so a cell is
 *    exactly `size / 5` whole pixels rather than `(size - 2) / 5`.
 */
export type IdenticonProps = {
  /** The seed — today the account email (the round left the source to the build:
   * "둘 중 무엇이든 이 함수의 입력일 뿐"). */
  seed: string;
  size?: IdenticonSize;
  /** The accessible name. Defaults to the record's own 「계정 아이디콘」. */
  title?: string;
  className?: string;
};

export function Identicon({ seed, size = 20, title, className }: IdenticonProps) {
  const { hue, cells } = identicon(seed);
  const cell = size / 5;

  return (
    <span
      role="img"
      aria-label={title ?? IDENTICON_LABEL_KO}
      className={[styles.mark, className].filter(Boolean).join(" ")}
      style={{ width: `${size}px`, height: `${size}px` }}
    >
      {cells.map((row, rowIndex) =>
        row.map((filled, columnIndex) => (
          <span
            key={`${rowIndex}-${columnIndex}`}
            className={styles.cell}
            style={{
              width: `${cell}px`,
              height: `${cell}px`,
              background: filled ? `var(${hue})` : "transparent",
            }}
          />
        )),
      )}
    </span>
  );
}
