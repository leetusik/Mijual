# Plan — P5.S8: Portfolio backend

## Context

Read `works/phases/active/P5/phase.md` (S1–S7/S20 findings binding — S7's notes give
you `WriteSession`/`get_write_session`, the `mj_session` cookie, the `X-Mijual-CSRF`
header, the `account.id` cascade seam, and the structural-error conventions). Design
contracts: R5 `build-prompt.md` + `result.md` (`rounds/05-account/output/` — the
Portfolio / D-day 목록 / 알림 / 샘플 sections and the R5-8 챙긴 돈 note) and
`docs/current/security.md`. DECOMP notes 5(b) and 6 still bind: no
conversation-joinable column, notification **preferences only** (sending is P4).

내 포트폴리오 is the **only** gated surface. Everything here requires the
authenticated owner; anonymous/sample portfolio editing is **client-side localStorage
by design** — the server never stores an anonymous holding, so there are no
anonymous portfolio endpoints. The 세션 이월/이전 제안 flows are client offers; the
server just receives ordinary authenticated writes when the user accepts.

## Deliverables

1. **Holdings model + CRUD** — a holdings table hanging off `account.id`
   (delete-cascade via S7's seam): corp (validate it resolves via the existing corp
   resolution — a holding references a real corp in the corpus), share count
   (positive int). Endpoints: list/add/update/delete, owner-scoped, `WriteSession`
   + CSRF for mutations. Duplicate corp per account: decide (merge/refuse) and
   record.
2. **D-day list composition** — the 내 포트폴리오 home payload: for the account's
   holdings, 다가오는 마감 (D-day ascending) and 지나간 마감 (recent first), per-type
   governing anchors, the stated 기준 date — all through `mijual.present` /
   `mijual.web.reads` (S4's stock machinery is the precedent; a portfolio is N corps'
   rights). Amounts follow the R4 contract exactly: ① with 확정발행가 → per-holding
   factors (client composes; serve factors like S4 does — decide whether to also
   serve the pre-multiplied per-holding amount server-side since here the server
   *does* know the holding count — either way the numbers must be `present`-derived
   and consistent with S4's; record the choice), 확정 전 → shares + chip inputs +
   확정 예정일, ②/③ → never money. Past ① 소멸 rows carry the 놓친 돈 per-holding
   basis (holding-count × the persisted factors) + the link key to the 조회
   breakdown.
3. **챙긴 돈 marks (R5-8)** — a user-claim mark on a past ① lapse row for an
   account+offering: check/uncheck endpoints, stored per account (never touching
   disclosure data or any aggregate — it re-labels the user's own row only). Design
   the row key on the offering identity (`rcept_no`/event id), record it.
4. **Notification preferences** — per account: 시점 칩 multiselect (7일/3일/1일/당일;
   default 7일+1일 at account creation or first read — record which), and the 수신
   주소: `security.md` fixes stored PII to **email + password hash only**, so the
   수신 주소 *is* the account email — "변경" edits the account email (an
   authenticated email-change endpoint; record the semantics). KakaoTalk is UI-only
   (「예정」, no control) — **no server field for it**. No sending, no scheduler —
   preferences persist for P4.
5. **Sample portfolio endpoint** — read-only, anonymous, no account: serves the fixed
   R5-4 composition (계양전기 500주 `20260724000546` · 대동기어 300주
   `20251016000315` · 한화솔루션 500주 `20260720000067` · 세기상사 100주
   `20260713000345`) resolved live through the same D-day/list composition as a real
   portfolio — 실제 corpus 이벤트, 수치는 서버 contract에서, but flagged as sample
   in the payload; the client keeps its edits in localStorage. No fake email, no
   알림 anything in the sample payload. If one of the four pinned filings no longer
   resolves (S5 re-parented things — 계양전기 `20260724000546` was the live case),
   verify what it resolves to now and record it; never silently substitute a
   different filing.
6. **Tests** — terse, DB-free: holdings CRUD owner-scoping (A cannot read/write B's),
   the D-day composition with a mixed portfolio (upcoming/past ordering, ②/③ no
   money), a 챙긴 돈 mark round-trip, preferences default + update, the sample
   payload shape. Baseline 99 ≈ 1.7 s.

## Constraints

- All numbers via `mijual.present` / `reads` — the "내 종목 조회와 수치 불일치 금지"
  rule is structural: same sources, no re-derivation.
- Structural error codes only; the Korean copy is R5's and client-side.
- Additive schema via `create_all`/`ensure_columns`; no Alembic.
- No mail, no marketing fields, no quota/limit copy.
- Do not touch the auth flows beyond consuming S7's dependencies.

## Validation

- `.venv/bin/python -m pytest` — green.
- Out-of-suite curl pass (live Postgres): signup → add the four sample-composition
  holdings as a real portfolio → D-day list (check 한화솔루션 past-① row basis math
  against S4's breakdown; 계양전기 확정 전 → no money) → 챙긴 돈 check/uncheck →
  preferences update → the anonymous sample endpoint (no cookie) → owner-scoping
  (second account sees nothing). Clean up the test accounts; stop the server.
- `python3 scripts/workflow.py validate`.

## Wrap-up

`result.md`; `phase.md` *Findings & Notes* (endpoint map + recorded decisions for
S15/S16, the sample payload shape) and *Doc impact* (`api`, `backend`, `data` — the
new tables/columns; `security` — email-change semantics if any nuance; `qa`).
Structured verdict. No commits, no status transitions.
