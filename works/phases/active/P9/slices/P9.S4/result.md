# P9.S4 — result

The citation gate stopped judging. Markers are stripped, chips still resolve, prose survives, and the
things that cannot be verified are taken **out of the sentence** instead of taking the sentence away:
an untraceable 공시 figure becomes a `TextEvent.unverified` span (the 「미확인」 claim marker, Q-B) and
a quote no tool returned loses its quotation marks. `loop._finish` no longer states 검증 미통과 폴백 —
the loop selects no refusal family at all, which is what stops 「안녕」 being refused.

## What changed

**`src/mijual/agent/citations.py`** — the whole slice, in `_release`:

- `_strip_markers()` removes **every** marker from the prose and reports, per marker, the ids it
  named. `_ANY_MARKER` became total (`[ \t]*\[\[[^\[\]]*\]{0,2}`): it eats the whitespace that
  introduced the marker (§4 check 3) and closes at `]]`, at a typo's single `]`, **or at the end of
  the piece** — so a stream that dies mid-marker leaves no `[[cite:c` debris on the reader's screen
  (the old gate hid that case by dropping the sentence).
- `self.blocked` is an **int**: markers removed *without being honoured* (an id no tool returned, a
  malformed marker, half of one). The `Blocked` dataclass is gone — nothing imported it, and there
  are no losses left to list. `loop` passes it straight to `TurnEnd.blocked` (R16 §1).
- An uncited sentence ships. The `P8` verbatim path is untouched: a sentence that **is** a tool's own
  string still leaves byte for byte, unrespelled and unmarked, borrowing that result's 근거.
- `_unverified()` returns character offsets, within the released text, of figures no tool returned.
  `_FILING_FIGURE` is 공시 figure **shapes** only — dates (matched whole), 접수번호-length runs,
  원·주·%·배 with a 만/억/조 scale, grouped numbers, decimals — so 「3가지」 and a bare 「2026년」 are
  never marked, and the span carries the **unit** so the surface marks one value rather than half of
  one. A verified 「…」 span is skipped.
- `_dequote()` implements 「인용문 재구성 금지」 (explicitly **not** superseded, result.md §5) in the
  strip era: a 「…」 span verbatim in nothing a tool returned is released without its marks. The words
  stay as the assistant's prose (and their figures are then traced like any other); what does not
  survive is the claim of being 원문.
- Family recognition (`_family_at_head`, `_is_family_prefix`) reads the **live** mapping, so a
  retired family arriving as words is prose, not a stored row.

**`src/mijual/agent/copy.py`** — `RETIRED_FAMILIES` (today: 검증 미통과 폴백) and the derived
`LIVE_REFUSAL_SENTENCES`; `family_of` matches live families only. `REFUSAL_SENTENCES` itself is
unchanged and `conversationstore.REFUSAL_FAMILIES` still holds all six: the producer side and the
stored whitelist are deliberately different, because a past row must stay findable. `P9.S7` adds
계산 요청 here and deletes `REFUSAL_FALLBACK`.

**`src/mijual/agent/loop.py`** — the `not gate.released` fallback branch and `ko.REFUSAL_FALLBACK`'s
use site are gone (with the now-unused `RefusalEvent` import); `_feedback_only` survives, narrowed to
"what to replay" when the model says nothing at all. `TurnEnd.blocked = gate.blocked`. One addition
the acceptance shape required: **a `done` turn that called no tool emits no `FooterEvent`** — §4
check 1 asks for 「도구 행 0 · 칩 0 · 푸터 없음」 and a greeting would otherwise have rendered
「근거 0건 · 생성시각」. Keyed on *tools ran*, not on *chips exist*, so a 0건 검색 turn keeps its footer
and with it the 관제 현황판 pointer (P8).

**`src/mijual/agent/events.py`** — docstrings only: `TextEvent` promised that nothing unverified
reaches it and that `unverified` is always empty. Both were `P9.S3` statements this slice makes
false, so they were rewritten rather than left to mislead.

## Validation

| command | outcome |
| --- | --- |
| `.venv/bin/python -m pytest tests/ -q` | **pass** — 144 tests, including the three AST-scanned invariants |
| `cd frontend && npm run typecheck` | **pass** (no frontend file changed; run as the additive-wire check) |
| `cd frontend && npm run smoke` | **pass** — 16/16 |
| `python3 scripts/workflow.py validate` | **pass** |
| ad-hoc scenario sweep against the real loop (scripted model, real tools) | **pass** — see below |

The scenario sweep, driven through `run_turn` over the test corpus, is what actually pins the
acceptance shape (§4 checks 1–3, 13):

- 「안녕」 → two prose sentences, `RefusalEvent` 없음, 도구 행 0, 칩 0, **푸터 0**, `kind == "answer"`;
- a bad marker → 「증자 규모는 확정되었습니다.」 with the marker gone and `blocked == 1`;
- an untraced figure → the sentence ships with `unverified` covering 「1,234,567원」 (unit included);
- a fabricated quote → 「공시는 신주인수권증서 매매기간이라고 적었습니다.」 (marks gone, words kept),
  while the verbatim 「신주인수권증서의 상장·매매기간」 quote is untouched;
- 0건 검색 → the signed `NOT_FOUND_KO` sentence verbatim + the 관제 현황판 link (P8 intact);
- 「미주얼은 3가지 권리를 다룹니다」 → **no** marker (a digit is not a 공시 수치);
- 「1,000주를 보유하고 계시면…」 → marked, deliberately (see the phase note; `P9.S5` traces it).

Test changes are terse and stay in the existing suites: `tests/test_agent_loop.py` — the
unverified-claim test rewritten as *stripped and marked, never dropped* (all four rules in one turn,
plus the mid-marker cut), the fallback test rewritten as *a greeting is answered* (plus: a retired
family arriving as words is not stored as a family), and the 의견 test extended with the silent-model
case; `tests/test_web_ask.py` — one line asserting `unverified` is **absent** from a text frame that
has nothing to hedge (추가만 한다).

**Not claimed: real-browser verification.** This slice draws nothing new — the 「미확인」 marker is
`P9.S9`'s — and the prompt still tells the model that an uncited sentence is discarded
(`instructions._CITATIONS`, build-prompt §3.1, `P9.S7`'s to rewrite), so the *live* 「안녕」 behaviour
cannot honestly be claimed yet. This slice makes it structurally possible; `P9.S11` is where it is
seen in the Operator Runtime.

## Deviations from `plan.md`

1. **`FooterEvent` is suppressed for a turn that called no tool** (loop change beyond the plan's
   three-item scope). §4 check 1 is named in the plan as this slice's acceptance shape and it says
   「푸터 없음」; without this the greeting turn renders 「근거 0건 · 생성시각」. Recorded as phase note 8
   so `P9.S9`/`P9.S10` do not re-derive the same suppression client-side.
2. **`src/mijual/agent/events.py` docstrings** were updated (no code): `TextEvent`'s contract text was
   written by `P9.S3` as a promise this slice breaks.
3. **`REFUSAL_SENTENCES` was not touched**, and 계산 요청 stays live. Only 검증 미통과 폴백 is retired
   as a producer, via the new `RETIRED_FAMILIES` / `LIVE_REFUSAL_SENTENCES` split — the copy pass
   (`REFUSAL_FALLBACK` deletion, 계산 요청 retirement, `_refusal_block()`) is build-prompt §3 and
   belongs to `P9.S7`, whose `reasons` map in `instructions.py` would break if the mapping shrank now.
4. **The `Blocked` dataclass was deleted** (`__all__` shrank to `["CitationGate"]`). Nothing imported
   it; `_block` became the counter the plan asked for.

## Notes appended to `phase.md`

A `### P9.S4 — strip, don't drop landed (2026-08-25)` section with twelve numbered decisions later
slices inherit — what `blocked` counts, the total marker pattern and the mid-stream cut, the
공시-figure shape rule, the deliberate reader-figure reading and its `P9.S5` resolution, the 오늘(KST)
limit for `P9.S7`, the de-quote decision and the two alternatives rejected, the live/retired family
split and what `P9.S7` adds to it, the footer rule, the narrowed `_feedback_only`, what was kept
untouched (closed citation space, `cite()`, per-sentence `TextEvent.citations` as a deliberate
compatibility choice, P8), the interim prompt mismatch `P9.S7` closes, and the additive wire. Three
**Doc impact** lines (`backend`, `api`, `decisions`) and one **Operator Question** (should the 대화
로그 keep the 「미확인」 hedge, answerable together with the `P9.DECOMP2` block-rendering question).
