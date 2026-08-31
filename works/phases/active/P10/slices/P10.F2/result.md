# Result — P10.F2 · R18 ②②b 활성 탭이 형제를 밀지 않게 (폭 예약)

- **status:** `done`
- **summary:** Applied R18 §② (nav) and §②b (`/ops` tab row): the label and a `visibility: hidden`
  `::after` twin carrying `attr(data-label)` at weight 600 now share one `inline-grid` cell, so the
  cell is always the 600 width and an active tab cannot shove its siblings. **The nav's 0.70px shove
  and `/ops`'s 0.31px shove are both 0** — `/ask` and `/portfolio` now report an identical `left`
  array to the decimal, and all six `/ops` routes report one array. The mobile sheet and the landing
  board were left alone, as the round and the plan require. Verified in real Chrome 152 over CDP
  (**no Aside on this machine**), in dev **and** the production build, at 1280 and 390 — 44
  page-views, production identical to dev on every number, 0 console errors. **The `visibility:
  hidden` clause was proved with a negative control**, not reasoned about: under `opacity: 0` the
  same markup makes Chrome name the link `AI 질문 AI 질문`.
- **files_changed:**
  - `frontend/components/chrome/Nav.module.css` (`.link` → `inline-grid`, new `.link > span` and
    `.link::after`)
  - `frontend/components/chrome/Nav.tsx` (**bar links only** — `data-label` + `<span>`)
  - `frontend/components/ops/Ops.module.css` (`.tab` gains `inline-grid`, new `.tab > span` and
    `.tab::after`)
  - `frontend/components/ops/OpsTabs.tsx` (`data-label` + `<span>`)
  - `works/phases/active/P10/phase.md` (edited under budget: 185 lines / **16,383 B**)
  - `works/phases/active/P10/slices/P10.F2/result.md` (this file)
  - untracked evidence (`var/` is gitignored): `var/p10f2/{before-dev,after-dev,after-prod}/` —
    **102 screenshots**
- **validation:**
  - `npm run typecheck` — **pass** (`tsc --noEmit`, no output)
  - `npm run build` — **pass**, 18 static pages / 19 route entries
  - `npm run smoke` — **pass**, `tests 22 / pass 22 / fail 0`
  - `python3 scripts/workflow.py validate` — **pass**, no warnings (the `phase.md` budget warning
    that appeared mid-edit is gone)
  - R18 §②'s own `left`-array check, **run before as well as after**, dev and production, 1280 and
    390 — §1 and §2 below
  - accessibility-tree dump **with a negative control** on both surfaces — §3
  - hit test, hover, a real mouse click through the navigation, mobile sheet — §4
  - 11 routes × 2 viewports × 2 runtimes regression, console errors counted — §5
- **deviations:** one, in §6: **`white-space: nowrap` is deliberately not copied onto `/ops`'s
  `.tab`** (it is in the nav's `.link`, per R18's diff). Measured reason, not a preference.
- **doc_impact:** one line appended to `phase.md` `## Doc impact` — `frontend.md`: nav `.link` and
  `/ops` `.tab` are `inline-grid` + a hidden 600 `::after` twin, so an active tab no longer moves its
  siblings (nav 0.70px, `/ops` 0.31px — both now 0); the mobile sheet and the landing board stay
  outside the rule, and `/ops` takes it without `white-space: nowrap`. **No `doc-new-version` run** —
  that is `P10.REVIEW`'s.

---

**Instrument.** Aside is **not installed on this machine** (`aside` is not on `PATH`, no app bundle
in `/Applications`), so per the doctrine's own fallback I drove **real Chrome 152.0.7977.65 over
CDP** — the same instrument `P10.S7`, `P10.REVIEW` and `P10.F1` used — in the runtime and access
path `docs/current/operations.md` `## Operator Runtime` names: `make stack-up`, dev at
`http://127.0.0.1:3010`, and the production build (`npm run build && npm run start`) on the same
origin, at 1280 and a true 390 (`mobile: true`, dsf 3). `/ops` was reached by **typing the throwaway
credentials into the real door form and clicking 로그인**, with `MIJUAL_OPS_ID` /
`MIJUAL_OPS_PASSWORD` passed as environment variables on the API process only. **`.env` was never
opened.** Every number below was read out of a live document; none is copied from the record.

## 1. The nav (§②) — the check that could have failed, and did

`plan.md` §6 asks whether my own verification is *capable* of failing. This one is, and the proof is
that I ran it first: R18's own expression,
`[...document.querySelectorAll('header nav a')].map(a => a.getBoundingClientRect().left)`, at 1280
in dev, **before touching anything** (the trailing zeros are the mobile sheet's rows, which are
`display: none` at this viewport):

| route | **before** | **after** |
|---|---|---|
| `/ask` | `[218.75, `**`279.484375`**`, 0, 0, 0]` | `[218.75, 279.484375, 0, 0, 0]` |
| `/portfolio` | `[218.75, `**`278.78125`**`, 0, 0, 0]` | `[218.75, 279.484375, 0, 0, 0]` |
| `/stocks` | `[218.75, 278.78125, 0, 0, 0]` | `[218.75, 279.484375, 0, 0, 0]` |
| `/auth` | `[218.75, 278.78125, 0, 0, 0]` | `[218.75, 279.484375, 0, 0, 0]` |
| `/` (landing) | `[218.75, 278.78125, 0, 0, 0]` | `[218.75, 279.484375, 0, 0, 0]` |

The baseline reproduces `P10.F1`'s **279.48 / 278.78** exactly, and the shove is precisely
**0.703125 px**. Afterwards **all five routes carry one array**, and it is the reserved (600) one.
The per-link widths say why:

| | before `/ask` (active) | before `/portfolio` (inactive) | after, every route |
|---|---|---|---|
| `AI 질문` width | 40.734 | **40.031** | **40.734** |
| `보유 종목` width | 53.469 | 53.469 | 53.469 |

**Only `AI 질문` ever changed width**, and that is the whole mechanism: it is the one bar label with
latin glyphs. In Noto Sans KR the Hangul advance widths are identical at 400 and 600 — `보유 종목`
measures 53.469 at both weights — so a pure-Hangul label never shoves anything. This matters again
in §7.

Not lost, measured after the change: the active link is still **600 with a 2px `rgb(255,255,255)`
underline**; inactive links still reserve `2px rgba(0,0,0,0)`; `aria-current="page"` still moves;
the link box is still the full **51px** bar height at `top: 0`; the twin computes to
`content: "AI 질문"`, `font-weight: 600`, `height: 0px`, `visibility: hidden`,
`pointer-events: none`; and the span computes to `grid-area: label`.

## 2. `/ops` (§②b) — the same defect, and the trap the plan warned about

Six routes, logged in, 1280. The shove was real and `/ops/accuracy` was the odd one out:

| route | **before** | **after** |
|---|---|---|
| `/ops` | `[139.6875, 180.53125, 274.84375, `**`360.515625, 429.984375, 483.25`**`]` | `[139.6875, 180.53125, 274.84375, 360.828125, 430.296875, 483.5625]` |
| `/ops/gates` | same as `/ops` | same |
| `/ops/accuracy` | `[…, `**`360.828125, 430.296875, 483.5625`**`]` | same |
| `/ops/conversations` | same as `/ops` | same |
| `/ops/users` | same as `/ops` | same |
| `/ops/feedback` | same as `/ops` | same |

**0.3125 px**, carried by `정확도·비용` — the only tab label containing a non-Hangul glyph (the `·`),
which is exactly the §1 mechanism again. Its inactive width goes `69.672 → 69.984`, i.e. it now
holds the 600 width whether or not it is the current tab, and the three tabs after it stop moving.

**The trap, checked as the plan asked.** `.tab` declares no `display` at all, so `inline-grid` was
*added*, not swapped, and `place-items: center` is new too; `padding-bottom: 2px` was kept. Every
other geometric property is **byte-identical before and after**, at both viewports and on all six
routes:

| | before | after |
|---|---|---|
| strip `top` / `bottom` / `height` (1280) | 12 / 36.922 / 24.922 | **12 / 36.922 / 24.922** |
| each tab `top` / `bottom` / `height` (1280) | 12 / 36.922 / 24.922 | **12 / 36.922 / 24.922** |
| `padding-bottom` | 2px | 2px |
| active underline | `2px rgb(234, 242, 237)` | `2px rgb(234, 242, 237)` |
| computed `display` | `block` | `grid` |

`display` reads `grid` rather than `inline-grid` because `.tabs` is a flex container and a flex item
is blockified — the same reason the nav's `.link` read `flex` rather than `inline-flex` before the
change. The reservation is unaffected: the cell is still sized to the wider of the two overlapping
items.

**390 is unchanged in every value** — see §6, which is the reason.

## 3. Does a screen reader read each label once? — asked with a control

This is the item `plan.md` flags as the most plausible way the prescription is wrong, so I did not
settle it by reading the CSS. I dumped Chrome's accessibility tree over CDP
(`Accessibility.getFullAXTree`), walked each link's AX subtree by `backendDOMNodeId`, and then
**re-ran the same dump with the twin switched to the rejected alternative**, so the check had a way
to come out wrong.

Nav, `/ask`, 1280 (identical in production):

| twin styling | link accessible name | `StaticText` nodes inside |
|---|---|---|
| **shipped — `visibility: hidden`** | `AI 질문` / `보유 종목` | **one each** |
| control A — `opacity: 0`, `height: 0`, `overflow: hidden` | **`AI 질문 AI 질문`** / **`보유 종목 보유 종목`** | **two each** |
| control B — `opacity: 0`, `height: auto`, `overflow: visible` | **`AI 질문 AI 질문`** / **`보유 종목 보유 종목`** | two each |
| restored — `visibility: hidden` | `AI 질문` / `보유 종목` | one each |

`/ops`, `/ops/accuracy`, all six tabs, same method:

- shipped: `개요` · `게이트 대기열` · `정확도·비용` · `대화 로그` · `사용자` · `피드백` — each once;
- control (`opacity: 0`): `개요 개요` · `게이트 대기열 게이트 대기열` · `정확도·비용 정확도·비용` ·
  `대화 로그 대화 로그` · `사용자 사용자` · `피드백 피드백` — **all six doubled**;
- restored: back to one each.

**So R18 is right, and for the reason it gives.** Note what the control also shows: `height: 0` and
`overflow: hidden` do **not** keep generated content out of the accessibility tree — only
`visibility: hidden` does. Anyone later "simplifying" this to `opacity: 0` breaks the a11y contract
while leaving the layout looking correct, which is precisely the failure mode the round anticipated.

## 4. Still a working control, not just a correctly sized one

Nav, production, 1280 — `elementsFromPoint` at five points per link (top edge `y=1`, middle, bottom
edge `y=height−2`, left edge, right edge): **every probe lands on the link or its span**, so the hit
area is still the full 51px bar height and the twin never intercepts (`pointer-events: none` plus
`visibility: hidden`). Hover, driven with a real `Input.dispatchMouseEvent`:
`rgb(234,242,237) → rgb(157,179,168)` and back — `--ink-2`, unchanged.

Then the user-visible symptom itself: a real mouse press/release on the **inactive** `보유 종목`
navigated to `/portfolio`, `aria-current` moved from `[page, null]` to `[null, page]`, and the
`left` array stayed `[218.75, 279.484375]` **across the navigation**. That is the shove, gone at the
moment it used to happen.

`/ops`, all six tabs: every hit probe inside the tab; active tab 600 with the `--ink-1` underline;
inactive tabs 400 with a transparent one.

**390 — the sheet was not touched, and the check proves it rather than asserting it.** Bar: mark at
`left: 16` (90.75×27), 메뉴 button 44×44 at `left: 330`, bar links `display: none`. Opening the sheet
gives three 48px rows, the active one at 600 — and each row reports `::after` content **`none`**,
`data-label` **`null`**, `span` count **0**. The prescription did not leak into `.sheetRow`.

## 5. Regression — 11 routes × 2 viewports × 2 runtimes

`/`, `/ask`, `/portfolio`, `/stocks`, `/auth/login`, and all six `/ops` routes, at 1280 and 390, in
dev and in the production build: **44 page-views, 0 console errors and 0 uncaught exceptions**, every
`document.title` still `주주의관제탑` (`주주의관제탑 운영` on `/ops`), a header present on all of
them, and **dev and production agreeing on every single measured value** — the nav array, the `/ops`
array, the titles. 102 screenshots in `var/p10f2/`.

## 6. Deviation — `white-space: nowrap` is not copied onto `/ops`'s `.tab`

R18 §②'s diff puts `white-space: nowrap` on the nav's `.link`, and §②b says to give `.tab` "위와
같은 3규칙". I applied the three **rules** (the modified `.tab`, the new `.tab > span`, the new
`.tab::after`) but **omitted `nowrap` from `.tab`**, because at 390 those six tabs currently *rely*
on wrapping to fit inside the bar. I measured what the alternative does rather than guessing, by
injecting `white-space: nowrap` at runtime on the shipped build at 390:

| | shipped (no `nowrap`) | with `nowrap` |
|---|---|---|
| tab strip width | 154.531 | **380.828** |
| last tab (`피드백`) `right` | 213.578 | **439.875** — 49.9px past a 390px viewport |
| strip `top` / `bottom` | 21.609 / 151.141 | **73.906 / 98.828** |
| `정확도·비용` width | 12.422 | 69.672 — still the **400** width, i.e. the reservation does not even engage |

So `nowrap` would have converted a known, filed defect (**D24**, the `/ops` bar at 390) into a
different and worse one, moved the whole bar vertically, and bought no reservation at that viewport
anyway — the reservation only does anything where the cell can take its max-content width, which is
desktop. Without it, **every 390 value on `/ops` is identical before and after** (§2). The reason is
written into the CSS comment beside the rule so it is not "tidied" back in later.

The nav keeps its `nowrap` exactly as R18 wrote it: those two links never wrap at any viewport where
they are visible.

## 7. Out of scope, and measured instead — the landing board (`plan.md` §3)

`components/landing/Board.module.css` carries the identical `.tab` / `.tabActive` pair
(`Board.tsx:407`) and **was not fixed**, for the plan's concrete reason: those tabs render three
children (`tabFull` / `tabCompact` / `tabCount`), which one `data-label` twin cannot reproduce, and
`.tabs` is `overflow-x: auto` on mobile. What I did instead was measure it — clicking each of the
four tabs in turn and reading every tab's `left` — so the open `## Operator Questions` entry becomes
decidable. **Dev and production agree; these numbers are the production run.**

**1280 — no shift at all.** Every selection gives the same array:

| selection | `left` array |
|---|---|
| initial / 전체 / 유상증자 신주인수권 / 전환사채 오버행 / 주식매수청구권 | `[129, 205.656, 366.422, 508.969]` |

Widths are constant too (60.656 / 144.766 / 126.547 / 116.156) at both weights. **The desktop labels
are pure Hangul**, and Hangul advance widths do not change between 400 and 600 — so the most-seen
tab strip in the product does not shove at the desktop viewport at all.

**390 — exactly one selection shifts, by 0.42px.** The mobile strip uses the compact labels
(전체 / 유증 / **CB** / 매수청구), and `CB` is the only latin one:

| selected | `left` array | shift |
|---|---|---|
| initial · 전체 · 유증 · 매수청구 | `[33, 109.656, 179.703, 249]` | — |
| **CB** | `[33, 109.656, 179.703, `**`249.422`**`]` | **+0.422px** on 매수청구 (CB's own width 53.297 → 53.719) |

**So: it is real but nearly benign** — zero at 1280, and a single 0.42px nudge of one tab at 390,
against the nav's 0.70px and `/ops`'s 0.31px. That is now in `phase.md` `## Operator Questions` with
both options (a design round, or a deferred job) for the operator to decide at the gate.

## 8. What was deliberately not touched

`.sheetRow` / `.sheetActive` (§4 proves it) · `components/landing/Board.module.css` (§7) ·
`public/foundations/tokens.css` · `Launcher.module.css` and its `mask-size: 84%` · everything the
wordmark/favicon work covered (`Wordmark.tsx`, `copy.ts`'s `WORDMARK_NATURAL`, `layout.tsx`, the
three tiles, both READMEs — all `P10.F1`'s) · `html:root` and `.inner:global(.content)`, the two
cascade traps the notebook warns about, both of which live in files adjacent to the ones I edited ·
`docs/current/*.md` · everything under `docs/reference/design/rounds/` (**read-only — nothing there
was edited**) · `.env`. **Token diff: 0. New or deleted copy: 0. New strings: 0.**

`git diff --name-only` is the proof: four product files, all four named in `plan.md`.

## 9. Notes and dead ends

- **The round documents §②b as out of scope (§⑦.1) and `phase.md` says the operator brought it in.**
  `plan.md` warned about this contradiction; `VERIFICATION.md` §5 records the approval
  (2026-08-31). I followed `phase.md` and did not edit the round record.
- **`display` computes to `grid`, not `inline-grid`, on both surfaces** — flex-item blockification.
  Worth writing down because a later checker that asserts `inline-grid` would report a false failure
  on correct code. The pre-change `.link` reported `flex` for the same reason.
- **The twin does not disturb the grid row's height.** `height: 0` plus `overflow: hidden` means the
  row is sized by the visible span alone; every `top`/`bottom`/`height` in §2 is unchanged, which is
  what confirms it rather than the rule's wording.
- **`place-items: center` centres the shorter (400) label inside the reserved cell** instead of
  left-aligning it, so an inactive label's glyphs sit ~0.35px right of where they used to. That is
  inherent to the signed prescription, is what makes the *box* stable, and is well under the shove it
  removes; recorded, not changed.
- **The stack was restored to how I found it.** The API had to be restarted with throwaway
  `MIJUAL_OPS_ID` / `MIJUAL_OPS_PASSWORD` to reach `/ops`, and `next dev` had to be stopped so
  `npm run start` could serve production on the same origin. Both were put back: `make stack-status`
  again reports postgres + api + web on 3010 / 8010 / 5434, the API process carries **no**
  `MIJUAL_OPS_*` variable, and `/ops` shows the door again. Chrome, its throwaway profile and every
  CDP script live in session scratch space; nothing was added to the repo.
- **Evidence:** `var/p10f2/{before-dev,after-dev,after-prod}/` — 102 PNGs. `var/` is gitignored.
