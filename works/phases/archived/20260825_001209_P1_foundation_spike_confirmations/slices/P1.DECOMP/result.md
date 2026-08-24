# Result — P1.DECOMP

**Slice:** decompose Phase P1 "Foundation Spike & Confirmations" · executed 2026-08-19 · `slice-executor-high`

## What I did

1. Read `intent.md`, `phase.md`, `P1.DECOMP/plan.md`, `docs/reference/challenge/00_HANDOFF.md` (§3.5–§3.7, §4, §6, §7) and skimmed `01_문제정의.md`; checked P2–P4 objectives to keep P1's scope from overlapping them.
2. Ran a **light live probe** of OpenDART (endpoint existence + one field-name peek) so the slice breakdown rests on facts rather than the handoff's assumptions. The plan put "a quick doc check of the API docs" in scope; the live probe replaced it and produced firmer answers. It is explicitly *not* the matrix — `P1.S1` still owns systematic verification.
3. Created the three middle slices as **bare folders** (`slice.json` only — nothing pre-filled).
4. Seeded `works/phases/active/P1/phase.md` with Context, Decomposition (+ ordering rationale), Findings & Notes (F1–F7), Constraints, a `Doc impact` running list, and Open Questions (Q1–Q7).

## Slices created

| order | id | name | kind | risk | depends_on |
|---|---|---|---|---|---|
| 1 | `P1.S1` | DART OpenAPI spike & field matrix (event-type x field x structured/LLM) | `spike` | high | — |
| 2 | `P1.S3` | Recon: daker.ai submission requirements + mijual domain availability | `research` | high | — |
| 3 | `P1.S2` | MVP rights-scope recommendation & operator confirmation | `decision` | high | `P1.S1`, `P1.S3` |

All three are `high` risk: S1 writes real multi-file spike code, S3 needs WebSearch/WebFetch, S2 needs judgment over the matrix + recon and ends in an operator gate. No `co-work` slice and no `DECOMP2` — P1 touches no product visual design, so it decomposes in a single pass.

## Deviations from `plan.md`

1. **Recon runs before the confirmation slice** (order: S1 → S3 → S2), which the plan invited me to decide. Reasons, recorded in `phase.md`: `P1.S2`'s `pending` gate halts the entire phase, so recon parked behind it would be blocked for unknown wall-clock time at D-19; recon is real input to the scope decision (submission format and 본선 schedule bound what can be built); and it batches both operator-facing outputs (scope decision + the mijual domain purchase) into one operator round-trip.
2. **IDs were not renumbered to match execution order.** `P1.S2` stays "scope confirmation" and `P1.S3` stays "recon" exactly as `plan.md` names them, and only `--order` sequences them, so plan text and slice folders keep referring to the same things. `works/backlog.md` therefore lists P1.S1, P1.S3, P1.S2 in that order — intentional, and explained in `phase.md`.
3. **Kinds:** `spike` / `research` / `decision`. `P1.S2` is deliberately **not** `kind: co-work` — `co-work` is reserved for orchestrator-run visual-design slices; S2 is a normally dispatched slice that returns `needs_operator` and is then set `pending` by the orchestrator.
4. **Live API probe instead of only a docs read** (see above). No spike artifact was written and no code was added to the repo — findings live in `phase.md` only.

## Findings that change how P1.S1 should be planned

Full detail in `phase.md` (F1–F6). The three that matter most:

- **`piicDecsn` (유상증자 결정) returns only 19 fields** across 15 sampled 2026 filings — no 신주배정기준일, no 발행가액, no 배정비율, no 청약일, no 증서 매매기간. The killer rights type gets nothing service-critical from that endpoint.
- **But `estkRs` (증권신고서 지분증권) does** carry 청약기일 `sbd`, 납입일 `pymd`, 배정기준일 `asstd`, 발행가 `slprc`, and the **인수(청약 취급) 증권사** `actnmn`. So `P1.S1`'s matrix must span 주요사항보고서 **and** 증권신고서 endpoints per event type; a 주요사항보고서-only matrix would overstate the LLM burden and mis-shape P2.
- **정정 samples are abundant** (37 `[기재정정]` in one 100-row page); the real work is **pairing** a correction with the original it supersedes — `list.json` does not expose that link.

Also resolved: `exbdIsDecsn` (교환사채) exists — the plan's "if available" is a yes. And `list.json` without `corp_code` is capped at a 3-month window (`status 100`), which constrains any bulk scan.

## Validation

| command | outcome |
|---|---|
| `python3 scripts/workflow.py validate` | **PASS** — `OK: workspace state is consistent.` |
| `python3 scripts/workflow.py next` | shows `P1.DECOMP` in progress with P1.S1 next; backlog lists the new slices in order 1 (S1), 2 (S3), 3 (S2) |
| folder check (`ls -A` each new slice dir) | each contains **only** `slice.json` — no `plan.md` pre-filled anywhere |

Live OpenDART probes ran read-only against the public API with the key read in-process from gitignored `.env`; the key was never printed, written to a file, or committed. No repo files were created outside `works/phases/active/P1/`.

## Handoff notes for the orchestrator

- `P1.S2` is the phase's **planned mid-phase stop**: its executor should return `needs_operator`, and the orchestrator sets it `pending`. Do not let it self-confirm the 3종 scope.
- When planning `P1.S1`, aim it at the *union* matrix (주요사항보고서 + 증권신고서 endpoints) and give it Q1–Q3 from `phase.md` as explicit questions to answer; the diff-target work hinges on solving the 정정↔원본 pairing.
- Nothing here versioned docs (correct for a non-review slice); the `Doc impact` list in `phase.md` is open and expects its first entry from `P1.S1` against `data`.
