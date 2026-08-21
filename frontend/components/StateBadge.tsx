import {
  MISMATCH_LABEL_KO,
  TBD_DISPLAY_KO,
  WITHDRAWN_NOTICE_KO,
  type RightsType,
} from "@/lib/copy";
import styles from "./StateBadge.module.css";

/**
 * The three product states that are answers rather than error handling.
 *
 * | kind | what it renders | rule |
 * |---|---|---|
 * | `tbd` | 추후결정 chip | **never with a date beside it.** 추후결정 means *no date*, not an unknown one (`ui-traps.md` #4); the superseded date is structurally absent from the contract and cannot leak. |
 * | `withdrawn` | the locked notice **replacing the card body** | one sentence per rights type, verbatim. R3: no fields, no countdown, no old dates. |
 * | `mismatch` | 발행사 기재 불일치 chip | the locked literal. It says the *issuer's filing* contradicts itself; the two readings sit side by side, each with its own citation, and are never reconciled (`ui-traps.md` #2). |
 *
 * **There is no variant for a blocked field or a blocked event**, and that
 * omission is the design. A field that fails its gate is absent from the payload
 * and the card renders around the hole as if the row had never existed; a blocked
 * event is not on the board and has no page. Not greyed out, not "확인 필요", not
 * a dash with a tooltip — the reason is internal and lives in the operator's
 * panel alone (`states-and-trust.md` §4, D-14).
 */
export type StateBadgeProps =
  | { kind: "tbd"; className?: string }
  | { kind: "mismatch"; className?: string }
  | {
      kind: "withdrawn";
      /** Picks the locked sentence when the payload's own is not to hand. */
      rightsType: RightsType;
      /** The event payload's `notice_ko` — the same string, from the product. */
      noticeKo?: string | null;
      className?: string;
    };

export function StateBadge(props: StateBadgeProps) {
  if (props.kind === "tbd") {
    return (
      <span className={join(styles.tbd, props.className)}>{TBD_DISPLAY_KO}</span>
    );
  }

  if (props.kind === "mismatch") {
    return (
      <span className={join(styles.mismatch, props.className)}>{MISMATCH_LABEL_KO}</span>
    );
  }

  // The payload's own `notice_ko` is preferred over the local table: both are the
  // same locked string, but the served one is the product's, and if the product
  // ever changes it the surface must not keep repeating an older copy.
  const notice = props.noticeKo ?? WITHDRAWN_NOTICE_KO[props.rightsType];
  return (
    <p role="status" className={join(styles.withdrawn, props.className)}>
      {notice}
    </p>
  );
}

function join(base: string, extra?: string): string {
  return extra ? `${base} ${extra}` : base;
}
