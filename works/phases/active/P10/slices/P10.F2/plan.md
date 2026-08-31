# Plan — P10.F2 · R18 ②②b 활성 탭이 형제를 밀지 않게

`kind: fix` · `risk: high` · 실행자 `slice-executor-high`

R18(`P10.review`)의 **§②(내비)**와 **§②b(`/ops` 탭 줄)**를 적용한다. `P10.F1`이 §①③④를 이미
끝냈으므로 워드마크·파비콘·README는 이 슬라이스의 일이 아니다.

## 계약

- `docs/reference/design/rounds/18-p10-review/output/handoff.md` **§②**와 **§②b**.
  **읽기 전용 기록 — 편집하지 않는다** (`docs/reference/design/rounds/**` 전부).
- `output/VERIFICATION.md` §3·§5 — 두 결함이 코드에 실재함을 오케스트레이터가 확인한 기록.

## 0. 결함과, 이미 측정된 크기

`.active { font-weight: 600 }`은 **글자 폭**을 바꾼다. 밑줄은 이미 안정적이다 — 비활성 링크가
`border-bottom: 2px solid transparent`로 같은 2px를 예약해 두었고 그 주석은 정확하다. 남은 것이
굵기고, 굵기가 뒤따르는 형제를 민다.

**`P10.F1`이 오늘 1280에서 실측한 기준선** (dev·prod 동일):

| | `/ask` | `/portfolio` |
|---|---|---|
| 첫 링크(`AI 질문`) `left` | 218.75 | 218.75 |
| 둘째 링크(`보유 종목`) `left` | **279.48** | **278.78** |

즉 **0.70px**의 밀림이고, 첫 링크는 두 라우트에서 같으므로 워드마크 폭 변경과는 무관하다.
**수정 후에는 두 배열이 소수점까지 같아야 한다.**

## 1. §② 내비 — 바 링크만

`components/chrome/Nav.module.css`와 `components/chrome/Nav.tsx`에 §②의 diff를 그대로 적용한다:
`.link`를 `inline-grid` + `grid-template-areas: "label"` + `place-items: center` +
`white-space: nowrap`으로, `.link > span { grid-area: label }`, 그리고 `content: attr(data-label)`
· `font-weight: 600` · `height: 0` · `overflow: hidden` · `visibility: hidden` ·
`pointer-events: none`인 `.link::after` 쌍둥이. `Nav.tsx`는 `data-label={link.label}`과
`<span>{link.label}</span>`.

**`visibility: hidden`이지 `opacity: 0`이 아니다** — 전자만 보조기술과 히트 테스트에서 빠진다.
§②의 diff가 그렇게 쓰여 있고, 이유가 있으니 바꾸지 말 것.

**모바일 시트(`.sheetRow` / `.sheetActive`)는 손대지 않는다.** 전폭 세로 목록이라 굵기가 형제를
밀 곳이 없다 — 같은 처방을 넣으면 이유 없는 마크업만 는다. R18이 명시적으로 그렇게 정했다.

**기각된 대안 셋**(활성도 400 · 링크별 `min-width` · 음수 `letter-spacing`)은 §②에 이유와 함께
적혀 있다. 다시 꺼내지 말 것.

## 2. §②b `/ops` 탭 줄 — 같은 결함, 그러나 **드롭인이 아니다**

`components/ops/Ops.module.css`의 `.tab`(71행)과 `.tabActive`(84행), 렌더는
`components/ops/OpsTabs.tsx:29`. 구조는 nav와 같다 — `<Link>` 안에 맨 `{tab.label}`.

**단, 한 군데가 다르고 이것이 이 항목의 유일한 함정이다:**

- **`.tab`에는 `display` 선언이 아예 없다** (nav의 `.link`는 `inline-flex`였다). 그러므로
  `inline-grid`를 **바꿔 넣는 것이 아니라 새로 넣는다.** `align-items: center`도 없으니
  `place-items: center`가 새로 들어온다.
- **`.tab`은 `padding-bottom: 2px`를 갖고 있다** — 유지한다. 쌍둥이는 `height: 0`이라 칸 높이에
  기여하지 않으므로 이 패딩과 충돌하지 않지만, 적용 후 탭 줄의 세로 위치와 밑줄이 그대로인지
  **눈으로 확인**할 것.
- `.tabs`는 `display: flex; align-items: center`다 (nav의 `.links`는 `stretch`). 인라인 그리드가
  그 안에서 예전과 같은 높이로 앉는지 확인.

여섯 탭(개요 · 게이트 대기열 · 정확도·비용 · 대화 로그 · 사용자 · 피드백) 전부에서 확인한다.

**②b는 라운드가 「운영자 판단」으로 남긴 항목이고, 운영자가 2026-08-31에 범위에 넣기로
했다** (`phase.md` `## Operator Questions`). 라운드 문서 자체(§⑦.1)는 아직 이것을 범위 밖으로
적고 있으니, 그 불일치에 혼란스러워하지 말 것 — `phase.md`가 최신이다.

## 3. 범위 밖 — 그리고 **고치지 말 것**

`components/landing/Board.module.css`에도 **같은 쌍**이 있다(`.tab { display: inline-flex }` /
`.tabActive { font-weight: 600 }`, 렌더는 `Board.tsx:407`), 랜딩 보드의 가로 탭 줄이다.
**R18은 이 표면을 보지 않았고, 이 슬라이스도 고치지 않는다.** 이유는 조심스러워서가 아니라
구체적이다: 그 탭은 자식을 셋(`tabFull` · `tabCompact` · `tabCount`) 렌더하므로 `data-label`
쌍둥이 하나로는 그 구성을 재현할 수 없고, `.tabs`가 모바일에서 `overflow-x: auto`다. 처방이
따로 필요하다 = 라운드가 따로 필요하다.

**당신이 할 일은 고치는 것이 아니라 재는 것이다:** 랜딩에서 탭을 바꿔 가며 뒤따르는 탭의
`left`가 실제로 움직이는지 측정하고, 그 숫자를 `result.md`에 남겨라. 오케스트레이터가
`phase.md`의 `## Operator Questions`에 이미 항목을 열어 두었으니, 당신의 실측이 그 항목을
운영자가 결정할 수 있는 것으로 만든다. **움직이지 않으면 그것도 그대로 보고하라.**

그 밖에 손대지 않는 것: `tokens.css`(동결) · `Launcher.module.css` · 워드마크와 파비콘 관련
전부(F1이 끝냈다) · `docs/current/*.md`(생성물) · `.env`.

## 4. 검증

`## Operator Runtime`(`docs/current/operations.md`): `make stack-up` → dev
**`http://127.0.0.1:3010`**, **그리고 프로덕션 빌드도**. `/ops`는 API 프로세스에 일회용
`MIJUAL_OPS_ID` / `MIJUAL_OPS_PASSWORD`가 필요하다 — **`.env`는 절대 열지 않는다**, 환경변수로만.
데스크톱 **1280**, 모바일 **390**.

- **핵심 측정** — 각 목적지에서:
  ```js
  [...document.querySelectorAll('header nav a')].map(a => a.getBoundingClientRect().left)
  ```
  `/ask`와 `/portfolio`의 두 배열이 **소수점까지 동일**해야 한다. 위 §0의 기준선(279.48 /
  278.78)이 하나로 수렴하는 것이 이 슬라이스의 성공 조건이다. `/ops`도 여섯 탭 전부에 대해
  같은 방식으로, 여섯 라우트를 돌며 잰다.
- **잃지 않았는지** — 활성 링크가 여전히 **600 + 흰 2px 밑줄**, `/ops`는 600 + `--ink-1` 밑줄.
  링크 히트 영역이 바 높이 전체. hover 색 반응 유지. `aria-current="page"` 유지.
- **스크린리더가 라벨을 한 번만 읽는지** — 쌍둥이가 접근성 트리에 새는지 보는 것이 목적이다.
  접근성 트리를 덤프해 라벨 중복이 없음을 확인하라(`visibility: hidden`이면 빠져야 한다).
  **이 항목은 이 처방이 틀릴 수 있는 가장 그럴듯한 지점이므로 실제로 확인할 것.**
- **390px**에서 nav 바(브랜드 + 메뉴 버튼)와 시트가 그대로인지 — 시트는 안 건드렸으니 회귀만.
- 회귀: 랜딩 · `/ask` · `/portfolio` · `/stocks` · `/auth` · `/ops` 여섯 탭.

브라우저 계측은 **Aside**(MCP 우선). 못 쓰면 같은 뷰포트·같은 런타임의 실제 브라우저로 같은
것을 확인하고 **`result.md`에 실제로 쓴 도구를 적는다.** 안 한 브라우저 실행을 했다고 쓰지 말 것.
(`P10.F1`은 Aside를 쓸 수 없어 CDP로 실제 Chrome을 몰았고, 그렇게 적었다.)

`npm run typecheck` · `npm run build` · `npm run smoke`. 끝나면 스택을 **찾은 상태로 되돌린다.**

## 5. 남길 것

- `result.md` — **구조화된 verdict 블록을 맨 앞에.** 수정 전/후 `left` 배열 전부(두 런타임 ×
  두 뷰포트), 접근성 트리 확인 결과, 랜딩 보드 탭의 실측(§3), 그리고 `plan.md`에서 벗어난 것.
- `phase.md` — 예산(200줄 / 16 KB) 안에서 **편집**한다. 지금 **16,197 B로 여유가 187 B**이니,
  소비한 `## Notes for later slices` 항목을 덜어내고 `## Now`를 **`P10.REVIEW`를 위한** 핸드오프로
  다시 써서 자리를 만든다. `## Doc impact`에 durable truth 변경을 한 줄씩 덧붙이고
  (`frontend.md`가 최소한 걸린다 — 활성 탭이 폭을 예약한다는 것은 두 표면의 규칙이 되었다),
  랜딩 보드 실측은 `## Operator Questions`의 열린 항목에 반영한다.
  **`doc-new-version`은 실행하지 않는다.**
- 커밋도 상태 전이도 하지 않는다 — 오케스트레이터의 몫이다.

## 6. 이 페이즈의 기록

R17과 R18이 서명한 값 중 **다섯 개가 틀렸고, 전부 재보고서야 드러났다** — 채워진 카운터,
유령 잉크, 8px이 여전히 덮인 84px, 틀린 종횡비, 투명 캔버스를 읽는 잉크 검사. 그중 셋은
**검산 절차 자체가 통과할 수밖에 없는 형태**였다. 당신이 쓰는 검증도 **실패할 수 있는
형태인지** 스스로 물어라: 위 §4의 `left` 배열 비교는 수정 전에 실제로 **다른 값**을 내야
하고(기준선이 그것을 증명한다), 그래야 수정 후의 일치가 의미를 갖는다.
