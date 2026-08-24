# P8.S15 plan — apply R14 (AI 질문) faithfully, verify in the operator runtime

## What this slice is

Implement the signed R14 round on the AI 질문 surface — widget, launcher existence, `/ask` page,
질문 스트립, citations, composer — exactly as the landed record specifies, then verify §6 items
1–20 in the operator's runtime. **RESPECT THE DESIGN**: never drop, simplify, restyle, or improve
a signed element; a design gap is catalogued on `phase.md` `## Operator Questions` (next free:
Q56), never invented or silently fixed.

## Read first (in this order)

1. `docs/reference/design/rounds/14-ask/output/build-prompt.md` — **the binding contract** (§1–§7).
2. `docs/reference/design/rounds/14-ask/output/result.md` — decisions Q-A…Q-F + §Copy (the 10 new
   signed strings) + departures.
3. `docs/reference/design/rounds/14-ask/output/ask/r14-ask.css` — geometry canon (port
   declaration-for-declaration onto the module class names; card-scaffolding classes at the top
   are cards-only, not product).
4. `docs/reference/design/rounds/14-ask/output/ask/r14-parts.jsx` — strings + the preset table.
5. `works/phases/active/P8/phase.md` §"R14 walk" + §"R14 landed spec" + Q50–Q55 answers.
6. SIGNOFF.md R14 entry (precedence: R14 supersedes R6's 480 boundary, the composer label,
   label-as-question presets, and R3's API-tier sentence — everything else R6 stands verbatim).
7. `docs/current/operations.md` `## Operator Runtime` — where and how to verify.

Current code: `frontend/components/ask/*` (`AskSurface`, `AskLauncher`, `AskWidget`, `AskPage`,
`AskPageScope`, `QuestionStrip`, `Composer`, `Answer`, `InlineCitation`, `presets.ts`, `links.ts`,
`copy.ts`, 4 module.css) and `frontend/lib/ask.ts`. The vocky trigger mount is in the chrome layer
(`frontend/components/chrome/` — find its mount; it is the bottom-left ⓝ).

## Build order

1. **§1 boundary migration (Q-A) first.** `Ask.module.css` 480→767; `AskPage.module.css` 481→768;
   `useAsk.ts` `DESKTOP_QUERY` → `"(min-width: 768px)"` (update its doc comment — the R1 480 line
   is superseded by R14); `AskSurface` renders launcher+widget only >767 (the existing
   render-not-hide mechanism, moved to the new line; `/ask`·`/ops` non-render unchanged);
   `.widget` loses its `max-width` guard, keeps `max-height`.
2. **§2 composer.** `SEND_KO = "보내기"` added to `copy.ts` with an R14 signature comment
   (2026-08-24, Q-C, operator-specified); button idle text uses it; `ASK_SUBMIT_KO` remains only
   on the strip's free chip (update its comment: the P6.S7 reuse flag is closed by R14). Disabled
   = ghost tier per canon `.asend[disabled]` (background none · border-soft · ink-3; delete
   `opacity:.72`); hover on solid = border-color `--live` only; no hover while disabled. Hit
   36px / ≤767 44px unchanged.
3. **§3 presets (Q-D).** `AskPreset.question` decoupled from `label`: a field-key → signed-question
   table in `presets.ts` (the 10 rows of `result.md` §Copy, each with its R14-D# signature;
   `forfeited_share_method` keeps the R6 sentence — do not re-sign it). Label stays the served
   `korean_name`. **A key absent from the table produces no chip** (no label-sending fallback) —
   same for a field with no `korean_name`. Order, generation rules, `correction_interpretation`
   exclusion, withdrawn-event zero-chips all unchanged. Chip `title` = the question it sends.
4. **§4 answer render.** (a) One paragraph: keep sentences as inline spans; normalize leading
   whitespace/newlines at the **store boundary** in `lib/ask.ts` where text blocks are appended
   (`text.replace(/^\s+/, "")` on the block's text as it enters the store; do not touch
   `.question`'s `pre-wrap`). No `<br>`/`pre-wrap`/`display:block` in prose. (b) Footer 근거 N건 =
   **chip count**: compute N from `turn.chips.length` in `Answer.tsx`'s `footerFacts` (ignore the
   server's `footer.count`; do not change the backend — note the server/client divergence as a
   one-line phase note so the review sees it deliberately). rcept_no list + KST stamp unchanged.
   (c) Tool rows: replace the current wrapping with canon `.atool` — `white-space:nowrap;
   overflow-x:auto; overscroll-behavior-x:contain`, scrollbar hidden. Verbatim content unchanged.
   (d) API-tier block: `InlineCitation` branch becomes "quote → quote block; no quote → link
   only" (canon `.aql.solo`, no top margin); **delete `API_TIER_KO`** from `copy.ts` (record the
   retirement in the copy-inventory tail). (e) Thread + quote scrollbars thin per canon.
5. **§5 page · mobile · hover.** `/ask` >767: `grid-template-columns: minmax(0,760px) 340px`,
   bundle `max-width:1124px; margin-inline:auto`, rail `position:sticky; top:var(--space-6)`;
   frameless chat unchanged. `/ask` ≤767: the chrome does **not render** the vocky trigger on
   this route at ≤767 (render decision at the trigger's mount — route check + the same media
   mechanism `useDesktop` uses; do not `display:none` it); the bar is not inset. Hover one-rule
   per canon (strip chip soft→strong; free chip + ink-2→ink-1; citation chip border → opaque
   `--live`; solid send border → `--live`; header icons/scope × ink-2→ink-1). Empty scoped
   widget: preset row under the intro (reuse `QuestionStrip` with `freeInput={false}`, fetching
   presets for the scope the same way `AskPage` does); 전체 공시 empty widget stays empty.
6. **Copy inventory.** Append the R14 tail to
   `docs/reference/design/grounding/copy-inventory.md` (hand-registered file, edit in place):
   신규 10건 (「보내기」 + R14-D1…D9, dated), 회수 2건 (`API_TIER_KO`; `ASK_SUBMIT_KO`'s composer
   use), labels stay server-owned.
7. **Result + notes.** `result.md` from scratch; append phase notes + one-line Doc impact entries
   (frontend / product / experience / qa / copy) to `phase.md`; catalogue any design gap as Q56+.

## Verification (all in the operator runtime, not a convenient one)

- `cd frontend && npm run typecheck` · `npm run smoke` · `npm run build` (scratch copy —
  `next-env.d.ts` untouched) · `.venv/bin/python -m pytest` · `python3 scripts/workflow.py validate`.
- Real browser (headless CDP, isolated profile — never the operator's Chrome session) at
  `http://127.0.0.1:3000`, `http://100.77.164.42:3000`, and a production build served on a spare
  port (e.g. `:3100`), widths **1440 / 1280 / 1024 / 768 / 767 / 600 / 390**.
- Run **build-prompt §6 items 1–20 verbatim** and table each outcome in `result.md`. Highlights:
  the 767/768 existence boundary (item 2); `rg "480|481" frontend/components/ask
  frontend/lib/ask.ts` → 0 (item 3; the only permissible hits are comments explicitly recording
  the superseded line — prefer none); one-paragraph streaming (item 5); footer N = chip count on
  a real 5-chip answer (item 9); strip chip sends the sentence (item 14); 390: no mid-number
  breaks, no vocky ⓝ on /ask, 0 horizontal overflow (item 15); 1564 bundle centering (item 16);
  **768–1024 corner measurement** for the vocky trigger on /ask (item 17 — if the bar touches the
  corner, apply the ≤767 rule and record it); new copy registered / retirements done (item 19).
- The surface is anonymous — no account creation needed. **Never touch the operator's session or
  their browser**; use your own isolated profile. Real questions through the agent are fine
  (anonymous server log only).

## Don'ts

No new features. No token changes. No new Korean beyond the 10 signed strings. Don't touch the
launcher mark/motion, the SSE contract or state names, the 세션·저장 copy, the anonymous path,
server-owned prose (tool rows, refusal sentences), or `links.ts` routes. Don't edit anything
under `docs/reference/design/rounds/*/output/**` (read-only). Don't run `doc-new-version`,
commit, or transition workflow state.
