# Result — P7.S8: 포트폴리오 layout fidelity + the 챙겼습니다 flip

**One file changed** (`frontend/components/portfolio/Portfolio.module.css`), **five measured layout
deviations closed**, **five record-silent items left for the operator**, and the 챙겼습니다 flip
verified end to end — sample/anonymous *and* account — on `127.0.0.1`, on the tailnet, and in an
isolated production build. No component markup, no copy, no `Deadlines.tsx`/`Holdings.tsx`/
`Portfolio.tsx` change. The 챙겼습니다 row was **not** removed (Q4 is the operator's).

## What the operator's "not organized" resolved to

Five things, all of them implementation slips against the record rather than design decisions —
none of them visible in the source, all of them measurable in a browser:

1. **The holdings table's column headers did not sit over their columns.** 보유량 was **18.7px**
   and 진행 중인 권리 **32.1px** to the right of the cells they name, at both 1440 and 768.
2. **The D-day list's hairline separator belonged to neither row** — 28px below the previous row's
   ink, 16px above its own — while the holdings sheet immediately above it on the same page was
   symmetric (12/12).
3. **The 지나간 ① row's three parts started at three different heights** — the money statement, the
   「놓친 돈 상세 →」 link and the 챙겼습니다 check spread over **21.7px** of vertical origin, so
   nothing on the row shared a line.
4. **The `// ` section eyebrow was a different size here than on every other surface** — 12px with
   no tracking, against 11px + 0.08em in `lookup`, `event` and `landing/Anchor`, and against R2's
   own literal "mono 11 `--ink-3` eyebrow".
5. (Introduced and closed inside this slice) the fixed action track needed the 수정·삭제 pair pinned
   to its end to keep the flush right edge the `auto` track used to give it.

The **sixth** candidate — the wide, ragged gulf between the 종목 name and the D-day block at desktop
widths — is real and measured, but fixing it requires geometry the record does not state. It is
**Q-A** below, not a fix.

## (a) Layout — the deviation table

Measured with headless Chrome over CDP, fresh profile per run, `next dev` on
`http://127.0.0.1:3000`, at **1440×900 / 768×1024 / 390×844**, sample loaded through the product
(the 로그인 page's 샘플 entry and the landing 샘플 line, both exercised). "before" was captured
against the untouched tree before any edit.

| # | element | what was off (measured) | record reference | fix | after (measured) |
|---|---|---|---|---|---|
| **D1** | `.holdingHead` vs `.holdingRow` — the 보유 종목 table | Head and rows are two separate grids sharing one track list `1.4fr 1fr 1.6fr auto`. The head's 4th cell is an empty `<span/>`, so its `auto` track resolved to **0px** while the rows' resolved to **53.5px** — the three `fr` tracks then split a different leftover in each grid. **1440:** head cells at x = 184 / **558.4** / **830.4**, rows at 184 / **539.7** / **798.3** → labels **18.7px** and **32.1px** off their columns. **768:** identical 18.7 / 32.1 offsets. | R5 §Portfolio 행: 종목 / 보유량 / 진행 중인 권리 요약 / 수정·삭제 — a table, and a header that does not stand over its column is not one | fourth track becomes a **fixed** `var(--holding-actions)` (= `--space-16`, 64px > the 53.5px pair), declared on `.holdings` | head **and** rows at x = 184 / 536 / 792 / 1192 (1440) and 24 / 252.8 / 420.8 / 680 (768) — **0.0px** offset on every column, at both widths, in dev **and** in the production build |
| **D1b** | `.holdingRow .actions` | Side-effect of D1: with a 64px track the 53.5px 수정·삭제 pair sat flush **left**, 10.5px short of the content edge it previously touched | R5 개정 ④ "우측 액션 열" | `justify-self: end` inside the ≥480 grid rule only | pair ends at x = **1256** (1440) / **744** (768) = the content column's right edge, exactly as before D1 |
| **D2** | `.rows` (the D-day row list) | `gap: var(--space-3)` **on top of** each row's own `padding: var(--space-4) 0` + `border-top`. The rule therefore sat **28px** below the previous row's last ink and **16px** above its own first ink (**24 / 12** at 390) — a separator belonging to neither row, on a page whose other list is symmetric (`.holdings`: 12/12, `gap: normal`) | R2 §Board row: "9px v-pad, **dashed `--border-soft` separators**" — padding + separator, no extra gap; `.holdings` on this very page already does it that way | drop the `gap` — the hairline **is** the separator | **16 / 16** at 1440 and 768, **12 / 12** at 390. Document height 1572→**1533** (1440), 1613→**1574** (768), 2407→**2367** (390) |
| **D3** | `.lapsed` + `.lapsedLine` — the 지나간 ① 소멸 row | `align-items: center` over children **23.3 / 44 / 66.6px** tall: the money line started at y=961.6, the 상세 link at 951.2, the 챙겼습니다 block at 939.9 — a **21.7px** spread, three origins, no shared line (768: same, 21.7px). The tallest child (the check + its caption) dragged the whole group off-centre | R5 §D-day 목록 "① 소멸 행은 500주 기준 「추정」 금액 + 놓친 돈 상세 → 링크" + R5-8's checkbox on the same row; R5 §Mobile's 44px target floor is what makes the two affordances 44px tall | `align-items: flex-start` on `.lapsed`; `min-height: 44px` + `align-content: center` on `.lapsedLine` so the money statement occupies the same 44px band the two affordances already do | all three children at y = **924.8** (1440) / **947.2** (768) — one origin, three texts centred on one 44px band. At 390 the money line and the link share y=1461.9 and the check wraps to its own line (1517.9), which is §Mobile's single column |
| **D4** | `.eyebrow` — `// 다가오는 마감` · `// 지나간 마감` | `--text-sm` (**12px**), `letter-spacing: normal` — while `lookup`, `event` and `landing/Anchor` all render the same `// ` eyebrow at `--text-xs` (**11px**) + `0.08em`. The two section headers read one step heavier than the identical device everywhere else | R2 §Retrospective anchor literal: "mono **11** `--ink-3` eyebrow"; R3's own comment "eyebrow mono, **tracked**"; R4 §4–5 name `// ` as the section eyebrow | `--text-xs` + `letter-spacing: 0.08em` | **11px / 0.88px** (= 0.08 × 11) on both headers, at all three widths, dev and prod |

Nothing else moved: no colour, token, radius, border width, height, padding scale, font family,
component markup or Korean string. Radius audit across the whole surface: **0 non-zero radii** at
all three widths. Non-token spacing audit inside `Portfolio-module` elements: only `pastChip`'s
2px chip padding (the R2/R5 chip idiom, shared with `plannedChip`) and the checkbox's UA
`margin: 3px 3px 3px 4px` — neither is a fidelity item. Overflow / clipped-text audit over every
element under `<main>`: **0** at 1440, 768 and 390, before and after.

### Anatomy walk against the record (everything the plan listed, checked)

| R5 says | rendered | verdict |
|---|---|---|
| 페이지 본문에 「내 포트폴리오」 대제목 없음 (개정 ③) | `main h1` count = **0**; the surface opens on the banner | ✓ |
| 샘플 inset 배너, "구성 예시" 문구, at the top of the 2층 surface | first child of `.surface`, `--surface-inset` + `--border-soft` hairline, 「샘플 포트폴리오 — 구성 예시입니다…」 | ✓ |
| 샘플에서 알림 설정 숨김 | no 알림 link anywhere on the page (`notifyLinkPresent: false` at all three widths) | ✓ |
| nav 「샘플」 칩 + 샘플 종료 (로그인 슬롯 대체) | both present in the chrome; nav is 관제 현황판 · AI 질문 (P7.S6's two slots) | ✓ |
| 섹션 2개, 다가오는 (D 오름차순) · 지나간 (최근순) | D-2, D-62 / D+44, D+46, D+48 — server-ordered | ✓ |
| 앵커 날짜 「기준 YYYY-MM-DD (KST)」 | stated **once**, on 다가오는 (`기준 2026-08-23 (KST)`) | see **Q-B** |
| 행 = 종목 / governing label + `D-n · date` / RightsChip / ① 금액「추정」 or 발행가 확정 전 칩 + 확정 예정일 / ②·③ no money | 계양전기 ① → `발행가 확정 전` + 확정 예정 2026-09-01 + 배정 115주 +23주, **no won**; 대동기어 ② → 오버행 6.68% / 643,004주 / 15,552원, **no per-holding won**; 세기상사 ③ → the 2단계 dependency line, **no won** | ✓ |
| 지나간 행 = inset 칩 `기간 지남 · D+n` / `통지 마감 지남 · D+n`, **alert 색 금지** | `.pastChip` on `--surface-inset` + `--border-soft`, text `--urgency-far` — not `--alert` | ✓ |
| ① 소멸 행 = 500주 기준 「추정」 금액 + 놓친 돈 상세 → | 한화솔루션 `500주 기준` `679,575원`「추정」; 대동기어 `300주 기준` `446,720원`「추정」 | ✓ (link text: **Q-D**) |
| 보유 4행: 계양전기 500 · 대동기어 300 · 한화솔루션 500 · 세기상사 100 | exactly those four, those counts, those 종목코드 | ✓ |
| 행 = 종목 / 보유량(인라인 편집) / 진행 중인 권리 요약 / 수정·삭제 | as drawn; 수정 → `SharesInput` + 저장·취소 in the same horizontal action column | ✓ (empty cells: **Q-C**) |
| 종목 추가 = 하단 패널 (mobile) | account mode only — 샘플 offers no 종목 추가 by `P5.S8`'s recorded decision | ✓, unchanged |
| ≤480: 단일 컬럼, 타깃 ≥44px, 아코디언 없음, 지나간 = 요약 행 | single column at 390; every `a`/`button`/`label` ≥44px (the 16px `claimBox` is inside a 44px `<label>` that is the actual target); `.pastSection .pastDate` hidden | ✓ |
| primitives: hairlines, radius 0, mono numerals, tokens for spacing, `.mono` size rule | radius audit 0/0/0; `.mono` numerals render at their surface's own size where one is set (12px on `.reference`/`.pastDate`/`.holdingMeta`) and at 0.95em where none is (14.25px on the 소멸 amounts) — `shell.css`'s `:where(.mono)` rule intact | ✓ |

**P5.S19 catalogue #6 — confirmed, not fixed.** The 샘플 entry subline says 「실제 공시 **4건**으로
구성된 예시 포트폴리오」 and the page renders **five** D-day rows from four holdings:
`GET /portfolio/sample` serves `holdings 4 · upcoming 2 · past 3`, because **대동기어 carries two
events** — an upcoming ② 전환청구 개시 (D-62) *and* a past ① 소멸 (D+46, 446,720원) — while R5's own
composition table pins one filing per holding. No row was hidden. It stays a data-vs-sentence item
for the operator, exactly as `docs/current/frontend.md:359-360` already records it.

## (b) 챙겼습니다 — measured, in both modes, on both origins, and in the build

R5-8 signs exactly four consequences of the check. All four fire, and the row and its figure stay:

| R5-8 | before check | after check | measured where |
|---|---|---|---|
| 라벨 놓친 돈 → **챙긴 돈** | `놓친 돈` | **`챙긴 돈`** | sample + account, dev 127.0.0.1 + tailnet + prod build |
| 금액 동일 | `679,575원` | `679,575원` — identical string | same |
| 「추정」 유지 | `추정` tag present | `추정` tag present | same |
| alert → live | label `rgb(224,87,63)` · value `rgb(224,87,63)` (`--alert`) | label **`rgb(95,208,165)`** · value **`rgb(95,208,165)`** (`--live`) — **both**, not just the label | same |
| 캡션 본인 표시 | 샘플/익명 `본인 표시` · 계정 `본인 표시 · 계정에 저장` | unchanged (see **Q-E**) | same |
| the row and its figure stay | — | row still in 지나간 마감, chip `기간 지남 · D+44`, 상세 link, 500주 기준 — nothing removed | same |

**No layout shift on the flip.** `.lapsed` box y=**427.8** h=**66.6** and document height **1533**
before *and* after the click, at 1440; account mode: row y=**371.9** h=**132.2**, doc **900** before
and after. Nothing under the reader's cursor moves.

**Persistence — 샘플/익명 (localStorage, R5-8).** After the click,
`mijual.portfolio.sample` = `{"v":1,"holdings":[…4…],"claims":["20260730000366"]}`; a full reload
re-renders `챙긴 돈` + live hue with the box checked. Verified on `127.0.0.1`, on
`100.77.164.42` (tailnet) and against the production build on `:3100`.

**Persistence — 계정 (the API path).** Exercised end to end with a throwaway account created and
deleted **through the product**:

| step | observed |
|---|---|
| 계정 만들기 `p7s8-probe@example.com` | signup → `/portfolio`, chrome slot switches to the 축약 이메일 menu |
| 종목 추가 → 한화솔루션 → 500주 → 담기 | holding added; the past ① 소멸 row appears with the 챙겼습니다 check |
| click the check | **`PUT /api/portfolio/claims/20260730000366` → 200**, then `GET /api/portfolio` → 200 (the write-then-re-read `Portfolio.tsx` documents); row flips to 챙긴 돈 + `rgb(95,208,165)`, `679,575원`「추정」 unchanged, caption **`본인 표시 · 계정에 저장`** |
| full reload of `/portfolio` | still `챙긴 돈` — server-side, in the server-rendered HTML |
| holdings column alignment in **account** mode (D1 applies here too) | head x = 184 / 536 / 792 / 1192, row x = 184 / 536 / 792 / 1202.5 (the 4th differs only because `justify-self: end` shrinks the action pair inside the 1192–1256 track; the head's 4th cell is empty) |
| 계정 삭제 | account gone → `/` |

**Test data removed.** `select id,email from account` → one row, `14 | s19-fidelity@example.com`
(P5.S19's leftover, deliberately untouched); `lapse_claim` **0**, `holding` **0**, `auth_session`
one row belonging to account 14 and dated 2026-08-22 — all pre-existing. Nothing of mine remains.

**Keyboard.** Tab reaches the checkbox as the **16th** stop (nav → 샘플 종료 → [의견] → the four
rows' 수정·삭제 → 놓친 돈 상세 →). Focused, it carries `outline: 2px solid rgb(143,178,232)` at
`outline-offset: 2px` with `:focus-visible` **true** — S5's preserved ring on a non-text control,
exactly as `app/shell.css` intends. **Space toggles it** → `챙긴 돈` + `rgb(95,208,165)`. (A
programmatic `.focus()` does **not** match `:focus-visible`; only a real Tab does. Worth knowing
before believing a focus probe.)

## Left for the operator — record-silent, so not invented

- **Q-A · the D-day rows' right-hand block has a ragged left edge, and a wide empty middle.** With
  `.rowHead { justify-content: space-between }` each row's governing label + D-day is right-aligned
  and therefore starts wherever its own content width puts it: at 1440 the five rows begin at x =
  **1035.5 / 1090.3 / 945.6 / 945.7 / 953.2** — a **144.7px** ragged edge — leaving **584.6–761.3px**
  of empty middle (768: the same 144.7px spread, 232.6–409.3px of middle). R5 §D-day 목록 names the
  row's *parts* and no geometry; **R2's board — this product's other deadline list — pins a fixed
  grid (`86px 1fr 300px 230px 96px`) precisely so those columns line up.** Adopting a board-style
  column grid here would very likely be what "organized" means at desktop width, but it is a
  geometry decision no round made for this surface. **Operator call.**
- **Q-B · 지나간 마감 states no 기준 anchor line.** R5: 「섹션 2개: 다가오는 마감 · 지나간 마감.
  앵커 날짜 명기 ("기준 YYYY-MM-DD (KST)")」. `P5.S8` read it as page-level and states it **once**,
  on the section that counts down (there is an explicit comment saying so); this slice's plan read
  it as per-section. Consequence today: the past chips `D+44 / D+46 / D+48` carry no visible basis
  of their own. Either way it is the existing `referenceKo()` string — **no new Korean**. Not
  changed here, because the record's sentence genuinely reads both ways and duplicating a line
  380px below itself may be the *opposite* of tidy.
- **Q-C · two holdings rows render an empty 진행 중인 권리 cell.** 한화솔루션 and 세기상사 hold only
  **past** rights, so `rights.next` is null and `P5.S8` renders nothing — R5 signs no empty-cell
  sentence and inventing one is copy. At ≥480 that is a visible hole in the middle column of two of
  the four rows (at 390 the cell collapses to 0px and nothing shows). Leave, or say something?
- **Q-D · a 챙긴 돈 row still links 「놓친 돈 상세 →」.** R5-8's checked-state delta is exactly four
  items and the link is not one of them; the link also points at R4's section whose signed name
  *is* 「2026년 놓친 돈」, so keeping it is defensible — but on a green 챙긴 돈 row it reads as a
  contradiction. Changing it mints Korean.
- **Q-E · the 본인 표시 caption renders whether or not the box is checked.** R5-8 phrases all four
  consequences as following 체크 (「체크 → … 캡션 "본인 표시 · 계정에 저장"」), which can be read as
  *the caption appears on check*. The build renders it always — arguably closer to the rule's own
  rationale (「사용자 주장 표시 — 공시 데이터와 혼동 금지」 is worth saying **before** the mark).
  **Deliberately not changed:** making it conditional adds a 22.6px layout shift on click, which
  this slice's plan forbids. If the operator wants the caption to appear on check, the shift needs
  a decision too (reserve the line, or accept the jump).

Plus the standing **Q4** (should a 챙겼습니다 row disappear altogether?) — untouched by this slice
by instruction; reading #5 stands and the row stays.

## Validation

| command / probe | outcome |
|---|---|
| CDP layout probe, `next dev` `127.0.0.1:3000`, 1440 / 768 / 390, before + after | **pass** — every number in the deviation table above |
| CDP flip probe (sample), `127.0.0.1:3000` @1440 — entry via `/auth/login` 샘플, click, reload | **pass** — flip, no shift, localStorage persistence |
| CDP entry probe — landing 샘플 line (`내 포트폴리오는 어떻게 보이나 — 샘플로 열어보기 →` → `/portfolio?sample=1`) | **pass** — both signed R5-4 entries reach the loaded state |
| CDP probe, **tailnet** `100.77.164.42:3000` @1440 + @390 | **pass** — hydrated, and identical on every measured number to `127.0.0.1` |
| CDP account probe — 계정 만들기 → 담기 → check (`PUT` 200 + re-read) → reload → 계정 삭제 | **pass** — table above; DB clean afterwards |
| CDP keyboard probe — Tab to the checkbox, ring, Space | **pass** — `2px solid rgb(143,178,232)` @2px, `:focus-visible` true, Space flips |
| overflow / clipped-text / radius / non-token-spacing audits @1440, 768, 390 | **pass** — 0 overflow, 0 clipped, 0 non-zero radii, no non-token spacing beyond the chip's signed 2px and the UA checkbox margin |
| `npx next build` in an **isolated copy** (`P7.S2` method) | **pass** — compiled 1.37s, TS 1.68s, 16 routes, identical route table |
| `next start -H 127.0.0.1 -p 3100` + the same CDP probes | **pass** — every measured number identical to `next dev` at all three widths; flip + persistence identical. Server stopped, `:3100` free |
| `cd frontend && npm run typecheck` | **pass** (no output) |
| `cd frontend && npm run smoke` | **pass** — 15/15, 169 ms |
| `python3 scripts/workflow.py validate` | **pass** — see below |
| `make stack-status` | dev stack left **running** (postgres healthy, api pid 25177, web pid 13009) as required |

## Files changed

- `frontend/components/portfolio/Portfolio.module.css` — the five rules above, each with the
  measurement that justifies it in a comment.

## Deviations from `plan.md`

1. **Q-A was not fixed, it was reported.** The plan lists "misaligned columns" among the things to
   fix, and the D-day rows' ragged right block is the largest single "not organized" symptom left.
   Closing it needs a column geometry R5 does not state, so it went to the operator under the
   plan's own "where the record is silent, do not invent" clause — with R2's board grid named as
   the precedent, so the decision is cheap to make.
2. **Q-B (the 지나간 anchor line) was not added**, though the plan's anatomy walk lists the anchor
   line on *each* section. `P5.S8` states it once by an explicit, recorded reading of the same
   sentence; the record supports both. Reported rather than flipped.
3. **One fix (D1b) exists only to absorb another fix's side effect** — `justify-self: end` on the
   action cell. It is listed as its own row so the diff is not mistaken for a restyle.
4. **The production build ran in an isolated copy** of `frontend/` in session scratch, as
   `P7.S2`/`P7.S5` did — the running dev server and its `.next` were never touched and the stack
   needed no restart.

## Scope kept

No copy (S7's), no focus rules (S5's), no nav (S6's), nothing outside
`components/portfolio/Portfolio.module.css`. No shared primitive was edited. No commit, no slice or
phase state transition, no `doc-new-version`. `docs/reference/design/` untouched. The 챙겼습니다 row
still renders with its figure — Q4 remains the operator's.
