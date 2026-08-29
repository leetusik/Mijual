# Intent — P10

- Captured at: 2026-08-30T00:53:42+09:00
- Origin: operator

## Original Input (verbatim)

> ---
> I'mma change the logo and the app's name.
> "주주의관제탑". logo file is in the ~/Downloads/juju_logo_no_back.png
> you change the app accordingly.

## Confirmed Intent (refined + clarified)

Rebrand the product's **user-facing identity**: the name **미주알 → 주주의관제탑**, and the
**MIJUAL wordmark → the operator's supplied logo** (`~/Downloads/juju_logo_no_back.png`).
Change the app accordingly, everywhere an operator or reader can see the old identity.

**The name is uniformly the unspaced form `주주의관제탑`.** No spaced variant, and **no latin
mark anywhere** — the English `MIJUAL` wordmark and the `MIJUAL OPS` bar mark are both
retired rather than romanized.

**In scope — user-facing only:**

1. **Brand binaries** (`frontend/public/assets/`). The operator's PNG is landed as the new
   mark, and a **white variant is derived from it** by this phase (see *Clarifications*).
   The four `mijual-*` binaries are retired. The assets README is rewritten: what each new
   file is, its sha256, and — for the derived variant — the exact operation performed, so a
   later slice can still prove nothing was re-encoded by accident.
2. **Document identity**: `frontend/app/layout.tsx` `metadata.title`, and the favicon
   (the old brand disclosed *no* favicon-scale mark — see *Notes*).
3. **Chrome copy**: `frontend/components/chrome/copy.ts` — `BRAND_ALT_KO`, `COPYRIGHT_KO`
   (`© 미주알`), the ring-wordmark path constant and its natural-dimension pair.
4. **Ops mark**: `frontend/components/ops/copy.ts` `OPS_MARK` (`MIJUAL OPS`), and the ops
   layout's own `title`.
5. **Signed Korean copy that names the product** — the 실권주 disclaimer in
   `components/event/copy.ts`, and the auth / portfolio / not-found prose that spells 미주알.
   These are landed design strings, so each replacement is a name substitution only; no
   sentence is rewritten and no new Korean is invented.
6. **User-visible docs**: `frontend/README.md`, the assets README, and the durable
   `docs/current/` sections that spell the product name.

**Explicitly out of scope** (operator's decision — invisible to users, and renaming them
days before the 2026-09-07 submission deadline would put the production deploy at risk):
the Python package `src/mijual/`, the `MIJUAL_*` environment variables, the
`X-Mijual-CSRF` header, the repository directory name, and the Claude Design project's
own name ("Mijual Design System").

**Ordering.** This phase is `order 3.9` — it lands **before P4 (Ship & Submit)** so the
presentation deck, demo video, and daker.ai submission all carry the new name.

**Acceptance.** Operator-visible by definition, so the phase ends at an acceptance gate:
the operator opens the running product and checks the mark reads correctly on the
**dark cosmos chrome**, at phone width, and in the **production build**.

## Clarifications Resolved

- Q: How deep should the rename go — user-facing only, user-facing plus repo internals, or
  everything including code identifiers? — A: **User-facing only.** Code identifiers
  (`src/mijual/`, `MIJUAL_*`, `X-Mijual-CSRF`) stay untouched.
- Q: The supplied PNG is pure black on a transparent background, but the site chrome is the
  dark "cosmos" theme and today renders the *white* ring wordmark — a black mark would be
  invisible there. Should the operator export a white version, should the agent derive one,
  or should the chrome get a light plate behind the mark? — A: **The agent makes the white
  version** — an alpha-preserving black→white recolor of the operator's own file, no shape
  change, recorded as a derivative.
- Q: What replaces the English marks — the `MIJUAL` wordmark and the `MIJUAL OPS` bar? —
  A: **Uniform, unspaced `주주의관제탑`.** No latin mark.
- Q: Does this need a Claude Design round, and how should the phase be shaped? — A: **No
  design round.** A single apply phase, ordered before P4, ending at an operator acceptance
  gate. The design decision was already made outside the workspace: the operator delivered a
  finished mark.

## Notes

- **The supplied file**: `juju_logo_no_back.png`, PNG 2560×1440 RGBA, transparent
  background, ink is pure black (`#000`), and the mark occupies a small region of a mostly
  empty canvas. The retired `mijual-*` binaries were tightly cropped (wordmark 1788×324,
  ring 2178×346) and the chrome places the wordmark at a constrained height (nav h19,
  footer h17), so the empty margin has to be dealt with — trimmed, or handled at placement.
  Which, and the resulting natural-dimension pair, is a decomposition decision.
- **The mark's shape changed, not just its letters.** The retired R2 asset was a *ring*
  logo — a wordmark with an orbital ring, which is what closed R1's disclosed
  "missing symbol mark" gap. The new mark is a Korean wordmark with a small sparkle
  cluster and **no ring**. Any code, comment, or doc that reasons about "the ring" is
  describing a mark that no longer exists.
- **There is still no favicon-scale mark.** The assets README recorded that gap explicitly
  and R2 closed only the ring half of it. The rule it states — *no image is substituted,
  generated or placeheld; a slice that needs a missing asset renders the real file or
  nothing* — still governs, so the favicon is a question for the operator if the supplied
  mark does not reduce legibly.
- **`docs/current/` spells the name too**, and durable docs are versioned once per phase at
  the review slice. Implementation slices append a "Doc impact" line; they do not run
  `doc-new-version`.
- Deadline pressure is real: P4 must ship by **2026-09-07 10:00** and today is 2026-08-30.
