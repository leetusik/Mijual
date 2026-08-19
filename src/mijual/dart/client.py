"""OpenDART client — the production port of ``scripts/spike/dart.py``.

The spike version was throwaway-grade, but it was proven against ~1,002 real
requests, and four of its behaviours are the ones a naive client gets wrong
(phase note N7 / field-matrix §6):

1. ``None`` query params are **dropped, never serialized** — ``corp_code=None``
   comes back as ``status 100 corp_code가 필드의 부적절한 값입니다``.
2. 증권신고서 endpoints (``estkRs``/``bdRs``/``mgRs``/…) return ``group[]`` of
   ``{title, list}``, not a flat ``list`` — :func:`groups` normalises both.
3. Transient ``HTTP 503`` happens under sustained calling → retry with backoff.
4. ``document.xml`` returns a ZIP (magic ``PK``); an error comes back as a
   non-ZIP XML body → detect it instead of caching a poisoned "document".

**Key safety is structural, not incidental.** The API key is appended only to
the live request URL; the cache filename, the ``_url`` recorded inside every
cached JSON envelope and every exception message are built from the
key-stripped query string.

**Cache compatibility is deliberate and load-bearing.** :meth:`DartClient.cache_path`
reproduces the spike's scheme byte-for-byte (sorted key-stripped querystring →
``sha1[:12]`` digest + a 60-char sanitised hint), so pointing ``cache_dir`` at
``scripts/spike/samples/`` turns the P1 cache into an offline fixture set — no
key, no network. Do not "improve" the naming without migrating that cache.
"""

from __future__ import annotations

import hashlib
import io
import json
import re
import time
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path
from typing import Any

from mijual.config import Settings, load_settings

__all__ = [
    "BASE_URL",
    "CacheMiss",
    "DartClient",
    "DartError",
    "DartFetchError",
    "NotAZipError",
    "groups",
    "rows",
    "safe_query",
    "status",
]

BASE_URL = "https://opendart.fss.or.kr/api"


class DartError(RuntimeError):
    """Base class for OpenDART access failures."""


class DartFetchError(DartError):
    """Transport failure after retries. Never carries the URL (it holds the key)."""


class CacheMiss(DartError):
    """Offline client asked for a response that is not on disk."""


class NotAZipError(DartError):
    """``document.xml`` returned an error body instead of a ZIP."""


def safe_query(params: dict[str, Any]) -> str:
    """Query string with the key removed and ``None`` values dropped.

    Safe to print, to store, and to hash into a cache filename.
    """
    clean = {k: v for k, v in params.items() if k != "crtfc_key" and v is not None}
    return urllib.parse.urlencode(sorted(clean.items()))


def rows(body: dict) -> list[dict]:
    """``list`` of a normal OpenDART response, ``[]`` when ``status != 000``."""
    if body.get("status") != "000":
        return []
    return body.get("list") or []


def groups(body: dict) -> list[tuple[str, list[dict]]]:
    """``(title, rows)`` pairs — normalises the 증권신고서 ``group[]`` shape."""
    if body.get("status") != "000":
        return []
    if body.get("group"):
        return [(g.get("title", "?"), g.get("list") or []) for g in body["group"]]
    return [("list", body.get("list") or [])]


def status(body: dict) -> str:
    return f"{body.get('status')} {body.get('message')}"


class DartClient:
    """Cached OpenDART client.

    Args:
        settings: process settings; defaults to :func:`mijual.config.load_settings`.
        cache_dir: on-disk response cache (defaults to ``settings.cache_dir``).
            Point it at ``scripts/spike/samples`` for the P1 fixture set.
        api_key: overrides ``settings.dart_api_key``. Resolved lazily — an
            offline client never needs one.
        offline: never hit the network; a cache miss raises :class:`CacheMiss`.
    """

    def __init__(
        self,
        *,
        settings: Settings | None = None,
        cache_dir: Path | str | None = None,
        api_key: str | None = None,
        offline: bool = False,
        base_url: str = BASE_URL,
        timeout: int = 30,
        tries: int = 4,
    ) -> None:
        self.settings = settings if settings is not None else load_settings()
        self.cache_dir = Path(cache_dir) if cache_dir is not None else self.settings.cache_dir
        self._api_key_override = api_key
        self.offline = offline
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.tries = tries

    # -- key handling -----------------------------------------------------
    @property
    def api_key(self) -> str:
        """The key, resolved on first *use*. Never logged or stored."""
        if self._api_key_override:
            return self._api_key_override
        return self.settings.require_dart_api_key()

    # -- cache ------------------------------------------------------------
    def cache_path(self, endpoint: str, params: dict[str, Any], ext: str) -> Path:
        """Cache location for one request — byte-compatible with the P1 spike."""
        safe = safe_query(params)
        digest = hashlib.sha1(safe.encode("utf-8")).hexdigest()[:12]
        hint = re.sub(r"[^A-Za-z0-9]+", "-", safe)[:60].strip("-")
        return self.cache_dir / endpoint / f"{hint}_{digest}.{ext}"

    # -- transport --------------------------------------------------------
    def _fetch(self, url: str, *, timeout: int | None = None) -> bytes:
        """GET with a small backoff (transient 503s are measured, not theoretical).

        The exception text never carries the URL — the URL holds the key.
        """
        if self.offline:
            raise CacheMiss("offline client: refusing to fetch")
        last: Exception | None = None
        for attempt in range(self.tries):
            try:
                with urllib.request.urlopen(url, timeout=timeout or self.timeout) as resp:  # noqa: S310
                    return resp.read()
            except Exception as exc:  # noqa: BLE001 - transient 503 / socket timeouts
                last = exc
                if attempt == self.tries - 1:
                    break
                time.sleep(1.5 * (attempt + 1))
        raise DartFetchError(
            f"DART fetch failed after {self.tries} tries: {type(last).__name__}"
        ) from None

    def _live_url(self, endpoint: str, params: dict[str, Any], suffix: str) -> str:
        query = {k: v for k, v in params.items() if v is not None}
        query["crtfc_key"] = self.api_key
        return f"{self.base_url}/{endpoint}.{suffix}?" + urllib.parse.urlencode(query)

    # -- JSON endpoints ---------------------------------------------------
    def get_json(self, endpoint: str, *, refresh: bool = False, **params: Any) -> dict:
        """``GET /api/<endpoint>.json``, cached on disk."""
        path = self.cache_path(endpoint, params, "json")
        if path.exists() and not refresh:
            payload = json.loads(path.read_text(encoding="utf-8"))
            return payload["body"]
        if self.offline:
            raise CacheMiss(f"{endpoint}.json not cached: {safe_query(params)}")

        body = json.loads(self._fetch(self._live_url(endpoint, params, "json")).decode("utf-8"))
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(
                {
                    "_endpoint": endpoint,
                    "_url": f"{self.base_url}/{endpoint}.json?{safe_query(params)}",
                    "body": body,
                },
                ensure_ascii=False,
                indent=1,
            ),
            encoding="utf-8",
        )
        return body

    def filings(
        self,
        bgn_de: str,
        end_de: str,
        *,
        pblntf_ty: str | None = None,
        pblntf_detail_ty: str | None = None,
        corp_cls: str | None = None,
        corp_code: str | None = None,
        pages: int = 1,
        page_count: int = 100,
    ) -> list[dict]:
        """``list.json`` rows across ``pages`` pages.

        Without ``corp_code`` the window is capped at 3 months (field-matrix §6.1).
        """
        out: list[dict] = []
        for page_no in range(1, pages + 1):
            body = self.get_json(
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

    # -- 본문 (document API) ------------------------------------------------
    def get_document(self, rcept_no: str, *, refresh: bool = False) -> bytes:
        """Raw 본문 ZIP bytes for one ``rcept_no``.

        An OpenDART error is returned as a non-ZIP XML body; that body is
        rejected (:class:`NotAZipError`) and **not** written to the cache, so a
        transient failure cannot poison the fixture set.
        """
        path = self.cache_path("document", {"rcept_no": rcept_no}, "zip")
        if path.exists() and not refresh:
            return path.read_bytes()
        if self.offline:
            raise CacheMiss(f"document not cached: rcept_no={rcept_no}")

        blob = self._fetch(self._live_url("document", {"rcept_no": rcept_no}, "xml"), timeout=60)
        if not blob.startswith(b"PK"):
            raise NotAZipError(f"document.xml returned a non-ZIP body for rcept_no={rcept_no}")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(blob)
        return blob

    def document_members(self, rcept_no: str) -> list[tuple[str, int]]:
        """``(filename, size)`` of each ZIP member; ``[]`` for a non-ZIP body."""
        blob = self.get_document(rcept_no)
        if not blob.startswith(b"PK"):
            return []
        with zipfile.ZipFile(io.BytesIO(blob)) as zf:
            return [(i.filename, i.file_size) for i in zf.infolist()]

    def document_text(self, rcept_no: str, member: str | None = None) -> str:
        """Decoded text of one ZIP member (the first member by default)."""
        return decode_document(self.get_document(rcept_no), member=member)


def decode_document(blob: bytes, member: str | None = None) -> str:
    """Decode one member of a 본문 ZIP. Declared UTF-8 in practice; EUC-KR fallback."""
    if not blob.startswith(b"PK"):
        raise NotAZipError("not a ZIP body (document API error response?)")
    with zipfile.ZipFile(io.BytesIO(blob)) as zf:
        name = member or zf.namelist()[0]
        raw = zf.read(name)
    for enc in ("utf-8", "euc-kr", "cp949"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")
