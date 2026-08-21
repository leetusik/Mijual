/**
 * The presentation contract, typed.
 *
 * Every shape here mirrors a `payload()` in `mijual.present` or a router's own
 * dict (`mijual.web.routers.*`), and the three contract-wide serialization rules
 * are encoded rather than described:
 *
 * 1. **Absent means the key is absent, never `null`.** So an omitted value is
 *    `?:` (optional), and `| null` appears *only* where the server genuinely
 *    emits `null` — `countdown.date`/`dday`/`days`, `corp_name`, `rcept_no`,
 *    `freshness.as_of`, a version row's `rcept_dt`/`correction_kind`. Those are
 *    keys that are always present and sometimes empty, which is a different
 *    statement from "this value does not exist".
 * 2. **Money and every ratio are exact decimal strings**, counts are `int`,
 *    calendar dates are bare `YYYY-MM-DD` and instants are `+09:00` strings. A
 *    decimal string is never parsed with `Number()` on the way in: 배정비율 keeps
 *    ten decimals and a ₩ total runs past 10^10.
 * 3. **Every value carries `estimated`** — see `Figure`.
 */

import type { RightsType } from "./copy";

export type { RightsType };

/** One addend of a citation the filer printed as a sum of table rows. */
export type QuotePart = {
  quote: string;
  span?: [number, number];
};

/**
 * One value a surface may render, and which of the product's two kinds it is.
 *
 * `estimated` is **required** — it has no default in `mijual.present.Figure`
 * either, so a value that forgets to say which kind it is does not construct.
 * `EstimateMarker` refuses to render without it.
 *
 * The citation is one of exactly three states and never a fourth: `quote` +
 * `span` (one cell), or `parts` (≥ 2 addends summing to `value`), or neither
 * (uncitable — no chip; `rcept_no` still links to DART).
 */
export type Figure = {
  /** A decimal **string** for money and ratios, `number` for counts, a bare ISO
   * string for a date. Never re-parsed into a float. */
  value: string | number;
  estimated: boolean;
  quote?: string;
  span?: [number, number];
  parts?: QuotePart[];
  rcept_no?: string;
};

/** One gate-passing field, with the citation triple that answers "왜 이 값?". */
export type FieldPayload = {
  field_key: string;
  /** `"value"` → render `value`; `"추후결정"` → render `StateBadge tbd` alone. */
  display: "value" | "추후결정";
  /** Always `false` — a reading of a filing is a fact, never a derivation. */
  estimated: boolean;
  korean_name?: string;
  /** Absent iff `display === "추후결정"`: 추후결정 means *no date*. */
  value?: unknown;
  quote?: string;
  span?: [number, number];
  rcept_no?: string;
};

/** `upcoming` / `open` / `closed` / `unknown` — machine tokens. The Korean is the
 * surface's, and it differs per rights type (`ui-traps.md` #5). */
export type WindowState = "upcoming" | "open" | "closed" | "unknown";

/** The one date a rights type counts down to. Computed upstream, in KST. */
export type Countdown = {
  label_ko: string;
  /** `null` when the schedule is 추후결정. **No date ever sits beside the badge.** */
  date: string | null;
  /** `D-5` / `D-DAY` / `D+41`. Never derived in the browser. */
  dday: string | null;
  days: number | null;
  window: [string | null, string | null];
  window_state: WindowState;
  /** The KST calendar day `dday` was computed against. */
  reference: string;
  source: string;
};

/** The 본문 identity check (`ui-traps.md` #3). The card shows the master name and
 * **states** a disagreement; it never silently corrects one. */
export type Identity = {
  corp_name: string | null;
  corp_name_in_body?: string;
  corp_name_agrees_with_body?: boolean;
};

/** One event as a detail page reads it. Carries **no gate reason code**. */
export type EventView = Identity & {
  event_id: number;
  corp_code: string;
  rights_type: RightsType;
  rcept_no: string | null;
  original_rcept_dt: string | null;
  state: "exposable" | "withdrawn";
  countdown: Countdown;
  /** A gate-blocked field has no key here at all. */
  fields: Record<string, FieldPayload>;
  /** The locked 철회 sentence, on a withdrawn event only. */
  notice_ko?: string;
};

/** ①'s money factors. With no 확정발행가 there is **no money key at all**. */
export type OfferingInputs = {
  rcept_no?: string;
  price_confirmed: boolean;
  planned_price?: Figure;
  confirmed_price?: Figure;
  discount_rate?: Figure;
  /** 배정비율 to its full ten decimals, as a decimal string. */
  allotment_ratio?: Figure;
  excess_ratio?: Figure;
  new_shares?: Figure;
  /** 증서 1주 이론가치 — an estimate, always tagged. */
  unit_value?: Figure;
  unit_value_floor?: Figure;
  record_date?: string;
  final_price_date?: string;
  subscription?: unknown;
};

/** One offering's 소멸 outcome, from the 증권발행실적보고서. */
export type LapseResult = {
  status: string;
  corp_code?: string;
  corp_name?: string;
  decision_rcept_no?: string;
  performance_rcept_no?: string;
  subscription_end?: string;
  warrants_issued?: Figure;
  warrants_exercised?: Figure;
  lapsed?: Figure;
  lapse_rate?: Figure;
  confirmed_price?: Figure;
  discount_rate?: Figure;
  allotment_ratio?: Figure;
  unit_value?: Figure;
  unit_value_floor?: Figure;
  value?: Figure;
  value_floor?: Figure;
};

/** 발행사 기재 불일치: both readings, both citations, **no verdict**. Exactly one
 * reading is `used` — naming none would hide the choice and naming two would be
 * a reconciliation. */
export type Disagreement = {
  kind: string;
  label_ko: string;
  readings: Array<Figure & { key: string; used: boolean; label?: string; inputs?: Figure[] }>;
};

/** R3's ② fact strip — exactly six values, all facts, none with a span (an API
 * row has no character offsets; its citation is the filing number). */
export type ConvertibleView = {
  rcept_no?: string;
  conversion_price?: Figure;
  overhang_pct?: Figure;
  shares?: Figure;
  face_amount?: Figure;
  issue_method?: string;
  maturity_date?: string;
};

export type Freshness = {
  /** `max(Event.last_seen_at)` — a corpus fact, never the request time. */
  as_of: string | null;
  stale: boolean;
  stale_after_hours: number;
  /** Floored, never rounded up. Served, so no client times its own clock. */
  age_hours?: number;
};

/** Every landing number, from one object — so the hero's stat line and the
 * countdown/stats card cannot disagree. */
export type BoardSummary = {
  as_of: string | null;
  watching: number;
  by_rights: Partial<Record<RightsType, number>>;
  within_30d: number;
  open_now: number;
  tbd: number;
  lapse_pending: number;
  performance_reports: number;
  lapsed_value?: Figure;
  lapsed_value_floor?: Figure;
  lapsed_warrants?: Figure;
  issued_warrants?: Figure;
  lapse_rate?: Figure;
  next_lapse?: { date?: string; corp_name?: string; target?: string };
  freshness?: Freshness;
};

/** ①'s board extras cell. ②/③ carry none — absence is the design, no dash. */
export type BoardOffering = {
  price_confirmed: boolean;
  subscription_start?: string;
  subscription_end?: string;
};

export type BoardRow = {
  event_id: number;
  corp_code: string;
  corp_name: string | null;
  rights_type: RightsType;
  rcept_no: string | null;
  state: string;
  countdown: Countdown;
  offering?: BoardOffering;
};

/** A pinned strip: `count` is what is served, `total` what exists. */
export type BoardStrip = { count: number; total: number; rows: BoardRow[] };

export type BoardResponse = {
  reference: string;
  /** Always whole-board, even under `?rights=` — the tabs must keep showing what
   * the other tabs hold. */
  counts: { all: number } & Partial<Record<RightsType, number>>;
  rows: BoardRow[];
  /** ② 전환청구 진행 중 — opened, not closed. **Never labelled 종료.** */
  open_now: BoardStrip;
  /** 일정 추후결정 — unranked, and no date anywhere near it. */
  tbd: BoardStrip;
  freshness: Freshness;
};

export type EventDetail = EventView & {
  corrections?: { corrected: boolean; versions: number; summary?: string; schedule_impact?: string };
  offering?: OfferingInputs;
  lapse_result?: LapseResult;
  issuer_disagreement?: Disagreement;
  convertible?: ConvertibleView;
  /** 철회 evidence: the 정정사항 row that retracted the decision. */
  withdrawal?: {
    rcept_no?: string;
    item?: string;
    before?: string;
    after?: string;
    span?: [number, number];
  };
};

export type VersionRow = {
  rcept_no: string;
  rcept_dt: string | null;
  correction_kind: string | null;
  /** Exactly one row carries `true` — unless the event has no readable 본문 at
   * all, in which case **no** row does (239 of 422 exposable ② have none). */
  is_current_readable: boolean;
  report_nm?: string;
};

export type CorrectionStory = {
  corrected: boolean;
  versions: VersionRow[];
  field_moves?: Array<Record<string, unknown>>;
  interpretation?: Record<string, unknown>;
  quote?: string;
  span?: [number, number];
  rcept_no?: string;
  event_id: number;
  rcept_no_current: string | null;
};

/** One row of 진행 중인 권리 / 포트폴리오: the event view plus its type's context.
 * The **same** shape on both surfaces — one composition, one reading. */
export type RightsRow = EventView & {
  offering?: OfferingInputs;
  convertible?: ConvertibleView;
  /** Portfolio only: a stored count, never a derived number. */
  shares?: number;
  holding_id?: number;
  lapse?: LapseResult;
  /** Absent — never `false` — when nobody is logged in. */
  claimed?: boolean;
};

/** A subset total. Emits no zero: outside coverage a number is *unstated*. */
export type LapseTotals = {
  offerings: number;
  valued: number;
  lapsed?: Figure;
  issued?: Figure;
  lapse_rate?: Figure;
  value?: Figure;
  value_floor?: Figure;
};

export type StockPage = {
  stock: { corp_code: string; corp_name: string | null; stock_code: string | null };
  reference: string;
  rights: { count: number; rows: RightsRow[] };
  lapse: {
    /** Served, never assumed client-side. Outside it, a row is **absent**. */
    coverage: { start: string; end: string; convertible_start: string };
    totals: LapseTotals;
    rows: Array<{ rights_type: RightsType; lapse: LapseResult } & Partial<RightsRow>>;
    pending?: { count: number; subscription_end: string };
  };
};

/** A search that finds nothing is a **result**, not an error — and it names no
 * reason, no candidate and no near-miss. */
export type StockLookup =
  | ({ query: string; found: true } & StockPage)
  | { query: string; found: false };

export type Account = { email: string; created_at: string | null };

export type AuthState =
  | { authenticated: false }
  | { authenticated: true; account: Account };

export type Holding = {
  id: number;
  corp_code: string;
  shares: number;
  corp_name?: string;
  stock_code?: string;
};

export type PortfolioHolding = Omit<Holding, "id"> & {
  id?: number;
  rights: { count: number; next?: Pick<EventView, "event_id" | "rcept_no" | "rights_type"> & { countdown: Countdown } };
};

export type Portfolio = {
  reference: string;
  holdings: PortfolioHolding[];
  /** 다가오는 마감: dated → ② 진행 중 → 일정 추후결정. An **open ② is never in
   * `past`** — filing it there is the 종료 label `ui-traps.md` #5 forbids. */
  upcoming: RightsRow[];
  past: RightsRow[];
  /** Present and `true` only on `GET /portfolio/sample`. */
  sample?: boolean;
};

/** 알림 설정. `[]` is a valid setting and means no mail (R5's only off switch);
 * an **absent** stored row means the 7일+1일 default, not "off". There is no
 * KakaoTalk key: that row renders a 「예정」 chip and no working control. */
export type Notifications = { address: string; lead_days: number[] };
