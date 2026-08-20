# R2 Implementation Contract — Landing + Chrome. Build from this without inventing anything.

R1 contract (tokens/type/motion/trust primitives) is locked and still governs; this adds the landing + chrome layer. Reference implementations: `landing/*.html`, `chrome/*.html` in the design-system project. Token delta (R2.1): the `.cosmos` dark scope + `--panel-bracket`, `--panel-glow` (shadow), `--live-solid` in `foundations/tokens.css`.

## Cosmos & craft panels (R2.1 — governs everything below)
- The landing is a **dark cosmos page**: body `#0a1310`; ONE continuous full-page starfield behind all sections (≈240 stars desktop / 160 mobile, twinkle 2.5–6.5s, 80s drift), root-level radial green glows (strong at ~12% height, faint echo at the bottom), shooting stars staggered down the whole page (~5 desktop / 3 mobile, 9–18s cycles). Orbit ellipses (980×280 + 1200×360, rotate −14°, orbiting star on offset-path 26s) live in the hero ONLY and must sit fully clear of the nav line and the first panel — give the hero vertical room (110/160px padding desktop); **never shrink the rings**.
- `class="cosmos"` on the page root (with `color: var(--ink-1)` set there) remaps every token — surfaces, ink, borders, semantic, rights tints, urgency — so RightsChip/DDay/etc. render correctly unchanged. All `--token` references below resolve through that remap.
- **Craft panel** = translucent dark card: `--surface-card`, 1px `--border-strong`, top-edge glow `box-shadow: var(--panel-glow)`, and 9px corner brackets (2px L-shapes, `--panel-bracket`) at all four corners. Used for: value card, countdown/stats card, 소멸주의보, board.
- Solid actions on dark (조회) = `--live-solid` bg, `rgba(95,208,165,.45)` hairline, white text. Search input = dark console field: `rgba(8,17,13,.72)` bg, `rgba(163,196,180,.4)` hairline, white text, placeholder `rgba(255,255,255,.38)`.
- **Estimate mark (landing surfaces)**: a bordered sans 10px 「추정」 tag beside the value (`#5fd0a5` text + hairline), NOT ▷. An estimate never renders untagged. (`EstimateMarker`'s ▷ stays for other surfaces pending sign-off.)
- Reduced motion: starfield/twinkle/orbit/colon-blink freeze; shooting stars hide.

## Page shell
- Body `#0a1310` + cosmos layers (above); content column max-width 1120px; breakpoints 480/768/1120 mobile-first.
- **Nav** 52px, transparent over the cosmos, 1px `rgba(255,255,255,.12)` bottom. Left: white ring wordmark PNG (h 19px) + links 내 종목 연결 · 관제 현황판 · 해설 (13.5px; active = 600 + 2px #fff underline; labels provisional). Right: 로그인 (quiet, `rgba(255,255,255,.68)`) + vocky trigger `[의견]` (mono, hairline `rgba(255,255,255,.3)`).
- **Mobile**: top bar 52px (white ring wordmark + `메뉴` button, mono, 44px hit) + sheet menu: rows ≥48px. Sheet close = 200ms fade.
- **Footer**: white-on-dark, 1px `rgba(255,255,255,.14)` top. Left col: white ring wordmark (h 17) + positioning line (mono 11, `rgba(255,255,255,.45)`). Right col, 12px `rgba(255,255,255,.72)`: ① provenance sentence "모든 수치는 DART 공시에서만 나왔고, 추정치는 [추정] 표시로 구분했습니다." (re-cut, needs sign-off), ② gate-cost sentence (추정-tagged 49.2억원 — its only remaining placement), ③ disclaimer. Bottom hairline row: © · 자료: 금융감독원 DART 전자공시 | 의견 보내기 · 해설 (mono 11).

## Hero (내 종목 연결, search-first — R2.1)
No logo or eyebrow in the hero body (the nav carries the mark). Centered: H1 52px/700 "내 종목 연결" → sub 17px `rgba(255,255,255,.78)` "종목명 하나로 놓친 권리와 진행 중인 권리를 조회합니다" → search row (console input + 조회, 52px tall, 560px total) → mono stat line: 2026년 소멸한 신주인수권 가치 718.1억원「추정」 · 감시 중 488건 · 30일 이내 마감 34건 (number+건 spans nowrap). Mobile: H1 34px, 48px controls. This IS the 내 종목 연결 surface — no separate bridge panel; submit goes to R4's 조회.

## Retrospective anchor (below hero — two craft panels, 1fr / 340px, 20px gap)
- **Value card**: mono 11 `--ink-3` eyebrow "2026년에 소멸한 신주인수권 가치" → 46px/700 718.1억원 + 「추정」 tag → band line mono 13.5 (밴드 하한 548.7억원「추정」 (권리락 조정 가정)) → fact sentence 15px, full card width, one line (no max-width cap). The gate-cost line does NOT appear here (operator) — footer only.
- **Countdown/stats card**: countdown + 2×2 live stats (감시 중 이벤트 488건 · 30일 이내 마감 34건 · 소멸 앞둔 신주인수권 15건 · 읽은 실적보고서 69건) — fed live from the same summary the board uses. Mobile: value card then countdown card, stacked.

## Countdown
Mono 28px/600 `--alert`: `{d}일 HH:MM:SS`, colons `animation: blink 1s step-end infinite`; `prefers-reduced-motion: reduce` → no animation, static value. Target = earliest 소멸 instant (today: 계양전기 청약 마감 2026-09-04 KST; exact cut-off time TBC). The instant arrives from the backend as an absolute KST timestamp; the browser only diffs against it — it never derives dates.

## 소멸주의보 strip
Per R1 Subbrand spec, full content-width, between the anchor panels and the board. Craft panel with `--alert` border + **10px hazard stripe on the left edge** (repeating −45° `--alert` stripes, 5px on / 5px off); filled alert badge 소멸주의보. Body = 발표용 문장 4 with live numbers (15건 / 2026-09-04 / 계양전기) in mono `--alert` 600.

## Board (소멸 카운트다운)
- Craft panel (translucent dark, brackets). Header row: title 17px/700 + freshness chip right.
- **Freshness**: mono 11 `기준 YYYY-MM-DD HH:MM KST` in `--ink-3`; when stale → `--alert` on `--alert-tint` padding 4×10 + suffix `· N시간 전 데이터`, plus inset notice (bg `--surface-inset`, 2px `--alert` left rule, 12px `--ink-2`) above the tabs. Board content NEVER dims/hides on staleness.
- **Tabs**: 전체 488 · 유상증자 신주인수권 50 · 전환사채 오버행 422 · 주식매수청구권 16 — counts mono 11; active = 600 + 2px `--ink-1` underline; ≥44px hit; mobile uses compact labels (전체/유증/CB/매수청구) with x-scroll.
- **Row** (desktop grid `86px 1fr 300px 230px 96px`, 9px v-pad, dashed `--border-soft` separators): RightsChip compact | corp 600 + `↗` link to `https://dart.fss.or.kr/dsaf001/main.do?rcpNo={rcept_no}` (mono 11 `--ink-3`) | countdown label + date (label 12px `--ink-2`, date mono `--ink-1`) | per-type extras | DDay right-aligned (showDate=false; date lives in col 3).
- **Extras col**: ① pre-fixing = `청약 YYYY-MM-DD` (mono) + chip `발행가 확정 전` (sans 11, `--surface-inset`, 2×8). ②/③ = empty — absence is the design, no dash.
- **Sort**: D-day ascending across types (전체). Rows with 날짜 없음 (추후결정 countdown, 4 today) do not rank — R3/R4 decide their surface.
- **Mobile row** = two lines: [chip + corp … DDay] / [label + date · extras], 11px v-pad.
- **② open-window strip** pinned under rows, `--surface-raised`, hairline top: "전환청구 **진행 중** — 개시일이 지나 지금 전환할 수 있는 전환사채 **56건**" (진행 중 in `--live` 600, count mono 600) + 펼치기 (hairline button; expands to the same row anatomy with DDay rendering D+N). Never label past ② "종료/마감". Past ①/③ rows: not on the landing at all.

## vocky
Load vocky script once, deferred, in the shell. Triggers: nav `[의견]` button, mobile sheet 의견 보내기 row, footer 의견 보내기 link — each a plain element with `data-vocky-trigger`. Trigger styling: mono 12, 1px `--border-strong`, white bg, `--ink-2`; hover = `--surface-raised` + border `--ink-3`; focus = 2px `--focus-ring`. Do not style the widget itself; do not add a floating button.

## Trust rules restated for this page
Every estimate carries the 「추정」 tag on this page (▷ elsewhere until the system-wide decision); a fact never carries either mark. D-day/dates computed upstream in KST. No placeholder where a gate-failed field would be. 추후결정 never shows a date. ② past language = 진행 중.
