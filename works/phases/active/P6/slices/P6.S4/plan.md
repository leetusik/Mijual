# Plan — P6.S4: SSE transport + persistence + the request-path boundary

## Goal

Put the agent on the wire: the FastAPI SSE endpoint(s) under `mijual.web` that
run `mijual.agent.run_turn` and stream its typed events; the anonymous session
handle over the request; per-turn persistence into S1's storage **from the
`TurnEnd` terminal alone**; server-side rate limiting decided honestly (zero UI
copy); and the honest re-aim of the architecture's "no LLM call in a request
path" invariant. No frontend in this slice (S5/S6) — verify with `curl`.

## Read first

- `works/phases/active/P6/phase.md` — Findings 1 (the re-aim, this slice's
  responsibility), 12, 13, 16 (SSE-over-rewrite buffering), Open Questions 1/3/4,
  and **notes 18–20** (S1 `record_turn`/`session_hash_or_new`; S2 `ToolContext`
  — the transport constructs it, write session when `save_feedback` may run;
  S3 `run_turn` signature, event `frame()`s, the `TurnEnd`-only persistence
  rule, 중지 = closing the generator, footer/links only on `done`).
- `src/mijual/agent/loop.py` · `events.py` · `client.py` — what you serialize.
  Events already provide `frame() -> {"event", "data"}`.
- `src/mijual/web/app.py` (router registration ~102–110, app.state seams),
  `deps.py` (session dependency), `csrf.py` (`X-Mijual-CSRF`, service-wide
  guard — the ask POST goes through it like every unsafe route), `errors.py`
  (the error envelope for non-stream failures), `routers/` conventions.
- `tests/test_web_smoke.py` (the `SPENDING` AST scan) and
  `tests/test_web_vocky.py` (the HTTP-speak scan) — the two invariants to
  re-aim, plus S2's agent-package scan in `tests/test_agent_tools.py`.
- `docs/current/security.md` §Rate Limits/Abuse; `frontend/next.config.ts`
  (the `/api/:path*` rewrite) for the buffering measurement.

## What to build

1. **The ask router** (new module under `src/mijual/web/routers/`, registered
   in `create_app`): a POST endpoint that accepts `{question, scope_rcept_no?,
   session?, history?}` (history = prose Q/A pairs, client-held per R6's
   sessionStorage model; cap its length defensively) and returns
   `text/event-stream`. Per request: resolve the caller's account exactly the
   way existing routes do (optional — same behavior logged-in or not),
   `session_hash_or_new(...)` the client token, build `ToolContext` (write
   session — `save_feedback` may run), and stream `run_turn`'s events as SSE
   frames via their `frame()`. First frame should hand the client its
   `session_hash` (a `session` event or equivalent) so the browser can keep it
   in sessionStorage — never a cookie (the thread is tab-scoped by design).
   - **중지**: client disconnect closes the generator; released text stands.
   - Validation errors (empty question, malformed cursor-style junk) use the
     normal error envelope **before** streaming starts; once streaming, errors
     arrive as the typed `error` terminal, never a half-frame.
   - Headers that matter for SSE through proxies (`Cache-Control: no-store`,
     `X-Accel-Buffering: no`, etc.) — set what's warranted, note why.
2. **Persistence — from `TurnEnd` alone** (note 20): on a `done` terminal,
   `record_turn` with its `kind` / `answer` / `refusal_category` / `scope` /
   `evidence` / `quotes` — the log replays what the reader saw. Decide and
   record the policy for `aborted`/`error` terminals and for client
   disconnects mid-stream (the honest default: persist the partial released
   prose the same way, since 품질 점검 wants exactly the broken turns; if you
   choose otherwise, say why in `phase.md`). The transport owns the
   transaction: commit on success, roll back cleanly on failure without
   killing the stream contract. `save_feedback` rows are the tool's own
   business (S2 flushes; you commit).
3. **The ▷ ledger line**: log `TurnEnd.usage`'s render per turn
   (server log only — Finding 14: no signed ops panel gains a row).
4. **Rate limiting (Open Question 3)**: ship the cheapest honest thing — a
   small in-process limiter (per session_hash and/or per IP *transiently in
   memory*, never persisted — the schema-level anonymity promise covers
   storage; document that reasoning) or nothing at all. Zero UI copy either
   way; a limited request gets the plain error envelope. Record the decision
   and its trade-offs in `phase.md` for P4 to revisit cross-process.
5. **The boundary re-aim (Finding 1 — the honest part).** `mijual.web` now
   imports `mijual.agent`, and the service now makes an LLM call in a request
   path *through that one seam*. Re-state the invariant in the tests so it
   stays true and scanned:
   - the web `SPENDING` scan stays green as-is (web still imports no
     `mijual.dart`/`collect`/`extract`);
   - extend/add a scan asserting `mijual.web` never imports `google.genai`
     (the model is reached only through `mijual.agent`), and keep S2's scan
     keeping spending modules out of `mijual.agent`;
   - update the two scan tests' docstrings (and any in-code comments that
     state the old absolute sentence) to the new truth: "no OpenDART call in
     any request path; the model is reached only through `mijual.agent`;
     `mijual.web` itself speaks no HTTP outside `vocky.py`". Do **not** touch
     `docs/current/*` — append the Doc impact line instead.
6. **SSE buffering measurement (Open Question 4).** With the API on uvicorn:
   `curl -N` the endpoint directly and confirm incremental frame arrival
   (a fake/scripted agent client injected via an app seam is fine for this —
   add a small injection point such as `create_app(agent_client=…)` /
   `app.state` so tests and the smoke don't spend money). Then, if
   practical, start `next dev` and repeat through the `/api` rewrite to see
   whether the proxy buffers; record the measurement (or the honest "not
   measured here, S7 must") in `phase.md` for S5/S7/P4.
7. **Tests (terse, no live model calls):** scripted agent client through the
   real endpoint — frames arrive in order with correct `event:` names and the
   session event first; a `done` turn lands exactly one `conversation_turn`
   row whose fields equal the terminal's; a refusal turn stores its family;
   the client token round-trips (and a malformed one is replaced); CSRF
   blocks a headerless POST; the boundary scans. Keep the suite green:
   baseline **130 passed**.

## Boundaries

- No frontend change (S5/S6 own `lib/api.ts` and the surfaces). No `/ops`
  change. No new column on S1's tables unless truly forced (additive
  `ensure_columns` only, per note 18 — and the two-list shape is signed).
- No quota concept, no UI copy for rate limiting, no Korean string invented —
  the transport emits S3's events and the error envelope, nothing prose.
- The stream never retracts released text; footer/links only on `done` (S3's
  rule — don't synthesize them on abort).
- `GEMINI_API_KEY` must not be required to import, test, or `create_app` —
  key resolution stays on first live use (S3's client already does this).

## Deliverables

- Router + wiring + persistence + limiter decision + re-aimed scans + tests,
  full `pytest` green; a `curl -N` transcript (or equivalent) in `result.md`
  showing real incremental SSE.
- `result.md`; `phase.md` notes (endpoint path + request/response contract for
  S5/S6 including the session event, the abort-persistence policy, the limiter
  decision, the buffering measurement, the injection seam name) + one-line
  **Doc impact** note (`architecture` · `api` · `backend` · `security` ·
  `operations` move here).
- `python3 scripts/workflow.py validate` passes. No commits, no status
  transitions.
