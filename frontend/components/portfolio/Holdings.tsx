"use client";

import { useEffect, useState } from "react";
import { DDay, RightsChip, StateBadge } from "@/components";
import { count } from "@/lib/format";
import { parseShares } from "@/lib/holding";
import type { PortfolioHolding } from "@/lib/types";
import { SharesInput } from "./SharesInput";
import {
  CANCEL_KO,
  COL_SHARES_KO,
  COL_STOCK_KO,
  DELETE_KO,
  EDIT_KO,
  RIGHTS_SECTION_KO,
  SAVE_KO,
  SHARES_UNIT_KO,
  UNDO_KO,
} from "./copy";
import styles from "./Portfolio.module.css";

/**
 * 보유 종목 — the rows R5 §Portfolio draws, and the two interactions it signs.
 *
 * > 행: 종목 / 보유량(인라인 편집: input — 확정은 우측 액션 열이 수정·삭제 →
 * > 저장·취소로 교체, **가로 배치**) / 진행 중인 권리 요약(RightsChip + governing
 * > label + `D-n · date`) / 수정·삭제. **삭제 = 즉시 + 8초 되돌리기, 모달 없음.**
 *
 * ## The row edit (개정 ④)
 *
 * Confirming is a *column swap*, not a dialog: 수정·삭제 becomes 저장·취소 in the
 * same horizontal action column, and the 보유량 cell becomes R4's own input
 * (`SharesInput`). Nothing overlays the page — R5's hard rule for this whole
 * layer is "게이트 화면·강제 모달 금지", and the round removes the page 대제목 for
 * the same reason: the surface stays one plain list.
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
 * deadline (`P5.S8`'s `_rights_summary`). A holding with no live rights states
 * nothing at all — R5 signs no empty-cell sentence, and an invented one would be
 * copy.
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
  /** 샘플 모드 keeps no caption — see `SharesInput`. */
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
    <ul className={styles.holdings}>
      <li className={styles.holdingHead} aria-hidden>
        <span>{COL_STOCK_KO}</span>
        <span>{COL_SHARES_KO}</span>
        <span>{RIGHTS_SECTION_KO}</span>
        <span />
      </li>

      {rows.map((row) => {
        const open = editing === row.corp_code;
        const next = row.rights.next;

        return (
          <li key={row.corp_code} className={styles.holdingRow}>
            <div className={styles.holdingStock}>
              <p className={styles.holdingName}>{row.corp_name ?? row.corp_code}</p>
              {row.stock_code ? (
                <p className={`mono ${styles.holdingMeta}`}>{row.stock_code}</p>
              ) : null}
            </div>

            <div className={styles.holdingShares}>
              {open ? (
                <SharesInput
                  id={`shares-${row.corp_code}`}
                  digits={digits}
                  caption={captionKo}
                  autoFocus
                  disabled={busy}
                  onChange={setDigits}
                  onSubmit={() => save(row)}
                />
              ) : (
                <p className={styles.sharesValue}>
                  <span className="mono">{count(row.shares)}</span>
                  {SHARES_UNIT_KO}
                </p>
              )}
            </div>

            <div className={styles.holdingRights}>
              {next ? (
                <>
                  <RightsChip rightsType={next.rights_type} compact />
                  <span className={styles.rightsLabel}>{next.countdown.label_ko}</span>
                  {next.countdown.dday !== null && next.countdown.days !== null ? (
                    <DDay
                      dday={next.countdown.dday}
                      days={next.countdown.days}
                      date={next.countdown.date}
                    />
                  ) : (
                    // 추후결정 means *no date* — never a dash, never the date it
                    // replaced (`ui-traps` #4).
                    <StateBadge kind="tbd" />
                  )}
                </>
              ) : null}
            </div>

            {/* The action column — horizontal, and the only thing that changes on
                a confirm (개정 ④). */}
            <div className={styles.actions}>
              {open ? (
                <>
                  <button
                    type="button"
                    className={styles.action}
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
  );
}
