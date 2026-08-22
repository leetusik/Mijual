# Plan — P5.S17: 운영 관제 (R7)

## Context

Read `works/phases/active/P5/phase.md` in full — binding here: S9 (the door, the
eleven `/ops` routes and their payloads, the port's honest zeros, the recounted
691 denominator, the absent 샘플-로드-여부 key, the run log), DECOMP note 5 (all six
tabs complete; 대화 로그/익명 세션 render honest 0건 through the port), S10 note 8
(**no CraftPanel here** — the ops idiom strips glow/brackets/translucency; build the
ops panel fresh: opaque `#0e1a15` + 1px `--border-strong`), S11 (chrome — but this
surface renders **none** of the reader chrome and is linked from nowhere). Design
chain: `frontend.md` → `SIGNOFF.md` (R7 — including the invented-chip override
note) → R7 `build-prompt.md` in full → `grounding/states-and-trust.md`.
**RESPECT THE DESIGN.**

## Deliverables — `/ops` route group, desktop-only

1. **The door** — pre-auth: an empty page with the Access card centered (no ops
   chrome, no reader chrome): 운영자 ID + password → S9's login; every failure
   renders the one uniform line 「자격증명이 올바르지 않습니다」 (the R7 literal);
   no signup/reset anything. Session probe via `GET /ops/session`; expiry → the
   door, and after login **restore the tab the operator was on** (R7 — record the
   mechanism, e.g. the door preserving the intended path). The ops layout must not
   share the reader session/state seams (separate cookie, S9).
2. **The ops chrome** — every authenticated section is a complete page: top ops
   bar (the six tabs · the lock chip live (`state`, held-since when held; the
   degraded `unknown` state rendered honestly) · a ticking KST clock · 로그아웃)
   and the bottom status footer. Idiom: `class="cosmos"` token scope, **zero
   ornament** (no starfield, shooting stars, glows, brackets, panel-glow); panels
   opaque `#0e1a15` + 1px `--border-strong`; chrome labels Korean; codes,
   identifiers, and stage output raw English mono. Desktop-only — no mobile
   layout, fixed min-width allowed.
3. **개요** — the four status tiles (`gates summary` verbatim values); the beat
   schedule table from the served config (never hardcoded); the 최근 실행 표 from
   the run log (per-row 시각 KST · trigger · per-stage counts + spend + the ▷ cost
   line **verbatim** — ▷ stays ▷ here); **the 「실행 기록 없음」 alert-ink row
   derived from the schedule + log** when a scheduled beat did not run (client
   derives it from the two served facts — implement per R7, never silent); budget
   exhaustion in reported style (alert is for not-run only); the lock chip
   (already in the bar — the tab shows its detail); 가동 전 미결 items read from
   the served decisions source per S9's payload (render what's served).
4. **게이트 대기열** — reason_code counts (code mono + served `reason_ko` +
   count); rates with the **served denominator** (691 distinct / 710 stored —
   print the basis, S9 ships both); row inspect (field + 한국어 이름, status,
   reason, quote/span or the 「없음」 state — no placeholder), rcept_no verbatim +
   DART link; the event-state table verbatim; the four blocking flags with their
   code-owned Korean; suppression codes **raw English, no mapping, no fallback**;
   철회 inspect (notice + note verbatim + gate-passing-unrendered count + blocked
   list).
5. **정확도·비용** — render what S9 serves from `evalset report`: the judged_by
   block **above the numbers**; the numbers always with their required
   decompositions in the same panel (과차단 성분 · 12.2% (77/633) · ③ 44% 4분해 ·
   strict 미스 = D4 — note: the served report is the frozen artifact; if its
   sentences still describe pre-S20 D4 as open, render them verbatim — the report
   is the source, not your knowledge); the quota bar with its window labeled
   (cumulative, per S9); LLM spend from the served `extraction_call` aggregates.
6. **대화 로그** — the full signed page over the port's empty results: filters
   (유형, 거절 카테고리), cursor pagination, the expanded-row conversation replay
   anatomy — all rendering the honest **0건** empty states (no 「준비 중」, no
   invented strings; the empty-state copy must come from the record/served data).
   Read-only.
7. **사용자** — two tables, no join: 독자 계정 (served: email · 가입일 · 종목 개수
   · 알림 설정 · the 샘플 로드 여부 column rendering the absent key honestly —
   decide the faithful rendering of an absent fact (e.g. `-`? no — R7 forbids
   placeholders where a value would be; render what states-and-trust allows and
   record it); count-only portfolio, nothing else) and 익명 세션 (the port's
   aggregate — 0건 now) with the two-way 대화 로그 cross-link wiring in place
   (it links into the log tab's filter even while empty). Read-only.
8. **피드백** — the save_feedback queue list anatomy + the signed empty state
   「대기 0건 — save_feedback 호출이 아직 없습니다」; no status bits, no merge with
   vocky (no vocky view at all this slice — `P5.S18`).

## Constraints

- **Read-only everywhere**; the only POSTs are the door's login/logout.
- Every number from the served payloads; nothing derived client-side except the
  R7-mandated 실행-기록-없음 derivation and the KST clock display.
- No reader chrome, no reader links in; nothing in the reader surfaces links here
  (S9 verified — keep it true; the `/ops` pages must not use `SiteChrome`).
- Copy: R7 literals + served strings only, cited in a `copy.ts`.
- Primitives: reuse only what fits the ops idiom (mono/DDay conventions); no
  CraftPanel; tokens untouched.
- No new dependencies.

## Validation

- `npm run build` + `typecheck` + `smoke`; Python 113 untouched.
- Dev + headless-Chrome pass — launch uvicorn with a throwaway credential as
  **process env vars** (`MIJUAL_OPS_ID=… MIJUAL_OPS_PASSWORD=… .venv/bin/uvicorn
  …`), never editing the operator's `.env`: door uniform failure (wrong ID vs
  wrong password render identically); login → 개요 tiles matching
  `python3 -m mijual.gates summary` output; run-log rows present (S9's check run
  wrote some), the 실행-기록-없음 derivation exercised (e.g. by asserting against
  the served schedule); tabs all render complete pages; 게이트 대기열 rates print
  the 691 basis; 정확도 markdown matches the served artifact; 대화 로그/익명
  세션/피드백 honest zeros with full anatomy; reader cookie rejected; `/ops` not
  reachable from any reader-page link (assert no `/ops` href in reader HTML);
  desktop 1440 screenshots (no mobile pass — desktop-only is signed). Log out;
  stop everything.
- `python3 scripts/workflow.py validate`.

## Wrap-up

`result.md`; `phase.md` *Findings & Notes* (the ops component idiom for S18's
vocky view; the tab-restore mechanism; the absent-fact rendering decision) and
*Doc impact* (`frontend`, `security` — the door UX + linked-from-nowhere verified;
`operations`; `qa`). Structured verdict. No commits, no status transitions.
