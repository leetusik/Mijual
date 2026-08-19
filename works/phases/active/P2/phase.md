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

### Appended by `P2.S3` (2026-08-19)

**N27 — `create_all` cannot add a COLUMN, and after S2 a `reset_schema` is no longer free.** N16's
"just edit `models.py` and re-run" works for a *table*; a new column on a populated table is
invisible to `create_all`, so the only N16 move would have been dropping the corpus that cost 291
live requests against an unmeasured quota (O-1). `mijual.db.schema_sync.ensure_columns(engine,
Base)` closes exactly that gap: it **adds** declared-but-missing **nullable, default-free** columns
via `ALTER TABLE … ADD COLUMN`, is idempotent, is a no-op on a fresh `create_all` database, and
raises on anything else. It is deliberately **not** a migration tool — no version table, no
history, no type changes, no drops — so N16 stands: a change bigger than an additive nullable
column is still the signal to reset (or to revisit N16 in P3).

**N28 — the 유상증자결정 본문 is not one form, it is a form *family*, and the difference is itself the
① filter.** Measured over 312 `piicDecsn` 본문 now held: **94 carry `18. 신주인수권양도여부`, and all
94 yield 10/10 of the field-matrix §1.3 target labels** (P1 measured 9/9; this is the same result
at 10× the sample). The other 218 use a different numbered template — 제3자배정 runs
`8. 제3자배정에 대한 정관의 근거 / 9. 납입일 / 12. 신주의 상장 예정일`, 주주우선공모 runs
`10. 청약예정일 / 11. 납입일 / 14. 신주의 상장 예정일` — with **no 신주인수권 rows at all**. So
"label `18.` is absent" is not a parse failure, it is evidence: **the form the filer used already
says whether a 증서 exists.** Any later reader must treat an absent `18.` as a negative, not as a gap.

**N29 — the `<CORRECTION>` header is not 100 % at scale, and the markup has two traps.** Over 360
`<CORRECTION>` blocks: **354 (98.3 %) carry `2. 최초제출일`; 6 state no date at all** (P1's 40/40 was
a small sample). 1,450 정정사항 rows parsed. Two markup facts must be got right or nothing parses:
(a) `<TABLE\b` also matches DART's `<TABLE-GROUP>` wrapper, which desynchronises table nesting and
makes a whole body look like one unclosed table — the pattern must be `<TABLE(?![-\w])`; (b) value
cells are `TE` / `TU`, **not** `TD`/`TH` (the spike's `T[DH]` regex silently dropped every value in
the form), and `TU` carries DART's own machine value in `AUNIT` + `AUNITVALUE`
(`AUNIT="ALL_BS_DT" AUNITVALUE="20260728"`, `AUNIT="NST_GV_YN" AUNITVALUE="Y"`), verified stable
across every ① filing that has the row. Also: the ① form leans on `ROWSPAN` hard enough that
`11. 청약예정일`'s value rows carry **no** label cell, so a ROWSPAN/COLSPAN grid expansion is
mandatory, not a nicety.

**N30 — a 주주배정 유증 CAN say `18. 신주인수권양도여부 = 아니오`, and that is the case the whole 본문
check exists for.** 제이알글로벌리츠 `01415892` (`20260205000605`): `ic_mthn = 주주배정후 실권주
일반공모` while 본문 `18.` reads `아니오` and `- 신주인수권증서의 상장여부` reads `아니오`. Publishing on
`ic_mthn` alone would have advertised a 증서 that does not exist. Per the plan and N20 it is **kept
live and flagged `warrant_conflict`**, never suppressed on conflicting evidence — but the honest
reading is that no tradeable 증서 exists, so **`P2.S5` (the gate layer) owns the exposure decision
for `warrant_conflict`**, and it should almost certainly block. Do not let this one sit unresolved
into S8/S9.

**N31 — the 본문 hint settles pairing far more often than it breaks it, and the failures are mostly
date skew.** Backfill over 360 parsed 정정: 143 `confirmed`, 20 `reattached` (the version moved to
the event the hint names), 63 `identified` (a placeholder whose original genuinely predates the
collection window — identity now known), 22 `duplicate` (N21's residue: the twin already holds the
`rcept_no`), 106 `mismatch`, 6 `absent`. **Of the mismatches, ~half sit within ±7 days of the
attached event's original 접수일** (접수일/결의일 skew, pairing almost certainly right) and only 4 are
>1 year stale — P1's `20260429000902`-declares-2022 pattern is rare, not typical. Worklist effect:
`*_ambiguous` 145 → **66**, `unpaired_correction` 99 → 99 but **46 identified**, exposable events
53 → **44**. Scheme to reuse: `pairing_method` keeps exactly what S2 wrote and `hint_status` +
`pairing_note` carry the 본문's verdict — evidence relabelled, never overwritten. Verified: exactly
20 versions changed `event_id` against a pre-S3 `pg_dump`, **0 rows removed, 0 added**.

**N32 — N20(b) is now proven in the data, and the hint is the splitter.** 9 of the 36
`event_key_collision` events carry **`hint_split_evidence`**: their versions' 본문 최초제출일 values
disagree, so the key really does hold 2+ events. 이렘 `00116426/piicDecsn/2026-02-04` holds
**three** chains (hints 2026-02-04, 2025-04-21, 2026-04-24). S3 re-attaches a version only when
the hint names an **existing** event (10 events lost a version that way, flag `hint_split`);
minting an event whose original filing was never collected is a *collector* decision, not a
parser's, so the rest is flagged for `P2.S5` or a wider re-collection.

**N33 — citation spans are real, cheap, and already verified at scale; S4/S5 must not re-invent
them.** `mijual.bodydoc` returns every value with a `Span` into the decoded XML **as the snapshot
stores it**, and `BodyDocument.verify(span, value)` is the exact predicate S5's *원문 인용 스팬 존재*
gate should call (normalized equality — the raw slice legitimately still contains markup).
Measured: **23,493 / 23,493** extracted values re-slice to themselves across the 364 documents
held, 4,538/4,538 over the P1 fixture cache. Offset preservation is an `array('i')` map built in
one pass, so a 3.4 M-char 증권신고서 costs ~27 MB — but **slice it by `<TITLE>` section first**
(`sections()` / `find_sections()`): 3.4 M chars → a 33,780-char 청약절차 section, 9.5 M → a
38,033-char 매수청구권 section, and the slices tile the document so offsets stay valid.

**N34 — S3's whole persisted outcome is reproducible from the on-disk caches at 0 requests.**
Proven by dropping the database to a pre-S3 `pg_dump` and rebuilding it with two offline
`backfill` passes (P1 spike cache read-only, then `var/dart-cache`) plus two offline `warrants`
passes: the rebuild converged to the same state **and improved on it**, attaching 28 documents the
budget-interrupted live runs had fetched-and-cached but never persisted. Practical rule for S4+:
after a budget-capped live run, always finish with an offline pass over the cache before reading
the numbers.

### Appended by `P2.S4` (2026-08-19/20)

**N35 — the Gemini integration facts, measured, not assumed.** Model id **`gemini-3.7-flash`** is
real and reachable on the operator's credential (`models.get` → version `3.7-flash-08-2026`, 1M
input / 64k output, 50 models visible). **The project preset applies a thinking level**: a probe
call with **no** thinking config returned `thoughts_token_count=423` on a trivial prompt (565 on a
small extraction, ~1.2k on a real one), so nothing in the code configures thinking — passing a level
would silently override an operator-side decision (D-4). Structured output works through
`response_json_schema`, **including union types (`["string","null"]`) and `enum` with `null`**, which
is what lets a value schema say "not stated" instead of inventing a value. ▷ Rate card used for every
cost figure in this phase: **$0.75 / $3.75 per 1M input / output tokens** (introductory through
2026-12-31; $1.50 / $7.50 after), thinking tokens billed as output. Costs are **estimates**; token
counts are measurements.

**N36 — group the call by document, not by field: it is the slice's main cost lever.** All five ①
prose fields live in the same `24. 기타 투자판단에 참고할 사항` block of a 2.6k–10k-char document, so
one call reads all five. Per-field calls would have been **140 for ① alone** — most of the whole
slice ceiling — to read the same text five times. The *response* stays one envelope per field
(`present`/`value`/`quote`/`note`) and every stored row is per field, so nothing is lost. Whole-run
effect: **100 calls, 983,529 tokens, ▷ $1.41** for 40 events.

**N37 — the span is located, never trusted, and locating is free to redo.** The model returns a
verbatim quote; `mijual.extract.locate` finds it in the stored snapshot through bodydoc's offset map
(N33). **292 of 293 quotes located (99.7 %)**: 290 `exact` (so `doc.verify` is True), 2 after
dropping a leading list marker the model re-rendered (`①` → `1)`), 1 **unresolved** — LB세미콘
`20260730000278`, where the model **stitched three formulas from different paragraphs** into one
quote. Each fragment is real; the concatenation is not in the document, so it is not a citation and
is stored `span_unresolved` for the gate to block. Because location is a pure function of (quote,
snapshot), `python -m mijual.extract relocate` re-derives every span for **0 calls** — improving the
locator must never mean paying for the extraction again, and a re-collected snapshot that moved under
a stored span makes its quote stop locating instead of pointing at the wrong characters.

**N38 — never put the gate's reference value in the prompt.** §7's gate for 청약 취급처 is *"청약일
must equal 본문 11. 청약예정일"*. Feeding 본문 11's parsed value into the prompt as "context" would let
the model copy the answer, and the gate would then be checking the prompt against itself. So the
extraction prompt carries **only the document**: no API values, no label values, no expected
schedule. The deterministic layer stays the independent witness. (The 정정 prompt is the deliberate
exception — there the deterministic 정정사항 rows are supplied **as ground truth to be normalised**,
and the code checks the model against them.)

**N39 — 철회 is invisible to the deterministic layer, and two exposable ① events are already
withdrawn. `P2.S5` must fix this.** 썸에이지 `20260805000454` (`warrant_confirmed`) and
제이알글로벌리츠 `20260205000605` (`warrant_conflict`) each file a ~1.9k-char `[기재정정]` whose
정정사항 table holds **one row — 항목 `유상증자 결정`, 정정 전 `유상증자 결정`, 정정 후 `유상증자
철회`** — and whose prose reads `부득이하게 금번 유상증자를 철회하기로 결정하였습니다`. Their label
table still parses **10/10**, so S3's ① filter sees a healthy event; only the extractor returning
`present=false` on all five fields surfaced it. **Publishing 썸에이지 today would advertise a
매매기간 that has been cancelled.** The detector is deterministic and cheap (that single 정정사항
row) and belongs in the gate layer, not in the LLM. A naive `"철회" in 본문` test does **not** work:
it also fires on 증권신고서 boilerplate (2 further ① events) and on 매수청구 boilerplate (7 of 15 ③).

**N40 — `추후결정` is a third field state, not a missing value.** 경남제약 `20260623000409` and
에이전트AI `20260619000455` are 정정 filings that suspended the entire schedule (`3) 신주인수권증서
상장예정기간 : 추후결정`, `청약일 추후결정`). Those extractions are `status='extracted'` with a
located, **verified** span and **all dates `null`** — deliberately not `absent`, because the document
does say something. The gate and the board must distinguish "no date yet" / "field absent" / "stale
date", and must never fall back to the superseded schedule.

**N41 — in a 정정, the deterministic rows are ground truth and the model only normalises.** Each
interpretation is built from (a) bodydoc's `3. 정정사항` before/after rows and (b) a value diff this
package computes in Python between the two versions' extractions; the model returns normalised
changes + schedule impact, and `check_against_items` scores it. Measured over **30 interpretations**:
137 deterministic rows in, **121 model changes with 0 unsupported**, **20 rows uncovered** (mostly
the two 13-row 합병 corrections, where near-duplicate rows were merged), 95 prose value moves,
**121/121 per-change quotes located**. The uncovered count is stored per record, so `P2.S9` gets a
recall measurement for free.

**N42 — the extraction schema, and the room left for `P2.S5`.** Two tables in `db/models.py`:
`extraction_call` (one row per call — model, prompt/schema version, input scope + chars, prompt /
thinking / output tokens, ▷ cost, latency, and the raw payload as evidence) and `extraction` (one row
per field, keyed **`(filing_version_id, field_key, schema_version)`** — value JSON, verbatim quote,
located span + `span_status` / `locate_method` / `span_verified`, snapshot FK, model note). That
identity is what makes a re-run **cost zero calls and never duplicate a row**, while a
`schema_version` bump records a new reading beside the old one. `gate_status` / `gate_reason_code` /
`gate_note` / `gate_checked_at` are declared nullable and unused — S5 fills them, and a re-extraction
clears them (a verdict judges a value, and the value just changed).

**N43 — what the corpus actually yields today** (current version of each event, 0 OpenDART requests):
① **25 of 29** events carry a citable 신주인수권증서 매매기간 (2 철회, 2 `추후결정`), 27/29 for
청약 취급처 · 실권주 · 초과청약, 26/29 for 발행가 산식; ③ **10 of 11** events with a 본문 carry the
반대의사 절차 (아시아나항공 `20260713000482` states the right but not the procedure), and **4 of the
15 ③ events — all SPAC 합병 — hold no 본문 at all**. For those five the 증권신고서 is the only
remaining source, and collecting it is collector-side work (a 증권신고서 is a *different* filing, not
a version of these events), so `mijual.extract.inputs` implements and tests the §5 section-slicing
path but no run needed it.

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

- **`data`** — **본문 (deterministic) layer landed (P2.S3), and three corrections/additions to
  `data.md`'s three-tier field model:** (a) the `본문-label` tier is now a measured, span-carrying
  parse — **94/94 of the 주주배정 계열 유상증자결정 본문 yield all 10 §1.3 target labels** and every
  extracted value carries a character span into the stored snapshot (**23,493/23,493 verified**),
  which is the mechanism §3.6 layer 2's *원문 인용 스팬 존재* gate will call; (b) the 유상증자결정
  본문 is a **form family, not one form** — 제3자배정 / 일반공모 / 주주우선공모 use templates with **no
  신주인수권 rows at all**, so an absent `18. 신주인수권양도여부` is *evidence of no 증서*, not a data
  gap; (c) the `<CORRECTION>` `2. 최초제출일` hint is recovered in **354/360 = 98.3 %** of blocks (P1's
  40/40 was a small sample) and 1,450 `3. 정정사항` rows parse. Also record the 증권신고서 rule as
  implemented: it is **sliced by `<TITLE>` section and never read whole** (3.4 M chars → a
  33,780-char 청약절차 section; 9.5 M → a 38,033-char 매수청구권 section). Source: `P2.S3` result
  (2026-08-19).
- **`decisions`** / **`data`** — **O-5 CLOSED: `주주우선공모증자` issues no 신주인수권증서**, so the ①
  rights universe is `주주배정후 실권주 일반공모` + `주주배정증자` only. Evidence: the corpus's single
  case (상지건설 `00232007`, 정정 `20260807000339`) uses a form with no `18. 신주인수권양도여부` row and
  the string `신주인수권` occurs **0 times** in its 33,886-char 본문 (▷ the class generalisation rests
  on the form template, not on a sample of one). Consequence for the documented filter:
  `WARRANT_BEARING_IC_MTHN` drops that value, and a new suppression reason **`no_warrant_bodymun`**
  joins the reason-code list (9 events, 8 of them `P2.S2`'s previously *undecided* ①). Also record
  the invariant this proves: **`ic_mthn` never confirms a right — 본문 `18.` is the final test**, and
  when the two disagree the event stays live with a `warrant_conflict` flag (1 case,
  제이알글로벌리츠 `01415892`) for the gate layer to decide. Source: `P2.S3` result (2026-08-19).
- **`architecture`** (same note as the S1/S2 entries) / **`operations`** — **the pairing method now
  has a second, documented arm, and the schema evolves additively:** the 정정 pairing method is
  `(P2.S2 nearest-earlier-original) + (P2.S3 본문 <CORRECTION> 최초제출일 verdict)`, stored as the pair
  `(FilingVersion.pairing_method, FilingVersion.hint_status)` with a `pairing_note` audit line —
  S2's value is never overwritten. Measured effect: `*_ambiguous` 145 → 66, 46 of 99 unpaired
  corrections identified, 9 collided event keys proven to hold 2+ events, exposable events 53 → 44.
  Operationally: **P2 still has no Alembic (N16), but `create_all` cannot add a column**, so
  additive nullable columns land through `mijual.db.schema_sync.ensure_columns` (add-only,
  idempotent, refuses anything else) rather than a corpus-destroying `reset_schema`; and a
  budget-capped live run must be followed by an offline pass over the response cache before its
  numbers are read (S3's live runs left 28 fetched-and-cached documents unpersisted).
  Source: `P2.S3` result (2026-08-19).

- **`architecture`** (same note as the S1/S2/S3 entries) / **`data`** — **the extraction layer landed
  (P2.S4), and it is the first place §3.6's layer 1 exists in code:** `mijual.extract` reads **only**
  field-matrix §7's 10 prose targets (the registry is a closed list and a test asserts it stays
  disjoint from the `본문-label` field set), asks the model for a value **plus a verbatim quote**, and
  then **locates the span itself** in the stored snapshot — *no span is ever taken from the model*;
  an unlocatable quote is stored `span_unresolved` and the gate blocks it. Storage: `extraction_call`
  (per call — model, prompt/schema version, input scope, prompt/thinking/output tokens, ▷ cost, raw
  payload) + `extraction` (per field, keyed `(filing_version_id, field_key, schema_version)`, with
  `gate_*` columns reserved for `P2.S5`), so a re-run costs **0 calls** and never duplicates a row.
  Input regime as implemented: 주요사항보고서 whole (≤ 25k normalized chars), a 100k–180k-char 합병
  본문 **windowed** around the field anchor, a 증권신고서 **only** as a `<TITLE>` section — never
  whole. Source: `P2.S4` result (2026-08-19/20).
- **`data`** — **first measured layer-1 accuracy/coverage, and two document states the field model did
  not have:** over the exposable corpus (40 events, 304 extraction rows) **292 of 293 model quotes
  located in the stored snapshot (99.7 %, 290 of them byte-faithful)**; per event's current version
  ① **25/29** carry a citable 신주인수권증서 매매기간, 27/29 청약 취급처 · 실권주 · 초과청약, 26/29
  발행가 산식, ③ **10/11** with a 본문 carry the 반대의사 절차 (4 further ③ SPAC 합병 events hold **no
  본문 at all**). Two states must enter the documented field model: **철회** — a 유상증자 withdrawn by
  a later 정정, invisible to the label layer (its table still reads 10/10) and detectable
  deterministically from the single 정정사항 row `유상증자 결정 → 유상증자 철회`, 2 currently-exposable
  ① events affected — and **`추후결정`** — a schedule suspended by a 정정, which is an *extracted*
  value with a verified span and null dates, not a missing field. Source: `P2.S4` result
  (2026-08-19/20), findings N39/N40.
- **`decisions`** / **`operations`** — **D-4 concretised, and LLM spend is bounded structurally:**
  the reading model is **`gemini-3.7-flash`** on the operator's credential with the **thinking level
  left to the project-side preset** (measured, not configured — a no-config probe returns thought
  tokens); calls are grouped **one per document, not per field** (five ① fields in one call: 28 calls
  instead of 140); `GeminiClient(max_calls=…)` refuses the call past the ceiling exactly as
  `DartClient(max_requests=…)` does for quota; every run reports calls / tokens / **▷ estimated cost**
  from a published rate card ($0.75 / $3.75 per 1M in/out, thinking billed as output) and never claims
  a billed figure. Whole-slice spend: **100 calls, 983,529 tokens, ▷ $1.41, 0 failures, 0 OpenDART
  requests**. Re-running is free (already-stored fields are skipped) and **span re-resolution is a
  separate 0-call pass**, so improving the locator never re-pays for extraction. Source: `P2.S4`
  result (2026-08-19/20).

## Open Questions

- ~~**O-1:**~~ **CLOSED by the operator (2026-08-19), recorded at `P2.S4`.** The **daily OpenDART
  quota is 20,000 requests per key** (operator statement, corroborated by community documentation;
  ▷ the official page defers to a homepage notice, so this is authoritative-by-operator rather than
  scraped). P2's spend to date is ~1,600 requests total (P1 ~1,002 + S2 291 + S3 289 + S4 **0**), so
  `P2.S7`'s ~300–600-request backfill is comfortably inside one day. **The `DartClient
  max_requests` ceiling stays** as good practice (N25) — a known cap is not a reason to run unbounded.
- ~~**O-2:**~~ **CLOSED by `P2.S4` (N35).** `GEMINI_API_KEY` (the "changple5" credential) is in the
  gitignored repo-root `.env` and reaches only the SDK; **model id `gemini-3.7-flash`** is confirmed
  present on the credential (`models.get` → `3.7-flash-08-2026`); and the **thinking level is a
  project-side preset** — a no-config probe returned 423 thought tokens — so no thinking config is
  hardcoded anywhere. ▷ Cost basis recorded: $0.75 / $3.75 per 1M in/out tokens.
- **O-9 (new, `P2.S5`, countdown-critical):** **what does a 철회 (withdrawn) 유상증자 do to exposure,
  and who detects it?** Two currently-exposable ① events are already withdrawn and the deterministic
  ① filter cannot see it (N39). The signal is one 정정사항 row (`유상증자 결정` → `유상증자 철회`) and
  the detector belongs in the gate layer. The companion question — how `추후결정` (schedule suspended,
  N40) is shown — is the same decision in a softer form: neither may fall back to the superseded
  schedule. Must not reach `P2.S8`/`P2.S9` unresolved.
- **O-3 (`P2.S9`):** the ~100-filing hand-labelling is **operator co-work** — expect a real `pending`
  gate. Decide the labelling format and the per-field precision definition before asking for the
  operator's time.
- ~~**O-4:**~~ **CLOSED by `P2.S2` (N24).** KONEX (`corp_cls=N`), 2026-01-01~08-19: 30 events, **0
  exposable rights** → no coverage conclusion changes; KOSPI+KOSDAQ stays the frame. `corp_cls=E`
  (기타) was not probed and is judged not worth the requests.
- ~~**O-5:**~~ **CLOSED by `P2.S3` (N28, Doc impact).** `주주우선공모증자` **does not** issue a
  신주인수권증서: the single case (상지건설 `00232007`, 정정 `20260807000339`) uses a 유상증자결정 form
  with **no `18. 신주인수권양도여부` row**, and `신주인수권` occurs **0 times** in its 33,886-char 본문.
  The value was removed from `WARRANT_BEARING_IC_MTHN` and the event is suppressed
  `no_warrant_bodymun`. ▷ Evidence is one filing; the generalisation rests on the form template,
  and the per-document 본문 check would surface a counter-example as a `warrant_conflict`.
- **O-8 (new, `P2.S5`):** the one **`warrant_conflict`** event — 제이알글로벌리츠 `01415892`,
  `ic_mthn = 주주배정후 실권주 일반공모` vs 본문 `18. 신주인수권양도여부 = 아니오` — is **kept live and
  flagged** because the phase rule forbids suppressing on conflicting evidence. The gate layer (or
  the operator) must decide whether `warrant_conflict` blocks exposure; the honest reading of the
  본문 is that no tradeable 증서 exists. See N30 — do not let it reach `P2.S8`/`P2.S9` unresolved.
  **Update (`P2.S4`, N39): that same filing is a 철회** — its 정정사항 table reads `유상증자 결정` →
  `유상증자 철회` and the extractor found all five prose fields absent — so in practice the conflict is
  moot and O-9's 철회 rule decides it; the formal `warrant_conflict` policy is still S5's to state.
- **O-6:** ▷ meaning of `estkRs.일반사항.exstk/exprc/expd` (2/35 filled) — not needed by any MVP field;
  answer only if it falls out for free.
- **O-7 (carried from P1 as Q7, deferred to P2/P3):** 증권사 MTS 권리 메뉴 coverage matrix (handoff §4,
  "미발견 ≠ 부존재") — differentiation evidence for the 기획서, not pipeline code. Must not be
  forgotten; a `defer-job` is the right home if no slice absorbs it.
