import type { RefObject } from "react";
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
 * The 보유량 strip — R4 §3 / decisions R4-2 and R4-6, **re-placed by R11 §3**.
 *
 * > label 보유 주식 수 · mono right-aligned integer input (`inputMode="numeric"`,
 * > comma-grouped) · suffix 주 · preset chips 100/500/1,000주 · caption
 * > 「서버 전송 없음」. Session memory: sessionStorage only; on a new stock with a
 * > remembered value, offer a restore chip 「이전 입력 {n}주」 — never auto-fill
 * > silently, never persist server-side.
 *
 * ## What R11 changed, and what it deliberately did not
 *
 * **Where it lives.** It is the identity panel's **bottom rail** now, not a panel
 * of its own: 종목 · 재조회 · 보유량 are one block of "what I am looking at". And
 * it renders **only where a number on this page changes with it** — a live ① or a
 * 놓친 돈 row (Q-C). On a ②-only or a no-rights stock it is absent, and the
 * absence says it: no disabled control, no apology, and therefore **no new copy**
 * for that decision. `StockView` owns that condition, because it owns the number.
 *
 * **Two chip grammars, one rule** (finding 15): a **solid** hairline is a value
 * you can set — selected is the inset surface plus `--ink-1`, not a hue — and a
 * **dashed** chip is an offer carried in from a previous session. The restore
 * chip is that offer; pressing it fills the field, and nothing fills it on its
 * own.
 *
 * **「서버 전송 없음」 moves up a tier** — mono `text-xs`, at the end of the row.
 * It is a term of this surface, not a footnote about it, and it is true by
 * construction: `lib/holding.ts` writes to sessionStorage and the API accepts no
 * holding count on any path.
 *
 * **No slider** (R4-2: holdings are exact integers) and **no debounce** — the
 * conversion is a multiplication, so the page recomputes on every keystroke. The
 * state itself lives one level up in `StockView`, because the same number drives
 * the ① cells and the 놓친 돈 breakdown and two copies of it could disagree.
 *
 * `inputRef` is the prompt's target: R11 §6's control focuses this field, so the
 * ref belongs to the owner of the number and is handed down here.
 */
export function HoldingStrip({
  digits,
  restore,
  inputRef,
  onChange,
  onRestore,
}: {
  /** The typed value as bare digits; the field displays it comma-grouped. */
  digits: string;
  /** The session's last count, when it belongs to a *different* stock. */
  restore: number | null;
  /** Focused by the 놓친 돈 prompt (R11 §6). */
  inputRef?: RefObject<HTMLInputElement | null>;
  onChange: (digits: string) => void;
  onRestore: () => void;
}) {
  return (
    <div className={styles.strip}>
      <label className={styles.striplab} htmlFor="holding-shares">
        {HOLDING_LABEL_KO}
      </label>

      {/* Stamped by extensions before hydration — see `SearchRow.tsx`. */}
      <input
        suppressHydrationWarning
        id="holding-shares"
        ref={inputRef}
        className={styles.num}
        type="text"
        inputMode="numeric"
        autoComplete="off"
        value={digits === "" ? "" : count(digits)}
        // Digits only: the grouping commas come back with the value, and
        // anything else the reader pastes is not a share count.
        onChange={(event) => onChange(event.target.value.replace(/[^\d]/g, ""))}
      />
      <span className={styles.unit}>{SHARES_UNIT_KO}</span>

      <div className={styles.presets}>
        {PRESET_SHARES.map((preset) => (
          <button
            key={preset}
            type="button"
            className={styles.preset}
            aria-pressed={digits === String(preset)}
            onClick={() => onChange(String(preset))}
          >
            {count(preset)}
            {SHARES_UNIT_KO}
          </button>
        ))}
      </div>

      {restore !== null ? (
        <button type="button" className={styles.restore} onClick={onRestore}>
          {restoreChipKo(count(restore))}
        </button>
      ) : null}

      <span className={styles.stripcap}>{HOLDING_CAPTION_KO}</span>
    </div>
  );
}
