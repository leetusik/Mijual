# Result — P5.S11: Global chrome (R2)

The chrome every page sits inside is built and wired into the root layout: the 52px nav with
the **three signed slots**, the mobile top bar + sheet, the footer with its three signed
sentences, and exactly three `data-vocky-trigger` elements behind an env seam. No page
surface was built (S12–S17's), no primitive was touched, no token was edited, and **no Korean
string was invented** — every string is transcribed with its source in
`frontend/components/chrome/copy.ts`.

**0 new dependencies. The Python suite is untouched at 113** (this slice edited no Python
file).

## What landed

| file | what it is |
|---|---|
| `frontend/lib/routes.ts` | **the route map** — one module, one statement per path, plus `isActiveRoute` |
| `frontend/components/chrome/copy.ts` | every Korean string the chrome renders, each with its citation |
| `frontend/components/chrome/SiteChrome.tsx` (+ `.module.css`) | nav + page + footer + vocky script; the root layout wraps every route in it |
| `frontend/components/chrome/Nav.tsx` (+ `.module.css`) | the 52px bar (both sides of 480px) and the sheet menu |
| `frontend/components/chrome/Footer.tsx` (+ `.module.css`) | identity column, the three sentences, the bottom hairline row |
| `frontend/components/chrome/AccountSlot.tsx` (+ `.module.css`) | the 로그인 slot — **`P5.S16`'s one swap point** |
| `frontend/components/chrome/VockyTrigger.tsx` (+ `.module.css`) | one trigger, three surface variants |
| `frontend/components/chrome/VockyScript.tsx` | `NEXT_PUBLIC_VOCKY_SRC` seam — unset ⇒ **no script tag** |
| `frontend/components/chrome/Wordmark.tsx` | the delivered ring PNG, height-constrained, never re-encoded |
| `frontend/components/chrome/index.ts` | the chrome barrel (separate from the trust-primitive barrel) |
| `frontend/app/layout.tsx` | edited: `<body><SiteChrome>{children}</SiteChrome></body>` |
| `frontend/app/stocks/page.tsx` · `frontend/app/ask/page.tsx` | bare shells — `P5.S14` / **P6** replace them |
| `frontend/README.md` | the layout tree, the route table, and the environment table |

`app/page.tsx` is untouched and now renders inside the chrome, as the plan requires.

## The route map (S12–S17 inherit it)

| route | surface | owner |
|---|---|---|
| `/` | 관제 현황판 | `P5.S12` (today: S10's foundation proof) |
| `/stocks` | 내 종목 조회 | `P5.S14` — the API's own noun for this surface, so page path and contract path are one vocabulary |
| `/ask` | AI 질문 | **P6** — deliberately not `/explain`: 해설 is the label R6 retired |
| `/auth/login` | 로그인 | `P5.S15` — **no page yet**; `mijual.web.auth.RESET_PATH` already fixes `/auth/reset`, so the auth surfaces live under `/auth/` |
| `/ops` | 운영 관제 | `P5.S17`, linked from nowhere in the reader chrome |

The nav's active state is `isActiveRoute`: `/` exact, everything else prefix-with-boundary, so
`/stocks/00162461` keeps 내 종목 조회 underlined.

## Decisions, and what each one is grounded in

1. **The superseded labels render, never R2's literals.** The bar reads 내 종목 조회 · 관제
   현황판 · AI 질문 (R4 and R6, via `docs/current/frontend.md`'s supersession table and R6's
   own "nav finalized" line), and the footer's bottom row reads **AI 질문** where R2 landed
   해설. Verified in the served HTML: the strings 해설 and `▷` appear **nowhere**.
2. **The gate-cost sentence keeps its words and loses its `▷`.** R2 §Copy landed
   "▷ 49.2억원은 할인율 인용이 게이트를 통과하지 못해 총액에서 제외했습니다"; the R2 gate
   retired `▷` from the UI and the build prompt asks for a "추정-tagged 49.2억원", so the
   value goes through `EstimateMarker` and the sentence is otherwise byte-identical
   (including its missing full stop). **Its only placement is the footer** (R2.1 note 4).
3. **The positioning line is transcribed verbatim, including 내 종목 연결.** It is *locked
   context*, not R2's copy: R2's handoff §3 lists "the positioning sentence" among the locked
   items and §1 states it (also R1's handoff and the operator's own
   `docs/reference/challenge/00_HANDOFF.md`). R4's supersession is about the **nav label**;
   rewriting a locked sentence would be a design change. Flagged for `P5.S19`/`P5.REVIEW`.
4. **`© 미주알`.** R2 writes the bottom row as "© · 자료: …" and the card that showed the
   line stays in the design project. The symbol is R2's, 미주알 is the product's own name
   (it is in the disclaimer sentence on the same surface), and **no year is invented**.
   `P5.S19` should check it against the card.
5. **The wordmark is the delivered ring PNG rendered with a plain `<img>`.** R2 says "white
   ring wordmark PNG (h 19px)" / "(h 17)" and R2.1 re-cut the chrome "with the white ring
   wordmark"; the file is `mijual-logo-ring-white.png` (2178×346 — the MIJUAL wordmark with
   its orbital ring; the *wordmark* pair has no ring and is 1788×324). `next/image` is
   deliberately not used: it would serve a re-compressed derivative of an asset the phase
   rule says is never re-encoded. Intrinsic dimensions travel as attributes so a 52px bar
   reserves the right box before the PNG arrives.
6. **vocky is wired through `NEXT_PUBLIC_VOCKY_SRC`, via `next/script` in the shell.** The
   script URL is external and appears in no record — inventing one would be inventing a fact
   about someone else's system. Unset ⇒ no tag, triggers still render (measured).
   `next/script` in the root layout is what Next documents as "only load once, even if a user
   navigates between multiple routes in the same layout", which is R2's "load vocky script
   **once**, deferred, in the shell".
7. **The sheet stays in the DOM and is hidden with `display: none`.** An external script that
   binds `[data-vocky-trigger]` at load would never see a trigger React mounts later, so all
   **three** triggers exist from the first paint; `display: none` keeps the closed sheet out
   of the tab order and out of the accessibility tree, and the desktop bar never shows it.
8. **Nothing in the chrome is `position: fixed` and no floating button exists** (R2 §6-4),
   so the bottom-right corner stays clear for P6's launcher (R6: 런처·위젯은 vocky 트리거와
   모서리 충돌 금지). Measured: zero fixed elements in the document.

## Validation

Every command was run from a clean tree at the end; servers and browsers were stopped
afterwards.

| command / check | result |
|---|---|
| `cd frontend && npm run build` | **pass** — 4 routes prerendered (`/`, `/_not-found`, `/ask`, `/stocks`); run last, so `next-env.d.ts` is back in its committed form |
| `cd frontend && npm run typecheck` | **pass**, no output |
| `cd frontend && npm run smoke` | **pass** — 3/3 in 75 ms |
| `.venv/bin/python -m pytest` | **113 passed**, 3.47 s — baseline untouched |
| `python3 scripts/workflow.py validate` | **Workflow validation passed.** |
| dev server: `GET /` · `/stocks` · `/ask` | **200** each |

### Real browser (headless Chrome 141 over CDP, `npm run dev` at `http://localhost:3000`)

Desktop 1280×1200:

- nav **height 52**, background `rgba(0,0,0,0)` (transparent over the cosmos), bottom border
  **`rgba(255,255,255,0.12) 1px`**;
- three links at **13.5px** → `/stocks`, `/`, `/ask`; on `/` the active one is
  **weight 600 + `rgb(255,255,255)` 2px underline** with `aria-current="page"`, and the
  active state **moves** to 내 종목 조회 on `/stocks` and to AI 질문 on `/ask`;
- wordmark `/assets/mijual-logo-ring-white.png`, `complete: true`, natural **2178×346**,
  rendered **119.59 × 19** in the nav and **17** high in the footer, `alt="미주알"`;
- 로그인 → `/auth/login`, colour **`rgba(255,255,255,0.68)`**;
- **three** `[data-vocky-trigger]` buttons — nav `[의견]` (mono 12px, hairline
  `rgba(255,255,255,0.3)`), sheet 의견 보내기, footer 의견 보내기 (mono 11 in the bottom row);
- footer top border **`rgba(255,255,255,0.14) 1px`**; positioning line **mono 11
  `rgba(255,255,255,0.45)`**; the three sentences at **12px `rgba(255,255,255,0.72)`** in
  Pretendard, byte-identical to the record; bottom row mono 11 =
  `© 미주알 · 자료: 금융감독원 DART 전자공시 | 의견 보내기 · AI 질문`;
- the 추정 tag renders on 49.2억원 in `rgb(95,208,165)` with its hairline border;
- **no `<script src>` matching vocky** with the env unset; **zero** `position: fixed`
  elements anywhere.

The vocky seam, both ways: rebuilt once with
`NEXT_PUBLIC_VOCKY_SRC=https://vocky.example.invalid/widget.js` → **exactly one** script tag,
still exactly one after a client-side navigation to `/ask`, triggers still 3. Rebuilt without
it → zero tags, triggers still 3. The committed state is the unset build.

Mobile 390×844:

- top bar **52**, wordmark h **19**, desktop links `display: none`, 메뉴 button **44×44** in
  mono with `aria-expanded="false"`;
- opening it: `aria-expanded="true"`, sheet `display: flex`, opaque `rgb(10,19,16)`, rows
  **48 / 48 / 48 · 1px divider · 48 / 48** — the three destinations, R5's 구분선, 로그인 and
  the 의견 보내기 trigger; three triggers in the document;
- closing it: `transition-duration 0.2s`, then `display: none` with the rows untabbable —
  the round's 200ms fade;
- under **`prefers-reduced-motion: reduce`** the same close is a **cut**: `display: none`
  immediately after the click, transition 0.001s.

Screenshots (scratch, not committed): desktop landing, desktop footer, mobile sheet open.

### Copy check, against the record

The served HTML was compared string-by-string with the landed record: provenance sentence,
gate-cost value + tail, disclaimer, positioning line, `자료: 금융감독원 DART 전자공시`,
`© 미주알`, the three nav labels, 로그인, 메뉴, `[의견]`, 의견 보내기, the 추정 tag — **all
present**. Absent, deliberately: `▷`, 해설, a 내 종목 연결 nav link, and any placeholder
string (`준비 중`, "Coming", "TODO").

## Deviations from `plan.md`

1. **The browser check ran against `npm run dev` at `http://localhost:3000`, and the same
   checks were also run against `npm run build && npm run start`.** Using
   `http://127.0.0.1:3000` trips **Next 16's dev-origin protection**: two client chunks
   answer **403** to the browser (curl gets 200), hydration never completes, and every
   interactive check silently reports the un-hydrated state. Recorded in `phase.md` for
   S12–S17.
2. **A bare `/stocks` shell was created as well as `/ask`'s.** The plan names one bare
   shell, but it also requires the nav's three slots and their active state to work; a nav
   link to a 404 is not a working slot. `P5.S14` replaces it, exactly like S12 replaces
   `app/page.tsx`.
3. **The 로그인 slot links to a route that has no page yet** (`P5.S15`'s). Deliberate: an
   empty stand-in for a signed surface would read as a dropped design element, while a
   missing page is honest and one slice away.

Nothing else departs from the plan.

## Findings recorded in `phase.md`

The chrome component map and its two seams, the route map, the estimate tag's rendered size
in a 12px sentence (**6.72px** — R2's landing literal is 10px; the primitive's `0.56em` is
what produces it, and the plan forbids touching a primitive), the gate-cost figure being a
dated-pack number the presentation contract does not serve, the locked positioning line's
내 종목 연결, R5-4's 랜딩 푸터 sample entry belonging to a later slice, and the
`allowedDevOrigins` gotcha.
