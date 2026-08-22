# Result — P6.REVIEW: phase review of P6 (Apply — AI 질문 agent)

**Verdict: `pass`**, with **6 non-blocking findings** — every one of them an *operator
decision to surface*, none an implementation defect. **11 doc versions** consolidated.

The phase's keystone is the operator's mid-phase addition — *"we need to build a agent
not just llm chain"* — and it is met **structurally**, not rhetorically: the property is
checkable in one function's control flow, and I checked it rather than taking the phase
notes' word for it. The one place the phase falls short of R6's literal record is a
single answer-footer context link (**finding 1**), which cannot be built faithfully
without inventing behaviour the record does not write — so it is escalated, not fixed.

---

## 1. Validation — all fresh, all green

| Command | Result |
|---|---|
| `.venv/bin/python -m pytest` | **137 passed**, 2.87 s, 1 pre-existing httpx deprecation warning. No network, no model, no DB, **no `GEMINI_API_KEY`** |
| `cd frontend && npm run build` | **PASS** — 15/15 static pages, 16 routes incl. `/ask` |
| `cd frontend && npm run typecheck` | **PASS** — `tsc --noEmit` clean |
| `cd frontend && npm run smoke` | **PASS** — **15/15** `node:test` cases, 167 ms |
| `python3 scripts/workflow.py validate` | **PASS** (run again last, after the doc rebuild) |
| `pytest` **re-run after the `decisions` rewrite** | **137 passed** — the ops 개요 tab reads that doc, so it was re-verified rather than assumed |

### Spot-verifications (run directly, not read off the notes)

- **The four AST boundary scans exist and pass**, by name:
  `test_no_request_path_module_imports_a_spending_module` ·
  `test_the_model_is_reached_only_through_the_agent_package` (bans `google`/`openai`/
  `anthropic` under `src/mijual/web/**`) · `test_the_agent_package_imports_no_spending_module` ·
  `test_only_the_vocky_module_may_speak_http`. Run in isolation: **4 passed**. I read the
  first two — they walk the real package with a shared `_offenders` helper, and the re-aimed
  docstrings state the narrowed claim honestly rather than papering over it.
- **The anonymity test genuinely walks both tables.** It iterates
  `ConversationTurn.__table__` and `ConversationFeedback.__table__` columns against a
  forbidden-word list, asserts `not table.foreign_keys` on both, walks **every** foreign key
  in `Base.metadata` for one crossing the conversation boundary, and checks `Account` has no
  session/conversation column. The one signed exception (`conversation_feedback.email`) is
  spelled out inline, so a second one cannot arrive unnoticed.
- **Forbidden strings: clean.** No 「남은 질문」, no quota bar, no 소진 state on any ask
  surface. 「저장 이력 없음」 and 「탭을 닫으면」 appear only in `components/ask/copy.ts`'s
  comment explaining they are forbidden — and once as `components/auth/copy.ts`'s
  `CONVERT_SESSION_KO`, which is **P5's 보유량 conversion line** on a different surface under
  a different (correct) storage rule, exactly as phase note 12 warns. The `quota` hits are
  the ops DART budget bar (R7-signed) and comments.
- **`localStorage` in the ask surfaces: none.** Every `window.localStorage` call is in
  `lib/sample.ts` (P5's 샘플 포트폴리오). `lib/ask.ts` writes one `sessionStorage` key.
- **`docs/reference/design/` is byte-untouched by P6.**
  `git diff --stat 0f0bb23..HEAD -- docs/reference/` is **empty**, and so is
  `-- docs/` overall — so no slice versioned a doc either, which is the correct per-phase rule.
- **No `/ops` route or component changed**: `git diff --stat 0f0bb23..HEAD --
  src/mijual/web/routers/ops.py src/mijual/web/ops.py` is empty, and no
  `frontend/components/ops/*` file appears in the phase's diff. The three tabs came alive
  purely through the port's default implementation.

---

## 2. Judgment

### 2.1 Agent, not chain — **met, and checkable** ✅

The binding operator addition is the phase's acceptance criterion, so I read
`src/mijual/agent/loop.py` and its tests rather than trusting note 20.

- **No tool name appears in the control flow.** `run_turn` is
  `generate → (function_call? → execute → feed back) → repeat → answer`. `messages` starts as
  history + the question and nothing else — **nothing is prefetched**. The turn ends at
  `if not calls: break`, i.e. when the model emits a round with no function calls.
- **`call_tool` is invoked from exactly one place in the entire codebase**
  (`loop.py:213`, inside `_execute`), dispatching on `call.name` — the name *the model
  supplied*. Grepped repo-wide for direct tool invocations and for other `run_turn` callers:
  the only caller is `web/ask.py:480`. **There is no hidden forced call anywhere.**
- **The one place a forced call could have hidden, isn't.** `instructions.scope_line` resolves
  the reader's 범위 with a plain `resolve_event` row read, and its docstring states the reason:
  routing it through the tool loop *"would make one call in every scoped turn mandatory, which
  is the exact property this phase is not allowed to have."* That is the right call and the
  right reasoning. The tool notes are headed **"advice, not instructions — you decide."**
- **An unknown tool is told, not absorbed** — the model gets a structured error naming the real
  tool set and may correct itself; there is no sixth tool and no silent fallback.
- **The tests assert the property rather than the output.**
  `test_the_model_chooses_the_tools_and_chains_rounds_until_it_can_answer` asserts round 2's
  request contains round 1's `ToolMessage` — *the chain exists because the model asked for it*
  — and the 계산 요청 case asserts **`not of(events, ToolRowEvent)` and `tool_calls == 0`,
  commented as "the loop having no mandatory pre-fetch rather than the model being lucky."**
- Live evidence (S3 + S7): a different tool path per turn, and a self-corrected re-search after
  a 0건. Two bugs surfaced that only a real loop can hit (the SDK's per-call reasoning signature
  must be echoed back or round 2 dies; the model writes `…입니다.[[cite:c2]]` with no space).

**A scripted retrieve→prompt→answer pipeline could not produce any of the above.** This is a
genuine agent.

### 2.2 RESPECT THE DESIGN — **held**, with one signed element unbuilt ⚠

- **Nothing under `docs/reference/design/` was written in the whole phase** (verified by diff,
  not by claim). Three nits found during the pass were fixed **in code**, and the two record
  contradictions were surfaced as operator questions rather than resolved by an executor.
- I walked R6's `build-prompt.md` clause by clause against S7's 41-stage table. Every element
  has an owning, landed, *measured* implementation: 위젯 (440×620, opaque, no backdrop/dim,
  layout unchanged) · 런처 (68×50 + tail + the two-half-ring Saturn, **ring reading test passes
  by hit grid**) · 전용 페이지 (frameless, rail exactly 340px, no launcher) · 모바일 (**480/481
  boundary exact**) · 질문 스트립 · 범위 모델 · 도구 행 · 인용 칩 + 제자리 블록 + API-tier
  variant · 답변 푸터 · the four SSE states · 거절 5가족 3단 · 세션·저장 · 의견 · 런처 마크 ·
  every Hard rule.
- **Copy fidelity confirmed at source**, not via summary: all five refusal sentences in
  `agent/copy.py` are **byte-identical** to R6 `result.md` §Proposed copy, as are the SSE
  strings, the feedback confirmation, the 세션 line, 「이 공시에 대해 질문」 and 「검증된 필드만
  근거로 답합니다 — 모든 답에 원문 인용」.
- **The shortfall:** the 답변 푸터's third context link 「필드로 이동」 is signed and **not
  rendered**. It is not silently dropped — the string is documented in `components/ask/copy.ts`
  at exactly the place it would render, was flagged by S5, re-verified by S7, and escalated.
  See finding 1 for why this is a pass rather than a `changes_requested`.

### 2.3 The hard rules as acceptance criteria — **all met** ✅

| Rule | Verified how |
|---|---|
| Citation forcing is **structural** | `CitationGate.feed()` is called **inside the streaming loop**, sentence by sentence — a generation boundary, not post-processing. Four checks (resolvable id · has an id or is a verbatim tool string · every numeral traceable · every quoted span verbatim); a failure is **dropped, never marked**. Test exercises all four failure modes at once: 1 survivor of 5 |
| Never-compute | Enforced in the gate (numeral membership over tool payload values) **and** upstream — no tool computes a number. Live: **0 numerals unaccounted for** across 24 stored answers |
| Refusal families only | Five signed sentences, **exact-match** recognition (`family_of`), so a paraphrase is uncited prose and gets dropped. All five exercised live |
| Schema-level anonymity | The column/FK walk above; re-asserted against the real Postgres |
| No quota | Grepped; and the limiter returns `429` with **no `message_ko`** and zero UI copy |
| sessionStorage-only client persistence | One key, no `localStorage`, never a cookie; a restored in-flight turn settles to 중단 |
| Server-side anonymous storage feeds the ops tabs | `create_app`'s default is `DbConversations`; **no `/ops` route or component changed**; 24 real rows, both filters working on the five signed Korean names |
| `get_contact` honest-unset | `operator_contact` has **no default and no `require_` accessor**; unset → `{"configured": false}` + 미정. Covered by test |

### 2.4 The catalogued items — **none is phase-blocking**

I re-judged S7's 16 dispositions and 9 operator questions against the plan's test
(*something signed but missing* vs. *an operator decision to surface*):

- **필드로 이동** is the only "signed but missing" item, and it is **also** a genuine operator
  decision — see finding 1. Everything else is correctly catalogued.
- **철회 by name** (#12) is the exposure contract working as designed; changing it means
  re-deciding a contract this phase is explicitly forbidden to touch. Correct.
- **Raw numerals** (#10) is R6's *own* instruction (「검증 계약 값 그대로」) plus never-compute;
  "improving" it would have been the violation. Correct.
- **Refusal footer** (#13) and the **mobile menu row** (#7) are record ambiguities, judged with
  reasoning and surfaced. The mobile-menu judgement is right: §Surfaces states a position by
  ordinal, §Mobile's clause is a touch-target floor that is met.
- **Ops ISO timestamps** (#14) and the **log→sessions cross-link** (#16) are P5 surfaces under a
  P5 convention, and P6 was constrained not to touch `/ops`. Correctly out of scope.
- **▷ ledger invisible under default uvicorn** (#11) is a real deploy risk, correctly parked as
  P4's and now recorded in `operations` as an explicit deploy obligation.

### 2.5 Workflow hygiene — **clean** ✅

- All 9 slices have `plan.md` + `result.md`; 8 are `done`, `P6.REVIEW` is `in_progress`.
- Kinds/risks are consistent with the tier rule (every middle slice `high`, each writing real
  code across several files).
- **The Doc impact list is complete against the diff.** I cross-checked `git diff --stat
  0f0bb23..HEAD` against the list: 21 backend files and 27 frontend files, every one accounted
  for by an S1–S7 entry. Nothing changed durable truth without a line.
- No slice versioned a doc (`docs/` untouched for the whole phase) — the per-phase rule held.
- One observation for the orchestrator, not a defect: `phase.json` still reads
  `status: "planned"` while every slice is done. `validate` passes, and `review-phase P6
  --verdict pass` transitions it — flagged only so it is not mistaken for drift.

---

## 3. Findings (all non-blocking; every one needs an **operator decision**, not a fix slice)

1. **⚠ 「필드로 이동」 is signed and not rendered — the phase's one shortfall against the record.**
   R6 §인라인 인용 signs three footer context links; two ship. Building it faithfully is
   **impossible without invention**: the wire's link kinds are a closed set, the detail page has
   no per-field anchor, and — the decisive part — the record never says *which* field an answer
   citing several across several filings should point at. It is also entangled with finding 2:
   adding a third link type would make the already-dense row worse. Under RESPECT THE DESIGN the
   remedy for "signed but unbuildable without inventing" is an operator decision, not an
   executor's guess, and the phase surfaced it correctly rather than dropping it silently.
   **Recommended:** operator decides *draw it or strike it* (with finding 2 in the same breath);
   a `P6.F1` fix slice only makes sense **after** that decision, and only if the answer is "draw
   it". Recorded in `decisions` as the one still-open reading, so it appears on the ops 가동 전
   미결 panel.
2. **The answer footer's link row is denser than the signed line implies** — up to 7 links on 3
   lines, 「이벤트 상세」 repeated up to 3×, one possibly for a filing not among the 근거 (links
   come from what the turn *read*; the footer's facts name what it *cited*). Capping, restricting
   to 근거, or per-filing labels are all design calls. Not changed, because dropping links drops
   signed destinations and relabelling invents copy.
3. **A completed refusal renders a 푸터** (`근거 0건 · 시각` + 다시 질문) beneath the signed three
   parts. Honest, and the ③ links correctly render once — but R6 signs the footer under 답변 and
   gives 거절 its own anatomy.
4. **The agent prints raw contract numerals** (`3200원`) where every rendered surface formats them
   (`3,200원`). This is R6's own instruction plus never-compute, so it is correct as shipped; the
   open question is whether the *tool contract* should hand over presentation-formatted values.
5. **R6 contradicts itself on the mobile menu row** (§Mobile 「메뉴 첫 행」 vs §Surfaces 「nav
   세번째 자리」). Shipped as third in both nav and sheet, with the touch-target floor met. One
   line either way; the record's owner decides.
6. **Three deploy obligations P4 must not miss** (each now explicit in `operations`): create the
   two conversation tables before the first `POST /ask` (there are no migrations — every turn
   fails otherwise); preserve `Cache-Control: no-store, no-transform` + `X-Accel-Buffering: no`
   through every proxy hop **and** keep idle timeouts above ~10 s (no heartbeat; 6.0 s observed
   inter-frame gap); install a root logging configuration or agent spend is recorded nowhere.
   Plus the operator's own `MIJUAL_OPERATOR_CONTACT` value.

**No proposed fix slices.** Findings 1–5 are decisions only the operator can take; finding 6 is
P4's inherited work, already recorded where P4 will read it.

---

## 4. Doc versions created (11)

Consolidated from the phase's Doc impact list (S1–S7). Each version is a **full document** —
latest read first, what still holds carried forward, the phase integrated — never a changelog.
`docs/current/*` was regenerated by `rebuild-docs` and **never hand-edited**.

| doc | version |
|---|---|
| `architecture` | **v0004** — the `mijual.agent` package, the re-aimed boundary as three scanned clauses, the loop as architecture, the conversation tables, the `no-transform` proxy fact |
| `backend` | **v0003** — the agent package module by module, the five tools' contract, the three new `reads` loaders, the streaming section (BackgroundTask commit, absorb-after-yield, abort persistence, no stop endpoint, the limiter) |
| `api` | **v0003** — the whole `POST /ask` contract incl. the frame vocabulary and its ordering rule, the session-first handle, kinds-not-URLs, the pre-stream envelope; the ops port filled with no route change |
| `data` | **v0005** — a new *Conversation Tables* section: the signed columns, the minted handle, the rejected-at-write vocabulary, and the **not-re-collectable** migration rule |
| `security` | **v0004** — the anonymity promise moved from *trivially true* to *asserted*, the identity-free limiter, sessionStorage-only persistence, honest-unset contact |
| `product` | **v0005** — *What P6 added: the AI 질문 agent*, in product terms; the whole designed product is now built |
| `experience` | **v0004** — the AI 질문 journey as built and browser-measured; the launcher/motion exception; the rail-contents and mobile-menu readings |
| `frontend` | **v0004** — a new *AI 질문 surfaces* section (module-scoped store, two views one store, the two scope setters, the pure SSE decoder) + three new engineering traps |
| `operations` | **v0006** — agent spend as a ▷ server-log line and why it is invisible by default; the three tabs alive; three deploy obligations; `MIJUAL_OPERATOR_CONTACT` |
| `qa` | **v0004** — suite at 137, *testing a non-deterministic component deterministically*, the four boundary scans + anonymity scan in the regression checklist, three new browser traps |
| `decisions` | **v0006** — **D-20** agent-not-chain (operator, verbatim, 2026-08-22) · **D-21** the boundary re-aimed not relaxed · **D-22** the contact honest-unset; **D-4** gains the `agent_turn` LOW row with its measurement, **D-10**'s SSE clause lands; plus *P6 readings of the record* |

### ⚠ The ops 개요 open-bullet re-check (`P5.REVIEW` note 8)

The 개요 tab parses `docs/current/decisions.md` for `- **Open…` bullets, so I rendered it after
the rewrite rather than assuming:

```
available: True | doc version: v0006 | open bullets: 3
  D-4  — Application LLM …                     : the unattended 정정 해석 thinking level (unchanged)
  D-22 — The 운영자 연락처 string …             : the string itself is still unset
  P6 readings of the record — …                : 「필드로 이동」 signed but not built
```

**1 → 3, and each renders with a sensible decision label, title and verbatim body.** The two new
bullets were chosen deliberately: both are items **only the operator can close**. P4's engineering
to-dos (create the tables, preserve the headers, configure logging) were kept **off** this panel
and put in `operations` instead — they are 미완, not 미결, and the panel's own docstring scopes it
to items "not decided yet". `pytest` was re-run after the rewrite: **137 passed**.

---

## 5. Deviations from `plan.md`

**None.** One note on method: the plan's judgment area 4 asked whether any catalogued item is a
phase-blocking gap. I found one item that is genuinely "signed but missing" (finding 1) and judged
it **non-blocking** because closing it requires inventing behaviour the record does not specify —
which RESPECT THE DESIGN forbids more strongly than it forbids an escalated gap. That judgement is
the review's to make and is recorded in full above and in `decisions` v0006 so it cannot be lost.

Also per the plan: **no commit, no `review-phase`, no `finish-slice`, no status command** — the
orchestrator records the verdict. `python3 scripts/workflow.py validate` was run last and passed.

**explain:** not written — run `/explain` for this phase.
