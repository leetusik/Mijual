# P4.S2 — The real `Mailer` over SMTP, and the D-day notification send path

## What this slice is

The last unbuilt product feature: 마감 임박 이메일. Today `src/mijual/mail.py` is a seam
(`Message(to, kind, data)`, `Mailer.send`, `ConsoleMailer` that prints and sends nothing) and the
only sender is the password-reset flow. This slice (1) implements the real transport over SMTP,
(2) builds the scheduled D-day send that reads each reader's 알림 설정 and portfolio deadlines and
mails them, (3) fixes D7 (`PUT /portfolio/notifications` is read-then-insert against a unique
constraint — make it an upsert), and (4) re-signs the mail subject to **주주의관제탑** (D23; the
operator answered this in `intent.md`: the retired name appears nowhere).

Read first: `phase.md` whole (the two notes tagged `for P4.S2` are yours to consume), `intent.md`
(items 5 and 7 of *Confirmed Intent*, and the D23 answer under *Clarifications Resolved*), the
signed spec at `docs/reference/design/rounds/05-account/output/build-prompt.md` § *알림 (R5-5,
R5-7)* and `.../output/result.md` § *Proposed copy → Notify*, and `docs/current/security.md`
§ *Rate Limits / Abuse Cases* (the "Notifications: email only … no marketing or digest mail,
ever" rule) and § *Secret Handling*. `docs/current/backend.md` § *Background Jobs* and
§ *Error Handling and Logging* for the logging rules. Do not read the whole doc set.

## Verified facts (already checked — build on them, do not re-derive)

**The seam.** `mijual.mail`: `PASSWORD_RESET = "password_reset"`, `Message(to, kind, data:
Mapping[str, str])`, `Mailer` protocol, `ConsoleMailer(stream)`. `create_app(mailer=...)` puts it
on `app.state.mailer`. The reset sender is `mijual.web.auth` (~line 440): `data={"url":
f"{settings.app_base_url}{RESET_PATH}?token=…", "expires_at": clock.iso(expires_at)}`,
`RESET_LIFETIME = 1 h`. `mijual.mail` must stay **stdlib-only** (`backend.md`: auth, hashing, mail
and the vocky client are all stdlib) — `smtplib` + `email.message.EmailMessage` + `ssl`.

**The signed spec (R5, build-prompt § 알림).** 메일: 라이트 표면. 제목 `"[미주알] {종목} — {마감명}
D-{n} ({date})"` → **now `[주주의관제탑] …`** by operator decision. 본문 = **사실 블록** (마감 mono
D-표기 · 기간 · 보유 N주 기준 주수 · 발행가 상태) + "미주알에서 보기 →" (→ 주주의관제탑에서 보기,
linking the event page) + **푸터** (rcept_no 출처 + 해지 안내: "이 메일은 회원님이 설정한 마감
알림입니다 — 알림 설정에서 끌 수 있습니다."). **확정발행가 전 금액 금지 — 메일에도 동일.** 발송
앵커 KST. 알림 외 메일(마케팅·다이제스트) 금지. The 시점 칩 are 7일/3일/1일/당일, default 7일+1일.

**What the sender reads.** `NotificationPref` (`notification_pref`, unique
`uq_notification_pref_account`, `lead_days` a JSON list ⊂ `(7, 3, 1, 0)`; **absent row = the
default `DEFAULT_LEAD_DAYS = (7, 1)`; `[]` = no mail**). The address is `Account.email` (stored
PII is exactly email + password hash — never a second address). Helpers in `mijual.web.portfolio`:
`LEAD_DAY_CHOICES`, `DEFAULT_LEAD_DAYS`, `lead_days_of(db, account)`, `set_lead_days(db, account,
raw)` (the D7 read-then-insert), `entries_of(db, account)`. Composition is
`mijual.web.reads.load_portfolio(session, entries, today=, claims=None)` →
`{"reference", "holdings", "upcoming": [...], "past": [...]}`; **`upcoming` is dated rows (days ≥ 0)
followed by open ② rows (days < 0, `window_state == "open"`) and 추후결정 rows (`date is None`)** —
select only `countdown["days"] is not None and countdown["days"] in lead_days`. Each row is the
`_rights_row` payload: `rcept_no`, `rights_type` (`R1`/`R2`/`R3`), `corp_name`, `countdown` =
`{label_ko, date, dday, days, window: [start, end], window_state, reference, source}`, `shares`,
and for ① `offering` = `OfferingInputs.payload()` (`allotment_ratio` to ten decimals,
`excess_ratio`, `confirmed_price` / `planned_price`, `final_price_date`, `unit_value`…). 마감명 is
`countdown.label_ko` (`COUNTDOWN_LABELS_KO`: R1 신주인수권증서 매매 마감 · R2 전환청구 개시 · R3
반대의사 통지 마감) and the D-표기 is `countdown.dday` (`mijual.calc.DDay.label`: `D-5` / `D-DAY`) —
**reuse both verbatim, never re-spell them**. 보유 N주 기준 주수 for ① is
`mijual.calc.allotted_shares(shares, allotment_ratio)`; ② and ③ have no share conversion. **No won
amount goes into any mail** — the safest reading of "확정발행가 전 금액 금지" and the one to take:
the 사실 블록 states 발행가 상태 (확정 전 + `final_price_date`, or 확정), not a figure.

**The schedule is one declaration.** `mijual.beat.BEAT_ENTRIES` (stdlib, imported by both the
worker and the ops 개요 tab) → `mijual.scheduler.app.BEAT_SCHEDULE`. Every entry carries
`trigger: "beat"` and a `label`; the ops panel's 「실행 기록 없음」 derivation
(`frontend/lib/opsRuns.ts`) joins `beat.entries[].due` against `runs.rows` **by `run.label ==
entry.kwargs.label`** and `trigger == "beat"`. So **a scheduled send that leaves no `PipelineRun`
row would render as a missed run forever.** `tests/test_scheduler.py` asserts every beat entry
names a registered task with usable kwargs; `tests/test_web_ops.py:242` asserts the exact set of
entry names (extend it). `run_pipeline` (`mijual.scheduler.pipeline`) already does everything a
scheduled job needs — lock (`config.lock_name`, `use_lock`), the run-log row (`open_run_row` /
`close_run_row`, label + trigger + stages + the verbatim spend line), `_stage` error containment,
`STAGE_FUNCTIONS` dispatch by name, `PipelineConfig.from_kwargs` for beat kwargs (`stages`,
`label`, `trigger`, `lock_name` all exist). The worker runs `-c 1`; morning pipeline 07:30 KST,
evening 19:30, Sunday 04:30 resync; runs take minutes.

**Import boundaries (tests):** no module under `mijual.web` may import `mijual.dart` /
`mijual.collect` / `mijual.extract` or a model SDK (`tests/test_web_smoke.py`); `mijual.agent` may
not import a spending module; only `web/vocky.py` may import an HTTP client. `mijual.web/__init__`
imports nothing, so `mijual.web.reads` is importable from the worker side without pulling FastAPI
(`mijual.web.portfolio` does reach `mijual.web.errors`; FastAPI is in the worker image anyway).
Nothing forbids the scheduler side importing `mijual.web.*` — but keep one statement of
`DEFAULT_LEAD_DAYS` and one composition function (`load_portfolio`); never re-spell either.

**Config + env.** `Settings` (`src/mijual/config.py`) has no SMTP fields. `.env.prod.example`
already carries a marked section `# --- mail (P4.S2 adds SMTP_* here) ---` (S1) — extend **that
file only**; the API, worker and beat all read the same `env_file`, so a beat task can send with no
compose change. The credentials are `hi2vi_web`'s transactional stream: Namecheap Private Email,
`SMTP_HOST=mail.privateemail.com`, `SMTP_PORT=587` (STARTTLS) or 465 (implicit TLS),
`SMTP_USER=hi@hi2vi.com`, `SMTP_PASS`, `SMTP_FROM` with a display name. Keep those names (the
operator copies the values across from hi2vi's `.env.prod` on the box); **no `SMTP_TO`** — this
product mails readers. The reference is `~/projects/personal/hi2vi_web/src/lib/mailer.ts` (read,
never edit): `secure` from the port, bounded connect/greeting/socket timeouts (~10 s), a display
name on From (Gmail renders a bare address as its local-part), CR/LF-stripping on any header value.

**Tooling on this Mac.** `uv 0.8.14` → `uvx aiosmtpd -n -l 127.0.0.1:8025` gives a local SMTP sink
(no TLS) that prints every received message. The operator's dev stack is **running** (`make
stack-status`: Postgres on host 5434, API pid on `127.0.0.1:8010` with **no** SMTP env — it stays on
`ConsoleMailer`, `next dev` on 3010) — never stop or restart it; run your own API on a spare port
(e.g. 8011) when you need SMTP wired. Tests use SQLite (`StaticPool`) — no Postgres-only SQL.

**Idempotency has no home yet.** 18 tables today; nothing records a sent notification.

## Design (decided — implement this; argue in `result.md` if a fact forces a change)

1. **The send is a pipeline stage on its own lock.** Add `stage_notify` to
   `mijual.scheduler.pipeline` (`STAGE_FUNCTIONS["notify"]`), a beat entry
   `notify-deadlines` in `mijual.beat` at **08:30 KST daily** (after the 07:30 run) with kwargs
   `{"stages": ["notify"], "label": "notify-deadlines", "trigger": "beat", "lock_name": "notify"}`,
   and a registered task `mijual.notify_deadlines` in `scheduler/app.py`. Its own lock name means it
   **never contends with the corpus lock** (a skipped run writes no row and would silently send no
   mail that day). Keep the six corpus stages as the **default** `stages` (add a
   `PIPELINE_STAGES`/`DEFAULT_STAGES` tuple beside `STAGES`, which now also knows `notify`) so the
   daily runs do not grow a mail step. This buys the run-log row, the verbatim spend line (0
   requests, 0 calls, ▷ $0), the ops 개요 rendering, error containment and the manual path for
   free: `python -m mijual.scheduler once --stages notify --no-lock --label smoke-notify`.
   Add `PipelineConfig.notify_today: str | None` (YYYYMMDD, CLI `--notify-today`) — an inspection
   knob that anchors the D-day arithmetic on another day, for the gate demo and for your smoke;
   and `notify_max_mails: int | None = 200`, a structural ceiling like every other outward action
   in this codebase, reported as a budget stop rather than an error.
2. **Selection + idempotency live in a new `src/mijual/notify.py`** (or a small package):
   for every account with ≥ 1 holding → `lead_days_of` (skip `[]`) → `load_portfolio(...,
   today=today_kst() or notify_today)` → `upcoming` rows with `countdown.days in lead_days` →
   one `Message(kind=DEADLINE)` per candidate not already recorded. Record each successful send in a
   **new table `notification_send`** (`NotificationSend`: `account_id` FK cascade, `event_id` FK
   cascade, `rcept_no`, `lead_day`, `anchor_date`, `sent_at`, unique on `(account_id, event_id,
   lead_day, anchor_date)`). **One mail per reader per deadline per lead day; a 정정 that moves the
   date is a new deadline and sends again** — say so in the model docstring. `create_all` is
   additive, so `python -m mijual.db ensure` / `make db-ensure` create it (19 tables). Per-account
   failures are contained (one bad address must not stop the run); the stage summary carries
   counts: candidates / sent / already-sent / skipped-no-chips / failed / budget.
   **Logs carry account ids, rcept_no and lead days — never an email address, never a subject.**
3. **Rendering + copy.** `mijual.mail` grows a `DEADLINE = "deadline"` kind and a
   `render(message) -> (subject, text[, html])` step the transport calls. **Every Korean string
   the mails carry lives in one module** (`src/mijual/mailcopy.py`), each with a one-line source
   comment (R5 build-prompt / result.md, or "drafted P4.S2 — operator approval at the P4 gate"),
   exactly as `frontend/lib/copy.ts` does. `Message.data` stays data (strings): for `deadline` —
   `corp_name`, `rights_type`, `label_ko`, `date`, `dday`, `days`, `window_start`, `window_end`,
   `shares`, `allotted_shares` (① only), `price_state` (① only: `confirmed` / `pending`),
   `final_price_date`, `rcept_no`, `event_url` (`{app_base_url}/events/{rcept_no}` —
   `frontend/lib/routes.ts` is the path authority; mirror it, do not invent), `settings_url`
   (`{app_base_url}/portfolio/notifications`). Draft the body from the R5 skeleton — 사실 블록 lines,
   the 보기 link, 출처 + 해지 footer — with **no won amount anywhere** and the ② and ③ variants
   omitting the lines they have no fact for. Draft the **password-reset** mail too (it becomes real
   the moment SMTP is configured; R5 signed only the UI line "재설정 링크를 보냈습니다 — 메일함을
   확인해 주세요."): subject, the link, its validity (`expires_at` rendered as KST), and a
   "요청하지 않으셨다면 무시" line. `text/plain` is the body; an `html` alternative is optional and,
   if you add one, may reference **no external resource** (no image, no font, no tracker — the
   measured "no third-party origin" property extends to mail by the same reasoning).
4. **`SmtpMailer`** in `mijual.mail`: `SmtpMailer.from_settings(settings)`; TLS policy explicit —
   port 465 → `SMTP_SSL`, any other port → **STARTTLS required** (refuse if not offered), and
   `SMTP_TLS=none` only when set explicitly (for a local sink; the `.env.prod.example` comment says
   never in production); `ssl.create_default_context()`; 10 s timeouts on connect and socket;
   `EmailMessage` with `From` = `SMTP_FROM` verbatim (display name included), `To`, `Subject` (CR/LF
   stripped on every header value); one connection reused across a batch (a context manager or a
   `send_many`) so a 50-mail run is not 50 logins. A send failure raises a typed error whose message
   carries **no address and no credential**.
5. **`Settings`**: `smtp_host`, `smtp_port` (int, default 587), `smtp_user`, `smtp_password`
   (from `SMTP_PASS`), `smtp_from`, `smtp_tls` (`ssl` / `starttls` / `none`, default derived from
   the port); `require_smtp()` naming the missing keys (never values); `__repr__` masks
   `smtp_password` — and, since you are in there, mask the password inside `database_url` too
   (`sqlalchemy.engine.make_url(url).render_as_string(hide_password=True)`), the S1 finding.
   `create_app`: `SmtpMailer.from_settings` when `smtp_host` is set, else `ConsoleMailer`; log **one**
   INFO line naming the transport (host + from, never the password) so a deploy can see which one
   it got. The notify stage builds the same mailer from the same settings; a stage run with no SMTP
   configured uses the console transport and says so in its summary (honest, sends nothing).
6. **D7 — the upsert.** `set_lead_days`: keep the read, but make the write race-safe on both
   SQLite and Postgres — a `begin_nested()` savepoint around the insert, `IntegrityError` →
   re-select and update (or the dialect-specific insert-on-conflict if you can keep one code path
   for both). Unchanged behaviour for the API contract.
7. **D23.** The subject is `[주주의관제탑] {종목} — {마감명} {D-표기} ({date})` with the served
   `dday` label verbatim (so 당일 reads `D-DAY`, as the board does; note it for the gate). 미주알
   appears nowhere — including the docstring at `mail.py:14`, which you rewrite. The orchestrator
   drops D23 after this slice lands; you only implement.
8. **`.env.prod.example`**: fill the mail section — `SMTP_HOST=mail.privateemail.com`,
   `SMTP_PORT=587`, `SMTP_USER=hi@hi2vi.com`, `SMTP_PASS=`, `SMTP_FROM="주주의관제탑 <hi@hi2vi.com>"`
   (the display name is product copy → it goes on the gate list with the brand question),
   `#SMTP_TLS=` documented. State in the comment that the values come from the operator's hi2vi
   `.env.prod` on the box and that unset SMTP means the console transport (no mail, said in the log).

## Tests (core behaviour only — the transport is verified live)

- `tests/test_notify.py` (small): with an account, a holding on a corp whose exposable event has
  an anchor at D-7/D-1 relative to a fixed `today`, lead days default → two candidates; run the
  stage with a recording mailer → two sends, two `notification_send` rows, the summary counts;
  run again → zero sends (idempotent); `lead_days=[]` → nothing; a moved anchor date → sends again;
  the ceiling stops at `notify_max_mails` with a budget status. Reuse the fixture style of
  `tests/test_web_portfolio.py` / `tests/test_scheduler.py` (SQLite `StaticPool`, no network).
- The mail rendering: one test that the deadline subject follows the operator's template, contains
  no `미주알`, and that no rendered deadline body contains `원` for a pending-price ① (the
  no-money rule) — a couple of asserts, not a suite.
- Extend the existing notification test in `tests/test_web_portfolio.py` for the upsert (a second
  save with a pre-existing row updates rather than raises).
- Update `tests/test_web_ops.py:242`'s expected entry set and check `tests/test_scheduler.py`
  still passes (the beat-entry contract test covers the new entry automatically).

## Verification (all of it; every command + outcome into `result.md`)

1. `.venv/bin/python -m pytest` green; `cd frontend && npm run typecheck && npm run smoke` green
   (the ops 개요 join sees a new label; check `frontend/components/ops` for any hard-coded stage
   or entry list before assuming it renders); `python3 scripts/workflow.py validate` clean.
2. `.venv/bin/python -m mijual.scheduler schedule` prints **four** entries including
   `notify-deadlines … 08:30 daily → mijual.notify_deadlines`, and `tasks` lists it.
3. `make db-ensure` against the running dev Postgres → `schema ok`, and `notification_send` exists
   (19 tables; count them the way S1 did, through SQLAlchemy — `psql` is not on this Mac).
4. **Live, through a local sink — no real credential, no real recipient:** start
   `uvx aiosmtpd -n -l 127.0.0.1:8025` in the background (kill it at the end). Export
   `SMTP_HOST=127.0.0.1 SMTP_PORT=8025 SMTP_TLS=none SMTP_USER=x SMTP_PASS=x
   SMTP_FROM="주주의관제탑 <hi@hi2vi.com>" MIJUAL_SESSION_SECRET=<throwaway>` for **your** processes
   only. (a) Run a second API on `127.0.0.1:8011` (`python -m mijual.web --host 127.0.0.1 --port
   8011`) against the dev database; sign up a throwaway account (`…@example.invalid`), request a
   password reset, and paste the sink's rendered reset mail (subject + body) into `result.md`.
   (b) Add a holding for a corp whose exposable event sits at D-7/3/1/0 from today (find one in
   `GET /board`), or pick any upcoming one and use `--notify-today`; run
   `python -m mijual.scheduler once --stages notify --no-lock --label smoke-notify [--notify-today
   YYYYMMDD]`; paste the sink's deadline mail and the stage line (`sent 1`); run it again → `sent 0
   / already-sent 1`; set the account's chips to `[]` through the API → run → `skipped`. (c) The
   ops tab: `GET /ops/overview` on your 8011 API with throwaway `MIJUAL_OPS_ID/PASSWORD` shows the
   `notify-deadlines` entry with its `due` list and the smoke run rows — or, if the door is more
   trouble than it is worth, the pytest over `/ops/overview` is the evidence; say which.
   (d) **Clean up:** delete the throwaway account through the product's own 계정 삭제 route
   (cascade wipes holdings, prefs and `notification_send` rows — prove the count is 0 afterwards),
   stop your 8011 API and the sink. `make stack-status` unchanged; the operator's 8010 API log
   shows it never left the console mailer.
5. State the instrument: curl + the SMTP sink; no browser run is claimed. **Do not send real mail
   from this slice** — the first real send to the operator's address is a gate/S4 action with the
   operator's credentials on the box.

If anything needs a real credential, a real recipient, or an operator decision you cannot draft
around, return `needs_operator` with the exact question.

## Notebook duties (`phase.md`, edited under budget — never append-only)

- **Drop** the two consumed notes `(from P4.DECOMP, for P4.S2)` and `(from P4.S1, for P4.S2)`.
- **Add** `(from P4.S2, for P4.S4/P4.REVIEW)`: the `.env.prod` SMTP keys and where the operator
  copies them from; the gate-demo command for one real D-day mail on the box (`docker compose -f
  compose.prod.yml exec mijual-worker python -m mijual.scheduler once --stages notify --no-lock
  --label gate-demo --notify-today YYYYMMDD` or the CLI form you shipped); that the reset mail is
  now real; that the ops 개요 shows `notify-deadlines` and its runs; the TLS policy. One line
  `(for P4.S8)`: notifications now ship (① 구현 범위 may include them; name the beat time).
- **Doc impact** (one line each, `(P4.S2)`): `backend` (the `SmtpMailer` + `render`, `mijual.notify`,
  the `notify` stage on its own lock, the 08:30 beat entry, the ceiling); `security` (mail policy:
  only configured deadline mail + reset, TLS policy, SMTP secret handling, no address in logs, the
  `database_url` password now masked); `operations` (Environment Variables: `SMTP_*`; Schedule:
  the fourth entry; the manual/demo command); `product` (notifications now send; the mail's
  content rules; the Korean copy pending literal approval); `data`/`architecture` (Storage Schema:
  `notification_send`, 19 tables); `api` only if any contract changed (the upsert does not).
- **Operator Questions** (append): the exact literal strings for approval at the gate — the
  deadline subject template + a fully rendered example body (① pending-price, and one ②/③), the
  reset mail subject + body, and the `SMTP_FROM` display name — one entry, the strings verbatim.
- **Decisions** (add): the send is a pipeline stage on its own lock; one mail per (reader, event,
  lead day, anchor date), a moved date re-sends; no won amount in any mail; TLS required outside
  an explicit local-sink override.
- Fix the stale line in `## Now`: the acceptance gate is **already declared** (`accept-gate P4`
  shows `required=true`) — drop "the orchestrator still owes `accept-gate`". Then rewrite `## Now`
  (≤ 15 lines) as the handoff to `P4.S3`: what S2 landed, the smoke evidence in one line, that S3
  owns `deploy/edge/jujutower.conf`, `deploy.sh`/`rollback.sh`, the runbook **and the owed
  backup/restore path**, and that S4 fills the SMTP keys.

## `result.md`

Verdict block first (`verdict`, `summary`, `files_changed`, `validation`, `deviations`,
`doc_impact`, `escalation: none`), then the log: commands and outcomes, the sink-captured mails
verbatim, dead ends. Reference `phase.md` sections rather than restating them.
