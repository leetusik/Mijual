# P9.S3 — R16 event vocabulary, block ids, and the two storage contracts

## Context

First build slice of P9 (the contract slice). The signed R16 design requires a richer typed event stream and two contract changes before anything else can build on them. The binding spec is `docs/reference/design/rounds/16-smart-assistant/output/build-prompt.md` §1 (event vocabulary), and the slice-level breakdown in `works/phases/active/P9/phase.md` → `### DECOMP2 (2026-08-25)` → **`P9.S3` — the contract slice (P10 first)** is this slice's detailed spec — follow it in full. The standing constraints section of DECOMP2 (RESPECT THE DESIGN; three stale build-prompt lines where the signed copy governs; additive-on-the-wire; the AST-scanned invariants) applies.

## Scope (from the DECOMP2 spec — read it verbatim in phase.md)

1. `src/mijual/agent/events.py`: event base gains `block_id` (turn-stable) + `persistent`; same-`block_id` follow-up = in-place replacement, absent id = today's append (backward compatible). New `StatusEvent` (transient, `phase ∈ read|search|open|calc|write` — D5's five signed phrases in `agent/copy.py`) and `DataBlockEvent` (`title|None`, rows `{label, value, citation|None, reader_input}`). `TextEvent` gains the `unverified` spans **field only** (P9.S4 fills it). `RefusalEvent.family` → 6-value whitelist. `TurnEnd`: `blocked` re-documented as removed markers; distinct-rcept_no count rides on it (server-known, never parsed from tool rows).
2. `src/mijual/agent/loop.py`: emission points — exactly one live `StatusEvent`, replaced per phase, gone at first `TextEvent`; `DataBlockEvent` composed from label/value tool results with per-row citation numbers via the existing `gate.learn` reference ids.
3. **Storage contract**: `web/ask.py::_Released.absorb` + `conversationstore.record_turn` + a new **nullable, default-free** column on `db/models.ConversationTurn` (added via `db/schema_sync.ensure_columns` — no Alembic) store persistent structured blocks **verbatim**; make `absorb` generic over any persistent structured event so S5's calc blocks need no second storage change. `StatusEvent` is never stored.
4. **Vocabulary contract**: `conversationstore.REFUSAL_FAMILIES` → six values (보안 added here as contract; S6 is the producer; the two retired families stay read-only for past rows — check `record_turn`'s error message naming five families), mirrored in `frontend/components/ops/copy.ts::REFUSAL_CATEGORIES_KO`.

## Constraints

- Additive on the wire: new events/fields ride only when non-empty; `lib/ask.ts`'s `switch (frame.event)` and both views must keep working untouched in this slice.
- Copy: only D5's five signed phrases (verbatim from build-prompt §0 `STATUS_KO`) may be added to `agent/copy.py` here; no other new Korean.
- Keep tests terse per the workspace rule — extend existing suites minimally; run the relevant test suite and `python3 scripts/workflow.py validate`.
- Append a one-line Doc impact note and any durable findings to `phase.md`; write `result.md`; return the structured verdict. Never commit or transition state.

## Acceptance

- Suite green (including the AST-scan invariants); a turn today (no new events emitted yet beyond status/data where the loop composes them) still renders identically in both views; `validate` passes.
