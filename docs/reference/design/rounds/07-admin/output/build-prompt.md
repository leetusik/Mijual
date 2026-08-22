# R7 Implementation Contract — admin panel 운영 관제 (`P3.S8`)

For the Next.js build. Reference cards: `admin/*.html`. **Token delta: none** —
ops 변형은 기존 cosmos 스코프 토큰 + 리터럴 `#0e1a15` (P3.S7 위젯 배경과 동일)만 사용.

## 표면 + 라우트

- 별도 경로 (예: `/ops` — 최종 경로는 배포 결정), **reader chrome 어디에서도 링크
  금지** (nav·푸터·계정 메뉴·sitemap). **6개 섹션: 개요 · 게이트 대기열 · 정확도·비용 ·
  대화 로그 · 사용자 · 피드백.** 모든 섹션은 완전한 페이지 (상단 ops 바: 탭 · lock 칩
  실시간 · KST 시계 · 로그아웃 / 하단 상태 푸터) — 컴포넌트 단편 렌더 금지.
  **전 화면 읽기 전용** — mutation 엔드포인트 없음 (§6.5).
- **데스크톱 전용** — 모바일 레이아웃·미디어쿼리 없음 (min-width 고정 허용).
- 아이디엄: `class="cosmos"` 토큰 스코프 유지, 장식 렌더 금지 (starfield·shooting
  star·radial glow·코너 브래킷·panel-glow 없음). 패널 = 불투명 `#0e1a15` + 1px
  `--border-strong`. 크롬 라벨 한국어, 코드·식별자·스테이지 출력 raw 영문 mono.

## 인증 (§6.4 — 별도 자격증명)

- 인증 전 표면이므로 ops 크롬 없음 — 빈 페이지 가운데 문 하나 (Access 카드).
- 운영자 ID + 비밀번호, R5 계정 테이블과 완전 분리 (조인 없음, admin flag 아님).
  자격은 배포 환경에서 발급·회전 (환경변수/시크릿) — 가입·재설정 UI 없음.
- 실패 응답 균일 「자격증명이 올바르지 않습니다」 + 상수 시간; 어느 필드가 틀렸는지
  구분 금지. 시도 제한은 서버 사안 (UI 카피 없음). 세션 만료 → 문으로 복귀, 로그인
  후 있던 탭 복원. 세션 쿠키 httpOnly·secure, reader 세션과 별도 이름.

## 개요 (파이프라인/beat)

- 상태 타일 4: `gates summary` 값 그대로 (이벤트 노출/고려 + 유형별 · 필드 verdict
  split · 렌더 가능 필드 · 마지막 측정 시각 KST).
- beat 스케줄 표는 Celery beat 설정에서 렌더 (하드코딩 금지 — 설정이 곧 진실).
- **최근 실행 표**: 실행별 행 (시각 KST · 트리거 · 스테이지별 카운트 + req/call
  스펜드 + ▷ 비용 행 verbatim). **스케줄된 beat가 안 돌았으면 「실행 기록 없음」
  행을 alert 잉크로 렌더** — 예정 시각으로부터 파생, 침묵 금지. 예산 소진은 보고된
  상태로 (실패 스타일 금지 — alert는 미실행에만).
- lock 칩: `mijual:lock:pipeline` 실시간 상태 (해제/보유 + 보유 시 시작 시각).
- 가동 전 미결 (D-4 등)은 decisions 문서에서 읽어 렌더 — 패널에 직접 쓰지 않음.

## 게이트 대기열 (§6.5 — 순수 관찰)

- reason_code별 카운트: 저장된 추출 행 기준, 코드 mono + 코드가 가진 reason_ko +
  카운트. **rate 계산은 distinct (rcept_no, field_key) 633 기준** (중복 16행 주의).
- 행 검사 (row inspect): field_key/한국어 이름 · gate_status · reason_code ·
  reason_ko · quote/span (차단 행은 대개 없음 — 「없음」을 상태로 렌더, 자리표시자
  금지) · rcept_no verbatim + DART 링크.
- 이벤트 상태 표 = `gates summary` by-state verbatim; blocked 라인 그대로; 차단
  플래그 4종은 코드의 한국어 카피로.
- **suppression 코드는 raw 영문 그대로 (§6.1 서명)** — 한국어 렌더 함수를 만들지
  말 것; 미지 코드도 코드 그대로 (폴백 문구 금지).
- 철회 이벤트 검사: notice_ko + note verbatim + 게이트 통과 기록(렌더 0) + 차단
  필드 목록.
- **액션 없음**: 검토/해제/승인/재실행 버튼 금지. 노출 변경은 파이프라인 CLI만.

## 정확도·비용

- evalset report의 렌더 — **`mijual.evalset report`가 출력하는 것을 출력** (프로즌
  JSON 2개, DB 접근 금지). **판정 출처(judged_by) 블록을 숫자 위에** — judge ·
  basis · imported_at KST · 인간 검증 0/344 문장. report가 산출물에서 읽은 문장
  그대로 (하드코딩 금지 — 재판정 시 자동 갱신되는 구조 유지).
- 수치 + 필수 분해: 과차단 48 성분 · 12.2% (77/633) · ③ 44% 4분해 · strict 미스
  3 = D4. 분해 없이 단독 인용되는 레이아웃 금지 (분해가 같은 패널 안).
- quota 바: 20,000/day vs 스펜드. **누적치를 일일치처럼 보이게 하지 말 것** —
  라벨에 구간 명시. 일일 실측 스펜드가 생기면 그때 일일 바로 전환.
- LLM 스펜드: `extraction_call` 집계 (calls · tokens · ▷ 비용 · 실패).
- ▷는 파이프라인 출력 verbatim — admin에서 「추정」으로 바꿔치기 금지 (경계 = 출처).

## 대화 로그 (R6-6이 연 루프)

- 스키마 (R6 계약과 정합): 세션 = 익명 해시, 시각 KST, 범위 (이벤트 rcept_no 또는
  전체), 질문, 답변/거절, 거절 카테고리 (R6-7 가족 5종), 근거 rcept_no 목록, 인용
  칩 원문. **계정·이메일·IP·UA 컬럼은 저장하지 않음** — 표시 정책이 아니라 스키마
  (「대화는 익명으로 저장됩니다 (품질 점검용)」 약속의 구현).
- 필터: 유형 (답변/거절) + 거절 카테고리. 시간 역순 커서 페이지네이션.
- 펼친 행 = 대화 재생: 저장분 그대로 (버블 + 거절 가족 문장 + 근거 칩 + DART 링크).
  거절도 저장 시 인용 동반 (R6 규칙) — 뷰어는 그 인용을 그대로 보여줌.
- 읽기 전용 — 삭제·편집·태깅 없음.

## 사용자 (신규 섹션 — operator 요청, 대화 로그와 연결)

- 두 표, 조인 없음: **독자 계정** (R5 층) — 이메일 · 가입일 · 포트폴리오 종목 개수 ·
  알림 설정 · 샘플 로드 여부. **최소 열람**: 포트폴리오 내용(종목·수량)은 열지 않고
  개수만; 비밀번호는 해시 존재 여부도 미표시.
- **익명 세션** — 대화 로그의 집계면: 세션 해시 · 최근 활동 KST · 질문 수 · 거절 수 ·
  마지막 범위 · 「대화 로그 →」 (로그 탭을 그 세션으로 필터). 양방향: 로그 표의 세션
  해시 클릭 → 사용자 탭의 그 행.
- **계정↔대화 연결 컴럼·조인·추정 매칭 금지 — 스키마 수준 부재가 약속의 구현**
  (「대화는 익명으로 저장됩니다」). 거절 비중 높은 세션 = 프리셋·게이트 점검 신호
  — 사용자 추적 용도 금지.
- 읽기 전용: 계정 정지·삭제·수정 없음 (필요해지면 새 서명 사안).

## save_feedback 대기열

- `save_feedback(text, email?)` 착지 목록: 시각 KST · 의견 텍스트 · 답장 이메일
  (선택 — 사용자가 자발 입력한 경우에만 값 존재) · 원 대화 링크 (세션 해시로).
- 빈 상태: 「대기 0건 — save_feedback 호출이 아직 없습니다」.
- 읽기 전용 — 처리 상태 비트 없음; 회신은 패널 밖 (메일 클라이언트).
- **vocky 수집분과 병합 금지** — 상호 링크만.

## vocky 관찰 뷰 (§6.3 — shape는 이 빌드가 결정)

- 운영자 위임: **관찰 API의 반환 shape (필드·granularity·pagination)는 Claude Code가
  vocky 쪽 실물에 맞춰 결정**하고, 결정한 shape를 이 절에 기록해 갱신할 것 — 그
  전까지 카드의 `?` 열 이름은 제안일 뿐 구현 대상이 아님.
- shape와 무관한 고정 계약: 읽기 전용 (관찰 API의 정의 — vocky 상태 변경 없음) ·
  agent 대기열과 별도 뷰 · 위젯 UI는 vocky 소유 (여긴 열람만) · 시각은 KST 표기 ·
  연결 전 상태는 「API shape 확정 대기」 문구 + 스켈레톤.

### 확정된 shape — 2026-08-22, Claude Code 결정 (위 위임 조항에 따른 기록 · `P5.S18`)

vocky 실물(운영자 소유 제품, 리포지터리 + 로컬 스택 실측)에 맞춰 결정하고, 이 절을
갱신한다. 이 절 밖은 건드리지 않음.

- **엔드포인트: `GET {base}/api/project/feedback`** (Project Feedback API v2).
  vocky 자신의 계약이 이 용도를 명시함 — "an external service's own admin panel /
  operator page … reading and managing its project's feedback directly by API".
  나머지 세 읽기면은 배제: `GET /api/feedback`은 제품 사용자 1인의 self-read
  (`user_id` 필요), `/app/feedback`은 사람 세션 토큰용, `/api/project/usage`는 조직의
  **credential 목록**을 반환 — 남의 키 메타데이터는 이 패널이 볼 것이 아님 (최소 열람).
- **인증: `Authorization: Bearer vk_…`** (project 또는 org 스코프). 스코프는 키에
  내재 — project 파라미터가 없고 보내지도 않음. ⚠ vocky에는 **읽기 전용 키 스코프가
  아직 없다** (같은 키로 PATCH·DELETE 가능). 그래서 읽기 전용은 Mijual 쪽에서 구조로
  강제한다: 프록시는 `GET`만 발행하고 다른 메서드를 낼 코드 경로가 없음.
- **granularity: 피드백 이벤트 1건 = 1행.** 집계·롤업 없음 (vocky가 말하지 않은 수를
  만들지 않음).
- **pagination: keyset 커서, 최신순.** `limit` (기본 50, **상한 100 — vocky 자신의
  상한**) + 불투명 `cursor`. `next_cursor`는 vocky 것을 그대로 통과시키고, 마지막
  페이지에서는 **키 자체가 없음** (null 아님). **총계는 없음** — vocky가 total을
  반환하지 않으므로 발명하지 않는다; `count`는 이 페이지의 행 수.
- **필드 (결정된 열, 이 순서 — vocky 자신의 영문 키 이름, §6.1/§6.2의 raw 영문 표기)**:
  `ingested_at` · `message` · `feedback_value` · `trigger_type` · `trigger_message` ·
  `target_type` · `target_id` · `target_text` · `channel` · `recorded_by` ·
  `source_product` · `source_integration` · `comment` · `tags` · `id` ·
  `project_id`(org 키일 때만 vocky가 실어 보냄). 카드의 `?` 열 이름은 이 목록으로
  대체된다. 열 목록은 **서버가 payload의 `fields`로 실어 보냄** — 나중에 넓혀도
  프런트 변경이 없고, 프런트는 vocky 필드명을 한 개도 적지 않는다.
- **제외한 필드와 이유 (통과시키지 않음 — 허용목록 방식)**: `user_id` ·
  `session_id` · `conversation_id` (상관 식별자 — 사용자 추적 용도 금지, 최소 열람) ·
  `messages` · `used_context` · `source_metadata` · `attributes` · `trigger_metadata`
  (자유 형식 블롭 — 관찰에 필요 없고 남의 제품 데이터를 이 패널에 옮겨 담게 됨) ·
  `target_role` · `event_at` (호출자 임의 값). 넓힐 때는 필드 단위로 의도적으로.
- **시각: `ingested_at`을 절대 KST(`+09:00`)로 변환해 제공.** vocky는 UTC(`…Z`,
  마이크로초)로 직렬화하므로 변환은 서버가 한다 — ops `Stamp`는 문자열을 잘라 쓸 뿐
  `Date` 파싱을 하지 않기 때문. 파싱 불가한 값은 **생략** (근사치를 만들지 않음).
- **상태 (payload의 `state`, raw 영문)**: `ok` · `unconfigured` (base/키 미설정 =
  연결 전) · `unreachable` (타임아웃·DNS·401·리다이렉트·이상 응답 — `reason`에 예외
  이름, HTTP 상태가 있으면 `status`). **500 없음, 지어낸 행 없음** (lock 칩이 죽은
  Redis를 보고하는 것과 같은 전례). 타임아웃 3초·재시도 없음·**리다이렉트 거부**
  (urllib이 리다이렉트 대상에 `Authorization`을 다시 보내므로 키가 새어 나감).
- **섹션 배치: vocky 관찰 뷰 = 「피드백」 섹션.** 이 라운드의 카드 7종이 6탭에
  순서대로 대응하고, 기록이 명시함 — result.md "**Feedback** — vocky 관찰 뷰 프레임
  (§6.3)", 그리고 `save_feedback` 대기열은 **Conversations** 카드에 그려져 있음
  (handoff §5도 동일: `admin/Feedback.html` = the vocky observation view,
  `admin/Conversations.html` = the log viewer **+ agent feedback queue**). 7번째 탭을
  만들면 서명된 6탭 내비가 깨진다. 두 수집분은 서로 다른 프라이버시 계약이므로
  (result.md의 분리 근거) 섹션이 다르고, **상호 링크만** 둔다.
- **⚠ 연결 전 문구:** shape가 확정된 지금 「API shape 확정 대기」의 문자 뜻은
  반보 뒤처진다 — 기다리는 대상은 shape가 아니라 `vk_` 자격증명이다. 서명된 카피를
  고쳐 쓰는 것은 설계 변경이므로 **서명된 그대로 렌더**하고, 원인은 옆의 raw 영문
  `state` 코드가 말한다. 문구 교체가 필요하면 새 서명 사안.
- **위젯 (R2/§6.3의 전제 점검):** vocky는 오늘 **임베드 가능한 스크립트 위젯을 제공하지
  않는다** — 캡처는 서버-투-서버 REST/MCP뿐이고, "Browser-direct unauthenticated
  ingestion"은 vocky 자신이 MVP 비목표로 명시함. Mijual의 `data-vocky-trigger` 3개와
  `NEXT_PUBLIC_VOCKY_SRC` seam은 그대로 두되(스크립트가 없으면 태그도 없고 트리거는
  그냥 렌더된다), 이 뷰가 관찰하는 행은 위젯이 아니라 **운영자가 붙일 캡처 경로**에서
  들어온다. 이는 발견 사항이지 이 라운드에서 만들 것이 아님.

## Hard rules (restated)

게이트 판정을 바꾸는 액션 — 금지 (읽기 전용 전면). 미검증 데이터가 독자에 닿는
경로 신설 — 금지. suppression 한국어 문구 발명 — 금지 (raw 코드, §6.1). vocky
필드명 선구현 — 금지 (§6.3 확정 후). 로그에 PII 저장 — 금지 (스키마 수준).
발명 수치 — 금지 (모든 숫자는 CLI/report/설정에서). 미실행 beat 침묵 — 금지 (행으로
렌더). 98.6%를 judged_by 없이 렌더 — 금지. 모바일 대응 — 하지 않음 (명시적).
장식 (별·브래킷·글로우) — admin에 금지. 계정↔대화 조인 — 금지 (스키마 수준).
컴포넌트 단편 화면 — 금지 (모든 섹션은 ops 크롬을 갖춘 완전한 페이지).
