# R17 — 구현 계약 (P10.S6 → 목업 빌드 + `P10.S7` 적용)

이 문서만으로 만들 수 있어야 한다. **카드를 볼 수 없는 두 소비자**를 위해 쓴다. 발명할 것은 없다.
근거·이유는 `chrome/r17-result.md`. **토큰 변경: 없음.**

---

## 0. 자산

| 파일 | 무엇 | 형식 |
|---|---|---|
| `juju2_2.png` | 운영자 전달 워드마크 **2차** (class B) — 그대로 착지, 참조되지 않음. **이것이 정본** | PNG 1614×1076 sRGBA |
| ~~`juju2.png`~~ | 1차 전달 — 「의」의 카운터가 불투명 흰색(2,864px)이어서 흰 변형에서 ㅇ이 속 찬 덩어리가 된다. **파생 금지** | (착지하되 미참조) |
| `favicon_and_chatbot_widget.png` | 운영자 전달 심볼 (class B) — 그대로 착지, 참조되지 않음 | PNG 278×278 sRGBA |
| `juju2-wordmark-white.png` | 파생 (class C) — 트림 + 알파 보존 흰색 | PNG **1292×371** sRGBA |
| `juju2-symbol-white.png` | 파생 (class C) — **잉크 크롭** + 알파 보존 흰색 | PNG **222×165** sRGBA |

### 파생 명령 (ImageMagick, 기록·재현 대상)

```sh
# 워드마크 — -trim이 정확히 1292x371+238+255를 준다 (juju2_2.png에서 검증됨)
# 검산: 파생물의 불투명 근백색 픽셀은 0이어야 한다. 0이 아니면 1차 파일을 쓴 것이다.
magick juju2_2.png -trim +repage \
       -channel RGB +level-colors white,white +channel \
       -define png:color-type=6 juju2-wordmark-white.png

# 심볼 — -trim은 쓰지 않는다. 좌하단 유령 두 조각을 명시적으로 잘라낸다 (아래 경고)
magick favicon_and_chatbot_widget.png -crop 222x165+39+62 +repage \
       -channel RGB +level-colors white,white +channel \
       -define png:color-type=6 juju2-symbol-white.png
```

> ⚠️ **`-trim`을 심볼에 쓰면 안 된다.** 전달 파일에는 좌하단에 저알파 조각 두 개가 있다 —
> `(52,257) 24×21 평균알파 19` · `(0,265) 24×13 평균알파 35`. 알파 > 0이므로 `-trim`이 살려 두고,
> 흰색 리컬러는 이들을 **불투명도 7~14%의 흰 얼룩**으로 만든다 (모든 파비콘·런처의 좌하단, 코스모스
> 표면에서 보인다). 실제 마크는 **222×165, 잉크 2,481px** — 워드마크 안의 스파클과 픽셀 수까지 같다.
> **이 크롭은 운영자 서명 대상이다** (`r17-result.md` §5). 서명 전에는 파비콘을 태우지 않는다.

> ⚠️ `-channel RGB … +channel` 가드와 `-define png:color-type=6`은 **둘 다 필수**다 — 가드 없는
> `+level-colors`는 알파를 뭉개 흰 사각형을 만들고, 지시 없는 출력은 GrayscaleAlpha로 조용히 저장된다.
> (`assets/README.md`가 이미 적어 둔 함정, 그대로 적용된다.)

### 워드마크 기하 상수 (실측, 소스 픽셀)

```
BOX           1292 × 371            aspect 3.4825 : 1
GLYPH_BAND    1132 × 176  rel y 195..370   (박스 하단 flush)  → 높이의 47.44%
SPARKLE        222 × 165  rel y 0..164     (박스 상단·우측 flush)
GAP           30행       rel y 165..194
BAND_CENTRE   박스 높이의 76.28% 지점
INK_OFFSET    0.2628 × H  (박스 중심 정렬 대비 위로 올릴 양)
```

---

## 1. 워드마크 — 크롬 두 표면

### 렌더 값

| 표면 | 높이 | 폭 | 잉크 오프셋 | 글리프 밴드 |
|---|---|---|---|---|
| nav | **27px** | 94.02px (auto) | **`translateY(-7px)`** | 12.81px |
| footer | **24px** | 83.57px (auto) | **`translateY(-6px)`** | 11.39px |

**R2의 h19/h17을 대체한다.** 뷰포트별 분기 없음 — 390px에서도 h27이다.

### `Wordmark.tsx`

- `height` prop의 타입을 `19 | 17` → **`27 | 24`**로 바꾼다.
- 잉크 오프셋을 컴포넌트가 진다 (호출자가 잊을 수 있는 값이 아니다):
  `style={{ height: \`${height}px\`, width: "auto", transform: height === 27 ? "translateY(-7px)" : "translateY(-6px)" }}`
- `width`/`height` 속성은 **새 고유 크기 `1292` / `371`**로 갱신 (52px 바에서 레이아웃 시프트 0).
- `<img>` 유지 — `next/image` 금지 (재압축이 픽셀 서명 증명을 깬다). 이유는 파일의 기존 주석 그대로.
- `alt`는 `BRAND_ALT_KO` 그대로.
- 파일 주석의 「h19/h17은 서명값이며 여전히 옳은지는 운영자의 열린 질문」 단락은 **삭제**하고 R17이 답한 것으로 대체한다.

### `Nav.module.css`

`.brand`·`.inner`·`gap: var(--space-6)`·52px·하이라인·링크·활성 밑줄 — **전부 그대로.**
바뀌는 것: 없음 (마크 크기는 컴포넌트가 진다).
**`gap: var(--space-6)` 24px을 줄이지 말 것** — 스파클이 글리프보다 11.6px 오른쪽으로 넘치므로 링크 활자 높이에서의 광학 간격은 이미 35.6px이고, 「넓어 보인다」고 줄이면 스파클이 링크를 물기 시작한다.

### `Footer.module.css`

- `.identity { gap: var(--space-3) }` **12px 유지** (스파클 넘침 10.3px → 활자 높이 광학 간격 22.3px).
- **추가 — `.inner`에 `padding-inline-end: 92px`** (런처 프레임 68 + 여백 24). 런처가 렌더되는 데스크톱 쪽에만 필요하고, 렌더되지 않는 ≤767px에서는 0으로 되돌린다:

```css
@media (min-width:768px) and (max-width:1255px){ .inner{ padding-inline-end:84px } }
```

  **84px = 런처 폭 68 (하한) + 여백 16.** 근거는 `app/shell.css`의 `.content{max-width:1120px;margin-inline:auto;padding-inline:24px}`와 `Footer.tsx`가 그 클래스를 쓴다는 사실이다 (`Footer.module.css` 자체에는 `max-width`가 없다). 런처 왼쪽 변 `viewport − 92`, 푸터 내용 오른쪽 변 `(viewport + min(viewport,1120))/2 − 24` →
  **viewport ≤ 1120에서 겹침 68px (일정)** · 1120–1256에서 `628 − viewport/2` · **1256 이상 겹침 없음** (1280은 12px 여유). 세로는 조건 없음 — 액션 행 bottom 24–44.9px가 런처의 24–74px 안에 완전히 든다. 즉 **768–1255의 모든 데스크톱 폭**에서 런처가 「AI 질문」을 덮는다.
  구간을 미디어 쿼리로 좁히는 이유: 플랫하게 걸면 1256 이상에서 액션 행이 페이지 오른쪽 정렬선에서 84px 안으로 들어와 다른 표면과 어긋난다. ≤767px은 런처 미렌더이므로 0.
  구조·내용·순서는 그대로다 — **여백만** 추가한다.
- 나머지 전부 그대로.

### 검증 (렌더에서 재측정할 값)

```
nav h27  → 박스 상단 5.5px · 하단 32.5px · 글리프 밴드 중심 26.10px (바 광학 중심 26px)
footer h24 → 밴드 중심이 행 광학 중심에서 ±0.3px 안, 하이라인에서 마크 상단까지 18px
세로 최소 여백 ≥ 4px (nav 실측 5.5 / 19.5)
```

---

## 2. 심볼 — 1급 마크

### 규칙

- **잉크 박스 222×165** (1.3455:1). `261×216`은 유령을 포함한 수치이므로 어디에도 쓰지 않는다.
- 정사각 박스 안에서 **잉크 폭 = 박스 변의 84%**, **잉크 박스 양축 중앙**. 무게중심 정렬 안 씀.
- **`<img>`가 아니라 mask로 칠한다** — 자산 하나로 모든 색:

```css
.symbol{
  display:inline-block;
  background-color: currentColor;
  -webkit-mask: url("/assets/juju2-symbol-white.png") no-repeat 50% 50%;
          mask: url("/assets/juju2-symbol-white.png") no-repeat 50% 50%;
  -webkit-mask-size: 84% auto;
          mask-size: 84% auto;
}
```

- 색은 두 개뿐: **`#eaf2ed`** (쉼 · 코스모스 `--ink-1`) · **`var(--live)`** (응답). 밝은 표면에서는 `--ink-1`.
- 금지: 회전 · 기울임 · 그림자 · 그라디언트 · 84% 외 스케일 · 별과 점의 분리 사용 · 두 색 밖의 색 · **데이터 표면에서의 사용**.

### 파비콘 / 앱 아이콘

- 정사각 **불투명 타일 `#0a1310`** + 흰 심볼, 84% 규칙. 투명 배경 금지 (밝은 탭에서 사라진다).
- 크기 **16 · 32 · 180**. 16px은 **32px 래스터의 다운스케일**이며 별도 아트워크가 아니다.
- 16px의 작은 점 다섯은 각 1.4px — 한계는 공개되어 있다 (`r17-result.md` §6). 개선안(별 하나만 쓰는 두 번째 크롭)은 **운영자 서명 전까지 구현하지 않는다.**
- `assets/README.md`의 「파비콘 없음 / 이 마크는 파비콘이 되지 않는다」 절은 이 계약으로 대체된다.

---

## 3. 런처 — `Launcher.module.css` 전면 교체

**남는 것:** 68×50 프레임 · 11×11 꼬리 (`right:12 / bottom:-6`, rotate 45°) · 호버 프레임 색 · 1.35 / 1.15 스케일 · 16px × · `z-index:30` · `right/bottom: var(--space-6)`.
**사라지는 것:** `.planet` `.band` `.ring` `.ringBehind` `.ringFront` `@keyframes bandspin` `@keyframes ringdrift` `data-motion="tick"`(2곳) `#dfe9e4` `rgba(95,208,165,.9)` `4.5s` `14s` `clip-path`(2개) `repeating-linear-gradient`. 213줄 → 약 90줄.

```css
.launcher{
  position:fixed; right:var(--space-6); bottom:var(--space-6); z-index:30;
  display:grid; place-items:center;
  width:68px; height:50px; padding:0;
  background:#0e1a15;
  border:1px solid var(--border-strong);
  box-shadow:var(--panel-glow);
  cursor:pointer;
  transition:background var(--dur-base) var(--ease), border-color var(--dur-base) var(--ease);
}
.tail{
  position:absolute; right:12px; bottom:-6px; width:11px; height:11px;
  background:#0e1a15;
  border-right:1px solid var(--border-strong);
  border-bottom:1px solid var(--border-strong);
  transform:rotate(45deg);
  transition:background var(--dur-base) var(--ease), border-color var(--dur-base) var(--ease);
}
/* 마크 = 32×32 심볼 박스, 잉크 26.9×20.0 (84% 규칙 — 파비콘과 같은 숫자) */
.mark{
  width:32px; height:32px;
  color:#eaf2ed;
  background-color:currentColor;
  -webkit-mask:url("/assets/juju2-symbol-white.png") no-repeat 50% 50%;
          mask:url("/assets/juju2-symbol-white.png") no-repeat 50% 50%;
  -webkit-mask-size:84% auto;
          mask-size:84% auto;
  transition:transform var(--dur-base) var(--ease), color var(--dur-base) var(--ease), opacity var(--dur-base) var(--ease);
}
.launcher:hover{ background:#122219; border-color:rgba(95,208,165,.7) }
.launcher:hover .tail{ background:#122219; border-color:rgba(95,208,165,.7) }
.launcher:hover .mark{ transform:scale(1.35); color:var(--live) }
.launcher:active .mark{ transform:scale(1.15); color:var(--live) }
.launcher:focus-visible{ outline:2px solid var(--focus-ring); outline-offset:2px }
.launcher:focus-visible .mark{ color:var(--live) }
/* 열림: 마크 페이드아웃 + × */
.close{
  position:absolute; top:calc(50% - 8px); left:calc(50% - 8px);
  width:16px; height:16px; opacity:0;
  transition:opacity var(--dur-base) var(--ease);
}
.close::before,.close::after{
  content:""; position:absolute; top:calc(50% - .75px); left:0;
  width:16px; height:1.5px; background:#eaf2ed;   /* R6의 #dfe9e4를 대체 */
}
.close::before{ transform:rotate(45deg) }
.close::after{ transform:rotate(-45deg) }
.launcher[data-open="true"] .mark{ opacity:0 }
.launcher[data-open="true"] .close{ opacity:1 }
/* 감축 모드 — transform·transition 정지. 색 변화는 남긴다 (색은 모션이 아니고,
   상시 모션이 사라진 지금 이것이 유일하게 남는 호버 응답이다). */
@media (prefers-reduced-motion: reduce){
  .launcher,.tail,.mark,.close{ transition:none }
  .launcher:hover .mark,.launcher:active .mark{ transform:none }
}
```

### 상태표

| 상태 | 프레임 | 꼬리 | 마크 |
|---|---|---|---|
| rest | `#0e1a15` · 1px `--border-strong` · `--panel-glow` | 프레임과 동일 | 32×32 `#eaf2ed` · **애니메이션 0개** |
| hover | `#122219` · `rgba(95,208,165,.7)` | **프레임과 함께 변한다** | `scale(1.35)` + `--live` |
| active | hover 유지 | hover 유지 | `scale(1.15)` + `--live` |
| focus-visible | `outline:2px var(--focus-ring)`, offset 2px | — | `--live` |
| open | 그대로 | 그대로 | `opacity:0` → × 16px (1.5px 바 ±45°, `#eaf2ed`) |
| reduced-motion | 전환 없음 | 전환 없음 | transform 없음, **색 변화 유지** |

### `AskLauncher.tsx`

- 마크 DOM이 `<span class="planet"><span class="band"/></span>` + 링 두 개에서 **`<span class="mark"/>` 하나**로 줄어든다.
- `data-motion="tick"` 속성 두 개 제거.
- `aria-label`·`aria-expanded`·열림 시 inert 처리 — R6/R14 그대로.
- 존재 경계 (R14, 구조): 데스크톱 전용, ≤767px 렌더 없음 · `/ask` 없음 · ops 크롬 없음.

---

## 4. 대체 관계 (무엇이 무엇을 이기는가)

| 이전 서명 | R17 |
|---|---|
| R2 §Page shell — 워드마크 h19 / h17, 박스 중심 | **h27 / h24, 잉크 정렬 −7px / −6px** |
| R6 §런처 마크 — 22×22 토성 + 4.5s + 14s + 두 반쪽 링 | **32×32 스파클, 모션 0** |
| R6 운영자 노트 — 상시 모션 예외 | **만료** |
| R6 — × `#dfe9e4` | **`#eaf2ed`** |
| `assets/README.md` — 파비콘 없음 / 심볼 마크 없음 | **스파클 = 심볼 마크, 파비콘 16/32/180** |

**건드리지 않는 것:** R8 크롬 구조 전부 · R14 런처 경계 · 모든 카피 (**신규 문자열 0건**) · `foundations/tokens.css` (**Token delta: None**) · a11y 하한 (감축 모드 · 히트 32/44 · `BRAND_ALT_KO`).

## 5. 서명 완료 — 열린 항목 없음 (운영자 승인 2026-08-31)

| 항목 | 결정 | 구현 |
|---|---|---|
| 심볼 크롭 | **`-crop 222x165+39+62` 채택** | §0의 명령 그대로. README에 명령 + 픽셀 서명 기록 |
| 16px 파비콘 | **전체 클러스터의 다운스케일.** 별 단독 크롭 **미채택** | 아트워크 하나, 규칙 하나. 16px의 부드러움은 기록된 한계 |
| 런처 × 색 | **`#eaf2ed`로 통일** | §3의 `.close::before/after` |
| 데스크톱 푸터 「AI 질문」 | **숨긴다** | §1 추가② `.actionAsk` |
| 푸터 코너 예약 | **넣는다** — ②의 대비책이 아니라 **별개 필수 항목** | §1 추가① `padding-inline-end` |
| 워드마크 소스 | **`juju2_2.png`** (1차 `juju2.png` 파생 금지) | §0. 검산: 파생물의 불투명 근백색 픽셀 = 0 |

**`P10.S7`은 이 문서만으로 진행할 수 있다 — 대기 중인 결정 없음.**
