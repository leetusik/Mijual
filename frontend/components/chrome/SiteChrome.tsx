import type { ReactNode } from "react";
import { SiteFooter } from "./Footer";
import { SiteNav } from "./Nav";
import { VockyScript } from "./VockyScript";
import styles from "./SiteChrome.module.css";

/**
 * The chrome every page sits inside — nav, page, footer, and vocky's script.
 *
 * R2 designs the landing *and* "the **global chrome** every later surface lives
 * in (nav, footer, mobile navigation, page shell)", so this is a layout
 * component the root layout wraps every route in: one nav, one footer, one
 * script tag, no matter how many routes a reader walks through. A page renders
 * its own `<main>` — the chrome does not wrap the content in an element that
 * would compete with a surface's own composition.
 *
 * What it deliberately does not do: nothing here is `position: fixed` and
 * nothing occupies a corner. R2's §6-4 decision is "chrome-level but not
 * floating … No floating corner button", and P6's AI 질문 launcher lands in the
 * bottom-right ("런처·위젯은 vocky 트리거와 모서리 충돌 금지") — that corner is
 * left clear.
 */
export function SiteChrome({ children }: { children: ReactNode }) {
  return (
    <div className={styles.frame}>
      <SiteNav />
      <div className={styles.page}>{children}</div>
      <SiteFooter />
      <VockyScript />
    </div>
  );
}
