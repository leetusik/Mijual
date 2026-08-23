# 구현 계약 — R9 폴리시: 랜딩 관제 현황판 + 보드 (P8.S5에서 적용)

대상 파일: `frontend/components/landing/{Board.tsx,BoardRow.tsx,Board.module.css,Anchor.tsx,
Anchor.module.css,Hero.module.css,copy.ts}` · `frontend/components/lookup/SearchRow.tsx` (Enter 규칙만) ·
`frontend/app/page.tsx` (갱신을 위한 클라이언트 경계). **토큰 변경 없음** — `foundations/tokens.css` 그대로.

**이번 라운드의 큰 축 6개** — ① 보드 창 15행 ② **고정폭 열 재구성** — D-day는 R2대로 행의 마지막 칸이고, 열이
패널 폭까지 늘어나지 않으므로 CB 행 가운데의 빈 구간이 사라진다 ③ 숫자를 설명하는 메타 줄 + D-day 범례 ④ 행 전체가 클릭 대상 + hover/focus ⑤ 스트립 토글이 상태를
읽고 행이 보드 열에 정렬 ⑥ 페이지가 열려 있는 동안의 자동 갱신 — 보이는 표면은 기준시각 칩과 바뀐 행뿐.

카드 = 정본: `landing/Board.html` · `landing/BoardRow.html` · `landing/BoardStrips.html` ·
`landing/Anchors.html` · `landing/HeroSearch.html` · `landing/Refresh.html` ·
`components/DDayTiers.html` · 기하는 `landing/r9-board.css` (열 구성의 정본, 그대로 이식 가능).

---

## 1. 창 (window)

- `WINDOW_STEP = 30` → **`15`**. 첫 화면 15행, 클릭당 +15. 표시 한도이며 필터가 아니다 (서버 목록·랭킹·
  whole-board `counts` 불변). 탭 전환은 창을 처음(15)으로 되돌린다. **갱신은 되돌리지 않는다** (§7).
- 15행 × 40px ≈ 600px — 두 스트립이 화면 밖으로 밀리지 않는 높이.

## 2. 행 열 구성 (R9 재컷, R2 구성 요소 불변)

행의 **구성 요소와 순서는 R2 그대로** (유형칩 · 회사 600 + `↗` · 카운트다운 라벨 + 날짜 · 유형별 extras ·
**D-day = 행의 마지막 칸, 우측 정렬**). 바뀐 것은 **열 폭과 늘어남**뿐이다.

| 폭 (desktop ≥1120, 패널 내부 1072) | 내용 |
|---|---|
| `76px` | `RightsChip compact` (`flex:none`) |
| `minmax(180px,1fr)` | 회사 600 + `↗` (DART 원문, mono 11 --ink-3) — **행에서 늘어나는 유일한 열** |
| `240px` | 카운트다운 라벨 (12px --ink-2) + 날짜 (mono 12 --ink-1, `nowrap`) |
| `190px` | extras — ① `청약 YYYY-MM-DD` (mono) + `발행가 확정 전` 칩. ②/③ 비어 있음 |
| `96px` | **D-day** — `justify-self:end`, `DDay showDate={false}`, 날짜 없으면 `StateBadge kind="tbd"` |

`gap: var(--space-3)` · `min-height: 44px` · `align-items: center` (내용은 수직 중앙) · `padding: 8px 12px` ·
`margin-inline: -12px` (hover 배경이 패널 여백까지 덮도록) · `border-bottom: 1px dashed var(--border-soft)`.

- **행은 패널을 꽉 채우고 D-day는 패널 우변에 붙는다.** 늘어나는 열은 **회사 하나뿐**이고 값 열은 전부 고정폭이므로
  유형이 섞인 탭에서도, 보드 ↔ 스트립 사이에서도 열이 어긋나지 않는다. walk 6의 ~450px 구멍은 빈 extras 열
  230px과 1fr 회사 열이 겹쳐 생긴 것이므로 **빈 열을 만들지 않는 것**으로 사라진다 — 남는 폭은 종목명 뒤 한 곳.
- **extras 열의 조건부 제거 — 판정은 패널(탭) 단위**: 그 탭의 랭킹 목록과 두 스트립을 합쳐 extras를 가진 행이
  하나도 없으면 (`R2`/`R3` 탭)
  `<ol data-extras="none">` → 템플릿 `76px minmax(180px,1fr) 300px 96px` + `.extras{display:none}` (빈 span이 그리드
  항목으로 남으면 D-day가 다음 줄로 밀린다). 키 날짜 열만 240 → 300으로 넓어지고 D-day는 같은 자리(패널 우변)에 남는다.
  **한 패널 안에서 두 가지 열 구성을 만들지 않는다** — 전체 탭에서는 진행 중 스트립 행도 extras 열을 그대로 쓰고 그 칸이 바어 있을 뿐이다.
- 768–1119: `72px minmax(120px,1fr) 200px 170px 96px` / no-extras `72px minmax(120px,1fr) 240px 96px`.
  **extras 열에 `auto`를 쓰지 않는다** — extras 없는 행에서는 0, 있는 행에서는 ~80px가 되어 한 패널 어디엔가 두 가지 열 구성이 섞이고, 그것이 walk 5가 말한 어긋남이다.
- ≤767 (390): `minmax(0,1fr) auto` 2줄 — 1줄 = 칩 + 회사 + `↗` (좌) · D-day (우), 2줄 = 라벨 + 날짜 · extras
  (`grid-column: 1/-1`, `extras:not(:empty)::before{content:"·"}`), `padding-block: 11px`. R2의 모바일 행 그대로.

## 3. 행 상태 (walk 1)

- **행 전체가 이벤트의 클릭 대상**: `li.row{position:relative}` + `a.corp::after{content:"";position:absolute;inset:0}`
  (stretched link — 접근 가능한 이름은 회사명 그대로, 링크는 하나). `↗`는 `position:relative;z-index:1`로 위에 남는다.
- hover: `background: var(--surface-raised)` + 회사명 밑줄, `cursor:pointer`. **「상세」 같은 지시 문구는 두지 않는다** — 배경과 밑줄이 이미 그 말을 한다.
- `:focus-within`: 같은 배경 + `outline: 2px solid var(--focus-ring); outline-offset:-1px` (행 둘레).
- press: `--surface-inset`. **색 반전 없음** (R1).
- 갱신으로 바뀐 행: `box-shadow: inset 2px 0 0 var(--live)` (§7).

## 4. 탭 · 메타 줄 · 범례 (walk 2·3·7·13)

- 탭 자체는 R2 그대로 (라벨, whole-board `counts`, 활성 = 600 + 2px --ink-1 밑줄, ≥44px 히트,
  `<button aria-pressed>` — `role="tab"` 아님).
- **hover (P7 Q9 결정)**: `color: var(--ink-1)` + `border-bottom-color: var(--border-strong)`.
  `:focus-visible`: 2px `--focus-ring`, `outline-offset:-2px`.
- 탭 아래 **메타 줄** (`--text-xs`, `--ink-3`, `padding: 10px 0 6px`, `justify-content: space-between`):
  - 좌: `탭 숫자는 감시 중 전체 건수입니다 · 아래 목록은 카운트다운 {ranked}건 중 {shown}건`
    (숫자는 mono `--ink-2`). `{ranked}` = 현재 탭의 랭킹 대상 행 수 (`rows.length`), `{shown}` = `min(shown, rows.length)`.
  - 우: **D-day 범례** — `D-DAY`(채운 배지) · `D-7 이내`(--urgency-soon) · `D-30 이내`(--urgency-near) ·
    `30일 초과`(--urgency-far), mono 11. ≤1119에서는 줄바꿈되어 메타 줄 아래로 내려간다.
- 푸터 (창 disclosure): `justify-content:center`, `gap: var(--space-4)`, `padding: 16px 0 18px`
  - 버튼 `{step}건 더 보기` (hairline `.btn`) — **클릭이 더하는 수**
  - 뒤에 mono `남은 {hidden}건` (`--ink-3`) — 남은 수는 버튼에서 분리한다
  - `shown > 15`이면 텍스트 버튼 `처음 15건으로 접기` (밑줄, `--ink-3` → hover `--ink-1`)
  - 남은 것이 없으면 세 컨트롤 모두 없다.
- **컨트롤 높이 (P7 Q11 결정)**: 보드의 모든 버튼 `min-height: 36px` (≥768) / **44px (≤767)**. 32px과 481px
  경계는 폐기 — 터치 하한이 태블릿 대역까지 올라간다 (행 그리드 브레이크포인트와 같은 지점).

## 5. 스트립 (walk 4·5)

- 밴드: `margin-inline: -24px; padding: 12px 24px; background: var(--surface-raised); border-top: 1px solid
  var(--border-strong)` — R2 그대로.
- **토글**: 라벨이 상태를 읽는다 — 닫힘 `펼치기` / 열림 **`접기`** (+ `aria-expanded`). 보드 창의 `접기`와 같은 규칙.
- **펼친 행은 보드 행과 같은 그리드·같은 좌표**: 스트립 안 `.rows .row{margin-inline:-12px}` → 시작선 24px으로
  보드 행과 일치 (오늘의 ~14px 어긋남 제거). 행 위에 `1px dashed var(--border-soft)` 한 줄로 문장과 목록을 나눈다.
- 진행 중 행은 `D+n` (D-day 칸). 「종료」·「마감」 금지 (`ui-traps` #5). extras 칸은 바어 있고, 열은 패널이 정한다.
- **날짜 없는 행**: 키 날짜 칸은 **라벨만** (빈 슬롯도, 대시도 없다). 「추후결정」은 D-day 칸에 선다 — 행마다 「언제」에
  답하는 칸은 하나. `발행가 확정 전` 칩은 extras에 그대로.
- ≤767: 문장 블록 + **전폭 44px 버튼** (혼자 뜬 32px 버튼 제거).

## 6. 앵커 카드 (walk 8·9)

- 카운트다운/지표 카드: `STAT_REPORTS_KO`(읽은 실적보고서) **삭제** — `summary.performance_reports`는 렌더하지
  않는다 (계약 필드는 유지, 화면에서만 제거). 남은 세 지표는 **라벨 좌 / 값 우의 3행**:
  `display:flex; justify-content:space-between; padding: 9px 0; border-bottom: 1px dashed var(--border-soft)`
  (마지막 행 보더 없음), 라벨 `--text-sm --ink-2`, 값 mono 17/600 `nowrap`. 2×2 그리드는 폐기.
- 카운트다운 자체 불변 (mono 28/600 --alert, 콜론 1s step-end, reduced-motion에서 인터벌 정지, 목표는 서버 인스턴트).
- **동시 마감 표기 (walk 8)**: 가장 빠른 청약 마감을 **여러 건이 공유하면** 파이프라인 문장의 `{corp}` 자리에
  종목명 대신 `{n}개 종목`이 들어간다 (문장 형태·낱말 불변). 한 건뿐이면 오늘처럼 종목명. 카운트다운 카드의 캡션도
  같은 규칙: `청약 마감 YYYY-MM-DD (KST) · {n}개 종목`. 판정은 `/board/summary`가 이미 아는 값으로 — 같은 날짜를
  가진 ① 이벤트 수. **없으면 API에 `next_lapse.tie_count`를 추가**하고, 그 전까지는 종목명을 그대로 둔다
  (추측으로 「3개 종목」을 쓰지 않는다).
- 소멸주의보 스트립: mono 날짜와 `({n}개 종목)`은 `white-space:nowrap` (walk 10). 나머지 불변.

## 7. 자동 갱신 — 보이는 계약 (운영자 q5)

페이지가 열려 있는 동안 보드 데이터를 주기적으로 다시 읽는다. **버튼도, 스피너도, 「새로고침」 문구도 없다.**

- **화면의 유일한 갱신 표면은 기준시각 칩**: 새 `as_of`가 오면 스탬프가 바뀌고 옆에 `갱신됨`
  (mono 11, `--live` on `--live-tint`, 2×8) 이 붙어 **다음 갱신까지 남는다** (사라지는 토스트 아님).
  `as_of`가 그대로면 **아무 표시도 하지 않는다**.
- **요청 중에는 화면이 변하지 않는다**: 흐려짐·자리 이동·스켈레톤·스피너 없음.
- **바뀐 행**: D-day·키 날짜·extras 중 하나라도 바뀐 행, 창 안으로 새로 들어온 행 → 행 원본 좌변에 `inset 2px 0 0 var(--live)`,
  바뀐 값만 `--dur-base` 페이드. 다음 갱신에서 엣지 제거. 사라진 행은 애니메이션 없이 사라진다.
- **살아남는 상태**: 활성 탭 · 창 크기(`shown`, 목록이 짧아지면 그 길이로 clamp) · 펼친 스트립 · 스크롤 ·
  포커스 (행은 `event_id` 키로 대체; 포커스 행이 사라진 경우에만 목록으로 이동).
- **문서가 숨겨져 있으면 갱신하지 않고**, 다시 보이면 즉시 한 번 읽는다.
- **실패 시 화면 불변** — 실패 문구를 만들지 않는다 (기준시각이 낡아 가는 것이 그 사실이다). 다음 주기에 재시도.
  결과가 `stale`이면 R2의 처리 그대로 (칩 경고 + 탭 위 안내, 본문 불변).
- **reduced-motion**: 페이드 없음(즉시 교체), 엣지는 표시, 갱신 자체는 계속.
- **주기**: 설계 가정 **60초** (기준시각이 분 단위이므로 더 잦아도 화면에 나타나지 않는다). 실제 값과 fetch 방식
  (라우트 핸들러 재검증 vs 클라이언트 `fetch`)은 이 슬라이스의 결정. `page.tsx`는 서버 fetch를 유지하고 보드만
  클라이언트에서 다시 읽는 형태를 권한다 — 갱신이 히어로의 카운트다운을 리마운트하면 안 된다.

## 8. 히어로 — 프리픽스에서의 맨 Enter (walk 11) + 390 줄바꿈 (walk 10)

- `SearchRow`의 Enter 규칙:
  1. 후보가 열려 있고 **선택된 후보가 없으면** → Enter는 **첫 후보를 선택**한다 (이동·제출 없음, `preventDefault`,
     `aria-activedescendant` 설정 = ↓ 한 번과 같은 상태).
  2. 선택된 후보가 있으면 → 그 후보로 이동 (P7 그대로).
  3. 입력이 후보의 **종목명 또는 종목코드와 정확히 일치**하면 → 첫 Enter가 바로 이동.
  4. 후보가 하나도 없으면 → 오늘처럼 `GET /stocks?q=…` 제출 (JS 없는 경로 유지).
- `/stocks` 쪽 (빈 결과 문구, 조사 「와→과」, 프리픽스 후보 표시)은 **R11 / 표면 4**. 이 라운드는 손대지 않는다.
- 390: 히어로 부제와 모든 한국어 산문에 `word-break: keep-all`, 부제에 `text-wrap: balance`
  (「…조회합니 / 다」 고아 제거). 모든 mono 값(날짜·D-day·금액·건수)은 `white-space: nowrap`.
  `word-break: keep-all`은 랜딩 산문에 전역으로 적용한다 (`app/shell.css` 또는 각 모듈).
- **P7 Q10 결정 = 변경 없음**: 포커스된 입력의 하이라인과 후보 패널의 상단선은 이미 한 선이다
  (패널 `border-top:none`). 포커스 링은 입력에만 둔다. walk 12(패널이 통계 줄을 덮음)도 운영자 지시대로 유지.

## 9. 카피 — 신규 문자열 (전부 `components/landing/copy.ts`, 인용 주석 필수)

이번 라운드에 **열린 카피**(운영자 승인, 2026-08-23): 개수/표시/남은 수 라벨, `접기`, 갱신 상태 라벨.
아래 **신규 상수 14개**가 전부이며, 그 밖의 제품 문구는 잠긴 상태 그대로다.

| 상수 | 문자열 | 자리 |
|---|---|---|
| `TAB_NOTE_KO` | `탭 숫자는 감시 중 전체 건수입니다` | 메타 줄 좌 |
| `shownLine.before` | `아래 목록은 카운트다운 ` | 메타 줄 좌 |
| `shownLine.middle` | `건 중 ` | 〃 |
| `shownLine.after` | `건` | 〃 |
| `moreKo(step)` | `{step}건 더 보기` | 창 푸터 버튼 |
| `remainingKo(n)` | `남은 {n}건` | 창 푸터 |
| `collapseToFirstKo(step)` | `처음 {step}건으로 접기` | 창 푸터 |
| `COLLAPSE_KO` | `접기` | 스트립 토글 (열림) |
| `REFRESHED_KO` | `갱신됨` | 기준시각 칩 옆 |
| `LEGEND_DDAY_KO` | `D-DAY` | 범례 |
| `LEGEND_SOON_KO` | `D-7 이내` | 범례 |
| `LEGEND_NEAR_KO` | `D-30 이내` | 범례 |
| `LEGEND_FAR_KO` | `30일 초과` | 범례 |
| `tieCountKo(n)` | `{n}개 종목` | 소멸주의보 · 카운트다운 캡션 |

`EXPAND_KO`(`펼치기`)는 유지하되 이제 `COLLAPSE_KO`와 짝을 이룬다. 14개 전부 `copy-inventory.md` 꼬리에 등재한다.

**삭제**: `STAT_REPORTS_KO`(읽은 실적보고서 — 운영자 9) · 푸터에서 R8이 뺀 게이트 비용/면책 상수
(`P8 Q5`: 폐기, 재배치 없음 — 랜딩 어디에도 두지 않는다).

## 10. 작업 순서

1. `copy.ts` — 신규 14개 추가, `STAT_REPORTS_KO` 및 게이트 비용/면책 상수 삭제.
2. `Board.module.css` — 열 구성 (§2), 행 상태 (§3), 메타/범례/푸터 (§4), 스트립 (§5). `landing/r9-board.css`가 정본.
3. `BoardRow.tsx` — DOM 순서 유지 (chip+corp → when+extras → D-day), stretched link, 날짜 없는 행, `min-height:44px` + 수직 중앙.
4. `Board.tsx` — `WINDOW_STEP=15`, 메타 줄, 푸터 3컨트롤, 스트립 토글 라벨, `data-extras` 판정.
5. 갱신 (§7) — 보드만 클라이언트에서 다시 읽고, 상태 보존 + 변경 표시 + 칩.
6. `Anchor.tsx`/`.module.css` — 3지표, 동시 마감 표기, 캡션.
7. `SearchRow.tsx` — Enter 규칙 4단.
8. 390 줄바꿈 규칙 (`keep-all`, mono `nowrap`).
9. `copy-inventory.md` 꼬리에 신규 카피 등재 (생성 스크립트가 지우지 않게 주석 유지).

## 11. 완료 확인 체크리스트

- [ ] 첫 화면에 랭킹 15행 · 「15건 더 보기」 + 「남은 N건」, 한 번 누르면 30행 + 「처음 15건으로 접기」
- [ ] 전체 탭에서 탭 숫자(488)와 메타 줄의 랭킹 수(386)가 서로 다르게, 각각 설명된 채로 보인다
- [ ] CB 탭에서 키 날짜와 D-day 사이에 빈 구간이 없고, D-day가 패널 우변에 붙어 있다 (행 오른쪽에 남는 여백 없음)
- [ ] 보드 행과 펼친 스트립 행의 모든 열 x좌표가 일치한다
- [ ] 행 높이가 44px 이상이고 값이 수직 중앙에 있으며, D-day가 다음 줄로 밀리는 행이 없다
- [ ] 행 아무 곳이나 클릭 → 이벤트 상세. `↗`는 DART. 키보드 Tab → 행 둘레 포커스 링
- [ ] 스트립 펼침 후 버튼이 「접기」, 펼친 행의 칩/회사/라벨 x좌표가 위 보드 행과 같다
- [ ] 추후결정 행에 날짜도 대시도 없고, D-day 칸에 「추후결정」이 있다
- [ ] D-day 범례 4단이 탭 아래에 있고, 색이 R1 사다리와 일치한다
- [ ] 카운트다운 카드 지표가 3개이고 「읽은 실적보고서」가 DOM에 없다
- [ ] 소멸주의보와 카운트다운 캡션이 같은 날짜를 말하고, 동시 마감이면 종목명 대신 「N개 종목」
- [ ] 페이지를 열어 두면 기준시각이 갱신되고, 스피너가 뜨지 않으며, 탭·창·펼친 스트립·스크롤이 유지된다
- [ ] 갱신 중/후에 카운트다운이 리마운트되지 않는다 (초가 튀지 않는다)
- [ ] 390px: 부제가 한 음절로 끊기지 않고, mono 날짜가 줄을 넘지 않으며, 스트립 버튼이 전폭 44px
- [ ] 히어로에서 「삼성」 + Enter → 이동하지 않고 첫 후보 선택, 다시 Enter → 이동
- [ ] `prefers-reduced-motion`: 페이드·블링크 정지, 갱신은 계속, 변경 엣지는 표시


## 12. 이 라운드 밖의 지시 (다음 크롬 슬라이스)

- **계정 메뉴에 「의견 보내기」 행 추가** (운영자, R9 세션 — *이번 apply 범위 아님*): 메뉴는
  `알림 설정 / 의견 보내기 / 로그아웃` 세 행이 된다. R8이 만든 미주알 소유 의견 표면을 여는 세 번째 진입점이며
  (푸터 · 모바일 시트 · 계정 메뉴), 새 표면도 새 카피도 없다 — 라벨은 기존 `FEEDBACK_OPEN_KO` 그대로,
  동작은 푸터 링크와 동일 (`chrome/Feedback.tsx` 패널 열기). 카드 `chrome/AccountSlot.html`에 반영해 두었다.
