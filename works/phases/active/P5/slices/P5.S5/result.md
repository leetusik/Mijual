# Result — P5.S5: Identity-scope the API-backed gates (promoted D1)

**Status: done.** The ② gate failures D1 was filed for are gone, the three named 정정 filings no
longer sit on another corp's 사채, and every landing/board number the phase measures is unchanged.

## What the defect turned out to be

N62 named 3 filings and 4 gate failures. Measured against today's corpus (2026-08-22) the failure
mode is **wider than the note and narrower than `hint_mismatch`**:

- **6** ② gate failures on exposable events, **5** of them on the three named filings
  (엑시큐어하이트론 `20260630000509` ×3, 알파AI `20250930000580`, 제이에스링크 `20251204000439`);
  the 6th (에이럭스 `20250908000110` `option_schedule/span_unresolved`) is a citation defect, not a
  pairing one, and is untouched here.
- **653** versions carry `hint_status='mismatch'`, but only **46** of them sat on an event the
  product actually renders. Blocking on the flag (N63's rejected shape) would still take down the
  whole ① board; the rest of the mismatches are not foreign documents at all:
  - **201** name a date **exactly 1 day** off their own event's key — DART's 접수일 is the next day
    for an after-hours 제출 (알파AI's original is `20250731000550` *dated* 2025-08-01);
  - **111** name a date one of the event's **own filings** carries (`rcept_no[:8]` or `rcept_dt`);
  - the rest sit on suppressed placeholders / `superseded_by_pairing` residue that renders nowhere.
- Of the 46 renderable ones, **22 were not foreign either**: the corp's *own* earlier 사채 sits
  exactly one 접수일 away (알파AI 2025-05-07 → event 2025-05-08, 차AI헬스케어 2025-03-27 → 2025-03-28,
  아리바이오홀딩스 2025-04-29 → 2025-04-30). Those are mis-*attachments*, not unknown originals: the
  right repair is to send them home, not to mint a twin — minting one would have manufactured
  D2/N81's duplicate-exposable disease.

## The rule that landed

In `src/mijual/bodydoc/backfill.py::_apply_hint` (**not** `collect/pairing.py` — see *Deviations*),
when the 본문 hint names **no** event of this corp+subtype:

1. **Self-evidence wins, always.** The hint names a filing this event already holds
   (`rcept_no[:8]` or `rcept_dt`), or sits within `HINT_SKEW_DAYS = 7` of the event's key → nothing
   moves, the version keeps its `mismatch` label exactly as before. This is the guard that keeps
   N31's ±7-day skew cases — including every ① one — untouched.
2. **Otherwise, and only on a *rendered* event** (`Event.exposure_state in {exposable, withdrawn}`):
   - a **unique** other event of the same corp+subtype within `HINT_NEAR_DAYS = 1` of the hint →
     the version is **reattached** there (the existing P2.S3 move path, one day of tolerance added).
     Ambiguity resolves to nothing; measured corpus-wide, **no** hint has two events within 3 days.
   - nothing at all → the version is **split** onto a chain head `ensure_event(corp, subtype, hint)`,
     suppressed `foreign_correction_head` and flagged `hint_foreign_split`, with
     `hint_status='split'`. Extractions and their calls follow the version (`_move_derived_rows`),
     so gates re-judge them against the document they actually belong to.
3. Anything else keeps P2.S3's behaviour byte for byte.

Three supporting changes: `hint_status='split'` is sticky and counts as `pairing_is_resolved`
(`db/models.py`); `_retire_emptied` now also relabels an event whose **every** version left
(two ② events were nothing but another bond's 정정); and `collect/runner.py::persist` refuses to
re-place a `rcept_no` whose identity a 본문 hint has settled elsewhere (`_identity_owner`) — it
stores that run's `list`/detail snapshot **on the owning version instead**, so evidence is never
dropped and a split head can still acquire the API row its own gates want. Without it a later wider
re-collection — N78(a) proposes one — would silently undo the repair, re-spend requests on a
duplicate 본문, and then hit the head's unique constraint.

## Commands run (all offline: 0 OpenDART requests, 0 model calls)

| command | outcome |
|---|---|
| `.venv/bin/python -m mijual.bodydoc --no-fetch --offline backfill` | pass 1: 26 split + 22 reattached, 14 heads minted, 2 events emptied |
| … same command, pass 2 | 1 more version split (a head minted in pass 1 became an exact target) |
| … same command, pass 3 | **0 moves — converged and idempotent** |
| `.venv/bin/python -m mijual.gates run` | 1,359 events re-judged, 649 field rows, verdicts + 철회 flags + exposure states re-derived |
| `.venv/bin/python -m mijual.estimate snapshot` | 545 ① precomputed, 32 lapse rows — unchanged from before |
| `.venv/bin/python -m pytest` | **89 passed, 1.2 s** (87 baseline + 2 new pairing tests) |
| `python3 scripts/workflow.py validate` | passed |
| `curl` sweep over 107 touched events + the board/summary/detail/corrections endpoints | no 5xx, no foreign citation |

A `pg_dump -Fc` of the pre-run corpus is at `var/preP5S5.dump` (gitignored); the three run reports
are `var/p5s5-backfill{,-2,-3}.json` and `var/p5s5-gates.json`.

## Before / after

| measure | before | after |
|---|---|---|
| **② gate failures on exposable events** | **6** | **1** (에이럭스 only — a span defect) |
| … the D1 five | 엑시큐어하이트론 ×3 · 알파AI ×1 · 제이에스링크 ×1 | **all gone** |
| exposable events | 488 | **488** |
| … by rights (board tabs) | 50 / 422 / 16 | **50 / 422 / 16** |
| ranked board rows · ② 진행 중 · 추후결정 | 389 · 57 · 4 | **389 · 57 · 4** |
| 30일 이내 · 소멸 앞둔 · 실적보고서 | 33 · 15 · 69 | **33 · 15 · 69** |
| headline / floor / 소멸률 | 718.1억 / 548.7억 / 0.1402 | **identical** (71,812,971,649 / 54,871,647,923) |
| ① gate rows on exposable events | 261 passed / 4 tbd / 4 failed | **identical** |
| ① renderable field instances | 매매기간 48+2 추후결정, 청약 취급처 48+2, … | **identical** |
| ② gate rows on exposable events | 123 passed / 21 n/a / 6 failed | 120 / 22 / 1 |
| events (total) | 1,345 | 1,359 (**+14** chain heads, all suppressed) |
| ② withdrawn | 8 | **6** |
| filing versions · extractions | 3,990 · 649 | **3,990 · 649** (0 added, 0 removed) |
| `hint_status` | mismatch 653 · reattached 76 · duplicate 364 | mismatch 593 · reattached 98 · duplicate 375 · **split 27** |

**Every row of the 488 is the same event as before** — the only state transitions were 14 brand-new
suppressed heads and 2 events going `withdrawn → suppressed`. The ② field-row drop (150 → 143) is
the foreign documents leaving: three exposable events stopped reading another bond's 본문.

The two ② `withdrawn` pages that disappeared are the finding, not a regression: 드래곤플라이
`cvbdIsDecsn/2025-03-20` and 캔버스엔 `cvbdIsDecsn/2025-01-20` held **no original and no detail row of
their own** — every version was another bond's 정정, and the 「이 사채 발행은 철회되었습니다」 notice
they rendered came from that foreign document. The 철회 evidence moved with the versions and is now
recorded on the head events (flag `withdrawn`, suppressed because the identity is unverified).

## The three-corp check (live Postgres, `uvicorn` on :8011)

| corp | before | after |
|---|---|---|
| 엑시큐어하이트론 | `/events/20260630000509` rendered event 751 with 3 failing 본문 fields from a **2024-09-06** bond | `/events/20250910000482` → 전환가액 **692** · 전환청구 개시 **2026-09-18 (D-27)** · 만기 2028-09-18, no foreign fields; rail = its own original only; the 정정's own URL **404s** |
| 알파AI | `/events/20250930000580` rendered event 772 with a failing `lockup_release` from a **2025-05-07** bond | `/events/20250918000398` → 전환가액 **2,000** · 개시 **2026-09-22 (D-31)** · `lockup_release` + `option_schedule` **passing**, both from its own 본문; rail = 9 versions, all its own |
| 제이에스링크 | `/events/20251204000439` rendered event 877 with a failing `lockup_release` from a **2024-12-17** bond | `/events/20250922000234` → 전환가액 **22,232** · 개시 **2026-10-02 (D-41)** · 조기상환 + 보호예수 + 리픽싱 all passing from its own 본문; rail = its own original |

Every `Figure` on those pages carries an `rcept_no` the event owns — checked as an invariant over
**all 488** exposable events: **0** extraction rows cite a filing their event does not hold.

## Deviations from `plan.md`

1. **The fix is in `bodydoc/backfill.py`, not `collect/pairing.py`.** The plan pointed at
   `pairing.py` / `runner.py` (`place`, the `pair_correction` call site). Those run at collection
   time from `list.json` alone and **cannot see a 본문**, so "the hint names no collected original"
   is not expressible there. The hint verdict already has one home — `_apply_hint` — and it is
   offline and re-runnable, which is what made a zero-request repair possible. `runner.py` still
   got the one change it *can* own: `persist` no longer re-places a filing whose identity a hint
   has settled.
2. **The rule needed a second arm the plan did not anticipate.** 22 of the 46 renderable cases are
   the corp's own bond one 접수일 away; splitting them (the plan's single recommended shape) would
   have minted duplicate events. Measured first, then scoped: `HINT_NEAR_DAYS = 1`, unique-or-decline.
3. **Scope: rendered events only.** The plan's literal "no-candidate" test fires on **398** versions
   corpus-wide; 352 of those sit on suppressed placeholders and retired residue that no surface
   reads, and moving them would restructure ~200 dead records for no product gain (and could clear
   `hint_split_evidence` — a *blocking* flag — on events whose exposure has never been measured).
   The scope is the harm D1 names: an event the reader renders. Recorded in `phase.md` as the one
   knob a later slice may widen, with the measurement to do it against.
4. **The heads are suppressed, not exposed.** The plan preferred "each bond its own truth" over
   field-level blocking. It gets its own **record**, keyed on the date it declares, healing
   automatically if the original is ever collected — but not a page: with no original and no
   `cvbdIsDecsn` row there is nothing verified to render, and for ① it would have put an offering of
   unknown 증자방식 on the board. `unpaired_correction`'s meaning, reused with its own reason code.
5. **Tests live in `tests/test_collect.py`**, not `test_bodydoc.py`: that module is skipped whole
   when the gitignored P1 cache is absent, and these two cases need no fixture at all (in-memory
   SQLite, hand-built rows). 87 → 89, still ~1.2 s.

## For the phase review

- No web/`present`/`reads` change was needed; `resolve_event`'s renderable-first rule already
  handles a `rcept_no` that now lives on a suppressed head plus a suppressed twin (both 404).
- One side effect to know: an offline repair run calls `ensure_event`, which bumps
  `Event.last_seen_at` — the landing's 기준시각 (`max(last_seen_at)`) therefore reads as "just now"
  after a maintenance pass that made no OpenDART call. Recorded in `phase.md` for `P5.S9`/P4.
