# P4.S2 — result

- **verdict:** `done`
- **summary:** The mail seam is filled: a stdlib `SmtpMailer` with an explicit TLS policy, a
  `render` step over the new `mijual.mailcopy` (every Korean string, one provenance comment each),
  a `mijual.notify` sender that reads each reader's 알림 설정 and their own portfolio composition,
  a `notification_send` idempotency table (19 tables), and a `notify` pipeline stage on **its own
  lock** behind a new 08:30 KST `notify-deadlines` beat entry. D7 (`PUT /portfolio/notifications`)
  is now an upsert and D23's subject is re-signed to 주주의관제탑. Proven live end to end against a
  local `aiosmtpd` sink — a real reset mail and two real D-day mails off the dev corpus (① and ②),
  idempotency, the off switch and the ceiling — then every throwaway row and process removed.
- **files_changed:**
  - `src/mijual/mail.py` (rewritten), `src/mijual/mailcopy.py` (new), `src/mijual/notify.py` (new)
  - `src/mijual/config.py`, `src/mijual/db/models.py`, `src/mijual/beat.py`
  - `src/mijual/scheduler/config.py`, `src/mijual/scheduler/pipeline.py`,
    `src/mijual/scheduler/app.py`, `src/mijual/scheduler/__main__.py`
  - `src/mijual/web/app.py`, `src/mijual/web/portfolio.py`
  - `.env.prod.example`
  - `tests/test_notify.py` (new), `tests/test_web_portfolio.py`, `tests/test_web_ops.py`
  - `works/phases/active/P4/phase.md`, `works/phases/active/P4/slices/P4.S2/result.md`
- **validation:** all pass — see *Verification* below for the commands and their output.
- **deviations:** three, all small and stated below (§ *Deviations*).
- **doc_impact:** six lines appended to `phase.md` § *Doc impact* — `backend`, `security`,
  `operations`, `product`, `data`/`architecture`, and an explicit "`api`: no contract change".
- **escalation:** none.

---

## What landed

Ten pieces, in the order they depend on each other. The reasoning for each lives in the code's own
docstrings (they are long on purpose in this codebase); this is the map.

1. **`mijual.mailcopy` (new).** Every Korean string a mail carries, each with a provenance comment
   in one of two forms: **signed** (transcribed from R5's build prompt § 알림 and its round record
   § *Proposed copy → Notify*) or **drafted P4.S2** (goes to the operator literally at the gate —
   the route `intent.md` fixes for new copy in this phase). It is stdlib-only and contains the
   whole body assembly, so `mijual.mail` and `mijual.notify` contain **no Korean sentence at all**.
2. **`mijual.mail` (rewritten).** `DEADLINE` kind, `Rendered`, `render(message)`, `MailError`,
   `SmtpMailer`, `mailer_for(settings)`, `describe_transport(settings)`. `ConsoleMailer` and the
   `Message`/`Mailer` seam are unchanged in shape. TLS: 465 → `SMTP_SSL`, anything else → STARTTLS
   **required** (refused, never downgraded), `none` only when set explicitly. 10 s connect/socket
   timeouts. CR/LF stripped from every header value. One connection per batch
   (`open`/`close`/context manager), `login` only when the server advertises AUTH — which is what
   lets the same code path drive a no-auth local sink and a real provider. A send failure raises
   `MailError` carrying a **type name and an SMTP code only**: `smtplib` routinely quotes the
   rejected recipient back at you and this error travels into logs and a stage summary.
   **No HTML alternative**, deliberately: an HTML part invites a logo, a web font and a tracking
   pixel — third-party fetches performed by a reader's mail client on this product's behalf, which
   is exactly the measured property `security.md` signs for pages.
3. **`mijual.notify` (new).** Selection reuses the reader's own surface exactly:
   `lead_days_of` → `load_portfolio(..., today=)` → `upcoming` rows whose `countdown.days` is one
   of that reader's chips. Per-message failure containment, a `_Batch` that opens the SMTP
   conversation **lazily on the first actual send** (a day with no candidate costs no login, and a
   misconfigured host does not fail a stage that had nothing to send), and a `NotifyReport` of
   counts with no address, no subject and no Korean in it.
4. **`NotificationSend` (new table, 19 total).** Unique on
   `(account_id, event_id, lead_day, anchor_date)`; `rcept_no` beside the key, not in it (an
   `rcept_no` mutates to its newest version on a 정정, N2). Written **after** the transport accepted
   the message and **committed per message**. ORM `cascade="all, delete-orphan"` on `Account` as
   well as the FK `ondelete`, because SQLite does not enforce foreign keys — the same pair every
   other reader-owned table uses, and the reason 계정 삭제 provably wiped the rows below.
5. **`stage_notify` + `STAGE_FUNCTIONS["notify"]`,** `PipelineConfig.notify_max_mails` (200) and
   `notify_today`, and the split of `STAGES` (now seven, the known set) from **`DEFAULT_STAGES`**
   (still the six corpus stages) so the 07:30/19:30 runs did not grow a mail step.
6. **`mijual.beat`:** `NOTIFY_LOCK_NAME = "notify"`, `NOTIFY_MAX_MAILS = 200`, and the
   `notify-deadlines` entry at **08:30 KST daily** → `mijual.notify_deadlines`.
7. **`mijual.scheduler.app`:** the `mijual.notify_deadlines` task, defaulting `lock_name` to the
   notify lock.
8. **CLI:** `--notify-today YYYYMMDD` and `--notify-max-mails`; `--stages` now offers `notify` but
   defaults to the six.
9. **D7 — the upsert.** `set_lead_days` keeps the read, then inserts inside a `begin_nested()`
   savepoint and, on `IntegrityError`, re-selects and updates. Dialect-neutral on purpose (one code
   path on Postgres and SQLite) rather than an `ON CONFLICT`; the API contract is unchanged.
10. **`Settings`:** `smtp_host/port/user/password/from/tls`, `smtp_tls_mode()`, `require_smtp()`,
    `smtp_password` masked in `__repr__` — **and `database_url`'s password masked too**
    (`mask_url_password`, S1's finding, the one hole left in "printing settings cannot leak a
    secret"). `create_app` now picks the transport from settings and logs **one** INFO line naming
    it.

**D23 is done and the retired name is gone from every rendered surface.** `grep -rn 미주알 src/
frontend/` now returns only *comments and citations* — `mailcopy.py` quotes R5's original subject
in a provenance comment, and the rest are pre-existing prose in docstrings and JSX comments. No
string the product renders, in the browser or in a mail, contains it.

## Verification

Every command run, and what it did.

| # | command | outcome |
|---|---|---|
| 1 | `.venv/bin/python -m pytest` | **165 passed** (6 new in `tests/test_notify.py`, +1 in `test_web_portfolio.py`) |
| 2 | `cd frontend && npm run typecheck` | clean (`tsc --noEmit`, no output) |
| 3 | `cd frontend && npm run smoke` | **22/22 pass**, 0 fail — including the two `opsRuns` beat-join tests |
| 4 | `python3 scripts/workflow.py validate` | `Workflow validation passed` (only the pre-existing `oversized_doc_sections=11` warning) |
| 5 | `.venv/bin/python -m mijual.scheduler schedule` | **four** entries; `notify-deadlines  mijual.notify_deadlines  <crontab: 30 8 * * *>` with `kwargs {'stages': ['notify'], 'label': 'notify-deadlines', 'trigger': 'beat', 'lock_name': 'notify'}`; `tasks` lists `mijual.notify_deadlines` |
| 6 | `make db-ensure` | `schema ok` |
| 7 | table count through SQLAlchemy `inspect` | **19**, `notification_send` present |

**Instrument: `curl` + a local `aiosmtpd` SMTP sink. No browser run was made and none is claimed.**
No real mail was sent: `SMTP_HOST=127.0.0.1:8025` throughout, and the sink saw **4 messages, all 4
addressed to `p4s2-throwaway@example.invalid`**. The first real send is a gate/S4 action with the
operator's credentials on the box.

### The live rig

```
uvx aiosmtpd -n -l 127.0.0.1:8025 -c aiosmtpd.handlers.Debugging stdout   # sink (pid killed at the end)
SMTP_HOST=127.0.0.1 SMTP_PORT=8025 SMTP_TLS=none SMTP_USER=x SMTP_PASS=x \
SMTP_FROM="주주의관제탑 <hi@hi2vi.com>" MIJUAL_SESSION_SECRET=<throwaway> \
MIJUAL_OPS_ID=<throwaway> MIJUAL_OPS_PASSWORD=<throwaway> \
.venv/bin/python -m mijual.web --host 127.0.0.1 --port 8011      # my own API, dev database
```

Startup line, verbatim — this is what a deploy reads to know which transport it got:

```
2026-09-02 07:54:16,951 mijual.web.app INFO mail transport: smtp 127.0.0.1:8025 tls=none from=주주의관제탑 <hi@hi2vi.com>
```

**Dead end, 10 minutes:** bare `uvx aiosmtpd -n -l …` accepted mail and printed nothing —
`PYTHONUNBUFFERED=1` did not help either, and the flush-on-exit theory was wrong. The default CLI
handler does not write message bodies to stdout; the explicit
`-c aiosmtpd.handlers.Debugging stdout` does. Use that form.

### (a) The password-reset mail — now real

`POST /auth/reset/request` (note: the path is `/auth/reset/request`, **not** `/auth/reset-request`)
→ `200`, `mijual.mail INFO smtp mailer: sent password_reset`. Captured and decoded from the sink:

```
From   : 주주의관제탑 <hi@hi2vi.com>
To     : p4s2-throwaway@example.invalid
Subject: [주주의관제탑] 비밀번호 재설정

비밀번호 재설정 링크입니다. 아래 주소를 열어 새 비밀번호를 설정해 주세요.

http://127.0.0.1:3010/auth/reset?token=boQUcCwcvaXW7wEmLqWkc36vbrREcgW6M5z-WlN5UPA

이 링크는 2026-09-02 08:55 (KST)까지 사용할 수 있습니다.
요청하지 않으셨다면 이 메일을 무시해 주세요. 비밀번호는 그대로입니다.
```

(The subject and the display name arrive RFC 2047 base64-encoded, decoded here; the body is
`text/plain; charset=utf-8`, base64 transfer-encoded. `EmailMessage` does that on its own.)

### (b) The D-day mails — real corpus events

Two holdings on the throwaway account, from `GET /board`: **툴젠** (① `20260806000329`, 매매 마감
2026-09-07) and **제이에스링크** (② `20250902000288`, 전환청구 개시 2026-09-03), 500주 each.

```
$ python -m mijual.scheduler once --stages notify --no-lock --label smoke-notify --notify-today 20260831
notify   : anchor 2026-08-31 | transport smtp 127.0.0.1:8025 tls=none from=주주의관제탑 <hi@hi2vi.com>
         | 2 account(s), 1 candidate(s) -> sent 1, already-sent 0, skipped-no-chips 0, failed 0 [0.2s]
spend     : 0 OpenDART request(s), 0 LLM call(s), ▷ $0.0000 estimated  |  0.3s total
```

The ① mail, verbatim from the sink — **발행가 상태, no won amount, the 배정 conversion, both links,
the 출처 and 해지 footer**:

```
From   : 주주의관제탑 <hi@hi2vi.com>
To     : p4s2-throwaway@example.invalid
Subject: [주주의관제탑] 툴젠 — 신주인수권증서 매매 마감 D-7 (2026-09-07)

툴젠 — 신주인수권증서 매매 마감

마감: D-7 (2026-09-07)
기간: 2026-09-01 ~ 2026-09-07
보유: 500주 기준 43주
발행가: 확정 전 (확정 예정일 2026-09-11)

주주의관제탑에서 보기 →
http://127.0.0.1:3010/events/20260806000329

————————————————————————
출처: 공시 접수번호 20260806000329
이 메일은 회원님이 설정한 마감 알림입니다 — 알림 설정에서 끌 수 있습니다.
알림 설정: http://127.0.0.1:3010/portfolio/notifications
```

The ② variant, from the run anchored on today — **no 발행가 line and no share conversion, because
② has neither fact**:

```
Subject: [주주의관제탑] 제이에스링크 — 전환청구 개시 D-1 (2026-09-03)

제이에스링크 — 전환청구 개시

마감: D-1 (2026-09-03)
기간: 2026-09-03 ~ 2028-08-03
보유: 500주

주주의관제탑에서 보기 →
http://127.0.0.1:3010/events/20250902000288

————————————————————————
출처: 공시 접수번호 20250902000288
이 메일은 회원님이 설정한 마감 알림입니다 — 알림 설정에서 끌 수 있습니다.
알림 설정: http://127.0.0.1:3010/portfolio/notifications
```

**One thing the operator should look at, and it is on the question list:** the fact block's first
label reads `마감:` for **all three** types, but ②'s countdown is 전환청구 **개시** — a start, not a
deadline. The header line above it already says 「전환청구 개시」, and R5 wrote the block generically
as 「마감 mono D-표기」, so nothing is wrong against the record — but `마감: D-1` above `전환청구
개시` reads oddly, and this is exactly the class of thing `ui-traps` #5 exists for. It is a one-word
copy decision and it is on the gate list.

The three remaining live checks, in order, all on the same rig:

```
# idempotent — the same anchor a second time mails nobody
-> 2 account(s), 1 candidate(s) -> sent 0, already-sent 1, skipped-no-chips 0, failed 0

# the off switch: PUT /portfolio/notifications {"lead_days": []}
-> 2 account(s), 0 candidate(s) -> sent 0, already-sent 0, skipped-no-chips 1, failed 0

# the ceiling (--notify-max-mails 0), all four chips selected
-> 1 candidate(s) -> sent 0 … | ceiling 0 — BUDGET EXHAUSTED      (a status, not an exception)
# and with the ceiling restored, the same anchor:
-> 2 candidate(s) -> sent 1, already-sent 1                        (툴젠 D-7 was already sent; 제이에스링크 D-3 was not)
```

The rows behind that last run are the design in one line — **one event, two chips, two mails, two
rows**:

```
(account 39, event 196, lead_day 7, anchor 2026-09-07, rcept 20260806000329)
(account 39, event 876, lead_day 1, anchor 2026-09-03, rcept 20250902000288)
(account 39, event 876, lead_day 3, anchor 2026-09-03, rcept 20250902000288)
```

### (c) The ops 개요 tab

`GET /ops/overview` on the 8011 API behind throwaway `MIJUAL_OPS_ID/PASSWORD` — the door opened and
the panel serves the new entry with its `due` list beside the three existing ones, plus the smoke
runs in 최근 실행:

```
daily-pipeline-morning | 07:30 daily | mijual.daily_pipeline    | due: 3
daily-pipeline-evening | 19:30 daily | mijual.daily_pipeline    | due: 3
notify-deadlines       | 08:30 daily | mijual.notify_deadlines  | due: 3  ['2026-08-31T08:30:00+09:00', '2026-09-01T08:30:00+09:00']
weekly-resync          | 04:30 Sun   | mijual.daily_pipeline    | due: 0
--- 최근 실행
smoke-notify manual 2026-09-02T07:57:15+09:00 ok=True ['notify']
    anchor 2026-08-31 | transport smtp 127.0.0.1:8025 … | 2 account(s), 2 candidate(s) -> …
```

`frontend/components/ops` hard-codes no stage or entry list (checked before assuming it would
render), and `frontend/lib/opsRuns.ts` joins on `run.label == entry.kwargs.label` + `trigger ==
"beat"` — which the entry carries. `npm run smoke`'s two `opsRuns` tests still pass. **Expected and
correct in dev:** those three `due` instants have no `beat`-triggered run, so the panel will render
「실행 기록 없음」 for them until a real worker runs at 08:30 — no worker has ever run on this Mac.

### (d) Cleanup, and the operator's stack

계정 삭제 through the product's own route (`DELETE /auth/account` → 200), then the counts:

| table | before | after |
|---|---|---|
| `account` | 3 | **2** (the operator's own two, untouched) |
| `holding` | 3 | **1** (the operator's own) |
| `notification_pref` | 1 | **0** |
| `notification_send` | 3 | **0** |
| `password_reset` | 1 | **0** |

The cascade is proven, including the new table. Both throwaway processes are stopped (`lsof` on
8011 and 8025 is empty). `make stack-status` is byte-for-byte what it was — `mijual-postgres: Up 2
days (healthy)`, api **pid 60158** on 8010, web **pid 61423**, same pids as before the slice — and
the operator's API log contains **zero** lines matching `mail`: it never left the console transport,
which is right, because the dev `.env` has no `SMTP_*` keys and the 8010 process was started before
this code existed.

**One thing deliberately left behind:** six `smoke-notify` rows in `pipeline_run`, visible in the
ops 최근 실행 표 as `manual` runs. They are truthful records of runs that actually happened, and
deleting rows out of a run log to tidy up would be falsifying the one surface whose whole job is to
say what ran. (`--no-run-log` exists and would have avoided them; using it would also have cost the
evidence in (c).)

## Tests

Core behaviour only — the transport itself is verified live above, not asserted.

- **`tests/test_notify.py`** (new, 6 tests, in-memory SQLite / `StaticPool` / no network, the
  `test_web_portfolio.py` fixture style): the default chips select two deadlines and a re-run sends
  nothing; `[]` is the off switch and is honoured; a **moved anchor date is a new deadline and mails
  again** (a 정정 that shifts the ① 매매 마감 by a day, checked the day after — three anchors on
  record afterwards); the ceiling is a reported stop; the subject template + D23 re-signature +
  no won amount in a pending-price ① body + the ③ variant carrying neither a price line nor a
  conversion; and an unknown message kind refuses to render.
- **`tests/test_web_portfolio.py`**: one added test for the D7 upsert that **forces** the race
  rather than hoping for it — the pre-write lookup is monkeypatched to miss a row that is already
  there, which is exactly what the loser of the race sees, and the save must land as an update
  (one row, updated; not a second row and not a 500).
- **`tests/test_web_ops.py:242`**: the expected beat-entry set now includes `notify-deadlines`,
  with a comment saying why the entry has to exist for the panel's 「실행 기록 없음」 derivation.
- `tests/test_scheduler.py` needed no change: its beat-entry contract test resolves the new task and
  its config automatically, and its `config.stages == (six)` assertion still holds because the
  default is `DEFAULT_STAGES`, not `STAGES`.

## Deviations from `plan.md`

Three, all small.

1. **The no-money assertion is a money *pattern*, not the character `원`.** The plan asked for "no
   rendered deadline body contains `원` for a pending-price ①". It cannot: R5's **signed** footer
   sentence is 「이 메일은 **회원**님이 설정한…」 and contains 원. The rule R5 actually states is
   「확정발행가 전 금액 금지」 — a *won amount* — so the test asserts
   `re.search(r"[0-9][0-9,]*\s*원", body) is None` **and** that the 예정발행가 (`3200`) is nowhere in
   the body. Same rule, correctly aimed.
2. **`NOTIFY_MAX_MAILS` (200) is declared in `mijual.beat`, not in `mijual.notify`.**
   `PipelineConfig` needs it as a field default and must not import `mijual.notify` (which reaches
   `mijual.web.*`), so the number lives in the stdlib declaration module both ends already read —
   the same reason `BEAT_ENTRIES` lives there. `mijual.notify.DEFAULT_MAX_MAILS` re-exports it, so
   there is still exactly one statement of the number.
3. **The plan's `POST /auth/reset-request` is `POST /auth/reset/request`** (and ops login is
   `POST /ops/login` with `{"id", "password"}`). Recorded because the gate walkthrough and S6's
   smoke suite will want the real paths.

Two decisions the plan left to judgement, made and recorded here:

- **`SmtpMailer` issues `AUTH` only when the server advertises it.** A no-auth local sink and a
  real provider then use one code path. The failure direction is acceptable: a real server that
  requires auth and does not advertise it fails the send with a typed error rather than silently
  sending unauthenticated.
- **The SMTP connection opens lazily, on the first actual send.** A day with no candidate costs no
  login, and a misconfigured SMTP host does not error a stage that had nothing to send anyway.

## Notes recorded in `phase.md` rather than here

`phase.md` carries the phase's state and this file does not restate it — see
[`../../phase.md`](../../phase.md):

- § *Decisions* — four new lines (the stage on its own lock; the idempotency key and the re-send
  rule; no won amount in any mail; TLS required outside an explicit local-sink override).
- § *Doc impact* — six lines, `(P4.S2)`.
- § *Operator Questions* — one entry carrying **the exact literal strings for gate approval**: the
  subject template, a fully rendered ① body and an ② body, the reset mail, the `SMTP_FROM` display
  name, and the `마감:` label question raised above.
- § *Notes for later slices* — `(from P4.S2, for P4.S4/P4.REVIEW)` with the SMTP keys, where the
  operator copies them from, the gate-demo command, and the TLS policy; and one line `(for P4.S8)`.
- The two notes tagged `for P4.S2` were consumed and dropped.
