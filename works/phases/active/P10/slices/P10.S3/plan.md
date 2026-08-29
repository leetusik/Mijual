# Plan — P10.S3 (the rendered-string sweep, including the assistant's own name)

Read `works/phases/active/P10/phase.md` whole first, then `intent.md`. S2 recorded the
S2/S3 scope split and a runtime workaround you will need; both are in the notebook.

`DECOMP` sized this slice as a handful of string swaps. **It is bigger than that, and the
extra part is the most user-visible thing in the phase.** Read §3 before you estimate.

## The rule that decides what you touch

The operator chose **user-facing only** over "user-facing plus repo internals". So:

- **In scope:** any string a user reads or hears the product say — rendered UI text, a served
  API title, and (see §3) **the name the assistant calls itself when it answers**.
- **Out of scope:** doc comments and docstrings, even when they name the old product. The
  operator declined that tier explicitly; do not widen it.
- **The one exception:** a comment that, after your edit, would state something **false about
  the code directly below it**. Then fix the comment — a lying comment is worse than a stale
  one. S2 set this precedent for `BRAND_ALT_KO`/`COPYRIGHT_KO`. Keep such fixes minimal and
  keep a historical 미주알/미주얼 token where the sentence is genuinely about the past.
- **Never touch `frontend/public/foundations/*.css`** — vendored byte-verbatim design
  foundations. Their comments do mention the old name and are publicly fetchable; that is
  noted and deliberately left alone.

## 1. The 실권주 disclaimer — the one rendered frontend string left

`frontend/components/event/copy.ts:114`, `MISMATCH_HEADER_KO`:

> `발행사의 공시가 실권주에 대해 서로 다른 두 값을 제시합니다 — 미주알은 어느 쪽도 고르지 않고 둘 다 보여드립니다`

Rendered in two places: `components/event/Offering.tsx:301` (`<p className={styles.mismatchHead}>`)
and `components/lookup/MissedMoney.tsx:395` (`<span className={styles.cap}>`); also re-exported
through `components/lookup/copy.ts:55`.

**Name swap only** — this is signed design copy. 미주알 and 주주의관제탑 both end in a
consonant, so the `은` particle is unchanged; confirmed, but re-check rather than trust it.

**The sentence grows by four syllables** and both render sites are single-line captions.
Look at both at **390px** and report whether either now wraps or clips. If it does, that is an
operator question, **not** a licence to shorten signed copy.

## 2. The served API title

`src/mijual/web/app.py:57`, `TITLE = "미주알 API"` → `"주주의관제탑 API"`. It reaches
`FastAPI(title=TITLE)` at `:113`, so it appears in `/openapi.json` and on the docs page. No
particle follows.

## 3. The assistant calls itself 미주얼 — a third spelling, and it says so out loud

**This is new work that the decomposition did not see**, because it searched for `미주알` and
these strings use `미주얼` (얼, not 알). Fourteen occurrences in `src/`, of which these are
**live prompt strings sent to the model on every `/ask` turn** — not comments:

- `src/mijual/agent/instructions.py` — `:52` (`_ROLE`: *"You are 미주얼(Mijual)'s 해설 agent…"*),
  `:83` (`_CITATIONS`), `:122` (`_CALCULATOR`), `:134` and `:141` (`_OUT_OF_SCOPE`),
  `:151` and `:162` (`_SECURITY`), `:198` (`_TOOL_NOTES`), `:213` (`_FINALLY`)
- `src/mijual/agent/tools.py:260` (`DATA_BOUNDARY`)
- `src/mijual/agent/declarations.py` — `:139` (`save_feedback` description, English:
  *"…about Mijual itself…"*), `:283`, `:300`

Verify that list yourself before editing; `:130` in `instructions.py`, `citations.py:19` and
the module docstrings are comments and stay.

**Why this is in scope even though no user reads a system prompt:** the prompt tells the model
what the product is called, and the model then says that name in Korean answers. Leaving it
would ship a rebrand where the chrome says 주주의관제탑 and the assistant introduces itself as
미주얼. "User-facing" has to mean the name the product uses when it talks to a user.

**Two shapes of edit here, not one:**

- `instructions.py:52` carries **both** the Korean variant and the retired latin mark:
  `미주얼(Mijual)`. Swap the Korean **and drop the parenthesized latin gloss** — there is no
  romanized replacement, by operator decision.
- `declarations.py:139` uses the latin mark as an **English noun** ("about Mijual itself").
  That cannot be substituted into English; **reword** it (e.g. "about this service itself").
  Same judgement wherever the latin mark is a grammatical subject.

**Constraints on prompt edits — these are behavioural, not cosmetic:**

- Change **only** the name. Do not reflow, reorder, retitle, tighten or "improve" any prompt
  line. This rulebook is signed P9 work and its ordering is load-bearing.
- `instructions.py` is a **static cache prefix** (its own header, `:26–36`, says the order of
  the instruction is a cache key). Editing it invalidates the implicit prompt cache once, which
  is an accepted one-time cost — but it is exactly why you must not restructure anything.
- Note in `result.md` that the product had been shipping **two spellings of its own name**
  (미주알 in the UI, 미주얼 in the prompts). That is pre-existing, the rename incidentally
  fixes it, and it is worth stating plainly rather than silently normalising.

## 4. Prove the sweep is complete

After editing, search for every remaining `미주알`, `미주얼`, `MIJUAL`, `Mijual`, `mijual`
outside `node_modules`, `.next`, `works/`, `docs/versions/` and classify **every** surviving
hit as one of: an out-of-scope identifier (`MIJUAL_*`, `X-Mijual-CSRF`, `mijual.<module>`,
`src/mijual`, the two `name` fields, the DB credential in `config.py:32`, `Mijual Design
System`); a doc comment or docstring (out of scope by the rule above); `docs/current/` prose
(**S4's job — leave it**); or history that must not change. Put that classification in
`result.md`. A hit you cannot classify is an operator question, not a silent edit.

## Constraints

- Do **not** touch `docs/current/`, `frontend/README.md`, `pyproject.toml`, `package.json`,
  `Makefile`, or `compose.yaml` — all S4's.
- Do **not** touch anything S2 owned (`chrome/copy.ts`, `Wordmark.tsx`, both layouts,
  `ops/copy.ts`) beyond reading it.
- No `doc-new-version`, no commits, no status transitions.

## Validation

Operator runtime only (`docs/current/operations.md` `## Operator Runtime`). **S2 recorded that
`make stack-up` currently fails at `db-up` because host port 5433 is held by an unrelated
project's container; `phase.md` `## Context` carries the 5434 workaround.** Use it; do not
stop the other project's container.

- `cd frontend && npm run typecheck` and `npm run smoke` — clean.
- Python: the repo's pytest suite (`pyproject.toml` configures it) — at minimum the web and
  agent tests. No test asserts on a brand string today, so a pass proves you broke nothing, not
  that you changed the right thing.
- **Browser, dev:** both render sites of the 실권주 disclaimer, at desktop **and 390px**.
- `/docs` and `/openapi.json` show the new API title.
- **The assistant's own name — try it.** Start the stack and ask `/ask` a meta question in
  Korean (`너는 뭐야?` or `너 이름이 뭐야?`) and check the answer names 주주의관제탑 and never
  미주얼. This needs live model credentials; **if they are not configured, say so explicitly in
  `result.md` and hand the check to S5** rather than skipping it silently or inventing a result.
- A production build check is not required of you — S5 does the comprehensive pass.

## `phase.md`

**It is at 191 lines / 16,168 bytes against a 200 / 16,384 budget — under 220 bytes of room.
You must compress before you add anything.** Drop the `for P10.S3` note you consume, and
compress `## Decisions` and `## Context` where S1/S2 detail has done its job (it survives in
git and in each `result.md` by path). Add a tagged note for S4 carrying the latin-mark
rewording problem and the history lines. Rewrite `## Now` (≤ 15 lines) last.

Add an operator question for the two-spellings finding **only if** you think the operator needs
to decide something about it; if the swap is unambiguous, a `result.md` note is enough.

## Verdict

`done` with a one-line summary that says how many live prompt strings you changed.
`needs_operator` if a signed sentence genuinely cannot carry the new name without being
rewritten — that is a real stop, and the right one.
