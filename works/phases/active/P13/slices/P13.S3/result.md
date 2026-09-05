# Result — P13.S3 (release to production + the live proof of the verification mail)

- **status:** done
- **summary:** P13 is live on `https://jujutower.com` at `1899111` — both images rebuilt, the schema
  one-shot reported **`schema ok (+1 columns)`** and user tables went **19 → 20**, and the
  grandfathering was measured **before anything wrote**: **3 accounts, 0 pending**, so every
  pre-existing production account arrived verified by the column's shape alone. A real signup on
  production answered **201 with no cookie** and put a real 6-digit code through
  `mail.privateemail.com:587` (three `smtp mailer: sent signup_verification` lines); login on the
  unverified account, the wrong-password 401s, the wrong code and the resend cooldown were all
  proven live, and the 인증번호 panel was driven in Aside (`u2`) against the public origin at 1280
  and 390. `make smoke-prod` 17/17 before **and** after; the four R7 no-harm assertions identical.
  **The proof account stands unverified with a fresh grant and all 5 attempts** — the operator
  enters the code at the gate.
- **files_changed:**
  - `works/phases/active/P13/slices/P13.S3/result.md` (this file)
  - `works/phases/active/P13/phase.md`
  - No source file was touched. Nothing was edited on the box; `.env.prod` was neither read nor
    written; nothing was pushed, bundled or `scp`'d.
- **validation:**

  | check | reading |
  |---|---|
  | **gate 1 — the push** | **OPEN.** `git fetch origin`; `HEAD` = `origin/main` = **`1899111`**, `merge-base --is-ancestor` true, `origin/main..HEAD` **empty** |
  | **gate 2 — the freeze** | **OPEN.** `TZ=Asia/Seoul date` → **2026-09-06 01:46:17 KST**, ~33 h before the 2026-09-07 11:00 KST freeze |
  | `make smoke-prod` **before** | **pass** — 17 pass · 0 fail · 11.2 s |
  | box HEAD before | **`004d936`** (the P12 release), clean tree; box clock 16:46 UTC = 01:46 KST |
  | pre-release `ps` / tables / transport | six services up · **19** user tables · `mail transport: smtp mail.privateemail.com:587 tls=starttls` |
  | quiet point | `celery inspect active` → **`- empty -`**, 1 node; last pipeline `daily-evening` succeeded **19:31 KST**; next beat 07:30 KST (≈5.6 h out) |
  | `deploy/deploy.sh` | **pass** — `DONE — released at ref origin/main`, **`grep -c ROLLBACK` = 0** |
  | box HEAD after | **`1899111`** |
  | `mijual-schema` | **`schema ok (+1 columns)`**, container **Exited (0)** |
  | user tables after | **20** (`email_verification` created by `create_all` in the same run) |
  | **grandfathering (before any write)** | **`3\|0`** — 3 accounts, **0** with `verification_pending_since` |
  | `POST /api/auth/signup` (live) | **201**, **0 `Set-Cookie`**, `{"verification":{"email":"leetusik+p13@gmail.com","expires_at":"2026-09-06T02:01:15+09:00"}}` |
  | the mail left the box | **`2026-09-06 01:51:17,619 mijual.mail INFO smtp mailer: sent signup_verification`** |
  | `POST /api/auth/login` right pw | **200**, **0 cookie**, `{"verification_required":true,…"expires_at":"2026-09-06T02:01:15+09:00"}` — **identical `expires_at`, so no second code was minted** |
  | `POST /api/auth/login` wrong pw | **401** `invalid_credentials` |
  | `POST /api/auth/verify` `code:"000000"` | **400** `verification_code_invalid` |
  | `POST /api/auth/verify/resend` (cooldown elapsed) | **200** `{"resent":true,…"02:03:38"}` + a second `smtp mailer: sent` at 01:53:41 |
  | `POST /api/auth/verify/resend` (3 s later, **inside** the cooldown) | **200** `{"resent":false,…"02:03:38"}` — same `expires_at`, **no mail** |
  | `POST /api/auth/verify/resend` wrong pw | **401** `invalid_credentials` |
  | `POST /api/auth/login` **nonexistent** address | **401** `invalid_credentials` — byte-identical body to the wrong-password 401 |
  | Aside `u2` @ **1280** (production origin) | **pass** — 로그인 on the unverified account renders 이메일 인증; field `type=text` `inputMode=numeric` `autocomplete=one-time-code` `maxLength=6` h **48** `tabular-nums` **focused**; 확인 48 / 인증번호 재전송 44 / the way back labelled **로그인**; wrong code → 「인증번호가 일치하지 않습니다.」; 2-digit → 「인증번호 6자리를 입력해 주세요.」 with no request |
  | Aside `u2` @ **390** (production origin) | **pass** — 계정 만들기 on the same unverified address renders the same state; field **324×48**, submit **48**, `docW 390 = viewW 390`, `tabular-nums`, the way back labelled **계정 만들기**; the re-drafted intro renders; 재전송 inside the cooldown → 「조금 전 보낸 인증번호가 아직 유효합니다 — 메일함을 확인해 주세요.」 |
  | `make smoke-prod` **after** | **pass** — 17 pass · 0 fail · 11.8 s |
  | R7 no-harm ×4, before vs after | **identical** — co-tenants 200 ×3, `edge-nginx StartedAt 2026-07-02T19:22:12.325478595Z`, 80/443 owned by `edge-nginx`, **28** containers; in-network `/api/health` `{"status":"ok"…}` |
  | api log since the release | **no error, no traceback** (the four `grep -i error` hits are `uvicorn.error` **INFO** lines) |
  | `python3 scripts/workflow.py validate` | **pass** — *Workflow validation passed*; three pre-existing advisories (`consolidation_owed=P4, P12`, `stale_docs=…`, `oversized_doc_sections=11`), all docs-phase items unrelated to this slice |

- **deviations:** five, all recorded in §5 below — the resend cooldown had to be re-created (a
  second mail), the browser sweep ran **both** routes into the code state rather than only 계정
  만들기 (a third mail), the final grant therefore carries **0** spent attempts instead of the
  planned 1, the throwaway password is deliberately **not written into this public repo**, and one
  1280 geometry number was mis-selected and is reported as not-measured rather than as a value.
- **doc_impact:** three lines appended to `phase.md` — `operations.md`, `qa.md`, `security.md`.

---

## 1. The two gates

Both re-run at the start of this dispatch, as the plan requires — the orchestrator had set the slice
`pending` on a closed push gate at 2026-09-06 00:53 KST.

```
HEAD        1899111
origin/main 1899111
git merge-base --is-ancestor HEAD origin/main   → true
git log --oneline origin/main..HEAD             → (empty)
TZ=Asia/Seoul date                              → 2026-09-06 01:46:17 KST
```

The operator's push landed. The freeze opens 2026-09-07 11:00 KST, so the release had ~33 h of
clearance; nothing below is a workaround of either gate.

## 2. The release

```sh
ssh oracle-cloud 'cd /home/opc/Mijual && nohup deploy/deploy.sh > var/deploy-20260905T164746.log 2>&1 < /dev/null &'
# launched pid=3367181, 2026-09-06 01:47:46 KST (16:47:46 UTC — the box clock is GMT)
```

Log `/home/opc/Mijual/var/deploy-20260905T164746.log`, **322 lines**:

| step | evidence |
|---|---|
| checkout | `HEAD is now at 1899111 chore(p13): S3 planned and pending …` |
| rollback points | `tagging mijual-api:latest -> mijual-api:previous`, `… mijual-web …` |
| **both images built** | `#37 naming to docker.io/library/mijual-api:latest done`, `#42 naming to docker.io/library/mijual-web:latest done` — the backend changed this time, so unlike P4.S10/P12.S2 the api image is **not** a cache hit |
| recreate set | `mijual-schema`, `mijual-beat`, `mijual-api`, `mijual-web`, `mijual-worker` all Recreated; `postgres` and `redis` untouched |
| schema one-shot | `mijual-schema` **Exited (0)** |
| health gate | `mijual-web healthy on poll 7`, `mijual-api healthy on poll 1`, `deploy healthy — mijual-api:latest + mijual-web:latest are live` |
| edge assertion (in-script) | `ok — edge-nginx StartedAt unchanged (2026-07-02T19:22:12.325478595Z)` |
| final | `DONE — released at ref origin/main`; `grep -c ROLLBACK` → **0** |

Because **both** images were rebuilt, `deploy/rollback.sh` is a genuine two-image rollback point
this time (back to the P12 release `004d936`), not the half no-op the frontend-only releases left.

## 3. The schema step and the grandfathering — the unrepeatable evidence

```
docker compose -f compose.prod.yml logs mijual-schema
  → mijual-schema-1  | schema ok (+1 columns)

select count(*) from pg_stat_user_tables;        → 20      (was 19 before the release)
select count(*) from email_verification;         → 0
select count(*), count(*) filter (where verification_pending_since is not null) from account;
  → 3|0
```

**`3|0`, captured before the test signup and before anything else wrote.** Three pre-existing
production accounts, **zero** with a pending stamp — the grandfathering, exactly as the notebook's
§ *Schema* predicted: a property of the column's shape, with no data step run and none needed. This
is the reading that cannot be taken again.

`+1 columns` is the schema one-shot's **first additive column on production**; the new table came
from `create_all` in the same run, which is why the count moves 19 → 20 while `ensure_columns`
reports only the one column.

Transport re-confirmed after the release:

```
2026-09-06 01:48:28,915 mijual.web.app INFO mail transport: smtp mail.privateemail.com:587 tls=starttls from=주주의관제탑 <hi@hi2vi.com>
```

Never `console`.

## 4. The live proof

Signup at **01:51:15 KST** through the public origin with the CSRF header, at the proposed proof
address `leetusik+p13@gmail.com` (see §5.4 on the password):

```
HTTP/2 201 · Set-Cookie count 0
{"verification":{"email":"leetusik+p13@gmail.com","expires_at":"2026-09-06T02:01:15+09:00"}}
```

and, on the box, the line that proves a real mail left over the live SMTP account:

```
2026-09-06 01:51:17,619 mijual.mail INFO smtp mailer: sent signup_verification
```

Per the secrets rule that line carries no address and no subject, and none was looked for.
**Receipt is the operator's to confirm** — that is the gate.

The rest of the contract, proven without the code:

| call | reading |
|---|---|
| `login` right password | **200**, no cookie, `verification_required: true`, `expires_at` **02:01:15 — identical to signup's**, so the "issue only when no live one exists" branch is live: no second code, no second mail |
| `login` wrong password | **401** `{"error":{"code":"invalid_credentials","message":"email or password is wrong"}}` |
| `login` **nonexistent** address | **401**, the **same bytes** — uniform, per R5 |
| `verify` with `code:"000000"` | **400** `{"error":{"code":"verification_code_invalid","message":"verification code is wrong"}}` |
| `resend` at 01:53:38 (cooldown elapsed) | **200** `{"resent":true,…"expires_at":"2026-09-06T02:03:38+09:00"}`, mail logged 01:53:41 |
| `resend` at 01:53:41 (**inside** the fresh cooldown) | **200** `{"resent":false,…"expires_at":"2026-09-06T02:03:38+09:00"}` — same grant, **no third mail from this pair** |
| `resend` wrong password | **401** `invalid_credentials`, uniform with login |

The grant row confirms the supersede-on-repeat rule: after the resend there was exactly **one** row
(`id 2`), the earlier one deleted, `attempts 0`, `used_at` null.

### The panel, live on production (Aside `u2`, `aside repl --account u2`)

Instrument: **Aside**, agent account **`u2`** (profile 「claude2」) — never `u0`, never
`aside account use`. Runtime and access path: `## Operator Runtime` § *Production* —
`https://jujutower.com` through Cloudflare → `edge-nginx` → `mijual-web`, which **is** a production
Next build, so no separate production-build check is owed.

**1280 — the 로그인 route** (chosen first precisely because it mints nothing while a grant is live,
so it cost no mail): the right password on the unverified account lands on 이메일 인증 without
leaving `/auth/login`.

- field `#auth-code`: `type=text`, `inputMode=numeric`, `autocomplete=one-time-code`,
  `maxLength=6`, height **48**, `font-variant-numeric: tabular-nums`, **focused on entry**
- buttons 확인 (48) · 인증번호 재전송 (44) · the way back wearing the **origin mode's own name**, 로그인
- label 인증번호; intro 「leetusik+p13@gmail.com 주소로 6자리 인증번호를 보냈습니다 — 10분 안에 입력해 주세요.」
- a wrong 6-digit code → 「인증번호가 일치하지 않습니다.」, still on the code field
- a **2-digit** code → 「인증번호 6자리를 입력해 주세요.」 — the client gate, no request

**390 — the 계정 만들기 route** on the same unverified address (the re-issue branch, live):

- the re-drafted intro renders on production: 「이메일과 비밀번호만으로 만듭니다 — **인증번호를 메일로 보내 드립니다.**」
- the code state: field **324×48**, submit **48**, `docW 390 = viewW 390` (no horizontal scroll),
  `tabular-nums`, the way back labelled **계정 만들기** — every one of these is the value S2 measured
  on the dev stack and the local production build, so production agrees with both
- 재전송 **inside** the cooldown → 「조금 전 보낸 인증번호가 아직 유효합니다 — 메일함을 확인해 주세요.」

Screenshots (evidence, outside the repo — `var/` is gitignored):
`var/p13/prod-code-state-1280.png`, `var/p13/prod-code-state-390.png`.

**What happened on the re-signup, since the plan asked which branch fired:** it was **outside** the
60 s cooldown, so it **superseded** the grant and mailed — the third and last mail.

## 5. Deviations

1. **The resend cooldown had to be re-created, which cost a second mail.** The plan's step 4 asks
   for `resent: false` *inside* the cooldown, but the 60 s window from the 01:51:15 signup had
   already elapsed by the time the four probes ran. Rather than skip the check, the resend was
   issued **twice**: once outside the window (`resent: true`, a new grant at 02:03:38, one mail) and
   again three seconds later, inside the fresh window (`resent: false`, the **same** `expires_at`,
   no mail). Both halves of the contract are therefore proven on production instead of one.
2. **The browser sweep ran both routes into the code state, not only 계정 만들기.** The plan named
   the signup route; the 로그인 route was added *first* because it mints nothing while a grant is
   live, so the desktop pass cost no mail at all, and it proves the second headline claim of the
   phase (「로그인 with the right password on an unverified account routes to the code step」)
   directly on production. 계정 만들기 then ran at 390 and superseded, as the plan anticipated. An
   addition, not a substitution.
3. **The final grant carries 0 spent attempts, not the 1 the plan predicted.** Two wrong codes were
   spent (one by `curl`, one through the panel), but each was spent on a grant that a later
   supersede deleted. The row the operator will meet is **`id 3`, created 01:58:41 KST, unused,
   `attempts 0`** — so **all five attempts remain**, not four. The plan's walkthrough note is
   corrected accordingly in `phase.md`.
4. **The throwaway password is not written into this repo.** `deploy/runbook.md` R6 records that
   this repository is public and that no credential sits in it, so the password lives only in this
   dispatch's scratchpad and in the structured return handed to the orchestrator. The gate
   walkthrough is built around a route that needs **no** secret to travel: 계정 만들기 on the same
   address re-issues **and replaces the password hash with the one just typed** (the notebook's
   § *API contract*, proven live at 390 above), so the operator can finish the proof with a
   password of their own choosing.
5. **One 1280 number is not a measurement.** The panel-width probe selected `form.closest('div')`,
   which resolved to a full-width wrapper and reported `1280`; it is a bad selector, not a geometry
   regression. The 390 pass selected the field directly and matched S2 exactly (324×48, submit 48),
   and no layout anomaly was visible in either screenshot. Reported as not-measured rather than as
   a value.

## 6. What existing accounts could and could not be proven

The plan is right that little is provable without a credential this slice does not hold, and none
was sought. What stands:

- **`3|0` before any write** — every pre-existing account carries a NULL stamp and is therefore
  verified. That is the whole grandfathering claim, measured on the production database.
- **The uniform 401** for a nonexistent address is unchanged, byte-identical to the wrong-password
  401 on the same route.
- No login as the operator was attempted, `/ops` was not opened, and `.env.prod` was neither read
  nor written.

## 7. The state production was left in

- **Released:** `1899111`, both images rebuilt, six services healthy, `mijual-schema` Exited (0).
- **One unverified account** at `leetusik+p13@gmail.com` (account id 41) — `4|1` accounts / pending.
- **One live grant**, `email_verification id 3`: created **2026-09-06 01:58:41 KST**, expires
  **02:08:41 KST**, `used_at` null, **`attempts 0`**. It will have expired long before the operator
  reads this, which is fine and is handled in the walkthrough note: 인증번호 재전송 (or 계정 만들기
  again) issues a fresh one.
- **Three mails** were sent to the proof address (01:51:17, 01:53:41, 01:58:43). Only the last
  code was ever live; the first two died with their grants.
- Nothing else on the box was touched: no edit, no `.env.prod` access, no `rollback.sh`, no `/ops`
  login, no account other than the proof address.
- Disposal of the proof account is the operator's call at the gate — it is routed as an open
  question in `phase.md` and in the note tagged `for P13.REVIEW`.
