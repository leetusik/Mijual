import type { ReactNode } from "react";
import estimate from "@/components/EstimateMarker.module.css";
import { TAG_CALC, TAG_UNVERIFIED } from "./copy";
import styles from "./Blocks.module.css";

/**
 * 「계산」 and 「미확인」 — 추정's two siblings (R16 §2.5).
 *
 * > 마커 가족 (배타적 3종): `추정`(기존, `--text-est`) · `계산`(신규, `--live`) ·
 * > `미확인`(신규, ink-2). 기하는 셋 다 `EstimateMarker` 그대로. 값은 mono 600
 * > tabular-nums nowrap.
 *
 * 「기하는 셋 다 `EstimateMarker` 그대로」 is why this component does not re-derive
 * the tag: it renders `components/EstimateMarker.module.css`'s own `.tag` class,
 * so the three markers are one shape by construction and can never drift apart.
 * **Only the colour is family-specific**, and only the word tells them apart —
 * 「색이 아니라 단어가 구분한다」 (r16-ask.css). The round's own CSS states the
 * geometry in em units (`.22em` vertical-align, `.1em .5em` padding, `.55em`
 * margin) where the shipped `EstimateMarker` states the same shape in its own
 * mix of em and px; the record's binding sentence is 「`EstimateMarker` 그대로」, so
 * the shipped tag is what all three wear. The numeric difference between the two
 * spellings is on `phase.md`'s `## Operator Questions` — changing it would restyle
 * 추정 everywhere, which is a design decision and not this slice's.
 *
 * ## Why `kind` has no default
 *
 * The same discipline `EstimateMarker` states for `estimated`: a value that does
 * not say which kind it is must not construct. The three markers are **exclusive**
 * (§2.5), so a default would be a marker chosen by omission — precisely the
 * failure the family exists to prevent (a computed number wearing 추정, or a
 * tool-verified figure wearing 미확인).
 *
 * 추정 itself is **not** here: it stays `EstimateMarker`, the one estimate mark in
 * the product, and this component never renders that word.
 */
export type ValueMarkerKind = "calc" | "unverified";

const TAGS: Record<ValueMarkerKind, string> = {
  calc: TAG_CALC,
  unverified: TAG_UNVERIFIED,
};

export function ValueMarker({
  kind,
  children,
}: {
  /** Which sibling. No default, on purpose — see above. */
  kind: ValueMarkerKind;
  /** The already-formatted value: the server's own string, never re-formatted. */
  children: ReactNode;
}) {
  return (
    <span className={`${estimate.marker} ${styles.marker}`} data-kind={kind}>
      {children}
      <span className={`${estimate.tag} ${styles.tag}`}>{TAGS[kind]}</span>
    </span>
  );
}
