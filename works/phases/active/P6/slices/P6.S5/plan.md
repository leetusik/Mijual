# Plan — P6.S5: 런처 + 위젯 — the whole desktop AI 질문 surface

## Goal

Ship the desktop AI 질문 surface complete: the Saturn launcher, the 440×620
widget, message bubbles, tool fact rows, numbered inline citations with
in-place quote blocks, the answer footer, refusal rendering, the four SSE
states, and the sessionStorage thread + scope model — all against the live
`POST /ask` contract. **One signed surface, complete**: nothing here ships
half-rendered (no prose without chips, no fake states). RESPECT THE DESIGN —
the build prompt's pixel values are literal.

## Read first

- `works/phases/active/P6/phase.md` — Findings 10, 11, 12, 13, 16, 17; the
  Constraints; **notes 20–21** (event vocabulary + ordering rule — a
  `citation` event *defines* a chip immediately before the `text` event that
  uses it; `TurnEnd` statuses; the `POST /ask` contract — `event: session`
  first, CSRF header, history cap, pre-stream error envelope with **no signed
  Korean copy** — S5 decides what a pre-stream failure shows, nearest signed
  thing is the 중단 inset + 「재시도」; no stop endpoint — 중지 = abort the
  fetch). Also note 20's nit: `copy.BOARD_POINTER_HREF` is a dead route — map
  link kinds through `frontend/lib/routes.ts`, never render that string.
- `docs/reference/design/rounds/06-explain/output/build-prompt.md` — §Surfaces
  (widget + launcher spec), §도구 행 렌더, §인라인 인용, §SSE, §거절, §세션 +
  저장, §의견·문의, §런처 마크 (the exact CSS recipe: two half-rings sharing
  one `ringdrift`, the flat-sticker bug warning), §Hard rules. `.../result.md`
  §Proposed copy + §This-session revisions. READ-ONLY; transcribe copy.
- `frontend/AGENTS.md` — Next 16.3.2 is NOT the Next in training data; read
  `node_modules/next/dist/docs/` before app-router work.
- `frontend/lib/api.ts` (the one CSRF/fetch seam — add the ask call here),
  `lib/routes.ts`, `lib/copy.ts` + `components/chrome/copy.ts` (copy-with-
  provenance convention), `lib/motion.ts` (reduced-motion helpers, if any),
  `lib/session.ts` (sessionStorage conventions), `components/chrome/SiteChrome.tsx`
  (the mount point — its docstring already reserves the bottom-right corner
  for this launcher), `components/Citation.tsx` + `Citation.module.css` (the
  Citation primitive — R6-4 chips are "Citation 프리미티브의 인라인형 —
  블록형과 스타일 공유"), `app/shell.css` / tokens for `--live`,
  `--border-soft`, `--surface-inset`, `--dur-base`, `--panel-glow`, mono
  classes.
- `src/mijual/agent/events.py` — the exact frame payloads.

## Architecture requirement — the shared thread store

R6 §상태 지속: the conversation + scope live in sessionStorage, survive
위젯↔페이지 and page navigation, **and streaming survives the move** (「스트리밍
중 이동/전환에도 끊김 없음」). That forces the shape:

- a **client-side conversation store provided at the root layout level**
  (context provider mounted once inside the app's persistent layout, likely
  alongside/inside `SiteChrome`) that owns: the message list, the scope, the
  session_hash, the SSE fetch lifecycle (start/abort), and sessionStorage
  hydration/write-through. The widget (this slice) and the `/ask` page (S6)
  are two views over this one store — navigation re-renders views, never
  interrupts the fetch. Document the store's API in `phase.md` for S6.
- sessionStorage only (never localStorage — R5's portfolio helper follows a
  different rule; do not copy it blindly). Keys documented for S6.
- The SSE client: `fetch` POST with the CSRF header through `lib/api.ts`
  conventions, parsing `text/event-stream` incrementally (AbortController for
  중지). Handle the `session` frame first, then paint events in arrival order
  — chip definitions arrive immediately before their sentence; render them
  together (no placeholder chips, no trailing attach).

## The signed surface (build-prompt values are literal)

1. **Launcher** (desktop only, hidden while the widget is open, hidden on
   `/ask`, hidden ≤480px, never rendered in ops chrome): 68×50 chat-box frame
   + 11×11 tail (45°, right 12 / bottom −6), bg `#0e1a15`, 1px
   `--border-strong`, `--panel-glow`; inside the 22×22 Saturn mark — planet
   22px circle `#dfe9e4` with the 4.5s band loop; **ring = two half-boxes**
   (40×13, left −9 / top 5, 1.5px rgba(95,208,165,.9), radius 50%) clipped
   bottom-half-in-front / top-half-behind, sharing one `ringdrift` 14s
   ease-in-out (rotate −19°↔−13°, scaleX .94) — a one-sided single ring is
   the recorded bug. Hover: frame holds, mark `scale(1.35)` (`--dur-base`),
   frame border rgba(95,208,165,.7) + bg `#122219` including the tail;
   active 1.15; open: mark fades to a 16px × (1.5px bars ±45°).
   `prefers-reduced-motion`: band, drift, transitions, and hover scale all
   stop. This is the one sanctioned motion exception — nothing of it leaks
   onto data surfaces.
2. **Widget**: fixed bottom-right, **440×620**, opaque `#0e1a15`, no
   backdrop/dim, page layouts unchanged (overlay only). Header: 범위 chip
   (`범위: {종목} · {rcept_no}` + × → 전체 공시; scope changes apply from the
   next question, prior answers untouched) and on the right Lucide
   `external-link` (28px square → navigate to `/ask`, closing the widget,
   same thread — S6 finishes the page side, but the redirect + close + thread
   survival work now) and × (28px, close, launcher returns).
3. **Conversation rendering**: intro line (signed agent intro + the anonymity
   session line from §Proposed copy); user/answer message bubbles; **tool
   fact rows** rendered verbatim from `tool_row.row` (mono `--text-xs`
   `--ink-3`, left 2px `--border-soft` hairline); **citation chips** (mono
   10px, `--live` ink, 1px rgba(95,208,165,.4) border, same 근거 = same
   번호) inline where the `text` event's `citations` place them; tap → the
   in-place quote block (`--surface-inset`, left 2px `--live`, verbatim
   quote + `DART 원문 {rcept_no} ↗` via `dartUrl`), re-tap closes; API-tier
   citations show the signed no-span sentence (R3 rule) + link. Build on the
   existing Citation primitive's styles.
4. **SSE states** (text replacement only — no spinner, no typing dots, no
   bubble slide): idle → **답변 준비 중** (send button text swap + disabled)
   → **스트리밍** (prose grows + 7×15px `--live` caret, 1s `steps(1)` blink,
   reduced-motion stops it; 「중지」 button = abort) → **완료** (footer fades
   in over `--dur-base`: `근거 N건 · {rcept_no} · {생성시각 KST}` + the
   context links from the `footer`/`links` events, mapped through `ROUTES`)
   → **중단/오류** (partial prose kept, dimmed `--ink-2`; inset row
   「연결이 끊겼습니다 — 답변이 여기서 중단되었습니다.」 + 「재시도」). A
   pre-stream envelope failure (429 etc.) uses the same 중단-style inset +
   재시도 — decide, keep it copy-minimal with signed strings only, and record
   the choice.
5. **Refusals**: ordinary prose bubbles — the `refusal` event's family
   sentence plus surrounding cited prose in the 3-part order, links from
   `links`; no alert color, no icon.
6. **의견 flow**: free text through the same conversation (the agent calls
   `save_feedback`); confirmation is the signed 「의견을 저장했습니다 —
   운영자가 확인합니다.」 (arrives as agent prose/tool row — render honestly);
   optional email is just text the reader includes; a failed save shows the
   tool row's 재시도 form only on failure. No dedicated feedback endpoint —
   don't invent UI beyond the record.
7. **Copy**: every Korean string transcribed into the surface's `copy.ts`
   with provenance comments (the `copy.ts` convention). Inventing a sentence
   is a design change — if a state genuinely lacks a signed string, reuse the
   nearest signed one and flag it in `phase.md` for S7/REVIEW.

## Validation

- `npm run build` · `npm run typecheck` · `npm run smoke` (all green), plus
  `pytest` untouched (**136 passed** baseline).
- A dev-server sanity pass with the scripted backend if convenient (S4's
  `create_app(agent_client=…)` seam + uvicorn makes a spend-free live wire),
  but the full real-browser fidelity pass is S7's — do not burn effort on
  screenshots here.
- Zero horizontal overflow introduced; the widget/launcher render nothing at
  ≤480px (mobile is S6's page); nothing new is `position: fixed` except the
  launcher + widget pair.

## Boundaries

- Desktop widget + launcher + shared store + SSE client + rendering
  components only. The `/ask` page stays P5's bare shell (S6 replaces it);
  no 질문 스트립 (S6); no mobile surface (S6). No backend change — if the
  contract pinches, note it in `phase.md` for S6/S7 rather than patching
  `mijual.web` here (a truly one-line fix is allowed but must be recorded).
- No quota UI, no history-list UI (no fake 지난 대화), no invented copy, no
  localStorage, no cookie. `docs/reference/design/` read-only.

## Deliverables

- Components + store + API client additions + copy, builds green.
- `result.md`; `phase.md` notes (store API + sessionStorage keys for S6, the
  pre-stream-failure rendering decision, any contract pinch for S6/S7) + a
  one-line **Doc impact** note (`frontend` · `experience` · `product`).
- `python3 scripts/workflow.py validate` passes. No commits, no status
  transitions.
