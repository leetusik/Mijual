# Result — P11.F2 (Publish the operator contact in the agent answer and the footer)

- **status:** `done`
- **summary:** The operator's own email and phone are now published in both places they asked for:
  the AI 질문 agent answers 「운영자 연락처 → 이메일 leetusik@gmail.com · 전화 010-3772-9916」 instead
  of the honest-unset line, and the global footer carries both values on every reader page — email in
  Pretendard, phone in mono, joined to the existing 자료/© row rather than re-adding the second row R8
  deleted. One setting (`MIJUAL_OPERATOR_CONTACT`) feeds both, served to the frontend by a new
  `GET /site/contact`. Verified live in dev and in the production build, at 1280 · 1120 · 1024 · 820 ·
  767 · 481 · 390, and with the API stopped on a cold cache.
- **files_changed:**
  - `.env` — `MIJUAL_OPERATOR_CONTACT` set (gitignored; **not** part of any commit)
  - `src/mijual/web/site.py` — **new**: the one place the operator's string is split into its parts
  - `src/mijual/web/routers/site.py` — **new**: `GET /site/contact`
  - `src/mijual/web/app.py` · `src/mijual/web/routers/__init__.py` — the router is included/named
  - `tests/test_web_site.py` — **new**, two cases
  - `frontend/lib/types.ts` · `frontend/lib/api.ts` — `SiteContact` + `getSiteContact` (the F1 seam)
  - `frontend/app/layout.tsx` — the read, cached 10 min, timed out at 2 s, `.catch(() => null)`
  - `frontend/components/chrome/SiteChrome.tsx` — passes the value through to the footer
  - `frontend/components/chrome/Footer.tsx` — renders it, and records the operator override
  - `frontend/components/chrome/Footer.module.css` — `.contact` / `.phone` (mono) + 44px at ≤480
  - `frontend/components/chrome/copy.ts` — why no constant and no label live there
  - `works/phases/active/P11/phase.md` — notebook edit
- **validation:**
  | command | result |
  |---|---|
  | `.venv/bin/python -m pytest` | **pass** — 158 passed (156 before; the two new cases) |
  | `npm run typecheck` (frontend) | **pass** |
  | `npm run build` (frontend) | **pass** — 19 routes, route kinds unchanged; the static `/_not-found` picks up the layout fetch's `10m` revalidate |
  | `npm run smoke` (frontend) | **pass** — 22/22 |
  | `python3 scripts/workflow.py validate` | **pass** |
  | agent: 연락처 start card pressed, **dev** `http://127.0.0.1:3010/ask` | **pass** — §2 |
  | agent: same card pressed, **production** build, same origin | **pass** — §2 |
  | footer on 5 routes (`/` `/ask` `/events/…` `/stocks/…` `/portfolio`), dev **and** production | **pass** — §3 |
  | type split measured: email Pretendard 12px · phone Plex Mono 11px | **pass** — §4 |
  | widths 1280 · 1120 · 1024 · 820 · 768 · 767 · 600 · 481 · 390, dev and production | **pass** — §5 |
  | 의견 보내기 hit-tested under the launcher at 1280/1120/1024/820/768 | **pass** — never covered |
  | 390: both contact links are 44 px tall and hit-test to themselves; nothing overflows | **pass** — §5 |
  | API stopped + **fetch cache cleared**, production reload | **pass** — §6 |
- **deviations:** three, all forced by where the data has to travel — see §7. `frontend/app/layout.tsx`
  and `frontend/components/chrome/SiteChrome.tsx` are outside the plan's scope list (the footer sits
  inside a client component, so the read cannot live in it); the endpoint's home is **two** new small
  modules rather than one, following this codebase's own `mijual.web.<surface>` + `routers.<surface>`
  split; and the API — not the frontend — splits the string into email and phone.
- **doc_impact:** five lines appended to `phase.md` `## Doc impact` —
  - `operations.md`: `MIJUAL_OPERATOR_CONTACT` must be **set wherever the API runs** or the deployed
    product answers 미정 and the footer shows no contact line, while this dev box answers correctly;
    the value is now published in the chrome as well as the agent's answer.
  - `backend.md`: the new site-config surface — `GET /site/contact` (`mijual.web.routers.site`) and
    `mijual.web.site`, the one place the single free-text setting is split into email + phone.
  - `frontend.md`: the footer publishes **served** config; the **root layout** does the read (cached
    10 min, 2 s timeout) because `SiteChrome` is a client component; the absent-value contract.
  - `experience.md`: `get_contact` now answers with a configured contact, and the same two values
    appear in the footer of every reader page — the 연락처 card no longer demonstrates honest-unset.
  - `security.md`: the one operator-identifying string the product publishes is now **genuinely
    published**, in two places, at the operator's explicit instruction.
- **operator_need:** none for this slice. One item is worth the review's attention — §8.
- **notebook:** `phase.md` came back **under budget** (183 lines / 15,840 B of 200 / 16,384). Getting
  there needed real compression: the `## Objective` paragraph is now a six-line summary pointing at
  `phase.json` (which holds the verbatim objective) and `intent.md`, and the S1/S2 decision bullets
  were tightened without losing a decision. Nothing was dropped from `## Doc impact` or
  `## Operator Questions`; the P11.DECOMP contact question is marked **ANSWERED** in place.

---

## 1. What the operator asked, and what was set

Their gate report, verbatim in `plan.md`: the 연락처 card answered 「현재 등록된 운영자 연락처가
없습니다…」 and they asked where to insert `leetusik@gmail.com` / `010-3772-9916`, **and** for the same
values in the footer. The clarification round confirmed **both values, both places**.

The setting is one free-text string and stays one — `security` records it as the single
operator-identifying string the product publishes, and `get_contact` hands out exactly that string:

```
MIJUAL_OPERATOR_CONTACT=이메일 leetusik@gmail.com · 전화 010-3772-9916
```

`.env` is gitignored, so **this value is not in any commit** and does not travel with the repo. That
is the whole reason the operations doc owes the line in `## Doc impact`: unset, the deployed product
answers 미정 while this machine answers correctly.

## 2. The agent half — no code, and it works

`get_contact` (`agent/tools.py`) already read `Settings.operator_contact` and already formatted
`CONTACT_ROW`. Nothing was restructured. Pressing the 연락처 start card (card 4 of `P11.F1`'s four),
live, in the operator's runtime:

| build | 도구 행 | answer |
|---|---|---|
| dev | `운영자 연락처 → 이메일 leetusik@gmail.com · 전화 010-3772-9916` | 「운영자 연락처는 이메일 leetusik@gmail.com, 전화 010-3772-9916입니다.」 |
| production | same | same, plus 「문의 사항이 있으시면 해당 연락처로 문의해 주시기 바랍니다.」 |

`근거 0건` on both, as before — a deploy setting has no filing to cite. The honest-unset line
(「연락처 미설정」) no longer appears anywhere, in either build.

## 3. The footer half — where the value comes from

The plan's claim was checked before anything was designed around it: `make web-up` (Makefile L78–92)
passes **only** `MIJUAL_DEV_ORIGINS` to `npm --prefix frontend run dev`, and there is no
`frontend/.env` (`ls frontend/.env*` → no matches). So `process.env.MIJUAL_OPERATOR_CONTACT` is
undefined in the Next process. Confirmed, not assumed.

So the API serves it, and one seam does the whole job:

- **`GET /site/contact`** → `{"contact": …, "email": …, "phone": …}`, `null` on all three when unset.
  Its home is its own router, not `routers/ask.py`: this is site-wide config with two unrelated
  consumers (the agent's tool and the global chrome).
- **`mijual.web.site.split_contact`** does the splitting **on the server**, once, so the two readouts
  cannot drift. It is tolerant of how the operator writes the value — the test pins
  `01037729916, leetusik@gmail.com` (no labels, reversed, unhyphenated) as well as the shipped form.
- **`frontend/app/layout.tsx`** reads it with `next: { revalidate: 600 }` and a 2 s timeout. Unlike
  `P11.F1`'s cards — deliberately `no-store`, because staleness is the defect they fix — this value
  changes almost never and the footer renders on **every** page, so a fetch per render is waste. A
  contact change costs up to ten minutes to propagate; that is the right thing to be slow.
- **The footer takes it as a prop.** `SiteChrome` is a client component (it branches on the pathname
  for `/ops`), so `SiteFooter` is client code and cannot read the API on the server. The root layout
  is the nearest server component and is also the one place the read happens once for all routes.

Measured on five routes, in **dev and in the production build**, all identical:

```
자료: 금융감독원 DART 전자공시 · © 주주의관제탑 · leetusik@gmail.com · 010-3772-9916
```

`/` · `/ask` · `/events/20260803000211` · `/stocks/00336817` · `/portfolio` — it is in the layout, and
it really is everywhere. `/ops` renders no footer, as R7 requires (see §8).

## 4. The R8 tension, recorded rather than smoothed over

R8 deleted four sentences from this footer at the operator's own earlier instruction (「remove the
text and keep it simple and clean」) and justified the surviving row's Pretendard by the absence that
deletion produced: 「mono는 숫자 전용(R1)이고 남은 줄에는 숫자가 없다」 (R8 result.md §2-14). A phone
number is numerals. This change therefore puts text back into a footer the operator asked to be
minimal, and digits into a row whose typeface was argued from having none.

It is landed as an **operator override**, in the voice `chrome/copy.ts` L64–69 already uses for one,
and written into `Footer.tsx`'s doc comment with the gate report quoted as its authority. It is not
presented as something R8 signed. The two calls the plan had already made were implemented and both
survive the running result:

| | measured (1280, dev and production) |
|---|---|
| email | `notoSansKr` **12px**, `rgba(255,255,255,.45)`, `mailto:leetusik@gmail.com` |
| phone | `plexMono` **11px**, same ink, `tel:010-3772-9916` |

`--text-xs` (11px) for the phone rather than `--text-sm`: Plex Mono runs optically larger than
Pretendard at the same size, and the row has to read as one line of one weight. The contact joins the
**existing** 자료/© row — no second row was added, R8's deletion is not undone — and no Korean label
precedes the values: 「문의」 or 「운영자 연락처」 here would be invented copy, which
`chrome/copy.ts`'s own first paragraph forbids. The labelled form belongs to the agent
(`CONTACT_ROW`); the footer publishes the bare values, separated by the `·` the row already uses.

R8's five unrendered constants were **not** reopened and **P8 Operator Question Q5 is untouched**.

They are links because the values are for using: `mailto:` on desktop, `tel:` on a phone. The `tel:`
href keeps the operator's own hyphens (RFC 3966 visual separators, which dialers strip), so what a
reader taps is what a reader reads.

## 5. Geometry — R17's corner, and 390

`.inner` is `space-between` **and wrapping** (R2/R8's own shape), and the launcher overlap R17 fixed
is the thing not to re-create. Hit-tested at the button's centre with the footer scrolled into view:

| width | row | 의견 보내기 | launcher | overflow |
|---|---|---|---|---|
| 1280 | one line | hits the button (x 1110–1176) | x 1188 | none |
| 1120 | one line | hits the button | x 1028 | none |
| 1024 | one line | hits the button | x 932 | none |
| 820 | one line | hits the button (own line, x 24) | x 728 | none |
| 768 | one line | hits the button (own line, x 24) | x 676 | none |
| 767 | one line | hits the button; 「AI 질문」 link back, 40 × 21 | not rendered | none |
| 481 | two lines | hits the button | not rendered | none |
| 390 | three lines | hits the button, 66 × 44 | not rendered | none |

**One honest consequence: the footer wraps to two rows earlier than it used to.** The identity line
grew by ~215 px, so `.inner` wraps its action row at **≤820** where it previously held one row down to
~500. Measured both ways in the same DOM (the contact links hidden = the pre-F2 footer): 73 px tall
vs 118 px in that band. Nothing overlaps and nothing overflows at any width; the footer is simply
taller between 481 and 820. That is the cost of the two values, and the operator should see it.

At **390** (touch emulation, DPR 3): both contact links are **44 px** tall and each hit-tests to
itself (`min-height: 44px` at ≤480, matching what `.action` already did); they sit 23 px apart, so
neither swallows the other; the email's box does not reach the wordmark above it (link top 714,
wordmark bottom 680); `document.scrollWidth === innerWidth`. **D30 is untouched** — the 「AI 질문」
link still measures 40 × 44 at 390, neither fixed nor made worse.

## 6. Absent value, and a dead API

The rule the plan set: unset or unreachable means **no contact line at all** — never an empty label,
and never 「미정」 in the chrome, which is the agent's voice and not the footer's.

Exercised for real in the production build, with the fetch cache emptied first
(`find frontend/.next/cache/fetch-cache -type f -delete`) so nothing could be served from it:

- API stopped → `GET /ask` **200**, footer renders 「자료: 금융감독원 DART 전자공시 · © 주주의관제탑」
  and **zero** occurrences of the email, the phone, `mailto:` or `tel:`. No hole, no label, no error.
- The landing 500s in that state — that is **pre-existing and not this slice's**: `app/page.tsx`
  awaits `getBoardSummary()`/`getBoard()` with no `catch` (unlike `/stocks`, which has one). The
  server log shows exactly those two failures per request; the layout's own read cannot throw, it is
  `.catch(() => null)`.
- API restarted → the next render carries both values again; a failed fetch is not cached.

The unset case is also pinned by `tests/test_web_site.py`: three `null`s and a **200**, never an error.

## 7. Deviations from `plan.md`

1. **Two files outside the scope list** — `frontend/app/layout.tsx` and
   `frontend/components/chrome/SiteChrome.tsx`. The plan scoped the footer plus a client seam, but
   `SiteFooter` renders inside `SiteChrome`, which is `"use client"`; nothing under it can read the
   API on the server. The root layout is the nearest server component, so the read lives there and
   the value arrives as a plain serializable prop. No behaviour of either file changed otherwise.
2. **Two new backend modules, not one.** `mijual.web.site` (the split) and
   `mijual.web.routers.site` (the route), following the codebase's own pattern — `mijual.web.ask` +
   `routers.ask`, `mijual.web.portfolio` + `routers.portfolio` — and `routers/__init__.py`'s stated
   rule that derivation does not live in a router.
3. **The API splits the string, not the frontend.** The plan said not to restructure the *setting*
   into two fields, and it is not: one string, one setting, `get_contact` unchanged. But the footer
   needs the parts to type them apart, and doing that on the server keeps one parser rather than a
   second one in TypeScript that could disagree with it.

## 8. For the review

- **`/ops` renders no footer** (R7's rule holds — checked: the 자료 line does not appear there), but
  the contact **values do appear in that page's flight data**, because the root layout hands them to
  the client `SiteChrome` on every route. Nothing renders them and nothing links to them. It
  discloses nothing new — the same two values are printed in the footer of every reader page by
  design and handed out by the agent on request — but the ops door is a surface designed to say
  nothing, so the review should see it stated rather than discover it. Removing it would mean the
  layout knowing the pathname, which a root layout cannot do.
- **The footer is taller between 481 and 820** than before this slice (§5). Visible, intended,
  and worth a line in the walkthrough.

## 9. Instrument

**Not Aside.** `which aside` → not found, and there is no `/Applications` entry — the same finding
`P11.S1`, `P11.S2` and `P11.F1` recorded. The documented fallback applies: the same checks, at the
same viewports, in the same manifest runtime (`make stack-up`, `http://127.0.0.1:3010`, and the
production build via `npm run build && npm run start` on the same origin), driven through the real
**Google Chrome** on this machine over CDP (`--headless=new`,
`Emulation.setDeviceMetricsOverride`, `Emulation.setTouchEmulationEnabled` at 390). Every number,
every hit test and every answer quoted above was read out of that live DOM or off the wire; nothing
here is inferred from source. The stack was returned to dev (`make stack-up`) afterwards.
