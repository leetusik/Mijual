# Result — P5.S9: Admin backend (the operator door, the run log, the read-only ops endpoints)

The panel's whole backend exists: a **separate** operator credential with one uniform
constant-time failure, a differently-named cookie over its own unrelated table, eleven
routes of which **nine are `GET` and the two `POST`s touch nothing but the operator's own
session row**, the pipeline run log R7's 개요 tab needs, and the storage port that lets the
three P6 tabs serve honest zeros without a conversation table existing.

**0 OpenDART requests, 0 model calls, 0 new dependencies** (`pyproject` untouched). Every
number the panel serves reproduces its source exactly: the 개요 tiles are byte-for-byte
`python -m mijual.gates summary`, and the 정확도 markdown is byte-for-byte
`python -m mijual.evalset report`.

## Validation

| command | outcome |
|---|---|
| `.venv/bin/python -m pytest` | **113 passed**, 2.49 s (baseline 104 ≈ 1.9 s → +9 tests: 7 new in `tests/test_web_ops.py`, 2 new in `tests/test_scheduler.py`). No network, no model, no Postgres. |
| `python3 scripts/workflow.py validate` | `Workflow validation passed.` |
| `.venv/bin/python -m mijual.scheduler once --offline --stages gates reparse snapshot --label p5s9-check` | ran, `lock=redis`, **0 req / 0 calls / ▷ $0.0000**; `reparse 69/69, 0 with changed facts`; `snapshot ① inputs 545 (54 priced, 26 upcoming) · 소멸 rows 32 (29 valued)`. One `pipeline_run` row landed with all three stages' counts and the ▷ line verbatim. |
| `/board/summary` before → after that run | **identical** (compared field by field, freshness/as_of excluded). |
| live curl pass against Postgres + Redis (`uvicorn`, port 8009) | door + all nine reads + both cookie-rejection directions + the degraded-Redis path — see below. |

### Live curl pass (2026-08-22, local Postgres, `MIJUAL_OPS_ID` / `MIJUAL_OPS_PASSWORD` set)

* **Door.** No cookie → `/ops/overview` **401 `ops_unauthenticated`**; `/ops/session`
  `{"authenticated": false}` (a result, not a 401). `POST /ops/login` without the CSRF
  header → **403 `csrf_required`** *before* the route runs. Wrong password, unknown 운영자
  ID and **a service with no credential configured at all** returned **byte-identical**
  401 bodies (`invalid_credentials`, no `message_ko`, no cookie).
* **Two credentials, two surfaces.** Reader cookie → `/ops/overview` 401; ops cookie →
  `/portfolio` 401 and `/auth/me` `{"authenticated": false}`; reader cookie →
  `/ops/session` `{"authenticated": false}`. `mj_ops` ≠ `mj_session` and the two digests
  live in tables with no relation.
* **개요** — 5.8 KB in 67 ms. Tiles reproduce `gates summary` exactly: **628 considered /
  488 exposable**, identical `by_state` (`R1:exposable 50 · R2:exposable 422 ·
  R3:exposable 16 · R2:no_detail 68 · R2:flagged 58 · R2:withdrawn 6 · R1:withdrawn 3 …`),
  identical `blocked` map, identical per-field renderable counts (**418 total**, with
  `subscription_agents`/`warrant_trading_period` 추후결정 **2** each). Suppression codes raw
  English incl. **`foreign_correction_head` 14** (P5.S5's chain heads). Beat table rendered
  from the declaration (`07:30 daily` · `19:30 daily` · `04:30 Sun`) with each entry's
  **due** instants. `measured_at` = the gate run's own timestamp.
* **lock 칩** — with a run in flight: `state: held`, real `holder` token, `ttl_seconds
  3599`, `expires_at`, and **`since` + `run_id` from the run log's open row** (not derived
  from the TTL). After the run: `state: free`. Pointed at a dead Redis: **200 in 0.13 s**
  with `state: "unknown", reason: "ConnectionError"` and the rest of the tab intact.
* **게이트 대기열** — 10 KB in 189 ms. `basis {stored_rows 710, distinct_rows 691,
  duplicates 19, key "(rcept_no, field_key)"}` — **the recount the plan asked for** (see
  finding 4). Per reason: `field_absent` 58 stored / 55 distinct / rate `0.0796`,
  `span_unresolved` 5/5/`0.0072`, `method_not_enumerated` 4/**2**/`0.0029` (the duplicate
  case, visible). 철회 **9 events** with `notice_ko` + the gate run's `note` verbatim +
  `gate_passed_unrendered` + the blocked-field list.
* **행 검사** — `?reason_code=span_unresolved` returns the quote with **no `span` key**;
  `?reason_code=field_absent` returns **neither `quote` nor `span`** (「없음」 is the
  client's state to render, and an absent value is an absent key).
* **정확도·비용** — 29 KB in 35 ms. `markdown` **identical to `mijual.evalset report`**
  (verified with `==`): 98.6% (213/216, CI 96–100%), 과차단 100% (19/19), 재현율 88.7%,
  `judged_by` present. Structured mirror carries every decomposition; five fields carry an
  `over_blocked_estimate` beside the rate and denominator it came from (Σ 57.0).
  Spend: LLM **cumulative**, 213 calls / 2,025,260 tokens / `▷ $2.7897`, `since`/`until`
  stated; DART **daily**, from the run log, against the operator-stated 20,000/day (O-1).
* **Port tabs** — `/ops/conversations`, `/ops/sessions`, `/ops/feedback` each
  `{"count": 0, "rows": []}`; no `next_cursor` key, no invented Korean.
* **사용자** — with a throwaway reader (1 holding, 알림 `[3, 0]`):
  `{email, created_at, holdings: 1, notifications: {lead_days: [3,0], stored: true}}` — a
  **count only**, no 종목/수량, no hash, no `sample_loaded`.
* **No reader payload mentions `/ops`** (`/board`, `/board/summary`, `/stocks`,
  `/portfolio/sample`, `/health` all checked; a test pins it).

**Cleanup.** Server stopped. The throwaway reader account and **every** `ops_session` row
deleted — verified `accounts 0 | holdings 0 | prefs 0 | auth sessions 0 | ops sessions 0`.
The **two `pipeline_run` rows were deliberately kept**: they are truthful records of two
runs that really happened (and one of them re-derived the corpus), so deleting them would
make the operator's log lie about its own history.

## What landed

**New modules.** `src/mijual/beat.py` (the Celery-free beat + lock-key declaration),
`src/mijual/web/ops.py` (the door), `src/mijual/web/opsreads.py` (the numbers),
`src/mijual/web/conversations.py` (the P6 port), `src/mijual/web/routers/ops.py`
(transport), `tests/test_web_ops.py`.

**New tables** (`create_all`, additive, no Alembic): `ops_session`, `pipeline_run`.

**New settings:** `MIJUAL_OPS_ID`, `MIJUAL_OPS_PASSWORD` — both masked in
`Settings.__repr__`. Local dev: add the two lines to the gitignored repo-root `.env`.
**Nothing was written into `.env`** — inventing a credential in the operator's own file is
theirs to do, and `P5.S17` cannot open the door until they do (one line in the verdict).

**Scheduler:** two new stages (`reparse`, `snapshot`), `PipelineConfig.trigger` /
`write_run_log`, `PipelineResult.spend_line`, `open_run_row` / `close_run_row`, CLI flags
`--trigger` / `--no-run-log`.

## Deviations from `plan.md`

1. **Two `GET` session routes, not one.** The plan named the door's login/logout as the
   only non-`GET` surface; I also added `GET /ops/session`, which reads nothing but the
   session row. R7 requires "세션 만료 → 문으로 복귀, 로그인 후 있던 탭 복원", and the door
   has to ask *something* whether a session exists before deciding between the Access card
   and the restored tab. It is a read and it answers `{authenticated: false}` rather than
   401, the same shape `GET /auth/me` uses.
2. **Three files outside `mijual/web` were touched to keep the import boundary honest**
   (`mijual/beat.py` new; two module-level imports in `mijual/evalset/sample.py` moved into
   the two draw functions that use them). Both are "move, not fork" — see findings 1–2.
   Without them, the ops router would have pulled `mijual.collect`/`mijual.extract` into the
   serving process, which is the smuggling `P5.S2` note 7 warns against.
3. **The gate-queue denominator is 691, not 633.** The plan predicted the recount; it moved
   because `P5.S6` added 61 label rows. Duplicates 16 → 19.
4. **R7's 샘플 로드 여부 column is served as an absent key, not as `false`.** There is no
   server-side fact behind it in P5 and building one would change `P5.S8`'s signed
   contract. Recorded as a finding **and as a new Open Question** rather than papered over —
   see phase note 8.
5. **`estimate reparse` was wired beside `estimate snapshot`.** The plan named both; worth
   restating that this makes the scheduler's stage tuple six long and changed
   `tests/test_scheduler.py`'s default-stages assertion deliberately.

## Doc impact

One line appended to the phase's *Doc impact* list, naming `security`, `operations`, `api`,
`data`, `backend`, `architecture`, `decisions` and `qa`. No doc version was created (P5
versions docs once, at `P5.REVIEW`).
