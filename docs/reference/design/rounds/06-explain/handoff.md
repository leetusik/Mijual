# Design Handoff — Round 6: grounded 해설 — 근거 강제 설명 층

- Round: **R6 of 7** · slice `P3.S7` · written 2026-08-21
- Status: OUT — awaiting the design session (Claude Design + operator)
- Repo: `leetusik/Mijual` via Connect GitHub (main, pushed at handoff commit)
- Builds on: **R1–R5 signed designs** (locked — cosmos theme, craft panels, chrome incl.
  the logged-in account menu, trust primitives, Citation, 「추정」, detail/조회/포트폴리오
  contracts). Changing any of them is a new superseding round.

## 1. Product context

미주알's AI architecture (§3.6, locked product truth): **AI reads and speaks; only
determinism calculates.** Layer 1 extracts fields from filings, layer 2's deterministic
gates verify them, and layer 3 — this round — **speaks about verified data under citation
forcing**. The 해설 layer is the interaction surface over layer 3: a reader asks "실권주
처리 방식이 뭔가요?" or "왜 이 날짜가 마감인가요?" and gets an explanation grounded in the
verified fields of a real filing, with inline citations back to the 원문.

This is the challenge's "what does the AI actually do?" answer made visible — so the
design must *show* the grounding, not just perform helpfulness. Two hard product stances,
confirmed in the inventory:

- **Not a chat UI as the default surface.** The R2-signed nav carries a provisional
  "해설" link; what it opens — and whether the primary entry is contextual (from an event
  detail) rather than destinational — is this session's decision.
- **Refusal is a product feature.** When the underlying data is not gate-passing (field
  suppressed, event withdrawn, no verified span to cite), the panel declines with the
  reason — it never answers from thin air. This state deserves design attention equal to
  the happy path.

## 2. Scope checklist — what this round must cover

- [ ] **Entry point(s)** — where 해설 lives: what the nav "해설" link opens, and the
      contextual entry from an event detail (or wherever the session places it). The
      anonymous path stays ungated (R5's rule; if any part of 해설 needs an account or a
      quota, that's a question — see §6).
- [ ] **Question affordance** — free text input, preset/suggested questions grounded in
      the current event's actual fields, or both. Korean-only.
- [ ] **The answer surface** — streamed Korean prose over verified fields with **inline
      citations**: how a Citation renders *inside* flowing text (the R1 primitive is a
      block affordance; its inline/streaming form is in play), and how facts vs 「추정」
      values appear inside prose (the R2-signed rule applies in sentences too).
- [ ] **SSE states** — streaming (including what the reader sees mid-stream), complete,
      interrupted/error, retry. Fade-only motion; no spinners (R5 set the pattern:
      text-swap in-flight states).
- [ ] **Refusal state** — data not gate-passing: what the reader sees, with the reason
      stated factually (철회됨, 확정 전, 검증 미통과 등 — real states from the corpus)
      and where they can go instead (DART 원문, detail page).
- [ ] **Scope of a question** — per-event (asked from a detail page about that filing) vs
      broader (portfolio-level "내 마감 뭐가 급한가요?") — what exists in this round, what
      is explicitly out.
- [ ] Desktop + mobile compositions.

Cross-cutting: Korean-only; copy from `copy-inventory.md`, new strings logged as proposed
chrome copy; 「추정」 on every estimate; mobile-first; a11y floor; urgency color-never-size.

## 3. Locked vs. in play

**Locked:** R1–R5 signed systems; §3.6 architecture (the panel never computes a number —
every figure it utters comes from the verified contract, every claim carries a citation);
SSE for streaming (stack decision); refusal on non-gate-passing data; Korean-only; no
invented Q&A history (Finding 8: no user data exists).

**In play:** everything visual and compositional — entry placement and what the nav link
opens, panel vs page vs drawer shape, question affordance, inline-citation rendering,
streaming presentation, refusal composition, preset-question content, mobile pattern, and
whether/where answers persist (session-only like R4's holdings, or not at all).

## 4. Where to look — real content, never lorem

- **Real filings to ground example answers**: the pinned samples —
  `samples/r1-live-healthy.json` (계양전기: 실권주 일반공모, 초과청약 0.2주, 발행가 산정방법
  MAX/MIN formula — rich fields to explain), `samples/r1-money-chain.json` (한화솔루션:
  the full money chain), `samples/r2-option-schedule.json` (대동기어: 리픽싱/콜풋
  `option_schedule` — the classic "이게 무슨 뜻인가요?" material),
  `samples/r1-withdrawn.json` (썸에이지 철회 — a natural refusal/redirect case),
  `samples/r3-field-absent.json` (absent field — the "그 정보는 공시에 없습니다" case).
- **Verbatim quotes for citations** are inside those samples' field views (the same
  quotes R3's detail cards cite) — an example answer's citations must be those real
  spans, never paraphrases.
- Korean state copy: `grounding/copy-inventory.md`, `grounding/states-and-trust.md`
  (철회/추후결정/불일치 vocabulary). Suppression reason codes have **no Korean copy yet**
  (that's R7's operator question) — a refusal card should state the *category* factually
  without inventing per-reason wording.
- An example streamed answer is **authored content** — compose it strictly from the real
  fields/quotes of one pinned filing and label the card as a composition example, the
  way `LookupEmpty` labeled 삼성전자.

Missing real content → ask; never invent.

## 5. Required outputs (a round is incomplete without all three)

1. **Card set** — line-1 `@dsCard` markers, review-time group `⏳ P3.S7 · Explain`:

   - `explain/Entry.html` — the entry point(s): nav-link destination + contextual entry
     from a detail page
   - `explain/Panel.html` — the panel with a complete grounded answer + inline citations
     (on a real pinned filing)
   - `explain/Streaming.html` — SSE states: mid-stream, complete, error/retry
   - `explain/Refusal.html` — non-gate-passing refusals (철회, 확정 전, absent field)
   - `explain/ExplainMobile.html` — the 해설 experience at 390px

   Split further freely; never a monolith.

2. **Record of what was designed** — refresh `handoff-output/result.md`; log every
   departure and all proposed copy (refusal copy especially).

3. **Implementation contract** — refresh `handoff-output/build-prompt.md`; state the
   token delta explicitly (none expected, but say so).

**Definition of done: the cards appear in the pane** under `⏳ P3.S7 · Explain` and the
refreshed record + contract exist.

## 6. Open questions — posed to the session, not answered here

1. What does the nav "해설" link open — a destination page, or does the nav slot change
   meaning now that 해설's primary home is contextual? (This finalizes the provisional
   nav label from R2.)
2. Question affordance: free input, preset questions derived from the event's actual
   fields, or presets-first with free input behind them?
3. What is a question's scope in this round — per-event only, or also portfolio-level
   (and if portfolio-level, how does it interact with the R5 sample)?
4. How does a citation render inline in streaming prose — and is the quote expandable in
   place or a jump to the detail/DART?
5. Is 해설 fully anonymous, or does anything (rate limits, question count) differ with an
   account — and how is a quota surfaced honestly if one exists? (Quota/cost *observation*
   is R7 admin material; this is the user-facing face of it, if any.)
6. Do answers persist (session-only recall like R4's holdings, or nothing persists)?
7. Refusal copy: the factual sentence family for "데이터가 검증을 통과하지 못해 해설할 수
   없습니다" — proposed wording logged for sign-off.

## 7. Operator setup + definition of done

Same project; pull latest `main` in the session first (this handoff + R1–R5 landed
records). When the cards are up and the record/contract refreshed, tell the orchestrator
to resume. Approval must be literal.
