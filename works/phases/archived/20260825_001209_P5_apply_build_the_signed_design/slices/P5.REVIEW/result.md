# Result — P5.REVIEW: phase review

**Verdict: `pass`.** P5 built everything its confirmed intent names, respected both exclusions
structurally, left every landed design record untouched but one sanctioned additive write, and closed
two of the four deferred jobs while honestly observing the other two. Eleven doc versions consolidate
the phase's durable truth.

---

## 1. Validation — the phase as one suite

| command | outcome |
|---|---|
| `.venv/bin/python -m pytest` | **pass — 118 passed, 2.57 s**, 1 warning (the known, deliberately-carried Starlette/httpx deprecation). No network, no model, no DB. |
| `cd frontend && npm run build` | **pass** — compiled, TypeScript clean, **16 routes** (10 `ƒ` request-time, 5 static, 1 not-found) |
| `cd frontend && npm run typecheck` | **pass** — `tsc --noEmit`, no output |
| `cd frontend && npm run smoke` | **pass — 11/11** `node:test` cases, ~90 ms, no jest/vitest/jsdom |
| `python3 scripts/workflow.py validate` | **pass** — `Workflow validation passed.` (re-run after doc consolidation: still passing) |
| cross-cutting live smoke (uvicorn + `npm run start`, `localhost`) | **pass** — detail below |

### The live smoke (liveness confirmation, not a repeat of S19's deep pass)

Both servers started against the live corpus, driven over `localhost:3000` / `localhost:8000`, then
stopped. Every number below was compared against the served payload, not eyeballed.

- **The landing renders live numbers.** `/board/summary` serves 488 (50/422/16) · 33 · 57 · 4 · 15 ·
  69 · 718.1억원「추정」 · 548.7억원 floor · 51,253,956 / 365,527,824 · 0.1402 · 퓨쳐켐 2026-09-04, and
  the rendered page states **each one identically** — hero stat line, both anchor cards, the
  소멸주의보 placard, the tab counts and the freshness stamp (`기준 2026-08-22 04:14 KST`, `stale:
  false`, `age_hours: 13` against the 18 h threshold). The countdown read `13일 06:04:19`, which is
  the exact diff to the served `next_lapse.target` (2026-09-05T00:00+09:00). `▷`, `해설`,
  `[object Object]`, `undefined` and `NaN` appear nowhere.
- **One event detail per rights type, all 200:** ① 계양전기 `20260724000546` (D-3, `발행가 확정 전`,
  할인율 20.0% with its `[근거]` chip, **no 원 amount**), ② 트리니티항공 `20250808000003` (a D-DAY
  opening reading **진행 중**, the six-value fact strip, **and the identity rule live** — 공시 본문
  표기: 주식회사 티웨이항공 stated as a fact, never silently corrected), ③ 휴맥스 `20260811000467`
  (D-5, the 통지 절차 field with its verbatim quote).
- **A 조회 with a breakdown:** 한화솔루션 resolves by name, serves coverage `2026-01-01 ~ 2026-08-22`
  (+ `convertible_start 2025-06-01`), and the page renders 발행 − 청약 = 소멸 **3,734,925주 (8.86%)**
  = **206.4억원「추정」** with the 매매기간 `[근거]`, plus 증서 1주 5,525원. The per-holding math is the
  one multiplication site, pinned by the smoke suite (500주 → 679,575원).
- **The auth round-trip:** anonymous `/auth/me` → `{"authenticated": false}` (a result, not a 401);
  `POST` without the CSRF header → **403** and no row written; signup → **201**; `/auth/me` →
  authenticated; `/portfolio` → 200 with `holdings`/`upcoming`/`past`/`reference`.
- **`/portfolio` is gated and is the only gate:** uncookied API → **401**; the frontend route → **307
  to `/auth/login`**; every other reader route still answers 200 uncookied.
- **`/ops` door + a tab:** uncookied → 401; **a reader cookie opens nothing** (401); a wrong ID and a
  wrong password return **byte-identical** 401 bodies (`cmp` clean); correct credentials open
  `/ops/overview`, which reproduces `gates summary` (628 considered / 488 exposable), serves 3 beat
  entries, 2 run-log rows, a **live Redis lock chip** (`state: free`) and the `decisions` block
  quoting `docs/current/decisions.md`'s single open bullet (D-4). The door page renders **bare** — no
  reader chrome, no 가입/재설정 affordance. OpenAPI shows **13 `/ops` routes, only login/logout
  unsafe**.
- **The vocky view degrades honestly:** unconfigured → `state: "unconfigured"`, the 16 decided field
  names served in `fields`, `count: 0`, no fabricated row, no 500.
- **Hygiene:** the test account was deleted through the product's own `DELETE /auth/account`
  (`account`/`auth_session`/`password_reset`/`holding`/`lapse_claim`/`notification_pref` all back to
  their pre-run state), the ops session was logged out, and both servers were stopped
  (ports 3000/8000 free). The operator's `.env` was never opened — ops credentials were passed as
  process env vars for this run only. `NEXT_PUBLIC_VOCKY_SRC` stayed unset, so no third-party script
  loaded.

---

## 2. Judgment against the confirmed intent

### 2.1 Scope — **pass**

Everything `intent.md` names is built, and I verified each against the running product rather than
against the slice notes:

| the intent names | evidence |
|---|---|
| FastAPI backend over the P2 exposure contract | `mijual.web` serving board/summary/detail/corrections/stocks/auth/portfolio/ops; the contract is `gates.exposure` and the API renders what it says (it even skips a row whose live verdict disagrees with the persisted column) |
| Next.js frontend for the R1–R5 + R7 surfaces | 16 routes built; landing, detail ×3 types, 조회, auth, portfolio + 알림, ops ×6 tabs all rendered live in this pass |
| auth + portfolio | the full round-trip above; the product's only gated surface |
| admin panel | the door + six signed tabs, 13 read-only routes |
| vocky integration | `GET /ops/vocky` + the 피드백 view + the three signed triggers and the script seam |

**Both exclusions are respected, and structurally rather than by discipline:**

- **No AI 질문 agent code.** `/ask` renders **chrome and nothing else** (293 characters of visible
  text, all of it nav + footer — no body, no invented copy, no fake chat). `web/conversations.py` is
  **123 lines: a `Protocol` plus an `EmptyConversations`** — no LLM client, no prompt, no storage. The
  three P6-facing ops tabs serve `{"count": 0, "rows": []}`. **No conversation table exists** — the
  live schema is the P2 corpus chain plus P5's serving/reader/operator tables and nothing else, so
  the schema-level 계정↔대화 no-join promise is trivially intact and P6 owns the storage. This is the
  signed boundary the decomposition recorded (notes 5/7/8), not a dropped design element.
- **No deployment work.** `compose.yaml` has **only `postgres` and `redis`** — no web or frontend
  service; there is no Dockerfile, no `deploy/`, no CI workflow, no `fly.toml`/`vercel.json`/
  `Procfile` anywhere. Everything deploy-shaped is a *seam* left for P4 (the mailer, `MIJUAL_API_ORIGIN`,
  `MIJUAL_COOKIE_SECURE`, the vocky credentials) rather than a half-built deployment.

### 2.2 RESPECT THE DESIGN — **pass**

- **`git log --oneline -- docs/reference/design/` shows exactly one P5 commit**: `f7eed0f` (S18).
  `git show --stat` on it: **one file — `rounds/07-admin/output/build-prompt.md` — 59 insertions,
  0 deletions**, and a grep for `^-` content lines in that diff returns **0**. So the no-`-`-lines
  fact holds, and the single write is the §6.3 subsection **the round itself delegated to the build**.
  Every other landed record — `SIGNOFF.md`, all seven `result.md`/`build-prompt.md` pairs, both
  token files, the grounding pack — is byte-untouched across the whole phase.
- The record readings the slices made are all *supersession-aware* rather than improvisations, and
  each is recorded with its citation: the superseded nav labels (내 종목 조회, AI 질문) render over
  R2's provisional literals; 「추정」 over `▷`; the locked positioning sentence is transcribed verbatim
  *including* its retired 내 종목 연결, precisely because R4's supersession is scoped to the nav label.
- The five S19 fixes are faithful-implementation corrections in **code only** — a specificity split,
  a named record-cited prop, a font-family completion, and a `minmax(0, …)` — and **not one chooses a
  value the record does not state**. The `.mono` fix is the strongest evidence of the discipline: the
  defect was that a global rule was *overriding the record's own stated sizes*, and the fix restores
  them rather than picking new ones.
- Where the design implied absent data, the backing was **built, not dropped** (D-15's rule): ③
  매수예정가 and R7's pipeline run log both exist. Where backing was genuinely impossible without
  changing a signed contract (R7's 샘플 로드 여부), the surface renders an **honest absent** — no
  placeholder, no invented `false`.

### 2.3 Trust rules — **pass, and structurally enforced where claimed**

Not merely tested — mostly *unconstructable*:

- **Present-layer construction guards.** `present.Figure` raises on an untagged estimate, on a quote
  attached to an estimate, and on `quote` beside `parts` or a one-element `parts`; `OfferingInputs` /
  `LapseResult` raise on money without `confirmed_price`; a `FieldPayload` raises on a value beside
  `추후결정`; a `Disagreement` raises with fewer than two readings. So "an estimate never renders
  untagged" and "no money before 확정발행가" are **not policies a future author can forget** — the
  objects refuse to exist. The frontend mirrors it: `EstimateMarker` has a required `estimated` prop
  with a runtime guard, and `convert()` returns `value: null` without a `unit_value`.
- **The AST/import tests are real and named.** `tests/test_web_smoke.py::test_no_request_path_module_imports_a_spending_module`
  and `tests/test_present.py::test_the_derivation_layer_imports_no_module_that_spends` enforce the
  "no OpenDART/LLM call in a request path" boundary; a third test confines HTTP clients to
  `web/vocky.py`; `WriteSession` refuses a safe method outright, so a GET cannot even acquire a
  committing session. Alongside them the suite pins the behavioural rules by name — a past ② opening
  is open not closed, a blocked field is absent and a tbd field carries no date, a summed figure is
  cited by every addend or by none, an instant serializes exactly as the web clock would.
- **The measured browser invariants** (S19's ~230 checks) cover what neither can: D-days identical to
  the served values, the countdown 0 s off, no ②/③ per-holding won, 조회 ↔ 포트폴리오 agreeing to the
  won, Korean prose verifiably drawing in Pretendard via platform fonts rather than a computed-style
  guess.
- I spot-re-measured the cheap ones live and they hold: across all **450 rendered board rows**, zero
  carry a 종료 label, zero 추후결정 rows carry a date, and all 57 open-② rows are in the 진행 중 strip.

### 2.4 The deferred-jobs record — **pass**

`workflow.py deferred` reports `open=2, promoted=2`, and that matches the reasoning:

- **D1 → `P5.S5`, promoted and closed.** The right call: its trigger was "before ② detail pages
  render", and P5 renders them. The repair was correctness work on *identity*, and the measurement is
  what makes it trustworthy — ② gate failures on exposable events **6 → 1**, the survivor a
  `span_unresolved` citation defect; **49 versions re-parented, 0 added, 0 removed**; exposable
  **488 = 50/422/16 unchanged**. The two-arm rule (reattach vs split) is well-judged: the
  single-shape fix the plan implied would have **minted duplicate events**, manufacturing D2's
  disease while fixing D1's.
- **D4 → `P5.S20`, promoted and closed.** Its trigger fired **wider than the deferred note assumed**
  (7 figures in 4 filings, not 2), and the slice found the real cause — the filer splits 청약 by
  경로, so the number the report means is printed on no row. **0 of 269 stored figures is now
  uncitable.** The interim guard S3 landed (drop the chip, keep the DART link) was the right
  behaviour while the fix was pending, and the fix generalized it rather than relaxing it.
- **D2 → still deferred, and its two watch conditions were observed and did not fire.** S12 (board),
  S14 (per-stock double-count), S19 (both halves) all measured it, and I re-measured the board half
  independently in this pass: **no two of the 450 rendered rows share an `rcept_no`**. The reasoning
  holds — the collided keys are *blocking* flags, so no rendered surface trips on them, and the
  residual `hint_duplicate` pair renders two **truthful** rows rather than a wrong number. Critically,
  **nothing was papered over with a display-level `DISTINCT`**, which was the explicit instruction.
- **D3 → still deferred, and its rationale stands.** The signed design removed the need: R4-3 fixes
  coverage at "2026-01-01 ~ 오늘 (KST)" with no 기간 picker, and outside it a figure is *unstated,
  never 0*. Pre-2026 ① depth would change no rendered number. Confirmed against the live payload —
  the coverage boundary is **served**, not assumed client-side.

### 2.5 The open questions — **pass; none hides a scope failure**

S19 §4's catalogue is **19 questions in four groups, and it is complete and honestly stated**. I
judged each; my conclusion matches the slice's — **none is an implementation defect**, and none is a
scope failure wearing a question's clothes. The distinction that makes them legitimate is consistent:
in every case the honest options were *invent something signed-looking* or *leave it visibly blank*,
and the build always chose blank.

- **Group A (copy the record does not contain) — 6 questions, all correctly left blank.** The English
  404, the silent `invalid_reset_token`, the half-stale 「API shape 확정 대기」, the locked 내 종목 연결
  positioning sentence, five composed labels, and the 4건-vs-five-rows sample subline. Writing Korean
  for any of them is a design change by the phase's own binding rule, so deferring is correct. The
  two most visible to a judge are the **English 404** (the one English string a reader can reach) and
  the **positioning sentence** — both worth an operator decision before submission, neither a defect.
- **Group B (states the design never drew) — 2, both genuinely undrawn.** The closed-청약-without-
  실적보고서 interval (센서뷰, 클로봇) and R7's 샘플 로드 여부. In both cases inventing a state would
  have meant rendering a *wrong* fact — `pending` copy for a 청약 that is over, or a `false` about a
  reader the server knows nothing about. Correctly left to the operator.
- **Group C (type/layout only the cards can settle) — 7, all inside signed anatomy.** The mono/Hangul
  face is the sharpest and the judgment is right: R1's rule is *"Korean **prose** never mono"*, every
  affected element is a chip or line **the record itself draws in mono**, prose does draw in
  Pretendard (measured), and a cross-platform Hangul mono means editing the vendored `tokens.css`,
  i.e. a design change. Same shape for `[근거]` under the 44px floor and the 340px chain step —
  enlarging either restyles a signed element.
- **Group D (product/data decisions already standing) — 4, each with a landed default or a stated
  owner.** The dated **49.2억원** footer figure is the one I would put in front of the operator first:
  it states a 2026-08-20 number on every page beside live landing numbers, and while the reasoning is
  sound (the contract serves no gate-cost figure and deriving one needs a module the request path may
  not import), it is the only place in the product where a stale number sits beside fresh ones. It is
  **backing work**, so my recommendation is a **deferred job** rather than a P5 fix slice — see §5.
- Also correctly noted as needing no decision: no favicon, and the cross-tab sample/account-slot
  observation (single-tab behaviour is correct).

### 2.6 Workflow hygiene — **pass**

All **21 middle slices + DECOMP are `done`**, `REVIEW` is `in_progress`, and **every slice folder
carries both `plan.md` and `result.md`** (checked mechanically across all 22). Orders are coherent
including the two fractional insertions (`P5.S20` at 6.5 for the promoted D4, `P5.S5` at 5 for the
promoted D1). `workflow validate` passes. `phase.md` is a genuine notebook — every slice appended its
findings, and the import maps in it are why later slices did not re-derive earlier work.

---

## 3. Two hygiene findings (neither blocks the pass; neither is code)

1. **A test account from S19 survives in the local dev database.** `s19-fidelity@example.com`
   (created 2026-08-22 08:16 UTC) plus its session row are still present, although `phase.md`'s S19
   note 11 and the S16 doc-impact line both state that all test accounts were deleted through the
   product. I left it rather than deleting it, because it is the operator's local database and the
   finding is worth more stated than silently erased. **Local dev data only — nothing is committed,
   and P4 deploys against a fresh database.** Worth one `DELETE` when convenient.
2. **Expired session rows are never pruned.** 15 `ops_session` rows have accumulated across S17/S18/
   S19 and this review. They grant nothing (expiry is checked against `expires_at`), but nothing
   deletes them either, so both session tables grow monotonically. Recorded as a **P4 operations
   item** in the `operations` and `qa` doc versions rather than as a P5 defect.

---

## 4. Doc consolidation — eleven versions, one per affected doc

The Doc impact list named eleven docs and all eleven were consolidated. Each version folds the whole
phase's substance into that doc's own structure and voice; `docs/current/` was regenerated with
`rebuild-docs` and `validate` re-run clean. **No source file was touched by this slice.**

| doc | new version | what it now carries |
|---|---|---|
| `api` | **v0002** (was the bootstrap stub) | the whole HTTP contract: the error envelope, the six contract-wide rules, the presentation contract's named shapes, board/event/stock/auth/portfolio/ops routes, and the vocky proxy's degradation contract |
| `backend` | **v0002** (was the bootstrap stub) | the module layout (`web` · `present` · `reads` · `beat` · `mail` · `labelfields`), the domain boundaries, auth/session mechanics, the offline workers, error handling |
| `architecture` | **v0003** | the HTTP + presentation layers land; the same-origin frontend boundary; the serving-precomputation seam; the six-stage topology; the import boundaries closed *by moving, not forking*; corpus at 1,359/3,990/7,076/69 |
| `data` | **v0004** | identity-scoped pairing (D1), the first stored label field, multi-part citations (D4), the serving + reader + operator tables, and D2/D3's standing rationale |
| `security` | **v0003** | the model implemented — session-as-a-row, scrypt at the `maxmem` ceiling, service-wide CSRF, the three-way uniform door, the measured no-join promise, the vocky key boundary; the checklist's implement-line closes |
| `operations` | **v0005** | the six-stage beat + run log, the fixed re-derivation order and its trap, running the API/frontend locally, the full environment table, the console as built, the freshness caveat |
| `frontend` | **v0003** | the Next.js app as built, the vendored read-only foundations, what the implementation added to the primitives, the surfaces table, the one multiplication site, and the engineering traps |
| `experience` | **v0003** | the journeys as built, **what each surface refuses to state** (measured), the behaviours decided inside the signed vocabulary, and the copy questions |
| `decisions` | **v0005** | **D-16** session mechanics · **D-17** factors-not-products · **D-18** the free label tier · **D-19** vocky read-only; **D-15 closed**; the stated defaults and record-readings |
| `product` | **v0004** | the designed product is built; the notification boundary (settings here, sending in P4); the five-row sample; the AI 질문 slot as a signed empty frame |
| `qa` | **v0003** | the suite at 118 + the framework-free frontend check, **real-browser verification as a durable method** with its four traps, and D1/D4 struck off the fragile list |

One deliberate check while writing: the ops 개요 tab parses `docs/current/decisions.md` for its
`- **Open…` bullets, so I confirmed the new `decisions` version still exposes **exactly one** open
bullet (D-4) — the panel's behaviour is unchanged, only its cited doc version moves v0004 → v0005.

---

## 5. Recommendation to the operator (not decisions taken here)

- **Read S19 §4's 19-question catalogue in one pass.** Nothing there blocks; the two I would surface
  first are the **English 404 sentence** and the **locked 내 종목 연결 positioning line**, because both
  are reader-visible before submission.
- **The footer's dated 49.2억원** is best handled as a **deferred job** (backing work: a persisted
  gate-cost precomputation + a summary key), not a P5 fix slice — P5's objective is met without it.
- **P4's wiring list is complete and written down** in `operations`: `MIJUAL_COOKIE_SECURE`,
  `MIJUAL_SESSION_SECRET`, a real `Mailer`, `MIJUAL_API_ORIGIN`, the vocky base + key over https, the
  ops credential's issuance, and ensuring the schema exists before first serve.
- **`NEXT_PUBLIC_VOCKY_SRC` has no value to set** until the operator decides a capture path into
  vocky — their own product, their call.

## 6. Deviations from `plan.md`

- **None of substance.** The plan's Job 1–3 were executed as written.
- Two small additions beyond the plan's letter, both in its spirit: I re-measured D2's board-half
  trigger independently rather than relying on S12/S14/S19's readings, and I checked the ops panel's
  `decisions.md` parser against the new doc version to be sure consolidating that doc could not
  change an operator surface.
- The plan said to clean up "any test account". I cleaned up the one **this review** created, and
  **deliberately did not delete** the pre-existing `s19-fidelity@example.com` — reporting it as a
  finding is worth more than silently erasing the evidence (§3.1).
