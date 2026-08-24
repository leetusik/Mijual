# Result — P6.S2: the five agent tools (`mijual.agent`)

The package exists and the five tools return verified-contract values only. No
model call, no HTTP, no SSE, no frontend change, no `/ops` change — and no number
computed anywhere in it.

## What landed

**`src/mijual/agent/`** (new top-level package, per Finding 1):

- `context.py` — `ToolContext`: `session` · `today` (KST) · `session_hash` ·
  `account | None` · `scope_rcept_no | None` · `settings | None`. No tool takes
  an identity or a holdings payload; `get_portfolio()`'s whole argument list is
  the context, which a signature test pins.
- `tools.py` — `search_events` · `get_event` · `get_portfolio` · `save_feedback`
  · `get_contact`, plus `Citation` / `citations_in` / `ToolResult` / `call_tool`.
  Every value comes back from `mijual.web.reads` + `mijual.present` untouched:
  「추정」 tags, absent-means-absent, quote/span/rcept_no triples and the API-tier
  handle all survive because nothing re-derives them.
- `copy.py` — the Korean strings with per-constant provenance (signed vs.
  composed; see the phase note and *Deviations* below).
- `declarations.py` — `TOOL_SPECS` (plain JSON-Schema data) + `declarations()`
  with a **local** `google.genai` import, so the package imports with no SDK
  installed and no credential present.

**`src/mijual/config.py`** — `Settings.operator_contact` /
`MIJUAL_OPERATOR_CONTACT`, no default and deliberately no `require_` accessor.

**`src/mijual/web/reads.py`** — three additions, all public and all in the read
layer where the derivation already lives:

- `event_payload(session, detail)` — the detail card's assembly, **moved out of
  `routers/events.py`** so the route and the agent's `get_event` return one
  payload rather than two that drift. `GET /events/{rcept_no}` is unchanged byte
  for byte (its five existing tests still pass untouched).
- `find_corps(session, q, limit=5)` — the multi-candidate lookup R6's tool needs,
  with `resolve_corp`'s exact normalization and tier order (Finding 15).
- `load_corp_events(session, codes, today=)` — exposable events as `EventView`s,
  batched through the same `_load_views` 조회/포트폴리오 use, gated twice.

**`src/mijual/web/routers/events.py`** — the route is now one line over
`event_payload`; the two moved helpers are gone from it.

**`tests/test_agent_tools.py`** — five terse cases over one in-memory corpus
(an ① with no 확정발행가, an open ②, a 철회된 filing): search lists/ranks/declines
with the signed line, `get_event` carries citations and no money, anonymous
`get_portfolio` serves the labelled sample, feedback lands and 연락처 stays 미정,
and the third AST scan (`mijual.agent` reaches no spending module).

## Validation

| command | outcome |
|---|---|
| `.venv/bin/python -m pytest` | **126 passed**, 1 warning (baseline 121 → +5) |
| `.venv/bin/python -m pytest tests/test_web_board.py` | 5 passed — the detail route after the assembly moved |
| `python3 scripts/workflow.py validate` | `Workflow validation passed.` |
| live-corpus smoke (Postgres, 0 spend, 12–52 ms/call) | see below |

Live corpus, 2026-08-22 (scratchpad script, not committed):

```
이벤트 검색 「대동기어」 → 2건 · ② 전환사채 · 20251016000315 · ① 유상증자 · 20260715000369
이벤트 검색 「계양」 → 1건 · ① 유상증자 · 20260724000546
이벤트 검색 「존재하지않는회사」 → 0건 | 「존재하지않는회사」에 해당하는 공시를 찾지 못했습니다
이벤트 읽기 → 계양전기 · ① 유상증자 · 20260724000546   (3 verbatim quotes, no won amount)
내 포트폴리오 읽기 → 샘플 포트폴리오 · 4종목 (구성 예시)  (15 quotes · 7 근거)
운영자 연락처 → 미정
20260805000454 → state=withdrawn · 이 유상증자는 철회되었습니다
    citation: quote 「유상증자 철회」 span [3445, 3461]
```

Also verified: `import mijual.agent` leaves `google` out of `sys.modules`
(google-genai is not installed in this venv at all).

## Deviations from `plan.md`

1. **The plan allowed a new query; it also got a small refactor of an existing
   file.** `get_event` had to return "the verification contract for one event",
   and the only existing assembly of that lived inline in the events router. I
   moved it to `mijual.web.reads.event_payload` and made the router call it
   rather than writing a second assembly in the agent — the phase's "no endpoint
   re-derives" constraint reads as strongly against two payload shapes for one
   event. Behaviour unchanged; existing tests untouched and green.
2. **Three of the five fact rows are composed, not transcribed** — the record
   signs one format and three examples, and there are five tools. `get_event`,
   the authenticated `get_portfolio` and the `save_feedback` failure row are
   built in the signed `{도구} → {결과}` grammar from signed vocabulary only
   (`읽기` · `재시도` · `미정` · `0건`), and `RIGHTS_TOOL_LABEL_KO`'s ① and ③
   follow R6's own `② 전환사채`. Every one is marked *composed* in `copy.py` with
   its reasoning, and the phase note flags them for `P6.S7`/`P6.REVIEW` to
   confirm against the record. No sentence was invented and no tool writes prose.
3. **One machine hint added to a 0건 search** (English, model-facing, not copy):
   a 14-digit query that finds nothing tells the model to call `get_event` first,
   because a 철회된 event is readable by number without being searchable. Without
   it the agent would answer 「찾지 못했습니다」 about an event that has a page and
   a locked 철회 notice — the weaker of two true statements.
4. **`declarations()` is not exercised.** google-genai is absent from this venv,
   so the specs are pinned by test and the SDK construction is left for `P6.S3`'s
   first live call (recorded in the phase note, with the one-function fallback if
   the SDK prefers `parameters_json_schema`).

## Phase notes

Appended to `works/phases/active/P6/phase.md` as **note 19** (the `ToolResult`
shape S3 consumes, the `ToolContext` contract S4 constructs, the Settings field
name, the search/ranking/cap decisions, the copy provenance, and the live
measurements) and one **Doc impact** line naming `architecture` · `backend`
(+ `api`, `operations`, `security`) for `P6.REVIEW` to consolidate.

No commit, no status transition, nothing under `docs/reference/design/` touched.
