# Result — P5.S13: Event detail ①②③ (R3)

The event detail page exists at `/events/[rcept_no]` and renders all three rights types plus
every state R3 draws, over the live `GET /events/{rcept_no}` and `GET /events/{rcept_no}/corrections`
endpoints `P5.S3` built. **0 new dependencies. No primitive, token, chrome or landing file was
touched.** Every Korean string on the surface is transcribed with its citation in
`components/event/copy.ts`; nothing was invented. Python suite untouched at 113.

## What landed

| file | what it is |
|---|---|
| `frontend/app/events/[rcept_no]/page.tsx` | the route — `connection()` + `await params` + `getEvent`, `ApiError 404 → notFound()` |
| `frontend/components/event/EventDetail.tsx` | composition in R3's order; the 철회 branch; the sparse-② closing line; the provenance line |
| `frontend/components/event/Header.tsx` | crumb, craft-panel header, identity rule, countdown side, window/state line |
| `frontend/components/event/Fields.tsx` | the `// {name}` sections and every per-field value renderer (exports `FieldValue`, reused by the CorrectionStory) |
| `frontend/components/event/Offering.tsx` | ① 환산 블록, 청약 결과 inset, 발행사 기재 불일치 |
| `frontend/components/event/Convertible.tsx` | ②'s six-value API fact strip |
| `frontend/components/event/Withdrawn.tsx` | the 철회 notice + its 정정사항 evidence |
| `frontend/components/event/Corrections.tsx` | the 정정 strip and the CorrectionStory it opens (`"use client"`) |
| `frontend/components/event/copy.ts` | every Korean string, one citation per entry |
| `frontend/components/event/Event.module.css` | the whole surface's styling (904 lines) |
| `frontend/lib/routes.ts` | **edited** — `+ stockPath(corpCode)` for the 환산 link-out |

## Validation

| command | outcome |
|---|---|
| `npm run build` | pass — compiled; `/events/[rcept_no]` is `ƒ` (request-time), as intended |
| `npm run typecheck` | pass |
| `npm run smoke` | pass — 3/3 |
| `.venv/bin/python -m pytest` | pass — **113**, exit 0, unchanged |
| `python3 scripts/workflow.py validate` | `Workflow validation passed.` |

### Browser pass — real headless Chrome over `localhost:3000` (`npm run start`), live API

13 real pages × 2 viewports (1280×900 and 390×844 mobile-emulated) plus two 404s. Automated
sweep result on every one of the 26 renders: **no `▷`, no `[object Object]`, no `undefined`/`NaN`/
`null`, no stray English token** (`original` / `TBD` / `N/A` / `Error` / `Loading`), **zero
`position: fixed`** elements (P6's corner stays clear), **zero horizontal overflow at 390px**.
Every one of R3's named mobile targets measures exactly 44px on every page — crumb 79×44, DART
link **308×44 full-width**, 내 보유량으로 환산 149×44, 정정 이력 71×44. The dev console is clean
(no hydration warning).

What each fixture proved:

1. **priced ① 한화솔루션 `20260720000067`** — chain 확정발행가 22,100원 → 할인율 20.0% → 증서 1주
   이론가치 5,525원`「추정」` → 배정비율 **0.2465120994** (all ten decimals). 청약 결과 inset:
   발행 42,165,422주 · 청약 38,430,497주 · 소멸 3,734,925주 (8.86%) · 소멸가치 206.4억원`「추정」`
   하한 165.5억원`「추정」`. **The multi-part citation renders both addends** — the 청약 chip opens
   `38,427,609` + `2,888` (= 38,430,497) against `20260730000366`, never one addend and never a
   sentence joining them (D4 / `P5.S20`).
2. **unpriced ① 계양전기 `20260724000546`** — `발행가 확정 전` chip + mono 확정 예정 date, and
   **no 원 amount anywhere on the page**; 할인율/배정비율 still render (ratios, not money).
   Open window → live-green `거래 가능 · 마감 D-n`.
3. **추후결정 ① 경남제약 `20260623000409`** — `StateBadge 추후결정` + "카운트다운 없음 — 일정이
   공시상 미정", **no date anywhere near it**.
4. **rich ② 대동기어 `20251016000315`** — six-value fact strip (전환가액 15,552원 · 오버행 6.68% ·
   전환 시 주식수 643,004주 · 권면총액 100.0억원 · 발행방법 사모 · 만기 2030-10-24) above the 본문
   fields, its citation being the filing number `20251016000315 ↗`. 리픽싱 and 콜·풋 render their
   `detail` strings with the stored range only as the locked caption.
5. **sparse ② 트리니티항공 `20250808000003`** — fact strip + the locked closing line "공시 본문에서
   확인된 추가 조건이 없습니다 — 위 값은 DART 공시 API 기준입니다", **no placeholders, no empty
   section**. Governing 전환청구 개시 at D-DAY → `진행 중`, **never 종료**.
6. **repaired ② 알파AI `20250918000398`** — serves **its own** bond (전환가액 2,000원 / 권면총액
   55.0억원 / 만기 2028-09-22), i.e. `P5.S5`'s identity-scoped pairing holds through the page;
   `정정 반영` in the meta line; both option blocks carry the locked "연속 기간 아님" caption.
7. **corrected ② HLB테라퓨틱스 `20260807000003`** — the rail's three versions render
   (2025-11-20 원본 · 2026-08-07 기재정정 ×2) with **no row marked 현재 읽는 버전**, because this
   event has no readable 본문 at all; the rail states that by filling nothing rather than by
   guessing a current version.
8. **③ with 매수예정가 세기상사 `20260713000345`** — 매수예정가격 **5,649원** as a standard row
   under `// 발행 조건` with its verified citation (`매수예정가격 5,649`); the 2단계 structure with
   both steps `기한 지남`, the locked dependency sentence, and 통지 방법 / 접수처 rows.
9. **③ without it 미래에셋비전스팩7호 `20260512000669`** — **no 매수예정가 row at all** (absent
   means absent), 2단계 structure intact.
10. **field-absent ③ 아시아나항공 `20260713000482`** — "현재 버전 공시에 없음", no countdown, and
    the CorrectionStory shows the passage's deletion as `(정정 후 본문에서 삭제됨)`.
11. **철회 썸에이지 `20260805000454`** — the notice "이 유상증자는 철회되었습니다" replaces the body:
    **0 field rows, no countdown, no old dates**, and below it only the 정정사항 evidence
    (유상증자 결정 → 유상증자 철회) with the served withdrawal quote as its `Citation`.
12. **불일치 대한광통신 `20260223002079`** — the two readings side by side, each with its own
    citation into the same filing (신주인수권증서 청약 실권주 **2,117,937주** vs 발행 − 청약
    **2,083,302주**, the derived one showing its 발행 23,465,365주 / 청약 21,382,063주 inputs),
    the locked header and the footer stating which reading the totals use. **Never reconciled.**
13. **corp_name trap 풍전약품 `20250930000508`** — DART master name as the H1, with the locked
    one-line 본문 표기 sentence beneath (also seen on 트리니티항공 / 알파AI).
14. **404** — `99999999999999` and the flagged `20260709000212` both render the not-found
    experience (see deviation 3).

Screenshots for the whole pass are in the session scratch directory (not committed).

## Deviations from `plan.md`

1. **The 환산 CTA links to `/stocks/{corp_code}`, not to `/stocks?<param>`.** The plan asked me
   to "record the query-param convention — S14 consumes it". `P5.S4` already built 조회's route
   map, and its stable handle is the **corp_code path segment** (`/stocks/00162461`, which
   `isActiveRoute` already knows); `?q=` is the *search* input the landing hero posts, and a
   `corp_code` is not a search term. So the convention S14 consumes is the path, and
   `lib/routes.ts` now states it once as `stockPath(corpCode)`. Recorded in `phase.md`.
2. **The CorrectionStory is an in-page disclosure, not a route.** The plan left this to me
   ("decide: route or in-page view; record"). A route needs its own way back, and the only crumb
   this product owns is "← 관제 현황판", which points at the board, not at the event — a second
   crumb would be copy nobody signed. The 정정 이력 button carries its state in `aria-expanded`
   and fetches `/corrections` on first open.
3. **A not-found `rcept_no` renders the framework's own 404 inside the chrome**, and no Korean
   404 copy was written. The plan says "no invented Korean beyond what exists", `P5.S3` note 5
   says a non-renderable event is a 404 that **never explains itself**, and the copy inventory
   holds no 404 sentence. Writing one would be a design change. Flagged for `P5.S19` /
   the operator in `phase.md` — the chrome around it is right, only the sentence is English.
4. **The 정정 이력 button label is R3's literal, and stays flagged.** Rendered as `정정 이력` per
   the plan's instruction; the phase's open question about it is untouched and now carries this
   slice as a second site.
5. **The superseded-version grey annotation is not rendered.** R3 says rows "*may* carry" the
   locked reason string; the reader payload carries **no gate reason at all** (that is operator
   truth, `states-and-trust.md` §4 / D-14), so there is nothing to render and nothing was
   invented.
6. **The rail's earliest row shows no `correction_kind`.** The value is Korean for every
   correction (기재정정 · 첨부정정) and the English token `original` for the first filing; printing
   that token on a Korean reader surface would be worse than the truth the rail already shows.
7. **No 예정발행가 is printed on an unpriced ①**, though R3 writes the chain's first link as
   "예정/확정발행가" and the payload carries `planned_price`. Three records state the governing
   rule absolutely — money never appears before 확정발행가 — and R3's own unpriced state replaces
   the money with the chip. Reasoned in full in `Offering.tsx`'s header comment.
8. **No 질문 스트립 on the page**, per DECOMP note 8 — R6's preset-chip strip on detail is **P6's**.
   Its absence here is a phase boundary, not a dropped element.

## Doc impact

One line appended to `phase.md`'s *Doc impact* list naming **`frontend`** (the detail surface's
durable component/composition truth, the field-label rule, the three-state citation rendering,
the `stockPath` convention), **`experience`** (what the reader sees and what the page refuses to
say — the state pages, absent-means-absent, the unreconciled 불일치, the CorrectionStory), and
**`qa`** (the frontend check now covers the detail surface: build/typecheck/smoke green, Python
113 untouched, and the 13-page × 2-viewport headless-Chrome pass with its measured invariants).
`P5.REVIEW` consolidates them; this slice created **no** doc version.
