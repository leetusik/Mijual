# Plan — P10.S5 (fidelity sweep in the operator runtime)

Read `works/phases/active/P10/phase.md` whole, then `intent.md`. Four slices have landed: the
binaries (S1), the chrome wiring and retirement (S2), fifteen live strings including the agent's
own name (S3), and the repo prose plus the review's doc ledger (S4).

**Your output becomes the operator's acceptance walkthrough.** The review will open the product
itself and spot-check, but it builds the walkthrough from what you found. So this slice is
judged on whether the operator, following it, sees what you said they would see — not on
whether you can assert "verified".

## The one rule

**Every check happens in the `## Operator Runtime`** (`docs/current/operations.md`) — `make
stack-up`, dev at `http://127.0.0.1:3000`, Chrome desktop plus a mobile viewport, **and
additionally the production build** (`cd frontend && npm run build && npm run start`). Not in
whatever runtime is most convenient.

**`make stack-up` currently fails at `db-up`** — host port 5433 is held by
`changple_web_dev_postgres`, an unrelated project of the operator's. `phase.md` `## Context`
carries the way through (same image, same `mijual_mijual-pgdata` volume, 5434 via a scratchpad
`!override` fragment, `DATABASE_URL=…@localhost:5434/mijual`). Use it. **Never stop the other
project's container**, and leave everything as you found it. Say in `result.md` exactly what the
operator will have to do to run the stack at the gate — they will hit this too.

## What to sweep

Every surface this phase touched, **dev and production, desktop and 390px**:

1. **The nav mark and the footer mark** on the cosmos-dark chrome. Both paint, neither is a
   broken image, no light fringing on the dark ground (S1 recorded why fringing was a live
   risk — the black variant's transparent pixels carry near-white RGB; the white one should be
   immune).
2. **Both document titles** in the actual browser tab: `주주의관제탑` and `주주의관제탑 운영`.
3. **`/ops`** — the bar (`OpsChrome`) and the door (`Door`), both marks.
4. **The 실권주 disclaimer** at both render sites — `components/event/Offering.tsx` and
   `components/lookup/MissedMoney.tsx` — at desktop and 390px.
5. **The 404 page**, which carries both marks.
6. **`/docs` and `/openapi.json`** — the served title.
7. **The assistant's own name.** Ask `/ask` at least two Korean meta questions and confirm the
   answer names 주주의관제탑 and never 미주얼 or 미주알. S3 verified this against the real
   model and credentials are in the repo-root `.env`; confirm it still holds after S4.
8. **A grep proving no live reference to `mijual-*.png` survives** in any code path (historical
   prose in `works/`, `docs/versions/` and `result.md` files is fine and expected).

## The two questions the operator will actually be deciding — build their evidence

These are the reason the gate exists. Do not re-litigate them; **document them well enough that
the operator can decide in one sentence.**

**(a) The signed heights.** S2 measured the nav mark at `72.24×19` with a `9.65px` Korean band,
and the footer at `64.64×17` with `8.63px`, against a nav label of `13.5px` — so the brand is
now the smallest text in its own bar (`0.72×` the type beside it, where the ring was `1.07×`).
S2 recommends `h27` nav / `h24` footer. **Verify those numbers independently** and describe
what it looks like in words a person can act on. If you can, capture a screenshot of the nav at
the current height and at S2's recommendation, and say which file the operator can look at.
**Change nothing** — `h19`/`h17` are signed.

**(b) The ops mark's typography.** S2 found `CSS.getPlatformFontsForNode` reports IBM Plex Mono
styling exactly **one** glyph (the space) and Apple SD Gothic Neo the other eight, with
`letter-spacing: 0.08em` on Hangul making the `관제탑␣운영` gap read as a double space. Confirm,
and describe how it actually looks. **Change nothing** — `Ops.module.css` is signed styling.

## Fix authority — deliberately narrow

You may fix a defect **only** when both hold: this phase introduced it, **and** the fix is
unambiguous (a wrong path, a missing file reference, a typo in a string this phase wrote).

Everything else is **report-only**: anything touching signed design (heights, typography,
copy wording), anything pre-existing, and anything where two reasonable fixes exist. Those
become findings for the review and, if needed, `fix` slices. A QA slice that silently
redesigns is worse than one that finds nothing.

## The regression checklist

`docs/current/qa.md` `## Regression Checklist` is ~130 lines and cumulative. **The review
re-runs it in full** — that is its job, not yours, and duplicating it wastes the phase's
remaining time. What you owe instead:

- run the cheap mechanical top of it (`pytest`, `workflow validate`, `npm run build`,
  `typecheck`, `smoke`) since you are in the runtime anyway, and report the numbers;
- **draft the lines this phase should append** to the checklist — the headline checks that
  would catch a rebrand regression later. Put the drafted lines in `result.md`; the review
  folds them into the new `qa.md` version.

## Constraints

- No commits, no status transitions, no `doc-new-version`.
- Do not edit `docs/current/*` or `docs/versions/*` (generated / immutable — S4 confirmed all
  eleven are byte-identical to their newest version file).
- Do not change signed design values.

## `phase.md`

**It is at 16,368 bytes against a 16,384 budget — sixteen bytes of headroom, and `finish-slice`
will add a row.** You must compress substantially before writing anything. Good candidates: the
`## Decisions` entries whose detail has done its job (the recolor command, the provenance
classes, the black-variant mechanism — all preserved in `slices/P10.S1/result.md` and the
assets README), and any `## Notes for later slices` you consume. Reference by path instead of
restating. Rewrite `## Now` (≤ 15 lines) last.

## Validation

Your `result.md` is the deliverable, so it must show the work rather than claim it: for each
surface, what you did, what you observed, in which runtime, at which viewport. Quote real
command output and real measurements. If something could not be checked, say so plainly and
name what would be needed — an unrunnable check reported honestly is worth more to the operator
than a check quietly skipped.

## Verdict

`done` if the sweep completed, **even if it found problems** — findings are the deliverable, not
a failure. Use `blocked` only if the runtime genuinely cannot be brought up, and
`needs_operator` only if a finding needs an operator decision before the review can proceed.
