---
doc_id: operations
version: v0004
created_at: 2026-08-21T23:51:38+09:00
source: P3.REVIEW
summary: P3 operations: the design grounding-pack export command at zero spend, and the observation-only operating rules the signed admin panel imposes
previous: v0003_pipeline_operations_quota_and_request_ceilings_beat_schedule_and_budgets_the_pipeline_lock_and_how_to_regenerate_every_artifact_at_zero_spend
---

# Operations

## Status

Nothing is deployed yet, and the submission truth from P1 is unchanged. What P2 adds is **running
truth**: the pipeline now collects, extracts and gates on a schedule, under explicit budgets, and
every committed artifact can be regenerated at **0 OpenDART requests and 0 LLM calls**. **P3 adds one
local documentation command** (the design grounding-pack export, below) and — from the signed but
not-yet-built admin panel — the **observation-only operating rules** the future ops surface must obey.

# Part 1 — Running the pipeline

## Quota and Request Ceilings

- **Daily OpenDART quota: 20,000 requests per key** (operator, corroborated by community
  documentation; ▷ the official page defers to a homepage notice, so this is authoritative-by-operator
  rather than scraped).
- **Every collection run is bounded anyway.** `DartClient(max_requests=…)` raises
  `RequestBudgetExceeded`; a run **stops cleanly and keeps what it collected**. A known cap is not a
  reason to run unbounded.
- **Re-collecting a window is nearly free** — a second live pass over the same window added zero
  events and zero versions for 25 requests. That property is what makes the scheduled job cheap.
- **LLM calls are capped the same way**: `GeminiClient(max_calls=…)` refuses past the ceiling, and a
  budget-exhausted stage is a *reported status*, not a failed run.
- ▷ Total spend to date is roughly **3,100 OpenDART requests** across P1 + P2 (P1 ~1,002; S2 291,
  S3 289, S7 584, S8 ~337, F1 585) — comfortably inside one day's quota. Measured LLM spend, read from
  `extraction_call`: **213 calls, 2,025,260 tokens, ▷ $2.79, 0 failures.**

## Schedule and Budgets

`mijual.scheduler` = Celery beat + worker on the compose Redis (host **6380**, profile `scheduling`),
running **`collect → bodydoc → extract → gates`** in that fixed order.

| when (KST, `enable_utc=False`, `Asia/Seoul` explicit) | window | budgets |
|---|---|---|
| daily **07:30** and **19:30** | rolling **14 days** | collect ≤ 500 requests, bodydoc ≤ 200, extract ≤ **60 LLM calls** |
| Sunday **04:30** | **90 days** | collect ≤ 1500, bodydoc ≤ 600, extract ≤ 60 |

- The window is anchored on **KST**, not the host clock.
- **One lock, `mijual:lock:pipeline`, on every corpus-writing entry point.** Re-running a window is
  free, but two concurrent runs double-fetch — and spent quota is the one thing idempotent upserts
  cannot repair.
- **Broker-free fallback:** `python -m mijual.scheduler once [--offline]` runs the same code path;
  `--offline` costs **0 requests / 0 calls** and is the tool the analysis slices reuse.
- **Nothing in the scheduler is reachable from a request path.** The board renders persisted rows
  filtered by `Event.exposure_state`, so a dead worker leaves it **stale, never dark** — which is what
  the 결격 window below requires.

**Open operational decision before a worker runs unattended:** the 정정 해석 task still inherits the
project thinking preset (the three prose tasks run `LOW`). Today's backlog prices at **69 calls**
(정정 R1 59 + R3 10) against `extract_max_calls=60` per run, so the beat drains it in two scheduled
runs — at whatever level the preset happens to be. Decide the level, or cap it, before deploying a
worker (see `decisions` D-4).

## A Corpus Is Not a Census

Two standing practices, both learned by measurement:

1. **Run both sweeps.** A `list.json` census over the *result* filings surfaced three 2026 KOSDAQ ①
   originals an earlier run had missed, and one offering the census itself cannot see (KB스타리츠
   `20260423000439`, filed as 증권발행실적보고서(집합투자증권) outside 발행공시 entirely) which only a
   **per-event backstop** — one corp-scoped, unfiltered `list.json` per closed-청약 event — caught.
2. **Measure the gap before spending on it.** Full-2026 discovery found **244 of 2,279 target filings
   (10.7 %) had never been stored** (`piicDecsn` 192/1,145, `pifricDecsn` 4/25, `cmpMgDecsn` 48/286),
   while **`cvbdIsDecsn` was 0/823** because ②'s backfill window strictly contains 2026 — *a wider
   historical backfill immunises a rights type against the run gap*. The gap check itself is free:
   discover offline, diff the `rcept_no` set against stored versions, then spend.

Repair is cheap and targeted: **per-corp adoption costs 3–4 requests per offering** (22 offerings for
~90 requests, against ~300 for a market-wide historical re-run), lands ordinary corpus rows, and
heals `unpaired_correction` placeholders through the existing `superseded_by_pairing` path.

Two smaller operational rules: **a budget-capped live run must be followed by an offline pass over the
response cache before its numbers are read** (a capped run once left 28 fetched-and-cached documents
unpersisted), and **after re-deriving stored evidence, chase the number into every frozen or rendered
copy** — the gate note embeds it and the frozen evalset sample carries a copy.

## Local Development

Prerequisites: docker (Postgres 16 on host **5433**, Redis 7 on **6380**) and a repo-local `.venv`.

```bash
# infrastructure
docker compose up -d postgres                 # add: --profile scheduling  for redis/worker/beat

# tests + workspace
.venv/bin/python -m pytest                    # 59 tests, ~1s, no network
python3 scripts/workflow.py validate

# the pipeline, offline (0 requests, 0 calls)
.venv/bin/python -m mijual.scheduler once --offline

# stages and reports
.venv/bin/python -m mijual.collect ...        # live; honours --max-requests
.venv/bin/python -m mijual.bodydoc ...        # live; 본문 ZIP fetch + parse
.venv/bin/python -m mijual.extract --dry-run recheck   # measure, write nothing
.venv/bin/python -m mijual.gates run          # deterministic, 0 calls / 0 requests
.venv/bin/python -m mijual.gates summary
.venv/bin/python -m mijual.estimate report --today YYYYMMDD [--korean]
.venv/bin/python -m mijual.evalset report
```

**Everything that is committed regenerates at zero spend.** The 소멸 estimate, the gate verdicts and
the accuracy report all read the database or two frozen JSON files; two consecutive runs of
`gates run` and of `estimate report` are byte-identical. Re-running extraction is free as well —
already-stored fields are skipped and span re-resolution is a separate 0-call pass.

Cheap deterministic re-derivations, both idempotent: `python -m mijual.extract recheck` (re-scores the
stored 정정 check) and `python -m mijual.evalset refresh-recall` (re-freezes the label-free recall
figure in the frozen sample). Neither re-pays for an extraction.

### The design grounding pack (P3)

```bash
.venv/bin/python scripts/export_design_grounding.py            # → docs/reference/design/grounding/
.venv/bin/python scripts/export_design_grounding.py --out DIR  # export elsewhere (safe for a diff check)
```

- **A documentation tool, not product code.** It writes only under its output directory, and nothing
  under `src/mijual/` depends on it. It regenerates the anti-lorem pack the design rounds were
  designed against: `board-snapshot.md`, `headline-numbers.md`, `copy-inventory.md` and 11 pinned
  `EventExposure` / `FieldView` sample JSONs (the three prose pages in the pack are hand-written and
  are not touched).
- **0 OpenDART requests, 0 LLM calls** — everything is read from the local Postgres corpus through the
  same modules the product will use (`mijual.gates.exposure`, `mijual.cb`, `mijual.estimate`,
  `mijual.calc`). Verified by re-running it, and the two CLIs it shells out to, with every
  non-loopback socket blocked.
- **Deterministic on a fixed corpus and anchor:** two runs in the same session are byte-identical.
  It is **anchored on today**, so a run on a later date legitimately changes `measured_at` and every
  D-day label — that is drift in the anchor, not in the data. Every artifact carries its measurement
  date and the command that regenerates it, so a stale figure is always distinguishable from a changed
  one. **Diff a re-run into `--out <scratch>` rather than over the landed pack** unless you intend to
  re-date the record the signed design rounds cite.
- **It exits non-zero if a pinned sample has left the corpus** (reported as a `GAP` rather than
  silently substituted). Samples are pinned by `rcept_no` **and** exposure state, because one
  `rcept_no` can belong to several events.

# Part 2 — Shipping (unchanged from P1)

## Submission Deliverables

| # | What | Deadline (KST) | How |
|---|---|---|---|
| ① 공모전 기획서 | 기획서 **PDF**, from the 첨부1 양식 | **2026-09-07 (월) 10:00** | 대회 페이지 [제출 탭] → [공모전 기획서 제출] |
| ② MVP 산출물 | 기능명세서 **PDF** (첨부2 양식) **+ 웹서비스 URL** | **2026-09-07 (월) 10:00** | [제출 탭] → [MVP 산출물 제출] |
| ③ 최종 산출물 (발표 진출자만) | 발표자료 **PDF** (자유 양식) + 소스코드 **ZIP** | 2026-10-08 (목) 23:59 | e-mail `dacon@dacon.io` |

- **No demo video, and no GitHub link** — the MVP stage's form schema is
  `linkConfig = {demo: enabled+required, github: disabled, youtube: disabled}`. Source code changes
  hands only at ③, by e-mail, if selected.
- **PPT is banned** at 발표 (PDF only).
- **The platform does not enforce the rules.** The MVP stage carries `pdfConfig.required: false` even
  though the rules require the 기능명세서 PDF, and a missing 제출물 is 결격.
- **최종 제출 is a distinct act from uploading** — "수정 이후 대회 종료전까지 다시 최종 제출 버튼을
  눌러야합니다".
- **참가 신청 closes 2026-09-07 10:00 — the same instant as submission**; registration is done
  (operator, 2026-08-19), ▷ not verifiable from this workspace.

### 양식 (mandatory, in-repo)

Both `.hwpx` templates are committed at `docs/reference/challenge/submission/` with source URLs, byte
sizes and SHA-256 in that folder's `README.md`. `.hwpx` **reads** fine with the Python stdlib;
*writing* the filled documents and exporting to PDF is unsolved and belongs to the ship phase.

Three template requirements bind the **service**, not just the paperwork: 첨부2 §2 wants a **관련
화면** per feature; 첨부2 §5 wants a **judge-executable verification script** (테스트 계정, 샘플
입력값, 예상 결과, browser restrictions, MVP limitations) — *the service must be verifiable by a
stranger, unattended, from the URL alone*; 첨부1 §5 asks **how the 생성형 AI 모델 is used and what role
it performs**, which the reads-and-speaks split answers directly. The rules ask about *use*, never
about training.

## Deployment — the two 결격-grade constraints

1. **Uptime window.** "제출된 웹서비스 URL은 2026. 9. 7(월) 11:00 ~ 9. 11.(금) 23:59 동안 접근
   가능하여야 하며, **접근 불가 시 결격 사유에 해당합니다**" — five consecutive business days of
   unattended reachability. A single outage disqualifies the entry.
2. **URL freeze.** "배포 URL은 최종 제출 이후 변경된다면 불이익이 발생할 수 있습니다.
   (**제출한 URL만 인정됩니다**)" — the URL entered at 9/7 10:00 is final.

Consequences that are requirements, not polish: uptime monitoring and a rollback/standby path are
mandatory; **the board must render from persisted snapshots with no OpenDART call in the request
path** (P2 satisfies this structurally — see `architecture`); the URL must be decided before the
freeze; plan for a platform hostname by default.

## Rules confirmed by the organizer (게시판)

Zero official 공지 have ever been posted, so nothing has amended the rules to date; every official
answer is a `DACON.GM` comment on a participant post.

- **Web only** — a mobile app is rejected, but **mobile-first responsive web is explicitly accepted**.
- **Commercial LLM APIs are explicitly allowed**, at the entrant's own cost.
- **가상(더미) 데이터 is allowed if disclosed**, and 공개/공공 API 연동 is allowed — so running on
  **real DART filings is a free differentiator**, at zero disclosure burden.
- **No page limit** on 기획서/기능명세서 as long as the 양식 is preserved.
- Whether MVP data is live rather than dummy is "참가자 선택 사항 … 평가 요소로 반영될 수도 있습니다".

**The brief is edited in place, with no changelog and no notice.** ▷ Re-reading the brief and the
board shortly before 9/7 is a real ship task, and so is re-checking both 양식 against their live URLs
with the recorded SHA-256.

## Timeline

| Date (KST) | Event |
|---|---|
| **2026-09-07 (월) 10:00** | 참가 신청 마감 **AND** 기획서 + MVP 산출물 마감 |
| 2026-09-07 11:00 → **09-11 (금) 23:59** | 웹서비스 URL 접근 가능 필수 — **결격 window** |
| 09-07 → 09-22 | 본선 심사 (내부 비공개 심사위원단, 100%) |
| 09-22 (화) 10:00 | 발표 심사 대상 발표 (상위 11팀 내외) |
| 09-23 (수) → 10-08 (목) 23:59 | 발표 진출자 최종 산출물 제출 |
| 10-13 (화) 10:00–16:00 | 오프라인 발표 심사 — PT 15분 + Q&A 5분 |
| 10-23 (금) 10:00 | 최종 결과 발표 / 대회 종료 |

Schedule management around these dates is **operator-owned** and is not planned around by the
workspace. The 결격 uptime window is exempt: it is a property of the service.

## Environment Variables

| Name | Required | Purpose | Notes |
|---|---|---|---|
| `DART_API_KEY` | yes | OpenDART auth | gitignored repo-root `.env`; read in-process, never printed, never committed |
| `GEMINI_API_KEY` ("changple5") | yes | reading layer | same handling; reaches only the SDK |
| `DATABASE_URL` | yes | Postgres (docker, host 5433) | corpus is re-collectable; no Alembic by design |
| `REDIS_URL` | for scheduling | Celery broker / result backend / lock | docker, host 6380 |

Gitignored and regenerable: `.env`, `.venv`, `var/`, the P1 response cache
(`scripts/spike/samples/*`, ~9.4 MB / 1,002 files). Committed as evidence: the small summaries under
`scripts/spike/samples/_summary/` and the `evalset/` artifacts.

## Observability

- Minimum bar set by the 결격 window: an external uptime check on the submitted URL covering
  2026-09-07 11:00 → 09-11 23:59, with an alert path that reaches the operator.
- Pipeline side: every stage prints its counts, its request/call spend and a ▷ cost line; the beat's
  budgets make a shortfall visible as a reported status rather than a silent stall.

### The operator surface, as signed at P3 R7 (built at the apply phase)

The 운영 관제 panel is designed and operator-approved; these are operating rules, not UI notes:

- **Pure observation — no mutation endpoints anywhere.** No review/clear/approve/re-run control, no
  status bits on the queues. **Exposure changes only through the pipeline CLI**, so no click can
  silently override a deterministic gate verdict.
- **A beat that did not run renders as an alert-ink 「실행 기록 없음」 row**, derived from the scheduled
  time. Silence must never read as success. A **budget exhaustion is a reported status, not a
  failure style** — alert styling is reserved for did-not-run.
- **Sources, not restatements:** the beat schedule renders from the Celery beat configuration (never
  hardcoded); the accuracy view prints what `mijual.evalset report` emits, with the **`judged_by`
  provenance block above the numbers** — 98.6 % never appears without it; ▷ cost markers are printed
  verbatim from pipeline output; open pre-launch items (D-4's thinking-level question) are read from
  `decisions` rather than restated in the panel.
- **The pipeline lock** `mijual:lock:pipeline` is surfaced live as a chip (held/free + held-since).
- **The cumulative quota bar is labeled as cumulative, not daily.**
- **Reason codes and suppression codes render verbatim in English**, unknown codes included — no
  Korean was invented for them and no fallback copy is allowed.
- Gate-queue rates are computed on **distinct `(rcept_no, field_key)` = 633**, not the 649 stored rows
  (16 duplicates).

## Knowledge (phase explainers)

The `explain` skill ships with this workspace, in `.claude/skills/`. Explaining is an **operator-run
step, separate from the phase review**: run `/explain` for a phase when you want one and it saves an
interactive HTML explainer to the knowledge service. The review itself writes no explainer — it only
reports the pointer `explain: not written — run /explain for this phase`.

**Setup is on first use, and it asks first.** Run `/explain`; if no knowledge base is configured it
offers to create one on the hosted service at `https://knowledge.hi2vi.com` — it asks for an email,
installs the `knowledge` CLI, signs you up (or logs you in), and writes an org-level key to
`~/.config/knowledge-kb/config.json` at mode 0600. One org key serves every repo.

Already have a knowledge base — hosted or self-hosted? Skip the setup by exporting the credentials in
`~/.zshenv` (never a repo `.env`):

    export KB_API_BASE_URL="https://knowledge.hi2vi.com"
    export KB_API_TOKEN="vk_..."

- **Alternative (Claude Code plugin):** `/plugin marketplace add leetusik/knowledge` →
  `/plugin install knowledge@knowledge` → `/knowledge:setup`, then `/knowledge:explain`.

## Open Questions

- The login-gated **[제출 탭]**: real form fields, file-size limits, the solo entrant's `팀명`, and
  whether 최종 제출 has extra steps.
- Deploy target, monitoring stack, and the `.hwpx` → PDF authoring path.
- Where the Celery worker runs in production, and at what thinking level the 정정 해석 task runs there.
- 발표 심사 venue and travel cost (unannounced by the organizer).
