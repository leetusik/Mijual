# P9.S4 — citations: strip don't drop, 미확인 marker

## Context

The slice that stops 「안녕」 being refused. The sentence-dropping citation gate becomes strip-don't-drop, and Q-B's claim-level backstop (「미확인」 spans on tool-unverified filing figures) lands in `TextEvent.unverified` — the field S3 already created. Binding spec: `works/phases/active/P9/phase.md` → `### DECOMP2 (2026-08-25)` → **`P9.S4` — strip, don't drop** (read it in full), plus `docs/reference/design/rounds/16-smart-assistant/output/build-prompt.md` §1 (`TurnEnd.blocked` = removed markers) and §2.5 (the marker rule: 마커도 칩도 없는 숫자는 존재해서는 안 된다 — and if the server cannot compute a span, the sentence still ships, counted on `TurnEnd`). Also read S3's `### P9.S3` decisions section in `phase.md` (13 numbered decisions you inherit — especially the `cite()` numbering seam and wire-additivity) and S3's `result.md`.

## Scope

1. `src/mijual/agent/citations.py::CitationGate._release` (line ~229): stop judging. Of today's four block reasons — `unresolved_citation`, `uncited`, `untraceable_number`, `reconstructed_quote`:
   - `unresolved_citation` → strip the bad marker (and its leading whitespace residue), keep the sentence.
   - `uncited` → the sentence ships as-is, unverified span only if it contains a filing-specific figure (below).
   - `untraceable_number` → **Q-B**: the sentence ships with `unverified` spans over the figures `learn()`'s `_values` cannot trace — the 「미확인」 claim-level marker. No turn or sentence replacement.
   - `reconstructed_quote` → **kept as a guard**: 인용문 재구성 금지 is explicitly *not* superseded by R16 (result.md §5). Decide the honest strip-era treatment — a fabricated quote must still not reach the reader as a quote — and record the decision in `phase.md`.
2. `_block` becomes a counter of removed markers feeding `TurnEnd.blocked` (S3 already re-documented the semantics).
3. `loop._finish` (line ~247–271): retire the `not gate.released` fallback and `copy.REFUSAL_FALLBACK`'s use site here. Careful: `copy.family_of`, `citations._family_at_head`, `citations._is_family_prefix` match families by exact string — retiring 검증 미통과 폴백 as a producer is a code change at those sites; the retired strings stay readable for past rows (S3's whitelist).
4. **Keep**: the closed citation space, `_number_for`/`cite()` (같은 근거 = 같은 번호), chip-arrives-with-its-claim, per-sentence `TextEvent.citations` (deliberate compatibility choice — record it), and **P8** — a tool's own signed string (`NOT_FOUND_KO` + 관제 현황판) reaches the reader verbatim.

## Constraints

- RESPECT THE DESIGN: no new Korean copy in this slice; behavior only. build-prompt §4 checks 1–3 and 13 are this slice's acceptance shape (「안녕」 → greeting prose, no refusal; bad marker → marker gone, sentence stays; untraced figure → unverified span, sentence and turn alive).
- Wire-additive: `unverified` rides only when non-empty; both views keep rendering (the 미확인 marker is drawn in S9 — until then the span is data).
- Terse tests; run the suite + `python3 scripts/workflow.py validate`.
- Append Doc impact + durable notes to `phase.md`; write `result.md`; return the structured verdict. Never commit or transition state.
