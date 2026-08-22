import type { ReactNode } from "react";
import { count as formatCount } from "@/lib/format";
import { KST, NONE_KO } from "./copy";
import styles from "./Ops.module.css";

/**
 * The small pieces every ops tab is built from.
 *
 * They exist so the idiom is stated once: an opaque `#0e1a15` panel with a 1px
 * hairline and no ornament, a mono cell for anything the machine wrote, and one
 * way of printing a KST instant. Nothing here renders a Korean string of its
 * own — the two it can print (`KST`, 「없음」) come from `./copy.ts` with their
 * citations.
 */

export function Panel({
  title,
  note,
  children,
}: {
  title?: ReactNode;
  /** A mono line beside the title — a basis, a source, a count. */
  note?: ReactNode;
  children: ReactNode;
}) {
  return (
    <section className={styles.panel}>
      {(title || note) && (
        <div className={styles.panelHead}>
          {title && <h2 className={styles.panelTitle}>{title}</h2>}
          {note && <span className={styles.panelNote}>{note}</span>}
        </div>
      )}
      {children}
    </section>
  );
}

/** Codes, identifiers and stage output: raw English in mono (R7 §6.1/§6.2). */
export function Code({ children }: { children: ReactNode }) {
  return <span className={styles.code}>{children}</span>;
}

/** A count, grouped the way every numeral in this product is. */
export function Num({ value }: { value: number | string }) {
  return <span className={styles.code}>{formatCount(value)}</span>;
}

/**
 * An absolute `+09:00` instant, **sliced rather than `Date`-parsed** — parsing
 * would re-render it in the operator's own timezone, and every instant in this
 * product is KST by contract (D-10, and `lib/format.kstStamp`'s own rule).
 */
export function Stamp({
  instant,
  seconds = false,
  suffix = true,
}: {
  instant?: string | null;
  seconds?: boolean;
  suffix?: boolean;
}) {
  if (!instant) return <span className={styles.faint}>{NONE_KO}</span>;
  const text = `${instant.slice(0, 10)} ${instant.slice(11, seconds ? 19 : 16)}`;
  return (
    <span className={styles.code}>
      {text}
      {suffix ? ` ${KST}` : ""}
    </span>
  );
}

/** 「없음」 as a *state* — R7 forbids a placeholder where a value would be, and
 * this is the word it names for evidence a blocked row genuinely does not have. */
export function Absent() {
  return <span className={styles.faint}>{NONE_KO}</span>;
}

/** rcept_no verbatim + its DART link, the panel's citation handle (R7). */
export function Rcept({ rceptNo, url }: { rceptNo?: string | null; url?: string }) {
  if (!rceptNo) return <Absent />;
  if (!url) return <Code>{rceptNo}</Code>;
  return (
    <a className={`${styles.code} ${styles.link}`} href={url} target="_blank" rel="noreferrer">
      {rceptNo}
    </a>
  );
}

/**
 * One line of the decisions document, rendered with its own emphasis.
 *
 * The 가동 전 미결 panel quotes `docs/current/decisions.md` verbatim, so the text
 * arrives with markdown in it (`**Open, …:**`, `` `operations` ``). This turns
 * those two markers into the emphasis they mean and changes not one word — the
 * alternative was printing asterisks at the operator or editing the quotation.
 */
export function Quoted({ text }: { text: string }) {
  const parts = text.split(/(\*\*[^*]+\*\*|`[^`]+`)/g).filter(Boolean);
  return (
    <>
      {parts.map((part, index) => {
        if (part.startsWith("**") && part.endsWith("**")) {
          return <strong key={index}>{part.slice(2, -2)}</strong>;
        }
        if (part.startsWith("`") && part.endsWith("`")) {
          return (
            <span key={index} className={styles.code}>
              {part.slice(1, -1)}
            </span>
          );
        }
        return <span key={index}>{part}</span>;
      })}
    </>
  );
}
