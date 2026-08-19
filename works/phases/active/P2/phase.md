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

### Appended by `P2.S5` (2026-08-20)

**N44 — the gate verdict has FOUR states, and the fourth is what keeps the trust claim honest.**
`passed` / `failed(reason)` / `tbd` / `not_evaluable(reason)`, written to
`Extraction.gate_status` / `gate_reason_code` / `gate_note` / `gate_checked_at`; only `passed` and
`tbd` are ever shown. The mechanism matters as much as the vocabulary: a gate is a **list of named
`Check`s** and the verdict is *derived* — a check whose reference value does not exist is
**skipped, never passed**, and a gate all of whose checks were skipped is `not_evaluable`, because
a gate that compared nothing has not vouched for anything. `gate_note` carries the whole list
(`citation=ok(verified) date_order=ok(…) after_record_date=ok(> 2026-07-28) …`), so every verdict
is auditable without re-running it. Conservative default everywhere: `not_evaluable` is **not
exposed**.

**N45 — §7's gate column is a specification written before the corpus was measured, and three of
the ten rows needed the data to settle them.** Do not re-litigate these; the measurements are in
`P2.S5`'s result.
(a) **#2 청약 취급처** — 55 우리사주조합/구주주 entries match 본문 `11.` **exactly, 0 mismatches**, but
**23 일반공모 entries have no `11.` row at all**: the 실권주 일반공모 청약 is a *later, separate*
window (계양전기 구주주 09-03~09-04 vs 일반공모 09-08~09-09). Equality would have failed 23 correct
fields, so those are gated on **ordering** (must start after the 구주주 청약 closes).
(b) **#5 발행가 산식** — 본문 `6. 확정예정일` is the day the price is **결정**되고, the prose names the
day it is **공시**된다: over 19 comparable ① filings **16 agree and 3 differ by exactly +1 day**
(계양전기, HLB제약, SG). The gate is therefore a **window** `[본문 6. 확정예정일, 첫 청약일]`, not an
equality. The MAX(…) operands §7 names are 가중산술평균주가 — market data this repo does not hold —
so what is checked is the *shape* (확정 산식 present, 할인율 a fraction) plus that schedule window.
(c) **#4 초과청약** — a filing states a **ratio**, never a holder's 배정주식수, so §7's
*배정주식수 × ratio* arithmetic cannot be a document check. It lives in
`mijual.calc.excess_subscription_cap` (unit-tested, P3's calculator) and the gate checks the
normalized ratio against the ratio the **cited text** states (`1주당 0.2주` / `20%`) — 27/27 agree,
and it catches the real failure mode of a normalized number, a unit slip.

**N46 — the stored API detail row is a reference value for the CURRENT version and for no other.**
N2 said the detail endpoints return one row per event, newest only; the consequence for layer 2 is
that comparing a **superseded** 본문 against today's API row measures the *correction*, not the
reading. The first gate run failed 3 ③ rows exactly that way (로젠, 알에프텍, 모다이노칩 —
all previous versions). `VersionContext.api_value()` is now version-scoped and those rows read
`not_evaluable(superseded_api_reference)`. Any later API-backed check (gates 6–8, ②) inherits it.
With the scoping in place: **9/9 current-version ③ rows equal `mgsc_mgop_rcpd_bgd/_edd` exactly.**

**N47 — the 철회 detector is a ROW-SHAPE test, and the corpus says there are FOUR withdrawals, not
two.** Over **1,282 정정사항 rows in 328 distinct 본문 documents**, `철회` appears in the 정정 후 cell
of **14 rows and only 4 are withdrawals** — a 71 % false-positive rate for the obvious keyword test
(N39's warning, now quantified). The rules: 정정 후 ≤ 30 squashed chars, the cell **ends** with 철회,
the 항목 carries **no form number**, and the subject either restates 정정 전 or names a filing-level
decision. On this corpus the length bound alone is exact. Findings: 썸에이지 `20260805000454` and
제이알글로벌리츠 `20260205000605` (both were exposable — now `withdrawn`), plus **디모아
`20260625000227`** and **코퍼스코리아 `20260130000680`**, which sit on already-suppressed
`unpaired_correction` placeholders and change no exposure. **코퍼스코리아 is the reason the subject
rule is not just "restates 정정 전"**: its 항목 is the bare `전 항목` and its 정정 전 is `-`, so the
first draft missed it silently. ③/② generalise on shape (`회사합병 결정 → 회사합병 철회` passes,
unit-tested) but **no ③/② case exists in this corpus** — untested against real data, say so.

**N48 — the exposure contract is one derivation and P3 must never re-implement it.**
`mijual.gates.exposure`: an **event** is exposable iff not suppressed, not withdrawn, and carrying
no identity/rights conflict flag (`warrant_conflict`, `detail_conflict`, `event_key_collision`,
`hint_split_evidence`); a **field** iff its gate said `passed` (show the value) or `tbd` (show
`추후결정` — `FieldView.value` is `None` there **by design**, so a superseded date cannot leak). The
two are independent; `EventExposure.renderable_fields` is the only thing that combines them.
Persisted on `Event.exposure_state/_reason/_note/_checked_at` (four additive nullable columns via
`ensure_columns`, N27) so P3 can filter in SQL and make **no OpenDART call in the request path**.
Side effect worth keeping: blocking 이렘's flagged twin makes the board show that `rcept_no` **once**
instead of twice (N21's residue).

**N49 — what the product may actually show today** (0 requests, 0 calls, regenerated from the DB):
**35 of 44 events exposable — ① 25/29** (2 철회, 2 flagged) **and ③ 10/15** (1 flagged, 4 with no
본문) — carrying **157 renderable field instances**. Per field on an exposable event:
매매기간 25 (**23 live + 2 추후결정**), 청약 취급처 25 (2 추후결정), 초과청약 25, 정정 해석 26,
실권주 24, 발행가 산식 24, 반대의사 8. Blocked: `detail_conflict` 3, `withdrawn` 2, `no_document` 4.
Field-level: **275 passed / 4 tbd / 5 failed / 20 not_evaluable** over 304 rows.

**N50 — every displayed number now comes from one deterministic module (`mijual.calc`), and S8
inherits it.** `d_day` (KST, `D-3`/`D-DAY`/`D+2`, `None` in → `None` out), `window_state`
(**inclusive at both ends** — the last 청약일 is still a 청약일), `allotted_shares` /
`excess_subscription_cap` (Decimal × floored 단수주 절사), and
`lapsed_warrant_value(주수, 배정비율, 증서가치)` → Decimal 원, rounded **once** at the end. §3.6's
*계산은 결정론* clause in code; no LLM, no clock unless one is passed.

**N51 — three exposable-quality ① / ③ events are blocked on IDENTITY, not on their content**, and
unblocking them is collector-side work: 한솔테크닉스 (a real 주주배정 유증), 이렘, 모다이노칩's 로젠
chain, all `detail_conflict` + `event_key_collision`. S3 already stored the 본문 `최초제출일` hints
that would split those keys (`hint_split_evidence`); minting the missing events is a *collector*
decision (N32), so it is handed forward — a good `defer-job` candidate worth ~1 event of
judging-window value per collided key.

### Appended by `P2.S6` (2026-08-20)

**N52 — the pipeline is now a job, and the topology is fixed: `collect → bodydoc → extract →
gates`.** `mijual.scheduler` wraps the four stages' *run functions* (imports, never subprocesses) as
five Celery tasks — `mijual.daily_pipeline` plus one per stage (`mijual.collect_recent`,
`mijual.bodydoc_sync`, `mijual.extract_new`, `mijual.gates_run`) — on the Redis `compose.yaml`
already reserved (host **6380**, `scheduling` profile, broker + result backend + lock store). Beat
runs `daily_pipeline` at **07:30** (before the open) and **19:30 KST** (after 공시 접수 closes at
18:00) over a rolling **14-day** window, plus a **Sunday 04:30, 90-day** straggler pass. Timezone is
**`Asia/Seoul` with `enable_utc=False`**, and the window is anchored on `mijual.calc.today_kst`, not
on the host clock — a worker in UTC must not poll yesterday's Korean calendar day. Order is a data
dependency, not a preference (each stage consumes what the previous one persisted), so
`daily_pipeline` runs the four **in-process in order** rather than as a Celery `chain`: one lock has
to span the whole run. `BEAT_SCHEDULE` is a plain dict — **`P2.S7` adds its ② task and one entry
beside these**, and should pass `extract_rights` nothing (② needs zero LLM, N6).

**N53 — repetition is safe, overlap is not, and that is the whole reason there is a lock.** N14/N25
proved a re-run adds nothing and costs almost nothing; two *concurrent* runs are a different failure
— both see "no 본문 held for this version yet" and both fetch it, and spent quota is the one thing an
idempotent upsert cannot repair. So every corpus-writing entry point (the pipeline task, each stage
task, and the inline `once`) takes the **same** lock `mijual:lock:pipeline`: Redis `SET NX PX`
released by **compare-and-delete** (a run that overran its TTL must not delete its successor's lock),
degrading to a single-host `O_EXCL` file lock under `var/locks/` when no broker answers, with an
expired lock stolen and the steal reported. A run that cannot take it returns **`skipped`** — it does
not wait and does not run anyway. Measured live: two `daily_pipeline` tasks dispatched together on a
2-slot worker, one ran, the other returned `skipped: true, requests: 0, calls: 0`.

**N54 — measured steady-state cost of a scheduled run, and where it actually goes.** A live 3-day
window cost **19 requests** (54 list rows → 23 targets → 1 new event) and **0 LLM calls**: extraction
skips every version whose fields are already stored (N42), so the daily marginal LLM cost is normally
**zero** and only genuinely new prose is paid for. The stage that keeps spending is **bodydoc** — the
`<CORRECTION>` backfill still has a queue (403 of 803 candidates parsed after this slice, up from
360) and drains at its `bodydoc_max_documents` cap per run, 40 requests at a time. Budgets are
explicit per stage (daily: collect ≤ 500 req, bodydoc ≤ 200 req, extract ≤ 60 calls; weekly 1500 /
600 / 60) and exhaustion is a **reported status, not an exception** — demonstrated with a 3-request
ceiling: `본문 +3 | 3 req — BUDGET EXHAUSTED`, exit 0, chain continued.

**N55 — N47's "4 withdrawals" is a floor measured on the documents then held, not a property of the
corpus.** The scheduled 본문 backfill drained 43 more documents and the same unchanged detector found
**two more real withdrawals** — 베노티앤알 `20260211001005` and 앱튼 `20260213002873`, both with 항목
`-` and a 정정 후 naming the filing-level decision (the 코퍼스코리아 shape). Distinct withdrawn
filings **4 → 6**; both sit on `unpaired_correction` placeholders, so exposure did not move (35
exposable events / 157 renderable fields / 275-4-5-20 field verdicts, all unchanged). Two
consequences: (a) any 철회 count must be quoted **with the document coverage it was measured at**, and
`P2.S9`'s evalset should draw after a backfill pass, not before; (b) the gate report counts **flagged
events**, and one withdrawn `rcept_no` can sit under two event keys (N21's residue), so 7 flagged
events = 6 distinct filings.

**N56 — `python -m mijual.scheduler once` is the reusable path, and it is broker-free.** The same
`run_pipeline()` the tasks call, synchronously: `--offline` runs all four stages at **0 requests / 0
calls** (extraction builds every prompt and sends none) and two consecutive runs print byte-identical
stage lines; `--stages`, `--window`/`--bgn`/`--end`, `--max-requests`, `--max-calls` and `--no-lock`
narrow it. This is the ops fallback, the testable path, and what **`P2.S7`/`P2.S8` should reuse**
instead of re-deriving a run loop. It also makes N34's rule ("finish a budget-capped live run with an
offline pass over the cache") one command — the 본문 stage passes `fetch=True` even offline and lets
the *client* decide, so a cached-but-unpersisted document is adopted rather than reported missing.
Ops footnote paid for once: start beat with `-s var/celerybeat-schedule`, or it drops its shelve DB in
the repo root (now gitignored).

### Appended by `P2.S7` (2026-08-20)

**N57 — the backfill's whole justification, measured: ②'s urgency comes from the 2025-H2 vintage
and from nothing else.** Before it, **1** of 267 cached 2026-filed CB events opened 전환청구
within 30 days of the judging week. After it (2025-06-01 → 2026-08-20, 584 live requests):
**33 events open within 30 days of 2026-09-07, 82 within 90, 152 within 180**, 67 are already
inside their 전환청구기간, and the largest overhang in the 90-day window is **67.8 %** (효성화학
`20251031000547`, opens 2026-12-04; 49.14 % 지엔코 `20250908000230` inside 30 days). The cause is
**not** a filing-rate effect — 530 CB originals over 14.7 months is ▷ ~36/month against P1's
▷ ~35/month for 2026 — it is the **~12-month 전환청구 lockup**: a CB filed in 2025-H2 opens in
2026-H2. Any later slice re-deriving ② urgency must keep the ≥ 2025-06 window; a 2026-only
corpus is structurally empty of near-term openings.

**N58 — ②'s exposure test is API completeness, not a 본문, and it needed two new states.** ② is
the only rights type whose countdown is entirely `API` (N6), so requiring a stored 본문 would
have blocked 422 renderable events for prose they do not need. `mijual.gates.exposure`'s R2 arm
keeps suppression / 철회 / blocking flags unchanged and replaces the document requirement with
`mijual.cb.R2_REQUIRED_API_FIELDS` — 전환가액 `cv_prc`, 전환청구기간 `cvrqpd_bgd`/`_edd`, 오버행
`cvisstk_cnt`/`cvisstk_tisstk_vs` — all present **and parseable** on the current version's detail
row. New states, both conservative and both real: `no_detail` (68 events — no stored row) and
`incomplete_api_row` (1 — 파이온엑스 `20260722000285` states a **38.45 % dilution with no
전환청구기간 at all**). **해외/USD decided:** exposable **iff the KRW fields parse**, never on
`ovis_*`; the corpus's one 해외 case (헝셩그룹 `20260213002703`, 16,000,000 HKD) states 전환가액
174원 / 17,110,804주 in KRW and passes on its own merits. Parsing lives in one place —
`mijual.cb.ConvertibleFacts` (Decimal 원, `korean_date`) — and `P2.S8`/P3 must call it rather
than re-parse `cv_prc` strings.

**N59 — a withdrawn CB keeps its detail row and OpenDART blanks all 46 fields to `-`.** Verified
on all 8 ② withdrawals (베노티앤알 `20260211001003`, 핀텔 `20260417000537`, 센서뷰
`20260227007913`, …) and re-probed live: the row is still returned, it is just empty. Two
consequences. (a) The N58 completeness rule already refuses to render them, so the 철회 detector
does not change *whether* they show — it changes *what is said*: `no_detail`/`incomplete_api_row`
(a silence) becomes `이 사채 발행은 철회되었습니다` with a 정정사항 row and a span. (b) **A blank
② row is not proof of a withdrawal** — 비트플래닛 `20260616000274` is blank and is not one — so
neither signal may be inferred from the other.

**N60 — N47's four shape rules generalise to ② unchanged, and ② is the clean case.** Over **808
② 본문 documents / 4,627 정정사항 rows**, `철회` appears in the 정정 후 cell of **10 rows, the
shape accepts 9, and all 9 are withdrawals — precision 9/9** (vs 71 % false positives for the
keyword test on ①/③: a CB's 정정 후 cells carry no 매수청구 boilerplate). **8 ② events / 9
filings**; 베노티앤알 and 코퍼스코리아 each withdrew a 유상증자 **and** a CB on the same day. The
tenth row is a **false negative left uncaught on purpose**: 비트플래닛 `20260616000274` withdraws
in a 143-char paragraph under `23. 기타 투자판단에 참고할 사항`, and relaxing any rule to admit
it re-admits the ①/③ boilerplate. N55's rule held again — 대진첨단소재 `20260714000506` surfaced
only after one more 본문 was fetched, which is why `python -m mijual.cb documents --blocked`
exists: **quote a 철회 count with the document coverage it was measured at.**

**N61 — gates 6–8 are exercised, #6 held exactly as written, #8 had to move.** 62 rows each.
**#6 리픽싱:** the 본문's 최저 조정가액 equals API `act_mktprcfl_cvprc_lwtrsprc` in **29/29**
comparable rows, **0 mismatches** (13 skipped — the API field itself is blank in 87/267 rows);
§7's row needed no change and this is its first corpus confirmation. **#7 콜·풋:** 37 checked,
1 failure, 16 skipped. **#8 보호예수 moved, N45-style:** a CB states 전매제한 as a **duration,
not a date** (`사모발행에 의한 1년간 …`) in **31 of 62 rows**, and every row that did carry a date
carried one the *model* computed by adding 12 months to the 발행일 — the arithmetic §3.6 assigns
to code. The gate now derives it (`mijual.calc.lockup_release_date` = API `pymd` + 개월수),
checks a model-stated date **against** the derivation (±3 days for 발행일/납입일 wobble), and
records an unquantified 전매제한 as `not_evaluable(lockup_not_quantified)`. 31 failures → 3.

**N62 — the API-derived cross-check caught a class of error no other layer sees: a 정정 attached
to the wrong 사채.** All 4 remaining ② gate failures are one finding — 엑시큐어하이트론
`20260630000509`, 알파AI `20250930000580`, 제이에스링크 `20251204000439` are corrections whose
본문 `최초제출일` names an event never collected (2024-09-06 / 2025-05-07 / 2024-12-17), so
nearest-earlier pairing attached each to a **different CB of the same corp**; their 조기상환
schedule and 보호예수 date belong to another bond. Nothing else notices, because no other check
compares a 본문 reading against a machine value scoped to one 사채. **Gate 7/8's API reference is
therefore also an identity check** — worth remembering wherever an API-backed gate exists.

**N63 — DEFER-JOB CANDIDATE (not taken here): `hint_mismatch` does not block exposure, and for ②
it probably should.** 30 of the 422 exposable ② events carry it; N62 shows at least 3 are real
mis-attachments whose *prose* describes another 사채 (the API countdown itself stays correct, so
the harm is bounded). Not fixed in this slice because the same rule would also block **42 passing
① rows + 2 tbd** and reopen S5/N48's settled decision that `hint_mismatch` is evidence, not a
blocker (N31: ~half of ① mismatches are ±7-day 접수일 skew). The right shape is probably
field-level (`not_evaluable(foreign_document)` for a version whose hint names a non-existent
event) rather than event-level, and it needs its own measurement pass. Sits beside N51 as
collector/identity work.

**N64 — ② rides the existing beat; it got no task and no entry of its own.** `DEFAULT_ENDPOINTS`
derives from `TARGETS` and `PipelineConfig.endpoints` defaults to it, so registering
`cvbdIsDecsn` put ② inside the existing `collect` stage — same window, same lock, same ceilings —
rather than adding a second schedule that could interleave (N53's lock argument applies to
schedules too). `extract_rights` stays `(R1, R3)`: ② needs zero LLM. Costs to expect on the daily
run: +~20 detail requests per 14-day window, and a much longer bodydoc queue (1,181 ② 기재정정
versions exist, 1,021 본문 now held) which drains at `bodydoc_max_documents` per run. The
backfill stays a one-off CLI — a scheduled job's window rolls forward, so a fixed historical
window has no business in one. **Subtype matching is exact string equality and must stay so:**
the same `pblntf_ty=B` stream carries 자기전환사채매도결정, 자기전환사채만기전취득결정,
전환사채매수선택권행사자지정, 제3자의전환사채매수선택권행사, 신주인수권부사채권발행결정 and
교환사채권발행결정 (EB, out by D-1) — a substring match on `전환사채` collects all of them.

**N65 — operator directive (2026-08-20), D-4 amended: the thinking level is per task and routine
reading is explicitly cheap.** The "changple5" preset applies **HIGH** to every call (N35 saw its
thought tokens but read it as untouchable); the operator has now reserved it for genuinely hard
work. Mechanism, verified against `google-genai` 2.18.1: gemini-3.7-flash is a 3.x model, so the
knob is `types.ThinkingConfig(thinking_level=…)` with `MINIMAL|LOW|MEDIUM|HIGH` — **not**
`thinking_budget` — and *omitting the field entirely* is what inherits the preset (an empty
`ThinkingConfig()` is still an instruction). Measured on one real `r2_prose` prompt (11,491
prompt tokens): preset **866** thinking tokens / ▷ $0.0160 → explicit `LOW` **0** / ▷ $0.0126,
**−21 % cost**, and a value-level diff against the stored preset-level extraction found **every
gated value identical** (floor 3,962, ratio 0.7, 해제일 2026-09-12, 12개월, put
2026-08-24~2028-08-07) with only free-text `detail` wording differing. `THINKING_BY_TASK` in
`mijual.extract.client`: prose tasks `LOW`, unlisted tasks `LOW`, **`correction` keeps the
preset** — it is the only task that *reasons* and N41's 121-changes/0-unsupported measurement was
taken at the preset level, so re-measuring it belongs with `P2.S9`. The level used is recorded
per call (`extraction_call.thinking_level`, additive nullable via `ensure_columns`), because a ▷
cost is only comparable across runs if the level behind it is known. **The 80 calls already spent
by this slice were not re-run** (operator instruction); they read `NULL`.

**N66 — what ② costs to read, and what the triage left undone.** 80 calls / 797,099 tokens /
▷ $1.0677 / 0 failures bought fields 6–8 on the **45 soonest-opening** exposable events (44
`r2_prose` + 36 correction; 112 of 114 quotes located, 111 byte-verified). The urgency set is
**171** events, so **126 keep the structured-only floor D-1 allows** — full API countdown, no
리픽싱/콜풋/보호예수 narrative. Extraction yield per document: lockup_release 42/44,
option_schedule 39/44, refixing_terms 33/44. Whole-slice request spend **1,398 of a 2,500
ceiling** (584 collection + 700 정정 본문 + 90 urgency 본문 + 13 blocked + 11 probes); nothing was
dropped for budget. Board today: **457 exposable events (① 25, ③ 10, ② 422) / 280 renderable
field instances**, up from 35 / 157.

### Appended by `P2.S8` (2026-08-20)

**N67 — the 청약 결과 is a deterministic table read, and the 증권발행실적보고서 is the
document family P1 never surveyed.** Filed on the 납입일 (pblntf_ty=**C**, 발행공시), it
carries `Ⅶ. 신주인수권증서 발행내역` (발행 증서 수, and the 증서 청약 / 초과청약 split),
`Ⅷ. 실권주 처리내역`, `3. 청약 및 배정현황` and `1. 청약 및 납입일정` — all labelled tables,
**so the whole 청약 결과 costs 0 LLM calls**. Two forms exist and both are read
(`mijual.estimate.perf`): the standard 주식 form and the 집합투자증권 (REIT) form, which carries
the same 실권주 table inside `4. 청약, 배정 및 인수에 관한 사항` and has **no Ⅶ section at all**
(KB스타리츠 `20260423000439`). Three parsing rules were paid for once and must not be relaxed:
(a) match the 실권주 column by its **header**, never by position — it appears in column 0, 1 and
2 across the corpus; (b) the discriminating word is **청약**: 대동기어 `20260728000264` labels
its 단수주 column `신주인수권증서 배정 실권주` beside the real `신주인수권증서 청약 실권주`, so a
match on 실권주 alone reads 9,397 instead of 1,437,309; (c) the `3. 청약 및 배정현황` `계` row is
ten numeric columns wide and the 확정발행가 is `최종 금액 ÷ 최종 수량` (index −2 ÷ −3), refused
with a note at any other width.

**N68 — 소멸 증서 = 발행 증서 − 증서 청약, NOT 최초배정 − 청약, and the filer's own cell is
wrong 5 times in 31.** 단수주 is never issued as a 증서, so counting it inflates the number
with rights that never existed. LB세미콘 `20260811000597` states 2,109,436 실권주 where its own
Ⅶ tables give 11,970,900 − 9,890,564 = **2,080,336** (the 29,100 gap is exactly the 단수주);
라온피플 `20260225003924`, 대한광통신 `20260306000600`, 인베니아 `20260206000357` and 피엠티
`20260629000392` differ the same way. Rule in code: `mijual.calc.lapsed_warrants`, and every
mismatch is stored on the report as a note rather than silently resolved.

**N69 — the 확정발행가 has two independent witnesses and they agree 31/31.** 본문
`6. 확정발행가` (a printed price) equals the 실적보고서's 최종 배정 금액 ÷ 최종 배정 수량 (an
arithmetic on a different filing) on every offering that states both — 형지엘리트
`20260130000043` prints a 9-column `계` row and is 본문-only. This is what lets the price be
treated as a **fact** rather than as a reading, and it means an out-of-corpus offering can be
priced from its 실적보고서 alone.

**N70 — the value proxy, and the algebraic reason it needs no formula branch.** ▷ 증서 이론가치
= `확정발행가 × 할인율 / (1 − 할인율)`. There is no price feed (DART-only), but the filing states
발행가액 = 기준주가 × (1 − 할인율), so the issuer's own 기준주가 inverts out of it. The identity
holds for **both** pricing formulas: the 2차 산식 measures 기준주가 at 구주주 청약일 전 제3거래일
(already ex-rights), and the 1차 산식's `/[1 + (증자비율 × 할인율)]` term **is** the 권리락
adjustment, so `(기준주가₁ − 확정)/(1+r)` reduces to the same expression (unit-tested). Band, not
point: a minority of filers write the 1차 산식 *without* the 증자비율 term (형지I&C
`20260707000087`), which if cum-rights lowers the value by `1 + 배정비율` — that is the reported
lower edge. The `MAX(…, 기준주가의 60%)` floor branch makes the proxy conservative, never
inflated. All of it lives in `mijual.calc` (`implied_reference_price`,
`warrant_intrinsic_value`, `warrant_intrinsic_value_floor`).

**N71 — `주요사항보고서(유무상증자결정)` is a fourth ① source and every run before this one was
blind to it.** Endpoint **`pifricDecsn`**, form code **11308**, subtype string `유무상증자결정` —
which `collect.targets`'s exact-equality match (correctly, N64) never accepted. It is
unambiguously ①: the form carries the *same* numbered 유상 section (10/10 target labels,
`6. 확정발행가`, `9. 1주당 신주배정주식수`, `11. 청약예정일`, `18. 신주인수권양도여부 = 예`) plus a
trailing 무상 section, and its 실적보고서 carries the same Ⅶ/Ⅷ tables. **7 of the 32 offerings
that lapsed in 2026 were filed this way** (루닛, 티엘비, 대동기어, 뉴로메카, 아모텍, 라온피플,
한국첨단소재). Registered in `TARGETS` now, so the scheduled daily pipeline picks it up with no
new task (N64's argument). Its detail row prefixes every 유상 field with `piic_`, so
`collect.filters` and `bodydoc.backfill._ic_mthn` now read `ic_mthn or piic_ic_mthn`. **The
first-wins rule in `LabelSet.get` is load-bearing here**: the 유상 section comes first, so
`shares_per_share`/`new_shares`/`allotment_record_date` resolve to the 유상 values.

**N72 — a lapse number cannot be framed on the 주요사항보고서 window; frame it on the
증권발행실적보고서.** The 청약 lands 2–6 months after the 결정, so 2026's lapses were mostly
decided in 2025. Measured: of the **32** completed ① offerings of 2026, only **10** were
reachable from the pre-S8 corpus. The census (`list.json pblntf_ty=C`, 2026, KOSPI+KOSDAQ,
8,841 rows → 2,533 증권발행실적보고서 → 68 on an equity offering, 91 pages ≈ 85 requests) is the
honest population. The equity filter matters: 2,465 of those 2,533 are ELS/DLS 실적보고서 filed
by 증권사, and filtering to corps that also registered an equity offering in the window cuts it
to 68 with no false negative found.

**N73 — three blind spots, each now measured, and only one of them was a code bug.**
(a) **14** offerings were decided before 2026-01-01 — outside `P2.S2`'s window (a frame
problem, fixed by adoption). (b) **7** were `유무상증자결정` (N71 — a real code gap, fixed).
(c) **3 were 2026 KOSDAQ `유상증자결정` originals that `P2.S2`'s *run* simply missed** —
레이저옵텍 `20260109000634`, RF머트리얼즈 `20260408002647`, 피엠티 `20260409002139`. Discovery
finds all three **today** (verified: a 1-day `discover` over 2026-01-09 returns
`20260109000634`), so the code is right and the corpus is **not a census**. (d) **1 was
invisible to the census itself**: KB스타리츠 `20260423000439` is 증권발행실적보고서(집합투자증권)
and appears on **no page** of 발행공시 — caught only by the per-event backstop (one corp-scoped,
unfiltered `list.json` per closed-청약 event). Practical rule: **a census and a per-event sweep
are two different completeness claims; run both.**

**N74 — adoption is cheap, targeted, and it HEALS N21 residue.** `mijual.estimate.adopt`
reaches one named corp with corp-scoped `list.json` (no 3-month cap) + the corp-scoped detail
endpoint + 2 본문 — **3–4 requests per offering**, against ~300 detail requests for a
market-wide 2025-H2 re-run. 22 offerings adopted for ~90 requests. Side effect worth keeping:
the corpus already held `unpaired_correction` placeholders for 코이즈, 캠시스, 진양폴리우레탄,
트리니티항공, 레이저옵텍, RF머트리얼즈 and 피엠티 **precisely because** their original was outside
the window or of the unknown subtype; adopting the real original let `P2.S2`'s own
`retire_superseded_unpaired` retire them as `superseded_by_pairing`. Also: when no original is
visible at all (코이즈 — six 기재정정 and no original over 2+ years), the earliest visible 정정
becomes the chain head (`pairing_method='unpaired_correction_head'`), because the 정정's 본문
carries the whole form — it is the *identity* that stays provisional, not the values.

**N75 — the 실적보고서 is bound to its event by SCHEDULE, not by corp.** Its own
`1. 청약 및 납입일정` must equal the 주요사항보고서's `11. 청약예정일`: **32/32 linked by
`schedule_match`**, none on the corp-only fallback. The fallback also has to respect time —
트리니티항공's single ① event is dated 2026-06-22 against a 2026-03-19 report, and a naive
"corp has one event" link attached the wrong 확정발행가 and 할인율 to a real 실권 count until the
`original_rcept_dt <= 청약 개시일` guard was added.

**N76 — what §3.6's gate costs, in won: ▷ 49.2억원, 6.4 % of the headline, and it is worth
it.** Three of the 32 offerings (진양폴리우레탄, 캠시스, LB세미콘) have a citable 실권 count and a
cross-checked 확정발행가 but **no gate-passed 할인율** — all three failed `span_unresolved` in the
same way N37 first saw: the model stitched formula fragments from separate paragraphs
(`▶ 1차 발행가액 = … ▶ 2차 발행가액 = … ▶ 확정 발행가액 = MAX…`) into one quote that exists
nowhere in the document. The values look right (0.25/0.25/0.20) and are **still not used** — the
report counts the 주식 and states the gap with a quantified upper bound. This is the single best
demo of the trust claim in the phase: the gate is not decoration, it costs money.

**N77 — the 2026 result, and the shape of the story.** ▷ **718.1억원** (71,812,971,649원; band
▷ 549억~718억) across 32 offerings; **51,253,956 of 365,527,824 배정 증서 lapsed = 14.02 %**;
per-offering 소멸률 ranges **2.51 % (SKC) to 49.09 % (형지I&C)**, median 11.60 %; 할인율 ranges
5 % (KB스타리츠, a REIT) to 40 % (인베니아 — a real 40 % 유증, not a floor-clause misread), median
25 %. Largest single loss ▷ 206.4억원 (한화솔루션 `20260730000366`). **18 ① offerings are still
open**, 11 with a 청약 ahead (soonest 2026-09-04 계양전기 · SG) — which is the line that turns
the retrospective number into the product's pitch. Regenerate with
`.venv/bin/python -m mijual.estimate report --today <YYYYMMDD> --korean` (0 requests, 0 calls).

**N78 — two DEFER-JOB candidates for the orchestrator (executors do not file them).**
(a) **Re-run `P2.S2`'s discovery over the full 2026 window and reconcile** — N73(c) proves the
corpus missed at least 3 collectable ① originals, and the same run would now also pick up every
`pifricDecsn` event (N71); ▷ ~120 requests, and it is the difference between "our board shows
the live rights" and "our board shows the live rights we happened to collect". (b) **Backfill
`pifricDecsn` history** the way `P2.S7` backfilled ② — 7 of 32 lapsed offerings were 유무상, so
the live board is under-counting ① by roughly the same fraction today.

**N79 — spend, and what `P2.S9` inherits.** ~337 OpenDART requests (159 survey/census, 111
collect, 39 warrants, 18 verification) of a 500 ceiling; **22 LLM calls at `thinking_level=LOW`,
158,863 tokens, ▷ $0.2186, 0 failures** — the 실적보고서 layer spent **0**. The corpus `P2.S9`
samples from is now materially larger: ① exposable events **25 → 47**, R1 `warrant_confirmed`
50, plus **32 증권발행실적보고서 with span-verified numbers** — a second document family with
ground truth that is *deterministic*, which makes it an unusually good accuracy fixture (the
LLM-read 할인율 can be scored against the 확정발행가/실적보고서 arithmetic on 29 offerings).

### Appended by `P2.F1` (2026-08-20)

**N80 — the run gap N73(c) called "at least 3" was 244 filings, and it was NOT uniform across
endpoints.** Full-2026 discovery (2026-01-01~08-20, KOSPI+KOSDAQ, `pblntf_ty=B`, 4,634 list rows
over 50 pages) returns 2,279 target filings. Checked against the stored `filing_version` table:
**`piicDecsn` 192 of 1,145 unstored, `pifricDecsn` 4 of 25, `cmpMgDecsn` 48 of 286 (17 of them
originals), `cvbdIsDecsn` 0 of 823.** Two lessons. (a) **② had no gap at all** because `P2.S7`
backfilled 2025-06-01→2026-08-20, a window that strictly contains 2026 — so the ② arm of the
sweep was skipped on evidence, saving a *measured* 266 detail requests + 69 history queries for
zero new rows. **A wider historical backfill immunises a rights type against this failure mode;
a window-limited one does not.** (b) The check itself is free and reusable: discover offline,
diff the `rcept_no` set against `filing_version`, and you have the gap before spending anything
(`DartClient.cache_path(...).exists()` prices the repair the same way). Run this **before**
claiming a corpus is a census — it is the cheap half of N73's "run both sweeps" rule.

**N81 — the pairing-history reach is a board-quality knob, not a request-saving detail.** This
slice passed `--history-bgn 20220601` (instead of the default `bgn − 3y` = 2023-01-01) purely to
reuse 440 already-cached corp-history responses, saving ~100 requests. It reached 7 months
further back and **minted a second exposable event**: 코이즈's 2026-01-22 정정 nearest-earlier
paired to a genuine but 3-years-stale `piicDecsn/2022-10-13` original, so `20260122000058` now
renders on **two** exposable events (the S8 `unpaired_correction_head` chain at 2025-09-15, and
the 2022 one). The 본문 hint already calls it — `hint_status='duplicate'` + flag `hint_duplicate`
on the 2022 side, `confirmed` on the 2025 side — but **`hint_duplicate` is not in N48's blocking
set**, so both render. Corpus-wide today: 840 of 3,024 `rcept_no` sit under 2+ event keys, but
only **2 sit on two *exposable* events** (this one, and ②'s 사토시홀딩스 `20251219000402`, which
predates this slice). Not fixed here on purpose — the field-level repair N63 already argues for
is the same decision, and reopening N48's exposure contract needs its own measurement pass.
**Practical rule: widening the pairing history is a correctness change, not an optimisation —
measure the duplicate-exposable count on both sides of it.**

**N82 — §7 #10's 정정 재추출 is now a 69-call job at the *preset* thinking level, and it did not
run.** Dry-priced after the sweep: **59 calls for ① + 10 for ③**, and
`THINKING_BY_TASK['correction'] = INHERIT_PRESET` (N65) means every one of them runs at the
project's HIGH preset. That is ~6× this slice's whole call ceiling at the most expensive level in
the codebase. Consequence on the board **today**: `correction_interpretation` stays at **41**
renderable instances while the ① corpus grew to 50 exposable events, so the 정정 story is the one
field that did not keep up with the sweep. It is a *coverage* gap, not a correctness one — every
stored interpretation is still gate-judged, and an unread 정정 shows nothing rather than something
stale. Whoever funds it should decide the thinking level first: N65 kept the preset because N41's
121-changes/0-unsupported quality measurement was taken there, and re-measuring at `LOW` is
`P2.S9` work that would likely cut the bill ~20 %.

**N83 — the sweep's real correctness save was 디모아, and it is the exact failure N39 named.**
Collecting the missing original `20260424000529` created a `warrant_confirmed` 주주배정 유상증자
event that had never existed — and the **unchanged** N47 row-shape detector immediately read its
`20260625000227` 정정 and blocked it as `withdrawn`. Before the sweep that 철회 sat on an
`unpaired_correction` placeholder and N47/N55 correctly recorded it as changing no exposure; the
moment the real event appeared it would have been **published as a live right**. ① `withdrawn`
2 → 3. Totals are otherwise stable — **15 distinct withdrawn filings (① 6, ② 9)**, matching N55's
6 and N60's 9 exactly at a coverage of **1,792 / 2,720 기재정정 versions carrying a 본문** — so the
sweep found no *new* withdrawal, it moved one onto a real event. **Generalisation worth keeping:
filling a collection gap can flip a previously harmless flag into a blocking one, so the gate
layer must be re-run after every collection repair, never assumed stable.** (Board after the
whole reconciliation: **488 exposable events — ① 50, ③ 16, ② 422 — and 409 renderable field
instances**, from 479 / 388; ③ `no_document` 9 → 1; the 소멸 headline ▷ 718.1억원 is unchanged
while the open pipeline grows 18 → 23 offerings, 11 → 15 with a 청약 ahead.)

### Appended by `P2.S9` — Phase A only (2026-08-20)

**N84 — the evalset measures TWO directions, and the second one is the only honest way to
price §3.6's gate.** (a) precision of what the product *shows* (rows whose gate said
`passed`/`tbd`), and (b) the gate's **over-blocking** price — of the rows the gate
*blocked*, how many the human judges to have been correct readings all along. S8 already
found one such pattern worth ▷ 49.2억원 / 6.4 % of the headline (N76); without direction
(b) a gate can buy any precision figure by blocking more. Both are on the same sheet and
the sample deliberately carries gate-blocked rows. Three picks keep the arithmetic
straight: `random` (the seeded stratified draw — **the only pick a rate is computed
from**), `forced` (every known hard case, included whole and reported case by case, never
averaged in), `booster` (extra filings contributing **only** their
`correction_interpretation` row, so boosting the thinnest field cannot de-randomise the
others on those filings). Rates carry a **95 % Wilson** interval, not a normal one — at
n ≈ 20 with p near 1 the textbook interval is simply wrong, and `21/21` is not "100 % ± 0".

**N85 — the gate-block rate is a corpus statistic and it is available BEFORE any label,
and it is wildly uneven per field.** Over the 633 deduped extraction rows, **77 (12.2 %)
are gate-blocked**. Per field: ① 4.0–8.0 % (`warrant_trading_period` 3/75,
`subscription_agents` 3/75, `excess_subscription` 3/75, `forfeited_share_method` 5/75,
`issue_price_formula` 6/75), 정정 해석 6.4 % (3/47), **② 14.5–32.3 %** (`option_schedule`
9/62, `lockup_release` 14/62, `refixing_terms` **20/62**), **③ 44.0 % (11/25)**, and the
증권발행실적보고서 figures **0 %** (they pass through no §7 gate — no model read them).
Reason mix corpus-wide: `field_absent` 44, `lockup_not_quantified` 9,
`superseded_api_reference` 8, `span_unresolved` 5, `no_correction_rows` 3,
`release_date_not_derived` 3, `method_not_enumerated` 2, `option_date_out_of_term` 1,
`dissent_period_mismatch` 1, `api_deadline_absent` 1. **③'s 44 % is mostly N46's
version-scoping, not a reading failure** — read it with that caveat or it looks like ③ is
badly extracted when it is mostly "we correctly refuse to compare a superseded 본문 against
today's API row".

**N86 — N41 re-measured at 45 records, and one trap in the number.** The 정정-해석 recall
proxy now stands at **177 deterministic 정정사항 rows, 26 uncovered → 85.3 % recall**, with
**0 unsupported of 157 model changes** — N41's "121 changes / 0 unsupported" holds at 1.5×
the sample. The trap: a naive aggregate reports **5** unsupported, and all 5 come from
**3 records whose 정정사항 table did not parse at all** (`items == 0`, 현대바이오
`20250925000643`, 오성첨단소재 `20251014000295`, 풍전약품 `20250930000508`) — with an empty
table every model change is trivially unsupported. Those records are counted separately, the
gate already blocks all three (`no_correction_rows`), and **any later reader must exclude
`items == 0` or a parse gap reads as a model regression.**

**N87 — N21/N81's duplicate-`rcept_no` residue reaches the extraction table too, and an
evalset must collapse it.** 16 `(rcept_no, field_key)` readings are stored twice because the
same filing sits under two event keys (3 filings carried 10–12 extraction rows for what is
5–6 fields). They are collapsed to one row — preferring the exposable/current-version
event, then the lowest id — because the evalset measures a *reading*, not a storage residue;
counting both would have double-weighted exactly the filings the collector is least sure
about. Corpus row count after dedupe: **633 extraction + 123 실적보고서 figures**.

**N88 — the operator gate is open and its cost is stated: 344 rows / 99 filings /
▷ 75–95 minutes.** Sheet `evalset/sheet.csv`, instructions `evalset/LABELING.md`, frozen
sample `evalset/sample.json`, machinery `python -m mijual.evalset {sample,sheet,status,
import,report}` at 0 requests / 0 calls. Two levers if the operator's budget is smaller,
neither needing code: the sheet is ordered ① → ② → ③ → 실적 with one filing's rows
contiguous, so stopping at a block boundary still gives a complete measurement for
everything above it (① alone is ▷ ~36 min); and a smaller sheet is one command
(`sample --R1-prose 14 … --force`, seconds). The sheet **refuses to be overwritten once it
holds labels**, and the refusal happens before `sample.json` is rewritten, so the frozen
sample and the labels can never drift apart.

### Appended by `P2.S9` — Phase B (2026-08-20)

**N89 — the accuracy numbers are CLAUDE-JUDGED (cross-model), not human ground truth, and
the provenance is part of the number.** The operator amended the slice on 2026-08-20 —
verbatim: _"you self evaluate and self validate. since the extraction done by gemini and you
are a claude fable. try by yourself."_ — so all 344 labels were judged by the slice executor
(Claude, Opus 5) against each row's quote and, where ±120 chars was not enough, the **full
stored 본문 read out of Postgres**. The §7 prose fields were extracted by **Gemini**, so no
model graded itself; the 69 실적 rows were read by no model at all (a parser audit). But this
is **inter-model agreement, not adjudication**: no human has verified a single label, a
shared misreading of a Korean disclosure convention would be invisible to both models, and
nothing in this phase may be described as "hand-labelled". The human override is free and
unchanged (overwrite column A of `evalset/sheet.csv`, re-run `import` + `report`; the sample
is frozen so only re-judged rows move). Provenance is now carried in three places —
`LABELING.md`'s footer, `P2.S9` result, this note — because **`labels.json` has no field for
it**, which is itself a small fix-slice item (`judged_by`). Spend: **0 LLM calls, 0 OpenDART
requests.**

**N90 — first measured extraction accuracy: 98.6 % strict on what the product would show,
0 `wrong` in 344 rows, and the whole strict-error surface is ONE defect class.** Random picks
(the only pick a rate is computed from): **213/216 = 98.6 %, 95 % Wilson [96–100 %]**, 100 %
with `partial` counted; pooled across picks, 291 `correct` + 5 `partial` of 296 shown rows;
344/344 judged with **0 `skip`**. All three strict misses are 실적보고서 figures where the value
is a **correct sum of two table rows but the citation points at one addend** — SKC
`20260522000297` (예탁결제원 청약 11,307,456 **+ 직접청약 239** = 11,307,695; and 초과청약
1,889,818 **+ 41**) and 에스에너지 `20260312000380` (12,001,809 **+ 866**). The summing is
right — not summing would under-report 청약 and over-report 실권주 — so the defect is the
**citation contract**: §3.6 promises a tappable number that lands on the text saying it, and
these land on a different number. ▷ **multi-span citation (or "sum of N cited rows")**, ~10 %
of 실적 filings carry the split-row form. The two remaining `partial`s are `correction_
interpretation` completeness, not falsehood (알파AI `20250930000580` omits 이자지급방법;
아시아나항공 `20260713000482` lists the footnote *references* as its changes while its 요약 is
accurate). **Read 100 % cells as "no error in n ≈ 10–22", not as solved** — and note the
inflation sources honestly: this is the post-S7/S8 pipeline, 26 of 275 model rows (9.5 %) are
`absent`/null readings, and the gate had already removed 48 rows from the shown set.

**N91 — over-blocking, measured: the gate blocked 48 rows in this sample and EVERY ONE was a
correct reading (19/19 random, 48/48 pooled).** In this sample the gate bought **zero**
precision: it removed no error. That is not "the gate is broken" — 30 of the 48 are blocks
the product wants (`field_absent` 26, `superseded_api_reference` 4). The other **18 are a
price list with three fixable causes**: (a) **API-vs-본문 정정 lag, 5 rows** — the model read
the corrected 본문 and the gate compared it against a stale API row (엑시큐어 `20260630000509`
납입일 2026-12-30 vs API `[2025-09-18, 2028-09-18]`; 알파AI `20250930000580` 2025-12-19 vs
2025-09-22; 제이에스링크 `20251204000439` 2025-01-15 vs 2026-10-02; 모다이노칩 `20260730000170`
통지 09-17~10-16 vs 03-09~03-23) — **the gate's reference data was wrong, not the reading**;
(b) **`span_unresolved`, 5 rows** — correct readings whose quote concatenates two
non-contiguous document lines (N76's ▷ 49.2억 pattern, now confirmed on LB세미콘, 진양폴리우레탄,
캠시스, 에이럭스, 엑시큐어); (c) **`lockup_not_quantified`, 4 rows** — a correctly read "12개월"
withheld for lacking a derived 해제일. Also confirmed as over-blocks: `method_not_enumerated`
×2 (이렘 — full-text search shows the filings contain no 일반공모/인수/미발행 clause, so
`method: 기타` was faithful) and `no_correction_rows` ×2 (풍전약품, 현대바이오 — the model read
real changes out of tables the deterministic 정정표 parser cannot reach).

**N92 — the 정정-해석 recall proxy is a FLOOR, not a measurement: a matcher bug understates
it (85.3 % → 88.7 %), and content-level coverage is ≈ 99 %.** In
`src/mijual/extract/runner.py:464-475` (`check_against_items`) the value-fallback arm
(`new_key in item["after"]`) is evaluated per item **inside the same loop as the item-name
match**, and nothing stops several changes from claiming the same item — so when a filing
corrects many rows **to the identical string** (에이전트AI `20260619000455` moves five schedule
rows to `-(추후 확정)`) every change binds to item 0 and four covered rows are counted
`uncovered`. A read-only re-match with a one-to-one, name-first matcher gives **20 uncovered
of 177 → 88.7 %** (3 records affected: `20260619000455` 5→1, `20250925000611` 1→0,
`20251204000439` 1→0; still 0 unsupported of 157). Judging the content of the 19 uncovered
items in the 32 sampled rows: **1** costs a reader information (알파AI's 이자지급방법); the other
18 are duplicate restatements of an already-listed change or bare `(주N)` footnote references
→ **≈ 99 % of investor-meaningful items covered**. **Not fixed here on purpose**:
`deterministic_check` is stored evidence written by S4 across the corpus, and correcting the
matcher without re-running S4 would leave code and database disagreeing. ▷ fix slice = fix
the matcher + re-run the check + re-freeze the number.

**N93 — three findings that are not accuracy numbers.** (a) **N68's five `lapse_mismatch`
filings are ISSUER table errors, not parser errors, and must be surfaced as such.** LB세미콘
`20260811000597` prints, under the headers `신주인수권증서 청약 실권주 | 구주주 배정단수주 |
실권주 및 단수주 총계`, the row `2,109,436 | 1,776,014 | 333,422` — a "총계" smaller than its own
first column, because the issuer filled the row with `[실권주+단수주 총계, 초과청약 배정분,
일반공모 잔여분]`; 인베니아 `20260206000357` (`563,178 | 2,821 | 560,357`) and 피엠티
`20260629000392` (`416,831 | 416,276 | 555`) have the same shape, while 대한광통신 and 라온피플
are internally consistent and simply define 실권주 to include the 단수주. The extraction reads
the header-named cell and records the gap in `facts.notes` — right behaviour; the product
must show **"발행사 기재 불일치"** rather than silently reconcile. (b) **#7 `option_schedule`
carries two date conventions**: `start_date`/`end_date` are sometimes the 조기상환**기일** range
(엑시큐어 `20260630000509`-class filings) and sometimes the 청구**기간** range — both
document-grounded, each filing self-consistent, so no row is `wrong`, but a UI that puts them
on one timeline compares a claim window against an exercise date. ▷ wants a per-option
`date_basis` marker, not a prompt change. (c) **`rcept_no 20250930000508` is stored under DART
`corp_name` 풍전약품 (corp_code `01110474`) while its own 본문 header reads 에스씨엠생명과학** — a
DART master/rename artifact: every extracted value is correct against the body, only the
display name would be wrong.

### Appended by `P2.REVIEW` — cycle 1, verdict `changes_requested` (2026-08-20)

**N94 — the phase's central invariant is verified on the live corpus, not just by test: 409
renderable field instances, 0 of them outside `passed`/`tbd`.** Re-derived read-only through
`mijual.gates.exposure.exposure_of_all` over all 630 judged events: 488 exposable, 409 renderable
fields, **0** renderable fields whose gate is `failed`/`not_evaluable`, **0** `tbd` fields leaking a
value (N48's `FieldView.value is None` holds), **0** exposable events sitting in a non-exposable
state. `python -m mijual.gates run` ×2 and `python -m mijual.estimate report --today 20260820` ×2 are
byte-identical, `python -m mijual.scheduler once --offline` completes all four stages at **0
requests / 0 calls**, and `pytest` is 56/56. Whoever changes the exposure contract in P3 should re-run
exactly this check — it is four lines and it is the product's trust claim in one number.

**N95 — a provenance claim survived the operator's amendment in the one place that prints to the
operator, and it is this review's only blocking finding.** `python -m mijual.evalset --help` renders
`src/mijual/evalset/__main__.py`'s docstring (`description=__doc__`) and therefore tells its reader
**"CLI for the hand-labelled evalset"**; `src/mijual/evalset/__init__.py` opens with "the
hand-labelled accuracy measurement" and describes "a sheet the operator labels by hand". N89 makes
that description forbidden — the 344 labels are Claude-judged, not human — and `P2.S9` fixed exactly
this class of wording in `report.py` (`사람이` → `판정자가`) while missing the module level. The
generated report, `LABELING.md`, `result.md` and this file are all correct; only the module docstrings
are not. **Rule to carry: when an amendment changes what a number *is*, grep the whole module for the
old description, not just the string the report prints.**

**N96 — two recorded fix-slice items are cheap enough to land before the docs freeze, and both are
provenance/accuracy integrity rather than features.** (a) `evalset/labels.json` stores only
`{labelled, corrections, source}` — verified — so the *only* non-regenerable artifact in the repo
carries its provenance in prose alone (N93c); a `judged_by` field makes it travel with the data.
(b) N92's `check_against_items` defect is confirmed still present at
`src/mijual/extract/runner.py:464-475` and it only ever **understates** (85.3 % stored vs 88.7 %
re-matched), so it is not a false claim — but the re-check runs over *stored* records at **0 LLM calls
and 0 OpenDART requests**, so freezing a durable `qa` number the repo already knows is low is the more
expensive choice.

**N97 — the mid-phase numbers in `P2.S5`/`P2.S7`/`P2.S8` results are point-in-time and MUST NOT be
copied into a doc.** The corpus grew under them (S7's ② backfill, S8's adoption, F1's sweep). Today's
regenerated truth, and the only figures a doc version may quote: **649 field rows — 566 passed / 4 tbd
/ 14 failed / 65 not_evaluable**; **488 exposable events (① 50, ② 422, ③ 16) / 409 renderable field
instances**; **32 offerings, ▷ 718.1억원, 51,253,956 / 365,527,824 = 14.02 %, 23 still open, 15 with a
청약 ahead**; 69 증권발행실적보고서 stored. S5's 275/4/5/20-over-304, S7's 457/280 and S8's
"18 open / 11 청약 ahead" are superseded (each was honest when written, and F1 restated the delta).

**N98 — the three soft spots the review was asked to weigh are all real, all bounded, and none of
them blocks P3.** Measured today, read-only: (a) **duplicate exposure** — 840 `rcept_no` sit under 2+
event keys corpus-wide and exactly **2 render on two exposable events** (코이즈 `20260122000058` under
`piicDecsn/2022-10-13` + `/2025-09-15`, and ②'s 사토시홀딩스 `20251219000402`), which is N81 confirmed
to the row; the trigger belongs on **D2**, not on a new fix slice. (b) **③'s 44 % block rate is
version scoping, not misreading** — of the 11 blocked `dissent_notice_procedure` rows, **8 are
`superseded_api_reference`**, 1 `api_deadline_absent`, 1 `field_absent`, and exactly 1 is a real
`dissent_period_mismatch`; any doc quoting the 44 % must carry that split or it reads as an extraction
failure. (c) **N82's 정정 재추출 backlog is exactly 69 calls today** (`scheduler once --offline`
dry-run: 정정 R1 50ev/59call + 정정 R3 13ev/10call) against `extract_max_calls=60` per run, so the
beat does drain it in two runs as N82 claims — **but `THINKING_BY_TASK['correction']` still inherits
the project HIGH preset, so an unattended scheduled run would make the thinking-level decision N82
asks a human to make.** Harmless while nothing runs unattended; decide it before P3 deploys a worker.

### Appended by `P2.F3` (2026-08-20)

**N99 — the evalset artifact is now self-describing: `labels.json` carries a `judged_by` block
(`judge` / `basis` / `imported_at` KST), `Labels.write()` refuses to write without one,
`import --judged-by` is required and **never inherited** from the previous file (a human re-judging
rows must not keep a machine's stamp), and the report prints the block instead of any hardcoded
sentence — re-stamped over the existing 344 labels with the label map verified byte-identical
(339 correct / 5 partial / 0 wrong, all rates unchanged), 0 calls / 0 requests.**

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

> **Cycle 1 of `P2.REVIEW` returned `changes_requested`, so NOTHING below has been consolidated yet
> and no doc version exists for P2.** The list itself was checked and is complete — every durable-truth
> change P2 made has a note here, grouped `architecture` (the S1→S6 running stack note) · `data` ·
> `operations` · `decisions` · `product` · `qa`. Two instructions for whoever consolidates: quote
> **N97's figures**, not the mid-phase ones the S5/S7/S8 notes carry; and state the accuracy numbers'
> **cross-model provenance** (N89) in the `qa` and `decisions` versions, never "hand-labelled".

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

- **`architecture`** (same note as the S1/S2/S3/S4 entries) / **`data`** — **§3.6 layer 2 landed
  (P2.S5), and it is where the product's trust claim becomes enforceable:** `mijual.gates`
  implements **one named gate per field-matrix §7 row plus a citation gate on every field**, judged
  against evidence the model never saw (본문 labels + the stored API detail row — N38 read from the
  other side), and writes a **four-state verdict** to `Extraction.gate_*`: `passed` / `failed(code)`
  / `tbd` / `not_evaluable(code)`, of which **only `passed` and `tbd` are ever shown**. A skipped
  check is never a pass, and a gate that compared nothing is `not_evaluable` — conservative by
  construction. The run is **LLM-free and request-free**, re-derives every verdict from scratch
  (drop-and-re-derive, S3's pattern) and is idempotent (two runs byte-identical). Also record the
  three places §7's gate column needed the corpus to settle it: **#2** 일반공모 청약 entries have no
  본문 `11.` reference (they are a *later* window → gated on ordering), **#5** 본문 `6. 확정예정일` is
  the 결정일 and the prose names the 공시일 (16 agree / 3 differ by exactly +1 day → the gate is a
  **window**, not an equality), **#4** §7's *배정주식수 × ratio* arithmetic needs a holder's 주수 and
  therefore lives in `mijual.calc`, not in a document check. And the version rule that follows from
  N2: **a stored API detail row is a reference value for the current version only** — a superseded
  reading is `not_evaluable(superseded_api_reference)`, never a failure. Source: `P2.S5` result
  (2026-08-20), findings N44–N46.
- **`data`** / **`product`** — **two document states enter the documented field model as
  first-class, and the field model gains an exposure boundary:** **철회** is now detected
  deterministically from one `3. 정정사항` row (shape rules, not the keyword — over **1,282 정정사항
  rows in 328 documents** the word `철회` appears in 14 정정 후 cells and only **4** are withdrawals,
  a 71 % false-positive rate), and a withdrawn event renders **"이 유상증자는 철회되었습니다"** instead
  of a cancelled countdown; **`추후결정`** is a verified citation with null dates and is shown as
  추후결정, with the superseded date structurally unable to leak (the exposed value is `None`).
  The **exposure contract** is the durable P2 → P3 boundary and P3 never re-implements it: an event
  is exposable iff not suppressed, not withdrawn and carrying no identity/rights conflict flag
  (`warrant_conflict`, `detail_conflict`, `event_key_collision`, `hint_split_evidence`); a field iff
  its gate passed or is `tbd`. Persisted on `Event.exposure_state/_reason/_note/_checked_at` so the
  board filters in SQL and makes **no OpenDART call in the request path**. Measured today:
  **35 of 44 events exposable (① 25/29, ③ 10/15), 157 renderable field instances, 275/304 field rows
  passed.** Source: `P2.S5` result (2026-08-20), findings N47–N49.
- **`decisions`** — **O-8 and O-9 CLOSED (see below), and the conservative default is now stated as
  a pair:** conflicting evidence is **not** a reason to delete an event (S2/S3's rule — never
  suppress on a conflict) and **not** a reason to publish it (S5's rule — never expose on a
  conflict). Also: **all displayed arithmetic is one deterministic module** (`mijual.calc` —
  D-day in KST, inclusive windows, floored 단수주, Decimal 원 rounded once), which is handoff §3.6's
  *계산은 결정론* clause in code and the arithmetic `P2.S8` inherits. Source: `P2.S5` result
  (2026-08-20), findings N44/N48/N50.

- **`architecture`** (same note as the S1–S5 entries) / **`operations`** — **the job topology landed
  (P2.S6): the pipeline runs on a schedule, and the schedule is part of the durable stack
  description.** `mijual.scheduler` = Celery beat + worker on the compose Redis (host 6380,
  `scheduling` profile — broker, result backend and lock store) running
  **`collect → bodydoc → extract → gates`** in that fixed order (each stage consumes what the
  previous persisted), as `mijual.daily_pipeline` plus one task per stage. Schedule:
  **07:30 and 19:30 KST daily over a rolling 14-day window, Sunday 04:30 over 90 days**, with
  **timezone `Asia/Seoul` explicit** (`enable_utc=False`) and the window anchored on KST rather than
  the host clock. Two operational invariants belong in the doc: (a) **every stage runs under an
  explicit ceiling** — collect ≤ 500 requests, bodydoc ≤ 200, extract ≤ 60 LLM calls per run
  (weekly 1500/600/60) — and a budget-exhausted stage is a *reported status*, not a failed run;
  (b) **one lock, `mijual:lock:pipeline`, on every corpus-writing entry point**, because re-running a
  window is free (N14/N25) but two concurrent runs double-fetch, and spent quota is the one thing
  idempotent upserts cannot repair. Restates the P2→P3 boundary from the scheduling side: **nothing in
  the scheduler is reachable from a request path**, the board renders persisted rows filtered by
  `Event.exposure_state`, so a dead worker leaves it **stale, never dark** (결격). Also record the
  broker-free fallback `python -m mijual.scheduler once [--offline]` — the same code path, 0
  requests / 0 calls offline, and the tool `P2.S7`/`P2.S8` reuse. Source: `P2.S6` result (2026-08-20),
  findings N52–N56.

- **`data`** / **`product`** — **② CB 오버행 landed (P2.S7), and it is the first rights type
  whose exposure test is not a 본문 reading.** Collection: `cvbdIsDecsn` → `전환사채권발행결정` is
  a normal collector target (so the **scheduled** daily pipeline picks ② up with no new task and
  no new beat entry), matched by **exact** parenthetical equality — the same `pblntf_ty=B` stream
  carries 자기전환사채매도결정 / 만기전취득결정 / 매수선택권행사자지정 / 신주인수권부사채권발행결정
  / 교환사채권발행결정 (EB, out by D-1), all of which a substring match would collect. Corpus:
  **2025-06-01 → 2026-08-20, 530 CB originals + 1,181 기재정정, 673 events, 584 live requests**
  (▷ ~36 originals/month, consistent with P1's ▷ ~35/month for 2026). **Exposure semantics for
  ②:** exposable iff not suppressed / not withdrawn / no blocking flag **and** the countdown API
  fields all parse on the current version (전환가액 `cv_prc`, 전환청구기간 `cvrqpd_bgd`/`_edd`,
  오버행 `cvisstk_cnt`/`cvisstk_tisstk_vs`) — **no 본문 required**, because ②'s countdown is
  entirely `API` tier (N6). Two new event states join the documented set: `no_detail` and
  `incomplete_api_row` (파이온엑스 `20260722000285` states a 38.45 % dilution with no
  전환청구기간). **해외/USD rule recorded: exposable iff the KRW fields parse, never on `ovis_*`**
  (one case, 헝셩그룹 `20260213002703`, HKD, passes on its KRW values). The D-1 backfill condition
  is met and measured: **33 ② events open 전환청구 within 30 days of 2026-09-07, 82 within 90,
  152 within 180, max 오버행 67.8 %** — against **1** before the backfill, because a CB filed in
  2025-H2 opens ~12 months later. Board total **457 exposable events (① 25, ③ 10, ② 422) / 280
  renderable fields**, up from 35 / 157. Source: `P2.S7` result (2026-08-20), findings N57–N59,
  N64, N66.
- **`data`** — **철회 and gates 6–8 are now corpus-measured for ②, and §7 #8 changed.** The N47
  row-shape detector generalises to ② **unchanged**: over **808 ② 본문 / 4,627 정정사항 rows** the
  word `철회` appears in 10 정정 후 cells, the shape accepts **9**, and **all 9 are withdrawals**
  (precision 9/9, against 71 % keyword false positives on ①/③) — **8 ② events withdrawn**. Record
  the mechanism, because it is a documented API behaviour: **a withdrawn CB keeps its detail row
  and OpenDART blanks all 46 fields to `-`**, so the completeness rule blocks it as a *silence*
  and only the 정정사항 row turns that into `이 사채 발행은 철회되었습니다` with a span — and a
  blank row is **not** proof of a withdrawal (비트플래닛 `20260616000274` is blank and is not
  one). Gates: **#6 리픽싱 held exactly as §7 wrote it — 본문 floor == API
  `act_mktprcfl_cvprc_lwtrsprc` in 29/29 comparable rows, 0 mismatches**; **#8 보호예수 had to
  move** — a CB states 전매제한 as a **duration, not a date** in 31 of 62 rows, and the rows that
  did carry a date carried one the *model* computed, so the 해제일 is now **derived
  deterministically** (`mijual.calc.lockup_release_date` = API 납입일 + 개월수) and a stated date
  is checked against that derivation (31 failures → 3). The 4 remaining ② failures are one
  finding worth documenting: an API-backed gate is also an **identity** check — it caught 3 정정
  filings paired to the wrong 사채 that no other layer sees. Source: `P2.S7` result (2026-08-20),
  findings N60–N63.
- **`decisions`** / **`operations`** — **D-4 amended by operator directive (2026-08-20): the
  Gemini thinking level is per task, `LOW` for routine schema extraction, the project preset
  (HIGH) reserved for reasoning.** N35 recorded the preset as untouchable; it is now a knob the
  code sets deliberately. Mechanism to document: gemini-3.7-flash takes
  `ThinkingConfig(thinking_level=MINIMAL|LOW|MEDIUM|HIGH)` (not the older `thinking_budget`), and
  **omitting the field entirely** is what inherits the preset. Measured on one real extraction
  prompt: preset **866** thinking tokens → explicit `LOW` **0**, **−21 % ▷ cost**, with **every
  gated value identical** (only free-text prose wording differs). Policy as implemented: the three
  prose tasks and any unlisted task run `LOW`; the **정정 해석** task keeps the preset because it
  is the only task that reasons and its quality measurement (N41) was taken there. Every call now
  records the level it ran at (`extraction_call.thinking_level`), because a ▷ cost figure is only
  comparable across runs if the level behind it is known. Source: `P2.S7` result (2026-08-20),
  finding N65.

- **`data`** / **`product`** — **the 소멸 신주인수권 estimate landed (P2.S8), and it added a
  fourth document family plus a fourth ① source to the documented data model.** (a)
  **증권발행실적보고서** (`pblntf_ty=C`, filed on the 납입일) is the 청약-결과 source the field
  matrix never surveyed, and it is **entirely `본문-label` tier — 0 LLM calls**: `Ⅶ` gives
  발행 증서 / 증서 청약 / 초과청약, `Ⅷ` the 실권주, `3.` the 계 row whose 최종 금액 ÷ 수량 **is**
  the 확정발행가 (agrees with 본문 `6. 확정발행가` on **31/31** offerings that state both), `1.`
  the schedule that binds the report to its event (**32/32 `schedule_match`**). Two forms: the
  standard 주식 form and the 집합투자증권 (REIT) form, which has no `Ⅶ` section. (b) **`유무상증자결정`
  (`pifricDecsn`, form 11308) is an ① source** — same numbered 유상 section, 10/10 target labels,
  `18. 신주인수권양도여부` — and was invisible to every earlier run; **7 of the 32 offerings that
  lapsed in 2026 were filed this way**. Registered in `collect.targets`, and the two `ic_mthn`
  readers now accept its `piic_ic_mthn` prefix. (c) Storage: a new **`performance_report`** table
  (sibling to `filing_version`, not a version of it — a 실적보고서 must never become an event's
  `latest_version`), keeping `Snapshot`'s evidence contract (raw ZIP + `content_sha1`) plus a
  `facts` JSONB in which every figure carries its char span. Source: `P2.S8` result (2026-08-20),
  findings N67–N71.
- **`data`** / **`decisions`** — **the 소멸가치 method, and the correction to how a year is
  framed.** ▷ 증서 이론가치 = **`확정발행가 × 할인율 / (1 − 할인율)`**, derived by inverting the
  filing's own 발행가 산식 (DART-only — there is no price feed); the identity holds for both the
  1차 (cum-rights, whose `증자비율` term *is* the 권리락 adjustment) and the 2차 (ex-rights)
  formula, so no formula branch is needed, and a filer who omits the 증자비율 term gives the
  band's lower edge (`× 1/(1+배정비율)`). 소멸 증서 수 = **발행 증서 − 증서 청약**, never
  최초배정 − 청약 (단수주 was never issued as a 증서, and the filer's own 실권주 cell disagrees in
  **5 of 31** filings). All of it in `mijual.calc`, unit-tested, no LLM. **Framing rule to
  record: a lapse year is defined by the 증권발행실적보고서, not by the 주요사항보고서** — the 청약
  lands 2–6 months after the 결정, and only **10 of the 32** 2026 lapses were reachable from a
  2026-filed corpus. Source: `P2.S8` result (2026-08-20), findings N68, N70, N72.
- **`operations`** — **the corpus is not a census, and completeness needs two sweeps.** A
  `list.json` census over the *result* filings surfaced three 2026 KOSDAQ ① originals that
  `P2.S2`'s run had missed although discovery finds them today (레이저옵텍 `20260109000634`,
  RF머트리얼즈 `20260408002647`, 피엠티 `20260409002139`), and one offering the census itself
  cannot see (KB스타리츠 `20260423000439`, filed as 증권발행실적보고서(집합투자증권) outside
  발행공시 entirely) which only a **per-event backstop** — one corp-scoped, unfiltered
  `list.json` per closed-청약 event — caught. Record both as standing practice, plus the cheap
  repair path: **targeted per-corp adoption** costs 3–4 requests per offering (22 offerings for
  ~90 requests) against ~300 for a market-wide historical re-run, lands ordinary corpus rows, and
  *heals* `unpaired_correction` placeholders through the existing `superseded_by_pairing` path.
  Slice spend: ~337 requests of a 500 ceiling, 22 LLM calls at `thinking_level=LOW` (▷ $0.2186).
  Source: `P2.S8` result (2026-08-20), findings N73–N75, N79.
- **`product`** — **the number the landing opens with, and the measured price of the gate.**
  ▷ **718.1억원** (band ▷ 549억~718억) of 신주인수권 value lapsed unexercised in 2026 YTD across
  **32** 주주배정 유상증자; **51,253,956 of 365,527,824 배정 증서 (14.02 %)** were neither
  subscribed nor sold; per-offering 소멸률 **2.51 %–49.09 %**, median 11.60 %; largest single
  loss ▷ 206.4억원 (한화솔루션). **18 offerings are still open**, 11 with a 청약 ahead — the
  retrospective number and the live board are the same pipeline. And the trust claim, priced:
  three offerings with a citable 실권 count are **excluded from the total** because their 할인율
  extraction failed its citation gate — **▷ 49.2억원, 6.4 % of the headline, deliberately left
  on the table**. Every committed figure is regenerated by
  `python -m mijual.estimate report --korean` at 0 requests and 0 calls. Source: `P2.S8` result
  (2026-08-20), findings N76, N77.

- **`operations`** / **`data`** / **`product`** — **the 2026 ①/③ corpus is now a swept census,
  and the board numbers move with it (P2.F1).** N73's "the corpus is not a census" is now
  quantified: full-2026 discovery returns 2,279 target filings and **244 of them (10.7 %) had
  never been stored** — `piicDecsn` 192/1,145, `pifricDecsn` 4/25, `cmpMgDecsn` 48/286 (17
  originals) — while **`cvbdIsDecsn` was 0/823**, because `P2.S7`'s backfill window strictly
  contains 2026. Record the operational rule that follows: **a wider historical backfill
  immunises a rights type against the run gap, and the gap itself is measurable for free**
  (discover offline, diff the `rcept_no` set against stored versions) before any request is
  spent. Board effect, all regenerated from the DB: **exposable events 479 → 488 (① 47 → 50,
  ③ 10 → 16, ② 422 unchanged), renderable field instances 388 → 409**, ③ blocked
  `no_document` 9 → 1. **`유무상증자결정` (`pifricDecsn`, N71) is confirmed live on the board**,
  not just in the retrospective: 9 events, all `warrant_confirmed`, and the 2 the sweep added
  are open offerings (퓨쳐켐 청약 2026-09-04 — tied soonest — and 엘앤씨바이오 2026-10-15). The
  **소멸 headline is unchanged at ▷ 718.1억원 / 32 offerings / 14.02 %** (it is framed on the
  증권발행실적보고서, N72, and S8 had adopted every offering that filed one), while the *live*
  pipeline grows **18 → 23 offerings still open, 11 → 15 with a 청약 ahead**. Also worth a line
  in `data`: filling a collection gap can flip a dormant flag into a blocking one — 디모아's 철회
  moved off an `unpaired_correction` placeholder onto a real `warrant_confirmed` event and now
  correctly blocks it (① `withdrawn` 2 → 3), with the 철회 totals otherwise stable at 15 distinct
  filings (① 6, ② 9). Slice spend: **585 of 700 OpenDART requests, 11 LLM calls at
  `thinking_level=LOW` (▷ $0.0898)**, 0 lines of package code changed. Source: `P2.F1` result
  (2026-08-20), findings N80–N83.

- **`qa`** — **how this repo measures extraction accuracy, landed as runnable machinery
  (P2.S9 Phase A; the measured numbers follow at Phase B).** `mijual.evalset` +
  `evalset/{sample.json,sheet.csv,LABELING.md}`: a **deterministic** (seed 20260907,
  per-stratum seeded shuffle over a sorted pool) stratified sample of **344 (filing, field)
  rows over 99 filings**, labelled through one sheet (**this round: Claude-judged, not
  hand-labelled — see the Phase B note below**), scored at **0 OpenDART requests and
  0 LLM calls** with no database in the read-back path (the sample is frozen to JSON, so a
  label stays meaningful after the corpus moves — N55/N83). The method itself is the durable
  part: **both error directions are measured** — precision of gate-passed/`tbd` fields *and*
  the gate's **over-blocking** rate on the rows it blocked, because a gate can buy any
  precision figure by blocking more (N76 priced one such pattern at ▷ 49.2억원) — rates are
  computed **only** on the random draw with the deliberately over-sampled hard cases reported
  case by case, and every rate carries a **95 % Wilson** interval. Also durable and available
  before any label: the corpus-wide **gate-block rate is 12.2 % (77/633)** and ranges from
  **0 %** (증권발행실적보고서 figures — no model reads them) through **4–8 %** (① prose) to
  **44 %** (③, mostly N46's superseded-API scoping, not misreading). Source: `P2.S9` result,
  findings N84–N88.

- **`qa`** / **`data`** / **`decisions`** — **first measured extraction accuracy, and the
  provenance that qualifies it (P2.S9 Phase B).** **`decisions`:** the operator amended
  P2.S9 on **2026-08-20** to replace the human labelling pass with **Claude self-evaluation**
  ("you self evaluate and self validate. since the extraction done by gemini and you are a
  claude fable. try by yourself."), so the durable statement of accuracy in this repo rests on
  **cross-model judgement — Claude (Opus 5) judging Gemini extractions — and explicitly not on
  human ground truth**; every doc that quotes a number must carry that qualifier, and no doc
  may say "hand-labelled". **`qa`:** on the frozen 344-row sample, **precision of what the
  product would show = 98.6 % strict (213/216 random picks, 95 % Wilson [96–100 %]), 100 %
  with `partial`; 0 `wrong` and 0 `skip` in 344 rows**; the whole strict-error surface is one
  defect class — a 실적보고서 value correctly summed from two table rows but cited by one addend
  (SKC, 에스에너지). The gate's **over-blocking price is 48/48**: every gate-blocked row in the
  sample was a correct reading (30 of them blocks the product wants — `field_absent`,
  `superseded_api_reference`; 18 actionable — stale API reference data, single-span citation
  for multi-line quotes, quantified 개월 withheld for a underived 해제일). The 정정-해석 recall
  proxy is a **floor**: 85.3 % as stored, **88.7 %** re-matched (a matcher bug in
  `check_against_items` understates it), ≈ **99 %** of investor-meaningful items.
  **`data`:** N68's five `lapse_mismatch` filings are **issuer table errors** (a 총계 smaller
  than its own first column), so the exposed contract is "발행사 기재 불일치", never a silent
  reconciliation; `option_schedule` dates carry two conventions (조기상환기일 range vs 청구기간
  range) and need a `date_basis` marker; `rcept_no 20250930000508`'s stored `corp_name`
  (풍전약품) disagrees with its 본문 header (에스씨엠생명과학) — a DART master artifact affecting
  display only. Source: `P2.S9` result (Phase B, 2026-08-20), findings N89–N93.

- **`qa`** — **the cross-model provenance qualifier is now mechanised, not just prose (P2.F3).**
  `evalset/labels.json` carries a `judged_by` block (`judge` / `basis` / `imported_at`), the import
  refuses to write an unstamped file and never inherits a previous judge, and the accuracy report
  prints the block verbatim — so the `qa` version should state *where* the qualifier lives, not a new
  number (all P2.S9 figures unchanged: 339 correct / 5 partial / 0 wrong of 344). Source: `P2.F3`
  result, finding N99.

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
- ~~**O-9:**~~ **CLOSED by `P2.S5` (N47, N48).** A **철회 event is not exposable, and it is not
  deleted**: `Event.exposure_state='withdrawn'` (+ a `withdrawn` review flag and an `exposure_note`
  carrying the 정정사항 row with its span), and the board renders
  **"이 유상증자는 철회되었습니다"** in place of the countdown — a demo asset like the 소규모합병
  suppression. The detector is deterministic, in the gate layer, and keys on the **row shape**, not
  the word `철회` (measured 71 % false positives for the keyword). It found **4** withdrawals, not
  the 2 N39 knew about: 썸에이지 `20260805000454` + 제이알글로벌리츠 `20260205000605` (both were
  exposable) and 디모아 `20260625000227` + 코퍼스코리아 `20260130000680` (already suppressed
  placeholders). **`추후결정` is `tbd`** — exposable, rendered as `추후결정`, and the exposed value is
  structurally `None` so the superseded schedule cannot leak (경남제약 `20260623000409`, 에이전트AI
  `20260619000455`). ▷ The ③/② generalisation of the detector has **no case in this corpus**: it is
  unit-tested on a constructed `회사합병 결정 → 회사합병 철회` row and untested against real data.
- **O-3 (`P2.S9`) — GATE RAISED, waiting on the operator (2026-08-20).** Its two
  prerequisites are answered: the **format** is `evalset/sheet.csv` (one row per
  `(rcept_no, field)`, labels `correct`/`wrong`/`partial`/`skip` in column A, optional
  corrected value in column B; instructions in `evalset/LABELING.md`), and the **precision
  definition** is N84's — strict precision (`partial` counts as a miss, stated beside the
  lenient figure) over **gate-passed/`tbd`** rows of the **random** draw only, with a 95 %
  Wilson interval, reported beside the gate's over-blocking rate on the rows it blocked.
  Cost to the operator: **344 rows / 99 filings / ▷ 75–95 minutes** (N88 lists the two ways
  to shrink it). Closes when the labels return and Phase B computes the report.
- ~~**O-4:**~~ **CLOSED by `P2.S2` (N24).** KONEX (`corp_cls=N`), 2026-01-01~08-19: 30 events, **0
  exposable rights** → no coverage conclusion changes; KOSPI+KOSDAQ stays the frame. `corp_cls=E`
  (기타) was not probed and is judged not worth the requests.
- ~~**O-5:**~~ **CLOSED by `P2.S3` (N28, Doc impact).** `주주우선공모증자` **does not** issue a
  신주인수권증서: the single case (상지건설 `00232007`, 정정 `20260807000339`) uses a 유상증자결정 form
  with **no `18. 신주인수권양도여부` row**, and `신주인수권` occurs **0 times** in its 33,886-char 본문.
  The value was removed from `WARRANT_BEARING_IC_MTHN` and the event is suppressed
  `no_warrant_bodymun`. ▷ Evidence is one filing; the generalisation rests on the form template,
  and the per-document 본문 check would surface a counter-example as a `warrant_conflict`.
- ~~**O-8:**~~ **CLOSED by `P2.S5` (N48).** **`warrant_conflict` blocks exposure.** The rule is
  stated as a pair, and both halves are the same conservative default: conflicting evidence is
  **not** a reason to delete an event (S2/S3 — never suppress on a conflict) and **not** a reason to
  publish it (S5 — never expose on a conflict). The blocking-flag set is `warrant_conflict`,
  `detail_conflict`, `event_key_collision`, `hint_split_evidence`; a blocked event keeps every
  snapshot, extraction and gate verdict and is simply not rendered. In practice the only
  `warrant_conflict` case (제이알글로벌리츠 `01415892`) is **also 철회**, and 철회 outranks it as the
  more specific truth — so the policy is asserted by test rather than by the corpus
  (`tests/test_gates.py::test_the_exposure_contract_blocks_a_flagged_event_and_shows_only_gated_fields`).
  Cost measured: 3 events blocked on `detail_conflict` (한솔테크닉스, 이렘, 모다이노칩), all of which
  are unblockable by a **collector-side** key split, not by relaxing this rule — see N51.
- **O-6:** ▷ meaning of `estkRs.일반사항.exstk/exprc/expd` (2/35 filled) — not needed by any MVP field;
  answer only if it falls out for free.
- **O-7 (carried from P1 as Q7, deferred to P2/P3):** 증권사 MTS 권리 메뉴 coverage matrix (handoff §4,
  "미발견 ≠ 부존재") — differentiation evidence for the 기획서, not pipeline code. Must not be
  forgotten; a `defer-job` is the right home if no slice absorbs it.
