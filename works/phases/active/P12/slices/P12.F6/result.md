# P12.F6 — result

- **status:** done
- **summary:** The 정정 이력 ↔ 접기 button on `/events/[rcept_no]` now keeps one width across the toggle — the `Nav.module.css` ghost-twin applied to `.historyButton` (`data-label` + a hidden `::after` sharing the button's single grid cell, the visible label moved into an inner `.historyLabel` span). The **77.53 → 66.70 px** (−10.83) narrowing on open becomes **one distinct rect, `[125, 1178.94, 77.53, 36]`**, in dev and a fresh production build against a HEAD control; 390 stays byte-identical in **both** states (the ≤767 `width: 100%` box was already immune); resting `AE = 0` vs HEAD at both viewports with live positive controls. **R1 F8 (the /ask composer) and R1 F10 (the auth mode switch) ship no code** — every fix for them changes the resting layout of a signed surface, so they become **Q7** and **Q8** on `## Operator Questions`, Q8 carrying a freshly measured 390 "before".
- **files_changed:**
  - `frontend/components/event/Corrections.tsx`
  - `frontend/components/event/Event.module.css`
  - `works/phases/active/P12/phase.md`
  - `works/phases/active/P12/slices/P12.F6/result.md`
- **validation:**
  - `cd frontend && npm run typecheck` — pass
  - `cd frontend && npm run smoke` — pass (22/22)
  - `NEXT_PUBLIC_SITE_URL=https://jujutower.com npm run build` in a fresh copy outside the repo — pass, **no warnings and no errors** (a second, HEAD-only copy built the same way as the control)
  - Aside `repl --account u2`, `/events/20260806000329`, **1280 + 390**, dev (3010) + fixed production build (3014) against a HEAD production build (3015), closed → open → closed — pass (tables below)
  - `python3 scripts/workflow.py validate` — pass (only the pre-existing `consolidation_owed=P4` / `stale_docs=product` / `oversized_doc_sections` warnings)
- **deviations:** Two, both about the instrument rather than the change. (1) The plan's evidence shape said "resting `AE = 0` vs HEAD"; my first screenshot pass produced that zero **falsely** and I caught and replaced it — see *Two instrument traps* below. The reported zeros are from one capture per invocation, with the macOS overlay-scrollbar strip excluded and a live positive control beside every zero. (2) The plan offered a choice for the ≤767 block (`justify-items` on the grid *or* leaving `justify-content` on the span); I kept the existing `justify-content: center` line untouched, since it keeps 390 byte-identical in both states, and added only a comment saying why it still works on a grid.
- **doc_impact:** one line appended to `phase.md` (`frontend.md`, Surfaces / 공시 상세) — quoted in the verdict at the end.
- **review_verdict:** n/a
- **explain:** n/a

---

## What changed

Two files, ~30 lines net, no copy and no new strings.

**`components/event/Corrections.tsx`** — the button carries `data-label={CORRECTION_HISTORY_KO}`
(the copy still lives in `components/event/copy.ts`; the attribute only re-uses it), and its visible
content moved into one inner `<span className={styles.historyLabel}>` holding the label text and,
when open, the existing `aria-hidden` `historyMark` span. `type`, `aria-expanded`, `aria-controls`
and `onClick` are untouched, and so are `COLLAPSE_KO` / `CORRECTION_HISTORY_KO` / `CLOSE_GLYPH`.

**`components/event/Event.module.css`** — `.historyButton` becomes the grid `Nav.module.css` §`.link`
already uses (`inline-grid`, `grid-template-areas: "label"`, `align-items: center`,
`justify-items: center`); `.historyLabel` takes `grid-area: label` plus the `inline-flex` +
`gap: var(--space-2)` that used to sit on the button; and `.historyButton::after` is the twin —
`content: attr(data-label)`, same cell, `height: 0`, `overflow: hidden`, `visibility: hidden`,
`pointer-events: none`, and **no `font-weight` override**, because both labels are the same weight.
`padding-inline`, `min-height`, `white-space`, the `:hover` and `[aria-expanded="true"]` rules and
the `background`/`color` transition are unchanged; **no width transition was added** (there was none).
The ≤767 block keeps `min-height: 44px; width: 100%; justify-content: center` verbatim: on the grid
that centres the single max-content track inside the full-width box, which is exactly what it did on
the old flex row.

Why the resting pixels cannot move: the twin renders the **resting** label 「정정 이력」, which is the
**wider** of the two states, so the shared cell is sized by the state the reader is already looking
at. The closed box is what it always was; the open state simply stops shrinking, and its
「접기 ×」 sits centred in the box it inherits. A side effect worth naming: the × is `--font-mono`,
so before this change the button's width also depended on which mono face had loaded (R1 F5's
territory) — it no longer does, because the sans twin sets the box.

## Before / after — the button across the toggle

Rects are `[x, y, w, h]` in document coordinates; each state harvested with the page scrolled to a
fixed offset so nothing is a scroll artefact. `n` = elements whose rect changed between the closed and
the open state, **excluding the disclosure panel's own subtree** (its 666.03 px appearance is the
intended effect).

**1280 — HEAD production build (3015)**

| state | button rect | width | label |
|---|---|---|---|
| closed | `[125, 1178.94, 77.53, 36]` | 77.53 | 정정 이력 |
| open | `[125, 1178.94, 66.70, 36]` | **66.70** | 접기 × |
| closed again | `[125, 1178.94, 77.53, 36]` | 77.53 | 정정 이력 |

Distinct rects sampled per `requestAnimationFrame` through the toggle: **two**
(`77.53` → `66.70` opening, `66.70` → `77.53` closing). R1's −10.83 px reproduces exactly, and the
`historyMark` enters at `[170.09, 1189.94, 6.61, 14]` — R1's 6.61 × 14 to the hundredth.

**1280 — fixed production build (3014); dev (3010) identical in every cell**

| state | button rect | width | inner label span |
|---|---|---|---|
| closed | `[125, 1178.94, 77.53, 36]` | 77.53 | `[140, 1188.44, 47.53, 17]` |
| open | `[125, 1178.94, 77.53, 36]` | **77.53** | `[145.41, 1188.44, 36.70, 17]` |
| closed again | `[125, 1178.94, 77.53, 36]` | 77.53 | `[140, 1188.44, 47.53, 17]` |

Distinct rects through the toggle: **one**, `125,1178.94,77.53,36`, opening and closing. The label
span is centred by construction — the cell's interior is 77.53 − 2 (border) − 28 (padding) = 47.53,
the open label is 36.70, and 140 + (47.53 − 36.70)/2 = **145.415**, which is what the browser reports.

**390 — HEAD and fixed, both builds, both states**

`[33, 1753.81, 324, 44]` in every reading — one distinct value before the change and after it. The
≤767 `width: 100%` box was already immune (R1 said so) and the fix does not disturb it; the inner
label span sits at `[171.23, 1767.31, 47.53, 17]` closed and `[176.64, 1767.31, 36.70, 17]` open,
both centred in the 324 px box exactly where the old flex row put the same glyphs.

**What else moved.** Closed → closed (a full toggle round trip): **0 rects changed**, on every build
and both viewports. Closed → open: only the button's own interior, the strip's own height, and
everything below the disclosure — `docH` 1464 → 2130 at 1280 and 2197 → 3470 at 390, byte-for-byte
the same numbers as HEAD, so the disclosure behaves exactly as it did.

## Resting `AE = 0` against HEAD, with the controls that make the zero mean something

Full-viewport captures with the 정정 band scrolled to a fixed offset, one capture per `aside repl`
invocation, right-hand 16 px (the macOS overlay scrollbar, which fades on its own schedule) excluded.

| viewport | comparison | AE |
|---|---|---|
| 1280 | **resting**, HEAD (3015) vs fixed (3014) | **0** |
| 1280 | open, HEAD vs fixed — *positive control* | 1.07376e+07, and the diff's bounding box is **63 × 36 at (140, 179)**: the button's interior and nothing else |
| 1280 | resting vs open, fixed — *positive control* | 4.32022e+09 |
| 390 | **resting**, HEAD vs fixed | **0** |
| 390 | **open**, HEAD vs fixed | **0** (mobile is byte-identical in both states) |
| 390 | resting vs open, fixed — *positive control* | 1.73704e+09 |

The open-state diff at 1280 being confined to a 63 × 36 rectangle at the button's interior is the
whole visual change, stated as a measurement: the box is the resting width and 「접기 ×」 is centred
in it. Enlarged crops of the HEAD and fixed open buttons sit beside these captures in the session
scratchpad; they show the same two glyphs at the same size, in a wider frame.

## Keyboard, semantics and the twin

Measured on the fixed build with the button focused:

- **Enter**, then a **real CDP `Space`** (`Input.dispatchKeyEvent` `rawKeyDown` / `char " "` / `keyUp`,
  not `keyboard.press(' ')` — the phase's recorded artefact), then Enter again: `aria-expanded`
  `false → true → false → true`, label 정정 이력 → 접기 × → 정정 이력 → 접기 ×, and the rect is
  `[125, 1178.94, 77.53, 36]` in **all four** states.
- `aria-controls` is the same generated id before and after; the panel's `hidden` attribute still
  drives it.
- **Accessible name**, via CDP `Accessibility.getPartialAXTree`: HEAD `button` / 「정정 이력」, fixed
  `button` / 「정정 이력」 — *identical*. In the open state both read 「접기」 (the × is `aria-hidden`,
  as before). **The twin contributes nothing to the name**, which is what `visibility: hidden` buys
  over `opacity: 0`.
- **Hit testing**: `document.elementFromPoint` at the button's centre returns
  `span.…__historyLabel` in every state — the twin is never the hit target (`pointer-events: none`,
  and `height: 0` besides).
- The computed `::after` is `content: "정정 이력"`, `visibility: hidden` — the twin is present and
  doing its job rather than silently absent.

## Console / hydration

Captured with an in-page shim installed through `Page.addScriptToEvaluateOnNewDocument` **before**
navigation (`console.log/info/warn/error/debug` + `error` + `unhandledrejection`), over the load and
two full toggles, **with a control** that proves the capture is live:

| runtime | output |
|---|---|
| fixed production build (3014), 1280 | **nothing** |
| fixed production build (3014), 390 | **nothing** |
| dev (3010), 1280 | `info: …React DevTools…`, `log: [HMR] connected` — dev noise only |

Control on every run: an injected `console.error` / `console.warn` appears immediately. No hydration
warning, no error, on any measured load.

## Served bytes

`/events/20260806000329` grows **83 B** (58,331 → 58,414) — the `data-label` attribute with its
escaped Korean plus the inner `<span>`. Only pages that render the 정정 band pay it; the CSS module
grows by the twin's rule.

## Two instrument traps, and why the first zeros were thrown away

Both are new; both would have produced a **false clean pass**, and both are in the `## Doc impact`
note's territory rather than the product's.

1. **A second `page.screenshot()` in the same `aside repl` invocation returns the first capture's
   bytes.** My first pass captured HEAD and then the fixed build in one invocation and got
   md5-identical PNGs — `AE = 0` "at both viewports". That zero was the instrument, not the product:
   captured one per invocation, the same pair is still `AE = 0` at rest but differs in the open state
   exactly as it must. This extends the seam already recorded for `Page.captureScreenshot` returning
   stale bytes: **treat any second capture in one invocation as stale.**
2. **`page.screenshot({fullPage: true})` under `Emulation.setDeviceMetricsOverride` tiles the top
   viewport down the image** instead of scrolling the page. The 1280 × 1464 and 390 × 2197 PNGs it
   produced have the right *dimensions* — which is exactly what makes it convincing — but they are
   the first 900 px repeated, so they never contained the 정정 band at all and every comparison over
   them was a comparison of the page header. The working shape is the one F2 recorded for phone
   captures: scroll to a fixed offset, take a **viewport** capture, crop the leftmost emulated tile.

A third, milder one: the right-hand ~7 px of a viewport capture is the macOS overlay scrollbar, which
fades on its own timer, so two otherwise identical captures differ there. Crop it out (and say so)
rather than chasing it.

## R1 F8 — no code, and why (→ Q7)

R1's numbers, quoted: on `/ask` at 1280 the send button is 보내기 **59.13** → 답변 준비 중…
**99.92** → 중지 **48.09** → 보내기 **59.13** px across one turn, its x travels 71 px, and the input
beside it swings **572.88 → 652.08 → 703.91 → 692.88** (131 px).

I read `components/ask/Composer.tsx` and `Ask.module.css` (read only — nothing was edited) to check
whether a resting-identical mechanism exists that the plan missed. **It does not.** The resting label
「보내기」 is the **narrowest** of the three, so Family B's ghost — which reserves the widest — makes
the *resting* button ≈ 40.8 px wider and the input that much narrower, on `/ask` **and** inside the
440 × 620 widget, whose width is a signed literal (`Ask.module.css`: 「440×620 exactly wherever it
exists」). The alternatives all move signed ground rather than pixels: the pending text does not fit
the resting box; putting the pending state somewhere other than the button, or shortening it, changes
copy the record signs three times over (`SEND_KO` was signed by R14 Q-C on 2026-08-24; `PREPARING_KO`
and `STOP_KO` are the record's own strings, and the CSS comment above `.send` quotes the rule
「버튼 텍스트 교체 + disabled — 스피너·점 금지」); and pinning the *input* instead simply relocates the
same 40.8 px. That is a visible change to a signed surface at rest, which is the operator's call —
the same reasoning `DECOMP2` applied to R1 F11. **Q7** carries it.

## R1 F10 — no code, and why (→ Q8), with the 390 "before" this slice was asked to take

Measured myself on a **plain** visit (no 로그아웃 flash — `AuthPanel`'s reservation only applies when
the stamp is present, and F5's note says the panel is 56.59 px taller in the flash landing), HEAD
production build (3015), pressing 계정 만들기 and then 로그인 back:

| | 1280 로그인 | 1280 계정 만들기 | Δ | 390 로그인 | 390 계정 만들기 | Δ |
|---|---|---|---|---|---|---|
| panel height | 404.11 | 425.48 | **+21.37** | 396.11 | 417.48 | **+21.37** |
| `.head` | 56.92 | 77.84 | +20.92 | 56.92 | 77.84 | +20.92 |
| `.intro` | 20.92 | 41.84 | **+20.92** (wraps to 2 lines) | 20.92 | 41.84 | **+20.92** |
| form `y` | 241.92 | 262.84 | +20.92 | 237.92 | 258.84 | +20.92 |
| email field `y` | 266.52 | 287.44 | +20.92 | 262.52 | 283.44 | +20.92 |
| password field `y` | 351.11 | 372.48 | +21.37 | 347.11 | 368.48 | +21.37 |
| quiet row `y` | 479.11 | 500.48 | +21.37 | 475.11 | 496.48 | +21.37 |
| `.rule` span | — | `41.75 × 17.05` inserted | | — | `41.75 × 17.05` | |
| mode-switch link | 58.56 | 33.13 | −25.43 | 58.56 | 33.13 | −25.43 |
| 비밀번호 재설정 | `80.64 × 44` | gone | | `80.64 × 44` | gone | |
| document height | 900 (viewport-bound) | 900 | 0 | 991 | 1013 | +22 |

Pressing 로그인 back restores every number exactly. R1's 1280 reading (404.1 → 425.5, +21.37, intro
+20.92) reproduces to the hundredth, and the new fact is that **390 behaves identically**: the intro
wraps to a second line at both widths, so a single reservation would serve both — and cost the same
+20.92 px at both. The `.rule` span and the quiet-row link swap change no height (the row is 44 px in
both modes), so the *entire* 21.37 px is the intro's second line.

That is why there is no code here. The only reservation available is a **blank line under the login
intro at rest** — +20.92 px of empty panel under 「가입한 이메일과 비밀번호로 로그인합니다.」 in the
state a reader lands on, at both viewports. Reserving in the *other* direction is not available: the
signup intro is genuinely two lines. So every fix trades a shift the reader causes with their own
press for a permanent gap on the landing page — a visible change to a signed surface, and the
operator's decision. **Q8** carries it, with these numbers.

## Notebook

`phase.md` was edited, not appended to: one `## Decisions` line for this slice's ruling, **Q7** and
**Q8** appended to `## Operator Questions`, one `## Doc impact` line, F5's `for P12.F6` note consumed
(see below), and `## Now` rewritten. No `for P12.F7` note was added — the feedback dialog's send
button is a ghost in a right-aligned actions row, and nothing I learned here changes how that behaves;
what I *did* learn that a later slice needs is the two instrument traps above, and those belong to the
qa doc's seam, so they are in the `## Doc impact` line and in this file rather than as a note that
every remaining dispatch would re-read.

**F5's `for P12.F6` note is consumed.** It told me exactly what moved in `AuthPanel.tsx` and which
three things not to disturb. **`AuthPanel.tsx` was read, not edited** — the F10 work in this slice is
a measurement and a question, so `.flashSlot`, its `display: contents`, the `:empty` reservation and
the `flashResolved` release were never touched. The note's operative instruction was followed: the
F10 "before" above was taken on a **plain** visit, with `data-mj-auth-flash` absent and the flash slot
measuring `[0, 0, 0, 0]` in every reading, which is also the state R1 F10 measured.

## Instrument

**Aside `repl` over Bash, `aside repl --account u2`** (profile 「claude2」) — never `u0`, never
`aside account use`. Each invocation opened its own tab with `openTab` and did one job. Everything the
phase's recorded seam says held: CDP through `page._sendToTarget`, `Emulation.setDeviceMetricsOverride`
for both viewports, one argument to `page.evaluate`, no top-level `return`, no `page.waitForTimeout`,
the script passed from a shell **variable**, and rect keys as `tag#id.classes` + occurrence index over
**visible** elements only. Additions and corrections:

- **`page.console.logs()` returns an object, not an array, and never captured anything** — and neither
  did `page.on("console", …)`, which did not fire even for an injected `console.error`. The reliable
  console capture is the in-page shim above, and it needs a control every time.
- The two screenshot traps and the scrollbar strip, in *Two instrument traps* above.
- `page` also exposes `cdp`, `mouse`, `keyboard`, `frameManager` and `targetId` directly; `pwd()` is
  **not** a function in this build even though `fs` is present, so a script must not end by asking for
  its own session directory — find it with `ls -dt ~/.aside/u/2/sessions/*/ | head -1` afterwards.
- `window.scrollTo(0, y)` clamps silently, so a "fixed scroll offset" shared by a short page and a tall
  one is not the same offset; assert the resulting `scrollY` in the same probe (both builds clamped to
  564 and 1297 identically here, which is itself a check).

## Hygiene

No account was needed — the 정정 band and `/auth/login`'s mode switch are both signed-out surfaces, so
nothing was created or deleted. **Production was never visited**; every request went to `127.0.0.1`.
Both build copies live under the session scratchpad, outside the repo; **3014 and 3015 are stopped**
and their ports confirmed closed, with only the dev stack's 3010 listening. `make stack-status` is as
found (postgres up 5 days, api pid 60158, web pid 61423 — the same pids as at the start). No test file
added, nothing committed, no workflow state command run other than `validate`.
