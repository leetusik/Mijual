# Plan — P6.S6: 전용 페이지 + 모바일 + 질문 스트립 + 진입점

## Goal

Finish the AI 질문 surfaces: replace P5's bare `/ask` shell with the frameless
dedicated page (desktop) and the ≤480px full-width mobile page, add the 질문
스트립 preset chips to event detail, and wire every signed entry point —
widget↔page continuity over the one store, event-scope binding from detail
pages, nav/footer/mobile-menu links. RESPECT THE DESIGN.

## Read first

- `works/phases/active/P6/phase.md` — Findings 10, 12, 13, 16, 17;
  Constraints; **notes 21–22**. Note 22 is this slice's foundation: the store
  API verbatim (`setPageScope` — a page's ambient 범위 applied at open, never
  over a reader-chosen one; `setScope` — **what the 질문 스트립 calls**, and a
  `scope` requires `{rcept_no, name}`; `ask` · `stop` · `retry`), the one
  sessionStorage key (S6 writes nothing of its own), the pre-stream-failure
  rendering rule, the three contract pinches, the two flagged reused strings.
- `docs/reference/design/rounds/06-explain/output/build-prompt.md` —
  §Surfaces (전용 페이지: 챗 표면 프레임 없음, 페이지에 직접, **우측 340 레일만
  패널**, 런처 렌더 금지, 위젯 열려 있으면 닫고 리다이렉트 — 같은 스레드),
  §Mobile (전폭 페이지 하나; 메뉴 첫 행 ≥44px; 프리셋 가로 스크롤 한 줄, 타깃
  ≥44px; 인용 블록 전폭 180px 캡 + 스크롤; 입력 바 하단 sticky 44px; 도구 행
  유지; 뒤로가기 = 있던 자리 복귀, 대화 유지), the 질문 스트립 sentence (상세의
  프리셋 칩 — **그 이벤트의 게이트 통과 필드에서 생성** — 위젯/모바일 페이지를
  이벤트 범위로 열며 질문 전송; 스트립 자체는 답변 렌더 금지), §범위 모델.
  `.../output/result.md` — search it for the Page / ExplainMobile card
  descriptions, the 340 rail's contents, and any preset-chip wording before
  writing anything. READ-ONLY; transcribe.
- `frontend/components/ask/` as landed (S5) — reuse these components; the page
  is **a second view over the same store**, never a second store or lifted
  state. `frontend/app/ask/page.tsx` (the shell to replace whole — its
  docstring says so), `frontend/components/event/` + `app/events/[rcept_no]/`
  (where the strip lands and where the page's gate-passing fields live),
  `components/chrome/` (nav, mobile sheet — the 메뉴 첫 행), `lib/routes.ts`.
- `frontend/AGENTS.md` (Next 16.3.2 caveat — read `node_modules/next/dist/docs/`
  for anything app-router-specific you touch).

## What to build

1. **The dedicated `/ask` page (desktop ≥481px).** Chat directly on the page —
   no panel frame, no brackets; the only panel is the **340px right rail**.
   Fill the rail with signed content only (check `result.md`'s Page card;
   the nearest signed strings are R6-2's panel copy and the 세션 line already
   in `components/ask/copy.ts` — reuse, and flag anything the record leaves
   unwritten). The page renders **no launcher** (S5 already suppresses it on
   `/ask`) and reuses S5's Answer/Composer/citation components and states.
   Arriving with the widget open: it closes (store `close()`) and the same
   thread renders — no reset, mid-stream streaming survives (the store owns
   the fetch; just render the snapshot).
2. **Mobile (≤480px): the page is the whole surface.** Full-width, no widget,
   no launcher (S5 renders neither); sticky bottom input bar (44px), preset
   row as one horizontal-scroll line (targets ≥44px), full-width in-place
   citation blocks capped at 180px with internal scroll, tool rows kept,
   ≥44px touch targets. 뒤로가기 returns the reader to where they were with
   the conversation intact (client-side nav + the persistent store give this;
   verify, don't assume). The mobile menu's first row already links 「AI
   질문」 — confirm it is the first row and ≥44px; adjust only if the signed
   spec disagrees with what P5 shipped.
3. **질문 스트립 on event detail.** Preset chips generated from **that
   event's gate-passing fields** (the detail payload's exposed fields — use
   what the page already renders; never a gate-failed field). Chip press:
   `setScope({rcept_no, name})` + `ask(question)` + open the widget (desktop)
   or navigate to `/ask` (mobile). The strip renders no answers and holds no
   state. Preset question wording: derive from the signed field labels the
   page already shows (e.g. the field name as the question subject) — check
   `result.md` for signed examples first; compose only in signed vocabulary
   and record how each string was formed in the strip's `copy.ts`, flagged
   for S7/REVIEW.
4. **Scope entry points.** On an event detail page, the ambient scope is that
   event: call `setPageScope({rcept_no, name})` (applied at open, never over
   a reader-chosen scope) and clear it on unmount/navigation away (decide the
   exact lifecycle; document it). Everywhere else the ambient scope is null
   (전체 공시).
5. **Entry-point audit.** Nav third slot and footer bottom-row link already
   route to `/ask` — verify labels/behavior; widget header's external-link →
   page with thread intact (S5 built the navigation; verify the landing).
   No duplicate surface anywhere: launcher never on `/ask`, page never
   rendering a second composer for the widget, ops chrome untouched.

## Boundaries

- No backend change (a truly one-line fix allowed but must be recorded in
  `phase.md`). No store rewrite — extend `lib/ask.ts` only if the page
  genuinely needs an API it lacks, and record any addition in `phase.md`.
- No quota UI, no history-list UI, no invented Korean copy (compose only from
  signed vocabulary, with provenance + flags). `docs/reference/design/`
  read-only. No new `position: fixed` beyond what exists (the sticky input
  bar is `position: sticky`).
- Do not degrade P5 surfaces: the detail page's existing layout rules (zero
  horizontal overflow at 390px, corner clear) must survive the strip.

## Validation

- `npm run build` · `npm run typecheck` · `npm run smoke` green; `pytest`
  untouched (**136 passed**).
- Overflow check at 390px on the pages you touched (the P5 method — a quick
  measurement, not a full browser pass; S7 owns fidelity).
- A spend-free wire sanity via S4's `ScriptedModel` seam if convenient.

## Deliverables

- The page (desktop + mobile), the strip, scope wiring, entry-point audit,
  copy with provenance; builds green.
- `result.md`; `phase.md` notes (rail contents + provenance, preset
  generation rule, scope lifecycle decision, anything reused/flagged, any
  store API additions) + one-line **Doc impact** note (`frontend` ·
  `experience` · `product`).
- `python3 scripts/workflow.py validate` passes. No commits, no status
  transitions.
