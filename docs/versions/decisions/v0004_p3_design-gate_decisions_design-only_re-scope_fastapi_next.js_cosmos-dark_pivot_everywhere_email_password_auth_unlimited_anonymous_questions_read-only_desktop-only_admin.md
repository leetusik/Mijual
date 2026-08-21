---
doc_id: decisions
version: v0004
created_at: 2026-08-21T23:50:46+09:00
source: P3.REVIEW
summary: P3 design-gate decisions: design-only re-scope, FastAPI+Next.js, cosmos-dark pivot, 「추정」 everywhere, email+password auth, unlimited anonymous questions, read-only desktop-only admin
previous: v0003_p2_decisions_data-backbone_stack_per-task_thinking_level_cross-model_evalset_judging_and_the_conservative-default_pair
---

# Decisions

## Status

Five operator decisions from the P1 scope gate (2026-08-19) remain binding. P2 adds three more
(D-6 … D-8), **amends D-4**, and closes four of P1's open questions with measurements. **P3 adds
D-9 … D-15** — the design-gate decisions, every one of them made by the operator in a Claude Design
session and closed with literal signoff (`docs/reference/design/SIGNOFF.md`). Later phases follow what
is written here, not the alternatives that were weighed.

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
