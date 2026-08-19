---
doc_id: data
version: v0002
created_at: 2026-08-19T20:58:28+09:00
source: P1.REVIEW
summary: DART as the MVP data source: rights-type field matrix, extraction targets, version and 정정 constraints
previous: v0001_bootstrap
---

# Data

## Status

No database schema exists yet (P2 owns it). What **is** durable truth after P1: the upstream
source is characterised, measured, and its collection constraints are known. Facts below carry an
evidence `rcept_no` or a command; estimates are marked `▷`. Full per-field detail lives in the
phase artifact `docs/reference/dart/field-matrix.md` — this doc carries the parts P2/P3 must not
re-derive.

## Source of Record

**OpenDART (`https://opendart.fss.or.kr/api`) is the MVP's sole data source.** No scraping, no
vendor feed. Auth is a single API key, `DART_API_KEY`, kept in the gitignored repo-root `.env`,
read in-process, never printed into logs or artifacts.

Measured frame for every number in this doc: **2026-01-01 ~ 2026-08-18, KOSPI (`corp_cls=Y`) +
KOSDAQ (`K`)**, 1,002 distinct cached requests (`P1.S1`). KONEX/기타 is unmeasured.

| rights type | endpoints | 2026 event universe (measured) |
|---|---|---|
| ① 유증 신주인수권 | `piicDecsn` (주요사항보고서) · `estkRs` (증권신고서 지분증권) · `document` | 299 유상증자결정 reports / 260 corps, of which only **32 (11%) are 주주배정 계열** — the only ones issuing a 신주인수권증서 (▷ ~4–5/month) |
| ② CB 오버행 | `cvbdIsDecsn` · (`exbdIsDecsn` for EB, out of MVP) · `document` | CB **263 reports / 236 corps**; EB 20 |
| ③ 매수청구권 | `cmpMgDecsn` · `mgRs` · (siblings `stkExtrDecsn`, `cmpDvmgDecsn`, out of MVP) · `document` | 83 회사합병 reports, but **65 소규모합병 grant no 매수청구권** → **15–17 real events** (▷ ~2/month) |

## Field Tiers (how each field is obtained)

Every service field is exactly one of three tiers, because their costs differ by orders of magnitude:

| tier | meaning | reader |
|---|---|---|
| `API` | named JSON field from an OpenDART endpoint | deterministic |
| `본문-label` | absent from the API, present in the filing's 본문 XML as a **numbered, stably-labelled table row** (e.g. `8. 신주배정기준일`) | deterministic table parse |
| `본문-prose` | free narrative inside a 본문 section; wording drifts per filer | **LLM schema extraction + deterministic gate** |

Per-type shape, as measured:

- **① 유증 — mixed.** `piicDecsn` is a constant **19 keys** with no dates and no prices (no
  배정기준일 / 발행가액 / 청약일 / 납입일 / 증서 매매기간). `estkRs` recovers 배정기준일 `asstd`
  (**28/28** for 주주배정), 청약기일 `sbd`, 납입일 `pymd`, 발행가 `slprc`, 주관사 `인수인정보.actnmn`
  — but only when a 증권신고서 exists (사모/소액 제3자배정 is 면제). The **주요사항보고서 본문**
  (~6,000 chars) carries the rest as numbered labels — **10/10 target labels present in 9/9**
  sampled 주주배정 filings (evidence `20260724000546`, `20260618000108`, `20260811000481`).
  Only ~5 fields are genuinely prose.
- **② CB — near-fully structured.** 전환가액 `cv_prc`, 전환비율 `cv_rt`, 전환청구기간
  `cvrqpd_bgd/edd`, 오버행 주식수·비율 `cvisstk_cnt`/`cvisstk_tisstk_vs` all **47/47**; 리픽싱 floor
  `act_mktprcfl_cvprc_lwtrsprc` 36/47 (evidence `20260521000775`). **② can ship with zero LLM extraction.**
- **③ 매수청구권 — near-fully structured.** 반대의사 통지 접수기간 `mgsc_mgop_rcpd_bgd/_edd`
  **41/41**, 주주확정기준일 41/41, 합병일정 41/41; 매수 예정가격 `aprskh_plnprc` 15/83 and 행사기간
  `mgsc_aprskh_expd_bgd/_edd` 17/83 — **that low fill is semantic, not a data gap** (소규모·간이합병
  grants no right). Evidence `20260713000345`, `20260810000482`. **③ can also ship with zero LLM extraction.**

**Negative result to not re-discover:** `bdRs` (증권신고서 채무증권) is **not** a CB source — 사모 CB
is 신고서-면제; across 77 sampled rows the 지분 관련 사채 fields were 0/77 filled. For ② the
주요사항보고서 is the only source.

## Extraction Targets (the LLM's entire reading job for the MVP)

Ten fields, each with the deterministic gate that must pass before exposure:

| # | field | type | 본문 위치 | gate |
|---|---|---|---|---|
| 1 | 신주인수권증서 상장·매매기간 | ① | 24-라 | date order; between 배정기준일 and 청약일 |
| 2 | 청약 취급처 (대상자별 증권사 + 청약일) | ① | 24-다 | 청약일 == 본문 `11. 청약예정일` |
| 3 | 실권주 처리 방식 | ① | 24-나 | enum-ish: 일반공모 / 대표주관회사 인수 / 미발행 |
| 4 | 초과청약 조건 (비율) | ① | 24-나 3) | 0 < ratio ≤ 1; 배정주식수 × ratio arithmetic |
| 5 | 발행가액 산정방법 | ① | 24-가 | consistency vs 본문 `6.` |
| 6 | 리픽싱 세부 조건 | ② | 9. 전환가액 조정 | floor == API `act_mktprcfl_cvprc_lwtrsprc` |
| 7 | 콜·풋 세부 스케줄 | ② | 9-1. 옵션 | within 발행일 ~ 만기일 |
| 8 | 보호예수 / 전매제한 해제일 | ② | 19. + 기타 투자판단 | ≥ 발행일; cross-check `ex_sm_r` |
| 9 | 반대의사 통지 방법·절차 | ③ | 13. 주식매수청구권 | 기한 == API `mgsc_mgop_rcpd_bgd/_edd` |
| 10 | 정정 해석 (what moved, and how the D-day shifted) | all | `<CORRECTION>` 3. 정정사항 | before/after both parse; dates move monotonically |

Everything else is `API` or `본문-label`, i.e. deterministic — per the fixed rule that **all
calculation (금액 환산·D-day) is deterministic**; the AI only reads and speaks.

Prose drift is real and is what justifies the LLM here rather than a regex: the same fact appears as
`상장예정기간` / `매매기간`, `(5영업일)` / `(5거래일)`, with list numbering bleeding into the value, and
one filing (`20260811000481` 이렘) carrying two ranges.

## 본문 (`document` API) Parseability

`GET /api/document.xml?rcept_no=…` returns a ZIP holding **one** UTF-8 XML with `TABLE/TR/TD` markup,
`<SECTION-1>` / `<TITLE ATOC>` section markers and, on corrections, a `<CORRECTION>` element. 5/5
probed filings parsed; no HTML-viewer fallback is needed. Two size regimes:

- **주요사항보고서: 2,598–9,848 text chars** — one-shot LLM input, with numbered labels supporting a
  deterministic pre-parse. **This is where extraction lives for all three types.**
- **증권신고서: 615,780–1,867,597 text chars** — 100–300× larger; slice by `<TITLE>` section, never
  feed whole. ▷ Best treated as a confirmation / citation-span source, not the primary target.

The XML is character-addressable, so an extracted value can carry its 원문 인용 스팬 offset — which is
what the citation-span gate needs.

## Collection Constraints (binding on P2's collector)

Three measured behaviours of the 주요사항보고서 detail endpoints, each verified on multiple corps:

1. **One row per event, newest version only.** SKC's 3 유증 filings collapse to `20260512000196`;
   디모아's 6 to `20260625000227`. Superseded structured values are **unrecoverable from the API**.
2. **The `bgn_de`/`end_de` window filters on the ORIGINAL 접수일, not the correction's.** The
   correction-date single-day probe returned `[]` in **40/40** samples. → *A daily "yesterday's
   filings" poll driven by the detail endpoints silently misses every 정정.* Poll `list.json` for
   `[기재정정]` rows, then re-fetch the detail endpoint on the **original** filing's date window.
3. **`rcept_no` is not a stable key** — it mutates to the newest version (only 7/39 `estkRs.rpt_rcpn`
   values match today's `piicDecsn` rcept_no).

**→ Event key: `(corp_code, report_subtype, original_rcept_dt)`, with every observed `rcept_no`
recorded as a version and every version snapshotted at collection time.** Without snapshots there is
no old→new field diff, and the 정정 story — the product's whole point — cannot be told.

Corollary for serving: **the board must render from persisted snapshots, with no OpenDART call in the
request path** (transient upstream 503s are measured; the judged uptime window is 결격-grade — see
`operations`).

### 정정공시 pairing (validated method)

1. Fetch the correction's 본문, read `<CORRECTION>` → `1. 정정대상 공시서류` (subtype) and
   `2. 정정대상 공시서류의 최초제출일`.
2. Candidates = same `corp_code` + same 보고서 subtype from `list.json`.
3. Prefer `rcept_dt == 최초제출일`; otherwise nearest earlier.
4. Read the `3. 정정사항` table (항목 / 정정사유 / 정정 전 / 정정 후) as the authoritative what-changed list.

Measured over 40 corrections spanning all three types: **30/40 paired** (16 exact, 14 nearest-earlier;
the 10 misses have pre-2026 originals) and **40/40 carried a parseable 정정사항 table**. Caveats:
`최초제출일` is filer-entered and sometimes wrong (`20260429000902` declares 2022-08-01) — a hint, not
a key; a single event can carry a chain (디모아 filed 6 corrections against one 유증); `[첨부정정]` is
attachment-only and can be skipped.

**Diff targets that actually move:** 납입일, 신주 상장예정일, 발행가액 (①); 사채만기일, 납입일,
전환에 관한 사항, 옵션, 청약일, 전환가액, 전환청구기간 (②); 합병일정, **합병반대의사통지 접수기간**,
주식매수청구권 행사절차 (③). Cross-cutting, `기타 투자판단에 참고할 사항` is the single most corrected
항목 (11/40) and is free text — **so 정정 diffing cannot be reduced to comparing structured fields; the
prose block must be re-extracted and re-diffed on every correction.**

Worked example: `20260813001290` (에넥스) moved 납입일 8/13 → 9/14 and 상장예정일 8/31 → 9/30 — a
user's D-day would have shifted 32 days.

## API Constraints

| # | constraint |
|---|---|
| 1 | `list.json` without `corp_code` allows a **3-month window only** (`status 100`) |
| 2 | `list.json`: `page_count` max 100, page via `page_no` to `total_page`; `pblntf_ty=B` 주요사항보고, `C` 발행공시 |
| 3 | 증권신고서 endpoints (`estkRs`, `bdRs`, `mgRs`, `dvRs`, `extrRs`) return **`group[]` of `{title, list}`**, not a flat `list` — a 주요사항보고서-shaped client silently reads 0 rows |
| 4 | `null` query params must be **dropped**, not serialized (`corp_code=None` → `status 100`) |
| 5 | Status codes: `000` 정상, `013` 조회된 데이타 없음 (endpoint real + key valid), `100` 부적절한 값, `101` 잘못된 URL |
| 6 | **Transient HTTP 503** under sustained calling → retry with backoff; 6 concurrent threads sustained ~1,000 requests without a ban |
| 7 | `document.xml` returns a ZIP (magic `PK`); errors come back as a non-ZIP XML body |
| 8 | `estkRs.일반사항.rpt_rcpn` joins 발행공시 ↔ 주요사항보고, but is **version-stale** (7/39 match) |
| 9 | 사모 CB/EB is 증권신고서-면제 → for ② the 주요사항보고서 is the only source |
| 10 | ▷ Daily call quota unmeasured; ~1,002 requests in one session drew no quota error. Confirm before P2's backfill |

**Filters that are correctness requirements, not conveniences:** exclude 제3자배정/일반공모 유증 (no
증서 issued — check 본문 `18. 신주인수권양도여부`, do not trust `ic_mthn` alone), and suppress
소규모합병 (`mg_stn` + `aprskh_*` presence) — publishing either as a live right is a correctness bug.

## Environment / Secrets

| Name | Required | Purpose | Notes |
|---|---|---|---|
| `DART_API_KEY` | yes | OpenDART auth | gitignored `.env`, read in-process, never echoed or committed |
| Gemini credential ("changple5") | yes (P2) | application LLM (reading + speaking layers) | not in this repo; obtained from the operator and stored gitignored beside `DART_API_KEY` |

## Open Questions

- ▷ Published daily OpenDART call quota (unmeasured) — confirm before P2's backfill.
- ▷ Whether KONEX / 기타 (`corp_cls=N/E`) changes any coverage conclusion (whole survey is KOSPI+KOSDAQ).
- ▷ Meaning of `estkRs.일반사항.exstk/exprc/expd` (2/35 filled); not needed by any MVP field.
- ▷ Whether `주주우선공모증자` issues a 증서 (1 case, `20260807000339`) — verify from 본문 `18.`.
- ② needs a CB backfill to **≥ 2025-06** to show any urgent 오버행 countdown: 0 of 267 cached
  2026-filed CB events have a 전환청구 개시일 before 2027-01-15 (▷ ~300–600 requests, ~half a day).
