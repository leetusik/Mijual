# Result — P11.S1 (Re-cut the ask citation chip onto the R10 popover anatomy)

- **status:** done
- **summary:** `InlineCitation` is now `Citation.tsx`'s R10 anatomy — a conditionally mounted,
  absolutely positioned popover in place of the always-mounted `display: grid` panel — so ask
  citation chips stop forcing line breaks: a sentence resting on two or three 근거 now renders on one
  line with the chips side by side after its period, in all three signed placements, on the page and
  in the widget, at desktop and 390, in dev and in the production build.
- **files_changed:**
  - `frontend/components/ask/InlineCitation.tsx`
  - `frontend/components/ask/Ask.module.css`
  - `frontend/components/ask/Blocks.module.css`
  - `works/phases/active/P11/phase.md`
  - `works/phases/active/P11/slices/P11.S1/result.md`
- **validation:**
  - `cd frontend && npm run typecheck` — **pass** (`tsc --noEmit`, no output)
  - `cd frontend && npm run build` — **pass**, `✓ Compiled successfully`, 19 route entries
  - `cd frontend && npm run smoke` — **pass**, `tests 22 / pass 22 / fail 0`
  - `python3 scripts/workflow.py validate` — **pass**, `Workflow validation passed.`
  - **real browser, dev** — `make stack-up`, `http://127.0.0.1:3010`, **Google Chrome 152.0.7977.65**
    (`--headless=new`) driven over CDP, 1280×800@2 and 390×844@3 with touch emulation — **pass**, §3–§6
  - **real browser, production** — `cd frontend && npm run build && npm run start`, same origin, same
    Chrome, same scripts — **pass**, and **identical to dev on every measured number**, §7
  - **instrument:** **not Aside.** `aside` is not installed on this machine (`command -v aside` →
    nothing) and no `aside mcp` tools were present in this session, so the workspace fallback applies:
    the same sweep, at the same viewports, in the same manifest runtime, through the real Chrome the
    machine has, driven over the DevTools protocol from a throwaway node harness (no Playwright).
    Every number below was measured in that browser; nothing here is asserted from reading the CSS.
- **deviations:** four, all deliberate and argued below — §2. (1) the popover's ground is **opaque**
  rather than R16's `--surface-inset` (the plan's decision 1, and the one visible change the operator
  should be told about); (2) `fit()` clamps to the **nearest clipping box** in both axes and flips the
  popover above the chip when the widget thread would cut it off (the plan's decision 3, exercised —
  it did clip); (3) the primitive's `×` is **not** adopted, so the close model is 칩 재탭 + outside
  press + Esc (the plan's decision 2); (4) the ≤767 **44px chip target** R16 §2.6 names is still not
  implemented — it never was, the round's own CSS does not implement it either, and closing it is a
  design decision, not a port. Raised as an Operator Question rather than invented — §5.
- **doc_impact:** two lines in `phase.md` — the foreseen `frontend.md` chip-anatomy line refined to
  what actually shipped (conditional mount + absolute popover, the opaque ground, `.row` taking
  `position: relative`, the clip-box fit and the upward flip), and one `qa.md` line for the two
  regression checks this slice's behaviour needs.

---

## 1. What changed

Three files, no props, no backend, no card work.

**`InlineCitation.tsx`** — the always-mounted `.quoteWrap` / `.quoteClip` / `.quotePanel` triple and
its `inert` attribute are gone. The chip's wrap is now a positioning context (`.citationWrap` in
prose, the unchanged `display: contents` `.citationRow` in a row) and the quote is mounted **only
while open**, absolutely positioned, with the primitive's three moving parts ported: `fit()` in the
ref callback that mounts the popover (so the fitted position is the first one painted), the
document-level `mousedown`/`keydown` listeners registered only while open, and Esc returning focus to
the trigger. `.chip` is untouched.

`fit()` differs from the primitive's in two ways, both because this surface clips where the
primitive's never did:

- it measures against **`nearestClip()`** — every scrolling/hidden ancestor intersected with the
  viewport — rather than against `window` alone, because inside the widget the clipping box is the
  440×620 panel's thread, not the screen;
- it adds a **vertical flip** (`data-flip="up"`, offsets in CSS) when the popover would fall past the
  bottom of that box and there is more room above. That is the plan's decision 3, and §4 shows it
  firing on the widget's last answer.

**`Ask.module.css`** — the four retired rules are replaced by `.citationWrap` + `.quotePop` (+ its
`[data-flip="up"]` and `.citationRow > .quotePop` variants). The ≤767 block's full-width `.quotePanel`
rule becomes the popover's mobile geometry (`right: 0; width: calc(100vw - 44px); max-width: 340px`),
which at 390 is the same edge-to-edge width R6 §Mobile asks for. `.quote`'s 180px cap, its thin
scrollbar, `.quoteLink` and `.quoteLinkSolo` are unchanged.

**`Blocks.module.css`** — `.row` takes `position: relative`. That is the whole of the row placement:
`display: contents` on the wrap means the chip's own span generates no box, so the row is what the
popover anchors to, and R16 §2.6's 「행 아래, 블록 전폭」 is preserved while an absolutely positioned
box sizes no grid track — the measured value-column collapse becomes impossible rather than avoided.

## 2. The four deviations

**(1) The ground is opaque.** R16 signed the 인용 블록 as `--surface-inset` + a 2px `--live` left
edge — as an *in-flow* panel, with nothing behind it. As an overlay it lies on the prose, and
`--surface-inset` is `rgba(255,255,255,.08)` (`public/foundations/tokens.css` L51): the sentence would
read straight through the reader's evidence, which is the one thing this affordance exists to make
readable. So the block keeps the **2px `--live` left edge** and the **180px** quote cap and takes the
ground this product already gives everything that floats: `#0e1a15` + 1px `--border-strong` +
`--panel-glow`. That trio is not invented here — it is the widget's own surface, three literals up in
the same file, and `Citation.module.css` uses it for exactly this reason. Measured open, both
runtimes: `background-color: rgb(14, 26, 21)`, `border-top: 1px rgba(163,196,180,.32)`,
`border-left: 2px rgb(95,208,165)`, `z-index: 40`, quote `max-height: 180px`.
**The operator should be told the quote block's fill changed, and why** (§8).

Rejected on the way: keeping `--surface-inset` over a `backdrop-filter`, and stacking an opaque
under-layer behind the translucent token. Both invent a surface the record does not have, and neither
is more faithful than reusing the product's own overlay ground.

**(2) `fit()` clamps to the clipping box, and flips.** The plan asked me to check the widget's
vertical clipping and extend the clamp only if it clips. It clips: opening the last answer's chip in
the 620px widget put the popover past the thread's bottom edge. With the flip, that popover is fully
inside the thread (§4). While measuring I found the same problem horizontally — a prose popover in the
widget was clamped to the *window* and so hung over the widget's own right border — so `nearestClip()`
serves both axes. On `/ask` there is no clipping ancestor, so this is exactly the primitive's viewport
clamp and nothing changed there (measured: identical transforms before and after the change).

**(3) No `×`.** 닫기 = **칩 재탭** is R6-4-signed and survives. The press outside and
Esc-with-focus-return come from R10 §6 with the anatomy — an overlay that cannot be dismissed by
clicking away is worse than the panel it replaced. The primitive's fourth close is not adopted: it
lives in a flex head beside the quote and is a 28px (44px mobile) control, and R6-4 draws no head and
no second control on a 10px chip's block; adding one inside a 440px widget is a design decision, not a
port. The result is a whole close model, not half of one — every pointer close and every keyboard
close is available, and all three were exercised (§3).

**(4) The ≤767 44px chip target is still absent.** R16 §2.6 lists 「≤767 타깃 44px」 under **변경 없음**
— i.e. inherited from R6-4 — and build-prompt check 14 repeats it. It is **not** implemented today and
was not implemented by this slice; the round's own CSS (`r16-ask.css`) does not implement it either
(`.m390` raises `.atx` and `.amore` to 44px and says nothing about `.achip`), so the product matches
the round's code and contradicts the round's prose. Measured at 390 in both runtimes: every chip is
**14 × 16 px**. I did not close it here because both ways of closing it are design changes, not ports:
the primitive's media block (`min-height: 44px; padding: 13px 8px`) would draw R16's 1px chip border
as a 44px-tall box around a 10px number, and an invisible `::after` hit expander on chips that sit
3px apart would make each chip's target swallow its neighbour's — on the very multi-chip sentence this
slice exists to fix. Filed as an Operator Question instead (§5).

## 3. `/ask` page, desktop 1280×800 — the headline case

Reproduced with a turn carrying **5 quotes across 4 sentences**, one sentence resting on **three**
근거 (see §6 for how the data was produced). Every number measured in the browser:

- **a sentence with three chips renders on one line, chips side by side after the period**: the three
  chips sit at `x = 859.1 / 876.1 / 893.1`, all at `y = 730.3` (identical top), 3px apart — the whole
  4-sentence answer is a **3-line paragraph** (`.prose` height 63px at 21px leading), so no chip
  breaks a line before or after itself;
- **`.sentence + .sentence` works again**: computed `margin-left: 3.375px` on every following
  sentence = `0.25em` at this surface's `--text-base`. It was inert while a block box split the
  paragraph;
- **opening a chip moves nothing**: a 40-element snapshot (`.prose`, every `.sentence`, every `.row`,
  `.rowLabel`, `.rowValue`, `.answer`, `.data`, `.calc`, every chip) taken in **document**
  coordinates before and after the click is **byte-identical** for all three placements
  (`moved: []` ×3), and `document.scrollHeight` stays 1129px;
- **close model**: chip re-tap closes; clicking a second chip closes the first (`openChips: ["3"]`,
  one popover in the DOM); a press outside closes (`pops: 0`, no chip left `aria-expanded="true"`);
  focus the chip → Enter opens → Esc closes and `document.activeElement === the chip`;
- **the closed popover is unreachable**: `a[href*="dart"]` = **0** with everything closed, **1** while
  one popover is open. That is what `inert` was buying, now by construction;
- **API-tier chip (no quote)**: opens to the solo `DART 원문 20260724000546 ↗` and nothing else —
  `.quoteLink .quoteLinkSolo`, `margin-top: 0px`, zero quote spans.

**데이터 행 값.** Row `[274, 277.4, 732 × 35.6]`, popover `[274, 313, 732 × 76]` — flush under the row,
the block's full width, 전폭 as R16 draws it. The row's grid tracks are
`283.188px 391.812px 17px` **before and after** opening, and `.rowValue` stays `391.8px` wide: the
collapse R16 measured cannot happen, and every row below keeps its exact position.

**계산 입력.** Same code path (`DataRowLine` inside `.calc`), heavier block border: chips 3 and 5 open
`[274, 416.3, 732 × 96.9]` under their own row inside the calc block, and the 「입력」-marked row (no
chip, by design) is untouched.

## 4. Widget, desktop — including the clipping case

Widget `[816, 156, 440 × 620]`, thread `[817, 202, 438 × 509]`, `overflow-y: auto`, scroll height 875.

- all three placements open **inside** the thread (`insideThread: true` in each case), and the
  thread's `scrollHeight` is **875 before and after every open** — the popover does not extend the
  scroll and does not push the composer;
- `moved: []` for all three placements here too;
- **the last answer's chip flips**: `data-flip="up"`, popover `[867, 451, 380 × 139]`, i.e. 121px
  clear of the thread's bottom edge instead of past it. Screenshot:
  `w-prose-chip-last-sentence-thread-bottom-.png` (scratchpad) shows the quote whole, opaque, with the
  live left edge, above the chip;
- prose popovers are clamped to the thread rather than the window (`translateX(-279px)`), so the
  quote no longer hangs over the widget's right border — that was visible before the §2(2) change.

**≤767 has no widget.** `AskSurface` returns null below 768 (R14 Q-A), verified at 390: no launcher,
no widget. So that cell of the matrix is "must not exist", and it does not.

## 5. `/ask` page, 390×844 (touch)

- **the multi-chip sentence stays on one line**: chips at `x = 32 / 49 / 66`, all `y = 823`;
- **nothing moves** in any of the four cases probed (mid-sentence chip, last chip on a line, row chip,
  calc chip): `moved: []`;
- **프로즈 popover**: 340px (`calc(100vw - 44px)` capped), right-anchored, and slid back inside by
  `fit()` — measured `[8, 436, 340 × 118]`, i.e. entirely on-screen, for a chip that would otherwise
  have started it at −294px;
- **행 popover**: `[18, 343, 354 × 97]` — 354 = 390 − 2×18, the block's own width after it pushes out
  through the answer box's padding. 전폭, as at desktop;
- **44px targets**: the composer's input and 보내기 clear 44px as before; **the chips are 14 × 16 px**
  — see deviation (4). This is unchanged from before the slice, not a regression.

## 6. How the answers under test were produced

Two ways, because one of them alone would have left a hole:

1. **Live, through the real agent** (no interception anywhere): asked 「계양전기 유상증자 조건
   알려줘」 — the question stored turn 103 carries — on `/ask` in dev and again in production. Both
   answers came back as **3 sentences each resting on 2 근거** (`perSentence: [2,2,2]`, 7 chips, 1
   data row), which is the headline case on real server output: the two chips of a sentence sit at
   `[820, 352]` and `[837, 352]` — same line — and the whole answer is a 3-line paragraph. Opening a
   chip moved nothing (`moved: []`) and showed the filing's own words on the opaque ground.
   **Server-side numbering was not touched and behaved exactly as before.**
2. **A canned replay of stored turn 28**, for the placements a live answer does not reliably produce.
   Turn 28's five verbatim `quotes` and its `evidence` rcept_no were read out of `conversation_turn`
   and replayed as an SSE body fulfilled at the **browser** (CDP `Fetch`), so the product's own store,
   renderer and DOM are exercised end to end and only the server is stubbed. That is what put a
   5-row 데이터 블록, a 계산 블록 with a cited input and a reader 「입력」 marker, an API-tier chip and a
   three-chip sentence on the page at once. There is no replay path for a stored turn in the product,
   so this was the only way to pin the data; every claim in §3–§5 that depends on it is a claim about
   rendering, not about the server.

`turn 17` was not used: it is a **refusal**, not an answer.

## 7. Production

`npm run build` → `npm run start` on the same origin, then the same three scripts. Every measured
number is **identical to dev**: the three-chip line at `859.1/876.1/893.1 @ 730.3`, the 3.375px
sentence gap, `moved: []` in all placements, the row's `283.188px 391.812px 17px` tracks, the widget's
`data-flip="up"` at `[867, 451, 380 × 139]`, 340px popovers at 390 clamped to `[8, 436]`. No console
errors and no exceptions were logged in either runtime (the harness listened for
`Runtime.exceptionThrown` and `console.error` throughout), including on a **reload**, where the thread
is restored from `localStorage` and the chips are re-rendered on a fresh document — the hydration path
this change could most plausibly have broken. Every element in the component is still phrasing
content, which is why it does not.

## 8. Findings that are not code

1. **The quote block's fill changed** (deviation 1). It is the one visible difference from what R16
   signed, it is deliberate, and the operator should see it and say whether they accept it. Folded
   into the gate walkthrough via `phase.md`.
2. **The ≤767 44px chip target** (deviation 4) — recorded as an Operator Question: the record's prose
   asks for it, the record's own CSS does not implement it, and both ways of implementing it change
   something signed (the chip's drawn size, or the neighbouring chip's reachability). Not this slice's
   to decide.
3. **A chip can wrap to the next line ahead of its sentence's text.** Seen at 390: 「…예정입니다.」 ends
   a line and `[2][3][6]` begin the next one, before the following sentence. The chips still follow
   their own sentence in reading order and the three stay together, but a reader could briefly read
   them as belonging to what follows. Preventing it means binding the chip to the sentence's last word
   (a change to `Answer.tsx`'s sentence structure), which is beyond this slice's scope and is a
   typographic decision R16 does not make. Recorded for the review to look at in the walkthrough.
4. **The turn's 갈 곳 link is also a `dart.fss.or.kr` anchor** (footer `links`), so "count the DART
   anchors" is 1→2 on a live turn and 0→1 on the fixture. Both show the citation link appearing only
   with the popover; the claim in §3 is about the delta.

## 9. Scope

Nothing outside `InlineCitation.tsx`, `Ask.module.css`, `Blocks.module.css` was touched.
`Answer.tsx` and `DataBlock.tsx` needed no change — the component's props are unchanged, exactly as
the plan predicted. `agent/citations.py` and `agent/events.py` were not opened. No card work.

The scratchpad harness (CDP client, the canned SSE fixture, the four check scripts and their
screenshots) lives outside the repo and is not committed; the numbers it produced are all above.
