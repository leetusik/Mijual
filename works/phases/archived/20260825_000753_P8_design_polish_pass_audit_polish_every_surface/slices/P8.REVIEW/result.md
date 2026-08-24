# P8.REVIEW result — gated phase review of the design polish pass

**Verdict: `pass`.** Every slice validated together, the phase's headline claims re-checked by this
review **in the operator's own runtime** (not on other slices' reports), the whole cumulative
`## Regression Checklist` re-run and extended, all `## Operator Questions` routed, and nine doc
versions cut. The acceptance gate (`acceptance.required: true`) is **open for the orchestrator** —
this executor never runs `accept-gate`.

Surface 8 (운영 관제 `/ops`, R15) was **cancelled by operator decision** on 2026-08-24 and parked as
**D6**. That is recorded operator intent and is **not** treated as a review finding anywhere below.

---

## Stage 1 — validation, all slices together

| command | outcome |
|---|---|
| `.venv/bin/python -m pytest -q` | **142 passed**, 0 failed (~3.5 s, one known Starlette/httpx deprecation warning) — the 139 → 142 the phase's Doc impact predicted |
| `cd frontend && npm run typecheck` | clean (`tsc --noEmit`) |
| `cd frontend && npm run smoke` | **16/16** `node:test` cases in 167 ms, incl. `a turn minted after a restored thread never reuses a stored id` (P8.S1) |
| `npm run build` in a scratch copy (`…/scratchpad/prod2`, `node_modules` via `cp -Rc`) | green, **16 routes**; repo's `frontend/next-env.d.ts` untouched (`git status frontend/` clean) |
| `python3 scripts/workflow.py validate` | `Workflow validation passed.` (before and after consolidation) |
| `.venv/bin/python -m mijual.gates run` ×2 | **byte-identical**; 710 field rows, split `passed 618 / tbd 4 / failed 10 / n_a 78`; 488 exposable events |
| `.venv/bin/python -m mijual.estimate report` ×2 | **byte-identical**; headline ▷ **718.1억원** (71,812,971,649원), band floor 548.7억원 |
| `.venv/bin/python -m mijual.scheduler once --offline` | **six** stages green, **0 requests / 0 calls / ▷ $0.0000** |
| `.venv/bin/python -m mijual.extract recheck` ×2 | identical, `rewritten: 0 record(s)` — second run writes nothing |
| `.venv/bin/python -m mijual.evalset refresh-recall` ×2 | identical, 재현율 88.70 %, `sample: unchanged — nothing written` |
| guard test files (`test_web_smoke`, `test_web_vocky`, `test_agent_tools`, `test_present`, `test_db_models`, `test_web_ops`) | **43 passed** — the four AST import scans, the anonymity scan, the tool-signature check and the ops safe-method check all still guard |
| exposure invariant, re-derived read-only | renderable fields outside `passed`/`tbd` **0** · `tbd` fields carrying a value **0** · exposable events in a non-exposable state **0** · 488 exposable |
| secret grep over tracked files (vocky / DART / Gemini keys) | **0 occurrences** each |
| `vk_` / `vocky` grep over the production `.next/static` | **0 files** |
| agent's own two numbers (a live pass *was* run — 3 real turns) | stored 인용 원문 byte-identical to a served payload value **4/4**; numerals in stored answers present in that turn's payloads **10/10** — 100 % / 0 misses, matching the P6 pass |

One note for the record: running the checklist's own `scheduler once --offline` refreshed the
corpus `as_of` (2026-08-23 21:38 → 2026-08-24 23:32), which cleared the landing's 「25시간 전
데이터 · 데이터가 갱신되지 않고 있습니다」 stale banner I had observed at the start of this review.
Same corpus, same numbers; the staleness notice was the product correctly reporting an 18h+ gap.

---

## Stage 2 — the gate stages (`acceptance.required: true`)

### The runtime, and how this review drove it

`## Operator Runtime` in `docs/current/operations.md` is present and filled. Everything below was
driven in **that** runtime: `make stack-up` (Postgres + API on `127.0.0.1:8000` + `next dev` on
`0.0.0.0:3000`), browsed at **`http://127.0.0.1:3000`** and the tailnet **`http://100.77.164.42:3000`**,
**plus a production build** (`npm run build && npm run start`) served on `:3100` from the scratch
copy. The browser is the operator's own Chrome **151.0.7922.174** driven headless over CDP from an
**isolated profile** in the scratchpad — the operator's own profile and session were never touched.
Widths: **1512 / 1456 / 1440 / 1280 / 1119 / 1024 / 900 / 768 / 767 / 600 / 390**.

Account states cost **one temporary account**, `p8review-temp@example.com`, created through the
product's own 계정 만들기 and removed through its own 계정 삭제. `account` / `auth_session` /
`holding` / `lapse_claim` / `notification_pref` were counted before and after and are at their exact
pre-review values **2 / 3 / 1 / 0 / 0** (`s19-fidelity@example.com` + the operator's own, as P7 Q13
left them). The `/ops` authenticated tabs take separate operator credentials this executor does not
hold and **did not attempt** — only the door's SSR was verified; the tabs are in the walkthrough.

### Stage 2.1 — the phase's headline claims, spot-checked by this review

**R8 — chrome / foundations.** nav is exactly two links (`AI 질문|/ask` · `보유 종목|/portfolio`);
`[의견]` chip absent; 샘플 chip absent; **0** `data-vocky-trigger` in the DOM; 52px bar; footer is
**one row with no mono**; at 390 the ≤480 menu is an **overlay + backdrop** — `main` top is **52 →
52** (0px push), rows 48px, body scroll `hidden` while open, released on Esc (measured: still open at
+300 ms, closed by +1500 ms — the sheet has a closing transition) and on the × ; 의견 보내기 dialog:
empty input ⇒ 보내기 `disabled`, one keystroke ⇒ enabled, **no contact field**, textarea `outline:
none` (the P7 field-focus split kept, Q7). Account slot signed in = full email + identicon + ▾, and
its menu is **three rows** — 알림 설정 · 의견 보내기 · 로그아웃 (P8.S5.5).

**R9 — landing / board.** 15 rows + 「15건 더 보기」 + 「남은 371건」; one click ⇒ **30** + 「처음
15건으로 접기」; a tab switch **resets to 15** with `aria-pressed` moving and the meta line following
(「카운트다운 362건 중 15건」). The D-day rail's right edge is **one value per width across all 15
rows**: 1267 / 1231 / 1070 / 719 / 734 / 357 at 1512 / 1440 / 1119 / 768 / 767 / 390, `overflowX 0`
everywhere. Row is a single click target (stretched-link `::after` on the corp anchor) with the
「↗」 DART link above it. Countdown card = three stats; 「읽은 실적보고서」 **absent from the DOM**.
소멸주의보 says 「가장 빠른 청약 마감 2026-09-04, **3개 종목**」 and `/board/summary`'s
`next_lapse.tie_count` is **3** — they agree. Strip 펼치기 `aria-expanded=false` ⇄ 접기 `true`.
**Auto-refresh watched over three intervals**: `/api/board` at 57 s, 76 s, 136 s, 180 s; row count,
first-row `top` and the 기준시각 line unchanged throughout, **no** 갱신됨 chip and no layout move —
which is the signed contract when the served `as_of` has not moved. (The chip + `--live` edge branch
needs a *changed* `as_of` and is therefore in the walkthrough, not claimable from this session.)

**R10 — event detail.** Six pages driven (① open 계양전기 · ① 추후결정 경남제약 · ② upcoming 라온텍 ·
② **past-open** 트리니티항공 · ③ open 휴맥스 · ③ 부재 아시아나). **One** `CraftPanel` root per page.
「종료」 appears on **none** of them. ② past-open renders 「진행 중」 — and note that this state is
**live in the corpus today** (60 `open` R2 events), so P8.S7's scratch-proxy verification is now
confirmable through the product itself. 아시아나 shows exactly **two** dashed 「현재 버전 공시에 없음」
chips (countdown slot + field row) and no placeholder for any other field. Citation: trigger **32px
desktop / 44px at 390**; opening it leaves the eight rows behind it at **identical `top` values**
(326/510/543/555/555/587/599/599 before and after); the panel is `position: absolute` on opaque
`rgb(14,26,21)`; Esc closes it (`aria-expanded` → false) **with focus returned to the trigger**; at
390 the panel measures left 22 → right 283 inside a 390 viewport (**fully in view**). The ② page
closes its fact frame with one mono `DART 공시 API {rcept} ↗` line and carries **no** `[근거]` in the
strip. Eyebrow `h2`s carry their own `aria-label` (일정 · 발행 조건 · 2단계 절차). **0** interactive
targets under 44px at 390 on any of the six pages; `overflowX 0`. 404: `/events/99999999999999` and
`/zzz-none` both **status 404** with the Korean not-found, the path echoed, **no reason**, in dev and
in the production build. Single 767 line: `DART 원문` is a 71×32 inline link at 768 and a **701×44**
full-width button at 767.

**R11 — 조회 / 놓친 돈.** `h1` is the 종목명 on all five stocks, with 종목코드/고유번호 under it and
the search box echoing the name; 「내 종목 조회」 appears **exactly once** per page. 보유량 strip
present on 한화솔루션 and 계양전기 (live ① / 놓친 돈 row), **absent** on 풍전약품 (②-only) and
세기상사 (no rights) — with no disabled control and no sentence. 풍전약품's three ② rows render as
**one table** closed by one 「DART 공시 API — 전환가액 · 전환 시 주식수 · 오버행 | 3건」 line.
아시아나's ③ shows the 2단계 절차 block with two dashed chips. 한화솔루션 (1건) prints **679,575원**
once in the row with **no total above it**, and its own 「배정 123주 × 5,525원 추정」 line —
123 × 5,525 = 679,575 exactly, and 42,165,422 − 38,430,497 = 3,734,925 (8.86 %) reproduces the served
`lapse` row. 「상세 보기 →」 is the only link out of a row. 계양전기 (발행가 확정 전) prints **no 원
amount** while still converting share counts. `/stocks` with no query = 감시 대상 3종 + 감시 중 488건
+ 집계 범위. 검색 불일치 particle: 「‘삼성’**과** …」 (Hangul) vs 「‘ABC’**와/과** …」 (non-Hangul).
**Production widths hold**: `/stocks/{corp}` **960px** and `/stocks` **620px** in the production
build as well as in `next dev` — the doubled-specificity fix doing its job.

**R12 — 인증.** Rail 「← 관제 현황판」 on both pages. `form.noValidate === true`, and **no**
`required` / `pattern` on any input (`type`/`autoComplete` kept). Empty submit ⇒
「이메일과 비밀번호를 입력해 주세요.」 and **0 requests** to `/api/auth`; malformed address ⇒
「이메일 주소 형식이 올바르지 않습니다.」 and **0 requests**. 재설정 with an empty address is
**clickable**, focuses the email input (`document.activeElement` = `INPUT:email`) and sends nothing.
Primary is **100 % × 48px** at 1456 / 768 / 767 / 390 with **0** sub-44px controls and `overflowX 0`.
Reset page: **one** password field with 「8자 이상」, no 이메일 field, no sample entry; an expired
token renders 「이 재설정 링크는 만료되었거나 이미 사용되었습니다 — 새 링크를 요청해 주세요.」 plus a
quiet 「로그인」. PII inset **absent**. `Auth.module.css` has exactly **one** media query. Logout ⇒
`/auth/login` with 「로그아웃되었습니다」 **above** the `h1` (top 169 vs 226), still present after
**11 s** (no timer), gone on the **first keystroke**. Login lands `/portfolio`.

**R13 — 보유 종목 / 알림 설정.** At 1440 all five D-day rows share one edge set — chip **285–369**,
종목 **385–703**, 라벨 **719–931**, countdown right **1155** — and the 소멸 금액's right edge is
**1155** too. The anchor 「기준 2026-08-24 (KST)」 renders **exactly once**, outside both sections.
Empty 진행 중인 권리 cells are dashed hairlines with `aria-hidden="true"` and no text. **챙겼습니다
moves 0px**: the 29 row `top` values are byte-identical before, after checking, and after unchecking
(510.33 … 1168.23 all three times), the 「놓친 돈 상세 →」 link leaves the money line on check and
**returns** on uncheck. 「포트폴리오」 **0건** on `/portfolio` and `/portfolio/notifications`. The
sample carries the R12 band after 지나간 마감 with body + CTA + 닫기 and **no lead line**; there is
**no** reset/종료 control. Caption is 「본인 표시」 on the sample and 「본인 표시 · 계정에 저장」 signed
in. 알림 설정: one `h1` 「마감 임박 이메일」, rail 「← 보유 종목」, chips on `aria-pressed`, KakaoTalk
with no control, and 로그아웃 / 계정 삭제 / 취소 all **104px** wide. 계정 삭제 sentence: absent →
**armed** → present → 취소 → absent. `Portfolio.module.css` has exactly **one** media query.

**R14 — AI 질문.** The 767 line is an **existence** line: launcher and widget absent from the DOM at
767 / 600 / 390 and present at 768 / 1024 / 1440, in dev **and** in the production build. `/ask`
desktop bundle measures **1072** = rail **340** + chat **708**, centred, rail sticky (Q57's numbers,
not the record's 1124/760). Composer idle = **ghost disabled** (`background rgba(0,0,0,0)`, border
`rgba(163,196,180,.15)`, colour `rgb(109,131,120)`, `opacity 1`) reading **「보내기」**; typed = solid
`rgb(15,107,80)`; streaming = **중지**. Preset chips carry `title` = `aria-label` = the **signed
sentence** while the label is the served field name (e.g. 「신주인수권증서 상장·매매기간」 →
「신주인수권증서는 언제부터 언제까지 매매할 수 있나요?」). **Three real agent turns** were run through
the live model: the answer renders as **one `<p>`** with 4 `.sentence` spans, **0 `<br>`**,
`white-space: normal`; the footer says 「근거 2건 · 20260724000546 · 2026-08-24 23:28 KST」 against
distinct chip numbers `[1, 2]` — the chip count, not the filing count; a chip opens quote + DART link
and **no API-tier sentence exists anywhere**; tool rows are `white-space: nowrap` with
`overflow-x: auto` and at 390 each is one line whose `scrollWidth` (336) exceeds its `clientWidth`
(330), i.e. it scrolls rather than breaking a 접수번호. `overflowX 0` at 390.

**P8.S1 — the `t1` bug, re-verified end to end.** Asked → reloaded → asked again: stored ids
`["ta24a0458-1", "tdc7915f7-1"]`, **unique**, two turns rendered, **0** duplicate-key warnings in the
console. The session tag changes per page load exactly as designed.

**Cross-runtime.** Tailnet (`100.77.164.42:3000`): `isSecureContext false`, `crypto.randomUUID
undefined`, `getRandomValues function` — and the ask store still works there (`mijual.ask.thread`
present, composer in its ghost state), which is the whole point of not reaching for `randomUUID`.
All the geometry above (board 15 rows / 1231 edge, 960/620 widths, 432 auth column, 1072 ask bundle,
1155 portfolio edge) is **identical on 127.0.0.1, the tailnet and the production build**. Console
noise across every page and origin is the pre-existing **`GET /favicon.ico` 404** (deferred **D5**)
and nothing else — 0 app errors, 0 React warnings. The production build has **no** `nextjs-portal`;
the 36×36 ⓝ at ≤767 in dev is Next's dev-tools badge (Q56), confirmed absent in production.

### Stage 2.2 — fresh-eyes walk (first-time user, *not* judged against the design record)

These are **walkthrough items for the operator to decide on**, not defects and not silent fixes.

1. **The countdown has no words.** The anchor card's headline is a big red `11일 00:20:41` with no
   label above it and no caption under it — at 1440 and at 390. A first-time user cannot tell what it
   counts down to. (This is exactly Q14, still open.)
2. **The landing's `h1` is 「내 종목 조회」**, which is the *lookup* surface's name, while the thing
   below it is the 관제 현황판. The nav has no 관제 현황판 slot either (it is the ring wordmark), so
   nothing on the screen names the page you are on. Signed R2.1 behaviour ("this IS the 내 종목 조회
   surface"), reported here only because it reads oddly cold.
3. **Three different words for "past" across three surfaces**: 상세 says 「기한 지남」, 조회 and
   보유 종목 say 「기간 지남」, and a ③ row says 「통지 마감 지남」. Each is its own round's signed
   string; a reader crossing surfaces meets three.
4. **`// 다가오는 마감` renders its slashes as literal text** on 보유 종목 (they are `::before` on
   조회). Cosmetically identical, but it is the surface that leaks them into the accessible name —
   the substance of Q21.
5. **The 배정비율 prints to ten decimals** (`0.2314082845`) on the detail page and in 조회. Answered
   at R10 (Q16 = keep the full value), noted here because it is the loudest number on the page.
6. **The ① 환산 chain's right half is empty** on the detail page: 「내 보유량으로 환산 →」 sits alone
   in a wide cell with a large blank to its left.
7. **The `/ops` door prints four internal implementation rules as visible page text** — 「reader
   chrome 어디에서도 링크 금지 (nav·푸터·계정 메뉴·sitemap)」, 「자격은 배포 환경에서 발급·회전
   (환경변수/시크릿) — 가입·재설정 UI 없음」, 「실패 응답 균일 + 상수 시간; 어느 필드가 틀렸는지 구분
   금지」, 「세션 만료 → 문으로 복귀, 로그인 후 있던 탭 복원」 — 11px `--ink-3`, `visibility: visible`,
   **in the production build**, below the login button. These are R7 design-record rules leaking onto
   the login screen of the admin console, and two of them describe the security posture. Pre-existing
   (R7 + P5/P7 state), **not** introduced by P8, and `/ops` is exactly the surface the operator
   cancelled — so it is reported, never touched. Deferred job proposed below.
8. **The 세기상사 row at the bottom of 지나간 마감** shows a lone sentence (「1단계에서 반대의사를
   통지한 주주만 행사 가능」) with no money and no action — honest, but it reads as an unfinished row
   after two money rows above it.

### Stage 2.3 — the cumulative `## Regression Checklist`

Re-run **whole**, not only this phase's lines: all 14 pre-existing boxes were exercised this cycle
(the evidence is the Stage 1 table plus the surface checks above), and the phase's headline checks
were appended in the qa doc version — the checklist now carries **72** boxes. Two counts were
corrected there: `pytest` **139 → 142** and `npm run smoke` **15/15 → 16/16**.

One box is **operator-only and is marked so in the walkthrough rather than skipped silently**: the
`/ops` six tabs (density, `OpsClock` liveness, gate queue + `RowInspect`, accuracy, 대화 로그 filter,
사용자, 의견) need the operator's own credentials, which this executor may not hold or type.

### Stage 2.4 — routing of `## Operator Questions`

**Q1–Q65 are all routed.** Already closed in-phase and verified as marked: Q2, Q3, Q4, Q5, Q12 (built
as `P8.S5.5`), Q15–Q18, Q23–Q28, Q35–Q38, Q41–Q45, Q50–Q55; Q59–Q65 carry their 「Routed to deferred
job **D6**」 marking and D6 exists in the open dashboard. Q1 is closed by the phase's own practice —
every round handed the operator its inherited P7 items together with that surface's walk findings.

The rest are routed by this review, and each is marked in `phase.md`:

- **Into the acceptance walkthrough** (the operator decides while walking): **Q6** · **Q7** · **Q8** ·
  **Q9** · **Q10** · **Q11** · **Q14** · **Q19** · **Q20** · **Q22** · **Q33** · **Q34(a)** ·
  **Q39** · **Q40** · **Q46** · **Q47** · **Q48** · **Q56** · **Q57** · **Q58**.
- **Listed for the orchestrator to file with `defer-job`** (structural follow-ups that need a slice,
  not a look): **Q13** · **Q21** · **Q29(b)** · **Q30(b)** · **Q31(b)** · **Q32(b)** · **Q34(b)** ·
  **Q49**, plus two this review raises — the `/ops` door's leaked rules (fresh-eyes 7) and the
  `copy-inventory.md` exporter tail. Full title/reason/trigger for each is in the returned verdict;
  this executor does not run `defer-job`.

Two entries moved on their own and are noted rather than re-asked: **Q22**'s first half is now
*reachable* — ② past-open 「진행 중」 renders from live corpus data today (60 `open` R2 events), so
only the multi-part-citation half (0/386) is still unseeable; and **Q29**'s missing
`subscription_agents` is served on the **event** route (the 청약 취급처 table renders in full on
`/events/20260724000546`) while remaining absent on the stock route — the gap is the route, not the
corpus.

---

## Stage 3 — consolidation (pass path only; this phase is not parallel-mode)

Nine doc versions cut from the phase's `## Doc impact` list, grouped by doc, each
`--source P8.REVIEW`, then `rebuild-docs` + `validate`:

| doc | version |
|---|---|
| `qa` | `v0007_p8_design_polish_pass_the_suite_at_142_smoke_16-16_…` |
| `frontend` | `v0006_p8_design_polish_pass_r8-r14_supersede_every_reader_surface_…` |
| `api` | `v0005_p8_design_polish_pass_post_feedback_write-only_outward_and_next_lapse.tie_count_…` |
| `architecture` | `v0007_p8_design_polish_pass_mijual.web_s_outbound_row_is_one_vocky_read_plus_one_vocky_capture_…` |
| `security` | `v0005_p8_design_polish_pass_the_vocky_key_boundary_now_covers_a_capture_path_…` |
| `operations` | `v0009_p8_design_polish_pass_the_vocky_env_row_serves_a_reader-facing_send_…` |
| `data` | `v0006_p8_design_polish_pass_the_vocky_env_row_covers_read_and_capture_…` |
| `experience` | `v0007_p8_design_polish_pass_every_reader_surface_re-cut_from_the_two-slot_chrome_to_the_composer` |
| `product` | `v0008_p8_design_polish_pass_the_layer_is_not_the_board_is_15_rows_and_keeps_itself_current_…` |

`docs/reference/design/grounding/copy-inventory.md` is a **hand-registered grounding file, not a
versioned doc**, and was left alone per the plan. `backend` and `decisions` are unchanged — the
phase's Doc impact list names neither, and P8 touched no derivation-layer contract.

`docs/current/*.md` was regenerated by `rebuild-docs`, never hand-edited, and the operations doc's
`## Operator Runtime` manifest survived the new version intact.

---

## Deviations from `plan.md`

None of substance. Two mechanical notes:

- The plan's Stage 1 says "build in a scratch copy (never rewrite the repo's `next-env.d.ts`)". The
  first attempt symlinked `node_modules` and Turbopack refused it (module-not-found flood, as
  `P8.S7`'s note warned); the copy was redone with `cp -Rc` and built green. The repo's
  `next-env.d.ts` is untouched.
- The `frontend` and `experience` doc summaries were shortened on the second attempt: the first
  wording produced a filename longer than the filesystem allows (`OSError: [Errno 63]`). No version
  was left half-created — the failures happened before any file was written.

## Housekeeping

The dev stack was left exactly as found (`make stack-status` still reports the same api/web pids).
The scratch production server on `:3100`, the isolated Chrome profile, the CDP driver and the
screenshots live only in the session scratchpad. Three real agent turns were run through the live
model (rows 73–75 in `conversation_turn`, anonymous by construction); no feedback row was sent to
vocky, so the operator's project still holds only `P8.S3`'s three clearly-marked test rows (Q9).
