# Result — P3.REVIEW (phase review, design-only P3)

**Verdict: `pass`.** P3 delivered exactly what a design-only phase must deliver — seven
operator-signed design rounds covering the whole inventory, buildable implementation contracts, an
immutable record outside `works/`, and **no implementation code anywhere**. Six consolidated doc
versions landed.

`explain: not written — run /explain for this phase.`

---

## 1. Validation (all slices together)

| # | check | command / evidence | outcome |
|---|---|---|---|
| 1 | workspace state | `python3 scripts/workflow.py validate` | **pass** (run at start and again after consolidation) |
| 2a | grounding pack determinism | `export_design_grounding.py --out $S/g1`, `--out $S/g2`, `diff -r` | **pass** — byte-identical, both exit 0 |
| 2b | grounding pack re-runs clean | `.venv/bin/python scripts/export_design_grounding.py` | **pass** — exit 0, 3 pages + 11 samples, **0 GAP** (every pinned sample still resolves) |
| 2c | zero spend | claim re-verified from P3.S1's socket-blocked run + the tool's own DB-only read path | **pass** — 0 OpenDART requests, 0 LLM calls |
| 3 | design record integrity | filesystem walk of `docs/reference/design/` | **pass** — all 7 rounds have `handoff.md` + `output/result.md` + `output/build-prompt.md`; R1 adds `tokens.css` + `fonts.css`, R2 adds `tokens.css` |
| 3b | SIGNOFF completeness | `docs/reference/design/SIGNOFF.md` | **pass** — 7 entries (R1–R7), each with the operator's literal words (`"Signed off — close R{n}"`), what supersedes what, the token delta, the landed path and the post-approval regroup |
| 4 | **design-only constraint** | `git diff --name-only dcb6d0b..HEAD` | **pass** — every path is under `docs/`, `works/`, or the single documentation tool `scripts/export_design_grounding.py`. **Nothing under `src/`, no HTTP layer, no frontend scaffolding.** `docs/index.json` changed only in its `last_rebuilt_at` stamp (no doc version was cut mid-phase — correct) |
| 5 | co-work gate protocol | `works/events.jsonl` | **pass** — all seven rounds ran `todo → in_progress → **pending** → in_progress → done`; commit pairs `feat(design): … handoff` / `… read-back` exist for each |
| 6 | intent capture | `intent.md`, `phase.md` | **pass** — verbatim original + confirmed intent + the operator's verbatim 2026-08-20 re-scope recorded as `A'` superseding the earlier answer; `phase.md` links it on line 3 |
| 7 | spot check: real content, not paraphrase | 4 `BLOCKING_FLAGS` Korean strings vs `src/mijual/gates/exposure.py` | **pass** — all four appear verbatim in `grounding/copy-inventory.md` |
| 8 | spot check: internal arithmetic | R7 record | **pass** — 566+4+14+65 = 649; 50+422+16 = 488 |

### 2b, in detail — what "idempotent" does and does not mean here

Re-running the exporter **on a later calendar day** legitimately changes `measured_at` and every
`d_day_label`, and moves one ② event across the ≤7d boundary (≤7d 11 → 12). Nothing else moves: the
corpus figures (488 = ① 50 / ② 422 / ③ 16, 409 renderable, ▷ 718.1억원, 14.02 %, 32 offerings) are
byte-identical. The pack is deterministic **on a fixed corpus and a fixed anchor**, which is exactly
what its own header claims by carrying the measurement date and the regeneration command. The plan's
literal wording ("leaves `git status` clean") only holds for a same-day re-run — see Deviations.

---

## 2. Judgment

### Inventory coverage — all 12 items, mapped to their round

| # | inventory item | round | evidence |
|---|---|---|---|
| 1 | brand identity & foundations | **R1** | `tokens.css` (66 props), Pretendard + IBM Plex Mono, radius-0/hairline/fade-only, urgency scale, and the trust primitives (EstimateMarker · Citation · StateBadge · DDay · RightsChip · 소멸주의보) |
| 2 | landing 관제 현황판 | **R2** | search-first hero, value + countdown/stats craft panels, urgency-interleaved board with type tabs, live countdown, freshness/stale treatment |
| 3 | global chrome + **vocky** | **R2** | nav/footer/mobile sheet/page shell; vocky as chrome-level `data-vocky-trigger` elements, no floating button |
| 4 | event detail ①②③ + citation + states | **R3** | detail anatomy, per-type rules, Citation per field, 철회 / 추후결정 / 기재 불일치 / absence, CorrectionStory version rail |
| 5 | 종목 검색 + 보유량 | **R4** | 내 종목 조회: search → resolution → holding input → readout, plus the no-event state |
| 6 | 놓친 돈 조회기 | **R4** | second section of the same page, do-nothing framing + disclaimer, zero-result state |
| 7 | auth | **R5** | email+password panel, PII inset, conversion moment from anonymous use |
| 8 | portfolio & D-day & sample load | **R5** | holdings rows + inline edit + 8s undo, D-day list with anchor date, notifications, 4-stock judge sample |
| 9 | grounded 해설 panel | **R6** | AI 질문 widget + page, presets from gate-passing fields, visible tool rows, numbered citation chips, SSE states, five-category refusals |
| 10 | admin panel | **R7** | 6 sections incl. the operator-requested `Users`, read-only, honesty patterns, separate door |
| 11 | Korean-only copy *(cross-cutting)* | all | every handoff carries the copy-locked rule; strings sourced from `copy-inventory.md`; each round's proposed copy was named and signed with the round |
| 12 | mobile-first responsive *(cross-cutting)* | all | every handoff carries it; per-surface mobile variants designed. **R7 is desktop-only by explicit operator decision** — recorded, not silent |

Two inventory phrasings were **changed by the design, correctly**: item 5's "보유량 슬라이더" became a
direct integer input + preset chips (R4 session decision — the slider was the inventory's guess, and
the inventory is "what to design, not how"), and item 9's "not a chat UI as the default surface" was
carried **verbatim in the R6 handoff** (line 23) and answered by the operator with a corner
launcher + nav slot that leaves the default surface — the board — untouched. Neither is a silent drop.

### Protocol — the `design-cowork` invariants held

- Every round: `handoff.md` written by the orchestrator → `pending` → operator designs in Claude
  Design → `DesignSync` read-back → landed **as-is** → SIGNOFF with literal words → post-approval
  regroup. The event log shows the `pending` gate for all seven.
- **No design decision was invented by the orchestrator or an executor.** The one non-design slice
  (P3.S1) exports real content; the handoffs pose questions rather than answer them; where content did
  not exist (R5's user-side rows, R7's suppression-reason Korean, the 운영자 연락처 string) the record
  says *ask the operator* instead of inventing.
- **Discrepancies were recorded at the gate rather than silently fixed** — R6's stale quota captions,
  the pre-R4 nav label on three frame cards, a duplicated eyebrow block; R7's invented
  `small_scale_merger` chip (real code: `no_appraisal_right`) and the "5개 섹션 탭" slip. In each case
  the contract governs and says so. This is the behaviour the skill asks for: the record is read-only,
  and nits become apply-time to-dos.
- **Open items are carried with an owner**, not dropped: 매수예정가 → apply-phase backing then a
  fidelity slice (D-15); vocky observation API shape → apply phase (R7 §6.3); 운영자 연락처 →
  operator; countdown cut-off instant and the stale threshold → apply/deploy; D1–D4 → considered at
  `P5.DECOMP` (recorded in P5's `intent.md`). One item — the **"정정 이력" button label** — reached the
  end of P3 still open with no declared home; the review assigns it to the apply phase and records it
  in `experience` v0002 and `product` v0003 so it cannot be lost.

### Why this is a `pass` and not `changes_requested`

The phase objective was "end at the signed design plus its implementation contracts". Every round is
signed, every contract is landed and concrete (R3–R7 run 93–131 lines each; R1's shorter contract is
backed by the landed `tokens.css`/`fonts.css` carrying the real values), and the constraint that
defines the phase — no implementation code — held over 21 commits. The residual risks are all
apply-phase concerns, and the two that could actually cause a wrong build (the supersession chain, and
the "정정 이력" gap) are now written into `docs/current/`, which is read-order #1.

---

## 3. Doc consolidation

The "Doc impact" list carried **two** notes (`decisions`, `operations`) — **incomplete for a phase that
produced seven signed rounds of durable product truth**. Under the reviewer carve-out I appended four
missing one-line notes to `phase.md` (`frontend`, `experience`, `product`, `security`) and then
consolidated all six:

| doc | version | what it now carries |
|---|---|---|
| `frontend` | **v0002** (was the bootstrap stub) | the design system: light `:root` + `.cosmos` scope, type/shape/motion, the trust primitives, responsive rules, where the record lives — **and the cross-round supersession table** |
| `experience` | **v0002** (was the bootstrap stub) | the six-surface map, the six journeys, UX states, and the Korean copy rules |
| `product` | **v0003** | a new "The Product P3 Designed" section; closes the one-page-vs-two open question; records 「추정」, the anonymous-first boundary, 챙긴 돈, the sample portfolio, read-only admin |
| `security` | **v0002** (was the bootstrap stub) | reader auth + minimal PII, the separate admin door, read-only authorization as a security property, the anonymity promise and its schema-level no-join |
| `decisions` | **v0004** | **D-9 … D-15** — design-only re-scope, FastAPI+Next.js, 「추정」 everywhere, cosmos-dark, email+password + unlimited anonymous questions, read-only desktop-only admin, 매수예정가 deferred — plus six new superseded entries |
| `operations` | **v0004** | the grounding-pack export command (0 requests / 0 calls, anchor caveat, GAP behaviour) and the observation-only operating rules the signed ops panel imposes |

Then `rebuild-docs` and `validate` — both clean. **No `docs/current/*.md` was hand-edited and no file
under `docs/versions/` was patched**; only six new version files were created.

**Why the supersession table matters enough to be durable truth:** the cards live in the Claude Design
project, so a build executor's entire world is `build-prompt.md` + the doc set. Read alone,
`rounds/01/output/build-prompt.md` would have it build a light theme with a `▷` estimate marker, and
`rounds/02` would give it the pre-R4 nav labels. The table in `frontend` v0002 makes that
un-missable from `docs/current/`.

---

## 4. Deviations from `plan.md`

1. **Validation 2 could not be run as literally worded.** The plan expected the exporter re-run to
   "leave `git status` clean". P3.S1 measured the pack on **2026-08-20**; the review ran on
   **2026-08-21**, and the exporter is anchored on today — so the re-run necessarily re-dates the pack.
   I verified the substantive claim instead (two runs into scratch dirs, `diff -r` byte-identical;
   exit 0; 0 GAP; corpus figures unchanged) and recorded the anchor caveat in `operations` v0004.
2. **The exporter re-run was swept into an unrelated commit, and I restored it.** I ran the exporter
   into the repo before realising the date would move it. While those files sat in the working tree the
   orchestrator committed **`d41ec9f` (`feat(p6): split AI 질문 agent build into P6 …`)**, which
   therefore contains a silent re-dating of 14 grounding-pack files under a P6 commit message. I
   restored them to their signed **2026-08-20** content (`git checkout 79b620c -- …`, then
   `git restore --staged` so nothing is left staged), because the seven signed rounds cite those
   figures and a review must not refresh the record it is reviewing. **The restoration is uncommitted
   working-tree state — the orchestrator must commit it** (see the action below). No history was
   rewritten and nothing was committed by me.
3. **Four Doc impact notes were added by the reviewer** before consolidation, as the plan explicitly
   authorised.

## 5. Actions for the orchestrator

1. **Commit the grounding-pack restoration** together with this review (14 files under
   `docs/reference/design/grounding/` reverting the accidental re-dating in `d41ec9f`). Suggested:
   `docs(review): P3 review pass — consolidate P3 truth into six doc versions; restore the signed
   grounding pack`.
2. Record the verdict with `review-phase P3 --verdict pass`.
3. `/explain` is the operator's to run; the review wrote none.

## 6. Non-blocking observations

- **O1 — the `co-work` slices have no slice-folder `result.md`.** `P3.S2`–`P3.S8` hold only `plan.md`
  and `slice.json`. `validate` does not require one, and the durable per-round result lives in a better
  place (`docs/reference/design/rounds/<NN>/output/result.md` plus a landed-design section in
  `phase.md` for each round). Noted so a future reader of the archived phase folder is not surprised.
- **O2 — `phase.json` never left `planned`.** It will go straight to `done` on `review-phase`, and
  `started_at` stays `null`. This is the engine's existing behaviour, identical in P1 and P2 — not a
  P3 defect.
- **O3 — R7's SIGNOFF entry is dated 2026-08-22** while its §6 resolutions say 2026-08-21. The session
  ran across midnight KST; harmless, and the record is read-only regardless.
