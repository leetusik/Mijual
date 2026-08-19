# DART 공시 필드 매트릭스 — MVP 권리 3종

**Event type × field × {structured API / 본문 label / 본문 prose (LLM extraction)}**

| | |
|---|---|
| Produced by | `P1.S1` (DART OpenAPI spike), 2026-08-19 |
| Purpose | Fixes the extraction-target list for handoff §3.6 layer 1 (AI가 '읽기'), and feeds the `P1.S2` MVP rights-scope decision |
| Method | Live OpenDART calls against real 2026 filings; **1,002 distinct cached API requests** (`scripts/spike/samples/`), 59 of them `document` 본문 ZIPs |
| Sample frame | 2026-01-01 ~ 2026-08-18, **KOSPI (`corp_cls=Y`) + KOSDAQ (`corp_cls=K`)** — 3,820 `pblntf_ty=B` (주요사항보고) rows and 3,843 `pblntf_ty=C` (발행공시) rows |
| Reproduce | `python3 scripts/spike/survey.py {rights1\|rights2\|rights3\|population\|labelscan\|docprobe}` · `python3 scripts/spike/corrections.py 40` |

**Reading the source column.** Every field is classified into exactly one of three tiers, because the cost of each is very different:

| tier | meaning | who reads it |
|---|---|---|
| **`API`** | returned as a named JSON field by an OpenDART endpoint | deterministic |
| **`본문-label`** | not in the API, but sits in the filing's 본문 XML as a **numbered, stably-labelled table row** (e.g. `8. 신주배정기준일`) | deterministic table parse — LLM optional |
| **`본문-prose`** | free-text narrative inside a 본문 section; wording and structure vary per filer | **schema-based LLM extraction (§3.6 layer 1) + 결정론 게이트 (layer 2)** |

Facts carry an evidence `rcept_no` (or a command). Estimates and inferences are marked `▷`. Sample counts are stated as measured, never rounded up.

---

## 0. Headline answers (Q1 / Q2 / Q3)

**Q1 — does `estkRs.asstd` (배정기준일) populate for 주주배정 유상증자, and does anything structured expose 신주인수권증서 상장·매매기간?**

- **배정기준일: YES, 100%.** Of the sampled 증권신고서(지분증권) filings whose `증권의종류.slmthn` contains **주주배정**, **28 / 28** carry a populated `일반사항.asstd`. Also 100% populated in the same sample: `sbd` 청약기일, `pymd` 납입일, `slprc` 발행가, `stkcnt` 발행주식수, `slmthn` 증자방식, `인수인정보.actnmn` 주관·인수 증권사. Evidence: `20260814004100` (계양전기), `20260318001009` (이뮨온시아), `20260427000469` (SKC), `20260512000558` (티엘비), `20260521000770` (경남제약) — full list in `scripts/spike/samples/_summary/survey_rights1.json`.
- **신주인수권증서 상장·매매기간: NO — no structured field anywhere.** Not in `piicDecsn` (19 keys), not in `estkRs` (6 groups, 34 distinct field ids). It lives as **본문-prose**: `라. 신주인수권에 관한 사항 → 3) 신주인수권증서 상장예정기간 : 2026년 08월 19일 ~ 2026년 08월 25일` (`20260724000546`, 계양전기).
- **But the surprise that changes the cost estimate:** the 유증 **주요사항보고서 본문** carries almost everything `piicDecsn` drops, as *numbered labelled table rows*, in a **~6,000-character** document. A label scan over 9 real 주주배정 filings found **10 / 10 target labels present in 9 / 9 filings** (§1.3). ① is therefore *not* uniformly "LLM-heavy" — its skeleton is deterministic, and only ~5 prose fields need the LLM.

**Q2 — how to pair a `[기재정정]` filing with the original, and is there a machine-readable "what changed" block?**

- **YES, there is a what-changed block.** The 정정 filing's 본문 opens with a `<CORRECTION>` element containing `1. 정정대상 공시서류`, `2. 정정대상 공시서류의 최초제출일`, and a **`3. 정정사항` table with columns 항 목 / 정정사유 / 정 정 전 / 정 정 후**. Parsed successfully in **40 / 40** sampled corrections. A field-by-field re-fetch diff is *not required* to know what moved.
- **Pairing works, with a caveat: 30 / 40 paired (16 by exact `최초제출일`, 14 by nearest-earlier same-corp same-subtype).** The 10 unpaired ones have an original outside the 2026 list window. `최초제출일` is **filer-entered and not always trustworthy** (e.g. `20260429000902` 우성머티리얼스 declares `2022년 08월 01일`, while the real predecessor is `20260416000330`), so treat it as a *hint* and fall back to nearest-earlier.
- **Critical collection consequence: the structured record of the superseded version is unrecoverable from the API.** A 주요사항보고서 detail endpoint returns **one row per event = the newest version only** (§4.2). Old-vs-new structured diffing therefore requires *snapshotting at collection time*; without a snapshot, the only diff source is the 정정사항 table.

**Q3 — is the `document` API (본문) parseable enough to feed schema-based extraction?**

**YES, comfortably.** 5 / 5 probed filings returned a valid ZIP holding a **single UTF-8 XML** member with HTML-like `TABLE/TR/TD` markup plus `<SECTION-1>` / `<TITLE ATOC=...>` semantic section markers. No HTML-viewer fallback is needed. Size splits into two regimes (§5).

---

## 1. ① 유상증자 신주인수권 (killer type)

**Endpoints:** `piicDecsn` (주요사항보고서 유상증자결정) · `estkRs` (증권신고서 지분증권) · `document` (본문).
**2026 universe (measured):** 299 distinct 유상증자결정 reports across 260 corps — of which only **32 (11%) are 주주배정 계열** (`주주배정후 실권주 일반공모` 29, `주주배정증자` 3) plus 1 `주주우선공모증자`; the other 252 are `제3자배정증자` and 14 `일반공모증자`. **신주인수권증서 is only issued by the 주주배정 계열 → the ① event universe is ~32 events in 7.5 months (▷ ~4–5/month).**

### 1.1 The §3.6 service-critical fields

| 서비스 필드 | source | endpoint.field / 본문 위치 | evidence `rcept_no` |
|---|---|---|---|
| **신주배정기준일** | `API` (증권신고서) + `본문-label` | `estkRs.일반사항.asstd` · 본문 `8. 신주배정기준일` | `20260814004100` / `20260724000546` |
| **1주당 신주배정주식수 (배정비율)** | `본문-label` only | 본문 `9. 1주당 신주배정주식수` (`0.2314082845`) | `20260724000546` |
| **발행가액 (예정/확정) + 확정예정일** | `API` (증권신고서) + `본문-label` | `estkRs.증권의종류.slprc` (3,200) · 본문 `6. 신주 발행가액 → 확정발행가 / 예정발행가 / 확정예정일` | `20260814004100` / `20260724000546` |
| **청약일 (구주주 / 우리사주 / 일반공모)** | `API` (증권신고서) + `본문-label` | `estkRs.일반사항.sbd` (`2026년 09월 03일 ~ 2026년 09월 04일`) · 본문 `11. 청약예정일` (대상자별 시작/종료일) | `20260814004100` / `20260724000546` |
| **납입일** | `API` + `본문-label` | `estkRs.일반사항.pymd` · 본문 `12. 납입일` | `20260814004100` / `20260724000546` |
| **신주 상장예정일** | `본문-label` | 본문 `16. 신주의 상장예정일` | `20260724000546` |
| **신주인수권 양도여부 / 증서 상장여부** | `본문-label` | 본문 `18. 신주인수권양도여부`, `- 신주인수권증서의 상장여부` | `20260724000546` |
| **증서 매매 중개 금융투자업자** | `본문-label` | 본문 `18. - 신주인수권증서의 매매 및 매매의 중개를 담당할 금융투자업자` (케이비증권) | `20260724000546` |
| **🔴 신주인수권증서 상장·매매기간** | **`본문-prose`** | 본문 `24. 기타 투자판단에 참고할 사항 → 라. 신주인수권에 관한 사항 → 3) 신주인수권증서 상장예정기간` | `20260724000546` (`2026-08-19 ~ 08-25`), `20260618000108` (`06-05 ~ 06-11`), `20260720000067` (`07-06 ~ 07-10`) |
| **🔴 청약 취급처 (대상자별 증권사 + 청약일)** | **`본문-prose`** (표 형태이나 절 제목·행 구성이 filer마다 다름) | 본문 `24. → 다. 청약취급처` (청약대상자 / 청약취급처 / 청약일) | `20260724000546` |
| 대표주관회사 | `API` + `본문-label` | `estkRs.인수인정보.actnmn` + `.udtmth` (잔액인수) · 본문 `17. 대표주관회사` | `20260814004100` / `20260724000546` |
| **🔴 실권주 처리 방식** | **`본문-prose`** | 본문 `13. 실권주 처리계획` is a *cross-reference* (`24. 기타 투자판단에 참고할 사항- 나. 신주의 배정방법 참조`) → the real content is prose in `24-나` | `20260724000546` |
| **🔴 초과청약 조건** | **`본문-prose`** | 본문 `24-나 3) 초과청약` (초과청약비율 배정 신주 1주당 0.2주 = 20%) | `20260724000546` |
| 발행가액 산정방법 (1차/2차/확정 산식) | `본문-prose` | 본문 `24-가. 신주발행가액 산정방법` | `20260724000546` |
| 우리사주조합 우선배정비율 | `본문-label` | 본문 `10. 우리사주조합원 우선배정비율 (%)` (20.0) | `20260724000546` |
| 공매도 금지기간 | `API` + `본문-label` | `piicDecsn.ssl_at/ssl_bgd/ssl_edd` · 본문 `22.` | `20260724000546` |
| 인수인 수수료·인수방법 | `API` | `estkRs.인수인정보.udtprc`, `.udtmth` | `20260814004100` |
| 자금조달 목적 | `API` | `piicDecsn.fdpp_*` · `estkRs.자금의사용목적.se/amt` | `20260724000546` / `20260814004100` |

🔴 = a §3.6 "서비스가 팔아야 하는" field that has **no structured source** — the LLM extraction targets.

### 1.2 `piicDecsn` is confirmed thin (F2 re-verified)

Constant 19 keys across 49 sampled reports; nothing date- or price-bearing:
`nstk_ostk_cnt`, `nstk_estk_cnt`, `fv_ps`, `bfic_tisstk_ostk`, `bfic_tisstk_estk`, `fdpp_fclt/bsninh/op/dtrp/ocsa/etc`, **`ic_mthn` (증자방식 — 100% filled, the 주주배정 filter)**, `ssl_at/ssl_bgd/ssl_edd`.
**No 배정기준일, no 발행가액, no 청약일, no 납입일, no 상장예정일, no 증서 매매기간.** Evidence: `20260413002472`, `20260724000546`.

`estkRs` recovers much of it — but **only when a 증권신고서 exists**. Measured: 44 original + 153 기재정정 + 96 발행조건확정 `증권신고서(지분증권)` rows across 85 corps in 2026. 사모/소액 제3자배정 유증 is 신고서-면제, so for those `estkRs` is empty and the 본문 is the *only* source.

`estkRs.일반사항.exstk / exprc / expd` filled in only 2 / 35 rows (`20260518000304`: 보통주 / 10,500 / —). ▷ Meaning unresolved; not needed by any §3.6 field. `estkRs.일반청약자환매청구권.*` was 0 / 35 filled.

### 1.3 본문 label stability — the load-bearing measurement

`python3 scripts/spike/survey.py labelscan 10`, over the 9 주주배정-type filings found among the sampled corps:

| measurement | result |
|---|---|
| 10 target numbered labels (`신주배정기준일`, `1주당 신주배정주식수`, `청약예정일`, `납입일`, `실권주 처리계획`, `신주의 상장예정일`, `대표주관회사`, `신주인수권양도여부`, `신주인수권증서의 상장여부`, `신주인수권증서의 매매…`) | **present in 9 / 9 filings, 10 / 10 each** |
| `신주인수권증서 상장(예정)기간` recoverable from prose | **8 / 9** — missing only in `20260625000227` (디모아), a terse 2,598-char 정정 that restates only changed items |
| document size | 2,598 – 8,664 characters of text |

Evidence set: `20260724000546` 계양전기, `20260618000108` 뉴인텍, `20260811000481` 이렘, `20260625000227` 디모아, `20260512000196` SKC, `20260707000087` 형지I&C, `20260709000212` 한솔테크닉스, `20260720000067` 한화솔루션, `20260804000486` 휴림에이텍.

**Phrasing drift is real and is exactly where the LLM earns its place.** Observed variants of the same fact: `상장예정기간`, `매매기간`, `(5영업일간)`, `(5거래일간)`, list numbering bleeding into the captured value (`… 2026년 08월 25일4`), and one filing (`20260811000481` 이렘) carrying **two** date ranges. A regex is brittle here; a schema-based extraction with a **date-order + within-청약일정 range gate** (§3.6 layer 2) is the right shape.

**Feasibility signal for `P1.S2`: ① is MIXED — deterministic skeleton + ~5 prose fields. Smallest event universe (~32 in 7.5 months), highest user value, moderate (not extreme) extraction cost.**

---

## 2. ② CB · EB 오버행

**Endpoints:** `cvbdIsDecsn` (전환사채권 발행결정) · `exbdIsDecsn` (교환사채권 발행결정) · `bdRs` (증권신고서 채무증권) · `document`.
**2026 universe (measured):** CB **263 distinct reports / 236 corps**; EB **20 reports / 20 corps**. By far the largest of the three types.

### 2.1 Structured coverage is excellent

| 서비스 필드 | source | field | fill | evidence |
|---|---|---|---|---|
| 전환가액 | `API` | `cvbdIsDecsn.cv_prc` | 47/47 | `20260521000775` (4,433) |
| 전환비율 | `API` | `cv_rt` | 47/47 | `20260521000775` |
| **전환청구기간 (시작/종료)** | `API` | `cvrqpd_bgd` / `cvrqpd_edd` | 47/47 | `20260521000775` (2027-05-29 ~ 2031-04-29) |
| **오버행 규모 — 전환 발행주식수 / 총수 대비 비율** | `API` | `cvisstk_cnt`, `cvisstk_tisstk_vs` | 47/47 | `20260521000775` (2,255,808주 / **15.65%**) |
| **리픽싱 최저 조정가액 + 근거** | `API` | `act_mktprcfl_cvprc_lwtrsprc`, `…_bs` | 36/47 | `20260521000775` (3,103 / `발행당시 전환가액의 70% 이상, 액면가 이상`) |
| 사채 종류·회차·권면총액 | `API` | `bd_knd`, `bd_tm`, `bd_fta` | 47/47 | `20260521000775` |
| 표면/만기 이자율, 만기일 | `API` | `bd_intr_ex`, `bd_intr_sf`, `bd_mtd` | 46–47/47 | `20260521000775` |
| 청약일 / 납입일 | `API` | `sbd`, `pymd` | 46–47/47 | `20260521000775` |
| 발행방법 (사모/공모) | `API` | `bdis_mthn` | 47/47 | `20260521000775` (사모) |
| 교환가액 / 교환비율 / 교환청구기간 / 교환대상 | `API` | `exbdIsDecsn.ex_prc`, `ex_rt`, `exrqpd_bgd/edd`, `extg`, `extg_stkcnt`, `extg_tisstk_vs` | 19/20 | `20260608000384` (21,000원, 2026-07-16 ~ 2029-05-16, 298,000주, 2.24%) |
| 교환가액 결정방법 | `API` (long text) | `ex_prc_dmth` | 19/20 | `20260608000384` |
| **🔴 리픽싱 세부 조건 (조정 사유·산식·주기)** | **`본문-prose`** | 본문 `9. 전환에 관한 사항 → 전환가액 조정에 관한 사항` | `20260521000775` |
| **🔴 콜·풋 세부 (조기상환청구권 / 매도청구권)** | **`본문-prose`** | 본문 `9-1. 옵션에 관한 사항` — free text, e.g. `[조기상환청구권(Put Option)] … 발행일로부터 1년 6개월이 되는 2027년 11월 29일 및 이후 매 3개월…` | `20260521000775` |
| **🔴 보호예수 / 전매제한 해제 스케줄** | **`본문-prose`** | 본문 `19. 제출을 면제받은 경우 그 사유` + `기타 투자판단에 참고할 사항`; `cvbdIsDecsn.ex_sm_r` carries the gist as long text (`사모발행에 의한 1년간 거래단위의 분할 및 병합금지`) | `20260521000775` |

`rmislmt_lt70p` was 0/47 filled; `ovis_*` (해외발행) filled only for genuine offshore issues (`20260401002847`, HD한국조선해양, USD/싱가포르거래소).

### 2.2 `bdRs` is **not** the CB source — an important negative result

`증권신고서(채무증권)` covers 공모 회사채, not 사모 CB. Across 77 sampled `bdRs.일반사항` rows, `estk_exstk / estk_exrt / estk_exprc / estk_expd` (지분 관련 사채 필드) were **0 / 77 filled** and `drcb_at` was `N` in 77/77 — plain 무보증사채 (`20260319001244`). Meanwhile `cvbdIsDecsn.bdis_mthn` reads `사모` in the overwhelming majority, with `ex_sm_r` explicitly saying `사모 전환사채 발행으로 인한 증권신고서 제출 면제`.
**→ For ②, the 주요사항보고서 is the source of truth; do not build the pipeline expecting a 증권신고서.**

**Feasibility signal for `P1.S2`: ② is the MOST DETERMINISTIC and has the LARGEST event universe.** 오버행 % (`cvisstk_tisstk_vs`), 전환청구 개시일 (`cvrqpd_bgd`) and 리픽싱 floor come straight out of the API. LLM is needed only for the 콜·풋 / 리픽싱-세부 / 보호예수 narrative.

---

## 3. ③ 매수청구권 (합병 등)

**Endpoints:** `cmpMgDecsn` (회사합병결정) · `mgRs` (증권신고서 합병) · siblings `stkExtrDecsn` (주식교환·이전), `cmpDvmgDecsn` (분할합병) · `document`.
**2026 universe (measured):** 83 distinct 회사합병 reports across 84 corps — but **65 are `mg_stn = 소규모합병`** and only 18 are `해당사항없음` (i.e. a full 합병). Matching that, `aprskh_plnprc` (매수 예정가격) is filled in **15 / 83** and `mgsc_aprskh_expd_bgd` (행사기간 시작일) in **17 / 83**. **This low fill rate is semantic, not a data gap: 소규모·간이합병 grants no 주식매수청구권.** The real ③ universe is ~15–17 events in 7.5 months (▷ ~2/month) — the smallest of the three.

Two denominators appear below and they come from two different passes — do not average them: **`/83`** = the full-population pass (every corp with a 2026 회사합병결정 filing); **`/41`** = the 35-corp field-survey pass. Both are stated as measured.

| 서비스 필드 | source | field | fill | evidence |
|---|---|---|---|---|
| **매수청구 예정가격** | `API` | `cmpMgDecsn.aprskh_plnprc` | 15/83 (all 매수청구-bearing) | `20260713000345` (5,649원, 세기상사) |
| **매수청구 행사기간** | `API` | `mgsc_aprskh_expd_bgd` / `_edd` | 17/83 | `20260713000345` (2026-07-07 ~ 07-27) |
| **🟢 합병 반대의사 통지 접수기간** | `API` | `mgsc_mgop_rcpd_bgd` / `_edd` | **41/41** | `20260810000482` (2026-08-26 ~ 09-09) |
| 주주확정기준일 | `API` | `mgsc_shddstd` | 41/41 | `20260810000482` |
| 주주총회 예정일 | `API` | `mgsc_gmtsck_prd` | 7/41 | `20260713000345` |
| 합병계약일 / 합병기일 / 합병등기예정일 | `API` | `mgsc_mgctrd`, `mgsc_mgdt`, `mgsc_mgrgsprd` | 41/41 | `20260810000482` |
| 채권자 이의제출기간 | `API` | `mgsc_cdobprpd_bgd` / `_edd` | 41/41 | `20260810000482` |
| 합병신주 상장예정일 | `API` | `mgsc_nstklstprd` | 8/41 | `20260626000005` |
| 합병 방식·비율·목적 | `API` | `mg_mth`, `mg_stn`, `mg_rt`, `mg_rt_bs`, `mg_pp` | 41/41 | `20260810000482` |
| 매수대금 지급시기·지급방법 | `API` (long text) | `aprskh_pym_plpd_mth` | 7/41 | `20260713000345` |
| 매수청구 관련 계약 해제조건 | `API` (long text) | `aprskh_ctref` | 7/41 | `20260713000345` |
| 매수청구 기간·가격 (증권신고서 측) | `API` | `mgRs.일반사항.aprskh_pd_bgd/_edd`, `aprskh_prc` | 7/7 | `20260713000459` (대한항공·아시아나, 2026-08-12 ~ 09-01, 7,030원) |
| **🔴 반대의사 통지 방법·절차 (어디에·어떻게 접수)** | **`본문-prose`** | 본문 `13. 주식매수청구권에 관한 사항 - 행사절차, 방법, 기간, 장소` | seen changing in `20260730000178` (한중엔시에스) 정정사항 |
| 매수청구권 미부여 사유 (소규모합병) | `본문-prose` | 본문 `18. 기타 투자판단과 관련한 중요사항` | `20260513000254` (SGA솔루션즈) |

🟢 = **better than §3.6 assumed**: the 반대의사 통지 **기한** is fully structured (41/41). Only the 방법·절차 narrative needs the LLM.

Sibling `stkExtrDecsn` (주식교환·이전) mirrors the shape — `aprskh_plnprc`, `extrsc_aprskh_expd_bgd/_edd`, `aprskh_lmt` (청구권 상실 조건) — evidence `20260522000296` (현대지에프홀딩스·현대홈쇼핑). ▷ If ③ ships, 분할합병·주식교환 should be treated as the same rights type with a different endpoint, not a new type; that roughly doubles the event universe at low marginal cost.

**Feasibility signal for `P1.S2`: ③ is ALMOST FULLY STRUCTURED but has the SMALLEST universe (~15–17 events).** Cheapest to build, thinnest to demo. Requires the `mg_stn` / `aprskh_*`-presence filter to avoid publishing 소규모합병 as if it granted a 매수청구권.

---

## 4. 정정공시 (기재정정) — pairing method and diff targets

### 4.1 Pairing method (validated)

**Discovery.** `list.json` `report_nm` prefix `[기재정정]` (skip `[첨부정정]`, which is attachment-only). 2026 KOSPI+KOSDAQ volume: 654 `[기재정정]주요사항보고서(유상증자결정)`, 373 CB, 83 회사합병 — corrections are *more numerous than originals* (252 유상증자 originals vs 654 corrections).

**Recommended algorithm** (as implemented in `scripts/spike/corrections.py`):

1. Fetch the correction's 본문 and read the `<CORRECTION>` element →
   `1. 정정대상 공시서류` (report subtype) and `2. 정정대상 공시서류의 최초제출일`.
2. Candidate set = same `corp_code` + same 보고서 subtype (the parenthesised part of `report_nm`) from `list.json`.
3. Prefer the candidate whose `rcept_dt` **equals 최초제출일**; otherwise take the **nearest earlier** `rcept_dt`.
4. Read the `3. 정정사항` table (항 목 / 정정사유 / 정 정 전 / 정 정 후) for the authoritative what-changed list.

**Measured over 40 corrections spanning all 3 rights types:** **30 / 40 paired** (16 exact `최초제출일`, 14 nearest-earlier); the 10 misses all have originals filed before 2026-01-01, i.e. outside the sampled list window, not a method failure. **40 / 40 carried a parseable 정정사항 table.**

**Caveats.**
- `최초제출일` is filer-entered and sometimes wrong or stale (`20260429000902` declares 2022-08-01; `20260612000630` declares 2024-11-07). Hint, not key.
- A single event can carry a **chain** of corrections; each correction's header points at the *first* submission, not at its immediate predecessor. 디모아 filed **6** corrections against one 유증 (`20260128000329 → 20260202000757 → 20260225003668 → 20260312001076 → 20260527000288 → 20260625000227`).
- `rm="정"` on the superseded original (F5) is an additional handle but was not needed.
- ▷ The 본문 sometimes contains an explicit revision-history table (`제출일자 / 문서명 / 비고`, e.g. `20260702000277` 유진스팩10호) that names every version — a richer pairing source when present, but it is not universal.

### 4.2 Version semantics of the structured API (**load-bearing for P2's collector**)

Three measured behaviours, each verified on multiple corps:

1. **One row per event, newest version only.** SKC filed 3 유증 주요사항보고서 (`20260226005077` original → `20260403003142` → `20260512000196`); `piicDecsn` returns exactly **one** row: `20260512000196`. 디모아's 6 filings collapse to `20260625000227`. 뉴인텍 has *two* separate 유증 events and returns exactly two rows.
2. **The `bgn_de`/`end_de` window filters on the report's ORIGINAL 접수일, not the correction's.** 에넥스 (`00139764`): original 2026-07-21, correction `20260813001290`. Querying `20260701~20260731` returns the row; querying `20260801~20260818` returns `013 조회된 데이타가 없습니다`. Across the 40-correction sample, the **correction-date single-day probe returned `[]` in every case**, while the original-date probe returned the record (carrying the *latest* `rcept_no`).
   **→ A daily "yesterday's filings" poll driven by the detail endpoints will silently MISS every 정정.** The collector must poll `list.json` for `[기재정정]` rows and then re-fetch the detail endpoint using the *original* filing's date window.
3. **`rcept_no` is not a stable primary key.** It changes to the newest version. Only 7 / 39 `estkRs.일반사항.rpt_rcpn` values matched the `rcept_no` that `piicDecsn` currently returns for the same corp — `rpt_rcpn` points at the 주요사항보고서 version that was current *when the 증권신고서 was filed* (e.g. 뉴인텍 `rpt_rcpn=20260514000551`, while `piicDecsn` now returns `20260618000108`). ▷ Suggested stable event key for P2: `(corp_code, report_subtype, original_rcept_dt)`, with every observed `rcept_no` recorded as a version.
   **→ The superseded version's structured values are unrecoverable. P2 must snapshot each version at collection time if it wants field-level old→new diffs beyond the 정정사항 table.**

### 4.3 Diff-target field list (what actually changes)

Frequency of the `항 목` column across the 40 sampled corrections (`scripts/spike/samples/_summary/corrections.json`):

| rights type | fields that actually move | D-day impact |
|---|---|---|
| **① 유증** | **납입일 (4)**, **신주의 상장예정일 (4+2)**, **신주 발행가액 / 예정발행가 (2+1)**, 기준주가, 신주의 종류와 수, 자금조달의 목적, 신주권교부예정일, 신주의 배당기산일, `기타 투자판단에 참고할 사항` (4) | ✅ direct — 청약일·납입일 shift the user's countdown; 발행가 shifts the 환산 금액 |
| **② CB** | **사채만기일 (6)**, **원금상환방법 (6)**, **납입일 (6)**, **전환에 관한 사항 (5)**, 이자지급방법 (4), **옵션(콜·풋)에 관한 사항 (4)**, **청약일 (4)**, 전환가액 (2), **전환청구기간 (2)**, 전환가액 조정에 관한 사항 (2), 권면총액 (2), 미상환 사채권 현황 (3) | ✅ direct — 전환청구 개시일·전환가액 move the 오버행 캘린더 |
| **② EB** | dominated by `기타 투자판단에 참고할 사항[그 외 …]` / `【조달자금의 구체적 사용 목적】` free-text blocks (**31 of 52 items** across 10 corrections); the rest are **교환가액, 교환가액 결정방법, 교환청구기간, 교환대상 주식수·비율, 사채만기일, 이자율, 권면총액** — incl. `20260416000477` (남성: 교환가액 1,029→10,290원, 교환대상 2,623,906→262,390주, a decimal-shift correction) and one full **철회** (`20260306001019` 위닉스, `전항목: 교환사채권발행 결정 → 교환사채권발행 결정 철회`) | ⚠️ mostly narrative, but 교환가액/주식수 move the 오버행 math and a **철회** must invalidate the event outright |
| **③ 합병** | **합병일정 (합병기일 / 합병보고총회일 / 합병등기예정일)**, **합병반대의사통지 접수기간** (`20260730000178`: 시작일 8/14 → 8/13), **주식매수청구권에 관한 사항 — 행사절차·방법·기간·장소**, 지급예정시기·지급방법, 채권자 이의제출기간, 주주명부폐쇄기간, 합병신주의 종류와 수, 합병비율 산출근거 | ✅ direct — the 매수청구 window itself moves |

**Cross-cutting:** `기타 투자판단에 참고할 사항` is the single most frequently corrected 항목 (11 / 40) in every rights type. It is free text and is where the 🔴 prose fields live — **so 정정 diffing cannot be reduced to comparing structured fields; the prose block must be re-extracted and re-diffed on every correction.** This is precisely the §3.6 "정정 diff + 해석이 상시 AI 작업" claim, now measured.

**Worked pair (illustrative).** `20260813001290` (에넥스, 2026-08-13) ← `20260721…` original, 정정사항 = `9. 납입일: 2026년 8월 13일 → 2026년 9월 14일`, `12. 신주의 상장예정일: 2026년 8월 31일 → 2026년 9월 30일`. A user D-day would have moved by 32 days.

Other verified pairs (exact `최초제출일`, with their changed fields):
`20260715000344` 케이지에이 ← `20260612000447` (신주수, 운영자금, **발행가 1,388→1,215**, 기준주가) ·
`20260730000278` LB세미콘 ← `20260515002719` (자금조달 목적, 신주 발행가액) ·
`20260529002142` 엑스페릭스 ← `20260507000567` (사채만기일, 전환가액 결정방식, 전환청구기간, **주식총수 대비 비율 7.36%→6.73%**) ·
`20260721001361` 애드바이오텍 ← `20260626000645` (사채만기일, 전환에 관한 사항, 옵션, 청약일) ·
`20260616000268` 포니링크 ← `20260529001660` (권면총액, 자금조달 목적, 전환에 관한 사항) ·
`20260203000135` 아주스틸 ← `20260126000473` · `20260210000877` 알서포트 ← `20260203000402` ·
`20260319000331` 모다이노칩 ← `20260219002620` (합병기일 4/28→4/30, 합병보고총회일 4/29→4/30) ·
`20260730000178` 한중엔시에스 ← `20260729000331` (합병반대의사통지 접수기간 8/14→8/13).

---

## 5. `document` API — 본문 parseability verdict (Q3)

`GET /api/document.xml?rcept_no=…` → ZIP containing **one** `<rcept_no>.xml` member, declared `encoding="utf-8"`, HTML-like `TABLE / TR / TD / TH / COLGROUP` markup with `<SECTION-1>`, `<TITLE ATOC="Y" …>` semantic markers, `ENG="…"` attributes on many header cells, and a `<CORRECTION>` element on 정정 filings.

| rcept_no | filing | XML chars | text chars | verdict |
|---|---|---|---|---|
| `20260724000546` | 주요사항보고서(유상증자결정), 주주배정 | 31,376 | **6,001** | one-shot LLM input; 신주인수권증서 ×17, 초과청약 ×8, 실권주 ×6, 배정기준일 ×4 |
| `20260521000775` | 주요사항보고서(전환사채권 발행결정) | 42,223 | **6,964** | one-shot; 전환가액 ×40, 조정 ×38 |
| `20260810000482` | 주요사항보고서(회사합병결정) | 65,532 | **9,848** | one-shot; 매수청구 ×8, 반대의사 ×3 |
| `20260814004100` | 증권신고서(지분증권) | 3,447,606 | **615,780** | needs section-targeted chunking; 신주인수권증서 ×130, 매매기간 ×4, 초과청약 ×43 |
| `20260713000459` | 증권신고서(합병) | 9,559,478 | **1,867,597** | needs section-targeted chunking; 매수청구 ×432, 반대의사 ×59 |

**Verdict: parseable, no HTML-viewer fallback needed.** Two regimes:
- **주요사항보고서 (2.6k–10k text chars)** — the whole document fits in one LLM call, and its numbered labels support a deterministic pre-parse. **This is where P2's extraction should live for all three rights types.**
- **증권신고서 (0.6M–1.9M text chars)** — 100–300× larger. Feed it only after slicing by `<TITLE>` section (the 신주인수권증서 section and 청약 일정 section), never whole. ▷ Given that the 주요사항보고서 already carries every 🔴 field, the 증권신고서 is best treated as a **confirmation / citation-span source**, not the primary extraction target.

Both regimes support §3.6 layer 2's **원문 인용 스팬 존재** gate: the source XML is character-addressable, so an extracted value can carry its offset span.

---

## 6. OpenDART API constraints (F6 re-verified + new)

| # | constraint | evidence |
|---|---|---|
| 1 | `list.json` without `corp_code` allows a **3-month window only** (`status 100`, `corp_code가 없는 경우 검색기간은 3개월만 가능합니다`). `20260101~20260331` (exactly 3 months) is accepted. | F6; re-confirmed in `discover()` |
| 2 | `list.json`: `page_count` max 100, page via `page_no` until `total_page`. `pblntf_ty=B` 주요사항보고, `C` 발행공시. | `scripts/spike/dart.py:filings` |
| 3 | Detail endpoints require `corp_code` **and** a date window; **the window filters on the report's ORIGINAL 접수일** and the response carries the **latest version's** `rcept_no` and values. | §4.2 |
| 4 | Detail endpoints return **one row per event** (versions are collapsed). Superseded versions are unrecoverable. | §4.2, SKC / 디모아 |
| 5 | 증권신고서 endpoints (`estkRs`, `bdRs`, `mgRs`, `dvRs`, `extrRs`) return **`group[]` of `{title, list}`**, not a flat `list` — a client written for 주요사항보고서 shape silently reads 0 rows. | `dart.groups()`; `estkRs` returned `status 000` with no `list` key |
| 6 | `null` query params must be **dropped**, not serialized — sending `corp_code=None` yields `status 100 corp_code가 필드의 부적절한 값입니다`. | fixed in `dart.get_json` |
| 7 | Status codes seen: `000` 정상, `013` 조회된 데이타가 없습니다 (endpoint real + key valid), `100` 부적절한 값, `101` 잘못된 URL. | F1; re-confirmed |
| 8 | **Transient `HTTP 503`** occurs under sustained calling and on some narrow date windows; a retry with backoff is required. 6 concurrent threads were sustainable (~1,000 requests without a ban). | `dart._fetch`; observed twice |
| 9 | `document.xml` returns a ZIP (magic `PK`); an error is returned as a non-ZIP XML body. | `dart.document_members` |
| 10 | `estkRs.일반사항.rpt_rcpn` = the 주요사항보고서 접수번호 as of the 신고서 filing — a **join key across 발행공시 ↔ 주요사항보고**, but version-stale (7/39 match today's `piicDecsn` rcept_no). | §4.2 |
| 11 | 사모 CB/EB is 증권신고서-면제 → for ② the 주요사항보고서 is the only source. | §2.2, `ex_sm_r` |
| 12 | ▷ Daily call quota not measured. ~1,002 distinct requests in one session drew no quota error. Confirm the published cap before P2's backfill. | — |

**Coverage gaps stated honestly.** The sample frame is KOSPI + KOSDAQ only (no KONEX/기타, `corp_cls=N/E`) and 2026-01-01 ~ 08-18 only. Per-endpoint corp sampling was capped (40 corps for `piicDecsn` in the field survey, 45 for `estkRs`, 35 CB, 20 EB, 35 합병) except for the `population` pass, which queried **every** corp with a matching 2026 filing. 정정 pairing used 40 corrections out of a much larger population. Nothing here is a census.

---

## 7. Consolidated extraction-target list for §3.6 layer 1

The LLM's entire reading job for the MVP, as measured:

| # | field | rights type | 본문 위치 | gate (§3.6 layer 2) |
|---|---|---|---|---|
| 1 | 신주인수권증서 상장·매매기간 | ① | 24-라 | date order; must fall between 배정기준일 and 청약일 |
| 2 | 청약 취급처 (대상자별 증권사 + 청약일) | ① | 24-다 | 청약일 must equal 본문 `11. 청약예정일` |
| 3 | 실권주 처리 방식 | ① | 24-나 | enum-ish; must name 일반공모 / 대표주관회사 인수 / 미발행 |
| 4 | 초과청약 조건 (비율) | ① | 24-나 3) | 0 < ratio ≤ 1; 배정주식수 × ratio arithmetic check |
| 5 | 발행가액 산정방법 (1·2차·확정 산식) | ① | 24-가 | 확정발행가 ≤ MAX(…) consistency vs 본문 `6.` |
| 6 | 리픽싱 세부 조건 | ② | 9. 전환가액 조정에 관한 사항 | floor must equal API `act_mktprcfl_cvprc_lwtrsprc` |
| 7 | 콜·풋 세부 스케줄 | ② | 9-1. 옵션에 관한 사항 | dates within 사채 발행일 ~ 만기일 |
| 8 | 보호예수 / 전매제한 해제일 | ② | 19. + 기타 투자판단 | ≥ 발행일; cross-check `ex_sm_r` |
| 9 | 반대의사 통지 방법·절차 | ③ | 13. 주식매수청구권에 관한 사항 | 기한 must equal API `mgsc_mgop_rcpd_bgd/_edd` |
| 10 | 정정 해석 (무엇이 바뀌어 D-day가 어떻게 이동했나) | all | `<CORRECTION>` 3. 정정사항 | before/after must both parse; changed dates must move monotonically |

Everything else in §3.6's list is either an `API` field or a `본문-label` row — i.e. **deterministic**, per §7's `계산은 결정론` rule.

---

## 8. Open items handed forward

- **`P1.S2` (scope):** the three types differ sharply — ② largest universe (263 CB reports) + most structured; ① smallest-but-killer (32 주주배정 events) with a mixed skeleton/prose cost; ③ smallest universe (~15–17) but nearly free to build. See the per-type feasibility signals above.
- **P2 (pipeline):** the version semantics in §4.2 are a hard collection-design constraint — poll `list.json`, key events by `(corp_code, subtype, original_rcept_dt)`, snapshot every version.
- ▷ **Unresolved:** meaning of `estkRs.일반사항.exstk/exprc/expd` (2/35 filled); whether 코넥스/기타 markets change any coverage conclusion; the published daily call quota.
