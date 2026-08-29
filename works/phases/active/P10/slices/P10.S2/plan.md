# Plan — P10.S2 (chrome, ops and document identity)

Read `works/phases/active/P10/phase.md` whole first. Its `## Context`, `## Decisions`, and the
two `for P10.S2` notes are the ground this builds on; the measured geometry is in there and
**you do not re-measure it**. `intent.md` is the confirmed operator intent.

This is the slice where the new mark first meets the product. S1 produced files; you decide
nothing about whether they were the right files, and everything about how they are wired.

## Scope boundary against S3 — read this before you touch a string

`DECOMP` listed the same few string sites under both S2 and S3. Resolving it: **you own the
identity strings bound to the mark and its chrome; S3 owns product-name prose everywhere
else.** Concretely —

**Yours:** `chrome/copy.ts` `BRAND_ALT_KO` and `COPYRIGHT_KO`; `app/layout.tsx` `metadata.title`;
`app/ops/layout.tsx` `metadata.title`; `components/ops/copy.ts` `OPS_MARK`.

**Not yours — leave them exactly as they are:** `components/event/copy.ts:114` (the 실권주
disclaimer), `src/mijual/web/app.py:57` (`TITLE = "미주알 API"`), and every doc comment
mentioning 미주알 anywhere. S3 sweeps those and needs them still present to prove its sweep
found everything.

Record this split in `phase.md` so S3 inherits it rather than rediscovering it.

## What to do

### 1. The wiring

`chrome/copy.ts:32–33` → `/assets/juju-wordmark-white.png`, natural pair
`{ width: 1213, height: 319 }`.

**Rename the constants**: `RING_WORDMARK_WHITE` → `WORDMARK_WHITE`, `RING_WORDMARK_NATURAL` →
`WORDMARK_NATURAL` (or better names if you have them — say why in `result.md`).
`chrome/Wordmark.tsx` is the only consumer. The `RING_` prefix and the doc comments above
those constants describe *the MIJUAL wordmark with its orbital ring* — a thing that no longer
exists. Rename and rewrite the prose together; a file whose values changed but whose comments
still explain the old mark is worse than one that was never touched.

**`Wordmark.tsx`'s header comment is now false** and S1 flagged it: it asserts the binary is
"the design project's own output, copied in byte-for-byte". The new mark is class **C**, a
repo-generated derivative (`phase.md` `## Decisions`). Keep the plain `<img>` and keep the
never-re-encode rule — both still hold, and `next/image` would ship a re-compressed
derivative — but re-state the *reason* truthfully rather than deleting the rule.

**Then delete the four `mijual-*.png`** from `frontend/public/assets/`, in this same slice, and
update the section of that directory's `README.md` that says S2 does it. Confirm by grep that
no reference to any `mijual-*.png` survives anywhere in the repo.

### 2. The heights — implement the signed numbers, report what they produce

`WordmarkProps.height` is the literal union `19 | 17` and there is **no CSS escape hatch**; the
inline style on the `<img>` is the only place a height is expressed.

**Do not change those numbers.** They are signed design record, the deviation is a filed
operator question, and the operator decides it at the acceptance gate with the running product
in front of them. Your job is to make the decision *easy* for them, not to make it:

- wire it at h19/h17;
- measure what actually renders — the `<img>`'s computed box and, from the geometry in
  `phase.md`, the Korean band's real pixel height at each size;
- look at it, and say in plain words whether the Hangul is legible at 9.7px in the nav and
  8.6px in the footer;
- check the **layout**, not just legibility: the mark is ~40% narrower than the ring
  (72×19 vs 120×19). The nav bar is a hard `height: 52px` with `align-items: stretch` and
  `.brand` re-centering via `inline-flex`; the footer's `.identity` is a flex row that wraps.
  A much narrower brand slot changes spacing and wrap behaviour — report what it does.
- state, as a recommendation the operator can accept in one word, what height you would use if
  the answer were yours.

### 3. The ops mark — change the string, do NOT change the typography

`components/ops/copy.ts:32` `OPS_MARK`: `"MIJUAL OPS"` → **`"주주의관제탑 운영"`**.

This string is the standing assumption from intent capture — the operator was told and did not
object, but never confirmed it in words. Implement it; the question stays filed.

**Leave `Ops.module.css` `.mark` and `.doorMark` alone.** Both set
`font-family: var(--font-mono)` with `letter-spacing: 0.08em`, because the design record called
the mark "an identifier, so it stays raw and mono". IBM Plex Mono carries no Hangul, so the
Korean will fall through to a system monospace and 0.08em tracking on Hangul reads wrong. That
is a **typography decision on signed styling**, and it is the operator's, not yours. Also note
`--font-mono` is defined in `public/foundations/tokens.css`, a **byte-verbatim vendored design
foundation** — never edit that file.

So: implement the string, look at both `/ops` surfaces (the bar via `OpsChrome.tsx` and the
door via `Door.tsx`), and sharpen the existing operator question with what you actually saw and
a concrete recommendation. Do not silently fix it.

### 4. The favicon — ship nothing, and say so

There is no favicon of any kind today: no `app/icon.*`, no `favicon.ico`, no `manifest`, no
`openGraph`/`twitter` metadata, and neither `metadata` export declares `icons`. The browser
gets its 404 default. **That is the status quo, not a regression this phase introduces.**

`DECOMP` verified the mark does not reduce — at 32px it is illegible mush — and the assets
README's rule forbids substituting, generating or placeholding an image. **Create no favicon
and crop nothing.** Confirm in `result.md` that the pre-existing state is unchanged, and leave
the filed operator question standing with its three options (ship nothing / operator supplies a
square symbol export / operator authorizes cropping the sparkle as a symbol).

## Constraints

- Nothing outside your scope boundary above. No `doc-new-version`, no commits, no status
  transitions, no `accept-gate`.
- Do not edit `public/foundations/*` — vendored byte-verbatim design foundations.
- Do not switch to `next/image`.
- Do not change `h19`/`h17`, and do not widen the `19 | 17` union.

## Validation — verify in the operator runtime, and nowhere else

`docs/current/operations.md` `## Operator Runtime` is filled and governs: `make stack-up`, dev
at `http://127.0.0.1:3000`, Chrome desktop plus a mobile viewport, **and additionally the
production build** (`cd frontend && npm run build && npm run start`) since dev and production
can differ. `make stack-status` prints the URLs; `make stack-down` stops it. Logs in
`var/stack/`.

Required:

- `cd frontend && npm run typecheck` — clean (the constant renames are exactly what this
  catches).
- `cd frontend && npm run smoke` — the `node --test lib/*.test.ts` suite still passes.
- **A real browser, dev**: the nav mark and the footer mark both render the new white wordmark
  on the cosmos-dark chrome — visible, not a broken image, not fringing. Report the computed
  box of each `<img>`.
- **A real browser, production build**: the same two, because a missing/renamed static asset
  behaves differently under `next build`.
- `/ops` — the bar mark and the door mark, both rendering the Korean string.
- Both document titles in the browser tab.
- `grep -rI "mijual-.*\.png" .` (excluding `node_modules`, `.next`, `works/`, `docs/versions/`)
  returns nothing live.

You are **not** doing the comprehensive sweep — that is S5's whole job. Verify what you
changed, well, and hand the rest forward.

Note: no test and no type will catch a wrong asset path — a string literal 404 is invisible to
`tsc`. The browser check is the only thing standing between this slice and a broken mark.

## `phase.md`

**It is at 188 lines / 15.6 KB against a 200 / 16 KB budget — you must compress, not append.**
Drop both `for P10.S2` notes (you consume them) and tighten `## Decisions` where S1's detail has
served its purpose; the pre-edit notebook is in git and the detail lives in each `result.md` by
path. Add the S2/S3 scope split, a tagged note for S3, and rewrite `## Now` (≤ 15 lines) last.
Sharpen the two operator questions you touched (ops mark, heights) with what you measured.
Append `## Doc impact` lines for durable truth you changed. Do not touch the generated
`## Slices` block.

## Verdict

`done` with a one-line summary. `needs_operator` only if something genuinely blocks — the
heights, the ops typography and the favicon are all **filed questions with defined defaults**
and are explicitly not reasons to stop.
