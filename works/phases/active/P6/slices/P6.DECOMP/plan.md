# Plan — P6.DECOMP (decompose Phase P6: Apply — AI 질문 agent)

## What this slice is

Decompose P6 into middle slices. P6 is the **apply phase of a two-phase split**
(P5 built everything else), so this is a **single-pass** decomposition: the design
already landed and was signed in P3's R6 round — there are no design slices and no
DECOMP2. You create the middle slices as **bare folders** with `new-slice` (never
pre-filling any slice's `plan.md`), and record the breakdown, rationale, findings,
and cross-slice notes in `works/phases/active/P6/phase.md`.

## Binding inputs — read these first

1. `works/phases/active/P6/intent.md` — the confirmed phase intent, **including the
   mid-phase Operator Addition (2026-08-22)**: *"we need to build a agent not just
   llm chain."* This is binding: the backend must be a **genuine agent** — an
   autonomous tool-calling loop where the model decides which tools to call, in
   what order, across multiple rounds, and when to answer. A fixed
   retrieve→prompt→answer chain is **not acceptable**. The decomposition must make
   this architecturally explicit (the agent-core slice is a loop over Gemini
   function calling, not a pipeline).
2. `docs/reference/design/rounds/06-explain/output/build-prompt.md` — R6's signed
   implementation contract (surfaces, widget/page/launcher specs, SSE states,
   citation forcing, refusal structure, session/storage rules, mobile, hard rules).
   READ-ONLY design record. **RESPECT THE DESIGN** — nothing in it may be dropped,
   simplified, restyled, or "improved" by any P6 slice.
3. `docs/reference/design/rounds/06-explain/output/result.md` — the refusal copy
   **families** (five categories: 철회 · 확정 전 · 공시에 없음 · 검증 미통과 폴백 ·
   계산 요청) and what was designed; also READ-ONLY.
4. `works/phases/active/P5/phase.md` — the P5→P6 boundary notes, especially:
   - DECOMP note 5 (~line 153): admin 대화 로그 / 익명 세션 tabs are **framed in P5,
     filled by P6**; conversation storage schema is P6's to design.
   - `P5.S9` note 9 (~line 1148): the conversation port — `mijual.web.conversations`
     `Conversations` protocol (`conversations()` / `sessions()` / `feedback()`),
     P5 wires `EmptyConversations` via `create_app(conversations=…)`. **P6 implements
     the port; no ops route changes.** Inherit its three rules; do not re-decide them.
   - `P5.S11` notes (~line 1344): `/ask` is the nav's third slot and already routes
     (P6's surface, deliberately not `/explain`); the bottom-right corner is kept
     clear on every page for the launcher; the footer bottom-row link is P6's too.
   - `P5.S13` note 8 (~line 1593): the 질문 스트립 (preset chips) on event detail is
     P6's.
   - `P5.S16` note 7 (~line 1945): 거절 카테고리 vocabulary keys the ops tabs expect.
5. `docs/current/` — `backend.md`, `api.md`, `frontend.md`, `architecture.md`,
   `data.md`, `security.md` for what P5 actually built (module layout
   `src/mijual/web/*`, presentation layer `mijual.present`, Next.js app in
   `frontend/`, error envelope, CSRF, session model).
6. `docs/current/decisions.md` D-4 — the application LLM is **Gemini 3.7 Flash**
   (`gemini-3.7-flash`, `GEMINI_API_KEY` in gitignored `.env`, thinking level per
   task via `ThinkingConfig(thinking_level=…)`). The agent loop runs on this model
   with Gemini **function calling**; every call records its thinking level, and
   cost figures are always ▷ estimates.

## Hard constraints the slice set must encode

- **Agent, not chain** (operator addition — see above). The five tools
  `search_events` / `get_event` / `get_portfolio` / `save_feedback` / `get_contact`
  are server-side; the model chooses when to call them; the UI renders each tool
  call as a fact row (mono, per the build prompt).
- **The agent never computes a number** (§3.6): D-day, 환산, 금액 all come from
  upstream verified-contract values (mijual.present); derived values keep the
  「추정」 tag. Citation forcing: no factual claim without a verified verbatim span —
  blocked at generation, not post-hoc; citations arrive with their claim in the
  stream, never as placeholders.
- **Refusals are the five signed families only** — no per-reason-code copy; refusals
  are normal prose (no alert colors), 3-part structure, and are themselves
  citation-forced where they state verified facts.
- **SSE streaming** with the exact signed states (답변 준비 중 → 스트리밍 with the
  7×15 caret → 완료 footer fade → 중단/오류 keeping partial output). No spinners, no
  typing dots.
- **Server-side anonymous conversation storage** (R6-6): anonymous hash only —
  **schema-level** no account/email/IP/UA columns; feeds the ops 대화 로그 · 익명
  세션 · 피드백 tabs through the existing `Conversations` port. No quota anywhere.
  Client persistence is sessionStorage only (not localStorage).
- **`get_contact`**: the operator contact string is a deploy config value —
  **미정, operator-provided, never invented**. Decompose so it reads config and
  handles "not configured" honestly; the actual string lands at P4/deploy. Record
  this as a phase note, not an open blocker.
- Frontend surfaces per the build prompt: 440×620 fixed widget (opaque `#0e1a15`),
  68×50 launcher with the two-half-ring Saturn mark (the one sanctioned motion
  exception — do not let it leak into data surfaces), dedicated frameless `/ask`
  page with the 340 rail, mobile (≤480px) full-width page with no widget/launcher,
  preset strips on event detail, scope model (event scope chip ↔ 전체 공시),
  widget↔page continuity over the same sessionStorage thread, no launcher/vocky
  corner collision, reduced-motion floor.

## Shape guidance (yours to finalize, with rationale in phase.md)

Aim for roughly 5–7 middle slices, ordered **backend first, design implementation
after**, fidelity last. A candidate cut — adjust as your reading dictates:

1. Tool layer: the five tools' server-side implementations over `mijual.present` /
   the exposure contract (search, verified-contract fetch, portfolio, feedback
   queue write, contact config) with their exact return contracts.
2. Agent core: the Gemini function-calling **loop** (multi-round tool use), system
   prompt, citation forcing / span verification at the generation boundary, refusal
   family selection, never-compute rule.
3. Transport + storage: the SSE endpoint (FastAPI), anonymous conversation schema +
   `Conversations` port implementation wired into `create_app`, save_feedback
   persistence, rate limiting as a server matter with zero UI copy.
4. Widget + launcher (frontend): launcher mark, widget chrome, message bubbles,
   tool rows, inline citations, SSE client states, sessionStorage thread + scope.
5. Dedicated page + mobile + preset strips + footer link.
6. Design-fidelity verification in a real browser (RESPECT THE DESIGN), like P5.S19.

Set each slice's `--risk` deliberately: everything above writes real code /
crosses files → `high`. Use `low` only if you genuinely cut a one-line/docs slice
(unlikely here). Kind: `implementation`. Do not create fix slices, do not touch
`P6.REVIEW`.

## Deliverables

- Middle slices created via
  `python3 scripts/workflow.py new-slice --phase P6 --slice P6.S<n> --name "..." --kind implementation --risk high --order <n>`
  (bare folders; no plan.md pre-fill).
- `phase.md` updated: Decomposition section (the breakdown table + rationale),
  Findings & Notes (boundary inheritances from P5, the get_contact config note, the
  agent-not-chain constraint restated, refusal vocabulary keys), Constraints filled.
- `result.md` in this slice folder: what you cut and why.
- Run `python3 scripts/workflow.py validate` at the end; it must pass.
- Do NOT commit, do NOT transition slice/phase status (the decomposition carve-out
  covers `new-slice` only).
