# P9.S9 — the five elements: CalcBlock · DataBlock · StatusLine · ToolTrace · markers, and §2.8's order

## Context

The design-implementation heart of the phase: everything the store now carries gets drawn, in both views, exactly as the record specifies. Binding spec: `works/phases/active/P9/phase.md` → `### DECOMP2` → **`P9.S9` — the five elements** (read in full) and `docs/reference/design/rounds/16-smart-assistant/output/build-prompt.md` §2.1–2.6 + §2.8 (element specs — **the numbers transfer exactly**), with `output/r16-ask.css` as the complete CSS source (token-only, zero new tokens; translate class names into this repo's CSS Module convention) and `output/r16-parts.babel.js` as the reference markup. Read the `### P9.S3`–`### P9.S8` decision sections in `phase.md` and S8's `result.md` — the store's shapes are landed facts (a `place()` keyed reduce; the transient line lives in `turn.blocks`; `AskTurn.reason` distinguishes 소진 from 연결 끊김; `Answer.tsx::group()` has an `isProse` guard you now replace with §2.8's child order; data-row chips are defined-but-undrawn until you draw them, at which point 근거 N건 and visible chips reconcile).

**RESPECT THE DESIGN.** Do not drop, simplify, restyle, or "improve" a designed element; where an exact value is unspecified, choose the option closest to the designed intent, never a plainer fallback. All rendered Korean comes from `copy.ts`'s §0 strings (S8 landed them) — no new strings.

## Scope

New components under `frontend/components/ask/`, used by **both** views through `Answer.tsx` (widget and `/ask` are two views over one store — do not fork):

1. **StatusLine** (§2.1): one line, mono `--text-xs` ink-3, left border **2px dashed** `--border-soft` + 8px padding-left (tool row is solid — the signed distinction), nowrap + hidden horizontal scroll, `role="status"`, last child before footer, **no animation of any kind** (the spinner/typing-dot ban stands). Renders the frame's own signed `text`.
2. **ToolTrace** (§2.2): rows verbatim in today's tool-row style; flat at ≤3 rows or while streaming; folded to `trace(tools, events)` + `자세히` at ≥4 on completion (mono order numbers on expand, ink-3, 8px margin-right); summary line 2px solid left border; fold state never stored; targets 32/44px. `events` = `turn.filings`.
3. **DataBlock/DataRow** (§2.3): 1px `--border-soft` block; mono 11px ink-3 heading (`DATA_HEADING` default, server `title` wins, `null` = none); three-column grid `minmax(0,40%) minmax(0,1fr) auto` (36% ≤767), 8px column-gap, `8px 12px` row padding, 1px dashed row separators; label sans `--text-sm` ink-2 keep-all; value mono tabular ink-1 nowrap **value-cell-only scroll** (hidden scrollbar, overscroll-contain); third column fixed and never scrolled away — 「입력」 marker and/or the citation chip (same `InlineCitation` component); `align-self: stretch` not `width:100%`; >6 rows → 6 + `모두 보기 (N)`/`접기`; `margin-inline: -12px` at ≤767; **no 3-column table**.
4. **CalcBlock** (§2.4): 1px `--border-strong`; heading mono 11px = `--live` word (`검증된 계산`|`식 계산`) + ink-3 name; inputs reuse the DataRow row component; expr line mono `--text-sm` ink-2 nowrap-scroll, hidden on error; one reserved slot so `pending`(「계산 중」 mono 11px ink-3) → `done`(result row: `--live-tint` bg, 「결과」 12px ink-2 left, value `--text-md` mono 600 `--live` + 「계산」 marker right) → or `error`(`calcError(why)` sans `--text-sm` ink-2, **no alert color/icon**) replaces in place without the block jumping.
5. **Marker family** (§2.5): 계산 (`--live`) and 미확인 (ink-2) as siblings of 추정 — inherit `frontend/components/EstimateMarker.tsx`'s geometry (.56em/.22em/.1em .5em/.55em/color-mix 42%/.08em) rather than re-deriving; respect its no-default typing discipline when extending or siblinging it. 미확인 renders `text.unverified` spans — the sentence lives, the figure is marked.
6. **Citation chips** (§2.6): unchanged component; new *places* only (data value, calc input); the chip sits **after the sentence's full stop**.
7. **`Answer.tsx` §2.8 child order**: 도구 흐름 → 구조화 블록 (server order) → 프로즈 → 링크 → 진행 표시/끝맺음 → 푸터; single `gap` (12px); blocks always full width, never side by side. The 소진 turn (`reason` = budget) renders per §2.7: dimmed prose + folded trace, **no inset, no button, no string** (the R14 disconnect inset stays for disconnects only — `reason` distinguishes them, S8's note).

## Constraints

- CSS in the existing module convention (`Ask.module.css` or new module files beside the components), numbers transferred exactly from `r16-ask.css`; zero new tokens.
- Terse tests; `npm run typecheck` + `npm run smoke` + `npm run build` green; Python suite untouched; `python3 scripts/workflow.py validate`.
- Anything the record never settled that you meet in the flesh: catalogue on `## Operator Questions`, never invent (design-cowork rule).
- Doc impact + durable notes to `phase.md`; `result.md`; structured verdict. Never commit or transition state.
