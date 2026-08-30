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

---

# Intent — P10, round 2 (post-gate)

- Captured at: 2026-08-31
- Origin: operator, at the open acceptance gate

## Original Input (verbatim)

> rebrand to 주주의관제탑 continues. I got new logo. previous one was so thin so we need to
> change to "~/Downloads/juju2.png". you change it's color too, and apply it. and use
> "favicon_and_chatbot_widget.png" as favicon and chatbot widget. you might need to create
> favicon though.

> research changple_web's case for the korean font. use same with it. and create slice and stop.

Plus, answering the gate's three questions:

> Q1 (nav/footer mark size) — "just open a design slice, I'll handle there."
> Q2 (/ops mark font) — "Drop mono, use Pretendard 600".
> Q3 (favicon) — option (b): the operator supplies a square symbol export.
> Chatbot launcher mark — "you may do a work for the colors" (the colour/asset work is the
> agent's; the treatment itself goes to the design slice).

## Confirmed Intent (refined + clarified)

The gate was **not cleared**. Recorded as `changes_requested`, and the phase reopens with
four directed fixes plus a design round.

1. **The mark is replaced, not resized.** `~/Downloads/juju2.png` supersedes
   `juju_logo_no_back.png` as the immutable brand source. Measured: the trimmed box is
   **1292×371** (3.48:1) against the retired **1213×319** (3.80:1), and the Korean glyph
   band is **1132×176 at 47.4% of the box** against **1063×162 at 50.8%** — so the mark is
   marginally *shorter* in proportion but its band carries **37.5% ink coverage against
   16.1%, i.e. 2.3× the ink**. That density is the answer to "so thin", and it is why the
   fix is a new source file rather than a larger placement.
2. **The agent derives the colour**, exactly as in round 1: an alpha-preserving black→white
   recolor of the operator's own file, no shape change, recorded as a derivative with its
   command and pixel signature. The operator's instruction "you change it's color too"
   authorises the derivation, not a new colour decision.
3. **The favicon gap closes.** `~/Downloads/favicon_and_chatbot_widget.png` (278×278, the
   sparkle cluster alone on transparency, trimming to 261×216) is the **square symbol
   export** the assets README said would be needed — gate answer (b). The README's standing
   rule *"no image is substituted, generated or placeheld"* is satisfied by an operator
   delivery and is **not** relaxed: nothing is cropped out of the wordmark.
4. **The same symbol becomes the chatbot launcher's mark**, retiring R6's animated CSS
   Saturn (planet + rotation band + drifting ring). **How** it sits there — frame, tail,
   motion, open/close states — is a visual decision and belongs to the design round, not to
   an agent. Only the asset and its colour are the agent's.
5. **The /ops mark drops `--font-mono` and its 0.08em tracking** (`.mark`, `.doorMark`),
   letting the Korean face carry it. R7's "an identifier, so it stays raw and mono" was
   written for a latin string; with `주주의관제탑 운영` it styles exactly one character out of
   nine — the space — which is what produced the 2.84× fake double-space. The string is
   unchanged. **The face it lands on is decided by item 6, not by R7.**
6. **The Korean font pipeline follows `changple_web`.** Researched at the operator's
   instruction; `~/projects/personal/changple_web` is the reference implementation:
   - face: **Noto Sans KR**, self-hosted, variable `wght 100–900` — changple_web switched
     off Pretendard deliberately, for "cleaner heavy-weight (700/900) Korean rendering";
   - delivery: **`next/font/local`**, `display:"swap"`, `preload:true`, exposed as a CSS
     variable, with `system-ui / -apple-system / Apple SD Gothic Neo / Malgun Gothic`
     fallbacks;
   - payload: a **used-glyph subset** under a ≤100 KB budget (theirs: 98,076 B), against
     Mijual's current **2,057,688 B** full Pretendard Variable — a ~20× reduction;
   - upkeep: `gen-korean-charset.mjs` re-extracts every Korean syllable the app renders and
     `subset_noto_sans_kr.sh` re-subsets from a **pinned google/fonts commit**, because a
     hand-maintained charset went stale and rendered missing syllables 자모 분리. The subset
     deliberately **omits the conjoining-jamo block U+1100–11FF** so an unknown syllable
     falls back to the system font *composed* rather than decomposed;
   - the mono comes with it: changple_web self-hosts an **IBM Plex Mono** subset at
     `preload:false`, where Mijual today `@import`s it from the **Google Fonts CDN**.
   Both OFL attribution files ship beside the fonts.

## Clarifications Resolved

- Q: Should the design round cover only the nav/footer sizing, or the launcher mark too? —
  A: **Both**, in one round.
- Q: Should the agent land the new assets first, so Claude Design reads them out of the
  repository? — A: **No — one design round, then everything else.** The operator's words:
  *"just one design round and then do rest. you overcomplicating it."* The two PNGs go into
  the session as **operator attachments**, which is the skill's own mechanism for exactly
  this; a preparatory asset slice would buy nothing and cost a round-trip.
- Q: Claude Design needs to see the new assets; that normally means pushing the branch. —
  A: **No push.** The operator connects Claude Design to this **local directory** instead,
  so the repository stays unpublished. The design slice therefore authorises no `git push`.
- Q: Is the typeface change a design question for the round? — A: **No.** It is a direct
  operator instruction naming an existing in-house implementation to copy, so it is a
  directed fix and it lands *before* the round — Claude Design should be looking at the
  face the product will actually ship.

## Design Style

**`paired`, one pair.** `P10.S6` is the design round; `P10.S7` applies it **and everything
else in the same slice** — the bold mark and its white derivation, the favicon, the launcher
asset, the `/ops` mono drop, and the Korean font pipeline. No `DECOMP2`, no preparatory
fix slices. `P10.S7` is cut as a bare folder and its `plan.md` is written when the round
comes back — that ban does not move.

*Suggested by the agent; the operator should confirm or override before `P10.S6` starts.*

## Notes

- **The gate's Q2 answer names a weight, not a family.** "Pretendard 600" is operative on
  *drop the mono and the tracking*; item 6 replaces the family underneath it in the same
  slice, so the ops mark lands as **Noto Sans KR 600**.
- **Two signed things are being superseded by operator instruction, not by an agent's
  judgement**, and `P10.S7` must record both the way the assets README records the retired
  `mijual-*` binaries — what it was, its sha256, why nothing loads it any more:
  `public/foundations/fonts.css` (a class-A vendored R1 export marked *"do not edit"*) with
  the 2,057,688-byte `PretendardVariable.woff2` beside it, and R7's mono declaration on
  `.mark`/`.doorMark`.
- **The retired thin mark gets the same treatment.** `juju-logo-source.png` and its two
  derivatives were landed by `P10.S1` five days earlier; they are superseded, not wrong.
- **R6's animated launcher Saturn is `P10.S6`'s to retire and `P10.S7`'s to replace** — not
  an agent's to decide. Its two-half ring is a bug the round already paid for.
- **`P10.S7` is large by design.** If the round comes back and it will not fit one slice,
  split it at fractional orders **then** — after the design has landed, never before.
- **The gate reopens after `P10.S7`.** `accept-gate P10 --require` still stands and now
  additionally covers a mockup, so it could not be waived.
