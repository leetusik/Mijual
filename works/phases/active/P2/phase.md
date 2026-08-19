# Phase P2: Data & Extraction Pipeline

_Intent: see [intent.md](intent.md)._

## Objective

Build the collection (DART OpenAPI + scheduled jobs) and schema-based LLM extraction pipeline with deterministic validation gates (arithmetic/date/citation-span checks, reason codes); produce the '2026 소멸 신주인수권 가치 총액' estimation and the ~100-filing labeled evalset + extraction-accuracy report.

## Context

P2 is the data backbone the whole product stands on. It inherits an unusually well-characterised
upstream from P1 — do **not** re-derive any of it:

- `docs/current/data.md` (v0002) — DART as the sole MVP source, the three-tier field model
  (`API` / `본문-label` / `본문-prose`), the 10-field extraction-target list with its gate per field,
  the 정정공시 pairing method, and the collection/version constraints that fix P2's entity keys.
- `docs/current/decisions.md` (v0002) — D-1 (all three rights types kept, exclusions, drop order),
  D-4 (Gemini 3.7 Flash high via the operator's "changple5" credential).
- `docs/current/operations.md` (v0002) — the 결격 uptime window and the "no OpenDART call in the
  request path" consequence that binds P2's persistence design.
- `docs/reference/dart/field-matrix.md` (295 lines) — per-field evidence, sample counts, the label
  scan, size regimes, and the API constraint table. **The primary reference for every P2 slice.**
- `scripts/spike/{dart,survey,corrections}.py` (731 lines, stdlib-only) — throwaway-grade by P1's own
  rule, but the DART client and the 본문 table/`<CORRECTION>` parsing in them are *proven against real
  filings* and are meant to be **ported**, not rewritten from scratch.
- An on-disk cache of 1,002 distinct OpenDART responses (`scripts/spike/samples/`, gitignored, ~9.4 MB,
  59 of them 본문 ZIPs) — offline development and deterministic tests are possible today.

What P2 must produce is the first **real** (non-throwaway) code in this repo: a persisted, scheduled,
gated pipeline plus two evidence deliverables (the 소멸 총액 number, the accuracy report).

## Decomposition

Nine middle slices, `P2.S1` … `P2.S9`, all `risk: high` — every one of them writes real code across
more than one file, which is the workspace's own line for the `high` tier. No `low` slice was carved
out: nothing in this phase is a one-line edit or a docs-only change.

**Ordering principle — build in reverse of D-1's drop order.** D-1 fixes the deadline-pressure drop
order as **EB → ②'s backfill → ③ → ②, with ① last**, because ① 유증 is the only rights type that
exercises the §3.6 reading layer at all (② and ③ are near-fully structured and need **zero** LLM).
So the phase builds ① end-to-end first (collect → parse → extract → gate), then makes it run on a
schedule, and only then adds ②'s corpus and the backfill. Everything after `P2.S6` degrades the board
rather than emptying it if the deadline bites.

| slice | order | kind | risk | scope |
|---|---|---|---|---|
| `P2.S1` | 1 | feature | high | Package scaffold, storage schema (event/version/snapshot), DART client port |
| `P2.S2` | 2 | feature | high | Collector for ① 유증 + ③ 매수청구: new filings **and** 정정 discovery |
| `P2.S3` | 3 | feature | high | 본문 XML parse layer: labeled rows, `CORRECTION` block, citation spans |
| `P2.S4` | 4 | feature | high | LLM extraction (layer 1) — Gemini schema extraction + 정정 re-extraction |
| `P2.S5` | 5 | feature | high | Deterministic validation gates (layer 2) + per-field reason codes |
| `P2.S6` | 6 | feature | high | Celery beat scheduling of the collect / extract / gate tasks |
| `P2.S7` | 7 | feature | high | ② CB collection + backfill to ≥ 2025-06 (quota-gated) |
| `P2.S8` | 8 | analysis | high | 2026 소멸 신주인수권 가치 총액 estimation pipeline |
| `P2.S9` | 9 | eval | high | ~100-filing labeled evalset + extraction-accuracy report |

### What each slice covers, and why it is its own slice

**`P2.S1` — Package scaffold + storage schema + DART client port.** Everything downstream needs a
place to live and a place to write. Creates the first real Python package (pyproject-based, in a
`.venv` — see C-8), the SQLAlchemy models implementing the **event / version / snapshot** design that
`data.md` makes non-negotiable (event key `(corp_code, report_subtype, original_rcept_dt)`, every
observed `rcept_no` a version, every version snapshotted at collection time, raw response body kept),
Postgres locally, and the port of `scripts/spike/dart.py` into the package as the DART client —
**keeping its retry/backoff, its `null`-param dropping, its `group[]` handling, and its key-safe
on-disk caching**, so the existing 1,002-response cache stays usable as an offline fixture path.
Its own slice because every later slice imports it and a wrong entity key is the one mistake that
silently destroys the 정정 story (F11/§4.2).

**`P2.S2` — Collector for ① and ③.** `list.json` polling within the 3-month window with paging, detail
fetch, snapshot persistence, and — the part that is easy to get wrong — **정정 discovery**: poll
`list.json` for `[기재정정]` rows and re-window the detail fetch on the **original** filing's date. A
naive "yesterday's filings" poll misses **100%** of corrections (40/40 measured). ① and ③ ride together
because ③ is nearly free once the collector exists (its fields are all `API`) and because both are
ahead of ② in the drop order. Two filters are **correctness requirements, not conveniences**: exclude
제3자배정/일반공모 유증 (they issue no 증서 — read 본문 `18. 신주인수권양도여부`, do **not** trust
`ic_mthn` alone) and suppress 소규모합병 (they grant no 매수청구권). Publishing either as a live right
is a correctness bug, and the suppression is also a demo asset (6 overlapping 소규모합병 windows in the
judging week).

**`P2.S3` — 본문 deterministic parse layer.** ZIP → single UTF-8 XML, labeled-row table parse (lift the
proven logic from `scripts/spike/corrections.py`), the 10/10 stable ① numbered labels, the
`<CORRECTION>` `1./2./3. 정정사항` parse, and **character-offset citation spans** — the parse layer is
what makes the layer-2 citation-span gate possible at all. Separate from S2 because it is a pure
function of a document (testable offline against the 59 cached 본문 ZIPs) and separate from S4 because
**it is deterministic**: everything it can read must not be paid for with an LLM call. Hard rule:
증권신고서 (0.6M–1.9M chars) is sliced by `<TITLE>` section and never fed whole; 주요사항보고서
(2.6k–10k chars) is the one-shot unit.

**`P2.S4` — LLM extraction, §3.6 layer 1.** Gemini schema extraction for the 10 target fields plus
정정 prose re-extraction and diff (structured-field diffing alone is not enough — `기타 투자판단에
참고할 사항` is the single most-corrected 항목, 11/40, and is free text). Every extracted value carries
its citation span. **Blocking operator dependency: the "changple5" Gemini credential is not in this
repo** (see O-2) — this slice cannot start without it, and it is also where the exact API model id for
"Gemini 3.7 Flash (high)" gets confirmed. Its own slice because it is the only slice that spends money
and the only one whose output is non-deterministic.

**`P2.S5` — Validation gates, §3.6 layer 2.** The named gate per field from `data.md`'s table
(arithmetic, date order, citation-span existence, cross-checks against the API values), per-field
reason codes, and the invariant that **a field failing its gate is never exposed** — it is recorded
with its reason code instead. All 금액/D-day computation is deterministic and unit-tested **without any
LLM call** (small, high-value suite per the workspace test rule — no fixture sprawl). Separate from S4
on purpose: the gate is the product's trust claim and must be testable with the LLM switched off.

**`P2.S6` — Celery beat scheduling.** Beat + worker + Redis broker, wiring the collect / extract / gate
tasks into periodic jobs with idempotency (re-running a collection must not duplicate versions) and a
lock so overlapping runs cannot double-fetch. Placed **before** `P2.S7` deliberately: "scheduled jobs"
is in the phase objective while ②'s backfill is D-1's second thing to drop, so the scheduler must not
sit behind a droppable slice in the tail.

**`P2.S7` — ② CB collection + backfill.** CB structured fields only (**zero LLM** — 전환가액, 전환비율,
전환청구기간, 오버행 수량·비율 are 47/47; the refixing floor 36/47), registering the CB task in the
beat schedule, plus the D-1-funded backfill to **≥ 2025-06** (▷ ~300–600 requests, ~half a day)
without which ② has density but no urgency (0 of 267 cached 2026-filed CB events open 전환청구 before
2027-01-15). **Measure/confirm the daily quota before running the backfill** (O-1). Split out of the
scheduling slice because it is the phase's one genuinely droppable unit and because the quota check is
an operator-facing gate; isolating it makes dropping it a clean no-op instead of losing the scheduler.
It can also ship structured-only, so it never blocks on the LLM.

**`P2.S8` — 소멸 신주인수권 가치 총액 estimation.** The year's 유증 corpus → an estimate of lapsed
warrant value (청약률 · 증서 시세), which is the presentation's opening number and the landing
headline. Handoff §7 discipline is load-bearing here: evidence-tagged facts vs `▷` estimates, no
inflation, honest gaps. Its own slice because it is a *reporting* pipeline over the collected corpus,
not part of the serving path — and because it produces the corpus `P2.S9` labels.

**`P2.S9` — Evalset + accuracy report.** ~100 filings drawn from S8's corpus, a hand-label workflow
(operator co-work — **expect a `pending` gate**), and a per-field precision + gate-block-rate report.
Last because it measures everything before it, and because its sample is free once S8 has collected.

### Refinement vs the approved plan

The plan's recommended breakdown was eight slices with "Celery beat jobs + ② CB collection & backfill"
as one slice (its S6). The executor split that into `P2.S6` (scheduling) and `P2.S7` (② + backfill),
staying inside the plan's stated latitude ("executor may refine, staying ordered along the D-1 drop
order"). Reasons: (a) they are two jobs with different failure modes — infrastructure wiring vs a
quota-sensitive half-day data operation; (b) the backfill is P2's only genuinely droppable unit, and
isolating it makes dropping it a no-op instead of also losing the scheduler, which the objective
requires; (c) the backfill carries its own operator-facing quota gate. Numbering shifted the plan's
S7/S8 to `P2.S8`/`P2.S9`; nothing else changed and no scope was added or dropped.

## Findings & Notes

_Durable findings and cross-slice notes; `DECOMP` seeds this, and each slice appends when it finishes._

### Seeded by `P2.DECOMP` (2026-08-19)

**N1 — Stack decision (operator, folded in at the P2.DECOMP planning gate): FastAPI + SQLAlchemy +
Postgres, with Celery beat + a Redis broker for scheduling.** P2 builds a **plain Python package** —
collector / parser / extractor / gates / estimation — with Postgres persistence via SQLAlchemy. **No
FastAPI endpoint is written in P2**: the HTTP layer is P3's, and it reads persisted snapshots only.
This is the concrete resolution of the handoff §6-5 stack preference and of `intent.md`'s note that the
final architecture choice happens at decomposition. Filed as a Doc impact note below.

**N2 — The version/snapshot design is the one place where a shortcut destroys the product.** Detail
endpoints return **one row per event, newest version only** (SKC's 3 유증 filings collapse to one row;
디모아's 6 to one); `rcept_no` **mutates** to the newest version (only 7/39 `estkRs.rpt_rcpn` values
match today's `piicDecsn` rcept_no); and superseded structured values are **unrecoverable from the
API**. Therefore: event key `(corp_code, report_subtype, original_rcept_dt)`, every observed `rcept_no`
stored as a version, **every version snapshotted at collection time**, raw body retained. Without
snapshots there is no old→new diff and the 정정 story — the product's whole point — cannot be told.

**N3 — 정정 discovery must be windowed on the ORIGINAL date.** The `bgn_de`/`end_de` window on the
detail endpoints filters on the **original** 접수일, not the correction's: a single-day probe on the
correction date returned `[]` in **40/40** samples. A daily "yesterday's filings" poll driven by detail
endpoints silently misses **every** 정정. Poll `list.json` for `[기재정정]` rows, then re-fetch the
detail endpoint on the **original** filing's date window. Pairing (validated, 30/40 paired — 16 exact,
14 nearest-earlier): read `<CORRECTION>` `2. 정정대상 공시서류의 최초제출일` as a **hint, not a key**
(it is filer-entered and sometimes years wrong), fall back to nearest-earlier same-corp same-subtype,
and read the `3. 정정사항` table (40/40 parseable) as the authoritative what-changed list. One event can
carry a chain (디모아: 6 corrections); `[첨부정정]` is attachment-only and skippable.

**N4 — `estkRs` schedules are version-stale in practice, not just in theory; 본문 wins.** 휴림에이텍's
`estkRs` still reads 청약 9/4~9/7 while its current 본문 reads 10/19~10/20. **The 주요사항보고서 본문 is
the source of truth for ① schedules**, and any ① schedule claim not read from 본문 must be marked `▷`.
`estkRs` remains useful for 발행가/주관사/배정기준일 confirmation and as the 발행공시 ↔ 주요사항보고
join (`rpt_rcpn`), but never as the last word on a date.

**N5 — `bdRs` is not a CB source (negative result, do not re-discover).** 사모 CB/EB is
증권신고서-면제; across 77 sampled rows the 지분 관련 사채 fields were 0/77 filled. For ② the
**주요사항보고서 (`cvbdIsDecsn`) is the only source**.

**N6 — ② and ③ need zero LLM extraction for the MVP.** All countdown-critical fields are `API`:
② 전환가액/전환비율/전환청구기간/오버행 수량·비율 47/47, refixing floor 36/47; ③ 반대의사 접수기간
41/41, 주주확정기준일 41/41, 합병일정 41/41 (the low fill on 매수 예정가격 15/83 and 행사기간 17/83 is
**semantic** — 소규모·간이합병 grants no right — not a data gap). ① is the only type that exercises the
reading layer, which is why it is built first and dropped last.

**N7 — Reuse the P1 cache and the P1 spike code deliberately.** `scripts/spike/samples/` holds 1,002
cached responses (gitignored, regenerable) including 59 본문 ZIPs — enough to develop and test the
parse/extract/gate path fully offline, with no key and no network. `dart.py` already handles the four
things a naive client gets wrong (dropping `null` params, `group[]` vs flat `list`, 503 retry/backoff,
ZIP-vs-error-XML detection). Port it; do not rewrite it.

**N8 — Lesson inherited from `P1.REVIEW`: regenerate any committed summary artifact from the FINAL
run before the slice closes.** P1 shipped a stale `corrections.json` (8 records) that its own prose
cited for a 40-record run. Every P2 slice that commits a generated report (S8's estimation, S9's
accuracy report) must regenerate it from the run whose numbers the prose quotes.

**N9 — Environment facts measured at decomposition time (2026-08-19, this machine).** Docker daemon is
up (server 28.2.2) → **Postgres and Redis are most cheaply run as containers**; `psql` is **not** on
PATH. `redis-server` is installed (`/opt/homebrew/bin`) but **not running** (connection refused on
6379). System Python is **3.13.5** with **no** `sqlalchemy` / `celery` / `fastapi` installed → `P2.S1`
must create a virtualenv (`.venv/` is already gitignored) rather than assume system packages. `.env`
exists at the repo root, gitignored, and currently holds `DART_API_KEY` only.

**N10 — Operator-facing gates should be raised EARLY, not when the consuming slice starts.** Two items
block slices in the middle of the phase: the Gemini credential (`P2.S4`, O-2) and the daily-quota
confirmation (`P2.S7`, O-1). P1's review found that batching operator questions into one round-trip
saved a phase-halting gate; the orchestrator should surface both at `P2.S1`/`P2.S2` time so neither
stalls the run later. (`P2.S9`'s hand-labelling co-work is a third, and is expected to be a real
`pending` gate.)

### Appended by `P2.S1` (2026-08-19)

**N11 — The package exists; import it, do not re-scaffold.** `pyproject.toml` (hatchling, `src/`
layout) + `.venv` with `sqlalchemy` 2.0.52 / `psycopg[binary]` 3.3.4 / `pytest`. Public surface:
`mijual.config` (`load_settings`, `Settings`, `SPIKE_CACHE_DIR`), `mijual.dart`
(`DartClient`, `rows`, `groups`, `decode_document`, `CacheMiss`, `NotAZipError`), `mijual.db`
(`Corp`, `Event`, `FilingVersion`, `Snapshot`, `RightsType`, `CorrectionKind`, `make_engine`,
`session_scope`, `create_all`, `reset_schema`), `mijual.db.repository` (`ensure_corp` /
`ensure_event` / `ensure_version` / `ensure_snapshot` — idempotent upserts), `mijual.smoke`.
Local infra: `docker compose up -d postgres` (host **5433**, `DATABASE_URL` default matches);
Redis sits behind the `scheduling` profile on host **6380** for S6
(`docker compose --profile scheduling up -d redis`). Celery/Redis/FastAPI are **not** dependencies yet.

**N12 — The P1 cache is now a first-class offline fixture path, and a test guards it.**
`DartClient(cache_dir=SPIKE_CACHE_DIR, offline=True)` resolves the 1,002 P1 responses with **no key and
no network**; a cache miss raises `CacheMiss` instead of silently going to the network. The cache
filename scheme is byte-identical to the spike's and is pinned by a golden filename in
`tests/test_dart_client.py`. **Develop and test S3/S4/S5 against this path**; use a live
`DartClient()` (cache → gitignored `var/dart-cache`) only when new data is actually needed.

**N13 — N2 re-measured live by the S1 smoke, on 계양전기 (`00102618`).** `list.json` shows three
versions of one 유증 event (`20260508000928` original → `20260611000483` → `20260724000546`, both
`[기재정정]`); `piicDecsn` over the whole 2026-01-01~08-18 window returns **exactly one row**, carrying
only `20260724000546`. The event row keys on `(00102618, piicDecsn, 2026-05-08)` and all three versions
hang off it. The persisted 본문 reproduces field-matrix §5 exactly (31,376 XML chars, 신주인수권증서
×17, `<CORRECTION>` present) — an independent check that the ported ZIP/decode path is faithful.

**N14 — Collection is idempotent by upsert, not by failure.** `ensure_*` are get-or-create on the
unique keys; a snapshot whose `sha1` is unchanged is a no-op, a changed body always becomes a new row.
Re-running the whole smoke (same process and a fresh process) leaves counts at 1 corp / 1 event /
3 versions / 5 snapshots. S6's scheduler can therefore re-run a window safely; it still needs its own
lock against *concurrent* runs, but not against repetition.

**N15 — S2's correctness filter has a schema home already: `Event.suppressed_reason` (plain VARCHAR,
deliberately not an enum) + `suppressed_note` + `suppressed_at`, with `Event.suppress()`.** Record
제3자배정/일반공모 유증 and 소규모합병 as *collected and excluded, with a reason* — never drop them
silently. Adding a new reason code costs no migration; adding a `RightsType`/`CorrectionKind` member
does (they are native PG enums, and P2 has **no Alembic** — see N16).

**N16 — No Alembic in P2 (deliberate decision).** Schema evolves via `create_all` /
`reset_schema` (drop + recreate) because every row is re-collectable from the cache or the API. Any
slice needing a schema change just edits `models.py` and re-runs; do not add a migration tool inside
P2. Revisit only if P3 needs migrations against data that cannot be rebuilt.

**N17 — Gotcha, already paid for once: SQLAlchemy JSON columns need `none_as_null=True`.** Without it a
Python `None` is stored as the JSON scalar `'null'`, not SQL `NULL` — which silently defeated
`Snapshot`'s "exactly one body" CHECK on Postgres and SQLite alike. Any new JSON/JSONB column in this
schema must carry the same flag.

**N18 — Client hardening beyond the spike (keep it).** A non-ZIP `document.xml` body now raises
`NotAZipError` and is **never cached**, so a transient error body cannot poison a fixture permanently
(all 63 currently cached document files were verified `PK`). Key safety stayed structural: the key
touches only the live request URL — never a filename, never the recorded `_url`, never an exception
message. A grep for the key value across every new file and the new cache returned 0 hits.

### Appended by `P2.S2` (2026-08-19)

**N19 — `report_nm` carries more prefixes than `[기재정정]`/`[첨부정정]`, and a wrong read mints a
phantom event.** Measured over the 2026 KOSPI+KOSDAQ 주요사항보고 list: also `[첨부추가]` (6 rows) and
`[정정명령부과]` (2). `CorrectionKind.from_report_nm` now buckets **any** bracketed prefix — `첨부*` →
`ATTACHMENT`, everything else → `DISCLOSURE` — so an unknown prefix is never mistaken for an original
(which would give later corrections the wrong `original_rcept_dt`). The literal string is kept in
`FilingVersion.report_nm`, so no PG-enum member (and no `reset_schema`) was needed.

**N20 — The N2 event key is NOT injective on real data: ~8% of events collide.** Two independent
collision modes, both measured: (a) a corp files **two** 주요사항보고서 of the same subtype on the same
day (한솔테크닉스 `20260410003732` + `…3738`, both `rcept_dt` 2026-04-13 — one 제3자배정, one 주주배정);
(b) a corp runs **two concurrent events** of the same subtype and only one original is visible, so
nearest-earlier pairing merges both chains (이렘 `00116426`: 제3자배정증자 + 주주배정증자; 모다이노칩
`00480048`: 소규모합병(케이브랜즈) + 정식합병(로젠)). Detector: the detail endpoint returns **one row per
event**, so **2+ detail rows landing on one event key means the key collided** — 36 events flagged
`event_key_collision`, 3 of them `detail_conflict` (the rows disagree about whether a right exists).
**Rule that follows and must not be relaxed: never suppress an event whose detail rows disagree** —
doing so hid a real 주주배정 유증 (한솔테크닉스) in the first implementation. S3 can split these using
`<CORRECTION> 2. 최초제출일`; until then they are flagged, not merged silently.

**N21 — Unpaired corrections need a placeholder *and* a retirement path.** A correction whose original
is invisible becomes its own event (`suppressed_reason=unpaired_correction`), with its chain-mates
within 240 days attached to it rather than one event each. When a later/wider run pairs the same
filing properly, the placeholder is re-suppressed `superseded_by_pairing` naming the winner
(17 retired). Residue after both runs: 47 of 1,179 `rcept_no` sit under two event keys — 38
placeholder-vs-real (labelled), 5 placeholder-vs-placeholder (window-dependent chain head, both
suppressed), **3 on two exposable events** (the N20(b) mis-merge, all flagged). Nothing exposable is
duplicated without a flag.

**N22 — The detail window must be per (corp, subtype), not per event, and joined by `rcept_no`.** One
call per corp+subtype covering `[min(original 접수일) − 30d, max(original 접수일)]` is the same request
count as per-corp and tolerates 접수일/결의일 skew. Rows are matched back by `rcept_no`; a row for a
version `list.json` never showed us (a 정정 filed after the window ends) is **adopted** as a
`detail_only` version instead of being dropped — 16–19 per run. Also: `rcept_no[:8]` is the submission
date and is **not always** the `rcept_dt` (`20260410003732` → `rcept_dt` 2026-04-13), so it is only a
fallback for versions discovery never saw.

**N23 — The P1 cache is complete for KOSPI but truncated for KOSDAQ H1.** P1 fetched 10 pages per
window; KOSDAQ 2026-01~03 has 14 pages and 04~06 has 15, so pages 11+ were never cached. Offline runs
over those windows are ~2,300 list rows short and say so (`gaps:` in the run report). Anything needing
the complete H1 KOSDAQ universe must re-fetch (~9 requests), **not** assume the cache is a census.

**N24 — O-4 answered (26 requests): KONEX changes nothing.** `corp_cls=N`, 2026-01-01~08-19: 30 events
(27 ①, 3 ③), of which **0 are exposable** — 25 `no_warrant_class`, 1 `no_appraisal_right`, 4 unpaired.
KOSPI+KOSDAQ stays the MVP frame. (`corp_cls=E` 기타 not probed.)

**N25 — Request discipline is now structural, not a habit.** `DartClient(max_requests=N)` raises
`RequestBudgetExceeded` on the next live fetch; the collector catches it per phase, keeps everything
already collected, and reports `BUDGET EXHAUSTED`. Slice spend: 291 live requests (26 KONEX + 240 +
25), no quota error. **Re-running a window is nearly free** — the second live pass over the same
window cost 25 requests (17 detail retries + 8 본문) and added zero events and zero versions, which is
the property S6's scheduler depends on.

**N26 — `ic_mthn` decides ① provisionally; the corpus for O-5 is one event.** The filter keeps
`주주배정후 실권주 일반공모` / `주주배정증자` / `주주우선공모증자` and suppresses the rest as
`no_warrant_class` (213 events). Exactly one `주주우선공모증자` exists in the corpus
(`20260807000339`, corp `00232007`), collected and unsuppressed — S3 can close **O-5** by reading its
본문 `18. 신주인수권양도여부` alone. Final exposure for every ① still requires that 본문 check
(S3/S5); `ic_mthn` alone never confirms a right.

## Constraints

Binding on every P2 slice (handoff §7 + `intent.md` + the P1 doc set):

- **§3.6 AI-role architecture is fixed.** The AI *reads* (schema extraction from 비정형 공시) and
  *speaks* (grounded generation); **all calculation — 금액 환산, D-day — is deterministic**. Extracted
  fields are exposed **only** after passing their deterministic gate; a failed field is recorded with a
  reason code and never shown.
- **Anything deterministically readable must not be paid for with an LLM call.** `API` and
  `본문-label` fields go through the parse layer, never the extractor.
- **No OpenDART call in the request path.** The board renders from persisted snapshots — transient
  upstream 503s are measured and the 9/7 11:00 → 9/11 23:59 window is 결격-grade (pass/fail, not
  scored). This is a P2 persistence requirement, not P3 polish.
- **Correctness filters, not conveniences:** exclude 제3자배정/일반공모 유증 (check 본문
  `18. 신주인수권양도여부`; do not trust `ic_mthn` alone) and suppress 소규모합병 (`mg_stn` +
  `aprskh_*` presence).
- **Secrets.** `DART_API_KEY` and the Gemini "changple5" credential live in the gitignored repo-root
  `.env`, are read in-process, and are **never** echoed, logged, embedded in a cached URL/filename, or
  committed. No key value may appear in any artifact.
- **Evidence tags.** Facts carry an `rcept_no`, a command, or a source; estimates are marked `▷`. Never
  blur the two, never round a sample up, never present a probe as a survey. Record honest gaps as gaps.
- **금지선:** no fine-tuning / PyTorch / HF framing anywhere — in code, comments, notes, docs, or
  pitch material. Model *training* is out of the story entirely.
- **Small scope, production-grade polish.** P2 code is the real thing (unlike P1's spike), but tests
  stay terse: minimal high-value cases, no fixture or scaffolding sprawl. Prefer a smoke run plus a
  small deterministic unit suite for the 금액/D-day math.
- **Deadline discipline: 2026-09-07 10:00.** A slice that starts sprawling records the surplus as a
  deferred job (`defer-job`) rather than absorbing it. Drop order under pressure is D-1's:
  EB → ②'s backfill → ③ → ②, ① last.
- **Schedule management is operator-owned** (D-5) — do not re-raise or plan around the operator's
  calendar. This does not relax the 결격 uptime window, which is a property of the service.
- **No commits by executors**; the orchestrator owns state transitions and commits. Durable-truth
  changes go to the Doc impact list below, never to `doc-new-version` inside a middle slice.

## Doc impact

_Running list; the `P2.REVIEW` slice consolidates these into doc versions on a pass._

- **`architecture`** (new doc) / **`decisions`** — **stack decision for the data backbone:** P2 builds a
  plain Python package (collector / parser / extractor / gates / estimation) persisting to **Postgres
  via SQLAlchemy**, with **Celery beat + Redis** for scheduled collection; **FastAPI is the P3 HTTP
  layer and reads persisted snapshots only — no FastAPI endpoint is written in P2**. Resolves the
  handoff §6-5 "reuse the operator's stack" preference and `intent.md`'s deferred architecture choice.
  Source: operator decision folded into `P2.DECOMP`'s plan (2026-08-19). _The review decides whether
  this lands as a new `architecture`/`backend` doc or as a decision entry — the phase's later slices
  will add the concrete schema and job topology to the same note._
- **`architecture`** (same note as above) / **`data`** — **collection schema landed (P2.S1):**
  `corp → event → filing_version → snapshot`, event key `(corp_code, report_subtype,
  original_rcept_dt)`, every observed `rcept_no` a version (`original`/`기재정정`/`첨부정정`), every
  version snapshotted with its raw body (JSONB for API responses, BYTEA for 본문 ZIPs) and a
  `content_sha1` that makes re-collection idempotent; excluded events are retained with a
  `suppressed_reason` rather than dropped. Package is `src/mijual` (SQLAlchemy 2 + psycopg3, Postgres
  in docker on host 5433; Redis reserved for S6 on 6380). **P2 runs without Alembic on purpose** —
  `create_all`/drop-and-recreate, since all data is re-collectable. Source: `P2.S1` result
  (2026-08-19).
- **`data`** — **collection method landed (P2.S2), and two corrections to `data.md`'s collection
  section:** (a) the 정정 pairing method's fallback arm is "nearest earlier **original**" (not nearest
  earlier filing — a chain would otherwise split into one event per correction), with a corp-scoped
  `list.json` widening (no 3-month cap) and an explicit `pairing_method` per version; (b) **the event
  key `(corp_code, report_subtype, original_rcept_dt)` is not injective** — ~8% of 2026 events collide
  (same-day double filings, and concurrent events of one corp), so the documented key needs the caveat
  plus the detector (2+ detail rows on one key) and the rule *never suppress an event whose detail rows
  disagree*. Also record: excluded events are retained with `suppressed_reason` ∈ {`no_warrant_class`,
  `no_appraisal_right`, `unpaired_correction`, `superseded_by_pairing`}; discovery covers
  originals + `[기재정정]` + `[첨부정정]` + `[첨부추가]` + `[정정명령부과]`; **O-4 is closed — KONEX adds
  zero exposable rights** (26-request probe), so KOSPI+KOSDAQ remains the frame. Source: `P2.S2` result
  (2026-08-19).
- **`operations`** — **collection is bounded by an explicit request ceiling** (`DartClient
  max_requests` → `RequestBudgetExceeded`; a run stops cleanly and keeps what it collected) because the
  daily OpenDART quota is unmeasured (O-1); and **re-collecting a window is nearly free** — the second
  live pass over the same window added zero events and zero versions and cost 25 requests, which is the
  property the scheduled job (S6) relies on. Source: `P2.S2` result (2026-08-19).

## Open Questions

- **O-1 (blocks `P2.S7`'s backfill):** ▷ the published **daily OpenDART call quota is unmeasured** —
  1,002 distinct requests in one P1 session drew no quota error, but the ② backfill is another
  ~300–600. **Measure or confirm the cap before running it**, and raise it with the operator early
  (N10).
- **O-2 (blocks `P2.S4`):** the Gemini **"changple5" credential is not in this repo** and must be
  obtained from the operator, stored gitignored beside `DART_API_KEY`, never echoed — and the **exact
  API model id** for "Gemini 3.7 Flash (high)" must be confirmed at integration time (D-4 says model
  naming is the operator's call). Raise early (N10).
- **O-3 (`P2.S9`):** the ~100-filing hand-labelling is **operator co-work** — expect a real `pending`
  gate. Decide the labelling format and the per-field precision definition before asking for the
  operator's time.
- ~~**O-4:**~~ **CLOSED by `P2.S2` (N24).** KONEX (`corp_cls=N`), 2026-01-01~08-19: 30 events, **0
  exposable rights** → no coverage conclusion changes; KOSPI+KOSDAQ stays the frame. `corp_cls=E`
  (기타) was not probed and is judged not worth the requests.
- **O-5 (now one filing away):** ▷ whether `주주우선공모증자` issues a 신주인수권증서 — the single case
  (`20260807000339`, corp `00232007`) is **collected and unsuppressed** in the database, so S3 closes
  this by reading its 본문 `18. 신주인수권양도여부`. Until then that 증자방식 is kept (not suppressed).
- **O-6:** ▷ meaning of `estkRs.일반사항.exstk/exprc/expd` (2/35 filled) — not needed by any MVP field;
  answer only if it falls out for free.
- **O-7 (carried from P1 as Q7, deferred to P2/P3):** 증권사 MTS 권리 메뉴 coverage matrix (handoff §4,
  "미발견 ≠ 부존재") — differentiation evidence for the 기획서, not pipeline code. Must not be
  forgotten; a `defer-job` is the right home if no slice absorbs it.
