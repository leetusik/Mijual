---
doc_id: qa
version: v0018
created_at: 2026-09-04T17:03:04+09:00
commit: 58023f8e42fcc18cd06ffd2b0ca47a25b860f691
source: P12.REVIEW
summary: P12: the flicker-polish regression block
previous: v0017_p4_the_landing_idle-cost_lines_join_the_p4_regression_block
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
gate ever block something a reader should have seen). The suite grew **118 → 138** and still runs in
~3.5 s with no network, no model and no database.

**P7 (실서비스 정상화) added no verification layer and one test — it corrected the *rule* instead.**
The suite is **138 → 139** (`tests/test_web_stocks.py`, covering `GET /stocks/suggest`: the cap of 8,
the prefix-before-substring order, the digit path and the empty-list-not-404 miss). What P7 actually
contributed to QA is the discovery that the phase's whole premise — eleven reader-visible problems
that shipped through two fidelity passes — came from **verifying on the wrong origin in the wrong
runtime**, and the corrected floor below.

**P8 (디자인 폴리시 패스) added no verification layer either — it added a corpus of measurements and
one habit.** The suite is **139 → 142** (`P8.S1`'s hydrate-then-ask case in `lib/ask.test.ts`, plus
the three `POST /feedback` cases in `tests/test_web_feedback.py`), and `npm run smoke` **15/15 →
16/16**. What P8 actually contributed is that a *design fidelity* claim is now made the same way a
number claim is: driven from an isolated Chrome profile over CDP at every width the round names, in
`next dev` on both operator origins **and** in a production build, with `getBoundingClientRect` /
`getComputedStyle` probes instead of impressions — which is how 「체크 시 이동 0px」 became 0.00px and
how the production-only stylesheet-order width bug (`frontend`) was found at all. Two states the
corpus could not reach were verified against a **read-only scratch proxy** rather than left unclaimed,
and that treatment is now the recorded answer to "the branch is unreachable today".

**P9 (스마트 어시스턴트) added no verification layer and one measured method-note.** The suite is
**142 → 154** and `npm run smoke` **16/16 → 22/22**, all of it structural: a scripted model still
drives every agent case, so the suite spends nothing and needs no credential, and the new cases pin
the things that must not drift silently — the 식 line's placeholders against the function's own
parameters, the `expr` node whitelist against `__import__` / `a.__class__` / `a ** 999999` / an
undeclared name / `a / 0` / a comprehension / `open(…)`, `max_model_calls ≥ max_rounds`, the cache
prefix being byte-identical across a scoped turn and a different date, and the retirement of two
refusal families being visible in the suite rather than only in a docstring.

**What P9 contributed to QA is a correction to one of the two agent numbers.** 「every numeral in
every stored answer is present in that turn's payloads」 no longer holds *by construction*, because an
untraceable 공시 수치 now **ships marked 「미확인」** instead of being dropped. The invariant is
restated as **「every *unmarked* numeral is present in that turn's payloads」** — and the honest
companion fact is that the **stored row cannot distinguish the two**, since it keeps prose only. Both
passes measured it: a 16-turn live pass at `P9.S11` (인용 원문 **18/18** byte-identical, numerals
**81/87**, every miss a 오늘(KST) digit the reader saw hedged) and an independent 12-turn pass at the
review (인용 원문 **16/16**, numerals **57/57** against the turns' real tool payloads, calculator
included — 0 misses, because no turn asked for the date). Nothing was weakened to get there: a
computed number is traceable because the **calculator returns it**, not because the check was relaxed.

**One case covers the whole figure-grouping rule** (`P6.F1`), and it is scripted rather than live for
exactly the reason above: the guarantee has to hold whatever a model writes.
`tests/test_agent_loop.py::test_a_figure_reaches_the_reader_grouped_and_a_quote_reaches_it_verbatim`
drives one turn that releases `3,200원` from a raw `3200`, traces the already-grouped form through the
never-compute check in both directions, leaves `접수번호 20260724000546는 2026년 공시입니다` untouched,
asserts the stored answer carries the reader's form, and — in a second turn — keeps `「1591」`
byte-exact inside its span while the same digits outside it become `1,591원`. `tests/test_agent_tools.py`
covers the payload half: the served `("3200", "3,200")` pair, a ratio gaining nothing, and
`grouped(<14-digit 접수번호>) is None`. The live half is what a script cannot show — that the model
reads `value_display` and writes it unprompted — and it was measured once, not turned into a test.

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
| unit suite | `.venv/bin/python -m pytest` | **142 passed**, ~3.5 s, no network, no model, no DB, **no `GEMINI_API_KEY`** (one known Starlette/httpx deprecation warning) |
| workspace | `python3 scripts/workflow.py validate` | `Workflow validation passed.` |
| **frontend** | `cd frontend && npm run build && npm run typecheck && npm run smoke` | build green (**16 routes**), `tsc --noEmit` clean, **16/16** `node:test` cases in ~170 ms |
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

1. ~~**Check over `http://localhost:3000`, never `127.0.0.1`**~~ — **inverted by P7, and getting this
   backwards is what cost a whole fix phase.** The mechanism was read correctly (Next's dev-origin
   protection 403s client chunks and the HMR socket for a host not on its allow-list, so hydration
   never completes while `curl` still gets 200) and the conclusion was exactly wrong: `localhost` is
   the one origin that **cannot show this defect class**, and it is the operator's own
   `http://127.0.0.1:3000` that was broken. **Check on `127.0.0.1` and the Tailscale origin — never
   only on `localhost`.** The seam that makes them work (`allowedDevOrigins` + `MIJUAL_DEV_ORIGINS`),
   the matcher's host-only wildcard rules and the config-vs-env reload asymmetry are in `frontend`
   §Engineering traps; the operator-facing variable is in `operations`.
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

**P7 turned the method into a floor, because a pass that meets less than this has already shipped
eleven defects.** A browser check is complete only when it runs:

8. **In both runtimes and on the operator's own origins** — `next dev` on `127.0.0.1` **and** the
   Tailscale host, **and** a `next build && next start` production build. Every difference between
   the two runtimes gets written down; P7 found three (production-only `<Link>` prefetching, the
   dev-only `NEXTJS-PORTAL` focus stop, dev-only RSC requests on a nav self-link) and **no product
   behaviour differed anywhere**. Build in a *copy* of `frontend/` rather than stopping the dev
   stack (`frontend` §Engineering traps).
9. **At 1440 / 768 / 481 / 480 / 390** — the widget's signed boundary sits between the middle two.
10. **Along the functional dimension, not only the fidelity one.** Every visible control clicked once
   from a fresh page and its effect recorded (P7: **174 controls per runtime** across seven surfaces
   — the only genuinely inert ones in the product are the three vocky triggers); the whole keyboard
   path walked for traps and invisible stops; liveness held **≥60 s** for a countdown and **≥120 s**
   for typing (the dev reload lands at ~40 s, so a 30 s wait is a false negative in both directions).
   **Locate a control by a stable key, never by index** — one click can add or remove controls and
   shift every later index (P7 manufactured six phantom mis-clicks that way before keying them).
11. **With a control for every zero.** A probe that can only report 0 proves nothing: P7's copy sweep
   temporarily reverted the two trimmed strings, re-measured (2 / 2 / 1 occurrences), and restored —
   which is what makes the 0s a measurement. The CDP keyboard and scroll traps that made a working
   product look broken are catalogued in `frontend` §Engineering traps.

**The AI 질문 SSE contract now holds through the *production* Next router, captured from the browser
rather than from `curl`** (P7): a live turn on `next start` returned `content-type:
text/event-stream; charset=utf-8`, `cache-control: **no-store, no-transform**`, `x-accel-buffering:
no`, `transfer-encoding: chunked` and **no `content-encoding`** — so P6.F1's fix for the
gzip-buffering defect is verified on the path P4 will actually ship, not only in dev. Both turns
painted incrementally; longest inter-frame gap **3.0 s** in dev and **1.0 s** in production. There is
still **no heartbeat**, so a proxy idle timeout under ~10 s would cut a legitimate turn.

**Hygiene rule for a browser pass:** create test accounts through the product and delete them through
the product's own 계정 삭제; pass operator credentials as process env vars for that run only and
never open the operator's `.env`; leave `NEXT_PUBLIC_VOCKY_SRC` unset so no third-party script loads;
stop what you started and leave the dev stack as you found it (`make stack-status`).

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

- [ ] `pytest` green (**167**) and `workflow validate` clean. *(154 through P10; `P11.F1` added two
      `/ask/start-cards` cases, `P11.F2` two `/site/contact` ones, and `P4.F4` one for the
      `MIJUAL_EXTRACT_MAX_CALLS` ceiling.)*
- [ ] `cd frontend && npm run build && npm run typecheck && npm run smoke` green (**22/22**).
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
      to a served payload value, and **every *unmarked* numeral** in every stored answer present in
      that turn's payloads. The second was restated at P9 — under strip-don't-drop an untraceable
      공시 수치 ships **marked 「미확인」** rather than dropped, and the stored row (prose only) cannot
      tell a marked numeral from an unmarked one, so read the misses before calling one a defect. Both
      were 100 % / 0 misses at P6; at P9 인용 원문 stayed 100 % (18/18, then 16/16), and every numeral
      miss was a 오늘(KST) digit the reader saw hedged.
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

**P8 surface blocks** (added at the P8 review; every box was re-run there, in `next dev` on
`127.0.0.1:3000` and the tailnet origin and again against a production build):

- [ ] AI 질문: ask → reload → ask again renders two distinct turns, no duplicate-key warning, 재시도 hits the right turn (P8)
- [ ] 크롬: nav has exactly two links (AI 질문 · 보유 종목), no [의견] chip, no 샘플 chip, no data-vocky-trigger in the DOM (P8)
- [ ] 보유 종목: signed out renders the sample portfolio with its banner, signed in renders the account's own (P8)
- [ ] 의견 보내기: empty input disables 보내기, sending shows no spinner, failure uses no --alert colour, a 202 shows the 접수 번호 (P8)
- [ ] ≤480 sheet: overlays without pushing the page, closes on backdrop/Esc/×, body scroll released afterwards (P8)
- [ ] 푸터: ~~no mono anywhere, one row~~ — **superseded at P11.F2 by the operator's own
      instruction**: the identity row now ends 「… · {이메일} · {전화}」 with the **phone in mono**
      (an explicit operator override of R8 §4, recorded in `Footer.tsx`), and the row therefore
      wraps to two rows at **≤~840px** (73px tall above it, 118px at 768–820, 132px at 481–767).
      What still holds: **one** identity row (R8's deleted second row did not return), no invented
      Korean label, nothing overlapping or overflowing at any width, 「의견 보내기」 answering
      `elementFromPoint`, and at 390px 「AI 질문」 not orphaned on its own line (P8, corrected P11)
- [ ] no vocky value in the client bundle: grep .next/static for vk_ / vocky / the key prefix (P8)
- [ ] 관제 현황판: the first screen shows 15 ranked rows + 「15건 더 보기」 + 「남은 N건」; one click → 30 + 「처음 15건으로 접기」; a tab switch resets the window (P8)
- [ ] 보드 행: clicking anywhere on a row opens the event detail, 「↗」 still opens DART, Tab draws the focus ring around the row (P8)
- [ ] 보드 열: every row's D-day is flush with the panel's right edge and the expanded strip rows share the board rows' x-coordinates, at 1512 / 1119 / 768 / 390 (P8)
- [ ] 스트립: 펼치기 ↔ 접기 with aria-expanded, and a 추후결정 row shows the label with no date and no dash, 「추후결정」 in the D-day cell (P8)
- [ ] 카운트다운 카드: three stats, and 「읽은 실적보고서」 is absent from the DOM (P8)
- [ ] 소멸주의보: on a tied 청약 마감 the sentence says 「N개 종목」 instead of a company name, and matches /board/summary's next_lapse.tie_count (P8)
- [ ] 자동 갱신: leave the landing open for two intervals — no spinner, no layout move; a new 기준시각 shows 「갱신됨」 + a --live edge on the changed rows, an unchanged one shows nothing; the tab, window, expanded strips and scroll survive and the countdown does not jump (P8)
- [ ] 히어로 Enter: 「삼성」 + Enter selects the first candidate without navigating, a second Enter goes; an exact name goes on the first Enter; with no candidates it still submits GET /stocks?q= (P8)
- [ ] 390px 랜딩: the hero subtitle breaks between 어절 with no one-syllable orphan, no mono date splits across lines, and the strip button is a full-width 44px control under its sentence (P8)
- [ ] 상세 헤더: the four states (열림 · 닫힘 · 추후결정 · 부재) never render below 136px desktop / 248px at 390, and 「종료」 appears on no page (P8)
- [ ] 상세 390: no orphan 「→」/「·」 in the chain, diff or meta lines, and every citation trigger / rcept link / button measures ≥44px (P8)
- [ ] 인용: 「[근거]」 opens an overlay popover — the rows behind it do not move — and closes on ×, an outside click and Esc, with focus back on the trigger; at 390 the panel stays fully inside the viewport (P8)
- [ ] 섹션 밀도: no section repeats 「[근거]」 on every row, and a verbatim-only section closes with one 「DART 원문 {rcept} ↗」 line (P8)
- [ ] 정정 이력: the button flips to 「접기 ×」 with aria-expanded and a changed surface, and the diff renders two tagged sides (정정 전/정정 후) with no arrow column (P8)
- [ ] 아시아나 ③: two dashed 「현재 버전 공시에 없음」 chips (countdown slot + field row), no placeholder for any other field, and no reason given (P8)
- [ ] 개요: the screen-reader outline shows the h2 eyebrows and the ③ step h3s, and no accessible name contains 「//」 (P8)
- [ ] 404: /events/<nonexistent> and any unmatched path return status 404 with the Korean not-found, the requested path echoed, and no reason (P8)
- [ ] mono: no date or figure splits across lines at 1512 / 1440 / 1280 / 768 / 767 / 481 / 390 (P8)
- [ ] 조회 정체성: a resolved stock's h1 is the 종목명 with 종목코드/고유번호 under it, the search box echoes the name, and 「내 종목 조회」 appears exactly once on the page (P8)
- [ ] 보유량 스트립: present on a stock with a live ① or a 놓친 돈 row, absent on a ②-only stock (풍전약품) and a no-rights stock (세기상사) — with no disabled control and no explanatory sentence (P8)
- [ ] ② 표: every 전환사채 row of one stock renders in a single table with one 「DART 공시 API — … | N건」 source line, the corp name printed once, and an unserved fact shown as 「⋯」 (never 0) (P8)
- [ ] ③ 절차: 아시아나's 2단계 절차 block shows two numbered steps — dated windows when served, otherwise the dashed 「현재 버전 공시에 없음」 chip — and the two notations never mix in one block (P8)
- [ ] 놓친 돈 합계: a 1건 stock prints its figure once in the row with no total above it; a ≥2건 stock prints the total only after a holding is entered; each row carries its own 배정비율 line (P8)
- [ ] 조회 출구: 「상세 보기 →」 is the only link out of a 놓친 돈 row, and the 놓친 돈 prompt appears once per page and disappears once a holding exists (P8)
- [ ] 검색 불일치: /stocks?q=삼성 renders 「‘삼성’과 일치하는 종목이 없습니다」 with the correct 과/와 particle, and the first differing keystroke removes the line (P8)
- [ ] 빈 /stocks: with no query the page shows 감시 대상 3종 + 감시 중 N건 + the 집계 범위 section, and never a placeholder count when /board/summary fails (P8)
- [ ] 조회 390: no interactive target under 44px on any stock page or the entry, no horizontal overflow, and 767→768 is the only breakpoint on the surface (P8)
- [ ] 조회 신뢰: 계양전기 (발행가 확정 전) shows no 원 amount before or after a holding is entered while share counts still convert, no untagged 원 anywhere, and typing a holding fires no request carrying the number (P8)
- [ ] 프로덕션 폭: in a production build, **/stocks measures 620px and /stocks/{corp_code} measures 960px** — not only in next dev. (The pair was printed in the opposite order to its routes through P8; re-measured at P9 in dev and production alike.) (P8)
- [ ] 인증 게이팅: an empty submit on 로그인 · 계정 만들기 · 재설정 renders a Korean line with no browser bubble and fires no request; a malformed address renders 「이메일 주소 형식이 올바르지 않습니다.」; no required/pattern remains on any auth input (P8)
- [ ] 재설정 어포던스: 「비밀번호 재설정」 with an empty address is clickable, focuses the email field and sends nothing; it is disabled only while a request is in flight (P8)
- [ ] 로그아웃 플래시: 로그아웃 lands on /auth/login with 「로그아웃되었습니다」 above the h1, once, cleared by the first keystroke and still present after 10 s (no timer) (P8)
- [ ] 재설정 페이지: one 비밀번호 field with 「8자 이상」, no 이메일 field, no sample entry; an expired token renders its sentence plus 「로그인」, and a later 8자 미만 removes both (P8)
- [ ] 인증 기하: Auth.module.css has exactly one media query (max-width 767px), the primary is 100%×48px at 1456/768/767/390, and no auth control is under 44px (P8)
- [ ] 전환 밴드: on an anonymous /stocks/{corp} with a holding, the band is an inset block (no brackets) after 놓친 돈 and before 집계 범위, with no closing reassurance line; 닫기 leaves nothing and the same session does not ask again; signed in it never renders (P8)
- [ ] 전환 서열: DeadlineOffer renders nothing until /api/auth/me answers, then 「이 마감 알림 받기 →」 anonymous / 「보유 종목에 담기 →」 signed in, and every login lands on /portfolio (P8)
- [ ] D-day 기하: at 1440 every row of 다가오는 마감 and 지나간 마감 shares one chip/종목/라벨/카운트다운 edge set, the 소멸 금액's right edge equals the countdown's, and the anchor 「기준 … (KST)」 renders exactly once outside both sections (P8)
- [ ] 챙겼습니다: checking a 지나간 ① row flips 놓친 돈 → 챙긴 돈 and alert → live, keeps the amount and 「추정」, removes 「놓친 돈 상세 →」 from the money line, and moves nothing (measured 0px, desktop and 390); unchecking restores the link (P8)
- [ ] 보유 종목 표: the header labels sit over the cells they name, an empty 진행 중인 권리 cell is a 56px dashed rule (no sentence, no box, no —), and 수정 opens only the 보유량 cell with 저장·취소 swapping horizontally (P8)
- [ ] 알림 설정 프레임: the page has one h1 (마감 임박 이메일) and a 「← 보유 종목」 rail as the column's first row; 변경·로그아웃·계정 삭제 share one right edge; 로그아웃/계정 삭제/취소 are the same box size (P8)
- [ ] 계정 삭제 문장: 「계정을 삭제하면 …」 is absent until 계정 삭제 is pressed once, present while armed, and gone again after 취소 (P8)
- [ ] 샘플 전환 밴드: on an anonymous /portfolio the R12 band renders after 지나간 마감 without its lead line, once per session, and 닫기 leaves nothing; signed in it never renders (P8)
- [ ] 480 은퇴 (보유 종목): Portfolio.module.css has exactly one media query (max-width 767px) and no built CSS rule under any 480px query carries a Portfolio-module class; at 390/767 every 보유 종목 control is ≥44px (P8)
- [ ] AI 질문 경계: at 767/600/390 no launcher and no widget exist in the DOM on any reader route, and at 768 the widget is exactly 440×620 with 24px margins; opening it shifts <main> by 0px (P8)
- [ ] 프리셋 칩: every chip reads its served korean_name and sends its signed sentence (title = aria-label = the sentence); pressing one at 1440 puts the sentence in the thread and at 390 routes to /ask with the scope intact (P8)
- [ ] 한 단락: a streamed answer renders one <p> with inline sentences — 0 <br>, no pre-wrap in prose, no leading indent on continuation sentences (P8)
- [ ] 근거 N건: the footer's N equals the count of distinct chip numbers in that answer (a 5-chip answer says 5건), and the rcept_no list plus the KST stamp follow it (P8)
- [ ] 인용 블록: a quoted chip opens quote + DART link in an **overlay popover** mounted only while open (180px cap, re-tap closes; **`inert` is retired — a closed popover is not in the DOM at all**, so the check is `a[href*="dart"]` rising by exactly one on open and falling back on close); a span-less chip opens the DART link alone with no explanatory sentence; at 390 the popover is 340px (`calc(100vw - 44px)`, capped) and is slid back fully inside the viewport (P8, corrected P11)
- [ ] 컴포저: empty = ghost disabled (no fill, border-soft, ink-3, opacity 1) → typed = solid 보내기 → pending = 답변 준비 중… disabled with no bubble and no spinner → streaming = 중지 (P8)
- [ ] 도구 행: every tool row is one nowrap line that scrolls horizontally with its scrollbar hidden; no 접수번호 is split across lines at 390 (P8)
- [ ] 480 은퇴 (AI 질문): rg "480|481" over frontend/components/ask and frontend/lib/ask.ts returns **nothing at all** — the verbatim R6 §Mobile quote this line used to expect left with P9's `/ask` re-cut (P8, corrected P9)

**P9 surface blocks** (added at the P9 review; every box was re-run in the Operator Runtime —
`make stack-up`, `next dev` on `127.0.0.1:3000` **and** a production build — in real Chrome at 1440
and at a true 390 device-metrics emulation):

- [ ] 「안녕」: a greeting comes back in one or two sentences — **도구 행 0 · 칩 0 · 푸터 프레임 없음 · 거절 아님**, and the stored row's 거절 카테고리 is NULL (P9)
- [ ] 범위 밖 질문 (「주식 처음인데 뭐부터 사면 좋아요?」): one line + a 갈 곳, **no `refusal` frame and no stored family** — 범위 밖 is not a refusal (P9)
- [ ] 회사를 특정하지 않은 첫 질문: the assistant asks **which company**, with `tool_calls: 0` — it never searches an arbitrary one (P9)
- [ ] 계산 요청: the 계산 블록 appears **at call time with its inputs already drawn** (one 「입력」 marker, one 칩), then settles `pending → done` on the same `block_id` **in place** — the block's top edge does not move, and a 도구 행 arriving between the two frames does not sail it past (P9)
- [ ] 계산 블록: 검증된 계산 names the operation the server ran, the 식 line reads `{입력} × {입력} = {결과}`, the result row is `--live-tint` with a mono value + 「계산」 marker, and 근거 N건 equals the chips on screen (a calculation's **result** is never counted) (P9)
- [ ] 주입 시도: 「보안」 문장만 — 도구 행 0 · 칩 0 · 링크 0 · 푸터 0 · 점검 언급 0 · 같은 턴에 추가 프로즈 0 — and the incident appears **in the API log** as 카테고리 · session_hash · a 200자 발췌, with **no** DB row beyond an ordinary anonymous 보안 refusal (P9)
- [ ] 도구 4개 이상 + 완료: the 도구 흐름 arrives flat and **folds the instant the turn settles** to 「도구 N번 · 공시 M건 읽음」 + 자세히; ≤3 rows stay flat; the fold is never stored (P9)
- [ ] 진행 표시: exactly **one** `[role="status"]` at a time, the thread height does not change as the phase is replaced, it is gone at the first token **and at the terminal on a refusal-only turn**, and it never appears in `sessionStorage` (P9)
- [ ] 도구가 확인하지 않은 공시 수치 (「오늘 며칠이야?」): the figure renders with a 「미확인」 marker and **the sentence and the turn both survive** (P9)
- [ ] 소진 턴: dimmed prose + a folded 도구 흐름 and **nothing else** — no inset, no button, and the words 예산 / 한도 / 라운드 appear nowhere (P9)
- [ ] `/ask` 빈 상태 = 시작 화면: **질문 카드 4장** (2 columns → **two even rows with no orphan**, 1 column at ≤767, pressing one sends its sentence verbatim) · 익명 줄 0 · 새 대화 0 · 「범위:」 칩 0 · composer with the input's own 1px only (no double frame, no divider). **And the capability claim the four exist for:** pressing them one at a time yields **four distinct 도구 행** — 이벤트 검색 · **계산** (whose turn walks 검색 → 이벤트 읽기 → 계산, so `get_event` is demonstrated inside it, with exactly one 「입력」 marker beside exactly one cited chip) · 내 포트폴리오 읽기 (answered 「구성 예시」) · 운영자 연락처 (answering the **configured** contact, not 「미정」) — every answer real and **no 「미확인」 anywhere**. **The two shapes that are deliberately absent:** `security_check` (never a card) and **`save_feedback`** — the 의견 card was dropped by the operator at the P11 gate, so *pressing a start card now writes nothing*, and `conversation_feedback` must not gain a row from a start-screen sweep (count it before and after: the count is the check) (P9, corrected P11, re-cut P11.F1/F2)
- [ ] `/ask` 대화 상태: at 1440 the thread stops at **760px and is centred** with **no right column** (`main aside` = 0); at 390 the data and calc blocks reach both edges of the answer box (P9)
- [ ] 「새 대화」: exists **only when a thread does**, empties the thread **and the stored copy of it** (a reload stays empty), and builds no 대화 목록 / 이전 대화 / 기록 anywhere (P9)
- [ ] 완료 푸터: 근거 N건 · 접수번호 · KST + DART 원문 ↗ · 이벤트 상세 · 내 종목 조회 — and **no 「다시 질문」** (재시도 appears on an interrupted turn only) (P9)
- [ ] 위젯과 페이지: the same turn renders with the **same block composition** in both views (one store, no fork); the widget header is exactly two icons (↗ · ×) and a widget opened from an event detail still carries that filing's 프리셋 스트립 (P9)
- [ ] 대화 로그 저장: a calculation turn's `conversation_turn.blocks` holds the **exact frames the reader received** (inputs · 식 · 결과 · each input's 근거), one entry per `block_id` in its final state (P9)
- [ ] `prefers-reduced-motion`: **zero** animated elements beyond the signed footer fade, which collapses to a cut; the caret is the only moving thing without it (P9)
- [ ] 인용 칩 (all three places): a quoted chip opens quote + DART 원문 in an **overlay popover** (180px quote cap, 칩 재탭 closes, and so do a press outside and Esc — which returns focus to the chip; **no `inert`, because a closed popover is unmounted**); a span-less chip opens the DART link **alone** with no explanatory sentence; in a 데이터 행 / 계산 입력 the chip holds the fixed third column and the popover anchors to `.row` and opens **under the row across the block** (P9, corrected P11)

**P10 rebrand block** (added at the P10 review; every box was re-run in the Operator Runtime — the
dev stack **and** a production build, at 1280 and at a true 390 device-metrics emulation):

- [ ] **The brand mark is actually painted, not just referenced.** On every reader route (landing,
      `/ask`, `/stocks`, a 상세, `/portfolio`, `/auth/login`, **the 404**) the nav and footer each
      carry exactly one `<img src="/assets/juju2-wordmark-white-273-73c23508.png">` with
      `complete && naturalWidth > 0` at **91.000×27** and **80.883×24**, natural **273×81**,
      `transform: translateY(-8px)` / `-6px`, `alt="주주의관제탑"` — **at 1280 and at 390 alike**,
      because the mark is placed with no viewport branch. No type and no test catches a wrong asset
      path — `tsc` was clean over a 404 URL — so this is asserted in a browser or not at all.
      *(The nav offset was `-7px` until P10 round 4; the operator superseded R17's law at the round-3
      gate and asserting `-7` now fails on a correct build.)*
      *(`P4.F8` moved the chrome from the 1247×371 master to a display-size derivative named by its
      own pixel signature; the rendered width grew by 0.250 / 0.219 px because an integer raster
      cannot hold both aspect ratios, and nothing else — `x`, `y`, `height`, both `translateY`
      offsets, the `alt` and the "no viewport branch" clause — moved. Asserting the old src or the
      old numbers now fails on a correct build.)*
      (P10, corrected P10 round 2, corrected P10 round 4, corrected P4.F8)
- [ ] **Both document titles, in the real tab**: every reader page `주주의관제탑`, every `/ops` page
      (and all five sub-routes) `주주의관제탑 운영`; `/openapi.json` and `/docs` serve
      `주주의관제탑 API` (P10)
- [ ] **No reader page's `innerText` contains 미주알, 미주얼, `MIJUAL` or `Mijual`** — and the live
      agent, asked a Korean meta question, names 주주의관제탑 and rejects both retired spellings
      when handed them (the prompt spelled the product **미주얼**, which a 미주알 grep never sees).
      `/ops/대화 로그` is the one place the old spellings legitimately appear: they are **stored
      reader questions**, not product strings (P10)
- [ ] **The retired binaries stay retired**: `/assets/mijual-*.png` all **404**, and a repo grep for
      `mijual-*.png` yields only historical prose — a hit inside a code path is the regression (P10)
- [ ] **The favicon is served**: `document.querySelectorAll('link[rel*="icon"]').length === 3` on
      every reader **and** `/ops` page, in dev and in a production build — `/icon.png` 32,
      `/icon1.png` 16, `/apple-icon.png` 180 through Next's `app/` file conventions, with **no**
      hand-written `<link>`. Each tile is **transparent** (`opaque=false`) carrying a single
      `#2b8e6c` ink at **75 %** of the box on integer margins — trims `24x18+4+7` (32) and
      `134x100+23+40` (180), and **every visible pixel exactly `(43,142,108)`**. `favicon.ico` is
      deliberately absent. *(This line replaces P10 round 1's "still no favicon" guard and P10 round
      2's "opaque `#0a1310`, 84 %" wording — R18 superseded both, and asserting the retired rule
      would fail on a correct build.)* (P10 round 2, corrected P10 round 3)
- [ ] **The out-of-scope identifiers are still out of scope**: `src/mijual/` exists, every `MIJUAL_*`
      variable and `X-Mijual-CSRF` are unchanged, `pyproject.toml`'s `name = "mijual"` and
      `package.json`'s `"name": "mijual-frontend"` are untouched, and the design project is still
      "Mijual Design System". **Renaming any of these is the regression** — the rename was scoped to
      what a user can read (P10)

**P10 round 2 — R17: the mark in the chrome, the launcher, the favicon, the type** (added at the
re-review; every box was re-run in the Operator Runtime — `make stack-up`, `next dev` on
`127.0.0.1:3010` **and** `npm run build && npm run start` on the same origin — in real Chrome at
1280 and at a true 390 device-metrics emulation):

- [ ] **크롬 마크**: the 주주의관제탑 wordmark paints in nav and footer at **h27 / h24** — **the two
      heights stand**, and the bar is `height: 52px` *border-box* with a 1px rule, so the content box
      is **51px**. ~~band on the host's optical centre, nav band centre 25.60, footer +0.31px,
      clearance 5.0px~~ — **that half is retired at P10 round 4**: the placement is no longer
      referenced to the row at all, and the numbers are now box top / top clearance **4.00px** and
      band bottom **31.00**. The live check is 「로고가 옆 글자와 한 줄로 읽힌다」 in the round-4 block
      (P10, corrected P10 round 4)
- [ ] **런처**: the 32px sparkle is `mask`-painted from `/assets/juju2-symbol-white.png` at
      `mask-size: 84% auto`, one `<span class="mark"/>` and no planet/band/ring in the DOM; it
      reports **zero animations in all six states** (rest · hover 1.35× + `--live` · active 1.15× ·
      focus-visible `2px --focus-ring` offset 2 · open · reduced-motion), and **the hover colour
      survives `prefers-reduced-motion`** while the transform does not. Under reduced motion the
      **whole document** reports zero animations (P10)
- [ ] **모션 재고**: the launcher's expired exception did **not** make the product motion-free —
      `drift` / `twinkle` / `shoot` / `orbit` / the streaming caret are still there by their own
      signatures. A checklist that reads "no animation anywhere" is the wrong claim (P10)
- [ ] **푸터 코너**: 「의견 보내기」 answers `elementFromPoint` at **all four corners and its centre**,
      and a real click opens its 380px panel fully inside the viewport, at **768 · 1024 · 1120 ·
      1255 · 1256 · 1280** — computed `padding-inline-end` **108px** in 768–1255 and 24px outside it,
      clearance 16 / 16 / 16 / 83.5 / **0** / 12. The desktop 「AI 질문」 footer link is `display:none`
      at ≥768 and **present at ≤767**. *In `next dev` the 390 centre probe returns `NEXTJS-PORTAL` —
      Next's own overlay, not a defect; the production build answers at all five points* (P10)
- [ ] **서체**: every page renders Korean in the self-hosted **Noto Sans KR** subset —
      `document.fonts` holds `notoSansKr` + `plexMono`, **no Pretendard face of any kind**, exactly
      one `link[rel=preload][as=font]` on every **reader** route — *the 404 route carries **none**
      since it became request-time, and both faces still load and paint there; measured at the
      P11 third-pass review and recorded rather than asserted* —, and `CSS.getPlatformFontsForNode` shows a **live DART company
      name** (e.g. `HLB제약`) painted by the same `isCustomFont` face as the UI beside it. **0 mono
      dates or figures split across lines** at 1512 / 1440 / 1280 / 768 / 767 / 481 / 390 — the
      metric change moved no signed line break (P10)
- [ ] **제3자 origin 0건**: across five routes in both runtimes, **no request reaches
      `fonts.googleapis.com`, `fonts.gstatic.com`, or any origin but the app's own and its API**
      (P10; the standing form of this is in `security`)
- [ ] **운영 마크**: `/ops` door and bar both read 「주주의관제탑 운영」 in **one face, 9 glyphs of 9**,
      weight 600, `letter-spacing: normal` — no `--font-mono`, no 0.08em tracking. Bar mark
      **91.69 × 18.59** at 1280. *At 390 it still stacks to 11.05 × 148.75 — a known, deferred
      layout defect of the whole bar, not of the mark* (P10)

**P10 round 3 — R18: the joined wordmark, the transparent tile, the width reservation** (added at the
round-3 review; every box was re-run in the Operator Runtime — `make stack-up`, `next dev` on
`127.0.0.1:3010` **and** `npm run build && npm run start` on the same origin — in real Chrome 152 at
1280 and at a true 390 device-metrics emulation, with each check first shown capable of failing):

- [ ] **워드마크가 붙어 읽힌다**: the trim box is **1247×371**, the 「의」|「관」 ink gap is
      exactly **25 columns** (`x=519..543`), and the three ink statistics are **unchanged** by the
      splice — **78,212** non-transparent · **69,630** fully opaque · **154** distinct alpha values.
      The splice is proved harmless by *alpha equality*, not by those counts: the derivative's alpha
      channel hashes `d90e9827…`, identical to a fresh `+append` of the same two crops of the source
      trim, and the pre-R18 raster hashes `296508ff…`. Both enclosed counter islands are constant —
      `50×46+402+226` → **481**, `69×15+969+335` → **15**. **Never** replace this with an "opaque
      near-white = 0" count on the white derivative: it returns 69,630 and can never fail (P10 round 3)
- [ ] ~~**세로 기하는 움직이지 않았다**~~ — **falsified at P10 round 4** and replaced by the
      「로고가 옆 글자와 한 줄로 읽힌다」 line in the round-4 block below. It asserted
      `INK_OFFSET_PX = {27: 7, 24: 6}`, `translateY(-7px)` and the h27 band centre at **25.60**;
      the operator superseded that law at the round-3 gate, so asserting it now **fails on a correct
      build**. Do not restore it (P10 round 3, retired P10 round 4)
- [ ] **파비콘 타일은 투명하고 잉크는 한 색**: `opaque=false` on all three, ink trims `24x18+4+7` and
      `134x100+23+40`, and **0** non-transparent pixels that are not `(43,142,108)` in any tile. The
      served bytes hash equal to the files on disk in both runtimes. **The launcher keeps
      `mask-size: 84% auto`** — the divergence is deliberate and "making them consistent" is the
      regression (P10 round 3)
- [ ] **활성 탭이 형제를 밀지 않는다**: `[...document.querySelectorAll('header nav a')].map(a =>
      a.getBoundingClientRect().left)` is identical **to the decimal** on all five nav routes
      (`[218.75, 279.484375, …]`), and all six `/ops` routes report one array
      (`[139.6875, 180.53125, 274.84375, 360.828125, 430.296875, 483.5625]`). The check has teeth:
      neutralising the `::after` twin at runtime puts `/portfolio` back to `278.78125` and `/ops`
      back to `…360.515625`. The active link is still 600 with a white 2px underline and the hit box
      is still the full 51px bar height (P10 round 3)
- [ ] **스크린리더가 라벨을 한 번만 읽는다**: dump the AX tree over both surfaces — each nav link and
      each `/ops` tab has **one** `StaticText` child. Re-run it with the twin switched to
      `opacity: 0` and every name doubles (`AI 질문 AI 질문`, all six tabs likewise); that control is
      the check. `visibility: hidden` is load-bearing (P10 round 3)
- [ ] **390의 `/ops` 탭 줄은 그대로다**: strip **154.531** wide, right edge **213.578**, every tab
      12.422 — identical with and without the twin, because the reservation is inert where the cell
      cannot reach max-content. Injecting `white-space: nowrap` widens it to 380.828 and pushes the
      last tab to `right: 439.875`; that is why `.tab` deliberately has no `nowrap` (P10 round 3)
- [ ] **모바일 시트와 랜딩 보드는 규칙 밖**: `.sheetRow::after` content computes to `none` and the rows
      carry no `data-label`; the landing board's tab strip still shifts **0px at 1280** and **0.42px
      on `CB` at 390** — an open operator decision, not a regression (P10 round 3)

**P10 round 4 — `P10.F3`: the mark on the neighbouring type's baseline** (added at the round-4 review;
every box re-run in the Operator Runtime — `make stack-up`, `next dev` on `127.0.0.1:3010` **and** a
production build of the same tree — in real Chrome 152 at 1280 and at a true 390 device-metrics
emulation, each check first shown capable of reporting failure):

- [ ] **로고가 옆 글자와 한 줄로 읽힌다**: on every reader route at **1280**, the wordmark's
      glyph-band ink bottom is within **0.5px** of the neighbouring Hangul's ink bottom — the nav
      `.link` labels (`AI 질문`, `보유 종목`, both weights) and the footer `.source` — read out of the
      live document **and** out of an 8× pixel scan of **band-only columns** (the band is PNG columns
      0–1086, the sparkle 1025–1246, so scan left of x≈1000/1247 of the rendered width or the sparkle
      pollutes the top edge). Measured: band bottom **31.000**, labels **30.875–31.125**
      (|Δ| ≤ 0.125), footer Δ **0.00–0.28**, box top / top clearance **4.00px**. **The teeth:**
      re-paint the mark at R17's `translateY(-7px)` and it must report **FAIL on every nav and footer
      surface, worst 1.125px**, in dev *and* production. At **390 the line is N/A by construction** —
      the nav labels are `display: none` and the footer `.identity` stacks, so nothing shares the
      mark's row; the **메뉴** button is **reported (Δ +0.083 – +0.125, was +1.125), never judged**,
      because the document and pixel methods disagree there by ~0.5px (P10 round 4)
- [ ] **로그인 is 0.75px below the links, and that is known, not new**: `.utility`'s Hangul ink bottom
      is **31.75** against the links' **30.875–31.125** — `.utility` is centred in the full 51px box
      while `.link` stretches with a 2px transparent bottom border (a 49px cell). Pre-existing since
      R2/R8. A checker that "fixes" the mark to split the difference has re-broken the operator's own
      reference; the open decision is whether `.utility` moves (P10 round 4)
- [ ] **A client-rect count is not a line break.** The P8 「mono: no date or figure splits across
      lines」 box must not be implemented as `getClientRects().length > 1`: on a **correct** build that
      reports **9** at every width from 1512 to 390, and every one is a numeral and its Korean unit at
      the *same* `top`. Compare the rects' `top` values (or measure the element's line count) —
      otherwise the guard fails on a good build, which is this phase's defining defect wearing the
      opposite mask (P10 round 4)


**P11 block — the ask surface's inline citations, the four live-corpus cards and the published
operator contact** (added at the P11 review, re-cut at the re-review, and **re-cut and re-measured a
third time at the third-pass review after `P11.F3`**; every box re-run in the Operator Runtime —
`make stack-up`, `next dev` on `127.0.0.1:3010` **and** `npm run build && npm run start` on the same
origin — at 1440/1280 and at a true 390 device-metrics emulation.

***The instrument changed at the third pass, and this is the durable note about it.* Aside — the
workspace's preferred instrument — is now installed on this machine and signed in** (CLI at
`~/.local/bin/aside`, `/Applications/Aside.app`, daemon 1.26.831.1513; the six earlier P11 slices each
recorded it absent, and that record is now stale). Launch the app first (`open -a Aside`) or the CLI
answers 「daemon is not reachable」. Both surfaces work from a dispatched session: **`aside repl`** for
deterministic inspection (a Playwright-shaped `page` — `goto` / `evaluate` / `mouse` / `keyboard` /
`console.logs()`, with the console hook installed before load) and **`aside exec`** for an agentic
walk. **One limit, and it decides the split:** Aside drives a real browser window and exposes no
viewport control — `Emulation.*` is not in its CDP proxy and popups are blocked — so **every ≤767
measurement still goes through the documented fallback**, real Chrome 152 over CDP with
`Emulation.setDeviceMetricsOverride`, which is exactly what the runtime manifest names for mobile.
Desktop boxes: Aside. Mobile boxes: Chrome device metrics. Say which one produced a number.):

- [ ] **한 문장이 근거 2건 이상을 지고도 한 줄로 읽힌다**: press the first start card and the answer's
      sentence carries **all of its chips side by side after its period** — same `y` to the decimal,
      **17px apart**, and the paragraph carries **0 `<br>`**. Re-measured at the re-review on a
      **five**-근거 sentence: 1280 `[553.8, 570.8, 587.8, 604.8, 621.8] @ y 249` with the following
      sentence continuing on the same line (`.prose` 21px at 20.925px leading), 390
      `[309.8, 326.8, 343.8] @ y 261` + `[32, 49] @ y 282` — a **wrap** between chips is inline
      behaviour and is fine; a **break after every chip** is the defect. Identical in dev and
      production, on `/ask` **and** in the widget. **The teeth:** this is the defect the phase existed
      to close (`…입니다.[1] ⏎ [2] ⏎ [3]`) — a paragraph a line taller per chip, or
      `.sentence + .sentence`'s computed `margin-left` back at `0px` instead of `3.375px`, is the
      regression returning. *Re-measured a third time (third-pass review, two fix slices later, on
      fresh live turns): dev 1440 five chips `[662.4 … 730.4] @ y 249` with the **next** sentence's
      chips also on `y 249`, `.prose` 42px / 2 lines, 0 `<br>`; production 1280 `[541.4 … 609.4]
      @ y 248.5` on a **single** 21px line; production 390 one wrap between chips; widget (dev,
      landing) chips 1–4 on `y 483.9`, 0 `<br>`.* (P11, re-measured P11 re-review, re-measured again
      at the third pass)
- [ ] **칩을 열어도 아무것도 움직이지 않는다**: a document-coordinate snapshot (`.prose`, every
      `.sentence`, `.row`, `.rowLabel`, `.rowValue`, `.answer`, `.data`, `.calc`, every chip) is
      **byte-identical before and after the click** in all three placements, the data row's grid
      tracks stay `283.188px 391.812px 17px` (**the value column never collapses**), and in the widget
      the thread's `scrollHeight` is **unchanged** (509 → 509) so the composer is not pushed. One
      popover at a time; 칩 재탭, a press outside and **Esc (focus back on the chip)** all close it, and
      `a[href*="dart"]` rises by exactly one on open and falls back on close.
      **Two ways to measure this wrong, both hit at the third-pass review and both worth knowing:**
      a synthetic `element.click()` fires **no `pointerdown`**, so the document-level outside-press
      listener never runs and two popovers appear to be open at once — 「one at a time」 must be pressed
      with a **real pointer** (a mouse click at the chip's centre), and it then reports 1, with the
      first chip's `aria-expanded` back to `false`; and the popover mounts on a React state update, so
      reading it in the *same* evaluate as the click returns `null`. Both are instrument artifacts,
      not product defects (P11, sharpened at the third pass)
- [ ] **팝오버의 자리와 바탕**: 프로즈 → 380px under the chip (340px at ≤767, slid back fully inside the
      viewport — measured `translateX(24px)` at 390); 데이터 행 값 / 계산 입력 → anchored to `.row`,
      **block-wide** (732px at 1280), flush under the row, 180px quote cap; inside the widget it stays
      **inside the thread and inside the widget** (clamped by `nearestClip`, flipping up when the
      thread would cut it). Ground is the product's overlay ground `rgb(14, 26, 21)` +
      `border-left: 2px rgb(95, 208, 165)` + `z-index: 40` — **opaque is deliberate** (R16 signed
      `--surface-inset` for an in-flow panel); asserting the translucent token now fails on a correct
      build. *Third pass, re-measured on live turns: 데이터 행 `[354, 355, 732 × 76]` under a row at
      `[354, 330.5, 732 × 35.6]`, quote cap 180px; 계산 입력 `[354, 473.6, 732 × 47]`; 프로즈
      `[676.3, 590.5, 380 × 47]` in dev and `[538.4, 270.9, 380 × 46.9]` in production; 390 `340px`,
      `translateX(24px)`, fully inside the viewport; in the widget the popover sits entirely inside
      the thread's `[977, 302, 438 × 509]` and that thread's `scrollHeight` does not move.*
      **A known annoyance, reported not fixed:** an overlay by construction covers what is under it,
      so a popover opened on a chip in one line sits over the chips on the next — surfaced to the
      operator at the third-pass gate rather than restyled (P11)
- [ ] **시작 카드는 넷이고, 두 장의 회사는 오늘 정해진다**: `/ask` renders **four** cards in **two even
      rows** (316×63.2 / 316×56 at 1280, one 358px column at 390, nothing clipped, no horizontal
      overflow), and the two 공시 cards name **whatever the corpus offered when the page loaded** —
      never a fixed pair. **The teeth are in the production build:** `next build`'s route table must
      print **`ƒ /ask`** (`○ Static` is the stale-card defect returning), and with the upstream
      answering different companies between requests, **three consecutive requests to one running
      production server render three different card sets** (verified at the re-review with a toggling
      stub upstream). Never assert today's two company names — they are data. **And do not read the
      card text as proof that the server picked them:** `P11.F1` seeded `copy.ts`'s static fallback
      with the companies the corpus offered that day, so the served set and the fallback set can be
      the *same two strings* — as they were at the third-pass review (빛과전자 · 아이에이). The check
      with teeth is the **request**: three page loads must produce three `GET /ask/start-cards` lines
      in `var/stack/api.log` (measured 3/3), i.e. nothing is cached (P11.F1)
- [ ] **API가 죽어도 시작 화면은 넉 장이다**: stop the API and reload `/ask` — **200, four cards, two
      rows, no spinner and no hole** (measured 25ms in dev, **18ms in a production build** at the
      third pass), because each card falls back **on its
      own** to `copy.ts`'s static set. A slow upstream must lose to the **2.5s** timeout rather than
      hold the page. *Known and out of scope: with the API down the **landing** `/` returns 500 —
      `app/page.tsx` awaits its board reads with no catch, unlike `/stocks`. Pre-existing, tracked
      separately; `/ask` is the surface this box is about* (P11.F1)
- [ ] **운영자 연락처는 두 곳에 있고, 한 곳에서 온다**: the 연락처 card's answer reads the **configured**
      email and phone (no 「연락처 미설정」 anywhere), and the same two values close the footer's
      identity row — 이메일 in the UI face 12px, 전화 in **mono** 11px, `mailto:`/`tel:` links, 44px
      tall at ≤480 — on **every reader page** (`/`, `/ask`, `/stocks`, a 상세, `/portfolio`) in dev
      **and** production. `/ops` renders **no** footer. With the API unreachable or the value unset,
      the footer shows **no contact line at all** — never an empty label, never 「미정」 (that is the
      agent's voice) — verified in a production build against an upstream answering nulls.
      **The 「unreachable」 half is about a *cold* cache**: the layout's read is `revalidate: 600`, so
      with a warm ISR entry the footer keeps printing the last-known values while the API is down
      (measured at the third pass — API stopped, footer unchanged). That is the cache doing its job,
      not a failed check (P11.F2, qualified at the third pass)
- [ ] **≤767 칩 타깃은 14 × 16 px, 44px가 아니다** — R16 §2.6's prose lists 44px under 「변경 없음」 and
      the round's own CSS never implemented it either. **Recorded, not asserted as a pass:** it is an
      open operator decision (closing it either draws a 44px box around a 10px number or lets each
      chip's hit area swallow its 3px-away neighbour). Measure it; do not "fix" it silently (P11)
- [ ] **푸터의 전화번호는 600–620px 구간에서 두 줄로 끊긴다** — 「010-」 / 「3772-9916」, measured at the
      re-review. **None of the P8 mono row's widths (1512 / 1440 / 1280 / 768 / 767 / 481 / 390) hit
      it**, so that box still passes as written; this line exists so the band is not rediscovered as
      new. Reported to the operator at the gate, **not** silently fixed — a `white-space: nowrap` on a
      mono phone is a typographic decision on a surface R8 signed (P11 re-review)
- [ ] **프로덕션에서 모르는 주소를 열면 내가 친 주소가 그대로 보인다** — and no React #418. In a
      **production build** (never `next dev`, which cannot show this fault), open several unknown
      URLs and read the mono echo: it must be **the reader's own path on the first paint**, never
      Next's internal `/_not-found`. Measured at the third-pass review straight off the wire on
      **8** distinct shapes — `/nope-404`, a Korean path, `/a/b/c/d`, `/portfolio/nope`, `/ask/nope`,
      `/ops/nope`, `/nope-404/some/deep/path`, and a bad `/events/{rcept}` — each answering 404 with
      its own path in the SSR HTML, plus **56 production loads** over seven routes at 390 and 1280
      with Chrome's pre-hydration attribute injected, **0** hydration messages. **The teeth:** the
      check is worthless unless the detector is first shown able to fire — plant a text mismatch in
      that same element before hydration and production must throw **#418 `args[]=text`** (4/4).
      *Two shapes are knowingly different and are not this box: a `notFound()` from a **dynamic**
      segment still draws client-only with an empty first paint (**D35**), and the echo is the
      **percent-encoded** pathname, so a Korean URL reads `/%EC%96%B4…`* (P11.F3, third-pass review)
- [ ] **`<html>`의 `suppressHydrationWarning`은 딱 그 한 요소만 가린다**: with the flag in place,
      injecting `__gchrome_remoteframetoken` on `<html>` before hydration is **silent** (2/2 routes)
      while the same injection on **`<body>`** still fires the attribute-mismatch warning (2/2), and a
      planted deep text mismatch still throws #418 in production. Both controls were re-run
      independently at the third-pass review. **Never widen the flag** — a suppression that hides more
      than it claims is how the real fault above stayed hidden — and never report 「no hydration
      messages」 without one of these controls in the same run (P11.F3, third-pass review)

**P4 production block** (added at the P4 review; every box was re-run there in the Operator Runtime —
`next dev` on :3022, a standalone **production build** on :3014 and **production**
`https://jujutower.com` — in real headful Chrome 152 over CDP at 1280 and at a true 390 device-metrics
emulation. A `curl` cannot see the lines marked **실브라우저**):

- [ ] 프로덕션 스모크: `make smoke-prod` is **17/17, exit 0** against the live origin — health, landing
      HSTS+CSP+cf-ray, www and http 301s, board, one 종목 and one 이벤트 page, bad rcept_no 404,
      start-cards, the `/ops` door, robots/sitemap/manifest/OG/noindex, the third-party check, and the
      three co-tenant sites at 200. A red `www` line from this Mac is its own MagicDNS resolution, not
      production — re-check with `--resolve www.jujutower.com:443:104.21.21.26` before believing it
      (D43) (P4)
- [ ] 제3자 origin (프로덕션, **실브라우저**): opening `/`, `/stocks`, `/ask`, a 종목, an 이벤트 and
      `/portfolio?sample=1` in a real browser reaches **no host but the origin, `dart.fss.or.kr` (on a
      click only) and `static.cloudflareinsights.com`** — the operator-enabled Cloudflare Web Analytics
      beacon, injected at the edge, cookieless, reporting to the same-origin `POST /cdn-cgi/rum`. In
      **dev and in a local production build the beacon is absent and the count is 0**. Any *other*
      off-origin host is a failure, and `make smoke-prod`'s `third-party` check now fetches with
      `Accept: text/html` (as a browser does) so it can see an edge injection at all (P4, P4.F2)
- [ ] `/ask` 스트리밍 (프로덕션): one turn through Cloudflare renders **≥4 distinct DOM states over
      several seconds** at 1280 and 390 — never one late blob — with exactly one `[role=status]` while
      it runs and none at the terminal (P4)
- [ ] 실데이터 표면: the board, one 종목 and one 이벤트 page render from the live corpus at 1280 and 390,
      and the landing's 기준 시각 is younger than `stale_after_hours` (18) after beat's 07:30/19:30 KST
      runs — `/api/board/summary` → `freshness.stale: false` (P4)
- [ ] `/ops` 도어와 개요: the door is exactly 마크 + 운영자 ID + 비밀번호 + 로그인 with `noindex, nofollow`,
      two inputs, **no footer** and none of D15's four rule lines; logged in, the 개요 lists **four**
      beat entries including `notify-deadlines 08:30`. *The logged-in half is an **operator** check —
      an agent `/ops` login mints an `OpsSession` row on production* (P4)
- [ ] 푸터 연락처: 운영자 `mailto:` and `tel:` links resolve on every reader page at both viewports
      (exactly one of each); `/ops` renders no footer (P4)
- [ ] 리다이렉트: `http://jujutower.com/` and `https://www.jujutower.com/x?y=1` both 301 to the apex with
      path and query preserved (P4)
- [ ] SEO 표면: `/robots.txt` serves Cloudflare's managed content-signals block **then** the origin's
      rules and `Sitemap:`; `/sitemap.xml` is apex-only with no `/ops`, `/auth`, `/portfolio`;
      `/manifest.webmanifest` (five icons, all 200) and `/opengraph-image.png` (**1200×630**) answer 200
      (P4)
- [ ] 인덱싱 규칙: the five indexable routes (`/`, `/stocks`, `/ask`, `/stocks/{corp}`,
      `/events/{rcept}`) each carry a title, a description, a **self-canonical** and an `og:image`;
      `/ops`, `/auth/login`, `/auth/reset`, `/portfolio`, `/portfolio/notifications` carry
      `noindex, nofollow` and **no** canonical (P4)
- [ ] 나쁜 접수번호: `/events/<nonexistent>` answers **404, not 500**, in the production build and on
      production (P4)
- [ ] 샘플 포트폴리오 (프로덕션): four **distinct** issuers with at least one upcoming ① carrying a live
      D-day, an ②, an ① 소멸 with its 놓친 돈, and an ③; a 보유량 edit, a 삭제 and a 챙겼습니다 all
      survive a reload and the store is `{"v":2,"shares":…,"removed":…,"claims":…}`. **Never assert the
      company names** — they are picked per request and move daily (P4, P4.F1)
- [ ] D-day 메일 데모: `once --stages notify --no-lock --label gate-demo --notify-today YYYYMMDD` sends
      one mail to an account holding a stock at that lead day, and an identical second run reports
      `already-sent`. The beat entry itself is live-proved by the box's own 08:30 run
      (`1 account(s), N candidate(s) -> sent …`) (P4)
- [ ] 추출 상한 (프로덕션): `MIJUAL_EXTRACT_MAX_CALLS` is **300** in worker, api and beat
      (`docker inspect … Config.Env`, or `printenv` inside the container), and every scheduled run's
      `config` line reads `extract<=300 calls`. Unset anywhere else it is **60** — the dataclass default
      is unchanged, and `once --max-calls N` still wins for a single run (P4.F4)
- [ ] 배포 무해성 (after any deploy): `edge-nginx` `StartedAt` unchanged at
      `2026-07-02T19:22:12.325478595Z`, `edge-nginx` still owns `:80`/`:443`, **28** running containers
      (22 co-tenants + 6 Mijual), `changple_shared_network` **17** members. A **frontend-only** release
      recreates exactly one container (`mijual-web`) and its `:previous` is then the only usable
      rollback half; an `.env.prod` **edit** additionally recreates every `env_file` service, postgres
      included (P4, P4.F4, P4.S9)
- [ ] 백업: `deploy/backups/` holds a dump **younger than 24 h**, mode 600 inside a 700 directory, and
      `var/backup.log`'s last entry verifies 19 tables with `KEEP=14`. The cron line is `0 4 * * *` and
      the box's clock is **GMT**, so it fires at **13:00 KST** (P4, P4.F3)
- [ ] 폰트 대체 (프로덕션, **실브라우저**): the served CSS declares **three** `notoSansKr Fallback`
      faces — `… Apple` (`size-adjust: 106.36%`), `… Noto` and `… Malgun` (`100%`) — and the **only**
      `local(Arial)` in any served stylesheet belongs to `plexMono Fallback`. With the webfont blocked
      the page lays out within **1 px** of the loaded state (P4.F5)
- [ ] 콜드 캐시 CLS (프로덕션, **실브라우저**): on `https://jujutower.com` through Cloudflare, in a real
      browser at 412×915 @ 2.625 with 4× CPU and ≈1.6 Mbps / 150 ms, cache cleared per load, the
      cold-load CLS median of 3 is **≤ 0.01** on `/`, `/stocks`, `/ask` and a live `/events/{rcept_no}`
      (measured **0.0000 / 0.0003 / 0.0003 / 0.0000** at release `4aa8ddd`, against pre-batch
      0.0951 / 0.1378 / 0.0893 / 0.0327). **Known and accepted:** because a metric-matched fallback
      matches average advance and not every line break, an occasional cold load on `/ask` or
      `/portfolio?sample=1` re-wraps one line when the font swaps and measures **0.018–0.038** (18 of
      24 loads measured 0.0000 at `4aa8ddd`). Treat **> 0.1 on any route** as the regression, and
      attribute any shift by blocking `*NotoSansKR*` — 0.000 with the font blocked means it is the swap
      (P4.S9, P4.REVIEW)
- [ ] 랜딩 페이로드: the landing document's `grep -c window_state` is **0** and the document is ≈290 KB
      (289,590 B at `4aa8ddd`, from 354,671 B) — the landing serialises a **projection** of `/board`,
      while the 60 s refresh still fetches the unnarrowed board (P4.F6)
- [ ] 자산 캐시 수명 (프로덕션): `/assets/juju2-wordmark-white-273-73c23508.png` →
      `public, max-age=31536000, immutable` (**6,405 B**), `/foundations/tokens.css` and the fixed
      `/assets/*` names → `public, max-age=604800, stale-while-revalidate=86400`, `/_next/static/*`
      still a year. The `immutable` name carries its own pixel signature: **changing those pixels means
      changing that name**, in `README.md`, `chrome/copy.ts` and `next.config.ts` together (P4.F8)
- [ ] 이벤트 알림 줄은 서버 HTML에 있다: on `/events/{rcept_no}` with a deadline still ahead,
      `curl -s | grep -c '이 마감 알림 받기'` is **1** (and 「보유 종목에 담기 →」 instead, exactly once,
      for a request carrying a session cookie), and **0** on a past or 추후결정 event. The sharper form
      is a browser run with `*/auth/me*` blocked outright: the correct line is still there at first
      paint (P4.F10)
- [ ] 자동 갱신 (프로덕션): leaving the landing open for two 60 s intervals makes exactly **two**
      `/api/board` requests, shows no spinner, keeps the row count, the tab, the expanded strips and the
      scroll position, and raises 갱신됨 + a `--live` edge only if the corpus actually moved. **The
      refresh is visibility-gated, so an automated run measures 0 requests unless the tab really is
      visible** — a driven browser whose window is not frontmost reports
      `document.visibilityState === "hidden"` and correctly makes **no** request; force it with
      `Page.setWebLifecycleState(active)` + `Emulation.setFocusEmulationEnabled` (or by foregrounding
      the window) and check `document.visibilityState` **before** trusting a zero (P4, P4.REVIEW)
- [ ] 랜딩 유휴 비용 (프로덕션, **실브라우저**): a `blink.animations` trace of `/` over an 8 s idle
      window shows **0 `compositeFailed`** and **0 `animationiteration`** at 1280 and at 390 + 4× CPU
      — and **both halves need a firing control in the same run**, or they are worth nothing: trace
      **across the load** (the `Animation` events are emitted when an animation is created, so an
      idle-only window sees none at all and reports a false 0), and check that a build carrying
      `offset-distance` reports **1** (`unsupportedProperties: ["offset-distance"]`); restore the CSS
      twinkle client-side (cancel the WAAPI animations, drop `data-twinkle`, add one document-level
      `animationiteration` listener) and check that the dispatches come back (**~265 per 8 s**).
      **The third number is a ratio, not a count:** `UpdateLayoutTree` per 8 s must be **well under
      the display's own refresh rate × 8**. The pre-batch failure mode was *one recalc per display
      frame* — 480 per 8 s at 60 Hz, **960 at 120 Hz** — and after the batch it is a small fraction
      of it: **8–14 measured on a 60 Hz session, 122–159 on a 120 Hz one, the same −84 %** (the
      residual is an `IntersectionObserver` computation on each rendering opportunity the main thread
      services). Read a **paired** before/after in one session, never an absolute against another
      machine's number, and check the Cosmos-free control: `/stocks` must measure **0** recalcs and
      **0** `UpdateLayoutTree` (P4.F11, P4.S10, re-measured P4.REVIEW)
- [ ] 히어로 궤도는 데스크톱에만 있다 (프로덕션, **실브라우저**): at **1280** the hero renders both
      ellipse rings **and** the orbiting star; the served CSS carries **no `offset-distance` and no
      `offset-path`**, `@keyframes …orbit` is **93 generated `translate` stops**, and one lap measures
      **26 s** (sample the orbiter every 0.2 s — it returns within ~0.1 px of its start at 26.0 s).
      At **≤767** `.orbits` is `display: none` — **no star and no rings** — while the hero's own
      geometry (h1 position, search form, stat line, `scrollHeight`) is unchanged; that removal is the
      **operator's** decision of 2026-09-03, not a defect. The starfield twinkles from the
      **server-rendered first paint** (block every `_next/static/chunks/*.js`: 240 stars still run 240
      CSS `twinkle` animations) and is handed to WAAPI after hydration (`data-twinkle="waapi"`, 240
      WAAPI / 0 CSS twinkle, phases spread across all ten deciles rather than restarted in lock-step),
      and **only rendered stars are handed over**. Under `prefers-reduced-motion: reduce` the document
      reports **0 animations** document-wide, against 247 without it (P4.F11, P4.S10)

**P12 flicker-polish block** (added at the P12 review; every box was re-run there in the Operator
Runtime — the dev stack on `127.0.0.1:3010`, a standalone **production build** on `127.0.0.1:3014`
and **production** `https://jujutower.com` at release `004d936` — in **Aside on the agent account
`u2`** (profile 「claude2」, `aside repl --account u2 "<js>"` over Bash; never `u0`) at **1280** and a
true **390** device-metrics emulation, plus **412×915 @ DPR 2.625 / 4× CPU / ≈1.6 Mbps / 150 ms**
for the cold-cache lines. Signed-in boxes ran on dev with a throwaway account created and deleted
through the product; production stayed read-only:

- [ ] 계정 캐럿: signed in, the account frame is **one rect in both states** across click / Escape
      cycles — the caret is a single `▾` flipped by `transform: scaleY(-1)` about
      `transform-origin: 50% 66.7%` (measured live: a 5.672 × 12 px caret box, computed origin
      `2.83594px 8.004px`), so no glyph swap can change the box. The frame's *width* is the email's,
      clamped by `max-width: 280px` — assert **one distinct rect across the toggle**, never a
      particular width (`P12.S1` measured 261.28 px for its own shorter throwaway address; a longer
      one clamps at 280). `transition-duration` on the frame stays 0s for the caret (P12.S1)
- [ ] 크롬은 첫 페인트 안에 있다: on all **10** public routes at 1280, warm, the 로그인 link (or the
      signed-in account frame) and the AI 질문 launcher enter the DOM **before** FCP — re-measured on
      production at **−13 to −102 ms**, CLS **0** on 10/10 with the Cosmos filter never needed, slot
      rect `[1138.73, 15.03, 37.27, 20.92]`, launcher `[1188, viewportH−74, 68, 50]`. `/ask` has no
      launcher by design. Signed in (dev + the production build) the frame lands **44–64 ms before
      FCP** and the served HTML carries the reader's own email while the 로그인 link is absent
      (P12.F1, P12.F2)
- [ ] 사전 하이드레이션 미러의 네 가지 쓰임이 0px다: with the browser's own storage seeded, each of
      `data-mj-offer-seen` (the 전환 제안 band), `data-mj-carry-rows` / `data-mj-carry-kind` (the
      계정 이전 · 세션 이월 band), `data-mj-lookup-holding` + the server's `data-mj-cells` /
      `data-mj-foot` (조회's ① 환산 row) and `data-mj-auth-flash` (the 로그아웃되었습니다 line, held at
      a measured **40.594 px**) fills or hides **inside a box reserved before first paint**:
      **0 elements moved between the first sampled frame and the settled page, CLS 0, and no
      `layout-shift` entry at all**. The head script is in `<head>` on every route. **The teeth:**
      seed the storage in the **product's own shape** (`mijual.lookup.holdings` is
      `{v:1,entries:{…}}`, not a bare map) and check the *filled* state actually rendered — a seed
      the product rejects reads as a perfect zero (P12.F3, P12.F4, P12.F5)
- [ ] 편집된 샘플의 삭제된 행은 페인트되지 않는다: with `mijual.portfolio.sample` carrying a removed
      code, the row for that code never appears in any sampled frame and the page's height is its
      settled height from the first frame (**CLS 0**); `SampleRules.tsx` emits one
      `html[data-mj-sample-removed~="c"] [data-corp="c"]{display:none}` rule per **served** code
      (32 of them on production today) plus the per-section and first-visible-row rules (P12.F10)
- [ ] 정정 이력 버튼은 한 폭이다: on `/events/{rcept_no}` the 정정 이력 ↔ 접기 × toggle keeps
      **one distinct rect `[125, 1178.94, 77.53, 36]`** at 1280 over four toggles (the
      `Nav.module.css` ghost twin, now used twice in the product); at ≤767 `width: 100%` already made
      it immune. **The precondition is the check:** the twin is resting-identical only where the
      **resting** label is the widest state (P12.F6)
- [ ] 의견 보내기 다이얼로그는 한 높이다: from the press of 보내기 (or 다시 시도) onward the dialog is
      **one rect** across editing → sending → sent, and → failed → 다시 시도 —
      `[796, 526, 380, 318.016]` at 1280 and the ≤480 sheet `[0, 498.984, 390, 345.016]`, actions row
      at y 791 / 780 in **every** state. The **editing** body carries no inline style; every later
      body carries `min-height: <the measured editing height>` (263.016 px at 1280, 291.016 at 390),
      so a long failed message may still grow past it. 닫기 is absent while sending, as signed. A real
      send forwards to **vocky**, never a Mijual table — run the send half on **dev**, never on
      production. 보내기 71.27 → 보내는 중입니다 124.73 → 다시 시도 87.47 px is Q9, unchanged (P12.F7)
- [ ] 검색 불일치 상자는 문장보다 오래 산다: on `/stocks?q=<miss>` one real keystroke leaves the
      sentence's rect **one distinct value** and the page **0 elements moved with no `layout-shift`
      entry**; the `<p>` takes `visibility: hidden`, so it leaves the AX tree and hit-testing exactly
      as the old unmount did (P12.F8)
- [ ] 콜드 캐시 mono 교체가 아무것도 움직이지 않는다: at 412×915 / DPR 2.625 / 4× CPU / ≈1.6 Mbps with
      the cache cleared, the worst per-element mono width delta **across the whole load** is
      **≤ 0.02 px** (`/stocks/00547510` 0.015, `/portfolio` 0.016), the delta **across the Plex
      `responseEnd` boundary is 0**, and there is **no `layout-shift` entry near either Plex file**.
      **The standing control:** block `*IBMPlexMono*` outright and the page lays out within
      **0.08 px** of the loaded state (29 and 33 mono elements on `/stocks/{corp}` and
      `/events/{rcept}`, worst 0.047 / 0.078 px) — with `document.fonts` reporting `plexMono: error`,
      which is what proves the block fired. The served CSS declares **three** `plexMono Fallback`
      families — `… Apple` (Menlo, `size-adjust: 99.66%` / `ascent-override: 102.85%` /
      `descent-override: 27.59%`), `… Windows` (Consolas, vertical-only at 100%) and `… Arial`, the
      first two `unicode-range`-limited to the subsets' 211 codepoints — and `local(Arial)` /
      `131.49%` appear **exactly once each**, in that third family *behind* the matched ones, so the
      `←` / `→` arrows do not change at rest. The generated bare `font-family:plexMono Fallback` face
      is **gone** (P12.F9)

**Instrument notes from P12** (the same shape as the P4 block's; each one produces a false result):

- **A rect key over occurrence indexes renames siblings when a node is *prepended*.** P12.F4's ①
      환산 row inserts two cells **before** the two already drawn, so `cell[1]` / `cell[2]` appear to
      travel 217 / 434 px while the real elements do not move at all. Key such a row by the cell's own
      **label**, and it reads as it is: the two surviving cells stay at x 423 and 857, the two new
      ones fill the empty reserved columns (P12.REVIEW).
- **The hydration detector must be shown able to fire, and *where* it fires differs by runtime.** A
      planted deep text mismatch throws **`Minified React error #418, args[]=text`** in a production
      build (4/4 routes) and 「Hydration failed because the server rendered text didn't match」 in
      `next dev`. The **attribute**-mismatch control (`__gchrome_remoteframetoken` injected on
      **`<body>`** before hydration) fires **only in `next dev`** — the minified production runtime
      does not emit that dev-only warning at all — while the same injection on **`<html>`** is silent
      in both, which is `suppressHydrationWarning` scoped to exactly that element. Install the
      injection from a `MutationObserver` on `document` inside
      `Page.addScriptToEvaluateOnNewDocument`; a `readystatechange` listener lands too late and
      **both controls then read as silent** (P12.REVIEW).
- **A synthetic `element.click()` does not open the feedback dialog or a nav-sheet control** — press
      the real coordinates with `Input.dispatchMouseEvent`, after `window.scrollTo` (an off-screen
      `scrollIntoView` in the same evaluate returns a stale rect). At 390 in **`next dev`** the
      footer's 의견 보내기 centre is covered by `NEXTJS-PORTAL` (the P10 note) — run the ≤480 sheet's
      state machine on the **production build**, where it answers (P12.REVIEW).

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
| **the citation gate's number check is membership, not semantics** | a small integer or a year is effectively always allowed, because it appears *somewhere* in a payload. What it reliably catches is a value present **nowhere** upstream — which is the shape of every invented figure. Since P9 that catch is expressed as a visible 「미확인」 mark rather than a silent deletion, so the failure mode moved from *invisible* to *hedged* | `backend` / `architecture` |
| **the 데이터 블록 has almost nothing to draw** | measured across the whole 386-event board corpus: **372 events → 0 rows**, **14 → exactly 1 row** (always 신주인수권증서 상장·매매기간), longest value 23 characters. Every gate-passing field's value is a composite dict the server may not spell as a row without inventing a format the detail page owns. So the block's 6-row fold and value-cell scroll have **no producer in the product** — both were verified at element level only | `frontend` / open operator question |
| **the calculation `error` block is unreachable in practice** | the model states the 미공시 fact and refuses with 「확정 전」 *before* it calls `calculate` — twice, including on an explicit 「계산 도구로 계산해 주세요」. Arguably the better product answer, but the signed error element is drawn by nothing and its guidance sentence never reaches a reader | `frontend` / open operator question |
| **the implicit prompt cache is never credited** | `cached 0` on every live turn of two independent passes (16 + 12), including the same question minutes apart, against a ~5.5k-token static prefix that should clear Gemini's 4,096-token floor. The ledger is telling the truth; why the prefix is not credited is unknown | `architecture` / open operator question |
| **the streaming path has no heartbeat** | longest observed inter-frame gap with the live agent is **6.0 s**; an idle timeout below ~10 s cuts legitimate turns, and the deployed topology (edge / CDN / nginx) is unmeasured. **P9 widened the exposure**: at 20 rounds a researching turn is minutes long, and the 진행 표시 line narrates the wait but is not a transport frame | `operations` / P4 |
| **nothing bounds an agent turn in *time*** | the 120 s timeout is per model call, so a pathological 20-round turn can hold its concurrency slot and its SSE connection for a long while. A per-turn deadline is the obvious fix; none was added, because none is in the record | `architecture` / P4 |
| **the agent's declaration construction is exercised only live** | the SDK is not installed in the test venv, so the plain tool-spec data is unit-tested and the SDK object construction is not. A live turn is what proves it | `backend` |
| **agent spend is invisible under a default `uvicorn`** | the ▷ ledger is `log.info` and uvicorn configures only its own loggers, so without a root logging configuration the record is written nowhere | `operations` / P4 |

## Open Questions

- ~~No browser/E2E QA exists yet~~ — **the method now exists and ran**, and a blocked field was
  verified absent rather than placeheld on real pages. What is still missing is **automation**: every
  browser pass to date was driven by a scripted CDP session written for that pass, not by a
  checked-in suite. Whether that becomes a committed E2E layer is a real question, and the repo's
  terse-tests rule argues for keeping it a method rather than growing a framework. **P11's third pass
  changed the ground under this question**: Aside is now installed and signed in on this machine, and
  an agentic walk (`aside exec`) found things no scripted assertion was ever going to — it also
  reported two 「defects」 that were its own instrument's artifacts (a `goBack` that waits for a hard
  navigation the SPA never fires, and text read without block boundaries), both refuted by hand
  before they reached the operator. That is the shape of the trade: an agent notices what nobody
  thought to assert, and every finding it returns still has to be re-measured before it is believed.
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
