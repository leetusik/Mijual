# Result — P5.S8: Portfolio backend

내 포트폴리오 is the product's **only gated surface**, and it now exists end to end:
holdings CRUD, the two-section D-day composition, the 챙긴 돈 marks, the 알림
preferences (settings only — sending is P4's) and the anonymous R5-4 sample.
**0 OpenDART requests, 0 model calls, 0 new dependencies** (`pyproject` untouched).

## Validation

| command | outcome |
|---|---|
| `.venv/bin/python -m pytest` | **104 passed, 1.87 s** (baseline 99 ≈ 1.7 s; +5 tests, `tests/test_web_portfolio.py`). No network, no model, no DB. The one warning is S1 note 6's known `StarletteDeprecationWarning`. |
| out-of-suite curl pass, live Postgres | **all listed checks pass** — transcript below |
| `python3 scripts/workflow.py validate` | `Workflow validation passed.` |

The tables were landed first with the S7-recorded one-liner (the serving process
creates no schema, by design):

```
.venv/bin/python -c "from mijual.config import load_settings; from mijual.db.session import make_engine; \
from mijual.db.models import Base; from mijual.db.schema_sync import ensure_columns; \
e=make_engine(load_settings().database_url); Base.metadata.create_all(e); print(ensure_columns(e, Base))"
```
→ `added columns: []` and three new tables (`holding` · `lapse_claim` ·
`notification_pref`) beside the eleven that existed.

### Curl pass (`uvicorn … --port 8011`, live Postgres, 2026-08-22 KST)

Signed up `p5s8-a@mijual.test`, added the four sample-composition holdings as a
**real** portfolio, then:

* `GET /portfolio` — **18.3 KB in 37 ms**. `reference: 2026-08-22`; 계양전기 ①
  **D-3 · 2026-08-25** with `price_confirmed: false` and **no `unit_value` /
  `unit_value_floor` / `confirmed_price` key at all**; 대동기어 ② 전환청구 개시
  **D-63 · 2026-10-24**, `convertible` strip only, no `offering`, no `lapse`;
  세기상사 ③ **D+47** with `dissent_notice_procedure` and **no money key of any
  kind**. R5's card (anchored 2026-08-20) said D-5 / D-65 / D+45 — same dates,
  two days later.
* **한화솔루션 past-① basis math against S4's breakdown.** The row's `lapse` block
  is **byte-identical** to the block `GET /stocks/00162461` serves for the same
  offering (compared as parsed JSON). `⌊500 × 0.2465120994⌋ = 123주 × 5,525원 =`
  **679,575원** — exactly R5-4's card figure. The string `679575` appears
  **nowhere** in the portfolio payload: the server ships factors, the client
  multiplies.
* **챙긴 돈** — `PUT /portfolio/claims/20260730000366` → `{claimed: true}`, the row
  comes back `claimed: true` with `value` unchanged at
  `{"value": "20635460625", "estimated": true}`; `DELETE` → `false`;
  a filing with no 소멸 → `404 not_found`.
* **preferences** — default `{address, lead_days: [7,1]}` with **no row stored**;
  `[0,3,3]` → `[3,0]` (deduped, chip order); `[]` persists as `[]` (R5's only off
  switch); `[5]` → `invalid_lead_days`. `PATCH /auth/account` with
  `P5S8-A2@Mijual.TEST` → the 수신 주소 **and** `/auth/me` both become
  `p5s8-a2@mijual.test`.
* **sample, no cookie** — `GET /portfolio/sample` **200, 18.2 KB in 25 ms**,
  `sample: true`, the four holdings in the pinned order, `claimed` **absent
  everywhere**, no `@` anywhere in the body, no `address` / `notifications` key,
  and no `id` on any holding.
* **owner-scoping** — a second account sees `holdings: []`; `PATCH` and `DELETE`
  of account A's holding both answer **404 `not_found`** (not 403 — a stranger's
  row must not be confirmed to exist) and A's rows are unchanged. Anonymous
  `GET /portfolio` → `401 unauthenticated`. Every mutation without
  `X-Mijual-CSRF` → `403 csrf_required` before the route runs.
* **anonymous surfaces still open** — `/health`, `/board?rights=R1`,
  `/board/summary`, `/stocks?q=계양전기`, `/events/20260724000546` all **200**
  without a cookie.
* **cascade** — with 2 accounts / 3 holdings / 1 claim / 1 pref / 2 sessions live,
  `DELETE /auth/account` on both left **0 / 0 / 0 / 0 / 0 / 0** across
  `account · holding · lapse_claim · notification_pref · auth_session ·
  password_reset`. Both test accounts are gone; the server is stopped.

## What was built

**Schema** (three tables, `create_all`, no Alembic): `holding`
(`account_id` + `corp_code` + `shares` `BigInteger`, unique per account+corp,
`shares > 0` check), `notification_pref` (`lead_days` JSON, one row per account,
written on first save), `lapse_claim` (`account_id` + `performance_rcept_no`,
**no amount**). All three hang off `account.id` with `ondelete="CASCADE"` **and**
an ORM `cascade="all, delete-orphan"` — S7 note 11's seam, both halves.

**Code**: `mijual.web.portfolio` (the decisions), `mijual.web.routers.portfolio`
(transport), `reads.load_portfolio` + `HoldingEntry` + `_load_views` /
`_events_for_corps` (batched loading, now shared with `load_stock`),
`auth.change_email` + `PATCH /auth/account`.

## Deviations from `plan.md`

* **Deliverable 1's "list" endpoint is `GET /portfolio` itself**, not a separate
  `GET /portfolio/holdings`. The home payload already carries every holding with
  its 진행 중인 권리 요약, and a second list endpoint would be a second shape of the
  same rows that could drift from it. Add/update/delete each answer with the row
  they touched.
* **The add endpoint takes a `corp_code`, not a typed 종목명.** `GET /stocks?q=`
  is the one place a reader's text becomes a company and it owns R4's signed
  검색 불일치 state; a second resolver would be a second way to open the wrong
  company. (The plan asked that the corp "resolves via the existing corp
  resolution" — this uses `reads.stock_by_code`, the existing handle resolver.)
* **The 수신 주소 변경 endpoint is `PATCH /auth/account`, in the auth router.** It
  edits the account resource, so it sits beside `DELETE /auth/account` rather than
  under `/portfolio`. The plan's "do not touch the auth flows" is intact: signup,
  login, logout, reset and delete are unchanged, and this is an additive sibling
  route consuming S7's `WriteAccount`.

Everything else follows the plan. No `doc-new-version` was run (P5 versions docs
once, at `P5.REVIEW`); the durable-truth changes are in *Doc impact*.
