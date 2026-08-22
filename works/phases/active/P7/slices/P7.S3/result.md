# Result — P7.S3: the board shows 30 firms at a time

Operator item **4a** is closed. The 관제 현황판's ranked list renders **30 rows** instead of 386 and
discloses the next 30 through the record's own **펼치기** hairline button; **no Korean string was
minted**. Two files changed, both in `components/landing/`. Item 4b (the strips' 펼치기) was
verified, not reworked — it still works.

## What changed

- **`frontend/components/landing/Board.tsx`** — a `WINDOW_STEP = 30` module constant, a `shown`
  `useState` beside the existing `tab` state, `rows.slice(0, shown)` in the ranked `<ol>`, and a
  disclosure under it that renders only while `hidden > 0`. Tab selection went through a small
  `selectTab()` so a tab switch resets the window. The doc comment's "Why the tabs filter in the
  browser" paragraph gained a **## The display window (`P7.S3`)** section, and its stale
  "450 rows are on the page" sentence was corrected to name the page's *corpus*, which is what it
  always meant.
- **`frontend/components/landing/Board.module.css`** — one new class, `.more`, a centred flex line
  with `padding-top: var(--space-5)`. The button itself is the strips' `.expand` class, unchanged.

No copy file, no API, no data, no other component. The served corpus, the ranked order and the
whole-board `counts` are untouched: this is a **display** window, never a filter.

## The three judgment calls, and why

1. **30, and 30 per click.** No round names a number (R2 draws the list with no length and no
   pagination control — `P5.S3` note 11), so the count is a P7 operator override. 30 is the horizon
   this very page already names in the hero's stat line (`30일 이내 마감`), and it is short enough
   to read without the ② strip sliding off. A click adds another 30 rather than revealing all 386,
   because "some amount at a time" is the whole of the ask — revealing everything on the first click
   would put the page straight back where the operator found it. **Listed for the operator at
   review** (phase Q3).
2. **Zero new copy.** The control is `EXPAND_KO` (펼치기) in `styles.expand` — same class, same
   hairline, same hover, same 44px mobile floor — plus a mono count in `styles.stripCount`
   rendered as `{count(hidden)}건`, exactly the two strips' own `{count(n)}건` idiom. Both the word
   and the `N건` shape are already signed and already on this panel three times, so nothing was
   invented. The count means *what this click discloses*, which is precisely what 60건 / 4건 mean
   beside the strips' own 펼치기 — the semantics carry over unchanged.
3. **It is not a third pinned strip.** `--surface-raised` + a hairline top is R2's treatment for the
   two *pinned* sections; a third raised band between the rows and the ② strip would read as a
   section the round never drew. The control is one line of breathing room under the last dashed
   row instead. Centred, because a bare count + button with no sentence would otherwise sit under
   the RightsChip column and read as a half-drawn row.

**No `aria-expanded`** on the new button: it is incremental, not a two-state disclosure, so the
attribute would be a lie in the false position forever. The strips keep theirs.

**No effect, no module state** — `useState` only. `P7.S2`'s StrictMode trap (a module-scope guard
claimed inside an effect) therefore cannot apply here, and every number below was measured in
`next dev` with StrictMode live anyway.

## Before → after

Headless Chrome over CDP (`P7.S1`'s approach), fresh profile, `Emulation.setDeviceMetricsOverride`
1440×900 and 390×844, on **`http://127.0.0.1:3000`** — the operator's own origin. "before" is a
genuine re-run: the two files were restored to `HEAD`, the dev server Fast-Refreshed, the baseline
was measured, then the change was put back.

| on `/` (전체 tab) | before | **after** |
|---|---|---|
| ranked rows rendered | **386** | **30** |
| 펼치기 buttons in the board | 2 (the strips) | **3** |
| the new control's text | — | **`356건` + `펼치기`** |
| `<li>` in the served HTML | 395 | **39** |
| served HTML | 701,871 B | **369,151 B** (−47%) |
| document height @1440 | 17,730 px | **3,047 px** |
| document height @390 | 30,806 px | **4,523 px** |
| tab counts | 488 / 50 / 422 / 16 | **488 / 50 / 422 / 16** |

### Clicking through, both viewports, both origins, dev and prod

| check | result |
|---|---|
| one click | 30 → **60** rows, control reads **`326건`** |
| click through to the end | **12** clicks → **386** rows — the ranked count for 전체, exactly |
| when exhausted | the control is **gone**; 2 펼치기 buttons remain (the strips) |
| network requests during all 12 clicks | **0** — entirely client-side |
| console errors / exceptions | **none** (the only 4xx is the pre-existing `/favicon.ico` 404) |

### Tabs — the window resets and the counts never move

| tab | ranked rows shown | control | tab counts |
|---|---|---|---|
| 전체 (386 ranked) | **30** | `356건 펼치기` | 488/50/422/16 |
| 유상증자 (14 ranked) | **14** | **none** (nothing to disclose) | 488/50/422/16 |
| 전환사채 (362 ranked) | **30** | `332건 펼치기` | 488/50/422/16 |
| 주식매수청구권 (10 ranked) | **10** | **none** | 488/50/422/16 |

Switching away at 386 rows shown and back to 전체 returns **30** — a tab is a new list. Order is
preserved in every tab (first rows: 계양전기 D-2 · 라온텍 D-3 · 휴맥스 D-4, D-day ascending).

### The strips are untouched (item 4b, verified not reworked)

`<li>` on the page, 전체 tab at the first window: **30** → open ② 전환청구 진행 중 → **90** (+60) →
open 일정 추후결정 → **94** (+4) → collapse both → **30**. `+60` / `+4` match `open_now` / `tbd`
exactly, the same numbers `P7.S1` measured.

### The control measures like the strip's own

Computed style, the new button vs. the ② strip's 펼치기, same page:

| | new control | strip 펼치기 |
|---|---|---|
| border | `1px solid rgba(163, 196, 180, 0.32)` | **identical** |
| border-radius | `0px` | **identical** |
| font | `12px "IBM Plex Mono", …` | **identical** |
| color / background | `rgb(157, 179, 168)` / transparent | **identical** |
| min-height @1440 | `32px` | `32px` |
| min-height @390 | **`44px`** | `44px` |
| width | 57px | 57px |

**No collision with the ② strip:** 16px between the control's box and the strip's hairline top at
both widths, and `document.scrollWidth === window.innerWidth` at 1440 and 390 (no horizontal
overflow). Screenshots at both widths confirm it visually — the centred `356건 펼치기` sits under the
last dashed row, with the raised ② band clearly separate below.

### Tailscale origin — `http://100.77.164.42:3000`

Identical on both viewports: 30 → 60 → 386 in 12 clicks, control gone at the end, 0 requests, tab
counts 488/50/422/16, strips 30 → 90 → 94 → 30, no console errors.

### Production build — isolated copy, `:3100`

`rsync` of `frontend/` (minus `.next`) into session scratch, `npx next build` (**pass**, the same 16
routes), `next start -H 127.0.0.1 -p 3100`. The CSS chunk returned **200** before anything was
believed (`phase.md`'s `EADDRINUSE` trap). Behaviour is identical to dev at both viewports —
30 → 60 → 386 in 12 clicks, control disappears, counts 488/50/422/16, tab reset, strips 30/90/94/30,
button min-height 32px→44px, 16px gap, 0 network requests, no errors. The server was killed;
**`:3100` is free** and the dev stack was never touched.

## Validation

| command | outcome |
|---|---|
| CDP before/after on `127.0.0.1:3000`, 1440 + 390 | tables above |
| CDP on `100.77.164.42:3000` (Tailscale), 1440 + 390 | identical |
| `npx next build` + `next start -p 3100` (isolated copy) | **pass**, 16 routes; behaviour identical; port freed |
| `cd frontend && npm run typecheck` | **pass** (`tsc --noEmit`, no output) |
| `cd frontend && npm run smoke` | **pass** — 15 passed, 0 failed |
| `grep -c "Blocked cross-origin" var/stack/web.log` | **4** — unchanged, still `P7.S1`'s four deliberate negative controls |
| `python3 scripts/workflow.py validate` | **Workflow validation passed.** |
| `make stack-status` | postgres **Up (healthy)**, api **running** (pid 99133), web **running** (pid 13009) — **left up, as found** |

`git status`: `frontend/components/landing/Board.tsx` and `Board.module.css` are the only source
files changed. No commit, no state transition, no `doc-new-version`.

## Copy minted

**None.** 펼치기 is R2/R3's signed disclosure label (`EXPAND_KO`), and `N건` is the strips' own mono
count idiom. The control renders no sentence at all. Nothing needs an operator copy decision — only
the **number 30** does (phase Q3), and that is a behaviour decision, not a string.

## Doc impact (appended to `phase.md`; no `doc-new-version`)

Two lines, both appended to `phase.md` (with the full findings note and decision **D-P7-1**):

- **`frontend`** — the landing board renders **30 ranked rows at a time** and discloses the next 30
  through the signed 펼치기 button with a mono remaining-count, **zero new Korean copy**; a
  **display window, never a filter** (corpus, ranked order and whole-board `counts` unchanged, 전체
  still reads 488; a tab switch resets it). A P7 operator override of an unsigned gap — R2 specifies
  no list length and no pagination control, so `P5.S3` note 11's "the design paginates nothing" no
  longer describes the rendered page (it still describes the API: the board is one request). Served
  HTML for `/` drops **701.9 KB → 369.2 KB**; the 30 awaits operator confirmation (Q3).
- **`experience`** — the 관제 현황판 §Board bullet should say the reader sees **30 rows at a time**
  and presses 펼치기 for the next 30; reading the whole list is now a deliberate act. The strips are
  unchanged. Flagged as foldable into the `frontend` line if the review prefers one.

`docs/current/product.md` was checked and needs nothing: it states the corpus (488 exposable events)
and the board's three product states, never a claim that every row is rendered. **`phase.md`'s
Open Question Q3 was updated** with the provisional answer (30, +30 per click) and the note that the
operator has not confirmed it.

## Deviations from `plan.md`

1. **A remaining-count was added beside the button** (the plan left it optional). It is the strips'
   exact `{count(n)}건` idiom in the same `stripCount` class, and it carries the same meaning there
   as here — *what this click discloses* — so it mints nothing and removes the one real ambiguity a
   bare 펼치기 under a list would have.
2. **The control is not styled as a pinned strip**, though the plan said "same position/feel as the
   strips' disclosure". The *button* is literally the strips' button; the *container* is not, on
   purpose — see judgment call 3. Both strips' treatment is R2's signed marker for a pinned section.
3. **The doc comment gained a section, not one sentence**, and one adjacent stale sentence
   ("450 rows are on the page") was corrected to say what it always meant (the page's corpus is 450
   rows). Comment only.
4. **The "before" column was re-measured rather than quoted** from `phase.md`: the two files were
   returned to `HEAD`, the baseline taken, then the change restored. It reproduced the recorded 386
   exactly.
