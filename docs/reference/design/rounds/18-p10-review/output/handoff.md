# P10.review — 로고 · 내비 · 파비콘 세 건의 수정 (핸드오프)

설계: Mijual Design System (디자인 프로젝트) · 2026-08-31
대상 리포: `leetusik/Mijual` · `main` · 적용 단위 하나 (`P10.review`)
카드: `p10-review/Review.html` (그룹 `P10.review`) — 세 건 모두 수정 전/후를 나란히 렌더한다
자산: `p10-review/assets/juju2-wordmark-white-unspaced.png` (1247×371, 픽셀 비교용) · `adopted-icon-{32,16}.png` · `adopted-apple-180.png` · `fallback-opaque-{32,180}.png`

운영자 지시 세 건이고, 세 건 다 **왜 그 숫자인지**까지 이 문서에 실측으로 들어 있다. 대기 중인 결정 없음 — 이 문서만으로 진행한다.

| | 지시 | 처방 | 성격 |
|---|---|---|---|
| ① | 워드마크 「의 관」의 공백을 없앤다 | class C 파생 명령에 **크롭 2조각 + `+append`** 한 단계 추가 → **1247×371** | 자산 재생성 + 상수 1개 |
| ② | 내비 링크가 활성화되며 굵어질 때 형제가 밀린다 | 링크가 **항상 600의 폭**을 점유 (숨은 쌍둥이) | CSS 3규칙 + TSX 1줄 |
| ③ | 파비콘을 더 중앙으로, 흰 브라우저와 어울리게 (배경 없이 가능한가) | **가능하다** — 투명 타일 + 잉크 색 `#2b8e6c` + 잉크 폭 84%→**75%** | 타일 3개 재생성 + 주석 |

**토큰 변경 없음.** 신규 카피 없음. `public/foundations/tokens.css`는 손대지 않는다 (여전히 동결된 R8 자산). ③의 색은 CSS가 읽지 않는 **이미지 합성용 리터럴**이다.

---

## ① 워드마크 — 「의」와 「관」 사이 45열 삭제

### 왜 45인가 (실측, `juju2-wordmark-white.png` 1292×371)

글자띠(`y≥190`)의 열 알파 프로파일에서 잉크 덩어리는 여섯 음절 + 분리된 두 획으로 잡힌다:

| 음절 | 잉크 구간 | 음절 간 잉크 간격 |
|---|---|---|
| 주 | `0..163` | — |
| 주 | `183..346` | 19px |
| 의 | `370..518` (`486..493`은 ㅢ 세로획 분리) | 23px |
| 관 | `589..756` | **70px** ← |
| 제 | `776..931` (`895..907` 분리) | 19px |
| 탑 | `971..1131` | 39px |

간격만으로는 글리프 모양 차이와 구분되지 않으므로 **전진폭**으로 확인했다. 동일 글리프인 주→주의 잉크 중심 간격이 **183.0px** — 이 마크의 한글 전진폭이다. 그런데 의→관은 **228.5px**, 초과분 **45.5px = 0.249em**. 즉 4분의 1 각공백 한 칸이 들어가 있다. 관·제·탑의 좌/우 잉크 경계를 183 격자에 맞춰 보면 초과분은 세 글자 모두에 **+40~+56px**(평균 45)로 동일하게 실려 있다 — 커닝 하나가 아니라 **한 칸이 밀린 것**이다.

**`x=519..588`(70열)은 이미지 전체 높이에서 알파가 0이다.** 스파클 무리는 `x≥1070`에만 있으므로 이 구간을 전 높이로 잘라내도 별에 닿지 않고, 잘라낸 만큼 우측 전체(관제탑 + 스파클)가 왼쪽으로 옮겨져 **상단·우측 flush가 그대로 유지된다.**

45열 채택. −40은 간격 30px으로 여전히 벌어져 보이고, −52는 18px으로 주|주의 19px보다 좁아져 「의관」이 붙는다 (카드 §① 3열 비교).

### 명령 — 같은 파일명, 한 단계 추가

`public/assets/`에서 실행. R17 §0의 워드마크 명령에 크롭/append만 붙는다. **파일명은 바꾸지 않는다** — 소비자 경로(`copy.ts` → `<img>`)가 하나뿐이고, 이건 같은 class-B 조상에서 나온 새 class C 파생이다.

```sh
magick juju2-logo-source.png -trim +repage \
       -channel RGB +level-colors white,white +channel \
       \( -clone 0 -crop 530x371+0+0 +repage \) \
       \( -clone 0 -crop 717x371+575+0 +repage \) \
       -delete 0 +append +repage \
       -define png:color-type=6 juju2-wordmark-white.png
```

`530 + 717 = 1247` · `575 = 530 + 45`. `-trim`이 주는 1292×371은 R17이 이미 검증한 값이므로 그 뒤에 붙인다. `-channel RGB … +channel` 가드와 `png:color-type=6`은 R17의 함정 3·4 그대로 — **지우면 알파가 평탄화되어 흰 사각형이 된다.**

### 검증 (재파생 후 반드시 실행)

```sh
identify -format '%wx%h %[channels] %[bit-depth]\n' juju2-wordmark-white.png   # 1247x371 srgba 8
```

| 확인 | 기대값 | 왜 |
|---|---|---|
| 박스 | **1247×371** (3.3603:1) | 세로는 건드리지 않았다 |
| 비투명 픽셀 | **78,212** | 원본과 동일 — 잘라낸 45열은 전부 완전 투명 |
| 완전 불투명 | **69,630** | 동일 |
| 서로 다른 알파값 | **154** | 동일 |
| 불투명 근백색(「의」 카운터) | **0** | R17 함정 2의 검산, 그대로 유효 |
| 의\|관 잉크 간격 | **25px** (`x=519..543`) | 70 − 45 |
| 스파클 | **222×165 at `x=1025, y=0`** | `1025+222 = 1247` — 상단·우측 flush 유지 |
| 글자띠 | **1087×176 at `y=195`**, 잉크 75,731px | 하단 flush 유지 (1132 − 45) |
| 빈 밴드 | `y=165..194` **30행** | 무변 |
| 갇힌 카운터 두 섬 | `50×46 at (402,226)` · `69×15 at (**969**,335)` | 두 번째만 −45 이동 |

**알파 해시 문장은 갱신해야 한다.** README의 "파생물의 알파 채널이 소스 트림과 바이트 동일"은 이제 성립하지 않는다(45열이 빠졌다). 대체 검산 — 소스 트림에서 같은 두 조각을 이어붙인 것과 비교한다:

```sh
magick juju2-logo-source.png -trim +repage \
  \( -clone 0 -crop 530x371+0+0 +repage \) \( -clone 0 -crop 717x371+575+0 +repage \) \
  -delete 0 +append +repage -alpha extract -depth 8 gray:- | shasum -a 256
magick juju2-wordmark-white.png -alpha extract -depth 8 gray:- | shasum -a 256   # 같아야 한다
```

새 `sha256`과 `identify -format '%#'` 픽셀 서명은 재파생한 값을 README에 적는다 (예전 값은 **재파생으로 복원되지 않는다** — 컨테이너가 달라진다).

### 코드 변경 — 두 줄

`components/chrome/copy.ts`
```diff
-export const WORDMARK_NATURAL = { width: 1292, height: 371 } as const;
+export const WORDMARK_NATURAL = { width: 1247, height: 371 } as const;
```
주석에 한 문장 추가: **1292는 4분의 1 각공백이 들어간 수정 전 값**이고, 파생 명령이 그 45열을 잘라낸다.

`components/chrome/Wordmark.tsx` — **`INK_OFFSET_PX`는 바꾸지 않는다.** 세로 기하가 하나도 변하지 않았으므로 `BAND_CENTRE 76.28%` / `0.2628 × H` / `translateY(-7px)` · `-6px`가 그대로 맞다. 문서 주석의 「1292×371」 두 곳만 1247로, 종횡비 3.4825 → **3.3603**으로 고친다. 렌더 폭만 따라 줄어든다: nav h27 **94.0 → 90.7px**, footer h24 **83.6 → 80.6px** (레이아웃 영향 없음 — `.brand`는 `flex:none`이고 폭 고정값이 없다).

`app/layout.tsx`·`Launcher.module.css`는 워드마크를 참조하지 않는다 (심볼만) → 무변.

---

## ② 내비 — 활성 링크가 형제를 밀지 않게

### 원인

`Nav.module.css`의 `.active { font-weight: 600 }`. **밑줄은 이미 흔들리지 않는다** — 비활성 링크가 `border-bottom: 2px solid transparent`로 같은 2px를 예약해 두었고, 그 주석은 정확하다. 남은 건 굵기고, 굵기는 **글자 폭**을 바꾼다: 「AI 질문」의 라틴 두 글자와 공백, 「보유 종목」의 공백이 특히. 그래서 `/ask` ↔ `/portfolio`를 오갈 때 두 번째 링크의 시작점이 움직인다.

### 처방 — 링크가 항상 600의 폭을 점유한다

`components/chrome/Nav.module.css`
```diff
 .link {
-  display: inline-flex;
-  align-items: center;
+  /* 폭 예약: 라벨과 숨은 600 쌍둥이를 같은 그리드 칸에 겹쳐 둔다. 칸의 폭은
+     둘 중 넓은 쪽(=600)이므로 활성 여부가 폭을 바꾸지 못한다. 밑줄 2px을
+     transparent로 예약해 둔 것과 같은 방식의 세로판 대응. */
+  display: inline-grid;
+  grid-template-areas: "label";
+  place-items: center;
+  white-space: nowrap;
   font-size: var(--text-base); /* R2: 13.5px */
   color: var(--ink-1);
   text-decoration: none;
   border-bottom: 2px solid transparent;
   transition: color var(--dur-fast) var(--ease);
 }
+
+.link > span {
+  grid-area: label;
+}
+
+/* 쌍둥이. `visibility: hidden`이지 `opacity: 0`이 아니다 — 전자는 보조기술이
+   무시하고 히트 테스트에서도 빠진다. 높이 0이라 칸 높이에는 기여하지 않는다. */
+.link::after {
+  content: attr(data-label);
+  grid-area: label;
+  font-weight: 600;
+  height: 0;
+  overflow: hidden;
+  visibility: hidden;
+  pointer-events: none;
+}
```

`components/chrome/Nav.tsx` — 바 링크만 (시트는 아래 참조)
```diff
               <Link
                 key={link.href}
                 href={link.href}
                 className={active ? `${styles.link} ${styles.active}` : styles.link}
                 aria-current={active ? "page" : undefined}
+                data-label={link.label}
               >
-                {link.label}
+                <span>{link.label}</span>
               </Link>
```

**모바일 시트는 손대지 않는다** (`.sheetRow` / `.sheetActive`). 행이 전폭 세로 목록이라 굵기가 형제를 밀 곳이 없다 — 같은 처방을 넣으면 이유 없는 마크업만 늘어난다.

### 기각한 대안

- **활성도 400으로 두고 색·밑줄만** — R2가 서명한 「active = 600 + 2px #fff underline」을 폐기하는 일이고, 지시는 흔들림을 없애라는 것이었다.
- **링크별 `min-width` 하드코딩** — 서체 로드 전/후, 브라우저별 실측에 의존한다. 폰트가 `next/font/local` 서브셋으로 바뀐 리포에서는 특히 취약하다.
- **`letter-spacing` 음수 보정** — 폭은 맞춰도 자간이 달라져 결함을 다른 결함으로 옮긴다.

### 검증

```js
// 각 목적지에서 두 링크의 left를 재고, 활성 여부와 무관하게 같아야 한다.
[...document.querySelectorAll('header nav a')].map(a => a.getBoundingClientRect().left)
```
`/ask`에서 잰 배열과 `/portfolio`에서 잰 배열이 **소수점까지 동일**해야 한다 (수정 전에는 두 번째 값이 움직인다). 함께 확인: 활성 링크의 굵기가 여전히 600이고 밑줄이 흰색 2px · 링크 히트 영역이 바 높이 전체 · 스크린리더가 라벨을 **한 번만** 읽는다.

### ②b (선택 — 같은 결함, 같은 처방)

`components/ops/Ops.module.css`의 `.tabActive { font-weight: 600 }`도 **수평 6탭 줄**에 걸린 같은 결함이다(`.tab`은 `border-bottom: 2px transparent`로 밑줄만 예약해 두었다). 운영 화면이라 지시에 없었으니 **적용 여부는 운영자 판단**으로 남긴다. 적용한다면 `.tab`에 위와 같은 3규칙 + `Ops` 탭 렌더에 `data-label`/`<span>`을 넣으면 끝난다. 적용하지 않는다면 이 문단이 그 기록이다.

---

## ③ 파비콘 — 배경 없음, 잉크 색 하나, 잉크 폭 75%

### 「배경 없는 파비콘이 가능한가」 — 가능하다

투명 PNG 파비콘은 모든 현대 브라우저가 그린다. 지금까지 불투명 `#0a1310` 타일이었던 이유는 README에 적힌 한 문장 하나뿐이다 — 「투명 파비콘은 밝은 탭에서 사라진다」. 그건 **배경**의 문제가 아니라 **흰 잉크**의 문제다. 색으로 푼다.

### 색 — `#2b8e6c` = `oklch(0.58 0.105 166)`

| 색 | 흰 탭 | Chrome 밝은 탭 `#f1f3f4` | 어두운 탭 `#202124` | cosmos `#0a1310` | 순검정 |
|---|---|---|---|---|---|
| `#5fd0a5` (cosmos `--live`) | 1.90 | 1.71 | 8.47 | 9.93 | 11.1 |
| `#0d5c48` (light `--live`) | 7.95 | 7.14 | 2.03 | 2.37 | 2.65 |
| **`#2b8e6c` 채택** | **4.05** | **3.64** | **3.98** | **4.66** | **5.19** |

디자인 시스템의 두 `--live` 사이, **같은 초록 축**이다: 채도 `0.105`는 cosmos `--live`의 `0.107`과 사실상 같고 명도만 두 값의 중간에 놓았다. 결과가 이 결정의 전부다 — 흰 탭 4.05, 어두운 탭 3.98. **어느 쪽으로도 기울지 않는다.** (`#009268` = 같은 명도·채도 0.13도 재봤다: 흰 탭 3.95로 조금 낮고 브랜드 축에서 벗어난다 → 기각.)

**토큰이 되지 않는다.** CSS가 읽는 값이 아니라 세 타일을 합성할 때 쓰는 리터럴이고, 소비자는 ImageMagick 명령 하나뿐이다. `tokens.css`는 동결 상태를 유지한다.

### 여백 — 잉크 폭 84% → 75%, 정수 중앙

운영자가 본 「왼쪽 성진이 테두리에 너무 붙었다」의 정체: 잉크 박스 222×165는 **4:3**이고 타일은 정사각이다. 종횡비를 지켜 넣으면 세로 여백이 언제나 가로보다 크고, 84%에서 32px 타일의 **좌우 여백은 2.5px**(실제 착지값 `+2`)뿐이었다 — 그런데 좌측 성진은 잉크 박스의 `x=0`에 **flush**로 붙어 있다(23×23 조각). 즉 성진과 타일 경계 사이에 2px밖에 없었다.

좌우 여백이 결정 변수다. **75%** — 그리고 반올림 편향이 없는 정수 기하로 못 박는다:

| 타일 | 잉크 | 위치 | 여백 |
|---|---|---|---|
| `app/icon.png` 32 | **24×18** | `+4+7` | 좌우 **4/4** · 상하 7/7 |
| `app/apple-icon.png` 180 | **134×100** | `+23+40` | 좌우 **23/23** · 상하 40/40 |
| `app/icon1.png` 16 | 32 래스터의 Box 다운스케일 | — | (12×9 at +2+3.5) |

좌측 성진의 숨 쉴 틈이 32px에서 **2px → 4px**로, 180px에서 **14px → 23px**로 늘어난다. 84%를 그대로 두고 여백만 손볼 방법은 없다(둘은 같은 숫자다). 78%도 재봤다: 여백 3.5px — 지금과 구분되지 않아 기각.

**런처의 `mask-size: 84% auto`는 유지한다.** 런처는 우리가 그리는 68×50 어두운 프레임 안에 있고, 남의 탭 텍스트와 이웃하지 않는다. R17의 「아트워크 하나, 규칙 하나」는 **크롭**에 대한 서명이고, 그 아트워크는 그대로다 — 표면이 다르면 배치 규칙은 갈릴 수 있고, 여기서 갈렸다. 이 문장이 그 기록이다.

### 명령 — `frontend/`에서 실행

```sh
# 투명 타일. 잉크 = 심볼을 #2b8e6c로 재색칠 후 폭 지정, 양축 정확 중앙.
magick -size 32x32 xc:none \
       \( public/assets/juju2-symbol-white.png \
          -channel RGB +level-colors '#2b8e6c','#2b8e6c' +channel \
          -resize 24x \) \
       -gravity center -composite -depth 8 -define png:color-type=6 app/icon.png

magick -size 180x180 xc:none \
       \( public/assets/juju2-symbol-white.png \
          -channel RGB +level-colors '#2b8e6c','#2b8e6c' +channel \
          -resize 134x \) \
       -gravity center -composite -depth 8 -define png:color-type=6 app/apple-icon.png

# 16은 32 래스터의 다운스케일 (R17 §5: 아트워크 하나, 규칙 하나). 2:1에서
# -filter Box는 2×2 평균 그 자체다 — Lanczos는 링잉으로 타일에 없던 색을 만든다.
magick app/icon.png -filter Box -resize 16x16 -depth 8 -define png:color-type=6 app/icon1.png
```

**세 개의 함정, 전부 조용하다.**

1. **`-alpha off`를 지워야 한다.** 배경을 만드는 건 `xc:'#0a1310'`이 아니라 그 플래그다 — 남겨두면 투명 영역이 검정으로 평탄화되고, 파일은 정상 크기로 나온다.
2. **`png:color-type=2` → `6`.** 2는 알파 없는 RGB다. 투명을 요구하면서 2를 남기면 IM은 조용히 배경을 합성한다.
3. **재색칠을 리사이즈보다 먼저** 한다. 그러면 투명 픽셀까지 전부 정확히 `#2b8e6c`가 되어(단색 1개), 하드 다운스케일에서 프리멀티플라이하지 않는 렌더러가 테두리에 다른 색을 흘릴 여지가 없다 — R17이 흰 파생물에서 기록한 그 이유의 초록 버전이다.

검증:
```sh
identify -format '%f %wx%h %[channels] %[opaque]\n' app/icon.png app/icon1.png app/apple-icon.png
# 32x32 / 16x16 / 180x180, srgba, opaque=false
magick app/icon.png -trim +repage -format '%wx%h%O' info:      # 24x18+4+7
magick app/apple-icon.png -trim +repage -format '%wx%h%O' info: # 134x100+23+40
magick app/icon.png -depth 8 -format '%[fx:int(255*u.r)],%[fx:int(255*u.g)],%[fx:int(255*u.b)]' info: # 43,142,108
```

### iOS/Safari — 예외 타일을 만들지 않는 이유

`apple-touch-icon`을 투명으로 두면 iOS가 홈 화면에서 검정(또는 흰 배경 컨텍스트)에 합성한다. `#2b8e6c`는 **순검정 5.19 · 순백 4.05** — 양쪽 다 읽힌다. 그래서 「탭 타일은 투명, 애플 타일만 불투명」 같은 갈래를 만들지 않는다. 세 타일, 한 규칙, 한 색.

배경을 남기라는 판단이 나올 경우의 대안은 카드에 렌더해 두었다 (`fallback-opaque-*`): `#0a1310` · 흰 잉크 · **같은 75% 여백**. 그 경우에도 여백 수정은 유효하다.

### 코드 변경

`app/layout.tsx` — **`icons` 키는 계속 넣지 않는다.** Next `app/` 파일 컨벤션이 그대로 유효하다. 다만 주석의 사실 두 개가 틀리게 되므로 갱신 대상이다: 「an opaque `#0a1310` square」 → 투명 타일 + `#2b8e6c` 잉크, 「the 84% ink-width rule」 → 파비콘은 75%(런처는 84% 유지). `P10.review`가 그렇게 정했다는 한 줄과 함께.

회귀 검사는 기존과 동일: dev·prod 양쪽에서 `link[rel="icon"][sizes="32x32"]` · `sizes="16x16"` · `link[rel="apple-touch-icon"][sizes="180x180"]`이 DOM에 있는지.

---

## ④ 문서 갱신 — 코드와 같은 변경에 포함한다

`public/assets/README.md`

1. **class C 표** — 워드마크 `PNG 1292×371` → **1247×371**, 바이트수 재실측.
2. **파생 명령 절** — 워드마크 명령을 위 4줄로 교체하고, 45열의 근거(전진폭 183 · 초과 45.5 = 0.249em · `x=519..588` 전 높이 알파 0)를 한 단락으로 남긴다.
3. **함정 절** — 함정 1~4는 유효하다. 함정 2(「의」 카운터)의 검산은 그대로 쓰고, 갇힌 두 섬의 좌표 중 두 번째를 `(1014,335)` → **`(969,335)`**로 고친다.
4. **「재색칠이 색만 바꿨다」 절** — 「알파 채널이 소스 트림과 바이트 동일」 문장을 §① 검증의 **두 조각 이어붙이기 해시** 비교로 교체한다. 잉크 픽셀 수(78,212 / 69,630 / 154)는 **변하지 않으므로** 그대로 두고, 「45열을 잘라도 잉크가 한 픽셀도 변하지 않는다」가 이 절의 새 주장이다.
5. **실측 기하 표** — 트림 박스 1247×371 · 종횡비 **3.3603:1** · 글자띠 **1087×176** at `y=195`(잉크 75,731px, 밴드 내 잉크 밀도 38.0% → **39.6%**) · 스파클 222×165 at `x=1025, y=0` · 빈 밴드 30행. `BAND_CENTRE 76.28%` / `INK_OFFSET 0.2628 × H` / `translateY(-7/-6px)`는 **무변**임을 명시. nav 렌더 폭 94.0 → 90.7px, footer 83.6 → 80.6px.
6. **파비콘 절** — 명령·표를 위 §③으로 교체. 「**The tile is opaque on purpose**」 단락을 **「투명 타일 + 한 색」** 단락으로 대체하되, *왜 예전 판단이 옳았는지*(흰 잉크는 밝은 탭에서 사라진다)와 *무엇이 그 전제를 무너뜨렸는지*(색을 흰색에 고정하지 않으면 배경이 필요 없다)를 함께 적는다. 84% 규칙은 **런처의 규칙으로 남는다**는 한 줄을 같은 자리에 둔다. 16px에서 점 다섯 개가 1.4px로 흐린 먼지처럼 읽힌다는 **기록된 한계는 유지**된다 (75%에서는 약 1.2px — 조금 더 흐리다. 이것도 적는다).
7. **체크섬 절** — 워드마크와 세 타일의 새 `sha256` + `identify -format '%#'` 픽셀 서명을 재실측해 교체. 심볼(`juju2-symbol-white.png`)과 두 class-B 원본은 **무변**이므로 기존 해시를 그대로 둔다.

`frontend/README.md` — 파비콘 한 줄 설명(`icon.png icon1.png apple-icon.png … (R17 §2)`)에 `P10.review` 갱신을 덧붙인다.

`docs/reference/design/rounds/**`는 **편집하지 않는다** — 기록이다. 이 문서가 R17의 세 값(워드마크 1292×371 · 파비콘 불투명 타일 · 파비콘 84%)을 **부분 승계(supersede)**한다는 사실만 적용 커밋 메시지와 `works/` 기록에 남긴다. 디자인 프로젝트 쪽 R17 카드(`chrome/NavMark.html` · `FooterMark.html` · `MarkScale.html` · `ask/Launcher.html` · `components/BrandSymbol.html`)의 1292·84% 수치도 같은 이유로 수정 전 기록이고, `p10-review/Review.html`이 그 위에 놓인다.

---

## ⑤ 작업 순서

1. `public/assets/`에서 워드마크 재파생 → §① 검증 표 전체 통과 (특히 `1247x371` · 비투명 78,212 · 근백색 0).
2. `copy.ts`의 `WORDMARK_NATURAL` → 1247. `Wordmark.tsx` 주석 수치 갱신 (오프셋 상수는 손대지 않는다).
3. nav 폭 예약 적용 (`Nav.module.css` 3규칙 + `Nav.tsx` 한 줄). `/ask`·`/portfolio`에서 left 배열 비교.
4. `frontend/`에서 타일 3개 재생성 → `identify` 3줄 통과.
5. README 7개 절 + `layout.tsx` 주석 + `frontend/README.md` 갱신. 새 해시/서명은 **재실측값**으로.
6. 회귀: 랜딩·`/ask`·`/portfolio`·`/stocks`·`/auth`·`/ops`에서 nav 마크와 링크 정렬, 푸터 마크, 탭 파비콘(밝은 탭·어두운 탭 양쪽), 390px 폭에서 브랜드 + 메뉴 버튼.

## ⑥ 완료 확인 체크리스트

- [ ] 워드마크가 **1247×371**이고, 「의관」이 붙어 읽힌다 (nav h27에서 간격 1.8px 상당).
- [ ] 잉크 통계 3개(78,212 / 69,630 / 154)가 수정 전과 **동일**하다.
- [ ] `translateY(-7px)` / `-6px`가 **그대로**이고, 52px 바에서 글자띠 중심이 26px 선을 물고 있다.
- [ ] `/ask` ↔ `/portfolio` 이동 시 두 링크의 `left`가 소수점까지 동일하다.
- [ ] 활성 링크는 여전히 600 + 흰 2px 밑줄이고, 스크린리더가 라벨을 한 번만 읽는다.
- [ ] 세 타일 모두 `opaque=false`, 잉크 트림이 `24x18+4+7` / `134x100+23+40`, 잉크 RGB가 `43,142,108`.
- [ ] 흰 탭과 어두운 탭 **양쪽**에서 파비콘이 보이고, 좌측 성진이 타일 경계에 붙어 있지 않다.
- [ ] `link[rel=icon]` 32/16 + `apple-touch-icon` 180이 dev·prod DOM에 있다.
- [ ] `tokens.css` diff **없음**. 신규/삭제 카피 **없음**.

## ⑦ 이탈 (이번 적용 범위 밖)

1. `components/ops/Ops.module.css` `.tabActive`의 같은 밀림 결함 — §②b, 운영자 판단 대기.
2. 디자인 프로젝트 R17 카드 5개의 1292×84% 수치 재컷 — 다음 크롬 라운드.
3. 16px에서 점 다섯 개의 가독성(1.4 → 1.2px) — 단일 별 크롭은 R17이 기각한 상태를 유지한다. 다시 열려면 운영자 지시가 필요하다.
4. `Launcher.module.css`의 `mask-size: 84%`는 유지 — 파비콘과 숫자가 갈렸다는 사실만 기록됨.
