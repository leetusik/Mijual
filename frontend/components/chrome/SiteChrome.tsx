"use client";

import type { ReactNode } from "react";
import { usePathname } from "next/navigation";
import { isOpsPath } from "@/components/ops/routes";
import { SiteFooter } from "./Footer";
import { SiteNav } from "./Nav";
import { VockyScript } from "./VockyScript";
import styles from "./SiteChrome.module.css";

/**
 * The chrome every **reader** page sits inside — nav, page, footer, and vocky's
 * script.
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
 *
 * ## 운영 관제 gets none of it (`P5.S17`)
 *
 * R7's admin surface is "**reader chrome 어디에서도 링크 금지**" and its own
 * pages carry the **ops** chrome instead (the pre-auth door carries no chrome at
 * all: 빈 페이지 가운데 문 하나). So under `/ops` this component renders its
 * children and nothing else — no nav, no footer, no vocky script, and no reader
 * link anywhere in the markup.
 *
 * That decision has to be made where the path is known, which is why this is a
 * client component: a root layout cannot read the pathname, and the alternative
 * — moving every reader route into a route group with its own layout — would
 * have changed which layout the framework's own 404 renders inside, a surface
 * `P5.S13` already verified. The children are server-rendered and passed in as a
 * prop, so nothing about the pages themselves moves to the client.
 */
export function SiteChrome({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  if (isOpsPath(pathname ?? "")) return <>{children}</>;

  return (
    <div className={styles.frame}>
      <SiteNav />
      <div className={styles.page}>{children}</div>
      <SiteFooter />
      <VockyScript />
    </div>
  );
}
