# 구현 계약 — R8 폴리시: 전역 크롬 + 의견 보내기 (P8.S3에서 적용)

대상 파일: `frontend/components/chrome/{Nav.tsx,Nav.module.css,AccountSlot.tsx,AccountSlot.module.css,
Footer.tsx,Footer.module.css,copy.ts}` · 신규 `frontend/components/chrome/{Feedback.tsx,
Feedback.module.css}` · 신규 `frontend/components/Identicon.tsx` · 신규 API 라우트
`frontend/app/api/feedback/route.ts` · 삭제 `VockyTrigger.tsx`(+ css) 및 `VockyScript.tsx`.
**토큰 변경 없음** — `frontend/public/foundations/tokens.css` 그대로.

**세션에서 확정된 이번 라운드의 큰 축 4개** — ① nav 목적지 2개 (AI 질문 · 보유 종목; 관제 현황판은
워드마크) + [의견] 칩 제거 ② 샘플 칩·샘플 종료 폐기 (계정 슬롯은 익명·로그인 두 상태) ③ 계정 슬롯 =
전체 이메일 + 아이디콘 + 프레임, 메뉴 2행 ④ 푸터 산문 제거 + 미주알이 소유하는 「의견 보내기」 표면 신설.

카드 = 정본: `chrome/Nav.html` · `chrome/NavMobile.html` · `chrome/AccountSlot.html` ·
`chrome/Footer.html` · `chrome/Feedback.html` · `chrome/FeedbackStates.html` ·
`components/Identicon.html`.

## 1. Nav (desktop)

- 바: `height 52px`, 배경 없음(투명), `border-bottom: 1px solid rgba(255,255,255,.12)`. 변경 없음.
- 좌: 링 워드마크 `h19` (`/assets/mijual-logo-ring-white.png`, 재인코딩 금지) → `ROUTES.board`.
- 목적지 **2개**, `gap: var(--space-5)`, `13.5px(--text-base)`, 활성 = `font-weight:600` + `border-bottom:
  2px solid #fff` (비활성은 2px transparent 예약). 순서와 라벨:

  | 라벨 | 라우트 | 비고 |
  |---|---|---|
  | AI 질문 | `ROUTES.ask` | 불변 |
  | **보유 종목** | `ROUTES.portfolio` | **신규 상수 `HOLDINGS_LABEL_KO = "보유 종목"`** |

  **「관제 현황판」 링크는 제거한다** — 현황판은 랜딩이고 링 워드마크(→ `ROUTES.board`)가 이미 그 목적지다.
  같은 목적지를 바에서 두 번 말하지 않는다. `BOARD_LABEL_KO`는 표면 제목 용도로만 남기고 크롬에서는 미사용.
  랜딩 경로에서는 활성 링크가 없다 (`aria-current`는 워드마크에 두지 않는다 — 밑줄도 없음).

  `보유 종목`은 로그인 여부와 무관하게 같은 라벨·같은 라우트. 익명이면 표면이 샘플 모드로 응답
  (`SampleBanner` + `lib/sample.ts` 기존 동작) — nav는 아무 배지도 붙이지 않는다.
- 우 유틸리티: **`VockyTrigger surface="nav"` 제거** (`VOCKY_NAV_KO` 상수도 삭제). 남는 것은
  `AccountSlotDesktop` 하나.
- 랜딩의 「내 포트폴리오는 어떻게 보이나 — 샘플로 열어보기 →」 링크와 그 빈 밴드 제거 (랜딩 컴포넌트에서).

## 2. AccountSlot

익명(`로그인` 조용한 링크)은 **변경 없음**. 샘플 상태는 **삭제**(위 §1). 로그인 상태만 재작성:

```
<button class=frame aria-haspopup="menu" aria-expanded title={email}>
  <Identicon seed={email} size={20} />         // 20px
  <span class="mono email">{email}</span>       // 전체 이메일, --text-sm, 말줄임
  <span aria-hidden>▾</span>                    // 열림 시 ▴
</button>
```

- 프레임: `height 32px`, `padding: 0 var(--space-2) 0 6px`, `gap var(--space-2)`,
  `border: 1px solid var(--border-strong)`, 배경 없음, 색 `rgba(255,255,255,.82)`, `max-width: 280px`.
- 이메일: `.mono`, `--text-sm`, `overflow:hidden; text-overflow:ellipsis; white-space:nowrap`.
  **축약 함수 `abbreviateEmail` 사용 중단** (`lib/account.ts`의 export는 다른 사용처 확인 후 제거).
- hover / `[aria-expanded="true"]`: `background: rgba(255,255,255,.045)`, 보더 `--ink-3` / `--ink-2`,
  색 `--ink-1`. 포커스는 셸의 2px `--focus-ring` 그대로.
- 메뉴: `position:absolute; top: calc(100% + var(--space-2)); right: 0; min-width: 100%; width: max-content;`
  배경 **`#0e1a15`(불투명)**, `border: 1px solid var(--border-strong)`, `box-shadow: var(--panel-glow)`.
  행 `min-height 40px`, `padding: 0 var(--space-3)`, `--text-base`, 행 사이 `1px var(--border-soft)`,
  hover `--surface-raised`.
- 행은 **두 개**: `알림 설정`(`ROUTES.notifications`) · `로그아웃`(즉시, 다이얼로그 없음, 기존 `useLogout`).
  `내 포트폴리오` 행 삭제 — `PORTFOLIO_LABEL_KO`는 계정 표면 자체 제목 용도로만 남기고 크롬에서는 미사용.
- Esc / 외부 클릭 닫힘 유지.

## 3. Nav 모바일 (≤480)

- 바 버튼: 닫힘 `메뉴`(mono, `--text-sm`), 열림 **`×`**(mono 20px, 같은 44×44 히트). `aria-label`은 항상
  `메뉴`, 상태는 `aria-expanded`. 새 문구를 만들지 않는다.
- 시트: `position:absolute; top:100%; left:0; right:0; z-index:10`, 배경 `var(--paper)`(불투명),
  하단 `1px rgba(255,255,255,.12)`. **본문을 밀지 않는다** (현재도 absolute — 인라인처럼 보이던 원인이
  `SiteChrome`의 스택 순서라면 시트가 바 위에 겹치도록 z-index/스태킹 컨텍스트를 고칠 것).
- **백드롭 신규**: `position:absolute; top:52px; bottom:0; left:0; right:0; background: rgba(10,19,16,.72);
  z-index:9`. 클릭 = `closeSheet()`. 시트 열림 동안 `document.body` 스크롤 잠금 (`overflow:hidden`).
  reduced-motion에서 백드롭 페이드도 컷.
- 행: `AI 질문` / `보유 종목` (각 `min-height 48px`; 관제 현황판 행 없음 — 바의 워드마크) → 구분선 →
  로그인 시 `[아이디콘 28 + 전체 이메일]` 표기 행(비인터랙티브, `padding: var(--space-3) var(--space-4)`) +
  `알림 설정` + `로그아웃`; 익명이면 `로그인` 한 행 → 구분선 → `의견 보내기`(시트 트리거, quiet).
- 페이드 200ms(`--dur-base`), Esc·경로 변경 닫힘 — 기존 로직 유지.

## 4. Footer

```
<footer>            border-top: 1px solid rgba(255,255,255,.14); padding-block: var(--space-6)
  <div class=in>    flex, space-between, gap var(--space-6), wrap
    <div class=id>  워드마크 h17 + "자료: 금융감독원 DART 전자공시 · © 미주알"
    <div class=acts> [의견 보내기 버튼] [AI 질문 링크]
```

- 삭제할 상수와 마크업: `POSITIONING_KO`, `PROVENANCE_KO`, `GATE_COST_VALUE_KO`, `GATE_COST_TAIL_KO`,
  `DISCLAIMER_KO`, 그리고 `EstimateMarker` 임포트. (문장 자체는 result.md §6-1의 이전 제안 대기 —
  상수를 지우기 전에 그 결정을 확인.)
- 남는 텍스트는 **Pretendard**: 출처·© 줄 `--text-sm`, `rgba(255,255,255,.45)`; 액션 `--text-base`,
  `rgba(255,255,255,.72)`, hover `--ink-1`. `font-family: var(--font-mono)` 전부 제거.
- 하단 별도 하이라인 행 폐기 — 푸터는 하이라인 하나, 행 하나.
- ≤480: `.in`을 `display:grid; gap: var(--space-4)`, `.id`를 열 스택(gap 10px), 액션은
  `gap: var(--space-6)` + 각 항목 `min-height:44px` — 줄바꿈 고아 금지.
- `margin-top: var(--space-16)` 유지.

## 5. Identicon (`frontend/components/Identicon.tsx`)

```ts
props: { seed: string; size?: 20|28|40 (default 20); title?: string }
key  = seed.trim().toLowerCase()
h    = fnv1a32(key)                  // h=0x811c9dc5; per char: h^=c; h=Math.imul(h,0x01000193)>>>0
hue  = ['--r1','--r2','--r3','--live'][h % 4]
bits = fnv1a32(key + ':cells')
row r(0..4): half=[bit(r*3+0),bit(r*3+1),bit(r*3+2)] → [h0,h1,h2,h1,h0]  // 세로축 대칭
```

- 렌더: `display:grid; grid-template-columns: repeat(5,1fr); width/height = size;`
  배경 `rgba(255,255,255,.06)`, `border: 1px solid var(--border-soft)`, 셀 = 채워지면 hue, 아니면 투명.
- `role="img"` + `aria-label`(기본 「계정 아이디콘」). 사각형만, 라운드·그림자·그라디언트 없음.
- `--alert`·`--brand` 사용 금지. 크기는 20/28/40만 (size/5가 정수).
- 시드: 이메일 문자열 또는 서버가 주는 per-account 시드 — 둘 중 무엇이든 이 함수의 입력일 뿐.

## 6. 의견 보내기 (신규 `Feedback.tsx`)

**진입점 2개**: 푸터 버튼, 모바일 시트 행. `data-vocky-trigger` 속성과 `VockyScript.tsx`(외부 스크립트
seam) **삭제** — 위젯은 존재하지 않으며 우리가 UI를 소유한다.

- desktop: 진입점 기준 앵커 패널 — `position:absolute; right:0; bottom: calc(100% + 10px); width:380px;
  z-index:20`, 배경 `#0e1a15`, `border:1px solid var(--border-strong)`, `box-shadow: var(--panel-glow)`.
- ≤480: 전폭 하단 시트 — `position:fixed; left:0; right:0; bottom:0`, 같은 표면, 좌우/하단 보더 없음,
  백드롭 `rgba(10,19,16,.72)` `position:fixed; inset:0`. 열 때 메뉴 시트는 닫는다. body 스크롤 잠금.
- 내부: 헤더(제목 `--text-md`/600 + × 28×28 하이라인 버튼) · 안내 `--text-base` `--ink-2` ·
  `<textarea>`(`min-height:104px`, 모바일 `120px`, 배경 `rgba(255,255,255,.045)`,
  `1px var(--border-strong)`, `--text-base`, placeholder `--ink-3`, 포커스 2px `--focus-ring`) ·
  fine print `--text-xs` `--ink-3` · 액션 우측 정렬(닫기 quiet + 보내기 솔리드 `--live-solid`/#fff,
  `height:36px`, 모바일 `min-height:48px`).
- 열림 = 200ms 페이드, reduced-motion = 컷. 닫힘 = ×, 닫기, Esc, 백드롭(모바일), 경로 변경.
  **우하단 모서리는 비운다** (AI 질문 런처). 어떤 상태에서도 떠 있는 원형 버튼을 만들지 않는다.
- 포커스: 열릴 때 textarea로 이동, 닫힐 때 진입점으로 복귀. `role="dialog"` + `aria-label="의견 보내기"`.

### 상태 기계

| 상태 | 화면 |
|---|---|
| idle (빈 입력) | 보내기 `disabled` (배경 없음, `--border-strong`, `--ink-3`) + 힌트 「내용을 입력하면 보낼 수 있습니다.」 · **오류 색 없음** |
| typing | 보내기 활성. 공백만 입력하면 다시 idle 취급 (trim) |
| sending | textarea `readOnly` + 흐리게(`rgba(255,255,255,.02)`, `--ink-2`), 버튼 라벨 「보내는 중입니다」 disabled, 닫기 숨김. **스피너·회전 금지** |
| sent (202) | 본문 교체: 「의견이 접수되었습니다.」 + `접수 번호 <mono request_id>` inset 박스 + fine print, 액션은 「닫기」 하나 |
| failed | 「의견을 보내지 못했습니다. 잠시 후 다시 시도해 주십시오.」 + 입력 내용 inset 보존 + 「입력한 내용은 그대로 남아 있습니다.」 + 「다시 시도」. **`--alert` 사용 금지** |

### API

- 브라우저 → `POST /api/feedback` (미주알, same-origin, JSON `{ message: string }`).
- 서버 라우트가 vocky로 전달: `POST ${VOCKY_API_BASE}/api/feedback`,
  `Authorization: Bearer ${VOCKY_API_KEY}` (서버 `.env`만; 클라이언트 번들·로그·기록에 절대 금지),
  본문:

```json
{ "message": "<사용자 입력, trim, 비어 있으면 400>",
  "source": { "product": "mijual" },
  "recorded_by": "human",
  "channel": "web" | "mobile",
  "target_type": "surface",
  "session_id": "<있으면 익명 세션 id>" }
```

  `feedback_value`·`comment`·`tags`·`user_id`·`attachment_ids` 미사용 (첨부 업로드 엔드포인트 없음).
  `channel`은 시트에서 열렸으면 `"mobile"`, 푸터에서 열렸으면 `"web"`.
- 응답 처리: `202` → sent (`request_id` 표시) · `400` → failed (입력은 UI에서 이미 막으므로 서버 오류로
  취급) · `401` → failed 유지 **재시도 금지** (키 문제는 독자가 해결 못 함; 서버 로그에 남길 것) ·
  `503`/네트워크/타임아웃(8초) → failed + 다시 시도.
- `/ops/feedback` 대기열(에이전트 `save_feedback`)과의 연결은 **적용 시점 질문** — 이 라운드의 설계
  대상이 아니다.

## 7. 카피 (신규 15 — 등재 필요)

`copy.ts`에 R8 인용과 함께 추가하고 `grounding/copy-inventory.md`에 등재:

| 상수 | 문자열 |
|---|---|
| `HOLDINGS_LABEL_KO` | 보유 종목 |
| `FEEDBACK_TITLE_KO` | 의견 보내기 |
| `FEEDBACK_GUIDE_KO` | 잘못된 수치나 바라는 점을 적어 주십시오. |
| `FEEDBACK_PLACEHOLDER_KO` | 예: 계양전기 청약 기간이 공시와 다릅니다 |
| `FEEDBACK_EMPTY_HINT_KO` | 내용을 입력하면 보낼 수 있습니다. |
| `FEEDBACK_FINE_KO` | 연락처를 받지 않으므로 답장은 드리지 못합니다. 이메일·계정 정보는 함께 보내지 않습니다. |
| `FEEDBACK_SEND_KO` | 보내기 |
| `FEEDBACK_SENDING_KO` | 보내는 중입니다 |
| `FEEDBACK_SENT_KO` | 의견이 접수되었습니다. |
| `FEEDBACK_RECEIPT_LABEL_KO` | 접수 번호 |
| `FEEDBACK_RECEIPT_FINE_KO` | 접수 번호는 문의 확인용 표기입니다. 답장은 드리지 못합니다. |
| `FEEDBACK_FAILED_KO` | 의견을 보내지 못했습니다. 잠시 후 다시 시도해 주십시오. |
| `FEEDBACK_KEPT_KO` | 입력한 내용은 그대로 남아 있습니다. |
| `FEEDBACK_RETRY_KO` | 다시 시도 |
| `FEEDBACK_CLOSE_KO` | 닫기 |

기존 `VOCKY_ROW_KO`(「의견 보내기」)는 진입점 라벨로 재사용하고 `VOCKY_NAV_KO`(「[의견]」)는 삭제.
삭제 대상 상수: `VOCKY_NAV_KO`, `POSITIONING_KO`, `PROVENANCE_KO`, `GATE_COST_*`, `DISCLAIMER_KO`
(§6-1 이전 결정 확인 후).

## 8. 작업 순서 (권장) 및 삭제 목록

1. **Identicon** (`frontend/components/Identicon.tsx`) — 의존 없음, 먼저.
2. **copy.ts** — §7 신규 15개 추가 + 삭제 대상 상수 제거 (`GATE_COST_*`·`DISCLAIMER_KO`는 §6-1 결정 확인 후).
3. **Feedback.tsx + Feedback.module.css + `app/api/feedback/route.ts`** — 상태 기계와 계약은 §6.
   `.env.example`에 `VOCKY_API_KEY`, `VOCKY_API_BASE` 키 이름만 추가 (값 금지).
4. **AccountSlot.tsx / .module.css** — §2 (+ `abbreviateEmail` 호출 제거).
5. **Nav.tsx / .module.css** — §1 목적지 표 + §3 모바일 시트/백드롭.
6. **Footer.tsx / .module.css** — §4, 의견 진입점 연결.
7. **랜딩 컴포넌트** — 「샘플로 열어보기 →」 링크와 빈 밴드 제거.

**삭제할 파일**: `VockyTrigger.tsx`(+ `.module.css`), `VockyScript.tsx`.
**삭제할 상수**: `VOCKY_NAV_KO`, `SAMPLE_CHIP_KO`, `SAMPLE_EXIT_KO`, `POSITIONING_KO`,
`PROVENANCE_KO`, `GATE_COST_VALUE_KO`, `GATE_COST_TAIL_KO`, `DISCLAIMER_KO`.
**삭제할 코드 경로**: 크롬의 샘플 로드 상태 분기, `data-vocky-trigger` 속성, 푸터 mono fine-print 행.

### 완료 확인 (이 라운드가 끝났다고 말할 수 있는 조건)

- [ ] nav에 링크가 **두 개**뿐 (관제 현황판 링크·[의견] 칩·샘플 칩·샘플 종료 중 어느 것도 DOM에 없다).
- [ ] 랜딩에서 활성 밑줄이 없는데도 워드마크로 현황판에 갈 수 있다.
- [ ] 계정 프레임이 **전체 이메일**을 보여주고, 메뉴가 프레임 우변에 정렬되며 코스모스가 비쳐 보이지 않는다.
- [ ] ≤480 시트가 본문을 밀지 않고, 백드롭 탭·Esc·× 로 닫히며, 모든 탭 대상이 ≥48px.
- [ ] 푸터에 mono가 없고, 줄은 하나이며, 390px에서 「AI 질문」이 고아 줄이 되지 않는다.
- [ ] 의견 보내기: 빈 입력에서 보내기 비활성 · 전송 중 스피너 없음 · 실패에 빨강 없음 · 202에서 접수 번호 표시.
- [ ] 클라이언트 번들에 `VOCKY_API_KEY` 문자열이 존재하지 않는다 (빌드 산출물 grep).
- [ ] 우하단 모서리에 떠 있는 버튼이 없다 (AI 질문 런처만).

## 9. 불변 (건드리지 말 것)

R1 토큰·타입·간격·모션·사각/하이라인 시스템 · `.cosmos` 스코프 · 숫자만 mono · 52px 바 · 활성 밑줄 ·
호버(색 변화) · P7 포커스 분리 · R5-1 로그아웃 즉시 · R6 런처 모서리 ·
`/ops` 크롬 격리 · 404 Next 기본 · favicon 미정(D5).
