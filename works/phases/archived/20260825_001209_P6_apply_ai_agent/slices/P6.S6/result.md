# Result — P6.S6: 전용 페이지 + 모바일 + 질문 스트립 + 진입점

The `/ask` shell P5 left behind is gone. In its place: the frameless dedicated
page (chat directly on the page, one 340 rail as the only panel), the ≤480px
full-width page with the sticky 44px bar, the 질문 스트립 on event detail, the
event page's ambient 범위, and an entry-point audit measured in a real headless
browser against a **spend-free** scripted agent. No backend file changed; the
store gained nothing — the page is S5's second view over S5's one store.

## What landed

**New** (all under `frontend/`):

| File | What it is |
|---|---|
| `components/ask/AskPage.tsx` | 전용 페이지 — the frameless chat + the 340 rail (a `CraftPanel`), the sticky bar, the scoped preset row, `close()` on arrival |
| `components/ask/AskPage.module.css` | its layout: mobile stack → `grid-template-columns: minmax(0,1fr) 340px` at ≥481px, `position: sticky` bar |
| `components/ask/QuestionStrip.tsx` | 질문 스트립 — preset chips + the 직접 질문 입력 → chip; used by event detail **and** by the page |
| `components/ask/Strip.module.css` | 가로 스크롤 한 줄, 타깃 ≥44px |
| `components/ask/presets.ts` | the generation rule (gate-passing fields → chips), with its provenance |
| `components/ask/AskPageScope.tsx` | the event page's ambient 범위, with the lifecycle documented in the file |
| `components/event/fieldOrder.ts` | `FIELD_ORDER` + `STORY_FIELD` moved out of `Fields.tsx` as plain data, so the page's row order and the strip's chip order are one list |

**Edited:** `app/ask/page.tsx` (replaced whole — it now renders `<AskPage/>` and
nothing else), `components/ask/copy.ts` (+`ASK_ABOUT_KO`, `VERIFIED_ONLY_KO`,
`FORFEITED_QUESTION_KO`/`FORFEITED_FIELD`, all transcribed with citations),
`components/ask/index.ts` (exports), `components/ask/Ask.module.css` (one
`@media (max-width: 480px)` block giving the composer 44px controls — the widget
never renders there, so the 36px desktop composer is untouched),
`components/event/EventDetail.tsx` (mounts `AskPageScope` + `QuestionStrip`),
`components/event/Fields.tsx` (imports the moved constants).

**Not touched:** `src/**` (pytest identical), `lib/ask.ts`, `lib/api.ts`,
`components/ask/{Answer,Composer,InlineCitation,AskWidget,AskLauncher,AskSurface}.tsx`,
`components/chrome/**`, `docs/reference/design/**`.

## Validation

| Command | Outcome |
|---|---|
| `cd frontend && npm run typecheck` | **pass** (clean) |
| `cd frontend && npm run build` | **pass** — 15/15 pages; `/ask` is `○ (Static)` |
| `cd frontend && npm run smoke` | **pass** — tests 15, fail 0 (unchanged from S5) |
| `.venv/bin/pytest` | **pass** — exit 0, **136 collected / 136 passed** (baseline held; no backend change) |
| CDP @390 overflow sweep | **0 px** horizontal overflow on `/ask`, `/events/20260724000546`, the 철회 event, and `/` |
| CDP flow @390 + @1440 (scripted agent) | **pass** — see below |
| `python3 scripts/workflow.py validate` | **pass** |

### The browser measurements (headless Chrome over CDP, `next build && next start` + uvicorn)

Two API instances were used, both local: the live-corpus app for the overflow
sweep, and — for anything that would have called a model — a **spend-free** one,
`create_app(Settings(), agent_client=lambda: ScriptedModel(...))` with S4's own
seam and the test corpus (`tests/test_agent_tools._corpus`) over in-memory
SQLite. **No live model call was made in this slice.**

Overflow / literals:

- `/ask` @390: `scrollWidth == clientWidth == 390`, `position: fixed` **none**,
  one `position: sticky` (the input bar), smallest interactive target **44px**.
- `/ask` @1440: rail **exactly 340px** with a 1px border; the chat column's
  computed `border-top-width: 0px` and `background-color: rgba(0,0,0,0)` —
  **프레임 없음**; zero fixed elements, i.e. **no launcher on the page**.
- `/events/20260724000546` @390: 0 px overflow with the strip in place; chips
  all **44px** tall; the strip's row scrolls (`scrollWidth 1009 > clientWidth
  358`) instead of widening the document; the six chips read
  `신주인수권증서 상장·매매기간` · `청약 취급처 (대상자별 증권사 + 청약일)` ·
  **`실권주는 어떻게 처리되나요?`** · `초과청약 조건 (비율)` ·
  `발행가액 산정방법 (1·2차·확정 산식)` · `직접 질문 입력 →`.
- 철회 event @390: strip present with **only** the 직접 질문 입력 → chip (no
  presets), 0 px overflow.
- `/` @390: unchanged — 0 px document overflow (P5's starfield still the only
  thing crossing the edge, inside its own fixed `.backdrop`).

Flow (mobile, scripted agent):

1. detail @390 → press the `신주인수권증서 상장·매매기간` chip → **navigates to
   `/ask`** with 범위 `범위: 계양전기 · 20260724000546`, the 도구 행
   `이벤트 읽기 → 계양전기 · ① 유상증자 · 20260724000546`, the sentence with chip
   `1`, and the footer `근거 1건 · 20260724000546 · 2026-08-22 21:49 KST`.
   Composer input **44px**, sticky bar present, 0 px overflow.
2. tap the chip → the in-place citation block opens **full width** (306px inside
   a 332px answer at 390) with `max-height: 180px` and `overflow-y: auto` — R6's
   「인용 블록 전폭 (180px 캡 + 스크롤)」, measured on the verbatim-quote variant
   and on the API-tier variant.
3. `history.back()` → back on the detail page with the thread intact
   (`sessionStorage` turns `[신주인수권증서 상장·매매기간/done]`).
4. `sessionStorage` keys throughout: **`["mijual.ask.thread"]`** and nothing
   else — this slice writes no key of its own.

Flow (desktop, scripted agent):

5. detail @1440 → 직접 질문 입력 → opens the widget **440×620** in the event's
   범위 and sends nothing; the widget header's `external-link` → `/ask` with the
   widget gone (zero fixed elements), the rail at 340 and the **same thread**.
6. Ambient 범위 lifecycle, fresh profile: launcher on the detail page opens at
   `범위: 계양전기 · 20260724000546`; `×` → `범위: 전체 공시`; reopening on the
   same page **keeps 전체 공시** (a reader's choice is not overridden).

Entry points: nav third slot `AI 질문 → /ask`; footer bottom row
`AI 질문 → /ask`; mobile sheet rows **48px** (`내 종목 조회` · `관제 현황판` ·
`AI 질문` · `로그인` · 의견 보내기) and the 메뉴 button **44px**.

## Decisions taken (the full list is in `phase.md` note 23)

- The page is a **view**: no second store, no lifted state, no sessionStorage
  write. It calls `close()` on mount, which is 「위젯이 열려 있으면 닫고
  리다이렉트」 for every way in (nav, footer, typed URL), not just the header
  icon.
- **Rail contents** — the record fixes 340 and 「레일만 패널」 and writes no
  contents (there are no R6 cards in this repo), so the rail carries the four
  signed things this surface has: the 범위 chip + ×, 「검증된 필드만 근거로
  답합니다 — 모든 답에 원문 인용」, the agent intro, and the 세션·저장 line. On
  ≤480px it stacks above the chat.
- **Preset rule**: served `korean_name` verbatim, in the page's own field order,
  minus `correction_interpretation`; `forfeited_share_method` renders R6's own
  question 「실권주는 어떻게 처리되나요?」. No sentence template was invented.
- **No auto-scroll on the page** (the widget scrolls its own 620px box; scrolling
  the document under a reader is the ambient motion R1 keeps off data surfaces).
- Presets on `/ask` come from a client `GET /events/{rcept_no}`; a 철회 event or a
  failed read yields **no chips and no message**.

## Flags for `P6.S7` / `P6.REVIEW`

1. **「메뉴 첫 행」** — R6 §Mobile writes 「메뉴 첫 행 ≥44px」 while R6 §Surfaces
   fixes 「nav 세번째 자리 「AI 질문」」, and the mobile sheet mirrors the nav. P5's
   shipped order was kept (AI 질문 = third row, 48px ≥ 44px, 메뉴 button 44px)
   rather than silently reordering the signed chrome. If the record is read the
   other way it is a one-line change to the sheet's list in `chrome/Nav.tsx`.
2. **Rail contents** (above) — nearest-signed, not transcribed from a Page card.
3. **Strip heading** 「이 공시에 대해 질문」 is R6-2's panel copy reused for the
   affordance the panel became.
4. **Chip width** — a preset chip is a whole field label, so
   「청약 취급처 (대상자별 증권사 + 청약일)」 is a wide chip in the scrolling row.
5. Desktop composer button measures 39px (36px + hairline) — the widget's signed
   size; ≥44px is the ≤480px rule and is met there.
6. Carried from S5, unchanged: 「직접 질문 입력 →」 as the composer's idle button
   and 「AI 질문」 as the field's accessible name.

## Deviations from `plan.md`

- The plan asked to "confirm [the mobile menu's AI 질문 row] is the first row";
  it is the **third**, and the conflict inside the record is flagged (above)
  rather than resolved by reordering P5's chrome.
- The plan's optional 「spend-free wire sanity … if convenient」 was done in full
  (the scripted app drove the browser end to end), which is why the citation cap,
  the tool row and 뒤로가기 are measured facts rather than code claims.
- One small refactor the plan did not name: `FIELD_ORDER`/`STORY_FIELD` moved
  from `components/event/Fields.tsx` into `components/event/fieldOrder.ts` so the
  strip and the page sort by one list. Behaviour identical (build + typecheck +
  the 390/1440 renders confirm the page is unchanged).
