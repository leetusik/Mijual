# Result — P10.F3 · 로고를 옆 글자에 맞춘다

- **status:** `done`
- **summary:** R17's image-derived `INK_OFFSET 0.2628·H` is replaced by a measured, text-referenced
  law — the mark's Korean glyph band now sits on the **same baseline as the Hangul standing beside
  it**. One constant moves (`27: 7 → 8`); the footer's `24: 6` is re-derived from the same law and
  proved already correct. Every number came out of a live document by two agreeing methods, the new
  check was shown failing on the pre-change placement in both runtimes, and the top clearance is
  **4.00px**.
- **files_changed:** `frontend/components/chrome/Wordmark.tsx` (the constant + the derivation in its
  doc comment) · `works/phases/active/P10/phase.md` · this file
- **validation:**
  | command | result |
  |---|---|
  | `npm run typecheck` | **pass**, no output |
  | `npm run build` | **pass** — 18/18 static pages, 19 routes |
  | `npm run smoke` | **pass** — 22/22 |
  | `python3 scripts/workflow.py validate` | **pass** — "Workflow validation passed." |
  | alignment check, dev (shipped) | **10/10** — 5 PASS at 1280, 5 N/A at 390 (no label shares the bar) |
  | alignment check, production (shipped) | **10/10**, identical to dev to the hundredth of a pixel |
  | alignment check, **negative control** (`-7`, dev **and** production) | **5 FAIL / 5 N/A** — the check has teeth |
  | §3.7 "nothing else moved" sweep, dev **and** production | **pass**, every field byte-identical between the two |
- **deviations:** three, all in §3.2/§3.3's *derivation*, none in scope — see §3 below.
  (1) The plan's premise «Hangul carries essentially no descender» is **false for the neighbouring
  type** and I measured it rather than asserting it, so "shared baseline" is implemented as *Hangul
  block bottom to Hangul block bottom*, not as *band bottom on the alphabetic baseline* (which
  paints the mark ~1px **high**; its number is given). (2) §3.1's two methods disagree by 0.28px in
  the **footer** — cause found and named (Chrome pixel-snaps the mark's paint origin), and both
  methods still yield the same integer, so I computed. (3) The 메뉴 button at 390 is **reported but
  not judged** by the shipped check: it is the one neighbour where the two methods disagree (0.52px).
- **doc_impact:** three notes appended to `phase.md` `## Doc impact` (`frontend.md`, `qa.md`,
  `decisions.md`) — reproduced verbatim in §7.
- **instrument:** **Aside is not installed on this machine** (`aside` not on `PATH`, no
  `/Applications/Aside.app`), so per the doctrine's own fallback I drove **real Chrome
  152.0.7977.64/.65 over CDP** — the same instrument `P10.S7`, `P10.REVIEW` r1–r3, `P10.F1` and
  `P10.F2` used — in the runtime `docs/current/operations.md` `## Operator Runtime` names:
  `make stack-up`, dev at `http://127.0.0.1:3010`, **and** `npm run build && npm run start` on the
  same origin, at 1280 and at a true 390 (`mobile: true`). My readings reproduce the phase's standing
  numbers exactly (`218.75`, `279.484375`, `90.75×27`, `80.66×24`, band centre `25.5957`), which is
  the evidence that the instrument is equivalent to the earlier slices'.

Phase-level state (the superseded decision, the three doc-impact notes, the new operator question,
the handoff) is in [`phase.md`](../../phase.md) and is **not** restated here.

---

## 1. What the operator saw, in numbers

R17 derived the offset from the image alone (glyph-band centre at 76.28 % of box height → lift by
`0.2628 × H`) and so put the band on the **row's** optical centre. Measured in the running product
at 1280, with `translateY(-7px)`:

| | ink top | ink bottom | ink centre |
|---|---|---|---|
| wordmark glyph band (h27) | 19.191 | **32.000** | 25.596 |
| `.link` 보유 종목 400 | 19.358 | **31.083** | 25.221 |
| `.link` 보유 종목 600 | 19.207 | **31.189** | 25.198 |
| `.link` AI 질문 400 / 600 | 18.873 / 18.771 | **30.947 / 31.091** | 24.910 / 24.931 |

The mark's ink bottom sat **0.81–1.05px below** every neighbouring label's, and its band is 1.1px
taller than the label ink, so the mark reads sunk. That is the defect, and it is about **1px**, not
the 2–4px the plan estimated — the plan's compounding argument is only half right: `.link` *is*
centred in a 49px cell (it stretches to the bar's 51px content box and carries a 2px transparent
bottom border), so its **line box** centre is at 24.49 against the bar's 25.50; but the Hangul **ink**
inside that line box sits *lower* than the line-box centre, not higher, which cancels most of it.

## 2. Two independent methods, and where they agree

- **(a) from the document** — a zero-size `inline-block` probe inserted as the element's first child
  (its `bottom` is the baseline; the element's own rect is asserted unchanged before/after) plus
  canvas `TextMetrics` with the element's **own computed `font` shorthand**
  (`actualBoundingBoxAscent/Descent`). The band comes from the `<img>`'s rect and the PNG's ink rows,
  which I re-derived from the binary rather than trusting the record: alpha-extract row profile says
  the sparkle occupies rows **0–164**, then **30 empty rows** (165–194), then the Korean glyph band
  **195–370** of 371 — flush to the bottom, band centre at 283/371 = **76.28 %**, confirming R17's
  own geometry.
- **(b) from the pixels** — an **8×** raster of the whole viewport (`deviceScaleFactor: 8`, **no
  clip**, so device row ÷ 8 *is* the CSS y and there is no clip-origin rounding), scanned row-wise
  inside band-only column windows (the mark's band spans x 15–1086 of 1247; the sparkle is 1025–1246,
  so the scan stops at x 178 and never sees it).

Agreement, nav at 1280 (the surface being changed):

| | (a) document | (b) pixels | Δ |
|---|---|---|---|
| band ink bottom, `-7` | 32.000 | 32.000 | 0.000 |
| band ink top, `-7` | 19.191 | 19.250 | 0.059 |
| 보유 종목 ink bottom | 31.083 | 31.125 | 0.042 |
| **required offset** | **7.917** | **7.875** | **0.042** |

Both methods round to the same integer. Two negative controls ran alongside: an empty column window
(x 200–215) reports **no ink**, so the cosmos starfield is not tripping the scan; and the
`AI 질문` window shows a 7-device-column stem starting 1px above the Hangul — the latin **I**'s cap,
which is why the pure-Hangul label is the reference.

**Where they disagree, and why (deviation 2).** In the **footer** the two methods differ by 0.28px on
the relationship. Cause, found before computing anything: the footer's mark is laid out at a
**fractional** y (`652.484375`), and Chrome paints it at `round(layoutTop)` — the painted band is
0.484px above where `getBoundingClientRect()` puts it. I proved this rather than assumed it: a
grid-aligned capture reproduced the 0.484 shift exactly, and an ImageMagick resample of the PNG to
both device heights (216 = h27@8×, 192 = h24@8×) shows the bottom output row still carrying
alpha ≥ 128 in 47–51 columns, which rules out the resample as the cause. Both methods still give
**6** for the footer, so the disagreement changes nothing; it does mean the footer's *painted*
residual varies by up to ±0.5px with where the footer lands on the page, which no single offset can
remove.

## 3. The two laws the operator named, computed — and the choice

Untranslated box tops are `12.0000` (nav h27, from the 51px content box) and `652.484375` (footer
h24, route `/`). Band bottom = boxTop − offset + H; band centre = boxTop − offset + 20.5957 (h27) /
+ 18.3073 (h24).

| law | nav h27, exact | rounds to | footer h24, exact | rounds to |
|---|---|---|---|---|
| **shared baseline** — band bottom on the neighbour's **Hangul ink bottom** | 7.917 / 7.811 / 8.053 / 7.909 (four label×weight combinations) | **8** | 6.281 | **6** |
| shared baseline, *literal* — band bottom on the **alphabetic** baseline (30.031) | 8.969 | 9 | 7.297 | 7 |
| **shared optical line** — band centre on the neighbour's ink centre | 7.375 / 7.398 (보유 종목) · 7.686 / 7.665 (AI 질문) | **7 or 8** | 6.060 | **6** |

**Adopted: the shared baseline, in its Hangul-block reading. Nav `-7 → -8`; footer stays `-6`.**

Three things decided it, and I rendered all three candidates in the live document (`translateY`
overrides at 1280, screenshot at 16×) before adopting one:

1. **The plan's descender premise is false for the neighbouring type (deviation 1).** The plan asked
   me to *confirm* it from the pixel scan, and the scan refutes it: rendered Hangul at 13.5px carries
   **1.05px (400) / 1.16px (600)** of ink below the alphabetic baseline, and **1.02px** at 12px. So
   the literal law paints the band bottom at 30.00 against labels ending at 31.08–31.19 — the mark
   rides **~1.06px high**, visibly, in the 3-up render. For Hangul beside Hangul the shared line the
   eye reads is the **syllable-block bottom**, not the latin baseline. Two independent derivations of
   that reading converge on the same integer: block-bottom-to-block-bottom gives 7.917, and carrying
   the *proportional* descender across the size difference (1.0519/11.7250 of the band's 12.808px =
   1.149 → implied mark baseline 30.851, needing 30.031) gives 7.820. Both → **8**.
2. **The optical-line law cannot decide, and against the operator's own reference it ships the status
   quo.** Because the band (12.81px) is taller than the label ink (11.73–12.32px), the law lands
   anywhere from 7.375 to 7.686 depending on which label you point it at — and against the
   **pure-Hangul** labels it rounds to **7**, i.e. re-derives exactly the placement the operator
   rejected. A law that answers "no change" to a complaint about that change is the wrong law here.
   Its rejected number is **7**. In the footer the two laws agree on 6, so there the choice is moot.
3. **On screen.** At `-7` the wordmark's bottom edge visibly drops below the labels'; at `-8` the
   mark and the labels read as one line; at `-9` the mark rides high. The pixel scan of the three
   candidates is the same story without the adjectives — band bottom 32.00 / 31.00 / 30.00 against
   보유 종목's 31.125.

Result at `-8`, both runtimes, both viewports:

| neighbour | band bottom | its Hangul ink bottom | Δ |
|---|---|---|---|
| `.link` 보유 종목 400 | 31.000 | 31.083 | **−0.083** |
| `.link` 보유 종목 600 | 31.000 | 31.189 | −0.189 |
| `.link` AI 질문 400 / 600 | 31.000 | 30.947 / 31.091 | +0.053 / −0.091 |
| footer `.source` 12px (`-6`, unchanged) | 2124.484 | 2124.203 | +0.281 |
| 390 메뉴 button (pixels) | 31.000 | 30.875 | +0.125 (was **+1.125**) |

One law, two numbers, no viewport branch — and the 390 bar, whose only neighbour is the 메뉴 button,
improves under the same constant rather than needing one of its own.

## 4. §3.5 — the clearance check, which could have blocked

At `-8` the h27 box top lands at **4.00px** below the bar's top edge (was 5.00), on every route, at
both viewports, in both runtimes. That is ≥ 2px, and at 8× the sparkle cluster's ink is nowhere near
the bar's 1px bottom hairline (it occupies the box's **top** 11.9px; the hairline is at y 51–52).
**Not blocking — h27 stands unshrunk**, which is what the plan required and what RESPECT THE DESIGN
requires.

## 5. §3.6 — the check, and proof that it can fail

The shipped check («로고가 옆 글자와 한 줄로 읽힌다»): *on each surface where the mark shares a row
with Hangul type, the mark's glyph-band ink bottom is within **0.5px** of that type's Hangul ink
bottom* — 0.5px being half the integer-px rounding quantum, so the tolerance is exactly what the
rounding rule can leave behind and no more.

| build | 1280 (nav + footer) | 390 |
|---|---|---|
| **pre-change placement `-7`, dev** | **5/5 FAIL**, worst **1.0531** | 5 N/A |
| **pre-change placement `-7`, production** | **5/5 FAIL**, worst **1.0531** | 5 N/A |
| shipped `-8`, dev | 5/5 PASS, worst 0.2814 (the footer) | 5 N/A |
| shipped `-8`, production | 5/5 PASS, worst 0.2814 — **identical to dev** | 5 N/A |

The negative control is the real one: it is the *shipped* R17 placement, re-painted, and the check
reports it as a failure of about the size the operator described. This phase has now shipped four
checks that could not fail; this one can, and its failure mode is the exact defect it exists to catch.

**N/A at 390 is deliberate, not a hole (deviation 3).** At ≤480 the nav's labels are `display: none`
and the footer's `.identity` stacks to a column, so **no Hangul label shares a row with the mark** —
there is nothing for this law to judge. The one candidate neighbour, the 메뉴 button, is the single
place where my two methods disagree (canvas 30.352 vs pixels 30.875 — a mono-family fallback for a
Hangul run), so it is **reported, never judged**: including it would have been a check whose number I
cannot defend. The 390 evidence is the pixel scan in §3, and it moves the right way.

## 6. §3.7 — nothing else moved

Swept in **dev and the production build**, over `/`, `/ask`, `/stocks`, `/portfolio`, `/auth/login`,
at 1280 and 390. Every field below is **identical between the two runtimes**.

- **The binary is untouched.** `git status --porcelain` reports exactly one modified file
  (`Wordmark.tsx`); `git diff -- frontend/public/assets frontend/app` is empty. `juju2-wordmark-white.png`
  is still 1247×371, sha256 `539dce78…`; `juju2-symbol-white.png` `7946b99c…`. The class-C pixel-signature
  proof in `frontend/public/assets/README.md` is untouched and still holds.
- **Nothing horizontal moved.** The nav mark computes **90.75×27** and the footer mark **80.6563×24**
  (Chrome's 80.66) on every route, natural 1247×371, `src="/assets/juju2-wordmark-white.png"`,
  `alt="주주의관제탑"`, `width`/`height` attributes intact.
- **`P10.F2`'s reservation holds.** `[...document.querySelectorAll('header nav a')].map(a => a.getBoundingClientRect().left)`
  is `[218.75, 279.484375, 0, 0, 0]` — identical to the decimal on all five nav routes, and equal to
  the value `P10.F2` and `P10.REVIEW` r3 recorded.
- **The launcher keeps `mask-size: 84% auto`** and reports **0 animations**; the three favicon tiles
  are untouched and re-measured **transparent** with a single ink — `opaque=false`, trim offsets
  `+4+7` (32) and `+23+40` (180), **0** visible pixels that are not `(43,142,108)`, at 84/37/1117
  visible pixels. The 75 % / 84 % divergence is intact; nothing was "made consistent".
- **Both cascade traps are intact.** `.inner:global(.content)` still computes `padding-inline-end`
  **16px @767 · 108px @768 · 108px @1024 · 108px @1255 · 24px @1256** — the scoped rule alive and
  correctly bounded; and `html:root` still resolves `--text-base: 13.5px` / `--text-sm: 12px` /
  `--font-sans: "notoSansKr"…`.
- `document.title` is `주주의관제탑`; the three `link[rel*="icon"]` are 32 / 16 / 180.

## 7. Doc impact (appended to `phase.md`, for `P10.REVIEW` to version)

1. **`frontend.md`** — the wordmark's vertical placement law is now **text-referenced**: the glyph
   band's ink bottom sits on the neighbouring Hangul's ink bottom, `INK_OFFSET_PX = {27: 8, 24: 6}`
   (`translateY(-8px)` / `-6px`), superseding R17's image-derived `0.2628 · H` and **retiring the
   sentences that align to the row** ("band centre 25.60 against the bar's real optical centre of
   25.50: +0.1px" and the footer's "+0.31px … entirely the integer-px rounding"). New measured
   numbers: nav band bottom **31.00** against labels at **30.95–31.19** (Δ ≤ 0.19), box top /
   **top clearance 4.00px**, bottom 31.00; footer unchanged at `-6`, band bottom **0.28px** below
   `.source`'s Hangul bottom; at 390 the band bottom is **0.125px** off the 메뉴 button's (was 1.125);
   render widths 90.75 / 80.66 and the 1247×371 binary unchanged.
2. **`qa.md`** — the regression line **「세로 기하는 움직이지 않았다」** is **falsified** (it asserts
   `{27: 7, 24: 6}`, `translateY(-7px)` and the 25.60 band centre) and must be replaced by a check
   that *can* fail: «로고가 옆 글자와 한 줄로 읽힌다» — on every reader route at **1280**, the mark's
   glyph-band ink bottom is within **0.5px** of the neighbouring Hangul's ink bottom (nav
   `.link`, and the footer `.source`), measured in the live document **and** in an 8× pixel scan of
   band-only columns; at **390** no label shares the bar (labels `display:none`, `.identity` stacks)
   so the line is **N/A there by construction** and the 메뉴 button is reported, not judged. The
   check's teeth: re-painting the mark at R17's `-7` makes it report **5/5 FAIL, worst 1.0531**, in
   dev and in production alike.
3. **`decisions.md`** — the operator **superseded R17's `INK_OFFSET 0.2628 · H` at the P10 round-3
   acceptance gate**, R18 having explicitly re-confirmed it: the mark is no longer aligned to the
   *row's* optical centre but to the **Hangul standing next to it**, on both chrome surfaces (nav
   h27 vs `.link` 13.5px, footer h24 vs `.source` 12px). Of the two laws the operator named, **shared
   baseline was adopted and shared optical line rejected** — the optical line cannot decide (7.38 to
   7.69 depending on the label, because the band is taller than the label ink) and against the
   pure-Hangul labels it re-derives the rejected placement. "Shared baseline" means **Hangul block
   bottom**, not the alphabetic baseline: the rendered type carries 1.02–1.16px of ink below its
   baseline, so the literal reading paints the mark ~1px high. h27/h24, the binary, and everything
   else R17 signed are untouched.

## 8. Findings the next reader needs

- **The bar's own type is not on one line with itself.** `.utility`'s 로그인 is `align-items: center`
  in the full 51px box, while `.link` stretches and reserves a 2px bottom border, so its cell is
  centred in 49px — the account slot's Hangul ink bottom is **31.75** (pixels) / **31.81** (document)
  against the links' **31.125 / 31.083**, i.e. **0.63–0.73px lower**, and its baseline is a full
  **1.00px** lower. Pre-existing since R2/R8 and untouched by R17/R18. Consequence of this slice,
  stated plainly: the mark now sits 0.75px *above* 로그인 where it used to sit 0.25px below it. The
  operator's instruction named the **nav links**, so the links are what I aligned to; bringing the
  account slot onto the links' line is a design decision and is **raised as an operator question in
  `phase.md`**, not taken here.
- **Chrome pixel-snaps the mark's paint origin to whole CSS pixels** when its layout y is fractional
  (footer: laid out at 652.484375, painted at 652). Any future slice comparing `getBoundingClientRect()`
  against a screenshot on the footer must expect up to 0.5px of this, and it is why the footer's
  painted residual is not a constant.
- **A zero-size `inline-block` baseline probe is invalid inside a flex or grid container** — it
  becomes a centred flex item and returns the box's centre, not the baseline. It cost me one wrong
  reading on the 메뉴 button (25.500, suspiciously exactly the box centre) before I caught it; the
  shipped check now wraps such text in a span first and asserts the host's rect is unperturbed.

## 9. Dead ends and things that cost time

- **A clipped screenshot's origin is not the number you passed.** `Page.captureScreenshot` with
  `clip.y = 2100.484375` rasterised from **2101**, which showed up as a phantom 0.48px disagreement
  between the two methods. Also, `clip.scale` **multiplies** `deviceScaleFactor` — my first band scan
  found "no ink" because I searched columns at 8× in a 16× image. Both are why the final method (b)
  uses a full-viewport raster at `deviceScaleFactor: 8` with **no clip at all**.
- **`scrollIntoView` can leave a fractional scroll offset that settles later**, so rects read before a
  wait did not describe the frame that was captured. The harness now snaps the scroll to an integer
  and re-reads the rects **after** the capture to assert they did not move.
- **`header nav a` also matches the mobile sheet's rows** (the sheet is a second `<nav>`), which have
  no `<span>` — the first measurement run threw on it. Filtered by `:scope > span` + `offsetParent`.
  Worth knowing: the F2 `left` array's trailing three zeros are those hidden sheet rows.
- A single luminance threshold cannot compare 100 %-white mark ink with 45 %-opacity footer text; the
  scanner takes a per-band threshold at 50 % of that band's own peak above its own floor.
- Chrome, its throwaway profile, every CDP script and all 60-odd screenshots live in session scratch
  space (`…/scratchpad/`); **nothing entered the repo.** The dev stack was stopped only long enough to
  run `npm run start` on 3010 and was restored (`make web-up`, pid 91834, `make stack-status` green).

## 10. Not done, deliberately

- No `doc-new-version` — doc versions are consolidated once, at `P10.REVIEW` (§7 is what it versions
  from).
- No commit, no status transition — the orchestrator owns both.
- The Python suite was not re-run: the change is one integer in one TSX module with no server
  surface. `npm run typecheck` / `build` / `smoke` and `workflow validate` are the plan's list and all
  four pass.
