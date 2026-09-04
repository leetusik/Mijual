# P12.F8 — `/stocks?q=<miss>`: the no-match line collapses on the first keystroke and lifts the page 30.6 px (R1 F7)

`kind: fix`, `risk: high` → `slice-executor-high`. Written 2026-09-04 by the orchestrator in `auto`
mode, after `P12.F7` (`47cb523`). **Family D** — the "keep the box" shape F7 just used, with no
measured constant at all: the box that stays *is* the real element.

## Read first

- `phase.md`: `## Decisions` — the instrument seam with F6's screenshot traps and F7's three
  instrument facts (`Network.setBlockedURLs`, the `<nextjs-portal>` dev badge at 390, `boxOf`
  skipping 0 × 0 elements), the build recipe; the shared bar (keep it); F1's seams note.
- The finding, from the R1-era notebook:
  `git show 8519f45:works/phases/active/P12/phase.md | grep -n "F7 (rank"` — `/stocks?q=zzz` at
  1280 (dev): `p.Lookup-module__noMatch` 「‘zzz’와 일치하는 종목이 없습니다 — 종목명 또는 종목코드로
  다시 검색해 주세요.」 is **18.6 px** tall; typing one character removes it and **everything below
  jumps up 30.6 px** (`CraftPanel__panel`, `Lookup__empty`, `Lookup__watch`, the `RightsChip` row,
  the 집계 범위 section — all `dy = −30.6`), **CLS 0.00299** (`ri: false`). 30.6 = the line's 18.6 +
  `.noMatch`'s `margin-top: 2px` + the `.entry` grid's `gap: 10px`. Not measured at 390.
- The code: `components/lookup/LookupHeader.tsx` ~L53–105 — `LookupHeader({ query, missed })`
  seeds `typedText` with the submitted query, listens to the bubbling native `input` event on its
  wrapper (`target.name === "q"`), and renders the sentence only while `missed && submitted !== ""
  && typedText === submitted`: `<p className={styles.noMatch} role="status">{noMatchKo(submitted)}</p>`.
  Its doc comment is R11 §7's rule (finding 9): 「the line lives exactly as long as the submitted
  query is what is in the box — the first differing keystroke removes it, and the candidates open
  into the space it leaves」. `SearchRow` is R9/P7's and **locked** — the docstring says so; do not
  touch it. `Lookup.module.css` ~L1201 `.entry { display: grid; gap: 10px }` (and the ≥ breakpoint
  `max-width: 620px` at ~L1701), ~L1270 `.noMatch { margin: 2px 0 0; font-size: var(--text-sm);
  line-height: var(--leading-base); color: var(--ink-2) }`. `components/lookup/copy.ts` ~L87–98
  `noMatchKo` (do not change it). `SearchRow.module.css` L34: the candidate `ul.listbox` is
  `position: absolute` — it overlays whatever is below the row, so a reserved box under it changes
  nothing about where the candidates open; R11's 「into the space it leaves」 was never geometric.
- `app/stocks/page.tsx` — the server decides `missed` and passes `query`; the sentence is in the
  served HTML of every miss page, which is why the resting state is already right.

## The change

Keep the sentence's **box** while the field is being re-typed; take only its ink, its accessible
presence and its hit target:

1. `LookupHeader.tsx`: render `<p className={styles.noMatch} role="status">` whenever
   `missed && submitted !== ""` (the same condition minus the `typedText` clause — the server
   already renders exactly this), and add the class `styles.noMatchStale` when
   `typedText !== submitted`. Nothing else changes: the wrapper's `onInput`, the seeding, the
   `name === "q"` filter, the copy call. Typing the submitted text back removes the class and the
   sentence is visible again in the same box — today it remounts; now it reappears. Rewrite the
   two sentences of the doc comment that describe the removal so they describe this (the rule is
   unchanged: the *sentence* still dies on the first differing keystroke; its box now outlives it
   until the next submit, so the page under it does not move).
2. `Lookup.module.css`: `.noMatchStale { visibility: hidden; }` — `visibility`, not `opacity`: it
   leaves the accessibility tree and hit-testing, exactly as an unmounted element would (the nav
   twin's own reasoning). No transition, no fade (R1 has no fade for this line, and a fade is
   motion the record never drew).
3. **RESPECT THE DESIGN:** the miss page as loaded is byte-identical (same element, same rule,
   same copy); the no-query `/stocks` and every hit page render no line and are untouched; the
   only new state is 「the sentence's blank box while re-typing」, which the record's rule permits
   and the candidates' absolute panel opens over as before.

Consider and reject in `result.md` (one line each): a `min-height` wrapper (more markup for the
same box), and `opacity: 0` (keeps the sentence in the AX tree and under the pointer).

## Verification (the shared bar, applied)

- `cd frontend && npm run typecheck`, `npm run smoke`; `npm run build` in a fresh copy outside the
  repo (no warnings). HEAD control build on 3015 beside the fixed build on 3014, plus dev 3010.
- **Before/after**, Aside `--account u2`, **1280 and 390**, dev + fixed vs HEAD, on
  `/stocks?q=zzz` (and one query whose sentence **wraps** at 390 — pick a longer miss, e.g. a
  20-character string — so the two-line box is exercised): type one character into the field
  (CDP `Input.insertText` on the focused input, so the native `input` event fires as a reader's
  keystroke does), sampling rects with `requestAnimationFrame` through the keystroke for
  `.CraftPanel__panel`, `.Lookup__empty`, `.Lookup__watch`, the `RightsChip` row and the 집계 범위
  section. Pass = every one of them has **one distinct rect** across the keystroke at both
  viewports (HEAD: `dy = −30.6` at 1280; measure HEAD's 390 delta as the control); no
  `layout-shift` entry from this source (corroboration only — `hadRecentInput` will be true);
  the `<p>` is still in the DOM with `visibility: hidden` and is **absent from the AX tree**
  (CDP `Accessibility.getPartialAXTree` on its node, or `getFullAXTree` filtered by name — HEAD's
  unmounted state as the comparison); the candidate list still opens over the row exactly where
  HEAD opens it (rect equal); typing the submitted text back shows the sentence again in the same
  rect with nothing moving; a new miss submit renders a fresh visible line; a hit submit
  navigates as before. **Resting `AE = 0`** vs HEAD on the miss page before any typing at both
  viewports, with a positive control; `/stocks` with no query `AE = 0` as well.
- **Console / hydration:** the F6 shim, proven live, on every measured load — nothing on the
  production build (the sentence is server-rendered; the first client render must match it).
- Hygiene: no account, no writes; production read-only; 3014/3015 stopped; `make stack-status`
  as found.
- `python3 scripts/workflow.py validate`.

## Notebook when you finish

- `## Decisions`: one line — the no-match line keeps its box while re-typed (files, the class, the
  after-numbers at both viewports, the AX check).
- `## Doc impact`: `frontend.md` — Surfaces / 조회 entry page (`/stocks`): the 검색 불일치 sentence's
  box outlives the sentence until the next submit; the sentence itself still dies on the first
  differing keystroke (R11 §7 unchanged) (P12.F8).
- `## Notes for later slices`: add nothing unless `P12.S2` needs it. Do not touch the shared bar,
  F1's seams note, or the `for P12.REVIEW` / `for P12.S2` notes.
- `## Now` (≤ 15 lines): F8 landed with numbers; `P12.F9` next (Family C — the mono fallback
  faces, ruling 3, `app/fonts.ts` + `app/shell.css`, the 412×915 cold-cache profile); freeze
  date; production on `a74c58a`.

`result.md`, verdict block first, before/after table at both viewports, the AX check, the rejected
shapes.

## Do not

- touch `SearchRow.tsx` / `SearchRow.module.css` / `copy.ts` / `app/stocks/page.tsx`, add a
  constant height, add a transition, change the sentence, add a test file, commit, run any
  workflow state command, write on production, or drive Aside `u0`.
