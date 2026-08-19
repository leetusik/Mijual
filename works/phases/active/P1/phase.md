# Phase P1: Foundation Spike & Confirmations

_Intent: see [intent.md](intent.md)._

## Objective

Validate DART OpenAPI coverage for the 3 MVP rights types — produce the event-type × field × {structured API / LLM extraction needed} matrix (incl. ≥5 정정공시 samples for diff targets), finalize MVP rights scope with the operator, and recon daker.ai submission requirements + mijual domain availability.

## Context

- **Project**: 미주알 / mijual — 2026 금융 AI Challenge entry. Submission deadline **2026-09-07 10:00 KST** (D-19 from 2026-08-19). Judged on a *working* web service, not an idea.
- **Source of truth for project context**: `docs/reference/challenge/00_HANDOFF.md` (§3.6 AI-role architecture, §6 backlog, §7 working principles) and `docs/reference/challenge/01_문제정의.md`. P1 covers handoff §6 items **1, 2, 6** (+ the domain-availability part of item 4). Everything else belongs to P2 (pipeline), P3 (web service), P4 (ship & submit).
- **OpenDART API key**: already provisioned and live-verified. Stored at repo root `.env` as `DART_API_KEY=...`. `.env` is gitignored — **never move, echo, or commit the key**; read it in-process (e.g. parse `.env` or `os.environ`) and never print it into logs, `result.md`, or spike artifacts.
- **Rights-scope gate is an operator decision (2026-08-19)**: the tentative MVP 3종 (① 유증 신주인수권 ② CB·EB 오버행 ③ 매수청구권) is *tentatively* confirmed only. `P1.S2` must **pause for the operator** — it produces a recommendation, returns `needs_operator`, and the orchestrator sets the slice `pending`. Nothing auto-confirms the scope.
- **Working language**: English for thinking/notes/docs; Korean stays for domain artifacts (공시 field names, 보고서명) and for the product surface (all user-facing copy is Korean-only).
- **No product visual design in P1** → single-pass decomposition. No `co-work` slice, no `P1.DECOMP2`.
- **Doc targets for this phase** (append Doc impact notes naming these; the REVIEW slice consolidates): `data` (DART sources, extraction-target field matrix, 정정 diff targets), `decisions` (MVP rights scope, ordering/gate decisions), possibly `architecture` (where the structured/LLM boundary sits in the §3.6 layer-1 design).

## Decomposition

Three middle slices. **Execution order deliberately differs from ID order** (selection is by `order`, not by ID):

| order | slice | kind | risk | one-line rationale |
|---|---|---|---|---|
| 1 | `P1.S1` — DART OpenAPI spike & field matrix | `spike` | high | The phase's load-bearing slice (handoff §6 #1, "최우선, 기획 성패 결정"): exercise the real APIs against real 2026 filings and produce the event-type × field × {structured / LLM-extraction} matrix, incl. ≥5 정정공시 samples for diff targets. Writes real code (spike scripts) across more than one file → high. |
| 2 | `P1.S3` — Recon: daker.ai + domain availability | `research` | high | External recon (handoff §6 #6 + the domain part of #4): submission format (데모 URL·영상·기획서 양식), 개인/팀 rules, 본선·발표 schedule vs the operator's 9/1 employment availability; mijual.ai / .kr / .com availability. Needs WebSearch/WebFetch → the high tier. Independent of S1. |
| 3 | `P1.S2` — MVP rights-scope recommendation & operator confirmation | `decision` | high | Reads S1's matrix (extraction feasibility inside 19 days) **and** S3's recon (what the submission actually demands), writes a keep/demote recommendation per rights type, then stops on the operator. `depends_on: [P1.S1, P1.S3]`. |

**Ordering rationale (the one real decomposition decision).** The plan sketched S1 → S2 → S3; recon is placed **before** the confirmation slice instead, because:

1. `P1.S2` ends in a `pending` operator gate, and `pending` **halts the whole phase** — `next` prints `WAITING ON OPERATOR` and no slice may start or advance past it. Recon parked behind that gate would be blocked for an unknown wall-clock stretch, which is unaffordable at D-19.
2. Recon is genuine *input* to the scope decision: submission format and 본선 schedule change how much can realistically be built and demoed, so the operator should decide scope with that on the table.
3. It batches both operator-facing outputs — the scope recommendation *and* the domain purchase question (mijual.ai is a decision only the operator can execute) — into **one** operator round-trip instead of two.

**ID mapping kept as written in `P1.DECOMP/plan.md`** (S2 = scope confirmation, S3 = recon) rather than renumbering, so that plan and slice folders keep referring to the same things; only `--order` was used to sequence them. Expect `works/backlog.md` to list P1.S1, P1.S3, P1.S2 in that order.

**Explicitly out of scope for P1** (do not let a slice grow into these): the 소멸 신주인수권 총액 estimation pipeline and the ~100-filing labeled evalset (P2), any service/UI build (P3), notifications/deploy/submission artifacts (P4). P1 produces knowledge and decisions, plus throwaway-grade spike code.

## Findings & Notes

Recorded by `P1.DECOMP` on 2026-08-19 from a **light live probe** of OpenDART (endpoint existence + one field-name peek). These are decomposition intel to aim `P1.S1`, **not** the matrix — `P1.S1` still owns systematic verification, sample counts, and the durable artifact.

**F1 — All the needed 주요사항보고서 endpoints exist and authenticate.** `piicDecsn` (유상증자), `fricDecsn`, `pifricDecsn`, `cvbdIsDecsn` (CB), `bdwtIsDecsn` (BW), `exbdIsDecsn` (EB), `cmpMgDecsn` (합병), `cmpDvmgDecsn` (분할합병), `cmpDvDecsn` (분할), `stkExtrDecsn` (주식교환·이전), `astInhtrfEtcPtbkOpt` all return `status 013` (조회된 데이타 없음) for a corp with no such filing, while a bogus endpoint returns `status 101 잘못된 URL`. So **013 = endpoint real + key valid**; 교환사채 `exbdIsDecsn` is available (the plan's "if available" is resolved: yes).

**F2 — 유상증자 결정 structured output is thin; this is the phase's most consequential finding so far.** Across 15 `piicDecsn` rows from 12 corps (2026-06-01 ~ 08-18, mixed 제3자배정 10 / 일반공모 4 / 주주배정 1) the field set was a constant **19 keys**: `rcept_no, corp_cls, corp_code, corp_name, nstk_ostk_cnt, nstk_estk_cnt, fv_ps, bfic_tisstk_ostk, bfic_tisstk_estk, fdpp_* (자금조달 목적), ic_mthn (증자방식), ssl_at/ssl_bgd/ssl_edd (공매도 관련)`. **No 신주배정기준일, no 발행가액, no 배정비율, no 청약일, no 신주인수권증서 매매기간.** i.e. the killer rights type (① 유증 신주인수권) gets essentially nothing service-critical from this endpoint — matching handoff §3.6's premise, but harder than the backlog's wording implies.

**F3 — …but the 증권신고서 APIs carry much of what `piicDecsn` lacks.** `estkRs` (증권신고서 지분증권 주요정보) returns grouped sections (`group[].title` + `list`) — 일반사항 with `sbd` 청약기일, `pymd` 납입일, `sband` 청약공고일, `asand` 배정공고일, **`asstd` 배정기준일**, `exstk/exprc/expd`; 증권의종류 with `slprc` 발행가·`stkcnt`·`slta`; **인수인정보 with the 대표주관·인수 증권사 name** (`actnmn`, `udtmth`) — which answers the §3.6 "청약 취급 증권사" field structurally. Sibling endpoints `bdRs`, `mgRs`, `dvRs`, `extrRs` exist too. **Implication for `P1.S1`: the matrix must span 주요사항보고서 *and* 증권신고서 endpoints per event type — a matrix built on 주요사항보고서 alone would overstate the LLM-extraction burden.** (The probed sample was 일반공모, so `asstd` was `-`; whether 주주배정 filings populate it is exactly what S1 must check.) Still expected to be 본문-only: 신주인수권증서 상장·매매기간, 실권주 처리 방식, 초과청약 조건, CB 리픽싱 세부·콜풋·보호예수 해제 스케줄, 매수청구 반대의사 통지 방법.

**F4 — CB/EB and 합병 are structurally much richer than 유증.** `cvbdIsDecsn` already returns `cv_prc` 전환가액, `cv_rt`, `cvrqpd_bgd/edd` 전환청구기간, `act_mktprcfl_cvprc_lwtrsprc(_bs)` 리픽싱 최저조정가액 + 근거, `rmislmt_lt70p`, `sbd/pymd`. `exbdIsDecsn` mirrors it with `ex_prc/ex_rt/exrqpd_bgd/edd/extg`. `cmpMgDecsn` returns `aprskh_plnprc` 매수청구 예정가격, `mgsc_aprskh_expd_bgd/edd` **매수청구 행사기간**, `mgsc_shddstd` 주주확정기준일, `mgsc_shclspd_*`, `mgsc_ergmd` 주총일, `mgsc_nstklstprd`. ▷ Provisional read (S1 to confirm): the structured/LLM boundary is **per rights type, not uniform** — ② and ③ may be largely deterministic, while ① carries most of the LLM load.

**F5 — 정정공시 samples are abundant; the pairing method is the open work.** In 2026-06-01 ~ 08-18, KOSPI-only `pblntf_ty=B` returned 413 filings; of the first 100, **37 were `[기재정정]주요사항보고서` and 10 `[첨부정정]`**. Two discovery handles exist: the `report_nm` prefix `[기재정정]` on the corrected filing, and `rm="정"` on the superseded original. `list.json` does **not** expose the original's `rcept_no` from the correction row, so S1 must decide how to pair original↔correction (same corp_code + same 보고서 subtype + nearest earlier `rcept_dt`, or parse the pairing out of the document header) — that pairing is the prerequisite for the diff-target field list. Note `[첨부정정]` (attachment-only) is likely a no-op for diffing; prefer `[기재정정]`.

**F6 — API constraints worth knowing before writing collection code.** `list.json` without `corp_code` allows a **3-month** window only (`status 100`, message `corp_code가 없는 경우 검색기간은 3개월만 가능합니다`); `page_count` max 100 with `page_no` paging; `pblntf_ty=B` = 주요사항보고, `C` = 발행공시(증권신고서 등); useful row fields `corp_code, corp_name, stock_code, corp_cls, report_nm, rcept_no, rcept_dt, rm`. 본문 원문 for LLM extraction comes from the `document` API (ZIP of the filing XML) keyed by `rcept_no`.

**F7 — Prior art / non-goal reminder.** Nothing here changes the §7 rule that calculation stays deterministic; a richer structured field set is *good news* for that rule, not a reason to widen the LLM's job.

### Findings from `P1.S1` (DART OpenAPI spike, 2026-08-19)

Systematic, not a probe: **1,002 distinct cached OpenDART requests** over 2026-01-01~08-18, KOSPI+KOSDAQ. Durable artifact: **`docs/reference/dart/field-matrix.md`** — read that for the per-field detail; the notes below are the cross-slice consequences.

**F8 — Q1 ANSWERED: `estkRs.asstd` populates 28/28 for 주주배정 filings; 신주인수권증서 매매기간 has no structured field anywhere.** Also 100% populated for 주주배정: `sbd` 청약기일, `pymd` 납입일, `slprc` 발행가, `stkcnt`, `slmthn`, `인수인정보.actnmn` 주관사. Evidence `20260814004100` (계양전기), `20260318001009`, `20260427000469`. F3's hypothesis is confirmed — the matrix had to span 주요사항보고서 **and** 증권신고서.

**F9 — The biggest finding, and it *reduces* P2's cost: the 유증 주요사항보고서 본문 carries nearly everything `piicDecsn` drops, as numbered labelled table rows, in a ~6,000-character document.** `8. 신주배정기준일`, `9. 1주당 신주배정주식수`, `11. 청약예정일`, `12. 납입일`, `16. 신주의 상장예정일`, `17. 대표주관회사`, `18. 신주인수권양도여부 / 증서 상장여부 / 증서 매매 중개 금융투자업자`. A label scan over 9 real 주주배정 filings found **10/10 labels present in 9/9**. So ① is **not** uniformly LLM-heavy: deterministic skeleton + ~5 prose fields (증서 상장·매매기간, 청약취급처, 실권주 처리, 초과청약 조건, 발행가 산정방법), all inside `24. 기타 투자판단에 참고할 사항`. Prose phrasing genuinely drifts (`상장예정기간` vs `매매기간`, `(5영업일)` vs `(5거래일)`, one filing with two ranges) — that drift, not the field's absence, is what justifies schema-based LLM extraction + a date-order gate.

**F10 — Q2 ANSWERED: the 정정 filing carries its own machine-readable what-changed block.** The 본문 `<CORRECTION>` element holds `정정대상 공시서류`, `정정대상 공시서류의 최초제출일`, and a `3. 정정사항` table (항목 / 정정사유 / 정정 전 / 정정 후) — parsed **40/40**. Pairing: **30/40** (16 by exact `최초제출일`, 14 nearest-earlier same-corp same-subtype); the 10 misses have pre-2026 originals. `최초제출일` is filer-entered and sometimes wrong (one declares 2022-08-01) — hint, not key. A single event can carry a chain (디모아: 6 corrections on one 유증).

**F11 — HARD CONSTRAINT ON P2's COLLECTOR (new, load-bearing).** Three measured behaviours of the 주요사항보고서 detail endpoints: (a) they return **one row per event, newest version only** — SKC's 3 filings collapse to `20260512000196`, 디모아's 6 to `20260625000227`; (b) the `bgn_de/end_de` window filters on the **original** 접수일, so the correction-date single-day probe returned `[]` in **every** one of 40 samples → *a daily "yesterday's filings" poll driven by the detail endpoints silently misses every 정정*; (c) `rcept_no` is **not a stable key** — it mutates to the newest version (only 7/39 `estkRs.rpt_rcpn` values match today's `piicDecsn` rcept_no). **→ P2 must poll `list.json` for `[기재정정]`, key events by `(corp_code, subtype, original_rcept_dt)`, and snapshot every version; superseded structured values are otherwise unrecoverable.**

**F12 — Q3 ANSWERED: `document` is comfortably parseable; no HTML-viewer fallback needed.** 5/5 ZIPs → one UTF-8 XML with `TABLE/TR/TD` markup plus `<SECTION-1>` / `<TITLE ATOC>` section markers. **Two size regimes:** 주요사항보고서 **2.6k–10k** text chars (one-shot LLM input) vs 증권신고서 **616k–1.87M** (needs `<TITLE>`-section slicing). Since the 주요사항보고서 already carries every service-critical field, ▷ the 증권신고서 is best treated as a confirmation/citation-span source, not the primary extraction target. Character-addressable XML also satisfies §3.6 layer 2's 인용 스팬 gate.

**F13 — Per-rights-type feasibility, for `P1.S2`'s decision (2026-01-01~08-18, KOSPI+KOSDAQ, measured).**

| | 2026 event universe | structured coverage | LLM load |
|---|---|---|---|
| ① 유증 신주인수권 | 299 유상증자 reports but only **32 주주배정 계열 (11%)** → ▷ ~4–5/month | thin API; rich 본문-label | ~5 prose fields — the heaviest of the three, but bounded |
| ② CB·EB 오버행 | **263 CB reports / 236 corps** + 20 EB — by far the largest | **excellent**: 전환가액, 전환청구기간, 오버행 % (`cvisstk_tisstk_vs` 47/47), 리픽싱 floor 36/47 | only 콜·풋 / 리픽싱 세부 / 보호예수 narrative |
| ③ 매수청구권 | 83 합병 reports but **65 are 소규모합병** (no 매수청구권) → only **15–17 real events** → ▷ ~2/month | **near-total**; 반대의사 통지 **접수기간 41/41 structured** (better than §3.6 assumed) | only 반대의사 통지 방법·절차 |

**F14 — Two negative results worth not re-discovering.** (a) `bdRs` (증권신고서 채무증권) is **not** a CB source — 사모 CB is 신고서-면제 (`ex_sm_r`), and across 77 `bdRs` rows the 지분 관련 사채 fields were 0/77 filled; for ② the 주요사항보고서 is the only source. (b) 소규모합병's empty `aprskh_*` is **semantically correct**, not a data gap — publishing those as if a 매수청구권 existed would be a correctness bug; filter on `mg_stn` / `aprskh_*` presence.

**F15 — API gotchas that cost time (beyond F6).** 증권신고서 endpoints (`estkRs`/`bdRs`/`mgRs`/…) return **`group[]` of `{title, list}`**, not a flat `list` — a 주요사항보고서-shaped client silently reads 0 rows. `None` query params must be **dropped**, not serialized (`corp_code=None` → `status 100`). Transient **HTTP 503** occurs under sustained calling → retry with backoff (6 concurrent threads sustained ~1,000 requests without a ban). ▷ Daily quota unmeasured — confirm before P2's backfill.

**F16 — Repo hygiene decision.** The raw response cache is ~9.4 MB / 1,002 files and is fully regenerable, so `.gitignore` now excludes `scripts/spike/samples/*` while keeping `scripts/spike/samples/_summary/` (7 small machine-readable summaries) as committed evidence. Confirmed by scan: no file in the repo contains the key value.

**Q7 addendum (for P2/P3):** ▷ 분할합병 (`cmpDvmgDecsn`) and 주식교환·이전 (`stkExtrDecsn`, evidence `20260522000296`) carry the same 매수청구 field shape as 합병 — if ③ ships, treat them as the same rights type on a different endpoint rather than a new type; roughly doubles ③'s universe at low marginal cost.

## Constraints

Binding on every P1 slice (handoff §7 + the intent):

- **Evidence tags.** Facts carry a source link/command; estimates are marked `▷`. Never blur the two — the operator's inventory culture and the whole "AI를 통제하며 썼다" pitch depend on it.
- **No inflation.** Never round a sample up, never present a probe as a survey, never invent counts. Record honest gaps as gaps.
- **§3.6 AI-role architecture is fixed**: AI does *reading* (schema-based extraction from 비정형 공시) and *speaking* (grounded generation); **all calculation (금액 환산·D-day) is deterministic**, and extracted fields must pass deterministic gates (arithmetic consistency, date order, citation-span presence) before exposure. P1's matrix must be usable as the input to that gate design.
- **금지선**: no fine-tuning / PyTorch / HF framing anywhere — not in code, notes, docs, or later pitch material. Model *training* is out of the story entirely.
- **Small scope, production-grade polish** — but P1 spike code is explicitly throwaway-grade: keep it to a script or two (e.g. `scripts/spike/`), tests terse, no framework scaffolding. The real pipeline is P2's.
- **Secrets**: `DART_API_KEY` stays in gitignored `.env`. Spike artifacts (sample JSON, matrix markdown) must not embed the key or a keyed URL.
- **Deadline discipline**: 2026-09-07 10:00. A P1 slice that starts sprawling should record the surplus as a deferred job rather than absorb it.
- **No commits by executors**; the orchestrator owns state transitions and commits.

## Doc impact

_Running list; the `P1.REVIEW` slice consolidates these into doc versions on a pass._

- (none from `P1.DECOMP` — the probe findings above are provisional decomposition intel. The first durable note is expected from `P1.S1` against `data` (extraction-target field matrix + DART source constraints), then `P1.S2` against `decisions` (confirmed MVP rights scope).)
- **`data`** — DART as the sole MVP source is characterised: per-rights-type structured/`본문-label`/`본문-prose` field matrix for the 3 MVP types (durable artifact `docs/reference/dart/field-matrix.md`), the 10-field §3.6 layer-1 extraction-target list with its 결정론 게이트, the 정정공시 pairing method + diff-target fields, and the version/collection constraints that shape P2's entity keys (detail endpoints return newest-version-only, `rcept_no` is version-mutable, event key must be `(corp_code, subtype, original_rcept_dt)` with per-version snapshots). Source: `P1.S1`.

## Open Questions

- **Q1 (for S1):** does `estkRs.asstd` (배정기준일) actually populate for **주주배정** 유상증자, and does any structured endpoint expose **신주인수권증서 상장·매매기간**? If not, ① 유증 is LLM-extraction-heavy and that is the single biggest cost driver in P2.
- **Q2 (for S1):** how to pair a `[기재정정]` filing with the original it supersedes (F5) — and does the 정정 document itself carry a machine-readable "what changed" block, or must the diff be computed field-by-field from re-fetched structured records?
- **Q3 (for S1):** is `document` (본문 XML/ZIP) parseable well enough to feed schema-based extraction directly, or is an HTML fallback (dart.fss.or.kr viewer) needed? Affects P2's collection design.
- **Q4 (for S2, operator):** if ① 유증 turns out to be the most LLM-expensive and ②/③ the most structured, does the MVP keep all three, or lead with the demo-strongest one? The tentative 3종 is not auto-confirmed.
- **Q5 (for S3):** does daker.ai treat a solo entrant differently (개인 vs 4인 이하 팀), and does the 본선/발표 schedule (9~10월) collide with the operator's 9/1 employment availability? Also: is a 기획서 template mandated, and is a demo video required or optional?
- **Q6 (for S3):** is `mijual.ai` actually purchasable and at what price tier — and if not, is `.kr` or `.com` the fallback the operator wants to buy *now* (a decision only the operator can execute)?
- **Q7 (deferred, P2/P3):** 증권사 MTS 권리 메뉴 coverage matrix (handoff §4: "미발견 ≠ 부존재", to be confirmed in development week 1) — not P1 work, but it must not be forgotten.
