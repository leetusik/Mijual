# Result — P1.S1: DART OpenAPI spike & field matrix

**Status: done.** The phase's load-bearing artifact exists and is grounded in real 2026 filings: `docs/reference/dart/field-matrix.md`. All three open questions aimed at this slice (Q1, Q2, Q3) are answered with measurements, not estimates.

## What was done

Three throwaway-grade stdlib-only scripts under `scripts/spike/` (no framework, no packaging, no tests — per the phase's "P1 spike code is explicitly throwaway-grade" constraint):

| file | role |
|---|---|
| `scripts/spike/dart.py` | tiny OpenDART client — in-process `.env` parse, on-disk response cache, retry/backoff, `groups()` helper for the 증권신고서 shape, `document` ZIP/XML access |
| `scripts/spike/survey.py` | field-coverage survey per rights type + `population` (event universe), `labelscan` (본문 label stability), `docprobe` (Q3) |
| `scripts/spike/corrections.py` | 정정공시 pairing + `<CORRECTION>` 정정사항 parse + structured-version probe (Q2) |

Sample frame: **2026-01-01 ~ 2026-08-18, KOSPI (`Y`) + KOSDAQ (`K`)** — 3,820 `pblntf_ty=B` rows and 3,843 `pblntf_ty=C` rows discovered. **1,002 distinct cached API requests** (59 of them `document` 본문 ZIPs).

## Answers

**Q1 — `estkRs.asstd` for 주주배정, and 신주인수권증서 매매기간.**
배정기준일 populates **28 / 28** in 주주배정-type 증권신고서 filings (as do 청약기일, 납입일, 발행가, 주관사). 신주인수권증서 상장·매매기간 has **no structured field anywhere** — but it is recoverable from 본문 prose in **8 / 9** sampled 주주배정 filings. The surprise: the 유증 **주요사항보고서 본문** is only ~6,000 characters and carries 배정기준일 / 배정주식수 / 청약예정일 / 납입일 / 상장예정일 / 대표주관회사 / 증서 상장여부 / 증서 매매 중개사 as **numbered labelled table rows — 10 / 10 labels present in 9 / 9 filings**. ① is therefore *mixed* (deterministic skeleton + ~5 prose fields), not uniformly LLM-heavy as the phase feared.

**Q2 — 정정 pairing and a machine-readable "what changed".**
The 정정 filing carries its own `<CORRECTION>` block with a `3. 정정사항` table (항목 / 정정사유 / 정정 전 / 정정 후) — parsed **40 / 40**. Pairing to the original: **30 / 40** (16 exact `최초제출일`, 14 nearest-earlier); the 10 misses have pre-2026 originals. `최초제출일` is filer-entered and sometimes wrong — a hint, not a key.
**The load-bearing sub-answer:** the structured API returns **one row per event, newest version only**, and its date window filters on the **original** 접수일 — the correction-date probe returned `[]` in every one of 40 samples. Superseded structured values are unrecoverable, and `rcept_no` is version-mutable. This is a hard constraint on P2's collector (see `phase.md` F11).

**Q3 — `document` parseability.**
Yes, comfortably. 5 / 5 ZIPs → one UTF-8 XML with HTML-like table markup and `<SECTION-1>` / `<TITLE ATOC>` section markers. Two regimes: 주요사항보고서 **2,598–9,848** text chars (one-shot LLM input) vs 증권신고서 **615,780–1,867,597** (needs `<TITLE>`-section slicing). No HTML-viewer fallback needed.

## Per-rights-type feasibility signal for `P1.S2`

| | 2026 event universe (measured) | structured coverage | verdict |
|---|---|---|---|
| **① 유증 신주인수권** | 299 유상증자 reports, only **32 주주배정 계열 (11%)** → ▷ ~4–5/month | thin API, rich 본문-label | **mixed** — smallest universe, highest user value, ~5 prose fields to extract. Bounded, not scary. |
| **② CB·EB 오버행** | **263 CB / 236 corps** + 20 EB — largest by far | **excellent** — 전환가액, 전환청구기간, 오버행 % all 47/47; 리픽싱 floor 36/47 | **most deterministic + biggest volume**. Cheapest path to a data-dense demo. |
| **③ 매수청구권** | 83 합병 reports but **65 소규모합병** (no 매수청구권) → **15–17 real events** → ▷ ~2/month | **near-total**; 반대의사 통지 접수기간 **41/41 structured** | **cheapest to build, thinnest to demo.** Needs a `mg_stn` filter or it will publish phantom rights. |

## Validation

| command | outcome |
|---|---|
| `python3 scripts/spike/dart.py` | pass (rc=0) |
| `python3 scripts/spike/survey.py rights1` | pass — 유증 field survey + Q1 |
| `python3 scripts/spike/survey.py rights2` | pass — CB/EB/bdRs survey |
| `python3 scripts/spike/survey.py rights3` | pass — 합병/mgRs/주식교환 survey |
| `python3 scripts/spike/survey.py population` | pass — 2026 event universe per type |
| `python3 scripts/spike/survey.py labelscan 10` | pass — 10/10 labels × 9/9 filings |
| `python3 scripts/spike/survey.py docprobe` | pass — Q3, 5/5 ZIPs parsed |
| `python3 scripts/spike/corrections.py 40` | pass — 30/40 paired, 40/40 정정사항 tables |
| `python3 scripts/workflow.py validate` | **Workflow validation passed** |

All eight spike entry points were re-run **from a clean environment** (`env -i`, so `DART_API_KEY` came only from the `.env` parse): rc=0 for all, and **zero occurrences** of the key value or of `crtfc_key` in any stdout. A repo-wide byte scan confirms **no file contains the key value**; the only `crtfc_key` hits are the literal parameter name inside `scripts/spike/dart.py` (and its gitignored `.pyc`), which is correct.

Plan acceptance criteria: matrix exists and covers all 3 rights types + the 정정 section ✅; every "structured" claim carries an evidence `rcept_no` ✅; **≥5 기재정정 pairs — 30 paired and diffed, well past the bar** ✅.

### The paired 기재정정 samples (exact-`최초제출일` subset, with what changed)

| rights type | 정정 | corp | ← original | changed fields |
|---|---|---|---|---|
| ① | `20260715000344` | 케이지에이 | `20260612000447` | 신주의 종류와 수, 운영자금, **발행가 1,388→1,215**, 기준주가 |
| ① | `20260730000278` | LB세미콘 | `20260515002719` | 자금조달 목적, 신주 발행가액 |
| ② CB | `20260529002142` | 엑스페릭스 | `20260507000567` | 사채만기일, 전환가액 결정방식, 전환청구기간, **총수 대비 비율 7.36→6.73%** |
| ② CB | `20260616000268` | 포니링크 | `20260529001660` | 권면총액, 자금조달 목적, 전환에 관한 사항 |
| ② CB | `20260721001361` | 애드바이오텍 | `20260626000645` | 사채만기일, 전환에 관한 사항, 옵션, 청약일 |
| ② EB | `20260203000135` | 아주스틸 | `20260126000473` | 기타 투자판단 free-text blocks |
| ② EB | `20260210000877` | 알서포트 | `20260203000402` | 기타 투자판단 free-text blocks |
| ② EB | `20260306001019` | 위닉스 | `20260224002371` | **전항목: 발행결정 → 발행결정 철회** |
| ② EB | `20260401002847` | HD한국조선해양 | `20260331003385` | 권면총액, 해외발행 통화·기준환율, 운영자금 |
| ③ | `20260319000331` | 모다이노칩 | `20260219002620` | 합병기일 4/28→4/30, 합병보고총회일 4/29→4/30 |
| ③ | `20260730000178` | 한중엔시에스 | `20260729000331` | **합병반대의사통지 접수기간 시작일 8/14→8/13** |

Plus 14 more paired nearest-earlier, and a worked non-exact illustration: `20260813001290` (에넥스) — 납입일 8/13→9/14, 상장예정일 8/31→9/30, i.e. a user's D-day would have moved 32 days. Full records in `scripts/spike/samples/_summary/corrections.json`.

## Deviations from `plan.md`

1. **Added `.gitignore` entries** for the raw response cache. The plan asked for caching under `scripts/spike/samples/`; that cache grew to **9.4 MB / 1,002 files** and is fully regenerable, so `scripts/spike/samples/*` is now ignored with `!scripts/spike/samples/_summary/` kept — the 7 small machine-readable summaries stay committed as evidence. Two lines in `.gitignore`; no other file was touched outside the slice's scope.
2. **Two extra `survey.py` modes beyond the plan's outline** — `population` (queried *every* corp with a matching 2026 filing, not a sample) and `labelscan` (본문 label stability). Both were cheap and both turned out decision-grade: `population` is the event-universe input `P1.S2` needs, and `labelscan` is what turned "① is LLM-heavy" from an assumption into a measurement. Still three files, still throwaway-grade.
3. **Sample volume above the plan's floor** in one place: 40 corrections instead of the required ≥5, because the 항목-frequency table is only meaningful with volume. Sample sizes are recorded honestly everywhere (per-endpoint corp caps are stated in the matrix's §6 coverage-gaps note).
4. **`bdRs` produced a negative result** rather than the expected CB coverage — 사모 CB is 증권신고서-면제, so `bdRs` is 공모 회사채. Recorded as a negative finding (F14a) rather than dropped.

No boundary was crossed: no P2 pipeline, no 총액 estimation, no evalset, no DB/scheduler, **no LLM calls at all**. The matrix states where LLM extraction *will* be needed; it performs none.

## Doc impact

One line appended to `phase.md`'s running list, against **`data`** (extraction-target field matrix, 정정 diff targets, DART source + version constraints). The `P1.REVIEW` slice consolidates it.

## Candidate deferred jobs (not absorbed)

- ▷ **분할합병 (`cmpDvmgDecsn`) / 주식교환·이전 (`stkExtrDecsn`) as part of rights type ③.** Same 매수청구 field shape (evidence `20260522000296`); would roughly double ③'s universe at low marginal cost. Belongs to P2 scope-sizing, only if ③ survives `P1.S2`.
- ▷ **KONEX/기타 (`corp_cls=N/E`) coverage.** The whole survey is KOSPI+KOSDAQ; unlikely to change any conclusion but unmeasured.
- ▷ **OpenDART daily call quota.** Not measured; ~1,002 requests in one session drew no error. Confirm before P2's backfill.
- ▷ **`estkRs.일반사항.exstk/exprc/expd` semantics** (2/35 filled) — unresolved, and not needed by any §3.6 field.
