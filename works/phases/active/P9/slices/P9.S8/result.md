# P9.S8 — result

The client can now hold everything R16 signed. Nothing new is drawn: `P9.S9` draws it, and until then
both views render exactly as they did before, with one deliberate transitional artifact (§4).

## What landed

**`frontend/lib/ask.ts` — the vocabulary, the keyed reduce, the transient line, the turn metadata.**

- `AskBlock` grows three variants — `status` (transient: `phase` + the server's own signed sentence),
  `data` (`rows` + optional `title`) and `calc` (`mode` · `name` · `inputs` · `state` · `expr?` ·
  `result?` · `why?`) — and `text` gains optional `unverified` spans. Every variant intersects a new
  `BlockIdentity` (`block_id?` / `persistent?`), which ride only when the server sends them, so a
  pre-R16 frame still reduces to byte-identical state (the existing `deepEqual` on a `text` block is
  untouched and still passes).
- New exported types for the surface to build on: `AskDataRow` (the one row schema §2.3 fixes and §2.4
  reuses), `AskCalcMode` (`verified | expr`) and `AskCalcState` (`pending | done | error`).
- `place(blocks, block)` is the keyed reduce and **every** block goes through it: an id replaces the
  block already wearing it **at its own index**, no id appends. That index is the point — in the landed
  wire a 도구 행 arrives between `calc(pending)` and `calc(done)`, so remove-and-push would sail the
  settled calculation past it (§4 check 5).
- `withoutStatus()` drops the transient line at the first `text`/`refusal`, at every terminal, and on
  both terminal-less paths (a cut stream; the `catch` that carries 중지 and a pre-stream 429) — §2.1
  plus `P9.S6` note 12, which the server cannot do for us. A `status` frame arriving after prose is
  ignored rather than re-placed.
- Persistence filters on `persistent === false` (the wire's own word, not on `kind`), at **both** the
  write-through and the read-back. Load-bearing: the write-through fires on every frame, so a tab
  reloaded mid-turn would otherwise restore a 중단 turn with a live 「공시 원문을 읽고 있습니다」 under it.
- `AskTurn` gains `filings` (D8's 「공시 M건 읽음」, server-known — never parsed out of 도구 행 strings),
  `blocked` (removed-marker count) and `reason`. A restored pre-R16 turn reads `0 / 0 / null`.
- `released()` now joins the prose kinds via a shared `isProse()` guard instead of "everything that is
  not a tool row" — a `data`/`calc` block has no `text` and must not enter the answer.

**`frontend/components/ask/copy.ts` — R16 §0, byte-verbatim.** `CALC_VERIFIED` · `CALC_EXPR` ·
`TAG_CALC` · `TAG_UNVERIFIED` · `TAG_INPUT` · `CALC_RESULT` · `CALC_RUNNING` · `calcError` ·
`DATA_HEADING` · `SHOW_ALL` · `FOLD` · `DETAIL` · `trace` · `START_HEADING_KO` · `NEW_CHAT_KO` ·
`START_CHIPS_KO` (**4** cards, no meta card) and D1 `AGENT_INTRO_KO`, each with its provenance
docstring. No status strings (they are the agent's, `P9.S3` note 3). `ANONYMITY_KO` ·
`VERIFIED_ONLY_KO` · `REASK_KO` stay in place with a comment naming `P9.S10` as the slice that deletes
them **with their call sites**.

## Validation

| command | outcome |
| --- | --- |
| `cd frontend && npm run typecheck` | **pass** (`tsc --noEmit`, clean) |
| `cd frontend && npm run smoke` | **pass** — 18 tests, 0 fail (2 new) |
| `cd frontend && npm run build` | **pass** — 15 routes, no warnings |
| `.venv/bin/python -m pytest` | **pass** — 154 passed, 1 pre-existing Starlette deprecation warning; the Python side was not touched |
| `python3 scripts/workflow.py validate` | **pass** |

No browser verification is claimed: this slice draws nothing. The Operator Runtime walk is `P9.S11`'s.

**Two tests added to `frontend/lib/ask.test.ts`** (terse, no new scaffolding — both reuse the existing
`stubStream`/`settled` helpers over one new frame constant shaped like `P9.S5`'s landed wire):

1. *a block arriving twice on one id is replaced where it stands* — two `status` frames and two `calc`
   frames add no blocks, the settled calculation is still **before** the 도구 행 that arrived between
   `pending` and `done`, the 진행 표시 line is gone at the first sentence, the data rows carry their
   chip number and 「입력」 flag, the sentence carries its `unverified` span, and the turn carries
   `filings`/`blocked`.
2. *the transient 진행 표시 line is never written to sessionStorage* — a subscriber proves the line was
   really on screen, and no captured write ever contains a `status` block.

**§0 verbatimness was verified as bytes, not by eye**: a throwaway script extracted every constant from
`copy.ts` and asserted it occurs verbatim in the signed §0 block, including the three template literals
and the four start cards in order.

## Deviations from `plan.md`

1. **`frontend/components/ask/Answer.tsx` was touched** (one guard + one 4-line comment + a 3-line
   `isProse` helper). The plan's own scope item 6 requires both views to keep rendering, and `group()`
   pushed every non-`tool` block into a prose paragraph — with the new kinds that is a **typecheck
   failure**, not a runtime no-op. The guard skips every non-prose block; `P9.S9` replaces it with
   §2.8's child order. No behaviour changed for any block that exists today.
2. **`AskTurn.reason` was added** beyond the plan's `filings` + `blocked`. §2.7 draws a 소진 turn
   (dimmed prose, folded 도구 흐름, 신규 문자열 0) and a 연결 끊김 turn (R14's inset + 재시도)
   **differently**, and both are `aborted` on `turn.status`; without `reason` neither `P9.S9` nor
   `P9.S10` can tell them apart, and one of them would have had to reopen this file. Same field family,
   same frame, one line.
3. **The 진행 표시 line lives in `turn.blocks`, not in a field beside them.** The plan allows either
   reading; `P9.S3` note 2 does not — it records that the client's *keyed reduce* is what makes 「항상
   하나만 살아 있다」 true. Putting it anywhere else would have made that note false.

## Doc impact

Two `frontend` lines appended to `phase.md` → `### Doc impact` (the store's R16 shape and the keyed
reduce; the §0 copy including D1 replacing R6's intro on both surfaces). No doc version created — that
is `P9.REVIEW`'s.

## Notes and questions

Eleven durable notes appended to `phase.md` → `### P9.S8 — the client store landed`. **No new
`## Operator Questions`**: everything this slice decided was an engineering reading of the signed
record, and the two things worth watching (중지 unavailable during the first model round; the empty
answer box that appears at `status(read)` until `P9.S9` fills it with the StatusLine) are in-the-flesh
checks for `P9.S9`/`P9.S11`, not operator decisions.
