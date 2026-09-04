# P12.F8 — result

- **status:** done
- **summary:** The 검색 불일치 sentence now keeps its **box** while the field is being re-typed —
  the `<p>` renders whenever `missed && submitted !== ""` and takes `.noMatchStale`
  (`visibility: hidden`) while `typedText !== submitted`. The 30.6 px lift at 1280 / 49.19 px at 390
  (67.78 px on a three-line box), and the `layout-shift` entries that came with them, become **zero
  elements moved and no `layout-shift` entry at all** in dev and a fresh production build against a
  HEAD control; the sentence still leaves the AX tree and hit-testing on the first differing
  keystroke, and comes back in the same rect when the submitted text is typed back.
- **files_changed:**
  - `frontend/components/lookup/LookupHeader.tsx`
  - `frontend/components/lookup/Lookup.module.css`
  - `works/phases/active/P12/slices/P12.F8/result.md`
  - `works/phases/active/P12/phase.md`
- **validation:**
  - `cd frontend && npm run typecheck` — pass (no output)
  - `cd frontend && npm run smoke` — pass (22/22)
  - `npm run build` in a fresh copy outside the repo (`NEXT_PUBLIC_SITE_URL=https://jujutower.com`) —
    pass, **no warnings** (`grep -i "warn\|error"` on the log: empty), for the fixed **and** the HEAD
    control copy
  - Aside `repl --account u2`, `/stocks?q=<miss>`, **1280 + 390**, dev (3010) + fixed production
    build (3014) against a HEAD production build (3015): one real keystroke over CDP
    `Input.insertText`, rects sampled every `requestAnimationFrame`, plus the type-back, the
    candidate list, a new miss submit, a hit submit, the AX tree, hit-testing and resting `AE = 0`
    with a live positive control — pass (tables below)
  - `python3 scripts/workflow.py validate` — pass (pre-existing P4 consolidation / stale-doc /
    oversized-section warnings only)
- **deviations:** one, in the wrap query only. The plan's suggested 20-character miss produces the
  **same** two-line box as `zzz` at 390 (37.188 px — the query sits on the first line and the tail
  copy wraps identically), so it proved nothing extra; I kept that run and added a **60-character**
  miss, which is the first one that makes the sentence **three** lines (55.781 px). Both are in the
  table. Nothing else departs from the plan.
- **doc_impact:** `frontend.md`: Surfaces / 조회 entry page (`/stocks`) — the 검색 불일치 sentence's
  box outlives the sentence until the next submit; the sentence itself still dies on the first
  differing keystroke (R11 §7 unchanged) (P12.F8).

## The change

Two files, both named in `DECOMP2`'s cut table, and no third.

`LookupHeader.tsx` — the `<p className={styles.noMatch} role="status">` is now rendered whenever
`missed && submitted !== ""` (the same condition minus the `typedText` clause, i.e. **exactly** what
the server already renders), and carries `styles.noMatchStale` beside `styles.noMatch` while
`typedText !== submitted`. The wrapper's `onInput`, the `target.name === "q"` filter, the seeding of
`typedText` from the submitted query and the `noMatchKo(submitted)` call are untouched; `SearchRow`,
`copy.ts` and `app/stocks/page.tsx` were not opened for edit. The doc comment's two sentences about
the removal were rewritten to describe the new shape and to record why the candidates are unaffected.

`Lookup.module.css` — one new rule, `.noMatchStale { visibility: hidden }`, with the reason in a
comment: no constant, no transition, no copy change.

Because `typedText` is seeded with `submitted`, the **first client render is byte-identical to the
server's** — the stale class can only appear after a keystroke, which is why nothing here can
produce a hydration mismatch (and none was logged in any dev load).

## Before / after — the keystroke

`/stocks?q=<miss>`, field focused, caret at end, one CDP `Input.insertText("a")` fired 150 ms into a
`requestAnimationFrame` sampling window (54–55 frames per run). The rect key is the phase's
insertion-robust `tag.classes` + occurrence index over **visible** elements; a key is counted as
"moved" if it has more than one distinct rect **or** is absent from some frames.

| runtime | vp | miss query | sentence box | keys moved | dy below the line | doc height | `layout-shift` |
|---|---|---|---|---|---|---|---|
| HEAD 3015 | 1280 | `zzz` | 18.594 (1 line) | **25** | **−30.594** | 800 → 800 | **0.00299** (`ri:false`) |
| fixed 3014 | 1280 | `zzz` | 18.594 | **0** | 0 | 800 | **none** |
| dev 3010 | 1280 | `zzz` | 18.594 | **0** | 0 | 800 | none |
| HEAD 3015 | 390 | `zzz` | 37.188 (2 lines) | **45** | **−49.187** | 911 → 862 | **0.03213** (`ri:false`) |
| fixed 3014 | 390 | `zzz` | 37.188 | **0** | 0 | 911 | none |
| dev 3010 | 390 | `zzz` | 37.188 | **0** | 0 | 911 | none |
| HEAD 3015 | 390 | 20 × `z` | 37.188 (2 lines) | 45 | −49.187 | 911 → 862 | 0.03213 |
| fixed 3014 | 390 | 20 × `z` | 37.188 | **0** | 0 | 911 | none |
| HEAD 3015 | 390 | 60 × `z` | 55.781 (3 lines) | **51** | **−67.781** | 930 → 862 | **0.04678** |
| fixed 3014 | 390 | 60 × `z` | 55.781 | **0** | 0 | 930 | none |

"Keys moved = 0" is literal on the fixed build: the *only* two keys that are not in every frame are
the sentence's own two class signatures — `p.…__noMatch#1` (frames before the keystroke) and
`p.…__noMatch.…__noMatchStale#1` (frames after it) — and **both carry the same single rect string**
(`354,254.922,572,18.594` at 1280; `16,254.922,358,37.188` at 390; `16,254.922,364.172,55.781` for
the three-line box). The key changes because the class list changes, not because anything moved.

The HEAD control reproduces R1 F7 exactly at 1280 — every element the finding named moves by
−30.594 px:

| element | HEAD before | HEAD after |
|---|---|---|
| `section.CraftPanel…__panel#1` | `354, 289.516, 572, 86.438` | `354, **258.922**, 572, 86.438` |
| `div.Lookup…__empty#1` | `355, 290.516, 570, 84.438` | `355, **259.922**, 570, 84.438` |
| `div.Lookup…__watch#1` | `375, 308.516, 530, 19.391` | `375, **277.922**, 530, 19.391` |
| `RightsChip` r1 / r2 / r3 | `…, 308.516, …` | `…, **277.922**, …` |
| 집계 범위 `section.Lookup…__section#1` | `354, 391.953, 572, 74.094` | `354, **361.359**, 572, 74.094` |
| `p.Lookup…__provenance#1` | `354, 482.047, 572, 15.5` | `354, **451.453**, 572, 15.5` |

At 390 the same set moves −49.187 (`.entry` 172.109 → 122.922) and the document shortens 911 → 862;
on the three-line query it is −67.781 (930 → 862). On the fixed build and in dev every one of those
rects has **one** distinct value across the whole window, and the document height never changes.

## The sequence: keystroke → type the query back → open the candidates

One 4-second sampling window per run, 240–241 frames, at both viewports.

| | fixed 3014 | HEAD 3015 |
|---|---|---|
| after the keystroke | `stale: true`, `visibility: hidden`, rect **unchanged**, page unmoved | `<p>` **gone**, page up 30.594 (1280) / 49.187 (390) |
| after typing `zzz` back | `stale: false`, `visible`, **same rect**, page unmoved | `<p>` back, page down again |
| after typing `계` (candidates open) | `stale: true`, `hidden`, same rect, page unmoved | `<p>` gone, page up again |
| keys moved over the whole sequence | **6** — the 2 sentence signatures (one rect each) + the 4 listbox elements (one rect each, present only while open) | **31**, all bouncing between the two y positions |
| `layout-shift` entries | **none** | **3 ×** 0.00299 @1280 / **3 ×** 0.03213 @390, all `ri:false` |

**The candidate list opens in exactly the same place on both builds** — `ul.…__listbox#1`
`[354, 242.922, 478.391, 41]` at 1280 and `[16, 242.922, 284.391, 45]` at 390, one option, rect
identical on 3014 and 3015. That is the measured form of the plan's point: `SearchRow.module.css`
L34 makes the panel `position: absolute`, so a reserved box under the row changes nothing about
where the candidates open, and R11's 「into the space it leaves」 was never geometric.

## The sentence is still gone in every sense that is not geometry

| check (fixed 3014, 1280) | visible state | stale state |
|---|---|---|
| in the DOM | yes | **yes** (this is the whole change) |
| `getComputedStyle().visibility` | `visible` | **`hidden`** |
| AX tree (`Accessibility.getFullAXTree`, filtered by name) | `StaticText` + `InlineTextBox` 「‘zzz’와/과 일치하는 종목이 없습니다 —」, `ignored: false` | **0 matching nodes** |
| AX tree on HEAD, same moment | same two nodes | **0 matching nodes** (unmounted) |
| `document.elementFromPoint` over the box | the `<p>` itself | **`div.…__entry`** — the wrapper behind it |
| `role` | `status` (unchanged) | `status` (unchanged) |

So a reader using assistive technology, or a pointer, sees precisely what an unmount gave them: the
AX-tree result is **identical to HEAD's** in both states, which is the comparison that matters. What
survives is a 572 × 18.594 px (or 358 × 37.188) piece of empty page that keeps everything below it
where the reader last saw it.

## Submits still behave exactly as before

| step | fixed 3014 | HEAD 3015 |
|---|---|---|
| type `qqq` + Enter (no candidates → plain GET) | → `/stocks?q=qqq`, sentence **visible**, `stale: false`, rect `[354, 254.922, 572, 18.594]` / `[16, 254.922, 358, 37.188]`, text 「‘qqq’와/과 …」 | identical |
| type `계양전기` + Enter (1 candidate, exact name → first Enter goes) | → `/stocks/00102618`, `h1` 「계양전기」 | identical |

One `layout-shift` entry appears on the **resolved stock page** at 390 after that navigation on both
builds (`ri: true`; fixed 0.01589, HEAD 0.03451) — post-navigation, `hadRecentInput`, on
`/stocks/[corp_code]`, i.e. P12.F4's surface and not this one; it is smaller on the fixed build and
was not touched here.

## Resting layout — `AE = 0`, with a live positive control

Viewport captures at rest (blurred, `<nextjs-portal>` removed), cropped to the emulated tile minus
the 8 px macOS overlay-scrollbar column: 1272 × 800 at 1280, 382 × 844 at 390.

| comparison | AE |
|---|---|
| `/stocks?q=zzz` @1280, fixed vs HEAD | **0** |
| `/stocks?q=zzz` @390, fixed vs HEAD | **0** |
| `/stocks` (no query) @1280, fixed vs HEAD | **0** |
| `/stocks` (no query) @390, fixed vs HEAD | **0** |
| **positive control** — miss page vs no-query page, same build @1280 | 4.37266e+08 |
| **positive control** — miss page vs no-query page, same build @390 | 5.66863e+08 |

(The control is what proves the zeros are measurements and not a stuck comparison. The served HTML
is also identical: `curl` of `/stocks?q=zzz` on 3014 and 3015 returns the same
`<p class="Lookup-module__uHmraa__noMatch" role="status">` line byte for byte — the resting miss page
is unchanged, which is what RESPECT THE DESIGN asks for here.)

## Console / hydration

The shim (installed through `Page.addScriptToEvaluateOnNewDocument` before navigation) was **proven
live on every measured load** by an injected `console.error("__probe_live__")` in the init script.

| runtime | captured output |
|---|---|
| fixed production build 3014, 1280 + 390, all runs | `["error: __probe_live__"]` — **nothing else** |
| HEAD production build 3015, 1280 + 390, all runs | `["error: __probe_live__"]` — nothing else |
| dev 3010, 1280 + 390 | the probe plus exactly two dev-only lines: the React DevTools notice and `[HMR] connected` — **no hydration warning** |

## The two shapes considered and rejected

- **A `min-height` wrapper around the sentence.** More markup for the same box, an element the record
  never drew, and a measured constant that would have to be *three* constants (18.594 / 37.188 /
  55.781 px all occur, by viewport and by how the query wraps) — where the real element already
  produces each of them for free. Family D's own lesson from F7: prefer the box that *is* the
  element.
- **`opacity: 0`.** It keeps the sentence **in the AX tree and under the pointer** — measured on this
  very page: `elementFromPoint` over the box returns the `<p>` while it is merely transparent, and
  the AX nodes stay `ignored: false`. That would leave a screen reader announcing a sentence about a
  query nobody is typing any more, which is the exact defect R11 §7 legislated against. `visibility`
  reproduces the unmount in every register except layout, which is the one register we wanted back.

## Instrument

**Aside**, `aside repl --account u2` (profile 「claude2」) — never `u0`, never `aside account use`.
The phase's recorded seam held with no new surprises: CDP through `page._sendToTarget`, the init
script installed once per tab before `page.goto`, `page.evaluate` with a single argument,
`new Promise(r => setTimeout(r, ms))` for waits, one route per invocation, script passed from a shell
variable, and one `page.screenshot()` per invocation copied out of that invocation's session
directory afterwards. Two small confirmations worth nothing to a later slice on their own: the
capture is 1440 × 900 (the real window) under `Emulation.setDeviceMetricsOverride`, so the emulated
tile is cropped from the top-left as F6 recorded; and `Input.insertText` on a focused uncontrolled
input fires the native bubbling `input` event that `LookupHeader`'s wrapper listens for, which is
what made a real keystroke measurable at all.

## Hygiene

Production was **never visited** — every request went to `127.0.0.1`. Both fresh build copies live
under the session scratchpad outside the repo, and **3014 / 3015 are stopped** with their ports
confirmed closed. No account was created, deleted or signed into; no writes anywhere. No test file
added, nothing committed, no workflow state command run other than `validate`. `make stack-status`
is as found (same api/web pids, dev still on 3010).

## Notebook

`phase.md` was edited, not appended to: one `## Decisions` line for this slice, one `## Doc impact`
line, `## Now` rewritten. Nothing was added to `## Notes for later slices` — `P12.S2` needs nothing
from this slice (frontend-only, two files, no env var, no new file, no server involvement), and the
shared bar, F1's seams note and the two `for P12.REVIEW` notes were left untouched. No new operator
question: this fix changes no resting layout, so it raises none of the Q7/Q8/Q9 kind.
