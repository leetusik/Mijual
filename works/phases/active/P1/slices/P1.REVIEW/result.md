# Result — P1.REVIEW: phase review of P1 "Foundation Spike & Confirmations"

**Verdict: `pass`.** Validation and judgment were completed in full before any consolidation, and the
three consolidated doc versions were then created. No source code was touched by this slice.

---

## 1. Validation re-run across the phase

### 1.1 Workspace

| command | outcome |
|---|---|
| `python3 scripts/workflow.py validate` | **PASS** — `Workflow validation passed.` (exit 0), before and after consolidation |
| `python3 scripts/workflow.py rebuild-docs` | **PASS** — `docs/current` regenerated from the latest versions |
| `python3 scripts/workflow.py docs` | **PASS** — `data`, `operations`, `decisions` now at `v0002`; the other 8 stay at `v0001_bootstrap` |
| `git status --porcelain` | clean apart from workflow-generated state + this slice's own files — **no stray source edits anywhere in the phase** |

### 1.2 `P1.S1` — all 8 spike entry points, from a clean environment

Every command re-run as `env -i /opt/homebrew/bin/python3 …`, so `DART_API_KEY` could only come from
the in-process `.env` parse. All hit the on-disk cache.

| command | rc | reproduced |
|---|---|---|
| `scripts/spike/dart.py` | 0 | `list.json -> 000 정상 \| rows: 10 \| total: 413` |
| `scripts/spike/survey.py rights1` | 0 | 유증 field survey + Q1 |
| `scripts/spike/survey.py rights2` | 0 | CB/EB/`bdRs` survey |
| `scripts/spike/survey.py rights3` | 0 | 합병/`mgRs`/주식교환 survey |
| `scripts/spike/survey.py population` | 0 | **299 유상증자 / 32 주주배정 계열 (11%)**; **263 CB / 236 corps**, **20 EB**; **83 합병, 65 소규모**, `aprskh_plnprc` 15, 행사기간 17 |
| `scripts/spike/survey.py labelscan 10` | 0 | **10/10 labels in 9/9** filings; prose 증서 매매기간 recovered, incl. 이렘's two ranges and the `…08월 25일4` numbering bleed |
| `scripts/spike/survey.py docprobe` | 0 | 5/5 ZIPs; both size regimes (6,001 vs 615,780 text chars) |
| `scripts/spike/corrections.py 40` | 0 | **`30/40 paired (16 by exact 최초제출일); 40/40 carry a parsed 정정사항 table`** |

Every headline number in `phase.md` F8–F16 and in `docs/reference/dart/field-matrix.md` reproduced
**exactly**. Nothing was rounded, and nothing had drifted.

**One real gap found and closed — a stale committed evidence file.** `P1.S1/result.md` and
field-matrix §4.3 both point at `scripts/spike/samples/_summary/corrections.json` for "full records"
of the 40-correction sample, but the **committed** copy held only **8 pairs (5 paired)** — it was
written by an earlier, smaller run and never refreshed after the final `corrections.py 40`. Its
`item_frequency` table therefore read `기타 투자판단 3, 납입일 2, …` while the matrix cites
`기타 투자판단 11/40, 납입일 10, 사채만기일 7, 원금상환방법 6, 이자지급방법 5` — the **re-run** figures.
Re-running the documented reproduce command (`python3 scripts/spike/corrections.py 40`, listed in the
matrix's own "Reproduce" row) regenerated the file to **40 pairs / 30 paired / 40 with 정정사항 items**,
which now matches every claim that cites it. **No claim changed** — the numbers in the docs were the
correct ones all along; only the committed snapshot lagged behind them. The regenerated file is left
in place as part of this slice's diff (`scripts/spike/samples/_summary/corrections.json`) because it
makes the committed evidence consistent with the documentation; it is pure regenerated data, not code,
and `git checkout -- scripts/spike/samples/_summary/corrections.json` reverts it if the orchestrator
prefers to keep the commit review-only.

**Evidence discipline spot-check (matrix):** sampled `estkRs.asstd` 28/28, `cvbdIsDecsn` 47/47 with
evidence `20260521000775`, `mgsc_mgop_rcpd_*` 41/41 with `20260810000482`, 증서 매매기간 prose with
`20260724000546` — each "structured" claim in §1–§3 carries an `rcept_no`, and every inference
(`▷ ~4–5/month`, `▷ ~2/month`, the daily quota, the `exstk/exprc/expd` semantics) is marked `▷`. §6
states the coverage gaps (KOSPI+KOSDAQ only, per-endpoint corp caps, "nothing here is a census")
rather than hiding them.

**Secret hygiene, re-verified rather than inherited:**
- zero occurrences of the key value in the 8 captured stdout/stderr streams;
- zero occurrences in **any tracked file**;
- zero occurrences in **any file under the repo** outside `.git/` and `.env`;
- the only `crtfc_key` hits are the literal parameter name in `scripts/spike/dart.py` plus prose in
  `P1.S1/result.md` and `P1.S2/result.md` — correct, not a leak.
- `.gitignore` correctly excludes the 9.4 MB regenerable cache while keeping the 7 committed
  `_summary/*.json` evidence files.

### 1.3 `P1.S3` — external facts re-fetched live

| check | outcome |
|---|---|
| official brief JSON (HTTP 200, 52,262 B) | **PASS** — `registrationDeadline 2026-09-07T01:00:00Z` (= 9/7 10:00 KST, same instant as submission), `competitionEndDate 2026-10-23`, `eligibility "anyone"`, `minTeamSize 1` / `maxTeamSize 4`, `updatedAt 2026-08-18T20:21:02.841Z` |
| 결격 uptime clause | **PASS** — verbatim: "제출된 웹서비스 URL은 2026. 9. 7(월) 11:00 ~ 9. 11.(금) 23:59 동안 접근 가능하여야 하며, 접근 불가 시 결격 사유에 해당합니다" |
| MVP stage form schema | **PASS** — `linkConfig {demo: enabled+required, github: disabled, youtube: disabled}`, `pdfConfig.required: false` — F18's "no video, no GitHub link" and F19(iii)'s "the platform does not enforce the rules" both hold structurally |
| 게시판 | **PASS** — `counts {all: 27, notice: 0, general: 27}`, 27 posts → **no notice has ever amended the rules** |
| 양식 files | **PASS** — both `.hwpx` present; SHA-256 recomputed and **matching the committed README byte-for-byte** (`15ba1f89…`, `83be2cd4…`), sizes 47,372 / 45,456 B |
| whois | **PASS** — `mijual.ai` `Domain not found.`, `mijual.kr` "등록되어 있지 않습니다", `mijual.com` GoDaddy, Creation 2018-08-28, **Registry Expiry 2026-08-28T11:06:44Z** |

F17–F23 are sourced throughout (a `[BRIEF]`/`[BOARD]`/`[TPL]`/`[WHOIS]` block heads the section), and
F23 states the honest gaps (login-gated 제출 탭, no brief changelog, unverified .ai checkout total,
unannounced 발표 venue) instead of glossing them.

### 1.4 `P1.S2` — package, decision record, and the new measurement

| check | outcome |
|---|---|
| `recommendation.md` covers 3 types + package + question set | **PASS** — §2 per type, §0/§3 package + five alternatives with costs, §5 the five-question round-trip, §6 method and gaps |
| F25 matches the operator's verbatim answers | **PASS** — the five-line quote block in `phase.md` F25 is byte-identical to the block the orchestrator appended to `P1.S2/plan.md`; the five recorded outcomes add no inference beyond it |
| two-pass `result.md` shows the closed gate | **PASS** — pass 1 `needs_operator` by design, pass 2 records the decision, files the deferred `decisions` Doc impact note, closes Q4, defers Q6's purchase half, opens Q8 |
| judging-week scan spot-checked against the cache | **PASS** — see below |

Spot-check of the load-bearing new measurement, re-derived from the cached 본문 and structured rows:

- 휴림에이텍 `20260804000486`: 신주배정기준일 **9/3 → 9/9** (정정), 증서 상장예정기간 **9/22~9/30 → 9/30~10/07**, 청약 10/13~14 → 10/19~20, 주주명부폐쇄 9/4~9/8 → **9/10~9/14**;
- 이렘 `20260811000481`: 배정기준일 8/13 → **9/2**, 청약 9/17~18 → **10/12~13**, 증서 **9/2~9/8 → 9/21~9/29**, 주주명부폐쇄 8/14~8/18 → **9/3~9/7**;
- 휴맥스홀딩스 `20260811000452` **6,839원** / 휴맥스 `20260811000467` **6,591원**, 행사기간 8/28~9/17; 에코볼트 `20260804000288` **1,968원** / 알에프텍 `20260804000294` **9,325원**, 반대의사 **9/8~9/22**, 행사 9/23~10/14, all `mg_stn = 해당사항없음`.

Every figure matches, and in each 정정 case S2 quoted the **정정-후** value — the correct one. The scan
was cache-only, so it made no network call and read no key material.

---

## 2. Judgment against the objective and intent

| objective clause | verdict |
|---|---|
| (a) event-type × field × {structured / LLM} matrix, incl. **≥5 정정공시 samples** | **MET, and exceeded** — `docs/reference/dart/field-matrix.md` spans 주요사항보고서 **and** 증권신고서 per type (the union the DECOMP probe insisted on), with **40 corrections sampled, 30 paired** against the bar of 5 |
| (b) MVP rights scope finalized **with the operator** | **MET** — the gate was a real stop: S2 returned `needs_operator`, decided nothing, and F25 records the operator's verbatim five-line answer plus exactly five outcomes |
| (c) daker.ai submission requirements + domain availability | **MET** — F17–F23, all re-verified live at review, with both 양식 committed and their structure extracted |
| (d) constraints honored | **MET** — no inflation (every number reproduced exactly), evidence tags used consistently, **no LLM call anywhere in P1** (the spike is stdlib-only; the matrix says where extraction *will* be needed and performs none), the key never left `.env`, no 금지선 framing anywhere, spike code kept to 3 throwaway files with no tests or scaffolding |
| (e) workspace hard rules | **MET** — no earlier slice ran `doc-new-version` (all docs were at `v0001_bootstrap` when this slice started); `docs/current/*.md` were never hand-edited; DECOMP created bare folders only; no executor commit or status transition |

Against `intent.md`: all three intent items are delivered, the working-language rule holds (English
notes and docs; Korean only for 공시 field names and quoted rules), and the "operator decides, nothing
auto-confirms" rule was honored literally.

**Two things the phase got right that are worth naming.** (1) The DECOMP's ordering deviation —
recon *before* the confirmation slice — converted what would have been two operator round-trips
around a phase-halting `pending` gate into one that closed five questions at once. (2) The phase
repeatedly overturned its own plan's assumptions with measurement and said so plainly (① is mixed,
not LLM-heavy; ③ was expected to have zero live judging-week events and has four; `bdRs` is not a CB
source; `mijual.com` cannot be acquired in time) — those are the corrections that make the rest of
the record trustworthy.

**One observation, not a finding.** `P1.S2`'s `recommendation.md` is a durable artifact inside a slice
folder that will be archived with the phase. Acceptable here: the *decision* it justifies now lives in
`decisions/v0002` (D-1…D-5) with its reasoning summarized, so nothing downstream depends on the
archived file. Future phases should still prefer `docs/reference/` for durable artifacts, as `P1.S1`
and `P1.S3` did.

**For the orchestrator (workspace state, outside this slice's authority):** `phase.json` still reads
`status: planned` while all four slices are done. `validate` passes and `review-phase` has no
precondition on phase status, so recording the `pass` verdict will move it straight to `done` — no
action needed beyond that.

---

## 3. Doc consolidation (pass-only work)

P1 is **not** in parallel mode (`phase.json` carries no `execution` block), so consolidation happens
here. The four Doc impact notes in `phase.md` map onto three doc versions — the two `decisions` notes
were merged, as the plan directed.

| doc | version | what it now carries |
|---|---|---|
| `data` | **`v0002_dart_as_the_mvp_data_source_rights-type_field_matrix_extraction_targets_version_and_constraints`** | OpenDART as the sole source; per-type endpoints + measured event universes; the three field tiers with per-type coverage; the 10 extraction targets with their deterministic gates; 본문 parseability and its two size regimes; **the collection constraints** (newest-version-only rows, original-date windowing, version-mutable `rcept_no` → event key `(corp_code, subtype, original_rcept_dt)` + per-version snapshots); the validated 정정 pairing method and diff targets; the API constraint table; the correctness filters; secrets |
| `operations` | **`v0002_challenge_submission_deliverables_deadlines_and_the_-grade_deploy_constraints`** | the three deliverables with KST deadlines; no video / no GitHub link; the platform's non-enforcement; 최종 제출 ≠ upload; the in-repo 양식 and the two template requirements that bind the *service*; **both 결격-grade deploy constraints** (uptime window, URL freeze) and their consequences; the organizer's confirmed rules (web-only, mobile-first OK, commercial LLM APIs allowed, dummy data allowed → real data is a free differentiator); the timeline; local dev + env vars. The workspace's "Knowledge (phase explainers)" section was carried over intact |
| `decisions` | **`v0002_mvp_rights_scope_confirmed_domain_fact_sheet_and_deferred_purchase_application_llm`** | D-1 rights scope (keep all three, named exclusions, funded CB backfill, drop order EB → ②'s backfill → ③ → ②, ① last), D-2 domain deferred, D-3 registration done, D-4 application LLM + credential handling, D-5 schedule operator-owned — each with context, alternatives, consequences and source; plus the verified domain fact sheet and a "Superseded Decisions" entry retiring the tentative 3종 and `mijual.com` |

`rebuild-docs` ran afterward and `docs/current/{data,operations,decisions}.md` regenerated (181 / 180 /
121 lines). The four Doc impact entries in `phase.md` are annotated with the version each landed in.

---

## 4. Deviations from `plan.md`

None in substance. Two additions, both inside the plan's intent:

1. **The plan asked for a repo-wide grep for the key pattern; the review went further** and scanned
   every tracked file *and* every file under the repo outside `.git`/`.env` for the literal key value
   read in-process from `.env` (the value itself was never printed). Same conclusion, stronger.
2. **`P1.S3`'s external facts were re-fetched live** (brief JSON, board counts, whois, template
   SHA-256) rather than only checked for sourcing, and `P1.S2`'s judging-week scan was independently
   re-derived from the cache. Both were cheap and both are what let this review call the numbers
   "reproduced" instead of "plausible".

And one unplanned side effect, kept deliberately: **the re-run refreshed the stale committed
`scripts/spike/samples/_summary/corrections.json`** from 8 records to the full 40 the docs cite
(§1.2). It is regenerated data, contradicts nothing, and removes a mismatch between an artifact and
the claims that reference it.

No source code was edited, no workflow state was transitioned, nothing was committed, and no
`review-phase` was run — those are the orchestrator's.

`explain: not written — run /explain for this phase.`
