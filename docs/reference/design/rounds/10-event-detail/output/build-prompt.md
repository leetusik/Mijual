# R10 — Build prompt (P8.S6: 이벤트 상세 ①②③ + 신뢰 상태 폴리시)

구현 대상: `frontend/app/events/[rcept_no]/page.tsx` · `frontend/components/event/*` ·
`frontend/components/Citation.tsx` · **신규** `frontend/app/not-found.tsx`.
**신규 기능 없음** — 페이로드도, 필드도, 계산도 추가하지 않는다. 아래는 전부 표기·상태·기하다.
정본: `detail/r10-detail.css` (기하) · `detail/r10-parts.jsx` (구조) · `components/Citation.jsx` (재컷).
토큰 변경 없음.

## 0. 공통 규칙

- 한국어 `word-break:keep-all`, 모든 mono 값 `white-space:nowrap`, 숫자는 `font-variant-numeric:tabular-nums`.
- 히트 하한: 데스크톱 32px, **≤767px 44px** (인용 트리거·rcept 링크·버튼·질문 칩 전부).
- 전역 `box-sizing:border-box` (전폭 44px 버튼이 패딩 때문에 넘치지 않게).
- 브레이크포인트는 **767px** 하나만 쓴다 (이 표면의 모바일 규칙 전체가 여기서 전환).
- 모션은 R1 그대로 (120/200/320ms, 단일 ease). 신규 애니메이션 없음.

## 1. 헤더 (`Header.tsx`)

기하: `display:grid; grid-template-columns:minmax(0,1fr) auto; gap:14px 24px; padding:18px 20px 14px`.
**크기 통일**: `min-height:136px` + `align-content:start` (데스크톱), ≤767px `min-height:248px` + `align-content:space-between` — 네 상태(열림·닫힘·추후결정·부재)가 같은 높이를 차지한다. 상태에 따라 헤더가 커지거나 줄어들지 않는다.
좌: RightsChip(`justify-self:start`) → `h1` 회사명 `text-2xl/700/-0.02em` + `DART 원문 ↗`(mono `text-sm`, `--ink-3`, inline-flex, min-height 32px) → 본문 표기 줄(조건부) → 메타 줄.
우(`.cd`): 라벨 `text-sm --ink-2` → DDay / StateBadge / 부재 칩 → 창 줄 → 담기 링크.

**메타 줄** — `display:flex;flex-wrap:wrap;column-gap:8px;row-gap:4px`, 각 항목 `nowrap`,
구분점은 `span+span:not(.corr)::before{content:"·";margin-right:8px}`.
「정정 반영」은 `.corr` = 1px `--border-soft` 하이라인 칩(`padding:1px 6px`).
≤767px: `span:first-child{flex:1 0 100%}` + 구분점 `content:none`.

**창 상태 (표 그대로 구현)** — `window_state`와 `rights_type`만 본다. 날짜는 언제나 렌더한다.

| 조건 | 상태어 | 표기 |
| --- | --- | --- |
| ① `window_state==='open'` | `거래 가능 · 마감 {dday}` | `--live` |
| ① `window_state==='closed'` | **`기한 지남`** | `.past` 칩 (`--surface-inset` / `--ink-3`) |
| ② 개시일 지남 | `진행 중` | `--live` · **「종료」 금지** |
| ② 개시 전 | 없음 | 날짜만 |
| ③ 단계 마감 지남 | `기한 지남` | 단계 블록의 칩 (기존) |

**카운트다운 칸 3형태** — ① `DDay`(서버 계산) · ② 추후결정 = `StateBadge kind="tbd"` + 「카운트다운 없음 — 일정이 공시상 미정」 · ③ 필드 부재 = **점선 칩** `.absent` (1px dashed `--border-strong`, mono `text-sm`, `--ink-3`)에 「현재 버전 공시에 없음」. 점선/실선의 구별이 계약이다.

**담기 줄** — 문구는 **「보유 종목에 담기 →」** (R5-2의 「내 포트폴리오에 담기 →」 대체 · nav 라벨과 일치 · `copy-inventory` 갱신 필요). 텍스트 링크(밑줄, `--ink-2`, hover `--live`), 기존 게이트 유지(`days >= 0`), ≤767px min-height 44px.

**≤767px 스택** — 한 열, `padding:16px 16px 12px`; `.cd`는 좌측 정렬; `DART 원문`은 `order:9` + 1px `--border-strong` + 전폭 + 44px + `--ink-1`. 순서: 유형칩·회사·(본문 표기)·메타 → 라벨 → DDay → 창 줄 → 담기 → DART → 질문 스트립 → 본문.

## 2. ① 환산 블록 (`Offering.tsx`)

**화살표 삭제** (`styles.chainArrow` 제거). 래퍼는 `--surface-raised` + 1px `--border-soft`.
셀: `display:grid;grid-auto-flow:column;grid-auto-columns:minmax(0,1fr)`, 각 셀 `padding:12px 16px`,
`border-left:1px dashed --border-soft` (첫 셀 제외), 내부 `라벨(mono 10px --ink-3) / 값(mono text-md 600)`.
- 확정 전: 첫 셀은 **라벨 없이** `발행가 확정 전` 칩 + `확정 예정 {date}` (mono text-sm `--ink-2`). 예정발행가는 여전히 렌더 금지.
- 이론가치: `EstimateMarker`만, 인용 없음. 배정비율: 10자리 전체, `text-base` + `nowrap`, 인용 없음.
- 인용은 `figure.quote`가 있는 셀에만 (`Citation`이 이미 빈 경우 무렴).
하단 줄(`.chainfoot`, dashed top): 좌측 설명 문장(있을 때) · 우측 `내 보유량으로 환산 →` = 1px `--border-strong` 버튼, `min-height:44px`, hover `--surface-inset`, focus 2px `--focus-ring` offset 2.
**≤767px**: `grid-auto-flow:row`; 셀은 `grid-template-columns:minmax(0,1fr) auto`(라벨 좌 · 값 우, `align-items:baseline`), `border-top` dashed, `min-height:44px`; 환산 버튼 전폭.
청약 결과 inset은 R3 그대로(`--surface-inset`), 소멸가치는 `--alert` + 「추정」 + 하한.

## 3. ② 팩트 스트립 (`Convertible.tsx`)

- 격자 **3열 × 2행 고정** (`repeat(3,minmax(0,1fr))`), 1px `--border-soft` 프레임 + 내부 dashed. 6칸 = 전환가액 · 오버행 (주식총수 대비) · 전환 시 주식수 · 권면총액 · 발행방법 · 만기. 「전환 시 주식수」는 독립 칸 (오버행 칸의 보조 문구 아님).
- 프레임 바로 아래 **출처 줄** `.fsrc`: `--surface-inset`, mono 10px `--ink-3`, 좌 `DART 공시 API` · 우 `{rcept_no} ↗`(32px / 모바일 44px). 스트립 칸에는 `[근거]`를 달지 않는다.
- 아래 본문 섹션은 `// 발행 조건` + 행마다 `[근거]`. 두 표면의 차이가 프로비넌스 차이다.
- **두 부분 값**: 값 줄(mono) + `.sub` 사유 줄(`text-sm --ink-2`). em dash 한 줄 연결 금지.
- 콜·풋 카드·구간 캡션은 R3 그대로, 구간 날짜 `nowrap`.
- sparse ②: 스트립 + 출처 줄 + 잠금 종결 문장(자리표시자 없음).
- ≤767px: 1열 6행.

## 4. ③ 2단계 절차 (`Fields.tsx` / 절차 블록)

`grid-template-columns:68px minmax(0,1fr)` (≤767px 60px), 단계 번호는 「1단계 / 2단계」를 담는 하이라인 필(높이 24px · `padding:0 8px` · mono `text-xs` · `nowrap`) — 정사각 박스에 넣지 않는다.
단계 제목 `h3`, 창은 mono `nowrap`, 지난 단계는 `--ink-2/--ink-3` + `기한 지남` 칩.
의존 문장은 `STEP_DEPENDENCY_KO` 한 문장만.

## 5. 필드 행 · 제목 의미 (`Fields.tsx`)

행: `grid-template-columns:220px minmax(0,1fr); gap:16px; padding:11px 20px; border-top:1px dashed`.
≤767px: 한 열(`gap:2px`), 취급처 등 하위 표도 한 열 스택 (mono 날짜는 `justify-self:start`).
**아이브로는 `h2`**: `.eyebrow::before{content:"// "}` — 접근 가능한 이름에 `//`가 들어가지 않게 한다. 정정 밴드 문장도 `h2`. 페이지 개요 = h1 회사명 → h2들.

**인용은 행마다 달지 않는다 (운영자 지시)** — 구현 규칙:
- 담기 줄 문구는 **「보유 종목에 담기 →」** (「포트폴리오」 금지).
- `[근거]`를 **단다**: 값이 산문에서 **추출된** 날짜·수치·비율 또는 파생값의 입력인 행/셀 — 매매기간, 초과청약 비율, 확정발행가, 할인율, 보호예수 해제일, 청약 결과 수치, 정정 요약, 철회 근거.
- **달지 않는다**: 값이 필러의 문장을 **1:1로 싣는** 행 — 발행가액 산정방법, 청약 취급처 표, 리픽싱 조건, 콜·풋 스케줄, 통지 방법·접수처. 인용 패널이 화면의 글을 되풀이할 뿐이다.
- 대신 **섹션마다 마지막 한 줄**: `.secsrc` — dashed top, 우상단 정렬(≤767px 좌정렬), mono `text-xs` `--ink-3`, `DART 원문 {rcept_no} ↗`, 히트 32px / 모바일 44px. 인용 칩이 하나도 없는 섹션에서는 필수다.
- 하단 프로버넌스 문장은 그대로 (잠금) — 칩을 줄여도 모든 값은 여전히 한 번의 탭으로 원문에 닿는다.

## 6. 인용 (`Citation.tsx`)

- 트리거: `<button aria-expanded>` `[근거]` mono `text-xs/500` `--live`, `text-decoration:underline dotted`, `padding:8px 6px`, `margin:-8px -2px`, `min-height:32px`, `display:inline-flex`.
- hover = `--live-tint` 채움 + 밑줄 해제 · focus-visible = 2px `--focus-ring` · **열림 = `--live-tint` 채움 + `×`(`--ink-3`) + `aria-expanded="true"`** (닫기는 같은 버튼 재클릭, 문구 없음).
- **팝오버**(인라인 패널 아님): `position:absolute; top:calc(100% + 6px)`, 폭 380px(모바일 `calc(100vw - 44px)`, 최대 340px), **불투명 `#0e1a15`** + 1px `--border-strong` + 2px `--live` 좌변, verbatim `pre-wrap` `max-height:200px` 스크롤, 우상단 `×`(28px / 모바일 44px), 하단 `DART 원문 {rcept} ↗`. 닫기 = `×` · 바깥 클릭 · Esc. 행은 움직이지 않는다.
- **≤767px**: 트리거 `min-height:44px; padding:13px 8px; margin:-8px -4px`; 패널 링크는 전폭 44px 하이라인 행.
- 컴포넌트가 자기 CSS를 한 번 주입(또는 CSS 모듈로 이관) — 미디어 쿼리가 필수다. props 변경 없음.

## 7. 정정 밴드 · 스토리 (`Corrections.tsx`)

- 밴드: `--surface-raised`, 문장 `h2`, 버튼 `.hist` 36px(모바일 44px 전폭).
- **버튼 라벨**: 닫힘 `정정 이력` → 열림 **`접기`** + `×`. 열려 있는 동안 `--surface-inset` + `--ink-2` 테두리. `aria-expanded`/`aria-controls` 유지, 첫 열림에 corrections 요청도 그대로.
- 레일: 행 `min-height:44px`, 접수번호 링크가 행 높이를 채움, `is_current_readable`만 칠해진 마커 + 「현재 읽는 버전」 배지. 이전 버전 주석 없음. ≤767px에서는 3열(마커 / 날짜·종류·링크 / 배지)로 접힌다.
- **필드 무브**: 화살표 열 삭제. 각 무브 = 라벨 + `.mpair` 2열(`정정 전` / `정정 후`), 각 쪽은 1px `--border-soft` 박스 + mono 10px 태그. 정정 후 쪽만 `--surface-raised` + `--ink-1` 600. `new === null` → 「(정정 후 본문에서 삭제됨)」. ≤767px: 세로 스택(두 번째 쪽의 `border-left`를 `border-top`으로).
- 요약: verbatim + `schedule_impact` bold + `[근거]`.
- **이전 버전 URL은 무언(Q-C)** — 리다이렉트도, 안내 줄도 만들지 않는다.

## 8. 404 (`frontend/app/not-found.tsx`, 신규)

- `page.tsx`의 `notFound()`가 이 파일로 떨어진다. 상태 코드 404 유지, R8 크롬(nav + 푸터) 안에서 렌더.
- 내용 4개, 순서대로: `h1` **「이 주소에 해당하는 공시가 없습니다」** (text-2xl/700) · 본문 **「관제 현황판에서 감시 중인 공시를 확인하실 수 있습니다.」** (text-base `--ink-2`) · 요청 경로 mono(`--surface-inset`, `padding:6px 10px`, `word-break:break-all`, **라벨 없음**) · 버튼 **「관제 현황판으로 →」** (1px `--border-strong`, 44px, 모바일 전폭) → `/`.
- **이유를 말하지 않는다**: flagged / incomplete / 실적보고서 / 오타를 구별하지 않고, 게이트·사유 코드·「없는 이유」를 절대 노출하지 않는다.
- 신규 카피 3개는 `copy-inventory.md`에 `not-found` 항목으로 등재 후 사용.

## 9. 질문 스트립 (배치만)

헤더 패널 하단에 `border-top:1px solid --border-soft`로 붙인다. `padding:10px 20px`(모바일 16px), 가로 스크롤 + 스크롤바 숨김, 칩 `min-height:36px`(모바일 44px), 마지막 「직접 질문 입력 →」은 `--border-strong` + `--ink-1`. 스트립 자체 설계·카피는 surface 7 / R14 — 이 라운드에서 바꾸지 않는다.

## 10. 회귀 체크리스트

0. 헤더 패널 높이가 네 상태에서 동일하다 (데스크톱 136px / 모바일 248px 하한).
1. 390px에서 체인·diff·메타 줄에 고아 기호(`→`, `·`)가 하나도 없다.
2. 모든 인용 트리거·rcept 링크·버튼이 모바일에서 44px 이상 (DevTools로 실측).
3. 한 섹션에 `[근거]`가 행마다 반복되지 않고, verbatim 행만 있는 섹션은 `.secsrc` 한 줄로 닫힌다.
4. 「정정 이력」을 열면 라벨이 「접기」로 바뀌고 버튼 표면이 변한다.
5. 닫힌 ① 창에 「기한 지남」이 뜨고, ② 과거 개시일에는 여전히 「진행 중」이며 「종료」는 어디에도 없다.
6. 아시아나 페이지: 점선 칩 두 곳(카운트다운·필드 행), 자리표시자 없음, 이유 없음.
7. 스크린리더 개요에 h2들이 보이고 이름에 `//`가 없다.
8. `/events/{존재하지 않는 rcept}`가 한국어 404, 상태 코드 404, 이유 없음.
9. 모든 mono 날짜·수치가 어떤 폭에서도 쪼개지지 않는다.
