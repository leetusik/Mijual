# Intent — P6

- Captured at: 2026-08-22
- Origin: operator

## Original Input (verbatim)

> and note that split agent and other building. other first, agent part later

> split phase

## Confirmed Intent (refined + clarified)

Split the apply work into **two phases**: P5 builds everything **except** the AI
질문 agent; this phase — P6, ordered 3.7, after P5 and before P4 (Ship & Submit)
— builds the **whole AI 질문 feature** per R6's signed design record
(`docs/reference/design/rounds/06-explain/output/build-prompt.md`):

- the citation-forced agent backend (§3.6 layer 3: SSE streaming; visible tools
  `search_events` / `get_event` / `get_portfolio` / `save_feedback` /
  `get_contact`; the reason-first refusal families; citation forcing — no claim
  without a verified span; the agent never computes a number),
- server-side anonymous conversation storage (the R6-6 promise: anonymous hash
  only, no account/email/IP/UA columns — schema-level),
- and the AI 질문 surfaces: the 440×620 widget, the dedicated 「AI 질문」 page
  (nav third slot), mobile full-width page, preset question strips on detail
  pages, and the Saturn launcher.

Faithful under **RESPECT THE DESIGN**; each phase gets its own review gate.

## Clarifications Resolved

- Q: Split within P5 as ordered slice groups, or two separate phases? —
  A: "Two phases" (AskUserQuestion), reconfirmed verbatim: "split phase".
- Boundary note (for both DECOMPs, not decided here): the R7 admin panel's
  대화 로그 tab and the 사용자 tab's anonymous-session table depend on this
  phase's conversation storage — P5's DECOMP decides whether those admin views
  land in P5 as empty frames or move here.

## Operator Additions (mid-phase)

- 2026-08-22, at P6.DECOMP, verbatim: "we need to build a agent not just llm chain."
  Read: the AI 질문 backend must be a **genuine agent** — the model runs an
  autonomous tool-calling loop (it decides which of the five tools to call, in
  what order, across multiple rounds if needed, and when it is ready to answer),
  not a scripted retrieve→prompt→answer chain. Binding on the P6 architecture
  and decomposition.

## Notes

- Ordering: P3 (design, done pending review) → P5 (apply, everything else) →
  **P6 (this: AI 질문 agent)** → P4 (Ship & Submit: deploy, deck, submission).
- Open items landing here from the design rounds: the 운영자 연락처 string for
  `get_contact` is operator-provided (never invented); refusal copy families are
  signed in R6 (five categories, no per-reason-code wording).
