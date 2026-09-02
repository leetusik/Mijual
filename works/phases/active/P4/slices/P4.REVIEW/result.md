# P4.REVIEW — phase review of P4 "Ship & Deploy" (gated)

- **status:** `done`
- **summary:** Validated all ten completed slices together (166 pytest, `uv lock --check`, frontend
  build/typecheck/smoke 22/22, `make smoke-prod` **17/17**, gates/estimate/pipeline determinism, both
  양식 drafts, the box read-only, GitHub secrets + probe), judged the phase against `intent.md`,
  ran the four gate stages myself in real Chrome 152 at 1280/390 against the **production build** and
  **`https://jujutower.com`**, re-ran the whole 123-line `## Regression Checklist`, and routed all
  **22** `## Operator Questions`. The phase objective shipped — the site is live, SEO is live, the
  mail transport is live, monitoring exists, both 양식 are written — but the walk found **three
  findings**, one of them material: **Cloudflare Web Analytics is ON and every production page loads
  `static.cloudflareinsights.com/beacon.min.js`**, which falsifies the phase's own decision, the
  signed `security.md` property, and a measured claim printed in 첨부2. Verdict
  **`changes_requested`**; the gate is not opened.
- **files_changed:**
  - `works/phases/active/P4/slices/P4.REVIEW/result.md` (this file)
  - `works/phases/active/P4/phase.md` (notebook: 2 Doc impact lines closing notebook findings, 1
    Doc impact line recording the beacon measurement, 1 Decision corrected in place, 6 consumed
    `for P4.REVIEW` notes dropped, `## Now` rewritten)
  - **no source file, no `docs/current`, no `docs/versions`** — nothing else was written anywhere,
    on this Mac or on the box.
- **validation:** the full table is in *Stage A* below. Everything green except the two items named
  as findings; `make smoke-prod` was **17/17 twice**, including the `www` line (the MagicDNS false
  FAIL did not reproduce this session).
- **deviations:** four, all forced by harness denials or by the operator's stale dev stack — see
  *Deviations*.
- **doc_impact:** three lines appended to `phase.md` § *Doc impact*, tagged `(P4.REVIEW)`:
  `architecture` (the Cloudflare ~100 s origin cap → 524), `qa`/`product` (renderable fields are
  **418**, not `product.md`'s 409 — re-derived twice this slice), and `security` (the
  no-third-party-origin property is **currently false on production**; do not re-assert the doc's
  checkbox without a browser re-measurement).
- **doc_versions:** none — `changes_requested`, so neither pass-only doc duty ran. The two named
  gate sections (`## Regression Checklist`, `## Operator Runtime`) are **not** written; the P4 block
  composed for the smoke list is parked in *Stage C-4* below for the passing re-review to append.
- **review_verdict:** `changes_requested` — three numbered findings, two proposed fix slices
  (`P4.F2`, `P4.F3`), both docs/config-only and both safely landable **before** the 2026-09-07 11:00
  KST freeze.
- **walkthrough:** written below under `## Walkthrough` — the operator still has 13 literal-approval
  decisions to take and five operator-only checks to run, and F1 needs their Cloudflare dashboard.
  The orchestrator should **not** run `accept-gate --open` on this verdict.
- **explain:** not written — run /explain for this phase

---

## Stage A — all ten slices validated together

| # | command (from each slice's verdict block) | outcome |
|---|---|---|
| A1 | `.venv/bin/python -m pytest` | **166 passed**, 1 standing starlette/httpx warning, 3.45 s. *(The plan expected 165; 166 is what `P4.F1` recorded and what the tree holds — the plan's number was stale, not the suite.)* **PASS** |
| A2 | `uv lock --check` | `Resolved 56 packages` — clean. **PASS** |
| A3 | `.venv/bin/python -c "import mijual.web.__main__"` | importable. **PASS** |
| A4 | `cd frontend && npm run typecheck` | `tsc --noEmit` clean, exit 0. **PASS** |
| A5 | `cd frontend && npm run smoke` | **22 pass / 0 fail**, 190 ms. **PASS** |
| A6 | `npm run build` (APFS clone, `NEXT_PUBLIC_SITE_URL=https://jujutower.com`, `MIJUAL_API_ORIGIN=…8011`) | **23 routes**, `ƒ /ask` dynamic, standalone emitted. **PASS** |
| A7 | `make smoke-prod` (twice, ~1 h apart) | **17 pass · 0 fail, exit 0** both times — including `www`. **PASS** |
| A8 | `docker compose -f compose.prod.yml config -q` | **PASS** with a throwaway `.env.prod` symlink to `.env.prod.example` (compose resolves the service-level `env_file`, so the plan's bare form cannot run off-box); symlink removed immediately, `git status` unchanged. |
| A9 | `bash -n deploy/{deploy,rollback}.sh deploy/db/{backup,restore}.sh` | all four clean. **PASS** |
| A10 | `.venv/bin/python -m mijual.gates run` ×2 | **byte-identical**; `1359 judged · 710 field rows`; `appraisal_price 47 passed / 14 n/a`; exposable `50+422+16 = 488`. **PASS** |
| A11 | `.venv/bin/python -m mijual.estimate report --today 20260902` ×2 | **byte-identical**; ▷ **718.1억원** / 하한 548.7억원 / 32 offerings / 소멸률 **14.02 %**. **PASS** |
| A12 | `.venv/bin/python -m mijual.scheduler once --offline` | **six** stages green, `0 req / 0 LLM calls / ▷ $0.0000`; `gates … exposable 488, renderable 418`. **PASS** |
| A13 | exposure invariant re-derived read-only (`exposure_of_all`, `include_suppressed=True`) | events 1359 · exposable **488** · renderable **418**; **renderable outside passed/tbd = 0**, **tbd carrying a value = 0**, **exposable in a non-exposable state = 0**. **PASS** |
| A14 | 양식 drafts — headings | 첨부1 seven `##` headings and 첨부2 five, in order, matching `submission/README.md`'s extraction verbatim; no extra section. **PASS** |
| A15 | 양식 drafts — forbidden vocabulary | `grep -ci` 미주알 / mijual / 파인튜닝 / fine-tun / PyTorch / Hugging Face → **0/0/0/0/0/0** in both `.md`. **PASS** |
| A16 | 양식 drafts — PDFs | `01_공모전기획서.pdf` **14 pages** (1,317,890 B), `02_기능명세서.pdf` **16 pages** (1,013,532 B), both `%PDF-1.4`, both open. **PASS** |
| A17 | 양식 drafts — `구성원 성명` | both carry `〈제출자 직접 기재〉 — 개인(1인) 참가`. **PASS** |
| A18 | `python3 scripts/workflow.py validate` | `Workflow validation passed.` (only the standing `oversized_doc_sections=11` advisory). **PASS** |
| A19 | box (read-only) — services | `docker ps -a --filter name=mijual`: web/api/worker/beat **Up (healthy)**, postgres/redis Up, **`mijual-schema` Exited (0)**. **PASS** |
| A20 | box — the four R7 no-harm assertions vs the R2 baseline | `edge-nginx` `StartedAt` **2026-07-02T19:22:12.325478595Z** (unchanged) · edge owns `0.0.0.0:80` and `:443` · **28** running containers (22 co-tenants + 6 Mijual) · `changple_shared_network` **17** members incl. `mijual-mijual-web-1`. **ALL FOUR MATCH.** |
| A21 | box — `crontab -l` | two lines: changple2's `0 3 * * *` certbot (untouched) and Mijual's `0 4 * * * … deploy/db/backup.sh`. **PASS** (but see **Finding 2** on what `0 4` means on a GMT box) |
| A22 | box — backups | `deploy/backups/` mode **700**, three dumps mode **600**; newest `mijual-20260902T040001Z.dump` (29 MB) is **5 h 49 m old** — younger than 24 h — and `var/backup.log` records `19 tables with data`, `KEEP=14`. **PASS** |
| A23 | box — API startup log | `mail transport: smtp mail.privateemail.com:587 tls=starttls from=주주의관제탑 <hi@hi2vi.com>`. **PASS** |
| A24 | `gh secret list -R leetusik/Mijual` | five names — `ALERT_TO`, `SMTP_FROM`, `SMTP_HOST`, `SMTP_PASS`, `SMTP_USER`. No value printed. **PASS** |
| A25 | `gh run list -w production-probe.yml` + the API | workflow `active`, latest scheduled run **success** — but **3 runs total**, only **1** of them scheduled. See **Finding 3**. |
| A26 | `python3 scripts/workflow.py docs` | no `STALE` flag (P4's notes are unconsolidated by design). **PASS** |

Container `StartedAt`s reconcile exactly with the recorded deploys once the box's **GMT** clock is
taken into account: api/web/worker/beat/schema `2026-09-02T08:54–08:55Z` = the `P4.F1` release
(17:54 KST), postgres/redis `01:29Z` = the first stand-up. Nothing on the box has moved since.

## Stage B — judgment, notebook cross-check, doc-impact coverage

**Did the objective ship?** Yes, on all six intent items. (1) Both 양식 are written, English body /
Korean headings verbatim, unsubmitted. (2) The stack is live and additive — the four no-harm
assertions still match the R2 baseline today. (3) SEO is live and measurably correct. (4) The mail
transport is live and proven by a real send; the D-day *selection* is unproven for a data reason,
not a code one. (5) A production smoke suite exists and is green, and an alerting probe exists and
was proven both ways. (6) All new Korean copy is drafted and queued for literal approval.

**Did each slice meet its brief?** Yes. Every `result.md` carries a verdict block, names its
deviations and explains them; `P4.S4` (3 dispatches), `P4.S6` and `P4.F1` (2 each) each carry their
earlier dispatches. The two multi-dispatch slices that touched production both measured the no-harm
assertions **before and after**. No slice worked around a harness denial.

**Orphaned design routes:** none. P4 shipped no design round; `frontend/app` contains no `mock*`
route (`npm run build`'s 23-route table is the whole surface).

**Notebook vs. the logs.** I checked every candidate the plan named. Covered by a `## Doc impact`
line already: the SEO disallow-vs-noindex caveat, `notify_max_mails`, the kept dev accounts
(`account 2` inside the corpus-seed line), `render_submission_pdf.py`, the freeze window, the
probe's GitHub caveats (auto-disable / default-branch / lag), `SAMPLE_FALLBACK`'s move, the
`NEXT_PUBLIC_SITE_URL` rebuild-not-restart rule, the agent's seven tools, and `## Operator Runtime`
gaining the production runtime. The `/ops` run log's seeded + `probe-anchor` rows are production
*data state* and an operator decision, correctly routed as a question rather than a doc line. **Two
gaps**, both closed by me in `phase.md` (notebook-only findings, per the plan):

- **N1 — the Cloudflare ~100 s origin cap → 524 has no Doc impact line.** `P4.S4`'s own note for
  this review says 「`architecture.md` lacks this」 and then nobody filed it. It is a durable
  architectural constraint on every long response (the agent turn most of all). Appended.
- **N2 — the renderable-field count has no Doc impact line.** `product.md` says **409**,
  `qa.md:98` says **418**; `P4.S8` found the conflict and resolved it *inside 첨부2* only. I
  re-derived **418** twice independently this slice (A12 pipeline `gates` line and A13's read-only
  `exposure_of_all`). Appended, so the docs phase corrects `product.md`.

I also appended a third line recording **Finding 1**'s measurement against `security.md`, because
whichever way the operator decides, a docs phase must not re-assert that checkbox unmeasured.

**Every `result.md` decision survives in `phase.md`.** No decision recorded in a slice log is
missing from `## Decisions`; one is now **wrong** rather than missing — the 「Cloudflare Web
Analytics stays OFF」 entry — and I corrected it in place with the measurement (`## Decisions` is the
section the review may replace superseded lines in; the finding itself is not closed by me).

### Findings

**1 — MATERIAL. Cloudflare Web Analytics is ON: every production page loads a third-party beacon,
and three signed/printed claims say it does not.**

Measured in real Chrome 152 over CDP, headful, on `https://jujutower.com` at 1280 and 390:

```
REQ : https://static.cloudflareinsights.com/beacon.min.js/v3d52b47920f24c319d37e2661827c42b1787588026925
RESP: … 200          on  /  ·  /ask  ·  /stocks   (script tag present in the served HTML)
```

`Network.requestWillBeSent` shows `static.cloudflareinsights.com` on **every one of the ten routes**
battery A visited, at both viewports. The same routes served from the local production build reach
**no host but their own**, so the injection is Cloudflare's, at the edge — exactly the mechanism the
phase's own `## Decisions` entry described when it decided to keep the feature **off**.

What it falsifies:

- `phase.md` `## Decisions`: 「**Cloudflare Web Analytics stays OFF**: it injects `beacon.min.js`
  from `static.cloudflareinsights.com` at the edge, against `security.md`'s *measured* signed
  property…」 — the decision is right; the zone does not implement it.
- `phase.md` `## Doc impact` (`P4.S5`, re-measured `P4.S6`): 「the measured **no-third-party-origin
  property survives SEO** … **zero off-origin `src`/`href` references** … Cloudflare injects nothing
  at the edge.」
- `docs/current/security.md` § 「**No page contacts a third-party origin.**」 — a **standing property
  to re-check**, checked `[x]`.
- **`02_기능명세서.md` §4**, in a document written for judges: 「Measured on the live pages: **no page
  contacts a third-party origin** — no analytics, no external font or script, no beacon; the only
  external references in the HTML are the DART 원문 links themselves.」
- the `## Regression Checklist` line 「**제3자 origin 0건**」.

**Why every earlier check passed.** Cloudflare serves the beacon only to browser-shaped clients:

```
curl -A "Mozilla/5.0 … Chrome/152 …" https://jujutower.com/ | grep cloudflareinsights   → 0
curl -A "Mijual-smoke/1.0"           https://jujutower.com/ | grep -c cloudflareinsights → 0
real Chrome                                                                              → 1 (fetched, 200)
```

So `scripts/smoke_production.py`'s `check_third_party` — which regexes `src|href` out of a
`urllib`-fetched landing page — **cannot ever see it**, and `P4.S6`'s "grep over 8 live pages" could
not either. This is precisely the bug class the workspace's "real browser, not a pre-written
assertion suite" doctrine exists to catch, and it took a real browser to catch it.

**Proposed fix slice `P4.F2` — `fix / high`:** turn Cloudflare Web Analytics **off** for the
`jujutower.com` zone (operator dashboard action; the slice verifies), re-measure the property in a
real browser at 1280/390 across five routes, teach `check_third_party` to fail on an edge-injected
beacon (it must fetch with a browser `User-Agent`/`Accept` and assert on `<script src>` too), and —
if the operator instead chooses to **keep** analytics — amend 첨부2 §4, `security.md`'s checkbox and
the checklist line instead of the zone. **Docs/config only: no image rebuild, no `deploy.sh`, so it
lands safely before the 09-07 11:00 KST freeze either way.**

**2 — MODERATE. `deploy/runbook.md` still calls the nightly backup an open decision, and its
rationale has the wrong timezone.**

R7 reads 「**Nightly backup — an open decision for `P4.S4`.** If the box has cron … a reasonable line
is `0 4 * * * …`」 and 「**04:00 KST** sits between the 19:30 evening pipeline and the 07:30 morning
one」; § *Open questions this runbook cannot answer* item **2** is still 「install it, or operator-run
only? … the decision is the operator's」. Both are stale: the operator decided, `P4.S4` installed it,
and it has already run (`mijual-20260902T040001Z.dump`, 19 tables, mode 600, `KEEP=14`). And the box
is **GMT** (`timedatectl` → `Time zone: GMT (GMT, +0000)`; `date` → `Wed Sep 2 09:49:11 GMT 2026`),
while the app containers log in KST — so `0 4 * * *` fires at **13:00 KST**, not 04:00 KST. No
operational harm (13:00 KST is still between the 07:30 and 19:30 collections), but an operator
reading R7 today is told the opposite of what is running, twice. Open question **1** (www) *was*
struck through and answered; **2** was missed.

**Proposed fix slice `P4.F3` — `fix / low` (docs only):** rewrite R7's nightly-backup paragraph and
open question 2 to record the installed line, the first two dumps, `KEEP=14`, and that `0 4 * * *`
on a GMT box is **13:00 KST**. No code, no deploy, no freeze interaction.

**3 — MODERATE, no fix slice: the Actions probe is delivering ~1 scheduled run in 5 hours, not 6 an
hour, so UptimeRobot stops being optional.**

`.github/workflows/production-probe.yml` is `state: active` with `cron: "3,13,23,33,43,53 * * * *"`,
and the one scheduled run there has been (`33612398750`, 2026-09-02 09:07:32Z) **succeeded**. But
`gh api …/runs` reports `total_count: 3` for the workflow — two manual dispatches from `P4.S6` and
that single scheduled run — against roughly 28 expected in the ~4 h 47 m since `811dec5` reached the
default branch. The workflow's own header predicted 「scheduled runs can **LAG**」; the measured
behaviour is heavier than lag. The phase's mechanism is sound (proven green *and* red, alert mail
really sent) but its **cadence** is GitHub's to give, and the 결격 rule this monitoring exists for
disqualifies on a single unnoticed outage in 09-07 11:00 → 09-11 23:59 KST.

This is not a defect the phase introduced and there is no code fix, so it earns **no fix slice** —
it is routed into the walkthrough, where the UptimeRobot monitor is promoted from
「belt-and-braces, not a blocker」 to **required before the freeze opens**, with its exact settings.

## Stage C — the gate stages (`acceptance.required: true`)

### C-1 Manifest

Present and filled. `## Operator Runtime` (operations v0013) records the dev runtime; `P4.S4`'s
`## Doc impact` line adds the production runtime, access path, logs command, credential location,
browser instrument and viewports. No `needs_operator` on the runtime.

**Instrument.** Aside is unavailable on this Mac (daemon down, no agent account) and the manifest
names Chrome desktop, so I used the sanctioned fallback: **real Google Chrome 152 over the DevTools
protocol, headful**, launched with
`open -na "Google Chrome" --args --remote-debugging-port=9477 --user-data-dir=<scratchpad>` — a
throwaway profile, never the operator's, confirmed headful via `/json/version` before use, and
killed at the end. Viewports **1280** and **390** (`Emulation.setDeviceMetricsOverride`, `mobile:
true` at 390), plus **1512 / 1440 / 768 / 767 / 481** for the mono guard. No `nohup` launch was used.

**Model calls: 6 of the 9 budgeted — 1 of 1 on production, 5 of 8 on the dev stack.**

### C-2 Independent spot-check of the phase's headline claims — I opened the product myself

| headline claim | what I measured | verdict |
|---|---|---|
| board with real corpus data, tab title `주주의관제탑` | `/` at 1280 & 390: 15 ranked rows, 「15건 더 보기」, 「남은 360건」, 15 DART `↗` links; title `주주의관제탑` | ✅ |
| a 종목 page: title `툴젠 \| 주주의관제탑`, drafted description, self-canonical, `og:image` | title exact; `description` = `툴젠 — 진행 중인 권리 1건. 놓친 권리와 진행 중인 권리를 마감일과 함께 조회합니다. 자료: 금융감독원 DART 전자공시.`; canonical `https://jujutower.com/stocks/00547510`; `og:image` present | ✅ |
| an 이벤트 page likewise | title `툴젠 — 신주인수권증서 매매 마감 \| 주주의관제탑`; description `툴젠 유상증자 신주인수권 — 신주인수권증서 매매 마감 2026-09-07. 자료: …`; self-canonical; `og:image`; one JSON-LD block | ✅ |
| `/events/00000000000000` → 404 not 500 | **404** on production and on the production build | ✅ |
| `/ask` streams **incrementally** | one production turn (「툴젠 신주인수권증서 매매 마감 언제야?」): **4 distinct DOM states at 366 / 2,483 / 3,894 / 6,008 ms**, one `[role=status]` throughout, 0 at the terminal — not one late blob | ✅ |
| `/portfolio?sample=1` — four states, edits survive | production: four distinct issuers (**뷰노 · 제이에스링크 · 페니트리움바이오 · 휴맥스** — *different from `P4.F1`'s 아이에이 set, because the composition is live*), ① D-43 발행가 확정 전, ② D-1, ① 소멸 with 놓친 돈 **79,182원추정**, ③ 통지 마감 지남 D+6; 보유량 500 → **777주** survives reload; a 삭제 stays hidden after reload; 챙겼습니다 flips 놓친 돈 → 챙긴 돈, drops 「놓친 돈 상세 →」, survives reload; store is `{"v":2,"shares":…,"removed":…,"claims":…}` | ✅ |
| `/ops` door = 마크 + 운영자 ID + 비밀번호 + 로그인, `noindex` | production door innerText is exactly `주주의관제탑 운영 / 운영자 ID / 비밀번호 / 로그인` (25 chars, 4 lines), two inputs, **no footer**, `robots: noindex, nofollow`, **none of D15's four rule lines** | ✅ |
| `/ops` 개요 shows four beat entries incl. `notify-deadlines 08:30` | **could not log in — the harness denied reading `MIJUAL_OPS_*` from `.env.prod`.** Verified instead from `src/mijual/beat.py`: exactly **four** entries — 07:30 daily-morning, 19:30 daily-evening, **08:30 notify-deadlines**, 04:30 weekly-resync; and `/ops/overview` answers **401** unauthenticated in the box's API log | ⚠️ operator-only |
| `/robots.txt` — Cloudflare's block then the origin's | **1,972 B** served, carrying `Sitemap: https://jujutower.com/sitemap.xml` (smoke `robots` PASS) | ✅ |
| `/sitemap.xml` on the apex, no `/ops`,`/auth`,`/portfolio` | **830 `<loc>`** now (was 800 at `P4.S6` — it is `force-dynamic` and the corpus grew 445 → 464); smoke asserts all-apex, 3 static, no excluded path | ✅ |
| `/manifest.webmanifest`, `/opengraph-image.png` 1200×630 | manifest 200 `name=주주의관제탑`, all 5 icons 200; OG image 200 `image/png` **1200×630**, 32,679 B — **and I looked at it** (white 주주의관제탑 wordmark + sparkle on cosmos paper; legible, no tagline) | ✅ |
| `/auth/login`, `/portfolio` → `noindex, nofollow` | both, plus `/auth/reset`, `/ops` and the 404 (`noindex`); the five indexable routes carry `index, follow` + a self-canonical | ✅ |
| `http://` and `www` → 301 to the apex | smoke `www` **301 → https://jujutower.com/x?y=1** and `http-redirect` **301**, green twice today | ✅ |
| footer 운영자 연락처 `mailto:`/`tel:` on every reader page | 1 `mailto:` + 1 `tel:` on all nine reader routes at 1280 **and** 390; `/ops` renders **no** footer | ✅ |
| no third-party `src`/`href` on the landing | **FAILS on production** — see Finding 1. Clean on the local production build and in dev | ❌ |
| the staleness banner after beat's 19:30 KST run | **cleared.** `/api/board/summary` → `freshness.stale: false`, `as_of 2026-09-02T19:37:03+09:00`, `age_hours 0`; the landing prints 「기준 2026-09-02 19:37 KST」 and **no** 「데이터가 갱신되지 않고 있습니다」 | ✅ resolved |

### C-3 Fresh-eyes walk (first-time Korean reader, production, 1280 and 390)

Not judged against the design record. Everything below is a **decision for the operator**, never a
silent fix.

1. **The big red timer has no subject on the first screen (390).** The 소멸 카운트다운 card opens with
   `2일 03:26:04` in alert red at ~40px; its label 「소멸 카운트다운」 and the 소멸주의보 sentence sit
   *below* it. A first-time reader meets an alarm clock counting down to something unnamed.
2. **The landing's `h1` is 「내 종목 조회」** — a feature name, not the service. Between the mark and the
   hero subtitle, nothing on the first screen says what 주주의관제탑 *is* or who it is for. The
   `<meta name="description">` says it well; the page does not.
3. **The share card carries the wordmark and nothing else.** A stranger meeting a KakaoTalk preview
   learns a name. One line of the description would make the link self-explanatory. (Gate item 8 in
   the meta-copy list — decide it with this in mind.)
4. **`배정비율 (1주당) 0.0863800841`** — ten decimals is faithful to the filing and unreadable as a
   number. The 배정 신주 conversion beside it is what a reader actually wants.
5. **The board's 종목 column gives no company context.** 「CB 지엔코 ↗ 전환청구 개시 2026-09-10 D-8」 is
   precise and completely opaque to someone who does not already know 지엔코. Nothing wrong; it is
   just a wall of 436 CB rows before the 유증 tab is discovered.
6. **`/auth/reset` without a token silently becomes `/auth/login`.** Correct, but a reader who
   bookmarked the reset page gets no line explaining the bounce.
7. **The footer publishes a personal e-mail and phone on every page.** Deliberate (R8 + `P11.F2`),
   and worth one conscious re-confirmation now that the site is public and indexable.
8. **Nothing dead.** Every visible control I pressed did something: the tabs, 더 보기/접기, 펼치기,
   row clicks, `[근거]`, 수정/저장, 삭제, the 챙겼습니다 checkbox, the composer, 새 대화, the search
   typeahead, both auth forms. No spinner without an end, no empty state without a sentence.

### C-4 The whole `## Regression Checklist`, re-run — 123 lines

Environments: **dev** = `next dev` on `127.0.0.1:3022`; **build** = the standalone production build
(`node .next/standalone/…/server.js`) on `127.0.0.1:3021`; **prod** = `https://jujutower.com`. Both
local servers ran against a **current-code** API on `127.0.0.1:8011` and the operator's dev Postgres
(see *Deviations* — the operator's own 8010 API is stale and I was not permitted to restart it).

| block | lines | dev | build | prod | not a clean pass |
|---|---|---|---|---|---|
| general (repo/pipeline/guards) | 14 | — | — | — | 3 recorded (below) |
| P8 surface | 58 | ✅ | ✅ | ✅ | 4 recorded |
| P9 surface | 18 | ✅ | ✅ | partial | 5 recorded |
| P10 rebrand + rounds 2/3/4 | 23 | ✅ | ✅ | ✅ | 6 recorded |
| P11 | 10 | ✅ | ✅ | ✅ | 3 recorded |
| **total** | **123** | | | | **21 not clean passes, of which 1 is a FAIL** |

**Highlights measured green** (one line each, all three environments unless noted): pytest 166 ·
build/typecheck/smoke 22/22 · `gates run` twice byte-identical over 710 rows · exposure invariant
0/0/0 · `estimate report` twice byte-identical · `once --offline` six stages at 0/0 · no quota or
storage-denial copy and no `localStorage` in the ask surfaces · no evalset "human ground truth"
claim (every occurrence is the denial) · no secret-shaped value in any tracked file · brand mark
painted in nav **90.75×27 `translateY(-8px)`** and footer **80.66×24 `translateY(-6px)`**, natural
**1247×371**, `alt="주주의관제탑"`, on all nine reader routes at 1280 **and** 390 · both document
titles in the real tab (reader `… | 주주의관제탑`, `/ops` `주주의관제탑 운영`) · three `link[rel*=icon]`
on every reader **and** `/ops` page · no reader page's innerText contains 미주알/미주얼/MIJUAL/Mijual ·
`/assets/mijual-*.png` referenced nowhere in any code path · `src/mijual/`, `MIJUAL_*`,
`X-Mijual-CSRF`, `name = "mijual"`, `"name": "mijual-frontend"` all intact · `notoSansKr` +
`plexMono` only, **no Pretendard face**, exactly one `link[rel=preload][as=font]` per reader route
and **none** on the 404 · no request to `fonts.googleapis.com`/`fonts.gstatic.com` anywhere · nav
link `left`s **identical to the decimal** across five routes (`[218.75, 279.484375, …]`) with the
`::after` twins carrying `content:"AI 질문"`/`"보유 종목"` at `visibility: hidden` · board 15 rows →
「15건 더 보기」 → 30 rows + 「처음 15건으로 접기」 (남은 360 → 345) and a tab switch resets the window ·
row click anywhere opens the detail · 펼치기 flips `aria-expanded` and a 추후결정 row shows the label
with no date · 소멸주의보 on a **tied** 청약 마감 says 「… 2026-09-04, **3개 종목**」 matching
`next_lapse.tie_count: 3` · 「읽은 실적보고서」 absent from the DOM · hero 「삼성」+Enter selects without
navigating and the second Enter goes (`/stocks/00126186`) · 「‘삼성’과 일치하는 종목이 없습니다」 with
the correct 과 particle · 빈 `/stocks` shows 감시 대상 3종 + 감시 중 464건 + 집계 범위 · **`/stocks`
main = 620px and `/stocks/{corp}` = 960px in the production build** · 계양전기-class 발행가 확정 전
(툴젠) prints **no 원 amount at all** before a holding · `[근거]` opens an **overlay popover** —
`a[href*=dart]` **3 → 4 → 3**, the document-coordinate snapshot of 12 elements **byte-identical**
before and after, one popover at a time under a real pointer click, Esc closes · popover ground
`rgb(14, 26, 21)` + `border-left: 2px rgb(95, 208, 165)` + `z-index: 40`, 380px under a prose chip
and **732px block-wide** under a data row · citation chips **14×16px** · answers carry their chips
inline after the period with **0 `<br>`** in the prose and 근거 N건 = the chip count · 「안녕」 → 1–2
sentences, 도구 0 · 칩 0 · 푸터 0 · not a refusal · 범위 밖 → one line + a 갈 곳, **no refusal frame** ·
계산 → 「검증된 계산 · 배정 신주 · 1,000주 × 0.507594018 = 507주」 with the 입력 chips and the walk
검색 → 이벤트 읽기 → 계산 · 주입 시도 → 「그 요청에는 답변하지 않습니다.」 with 도구 0 · 칩 0 · 링크 0
and the incident in the API log as `agent security_check · prompt_extraction · <session_hash> ·
<발췌>` · the ▷ spend ledger line present on every turn · `/ask` start screen = **four cards in two
even rows** (316×56 at 1280, one 358px column at 390), 익명 줄 0 · 새 대화 0 · 「범위:」 0, composer
disabled-when-empty → 보내기 → one `[role=status]` → gone at the terminal · four page loads produced
**four** `GET /ask/start-cards` (nothing cached) · with the API unreachable `/ask` still answers
**200 with four cards** · 「새 대화」 exists only once a thread does · 완료 푸터 = 근거 N건 · 접수번호 ·
KST + DART 원문 ↗ + 이벤트 상세 + 내 종목 조회 and **no 「다시 질문」** · no launcher/widget in the DOM
at 767/600/390 and a launcher at 768 · auth: empty submit → 「이메일과 비밀번호를 입력해 주세요.」 with
**no** request and no `required`/`pattern`; malformed → 「이메일 주소 형식이 올바르지 않습니다.」 with no
request; 「비밀번호 재설정」 with an empty address is clickable, focuses the email field, sends nothing;
`/auth/reset?token=…` has **one** password field, 「8자 이상」, no email field · **0 mono line splits**
at 1512/1440/1280/768/767/481/390 measured by rect `top` (never by rect count) · 0 interactive
targets under 44px on the 390 detail and stock pages, no horizontal overflow anywhere · the 404
echoes **the reader's own path in the SSR HTML** on 7/7 static shapes in the production build **and
on production**, Korean reading `/%EC%96%B4%EB%94%94` · `make smoke-prod` 17/17 twice.

**The 21 lines that are not clean passes:**

| # | line | what I recorded |
|---|---|---|
| 1 | 「pytest green (**158**)」 | the count in the doc is **stale**: the suite is **166**. Green, but the number needs updating at the next consolidation |
| 2 | 「the **four** AST import scans / anonymity scan / tool signature / ops unsafe method」 | **covered by the 166-test run**, not re-derived as four standalone scans. Named guards confirmed present: `test_no_request_path_module_imports_a_spending_module`, `test_the_agent_package_imports_no_spending_module`, `test_no_conversation_column_can_name_a_person_and_none_joins_an_account` |
| 3 | 「`extract recheck` and `evalset refresh-recall` → second run writes nothing」 | **not re-run.** Both write to the operator's dev database; a review slice does not. The `--offline` pipeline's own `extract [dry-run]` and `reparse 69/69, 0 with changed facts` exercise the same idempotence read-only |
| 4 | 「the agent's own two numbers (인용 원문 / unmarked numerals), if a live pass was run」 | **N/A** — no live evalset pass was run this slice. The six turns I did spend produced no 「미확인」 and every citation opened its own DART 원문 |
| 5 | 「자동 갱신: leave the landing open for two intervals」 | **not re-run** — two full refresh intervals of dwell time did not fit the slice. The refresh path is live: the anchor moved 03:20 → **19:37 KST** across the phase and the board re-rendered |
| 6 | 「의견 보내기 … a 202 shows the 접수 번호」 | the control is present and answers at 1280/390; **I did not submit feedback** (it writes a production row) |
| 7 | 「≤480 sheet: overlays without pushing the page…」 | 390 renders the 메뉴 sheet and no horizontal overflow; the backdrop/Esc/× + body-scroll-release triad **not re-derived** |
| 8 | 「푸터 코너: 「의견 보내기」 answers `elementFromPoint` at 768·1024·1120·1255·1256·1280」 | **not re-derived** — my selector matched a 0×0 duplicate of the label, an instrument failure, not a product one. The other half **passed**: the desktop footer 「AI 질문」 link is `display: none` at all six widths |
| 9 | 「no vocky value in the client bundle」 | **passed**, on the production build I made (`grep -rl 'vk_\|vocky' .next/static` → nothing) rather than on the box's image |
| 10 | 「아시아나 ③ / 풍전약품 / 세기상사 / 계양전기 …」 (4 P8 lines keyed to named corpus rows) | the corpus moved; 세기상사 and 계양전기 are **no longer in the sample or the board's first window**. I checked the *shapes* on today's rows instead — 툴젠 ①, 제이에스링크 ②, 휴맥스 ③, 페니트리움바이오 ① 소멸 — and every shape held. Recorded as precondition-gone, not as a pass |
| 11 | 「보유 종목 controls ≥44px at 390/767」 | **one** raw `input[type=checkbox]` measures **15×15** on `/portfolio` at 390 (the 챙겼습니다 box). Its label is the real target; earlier reviews evidently measured labels. Reported, not judged |
| 12 | 「진행 표시 … never appears in `sessionStorage`」 | the on-screen half passed (exactly one `[role=status]`, gone at the terminal); the `sessionStorage` half **not inspected** |
| 13 | 「도구 4개 이상 + 완료 → folds to 「도구 N번 · 공시 M건 읽음」」 | **not exercised** — none of my six turns reached 4 tool rows (max 3). ≤3 stayed flat, as required |
| 14 | 「소진 턴: dimmed prose + folded 도구 흐름」 | **not exercised** — no budget-exhausted turn was provoked |
| 15 | 「도구가 확인하지 않은 공시 수치 (「오늘 며칠이야?」) → 「미확인」 marker」 | **not exercised** (would have cost a seventh turn); no 「미확인」 appeared spuriously in the six turns that ran |
| 16 | 「대화 로그 저장: `conversation_turn.blocks` holds the exact frames」 | **not inspected** — reading stored conversation rows was out of scope for a read-only review |
| 17 | 「`prefers-reduced-motion`: zero animated elements beyond the footer fade」 | **not re-derived** |
| 18 | 「로고가 옆 글자와 한 줄로 읽힌다 (8× pixel scan, band bottom vs Hangul ink bottom ≤0.5px)」 | verified **by proxy**: the mark paints at the exact post-round-4 geometry (`90.75×27` / `80.66×24`, `translateY(-8px)`/`(-6px)`, natural 1247×371) on every route in all three environments. The pixel scan and its `translateY(-7px)` control were **not** re-run |
| 19 | 「워드마크가 붙어 읽힌다 (alpha hash, ink columns, counter islands)」 · 「파비콘 타일은 투명하고 잉크는 한 색」 | **not re-derived** — pixel-level asset forensics. Served-bytes half held: OG image 1200×630/32,679 B on production, all five manifest icons 200 |
| 20 | 「스크린리더가 라벨을 한 번만 읽는다」 · 「활성 탭이 형제를 밀지 않는다 (`/ops` six routes)」 · 「390의 `/ops` 탭 줄」 | the reader half **passed** (nav lefts identical to the decimal; twins `visibility: hidden`); the **`/ops` half needs a login the harness denied** |
| 21 | 「프로덕션에서 모르는 주소를 열면 … no React #418」 + 「`suppressHydrationWarning`은 딱 그 한 요소만」 | the echo half **passed** 7/7 in both production runtimes. **0 hydration messages** across 4 routes × 2 viewports — but **my control could not be made to fire** (a pre-hydration `<body>` attribute produced no warning), and the checklist itself forbids reporting 「no hydration messages」 without a firing control, so this is recorded as **not re-derived**, not as a pass |

**The P4 block composed for the smoke list** (parked — **not** appended, because this is not a
passing review; the passing re-review appends it verbatim after the P11 block, and updates the
first line's counts to pytest **166** / frontend smoke **22/22**):

```
- [ ] 프로덕션 스모크: `make smoke-prod` is 17/17 exit 0 against the live origin — health, landing
      HSTS+CSP+cf-ray, www and http 301s, board, one 종목 and one 이벤트 page, bad rcept_no 404,
      start-cards, the /ops door, robots/sitemap/manifest/OG/noindex, no off-origin src/href, and
      the three co-tenant sites at 200. A red `www` line from this Mac is its own MagicDNS
      resolution, not production — re-check with `--resolve www.jujutower.com:443:104.21.21.26` (P4)
- [ ] `/ask` 스트리밍 (프로덕션): one turn through Cloudflare renders **≥4 distinct DOM states over
      several seconds** at 1280 and 390 — never one late blob — with exactly one `[role=status]`
      while it runs and none at the terminal (P4)
- [ ] 실데이터 표면: the board, one 종목 and one 이벤트 page render from the live corpus at 1280 and
      390, and the landing's 기준 시각 is younger than the staleness threshold after beat's 19:30 KST
      run (P4)
- [ ] `/ops` 도어와 개요: the door is exactly 마크 + 운영자 ID + 비밀번호 + 로그인 with `noindex,
      nofollow` and none of D15's four rule lines; logged in, 개요 lists **four** beat entries
      including `notify-deadlines 08:30` (P4)
- [ ] 푸터 연락처: 운영자 `mailto:` and `tel:` links resolve on every reader page at both viewports;
      `/ops` renders no footer (P4)
- [ ] 리다이렉트: `http://jujutower.com/` and `https://www.jujutower.com/x?y=1` both 301 to the apex
      with path and query preserved (P4)
- [ ] SEO 표면: `/robots.txt` serves Cloudflare's managed block **then** the origin's rules and
      `Sitemap:`; `/sitemap.xml` is apex-only with no `/ops`,`/auth`,`/portfolio`;
      `/manifest.webmanifest` and `/opengraph-image.png` (1200×630) answer 200 (P4)
- [ ] 인덱싱 규칙: the five indexable routes each carry a title, a description, a **self-canonical**
      and an `og:image`; `/ops`, `/auth/login`, `/auth/reset`, `/portfolio`,
      `/portfolio/notifications` carry `noindex, nofollow` and no canonical (P4)
- [ ] 나쁜 접수번호: `/events/<nonexistent>` answers **404, not 500**, in the production build and on
      production (P4)
- [ ] 샘플 포트폴리오 (프로덕션): four **distinct** issuers with at least one upcoming ① carrying a
      live D-day, an ②, the ① 소멸 with its 놓친 돈, and the ③; a 보유량 edit and a 삭제 both survive
      a reload. **Never assert the company names** — they move daily (P4)
- [ ] D-day 메일 데모: `once --stages notify --no-lock --label gate-demo --notify-today YYYYMMDD`
      sends one mail to an account holding a stock at that lead day, and an identical second run
      reports `already-sent` (P4)
- [ ] 배포 무해성 (any deploy): `edge-nginx` `StartedAt` unchanged at
      `2026-07-02T19:22:12.325478595Z`, `edge-nginx` still owns :80/:443, **28** running containers,
      `changple_shared_network` **17** members (P4)
- [ ] 백업: `deploy/backups/` holds a dump **younger than 24 h**, mode 600 inside a 700 directory,
      and `var/backup.log`'s last entry verifies 19 tables with `KEEP=14` (P4)
- [ ] 제3자 origin (프로덕션, 실브라우저): opening `/`, `/ask` and `/stocks` in a **real browser**
      issues **no request to any host but the origin and `dart.fss.or.kr`**. A `curl`-based grep
      cannot see an edge-injected beacon — this line must be run in a browser (P4)
```

### C-5 Routing — all 22 `## Operator Questions`

| # | entry (source) | route |
|---|---|---|
| 1 | Mail sender brand — `hi@hi2vi.com` or a new sender (P4.DECOMP) | **walkthrough decision 3a** |
| 2 | Mail subject re-signature, D23 (P4.DECOMP) | **answered — nothing outstanding.** Re-signed to 주주의관제탑 by `P4.S2`; D23 dropped to `works/deferred/dropped/D23/`. Confirmed live: the API announces `from=주주의관제탑 <hi@hi2vi.com>` |
| 3 | New Korean product copy needs literal approval (P4.DECOMP) | **walkthrough decisions 3a–3b** (this is the umbrella over #6 and #17) |
| 4 | Removing the R7 rules from the `/ops` door, D15 (P4.DECOMP) | **walkthrough decision 3c.** Applied and verified by me on production: the door is exactly four lines |
| 5 | `구성원 성명` on both 양식 headers (P4.S7) | **walkthrough decision 3j** |
| 6 | **THE MAIL COPY** — 6 items incl. the `마감:` label doubt (P4.S2) | **walkthrough decision 3a** (items 1–6 listed) |
| 7 | `www.jujutower.com` alias (P4.S3) | **answered — ANSWERED AND DONE.** Verified by me: `301 → https://jujutower.com/x?y=1`, path+query preserved, apex canonical |
| 8 | Nightly backup cron — install or not (P4.S3) | **answered — ANSWERED AND DONE** (installed, has run). **But the runbook still says otherwise → Finding 2 / `P4.F3`** |
| 9 | The 정정 해석 thinking preset, D-4 (P4.DECOMP) | **deferred job A** |
| 10 | The corpus seed (P4.S4) | **answered — ANSWERED AND DONE.** Re-confirmed live: 464 events after beat's 19:30 run |
| 11 | The harness's ssh permission for the box (P4.S4) | **deferred job C.** Still unstable — this slice was allowed `docker ps`/`inspect`/`logs`/`crontab`/`ls` and denied `docker compose …` and the `.env.prod` credential read |
| 12 | **THE D-DAY MAIL WAS NEVER SENT ON PRODUCTION** (P4.S4) | **walkthrough operator-only check 2e** — still the one surface a browser cannot show. 툴젠 `00547510` is **D-5** today (마감 2026-09-07) |
| 13 | Which Cloudflare SSL/TLS mode is set (P4.S4) | **walkthrough decision 3k** (one look; and take 3l in the same visit) |
| 14 | The `/ops` run log's 21 dev-era + 21 `probe-anchor` rows (P4.S4) | **walkthrough decision 3g** |
| 15 | The board's staleness banner (P4.S4 / P4.S8) | **answered — resolved by measurement.** `freshness.stale: false`, 기준 **2026-09-02 19:37 KST**, banner gone. Nothing outstanding |
| 16 | The harness denied three production actions (P4.S4) | **deferred job C** (same boundary as #11) |
| 17 | **THE META COPY** — 9 items incl. the share card and Naver (P4.S5) | **walkthrough decision 3b** (items 1–8) and **3h** (Naver, item 9) |
| 18 | The public repo publishes box IP / user / paths and the alert address (P4.S6) | **deferred job B** |
| 19 | The sample's companies change daily → 첨부2 §5 shape (P4.F1 / P4.S8) | **walkthrough decisions 3d** (accept F1's supersession of R5-4 「고정」) and **3f** (accept 첨부2 §5's state-plus-dated-example shape) |
| 20 | `make smoke-prod` can go red from this Mac (MagicDNS) (P4.F1) | **deferred job D** — and folded into the walkthrough as a known local false FAIL. It did **not** reproduce today: 17/17 twice |
| 21 | The 심사용 테스트 계정 — self-signup or an operator-made account (P4.S8) | **walkthrough decision 3e** |
| 22 | The two drafts disagree about their own body language (P4.S8) | **walkthrough decision 3i** |

**Nothing is unrouted:** 13 walkthrough decisions, 5 operator-only checks, 4 deferred jobs, 5
answered-and-closed.

**Deferred jobs for the orchestrator to file** (I do not run `defer-job`):

- **A — Decide the 정정 해석 thinking preset.** *Reason:* the backlog prices at 69 calls against
  `extract_max_calls=60` per run and the level is undecided; production is now the first unattended
  worker. *Trigger:* the first production run whose `extract` stage hits the call ceiling, or before
  any backfill.
- **B — Harden what the public repo publishes.** *Reason:* `leetusik/Mijual` is public;
  `deploy/runbook.md` and `deploy/edge/README.md` carry the box's IP, ssh user and absolute paths,
  and `works/**` carries the operator's personal alert address. No credential, but it is the
  reconnaissance an attacker starts from. *Trigger:* before the URL is circulated beyond the
  judges, or immediately if the repo stays public after the contest.
- **C — Settle the harness's production boundary.** *Reason:* `ssh oracle-cloud` reads are allowed
  or denied unpredictably (`docker ps` yes, `docker compose … ps` no; `.env.prod` credential read
  no), which cost this review the `/ops` 개요 check and cost `P4.S4` the D-day demo. *Trigger:* the
  next slice that needs box inspection or an `/ops` login.
- **D — This Mac's MagicDNS answer for `www.jujutower.com`.** *Reason:* Tailscale's resolver
  (`100.100.100.100`) returns `104.219.250.36` / `2.59.170.19` for `www`, in no Cloudflare range, so
  `make smoke-prod` can show a red `www` line that is not production. *Trigger:* the next red `www`
  line — check `dig @1.1.1.1` before believing it.

---

## Walkthrough

**Do not run this as an acceptance walk yet.** This review is `changes_requested`, so the gate stays
shut until `P4.F2` and `P4.F3` land. Step 1 is the one thing to do **now**; everything else is the
script for the re-review's gate. Reply per number ("1 ok, 4 change X").

**0. What is already true, verified by the reviewer on `https://jujutower.com` today.** The site is
live and correct at 1280 and on a phone: real corpus (464 감시 중), the streaming AI answer, the four
SEO surfaces, the four-state sample with edits that survive a reload, the `/ops` door, both
redirects, the footer contact links, `make smoke-prod` 17/17. The staleness banner **cleared itself**
at beat's 19:37 KST run. You do not need to re-derive any of that.

**1. FIRST, and it is yours alone: Cloudflare Web Analytics is ON.** Every page on
`jujutower.com` loads `static.cloudflareinsights.com/beacon.min.js` in a real browser — it is
invisible to `curl`, which is why nothing caught it. It contradicts the phase's own decision, the
security doc's signed 「no page contacts a third-party origin」, and a sentence printed in 첨부2 §4.
Open **Cloudflare → jujutower.com → Analytics & Logs → Web Analytics** and either
**(a)** turn it **off** — the intended state, one toggle, no deploy — or **(b)** decide to keep it,
in which case 첨부2 §4, `security.md` and the regression line get corrected instead. Tell the
orchestrator which; `P4.F2` does the rest and re-measures in a browser.

**2. Operator-only checks the agent could not run.**
   a. **UptimeRobot — now required, not optional.** GitHub has delivered **one** scheduled probe run
      in five hours against a 10-minute cron, so the Actions probe alone is not enough cover for the
      09-07 11:00 → 09-11 23:59 KST 결격 window. Create it in the UI: HTTP(S) **keyword** monitor ·
      `https://jujutower.com/api/health` · keyword `"status":"ok"` · **5 min** · alert contact = your
      own address.
   b. **Confirm two mails actually arrived** at your alert address: the password-reset mail sent
      2026-09-02 11:29 KST, and the probe alert `[jujutower] PRODUCTION PROBE FAILED — health` from
      `주주의관제탑 <hi@hi2vi.com>` (run 33592665185 — its URL was the drill's deliberate
      `…/api/nope`; production was never touched). A send is not a receipt.
   c. **Commit your edge repo.** `~/projects/personal/edge/` still holds three uncommitted edits
      applied by `P4.S4`: `edge/conf.d/jujutower.conf`, and the `CERT_NAMES` / `[2/6]`-`[4/6]`
      changes in `validate.sh` / `stage.sh`. They are live on the box; only the repo is behind.
   d. **The five 첨부2 §5 account blocks (A1–A5), in one pass** — the agent may not create an account
      on production. Sign up at `https://jujutower.com/auth/login → 계정 만들기` (8자 이상, no
      verification mail) · open **툴젠** and 담기 · check 알림 설정 (7일 전 default, add 1일 전;
      KakaoTalk shows 「예정」 with no control) · request a password reset and read the mail
      (subject 「[주주의관제탑] 비밀번호 재설정」).
   e. **The D-day mail demo — the one product surface a browser cannot show.** With that account
      holding **툴젠 `00547510`** (신주인수권증서 매매 마감 **2026-09-07**, today **D-5**) and the 7일
      chip set, run on the box in `/home/opc/Mijual`:
      `docker compose -f compose.prod.yml exec mijual-worker python -m mijual.scheduler once --stages notify --no-lock --label gate-demo --notify-today 20260831`
      → one mail. Run it again identically → it must report **`already-sent`**.
   f. **`/ops` 개요, logged in** (the agent was denied the credential; read it on the box with
      `grep '^MIJUAL_OPS_' /home/opc/Mijual/.env.prod`, id `operator`): confirm the 개요 tab lists
      **four** beat entries including `notify-deadlines 08:30`, and look at 최근 실행 — see 3g.
   g. **One click the agent could not make:** log in on a browser that has already opened
      `/portfolio?sample=1`, and confirm the **계정 이전** offer lists *today's* sample rows.

**3. Decisions to take, literally. Every string is in `phase.md` § `## Operator Questions`.**
   a. **The mail copy** (entry 「THE MAIL COPY…」, items 1–6) — subject template
      `[주주의관제탑] {종목} — {마감명} {D-표기} ({date})` · the ① body verbatim · the ② body · the
      password-reset mail · `SMTP_FROM` display name `주주의관제탑 <hi@hi2vi.com>` (this also settles
      the sender-brand question) · **item 6 is a real doubt**: the fact block labels every type
      `마감:` but ②'s countdown is 전환청구 **개시** — keep one label, or vary it per type? Accept or
      change each.
   b. **The meta copy and the share card** (entry 「THE META COPY…」, items 1–8) — the site
      description · the `%s | 주주의관제탑` title template · the three static titles · the
      `/stocks/{corp}` pattern (툴젠 example) · the `/events/{rcept}` pattern (two examples) · the four
      `noindex` titles · the manifest · **item 8, the share card**: open
      `https://jujutower.com/opengraph-image.png` and *look* at it — the white wordmark on cosmos
      paper, no tagline. Rejecting it is one file and one command.
   c. **The `/ops` door** now shows 마크 + 운영자 ID + 비밀번호 + 로그인 and nothing else (D15).
      Accept, or reverse — reversing is one `git revert`.
   d. **The sample portfolio picks its four companies live, per request** — R5-4's 「구성 (고정)」 is
      superseded on your own 2026-09-02 instruction. Accept, or reverse to the fixed tuple.
      *(Expect different company names than any document prints; assert the four **states**.)*
   e. **The 심사용 테스트 계정**: leave 첨부2 §5.1's self-signup as the only path (no shared credential
      in a submitted document), or make one production account whose id/password goes literally into
      §5.1's second bullet. The second choice also unblocks 2e.
   f. **첨부2 §5's shape**: each block states the observable **state** first and then a dated
      2026-09-02 example, under one standing warning. Accept, or pin differently. (Prose, not code.)
   g. **The production `/ops` run log** opens on 21 dev-era rows — including `transport smtp
      127.0.0.1:8025`, the local test sink — plus 21 `probe-anchor` rows from the D-day hunt. Honest
      history a judge would see. Leave it, or truncate `pipeline_run` to the box's own runs?
   h. **Naver Search Advisor** — register or not? Google is already covered by a DNS-TXT property.
      Naver needs an HTML `<meta>`; the build arg exists and is empty, and filling it is a
      **rebuild**, not a restart (so before 09-07 11:00 KST, or after the freeze).
   i. **The two drafts' body language.** 첨부2 is English throughout; 첨부1's §2 요약, most of §5 and
      all of §7 are Korean, while both notes declare 「English body」. Leave it, bring 첨부1 into
      English, or relax the rule in both notes.
   j. **`구성원 성명`** — both drafts carry `〈제출자 직접 기재〉 — 개인(1인) 참가`. Fill it before either
      PDF is treated as final.
   k. **Cloudflare SSL/TLS mode** — one look at the dashboard: it must be **Full (Strict)**, per
      runbook R5. (Do it in the same visit as step 1.)
   l. **The footer publishes your personal e-mail and phone on every public page**, and the site is
      now indexable. Deliberate since R8/`P11.F2` — worth one conscious re-confirmation now.

**4. Deferred jobs the orchestrator will file** (title · reason · trigger): **A** the 정정 해석
thinking preset · **B** public-repo hardening (box IP/user/paths in `deploy/**`, your address in
`works/**`) · **C** the harness's production ssh/credential boundary · **D** this Mac's MagicDNS
answer for `www.jujutower.com`. Full text in *Stage C-5* above.

**5. How this closes.** Answer step 1 and the step-3 decisions to the orchestrator. It creates
`P4.F2` and `P4.F3` (both docs/config-only — **land them before 2026-09-07 11:00 KST**, or after
09-11 23:59 KST, though neither needs a deploy), re-runs the review, and only then runs
`accept-gate P4 --open`. You clear it with
`python3 scripts/workflow.py accept-gate P4 --clear --note "..."`, or report failures in your reply.

---

## Deviations from `plan.md`

1. **The dev runtime is not the operator's stack.** The plan opens with
   `make stack-down && make stack-up` because the API on 8010 is stale. **`make stack-down` was
   denied by the harness** (twice, in two forms), and killing the operator's processes by hand is
   the same act, so I did not. I confirmed the staleness rather than assuming it —
   `127.0.0.1:8010/portfolio/sample` still served the pre-`P4.F1` fixed tuple (계양전기 · 대동기어 ·
   한화솔루션 · 세기상사) with **1 upcoming ② D-52 and no ① at all**, which is exactly the failure
   `P4.F1` fixed. So I built the three runtimes **additively**, touching nothing of the operator's:
   a current-code API on `127.0.0.1:8011` against the same dev Postgres, a `next dev` on
   `127.0.0.1:3022` and a standalone **production** build on `127.0.0.1:3021` (the container's own
   entrypoint, not `next start`), both from APFS clones in the session scratchpad. All three were
   stopped at the end; the operator's stack is up and healthy, untouched, on its original pids.
2. **`docker compose -f compose.prod.yml config -q` needed an env file.** The compose file's
   services declare `env_file: .env.prod`, which does not exist off-box, so the plan's bare form
   cannot run here. I symlinked `.env.prod → .env.prod.example`, ran the check (**clean**), and
   removed the symlink; `git status` is unchanged and `.env.prod` does not exist.
3. **Three harness denials, none worked around** (all recorded, per the plan): `make stack-down`;
   `ssh oracle-cloud "docker compose -f … ps"` in three forms (while plain `docker ps`,
   `docker inspect`, `docker logs`, `crontab -l`, `ls`, `date` were all allowed); and the
   `grep '^MIJUAL_OPS_' /home/opc/Mijual/.env.prod` credential read, which cost the `/ops` 개요
   check — routed to the walkthrough as 2f. This is the same unstable boundary `P4.S4` recorded, and
   it is deferred job **C**.
4. **`extract recheck` / `evalset refresh-recall` were not re-run** — both write to the operator's
   dev database and a read-only review should not. The `--offline` pipeline covers the same
   idempotence read-only (`extract [dry-run] … 0 live call(s)`, `reparse 69/69, 0 with changed
   facts`). Recorded as line 3 of the not-clean-pass table rather than claimed.

## Instrument, budget, machine state

- **Instrument:** real **Google Chrome 152** over the DevTools protocol, **headful**, launched with
  `open -na "Google Chrome" --args --remote-debugging-port=9477 --user-data-dir=<scratchpad>` on a
  throwaway profile — never the operator's. Confirmed headful before use. **Aside was not used:** it
  is unavailable on this Mac (daemon down, no agent account) and the manifest names Chrome, so this
  is the sanctioned fallback, not a substitution. Viewports 1280 and 390 (`mobile: true`), plus
  1512 / 1440 / 768 / 767 / 481 for the mono guard.
- **Model calls: 6 total — 1 of 1 on production** (「툴젠 신주인수권증서 매매 마감 언제야?」) **and 5 of 8
  on the dev stack** (안녕 · 범위 밖 · 뷰노 유상증자 · 주입 시도 · 아이에이 배정 신주). No turn was run
  twice; the citation, footer, popover and paragraph lines were read off threads that already
  existed.
- **Production was read only.** HTTPS GETs, one `POST /api/ask`, and `ssh` inspection
  (`docker ps` / `inspect` / `logs` / `crontab -l` / `ls` / `date`). Nothing was deployed, rebuilt,
  restarted, recreated or stopped; `edge-nginx` was not touched and its `StartedAt` is unchanged;
  nothing under `/home/opc` was written; no account was created; no `psql` was run; no reader row
  was read. The only production writes are the one conversation row the single `/ask` turn creates
  and the localStorage of a throwaway browser profile.
- **Machine left as found.** The operator's dev stack is **up** — web pid 47136 on `:3010`
  (`200`), api pid 60158 on `:8010` (`{"status":"ok"}`) — on their original pids. My API 8011, web
  3021 and web 3022 are stopped, the throwaway Chrome on 9477 is closed, and nothing but
  `result.md` and `phase.md` changed in the tree.
