# Intent — P11

- Captured at: 2026-08-31T12:28:12+09:00
- Origin: operator

## Original Input (verbatim)

> Improve ask agent:—1. consecutive cite numbering gives numbering only new lines. And it’s not good.2. The prepared questions. invent better one so that we can show our all features(tool related) just by clicking the cards. One at a time fine.

Operator's follow-up note on item 1, same session, verbatim:

> 입니다.[1]\n[2]\n[3] kind of conversation happened you maybe look up the conversatoin db

Operator's follow-up note on item 2, same session, verbatim:

> 2. you decide. i

## Confirmed Intent (refined + clarified)

Two operator-reported defects on the AI 질문 surface, in one phase, landing **before P4
Ship & Submit** so the deck and demo video carry both.

### 1 — Citation chips break the prose

The reader sees `…입니다.[1]` ⏎ `[2]` ⏎ `[3]`: a sentence resting on two or more 근거
stacks its chips one per line, and even a single chip breaks the line after it.

**This is CSS, not the numbering logic.** `frontend/components/ask/InlineCitation.tsx`
(L58–107) mounts its collapsed quote panel **unconditionally** after every chip, and
`frontend/components/ask/Ask.module.css` L261 gives that panel `display: grid`
(`.quoteWrap { grid-template-rows: 0fr; opacity: 0 }`), with `.quoteClip { overflow: hidden }`
(L275) and `.quotePanel { display: block }` (L279). A block-level box inside
`<p class={styles.prose}>`'s inline formatting context (`Answer.tsx` L158–186) splits the
paragraph into anonymous block boxes — so every chip forces a line break. The sibling rule
`.sentence + .sentence { margin-left: .25em }` (L209–211) assumes inline siblings and is
defeated by the same box.

**Server-side numbering is correct and is not touched.** `agent/citations.py`
`_number_for()` (L397–409) assigns `len(self._number_of) + 1` on first use, stable per
answer, two id spaces on purpose (model cites `c7`, reader sees chip `1`); and
`agent/events.py` `TextEvent.citations` (L194–226) carries every number a sentence rests on
in a single frame. Nothing in the backend needs to change for this item.

**The fix pattern already exists in this repo.** `frontend/components/Citation.tsx` (L165+)
with `Citation.module.css` (L1–32, L74+) retired exactly this inline-height anatomy at R10:
`.wrap { display: inline-block }` plus a **conditionally mounted**, absolutely positioned
`.pop`. `Citation.tsx` L30–33 records in so many words that the ask surface's
`InlineCitation` was never re-cut with it. Re-cut it now.

The fix must hold across all three signed chip placements (프로즈 · 데이터 행 값 · 계산 입력
— R16 §2.6), on both the `/ask` page and the widget, at desktop and ≤767 (44px targets), and
must keep everything R16 signed about the chip: mono 10px, `rgba(95,208,165,.4)` border,
hover `--live`, open `--live-tint`, the 180px 인용 블록 cap, chip after the sentence's period,
and — in a data row — the third column that never scrolls out of view
(`Ask.module.css` L331–359 `.citationRow { display: contents }`, which is a grid child and is
**not** the broken case).

**Measured, not assumed:** 137 stored turns in `conversation_turn`; turns 28, 17 and 103 each
carry 5 quotes across 4 sentences. Sentences resting on two or more 근거 are routine on this
product, not an edge case.

### 2 — The start-screen cards showcase one feature out of seven

`frontend/components/ask/copy.ts` L306–323 hard-codes four cards, rendered by
`AskPage.tsx` L119–130 on the empty `/ask` state (the widget shows none):

```
계양전기 신주인수권증서 매매기간
퓨쳐켐 실권주는 어떻게 처리되나요?
대동기어 전환청구는 언제부터 할 수 있나요?
아시아나항공 주식매수청구 가격은 얼마인가요?
```

All four are read-a-filing questions. They exercise `search_events` + `get_event` and nothing
else. The agent has **seven** tools (`agent/tools.py` L1238–1246): `search_events`,
`get_event`, `get_portfolio`, `save_feedback`, `get_contact`, `calculate`, `security_check`
— so the auditable calculator (배정 신주 · 초과청약 한도 · 소멸 증서 · D-day · 전매제한
해제일), the portfolio D-day read with its anonymous sample, the feedback queue and the
operator contact are all invisible from the first screen a reader meets.

Replace the set with cards chosen so that **clicking them one at a time demonstrates every
agent capability** — the operator's "One at a time fine" means one card may demonstrate one
feature; no card has to carry several.

**What stays:** R16's layout (2-column grid, 1 column at ≤767, `--surface-raised` + 1px
`--border-soft`, hover border `--live`, `min-height: 56px`), and the rule that **the card's
sentence is the question sent** verbatim (the R14 label≠question convention is deliberately
not applied to the start screen).

**What is superseded, by operator instruction:** D11's **「4장」**. The card count is free.
The 2026-08-25 retirement of the 제품 메타 card is **not** reopened by this — `AGENT_INTRO_KO`
still says what the product is; these cards are samples of what can be asked.

## Clarifications Resolved

- Q: For item 1, which symptom — chips forcing line breaks, numbering only assigned on new
  lines, or adjacent chips needing to be grouped?
  A: Chips forcing line breaks. Operator's own example: `입니다.[1]\n[2]\n[3]`, with a
  pointer to the conversation DB for real cases. Root-caused to the always-mounted
  `display: grid` quote panel; server-side numbering confirmed correct.
- Q: For item 2, how far does the rework go — copy only in the signed 4 slots, copy plus a
  freed card count, or a full Claude Design co-work round?
  A: **Copy + card count may change**, existing visual style kept, **no design round**.
  Specifics left to the agent ("you decide").
- Q: Where does the phase sit relative to P10 (open, changes_requested) and P4 (due
  2026-09-07)?
  A: **After P10, before P4.** Ordered `3.95`. Sequential — parallel mode declined.

## Notes

- **Not a visual-design phase.** No `## Design Style` section, and none is owed: the
  operator explicitly declined a design round. `P11.DECOMP` must not read that absence as an
  unanswered question. R16's signed layout is respected; only the card copy and count move,
  and item 1 is a fidelity repair *toward* the signed chip behaviour, not away from it.
- The phase still changes operator-visible surfaces, so `P11.DECOMP` is expected to declare
  `accept-gate P11 --require`.
- **Two questions left open for `P11.DECOMP` to decide, deliberately not decided here:**
  1. **Hard-coded card companies, or data-derived?** The current four name 계양전기 · 퓨쳐켐 ·
     대동기어 · 아시아나항공, which will fall out of the corpus as filings age — a start
     screen offering a question the agent can no longer answer is worse than a generic one.
     Leaning: keep them as signed strings in `copy.ts` (the frontend's one Korean-string
     rule, `frontend.md` L412–413) and let `DECOMP` weigh a served variant against it.
  2. **Does a `save_feedback` card belong on the start screen?** Clicking it writes a row to
     the operator review queue — a side effect no other card has. Leaning: demonstrate the
     capability, but `DECOMP` decides whether the card asks *about* leaving feedback or
     actually files one.
- `security_check` is the seventh tool and is **never narrated** (it ends a turn with a fixed
  Korean sentence). It is not a card candidate; showing it off would mean inviting a
  prompt-injection attempt from the first screen.
