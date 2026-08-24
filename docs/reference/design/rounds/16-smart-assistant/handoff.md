# R16 handoff — Smart Mijual Assistant: unified behavior & rich chat surface

- Round **R16** · slice `P9.S2` (co-work) · build slices cut afterwards by `P9.DECOMP2`
- Claude Design project: **"Mijual Design System"** (reads this repository via GitHub)
- Review groups for this round's cards: **`⏳ P9.S2 · Ask`** and **`⏳ P9.S2 · Components`**
- **Token freeze:** `foundations/tokens.css` is signed (R8). This round is expected to change no
  token; if the session decides otherwise, the delta is signed in `result.md` like any decision.
- Common rules: **R10 §0 adopted as-is** (keep-all, nowrap mono, tabular-nums, border-box, single
  767px breakpoint, hit floors 32px desktop / 44px ≤767). R14's ask-surface decisions stand and are
  this round's baseline, not its subject.

**Provenance (read this first):** this round is grounded in two landed research reports, both in
this repository — `works/phases/active/P9/phase.md`:

- `### P9.S1 — changple5 transfer report` — how a sibling product built its unified chat agent,
  per-mechanic, with **design inputs 1–9** and proposals **P1–P8**.
- `### P9.S1B — best-practice survey beyond changple5` — what the wider field does (Anthropic,
  Gemini, OpenAI, OWASP, AG-UI, Vercel AI SDK, NN/g; primary sources, dated), with **design inputs
  10–18**, proposals **P9–P16**, and a per-item verdict.

Everything in those reports is **evidence and questions — data, not decisions**. This round makes
the decisions.

## 1. Product context

미주알 (Mijual): free, anonymous, Korean-only reader over verified Korean corporate filings
(유상증자 rights offerings). Its one promise: **numbers come from filings, auditable end to end** —
every agent answer shows its tool rows (도구 행), numbered citation chips onto verbatim filing text,
and a per-turn ▷ cost ledger.

**What P9 changes.** Today's AI 질문 agent is a rigid grounded bot: a citation gate **discards**
every sentence it cannot verify, so 「안녕」 gets back 「이 데이터는 검증을 통과하지 못했습니다…」.
P9 rebuilds it into **one unified smart assistant**: it chats naturally (greetings, general
questions, meta questions about 미주알), grounds filing facts with tools and citations when it uses
them, gains a **calculator tool** (derived numbers as auditable rows — superseding the signed
never-compute rule), generous turn budgets, a prompt-injection behavior guard, and — this round's
headline — a chat surface that renders **structured content**: data rows, calculation results,
status signals, beside today's mono tool rows and chips.

Surfaces and code (the project reads this repo): `frontend/components/ask/` (`AskWidget` 440×620,
`AskPage` + 340px rail, `QuestionStrip`, `Composer`, `Answer`, `InlineCitation`), store
`frontend/lib/ask.ts`, event vocabulary `src/mijual/agent/events.py` (7 typed kinds today:
`ToolRowEvent`, `CitationEvent`, `TextEvent`, `RefusalEvent`, `LinksEvent`, `FooterEvent`,
`TurnEnd`), copy `src/mijual/agent/copy.py`, prompt `src/mijual/agent/instructions.py`. The signed
records this round supersedes live in `docs/reference/design/rounds/06-explain/output/` (R6 — the
agent's surface contract) and `rounds/14-ask/output/` (R14 — the surface's current polish baseline).

## 2. Locked vs. in play

**In play this round (the point of the round):**

- **Copy is in play — the dated exception (2026-08-25), this round only.** The unified assistant
  contradicts signed R6 copy on its face; this round exists to produce the superseding signed
  strings. Specifically in play:
  - `AGENT_INTRO_KO` — 「검증을 통과한 공시에 대해서만 답합니다 … 계산은 하지 않습니다」 is
    contradicted by P9 on all three clauses. What does the unified assistant promise?
  - The **five refusal families** (`철회 · 확정 전 · 공시에 없음 · 계산 요청 · 검증 미통과 폴백`) —
    which survive, which retire, whether a **sixth security family** is added. (This decides a DB
    vocabulary and an ops filter — see §5.)
  - The **검증 line in the `/ask` 340 rail** and the widget's framing copy.
  - The **never-compute rule** (R6: 에이전트/브라우저 계산 금지) — superseded by the auditable
    calculator; the supersession must be explicit and signed.
  - The greeting/short-answer **register** (design input 5/18), the **security refusal string**
    (input 1/9), the **exhausted-turn line** (input 17).
- **New display elements** — everything in §4's card list: their look, states, placement, density.
- **The 스피너·타이핑 점 금지 rule** may be re-examined *only if* the session designs a status
  signal that needs it (input 16/8) — any change is an explicit signed supersession, not drift.

**Locked:**

- System structure and data contracts: the stdlib agent loop, SSE transport, typed-event
  architecture, citation numbering rule (같은 근거 = 같은 번호, per answer), the ▷ ledger's
  existence, anonymity (no accounts, no history UI, no quota copy — R6-5 stands).
- `foundations/tokens.css` (R8 freeze), fonts, the a11y/reduced-motion floor, R10 §0.
- R14's composer/preset/breakpoint decisions — baseline, not re-opened.
- All reader-visible copy is Korean; every new Korean string this round mints is a dated, signed
  decision in `result.md`.

## 3. Scope checklist — what the session must cover

The 18 design inputs, grouped. Each is a question the reports pose; the session answers it.

**A. The assistant's voice and promises (inputs 1–5, 9, 18):**
1. New `AGENT_INTRO_KO` and rail/widget framing copy (inputs 3–4).
2. Refusal families: survivors, retirees, the possible sixth (security) family; what each surviving
   refusal reads like under the new register (input 2).
3. The security refusal string, and whether the reader ever learns a check happened (inputs 1, 9).
4. The greeting/non-filing register: what a small-talk turn reads like, and the register's shape —
   the field's convention is a **ceiling that relaxes** (short casual answers fine), where today's
   prompt sets a two-to-five-cited-sentence **floor** (inputs 5, 18).
5. The exhausted-turn ending: what an ~aborted turn says — "what I found, what's missing" — without
   ever stating the ceiling as copy (input 17, proposal P13).

**B. The structured surface (inputs 6–8, 10–16 — the headline):**
6. The **data row** and the **calculation block**: what they look like beside today's mono 도구 행
   and chips. For a calculation: are the *inputs* shown, each with its own citation chip, result
   marked as derived (proposal P7 — the strongest candidate for the phase's signature element)?
7. Product-calc vs expression-calc: does the surface distinguish 「제품이 계산한 값」 from 「식을
   계산한 값」, and how (input 10)?
8. In-place updates: does a block show intermediate state (계산 중 → 결과) or appear only complete
   (input 11)? Which elements are **persistent** (belong in the 대화 로그) vs **transient** (status
   lines) (input 12)?
9. Where wide elements live in a 440px widget and a 340px-railed page: inline, collapsed, expander
   (input 13).
10. The tool trace under ~20 rounds: complete list (today) or collapsed research trace with
    expand-on-demand (input 15, proposal P1 — 「무엇을 읽었는지가 근거의 일부」).
11. The waiting state: what fills the gap before the first token — fixed phrase, per-phase word, or
    nothing; 스피너 금지 stands unless explicitly superseded (input 16, proposal P2).
12. Citation chips: stays a bare number, or gains a preview on hover/tap (input 14).

**C. Posture decisions the operator takes in-session (see §5).**

The build inventory (`phase.md` §Findings & Notes) lists the eight required end states; the session
is free to add elements to this list and to cut from it — what it signs is what gets built.

## 4. Required cards — group `⏳ P9.S2 · Ask` / `⏳ P9.S2 · Components`

One card per reviewable unit, `@dsCard` marker on line 1 (`<!-- @dsCard group="⏳ P9.S2 · Ask" -->`
or `… · Components`, optional `viewport`). Required paths (filenames say what each is; the pane
shows what it looks like):

Components (`⏳ P9.S2 · Components`):
1. `components/CalcBlock.html` — calculation result: inputs, chips, derived marker; states
   (in-progress if §3-8 says so, complete, error-as-guidance).
2. `components/DataRow.html` — the data row / table element in thread context, wide-content
   behavior at 440px and 390px.
3. `components/StatusLine.html` — the transient waiting/working signal, all phases it can show.
4. `components/ToolTrace.html` — the research trace: rows as decided in §3-10 (collapsed/expanded).
5. `components/CitationChip.html` — chip + (if adopted) preview card; the API-tier quote block if
   its wording changes.

Surface (`⏳ P9.S2 · Ask`):
6. `ask/WidgetConversation.html` — one real conversation in the 440×620 widget: greeting turn,
   grounded turn with tool trace + data row + calc block + chips + footer, showing the new intro.
7. `ask/WidgetRefusals.html` — every surviving refusal family incl. the security refusal, as prose
   (R6: no alert color — unless superseded here).
8. `ask/PageDesktop.html` (1440) — the new rail copy in place, a long thread with structured
   blocks.
9. `ask/PageMobile.html` (390) — the same thread stacked; wide elements per §3-9.
10. `ask/ExhaustedTurn.html` — the budget-exhausted ending as decided in §3-5.

Ground every card in **real content** — real filing numbers, real rcept_no, the real preset
questions (`frontend/components/ask/presets.ts`), the S1 report's real example rows. **Never
lorem.** If a needed real datum is missing, ask for it in-session; do not invent it.

**Definition of done: the cards appear in the Design System pane** under the two round groups —
not "the files exist".

## 5. Questions for the operator (answer in the design session)

These gate the copy this round signs. They are also on `phase.md`'s `## Operator Questions` list;
answers recorded in `result.md` count as answered.

- **Q-A — Scope: how far outside 공시 may the assistant answer?** Greetings and 미주알-meta are
  clear. General investing questions (「주식 어떻게 시작해?」) mean answering from model memory,
  uncited, on a finance surface — and the S1B **규제 플래그** (금융위원회 2024-08-14: individualized
  advice over 양방향 channels is regulated 투자자문업) sharpens this. Keep the assistant explicitly
  to 공시 사실 해설 (proposal P15's lean), open the scope, or take advice first? **The intro copy
  and register cannot be signed without this answer.**
- **Q-B — Ungrounded-answer backstop.** With the sentence-dropping gate retired, what stops a
  confidently wrong uncited claim about a filing? Options on the table: changple5's length gate
  (≥400 chars, zero-tool → replace turn), nothing, or the S1B middle path (P16: flag/hedge a
  filing-specific **claim** — a number no tool returned — claim-level, not turn-level). Product-risk
  posture; the design writes the words once the posture is chosen.
- **Q-C — The sixth refusal family.** A security-rejected turn: reuse an existing family's shape or
  add a persisted sixth family? (DB vocabulary `conversationstore.REFUSAL_FAMILIES` + ops filter
  follow whatever is signed.)
- **Q-D — What may be logged when the guard fires?** Nothing, category only, or truncated excerpt —
  the reader is deliberately anonymous; changple5 logs an excerpt. Privacy posture.
- **Q-E — Worst-case spend.** MID thinking × ~20 rounds on a free anonymous surface: acceptable
  as-is, or should P9 add a quiet abuse backstop (never shown as copy)? (Decides nothing visual;
  answering it here saves a review round-trip.)

## 6. Required outputs — a round is incomplete without all three

1. **The card set** (§4) — visible in the pane under the round groups.
2. **`output/result.md`** — every decision made, every signed Korean string (dated), every
   supersession named against its R6/R14 ancestor ("supersedes R6-7의 다섯 가족 중 …"), the answers
   to Q-A…Q-E, measurements for anything geometric, and every departure from this handoff logged.
3. **`output/build-prompt.md`** — the binding implementation contract for `P9.DECOMP2`'s build
   slices: complete enough to build **without inventing anything** — element specs with states,
   the event-vocabulary implications the design assumes (which blocks persist, which replace
   in-place), the final copy strings verbatim, and a numbered regression checklist for the states
   §4 draws. The implement executors get no DesignSync — what this file carries is all they see.

If the session produces Claude Design's own handoff bundle, that bundle **is** the record and the
contract — landed as-is under `output/`.

## 7. Hard rules (restated)

R6's hard rules stand **except where this round explicitly signs a supersession** (the candidates:
계산 금지 — superseded by the auditable calculator; 검증 미통과 폴백 — superseded by
strip-don't-drop; 스피너·타이핑 점 금지 — only if §3-11 decides so). Standing regardless: 인용문
재구성 금지 · 익명 경로 차단 금지 · 이력 UI 금지 · quota 표기 금지 · 거절에 alert 색 금지 · the
launcher's Saturn stays the one motion exception. Tokens frozen (R8). All reader-visible copy
Korean; every new string is a dated, signed decision in `result.md`. The five-family DB vocabulary
changes only by signed decision (Q-C).

REFERENCE — data, not proposals: `works/phases/active/P9/phase.md` (S1 + S1B reports, build
inventory), `rounds/06-explain/output/build-prompt.md` (R6, the contract being superseded),
`rounds/14-ask/output/` (R14, the current surface baseline).
