# Result — P5.S19: Design-fidelity verification in a real browser

The whole product was run (`npm run build` + `npm run start` on `http://localhost:3000`,
uvicorn on `:8000` against the live corpus) and checked **surface by surface against its
signed contract** in headless Chrome over CDP, at 1440 / 768 / 390 and at the intermediate
widths the phase flagged. **~230 scripted checks across 11 stages**, 41 screenshots kept as
evidence in the run's scratch dir.

**Five faithful-implementation fixes landed** (one of them a systemic CSS-cascade defect that
had flattened the type scale on every reader surface), **no landed record was touched**, and
**19 items are catalogued for the operator** — none of them fixable without a new visual
decision.

---

## 1. Fixes landed here (code only — never a record edit)

| # | Defect (measured) | Fix | Re-measured |
|---|---|---|---|
| F1 | **The global `.mono` rule silently overrode every surface's own font-size.** `app/shell.css`'s `.mono {font-size: 0.95em}` and a CSS-module class are both specificity (0,1,0), so source order decided — and the global won **everywhere**: R4's 놓친 돈 **총액 headline rendered at 12.8px instead of 32px**, 보유량 input 12.8 not 20, 조회/포트폴리오 per-holding 금액 12.8 not 20, R3's 청약 결과 inset 12.8 not 20, R3 crumb 12.8 not 12, R2's tab counts 12.8 not 11 — 23 classes in all, one flat size | split the rule: `.mono` keeps family + tabular-nums at normal specificity; **`:where(.mono) {font-size: .95em}`** makes R1's 0.95em a zero-specificity *default* that a surface's stated size beats (`frontend/app/shell.css`) | every declared size now applies (총액 **32px**, 금액 20px, inset 20px, crumb 12px, meta 11px, tab counts **11px**), plain `.mono` numerals still 0.95em; screenshots before/after |
| F2 | **Footer 「추정」 tag at 6.72px** (the S11 note 9 item): 0.56em of a 12px sentence, against R2's own *"bordered sans **10px** 「추정」 tag"* | a **named prop** on the primitive with its citation — `EstimateMarker size="landing"` → 10px (`EstimateMarker.tsx/.module.css`), used by the footer's gate-cost sentence (`chrome/Footer.tsx`). No local restyle, no resize of the signed sentence, no token touched | footer tag **10px**; landing tags unchanged at 9.52px (the surface still supplies R2's ~17.9px context) |
| F3 | **R3 §2's "mono window/state line" rendered half sans** — the window dates were mono through their own span, the state phrase (`거래 가능 · 마감 D-3`, `진행 중`) inherited sans, so a **D-day numeral rendered outside R1's mono rule**. 조회 already renders the same line fully mono | `font-family: var(--font-mono)` on `.windowLine` (`components/event/Event.module.css`) | line renders `IBM Plex Mono 12px`, phrase still `--live` |
| F4 | **41px of horizontal document overflow on the landing at 768px** (and through ~830px): the desktop board grid `86px 1fr 300px 230px 96px` + 4×12px gaps = 760px against a 720px padded content column | the two wide columns become `minmax(0, 300px)` / `minmax(0, 230px)` — R2's widths wherever they fit, shrink instead of scrolling below that (`components/landing/Board.module.css`) | 0 overflow at 481/600/768/900/1024/1119/1440 and 390; rows wrap, **no value truncated** |
| F5 | (subsumed by F1) R2's *"counts mono 11"* on the board tabs | — | 11px IBM Plex Mono |

Nothing else was changed. **Tokens, `fonts.css`, the vendored assets and every landed record
file are byte-identical**; no dependency added; the primitives were extended only through the
sanctioned route (a named prop + citation, `components/index.ts`'s own rule).

### Why F1 is a fidelity fix and not a restyle

Every one of the 23 overridden declarations is a size the *surface* wrote with a record
citation (`.totalAmount: var(--text-3xl)` under R4's headline, `.crumb: var(--text-sm)` under
R3 §1's "mono text-sm", `.tabCount: var(--text-xs)` under R2's "counts mono 11"). The fix does
not choose a new value anywhere — it lets the already-approved values take effect. R1's rule
that mono runs "~0.95em of the surrounding sans" is preserved as the default it is; where the
record states a size, the stated size governs. `states-and-trust.md` §1's own words for the
same class of failure: *"a `▷ 718.1억원` shrunk into a caption while the number grows to 72pt
has broken the rule"* — here R4's total **was** the caption-sized one.

---

## 2. Surface-by-surface verification

Legend: **pass** = matches the signed contract as measured; *artifact* = the check script's
flattened-text heuristic, re-measured precisely and passing.

### R1 foundations, swept across 12 reader pages

| Check | Result |
|---|---|
| Off-token colour anywhere | **pass** — 35 distinct rendered colours, **every one** a `.cosmos` token or an R2 literal (`rgba(255,255,255,.12/.14/.3/.45/.68/.72/.78)`, `rgba(8,17,13,.72)`, `rgba(95,208,165,.45)`, `rgba(163,196,180,.4)`). The only stray is the UA default link colour on the nav brand `<a>`, which renders no ink (it wraps only the wordmark `<img>`) |
| Radius 0 everywhere | **pass** — the only non-zero radii are the hero's two orbit **ellipses** and the orbiting star (R2 draws them as ellipses) |
| No shadows | **pass** — one box-shadow value exists, `inset 0 1px 0 rgba(186,232,209,.14)` = `--panel-glow`, only on craft panels |
| Mono for every numeral | **pass** after F3 — the remaining sans digits are all inside Korean prose (verbatim 인용문, 산식, 정정 요약, signed sentences) |
| Korean prose never mono | **pass** — `CSS.getPlatformFontsForNode`: prose draws in **Pretendard Variable** (hero sub ×30 glyphs, board corp links, fact sentence ×45). Every Korean-in-mono instance is an element the record *draws* in mono (R1 StateBadge chip · 소멸주의보 tag · `[근거]` chip; R2 positioning line, stat/band lines, tab strip, 메뉴/[의견]; R3 crumb, meta, eyebrows, provenance; R4 eyebrows, provenance) |
| Motion durations/eases | **pass** — transitions only 0.12s / 0.2s / 0.32s with `cubic-bezier(.2,0,.2,1)`; animations only `twinkle 2.5–6.5s`, `drift 80s`, `shoot 10.5–17.7s`, `orbit 26s`, `blink 1s steps(1)` |
| Reduced motion | **pass** — countdown identical after 3.2s (the interval never runs), twinkle/drift/orbit/colon `animation: none`, shooting-star layer `display: none` |

### R2 / R2.1 — landing + chrome (S11/S12)

| Check | Measured |
|---|---|
| Cosmos layers | 240 stars desktop / **160 mobile**, 5 shooting stars desktop / **3 mobile**, one glow layer with **both** radial gradients (strong `50% 12%`, faint echo `50% 100%`), one continuous fixed backdrop (`z-index:-1`) |
| Orbit rings | bounding boxes **1019×509** and **1251×640** = exactly 980×280 and 1200×360 rotated −14°; tops 138/72 vs nav bottom **52**, bottoms 646/712 vs first panel **732** — clear at 768 / 1120 / 1440 |
| Hero | H1 52px/700/−0.02em (mobile **34px**), sub 17px `rgba(255,255,255,.78)`, search row **560px** with 52px controls (mobile 48px), console input `rgba(8,17,13,.72)` + `rgba(163,196,180,.4)`, 조회 on `--live-solid`, **mono stat line**, `min-height: 680px` floor holds at every width |
| Anchor cards | grid **712px / 340px, gap 20px**; eyebrow mono 11; value **46px/700** (its `.mono` numeral 43.7 = R1's 0.95em) + 「추정」; band line mono 13.5; fact sentence 15px, full card width, one line |
| Countdown | mono **28px/600 `--alert`**, colons `blink 1s steps(1) infinite`, **0 s** difference against the served `next_lapse.target` (2026-09-05T00:00+09:00, 퓨쳐켐) |
| 소멸주의보 | 1px `--alert` border, **10px** left hazard stripe (`repeating-linear-gradient(-45deg, …5px on/5px off)`), filled mono badge, live numbers mono 600 `--alert` (15건 · 2026-09-04 · 퓨쳐켐) |
| Board | craft panel; title 17/700; freshness `기준 2026-08-22 04:14 KST` mono 11 `--ink-3`; tabs 488/50/422/16 at **44px** hit, active 600 + **2px `--ink-1`** border, counts **mono 11** (F5); row grid `86px 262px(1fr) 300px 230px 96px`, **9px** v-pad, **dashed `--border-soft`**; ① extras `청약 2026-09-04` + `발행가 확정 전`; ②/③ extras empty (no dash); DDay right-aligned, 17px mono 600, D-DAY **white on `--alert` 2px 10px**, ≤7d alert, **D+n faint `--urgency-far`** |
| Two strips | ② 진행 중 **57건** = `open_now.count`, expands to 57 rows all with faint D+ and **no 종료**; 일정 추후결정 **4건**, 4 `StateBadge`, **no date anywhere in the strip** |
| Stale state | with `MIJUAL_STALE_AFTER_HOURS=1`: chip flips to `--alert` on `--alert-tint` **4×10** + `· 13시간 전 데이터`, the inset notice appears (`--surface-inset`, **2px `--alert`** left rule, 12px `--ink-2`), **389 rows render identically, opacity 1** — never dims, never dark |
| Chrome | nav **52px**, transparent, 1px `rgba(255,255,255,.12)`; ring-white wordmark **h19** (natural 2178×346, 119.59×19); links 13.5px, active 600; 로그인 `rgba(255,255,255,.68)`; `[의견]` mono 12 + `rgba(255,255,255,.3)`; **3 `data-vocky-trigger`**, **0 script tags** (`NEXT_PUBLIC_VOCKY_SRC` unset, as S18 decided); footer 1px `rgba(255,255,255,.14)`, wordmark h17, positioning mono 11 `.45`, right column 12px `.72`, bottom row mono 11 with **AI 질문** (not 해설) |
| Mobile | top bar 52px, 메뉴 **44×44**, sheet rows **48px** with a **200ms opacity** fade (`.sheet.sheetOpen`), compact tabs 44px, two-/three-line rows at 11px v-pad, **0 px** horizontal overflow, exactly **one** `position: fixed` element (the backdrop) — P6's corner stays clear |

### R3 — event detail (S13), 11 real pages × 2 viewports

Anatomy (crumb · craft header · identity · countdown · 환산 블록 · field sections with a
`Citation` each · 정정 strip · provenance mono 10px) verified on ①/②/③; **220px label column**
(`"label value" / "label cite"`) confirmed; **86/88 checks pass**, the two non-passes being
script artifacts (below). Highlights:

- **① unpriced (계양전기)** — `발행가 확정 전` + `확정 예정 2026-09-01`, **no derived money**;
  the only 원 figures on the page are `4,985원 -> 3,200원` **inside the 정정 요약 rendered
  verbatim** (R3 §5 asks for `interpretation.summary` verbatim; those are the issuer's own
  stated 예정발행가, not a product-derived amount, and the 환산 chain still shows none).
- **① lapsed (한화솔루션)** — chain 확정발행가 22,100원 → 할인율 20.0% → 증서 1주 5,525원「추정」
  → 배정비율 10 decimals; 청약 결과 inset **206.4억원**「추정」; the **multi-part citation**
  opens **both addends separately** (`38,427,609` + `2,888`), never joined (P5.S20's rule).
- **② sparse (트리니티항공)** — fact strip + the locked closing line, **0 field rows, no
  placeholder**. **② past opening** — reads **진행 중**, 종료 appears nowhere.
- **② identity (풍전약품 `20250930000508`)** — `공시 본문 표기: 에스씨엠생명과학 주식회사 — …`.
- **③** — 매수예정가격 **5,649원** with its `매수예정가격 5,649` quote on 세기상사; **no row at
  all** on 미래에셋비전스팩7호; 1단계/2단계 + the dependency sentence.
- **추후결정 (경남제약)** — badge + `카운트다운 없음 — 일정이 공시상 미정`; the countdown column
  contains **no digit at all**.
- **철회 (썸에이지)** — notice + one citation, **0 field rows, no countdown, no old dates**.
- **기재 불일치 (대한광통신)** — both readings (2,117,937 vs 2,083,302), both cited, the locked
  header/footer sentences, badge `발행사 기재 불일치`.
- **CorrectionStory (HLB테라퓨틱스)** — rail opens with 3 rows and, with no readable 본문,
  marks **no** row 현재 읽는 버전.
- Every page: no `▷`, no `undefined/NaN/[object Object]`, **zero fixed elements**, DART link
  carries the page's own `rcpNo`.
- **Collapsed-citation width rule holds at 768 / 1120 / 1440**: every `.chainStep` ≤ 340px, no
  one-character-per-line row, 0 overflow.

### R4 — 내 종목 조회 (S14)

Search + locked 검색 불일치 line (query kept in the box) · 보유량 strip (mono right-aligned
`inputMode=numeric`, 100/500/1,000주 chips, session caption) · **restore chip `이전 입력 500주`
on a different stock, never auto-filled** (sessionStorage `mijual.lookup.holdings` only) ·
live rights ranking (D-91 → D-280 → D-327 → **D+46 open last**) · 놓친 돈 (frame line appears
only once a count exists, **679,575원**「추정」 + 하한 545,181원「추정」 + coverage caption,
`배정 123주 × 5,525원`, `= 500주 × 0.2465120994 · 1주 미만 버림`, `발행 − 청약 = 소멸
3,734,925주 (8.86%)` + 206.4억원, one `Citation` per row, calc footer, disclaimer footnote) ·
unpriced ① (배정 115주 · **+23주** · **no 원 anywhere**) · no-event empty state (고려아연,
감시 중 488건) · ② rows carry only R4's signed per-share 전환가액, **no per-holding money**,
**진행 중** never 종료 · coverage boundary panel · mobile 0 overflow. **27/29**, both
non-passes script artifacts.

### R5 — auth + 내 포트폴리오 (S15/S16)

Auth panel (one panel + 전환 링크, permanent PII inset, sample entry at the foot, 8자 미만
client-side, login failure as **one body line in body ink — never `--alert`**, 확인 중 on the
button) · reset request + confirm surfaces, **`invalid_reset_token` stays silent** ·
conversion touchpoints (조회 offer only after `convert()` yields a value and **only for an
anonymous reader** — verified in the running product and in the gate itself; the detail
one-liner present on a D-3 ①, **absent on a D+43 one**) · holdings row + **inline edit with
저장/취소 on one row, no modal** · 삭제 → **되돌리기** restores · D-day sections with
`기준 2026-08-22 (KST)` · 지나간 chip `기간 지남 · D+43` on `--surface-inset`, **never alert** ·
**챙긴 돈 flips label 놓친 돈 → 챙긴 돈 to `--live`, same 679,575원「추정」, caption 본인 표시 ·
계정에 저장, no total anywhere** · 알림 설정 (수신 주소 + 변경, chips **7일 전 + 1일 전**
selected by default, **KakaoTalk row with zero controls**, 로그아웃, 계정 삭제 arming in place)
· logged-in chrome (nav links unchanged, **mono 축약 이메일 `s19-…com`**, menu =
내 포트폴리오/알림 설정/로그아웃) · 로그아웃 flash **once**, gate redirects only `/portfolio*` ·
**sample mode**: banner 「구성 예시」, nav 「샘플」 + 샘플 종료, **no `@`, no 알림 설정, no
종목 추가**, four pinned issuers, five D-day rows (S8 note 14's live extra), and **logging in
with a sample loaded shows an empty account portfolio + a 계정 이전 offer — never the sample
rows as the account's**. Test accounts created for this pass were deleted through the
product's own 계정 삭제; `GET /auth/me` back to `{"authenticated": false}`.

### R7 — 운영 관제 (S17/S18)

Door renders **in place at the requested URL** with no ops chrome, no reader chrome, exactly
one control, and a **byte-identical failure line for a wrong ID and a wrong password**; login
restores the requested tab. Six signed tabs in order; ops bar with lock chip
(`mijual:lock:pipeline free`), KST clock, 로그아웃. Idiom: opaque **`rgb(14,26,21)`** panels,
1px `--border-strong`, **zero ornament, zero shadows, all radii 0**, `min-width: 1180px` and no
reflow at 900px. 개요: tiles reproduce `gates summary` (488/628 · 710 · 618/4/10/78), beat
schedule from the configuration (07:30/19:30), run log, **「실행 기록 없음」 rows in alert ink
`rgb(224,87,63)`**, `▷ $0.0000` verbatim, 가동 전 미결 quoted from `decisions` (D-4). 게이트
대기열: raw English codes, `rate 기준 691 distinct (rcept_no, field_key) / 710 stored · 19
duplicates`, **no action control anywhere**. 정확도: `judged_by` block above the numbers,
quota labelled `20,000/day`. 대화 로그 / 사용자 / 피드백: honest `0건`, **no 「준비 중」**, no
샘플 로드 여부 column, `save_feedback 대기 0건` on 대화 로그, and the vocky view rendering the
signed 「API shape 확정 대기」 beside the raw `unconfigured` state over the decided column
names. **No `/ops` substring in any reader surface's HTML.** 41 checks, 40 pass + 1 artifact.

### Cross-cutting trust rules

| Rule | Result |
|---|---|
| No untagged estimate / no tagged fact | **pass** — every 억원/원 estimate carries 「추정」; the fact sentence (365,527,824주 · 14.0%) and the four stat counts carry none |
| No money before 확정발행가, any surface | **pass** — detail, 조회 and the portfolio all show share counts and no derived money on an unpriced ① (the only 원 text is the verbatim 정정 요약, above) |
| No ②/③ per-holding money | **pass** — the sample's ② row carries only 전환가액 15,552원 (R4's signed per-share context), the ③ row no amount at all |
| No browser-computed / non-KST D-day | **pass** — 40 board rows compared against `/board`'s own `countdown.dday`: **0 mismatches**; the countdown diffs the served absolute instant (0 s off) |
| Past ② never 종료 | **pass** — landing strip, detail, 조회 |
| 추후결정 never beside a date | **pass** — board strip and detail column |
| No placeholder where a gate blocked a field | **pass** — 에이럭스 `20250908000110` renders exactly its two served fields and nothing else |
| 조회 and 포트폴리오 never disagree | **pass** — 한화솔루션 500주 = **679,575원** on both (and 1,000주 = 1,359,150원) |
| **D2's trigger (both halves)** | **not fired** — no two of the 389 rendered board rows share an `rcept_no`; 코이즈 serves `totals.offerings: 1` and renders one breakdown row |

### Script artifacts (the four "FAIL" lines that are not defects)

1. *"①-unpriced: no 원 amount anywhere"* — matches `4,985원 -> 3,200원` inside the verbatim
   정정 요약 (see R3 above).
2. *"추후결정: no date within 60 chars"* — `innerText` flattening puts the header's
   `최초 공시 2026-05-21` near the badge; the countdown column itself has no digit.
3. *"놓친돈: frame line"* — ran before a holding count was typed, and the frame line is
   deliberately absent until then (S14 note 4).
4. *"② 진행 중, never 종료"* — the probe used a wrong `corp_code` and measured a 404 page.

---

## 3. Every `S19` mention in `phase.md`, with its disposition

| Where | Item | Disposition |
|---|---|---|
| DECOMP n2 | D2 duplicate row / double-counted total | **verified** — not fired (board + 코이즈) |
| S1 n6 | Starlette/httpx deprecation warning | **verified** — still one warning, not an error (118 passed); P4's call |
| S3 n9 | next_lapse tie-break shows 퓨쳐켐, not the card's 계양전기 | **verified** — live data, both dated 2026-09-04 |
| S4 n8 / S14 n9 | 청약 closed, 실적보고서 not filed → no signed state | **catalogued** (design gap) |
| S8 n14 / S15 n12 | sample renders 5 rows while the signed subline says 4건 | **verified** — live data, sentence describes the composition; **catalogued** |
| S10 n4 | tag renders `추정` (border = the enclosure); faint `D+n` | **verified consistent everywhere** (landing strip, 조회 기간 지남, 포트폴리오 지나간, detail) |
| S10 n19 / S11 n10a / S12 n12a | Korean inside `--font-mono` falls to the OS face | **judged, no fix** + **catalogued** (below) |
| S11 n2 | footer 49.2억원 is a dated-pack figure | **catalogued** (backing work) |
| S11 n3 | locked positioning line still says 내 종목 연결 | **verified rendered**; **catalogued** |
| S11 n4 | `© 미주알` | **verified rendered**, no year invented; card-only check → **catalogued** |
| S11 n9 | footer 「추정」 at 6.72px | **FIXED (F2)** |
| S11 n10b | 메뉴 button's hairline is a build reading | **verified**; minor, **catalogued** |
| S12 n1 | hero H1 renders 내 종목 조회 | **verified**; card-only → **catalogued** |
| S12 n4 | hero 680px floor | **verified at 768 / 1120 / 1440** |
| S12 n5 | the two tag readings settle together | **settled**: footer = R2's 10px literal via the named prop; landing = 0.56em of the surface's 17px context (9.52px). Both are R2's "10px on landing surfaces" |
| S12 n12b | mobile ① row wraps to a third line | **verified** — content does not fit; nothing truncated |
| S13 n2 | 매수예정가 rendered as an ordinary field row | **verified** (세기상사 / 스팩) |
| S13 n4 / open q | English framework 404 | **verified**; **catalogued** |
| S13 n12 | 340px chain-step cap widens the gap before the arrow | **verified at 768/1120/1440**; **catalogued** (cards decide) |
| S14 n5 | three R4 readings (served coverage start, rights-type chips, per-row calc footer) | **verified rendered as described**; **catalogued** |
| S14 n10b | `[근거]` chip 14px + DART link 17px under the mobile 44px floor | **verified still true**; **catalogued** (a primitive change needs a signed decision) |
| S15 n7 | 조회 offer only for anonymous readers | **confirmed** — R5-2 signs no logged-in variant of that panel; gate verified in the product and in the code |
| S15 n10 | PII inset renders two lines, not "3행" | **verified**; **catalogued** |
| S15 n11 | three composed labels (비밀번호 재설정 · 이메일 · 비밀번호) | **verified rendered**; **catalogued** |
| S16 n3 | storage keys — "S19 will inspect these" | **inspected**: localStorage `mijual.portfolio.sample`; sessionStorage `mijual.lookup.holdings`, `mijual.convert.offer`, `mijual.auth.flash`; **nothing anonymous reaches the server** |
| S16 open q | 계정 이전 heading composed from the round's nouns | **verified rendered**; **catalogued** |
| S15 open q | `invalid_reset_token` silent | **verified**; **catalogued** |

---

## 4. Operator-question catalogue — **do not implement without a signed decision**

Consolidated for `P5.REVIEW` and the operator. None of these is an implementation defect;
each needs a *new visual/product decision* or an operator fact.

**A. Copy the record does not contain**

1. **The not-found page has no Korean sentence** — `notFound()` renders the framework's
   English default inside the correct chrome. The one English string a reader can reach.
2. **An expired/spent 재설정 link says nothing** — `invalid_reset_token` is not one of R5's
   three signed error lines, so the confirm page returns to idle silently.
3. **「API shape 확정 대기」 is half a step stale** (S18) — the shape is decided; what the vocky
   view waits for is the `vk_` credential. Rendered as signed.
4. **The locked positioning sentence still says 내 종목 연결** while the nav says 내 종목 조회.
5. **Composed labels** that no signed line spells: `비밀번호 재설정`, `이메일`, `비밀번호`,
   `계정 이전`, `© 미주알`.
6. **The sample subline says 4건 while the live composition renders 5 D-day rows** (대동기어's
   own lapsed ①). Signed sentence vs live corpus.

**B. States the design never drew**

7. **An ① whose 청약 closed but whose 증권발행실적보고서 has not been filed** (센서뷰 `01593668`,
   클로봇 `01784914`) falls into neither 조회 section, so the stock renders the *no-event*
   empty state. Inventing a line or a 놓친 돈 row would be an invented figure.
8. **R7's 샘플 로드 여부 column has no backing fact** — the column is data-driven and today
   renders as absent; building the backing changes S8's contract and adds a behavioural fact
   about a reader.

**C. Type / layout questions only the cards can settle**

9. **Korean glyphs inside `--font-mono` elements are drawn by the OS Korean face**
   (macOS: Apple SD Gothic Neo) — `StateBadge 추후결정`, the 소멸주의보 badge, `[근거]`'s 근거,
   the footer positioning line, the stat/band lines, the ops-free mono chrome. **Reading I can
   defend, and the one this build keeps:** R1's rule is *"Korean **prose** never mono"*, and
   every prose element does draw in Pretendard (verified with `getPlatformFontsForNode`); the
   three primitives are **chips the record itself draws in mono** ("추후결정 = mono chip",
   "mono tag", "`[근거]` chip mono 11"), as are R2's positioning/stat/band lines. So this is
   the specified face, not a violation — **but** `--font-mono` carries no Hangul, so those
   Korean glyphs are a different face per platform. Changing it means editing the landed
   `tokens.css` (adding a Hangul-capable mono or a Pretendard tail) = **a design change**.
10. **`[근거]` chip (14px) and its DART link (17px) sit under the mobile 44px floor**, as do
    the board row's inline corp name (~21px tall) and `↗` (7×17) — the signed row anatomy is
    11px v-padding and two lines, so enlarging them restyles a signed element.
11. **The ① 환산 chain's 할인율 step occupies its 340px citation cap on desktop**, so the gap
    before the next arrow is wider than the round's even spacing.
12. **The hero H1 renders 내 종목 조회** (R4 named the surface) where R2's literal says
    내 종목 연결 — check against the card.
13. **The PII inset renders two lines** where R5's copy list says "PII 패널 3행".
14. **The 메뉴 button's hairline** (`rgba(255,255,255,.3)`, borrowed from the `[의견]` trigger)
    is this build's reading of "button".
15. **A mobile ① board row wraps to three lines**, and R4's coverage caption / 청약 종료 line
    render their served dates in **sans**, while the boundary panel renders its dates in mono —
    a small internal inconsistency I deliberately did **not** "fix", because the record gives
    those as whole signed sentences and choosing the split is a typographic decision.

**D. Product / data decisions already standing**

16. **The footer's 49.2억원 is a dated-pack figure**, not a served one — making it live is
    backing work (a persisted precomputation + a summary key).
17. **vocky ships no embeddable widget script**, so the three signed triggers have nothing to
    bind to until the operator wires a capture path.
18. **The countdown cut-off instant** (`MIJUAL_COUNTDOWN_CUTOFF_TIME`, default end of the
    청약 day) and **the 18-hour stale threshold** are stated defaults awaiting the operator.
19. **Re-authentication for 수신 주소 변경** — a live session is authority today; requiring the
    current password would add a control the signed round does not have.

**Observations worth one line each (no decision needed):** the app has **no favicon** (the ring
PNG is 2178×346 and cannot be one without re-encoding a delivered asset — P4/design); and a
tab whose chrome mounted *before* another tab loaded the sample can show the account slot while
its body renders the sample (single-tab behaviour is correct; cross-tab live sync is not signed).

---

## 5. Validation

| Command | Outcome |
|---|---|
| `cd frontend && npm run build` | **pass** (15 routes; re-run after the fixes) |
| `cd frontend && npm run typecheck` | **pass** |
| `cd frontend && npm run smoke` | **pass** — 11/11 `node:test` |
| `.venv/bin/python -m pytest` | **pass** — **118 passed**, 1 warning (the known Starlette/httpx one), 2.58 s |
| `python3 scripts/workflow.py validate` | **pass** — `Workflow validation passed.` |
| Browser pass (headless Chrome over CDP, `npm run start` + uvicorn, `http://localhost:3000`) | ~230 checks across 11 stages; **every failure either fixed and re-measured (F1–F5) or explained above**; re-run of the R3/R4/trust/intermediate-width suites after the fixes shows **no regression** (R3 86/88, R4 27/29, trust 7/9 — same four artifacts; widths **25/25**, previously 24/25) |
| Both servers stopped afterwards | yes (uvicorn + `next start` killed; the test accounts deleted through the product) |

Environment notes: the API ran with `MIJUAL_OPS_ID` / `MIJUAL_OPS_PASSWORD` supplied **on the
command line for this pass only** — the operator's `.env` was never opened, and no credential
was written anywhere. One measurement (`MIJUAL_STALE_AFTER_HOURS=1`) needed its own restart and
was reverted. `NEXT_PUBLIC_VOCKY_SRC` stayed unset, so no third-party script was loaded.

**Gotcha for the next slice that rebuilds:** `npm run start` fails silently into the log with
`EADDRINUSE` if an older `next start` is still listening — and the old server then serves a
build manifest whose CSS chunks 500, which looks exactly like "the fix did nothing". Kill the
listener (`lsof -nP -iTCP:3000 -sTCP:LISTEN`) before restarting, and confirm a CSS chunk
returns 200 before believing a measurement.

## 6. Deviations from `plan.md`

- **The plan named one fix (the footer tag) and a checklist; the browser pass surfaced four
  more contract-level defects** (F1, F3, F4 and, inside F1, R2's tab counts). F1 in particular
  is wider than any single surface — one line in `app/shell.css` — but it is the root cause of
  a type scale that contradicted the surfaces' own cited sizes, so leaving it would have failed
  the slice's purpose. All five are faithful-implementation corrections; none chooses a value
  the record does not state.
- **The 조회 coverage caption / 청약 종료 line keep their dates in sans** (catalogue item 15)
  rather than being "fixed" — the record gives them as whole signed sentences.
- No doc versions were created (P5 versions docs once, at `P5.REVIEW`); the doc-impact notes
  are appended to `phase.md`.
