# P4.F2 — Cloudflare Web Analytics off: re-measure the no-third-party-origin property, harden `check_third_party`, re-date the printed claim

Fix slice cut by `P4.REVIEW` (finding 1, MATERIAL). Tier `slice-executor-high`. **Two dispatches
with an operator stop between them** — dispatch 1 ends `needs_operator`, because the zone setting
lives in the operator's Cloudflare dashboard and nothing in this repo can flip it.

## The finding, in one paragraph

`P4.REVIEW` opened `https://jujutower.com` in real Chrome 152 and saw every one of ten routes, at
1280 and 390, load `https://static.cloudflareinsights.com/beacon.min.js/v3d52b…` (200) from a
`<script type="module" src=…>` tag that Cloudflare injects **at the edge** — the local production
build of the same routes reaches no host but its own. That is Cloudflare **Web Analytics** with
automatic setup, exactly the feature the phase's `## Decisions` entry says 「stays OFF」, and it
falsifies `security.md`'s signed 「No page contacts a third-party origin」 property, the `P4.S5`/`P4.S6`
Doc impact claims, the `## Regression Checklist` line 「제3자 origin 0건」, and — printed for judges —
`02_기능명세서.md` §4 (line ~302: 「Measured on the live pages: **no page contacts a third-party
origin** — no analytics, no external font or script, no beacon…」). The intent's DECOMP constraint
already ruled it out by name: 「Do not add a third-party origin to any page … that rules out
Cloudflare Web Analytics」.

**Why every earlier check passed, measured by the orchestrator 2026-09-02 (read-only GETs):**
Cloudflare injects the tag only into responses to requests that carry **`Accept: text/html`**.
`scripts/smoke_production.py`'s `fetch()` sends `Accept: */*` (line ~112), so `check_third_party`
(line ~346) scans HTML that never had the tag. The User-Agent is irrelevant:

| request | `cloudflareinsights` in body |
|---|---|
| `-A 'Mijual-smoke/1.0'` (Accept `*/*`) | 0 |
| Chrome UA, Accept `*/*` | 0 |
| **`-A 'Mijual-smoke/1.0' -H 'Accept: text/html'`** | **1** (also on `/stocks/00547510`) |

## Hard rules

- **No deploy, no image rebuild, nothing on the box changes.** The smoke suite is laptop-side; the
  document is a repo file. Production stays at `96f7141`. Freeze 2026-09-07 11:00 → 09-11 23:59 KST.
- Production is **read-only**: GETs, and at most **one** `POST /api/ask` (dispatch 2 only, and only
  if you need `/ask` in the five-route measurement — you do not; open `/ask` without sending).
- **No secret values** anywhere; the repo is public.
- Browser: real Google Chrome over CDP, headful, `open -na "Google Chrome" --args
  --remote-debugging-port=<fresh port> --user-data-dir=<throwaway in the session scratchpad>`, never
  the operator's profile; a `nohup` launch is headless and does not count. Viewports 1280 and 390.
  Name the instrument in `result.md`.
- Never run `accept-gate`, `defer-job`, `review-phase`, `git commit`, `git push`.
- `uv` discipline: `uv run pytest`, never `uv run --with`.

## Dispatch 1 — harden the check, prove it red, stop for the operator

1. **`scripts/smoke_production.py` — make `check_third_party` see what a browser sees.**
   - Give `fetch()` an optional `accept: str = "*/*"` keyword (or an `html=True` switch — your
     call, smallest diff) and have `check_third_party` do its **own** fetch of `/` with
     `Accept: text/html`, never reusing `ctx["landing_html"]` (which `check_landing` fetched with
     `*/*` and which must keep doing so — its assertions are about the origin's HTML). Update the
     `CHECKS` comment 「`landing` feeds `third-party`」 accordingly.
   - Keep the existing `src|href` regex — it already matches the injected `<script … src="https://
     static.cloudflareinsights.com/…">`. Keep `ALLOWED_EXTERNAL_HOSTS` as is (`dart.fss.or.kr`).
   - Add the fifth "easy to get wrong" bullet to the module docstring: **Cloudflare injects its Web
     Analytics beacon only into `Accept: text/html` responses**, so a `*/*` fetch can never see an
     edge-injected script; measured 2026-09-02.
   - Optionally scan one 종목 page too (`ctx` already knows a `corp_code` from `check_board`) — only
     if it stays a few lines; the landing alone is acceptable.
2. **Prove it.** `make smoke-prod` must now go **red on exactly `third-party`** (16 pass · 1 fail,
   `off-origin reference(s): static.cloudflareinsights.com (…)`) while the zone setting is still on.
   Then prove the check does not false-alarm: start the local production build
   (`cd frontend && NEXT_PUBLIC_SITE_URL=https://jujutower.com npm run build && npm run start -- -p
   3013` against the dev API on 8010 — do **not** stop the operator's stack; the review was denied
   `make stack-down`, so add, never replace) and run `python3 scripts/smoke_production.py --base
   http://127.0.0.1:3013 --light`… `--light` skips `third-party`, so instead call the check directly
   (a two-line `python3 -c` importing the module and running `check_third_party` with a ctx for
   that base) → green. Stop the build server afterwards.
3. **`tests/`** — nothing. The suite is verified live, per `CLAUDE.md`'s test rule.
4. **`phase.md`**: append one `## Operator Questions` entry — 「**CLOUDFLARE WEB ANALYTICS IS ON —
   turn it off (the phase's decision and the intent's constraint), or keep it and amend the
   claims?**」 with the measured facts, the dashboard path, and what each branch costs (off: nothing
   in the product changes and dispatch 2 re-measures and re-dates; keep: 첨부2 §4, `security.md`'s
   checkbox via a Doc impact line, and the checklist line are amended to say the beacon exists) —
   tag `(P4.F2)`. Do **not** touch `## Decisions` (the review already corrected the entry in
   place). Rewrite `## Now` (≤ 15 lines): `P4.F2` waiting on the operator's dashboard action, the
   exact re-check the operator can do (`curl -s -H 'Accept: text/html' https://jujutower.com/ |
   grep -c cloudflareinsights` → `0`), dispatch 2's scope, then the re-review; keep the freeze
   line and the gate-shut line.
5. **`result.md`** verdict-block-first, then the measurements, the diff summary, the local proof.
   Return **`needs_operator`** with the ask below, verbatim enough for the orchestrator to relay:

   > Turn Cloudflare Web Analytics **off** for `jujutower.com`: Cloudflare dashboard → *Analytics &
   > Logs* → *Web Analytics* → the `jujutower.com` site → *Manage site* → disable **automatic
   > setup** (the injected JS snippet), or remove the site. Confirm with
   > `curl -s -H 'Accept: text/html' https://jujutower.com/ | grep -c cloudflareinsights` → `0`
   > (it prints `1` today). If you would rather **keep** analytics, say so instead and dispatch 2
   > amends the three claims rather than the zone.

## Dispatch 2 — after the operator acts (the orchestrator appends the branch taken here)

- **Off branch (default):** re-measure in real Chrome at 1280 and 390 across five routes — `/`,
  `/stocks`, `/stocks/00547510`, one `/events/{rcept_no}` from the live board, `/portfolio?sample=1`
  — capturing `Network.requestWillBeSent` for each load: every request host must be
  `jujutower.com` (a `dart.fss.or.kr` request appears only on a click, never on load). Record the
  per-route host sets. `make smoke-prod` → **17/17** with the hardened check. Then **re-date the
  printed claim**: edit `02_기능명세서.md` §4's sentence to say when and how it was measured (real
  Chrome 152 over CDP, five routes, 1280/390, the date, `make smoke-prod`'s `third-party` check
  now fetching as a browser does) and re-render the PDF with
  `python3 scripts/render_submission_pdf.py docs/reference/challenge/submission/drafts/02_기능명세서.md
  docs/reference/challenge/submission/drafts/02_기능명세서.pdf` (page count may move by one; say
  so). Append `## Doc impact` lines: `security` (the property is **true again as of <date>**,
  measured in a real browser; a `*/*` fetch cannot assert it, `Accept: text/html` can; the
  `[x]` may be re-asserted with that caveat) and `qa` (`check_third_party` fetches as a browser;
  the checklist line 「제3자 origin 0건」 gains 「and on production through Cloudflare」). Mark the
  Operator Question **ANSWERED AND DONE**.
- **Keep branch:** no re-measure needed; amend 첨부2 §4 to state the beacon exists and what it is,
  re-render the PDF, append Doc impact lines for `security` (the property no longer holds on
  production; the checkbox must be unticked with the beacon named) and `qa` (the checklist line
  must exempt `static.cloudflareinsights.com` on production, or be reworded), and add
  `static.cloudflareinsights.com` to `ALLOWED_EXTERNAL_HOSTS` **only if the operator says so** —
  otherwise `make smoke-prod` stays red by design and the Doc impact line says why.
- Either branch: rewrite `## Now` for `P4.REVIEW`'s re-run (it starts from the top, gate stages
  included; the parked P4 regression block is in `slices/P4.REVIEW/result.md` § Stage C-4).

## Validate (dispatch 1)

- `python3 -m py_compile scripts/smoke_production.py`; `make smoke-prod` → 16 pass · **1 fail
  (`third-party`, naming `static.cloudflareinsights.com`)**; the direct check against the local
  production build → green; `python3 scripts/workflow.py validate` → passes; `git diff --stat` →
  `scripts/smoke_production.py`, `phase.md`, this slice's `result.md` only.

## Dispatch 2 — branch taken: KEEP (orchestrator addendum, 2026-09-02 ~22:10 KST)

The operator answered dispatch 1's ask with **「And I enabled the analytics.」** — Cloudflare Web
Analytics is on by the operator's own choice and stays on. Take the **keep branch** above, with
these specifics (they override the generic keep paragraph where they differ):

1. **Measure what the beacon actually contacts**, once, in real Chrome over CDP (headful, throwaway
   profile, fresh port) at 1280 and 390 on five production routes (`/`, `/stocks`,
   `/stocks/00547510`, one live `/events/{rcept_no}`, `/portfolio?sample=1`): capture
   `Network.requestWillBeSent` per load and list every off-origin host — expect
   `static.cloudflareinsights.com` (the script) and the beacon's own report endpoint (likely
   `cloudflareinsights.com/cdn-cgi/rum`, possibly on the apex under `/cdn-cgi/…`). Record the exact
   host set per route in `result.md`; the claims below name exactly those hosts. No `/api/ask` turn.
2. **`scripts/smoke_production.py`**: add the measured beacon host(s) to `ALLOWED_EXTERNAL_HOSTS`
   with a comment that says why — *operator-enabled Cloudflare Web Analytics, 2026-09-02; injected at
   the edge for `Accept: text/html` responses; any other off-origin host is still a failure* — and
   make the `third-party` check's return line name the allowance. `make smoke-prod` → **17/17**.
   Nothing else in the script changes.
3. **The printed claim**: edit `docs/reference/challenge/submission/drafts/02_기능명세서.md` §4 (the
   sentence at ~line 302) so it is true: no page contacts a third-party origin **except Cloudflare's
   Web Analytics beacon** (`static.cloudflareinsights.com`, cookieless, enabled by the operator at
   the edge, not by the application), measured in real Chrome 152 on 2026-09-02; the application's
   own HTML references no external host but the DART 원문 links. Also `grep -n 'third-party\|제3자'`
   in `01_공모전기획서.md` and fix the same claim there if it appears. Re-render the PDF(s) with
   `python3 scripts/render_submission_pdf.py <md> <pdf>`; report page counts.
4. **`phase.md`**:
   - `## Decisions`: replace the 「Cloudflare Web Analytics stays OFF」 entry (already corrected in
     place by the review) with the operator's decision: **ON, deliberately, 2026-09-02** — the
     no-third-party-origin property is now *「no third-party origin except the operator-enabled
     Cloudflare beacon」*; the application itself still references none.
   - `## Operator Questions`: mark dispatch 1's entry **ANSWERED AND DONE: keep** with the hosts.
     And mark the `P4.S6` entry about UptimeRobot / the probe **ANSWERED (operator, 2026-09-02):
     「drop uptime bot and system up checker. just fine if it works now.」** — no UptimeRobot, the
     probe's cadence (review finding 3) is closed by operator decision, the Actions workflow stays as
     it is. Add the same as a `## Decisions` line so the re-review does not re-raise it.
   - `## Doc impact` (append, tag `(P4.F2)`): `security` — the signed 「No page contacts a
     third-party origin」 property gains one operator-enabled exception (name the hosts; the
     application emits nothing off-origin; the checkbox must be re-worded, not simply re-ticked;
     only a real-browser or `Accept: text/html` fetch can observe it); `qa` — the checklist line
     「제3자 origin 0건」 becomes 「0건 beyond the operator-enabled Cloudflare beacon on production;
     still 0 in dev and the local production build」, and `check_third_party` now fetches as a
     browser and allows exactly that host; `operations` — Cloudflare Web Analytics is ON as a
     zone/dashboard setting (on/off needs no deploy) and UptimeRobot is dropped by operator decision.
   - `## Now` (≤ 15 lines): `P4.F2` done; **`P4.F4` next** — the operator's 2026-09-02 instruction
     「give relaxed extract max call to the prod, I don't want to miss a thing」: a
     `MIJUAL_EXTRACT_MAX_CALLS` env knob (code) + `.env.prod` value + deploy before the freeze; then
     the re-review (from the top, gate stages included; its walkthrough must **not** carry
     UptimeRobot, the Cloudflare toggle, or the runbook item).
5. **Validate**: `python3 -m py_compile scripts/smoke_production.py`; `make smoke-prod` 17/17;
   the drafts' forbidden-word greps still 0; `python3 scripts/workflow.py validate`; `git diff
   --stat` → the smoke script, the draft(s) + PDF(s), `phase.md`, `result.md`.
6. **`result.md`**: rewrite the verdict block first for dispatch 2 (`status: done`), keep dispatch
   1's log under `## Dispatch 1`. No deploy, nothing on the box, no commit.
