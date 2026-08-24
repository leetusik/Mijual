# P9.S10 — result

**Status: done.** `/ask` is R16 §2.7b's single 760 column with the start screen, 「새 대화」 and the
bottom-sticky composer; the widget's header is two icons and its empty state is D1 alone; and the
three retirements landed **with their call sites**, so nothing dead was left behind. Ten files
changed, all under `frontend/components/ask/` and `frontend/lib/`; the Python side was not touched.

## What landed

| file | what it is |
| --- | --- |
| `frontend/components/ask/AskPage.tsx` | **re-cut whole.** `CraftPanel` rail, two-column grid, 범위 chip, promise line, 익명 줄 and the page's 프리셋 스트립 are gone. Two states off `state.turns.length`: the **start screen** (`START_HEADING_KO` → `AGENT_INTRO_KO` → composer → **4** `START_CHIPS_KO` cards, each sending its own sentence verbatim) and the **대화 상태** (sticky 「새 대화」 above the column, turns, bottom-sticky composer). |
| `frontend/components/ask/AskPage.module.css` | **re-cut whole**, ported from `output/r16-ask.css`: `.apagec`→`.centered` (560 / 420 ≤767), `.acol1`→`.column` (760, centred), `.astart`→`.start` (640, centre-aligned) + `.astarth`/`.astartp`/`.astartc`, `.acards`/`.acard` (2 cols → 1 at ≤767, 56px, 12px, `--surface-raised` + `--border-soft`, hover `--live`), `.atop`/`.anew` (sticky, mono xs ink-2 underline, 32 → 44px), R14's `.apage`/`.abar` unchanged. Tokens only, **zero new tokens**; the ≤767 mirror S9 left is included. |
| `frontend/components/ask/AskWidget.tsx` | 헤더 = ↗ + × only (폐기 ①); the empty thread carries the D1 intro and **no 익명 줄** (폐기 ⓐ); `onReask` gone. The 범위 *state* and the event-detail 프리셋 스트립 are untouched (check 19). |
| `frontend/components/ask/Answer.tsx` | 「다시 질문」 and its `onReask` prop retired; the 갈 곳 링크 take the right end the button held (§2.7b 「이벤트 상세(오른쪽 끝)」). 재시도 stays, on the disconnect row alone. |
| `frontend/components/ask/Composer.tsx` | one optional `plain` flag = `/ask`'s placement (`.apage .acom`: no divider, no inline padding). The widget's R14 geometry is untouched — one component, two placements. |
| `frontend/components/ask/Ask.module.css` | `.scope`/`.scopeText`/`.scopeClear` and `.anonymity` deleted with their markup; `.composerPlain` and `.footerLinks` added. |
| `frontend/components/ask/copy.ts` | `ANONYMITY_KO` · `VERIFIED_ONLY_KO` · `REASK_KO` **and** `scopeLabel()` · `SCOPE_ALL_KO` deleted (the last two are the retired chip's own copy and had no call site left). A 은퇴 block records what each said and why it went, so no later reader restates one. |
| `frontend/components/ask/AskPageScope.tsx` | docstring only — it still feeds the widget's 범위, which is exactly 「`scope` 상태 자체는 … 표면에 그리지 않는다」. |
| `frontend/lib/ask.ts` | `AskStore.newChat()` — 스레드를 비우는 동작만: empties `turns` (and the `sessionStorage` copy with it), aborts a turn in flight, keeps the 범위 and the `session_hash`. `clearScope`'s docstring updated (no caller left; the door stays). |
| `frontend/lib/ask.test.ts` | one terse case: 「새 대화 empties the thread and the storage behind it, and nothing else」. |

## Validation

| command | outcome |
| --- | --- |
| `cd frontend && npm run typecheck` | **pass** (clean) |
| `cd frontend && npm run smoke` | **pass** — 22 tests, 0 fail (21 existing + 1 new) |
| `cd frontend && npm run build` | **pass** — 16 routes, no warnings from this slice |
| `.venv/bin/pytest -q` | **pass** — 154 tests, 0 fail (Python untouched by this slice) |
| `python3 scripts/workflow.py validate` | **pass** |

`npm run build` rewrites the generated `frontend/next-env.d.ts`; it was restored with `git checkout`
so the slice's diff carries no generated churn.

### What the validation does *not* cover, and what was measured

**No Operator Runtime pass.** Nothing here ran under `make stack-up` at `http://127.0.0.1:3000`, and
no §4 check is claimed — `P9.S11` owns that sweep in dev *and* in the production build.

What *was* done is S9's arrangement: a **static harness** (the real `public/foundations/tokens.css`
plus the two CSS modules, class names namespaced, DOM copied from the components) rendered in
headless Chrome at 1440 and at a 390-equivalent, in the app's own **`class="cosmos"`** scope. The
theme matters more than it looks: `--live-solid` exists **only** in the cosmos scope, so a harness
rendered on the light `:root` silently draws an unfilled 보내기 and the wrong surface entirely — the
first pass did exactly that and was redone. What the second pass showed:

- 1440 — one column, x 340…1100 (**760, centred**), no right column, 「새 대화」 at the column's top
  right, 이벤트 상세 at the footer's right end, the composer with the input's own 1px and no divider.
- 1440 empty — the start block centres inside the 560px box: 안녕하세요! (`--text-2xl`) → D1
  (`--text-sm` ink-2) → composer (typed text **left**-aligned inside a centre-aligned block) → four
  cards in two columns, card text left-aligned, `--surface-raised` on `--border-soft`.
- 390-equivalent — one column of cards, `--text-xl` heading, 44px composer targets, no clipping; the
  footer wraps and 이벤트 상세 keeps the right end (R14's own `flex-wrap`, unchanged).
- **Caveat for whoever repeats this:** headless Chrome clamps the window to a **500px minimum**, so a
  true 390 viewport cannot be screenshot this way. The ≤767 branch is the same one, the pixel width
  is not — `P9.S11`'s real device/viewport pass is what settles 390.

## Deviations from `plan.md`

- **Two more constants than the plan named.** `scopeLabel()` and `SCOPE_ALL_KO` went with
  `ANONYMITY_KO`/`VERIFIED_ONLY_KO`/`REASK_KO`: they *are* the 범위 chip's copy (폐기 ①) and had no
  call site left once the header and rail chips were removed. The **server's**
  `conversationstore.SCOPE_ALL_KO` (「전체 공시」 — a different string) and the store's `scope` are
  untouched, as the record requires.
- **Two files the plan did not name.** `Composer.tsx` gained the `plain` flag (§2.7b's 「감싸는
  테두리·구분선 없음」 is a property of the *page's* composer, and one component with two placements is
  the alternative to a second composer), and `lib/ask.ts` gained `newChat()` (「새 대화」 empties the
  thread *and* the thread's storage — a page-local `turns` reset would have left the conversation in
  `sessionStorage` to be restored on the next reload, i.e. exactly the history §2.7b forbids).
- **`AskPageScope.tsx` was neither retired nor gutted** ("as the tree dictates"): it is what gives a
  widget opened on an event detail its 범위, which §4 check 19 still requires. Docstring only.
- **The `/ask` page's R14 프리셋 스트립 was removed** — a reading of §2.7b's page structure, not a
  settled line, so it is catalogued as an `## Operator Questions` entry rather than treated as
  decided. The widget's strip is untouched.
- Nothing else. No Korean was invented, no signed element was restyled or dropped beyond the four
  explicit 폐기, no history UI exists, the two views still share one store and one `Answer`, and no
  animation was added.

## Notes carried to `phase.md`

Eleven decisions under `### P9.S10 — the page, the widget, and the retirements landed`, four **Doc
impact** lines (three `frontend`, one `qa` with the page's headline regression checks), and two new
`## Operator Questions`: whether `/ask` should keep R14's 프리셋 스트립 in the 대화 상태, and the one
real tension in 폐기 ① — 범위 is now invisible on both surfaces but still rides the next turn, so a
reader who came from an event detail can press a start card naming another company inside that
filing's 범위, with no chip and no × to see or clear it. Both are worth pressing during the
acceptance walkthrough.
