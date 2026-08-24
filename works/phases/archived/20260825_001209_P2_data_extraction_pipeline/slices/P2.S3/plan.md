# Plan: P2.S3 — 본문 deterministic parse layer: labeled rows, CORRECTION block, citation spans

_Mode: auto. Plan written inline by the orchestrator._

## Context

S1 gave us the package/schema/client; S2 collected the 2026 ①③ universe (434 events / 1,226 versions / 1,612 snapshots in the docker Postgres, 5433) and left a concrete worklist: 145 `*_ambiguous` pairings, 99 `unpaired_correction` events, 36 `event_key_collision` + 3 `detail_conflict` flags, O-5 (`20260807000339` 본문 `18.`), and the ① filter's final test (본문 `18. 신주인수권양도여부` — `ic_mthn` is provisional). This slice builds the deterministic 본문 layer that everything reads: it is a pure function of a document (testable offline against 59+ cached ZIPs), it makes the layer-2 citation-span gate possible, and it must never cost an LLM call for anything it can read.

Read first: `works/phases/active/P2/phase.md` (N19–N26 especially), `works/phases/active/P2/slices/P2.S2/result.md` (§Open items — your worklist), `docs/reference/dart/field-matrix.md` §1.3, §4.1, §5. The proven parse logic to lift: `scripts/spike/corrections.py` (`top_tables`, `text_of`, `table_rows`, `parse_correction`) and `scripts/spike/survey.py` (`LABELS`, `labelscan`). Spike files stay untouched.

## Deliverables

1. **Parse library** (`src/mijual/bodydoc/` — name is yours) — pure functions over a document snapshot's decoded XML:
   - Document model: decoded text with **offset preservation** — the spike's `text_of` collapses whitespace and loses positions; this layer must be able to report a `(start, end)` character span into the stored decoded XML for any value it extracts, because the layer-2 "원문 인용 스팬 존재" gate verifies spans against the snapshot. Design freely (offset map from normalized→raw, or raw-text search) but the span must locate the value in the snapshot as stored.
   - Top-level table iteration + row/cell extraction (lift the spike's nesting-aware `top_tables` / `table_rows`).
   - **① labeled-row extraction**: the 10 stable numbered labels (field-matrix §1.3 / spike `LABELS`) → typed values (Korean dates `YYYY년 M월 D일` → ISO, ratios/decimals, enums like 양도여부), each with its span. Handle multi-date rows (청약예정일 대상자별) conservatively — a raw string + span beats a wrong parse.
   - **`<CORRECTION>` parse**: target report, 최초제출일 (hint), and the `3. 정정사항` table (항목 / 정정사유 / 정정 전 / 정정 후) with spans — 40/40 parseable in P1.
   - **증권신고서 section slicer**: split by `<TITLE ATOC>` markers, return named sections with offsets. Never feed a 증권신고서 whole to anything (0.6M–1.9M chars) — this slicer is S4's only sanctioned access to that regime.
2. **CORRECTION backfill job** (CLI, e.g. `python -m mijual.bodydoc backfill [--offline] [--max-requests N]`): for `기재정정` versions with a 본문 snapshot (fetch missing ones within budget, see §Budget), parse the CORRECTION block; store `declared_original_dt` on the version; re-evaluate S2's pairing: hint agrees → e.g. `pairing_method += '_hint_confirmed'` (or a cleaner scheme — record it); hint disagrees or resolves an `*_ambiguous` case → resolve or flag (`hint_mismatch`), and attack the `unpaired_correction` / `event_key_collision` / `detail_conflict` worklists where the hint decides them. Never delete evidence; relabel (S2's `superseded_by_pairing` pattern).
3. **① filter confirmation job**: for unsuppressed ① events with 본문 available, read label `18. 신주인수권양도여부` (+ 증서 상장여부): confirms warrant → mark confirmed (a flag or field); clearly denies → suppress with a new reason code (e.g. `no_warrant_bodymun`); conflicts with `ic_mthn` → keep live + flag (S2's "never suppress on conflict" rule). Close **O-5**: read `20260807000339`'s `18.` and record the answer as a finding.
4. **NO field-materialization tables.** Extracted-field storage (with tier, span, gate status) is S4's schema design, shared by the label tier and the LLM tier. S3 persists only: `declared_original_dt`, pairing/flag updates, suppression updates, and whatever tiny column additions those need (free under N16). Parsed values are recomputed on demand via the pure functions.

## Budget (O-1 still open)

Live requests ≤ ~300 total, via the client's `max_requests`. Priority for 본문 fetches: (a) every version of the 53 exposable events, (b) corrections on the `*_ambiguous`/collision worklist, (c) `unpaired_correction` events' own 본문 (their CORRECTION hint may identify them). Offline cache first — 59+ ZIPs cost nothing.

## Tests (terse)

Against cached ZIPs only: 계양전기 `20260724000546` label extraction (10/10 with typed values + spans verified by slicing the raw text), one CORRECTION parse with known before/after items (e.g. the 에넥스 or a cached pair), span-existence round-trip (extract → slice snapshot text by span → substring matches), section slicer on the one cached 증권신고서 if present. No invented XML.

## Out of scope

LLM anything (S4), gates beyond span mechanics (S5), Celery (S6), ② (S7). No commits, no state transitions, no doc-new-version — Doc impact one-liners + numbered N-notes to phase.md.

## Verification

- `.venv/bin/python -m pytest` green (existing 14 + new terse cases).
- Backfill run over the collected corpus: report counts — hints parsed, pairings confirmed/resolved/mismatched, worklist deltas (ambiguous 145 → ?, unpaired 99 → ?, collisions 36 → ?), suppressions added by 본문 18, O-5 answer.
- Request count reported, ≤ budget; no key material anywhere.
- `python3 scripts/workflow.py validate` passes.
