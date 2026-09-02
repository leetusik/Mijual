#!/usr/bin/env python3
"""Production smoke suite for 주주의관제탑 — the live origin, end to end.

Run it against the PUBLIC origin, never a local stack: every check travels
Cloudflare → the shared edge nginx → the `mijual-web` container → (for `/api/*`)
Next's rewrite → FastAPI, so one green run says the whole chain is intact.

    make smoke-prod                                   # the whole suite
    python3 scripts/smoke_production.py               # the same thing
    python3 scripts/smoke_production.py --light       # only the two probe checks
    python3 scripts/smoke_production.py --no-cotenants
    python3 scripts/smoke_production.py --base https://jujutower.com

Stdlib only, on purpose: the operator runs this from a laptop with nothing
installed, and CI runs it with no dependency step.

Nothing here spends money or writes data. Every request is a GET; there is no
`POST /api/ask` (that one is a model call — `GET /api/ask/start-cards` is its
free sibling), no account creation, no mutation of any kind.

Four things that are easy to get wrong here, each of them measured (P4.S4, P4.S5,
P4.S6) rather than assumed:

- **Send a User-Agent.** Bare urllib gets Cloudflare's `403 error 1010`.
- **Probe with GET, never HEAD.** `HEAD /api/health` answers **405** — the Next
  route handler exports `GET` only — so a HEAD-based monitor alerts forever on a
  perfectly healthy product. Assert on the BODY, not just on the status.
- **Read the SERVED `robots.txt`.** Cloudflare prepends its own managed
  content-signals block to whatever the origin returns; the origin's own rules
  come after it, and that second half is what `robots` asserts on.
- **Do not follow redirects** unless the check is *about* the redirect: `www` and
  `http-redirect` assert on the 301 itself, and everything else would silently
  pass on a redirected page.

Exit status is 0 only when every check passed.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

DEFAULT_BASE = "https://jujutower.com"
UA = "Mijual-smoke/1.0 (+https://jujutower.com)"
TIMEOUT = 20
KST = timezone(timedelta(hours=9))

#: The box's other doors. Mijual shares one nginx and one host with them, so a
#: smoke run that only looked at Mijual could call a deploy green while it had
#: taken a neighbour down. This is the runbook's R7 no-harm assertion, in code.
CO_TENANTS = ("https://hi2vi.com/", "https://vocky.hi2vi.com/", "https://changple.ai/")

#: The four R7 implementation-rule lines D15 removed from the *public* `/ops`
#: door (P4.S4). Two of them described this product's own security posture, so
#: their return to an unauthenticated page is a regression, not a copy tweak.
#: The rules themselves are unchanged in the R7 record.
OPS_FORBIDDEN = (
    "reader chrome 어디에서도 링크 금지",
    "가입·재설정 UI 없음",
    "실패 응답 균일",
    "세션 만료",
)

#: The only external host any reader page may reference (the DART 원문 links).
#: `schema.org` appears in the JSON-LD as an `@context` *string* and is never
#: fetched, so it is not a `src`/`href` and does not belong here.
ALLOWED_EXTERNAL_HOSTS = {"dart.fss.or.kr"}


class Fail(Exception):
    """A check's own verdict. The message is what the table prints."""


def need(condition: object, message: str) -> None:
    if not condition:
        raise Fail(message)


class Resp:
    __slots__ = ("status", "headers", "body", "url")

    def __init__(self, status, headers, body, url):
        self.status = status
        self.headers = headers
        self.body = body
        self.url = url

    def text(self) -> str:
        return self.body.decode("utf-8", "replace")


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    """Return the 3xx itself instead of chasing it (as an HTTPError, below)."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


_NO_REDIRECT_OPENER = urllib.request.build_opener(_NoRedirect)
_FOLLOW_OPENER = urllib.request.build_opener()


def fetch(url: str, *, follow: bool = False) -> Resp:
    """GET `url` with a User-Agent, never raising for a non-2xx status."""
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    opener = _FOLLOW_OPENER if follow else _NO_REDIRECT_OPENER
    try:
        with opener.open(req, timeout=TIMEOUT) as r:
            return Resp(r.getcode(), r.headers, r.read(), r.geturl())
    except urllib.error.HTTPError as e:
        # A 3xx reaches here too, because _NoRedirect declines to follow it.
        try:
            body = e.read()
        except Exception:  # pragma: no cover - defensive
            body = b""
        return Resp(e.code, e.headers, body, url)
    except urllib.error.URLError as e:
        raise Fail(f"{url} unreachable: {e.reason}") from None


def _attr(tag: str, name: str) -> str | None:
    m = re.search(rf'{name}\s*=\s*"([^"]*)"', tag, re.I)
    return m.group(1) if m else None


def _png_size(body: bytes) -> tuple[int, int] | None:
    if len(body) >= 24 and body[:8] == b"\x89PNG\r\n\x1a\n" and body[12:16] == b"IHDR":
        return int.from_bytes(body[16:20], "big"), int.from_bytes(body[20:24], "big")
    return None


# ── the checks ───────────────────────────────────────────────────────────────
# Each takes the run context and returns the one-line detail the table prints,
# or raises Fail(reason). Anything a later check needs goes back into ctx.


def check_health(ctx):
    r = fetch(ctx["base"] + "/api/health")
    need(r.status == 200, f"HTTP {r.status} (want 200)")
    try:
        d = json.loads(r.text())
    except ValueError:
        raise Fail(f"body is not JSON: {r.text()[:120]!r}") from None
    need(d.get("status") == "ok", f'status={d.get("status")!r} (want "ok")')
    raw = d.get("now_kst")
    need(raw, "no now_kst in the payload")
    try:
        stamp = datetime.fromisoformat(raw)
    except ValueError:
        raise Fail(f"now_kst does not parse: {raw!r}") from None
    # The freshness of the serving process's clock, not of the corpus.
    age = abs((datetime.now(KST) - stamp).total_seconds())
    need(age <= 600, f"now_kst {raw} is {age:.0f}s from now (want ≤ 600)")
    return f'200 · status=ok · v{d.get("version")} · now_kst {age:.0f}s off'


def check_landing(ctx):
    r = fetch(ctx["base"] + "/")
    need(r.status == 200, f"HTTP {r.status} (want 200)")
    html = r.text()
    ctx["landing_html"] = html
    need("주주의관제탑" in html, "the brand string 주주의관제탑 is not in the body")
    missing = [
        h
        for h in ("strict-transport-security", "content-security-policy", "cf-ray")
        if not r.headers.get(h)
    ]
    need(not missing, "header(s) missing: " + ", ".join(missing))
    return f'200 · {len(r.body)} bytes · HSTS + CSP · cf-ray {r.headers.get("cf-ray")}'


def check_www(ctx):
    host = ctx["host"]
    www = host if host.startswith("www.") else "www." + host
    r = fetch(f'{ctx["scheme"]}://{www}/x?y=1')
    need(r.status == 301, f"HTTP {r.status} (want 301)")
    loc = r.headers.get("location", "")
    want = ctx["base"] + "/x?y=1"
    need(loc == want, f"Location {loc!r} (want {want!r}) — path and query must survive")
    return f"301 → {loc}"


def check_http_redirect(ctx):
    r = fetch(f'http://{ctx["host"]}/')
    need(r.status == 301, f"HTTP {r.status} (want 301)")
    loc = r.headers.get("location", "")
    need(loc.startswith("https://"), f"Location {loc!r} is not https")
    return f"301 → {loc}"


def check_board(ctx):
    r = fetch(ctx["base"] + "/api/board")
    need(r.status == 200, f"HTTP {r.status} (want 200)")
    d = json.loads(r.text())
    rows = d.get("rows") or []
    need(rows, "rows is empty — the production corpus is not serving")
    for row in rows:
        if row.get("state") == "exposable" and row.get("rcept_no"):
            ctx["rcept_no"] = row["rcept_no"]
            ctx["corp_code"] = row.get("corp_code")
            ctx["corp_name"] = row.get("corp_name")
            break
    need(ctx.get("rcept_no"), "no exposable row carrying an rcept_no")
    return f'200 · {len(rows)} rows · sample {ctx["corp_name"]} {ctx["rcept_no"]}'


def check_event_page(ctx):
    need(ctx.get("rcept_no"), "no rcept_no — the board check found none")
    r = fetch(f'{ctx["base"]}/events/{ctx["rcept_no"]}')
    need(r.status == 200, f"HTTP {r.status} (want 200)")
    m = re.search(r"<title>(.*?)</title>", r.text(), re.S)
    need(m, "no <title> in the served head")
    title = m.group(1).strip()
    need(title and title != "주주의관제탑", f"<title> is the bare brand: {title!r}")
    return f"200 · <title> {title}"


def check_stock_page(ctx):
    need(ctx.get("corp_code"), "no corp_code — the board check found none")
    r = fetch(f'{ctx["base"]}/stocks/{ctx["corp_code"]}')
    need(r.status == 200, f"HTTP {r.status} (want 200)")
    return f'200 · /stocks/{ctx["corp_code"]} ({ctx.get("corp_name")})'


def check_bad_event(ctx):
    r = fetch(ctx["base"] + "/events/00000000000000")
    need(r.status == 404, f"HTTP {r.status} (want 404 — a 500 means it threw)")
    return "404 (not 500)"


def check_start_cards(ctx):
    r = fetch(ctx["base"] + "/api/ask/start-cards")
    need(r.status == 200, f"HTTP {r.status} (want 200)")
    try:
        d = json.loads(r.text())
    except ValueError:
        raise Fail("body is not JSON") from None
    return f"200 · JSON {type(d).__name__}"


def check_ops_door(ctx):
    r = fetch(ctx["base"] + "/ops")
    need(r.status == 200, f"HTTP {r.status} (want 200)")
    html = r.text()
    need("운영자 ID" in html, "the door does not render 운영자 ID")
    back = [s for s in OPS_FORBIDDEN if s in html]
    need(not back, "D15 rule line(s) are back on the public door: " + " / ".join(back))
    return "200 · 운영자 ID present · none of D15's four rule lines"


def check_robots(ctx):
    r = fetch(ctx["base"] + "/robots.txt")
    need(r.status == 200, f"HTTP {r.status} (want 200)")
    body = r.text()
    want = f'Sitemap: {ctx["base"]}/sitemap.xml'
    need(
        want in body,
        f"the ORIGIN's own block is missing (no {want!r}) in {len(r.body)} bytes — "
        "Cloudflare's managed block alone means the app is not serving robots.txt",
    )
    return f"200 · {len(r.body)} bytes · carries {want}"


def check_sitemap(ctx):
    r = fetch(ctx["base"] + "/sitemap.xml")
    need(r.status == 200, f"HTTP {r.status} (want 200)")
    locs = re.findall(r"<loc>(.*?)</loc>", r.text())
    need(locs, "no <loc> entries")
    need(len(set(locs)) == len(locs), f"{len(locs) - len(set(locs))} duplicate <loc> entries")
    prefix = ctx["base"] + "/"
    stray = [u for u in locs if u != ctx["base"] and not u.startswith(prefix)]
    # `raise Fail` and not `need(...)`: the f-string argument is evaluated
    # BEFORE the call, so `stray[0]` on the empty (passing) list would raise
    # IndexError. Same below. Measured on the first green sitemap, P4.S6.
    if stray:
        raise Fail(f"{len(stray)} URL(s) off the apex, e.g. {stray[0]}")
    for banned in ("www.", "/ops", "/auth", "/portfolio"):
        hits = [u for u in locs if banned in u]
        if hits:
            raise Fail(f"{len(hits)} URL(s) contain {banned!r}, e.g. {hits[0]}")
    norm = {u.rstrip("/") for u in locs}
    missing = [
        p for p in ("", "/stocks", "/ask") if (ctx["base"] + p).rstrip("/") not in norm
    ]
    need(not missing, "static route(s) absent: " + ", ".join(p or "/" for p in missing))
    events = [u for u in locs if "/events/" in u]
    need(events, "no /events/ URLs — the sitemap carries no corpus")
    # `force-dynamic`: the count moves with beat's 07:30/19:30 runs, so the
    # shape is asserted and the number is only reported.
    return f"200 · {len(locs)} URLs ({len(events)} events) · 3 static · all on the apex"


def check_manifest(ctx):
    r = fetch(ctx["base"] + "/manifest.webmanifest")
    need(r.status == 200, f"HTTP {r.status} (want 200)")
    try:
        d = json.loads(r.text())
    except ValueError:
        raise Fail("body is not JSON") from None
    icons = d.get("icons") or []
    need(icons, "no icons[]")
    bad = []
    for icon in icons:
        src = urllib.parse.urljoin(ctx["base"] + "/", icon.get("src", ""))
        got = fetch(src)
        if got.status != 200:
            bad.append(f"{src} → {got.status}")
    need(not bad, "icon(s) not 200: " + "; ".join(bad))
    return f'200 · name={d.get("name")} · {len(icons)} icons, all 200'


def check_og_image(ctx):
    # That exact path: `/opengraph-image` (no extension) 404s.
    r = fetch(ctx["base"] + "/opengraph-image.png")
    need(r.status == 200, f"HTTP {r.status} (want 200)")
    ctype = (r.headers.get("content-type") or "").split(";")[0].strip()
    need(ctype == "image/png", f"content-type {ctype!r} (want image/png)")
    size = _png_size(r.body)
    need(size, "not a PNG (no IHDR)")
    return f"200 · image/png · {size[0]}×{size[1]} · {len(r.body)} bytes"


def check_noindex(ctx):
    seen = []
    for path in ("/auth/login", "/portfolio"):
        r = fetch(ctx["base"] + path)
        need(r.status == 200, f"{path} → HTTP {r.status} (want 200)")
        content = None
        for tag in re.findall(r"<meta\b[^>]*>", r.text(), re.I):
            if (_attr(tag, "name") or "").lower() == "robots":
                content = _attr(tag, "content") or ""
                break
        need(content is not None, f"{path} has no robots meta tag")
        need("noindex" in content.lower(), f'{path} robots meta is "{content}" (want noindex)')
        seen.append(f"{path} → {content}")
    return " · ".join(seen)


def check_third_party(ctx):
    html = ctx.get("landing_html")
    if html is None:
        r = fetch(ctx["base"] + "/")
        need(r.status == 200, f"HTTP {r.status} (want 200)")
        html = r.text()
    found = {}
    for ref in re.findall(r'(?:src|href)\s*=\s*"([^"]+)"', html, re.I):
        if ref.startswith("//"):
            ref = ctx["scheme"] + ":" + ref
        parts = urllib.parse.urlsplit(ref)
        if parts.scheme in ("http", "https") and parts.hostname:
            host = parts.hostname.lower()
            if host != ctx["host"] and host not in ALLOWED_EXTERNAL_HOSTS:
                found.setdefault(host, ref)
    need(
        not found,
        "off-origin reference(s): " + "; ".join(f"{h} ({u})" for h, u in found.items()),
    )
    return "no off-origin src/href beyond " + ", ".join(sorted(ALLOWED_EXTERNAL_HOSTS))


def check_cotenants(ctx):
    bad = []
    for url in CO_TENANTS:
        got = fetch(url)
        if got.status != 200:
            bad.append(f"{url} → {got.status}")
    need(not bad, "; ".join(bad))
    hosts = ", ".join(urllib.parse.urlsplit(u).hostname for u in CO_TENANTS)
    return f"200 ×{len(CO_TENANTS)} — {hosts}"


#: (name, function, in --light). Order matters: `board` feeds `event-page` and
#: `stock-page`, `landing` feeds `third-party`.
CHECKS = [
    ("health", check_health, True),
    ("landing", check_landing, True),
    ("www", check_www, False),
    ("http-redirect", check_http_redirect, False),
    ("board", check_board, False),
    ("event-page", check_event_page, False),
    ("stock-page", check_stock_page, False),
    ("bad-event", check_bad_event, False),
    ("start-cards", check_start_cards, False),
    ("ops-door", check_ops_door, False),
    ("robots", check_robots, False),
    ("sitemap", check_sitemap, False),
    ("manifest", check_manifest, False),
    ("og-image", check_og_image, False),
    ("noindex", check_noindex, False),
    ("third-party", check_third_party, False),
]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="Smoke the live 주주의관제탑 origin end to end (read-only, stdlib only).",
    )
    ap.add_argument("--base", default=DEFAULT_BASE, help=f"origin to smoke (default {DEFAULT_BASE})")
    ap.add_argument(
        "--light",
        action="store_true",
        help="only the two probe checks (health, landing) — what the uptime monitor runs",
    )
    ap.add_argument(
        "--no-cotenants",
        dest="cotenants",
        action="store_false",
        help="skip the shared-box no-harm check on the neighbouring sites",
    )
    args = ap.parse_args(argv)

    base = args.base.rstrip("/")
    parts = urllib.parse.urlsplit(base)
    if parts.scheme not in ("http", "https") or not parts.hostname:
        print(f"--base must be an absolute http(s) URL, got {args.base!r}", file=sys.stderr)
        return 2
    ctx = {"base": base, "host": parts.hostname.lower(), "scheme": parts.scheme}

    checks = [(n, f) for n, f, light in CHECKS if light or not args.light]
    if args.cotenants and not args.light:
        checks.append(("cotenants", check_cotenants))

    label = "light" if args.light else "full"
    print(f"── production smoke ({label}): {base} ─────────────────────")
    failures = []
    started = time.monotonic()
    for name, fn in checks:
        t0 = time.monotonic()
        try:
            detail = fn(ctx)
            verdict = "PASS"
        except Fail as e:
            detail, verdict = str(e), "FAIL"
            failures.append(name)
        except Exception as e:  # a check that itself broke is a failure, loudly
            detail, verdict = f"{type(e).__name__}: {e}", "FAIL"
            failures.append(name)
        print(f"{verdict}  {name:<14} {(time.monotonic() - t0) * 1000:6.0f}ms  {detail}")
    elapsed = time.monotonic() - started

    passed = len(checks) - len(failures)
    print(f"── {passed} pass · {len(failures)} fail · {elapsed:.1f}s ──")
    if failures:
        print("FAILED: " + ", ".join(failures))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
