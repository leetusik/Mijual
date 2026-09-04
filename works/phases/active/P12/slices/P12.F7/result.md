# P12.F7 — result

- **status:** done
- **summary:** The 의견 보내기 dialog keeps **one body height** from the moment 보내기 (or 다시 시도) is pressed: the body's own rendered height is read in the submit handler and handed to every later body as an inline `min-height`, and `.actions` gained `margin-top: auto` so the buttons stay at the bottom of a pinned body. The panel's **−75.45 px / top edge +75.45 at 1280** and the ≤480 sheet's **−91.46 / top edge +91.46** become **one distinct dialog rect** across editing → sending → sent and → failed, in dev, the fixed production build and against a HEAD control; resting `AE = 0` at both viewports with live positive controls. **닫기's unmount was measured before touching it and moves nothing else** (1 of 11 visible elements changes — itself), so the record's 「닫기 disappears」 ships unchanged. The 보내기 ↔ 보내는 중입니다 **+53.47 px** send button ships **no code** and becomes **Q9**.
- **files_changed:**
  - `frontend/components/chrome/Feedback.tsx`
  - `frontend/components/chrome/Feedback.module.css`
  - `works/phases/active/P12/phase.md`
  - `works/phases/active/P12/slices/P12.F7/result.md`
- **validation:**
  - `cd frontend && npm run typecheck` — pass
  - `cd frontend && npm run smoke` — pass (22/22)
  - `NEXT_PUBLIC_SITE_URL=https://jujutower.com npm run build` in a fresh copy outside the repo — pass, **no warnings, no errors** (a second copy built the same way from HEAD as the control)
  - Aside `repl --account u2`, footer entry + nav sheet row, **1280 + 390**, dev (3010) + fixed production build (3014) against a HEAD production build (3015), editing → sending → sent and editing → sending → failed (failure forced over CDP `Network.setBlockedURLs`), plus the dragged textarea, a 498-character failed body, the 다시 시도 retry, the `below` placement, all four close paths and focus return — pass (tables below)
  - `python3 scripts/workflow.py validate` — pass (only the pre-existing `consolidation_owed=P4` / `stale_docs=product` / `oversized_doc_sections` warnings)
- **deviations:** Three, all in the verification rather than the change. (1) **The plan's premise about where a real send lands is wrong, and this is worth recording:** `src/mijual/web/vocky.py` `submit()` **forwards** the message to vocky's ingest endpoint and 「touches no table」 — so the 8 real sends below created 8 rows **in the vocky project**, through the dev API, and wrote **nothing** in Mijual's database. Production was never visited. (2) The `below` placement (the signed-in account menu's entry) was verified **without an account**: the footer's panel was given the same `.asPanelBelow` class through the DOM and driven with real mouse presses, on both builds. That measures the mechanism under test — the body pin is placement-independent — but it is not the account menu itself, and I say so rather than claim it. (3) The failed state is forced with `Network.setBlockedURLs` (the plan's first option, `Fetch.failRequest`, needs CDP *events*, which this repl surface does not deliver); nothing leaves the browser on those runs.
- **doc_impact:** one line appended to `phase.md` (`frontend.md`, Surfaces / 의견 보내기) — quoted at the end.
- **review_verdict:** n/a
- **explain:** n/a

---

## What changed

Two files. No copy, no new string, no transition, no test file; `Nav.tsx`, `Footer.tsx` and
`AccountSlot.tsx` untouched.

**`components/chrome/Feedback.tsx`** — a callback ref (`holdBody`) on **each** of the three bodies
(they are mutually exclusive, and 다시 시도 must pin the *failed* body it was pressed in), a
`pinnedHeight` state, and three lines in `send()`: read
`body.current.getBoundingClientRect().height` **before** anything changes, then set the pin and the
phase **in the same handler call**, so React commits them together and no intermediate frame exists.
Every non-editing body renders `style={{ minHeight: pinnedHeight }}`; the editing body renders
`undefined` — **no inline style at all** — which is why the resting dialog is byte-identical.

`min-height`, never `height`, is F4's rule applied here: a failed body carrying a long message may
legitimately exceed the pin and must be allowed to grow (measured below).

**Why not a CSS constant.** The editing body's height depends on the viewport *and* on a textarea
the reader may have dragged taller. Measured: a 60 px drag makes the body **323.016 px** instead of
**263.016**, so a constant would have been 60 px wrong exactly when the reader had just taken the
trouble to make room.

**`components/chrome/Feedback.module.css`** — `.actions { margin-top: auto }`. The row is already
the last child of the `.body` flex column, so the auto margin absorbs exactly the free space the
body has — **none at all** in the editing state, whose height is its content's. It takes effect only
in a pinned body, and what it buys is measured: on the fixed build the actions row sits at
**y = 791.016** at 1280 and **y = 780** at 390 in *every* state — precisely where 보내기 was when
the reader pressed it. Without it the sent body's buttons would have packed to the top of the pinned
box, ~136 px above the reader's cursor.

## Before / after — the footer entry, anchored panel, 1280

Rects are `[x, y, w, h]` in viewport coordinates at a fixed scroll offset; every state harvested per
`requestAnimationFrame` by an init script installed before navigation.

**HEAD production build (3015) — the "before"**

| state | dialog | body | actions y | send button | 닫기 |
|---|---|---|---|---|---|
| editing (empty) | `[796, 526, 380, 318.016]` | `[797, 580, 378, 263.016]` | 791.016 | `[1087.734, 791.016, 71.266, 36]` 보내기 | `[1026.891, 791.016, 48.844, 36]` |
| editing (typed) | `[796, 526, 380, 318.016]` | same | 791.016 | same | same |
| **sending** | `[796, 526, 380, 318.016]` | same | 791.016 | `[1034.266, 791.016, **124.734**, 36]` 보내는 중입니다 | **absent** |
| **sent** | `[796, 601.453, 380, **242.563**]` | `[797, 655.453, 378, 187.563]` | 791.016 | — | `[1110.156, 791.016, 48.844, 36]` |
| **failed** (short) | `[796, 602.453, 380, **241.563**]` | `[797, 656.453, 378, 186.563]` | 791.016 | `[1071.531, 791.016, 87.469, 36]` 다시 시도 | `[1010.688, 791.016, 48.844, 36]` |

**−75.453 px** tall on 접수, top edge **down 75.453**; **−76.453** on 실패, top edge **down 76.453**
(R1 measured the sent side as −75.46 / 75.45 and never measured the failed one; it is very slightly
worse). Distinct dialog rects through editing → sent: **two**. `layout-shift` at the send: **0.00618**.

**Fixed production build (3014); dev (3010) identical in every cell**

| state | dialog | body | `min-height` | actions y |
|---|---|---|---|---|
| editing (empty) | `[796, 526, 380, 318.016]` | `[797, 580, 378, 263.016]` | `auto` | 791.016 |
| editing (typed) | `[796, 526, 380, 318.016]` | same | `auto` | 791.016 |
| sending | `[796, 526, 380, 318.016]` | same | **263.016px** | 791.016 |
| **sent** | `[796, 526, 380, 318.016]` | `[797, 580, 378, 263.016]` | 263.016px | 791.016 |
| **failed** | `[796, 526, 380, 318.016]` | `[797, 580, 378, 263.016]` | 263.016px | 791.016 |
| **failed → 다시 시도 → sending → failed** | `[796, 526, 380, 318.016]` | same | 263.016px | 791.016 |

**One distinct dialog rect** — 6 sampled frames across the retry round trip, all identical. No
`layout-shift` entry at the send at all (only the reader's own typing, 0.00016, `hadRecentInput`).

## Before / after — 390, the bottom sheet (footer entry **and** the nav sheet's row)

| build | editing | sending | sent | failed |
|---|---|---|---|---|
| HEAD (3015), footer | `[0, 498.984, 390, 345.016]` | same box | `[0, 590.438, 390, **253.563**]` | `[0, 591.438, 390, **252.563**]` |
| HEAD (3015), nav sheet row | `[0, 498.984, 390, 345.016]` | same box | — | `[0, 591.438, 390, 252.563]` |
| **fixed (3014) + dev (3010)**, both entries | `[0, 498.984, 390, 345.016]` | `[0, 498.984, 390, 345.016]` | `[0, 498.984, 390, 345.016]` | `[0, 498.984, 390, 345.016]` |

**−91.453 / top edge down 91.454** on 접수 and **−92.453 / 92.454** on 실패 become **one distinct
value**; `min-height` reads **291.016px**; the actions row is at **y = 780** in every state on both
builds. The nav sheet's row (`variant="sheet"`) produces the identical numbers, and the class on the
surface was confirmed to be `…__asSheet` with the menu sheet closed behind it. `layout-shift` at the
send: HEAD **0.04407** (sent) / **0.04456** (failed, footer and nav alike) → **no entry at all** on
the fixed build.

## The dragged textarea — why the pin is read at runtime

Fixed build, 1280, resize handle dragged 60 px down with real CDP mouse events (6 × 10 px moves):

| | field | body | dialog | `min-height` |
|---|---|---|---|---|
| opened | `346 × 104` | `378 × 263.016` | `[796, 526, 380, 318.016]` | auto |
| after the drag | `346 × 164` | `378 × 323.016` | `[796, 466, 380, 378.016]` | auto |
| sending | `346 × 164` | `378 × 323.016` | `[796, 466, 380, 378.016]` | **323.016px** |
| failed | — | `378 × 323.016` | `[796, 466, 380, 378.016]` | 323.016px |

The pin equals the **enlarged** form and the top edge holds at 466. A measured CSS constant would
have been the 263.016 number and would have dropped this panel 60 px.

## The failed body that is legitimately taller

Fixed build, 1280, a 498-character message, forced failure:

| build | dialog | body | `min-height` | actions y |
|---|---|---|---|---|
| fixed (3014) | `[796, 360.734, 380, 483.281]` | `378 × 428.281` | 263.016px (floor, exceeded) | 791.016 |
| HEAD (3015) | `[796, 360.734, 380, 483.281]` | `378 × 428.281` | auto | 791.016 |

The preserved message's `.inset.kept` is **286.313 px** tall, so the body exceeds the pin by
**165.265 px** and grows — and because the panel is bottom-anchored the growth appears *upward*, the
top edge rising from 526 to 360.734. **HEAD renders the identical box**, which is the proof that the
fix only ever installs a floor: where the content is taller than the pin, the two builds are
numerically the same. That is `min-height` doing it; `height` would have clipped or scrolled the
reader's own words.

## 닫기 while sending — measured before touching, and therefore not touched

The record says 닫기 **disappears** while sending; `DECOMP2`'s cut line said "keep it
mounted-but-disabled". The plan made the measurement decide. On the HEAD build, in the editing state
(so the send button's label is constant), I mapped **every visible element** in the dialog, removed
the 닫기 button from the DOM exactly as React does, re-mapped, then put it back with
`visibility: hidden`, then restored it:

| viewport | visible elements | 닫기 removed | 닫기 restored, `visibility: hidden` | restored |
|---|---|---|---|---|
| 1280 | 11 | **1 changed** — `BUTTON.quiet` itself (`[1026.891, 791.016, 48.844, 36]` → absent) | **0 changed** | **0 changed** |
| 390 | 11 | **1 changed** — `BUTTON.quiet` itself (`[241.891, 780, 48.844, 48]` → absent) | **0 changed** | **0 changed** |

Nothing else moves, at either viewport. The row is `justify-content: flex-end` and 닫기 is *left* of
the send button, so removing it cannot move anything to its right; the row's height is 36 (48 at
≤480) with or without it, because both buttons are that tall. **So the record's behaviour ships
exactly as it is** — no `visibility: hidden`, no `disabled`, no code. The send button's own
+53.47 px growth is a separate matter and is Q9.

## The `below` placement (the account menu's entry point)

Verified **without an account**, on both builds, by adding the surface's own `.asPanelBelow` class
to the footer's panel through the DOM and then driving it with real mouse presses — the mechanism
under test (the body pin) is placement-independent, and this is the opposite anchored edge:

| build | editing | sending | failed |
|---|---|---|---|
| HEAD (3015) | `[796, 581.938, 380, 318.016]`, actions y 846.953 | same | `[796, 657.938, 380, **241.563**]`, actions y **846.5** |
| fixed (3014) | `[796, 581.938, 380, 318.016]`, actions y 846.953 | same | `[796, 581.938, 380, 318.016]`, actions y **846.953** |

Top-anchored, the **bottom** edge is what used to move (up 76.453 px) and the actions row wobbled
0.453 px with it; both are gone. The signed-in account menu itself was **not** exercised — no
throwaway account was created for this slice.

## Resting `AE = 0` against HEAD, with the controls that make the zero mean something

One capture per `aside repl` invocation (F6's trap (a)); a **viewport** capture, never
`{fullPage: true}` under emulation (trap (b)); cropped to the leftmost emulated tile with the
right-hand strip (the macOS overlay scrollbar) excluded — 1264 × 900 at 1280, 374 × 844 at 390. Route
`/events/20260806000329` (F6 proved it static; the landing's Cosmos star field would have made a
zero impossible to trust). Both builds at the identical scroll offset (`scrollY` 564 / 1353, document
1464 / 2197 — asserted in the same probe).

| viewport | comparison | AE | diff box |
|---|---|---|---|
| 1280 | **resting (editing)**, HEAD (3015) vs fixed (3014) | **0** | — |
| 1280 | failed, HEAD vs fixed | 4.85724e+08 | **380 × 259 at (796, 525)** — the panel's own column |
| 1280 | sent, HEAD vs fixed | 4.89963e+08 | 380 × 263 at (796, 525) (includes the two different 접수 번호 uuids) |
| 1280 | resting vs failed, fixed — *positive control* | 3.52901e+08 | 362 × 272 at (813, 599) |
| 1280 | resting vs sent, fixed — *positive control* | 2.69329e+08 | 362 × 272 at (813, 599) |
| 1280 | resting vs failed, HEAD — *positive control* | 5.59303e+08 | 380 × 346 at (796, 525) |
| 390 | **resting (editing)**, HEAD vs fixed | **0** | — |
| 390 | failed, HEAD vs fixed | 4.31394e+08 | **374 × 266 at (0, 499)** |
| 390 | resting vs failed, fixed — *positive control* | 4.00905e+08 | 358 × 255 at (16, 573) |

**Name the diff box:** at 1280 the whole visible change is a **380 × 259 rectangle at (796, 525)** —
the panel's own width, from the fixed build's top edge down to y = 784. It stops there, and that is
the result stated as a measurement: **the actions row (y 791–827) and the panel's bottom padding are
outside the diff box**, i.e. 닫기 and 다시 시도 are pixel-for-pixel where HEAD put them, and what
changed is that the panel above them no longer shrinks. The 390 box says the same thing (0–765, the
row at 780–828 untouched).

## Console / hydration, and served bytes

The F6 console shim (`console.log/info/warn/error/debug` + `error` + `unhandledrejection`), installed
through `Page.addScriptToEvaluateOnNewDocument` before navigation, on **every** measured load, each
with an injected `console.error` proving the capture is live:

| runtime | output |
|---|---|
| fixed production build (3014), 1280 and 390 | **nothing but the injected control** |
| HEAD production build (3015), 1280 and 390 | **nothing but the injected control** |
| dev (3010), 1280 and 390 | React DevTools notice + `[HMR] connected` + the control — dev noise only |

No hydration warning anywhere, and none was possible: the dialog is client-only (it mounts on a
press), the editing render carries no inline style, and nothing about the pin reaches the server.
Served HTML: `/` is **282,091 bytes on both builds** — byte-for-byte the same size. The CSS chunk
grows **16 B** (`margin-top:auto`).

## Close paths, focus return, the scroll lock

Fixed build (3014), with the HEAD build run identically as the control:

| path | fixed (3014) | HEAD (3015) |
|---|---|---|
| Esc from editing | closed, focus → the footer's 의견 보내기 button | same |
| header × | closed, focus → the entry | same |
| 닫기 from the failed state | closed, focus → the entry | same |
| backdrop tap at 390 | closed, focus → the entry | same |
| `document.body.style.overflow` at 390 | `hidden` while open, `(none)` after | same |

The only difference between the two columns is the failed panel's rect at the moment 닫기 was
pressed — `[796, 526, 380, 318.016]` on the fixed build, `[796, 602.453, 380, 241.563]` on HEAD.

## The send button: no code, and the numbers Q9 carries

F6's precondition — the ghost twin is resting-identical **only where the resting label is the widest
state** — fails here, and by a wider margin than R1 recorded, because the slot takes **three**
labels, not two:

| label | width, 1280 | width, 390 | left edge, 1280 |
|---|---|---|---|
| 보내기 (resting) | **71.266** | 71.266 | 1087.734 |
| 보내는 중입니다 (sending) | **124.734** | 124.734 | 1034.266 (**53.468 px left**) |
| 다시 시도 (failed) | **87.469** | 87.469 | 1071.531 |

The right edge is fixed at 1159 (374 at 390) — the row is `justify-content: flex-end` — so the label
travels leftward and 닫기 travels with it (`[1026.891 …]` editing → `[1010.688 …]` failed,
**16.203 px**). A ghost reserving the widest state would make the resting 보내기 button **124.734 px**
(+53.468) in a signed dialog, at both viewports. Not implemented; **Q9** on `## Operator Questions`
carries it, with the note that it is the same decision as **Q7** one surface over.

## What was sent, and where it went

**8 real 의견 messages** were sent — and the plan's premise about them needs correcting for the
record: `src/mijual/web/vocky.py` `submit()` **forwards** the message to vocky's ingest endpoint and
「touches no table」, so these are 8 rows **in the vocky project**, created through the **dev** API on
`127.0.0.1:8010` (all three ports proxy there), and **nothing was written in Mijual's database**.
Every message was one short line beginning 「[테스트] P12.F7」. Receipts:

| # | port | viewport | 접수 번호 |
|---|---|---|---|
| 1 | 3015 | 1280 | `6ede86a7-0e05-4e1f-a2f3-dfcfa9645482` |
| 2 | 3015 | 390 | `ab5fb9ff-ef1b-4380-8ffd-c4241e8f25dd` |
| 3 | 3014 | 1280 | `f99bfaec-03d1-478b-b8c4-c614bfa89c6a` |
| 4 | 3014 | 390 | `731557ed-1070-425e-8300-b4eb792610f6` |
| 5 | 3010 (dev) | 1280 | `23db8d0f-6b61-4c26-a37d-b0cf92365ba9` |
| 6 | 3010 (dev) | 390 | `43070207-1208-4934-979b-7de793278c30` |
| 7 | 3015 | 1280 (sent-state capture) | `3ea079ad-5d93-47b6-95b2-fedfa0cf30ee` |
| 8 | 3014 | 1280 (sent-state capture) | `339ae1be-361f-4627-9af7-adb8a0025820` |

Every **failed**-state run wrote nothing at all: the POST was blocked at the network layer with
`Network.enable` + `Network.setBlockedURLs(['*/api/feedback', '*api/feedback*'])`, so the request
never left the browser. That is also why the failure is deterministic and instant rather than an
8 s `TIMEOUT_MS` abort.

## Instrument

**Aside `repl` over Bash, `aside repl --account u2`** (profile 「claude2」) — never `u0`, never
`aside account use`. One job per invocation, each opening its own tab. The phase's recorded seam held
in every particular (CDP through `page._sendToTarget`, the init script before `Page.navigate`, one
argument to `page.evaluate`, no top-level `return`, no `page.waitForTimeout`, the script passed from
a shell **variable**, rect keys over **visible** elements only, one screenshot per invocation
resolved inside that invocation's session directory). Three notes for the next browser slice, all
small:

- **`Network.setBlockedURLs` is the cheap deterministic failure.** `Fetch.enable` + `Fetch.failRequest`
  needs CDP **events** (`Fetch.requestPaused`), which this surface does not deliver to the script;
  `Network.enable` + `Network.setBlockedURLs` is two commands, no events, and fails the POST before
  it leaves the browser.
- **Next's own dev-tools badge (`<nextjs-portal>`) eats clicks in dev at 390.** It sits over the
  footer's bottom-left corner, which is exactly where the 의견 보내기 entry is at that width, and a
  CDP mouse press lands on the badge instead. `document.querySelectorAll('nextjs-portal').forEach(e => e.remove())`
  before the first press; it does not exist on a production build.
- **A text-matching `boxOf` must skip zero-sized elements.** The nav sheet's 의견 보내기 row is in the
  DOM at every width (0 × 0 while the sheet is closed) and matched *before* the footer's, so the
  first press went to `(0, 0)` and opened nothing.

## Hygiene

Production was **never visited**; every request went to `127.0.0.1`. Both fresh build copies live
under the session scratchpad, outside the repo, and **3014 / 3015 are stopped** with their ports
confirmed closed. No account was created or deleted. No test file added, nothing committed, no
workflow state command run other than `validate`. `make stack-status` as found.

## Notebook

`phase.md` was edited, not appended to: one `## Decisions` line for this slice, **Q9** appended to
`## Operator Questions`, one `## Doc impact` line, `## Now` rewritten. No note was added to
`## Notes for later slices` — `P12.S2` needs nothing from this slice (frontend-only, no env var, no
new file), and the three instrument notes above belong to the qa doc's seam rather than to every
remaining dispatch.

**Doc impact line, as appended:**

> - frontend.md: Surfaces / 의견 보내기 — the dialog now keeps **one body height** from the press of
>   보내기 (or 다시 시도) onward. `Feedback.tsx` reads the rendered `.body` height in the submit
>   handler, in the same handler call as the phase change, and every later body (sending / sent /
>   failed) renders it as an inline **`min-height`** — never a `height`, so a failed body carrying a
>   long message still grows; the editing body renders no inline style, so the resting dialog is
>   unchanged. `Feedback.module.css` pins `.actions` to the bottom of a pinned body
>   (`margin-top: auto`, inert everywhere else), so 닫기 / 다시 시도 land where 보내기 was. What used
>   to drop the anchored panel's top edge 75.45 px on 접수 (76.45 on 실패) and jump the ≤480 sheet's
>   top edge 91.46 px (92.45) now moves nothing. **닫기 still disappears while sending, as signed** —
>   its unmount was measured and moves nothing else. The 보내기 ↔ 보내는 중입니다 button's
>   71.27 → 124.73 px growth is unchanged and is Q9 (P12.F7)
