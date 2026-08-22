"use client";

import { useState, type ReactNode } from "react";
import { CraftPanel } from "@/components";
import { count, kstStamp } from "@/lib/format";
import {
  RIGHTS_LABEL_COMPACT_KO,
  RIGHTS_LABEL_KO,
  type RightsType,
} from "@/lib/copy";
import type { BoardResponse, BoardRow as Row, Freshness } from "@/lib/types";
import { BoardRow } from "./BoardRow";
import {
  BOARD_TITLE_KO,
  EXPAND_KO,
  FRESHNESS_PREFIX_KO,
  FRESHNESS_TZ_KO,
  STALE_NOTICE_KO,
  TAB_ALL_KO,
  openNowSentence,
  staleSuffixKo,
  tbdSentence,
} from "./copy";
import styles from "./Board.module.css";

/**
 * The board — 소멸 카운트다운 (R2 §Board, plus R3's 추후결정 strip).
 *
 * Craft panel: header (title + freshness chip) → the stale notice when there is
 * one → tabs → rows → the two pinned strips. Three rules the round states as
 * prohibitions and this component keeps structurally:
 *
 * - **Content never dims on staleness.** The chip flips to the alert treatment
 *   and an inset notice appears above the tabs; the rows are untouched. A board
 *   that hides itself when the corpus is old is the "dark" half of
 *   *stale-never-dark*.
 * - **`stale` and `N시간 전` are served** (`freshness.stale` / `age_hours`), so
 *   no client measures the corpus against its own clock (`P5.S3` decision 2).
 * - **A past ② is 진행 중, never 종료** (`ui-traps.md` #5) — those rows are not in
 *   the ranked list at all; they are the pinned `open_now` strip, whose signed
 *   sentence says the window is open right now.
 *
 * ## Why the tabs filter in the browser
 *
 * `GET /board?rights=` exists and does exactly this, but the whole board is one
 * request (`P5.S3` note 11: 160 KB in ~54 ms, and the design paginates nothing),
 * and `counts` is **always whole-board** either way. Filtering the served list
 * reproduces the endpoint's own `keep()` — same predicate, same order — while a
 * tab click costs no request and cannot show a different corpus in two tabs.
 * `counts` stays the tab numbers, so 전체 reads 488 even though 450 rows are on
 * the page: the 38 past ①/③ belong to 조회 and the retrospective, not here.
 */
export function Board({ board }: { board: BoardResponse }) {
  const [tab, setTab] = useState<RightsType | null>(null);

  const keep = (rows: Row[]) => (tab ? rows.filter((row) => row.rights_type === tab) : rows);
  const rows = keep(board.rows);
  const openNow = keep(board.open_now.rows);
  const tbd = keep(board.tbd.rows);

  return (
    <CraftPanel as="section" className={styles.board}>
      <header className={styles.header}>
        <h2 className={styles.title}>{BOARD_TITLE_KO}</h2>
        <FreshnessChip freshness={board.freshness} />
      </header>

      {board.freshness.stale ? <p className={styles.notice}>{STALE_NOTICE_KO}</p> : null}

      <div className={styles.tabs}>
        {/* 전체 is the same word in both label sets — R2's mobile strip reads
            전체/유증/CB/매수청구 — so it carries its own compact form too. */}
        <Tab
          active={tab === null}
          onSelect={() => setTab(null)}
          count={board.counts.all}
          compact={TAB_ALL_KO}
        >
          {TAB_ALL_KO}
        </Tab>
        {(["R1", "R2", "R3"] as const).map((type) => (
          <Tab
            key={type}
            active={tab === type}
            onSelect={() => setTab(type)}
            count={board.counts[type]}
            compact={RIGHTS_LABEL_COMPACT_KO[type]}
          >
            {RIGHTS_LABEL_KO[type]}
          </Tab>
        ))}
      </div>

      <ol className={styles.rows}>
        {rows.map((row) => (
          <BoardRow key={row.event_id} row={row} />
        ))}
      </ol>

      {/* ② 전환청구 진행 중 — the signed sentence with the live count. */}
      <Strip rows={openNow}>
        {openNowSentence.before}
        <span className={styles.live}>{openNowSentence.emphasis}</span>
        {openNowSentence.middle}
        <span className={`mono ${styles.stripCount}`}>{count(openNow.length)}건</span>
      </Strip>

      {/* R3 §추후결정 board strip — below the ② strip, same pattern, not ranked. */}
      <Strip rows={tbd}>
        {tbdSentence.before}
        <span className={`mono ${styles.stripCount}`}>{count(tbd.length)}건</span>
      </Strip>
    </CraftPanel>
  );
}

/**
 * The freshness chip: mono 11 `기준 YYYY-MM-DD HH:MM KST`, and when the corpus is
 * stale, the alert treatment plus `· N시간 전 데이터`.
 *
 * With no 기준시각 at all there is no chip — the freshness object counts an
 * unknown `as_of` as stale, and the notice above the tabs says so; a chip with a
 * dash in it would be the placeholder the system forbids.
 */
function FreshnessChip({ freshness }: { freshness: Freshness }) {
  if (!freshness.as_of) return null;
  const stamp = kstStamp(freshness.as_of);
  const classes = [styles.freshness, freshness.stale ? styles.stale : null]
    .filter(Boolean)
    .join(" ");

  return (
    <span className={classes}>
      {FRESHNESS_PREFIX_KO} {stamp.date} {stamp.time} {FRESHNESS_TZ_KO}
      {freshness.stale && freshness.age_hours !== undefined
        ? ` ${staleSuffixKo(freshness.age_hours)}`
        : null}
    </span>
  );
}

function Tab({
  active,
  count: total,
  compact,
  onSelect,
  children,
}: {
  active: boolean;
  count?: number;
  /** The mobile label (유증 / CB / 매수청구) — R1's compact strings, reused by R2. */
  compact?: string;
  onSelect: () => void;
  children: ReactNode;
}) {
  return (
    <button
      type="button"
      className={active ? `${styles.tab} ${styles.tabActive}` : styles.tab}
      aria-pressed={active}
      onClick={onSelect}
    >
      <span className={styles.tabFull}>{children}</span>
      {compact ? <span className={styles.tabCompact}>{compact}</span> : null}
      {total !== undefined ? (
        <span className={`mono ${styles.tabCount}`}>{count(total)}</span>
      ) : null}
    </button>
  );
}

/**
 * A pinned strip under the rows (`--surface-raised`, hairline top): the signed
 * sentence, the 펼치기 disclosure, and the same row anatomy when it is open.
 *
 * The button keeps its signed label while the strip is open and states its state
 * through `aria-expanded` — a 접기 label is copy nobody signed, the same decision
 * the chrome's 메뉴 button records.
 *
 * A tab with none of these rows has no strip: the count would be 0건, which is a
 * sentence about nothing.
 */
function Strip({ rows, children }: { rows: Row[]; children: ReactNode }) {
  const [open, setOpen] = useState(false);
  if (rows.length === 0) return null;

  return (
    <div className={styles.strip}>
      <p className={styles.stripLine}>
        <span>{children}</span>
        <button
          type="button"
          className={styles.expand}
          aria-expanded={open}
          onClick={() => setOpen((value) => !value)}
        >
          {EXPAND_KO}
        </button>
      </p>
      {open ? (
        <ol className={styles.rows}>
          {rows.map((row) => (
            <BoardRow key={row.event_id} row={row} />
          ))}
        </ol>
      ) : null}
    </div>
  );
}
