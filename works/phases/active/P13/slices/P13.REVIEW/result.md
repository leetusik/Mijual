# Result — P13.REVIEW (phase review, `slice-executor-high`)

- **status:** `done`
- **review_verdict:** **`pass`** — with two notebook-only findings closed in place (below). No product,
  code or deploy finding; no fix slice proposed. The phase's gate is `required: true` and was never
  opened, so this pass is not the last word: the orchestrator opens the gate with the walkthrough and
  the operator has it.
- **summary:** Re-ran every slice's validation across the finished phase (171 pytest, a clean
  production build + typecheck + 23/23 smoke in a copy outside the tree, `db ensure` idempotent, the
  whole S1/F1 HTTP contract over the running dev API, `make smoke-prod` 17/17, the box read-only, and
  `workflow validate`), judged the four implementation slices against `phase.md`'s decisions line by
  line in the code, cross-checked the notebook against every `result.md`, opened the running product
  myself on production and on a local production build in Aside (`u2`), walked the flow with fresh
  eyes, and re-ran the cumulative regression checklist. Everything P13 claims is true in the running
  product, including the one thing that was false between S1 and F1: the 5-attempt cap is real over
  HTTP (measured today, `attempts = 5`).
- **files_changed:**
  - `works/phases/active/P13/slices/P13.REVIEW/result.md` (this file)
  - `works/phases/active/P13/phase.md`
  - `docs/versions/qa/v0019_*.md` + `docs/current/qa.md` + `docs/index.json` (the gate's stage-4
    append — the `## Regression Checklist` P13 block, through `doc-new-version` + `rebuild-docs`)
  - **No source file was touched.** Nothing on the production box was edited; `.env.prod` was never
    read or written; `/ops` was never logged in to.
- **validation:** the full table is § 1. Every command passed. Headline: `pytest` **171 passed** ·
  `npm run build` clean / `typecheck` clean / `smoke` **23/23** · `db ensure` → `schema ok`
  (idempotent) · the HTTP contract **9/9 steps** · `make smoke-prod` **17/17, 0 fail** · box: six
  services up, `mijual-schema` Exited 0 with `schema ok (+1 columns)`, `/home/opc/Mijual` at
  **`1899111`**, **20** user tables, SMTP transport line present · `workflow validate` passed (three
  pre-existing warnings).
- **deviations:** three, all recorded with reasons in § 6.
  1. The dev stack was **not** restarted, though the plan's trigger (API pid older than F1's commit)
     fired. The trigger is a false positive here and a stronger check replaces it — see § 6.1.
  2. The one sanctioned production write was made **twice** (1280 and 390), not once. The second
     mailed **nothing** — it fell inside the 60 s cooldown — so the operator's mailbox holds four
     mails, not five. See § 6.2.
  3. The regression checklist's **paid model-call lines were stopped after 2 of the 6 dev calls the
     plan allowed, and 0 of the 1 production call**, on the operator's mid-review instruction. See
     § 6.3 — the blast radius is proven instead.
- **doc_impact:** two lines appended to `phase.md`, both closing a notebook-only finding —
  `backend.md` (the `_stored_utc` naive/aware seam and the rule it states for future code) and
  `frontend.md` (the 만료/소진 line is drafted and may change at the gate). Plus one line for the qa
  version this review wrote.
- **doc_versions:** the phase's own durable-truth changes are **`none — deferred to a docs phase`**
  (13 `## Doc impact` notes across 8 docs, verified complete in § 3). The review wrote **one** of its
  two named gate sections: **`qa` — `## Regression Checklist`**, the stage-4 append. It wrote **no**
  `operations` version: P13 changed nothing about how the operator runs or views the product, and the
  section's one stale sentence is **P4's** owed note, not P13's.
- **explain:** `not written — run /explain for this phase`
- **deferred jobs to file** (the orchestrator files these; the last id is **D49**, so these are the
  next two):
  1. **title:** `/ops 독자 계정 table — mark or hide unverified accounts`
     **reason:** After P13 the 독자 계정 table (`GET /ops/users`) silently lists accounts that cannot
     log in, and nothing on the surface says so; P13 excluded every `/ops` change by intent, so
     neither marking nor hiding was built.
     **trigger:** The next `/ops` phase, or the first time the operator reads that table and cannot
     tell a pending signup from a real reader.
  2. **title:** `Janitor for long-dead unverified accounts and their spent code grants`
     **reason:** P13 deliberately ships no sweep — re-signup re-takes any address at any age, which
     is what `intent.md` assumption 3 actually asks for — so unverified `account` rows and their
     `email_verification` rows accumulate with nothing to remove them. `verification_pending_since`
     already doubles as the age stamp, so the job is housekeeping, not design.
     **trigger:** When the unverified count on production becomes noticeable, or the next backend
     housekeeping phase.
- **walkthrough:** § 5, verbatim. It is what the orchestrator passes to `accept-gate --open`.

---

## 1. Stage A — every slice's validation, re-run across the finished phase

| # | command / check | runtime | outcome |
|---|---|---|---|
| A1 | `.venv/bin/pytest` | dev | **pass — 171 passed**, 1 pre-existing `StarletteDeprecationWarning` (S1 + F1's count exactly) |
| A2 | `npm run build` in a `frontend/` copy **outside the repo** (`NEXT_PUBLIC_SITE_URL=https://jujutower.com MIJUAL_API_ORIGIN=http://127.0.0.1:8010`) | prod-build | **pass** — clean, 23 routes, no warning; the working tree's `.next` untouched |
| A3 | `npm run typecheck` | prod-build | **pass** — `tsc --noEmit`, no output |
| A4 | `npm run smoke` | prod-build | **pass — 23/23**, 0 fail (S2 recorded 23/23) |
| A5 | `.venv/bin/python -m mijual.db ensure` | dev Postgres | **pass — `schema ok`**, no column added: idempotent, exactly as S1 left it |
| A6 | HTTP: signup | dev API | **pass — 201**, **no `Set-Cookie`**, body `{"verification":{"email":…,"expires_at":…}}`, **no code in the body** |
| A7 | HTTP: login on the unverified account | dev API | **pass — 200 `verification_required`**, **no cookie**, the **same `expires_at`** (no second code minted) |
| A8 | HTTP: wrong code ×4, then the 5th | dev API | **pass** — `verification_code_invalid` ×4, the 5th **`verification_code_expired`** |
| A9 | the grant row after A8 | dev Postgres | **pass — `attempts = 5`**, unused, account still pending. **F1's fix is real in the running product.** |
| A10 | HTTP: the genuinely mailed code after A8 | dev API | **pass — 400 `verification_code_expired`** — the mailed code died with the grant |
| A11 | HTTP: 재전송 inside the cooldown | dev API | **pass — `{"resent":false,"verification":{"email":…}}` — `expires_at` *absent*, never null**, on a dead grant. The contract's own corner, live. |
| A12 | back-date `created_at` 61 s, then 재전송 | dev API | **pass — `resent: true`** + a fresh code in `var/stack/api.log`, new `expires_at` |
| A13 | HTTP: the fresh code | dev API | **pass — 200 `{"account":…}` + `Set-Cookie: mj_session=…; HttpOnly; …; SameSite=lax`** |
| A14 | `GET /auth/me` with that cookie | dev API | **pass — `authenticated: true`** |
| A15 | a completed reset on a **second, unverified** account | dev API + Postgres | **pass** — `reset/confirm` → 200 + cookie, the column read `t` before and **`f` after**, `/auth/me` authenticated. **Assumption 4, live.** |
| A16 | both throwaway accounts deleted (`DELETE /auth/account`) | dev | **pass — 200 ×2**, `select email from account where email like 'p13-%'` → **empty** |
| A17 | `make smoke-prod` | production | **pass — 17 pass · 0 fail · 11.6 s**. The `www` line passed from this Mac too; no local false FAIL this run. |
| A18 | six services up | box | **pass** — api/beat/postgres/redis/web/worker, api+web healthy, all `Up 20 minutes` (the release) |
| A19 | `mijual-schema` one-shot | box | **pass — Exited (0)**, log `schema ok (+1 columns)` |
| A20 | `git rev-parse --short HEAD` in `/home/opc/Mijual` | box | **pass — `1899111`** |
| A21 | `select count(*) from pg_stat_user_tables` | production DB | **pass — 20** |
| A22 | `mail transport:` line | box | **pass — `smtp mail.privateemail.com:587 tls=starttls from=주주의관제탑 <hi@hi2vi.com>`**, never `console` |
| A23 | `smtp mailer: sent signup_verification` | box | **pass — present**, S3's three lines at 01:51:17 / 01:53:41 / 01:58:43 KST |
| A24 | the proof account's row, as S3 left it | production DB | **pass — `4\|1`** (4 accounts, 1 pending = id 41); grant id 3, **`attempts 0`** — all five unspent, exactly S3's note |
| A25 | `python3 scripts/workflow.py validate` | repo | **pass** — `Workflow validation passed.` The three warnings are pre-existing and none is P13's: `consolidation_owed=P4, P12`, `stale_docs=frontend, operations, product, qa, security`, `oversized_doc_sections=11` |

**Instrument for every browser claim below: Aside on the agent account `u2` (profile 「claude2」)**,
`aside repl --account u2 "<js>"` — never `u0`, never `aside account use`, never `aside profile list`.
Fifteen invocations, each opening its own tab and doing its whole job in one script (tabs do not
survive between calls; profile cookies do, and ignore ports).

## 2. Stage B — did each slice meet its brief, and does the built product match `## Decisions`?

Read head-first, then whole where it mattered: S1 § *Step 4*, S2 § *Finding 1* and § *The drafted
Korean, verbatim*, F1 § the red run and the write-path audit, S3 § the release table and the proof.
Then the code itself. Every load-bearing claim in `## Decisions` was checked **against the source**,
not against the prose that describes it.

**`P13.DECOMP` — the cut and the schema mechanism.** Sound, and its two corrections to the plan were
right. `ensure_columns` does refuse a non-nullable or defaulted column
(`src/mijual/db/schema_sync.py:45`), and the shipped column is exactly what survives that guard:
`verification_pending_since: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))` —
nullable, **no `default=`** (`models.py:802`), set to `utcnow()` in `create_account`'s **body**
(`auth.py:345`, `:352`). `intent.md` assumption 6's Alembic path really does not exist, and correcting
it in `## Decisions` rather than in the immutable `intent.md` was the right call. The `email_verification`
table's three deliberate differences from `PasswordReset` are all in the code as argued, and finding 2
(no `UniqueConstraint` on a 6-digit digest) is a genuine latent-500 avoided, not a rationalisation.

**`P13.S1` — the backend.** Met its brief. The claims I checked directly:
- **`start_session` refuses an unverified account by raising** (`auth.py:445`), and it is a real single
  enforcement point: `grep` finds **exactly three** callers, all in `routers/auth.py` — `verify`
  (`:155`, after `verify_code` cleared the column), `login` (`:205`, which branches to
  `verification_required` before reaching it) and `reset/confirm` (`:270`, after `confirm_reset`
  cleared it). Signup no longer calls it at all. Nothing else has to remember the gate.
- **The three-kind rule is stated in both docstrings, not slipped in** — `mail.py:18` («Three kinds,
  deliberately — and the third one arrived exactly the way this…», naming what the paragraph used to
  say and rewriting it) and `mailcopy.py:38` («알림 외 메일 금지. Three kinds exist, and the third was
  added in a diff»). Assumption 5, honoured to the letter.
- **`Account`'s docstring names the column as account *state*, not PII** (`models.py:767-780`), and
  the must-stay-absent list is unchanged — it argues the point rather than asserting it.
- **The `_stored_utc` SQLite/Postgres seam** (`auth.py:635`) is correct and its docstring states the
  convention. It is also the review's finding N1 — see § 3.
- **Malformed code costs an attempt:** `verify_code` `strip()`s and compares, with no length branch
  (`auth.py:809-810`), so there is no cheaper guess. Proven over HTTP (A8 used six-digit wrong values;
  the client gate covers the short ones before they leave the browser).
- **Re-signup replaces the hash** (`auth.py:342`) and restarts the pending clock; a **verified**
  address is still `409 email_taken` (`:339`). The takeover objection is answered in the code's own
  words and is right: no session can ever have existed on an unverified account, because
  `start_session` refuses to make one.

**`P13.S2` — the frontend.** Met its brief, and its drafting discipline holds:
- Every new string carries `drafted P13 — approved literally at the P13 gate` (`mailcopy.py:22`,
  `:122`; `copy.ts:55`, `:88`, `:169`).
- **`--alert` is absent from this layer.** Every hit in `frontend/components/auth/` is a comment
  *asserting* it must not appear (`AuthPanel.tsx:65`, `:153`; `Auth.module.css:17`).
- **The way back needed no constant** — it renders the origin mode's own name
  (`AuthPanel.tsx:533`, `origin === "signup" ? SIGNUP_KO : LOGIN_KO`), confirmed live: 계정 만들기 when
  entered from 가입, 로그인 when entered from 로그인.
- **The P12.F5 reservation is intact** (`AuthPanel.tsx:394` — the band's slot is still
  `display: contents`; `Auth.module.css:113` still names it the pre-hydration mirror's fourth use).
- **The client six-digit gate sends nothing** (`AuthPanel.tsx:321-323`, `CODE_RE` before any request),
  proven live at 390 on **production**: typing `12` and submitting rendered
  「인증번호 6자리를 입력해 주세요.」 in the status slot with no request.
- **`authErrorKo` maps both new codes** (`copy.ts:303-306`) — without which they would have been
  silently invisible, per its `null`-for-unsigned rule.
- **Exactly one CSS rule was added** (`Auth.module.css:213`, `.code { font-variant-numeric:
  tabular-nums }`), and `Auth.module.css` still has **exactly one** real `@media` (`:489`,
  `max-width: 767px`) — the other two hits are comment lines.
- **`SIGNUP_INTRO_KO`'s re-draft keeps R5's first clause verbatim.** At `0fa2e36` it read
  「이메일과 비밀번호만으로 만듭니다 — 만들어지면 바로 로그인됩니다.」; today
  「이메일과 비밀번호만으로 만듭니다 — 인증번호를 메일로 보내 드립니다.」 Only the promise after the
  em dash moved, exactly as the code comment claims.

**`P13.F1` — the fix.** The most important slice to check, and it holds up.
- **The commit is justified and the justification is right.** `verify_code`'s wrong-code branch reads
  `reached_cap` **before** `db.commit()` and then raises (`auth.py:811-823`); the docstring
  (`:781-799`) argues it correctly — `get_write_session` rolls back on any exception, which is right
  for a rejected 가입 and wrong for a counter whose job is to make failures expensive — and it names
  the one thing that could ride along (a password-hash upgrade on a *correct* password, which deserves
  to survive). I could not find a second write it silently commits.
- **The fixture change is applied to all three files** — `tests/test_web_auth.py:59-71`,
  `tests/test_web_ops.py:65-75`, `tests/test_web_portfolio.py:155-165`, each now `yield` → `commit` on
  a normal return, `rollback` + `raise` on an exception, each with a comment naming why. This is the
  part that makes the suite able to see the bug class at all.
- **And it is real in the running product**, not just in the suite: A8/A9 measured five wrong codes
  over HTTP against the live dev API, `불일치 ×4` then `만료`, and the row persisting **`attempts = 5`**.
  S2's finding is closed by measurement, not by argument.

**`P13.S3` — the release.** Met its brief and left the box alone. Both gates were checked before
releasing; the schema line, the 19 → 20 table count, the grandfathering `3|0` **captured before any
write**, the SMTP transport line and the send lines are all still readable on the box today and all
match its `result.md` exactly (A18-A24). The freeze was respected with ~33 h of clearance. Nothing
under `/home/opc` was edited.

**Orphaned design routes:** none, as expected — P13 ran with **no design round**. `frontend/app/**`
contains no `mock*` route (the production build's 23-route listing carries none either).

## 3. Stage B — the notebook against the logs, and the `## Doc impact` coverage

`phase.md` carries **13** `## Doc impact` notes across **8** docs: `api` ×1, `backend` ×2,
`security` ×3, `data` ×1, `architecture` ×1, `frontend` ×1, `experience` ×1, `product` ×1,
`operations` ×1, `qa` ×2. I checked each against the code and against the slice logs.

**Coverage — the plan's candidate list, checked one by one:**

| candidate | covered? |
|---|---|
| the `start_session` guard | **yes** — `backend.md` ("now **raises** on an unverified account") and `security.md` ("the single structural enforcement point") |
| the `.code` CSS rule | **yes** — `frontend.md`, named with its declaration |
| the `AuthResult` union | **yes** — `frontend.md`, including the branch-on-the-key rule |
| `authErrorKo`'s two new codes | **yes** — `frontend.md` |
| the three fixtures' rollback shape | **yes** — `backend.md` (F1) and `qa.md` (F1) |
| the box's 19 → 20 and the first additive column | **yes** — `operations.md` (S3), with the deploy log and the rollback-point consequence |
| the `## Operator Runtime` staleness | **correctly absent, and not lost** — it is on **P4's** owed list (`works/phases/active/P4/phase.md:1163-1165`, "v0014 still says Aside is unavailable, which stopped being true 2026-09-03"), and P12 recorded that P4 owes it. P13 writing a second note would duplicate a debt, not pay one. |
| the F1 copy corner | **partly** — see finding **N2** |
| `_stored_utc` | **no** — see finding **N1** |

**Finding N1 (notebook-only, closed by this review).** `slices/P13.S1/result.md` § *One finding worth
carrying* records a constraint in as many words — «Any future backend code that does Python arithmetic
on a stored timestamp will meet the same trap» — and neither the constraint nor `_stored_utc` appears
anywhere in `phase.md`. By the plan's own rule that is a finding. It is notebook-only (the code is
correct and the docstring carries the trap), so I closed it: a `## Decisions` line now records the
seam, and a `## Doc impact` line on `backend.md` sends it to the docs phase.

**Finding N2 (notebook-only, closed by this review).** The `frontend.md` note describes the 만료/소진
line as shipped, with nothing to say it is **drafted and may change at the gate** — while
`## Operator Questions` carries F1's open question about that exact line. A docs phase consolidating
from the notes alone would version a sentence the operator may be about to replace. Closed by
appending a `## Doc impact` line saying so.

**No other drift.** Every other decision or constraint in the five `result.md` files appears in
`phase.md`, and no `## Operator Questions` entry was dropped. The notebook being *shorter* than the
logs is the design, not a finding.

## 4. Stage C — the gate stages

### C.1 — the manifest

`## Operator Runtime` in `docs/current/operations.md` is **present and filled**: run command
(`make stack-up`, API `127.0.0.1:8010` + `next dev` `:3010`), mode (dev), origins, viewports (1280 /
390, plus 412×915 @ DPR 2.625 / 4× CPU / ≈1.6 Mbps / 150 ms for cold-cache work), the production
runtime `https://jujutower.com` with its Cloudflare → `edge-nginx` → `mijual-web` access path, the
local production-build recipe on **3014**, and the freeze. **Not a halt.** It is stale on exactly one
sentence — the one saying Aside's daemon does not run on this Mac — and that correction is P4's owed
note, recorded in two notebooks. A manifest whose instrument sentence is stale is not an unfilled
manifest, and P13's own `## Decisions` name the instrument and the account (`u2`) explicitly.

### C.2 — I opened the running product myself

**On production (`1899111`), 1280 and 390, in Aside `u2`:**

- `/auth/login` → **계정 만들기** renders the re-drafted intro, verbatim:
  「이메일과 비밀번호만으로 만듭니다 — 인증번호를 메일로 보내 드립니다.」
- `GET /api/auth/me` → **`{"authenticated": false}`**.
- **The served HTML of `/auth/login` carries no code and no verification state**: `이메일 인증` absent,
  `auth-code` absent. The one six-digit run in the document is the Next chunk filename
  `3fntmmi971322.js` (13 occurrences, 1 distinct) — I checked, because a false clean here is exactly
  the shape a leak would take.
- **`POST /api/auth/login`, proof address + wrong password → `401 invalid_credentials`**, and a
  nonexistent address answers a **byte-identical body** (`cmp` clean). Discloses nothing.
- **The one sanctioned production write** (see deviation § 6.2): re-submitting 계정 만들기 with the
  proof address, which S3 left unverified, lands the code state **on production** without creating a
  second account (`4|1` before and after). At **1280**: title 이메일 인증, the intro naming the
  normalized address and the 10분 window, `#auth-code` `type=text` `inputMode=numeric`
  `autocomplete=one-time-code` `maxLength=6`, **382×48**, `tabular-nums`, **focused**, 확인 **48**,
  the quiet row 인증번호 재전송 + a way back labelled **계정 만들기**. At **390**: field **324×48**,
  `docW 390 = viewW 390`, and typing a 2-digit code answered 「인증번호 6자리를 입력해 주세요.」 with
  **no request**. Every number equals S2's dev measurements and S3's production ones.
- **It mailed**, once: a fourth `smtp mailer: sent signup_verification` at **02:15:07 KST**, grant
  id 4 superseding id 3, `attempts 0`, expiring 02:25:05 KST.
- **And the second submit mailed nothing** — it fell inside the 60 s cooldown, the live grant stood
  and its `expires_at` came back unchanged. That is S1's anti-mail-bomb property outranking a caller,
  observed live on production by accident rather than by design, which is the best kind of proof.
- **Every other reader route still answers 200 uncookied**: `/`, `/stocks`, `/stocks/00547510`,
  `/events/20260806000329`, `/auth/login`. (`/board` answers 404 — it is **not a route** and never was;
  the plan's list named it, the product's 23-route listing does not. Not a finding.)

**On the local production build (`:3014`, built from this tree outside the repo), 1280 and 390:** the
code state is byte-for-byte the same product — field **382×48** at 1280 / **324×48** at 390,
`tabular-nums`, focused, submit **48**, `docW 390 = viewW 390`. **Dev, the production build and
production agree on every measured value.** There is no dev/production gap on this surface.

### C.3 — fresh eyes, as a first-time Korean reader (dev for the flow, production for the anonymous half)

I walked it: land → 로그인 → 계정 만들기 → read the intro → submit → the code state → mistype →
재전송 → the code from the log → 보유 종목 → 로그아웃 → 로그인 again. All of it worked, first try, and
the strings read like one voice with the rest of the panel. What I would raise as a reader — **not
judged against the design record, and none of it fixed silently:**

1. **A reload mid-code drops you back to a bare 로그인 panel with no explanation.** Measured: after a
   reload the `#auth-code` field is gone and the panel reads 「가입한 이메일과 비밀번호로
   로그인합니다.」 — nothing says an account is half-made, nothing says a code is sitting in your
   mailbox. It **is** recoverable without help, and elegantly: typing the same address and password
   into 로그인 lands straight back on the 인증번호 state (I did it). But nothing on the screen tells
   you that, and a reader who assumes the signup failed will press 계정 만들기 again — which happens
   to work too. Worth a decision, not a fix.
2. **The 인증번호 state still offers 「샘플 포트폴리오로 둘러보기」** underneath the way back. It is the
   pre-existing R12 sample entry and P13 changed nothing about it, but it is now an exit offered
   mid-verification, one tap from the field you are meant to be typing into.
3. **There is no countdown, by design — and the reader has no way to tell how much of the 10분 is
   left.** The record argues this well (a countdown makes a non-event into something to watch, and
   `expires_at` can be absent entirely), and I am not disputing it. I am reporting what it feels like:
   the intro promises 10분, and after a minute of hunting for the mail there is nothing on screen that
   says whether you still have it. The 만료 line, when it comes, is clear and points at 재전송 — so the
   flow terminates correctly either way.
4. **Nothing dead, nothing broken.** Every control on the 인증번호 state does something: 확인 submits,
   재전송 answers in the same slot whether or not it mailed, the way back returns to the mode you came
   from with both fields still filled. The anonymous half on production (land → search → an event →
   the login page) is unchanged at both viewports.

### C.4 — the cumulative `## Regression Checklist`, re-run

**154 lines.** Grouped by block, with every line that is not a clean pass named individually.

| block | lines | dev | prod-build | production | result |
|---|---|---|---|---|---|
| Foundation (pre-P8): suite, build, gates, guards, exposure, corpus idempotence, secrets | 14 | ✓ | ✓ | ✓ | **14 pass** |
| P8 surface blocks (chrome, board, event detail, stocks, auth, portfolio, ask boundary) | 58 | ✓ | ✓ | ✓ | **52 pass · 6 not re-run** (paid model calls — see below) |
| P9 surface blocks (ask behaviour, calculation, refusals, `/ask` shell) | 18 | partial | — | — | **6 pass · 12 not re-run** (paid model calls) |
| P10 brand rounds (mark, launcher, favicon, type, wordmark geometry) | 33 | ✓ | ✓ | ✓ | **33 pass** (live where observable; the ImageMagick trim-box lines re-derived from the served asset, which is byte-identical — see below) |
| P4 production block | 23 | — | ✓ | ✓ | **22 pass · 1 not re-run** (the D-day mail demo — it sends real mail from the box; operator-only) |
| P12 flicker-polish block + instrument notes | 8 | ✓ | ✓ | ✓ | **8 pass** |
| | **154** | | | | **135 pass · 19 not re-run, each named below** |

**Selected measurements, so the "pass" above is checkable rather than asserted:**

- `pytest` **171** / `validate` clean · `build`+`typecheck`+`smoke` **23/23** · `gates run` ×2
  **byte-identical**, **710** field rows unchanged · `estimate report` ×2 **byte-identical** ·
  `scheduler once --offline` **six stages green at 0 requests / 0 calls** · `extract recheck` ×2 and
  `evalset refresh-recall` ×2 both **"unchanged — nothing written"**, and the tree stayed clean.
- **Exposure invariant, re-derived read-only:** 628 events, 488 exposable, **418** renderable
  fields — **0** outside `passed`/`tbd`, **0** `tbd` carrying a value, **0** renderable fields on a
  non-exposable event. The 418 matches `gates run`'s own line.
- **The structural guards** (four AST import scans, the anonymity scan, the tool-signature check, the
  ops unsafe-method check) live in the suite and are green inside the 171
  (`test_no_request_path_module_imports_a_spending_module`,
  `test_the_agent_package_imports_no_spending_module`,
  `test_the_derivation_layer_imports_no_module_that_spends`,
  `test_the_sample_is_anonymous_and_carries_no_account_fact`, …).
- **No quota or storage-denial copy:** the only 「탭을 닫으면」 in the tree is
  `CONVERT_SESSION_KO` — the 보유량 conversion offer, the documented exception. No `localStorage` in
  the ask surfaces beyond comments asserting `sessionStorage`. No `vk_`/`vocky` string in the built
  `.next/static`. `rg 480|481` over `components/ask` + `lib/ask.ts`: **nothing**.
- **Chrome / brand, live on production at 1280:** title 주주의관제탑 · **no** 미주알/미주얼/MIJUAL/Mijual
  in any reader page's `innerText` · **3** icon links · the wordmark paints at **h27 (nav) / h24
  (footer)** from `juju2-wordmark-white-273-73c23508.png` · `/assets/mijual-*.png` → **404** ·
  `cache-control: public, max-age=31536000, immutable`. The content-hashed filename is what makes the
  P10 trim-box measurements still true: the bytes cannot have changed under the same URL.
- **Widths, on production:** `/stocks` **620px**, `/stocks/{corp_code}` **960px** — the pair exactly.
- **`.orbits` is `display: none` at ≤767** (no orbiting star, no rings) while **240** twinkling stars
  remain and the hero's h1 sits at the same offset; at 1280 both render. The **served CSS carries no
  `offset-distance` and no `offset-path`**, and `@keyframes Hero-module__…__orbit` is **93 translate
  stops** — the recorded number, unchanged.
- **Fonts:** three `notoSansKr Fallback` families declared (Apple · Malgun · Noto), self-hosted
  `NotoSansKR_subset` + three `IBMPlexMono_*_subset` woff2.
- **Cold-cache CLS on production through Cloudflare**, at **412×915 / DPR 2.625 / 4× CPU / ≈1.6 Mbps /
  150 ms with the cache disabled**: **CLS 0, zero `layout-shift` entries at all** (`n = 0`, not a
  filtered zero — no typing preceded it, so P12's `hadRecentInput` trap does not apply), with the
  fonts observably loading during the window. That also corroborates the P12.F9 mono-reflow line.
- **Event detail:** 정정 이력 ↔ 접기 × keeps **one width, 77.53 px**, across the toggle, with
  `aria-expanded` flipping — the recorded number.
- **`/events/<nonexistent>` → 404 (not 500) with the path echoed, in all three runtimes.** Landing
  document: `grep -c window_state` **0**, **289,292 bytes**. `이 마감 알림 받기` is in the **server**
  HTML on dev and on production.
- **Auth (P8 block, re-run because P13 rewrote this surface):** an empty submit on 로그인 renders
  「이메일과 비밀번호를 입력해 주세요.」 with **0 requests** and no browser bubble; a malformed address
  with a password renders 「이메일 주소 형식이 올바르지 않습니다.」; **no `required` and no `pattern`**
  on any auth input; the primary is **48px** high with nothing under 44px; `Auth.module.css` has
  **exactly one** media query; 로그아웃 lands on `/auth/login` with 「로그아웃되었습니다」 **once**,
  above the h1.
- **Portfolio (signed in, through the new gate):** 변경 · 로그아웃 · 계정 삭제 share one right edge
  (**901** ×3); 로그아웃 / 계정 삭제 / 취소 are one box size (**104×32**); 「계정을 삭제하면 …」 is
  **absent → present when armed → absent after 취소**. The account caret is **one rect
  (5.67×12 @ x 1161.33)** across click and Escape.
- **`/ask` structure (free half):** **four** cards in **two even rows** (2 at y 372, 2 at y 443, no
  orphan), 익명 줄 **0**, 새 대화 **0** until a thread exists then present, 「범위:」 칩 **0**, `main
  aside` **0** at 1440. **`conversation_feedback` was 8 before the sweep and 8 after** — pressing a
  start card still writes nothing.
- **`/ask` behaviour (the 2 model calls spent):** the 이벤트 검색 card → one flat 도구 행, inline
  sentences with **0 `<br>`**, **근거 5건** matching 5 chips, the footer's five `rcept_no` + the KST
  stamp, **no 「다시 질문」**, **no 「미확인」**, and `[role=status]` **0** at the terminal. The 계산 card
  → 도구 흐름 이벤트 검색 → 이벤트 읽기 → 계산 (so `get_event` is demonstrated inside it), a
  **검증된 계산** block with exactly **one 「입력」** marker, the 식 line
  `1,000주 × 1.4995844901 = 1,499주`, a `--live-tint` result row marked 계산, and **근거 2건** — the
  calculation's *result* not counted.
- **`make smoke-prod` 17/17** covers the redirect, robots, sitemap, manifest, OG, noindex,
  third-party-origin and co-tenant lines; the third-party check was re-confirmed in a real browser on
  production (only `static.cloudflareinsights.com`, the operator-enabled edge-injected beacon).
- **Box:** `MIJUAL_EXTRACT_MAX_CALLS` is **300** in worker, api **and** beat; `edge-nginx` `StartedAt`
  **`2026-07-02T19:22:12.325478595Z`**, unchanged; `deploy/backups/` is mode **700** holding mode-600
  dumps, newest **~13 h old** (`mijual-20260905T040001Z.dump`).

**The 19 lines not re-run, each with its reason:**

- **18 of them are the paid model-call lines** across the P8 ask-boundary and P9 blocks — L121
  (범위 밖), L122 (회사 미특정), L123/L124 (계산 block frames, though the 계산 card's *rendered* result
  was checked), L125 (주입 시도), L126 (도구 4개 이상 + 폴드), L128 (미확인 marker), L129 (소진 턴),
  L130's remaining two cards, L132's empty-and-reload half, L134 (widget/page parity), L135 (stored
  block frames), L137 (칩 in all three places), L316, L332, L346, L374, L381, and the production
  streaming line L440. The plan budgeted 6 dev + 1 production; **I stopped after 2 dev and 0
  production on the operator's instruction** (§ 6.3). What replaces them is proof of the blast radius
  rather than payment: `git diff --stat e88f629..HEAD -- src frontend` shows P13 touched **11 files,
  all of them auth or mail** — `components/auth/{AuthPanel.tsx,copy.ts,Auth.module.css}`,
  `lib/{api.ts,types.ts,auth.test.ts}`, `src/mijual/{db/models.py,mail.py,mailcopy.py,web/auth.py,web/routers/auth.py}`.
  **Nothing under `src/mijual/agent`, `src/mijual/gates` or `frontend/components/ask` changed at all**,
  and the free structural half of the `/ask` lines (card count, row parity, absent affordances, thread
  geometry, the feedback-row count) was re-run and passed. These lines cannot have gone stale from
  P13's code.
- **L468 — the D-day mail demo** (`scheduler once --stages notify --notify-today …` on the box). Not
  re-run **deliberately**: it sends real mail from production and writes, and this review is read-only
  on the box beyond the one named write. Operator-run.

**The P13 block appended to `## Regression Checklist`** (the stage-4 append, written as qa `v0019`):

```
- [ ] 가입 인증: 계정 만들기 answers 201 with **no session and no cookie**, mails a 6-digit code, and the code appears in **no** response body — measured on dev, on the local production build and on production (P13)
- [ ] 인증번호 상태: the code step is a **state of the same panel**, not a route — 이메일 인증 + the normalized address + the 10분 window, one `#auth-code` field (`type=text` · `inputMode=numeric` · `autocomplete=one-time-code` · `maxLength=6` · `tabular-nums`, focused on entry), 확인 · 인증번호 재전송 · a way back wearing the origin mode's own name; **382×48 at 1280 and 324×48 at 390**, identical in all three runtimes (P13)
- [ ] 5회 소진: five wrong codes over **HTTP** end the grant — 불일치 ×4 then the fifth answers 만료, the genuinely mailed code is dead too, and the row persists **`attempts = 5`**. The cap was inert between P13.S1 and P13.F1 because the increment was rolled back with its own 400; a write-session fixture that never rolls back cannot see it (P13)
- [ ] 재전송 쿨다운: 재전송 (and a re-signup) inside 60 s mails **nothing** and answers `resent: false` as a 알림 line, never an error, with the same `expires_at`; past it, `resent: true` and a fresh code that supersedes the old one. The cooldown outranks every caller (P13)
- [ ] 미인증 로그인: 로그인 with the **right** password on an unverified account opens no session and routes to the same code step — and mints **no second code** when a live one exists (the `expires_at` comes back identical) (P13)
- [ ] 재설정이 인증한다: a completed 비밀번호 재설정 on an unverified account clears `verification_pending_since` — the mailbox was proven (P13)
- [ ] 기존 계정 무영향: every pre-existing account still logs in unchanged; the grandfathering is the column's shape, measured on production **before any write** as `3|0` — 3 accounts, 0 pending, with no data step run (P13)
- [ ] 6자리 클라이언트 게이트: a short or empty 인증번호 is answered on the surface — 「인증번호 6자리를 입력해 주세요.」 — and **no request leaves the browser** (P13)
- [ ] 프로덕션 SMTP: a real 가입 puts a real code through `mail.privateemail.com:587` — `smtp mailer: sent signup_verification` in the api log, and the transport line reads `smtp …`, never `console` (P13)
```

### C.5 — every `## Operator Questions` entry, routed

| # | entry (source) | routing |
|---|---|---|
| 1 | The production proof needs a real mailbox — confirm `leetusik+p13@gmail.com` and the disposal (DECOMP) | **walkthrough** — items **1** (the operator finishes the proof themselves) and **4a** (disposal, theirs to decide) |
| 2 | Every new Korean string is drafted, never signed — literal approval (DECOMP) | **walkthrough** — item **3**, all fourteen strings numbered and verbatim |
| 3 | The 5-attempt cap does not exist in the running product (S2) | **answered — nothing outstanding.** F1 landed before the release, and I re-proved the cap live over HTTP today: `불일치 ×4` → `만료`, row `attempts = 5`. |
| 4 | Should `/ops` mark or hide unverified accounts? (DECOMP) | **deferred job** — the first of the two listed in the verdict block |
| 5 | Answered by the orchestrator: the release waited for F1 (F1) | **answered — nothing outstanding**, and confirmed: production runs `1899111`, which is after `12fbdbe` |
| 6 | One drafted line is untrue in the corner the working cap made reachable (F1) | **walkthrough** — item **4b**, with the three options spelled out |
| — | DECOMP's `for P13.REVIEW` note (a): a janitor for long-dead unverified rows | **deferred job** — the second of the two listed in the verdict block |
| — | DECOMP's `for P13.REVIEW` note (b): the walkthrough must carry every drafted string verbatim | **discharged** — item **3** |

**No entry is unrouted.**

## 5. The walkthrough (verbatim — this is what `accept-gate --open` carries)

```
P13 — Email verification at signup. Production is live at 1899111.
About 10 minutes. Nothing here needs a password you do not choose yourself.

0. ALREADY VERIFIED BY THE REVIEWER TODAY — you do not need to re-check any of it.
   171 backend tests, a clean production build + typecheck + 23/23 frontend smoke.
   The whole gate contract over HTTP: signup opens no session and puts no code in any
   response body; five wrong codes end the grant (the fifth says 만료 and the mailed
   code dies with it, row attempts = 5); 재전송 inside 60 seconds mails nothing; a
   completed password reset verifies the account. On the box: six services up, the
   schema one-shot Exited 0 with "schema ok (+1 columns)", 20 user tables, and the
   mail transport reading smtp mail.privateemail.com:587 — never console. Your three
   pre-existing accounts were measured as 3|0 (none pending) BEFORE anything wrote,
   so nobody who already had an account is affected. make smoke-prod: 17/17.
   I opened jujutower.com myself at desktop and phone widths and drove the 인증번호
   panel there; it measures identically on dev, on a local production build and on
   production.

1. FINISH THE LIVE PROOF YOURSELF  (~3 min)
   P13.S3 registered leetusik+p13@gmail.com on production and left it UNVERIFIED on
   purpose, with its throwaway password deliberately kept out of this public repo. So
   you finish it with a password of your own:

     a. Open  https://jujutower.com/auth/login  →  계정 만들기
     b. Email: leetusik+p13@gmail.com   Password: anything you like (8+ chars)
     c. Press 계정 만들기.

   Signing up again on an address nobody has verified is a re-issue, not a duplicate:
   it replaces the stored password with the one you just typed and mails a fresh code.
   No second account is created.

   YOUR INBOX ALREADY HOLDS FOUR OLD MAILS for that address (01:51, 01:53, 01:58 and
   02:15 KST — three from S3's proof, one from my own check on production). ALL FOUR
   ARE DEAD. Use only the newest one, the one your own 계정 만들기 just triggered.

   If no new mail arrives: you submitted within 60 seconds of a previous send, which
   the cooldown deliberately suppresses. Wait a minute, press 인증번호 재전송, and the
   next mail is yours.

     d. Type the 6 digits → 확인 → you land on 보유 종목, signed in.

2. OPEN IT AND LOOK  (~5 min) — desktop and phone
   Worth trying while you are in there:
     - the 계정 만들기 intro (item 3.1 below) — does it make you look at your mailbox?
     - 확인 with a wrong 6-digit number → the 불일치 line
     - 인증번호 재전송 straight away → the 쿨다운 line (this is item 4b's question)
     - the way back, which wears the name of the mode you came from (계정 만들기 or 로그인)
     - type only two digits and press 확인 → answered on the page, nothing sent

3. APPROVE THE STRINGS, LITERALLY.  Reply "3.N ok" or "3.N change to: …".
   Nothing here is signed yet — this phase drafted all of it inside the R5/R12 voice.

   THE MAIL
     3.1  제목:  [주주의관제탑] 가입 인증번호
     3.2  본문:  가입 인증번호입니다. 아래 6자리 숫자를 입력해 주세요.
     3.3  본문:  이 번호는 {KST 시각}까지 사용할 수 있습니다.
     3.4  본문:  요청하지 않으셨다면 이 메일을 무시해 주세요. 인증하지 않으면 계정은 사용되지 않습니다.
                 (the 6 digits sit on their own line between 3.2 and 3.3)

   THE PANEL
     3.5  제목:      이메일 인증
     3.6  본문:      {email} 주소로 6자리 인증번호를 보냈습니다 — 10분 안에 입력해 주세요.
     3.7  필드 라벨:  인증번호
     3.8  버튼:      확인          (in flight: 확인 중…)
     3.9  재전송:     인증번호 재전송
     3.10 재전송됨:   인증번호를 다시 보냈습니다 — 메일함을 확인해 주세요.
     3.11 쿨다운:     조금 전 보낸 인증번호가 아직 유효합니다 — 메일함을 확인해 주세요.
     3.12 형식:      인증번호 6자리를 입력해 주세요.
     3.13 불일치:     인증번호가 일치하지 않습니다.
     3.14 만료/소진:  이 인증번호는 더 이상 사용할 수 없습니다 — 인증번호 재전송을 눌러 새 번호를 받아 주세요.

   THE ONE RE-DRAFTED SIGNED STRING (its old promise became false under the gate)
     3.15 계정 만들기 intro:
            now:  이메일과 비밀번호만으로 만듭니다 — 인증번호를 메일로 보내 드립니다.
            was:  이메일과 비밀번호만으로 만듭니다 — 만들어지면 바로 로그인됩니다.

4. DECISIONS — reply with a letter each.
   4a. THE PROOF ACCOUNT. Once verified, delete it (계정 삭제 on /portfolio/notifications)
       or keep it standing for your own inspection? Nothing has been deleted.
   4b. STRING 3.14 IN ONE CORNER. Burn all five attempts, then press 재전송 within the
       first 60 seconds: you are told the code is unusable (3.14) and then told the code
       is still valid (3.11). Both sentences are individually true of different things
       and together they contradict. The flow still terminates correctly — wait out the
       minute, press 재전송, type the new number. No backend behaviour is wrong (the
       cooldown outranking every caller is what stops the signup form being a mail
       cannon). Pick one:
         (i)   leave both lines as drafted;
         (ii)  draft a third line for "재전송 under cooldown with no live code";
         (iii) hide 재전송 until the cooldown elapses.
       (ii) and (iii) are each a later frontend slice, not a change to this phase.
   4c. /ops 독자 계정 TABLE. After P13 it silently lists accounts that cannot log in.
       Out of scope by intent, so nothing was built. Say "later" and I file it as a
       deferred job; say "now" and it becomes a phase.
   4d. A JANITOR for long-dead unverified accounts. P13 builds no sweep on purpose (a
       re-signup re-takes any address at any age), so the rows just accumulate. Same
       choice: "later" (deferred job) or "now".

5. THINGS I NOTICED AS A FIRST-TIME READER — not defects, and nothing was changed for
   them. Decide if any is worth a later slice.
   5a. Reload the page mid-code and you are back at a bare 로그인 panel with no hint
       that an account is half-made and a code is waiting in your mailbox. It IS
       recoverable — logging in with the same address and password returns you straight
       to the code step — but nothing on screen says so.
   5b. The 인증번호 state still offers 「샘플 포트폴리오로 둘러보기」 under the way back:
       an exit one tap from the field you are meant to be typing into.
   5c. There is no countdown for the 10분, deliberately — so there is also no way to
       tell how much of it is left while you hunt for the mail.

6. IF SOMETHING IS WRONG, say so plainly and I will record it as a failure and turn it
   into fix slices — the gate resets and the review runs again from the top.
```

## 6. Deviations from `plan.md`

**6.1 — the dev stack was not restarted.** The plan says to restart if the API pid predates F1's
commit `12fbdbe`. It does: the API started **00:47:50** and F1 committed **00:53:25**. But the trigger
is a false positive — F1 restarted the stack *after* editing and *before* committing, and its own HTTP
proof ran against this very process at 00:48 (`var/stack/api.log` shows the five-wrong-code run there).
I replaced the trigger with a stronger check: `find src frontend/{lib,components,app} -newermt
"2026-09-06 00:47:50"` returns **nothing**, and `git status` shows no source edit at all, so the
running process imported exactly the tree under review. Then I proved it behaviourally — A8/A9's cap
measurement (`attempts = 5`) is F1's fix and could not pass on pre-F1 code. Restarting would also have
destroyed `var/stack/api.log`, which is where the codes are read from. (A first attempt to restart was
in any case refused by the sandbox classifier.)

**6.2 — the one sanctioned production write was made twice.** The plan says "do it once". I did it at
1280 and again at 390, because tabs do not survive between `aside repl` invocations and the password I
had minted for the first submit was generated **inside the page** and discarded — deliberately, so no
secret would exist to leak into this public repo — which left the 로그인 route back into the code state
unavailable to me. The cost turned out to be nil: the second submit fell **inside** the 60 s cooldown,
so it mailed nothing, created nothing and superseded nothing (production went `4|1` → `4|1`, one grant,
`attempts 0`). Net effect on the operator: **one** extra mail, not two, and the walkthrough names the
count. I should have planned the two viewports as one invocation.

**6.3 — the paid model-call sweep was stopped at 2 of 7 budgeted calls.** The plan budgeted 6 dev and
1 production for the checklist's AI 질문 lines. After 2 dev calls the operator asked, mid-review, why
`/ask` was being tested when it is not in P13's range. It is a fair challenge: the stage-4 rule ("re-run
the *whole* list") exists to catch shared-surface drift, and `/ask` shares no surface with this phase.
I stopped, and replaced payment with proof — the `git diff --stat` blast radius in § C.4 shows P13
touched 11 files, all auth or mail, and none under `src/mijual/agent` or `frontend/components/ask`. The
free structural half of those lines was re-run and passed, and the 18 behavioural lines are recorded as
not re-run with that reason attached rather than quietly marked green.

## 7. What was left behind

- **Production:** one unverified account at the proof address (`4|1`, id 41), **one** live grant
  (id 4, `attempts 0`, expired 02:25:05 KST — the operator's own 계정 만들기 mints a fresh one), and
  **four** now-dead codes already mailed. Nothing on the box was edited, `.env.prod` was never touched,
  `/ops` was never logged in to, no container was rebuilt, restarted or stopped, and nothing deployed.
- **Dev:** the stack is up on the same pids it was found on (api 46137, web 46149, postgres 6 days).
  Every throwaway account is gone — `select email from account where email like 'p13-%'` is empty and
  the DB is back to its original `2|0`. `conversation_feedback` is 8, as before.
- **The local production build** was served on 3014 for the runtime check and **stopped** (the port no
  longer answers); the copied tree lives outside the repo in session scratch and never touched
  `frontend/.next`.
- **Instrument:** Aside on `u2` throughout, fifteen invocations. No `aside mcp` registration was made,
  `aside account use` was never called, and the operator's `u0` profile was never driven.
</content>
</invoke>
