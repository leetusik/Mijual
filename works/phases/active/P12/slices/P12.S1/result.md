# P12.S1 — result

```yaml
status: done
summary: >
  The account frame's caret is now one glyph in both states — ▾, flipped by a layout-neutral
  transform when the menu is open — so the frame is pixel-equal across the toggle (261.28px wide,
  left 914.72, height 32, one distinct value over 15 readings) in dev at 1280 and in the local
  production build, where the +5.38px jump used to be. The flip pivots on the glyph's own ink
  centre (transform-origin: 50% 66.7%), which is what keeps the caret's ink in place (+0.5px)
  instead of the −3.5px it jumps with the default box-centre pivot.
files_changed:
  - frontend/components/chrome/AccountSlot.tsx
  - frontend/components/chrome/AccountSlot.module.css
  - works/phases/active/P12/phase.md
  - works/phases/active/P12/slices/P12.S1/result.md
validation:
  - cmd: cd frontend && npm run typecheck
    result: pass (re-run on the final tree)
  - cmd: cd frontend && npm run smoke
    result: pass — 22/22
  - cmd: "Aside repl --account u2 — dev 1280, /portfolio, 15 readings over 7 opens / 7 closes (click, Escape, outside-click, Enter, hover)"
    result: "pass — frame width 261.28 / left 914.72 / top 9.5 / height 32, one distinct value each (before: 239.67 → 245.05, +5.38px, left edge sliding); menu {l 914.72, r 1176, w 261.28, t 49.5} identical on every open; glyph '▾' in every reading; transition-duration 0s"
  - cmd: "Aside repl --account u2 — paired closed/open screenshots at 1280, luminance profile of the caret column"
    result: "pass — caret ink rows 25–29 (closed) vs 26–29 (open), ink-bbox centre 27.5 → 28.0 = +0.5px (bar: 1px). With the default 50% pivot: rows 22–25, −3.5px"
  - cmd: "local production build — copy of frontend/ outside the repo, NEXT_PUBLIC_SITE_URL=https://jujutower.com MIJUAL_API_ORIGIN=http://127.0.0.1:8010 npm run build, standalone on :3014, same 15-reading pass"
    result: "pass — every number identical to dev; the caret ink profiles are byte-identical"
  - cmd: "Aside repl --account u2 — 390 mobile, dev, signed in, sheet opened/closed twice + 1.5s idle"
    result: "pass — desktop slot not rendered, 0 caret glyphs in the sheet, account row rects byte-identical across both cycles"
  - cmd: "hygiene — throwaway account created through the signup form, deleted through /portfolio/notifications → 계정 삭제 (arm, then confirm)"
    result: "pass — armed note rendered, deletion landed on / signed out; dev stack unchanged (api pid 60158, web pid 61423); :3014 stopped; production untouched"
  - cmd: python3 scripts/workflow.py validate
    result: pass
deviations:
  - "The plan's own tuning licence was used: a plain scaleY(-1) about the default box centre moves the caret's ink up 3.5px (measured, not predicted), so the rule carries transform-origin: 50% 66.7% — the glyph's ink centre, 8px down a 12px box. Nothing else in the mechanism changed."
  - "No Retina (dsf 2) paired-pixel proof: Aside's real window is 1440×900, so a 1280 CSS viewport emulated at dsf 2 renders past the captured surface. The pixel proof is at 1280 / dsf 1, which is the conservative grid — a finer device grid halves the snap quantum and can only shrink the 0.5px residual."
  - "Space-key activation of the frame did not toggle the menu through the instrument (keyboard.press(' ') and 'Space'); Enter did. Read as an instrument limitation, not a product finding — this slice does not touch activation, and the caret no longer depends on state at all. Named so it is not mistaken for a claim, and passed to P12.R1 to confirm with a real key event."
  - "The scratch production-build directory could not be deleted (the sandbox denied rm -rf). It sits outside the repo at <scratchpad>/p12s1-build."
doc_impact:
  - "frontend.md: Surfaces / the chrome's account slot — the caret is one ▾ flipped by a layout-neutral CSS transform in the open state (both caret code points are absent from the Noto subset, so a glyph pair meant two fallback faces with different advances and a frame that changed width on toggle); the flip pivots on the glyph's ink centre, not the line box's (P12.S1)"
doc_versions: n/a (non-review slice — deferred to a docs phase)
```

## What was wrong, and the one fact that decided the fix

`AccountSlotDesktop` rendered `{open ? CARET_OPEN : CARET_CLOSED}` — `▴` for open, `▾` for closed.
Neither U+25BE nor U+25B4 is in `frontend/app/fonts/NotoSansKR.subset.woff2` (nor in
`frontend/scripts/korean-charset.txt`), so both were **fallback** glyphs drawn out of whatever
system face `--font-sans` reached next, and the two landed in faces with different advances.
Measured again in this slice, in the caret's own computed font
(`notoSansKr, "notoSansKr Fallback Apple", …` at 12px), with a hidden probe span:

| glyph | advance @12px |
|---|---|
| `▾` U+25BE | **5.67px** |
| `▴` U+25B4 | **11.05px** |
| `▼` U+25BC | 11.05px |
| `▲` U+25B2 | 11.05px |

That is the +5.38px the frame changed by — the same delta `P12.DECOMP` measured on the operator's
own email (239.67 → 245.05px), and it is independent of the email's length: it is the glyph pair's,
not the frame's. Any fix keeping two code points keeps a platform-dependent pair of boxes (Windows
and Android reach different fallback faces again).

## The fix

`AccountSlot.tsx` renders one constant `CARET = "▾"` (`CARET_OPEN` retired; the header sketch and
the constant's doc comment now say the open reading is the same glyph flipped). `aria-expanded` on
the button already carries the state for assistive tech, and the span stays `aria-hidden`.

`AccountSlot.module.css` adds one rule:

```css
.frame[aria-expanded="true"] .caret {
  transform-origin: 50% 66.7%;
  transform: scaleY(-1);
}
```

No transition (R8 signed an instant swap; `transition-duration` on the span computes to `0s` and
`animation-name` to `none`). Nothing else in `.frame`, the hover state, the open state's colours,
the menu, the sheet or `Nav.tsx` moved.

### Why `transform-origin` is not decoration

A flip pivots on the element's box, and the caret's **ink** is not centred in that box: `▾` sits
down by the baseline, its ink occupying roughly the lower half of the 12px line box (canvas metrics:
ink 6.75px–9.99px from the box top; pixels: rows 25–29 of a box spanning 19.5–31.5). Flipping about
the box centre therefore lifts the ink. Measured at 1280, dsf 1, from paired screenshots:

| pivot | open-state caret ink rows | ink-bbox centre | shift vs closed |
|---|---|---|---|
| `50% 50%` (default) | 22–25 | 23.5 | **−3.5px** — visible |
| `50% 64.6%` | 26–29 | 28.0 | +0.5px |
| **`50% 66.7%`** (shipped) | 26–29 | 28.0 | **+0.5px** |
| `50% 69.8%` (canvas-ideal 8.37px) | 27–30 | 28.5 | +1.0px |

Chromium snaps the transformed layer to whole device pixels, so 64.6–66.7% land on the same rows;
66.7% is kept because it is also what the measurement says on its own terms (ink centre 8px down a
12px box = 2/3) and, being a percentage, it follows `--text-sm` if that ever changes.

The rendered pair, closed then open, same columns and the same 4–5 row band (luminance ramp over
the caret's own 11px-wide column, dev at 1280):

```
CLOSED                      OPEN
y= 25 |    .--:     |       y= 25 |             |
y= 26 |    *@@%     |       y= 26 |     :=      |
y= 27 |     @@:     |       y= 27 |     %@      |
y= 28 |     #%      |       y= 28 |    :@@+     |
y= 29 |     .:      |       y= 29 |    +@@#     |
```

The ink-**weighted centroid** moves +1.35px, and that is not displacement: mirroring a triangle
necessarily moves its centroid (the mass sits at the wide end) even when the shape lands exactly
in place. The bounding box is the honest measure of "did the caret move", and it moves 0.5px.

## The numbers, both runtimes

15 readings per runtime over 7 opens (click ×4, `Enter`, plus hover and unhover while open) and 7
closes (click, `Escape` ×4, outside-click), signed in on `/portfolio` at 1280:

| | dev (`127.0.0.1:3010`) | local production build (`:3014`) |
|---|---|---|
| frame `width` | **261.28** (one distinct value) | **261.28** (one distinct value) |
| frame `left` / `right` | 914.72 / 1176 | 914.72 / 1176 |
| frame `top` / `height` | 9.5 / 32 | 9.5 / 32 |
| caret `left` / `width` | 1161.33 / 5.67 | 1161.33 / 5.67 |
| menu (every open) | `{l 914.72, r 1176, w 261.28, t 49.5}` | identical |
| glyph / transform | `▾` always · `none` ⇄ `matrix(1,0,0,-1,0,0)` | identical |
| caret ink centre, closed → open | 27.5 → 28.0 (+0.5px) | byte-identical profiles |

The menu still hangs off the frame's right edge (`r` 1176 = the frame's `right`) with `min-width` =
frame width (`w` 261.28). Hovering the frame moves nothing, in either state.

**Layout is untouched, which is the point.** In both states the caret span's *layout* box is the
same — `offsetTop` 10, `offsetLeft` 247, `offsetWidth` 6, `offsetHeight` 12 — the frame's
`offsetWidth`/`offsetHeight` are 261/32, and `document.documentElement.scrollWidth` is 1280. The
span's `getBoundingClientRect().top` does read 19.5 closed / 23.51 open: that is the *visual* box a
transform reports (19.5 + 2 × (8.004 − 6) = 23.508, exactly the flip), and it is invisible because
the span has no background or border — only the ink inside it can be seen, and that stays put.

## 390 (mobile)

The desktop slot is `display: none` at ≤480 (`Nav.module.css` `.utility`) and the sheet has no
caret, so this fix cannot reach it — confirmed rather than assumed. At 390 in dev, signed in:
`button[aria-haspopup=menu]` has `offsetParent === null` (not rendered on screen), **0** caret
glyphs (`▾▴▼▲`) are visible anywhere in the sheet, and the account rows are byte-identical across
two open→close cycles and a 1.5s idle inside an open sheet:

| row | rect (all six readings) |
|---|---|
| identity row | `{l 0, t 148, w 390, h 54}` |
| email span | `{l 58, t 165.7, w 201.61, h 18.59}` |
| 알림 설정 | `{l 0, t 202, w 390, h 48}` |
| 로그아웃 | `{l 0, t 250, w 390, h 48}` |

## Instrument, and the runtime

**Aside, `aside repl --account u2` (profile 「claude2」)** — every invocation carried `--account u2`;
the operator's `u0` was never driven and `aside account use` was never run. The CDP fallback was not
needed. `## Operator Runtime` (operations.md v0014) is stale on exactly that point, as `phase.md`
records; P4 already owes the correcting note, so this slice writes none for it.

Runtime: the manifest's dev stack (`make stack-up`, `next dev`, StrictMode) at
`http://127.0.0.1:3010`, **plus** the local production build, which is where dev and production
differ — a copy of `frontend/` outside the working tree, built with
`NEXT_PUBLIC_SITE_URL=https://jujutower.com MIJUAL_API_ORIGIN=http://127.0.0.1:8010 npm run build`,
`.next/static` and `public/` staged into `.next/standalone/`, served with `node server.js` on
**3014** and stopped afterwards. Production (`https://jujutower.com`) was never opened for writes
and still serves `a74c58a`; this fix reaches it only through `P12.S2`.

Three instrument notes, all passed to `P12.R1` in the notebook because they cost real time here:

1. **`page.screenshot({clip})` is unusable for a region under device-metrics emulation** — the clip
   is taken in *device* pixels against Aside's real 1440×900 window, not in the emulated viewport's
   CSS pixels, so it silently captures the wrong place (a first attempt returned 280 identical
   background pixels).
2. **`cdp.send('Page.captureScreenshot', {clip})` returned byte-identical images for two visibly
   different states** (closed vs open, where the frame's background and border both change) — a
   stale capture, and it must not be trusted for before/after work.
3. What does work: full-viewport `await page.screenshot()` (a PNG `Buffer` → base64) and cropping
   outside the browser. There is no PIL on this machine; `zlib` + a ~40-line scanline unfilter is
   enough, and unfiltering only up to the last row you need keeps it instant.

Also worth knowing for any Aside slice: the CLI takes **top-level `await`** (a `return` at top level
makes it wrap the code and then `await` is a syntax error), and **tabs do not survive between
invocations** — `listBrowserTabs()` comes back empty in the next call, so each invocation opens its
own tab, while the profile's cookies persist (the throwaway session carried across every call here).

## Hygiene

The signed-in state needed an account, so one was created **through the product** (the login
panel's own 계정 만들기 form, `p12s1-caret-0903@example.com`) and deleted **through the product**
(`/portfolio/notifications` → 계정 삭제, pressed once to arm — the
「계정을 삭제하면 이메일 주소를 즉시 지웁니다」 note and 취소 both rendered — then confirmed), which
landed on `/` signed out with the 로그인 link back and no account frame. `NEXT_PUBLIC_VOCKY_SRC` was
never set, the operator's `.env` was never opened, and `make stack-status` shows the stack exactly as
found (postgres healthy, api pid 60158, web pid 61423 — the same pids as at plan time).

## Dead ends

- **A fixed-width centred caret box** (the plan's option (b)) was not built: it needs a chosen width
  wide enough for the widest fallback glyph on *some* platform, which is a guess on every other one,
  and it changes what R8 signed (the caret gains padding). One glyph has no second box to size.
- **`rotate(180deg)`** was not needed: on a horizontally symmetric triangle it renders the same ink
  as `scaleY(-1)` and has the identical pivot problem, so it would have needed the same
  `transform-origin` tuning with nothing gained.
- **The canvas-metric ideal pivot (69.76%)** measured *worse* than the value derived from pixels
  (+1.0px vs +0.5px) because Chromium snaps the transformed layer to whole device pixels. Where the
  two disagree, the pixels are what the operator sees.
- Notebook state for the next slice is in `works/phases/active/P12/phase.md`; it is not restated here.
