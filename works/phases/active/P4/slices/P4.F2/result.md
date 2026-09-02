# P4.F2 — result (dispatch 2 of 2, the KEEP branch)

- **status:** `done`
- **summary:** The operator kept Cloudflare Web Analytics on, so this dispatch measured what the
  beacon actually contacts — **exactly one off-origin host, `static.cloudflareinsights.com`, on all
  ten loads** (five production routes × 1280/390, real Chrome 152 over CDP) — allowed that one host
  in `scripts/smoke_production.py` with the reason in a comment (**`make smoke-prod` back to
  17/17**, any other off-origin host still fails), and corrected the claim 첨부2 §4 prints for judges
  so it names the exception, who enabled it and how it was measured (PDF re-rendered, still 16
  pages). Nothing was deployed and nothing on the box changed.
- **files_changed:**
  - `/Users/sugang/projects/personal/Mijual/scripts/smoke_production.py`
  - `/Users/sugang/projects/personal/Mijual/docs/reference/challenge/submission/drafts/02_기능명세서.md`
  - `/Users/sugang/projects/personal/Mijual/docs/reference/challenge/submission/drafts/02_기능명세서.pdf`
  - `/Users/sugang/projects/personal/Mijual/works/phases/active/P4/phase.md`
  - `/Users/sugang/projects/personal/Mijual/works/phases/active/P4/slices/P4.F2/result.md`
- **validation:**
  - real-Chrome-over-CDP measurement, 5 routes × 2 viewports — **pass** (10/10 loads: off-origin host
    set = `{static.cloudflareinsights.com}`, nothing else)
  - `python3 -m py_compile scripts/smoke_production.py` — **pass**
  - `make smoke-prod` — **17 pass · 0 fail · 11.9 s, exit 0**
  - `python3 scripts/render_submission_pdf.py …/02_기능명세서.md …/02_기능명세서.pdf` — **pass**
    (1,017,619 B, **16 pages**, unchanged; the amended sentence verified in the rendered text)
  - drafts' forbidden-word grep (`mijual|미주알`, both drafts) — **0, unchanged**
  - `python3 scripts/workflow.py validate` — **pass** (only the pre-existing
    `oversized_doc_sections=11` warning)
  - `git diff --stat` — the smoke script, the 첨부2 draft + PDF, `phase.md`, this `result.md` (plus
    the orchestrator's own `start-slice` files)
- **deviations:** none from the dispatch-2 addendum. One judgment call inside step 3 is recorded
  under *The printed claim* below (the sentence names the same-origin `/cdn-cgi/rum` report endpoint,
  which the addendum did not ask for, because it is what makes 「first-party」 still defensible).
- **doc_impact:** three lines appended to `phase.md` `## Doc impact`, all tagged `(P4.F2)` —
  `security` (the signed 「No page contacts a third-party origin」 property gains one
  operator-enabled exception and must be **re-worded, not re-ticked**; the application emits nothing
  off-origin; only a real browser or an `Accept: text/html` fetch can observe it); `qa` (the
  「제3자 origin 0건」 checklist line becomes 「0건 beyond the operator-enabled Cloudflare beacon on
  production; still 0 in dev and in the local production build」, and `check_third_party` now fetches
  as a browser and allows exactly that host); `operations` (Web Analytics is ON as a zone/dashboard
  setting — flipping it needs no deploy — and **UptimeRobot is dropped by operator decision**).

---

## What the beacon actually contacts (measured, dispatch 2)

**Instrument:** real **Google Chrome 152.0.7977.65**, headful, launched through LaunchServices with
a **throwaway profile** and a fresh debug port — `open -na "Google Chrome" --args
--remote-debugging-port=9331 --user-data-dir=<scratchpad>/chrome-f2d2 --no-first-run
--no-default-browser-check` — driven over the DevTools protocol. **Never the operator's profile**,
and the instance was quit afterwards (`pgrep -f chrome-f2d2` → 0). This is the fallback the
`## Operator Runtime` manifest prescribes for this Mac (Aside's daemon does not run here and there
is no agent Aside account). **Runtime:** production, `https://jujutower.com` — Cloudflare-proxied →
`edge-nginx` → the `mijual-web` standalone build; production *is* the runtime, so there is no second
build to check. Viewports **1280×900** (desktop) and **390×844** (`mobile: true`, DSR 2).

Method: `Network.enable`, then per route — `about:blank` → clear → navigate → pump 8 s → back to
`about:blank` and pump 2.5 s (so any `sendBeacon` queued at unload is captured too) → collect every
`Network.requestWillBeSent`. Read-only: **no `POST /api/ask` turn, no click, no form submit, no
account.** Script and raw capture:
`<scratchpad>/f2d2/measure.py`, `<scratchpad>/f2d2/hosts.json`.

| route | @1280 | @390 |
|---|---|---|
| `/` | `jujutower.com` (37) · `static.cloudflareinsights.com` (1) | `jujutower.com` (27) · `static.cloudflareinsights.com` (1) |
| `/stocks` | `jujutower.com` (38) · `static.cloudflareinsights.com` (1) | `jujutower.com` (33) · `static.cloudflareinsights.com` (1) |
| `/stocks/00547510` | `jujutower.com` (40) · `static.cloudflareinsights.com` (1) | `jujutower.com` (33) · `static.cloudflareinsights.com` (1) |
| `/events/20250902000288` | `jujutower.com` (37) · `static.cloudflareinsights.com` (1) | `jujutower.com` (32) · `static.cloudflareinsights.com` (1) |
| `/portfolio?sample=1` | `jujutower.com` (38) · `static.cloudflareinsights.com` (1) | `jujutower.com` (32) · `static.cloudflareinsights.com` (1) |

**The host set is identical on all ten loads: exactly one off-origin host.** The single request to it
is, every time:

```
GET https://static.cloudflareinsights.com/beacon.min.js/v3d52b47920f24c319d37e2661827c42b1787588026925   [Script]
```

Three facts that decide the wording of every claim below, all from the full request list of `/`
(`<scratchpad>/f2d2/allreqs.py`):

1. **The beacon reports SAME-ORIGIN.** `POST https://jujutower.com/cdn-cgi/rum?` `[XHR]` — the RUM
   endpoint is on the apex, terminated at Cloudflare's edge, so the expected second host
   (`cloudflareinsights.com/cdn-cgi/rum`) never appears. One off-origin host is the whole footprint.
2. **There is a second, same-origin edge injection:**
   `GET https://jujutower.com/cdn-cgi/scripts/5c5dd728/cloudflare-static/email-decode.min.js`
   `[Script]` — Cloudflare Email Obfuscation, rewriting the footer's 운영자 연락처 `mailto:`. Also not
   the application's code, also not a third-party origin. Recorded so nobody re-discovers it as a
   finding.
3. **`dart.fss.or.kr` is not requested on load at all** — it is an `href` the reader clicks, exactly
   as the plan predicted. It stays in `ALLOWED_EXTERNAL_HOSTS` because the *check* is about
   references in the HTML, not about requests.

## The smoke suite (`scripts/smoke_production.py`, +21 / −6)

`ALLOWED_EXTERNAL_HOSTS` is now `{"dart.fss.or.kr", "static.cloudflareinsights.com"}`, and the
comment above it carries the whole reason: operator-enabled Cloudflare Web Analytics, 2026-09-02,
injected **at the edge** into `Accept: text/html` responses (the application emits nothing
off-origin), cookieless, report endpoint same-origin, measured in real Chrome 152 over CDP on five
routes at 1280/390 — **"an allowance, not an amnesty: any other off-origin host is still a
failure."** The module docstring's fifth easy-to-get-wrong bullet gained the same one-sentence
qualifier, and the check's pass line names the allowance rather than just listing hosts:

```
PASS  third-party      1078ms  2 page(s) as text/html · no off-origin src/href beyond
                               dart.fss.or.kr, static.cloudflareinsights.com
                               (the DART 원문 links + the operator-enabled Cloudflare beacon, edge-injected)
── 17 pass · 0 fail · 11.9s ──
```

Nothing else in the script changed — dispatch 1's `accept=` keyword and the check's own
`Accept: text/html` fetches are what make the allowance meaningful rather than decorative: the check
can *see* the beacon and chooses to permit exactly it.

## The printed claim (첨부2 §4)

`02_기능명세서.md` §4's 「Everything is first-party」 bullet said 「Measured on the live pages: **no
page contacts a third-party origin** — no analytics, no external font or script, no beacon」. That
sentence is false in three of its four clauses today. It now reads (English body, as the rest of
첨부2): **Everything is first-party, with one named exception** — the application itself contacts no
third-party origin (no external font, no external script, no tracking pixel; the only external
references in the HTML *it* emits are the DART 원문 links), and the one off-origin request a live
page makes is **Cloudflare Web Analytics**, `static.cloudflareinsights.com/beacon.min.js`, enabled by
the operator at the CDN edge, injected into the response by Cloudflare rather than emitted by the
application, cookieless, reporting to the same-origin `POST /cdn-cgi/rum` — measured 2026-09-02 in
real Google Chrome 152 over the DevTools protocol, five pages at 1280 px and 390 px, every request
going to `jujutower.com` or to that one host and nothing else, with the production regression suite
asserting the same on every run.

Three deliberate choices in that wording: it separates **what the application does** from **what the
CDN adds** (the entrant's honest claim survives, and it is the true one); it names the same-origin
report endpoint, because 「first-party」 would otherwise invite the obvious objection; and it prints
the **method** (real browser, viewports, date), since the earlier claim was false precisely because
`curl` cannot observe this property.

- `grep -n 'third-party|제3자|beacon|analytics|Analytics'` over **`01_공모전기획서.md`** → **no
  match**: 첨부1 never printed the claim, so it is unedited and **not re-rendered**.
- PDF re-rendered: `02_기능명세서.pdf` 1,013,532 → 1,017,619 B, **16 pages before and after** — the
  page count did **not** move. The amended sentence is in the rendered text (`pdftotext -layout`,
  p. ~11), and both drafts still grep **0** for the forbidden package identifier.

## Hard rules, kept

No deploy, no image rebuild, **nothing on the box** — production is untouched at `96f7141` and the
freeze (2026-09-07 11:00 → 09-11 23:59 KST) is irrelevant to this slice. Every production request
was a **GET** except the beacon's own `POST /cdn-cgi/rum`, which the browser issues by itself.
No secret value appears in any changed file. No `git commit`, no `git push`, no workflow
state-transition command; `uv run python …` with no `--with`. The operator's dev stack was never
touched (this dispatch needed no local build at all).

## Notebook

`phase.md` carries the durable half and is not restated here: `## Decisions` — the Web Analytics
entry **replaced in place** with the operator's ON decision (plus the measured host set) and a new
entry recording that UptimeRobot is dropped and `P4.REVIEW` finding 3 is closed by that answer;
`## Operator Questions` — dispatch 1's entry marked **ANSWERED AND DONE: keep** with the hosts and
what ran, plus a new ANSWERED entry for UptimeRobot / the probe cadence; `## Doc impact` — the three
lines quoted in the verdict block; `## Notes for later slices` — the consumed
`(from P4.REVIEW, for P4.F2)` block **removed**, and one new `(from P4.F2, for P4.REVIEW)` block
warning that the parked P4 `## Regression Checklist` block's 제3자 line is now stale in its host list
and that neither finding may be re-raised; `## Now` — rewritten for `P4.F4` then the re-review.

---

## Dispatch 1 — the log, unchanged

_Dispatch 1 ended `needs_operator` (the zone setting is the operator's dashboard action). Its
verdict block and measurements are kept verbatim below; where the two disagree, dispatch 2 above is
the outcome._

- **status:** `needs_operator`
- **summary:** Hardened `scripts/smoke_production.py`'s `third-party` check to fetch as a browser
  does (`Accept: text/html`, its own fetches of `/` and one 종목 page), which makes `make smoke-prod`
  go **red on exactly that check** against production today — 16 pass · 1 fail naming
  `static.cloudflareinsights.com` — while the same check is **green** against a local production
  build. The beacon is a Cloudflare **zone setting**, so the slice stops for the operator's
  dashboard action; dispatch 2 re-measures (or amends the claims) afterwards.
- **files_changed:**
  - `/Users/sugang/projects/personal/Mijual/scripts/smoke_production.py`
  - `/Users/sugang/projects/personal/Mijual/works/phases/active/P4/phase.md`
  - `/Users/sugang/projects/personal/Mijual/works/phases/active/P4/slices/P4.F2/result.md`
- **validation:**
  - `python3 -m py_compile scripts/smoke_production.py` — **pass**
  - `make smoke-prod` — **16 pass · 1 fail (`third-party`), exit 1 — the intended red**
  - `check_third_party` called directly against the local production build on `127.0.0.1:3013` —
    **green** (`2 page(s) as text/html · no off-origin src/href beyond dart.fss.or.kr`)
  - `python3 scripts/workflow.py validate` — **pass** (only the pre-existing
    `oversized_doc_sections=11` warning)
  - `git diff --stat` — `scripts/smoke_production.py` only (plus this `result.md` and `phase.md`)
- **deviations:** two, both small — see *Deviations* below (a 종목 page is scanned as well as the
  landing, which the plan made optional; and the local proof needed a clean rebuild of the frontend
  clone with a self-origin `NEXT_PUBLIC_SITE_URL`).
- **doc_impact:** none in this dispatch — per `plan.md`, the `qa` and `security` lines are dispatch
  2's, because their wording depends on which branch the operator takes.
- **operator_need:** turn Cloudflare Web Analytics **off** for `jujutower.com` (or say you want to
  keep it) — the verbatim ask is in *The operator ask* below and in `phase.md`
  `## Operator Questions`.

---

### What was measured (production, read-only GETs, 2026-09-02)

Cloudflare injects its Web Analytics beacon **only into `Accept: text/html` responses**; the
User-Agent makes no difference. Reproduced from this laptop with `curl` alone:

| request to `https://jujutower.com/` | `grep -c cloudflareinsights` |
|---|---|
| `-A 'Mijual-smoke/1.0 (+https://jujutower.com)' -H 'Accept: */*'` (what the suite sent) | **0** |
| Chrome 152 User-Agent, `Accept: */*` | **0** |
| `-A 'Mijual-smoke/1.0' -H 'Accept: text/html'` | **1** |
| `/stocks/00547510` with `Accept: text/html` | **1** |

The injected tag, verbatim from the served HTML (double-quoted `src`, so the check's existing
`(?:src|href)\s*=\s*"…"` regex matches it unchanged):

```html
<script type="module" src="https://static.cloudflareinsights.com/beacon.min.js/v3d52b47920f24c319d37e2661827c42b1787588026925"
        integrity="sha512-d9sL6GJ…" data-cf-beacon='{"version":"2024.11.0","token":"…","r":1}' crossorigin="anonymous">
```

That is the whole explanation for why every earlier check passed: `check_third_party` scanned an
HTML body that never had the tag. Nothing in `frontend/` is implicated — the local production build
of the same routes reaches no host but its own (confirmed again below).

### The diff (`scripts/smoke_production.py`, +44 / −21, one file)

1. **`fetch()` gained an `accept: str = "*/*"` keyword** (the smallest of the two shapes the plan
   offered) and a docstring line saying why. Every existing call site is unchanged and still sends
   `*/*`.
2. **`check_third_party` does its own fetches** and no longer reads `ctx["landing_html"]`. It fetches
   `/` with `Accept: text/html`, plus `/stocks/{corp_code}` when `check_board` has already put a
   `corp_code` in `ctx` (it runs earlier in `CHECKS`, so on a full run it has). `check_landing` is
   untouched and keeps its `*/*` fetch — its assertions are about the origin's own HTML and headers.
   The regex and `ALLOWED_EXTERNAL_HOSTS` (`dart.fss.or.kr`) are unchanged; the failure detail now
   names the page a reference was found on. Pass line: `2 page(s) as text/html · no off-origin
   src/href beyond dart.fss.or.kr`.
3. **The module docstring's list went from four to five** easy-to-get-wrong bullets. The new one:
   Cloudflare injects the Web Analytics beacon at the edge **only** into `Accept: text/html`
   responses — the User-Agent is irrelevant — so a `*/*` fetch can never see an edge-injected
   script, measured 2026-09-02 (P4.F2).
4. **The `CHECKS` ordering comment** no longer says 「`landing` feeds `third-party`」; it now records
   that `board` feeds the 종목 page `third-party` also scans and that `third-party` fetches its own
   `text/html` pages.

No test file was added — per `CLAUDE.md`'s test rule this suite is verified live, and it just was,
both red and green.

### Proof, both directions

**Red against production** (`make smoke-prod`, 10.8 s, exit 1):

```
PASS  landing           703ms  200 · 353911 bytes · HSTS + CSP · cf-ray a34c4e1f98f10717-HKG
…
FAIL  third-party      1143ms  off-origin reference(s): static.cloudflareinsights.com
                               (https://static.cloudflareinsights.com/beacon.min.js/v3d52b479… on /)
PASS  cotenants        1482ms  200 ×3 — hi2vi.com, vocky.hi2vi.com, changple.ai
── 16 pass · 1 fail · 10.8s ──
FAILED: third-party
```

Every other check still passes, including `www` (the `P4.F1` MagicDNS false FAIL did not reproduce)
and the three co-tenants.

**Green against a local production build** — proving the hardened check does not false-alarm on the
product's own HTML. Built **additively**, exactly as `P4.REVIEW` did: an APFS clone of `frontend/`
in the session scratchpad, `npm run build` (`NEXT_PUBLIC_SITE_URL=http://127.0.0.1:3013`,
`MIJUAL_API_ORIGIN=http://127.0.0.1:8010`), then the standalone server (`node
.next/standalone/server.js`, the container's own entrypoint) on `127.0.0.1:3013` against the
operator's dev API on 8010. `--light` skips `third-party`, so the check was called directly:

```
board      : 200 · 375 rows · sample 제이에스링크 20250902000288
third-party: 2 page(s) as text/html · no off-origin src/href beyond dart.fss.or.kr
```

and, independently, `curl -H 'Accept: text/html' http://127.0.0.1:3013/` and
`…/stocks/00642541` both grep **0** for `cloudflareinsights`. The build server was stopped
afterwards (port 3013 free). **The operator's stack was never stopped or restarted** — web pid
47136 on `:3010` still answers 200 and api pid 60158 on `:8010` still answers `{"status":"ok"}`, on
their original pids.

**Instrument:** none — this dispatch needed no browser. Every production request was a `curl` or
`urllib` **GET**; no `POST /api/ask`, no account, no write, no deploy, no image rebuild, nothing on
the box touched. The real-browser re-measurement (real Chrome 152 over CDP, headful, 1280/390, five
routes) is dispatch 2's, per the plan.

### Deviations from `plan.md`

1. **The 종목 page scan was taken, not skipped.** The plan made it optional 「only if it stays a few
   lines」 — it is four lines (a `paths` list plus one `if`), it reuses the `corp_code` `check_board`
   already resolves, and it is the second page `P4.REVIEW` measured the beacon on. If `board` fails
   or is skipped, `paths` is just `["/"]`, so the check never depends on it.
2. **The local proof needed a clean rebuild with a self-origin `NEXT_PUBLIC_SITE_URL`.** With the
   plan's `NEXT_PUBLIC_SITE_URL=https://jujutower.com`, the build's own canonical/`og:url`/`og:image`
   are absolute apex URLs, which the check correctly reports as an off-origin host when the same
   build is served from `127.0.0.1:3013` (`off-origin reference(s): jujutower.com (…)`). That is the
   check working, not a false alarm — but it does not *prove* no-false-alarm, so the clone was
   rebuilt with `NEXT_PUBLIC_SITE_URL=http://127.0.0.1:3013` for a genuinely green run. Two traps
   worth carrying: `NEXT_PUBLIC_*` is inlined at build time and a warm `.next` will keep the old
   value (the `.next` directory had to be moved aside for the value to change), and a still-running
   standalone server holds the port and the new one silently `EADDRINUSE`s into its log.
3. **No `## Doc impact` line was filed in this dispatch**, per the plan: both lines (`qa`,
   `security`) are dispatch 2's, and their wording depends on the branch the operator takes.

### The operator ask (verbatim, for the orchestrator to relay)

> Turn Cloudflare Web Analytics **off** for `jujutower.com`: Cloudflare dashboard → *Analytics &
> Logs* → *Web Analytics* → the `jujutower.com` site → *Manage site* → disable **automatic setup**
> (the injected JS snippet), or remove the site. Confirm with
> `curl -s -H 'Accept: text/html' https://jujutower.com/ | grep -c cloudflareinsights` → `0`
> (it prints `1` today). If you would rather **keep** analytics, say so instead and dispatch 2
> amends the three claims rather than the zone.

Turning it off changes nothing in the product and needs **no deploy** — so it lands safely on either
side of the 2026-09-07 11:00 → 09-11 23:59 KST freeze, and production stays at `96f7141`.

### Notebook

`phase.md` carries the durable half: one new `## Operator Questions` entry (the question above with
its measured facts, the dashboard path and what each branch costs), and a rewritten `## Now`.
`## Decisions` was **not** touched — `P4.REVIEW` already corrected the Web Analytics entry in place —
and `P4.REVIEW`'s note block for this slice was **kept**, because dispatch 2 still consumes it.
