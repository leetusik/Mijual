"use client";

import { useEffect, useState } from "react";
import { CraftPanel, DDay, RightsChip, StateBadge } from "@/components";
import { count } from "@/lib/format";
import { parseShares } from "@/lib/holding";
import type { PortfolioHolding } from "@/lib/types";
import {
  CANCEL_KO,
  COL_SHARES_KO,
  COL_STOCK_KO,
  DELETE_KO,
  EDIT_KO,
  HOLDING_LABEL_KO,
  RIGHTS_SECTION_KO,
  SAVE_KO,
  SHARES_UNIT_KO,
  UNDO_KO,
} from "./copy";
import styles from "./Portfolio.module.css";

/**
 * 보유 종목 — the rows R5 §Portfolio draws, at **R13 §2**'s geometry.
 *
 * > 행: 종목 / 보유량(인라인 편집: input — 확정은 우측 액션 열이 수정·삭제 →
 * > 저장·취소로 교체, **가로 배치**) / 진행 중인 권리 요약(RightsChip + governing
 * > label + `D-n · date`) / 수정·삭제. **삭제 = 즉시 + 8초 되돌리기, 모달 없음.**
 *
 * ## R13: content-independent tracks, twice
 *
 * The list is a real table with headers — R5 enumerates the row's four cells and
 * the reader compares 보유량 down the column — so the tracks are
 * `minmax(0,1.15fr) 132px minmax(0,1.5fr) 152px` and **nothing in a row can move
 * one**: the action column has one left edge on every row, and the header labels
 * sit over the cells they name (P7.S8 measured them 18.7px / 32.1px off when the
 * head and the rows were two grids sharing an `auto` track).
 *
 * The 진행 중인 권리 cell has its own three tracks (`52px minmax(0,1fr) auto`) for
 * the same reason one level down: 유증 / CB / 매수청구 are three different chip
 * widths, and without a track the governing label started at three different x
 * and the countdown ended at three different right edges.
 *
 * ## finding 2 — an empty 진행 중인 권리 cell is a dashed hairline
 *
 * Two of the four rows hold nothing but past rights. R5 signs no empty-cell
 * sentence, and the walk's question was what the *cell* is, not what Korean to
 * mint: it is R10/R11's **dashed rule** (`.rightsSlot`, 56px, `aria-hidden`) —
 * this system's own mark for 「이 자리에 값이 없다」. Never a sentence, never a
 * dashed *box* (a dashed box with a label in it is this product's control
 * grammar, `.prompt` / `.restore`), never a `—` and never 「0건」.
 *
 * ## The row edit (개정 ④, R13 §2)
 *
 * Confirming is a *column swap*, not a dialog: 수정·삭제 becomes 저장·취소 in the
 * same horizontal action column, and the 보유량 cell — only that cell — becomes an
 * input. R13 draws the inline field as the cell's own 36px right-aligned mono box
 * (`.holdingInput`), not R4's full 보유량 primitive: the label, the 주 suffix and
 * the preset chips belong to the 종목 추가 panel, where the reader is stating a
 * count for the first time. The behaviour is R4's unchanged — digits only,
 * comma-grouped on display (`lib/holding.ts`'s `parseShares` reads them back),
 * Enter confirms — and the label survives as the field's `aria-label`, so nothing
 * is lost to a reader who cannot see the column header.
 *
 * ## 삭제 = 즉시 + 8초 되돌리기
 *
 * The delete is real the moment it is pressed (`DELETE /portfolio/holdings/{id}`
 * — there is no soft-delete column and `P5.S8` deliberately built none), and the
 * 되돌리기 window is the client's: the row's issuer and count are held in memory
 * for the round's own 8 seconds and 되돌리기 re-adds them through the ordinary
 * `POST`. Two consequences worth knowing rather than discovering: the restored
 * row is a **new** holding (its `created_at` puts it last in the list, which is
 * the order `P5.S8` serves), and a 챙긴 돈 mark is untouched either way because it
 * is keyed on the 실적보고서, not on the holding (`P5.S8` note 7).
 *
 * The 진행 중인 권리 summary is the server's: `holding.rights.next` reuses the
 * **already-serialized** countdown of the row the D-day section shows, so the
 * chip here and the row below it cannot say two different things about one
 * deadline (`P5.S8`'s `_rights_summary`).
 */
export function Holdings({
  rows,
  busy,
  captionKo,
  editing,
  onEditing,
  undo,
  onSave,
  onDelete,
  onUndo,
}: {
  rows: PortfolioHolding[];
  busy: boolean;
  /** 샘플 모드 keeps no caption — the sentence names the **account** as where the
   * count lives, which is not true of a sample (R5-4), and no second caption is
   * signed for that case. */
  captionKo: string | null;
  /** The row currently in 수정, by `corp_code`. It is lifted so a repeat 담기 can
   * open the existing row instead of needing an "이미 담긴 종목" line R5 never
   * wrote (`P5.S8` note 3). */
  editing: string | null;
  onEditing: (corpCode: string | null) => void;
  undo: { corp_code: string; corp_name?: string | null; shares: number } | null;
  onSave: (row: PortfolioHolding, shares: number) => void;
  onDelete: (row: PortfolioHolding) => void;
  onUndo: () => void;
}) {
  const [digits, setDigits] = useState("");

  // The field starts at the row's current count — whoever opened the row, the
  // reader or a repeat 담기 from the panel below.
  useEffect(() => {
    const row = rows.find((entry) => entry.corp_code === editing);
    if (row) setDigits(String(row.shares));
  }, [editing, rows]);

  const save = (row: PortfolioHolding) => {
    const shares = parseShares(digits);
    // An empty or unparseable field is not a zero and not a deletion: the round
    // gives 삭제 its own control, so a confirm with nothing in the field simply
    // keeps the row as it was.
    if (shares !== null && shares !== row.shares) onSave(row, shares);
    onEditing(null);
  };

  return (
    <CraftPanel>
      <ul className={styles.holdings}>
        <li className={`${styles.holdingRow} ${styles.holdingHead}`} aria-hidden>
          <span>{COL_STOCK_KO}</span>
          <span>{COL_SHARES_KO}</span>
          <span>{RIGHTS_SECTION_KO}</span>
          <span />
        </li>

        {rows.map((row) => {
          const open = editing === row.corp_code;
          const next = row.rights.next;

          return (
            // `data-corp` is the pre-hydration mirror's hook, not a style hook
            // (`P12.F10`): in 샘플 모드 the server renders every served row and
            // only the browser knows which issuers it removed, so a generated
            // rule keyed on this attribute hides such a row before it paints and
            // React's own filter then unmounts an element that had no box. It
            // costs one attribute per row and does nothing in 계정 모드, where no
            // rule is emitted at all.
            <li key={row.corp_code} className={styles.holdingRow} data-corp={row.corp_code}>
              <div className={styles.holdingStock}>
                <p className={styles.holdingName}>{row.corp_name ?? row.corp_code}</p>
                {/* 종목코드, at the canon's `.phmeta` tier. The R13 cards omit it
                    because the design walk's payload did not carry one (Q46 = a);
                    a served value is not an absent one. */}
                {row.stock_code ? (
                  <p className={`mono ${styles.holdingMeta}`}>{row.stock_code}</p>
                ) : null}
              </div>

              {open ? (
                <div className={styles.holdingEdit}>
                  <input
                    id={`shares-${row.corp_code}`}
                    className={styles.holdingInput}
                    type="text"
                    inputMode="numeric"
                    autoComplete="off"
                    aria-label={HOLDING_LABEL_KO}
                    autoFocus
                    disabled={busy}
                    value={digits === "" ? "" : count(digits)}
                    onChange={(event) => setDigits(event.target.value.replace(/[^\d]/g, ""))}
                    onKeyDown={(event) => {
                      if (event.key === "Enter") {
                        event.preventDefault();
                        save(row);
                      }
                    }}
                  />
                  {captionKo ? <span className={styles.caption}>{captionKo}</span> : null}
                </div>
              ) : (
                <p className={styles.sharesValue}>
                  <span className="mono">{count(row.shares)}</span>
                  <span className={styles.sharesUnit}>{SHARES_UNIT_KO}</span>
                </p>
              )}

              <div className={styles.holdingRights}>
                {next ? (
                  <>
                    <RightsChip rightsType={next.rights_type} compact />
                    <span className={styles.rightsLabel}>{next.countdown.label_ko}</span>
                    <span className={styles.holdingDDay}>
                      {next.countdown.dday !== null && next.countdown.days !== null ? (
                        <DDay
                          dday={next.countdown.dday}
                          days={next.countdown.days}
                          date={next.countdown.date}
                        />
                      ) : (
                        // 추후결정 means *no date* — never a dash, never the date
                        // it replaced (`ui-traps` #4).
                        <StateBadge kind="tbd" />
                      )}
                    </span>
                  </>
                ) : (
                  <span className={styles.rightsSlot} aria-hidden />
                )}
              </div>

              {/* The action column — horizontal, and the only thing that changes
                  on a confirm (개정 ④). */}
              <div className={styles.actions}>
                {open ? (
                  <>
                    <button
                      type="button"
                      className={`${styles.action} ${styles.actionPrimary}`}
                      disabled={busy}
                      onClick={() => save(row)}
                    >
                      {SAVE_KO}
                    </button>
                    <button
                      type="button"
                      className={styles.action}
                      onClick={() => onEditing(null)}
                    >
                      {CANCEL_KO}
                    </button>
                  </>
                ) : (
                  <>
                    <button
                      type="button"
                      className={styles.action}
                      disabled={busy}
                      onClick={() => onEditing(row.corp_code)}
                    >
                      {EDIT_KO}
                    </button>
                    <button
                      type="button"
                      className={styles.action}
                      disabled={busy}
                      onClick={() => onDelete(row)}
                    >
                      {DELETE_KO}
                    </button>
                  </>
                )}
              </div>
            </li>
          );
        })}

        {/* 8초 되돌리기 — an inset row where the deleted one was, never a toast and
            never a modal. It disappears on its own when the window closes. */}
        {undo ? (
          <li className={styles.undoRow}>
            <span className={styles.undoName}>
              {undo.corp_name ?? undo.corp_code}{" "}
              <span className="mono">{count(undo.shares)}</span>
              {SHARES_UNIT_KO}
            </span>
            <button type="button" className={styles.action} disabled={busy} onClick={onUndo}>
              {UNDO_KO}
            </button>
          </li>
        ) : null}
      </ul>
    </CraftPanel>
  );
}
