# Result: P2.DECOMP — decomposition of Phase P2 (Data & Extraction Pipeline)

**Status: done.** P2 is decomposed into **nine** middle slices (`P2.S1` … `P2.S9`), all created as
bare folders, and `phase.md` is seeded with the breakdown + rationale, ten findings, the constraint
set, the first Doc impact note (the stack decision), and seven open questions. No implementation code
was written, no other slice's `plan.md` was pre-filled, no doc version was created, no state
transition was run, and nothing was committed.

## What was read first

`plan.md`, `intent.md`, `phase.md`, `docs/current/{data,operations,decisions}.md` (all v0002),
`docs/reference/dart/field-matrix.md` (§0–§8), P1's `phase.md` (findings F24/F25, constraints, Doc
impact list, and the `P1.REVIEW` closing note), and handoff §6/§7. Also inspected the repo's actual
state: `scripts/spike/` (731 lines, 3 files), `.gitignore`, `.env` presence, and the local toolchain.

## Slices created

| slice | order | kind | risk | depends_on |
|---|---|---|---|---|
| `P2.S1` Package scaffold, storage schema (event/version/snapshot) & DART client port | 1 | `feature` | `high` | — |
| `P2.S2` Collector: 유증(①) + 매수청구(③) new filings and 정정 discovery | 2 | `feature` | `high` | `P2.S1` |
| `P2.S3` 본문 XML parse layer: labeled rows, CORRECTION block, citation spans | 3 | `feature` | `high` | `P2.S1` |
| `P2.S4` LLM extraction (layer 1): Gemini schema extraction for the 10 fields + 정정 re-extraction | 4 | `feature` | `high` | `P2.S3` |
| `P2.S5` Deterministic validation gates (layer 2) + per-field reason codes | 5 | `feature` | `high` | `P2.S4` |
| `P2.S6` Celery beat scheduling: collect / extract / gate tasks | 6 | `feature` | `high` | `P2.S2`, `P2.S5` |
| `P2.S7` ② CB collection + backfill to 2025-06 (quota-gated) | 7 | `feature` | `high` | `P2.S2`, `P2.S6` |
| `P2.S8` 2026 소멸 신주인수권 가치 총액 estimation pipeline | 8 | `analysis` | `high` | `P2.S2`, `P2.S5` |
| `P2.S9` ~100-filing labeled evalset + extraction-accuracy report | 9 | `eval` | `high` | `P2.S5`, `P2.S8` |

Every folder contains **only** `slice.json` (verified by listing all nine).

**Risk rating — all `high`, deliberately.** `risk` is the phase's main cost lever, and `low` is
reserved for a one-line/few-line edit or docs. Every slice here writes real code across more than one
file (package + models + tasks + tests), which is the workspace's own line for the `high` tier. There
is no honest `low` carve-out in this phase.

**Ordering — build in reverse of D-1's drop order.** D-1 fixes the drop order as
EB → ②'s backfill → ③ → ②, **① last**, because ① 유증 is the only rights type that exercises the §3.6
reading layer (② and ③ are near-fully structured and need zero LLM). So ① goes end-to-end first
(collect → parse → extract → gate), the scheduler lands next, and ②'s corpus + backfill sit at the
droppable tail; the two evidence deliverables (estimation, evalset) close the phase because each
consumes everything before it.

## Deviation from `plan.md`

One, inside the plan's stated latitude ("executor may refine, staying ordered along the D-1 drop
order"): **the plan's single S6 — "Celery beat jobs + ② CB collection & backfill" — was split into
`P2.S6` (scheduling) and `P2.S7` (② collection + backfill).** Rationale, also recorded in `phase.md`:

1. They are two jobs with different failure modes — Celery/Redis/beat infrastructure wiring versus a
   quota-sensitive ~half-day data operation.
2. The backfill is P2's **only** genuinely droppable unit (D-1's second drop). Isolating it makes
   dropping it a clean no-op; bundled, dropping it would also cost the scheduler, and "scheduled jobs"
   is in the phase objective.
3. The backfill carries its own operator-facing gate (the unmeasured daily quota), which deserves its
   own slice boundary rather than being buried mid-slice.

Consequence: the plan's S7 (estimation) and S8 (evalset) became `P2.S8` and `P2.S9`. **No scope was
added, dropped, or moved between slices** beyond that split. Everything else follows the plan's
recommended breakdown, including the plan's operator decisions (FastAPI + SQLAlchemy + Postgres with
FastAPI deferred to P3; Celery beat + Redis) and its instruction to record the stack as a Doc impact
note rather than a doc version.

## `phase.md` seeded

- **Context** — what P1 handed over and must not be re-derived (docs v0002, the 295-line field matrix,
  the 731-line spike code, the 1,002-response offline cache).
- **Decomposition** — the nine-slice table, the ordering principle, a paragraph per slice explaining
  what it covers and *why it is its own slice*, and the refinement note above.
- **Findings & Notes N1–N10** — the stack decision (N1); the event/version/snapshot design as the one
  place a shortcut destroys the product (N2); 정정 discovery must window on the **original** date, with
  the validated pairing method and its caveats (N3); `estkRs` schedules are version-stale so **본문
  wins** for ① dates (N4); `bdRs` is **not** a CB source (N5); ② and ③ need **zero** LLM (N6); port —
  don't rewrite — the spike client, and reuse the cache for offline dev (N7); the `P1.REVIEW` lesson
  about regenerating committed summaries from the final run (N8); measured local environment facts
  (N9); and raise the operator gates early (N10).
- **Constraints** — §3.6 role split with deterministic calculation; never spend an LLM call on a
  deterministically readable field; no OpenDART call in the request path; the two correctness filters;
  secret hygiene; evidence tags; the 금지선; terse tests; deadline discipline with D-1's drop order;
  operator-owned schedule; no executor commits or per-slice doc versions.
- **Doc impact** — one note (below).
- **Open Questions O-1…O-7** — quota (blocks S7), Gemini credential + model id (blocks S4), labelling
  co-work format (S9), KONEX coverage, 주주우선공모증자, `exstk/exprc/expd`, and P1's carried-forward
  MTS coverage matrix.

## Doc impact note appended

> **`architecture`** (new doc) / **`decisions`** — stack decision for the data backbone: P2 builds a
> plain Python package (collector / parser / extractor / gates / estimation) persisting to **Postgres
> via SQLAlchemy**, with **Celery beat + Redis** for scheduled collection; **FastAPI is the P3 HTTP
> layer and reads persisted snapshots only — no FastAPI endpoint is written in P2**. Resolves the
> handoff §6-5 stack preference and `intent.md`'s deferred architecture choice. Source: operator
> decision folded into `P2.DECOMP`'s plan (2026-08-19).

The note flags for `P2.REVIEW` that it must decide whether this lands as a new `architecture`/`backend`
doc or as a `decisions` entry, and that later slices will extend the same note with the concrete schema
and job topology.

## Environment facts measured during decomposition (recorded as N9)

Relevant because `P2.S1` would otherwise waste time discovering them:

- Docker daemon **up**, server `28.2.2` → Postgres and Redis are cheapest as containers. `psql` is
  **not** on PATH.
- `redis-server` installed at `/opt/homebrew/bin` but **not running** (6379 connection refused).
- System Python `3.13.5` with **no** `sqlalchemy` / `celery` / `fastapi` → `P2.S1` must create a
  virtualenv; `.venv/` is already gitignored.
- Repo-root `.env` exists (gitignored, `DART_API_KEY` only — the Gemini credential is absent, per O-2).
- The gitignored response cache `scripts/spike/samples/` (1,002 files, ~9.4 MB, 59 본문 ZIPs) is on
  disk, so the parse/extract/gate path can be developed and tested fully offline.

No secret value was read, printed, or written anywhere; only the presence of `.env` was checked.

## Validation

| command | outcome |
|---|---|
| `python3 scripts/workflow.py validate` | **passed** — `Workflow validation passed.` (rc=0) |
| `python3 scripts/workflow.py next` | `current_slice=P2.DECOMP`, **`next_slice=P2.S1`** — the first middle slice, as required |
| `ls` of all nine new slice folders | each contains **only** `slice.json` (no pre-filled `plan.md`) |
| `works/backlog.md` inspection | regenerated; the P2 table lists `DECOMP` + `S1…S9` + `REVIEW` in order with the right kinds and paths |

## Not done, on purpose

No `plan.md` was written for any middle slice; no code was written; no `doc-new-version` /
`rebuild-docs` was run; no `start-slice` / `finish-slice` / `set-*-status` was run; nothing was
committed or staged. P2 carries no visual-design work, so this is a **single-pass** decomposition — no
`co-work` slice and no `P2.DECOMP2`.

## Handover to the orchestrator

1. The two mid-phase operator gates (**O-2** Gemini credential + exact model id, blocking `P2.S4`;
   **O-1** daily OpenDART quota, blocking `P2.S7`'s backfill) should be raised **early** — ideally
   batched at `P2.S1`/`P2.S2` dispatch time. P1's review found that batching operator questions into
   one round-trip avoided a phase-halting gate; leaving these until their consuming slice starts will
   stall the run mid-phase.
2. `P2.S9`'s hand-labelling is genuine operator co-work and should be expected to go `pending`.
