# P4.DECOMP — decompose "Ship & Deploy" under the revised operator intent

## Context

P4 is the last phase. It is `planned` and undecomposed: only `P4.DECOMP` and `P4.REVIEW` exist.
Its recorded intent (`works/phases/active/P4/intent.md`, captured 2026-08-19) is now **materially
wrong in five places**, and this session's operator answers replace it. That correction is the
first thing this slice's plan has to carry, because `P4.REVIEW` judges the phase against the
objective and `intent.md`.

What changed, and what the verified record says:

| `intent.md` says | Now |
|---|---|
| Deploy to `ssh h`, "a public demo URL" | Deploy to the **Oracle Cloud box**, nginx at the edge, **Cloudflare** in front, domain **`jujutower.com`** |
| Presentation deck (주최사별 효용 매핑, AI-role architecture, 소멸 총액 opening) | **Out.** The 발표자료 PDF is deliverable ③ — October 8, **finalists only** |
| Demo video | **Out.** The MVP form is `linkConfig = {demo: enabled+required, github: disabled, youtube: disabled}` — a demo **URL**, never a video |
| daker.ai submission | **Out — "no submit."** The phase prepares the documents and stops |
| Submission-facing materials in Korean | **English body, Korean section headings preserved verbatim** |
| (not mentioned) | **SEO setup required** |

Two items in `intent.md` survive unchanged: **email D-day notifications** (the last unbuilt
product feature — settings exist, nothing sends) and **production polish** (smoke tests, honest
incompleteness, operational checks).

Deadline context, not a binding constraint any more: the contest closes **2026-09-07 10:00 KST**
(5 days). Since the operator is not submitting through this phase, the two 결격-grade constraints
in `docs/current/operations.md` — the 09-07 11:00 → 09-11 23:59 unattended-uptime window and the
URL freeze — are **design inputs, not gates**. They are still the reason uptime monitoring is in
scope.

## Confirmed intent (this session, operator-answered)

1. **Documents — both official 양식, filled, not submitted.**
   첨부1 공모전 기획서 (7 sections, 1–6 필수) and 첨부2 기능명세서 (5 sections, all 필수).
   Structure extracted verbatim in `docs/reference/challenge/submission/README.md`.
2. **Language: English body, Korean section headings kept verbatim.** Product screenshots stay
   Korean — the surface is Korean.
3. **No demo video, no deck.**
4. **Deploy: I run it over ssh, additive only.** A dedicated user and directory, exactly one new
   nginx server block, only new systemd units. Nothing existing on that box is touched, restarted,
   rebound or dropped; destructive steps stop for the operator.
5. **Domain `jujutower.com`**, still wired through one env var so nothing hardcodes an origin.
6. **SEO setup required.**
7. **Email D-day notifications in scope**, using the existing `hi2vi_web` mail credentials,
   sender `hi@hi2vi.com`.
8. **Production smoke suite: yes. Uptime monitoring: yes**, alerting by email to
   `swangle2100@gmail.com`.
9. **Deploy-hardening deferred jobs stay deferred** — D32, D35, D37, D19, D22 are explicitly out.
10. **Meta/OG Korean copy: drafted here, approved by the operator at the acceptance gate** — not a
    design round.

## Orchestrator work in this slice (before dispatch)

These are mine, not the executor's, and land in the same commit as `P4.DECOMP`:

1. **Rewrite `works/phases/active/P4/intent.md`.** The *Original Input (verbatim)* block is
   immutable and stays byte-for-byte. Replace *Confirmed Intent* with the ten points above and
   append the new clarifications to *Clarifications Resolved*, dated 2026-09-02.
2. **Correct the stale `objective` in `works/phases/active/P4/phase.json`** (it still names the
   deck, the video, the submission and `ssh h`) and run `rebuild`. Flagged explicitly because it
   is a hand-edit of a state file — say no and I will instead record the correction only in
   `phase.md` and `intent.md`.
3. After `finish-slice P4.DECOMP`, declare the gate: **`accept-gate P4 --require`**. Not a
   judgment call — a public deployed site, new SEO metadata, and notification email are all
   operator-visible.

## What the executor does

`slice-executor-high` (kind `decomposition`, so high by kind whatever the risk says). It creates
the middle slices as **bare folders** with `new-slice` — never pre-filling any `plan.md` — and
records the breakdown, findings and notes in `phase.md`. It writes no product code.

### Slice cut to create

Ordering is forced by two dependencies: 첨부2 §5 is a judge-executable script **against the live
URL**, and SEO's `metadataBase`/canonicals/sitemap need the **real origin**. So the deploy leads,
the documents close.

| Slice | Name | Kind | Risk |
|---|---|---|---|
| `P4.S1` | Containerize: Dockerfile(s), `compose.prod.yml`, schema bootstrap, production config seam | implementation | high |
| `P4.S2` | The real `Mailer` over SMTP, and the D-day notification send path | implementation | high |
| `P4.S3` | Deploy artifacts: the `jujutower.conf` edge vhost, `deploy.sh`/`rollback.sh`, runbook | implementation | high |
| `P4.S4` | Execute the deploy on the Oracle box; Cloudflare zone, DNS, Origin CA, edge reload | implementation | high |
| `P4.S5` | SEO: metadata, robots, sitemap, canonicals, OG, JSON-LD | implementation | high |
| `P4.S6` | Production smoke suite + uptime monitoring with email alerting | qa | high |
| `P4.S7` | 첨부1 공모전 기획서 | docs | high |
| `P4.S8` | 첨부2 기능명세서 | docs | high |

Every slice is `high`. Nothing here is a one-line edit, and `S7`/`S8` are `docs` by kind but are
substantial authored documents, not a text tweak — `risk: low` would route them to `mid` and is
wrong.

`P4.S2` is pulled ahead of the deploy so the transport ships in the first image rather than forcing
a second release.

`P4.S4` is expected to stop `pending` at least once: adding the `jujutower.com` zone, its DNS
record and its Cloudflare Origin CA certificate are actions on the operator's Cloudflare account.

### The box already has a front door — this is the "no harm" contract

The single most important finding, and it corrects the obvious assumption: **the operator's Oracle
box does not use systemd, and Mijual must not install nginx.** A separate repo,
`~/projects/personal/edge`, owns `:80` and `:443` for every site on that box — one pinned
`nginx:1.27-alpine` container, `container_name: edge-nginx`, with `./conf.d` and `./certs`
bind-mounted read-only. It belongs to no app precisely so that an app redeploy can never take the
front door down.

So "additive, no harm to running apps" has a concrete, already-proven shape:

- **Add one file** to the edge repo's `conf.d/` (`jujutower.conf`), plus this zone's cert pair in
  `certs/`. Author it in *this* repo as `deploy/edge/jujutower.conf` — `hi2vi_web` uses exactly
  that convention — and copy it across. Edge-repo changes are outside Mijual's git; commit only
  what is in this repo, and name the edge-side file in the runbook.
- **Never** `up`, `restart` or `--force-recreate` the edge container. A config change is: drop the
  file → `nginx -t` → `nginx -s reload`. Recreating it drops the shared-network attachment and
  cascades into every co-tenant. The edge repo's own `validate.sh → stage.sh → deploy.sh` loop
  already encodes this, with `nginx -t` as a hard gate so a bad config reloads nothing.
- **Containers, not systemd.** Mirror `hi2vi_web/compose.prod.yml`: `restart: unless-stopped`,
  a healthcheck (which is also the rollback trigger), **`expose:` and never `ports:`** — host ports
  collide with co-tenants — and `networks: {external: true}` so `docker compose down` can never
  delete a network another site is on. Rollback is a tag flip: tag `:previous` *before* building,
  health-gate after `up -d`, retag and re-up on failure.
- **`next.config.ts` needs `output: "standalone"`** for the containerized frontend.
- Existing zone/upstream/`map` names in `conf.d/` are **global across the whole tree** — a
  duplicate name fails `nginx -t` for *every* site on the box. Namespace everything `jujutower_*`.

**Copy `edge/conf.d/vocky.conf`, not `hi2vi.conf`** — vocky is the same shape as Mijual, a FastAPI
and a Next upstream behind one vhost. Three rules it encodes, each of which is a live outage if
missed:

1. **Variable `proxy_pass` with a `resolver 127.0.0.11`** — container IPs change on every recreate,
   and a literal `proxy_pass http://svc:3000` resolves once at config load and then 502s forever.
2. **The `proxy_set_header` inheritance footgun** — nginx inherits the server-level header block
   into a location **only if that location sets none of its own**. One `proxy_set_header` inside a
   location silently drops the entire inherited set. So either hoist them all to server level and
   let every location set zero, or re-declare all of them in any location that sets any.
3. **Longest-prefix routing.** Mijual is simpler than vocky here — `/api/*` is a Next rewrite to
   the API, so the vhost can route everything to the frontend container and let Next proxy. That is
   the safer cut and it preserves the same-origin CSRF design; the alternative (nginx splitting
   `/api/` off to FastAPI directly) changes the origin model and must not be done casually.

### Streaming through two proxies, not one

`/ask` now traverses **Cloudflare → edge nginx → Next → FastAPI**, and each hop can break it:

- nginx needs `proxy_buffering off`, `proxy_request_buffering off`, `proxy_cache off`,
  `chunked_transfer_encoding on`, `proxy_http_version 1.1`, `proxy_set_header Connection ""`,
  a long `proxy_read_timeout`, and `add_header X-Accel-Buffering no`. The full-fat block in
  `edge/conf.d/changple-web.conf` (`location /bff/`, marked "do not tidy") is the one to copy.
- **Cloudflare caps an origin response at ~100 s and then serves a 524**, whatever nginx's timeout
  says. A single agent turn must stay well under that. This is new information the existing
  `architecture.md` note does not have.
- **`gzip` is off everywhere in the edge tree** deliberately — compression is Cloudflare's job.
  That happens to be the right answer for `no-transform` too; do not add gzip at the origin.

### Cloudflare: two things this repo's signed properties forbid

- **Do not enable Cloudflare Web Analytics.** It injects `beacon.min.js` from
  `static.cloudflareinsights.com` at the edge, and `security.md` carries a *measured* property that
  **no page contacts a third-party origin** (0 requests across five routes, dev and production).
  hi2vi_web accepts that trade; Mijual cannot without an explicit operator decision to retire a
  signed security property. Recommendation: leave it off and say so in `phase.md`.
- **Cloudflare prepends its own managed content-signals block to `/robots.txt`.** Do not duplicate
  it at the origin.
- Verify Search Console with a **DNS TXT Domain property** through the Cloudflare integration, not
  an HTML meta token — no new copy, no new tag in the layout.
- **Order is load-bearing** when standing the site up: HTTP-first over grey (DNS-only) DNS → mount
  the origin cert → enable `:443` → `nginx -t` → reload → flip DNS to proxied → set SSL/TLS mode
  **Full (Strict)** → enable the `:80`→HTTPS redirect **last** → HSTS. Out of order gives an
  instant 526 or a cached redirect loop. A wrong A record shows up as a **522**, not a DNS error.

### Mail: the transport already exists next door

The credentials the operator pointed at are `hi2vi_web`'s **transactional** stream: nodemailer over
**Namecheap Private Email** (`mail.privateemail.com`), env `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`,
`SMTP_PASS`, `SMTP_FROM`, `SMTP_TO`, supplied on the box through a gitignored `.env.prod`. Not
Resend — Resend is the separate cold-outreach stream on `send.hi2vi.com`, which this must not use.

Mijual's mailer is Python, so `P4.S2` implements `Mailer` over `smtplib` against the same account,
mirroring four patterns worth stealing verbatim: `secure` derived from the port (465), bounded
connect/greeting/socket timeouts so a dead SMTP host cannot hang a request handler, a display name
on `SMTP_FROM` (Gmail renders a bare address as its local-part), and newline-stripping on any value
that reaches a header.

Two things for the operator to weigh, recorded rather than decided here: the product would be
sending reader mail **from `hi@hi2vi.com`**, a different brand from 주주의관제탑 — a
`jujutower.com` sender needs its own DNS and warm-up; and `swangle2100@gmail.com` is the alert
recipient, not a product-facing address.

### Uptime: two mechanisms, and one is free

`hi2vi_web` learned that a **free UptimeRobot account cannot create monitors via the API at all**
(`newMonitor` → `access_denied`; reads and edits work). So: a UI-created 5-minute HTTP monitor on
`https://jujutower.com` with an email alert contact, **plus** a GitHub Actions synthetic probe on
`cron` — this repo is `leetusik/Mijual` on GitHub, and **a failed scheduled run makes GitHub email
the repo owner**, which is the alerting path with no new infrastructure. Two caveats it recorded:
GitHub disables a scheduled workflow after 60 days of repo inactivity, and the schedule only starts
once the file is on the default branch.

The probe should exercise the whole stack (Cloudflare → nginx → container) while consuming nothing
— `GET /api/health` plus the landing, rather than anything that spends a model call.

### Deferred jobs the decomposition must promote

Three open jobs are not "extra scope" — they are the unfinished halves of slices already in scope,
and each is filed with a trigger naming P4. `promote-deferred` them into their slice:

- **D5** → `P4.S5`. *"Favicon + per-route `<title>`/meta for the reader chrome"*, trigger *"before
  P4 Ship & Submit"*. The favicon half shipped in P10; the per-route title/meta half **is** the SEO
  slice.
- **D7** → `P4.S2`. *"Make the `notification_pref` save an upsert"*, trigger *"Before P4 Ship &
  Submit"*. A save bug in the surface the D-day mail reads from.
- **D23** → `P4.S2`. *"P4 mail subject still carries the retired name [미주알]"*. The signed R5
  subject template at `src/mijual/mail.py:14` renders
  `[미주알] {종목} — {마감명} D-{n} ({date})`. Nothing sends it today, so nothing has shipped the
  retired name — but `P4.S2` is the first send.

**D15** (*"Take the R7 implementation rules off the /ops door"*, trigger *"Before P4 Ship &
Submit"*) is a judgment call for the decomposition: it is small, and the `/ops` login page becomes
publicly reachable at this deploy. Promote it into `P4.S4` or leave it deferred with a reason.

The operator's "defer deploy hardening" covers **D32, D35, D37, D19, D22** — those stay deferred.
D31 loses its trigger entirely (it was *"before the P4 demo video"*).

### Copy that needs the operator's literal approval

Two slices generate **new Korean product copy**, which the design contract treats as a design
decision, not an implementation detail. Neither warrants a design round — both go to the acceptance
gate as literal strings, per the operator's answer:

1. **`P4.S5`** — meta description, OG title/description, per-route `<title>` patterns.
   `app/layout.tsx` records why none exist: *"the signed design writes no document-level copy, and
   inventing a Korean sentence would be a design change."*
2. **`P4.S2`** — the mail subject and body. `src/mijual/mail.py` is explicit that a `Message`
   carries *data, not copy* — *"a P5 module that wrote a Korean subject line would be inventing
   product copy"* — and that P4's transport renders it from R5's signed spec. With D23, that spec's
   subject must be re-signed anyway.

Draft both from copy that already exists in the signed record wherever possible, and put the exact
strings in the gate walkthrough.

### Constraints the executor must record in `phase.md`

These are already-verified facts from `docs/current/`; the decomposition carries them forward so
each middle slice inherits them instead of rediscovering them.

**Deploy (from `operations.md`, `architecture.md`, `api.md`, `security.md`):**

- `Cache-Control: no-store, **no-transform**` and `X-Accel-Buffering: no` must survive **every**
  hop on `/ask`. nginx and CDNs re-encode otherwise and the streaming state simply does not happen.
  Found in a real browser; `curl` without `Accept-Encoding` will not reproduce it.
- **Proxy idle timeout above ~10 s.** There is no heartbeat; the longest observed gap between
  frames is **6.0 s**. A shorter timeout cuts legitimate turns.
- **Create `conversation_turn` / `conversation_feedback` before the first question.** There are no
  migrations; a fresh database has 16 tables, not 18, and every `/ask` turn fails at persistence.
  `create_all` + `ensure_columns` is additive and idempotent (`make db-ensure`).
- **Install a root logging config**, or the `▷` agent-spend ledger is written nowhere. The
  Makefile's API launch inlines it; a bare `uvicorn` as a container entrypoint does not.
- **Eight env vars the live `.env` does not have** and the deploy must supply: `DATABASE_URL`,
  `REDIS_URL`, `MIJUAL_SESSION_SECRET`, `MIJUAL_COOKIE_SECURE=1`, `MIJUAL_OPS_ID`,
  `MIJUAL_OPS_PASSWORD`, `MIJUAL_APP_BASE_URL`, `MIJUAL_API_ORIGIN` — through a gitignored
  `.env.prod` on the box, with a committed `.env.prod.example` naming every key.
- **Postgres is net-new on that box for this stack.** hi2vi uses SQLite; there is no
  backup/restore or migration runbook next door to lift. `compose.yaml` here is dev-only (host port
  5434). The production database, its volume, and a restore path are this phase's own work.
- **There is no Python lockfile** — no `uv.lock`, no `requirements.txt`, only `pyproject.toml`
  ranges. A reproducible image wants one pinned.
- **`MIJUAL_OPERATOR_CONTACT` must be exported where the API runs**, not the frontend. Unset is
  invisible in dev and visible to every reader in production (the footer silently loses its links).
- **Do not add CORS.** The CSRF design rests on `/api/*` being a same-origin Next rewrite with no
  preflight.
- **Do not add a third-party origin to any page.** "No page contacts a third-party origin" is a
  measured, signed security property — that rules out Cloudflare Web Analytics, CDN fonts and any
  injected edge script.
- Cross-process state (the ask limiter, login attempt limiting) is **per process**. N workers means
  N× the intended cap.
- Anything in this repo calling a Cloudflare-fronted host over `urllib` must send a `User-Agent`
  or gets `403 error 1010 browser_signature_banned`.

**SEO (from the frontend survey):**

- **Nothing is prerendered.** `prerender-manifest.json` lists exactly four static routes, all icon
  files; `dynamicRoutes: []`. Every reader route is request-time via `await connection()`, and
  `/portfolio` + `/ops` via `cookies()`. Every crawl is a full SSR + FastAPI round trip with no
  `Cache-Control`. This is the biggest structural SEO item and the one place the phase may need to
  make a real rendering decision.
- **What exists:** `<html lang="ko">`, one global `<title>주주의관제탑</title>`, and the three
  `app/icon*.png` favicon conventions.
- **What is missing, everywhere:** meta description, `metadataBase`, canonical/`alternates`,
  openGraph, twitter, `opengraph-image`, `robots.ts`, `sitemap.ts`, `manifest.ts`, JSON-LD, and any
  `noindex` on `/ops`, `/auth/*`, `/portfolio`. **There is no `generateMetadata` anywhere in the
  tree** — so `/stocks/[corp_code]` and `/events/[rcept_no]`, the two real long-tail surfaces, all
  serve the same title and no description.
- **Reuse `frontend/lib/routes.ts`** — the single source of truth for reader paths — as the sitemap's
  static half. `/ops` paths deliberately live in a separate `components/ops/routes.ts` so no reader
  module can import them; keep it that way.
- A sitemap's dynamic half is buildable from `GET /board?rights=…` (nothing is paged): every
  exposable event gives `/events/{rcept_no}`, and the board's companies give `/stocks/{corp_code}`.
- **`/stocks` has no nav link** (nav is two slots: 관제 현황판 · AI 질문), so it is orphaned for
  crawlers — an internal-linking gap worth naming.
- The missing description is a **deliberate design-gate blocker**, not an oversight:
  `app/layout.tsx` records that the signed design writes no document-level copy. Per the operator's
  answer, drafted Korean strings go to the acceptance gate for literal approval.
- **There is a proven implementation to mirror, file for file**, in `hi2vi_web/src/app/`:
  `robots.ts`, `sitemap.ts` (with `dynamic = "force-dynamic"` and the DB read wrapped in try/catch
  so an outage degrades to the static routes instead of 500-ing), `manifest.ts`, the `layout.tsx`
  metadata block (`metadataBase`, title `default` + `template`, `alternates.canonical`,
  `openGraph.locale: "ko_KR"`, twitter card, and `verification` tokens **conditionally spread** so
  an empty string renders no tag), the `opengraph-image.png` file convention, and
  `components/seo/json-ld.tsx` (an `@graph` of `Organization` + `WebSite`, `@id`-linked,
  `inLanguage: "ko-KR"`). Two structural decisions worth copying: **every SEO string comes from one
  typed source module**, never inline; and the site URL derives from a build-baked
  `NEXT_PUBLIC_*` var. Its recorded trap: a `?? "https://…"` fallback lets a build with the var
  missing *silently succeed* with wrong canonical URLs — so assert the build arg is non-empty
  rather than defaulting it.

**Documents (from `operations.md` + the submission README):**

- 첨부1: ①서비스 명칭 ②아이디어 기획 핵심내용(요약) ③문제 정의 및 제안 배경 ④서비스 컨셉 및 차별성
  ⑤활용 데이터 및 생성형 AI 모델 적용 방안 ⑥기대 효과 및 확장 가능성 ⑦자유 타이틀. Both templates
  open with `팀명` + `구성원 성명`.
- 첨부2: ①MVP 구현 범위 (**미구현·향후 기능은 제외** — so notifications may only appear here if
  `P4.S2` actually ships) ②주요 기능 목록 (기능명·설명·**관련 화면**·구현 상태) ③사용자 이용 흐름
  ④AI 및 데이터 처리 방식 ⑤**MVP 검증 방법** — 테스트 계정, 샘플 입력값, 예상 결과, browser
  restrictions, limitations.
- **§3.6 AI-role architecture must appear** — "AI는 '읽기'와 '말하기'를 하고, '계산'만 결정론이 한다"
  — it is the registered #1 expected Q&A and answers 첨부1 §5 directly.
- **§7 working rules bind the prose**: evidence-tagged facts separated from estimates, no inflation,
  and **no fine-tuning / PyTorch / HF framing anywhere** (the forms ask about *use*, never training,
  so this costs nothing).
- **The measured numbers to use, with their caveats**: ▷ 718.1억원 lapsed 신주인수권 value 2026 YTD
  (conservative band edge ▷ 548.7억원); 488 exposable events (① 50, ② 422, ③ 16); 98.6 % strict
  extraction accuracy (213/216, Wilson 96–100 %) — which **must** carry its caveat that it is
  cross-model judgement, not human ground truth (D-7); ▷ 49.2억원 deliberately excluded by the gates.
- The product is **주주의관제탑**, renamed from 미주알 in P10. Code identifiers keep `mijual`.
- 첨부2 §5's 샘플 입력값 is already built: the judge-facing **샘플 포트폴리오** loads four real
  pinned events in one click.

### Output-format decision to record

The `.hwpx` → filled → PDF path is **unsolved** (writing OWPML needs Hangul or a converter) and is
recorded as an open question. Since the operator is **not submitting**, that constraint is no longer
binding. Recommended and to be recorded as a decision in `phase.md`:

> Markdown source of truth in the repo (`docs/reference/challenge/submission/drafts/`), Korean
> section headings verbatim, English body, exported to PDF through a print stylesheet. If the
> documents are ever actually submitted, filling the real `.hwpx` becomes a separate job.

## Validation

- `python3 scripts/workflow.py validate` — clean.
- `python3 scripts/workflow.py next` — points at `P4.S1`.
- `works/backlog.md` shows the eight new slices with the intended kinds and risks.
- `phase.md` is under budget (200 lines / 16 KB) and its `## Slices` block is generated, not
  hand-edited.
- `intent.md`'s verbatim block is byte-identical to before.

## Verification of the phase as a whole (for `P4.REVIEW`, not this slice)

The acceptance gate walkthrough will be: open `https://jujutower.com` in a real browser, walk the
six surfaces, run a streaming `/ask` turn and confirm it arrives frame by frame rather than in one
burst, view source on `/stocks/{corp_code}` for a real per-company title and description, fetch
`/robots.txt` and `/sitemap.xml`, confirm `/ops` is `noindex`, trigger one D-day notification mail
to the operator's address, and approve the literal Korean meta strings.

## Reference material the middle slices should read

Two sibling repos of the operator's, on the same box, solve most of this already. Named here so the
decomposition can point each slice at them instead of every executor rediscovering the box:

- `~/projects/personal/edge` — **owns `:80`/`:443` on the Oracle box.** `edge/conf.d/vocky.conf` is
  the FastAPI + Next vhost to copy; `edge/conf.d/changple-web.conf` `location /bff/` is the
  streaming block to copy; `edge/conf.d/00-default.conf` explains why a vhost must not declare
  `default_server`; `edge/{validate,stage,deploy}.sh` and `edge/README.md` are the config-change
  loop.
- `~/projects/personal/hi2vi_web` — `compose.prod.yml` and `deploy/deploy.sh` / `rollback.sh` for
  the build-on-box, tag-flip, health-gated release; `deploy/runbook.md` §S4–S6 for the Cloudflare
  stand-up order; `src/lib/mailer.ts` for the SMTP transport patterns; `.github/workflows/
  synthetic-contact-probe.yml` + `deploy/monitoring/README.md` for the probe; `src/app/{robots,
  sitemap,manifest}.ts`, `src/app/layout.tsx` and `src/components/seo/` for SEO.

Neither is this repo. Read them; do not edit them. The one file that must eventually land in the
`edge` repo is authored here as `deploy/edge/jujutower.conf` and copied across by the deploy slice.

## Honest note on scale

This is eight slices — a containerization, a mail transport, a first production deploy onto a
shared box, an SEO pass, monitoring, and two authored documents — against a contest deadline five
days out. The document slices (`S7`, `S8`) depend on the deploy only for 첨부2 §5's judge-run
script and its 관련 화면 screenshots, so if the deploy stalls they can still be drafted and finished
later. If something has to give, the order I would protect is: **documents → deploy → SEO →
monitoring**, because the documents are what you asked for and the rest can land after 9/7 when
nothing is being submitted. I will flag it rather than silently reordering if we get there.

## Explicitly out of scope

daker.ai submission · demo video · 발표자료 deck · D32, D35, D37, D19, D22 · the remaining 29 open
deferred jobs · archiving the phase.
