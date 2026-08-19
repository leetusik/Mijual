---
doc_id: operations
version: v0002
created_at: 2026-08-19T20:58:29+09:00
source: P1.REVIEW
summary: Challenge submission deliverables, deadlines and the 결격-grade deploy constraints
previous: v0001_bootstrap
---

# Operations

## Status

Nothing is deployed yet. What **is** durable ship truth after P1: the challenge's submission
deliverables, their deadlines, and two **결격-grade** (pass/fail, not scored) constraints on the
deployed URL. Every fact below was read from the official brief JSON
(`https://daker.ai/api/hackathons/2026-finance-ai-challenge`) and the public 게시판
(`.../posts`, `.../posts/<id>/comments`) on 2026-08-19, and re-verified at the P1 review.

## Submission Deliverables

| # | What | Deadline (KST) | How |
|---|---|---|---|
| ① 공모전 기획서 | 기획서 **PDF**, from the 첨부1 양식 | **2026-09-07 (월) 10:00** | 대회 페이지 [제출 탭] → [공모전 기획서 제출] |
| ② MVP 산출물 | 기능명세서 **PDF** (첨부2 양식) **+ 웹서비스 URL** | **2026-09-07 (월) 10:00** | [제출 탭] → [MVP 산출물 제출] |
| ③ 최종 산출물 (발표 진출자만) | 발표자료 **PDF** (자유 양식) + 소스코드 **ZIP** | 2026-10-08 (목) 23:59 | e-mail `dacon@dacon.io` |

- **No demo video, and no GitHub link** — the MVP stage's form schema is
  `linkConfig = {demo: enabled+required, github: disabled, youtube: disabled}`. The only link the
  platform accepts is the demo URL. Source code changes hands only at ③, by e-mail, if selected.
- **PPT is banned** at 발표 (PDF only, "기술적 오류 방지").
- **The platform does not enforce the rules.** The MVP stage carries `pdfConfig.required: false` even
  though the rules require the 기능명세서 PDF, and a missing 제출물 is 결격. Never let the form's
  leniency stand in for the rules.
- **최종 제출 is a distinct act from uploading.** A 최종 제출 can be reverted to 임시 저장 on request,
  but "수정 이후 대회 종료전까지 다시 최종 제출 버튼을 눌러야합니다" — pressing the button is its own
  checklist item.
- **참가 신청 closes 2026-09-07 10:00 — the same instant as submission** and requires a `dacon.io`
  account (one account only). Registration is **done** (operator, 2026-08-19); ▷ not verifiable from
  this workspace, the 제출 탭 is login-gated.

### 양식 (mandatory, in-repo)

Both `.hwpx` templates are committed at `docs/reference/challenge/submission/` with source URLs,
byte sizes and SHA-256 in that folder's `README.md`, plus the required section structure extracted
verbatim. `.hwpx` is a ZIP of OWPML XML and **reads** fine with the Python stdlib; *writing* the
filled documents (Hangul or an .hwpx-capable converter, then export to PDF) is unsolved and belongs
to the ship phase.

Two template requirements bind the **service**, not just the paperwork:

- 첨부2 §2 wants a **관련 화면** per feature;
- 첨부2 §5 wants a **judge-executable verification script** — 테스트 계정, 샘플 입력값, 예상 결과,
  browser restrictions, MVP limitations. **The service must be verifiable by a stranger, unattended,
  from the URL alone.**
- 첨부1 §5 asks explicitly **how the 생성형 AI 모델 is used and what role it performs** — the AI-role
  split (reads and speaks; calculation deterministic) answers this directly. The rules ask about
  *use*, never about training.

## Deployment — the two 결격-grade constraints

1. **Uptime window.** "제출된 웹서비스 URL은 2026. 9. 7(월) 11:00 ~ 9. 11.(금) 23:59 동안 접근
   가능하여야 하며, **접근 불가 시 결격 사유에 해당합니다**" — five consecutive business days of
   unattended reachability. A single outage disqualifies the entry; it is not a deduction.
2. **URL freeze.** DACON.GM, 2026-08-19: "배포 URL은 최종 제출 이후 변경된다면 불이익이 발생할 수
   있습니다. (**제출한 URL만 인정됩니다**)" — the URL entered at 9/7 10:00 is final.

Consequences that are requirements, not polish:

- **Uptime monitoring and a rollback/standby path are mandatory** for the ship phase, and the
  operator may be unavailable that week.
- **The board must render from persisted snapshots, with no OpenDART call in the request path** —
  transient upstream 503s are measured (see `data`), and an upstream wobble during the judged window
  would turn into an empty or erroring board.
- **The URL must be decided before the deployment freeze.** Any custom domain has to be bought and
  wired *before* that point, not after (see `decisions` for the domain fact sheet — none is purchased).
- Plan for a **platform hostname** by default; a branded URL is a late swap only if the operator
  supplies one in time.

## Rules confirmed by the organizer (게시판)

The board is fully public and unauthenticated: `counts = {all: 27, notice: 0, general: 27}` —
**zero official 공지 have ever been posted**, so nothing has amended the rules to date. Every official
answer is a **`DACON.GM` comment** on a participant post; 19 of the 27 posts are auto-generated
"요약: …" third-party marketing content with no authority.

- **Web only.** A mobile app or app-download page is rejected — but **mobile-first responsive web is
  explicitly accepted**.
- **Commercial LLM APIs (GPT 등) are explicitly allowed**, at the entrant's own cost.
- **가상(더미) 데이터 is allowed if disclosed**, and 공개/공공 API 연동 is allowed where legally
  unconstrained — so running on **real DART filings is a free differentiator**, at zero disclosure burden.
- **No page limit** on 기획서/기능명세서 as long as the given 양식 is preserved; 시각자료 may be added.
- Whether MVP data is live rather than dummy is "참가자 선택 사항 … 평가 요소로 반영될 수도 있습니다".

**The brief is edited in place, with no changelog and no notice** (`updatedAt` was
`2026-08-18T20:21:02.841Z`). ▷ **Re-reading the brief and the board shortly before 9/7 is a real ship
task, not a nicety** — and re-checking both 양식 against their live URLs with the recorded SHA-256.

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

Schedule management around these dates is **operator-owned** (operator, 2026-08-19) and is not planned
around by the workspace. The 결격 uptime window above is exempt from that: it is a property of the
service, not of anyone's calendar.

## Local Development

- Run: `python3 <script>` — the P1 spike is stdlib-only, no dependencies, no packaging.
- Spike entry points (all read an on-disk response cache; safe to re-run):
  `python3 scripts/spike/dart.py`,
  `python3 scripts/spike/survey.py {rights1|rights2|rights3|population|labelscan|docprobe}`,
  `python3 scripts/spike/corrections.py 40`.
- Workflow: `python3 scripts/workflow.py validate`.

## Environment Variables

| Name | Required | Purpose | Notes |
|---|---|---|---|
| `DART_API_KEY` | yes | OpenDART auth | gitignored repo-root `.env`; read in-process, never printed, never committed |
| Gemini credential ("changple5") | yes (from P2) | application LLM | not in this repo; store gitignored beside `DART_API_KEY` |

The raw OpenDART response cache (`scripts/spike/samples/*`, ~9.4 MB / 1,002 files) is gitignored and
fully regenerable; the small summaries under `scripts/spike/samples/_summary/` are committed as evidence.

## Knowledge (phase explainers)

The `explain` skill ships with this workspace, in `.claude/skills/`.
Explaining is an **operator-run step, separate from the phase review**:
run `/explain` for a phase when you want one and it saves an interactive HTML explainer to
the knowledge service. The review itself writes no explainer — it only reports the pointer
`explain: not written — run /explain for this phase`.

**Setup is on first use, and it asks first.** Run `/explain`; if no knowledge base is
configured it offers to create one on the hosted service at `https://knowledge.hi2vi.com`
— it asks for an email, installs the `knowledge` CLI, signs you up (or logs you in), and
writes an org-level key to `~/.config/knowledge-kb/config.json` at mode 0600. One org key
serves every repo. Each document's project defaults to the repo's directory name.

Already have a knowledge base — hosted or self-hosted? Skip the setup entirely by exporting
the credentials in `~/.zshenv` (sourced by every zsh invocation) — never a repo `.env`,
which Claude Code does not auto-load and which risks committing the secret:

    export KB_API_BASE_URL="https://knowledge.hi2vi.com"
    export KB_API_TOKEN="vk_..."

- **Alternative (Claude Code plugin):** `/plugin marketplace add leetusik/knowledge` →
  `/plugin install knowledge@knowledge` → `/knowledge:setup`, then `/knowledge:explain`.
  A separate namespace from this workspace's `/explain`; you do not need both.

Drive knowledge through the skill/agents; REST is the substrate.

## Deployment

- Target: undecided. ▷ The operator's own box (`ssh h`) is a candidate, but constraint 1 above makes a
  weekday outage a disqualification — budget for monitoring and a standby path either way.
- Process: undecided (ship phase).
- Rollback: **required** — see the 결격 window.

## Observability

- Minimum bar set by the 결격 window: an external uptime check on the submitted URL covering
  2026-09-07 11:00 → 09-11 23:59, with an alert path that reaches the operator.

## Open Questions

- The login-gated **[제출 탭]**: real form fields, file-size limits, what a solo entrant writes in the
  templates' `팀명` field ("등록된 팀명과 동일하게 작성"), and whether 최종 제출 has extra steps.
- ▷ Whether any earlier version of the brief said something different — it is edited in place with no
  changelog, so `updatedAt` is all that is knowable.
- 발표 심사 venue and travel cost (unannounced by the organizer).
- Deploy target, monitoring stack, and the `.hwpx` → PDF authoring path are all still open.
