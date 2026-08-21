# Result — P5.DECOMP

Decomposed P5 "Apply — build the signed design" into **19 middle slices**, all bare folders, all
`risk: high`. Single pass — no `DECOMP2`, no `co-work` slice, as the plan specified for the *apply*
half of the P3 design/apply split. Nothing was implemented; no state transition, no commit.

## What I read before cutting

`intent.md` + `phase.md` (P5) · `docs/reference/design/README.md` + `SIGNOFF.md` + all seven
`rounds/*/output/build-prompt.md` + `grounding/README.md` + `headline-numbers.md` + `ui-traps.md`
(headings) + `fonts.css` · `docs/current/{api,architecture,backend,data,frontend,experience,product,
security,decisions,operations,qa}.md` · `works/phases/active/P3/phase.md` (Design Inventory,
Decomposition, Doc impact, Constraints, P3.REVIEW notes) · `works/phases/active/P6/{phase,intent}.md`
and `P4/intent.md` for the boundaries · `works/deferred/open/D{1..4}/deferred.json` · the repo itself
(`pyproject.toml`, `compose.yaml`, `src/mijual/**`, notably `gates/exposure.py`, `calc.py`,
`db/models.py`).

## Slices created

| Slice | Order | Kind / risk | Name |
|---|---|---|---|
| `P5.S1` | 1 | implementation / high | FastAPI service skeleton + read-layer foundations |
| `P5.S2` | 2 | implementation / high | Presentation contract: countdowns, 환산 chain, lapse results, citations, 「추정」 tagging |
| `P5.S3` | 3 | implementation / high | Board, summary and event-detail read endpoints (+ CorrectionStory version rail) |
| `P5.S4` | 4 | implementation / high | 내 종목 조회 endpoints: stock resolution, live rights, 2026 놓친 돈 breakdown |
| `P5.S5` | 5 | implementation / high | **(D1 promoted)** Identity-scope the API-backed gates: re-pair 정정 filings joined to the wrong 사채 |
| `P5.S6` | 6 | implementation / high | ③ 매수예정가 backing (D-15): extraction target, gate, exposure |
| `P5.S7` | 7 | implementation / high | Reader auth backend: accounts, password hashing, sessions, reset flow |
| `P5.S8` | 8 | implementation / high | Portfolio backend: holdings, D-day list, 챙긴 돈, 알림 preferences, sample portfolio |
| `P5.S9` | 9 | implementation / high | Admin backend: operator door + read-only ops endpoints + pipeline run log |
| `P5.S10` | 10 | implementation / high | Next.js foundation: scaffold, tokens/fonts/assets, cosmos shell, trust primitives, API client |
| `P5.S11` | 11 | implementation / high | Global chrome: nav, footer, mobile sheet, vocky triggers |
| `P5.S12` | 12 | implementation / high | Landing 관제 현황판: hero, 회고 anchor panels, countdown, 소멸주의보, board |
| `P5.S13` | 13 | implementation / high | Event detail ①②③: header, 환산 블록, field rows, trust states, CorrectionStory |
| `P5.S14` | 14 | implementation / high | 내 종목 조회 surface: search, 보유량, 진행 중인 권리, 놓친 돈 breakdown, empty states |
| `P5.S15` | 15 | implementation / high | Auth surfaces + conversion offers + sample entry |
| `P5.S16` | 16 | implementation / high | 내 포트폴리오: holdings, D-day list, 챙긴 돈, 알림 설정, sample mode, account menu |
| `P5.S17` | 17 | implementation / high | 운영 관제 admin panel: door + six sections |
| `P5.S18` | 18 | implementation / high | vocky integration: observation API shape decision + admin vocky view |
| `P5.S19` | 19 | implementation / high | Design-fidelity verification in a real browser (RESPECT THE DESIGN) |

`P5.REVIEW` already existed at order 9999. Every new folder holds **only `slice.json`** — no
`plan.md` was pre-filled anywhere.

Advisory `depends_on` chains: S2←S1 · S3←S2 · S4←S2 · S5←S3 · S6←S2 · S7←S1 · S8←S7 · S9←S1 ·
S10←S3 · S11←S10 · S12←S11 · S13←S12 · S14←S4,S12 · S15←S7,S11 · S16←S8,S15 · S17←S9,S10 ·
S18←S11,S17 · S19←S17,S18.

## The four decisions the plan required (full rationale in `phase.md`)

1. **Breakdown and order** — backend first (S1–S9), then the design implementation (S10–S18), then a
   dedicated real-browser fidelity slice (S19). The rationale table and the per-cut reasoning are in
   `phase.md` § *Decomposition*.
2. **Deferred jobs.**
   - **D1 → promoted** into `P5.S5`. Its trigger ("before P3 renders ② event detail pages") fires
     here, and a 정정 filing paired to the wrong 사채 can put the wrong version's numbers on a
     rendered ② page — the one defect class this product cannot ship.
   - **D2 → left deferred**, with a named check. The 9 collided keys carry **blocking flags**, so the
     exposure contract already keeps them off every page. The only product-visible residue is
     `hint_duplicate` — 2 of 488 events share an `rcept_no` (코이즈, 사토시홀딩스; `qa` v0002) —
     which renders two truthful rows, not a wrong number. Recorded as an explicit check for
     `P5.S12`/`P5.S14`/`P5.S19`: a visibly duplicated board row or a double-counted 놓친 돈 total
     means the trigger fired → promote then, and do not paper over it with a display-level `DISTINCT`.
   - **D3 → left deferred.** The signed design removed the need: R4-3 fixed the coverage line at
     2026-01-01 ~ 오늘 with **no 기간 picker**, and outside coverage is *unstated*, never 0. Pre-2026
     ① depth would change no rendered figure.
   - **D4 → left deferred, conditionally.** Its trigger is 실적보고서 figures *with citations*; the
     signed surfaces cite 본문 extraction fields, and R4's 놓친 돈 row carries a single-span
     warrant-period quote, not the summed 발행/청약 numbers. Condition recorded for `P5.S13`/`P5.S14`:
     attaching a `[근거]` chip to a multi-addend 실적보고서 figure (SKC, 에스에너지 — the latter is in
     the 2026 놓친 돈 table) fires the trigger → promote D4 rather than ship a one-addend quote.
3. **Admin 대화 로그 / 익명 세션 → framed now in P5, filled by P6.** R7's six-tab ops chrome is signed
   and "모든 섹션은 ops 크롬을 갖춘 완전한 페이지" — dropping two tabs would break it, and the 사용자
   tab is half P5 data (독자 계정) and half P6 data (익명 세션). `P5.S17` builds all six complete, with
   대화 로그 and the 익명 세션 table reading through a thin storage-agnostic port that P5 implements as
   an empty source. **P5 creates no conversation tables** (P6's intent owns that schema and its
   anonymity promise), so the tabs render an honest **0건** with no invented Korean, and the
   schema-level 계정↔대화 no-join promise is intact by construction.
4. **Risk** — all 19 are `high`. Every one writes real code across more than one file; none is a
   one-line edit or docs, so none belongs on the `mid` tier.

## Additional boundary decisions recorded (not in the plan's list, but forced by the records)

- **Notifications:** R5's 알림 **설정** surface + preference persistence are P5 (S8/S16); the D-day
  alert **channel** (provider, scheduled send, mail body) is P4's own intent item 1. `P5.S7`'s
  password reset therefore sits behind a mailer seam with a dev transport, so P5 carries no deploy
  dependency.
- **The AI 질문 nav slot stays** (signed three-slot nav; RESPECT THE DESIGN), routing to a bare
  P6-owned page shell with no invented copy; the footer's bottom-row 해설 link renders as **AI 질문**
  per R6's supersession.
- **P5's detail pages ship without the R6 preset 질문 스트립** — a phase boundary, not a dropped
  design element. Recorded so `P5.REVIEW` does not read it as a violation.

## Findings worth the orchestrator's attention

1. **The presentation contract does not exist yet.** `offering_inputs`, `lapse_result`, `countdown` /
   `label_ko`, `corp_name_agrees_with_body` appear in the build prompts but **nowhere in
   `src/mijual`** (grepped). They are a derivation layer P5 must build on top of `gates.exposure` +
   `calc` — which is exactly why `P5.S2` exists as its own slice. Full shape list in `phase.md`.
2. **Two pieces of backing work the design implies:** ③ 매수예정가 (D-15, `P5.S6`) and a **pipeline
   run log** — R7's 개요 tab needs a 최근 실행 표 and an alert-ink 「실행 기록 없음」 row, and there is
   no run table in `mijual.db.models` today (`P5.S9`).
3. **`P5.S10` will likely need an operator hand-off.** The wordmark PNGs, the ring logo and
   `PretendardVariable.woff2` live in the Claude Design project, **not in the repo** (`frontend` v0002),
   and `fonts.css` self-hosts Pretendard from `../assets/fonts/`. An executor cannot invent a wordmark;
   expect a `pending` co-work step. Worth warning the operator before `P5.S10` starts.
4. **Six open items need an owner before the slices that consume them run** — the countdown cut-off
   instant (S3), the stale threshold in hours (S3/S12), the "정정 이력" button label (S13), the binary
   assets (S10), the local admin route/credential (S9/S17), and vocky's real API + any credential
   (S18). All are listed in `phase.md` § *Open Questions*.
5. **`api` and `backend` docs are still bootstrap v0001 stubs**, and `architecture` still defers the
   HTTP layer to "P3". P5 makes all three real — the *Doc impact* list should grow accordingly, and
   `P5.REVIEW` will have a lot to consolidate. (P3.REVIEW's note 4 — "doc impact was incomplete" — is
   worth remembering here.)

## Validation

| command | outcome |
|---|---|
| `python3 scripts/workflow.py validate` | **passed** — `Workflow validation passed.` (run after all 19 slices + the D1 promotion) |
| `python3 scripts/workflow.py deferred` | `open=3 promoted=1 dropped=0` — D1 promoted, D2/D3/D4 still open, as decided |
| `ls works/phases/active/P5/slices/*` | 21 folders (DECOMP, S1–S19, REVIEW); every new folder holds `slice.json` only — no `plan.md` pre-filled |

## Deviations from `plan.md`

- **The plan's suggested slice shape was adapted, as it invited.** Two changes worth naming: global
  chrome was split out of the landing slice (R2 designed them together, but the chrome is what every
  later page sits inside), and auth was split from portfolio (R5 is one round but four surfaces'
  worth of build).
- **The plan left room for a "non-agent 해설" component in P5. There is none.** R6 is the AI 질문 agent
  end to end — widget, page, launcher, tools, SSE, refusals, storage — so all of it is P6, per the
  plan's own instruction to put anything inseparable from the agent on the P6 side and record it.
  P5's only R6 touchpoints are the nav/footer slot, the detail strip's absence, the admin 대화 로그
  frame, and keeping the bottom-right corner clear of the vocky trigger for P6's launcher.
- No doc versions created and no "Doc impact" content added beyond a placeholder line — a pure
  decomposition changed no durable truth.
