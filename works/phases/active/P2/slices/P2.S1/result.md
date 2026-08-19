# Result: P2.S1 — package scaffold, storage schema, DART client port

Status: **done**. All six deliverables landed; the smoke runs fully offline against the P1
response cache and persists to the local docker Postgres. First real (non-throwaway) code in the repo.

## What exists now

```
pyproject.toml            hatchling, src layout, deps: sqlalchemy>=2.0, psycopg[binary]>=3.2; dev: pytest
compose.yaml              postgres:16 (host 5433, named volume, healthcheck) + redis:7 behind a profile
src/mijual/config.py      Settings + .env parsing, masking __repr__, lazy secret requirement
src/mijual/dart/client.py DartClient — the port of scripts/spike/dart.py (spike untouched)
src/mijual/db/models.py   Corp / Event / FilingVersion / Snapshot (the N2 design)
src/mijual/db/session.py  engine, session factory, session_scope, create_all, reset_schema
src/mijual/db/repository.py  idempotent ensure_corp / ensure_event / ensure_version / ensure_snapshot
src/mijual/smoke.py       `python -m mijual.smoke` — offline end-to-end evidence run
tests/                    9 tests, two files
```

`.gitignore` gained `var/` (the pipeline's own response cache) and `*.egg-info/`.
`.venv/` created and the package installed editable (`.venv/bin/pip install -e ".[dev]"`).

## The DART client port

All four proven behaviors (N7 / field-matrix §6) carried over verbatim in effect:
`None` params dropped rather than serialized; `group[]` vs flat `list` normalized by `groups()`;
503 retry with the same 4-try / `1.5·n` backoff; `PK` magic checked on `document.xml`.
Key safety is structural: the key is appended only to the live request URL, never to the cache
filename, the recorded `_url`, or any exception text.

**Cache byte-compatibility is verified, not assumed.** `DartClient.cache_path` reproduces the spike's
scheme exactly (sorted key-stripped querystring → `sha1[:12]` + a 60-char sanitized hint), so
`cache_dir=scripts/spike/samples` makes the 1,002 cached P1 responses (59 본문 ZIPs) a working
offline fixture path. A golden filename is pinned in `tests/test_dart_client.py` — if the scheme ever
drifts, the test fails instead of the cache silently going cold.

Two deliberate improvements over the spike, both recorded as decisions:

1. **A non-ZIP `document.xml` body is rejected (`NotAZipError`) and never written to the cache.** The
   spike cached whatever came back, so one transient error body would have poisoned a fixture
   permanently. All 63 currently cached document files were checked: 63/63 start with `PK`, so nothing
   in the existing cache is affected.
2. **`offline=True` mode** — a cache miss raises `CacheMiss` instead of reaching the network, and the
   key is resolved lazily so an offline client never needs one. This is what makes the smoke and the
   tests key-free.

## Storage schema (the N2 design)

- `Corp` — `corp_code` PK, name, `stock_code`, `corp_cls`.
- `Event` — unique **`(corp_code, report_subtype, original_rcept_dt)`**; `report_subtype` is the detail
  endpoint name (`piicDecsn`, `cvbdIsDecsn`, `cmpMgDecsn`, …); `rights_type` native PG enum
  `R1/R2/R3` (① 유증 신주인수권 / ② CB·EB 오버행 / ③ 매수청구권).
- `FilingVersion` — FK event, `rcept_no`, `rcept_dt`, `correction_kind` (`original` / `기재정정` /
  `첨부정정`, derived from `report_nm`), `declared_original_dt` (the filer-entered `<CORRECTION> 2.`
  hint — stored as a hint, never a key), `observed_at`; unique `(event_id, rcept_no)`.
- `Snapshot` — FK version, `source` (endpoint name or `document`), `captured_at`, `payload_json`
  (JSONB on PG) **or** `payload_bytes` (BYTEA for 본문 ZIPs), `content_sha1`, `byte_size`;
  `CHECK` exactly one body; unique `(filing_version_id, source, content_sha1)`.

Verified in the live database: `payload_json` is `JSONB`, `payload_bytes` is `BYTEA`, every timestamp is
`timestamptz`, `rights_type`/`correction_kind` are native PG enum types, and both unique constraints
plus `ck_snapshot_exactly_one_body` exist.

**S2's correctness filter has a home without a migration:** `suppressed_reason` (short code, plain
`VARCHAR` on purpose — *not* an enum, so a new reason costs nothing), `suppressed_note`,
`suppressed_at`, plus `Event.suppress()` / `Event.is_suppressed`. A 제3자배정 유증 or a 소규모합병 is
therefore *collected and recorded as excluded*, never silently dropped.

**No Alembic (deliberate).** Schema evolves through `create_all` / `reset_schema` (drop + recreate)
for the whole of P2, because every row is re-collectable from the response cache or the API. The one
edge worth knowing: `rights_type` / `correction_kind` are native PG enums, so adding a member means a
`reset_schema` (or a manual `ALTER TYPE … ADD VALUE`) — which is why the S2-facing suppression columns
were kept as free `VARCHAR`. Revisit only if P3 needs migrations against data that cannot be rebuilt.

**Idempotency answer (the plan asked which):** **upsert, not failure.** `ensure_*` are get-or-create on
the unique keys; a snapshot whose body hash is unchanged is a no-op, while a changed body always
becomes a new row — which is precisely what the old→new 정정 diff needs.

## Validation

| command | outcome |
|---|---|
| `.venv/bin/python -m pytest` | **9 passed** in 0.13s |
| `docker compose up -d postgres` | container `mijual-postgres` healthy (host 5433) |
| `.venv/bin/python -m mijual.smoke` | **OK** — see the evidence below |
| `.venv/bin/python -m mijual.smoke --keep` | **OK** — counts unchanged across processes (1/1/3/5) |
| live one-request probe (`list.json`, 5 rows) | `000 정상`, cache written to `var/dart-cache`, recorded `_url` key-free |
| key-leak grep across every new file + `var/` | **0 files** contain the key value |
| `python3 scripts/workflow.py validate` | OK (see below) |

Smoke output (no key material anywhere; `Settings.__repr__` masks secrets as `<set>`/`<unset>`):

```
collected : 3 list rows, 1 detail row(s), document 8044B — all cache hits, no key, no network
persisted : corp=1 event=1 version=3 snapshot=5
re-run    : corp=1 event=1 version=3 snapshot=5
event key : (00102618, piicDecsn, 2026-05-08)
versions  : 3  (latest 20260724000546)
  - 20260508000928 2026-05-08 original  [list:bb193494(246B)]
  - 20260611000483 2026-06-11 기재정정   [list:11c958ca(260B)]
  - 20260724000546 2026-07-24 기재정정   [list:3c16be68(257B), piicDecsn:55b9179e(494B), document:43040d35(8044B)]
N2 check  : list gave 3 versions, piicDecsn gave 1 row(s) -> ['20260724000546']
본문 check : ZIP 8044B -> 31376 XML chars, '신주인수권증서' ×17, CORRECTION block: True
```

The fixture is 계양전기 (`00102618`), the field matrix' worked ① example. The smoke **re-measures N2
live**: three versions visible in `list.json`, exactly **one** row from `piicDecsn` carrying only the
newest `rcept_no` — the superseded structured values are gone unless snapshotted. The 본문 numbers
(31,376 XML chars, 신주인수권증서 ×17) reproduce field-matrix §5 exactly, which independently confirms
the ported ZIP/decoding path.

Tests (terse, 9 total, no fixture sprawl): cache-path golden filename + key/`None` stripping, the P1
cache actually resolving as a fixture (skipped when `samples/` is absent, since it is gitignored),
`None`-param dropping, `group[]` normalization, offline `CacheMiss` without a key, the event key,
DB-level rejection of a duplicate event key, snapshot idempotency vs a changed body, and
`CorrectionKind.from_report_nm`. DB tests run on in-memory SQLite so `pytest` needs no docker; the
models stay Postgres-first via `with_variant`.

## Deviations from plan.md

1. **Redis is in `compose.yaml` but behind a `scheduling` profile** (the plan left this to the
   executor). `docker compose up -d postgres` and a bare `up` never start it; S6 runs
   `docker compose --profile scheduling up -d redis`. Host port 6380 (and `DEFAULT_REDIS_URL` matches),
   keeping the machine's installed-but-stopped `redis-server` on 6379 out of the way. Postgres is on
   host 5433 for the same reason.
2. **Added `src/mijual/db/repository.py`** (4 small `ensure_*` upserts). Not named in the plan, but the
   smoke's idempotency requirement needs them and they are storage-side, not collector logic — S2 still
   owns polling, windows and 정정 discovery.
3. **One live OpenDART request** (5 rows) beyond the offline path, to prove the online fetch + cache
   write + key-safe `_url` actually work. Everything else ran offline.
4. `NotAZipError` / `offline` mode are behavior changes vs the spike (both described above).

## Bug found and fixed during the slice (worth remembering)

`Snapshot.payload_json` initially stored a Python `None` as the **JSON scalar `'null'`**, not SQL
`NULL`, which silently defeated `ck_snapshot_exactly_one_body` — the check constraint fired on a
document snapshot that was in fact perfectly valid. Fixed with
`JSON(none_as_null=True).with_variant(JSONB(none_as_null=True), "postgresql")`. It would have bitten
Postgres identically; any later JSON column in this schema needs the same flag.

## Handover to P2.S2

- Import surface: `from mijual.dart import DartClient, rows, groups`;
  `from mijual.db import Event, FilingVersion, Snapshot, RightsType, make_engine, session_scope`;
  `from mijual.db.repository import ensure_corp, ensure_event, ensure_version, ensure_snapshot`.
- Develop offline with `DartClient(cache_dir=SPIKE_CACHE_DIR, offline=True)` — no key, no network,
  1,002 responses; switch to `DartClient()` for live runs (cache lands in gitignored `var/dart-cache`).
- `ensure_event` takes `original_rcept_dt` — for a 정정 that value comes from the **paired original**
  (N3), never from the correction's own `rcept_dt`. `declared_original_dt` is where the filer's
  `<CORRECTION> 2.` claim goes, as a hint.
