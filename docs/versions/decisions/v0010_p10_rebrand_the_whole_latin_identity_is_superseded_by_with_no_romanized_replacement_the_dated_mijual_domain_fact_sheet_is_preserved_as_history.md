---
doc_id: decisions
version: v0010
created_at: 2026-08-30T03:14:21+09:00
source: P10.REVIEW
summary: P10 rebrand — the whole latin identity is superseded by 주주의관제탑 with no romanized replacement; the dated mijual domain fact sheet is preserved as history
previous: v0009_p9_r16_supersessions_thinking_mid_strip-don_t-drop_the_auditable_calculator_replacing_never-compute_six-value_refusal_vocabulary_with_two_producers_retired_and_the_ask_re-cut
---

# Decisions

## Status

Five operator decisions from the P1 scope gate (2026-08-19) remain binding. P2 adds three more
(D-6 … D-8), **amends D-4**, and closes four of P1's open questions with measurements. **P3 adds
D-9 … D-15** — the design-gate decisions, every one of them made by the operator in a Claude Design
session and closed with literal signoff (`docs/reference/design/SIGNOFF.md`). **P5 adds D-16 … D-19**
— engineering decisions taken while building the signed design, recorded because each one closes a
question a later phase would otherwise reopen, and **closes D-15**. **P6 adds D-20 … D-22** and
amends **D-4** and **D-10**: one of the three is an operator decision that arrived mid-phase and was
binding on the architecture (**D-20**), and one records an invariant that had to be rewritten rather
than allowed to quietly become false (**D-21**). **D-23** was added after P6's first review pass, on
a second operator disposition, and supersedes one of the phase's own readings of the record.
**P7 (실서비스 정상화) adds D-24 … D-26** — three engineering decisions taken under explicit operator
overrides of the signed record — plus six readings of the record and, most importantly, a **catalogue
of thirteen calls that are the operator's** and were routed rather than invented. Later phases follow
what is written here, not the alternatives that were weighed.

## Decision Log

### D-1 — MVP rights scope: keep all three types

- **Date:** 2026-08-19 · **Status:** accepted (operator, verbatim: "keep all")
- **Decision:** the MVP ships **① 유증 신주인수권 (the hero) + ② CB 오버행 + ③ 매수청구권**, with the
  exclusions standing: **EB — out**; **분할합병 · 주식교환·이전 — out**; **제3자배정 유증 — filtered
  out**; **소규모합병 — suppressed** (publishing it would be a correctness bug).
- **Condition attached and funded:** ② needed a **CB backfill to ≥ 2025-06**. **Done in P2.S7** —
  2025-06-01 → 2026-08-20, 530 CB originals + 1,181 기재정정, 673 events, 584 live requests. The
  urgency it was bought for exists: **33 ② events open 전환청구 within 30 days of 2026-09-07, 82 within
  90, 152 within 180, max 오버행 67.8 %** — against 1 before the backfill.
- **Consequences:** drop order under deadline pressure is **EB → ②'s backfill → ③ → ②, ① last**.
- **Source:** `works/phases/active/P1/slices/P1.S2/recommendation.md`; P1 finding F25.

### D-2 — Custom domain: deferred, nothing purchased

- **Date:** 2026-08-19 · **Status:** accepted (operator, verbatim: "I'll get you a domain later.")
- **Decision:** no domain was bought; the operator will supply one later. A custom domain is a
  branding choice, not a submission requirement.
- **Consequences:** plan for a platform hostname; any operator-supplied domain must be **wired before
  the deployment freeze** (see `operations`). Fact sheet below.

### D-3 — Challenge registration: done

- **Date:** 2026-08-19 · **Status:** accepted (operator, verbatim: "I registered")
- **Consequences:** only the 제출 steps remain — and uploading is not 최종 제출. ▷ Not verifiable from
  this workspace; taken on the operator's word.

### D-4 — Application LLM: Gemini 3.7 Flash on the "changple5" credential — **amended 2026-08-20**

- **Date:** 2026-08-19, amended 2026-08-20 · **Status:** accepted (operator)
- **Original decision:** the reading (schema extraction) and speaking (grounded generation) layers run
  on **Gemini 3.7 Flash at high thinking**, via the operator's "changple5" credential.
- **Concretised by P2.S4:** the model id is **`gemini-3.7-flash`** (`models.get` → `3.7-flash-08-2026`),
  the credential is `GEMINI_API_KEY` in the gitignored `.env` and reaches only the SDK, and the
  thinking level was a **project-side preset** (a no-config probe returned thought tokens). ▷ Cost
  basis recorded: **$0.75 / $3.75 per 1M in/out tokens**, thinking billed as output; every run reports
  calls / tokens / **▷ estimated cost** and never claims a billed figure.
- **Amendment (operator, 2026-08-20): the thinking level is per task — `LOW` for routine schema
  extraction, the project preset reserved for reasoning.** Mechanism:
  `ThinkingConfig(thinking_level=MINIMAL|LOW|MEDIUM|HIGH)` (not the older `thinking_budget`), and
  **omitting the field entirely** is what inherits the preset. Measured on one real extraction prompt:
  preset **866** thinking tokens → explicit `LOW` **0**, **−21 % ▷ cost**, with **every gated value
  identical** (only free-text prose wording differed).
- **Policy as implemented:** the three prose tasks and any unlisted task run `LOW`; the **정정 해석**
  task keeps the preset, because it is the only task that reasons and its quality measurement was
  taken there. Every call records the level it ran at (`extraction_call.thinking_level`) — a ▷ cost
  figure is only comparable across runs if the level behind it is known.
- **P6 added the `agent_turn` task at `LOW`; P9 raises it to `MID`, and the third of P6's three
  reasons is *why*.** P6's argument was: the surface is free and unlimited (R6-5), so per-turn cost is
  the product's; streaming makes first-token latency reader-visible and thinking precedes it; and 인용
  강제 / never-compute / 거절 가족 were enforced **structurally**, so a cheaper level could only produce
  a *blocked* claim. **That third leg died with strip-don't-drop** (D-27 below): once nothing is
  blocked, a cheaper level no longer degrades safely — it degrades into wrong prose that ships. The
  second leg was measured away too: vendor figures put thinking's cost at roughly **one second** of
  first-token latency, while this product's real wait is the tool round trip. So `agent_turn` runs
  **MID**, which on the wire is the SDK's **`MEDIUM`** — `types.ThinkingLevel` has no `MID`, and
  `ThinkingConfig(thinking_level="MID")` does not raise locally: it warns and carries the string to
  the API, where the call is rejected in front of a reader. The phase's word and the API's word are
  reconciled once, in one constant. **Measured live at MID:** `thinking MEDIUM` end to end, turn cost
  **$0.0046** (a greeting) to **$0.0548** (a 6-round, 5-tool calculation at 63k prompt tokens).
- **The ▷ cost basis gains a cached-input rate, and caching is now measured rather than assumed.**
  `Usage.cached_tokens` (from the SDK's `cached_content_token_count`) rides the ledger end to end and
  is priced at **¼ of the input rate**, printed *inside* the prompt count because it is a subset.
  Across every live P9 turn the reading is **`cached 0`** — including the same question repeated
  minutes apart, against a ~5.5k-token static prefix that should clear Gemini's 4,096-token implicit
  floor. That is an honest reading of a real number and an open operator question, not a claim that
  caching never happens; it is exactly why the field was added instead of the reorder being assumed
  to pay.
- **`temperature = 0.2` is now a recorded choice, not an unexamined default** (changple5 runs its
  chat model at `0.0`): this surface is a *conversation*, and the same question twice should not come
  back word for word. Nothing that must not vary depends on the sampler — signed sentences are quoted
  from `copy.py` rather than generated, figures are respelled from `value_display`, and an untraced
  number is marked whatever the temperature.
- **Open, and operationally load-bearing:** an unattended beat run would make that preset choice for
  a human. Decide (or cap the 정정 task) before a worker runs in production — see `operations`.
- **Cost structure that follows:** calls are grouped **one per document, not per field** (five ①
  fields in one call: 28 calls instead of 140), re-running is free (stored fields are skipped), and
  span re-resolution is a separate **0-call** pass. Phase total, read from `extraction_call`:
  **213 calls, 2,025,260 tokens, ▷ $2.79, 0 failures.**

### D-5 — Schedule management is operator-owned

- **Date:** 2026-08-19 · **Status:** accepted (operator, verbatim: "you don't need to worry about the
  schedule. I'll handle it. only focus on building")
- **Consequences:** the calendar conflicts surfaced during recon must not be re-raised or planned
  around. This does **not** relax the 결격 uptime window — that is a property of the service.

### D-6 — Data-backbone stack: plain Python package + Postgres + Celery beat; FastAPI deferred to P3

- **Date:** 2026-08-19 · **Status:** accepted (operator, folded into the P2 decomposition gate)
- **Decision:** P2 builds a **plain Python package** (collector / parser / extractor / gates /
  estimation) persisting to **Postgres via SQLAlchemy**, with **Celery beat + a Redis broker** for
  scheduling. **No FastAPI endpoint is written in P2** — the HTTP layer is P3's and reads persisted
  snapshots only.
- **Context:** resolves the handoff §6-5 "reuse the operator's stack" preference and `intent.md`'s
  deferred architecture choice.
- **Consequences:** the P2 → P3 boundary is the persisted **exposure contract**, not a function call
  (see `architecture`); **no Alembic** — the corpus is re-collectable, so `create_all` plus an
  add-only `ensure_columns` replaces migrations; ② rides the ordinary collector, so scheduling it cost
  no new task and no new beat entry.

### D-7 — Extraction accuracy is measured by **cross-model judging**, not by human ground truth

- **Date:** 2026-08-20 · **Status:** accepted (operator, verbatim: "you self evaluate and self
  validate. since the extraction done by gemini and you are a claude fable. try by yourself.")
- **Decision:** the P2 evalset's 344 labels were produced by **Claude (Opus 5) judging Gemini
  extractions**. The human labelling pass the slice had planned was replaced by this.
- **Consequences, and they are binding on every future claim:** every doc, deck or page quoting an
  accuracy number **must carry the cross-model qualifier**, no artifact may describe these labels as
  human ground truth, and the phrase "hand-labelled" is forbidden for them. The qualifier is
  **mechanised, not just prose**: `evalset/labels.json` carries a `judged_by` block
  (`judge` / `basis` / `imported_at`), `Labels.write()` refuses to write an unstamped file,
  `import --judged-by` is required and **never inherited** from the previous file (a human re-judging
  rows must not keep a machine's stamp), and the report prints what the file says rather than a
  hardcoded sentence.
- **The human path stays open and cheap:** overwrite column A of `evalset/sheet.csv` and re-run
  `import` with a new `--judged-by`; the same report then states the new judge.

### D-8 — The conservative default, stated as a pair

- **Date:** 2026-08-20 · **Status:** accepted (engineering decision, recorded at P2.S5)
- **Decision:** conflicting evidence is **not a reason to delete an event** (never suppress on a
  conflict) and **not a reason to publish it** (never expose on a conflict). A blocked event keeps
  every snapshot, extraction and gate verdict and is simply not rendered.
- **Companion rule:** a skipped check is never a pass. The four-state verdict
  (`passed`/`failed`/`tbd`/`not_evaluable`) exists so that "we could not check" can never be
  mistaken for "we checked and it was fine".
- **Consequence:** **all displayed arithmetic is one deterministic module** (`mijual.calc` — D-day in
  KST, inclusive windows, floored 단수주, Decimal 원 rounded once), which is handoff §3.6's
  *계산은 결정론* clause in code.

### D-9 — P3 is **design-only**; the build moves to a separate apply phase

- **Date:** 2026-08-20 · **Status:** accepted (operator, verbatim: "make this phase design only. one by
  one. we have nothing to hurry. vocky will be added as feedback inception, admin panel required, auth
  related required.")
- **Decision:** P3 runs `DECOMP` → seven `co-work` design rounds, one at a time, each with its own
  handoff and `pending` gate → `REVIEW`. **No `DECOMP2`, no build slices, no implementation code in
  P3.** Scope additions in the same breath: the **vocky** feedback touchpoint, an **admin panel** and
  the **auth** surfaces are all designed here.
- **Supersedes** the earlier answer ("one mixed design+build phase, leaner for the deadline").
- **Consequences:** the build phases are sized from each round's `build-prompt.md` and were created
  after the design landed — **P5** (everything except the AI 질문 agent) and **P6** (the agent), with
  deployment staying in **P4**. Every build slice runs under **RESPECT THE DESIGN**.

### D-10 — Web stack: **FastAPI + Next.js**, SSE confined to AI 질문 streaming

- **Date:** 2026-08-20 · **Status:** accepted (operator, confirmed at phase intent capture)
- **Decision:** the HTTP layer is **FastAPI** over the persisted P2 exposure contract; the frontend is
  **Next.js**; **SSE is used only for the AI 질문 answer stream** and nowhere else.
- **Context:** it completes D-6 (which deferred the HTTP layer to P3) and reuses the operator's
  existing stack and the P2 Python package.
- **Consequences:** locked as system structure in every design handoff — never in play as a visual
  decision. The request path makes **no OpenDART call**: it reads the persisted exposure contract.
- **Landed in P6, and the clause held exactly.** `POST /ask` is the service's first and only
  `text/event-stream` endpoint; every other route still returns a complete JSON body. The "no OpenDART
  call in the request path" half is unchanged and still enforced; the model half was re-aimed rather
  than dropped — see **D-21**.

### D-11 — Estimate mark: **「추정」 everywhere**; `▷` retires from the UI

- **Date:** 2026-08-21 · **Status:** accepted (operator, at the R2 gate; executed in R3)
- **Decision:** a bordered **「추정」** tag is the system-wide estimate mark on every product surface.
  **`▷` is retired from the UI** and survives only in documents and pipeline output. The
  `EstimateMarker` component was re-cut to the tag at R3.
- **Consequences:** an estimate never renders untagged and a fact never carries a mark. R1's and R2's
  landed records still show `▷` — they are immutable history, and this decision governs over them.

### D-12 — App surfaces run **cosmos-dark**; R1's "light theme only" is superseded

- **Date:** 2026-08-21 · **Status:** accepted (operator, R2.1 revision)
- **Decision:** a `.cosmos` token scope (29 remapped tokens + `--panel-bracket`, `--panel-glow`,
  `--live-solid`) makes the app surfaces a continuous dark starfield with aerospace-craft panels; the
  light `:root` set stays for light and print contexts. R1's components adapt unchanged.
- **Consequences:** the admin panel (R7) reuses the same token scope with **all ornament removed**
  (opaque flat `#0e1a15` panels) — an ops idiom, not a second theme.

### D-13 — Reader auth is **email + password**, and only 내 포트폴리오 is gated

- **Date:** 2026-08-21 · **Status:** accepted (operator revision at R5; the session's code-based
  proposal was discarded)
- **Decision:** email + password (≥8 chars, reset by emailed link, no signup-status disclosure).
  **Stored PII = email + password hash.** Exactly one gated surface: **내 포트폴리오**, entered from the
  account menu rather than a fourth nav link. Everything else — board, detail, 조회, 놓친 돈, AI 질문 —
  stays anonymous.
- **Companion (R6, operator):** AI 질문 is **completely anonymous with unlimited questions** — no quota
  and therefore **no quota display anywhere** — while conversations **are** stored server-side for
  quality review, with the 계정↔대화 join absent at schema level and honest UI copy. See `security`.

### D-14 — The admin panel is **read-only and desktop-only**, and invents no Korean

- **Date:** 2026-08-21 · **Status:** accepted (operator, R7 §6 resolutions)
- **Decision:** 운영 관제 has **no mutation endpoints at all** — no review/clear/approve/re-run control,
  no status bits (§6.5). Exposure changes only through the pipeline CLI. It is **operator-only** (no
  judge-visible "how the gate works" view, §6.2) and **desktop-only** by explicit decision.
  **Suppression reason codes render as raw English codes** — no Korean was invented (§6.1); adding
  Korean later is new signed matter. The admin door is a **separate credential** (§6.4, see `security`).
- **Rationale that makes this a security property, not a preference:** the product's core promise is
  that a field failing its deterministic gate is never shown. **No click may override a gate verdict.**
- **Delegated (§6.3):** the vocky **observation** API shape is decided by Claude Code at the apply
  phase; until then the cards ship a `?`-columned frame labeled 「API shape 확정 대기」.

### D-15 — 매수예정가 (③) is **added at the apply phase**, not designed around

- **Date:** 2026-08-21 · **Status:** accepted (operator, at the R3 gate)
- **Decision:** ③ detail does not render 매수예정가 today because it is **not in the exposure
  contract**. The apply phase extends extraction/exposure for it as backing work, and a design-fidelity
  slice then adds it to the ③ surface.
- **Why it is recorded here:** it is the worked example of the `design-cowork` rule that a design
  implying data that does not exist means **build the backing**, never quietly drop the feature.
- **Closed 2026-08-22 (P5).** The backing landed and ③ detail renders 매수예정가격 as an ordinary
  field row with a verbatim citation on 12 of the 16 exposable ③ events. The worked example carries a
  second lesson worth as much as the first: **measure which tier the value lives in before assuming
  it needs a model.** The plan assumed a bounded Gemini run; reading the 본문 first showed the value
  is a form cell present in 95/95 stored ③ 본문 *and* independently in the API row, agreeing 17/17. So
  the honest build cost **0 calls, 0 requests and ▷ $0.0000** — and paying a model for it would have
  broken both the phase's anti-rule and the field registry's own tiering rule.

### D-16 — Reader sessions are **rows**, 30 days absolute, with service-wide header CSRF

- **Date:** 2026-08-22 · **Status:** accepted (P5.S7, implementing R5)
- **Decision:** a session is a database row holding a **digest** of the cookie token, not a signed
  stateless cookie; the cookie is `mj_session` (`HttpOnly` · `SameSite=Lax` · `Path=/` · `Secure` by
  env), **30 days absolute and never extended on a read**; CSRF is a **service-wide middleware**
  requiring `X-Mijual-CSRF` on every unsafe method; passwords use stdlib **scrypt `n=2**14,r=8,p=1`**
  with the parameters carried inside the hash.
- **Why:** immediacy beats statelessness when the request path loads the account anyway — a stateless
  cookie would have needed a revocation list, i.e. this table, and saved no query. A **sliding**
  session would have to write during `GET /auth/me`, and a GET may not write. The scrypt parameters
  are the largest that fit **OpenSSL's default `maxmem`**: a parameter that only works with a private
  knob turned up is a login endpoint one deployment away from raising. Header CSRF works because the
  frontend is same-origin, so nothing has to be minted, stored or rotated.
- **Consequence to carry:** rotating `MIJUAL_SESSION_SECRET` logs out every reader *and* operator —
  which is the lever you want in that hour.

### D-17 — Every surface serves **factors, never products**

- **Date:** 2026-08-22 · **Status:** accepted (P5.S4/S8, implementing R4/R5)
- **Decision:** no endpoint accepts a holding count and no payload contains a per-holding number. The
  product has **exactly one multiplication site** (`frontend/lib/holding.ts`), shared by 내 종목 조회
  and 내 포트폴리오.
- **Why:** the server *does* know the holding count, so this was a real choice. Pre-multiplying would
  put a second multiplication site in the product for one number — precisely the "두 divergent
  readouts for the same number" R4 names as the failure mode and R5 restates as "수치 불일치 금지".
  Verified: the 한화솔루션 `lapse` block is byte-identical across both surfaces, and R5-4's own card
  figure (679,575원) appears **nowhere** in any payload.

### D-18 — A deterministic reading is a **free tier**, never a budgeted one

- **Date:** 2026-08-22 · **Status:** accepted (P5.S6)
- **Decision:** the `본문-label` reader (`mijual.extract.labelfields`) writes the same `Extraction`
  row shape as the LLM reader with `call_id`/`model` **NULL**, and runs **first inside the extract
  stage and outside `extract_max_calls`**.
- **Why:** budgeting a pass that spends nothing could only starve it. Storing it in the same row
  shape means the gate layer, the exposure contract and the presentation contract needed no change —
  and a NULL `call_id` is how a report tells a free reading from a paid one. A second label field is
  now a registry entry plus a gate, nothing more.

### D-19 — vocky is **observed read-only**, and read-only is enforced on our side

- **Date:** 2026-08-22 · **Status:** accepted (P5.S18, closing R7 §6.3's delegation)
- **Decision:** this product reads vocky's **Project Feedback API** server-side with a `vk_` key the
  browser never sees, serving an explicit **sixteen-field allowlist** in vocky's own English key
  names; correlation handles (`user_id`, `session_id`, `conversation_id`) and free-form blobs are
  excluded. The decided shape was written back into the R7 record's own §6.3 section — the only write
  into a landed record in all of P5, and purely additive.
- **Why:** vocky offers **no read-scoped credential** — one key does capture *and* full read+manage —
  so read-only cannot be a property of the credential and must be a property of our code: the client
  issues `GET` and has no path that could issue another method, and a test asserts that **only that
  one module may import an HTTP client**. Redirects are refused because `urllib` re-sends
  `Authorization` to the redirect target.
- **Finding recorded with it:** vocky ships **no embeddable widget script**, so the three signed
  `data-vocky-trigger` elements have nothing to bind to yet. Nothing was dropped and nothing was
  invented — wiring a capture path is the operator's call about their own product.

### D-20 — The AI 질문 backend is an **autonomous agent**, not an LLM chain

- **Date:** 2026-08-22 · **Status:** accepted (**operator**, mid-phase addition at P6.DECOMP)
- **Operator's words, verbatim:** *"we need to build a agent not just llm chain."*
- **Decision:** the model runs an autonomous tool-calling loop — **it** decides which of the five
  tools to call, in what order, across as many rounds as it needs, and when it is ready to answer. A
  fixed retrieve → prompt → answer pipeline does not satisfy this, **however good its output looks**.
  Binding on the architecture, not a quality target.
- **How it is kept, and how to check it.** The property lives in one function's control flow
  (`mijual.agent.loop.run_turn`), and the check is legible: **no tool name appears in the control
  flow**. Nothing is fetched before the model speaks or after it, no tool fires because a question
  matched a pattern, no ordering is imposed on the calls it asks for, and the turn ends when the
  model emits a round with **no** function calls. `call_tool` is invoked from exactly one place in
  the codebase, dispatching on the name the model supplied. Even the reader's 범위 is resolved with a
  plain row read into the system instruction rather than through a tool, **specifically so that a
  scoped turn does not make one call mandatory**; the instruction's tool notes are labelled *advice,
  not instructions — you decide*.
- **What the loop keeps for itself**, because it must not be left to a model: the visible tool fact
  rows, the citation gate, the signed refusal families, the 갈 곳 links and footer composed from
  tool results **as data** (so the model never writes a URL — the agent carries no route string at
  all), a structural round/call budget, and the ▷ ledger. **P9 added two tools and a hard reject
  without weakening this**: the loop still names no tool — it asks the tools module what a call *is*
  — and the security reject is the one place the loop ends a turn on its own initiative, which is
  the point of it.
- **Measured, live:** the model took a different tool path in every turn; on a 0건 search it corrected
  its own query and searched again unprompted; a 계산 요청 reached the answer with **zero** tool
  calls. Two bugs surfaced that a chain-shaped implementation would never have hit — the SDK's
  per-call reasoning signature must be echoed back or the *second* round fails, and the live model
  writes its citation markers with no space after a full stop.
- **Consequences:** the agent is a package of its own (`mijual.agent`), it is the phase's keystone
  rather than one feature among several, and a future change that pre-fetches "just to be safe" would
  break this decision rather than optimise it.

### D-21 — The request-path boundary is **re-aimed, not relaxed**

- **Date:** 2026-08-22 · **Status:** accepted (P6.S4, closing the phase's own Finding 1)
- **The problem, stated honestly.** Through P5 the architecture's loudest invariant was *"no OpenDART
  call **and no LLM call** happens in a request path,"* published in three docs and the service's own
  OpenAPI description. **D-20's agent is an LLM call in a request path by design** — SSE streaming
  cannot be anything else. Putting the agent in a new top-level package would have kept the existing
  AST scans literally green while the published sentence quietly became false, and **that was
  explicitly judged not good enough**.
- **Decision:** the sentence becomes three clauses, each carried by its own AST import scan rather
  than by prose: **(1)** no OpenDART call happens in **any** request path; **(2)** the model is
  reached **only** through `mijual.agent` — no module under `mijual.web` may import a model SDK, so
  the credential, the call budget, the citation gate and the ▷ ledger cannot be bypassed by a handler
  that talks to the API itself; **(3)** `mijual.web` speaks HTTP in exactly one file. A fourth scan
  keeps spending modules out of `mijual.agent` too: the agent reads persisted rows, it never collects
  or extracts.
- **Also decided with it:** `mijual.extract.client` is **not** imported by the agent despite the
  convenient wrapper, because it lives inside a package the request path may not reach. The two ideas
  worth keeping (a structural call budget, a recorded thinking level + ▷ ledger) were copied; the two
  clients diverged immediately anyway.
- **Why it is a decision and not a refactor:** an invariant that is enforced by a test everyone
  trusts, but has silently stopped meaning what it says, is worse than no invariant. The old wording
  was corrected everywhere it was published, **including the OpenAPI description**, which is an
  outward surface.

### D-22 — The 운영자 연락처 string is a deploy value, and the agent is **honest without it**

- **Date:** 2026-08-22 · **Status:** accepted (P6.S2) · the value itself is **operator-provided**
- **Decision:** `get_contact()` reads `MIJUAL_OPERATOR_CONTACT`, which has **no default and
  deliberately no required-accessor** — nothing may fail for want of it, and nothing may substitute
  for it. Unset, the tool states that no contact string exists and the answer says so plainly; it
  **never invents an address and never promises one is coming** («준비 중» is as forbidden as a made-up
  address, because both are claims).
- **Why the shape matters:** a `require_` accessor would let the feature break on a missing value; a
  default would let a placeholder ship. This is the one operator-identifying string the product will
  publish, so the only correct source is the operator.
- **Open, and the operator's alone:** the string itself is still unset. **Set it before launch** —
  until then the agent answers 미정, which is true but is not what a reader asking how to reach the
  operator needs. See `operations` for where it goes.

### D-23 — Agent prose prints the product's numerals, and that is **presentation, not computation**

- **Date:** 2026-08-23 · **Status:** accepted (operator disposition, landed in `P6.F1`) ·
  **supersedes** the P6 reading below that the agent quotes contract numerals exactly as given
- **Operator, verbatim:** «make it 3,200원. dk how» — the *what* was decided by the operator and the
  mechanism was delegated.
- **Decision:** the agent's own prose writes a figure the way every other surface in the product
  writes it — `3,200원`, not `3200원`. Two halves enforce it and both are presentation only.
  (1) The tool contract serves the reader's form: beside each figure's exact contract `value` sits a
  `value_display` string carrying the same number in the product's grouping, and one line of the
  system instruction tells the model to write it that way. (2) The citation gate guarantees it: a
  released sentence's raw figures are respelled from a `{raw: grouped}` table built from those same
  nodes — **after** the citation, never-compute and verbatim-quote checks have all passed.
- **What a figure is, is the contract's own predicate, not a key list:** a node carrying both `value`
  and `estimated`. So a 접수번호, a date, a year, a D-day, a character span and an `event_id` are
  structurally *not* figures and can never be grouped, and a bare 14-digit integer is refused even
  where it is a figure's value, because that shape is a filing number here.
- **Why this does not touch never-compute.** Grouping cannot change *which* number a sentence
  states, so it can neither satisfy nor defeat the rule. The membership check still runs on what the
  model actually wrote, before any respelling, and separators were already normalized away on both
  sides — `3,200` and `3200` are one member. An invented figure is still blocked in its raw form.
- **Why this does not touch 인용문 재구성 금지.** The respelling skips every 「…」/"…" span (the gate
  and the grouping share one pattern), a sentence released because it *is* a tool's own string is
  copy and is never respelled at all, and `TurnEnd.quotes` and the citation chips are built from the
  tools' `Citation`s and are untouched. A filing's own quote keeps the filing's spelling, whatever
  it is.
- **Recorded limit:** grouping reaches contract figures only. A genuine quantity that is not a
  `Figure` — `holdings[].shares` — is still spoken ungrouped; nothing is visible today because the
  sample's holdings are all under 1000. Widening the predicate would mean naming keys by hand, which
  is the drift this seam exists to avoid.

### D-24 — The 관제 현황판 board is a **30-row display window**, +30 per 펼치기 — a stated default

- **Date:** 2026-08-23 · **Status:** landed and live; **the number is still the operator's to confirm**
  (phase label D-P7-1)
- **Decision:** the ranked board renders **30 rows**, and the panel's own 펼치기 control discloses the
  next 30 (12 clicks reach all 386, after which the control disappears). It is a **display window,
  never a filter**: the served corpus, the ranked order and the whole-board tab counts are untouched
  (전체 still reads 488) and a tab switch resets the window.
- **Why this and not something else:** R2 specifies the sort, the row anatomy and the two pinned
  strips but **no list length and no pagination control** — P5.S3 recorded "the design paginates
  nothing" as the reason the whole board is one request — so the operator's "not all at once" lands on
  an unsigned gap. **30** is the horizon the same page already names in its hero stat line
  (`30일 이내 마감`) and is short enough to read without the ② strip sliding off; revealing everything
  in one click would put the page back where the operator found it. **Zero Korean was minted**: the
  button is `EXPAND_KO` (펼치기, already signed twice on this panel) in the strips' own class, beside
  a mono `{n}건` in the strips' own count idiom.
- **Consequences:** the served HTML for `/` drops **701.9 KB → 369.2 KB** and the document from
  17,730 px to 3,047 px at 1440 — in production the cheaper default page also avoids 366 `<Link>`
  prefetches that only twelve deliberate clicks now trigger. **Changing the number is a one-constant
  edit** (`WINDOW_STEP` in `components/landing/Board.tsx`), not a fix slice.
- **Source:** `P7.S3`; `frontend`, `experience`, `product`.

### D-25 — The hero's ring clip lives on `.orbits`, not `.hero`

- **Date:** 2026-08-23 · **Status:** accepted (engineering, phase label D-P7-2)
- **Decision:** `overflow: hidden` moved off `.hero` onto `.orbits` (`position: absolute; inset: 0` of
  the hero — **the same rectangle**, measured identical afterwards: hero `[52,732,1440]` ≡ orbits
  `[52,732,1440]`).
- **Why:** R2.1 §3 says never shrink the orbit rings, so the clip must stay; but with it on `.hero`
  the typeahead's candidate panel was cut at the hero's bottom edge (measured at 1440: the panel spans
  y 440→761, the hero ends at 732, and `elementFromPoint` on the last option returned the card below).
  Clipping the rings by the hero's own box while letting a panel hang off the input satisfies both.
- **Consequences:** **no later slice may reintroduce `overflow: hidden` on `.hero`.** Proof nothing
  else moved: `scrollWidth == viewport` at 390 **and** 1440 (the rings are 1251px wide) and the
  document height is unchanged at both widths.
- **Source:** `P7.S4`; `frontend`.

### D-26 — Focus indication is **split**: the ring stays for everything but text-entry controls

- **Date:** 2026-08-23 · **Status:** accepted under an explicit operator override (phase label
  D-P7-3); **how far the override goes is still the operator's to say** (catalogue #2 below)
- **Decision:** every button, link, tab, chip, checkbox, radio and R2 §vocky trigger keeps the signed
  **2px `--focus-ring` @ `outline-offset: 2px`**, unchanged. A text-entry control (`input` of a
  text-entry type, `textarea`, `select`) gets `outline: none` and brightens **its own hairline** on
  `:focus` instead.
- **Why the operator's "no selected focus on all the input boxes" was not read as "delete the rule":**
  the a11y floor "Focus ring: 2px `--focus-ring`" is stated in `frontend` v0002/v0004 and R2 spells it
  for the vocky triggers, so deleting the indicator would drop a signed element. The actual defect was
  the **treatment**: `--focus-ring` aliases `--r1`, the ① 유상증자 rights hue (the "annoying blue box"
  is this product's own colour, not a UA default), and at `outline-offset: 2px` it painted 4px **under**
  the 조회 button, whose left edge is the input's right edge exactly (gap **0**, measured — the button
  did not move and no gap was added). So: **treatment changed, existence kept.**
- **Consequences:** measured state-change contrast 3.30–4.01:1 on the three field families, all clear
  of 3:1; the rule is `:focus` rather than `:focus-visible` (a programmatic focus may not match the
  latter), specificity (0,1,1) on purpose, and the selector is an allow-list of text-entry types so a
  future input type keeps the ring by default. `--field-focus-border` is the per-field hook.
- **Source:** `P7.S5`; `frontend` §Accessibility.

### P7 readings of the record — stated as decisions

The operator's framing was *"respect the design, double check everything"* — **no new design round** —
so where a request collided with the signed record the slice implemented **what the record says**, and
where the operator was overriding the record it did **only** the override and restyled nothing around
it. The six readings, settled once at decomposition so no slice re-argued them:

- **Focus (item 3): the defect is the treatment, not the existence** — D-26 above.
- **Nav (item 1): an operator override scoped to the slot.** R2 signs three slots and R5-6 explicitly
  *withdrew* a fourth, so a two-slot bar is a shape no round drew. Remove the entry and **nothing
  else** — no re-centring, no re-spacing, no new slot; the label constant stays where other surfaces
  use it.
- **Board length (item 4a): the record paginates nothing, so the control is new** — reuse the record's
  own disclosure word (펼치기) rather than mint a Korean label, keep the row anatomy and the
  whole-board counts, and never drop a row from the corpus. D-24 above.
- **Typeahead (item 2): the "never a candidate list" rule survives if the suggestion is a *choice*.**
  The rule exists to stop **the system** silently opening a different company's 놓친 돈; a reader
  picking from a list is the opposite. So every candidate carries its 종목코드 and navigates by the
  exact `corp_code`, and a bare submit keeps the unique-or-decline resolver, 검색 불일치 included.
- **챙겼습니다 (item 9): R5-8 says re-label, not delete.** The signed post-gate addition is
  「금액 동일(「추정」 유지), alert → live, 라벨 놓친 돈 → 챙긴 돈, 캡션 본인 표시」 — so the 놓친 돈
  *framing* leaves and the row and its figure stay. Removing the row would supersede a signed round
  (catalogue #4).
- **Self-narrating copy (item 10): separate the narration from the promise.** 「브라우저 세션에만
  저장 · 서버 전송 없음」 is R4 §3's literal and the anonymous-first boundary leans on its second
  half — `api` records that `GET /stocks` has **no `n` parameter** precisely so it stays true. Strip
  the mechanism, keep the promise verbatim; anything that cannot be cleanly classified goes to the
  operator rather than being deleted.

### P7 open operator calls — the catalogue, routed rather than invented

**This list is the point.** P7 exists partly because a comparable catalogue was left in a review
record and effectively lost. Every item below is live in the product today with the default named;
none is a defect and none is blocking; each needs the operator, not a slice.

| # | the call | what is live today |
|---|---|---|
| **1** | **의견 (vocky) has nothing to bind to** — supply a script URL / capture path, or decide 의견 routes somewhere else (the agent already has a 의견 tool). **No slice may invent a URL**: that is inventing a fact about someone else's system | the three signed `data-vocky-trigger` elements render on every surface and **0** scripts load — measured across seven surfaces in both runtimes, they are **the only genuinely inert controls in the product** |
| **2** | **How far does "no selected focus on all the input boxes" go?** If it means *zero* indication, that drops the record's a11y floor and needs an explicit call | D-26: ring off text fields, their own hairline brightens instead; ring intact everywhere else |
| **3** | **How many firms is "some amount"?** | D-24: 30, +30 per click. One-constant edit |
| **4** | **Should a 챙겼습니다 row disappear from 지나간 마감?** That supersedes R5-8 | the row stays, re-labelled 챙긴 돈 with the same 「추정」 figure, hue alert → live, shift-free |
| **5** | **Live *data* refresh?** Behaviour no round specifies — a deferred job if wanted | countdowns tick and nothing stomps typing, but board data is as fresh as the last load; the freshness chip states 기준시각 and the board is **never dimmed** |
| **6** | **Five P5 catalogue items P7 brushed but does not own** | the footer's locked 내 종목 연결 line and the hero H1's 내 종목 조회 (both *more* visible now the nav slot is gone); the sample's signed 「4건」 subline above five live D-day rows (대동기어 carries two events); `[근거]` + DART link under the mobile 44px floor; the English 404 sentence |
| **7** | **Four reader-visible strings speak developer vocabulary but are promises** — re-saying any of them is a copy decision | `API_TIER_KO` and `SPARSE_CLOSING_KO` (both explain *why a fact carries no verbatim quote*), `GATE_COST_TAIL_KO` (machinery vocabulary, but also the one disclosure of a deliberately excluded number) and `carryOverKo` (세션 is the only word conveying impermanence) all still render. Plus: should the **account** caption drop 「· 계정에 저장」 like the sample one did? |
| **8** | **The 내 포트폴리오 D-day rows have a 144.7px ragged left edge** at 1440 (232.6–409.3px at 768) with 584.6–761.3px of empty middle, because `.rowHead` is `justify-content: space-between`. **This is the one remaining "not organized" symptom**; R2's board pins a fixed grid (`86px 1fr 300px 230px 96px`) for exactly this reason, but R5 states the row's parts and no geometry | unchanged — a geometry decision no round made |
| **9** | **Four smaller record-silent portfolio items** | 지나간 마감 states no 「기준 … (KST)」 line (the counting-down section does); 한화솔루션 and 세기상사 render an **empty 진행 중인 권리 cell**; a 챙긴 돈 row still links 「놓친 돈 상세 →」 (R5-8's checked-state delta is exactly four items and the link is not one); the 「본인 표시」 caption renders checked or not (making it conditional adds a 22.6px click-time shift) |
| **10** | **Five interactive controls have no hover state and the record is silent** — the four board tabs, the 조회 submit, the 로그인 submit, the ask send button and the 샘플 chip, while 회사명 / `↗` / 펼치기 on the same panel do. The record specifies hover in exactly two places (R6 §117's launcher mark, R2 §vocky's trigger — both verified live) and R2 §Tabs draws the tabs' active state, count size and 44px hit and **no hover** | affordance polish over a silent record: every one works on click and wears its focus ring |
| **11** | **The focused input's hairline is brighter than the open candidate panel's side edges** (hero `rgb(163,196,180)` vs `rgba(163,196,180,.4)`) — same hue, different alpha. Matching them is one line in `SearchRow.module.css` | left as is; it reads correctly at 2× (the field is the active thing, the panel hangs off it) |
| **12** | **Two components draw the "mobile" boundary at different widths** — `SearchRow` switches at 768, the board's 펼치기 at 480, so at 481 a candidate row is 44px beside a 32px button. Both clear the 44px floor wherever R5 §Mobile applies | unchanged — a geometry decision no round made |
| **13** | **Two environment leftovers:** the browser's own empty-form validation bubble is **English** (「Please fill out this field.」 on `/auth/login` — UA chrome, locale-driven, not our copy; suppressing it means owning the validation copy, which is new Korean), and **`s19-fidelity@example.com`** (account id 14, one live `auth_session`) is still in the dev database from P5.S19 | both left in place; deleting someone else's leftover row is the operator's call |

### P6 readings of the record — stated as decisions, and the one still open

Settled from R6's own record rather than invented, in the same spirit as P5's list below:

- **Citation forcing is a generation-boundary gate that *drops*, never flags.** A sentence that
  fails verification is not emitted at all — no caveat, no marker, no "unverified" styling — and the
  blocked count is reported to the operator instead of to the reader. If a turn releases nothing, the
  loop states the 검증 미통과 폴백 family itself; a **budget or error abort is deliberately not**
  turned into that family, because that sentence would be a false claim about the data.
- **A saved 의견 never ends in a refusal.** A feedback turn has nothing citable by construction, so
  the fallback would contradict the save the reader just watched succeed. The exception is narrow on
  purpose: a turn that *also* read an event and then said nothing verifiable has genuinely failed to
  verify something and keeps the 폴백.
- **The stored conversation row replays what the reader saw, not what the agent researched.** R7's
  column is 「인용 칩 원문」, so the row carries the chips the reader saw rather than the union of every
  tool result — and it records nothing about the mechanism, because the signed columns carry no status
  bit and none was added.
- **An unknown 거절 가족 is rejected at the write.** An invented family would be a row the signed
  filter can never find. The five names are *not* in the schema, though, because copy can be re-signed
  and conversation rows cannot be re-collected — a re-signed family must not cost a destructive
  migration.
- **The mobile menu keeps AI 질문 in the third slot.** The record contradicts itself (§Surfaces
  states the position by ordinal; §Mobile mentions the menu's first row inside a list of
  touch-target constraints, and that constraint is met — rows 48 px, button 44 px). Reordering signed
  chrome on the weaker reading would have made the sheet disagree with the nav.
- ~~**The agent quotes contract numerals exactly as given**~~ — **superseded by D-23** (operator,
  2026-08-23). The reading was that formatting inside prose would be the agent transforming a
  number; the disposition draws the line differently and correctly — *which* number a sentence
  states is the agent's to never touch, *how it is spelled* is presentation. A figure's exact value
  is still what travels, and a filing's quote is still byte-exact.
- **Open — the answer footer's third context link 「필드로 이동」 is signed but not built, and closing
  it is a design call:** the wire's link kinds are a closed set, the detail page has no per-field
  anchor, and the record does not say which field an answer citing several should point at. It was
  **not invented** and **not quietly dropped**. It is entangled with the footer's link density (up to
  seven links, 「이벤트 상세」 repeated, because the links come from what the turn *read* while the
  footer names what the answer *cited*). **Draw it, or strike it from the footer's list** — and
  decide the row's density in the same breath.

### P5 stated defaults — landed, and still the operator's to confirm

Each ships a working value so nothing was blocked, and each moves by environment variable with **no
code change**, so confirming one is a deployment edit rather than a fix slice.

| default | value | derivation |
|---|---|---|
| landing countdown cut-off | **end of the 청약 day** (00:00 KST of the next day), `MIJUAL_COUNTDOWN_CUTOFF_TIME` | R2's own stated assumption; the real 접수 마감 시각 replaces it |
| freshness stale threshold | **18 hours**, `MIJUAL_STALE_AFTER_HOURS` | the 07:30/19:30 KST beat means the widest *healthy* gap is 12 h and a **missed** beat reaches ~24 h; 18 h is the smallest threshold that cannot fire on a healthy schedule and still fires on the first miss |
| reader session lifetime | **30 days absolute** (D-16) | renewal happens at the next login, which is already a write |
| operator session lifetime | **12 hours absolute** | a working day — an operator console should not still be open the next morning; deliberately not the reader's 30 |

### P5 readings of the record, stated as decisions

Small, load-bearing, and each one settled from the record rather than invented:

- **The estimate mark renders `추정`, not `「추정」`** — the 「」 are the documents' own quoting
  notation and the mark is specified as a *bordered* tag, so the border is the enclosure. `[근거]` is
  the opposite case: its brackets are literal and are rendered.
- **A past `D+n` renders faint, never in the expiring/lost hue** — which is also what keeps an open ②
  from reading as 종료.
- **The frontend reaches the API through a same-origin proxy rather than CORS.** A cross-origin setup
  would have weakened a landed security decision to save a proxy line.
- **`▷` is served verbatim inside the ops panel and never becomes 「추정」** — the boundary is the
  source. Everywhere else 「추정」 is the only estimate mark.
- **The run log is written start-then-close**, which is what makes a crashed run visible *and* gives
  the lock chip an honest 시작 시각: the Redis lock holds an owner token and no start time, so
  deriving one from its TTL would be an invented number.
- **The OpenDART quota bar's denominator is served with its provenance** (`operator (decisions O-1)`)
  because 20,000/day is an operator statement, not something this service can measure.

### D-27 — The AI 질문 agent is **one smart assistant**: strip-don't-drop, an auditable calculator, a behavioural guard (R16)

- **Date:** 2026-08-25 · **Status:** accepted (**operator**, R16 design round `16-smart-assistant`,
  signed with the literal word "done"; in-session answers Q-A…Q-E recorded in the round's
  `output/result.md` §1)
- **Operator's framing, verbatim from the phase intent:** *"Currently just saying 「안녕」 got 「이
  데이터는 검증을 통과하지 못했습니다…」 and it shouldn't. This agent should be more like smart mijual
  assistant not rigid bot."*
- **The decision, in six clauses:**
  1. **Strip, don't drop.** The generation boundary stays; its *judgement* goes. Markers are removed
     (resolvable ones become chips), an uncited sentence ships, a 공시 figure no tool returned is
     **marked 「미확인」** rather than deleted, and a quote no tool returned loses its **quotation
     marks** while the words survive. `REFUSAL_FALLBACK` — literally the sentence the operator saw —
     is deleted. **Q-B decided the shape:** claim-level marking, **not** a turn-replacing gate.
  2. **The agent may derive a number, through an auditable calculator and nowhere else.** R6's hard
     「에이전트 계산 금지」 is superseded by a `calculate` tool whose block shows its **inputs (each with
     its own 근거 칩), its 식, and its result** before any number exists. 「검증된 계산」 (the product's
     own verified operation) and 「식 계산」 (arithmetic) are **never rendered identically** — rendering
     them the same launders one into the other. Browser-side calculation stays banned.
  3. **Refusal families: five → four live, six stored.** 「보안」 is added (Q-C), 「계산 요청」 and
     「검증 미통과 폴백」 are retired **as producers** and kept **read-only** in the stored whitelist so
     past rows stay findable. 범위 밖 questions are **not** a refusal family at all — they get an
     ordinary one-line answer with a 갈 곳 (Q-A: the assistant stays 공시 사실 해설).
  4. **The guard is behavioural, and the doc says so.** `security_check` + a deterministic
     after-model hard reject ends an adversarial turn on one signed sentence, with **no** mention of
     the check to the reader. It is **not** prompt-injection protection (see `security`); the
     mitigation that matches the real threat is **input segregation**. Q-D signed the logging:
     category + a 200-character excerpt + `session_hash`, **log-only, no DB row**.
  5. **Generous ceilings, not unlimited.** `20 / 30 / 22`, with `max_model_calls ≥ max_rounds` so an
     abort never names the wrong limit. Ceilings stay structural and are **never rendered as copy**
     (R6-5 intact). Q-E accepted the spend as-is: **no abuse backstop was added.**
  6. **The thread shows structured content, not only prose** — a 계산 블록, a 데이터 블록, a transient
     진행 표시 line, a folding 도구 흐름 and a three-marker family (추정 · 계산 · 미확인, closed and
     exclusive) — through **one** renderer for both views. The `/ask` page loses its 340 rail for a
     single centred column with a start screen; the 범위 칩, the 익명 줄 and R14's 「다시 질문」 retire.
- **What was deliberately *not* superseded**, and is therefore still binding: the spinner/typing-dot
  ban, 인용문 재구성 금지, the history-UI ban, the quota-copy ban, no alert colour on a refusal,
  같은 근거 = 같은 번호, 도구 행 verbatim, one store for both views, and 767 as the single breakpoint.
- **Consequences worth knowing.** The 데이터 블록 can render **at most one row** on today's corpus
  (372 of 386 board events produce no block at all) because every gate-passing field's value is a
  composite dict the server may not spell without inventing a row format — an open operator question,
  not a defect. And the stored conversation row keeps prose only, so a 「미확인」 hedge the reader saw
  is **not** distinguishable in the 대화 로그 — also open.
- **Source:** `P9` (`P9.S2` design round, `P9.S3`–`P9.S11` build), R16 record at
  `docs/reference/design/rounds/16-smart-assistant/`, SIGNOFF §R16.

## Resolved Open Questions (P1 → P2)

| id | question | resolution |
|---|---|---|
| **O-1** | daily OpenDART quota | **20,000 requests/key** (operator; ▷ authoritative-by-operator, not scraped). Ceilings stay anyway. |
| **O-2** | Gemini credential + model id + thinking config | **CLOSED** — `GEMINI_API_KEY` in `.env`, `gemini-3.7-flash` confirmed on the credential, thinking level was a project preset (now per task, D-4). |
| **O-4** | does KONEX change any coverage conclusion? | **No.** 2026-01-01~08-19, `corp_cls=N`: 30 events, **0 exposable rights** (26-request probe). KOSPI+KOSDAQ stays the frame; `corp_cls=E` was judged not worth the requests. |
| **O-5** | does `주주우선공모증자` issue a 증서? | **No.** The corpus's single case (상지건설 `00232007`, 정정 `20260807000339`) uses a form with **no `18. 신주인수권양도여부`** row and `신주인수권` occurs **0 times** in its 33,886-char 본문. The value left `WARRANT_BEARING_IC_MTHN`; a new suppression reason `no_warrant_bodymun` joined the list (9 events). ▷ The class generalisation rests on the form template, not on a sample of one — a counter-example would surface as a `warrant_conflict`. |
| **O-8** | does `warrant_conflict` block exposure? | **Yes** — it is one of the four blocking flags (`warrant_conflict`, `detail_conflict`, `event_key_collision`, `hint_split_evidence`). Cost measured: 3 events blocked on `detail_conflict`, all fixable only by a collector-side key split. |
| **O-9** | how is a 철회 event handled? | **Not exposable and not deleted:** `exposure_state='withdrawn'` plus the 정정사항 row with its span, rendered as **"이 유상증자는 철회되었습니다"**. The detector keys on **row shape**, not the word 철회 (71 % keyword false positives). |

Still open: ▷ the meaning of `estkRs.exstk/exprc/expd` (unneeded); the 증권사 MTS 권리 메뉴 coverage
matrix carried from P1 (differentiation evidence for the 기획서, not pipeline code — it needs a home
in P3/P4 or a deferred job).

## Reference — mijual domain fact sheet (verified 2026-08-19)

| Domain | Status | Price |
|---|---|---|
| `mijual.ai` | **AVAILABLE** (`whois.nic.ai`) | ~**$82.70**/yr with a **2-year minimum** → ~$165 upfront. ▷ Checkout total unverified — nothing was purchased |
| `mijual.kr` | **AVAILABLE** (`whois.kr`) | **22,000원/yr + VAT** (도레지); ▷ comparable elsewhere |
| `mijual.co.kr` | **AVAILABLE** | same tier as `.kr` |
| `mijual.io` | **AVAILABLE** (`whois.nic.io`) | — |
| `mijual.com` | **REGISTERED — struck from the options** | actively forwards to a live blog; earliest possible drop **2026-10-02**, weeks after the deadline |

No account was created and nothing was purchased in reaching these facts.

## Superseded Decisions

- The rights-type 3종 was previously tentative; **D-1** supersedes that with a measured, confirmed
  keep-all plus named exclusions.
- `mijual.com` as a fallback domain, and any "watch it lapse" plan, is **withdrawn**.
- **D-4's "high thinking everywhere" is superseded by the 2026-08-20 per-task amendment.**
- **The evalset's planned human labelling pass is superseded by D-7** (cross-model judging).
- **The "one mixed design+build phase" answer is superseded by D-9** (design-only P3 + apply phases).
- **`▷` as the product's estimate mark is superseded by D-11** (「추정」 tag; `▷` stays internal).
- **R1's "light theme only" is superseded by D-12** (cosmos-dark app surfaces).
- **The R5 session's code-based login proposal is superseded by D-13** (email + password).
- **The R6 session's question-quota copy is superseded by D-13's companion** (unlimited, no quota
  display) — the stale quota captions on three R6 cards are known and governed by the contracts.
- **The MIJUAL + 한글 '미주알' 병기 lockup is superseded** by the operator's R1 revision: English
  wordmark alone.
- **The whole latin identity is superseded by 주주의관제탑 (P10, operator, 2026-08-30).** The product's
  name is now uniformly the **unspaced 주주의관제탑**; the `MIJUAL` wordmark, the `MIJUAL OPS` bar mark
  and the name 미주알 are retired with **no romanized replacement**, and the prompts' third spelling
  미주얼 goes with them. Two things this does **not** supersede. First, **code identifiers**:
  `src/mijual/`, every `MIJUAL_*` variable, `X-Mijual-CSRF`, the repository directory, both `name`
  fields, the local DB credential and the Claude Design project's own name ("Mijual Design System")
  are deliberately untouched — the operator scoped the rename to what a user can see, days before the
  2026-09-07 deadline, because renaming identifiers would put the production deploy at risk. Second,
  **history**: the 2026-08-19 `mijual` domain fact sheet above, the verbatim operator quote in D-27,
  and this list's own earlier entries are preserved exactly as written, as dated records of a name
  the product no longer uses. A doc that renames its own history stops being a record.
- **P6's reading that the agent quotes contract numerals exactly as given is superseded by D-23**
  (operator disposition, 2026-08-23): agent prose prints `3,200원`, and grouping is presentation.
- **D-4's `LOW` for `agent_turn` is superseded by the P9 amendment above** (`MID` / SDK `MEDIUM`),
  because the argument that made `LOW` safe — "a cheaper level can only produce a *blocked* claim" —
  stopped being true the moment nothing is blocked.
- **P6's generation-boundary *judgement* is superseded by R16 strip-don't-drop (D-27).** The boundary
  itself is not superseded: the gate still stands between the model and the reader, it just strips
  instead of dropping. `REFUSAL_FALLBACK` and its sentence are deleted.
- **R6's 「에이전트는 계산하지 않습니다」 is superseded by D-27's auditable calculator**; the browser-side
  calculation ban is **not** superseded.
- **R6-7's five refusal families are superseded by D-27's six-value vocabulary** — four live
  (철회 · 확정 전 · 공시에 없음 · 보안), two read-only for past rows.
- **`AGENT_INTRO_KO`'s R6 three-sentence promise is superseded by R16 D1** (「주주의 권리를 지키기 위해
  공시를 근거로 질문에 답합니다.」), which contradicted all three of its clauses.
- **R6/R14's `/ask` 340 rail, the 범위 칩 and its ×, the 익명 줄 and R14's 「다시 질문」 are retired by
  R16** — the anonymity *property* is unchanged, it is simply no longer declared as copy.
