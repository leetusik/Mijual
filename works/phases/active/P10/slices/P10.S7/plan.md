# Plan — P10.S7 · Apply it all

`kind: implementation` · `risk: high` · order 7 · the phase's last work slice before `P10.REVIEW`

Everything round 2 owes, in one slice, because the operator asked for exactly that: *"just one
design round and then do rest."* The design round (`P10.S6`) has landed as **R17**; this slice
implements it and the operator's four directed items alongside it.

**RESPECT THE DESIGN.** R17 is signed. Nothing it decided may be dropped, simplified, restyled or
"improved". Where it gives an exact value, use that value. Where it does not, pick the option
closest to its intent, never a plainer fallback.

## The authority, and how to read it

- **`docs/reference/design/rounds/17-brand-mark-launcher/output/build-prompt.md` — the contract.
  Build from this alone.** It is complete and its §5 states there is no open decision. Every value,
  command, state and supersession is in it.
- `output/result.md` — the *why*, including three findings you must not re-derive from scratch but
  **must** honour (§1b, §5, §7b).
- `output/r17-mark.css` — the geometry canon.
- `docs/reference/design/SIGNOFF.md` § R17 — what supersedes what.

The record is **read-only**. If you find a nit in it, catalogue it; never edit it.

## Operator runtime — where "verified" has to mean something

`docs/current/operations.md` § Operator Runtime, and it is filled (no `UNFILLED`). `make stack-up`
**does not work**: host port 5433 is held by `changple_web_dev_postgres`, which must never be
stopped. The way through — same image and `mijual_mijual-pgdata` volume on **5434** via an
`!override` compose fragment, plus throwaway `MIJUAL_OPS_ID` / `MIJUAL_OPS_PASSWORD` for `/ops` —
is written out with real command bodies in `slices/P10.S5/result.md` §0 and versioned in
`operations.md` § Local Development. **Read it before starting the stack.**

Verify in **dev** (`http://127.0.0.1:3000`) **and additionally in the production build**
(`npm run build && npm run start`), at **1280 and 390**. Your convenient runtime is not the
operator's.

---

## Block 1 — brand binaries

In `frontend/public/assets/`.

**Land as class B, byte-exact, never re-encoded:**

- `~/Downloads/juju2_2.png` → `juju2-logo-source.png`
- `~/Downloads/favicon_and_chatbot_widget.png` → `juju2-symbol-source.png`

**Derive as class C, by the contract's commands verbatim** (§0) — `juju2-wordmark-white.png`
(1292×371) and `juju2-symbol-white.png` (222×165).

**Two guards, both mandatory, both from real defects in the operator's own files:**

1. **The wordmark derivative must have 0 opaque near-white pixels.** The first delivery had 2,864
   inside 「의」's counter; the alpha-preserving recolor keeps opaque pixels opaque, so they render
   as a solid white blob — **only in the white variant, which is the only one the product uses.**
   Check it and put the number in `result.md`.
2. **Never `-trim` the symbol — crop it**: `-crop 222x165+39+62`. `-trim` reports 261×216 because
   two low-alpha ghost fragments sit bottom-left; the recolor turns them into visible smudges on
   the cosmos surface. After cropping, a re-trim must return `222x165+0+0` exactly.

The README's two ImageMagick traps still apply and are not optional: the `-channel RGB … +channel`
guard (without it `+level-colors` flattens alpha to an opaque rectangle) and
`-define png:color-type=6` (without it you silently get GrayscaleAlpha).

**Retire — delete from the working tree:** `juju-logo-source.png`, `juju-wordmark-black.png`,
`juju-wordmark-white.png`. Delete them **in the same commit** that repoints the chrome, exactly as
`P10.S2` did with the `mijual-*` set — the white one is the only image the app loads, so deleting
it earlier leaves every page rendering a broken image.

**Do not create a black variant.** Nothing references one and the contract does not name one. Say
so in the README rather than leaving the absence unexplained.

**Verify derivations by pixel signature** (`identify -format '%#'`), **never by file sha256** —
re-deriving changes the container, not the pixels. Record both anyway, as the README already does.

## Block 2 — the wordmark in the chrome

Per contract §1. `Wordmark.tsx`: `height` prop `19 | 17` → **`27 | 24`**; the component carries the
ink offset itself (`translateY(-7px)` at 27, `-6px` at 24) because a caller can forget it; intrinsic
`width`/`height` attributes become **1292 / 371**. Call sites: `Nav.tsx` → `height={27}`,
`Footer.tsx` → `height={24}`.

**Keep the plain `<img>`.** `next/image` is forbidden here and the reason is in the file's own
comment: it serves a re-compressed derivative, which destroys the pixel-signature proof that is
this binary's only link to the operator's file.

`Nav.module.css` and `Footer.module.css` keep their existing spacing — **do not shrink
`gap: var(--space-6)` or `.identity`'s `gap: var(--space-3)`.** The sparkle overhangs the glyphs to
the right, so the optical gap is already larger than the declared one; closing it makes the sparkle
bite the links.

Update the doc comment in `Wordmark.tsx`: the paragraph calling h19/h17 "signed, and whether they
are still right is an open question for the operator" is now **answered**, and must be replaced,
not left contradicting the code.

## Block 3 — the footer overlap (a dead interaction, not a cosmetic bug)

Contract §1, and this is a **real defect R17 found**: the launcher covers the footer's
「의견 보내기」 button by a **constant 68px at every viewport ≤1120px**, zero at ≥1256.
`Feedback.tsx` anchors its 380px panel on that button, so the covered control is dead, not merely
overlapped.

**Both measures, and neither replaces the other:**

1. corner reservation on `.inner` so whatever ends the row clears the launcher;
2. hide the duplicated 「AI 질문」 footer link on desktop — R8 §1's "the same destination is not said
   twice in the bar". **≤767px keeps it**: the launcher does not render there, so the footer link is
   the only entry point.

The link needs a class to be hidden by; add one. **Structure, content and order are unchanged —
only spacing and one desktop-only visibility rule.**

## Block 4 — the launcher

Contract §3, which gives the whole replacement CSS and the state table. `Launcher.module.css` is
largely replaced (~213 lines → ~90): the planet, band, both clipped ring halves, both `@keyframes`,
both `data-motion="tick"` hooks, `#dfe9e4` and the two animation durations all go. `AskLauncher.tsx`
collapses four mark spans into one.

**What this retires is bigger than a mark:** R6 granted the launcher the product's *one* sanctioned
ambient-motion exception, and it expires here. After this slice the product has **no ambient motion
anywhere**, and R1's "no spinners, no ambient motion" holds without exception.

Because the motion is gone, **hover response moves to colour** (`#eaf2ed` → `--live`) and — this is
deliberate — **survives `prefers-reduced-motion`, because colour is not motion.** Do not "tidy" that
into the reduced-motion block. R17 also adds `focus-visible` (`outline: 2px solid var(--focus-ring)`,
offset 2px, mark `--live`), which R6 had left to P7.

R14's existence boundary is untouched: desktop only, never `/ask`, never ops.

## Block 5 — the favicon, at last

Contract §2. The operator answered the gate's favicon question by supplying a square symbol export,
so the assets README's "no favicon, and this mark does not become one" section is **retired by
R17** — quote the contract when you rewrite it.

Opaque **`#0a1310`** tile (never transparent — it vanishes on a light tab), white symbol at the
**84% ink-width rule**, sizes **16 / 32 / 180**, where 16 is a **downscale of the 32 raster and not
separate artwork**. Use Next's `app/` file conventions rather than hand-written `<link>` tags.

Two bounds: the single-star crop is **explicitly not adopted** (one artwork, one rule — R17 §6), and
the 16px softness is a **recorded limitation**, not a bug to fix. Do not invent a second icon
variant.

`layout.tsx`'s metadata comment currently explains why there is *no* favicon. Replace it.

**Verify a real `link[rel*=icon]` reaches the browser in dev and in production** — `P10.S5` proved
the absence by inspecting the served HTML; prove the presence the same way.

## Block 6 — the `/ops` mark

`components/ops/Ops.module.css`: drop `--font-mono` **and** the `letter-spacing: 0.08em` from
`.mark` and `.doorMark`. The string does not change. Operator's literal answer at the gate: *"Drop
mono, use Pretendard 600."*

R7 called the mark "an identifier, so it stays raw and mono" — written for a latin string. With
`주주의관제탑 운영` it styles **one glyph of nine, the space**, which is what produced the 2.84×
fake double space and left the other eight glyphs to whatever Korean face the OS has.

Note the answer names a **weight**, not a family: Block 7 replaces the family underneath it, so the
mark lands as **600 in the shipped Korean face**. That is the intended outcome, not a drift.

## Block 7 — the Korean font pipeline

The operator's instruction was to research `~/projects/personal/changple_web` and use the same.
**Read it rather than reinventing it:** `src/app/fonts.ts`, `scripts/subset_noto_sans_kr.sh`,
`scripts/gen-korean-charset.mjs`, `src/app/fonts/`, and the `noto` assertion in
`tests/browser/smoke.spec.ts`.

**Adopt:** self-hosted **Noto Sans KR** (variable `wght 100–900`) and **IBM Plex Mono** subsets via
`next/font/local`, `display:"swap"`, `preload:true` for the Korean face and `false` for the mono,
CSS variables, OS fallbacks, an auto-generated charset, a pinned google/fonts source SHA, and the
OFL attribution files beside the fonts. `pyftsubset` is installed at `/opt/homebrew/bin/pyftsubset`
and its interpreter has `brotli`, so woff2 output works.

**Two constraints their comments carry, both load-bearing:** the charset is auto-extracted because a
hand-maintained one went stale and rendered missing syllables **자모 분리**; and the subset
deliberately **omits the conjoining-jamo block U+1100–11FF** so an unknown syllable falls back to
the system font *composed* rather than decomposed.

**Retire:** `public/foundations/fonts.css` (a class-A vendored R1 export marked "do not edit"), the
**2,057,688-byte** `public/assets/fonts/PretendardVariable.woff2`, and `layout.tsx`'s IBM Plex Mono
`@import` **to the Google Fonts CDN** — self-hosting removes a third-party request from every page.
Both retirements are operator-directed supersessions of signed material; record them in the README
the way the four `mijual-*.png` are recorded: what it was, its sha256, why nothing loads it.

**Do not edit `public/foundations/tokens.css`.** It is frozen (R8, byte-verbatim) and it defines
`--font-sans` and `--font-mono` as Pretendard / CDN Plex Mono. Override those two variables in
**`app/shell.css`** — application code, not the vendored record — pointing at the `next/font`
variables. R17 did the same thing inside its cards and explicitly recorded the token as **not**
superseded.

### One adaptation, deliberate and flagged

changple_web subsets to *rendered* glyphs and lets dynamic database copy fall back to the OS font.
**Mijual is not the same product**: it renders **DART company names** on the board, on every event
page and throughout `/ask`, and those are dynamic. A rendered-glyph-only subset would put half of
what the reader actually looks at in a different typeface from the UI around it.

So: **extend Hangul coverage far enough that company names render in the web font** — measure the
options (auto-extracted glyphs alone; plus the KS X 1001 common set ≈2,350 syllables; the full
11,172-syllable block) and choose the smallest that keeps dynamic Korean in the shipped face.
**Report the payload number for each in `result.md`.** Even a several-hundred-KB subset is a large
improvement on today's 2,057,688 bytes, so do not sacrifice correctness to hit changple_web's
100 KB, which was set for a product with no dynamic Korean.

Add a one-line entry to **`## Operator Questions`** in `phase.md` naming the coverage chosen and its
payload, so the review routes it and the operator can pull it back if they disagree.

## Block 8 — the record

- **Rewrite `frontend/public/assets/README.md`.** Not a patch: three files are superseded, two
  class-A font files leave, the favicon prohibition is retired, and two new class-C derivatives
  arrive with a *crop* in one of the commands. Keep its provenance-class structure and its
  "verify by pixel signature, not sha256" rule.
- **Append `## Doc impact` lines to `phase.md`** — one per durable-truth change. **Do not run
  `doc-new-version`**; the review consolidates.
- Draft the phase's new **`## Regression Checklist`** lines in `result.md` for the review to append:
  the mark at its new size on both chrome surfaces, the favicon actually present, the launcher's
  states with no ambient motion, the footer button reachable, and the Korean face served
  self-hosted.
- **Edit `phase.md` under budget** (200 lines / 16 KB) — replace superseded decisions rather than
  stacking, drop the notes you consumed, rewrite `## Now` last.

---

## Out of scope — do not touch

Code identifiers (`src/mijual/`, `MIJUAL_*`, `X-Mijual-CSRF`, the repo directory, both package
`name` fields, the DB credential, the Claude Design project's name), the three dev-tooling banners,
and P4's mail subject. All are the operator's explicit decisions or already-filed deferred jobs.
**No new user-facing string** — R17 added zero and this slice adds zero.

## Validation

Beyond `python3 scripts/workflow.py validate`:

- `npm run typecheck`, `npm run build`, `npm run smoke`; `pytest` if anything under `src/` changed
  (nothing should).
- **The contract's own render checks** (§1): nav h27 → box top 5.5px, glyph band centre **26.10px**
  against the bar's 26px optical centre; footer h24 band centre within ±0.3px of the row's; minimum
  vertical clearance ≥4px.
- **The footer fix, measured**: 의견 보내기 is clickable and its panel opens at **1280, 1120 and
  1024**, and the desktop 「AI 질문」 link is gone while the ≤767 one remains.
- **The launcher**: rest / hover / active / focus-visible / open / reduced-motion all render as the
  state table says, and **no animation remains** — grep the file and confirm in the browser.
- **The favicon**: `link[rel*=icon]` served in dev *and* production; the tile is opaque.
- **The font**: the served page uses the self-hosted face, a woff2 is preloaded, **no request goes
  to `fonts.googleapis.com` or `fonts.gstatic.com`**, and a **company name renders in the same face
  as the UI** — check a real one on the board and an event page.
- Screenshots at 1280 and 390, dev and production, into `var/p10s7/`.

**Keep tests terse** — the contract's small-test-files rule applies to verification too. Measure,
screenshot, report; do not build a conformance suite.

## If the slice proves too large

Do the blocks **in order** — each is coherent on its own, so a partial is still a usable state.
Reserve `needs_operator` for a genuine operator decision. If you cannot finish every block to the
bar, finish the ones you can **properly**, and say plainly in the verdict and at the top of
`result.md` which blocks remain and why. A shallow pass over all eight is worse than a solid pass
over six; I will cut a follow-up slice. Do not report completion you did not reach.
