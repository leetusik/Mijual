# Plan — P10.DECOMP (decompose the rebrand phase)

## What this slice is

Cut P10's middle slices and record the breakdown in `phase.md`. **Create bare slice folders
only** (`new-slice`) — do not pre-fill any slice's `plan.md`, do not land the logo, do not
edit a single line of product code or copy. Decomposition is survey + judgement + slice
creation, nothing else.

Read `works/phases/active/P10/intent.md` first and in full. It is the confirmed record of
what the operator asked, it already carries four resolved clarifications, and it names the
scope boundary precisely. Everything below assumes you have read it.

## Settled before you start — do not re-open these

1. **There is NO design style question here, and you must not stop `pending` to ask one.**
   The phase touches brand identity, so the design-style question was asked at
   `/create-phase` and the operator answered: **no Claude Design round.** The design decision
   was made outside the workspace — the operator delivered a finished mark. `intent.md`
   therefore carries no `## Design Style` heading, which per `CLAUDE.md` reads as "not a
   design phase". Cut **no `co-work` slice**, write **no `handoff.md`**, and do not invoke
   `design-cowork`. This phase is apply-only.
2. **Scope is user-facing only.** Code identifiers — the Python package `src/mijual/`, the
   `MIJUAL_*` environment variables, the `X-Mijual-CSRF` header, the repo directory name, and
   the Claude Design project's own name — are **explicitly out of scope by operator
   decision**. Do not cut a slice that renames any of them.
   **But mind the distinction:** the *package* is out of scope; **Korean strings that live
   inside Python and reach a user are in scope.** Concretely `src/mijual/web/app.py:57`
   (`TITLE = "미주알 API"`, the OpenAPI title served at `/docs`) is in scope. Comments in
   `src/mijual/mail.py`, `web/vocky.py`, `web/routers/feedback.py` that merely mention 미주알
   are prose about the product — treat them as documentation, not product copy.
3. **The name is uniformly the unspaced `주주의관제탑`.** No spaced variant anywhere, and no
   latin mark at all — `MIJUAL` and `MIJUAL OPS` are retired rather than romanized.
4. **One open assumption to surface, not to decide.** The ops bar mark
   (`components/ops/copy.ts` `OPS_MARK`, currently `"MIJUAL OPS"`) is assumed to become
   **`주주의관제탑 운영`**. The operator was told this and did not object, but never confirmed
   it in words. Record it on `phase.md`'s `## Operator Questions` list so the review routes
   it; do not treat it as blocking.

## Survey already done — start from this, verify it, extend it

I ran this before writing the plan. Re-verify anything you rely on; the point is to save you
the first pass, not to replace your own reading.

### The supplied mark (`~/Downloads/juju_logo_no_back.png`)

- PNG **2560×1440** RGBA, mostly empty canvas.
- `magick … -trim +repage` yields **1213×319** — comparable to the retired binaries
  (wordmark 1788×324, ring 2178×346) but a **chunkier aspect ratio, ~3.8:1** against the
  retired ring's ~6.3:1. At the chrome's constrained heights (nav h19, footer h17) the new
  mark renders roughly **72px** wide where the ring rendered ~120px. Whether that reads
  correctly is exactly what the acceptance gate is for.
- **Structure, verified pixel-by-pixel:** fully-opaque pixels are **pure black**
  (7,488 px, mean R = 0.5, max R = 2). Anti-aliasing lives **in the alpha channel**
  (22,956 partial-alpha px). Fully-transparent pixels carry near-white RGB
  (~254,254,253) — the signature of a background knocked out of a white-backed export.
- **Consequence for the derived white variant:** because the shape is carried by alpha and
  the ink is uniformly black, `magick in.png -trim +repage +level-colors white,white`
  forces every RGB to white and leaves alpha untouched — a clean, correctly anti-aliased
  white mark. Verify this claim yourself rather than trusting it; the implementation slice
  owns the actual command and must state the exact one it ran.
- **Consequence for the black original:** its partial-alpha edge pixels blend toward white,
  so composited over a *dark* surface it would fringe light. That is fine as long as the
  black file is only ever placed on light surfaces — which is the retired charcoal pair's
  role. Note it; do not solve it here.
- `magick` / `identify` are available at `/opt/homebrew/bin/`.

### Where the old identity lives

**Brand binaries** — `frontend/public/assets/`: `mijual-wordmark-{charcoal,white}.png`,
`mijual-logo-ring-{charcoal,white}.png`, plus `README.md` which records each file's sha256
and states the rules that govern them (*do not edit, re-export, downscale or re-compress; no
image is substituted, generated or placeheld; a slice needing a missing asset renders the
real file or nothing*). Those rules were written for design-project exports. The new mark is
an operator delivery and its white variant is a **derivative this phase creates** — so the
README has to be rewritten to say honestly what each new file is and what operation produced
it, rather than silently inheriting a provenance story that no longer applies.

**Rendering sites** (`grep` verified):

| file | what |
|---|---|
| `frontend/components/chrome/copy.ts:32,33` | `RING_WORDMARK_WHITE` path + `RING_WORDMARK_NATURAL` `{2178,346}` |
| `frontend/components/chrome/copy.ts:38` | `BRAND_ALT_KO = "미주알"` (the mark's alt text) |
| `frontend/components/chrome/copy.ts:172` | `COPYRIGHT_KO = "© 미주알"` |
| `frontend/components/chrome/Wordmark.tsx:31–34` | the only consumer of all three |
| `frontend/components/chrome/Footer.tsx:47` | renders `COPYRIGHT_KO` |
| `frontend/components/ops/copy.ts:32` | `OPS_MARK = "MIJUAL OPS"` |
| `frontend/components/ops/{OpsChrome,Door}.tsx` | render `OPS_MARK` |
| `frontend/app/layout.tsx:23` | `metadata.title = "미주알"` |
| `frontend/app/ops/layout.tsx:34` | `title: "MIJUAL OPS"` |

Note the constant names themselves say **`RING_`**, and the doc comments above them explain
the mark as "the MIJUAL wordmark with its orbital ring" — the thing that closed R1's
disclosed missing-symbol-mark gap. **The new mark has no ring**; it is a Korean wordmark with
a small sparkle cluster. Every name, comment and doc line reasoning about "the ring" is now
describing something that does not exist. Decide whether renaming those constants belongs in
the same slice as the swap or its own, and say why in `phase.md`.

**Korean copy naming the product** — `grep -rIc "미주알"` across `frontend/`, highest first:
`components/chrome/copy.ts` (5), `chrome/Feedback.tsx` (3), `chrome/Footer.tsx` (2),
`chrome/AccountSlot.tsx` (2), `auth/copy.ts` (2), then one each in `lib/copy.ts`,
`lib/api.ts`, `portfolio/copy.ts`, `event/Offering.tsx`, `event/copy.ts`,
`chrome/SiteChrome.tsx`, `chrome/Nav.tsx`, `chrome/index.ts`, `app/layout.tsx`,
`app/events/[rcept_no]/page.tsx`. **Most of these are doc comments, not rendered strings** —
you must separate the two, because they carry different risk and possibly different slices.
The one clearly-rendered non-chrome string is `components/event/copy.ts:114`, the 실권주
disclaimer: `"…미주알은 어느 쪽도 고르지 않고 둘 다 보여드립니다"`.

**These are landed, signed design strings.** The substitution is a **name swap only** — no
sentence is rewritten, no Korean is invented, no phrasing is "improved". If a swap makes a
sentence read badly (particle agreement after a different final consonant is the likely
one: 미주알**은** vs 주주의관제탑**은** — both end in a consonant, so 은/이/을 stay, but
check every site rather than assuming), raise it as an operator question; do not rewrite.

**Docs** — `docs/current/` occurrences of `미주알|MIJUAL`: operations 19, frontend 8,
security 6, data 5, decisions 5, product 4, backend 3, api 2, architecture 2, experience 1,
qa 1. **Many of those are `MIJUAL_*` env-var names and are out of scope** — count them
properly before sizing the slice. Durable docs are versioned **once, at the review slice**:
implementation slices append a one-line note to `phase.md`'s `## Doc impact` and never run
`doc-new-version`.

**Other user-visible text**: `frontend/README.md:1,87`, `pyproject.toml:8` (the package
`description`, Korean, visible in package metadata), `Makefile:1` (a comment).

**Favicon**: there is **none** — no `frontend/app/icon.*`, no `favicon.ico`, no
`public/favicon*`. The assets README disclosed this gap explicitly and it was never closed.
The intent lists the favicon as in scope. The assets README's own rule forbids substituting,
generating or placeholding an image, so if the supplied mark does not reduce legibly to
32px, that is an **operator question**, not something a slice invents around.

## How to cut the slices

`--risk` selects the executor tier and is the phase's main cost lever. Rate `low` (→
`slice-executor-mid`) **only** for a one-line/few-line edit or pure docs; anything writing
real code, and anything spanning more than one file, is `high`. Bump up on doubt, never down.

A starting cut — **revise it if the survey tells you otherwise, and justify what you chose**:

1. **Brand binaries.** Land the operator's PNG, derive the white variant, deal with the
   empty margin, retire the four `mijual-*` files, rewrite the assets README with honest
   provenance and fresh sha256s. Own the natural-dimension pair the chrome will need.
2. **Chrome + document identity.** `Wordmark.tsx` and the `chrome/copy.ts` constants (paths,
   dimensions, alt text, copyright), both `layout.tsx` titles, the ops mark, the favicon
   decision, and the stale "ring" vocabulary.
3. **The Korean copy sweep.** Every rendered string naming the product, across `frontend/`
   and `src/mijual/web/app.py`'s OpenAPI title. Name swap only.
4. **Docs and repo-visible prose**, separating in-scope product-name occurrences from
   out-of-scope `MIJUAL_*` identifiers.
5. **A fidelity sweep in the operator runtime** — the gate depends on it landing right.

Whether 3 and 4 merge, or 1 and 2 split differently, is your call. What must not happen is a
slice that both derives the binary and rewires the chrome without ever looking at the
result in a browser.

**Every slice claiming "verified in a real browser" verifies in the `## Operator Runtime`
manifest** (`docs/current/operations.md`): `make stack-up`, dev `next dev` at
`http://127.0.0.1:3000`, Chrome desktop on this Mac plus a mobile viewport, **and
additionally the production build** (`cd frontend && npm run build && npm run start`) where
dev and production could differ. The manifest is filled — no `UNFILLED` marker — so no slice
needs to stop and ask for it. State that in `phase.md` so no later slice re-litigates it.

## What to write in `phase.md`

Seed the notebook (it is currently the bare template):

- `## Context` — the scope boundary in a few lines: user-facing only, code identifiers out,
  uniform unspaced name, no design round.
- `## Decomposition` — the slice breakdown and **why you cut it that way**, including the
  `--risk` reasoning per slice.
- `## Findings & Notes` — the mark's technical structure (alpha-carried shape, pure-black
  ink, the trim result and the aspect-ratio change), the retired-ring vocabulary problem,
  the missing favicon, and the operator-runtime pointer.
- `## Operator Questions` — at minimum the `OPS_MARK` assumption (item 4 above), plus the
  favicon if the mark will not reduce, plus any Korean sentence the swap reads badly in.
- `## Now` (≤ 15 lines) — the handoff for the first middle slice.

Keep the whole notebook under budget (200 lines / 16 KB). Do not touch the generated
`## Slices` block.

## Constraints

- `new-slice` only. **No `plan.md` for any slice you create.** No product code, no copy, no
  binaries, no `doc-new-version`, no commits, no status transitions beyond what `new-slice`
  itself does. The orchestrator owns commits and state.
- `--kind` is a closed set: `implementation`, `review`, `decomposition`, `fix`, `docs`, `qa`,
  `co-work`. An unknown kind is a hard error.
- Do **not** run `accept-gate` — that is a phase-state command and the orchestrator's job.
  (For your awareness: this phase will take `--require`; it changes what the operator sees on
  every page.)
- Write `result.md` verdict-block-first. Put in it what *this* slice did — the survey you
  actually ran, what you verified versus took from this plan, dead ends. Put in `phase.md`
  what the *next* slice needs. Never both.

## Validation

- `python3 scripts/workflow.py validate` passes (two pre-existing `unknown kind 'research'`
  warnings on P9.S1/P9.S1B are history and expected).
- `python3 scripts/workflow.py rebuild` regenerates the `## Slices` table and every slice you
  created appears with the intended kind, risk and order.
- Every created slice folder holds **only** `slice.json`.
- `phase.md` is under budget and its sections are filled as above.

## Verdict

Return `done` with a one-line summary naming the slice count and the shape you chose.
Return `needs_operator` only if something genuinely cannot be decided here — but note that
the design-style question and the scope boundary are already settled above, so neither is a
reason to stop.
