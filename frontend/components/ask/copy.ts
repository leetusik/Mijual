/**
 * Every Korean string the AI 질문 surface renders, and where each one comes from.
 *
 * Same rule and same shape as `lib/copy.ts` and `components/chrome/copy.ts`:
 * **nothing here is invented**, every constant carries the round and section it
 * was transcribed from, and a string with no citation does not belong in this
 * file. Inventing a Korean sentence is a design change (P6 note 17 — P5 shipped
 * an English framework 404 rather than write one).
 *
 * Two sources, both read-only:
 *
 * - `docs/reference/design/rounds/06-explain/output/build-prompt.md` — the
 *   binding contract (§Surfaces · §Agent · §인라인 인용 · §SSE · §거절 ·
 *   §세션+저장 · §의견·문의 · §런처 마크);
 * - `…/output/result.md` — the round record (§Proposed copy · §Agent
 *   capabilities · §This-session revisions).
 *
 * **The agent's own words are not here.** The 도구 행 strings, the five refusal
 * sentences and the 의견 confirmation are composed server-side
 * (`src/mijual/agent/copy.py`, transcribed there with the same convention) and
 * arrive on the wire; the surface renders them **verbatim** and never restates
 * them. A string this file duplicated would be a second copy of a signed
 * sentence, and the two could drift.
 *
 * ## Two strings this slice reuses rather than invents, flagged for `P6.S7`
 *
 * R6 signs no label for the composer's idle send button and no accessible name
 * for the question field. Per the phase rule (「reuse the nearest signed one and
 * flag it」) the button takes R6-2's own free-input affordance 「직접 질문 입력 →」
 * and the field takes the surface's signed name 「AI 질문」. Both are recorded in
 * `works/phases/active/P6/phase.md` for `P6.S7`/`P6.REVIEW` to confirm.
 */

import { ASK_LABEL_KO, BOARD_LABEL_KO, STOCKS_LABEL_KO } from "@/components/chrome/copy";
import type { AskScope } from "@/lib/ask";

export { ASK_LABEL_KO, BOARD_LABEL_KO, STOCKS_LABEL_KO };

// ---------------------------------------------------------------------------
// 인트로 (result.md §Proposed copy)
// ---------------------------------------------------------------------------

/** 에이전트 인트로, verbatim. The same three sentences `mijual.agent.copy`
 * keeps beside the agent's promise; this is the surface that prints them. */
export const AGENT_INTRO_KO =
  "검증을 통과한 공시에 대해서만 답합니다. 모든 답에는 원문 인용이 붙습니다. " +
  "계산은 하지 않습니다 — 계산은 내 종목 조회가 합니다.";

/**
 * 세션·저장 (R6-6 개정), verbatim — and **the exact wording is the point**.
 *
 * The round replaced its own earlier copy when server-side storage landed:
 * 「저장 이력 없음」 and 「탭을 닫으면 사라집니다」 are **forbidden** because they
 * became false, and `security` restates the ban. This sentence says both true
 * things at once — the reader is anonymous and unlimited, and the conversation is
 * kept anonymously for 품질 점검.
 */
export const ANONYMITY_KO =
  "완전 익명 — 로그인도, 질문 수 제한도 없습니다 · 대화는 익명으로 저장됩니다 (품질 점검용)";

// ---------------------------------------------------------------------------
// 범위 (build-prompt §범위 모델)
// ---------------------------------------------------------------------------

/** 「그 외 = `범위: 전체 공시`」. The same words `mijual.web.conversationstore`
 * stores as `SCOPE_ALL_KO`, so the screen and the log say one thing. */
export const SCOPE_ALL_KO = "범위: 전체 공시";

/** 「헤더 칩 `범위: {종목} · {rcept_no}`」 — the format, filled by the event the
 * widget was opened on. */
export function scopeLabel(scope: AskScope | null): string {
  return scope ? `범위: ${scope.name} · ${scope.rcept_no}` : SCOPE_ALL_KO;
}

// ---------------------------------------------------------------------------
// 헤더 (build-prompt §Surfaces · result.md §This-session revisions ②)
// ---------------------------------------------------------------------------

/** The header's Lucide `external-link` button: 「위젯 헤더 ⤢ 폐기 → Lucide
 * external-link 「AI 질문 페이지 →」」. Rendered as the icon's accessible name —
 * the icon is the signed affordance and the words are what it means. */
export const ASK_PAGE_LINK_KO = "AI 질문 페이지 →";

/** The header's close control. The record writes the glyph itself (「+ ×, 각
 * 28px 정사각」) and signs no 닫기 label — the same reason the mobile sheet's
 * button keeps 메뉴 and carries its state on `aria-expanded`. */
export const CLOSE_GLYPH = "×";

// ---------------------------------------------------------------------------
// SSE 상태 (build-prompt §SSE · result.md §Proposed copy)
// ---------------------------------------------------------------------------

/** 「idle → **답변 준비 중** (버튼 텍스트 교체 + disabled — 스피너·점 금지)」.
 * §Proposed copy writes it with the ellipsis, which is the copy source. */
export const PREPARING_KO = "답변 준비 중…";

/** 「스트리밍 (… 중지 버튼)」 — the same button, its text replaced. */
export const STOP_KO = "중지";

/** 「중단/오류 (부분 답변 유지 — 지우기 금지, `--ink-2`로 감쇠; inset 행 "연결이
 * 끊겼습니다 — 답변이 여기서 중단되었습니다." + 재시도)」, verbatim.
 *
 * This is the **only** sentence R6 writes for a turn that did not finish, so it
 * is what the surface shows for all of them: a 중지 the reader pressed, a stream
 * cut on the way, a typed `error` terminal, and a pre-stream refusal (429 and the
 * rest arrive as the ordinary envelope with no Korean at all — `P6.S4` note 21).
 * Writing a second sentence for any of those would be inventing copy. */
export const DISCONNECTED_KO = "연결이 끊겼습니다 — 답변이 여기서 중단되었습니다.";

export const RETRY_KO = "재시도";

// ---------------------------------------------------------------------------
// 인라인 인용 + 푸터 (build-prompt §인라인 인용)
// ---------------------------------------------------------------------------

/** 「API-tier 사실 (quote 없음): 블록에 "DART 공시 API 수치 — 원문 스팬 없음,
 * 접수번호가 인용 핸들" + 링크 (R3 규칙)」, verbatim. */
export const API_TIER_KO = "DART 공시 API 수치 — 원문 스팬 없음, 접수번호가 인용 핸들";

/** 「verbatim quote + `DART 원문 {rcept_no} ↗`」 — the citation block's own link,
 * and the same words the 갈 곳 링크 uses for 「DART 원문 rcept_no verbatim」. */
export function dartSourceLabel(rceptNo: string): string {
  return `DART 원문 ${rceptNo} ↗`;
}

/** 「답변 푸터: `근거 N건 · {rcept_no} · {생성시각 KST}`」. 「근거 N건」 is also in
 * §Proposed copy. Several 근거 are printed with the format's own `·`. */
export function evidenceCount(count: number): string {
  return `근거 ${count}건`;
}

/** 「컨텍스트 링크 (필드로 이동 / 이벤트 상세 / 다시 질문)」 — the footer's own
 * action, which puts the reader back in the question field. */
export const REASK_KO = "다시 질문";

/** 「③ 갈 곳 링크 (DART 원문 rcept_no verbatim · **이벤트 상세** · 내 종목 조회)」
 * (§거절), and the same destination the footer's context links name. */
export const EVENT_DETAIL_KO = "이벤트 상세";

// ---------------------------------------------------------------------------
// 의견 (build-prompt §의견·문의 · result.md §Proposed copy)
// ---------------------------------------------------------------------------

/**
 * 「의견: 자유 텍스트 → 자동 저장 (`save_feedback`), 확인 "의견을 저장했습니다 —
 * 운영자가 확인합니다."」, verbatim — and **this file is where it is rendered
 * from**, not the agent.
 *
 * `mijual.agent.tools.save_feedback`'s own docstring fixes the split: 「the tool
 * writes no Korean sentence about it, because R6 signs the confirmation copy and
 * the surface renders it」, and `mijual.agent.copy` keeps the string with the note
 * 「the surface renders it (`P6.S5`), the agent never writes it as prose」. So the
 * surface prints it off the tool's own `ok`, after the 의견 저장 행 — a fact about
 * a write that happened, never a sentence a model chose to say.
 *
 * 「실패 시에만 재시도 행」: a failed save needs nothing added here, because the
 * tool's own row already **is** 「의견 저장 → 재시도」.
 */
export const FEEDBACK_SAVED_KO = "의견을 저장했습니다 — 운영자가 확인합니다.";

/** The tool whose row that confirmation follows (`mijual.agent.tools`). */
export const FEEDBACK_TOOL = "save_feedback";

// ---------------------------------------------------------------------------
// 입력 (R6-2 · reused, flagged above)
// ---------------------------------------------------------------------------

/** R6-2: 「자유 입력은 한 단계 뒤 ("직접 질문 입력 →")」 — the signed affordance for
 * typing your own question, reused as the composer's idle button text. */
export const ASK_SUBMIT_KO = "직접 질문 입력 →";
