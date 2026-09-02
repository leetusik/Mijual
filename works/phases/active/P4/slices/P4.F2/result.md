# P4.F2 — result (dispatch 1 of 2)

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

## What was measured (production, read-only GETs, 2026-09-02)

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

## The diff (`scripts/smoke_production.py`, +44 / −21, one file)

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

## Proof, both directions

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

## Deviations from `plan.md`

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

## The operator ask (verbatim, for the orchestrator to relay)

> Turn Cloudflare Web Analytics **off** for `jujutower.com`: Cloudflare dashboard → *Analytics &
> Logs* → *Web Analytics* → the `jujutower.com` site → *Manage site* → disable **automatic setup**
> (the injected JS snippet), or remove the site. Confirm with
> `curl -s -H 'Accept: text/html' https://jujutower.com/ | grep -c cloudflareinsights` → `0`
> (it prints `1` today). If you would rather **keep** analytics, say so instead and dispatch 2
> amends the three claims rather than the zone.

Turning it off changes nothing in the product and needs **no deploy** — so it lands safely on either
side of the 2026-09-07 11:00 → 09-11 23:59 KST freeze, and production stays at `96f7141`.

## Notebook

`phase.md` carries the durable half: one new `## Operator Questions` entry (the question above with
its measured facts, the dashboard path and what each branch costs), and a rewritten `## Now`.
`## Decisions` was **not** touched — `P4.REVIEW` already corrected the Web Analytics entry in place —
and `P4.REVIEW`'s note block for this slice was **kept**, because dispatch 2 still consumes it.
