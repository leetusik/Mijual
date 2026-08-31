# Plan — P10.F3 · 로고를 옆 글자에 맞춘다

**Kind/risk:** `fix / high` → `slice-executor-high`.
**Origin:** the operator's failure report at the **round-3 acceptance gate**, recorded verbatim as
`P10`'s `review.note`:

> 로고 글자가 옆 nav 링크 글자보다 아래로 내려가 있다. R17의 잉크 정렬은 마크를 '바'의 광학
> 중심에 맞췄을 뿐, '옆 글자'와 맞춘 적이 없다. 텍스트 기준 수평 정렬(공유 베이스라인/광학선)로
> 바꿀 것.

The operator is the design authority here and this is a literal instruction given at their own gate.
It **supersedes** R17's `INK_OFFSET 0.2628·H`, which R18 had explicitly re-confirmed as unchanged
(`SIGNOFF.md`, `docs/reference/design/rounds/18-p10-review/handoff.md`). Superseding a signed value
is the operator's to do and they have done it; your job is to execute it and record the supersession
— **not** to reopen anything else R17 signed.

---

## 1. The defect, in the numbers the repo already holds

R17 derived the offset from the **image alone**: the Korean glyph band's geometric centre sits at
**76.28 %** of the 1247×371 box, so the image is lifted by `0.2628 × H` to put that centre on the
centre of *the row it sits in*. `docs/current/frontend.md` states the achieved result in exactly
those terms — the h27 band centre at **25.60px** against *"the bar's real optical centre of
25.50px: +0.1px"*, and in the footer **+0.31px** off *that row's* optical centre.

That is the whole bug. **The row's centre is not where the neighbouring type's ink is**, for two
compounding reasons, and neither entered R17's derivation:

1. `Nav.module.css` `.link` stretches to the bar's **51px** content box (`.bar` is `height: 52px`
   border-box with a 1px bottom hairline) and carries `border-bottom: 2px solid transparent`, so its
   `inline-grid` / `place-items: center` cell is centred in **49px** — the label's *line box* centre
   already sits ≈ **24.5px**, about 1px above the bar's 25.5.
2. Inside that line box, Hangul **ink** is not centred: it occupies the ascent side of the baseline
   with effectively no descender, so the ink centre sits higher again by roughly half the
   descent-side leading.

Both push the link's ink **up**; the mark's band stays at 25.60; the mark reads low. Expect the
total to land somewhere around 2–4px — **but do not use that estimate for anything.** Measure it.

The footer is the same shape at smaller magnitude: `Footer.module.css` `.identity` is
`display: flex; align-items: center` with the h24 mark beside `.source` at `--text-sm` (12px). Same
law, different neighbouring type — so it is in scope even though the operator named the nav. One
component owns both numbers.

`/ops` is **not** in scope: its mark is the `OPS_MARK` *string* in Pretendard 600, not this image
(`grep` confirms `Wordmark` is imported only by `Nav.tsx` and `Footer.tsx`).

## 2. What changes

The alignment law. `INK_OFFSET` stops being a function of the image's internal geometry and becomes
a **measured relationship between two rendered ink boxes** — the wordmark's Korean glyph band, and
the Hangul ink of the type standing next to it — computed per surface.

Code change is expected to be small and confined to `frontend/components/chrome/Wordmark.tsx`
(the constant plus the doc comment that derives it). If you find you need to touch a stylesheet to
express it, that is allowed but say why in `result.md` — a `transform` on the image is what the
component already uses and it has no layout consequence, which is the property that keeps this a
one-file change.

## 3. Steps

### 3.1 Measure, in the operator runtime, with a live document

`docs/current/operations.md` `## Operator Runtime` is the runtime: `make stack-up`, dev at
`http://127.0.0.1:3010`, production `npm run build && npm run start` on the same origin, at **1280**
and a true **390** (`mobile: true`, dsf 3). **Aside is not installed on this machine** (not on
`PATH`, no app bundle) — the fallback every slice in this phase has used is **real Chrome over
CDP**, and that is the instrument here too. Name whichever you actually used in `result.md`; never
claim a browser run you did not make.

Produce an absolute table, in bar/row coordinates, of:

- **the nav link's type** — the baseline y, and the ink top/bottom of a real label (`AI 질문`,
  `보유 종목`), in both the active (600) and inactive (400) weights.
- **the footer's `.source`** — the same, at 12px.
- **the wordmark's glyph band** — its rendered ink top/bottom/centre on each surface, at the
  *current* offset, so the measured delta is the misalignment the operator is looking at.

**Two independent methods, and they must agree** — this phase has now shipped four checks that could
not fail, and the standing rule is that a guard is only a guard if some input makes it report
failure:

- (a) **from the document**: canvas `TextMetrics` with the element's own computed `font` shorthand
  (`actualBoundingBoxAscent` / `actualBoundingBoxDescent` give ink relative to the baseline), plus
  the DOM baseline y from a zero-height inline probe or `Range.getClientRects()`.
- (b) **from the pixels**: screenshot the bar at a high `deviceScaleFactor` and scan for ink —
  the same technique `P10.F1` used on the favicon tiles. Scan *columns that contain only the label*,
  and for the mark scan the **band's** columns, not the sparkle's.

If (a) and (b) disagree by more than a rounding, stop and find out why before computing anything.

### 3.2 Compute both laws the operator named

For each surface, in exact px and then rounded to whole px (R17's integer-px rounding rule stands —
it exists because the PNG resamples to a fractional height anyway):

- **shared baseline** — the band's ink bottom on the text's baseline. Hangul carries essentially no
  descender, so the band's ink bottom *is* the mark's baseline; **confirm that from your pixel scan**
  rather than asserting it.
- **shared optical line** — the band's ink centre on the text's ink centre.

### 3.3 Choose one — by looking

Render both candidates, screenshot the nav and the footer at ≥4× at 1280 and 390, and compare. Adopt
one, state the rejected one's number, and say in one sentence what made the difference on screen.
If the two round to the same integer px, say so and note that the choice was moot.

The band (12.81px at h27) is taller than the link's Hangul ink (≈ 9.7px at 13.5px type), so the two
laws will **not** generally agree — this is a real visual judgment, and the operator delegated it by
naming both. Make it honestly and record it; they will see the result at the re-opened gate.

### 3.4 Apply

In `Wordmark.tsx`, per height. **The offset stays a module constant inside the component, not a
call-site prop** — R17's reason for that is untouched by this change and is quoted in the file.
Rewrite the doc comment's `## The two heights, and the offset that comes with them` section so the
derivation in the file is the *new* one; leave the "never re-encoded" and "height-constrained
rendering only" rules exactly as they are.

If the nav and the footer turn out to need different *laws* (their neighbouring type differs — 13.5px
vs 12px), keep one law and two numbers. If one law genuinely cannot serve both, **say so and propose**;
do not invent a second rule silently.

**In passing, one correction this slice is the right place for:** the doc comment still quotes R17's
`26.10px` band centre; the measured value in the 51px content box is **25.60**. `phase.md`
`## Notes for later slices` asks for exactly this fix "next time that file is edited" — this is that
time. It will be superseded by your own new numbers anyway; make sure nothing stale survives.

### 3.5 The clearance check — **this one can block**

Moving the mark up shrinks its **top** clearance, and the sparkle cluster is flush to the box's top
edge. Today the h27 box top is at **5.00px** under the hairline. Measure the new top clearance at
h27 after the change.

If it is **< 2px**, or the sparkle's ink visibly touches or crowds the 1px hairline at either
viewport, **stop and return `needs_operator`** with the measured number and the options (a smaller
h, or accepting the crowding). Shrinking R17's signed h27 is a design decision this slice does not
own, and the operator questioned the *offset*, not the size.

### 3.6 Prove the check can fail

Run your chosen alignment check **against the pre-change build** and show it reporting the
misalignment the operator saw. If it passes on the old code, it is the wrong check and the number it
produces means nothing. This is the phase's own standing rule and round 3 caught a fourth violation
of it; do not add a fifth.

### 3.7 Verify nothing else moved

- the wordmark PNG is **byte-identical** — 1247×371, not re-derived, not re-encoded, not replaced.
- render widths **90.75 / 80.67px** unchanged (nothing horizontal moves).
- `P10.F2`'s active-tab reservation still holds: the `left` arrays
  (`[...document.querySelectorAll('header nav a')].map(a => a.getBoundingClientRect().left)`)
  identical to the decimal across nav routes.
- the launcher keeps `mask-size: 84%`; the favicon tiles keep 75 % and stay transparent `#2b8e6c`.
  **"Making them consistent" is the regression** — do not.
- the footer's corner reservation (`.inner:global(.content)` at 108px) and `html:root` for the font
  tokens are cascade traps; **do not "simplify" either selector.**

### 3.8 Validate

`npm run typecheck`, `npm run build`, `npm run smoke`, `python3 scripts/workflow.py validate`, and
the browser sweep of §3.1/§3.7 in **dev and the production build**, at 1280 and 390. Dev and
production must agree to the hundredth of a pixel, as every prior slice in this phase has proved.

## 4. Constraints — RESPECT THE DESIGN

- **h27 / h24 do not change.**
- The binary is untouched; `frontend/public/assets/README.md`'s class-C pixel-signature proof must
  still hold unchanged.
- Nothing horizontal moves.
- Nothing about the launcher, the favicon, the tab reservation, the corner reservation or the fonts
  is in scope.
- Do not run `doc-new-version`. Doc versions are consolidated once, at `P10.REVIEW`.

## 5. Doc impact you will owe (one-line notes appended to `phase.md` `## Doc impact`)

Three durable truths are **falsified** by this slice, and each note must be specific enough for the
review to version from it:

1. **`frontend.md`** — the alignment law. Its current sentences ("band centre 25.60 against the
   bar's real optical centre of 25.50: +0.1px", and the footer's "+0.31px … entirely the integer-px
   rounding") describe alignment **to the row**, which is precisely what the operator rejected.
   Replace with the text-referenced law and its measured numbers, and with the new top clearance.
2. **`qa.md`** — the regression-checklist line **「세로 기하는 움직이지 않았다」** asserts
   `INK_OFFSET_PX = {27: 7, 24: 6}`, `translateY(-7px)/-6px` and the 25.60 band centre. That line is
   now **wrong** and would fail the next regression sweep for the wrong reason. It must be replaced
   by a check of the new law **that can fail** — one that reports failure when the mark is put back
   where it was.
3. **`decisions.md`** — the supersession itself: the operator superseded R17's `INK_OFFSET 0.2628·H`
   at the round-3 acceptance gate, R18 having re-confirmed it; what is now aligned to what, on which
   two surfaces, and which of the two named laws was adopted and why.

## 6. `phase.md`

Edit it under budget (200 lines / 16 KB — it is already near the ceiling, so **compress**, do not
append). Replace the superseded `## Decisions` bullet about R17's vertical constants rather than
stacking a contradiction next to it; drop the `## Notes for later slices` entry about the `26.10px`
comment, which you will have consumed. Leave the generated `## Slices` block alone.

## 7. What "done" looks like

The mark's glyphs and the neighbouring links' glyphs read as **one line** at 1280 and 390 in both
runtimes; every number behind that came out of a live document by two agreeing methods; the check
was shown failing on the old build; the top clearance is stated; nothing else in the chrome moved;
and the three doc-impact notes are on `phase.md`.
