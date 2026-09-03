# P4.REVIEW — re-review of P4 "Ship & Deploy" (gated: `acceptance.required: true`) — dispatch 3, from the top

You are `slice-executor-high` executing the phase review **a third time**. Dispatch 1 (2026-09-02)
returned `changes_requested`; dispatch 2 (2026-09-03 morning) returned **`pass`** and the gate was
opened with its walkthrough; the operator answered walkthrough item **3n** (the landing starfield:
「find best way to reduce starfield cost. same effect only reduce the cost.」, then 「both do as your
recommendations. cost saving first.」, then for mobile 「just remove the orbit … not only the star
but the orbit itself also」), which the orchestrator recorded as an operator-reported
`changes_requested`; `P4.F7`, `P4.F11` and their release `P4.S10` landed. **This is again a full
review, not a delta**: production changed (`4aa8ddd` → `a74c58a`), the landing's hero is different
on mobile by operator decision, and the star twinkle is driven differently. Where dispatch 2 or a
later slice measured something on a surface that did not change and tagged it for you, you may
**cite instead of re-derive** — the notes say which — but the gate stages are yours to walk again.

The contract is `.claude/skills/review-phase/SKILL.md` — read it first and follow it to the letter;
this plan adds the P4-specific facts, order, budgets and hard rules. You are not the last word: on a
`pass` you return a **`walkthrough`** and the orchestrator opens the operator acceptance gate. You
never run `accept-gate`, `defer-job`, `review-phase`, `docs-consolidated`, `git commit` or `git push`.

## What P4 set out to do (judge against this)

`works/phases/active/P4/intent.md`, confirmed 2026-09-02: (1) both 양식 filled, English body, Korean
headings verbatim, **not submitted**; (2) production deploy to the operator's Oracle box behind the
shared `edge-nginx` and Cloudflare at `jujutower.com`, **additive only**; (3) SEO; (4) the D-day
notification e-mail from `hi@hi2vi.com`; (5) production smoke + uptime monitoring alerting the
operator by e-mail — **amended by the operator 2026-09-02**: 「drop uptime bot and system up checker.
just fine if it works now」, so the monitoring half is satisfied by `make smoke-prod` and the GitHub
Actions probe as they are, and no monitor is a finding; (6) new Korean copy approved **literally** at
the gate. Out of scope: the submission itself, the demo video, the deck. Added by operator
instruction during the phase: the relaxed extract ceiling (`P4.F4`) and the Core Web Vitals work
(`P4.R1` → the fixes → `P4.S9`).

Twenty-one slices are `done`: `P4.DECOMP`, `P4.S7`, `P4.S1`–`P4.S6`, `P4.F1`, `P4.S8`, `P4.F3`,
`P4.F2`, `P4.F4`, `P4.R1`, `P4.F5`, `P4.F6`, `P4.F8`, `P4.F10`, `P4.S9`, `P4.F7`, `P4.F11`, `P4.S10`.
`P4.F9` (landing TTFB) was never cut and waits on walkthrough item 3o. Production runs
`origin/main` = **`a74c58a`** (released by `P4.S10` on 2026-09-03 evening — its `result.md` has the
exact time, the image table and the rollback point). Today is 2026-09-03 (KST).

## Read (in this order, just in time)

1. `CLAUDE.md`; `.claude/skills/review-phase/SKILL.md`.
2. `python3 scripts/workflow.py next`; `works/phases/active/P4/phase.json` (the `acceptance` block —
   still `required: true`, never opened).
3. `works/phases/active/P4/intent.md`; `works/phases/active/P4/phase.md` **whole** — ~1,470 lines:
   `## Decisions` (many corrected in place since the first dispatch), `## Doc impact` (append-only,
   now long), `## Operator Questions` (**28 entries**; several marked ANSWERED AND DONE), `## Notes
   for later slices` (every block tagged `for P4.REVIEW` or `for the passing re-review` was written
   for you — `P4.F5`, `P4.F10`, `P4.F8`, `P4.S9`, the first review, `P4.F2`, `P4.F4`), `## Now`.
4. **Your own dispatch 2**: `slices/P4.REVIEW/result.md` (761 lines; dispatch 1 trimmed at its tail) — the Stage A–C tables,
   the 23 not-clean checklist lines and why, the routing table, the `## Walkthrough` (15 decisions
   3a–3p, six operator-only checks 2a–2f). Reuse what still holds; re-measure what the product
   changed. **Before you overwrite it**, move what you still cite under a trailing `## Earlier
   dispatches` heading, trimmed — the new verdict block goes first.
5. Every slice's `slice.json` and `result.md`, **head-first** (verdict block), whole where the detail
   matters. The three since dispatch 2 — `P4.F7`, `P4.F11`, `P4.S10` — are the ones you have not
   judged yet; the eighteen earlier ones you judged and re-validate.
6. `docs/current/operations.md` `## Operator Runtime` (now **v0014**, carrying the production
   runtime — written by dispatch 2); `docs/current/qa.md` `## Regression Checklist` (now **v0016**:
   144 `- [ ]` lines including the P4 production block dispatch 2 appended) — read it whole, you
   re-run all of it. Other `docs/current/`
   sections **only** where a `## Doc impact` line names them, and only to judge. Every doc P4
   touched is behind the code **by design** (the deferral to a docs phase), not a defect.
7. The two 양식 drafts and their PDFs (`docs/reference/challenge/submission/drafts/`), and
   `docs/reference/challenge/submission/README.md` for the heading structure. `02_기능명세서.md` §4
   was amended by `P4.F2` (the analytics beacon exception) and its PDF re-rendered (16 pages).

## Hard rules (all of them, no exceptions)

- **Production no-harm.** You may **read** production: HTTPS GETs against `https://jujutower.com`,
  `ssh oracle-cloud` for read-only inspection (`docker compose -f compose.prod.yml ps/logs`,
  `docker inspect`, `crontab -l`, `ls`), and at most **one** `POST /api/ask` turn (one model call).
  You may **not**: deploy, rebuild, restart, recreate or stop any container; touch `edge-nginx` in
  any way (baseline `StartedAt 2026-07-02T19:22:12.325478595Z` — assert it, never change it); edit
  anything under `/home/opc`; create an account on production; log in anywhere on production with
  a reader account; run `psql` or any write against the production database; read reader account
  rows. **`/ops` login on production:** the credential lives in `/home/opc/Mijual/.env.prod`
  (`MIJUAL_OPS_*`, read into a shell variable over ssh, never printed); an earlier dispatch was
  denied that read and `P4.F4` chose not to log in because a login mints an `OpsSession` row. Try
  once; if denied or you judge the row not worth minting, the `/ops` 개요 check is an
  **operator-only walkthrough item** (it already was) — record which. If the harness denies
  anything else, record it and do not work around it. Long remote commands run via `nohup … > log
  &` and polling, never a foreground ssh that a 120 s timeout can kill.
- **Deploy freeze** 2026-09-07 11:00 → 09-11 23:59 KST. Nothing in this slice deploys. A fix slice
  you propose that changes product code must say it needs a deploy before 09-07 11:00 KST or waits
  for 09-12 — there is room: `P4.S9` landed four days early.
- **Secrets.** Never print, quote or store a secret value: not `.env.prod` values, not the `/ops`
  password, not repository secrets, not SMTP credentials, not the Cloudflare token (`P4.R1` reads
  it by path from `../changple5/.dev.env` — you do not need it). The repo `leetusik/Mijual` is
  **public**: `result.md`, `phase.md`, the walkthrough and the two doc sections are published the
  moment they are committed. The walkthrough names **where** a credential is, never what it is.
- **Browser instrument.** Aside is unavailable on this Mac; the manifest names Chrome desktop and no
  Aside, so this is the sanctioned fallback, not a halt. Use **real Google Chrome over the DevTools
  protocol, headful**: `open -na "Google Chrome" --args --remote-debugging-port=<p>
  --user-data-dir=<throwaway dir in the session scratchpad>` (a `nohup` launch yields headless and
  does not count; ports 9223, 9331, 9333, 9351, 9360, 9391, 9445, 9451 were used by earlier
  sessions — pick a fresh one and confirm with `curl -s 127.0.0.1:<p>/json/version`). **Never**
  the operator's Chrome profile. Viewports **1280** and **390** (`Emulation.setDeviceMetricsOverride`,
  mobile true at 390), plus any width a checklist line names explicitly (1512/1440/1119/768/767/481).
  Say in `result.md` which instrument you used; never report a walk you did not make. Close every
  browser you open (a stale headless Chrome from a previous review was found still running by a
  later slice — do not leave one).
- **Model-call budget.** Checklist lines on the AI 질문 surface need real turns. Cap: **8** turns on
  the dev stack, **1** on production. Prefer the cheap greeting/범위 밖 lines and reuse one answered
  thread for the citation/footer/paragraph lines. State the count spent.
- **No source code edits, no fixes, no `docs/current` hand-edits, no `docs/versions` patches.** The
  only files you write: `result.md`, `phase.md`, and — on a pass only — the two named sections via
  `doc-new-version`. Notebook-only findings are the one thing you may close yourself (Stage B).
- **`uv` discipline.** `uv run pytest`, `python3 scripts/…`; never `uv run --with …`.

## Runtime: three environments, and what runs where

`## Operator Runtime` in `docs/current/operations.md` records only the **dev** runtime (`make
stack-up` → API `127.0.0.1:8010` + `next dev` on `127.0.0.1:3010`, Chrome desktop, mobile by
emulation, production build on the same port). `P4.S4`'s Doc impact line adds the **production**
runtime (`https://jujutower.com`, Cloudflare → `edge-nginx` → `mijual-web`, standalone build,
1280/390, real Chrome over CDP). The manifest is present and filled → no `needs_operator`.

| environment | how | what runs there |
|---|---|---|
| **dev** | the operator's stack on 3010/8010. **It is still stale** (the API on 8010 was started 2026-09-01 and serves the pre-`P4.F1` fixed sample 계양전기/대동기어/…; the orchestrator confirmed it minutes before this dispatch). First try `make stack-down && make stack-up` and confirm `curl -s 127.0.0.1:8010/portfolio/sample` shows a state-picked composition. **If the harness denies the restart** (it did on 2026-09-02): do not fight it — start an **additive** API on `127.0.0.1:8011` from the current tree against the same dev database (an earlier slice did exactly this; `uv run python -m mijual.web` with the port the Makefile uses, `nohup` + log + pid in the scratchpad) and a `next dev` **or** the production build on **3014** with `MIJUAL_API_ORIGIN=http://127.0.0.1:8011`, record the deviation, and leave the operator's 3010/8010 untouched. | **every** checklist line, including account-bound ones — one throwaway reader account on the **dev** database (create through `POST /auth/signup`, delete through `DELETE /auth/account` at the end, as `P4.F10` did), delete nothing of the operator's. |
| **production build** on 3014 | a **copy** of `frontend/` (never build into `frontend/.next`), `NEXT_PUBLIC_SITE_URL=https://jujutower.com npm run build`, served by `node .next/standalone/server.js` with `.next/static` and `public/` staged in (Next 16 refuses `next start` under `output: "standalone"`), against the dev API. `P4.R1`/`P4.F5`/`P4.F6`/`P4.F8`/`P4.F10`'s `result.md` each describe the recipe. | every line that could differ between dev and production (hydration, StrictMode double effects, caching, the two width lines `/stocks` 620 / `/stocks/{corp}` 960, `not-found`, the sample store, and the four CWV fixes' local proofs if you want them first-hand). |
| **production** `https://jujutower.com` | read-only, one model call max, no account, no login. | every anonymous/read-only line + this phase's headline claims (Stage C). Account-bound lines → 「운영자 검증 항목」 in the walkthrough, never silently skipped. |

Leave the machine as you found it: the operator's dev stack **up**, every server you started
stopped (pids recorded), the throwaway Chrome closed.

## Stage A — validate all slices together

Re-run each slice's validation from its verdict block (`plan.md` as fallback), collapsed into one
run of each; record every command and its outcome in `result.md`:

- `uv run pytest -q` → **167** expected (`P4.F4` added one). `uv lock --check` clean;
  `python3 -c "import mijual.web.__main__"` importable; `python3 -m mijual.scheduler once --help`
  shows the `--max-calls` default wording (env → 60); `MIJUAL_EXTRACT_MAX_CALLS=300 python3 -m
  mijual.scheduler once --offline --stages extract --window 14 --label review-proof --no-run-log
  --no-lock` prints `extract<=300 calls`.
- `cd <frontend copy> && npm run build && npm run typecheck && npm run smoke` green (22/22). The
  build needs `NEXT_PUBLIC_SITE_URL` (it throws at module load without it — `P4.S5`'s assertion).
- `make smoke-prod` → **17/17**; the `third-party` line names the two allowed hosts
  (`dart.fss.or.kr`, `static.cloudflareinsights.com` — the operator's decision to keep analytics).
  The `www` line is **intermittent** from this Mac (MagicDNS; `P4.F4` saw it pass twice) — if it
  fails, re-check with `--resolve` as the earlier plan described and count it as a known local
  false FAIL, not a production failure. Any **other** red line is a finding.
- `docker compose -f compose.prod.yml config -q` locally; `bash -n` on the four deploy scripts.
- `P4.F3`: `grep -n 'open decision\|Ask; do not assume' deploy/runbook.md` → nothing in R7;
  `grep -rn '04:00 KST' deploy/` → nothing; R7 records the cron as 04:00 GMT = 13:00 KST.
- `P4.F8`: the README verify block re-derives `juju2-wordmark-white-273-73c23508.png` to `AE 0`
  and the same sha256 (`magick` is at `/opt/homebrew/bin/magick`).
- The 양식 drafts: the five/seven `##` headings byte-identical to `README.md`'s extraction, in
  order; `grep -ci` of 미주알 / mijual / 파인튜닝 / fine-tun / PyTorch / Hugging Face → 0 in both
  `.md` files; the PDFs open (page counts 14 and 16); `구성원 성명` cells carry the placeholder;
  `02_기능명세서.md` §4 states the analytics beacon exception (the property no longer reads 「no
  third-party origin」 unqualified).
- `python3 scripts/workflow.py validate` (the `oversized_doc_sections` warning is pre-existing).
- On the box (read-only): six services up + `mijual-schema` exited 0; `edge-nginx` `StartedAt`
  unchanged; `/home/opc/Mijual` at `a74c58a`; `docker compose -f compose.prod.yml exec -T
  mijual-worker printenv MIJUAL_EXTRACT_MAX_CALLS` → 300; `crontab -l` carries the `0 4 * * *`
  backup line; `deploy/backups/` holds a dump younger than 24 h (mode 600); the API log announces
  `mail transport: smtp mail.privateemail.com:587 tls=starttls`; the worker log shows the 07:30
  morning, the 08:30 notify and the 19:30 evening runs of 2026-09-03 completing, and `P4.S10`
  launched the deploy only after the evening run (its log has the times).
- GitHub: `gh secret list -R leetusik/Mijual` shows the five names (never values); the probe
  workflow's latest scheduled runs (`gh run list -w production-probe.yml -L 5`) — report their
  state; a red one is a finding only if it is red for a product reason (the operator dropped
  further monitoring, not this workflow).

## Stage B — judgment, cross-check, doc-impact coverage

- Did every slice meet its brief and plan? Are deviations explained in each `result.md`? The eight
  new ones are judged for the first time; pay attention to `P4.F4`'s deliberate convention
  departure (a malformed ceiling is fatal — recorded as a decision, argue against it only with the
  trade-off), `P4.F6`'s smaller-than-estimated gain (reported honestly, the R1 note corrected in
  place), `P4.F8`'s one-device-pixel footer edge at DPR 2/3 (deviation 7 — is it acceptable under
  RESPECT THE DESIGN? say so either way), `P4.F10`'s account created and deleted on **dev**; and the three newest: `P4.F7` (the stars were
  already composited; candidate A rejected on total CPU; the canvas refused), `P4.F11` (the orbiter as
  93 generated arc-length `transform` stops — 32 of 261 sampled instants exceed the plan's 0.25 px, max
  0.41 px, attributed to `offset-distance`'s own progress wobble: judge whether that is acceptable
  under RESPECT THE DESIGN on a 5 px dot and say so; the **whole orbit block removed at ≤767px by
  operator instruction**, recorded verbatim in `## Decisions` — an operator-decided design change, not
  a finding; the `StarTwinkle.tsx` client component and its rendered-stars-only rule; declarative
  shadow DOM refuted by measurement), `P4.S10` (the release, timed after the 19:30 run; the
  production idle-cost numbers).
- **Cross-check the notebook against the logs**: a decision or constraint recorded in any
  `result.md` that appears nowhere in `phase.md` is a finding; so is a durable-truth change a log
  describes that has no `## Doc impact` line. Candidates to check explicitly, on top of the first
  dispatch's list: `MIJUAL_EXTRACT_MAX_CALLS` (operations + backend lines), the `.env.prod`-edit-
  recreates-postgres fact and the web/api `:previous` no-op asymmetry (operations), the fallback
  faces and Chrome's `local()` full-name rule (frontend), the landing projection (frontend), the
  public/ cache headers and the immutable-name rule (frontend + operations), the event page's
  request-time session read and the one-bit rule (frontend + security), how to read this site's
  Cloudflare RUM (operations), the production CWV baseline (qa), the P10 wordmark checklist line
  now false (qa), the analytics beacon allowance (security + qa), the backup cron's GMT firing time,
  the orbit keyframe generator as provenance and its regenerate-never-hand-edit rule (frontend), the
  WAAPI handover and why CSS must keep painting first paint (frontend), the **mobile hero without the
  orbit** (frontend — a signed-design departure by operator decision that the docs phase must carry),
  the landing's new idle-cost baseline (qa).
- **Notebook-only findings you close yourself** (append to `phase.md`, tag `(P4.REVIEW)`, report as
  closed). Product/code/deploy/draft findings become numbered findings with a proposed fix slice
  (`P4.F11`, …) and `changes_requested`.
- Orphaned design routes: confirm none (`app/**/mock*`).
- The **28 `## Operator Questions`** — build the routing table (Stage D consumes it): each entry is
  **walkthrough decision** / **deferred job (title / reason / trigger)** / **answered — nothing
  outstanding**. Already filed by the orchestrator, so cite rather than re-propose: **D40** (정정
  해석 thinking preset), **D41** (public-repo hardening), **D42** (harness production boundary),
  **D43** (MagicDNS www), **D44** (the 60 s whole-board poll), **D45** (Malgun Gothic's
  Hangul advance for the Windows fallback). Answered by the operator and out of
  the walkthrough: analytics **KEEP**, UptimeRobot **dropped**, the backup cron (installed), www
  (yes), D23 (re-signed), corpus seed, the ssh permission entry. New since the first dispatch and
  yours to route: the accepted extract cost (≈ $3.5 bound per full run, measured $0.0115/call —
  walkthrough, one line to accept), D40's fired trigger (keep deferred, or fold into the same
  line), the **starfield CPU** decision (**answered** — `P4.F7`/`P4.F11` shipped and both `P4.F7`
  questions are marked answered; only the confirmation at the gate remains),
  the **landing TTFB** decision (walkthrough, recommend-defer; `P4.F9`), and the Windows Malgun
  fallback width (deferred job candidate — list it for the orchestrator).

## Stage C — gate stages 1–4 (the phase is gated)

1. **Manifest** — present and filled. No halt.
2. **Spot-check the headline claims yourself** on `https://jujutower.com`, 1280 and 390 — the first
   dispatch's list stands (board + title, 툴젠 `00547510`, `/events/20260806000329`, the 404 echo,
   `/ask` one incremental streaming turn, `/portfolio?sample=1`'s four states with edits surviving
   reload, `/robots.txt`/`/sitemap.xml`/`/manifest.webmanifest`/`/opengraph-image.png`, the
   `noindex` five, `http://` and `www` 301s, the footer contact links) **plus this phase's later
   claims**: the served CSS carries the three `notoSansKr Fallback` faces and no `local(Arial)`;
   the landing HTML has `window_state` 0 times and is ≈ 290 KB; the chrome loads
   `juju2-wordmark-white-273-73c23508.png` (6,405 B, `immutable`) and `tokens.css` carries a
   week; an event page with a deadline ahead has 「이 마감 알림 받기 →」 **in the server HTML** and it
   is there at first paint; the off-origin host set on load is `static.cloudflareinsights.com` only
   (P4.S9 measured 16 loads — one route first-hand is enough); a cold-cache mobile load of `/` shows
   no visible re-wrap when the font lands (you need not re-measure CLS to four decimals — `P4.S9`
   did — but say what you saw); **the landing after `P4.F11`**: the served CSS has no
   `offset-distance` and carries the generated `@keyframes orbit`; at 1280 the star rides the ring at
   the same speed (one lap ≈ 26 s — time it); at 390 the hero shows **no orbit at all** (rings and
   star gone, the rest of the hero as before); the stars twinkle from first paint and keep
   twinkling after hydration with no visible step; one 8 s idle trace of your own at each viewport
   shows `compositeFailed` 0, `animationiteration` 0 and `UpdateLayoutTree` in the single digits
   per 8 s (`P4.S10` measured it on production — cite its numbers beside yours). `/ops`: the door (마크 + 운영자 ID + 비밀번호 + 로그인, `noindex`)
   from outside; the 개요 with four beat entries and the `f4-drain` run row only if you log in (see
   Hard rules). The staleness banner state at the time of your walk.
3. **Fresh-eyes walkthrough** as a first-time Korean reader on production at both viewports: land
   → search a company → open an event → read a `[근거]` → try the sample portfolio → ask one question
   (the one production model call — combine with stage 2) → sign-up page (do not submit) → 404.
   Report everything dead, confusing or annoying, **not** judged against the design record. These
   go into the walkthrough as decisions, never into fixes.
4. **Re-run the whole `## Regression Checklist`** — all 123 lines, per *Runtime* above; results as
   a table in `result.md` (line → dev / prod-build / production, one-word result, a note where not
   a clean pass; a line whose precondition no longer exists is recorded as such with what you
   checked instead). The first dispatch's 21 not-clean lines are listed in its result — re-check
   them, do not assume. The **P4 block already exists** in `qa` v0016 (dispatch 2 appended its 21
   lines, corrected the P10 wordmark line in place and moved the counts to 167 / 22) — re-run those
   21 lines too, they are part of the 144. Then compose the **two or three lines `P4.F11`/`P4.S10`**
   **earned**, in the same shape, to add to that block: the landing's idle trace (0 `compositeFailed`,
   0 `animationiteration`, `UpdateLayoutTree` ≤ ~30 per 8 s at 1280 and 390); the hero orbit present
   at 1280 on the generated keyframes and **absent at 390** with hero geometry unchanged; the twinkle
   painted from first paint and handed to WAAPI after hydration. Nothing else in the block changes.

## Stage D — route every operator question; build the walkthrough

Every one of the 28 entries lands in exactly one of: walkthrough decision / deferred job (new — the
orchestrator files it; or already filed — cite the D-id) / answered. Write the routing table into
`result.md`. Then write the **walkthrough** — the script the operator runs. Constraints: English
prose, Korean product strings verbatim; **≤ ~90 lines**; no secret values; numbered so the operator
can reply "1 ok, 4 change X". Start from **dispatch 2's** `## Walkthrough` (15 decisions 3a–3p,
operator-only checks 2a–2f) and edit: **3n is answered** — replace it with a one-line confirmation
item: at desktop the landing feels exactly as before (the star rides the ring, the field twinkles)
and the mobile hero now has **no orbit**, as the operator decided, with the measured result in one
line (main-thread frames 60/s → ~1/s; total Chrome CPU −25 % desktop / −7 % throttled mobile
locally, plus `P4.S10`'s production numbers). Keep 3o (landing TTFB, recommend-defer). Keep every
other item the operator has not answered **exactly as dispatch 2 worded it** — the only reply was
about 3n. Add anything Stage 3 surfaced on the changed landing. Update section 0 (what is already
verified) and section 4 (D45 is filed). Shape:

1. **Open** — the URLs and clicks, 1280 and a phone: board · 툴젠 · one event · `[근거]` · `/ask` one
   question · `/portfolio?sample=1` edit/reload · `/ops` login · robots/sitemap/share card · `http://`
   and `www` redirects · one `make smoke-prod` · a cold-cache mobile load of `/` (DevTools, disable
   cache, slow 4G) to see the font land without a re-wrap.
2. **Operator-only checks**: the five 첨부2 §5 account blocks A1–A5 in one pass (sign up → 담기
   툴젠 → 알림 설정 → reset mail → the D-day demo command on the box, second run `already-sent`);
   receipt of the two mails already sent; the 계정 이전 offer after visiting the sample; the F10
   signed-in line; Cloudflare SSL mode; the edge repo commit; `/ops` 개요.
3. **Decisions to take, literally** — the mail copy (six items by number), the meta copy + share
   card (nine items), D15, F1's supersession, 심사용 계정, the drafts' body language, 첨부2 §5's
   shape, the `/ops` run log rows, Naver, `구성원 성명`, the extract cost, the starfield, the TTFB.
   Each one line: what it is, where the exact strings are, accept/change.
4. **Deferred jobs** — those already filed (D40–D44, one line each) and any new ones the orchestrator
   will file (title · reason · trigger), so the operator sees them here too.
5. **How to clear**: `python3 scripts/workflow.py accept-gate P4 --clear --note "..."`, or report
   failures in the reply.

Put the walkthrough in `result.md` under a heading that is **exactly** `## Walkthrough`, followed
by a blank line, ending at the next `## ` heading (the orchestrator extracts it mechanically for
`accept-gate --open --walkthrough`). Also return it in the structured verdict.

## Pass-only writes (only after the verdict is settled as `pass`)

(a) Verify the `## Doc impact` list covers every durable-truth change (Stage B), and report
`doc_versions: none — deferred to a docs phase` for consolidation.
(b) The two named sections, each through the engine and nothing else in those docs:
- `python3 scripts/workflow.py doc-new-version --doc qa --summary "P4: the landing idle-cost lines join the P4 regression block" --source P4.REVIEW`
  → edit **only** `## Regression Checklist` in the returned `edit_path`: add the `P4.F11`/`P4.S10`
  lines to the existing P4 block (Stage C-4); nothing else in the section changes (the counts are
  already 167 / 22).
- `## Operator Runtime` in `operations` **v0014** was written by dispatch 2 and nothing about the
  runtime changed since; **do not write a second operations version** unless you find the section
  wrong — say in the return that it stands.
- `python3 scripts/workflow.py rebuild-docs`, then `python3 scripts/workflow.py validate`.
On `changes_requested` or `blocked`: **none of (a)/(b)** — stop and hand back.

## `phase.md` duties (every verdict)

Edit the notebook under its budget: consume (drop) the `## Notes for later slices` blocks tagged
`for P4.REVIEW` / `for the passing re-review` / `for P4.S9` whose content now lives in the
walkthrough or `result.md`; keep any note a docs phase will still need and retag it `for the docs
phase`; correct `## Now`'s stale line 「one deferred job still unfiled」 (the 60 s poll is **D44**);
append your Doc impact / Operator Questions lines only if you add any; never touch the generated
`## Slices` block; rewrite `## Now` (≤ 15 lines) as the handoff: the verdict, the gate state the
orchestrator is about to open, the operator's next action, the freeze date, and the docs-phase debt.

## Return

The structured verdict block, `result.md` first (verdict block at the head, then: validation
table, the per-line regression table, findings numbered, the routing table, `## Walkthrough`,
deviations, instrument used, model calls spent, machine state left, then the trimmed earlier
dispatch). `explain: not written — run /explain for this phase` on every verdict.

- `pass` → `walkthrough` filled; deferred jobs to file listed (title/reason/trigger) in the return
  **and** in `result.md`.
- `changes_requested` → numbered findings + proposed fix slices (`P4.F11`…), no pass-only step run,
  and say which findings force a deploy before the freeze.
- `blocked` → the blocker and the input needed. Do **not** use `blocked` for running out of room.

**Partial-return protocol.** If you cannot finish in this context, stop at a clean boundary: write
`result.md` with a `## Progress` section (what is validated with results, what remains, the exact
next step, the machine state you left — Chrome pid/port, which servers are up) and return
`status: done` with `review_verdict: n/a — partial, resume at <stage/step>`. The orchestrator
re-dispatches you from `## Progress`; the final dispatch rewrites the verdict block. Never form a
verdict from a partial picture.

## Addendum — state at dispatch 3 (orchestrator, 2026-09-03 evening)

- Production is **`a74c58a`**, released by `P4.S10` at **19:47 KST** after the evening pipeline
  (`daily-evening` succeeded 19:31:02). Rollback point: `mijual-web:previous` = `028b480a7b37`
  (the `4aa8ddd` image); the api tags are equal, so the pre-CWV image is reachable only through
  `REF=<sha> deploy/deploy.sh`. `P4.S10`'s production numbers, paired against a same-evening
  pre-deploy baseline (70 s idle on `/`): style recalculation **6.235 → 0.416 s** at 1280 and
  **5.021 → 0.153 s** at 390 + 4×; total Chrome CPU **−31 % / −6.5 %**; `UpdateLayoutTree` **480 →
  14 / 8** per 8 s; `animationiteration` and `compositeFailed` **0**; cold-cache CLS on `/` 0.0000 ×3;
  `make smoke-prod` 17/17. Cite them; run one trace and one look of your own.
- The next beat windows are 07:30 / 08:30 KST tomorrow — irrelevant to a read-only review.
- Time budget: the freeze opens 2026-09-07 11:00 KST; nothing here deploys, but if you return
  `changes_requested` with a code fix, say so in the finding.
