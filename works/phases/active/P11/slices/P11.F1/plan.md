# Plan — P11.F1 (Serve the start cards from the live corpus and drop two cards)

Kind `fix`, risk `high`, executed by `slice-executor-high`. Promoted from deferred
job **D28**, which predicted exactly this.

## Why this slice exists

The operator walked P11's acceptance gate and rejected it. Two of their three
reports are this slice (the third is `P11.F2`). Their words, confirmed back:

1. **Drop two cards** — 「접수번호… 내용이 있나요」 (the bare 접수번호 `get_event`
   card) and 「공시를 원문으로… 좋겠습니다」 (the 의견 `save_feedback` card). Four
   cards remain.
2. **The company-bearing cards must be caught in real time, not fixed** — 「the
   HLB, 에코프로비엠 default is fine but when they are outdated, what happen? we
   should make them to be real time catch. not fixed.」

Confirmed decisions from the clarification round — do not re-open them:

- **Server picks at request time.** The `/ask` route asks the API for a live
  company per card shape on every render; the question wording stays a template
  in `copy.ts` with a company slot. Not build-time (still goes stale), not a
  client fetch (this is the one screen that must never look empty).
- **`save_feedback` becoming undemonstrated is accepted.** Do not try to keep it.
  `get_event` is **not** lost — the calculate card already chains 검색 → 이벤트 →
  계산, which `P11.S2` and `P11.REVIEW` both measured.

## The four cards

| # | Shape | Company | Tool |
|---|---|---|---|
| 1 | 전환사채 공시 건수 | **live, multi-hit** | `search_events` |
| 2 | 유상증자 + reader's 1,000주 → 배정 신주 | **live, R1** | 검색 → 이벤트 → `calculate` |
| 3 | 내 포트폴리오에서 가장 급한 일정 | none | `get_portfolio` |
| 4 | 운영자에게 직접 연락 | none | `get_contact` |

Cards 3 and 4 carry no company and stay static strings. Only 1 and 2 are derived.

## Selection rules — the point is that a card is never a dead question

The server picks, per render, a company that can actually answer the card's own
question. Derive these from the corpus rather than hard-coding a list:

- **Card 1** wants a company with **several live filings** of the family it names,
  so the answer visibly demonstrates 「several matches are normal」. Prefer a real
  multi-hit; if none, a single-hit company is acceptable and the sentence must
  still be true.
- **Card 2** wants an event that **exposes what the question asks about** — an R1
  (유상증자) whose `allotment_ratio` is present and citable — with a **future**
  deadline. Prefer a comfortable window (roughly **D-20…D-60**): a card whose
  deadline expires the day after a reader presses it is the defect you are
  fixing, in slower motion.
- Keep R16 D11's surviving set-level rules: every 공시 question carries a 회사,
  and the two derived cards should not collapse onto the same company or the same
  권리 가족 when the corpus allows otherwise.

**Do not hard-code today's answers.** 에코프로비엠 and HLB are today's picks, not
the specification — the whole point is that the same code names different
companies next month. Prove that: run the selection twice against different
inputs (a narrowed corpus, a shifted `today`, or a direct call to the selector)
and show it returns different companies.

## The fallback is load-bearing

This is the empty state of the product's flagship surface. If the API is down,
slow, or the corpus yields no suitable event, **the cards must still render** —
fall back to a static set in `copy.ts` rather than showing a blank grid, a
spinner, or three cards where four belong. Verify the fallback **by actually
exercising it** (stop the API, or point the fetch at a dead origin), not by
reading the code. Say in `result.md` how you exercised it.

## Shape of the change

- **Backend** — a small read endpoint in `src/mijual/web/routers/ask.py`
  following the existing router conventions (`/board/summary`, "every landing
  number from one summary", is the closest precedent). It returns the resolved
  card set, or enough for the frontend to build it. Reuse the corpus reads that
  already exist (`web/reads.py` `load_corp_events` and friends) — do not write a
  new query layer.
- **Frontend** — `frontend/app/ask/page.tsx` becomes the data boundary. **Note
  what you are changing:** its docstring today says in so many words 「This file
  stays a plain route entry: no data loading, no layout and no copy of its own」.
  That was a real decision and this slice supersedes it, so rewrite the comment
  to say what the route now does and why (the operator's gate report), rather
  than leaving it contradicting the code. `AskPage.tsx` stays a client component
  and takes the resolved cards as a prop; keep `START_CHIPS_KO`'s role as the
  **fallback** and the templates' home.
  Make sure the fetch is genuinely per-request (Next will happily cache it into a
  static render — `cache: "no-store"` or the equivalent) and confirm that in the
  **production build**, where the failure mode actually shows up.
- **Copy** — templates with a company slot, cited as the existing entries are
  (`intent.md` §2 + the operator's gate report). `key={question}` in `AskPage.tsx`
  is the sentence itself, so all four resolved strings must stay distinct.
- **Stale comments `P11.S2` just wrote** — `AskPage.tsx` L33 and
  `AskPage.module.css` L94 now say **six cards**. They become wrong the moment
  this lands. Update both; four cards make two clean grid rows.

## Verify — live, in the operator's runtime

`docs/current/operations.md` `## Operator Runtime`: `make stack-up`,
`http://127.0.0.1:3010`, Chrome desktop **and** 390, **and the production build**.

- Press all four cards; record per card which tool rows appeared and whether the
  answer is real. Card 2 must still show one 「입력」 marker on the reader's 1,000주
  beside one cited chip, and card 3's answer must say 구성 예시.
- Show the derivation is live: the companies come from the corpus, and a changed
  corpus/`today` changes them.
- Exercise the fallback for real.
- Check the 4-card grid at 1280 and 390 — two rows, no orphan, no clipping.

Aside is not installed on this machine (both earlier slices recorded it), so the
documented fallback applies: the same sweep, same viewports, same runtime,
through the real browser available. Name the instrument; never claim a run you
did not make.

Run `npm run typecheck`, `npm run build`, `npm run smoke`, the backend
`pytest`, and `python3 scripts/workflow.py validate`. A new endpoint deserves a
terse test — a couple of high-value cases (it picks something answerable; it
degrades sanely when the corpus offers nothing), not a fixture suite.

## Scope

`src/mijual/web/routers/ask.py` (+ whatever read helper it legitimately needs),
`frontend/app/ask/page.tsx`, `frontend/components/ask/AskPage.tsx`,
`copy.ts`, `AskPage.module.css`'s comment, and a small test. **Not** the chip
work (`P11.S1`, landed), **not** the operator contact (`P11.F2`, running
separately — do not touch the footer or `get_contact`). If you cannot do this
without changing something outside that, stop and say so in `result.md`.

## Notebook and result

Edit `phase.md` under budget (it is at 122 lines / 11.1 KB of 200 / 16 KB after
the review compressed it). Record the new card set and the selection rules in
`## Decisions` — replacing, not stacking on, the six-card decision `P11.S2`
wrote, which the operator has now superseded. Append the `## Doc impact` lines
this needs: **`experience.md`** (the start-card set changes again — four cards,
two of them derived at request time, and `save_feedback` no longer shown) and
**`frontend.md`** (the `/ask` route now loads data; the fallback contract). Note
that `qa.md`'s just-written 「6장」 checklist row needs re-cutting too. Rewrite
`## Now` last. Do **not** run `doc-new-version` — the re-review consolidates.

Write `result.md` verdict-block-first with the per-card routing table, how you
proved the derivation is live, how you exercised the fallback, the instrument,
and anything you rejected. Return the structured verdict.
