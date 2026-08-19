"""Throwaway-grade OpenDART client for the P1.S1 spike.

Stdlib only. Reads DART_API_KEY from repo-root .env (or the environment) in
process. The key is NEVER printed, logged, or written into any cached artifact:
cache filenames and the `_url` recorded inside each cache file are built from
the key-stripped query string.

Not production code. P2 owns the real collector.
"""

from __future__ import annotations

import hashlib
import io
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SAMPLES = Path(__file__).resolve().parent / "samples"
BASE = "https://opendart.fss.or.kr/api"


def _api_key() -> str:
    key = os.environ.get("DART_API_KEY")
    if key:
        return key.strip()
    env = ROOT / ".env"
    if env.exists():
        for line in env.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            name, _, value = line.partition("=")
            if name.strip() == "DART_API_KEY":
                return value.strip().strip('"').strip("'")
    raise SystemExit("DART_API_KEY not found (repo-root .env or environment)")


KEY = _api_key()


def _safe_query(params: dict) -> str:
    """Query string with the key removed — safe to print and to store."""
    clean = {k: v for k, v in params.items() if k != "crtfc_key" and v is not None}
    return urllib.parse.urlencode(sorted(clean.items()))


def _fetch(url: str, *, timeout: int = 30, tries: int = 4) -> bytes:
    """GET with a small backoff. Exception text never carries the URL (it holds the key)."""
    for attempt in range(tries):
        try:
            with urllib.request.urlopen(url, timeout=timeout) as resp:  # noqa: S310
                return resp.read()
        except Exception as exc:  # noqa: BLE001 - transient 503 / socket timeouts
            if attempt == tries - 1:
                raise RuntimeError(f"DART fetch failed after {tries} tries: {type(exc).__name__}") from None
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError("unreachable")


def _cache_path(endpoint: str, params: dict, ext: str) -> Path:
    safe = _safe_query(params)
    digest = hashlib.sha1(safe.encode("utf-8")).hexdigest()[:12]
    hint = re.sub(r"[^A-Za-z0-9]+", "-", safe)[:60].strip("-")
    return SAMPLES / endpoint / f"{hint}_{digest}.{ext}"


def get_json(endpoint: str, *, refresh: bool = False, **params) -> dict:
    """GET https://opendart.fss.or.kr/api/<endpoint>.json, cached on disk."""
    path = _cache_path(endpoint, params, "json")
    if path.exists() and not refresh:
        payload = json.loads(path.read_text(encoding="utf-8"))
        return payload["body"]

    query = {k: v for k, v in params.items() if v is not None}
    query["crtfc_key"] = KEY
    url = f"{BASE}/{endpoint}.json?" + urllib.parse.urlencode(query)
    body = json.loads(_fetch(url).decode("utf-8"))

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {"_endpoint": endpoint, "_url": f"{BASE}/{endpoint}.json?{_safe_query(params)}", "body": body},
            ensure_ascii=False,
            indent=1,
        ),
        encoding="utf-8",
    )
    return body


def get_document(rcept_no: str, *, refresh: bool = False) -> bytes:
    """GET the document API ZIP for one rcept_no. Returns raw ZIP bytes."""
    path = _cache_path("document", {"rcept_no": rcept_no}, "zip")
    if path.exists() and not refresh:
        return path.read_bytes()
    url = f"{BASE}/document.xml?" + urllib.parse.urlencode({"crtfc_key": KEY, "rcept_no": rcept_no})
    blob = _fetch(url, timeout=60)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(blob)
    return blob


def document_members(rcept_no: str) -> list[tuple[str, int]]:
    blob = get_document(rcept_no)
    if not blob.startswith(b"PK"):
        return []
    with zipfile.ZipFile(io.BytesIO(blob)) as zf:
        return [(i.filename, i.file_size) for i in zf.infolist()]


def document_text(rcept_no: str, member: str | None = None) -> str:
    """Decoded text of one member of the document ZIP (first member by default)."""
    blob = get_document(rcept_no)
    with zipfile.ZipFile(io.BytesIO(blob)) as zf:
        name = member or zf.namelist()[0]
        raw = zf.read(name)
    for enc in ("utf-8", "euc-kr", "cp949"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def rows(body: dict) -> list[dict]:
    """`list` of a normal OpenDART response, [] when status != 000."""
    if body.get("status") != "000":
        return []
    return body.get("list") or []


def groups(body: dict) -> list[tuple[str, list[dict]]]:
    """(title, rows) pairs for the 증권신고서 endpoints, which return `group`."""
    if body.get("status") != "000":
        return []
    if body.get("group"):
        return [(g.get("title", "?"), g.get("list") or []) for g in body["group"]]
    return [("list", body.get("list") or [])]


def status(body: dict) -> str:
    return f"{body.get('status')} {body.get('message')}"


def filings(bgn_de: str, end_de: str, *, pblntf_ty: str | None = None, corp_cls: str | None = None,
            corp_code: str | None = None, pages: int = 1, page_count: int = 100,
            pblntf_detail_ty: str | None = None) -> list[dict]:
    """list.json rows across `pages` pages. Mind the 3-month cap without corp_code."""
    out: list[dict] = []
    for page_no in range(1, pages + 1):
        body = get_json(
            "list",
            bgn_de=bgn_de,
            end_de=end_de,
            pblntf_ty=pblntf_ty,
            pblntf_detail_ty=pblntf_detail_ty,
            corp_cls=corp_cls,
            corp_code=corp_code,
            page_no=page_no,
            page_count=page_count,
        )
        got = rows(body)
        out.extend(got)
        if not got or page_no >= int(body.get("total_page") or 1):
            break
    return out


if __name__ == "__main__":  # tiny self-check: no key material in output
    probe = get_json("list", bgn_de="20260601", end_de="20260818", corp_cls="Y", pblntf_ty="B", page_no=1, page_count=10)
    print("list.json ->", status(probe), "| rows:", len(rows(probe)), "| total:", probe.get("total_count"))
    print("cache dir:", SAMPLES)
    sys.exit(0)
