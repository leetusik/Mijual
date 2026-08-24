# Result — P5.S17: 운영 관제 (R7)

The admin panel is live at `/ops`, desktop-only, behind its own door, linked from
nowhere. Six complete tabs render `P5.S9`'s eleven endpoints (twelve now — see
*Deviations*), every number from a served payload, no mutation anywhere.

## What landed

**Frontend — `frontend/components/ops/` (new, 20 files) + `frontend/app/ops/` (7 routes)**

| file | what it owns |
| --- | --- |
| `routes.ts` | `OPS_ROOT` / `OPS_ROUTES` / `isOpsPath()` / `conversationsForSession()` — deliberately **not** in `lib/routes.ts`, so no reader-chrome module can pick up an ops path |
| `copy.ts` | every Korean string on the surface, each with the R7 line or served field it comes from (301 lines, ~60 constants) |
| `Ops.module.css` | the ops idiom stated once: `--ops-panel: #0e1a15`, 1px `--border-strong`, zero ornament, `min-width: 1180px`, **not one media query** |
| `atoms.tsx` | `Panel` · `Code` · `Num` · `Stamp` · `Absent` · `Rcept` · `Quoted` |
| `OpsChrome/OpsTabs/OpsClock/LockChip/LogoutButton` | the bar (six tabs · live lock chip · ticking KST clock · 로그아웃) + the status footer |
| `Door.tsx` | the pre-auth card: 운영자 ID + 비밀번호 → 로그인, one uniform failure line, four rules |
| `Overview / GateQueue + RowInspect / Accuracy / Conversations / Users / Feedback` | the six tabs |
| `log.ts`, `server.ts` | the log-row key convention; the server-side ops fetch helpers (`opsHeaders`, `opsAuthenticated`, `opsRead`) |
| `lib/opsRuns.ts` (+ `.test.ts`) | the one sanctioned client derivation — the beat-schedule × run-log join that emits 「실행 기록 없음」 |
| `lib/types.ts`, `lib/api.ts` | the `Ops*` payload types and the twelve ops calls |
| `components/chrome/SiteChrome.tsx` | **the one reader-side edit**: now a client component that returns `children` bare on an ops path |

**Backend — two additions (see *Deviations*)**

- `src/mijual/web/opsreads.py` → `open_decisions()`: the still-open bullets of
  `docs/current/decisions.md`, quoted **verbatim** with the doc's own version
  (`v0004` today, exactly one open item — D-4).
- `src/mijual/web/routers/ops.py` → `GET /ops/lock`: the lock chip's own cheap
  endpoint, and `overview()` now carries `"decisions"`.
- `tests/test_web_ops.py` → one terse test covering both.

## Validation

| command | outcome |
| --- | --- |
| `.venv/bin/python -m pytest -q` | **114 passed** (was 113; +1 for the two backend additions) |
| `npm run typecheck` | clean |
| `npm run smoke` | **11 pass / 0 fail** (was 9; +2 for the 실행-기록-없음 join) |
| `npm run build` | green — **16 routes**, all six `/ops` routes `ƒ` (request-time) |
| `python3 scripts/workflow.py validate` | `Workflow validation passed.` |

### Headless-Chrome pass — 104 scripted checks, 104 pass

Run over `npm run build && npm run start` on `http://localhost:3000` with the API
started as
`MIJUAL_OPS_ID=opsdev MIJUAL_OPS_PASSWORD=s17-throwaway-pw .venv/bin/uvicorn mijual.web.app:app`
— a throwaway credential passed as **process env vars**; the operator's `.env`
was never opened or edited. Chrome driven over CDP with Node 24's global
`WebSocket` (no new dependency, nothing installed).

1. **The door — 15/15.** `/ops` renders the card alone (no ops chrome, no reader
   chrome, no nav, no footer); a wrong ID and a wrong password produce the
   **byte-identical** line 「자격증명이 올바르지 않습니다」 in body ink (compared with
   `==`); the only control is 로그인 — no 가입, no 재설정, no third link; a deep tab
   (`/ops/accuracy`) shows the same door **at its own URL** and lands back on that
   tab after login; login sets `mj_ops` and **only** `mj_ops`.
2. **개요 — 29/29.** The four tiles equal `python3 -m mijual.gates summary`
   (488/628 exposable, 710 stored rows with its verdict split, 418 renderable,
   measured 2026-08-22 04:14 KST); the beat table renders from the served config;
   the six due instants with no run render six **alert-ink** 「실행 기록 없음」 rows
   (measured `rgb(224, 87, 63)`); the ▷ spend line renders verbatim and 「추정」
   appears nowhere on the surface; 가동 전 미결 quotes `docs/current/decisions.md
   v0004`; the lock panel shows state/source/holder/ttl.
3. **게이트 대기열 — part of 29/29 above.** The basis prints
   `691 distinct (rcept_no, field_key) / 710 stored · 19 duplicates`; reason codes
   render raw English with the served `reason_ko` and their rate; the four blocking
   flags carry their code-owned Korean; 철회 shows notice + note + the
   gate-passing-unrendered count; 없음 is a state, never a placeholder; **no action
   control exists on the page**; 행 검사 is a plain GET form and its result is in
   the URL.
4. **정확도·비용 — 32/32.** 판정 출처 renders above every number; 98.6% never
   appears without `213/216`, its CI and `partial 3`; 과차단 100% carries 19/19;
   ③ 44.0% carries 11/25; `mijual.evalset report`'s markdown renders
   **byte-identically** to the served artifact; both spend windows are labelled
   (`cumulative` / `daily`), the quota bar names its `20,000/day` denominator and
   its `operator (decisions O-1)` provenance, and the LLM line renders `▷ $2.7897`.
5. **대화 로그 / 사용자 / 피드백 — in the same 32.** The anonymity promise renders;
   the log shows an honest `0건` with its full anatomy (six signed columns, 답변/거절,
   the five signed refusal families) and invents no 「준비 중」; 사용자 renders the four
   backed columns, the signed 「가입 0건 — 미배포 상태의 실제값」 and the five 익명 세션
   columns; the 세션 cross-link filters the log; 피드백 renders its signed empty line and
   four columns, with 로그아웃 as the only button on the tab.
6. **The reader half — 19/19.** `/`, `/stocks`, `/stocks/00162461`,
   `/events/…`, `/auth/login`, `/ask` all still render the reader chrome and
   contain **no `/ops` href and no `/ops` substring at all**; a not-found event
   still renders inside the reader chrome (`P5.S13`'s measured behaviour,
   unchanged); a reader `mj_session` cookie opens nothing — `/ops` shows the door.
7. **Live state — 9/9.** A real account created through `/auth/signup` renders as
   one 독자 계정 row (`이메일 · 가입일 · 0 · 7 · 1 기본값`) with **no 샘플 로드 여부
   column and no placeheld cell**, and no portfolio contents; 계정 삭제 through the
   product's own endpoint empties the table and restores its signed line. Holding
   `mijual:lock:pipeline` in Redis flips the chip to `held` **live** with the holder
   and ttl on 개요; releasing it returns the chip to `free`.
8. **Screenshots** at 1440×1000 for all six tabs (`shots/ops-*.png` in the session
   scratchpad — reviewed, not committed).
9. 로그아웃 returns to the door. Cleanup: the test account was deleted through the
   product's own 계정 삭제 (**all six reader tables back to 0**: `account`,
   `auth_session`, `holding`, `lapse_claim`, `notification_pref`,
   `password_reset`), the Redis key removed (`exists` → 0), and uvicorn /
   `npm run start` / Chrome stopped (ports 3000, 8000 and 9222 all refuse).
   One residue, stated rather than forced: **5 rows in `ops_session`** — token
   *digests* from the pass's logins. The live session was revoked through
   `POST /ops/logout` and the browser profile is gone, so no token for them exists
   anywhere; they expire on their own by 2026-08-22 19:16 UTC. A direct `DELETE`
   against the dev database was refused by the sandbox and **was not worked
   around**; the operator can drop them or let them lapse.

## Deviations from `plan.md`

1. **"Python 113 untouched" → 114.** Two signed R7 elements had no source in
   `P5.S9`'s payloads, and RESPECT THE DESIGN says build the backing rather than
   drop the element:
   - **가동 전 미결** — the plan assumed a served decisions source; there is none.
     `opsreads.open_decisions()` now parses `docs/current/decisions.md` and quotes
     its own `- **Open…` bullets **verbatim** (never re-worded, never summarised),
     reporting `{available: false, reason}` if the file is missing.
   - **The live lock chip on all six tabs** — the only lock fact was inside
     `/ops/overview`, which walks 488 events; polling it from every tab every 15 s
     would have made the chip the most expensive thing on the surface. `GET
     /ops/lock` serves the chip alone.
   Both are read-only, behind the same `OpsGate`, and covered by the one new test.
2. **`SiteChrome` became a client component.** It is the single reader-side file
   touched. A root layout cannot read the pathname, and moving every reader route
   into a route group would have changed which layout the framework's 404 renders
   inside — behaviour `P5.S13` measured and `P5.S17` re-verified. The reader-chrome
   markup itself is untouched.
3. **Tab restore has no `?next=`.** The plan asked for the mechanism to be
   recorded: the door renders **in place**, at the tab's own URL, and
   `router.refresh()` re-runs that route on success. Nothing is stored, nothing is
   redirected, and an expiry mid-session returns to the same tab.
4. **샘플 로드 여부 renders as an absent fact, not an empty column.** R7 forbids a
   placeholder where a value would be, and `states-and-trust` §4 forbids asserting
   a fact the system does not hold. The column is **data-driven**: it appears iff a
   served row carries `sample_loaded`. Today no row does, so there is no column and
   no cell — measured (0 placeheld cells anywhere on the tab). If the backing is
   ever built (the standing open question `P5.S9` raised), the column appears with
   no frontend change.
5. **No Korean was invented for controls.** Pagination uses `←` / `→` (the record's
   own arrow vocabulary), filter labels are the API's raw parameter names in mono,
   and an empty table with no signed sentence states `{count}건`. Where R7 signs a
   sentence, that sentence is used verbatim.

## Notes for the next slices

`P5.S18` (vocky) inherits the whole ops idiom — import `Panel`/`Code`/`Stamp`/
`Absent` from `components/ops`, add the tab to `OPS_ROUTES` + `OPS_TABS`, and keep
the 병합 금지 rule the 피드백 tab already states. `P5.S19` may want to look at the
copy citations in `copy.ts`. The full findings are in `phase.md` under
`### P5.S17`.
