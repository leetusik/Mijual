/**
 * Rendering the contract's numbers — exactly, and without a float anywhere.
 *
 * The API serves money and every ratio as **exact decimal strings** and counts as
 * integers (`lib/types.ts` rule 2), for a reason this module has to keep: 배정비율
 * carries ten decimals and a ₩ total runs past 10^10, so `Number()` is the one
 * operation that can quietly change a published number. Everything here is
 * therefore string arithmetic on the decimal digits — shift the point, round, put
 * the commas back — and no value is ever parsed into a float.
 *
 * `won()` is not a new rule either: it mirrors **`mijual.estimate.won`**, the
 * product's own unit ("``2989863900`` → ``29.9억원`` — the unit the board and the
 * deck speak"), including its 조원/억원/원 thresholds, its decimal places and its
 * round-half-even. The landing prints 718.1억원 because that is what the pipeline
 * prints, not because this file rounded to taste.
 */

/** A decimal number as digits and a scale: value = ±digits × 10^-scale. */
type Dec = { neg: boolean; digits: string; scale: number };

function parse(value: string | number): Dec {
  const text = typeof value === "number" ? String(value) : value.trim();
  const match = /^([+-]?)(\d*)(?:\.(\d*))?$/.exec(text);
  if (!match || (match[2] === "" && (match[3] ?? "") === "")) {
    // Loud rather than quiet: a value that is not a plain decimal did not come
    // from the contract, and rendering it as if it had would be a number this
    // product cannot source.
    throw new Error(`format: not a decimal value: ${JSON.stringify(value)}`);
  }
  const frac = match[3] ?? "";
  const digits = `${match[2]}${frac}`.replace(/^0+(?=\d)/, "");
  return { neg: match[1] === "-", digits: digits === "" ? "0" : digits, scale: frac.length };
}

/** Multiply by 10^places (a negative `places` divides) — the decimal point moves,
 * the digits do not change. */
function shift(value: Dec, places: number): Dec {
  const scale = value.scale - places;
  if (scale >= 0) return { ...value, scale };
  return { ...value, digits: value.digits + "0".repeat(-scale), scale: 0 };
}

/** Round to `scale` decimal places, **half to even** — Python's own rule when it
 * formats a `Decimal`, which is what `mijual.estimate.won` does. */
function round(value: Dec, scale: number): Dec {
  if (value.scale <= scale) {
    return { ...value, digits: value.digits + "0".repeat(scale - value.scale), scale };
  }
  const drop = value.scale - scale;
  const padded = value.digits.padStart(drop + 1, "0");
  const keep = padded.slice(0, padded.length - drop);
  const cut = padded.slice(padded.length - drop);
  const half = `5${"0".repeat(drop - 1)}`;
  const roundUp =
    cut > half || (cut === half && (keep.charCodeAt(keep.length - 1) - 48) % 2 === 1);
  const digits = roundUp ? addOne(keep) : keep;
  return { neg: value.neg, digits, scale };
}

/** `"1299"` → `"1300"`. Decimal increment, so no integer ever overflows. */
function addOne(digits: string): string {
  const out = digits.split("");
  for (let i = out.length - 1; i >= 0; i -= 1) {
    if (out[i] !== "9") {
      out[i] = String(Number(out[i]) + 1);
      return out.join("");
    }
    out[i] = "0";
  }
  return `1${out.join("")}`;
}

/** Thousands separators — the grouping every numeral in this product carries. */
function group(digits: string): string {
  return digits.replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

function render(value: Dec): string {
  const padded = value.digits.padStart(value.scale + 1, "0");
  const int = padded.slice(0, padded.length - value.scale) || "0";
  const frac = value.scale > 0 ? padded.slice(padded.length - value.scale) : "";
  const sign = value.neg && /[1-9]/.test(value.digits) ? "-" : "";
  return `${sign}${group(int)}${frac ? `.${frac}` : ""}`;
}

/** How many digits the integer part has — the comparison `won()` needs against
 * 10^12 and 10^8, done on digit counts so nothing is converted to a number. */
function intDigits(value: Dec): number {
  const padded = value.digits.padStart(value.scale + 1, "0");
  return padded.slice(0, padded.length - value.scale).replace(/^0+(?=\d)/, "").length;
}

/**
 * A won amount in the unit the product speaks.
 *
 * Mirrors `mijual.estimate.won` branch for branch:
 * `≥ 10^12` → `조원` with 2 decimals · `≥ 10^8` → `억원` with 1 decimal ·
 * otherwise `원` with none. `71812971649` → `718.1억원`.
 */
export function won(value: string | number): string {
  const decimal = parse(value);
  const digits = intDigits(decimal);
  if (digits >= 13) return `${render(round(shift(decimal, -12), 2))}조원`;
  if (digits >= 9) return `${render(round(shift(decimal, -8), 1))}억원`;
  return `${render(round(decimal, 0))}원`;
}

/** A count with its thousands separators: `51253956` → `51,253,956`. */
export function count(value: string | number): string {
  return render(round(parse(value), 0));
}

/** A served ratio as a percentage — `"0.1402"` → `"14.0%"`, which is the
 * pipeline's own `f"{rate:.1%}"` in the 발표용 문장 block. */
export function percent(value: string | number, decimals = 1): string {
  return `${render(round(shift(parse(value), 2), decimals))}%`;
}

/**
 * The 기준시각 as the board prints it: `YYYY-MM-DD HH:MM`.
 *
 * The instant arrives as an absolute `+09:00` string and is **sliced, never
 * re-parsed into a `Date`** — parsing would render it in the reader's own
 * timezone, and every date and time in this product is KST by contract (D-10).
 * The `KST` suffix beside it is the surface's, and it is true because the server
 * only ever emits `+09:00`.
 */
export function kstStamp(instant: string): { date: string; time: string } {
  return { date: instant.slice(0, 10), time: instant.slice(11, 16) };
}
