# Result — P7.REVIEW: phase review of P7 (실서비스 정상화 fix pass)

**Verdict: `pass`.** All eleven operator items are closed or correctly routed, every override is one
`intent.md` authorises and is scoped to the override, no signed element was dropped, **zero Korean was
minted**, and the trust rules are intact — all of it re-measured here independently rather than read
out of the slices' reports. Two things the operator must see before P4: **item 8 is closed only on its
/ask half** (의견 needs an operator input no code can supply, decision #1 below), and **the largest
remaining "not organized" symptom on 내 포트폴리오 was deliberately not invented** (decision #8). Nine
doc versions consolidate the phase; the Doc impact list under-covered four docs and this review closed
that itself (§5).

---

## 1. Validation — the whole phase, together

| command | outcome |
|---|---|
| `python3 scripts/workflow.py validate` | **pass** — `Workflow validation passed.` (re-run after consolidation: still pass) |
| `cd frontend && npm run typecheck` | **pass** — `tsc --noEmit`, no output |
| `cd frontend && npm run smoke` | **pass** — **15/15** `node --test lib/*.test.ts`, 170 ms |
| `.venv/bin/python -m pytest` | **pass** — **139 passed**, 1 known Starlette/httpx deprecation warning |
| `git status` | clean of source changes — only `works/` files and this slice's own outputs |
| `make stack-status` | postgres **Up (healthy)**, api pid 25177, web pid 13009 — **left up, as found** |
| isolated production build (`rsync` copy of `frontend/`, `npx next build`, `MIJUAL_API_ORIGIN=http://127.0.0.1:8000`) | **pass** — compiled 243 ms, TS 1.17 s, **16 routes**, static 15/15. The dev server's `.next` was never touched (`frontend/.next/dev` untouched, stack never restarted) |

### The independent headline spot-check (this review's own harness, not S1–S9's numbers)

Headless Chrome over CDP, **fresh profile per run**, `next dev` on **`http://127.0.0.1:3000`** — the
operator's own origin — at **1440×900 and 390×844**. Storage cleared before every run.

| # | operator item | check | measured |
|---|---|---|---|
| 1 | nav | anchors in the chrome | **관제 현황판 · AI 질문** + brand + 로그인; **no `/stocks` link**; the 390 sheet shows the same two rows + 로그인 |
| 2 | typeahead | `계양` typed into the hero | `role="combobox"`, **1** candidate 「계양전기 012200」, exactly **1** `GET /stocks/suggest` 200; ↓ sets `aria-activedescendant`; **Enter → `/stocks/00102618`** (the handle), page rendered. At 390 on `/stocks`: `에스` → **8** options, 44px each, panel `dx=0 dw=0`, **0** horizontal overflow |
| 2b | the rule survives | submit **without** choosing | `에스` → stays on `/stocks?q=에스` with the 검색 불일치 sentence; `계양` → `/stocks/00102618`. `GET /stocks/suggest?q=zzzz` → **200 `{"candidates": []}`**, never 404; `/stocks/{corp_code}` still 200 (declaration order intact) |
| 3 | focus | click the hero input | `outline-style: **none**`, `border-color: rgb(163,196,180)` (the brightened hairline), input right edge **924.1** = 조회 left edge **924.1**, **gap 0** — nothing left that *can* paint under the button |
| 3b | the floor kept | a **real** Tab walk (not `.focus()`) | brand · 관제 현황판 · AI 질문 · 로그인 · `[의견]` all wear **`solid 2px rgb(143,178,232)` @2px** with `:focus-visible` true; the single `input[type=text]` stop is the one difference |
| 4a | board length | rows at first paint | **30** at 1440 **and** 390; control reads 「**356건 펼치기**」, 44px at 390 |
| 4a | window works | click it | 30 → **60**, **0 network requests**; tab counts unchanged **488 / 50 / 422 / 16** |
| 4b | 펼치기 lives | click both strips | 60 → **120** (+60) → **124** (+4); `aria-expanded` false → **true** on both; the window control correctly carries none |
| 5 | login | the chrome, sample cleared | **2** `a[href="/auth/login"]` (desktop slot + sheet row); clicking it reaches `/auth/login` with **0 document loads**, and the form renders 이메일 / 비밀번호 / 로그인 / 계정 만들기 / 비밀번호 재설정 / 샘플 |
| 6 | countdown | one page, 75 s | `12일13:12:54` → `…:12:42` at 12 s → `…:11:39` at 75 s — **ticking** |
| 7 | no state stomp | same page, typed 계양 + a `window` marker | after **75 s**: marker alive, input still `계양`, **0 top-frame navigations**; `/_next/*` 403s **0**, HMR handshake **101** |
| 8 | AI 질문 send | **one live turn** through the widget | `POST /api/ask` **200**, streamed to completion in **6 s** — tool rows, answer, verbatim DART 원문 citations, footer 「근거 1건 · 20260724000546 · 2026-08-23 10:49 KST」, link row. Server ledger: **▷ $0.0115 estimated** (14,319 tokens, thinking LOW, never billed) |
| 9 | 챙겼습니다 | sample portfolio, click the checkbox | 놓친 돈 4 → **3**, 챙긴 돈 0 → **1**; the row reads 「챙긴 돈 500주 기준 **679,575원**추정」 — same figure, 「추정」 kept; document height **1533 → 1533**, zero shift |
| 10 | self-narrating copy | `innerText` of `/`, `/stocks`, `/stocks/00102618`, `/portfolio?sample=1`, `/auth/login`, `/ask` | `localStorage` **0** · `sessionStorage` **0** · `브라우저 세션` **0** · `이 브라우저` **0** · bare `브라우저` **0** on all six. 「서버 전송 없음」 renders once (stock page), 「본인 표시」 twice (the sample's two past ① rows) |
| 11 | widget | launcher | **1** launcher, **2** `position: fixed` nodes at 1440; opens the **440×620** widget whose empty state still prints 「완전 익명 — 로그인도, 질문 수 제한도 없습니다 · 대화는 익명으로 저장됩니다 (품질 점검용)」. **0** at 390 — the signed ≤480 rule |
| — | RC-A holds | whole session | `/_next/*` **403s = 0**, HMR **101** at both widths; `grep -c "Blocked cross-origin" var/stack/web.log` = **4**, still only `P7.S1`'s deliberate negative controls — **none from `127.0.0.1`** across this review |
| — | console | every page above | **0** errors, **0** hydration warnings, **0** responses ≥ 400 (not even the `/favicon.ico` 404 on these loads) |

No account was created (the slot check needed none), so none had to be deleted;
`s19-fidelity@example.com` was left in place per plan. The isolated build copy and the CDP scripts
live in session scratch. The dev stack is up and unchanged.

---

## 2. The eleven items against `intent.md`

Every one is closed **on the operator's own runtime**, which is the acceptance condition
`intent.md` actually sets ("verified in a real browser on the running dev stack").

| item | verdict | note |
|---|---|---|
| 1 nav | **closed** | two slots; scoped to the slot exactly as reading #2 requires; 조회 still reachable |
| 2 typeahead | **closed** | candidates before submit **and** the "never a candidate list" rule intact — reading #4 implemented literally, verified on both halves above |
| 3 focus | **closed, with the question routed** | ring off the text fields; a keyboard indicator kept (reading #1 / D-26). The literal ask ("no selected focus on **all** the input boxes") is honoured for mouse users and for the clipping complaint; whether the operator meant *zero* indication is decision #2 |
| 4 board | **closed, with the number routed** | both halves: 30-row window **and** the strips' 펼치기 working. The 30 is D-24, decision #3 |
| 5 login | **closed** | RC-B was a real, origin-independent bug; the slot answers, the round trip works (S2 and S9 each ran a full signup→삭제 cycle through the product and left the DB clean) |
| 6 countdown | **closed** | RC-A artifact; ticks |
| 7 auto-reload | **closed** | there is no auto-refresh feature in the app; the reload was Next's dev client after a rejected HMR socket. 75 s, value kept, 0 navigations |
| 8 AI 질문 send | **closed on /ask; 의견 is the operator's** | the agent, the SSE path and the store were never broken. **의견 is a genuinely separate cause and it cannot be closed by code**: `NEXT_PUBLIC_VOCKY_SRC` is unset because vocky ships no embeddable widget script (already recorded at `P5.S19` #17). Refusing to invent a URL is correct — see decision #1 |
| 9 portfolio | **closed on the record; one symptom routed** | five measured layout slips fixed against the record, the flip proven in both modes. The 144.7px ragged edge is a geometry R5 never states — decision #8, and the operator will still see it |
| 10 copy | **closed** | two strings trimmed, mechanism stripped and promise kept verbatim; measured with a revert-and-re-measure control, so the zeros are a measurement |
| 11 widget | **closed** | RC-A artifact; launcher and widget live |

**On the defaults nobody confirmed** (Q2 focus, Q3 = 30, Q4 the row stays, S8's Q-A…Q-E, Q9–Q13):
each is defensible under RESPECT THE DESIGN — every one either implements the record literally
(Q4, Q-D, Q-E) or fills a gap the record leaves silent using the record's own idiom (Q3), and each is
routed to the operator rather than buried. That is a `pass` by the plan's own test.

## 3. RESPECT THE DESIGN

- **`docs/reference/design/` is untouched** — `git diff ccbed5a..HEAD --stat -- docs/reference` is
  empty. No round was edited, no nit was written back into the record.
- **Four overrides, all authorised by `intent.md`, all scoped**: the nav slot (nothing re-centred or
  re-spaced), the focus treatment (ring intact on all 13 other tab stops — verified by a real Tab
  walk), the board window (counts, order and corpus untouched; strips unchanged), the two caption
  trims (promise kept verbatim, account captions untouched).
- **Zero Korean minted.** Checked against the diff, not the reports: the only Hangul added to
  `SearchRow.*`, `Board.*` and the copy files is comments plus `{count(hidden)}건` in the strips' own
  class; the two `copy.ts` string changes are both **trims of existing signed strings**. The two
  unsigned elements (candidate panel, window control) reuse signed idiom — radius 0, hairline, the
  surrounding console field's colours, fade-only motion, 44px at 390.
- **Trust rules intact**, re-measured here: an ambiguous prefix still declines rather than guessing,
  the flipped figure keeps 「추정」 and its exact value, tab counts stay whole-board, and the display
  window drops no row from the corpus.

## 4. Workflow hygiene

`plan.md` + `result.md` present for all ten executed slices; every slice `done`; `REVIEW` in
`in_progress`; **no slice ran `doc-new-version`** (`docs/versions` shows no P7-sourced file before
this review, and the only `docs/index.json` change in the range is a rebuild timestamp); one commit
per slice on `main` in convention, each naming its slice id; `validate` clean. `phase.json` is still
`planned` — that is this repo's normal pattern (P1/P2/P3/P5/P6 all went `planned` → `done` at
`review-phase`), not a P7 defect.

## 5. Doc impact completeness — one finding, closed inside this review

Spot-checking `git diff ccbed5a..HEAD --stat` against the Doc impact list found **four durable changes
with no line**:

1. **`product.md:98` still said "Six surfaces, three of them in the nav. Nav = 내 종목 조회 · 관제
   현황판 · AI 질문"** — false since `P7.S6`. Three slices wrote "product.md was checked and needs
   nothing"; each checked its own topic, and the nav override was checked against `frontend` only.
   (`experience.md:41` carried the same claim and *was* on the list, via the `frontend` line's
   "any current-doc language describing the nav as three links".)
2. **`backend.md` enumerates the read layer by name** (`load_board · … · resolve_corp`, plus P6's
   three additions) and `reads.suggest_corps` was missing from it.
3. **the pytest baseline moved 138 → 139** (`tests/test_web_stocks.py`, +37 lines) while `qa.md`
   states 138 three times and `architecture.md` states "138 tests".
4. **P7 named three decisions (D-P7-1…3), six record readings and a 13-item operator catalogue**, and
   `decisions.md` — the doc whose whole job is exactly that, and which already carries "P5 stated
   defaults — landed, and still the operator's to confirm" — had no line.

**Disposition: recorded as a finding, closed by this review rather than by a fix slice.** Docs are the
review's to write, no source change is implied by any of the four, and a `changes_requested` would
have handed an executor nothing to do. All four are covered by the versions below. The rule worth
carrying: *"product.md needs nothing" is a per-topic answer, and a phase-wide claim needs the review to
re-check it* — this one slipped past three separate slices.

## 6. Doc versions created (nine — the phase is not in parallel mode)

| doc | version | what it consolidates |
|---|---|---|
| `frontend` | **v0005** | the dev-origin seam + **the browser-check rule inverted** (127.0.0.1/tailnet, never localhost) with the matcher's host-only wildcard limits and the config-vs-env reload asymmetry; the StrictMode module-store trap; the two-slot nav; the 30-row window; the shared `SearchRow` combobox + the candidate panel; the `.orbits` clip; the two trimmed captions; the portfolio layout primitives + the shared-track grid trap; the focus split (§Accessibility); the three CDP probe traps; the two production-only Next behaviours; the verification floor; the build-in-a-copy recipe. Two Open Questions re-worded (the footer's 내 종목 연결 line; vocky's triggers now measured as the product's only inert controls) |
| `api` | **v0004** | `GET /stocks/suggest` — shape, cap of 8, empty-list-not-404, `q` as its only parameter, `suggest_corps`' union-of-tiers matching, the declaration-order rule, and the restated miss rule |
| `experience` | **v0006** | two-slot nav; the 30-at-a-time board; candidates while typing; the miss rule **split** from the typing rule; the 조회 caption's narrower stated promise; the 챙긴 돈 flip as measured behaviour |
| `operations` | **v0007** | `MIJUAL_DEV_ORIGINS` in the Environment Variables table, and a Local Development note on `make stack-up/status/down` — the doc described no dev stack at all, and the variable is unusable without it (the plan left this call to the review) |
| `qa` | **v0006** | suite **139**; trap #1 **inverted** (with the mechanism left in `frontend`, not duplicated); the verification floor as items 8–11 of the method (both runtimes × operator origins, five widths, the functional dimension, controls for zeros); the SSE contract captured from a browser on the production build; the regression checklist number |
| `product` | **v0007** | nav 3 → 2 (the false sentence); a "What P7 changed" section: the one-bug headline, the display window, and the suggest-without-guessing rule |
| `architecture` | **v0006** | suite **139**; `mijual.web` gains one read-only route |
| `backend` | **v0005** | `reads.suggest_corps` beside `resolve_corp`/`find_corps`, with the prefix invariant and the route-order rule |
| `decisions` | **v0008** | **D-24** (30-row window, a stated default awaiting confirmation), **D-25** (`.orbits` clip), **D-26** (focus split); the six design-collision readings; and **the 13-item operator catalogue** as a durable table — the whole reason this phase exists is that a comparable catalogue was lost in a review record |

`security.md` and `data.md` were checked and need nothing: the storage mechanisms are unchanged
(P7 changed only what the surface *says*), and no table moved.

---

## 7. DECISIONS FOR THE OPERATOR

Thirteen calls, none blocking, each live today with the default named. **Hand this list to the
operator; it is also now durable in `docs/current/decisions.md` §"P7 open operator calls".**

1. **의견 (vocky) has nothing to bind to — this is the one part of item 8 that is still open.**
   `NEXT_PUBLIC_VOCKY_SRC` is unset because vocky ships no embeddable widget script; the three signed
   `[의견]` triggers are, measured across seven surfaces in both runtimes, **the only genuinely inert
   controls in the whole product**. *You must either supply a script URL / capture path, or decide
   의견 routes elsewhere — the AI 질문 agent already has a 의견 tool that saves feedback.* No slice
   may invent a URL.
2. **How far does "no selected focus on all the input boxes" go?** Live: the blue ring is off every
   text field (it was R1's ① hue and it painted under the 조회 button); the field brightens its own
   hairline instead, and every button/link/tab/chip/checkbox keeps the 2px ring. If you meant *zero*
   indication anywhere, that removes the record's a11y floor and needs your explicit word.
3. **How many firms is "some amount"?** Live: **30**, +30 per 펼치기 click, 12 clicks to all 386.
   A different number is a one-constant edit (`WINDOW_STEP`).
4. **Should a 챙겼습니다 row disappear from 지나간 마감?** Live: R5-8 implemented literally — label
   놓친 돈 → 챙긴 돈, hue alert → live, **same figure**, no layout shift. Removing the row supersedes
   a signed round.
5. **Do you want live *data* refresh?** Live: countdowns tick and nothing stomps typing, but board
   data is only as fresh as the last page load (the freshness chip states 기준시각 honestly and the
   board is never dimmed). Polling is behaviour no round specifies — a deferred job if wanted.
6. **Five P5 catalogue items P7 brushed but does not own:** the footer's locked 내 종목 연결 line and
   the hero H1's 내 종목 조회 (**both more visible now the nav slot is gone**); the sample's signed
   「4건」 subline above five live D-day rows; `[근거]` + DART link under the mobile 44px floor; the
   English 404 sentence.
7. **Four reader-visible strings speak developer vocabulary but are promises**, so the sweep kept
   them: `API_TIER_KO`, `SPARSE_CLOSING_KO` (both explain *why a fact carries no verbatim quote*),
   `GATE_COST_TAIL_KO` (the product's one disclosure of a deliberately excluded number) and
   `carryOverKo` (세션 is the only word conveying impermanence). Re-saying any of them is a copy
   decision. Sub-question: the sample caption is now 「본인 표시」 — should the **account** caption
   drop 「· 계정에 저장」 too?
8. **The one remaining "not organized" symptom on 내 포트폴리오.** The D-day rows' right-hand block
   has a **144.7px ragged left edge** at 1440 (232.6–409.3px at 768) with 584.6–761.3px of empty
   middle, because `.rowHead` is `justify-content: space-between`. R2's board pins a fixed grid
   (`86px 1fr 300px 230px 96px`) for exactly this reason; R5 states this row's *parts* and no
   geometry, so adopting a column grid here is a decision no round made. **Adopting the board's grid
   is probably what "organized" means at desktop width** — your call.
9. **Four smaller record-silent portfolio items:** 지나간 마감 states no 「기준 … (KST)」 line (the
   counting-down section does); 한화솔루션 and 세기상사 render an **empty 진행 중인 권리 cell**; a
   챙긴 돈 row still links 「놓친 돈 상세 →」; the 「본인 표시」 caption renders whether or not the box
   is checked (making it conditional costs a 22.6px click-time shift).
10. **Five interactive controls have no hover state and the record is silent** — the four board tabs,
    the 조회 submit, the 로그인 submit, the ask send button and the 샘플 chip, while 회사명 / `↗` /
    펼치기 on the *same panel* do. The record specifies hover in exactly two places and R2 §Tabs draws
    the tabs with none. Affordance polish, not a defect.
11. **The focused input's hairline is brighter than the open candidate panel's side edges** (same hue,
    different alpha). One line in `SearchRow.module.css` if you want them matched.
12. **Two components draw the "mobile" boundary at different widths** — at 481 a candidate row is
    44px beside a 32px 펼치기. Both clear the 44px floor wherever R5 §Mobile applies.
13. **Two environment leftovers:** Chrome's own empty-form validation bubble is **English**
    (「Please fill out this field.」 on `/auth/login`) — UA chrome, and suppressing it means owning the
    validation copy; and **`s19-fidelity@example.com`** (account id 14, one live session) is still in
    the dev database from P5.S19.

---

## 8. FIVE-MINUTE OPERATOR WALKTHROUGH

The dev stack is already up. **Open `http://127.0.0.1:3000` — that exact URL, not `localhost`** (the
whole phase is about that difference), or the Tailscale URL `make stack-status` prints.

1. **`/` — the nav (item 1).** Top bar: **관제 현황판 · AI 질문**, and 내 종목 조회 is gone. Narrow the
   window under 480px and open 메뉴: the same two rows.
2. **`/` — the hero search (item 2).** Type `계양` slowly. A candidate panel opens under the box:
   **계양전기 012200**. Press **↓** then **Enter** → you land on the company page. Go back, type
   `에스` and press **Enter without choosing** → the old behaviour is intact: 「‘에스’와 일치하는
   종목이 없습니다」. The product still never guesses for you; it only lets you pick.
3. **`/` — the focus box (item 3).** Click into the search box: no blue rectangle, and nothing paints
   under 조회 — the box's own hairline brightens instead. Press **Tab** a few times from the top of the
   page: the wordmark, both nav links, 로그인 and `[의견]` all still show the blue keyboard ring. That
   is the split — mouse-click box gone, keyboard indicator kept.
4. **`/` — the board (item 4).** Scroll to the list: **30 firms**, then 「**356건 펼치기**」. Click it
   → 60. Click the two grey strips' 펼치기 (전환청구 진행 중 60건 / 일정 추후결정 4건) → they open
   too. The tab numbers (488 / 50 / 422 / 16) never move: it is a display window, not a filter.
5. **`/` — the countdown and typing (items 6, 7).** Watch a D-day countdown for ten seconds: it
   **ticks**. Type something into the search box and leave the tab alone for a minute or two: it is
   **still there**, and the page never reloads itself.
6. **The 로그인 link, top-right (item 5).** Click it → `/auth/login` with 이메일 / 비밀번호 /
   계정 만들기 / 비밀번호 재설정. If you want the full round trip, make a throwaway account and then
   delete it from 알림 설정 → 계정 삭제 (it works end to end; two slices verified exactly that).
   *If you see a 「샘플」 chip instead of 로그인, you are in sample mode — press 샘플 종료 first.*
7. **The corner launcher (items 8, 11).** Bottom-right on desktop: click it → the 440×620 AI 질문
   widget. Ask 「계양전기 유상증자 일정 알려줘」 — the answer streams in a few seconds with DART 원문
   citations and a 근거 footer. (On a phone-width window there is no launcher: `/ask` is the whole
   surface, by the signed rule.)
   **`[의견]` in the nav still does nothing** — that is decision #1, and it needs you, not code.
8. **`/portfolio?sample=1` (items 9, 10).** Scroll to **2026년 놓친 돈** and tick 「청약·매도로
   챙겼습니다」 on the 한화솔루션 row: the label flips 놓친 돈 → **챙긴 돈** and the colour goes from
   red to green, with the **same 679,575원 「추정」** and no jump. The caption under it now reads just
   「본인 표시」 — the old 「· 이 브라우저(localStorage)에」 is gone, here and everywhere.
9. **`/stocks/00102618` (item 10, the promise half).** Type 500 into 보유 주식 수. The caption reads
   「**서버 전송 없음**」 — the promise kept, the mechanism words dropped.
10. **What to look at with decision #8 in mind:** back on `/portfolio?sample=1`, look at the right-hand
    side of the D-day rows at full width. Their money blocks do not line up in a column. That is the
    one "not organized" thing P7 deliberately did **not** invent a fix for.

---

## 9. Deviations from `plan.md`

1. **Nine doc versions, not the five the plan expected** — the extra four (`product`, `architecture`,
   `backend`, `decisions`) close the Doc impact gap found in §5. `product` in particular was declared
   "needs nothing" by three slices and carried a sentence P7 made false.
2. **The verification floor went into `frontend`, the floor's *rule* into `qa`** (the plan asked the
   review to decide who owns it): `frontend` §Engineering traps already held the stale origin note and
   the probe traps, so the mechanism lives there and `qa` states the completion criteria and points at
   it — no sentence is duplicated. Both docs' wrong `localhost` rule is struck/inverted.
3. **`operations` did get the dev-stack note** (the plan left it optional): `MIJUAL_DEV_ORIGINS` is
   filled by `make web-up`, so documenting the variable without the Makefile would have been useless.
4. **The spot-check ran a real Tab walk for the ring keepers** after a programmatic `.focus()` read
   `outline: none` on a *button* — the `:focus-visible` trap `P7.S8` recorded. Worth re-recording: the
   review nearly manufactured a false finding with it.
5. **One live agent turn** (the plan's cap): ▷ **$0.0115 estimated**, 14,319 tokens, never billed.
6. **No account was created**, so none had to be deleted; `s19-fidelity@example.com` was left in place.

`explain`: **not written — run `/explain` for this phase.** No commit, no `review-phase`, no state
transition: the orchestrator records the verdict.
