# Design Handoff — Round 7: admin panel — 운영 관제

- Round: **R7 of 7 (final)** · slice `P3.S8` · written 2026-08-21
- Status: OUT — awaiting the design session (Claude Design + operator)
- Repo: `leetusik/Mijual` via Connect GitHub (main, pushed at handoff commit)
- Builds on: **R1–R6 signed designs** (locked — cosmos theme, craft panels, chrome,
  trust primitives, Citation, 「추정」, detail/조회/계정/AI-질문 contracts). Changing
  any of them is a new superseding round.

## 1. Product context

The last surface is the one only the operator sees: the panel that watches the
machine. Everything the end-user surfaces *hide* by design — suppressed events,
gate-blocked fields, pipeline spend, model provenance — has to be *visible*
somewhere, or the operator is running §3.6's deterministic gates blind. This round
designs that somewhere.

Two things make this round different from R1–R6:

- **The audience is the operator, not the reader.** Density, English reason codes
  as raw data, and ops-shaped tables may all be right here where they'd be wrong on
  the reader surfaces — how far the admin panel departs from the reader idiom (or
  deliberately doesn't) is this session's core call.
- **It closes two loops opened by earlier rounds.** R6 stored anonymous
  conversations server-side *specifically so this panel can review them*, and R6's
  agent `save_feedback` tool feeds a 운영자 검토 대기열; the operator resolved that
  vocky exposes an observation API *specifically so this panel can watch collected
  feedback*. Both viewers live here or nowhere.

## 2. Scope checklist — what this round must cover

- [ ] **Pipeline run / beat status** — the beat schedule, last run per stage with
      its counts and request/LLM spend (each stage already prints counts + a ▷ cost
      line), the pipeline lock state, and failure visibility (a beat that didn't
      run is a fact the operator must see, not infer).
- [ ] **Gate-blocked field / reason-code review queue** — the fields that failed
      their gate (`FieldView.reason_code`) and the events carrying blocking flags
      (`BLOCKING_FLAGS` — these four have Korean copy in code), as a workable queue:
      what the operator sees per item and what "reviewed" means here (observation
      only, or an action?) is in play.
- [ ] **Event state inspection** — suppressed / withdrawn / flagged events with
      their reason codes. **Suppression reasons (`no_appraisal_right`,
      `superseded_by_pairing`, `unpaired_correction`, 소규모합병 …) have NO Korean
      copy anywhere in the codebase** — this panel is the first surface that needs
      them. Operator question §6.1; never invent the wording.
- [ ] **Accuracy & evalset report view** — the frozen 344-row evalset report,
      including `judged_by` provenance (the 판정 출처 line): the honesty machinery
      of the accuracy claim, rendered.
- [ ] **Quota / cost visibility** — daily OpenDART quota (20,000 requests/key)
      versus spend, and LLM call spend, at whatever granularity the ops doc's
      numbers actually support.
- [ ] **vocky feedback observation view** — collected feedback read through vocky's
      observation API (operator-resolved 2026-08-20). API shape is an operator
      question (§6.3); design the view against what the operator says it returns.
- [ ] **Anonymous conversation log viewer (from R6)** — the server-stored 해설
      Q&A logs for quality/refusal review. The reader-side promise is exactly
      「대화는 익명으로 저장됩니다 (품질 점검용)」 — this viewer must stay inside
      that promise (anonymous; quality review), and refusals are first-class here
      (reviewing *what was refused and why* is the point).
- [ ] **Agent feedback queue** — R6's `save_feedback` tool lands user feedback in a
      운영자 검토 대기열; its review view (and how it relates to the vocky view —
      merged or separate) is in play.
- [ ] **Access** — how the operator reaches this panel at all (§6.4). R5's auth is
      the reader-facing account layer; whether admin is an R5 account with a flag,
      a separate door, or something simpler is undecided.
- [ ] Desktop composition first; state explicitly what (if anything) mobile gets.

Cross-cutting: team language is English but the **product surface is Korean-only**
— whether that rule binds an operator-only surface, or raw English codes are
honest data here, is itself in play (§6.1 folds into this); 「추정」 discipline and
urgency color-never-size still apply wherever reader-facing numbers are echoed.

## 3. Locked vs. in play

**Locked:** R1–R6 signed systems and contracts; §3.6 (this panel *observes* the
gates, it never overrides a gate verdict silently — any action design must not
create a path where unverified data reaches readers); the R6 storage promise
(anonymous, 품질 점검용); reason codes and state vocabulary as they exist in code;
no invented ops data — every number on a card comes from the grounding pack or the
ops doc.

**In play:** everything visual and compositional — whether admin lives in the
cosmos idiom or deliberately departs; information architecture (one dense page vs
sections); queue interaction model (read-only observation vs actions, and what
actions exist); table/density patterns; how spend and quota render; log-viewer
composition; the admin door; mobile stance.

## 4. Where to look — real content, never lorem

- **Ops truth**: `docs/current/operations.md` — beat schedule, per-run request
  counts (S3 289, S7 584, S8 ~337, F1 585), the 20,000/day quota, the pipeline
  lock, the zero-spend regeneration paths.
- **Accuracy truth**: `docs/current/qa.md` — the evalset method, the report
  command, `judged_by` provenance, the first measured numbers. Render *those*
  numbers, dated.
- **States & reasons**: `grounding/states-and-trust.md` and
  `grounding/copy-inventory.md` §"reason codes" — which codes have Korean copy
  (the four `BLOCKING_FLAGS`, `WITHDRAWN_NOTICE_KO`) and which have none
  (suppression codes — §6.1).
- **Real queue material**: the pinned samples — `samples/r1-withdrawn.json`
  (썸에이지, a withdrawn event to inspect), `samples/r3-field-absent.json`
  (a gate-failed field with its reason code), plus the board snapshot's counts
  (488 exposable: ① 50 / ② 422 / ③ 16, dated 2026-08-20) for realistic totals.
- **Conversation-log material**: compose example log rows strictly from the R6
  cards' real Q&A (실권주 question + its cited answer; the four refusal cases) —
  they are the only conversations that "exist"; label the card as a composition
  example.
- **vocky**: no schema exists in this repo. Whatever the operator provides in
  session (§6.3) is the grounding; if none arrives, design the frame and mark the
  rows explicitly as awaiting the API shape — never invent field names silently.

Missing real content → ask; never invent.

## 5. Required outputs (a round is incomplete without all three)

1. **Card set** — line-1 `@dsCard` markers, review-time group `⏳ P3.S8 · Admin`:

   - `admin/Overview.html` — the panel's shell + pipeline/beat status
   - `admin/GateQueue.html` — the reason-code review queue + event state inspection
   - `admin/Accuracy.html` — the evalset report view + quota/cost visibility
   - `admin/Conversations.html` — the anonymous 해설 log viewer + agent feedback
     queue
   - `admin/Feedback.html` — the vocky observation view
   - `admin/Access.html` — the admin door (per §6.4's answer)

   Split or repack freely; never a monolith.

2. **Record of what was designed** — refresh the round's `output/result.md`; log
   every departure and all proposed copy (suppression wording especially).

3. **Implementation contract** — refresh the round's `output/build-prompt.md`;
   state the token delta explicitly (none expected, but say so).

**Definition of done: the cards appear in the pane** under `⏳ P3.S8 · Admin` and
the refreshed record + contract exist.

## 6. Open questions — posed to the session, not answered here

1. **Suppression reason copy (the carried R7 question):** the suppression codes
   have no Korean rendering anywhere. Does the operator supply Korean wording per
   code, or rule that raw English codes are the honest rendering on an
   operator-only surface? Either answer must be signed — never invented.
2. **Audience boundary (carried from the phase):** operator-only, or does a
   judge-visible "how the gate works" read-only view exist (challenge-judging
   material)? If judge-visible, which sections, and does that change the
   Korean-copy answer to §6.1?
3. **vocky observation API shape:** what does it return (fields, granularity,
   pagination)? Operator-provided in session; the view is designed against the
   answer.
4. **The admin door:** how does the operator authenticate — an R5 account with an
   admin flag, a separate credential, or out-of-scope for design (e.g. network-
   level)? Decides whether an admin login surface exists at all.
5. **Queue semantics:** is the gate/review queue pure observation, or does
   "reviewed/dismissed" state exist — and if actions exist, which ones are safe
   under the locked rule that no action silently overrides a gate verdict?
6. **Panel idiom:** same cosmos-dark system, or a deliberate operator-density
   variant? (A visual decision — the session's, listed only because it shapes
   every card.)

## 7. Operator setup + definition of done

Same project; pull latest `main` in the session first (this handoff + R1–R6 landed
records). When the cards are up and the record/contract refreshed, tell the
orchestrator to resume. Approval must be literal.
