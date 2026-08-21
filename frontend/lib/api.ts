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
  AuthState,
  BoardResponse,
  BoardSummary,
  CorrectionStory,
  EventDetail,
  Holding,
  Notifications,
  Portfolio,
  RightsType,
  StockLookup,
  StockPage,
} from "./types";

/** The client-side base. Same origin by default; `next.config.ts` proxies it. */
const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "/api";

/** Server components have no origin to be relative to — and no proxy to go
 * through, since they run beside the service. Same value `next.config.ts` uses. */
const SERVER_ORIGIN = process.env.MIJUAL_API_ORIGIN ?? "http://localhost:8000";

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
