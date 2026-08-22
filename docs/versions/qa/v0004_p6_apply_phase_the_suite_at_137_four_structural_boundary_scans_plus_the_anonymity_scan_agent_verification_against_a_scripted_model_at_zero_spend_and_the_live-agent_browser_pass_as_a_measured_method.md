---
doc_id: qa
version: v0004
created_at: 2026-08-22T22:59:53+09:00
source: P6.REVIEW
summary: P6 apply phase: the suite at 137, four structural boundary scans plus the anonymity scan, agent verification against a scripted model at zero spend, and the live-agent browser pass as a measured method
previous: v0003_p5_apply_phase_the_suite_at_118_plus_the_framework-free_frontend_check_real-browser_verification_as_a_method_and_d1_d4_closed_off_the_fragile_list
---

# QA

## Status

P2 established how this repo measures extraction accuracy and produced the first numbers. The
**method** is the durable part; the accuracy numbers are true of the corpus as it stood on 2026-08-20
and are re-measurable at **0 OpenDART requests and 0 LLM calls**. **P5 added two more layers of
verification**: a framework-free frontend check, and **real-browser verification as a durable
method** — which is what a product whose whole claim is "never show a wrong number" actually needs.
The Python suite grew **59 → 118** across the phase.

**P6 added a third layer: verifying a non-deterministic component deterministically.** The agent's
guarantees are structural, so its tests are structural too — a scripted model drives the loop, which
means the whole suite still **spends nothing and needs no credential**, and the live model is used
only to measure what a script cannot (does it actually choose its own tools, and does the citation
gate ever block something a reader should have seen). The suite grew **118 → 137** and still runs in
~3.5 s with no network, no model and no database.

## Provenance — read this before quoting any number below

**The labels are cross-model judgements: Claude (Opus 5) judging Gemini extractions, at the
operator's direction (2026-08-20). They are explicitly not human ground truth — 0 of the 344 labels
were verified by a person.** Every quote of an accuracy figure must carry that qualifier.

The qualifier is mechanised, not merely written down: `evalset/labels.json` carries a `judged_by`
block (`judge` / `basis` / `imported_at` in KST), `Labels.write()` refuses to write an unstamped file,
`import --judged-by` is **required and never inherited** from the previous file, and the report prints
what the artifact says rather than any hardcoded sentence. A human re-judgement is cheap and open:
overwrite column A of `evalset/sheet.csv`, re-run `import` with a new `--judged-by`, and the report
states the new judge. See `decisions` D-7.

## Test Commands

| purpose | command | expectation |
|---|---|---|
| unit suite | `.venv/bin/python -m pytest` | **137 passed**, ~3.5 s, no network, no model, no DB, **no `GEMINI_API_KEY`** (one known Starlette/httpx deprecation warning) |
| workspace | `python3 scripts/workflow.py validate` | `Workflow validation passed.` |
| **frontend** | `cd frontend && npm run build && npm run typecheck && npm run smoke` | build green (**16 routes**), `tsc --noEmit` clean, **15/15** `node:test` cases in ~170 ms |
| gates (deterministic) | `.venv/bin/python -m mijual.gates run` | **710 field rows** (the P2 split plus 47 passed / 14 not_evaluable `appraisal_price`); **488 exposable events**; two runs byte-identical |
| exposure summary | `.venv/bin/python -m mijual.gates summary` | 488 exposable of 628 considered, **418 renderable field instances** |
| estimate | `.venv/bin/python -m mijual.estimate report --today YYYYMMDD` | ▷ 718.1억원 / 32 offerings / 14.02 %; byte-identical across runs |
| accuracy | `.venv/bin/python -m mijual.evalset report` | the table below, incl. the 판정 출처 line |
| whole pipeline, offline | `.venv/bin/python -m mijual.scheduler once --offline` | **six** stages green, **0 requests / 0 calls / ▷ $0.0000** |
| derived re-scores | `.venv/bin/python -m mijual.extract --dry-run recheck` · `... evalset refresh-recall` · `... estimate reparse` | idempotent; a second run writes nothing |

**The frontend check is deliberately framework-free.** `npm run build` prerenders through the shell
and every primitive, so a broken component fails the build; `npm run smoke` is `node --test lib/*.ts`
with **no jest, no vitest, no jsdom and no fixtures**, covering what a render cannot show — the CSRF
header on a mutation and not on a read, the error envelope becoming a typed error, the ⌊N ×
배정비율⌋ arithmetic reproducing R4's own card figure, 확정발행가 `null` producing no money number,
and the beat-coverage join behind 「실행 기록 없음」. Adding a browser-test framework here would be
the fixture sprawl the repo rule forbids.

**P6's frontend cases follow the same rule and test what a render cannot**: that a frame split across
network chunks is decoded once and whole, that a turn paints its tool rows, numbered chips and footer
and ends complete, that a pre-stream refusal leaves the turn in the signed 중단 state **with nothing
invented**, and that a reader's 중지 keeps the partial answer. They run against **the real SSE bytes**
a scripted turn produced, fed back in 3-byte chunks so frames *and* multi-byte Korean are split — a
purpose-built fixture would have proved less.

### Testing a component that is deliberately non-deterministic

The agent's control flow is the thing that must be verified, and a scripted model verifies it exactly:

- **"The model chooses" is a test, not a claim.** A scripted three-round turn asserts that round 2's
  request contains round 1's tool result — the chain exists because the model asked for it, not
  because the loop scripted it — and a 계산 요청 turn asserts **zero** tool calls, which is the loop
  having no mandatory pre-fetch rather than the model being lucky.
- **The citation gate is tested by its four failure modes at once**: a sentence with no marker, a
  marker naming an id no tool returned, a number that appears nowhere upstream, and a quote that is
  not verbatim — one survivor out of five sentences, and the blocked count reported.
- **Degradation is tested as carefully as success**: a turn that verifies nothing falls back to the
  signed family, a budget ceiling ends the turn `aborted` **without** inventing a refusal about the
  data, and a disconnected turn's stored row is asserted equal to what the terminal would have said.
- **The five refusal families are asserted by their signed sentences**, so a paraphrase fails the
  test the same way it fails the gate.
- **The whole agent suite spends nothing.** Verified: with `GEMINI_API_KEY` unset, the app builds and
  the SDK is never imported.

Tests stay terse — minimal high-value cases, no fixture sprawl. There is still no automated E2E
layer; **real-browser verification is a driven method, not a suite** (below).

## Real-browser verification (the P5 method)

The product's claim is that it never shows a wrong or unbacked number, and that claim lives in the
rendered page, not in the payload. So each frontend slice drove the **built** product in headless
Chrome over CDP — `npm run build && npm run start` plus uvicorn against the live corpus — and the
final fidelity pass swept **~230 scripted checks across 11 stages** at 1440 / 768 / 390 plus the
intermediate widths, with screenshots kept per surface.

**What that method is for** is measuring the trust rules against the *served* payload rather than
eyeballing them: 40 board D-days byte-identical to `countdown.dday`, the countdown 0 s off the served
instant, no untagged estimate and no tagged fact, no money before 확정발행가 on any of the three
money-bearing surfaces, a gate-blocked field absent rather than placeheld, and 조회 ↔ 포트폴리오
agreeing to the won. It also caught what unit tests structurally cannot: a global CSS rule silently
flattening 23 surface-stated font sizes, 41px of horizontal overflow in one width band, and a
half-sans "mono" line putting a D-day numeral outside R1's mono rule.

**Four traps worth more than they look**, all of which produced confident wrong readings first:

1. **Check over `http://localhost:3000`, never `127.0.0.1`** — Next 16's dev-origin protection 403s
   two client chunks for a foreign host, so hydration never completes and the check silently measures
   an un-hydrated page. `curl` returns 200 for the same URLs, which makes it look fine.
2. **`npm run start` fails silently into its log with `EADDRINUSE`** if an older server holds the
   port, and the stale server serves a manifest whose CSS chunks 500 — indistinguishable from "my fix
   did nothing". Confirm a CSS chunk returns 200 before believing any measurement.
3. **Flattened-`innerText` proximity checks yield false failures.** Several "FAIL" lines across the
   phase were probe artifacts (a verbatim 정정 요약 containing 원, a header date near a badge, a frame
   line checked before a count was typed). Re-measure with a scoped selector before believing one.
4. **Measure a tap target on the enclosing `<label>`, not the native checkbox**, and scope
   reader-chrome nav assertions to the *first* `header nav` — the mobile sheet is always in the DOM.

**P6 extended the method to a live agent, and added three traps of its own:**

5. **⚠ `curl` and a browser are different clients, and the difference can hide a whole signed state.**
   The streaming endpoint measured perfectly unbuffered under `curl` and delivered nothing
   incrementally to a real browser — because `curl` sends no `Accept-Encoding` by default and a
   browser asks for gzip, which the dev proxy obligingly applied to the event stream. **Time the wire
   with `curl --compressed` and the reader with a `MutationObserver`.**
6. **⚠ A `Response.clone()` tee installed to capture raw stream bytes buffers, and therefore lies.**
   It reported one 2 KB chunk where the wire had seven frames spread over seconds — which would have
   hidden the bug above entirely. Never time a stream through a tee.
7. **The re-measure rule held again, five more times.** Every "FAIL" in the pass was a probe artifact
   (an `nth-child` selector matching a ring instead of a close glyph, a transparent overlay winning
   `elementsFromPoint`, a transform read mid-transition, a sticky bar measured on the wrong wrapper,
   and one case of checking the wrong tab entirely). **A browser-probe FAIL is a hypothesis.**

**Verifying an agent in a browser means verifying its output against the data, not eyeballing it.**
The live pass ran **25 turns** covering all five refusal families and checked, mechanically: every
stored 인용 칩 원문 byte-identical to a value the served payload carries (**27/27**), and every
numeral in every stored answer traced to that turn's own payloads (**0 unaccounted for across 24
answers**). Those two numbers are the trust claim, measured on prose a model wrote.

**Hygiene rule for a browser pass:** create test accounts through the product and delete them through
the product's own 계정 삭제; pass operator credentials as process env vars for that run only and
never open the operator's `.env`; leave `NEXT_PUBLIC_VOCKY_SRC` unset so no third-party script loads;
stop both servers afterwards.

## The Measurement Method

- **A frozen, stratified sample.** `evalset/sample.json` holds **344 (filing, field) rows over 99
  filings**, drawn deterministically (seed 20260907, per-stratum seeded shuffle over a sorted pool)
  and frozen with every row's value, quote, context and gate verdict. The report reads two JSON files
  and **never the database**, so a label stays meaningful after the corpus moves under it.
- **Both error directions are measured.** Precision of gate-passed/`tbd` rows (what the product would
  show) **and** the gate's **over-blocking** rate on the rows it blocked — because a gate can buy any
  precision figure by blocking more, and one such pattern is already priced at ▷ 49.2억원 of the
  headline.
- **Rates come only from the random draw.** Known hard cases (철회, 추후결정, span-unresolved, gate
  failures, the 실권주 cells that disagree with their own tables) are over-sampled on purpose and
  reported case by case; a `booster` pick adds 정정-해석 rows *only*, so no field's own sample stops
  being random.
- **Strict is the headline.** `partial` counts as a miss; the lenient figure is stated beside it.
  Every rate carries a **95 % Wilson** interval.

## Measured Results (2026-08-20)

**Precision of what the product would show: 98.6 % strict — 213/216 random picks, 95 % CI
[96–100 %]; 100 % counting `partial`.** Labels: 339 `correct` / 5 `partial` / **0 `wrong`** / 0 `skip`
across all 344 rows.

**Over-blocking: 100 %** — 19/19 blocked rows in the random draw, and **48/48** across every pick,
were judged correct readings. In this sample the gate bought **no** precision: it removed no error and
removed 48 true statements. Of those 48, **30 are blocks the product wants** (`field_absent`,
`superseded_api_reference`); 18 are actionable (stale API reference data, single-span citation for
multi-line quotes, a quantified 개월 withheld for an underived 해제일).

**Corpus-wide gate-block rate: 12.2 % (77 of 633 distinct `(rcept_no, field_key)` rows)** — 0 % on
증권발행실적보고서 figures (no model reads them), 4–8 % on ① prose, and **44 % on ③**, which needs its
split every time it is quoted: of 11 blocked `dissent_notice_procedure` rows, **8 are
`superseded_api_reference`**, 1 `api_deadline_absent`, 1 `field_absent`, and exactly **1** is a real
`dissent_period_mismatch`. Quoting 44 % without that split reads as "③ is badly extracted", which the
data does not say.

**정정-해석 recall proxy: 88.70 %** — 177 deterministic `3. 정정사항` rows, 20 unmentioned by the
model, **0 unsupported of 157 model changes**, over 45 records with a parsed table (3 records without
one are excluded and already blocked `no_correction_rows`). This is a **measurement, not a floor**:
the earlier 85.31 % was a matcher artifact (several model changes could bind to one table row), fixed
in P2.F4 and re-scored over stored records at 0 calls / 0 requests. ▷ At the content level the model
covers ≈ 99 % of investor-meaningful items; the residue is boilerplate rows.

**The whole strict-error surface is one defect class.** All 3 strict misses are 실적보고서 values
**correctly summed** from two table rows (예탁결제원 청약 + 직접청약) but cited by one addend (SKC
`20260522000297` ×2, 에스에너지 `20260312000380`). Summing is the right behaviour — not summing would
under-report 청약 and over-report 실권주 — so the defect is the citation contract, not the reading.
▷ ~3 of the corpus's 31 실적 filings carry the split-row form. Tracked as deferred job **D4**.

## Regression Checklist

- [ ] `pytest` green (**137**) and `workflow validate` clean.
- [ ] `cd frontend && npm run build && npm run typecheck && npm run smoke` green (**15/15**).
- [ ] `gates run` twice → **byte-identical** output, and the verdict split unchanged over **710** rows
      unless the corpus grew.
- [ ] **The structural guards still guard.** These encode rules that are cheap to break by accident
      and expensive to notice:
      - the **four** AST import scans — no request-path or derivation-layer module imports a spending
        module; **no module under `mijual.web` imports a model SDK** (the model is reached only
        through `mijual.agent`); **`mijual.agent` imports no spending module**; only the vocky module
        imports an HTTP client;
      - the **anonymity scan** — no account/email/IP/UA column on either conversation table, **no
        foreign key in either direction**, nothing on `account` naming a conversation. *Adding a
        foreign key to a conversation table fails this, by design.*
      - the **tool signature check** — no tool takes an identity argument, and `get_portfolio()` takes
        none at all;
      - the ops surface carrying **no** unsafe method beyond login/logout, and `WriteSession`
        refusing a safe method.
- [ ] **No reader-facing quota or storage-denial copy exists.** Grep the frontend for 「남은 질문」,
      「저장 이력 없음」, 「탭을 닫으면」 and quota strings in the AI 질문 surfaces, and for
      `localStorage` in them (the thread is `sessionStorage`, one key). The 「탭을 닫으면 사라집니다」
      that legitimately exists belongs to the 보유량 conversion offer — a different surface under a
      different signed rule.
- [ ] **The agent's own two numbers, if a live pass was run**: every stored 인용 원문 byte-identical
      to a served payload value, and every numeral in every stored answer present in that turn's
      payloads. Both were 100 % / 0 misses at the P6 pass.
- [ ] Exposure invariant re-derived read-only: **0** renderable fields outside `passed`/`tbd`, **0**
      `tbd` fields carrying a value, **0** exposable events in a non-exposable state. (Four lines
      through `mijual.gates.exposure.exposure_of_all`; it is the product's trust claim in one number,
      and anything that touches the exposure contract must re-run it.)
- [ ] `estimate report` twice → byte-identical, headline unchanged.
- [ ] `scheduler once --offline` → **six** stages green at 0 requests / 0 calls.
- [ ] After any corpus change, the rendered numbers were re-measured, not assumed: the landing
      headline pair, the five board counts, and one 조회 breakdown against the served payload.
- [ ] `extract recheck` and `evalset refresh-recall` → second run writes nothing.
- [ ] No secret value appears in any tracked file or generated artifact.
- [ ] No committed claim describes the evalset labels as human ground truth.
- [ ] Any regenerated summary artifact was regenerated **from the final run** whose numbers the prose
      quotes (P1 shipped a stale one once).

## Known Fragile Areas

| area | state | tracked as |
|---|---|---|
| ~~multi-addend 실적보고서 citations~~ | **CLOSED (P5)** — **0 of 269** stored figures uncitable (was 7); a figure is cited by one cell, by every addend, or by none, and any other combination is unconstructable. The evalset sheet shows the grader every addend too | ~~D4~~ |
| ~~② 정정 filings paired to the wrong 사채~~ | **CLOSED (P5)** — identity-scoped pairing took ② gate failures on exposable events **6 → 1**, and the survivor is a `span_unresolved` citation defect, not pairing. New invariant: **0** extraction rows on any of the 488 exposable events cite a filing their event does not hold | ~~D1~~ |
| two `rcept_no` rendering on two exposable events each (코이즈 `20260122000058`, 사토시홀딩스 `20251219000402`) | still open, and **its trigger did not fire in P5**: no two of the 450 rendered board rows share an `rcept_no`, and 코이즈's 놓친 돈 total is not double-counted (the breakdown keys on the 실적보고서, which is unique). Nothing was de-duplicated at display level | deferred **D2** |
| unattended thinking level for the 정정 해석 task | inherits the project preset; a beat run would decide it for a human | `operations` / `decisions` D-4 |
| the 철회 detector on ③ | no real case in the corpus; unit-tested on a constructed row only | `data` |
| **19** duplicate `(rcept_no, field_key)` extraction rows | harmless for verdicts, but a rate computed on 710 instead of **691** is subtly wrong. The ops panel now **serves both bases** with every rate, so the denominator is never implicit | note when computing rates |
| expired `auth_session` / `ops_session` rows are never pruned | grants nothing (expiry is checked), but the tables grow monotonically | `operations` / P4 |
| **the citation gate's number check is membership, not semantics** | a small integer or a year is effectively always allowed, because it appears *somewhere* in a payload. What it reliably catches is a value present **nowhere** upstream — which is the shape of every computed or invented figure. Recorded honestly rather than overstated | `backend` / `architecture` |
| **the streaming path has no heartbeat** | longest observed inter-frame gap with the live agent is **6.0 s**; an idle timeout below ~10 s cuts legitimate turns, and the deployed topology (edge / CDN / nginx) is unmeasured | `operations` / P4 |
| **the agent's declaration construction is exercised only live** | the SDK is not installed in the test venv, so the plain tool-spec data is unit-tested and the SDK object construction is not. A live turn is what proves it | `backend` |
| **agent spend is invisible under a default `uvicorn`** | the ▷ ledger is `log.info` and uvicorn configures only its own loggers, so without a root logging configuration the record is written nowhere | `operations` / P4 |

## Open Questions

- ~~No browser/E2E QA exists yet~~ — **the method now exists and ran**, and a blocked field was
  verified absent rather than placeheld on real pages. What is still missing is **automation**: every
  browser pass to date was driven by a scripted CDP session written for that pass, not by a
  checked-in suite. Whether that becomes a committed E2E layer is a real question, and the repo's
  terse-tests rule argues for keeping it a method rather than growing a framework.
- Whether a human spot-check pass over a subset of the 344 labels is worth its time before submission
  (it would upgrade the provenance statement, not the machinery).
- **Whether a deterministic two-witness field belongs in an *accuracy* evalset at all.**
  `appraisal_price` is outside the evalset's universe by construction (the sampler skips a field key
  that is not in the prose registry), which is arguably correct — measuring hallucination rates on a
  field that cannot hallucinate would dilute the number. Recorded rather than decided.
- **No load or performance budget exists.** Payload sizes and timings were measured per surface
  (`/board` 160 KB in ~54 ms, a detail 6–15 ms, the portfolio 18 KB in 37 ms, the ops 개요 67 ms) but
  nothing is paged, nothing is cached and no threshold is enforced. Fine at this corpus size; a P4
  question if traffic is ever real.
