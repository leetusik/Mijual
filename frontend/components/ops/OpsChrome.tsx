import type { ReactNode } from "react";
import type { OpsLock } from "@/lib/types";
import { OPERATOR_ONLY_KO, OBSERVATION_ONLY_KO, OPS_MARK } from "./copy";
import { LockChip } from "./LockChip";
import { LogoutButton } from "./LogoutButton";
import { OpsClock } from "./OpsClock";
import { OpsTabs } from "./OpsTabs";
import { Stamp } from "./atoms";
import styles from "./Ops.module.css";

/**
 * The ops chrome every authenticated section sits inside.
 *
 * > 모든 섹션은 완전한 페이지 (상단 ops 바: 탭 · lock 칩 실시간 · KST 시계 ·
 * > 로그아웃 / 하단 상태 푸터) — 컴포넌트 단편 렌더 금지.
 *
 * It is **not** the reader chrome and shares nothing with it: `SiteChrome`
 * renders nothing under `/ops`, so there is no nav, no footer, no vocky script
 * and no reader link anywhere in this markup (R7: reader chrome 어디에서도 링크
 * 금지 — and nothing links *out* to a reader surface either, which is the same
 * boundary from the other side).
 *
 * The status footer states the two facts that are true of every tab — 운영자
 * 전용 and 순수 관찰 (§6.5's 전 화면 읽기 전용) — beside the instant the tab's own
 * payload was served at, so a stale tab is visible rather than inferred.
 */
export function OpsChrome({
  lock,
  asOf,
  children,
}: {
  /** Server-rendered at page load; the chip re-reads it live from there on. */
  lock: OpsLock | null;
  /** The `as_of` of this tab's own payload. */
  asOf?: string;
  children: ReactNode;
}) {
  return (
    <>
      <header className={styles.bar}>
        <span className={styles.mark}>{OPS_MARK}</span>
        <OpsTabs />
        <div className={styles.barRight}>
          <LockChip initial={lock} />
          <OpsClock />
          <LogoutButton />
        </div>
      </header>

      <main className={styles.ops}>{children}</main>

      <footer className={styles.statusFooter}>
        <span>{OPERATOR_ONLY_KO}</span>
        <span>·</span>
        <span>{OBSERVATION_ONLY_KO}</span>
        {asOf && (
          <>
            <span>·</span>
            <Stamp instant={asOf} seconds />
          </>
        )}
      </footer>
    </>
  );
}
