# Plan — P6.S3: agent core — the autonomous Gemini function-calling loop

## Goal

Build the agent itself in `mijual.agent`: the loop that streams an answer while
the **model decides which tools to call, in what order, across as many rounds
as it needs, and when to answer**. This is the phase's keystone — the operator's
binding addition is *"we need to build a agent not just llm chain"*, and it must
be readable as a control-flow property of one module: `generate → (function_call?
→ execute → feed result back) → repeat → answer`. A scripted
retrieve→prompt→answer pipeline fails the slice no matter how good its output is.

Also in scope: the agent's own Gemini client, the system instruction, **citation
forcing at the generation boundary**, refusal-family selection, the
never-compute rule, scope handling, a structural round/call budget, the ▷ usage
ledger, and the **typed event stream** S4 will serialize and S5 will render.
NOT in scope: HTTP/SSE endpoints (S4), persistence of turns (S4), any frontend.

## Read first

- `works/phases/active/P6/phase.md` — Findings 1, 6, 7, 8, 13, 14, 17;
  Constraints; **notes 18–19** (S1 storage API; S2's `ToolResult` / `Citation` /
  `ToolContext` / `call_tool` / `declarations()` / copy provenance — note 19 is
  the contract this slice builds on, including the filing-number→`get_event`
  hint the system instruction must restate).
- `src/mijual/agent/` as landed — `tools.py`, `context.py`, `copy.py`,
  `declarations.py`. Read `copy.py`'s provenance discipline before touching any
  Korean string.
- `docs/reference/design/rounds/06-explain/output/build-prompt.md` — §Agent,
  §인라인 인용, §SSE, §거절, §Hard rules. `.../output/result.md` §Proposed copy
  (~line 66): the agent intro, the five signed refusal-family sentences.
  READ-ONLY; transcribe, never paraphrase.
- `src/mijual/extract/client.py` — the patterns to **copy, not import**
  (Finding 1): `CallBudgetExceeded` structural budget, `Usage`/`UsageLedger`
  with ▷ cost, per-task thinking map, `Pricing`, lazy `google.genai` import,
  dry-run posture. The agent gets its **own** client in `mijual.agent`; if you
  lift a shared piece into a neutral module instead, record the decision in
  `phase.md`. Importing `mijual.extract` from the agent is forbidden and the
  AST-scan test will fail it.
- SDK: **google-genai 2.18.1 is installed in `.venv`** (an S2 note says
  otherwise — that note is wrong; `.venv/bin/python -c "from google import
  genai; print(genai.__version__)"` prints 2.18.1). Read the SDK's own docs for
  `generate_content_stream` + `types.Tool(function_declarations=…)` +
  `types.Part.from_function_response` rather than trusting training data.
- `docs/current/decisions.md` D-4 — model `gemini-3.7-flash`, `GEMINI_API_KEY`
  from the gitignored `.env`, thinking level per task
  (`ThinkingConfig(thinking_level=…)`; omitting inherits the preset; unlisted
  tasks run `LOW`), every call recording its level, every cost figure a ▷
  estimate.

## Requirements

1. **The loop (agent, not chain).** One entry point (suggested:
   `run_turn(ctx, question, history) -> Iterator[AgentEvent]` — a sync
   generator is fine; S4 adapts it to SSE). Inside: hand the model the five
   declarations and stream; on a `function_call` part, execute via `call_tool`,
   emit the tool's fact row as an event, append the function response to the
   conversation contents, and loop for another model round; on text, run it
   through the citation gate and emit verified prose. **No fixed tool order, no
   mandatory pre-fetch, no hardcoded "call search first"** — the system
   instruction may advise (e.g. the filing-number hint), but control flow never
   forces a call. Multi-round must genuinely work (tool → model → another tool
   → answer). A structural budget caps rounds/calls per turn
   (`CallBudgetExceeded` pattern) and maps to an honest terminal event, never a
   silent truncation.
2. **Citation forcing is a generation-boundary gate.** R6: 인용 없는 주장은
   생성 단계에서 차단 — 스트림에 나올 수 없음; 칩은 주장과 동시에 도착, 자리표시
   칩·후행 부착 금지; 인용문 재구성·요약 금지 — verbatim span만. Mechanism is
   yours to design, but it must be **structural, not prompt-trust**. A workable
   shape: the loop assigns ids to the `Citation`s each tool returns; the system
   instruction requires inline markers binding each factual sentence to
   citation ids; the loop buffers text per sentence, releases a sentence only
   when its markers resolve to real citations (marker stripped, chip event
   emitted with the sentence), and **blocks** a factual sentence with no/bogus
   marker. Whatever you build:
   - a chip event carries the verified data (rcept_no + verbatim quote/span, or
     the API-tier no-quote form — `Citation.quote is None` is a citation, not a
     missing one), taken from `ToolResult.citations` only — never from model
     text;
   - same 근거 = same 번호 (칩 numbering is per-answer and stable);
   - a blocked claim degrades honestly: into the 검증 미통과 폴백 family (or a
     clean answer without that sentence when the rest stands verified — decide,
     and record the rule in `phase.md`);
   - **the never-compute rule rides the same gate**: numeric tokens in released
     prose must trace to tool-payload values (or be plain Korean counting words
     — define the check pragmatically and record its limits honestly); derived
     values keep upstream 「추정」 tags; a won amount before 확정발행가 cannot
     appear because upstream never supplies one (Finding 6).
3. **Refusals (R6-7).** Family selection from tool results (철회 · 확정 전 ·
   공시에 없음 · 검증 미통과 폴백 · 계산 요청) — the five signed sentences
   transcribed into `copy.py` with provenance. 3-part structure as a typed
   event sequence: ① 상태 사실 with its own 근거 칩 (잠긴 카피 우선 — e.g. the
   withdrawn notice with the 철회 citation `get_event` prepends), ② the family
   sentence, ③ 갈 곳 링크 (DART 원문 rcept_no verbatim · 이벤트 상세 · 내 종목
   조회 — as link data for S5, not prose). Refusals are **not errors**: same
   prose path, citation-forced where they state verified facts. 확정 전 금액:
   answer the known cited facts, refuse only the amount. 계산 요청 → the fixed
   redirect sentence. **No per-reason-code wording** — a family is the most
   specific thing said.
4. **Typed event stream.** Define the vocabulary S4/S5 consume (suggested:
   `tool_row` · `text` (verified sentence/segment) · `citation` (chip, bound to
   the text it arrives with) · `footer` (근거 N건 · rcept_no list · 생성시각
   KST from the clock — composed data, prose is S5's) · `refusal` parts ·
   `done` · `aborted` / `error` (partial output stands — the stream never
   retracts released text) · a terminal carrying `evidence`/`quotes`/`kind`/
   `refusal_category` so S4 can `record_turn` without re-reading prose. Keep it
   serializable (dataclasses with a `payload()`), document it, and note it in
   `phase.md` for S4/S5.
5. **Scope.** `ctx.scope_rcept_no` set → the system instruction names the
   scoped event (범위: {종목} · {rcept_no}) and answers prefer it; unset →
   전체 공시. Scope never blocks the model from searching wider when the
   question demands it — it is context, not a filter the code enforces.
6. **The agent's own client + ledger.** Model `gemini-3.7-flash`, key from
   Settings/`.env` (mirror `mijual.config` conventions), lazy SDK import,
   per-call `Usage` recording (calls · tokens · thinking level · ▷ cost) into a
   per-turn ledger surfaced on the terminal event and loggable by S4. Thinking
   level: pick per D-4 (unlisted tasks run `LOW`; if you judge the agent's tool
   choice needs more, say which level and why in `phase.md` — the level must be
   recorded on every call either way). **Agent spend joins no signed ops
   panel** (Finding 14).
7. **Tests (terse, no live calls in the suite).** A scripted fake client
   (feed function-call parts, then text with markers) driving the real loop:
   multi-round tool use happens under model control; an unverified claim is
   blocked and degrades per your rule; verbatim-only quotes (a reconstructed
   quote in a marker fails); refusal families select correctly (철회 via the
   real `get_event` shape; 계산 요청 fixed sentence; 확정 전 partial answer);
   budget trips to the honest terminal event; same-근거-same-번호. Keep the
   suite green: baseline **126 passed**.
8. **Live smoke (allowed, bounded).** With `GEMINI_API_KEY` present you may run
   a **handful** of real calls (a scratchpad script, not committed into the
   suite) to verify the SDK path: declarations construct, the model actually
   calls a tool, a streamed answer passes the gate end to end. Report calls ·
   tokens · ▷ cost in `result.md` (D-4's reporting rule). If the key is absent,
   say so and rely on the fake-client tests; do not fail the slice on it.

## Boundaries

- No HTTP, no SSE endpoint, no route, no frontend, no `/ops` change, no turn
  persistence (S4 owns those). No import of `mijual.dart`/`mijual.collect`/
  `mijual.extract` in `mijual.agent` (scan-asserted). No invented Korean copy —
  transcribe from the record into `copy.py` with provenance. Quotes verbatim
  only. No quota concept anywhere. `docs/reference/design/` is read-only.

## Deliverables

- The loop + client + gate + events in `src/mijual/agent/` (new modules as you
  see fit), tests green (full `pytest`).
- `result.md` (include the live-smoke ▷ ledger if run).
- `phase.md` notes: the event vocabulary + terminal shape S4 consumes, the
  entry-point signature, the citation-gate rule chosen (block-vs-degrade), the
  thinking-level decision, client/ledger location; one-line **Doc impact** note
  (`architecture`, `backend`, `security`, `operations`, `decisions` candidates).
- `python3 scripts/workflow.py validate` passes. No commits, no status
  transitions.
