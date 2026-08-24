"use client";

import { useState } from "react";
import estimate from "@/components/EstimateMarker.module.css";
import type { AskChip, AskDataRow } from "@/lib/ask";
import { DATA_HEADING, FOLD, SHOW_ALL, TAG_INPUT } from "./copy";
import { InlineCitation } from "./InlineCitation";
import styles from "./Blocks.module.css";

/** 「`rows.length > 6` → 6행 + `모두 보기 (N)` / `접기`」 (§2.3). */
const CAP = 6;

/**
 * One 라벨/값 row — §2.3's three columns, and §2.4 reuses **this component** for a
 * 계산 블록's inputs (「DataRow와 같은 행 스키마·같은 CSS」).
 *
 * > 행: **세 칸** `grid-template-columns: minmax(0,40%) minmax(0,1fr) auto`
 * > (≤767: 36%) … 라벨 = sans `--text-sm` ink-2 `word-break:keep-all`. 값 = mono
 * > `--text-sm` tabular-nums ink-1, **`nowrap` + 값 칸만 가로 스크롤**. 셋째
 * > 칸(고정, `nowrap`): `reader_input`이면 「입력」 마커(ink-3), `citation`이 있으면
 * > 인용 칩 (프로즈의 칩과 **같은 컴포넌트**). **칩은 값과 함께 스크롤되지
 * > 않는다** — 390에서 긴 값이 있을 때 칩이 화면 밖으로 밀리면 근거가 사라진 것과
 * > 같다.
 *
 * The value is the **server's** string and is never formatted here (`AskDataRow`:
 * 「the surface never formats a number」), and the chip's number comes from the one
 * numbering the prose uses — 같은 근거 = 같은 번호 (R6-4), which is also why a
 * data-row chip counts in the footer's 근거 N건 (`P9.S3` note 7).
 *
 * 「입력」 is the marker family's geometry with no value beside it: the tag alone,
 * in ink-3, because the reader's own number is not a 근거 and carries no chip.
 * A row that carries both a chip and `reader_input` cannot arrive from the server
 * — `reader_input` **is** the absence of a citation (`P9.S5` note 4) — and would
 * put two things in one fixed cell, so nothing is designed for it.
 */
export function DataRowLine({
  row,
  chips,
}: {
  row: AskDataRow;
  chips: Map<number, AskChip>;
}) {
  const chip = row.citation === undefined ? undefined : chips.get(row.citation);

  return (
    <div className={styles.row}>
      <span className={styles.rowLabel}>{row.label}</span>
      <span className={styles.rowValue}>{row.value}</span>
      {row.reader_input ? (
        <span className={styles.rowMark}>
          <span className={`${estimate.tag} ${styles.inputTag}`}>{TAG_INPUT}</span>
        </span>
      ) : null}
      {chip ? <InlineCitation chip={chip} place="row" /> : null}
    </div>
  );
}

/**
 * 공시에서 읽은 값 — the block a 도구 행 cannot be (R16 §2.3).
 *
 * > 블록: 1px `--border-soft`. 머리말 = mono 11px ink-3, 기본값 `DATA_HEADING`,
 * > 서버가 title을 주면 그것을 쓴다. 머리말 없음도 허용(`title: null`). …
 * > `rows.length > 6` → 6행 + `모두 보기 (N)` / `접기`. 타깃 32/44px. ≤767: 블록
 * > `margin-inline: -12px` (답변 상자 패딩 밀어내기). **3열 이상 표는 만들지
 * > 않는다.**
 *
 * 「머리말 없음」 has no producer today and that is the server's landed reading, not
 * a dropped element: `DataBlockEvent.title = None` means 「use the signed default」
 * and never reaches the wire (`P9.S3`), so a heading is always drawn.
 *
 * The fold is surface state and is never stored — the store keeps every row, and
 * a re-mounted block shows the first six again.
 */
export function DataBlock({
  rows,
  title,
  chips,
}: {
  rows: readonly AskDataRow[];
  title?: string;
  chips: Map<number, AskChip>;
}) {
  const [all, setAll] = useState(false);
  const shown = all ? rows : rows.slice(0, CAP);

  return (
    <div className={styles.data}>
      <p className={styles.dataHeading}>{title === undefined ? DATA_HEADING : title}</p>
      {shown.map((row, index) => (
        <DataRowLine key={index} row={row} chips={chips} />
      ))}
      {rows.length > CAP ? (
        <button
          type="button"
          className={styles.more}
          aria-expanded={all}
          onClick={() => setAll(!all)}
        >
          {all ? FOLD : SHOW_ALL(rows.length)}
        </button>
      ) : null}
    </div>
  );
}
