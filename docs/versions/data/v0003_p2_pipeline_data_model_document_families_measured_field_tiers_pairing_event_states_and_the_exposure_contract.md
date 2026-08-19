---
doc_id: data
version: v0003
created_at: 2026-08-20T05:06:14+09:00
source: P2.REVIEW
summary: P2 pipeline data model: document families, measured field tiers, 정정 pairing, event states and the exposure contract
previous: v0002_dart_as_the_mvp_data_source_rights-type_field_matrix_extraction_targets_version_and_constraints
---

# Data

## Status

P1 characterised the upstream; **P2 turned it into a stored, gated corpus**. This version keeps P1's
durable survey truth and supersedes it wherever P2 measured something different at larger scale.
Facts carry an `rcept_no`, a command or a count; estimates are marked `▷`. Per-field survey detail
still lives in `docs/reference/dart/field-matrix.md`; the storage schema lives in `architecture`.

Corpus as it stands (`.venv/bin/python -m mijual.gates run`, 2026-08-20): **1,345 events / 3,990
filing versions / 7,076 snapshots / 69 증권발행실적보고서**, **649 extraction rows** (633 distinct
`(rcept_no, field_key)`), **488 exposable events (① 50, ② 422, ③ 16) / 409 renderable field
instances**.

## Source of Record

**OpenDART (`https://opendart.fss.or.kr/api`) is the MVP's sole data source.** No scraping, no vendor
feed. Auth is a single API key, `DART_API_KEY`, kept in the gitignored repo-root `.env`, read
in-process, never printed into logs or artifacts.

| rights type | endpoints | notes |
|---|---|---|
| ① 유증 신주인수권 | `piicDecsn` · **`pifricDecsn` (유무상증자결정)** · `estkRs` · **증권발행실적보고서 (`pblntf_ty=C`)** · `document` | only 주주배정 계열 issues a 증서 |
| ② CB 오버행 | `cvbdIsDecsn` · `document` | `bdRs` is **not** a CB source (사모 CB is 신고서-면제, 0/77 filled) |
| ③ 매수청구권 | `cmpMgDecsn` · `mgRs` · `document` | 소규모합병 grants no right and is suppressed |

**`유무상증자결정` (`pifricDecsn`, form 11308) is a first-class ① source** (P2.S8) — same numbered
유상 section, 10/10 target labels, `18. 신주인수권양도여부`, and its `ic_mthn` arrives under the
`piic_ic_mthn` prefix. It was invisible to every pre-S8 run: **7 of the 32 offerings that lapsed in
2026 were filed this way**, and 9 such events are live on the board today.

## Field Tiers (how each field is obtained)

Unchanged in principle, and now measured in code:

| tier | reader | measured |
|---|---|---|
| `API` | deterministic JSON read | ②'s whole countdown (전환가액, 전환청구기간, 오버행) and ③'s 반대의사 접수기간 |
| `본문-label` | deterministic table parse with a character span | **94/94** 주주배정 계열 유상증자결정 본문 yield all 10 §1.3 target labels; **23,493/23,493** extracted values carry a verified span |
| `본문-prose` | LLM schema extraction **+ deterministic gate** | the 10 targets below, and nothing else — the registries are asserted disjoint by test |

**② and ③ still need zero LLM extraction for their countdowns.** ① is the only type that exercises
the reading layer.

## Document Families (P2 additions)

- **유상증자결정 is a form family, not one form.** 제3자배정 / 일반공모 / 주주우선공모 templates carry
  **no 신주인수권 rows at all**, so an absent `18. 신주인수권양도여부` is *evidence of no 증서*, not a
  data gap. `ic_mthn` never confirms a right — **본문 `18.` is the final test**; when the two
  disagree the event stays live with a `warrant_conflict` flag for the gate layer to decide.
- **증권발행실적보고서 (`pblntf_ty=C`, filed on the 납입일)** is the 청약-결과 source the P1 matrix never
  surveyed, and it is **entirely `본문-label` tier — 0 LLM calls**: `Ⅶ` gives 발행 증서 / 증서 청약 /
  초과청약, `Ⅷ` the 실권주, `3.`'s 계 row's 최종 금액 ÷ 수량 **is** the 확정발행가 (agrees with 본문
  `6. 확정발행가` on **31/31** offerings that state both), `1.` the schedule that binds the report to
  its event (**32/32 `schedule_match`**). Two forms exist: the standard 주식 form and the
  집합투자증권 (REIT) form, which has no `Ⅶ` section.
- **증권신고서 is sliced by `<TITLE>` section and never read whole** (3.4 M chars → a 33,780-char
  청약절차 section; 9.5 M → a 38,033-char 매수청구권 section). 주요사항보고서 (≈2.6k–10k chars) is the
  one-shot unit; a 100k–180k-char 합병 본문 is **windowed** around the field anchor.
- **`<CORRECTION>` `2. 최초제출일` is recovered in 354/360 = 98.3 %** of correction blocks (P1's 40/40
  was a small sample) and 1,450 `3. 정정사항` rows parse.

## Extraction Targets (the LLM's entire reading job)

Ten fields. The gate column is what P2 actually implemented — three rows needed the corpus to settle:

| # | field | type | gate as implemented |
|---|---|---|---|
| 1 | 신주인수권증서 상장·매매기간 | ① | date order, between 배정기준일 and 청약일 |
| 2 | 청약 취급처 (대상자별 증권사 + 청약일) | ① | 청약일 vs 본문 `11.`; **일반공모 entries have no `11.` reference and are gated on ordering** |
| 3 | 실권주 처리 방식 | ① | enumerated method (일반공모 / 대표주관회사 인수 / 미발행) |
| 4 | 초과청약 조건 (비율) | ① | 0 < ratio ≤ 1; the *배정주식수 × ratio* arithmetic needs a holder's 주수 and therefore lives in `mijual.calc`, not in a document check |
| 5 | 발행가액 산정방법 | ① | vs 본문 `6. 확정예정일`, which is the **결정일** while the prose names the 공시일 (16 agree / 3 differ by exactly +1 day) → **a window, not an equality** |
| 6 | 리픽싱 세부 조건 | ② | floor == API `act_mktprcfl_cvprc_lwtrsprc` — **held exactly as written: 29/29 comparable rows, 0 mismatches** |
| 7 | 콜·풋 세부 스케줄 | ② | within 발행일 ~ 만기일; dates carry two conventions (조기상환기일 range vs 청구기간 range) and need a `date_basis` marker |
| 8 | 보호예수 / 전매제한 해제일 | ② | **changed**: a CB states 전매제한 as a *duration*, not a date, in 31 of 62 rows, so the 해제일 is **derived deterministically** (`mijual.calc.lockup_release_date` = API 납입일 + 개월수) and any stated date is checked against that derivation (31 failures → 3) |
| 9 | 반대의사 통지 방법·절차 | ③ | 기한 == API `mgsc_mgop_rcpd_bgd/_edd` |
| 10 | 정정 해석 (what moved, how the D-day shifted) | all | before/after both parse; every model change must be backed by a `3. 정정사항` row |

Plus a **citation gate on every field**: the model returns a verbatim quote, the package locates its
character span in the stored snapshot, and an unlocatable quote is `span_unresolved` and blocked.
Gates are judged against evidence the model never saw (본문 labels + the stored API detail row).

**An API-backed gate is also an identity check.** ②'s 4 remaining failures were 정정 filings paired to
the wrong 사채 — a defect no other layer sees (deferred as `D1`).

## Event and Version States

- **철회 is a first-class state, detected deterministically from one `3. 정정사항` row shape — not from
  the keyword.** Measured: over 1,282 정정사항 rows in 328 ①/③ documents the word `철회` appears in 14
  정정 후 cells and only **4** are withdrawals (**71 % keyword false-positive rate**); the row-shape
  detector generalises to ② unchanged — over 808 ② 본문 / 4,627 rows it accepts 9 of 10 and **all 9 are
  withdrawals**. Today: **15 distinct withdrawal filings (① 6, ② 9)**, 11 withdrawn events blocked.
  A withdrawn ① renders **"이 유상증자는 철회되었습니다"** instead of a cancelled countdown.
- **A withdrawn CB keeps its detail row and OpenDART blanks all 46 fields to `-`.** The completeness
  rule blocks that as *silence*; only the 정정사항 row turns it into a stated withdrawal with a span.
  **A blank row is not proof of a withdrawal** (비트플래닛 `20260616000274` is blank and is not one).
- **`추후결정` is `tbd`, not missing** — a schedule suspended by a 정정 is an *extracted* value with a
  verified span and null dates; the exposed value is structurally `None`, so a superseded date cannot
  leak (경남제약 `20260623000409`, 에이전트AI `20260619000455`).
- Other stored states: `no_detail`, `incomplete_api_row` (파이온엑스 `20260722000285` states 38.45 %
  dilution with no 전환청구기간), `no_document`, `warrant_conflict`, `detail_conflict`,
  `event_key_collision`, `hint_split_evidence`, `hint_duplicate`.
- **② 해외/USD rule:** exposable iff the KRW fields parse, never on `ovis_*` (헝셩그룹
  `20260213002703`, HKD, passes on its KRW values).

## The Exposure Contract (durable P2 → P3 boundary)

An **event** is exposable iff it is not suppressed, not withdrawn and carries no blocking flag
(`warrant_conflict`, `detail_conflict`, `event_key_collision`, `hint_split_evidence`). A **field** is
renderable iff its gate verdict is `passed` or `tbd`. Four verdicts exist —
`passed` / `failed(code)` / `tbd` / `not_evaluable(code)` — **a skipped check is never a pass**, and a
gate that compared nothing is `not_evaluable`. A stored API detail row is a reference value **for the
current version only**: a superseded reading is `not_evaluable(superseded_api_reference)`, never a
failure.

Verified read-only over the live corpus at the P2 review: **409 renderable field instances, 0 of them
outside `passed`/`tbd`; 0 `tbd` fields leaking a value; 0 exposable events in a non-exposable state.**

Field verdicts today (`gates run`, byte-identical across two runs): **649 rows — 566 passed / 4 tbd /
14 failed / 65 not_evaluable**. P3 filters in SQL on the persisted columns and makes **no OpenDART
call in the request path**.

## Collection Constraints

P1's three measured behaviours stand (one row per event newest-version-only; the `bgn_de`/`end_de`
window filters on the **original** 접수일 — a correction-date probe returned `[]` in 40/40 samples;
`rcept_no` mutates), and so does the resulting key: **`(corp_code, report_subtype,
original_rcept_dt)`**, every observed `rcept_no` a version, every version snapshotted.

Two P2 corrections to that section:

1. **The pairing fallback is "nearest earlier ORIGINAL"**, not nearest earlier filing — otherwise a
   correction chain splits into one event per correction. Discovery widens corp-scoped (no 3-month
   cap) and stores an explicit `pairing_method` per version.
2. **The event key is not injective** — ~8 % of 2026 events collide (same-day double filings,
   concurrent events of one corp). Keep the detector (2+ detail rows on one key) and the rule
   **never suppress an event whose detail rows disagree**.

Discovery covers originals + `[기재정정]` + `[첨부정정]` + `[첨부추가]` + `[정정명령부과]`.

### 정정 pairing, as implemented

`pairing_method` is the pair **(nearest-earlier-original) + (본문 `<CORRECTION>` 최초제출일 verdict)**,
stored with `hint_status` and a `pairing_note`; the collector's value is never overwritten. Measured
effect of adding the 본문 arm: `*_ambiguous` 145 → 66, 46 of 99 unpaired corrections identified, 9
collided keys proven to hold 2+ events.

`기타 투자판단에 참고할 사항` remains the most-corrected 항목 and is free text, so **정정 diffing cannot
be reduced to comparing structured fields**: the prose is re-extracted and re-diffed on every
correction, and every model-stated change is checked against the deterministic `3. 정정사항` rows.
That deterministic check is **derived data** — it is re-scored from stored records at **0 LLM calls /
0 OpenDART requests** (`python -m mijual.extract recheck`, idempotent).

## Measured Reading Quality

- **Spans land.** 292 of 293 model quotes located in the stored snapshot at first measurement
  (99.7 %, 290 byte-faithful); corpus-wide today only **5** rows are blocked `span_unresolved`.
- **Extraction accuracy (cross-model judged — see `qa` for the method and the provenance):** 98.6 %
  strict on the frozen 344-row sample; **정정-해석 recall proxy 88.70 %** (177 deterministic 정정사항
  rows, 20 uncovered, 0 unsupported of 157 model changes, 45 records with a parsed table). The earlier
  "85.3 % as stored" figure was a matcher artifact and is **superseded** (P2.F4).
- **Three data facts worth carrying:** N68's five `lapse_mismatch` filings are **issuer table errors**
  (a 총계 smaller than its own first column) — the exposed contract is "발행사 기재 불일치", never a
  silent reconciliation; `option_schedule` dates need a `date_basis` marker; `rcept_no
  20250930000508`'s stored `corp_name` (풍전약품) disagrees with its 본문 header (에스씨엠생명과학) — a
  DART master artifact affecting display only.

## The 소멸가치 Method (data side)

- ▷ 증서 이론가치 = **`확정발행가 × 할인율 / (1 − 할인율)`**, derived by inverting the filing's own
  발행가 산식 (DART-only — there is no price feed). The identity holds for both the 1차 (cum-rights,
  whose `증자비율` term *is* the 권리락 adjustment) and the 2차 (ex-rights) formula, so no formula
  branch is needed; a filer who omits the 증자비율 term gives the band's lower edge (`× 1/(1+배정비율)`).
- 소멸 증서 수 = **발행 증서 − 증서 청약**, never 최초배정 − 청약 (단수주 was never issued as a 증서,
  and the filer's own 실권주 cell disagrees in **5 of 31** filings).
- **A lapse year is defined by the 증권발행실적보고서, not by the 주요사항보고서**: the 청약 lands 2–6
  months after the 결정, and only **10 of the 32** 2026 lapses were reachable from a 2026-filed corpus.

## API Constraints

P1's table stands (3-month `list.json` window without `corp_code`; `page_count` ≤ 100; 증권신고서
endpoints return `group[]`; `null` params must be dropped; status codes `000/013/100/101`; transient
503 → retry with backoff; `document.xml` returns a ZIP; `estkRs.rpt_rcpn` is version-stale; 사모 CB is
신고서-면제). Two updates:

- **Daily quota: 20,000 requests per key** (operator, corroborated by community documentation;
  ▷ the official page defers to a homepage notice). The `max_requests` ceiling stays anyway.
- **`cvbdIsDecsn` must be matched by exact parenthetical equality**, not substring: the same
  `pblntf_ty=B` stream carries 자기전환사채매도결정 / 만기전취득결정 / 매수선택권행사자지정 /
  신주인수권부사채권발행결정 / 교환사채권발행결정 (EB, out by D-1).

**Filters that are correctness requirements, not conveniences:** exclude 제3자배정 / 일반공모 /
주주우선공모 유증 (check 본문 `18.`; do not trust `ic_mthn` alone) and suppress 소규모합병 — publishing
either as a live right is a correctness bug.

## Environment / Secrets

| Name | Required | Purpose | Notes |
|---|---|---|---|
| `DART_API_KEY` | yes | OpenDART auth | gitignored `.env`, read in-process, never echoed, never in a cached filename or recorded URL |
| `GEMINI_API_KEY` ("changple5") | yes | reading layer (`gemini-3.7-flash`) | same handling; reaches only the SDK |
| `DATABASE_URL` | yes | Postgres (docker, host 5433) | corpus is re-collectable |

## Open Questions

- ▷ Meaning of `estkRs.일반사항.exstk/exprc/expd` (2/35 filled) — unneeded by any MVP field; answer
  only if it falls out for free.
- Pre-2026 `pifricDecsn` depth is uncollected (deferred `D3`); ②'s history reaches 2025-06 only.
- The 철회 detector's ③ generalisation has **no case in this corpus** — it is unit-tested on a
  constructed `회사합병 결정 → 회사합병 철회` row and untested against real data.
- `corp_cls=E` (기타) was never probed; KONEX was probed and adds **zero** exposable rights.
