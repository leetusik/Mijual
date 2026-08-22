---
doc_id: data
version: v0005
created_at: 2026-08-22T22:52:38+09:00
source: P6.REVIEW
summary: P6 apply phase: the two anonymous conversation tables — no account/email/IP/UA column, no foreign key in either direction, a randomly minted session handle, and rows that are not re-collectable
previous: v0004_p5_apply_phase_identity-scoped_pairing_the_first_stored_label_field_multi-part_citations_and_the_serving_reader_tables
---

# Data

## Status

P1 characterised the upstream; **P2 turned it into a stored, gated corpus**. This version keeps P1's
durable survey truth and supersedes it wherever P2 measured something different at larger scale.
Facts carry an `rcept_no`, a command or a count; estimates are marked `▷`. Per-field survey detail
still lives in `docs/reference/dart/field-matrix.md`; the storage schema lives in `architecture`.

Corpus as it stands (2026-08-22, after P5's three corpus jobs): **1,359 events / 3,990 filing
versions / 7,076 snapshots / 69 증권발행실적보고서 / 545 offering inputs**, **710 extraction rows**
(691 distinct `(rcept_no, field_key)`, 19 duplicates), **488 exposable events (① 50, ② 422, ③ 16) /
418 renderable field instances**.

**P5 changed the corpus in three ways, all offline** (0 OpenDART requests, 0 model calls, ▷
$0.0000 between them): identity-scoped 정정 pairing (**49 versions re-parented, +14 suppressed chain
heads**), the first stored `본문-label` field (**+61 extraction rows**), and multi-part citations on
summed 실적보고서 figures (**7 figures in 4 filings**). **The 488 exposable events and every rendered
number are byte-identical before → after all three** — these were correctness repairs to *evidence*,
not to values.

**P6 changed no corpus row at all.** It added two tables that sit entirely outside the corpus chain —
`conversation_turn` and `conversation_feedback` — and read the existing corpus through the same
loaders every other surface uses. They are the first tables in the system whose rows are **not
re-collectable**, which changes how they may be migrated (see *Conversation Tables* below).

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
| `본문-label` | deterministic table parse with a character span | **94/94** 주주배정 계열 유상증자결정 본문 yield all 10 §1.3 target labels; **23,493/23,493** extracted values carry a verified span. **P5 gave this tier its first *stored* field** — see below |
| `본문-prose` | LLM schema extraction **+ deterministic gate** | the 10 targets below, and nothing else — the registries are asserted disjoint by test |

**The 11th field, and the first stored label field: ③ `appraisal_price` (매수예정가격).** Read from
본문 `13. 주식매수청구권에 관한 사항 → 매수예정가격` — a form cell `bodydoc.extract_labels` already
parses with a real span, present in **95/95** stored ③ 본문 (70 a number, 25 `-`) and never twice, so
there is no per-주식종류 split. It is stored in the **same `Extraction` row shape as an LLM field**
with `call_id`/`model` **NULL**, which is how a report tells a free reading from a paid one — so
exposure, the presentation contract and the detail payload needed no change at all. Its declaration
lives in the new registry `mijual.extract.labelfields.LABEL_SPECS` (key · Korean name · 본문 위치 ·
label block · qualifier · gate), so **a second label field is a registry entry plus a gate, nothing
more**.

Its **gate is two machine witnesses**: the citation resolves and re-slices, the value is a positive
원 figure, the value equals the number the citation prints, and the value **equals the API's
`aprskh_plnprc`** — measured agreeing **17/17 with 0 mismatches**. An absent API value is a *skip*,
not a pass in disguise. Result over the corpus: **47 passed / 0 tbd / 0 failed / 14 not_evaluable**,
and no `appraisal_price_*` reason code fired anywhere. **An empty cell is `absent`, never 0 and never
a null**, and there is **no `추후결정` case** for this field: the four ③ without a price
(소규모합병 · three 스팩 합병) write "향후 … 결정하여 공시할 예정", not 추후결정, and only positive
evidence earns a `tbd`.

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

Field verdicts today (`gates run`, byte-identical across two runs): **710 rows** — the P2 distribution
unchanged plus P5's 61 `appraisal_price` rows (47 passed / 0 tbd / 0 failed / 14 not_evaluable). The
API filters in SQL on the persisted columns and makes **no OpenDART call in the request path**.

**The contract outranks the persisted column.** The serving layer skips a row whose live
`exposure_of` verdict is not `exposable` even where `Event.exposure_state` says it was (a gate run
that has not landed). The API renders what `gates.exposure` says — never its own reading.

**A non-exposable event has no countdown and no fields, and therefore no page**: renderable is
`state in {exposable, withdrawn}` — 철회 *is* a surface, since the notice replaces the body — and
everything else (suppressed / flagged / `no_document` / `no_detail` / `incomplete_api_row`) answers
**404** rather than rendering a page that explains why an event is not exposed.

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
0 OpenDART requests** (`python -m mijual.extract recheck`, idempotent). The 정정 diff now covers
**label fields too**, so a 정정 that revises the 매수예정가격 shows up in the CorrectionStory's
`field_moves` rather than changing a published number silently.

### The pairing rule is identity-scoped (P5, closing D1)

The 본문 `<CORRECTION>` 최초제출일 is now an **identity check as well as evidence**. When the hint
names no event of this corp+subtype:

1. **Self-evidence wins.** The hint matches a filing the event already holds (`rcept_no[:8]` **or**
   `rcept_dt`), or falls within **±7 days** (`HINT_SKEW_DAYS`) of the event's key → nothing moves.
   This is what keeps the ±1-day 접수일/제출일 skew — and every ① row — untouched.
2. **Only on a *rendered* event** (`exposure_state in {exposable, withdrawn}`): a **unique** other
   event of the same corp within **±1 day** (`HINT_NEAR_DAYS`) → the version is **reattached** there;
   nothing at all → the version is **split** onto a chain head keyed on the declared date, suppressed
   **`foreign_correction_head`**, flagged `hint_foreign_split`, `hint_status='split'` (sticky, and
   counting as `pairing_is_resolved`).
3. Everything else is the previous behaviour, unchanged.

**Why two arms and not one.** Of 653 mismatches, **201 are a 1-day 접수일/제출일 skew** (DART accepts
an after-hours 제출 the next day), **111 name a filing the event already holds**, and only **46 sat
on an event the product renders**. Of those 46, **22 were the corp's own earlier 사채 one 접수일
away** — mis-*attachments*, not unknown originals. Splitting those (the single-shape fix) would have
minted duplicate events, i.e. manufactured the very disease D2 describes. No hint anywhere in the
corpus has two events within 3 days of it, so unique-or-decline never had to decline.

Measured: ② gate failures on exposable events **6 → 1** (the survivor is a `span_unresolved`
citation defect, not pairing); **49 versions re-parented, 0 rows added, 0 removed, +14 suppressed
chain heads**; exposable **488 = 50/422/16 unchanged**. Two ② 철회 pages went away and that is the
finding: they held **no original and no detail row of their own**, so the 「이 사채 발행은
철회되었습니다」 they rendered belonged to a *different* 사채. **An event with no version has no filing
number and cannot be cited, so it must not render.**

Two durable consequences: the collector can no longer undo the repair (`collect.persist` skips a
`rcept_no` whose identity a hint has settled elsewhere and stores that run's snapshots on the owning
version instead — **any later re-collection must keep this**), and the repair converges in two passes
and is idempotent from the third. **Re-derivation order after any collect: `bodydoc backfill` →
`gates run` → `estimate reparse` → `estimate snapshot`.**

### Citations may have parts (P5, closing D4)

A stored citation must **state the number it backs**. `estimate.perf.Cited` now carries `parts` (one
`{raw, span}` per contributing cell) for a figure the filer printed as a **sum of table rows**, and
`performance_report.facts` gains an optional `parts` list on such a figure.

**Why they existed:** the filer splits the same 청약 by 경로 — 한국예탁결제원 *and* 직접청약/실질주주 —
so `Ⅶ 청약내역` states two numbers on two rows and the number the report means on **none**. All 7
cases are exactly two rows and the missing term was small (866 · 10 · 2 · 239 · 41 · 2,888 · 149),
which is why the defect read as a typo rather than a sum. Affected: 에스에너지 · 루닛 · SKC ·
한화솔루션 (the landing's own headline example, 청약 38,430,497 against a cell reading 38,427,609).

**0 of the 269 stored figures is now uncitable** (was 7), all 14 spans re-slice to their cells. The
stored form is additive and byte-compatible — `parts` appears only on a real multi-addend sum, so the
other 262 figures serialize exactly as before, and `performance_report.lapse` did not change at all
(it carries values, not citations). **Gotcha for anyone touching `perf.py`:** the shape to watch for
is `x = x or cell` beside an accumulating `+=` — that is what drops evidence.

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

## Serving and Reader Tables (P5)

All additive, all through `create_all` + `ensure_columns` — **still no Alembic**.

**Serving precomputation** (written by the offline worker, read by the request path, because
`mijual.estimate` may not be imported there): **`offering_input`** — one row per ① event, the whole
`EventInputs.as_json()` plus `price_confirmed` / `subscription_start` / `subscription_end` /
`decision_rcept_no` as **columns**, so the 소멸 앞둔 count and the 발행가 확정 전 state are SQL — and
the additive column **`performance_report.lapse`**, one `LapseRow.as_json()` per 실적보고서.

**Reader data, and it is deliberately barren.** `account` = `id · email · password_hash ·
created_at · updated_at` and nothing else: no name, no phone, **no admin flag**, no activity trail,
and **no column that could ever join to a conversation**. Email is stored in exactly one spelling
(NFKC + strip + case-fold, whole address; plus-tags kept, since `a+alerts@x.kr` is a deliverable
address a reader may want). `auth_session` stores a **digest** of the cookie token — no IP, no user
agent, no last-used column, because updating one would make an authenticated GET write.
`password_reset` is single-use with a 1-hour expiry. `holding` (`corp_code` + `shares` `BigInteger`,
unique per account+corp) is **deliberately not FK'd to `corp`**: the corp table is re-collectable
pipeline data and a reader's portfolio must survive a rebuild, so the reference is validated on
write instead. `notification_pref` holds `lead_days` JSON only — **no address column** (the 수신 주소
*is* the account email) and **no KakaoTalk column** (that row renders a 「예정」 chip and no working
control). `lapse_claim` stores account + the 증권발행실적보고서's `rcept_no` **and no amount**; the
claim key is that number on purpose, because a 유상증자결정's `rcept_no` mutates and an `event.id`
survives neither a rebuild nor a re-parenting.

Everything reader-side hangs off `account.id` with `ondelete="CASCADE"` **and** an ORM
`cascade="all, delete-orphan"`. Both halves are needed: SQLite (the test engine) does not enforce
foreign keys by default, so relying on the database alone would make 계정 삭제's completeness
environment-dependent.

**Operator data:** `ops_session` (token digest + expiry) has **no `account_id`, no FK and no
operator identifier at all** — a row means "somebody proved they hold the credential", which is the
whole fact. `pipeline_run` records one row per run (label · trigger · started/finished · seconds ·
window · config line · lock kind · ok · requests · calls · ▷ cost · the **verbatim** spend line ·
per-stage JSON · notes).

## Conversation Tables (P6) — anonymity as a schema property

R7 signs these columns and R6 signs the promise the reader is told: 「대화는 익명으로 저장됩니다
(품질 점검용)」. P6 implemented both, and the promise is **asserted by a test rather than kept by
discipline** — a promise nobody can check is a promise nobody keeps.

- **`conversation_turn`** — one row per turn as the reader saw it: 세션 해시 · 시각 (KST) · 범위
  (이벤트 rcept_no 또는 전체 공시) · 질문 · 답변/거절 · 거절 카테고리 · **근거 rcept_no 목록** ·
  **인용 칩 원문**, the last two stored as JSON lists of plain strings. There is deliberately **no
  quote↔rcept_no pairing column**: R7 signs two lists and that is what exists.
- **`conversation_feedback`** — 시각 · 의견 텍스트 · **답장 이메일 (optional, and only when the
  reader volunteered it)** · 세션 해시 as the link back to the conversation.
- **No account, email, IP or user-agent column exists on `conversation_turn` at all**, and the
  feedback row's `email` is the single exception R7 signs, spelled out in the test so a second one
  cannot arrive unnoticed. **Neither table has a foreign key in either direction**, no foreign key
  anywhere in the metadata crosses the conversation boundary, and no column on `account` names a
  session or a conversation. `tests/test_web_conversations.py::test_no_conversation_column_can_name_a_person_and_none_joins_an_account`
  walks all of that. **Do not add a foreign key to either table** — the test fails on any, and the
  point is that there is nothing to join *through*.
- **The session handle is minted, never derived.** `secrets.token_hex(16)` — random, with no input
  from IP, user agent, account or email, so the column cannot encode an address even in principle.
  A missing or malformed handle arriving from a client is **replaced, not trusted**, and both write
  functions refuse a non-handle outright, so nothing client-controlled reaches storage unchecked.
- **The stored vocabulary is Korean and signed.** `kind` is `answer`/`refusal` (a database
  `CheckConstraint`), and a refusal's 거절 카테고리 is one of the five signed family names — the exact
  strings the ops filter sends. An **unknown family is rejected at the write**, as is a refusal
  without a family and a category on an answer: an invented family would be a row the signed filter
  can never find. The five names are deliberately **not** in the schema, because copy can be re-signed
  and these rows cannot be re-collected — a re-signed family must not cost a destructive migration.
- **These rows are not re-collectable, and that changes the migration rule.** Every pipeline table
  can be rebuilt from upstream, so schema changes there are `create_all` plus a drop-and-refill if
  needed. A conversation cannot be rebuilt from anything. So the two tables change **additively
  (`ensure_columns`) or not at all** — if a later need appears (a quote↔filing pairing, say), add a
  nullable column rather than reshaping what exists.
- **익명 세션 is derived, not stored.** R7 calls it 「대화 로그의 집계면」, so it is a `GROUP BY
  session_hash` over the turn table plus one follow-up for each page's 마지막 범위. There is exactly
  one place a session can be written, so a session can never drift from its turns.
- **What a turn stores is what the reader read** — including a turn that ended in a refusal, a
  budget abort, an error, or a mid-stream 중지. Nothing about the *mechanism* is stored: R7 signs the
  columns and there is no status bit, so `aborted` versus `error` lives in the server log. A 중지
  before the first sentence stores nothing at all.
- **The stated default on portfolio-derived prose, taken as stated:** the turn is stored as the
  reader saw it, and there is **no portfolio or holdings column and no structured tool payload
  stored**. The row is unattributable and the log's purpose is 품질 점검.

**Deployment note P4 inherits:** these tables land through `mijual.db.session.create_all` like every
other, which is additive and idempotent (measured: 16 → 18 tables, nothing existing touched, still
zero foreign keys) — but there are no migrations and `create_all` otherwise runs only from the
collect/gates/pipeline entry points, so **P4 must create them before the first `POST /ask`**.

## Environment / Secrets

| Name | Required | Purpose | Notes |
|---|---|---|---|
| `DART_API_KEY` | yes | OpenDART auth | gitignored `.env`, read in-process, never echoed, never in a cached filename or recorded URL |
| `GEMINI_API_KEY` ("changple5") | yes | reading layer (`gemini-3.7-flash`) — **and, since P6, the in-request agent turn** | same handling; reaches only the SDK. Required neither to import `mijual.agent` nor to `create_app`: the client resolves it on first *use*, so the suite and a keyless boot both work |
| `MIJUAL_OPERATOR_CONTACT` | operator | the string `get_contact()` answers with | **no default and deliberately no `require_` accessor** — nothing may fail for want of it and nothing may substitute for it. Unset, the tool answers that no contact string exists; it never invents an address or promises one is coming. **Operator-provided at P4/deploy** |
| `DATABASE_URL` | yes | Postgres (docker, host 5433) | corpus is re-collectable |
| `MIJUAL_SESSION_SECRET` | P4 | peppers the stored session/reset digests | unset = unkeyed digests + one log warning (a development state); rotating it logs everyone out |
| `MIJUAL_COOKIE_SECURE` | P4 | `Secure` flag on both cookies | **off locally on purpose** — a `Secure` cookie on plain http silently never arrives |
| `MIJUAL_OPS_ID` / `MIJUAL_OPS_PASSWORD` | operator | the ops door | no operator row exists; unset means the door never opens, and says so identically to a wrong password |
| `MIJUAL_VOCKY_API_BASE` / `_API_KEY` | P4 | the vocky observation read | `vk_` key, masked repr, raises only on use, never logged, never in a URL, **https matters** |

## Open Questions

- ▷ Meaning of `estkRs.일반사항.exstk/exprc/expd` (2/35 filled) — unneeded by any MVP field; answer
  only if it falls out for free.
- Pre-2026 `pifricDecsn` depth is uncollected (deferred `D3`); ②'s history reaches 2025-06 only. P5
  did not need it: the signed 조회 surface fixes coverage at "2026-01-01 ~ 오늘 (KST)" with no 기간
  picker, and outside that boundary a figure is **unstated, never counted as 0** — so pre-2026 depth
  would change no rendered number.
- **D2 stands, and its trigger did not fire in P5.** The two `hint_duplicate` events (코이즈
  `20260122000058`, 사토시홀딩스 `20251219000402`) still carry a version whose hint names a different
  existing event — a duplicate record, not a foreign document, so the identity-scoped rule cannot fix
  it and the remedy is still a corpus-mutating merge. Measured on the built product: **no two of the
  450 rendered board rows share an `rcept_no`**, and 코이즈's 놓친 돈 total is not double-counted (the
  breakdown is keyed on the 실적보고서, which is unique — one row, `offerings: 1`). Nothing was
  de-duplicated at display level.
- **The literal "no collected original" test fires on 398 versions corpus-wide**, but 352 sit on
  suppressed placeholders and `superseded_by_pairing` residue no surface reads, and they are excluded
  on purpose. Widening that scope is a correctness change, not a cleanup: measure the exposable count
  on both sides of it.
- The 철회 detector's ③ generalisation has **no case in this corpus** — it is unit-tested on a
  constructed `회사합병 결정 → 회사합병 철회` row and untested against real data.
- `corp_cls=E` (기타) was never probed; KONEX was probed and adds **zero** exposable rights.
