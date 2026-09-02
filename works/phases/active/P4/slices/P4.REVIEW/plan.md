# P4.REVIEW — phase review of P4 "Ship & Deploy" (gated: `acceptance.required: true`)

You are `slice-executor-high` executing the phase review. The contract is
`.claude/skills/review-phase/SKILL.md` — read it first and follow it to the letter; this plan adds
the P4-specific facts, order, budgets and hard rules. You are not the last word: on a `pass` you
return a **`walkthrough`** and the orchestrator opens the operator acceptance gate. You never run
`accept-gate`, `defer-job`, `review-phase`, `docs-consolidated`, `git commit` or `git push`.

## What P4 set out to do (judge against this)

`works/phases/active/P4/intent.md`, confirmed 2026-09-02: (1) both 양식 filled, English body, Korean
headings verbatim, **not submitted**; (2) production deploy to the operator's Oracle box behind the
shared `edge-nginx` and Cloudflare at `jujutower.com`, **additive only**; (3) SEO; (4) the D-day
notification e-mail from `hi@hi2vi.com`; (5) production smoke + uptime monitoring alerting the
operator by e-mail; (6) new Korean copy (meta/OG, mail, the D15 door) drafted by the phase and
approved **literally** at the gate. Out of scope: the submission itself, the demo video, the deck.

Ten slices are `done`: `P4.DECOMP`, `P4.S7`, `P4.S1`, `P4.S2`, `P4.S3`, `P4.S4`, `P4.S5`, `P4.S6`,
`P4.F1`, `P4.S8`. Production runs `origin/main` = `96f7141` (the last deploy before the freeze); the
two later commits on `main` are workspace/docs only. Today is 2026-09-02 (KST).

## Read (in this order, just in time)

1. `CLAUDE.md`; `.claude/skills/review-phase/SKILL.md`.
2. `python3 scripts/workflow.py next`; `works/phases/active/P4/phase.json` (the `acceptance` block).
3. `works/phases/active/P4/intent.md`; `works/phases/active/P4/phase.md` **whole** — it is ~850
   lines: `## Decisions`, `## Doc impact` (append-only, ~40 lines), `## Operator Questions`
   (**22 entries**, several answered inline and marked DONE), `## Notes for later slices` (every
   block tagged `for P4.REVIEW` was written for you), `## Now`.
4. Every completed slice's `slice.json` and `result.md`, **head-first** (verdict block), whole where
   the detail matters: `slices/{P4.DECOMP,P4.S7,P4.S1,P4.S2,P4.S3,P4.S4,P4.S5,P4.S6,P4.F1,P4.S8}/`.
   `P4.S4`'s `result.md` carries three dispatches (the latest first, earlier ones under
   `## Earlier dispatches`); `P4.S6` and `P4.F1` carry two each.
5. `docs/current/operations.md` `## Operator Runtime` and `## Deployment`/production sections;
   `docs/current/qa.md` `## Regression Checklist` (123 `- [ ]` lines: 14 general, 58 P8, 18 P9,
   23 P10 across four blocks, 10 P11) — read it whole, you re-run all of it. Read other
   `docs/current/` sections **only** where a `## Doc impact` line names them, and only to judge.
   `python3 scripts/workflow.py docs` flags nothing STALE yet only because the P4 notes are not
   consolidated; every doc P4 touched is behind the code **by design** — that is the deferral, not
   a defect.
6. The two 양식 drafts: `docs/reference/challenge/submission/drafts/01_공모전기획서.md` and
   `02_기능명세서.md` (+ their PDFs), and the structure they must match:
   `docs/reference/challenge/submission/README.md`.

## Hard rules (all of them, no exceptions)

- **Production no-harm.** You may **read** production: HTTPS GETs against `https://jujutower.com`,
  `ssh oracle-cloud` for read-only inspection (`docker compose -f compose.prod.yml ps/logs`,
  `docker inspect`, `crontab -l`, `ls`), and at most **one** `POST /api/ask` turn (one model call).
  You may **not**: deploy, rebuild, restart, recreate or stop any container; touch `edge-nginx` in
  any way (baseline `StartedAt 2026-07-02T19:22:12.325478595Z` — assert it, never change it); edit
  anything under `/home/opc`; create an account on production; run `psql` or any write against the
  production database; read reader account rows. The harness denies the last three anyway; if it
  denies something else, record it and do not work around it. Long remote commands run via
  `nohup … > log &` and polling, never a foreground ssh that a 120 s timeout can kill.
- **Deploy freeze** 2026-09-07 11:00 → 09-11 23:59 KST. Nothing in this slice deploys. If you
  propose fix slices that change product code, say in the finding that they must be deployed before
  09-07 11:00 KST or wait until 09-12.
- **Secrets.** Never print, quote or store a secret value: not `.env.prod` values, not the `/ops`
  password (if you log in to `/ops`, read it into a shell variable with
  `grep '^MIJUAL_OPS_' /home/opc/Mijual/.env.prod` over ssh and pass it to the browser from that
  variable), not repository secrets, not SMTP credentials. The repo `leetusik/Mijual` is **public**:
  `result.md`, `phase.md`, the walkthrough and the two doc sections are published the moment they
  are committed. The walkthrough must name **where** a credential is, never what it is.
- **Browser instrument.** Aside is unavailable on this Mac (daemon down, no agent account) — the
  manifest names Chrome desktop and no Aside, so this is the sanctioned fallback, not a halt. Use
  **real Google Chrome over the DevTools protocol, headful**, launched with
  `open -na "Google Chrome" --args --remote-debugging-port=<p> --user-data-dir=<throwaway dir in
  the session scratchpad>` (a `nohup` launch yields headless and does not count; ports 9223, 9333,
  9445 and 9451 were used by earlier sessions — pick a fresh one and confirm with
  `curl -s 127.0.0.1:<p>/json/version`). **Never** the operator's Chrome profile. Viewports **1280**
  and **390** (`Emulation.setDeviceMetricsOverride`, mobile true at 390), plus any width a
  checklist line names explicitly (1512/1440/1119/768/767/481). Say in `result.md` which instrument
  you used; never report a walk you did not make.
- **Model-call budget.** Checklist lines on the AI 질문 surface need real turns. Cap: **8** turns on
  the dev stack, **1** on production. Prefer the cheap greeting/범위 밖 lines and reuse one answered
  thread for the citation/footer/paragraph lines. State the count spent.
- **No source code edits, no fixes, no `docs/current` hand-edits, no `docs/versions` patches.** The
  only files you write: `result.md`, `phase.md`, and — on a pass only — the two named sections via
  `doc-new-version` (see *Pass-only writes*). Notebook-only findings are the one thing you may close
  yourself (see *Stage B*).
- **`uv` discipline.** Run Python through the project's existing `.venv` (`uv run pytest`,
  `python3 scripts/…`); never `uv run --with …` — it re-syncs the venv and strips the operator's
  undeclared tools.

## Runtime: three environments, and what runs where

`## Operator Runtime` in `docs/current/operations.md` (v0013) records only the **dev** runtime:
`make stack-up` → API `127.0.0.1:8010` + `next dev` on `127.0.0.1:3010`, Chrome desktop on this
Mac, mobile by device emulation, production build `cd frontend && npm run build && npm run start`
on the **same** port 3010. `P4.S4`'s `## Doc impact` line adds the **production** runtime:
`https://jujutower.com` (www 301s), Cloudflare → `edge-nginx` → `mijual-web`, a standalone
production build, 1280/390, real Chrome over CDP. The manifest is present and filled → no
`needs_operator` on the runtime.

So the checklist runs in **three** places, and `result.md` records the result per line per place:

| environment | how | what runs there |
|---|---|---|
| **dev** `http://127.0.0.1:3010` | the operator's stack. **It is stale**: the API on 8010 was started 2026-09-01 03:14 KST and still serves the pre-`P4.F1` fixed sample (계양전기/대동기어/…). Before anything: `make stack-down && make stack-up`, then confirm `curl -s 127.0.0.1:8010/portfolio/sample` shows a state-picked composition (four distinct issuers, one upcoming ①). | **every** checklist line, including account-bound ones — create one throwaway reader account on the **dev** database (local, allowed), delete nothing of the operator's. |
| **production build** on 3010 | `make stack-down` (web only is fine if the Makefile allows; otherwise the whole stack, then restart the API half as the Makefile does), `cd frontend && npm run build && npm run start` against the same API/DB. | every line that could differ between dev and production (hydration, StrictMode double effects, caching, the two width lines `/stocks` 620 / `/stocks/{corp}` 960, `not-found`, the sample store). Use judgment — the qa doc names which lines were production-sensitive before. |
| **production** `https://jujutower.com` | read-only, one model call max, no account. | every anonymous/read-only line + this phase's headline claims (Stage C). Account-bound lines → 「운영자 검증 항목」 in the walkthrough, never silently skipped. |

Leave the machine as you found it: the operator's dev stack **up** (`make stack-up`) at the end,
the production-build server stopped, the throwaway Chrome closed (`kill` its pid; if `rm -rf` of
the throwaway profile is denied, leave it — it is disposable scratch).

## Stage A — validate all slices together

Re-run each slice's validation from its verdict block (`plan.md` as fallback). Collapse the
duplicates into one run of each; record every command and its outcome in `result.md`:

- `uv run pytest -q` → **165** expected (`P4.S2` 19 tables, `P4.F1` `tests/test_web_portfolio.py`).
- `uv lock --check` clean; `python3 -c "import mijual.web.__main__"` importable.
- `cd frontend && npm run build && npm run typecheck && npm run smoke` green (22/22 or more).
  The build needs `NEXT_PUBLIC_SITE_URL` (it throws at module load without it — that is `P4.S5`'s
  assertion, not a defect): export `NEXT_PUBLIC_SITE_URL=https://jujutower.com` for local builds.
- `make smoke-prod` → 17 checks. The `www` line **can fail from this Mac** because Tailscale
  MagicDNS resolves `www.jujutower.com` to non-Cloudflare addresses (an open `## Operator
  Questions` entry). If it fails with `SSL: UNEXPECTED_EOF`, re-check with
  `curl -sI --resolve www.jujutower.com:443:104.21.21.26 https://www.jujutower.com/x?y=1` → 301 to
  the apex with path+query preserved, and count the line as a known local false FAIL, not a
  production failure. Any **other** red line is a finding.
- `docker compose -f compose.prod.yml config -q` locally; `bash -n` on the four deploy scripts.
- The 양식 drafts: the five/seven `##` headings byte-identical to `README.md`'s extraction, in
  order; `grep -ci` of 미주알 / mijual / 파인튜닝 / fine-tun / PyTorch / Hugging Face → 0 in both
  `.md` files; the PDFs open (page counts 14 and 16); `구성원 성명` cells carry the placeholder.
- `python3 scripts/workflow.py validate` (the `oversized_doc_sections` warning is pre-existing).
- On the box (read-only): six services up + `mijual-schema` exited 0; `edge-nginx` `StartedAt`
  unchanged; `crontab -l` carries the `0 4 * * *` backup line; `deploy/backups/` holds ≥1 dump
  (mode 600); the API log announces `mail transport: smtp mail.privateemail.com:587 tls=starttls`.
- GitHub: `gh secret list -R leetusik/Mijual` shows the five names (never values); the probe
  workflow's latest scheduled runs are green (`gh run list -w production-probe.yml -L 5`).

## Stage B — judgment, cross-check, doc-impact coverage

- Did every slice meet its brief and plan? Are deviations explained in each `result.md`?
- **Cross-check the notebook against the logs**: a decision or constraint recorded in any
  `result.md` that appears nowhere in `phase.md` is a finding; so is a durable-truth change a log
  describes that has no `## Doc impact` line. Candidates to check explicitly (verify, do not
  assume): the Cloudflare ~100 s origin cap → 524 (a `P4.S4` note says `architecture.md` lacks it —
  is there a Doc impact line?); the SEO disallow-vs-noindex caveat; the `notify` stage's
  `notify_max_mails` ceiling; the seeded dev accounts kept on production; the `/ops` run log rows;
  `render_submission_pdf.py`; the freeze window; the probe's GitHub caveats; `SAMPLE_FALLBACK`'s
  move; the `NEXT_PUBLIC_SITE_URL` rebuild-not-restart rule; the agent's seven tools (filed by
  `P4.S8`); `## Operator Runtime` gaining the production runtime (filed by `P4.S4`).
- **Notebook-only findings you close yourself**: a missing `## Doc impact` line or a dropped
  decision is closed by appending it to `phase.md` (append-only sections; tag it `(P4.REVIEW)`),
  and reported in `result.md` as a finding you closed. A finding in **product, code, deploy or the
  drafts** is never closed by you — it becomes a numbered finding with a proposed fix slice
  (`P4.F2`, `P4.F3`, …, one line of scope each) and the verdict `changes_requested`.
- Orphaned design routes: P4 shipped none — confirm no `app/**/mock*` or design route exists.
- The **22 `## Operator Questions`** — build the routing table now (Stage D consumes it): for each
  entry, either **walkthrough decision** or **deferred job (title / reason / trigger)** or
  **answered — nothing outstanding** (the entries marked ANSWERED AND DONE; say so explicitly, an
  answered entry is still a routed one). Suggested routing, yours to overrule with a reason:
  - walkthrough decisions: mail sender brand (de facto `hi@hi2vi.com` — accept); the mail copy
    (six items incl. the `마감:` label doubt); the meta copy + share card (nine items incl. Naver);
    D15 door removal; F1's supersession of R5-4 「고정」; the 심사용 계정 choice; the drafts'
    body-language mismatch; 첨부2 §5 by-state-plus-dated-example shape; the `/ops` run log's
    seeded + `probe-anchor` rows; the staleness banner (verify yourself whether beat's 19:30 KST
    run cleared it — it still showed at 18:37 KST — and report the state you saw); Cloudflare SSL
    mode (one look); the D-day gate demo (holding on 툴젠 `00547510` → the `once --stages notify
    … --notify-today 20260831` run → second run `already-sent`); receipt of the reset mail
    (09-02 11:29 KST) and of the probe alert (`[jujutower] PRODUCTION PROBE FAILED — health`);
    the UptimeRobot keyword monitor; committing the edge repo's three uncommitted edits;
    `구성원 성명`.
  - deferred jobs: public-repo hardening (`deploy/**` publishes box IP/user/paths, `works/**` the
    alert address); the 정정 해석 thinking preset (D-4, undecided, first unattended worker); this
    Mac's MagicDNS `www` resolution (or fold into the walkthrough as "known local false FAIL" —
    your call, but it must land somewhere); the harness ssh/production-data boundary (a note for
    the operator's settings, not a product job — walkthrough or defer, your call).
  - answered: D23 (re-signed, deferred job already closed), www alias, backup cron, corpus seed,
    the ssh permission entry (resolved for later dispatches; keep the boundary note).

## Stage C — gate stages 1–4 (the phase is gated)

1. **Manifest** — present and filled (see *Runtime*). No halt.
2. **Spot-check the headline claims yourself** on `https://jujutower.com`, 1280 and 390:
   - the board with real corpus data, the tab title `주주의관제탑`; a 종목 page (툴젠 `00547510`) with
     title `툴젠 | 주주의관제탑` and the drafted description in `<head>`, self-canonical, `og:image`;
     an 이벤트 page (`/events/20260806000329`) likewise; `/events/00000000000000` → 404 not 500;
   - `/ask`: **one** turn, streaming **incrementally** (count DOM states / SSE frames over time;
     `P4.S4` measured 5–9 distinct states over ~7 s — assert incremental, do not re-derive);
   - `/portfolio?sample=1`: four distinct issuers, one upcoming ① with a live D-day, an ②, the ①
     소멸 with 놓친 돈, the ③; edit a 보유량 → reload → persists; remove → reload → hidden;
   - `/ops`: the door is 마크 + 운영자 ID + 비밀번호 + 로그인 and nothing else, `noindex`; log in
     (credential via ssh into a variable) → 개요 shows **four** beat entries incl.
     `notify-deadlines 08:30`; note whether `notify-deadlines` has a run yet and what the run log
     opens on; log out;
   - `/robots.txt` (Cloudflare's block **then** the origin's rules + `Sitemap:`), `/sitemap.xml`
     (800 `<loc>` on the apex, none of `/ops`,`/auth`,`/portfolio`), `/manifest.webmanifest`,
     `/opengraph-image.png` 1200×630 — **look at the share card**; view-source `/auth/login`,
     `/portfolio` → `noindex, nofollow`;
   - `http://jujutower.com/` and `https://www.jujutower.com/x?y=1` → 301 to the apex (use
     `--resolve` for www if this Mac's resolver misbehaves);
   - the footer's 운영자 연락처 `mailto:`/`tel:` on every reader page; no third-party `src`/`href`
     on the landing (grep the served HTML);
   - the staleness banner state at the time of your walk (after 19:30 KST it should be gone).
3. **Fresh-eyes walkthrough** as a first-time Korean reader on production at both viewports:
   land → search a company → open an event → read a `[근거]` → try the sample portfolio → ask one
   question (that is the one production model call — combine with stage 2) → sign-up page (do not
   submit) → 404. Report everything dead, confusing or annoying, **not** judged against the design
   record. These go into the walkthrough as decisions, never into fixes.
4. **Re-run the whole `## Regression Checklist`** — all 123 lines, per *Runtime* above; results as
   a table in `result.md` (line → dev / prod-build / production, with a one-word result and a note
   where it is not a clean pass). A line whose precondition no longer exists (a retired string, a
   corpus row that is gone) is recorded as such with what you checked instead — not as a pass.
   Then compose this phase's **P4 block** to append (shape `- [ ] <surface>: <one observable
   behaviour> (P4)`), built from the notes tagged `for P4.REVIEW`: `make smoke-prod` as the machine
   half (17/17, the `www` local caveat named), `/ask` streaming incrementally at 1280/390 through
   Cloudflare, the board/종목/이벤트 pages with real data, the `/ops` door + 개요 four beat entries,
   the footer links, www/http 301s, robots/sitemap/manifest/OG, title + description + canonical +
   `og:image` on indexable pages and `noindex` on the five others, bad `rcept_no` 404, the sample's
   four states with ≥1 upcoming ① and edits surviving reload, the D-day mail demo (`once --stages
   notify` → sent, second run `already-sent`), the four R7 no-harm assertions after a deploy
   (`edge-nginx` `StartedAt`, :80/:443 owner, container count, network members), a backup dump
   younger than 24 h on the box.

## Stage D — route every operator question; build the walkthrough

Every one of the 22 entries lands in exactly one of: walkthrough decision / deferred job / answered.
Write the routing table into `result.md`. Then write the **walkthrough** — the script the operator
runs. Constraints: English prose, Korean product strings verbatim; **≤ ~90 lines**; no secret
values; numbered so the operator can reply "1 ok, 4 change X". Shape:

1. **Open** — the URLs and clicks, 1280 and a phone (the operator's Chrome + device emulation):
   board · 툴젠 · one event · `[근거]` · `/ask` one question · `/portfolio?sample=1` edit/reload ·
   `/ops` login · robots/sitemap/share card · `http://` and `www` redirects · one `make smoke-prod`.
2. **Operator-only checks** (the agent could not): the five 첨부2 §5 account blocks A1–A5 in one
   pass (sign up → 담기 툴젠 → 알림 설정 → reset mail → the D-day demo command on the box, second run
   `already-sent`); receipt of the two mails already sent; the 계정 이전 offer after visiting the
   sample; UptimeRobot monitor creation; Cloudflare SSL mode; the edge repo commit.
3. **Decisions to take, literally** — the mail copy (point at the `## Operator Questions` entry;
   list the six items by number), the meta copy + share card (nine items), D15, F1's supersession,
   심사용 계정, the drafts' body language, 첨부2 §5's shape, the `/ops` run log rows, Naver,
   `구성원 성명`. Each one line: what it is, where the exact strings are, accept/change.
4. **Deferred jobs the orchestrator will file** (title · reason · trigger), so the operator sees
   them here too.
5. **How to clear**: `python3 scripts/workflow.py accept-gate P4 --clear --note "..."`, or report
   failures in the reply.

Put the walkthrough in `result.md` under a heading that is **exactly** `## Walkthrough`, followed
by a blank line, ending at the next `## ` heading (the orchestrator extracts it mechanically for
`accept-gate --open --walkthrough`). Also return it in the structured verdict.

## Pass-only writes (only after the verdict is settled as `pass`)

(a) Verify the `## Doc impact` list covers every durable-truth change (Stage B), and report
`doc_versions: none — deferred to a docs phase` for consolidation.
(b) The two named sections, each through the engine and nothing else in those docs:
- `python3 scripts/workflow.py doc-new-version --doc qa --summary "P4: production regression block appended" --source P4.REVIEW`
  → edit **only** `## Regression Checklist` in the returned `edit_path`: append the P4 block after
  the P11 block, in the shipped shape; update the two headline counts in the first line if they
  changed (pytest **165**, frontend smoke count as measured) — that line is inside the section.
- `python3 scripts/workflow.py doc-new-version --doc operations --summary "P4: the production runtime joins the Operator Runtime manifest" --source P4.REVIEW`
  → edit **only** `## Operator Runtime`: add the production runtime and access path from `P4.S4`'s
  Doc impact line (origin, Cloudflare → `edge-nginx` → `mijual-web`, standalone build released by
  `deploy/deploy.sh` from `/home/opc/Mijual`, logs command, where the `/ops` credential lives —
  by path, never value — the browser instrument fallback and why, viewports 1280/390, the freeze
  pointer to `deploy/runbook.md`). Keep the dev paragraphs as they are.
- `python3 scripts/workflow.py rebuild-docs`, then `python3 scripts/workflow.py validate`.
On `changes_requested` or `blocked`: **none of (a)/(b)** — stop and hand back.

## `phase.md` duties (every verdict)

Edit the notebook under its budget: consume (drop) the `## Notes for later slices` blocks tagged
`for P4.REVIEW` whose content now lives in the walkthrough or `result.md`; keep any note a docs
phase or fix slice will still need and retag it; append your Doc impact / Operator Questions lines
only if you add any (closed notebook findings go to `## Doc impact`); never touch the generated
`## Slices` block; rewrite `## Now` (≤ 15 lines) as the handoff: the verdict, the gate state the
orchestrator is about to open, the operator's next action, the freeze date, and the docs-phase debt.

## Return

The structured verdict block, `result.md` first (verdict block at the head, then: validation
table, the per-line regression table, findings numbered, the routing table, `## Walkthrough`,
deviations, instrument used, model calls spent, machine state left). `explain: not written — run
/explain for this phase` on every verdict.

- `pass` → `walkthrough` filled; deferred jobs listed (title/reason/trigger) in the return **and**
  in `result.md`.
- `changes_requested` → numbered findings + proposed fix slices (`P4.F2`…), no pass-only step run,
  and say which findings force a deploy inside/after the freeze.
- `blocked` → the blocker and the input needed. Do **not** use `blocked` for running out of room.

**Partial-return protocol.** If you cannot finish in this context, stop at a clean boundary: write
`result.md` with a `## Progress` section (what is validated with results, what remains, the exact
next step, the machine state you left — Chrome pid/port, which server is on 3010) and return
`status: done` with `review_verdict: n/a — partial, resume at <stage/step>`. The orchestrator
re-dispatches you from `## Progress`; the final dispatch rewrites the verdict block. Never form a
verdict from a partial picture.
