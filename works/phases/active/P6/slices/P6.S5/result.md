# Result — P6.S5: 런처 + 위젯 — the whole desktop AI 질문 surface

**Status: done.** The desktop AI 질문 surface is complete against the live
`POST /ask` contract: the Saturn launcher, the 440×620 widget, the shared
conversation store, the SSE client, message bubbles, verbatim 도구 행, numbered
inline citation chips with in-place quote blocks (both tiers), the 답변 푸터,
refusals as ordinary prose in the signed 3-part order, and the four SSE states.
Nothing ships half-rendered and no Korean sentence was invented.

## What landed

| File | What it is |
|---|---|
| `frontend/lib/ask.ts` (new) | The conversation store — framework-free, **module scope**. Turns, 범위, `session_hash`, the SSE lifecycle with `AbortController`, sessionStorage hydration/write-through. |
| `frontend/lib/api.ts` (edited) | `ASK_PATH` · `streamAsk()` (the one streaming call, CSRF header + `credentials: "include"`, pre-stream envelope → `ApiError`) · `decodeSse()` (pure, incremental). |
| `frontend/lib/ask.test.ts` (new) | Four terse smoke cases: split-frame decode, a full turn (chips defined before their sentence), a pre-stream refusal, 중지 keeping the partial answer. |
| `frontend/components/ask/` (new) | `copy.ts` (every Korean string, with provenance) · `links.ts` (kinds → `ROUTES`) · `useAsk.ts` (context + `useSyncExternalStore` + `useDesktop`) · `AskProvider.tsx` · `AskSurface.tsx` (where the pair may exist) · `AskLauncher.tsx` + `Launcher.module.css` · `AskWidget.tsx` · `Answer.tsx` · `InlineCitation.tsx` · `Composer.tsx` · `Ask.module.css` · `index.ts`. |
| `frontend/components/chrome/SiteChrome.tsx` (edited) | Wraps the reader tree in `AskProvider` and renders `AskSurface` inside the frame; the docstring records why the store is provided at the persistent layout. |

**Nothing else moved.** `git status` shows no change under `src/`, none under
`docs/reference/design/`, and `frontend/app/ask/page.tsx` is still P5's bare
shell (`P6.S6` replaces it).

## The architecture decision, and why

R6 requires 「스트리밍 중 이동/전환에도 끊김 없음」. Navigation unmounts a page, so
the fetch cannot belong to one. The thread therefore lives in **module scope** in
`lib/ask.ts` and `AskProvider` (mounted once in `SiteChrome`, the client half of
the persistent root layout) only hands the store out through context. Two
consequences worth keeping:

- the provider holds **no state**, so a `text` frame arriving mid-stream
  re-renders the subscribed views and never the pages under them;
- closing the widget, or walking to `/ask`, interrupts nothing — the widget and
  `P6.S6`'s page are two views over one store, which is exactly the shape S6 needs.

`lib/ask.ts` imports **no React** (the rule `lib/session.ts` already states), which
is what lets `lib/ask.test.ts` run under `node --test`.

## Validation

| Command | Outcome |
|---|---|
| `npm run build` (frontend) | **pass** — Next 16.3.2, compiled, 15/15 pages generated, `/ask` still prerendered static. |
| `npm run typecheck` | **pass** — `tsc --noEmit`, clean. |
| `npm run smoke` | **pass** — 15 tests, 15 passed (11 pre-existing + 4 new). |
| `.venv/bin/python -m pytest` | **136 passed** — the P6.S4 baseline, untouched (no backend file changed). |
| `python3 scripts/workflow.py validate` | **pass** — `OK` (recorded below). |

**Extra check — the client run against the real wire, spend-free.** A scratch
script built the app with `create_app(agent_client=lambda: ScriptedModel(…))`
(S4's seam) over the in-memory corpus and dumped the **actual** SSE bytes for an
answer turn and a 철회 refusal turn; those bytes were then fed through
`decodeSse` + the store in Node **in 3-byte chunks**, so every frame — and several
multi-byte Korean characters — was split across reads. The store produced exactly
what the widget renders:

- answer: two 도구 행 verbatim, `citation 1` (quote + span + field_key) defined
  **before** the sentence that names it, `text` carrying `[1]`, footer
  `근거 1건 · 20260724000546 · 2026-08-22 21:25 KST`, terminal `done`;
- refusal: 도구 행, an **API-tier** chip (`api_tier: true`, no quote), ① 상태 사실
  「이 유상증자는 철회되었습니다.」 with its 근거 칩, ② the signed family sentence
  「철회된 공시는 해설하지 않습니다.」, ③ the 갈 곳 links, footer, terminal `done`
  with `refusal_category: 철회`.

Not done here (S7's, by the plan): the real-browser fidelity pass — the launcher
mark reading test, the corner-collision check against vocky, reduced-motion in a
browser, and a live agent conversation.

**Overflow / fixed-position audit.** `grep -rn "position: fixed" app components`
returns exactly three: `app/shell.css`'s pre-existing `.backdrop`, and the
launcher + widget. Both are anchored `right/bottom: var(--space-6)` so neither can
push the document rightward, and the widget carries
`max-width: calc(100vw - 2*var(--space-6))` / `max-height: calc(100dvh - …)` guards
that bite only on a window smaller than the signed panel plus its margins.

## Decisions this slice took (all also in `phase.md`)

1. **Pre-stream failure rendering** — a `429 rate_limited` / `invalid_question` /
   dead-service failure ends the turn with **no blocks** and shows R6's one 중단
   inset row + 「재시도」. No code, no English, no invented sentence, and **no quota
   copy** (a limit that is not shown must not be implied).
2. **`open` is not persisted**; the thread, 범위 and handle are. A widget that
   reopened itself on reload would be an unsigned behaviour.
3. **A restored `pending`/`streaming` turn becomes `aborted`** — the fetch died
   with the page, which *is* 「연결이 끊겼습니다」.
4. **재시도 re-runs the same question in the turn's own place** rather than
   appending a second question.
5. **The 의견 confirmation is rendered by the surface** off `save_feedback`'s own
   `ok`, immediately after its 도구 행 — see the deviation below.
6. **③ 갈 곳 링크 render under the refusal sentence** (from the `links` event) and
   the footer then shows facts + 다시 질문 only, so the same list is never drawn
   twice; an answer (no `links` event) takes its context links in the footer.

## Deviations from `plan.md`

1. **의견 확인 line — the plan's assumption was wrong, and the record decides.**
   The plan says the confirmation 「의견을 저장했습니다 — 운영자가 확인합니다.」
   "arrives as agent prose/tool row — render honestly". It does not:
   `mijual.agent.tools.save_feedback` returns `{"saved": true}` with the row
   `의견 저장 → 운영자 검토 대기열` and its docstring states 「the tool writes no
   Korean sentence about it, because R6 signs the confirmation copy and **the
   surface renders it**」 — `mijual.agent.copy.FEEDBACK_SAVED_KO` repeats it
   ("the surface renders it (`P6.S5`), the agent never writes it as prose").
   Waiting for prose that cannot come would have dropped a signed element, so the
   surface prints the sentence after a successful `save_feedback` row, from the
   tool's own `ok`. A failed save adds nothing: the tool's row already **is**
   「의견 저장 → 재시도」 (R6: 실패 시에만 재시도 행).
2. **Two strings R6 does not write are reused, not invented** (the phase rule):
   the composer's idle button takes R6-2's 「직접 질문 입력 →」, and the question
   field's accessible name (plus the panel's) is the surface's own 「AI 질문」.
   Flagged in `phase.md` for `P6.S7`/`P6.REVIEW`.
3. **필드로 이동 is not rendered.** R6 lists it among the footer's context links,
   but the server serves no such link kind (only `dart` · `event` · `board` ·
   `stocks`) and the detail page has no field anchors. Recorded as a contract
   pinch for S6/S7 rather than invented here; 다시 질문 and 이벤트 상세 are both
   rendered.
4. **The launcher's 열림 상태 is implemented but sits behind the widget.**
   §Surfaces says 「런처는 열리면 숨음」 and §런처 마크 specifies an open state
   (마크 페이드아웃 + 16px ×). Both are honoured: the launcher keeps its place and
   gets `data-open` (the mark fades, the × appears) and `inert`, while the opaque
   440×620 widget covers that exact corner — so the reader sees the widget, the
   signed open state exists, and only the widget's × can be clicked.
5. **No event-detail scope binding.** The store implements the whole 범위 model
   (`setPageScope` / `setScope` / `clearScope`, chip + ×, next-question-only), but
   the entry point that sets an event 범위 is the 질문 스트립, which the plan's
   Boundaries assign to `P6.S6`. So in this slice the chip reads 「범위: 전체 공시」
   until S6 calls `setPageScope`/`setScope`.
6. **`lib/ask.ts` imports `./api.ts` with the extension** — `tsconfig`'s
   `allowImportingTsExtensions`, the spelling every `lib/*.test.ts` already uses,
   required so `node --test` can load the store. Both bundler and `tsc` accept it.

## Doc impact

One line appended to `phase.md`'s running list (`frontend` · `experience` ·
`product`); `P6.REVIEW` consolidates it. No doc version was created here.
