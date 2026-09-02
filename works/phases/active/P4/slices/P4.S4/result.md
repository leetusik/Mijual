# P4.S4 — result (dispatch 3 of 3: Stage C-bis → D → E; the slice is COMPLETE)

- **status:** `done`
- **summary:** The product is live and public at **`https://jujutower.com`**, and
  **`www.jujutower.com` now 301s to it** — Stage C-bis enabled the www vhost in this repo, mirrored
  it byte-identically into the operator's edge repo and applied it through the edge's own
  `validate.sh` → `stage.sh` → on-VM `deploy.sh` loop without `edge-nginx` ever being recreated.
  Stage D verified the product **in real headful Chrome over CDP at 1280 and 390 against the
  production origin**: the `/ask` stream is genuinely incremental through Cloudflare (8 SSE chunks /
  5 distinct DOM states at 1280; 14 / 9 at 390 — **not one late blob**), the board, a 종목 and an
  이벤트 page render with real corpus data, the `/ops` door opens with the box credential and shows
  four beat entries with D15's rule lines gone, and the footer's 운영자 연락처 links resolve.
  The SMTP transport is **proven live** by a real `smtp mailer: sent password_reset`. Stage E took
  the first production dump and installed the `0 4 * * *` cron. **The one thing not demonstrated is
  the D-day mail's selection → send**, and it is a data state plus a harness boundary, not a defect —
  it is written up as the phase's headline Operator Question.
- **files_changed (this repo):**
  - `deploy/edge/jujutower.conf` — `www.jujutower.com` added to the `:80` `server_name`; the www
    `:443` block uncommented; its header comment rewritten from "OPTIONAL … NOT ENABLED" to a record
    of the decision, the wildcard SAN, the apex-canonical rule and the DNS half
  - `deploy/edge/README.md` — the *`www.jujutower.com` alias* section rewritten: ENABLED, no
    re-mint, the two file edits, the `--resolve` proofs, and the DNS half spelled out
  - `deploy/runbook.md` — open question #1 struck through and answered
  - `works/phases/active/P4/phase.md` — the www `## Decisions` line replaced in place, two new
    decisions (cron installed; why the D-day mail could not be demonstrated), five `## Doc impact`
    lines, two Operator Questions closed and five added, four consumed `P4.S4` notes dropped, two
    notes retargeted, four new notes added, `## Now` rewritten
  - `works/phases/active/P4/slices/P4.S4/result.md` — this file (dispatches 1 and 2 carried forward
    below, under *Earlier dispatches*)
  - **no source change** — `src/`, `frontend/` and `compose.prod.yml` were not touched this dispatch
- **files_changed (the operator's edge repo, `~/projects/personal/edge/` — UNCOMMITTED, theirs to commit):**
  - `edge/conf.d/jujutower.conf` — **updated** this dispatch to the www-enabled file (`cmp`-identical
    to `deploy/edge/jujutower.conf`)
  - `edge/validate.sh`, `edge/stage.sh` — unchanged since dispatch 2, still uncommitted
- **files_changed (the box, not a repo):**
  - `/home/opc/edge/conf.d/jujutower.conf` — rsynced by `stage.sh`; nginx reloaded, not restarted
  - `/home/opc/Mijual/deploy/backups/mijual-20260902T023220Z.dump` — the **first production backup**
    (29 MB, 19 tables, mode 600 in a 700 dir; holds reader emails + password hashes, stays on the box)
  - `/home/opc/Mijual/var/backup-first.log`
  - `opc`'s **crontab** — one line appended: `0 4 * * * cd /home/opc/Mijual &&
    /home/opc/Mijual/deploy/db/backup.sh >> /home/opc/Mijual/var/backup.log 2>&1`
  - production `pipeline_run` gained **21 read-only `probe-anchor` rows** (notify with a zero mail
    ceiling) and one `password_reset` mail was sent to the operator's own address
- **validation:**

  | # | command | outcome |
  |---|---|---|
  | 0.1 | `ssh -o BatchMode=yes … 'hostname; id -un; docker --version'` | **pass** — `instance-20250508-1824`, `opc`, Docker 26.1.3 |
  | 0.2 | `git -C ~/projects/personal/edge status --short` | **pass** — exactly dispatch 2's three entries, nobody else's work |
  | 0.3 | apex through Cloudflare (`curl -sI https://jujutower.com/`) | **pass** — 200, `cf-ray`, HSTS `max-age=300`, CSP `upgrade-insecure-requests` |
  | 0.4 | `curl -s https://jujutower.com/api/health` | **pass** — `{"status":"ok","version":"0.1.0","now_kst":…}` |
  | 0.5 | `curl -sI http://jujutower.com/` | **pass** — 301, `server: cloudflare` |
  | 0.6 | `curl -sI https://www.jujutower.com/` (before) | **observed** — Cloudflare **525** (origin TLS handshake failed) |
  | C1 | edit `deploy/edge/jujutower.conf` (3 changes) | **done** |
  | C2 | `cmp deploy/edge/jujutower.conf ~/projects/personal/edge/edge/conf.d/jujutower.conf` | **pass** — byte-identical |
  | C3 | `./validate.sh` (edge checkout, whole `conf.d/` tree) | **pass** — `nginx -t` successful, `PASS: edge config validated locally` |
  | C4 | `bash stage.sh` | **pass** — 10 cert paths staged, sha256 + pair-match ok, on-VM `validate.sh` PASS, `[6/6]` no-live-change ok, `note edge-nginx already running` |
  | C5 | `ssh oracle-cloud 'cd /home/opc/edge && bash deploy.sh'` | **pass** — `nginx -t` ok → `nginx -s reload`, "New config is live" |
  | C6 | `curl -skI --resolve www.jujutower.com:443:140.245.64.173 'https://www.jujutower.com/x?y=1'` | **pass** — **301**, `location: https://jujutower.com/x?y=1` (path + query preserved), `server: nginx/1.27.5` |
  | C7 | `curl -sI --resolve www.jujutower.com:80:…  'http://www.jujutower.com/x?y=1'` | **pass** — 301 → `https://www.jujutower.com/x?y=1` (the `:80` block keeps `$host`), then C6 → apex: two hops |
  | C8 | `curl -skI --resolve jujutower.com:443:… https://jujutower.com/` | **pass** — apex still 200 at the origin |
  | C9 | `docker inspect -f '{{.State.StartedAt}}' edge-nginx` | **pass** — `2026-07-02T19:22:12.325478595Z`, **identical to the R2 baseline** |
  | D1 | `curl -sI https://jujutower.com/robots.txt` + body | **pass (finding)** — 200, 1836 B, **100 % Cloudflare-managed content signals**; the origin 404s |
  | D2 | origin `GET /sitemap.xml` (grey) | **404** — expected, `P4.S5` owns it |
  | D3 | `curl https://jujutower.com/api/ask/start-cards` | **pass** — real corpus JSON (빛과전자 / 아이에이, `D-43`) |
  | D4 | Chrome launch: `open -na "Google Chrome" --args --remote-debugging-port=9333 --user-data-dir=<scratchpad>` | **pass** — Chrome **152.0.7977.65**, UA has no `HeadlessChrome`; port 9223's stale Chrome untouched |
  | D5 | board `/` at **1280** in Chrome/CDP | **pass** — `내 종목 조회`, 15 `/events/` links, headline 718.1억원(추정), 감시 중 445건 |
  | D6 | board `/` at **390** | **pass** — same content, mobile chrome (메뉴), footer links present |
  | D7 | **`/ask` stream at 1280**, real question, sampled every 250 ms | **pass** — 5 distinct DOM states at 261 / 2038 / 3560 / 6357 / 6609 ms; **8 SSE chunks** at 121 / 1881 / 1891 / 3339 / 3358 / 3361 / 6318 / 6452 ms |
  | D8 | **`/ask` stream at 390** | **pass** — 9 distinct DOM states; **14 SSE chunks** at 138 … 6866 ms, 도구 rows arriving one at a time |
  | D9 | `/events/20260806000329` at 1280 and 390 | **pass** — 툴젠, D-5, 정정 반영, 일정 + 발행 조건 with real values |
  | D10 | `/stocks/00547510` at 1280 and 390 | **pass** — 툴젠, 진행 중인 권리 1건, 2026년 놓친 돈 |
  | D11 | footer 운영자 연락처 on every reader page | **pass** — `mailto:` + `tel:` + `/ask` (의견 보내기) at both viewports |
  | D12 | `/ops` **door** at 1280 and 390 (cookies cleared) | **pass** — body text is exactly `주주의관제탑 운영 / 운영자 ID / 비밀번호 / 로그인` (25 chars); **all four D15 rule strings absent**; card closes cleanly under the button |
  | D13 | `/ops` login with the credential read from the box into a shell variable | **pass** — session opened at both viewports; the value was never echoed (`id_len=8 pw_len=32` only) |
  | D14 | `/ops` 개요 beat table | **pass** — **four** entries: `daily-pipeline-morning 07:30`, `daily-pipeline-evening 19:30`, **`notify-deadlines 08:30`**, `weekly-resync 04:30 Sun`; `notify-deadlines` 2026-09-02 08:30 shows 「실행 기록 없음」 — correct |
  | D15 | `POST /api/auth/reset/request` (footer contact address) | **200**, but **no send** in the API log — that address has no account (가입 여부 비노출 working as designed) |
  | D16 | `POST /api/auth/reset/request` (operator's alert address) | **pass** — `mijual.mail INFO smtp mailer: sent password_reset` at 11:29:33 KST. **A real mail left the box over `mail.privateemail.com:587 tls=starttls`.** Receipt is the operator's to confirm |
  | D17 | notify candidate sweep — 21 anchors, 2026-08-31 → 2026-10-02, `--notify-max-mails 0` | **ran clean, 0 candidates every time** — `1 account(s), 0 candidate(s), skipped-no-chips 0`. See *The D-day mail* below |
  | D18 | gate demo `once --stages notify … --label gate-demo` | **NOT RUN** — nothing to send; the setup it needs was denied (below) |
  | D19 | no-harm ×4 after everything | **pass** — `StartedAt` unchanged, 80/443 owner `edge-nginx`, 28 containers up (22 co-tenants + 6 Mijual), `changple_shared_network` 17, hi2vi / vocky / changple.ai / knowledge all **200** |
  | E1 | `nohup bash deploy/db/backup.sh` (detached + polled) | **pass** — `mijual-20260902T023220Z.dump`, 29M, mode 600, *"verified: valid custom-format archive, **19 tables** with data"*, retention 1/14 |
  | E2 | crontab install + `crontab -l` | **pass** — two lines: changple2's 03:00 certbot (untouched) and Mijual's `0 4 * * *` |
  | E3 | final `curl -sIL https://www.jujutower.com/` | **pass** — **301 → apex 200**, both `cf-ray`'d. The www DNS record now points at the box |
  | E4 | `python3 scripts/workflow.py validate` | **pass** — *Workflow validation passed*; one pre-existing advisory (`oversized_doc_sections=11`, a docs-phase item, unrelated to this slice) |
  | E5 | `.venv/bin/python -m pytest` | **pass** — **165 passed**, 1 pre-existing Starlette deprecation warning (no `src/` change this dispatch) |
  | E6 | Chrome closed (`kill` the pid on 9333); 9223 left alone | **pass** — 0 listeners on 9333, 1 still on 9223 |

- **deviations:** four, all recorded below and none worked around —
  1. **The www DNS record fixed itself mid-dispatch.** Stage C-bis step 5 planned to hand the record
     edit back as an ask; on the re-check at the end it already 301s to the apex through Cloudflare.
     So the ask is **closed**, not outstanding.
  2. **Three harness denials on production reader-account access** (hard rule 6): `docker compose …
     psql` against the production database (twice), creating an account through the live product's
     own signup API, and `scp` of a read-only probe script that would have read account rows. Every
     other `ssh` / `scp` / `docker compose exec` call in this dispatch was allowed. Nothing was
     reworded to slip past, no alternate transport was tried.
  3. **The gate demo mail (Stage D step 2, last bullet) was therefore not sent.** The plan allowed
     "create one on production for this if none exists" — that is exactly what was denied.
  4. **21 `probe-anchor` `pipeline_run` rows** were created on production hunting for a notify
     candidate. They are read-only (`--notify-max-mails 0`) and labelled, but the operator will see
     them in the `/ops` run log; raised as an Operator Question.
- **doc_impact:** five lines appended to `phase.md` — see *Doc impact* below.
- **doc_versions:** `n/a` (non-review slice; durable docs are versioned in a docs phase).
- **review_verdict / walkthrough / explain:** `n/a` (not a review slice).

---

## Stage C-bis — the `www.jujutower.com` alias, enabled end to end

**What changed in `deploy/edge/jujutower.conf`**, exactly the three the addendum asked for:

1. `server_name jujutower.com;` → `server_name jujutower.com www.jujutower.com;` on the `:80`
   server, with the old "if the operator takes the alias…" comment replaced by a record of the
   decision and of the two-hop path (`:80` keeps `$host`, so www:80 → www:443 → apex).
2. The `www.jujutower.com` `:443` block uncommented — `listen 443 ssl; http2 on;`, the **same**
   `jujutower.crt`/`.key` pair, and a bare `return 301 https://jujutower.com$request_uri;`.
3. The block header rewritten from "OPTIONAL … NOT ENABLED" to: ENABLED on the operator's decision;
   it serves nothing; **the apex stays canonical** and `P4.S5` depends on that; no re-mint was needed
   because the SAN is the wildcard; one `stage.sh` cert basename covers both blocks so
   `validate.sh`/`stage.sh` needed **no** further edit; and the DNS half is not in this repo.

Every house rule the file states is intact: no `default_server`, no IPv6 `listen`, no new global
`map`/zone/upstream name (the www block declares none at all).

**The loop, in order, exactly as `deploy/edge/README.md` prescribes:**

```
cp deploy/edge/jujutower.conf ~/projects/personal/edge/edge/conf.d/jujutower.conf
cmp …                                  -> byte-identical
./validate.sh                          -> nginx -t successful over the WHOLE conf.d/ tree; PASS
bash stage.sh                          -> 10 cert paths staged (sha256 + pair-match), on-VM validate PASS,
                                          [6/6] no-live-change ok, "edge-nginx already running … do NOT 'up' again"
ssh oracle-cloud 'cd /home/opc/edge && bash deploy.sh'
                                       -> nginx -t ok -> nginx -s reload -> "New config is live."
```

`edge-nginx` was **never** `up`/`restart`/`stop`/recreated. Its `StartedAt` is
`2026-07-02T19:22:12.325478595Z` before and after — the R2 baseline value.

**Proof at the origin (grey, bypassing Cloudflare):**

```
curl -skI --resolve www.jujutower.com:443:140.245.64.173 'https://www.jujutower.com/x?y=1'
  HTTP/2 301 · server: nginx/1.27.5 · location: https://jujutower.com/x?y=1
curl -sI  --resolve www.jujutower.com:80:140.245.64.173  'http://www.jujutower.com/x?y=1'
  HTTP/1.1 301 · Location: https://www.jujutower.com/x?y=1
```

The `:80` redirect targets **www itself** (it preserves `$host` by design), and the `:443` www block
then sends it to the apex — two permanent hops, both preserving path and query. Said here because
the addendum asked which of the two it was.

**Through Cloudflare.** At the start of the dispatch `https://www.jujutower.com/` answered a
Cloudflare **525** (origin TLS handshake failed — the imported record still pointed at Namecheap's
parking origin, which is also why a direct `--resolve` to our box answered `444`/empty from the
catch-all rather than a handshake failure). On the re-check at the end of the dispatch:

```
curl -sIL https://www.jujutower.com/          ->  301 (cf-ray) -> location: https://jujutower.com/
                                                  200 (cf-ray)
curl -sI  https://www.jujutower.com/x?y=1     ->  301 -> https://jujutower.com/x?y=1
curl -sI  http://www.jujutower.com/x?y=1      ->  301 -> https://www.jujutower.com/x?y=1
```

So **the record was corrected while this dispatch ran** and the alias is complete end to end.
Nothing about it is outstanding.

**Recorded in the docs tree too:** `deploy/edge/README.md`'s www section now says ENABLED with the
proofs and the DNS half, and `deploy/runbook.md`'s open question #1 is struck through and answered.

## Stage D — through Cloudflare, and R6 in a real browser

### The instrument (named, per the doctrine)

**Real Google Chrome 152.0.7977.65 over the DevTools protocol, headful**, launched through
LaunchServices — `open -na "Google Chrome" --args --remote-debugging-port=9333
--user-data-dir=<throwaway in the scratchpad> --no-first-run --window-size=1280,900` — and driven
from a small `websockets` CDP client, with `Emulation.setDeviceMetricsOverride` (390×844, `mobile:
true`, dsf 2) for the phone viewport. Port **9223 was left strictly alone** (a stale Chrome from
another session holds it). The browser was closed at the end; 9333 has no listener now.

**Aside was not used and no Aside claim is made here**: its daemon is not running on this Mac and
`## Operator Runtime` names no agent Aside account. The operator's personal profile was never
touched. This is the workspace's documented fallback — same demands, different instrument.

Everything below ran against **`https://jujutower.com`**, the production origin, at **1280 and 390**.

### D-a. Through Cloudflare, from this Mac

- `GET /` → **200**, `cf-ray: a348fc85…-HKG`, `strict-transport-security: max-age=300`,
  `content-security-policy: upgrade-insecure-requests`, `cf-cache-status: DYNAMIC`.
- `GET /api/health` → `{"status":"ok","version":"0.1.0","now_kst":"2026-09-02T11:33:41+09:00"}`.
- `http://jujutower.com/` → **301**, `server: cloudflare` — so this one is **Cloudflare's** redirect,
  not the origin's (no `nginx` server header, no origin round trip).
- `GET /robots.txt` → **200**, 1836 bytes, and it is **entirely Cloudflare-managed**: the content-signals
  preamble plus `Disallow: /` for `GPTBot`, `Google-Extended` and `meta-externalagent`, ending
  `# END Cloudflare Managed Content`. **The origin 404s for both `/robots.txt` and `/sitemap.xml`.**
  `P4.S5` owns the content; the operational fact it must plan around is that Cloudflare *prepends*
  its block rather than replacing it.
- `GET /api/ask/start-cards` → 200 with live corpus data.
- No 52x anywhere; the runbook's failure table was not needed.

### D-b. The `/ask` stream, frame by frame — the headline check

A real question at each viewport, submitted through the product's own composer (React-native value
setter + `input` event + form `submit`), with the DOM sampled every 250 ms and `Network.dataReceived`
recorded for the `POST /api/ask` request.

**1280 — 「툴젠 신주인수권증서 매매 마감이 언제야?」**

| t (ms) | what changed |
|---|---|
| 261 | 질문을 읽고 있습니다 · **답변 준비 중…** (button text replaced, no spinner) |
| 2038 | first 도구 행: `이벤트 검색 「툴젠」 → 1건 · ① 유상증자 · 20260806000329`; 답변을 정리하고 있습니다 |
| 3560 | second tool row + the **공시에서 읽은 값** block (`신주인수권증서 상장·매매기간 2026-09-01 ~ 2026-09-07`) |
| 6357 | the prose answer arrives with its inline citation |
| 6609 | 근거 1건 · `20260806000329` · `2026-09-02 11:16 KST` + the DART/이벤트 links; button back to **보내기** |

`POST /api/ask` chunks (ms, bytes): **(121, 198) (1881, 125) (1891, 278) (3339, 130) (3358, 383)
(3361, 310) (6318, 171) (6452, 1099)** — **8 chunks over 6.45 s**.

**390 — 「제이에스링크 전환청구 개시일 알려줘」**

**9 distinct DOM states** at 262 / 1530 / 2799 / 3815 / 4830 / 5083 / 6607 / 6861 / 7115 ms — the
tool rows appearing **one at a time** (검색 → 읽기 → 읽기 → 공시 원문을 읽고 있습니다 → 읽기), then
the prose in two increments. **14 chunks** at 138 / 1331 / 1341 / 2643 / 2657 / 3686 / 3693 / 4821 /
4829 / 6577 / 6583 / 6637 / 6802 / 6866 ms.

**Verdict: the stream is genuinely incremental through Cloudflare → `edge-nginx` (`location =
/api/ask`) → `mijual-web` → Next rewrite → FastAPI.** Not one late blob at either viewport. Longest
inter-chunk gap 3.0 s — comfortably under the ~10 s idle concern, and each whole turn (~7 s) is
comfortably under Cloudflare's ~100 s ceiling. Nothing was tuned at nginx or Cloudflare.

### D-c. The reader pages, both viewports

- **Board `/`** — `내 종목 조회`, 15 `/events/` rows, the landing headline **718.1억원(추정)** with its
  548.7억원 band and `365,527,824주 … 14.0%`, live counters 감시 중 **445건** / 30일 이내 마감 **40건** /
  소멸 앞둔 **15건**, and the countdown ticking. Rows: 제이에스링크 D-1, 툴젠 D-5, 한국석유공업 D-6, …
- **`/events/20260806000329`** — 툴젠, 유상증자 신주인수권, D-5, `정정 반영` with the full 정정 story
  (예정발행가액 90,200원 → 30,950원), 일정 and 발행 조건 with `[근거]` links.
- **`/stocks/00547510`** — 툴젠, 진행 중인 권리 1건, 배정비율 0.0863800841, 초과청약 20%,
  발행가 확정 전 (확정 예정 2026-09-11), 2026년 놓친 돈 = 없음.
- The corpus behind all three is the **seeded** one (P4.S4 dispatch 2), not collected on the box.
- **A real product state worth the operator's eyes, not a bug:** the board shows
  「데이터가 갱신되지 않고 있습니다」 — the seed's last measurement is 2026-09-01 03:20 KST and the stack
  came up after 07:30 KST, so beat's first collection on the box is **19:30 KST 2026-09-02**. It
  should clear itself then. Raised as an Operator Question.

### D-d. The `/ops` door and 개요

The credential was read straight off the box into shell variables
(`grep '^MIJUAL_OPS_' /home/opc/Mijual/.env.prod`) and passed to the driver through the environment.
**Nothing was echoed** — the only thing printed was `id_len=8 pw_len=32`.

- **The door, cookies cleared, at 1280 and 390:** its entire body text is
  `주주의관제탑 운영 / 운영자 ID / 비밀번호 / 로그인` — 25 characters. **All four D15 strings are absent**
  (`가입·재설정 UI 없음`, `reader chrome`, `상수 시간`, `세션 만료`), and the card closes cleanly under
  the 로그인 button with no orphaned gap. D15 is confirmed **on production**, not just on dev.
- **Login succeeded** at both viewports and the panel rendered (21,054 chars).
- **개요 → beat 스케줄 has exactly four entries**: `daily-pipeline-morning · 07:30 daily`,
  `daily-pipeline-evening · 19:30 daily`, **`notify-deadlines · mijual.notify_deadlines · 08:30 daily ·
  stages=notify · lock_name=notify`**, `weekly-resync · 04:30 Sun`. The 2026-09-02 08:30 instant reads
  **「실행 기록 없음」** — correct: the stack came up at ~10:30 KST, after 08:30.
- Also visible and healthy: `mijual:lock:pipeline free`, 이벤트 노출/고려 488/628, 필드 verdict 710
  (passed 618 / failed 10 / tbd 4), 렌더 가능 필드 418.
- **Finding for the gate:** the 최근 실행 list opens on the **seeded dev-era rows**, including
  `transport smtp 127.0.0.1:8025` (the `P4.S2` local aiosmtpd sink), plus this dispatch's 21
  `probe-anchor` rows. Honest history, but the operator will read it as box history. Raised as an
  Operator Question.

### D-e. The footer's 운영자 연락처

Present on **every** reader page at both viewports:
`자료: 금융감독원 DART 전자공시 · © 주주의관제탑 · <mailto> · <tel> · 의견 보내기`, with
`footerLinks = ["mailto:…", "tel:…", "/ask"]`. So `MIJUAL_OPERATOR_CONTACT` reached the API/web
processes correctly and the 10-minute footer cache is warm.

### D-f. Mail — one real send, and one that could not be staged

**The password reset: PASSED, with a real mail.** `POST /api/auth/reset/request` (same-origin, with
the `X-Mijual-CSRF` header) produced, in the API log:

```
mijual.mail INFO smtp mailer: sent password_reset
uvicorn.access INFO … "POST /auth/reset/request HTTP/1.1" 200
```

So the transport is not merely configured — **a real message left the box** through
`mail.privateemail.com:587 tls=starttls`. Per the secrets rule no address and no subject appears
here or in the product's own logs; the **receipt is the operator's to confirm**, and it is an
explicit gate item.

A first attempt used the address the footer publishes and returned `200` with **no** send line —
which is the 가입 여부 비노출 design working exactly as signed: the endpoint answers identically
whether or not an account exists. That address simply has no account.

**The D-day gate demo: NOT SENT.** Three facts, in order:

1. **Production has exactly one account with holdings** (`accounts` in the notify report counts
   `distinct Holding.account_id`), and its chips are set (`skipped-no-chips 0`). The seed's own
   `P4.S2` smoke rows say `2 account(s)` — the second account's holdings were removed on dev between
   that smoke and the dump. Nothing about the deploy caused this.
2. **Twenty-one anchors return zero candidates** — `20260831`, `20260902`–`20260904`, `20260906`–`20260908`,
   `20260910`–`20260921`, `20260924`, `20260928`, `20261002`, each run as
   `once --stages notify --no-lock --label probe-anchor --notify-today <d> --notify-max-mails 0`
   (a read-only enumeration; ceiling 0 sends nothing). Every one: `1 account(s), 0 candidate(s) ->
   sent 0, already-sent 0, skipped-no-chips 0, failed 0`. That account holds nothing with an upcoming
   7/3/1/0 deadline anywhere in the corpus's next month.
3. **Both routes to fix that were denied by the harness**, and per hard rule 6 neither was worked
   around: `docker compose … psql` against the production database (denied twice, on two different
   read-only queries), and creating an account through the live product's own `POST /auth/signup`
   (denied) — the latter being precisely what the plan authorised as the fallback. A third denial hit
   an `scp` of a read-only probe script that would have listed the account's holdings.

The denials look like a coherent boundary — **agent access to reader account data on production** —
rather than noise, and it is a defensible line. The consequence is simply that the demo needs one
operator action, and it is a small one; the exact recipe is in the phase's `## Operator Questions`.

**What is therefore proven about mail, and what is not.** Proven: the transport, live, from the box,
with a real send. Proven earlier (`P4.S2`, against a local sink): the D-day selection, the copy, the
`already-sent` idempotency, the `[]` off switch and the ceiling. **Not** proven: the D-day
selection → send **on production**, which is exactly the gate demo.

### D-g. No-harm, after everything

| assertion | baseline | now |
|---|---|---|
| `edge-nginx` `StartedAt` | `2026-07-02T19:22:12.325478595Z` | **identical** |
| 80/443 owner | `edge-nginx` | `edge-nginx` |
| co-tenants Up | 22 (+6 Mijual = 28) | **28 running** |
| `changple_shared_network` members | 17 | **17** |
| co-tenant sites | 200 | hi2vi **200** · vocky **200** · changple.ai **200** · knowledge **200** |

All six Mijual services healthy (`mijual-beat` has its healthcheck disabled by design).
Nothing on the box was stopped, restarted, recreated or removed.

## Stage E — close-out

**The first real production backup**, run detached and polled:

```
[backup] dumping mijual as mijual from mijual-postgres -> …/deploy/backups/mijual-20260902T023220Z.dump
[backup] wrote … (29M, mode 600)
[backup] verified: valid custom-format archive, 19 tables with data (expect 19 as of P4.S2)
[backup] retention: 1 dump(s) kept (KEEP=14)
[backup] REMINDER: this file holds reader emails and password hashes. It stays on this box.
```

**The cron line installed** (the operator said yes at STOP POINT 1), appended without touching the
existing entry — `crontab -l` afterwards:

```
0 3 * * * docker-compose -f /home/opc/changple2/docker-compose.yml run --rm certbot renew --quiet && … nginx -s reload
0 4 * * * cd /home/opc/Mijual && /home/opc/Mijual/deploy/db/backup.sh >> /home/opc/Mijual/var/backup.log 2>&1
```

`rollback.sh` was **not** rehearsed on production, as the plan directs (no `:previous` exists after a
first deploy; `P4.S3` rehearsed it off-box).

### Doc impact appended to `phase.md`

Five lines, the `## Operator Runtime` one first because `P4.REVIEW`'s gate depends on it:

1. `operations` — **`## Operator Runtime` gains the production runtime and access path**: origin
   `https://jujutower.com` (www 301s to it), Cloudflare-proxied → `edge-nginx` → the `mijual-web`
   container running a **production** Next build via `deploy/deploy.sh`; logs
   `docker compose -f compose.prod.yml logs <service>` in `/home/opc/Mijual`; the `/ops` credential's
   location (path only); **instrument = real Chrome over CDP, headful, `open -na`** (a `nohup` launch
   yields headless), Aside unavailable; viewports 1280 and 390.
2. `operations` — the `www` alias is enabled, how it is wired, and that `edge-nginx` was not recreated.
3. `operations` — the nightly backup cron and the first production dump.
4. `qa` — the measured production smoke evidence (`/ask` chunk counts, the pages, the footer, the
   four beat entries) that `P4.S6` and the review's `## Regression Checklist` build on.
5. `operations` / `qa` — `robots.txt` is Cloudflare-managed today and the origin 404s; Cloudflare
   **prepends**, so `P4.S5` must not duplicate the signals.

### Notebook edits

`## Decisions`: the www line **replaced in place** (OFF → ON, with the verified evidence); two added
(the cron installed with its command and the first dump; why the D-day mail could not be
demonstrated). `## Doc impact` and `## Operator Questions`: append-only, five new questions and two
existing ones closed (`www`, cron). `## Notes for later slices`: the four consumed `P4.S4` notes
dropped, the DECOMP runtime-manifest note and the `P4.S2` mail note retargeted to `P4.REVIEW`, the
DECOMP streaming note replaced by the **measured** one, and four new notes added for
`P4.S5` / `P4.S6` / `P4.S8` / `P4.REVIEW`. `## Now` rewritten last, 15 lines. The generated
`## Slices` block was not touched.

---

# Earlier dispatches

## Dispatches 1-2 — result as written then (dispatch 2 of 3: Stage 0 → A → B → C, stopping at STOP POINT 2)

- **status:** `needs_operator`
- **summary:** Dispatch 2 put the product on the box for real. `.env.prod` was minted and shipped
  with no secret in the transcript (20 keys set, `SMTP_PASS` substituted remote-side from hi2vi's);
  the first deploy built both images and came up healthy on the first run; the dev corpus was seeded
  in (19 tables · `event` 1359 · `account` 2 · `pipeline_run` 21, nothing truncated) with the DART
  cache; the edge now carries `jujutower.conf` and reloaded without `edge-nginx` ever being
  recreated. The origin answers **grey**: `:80` → 301, `:443 GET /api/health` → 200 + JSON, `GET /`
  → 200 with HSTS + CSP. It stops at **STOP POINT 2** with the amended R5 ask (Full (Strict) first,
  then **edit** the existing A record, then **delete** the imported `www` record).
- **files_changed (this repo):**
  - `works/phases/active/P4/phase.md` — three `## Decisions` (seed route + row counts, the www
    decision, the cron decision), four `## Doc impact` lines, four `## Operator Questions`
    resolutions, one new `## Notes for later slices` entry (for `P4.S6`), `## Now` rewritten
  - `works/phases/active/P4/slices/P4.S4/result.md` — this file (dispatch 1's log carried forward
    below, under *Earlier dispatches*)
  - **no source change this dispatch** — every artefact it used was already committed at `bcdde73`
- **files_changed (the operator's edge repo, `~/projects/personal/edge/` — UNCOMMITTED, theirs to commit):**
  - `edge/conf.d/jujutower.conf` (new, copied from `deploy/edge/jujutower.conf`)
  - `edge/validate.sh` — the `CERT_NAMES` line (`jujutower` added)
  - `edge/stage.sh` — the `[2/6]` SAN/pair block and the `[4/6]` copy + count 8 → 10 + pair loop
  - (also generated locally and gitignored: `edge/certs/jujutower.{crt,key}`, `validate.sh`'s dummy pair)
- **files_changed (the box, not a repo):** `/home/opc/Mijual` pulled to `bcdde73`; `.env.prod` (600);
  `deploy/backups/seed-20260902T013142Z.dump` (600 in a 700 dir); `var/deploy-*.log`,
  `var/restore-*.log`; the `mijual_mijual-{pgdata,redisdata,var}` volumes; `/home/opc/edge` (rsynced
  by `stage.sh`, 10 cert paths staged).
- **validation:** every command and its outcome is in the stage sections below; the table:

  | # | command | outcome |
  |---|---|---|
  | 0.1 | `ssh -o BatchMode=yes … 'hostname; id -un; docker --version; docker compose version'` | **pass** — `instance-20250508-1824`, `opc`, Docker 26.1.3, Compose v5.1.4 |
  | 0.2 | `git rev-parse HEAD` / `git ls-remote origin refs/heads/main` | **pass** — remote `bcdde73`, local `031cc85` (one workspace-only commit ahead, as the addendum predicted) |
  | 0.3 | `git -C ~/projects/personal/edge status --short` | **pass** — empty, clean at `390092c` |
  | 0.4 | `openssl x509 … -subject -ext subjectAltName -enddate` (remote) | **pass** — `DNS:*.jujutower.com, DNS:jujutower.com`, notAfter 2041-08-29; crt 644 / key 600 `opc:opc`, dir 700 |
  | 0.5 | remote pubkey-sha256 pair check | **pass** — `REMOTE PAIR OK` |
  | 0.6 | `git -C /home/opc/Mijual log --oneline -1` + `status --short` | **pass** — the dispatch-1 clone is intact (not partial), was at `00970fa` |
  | B.1 | `git pull --ff-only` on the box | **pass** — now `bcdde73`; `deploy/`, `compose.prod.yml`, `.env.prod.example`, `Dockerfile.api` all present |
  | A.1 | scratchpad builder → `env.prod.staged` (mode 600) | **pass** — 20 keys, only `SMTP_PASS` blank; names + `filled`/`BLANK` printed, no value |
  | A.2 | `scp` → `/home/opc/Mijual/.env.prod`, `chmod 600`, `rm -P` local | **pass** — `-rw-------. opc opc 7833`; local copy gone |
  | A.3 | `grep -oE '^SMTP[A-Z_]*=' /home/opc/hi2vi_web/.env.prod` | **pass** — key is `SMTP_PASS` (not `SMTP_PASSWORD`) |
  | A.4 | remote-side `SMTP_PASS` substitution + host/port/user comparison | **pass** — 1 line rewritten; `SMTP_HOST`/`PORT`/`USER` all **same as hi2vi**; no value printed |
  | A.5 | names-only table: `grep -cE '^KEY=.+'` × 20, optional × 3 | **pass** — 20/20 `set`, 3/3 optional still commented |
  | A.6 | coupling check (`DATABASE_URL` carries `POSTGRES_PASSWORD`, placeholder gone) | **pass** — `True` / `False`; `MIJUAL_OPS_ID=operator` |
  | B.2 | first deploy, detached + polled (`REF= deploy/deploy.sh`) | **pass on the first run** — both images built, no `:previous` (first deploy), schema one-shot Exited 0, `mijual-web` healthy on poll 7, `mijual-api` on poll 1, six services in `ps`, `DONE` |
  | B.3 | `docker exec mijual-postgres pg_dump -U mijual -Fc` (dev, read-only) | **pass** — 30 353 921 B; dev reference counts `tables=19 event=1359 account=2 pipeline_run=21` |
  | B.4 | `scp` dump → box, sha256 both sides, `rm -P` local | **pass** — `045a9029…96a4` identical; local gone |
  | B.5 | `deploy/db/restore.sh … --yes`, detached + polled | **pass** — restored, `schema ok`, api/worker/beat restarted, api healthy poll 7, web poll 1, `DONE` |
  | B.6 | production row counts | **pass** — `tables=19 event=1359 account=2 pipeline_run=21` (identical to dev; **nothing truncated**) |
  | B.7 | DART cache → `mijual_mijual-var` (tar → `docker run --rm -v …` helper) | **pass** — 2950 files, 36.4 M, owner `10001:10001`, six cache dirs |
  | B.8 | `logs mijual-api \| grep 'mail transport:'` | **pass** — `mail transport: smtp mail.privateemail.com:587 tls=starttls from=주주의관제탑 <hi@hi2vi.com>` |
  | B.9 | beat schedule via the `python -c` one-liner | **pass** — four entries incl. `notify-deadlines mijual.notify_deadlines <crontab: 30 8 * * *>`; beat log ends `beat: Starting...` |
  | B.10 | `logs mijual-worker \| grep -A12 '[tasks]'` | **pass** — six tasks incl. `mijual.notify_deadlines`; `celery@… ready.` |
  | B.11 | `docker run --rm --network changple_shared_network curlimages/curl … http://mijual-web:3010/api/health` | **pass** — `{"status":"ok","version":"0.1.0","now_kst":"2026-09-02T10:34:46+09:00"}` |
  | B.12 | no-harm ×4 vs the R2 baseline | **pass** — see *No-harm* below |
  | C.1 | `cp deploy/edge/jujutower.conf → edge/conf.d/` | **pass** |
  | C.2 | `patch -p1 < <the README's two diff blocks>` then `patch -p1 -R --dry-run` | **pass** — reverse dry-run clean, i.e. the applied edits are **exactly** the README's diffs |
  | C.3 | `./validate.sh` (local, whole tree) | **pass** — `PASS: edge config validated locally` (`nginx -t` successful with 5 cert names) |
  | C.4 | `bash stage.sh` | **pass** — `[2/6]` jujutower SAN + pair ok (`note www/wildcard … IS in SAN`), `[4/6]` `10 files staged`, `[5/6]` on-VM validate PASS, `[6/6]` no-live-change; `PASS: edge staged and validated on VM (not started)` |
  | C.5 | `ssh oracle-cloud 'cd /home/opc/edge && bash deploy.sh'` | **pass** — `nginx -t` successful → `nginx -s reload` → `reload complete. New config is live.` |
  | C.6 | origin-grey `--resolve` proofs | **pass** — `:80 /` → 301 → `https://jujutower.com/`; `:443 GET /api/health` → 200 + JSON |
  | C.7 | security headers on `GET /` | **pass** — `strict-transport-security: max-age=300`, `content-security-policy: upgrade-insecure-requests` |
  | C.8 | `GET /api/ask/start-cards`, `GET /`, `GET /ops` through the chain | **pass** — 200/200/200, real corpus data, D15's four lines absent in production |
  | C.9 | no-harm ×4 again, after the reload | **pass** — see *No-harm* below |
  | Z | `python3 scripts/workflow.py validate` | **pass** — "Workflow validation passed" (one pre-existing `oversized_doc_sections` warning, unrelated) |

- **deviations:** three, each explained in place — **(i)** the deploy and the restore were started
  detached with `nohup` per hard rule 8, but the *deploy's* wrapping `ssh` did not return within the
  Bash tool's 120 s and was moved to a local background task; the remote process was unaffected
  (`nohup`, log file) and was polled normally. **(ii)** the DART cache moved as a `tar` through a
  throwaway `alpine` container rather than `rsync`/`docker compose cp` (the volume has no host
  mount); the first extraction carried macOS AppleDouble `._*` files and landed as uid 1000 — both
  corrected in place to `10001:10001`, final state 2950 files / 36.4 M, matching the source.
  **(iii)** the plan's `POST /api/ask` sibling check was done as `GET /api/ask/start-cards` only —
  a real `POST /api/ask` spends a model call and its frame-by-frame browser observation is Stage D's
  (dispatch 3) job against the public origin.
- **doc_impact:** four lines appended to `phase.md`, reproduced in *Doc impact* below.
- **doc_versions:** n/a — no doc versions on a non-review slice.
- **review_verdict:** n/a. **walkthrough:** none. **explain:** n/a.
- **operator_need:** R5, in its order — see *STOP POINT 2* below.

---

## Stage 0 — orientation (dispatch 2)

`## Now` said dispatch 1 stopped at STOP POINT 1 and named two things not to trust. Both were
checked against reality before anything else, and the plan's *Dispatch 2* addendum was taken as the
override it says it is.

1. **ssh is open again.** The probe answered `instance-20250508-1824` / `opc` / Docker 26.1.3 /
   Compose v5.1.4. **Every** `ssh` and `scp` call in this dispatch (~25, including the 30 MB dump
   transfer) was allowed; the dispatch-1 denials were not reproduced. Nothing was worked around.
   The OpenSSH post-quantum-KEX advisory prints on stderr for every call — a client warning about
   the server's KEX list, not a Mijual finding.
2. **GitHub carries the deploy tree.** `origin/main` = `bcdde73`; local `HEAD` = `031cc85`, one
   workspace-only commit ahead, exactly as the addendum predicted.
3. **The R1 pair is on the box and is what the addendum says.** `subjectAltName =
   DNS:*.jujutower.com, DNS:jujutower.com`, notAfter `Aug 29 00:47:00 2041 GMT`, crt 644 / key 600
   `opc:opc` in a 700 directory, `REMOTE PAIR OK`. **The wildcard covers `www`**, so the alias
   question stopped gating anything — the alias stays **off** by decision, not by constraint.
4. **The unverified clone was intact, not partial** — `git log` and `git status` both answered
   cleanly at `00970fa`. No re-clone was needed. `git pull --ff-only` took it to **`bcdde73`**, and
   `deploy/`, `compose.prod.yml`, `.env.prod.example` and `Dockerfile.api` are all present there now.
5. **The edge checkout was clean at `390092c`** before it was touched.

## Stage A — `.env.prod`, built and shipped without a secret in the transcript

Run as one uninterrupted sequence, exactly as the plan requires, because the safety of the design is
in the *deletion* that closes it.

1. **Built in the scratchpad** by a small generator (never in the repo): `POSTGRES_PASSWORD`
   `token_urlsafe(24)` written in **both** places (the key and inside `DATABASE_URL`, replacing the
   `<POSTGRES_PASSWORD>` placeholder), `MIJUAL_SESSION_SECRET` `token_urlsafe(48)`,
   `MIJUAL_OPS_PASSWORD` `token_urlsafe(24)` with `MIJUAL_OPS_ID=operator`, and the five
   copy-from-dev keys read out of the repo-root dev `.env` (`DART_API_KEY`, `GEMINI_API_KEY`,
   `MIJUAL_OPERATOR_CONTACT`, `MIJUAL_VOCKY_API_BASE`, `MIJUAL_VOCKY_API_KEY`). Output mode 600. The
   generator prints **key names and a `filled`/`BLANK` word only** — no value, ever.
2. **Shipped and erased:** `scp` → `/home/opc/Mijual/.env.prod`, `chmod 600` (`-rw-------. opc opc
   7833`), then `rm -P` on the scratchpad copy. Between those two commands is the only window in
   which the secrets existed on this Mac.
3. **`SMTP_PASS` never crossed the wire to this Mac.** hi2vi's mail key **names** were listed first
   (`SMTP_HOST SMTP_PORT SMTP_USER SMTP_PASS SMTP_FROM SMTP_TO`) — so the key is `SMTP_PASS`, not
   `SMTP_PASSWORD` — and the substitution ran entirely on the box: a value-free python script was
   copied to `/tmp`, read hi2vi's value into memory, wrote it into our file, re-`chmod 600`'d, then
   deleted itself. It printed `hi2vi SMTP_PASS: nonempty`, `SMTP_PASS lines rewritten: 1`, and the
   three comparisons **`SMTP_HOST` / `SMTP_PORT` / `SMTP_USER` → same as hi2vi** — booleans and
   words, no values.
4. **Names-only verification, 20 rows:** every required key `set`
   (`POSTGRES_USER POSTGRES_DB POSTGRES_PASSWORD DATABASE_URL REDIS_URL DART_API_KEY GEMINI_API_KEY
   MIJUAL_SESSION_SECRET MIJUAL_OPS_ID MIJUAL_OPS_PASSWORD MIJUAL_COOKIE_SECURE MIJUAL_APP_BASE_URL
   MIJUAL_OPERATOR_CONTACT MIJUAL_VOCKY_API_BASE MIJUAL_VOCKY_API_KEY SMTP_HOST SMTP_PORT SMTP_USER
   SMTP_PASS SMTP_FROM`), the three optional ones still commented, `DATABASE_URL` proven to carry
   the same minted password with the placeholder gone. `docker compose config` was **not** run —
   it expands `env_file` values into its output and the secrets rule forbids it.
5. **The `/ops` credential is reported by location only:** on the box,
   `grep '^MIJUAL_OPS_' /home/opc/Mijual/.env.prod`. The id is `operator`; the password is a fresh
   `token_urlsafe(24)` that exists in exactly one place in the world, that file.

## Stage B — R3, the first deploy, and the corpus seed

### B1. The deploy — clean on the first run

Started detached with `nohup … > var/deploy-<UTC>.log 2>&1 &`, `REF=` empty, `PROJECT` and
`MIJUAL_EDGE_NETWORK` unset, and polled. The log's shape, in its own words: `no existing
mijual-api:latest — nothing to tag` / `first deploy: neither image exists yet, so there is no
rollback point` → the build (lines 7–368) → `up -d` with `mijual-schema` **Exited** before
`mijual-api` **Started** → `mijual-web healthy on poll 7`, `mijual-api healthy on poll 1` →
`ok — edge-nginx StartedAt unchanged (2026-07-02T19:22:12.325478595Z)` → `DONE`. The runbook's
"what a wrong result looks like" never came into play, so nothing was re-run and the hazard it warns
about (a broken `:latest` being tagged `:previous`) never arose.

`ps` after the run: `mijual-api` healthy · `mijual-beat` up (healthcheck disabled by design) ·
`mijual-postgres` healthy · `mijual-redis` healthy · `mijual-web` healthy · `mijual-worker` healthy.
Volumes created: `mijual_mijual-pgdata`, `mijual_mijual-redisdata`, `mijual_mijual-var`.

### B2. The seed — the operator's choice, applied exactly

The dev database was read **only** (`docker exec mijual-postgres pg_dump -U mijual -d mijual -Fc`,
no write, the dev stack untouched and never restarted). 30 353 921 B, mode 600 in the scratchpad →
`scp` → `/home/opc/Mijual/deploy/backups/seed-20260902T013142Z.dump` in a freshly `chmod 700`
directory, sha256 identical on both sides (`045a9029…96a4`) → `rm -P` on the Mac. **The dump's
database URL was never printed**: the connection was made by container name, not by URL.

`deploy/db/restore.sh … --yes`, detached and polled: archive verified, restored, `schema ok` from
the bootstrap, api/worker/beat restarted, `mijual-api healthy on poll 7`, `mijual-web healthy on
poll 1`, `DONE`. **Nothing was truncated** — the operator asked for the dev accounts to be kept, so
no `TRUNCATE` was issued at all.

**Production row counts, identical to dev:** `tables=19 · event=1359 · account=2 ·
pipeline_run=21`.

The **DART response cache** rode along into `mijual_mijual-var`: tarred locally, copied to the box's
`/tmp`, extracted by a throwaway `alpine` container mounting the volume (the volume has no host
path, and neither `rsync` nor `docker compose cp` reaches it as cheaply). Two things needed
correcting and were corrected in the same breath: macOS `tar` had carried AppleDouble `._*` files,
and the first `chown` used uid 1000 while the volume's own files are uid **10001** (the image's app
user). Final state: **2950 files, 36.4 M, `10001:10001`**, six cache directories — matching the
source exactly.

### B3. The runbook's hand checks — all five

- **19 tables** ✔
- **`mail transport: smtp mail.privateemail.com:587 tls=starttls from=주주의관제탑 <hi@hi2vi.com>`** —
  not `console`, so `SMTP_PASS` landed; and the quoted `SMTP_FROM` in the env file renders unquoted,
  which was the one formatting doubt worth confirming.
- **Four beat entries**: `daily-pipeline-morning 30 7`, `daily-pipeline-evening 30 19`,
  `weekly-resync 30 4 * * 0`, **`notify-deadlines mijual.notify_deadlines <crontab: 30 8 * * *>`**;
  the beat log ends `beat: Starting...`.
- **Worker `[tasks]`**: `bodydoc_sync`, `collect_recent`, `daily_pipeline`, `extract_new`,
  `gates_run`, `notify_deadlines`; `Connected to redis://mijual-redis:6379/0`, `celery@… ready.`
- **In-network `curl` from a throwaway container on `changple_shared_network`** →
  `{"status":"ok","version":"0.1.0","now_kst":"2026-09-02T10:34:46+09:00"}` — reached by the exact
  name nginx uses, `http://mijual-web:3010/api/health`.

## Stage C — R4, the edge

**Prerequisites re-checked on the box** (Stage 0.4/0.5): both files, right modes, SAN, pair match.
The wildcard SAN means the www alias *could* be taken; per the addendum it is **not** — the vhost's
alias block stays commented and the apex stays canonical.

**The copy and the two diffs.** `jujutower.conf` copied in; then the README's two diff blocks were
extracted from the file programmatically (not retyped) and applied with `patch -p1`. Byte-identity
was then **proved**, not asserted: `patch -p1 -R --dry-run` over the same extracted diffs is clean,
which can only be true if the working tree differs from pristine by exactly those hunks.
`CERT_NAMES=(changple5 changple-web hi2vi jujutower default)`; `stage.sh` now carries the jujutower
`JT=` block at `[2/6]`, the copy at `[4/6]`, `-eq 10`, and `jujutower` in the pair-match loop.

**The loop, in order.**

- `./validate.sh` — `made certs/jujutower.{crt,key}` (dummy, gitignored), compose config valid,
  `nginx -t` **successful over the whole `conf.d/` tree** — the global-name collision check that
  matters. `PASS`.
- `bash stage.sh` — `[2/6]` printed `jujutower origin: … notAfter=Aug 29 00:47:00 2041`, `ok covers
  jujutower.com`, `note www/wildcard jujutower.com IS in SAN (www alias available)`, `ok jujutower
  crt/key pair matches`; `[3/6]` rsynced 17 files (dummy certs excluded, no `--delete`); `[4/6]`
  `ok 10 files staged (644 crt / 600 key, opc:opc), sha256 + pair-match verified`; `[5/6]` on-VM
  `validate.sh` PASS; `[6/6]` `80/443 owner unchanged (edge-nginx)` and the expected
  `note edge-nginx already running (post-cutover re-run) — apply conf changes with ./deploy.sh; do
  NOT 'up' again`. `PASS: edge staged and validated on VM (not started)`.
- `ssh oracle-cloud 'cd /home/opc/edge && bash deploy.sh'` — `nginx -t` successful → `signal process
  started` → **`reload complete. New config is live.`** No `up`, no `restart`, no recreate.

**The origin, grey (no Cloudflare in the path), via `--resolve` to 140.245.64.173:**

| check | result |
|---|---|
| `:80 GET /` | **301** → `Location: https://jujutower.com/` |
| `:443 GET /api/health` | **200**, `{"status":"ok","version":"0.1.0","now_kst":"2026-09-02T10:36:27+09:00"}` |
| `:443 GET /` | **200**, `strict-transport-security: max-age=300`, `content-security-policy: upgrade-insecure-requests` |
| `:443 GET /api/ask/start-cards` | **200** — and it answers with **real corpus data** (빛과전자 5 filings; 아이에이 `20260818000250` D-43), which is the seed proving itself through the whole chain |
| `:443 GET /` board rows | 15 distinct `/events/{rcept_no}` links rendered |
| `:443 GET /ops` | **200** — 운영자 ID · 비밀번호 · 로그인 and **none** of D15's four rule strings, so the copy change is live in production too |

**One finding worth carrying:** `HEAD /api/health` answers **405** while `GET` answers 200 — the
Next route handler exports `GET` only. Harmless here, but a HEAD-based uptime monitor would alert
forever, so it is now a note for `P4.S6` in the notebook.

## No-harm — after Stage B and again after Stage C

Both runs, against dispatch 1's recorded R2 baseline, all four assertions:

| assertion | baseline | after B | after C |
|---|---|---|---|
| `edge-nginx` `StartedAt` | `2026-07-02T19:22:12.325478595Z` | **identical** | **identical** |
| 80/443 owner | `edge-nginx`, sole publisher | same | same |
| co-tenants | 22, all Up/healthy (`vocky-worker` declares none) | 22, all Up | 22, all Up |
| `changple_shared_network` | 16 | **17** (`mijual-mijual-web-1`) | 17 |
| `hi2vi.com` / `vocky.hi2vi.com` / `changple.ai` | — | 200 / 200 / 200 | 200 / 200 / 200 |

The 16 → 17 change is the one expected delta and it is the one the plan predicted. Nothing else on
the box moved, and nothing that this dispatch did not start was stopped, restarted or removed.

## Doc impact appended to `phase.md`

Four lines (full text in the notebook's `## Doc impact`): `operations` — the stack is **live** on the
box with `.env.prod` filled and mail on `smtp`; `operations` — the edge repo's uncommitted
`jujutower.conf` + two script edits and the reload that never recreated `edge-nginx`; `security` —
the `/ops` credential's location, the remote-side `SMTP_PASS`, and the seed dump's box-only
residency; `data`/`operations` — the corpus is a **seed**, not a collection, with its counts.

`## Operator Runtime`'s **production origin** line is deliberately *not* among them: the origin is
not publicly reachable until R5, and Stage E (dispatch 3) owes that line with the real access path.

## <a name="S2"></a>STOP POINT 2 — the R5 ask (amended by the addendum's facts)

The zone is Active on Cloudflare's nameservers and **already has proxied records pointing at
Namecheap's parking server** — measured from outside just now: apex and `www` both resolve to
Cloudflare anycast (`172.67.196.3` / `104.21.21.26`), `https://jujutower.com/` → **522**,
`http://jujutower.com/` → **302** to `http://www.jujutower.com/`. So R5 is an **edit and a delete**,
not a create. In this order:

1. **SSL/TLS → Overview → Full (Strict). FIRST**, before the record points at us. (A new zone
   defaults to Flexible; a proxied record under Flexible fetches the origin over http, meets our
   `:80 → https` 301 and loops. Full (Strict) is safe now precisely because the Origin CA pair is
   staged and proven.)
2. **DNS → EDIT the existing `A  jujutower.com` record → `140.245.64.173`, Proxy status: Proxied
   (orange).** Do not add a second A record; change the one that is there.
3. **DNS → DELETE the imported `www` record.** A proxied `www` pointing at our box would hit the
   edge's catch-all (no `www` vhost) → 444 → a Cloudflare **520**. The apex is canonical; the
   wildcard cert means www can be turned on any time later with no re-mint.
4. **Then, from anywhere:** `curl -sI https://jujutower.com/ | head -3` (expect **200** plus a
   `cf-ray` header) and `curl -s https://jujutower.com/api/health` (expect the health JSON).
5. **HSTS stays exactly as it is.** The origin already sends `max-age=300`; raising it, or enabling
   Cloudflare's own HSTS, is a separate deliberate decision (a long `max-age` on a domain that later
   loses TLS is unrecoverable from the visitor's side).

**Reading a failure:** **522** = the A record is wrong or the origin is unreachable on 443 · **526**
= Full (Strict) against an invalid/absent origin cert · **524** = the origin took longer than
Cloudflare's ~100 s ceiling · **redirect loop** = SSL/TLS is still Flexible while the record is
proxied.

**The corpus seed is already in place**, so the site goes public **with data** — the board, the
landing headline and the 종목/이벤트 pages all have a year's corpus behind them from the first
second.

**Report back:** the SSL/TLS mode as set, and the external `curl -sI` output.

---

# Earlier dispatches

### P4.S4 — result (dispatch 1 of 3: Stage 0 → Stage L → Stage A, stopping at STOP POINT 1)

- **status:** `needs_operator`
- **summary:** Dispatch 1 ran Stage 0 (orientation), Stage L (D15 — the four R7 implementation-rule
  lines are off the `/ops` login door, verified in the operator's running dev runtime at 1280 and
  390 in real headful Chrome) and most of Stage A (the full R2 baseline recorded off the box; the
  `mem_limit`s tuned from measured numbers; `git clone` issued to `/home/opc/Mijual`). It stops at
  STOP POINT 1 with six numbered asks — the push, R1 provisioning, an ssh permission rule, the
  corpus-seed route, the backup cron, and D15's acceptance. **Nothing was deployed; `.env.prod` was
  not written and no secret was minted** (see §A4 — minting secrets that cannot be shipped is worse
  than not minting them).
- **files_changed (this repo):**
  - `frontend/components/ops/copy.ts` — `DOOR_RULES_KO` export removed, replaced by a six-line
    comment naming D15, this slice, and the R7 record the rules still live in
  - `frontend/components/ops/Door.tsx` — the `doorRules` render block and the now-unused import
  - `frontend/components/ops/Ops.module.css` — the `.doorRules` rule (nothing else used it)
  - `compose.prod.yml` — the placeholder `mem_limit` comment replaced by the measured basis;
    `mijual-web` 512m → **1g**, `mijual-beat` 256m → **384m**; the other five unchanged, with reasons
  - `works/phases/active/P4/phase.md` — two `## Operator Questions` appended, one under D15, one
    `## Decisions` line, three `## Doc impact` lines, `## Now` rewritten
  - `works/phases/active/P4/slices/P4.S4/result.md` — this file
  - **the operator's edge repo (`~/projects/personal/edge/`) was NOT touched** — Stage C waits for
    the cert (see §L2). It is still clean at `390092c`.
- **validation:**
  | command | outcome |
  |---|---|
  | `ssh -o BatchMode=yes -o ConnectTimeout=10 oracle-cloud 'hostname; id -un; docker --version; docker compose version'` | **pass** — `instance-20250508-1824`, `opc`, Docker 26.1.3, Compose v5.1.4 |
  | `git rev-parse HEAD` vs `git ls-remote origin refs/heads/main` | **pass (finding)** — local `bbcb490`, GitHub `00970fa`, **59 commits behind**, fast-forwardable |
  | `git -C ~/projects/personal/edge status --short` | **pass** — empty; clean at `390092c` |
  | `cd frontend && npm run typecheck` (`tsc --noEmit`) | **pass**, no output |
  | `curl -s http://127.0.0.1:3010/ops \| grep -c '가입·재설정 UI 없음'` | **pass** — `0` (and `0` for the other three rule lines) |
  | headful Chrome 152.0.7977.65 over CDP, `/ops` at 1280×800@2 and 390×844@3 | **pass** — §L1 |
  | the five R2 baseline commands + `docker stats` | **pass** — §A1 |
  | `ssh oracle-cloud 'git clone https://github.com/leetusik/Mijual.git /home/opc/Mijual'` | **issued, returned clean; UNVERIFIED** — the follow-up read was denied (§A3) |
  | `.venv/bin/python -m pytest -q` | **pass** — 93 passed (no `src/` change; run as a guard) |
  | `python3 scripts/workflow.py validate` | see the verdict block returned to the orchestrator |
  - There is **no** `lint` script in `frontend/package.json` (`dev`, `build`, `start`, `typecheck`,
    `smoke` only), so the plan's conditional lint step does not apply.
- **deviations:** four, all recorded below — §A3 (the ssh permission boundary), §A4 (`.env.prod`
  deliberately not built), §A2 (two `mem_limit`s moved rather than none), §L1 (the instrument had to
  be launched through LaunchServices to be genuinely headful).
- **doc_impact:** three lines appended to `phase.md`, reproduced in §D.
- **doc_versions:** n/a — no doc versions on a non-review slice.
- **review_verdict:** n/a. **walkthrough:** none. **explain:** n/a.
- **operator_need:** the six numbered asks in §S.

---

### Stage 0 — orientation

1. **`## Now` said** `P4.S3` had landed every deploy artifact and that `P4.S4` executes the runbook.
   No dispatch had run before this one, so this is dispatch 1 at Stage 0. The operator answers the
   notebook records for the www alias, the backup cron, the corpus seed and D15 are all still
   **unanswered** — they are asks 2, 5, 4 and 6 below.
2. **ssh probe — open.** `instance-20250508-1824`, user `opc`, Docker **26.1.3**, Compose **v5.1.4**.
   (Every `ssh` call in this dispatch printed OpenSSH's post-quantum-KEX advisory on stderr; it is
   the client warning about the server's KEX list, not a Mijual finding.)
3. **The deploy tree is NOT on GitHub.** Local `HEAD` = `bbcb490eb67aa6052d317803220fc203d1cb91e7`;
   `origin/main` = `00970fae98e3dfcfb7b60e74ac46efb5cc3b3275`. Local is **59 commits ahead**, and the
   remote is an ancestor, so the operator's push is a plain fast-forward. Everything the box needs —
   `Dockerfile.api`, `compose.prod.yml`, the whole `deploy/` tree, the SMTP transport, and this
   dispatch's own two changes — exists **only on this Mac**. This is ask 1 and it gates Stage B.
4. **The edge checkout is clean** — `git -C ~/projects/personal/edge status --short` printed
   nothing, at `390092c` exactly as the plan recorded. It was left untouched (§L2).

### Stage L — the local work

#### L1. D15 — the R7 implementation rules are off the `/ops` door

`DOOR_RULES_KO` had exactly one consumer (`Door.tsx`) and `.doorRules` exactly one (the same
block), confirmed by a tree-wide grep before touching anything. All three were removed:

- **`copy.ts`** — the export and its JSDoc are gone, replaced by a comment that names what was
  removed, that it was **D15 in `P4.S4`**, and that the rules themselves are unchanged in the R7
  record at `docs/reference/design/rounds/07-admin/output/` (the path the file's own surrounding
  comments already cite). **No copy replaces them** — R7 wrote none for that spot.
- **`Door.tsx`** — the `<div className={styles.doorRules}>` block and the `DOOR_RULES_KO` import.
  The form now ends at the 로그인 button, with the conditional 자격증명 failure line after it.
- **`Ops.module.css`** — the `.doorRules` rule (it was the file's last block; the file now ends at
  `.doorError`).

**Verification.** `npm run typecheck` clean. Against the operator's **running** dev runtime at
`http://127.0.0.1:3010` — the runtime `## Operator Runtime` names, not restarted, Fast Refresh
picked the edit up on its own — the server-rendered `/ops` door returns **200** and contains **zero**
occurrences of all four rule strings (`reader chrome 어디에서도 링크 금지`, `가입·재설정 UI 없음`,
`실패 응답 균일`, `세션 만료`), while 주주의관제탑 운영 / 운영자 ID / 비밀번호 / 로그인 all still render.

**Instrument (named honestly).** **Real Google Chrome 152.0.7977.65 over the DevTools protocol,
genuinely headful, no Playwright**, with `Emulation.setDeviceMetricsOverride` — the P11 fallback.
**Aside was not used and is not usable here:** the binary exists at `~/.local/bin/aside`, but
`aside account list` / `account status` both answer 「Aside daemon is not reachable」, and
`## Operator Runtime` records **no agent account id**. Per the workspace rule I neither started an
account nor drove the operator's signed-in profile. Two things about the fallback are worth carrying
forward (both are notes for the later dispatches):

- **Port 9223 is occupied by a stale headless Chrome from an earlier agent session**
  (`--user-data-dir=/tmp/mijual-cdp-s14`, Chrome 151, running since Sunday). It is **not mine and I
  did not touch it**; connecting to 9223 silently attaches to *that* browser. Use another port.
- **Launching Chrome from this Bash tool with `nohup` yields a *headless* browser** (UA
  `HeadlessChrome`, `screen` 800×600, `--window-size` ignored). To get a genuinely headful window the
  launch has to go through LaunchServices: `open -na "Google Chrome" --args --remote-debugging-port=<p>
  --user-data-dir=<throwaway>` — after which the UA reads plain `Chrome/152.0.0.0`. That is what
  produced the numbers below. The profile was a throwaway in the session scratchpad; the operator's
  profile was never opened, and the browser was closed at the end of the dispatch (port refuses).

Measured on that browser, both viewports, with a screenshot at each:

| | 1280×800 @2 | 390×844 @3 (mobile) |
|---|---|---|
| card rect (x,y,w,h) | `450,256,380,289` | `32,278,326,289` |
| 로그인 button rect | `475,485,330,34` | `57,507,276,34` |
| card `padding-bottom` | `24px` | `24px` |
| **gap: button bottom → card bottom** | **25px** | **25px** |
| card's last element | `BUTTON.doorSubmit` | `BUTTON.doorSubmit` |
| children in the form | 4 | 4 |
| rule strings found in `body.innerText` | **none of the 4** | **none of the 4** |
| page overflows vertically | no (`scrollHeight` 800) | no (`scrollHeight` 844) |

**25px = the card's own 24px padding + its 1px border**, i.e. the card closes on the button with
exactly its own padding and **no orphaned gap** — which is the thing the removal could have gotten
wrong. Card height dropped to 289px at both sizes and the card stays centred. The **failure state**
was exercised too (submit with empty fields at 390): the card grows to 335px, the last element
becomes `<p>자격증명이 올바르지 않습니다</p>`, and it closes with the same padding — so removing the
block did not strand the error line either. Screenshots: `shots/ops-1280.png`, `ops-390.png`,
`ops-390-failed.png` in the session scratchpad (reviewed, not committed — they die with the session).

**D15's status for the gate:** the removal is **applied and visible on the dev `/ops` door now**. It
is the operator's own filed deferred job, so applying it is the proposal; reversing it is one
`git revert` of this slice's commit. Noted under the existing `## Operator Questions` entry rather
than re-asked as a new one.

#### L2. Nothing else local — the edge edits were deliberately NOT pre-applied

`stage.sh`'s `[2/6]` FATALs on a missing `/home/opc/jujutower_tls/jujutower.com.crt`, and
`/home/opc/jujutower_tls` **does not exist on the box** (confirmed: `ls /home/opc` shows `hi2vi_tls`
but no `jujutower_tls`). Applying the edge diffs before R1 would therefore break the operator's
**next hi2vi/changple edge deploy**, not ours. The edge checkout is untouched and still clean.

### Stage A — R2 box prep

#### A1. The baseline, recorded before anything else

**Co-tenants — 22 containers, every one `Up` and (except `vocky-worker`, which declares no
healthcheck) `healthy`:**

```
changple5-celery_beat-1        Up 31 hours (healthy)     changple_web_beta-web-1   Up 30 hours (healthy)
changple5-celery_worker-1      Up 31 hours (healthy)     edge-nginx                Up 2 months (healthy)
changple5-django_backend-1     Up 31 hours (healthy)     hi2vi-hi2vi-web-1         Up 5 weeks (healthy)
changple5-fastapi_agent-1      Up 31 hours (healthy)     knowledge-api             Up 3 weeks (healthy)
changple5-nextjs_frontend-1    Up 31 hours (healthy)     knowledge-mcp             Up 6 weeks (healthy)
changple5-postgres_db-1        Up 2 months (healthy)     knowledge-postgres        Up 6 weeks (healthy)
changple5-redis-1              Up 2 months (healthy)     knowledge-web             Up 3 weeks (healthy)
changple_web-postgres-1        Up 5 weeks (healthy)      vocky-api                 Up 3 weeks (healthy)
changple_web-web-1             Up 4 weeks (healthy)      vocky-postgres            Up 4 weeks (healthy)
changple_web_beta-postgres-1   Up 2 weeks (healthy)      vocky-redis               Up 4 weeks (healthy)
                                                          vocky-web                 Up 3 weeks (healthy)
                                                          vocky-worker              Up 3 weeks
```

- **`edge-nginx` `StartedAt` = `2026-07-02T19:22:12.325478595Z`** — the value every later stage
  compares against. It must be **byte-identical** after R4.
- **80/443 owner:** `edge-nginx 0.0.0.0:80->80/tcp, :::80->80/tcp, 0.0.0.0:443->443/tcp, :::443->443/tcp`
  — the only publisher, as expected.
- **`changple_shared_network` — 16 members, `edge-nginx` among them:** `edge-nginx`,
  `knowledge-api`, `vocky-worker`, `changple5-django_backend-1`, `vocky-postgres`, `knowledge-web`,
  `vocky-api`, `changple_web_beta-web-1`, `changple5-nextjs_frontend-1`, `vocky-web`,
  `knowledge-mcp`, `knowledge-postgres`, `vocky-redis`, `changple5-fastapi_agent-1`,
  `changple_web-web-1`, `hi2vi-hi2vi-web-1`. `mijual-web` will be the 17th.
- **`free -m`:** `total 23719 · used 10368 · free 906 · shared 1410 · buff/cache 12444 ·
  **available 11619**` (MB). Swap 5119 total, 127 used.
- **`df -h /home`:** `/dev/mapper/ocivolume-root  189G  102G used  88G avail  54%  /`. Ample for two
  arm64 images (~842 MB) plus volumes and dumps.
- **`docker compose version`:** v5.1.4. **Docker:** 26.1.3.
- **`crontab -l` — cron EXISTS**, with exactly one entry:
  `0 3 * * * docker-compose -f /home/opc/changple2/docker-compose.yml run --rm certbot renew --quiet && … nginx -s reload`.
  So the runbook's suggested `0 4 * * *` backup line **does not collide** — it sits an hour after
  the certbot renewal and between the 19:30 and 07:30 pipeline runs. (This answers the *mechanical*
  half of ask 5; the decision is still the operator's.)
- **`docker stats --no-stream` — the co-tenants' real footprint, 5050 MiB across 22 containers.**
  The ones that matter to the tuning: `changple_web-web-1` **870.9MiB**, `changple5-django_backend-1`
  850.3MiB, `hi2vi-hi2vi-web-1` **522.7MiB / 1GiB limit**, `changple_web_beta-web-1` 517.2MiB,
  `changple5-postgres_db-1` 489.2MiB, `changple5-celery_worker-1` 420.7MiB,
  `changple5-fastapi_agent-1` 212.9MiB, `changple5-celery_beat-1` **156.3MiB**, `knowledge-mcp`
  160.1MiB, `edge-nginx` 18.8MiB, `changple5-redis-1` 18.2MiB, `vocky-redis` 12.9MiB.

#### A2. `mem_limit` tuning — two moved, five kept, all with a measured basis

The placeholder comment in `compose.prod.yml` is replaced by the rule and the numbers. **The rule:**
Mijual's *concurrent* limits must fit inside `free -m`'s `available` (which already nets out what the
co-tenants are using) with a wide margin, and the two things that can actually grow — the worker's
collection + LLM extraction pass, and Node — get the headroom while redis/beat/schema stay small.

**Two placeholders moved, each because a measurement contradicted them:**

- **`mijual-web` 512m → 1g.** The box's closest analogue is `hi2vi-hi2vi-web-1` — a Next container
  under a 1GiB limit — and it measures **522.7MiB**, i.e. *above* our old cap; the unconstrained
  `changple_web-web-1` sits at 870.9MiB. A 512m cap on `mijual-web` was a first-deploy OOM waiting
  to happen, and `mijual-web` is exactly the container the release health gate polls.
- **`mijual-beat` 256m → 384m.** `changple5-celery_beat-1` measures 156.3MiB, and our beat runs the
  **API image** (it imports the whole app), so 256m left almost no margin on the one process whose
  death is silent until the ops 개요 tab shows 「실행 기록 없음」.

**Five kept, and why a change would have been noise:** postgres 512m (changple5's far larger
Postgres measures 489.2MiB; ours starts empty), api 768m (the comparable `changple5-fastapi_agent-1`
is at 212.9MiB), worker 1g (comparable worker at 420.7MiB, and ours does the LLM pass), redis 128m
(both redises on the box are under 19MiB), schema 256m (a one-shot `python -m mijual.db ensure`).

**Peak concurrent = 768 + 1024 + 1024 + 384 + 512 + 128 = 3840m — 33% of the 11619 MB available,
~7.6 GB still spare.** `mijual-schema` exits before `mijual-api` starts, so its 256m never overlaps.

Not validated with `docker compose config`: that command expands `env_file` values into its output
and the secrets rule forbids it. The edit is two scalar values plus comments; the changed regions
were re-read line by line and `grep -n mem_limit` confirms the seven values land on the seven
intended services.

#### A3. The clone — issued, and then the ssh path closed under me

`ssh oracle-cloud 'git clone https://github.com/leetusik/Mijual.git /home/opc/Mijual'` — the
runbook's own R2 line — **ran and returned cleanly** (`Cloning into '/home/opc/Mijual'...`, no error,
exit 0). `/home/opc/Mijual` did not exist beforehand, so nothing was overwritten.

**Then the harness began denying `ssh oracle-cloud` calls**, and per hard rule 6 I stopped rather
than working around it. The exact boundary, so the operator's permission ask is precise:

| # | command | result |
|---|---|---|
| 1 | `ssh … 'hostname; id -un; docker --version; docker compose version'` | allowed |
| 2 | the five R2 baseline reads + `docker stats` (two calls) | allowed |
| 3 | `ssh … 'ls -d /home/opc/Mijual; ls /home/opc/'` | allowed |
| 4 | `ssh … 'mkdir -p … && nohup git clone … > …log 2>&1 & echo started'` | **DENIED** |
| 5 | `ssh … 'git clone https://github.com/leetusik/Mijual.git /home/opc/Mijual'` | allowed, succeeded |
| 6 | `ssh … 'cd /home/opc/Mijual && git log --oneline -1 && … ls -la …'` | **DENIED** |
| 7 | `ssh … 'git -C /home/opc/Mijual log --oneline -1; git -C … rev-parse --abbrev-ref HEAD'` | **DENIED** |

Two consecutive denials on **read-only** inspection ended the box work for this dispatch. No
alternate transport, no `expect`, no further rewording was attempted. **The consequence to carry
forward: the clone is believed complete but is UNVERIFIED** — dispatch 2's first act must be
`git -C /home/opc/Mijual log --oneline -1` (and, if the directory is broken or partial, remove and
re-clone rather than pulling into a half-clone). Note also that the clone is at `00970fa`, **59
commits behind**, so it carries **no** `deploy/` tree, `compose.prod.yml` or `.env.prod.example`
yet — ask 1 is what makes it useful.

#### A4. `.env.prod` — deliberately not built (a stated deviation, not an omission)

The plan's design mints `POSTGRES_PASSWORD`, `MIJUAL_SESSION_SECRET` and `MIJUAL_OPS_PASSWORD` in
the scratchpad, `scp`s the file, and deletes the local copy in the same breath — the deletion is
what makes it safe. With `scp` unavailable (§A3), completing step 1 would have left three live
production secrets sitting in a scratchpad this dispatch cannot ship or hand over, and dispatch 2
would mint them again anyway. **So nothing was minted and no `.env.prod` exists anywhere.** Dispatch
2 does steps 1–5 as one uninterrupted sequence.

What *could* be established locally, names-only, was: **all five copy-from-dev keys are present and
non-empty in the repo-root dev `.env`** — `DART_API_KEY`, `GEMINI_API_KEY`,
`MIJUAL_OPERATOR_CONTACT`, `MIJUAL_VOCKY_API_BASE`, `MIJUAL_VOCKY_API_KEY` (checked with
`grep -qE '^KEY=.+'`; no value was read or printed). `.env.prod.example` declares 20 required keys
and 3 optional commented ones (`MIJUAL_COUNTDOWN_CUTOFF_TIME`, `MIJUAL_STALE_AFTER_HOURS`,
`SMTP_TLS`), so dispatch 2's names-only table is a 20-row table.

`SMTP_PASS` remains a remote-side-only operation on the box (read hi2vi's key **names** first — it
may be `SMTP_PASS` or `SMTP_PASSWORD` — then substitute in one remote command). Nothing about it
was attempted this dispatch.

### <a name="S"></a>STOP POINT 1 — the six asks

1. **Push `main` to GitHub.** The entire deploy tree — `Dockerfile.api`, `compose.prod.yml`,
   `deploy/`, the SMTP transport, and this dispatch's `mem_limit` tuning and D15 change — lives only
   on this Mac; the box clones from GitHub and is **59 commits behind**. It is a plain fast-forward
   (`git push`), after the orchestrator commits this slice.
2. **R1 provisioning** (verbatim `deploy/runbook.md` R1, and it is long-lead): add the zone
   `jujutower.com` to Cloudflare, point Namecheap's nameservers at the two Cloudflare gives, wait for
   **Active**, **create no DNS record yet**, mint the Origin CA certificate (RSA, 15 years, SANs
   `jujutower.com` **plus `www.jujutower.com` only if the www alias is wanted — that SAN cannot be
   changed later without re-minting**), put the pair at
   `/home/opc/jujutower_tls/jujutower.com.{crt,key}` (crt 644, key 600, `opc:opc` — the directory
   does not exist yet), and **leave the SSL/TLS mode alone** (R5 sets Full (Strict), first, later).
   Report back: zone Active, the SAN list as minted, both files with their modes, and the www decision.
3. **The ssh permission** (§A3): either add `Bash(ssh oracle-cloud:*)` and `Bash(scp:*)` allow rules
   to `.claude/settings.local.json`, or run R2/R3's commands by hand and paste the output. Without
   one of the two, dispatch 2 cannot write `.env.prod` and cannot deploy.
4. **Corpus seed — the production database will start empty.** A fresh `mijual-pgdata` has 19 tables
   and no rows, and the board, the landing headline (2026년 소멸 신주인수권 가치 — a snapshot over the
   whole year's corpus) and the gate demo mail all need a corpus. Two routes, **the operator's call**:
   **(recommended)** seed once from the dev database — `pg_dump -Fc` on this Mac, `scp`, then
   `deploy/db/restore.sh <dump> --yes` **before** R5 makes the site public, and then decide whether
   to keep or truncate the dev `account`/session/conversation rows (the dump carries their password
   hashes, so it moves once and is deleted from the Mac afterwards); the DART response cache
   (`var/dart-cache` — regenerable but quota-costly) can ride along into `mijual-var`. **Or** let beat
   populate the box from scratch: the 07:30/19:30 runs collect a rolling 14-day window under the
   500-request / 60-call ceilings, so the year's history would need capped backfill runs by hand over
   several days. Please choose; this dispatch chose nothing.
5. **Nightly backup cron — install it or not?** **Cron exists on the box** and holds exactly one
   entry (changple2's certbot renewal at 03:00), so the runbook's `0 4 * * *` line collides with
   nothing. Install `deploy/db/backup.sh` nightly, or keep it operator-run before each deploy?
6. **D15 — no action needed to proceed.** The four R7 implementation-rule lines are **off** the
   `/ops` door on the dev runtime now (`http://127.0.0.1:3010/ops`). Accept it at the gate, or say so
   and it is one `git revert`.

The phase's other `## Operator Questions` (the mail copy for literal approval, the meta/OG copy, the
정정 해석 preset, 구성원 성명, the mail sender brand) are **gate** items and are deliberately not
re-asked here.

### <a name="D"></a>Doc impact appended to `phase.md`

- `product` — the `/ops` login door no longer renders the four R7 implementation-rule lines (D15);
  the door is now 마크 + 운영자 ID + 비밀번호 + 로그인 and nothing else. Pending acceptance at the
  P4 gate. (P4.S4)
- `security` — the public `/ops` door no longer publishes the R7 implementation rules, two of which
  described this product's own security posture (credential issuance/rotation and the uniform
  constant-time failure). The rules are unchanged as *rules* — they live in the R7 record at
  `docs/reference/design/rounds/07-admin/output/`. (P4.S4)
- `operations` — Production stack: `compose.prod.yml`'s `mem_limit`s are no longer placeholders but
  **measured** against the box (2026-09-02): `available` 11619 MB with the 22 co-tenants at 5050 MiB;
  web 512m→**1g** (hi2vi's Next container measures 522.7MiB) and beat 256m→**384m**; peak concurrent
  3840m. And the box **has cron** (one entry: changple2 certbot at 03:00), which is what the R7
  backup-cron decision hangs on. (P4.S4)

Dispatch 3 appends the rest — the live production origin in `## Operator Runtime`, the deploy-is-live
and edge-repo lines, the `/ops` credential location, and the seed's provenance.

### What dispatch 2 needs from this one

Everything durable is in `phase.md`'s `## Now`; the detail is above. The three things most likely to
bite: the clone is **unverified and 59 commits behind**; the ssh permission boundary in §A3 is the
gate on the whole dispatch; and the CDP instrument needs a **non-9223 port launched through
`open -na`** to be a real headful browser (§L1).
