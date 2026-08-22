"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { OPS_TABS } from "./copy";
import styles from "./Ops.module.css";

/**
 * The six signed sections (개요 · 게이트 대기열 · 정확도·비용 · 대화 로그 ·
 * 사용자 · 피드백).
 *
 * Each one is a route, not a panel switch: R7 forbids 컴포넌트 단편 화면 and asks
 * for 완전한 페이지, and routing is also what makes 「로그인 후 있던 탭 복원」 free
 * — the door renders in place at the tab's own URL, so the path never moves.
 *
 * Active state is R2's, unchanged: 600 + a 2px underline. `/ops` is matched
 * exactly, or it would underline itself on every other tab.
 */
export function OpsTabs() {
  const pathname = usePathname() ?? "";
  return (
    <nav className={styles.tabs}>
      {OPS_TABS.map((tab) => {
        const active = tab.key === "overview" ? pathname === tab.href : pathname.startsWith(tab.href);
        return (
          <Link
            key={tab.href}
            href={tab.href}
            className={active ? `${styles.tab} ${styles.tabActive}` : styles.tab}
            aria-current={active ? "page" : undefined}
          >
            {tab.label}
          </Link>
        );
      })}
    </nav>
  );
}
