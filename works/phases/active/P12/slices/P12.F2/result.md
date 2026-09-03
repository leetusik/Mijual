# P12.F2 — result

- **status:** done
- **summary:** The AI 질문 launcher is now rendered by the server — `AskSurface` asks for
  `useDesktop(true)` and `Launcher.module.css` carries a `(max-width: 767px) { display: none }`
  guard for the pre-hydration window only — so on the 9 non-`/ask` routes at 1280 it is in the DOM
  **49–87 ms before FCP** in dev and in a fresh local production build, where the HEAD control
  still inserts it **+5.5 to +106 ms after** it. The signed ≤767 end state is untouched: after
  hydration the launcher is **absent from the DOM** at 390 and 767, before hydration it is
  `display: none` and 14 real Tab presses never reach it, and the resting / hover / open corner is
  pixel-identical to HEAD (`AE = 0`).
- **files_changed:**
  - `/Users/sugang/projects/personal/Mijual/frontend/components/ask/useAsk.ts`
  - `/Users/sugang/projects/personal/Mijual/frontend/components/ask/AskSurface.tsx`
  - `/Users/sugang/projects/personal/Mijual/frontend/components/ask/Launcher.module.css`
  - `/Users/sugang/projects/personal/Mijual/works/phases/active/P12/phase.md`
  - `/Users/sugang/projects/personal/Mijual/works/phases/active/P12/slices/P12.F2/result.md`
- **validation:**
  - `cd frontend && npm run typecheck` — pass (twice: after the edit and at the end)
  - `cd frontend && npm run smoke` — pass, 22/22 (twice)
  - `NEXT_PUBLIC_SITE_URL=https://jujutower.com MIJUAL_API_ORIGIN=http://127.0.0.1:8010 npm run build`
    in a fresh copy — exit 0, **0 warnings**, route table byte-identical to the HEAD control build
  - markup greps, 11 routes × 3 origins (dev 3010, fixed build 3014, HEAD build 3015) — pass
  - Aside `--account u2` late-insert sweep, 10 routes × {dev, fixed build, HEAD control build},
    1280 — pass (table below)
  - Aside pre/post-hydration reads at 390 / 767 / 768 / 1280, dev and fixed build — pass
  - Aside real-Tab sweeps at 390, pre- and post-hydration — pass, launcher never focused
  - resize sweep 1280 → 768 → 767 → 768 → 767 → 390 → 768 — pass, existence toggles at the line
  - open/close/inert function check at 1280, fixed vs HEAD — **byte-identical** four-state reading
  - `QuestionStrip` chip press at 1280 (opens widget) and 390 (routes to `/ask`), fixed vs HEAD — pass
  - resting / hover / open corner screenshots, fixed build vs HEAD build — `AE = 0` ×3, with two
    positive controls
  - console capture at 390 and 1280 on both builds — **no hydration warning, no error, empty log**
  - `python3 scripts/workflow.py validate` — passed (pre-existing warnings only; quoted below)
- **deviations:** two, both about the *instrument*, none about the change — see *Deviations*.
- **doc_impact:** one line appended to `phase.md` (`frontend.md`) — quoted under *Notebook*.

---

## What changed

Ruling 2 of `phase.md`, implemented as written. Three files, no DOM change, no launcher number
touched, `AskLauncher.tsx` and `QuestionStrip.tsx` not edited at all.

1. **`components/ask/useAsk.ts`** — `useDesktop(initial = false)`; `useState(initial)`, the effect
   unchanged. The header's "server-rendered as `false` … would flash a launcher onto a phone"
   paragraph is replaced by the two callers' opposite defaults and by where the flash guard went.
2. **`components/ask/Launcher.module.css`** — a new `@media (max-width: 767px) { .launcher {
   display: none } }` immediately after `.launcher`, with a comment saying it is the pre-hydration
   guard *only*, why `display: none` (and not `visibility` or opacity) is what makes it safe, and
   why it must not be deleted "because the component already handles the width". No other rule in
   the file moved — frame, tail, mark, hover, focus-visible, open state, reduced-motion untouched.
3. **`components/ask/AskSurface.tsx`** — `useDesktop(true)` with a three-line inline reason, and
   the header's first rule rewritten as *after hydration: not rendered / before hydration: not
   painted*, naming `P12.F2` and answering the original tab-order argument.

`QuestionStrip` keeps its bare `useDesktop()` — its value is read inside the press handler, so a
390 chip press during the effect window must still route to `/ask`, which the `false` default is
what guarantees.

## The numbers

Probe: the phase's recorded seam — `Page.addScriptToEvaluateOnNewDocument` installed **before**
`goto`, a `MutationObserver` on `document` (never `documentElement`), FCP and CLS from buffered
`PerformanceObserver`s, one route per `aside repl` invocation, `Emulation.setDeviceMetricsOverride`
for the 1280 viewport. `delta` = (time `button[class*="__launcher"]` entered the DOM) − FCP, in ms.
**Negative is the fix.** The "before" column is a **second production build from HEAD (`4730c41`)
served on 3015** — F1's measurement seam, never a `git stash` sweep against `next dev`.

### Launcher, 1280, signed out

| Route | dev after (3010) | prod-build after (3014) | HEAD control (3015) | R1's dev "before" |
|---|---|---|---|---|
| `/` | **−60.7** (fcp 424) | **−80.7** (fcp 272) | +106.2 | +288 |
| `/stocks` | **−53.1** | **−61.6** | −8.4 | +46 |
| `/stocks?q=zzz` | **−57.0** | **−49.5** | +43.1 | +67 |
| `/stocks/00547510` | **−87.3** | **−67.7** | +10.8 | +46 |
| `/portfolio` | **−67.7** | **−70.1** | +21.2 | +51 |
| `/portfolio/notifications` → `/auth/login` | **−48.2** | **−58.2** | +44.4 | +44 |
| `/events/20260806000329` | **−68.6** | **−59.2** | +10.4 | +49 |
| `/auth/login` | **−75.2** | **−70.5** | +7.3 | +53 |
| `/auth/reset` → `/auth/login` | **−69.4** | **−56.7** | +5.5 | +69 |
| `/ask` | **no launcher** | **no launcher** | no launcher | — (by design) |

9/9 non-`/ask` routes, both runtimes: the launcher is in the DOM before first contentful paint.
Its rect is `[1188, 726, 68, 50]` in **every** reading on every port — R1's F1 rect exactly, and
`[676, 770, 68, 50]` at 768 / `[1348, 826, 68, 50]` in the unemulated 1440 window, i.e. the same
24px-inset 68×50 corner box in each. The account slot's own delta (F1's fix) is negative on
**both** sides — the control proves only the launcher moved.

`/portfolio/notifications` and `/auth/reset` answer **307 → `/auth/login`** for an anonymous
reader, on the fixed build and at HEAD alike, so those two rows are the login page's numbers in
both columns. Nothing there changed.

### CLS

0 on every route on both production builds, and 0 in dev except `/` (0.0001) and the event page
(0.00171). The event-page value is **not** this change: the layout-shift sources are
`SPAN.mono …__agentWhen` narrowing 161.92 → 149.47 px and `DIV.…__cd` narrowing 266.5 → 263.06 —
the IBM Plex Mono metric mismatch, i.e. R1 F5 / `P12.F9`. It reads 0.00171 deterministically over
three runs and no launcher node appears in any shift source. A `position: fixed` element cannot
shift layout in the first place.

### The pre-hydration window, measured directly

Blocking `*/_next/static/chunks/*.js` at the CDP layer (**JS only** — the CSS lives under the same
prefix, so blocking `chunks/*` blocks the stylesheets too and produces a meaningless unstyled read)
freezes the page in exactly the state a reader sees before React runs:

| Viewport | in DOM | computed `display` | rect | in tab order |
|---|---|---|---|---|
| 390 | yes | **`none`** | 0×0 | **no** |
| 767 | yes | **`none`** | 0×0 | **no** |
| 768 | yes | `grid` | `[676, 770, 68, 50]` | yes |
| 1280 | yes | `grid` | `[1188, 770, 68, 50]` | yes |

Identical on dev 3010 and on the fixed production build 3014. After hydration, same page:
**390 and 767 → the launcher is not in the DOM at all** (`document.querySelector` → `null`), 768
and 1280 → present. That is the signed rule end to end: not painted before, not rendered after.

Visual proof: with JS blocked at 390 the bottom-right corner is empty (a cropped
`f2-corner-390-pre.png`), and at 1280 the same crop shows the 68×50 frame with its sparkle and
tail already painted (`f2-corner-1280-pre.png`) — the launcher is in the *first* paint.

### Tab order — real Tab presses, not a computed-style guess

`Input.dispatchKeyEvent` Tab at 390 on `/stocks`, 45 presses **after** hydration and 14 **before**
it (JS blocked, launcher in the DOM with `display: none`). Both give the same 9-stop cycle:

`brand → 메뉴 → ← 관제 현황판 → 종목 input → 조회 → leetusik@gmail.com → 010-3772-9916 →
의견 보내기 → AI 질문(footer link) → body → (repeat)`

No stop's class ever contains `__launcher`. (The last stop is `Footer-module__actionAsk`, the
footer's own 「AI 질문」 link — a different, pre-existing control; a first grep of mine matched its
label and had to be tightened to the class.) This is the substance of the signed argument — "a
launcher merely not painted would still be in the tab order" — measured and answered.

### Resize toggles existence exactly as today

One page session, `/stocks`, metrics stepped `1280 → 768 → 767 → 768 → 767 → 390 → 768`:
present `[1188,770,68,50]` → present `[676,770,68,50]` → **absent** → present → **absent** →
absent → present. The media-query effect still owns existence.

### Function, 1280 — byte-identical to HEAD

| State | fixed build 3014 | HEAD build 3015 |
|---|---|---|
| rest | launcher present, `inert` false, `data-open="false"`, mark opacity 1, × 0 | same |
| focused (`.focus()`) | `activeElement` = the launcher button | same |
| Enter pressed | widget open, launcher **`inert` true**, `data-open="true"`, mark 0, × 1 | same |
| widget × clicked | widget gone, launcher back to `inert` false / `data-open="false"` / mark 1 | same |

`QuestionStrip`, event page, both builds: at **1280** a chip press opens the widget in place
(`location.pathname` unchanged, `section[class*="__widget"]` present); at **390** it routes to
**`/ask`** with no widget. The `false` default is preserved in behaviour, not only in the source.

One thing the plan expected that the product does not do, on **either** side: after the widget
closes, focus does **not** return to the launcher — `document.activeElement` is `BODY`, identically
at HEAD. Pre-existing, unchanged by this slice, and filed as **Q6** on the phase's operator-question
list rather than "improved" here.

### Resting layout — `AE = 0`

Full-window PNGs of `/stocks` (unemulated 1440 window, so the corner is captured at native scale),
fixed build 3014 vs HEAD build 3015, same browser, same window, three states:

- **rest** → `AE = 0`; **hover** (real `Input.dispatchMouseEvent` over the launcher centre) →
  `AE = 0`; **open** (real click, pointer moved away) → `AE = 0`
- positive controls, same pipeline: 3014 rest vs 3014 open → **3.887e+08**; 3014 rest vs 3014
  hover → **8.581e+06**. The zeros are measured zeros and the hover actually fired.
- the launcher box reads `[1348, 826, 68, 50]` on both ports.

### Markup

`Launcher-module__<hash>__launcher` occurrences in the served HTML (anonymous):

| Origin | `/` `/stocks` `/stocks?q=zzz` `/stocks/00547510` `/portfolio` `/events/…` `/auth/login` | `/ask` | `/ops` | the two 307s |
|---|---|---|---|---|
| dev 3010 | 1 each | 0 | 0 | redirect body |
| fixed build 3014 | 1 each | 0 | 0 | redirect body; **1** when followed |
| HEAD build 3015 | **0** each | 0 | 0 | **0** when followed |

The served HTML grows by **290 bytes** per page (26,214 vs 25,924 on `/stocks`) — the launcher's
markup. `/ops` contains no ask markup at all, before or after.

## Deviations from `plan.md`

1. **The class name in the plan's curl check does not exist verbatim.** The plan says the markup
   "contains `Launcher-module__launcher`"; the emitted CSS-module class carries a build hash in the
   middle — `Launcher-module__3_folq__launcher` — so the grep used is
   `Launcher-module__[a-z0-9_]*__launcher`, and every browser selector is
   `button[class*="__launcher"]`. Nothing about the check's meaning changed.
2. **The pre-hydration screenshot is taken with the JS chunks blocked at the CDP layer, not "as
   early as the repl allows after `goto`".** Racing a `goto` is not reproducible; blocking
   `*/_next/static/chunks/*.js` holds the page in the pre-hydration state indefinitely and is a
   strictly stronger read (it also lets real Tab presses be dispatched in that state, which a race
   would not). Two instrument facts came out of it and are recorded above: blocking `chunks/*`
   rather than `chunks/*.js` also blocks the stylesheets, and `Browser.setWindowBounds` is accepted
   but does **not** resize Aside's window (`innerWidth` stayed 1440), so a real-390-pixel window
   screenshot is not available — the 390 evidence is the emulated-viewport capture cropped to
   390×844 plus the rect/`display`/tab-order reads.

Not a deviation: the 412×915 cold-cache throttled profile was **not** run. The shared bar asks for
it "for anything font- or load-related"; this change is neither, and at 412 the launcher is not
rendered at all (≤767) — the 390 and 767 readings above are the phone evidence.

## Instrument

**Aside `repl` over Bash, `aside repl --account u2`** (profile 「claude2」) — never `u0`, never
`aside account use`. Each invocation opened its own tab (`openTab`) and did its whole job in one
script, per the phase's corrected preamble. Confirmations and additions to the recorded seam:

- `page._sendToTarget` reached `Emulation.setDeviceMetricsOverride`, `Network.enable` /
  `Network.setBlockedURLs`, `Input.dispatchKeyEvent`, `Input.dispatchMouseEvent`,
  `Browser.getWindowForTarget` and `Page.addScriptToEvaluateOnNewDocument` without trouble;
- **`Browser.setWindowBounds` returns success and changes nothing** — the window stays 1440×900,
  so `page.screenshot()` cannot be given a real narrow viewport. Under
  `setDeviceMetricsOverride` the capture tiles the emulated viewport across the real window; the
  leftmost tile is a faithful 390×844 render and cropping it is the way to a phone screenshot;
- zsh does **not** word-split an unquoted `$ROUTES` variable — a route loop must list its routes
  literally or use an array, or the whole list is passed as one URL (caught by a nonsense
  `location.pathname` in the first sweep).

## Hygiene

No account was needed — every check is signed-out, so nothing was created or deleted. **Production
was never touched**; every request was to `127.0.0.1`. Both scratch servers (3014 fixed build, 3015
HEAD control) were stopped and their ports confirmed closed; only the dev stack's 3010 is listening.
The dev stack is exactly as found (`make stack-status`: postgres up 4 days, api pid 60158, web pid
61423 — the same pids as at the start). The build copies live under the session scratchpad, outside
the repo; nothing was built into the working tree's `.next`. The HEAD control build was the copy
`P12.F1` left behind, re-verified first: it differs from the working tree in **exactly** the three
files this slice edits, so it is `4730c41` — the same reuse-after-`diff` `P12.R1` did with `P12.S1`'s
build.

## Workflow validation

```
python3 scripts/workflow.py validate
```
passed, with the three pre-existing warnings only: P4's `consolidation_owed`, `stale_docs=product`,
and `oversized_doc_sections`.

## Notebook

`phase.md` edited per the plan: one `## Decisions` line (the launcher is server-rendered behind the
≤767 CSS guard and unmounted after hydration, with the seam and the after-numbers), one
`## Doc impact` line (`frontend.md`), one new `## Operator Questions` entry (**Q6**, the focus that
does not return to the launcher — observed, pre-existing, identical at HEAD), the `for P12.F2` note
removed, and a rewritten `## Now`. The shared bar and F1's measurement-seams note were left in
place — seven fix slices still need them. No `for P12.S2` note was added: the release learns nothing
new from this slice (frontend-only, no env var, no new file; the only side effect is 290 bytes more
HTML per page).
