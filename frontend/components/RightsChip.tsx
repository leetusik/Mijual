import { RIGHTS_LABEL_COMPACT_KO, RIGHTS_LABEL_KO, type RightsType } from "@/lib/copy";
import styles from "./RightsChip.module.css";

/**
 * The rights-type chip: label only, type tint.
 *
 * R1 revision 1 removed the ①②③ numbering from the UI — the numbers survive as
 * internal shorthand in the docs and in `rights_type`, never on a surface. The
 * three hues (① `#2b5aa0` · ② `#96610f` · ③ `#6d3a5d`, remapped by the cosmos
 * scope) are the one place a rights type carries colour, and they are tints, so
 * they never compete with `--live` and `--alert`, which mean something.
 *
 * `compact` is the board's mobile tab and row form (유증 / CB / 매수청구).
 */
export type RightsChipProps = {
  rightsType: RightsType;
  compact?: boolean;
  className?: string;
};

const TONE: Record<RightsType, string> = {
  R1: styles.r1,
  R2: styles.r2,
  R3: styles.r3,
};

export function RightsChip({ rightsType, compact = false, className }: RightsChipProps) {
  const label = compact
    ? RIGHTS_LABEL_COMPACT_KO[rightsType]
    : RIGHTS_LABEL_KO[rightsType];

  return (
    <span
      className={[styles.chip, TONE[rightsType], className].filter(Boolean).join(" ")}
    >
      {label}
    </span>
  );
}
