# Plan — P10.S1 (brand binaries: land the mark, derive the white variant, rewrite the assets README)

Read `works/phases/active/P10/phase.md` whole before starting — its `## Context`,
`## Decisions` and the `(from P10.DECOMP, for P10.S1)` note are the ground you build on and
are not repeated here. `intent.md` is the confirmed operator intent if anything is unclear.

This slice produces **files and provenance only**. It wires nothing, edits no TypeScript, and
does not decide whether the mark reads at the chrome's heights — that is deliberately S2's
and S5's job. Resist the pull to "just fix" the wiring while you are in there.

## Two orchestrator decisions that change what `DECOMP` wrote

`DECOMP` gave S1 the retirement of the four `mijual-*` binaries. **It moves to S2**, and one
thing is added:

1. **Do NOT delete `mijual-wordmark-{charcoal,white}.png` or
   `mijual-logo-ring-{charcoal,white}.png`.** `chrome/copy.ts` still points
   `RING_WORDMARK_WHITE` at `mijual-logo-ring-white.png`, and S2 is the slice that repoints
   it. If you delete the file here, the commit that closes S1 leaves the nav and footer
   rendering a broken image on every page of the product — a state someone could deploy from,
   eight days before the submission deadline. Retirement therefore lands in **the same commit
   that rewires the path**, which is S2's. Leave all four in place and hand the retirement
   forward in `phase.md`.
2. **Land the operator's delivered file byte-exact as well**, as
   `frontend/public/assets/juju-logo-source.png` — copied with `cp`, never re-encoded,
   verified by sha256 against
   `a22c9c4478e1a04a43022bf7c220d72581f62fade03072b053c20fd012ad8477` (235,823 b).
   Nothing references it and nothing should; it is the immutable record of what the operator
   actually delivered. The original lives in `~/Downloads/` and will not survive — once it is
   gone, every file in this directory is a derivative with no verifiable ancestor. 236 KB is a
   cheap price for that.

## What to produce

Three files in `frontend/public/assets/`:

| file | what | how |
|---|---|---|
| `juju-logo-source.png` | the operator's delivery, byte-exact, unreferenced | `cp` + sha256 check |
| `juju-wordmark-black.png` | the mark, trimmed | `-trim +repage` from the source |
| `juju-wordmark-white.png` | the same shape, white ink, for the cosmos-dark chrome | trim + an **alpha-preserving** recolor |

**On the filenames.** They are mine, not `DECOMP`'s, and the reasoning is worth one line in
the README: `mijual-` is the retired name and cannot stay; `-logo-ring-` describes a ring the
mark does not have; and `juju-` echoes the operator's own `juju_logo_no_back.png`. If you see
a concrete reason one of these is wrong, say so in `result.md` rather than silently picking
different names — S2 hard-codes whatever you produce.

**Ship both black and white.** Only the white one has a consumer today (`Wordmark.tsx`, via
`RING_WORDMARK_WHITE`), exactly as only the white ring did before. The black is for light
surfaces and must never reach the cosmos chrome — `phase.md` `## Decisions` records why
(its partial-alpha edge pixels carry near-white RGB and fringe light on dark).

## The derivation, and the trap in it

`phase.md` `## Decisions` records the verified finding: **`+level-colors white,white` alone
flattens the alpha channel** and yields an all-white opaque rectangle. Do not use it. The two
alpha-preserving forms, both already verified to keep all 42 distinct alpha values:

```
magick SRC -trim +repage -channel RGB +level-colors white,white +channel OUT
magick SRC -trim +repage -fill white -colorize 100                OUT
```

Pick one, run it, and **state in `result.md` the exact command you ran** — not the one you
meant to run. Then prove the output is what you claim, rather than asserting it:

- `identify` reports RGBA with an alpha channel, and dimensions **1213×319**;
- the count of **distinct alpha values is preserved** between the black and white variants
  (the shape is carried entirely by alpha, so any change here is a change to the artwork);
- every non-transparent pixel's RGB is `#FFFFFF` in the white variant and `#000000`-ish in
  the black one;
- the two variants have **identical alpha channels** — the strongest single check that the
  recolor changed color and nothing else. `magick a.png -alpha extract` on each and compare
  their sha256, or use `compare -metric AE` on the extracted alpha.

If any check fails, stop and report rather than shipping a mark whose shape drifted.

## The README rewrite

`frontend/public/assets/README.md` is currently written for **design-project exports** —
"delivered by the operator, exported from the design project", "not regenerable here", "do
not edit, re-export, downscale or re-compress". That provenance story is **false for these
new files** and must not be inherited by copy-paste. Two of the three are derivatives this
repository generated, and they *are* regenerable here — that is a different kind of trust,
and the README's job is to say which kind each file has.

Rewrite it to carry, honestly:

- **The source**: the operator's `juju_logo_no_back.png`, its sha256 and byte count, the date
  (today is 2026-08-30), and that it was delivered directly by the operator rather than
  exported from the Claude Design project.
- **Per derived file**: the exact command that produced it, and its own sha256 — so a later
  slice can re-run the command and prove the file was not touched since.
- **What the mark is**: a Korean wordmark 주주의관제탑 with a sparkle cluster at the upper
  right, and explicitly **no ring**. The retired ring closed R1's disclosed missing-symbol-mark
  gap; that gap is **open again**, and the README is where it gets disclosed, exactly as the
  old one disclosed the missing favicon.
- **The measured geometry**, because S2 and S5 need it and the gate turns on it: trimmed
  1213×319, ratio 3.80:1 against the retired ring's 6.29:1; the ink bbox is 946×161 at y=158,
  so **Korean glyphs occupy 50.5% of the box height** where the ring's ink filled 75.7%.
- **The favicon gap, still open and now with evidence**: the mark does not reduce — at 32px
  it is illegible. Keep the old README's rule that no image is substituted, generated or
  placeheld.
- **The font section is untouched.** `assets/fonts/PretendardVariable.woff2` is still a real
  design-project export under the original rules; carry its row, its sha256 and its
  "how the font is reached" section across unchanged.
- **The four `mijual-*` files**: still present, retired by `P10.S2`. Say so, so the README is
  never out of step with the directory.

Preserve what is still true; do not preserve what is no longer true.

## Constraints

- No TypeScript, no CSS, no wiring, no `doc-new-version`, no commits, no status transitions.
- Do not touch `assets/fonts/` or `public/foundations/`.
- Do not create a favicon, and do not crop the mark to make one — that is a filed operator
  question with three options and none of them is yours to pick.
- Do not re-encode, optimise, resize or strip metadata beyond the single documented command
  per file. `-trim +repage` and the recolor are the whole of it.
- Append your `## Doc impact` line(s) to `phase.md` if you change durable truth (a new brand
  asset set and the reopened symbol-mark gap plausibly do — `frontend.md` and `product.md` are
  the likely docs). Never run `doc-new-version` yourself.

## `phase.md` edits

Edit, do not merely append, and stay under budget (200 lines / 16 KB — it is at 177/13.8 KB,
so you are tight: drop the `(from P10.DECOMP, for P10.S1)` note you have now consumed, which
buys you the room).

Hand forward to S2, as a tagged note:

- the three filenames and the **natural dimension pair** `{ width: 1213, height: 319 }`;
- that **S2 owns retiring the four `mijual-*` binaries, in the same commit as the rewiring**,
  and why;
- the measured glyph-height numbers, so S2 can report what the signed h19/h17 actually
  produce rather than re-measuring.

Rewrite `## Now` (≤ 15 lines) last.

## Validation

- `shasum -a 256` on the landed source matches the operator's file exactly.
- The four `identify`/alpha checks above, each with its output quoted in `result.md`.
- `python3 scripts/workflow.py validate` passes.
- `cd frontend && npx tsc --noEmit` (or the repo's existing typecheck) still passes — you
  changed no TypeScript, so this is a cheap proof you did not break the build.
- Confirm the four `mijual-*` files are **still present** (this slice's correctness depends on
  their absence *not* happening).

## Verdict

`done` with a one-line summary naming the three files and the derivation command used.
`needs_operator` only for something genuinely undecidable here — the favicon and the chrome
heights are already filed as operator questions and are **not** reasons to stop.
