"use client";

import { useEffect, useState } from "react";
import { getOpsLock } from "@/lib/api";
import type { OpsLock } from "@/lib/types";
import { LOCK_HELD_SINCE_KO } from "./copy";
import { Stamp } from "./atoms";
import styles from "./Ops.module.css";

/**
 * `mijual:lock:pipeline`, live in the ops bar of every tab.
 *
 * > lock 칩: `mijual:lock:pipeline` 실시간 상태 (해제/보유 + 보유 시 시작 시각).
 *
 * Three things it will not do:
 *
 * - **It states the state as a word** (`free` / `held` / `unknown`, the served
 *   tokens, raw and mono per §6.1) rather than as a colour alone.
 * - **`unknown` is rendered, not hidden.** A broker that is down is a fact the
 *   operator wants; `P5.S9` degrades the read instead of failing the tab, and
 *   the served `reason` travels with it.
 * - **The held-since instant comes from the open run row**, never from the
 *   lock's TTL — the lock value is an owner token with no start time, so a
 *   derived one would be an invented number.
 *
 * It re-reads `GET /ops/lock`, which exists so that 실시간 costs one Redis read:
 * polling `/ops/overview` would walk every exposable event to answer one field.
 * A 401 (the 12-hour session ran out) stops the poll and leaves the last state
 * on screen — the next navigation renders the door, which is where the operator
 * has to go anyway.
 */
const POLL_MS = 15_000;

export function LockChip({ initial }: { initial: OpsLock | null }) {
  const [lock, setLock] = useState<OpsLock | null>(initial);

  useEffect(() => {
    let live = true;
    const read = () => {
      getOpsLock()
        .then((next) => {
          if (live) setLock(next);
        })
        .catch(() => {
          /* An expired session or an unreachable service leaves the last known
             state on screen; the tab itself is what reports the expiry. */
        });
    };
    const timer = window.setInterval(read, POLL_MS);
    return () => {
      live = false;
      window.clearInterval(timer);
    };
  }, []);

  if (!lock) return null;

  const tone =
    lock.state === "held" ? styles.chipHeld : lock.state === "unknown" ? styles.chipUnknown : "";

  return (
    <span className={`${styles.chip} ${tone}`.trim()} title={lock.key}>
      <span>{lock.key}</span>
      <span>{lock.state}</span>
      {lock.reason && <span className={styles.faint}>{lock.reason}</span>}
      {lock.since && (
        <>
          <span className={styles.faint}>{LOCK_HELD_SINCE_KO}</span>
          <Stamp instant={lock.since} seconds suffix={false} />
        </>
      )}
    </span>
  );
}
