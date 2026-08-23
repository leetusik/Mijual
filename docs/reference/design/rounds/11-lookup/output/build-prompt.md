# R11 — Build prompt (P8.S9: 내 종목 조회 + 놓친 돈 조회기)

구현 대상: `frontend/app/stocks/page.tsx` · `frontend/app/stocks/[corp_code]/page.tsx` ·
`frontend/components/lookup/*` (`LookupHeader` · `StockView` · `HoldingStrip` ·
`RightsSection` · `MissedMoney` · `LookupEmpty` · `Lookup.module.css` · `copy.ts`).
**신규 기능 없음** — 페이로드·필드·계산을 추가하지 않는다. 전부 표기·상태·기하다.
정본: `lookup/r11-lookup.css` (기하) · `lookup/r11-parts.jsx` (구조) · 카드 6장.
토큰 변경 없음. `SearchRow`/`Citation`은 R9/R10 그대로 — 수정 금지.

## 0. 공통 규칙 (R10 §0을 이 표면에도 그대로)

- 한국어 `word-break:keep-all`, mono 값 `white-space:nowrap`, 숫자 `font-variant-numeric:tabular-nums`.
- 히트 하한: 데스크톱 32px, **≤767px 44px**.
- 전역 `box-sizing:border-box`.
- **브레이크포인트는 767px 하나**. `Lookup.module.css`의 `480px` 쿼리를 전부 이 값으로 이관한다
  (중간 레이아웃을 만들지 않는다).
- 모션은 R1 그대로. 신규 애니메이션 없음.

## 1. 라우트별 골격

**`/stocks` (질의 없음 · 불일치)** — `.page.narrow` (620px): 레일(`← 관제 현황판`만) → `h1`
「내 종목 조회」 → 히어로 서브라인 → 검색 행(48px) → (불일치일 때) 불일치 문장 → **맥락 패널**
(감시 대상 3종 칩 + 「감시 중 {n}건」) → `h2 집계 범위` 패널 → 프로비넌스. **Q-A = (b)**:
리다이렉트 금지, 신규 카피 금지.

**`/stocks/{corp_code}`** — `.page` (960px): 레일(`← 관제 현황판` · `내 종목 조회`) →
**아이덴티티 패널** → `h2 진행 중인 권리 — N건` → `h2 2026년 놓친 돈` → `h2 집계 범위` →
프로비넌스. **h1 「내 종목 조회」와 히어로 서브라인은 결과 페이지에 렌더하지 않는다.**

## 2. 아이덴티티 패널 (신규 · `LookupHeader` 재구성)

`.idp{display:grid;grid-template-columns:minmax(0,1fr) minmax(300px,400px);gap:12px 24px;padding:16px 20px 14px}`

- 좌: `h1.corp` 종목명 (`text-2xl/700/-0.02em`) + `.idmeta` 모노 `text-xs` —
  **`stock.stock_code`가 있으면 「종목코드 {code}」가 먼저**, 이어서 「고유번호 {corp_code}」,
  구분점은 뒤 항목의 `::before`.
- 우: `SearchRow`(변형 `surface`, 44px) — `defaultValue = stock.corp_name`. **결과 위에서 빈
  입력 금지.** 후보 패널은 `.field`(position:relative)에 그대로 매단다.
- 하단 레일: 보유량 strip (§3). 없으면 패널은 한 블록으로 끝난다.

## 3. 보유량 strip (`HoldingStrip`)

**렌더 조건 (Q-C)** — `rights.rows`에 살아 있는 ①이 있거나 `lapse.rows.length > 0`일 때만.
그 밖에는 **렌더하지 않는다** (비활성 컨트롤도, 설명 문장도 없다).

`.strip{display:flex;align-items:center;gap:10px;flex-wrap:wrap;padding:10px 20px;border-top:1px solid var(--border-soft);background:var(--surface-raised)}`
- `label[for=held]` 「보유 주식 수」 → `input.num` (mono, 우정렬, 44px, `inputMode="numeric"`)
  → 「주」 → 프리셋 3개(36px 데스크톱 / 44px 모바일, `aria-pressed`, 선택 = `--surface-inset` +
  `--ink-1` + `--ink-2` 테두리) → 복원 칩(**점선**, `이전 입력 {n}주`) → `.stripcap`
  「서버 전송 없음」 (mono **`text-xs`**, `margin-left:auto`).
- **칩 문법**: 실선 = 지금 설정할 값 · 점선 = 지난 세션의 제안. 두 문법이 섞이지 않게 한다.
- 세션 메모리·복원 칩 동작은 R4 그대로 (자동 채움 금지, 서버 전송 금지).

## 4. 진행 중인 권리 (`RightsSection`)

**패널 제목 규칙** — 한 종목 페이지에서 **회사명은 h1에만**. 패널 헤드:
`.rhead{grid-template-columns:minmax(0,1fr) auto}` · 좌: `RightsChip` + `.rmeta`
(`접수번호 {rcept}` · `{filed} 공시` · `정정 반영`) · 우: **`h3.whenlab` = `countdown.label_ko`**
→ `DDay` / `StateBadge state="tbd"` → `.win` 창 줄(열림이면 `--live` 문구, 닫힘이면 `기한 지남` 칩).

**① 패널** — `.chainwrap` 안에 `.chain`(R10 §2 계기 셀: `grid-auto-flow:column`, 셀마다
`border-left:1px dashed`, 라벨 mono 10px / 값 mono `text-md` 600):
- 보유량 **있음**: `보유` · `배정비율 (1주당)`(10자리 전체, `.ratio` = `text-base`, nowrap) ·
  `배정 신주`(+ 셀 안 두 번째 줄에 `= {n}주 × {ratio} · 1주 미만 버림`) · `초과청약 한도 +{k}주`.
- 보유량 **없음**: **두 셀** — `배정비율 (1주당)` · `초과청약 비율 {pct}` (공시가 말한 값만).
  한 줄이 홀로 매달리지 않게 한다.
- `.chainfoot`: 좌 = `발행가 확정 전` 칩 + `확정 예정 {date} — 확정 후 증서 이론가치와 금액을
  환산합니다` (확정발행가가 있으면 R4의 환산액 줄) · 우 = **입력 프롬프트**(§6)를 보유량이 없을 때만.
- 그 아래 `.rowline`: 구주주 청약 · 일반공모 창. **예정발행가는 렌더 금지** (R10과 동일).

**② — 유형당 한 표** (`Dilution` 대체). 패널 하나 안에:
`.ctop`(RightsChip 한 번) → `.ctrow.cthead`(mono 10px: 공시 · 전환가액 · 전환 시 주식수 ·
오버행 · 전환청구 개시 · —) → 건마다 `.ctrow`
(`grid-template-columns:minmax(0,1.1fr) .8fr .9fr .62fr minmax(0,1.25fr) auto`):
공시일(mono `text-sm`) + 접수번호(mono `text-xs`) · 전환가액 · 전환 시 주식수 · 오버행 ·
`{개시일} + DDay` · `상세 보기 →`. **서빙되지 않은 값은 `.ctmiss`(mono `--ink-3`)로 비운다 —
0도, 대시 문장도 만들지 않는다.** 표 하단 `.ctsrc`: 좌 `DART 공시 API — 전환가액 · 전환 시
주식수 · 오버행`, 우 `{n}건`. **칸마다 `[근거]`를 달지 않는다** (R10 §3의 티어 규칙).
개시일이 지난 건은 창 줄에 `진행 중` (「종료」 금지, `ui-traps` #5).

**③ 패널** — 헤드는 위와 같고(`dday: null` → `StateBadge state="tbd"` + `일정이 공시상 미정`),
본문은 R10 §4 절차 블록: `.steps` → 단계마다 `68px` 필(`1단계`/`2단계`) + 제목 `h4` + 창 mono,
지난 단계는 `.pastStep` + `기한 지남` 칩, **창이 공시에 없으면 점선 `.absent`
「현재 버전 공시에 없음」**. 마지막에 의존 문장 한 줄
(`1단계에서 반대의사를 통지한 주주만 행사 가능`). 매수예정가는 이 표면에 없다.

**0건** — 섹션을 비우지 않는다: `.closed` 「청약 {subscription_end} 종료」(있는 만큼).

**이벤트로 가는 길 (한 규칙)** — `상세 보기 →` (`.golink`, 밑줄 텍스트 링크, 32/44px):
① 패널 하단 `.rowfoot`, ② 행 끝, 놓친 돈 건의 이름 아래. **접수번호는 링크가 아니다.**

## 5. 2026년 놓친 돈 (`MissedMoney`)

`.mmhead`: 프레임 문장(`MISSED_FRAME_KO`) → (보유량 없음일 때) 프롬프트 → `.mmcap`
「유상증자 {n}건 · 집계 범위 {start} ~ 오늘 (KST) · 시장 가격 미사용 — 소멸된 증서의 이론가치 환산」.

**합계 규칙** — `lapse.rows.length >= 2` **일 때만** `.total`(`text-3xl/700`, `EstimateMarker`
+ `하한`)을 `.mmcap` 위에 그린다. **1건이면 합계를 그리지 않고**, 그 행의 `{n}주 기준` 칸이
`.big`(`text-2xl/700`, `--alert`, 「추정」) + 하한 줄 + `배정 {k}주 × 「추정」{unit}원` 캡션을
가진다. 같은 원화 금액이 한 섹션에 두 번 나오면 안 된다.

**breakdown** — `.brow{grid-template-columns:minmax(0,1.5fr) .95fr minmax(0,1.7fr) minmax(0,1.1fr)}`
+ `.bhead` 라벨 행(유상증자 · 증서 매매기간 · 소멸 계산 (시장 전체) · **`{n}주 기준` / 보유량이
없으면 `보유 주식 수`**).
행: ① 칩 + 건 이름 + 모노 메타(접수번호 / 확정발행가) + `상세 보기 →` · 매매기간 + `기간 지남 ·
D+{n}` 칩(**경보색 금지**) · `발행 − 청약 = 소멸 {k}주 ({rate})` + `EstimateMarker` 시장 소멸가치 ·
내 기준 칸. **보유량이 없으면 마지막 칸은 `.bslot`(점선 빈 자리, 44px)** — 0원도 대시도 넣지 않는다.
`[근거]`는 **자기가 인용하는 칸 안에** 둔다 — 한화솔루션의 인용은 신주인수권증서 상장예정기간이므로
`증서 매매기간` 칸의 「기간 지남」 칩 아래(`.bwin`의 세 번째 요소). 행 전체를 가로지르는 인용 줄을
따로 만들지 않는다 (R10 컴포넌트 그대로, 인용이 있는 건만, 건당 하나).
`.calcfoot`(보유량 있을 때만) = R4의 계산 푸터 문장 · `.disc` = R4 면책 문장 (mono 10px).

**zero 상태** — `이 종목은 2026년 집계 범위에서 놓친 권리가 없습니다` + (살아 있는 ①이 있으면)
`진행 중인 건의 소멸 여부는 청약 종료({subscription_end}) 후 집계됩니다`.

## 6. 입력 프롬프트 (신규 카피 · 유일)

`.prompt` = `<button>` 1px **dashed** `--border-strong`, `min-height:44px`, 문구
**「보유 주식 수를 입력하면 내 보유량 기준으로 환산합니다」** + 모노 `→`.
클릭 → strip 입력에 `focus()`. **페이지당 한 번**: 살아 있는 ① 블록이 있으면 `.chainfoot`,
없으면 `.mmhead`. 보유량이 입력되면 사라진다. `copy-inventory.md`에 `lookup` 항목으로 등재 후 사용.

## 7. 검색 · 불일치 · 후보

- **불일치 문장은 제출된 질의의 것**: 입력값이 제출 질의와 달라지는 첫 타건에 **제거**한다
  (`LookupHeader`가 `missed && query === currentInput`을 렌더 조건으로 갖는다). 후보 패널이
  낡은 문장 위에 겹치는 상태는 존재할 수 없다.
- **조사**: `‘{q}’` 뒤는 한글이면 `(code−0xAC00) % 28 !== 0 ? '과' : '와'`, **한글이 아니면
  `와/과` 병기**. `copy.ts`의 `noMatchKo`만 고친다 (문장 본문은 잠금).
- 후보 패널 자체(`SearchRow.module.css`)는 **수정 금지**.

## 8. 제목 의미 · a11y

- 결과: `h1` 종목명 → `h2` 진행 중인 권리 — N건 → `h3` 마감 라벨 → `h2` 2026년 놓친 돈 →
  `h2` 집계 범위. 진입: `h1` 내 종목 조회 → `h2` 집계 범위.
- `.eyebrow::before{content:"// "}` — 접근 가능한 이름에 `//`가 들어가지 않는다.
- strip은 `label[for]`, 프리셋은 `aria-pressed`, 불일치 문장은 `role="status"`,
  후보 목록은 R9의 `listbox`/`option` 그대로.

## 9. ≤767px

- 아이덴티티 한 열 · 검색 48px · 프리셋 **3열 격자 44px** · 복원 칩 **전폭 44px 자기 줄** ·
  `.stripcap` 자기 줄.
- 환산 셀: `grid-auto-flow:row`, 셀은 `라벨 좌 / 값 우` 44px 행.
- **권리 패널 헤드**: `.rid`/`.rwhen`이 `display:contents`가 되어 한 격자로 풀린다 —
  칩 · 메타(전폭) → **지배 라벨(좌) + D-day/StateBadge(우)가 한 행** → 창 줄(전폭, 좌정렬).
  라벨과 D-day가 갈라져 네 줄로 쌓이지 않게 한다 (R10 헤더의 390 규칙과 같은 서열).
- ② 표 → **건별 카드**: 공시일·접수번호가 첫 줄이고 **개시일 + D-day는 같은 행의 우측**
  (`grid-row:1;grid-column:2`, 세로 스택·우정렬) — 행에서 가장 먼저 읽히는 사실이 헤더에 있다.
  각 값은 `grid-column:1/-1`의 `flex(space-between)` 행이고 라벨은
  `::before{content:attr(data-l)}` 10px 모노. `상세 보기 →`는 44px 전폭 행.
- 놓친 돈 건 → 카드 한 장, 내 기준 블록은 dashed 하이라인 아래 마지막 블록.
- 목표 높이: 한화솔루션 ≈1,250px / 풍전약품 ≈1,150px (walk 대비 −25~45%).

## 10. 회귀 체크리스트

0. `/stocks/{corp_code}` 어느 종목에서도 **종목명이 h1로 한 번** 나오고, 검색 입력이 그 이름을 담는다 (세기상사 포함).
1. 결과 페이지에 「내 종목 조회」 h1과 히어로 서브라인이 **없다**; 레일 라벨로만 남는다.
2. 풍전약품 `01110474`: ② 패널이 하나의 표이고, 「풍전약품」이 페이지에 **한 번**만 인쇄된다.
3. 아시아나 `00138792`: ③의 D-day 자리가 `StateBadge 추후결정`(실선), 창 부재는 **점선** 칩. 두 표기가 섞이지 않는다.
4. `[근거]`가 증서 매매기간 칸 안에 있고, breakdown 행 아래에 인용 전용 줄이 없다. 390에서 ①/③ 패널의 마감 라벨과 D-day가 **같은 행**이고, ② 카드의 D-day가 첫 행 우측이다.
5. 한화솔루션 `00162461` 500주: `679,575원`이 페이지에 **한 번**만 나온다. 보유량을 지우면 프롬프트가 돌아오고 마지막 칸은 점선 빈 자리가 된다.
6. 풍전약품·세기상사에서 **보유량 strip이 렌더되지 않는다**.
7. `/stocks?q=삼성` → 「‘삼성**과** 일치하는」. 이어서 한 글자만 입력하면 문장이 사라지고 그 자리에 후보 패널이 열린다.
8. 빈 `/stocks`에 감시 대상 3종 · 감시 중 건수 · 집계 범위 패널이 있다.
9. 접근성 트리: `//`가 어떤 heading 이름에도 없고, `h2 집계 범위`가 존재한다.
10. 390px 실측: 프리셋·복원 칩·프롬프트·「상세 보기 →」·`[근거]`·크럼·후보 행이 전부 **≥44px**.
11. 481–767px에서 4열 breakdown·220px 라벨 격자가 나타나지 않는다 (경계는 767px 하나).
12. 「추정」 없는 추정 없음 · 확정발행가 없이 금액 없음 · 집계 범위 밖 미기재 · 보유량 미전송 — 넷 다 유지.
