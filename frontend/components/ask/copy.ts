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
 * ## The two strings this file once reused rather than invented — one closed
 *
 * R6 signed no label for the composer's idle send button and no accessible name
 * for the question field, so per the phase rule (「reuse the nearest signed one
 * and flag it」) the button took R6-2's free-input affordance 「직접 질문 입력 →」
 * and the field took the surface's signed name 「AI 질문」.
 *
 * **R14 Q-C closed the first one**: the operator specified 「보내기」 in the round's
 * session, it is signed below as `SEND_KO`, and `ASK_SUBMIT_KO` went back to being
 * the strip's free-input chip and only that. The field's accessible name is still
 * the reuse it always was (`ASK_LABEL_KO`), and stays flagged.
 *
 * ## R14 also **retires** a string (finding 10)
 *
 * `API_TIER_KO` — R3's 「DART 공시 API 수치 — 원문 스팬 없음, 접수번호가 인용
 * 핸들」 — is gone: a span-less citation block is now the `DART 원문 {rcept_no} ↗`
 * link alone, because 스팬 and 인용 핸들 are our contract's vocabulary and the
 * link's existence is what that sentence was doing. This closes **P7 Q7①**, and
 * the retirement is registered in `docs/reference/design/grounding/copy-inventory.md`.
 */

import { ASK_LABEL_KO, BOARD_LABEL_KO, STOCKS_LABEL_KO } from "@/components/chrome/copy";

export { ASK_LABEL_KO, BOARD_LABEL_KO, STOCKS_LABEL_KO };

// ---------------------------------------------------------------------------
// 인트로 (result.md §Proposed copy)
// ---------------------------------------------------------------------------

/**
 * 에이전트 인트로 — **R16 §0 D1**, verbatim, superseding R6's three sentences.
 *
 * Each of the three said something that stopped being true this phase:
 * 「검증을 통과한 공시에 대해서만 답합니다」 the moment a greeting stopped being a
 * refusal (`P9.S4`), 「모든 답에는 원문 인용이 붙습니다」 the moment 인용 강제 became
 * a rule about 공시 사실 문장 only, and 「계산은 하지 않습니다」 the moment the
 * auditable calculator landed (`P9.S5`). D1 says what is still true, and says it
 * as a promise about the reader rather than about the machinery.
 *
 * `mijual.agent.copy.AGENT_INTRO_KO` holds the same sentence because that is
 * where the agent's own words live, but it is **not served**: the two surfaces
 * that print it print it from here, and no code compares the two.
 */
export const AGENT_INTRO_KO = "주주의 권리를 지키기 위해 공시를 근거로 질문에 답합니다.";

// ---------------------------------------------------------------------------
// 은퇴한 문자열 (R16 §0 폐기 — `P9.S10`, 2026-08-25)
//
// Four strings left this file with their call sites, and none of them is coming
// back as a rewrite: a retired sentence is retired, not restated.
//
// - **`ANONYMITY_KO`** 「완전 익명 — 로그인도, 질문 수 제한도 없습니다 · 대화는
//   익명으로 저장됩니다 (품질 점검용)」 (폐기 ⓐ) — removed from the widget's empty
//   thread and from the start screen. R6-5 은 **기능으로** 지켜진다: there is no
//   login, no history and no quota to declare, so the surface declares nothing.
//   R6-6's ban on 「저장 이력 없음」/「탭을 닫으면 사라집니다」 still stands — this
//   retirement removes a true sentence, it does not license a false one.
// - **`VERIFIED_ONLY_KO`** 「검증된 필드만 근거로 답합니다 — 모든 답에 원문 인용」
//   (폐기 ②) — the 340 레일's promise line went with the rail, and both halves of
//   it stopped being true this phase anyway (`P9.S4` 인용 강제 → 공시 사실 문장만,
//   `P9.S5` the auditable calculator). `AGENT_INTRO_KO` is the surviving promise.
// - **`SCOPE_ALL_KO` / `scopeLabel`** 「범위: {종목} · {rcept_no}」/「범위: 전체
//   공시」 (폐기 ①) — the chip and its × are gone from the header and the rail
//   both. The **state** stays (`lib/ask.ts`'s `scope`, and the server's own
//   `SCOPE_ALL_KO`, which is a different string: 「전체 공시」 without the label),
//   it is simply never drawn.
// - **`REASK_KO`** 「다시 질문」 (§2.7b 폐기) — the completed footer ends at
//   이벤트 상세; 재시도 stays, and only on an interrupted turn.
// ---------------------------------------------------------------------------

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
// 입력 (R14 Q-C · R6-2)
// ---------------------------------------------------------------------------

/**
 * 「보내기」 — the composer's idle button, **signed by R14 (2026-08-24, Q-C)** and
 * specified by the operator in that round's own session.
 *
 * It is the one string this round wrote for a control (its other nine are the
 * preset questions in `presets.ts`). The three-text machine R6 signed is
 * unchanged — 보내기 → 답변 준비 중… → 중지, one button whose text is replaced —
 * and this is the first text finally saying what pressing it does. R14 result.md
 * §Copy, and `build-prompt.md` §2.
 */
export const SEND_KO = "보내기";

/** R6-2: 「자유 입력은 한 단계 뒤 ("직접 질문 입력 →")」 — the signed affordance for
 * typing your own question.
 *
 * **R14 Q-C sent it back to its own place** and it is now used in exactly one:
 * the 질문 스트립's last chip, which opens the surface in the event's 범위 and
 * sends nothing (R6-2's presets-first order — 프리셋 먼저, 자유 입력 한 단계 뒤).
 * Its stint as the composer's idle button — a reuse this file flagged for `P6.S7`
 * — ended there: 「직접 질문 입력 →」 on the control that submits an already-typed
 * question told the reader to do what they had just done. */
export const ASK_SUBMIT_KO = "직접 질문 입력 →";

// ---------------------------------------------------------------------------
// 패널 카피 (result.md §Proposed copy) — the 질문 스트립 heading
// ---------------------------------------------------------------------------

/**
 * 「패널: "이 공시에 대해 질문"」, verbatim (result.md §Proposed copy).
 *
 * R6-1's first design put an inline **패널** on the event detail page; the final
 * revision replaced the panel with the widget + page pair and left 상세 with the
 * 질문 스트립 (「상세의 질문 스트립(프리셋 칩 …)은 위젯을 이벤트 범위로 열며 질문
 * 전송」). The strip is therefore that panel's surviving affordance on that page,
 * and this is the round's own name for it — the nearest signed string rather than
 * a new heading. **Flagged for `P6.S7`/`P6.REVIEW`**: R6 draws the strip but
 * writes no label for it.
 */
export const ASK_ABOUT_KO = "이 공시에 대해 질문";

// ---------------------------------------------------------------------------
// 질문 스트립 (R6-2 · result.md §Composition examples)
// ---------------------------------------------------------------------------

/**
 * The **first** preset question the record wrote — R6's own.
 *
 * result.md §Composition examples: 「Panel: 계양전기 `20260724000546` — "실권주는
 * 어떻게 처리되나요?" 답변, 근거 = forfeited_share_method · excess_subscription의
 * verbatim quote」 — a question about a **gate-passing field** of one event, which
 * is exactly what R6-2 says a preset is (「프리셋은 그 이벤트의 게이트 통과
 * 필드에서 생성」).
 *
 * **R14 Q-D made every chip work the way this one always did**: nine more
 * sentences were signed (R14-D1…D9) so each chip *sends* a question while
 * *reading* the served `korean_name`, and this one was kept exactly as R6 wrote
 * it rather than re-signed. The table lives in `presets.ts`, which is also where
 * the round's no-fallback rule is stated — a key with no signed sentence renders
 * no chip at all. Templates stay banned: 「{label}은 어떻게 되나요?」 would be
 * invented copy and would read wrongly over half the field names (a 기간 is not
 * 처리되는 것). The `P6.S7` flag this docstring used to carry is **closed by R14**.
 */
export const FORFEITED_QUESTION_KO = "실권주는 어떻게 처리되나요?";
export const FORFEITED_FIELD = "forfeited_share_method";

// ---------------------------------------------------------------------------
// R16 (`rounds/16-smart-assistant/output/build-prompt.md` §0) — 구조화 블록의 말
//
// Transcribed character for character from the signed block, names included.
// **The agent's own Korean is still not here**: R16 signs `STATUS_KO` in
// `copy.py`, so the 진행 표시 line arrives on the wire with its sentence already
// composed (`P9.S3` decision 3) and this file holds no status strings. `P9.S9`
// draws every element below; `P9.S10` draws the start screen.
// ---------------------------------------------------------------------------

/** 계산 블록 머리말의 `--live` 색 단어 (§2.4). 검증된 계산 = 제품의 검증된 연산이
 * 계산한 값, 식 계산 = 산술식이 계산한 값 — **같은 말로 렌더하면 후자가 전자로
 * 세탁된다** (result.md §3-7), 그래서 두 단어는 서로 다르다. */
export const CALC_VERIFIED = "검증된 계산";
export const CALC_EXPR = "식 계산";

/** 마커 가족 (§2.5, 배타적 3종). `추정`은 기존 `EstimateMarker`의 것이고, 이 둘이
 * 신규다 — `계산`은 도구가 계산한 값에, `미확인`은 어떤 도구도 반환하지 않은 공시
 * 수치(`AskBlock` `text.unverified` span)에 붙는다. */
export const TAG_CALC = "계산";
export const TAG_UNVERIFIED = "미확인";

/** 독자가 준 값의 셋째 칸 마커 (§2.3 · §2.4) — 칩 대신 오며, 칩은 붙지 않는다. */
export const TAG_INPUT = "입력";

/** 계산 블록의 두 상태 줄 (§2.4): `done`의 결과 행 라벨과 `pending`의 한 줄. */
export const CALC_RESULT = "결과";
export const CALC_RUNNING = "계산 중";

/** `state=error`인 계산 블록의 문장 (§2.4). `why`는 서버가 보낸 **데이터**
 * (멈춰 세운 입력의 라벨과 표기)이고, 문장은 표면이 이 형식으로 조립한다 —
 * alert 색·아이콘 금지. */
export const calcError = (why: string) => `계산할 수 없습니다 — ${why}`;

/** 데이터 블록의 기본 머리말 (§2.3). 서버가 `title`을 주면 그것을 쓰고, `null`이면
 * 이 말을 쓴다. */
export const DATA_HEADING = "공시에서 읽은 값";

/** 6행을 넘는 데이터 블록의 접힘 토글 (§2.3), 그리고 그 반대말. */
export const SHOW_ALL = (n: number) => `모두 보기 (${n})`;
export const FOLD = "접기";

/** 4행 이상으로 도착한 도구 흐름의 펼침 토글 (§2.2). */
export const DETAIL = "자세히";

/** 접힌 도구 흐름의 한 줄 요약 (§2.2). `events`는 그 턴이 읽은 **서로 다른
 * 접수번호 수**이며 서버가 아는 값(`AskTurn.filings`)이다 — 도구 행에서 파싱하지
 * 않는다 (§1). */
export const trace = (tools: number, events: number) => `도구 ${tools}번 · 공시 ${events}건 읽음`;

// ---------------------------------------------------------------------------
// R16 §2.7b — `/ask` 시작 화면 (레일 없음)
// ---------------------------------------------------------------------------

/** 빈 상태의 인사 (§0 · §2.7b). `AGENT_INTRO_KO`가 그 아래에 온다. */
export const START_HEADING_KO = "안녕하세요!";

/** 스레드가 있을 때만 존재하는 sticky 동작 (§2.7b): 스레드를 비우는 것뿐이며
 * 이력 목록·제목·복원을 만들지 않는다 (R6 금지 유지). */
export const NEW_CHAT_KO = "새 대화";

/**
 * 시작 화면의 질문 카드 — **4장**, §0 서명분 그대로.
 *
 * 카드의 문장이 곧 보내는 질문이다: R14의 label≠question 관례(`presets.ts`)는
 * 시작 화면에 적용하지 않는다고 §0이 못 박는다. 네 장은 서로 다른 회사 · 권리 가족 ·
 * 질문 꼴이며, 범위가 항상 전체 공시이므로 첫 질문이 회사를 담는다.
 *
 * **넷이다.** 랜딩된 build-prompt의 §2.7b 산문과 회귀 항목 21은 아직 「질문 카드
 * 5장」과 제품 메타 카드를 말하지만, 그 메타 카드는 2026-08-25에 폐기되었고
 * (「그 말은 `AGENT_INTRO_KO`가 이미 한다」) 서명된 카피가 governs — `P9.S2` 노트에
 * 세 줄의 stale 라인으로 기록되어 있다.
 */
export const START_CHIPS_KO = [
  "계양전기 신주인수권증서 매매기간",
  "퓨쳐켐 실권주는 어떻게 처리되나요?",
  "대동기어 전환청구는 언제부터 할 수 있나요?",
  "아시아나항공 주식매수청구 가격은 얼마인가요?",
];
