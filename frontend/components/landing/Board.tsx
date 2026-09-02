"use client";

import { useCallback, useEffect, useRef, useState, type ReactNode } from "react";
import { CraftPanel } from "@/components";
import { getBoard } from "@/lib/api";
import { count, kstStamp } from "@/lib/format";
import {
  RIGHTS_LABEL_COMPACT_KO,
  RIGHTS_LABEL_KO,
  type RightsType,
} from "@/lib/copy";
import type { Freshness, LandingBoard, LandingRow as Row } from "@/lib/types";
import { BoardRow, type RowChange } from "./BoardRow";
import {
  BOARD_TITLE_KO,
  COLLAPSE_KO,
  EXPAND_KO,
  FRESHNESS_PREFIX_KO,
  FRESHNESS_TZ_KO,
  REFRESHED_KO,
  STALE_NOTICE_KO,
  TAB_ALL_KO,
  collapseToFirstKo,
  moreKo,
  openNowSentence,
  remainingKo,
  staleSuffixKo,
  tbdSentence,
} from "./copy";
import styles from "./Board.module.css";

/**
 * How many ranked rows the board shows before the first 더 보기, and how many
 * each click adds.
 *
 * **The operator set it at the R9 gate — "q3: 15"** — which closes P7 Q3 (the
 * board window was that phase's own override at 30, and R9's build-prompt §1
 * supersedes it: "`WINDOW_STEP = 30` → **`15`**"). Fifteen rows ≈ 600px, so the
 * two pinned strips stay on the first screen instead of being pushed off it.
 *
 * It is a **display limit and never a filter**: the served list, its ranking and
 * the tab `counts` are untouched, a tab switch starts a new list at the first
 * window — and a refresh does **not** reset it (§7).
 */
const WINDOW_STEP = 15;

/**
 * How often the open page re-reads the board (R9 §7).
 *
 * The round drew the *visible* contract and left the number to this slice with a
 * stated assumption of **60 s** (P8 Operator Question Q10, unchallenged): the
 * 기준시각 this refresh exists to move is minute-granular, so a shorter period
 * would spend requests on a screen that cannot change. Nothing else in the file
 * depends on the value — the visible rules are the same at any period.
 */
const REFRESH_INTERVAL_MS = 60_000;

/**
 * The board — 소멸 카운트다운 (R2 §Board + R3's 추후결정 strip, re-cut by R9).
 *
 * Craft panel: header (title + freshness chip, and the 갱신됨 badge beside it) →
 * the stale notice when there is one → tabs → rows → the window footer → the two
 * pinned strips. Three rules the rounds state as prohibitions and this component
 * keeps structurally:
 *
 * - **Content never dims on staleness.** The chip flips to the alert treatment
 *   and an inset notice appears above the tabs; the rows are untouched. Same on
 *   a refresh whose result is stale — R2's handling, unchanged (§7).
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
 * and `counts` counts the same population either way. Filtering the served list
 * reproduces the endpoint's own `keep()` — same predicate, same order — while a
 * tab click costs no request and cannot show a different corpus in two tabs.
 * That is also what makes the refresh cheap: one request replaces every tab.
 *
 * ## What a tab's number counts
 *
 * Every event the board can **show** — the ranked list plus the two pinned
 * strips — and nothing else, which is `board_bucket`'s definition on the server
 * (전체 450: 386 ranked + 60 진행 중 + 4 추후결정). It used to count every
 * exposable event, past ones included, and read 488 over a list that could never
 * reach it. The R9 meta line and its D-day legend explained that gap in words;
 * the operator removed both once the number stopped needing an explanation, and
 * the window footer still separates what a click adds (「15건 더 보기」) from what
 * is left (「남은 371건」).
 *
 * ## The extras column is a panel-level decision (R9 §2)
 *
 * Whether the ① `청약 …` + `발행가 확정 전` column exists is decided for the whole
 * panel — the tab's ranked rows **and** both strips — and never per row: a row is
 * its own grid container, so a content-sized column would resolve differently row
 * by row, which is walk finding 5's misalignment. `data-extras="none"` swaps the
 * template and removes the cell; `"yes"` keeps it, empty where a ②/③ row has
 * nothing to put in it.
 *
 * ## The refresh (R9 §7)
 *
 * The page re-reads `GET /board` while it is open. **There is no button, no
 * spinner and no 새로고침 text**: the whole visible surface is the 기준시각 chip
 * (a new stamp + 갱신됨 beside it) and a `--live` edge on the rows whose values
 * moved. An unchanged 기준시각 changes nothing on screen; a failed read says
 * nothing at all and retries on the next tick — a 기준시각 growing old is already
 * that sentence. The reader's own state — tab, window, expanded strips, scroll,
 * focus — is not data and survives. `page.tsx` keeps its server fetch as the
 * first render, so the hero and the countdown never remount.
 */
export function Board({ board: initial }: { board: LandingBoard }) {
  const [board, setBoard] = useState(initial);
  const [tab, setTab] = useState<RightsType | null>(null);
  const [shown, setShown] = useState(WINDOW_STEP);
  /** Set on a refresh that brought a new 기준시각; replaced by the next one. */
  const [refreshed, setRefreshed] = useState(false);
  /** `event_id` → which of that row's values the last refresh replaced. */
  const [changed, setChanged] = useState<ReadonlyMap<number, RowChange>>(EMPTY);

  const boardRef = useRef(initial);
  const tabRef = useRef<RightsType | null>(null);
  const shownRef = useRef(WINDOW_STEP);
  /** The list a vanished focused row belonged to, and that row's id. */
  const orphan = useRef<{ list: HTMLElement; id: string } | null>(null);

  boardRef.current = board;
  tabRef.current = tab;
  shownRef.current = shown;

  /** A tab is a new list, so it starts at the first window. */
  const selectTab = (next: RightsType | null) => {
    setTab(next);
    setShown(WINDOW_STEP);
  };

  const apply = useCallback((next: LandingBoard) => {
    const previous = boardRef.current;
    // 기준시각 unchanged → the corpus has not moved, so nothing on the screen
    // may move either. Not even a flicker: a 0.2s blink is not information.
    if (next.freshness.as_of === previous.freshness.as_of) return;

    const active = document.activeElement;
    const row = active instanceof HTMLElement ? active.closest<HTMLElement>("li[data-event-id]") : null;
    const list = row?.parentElement;
    orphan.current =
      row?.dataset.eventId && list instanceof HTMLElement
        ? { list, id: row.dataset.eventId }
        : null;

    const ranked = keep(next.rows, tabRef.current);
    setChanged(diff(previous, next, tabRef.current, shownRef.current));
    setBoard(next);
    setRefreshed(true);
    // The window is a count, so it carries over — trimmed to the new list when
    // that list got shorter, never below the first window.
    setShown((value) => Math.max(WINDOW_STEP, Math.min(value, ranked.length)));
  }, []);

  useEffect(() => {
    let alive = true;

    const read = async () => {
      // A hidden tab reads nothing: a 30-minute-old 기준시각 on a tab nobody is
      // looking at is more honest than a screen kept quietly warm.
      if (document.hidden) return;
      try {
        const next = await getBoard();
        if (alive) apply(next);
      } catch {
        // The failure has no surface (§7). The stamp ageing is the message, and
        // the next tick retries.
      }
    };

    const timer = setInterval(() => void read(), REFRESH_INTERVAL_MS);
    const onVisibility = () => {
      if (!document.hidden) void read();
    };
    document.addEventListener("visibilitychange", onVisibility);

    return () => {
      alive = false;
      clearInterval(timer);
      document.removeEventListener("visibilitychange", onVisibility);
    };
  }, [apply]);

  // Rows are keyed by `event_id`, so a refresh replaces values in place and the
  // focus ring stays where the reader put it. The one case that needs help is a
  // focused row that no longer exists: focus falls to the document, so it is
  // moved to the list the row was in.
  useEffect(() => {
    const lost = orphan.current;
    orphan.current = null;
    if (!lost) return;
    if (lost.list.querySelector(`[data-event-id="${lost.id}"]`)) return;
    if (!lost.list.isConnected) return;
    lost.list.focus();
  }, [board]);

  const rows = keep(board.rows, tab);
  const openNow = keep(board.open_now.rows, tab);
  const tbd = keep(board.tbd.rows, tab);
  const hidden = Math.max(rows.length - shown, 0);
  // One column plan per panel — the ranked list and both strips together.
  const extras = hasExtras(rows) || hasExtras(openNow) || hasExtras(tbd) ? "yes" : "none";

  return (
    <CraftPanel as="section" className={styles.board}>
      <header className={styles.header}>
        <h2 className={styles.title}>{BOARD_TITLE_KO}</h2>
        <span className={styles.fresh}>
          <FreshnessChip freshness={board.freshness} />
          {refreshed ? <span className={styles.updated}>{REFRESHED_KO}</span> : null}
        </span>
      </header>

      {board.freshness.stale ? <p className={styles.notice}>{STALE_NOTICE_KO}</p> : null}

      <div className={styles.tabs}>
        {/* 전체 is the same word in both label sets — R2's mobile strip reads
            전체/유증/CB/매수청구 — so it carries its own compact form too. */}
        <Tab
          active={tab === null}
          onSelect={() => selectTab(null)}
          count={board.counts.all}
          compact={TAB_ALL_KO}
        >
          {TAB_ALL_KO}
        </Tab>
        {(["R1", "R2", "R3"] as const).map((type) => (
          <Tab
            key={type}
            active={tab === type}
            onSelect={() => selectTab(type)}
            count={board.counts[type]}
            compact={RIGHTS_LABEL_COMPACT_KO[type]}
          >
            {RIGHTS_LABEL_KO[type]}
          </Tab>
        ))}
      </div>

      <ol className={styles.rows} data-extras={extras} tabIndex={-1}>
        {rows.slice(0, shown).map((row) => (
          <BoardRow key={row.event_id} row={row} changed={changed.get(row.event_id)} />
        ))}
      </ol>

      {/* The window's three controls (R9 §4): what a click adds, what is left,
          and the way back to the first window. Nothing left and nothing expanded
          → no footer at all. */}
      {hidden > 0 || shown > WINDOW_STEP ? (
        <p className={styles.more}>
          {hidden > 0 ? (
            <>
              <button
                type="button"
                className={styles.btn}
                onClick={() => setShown((value) => value + WINDOW_STEP)}
              >
                {moreKo(count(WINDOW_STEP))}
              </button>
              <span className={styles.rest}>{remainingKo(count(hidden))}</span>
            </>
          ) : null}
          {shown > WINDOW_STEP ? (
            <button type="button" className={styles.flat} onClick={() => setShown(WINDOW_STEP)}>
              {collapseToFirstKo(count(WINDOW_STEP))}
            </button>
          ) : null}
        </p>
      ) : null}

      {/* ② 전환청구 진행 중 — the signed sentence with the live count. */}
      <Strip rows={openNow} extras={extras} changed={changed}>
        {openNowSentence.before}
        <span className={styles.live}>{openNowSentence.emphasis}</span>
        {openNowSentence.middle}
        <span className={`mono ${styles.stripCount}`}>{count(openNow.length)}건</span>
      </Strip>

      {/* R3 §추후결정 board strip — below the ② strip, same pattern, not ranked. */}
      <Strip rows={tbd} extras={extras} changed={changed}>
        {tbdSentence.before}
        <span className={`mono ${styles.stripCount}`}>{count(tbd.length)}건</span>
      </Strip>
    </CraftPanel>
  );
}

const EMPTY: ReadonlyMap<number, RowChange> = new Map();

const keep = (rows: Row[], tab: RightsType | null) =>
  tab ? rows.filter((row) => row.rights_type === tab) : rows;

/** ①'s extras cell is the only one with content; ②/③ carry no `offering`. */
const hasExtras = (rows: Row[]) => rows.some((row) => Boolean(row.offering));

const extrasKey = (row: Row) =>
  row.offering
    ? `${row.offering.price_confirmed}|${row.offering.subscription_start ?? ""}|${row.offering.subscription_end ?? ""}`
    : "";

/**
 * Which rows a refresh changed (R9 §7).
 *
 * A row is marked when one of the three values the row prints moved — the key
 * date, the extras, the D-day — or when it is **new to the shown window**. The
 * mark carries the `--live` edge for one cycle; the per-value flags carry the
 * fade, so only what actually changed fades in. A row that appeared in the
 * corpus for the first time has all three: everything about it is new.
 *
 * Rows that left are not marked at all: an event that fell out of the gate is
 * not an animation.
 */
function diff(
  previous: LandingBoard,
  next: LandingBoard,
  tab: RightsType | null,
  shown: number,
): ReadonlyMap<number, RowChange> {
  const before = new Map<number, Row>();
  for (const row of [...previous.rows, ...previous.open_now.rows, ...previous.tbd.rows]) {
    before.set(row.event_id, row);
  }
  const window = new Set(
    keep(previous.rows, tab)
      .slice(0, shown)
      .map((row) => row.event_id),
  );

  const changes = new Map<number, RowChange>();
  const mark = (rows: Row[], newToWindow: boolean) => {
    for (const row of rows) {
      const old = before.get(row.event_id);
      if (!old) {
        changes.set(row.event_id, { when: true, extras: true, dday: true });
        continue;
      }
      const change: RowChange = {
        when: old.countdown.date !== row.countdown.date || old.countdown.label_ko !== row.countdown.label_ko,
        extras: extrasKey(old) !== extrasKey(row),
        dday: old.countdown.dday !== row.countdown.dday,
      };
      if (change.when || change.extras || change.dday) changes.set(row.event_id, change);
      else if (newToWindow && !window.has(row.event_id)) {
        // It did not change; it moved into view. The edge says so, and nothing
        // fades — there is no new value to fade in.
        changes.set(row.event_id, { when: false, extras: false, dday: false });
      }
    }
  };

  mark(keep(next.rows, tab).slice(0, shown), true);
  mark(next.open_now.rows, false);
  mark(next.tbd.rows, false);
  return changes;
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
 * A pinned strip under the rows (`--surface-raised`, hairline top, bled to the
 * panel's edge): the signed sentence, its disclosure, and the board's own row
 * anatomy when it is open.
 *
 * **R9 §5 gave the toggle its second label**: 펼치기 ↔ 접기, with `aria-expanded`
 * agreeing with it rather than standing in for it (walk finding 4 — the button
 * never changed, and a tab switch was the only way back). The expanded rows sit
 * on the board's grid at the same 24px start line, so the two tables read as one
 * (walk finding 5), and they take the **panel's** column plan, not their own.
 *
 * A tab with none of these rows has no strip: the count would be 0건, which is a
 * sentence about nothing.
 */
function Strip({
  rows,
  extras,
  changed,
  children,
}: {
  rows: Row[];
  extras: "yes" | "none";
  changed: ReadonlyMap<number, RowChange>;
  children: ReactNode;
}) {
  const [open, setOpen] = useState(false);
  if (rows.length === 0) return null;

  return (
    <div className={styles.strip}>
      <p className={styles.stripLine}>
        <span>{children}</span>
        <button
          type="button"
          className={styles.btn}
          aria-expanded={open}
          onClick={() => setOpen((value) => !value)}
        >
          {open ? COLLAPSE_KO : EXPAND_KO}
        </button>
      </p>
      {open ? (
        <div className={styles.sbody}>
          <ol className={styles.rows} data-extras={extras} tabIndex={-1}>
            {rows.map((row) => (
              <BoardRow key={row.event_id} row={row} changed={changed.get(row.event_id)} />
            ))}
          </ol>
        </div>
      ) : null}
    </div>
  );
}
