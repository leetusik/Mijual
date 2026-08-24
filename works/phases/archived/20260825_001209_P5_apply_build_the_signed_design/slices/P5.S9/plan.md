# Plan — P5.S9: Admin backend — the operator door, read-only ops endpoints, and the pipeline run log

## Context

Read `works/phases/active/P5/phase.md` (S1–S8/S20 findings binding; DECOMP notes 5
(the 대화 로그/익명 세션 port), and *Backing work the design implies* (the run log)).
Governing records: R7 `build-prompt.md` (`rounds/07-admin/output/`) — the backend
contract behind all six tabs — plus `docs/current/security.md` (§the admin door) and
R7's SIGNOFF entry. S3's deviation note also binds: **the `estimate snapshot` stage is
not yet in the beat schedule, and this slice (which touches the scheduler for the run
log) is where it gets wired.**

This slice is the **backend only** — `P5.S17` renders. Everything is **read-only: zero
mutation endpoints** (§6.5; the door's login/logout session handling is the sole
exception and touches only its own session state).

## Deliverables

1. **The operator door** — separate credential: 운영자 ID + password from the
   environment/`.env` (via `Settings`, masked; no signup, no reset, no account-table
   row, no admin flag anywhere). Uniform constant-time failure — one response body,
   one structural code, for every cause (unknown ID, wrong password, unset
   credential); burn the hash-verify on the miss path like S7 did. Separate session:
   its own table or a partitioned reuse (decide; **no join to reader rows**), its own
   cookie — httpOnly, secure-in-prod, SameSite, and a **different name** from
   `mj_session` (record the name). CSRF middleware already covers the method surface.
   Session expiry → 401 (the client returns to the door and restores the tab).
   Attempt limiting: same posture as S7 (server concern; P4 owns shared state —
   record, don't build).
2. **The pipeline run log (backing work)** — a new table via `create_all`: one row
   per pipeline run — started/finished KST, trigger (beat/manual), per-stage counts
   and request/call spend, and the ▷ cost line verbatim as the pipeline reports it.
   Write it from the scheduler path (`mijual.scheduler` — find where a run's
   stage results are already summarized; the run log rows must come from the same
   facts the CLI prints, never re-derived). Wire **`estimate reparse` + `estimate
   snapshot`** into the run so the ① extras and headline can no longer silently age
   (S3 deviation; respect the existing stage/lock/ceiling architecture — additive,
   and update `tests/test_scheduler.py` deliberately). The 개요 tab's 「실행 기록
   없음」 alert row is *derived client-side from the beat schedule + this log* — the
   backend serves both facts; it does not fabricate a row.
3. **Read-only ops endpoints** (`/ops/...` — local route; the deploy route is P4's;
   linked from nowhere in reader chrome — verify no reader payload/router references
   it). Behind the operator session:
   - **개요**: the four status tiles (`gates summary` facts: exposure by state and
     type, field verdict split, renderable fields, last measured KST), the beat
     schedule **rendered from the Celery beat config** (never hardcoded), the run-log
     list, and the `mijual:lock:pipeline` state (read Redis; when Redis is down
     serve a degraded-but-honest state, never 500 the tab).
   - **게이트 대기열**: reason_code counts over stored extraction rows with the
     Korean `reason_ko` the code already owns; rates over **distinct
     `(rcept_no, field_key)`** (the constant lives in phase notes: 633 was measured
     pre-S6 — recount now that label rows exist, and serve the denominator with the
     counts); row inspect (field, status, reason, quote/span or an honest absent,
     rcept_no); the event-state table verbatim from the summary source; 철회
     inspect (notice_ko, note, gate-passing-but-unrendered count, blocked list).
     Suppression codes raw English — no mapping layer.
   - **정확도·비용**: the evalset report — serve what `mijual.evalset report` emits
     from its **frozen JSON artifacts, no DB** (check how the CLI reads them and
     reuse that reader; judged_by block included; the numbers' required
     decompositions come with them). Quota/spend: `extraction_call` aggregates
     (calls, tokens, ▷ cost verbatim, failures) + the 20,000/day quota constant with
     the aggregation window labeled (cumulative vs daily — serve what is true).
   - **대화 로그 / 익명 세션 / 피드백**: the **storage-agnostic port** (DECOMP note
     5): define a small interface (list conversations w/ filters + cursor, session
     aggregates, feedback queue) with P5's implementation returning empty results —
     **no conversation tables are created**; P6 implements the port. The endpoints
     serve honest zeros through the port. 사용자's reader-account half is real now:
     email, 가입일, holdings count (count only — never contents), 알림 설정 summary
     — read-only, minimal-disclosure (no hash, no anything else).
   - **vocky**: not this slice (`P5.S18`) — leave no stub route, just nothing.
3. **Tests** — terse, DB-free where possible: door uniform-failure (unknown vs wrong
   → byte-identical), reader cookie cannot open `/ops` and vice versa, one run-log
   round-trip (write a row through the scheduler's writer, read it back), the
   distinct-basis rate math, the port's empty defaults, scheduler stage wiring
   (extend `tests/test_scheduler.py` deliberately). Baseline 104 ≈ 1.9 s.

## Constraints

- **Read-only is structural**: no POST/PUT/PATCH/DELETE outside the door's own
  login/logout. No endpoint may mutate pipeline, corpus, or reader data.
- All numbers from existing sources (gates summary code, stored rows, frozen evalset
  artifacts, Celery config, ExtractionCall) — invent nothing, translate nothing
  (suppression codes stay English; ▷ stays ▷ in ops output).
- The no-join promise: nothing in this slice may relate reader accounts to
  (future) conversations — the 사용자 tab is two independent reads.
- Additive schema only; no Alembic. Redis is optional at request time (degrade
  honestly). No new deps expected.
- Local dev credential: document how to set it in `.env`
  (`MIJUAL_OPS_ID`/`MIJUAL_OPS_PASSWORD` or similar — record); the deploy-time
  issuance stays P4's open question.

## Validation

- `.venv/bin/python -m pytest` — green (including the scheduler test update).
- Out-of-suite: run `python3 -m mijual.scheduler once --offline` (or the cheapest
  real path) and confirm a run-log row lands with stage counts; curl the ops door
  (fail uniform, login with the local credential), 개요/게이트 대기열/정확도·비용/
  사용자/대화 로그/피드백 endpoints (zeros where the port is empty), reader-cookie
  rejection. Stop the server; remove test operator sessions.
- `python3 scripts/workflow.py validate`.

## Wrap-up

`result.md`; `phase.md` *Findings & Notes* (door + endpoint map + port interface for
P6 and S17; the recounted gate-queue denominator; run-log schema) and *Doc impact*
(`security` — the door as implemented; `operations` — run log + wired snapshot stage
+ beat truth; `api` — the ops endpoints (marked operator-only); `data` — the run-log
table + port; `backend`; `qa`). Structured verdict. No commits, no status
transitions.
