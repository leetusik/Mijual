# Plan: P2.S4 — LLM extraction (layer 1): Gemini schema extraction for the 10 fields + 정정 재추출

_Mode: auto. Plan written inline by the orchestrator._

## Operator inputs (resolved 2026-08-19, O-1/O-2 closed)

- **`GEMINI_API_KEY` is now in `.env`** (the "changple5" credential). Never echo/log/commit it.
- **Model id: `gemini-3.7-flash`.** The thinking/effort level is preconfigured on the credential/project side ("changple5") — do **not** hardcode a thinking config; make one minimal probe call first, inspect the response's usage metadata (thinking-token counts etc.), record what the preset actually returns in result.md, and only pass an explicit thinking setting if the probe shows the preset is absent. D-4's architecture stands: gates mandatory, all calculation deterministic.
- **OpenDART quota: 20,000 requests/day per key** (operator + community-doc corroborated, ▷ official page defers to a homepage notice). Record as an O-1-closing note in phase.md. The `max_requests` ceiling stays as good practice.

## Context

S3 left a deterministic parse layer (`mijual.bodydoc`): typed ① label values with verified citation spans, `<CORRECTION>` 정정사항 rows with before/after, and a 증권신고서 `<TITLE>` slicer. The corpus (docker Postgres, 5433 — do NOT reset) holds 434 events / 1,226 versions / 364 본문 snapshots; 28 ① events are `warrant_confirmed`, 15 ③ exposable, 1 `warrant_conflict` (제이알글로벌리츠 — S5 owns its exposure decision). This slice is the only one that spends money and the only non-deterministic one: schema-based Gemini extraction for exactly the 10 prose fields of field-matrix §7, plus 정정 prose re-extraction/diff (field 10). Anything `API` or `본문-label` never goes through the LLM.

Read first: `works/phases/active/P2/phase.md` (N27–N33, Constraints), `works/phases/active/P2/slices/P2.S3/result.md` (the bodydoc API and its span contract — `doc.verify(span, value)`), `docs/reference/dart/field-matrix.md` §7 (the 10 fields + their gates) and §1.1 (본문 위치).

## Deliverables

1. **Gemini client wrapper** (`src/mijual/extract/` — layout yours): `google-genai` SDK as a new dependency (add to pyproject); key from `Settings` (lazy, masked); model `gemini-3.7-flash`; structured output via response JSON schema; retry/backoff on transient errors; a **call counter + `max_calls` ceiling** (same pattern as the DART client's request budget) and a per-run cost/token report.
2. **Field schemas for the 10 targets** (§7): per-field JSON schema asking for (a) the value in a normalized shape (dates as ISO, ratios as decimals, enums where §7 says enum-ish), (b) a **verbatim quote** of the supporting 본문 passage. **The span is never trusted from the model**: deterministic code locates the quote in the snapshot via the bodydoc layer (its normalize/verify contract) and stores the resolved `(start, end)`; a quote that cannot be located → the extraction is recorded as span-unresolved (S5's citation gate will block it). Input regime: 주요사항보고서 text whole (2.6k–10k chars); 증권신고서 only via the section slicer, and only as a secondary/confirmation source if a field is missing from the 주요사항보고서 — never whole.
3. **Extraction storage** (your schema design — S3 deliberately deferred it): a table (or two) recording event/version FK, field key, extracted value (JSON), located span + document snapshot reference, the verbatim quote, model id, schema/prompt version, token/cost accounting, extracted_at. Leave room for S5 to attach per-field gate verdicts + reason codes without redesign (nullable columns or a separate gate-result table — your call; plain VARCHar for codes per N16/N27 conventions, additive columns via `ensure_columns`).
4. **정정 re-extraction + diff (field 10)**: for corrections on target events, re-extract the prose fields from the new version's 본문 and produce a structured interpretation combining (a) the deterministic 정정사항 before/after rows (bodydoc), (b) prose-field value changes between versions. Output: which fields moved, old → new, with spans on the new version. The deterministic rows are ground truth for *what changed*; the LLM interprets/normalizes, never contradicts them.
5. **Run over the target corpus** (bounded): ① fields 1–5 for the 28 `warrant_confirmed` events (current version first, then corrections for field 10); ③ field 9 for the 15 exposable events; ② fields 6–8 are S7's corpus (skip). Include the `warrant_conflict` event's extraction only if cheap — flagged, not exposed. **Cap total LLM calls ≈ 150–200 for this slice**; report calls, tokens, and an estimated cost in result.md. If the cap forces triage, prioritize ① fields 1–2 (매매기간, 청약 취급처 — the countdown-critical ones) across all events over completing all 5 fields on some.
6. **Probe + tests**: the one-call probe (deliverable via §Operator inputs); tests stay terse and **offline/deterministic** — schema validation, quote→span location logic (feed a known cached 본문 + a fabricated model payload), storage round-trip. No live-API tests in pytest; live evidence lives in the run report.

## Out of scope

Gate verdicts (S5 — but leave the storage room), ② (S7), Celery (S6), any exposure decision. No commits, no state transitions, no doc-new-version. Findings → numbered N-notes (continue from N33); durable truth → one-line Doc impact entries; also record the O-1 (20,000/day) and O-2 (credential + model id) closures in phase.md's Open Questions.

## Verification

- `.venv/bin/python -m pytest` green (existing 19 + new terse cases).
- Extraction run report: per-field counts (extracted / span-resolved / span-unresolved), calls, tokens, ▷ cost; idempotent re-run behavior stated (re-extract vs skip — your call, but a re-run must not duplicate rows).
- One worked example in result.md: 계양전기 (or another confirmed event) field 1 with value + quote + resolved span verified by `doc.verify`.
- No key material anywhere (grep proof). `python3 scripts/workflow.py validate` passes.
