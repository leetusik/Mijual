import {
  FEEDBACK_EMAIL_KO,
  FEEDBACK_TEXT_KO,
  FEEDBACK_THREAD_KO,
  FEEDBACK_TIME_KO,
  FILTER_REFUSAL_KO,
  LAST_ACTIVITY_KO,
  LAST_SCOPE_KO,
  LOG_ANSWER_KO,
  LOG_EVIDENCE_KO,
  LOG_QUESTION_KO,
  LOG_QUOTE_KO,
  LOG_SCOPE_KO,
  LOG_SESSION_KO,
  LOG_TIME_KO,
  QUESTIONS_KO,
  REFUSALS_KO,
  SESSION_HASH_KO,
} from "./copy";

/**
 * The columns 대화 로그 · 익명 세션 · 피드백 render, and the keys they read.
 *
 * **The Korean is signed; the keys are a convention, and the difference matters.**
 * R7 fixes each table's *columns* (build-prompt §대화 로그 / §사용자 /
 * §save_feedback), so the labels below are transcriptions. The *storage* is
 * P6's: `mijual.web.conversations` deliberately types a row as a plain mapping
 * "so P6 can serve the fields R7 lists … without this module having to know them
 * before they exist", and P5 stores no conversation at all.
 *
 * So this file states what the panel reads, in three tiers of certainty:
 *
 * 1. **`session_hash`, `kind`, `refusal_category` are already the API's own**
 *    names — they are `P5.S9`'s query parameters (`/ops/conversations?kind=…`),
 *    so using them here invents nothing.
 * 2. The rest are the panel's expectation, recorded for P6 to implement or to
 *    replace. They are the R7 column list in `snake_case`, nothing cleverer.
 * 3. **A served key this file does not know is still rendered** (see
 *    `extraKeys`), so a P6 that names things differently shows its data rather
 *    than a table of blanks — and nothing is silently hidden from the operator.
 *
 * Today every one of these tables is empty, which is the honest state of a build
 * with no conversation storage: an honest `0건`, never a 「준비 중」 nobody signed.
 */

export type Column = { key: string; label: string };

/** 스키마 (R6 계약과 정합): 세션 = 익명 해시, 시각 KST, 범위 (이벤트 rcept_no 또는
 * 전체), 질문, 답변/거절, 거절 카테고리, 근거 rcept_no 목록, 인용 칩 원문. */
export const LOG_COLUMNS: Column[] = [
  { key: "session_hash", label: LOG_SESSION_KO },
  { key: "at", label: LOG_TIME_KO },
  { key: "scope", label: LOG_SCOPE_KO },
  { key: "question", label: LOG_QUESTION_KO },
  { key: "kind", label: LOG_ANSWER_KO },
  { key: "refusal_category", label: FILTER_REFUSAL_KO },
];

/** The expanded row — 대화 재생: 저장분 그대로 (버블 + 거절 가족 문장 + 근거 칩 +
 * DART 링크). The reply, its evidence and the quotes the chips carried. */
export const LOG_DETAIL_COLUMNS: Column[] = [
  { key: "answer", label: LOG_ANSWER_KO },
  { key: "evidence", label: LOG_EVIDENCE_KO },
  { key: "quotes", label: LOG_QUOTE_KO },
];

/** 익명 세션 — 세션 해시 · 최근 활동 KST · 질문 수 · 거절 수 · 마지막 범위. */
export const SESSION_COLUMNS: Column[] = [
  { key: "session_hash", label: SESSION_HASH_KO },
  { key: "last_activity", label: LAST_ACTIVITY_KO },
  { key: "questions", label: QUESTIONS_KO },
  { key: "refusals", label: REFUSALS_KO },
  { key: "last_scope", label: LAST_SCOPE_KO },
];

/** save_feedback 대기열 — 시각 KST · 의견 텍스트 · 답장 이메일 (선택) · 원 대화
 * 링크 (세션 해시로). */
export const FEEDBACK_COLUMNS: Column[] = [
  { key: "at", label: FEEDBACK_TIME_KO },
  { key: "text", label: FEEDBACK_TEXT_KO },
  { key: "email", label: FEEDBACK_EMAIL_KO },
  { key: "session_hash", label: FEEDBACK_THREAD_KO },
];

/** Keys a row carries that the column list does not name — rendered raw, so a
 * P6 row is never partly invisible. */
export function extraKeys(rows: Record<string, unknown>[], columns: Column[]): string[] {
  const known = new Set(columns.map((column) => column.key));
  const seen = new Set<string>();
  for (const row of rows) {
    for (const key of Object.keys(row)) if (!known.has(key)) seen.add(key);
  }
  return [...seen];
}

/** One cell, printed as the row stored it — an array joined, everything else as
 * text. Nothing is reformatted: this panel quotes its source. */
export function cellText(value: unknown): string {
  if (value === null || value === undefined) return "";
  if (Array.isArray(value)) return value.map((item) => cellText(item)).join(" · ");
  if (typeof value === "object") return JSON.stringify(value);
  return String(value);
}
