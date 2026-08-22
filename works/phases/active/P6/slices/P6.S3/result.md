# Result — P6.S3: agent core — the autonomous Gemini function-calling loop

**Status: done.** The agent exists, it is an agent, and it was watched deciding
things against the live corpus and the real model. `pytest` **130 passed**
(baseline 126 + 4), `python3 scripts/workflow.py validate` passes.

## What landed

Six new modules under `src/mijual/agent/`, plus the five signed refusal sentences
transcribed into the package's existing `copy.py`:

| Module | What it owns |
|---|---|
| `loop.py` | **`run_turn(ctx, question, history=(), *, client=None, budget=None, now=None) -> Iterator[AgentEvent]`** — the turn. `generate → (function_call? → execute → feed back) → repeat → answer`, plus the fact rows, the fallback family, the 갈 곳 links, the footer, the budget and the terminal. |
| `client.py` | The agent's **own** streaming Gemini client (`AgentGeminiClient`), the `ModelClient` protocol, the neutral message/chunk types the loop speaks, `CallBudgetExceeded`, `Usage`/`UsageLedger`/`Pricing` with ▷ cost. |
| `citations.py` | `CitationGate` — 인용 강제 at the generation boundary, the never-compute check, the verbatim-quote check, chip numbering. |
| `events.py` | The typed event stream: `tool_row` · `citation` · `text` · `refusal` · `links` · `footer` · `done`/`aborted`/`error`. |
| `instructions.py` | The system instruction. It **advises**; no tool name appears in control flow. |
| `copy.py` (edited) | `REFUSAL_SENTENCES` (the five, verbatim), `REFUSAL_FALLBACK`, `family_of()`, `AGENT_INTRO_KO`, `FEEDBACK_SAVED_KO`. |

`tests/test_agent_loop.py` (4 tests) drives the **real** loop with a scripted
`ModelClient` over the same in-memory corpus `test_agent_tools.py` builds.

## Agent, not chain — how it is checkable rather than asserted

`loop.py` contains **no tool name in its control flow**: nothing is fetched
before the model speaks, nothing after, and no ordering is imposed. The loop ends
a turn when the model emits a round with no function calls. Three of the four
tests are exactly this property:

- `…chooses_the_tools_and_chains_rounds…` — round 2 is decided *after* round 1's
  result went back to the model (asserted on the messages the client actually
  received), so the chain exists because the model asked for it;
- the 계산 요청 case asserts **zero** tool rows and `tool_calls == 0` — a scripted
  pre-fetch would fail here;
- the budget case asserts the loop keeps going as long as the model keeps asking,
  until a ceiling stops it honestly.

Live, the model chose differently every time and was never told to: search →
get_event → answer; get_event alone; get_portfolio alone; and, on a 0건 search,
it **re-searched with a corrected query on its own** before refusing.

## The citation gate (the rule chosen, and why)

Structural, not prompt-trust. Each tool result is `learn`-ed: its `Citation`s get
reference ids (`c1`, `c2`, …) that travel back inside the function response, so
the citable space is **closed** — there is no id for a filing no tool returned.
Streamed text goes into the gate, not to the reader. Per sentence:

1. every marker id must resolve, or the sentence dies (a fabricated id is worse
   than a missing one — it looks verified);
2. a sentence with no resolving marker is released **only** if it is verbatim a
   string a tool returned (the signed 0건 sentence, a 잠긴 `notice_ko`, a 본문
   quote). A result naming exactly one filing lends that string its citation, so
   「이 유상증자는 철회되었습니다」 carries a 근거 칩 — R6's 「거절도 인용 강제」;
3. every numeric token must appear among the tools' own values;
4. every 「…」/"…" span must occur verbatim in something a tool returned.

**Degrade rule chosen: drop-not-fail.** A blocked sentence is dropped — never
emitted, never marked (a visible hole would be a placeholder chip by another
name). If a turn ends with **nothing** released, the loop states the 검증 미통과
폴백 family itself. The blocked count rides the terminal so the rate is
observable. A budget/error abort is *not* turned into 폴백: saying 「이 데이터는
검증을 통과하지 못했습니다」 after a timeout would be a false statement about the
data.

**Chip protocol:** two id spaces. The model cites `c7` (assigned when the tool
ran); the reader sees chip `1` (assigned on first use in the answer). So chips
are numbered in reading order, 같은 근거 = 같은 번호, and the model never has to
manage the reader's numbering. A `citation` event is emitted **before** the
`text` event that names it — a definition, so the renderer can paint the chip in
the same frame as its sentence (칩은 주장과 동시에 도착, 후행 부착 없음).

## Validation

| Command | Outcome |
|---|---|
| `.venv/bin/python -m pytest` | **130 passed**, 1 pre-existing warning (baseline 126) |
| `.venv/bin/python -m pytest tests/test_agent_loop.py` | 4 passed |
| `python3 scripts/workflow.py validate` | `Workflow validation passed.` |
| live smoke (scratchpad, not committed) | 5 turns over the live corpus + real model — see below |

### Live smoke — ▷ ledger

Scratchpad script, **not** in the suite. Five question turns over the live
Postgres corpus with `GEMINI_API_KEY` present, plus one debug call and one
pre-fix run:

```
run A (pre thought_signature fix)  6 calls   7,448 tokens  ▷ $0.0068
debug repro                        1 call        —         ▷ ~0
run B (fix in)                     7 calls  38,495 tokens  ▷ $0.0352
run C (post sentence-cut fix)      7 calls  38,256 tokens  ▷ $0.0344
run D (철회 + 0건)                  5 calls  13,802 tokens  ▷ $0.0136
run E (철회, instruction tweak)     2 calls   5,433 tokens  ▷ $0.0042
────────────────────────────────────────────────────────────────────
total                             28 calls ~103,434 tokens ▷ $0.0942
```

All at thinking level **LOW**, recorded on every call. Every figure is a ▷
estimate off the D-4 rate card, never a billed amount.

What the live runs showed (all `blocked == 0`, so the model met the protocol at
LOW without the gate having to drop anything):

- `대동기어 전환사채는 언제부터…` → search → get_event → 2 cited sentences,
  `근거 1건`, D-63 quoted from the countdown (not computed);
- `이 유상증자 발행가는 얼마인가요?` (scoped to 계양전기 `20260724000546`) →
  **exactly R6-7's 확정 전 shape**: the known facts cited (1차 발행가액 반영
  예정발행가액, 최종 발행가액 공시 예정일 with the 확정 발행가액 공식 as a verbatim
  chip), then 「확정 전 금액은 해설하지 않습니다.」, then 갈 곳;
- `300주 가지고 있으면 얼마 받을 수 있나요?` → get_portfolio (샘플, 구성 예시),
  one cited holding sentence, then the fixed 계산 요청 redirect;
- `썸에이지 20260805000454…` → 「이 유상증자는 철회되었습니다.」 with its chip →
  「철회된 공시는 해설하지 않습니다.」 → 갈 곳. The signed 3-part refusal, live;
- `삼성전 유상증자 있나요?` → 0건, the model retried `삼성전자` itself, then the
  signed 「「삼성전」에 해당하는 공시를 찾지 못했습니다」 + 공시에 없음.

`declarations()` — S2's one untested path — constructs correctly against
google-genai 2.18.1 and the model called all five shapes it was offered.

### Two defects the live smoke found (both fixed here)

1. **`400 INVALID_ARGUMENT` on every second round.** Gemini 3.x requires the
   `thought_signature` bytes attached to a function-call part to be **echoed back**
   in the conversation history. `ModelCall` now carries it opaquely and `_contents`
   replays it. Without this the agent could not chain a single round — a
   chain-shaped implementation would never have hit it.
2. **The whole answer arriving as one sentence with every chip at once.** The live
   model writes `…입니다.[[cite:c2]]` with *no space* after the full stop, and the
   sentence boundary required whitespace. `_SENTENCE_END` now also cuts before a
   marker; a trailing loose full stop left by marker removal is closed at the end
   of a sentence only (never inside a 「verbatim」 span).

## Deviations from `plan.md`

- **`evidence`/`quotes` on the terminal are the chips the reader saw**, not the
  union of every tool result (note 19 suggested the union). R7's column is 「인용
  칩 원문」, so the log replays the answer rather than the research. `ToolResult`'s
  own `.evidence`/`.quotes` are untouched and still available to `P6.S4`.
- **One terminal shape, three statuses** (`TurnEnd.status`) rather than three
  event classes. `TurnEnd.event` returns the status, so the SSE names are still
  `done` / `aborted` / `error`.
- **The `links` event carries no href.** R6 asks for 「DART 원문 rcept_no
  verbatim · 이벤트 상세 · 내 종목 조회」; the routes for those belong to
  `frontend/lib/routes.ts` and `lib/api.ts`. Serving `{kind, rcept_no}` keeps one
  owner per route and makes it impossible for the agent to point at a page that
  does not exist. (Related nit found and **not** fixed here — see the phase note
  on `BOARD_POINTER_HREF`.)
- **No `changes` to `mijual.extract`, and nothing lifted into a neutral module.**
  The budget + ledger ideas are copied into `mijual.agent.client`, as Finding 1
  prefers; the two clients diverged immediately (JSON vs. streamed tool calls), so
  a shared base would have been a shared constraint.
- Thinking level: **`LOW`** (D-4's rule for an unlisted task), recorded on every
  call, and measured — see the phase note.

## Boundaries respected

No HTTP, no SSE, no route, no persistence, no frontend, no `/ops` change. No
import of `mijual.dart` / `mijual.collect` / `mijual.extract` (the S2 AST scan
still passes over the enlarged package). No Korean sentence invented — the five
families and the intro are transcribed with provenance. `docs/reference/design/`
untouched. No quota concept anywhere. No commit, no status transition.
