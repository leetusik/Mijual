# Plan — P7.S9: fidelity sweep — all 11 items in a real browser, dev and production build, on the operator's own origins

## Goal

The phase's last middle slice. P7 exists because `P5.S19` / `P6.S7` verified a production build on
`localhost` while the operator runs `next dev` on `127.0.0.1` / Tailscale — so this sweep runs the
whole product **the way the operator does** and **the way it ships**, and checks every one of the
11 operator items plus the headline behaviour of every surface P7 touched. Fix
faithful-implementation nits **in code** (never in a landed record); anything needing a new visual
or product decision is **catalogued for the operator**, not fixed; and leave `P7.REVIEW` a measured
picture — a check table, not assertions.

## Read first

`works/phases/active/P7/intent.md` (the 11 items — the acceptance list), `phase.md` **end to end**
(Decomposition table, every `### RC-*`/per-slice findings block, the Design-collision readings,
Constraints, the Doc impact list, Open Questions Q1–Q7), each slice's `result.md` (`P7.S1`–`S8`) for
its measured numbers — **this sweep re-measures them independently**, it does not copy them — and
the `P5.S19` / `P6.S7` sections of the P5/P6 `phase.md` for the method and standing rules (`.mono`
split rule, overflow rules, the 480/481 widget boundary). Design record: `docs/current/frontend.md`
supersession table → `SIGNOFF.md` → the governing `build-prompt.md` per surface (read-only).

## Method

- **Two runtimes, three origins.** (1) The dev stack as the operator runs it: `make stack-up` /
  `make stack-status` (`next dev -H 0.0.0.0`, StrictMode on), opened at **`http://127.0.0.1:3000`**
  and the **Tailscale URL** `stack-status` prints (and `localhost` once as the control); (2) the
  production build: an isolated `rsync` copy of `frontend/` (the `P7.S2` method — no `--dist-dir`,
  real `node_modules`), `next build && next start -H 0.0.0.0 -p 3100`, opened at `127.0.0.1:3100`
  and the Tailscale IP `:3100`. Never touch the dev server's `.next`; leave the dev stack running at
  the end; kill the prod server and free `:3100`.
- Headless Chrome over CDP (the S1–S8 approach), fresh profile per run, **widths 1440 / 768 / 481 /
  480 / 390**, screenshots into the session scratchpad (not the repo), a check table in `result.md`
  (stage · check · dev 127 · dev tailnet · prod · result).
- A browser-probe FAIL is a hypothesis: re-measure with a scoped selector before believing it
  (`frontend` v0004 rule); `EADDRINUSE` / stale server traps per `phase.md` Constraints.
- Live agent spend for item 8: **two turns at most** (one in dev on 127.0.0.1, one in prod),
  recorded with the ▷ ledger line.
- Test accounts: create through the product and delete afterwards (as S2/S5/S8 did). The
  pre-existing `s19-fidelity@example.com` account is P5.S19's residue — list it in the operator
  catalogue, do not delete.

## Stage 1 — the 11 items, each on all three origins × both runtimes

1. **Nav**: two slots 관제 현황판 · AI 질문 at 1440; the 390 sheet shows the same two + the account
   row; `/stocks` still reachable from the hero, an R3 detail link-out and the agent link row.
2. **Typeahead**: on `/` and `/stocks` — no request on mount, one request per debounced keystroke,
   candidates with 종목코드, ↓+Enter → `/stocks/{corp_code}`, click works at 390 (44px), Esc closes,
   unchosen Enter keeps today's submit/miss behaviour (`에스` → 검색 불일치), JS-off form still plain
   GET.
3. **Focus**: click and Tab into every text field on `/`, `/stocks`, a stock page, `/auth/login`,
   `/portfolio` (sample), the ask composer — `outline: none`, border colour changes, nothing under
   the 조회 button (zero-gap rows); Tab onto links/buttons/tabs/펼치기/checkbox → 2px ring present.
4. **Board**: 30 rows initially; 펼치기 → +30 … until exhausted and the control disappears
   (전체: 30 → … → 386 — re-count against the live `/board` payload, the corpus may have moved);
   tab switch resets; whole-board counts unchanged; both strips open/close (30 → 90 → 94 → 30
   idiom — re-measure).
5. **Login**: sample cleared → 로그인 in the slot and the 390 sheet; one `/api/auth/me` per path;
   full 계정 만들기 → 로그아웃 → 로그인 → 계정 삭제 round trip (one run, dev 127.0.0.1; confirm the
   account is gone).
6. **Countdown**: ticks every second for **≥60 s** without a reload (read the digits at t0, t+30,
   t+60; `performance.navigation` / a window marker unchanged).
7. **No stomping**: type into the hero input, wait **≥120 s** (the old reload hit at ~40 s) — value
   kept, 0 navigations, HMR socket 101 in dev; `/_next/*` 403s = 0.
8. **AI 질문 send**: open the widget at 1440, send one question, a turn streams end to end (tool
   rows, answer, citation, footer, links) — once in dev on 127.0.0.1, once in prod.
9. **Portfolio**: the sample page at 1440/768/390 matches S8's measured layout (re-measure its
   deviation table's "after" numbers); 챙겼습니다 click flips label → 챙긴 돈 / hue / caption `본인
   표시`, same figure + 「추정」, persists across reload.
10. **Copy**: `document.body.innerText` on `/`, `/stocks`, a stock page, `/portfolio` (sample),
    `/auth/login`, `/ask` contains 0 of `localStorage` / `sessionStorage` / `브라우저 세션` / `이
    브라우저`; the captions read `본인 표시` / `서버 전송 없음`.
11. **Widget**: launcher present at 1440 and 481, absent at 480 (signed rule), on every origin.

## Stage 2 — the functional sweep P5/P6 never ran (the new dimension, on the P7-touched surfaces)

On `/`, `/stocks`, one `/stocks/{corp_code}`, one event detail, `/portfolio` (sample),
`/auth/login`, `/ask`, the widget: (a) **every visible interactive element does something
observable** — click each button/link/tab/checkbox/chip once and record the effect; a control that
no-ops is a defect (fix if it is a faithful-implementation slip; catalogue if the record drew it
inert); (b) **interaction states** — hover + focus + keyboard path through each surface's tab
order, no trap, no invisible stop; (c) **liveness over time** — countdown and any relative-time
text over 60 s, typing survives 120 s, no unrequested navigation; (d) dev **and** prod, recording any
behaviour that differs between them (that difference is exactly the P7 failure class).

## Stage 3 — cumulative headline smoke of what earlier phases shipped (terse)

Re-run the headline checks of `P5.S19` / `P6.S7` for the surfaces P7 touched (chrome, hero,
board, lookup, portfolio, auth, ask widget) — not all 230 assertions: the trust rules block in
`phase.md` Constraints (untagged estimate / money before 확정발행가 / ②③ money / KST D-day /
추후결정 beside a date / gate-failed field / past ② never 종료), the 조회 ↔ 포트폴리오 number
agreement (한화솔루션 679,575원 chain), the `.mono` split rule, no horizontal overflow at any width,
no console errors or hydration warnings. Record each as verified / regressed (fix) / catalogued.

## Stage 4 — dispositions and the operator catalogue

- Sweep `phase.md` for every mention of `S9` / `P7.S9` and give each a disposition (verified /
  fixed / catalogued).
- **One clearly labelled section** in `result.md` (mirrored into `phase.md` Open Questions /
  Findings) collecting every operator decision the phase accumulated, with the current default each
  slice implemented: Q1 의견 (vocky) unbound; Q2 focus (reading #1 applied); Q3 board 30
  (D-P7-1); Q4 챙겼습니다 row stays (R5-8); Q5 data auto-refresh (none exists); Q6 the P5 catalogue
  items P7 brushed (#1, #4, #6, #10, #12); Q7 S7's four promise-bearing developer-vocabulary
  strings + the account-caption consistency question; the `s19-fidelity` residue; anything new from
  this sweep. The review will put this list in front of the operator.
- Every code nit you fix: name it, file, why it is faithful-implementation and not a new decision,
  and re-verify on both runtimes.

## Validation (report outcomes)

`cd frontend && npm run typecheck && npm run smoke`; `.venv/bin/python -m pytest`; the CDP check
table; `grep -c "Blocked cross-origin" var/stack/web.log` (no new lines from 127.0.0.1/tailnet);
`make stack-status` (stack left up); `:3100` freed; `python3 scripts/workflow.py validate`.

## Record

`result.md`: the full check table, the functional-sweep table, fixes, the operator catalogue, the
ledger line, screenshots' scratch path, deviations. `phase.md`: Findings note + Doc impact lines for
anything durable this sweep establishes (e.g. a `frontend` line: the verification rule — dev on the
operator's origins **and** prod, functional sweep dimensions — is now the floor; extend existing
lines rather than duplicate). No `doc-new-version`, no commits, no state transitions.

## Reconciled against P7.S8 (landed after this plan was drafted)

- S8 fixed five portfolio layout slips in `Portfolio.module.css` (D1/D1b/D2/D3/D4 — see its
  `result.md` table) — re-measure its "after" numbers at 1440/768/390 in item 9.
- S8's operator questions Q-A (ragged right block in the D-day rows, record-silent geometry), Q-B,
  Q-C, Q-D, Q-E, and `phase.md` Q8 join the Stage 4 catalogue; P5.S19 catalogue #6 (sample 4건 vs
  five D-day rows) is confirmed, not fixed.
- The dev stack's api pid changed in S4 (restarted for the suggest route); `make stack-status` is
  the truth.
