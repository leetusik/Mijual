# Result — P10.F1 · R18 ①③ 워드마크와 파비콘, 그리고 두 README

- **status:** `done`
- **summary:** Applied R18 §①③ and §④ in one change. Re-derived
  `juju2-wordmark-white.png` to **1247×371** with the splice command — 45 dead columns cut from
  inside a 70-column full-height transparent band — with **all three ink statistics unchanged**
  (78,212 / 69,630 / 154) and the alpha proved to be a pure splice of the source's; re-derived the
  three favicon tiles as **transparent** tiles with a single `#2b8e6c` ink at **75 %**; rewrote the
  seven `public/assets/README.md` sections, `layout.tsx`'s two now-false comment facts, `copy.ts`'s
  `WORDMARK_NATURAL`, `Wordmark.tsx`'s comment numbers and `frontend/README.md:60`. Verified in real
  Chrome 152 over CDP in **dev and the production build** at **1280 and 390** — production matched
  dev on every measured number. **`INK_OFFSET_PX`, both `translateY` values and the launcher's
  `mask-size: 84%` were not touched.** Found **three broken verification procedures in R18** (not
  prescriptions — every prescription reproduced exactly) and replaced all three with checks that
  work; the design record was not edited.
- **files_changed:**
  - `frontend/public/assets/juju2-wordmark-white.png` (re-derived, 1292×371 → **1247×371**)
  - `frontend/app/icon.png`, `frontend/app/icon1.png`, `frontend/app/apple-icon.png` (re-derived,
    opaque → **transparent**)
  - `frontend/components/chrome/copy.ts` (`WORDMARK_NATURAL` → 1247 + a comment)
  - `frontend/components/chrome/Wordmark.tsx` (**doc comment numbers only**)
  - `frontend/app/layout.tsx` (**comment only** — no `icons` key added)
  - `frontend/public/assets/README.md` (seven sections)
  - `frontend/README.md` (the favicon line, `:60`)
  - `works/phases/active/P10/phase.md` (edited under budget: 188 lines / **16,381 B**)
  - `works/phases/active/P10/slices/P10.F1/result.md` (this file)
  - untracked evidence (`var/` is gitignored): `var/p10f1/{dev,prod}/` — **35 screenshots**
- **validation:**
  - `npm run typecheck` — **pass** (`tsc --noEmit`, no output)
  - `npm run build` — **pass**, 18 static pages, 19 route entries including `/icon.png`,
    `/icon1.png`, `/apple-icon.png`
  - `npm run smoke` — **pass**, `tests 22 / pass 22 / fail 0`
  - `python3 scripts/workflow.py validate` — **pass**, no warnings (the `phase.md` budget warning
    that appeared mid-edit is gone)
  - R18 §① verification table — **every row re-measured after writing**, §2 below
  - R18 §③ tile verification — **re-measured**, §3 below
  - real Chrome 152.0.7977.65 over CDP, **dev and production**, 1280 and 390 — §5 below
- **deviations:** four, all recorded in §6. Three are R18 *verification procedures* that cannot
  work as written (the "opaque near-white = 0" guard, the aspect/render-width arithmetic, the
  `%[fx:int(255*u.r)]` ink-colour check); one is that the **OS tab strip could not be
  photographed** — no Screen Recording permission for this process — so the tab check was done by
  re-fetching the served bytes and having Chrome paint them at 16 CSS px on four tab colours.
- **doc_impact:** one entry appended to `phase.md` `## Doc impact` covering `frontend.md`, `qa.md`
  and `decisions.md`. **No `doc-new-version` run** — that is `P10.REVIEW`'s.

---

Instrument: **Aside is not installed on this machine** (`aside` is not on `PATH`, no app bundle),
so per the doctrine's own fallback I drove **real Chrome 152.0.7977.65 over CDP**, in the runtime
and access path `docs/current/operations.md` `## Operator Runtime` names — `make stack-up`, dev at
`http://127.0.0.1:3010`, and the production build (`npm run build && npm run start`) on the same
origin — at 1280 and at a true 390. This is the same instrument `P10.S7` and `P10.REVIEW` used.
Every number below is read out of a live document or measured with ImageMagick 7.1.2-27, not
copied from the record.

---

## 1. The wordmark re-derivation (§①)

Run from `frontend/public/assets/`, R18 §①'s command **verbatim** — the `-channel RGB … +channel`
guard and `-define png:color-type=6` both kept (R17 traps 3 and 4):

```sh
magick juju2-logo-source.png -trim +repage \
       -channel RGB +level-colors white,white +channel \
       \( -clone 0 -crop 530x371+0+0 +repage \) \
       \( -clone 0 -crop 717x371+575+0 +repage \) \
       -delete 0 +append +repage \
       -define png:color-type=6 juju2-wordmark-white.png
```

`530 + 717 = 1247`, `575 = 530 + 45`.

## 2. §①'s verification table, re-measured **after** writing

| check | expected | measured | |
|---|---|---|---|
| box | 1247×371 srgba 8 | `1247x371 srgba 4.0 8`, `opaque=False` | ✅ |
| non-transparent px | 78,212 (unchanged) | **78,212** | ✅ |
| fully opaque px | 69,630 (unchanged) | **69,630** | ✅ |
| distinct alpha values | 154 (unchanged) | **154** | ✅ |
| 의\|관 ink gap | 25px, `x=519..543` | ink at `x=518` (α 175) → **`519..543` all α 0** → ink at `x=544` (α 152) | ✅ |
| sparkle | 222×165 at `x=1025` | `222x165+1025+0`, `1025+222=1247` | ✅ |
| glyph band | 1087×176 at `y=195`, 75,731 ink px | `1087x176`, crop offset 190 + 5 = **195**, **75,731** | ✅ |
| empty band | 30 rows, `y=165..194` | full-height zero-alpha row run **`(165,194,30)`** | ✅ |
| every pixel `#FFFFFF` | 1 distinct RGB | **1** — `srgb(255,255,255)` | ✅ |

**The two counter islands, before and after** — this is what replaces R18's broken "opaque
near-white = 0" row (see §6.1). Both were measured on the shipped file before the change and on the
shipped file after it:

| island | before (`1292×371`) | after (`1247×371`) | |
|---|---|---|---|
| `50×46 at (402,226)` — 「의」's ㅇ | **481** | `+402+226` → **481** | ✅ |
| `69×15` — 「탑」's ㅂ | `(1014,335)` → **15** | `(969,335)` → **15** | ✅ (moved −45, as R18 said) |

**Alpha splice hash** — the stronger guarantee, and the reason the three ink statistics *cannot*
have moved:

```
source trim, same two crops, +append, alpha : d90e982748259b5356373cb82b5fb9fc20678947eb6df1994554b56ae895df79
shipped derivative, alpha                   : d90e982748259b5356373cb82b5fb9fc20678947eb6df1994554b56ae895df79
```

**Independent confirmation that the cut was safe.** On the *pre-change* raster the full-height
zero-alpha column runs are
`[(164,182,19), (347,369,23), (486,493,8), (519,588,70), (757,775,19), (895,907,13), (932,970,39), (1137,1141,5), (1172,1201,30)]`
— `x=519..588` is the **70-column band**, and the command removes `x=530..574` from strictly inside
it (11 columns of clearance left, 14 right).

**A counting caveat worth recording.** `'%[fx:int(w*h*mean)]'` truncates: over the whole 1247×371
raster it returns **78,211**, one short, because the mean is a double. `'%[fx:int(w*h*mean+0.5)]'`
returns **78,212**, and a raw-byte scan of the RGBA stream agrees. The README now uses the rounded
form. (This is why the first measurement in this slice looked like an off-by-one and was not.)

## 3. The three favicon tiles (§③)

R18 §③'s three commands **verbatim**, run from `frontend/` — `-alpha off` absent,
`png:color-type=6` (not 2), recolour **before** resize.

| check | expected | measured | |
|---|---|---|---|
| `app/icon.png` | 32×32 srgba, `opaque=false` | `32x32 srgba 4.0 opaque=False` | ✅ |
| `app/icon1.png` | 16×16 srgba, `opaque=false` | `16x16 srgba 4.0 opaque=False` | ✅ |
| `app/apple-icon.png` | 180×180 srgba, `opaque=false` | `180x180 srgba 4.0 opaque=False` | ✅ |
| icon ink trim | `24x18+4+7` | **`24x18+4+7`** | ✅ |
| apple ink trim | `134x100+23+40` | **`134x100+23+40`** | ✅ |
| ink RGB | `43,142,108` | **every** non-transparent pixel is exactly `(43,142,108)` in all three tiles; zero pixels of any other colour | ✅ (by a different command — §6.3) |

`icon1.png` trims to `12x10+2+3`. R18's parenthetical guessed `12×9 at +2+3.5`; a Box downscale of
an 18-tall ink starting at the odd row 7 lands on 10 rows. The signed checklist only names the 32
and 180 trims, both of which match, so this is a note, not a miss.

**Margins.** 32: `(32−24)/2 = 4` each side, `(32−18)/2 = 7` top and bottom. 180: `(180−134)/2 = 23`,
`(180−100)/2 = 40`. Integer, no rounding bias. The left sparkle's breathing room goes **2px → 4px**
at 32 and **14px → 23px** at 180.

**Contrast, recomputed independently** (WCAG relative luminance, `#2b8e6c` → L = 0.20942): white
**4.047**, `#f1f3f4` **3.636**, `#202124` **3.978**, `#0a1310` **4.659**, black **5.188** — R18's
4.05 / 3.64 / 3.98 / 4.66 / 5.19 to the digit.

## 4. Hashes, signatures and byte counts — all measured from the re-derived files

Nothing here is estimated; every value is the output of `shasum -a 256`,
`identify -format '%#'` and `stat -f %z` on the shipped file.

| file | sha256 | pixel signature | bytes |
|---|---|---|---|
| `juju2-wordmark-white.png` | `539dce78…8fd2` | `bc1bfd6c…a891` | **21,920** (was 21,998) |
| `app/icon.png` | `f12828c3…2e06` | `07aa766b…9794` | **684** (was 937) |
| `app/icon1.png` | `54ff6da3…92d2` | `c57c675a…6166` | **476** (was 561) |
| `app/apple-icon.png` | `72fc30fb…e418` | `9d8c0e00…2962` | **2,799** (was 4,353) |

Unchanged, and left as `P10.S7` recorded them: `juju2-logo-source.png` `393361d7…`,
`juju2-symbol-source.png` `1c44ca40…`, `juju2-symbol-white.png` `7946b99c…` / `37577b87…`. The
tiles shrank because a transparent PNG stores no background.

**Regenerability re-proved.** All four derivatives were re-run into a scratch directory from the
recorded commands and compared against the shipped files: **pixel signature identical and
`compare -metric AE` = 0** on every one.

## 5. The runtime — dev and production, 1280 and 390

Six routes (landing, `/ask`, `/portfolio`, `/stocks`, `/auth`, `/ops`) × two viewports × two
runtimes. **Production matched dev on every number below**, so one table serves both.

| | measured |
|---|---|
| `src` | `/assets/juju2-wordmark-white.png` |
| natural / attributes | **1247×371** / `width=1247 height=371`, `complete && naturalWidth>0` |
| nav mark rect | **90.75 × 27** at `left=104` (1280) / `left=16` (390) |
| footer mark rect | **80.66 × 24** |
| transform | `matrix(1, 0, 0, 1, 0, -7)` nav, `-6` footer — **unchanged** |
| bar | 52px border-box, 51px content |
| glyph-band centre in the bar | **25.60** — identical to `P10.REVIEW`'s pre-change **25.596 ≈ 25.60**, against the real optical centre 25.5 |
| favicon links | `link[rel=icon][sizes=32x32]`, `[sizes=16x16]`, `link[rel=apple-touch-icon][sizes=180x180]` on **all 12 page-views** |
| document title | `주주의관제탑`, and `주주의관제탑 운영` on `/ops` |

**The mark reads joined.** `var/p10f1/prod/mark-nav-zoom.png` is the nav at 300 %: 주주의관제탑,
no space. `var/p10f1/before-after-wordmark-zoom.png` puts the retired raster above the new one at
the same height — the top line reads 「주주의 관제탑」, the bottom 「주주의관제탑」, sparkle cluster
intact in both.

**The vertical position did not move**, which was the thing to prove after leaving `INK_OFFSET_PX`
alone: 25.60 then, 25.60 now.

**의견 보내기 still opens.** Footer button, hit-tested at its own centre and then clicked:
- production **1280** — `hitIsSelf: true`, `aria-expanded false → true`, panel visible, 1 textarea;
- production **390** — same, `hitIsSelf: true`, panel opens;
- dev **1280** — same;
- dev **390** — the hit test returns `NEXTJS-PORTAL`, the Next dev-tools indicator, which sits over
  that corner in `next dev` only. **Not the launcher** — the full `elementsFromPoint` stack is
  `NEXTJS-PORTAL → BUTTON.Footer…action → SPAN.Feedback…anchor → …`, i.e. the button is directly
  under it, and in production (no portal) the click lands. Recorded, not fixed: it is a dev-tools
  artifact, not product behaviour.

**Favicon — the tag count is not the check.** The three hashed URLs the DOM actually names were
re-fetched from the running server and their `sha256` compared against the files on disk: **all
four match in production** (three tiles + the wordmark). Then Chrome painted each tile at the tab
strip's **16 CSS px** on four backgrounds:

| tile | white tab | `#f1f3f4` | `#202124` | `#0a1310` |
|---|---|---|---|---|
| `icon.png` @16 | 37 px differ, peak CR **2.94** | 37, **2.71** | 34, **3.02** | 34, **3.38** |
| `icon1.png` @16 | 37 px differ, **2.94** | 37, **2.71** | 37, **3.02** | 37, **3.38** |
| `apple-icon.png` @32 | 78 px differ, **3.98** | 78, **3.58** | 73, **3.93** | 73, **4.54** |

It reads on all four — `var/p10f1/dev/favicon-on-tab-colours.png` shows the cluster clearly green
on white, on Chrome light, on Chrome dark and on cosmos. The peak per-pixel contrast is *below* the
flat colour's 4.05/3.98 because a 16px downscale of a five-dot cluster leaves almost no fully
opaque pixel (**1 of 84** in `icon.png`, **0 of 37** in `icon1.png`). That is the same recorded
limitation as R18's "1.2px dots", seen from the contrast side; it is written into the README and
routed to the gate (§6.4), not silently fixed.

**Nav regression baseline for `P10.F2`** (1280, production; dev identical):

| | `/ask` | `/portfolio` |
|---|---|---|
| first link `AI 질문` `left` | **218.75** | **218.75** |
| `AI 질문` width / weight | 40.73 / **600** (active) | 40.03 / 400 |
| `보유 종목` `left` | **279.48** | **278.78** |

The R18 §② shove is **0.70px** on `보유 종목`, present and unchanged — correct for this slice, and
the number `P10.F2` has to drive to zero. The first link's `left` is identical on both routes, so
the mark's 3.28px narrowing neither caused nor masked it. At 390 the bar links are hidden and the
**메뉴** button is 44×44 at `left=330`, with the brand mark at `left=16` — brand + menu button both
present, as §⑤.6 asks.

## 6. Deviations from `plan.md`

### 6.1 R18's "opaque near-white = 0" row — not copied (this was in the plan)

`plan.md` and `VERIFICATION.md` §2 both directed this, and it is confirmed: over the whole white
derivative the expression returns **69,630**, the opaque count itself, and can never be 0. The
README now carries the two counter islands and the alpha-splice hash in its place, with an explicit
"do not replace this with…" paragraph so the broken form does not come back.

### 6.2 R18's aspect and render widths are arithmetically wrong — measured values used instead

R18 §① signs **3.3603 : 1**, nav **90.7px**, footer **80.6px**. But `1247 / 371 = 3.361186`, so
`× 27 = 90.752` and `× 24 = 80.668`. All three of the round's figures follow from one slip in the
aspect (the pre-change 3.4825 was computed correctly, and `3.4825 − 45/371` = 3.3612 as well).

I did not settle this by arithmetic alone. **Chrome reports `getBoundingClientRect()` of exactly
`90.75 × 27` in the nav and `80.66 × 24` in the footer**, in dev and in the production build, at
both viewports — so **90.75 / 80.67** is what the README and `Wordmark.tsx` now say. The design
record is **not** edited; the correction is recorded here, in `phase.md` `## Decisions`, and in a
parenthetical in the README, which is exactly how `P10.S7` handled R17's two arithmetic errors.

### 6.3 R18 §③'s ink-colour check reads the wrong pixel

`magick app/icon.png -depth 8 -format '%[fx:int(255*u.r)],…' info:` is signed as printing
`43,142,108`. `u.r` with no coordinate is **pixel (0,0)**, which on all three tiles is now
transparent canvas — it prints `0,0,0`, and `-trim +repage` first does not help (the ink box's own
top-left pixel is transparent too, because ImageMagick premultiplies during `-resize`).

The check itself is worth keeping, so the README carries a form that works: count non-transparent
pixels whose RGB is not `(43,142,108)`. **It is 0 in all three tiles** — i.e. every visible pixel
is exactly `#2b8e6c` and there is no edge bleed, which is the property trap 3 exists to protect.

### 6.4 The OS tab strip could not be photographed

`plan.md` asks for the favicon to be confirmed "탭에서 실제로 보이는지 — 밝은 탭과 어두운 탭
양쪽에서". `screencapture` fails with `could not create image from display` — this process has no
Screen Recording permission, and CDP's `Page.captureScreenshot` captures page content only, never
the browser chrome. I did **not** photograph a tab and do not claim to have.

What I did instead is in §5: the served bytes were proved identical to the shipped files in both
runtimes, and the same Chrome rasterized each tile at the tab strip's 16 CSS px on white, Chrome
light, Chrome dark and cosmos, with the ink measurably and visibly present on all four. The
remaining gap — what the tile looks like inside the operator's own tab strip — is routed into
`phase.md` `## Now` as a gate item, since the operator opens their own browser there anyway.

## 7. What was deliberately not touched

`INK_OFFSET_PX` and both `translateY` values (`Wordmark.tsx` line 67 and 80 — comment lines only in
the diff) · `Launcher.module.css`'s `mask-size: 84% auto` · `public/foundations/tokens.css` ·
everything under `Nav.*` (that is `P10.F2`) · `docs/current/*.md` · `docs/reference/design/rounds/**`
· `.env`. `app/layout.tsx` still has **no `icons` key** — the Next `app/` file convention stands and
only the comment changed. **Token diff: 0. New or deleted copy: 0.**

`git diff --name-only` is the proof: nine product files, all of them named in `plan.md`.

## 8. Notes and dead ends

- **The first island/statistic reading looked like an off-by-one and was not** — see §2's counting
  caveat. Worth an entry because the natural next move (assuming the splice had eaten a pixel) would
  have been to doubt a correct derivation.
- **`-trim +repage` hides the offsets.** `plan.md` warned about this but stated that R18's §③
  command omits `+repage`; it does not — the signed command is
  `magick app/icon.png -trim +repage -format '%wx%h%O' info: # 24x18+4+7`, which can only ever print
  `+0+0`. Dropping `+repage` gives the signed `24x18+4+7`. Same class of error as §6.1–6.3, but the
  plan already anticipated the fix, so it is a note rather than a deviation.
- **The dev/production swap was reversed cleanly.** The dev web process was stopped, `npm run start`
  served the production build on the same origin for the production sweep, then `make stack-up`
  brought `next dev` back; `stack-status` shows postgres + api + web running on 3010 / 8010 / 5434,
  and a post-restore probe reproduces the dev numbers exactly. Chrome, its throwaway profile and
  every CDP script live in session scratch space; nothing was added to the repo.
- **Evidence:** `var/p10f1/dev/` and `var/p10f1/prod/` — 35 PNGs (12 page-views per runtime plus
  the feedback panels, the nav crops, the favicon strip and the before/after wordmark). `var/` is
  gitignored, so none of it is committed.
