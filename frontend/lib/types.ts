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
  /** `tie_count` is how many offerings share that 청약 마감 (R9 §6): 1 when only
   * `corp_name`'s does, and the surface says 「N개 종목」 instead of a name when it
   * is more. Optional because it is `P8.S5`'s addition to an older contract. */
  next_lapse?: { date?: string; corp_name?: string; target?: string; tie_count?: number };
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

/**
 * One 놓친 돈 row: the 실적보고서's outcome, plus the event-derived block **only
 * when the 유상증자결정 is exposable** (`P5.S4` note 6). A row hanging off a
 * flagged event keeps its 소멸 계산 — a lapse is a fact the 실적보고서 attests —
 * and has no `countdown`, no `warrant_trading_period` quote and no `rcept_no` to
 * link, rather than a "상세 보기" that would 404.
 */
export type LapseBreakdownRow = { rights_type: RightsType; lapse: LapseResult } & Partial<
  RightsRow
> & {
    /** The 매매기간 field payload — this row's one `Citation` (R4). */
    warrant_trading_period?: FieldPayload;
    /** Present where the filing contradicts itself; `ui-traps.md` #2 is a
     * payload rule, so it rides on a breakdown row too. */
    issuer_disagreement?: Disagreement;
  };

export type StockPage = {
  stock: { corp_code: string; corp_name: string | null; stock_code: string | null };
  reference: string;
  rights: { count: number; rows: RightsRow[] };
  lapse: {
    /** Served, never assumed client-side. Outside it, a row is **absent**. */
    coverage: { start: string; end: string; convertible_start: string };
    totals: LapseTotals;
    rows: LapseBreakdownRow[];
    pending?: { count: number; subscription_end: string };
  };
};

/** A search that finds nothing is a **result**, not an error — and it names no
 * reason and no near-miss. Candidates live on their own route, before the submit
 * (`StockSuggestions`); this payload still offers none. */
export type StockLookup =
  | ({ query: string; found: true } & StockPage)
  | { query: string; found: false };

/**
 * One candidate for a query still being typed (`GET /stocks/suggest`, `P7.S4`).
 *
 * The `corp_code` is the whole point: a chosen candidate is navigated by the
 * **handle** (`stockPath`), never re-resolved from its name, which is what keeps
 * "the system never silently opens a different company" true while still letting
 * a reader choose one.
 */
export type StockSuggestion = {
  corp_code: string;
  corp_name: string | null;
  stock_code: string | null;
};

/** At most eight candidates; nothing matching is an **empty list**, not a 404. */
export type StockSuggestions = { query: string; candidates: StockSuggestion[] };

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

// ---------------------------------------------------------------------------
// 운영 관제 (P5.S9's `/ops` routes) — the operator's panel, R7
// ---------------------------------------------------------------------------
//
// A different contract from everything above: this is the operator surface, and
// what the reader contract hides is exactly what it serves. Three of its rules
// are in the types rather than in prose:
//
// 1. **A reason/suppression code travels raw English** and carries `reason_ko`
//    *only* where the gate layer itself owns that Korean (§6.1) — hence
//    `reason_ko?:`, never a string with a fallback.
// 2. **A rate never travels without its basis**: `distinct_count` + `rate` sit
//    beside `count`, and the queue's own `basis` names the denominator.
// 3. **`▷` is pipeline output quoted verbatim** (`spend_line`, `cost_line`) and
//    must never be swapped for 「추정」 here — 경계 = 출처.

/** One reason or suppression code as the panel renders it: the code raw. */
export type OpsReason = {
  /** Raw English, `""` for a row with no reason (the `passed` bucket). */
  code: string;
  count: number;
  /** Only when the **code** owns that Korean. Absent is a rendering, not a gap. */
  reason_ko?: string;
  gate_status?: string;
  distinct_count?: number;
  /** An exact decimal string over the distinct basis, never a float. */
  rate?: string;
};

export type OpsEvents = {
  considered: number;
  exposable: number;
  suppressed: number;
  /** `"R1:exposable"` → count, `gates summary`'s own by-state line. */
  by_state: Record<string, number>;
  blocked: OpsReason[];
  suppressed_reasons: { code: string; count: number }[];
  /** The four `BLOCKING_FLAGS`, with the Korean the **code** carries. */
  blocking_flags: { code: string; reason_ko: string }[];
};

export type OpsFields = {
  verdicts: Record<string, number>;
  stored_rows: number;
  renderable: {
    total: number;
    by_field: { field_key: string; korean_name?: string | null; count: number; tbd: number }[];
  };
};

export type OpsGateSummary = {
  events: OpsEvents;
  fields: OpsFields;
  /** When the gate layer last measured any of it — absent if it never has. */
  measured_at?: string;
};

/** One periodic job as `mijual.beat` declares it, plus every instant it was due
 * in the served window — the schedule's half of the 「실행 기록 없음」 join. */
export type OpsBeatEntry = {
  name: string;
  task: string;
  /** `"07:30 daily"` / `"04:30 Sun"` — configuration, so raw English mono. */
  spec: string;
  hour: number;
  minute: number;
  day_of_week: number | null;
  kwargs: Record<string, unknown>;
  due: string[];
};

export type OpsBeat = {
  timezone: string;
  as_of: string;
  entries: OpsBeatEntry[];
  due_since: string;
};

export type OpsStage = {
  name: string;
  status: string;
  seconds?: number;
  requests?: number;
  calls?: number;
  cost_usd?: number;
  summary?: string;
  detail?: Record<string, unknown>;
};

/** One row of the run log. A run **in flight** has no `finished_at`, no `ok` and
 * no `spend_line`: it says so by omission rather than by a zero that would read
 * as "cost nothing". */
export type OpsRun = {
  id: number;
  label: string;
  /** `beat` (the schedule fired it) or `manual`. */
  trigger: string;
  started_at: string;
  window: [string | null, string | null];
  lock: string | null;
  requests: number;
  calls: number;
  stages: OpsStage[];
  finished_at?: string;
  seconds?: number;
  ok?: boolean;
  cost_usd?: number;
  /** The pipeline's own sentence, `▷` included. Rendered verbatim. */
  spend_line?: string;
  config?: string;
  notes?: string[];
};

export type OpsRunLog = { count: number; limit: number; rows: OpsRun[] };

/** `mijual:lock:pipeline`, live from Redis. An unreachable broker is
 * `state: "unknown"` **with its reason** — a fact the operator wants, not a
 * failed page. `since` comes from the open run row, never from the lock's TTL. */
export type OpsLock = {
  name: string;
  key: string;
  source: string;
  state: "free" | "held" | "unknown";
  reason?: string;
  holder?: string;
  ttl_seconds?: number;
  expires_at?: string;
  since?: string;
  run_id?: number;
  as_of?: string;
};

/** 가동 전 미결 — the still-open bullets of `docs/current/decisions.md`,
 * quoted. `available: false` when the doc is not on the service's disk. */
export type OpsDecisions = {
  available: boolean;
  reason?: string;
  doc?: string;
  path?: string;
  version?: string;
  count?: number;
  items?: { decision: string | null; title: string | null; text: string }[];
};

export type OpsOverview = {
  as_of: string;
  gates: OpsGateSummary;
  beat: OpsBeat;
  runs: OpsRunLog;
  lock: OpsLock;
  decisions: OpsDecisions;
};

/** One withheld field of an event: which field, and the reason code raw. */
export type OpsBlockedField = {
  field_key: string;
  gate_status: string;
  korean_name?: string;
  reason_code?: string;
  reason_ko?: string;
};

export type OpsWithdrawn = {
  event_id: number;
  corp_code: string;
  corp_name: string | null;
  rights_type: string;
  rcept_no: string | null;
  /** The product's own 철회 sentence for this rights type. */
  notice_ko: string | null;
  /** The evidence line the gate run wrote, verbatim. */
  note: string | null;
  /** Gate-passing fields that will never render: the notice replaces the body. */
  gate_passed_unrendered: number;
  blocked: OpsBlockedField[];
  dart_url?: string;
};

export type OpsGateQueue = {
  as_of: string;
  basis: { stored_rows: number; distinct_rows: number; duplicates: number; key: string };
  reasons: OpsReason[];
  events: OpsEvents;
  withdrawn: { count: number; rows: OpsWithdrawn[] };
};

/** One stored gate verdict. A blocked row usually carries **no** `quote` and no
 * `span`: both keys are absent, and 「없음」 is the state the panel renders. */
export type OpsGateRow = {
  id: number;
  rcept_no: string | null;
  event_id: number;
  rights_type: string | null;
  corp_code: string;
  corp_name: string | null;
  field_key: string;
  gate_status: string;
  status: string | null;
  span_status: string | null;
  exposable: boolean;
  korean_name?: string;
  reason_code?: string;
  reason_ko?: string;
  gate_note?: string;
  value_summary?: string;
  quote?: string;
  span?: [number, number];
  dart_url?: string;
};

export type OpsGateRows = {
  count: number;
  limit: number;
  offset: number;
  rows: OpsGateRow[];
};

/** One judged bucket. Rates are exact decimal **strings** with their n beside
 * them — R7 forbids a rate quoted without its decomposition. */
export type OpsBucket = {
  judged: number;
  correct: number;
  partial: number;
  wrong: number;
  skipped: number;
  unlabelled: number;
  strict?: string;
  lenient?: string;
  interval?: [string, string];
  over_block_rate?: string;
  /** A ▷ projection, served only beside the rate it came from. */
  over_blocked_estimate?: string;
};

export type OpsFieldScore = {
  field_key: string;
  korean_name: string;
  shown: OpsBucket;
  blocked: OpsBucket;
  corpus_total: number;
  corpus_blocked: number;
  corpus_reasons: OpsReason[];
  block_rate?: string;
};

/** The evalset report, read from its **frozen JSON artifacts** (never the DB).
 * `judged_by` is what R7 forbids rendering the headline without. */
export type OpsEvalset =
  | { available: false; reason: string }
  | {
      available: true;
      sample: {
        units: number;
        rows: number;
        seed: number;
        generated_at: string;
        labelled: number;
        coverage: Record<string, number>;
      };
      shown: OpsBucket;
      blocked: OpsBucket;
      fields: OpsFieldScore[];
      correction_recall: Record<string, number>;
      hard_cases: {
        hard_case: string;
        corp_name: string;
        rcept_no: string;
        field_ko: string;
        label: string;
        dart_url: string;
      }[];
      /** `mijual.evalset report`'s exact output. */
      markdown: string;
      judged_by?: { judge: string; basis: string; imported_at: string };
    };

export type OpsSpend = {
  llm: {
    /** `"cumulative"` — labelled, because R7 forbids showing it as a daily figure. */
    window: string;
    calls: number;
    failures: number;
    tokens: number;
    cost_usd: string;
    /** `▷ $2.7897` — the pipeline's own format. */
    cost_line: string;
    by_model: { model: string; calls: number; tokens: number }[];
    since?: string;
    until?: string;
  };
  dart: {
    window: string;
    quota: { requests_per_day: number; source: string };
    measured_from: string;
    days: { date: string; requests: number; calls: number; runs: number }[];
  };
};

export type OpsAccuracy = { as_of: string; evalset: OpsEvalset; spend: OpsSpend };

/**
 * One page from the conversation port (`mijual.web.conversations`).
 *
 * **P6 owns the row's columns**, so a row is an open mapping here rather than a
 * shape this build invented for storage that does not exist yet (the same reason
 * §6.3 forbids pre-implementing vocky's field names). `next_cursor` is absent —
 * never null — at the end of the list.
 */
export type OpsPage = {
  count: number;
  rows: Record<string, unknown>[];
  next_cursor?: string;
};

/** 독자 계정 — 최소 열람: a portfolio **count**, never its contents, and no
 * mention of the password. `sample_loaded` has **no backing fact in P5** and is
 * therefore absent rather than `false` (`P5.S9` note 8, an open question). */
export type OpsAccount = {
  id: number;
  email: string;
  created_at: string;
  holdings: number;
  notifications: { lead_days: number[]; stored: boolean };
  sample_loaded?: boolean;
};

export type OpsUsers = {
  accounts: { count: number; limit: number; offset: number; rows: OpsAccount[] };
  /** The 익명 세션 half — **a second independent read**, never a join. */
  sessions: OpsPage;
};

/**
 * vocky 관찰 뷰 — one page of the operator's vocky feedback, proxied server-side
 * (`mijual.web.vocky`; the shape §6.3 delegated to the build and `P5.S18`
 * decided against vocky's running product).
 *
 * **`fields` is served, not hard-coded here.** It is the decided field set in the
 * table's own order — vocky's own English key names, which §6.1 signs as the
 * honest rendering for identifiers on an operator surface — so widening it later
 * needs no frontend change and this file invents no vocky field name.
 *
 * `count` is **this page's** row count. vocky's list surface returns a keyset
 * page and no total, so there is no total to state and none is invented.
 */
export type OpsVocky = {
  as_of: string;
  /** `unconfigured` = 연결 전 (no base/key); `unreachable` = vocky did not
   * answer — both render a state, never a fabricated row. */
  state: "ok" | "unconfigured" | "unreachable";
  source: { endpoint: string; base?: string };
  fields: string[];
  count: number;
  rows: Record<string, unknown>[];
  next_cursor?: string;
  /** Raw English exception name, and the HTTP status when there was one. */
  reason?: string;
  status?: number;
};

/**
 * 의견 보내기's receipt (R8, `POST /feedback`).
 *
 * `request_id` is **vocky's own** handle, passed through by this API and rendered
 * as the 접수 번호; nothing on either side mints one. `accepted_at` is absolute
 * KST like every other instant this API serves, and it is absent rather than
 * `null` when vocky did not send one — the surface renders only the number.
 */
export type FeedbackReceipt = { request_id: string; accepted_at?: string };

/**
 * One company a `/ask` start card names, resolved from the corpus **on the
 * request that rendered the card** (`GET /ask/start-cards`, `P11.F1`).
 *
 * The operator rejected fixed companies at P11's acceptance gate — a card whose
 * filing has aged out is a dead question on the first screen a reader meets — so
 * the server picks whoever can answer that card's own shape today. **No Korean
 * arrives in this payload:** the sentence is a template in
 * `components/ask/copy.ts` with a company slot, and everything here is
 * provenance for the slot it fills (`filings` = how many filings of that family
 * the issuer has, `dday`/`rcept_no` = which ① the 계산 card will end up reading).
 */
export type AskStartCardPick = {
  corp_name: string;
  corp_code: string;
  filings?: number;
  rcept_no?: string | null;
  dday?: string | null;
  days?: number | null;
};

/**
 * The two derived start cards. A slot is **`null`** when today's corpus offers
 * no company that could answer it, and the surface then falls back to that
 * card's static sentence rather than drawing a grid with a hole in it.
 */
export type AskStartCards = {
  reference: string;
  search_events: AskStartCardPick | null;
  calculate: AskStartCardPick | null;
};
