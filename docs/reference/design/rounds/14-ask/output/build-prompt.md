# R14 build-prompt — AI 질문 (binding contract for `P8.S15`)

Surface 7 of 8. Group `⏳ P8.S14 · Ask` · cards `ask/{Widget,Page,Mobile,Strip,Citations}.html` ·
geometry canon `ask/r14-ask.css` · strings `ask/r14-parts.jsx` · decisions `ask/result.md`.
**Token freeze holds (R8): 이 라운드는 토큰을 하나도 바꾸지 않는다.** 새 한국어는 `result.md`
§Copy의 10건뿐이며, 그 밖의 모든 문자열은 `components/ask/copy.ts`와 서버 것 그대로다.

## §1 경계 이관 (Q-A) — 먼저 한다

1. `Ask.module.css:421` `@media (max-width:480px)` → **`(max-width:767px)`** (44px 컨트롤).
2. `AskPage.module.css:64` `@media (min-width:481px)` → **`(min-width:768px)`**.
3. `useAsk.ts` `DESKTOP_QUERY = "(min-width: 481px)"` → **`"(min-width: 768px)"`**.
4. `AskSurface`: 런처·위젯은 **>767에만** 렌더 (지금의 ≤480 미렌더 규칙을 그 선으로 옮긴다).
   `/ask`·`/ops`에서의 미렌더는 그대로.
5. `.widget`의 **`max-width` 가드 삭제** (768px 창에 440+48이 들어간다). `max-height` 가드는 유지.
6. 481–767은 `/ask` 전폭 한 열 — 레일의 네 항목이 대화 위에 쌓인다. 진입은 nav 「AI 질문」과
   상세의 질문 스트립뿐.

## §2 컴포저 (Q-C, finding 13)

- 버튼 텍스트 세 개: **`보내기`** → `답변 준비 중…` → `중지`. `SEND_KO = "보내기"`를 `copy.ts`에
  R14 서명 주석과 함께 신규 등재하고, 버튼에서 `ASK_SUBMIT_KO` 사용을 **제거**한다
  (상수는 스트립의 자유 입력 칩용으로 남는다).
- `disabled`(빈 입력·pending) = **고스트 티어**: `background:none`, `border-color:var(--border-soft)`,
  `color:var(--ink-3)`. `opacity:.72` 삭제. 히트 36px / ≤767 44px 불변.
- hover: 솔리드 상태에서 **테두리만** `--live`. disabled는 hover 없음.

## §3 프리셋 (Q-D)

- `AskPreset.question`이 더 이상 `label`과 동일하지 않다. `presets.ts`에 **필드 키 → 서명된 질문**
  표(`result.md` §Copy의 10건)를 두고, `label`은 서빙된 `korean_name` 그대로 둔다.
- `forfeited_share_method`는 R6 문장 유지. **표에 없는 키는 칩을 만들지 않는다** (라벨 폴백 금지).
  `korean_name`이 없는 필드도 그대로 칩 없음.
- 순서·생성 규칙·`correction_interpretation` 제외·철회 이벤트 0칩은 전부 불변.
- 칩의 `title`/접근명은 **보내는 문장**이다(라벨은 눈에 보이는 텍스트).

## §4 답변 렌더 (Q-E, Q-B, findings 5·10·14)

- **한 단락.** 인접 프로즈 블록은 한 `<p>`, 문장은 인라인 `span`, 간격은 `.sentence+.sentence`의
  `0.25em` 하나. 스토어가 블록을 넣을 때 **선행 공백·개행을 정규화**한다
  (`text.replace(/^\s+/, "")`); `<br>`·`white-space:pre-wrap`·`display:block`을 프로즈에 두지 않는다.
  질문 버블(`.question`)의 `pre-wrap`은 그대로 — 독자가 친 것은 독자가 친 그대로다.
- **푸터 `근거 N건` = 칩 번호의 개수** (`turn.chips` 기준). 서버의 `footer.count`가 공시 수를
  세고 있으면 그 값을 쓰지 않고 칩에서 센다 (또는 서버를 칩 수로 맞춘다 — 둘 중 하나이며
  화면과 어긋나면 안 된다). 접수번호 목록·KST 스탬프는 그대로.
- **도구 행**: `word-break:break-all` 삭제 → `white-space:nowrap; overflow-x:auto;
  overscroll-behavior-x:contain`, 스크롤바 숨김. 행 내용은 여전히 verbatim.
- **API-tier 인용 블록**: 설명 줄 삭제. 블록은 `DART 원문 {rcept_no} ↗` 하나만 (`.aql.solo` —
  위 여백 없음). `API_TIER_KO` 삭제, `InlineCitation`의 분기는 「quote 있으면 인용문, 없으면 링크만」.
- **스크롤바**: 스레드와 인용문 모두 `scrollbar-width:thin` + thumb `--border-strong` + track 투명.

## §5 페이지·모바일·hover (findings 9·11, Q-F)

- `/ask` >767: `grid-template-columns: minmax(0,760px) 340px`, 묶음 `max-width:1124px;
  margin-inline:auto`, 레일 `position:sticky; top:var(--space-6)`. 프레임 없음 유지(레일만 패널).
- `/ask` ≤767: chrome이 **vocky 트리거를 렌더하지 않는다**. 바는 인셋하지 않는다(전폭 44px).
- hover 한 규칙: 스트립 칩 soft→strong · 자유 칩 + ink-2→ink-1 · 인용 칩 테두리 → 불투명 `--live`
  · 솔리드 테두리 → `--live` · 헤더 아이콘·범위 × ink-2→ink-1.
- 빈 위젯: 범위가 이벤트면 인트로 아래 **프리셋 한 줄**(자유 칩 없음), 전체 공시면 아무것도 없음.

## §6 회귀 체크리스트 (§1 baseline 전부 + 이 라운드)

1. 런처 → 위젯 제자리 열림, 레이아웃 시프트 0 (1440·1024·**768**).
2. **767/768 경계**: 767px에서 런처·위젯 없음 + `/ask` 한 열 · 768px에서 런처 있음 + 440×620 정확.
3. 480px 잔재 0건 — `rg "480|481" frontend/components/ask frontend/lib/ask.ts` 결과 없음.
4. pending: 버튼 `답변 준비 중…` + disabled(고스트), 버블·스피너 없음.
5. streaming: 도구 행 verbatim · 프로즈가 **한 단락**으로 자람(줄바꿈 0) · 캐럿 7×15 1s step · 버튼 `중지`.
6. 빈 입력 버튼 = 고스트 disabled, 질문 입력 시 솔리드 `보내기`, 클릭으로 전송.
7. 인용 칩 탭 → 제자리 인용문(180px 캡) · 재탭 닫힘 · 같은 근거 = 같은 번호.
8. API-tier 칩 → 블록에 **링크만** (설명 줄 없음), 새 탭 이동.
9. 완료 푸터: `근거 N건`의 N = 화면의 칩 번호 개수 (5칩 답변에서 5건) · 접수번호 전부 · KST 스탬프 · `다시 질문` 포커스.
10. 거절: 프로즈 경로 + 인용 + 갈 곳 3링크, alert 색 없음.
11. 중지: 부분 답변 유지 + `--ink-2` 감쇠 + 서명 문장 한 줄 + `재시도` → 같은 턴 제자리 재실행.
12. external-link → 위젯 닫힘 + `/ask` 도착, 대화·범위 그대로. reload → 스레드 복원, 콘솔 경고 0.
13. 범위 칩 × → 전체 공시로 해제, 기존 답변 불변.
14. 스트립 칩: **라벨이 보이고 문장이 전송된다** — 스레드의 버블이 문장 (1440·390 모두).
15. 390: 인용 블록 전폭 · 도구 행의 접수번호 **쪼개짐 0** (가로 스크롤) · 바 44px sticky ·
    **vocky ⓝ 없음** · 가로 오버플로 0px.
16. `/ask` 1564px: 챗 열 ≤760px, 묶음 가운데, 레일 sticky, 짧은 스레드에서 바가 마지막 요소 바로 아래.
17. 768–1024의 `/ask`에서 바의 좌하단이 chrome 코너에 닿는지 **실측** — 닿으면 ≤767과 같은 규칙 적용.
18. 스레드·인용문 스크롤바가 얇은 제품 스타일 (기본 회색 바 없음).
19. 신규 카피 10건이 `copy.ts`/`presets.ts`에 R14 서명 주석과 함께 등재 · `API_TIER_KO` 삭제 ·
    `ASK_SUBMIT_KO`는 스트립 자유 칩에만 남음.
20. 하드룰 재확인: 인용 없는 주장 0 · 인용문 재구성 0 · 브라우저 계산 0 · 확정 전 금액 0 ·
    스피너·타이핑 점 0 · 거절 alert 색 0 · 이력 UI 0 · quota 표기 0.

## §7 이 라운드가 손대지 않는 것

`get_contact`의 연락처 플레이스홀더(운영자 지정 대기) · `favicon.ico` 404(chrome, R15) ·
런처 마크와 새턴 모션(R6 개정 ⑤ 서명분) · SSE 계약과 상태 이름 · 세션·저장 문구 ·
익명 경로 · 에이전트의 도구 행·거절 문장(서버 소유).
