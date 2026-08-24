# Result — P7.S5: focus treatment (operator item 3)

**Status: done.** The ① rights-blue ring is off every text field, and every text field still says
"I am focused" — in its own hairline, inside its own box. Everything that is not a text field keeps
the signed 2px `--focus-ring` ring, untouched.

## What changed — two files, both CSS, ~55 lines

### 1. `frontend/app/shell.css` — one new rule beside the existing ring

```css
input:where(:not([type]), [type="text"], [type="search"], [type="email"], [type="password"],
            [type="tel"], [type="url"], [type="number"], [type="date"], [type="datetime-local"],
            [type="month"], [type="week"], [type="time"]):focus,
textarea:focus,
select:focus {
  outline: none;
  border-color: var(--field-focus-border, var(--ink-2));
}
```

Three decisions inside that, each of which had to go the way it went:

- **Allow-list, not deny-list.** The plan proposed
  `input:not([type=checkbox]):not([type=radio])`. Naming the text-entry types instead means a
  future `submit` / `file` / `range` / `color` input keeps the ring by default rather than silently
  losing it. Measured partition below (`select`/`textarea`/typeless input → border; checkbox,
  radio, submit, range → ring).
- **`:focus`, not `:focus-visible`.** The removal has to cover the mouse click *and* the Tab, and
  the positive indicator has to cover a programmatic `.focus()` too (`/portfolio` 수정 autofocuses
  its `SharesInput` — measured). `:focus` is a superset of `:focus-visible` here, and the only
  outline in the app is the `:focus-visible` rule above, so one rule does both jobs.
- **Specificity (0,1,1), not zero.** The plan suggested `:where()`/low specificity. A
  zero-specificity rule **cannot work here**: every field paints its hairline through a CSS-module
  class at (0,1,0) (`border: 1px solid …`), so a (0,0,0) `border-color` would lose and a (0,0,0)
  `outline: none` would tie-and-lose against the (0,1,0) `:focus-visible` ring. `:where()` is
  therefore used only to flatten the type list, leaving `input…:focus` at (0,1,1) — exactly one
  step above the module class, and still overridable by any module that later wants its own focus
  state (none does today; re-grepped).

### 2. `frontend/components/landing/Hero.module.css` — the one field that is not on the shared hairline

`.input` gains `--field-focus-border: rgba(163, 196, 180, 1)` — R2 §Cosmos's own console-field
colour at full strength. No other module needed a hook: every other field is on
`border: 1px solid var(--border-strong)` or `--border-soft`, and the default `--ink-2` is the
opaque member of that same greenish-grey family.

**Deviation from the plan, deliberate and measured:** the plan illustrated `rgba(163,196,180,.8)`.
Composited over this field, `.4 → .8` is only a **2.63:1** state change — under the 3:1 an
indicator wants. `.4 → 1` is **3.95:1** (rendered-pixel measurement: 4.01:1). Same hue, same
declaration shape, one number different.

Nothing else moved: no radius, height, padding, background, border-width, `--focus-ring` token,
`tokens.css`, vocky trigger, `SearchRow.module.css`, or DOM.

## Per-surface measurements

Headless Chrome over CDP, fresh profile per run, `next dev` on **`http://127.0.0.1:3000`**, 1440×900
and 390×844. "before" was captured against the un-edited tree *before any edit was made*, per the
phase's own Fast-Refresh-contamination warning.

| surface / field | class | blurred border | **focused border** | focused outline (before → **after**) |
|---|---|---|---|---|
| `/` hero 조회 row | `Hero .input` | `rgba(163,196,180,.4)` | **`rgb(163,196,180)`** | `solid 2px rgb(143,178,232) @2px` → **`none`** |
| `/stocks` 조회 row | `Lookup .input` | `rgba(163,196,180,.32)` | **`rgb(157,179,168)`** | same → **`none`** |
| `/stocks/00102618` 보유 주식 수 | `Lookup .holdingInput` | `.32` | **`rgb(157,179,168)`** | same → **`none`** |
| `/auth/login` 이메일 | `Auth .input` | `.32` | **`rgb(157,179,168)`** | same → **`none`** |
| `/auth/login` 비밀번호 | `Auth .input` | `.32` | **`rgb(157,179,168)`** | same → **`none`** |
| AI 질문 위젯 composer (`/`) | `Ask .input` | `rgba(163,196,180,.15)` | **`rgb(157,179,168)`** | same → **`none`** |
| `/ask` page composer | `Ask .input` | `.15` | **`rgb(157,179,168)`** | same → **`none`** |
| `/ops` door 운영자 ID · 비밀번호 | `Ops .doorInput` | `.32` | **`rgb(157,179,168)`** | same → **`none`** |
| `/portfolio?sample=1` → 수정 → 주식 수 | `Portfolio .sharesInput` | `.32` | **`rgb(157,179,168)`** | same → **`none`** |
| `/portfolio` (계정) 종목 추가 검색 | `Portfolio .searchInput` | `.32` | **`rgb(157,179,168)`** | same → **`none`** |
| `/portfolio/notifications` → 변경 → 주소 | `Portfolio .emailInput` | `.32` | **`rgb(157,179,168)`** | same → **`none`** |

`rgb(157,179,168)` is `--ink-2` in the `.cosmos` scope; `rgb(143,178,232)` is `--focus-ring` →
`--r1`, the ① 유상증자 hue. Every row above was measured **twice** — mouse click *and* keyboard Tab
— and the two agree on every surface: the border treatment is identical for both, so a keyboard
reader is never left without an indicator.

The last three rows needed an account. A throwaway (`p7s5-before@example.com`,
`p7s5-after@example.com`) was created through 계정 만들기 and deleted through 계정 삭제 in the same
session; `GET /api/auth/me` answers `{"authenticated":false}` afterwards and `select id, email from
account` now returns exactly one row — `s19-fidelity@example.com` (id 14), the pre-existing P5.S19
leftover `P7.S2` already recorded. **No residue from this slice.**

### The two zero-gap rows

| | input right edge | 조회 left edge | gap | ring/border outside the input box |
|---|---|---|---|---|
| `/` hero @1440 | 924 | 924 | **0** | before: 4px of ring under the button · **after: none** |
| `/stocks` @1440 | 656 | 656 | **0** | before: 4px under the button · **after: none** |
| `/` hero @390 | 298 | 298 | **0** | **after: none** |
| `/stocks` @390 | 286 | 286 | **0** | **after: none** |

The rects are byte-identical before and after — the button did not move and no gap was introduced,
as the plan requires. With `outline: none` the whole focus treatment is now inside the input's own
border box, so there is nothing left that *can* paint under the button. Screenshots at 2× confirm
it: the before shot shows the blue ring running behind the green 조회 button; the after shot shows a
clean brightened hairline stopping at the button's edge. The hero input's `border-right: none` means
its focused hairline is three-sided — the signed geometry, unchanged and accepted per plan item 3.

### The state change is legible — rendered pixels, not just computed values

Sampled from 2× screenshots of the border row (blurred vs focused documents):

| surface | blurred pixel | focused pixel | Δ contrast | focused border vs field interior |
|---|---|---|---|---|
| `/` hero | `rgb(70,88,80)` | `rgb(163,196,180)` | **4.01 : 1** | 10.12 : 1 |
| `/stocks` | `rgb(71,88,81)` | `rgb(157,179,168)` | **3.40 : 1** | 7.05 : 1 |
| `/auth/login` | `rgb(72,90,82)` | `rgb(157,179,168)` | **3.30 : 1** | 6.76 : 1 |

All three clear 3:1 both ways — the change from unfocused to focused, and the focused hairline
against the surface either side of it.

### Everything else keeps the 2px ring

Tabbed through the landing page (real `Input.dispatchKeyEvent`, 14 stops) and focused each named
element directly. All still `solid 2px rgb(143,178,232) @2px`, before and after, at 1440 and 390:
the wordmark, all three nav links, the 샘플 chip, 샘플 종료, the `[의견]` vocky trigger, the **조회
submit**, all four **board tabs**, the **펼치기** buttons (both strips and `P7.S3`'s window
control), the AI 질문 **launcher**, board row links, and the **`/portfolio` 챙겼습니다 checkbox**.
The only difference in the whole tab order, before → after, is the one `input[type=text]` stop:
`solid 2px rgb(143,178,232)` → `none`. That is the entire behavioural diff.

The two selector branches no live surface here can exercise — `select:focus` (every `<select>` is
behind the `/ops` door and **no ops credential is configured in this environment**; the service 401s
identically for an unconfigured credential, R7's signed behaviour) and `textarea:focus` (the app
renders none today — the ask composer is an `<input type="text">`, not the textarea the plan's
wording assumed) — were exercised by injecting elements carrying a (0,1,0) class border into a live
page, so the real stylesheet decided:

| injected element | blurred | focused |
|---|---|---|
| `<select class=…>` | `none` / border `.32` | **`none` / border `rgb(157,179,168)`** |
| `<textarea class=…>` | `none` / border `.32` | **`none` / border `rgb(157,179,168)`** |
| `<input class=…>` (no type) | `none` / border `.32` | **`none` / border `rgb(157,179,168)`** |
| `<input type=checkbox>` | `none` | **`solid 2px rgb(143,178,232)`** |
| `<input type=radio>` | `none` | **`solid 2px rgb(143,178,232)`** |
| `<input type=submit>` | `none` | **`solid 2px rgb(143,178,232)`** |
| `<input type=range>` | `none` | **`solid 2px rgb(143,178,232)`** |

### `P7.S4`'s typeahead — untouched, and it still reads as one object

With the listbox open under a focused field (`계` → 1 candidate), on both rows: `aria-expanded=true`,
panel `dx=0 dy=0 width-delta=0`, `border-top-width: 0px`, `border-radius: 0` — identical to `P7.S4`'s
numbers. `SearchRow.module.css` was not edited. One thing to note rather than change (plan §
"Reconciled against P7.S4" says exactly this): the focused input's hairline is now brighter than the
panel's `--candidate-border` side edges (`rgb(163,196,180)` vs `rgba(163,196,180,.4)` on the hero;
`rgb(157,179,168)` vs `rgba(163,196,180,.32)` on `/stocks`), so the seam is visible at 2×. Looked at
in the 2× screenshots it reads correctly — the *field* is the active thing and the panel hangs off
it — so nothing was changed. Carried to `phase.md` as a note for the review.

## Validation

| command / check | outcome |
|---|---|
| `npm run typecheck` (`tsc --noEmit`) | **pass**, no output (re-run after the final edit) |
| `npm run smoke` (`node --test lib/*.test.ts`) | **pass** — 15/15, 0 fail, 172 ms |
| CDP focus probe, `next dev` `127.0.0.1:3000` @1440 | **pass** — table above; only 4xx is the pre-existing `/favicon.ico` 404 |
| CDP focus probe, `next dev` `127.0.0.1:3000` @390 | **pass** — same treatment, gap 0 on both rows; launcher absent at 390 is the signed ≤480 rule, identical before and after |
| CDP focus probe, **Tailscale** `100.77.164.42:3000` @1440 | **pass** — identical to 127.0.0.1 on every field and every ring keeper |
| Injected `select`/`textarea`/checkbox/radio/submit/range probe | **pass** — partition table above |
| Typeahead-open probe on `/` and `/stocks` | **pass** — `P7.S4` geometry unchanged |
| Isolated production build (`P7.S2`'s copy-to-scratch method) + `next start -p 3100` | **pass** — build clean, 16 routes; every field and every ring keeper matches dev; port freed, `lsof -ti tcp:3100` empty |
| `python3 scripts/workflow.py validate` | **pass** — `Workflow validation passed.` |
| `make stack-status` | dev stack left **running** — postgres healthy, api pid 25177, web pid 13009, `127.0.0.1:3000` + tailnet |
| DB residue check | `select id, email from account` → one row, `s19-fidelity@example.com` (pre-existing) |

Backend `pytest` was not run: this slice touches no Python, no template and no API. Console errors
across every run: only `Failed to load resource … 404` for `/favicon.ico`, which `P7.S2` and `P7.S3`
both recorded as pre-existing and nobody's item.

## Deviations from `plan.md`

1. **Hero `--field-focus-border` is `rgba(163,196,180,1)`, not the plan's illustrative `.8`** —
   `.8` measures a 2.63:1 state change, under 3:1; full opacity measures 3.95:1. Same colour, same
   family, one number.
2. **The selector is an allow-list of text-entry types** rather than the plan's
   `:not([type=checkbox]):not([type=radio])` — so a future non-text input type keeps the ring by
   default instead of silently losing it. Verified partition, above.
3. **Specificity is (0,1,1), not `:where()`-flattened to zero** — a zero-specificity rule loses to
   the (0,1,0) module class that paints each field's hairline, so it could not have worked. `:where()`
   is still used, on the type list only. (Re-checked the plan's premise: no module sets a focus
   style today.)
4. **`:focus`, not `:focus-visible`** — needed to cover the mouse click, the Tab *and* the
   programmatic focus `SharesInput` receives from 수정.
5. **The "ask composer textarea" is an `<input type="text">`** (`components/ask/Composer.tsx:49`).
   The app renders no `<textarea>` at all; the rule still names `textarea` for the future and that
   branch was verified by injection.
6. **Two extra surfaces were verified beyond the plan's list** — `/ops`'s door fields and the
   account-only `AddHolding` / `NotificationsView` fields (a throwaway account created and deleted
   through the product) — because they are the fields whose colour families the shared default had
   to be right for.
7. **`/ops`'s *inner* filter fields (`Ops .input`, `.select`) could not be reached live**: no ops
   credential is configured in this environment. They share one declaration block with the door
   field that *was* measured live, and the `select` branch was verified by injection.

## Notes for the orchestrator / review

- **Open Question Q2 stands unchanged and unanswered.** This slice implements collision reading #1
  — the treatment changed, the keyboard indicator survives. If the operator meant *zero* focus
  indication on inputs, that removes the record's a11y floor and is their call, not a slice's.
- Scratch artefacts (CDP scripts, JSON measurements, 2× screenshots, the isolated build copy) live
  in this session's scratchpad and are not in the repo. `rm -rf` on the scratch build copy was
  denied by the sandbox, so `…/scratchpad/prodbuild` (357 MB) is still there; it is outside the
  repo and disposable.
