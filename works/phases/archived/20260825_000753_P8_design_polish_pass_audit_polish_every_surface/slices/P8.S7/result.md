# `P8.S7` — R10 applied to the event detail surface

Built the signed R10 record (`docs/reference/design/rounds/10-event-detail/`) on `/events/[rcept_no]`,
plus the round's §8 not-found surface. Eleven files changed, three added. Nothing under
`docs/reference/design/rounds/**` or `docs/versions/**` was touched, no doc version was cut, no state
was transitioned and nothing was committed.

The durable, cross-slice half of this write-up (what later surfaces inherit) is in `phase.md`
§`P8.S7 — R10 applied`; this file records the validation, the readings and the deviations.

## 1. What landed

| file | what |
|---|---|
| `frontend/components/Citation.tsx` · `Citation.module.css` | the §6 re-cut: 32/44px trigger, open state on the trigger, **overlay popover** (opaque `#0e1a15`, 2px `--live` edge, 200px scroll, `×`/outside/Esc, focus return), multi-part passages, + a viewport clamp (reading 5) |
| `frontend/components/event/Event.module.css` | a full port of `detail/r10-detail.css` — header grid, chain cells, fact frame, sections, 절차 block, 정정 밴드 + story, and the whole `@media (max-width:767px)` stack |
| `frontend/components/event/Header.tsx` | §1: `header` (no inner panel), `.hid`/`.cd` columns, three countdown forms, the §1 window-state table, 담기 line relabelled |
| `frontend/components/event/EventDetail.tsx` | the page is **one `CraftPanel`**; 질문 스트립 attached under the header; `rceptNo`/`rightsType` passed down |
| `frontend/components/event/Offering.tsx` | §2 chain: hairline instrument cells, **no arrows**, `.chainfoot` 환산 button |
| `frontend/components/event/Convertible.tsx` | §3 fact frame 3×2 + the mono `.fsrc` source row |
| `frontend/components/event/Fields.tsx` | §4 절차 block (`h2` + pills + `h3`), §5 rows/eyebrows/`.secsrc`, the absent-procedure row (reading 3), `aria-label` on eyebrows (reading 6) |
| `frontend/components/event/Corrections.tsx` · `Withdrawn.tsx` | §7: band sentence as `h2`, 「접기 ×」, **two tagged sides** instead of an arrow column (the 철회 정정사항 uses the same grammar) |
| `frontend/components/event/fieldOrder.ts` | R10's citation-density rule as data (`fieldCites`) |
| `frontend/components/event/copy.ts` · `lib/copy.ts` · `auth/copy.ts` | the round's strings (§9 of `copy-inventory.md`'s new tail) |
| `frontend/components/auth/DeadlineOffer.tsx` | additive `className` only |
| `frontend/app/not-found.tsx` · `RequestedPath.tsx` · `not-found.module.css` **(new)** | §8's Korean not-found |
| `frontend/app/events/[rcept_no]/page.tsx` | doc comment only (the surface now has its own 404) |
| `docs/reference/design/grounding/copy-inventory.md` | hand-registered **「R10 additions」** tail |

## 2. Validation

| command | outcome |
|---|---|
| `cd frontend && npm run typecheck` | pass (clean) |
| `cd frontend && npm run smoke` | pass — **16/16** |
| `npm run build` (production, scratch copy) | pass — exit 0, 15 routes; `/_not-found` static, `/events/[rcept_no]` dynamic |
| `.venv/bin/python -m pytest` | pass — **142** |
| `python3 scripts/workflow.py validate` | `Workflow validation passed.` |

The build was run on a copy of `frontend/` in scratch so the operator's `next dev` `.next` and the
tracked `next-env.d.ts` were never touched (`git status` confirms neither moved). **Copy
`node_modules` with `cp -Rc`, not a symlink** — Turbopack aborts with a panic on a `node_modules`
symlink that points outside the project root; that cost one failed build here.

Browser verification ran through a CDP harness (headless Chrome, fresh profile) in the operator's
runtime as `docs/current/operations.md` §Operator Runtime records it: `next dev` on
**`http://127.0.0.1:3000`** *and* **`http://100.77.164.42:3000`**, plus a **production build** served
with `next start` on `:3100`. Desktop (1440, plus 1512/1280/768/767/481 for the mono sweep) and 390.
Both scratch servers were stopped afterwards; the operator's dev server is untouched and still up.

## 3. build-prompt §10, box by box

Sample pages: ① 계양전기 `20260724000546` (열림) · 한화솔루션 `20260720000067` (닫힘) · 경남제약
`20260623000409` (추후결정) · 썸에이지 `20260805000454` (철회) · ② 대동기어 `20251016000315` · 풍전약품
`20250930000508` · ③ 세기상사 `20260713000345` · 아시아나항공 `20260713000482`.

0. **헤더 높이** — 닫힘 · 추후결정 · 부재 · 철회 all render exactly on the floor (**136.0** desktop /
   **248.0** at 390); 열림 is **156.6 / 308.5** because that state alone carries the 담기 line. The
   floor is what the record's CSS states; see reading 1 and phase Q20.
1. **고아 기호** — 0 elements whose whole text is `→`, `·` or `~` on any page at 390; 0 `→` inside
   `.chain`, `.movePair` or `.meta` at any width (the only `→` on the page is 「직접 질문 입력 →」 and
   the 환산/담기 labels, which are copy).
2. **44px at 390** — every `<a>`/`<button>` inside `main` measured on all eight pages: **0 below
   44px** after one fix (the ② fact strip's source link, reading 2). Citation chips 44 · crumb 44 ·
   `DART 원문` 44 · 담기 44 · 환산 44 · 질문 chips 44 · 정정 이력 44 · popover `×` 44 · popover DART
   row 44 (full width).
3. **인용 밀도 · `.secsrc`** — 계양전기 일정 6 rows/**1** chip, 발행 조건 9 rows/**2** chips; 세기상사
   발행 조건 9 rows/**1**; 아시아나 3 rows/**1**; every one of those sections closes with a single
   `DART 원문 {rcept} ↗` line. The five verbatim fields carry no chip (`fieldCites`).
4. **정정 이력 → 접기** — label flips to 「접기 ×」, `aria-expanded` `false → true`, surface changes
   (`rgba(0,0,0,0)` → `rgba(255,255,255,0.08)`, border → solid `--border-strong`), 36px desktop /
   44px at 390. The story renders the version rail (44px link rows, filled marker + 「현재 읽는 버전」)
   and the field move as **two tagged sides** (`515px 515px` desktop, one column at 390, **0** arrows).
5. **창 상태** — 한화솔루션 (① closed) wears 「기한 지남」; 세기상사 shows it three times (window + two
   step chips); **「종료」 count = 0 on every page, both modes**. ②'s past-open 「진행 중」 is
   unreachable in today's corpus (386/386 `upcoming`) and was verified against a scratch proxy that
   moved one window into the past: 「진행 중」 in `--live` (`rgb(95,208,165)`), dates kept, no chip, no
   담기 line, 「종료」 0. See reading 7.
6. **아시아나** — **two** dashed `.absent` chips (countdown slot + the `반대의사 통지 접수기간` field
   row), no placeholder for any other missing field, no reason anywhere. Reading 3 explains why the
   row exists.
7. **개요** — through the CDP accessibility tree: `h1 세기상사` · `h2 2단계 절차` · `h3 반대의사 통지` ·
   `h3 매수청구 행사` · `h2 발행 조건` · `h2 정정공시 반영 — …`; **no name contains `//`** (reading 6).
   Citation buttons name themselves 「{필드} [근거]」.
8. **404** — `/events/99999999999999`, the three non-exposable rcepts (`20260709000212` flagged,
   `20260722000285` incomplete, `20260306000600` 실적보고서) and an unmatched `/nope` all return
   **status 404** with the Korean surface, the requested path echoed in mono, a 44px (full-width at
   390) 관제 현황판 button, and **no reason**. Verified in dev on both origins and in the production
   build.
9. **mono 분절** — 0 mono runs occupying more than one line box, on all eight pages, at 1512 / 1440 /
   1280 / 768 / 767 / 481 / 390.

Also measured: **0** document horizontal overflow at every width on every page and in both modes; the
popover's three closes (× · outside click · Esc) with focus returned to the trigger on × and Esc, and
only ever one `[role=dialog]` open; the 질문 스트립 attached to the header's bottom edge (gap 0) with
36/44px chips and horizontal scroll at 390 (`scrollWidth 1009 > clientWidth 324`) and its surface-7
copy untouched. Console: 0 errors and 0 uncaught exceptions on all eight pages in both modes, except
the known favicon 404 (D5) on the first page loaded in a fresh profile.

**Regression on the other `Citation` users** — 조회 `/stocks/00162461` (한화솔루션, 환산 with a cited
factor): chip 32px desktop / 44px at 390, popover 380/340px fully in view, quote verbatim, DART row
32/44px, and **the rows behind it do not move** (`moved: false`), in dev and in the production build.
`/stocks/00102618` renders no citation chip at all (that stock's 진행 중 card is 발행가 확정 전 and its
놓친 돈 list is empty), so the surface was exercised on a stock that has one. The ask surface's
`InlineCitation` is R6-4's own component in `components/ask/` — **not one file under `components/ask/`
is in this slice's diff** — and `/ask` renders clean with 0 console errors; generating a live answer
needs the operator's model key, so it was not run.

## 4. Readings logged (where the record needed reading, or disagreed with itself)

1. **Header 「크기 통일」 is a floor, not a fixed height.** §1 says the four states occupy the same
   height and gives `min-height:136px` / `248px`; the round's own stylesheet has no fixed height. Built
   literally → three states sit on the floor and 열림 exceeds it by the 담기 line. Filed as Q20 rather
   than invented either way (clipping the 담기 line or padding the other three would both change the
   record).
2. **`.fsrc a` — prose beats the stylesheet.** §3 states the fact strip's source link as
   「32px / 모바일 44px」, and §10 box 2 measures every rcept link at 44px, but `r10-detail.css`'s
   ≤767 block has no `.fsrc a` rule (it stays at the desktop 32px). Added the mobile rule with a
   comment naming the conflict; the measurement decides.
3. **The absent field row on 아시아나 (③).** The payload has no `dissent_notice_procedure` — a
   정정 deleted it (`correction_interpretation.field_moves`: `old` present, `new: null`) — so nothing
   renders it, and box 6 nonetheless expects **two** dashed chips (카운트다운 · **필드 행**);
   `detail/Procedure.html` draws exactly that row (`<Row label="반대의사 통지 접수기간">` + the chip)
   and the walk note says the dashed frame must appear in both places so absence reads as a *state*.
   Implemented as: ③ + no procedure field → one row, labelled with the round's own string, valued
   with the locked 「현재 버전 공시에 없음」 chip. This is **not** the forbidden placeholder — no
   fabricated value, no reason, no row for any other missing field — and it states nothing the
   countdown slot on the same page does not already state.
4. **The card's 아시아나 panel shows only that one row; the product shows it *plus* 발행 조건.** The
   card is a sketch with its own sample data; the served payload really does carry 매수예정가격
   7,030원 with a quote. Never drop served data to match a card — the row was added, nothing removed.
5. **The popover's anchor needed a clamp the card could not reveal.** §6/`Citation.jsx` anchor the
   panel to the trigger (`left:0` desktop, `right:0` ≤767px, `.m390` frames repeat it). Inside a wide
   review canvas that is always visible; in a real 390 viewport a mid-row chip opened the 340px panel
   at **left −90px**, clipping the first characters of every line — i.e. the affordance's own content.
   The component now slides the panel back inside the viewport (ref callback on mount + a resize
   listener while open; ±8px gutter). No approved property changes — width, colour, border, padding,
   the 6px drop, the anchor — only the horizontal offset, and only when it would otherwise be cut.
   Desktop is untouched at 1440 (`transform: none`); the same clamp catches the mirrored overflow at
   768 (two panels pulled left by 78 / 53px).
6. **`::before` content reaches the accessible name.** §12 requires the eyebrow's `//` to be CSS-drawn
   「접근 가능한 이름은 「일정」이다」, and the port did draw it with `::before` — but Chrome puts
   generated content into the accessible name, measured as `2: "// 발행 조건"`. The eyebrows now carry
   an `aria-label` of their own words, which satisfies both halves of the record. The same leak exists
   on 조회/보유 종목, which print `// {title}` as literal text from earlier rounds → phase Q21 (not
   touched here: they belong to other signed rounds).
7. **Two branches are unreachable in the corpus.** ② past-open (**386/386** R2 events are
   `window_state: "upcoming"` on 2026-08-24) and multi-part citations (**0/386** figures carry
   `parts`). The first was verified in a real browser against a scratch read-only proxy that rewrote
   one event's countdown (nothing in the repo, the dev server or the database was touched, and the
   proxy is gone); the second by code — the popover renders each addend as its own passage with a
   dashed separator, unchanged from P5.S20's contract apart from its container. → phase Q22.
8. **`.optionKind`** (carried from earlier in the slice): the canon paints a 풋 in `--alert`; the port
   keeps R3's `--r2-tint`/`--r2`, because `--alert` means *expiring/lost* in this product and
   build-prompt §3 says 콜·풋 카드는 R3 그대로.
9. **The 환산 foot** — `.chainfoot` holds one child (the 환산 button), so `space-between` left it on the
   left edge; set to `flex-end`. The card's foot sentence beside it is card commentary, not product
   copy, and was not minted.

## 5. Deviations from `plan.md`

- **Three fixes the plan did not list**, each recorded above as a reading: the popover viewport clamp
  (5), `aria-label` on the eyebrows (6), and the ③ absent field row (3). All three exist to make a
  §10 box true in the running product; none changes an approved visual property.
- **`npm run build` was run on a scratch copy**, not in `frontend/` — the plan allows for the
  `next-env.d.ts` rewrite; building in place would also have clobbered the operator's running dev
  server's `.next`.
- **Box 5's ② half and the multi-part popover could not be exercised with served data** (reading 7).
  The plan's 「find one via the API」 for a `parts` figure has no answer in this corpus — all 386 events
  were scanned.
- **An ask answer with inline citations was not generated** — it needs the operator's model key, and
  the slice's brief forbids touching credentials. The ask surface is untouched by this diff and
  renders clean.
- Nothing else: no new data/fields/API, no change to QuestionStrip internals, lookup, ask, portfolio or
  the R8 chrome.

## 6. Doc impact recorded (in `phase.md`, for `P8.REVIEW` to consolidate)

**frontend** (R10 supersedes the detail surface + R5-2's 담기 label + the shared Citation re-cut + the
404 surface) · **product** (미주알 owns its 404; an absent governing field is *stated*) · **experience**
(one panel, evidence over the page, section source lines, 「기한 지남」, 44px targets) · **qa** (nine new
`## Regression Checklist` lines, one per §10 box) · **copy** (the hand-registered 「R10 additions」 tail
in `copy-inventory.md`, which is a grounding doc and not a versioned one).

Three operator questions were appended to `## Operator Questions`: **Q20** (header floor vs fixed
height), **Q21** (the `//` accessible-name leak on the other surfaces), **Q22** (states unreachable in
the corpus).
