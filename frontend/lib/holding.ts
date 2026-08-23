/**
 * The N주 conversion — **the product's one multiplication site**.
 *
 * R4 owns the whole per-holding math ("The surface owns ALL N주 math display —
 * R3: detail shows per-unit only"), and both surfaces that convert a holding
 * compose it from *served factors*: 내 종목 조회 (`P5.S14`) and 내 포트폴리오
 * (`P5.S16`). The server deliberately ships factors and never products —
 * `P5.S8` note 1 measured that decision and named its consequence: **exactly one
 * implementation of ⌊N × 배정비율⌋ × 증서 1주 이론가치 may exist**, or the two
 * surfaces become "두 divergent readouts for the same number", which is the
 * failure mode R4 names and R5 restates ("내 종목 조회와 수치 불일치 금지 (같은
 * contract 소스)"). That implementation is this module. **`P5.S16` imports it;
 * it does not write a second one.**
 *
 * ## No float, anywhere
 *
 * The contract serves money and every ratio as **exact decimal strings** and
 * 배정비율 keeps all ten decimals (`lib/types.ts` rule 2). `Number()` on any of
 * them is the one operation that can quietly change a published number, so the
 * arithmetic here is `BigInt` over the digits with the decimal point tracked
 * separately — exact by construction, arbitrary precision, and no dependency.
 * `lib/format.ts` renders these strings; this module produces them.
 *
 * ## Two rules that are structural rather than remembered
 *
 * 1. **⌊N × 배정비율⌋ — 단수주 절사.** `mijual.calc.allotted_shares` governs
 *    (R4's signoff records the orchestrator's verification that the cards' floor
 *    assumption matches it), so the flooring is the multiplication's own step,
 *    never a rounding of a float that already lost the digits.
 * 2. **확정발행가 null ⇒ no money number at all.** `convert()` returns
 *    `value: null` and `valueFloor: null` when the factors carry no
 *    `unit_value`, so a surface *cannot* print money before the price is fixed
 *    — the same shape `mijual.present` uses on the server, where an
 *    `OfferingInputs` carrying money with no `confirmed_price` does not
 *    construct. Share counts still compute: 배정 신주 is a fact about the ratio,
 *    not about the price.
 */

import type { Figure } from "./types";

/** A decimal number as an exact integer and a scale: value = units × 10^-scale. */
type Decimal = { units: bigint; scale: number };

function decimal(value: string | number): Decimal {
  const text = typeof value === "number" ? String(value) : value.trim();
  const match = /^([+-]?)(\d*)(?:\.(\d*))?$/.exec(text);
  if (!match || (match[2] === "" && (match[3] ?? "") === "")) {
    // Loud rather than quiet, exactly as `lib/format.ts` is: a value that is not
    // a plain decimal did not come from the contract.
    throw new Error(`holding: not a decimal value: ${JSON.stringify(value)}`);
  }
  const frac = match[3] ?? "";
  const units = BigInt(`${match[2] || "0"}${frac}`) * (match[1] === "-" ? -1n : 1n);
  return { units, scale: frac.length };
}

/** Back to a plain decimal string — the same shape the API serves. */
function text({ units, scale }: Decimal): string {
  const negative = units < 0n;
  const digits = (negative ? -units : units).toString().padStart(scale + 1, "0");
  const int = digits.slice(0, digits.length - scale);
  const frac = scale > 0 ? digits.slice(digits.length - scale).replace(/0+$/, "") : "";
  return `${negative && /[1-9]/.test(digits) ? "-" : ""}${int}${frac ? `.${frac}` : ""}`;
}

/** An exact product of a whole share count and a served decimal factor. */
function product(shares: number, factor: string | number): Decimal {
  const { units, scale } = decimal(factor);
  return { units: units * BigInt(shares), scale };
}

/** ⌊value⌋ for a non-negative decimal. Share counts are never negative here, so
 * truncating division *is* flooring, and it happens on the exact digits. */
function floor({ units, scale }: Decimal): bigint {
  if (scale === 0) return units;
  const divisor = 10n ** BigInt(scale);
  const quotient = units / divisor;
  return units < 0n && units % divisor !== 0n ? quotient - 1n : quotient;
}

/**
 * The largest holding this surface accepts.
 *
 * The same bound the backend puts on a stored holding (`P5.S8` note 4:
 * `MAX_SHARES = 10_000_000_000`, because 삼성전자 alone has ~5.97bn shares
 * outstanding). Nothing here is ever sent to a server, but a number 조회 accepts
 * and 포트폴리오 refuses would be two answers to one question.
 */
export const MAX_SHARES = 10_000_000_000;

/**
 * A typed holding count from what the reader actually typed.
 *
 * The input is `inputMode="numeric"` and comma-grouped (R4 §3), so the commas
 * come back with the value; everything else is refused rather than coerced —
 * `null` means "no holding entered", which is a different state from zero and is
 * what keeps the per-holding figures off the page until there is a holding.
 */
export function parseShares(raw: string): number | null {
  const digits = raw.replace(/,/g, "").trim();
  if (digits === "" || !/^\d+$/.test(digits)) return null;
  const shares = Number(digits);
  if (!Number.isSafeInteger(shares) || shares <= 0) return null;
  return Math.min(shares, MAX_SHARES);
}

/** ⌊n × 배정비율⌋ — `mijual.calc.allotted_shares`, 단수주 절사. */
export function allottedShares(shares: number, allotmentRatio: string | number): number {
  return Number(floor(product(shares, allotmentRatio)));
}

/** ⌊배정 신주 × 초과청약비율⌋ — R4: shown as "+{k}주" where the field passed. */
export function excessLimit(allotted: number, excessRatio: string | number): number {
  return Number(floor(product(allotted, excessRatio)));
}

/** 배정 신주 × 증서 1주 이론가치, exact — the string `won()` then renders. */
export function sharesValue(allotted: number, unitValue: string | number): string {
  return text(product(allotted, unitValue));
}

/** Σ over offerings, exact. An empty list has no total — **not** a zero. */
export function sumValues(values: readonly string[]): string | null {
  if (values.length === 0) return null;
  const parsed = values.map(decimal);
  const scale = Math.max(...parsed.map((value) => value.scale));
  const units = parsed.reduce(
    (total, value) => total + value.units * 10n ** BigInt(scale - value.scale),
    0n,
  );
  return text({ units, scale });
}

/**
 * The served factors this math reads.
 *
 * Both payload shapes that carry them satisfy it structurally — ①'s
 * `OfferingInputs` (a live 진행 중인 권리 row) and `LapseResult` (a 놓친 돈 row)
 * — which is why one function serves both sections *and* 내 포트폴리오's rows.
 */
export type ConversionFactors = {
  price_confirmed?: boolean;
  allotment_ratio?: Figure;
  excess_ratio?: Figure;
  unit_value?: Figure;
  unit_value_floor?: Figure;
};

/** What a holding converts to. A `null` is an **absent** number, never a zero. */
export type Conversion = {
  /** ⌊n × 배정비율⌋. `null` when the filing states no 배정비율. */
  allotted: number | null;
  /** ⌊배정 신주 × 초과청약비율⌋, when that field passed its gate. */
  excess: number | null;
  /** 배정 신주 × `unit_value`. **`null` before 확정발행가 — no money at all.** */
  value: string | null;
  /** The band's lower edge, on the same condition. */
  valueFloor: string | null;
  /** The factors' own `estimated` flags, passed through — never a literal. */
  valueEstimated: boolean;
  floorEstimated: boolean;
};

/**
 * Convert a holding against one offering's served factors.
 *
 * `shares` is the reader's own number and never leaves the browser (R4 §3,
 * `security`: "Holding value sent to a server — never"). Everything else is
 * upstream: this composes, it derives nothing.
 */
export function convert(factors: ConversionFactors, shares: number | null): Conversion {
  const ratio = factors.allotment_ratio;
  const allotted =
    shares !== null && ratio !== undefined ? allottedShares(shares, String(ratio.value)) : null;

  const excessRatio = factors.excess_ratio;
  const excess =
    allotted !== null && excessRatio !== undefined
      ? excessLimit(allotted, String(excessRatio.value))
      : null;

  // The money gate. `unit_value` is present only where the price is confirmed —
  // `mijual.present` refuses to build the shape otherwise — and the explicit
  // `price_confirmed === false` check is the same rule stated from the other end.
  const priced = factors.price_confirmed !== false && factors.unit_value !== undefined;
  const unit = priced ? factors.unit_value : undefined;
  const unitFloor = priced ? factors.unit_value_floor : undefined;

  return {
    allotted,
    excess,
    value: allotted !== null && unit ? sharesValue(allotted, String(unit.value)) : null,
    valueFloor:
      allotted !== null && unitFloor ? sharesValue(allotted, String(unitFloor.value)) : null,
    valueEstimated: unit?.estimated ?? false,
    floorEstimated: unitFloor?.estimated ?? false,
  };
}

// ---------------------------------------------------------------------------
// Session memory (R4 decision R4-6)
// ---------------------------------------------------------------------------

/**
 * Where 조회's holding counts live: **sessionStorage, and nowhere else**.
 *
 * R4-6: "remember within the browser session only … Nothing server-side". The
 * surface used to state both halves; since **P7 (item 10)** the caption renders
 * only the promise, 「서버 전송 없음」 — the storage is still exactly this module
 * and is simply no longer narrated to the reader.
 * `security` says the same from the other side — anonymous state never reaches
 * the server, and there is no anonymous write endpoint to reach (`P5.S8` note
 * 13).
 *
 * One key, one JSON object, so **`P5.S16` can read the whole session in one go**
 * for R5-3's 세션 이월 제안 (which offers to carry these into a portfolio and
 * makes ordinary authenticated writes only if the reader accepts):
 *
 * ```json
 * {"v": 1,
 *  "entries": {"00162461": 500, "00102618": 300},
 *  "last": {"corp_code": "00102618", "shares": 300}}
 * ```
 *
 * `entries` is per-issuer (the reader's own input for that exact stock, restored
 * within the session); `last` is what the **restore chip** on a *different*
 * stock offers — "이전 입력 {n}주", offered and never auto-filled.
 */
export const SESSION_KEY = "mijual.lookup.holdings";

export type SessionHoldings = {
  v: 1;
  entries: Record<string, number>;
  last?: { corp_code: string; shares: number };
};

const EMPTY: SessionHoldings = { v: 1, entries: {} };

/** Read the session's holdings. Any unreadable state is treated as none: a
 * remembered number is a convenience, and a broken one must never break a page. */
export function readSessionHoldings(): SessionHoldings {
  if (typeof window === "undefined") return EMPTY;
  try {
    const raw = window.sessionStorage.getItem(SESSION_KEY);
    if (!raw) return EMPTY;
    const parsed: unknown = JSON.parse(raw);
    if (!parsed || typeof parsed !== "object") return EMPTY;
    const value = parsed as Partial<SessionHoldings>;
    const entries: Record<string, number> = {};
    for (const [corp, shares] of Object.entries(value.entries ?? {})) {
      if (typeof shares === "number" && Number.isSafeInteger(shares) && shares > 0) {
        entries[corp] = shares;
      }
    }
    return { v: 1, entries, last: value.last };
  } catch {
    return EMPTY;
  }
}

/** Remember one issuer's count, and make it the session's `last`. */
export function writeSessionHolding(corpCode: string, shares: number | null): void {
  if (typeof window === "undefined") return;
  try {
    const current = readSessionHoldings();
    const entries = { ...current.entries };
    if (shares === null) delete entries[corpCode];
    else entries[corpCode] = shares;
    const next: SessionHoldings = {
      v: 1,
      entries,
      last: shares === null ? current.last : { corp_code: corpCode, shares },
    };
    window.sessionStorage.setItem(SESSION_KEY, JSON.stringify(next));
  } catch {
    // A storage quota or a privacy mode that refuses writes costs the reader a
    // remembered number, which is not worth an exception on a data surface.
  }
}
