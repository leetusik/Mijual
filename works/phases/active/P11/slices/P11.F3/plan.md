# Plan — P11.F3 (Silence the browser-injected hydration warning and check the root layout's cached read)

Kind `fix`, risk `high`, executed by `slice-executor-high`.

## Why this slice exists

The operator walked P11's reopened acceptance gate, accepted everything else, and
reported one thing: a React hydration warning on mobile. **Two separate matters
hide behind that one report. Keep them separate — do not let the cheap one be
used to close the real one.**

### Matter 1 — the warning they actually saw is not ours

The diff in their report names exactly one attribute on `<html>`:

```
__gchrome_remoteframetoken="369be69d8f14cee0c3da613d5529c729"
```

Chrome injects that into the DOM before React hydrates. Our own attributes —
`lang="ko"` and the two font `className` variables — carry no diff marker, so they
matched. The stack frames (`HotReload`, `AppDevOverlayErrorBoundary`) show this is
the **dev overlay** under `next dev`, not something a visitor meets.

No server change stops Chrome doing that. The documented remedy is
**`suppressHydrationWarning` on the `<html>` element** in
`frontend/app/layout.tsx` (L106 — it is not there today).

**Know precisely what that buys and costs.** It applies to that element only —
its own attributes and direct text — not to descendants. So it silences Chrome's
injection *and* would silence a genuine `<html>`-level mismatch (the font
variables, say). Everything deeper still reports. That is an acceptable trade
here, but write it into the code comment so the next reader knows the suppression
is scoped and deliberate, and why. Do not put `suppressHydrationWarning` anywhere
else, and above all **do not put it on `<body>` or on `SiteChrome`** — that would
mask matter 2.

### Matter 2 — the real one: D34, and `P11.F2`'s cached root-layout read

`P11.REVIEW` saw a React **#418 text mismatch** once in ~20 production loads and
could not reproduce it in 11 further attempts (deferred **D34**). That is a
**different signature** from the operator's report — text, not attribute;
production, not dev — and `suppressHydrationWarning` on `<html>` will **not**
hide it. It must not be treated as fixed by matter 1.

There is a concrete suspect. `P11.F2` added to the root layout a fetch with
`next: { revalidate: 600 }` whose result is passed as `contact` into
`SiteChrome`, a client component (`layout.tsx` ~L90–118). That is the shape that
produces intermittent text mismatches: a **statically rendered** route can bake a
build-time contact string into its HTML while the client is hydrated against a
different (revalidated) value, and the footer's contact text then differs between
server and client.

**Investigate this specifically.** Read `npm run build`'s route table and
establish which routes are static (`○`) and which dynamic (`ƒ`) — `/ask` is
dynamic by `P11.F1`'s `connection()`, but the rest of the site is where the risk
lives, and the footer is in the layout, so it is on **every** route. Determine
whether a static route can serve HTML whose contact differs from what hydration
computes. If it can, **fix it properly** — make the value consistent for a given
render rather than suppressing the symptom. If it cannot, say so with the
evidence, and leave D34 open with what you learned recorded in `result.md`, so
the next sighting starts from your work rather than from scratch.

Either way, do **not** widen the footer's behaviour or revisit what the contact
says — `P11.F2` is landed and accepted.

## Verify

The operator saw this **on mobile, in dev**, so reproduce it there first:
`make stack-up`, `http://127.0.0.1:3010` (or the tailnet URL from
`make stack-status` from a phone), at a mobile viewport in Chrome. Confirm the
overlay's hydration error is gone after the change, and that the page still
renders identically.

Then the production build (`cd frontend && npm run build && npm run start`), where
matter 2 lives: reload the landing repeatedly — twenty-plus times, and across a
revalidation boundary if you can force one — watching the console for a #418. A
single non-reproduction is not proof; say honestly what you observed and how many
loads it took, rather than declaring D34 closed on a quiet run.

Also confirm you have not masked anything real: with the change in place, a
deliberately introduced `<html>`-level mismatch should still be caught by
whatever you rely on, or note plainly that it would not be.

Aside is not installed (five slices have now recorded it), so the documented
fallback applies — same sweep, same viewports, same manifest runtime, through the
real browser available. Name the instrument; never claim a run you did not make.

Run `npm run typecheck`, `npm run build`, `npm run smoke`, `pytest`, and
`python3 scripts/workflow.py validate`.

## Scope

`frontend/app/layout.tsx`, and whatever matter 2 genuinely requires if it turns
out to be real. **Not** the citation chip (`P11.S1`), **not** the start cards
(`P11.F1`), **not** the footer's content or the contact endpoint (`P11.F2`) — all
landed and accepted. If matter 2's fix would reach into any of those, stop and say
so in `result.md` rather than widening on your own.

## Notebook and result

`phase.md` is at **186 lines / 16,250 bytes** against 200 / 16,384 — it will go
over on your first append, so **compress**. The phase is nearly closed; most notes
are consumed and superseded decisions can collapse to what is true now. The detail
lives in six `result.md` files and in git.

Record in `## Decisions` that the `<html>` suppression is scoped and deliberate
and why. Append a `## Doc impact` line only if durable truth actually changed —
if matter 2 turns out to be real, `frontend.md` owes the corrected contract for
the root layout's read. Do **not** run `doc-new-version`; the re-review
consolidates.

Write `result.md` verdict-block-first, separating matter 1 from matter 2 and
saying plainly what you concluded about D34 and on what evidence. Return the
structured verdict.
