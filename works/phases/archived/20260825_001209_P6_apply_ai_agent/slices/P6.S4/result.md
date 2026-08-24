# Result — P6.S4: SSE transport + persistence + the request-path boundary

**Status: done.** The agent is on the wire. `POST /ask` streams `run_turn`'s typed
events as SSE, hands the anonymous handle back in frame one, stores one row per
turn, logs the ▷ line server-side, ships an identity-free rate limiter that says
nothing, and re-aims the architecture's loudest invariant so it stays true and
scanned. Measured incremental over `curl -N`, straight at uvicorn **and** through
the Next `/api` rewrite in both `next dev` and a production `next start` build.

Suite **130 → 136 passed**. No frontend change, no `/ops` change, no new column,
no Korean string invented, no live model call anywhere in the suite.

---

## What landed

| File | What |
|---|---|
| `src/mijual/web/ask.py` | **new** — the transport's decisions: SSE framing, request validation, the turn's own session/transaction, the terminal-or-frames persistence rule, the ▷ ledger line, `TurnLimiter` |
| `src/mijual/web/routers/ask.py` | **new** — `POST /ask`, the request model, the streaming response + its background task |
| `src/mijual/web/app.py` | `create_app(agent_client=…)` seam, `app.state.ask_limiter`, the ask router, the re-aimed OpenAPI description |
| `src/mijual/web/__init__.py` | the re-aimed request-path rule (three clauses, each named with the scan that keeps it) + the layout line |
| `src/mijual/web/routers/__init__.py` | one line for the new surface |
| `src/mijual/agent/__init__.py` | the re-aim recorded from the agent's side; "P6.S4 adds the transport" → what it actually did |
| `tests/test_web_ask.py` | **new** — 5 tests over the real endpoint with a scripted agent client |
| `tests/test_web_smoke.py` | scan re-aimed + **new scan**: `mijual.web` imports no model SDK |
| `tests/test_web_vocky.py` | scan docstring re-aimed (the HTTP clause is now precise) |

---

## The endpoint contract (for `P6.S5`/`P6.S6`)

`POST /ask` · `Content-Type: application/json` · `X-Mijual-CSRF` required
(service-wide guard) → `text/event-stream; charset=utf-8`, plus
`Cache-Control: no-store` and `X-Accel-Buffering: no`.

```json
{"question": "계양전기 증서 언제까지예요?",
 "scope_rcept_no": "20260724000546",
 "session": "23d2a24509faa06fb7c9088d8b70a6ee",
 "history": [{"question": "…", "answer": "…"}]}
```

`question` required. `history` is oldest-first prose, capped at the newest **8**
turns × 8 000 chars (dropped, not refused). Everything refusable is refused
**before** the response starts, in the ordinary envelope with no Korean:
`invalid_question` (400) · `invalid_scope` (400, not a 14-digit filing number) ·
`csrf_required` (403) · `rate_limited` (429) · `invalid_request` (422, pydantic).

Frames: `session` **first** (`{"session_hash", "scope"?}`), then the agent's own
events by their `frame()` — `tool_row` · `citation` · `text` · `refusal` · `links`
· `footer` — then exactly one terminal, `done` | `aborted` | `error`. Nothing is
reordered or invented: a `citation` is defined immediately before the `text` that
names its number.

---

## Validation

| Command | Result |
|---|---|
| `.venv/bin/pytest -p no:warnings` | **136 passed** (baseline 130 + 5 ask + 1 new boundary scan) |
| `python3 scripts/workflow.py validate` | `Workflow validation passed.` |
| `MIJUAL_API_ORIGIN=… npm run build` (frontend) | exit 0 — run only to get a production server for measurement D; **no frontend file changed** (`git status` clean under `frontend/`) |
| `curl -N` × 4 (below) | incremental in every topology measured |

The five new tests (`tests/test_web_ask.py`), all driving the **real** endpoint
over the **real** loop and **real** tools with `test_agent_loop`'s scripted model
through `create_app(agent_client=…)`:

1. the handle arrives first, the frames arrive in order, and the turn lands as
   one row whose fields equal the terminal's;
2. a 철회 refusal stores its family and a junk client token is replaced (and the
   fixture's chip is honestly the **API-tier** one — a citation, not a missing one);
3. a refusable request never becomes a stream (empty question · bad scope · no
   CSRF header) and writes no row;
4. a disconnected turn cannot disagree with a terminal — the frames-accumulation
   reproduces `kind`/`answer`/`refusal_category`/`evidence`/`quotes` exactly, and
   a 중지 before the first sentence stores nothing;
5. rate limiting refuses with **no copy at all** — 429, no `message_ko`, no row —
   and a lost slot expires instead of wedging the endpoint.

`GEMINI_API_KEY` is required neither to import nor to `create_app`: verified
directly — with the variable unset, `create_app(Settings())` builds and
`google` is absent from `sys.modules`.

---

## `curl -N` transcripts (the buffering measurement, Open Question 4)

Scripted agent (`create_app(agent_client=…)`), deliberate pauses between chunks,
real uvicorn. Timestamps are seconds since the first byte, stamped **per line as
curl emitted it**.

### A · straight at uvicorn (`http://127.0.0.1:8123/ask`)

```
  0.01s  event: session
  0.01s  data: {"session_hash": "23d2a24509faa06fb7c9088d8b70a6ee", "scope": "20260724000546"}
  0.83s  event: tool_row
  0.83s  data: {"tool": "search_events", "row": "이벤트 검색 「계양전기」 → 2건 · ① 유상증자 · 20260724000546 · ② 전환사채 · 20250820000220", "ok": true}
  1.64s  event: tool_row
  1.64s  data: {"tool": "get_event", "row": "이벤트 읽기 → 계양전기 · ① 유상증자 · 20260724000546", "ok": true}
  4.92s  event: citation
  4.92s  data: {"number": 1, "rcept_no": "20260724000546", "api_tier": false, "quote": "신주인수권증서의 상장·매매기간", "span": [10, 30], "field_key": "warrant_trading_period"}
  4.92s  event: text
  4.92s  data: {"text": "매매기간은 「신주인수권증서의 상장·매매기간」로 공시되어 있습니다.", "citations": [1]}
  6.54s  event: text
  6.54s  data: {"text": "같은 공시가 근거입니다.", "citations": [1]}
  6.54s  event: footer
  6.54s  data: {"count": 1, "evidence": ["20260724000546"], "generated_at": "2026-08-22T20:47:46+09:00", "links": [{"kind": "dart", "rcept_no": "20260724000546"}, {"kind": "event", "rcept_no": "20260724000546"}, {"kind": "dart", "rcept_no": "20250820000220"}, {"kind": "event", "rcept_no": "20250820000220"}, {"kind": "stocks"}]}
  6.55s  event: done
  6.55s  data: {"status": "done", "kind": "answer", "answer": "매매기간은 「신주인수권증서의 상장·매매기간」로 공시되어 있습니다. 같은 공시가 근거입니다.", "evidence": ["20260724000546"], "quotes": ["신주인수권증서의 상장·매매기간"], "blocked": 0, "rounds": 3, "tool_calls": 2, "usage": {"model": "gemini-3.7-flash", "calls": 3, "failures": 0, "prompt_tokens": 3000, "thoughts_tokens": 0, "output_tokens": 120, "total_tokens": 3120, "thinking_levels": ["LOW", "LOW", "LOW"], "cost_usd_estimate": 0.0027}, "scope": "20260724000546"}
```

Six distinct arrival times across 6.5 s. Nothing is buffered; the reader's
「답변 준비 중…」 ends at 0.83 s, not at the end.

Response headers (direct, and unchanged through the proxy):

```
HTTP/1.1 200 OK · server: uvicorn · cache-control: no-store
x-accel-buffering: no · content-type: text/event-stream; charset=utf-8
Transfer-Encoding: chunked
```

### B · 중지 — `curl --max-time 5.5`, cut mid-answer

```
  0.00s  event: session
  0.80s  event: tool_row      (search_events)
  1.62s  event: tool_row      (get_event)
  4.87s  event: citation
  4.87s  event: text          "매매기간은 「신주인수권증서의 상장·매매기간」로 공시되어 있습니다."
  ── connection closed at 5.50s; the second sentence (6.5s) never arrived ──
```

Server log: `agent turn disconnected · answer · rounds 0 · tools 0 · blocked 0 ·
… ▷ $0.0000 estimated`. Read back through the **real** R7 대화 로그 route:

```json
{"session_hash": "e7f2af4d7e0a3780bd14bafa3e1c3e5c", "at": "2026-08-22T20:48:03+09:00",
 "scope": "전체 공시", "question": "중지를 누르면 어떻게 되나요?", "kind": "answer",
 "answer": "매매기간은 「신주인수권증서의 상장·매매기간」로 공시되어 있습니다.",
 "evidence": ["20260724000546"], "quotes": ["신주인수권증서의 상장·매매기간"]}
```

Exactly the one sentence the reader received — see *A bug this measurement
caught* below. Two further requests cut at 1.2 s (before any sentence) logged
`disconnected` and wrote **no row**, which is the storable rule holding.

### C · through the Next `/api` rewrite, `next dev` 16.3.2 (Turbopack)

```
  0.00s  event: session      0.81s  tool_row      1.63s  tool_row
  4.89s  citation + text     6.52s  text + footer + done
```

### D · through the same rewrite on a production build (`next build && next start`)

```
  0.00s  event: session      0.81s  tool_row      1.62s  tool_row
  4.86s  citation + text     6.49s  text
```

**Answer to Open Question 4, for the topologies measured:** the Next rewrite
**does not buffer** SSE — dev and production timings match the direct ones inside
~30 ms, and `cache-control` / `x-accel-buffering` / `transfer-encoding: chunked`
all travel through untouched. What is **not** measured is P4's deployed topology
(an edge route, a CDN, or nginx in front); `X-Accel-Buffering: no` is set for the
nginx case, and P4/`P6.S7` still own the deployed check.

---

## A bug this measurement caught (and the rule that came out of it)

The first 중지 run stored **one sentence more than `curl` had been sent**: the
transport absorbed each event *before* yielding its frame, so the sentence
produced-but-never-delivered when the connection died still reached the row.

Fixed by inverting the order — an event is absorbed **after** its frame is
yielded. Being resumed past a `yield` is proof the consumer took the previous
frame and wrote it out, which is as close to "the reader saw it" as a server gets.
The transcript above is the re-measurement: one sentence sent, one sentence
stored. `AskTurn.frames()` carries the reasoning in its docstring.

---

## Decisions taken here

**No stop endpoint.** The `DECOMP` table said "ask · stop"; `P6.S3` decided 중지 =
closing the generator, and a stop endpoint would need a server-side turn registry
(a handle for a *running* turn) whose only job would be to cancel something the
socket already cancels. The reader aborts the fetch; nothing is retracted.

**The session is the transport's, not a dependency's.** A FastAPI `yield`
dependency is torn down when the *handler* returns — for a streaming response
that is **before the first frame**. So `mijual.web.ask` opens its own session
inside the body iterator and commits it from the response's background task, the
one hook Starlette runs on both exits (measured: it runs after a disconnect).

**Persistence policy — every terminal, plus any partial the reader actually saw.**
`done`/`aborted`/`error` all store, from `TurnEnd` alone. A disconnect has no
terminal, so the row is built from the frames that were written (identical fields
by construction — test 4). A 중지 before the first sentence stores nothing. The
row records **what the reader saw and nothing about the mechanism**: R7 signs the
columns and there is no status bit, so `aborted` vs `error` lives in the server
log, not in the anonymous log.

**Rate limiting: two ceilings, in process, holding no identity, saying nothing.**
`max_concurrent=6` (an integer, unevadable, the one that bounds spend) and 30
turns / 300 s per session handle (evadable by minting a handle — stated, not
hidden). No IP, no UA, no account, nothing written. 429 in the plain envelope with
no `message_ko`; zero UI copy anywhere. Per process — P4 owns cross-process state.

**Injection seam: `create_app(agent_client=…)`, a *factory*.** One client per turn,
because the call budget and the ▷ ledger are per turn. `None` → each turn builds
its own live `AgentGeminiClient`, key resolved on first use.

---

## Deviations from `plan.md`

- **No stop endpoint** (plan §1 asked for "endpoint(s)"; the `DECOMP` table said
  "ask · stop"). Reasoned above; the plan's own 중지 sentence is what was built.
- **The disconnect row is assembled from the frames sent**, not from `TurnEnd`
  alone — because a disconnect *has* no terminal. The terminal still wins wherever
  it exists, and the two are asserted equal.
- **No live model call was made from the endpoint.** `P6.S3` proved the client
  live; S4's live path (`agent_client=None`) is exercised for the first time in a
  browser at `P6.S5`/`P6.S7`. Worth knowing: the operator's dev Postgres does not
  yet have `conversation_turn` / `conversation_feedback` (P2 has no migrations —
  `create_all` runs from the collect/gates/pipeline entry points), so a local
  end-to-end run needs the tables created first.
- Everything else is as planned.

## Doc impact

One line appended to `phase.md` — `architecture` · `backend` · `api` · `security`
· `operations` · `qa`. No `docs/current/*` file was touched; `P6.REVIEW`
consolidates.
