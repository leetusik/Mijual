/**
 * The one client for the 미주알 API.
 *
 * Every route path is **hard-coded here** (`P5.S3`'s note): the service exposes
 * no prefix and no discovery document a client should follow, and a path built
 * out of interpolated fragments is how a surface ends up calling an endpoint the
 * contract does not have. Adding a surface means adding a function here, with the
 * response type from `./types`.
 *
 * ## Three decisions this module encodes
 *
 * **Same origin, therefore no CORS.** Calls go to `/api/…` on this app's own
 * origin and `next.config.ts` rewrites them to the FastAPI service. `P5.S1` left
 * "the CORS/origin question" to this slice and the answer is that the question
 * does not arise: the service configures no CORS middleware and grants no
 * preflight, which is exactly what `P5.S7`'s CSRF design relies on.
 *
 * **`X-Mijual-CSRF` on every mutating call.** `mijual.web.csrf` refuses any
 * `POST`/`PUT`/`PATCH`/`DELETE` without the header — *before* the route runs —
 * and accepts any non-empty value. Nothing is minted, stored or rotated: the
 * header's protection is that a cross-origin page cannot set a custom header
 * without a preflight the service does not grant. The wrapper sets it once, so
 * no call site can forget.
 *
 * **`credentials: "include"`.** The session cookie `mj_session` is `HttpOnly` ·
 * `SameSite=Lax` · `Path=/`, and 내 포트폴리오 is the product's only gated
 * surface; every other route answers 200 uncookied.
 */

import type {
  Account,
  AskStartCards,
  AuthState,
  BoardResponse,
  BoardSummary,
  CorrectionStory,
  EventDetail,
  FeedbackReceipt,
  Holding,
  Notifications,
  OpsAccuracy,
  OpsGateQueue,
  OpsGateRows,
  OpsLock,
  OpsOverview,
  OpsPage,
  OpsUsers,
  OpsVocky,
  Portfolio,
  RightsType,
  StockLookup,
  StockPage,
  StockSuggestions,
} from "./types";

/** The client-side base. Same origin by default; `next.config.ts` proxies it. */
const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "/api";

/** Server components have no origin to be relative to — and no proxy to go
 * through, since they run beside the service. Same value `next.config.ts` uses. */
const SERVER_ORIGIN = process.env.MIJUAL_API_ORIGIN ?? "http://localhost:8010";

/** `mijual.web.csrf.CSRF_HEADER`. Any non-empty value is accepted. */
export const CSRF_HEADER = "X-Mijual-CSRF";
const CSRF_VALUE = "1";

const SAFE_METHODS = new Set(["GET", "HEAD", "OPTIONS"]);

/** The 원문 on DART. The one link shape the whole product uses. */
export function dartUrl(rceptNo: string): string {
  return `https://dart.fss.or.kr/dsaf001/main.do?rcpNo=${rceptNo}`;
}

/**
 * A failure the API reported in its envelope:
 * `{"error": {code, message, message_ko?, fields?}}`.
 *
 * `code` is the stable English token a surface branches on. `message` is
 * developer-facing English and **must never be rendered to a reader** — the
 * signed design writes state copy, not error copy, so the Korean for a failure is
 * the surface's own (`P5.S15` renders 불일치 / 중복 가입 / 8자 미만 from the
 * code). `message_ko` appears only where the product already owns that string.
 */
export class ApiError extends Error {
  readonly status: number;
  readonly code: string;
  readonly messageKo?: string;
  readonly fields?: unknown;

  constructor(
    status: number,
    body: { code?: string; message?: string; message_ko?: string; fields?: unknown },
  ) {
    super(body.message ?? `HTTP ${status}`);
    this.name = "ApiError";
    this.status = status;
    this.code = body.code ?? "http_error";
    this.messageKo = body.message_ko;
    this.fields = body.fields;
  }
}

function resolve(path: string): string {
  if (API_BASE.startsWith("http")) return `${API_BASE}${path}`;
  // On the client the relative base goes through the rewrite; on the server
  // there is nothing to be relative to, so talk to the service directly.
  return typeof window === "undefined" ? `${SERVER_ORIGIN}${path}` : `${API_BASE}${path}`;
}

export type RequestInitLike = Omit<RequestInit, "body" | "method"> & {
  method?: string;
  /** Serialized as JSON. */
  json?: unknown;
};

/**
 * One request, one envelope.
 *
 * A gated read from a **server** component must forward the incoming request's
 * `cookie` header itself (`headers: { cookie }`): `credentials` is a browser
 * concept and does nothing in Node.
 */
export async function request<T>(path: string, init: RequestInitLike = {}): Promise<T> {
  const method = (init.method ?? "GET").toUpperCase();
  const headers = new Headers(init.headers);
  headers.set("Accept", "application/json");
  if (init.json !== undefined) headers.set("Content-Type", "application/json");
  if (!SAFE_METHODS.has(method)) headers.set(CSRF_HEADER, CSRF_VALUE);

  const response = await fetch(resolve(path), {
    ...init,
    method,
    headers,
    credentials: "include",
    body: init.json !== undefined ? JSON.stringify(init.json) : undefined,
  });

  if (response.status === 204) return undefined as T;

  const text = await response.text();
  const parsed: unknown = text ? JSON.parse(text) : null;

  if (!response.ok) {
    const envelope =
      parsed && typeof parsed === "object" && "error" in parsed
        ? (parsed as { error: Record<string, unknown> }).error
        : {};
    throw new ApiError(response.status, envelope as ConstructorParameters<typeof ApiError>[1]);
  }

  return parsed as T;
}

// ---------------------------------------------------------------------------
// 관제 현황판 / 이벤트 상세 (P5.S3)
// ---------------------------------------------------------------------------

/** Every landing number in one object, so no two readouts can disagree. */
export const getBoardSummary = (init?: RequestInitLike) =>
  request<BoardSummary>("/board/summary", init);

/** `rights` filters the rows; the tab **counts stay whole-board**. */
export const getBoard = (rights?: RightsType, init?: RequestInitLike) =>
  request<BoardResponse>(rights ? `/board?rights=${rights}` : "/board", init);

/** Keyed by `rcept_no`, resolved against every stored version. A non-renderable
 * event answers 404 — never a page explaining why it is not exposed. */
export const getEvent = (rceptNo: string, init?: RequestInitLike) =>
  request<EventDetail>(`/events/${rceptNo}`, init);

export const getCorrections = (rceptNo: string, init?: RequestInitLike) =>
  request<CorrectionStory>(`/events/${rceptNo}/corrections`, init);

// ---------------------------------------------------------------------------
// 내 종목 조회 (P5.S4)
// ---------------------------------------------------------------------------

/** A miss comes back `200 {found: false}` and says nothing else — no reason, no
 * candidate list, no near-miss. **No holding count is ever sent**: these
 * endpoints serve factors, and the N주 math happens in the browser. */
export const lookupStock = (query: string, init?: RequestInitLike) =>
  request<StockLookup>(`/stocks?q=${encodeURIComponent(query)}`, init);

/** The same page by stable handle. An unknown code **is** a 404. */
export const getStock = (corpCode: string, init?: RequestInitLike) =>
  request<StockPage>(`/stocks/${corpCode}`, init);

/**
 * Candidates for a query still being typed (`P7.S4`, operator item 2).
 *
 * Read-only, anonymous, and **only `q`** — the same reason `lookupStock` takes no
 * holding count. Nothing matching is `200 {candidates: []}`, so a caller branches
 * on the list's length and never on a status. Pass `init.signal`: the typeahead
 * aborts the previous keystroke's request on every new one, and an aborted
 * `fetch` rejects with an `AbortError` the caller is expected to swallow.
 */
export const suggestStocks = (query: string, init?: RequestInitLike) =>
  request<StockSuggestions>(`/stocks/suggest?q=${encodeURIComponent(query)}`, init);

// ---------------------------------------------------------------------------
// 계정 (P5.S7)
// ---------------------------------------------------------------------------

export const signup = (email: string, password: string) =>
  request<{ account: Account }>("/auth/signup", { method: "POST", json: { email, password } });

export const login = (email: string, password: string) =>
  request<{ account: Account }>("/auth/login", { method: "POST", json: { email, password } });

export const logout = () => request<AuthState>("/auth/logout", { method: "POST" });

/** Anonymous is a **result, not a 401**: `{authenticated: false}`. The chrome can
 * call this on every page load without filling a console with errors. */
export const getAuthState = (init?: RequestInitLike) => request<AuthState>("/auth/me", init);

/** Answers identically whether or not the address exists; the link travels only
 * through the mailer, never in this response. */
export const requestPasswordReset = (email: string) =>
  request<{ requested: true }>("/auth/reset/request", { method: "POST", json: { email } });

export const confirmPasswordReset = (token: string, password: string) =>
  request<{ account: Account }>("/auth/reset/confirm", {
    method: "POST",
    json: { token, password },
  });

/** 수신 주소 = the account email, so 변경 edits the account. */
export const changeEmail = (email: string) =>
  request<{ account: Account }>("/auth/account", { method: "PATCH", json: { email } });

export const deleteAccount = () =>
  request<{ deleted: true; authenticated: false }>("/auth/account", { method: "DELETE" });

// ---------------------------------------------------------------------------
// 의견 보내기 (P8.S3, R8)
// ---------------------------------------------------------------------------

/**
 * One reader message, forwarded server-side to vocky.
 *
 * The browser talks to **this app's own origin** and nothing else — R8 keeps the
 * `vk_` credential in the server's `.env`, so there is no third-party endpoint,
 * no third-party script and no key in this bundle. `channel` is the entry point
 * the surface was opened from (footer = `web`, mobile sheet = `mobile`), and
 * `session` is the anonymous AI 질문 tab handle **only when the browser already
 * had one**; no identifier is minted for a 의견.
 *
 * Failures arrive as an `ApiError` whose `code` says whether 다시 시도 is
 * offered: `feedback_rejected` / `feedback_unconfigured` cannot be fixed by a
 * reader (the envelope also carries `retryable: false`), while
 * `feedback_unavailable` may pass on a second try.
 */
export const sendFeedback = (
  message: string,
  channel: "web" | "mobile",
  options: { session?: string; signal?: AbortSignal } = {},
) =>
  request<FeedbackReceipt>("/feedback", {
    method: "POST",
    json: { message, channel, session_id: options.session },
    signal: options.signal,
  });

/** The failure codes above, in one place, so the surface branches on a token
 * rather than on a status. */
export const FEEDBACK_NO_RETRY_CODES = ["feedback_rejected", "feedback_unconfigured"];

// ---------------------------------------------------------------------------
// 내 포트폴리오 (P5.S8) — the product's only gated surface
// ---------------------------------------------------------------------------

export const getPortfolio = (init?: RequestInitLike) =>
  request<Portfolio>("/portfolio", init);

/** Anonymous and read-only. Carries no account fact — no address, no 알림 설정,
 * no `claimed` key. */
export const getSamplePortfolio = (init?: RequestInitLike) =>
  request<Portfolio>("/portfolio/sample", init);

/** A duplicate 담기 is refused (`holding_exists` 409), never merged or replaced:
 * merging invents a count the reader never typed and replacing discards one they
 * did. Route a repeat to the row's inline 수정. */
export const addHolding = (corpCode: string, shares: number) =>
  request<{ holding: Holding }>("/portfolio/holdings", {
    method: "POST",
    json: { corp_code: corpCode, shares },
  });

export const updateHolding = (holdingId: number, shares: number) =>
  request<{ holding: Holding }>(`/portfolio/holdings/${holdingId}`, {
    method: "PATCH",
    json: { shares },
  });

export const deleteHolding = (holdingId: number) =>
  request<{ deleted: true }>(`/portfolio/holdings/${holdingId}`, { method: "DELETE" });

/** 챙긴 돈: the reader's own assertion, keyed on the 증권발행실적보고서's own
 * `rcept_no`. It stores no amount and reaches no aggregate. */
export const setClaim = (rceptNo: string, claimed: boolean) =>
  request<{ rcept_no: string; claimed: boolean }>(`/portfolio/claims/${rceptNo}`, {
    method: claimed ? "PUT" : "DELETE",
  });

export const getNotifications = (init?: RequestInitLike) =>
  request<Notifications>("/portfolio/notifications", init);

/** `[]` persists and means no mail — it is the only off switch R5 ships. */
export const saveNotifications = (leadDays: number[]) =>
  request<Notifications>("/portfolio/notifications", {
    method: "PUT",
    json: { lead_days: leadDays },
  });

// ---------------------------------------------------------------------------
// 운영 관제 (P5.S9) — the operator's own door and its read-only tabs
// ---------------------------------------------------------------------------
//
// A second credential, not a second role: `mj_ops` is its own cookie and the
// reader's `mj_session` cannot open any of this (nor the reverse). Nine of the
// twelve routes are `GET` and the three that are not touch only the operator's
// own session row — §6.5 전 화면 읽기 전용.
//
// **Nothing in the reader chrome may link to these.** They are called from
// `app/ops/**` only, and `components/ops/routes.ts` is where the paths live so
// a reader surface cannot pick one up from `lib/routes.ts` by accident.

/** The door asks this on load: not authenticated is a **result**, not a 401. */
export const getOpsSession = (init?: RequestInitLike) =>
  request<{ authenticated: boolean }>("/ops/session", init);

/** One failure for every cause — the 401 body says only `invalid_credentials`,
 * and 「자격증명이 올바르지 않습니다」 is the client's own signed line. */
export const opsLogin = (id: string, password: string) =>
  request<{ authenticated: true }>("/ops/login", { method: "POST", json: { id, password } });

export const opsLogout = () =>
  request<{ authenticated: false }>("/ops/logout", { method: "POST" });

/** 개요 — the tiles, the beat schedule, the run log, the lock and 가동 전 미결.
 * The 「실행 기록 없음」 row is the **client's** join of `beat.entries[].due` with
 * `runs.rows`: the backend states both facts and fabricates neither. */
export const getOpsOverview = (init?: RequestInitLike) =>
  request<OpsOverview>("/ops/overview", init);

/** The lock chip alone, for the ops bar on every tab (`P5.S17`). */
export const getOpsLock = (init?: RequestInitLike) => request<OpsLock>("/ops/lock", init);

export const getOpsGates = (init?: RequestInitLike) =>
  request<OpsGateQueue>("/ops/gates", init);

/** 행 검사. Every filter is one the panel renders; there is no query surface
 * beyond them. */
export const getOpsGateRows = (
  params: {
    field_key?: string;
    reason_code?: string;
    gate_status?: string;
    rcept_no?: string;
    limit?: number;
    offset?: number;
  } = {},
  init?: RequestInitLike,
) => request<OpsGateRows>(`/ops/gates/rows${opsQuery(params)}`, init);

export const getOpsAccuracy = (init?: RequestInitLike) =>
  request<OpsAccuracy>("/ops/accuracy", init);

/** 대화 로그. P5 stores no conversations, so this is an honest `0건` — not
 * 「준비 중」 and not a 404; P6 fills the same port with no route change. */
export const getOpsConversations = (
  params: {
    kind?: string;
    refusal_category?: string;
    session_hash?: string;
    cursor?: string;
    limit?: number;
  } = {},
  init?: RequestInitLike,
) => request<OpsPage>(`/ops/conversations${opsQuery(params)}`, init);

export const getOpsSessions = (
  params: { cursor?: string; limit?: number } = {},
  init?: RequestInitLike,
) => request<OpsPage>(`/ops/sessions${opsQuery(params)}`, init);

export const getOpsFeedback = (
  params: { cursor?: string; limit?: number } = {},
  init?: RequestInitLike,
) => request<OpsPage>(`/ops/feedback${opsQuery(params)}`, init);

/**
 * vocky 관찰 뷰 — the operator's vocky feedback, read **through the service**.
 *
 * The browser never talks to vocky: the `vk_` key is a server secret, and a
 * key that reached a client would be a key anyone could capture (or write) with.
 * The ceiling is vocky's own 100, not this panel's usual 200.
 */
export const getOpsVocky = (
  params: { cursor?: string; limit?: number } = {},
  init?: RequestInitLike,
) => request<OpsVocky>(`/ops/vocky${opsQuery(params)}`, init);

/** 사용자 — 독자 계정 **and** 익명 세션 in one response and **two independent
 * reads**: there is no key in either block that could be matched against the
 * other (계정↔대화 연결·조인·추정 매칭 금지, kept at the schema level). */
export const getOpsUsers = (
  params: { limit?: number; offset?: number } = {},
  init?: RequestInitLike,
) => request<OpsUsers>(`/ops/users${opsQuery(params)}`, init);

// ---------------------------------------------------------------------------
// AI 질문 (P6.S5) — the API's one streaming call, and the start screen's read
// ---------------------------------------------------------------------------

/**
 * The companies the `/ask` start cards name, **resolved on this request**
 * (`P11.F1`).
 *
 * Called from the `/ask` route's server component, never from the browser: the
 * start screen is the one surface that must never look empty, so the sentences
 * arrive with the HTML instead of appearing after a spinner. Pass
 * `cache: "no-store"` and a timeout signal — a card is only worth serving if it
 * is today's, and a slow API must degrade to the static fallback rather than
 * hold the page.
 */
export const getAskStartCards = (init?: RequestInitLike) =>
  request<AskStartCards>("/ask/start-cards", init);

//
// `POST /ask` answers `text/event-stream`, so it cannot go through `request()`:
// that helper reads the whole body before it returns, which is the one thing a
// stream must not do. What it *does* share is the three decisions at the top of
// this file — the hard-coded path, the CSRF header on an unsafe method, and
// `credentials: "include"` — so the ask call lives here beside every other one
// rather than growing a second fetch seam in a component.
//
// The contract (`mijual.web.routers.ask`): frame one is **always** `event:
// session` carrying the anonymous handle for `sessionStorage`; then the agent's
// own events (`tool_row` · `citation` · `text` · `refusal` · `links` ·
// `footer`); then **exactly one** terminal, `done` | `aborted` | `error`. A
// failure *before* the stream opens is the ordinary error envelope (429
// `rate_limited`, `invalid_question`, …) and therefore an `ApiError`; once the
// stream is open the only failure is the typed `error` terminal.
//
// **중지 has no endpoint.** The reader aborts the fetch, the consumer stops
// pulling, and the server's generator is closed — so the `AbortSignal` below is
// the whole stop mechanism.

/** `mijual.web.ask.ASK_PATH`. Hard-coded like every other path in this module. */
export const ASK_PATH = "/ask";

/** One earlier exchange, as prose. Chip numbering is per answer (R6-4), so
 * history carries no citations — the server caps it at the newest 8 turns. */
export type AskHistoryTurn = { question: string; answer: string };

/** `mijual.web.routers.ask.AskIn`. Every field but `question` is optional. */
export type AskBody = {
  question: string;
  /** 범위 = this event, as a 14-digit filing number. Junk is refused server-side
   * rather than ignored, because ignoring it would answer a different question. */
  scope_rcept_no?: string;
  /** This tab's anonymous handle, from an earlier turn's `session` frame. A
   * missing or malformed one is **replaced, not trusted** (`P6.S1`). */
  session?: string;
  history?: readonly AskHistoryTurn[];
};

/** One SSE frame: the `event:` name and its still-unparsed `data:` payload. */
export type SseFrame = { event: string; data: string };

/**
 * Split whatever has arrived so far into complete frames plus the remainder.
 *
 * Pure and buffer-in/buffer-out so the incremental case is the only case: a
 * chunk boundary can fall anywhere, including inside a Korean quote, and a
 * decoder that assumed one chunk = one frame would paint half a sentence. The
 * subset of the SSE grammar this implements is the subset the service writes
 * (`mijual.web.ask.sse_frame`): `event:` + one or more `data:` lines, terminated
 * by a blank line, with `\n` newlines and no ids or retry fields. A comment line
 * (`:`) is skipped, and `\r\n` is tolerated because a proxy may rewrite it.
 */
export function decodeSse(buffer: string): { frames: SseFrame[]; rest: string } {
  const text = buffer.replace(/\r\n/g, "\n");
  const blocks = text.split("\n\n");
  // The tail after the last blank line is by definition incomplete.
  const rest = blocks.pop() ?? "";
  const frames: SseFrame[] = [];

  for (const block of blocks) {
    let event = "message";
    const data: string[] = [];
    for (const line of block.split("\n")) {
      if (line === "" || line.startsWith(":")) continue;
      const colon = line.indexOf(":");
      const field = colon === -1 ? line : line.slice(0, colon);
      const value = colon === -1 ? "" : line.slice(colon + 1).replace(/^ /, "");
      if (field === "event") event = value;
      else if (field === "data") data.push(value);
    }
    if (data.length > 0) frames.push({ event, data: data.join("\n") });
  }

  return { frames, rest };
}

/**
 * One question, streamed frame by frame.
 *
 * Throws an {@link ApiError} for a **pre-stream** refusal (the ordinary
 * envelope) and yields nothing in that case; once the first frame is yielded the
 * turn can only end in a terminal frame or in the caller aborting `signal`.
 */
export async function* streamAsk(
  body: AskBody,
  init: { signal?: AbortSignal } = {},
): AsyncGenerator<SseFrame, void, undefined> {
  const response = await fetch(resolve(ASK_PATH), {
    method: "POST",
    headers: {
      Accept: "text/event-stream",
      "Content-Type": "application/json",
      [CSRF_HEADER]: CSRF_VALUE,
    },
    credentials: "include",
    body: JSON.stringify(body),
    signal: init.signal,
  });

  if (!response.ok) {
    const text = await response.text();
    let envelope: Record<string, unknown> = {};
    try {
      const parsed: unknown = text ? JSON.parse(text) : null;
      if (parsed && typeof parsed === "object" && "error" in parsed) {
        envelope = (parsed as { error: Record<string, unknown> }).error;
      }
    } catch {
      // A body that is not the envelope tells the surface nothing it may show:
      // the design writes state copy, not error copy. The status is the fact.
    }
    throw new ApiError(response.status, envelope as ConstructorParameters<typeof ApiError>[1]);
  }

  if (!response.body) {
    throw new ApiError(response.status, { code: "no_stream", message: "no response body" });
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  try {
    for (;;) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const { frames, rest } = decodeSse(buffer);
      buffer = rest;
      for (const frame of frames) yield frame;
    }
  } finally {
    // A consumer that stops pulling (중지, or a `break`) must not leave the
    // socket open: cancelling the reader is what closes the server's generator.
    await reader.cancel().catch(() => undefined);
  }
}

/** `{a: 1, b: undefined}` → `"?a=1"`. An unset filter is not sent at all. */
function opsQuery(params: Record<string, string | number | undefined>): string {
  const search = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== "") search.set(key, String(value));
  }
  const text = search.toString();
  return text ? `?${text}` : "";
}
