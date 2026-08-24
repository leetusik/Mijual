"use client";

import { count } from "@/lib/format";
import { HOLDING_CAPTION_KO, HOLDING_LABEL_KO, PRESET_SHARES, SHARES_UNIT_KO } from "./copy";
import styles from "./Portfolio.module.css";

/**
 * 보유량 input — **R4's signed primitive, with one caption swapped** (R5
 * §Portfolio).
 *
 * > 입력은 R4 서명 프리미티브 재사용: mono 우측정렬, `inputMode="numeric"`, 콤마
 * > 그룹, 프리셋 칩 100/500/1,000주. **저장 위치 캡션만 교체**: "계정에 저장 ·
 * > 마감 알림의 기준".
 *
 * So this is `components/lookup/HoldingStrip.tsx`'s field, with the sentence that
 * states where the number lives replaced, because on this surface it goes to the
 * account (or, in 샘플 모드, to this browser) rather than to the tab's session.
 * Everything else about it is R4's: digits only, comma-grouped on display, no
 * slider (holdings are exact integers, decision R4-2), no debounce.
 *
 * **R13 §2 leaves it in one of R5's two places — 종목 추가.** A row's inline 수정
 * is now the 보유량 cell's own 36px field (`Holdings.tsx`, canon `.penum`): the
 * label, the 주 suffix and the preset chips are for stating a count the first
 * time, and inside a 132px table cell they were the reason that cell could not
 * hold a track. The behaviour they carried is unchanged there — same digits, same
 * comma grouping, same Enter — and `HOLDING_LABEL_KO` survives as that field's
 * `aria-label`.
 *
 * It is a controlled field over **bare digits**: the commas are display, and
 * `lib/holding.ts`'s `parseShares` is what turns them back into a count.
 */
export function SharesInput({
  id,
  digits,
  caption = HOLDING_CAPTION_KO,
  autoFocus = false,
  disabled = false,
  onChange,
  onSubmit,
}: {
  id: string;
  digits: string;
  /**
   * `null` in 샘플 모드, and that is a decision rather than an omission: the
   * signed caption states that the count goes to the **account**, which is not
   * true of a sample (it goes to this browser, R5-4), and no second caption is
   * signed for that case. So the sample renders **no line** rather than a false
   * one — its banner already states where the whole mode lives — and the gap is
   * flagged for `P5.S19` like every other unsigned sentence.
   */
  caption?: string | null;
  autoFocus?: boolean;
  disabled?: boolean;
  onChange: (digits: string) => void;
  /** Enter confirms, where the surrounding control has a confirm. */
  onSubmit?: () => void;
}) {
  return (
    <div className={styles.sharesField}>
      <label className={styles.sharesLabel} htmlFor={id}>
        {HOLDING_LABEL_KO}
      </label>

      <div className={styles.sharesRow}>
        <input
          id={id}
          className={`mono ${styles.sharesInput}`}
          type="text"
          inputMode="numeric"
          autoComplete="off"
          autoFocus={autoFocus}
          disabled={disabled}
          value={digits === "" ? "" : count(digits)}
          onChange={(event) => onChange(event.target.value.replace(/[^\d]/g, ""))}
          onKeyDown={(event) => {
            if (event.key === "Enter" && onSubmit) {
              event.preventDefault();
              onSubmit();
            }
          }}
        />
        <span className={styles.sharesUnit}>{SHARES_UNIT_KO}</span>
      </div>

      <div className={styles.presets}>
        {PRESET_SHARES.map((preset) => (
          <button
            key={preset}
            type="button"
            className={styles.preset}
            disabled={disabled}
            aria-pressed={digits === String(preset)}
            onClick={() => onChange(String(preset))}
          >
            <span className="mono">{count(preset)}</span>
            {SHARES_UNIT_KO}
          </button>
        ))}
      </div>

      {caption ? <p className={styles.caption}>{caption}</p> : null}
    </div>
  );
}
