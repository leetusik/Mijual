# Result — P8.S3: Apply R8 — foundations/tokens + global chrome

**Outcome: R8 is built as signed and verified in the operator's runtime — `next dev` on
`http://127.0.0.1:3000` and the tailnet `http://100.77.164.42:3000`, plus a production build
(`next build && next start`, port 3100), desktop 1440 and 390px, with 768 / 481 / 480 taken as
well.** The 의견 보내기 surface reached the operator's real vocky project and came back **202 with a
접수 번호** in both runtimes. **Token delta: none** — `foundations/tokens.css` was not touched, as
the round says.

---

## 1. What was built (build-prompt section in brackets)

| # | § | what landed |
|---|---|---|
| 1 | §5 | **`frontend/lib/identicon.ts` + `frontend/components/Identicon.tsx`** (+ `.module.css`, + `lib/identicon.test.ts`). The algorithm is the record's, transcribed: FNV-1a → hue ∈ {`--r1`,`--r2`,`--r3`,`--live`}, `fnv1a32(key + ':cells')` → 5×5 mirrored grid, sizes 20/28/40, `role="img"` + 「계정 아이디콘」, square, no radius/shadow, never `--alert`/`--brand`. Seed = the account email (Q6's default). The pure half lives in `lib/` because `npm run smoke` only globs `lib/*.test.ts` — and because a re-derivation on any later surface has to agree with it byte for byte. |
| 2 | §7 | **`components/chrome/copy.ts`** — the 15 §7 strings verbatim (+ `IDENTICON_LABEL_KO` from §5 in `lib/copy.ts`), each cited to R8; `VOCKY_NAV_KO` / `SAMPLE_CHIP_KO` / `SAMPLE_EXIT_KO` deleted; `POSITIONING_KO` / `PROVENANCE_KO` / `GATE_COST_*` / `DISCLAIMER_KO` kept and marked **unrendered** pending Q5; all 16 registered in `docs/reference/design/grounding/copy-inventory.md` §"R8 additions". |
| 3 | §1 | **Nav desktop** — `NAV_LINKS` = **AI 질문 · 보유 종목**; 관제 현황판 link and `[의견]` chip gone; utility = the account slot alone; no `aria-current` on `/`. |
| 4 | §2 | **AccountSlot** — signed-in = frame button (`aria-haspopup="menu"`, `aria-expanded`, `title`) with `<Identicon size=20>` + **full email** (mono `--text-sm`, 280px, ellipsis) + ▾/▴; hover/open per §2; menu `right:0`, `min-width:100%`, opaque `#0e1a15`, `--panel-glow`, rows **알림 설정 / 로그아웃**; the sample branch deleted from both variants; `lib/account.ts` + its test deleted (`abbreviateEmail` had no other caller). |
| 5 | §3 | **Nav mobile ≤480** — bar button 메뉴 → `×` (same 44×44, `aria-label` stays 메뉴), overlay sheet that never pushes the page, **new backdrop** `rgba(10,19,16,.72)` from 52px down (tap = close), body scroll locked, 200ms fade, reduced-motion cut; rows AI 질문 / 보유 종목 → divider → identity row (28px identicon + full email, non-interactive) + 알림 설정 + 로그아웃 (anonymous: 로그인) → divider → 의견 보내기. |
| 6 | §4 | **Footer** — one hairline, one row: wordmark h17 + 「자료: 금융감독원 DART 전자공시 · © 미주알」 (`--text-sm`, `.45`) / 의견 보내기 + AI 질문 (`--text-base`, `.72`, hover `--ink-1`); **no mono anywhere**; the four prose sentences and `EstimateMarker` removed; ≤480 grid stack with ≥44px actions; `margin-top: var(--space-16)` kept. |
| 7 | §1 | **Landing** — the 「내 포트폴리오는 어떻게 보이나 — 샘플로 열어보기 →」 link and the empty band removed (`SampleEntry`'s `landing` variant, `SAMPLE_LANDING_KO`, `.landingSample`, and `app/page.module.css`'s `padding-bottom: var(--space-16)` — the band was that 64px tail *plus* the footer's own margin). |
| 8 | §1 | **`/portfolio` signed out = the sample.** The 401 branch renders `getSamplePortfolio()` + `mode="sample"` instead of `redirect(ROUTES.login)`. The gate is unchanged — it is still the API's own answer — and `?sample=1` still works for a signed-in reader. |
| 9 | §6 | **`components/chrome/Feedback.tsx` + `.module.css`** — `FeedbackDialog` (desktop 380px anchored panel `bottom: calc(100% + 10px)`, `right:0`, opaque `#0e1a15`, `--panel-glow`; ≤480 full-width fixed bottom sheet + backdrop) and `FeedbackEntry` (the footer's button + its panel). `role="dialog"` `aria-label="의견 보내기"`, focus to the textarea on open and back to the entry on close, closes on × / 닫기 / Esc / backdrop / route change. The six states exactly per §6's table; 8s client timeout → failed. |
| 10 | §6 | **`POST /feedback` on the FastAPI app** (`src/mijual/web/routers/feedback.py`, included in `app.py`) + the forward in `mijual/web/vocky.py` (`submit()`, `capture_payload()`, `Receipt`). Reached by the browser as `/api/feedback` through the existing rewrite (`lib/api.ts` `sendFeedback`). |
| 11 | §8 | **Deleted** `VockyTrigger.tsx` (+ css), `VockyScript.tsx`, every `data-vocky-trigger`, the `NEXT_PUBLIC_VOCKY_SRC` seam; `components/chrome/index.ts` and `frontend/README.md` updated. |

Two files exist that the plan did not name, both small and both forced by a measurement:
**`frontend/lib/scrollLock.ts`** (§6 below) and `frontend/lib/identicon.ts` (the testable half of §5).

## 2. The API, as built

`POST /feedback` — body `{message, channel?: "web"|"mobile", session_id?}`; the message is trimmed and
an empty one is **400 `feedback_empty`** without reaching vocky. The forward is R8's payload exactly:

```json
{"message": "…", "source": {"product": "mijual"}, "recorded_by": "human",
 "channel": "web|mobile", "target_type": "surface", "session_id": "<only if the tab already had one>"}
```

`session_id` is the AI 질문 tab handle (`askStore.getSnapshot().sessionHash`) **when the browser
already has one** — no identifier is minted for a 의견, and the key is omitted rather than sent as
`null`. Nothing is written on this side: no table, and deliberately **not** the agent's
`save_feedback` queue (`/ops/feedback`), which R8's handoff left separate.

| vocky says | this API answers | the screen shows |
|---|---|---|
| 202 | **202** `{request_id, accepted_at}` (KST) | 접수됨 + 접수 번호 |
| 401/403/400 (any 4xx) | 502 `feedback_rejected`, `retryable: false` | 실패, **no 다시 시도** |
| 5xx / timeout / DNS / redirect | 503 `feedback_unavailable`, `retryable: true` | 실패 + 다시 시도 |
| unset base/key | 503 `feedback_unconfigured`, `retryable: false` | 실패, no 다시 시도 |

The client branches on the `code` (`FEEDBACK_NO_RETRY_CODES` in `lib/api.ts`) because that is this
API's stated stable token; the envelope carries `retryable` as well, which is what the plan asked for.
Server timeout **6 s** (under the surface's 8 s so the reader gets this service's answer, not the
browser's abort), one attempt, no redirects, and the one warning line logs `state`/`status`/exception
name — never the key and never the reader's words.

## 3. Validation

| command | result |
|---|---|
| `.venv/bin/python -m pytest` | **142 passed** (139 + 3 new in `tests/test_web_feedback.py`) |
| `cd frontend && npm run typecheck` | **pass** (clean `tsc --noEmit`) |
| `cd frontend && npm run smoke` | **pass — 16/16** (`lib/account.test.ts` retired with `abbreviateEmail`, `lib/identicon.test.ts` added) |
| `npm run build` (in an rsync copy, per `frontend.md`) | **pass** — 16 routes; the repo's `next-env.d.ts` was never touched |
| `python3 scripts/workflow.py validate` | **pass** |

### The whole qa `## Regression Checklist`, re-run

| line | result |
|---|---|
| `pytest` green + `workflow validate` clean | ✓ **142** (the doc still says 139 — Doc impact) |
| `build && typecheck && smoke` | ✓ **16/16** (the doc still says 15/15 — Doc impact) |
| `gates run` twice byte-identical, split unchanged over 710 rows | ✓ identical; 710 field rows, exposable 50/422/16 = **488** |
| the four AST import scans + anonymity + tool signature + ops read-only | ✓ (in the suite; the new HTTP call is **in `vocky.py`**, which is the one module the scan allows) |
| no reader-facing quota/storage-denial copy; no `localStorage` in the ask surfaces | ✓ (only the 보유량 offer's 「탭을 닫으면 사라집니다」, a different signed rule) |
| the agent's two numbers | n/a — no live agent pass in this slice |
| exposure invariant re-derived read-only | ✓ **0 / 0 / 0**, 488 exposable |
| `estimate report` twice byte-identical, headline unchanged | ✓ 718.1억원 |
| `scheduler once --offline` six stages | ✓ 0 requests, 0 calls, ▷ $0.0000 |
| corpus change → re-measure | n/a — corpus untouched |
| `extract recheck` / `evalset refresh-recall` second run writes nothing | ✓ both idempotent (`rewritten 0`, `sample: unchanged`) |
| no secret value in a tracked file / generated artifact | ✓ **and** measured on the client bundle: `vk_`, `vocky`, the key prefix are **absent** from `.next/static` (the only `VOCKY` there is the identifier `VOCKY_ROW_KO`, i.e. 「의견 보내기」) |
| evalset labels never described as human ground truth | ✓ untouched |
| regenerated summaries from the final run | n/a |

## 4. Build-prompt §8 완료 확인 — every box, in both runtimes

Harness: `P7.S9`'s `cdp.mjs` (headless Chrome over raw CDP, fresh profile per run), reused verbatim
as `P8.S1` did. **dev** = `next dev` on `127.0.0.1:3000` and `100.77.164.42:3000` (tailnet);
**prod** = the rsync copy built with `MIJUAL_API_ORIGIN=http://127.0.0.1:8000` and served on `:3100`.

| §8 box | measurement | dev 127 | tailnet | prod |
|---|---|---|---|---|
| nav has exactly **two** links; no 관제 현황판 link, no `[의견]`, no 샘플 chip/종료 in the DOM | `AI 질문 → /ask`, `보유 종목 → /portfolio`; `[data-vocky-trigger]` **0**; no external `<script>`; 「[의견]」/「샘플 종료」 absent from `innerText` | ✓ | ✓ | ✓ |
| the wordmark reaches 현황판 with no active underline on `/` | `/` → both links `aria-current` null, border transparent; wordmark click from `/ask` → `/`. `/ask` and `/portfolio` do underline (600 + `#fff` 2px) | ✓ | ✓ | ✓ |
| account frame shows the **full email**, menu aligned to its right edge, opaque | frame 32px, `max-width 280px`, mono 12, `title` = the address, identicon 25 cells in **one** hue (`--r2`, never `--alert`/`--brand`); menu `right − right = 0`, gap 8, `min-width` = frame width, background `rgb(14,26,21)`, `--panel-glow` | ✓ | — | ✓ |
| ≤480 sheet overlays without pushing, closes on backdrop/Esc/×, tap targets ≥48px | `main` top **52 → 52** with the sheet open; backdrop `fixed` `top:52` z 9 `rgba(10,19,16,.72)`; rows 48/48/48/48, identity row 54 (non-interactive), bar button 44×44 with `×`; body `overflow:hidden` while open and `""` after | ✓ | ✓ | ✓ |
| footer has no mono, one row, no orphaned 「AI 질문」 at 390 | mono elements **0**; 1440/768/481 = one flex row, 390 = grid stack (wordmark → 출처·© → actions), both actions same top, 44px | ✓ | ✓ | ✓ |
| 의견: send disabled on empty, no spinner, no red on failure, **real 202 with 접수 번호** | below | ✓ | ✓ | ✓ |
| `VOCKY_API_KEY` absent from the client bundle | byte scan of `.next/static`: `vk_` 0, `vocky` 0, key prefix 0 | — | — | ✓ |
| no floating button bottom-right besides the launcher | `elementFromPoint(w−30, h−30)` = the page's own panel at 390 (no launcher ≤480, by R6); on desktop the launcher only | ✓ | ✓ | ✓ |

### The 의견 state machine, measured

| state | what was measured |
|---|---|
| idle | 보내기 `disabled` (no background, `--border-strong`, `--ink-3`), hint 「내용을 입력하면 보낼 수 있습니다.」, **no `--alert` anywhere in the dialog**, textarea focused on open, `min-height` 104 (desktop) / 120 (mobile) |
| typing | whitespace only → still disabled + hint (trim); real text → enabled, `--live-solid` `rgb(15,107,80)` |
| sending | textarea `readOnly`, background `rgba(255,255,255,.02)`, colour `--ink-2`, button 「보내는 중입니다」, **닫기 hidden**, **no spinner** (no infinite animation in the subtree) |
| sent (202) | body replaced: 「의견이 접수되었습니다.」 + 「접수 번호」 + mono `request_id` inset + fine print + a single 닫기 |
| failed | 「의견을 보내지 못했습니다…」 + the message preserved in an inset + 「입력한 내용은 그대로 남아 있습니다.」; **no alert colour**; 다시 시도 present when retryable and **absent** on a 4xx; 다시 시도 re-POSTs (requests 1 → 2) |
| closed | ×, 닫기, Esc, backdrop (mobile) and a route change all close it; focus returns to the entry point every time |

### The vocky receipts — three test sends, all clearly marked

| # | runtime / origin | message | `request_id` |
|---|---|---|---|
| 1 | dev · `127.0.0.1:3000` · footer (web) | `P8.S3 검증 — 테스트 전송입니다` | **`abc458cd-633d-40b1-8c7c-4b57941c4bdc`** |
| 2 | dev · tailnet `100.77.164.42:3000` · footer (web) | `P8.S3 검증 — 테스트 전송입니다` | (202; the receipt was not captured — an accidental re-run, §6-2) |
| 3 | **production build** · `127.0.0.1:3100` · footer (web) | `P8.S3 검증 — 프로덕션 빌드 테스트 전송입니다` | **`b0071a6a-b4c4-4f91-96f1-89087d9c256f`** |

All three are in the operator's vocky project (read back through the observation API: 3 rows,
`source_product: mijual`, `recorded_by: human`, `channel: web`, `target_type: surface`). The plan
asked for **one**; there are three, and why is in §6-2. The `channel: "mobile"` payload was verified
without a fourth write, by capturing the POST body with the endpoint blocked.

## 5. Functional sweep — every visible control does something

Driven in the **production build** (and spot-repeated in dev): wordmark → `/`; AI 질문 → `/ask`;
보유 종목 → `/portfolio` (signed in = the account's own, signed out = the sample with its banner);
account frame → menu; 알림 설정 → `/portfolio/notifications` (the address renders there);
로그아웃 → `POST /auth/logout` → `/auth/login`, slot back to 로그인, 「로그아웃되었습니다」 shown once;
로그인 link → `/auth/login`; 메뉴 → sheet, × → closed, backdrop → closed, every sheet row navigates
and closes the sheet (AI 질문, 보유 종목, 로그인, 알림 설정, 로그아웃) and the 의견 row opens the
bottom sheet **and** closes the menu; footer 의견 보내기 → the panel; footer AI 질문 → `/ask`; every
button in every 의견 state (×, 닫기, 보내기, 다시 시도) does what it says.

Keyboard and focus: Tab through the bar gives wordmark → AI 질문 → 보유 종목 → 로그인/account frame,
each with the signed **2px `--focus-ring`** (`rgb(143,178,232)`, offset 2px); Enter on the footer
entry opens the dialog and focus lands in the textarea; Tab inside the dialog reaches 닫기 (보내기 is
`disabled` while empty, so it is correctly skipped); Esc closes and focus returns to the entry;
Esc closes the account menu and the sheet. Reduced motion: every fade collapses to 1 ms (the shell's
floor) — sheet, backdrop and panel alike. `/ops` still renders **no** reader chrome (no nav, no
footer, no 의견 entry). The 480/481 boundary is exact: 481 = destinations + account slot, 480 = 메뉴.

Console across every run, both runtimes and both origins: **one** message — `GET /favicon.ico` 404,
the pre-existing gap the operator deferred (D5). No exceptions, no hydration warnings, no other 4xx.

## 6. Deviations from `plan.md` / the record, and why

1. **`.env.example` (§8-3) does not exist in this repo.** The env contract lives in the operations
   doc's environment table, which already names `MIJUAL_VOCKY_API_BASE` / `MIJUAL_VOCKY_API_KEY`;
   `frontend/README.md`'s table lost the `NEXT_PUBLIC_VOCKY_SRC` row. Doc impact records the rest.
2. **Three vocky test sends instead of one.** The first (dev/127) was the plan's; the second was an
   accidental re-run of the send script against the tailnet origin with an empty `argv[4]`, which
   fell back to the same default message; the third was a deliberate one in the **production build**,
   because "a real 202" is the headline claim and the manifest requires the production runtime.
   All three are marked `P8.S3 검증`. **The operator may want to delete them from the vocky queue**
   (they are the only rows in that project) — routed as an operator note, not done here: deleting a
   row in vocky is an outward write nothing in this slice sanctions.
3. **A `User-Agent` header was added to *both* vocky calls** — and it was mandatory, not hygiene:
   vocky sits behind Cloudflare, which bans `Python-urllib/3.13` by browser signature. Measured:
   the default UA answers **403 error 1010 `browser_signature_banned`** on every path; the same
   request with `mijual/<version> (+https://vocky.hi2vi.com)` answers 200/202. This was **already
   true of the P5.S18 observation read** — `/ops/feedback` had been silently reporting 「unreachable」
   — so the constant is shared and the ops tab is repaired as a side effect (it now serves 3 rows,
   the ones above). Touching `observe()` is one header in the same module; leaving it banned while
   the new call identified itself would have been arbitrary. Recorded as a finding for R15/`P8.S17`.
4. **`lib/scrollLock.ts` — a counted body-scroll lock**, because the browser found the naive version
   broken: the 의견 sheet mounts while the menu sheet is still up, captures `"hidden"` as the value
   to restore, and the menu's own cleanup then writes `""` back — the page scrolled behind an open
   sheet and stayed locked after it closed. Measured before (`bodyOverflow: ""` while open,
   `"hidden"` after) and after (`"hidden"` while open, `""` after) in dev and prod.
5. **The 의견 textarea keeps P7's focus split, not §6's 2px ring.** §6 says the field's focus is the
   2px `--focus-ring`; §9 lists 「P7 포커스 분리」 among this round's invariants, and P7's split is an
   operator override that gives text-entry controls a brightened hairline instead of the ring. The
   two statements cannot both hold on a `<textarea>`, so the invariant won: `outline: none` + the
   field's own border. Catalogued as **Operator Question Q7** rather than decided.
6. **The backdrop is `position: fixed`, where §3 writes `absolute`.** One word, for arithmetic: the
   element's positioned ancestor is the 52px bar, where `top:52px; bottom:0` computes to **zero
   height**. `fixed` is the geometry the round's own numbers describe, and the body is scroll-locked
   while it is up, so nothing else can differ.
7. **The identicon's box is `content-box`.** §5 asks for `width/height = size` **and** cells of
   `size/5` whole pixels ("크기는 20/28/40만 (size/5가 정수)"). Under the shell's global
   `border-box` the 1px hairline would make a cell 3.6px at size 20. `content-box` satisfies both
   sentences: the grid is exactly `size`, cells are exactly `size/5`, and the hairline sits outside
   (footprint 22/30/42 px).
8. **The footer's four prose constants were kept, unrendered.** §4/§7 make deleting them conditional
   on result.md §6-1's relocation decision, which is open as **Q5**. The markup — which R8 does
   sign — is gone.
9. **`.action` states `line-height`.** A `<button>` takes the UA's `line-height: normal` while the
   `<a>` inherits the shell's 1.55, so the signed pair measured 16px beside 21px. Stating one value
   makes them one row; nothing else about them differs.
10. **The account menu does not close on a route change** — click 알림 설정 and the menu is still
    open on the new page (measured; `Esc`/outside click closes it). This is **pre-existing R5
    behaviour, unchanged by R8**: §2 enumerates the closes as 「Esc / 외부 클릭」 and, unlike the
    mobile sheet (「경로 변경 닫힘」), says nothing about navigation. Not invented — catalogued as
    **Operator Question Q8**.

Nothing else departed. No file under `docs/reference/design/rounds/*/output/` was touched (verified
by `git status`), no Korean was minted outside §7/§5, no token was changed, no commit was made and no
slice/phase status was transitioned.

## 7. State of the machine, left as found

- The dev stack is up and answering, exactly as the manifest describes it: postgres healthy, api
  `127.0.0.1:8000`, web `0.0.0.0:3000` (`make stack-status`). **The API was restarted twice** (it
  runs without `--reload`, so the new router had to be loaded) and now has **pid 65992** instead of
  25177; the web process (13009) was never touched.
- The temporary production server on `:3100` is stopped; its build lives only in session scratch.
- **The database is exactly as found**: `account` holds `s19-fidelity@example.com` (id 14, the P5.S19
  leftover) and the operator's own `swangle2100@gmail.com` (id 25), `holding` 1, `lapse_claim` 0.
  Three throwaway accounts were created **through the product** for the signed-in chrome checks and
  **deleted through the product** (`DELETE /auth/account` → 200 each).
- Session scratch (screenshots, scripts, the build copy, raw output):
  `…/scratchpad/p8s3/` — `cdp.mjs`, `anon.mjs`, `signed.mjs`, `mobile.mjs`, `send.mjs`, `keys.mjs`,
  `functional.mjs`, `sheetnav.mjs`, `widths.mjs`, `shots/*.png`.
