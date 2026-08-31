# Plan — P11.F2 (Publish the operator contact in the agent answer and the footer)

Kind `fix`, risk `high`, executed by `slice-executor-high`.

## Why this slice exists

The third of the operator's three gate reports. Their words:

> the 운영자에게 직접 연락하려면... part is I think good. but it answers like
> "현재 등록된 운영자 연락처가 없습니다…" where to insert those values? and I want
> those values to the footer as well. email: leetusik@gmail.com phone:
> 010-3772-9916

Confirmed in the clarification round: **both values, everywhere** — the footer on
every page **and** the agent's 연락처 answer. They were shown the email-only
alternative and chose both.

## The agent half needs no code

`get_contact` (`src/mijual/agent/tools.py` ~L638) already reads
`Settings.operator_contact` (`config.py:159`, a single free-text `str | None`,
populated from `MIJUAL_OPERATOR_CONTACT` at `config.py:269`) and already formats
`CONTACT_ROW` when it is set. Both values fit one string. So: **set the value**,
then **verify** the agent answers with it. Do not restructure the setting into
two fields — the string is the contract `security` records, and one string is
enough.

Set it in the repo `.env`. Note that `.env` is **gitignored**, so the value is a
local/deploy setting and will not be committed — which means the **operations doc
owes a line** telling the operator to set `MIJUAL_OPERATOR_CONTACT` wherever the
API runs, or the deployed product answers 미정 while the dev box answers
correctly. Add that to `## Doc impact`.

## The footer half — read this before touching `Footer.tsx`

**There is a real tension here and it must be recorded, not smoothed over.**
`components/chrome/Footer.tsx` is signed R2 → R8 §4 → R17. R8 deleted **four
sentences** from this exact footer *at the operator's own earlier instruction*
(「remove the text and keep it simple and clean」), leaving one hairline, one row,
and deliberately **no numerals at all** — and the record says that absence is
precisely why the row's type is Pretendard rather than mono (「mono는 숫자
전용(R1)이고 남은 줄에는 숫자가 없다」, R8 result.md §2-14).

A phone number is numerals. So this change puts text back into a footer the
operator asked to be minimal, and digits into a row whose typeface was justified
by their absence.

**Proceed** — the operator's instruction supersedes the round, exactly as
`intent.md` §2 superseded R16 D11's 「4장」 — and record it in the component's doc
comment as an operator override citing the gate report, in the voice the repo
already uses for one (`chrome/copy.ts` L64–69's P7 note). Do not present it as
what R8 signed.

Two calls the orchestrator has already made, so you do not have to invent them —
implement them unless the running result is visibly wrong, and say so if it is:

- the **phone renders mono** (R1: numerals are mono) while the **email stays
  sans**, so the row honours both rules rather than breaking one silently;
- the contact **joins the existing 자료/© row** rather than adding a second row —
  R8's deletion was of a second mono row, and re-adding one would undo the shape
  of the thing the operator asked for.

Do **not** reopen R8's five deleted constants (they still sit unrendered in
`chrome/copy.ts`) and do **not** touch **P8 Operator Question Q5**, which is still
open about where those deleted sentences should go. New Korean copy is cited the
way `copy.ts` cites everything: the operator's gate report is the authority.

**R17's corner reservation on `.inner` exists because the AI 질문 launcher was
overlapping this row** — a covered 의견 보내기 button is a dead interaction, not a
cosmetic overlap. Anything you add must not re-create that. Check at **≤1120** and
**390** specifically. Deferred job **D30** (the footer's 「AI 질문」 link is 40 × 44
at 390) is open and is **not** yours to fix — but do not make it worse.

## Getting the value to the footer

**The frontend cannot see the repo-root `.env`.** `make web-up` (Makefile ~L78–92)
passes only `MIJUAL_DEV_ORIGINS` to `npm --prefix frontend run dev`, and Next reads
`.env` from `frontend/`, not the repo root — so `process.env.MIJUAL_OPERATOR_CONTACT`
in a server component is **undefined** as the stack stands. Verify that claim
yourself before designing around it.

Serve it from the API, so there is one source of truth. `P11.F1` just established
the shape to follow — a small typed read, its path hard-coded in
`frontend/lib/api.ts` with its type in `lib/types.ts`. But note where the two
differ: the start cards are deliberately **`cache: "no-store"`** because staleness
is the defect they fix; **this value changes almost never** and the footer renders
on **every page in the layout**, so a per-render fetch is waste. Cache it with a
sane revalidate window and let a contact change take minutes to propagate. Choose
the endpoint's home deliberately: this is **site-wide** config, not ask-specific,
so `routers/ask.py` is the wrong file.

The footer must render correctly when the value is **absent or the API is down** —
the same lesson F1 just learned on the cards. An unset contact means the footer
shows no contact line at all (never an empty label, never 「미정」 in the chrome —
that honest-unset line is the *agent's* voice, not the footer's).

## Verify — in the operator's runtime

`make stack-up`, `http://127.0.0.1:3010`, Chrome desktop **and** 390, **and the
production build**.

- The footer carries both values on **several different routes** (landing, `/ask`,
  an event detail, a stock page) — it is in the layout, so prove it is really
  everywhere rather than checking one page.
- The 연락처 start card's answer now returns both values instead of the
  honest-unset line. This is one of the four cards `P11.F1` just landed — press it.
- **≤1120 and 390:** the launcher does not cover 의견 보내기, the row wraps
  sanely, nothing overflows.
- The email is a working `mailto:` and the phone a `tel:` link if you add them as
  links — decide, and make the touch targets sane at 390 if you do.
- Kill the API and reload: the footer still renders, minus the contact line.

Aside is not installed (three slices have now recorded it), so the documented
fallback applies. Name the instrument; never claim a run you did not make.

Run `npm run typecheck`, `npm run build`, `npm run smoke`, `pytest`, and
`python3 scripts/workflow.py validate`. Keep any new test terse.

## Scope

`.env` (the value), `components/chrome/Footer.tsx` + its CSS + `chrome/copy.ts`,
a small site-config endpoint and its `lib/api.ts` / `lib/types.ts` entries, and
the operations doc note. **Not** the start cards (`P11.F1`, landed — do not touch
`app/ask/page.tsx`, `components/ask/copy.ts` or `routers/ask.py`), **not** the
citation chip (`P11.S1`, landed), **not** D30's link target.

## Notebook and result

Edit `phase.md` under budget (153 lines / 14.4 KB of 200 / 16 KB — compress as you
add). Record in `## Decisions` that the contact is published at the operator's
instruction, the R8 tension, and the mono-phone/sans-email call. Append
`## Doc impact` lines for **`operations.md`** (set `MIJUAL_OPERATOR_CONTACT`
wherever the API runs, or production answers 미정), **`frontend.md`** (the footer
now carries served config; the absent-value contract) and **`experience.md`** /
**`security.md`** as the change actually warrants — `security` already names this
as the one operator-identifying string the product publishes, so check whether
that entry needs updating now that it is genuinely published. Do **not** run
`doc-new-version`.

Write `result.md` verdict-block-first. Return the structured verdict.
