/**
 * Every Korean string 운영 관제 renders, and where each one comes from.
 *
 * Same rule and same shape as `lib/copy.ts`, `components/chrome/copy.ts` and the
 * other surfaces': **nothing here is invented.** Every entry is transcribed from
 * R7's landed record — `docs/reference/design/rounds/07-admin/output/`
 * (`build-prompt.md`, and `result.md`'s 「Proposed copy (신규 — 서명 대기)」 list,
 * which the operator's "Signed off — close R7" closed) — or from R6 where R7
 * quotes it.
 *
 * This panel has a second source of text that no reader surface has, and it is
 * the reason the file is shorter than the screens are: **§6.1/§6.2 sign raw
 * English for codes, identifiers and pipeline output.** So a gate status, a
 * reason code, a suppression code, a stage name, a beat spec, a window label
 * (`cumulative` / `daily`) and the ▷ spend line are rendered as the machine
 * writes them, in mono — not translated, not given a Korean fallback, and not
 * paraphrased into a label this file would have had to invent.
 *
 * Everything else comes off the wire: `reason_ko` (the gate layer's own Korean),
 * `korean_name` (the field registry's), `notice_ko` (the product's 철회
 * sentence), and the evalset report's own markdown.
 */

import { OPS_ROUTES, type OpsRouteKey } from "./routes";

// ---------------------------------------------------------------------------
// The ops chrome (build-prompt §표면 + result.md's Overview card)
// ---------------------------------------------------------------------------

/** The bar's own mark. R7 result.md: "ops 크롬 (**MIJUAL OPS** 바 …)" and the
 * Access card's 「MIJUAL OPS 표기」 — an identifier, so it stays raw and mono.
 *
 * P10 retired the latin mark: the string is now `주주의관제탑 운영`, the same
 * shape (product name + role) in the product's own language. R7's *treatment* is
 * untouched on purpose — `Ops.module.css` `.mark`/`.doorMark` still set
 * `--font-mono` + `0.08em`, which is signed styling, and IBM Plex Mono carries no
 * Hangul. Changing that is a typography decision on a signed round and it is the
 * operator's; P10 filed it as an open question rather than fixing it quietly. */
export const OPS_MARK = "주주의관제탑 운영";

/** Signed section labels (build-prompt §표면; result.md's copy list ends with
 * "섹션 라벨 (개요 · 게이트 대기열 · 정확도·비용 · 대화 로그 · 사용자 · 피드백)").
 * Six sections, in the round's own order. */
export const LOG_SECTION_KO = "대화 로그";
export const FEEDBACK_SECTION_KO = "피드백";

export const OPS_TABS: { key: OpsRouteKey; label: string; href: string }[] = [
  { key: "overview", label: "개요", href: OPS_ROUTES.overview },
  { key: "gates", label: "게이트 대기열", href: OPS_ROUTES.gates },
  { key: "accuracy", label: "정확도·비용", href: OPS_ROUTES.accuracy },
  { key: "conversations", label: LOG_SECTION_KO, href: OPS_ROUTES.conversations },
  { key: "users", label: "사용자", href: OPS_ROUTES.users },
  { key: "feedback", label: FEEDBACK_SECTION_KO, href: OPS_ROUTES.feedback },
];

/** result.md's copy list: 「운영자 전용」. The status footer states it on every
 * tab, which is also the honest answer to "who is this screen for". */
export const OPERATOR_ONLY_KO = "운영자 전용";

/** result.md's copy list: 「순수 관찰 — 이 화면에는 액션이 없습니다」. §6.5 makes it
 * true of the whole panel (전 화면 읽기 전용), and the GateQueue card renders it
 * as its own banner — so it sits in the status footer and above 게이트 대기열. */
export const OBSERVATION_ONLY_KO = "순수 관찰 — 이 화면에는 액션이 없습니다";

/** R5's own chrome word, and R7's ops bar ends with it (build-prompt §표면:
 * "상단 ops 바: 탭 · lock 칩 실시간 · KST 시계 · 로그아웃"). */
export const LOGOUT_KO = "로그아웃";

/** The time zone every instant in this product is stated in (D-10). The clock
 * and every stamp carry it, as the round writes them ("시각 KST"). */
export const KST = "KST";

/** The product's own counting unit — R7 writes it in its own two empty states
 * (「대기 **0건**」, 「가입 **0건**」) and the board counts 488건 with it. It is
 * what an empty table on this surface says, because R7 signs an empty-state
 * *sentence* for two tables only and inventing one for the others is a design
 * change: the count and its unit are the honest rendering of nothing. */
export const COUNT_UNIT_KO = "건";

// ---------------------------------------------------------------------------
// 문 — the Access card (build-prompt §인증, R7 §6.4)
// ---------------------------------------------------------------------------

/** build-prompt §인증: "실패 응답 균일 「자격증명이 올바르지 않습니다」 + 상수
 * 시간". The **one** thing the door ever says about a failure: not which field,
 * not whether the ID exists, not that no credential is configured. */
export const CREDENTIALS_INVALID_KO = "자격증명이 올바르지 않습니다";

/** build-prompt §인증: "운영자 ID + 비밀번호". */
export const OPERATOR_ID_KO = "운영자 ID";
export const PASSWORD_KO = "비밀번호";

/** The door's own verb, taken from the same section's sentence — "세션 만료 →
 * 문으로 복귀, **로그인** 후 있던 탭 복원" (and §6.4's "전용 로그인"). The round
 * draws the control and does not label it, so the label is the round's own noun
 * rather than a sentence written here. Flagged for `P5.S19`. */
export const LOGIN_KO = "로그인";

// The door's 규칙 패널 (R7's four implementation-rule lines, `DOOR_RULES_KO`)
// was removed here by D15 in `P4.S4`: they are rules addressed to us, and two of
// them describe the security posture of a page that is now public. The rules
// themselves are unchanged in the R7 record —
// `docs/reference/design/rounds/07-admin/output/` (build-prompt §표면/§인증 and
// result.md's Access card). No copy replaces them: R7 wrote none for that spot.

// ---------------------------------------------------------------------------
// 개요 (build-prompt §개요)
// ---------------------------------------------------------------------------

/** "상태 타일 4: `gates summary` 값 그대로 (이벤트 노출/고려 + 유형별 · 필드
 * verdict split · 렌더 가능 필드 · 마지막 측정 시각 KST)" — the round's own four
 * tile names, in its own order. */
export const TILE_EVENTS_KO = "이벤트 노출/고려";
export const TILE_VERDICTS_KO = "필드 verdict";
export const TILE_RENDERABLE_KO = "렌더 가능 필드";
export const TILE_MEASURED_KO = "마지막 측정 시각";

/** "beat 스케줄 표는 Celery beat 설정에서 렌더 (하드코딩 금지 — 설정이 곧 진실)". */
export const BEAT_KO = "beat 스케줄";
/** "**최근 실행 표**: 실행별 행 …". */
export const RUNS_KO = "최근 실행";
/** "lock 칩: `mijual:lock:pipeline` 실시간 상태 (해제/보유 + 보유 시 시작 시각)". */
export const LOCK_KO = "lock";
export const LOCK_HELD_SINCE_KO = "시작 시각";
/** "가동 전 미결 (D-4 등)은 decisions 문서에서 읽어 렌더 — 패널에 직접 쓰지 않음". */
export const PENDING_KO = "가동 전 미결";

/** result.md's copy list: 「실행 기록 없음」 — the alert-ink row a scheduled beat
 * that did not run gets. Derived from the schedule's own due time, never
 * fabricated by the backend, and never silent (build-prompt §개요: 침묵 금지). */
export const NO_RUN_RECORD_KO = "실행 기록 없음";

// ---------------------------------------------------------------------------
// 게이트 대기열 (build-prompt §게이트 대기열)
// ---------------------------------------------------------------------------

/** "reason_code별 카운트: 저장된 추출 행 기준 …". */
export const REASON_COUNTS_KO = "reason_code별 카운트";
/** "**rate 계산은 distinct (rcept_no, field_key) … 기준** (중복 16행 주의)" — the
 * basis is served (`P5.S9` recounted it to 691 distinct of 710 stored) and the
 * panel prints it beside every rate rather than leaving a denominator implicit. */
export const BASIS_KO = "rate 기준";
/** "행 검사 (row inspect): …". */
export const ROW_INSPECT_KO = "행 검사";
/** "이벤트 상태 표 = `gates summary` by-state verbatim; blocked 라인 그대로". */
export const EVENT_STATE_KO = "이벤트 상태";
export const BLOCKED_KO = "blocked";
/** "차단 플래그 4종은 코드의 한국어 카피로" — the Korean comes from
 * `BLOCKING_FLAGS` on the wire, never from this file. */
export const BLOCKING_FLAGS_KO = "차단 플래그";
/** "**suppression 코드는 raw 영문 그대로 (§6.1 서명)** — 한국어 렌더 함수를 만들지
 * 말 것; 미지 코드도 코드 그대로 (폴백 문구 금지)." */
export const SUPPRESSION_KO = "suppression 코드";
/** "철회 이벤트 검사: notice_ko + note verbatim + 게이트 통과 기록(렌더 0) + 차단
 * 필드 목록". */
export const WITHDRAWN_KO = "철회 이벤트 검사";
export const WITHDRAWN_UNRENDERED_KO = "게이트 통과 기록 (렌더 0)";
export const BLOCKED_FIELDS_KO = "차단 필드";

/** "quote/span (차단 행은 대개 없음 — **「없음」을 상태로 렌더, 자리표시자 금지**)".
 * 없음 is a *state* — it is what the panel says about a blocked row's evidence,
 * and it is never used where a value would otherwise be. */
export const NONE_KO = "없음";

// ---------------------------------------------------------------------------
// 정확도·비용 (build-prompt §정확도·비용)
// ---------------------------------------------------------------------------

/** "**판정 출처(judged_by) 블록을 숫자 위에**" — and the hard rule: 98.6%를
 * judged_by 없이 렌더 — 금지. */
export const JUDGED_BY_KO = "판정 출처";
export const JUDGE_KO = "judge";
export const BASIS_LABEL_KO = "basis";
export const IMPORTED_AT_KO = "기록";
/** "표본" — the report's own word for the sample line it prints. */
export const SAMPLE_KO = "표본";
/** "수치 + 필수 분해 … 분해 없이 단독 인용되는 레이아웃 금지 (분해가 같은 패널 안)". */
export const SHOWN_PRECISION_KO = "노출 필드 정밀도 (strict)";
export const OVER_BLOCK_KO = "과차단";
export const BY_FIELD_KO = "필드별";
export const CORPUS_BLOCK_KO = "코퍼스 게이트 차단율";
export const HARD_CASES_KO = "하드 케이스";
export const CORRECTION_RECALL_KO = "정정 해석 재현율 프록시";
/** "**`mijual.evalset report`가 출력하는 것을 출력**" — the CLI's own markdown,
 * quoted verbatim so the tab can never state a number the command does not. */
export const REPORT_OUTPUT_KO = "evalset report 출력";
/** "quota 바: 20,000/day vs 스펜드. **누적치를 일일치처럼 보이게 하지 말 것** —
 * 라벨에 구간 명시." The window labels themselves stay the served English tokens
 * (`cumulative` / `daily`), which §6.2 signs for identifiers. */
export const QUOTA_KO = "quota";
export const QUOTA_PER_DAY_KO = "20,000/day";
/** "LLM 스펜드: `extraction_call` 집계 (calls · tokens · ▷ 비용 · 실패)". */
export const LLM_SPEND_KO = "LLM 스펜드";
export const DART_SPEND_KO = "OpenDART 요청";

// ---------------------------------------------------------------------------
// 대화 로그 · 사용자 · 피드백 (build-prompt §대화 로그 / §사용자 / §save_feedback)
// ---------------------------------------------------------------------------

/**
 * R6's own UI copy, which R7 renders as this panel's promise banner
 * (result.md's Conversations card: "약속 배너 (「대화는 익명으로 저장됩니다 (품질
 * 점검용)」의 내부면 — 계정·이메일·IP·UA 열은 저장 자체가 없음)").
 *
 * It is the same promise the 사용자 tab's two unjoined tables implement, so both
 * carry it — and it is a statement about the **schema**, which is why P5 can make
 * it without qualification: this build stores no conversation at all.
 */
export const ANONYMOUS_PROMISE_KO = "대화는 익명으로 저장됩니다 (품질 점검용)";

/** "필터: 유형 (답변/거절) + 거절 카테고리. 시간 역순 커서 페이지네이션." */
export const FILTER_KIND_KO = "유형";
export const FILTER_REFUSAL_KO = "거절 카테고리";
export const ANSWER_KO = "답변";
export const REFUSAL_KO = "거절";
/** The API's own tokens for 유형 (`mijual.web.conversations`: "``kind`` is
 * ``answer`` | ``refusal``"). Korean is the label; the value stays the code. */
export const KIND_VALUES = { answer: "answer", refusal: "refusal" } as const;

/**
 * The refusal families — **six values**, and the exact mirror of
 * `mijual.web.conversationstore.REFUSAL_FAMILIES` (same values, same order).
 *
 * R6 signed five (build-prompt §거절: "reason code별 문구 생성 금지 — **카테고리
 * 5종**만"); R16 re-signed them (build-prompt §0 + result.md §7 계약 확장 2/2):
 * **보안** is the new sixth family, and 계산 요청 · 검증 미통과 폴백 are **retired
 * — kept here read-only, for past rows**. Both are still in the filter on purpose:
 * turns stored under them exist, and a 품질 점검 that cannot find them would be a
 * hole in the log rather than a tidier dropdown. Nothing new is written with either.
 *
 * They travel as the filter's *value* too. P6 owns the storage vocabulary
 * (`refusal_category` is an opaque string to `P5.S9`'s port), and inventing an
 * English token for each family here would be the same pre-implementation §6.3
 * forbids for vocky — so the signed Korean name is what the panel sends, and P6
 * inherits it.
 */
export const REFUSAL_CATEGORIES_KO = [
  "철회",
  "확정 전",
  "공시에 없음",
  "보안",
  "계산 요청",
  "검증 미통과 폴백",
];

/** "스키마 (R6 계약과 정합): 세션 = 익명 해시, 시각 KST, 범위 (이벤트 rcept_no
 * 또는 전체), 질문, 답변/거절, 거절 카테고리, 근거 rcept_no 목록, 인용 칩 원문." */
export const LOG_SESSION_KO = "세션";
export const LOG_TIME_KO = "시각";
export const LOG_SCOPE_KO = "범위";
export const LOG_QUESTION_KO = "질문";
export const LOG_ANSWER_KO = "답변/거절";
export const LOG_EVIDENCE_KO = "근거";
export const LOG_QUOTE_KO = "인용";

/** "두 표, 조인 없음: **독자 계정** (R5 층) — 이메일 · 가입일 · 포트폴리오 종목
 * 개수 · 알림 설정 · 샘플 로드 여부." */
export const READER_ACCOUNTS_KO = "독자 계정";
export const EMAIL_KO = "이메일";
export const JOINED_KO = "가입일";
export const HOLDINGS_COUNT_KO = "포트폴리오 종목 개수";
export const NOTIFICATIONS_KO = "알림 설정";
export const SAMPLE_LOADED_KO = "샘플 로드 여부";
/** "**최소 열람**: 포트폴리오 내용(종목·수량)은 열지 않고 개수만; 비밀번호는 해시
 * 존재 여부도 미표시." */
export const MINIMAL_READ_KO = "최소 열람";
/** result.md's copy list: 「가입 0건 — 미배포 상태의 실제값」. */
export const NO_SIGNUPS_KO = "가입 0건 — 미배포 상태의 실제값";
/** `P5.S8` note 9: an absent preference row means the 7일+1일 default, not
 * "off", and the payload says which of the two it is looking at. `stored` is the
 * served flag, so the panel states the served word rather than a judgement. */
export const DEFAULT_KO = "기본값";
export const STORED_KO = "저장됨";

/** "**익명 세션** — 대화 로그의 집계면: 세션 해시 · 최근 활동 KST · 질문 수 ·
 * 거절 수 · 마지막 범위 · 「대화 로그 →」". */
export const ANON_SESSIONS_KO = "익명 세션";
export const SESSION_HASH_KO = "세션 해시";
export const LAST_ACTIVITY_KO = "최근 활동";
export const QUESTIONS_KO = "질문 수";
export const REFUSALS_KO = "거절 수";
export const LAST_SCOPE_KO = "마지막 범위";
/** The signed cross-link, arrow included. */
export const TO_LOG_KO = "대화 로그 →";
/** "거절 비중 높은 세션 = 프리셋·게이트 점검 신호 — 사용자 추적 용도 금지." */
export const REFUSAL_SIGNAL_KO =
  "거절 비중 높은 세션 = 프리셋·게이트 점검 신호 — 사용자 추적 용도 금지";

/** "`save_feedback(text, email?)` 착지 목록: 시각 KST · 의견 텍스트 · 답장 이메일
 * (선택 — 사용자가 자발 입력한 경우에만 값 존재) · 원 대화 링크 (세션 해시로)." */
export const FEEDBACK_TIME_KO = "시각";
export const FEEDBACK_TEXT_KO = "의견 텍스트";
export const FEEDBACK_EMAIL_KO = "답장 이메일 (선택)";
export const FEEDBACK_THREAD_KO = "원 대화";
/** build-prompt §save_feedback: "빈 상태: 「대기 0건 — save_feedback 호출이 아직
 * 없습니다」." (result.md's list writes the same line ending 「없음」; the
 * implementation contract governs.) */
export const FEEDBACK_EMPTY_KO = "대기 0건 — save_feedback 호출이 아직 없습니다";
/** "읽기 전용 — 처리 상태 비트 없음; 회신은 패널 밖 (메일 클라이언트)." */
export const FEEDBACK_READ_ONLY_KO = "읽기 전용 — 처리 상태 비트 없음; 회신은 패널 밖";

/** "**vocky 수집분과 병합 금지** — 상호 링크만." Two collections, two privacy
 * contracts, two sections: the queue rides with the 대화 로그 it came from and
 * the vocky view is the 피드백 section (see `Vocky.tsx` for the record's own
 * card→section mapping). The link between them is the 상호 링크 this line allows. */
export const NO_VOCKY_MERGE_KO = "vocky 수집분과 병합 금지 — 상호 링크만";

// ---------------------------------------------------------------------------
// vocky 관찰 뷰 (build-prompt §vocky 관찰 뷰, R7 §6.3)
// ---------------------------------------------------------------------------

/** The section's own heading in the implementation contract: "## vocky 관찰 뷰". */
export const VOCKY_VIEW_KO = "vocky 관찰 뷰";

/**
 * "연결 전 상태는 「API shape 확정 대기」 문구 + 스켈레톤" — signed copy
 * (result.md's Proposed-copy list, closed by the operator's "Signed off — close
 * R7"), rendered **only** in the 연결 전 state, which is what this build is in:
 * no `vk_` credential is wired, so nothing has ever been read.
 *
 * ⚠ The literal is now slightly behind its own surface: `P5.S18` confirmed the
 * shape, so what the view waits for is the credential, not the shape. Rewriting
 * a signed line is a design change, so it is rendered **as signed** and the raw
 * English `state` code beside it says which cause it is. Flagged for the review.
 */
export const API_SHAPE_PENDING_KO = "API shape 확정 대기";

/**
 * "shape와 무관한 고정 계약" — the three lines the round fixes regardless of what
 * the API turned out to return, transcribed from the build prompt's own bullet.
 * The fourth ("시각은 KST 표기") is not a sentence the panel prints: it is the
 * `Stamp` on every instant in the table.
 */
export const VOCKY_CONTRACT_KO = [
  "읽기 전용 (관찰 API의 정의 — vocky 상태 변경 없음)",
  "agent 대기열과 별도 뷰",
  "위젯 UI는 vocky 소유 (여긴 열람만)",
];
