# Result — P10.S7 (Apply it all)

- **status:** `done`
- **summary:** Applied R17 and all four operator-directed items in one slice — **all eight blocks
  complete**. Landed the second delivery byte-exact and derived both class-C whites with the
  contract's commands (wordmark guard **0** opaque near-white px, symbol re-trims to
  **222x165+0+0**); shipped nav h27 / footer h24 with the ink offset in the component; fixed the
  launcher covering 의견 보내기; replaced the launcher with the 32px mask-painted sparkle at zero
  animations; shipped the favicon (16/32/180); dropped mono from both `/ops` marks; and adopted
  changple_web's Noto Sans KR + IBM Plex Mono pipeline, retiring 2,057,688 B of Pretendard and the
  Google Fonts CDN for **330,480 B and no third-party origin**. Verified in real Chrome in **dev and
  production** at 1280 and 390 — production matched dev on every measured number. **Found and
  corrected two arithmetic errors in the landed R17 record** (the 84px corner reservation still left
  8px of overlap; the nav's absolute numbers are 0.5px high) and **two cascade traps** that made
  correct-looking CSS do nothing; the record itself was not edited.
- **files_changed:**
  - `frontend/public/assets/juju2-logo-source.png`, `juju2-symbol-source.png` (new, class B, byte-exact)
  - `frontend/public/assets/juju2-wordmark-white.png`, `juju2-symbol-white.png` (new, class C)
  - `frontend/app/icon.png`, `frontend/app/icon1.png`, `frontend/app/apple-icon.png` (new, class C)
  - `frontend/app/fonts.ts` (new) · `frontend/app/fonts/` (new: 4 woff2 + 2 OFL files)
  - `frontend/scripts/gen-korean-charset.mjs`, `subset_noto_sans_kr.sh`, `subset_plex_mono.sh`,
    `korean-charset.txt` (new)
  - `frontend/app/layout.tsx`, `frontend/app/shell.css`
  - `frontend/components/chrome/Wordmark.tsx`, `copy.ts`, `Nav.tsx`, `Footer.tsx`, `Footer.module.css`
  - `frontend/components/ask/AskLauncher.tsx`, `Launcher.module.css`
  - `frontend/components/ops/Ops.module.css`
  - `frontend/public/assets/README.md` (rewritten), `frontend/README.md`
  - **deleted:** `public/assets/juju-logo-source.png`, `juju-wordmark-black.png`,
    `juju-wordmark-white.png`, `public/assets/fonts/PretendardVariable.woff2`,
    `public/foundations/fonts.css`
  - `works/phases/active/P10/phase.md` (rewritten under budget: 192 lines / 16,367 B)
  - `works/phases/active/P10/slices/P10.S7/result.md` (this file)
  - untracked evidence (`var/` is gitignored): `var/p10s7/{dev,prod}/` — **46 screenshots**
- **validation:**
  - `npm run typecheck` — **pass** (`tsc --noEmit`, no output)
  - `npm run build` — **pass**, `✓ Compiled successfully`, 18 static pages, 19 route entries
    including `/icon.png`, `/icon1.png`, `/apple-icon.png`
  - `npm run smoke` — **pass**, `tests 22 / pass 22 / fail 0`
  - `.venv/bin/python -m pytest` — **pass**, `154 passed, 1 warning in 3.26s` (the pre-existing
    starlette/httpx deprecation). Nothing under `src/` changed; run as a guard.
  - `python3 scripts/workflow.py validate` — **pass**, `Workflow validation passed.`, no warnings
  - **real browser, dev** (`make stack-up`, `http://127.0.0.1:3010`, Chrome 152 headless over CDP,
    1280×800@2 and 390×844@3) — **pass**, §3–§7
  - **real browser, production** (`npm run build && npm run start`, same origin, same Chrome) —
    **pass**, and **identical to dev on every measured number**, §8
- **deviations:** four, all recorded below with their measurements — §2. Two are corrections of
  errors *in the landed record* (never edits to it); two are cascade fixes without which the
  contract's own rules were inert.
- **doc_impact:** eight lines appended to `phase.md` — `frontend.md` ×2 (the chrome/launcher/footer
  and the favicon), `architecture.md` (payload 2,057,688 → 330,480 B), `security.md` (no
  third-party origin remains), `operations.md` (the regeneration scripts), `experience.md` (the
  ambient-motion inventory), `decisions.md` (R17 applied + the two record corrections), `qa.md`
  (checklist lines drafted here, §11).

---

## 1. What the record is, and what I did with it

Built from `docs/reference/design/rounds/17-brand-mark-launcher/output/build-prompt.md` alone, with
`result.md` §1b/§5/§7b for the three findings I had to honour and `r17-mark.css` as the geometry
canon. **The record was not edited.** Where I departed from a literal value I say so in §2 and give
the live measurement that forced it.

## 2. Deviations — all four, with the measurement behind each

### 2.1 The footer corner reservation is **108px**, not the contract's 84px (a real error in the record)

R17 §1 gives **two contradicting values** for the same declaration:

- prose: `padding-inline-end: 92px` — *"런처 프레임 68 + 여백 24"*
- code block: `padding-inline-end: 84px` — *"84px = 런처 폭 68 (하한) + 여백 16"*

The second is wrong, and it is wrong in a specific way: it treats **68** (the launcher's width) as
the floor. But the launcher is `right: var(--space-6)`, so from the viewport's right edge it
occupies **24 + 68 = 92px** — which is exactly what the prose's own decomposition says. With
`padding-inline-end: P`, the footer content's right edge is `viewport − P` at `viewport ≤ 1120` and
the launcher's left edge is `viewport − 92`, so **clearance = P − 92**:

| P | clearance | |
|---|---|---|
| 24 (before) | −68px | the defect R17 found |
| **84 (the contract's code block)** | **−8px** | **still overlapping** |
| 92 (the contract's prose) | 0px | flush against the frame |
| **108 (shipped)** | **+16px** | 68 frame + 24 offset + the 16 of air the code block asked for |

Not derived — **measured**, in Chrome, with 84px in place:

```
--- 1120px  pad=84px  ask=none  btn=[970.1,753.6,65.9,20.9]  launcher=[1028,726,68,50]
    overlap x=65.9 y=20.9 | all 5 probe points hit the button: False
--- 1024px  pad=84px  ...  overlap x=65.9 | all 5 probe points hit the button: False
---  768px  pad=84px  ...  overlap x=65.9 | all 5 probe points hit the button: False
```

`1036 (button right) − 1028 (launcher left) = 8`, and because the button is only 65.9px wide the
8px shortfall left **the whole button** under the launcher at every hit-test probe. **The fix, as
written, did not fix the bug** — and it would have shipped looking fixed. With 108px, §7 below.

R17 §5 signs *「푸터 코너 예약 — 넣는다」* as a required item; 108 is the only value that satisfies
what was signed. Catalogued here as an apply-time correction; `build-prompt.md` is untouched.

### 2.2 The contract's absolute nav numbers are 0.5px high (no fix needed)

R17 §1 predicts, for h27 in the nav: box top **5.5px**, glyph band centre **26.10px**, bottom
clearance **19.5px**, against "the bar's 26px optical centre". Rendered, I measure **5.0 / 25.60 /
19.0**.

The cause is the bar's box model: `.bar` is `height: 52px` with `border-bottom: 1px` under a global
`box-sizing: border-box`, so the **content** box `.inner` stretches into is **51px**, not 52.
`(51 − 27) / 2 − 7 = 5.0`. Every number shifts down by exactly 0.5px.

**The relationship R17 specifies holds exactly.** The bar's real optical centre is `51/2 = 25.5`,
and the band centre lands at **25.60** — a **0.1px** error, precisely the 0.1px the contract itself
claimed against its own assumed centre (26.10 vs 26.0). Minimum vertical clearance **5.0px ≥ 4px**.
Nothing to change; recorded so the review does not read a 0.5px difference as drift.

The footer's equivalent: band centre **12.31** against a row optical centre of **12.0** = **+0.31px**,
where R17 claims "within ±0.3px". That 0.31 is entirely the integer rounding the contract itself
mandates (*"정수 px로 반올림"*): the exact offset is `0.2628 × 24 = 6.307px` and it ships as `-6`.
Its own ±0.3 was 0.007px optimistic. Left as signed.

### 2.3 `html:root`, not `:root`, for the font tokens (a cascade trap)

`app/layout.tsx` links `/foundations/tokens.css` from `<head>`, and **React places it after the CSS
Next hoists for the bundle** — verified in the served HTML, dev and production:

```
<link rel="stylesheet" href="/_next/static/chunks/….css" data-precedence="next"/>   x3
<link rel="stylesheet" href="/foundations/tokens.css"/>                              <- last
```

So a bare `:root { --font-sans: … }` in `app/shell.css` ties `tokens.css`'s own `:root` on
specificity (0,1,0) and **loses on source order**, silently leaving the product on a Pretendard that
no longer exists on disk. `html:root` is (0,1,1) and wins regardless of order. Commented in place
with "do not simplify".

### 2.4 `.inner:global(.content)`, not `.inner`, for the corner reservation (the same trap)

`Footer.tsx` puts both classes on one element, and `app/shell.css` gives the global `.content` a
`padding-inline` **shorthand** — which sets the end padding too. `layout.tsx` imports the chrome
before `./shell.css`, so shell wins the (0,1,0) tie. Measured with a bare `.inner`: computed
`padding-inline-end` stayed **24px at every width**. Naming both classes makes it (0,2,0) and states
the real condition.

**Both traps have the same shape and it is worth naming:** a rule that is correct in isolation, that
type-checks, that builds, and that does nothing. Neither is visible in source review; both took a
browser.

## 3. Block 1 — brand binaries

Landed byte-exact (`cp`, verified by sha256 against `~/Downloads/`):

| landed | from | sha256 | format |
|---|---|---|---|
| `juju2-logo-source.png` | `juju2_2.png` | `393361d7…3450` | PNG 1614×1076 sRGBA, 239,858 b |
| `juju2-symbol-source.png` | `favicon_and_chatbot_widget.png` | `1c44ca40…6f3c` | PNG 278×278 sRGBA, 31,674 b |

Both match the contract's stated formats exactly. `-trim` on the wordmark gives
**`1292x371+238+255`** — the contract's number, to the pixel.

Derived with §0's commands verbatim (only the input filenames changed to the landed class-B names,
same bytes):

| derivative | dims | bytes | pixel signature `identify -format '%#'` | sha256 |
|---|---|---|---|---|
| `juju2-wordmark-white.png` | 1292×371 sRGBA | 21,998 | `66d9354b…8e1e` | `749d413f…eba6` |
| `juju2-symbol-white.png` | 222×165 sRGBA | 3,232 | `37577b87…fedb` | `7946b99c…cc7c` |

### Guard 1 — opaque near-white pixels: **0**

The guard cannot be read off the derivative's RGB (the recolor makes every pixel white), so it is
measured on the artwork's own RGB, which is what R17 §1b measured. On the **trimmed adopted source**:

```
opaque(a=255) & min(RGB)>=200  ->  0
opaque(a=255) & min(RGB)>=240  ->  0
opaque(a=255) & min(RGB)>=250  ->  0            (479,332 px, 69,630 fully opaque)
```

**0 at every threshold.** The same run against `~/Downloads/juju2.png` (the first delivery) also
gives 0 — confirming the notebook's re-verification that the operator fixed both copies; the guard
holds regardless of which file was reached for.

A second, independent check on the thing that actually breaks — is the counter a **hole**? Flood-
filling the derivative's transparent region inward from the border leaves **2,845 enclosed pixels in
two islands**:

```
island 1824 px  at (402,226)  50x46     <- 「의」's ㅇ
island 1021 px  at (1014,335)  69x15    <- 「탑」's ㅂ
```

Both counters punched through. The failure mode R17 §1b describes cannot occur.

### Guard 2 — cropped, never trimmed

```
$ magick juju2-symbol-source.png -trim info:-      # the misleading number
  261x216 278x278+0+62
$ magick juju2-symbol-white.png -trim info:-       # after -crop 222x165+39+62
  222x165 222x165+0+0        <- tight, nothing left over
```

The ghosts, accounted for exactly: source ink **2,570** px, ink inside the crop **2,481** px,
fragment `(52,257) 24×21` = **54** px, fragment `(0,265) 24×13` = **35** px. `54 + 35 = 89` and
`2,570 − 2,481 = 89`. R17 §5's "합 89px" reproduces to the pixel.

And the identity claim: the standalone symbol's ink (**2,481**) equals the sparkle's ink inside the
wordmark (`222×165 at (1070,0)` → **2,481**). Same cluster, same scale, not redrawn.

### The recolor changed colour and nothing else

Alpha channels are **byte-identical** between source and derivative in both cases:

```
wordmark  source(trimmed) alpha sha256 == derivative alpha sha256   296508ff…2fbe
symbol    source(cropped) alpha sha256 == derivative alpha sha256   5e6540eb…67fc
```

Wordmark: 154 distinct alpha values, 78,212 non-transparent, 69,630 opaque, and **1 distinct RGB
over the whole raster** — every pixel `#FFFFFF`, transparent ones included, so there is no
near-white bleed exposure on cosmos (the thing that ruled the old black variant out). Symbol: 112
distinct alpha values, 2,481 non-transparent, 1 distinct RGB. Neither is GrayscaleAlpha — both
report `srgba 4.0`, so the `-define png:color-type=6` directive took.

Geometry constants re-measured on the derivative and all matching `r17-mark.css`: glyph band
`1132×176 at (0,195)` ink **75,731** (R17 §1b's exact figure for `juju2_2.png`), gap rows 165–194
ink **0** (exactly 30 empty rows), sparkle `222×165` top-right flush.

**No black variant was created**, and the README now says why rather than leaving the absence
unexplained: nothing referenced the old one, R17 names none, and the symbol — the one mark that
needs recolouring — is painted with `mask` + `currentColor` from a single asset.

The retired trio was deleted **in the same change that repointed the chrome** (`chrome/copy.ts`
`WORDMARK_WHITE` → `/assets/juju2-wordmark-white.png`, `WORDMARK_NATURAL` → `{1292, 371}`), and
recorded in the README with dimensions and sha256 first.

## 4. Blocks 2 and 3 — the wordmark and the footer, measured

`Wordmark.tsx`: prop type `19 | 17` → `27 | 24`; the offset is a module constant
(`{27: 7, 24: 6}`) applied by the component, so no call site can forget it; intrinsic
`width`/`height` → 1292 / 371; still a plain `<img>` (the `next/image` prohibition and its
provenance reason are restated in the file); the "open question for the operator" paragraph is
replaced by what R17 answered.

Rendered at 1280, dev **and** production, byte-identical between them:

| | nav | footer |
|---|---|---|
| src / natural / painted | `/assets/juju2-wordmark-white.png` · 1292×371 · `true` | same |
| box | **94.02 × 27** (R17: 94.02) | **83.58 × 24** (R17: 83.57) |
| transform | `matrix(1,0,0,1,0,-7)` | `matrix(1,0,0,1,0,-6)` |
| glyph band height | **12.81px** (R17: 12.81) | **11.39px** (R17: 11.39) |
| band centre vs host optical centre | 25.60 vs 25.50 → **+0.10px** | 12.31 vs 12.00 → **+0.31px** |
| min vertical clearance | **5.0px** (≥4 required) | — |

`alt` is `BRAND_ALT_KO` unchanged; `document.title` is `주주의관제탑` on all 12 page-views; no
horizontal overflow at either viewport; **h27 at 390 too** — no viewport branch, as R17 requires.
`Nav.module.css` and `Footer.module.css` keep `gap: var(--space-6)` and `.identity`'s
`gap: var(--space-3)` untouched.

### The footer fix, measured at seven widths with real clicks

`.actionAsk` added to the 「AI 질문」 link (class only — structure, content and order unchanged) and
hidden at `min-width: 768px`; the corner reservation on `.inner:global(.content)` at 768–1255.
After the §2.1 correction, in **production**:

| viewport | `padding-inline-end` | 「AI 질문」 | launcher/button overlap | button reachable at all 5 probes | panel opens, fully on screen |
|---|---|---|---|---|---|
| 1280 | 24px | `none` | **0** | ✅ | ✅ |
| 1255 | 108px | `none` | **0** | ✅ | ✅ |
| 1120 | 108px | `none` | **0** | ✅ | ✅ |
| 1024 | 108px | `none` | **0** | ✅ | ✅ |
| 768 | 108px | `none` | **0** | ✅ | ✅ |
| 767 | 16px | `flex` | (no launcher) | ✅ | ✅ |
| 390 | 16px | `flex` | (no launcher) | ✅ | ✅ |

"Reachable" is `document.elementFromPoint` at all four corners **and** the centre of the button,
after scrolling the footer into view — the covered-control test, not a rectangle comparison. "Panel
opens" is a real `click()` followed by finding `[role="dialog"]` and checking it is fully within the
viewport; it was then closed again.

Two things this table settles: **≤767 keeps the link** (the launcher does not render there, so it is
that destination's only footer entry), and the crossover is where R17 says — at 1255 the raw overlap
is `628 − 1255/2 = 0.5px` and at 1280 it is 0, so `max-width: 1255px` is the right bound.

*(In **dev** the 390 centre probe returns `NEXTJS-PORTAL` — Next's dev-only overlay. All four
corners return the button, and production returns the button at all five. Dev-tooling artifact, not
a product defect; noted because it would otherwise read as a failure.)*

## 5. Block 4 — the launcher

`Launcher.module.css` replaced (213 → 194 lines, of which ~40 are the record of what left);
`AskLauncher.tsx`'s four nested mark spans → **one** `<span class="mark"/>`, all three
`data-motion="tick"` hooks gone. Deleted: `.planet` `.band` `.ring` `.ringBehind` `.ringFront`
`@keyframes bandspin` `@keyframes ringdrift` `#dfe9e4` `rgba(95,208,165,.9)` `4.5s` `14s` both
`clip-path`s and the `repeating-linear-gradient`. Every remaining textual occurrence of those names
is inside a comment recording the removal — grep confirms no live declaration.

All six states, measured in production (dev identical):

| state | frame | mark | transform | animations |
|---|---|---|---|---|
| rest | `rgb(14,26,21)` = `#0e1a15`, border `rgba(163,196,180,.32)` | `rgb(234,242,237)` = `#eaf2ed` | none | **[]** |
| hover | `rgb(18,34,25)` = `#122219`, border `rgba(95,208,165,.7)` | `rgb(95,208,165)` = `--live` | `scale(1.35)` | **[]** |
| active | hover kept | `--live` | `scale(1.15)` | **[]** |
| focus-visible | `outline: 2px solid rgb(143,178,232)` = `--focus-ring`/`--r1`, offset **2px** | `--live` | none | **[]** |
| open | unchanged | `opacity: 0`, `.close` `opacity: 1`, bar `rgb(234,242,237)` 16×1.5px ±45° | — | **[]** |
| reduced-motion | transitions `none` | **`--live` on hover — colour preserved** | **none** | **[]** |

The mark is `width/height: 32px`, `background-color: currentColor`,
`mask: url("/assets/juju2-symbol-white.png") no-repeat 50% 50%`, `mask-size: 84% auto` — read back
from the live computed style, and the tail changes with the frame on hover as the table requires.
`:focus-visible` genuinely matches (`el.matches(":focus-visible") === true`), so the outline is the
keyboard's, not the mouse's. The `#eaf2ed` × replaces R6's `#dfe9e4` (R17 §7).

**On "the product now has no ambient motion anywhere".** The launcher's exception is genuinely gone
and the launcher animates not at all. But the product is *not* motion-free: `@keyframes drift`
(80s), `twinkle`, `shoot` in `landing/Cosmos.module.css`, `orbit` (26s) in `Hero.module.css` and
`caretblink` while streaming all remain — R2's cosmos backdrop, separately signed, and not what R6's
note was about. The precise claim is **"R6's brand-launcher motion exception expired"**. Recorded in
`phase.md` § Decisions as a record nit, not edited in the record.

## 6. Blocks 5 and 6 — the favicon and the `/ops` mark

Three tiles, all composited from `juju2-symbol-white.png` onto an opaque `#0a1310` square:

| file | tile | ink measured | ink/box | opacity |
|---|---|---|---|---|
| `app/icon.png` | 32×32 | 27×20 at +2+6 | **84.4%** | no alpha channel at all (`srgb 3.0`) |
| `app/icon1.png` | 16×16 | downscale of the 32 raster | — | same |
| `app/apple-icon.png` | 180×180 | 151×112 at +14+34 | **83.9%** | same |

`32 × 0.84 = 26.88` wide and `26.88 × 165/222 = 19.98` tall — R17's stated "잉크 26.9 × 20.0",
reproduced. Centring verified by pixel enumeration, not by trusting `-gravity`.

**One judgement inside 16px, disclosed.** The contract says only that 16 is a downscale of the 32
raster and names no filter. ImageMagick's default (Lanczos) rings: **36 pixels darker than the
tile** — a colour the design never specified — and dims the ink (brightest 214). At exactly 2:1
`-filter Box` is a plain 2×2 mean, i.e. the literal reduction: **0 ringing** (the 4 pixels that
differ are `(9,18,15)` vs `(10,19,16)`, a 1/255 rounding artifact), brightest **232**, and the ink
box lands at exactly half the 32's geometry. Box shipped; the choice and its numbers are in the
README.

Both R17 bounds honoured: the single-star crop is **not** adopted, and the 16px softness (five dots
at ~1.4px each) is recorded as a limitation, not fixed by inventing a second variant.

Shipped through Next `app/` file conventions, so no hand-written `<link>` exists. Served, **dev and
production**, read back from the live DOM:

```
<link rel="icon"            href="/icon.png?icon.2a95k8aqy9h_w.png"        sizes="32x32"   type="image/png">
<link rel="icon"            href="/icon1.png?icon1.22riy1yb6nph3.png"      sizes="16x16"   type="image/png">
<link rel="apple-touch-icon" href="/apple-icon.png?apple-icon.3he1bmret33eb.png" sizes="180x180" type="image/png">
```

`P10.S5` proved the absence by inspecting the served HTML; this is the same check with the opposite
result. `layout.tsx`'s metadata comment, which explained why there was *no* favicon, is replaced.

**`/ops`:** `--font-mono` and `letter-spacing: 0.08em` dropped from `.mark` **and** `.doorMark`;
`OPS_MARK` unchanged. Verified on the **door** and — after restarting the API with throwaway
`MIJUAL_OPS_ID`/`MIJUAL_OPS_PASSWORD`, then restoring it — on the **bar**:

| | family | weight | letter-spacing | glyphs painted by | box |
|---|---|---|---|---|---|
| `.mark` (bar), 1280 | `notoSansKr, …` | 600 | **normal** | **9 / 9**, one custom face | 91.69 × 18.59 |
| `.doorMark`, 1280 | `notoSansKr, …` | 600 | **normal** | **9 / 9**, one custom face | 330 × 18.6 |

Nine of nine, where before the mono covered **one glyph of nine — the space** — and left the other
eight to whatever Korean face the OS had. The 2.84× fake double space is gone with the tracking. The
weight survives the operator's answer and the *family* underneath it changed, which is block 7's
intended consequence.

At 390 the bar mark still measures **11.05 × 148.75** (was 11.34 × 148.75): the typography change
did not touch the 390 stacking, which confirms the already-deferred defect is a **layout** problem,
not a typographic one.

## 7. Block 7 — the Korean font pipeline, and the one deliberate adaptation

Read `~/projects/personal/changple_web` rather than reinventing: `src/app/fonts.ts`,
`scripts/subset_noto_sans_kr.sh`, `scripts/gen-korean-charset.mjs`, `scripts/subset_plex_mono.sh`,
`src/app/fonts/`, and the `noto` assertion in `tests/browser/smoke.spec.ts`. Adopted whole: the
face, `next/font/local`, `display:"swap"`, `preload:true` for Korean / `false` for mono, CSS
variables, the OS fallback stacks, the auto-generated charset, the pinned google/fonts SHA
(`4efc2774c63917927efe769ca845def6bd6debae` — theirs, deliberately, for reproducibility), and both
OFL files beside the fonts. Both of their load-bearing constraints are carried and re-documented:
the charset is **auto-extracted** (a hand-kept one goes stale and renders 자모 분리) and the subset
**omits U+1100–11FF** so an unknown syllable falls back *composed*.

**Two adaptations to Mijual's layout:** the charset generator scans `app/`, `components/`, `lib/`
(509 unique Korean chars from 142 files) rather than `src/`; and the mono ships **three** weights
(400/500/600) rather than their two, because the retired CDN request asked for `wght@400;500;600`
and taking two would silently drop a weight R1 signed.

### The coverage decision, measured

| option | subset | payload | verdict |
|---|---|---|---|
| (a) auto-extracted app glyphs alone (509) | changple_web's own policy | **94,604 B** | **fails the requirement** — every dynamic company name falls back to the OS face |
| **(b) + KS X 1001 wansung set (2,350)** | **adopted** | **291,072 B** | smallest that works |
| (c) + the full 11,172-syllable block | | **1,022,828 B** | covers by construction |

Against today's `PretendardVariable.woff2` at **2,057,688 B**: (a) 21.7×, **(b) 7.1×**, (c) 2.0×.

**Why (b) is the smallest that works, measured rather than assumed.** I queried the live corpus for
every Korean syllable in every stored text column — company names, agent answers, extraction values
and summaries, quoted DART filing text:

```
distinct Hangul syllables across ALL stored text: 654
  of those, OUTSIDE KS X 1001: 1  ->  쳥
    corp.corp_name              360 syllables,   0 outside KS X 1001
    conversation_turn.answer    263 syllables,   0 outside KS X 1001
    extraction.quote            339 syllables,   0 outside KS X 1001
    snapshot.payload_json       588 syllables,   1 outside KS X 1001
```

The single miss is a **typo inside a real filing** — `"본 건 합병에 따른 쳥약의 권유자가…"`, 쳥 for
청. A repo-wide sweep of 1,933 files (all product Korean, prompts, docs) finds no other real miss.
All **360** company-name syllables are covered, and I verified it again against the built subset's
cmap: 2,733 codepoints, **0 missing** from either the app charset or the corpus company names, and
**no conjoining jamo present**.

I also checked whether the weight axis was a cheaper lever than glyph coverage. It is not:
instancing `wght` down to 400–700 gives **1,053,156 B** for option (c) against 1,022,828 B — very
slightly *larger*, because the instancer bakes deltas. So the full `wght 100 900` axis is free and
is kept, exactly as changple_web has it.

**Flipping to (c) costs one variable** (`HANGUL_COVERAGE=full`), and the operator question is filed
in `phase.md` so the review routes it.

### Retirements, and what ships instead

Deleted with their sha256 recorded in the README: `public/foundations/fonts.css` (886 B,
`bf897fb8…4436`, the class-A R1 export marked *"do not edit"*) and
`public/assets/fonts/PretendardVariable.woff2` (**2,057,688 B**, `9599f12f…d900b4`). The
hand-written `<link>` to the Plex Mono CDN went with them — it existed only because the landed
`fonts.css` put its `@import` after an `@font-face`, where CSS drops it, so the workaround has
nothing left to work around.

| ships | bytes |
|---|---|
| `app/fonts/NotoSansKR.subset.woff2` | 291,072 |
| `app/fonts/IBMPlexMono-{Regular,Medium,SemiBold}.subset.woff2` | 12,712 + 13,012 + 13,684 |
| **total** | **330,480** |

**`public/foundations/tokens.css` was not touched** (frozen, R8 byte-verbatim, R17 `Token delta:
None`). `--font-sans` / `--font-mono` are overridden in `app/shell.css` — application code — at
`html:root` for the reason in §2.3.

### Verified in the browser, not asserted

```
document.fonts:  notoSansKr (100 900) loaded · plexMono 400 loaded · plexMono 600 loaded
                 plexMono 500 unloaded (present, simply not needed by these routes)
                 NO Pretendard face of any kind
```

`CSS.getPlatformFontsForNode` — which font Blink **actually painted with**:

| node | painted by |
|---|---|
| a real DART company name on the board (`HLB제약`) | `OTS derived font` / `OTS-derived-font_SemiBold`, `isCustomFont: true`, **5 / 5 glyphs** |
| a nav link | `OTS-derived-font_Regular`, `isCustomFont: true`, 5 / 5 |
| the `/ops` mark | `OTS-derived-font_SemiBold`, `isCustomFont: true`, 9 / 9 |

**The company name and the UI around it are painted by the same shipped face** — which is the entire
point of the adaptation, and it is checked on real DART data, not a fixture.

Network, across 5 routes in each runtime:

```
total requests 125 (dev) / 139 (prod)
thirdParty:  []          <- zero, both runtimes
googleFonts: []          <- no fonts.googleapis.com, no fonts.gstatic.com
fontRequests: NotoSansKR_subset-s.p.….woff2
              IBMPlexMono_Regular_subset-s.….woff2
              IBMPlexMono_SemiBold_subset-s.….woff2       (all same-origin)
```

The preload is present in production, and it took a moment to find: Next 16 does not put a static
`<link rel="preload" as="font">` in the HTML string — it emits an RSC resource hint
(`:HL["/_next/static/media/NotoSansKR_subset-s.p.….woff2","font",{"crossOrigin":"","type":"font/woff2"}]`)
that React materialises into the DOM. Read back from the live production DOM:

```
link[rel=preload][as=font]  ->  1 entry: NotoSansKR_subset-s.p.….woff2, font/woff2, crossorigin=anonymous
```

Exactly one — the Korean face. Neither mono file is preloaded, which is the `preload: false` split
working.

## 8. Production vs dev

`npm run build && npm run start` on the same origin, same Chrome, same scripts. **Every measured
number was identical**: nav 94.02×27 / band 25.60, footer 83.58×24 / band 12.31, the whole footer
table at seven widths, all six launcher states, the three icon links, the font stack and the painted
faces. The two differences are both dev-only artifacts and neither is a product difference: the
`NEXTJS-PORTAL` overlay at the 390 centre probe (§4), and the font preload appearing only in the
production render path.

12 page-views (6 routes × 2 viewports) in each runtime, plus `/ops` door and bar, plus the footer at
7 widths and the launcher's states — **46 screenshots** under `var/p10s7/{dev,prod}/`.

## 9. Runtime notes for whoever runs this next

`make stack-up` **works now** — commit `c8606d0` moved the stack to 3010 / 8010 / 5434, so the 5433
collision with `changple_web_dev_postgres` that `P10.S5` documented is gone and the `!override`
compose fragment is no longer needed. **The plan's `http://127.0.0.1:3000` is stale; the manifest's
`http://127.0.0.1:3010` is right** and is what I used. `changple_web_dev_postgres` was never
touched. The stack was left exactly as found (API without ops credentials, dev web on 3010).

## 10. Nits catalogued against the landed record — not edited

1. `build-prompt.md` §1 states `92px` in prose and `84px` in its code block for the same
   declaration, and §5 points at an "추가②" `.actionAsk` block that §1 never actually writes out
   (the rule is only in `result.md` §7b ②). Both reconstructable; both cost a measurement.
2. §1's render-check block computes from a 52px content box; the bar is 52px **border-box** (§2.2).
3. `result.md` §7b ①'s `calc` form carries the same 84px error as the media-query form.
4. §3's "213줄 → 약 90줄" — the replacement is 194 lines here, but ~104 of those are the comment
   block recording what was deleted and why. The CSS itself is ~90.
5. Three doc comments now name a retired typeface — `chrome/Footer.tsx:23`, `chrome/copy.ts:181`,
   `chrome/Footer.module.css:31` all say the footer type is "Pretendard". Left for the **existing
   deferred comment-sweep job** (`phase.md` § Decisions names it), scope not widened.

## 11. Regression Checklist lines, drafted for `P10.REVIEW` to append

```
- [ ] chrome: the 주주의관제탑 wordmark paints in nav and footer at h27 / h24 with its glyph band on the bar's optical centre — `/assets/juju2-wordmark-white.png`, natural 1292x371, at 1280 and 390 (P10)
- [ ] document: a real `link[rel*=icon]` is served — 32 / 16 / apple-touch 180 — and the tile is opaque, in dev and in the production build (P10)
- [ ] ask launcher: the 32px sparkle renders at rest, turns `--live` and scales on hover, and has **zero** animations in every state; the colour change survives `prefers-reduced-motion` (P10)
- [ ] footer: 의견 보내기 is clickable and its 380px panel opens at 1280 / 1120 / 1024 / 768 — the launcher never covers it — and the desktop 「AI 질문」 link is hidden while the ≤767 one remains (P10)
- [ ] type: every page renders Korean in the self-hosted Noto Sans KR subset, a woff2 is preloaded, **no request reaches fonts.googleapis.com or fonts.gstatic.com**, and a DART company name paints in the same face as the UI beside it (P10)
```
