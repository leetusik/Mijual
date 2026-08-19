# Plan: P2.S2 — collector for ① 유증 + ③ 매수청구: new filings and 정정 discovery

_Mode: auto (operator directive after P2.S1). Plan written inline by the orchestrator._

## Context

S1 landed the package (`src/mijual`), the `Corp → Event → FilingVersion → Snapshot` schema with the N2 event key, idempotent `ensure_*` upserts, and a cache-byte-compatible `DartClient` with `offline=True` against `scripts/spike/samples/` (1,002 responses). This slice adds the collection logic on top: discovery, pairing, detail/본문 snapshotting, and the two correctness filters — for rights types ① (유상증자결정 → `piicDecsn`) and ③ (회사합병결정 → `cmpMgDecsn`). ② is S7's. 분할합병·주식교환 are OUT of MVP scope (D-1) — do not collect them.

Read first: `works/phases/active/P2/phase.md` (N2, N3, N11–N18 from S1), `works/phases/active/P2/slices/P2.S1/result.md` (§Handover — import surface, `ensure_event` semantics), `docs/reference/dart/field-matrix.md` §4 (pairing + version semantics) and §6 (API constraints).

## Deliverables

1. **Collector module** (`src/mijual/collector/` or `src/mijual/collect.py` — executor's call) with a windowed collection function S6 can later schedule, plus a CLI entry (`python -m mijual.collect --bgn YYYYMMDD --end YYYYMMDD [--offline]`). Idempotent: re-running a window must not duplicate versions (S1's upserts already guarantee the storage side).
2. **Discovery** via `list.json` (`pblntf_ty=B`, KOSPI `Y` + KOSDAQ `K`, paging to `total_page`, window ≤ 3 months without `corp_code` — split longer requests into ≤3-month chunks):
   - Target subtypes parsed from `report_nm`'s parenthetical: `유상증자결정` (①) and `회사합병결정` (③).
   - Collect **originals and `[기재정정]` rows**. `[첨부정정]` rows: record as a `FilingVersion` (correction_kind already supports it) but skip detail/본문 re-fetch — attachment-only (field-matrix §4.1).
3. **정정 pairing (N3)** — for a `[기재정정]` row, find the original **without 본문 parsing** (that's S3's layer): query `list.json` with `corp_code` (no 3-month cap applies) for the same corp + same subtype, take the **nearest earlier** original row; its `rcept_dt` becomes the event's `original_rcept_dt`. This is the validated fallback arm of the §4.1 algorithm (the `<CORRECTION>` 최초제출일 hint is 본문-derived; S3 will backfill `declared_original_dt` and flag pairing mismatches later). An unpairable correction (original before the corp's earliest visible listing) is recorded as its own event flagged for review, never silently dropped — state how in result.md.
4. **Detail + 본문 snapshotting** per event: fetch the detail endpoint (`piicDecsn` / `cmpMgDecsn`) windowed on the **original** filing's date (never the correction's — N3: a correction-date window returns `[]` 40/40), snapshot the JSON body; fetch `document.xml` for each newly observed `rcept_no` and snapshot the raw ZIP bytes. No 본문 parsing beyond what S1's client already does (ZIP validity) — parsing is S3.
5. **Correctness filters** (constraints section of phase.md; record, never silently drop):
   - ① — `ic_mthn` not in the 주주배정 계열 (`주주배정후 실권주 일반공모`, `주주배정증자`) → `Event.suppress(reason)` e.g. `no_warrant_class` (제3자배정증자, 일반공모증자). `주주우선공모증자` stays UNsuppressed pending O-5 — flag it in result.md if one is seen. Note in code that final exposure additionally requires 본문 `18. 신주인수권양도여부` confirmation (S3/S5) — `ic_mthn` alone is provisional.
   - ③ — `mg_stn` = 소규모합병 (and 간이합병 if observed) or absent `aprskh_*` fields → suppress with reason `no_appraisal_right`. These are the 6-overlapping-windows demo asset; keep them collected.
6. **Evidence run** — offline tests first, then one bounded **live** collection: a recent window (e.g. 2026-06-01 ~ 2026-08-19, chunked) for both subtypes, cache to `var/dart-cache`, persist to the docker Postgres (`mijual-postgres` is running on 5433). Report counts in result.md: events / versions / snapshots / suppressed-by-reason, and whether the live numbers are consistent with P1's measured universe (▷ ~4–5 ①/month, ~2 ③/month real events). **Keep total new API requests modest (≤ ~300)** — the daily quota is unmeasured (O-1).
7. **O-4 cheap check (optional, if it costs ≤ a handful of requests):** one `list.json` count probe for `corp_cls=N` (KONEX) on the same window/subtypes, recorded as a finding — answers whether KONEX changes any coverage conclusion.

## Tests (terse)

A few high-value offline cases against the spike cache (`DartClient(cache_dir=..., offline=True)`): subtype/`report_nm` parsing incl. `[기재정정]`/`[첨부정정]` detection; nearest-earlier pairing on a cached corp with a known chain (계양전기 `00102618` has 3 versions in cache; 디모아's 6-correction chain if its list rows are cached); the ① `ic_mthn` filter and ③ 소규모합병 suppression paths. No fixture sprawl — reuse cached bodies, don't invent JSON.

## Out of scope

본문 XML parsing / labels / CORRECTION content (S3), LLM anything (S4), gates (S5), Celery (S6), ② CB (S7). No commits, no state transitions, no doc-new-version — durable-truth changes go as one-line Doc impact notes to phase.md.

## Verification

- `.venv/bin/python -m pytest` green (existing 9 + new terse cases).
- Offline collect run over cached data persists expected events idempotently (run twice, counts stable).
- Bounded live run: counts reported with evidence, no key material anywhere, requests ≤ ~300.
- `python3 scripts/workflow.py validate` passes.
