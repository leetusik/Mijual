import { CraftPanel } from "@/components";
import { count } from "@/lib/format";
import {
  HOLDING_CAPTION_KO,
  HOLDING_LABEL_KO,
  PRESET_SHARES,
  SHARES_UNIT_KO,
  restoreChipKo,
} from "./copy";
import styles from "./Lookup.module.css";

/**
 * The 보유량 strip (R4 §Page anatomy 3, decisions R4-2 and R4-6).
 *
 * > **보유량 strip** (craft panel): label 보유 주식 수 · mono right-aligned
 * > integer input (`inputMode="numeric"`, comma-grouped) · suffix 주 · preset
 * > chips 100/500/1,000주 · caption "브라우저 세션에만 저장 · 서버 전송 없음".
 * > **Session memory:** sessionStorage only; on a new stock with a remembered
 * > value, offer a restore chip "이전 입력 {n}주" — never auto-fill silently,
 * > never persist server-side.
 *
 * **No slider** (decision R4-2: holdings are exact integers), and no debounce —
 * the conversion is a multiplication, so the page recomputes on every keystroke.
 * The state lives one level up in `StockView`, because the same number drives the
 * ① rows and the 놓친 돈 breakdown and two copies of it could disagree.
 *
 * The restore chip is an **offer**: pressing it fills the field, and nothing
 * fills it on its own.
 */
export function HoldingStrip({
  digits,
  restore,
  onChange,
  onRestore,
}: {
  /** The typed value as bare digits; the field displays it comma-grouped. */
  digits: string;
  /** The session's last count, when it belongs to a *different* stock. */
  restore: number | null;
  onChange: (digits: string) => void;
  onRestore: () => void;
}) {
  return (
    <CraftPanel className={styles.holding}>
      <label className={styles.holdingLabel} htmlFor="holding-shares">
        {HOLDING_LABEL_KO}
      </label>

      <div className={styles.holdingField}>
        <input
          id="holding-shares"
          className={`mono ${styles.holdingInput}`}
          type="text"
          inputMode="numeric"
          autoComplete="off"
          value={digits === "" ? "" : count(digits)}
          // Digits only: the grouping commas come back with the value, and
          // anything else the reader pastes is not a share count.
          onChange={(event) => onChange(event.target.value.replace(/[^\d]/g, ""))}
        />
        <span className={styles.holdingUnit}>{SHARES_UNIT_KO}</span>
      </div>

      <div className={styles.presets}>
        {PRESET_SHARES.map((preset) => (
          <button
            key={preset}
            type="button"
            className={styles.preset}
            aria-pressed={digits === String(preset)}
            onClick={() => onChange(String(preset))}
          >
            <span className="mono">{count(preset)}</span>
            {SHARES_UNIT_KO}
          </button>
        ))}
        {restore !== null ? (
          <button type="button" className={styles.restore} onClick={onRestore}>
            {restoreChipKo(count(restore))}
          </button>
        ) : null}
      </div>

      <p className={styles.holdingCaption}>{HOLDING_CAPTION_KO}</p>
    </CraftPanel>
  );
}
