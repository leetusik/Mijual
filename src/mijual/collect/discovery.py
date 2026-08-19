"""Discovery: which filings exist in a window, from ``list.json`` only.

Two API constraints shape this module (field-matrix §6):

* without ``corp_code`` the window is capped at **3 months**
  (``status 100 … 검색기간은 3개월만 가능합니다``) → :func:`chunk_windows`;
* ``page_count`` maxes out at 100 and paging runs to ``total_page``
  (handled inside :meth:`mijual.dart.DartClient.filings`).

Discovery must see **originals and 정정 alike**: a poll driven by the detail
endpoints misses 100% of corrections (40/40 measured, note N3), and the
corrections are the majority — 2026 KOSPI+KOSDAQ carries 252 유상증자결정
originals against 654 ``[기재정정]`` rows.
"""

from __future__ import annotations

import calendar
import re
from dataclasses import dataclass, field
from datetime import date, timedelta

from mijual.collect.targets import BY_SUBTYPE_NM
from mijual.dart import DartClient
from mijual.dart import rows as client_rows
from mijual.db.models import parse_dart_date

__all__ = [
    "DEFAULT_MARKETS",
    "PBLNTF_TY",
    "Discovery",
    "chunk_windows",
    "discover",
    "parse_report_nm",
]

#: 주요사항보고 — the pblntf_ty that carries all three MVP rights types.
PBLNTF_TY = "B"
#: KOSPI + KOSDAQ. ``N`` (KONEX) / ``E`` (기타) are the O-4 probe, not the default.
DEFAULT_MARKETS: tuple[str, ...] = ("Y", "K")

_PREFIX = re.compile(r"^\s*\[([^\]]+)\]")
_SUBTYPE = re.compile(r"\(([^()]+)\)\s*$")


def parse_report_nm(report_nm: str | None) -> tuple[str | None, str | None]:
    """``'[기재정정]주요사항보고서(유상증자결정)'`` → ``('기재정정', '유상증자결정')``.

    The bracketed prefix decides the :class:`~mijual.db.models.CorrectionKind`;
    the trailing parenthetical is the report subtype this collector filters on.
    """
    name = report_nm or ""
    prefix = _PREFIX.match(name)
    subtype = _SUBTYPE.search(name)
    return (prefix.group(1) if prefix else None, subtype.group(1) if subtype else None)


def _add_months(day: date, months: int) -> date:
    year, month = divmod(day.month - 1 + months, 12)
    year += day.year
    month += 1
    return date(year, month, min(day.day, calendar.monthrange(year, month)[1]))


def chunk_windows(bgn_de: str, end_de: str, *, months: int = 3) -> list[tuple[str, str]]:
    """Split ``[bgn, end]`` into ``<= months``-long ``list.json`` windows.

    ``20260101~20260331`` (exactly 3 months) is accepted by the API, so the
    chunks are half-open on the right by one day: ``bgn + 3개월 - 1일``.
    """
    start, stop = parse_dart_date(bgn_de), parse_dart_date(end_de)
    if start is None or stop is None:
        raise ValueError(f"unparseable window: {bgn_de!r}~{end_de!r}")
    if stop < start:
        raise ValueError(f"window ends before it starts: {bgn_de}~{end_de}")

    out: list[tuple[str, str]] = []
    cursor = start
    while cursor <= stop:
        edge = min(stop, _add_months(cursor, months) - timedelta(days=1))
        out.append((cursor.strftime("%Y%m%d"), edge.strftime("%Y%m%d")))
        cursor = edge + timedelta(days=1)
    return out


@dataclass
class Discovery:
    """Target ``list.json`` rows for one window, deduplicated by ``rcept_no``."""

    rows: list[dict] = field(default_factory=list)
    chunks: list[tuple[str, str]] = field(default_factory=list)
    scanned: int = 0
    missing_chunks: list[tuple[str, str, str]] = field(default_factory=list)


def discover(
    client: DartClient,
    bgn_de: str,
    end_de: str,
    *,
    markets: tuple[str, ...] = DEFAULT_MARKETS,
    endpoints: tuple[str, ...] | None = None,
    months: int = 3,
    pages: int = 100,
    on_error: str = "raise",
    log=None,
) -> Discovery:
    """Every target filing (original **and** 정정) filed in ``[bgn_de, end_de]``.

    ``on_error='skip'`` keeps going when a chunk cannot be read (an offline
    cache miss, say) and records it in :attr:`Discovery.missing_chunks`.
    """
    wanted = {
        target.subtype_nm
        for name, target in BY_SUBTYPE_NM.items()
        if endpoints is None or target.endpoint in endpoints
    }
    result = Discovery(chunks=chunk_windows(bgn_de, end_de, months=months))
    seen: dict[str, dict] = {}

    for bgn, end in result.chunks:
        for market in markets:
            got = 0
            total_page = 1
            for page_no in range(1, pages + 1):
                try:
                    body = client.get_json(
                        "list",
                        bgn_de=bgn,
                        end_de=end,
                        pblntf_ty=PBLNTF_TY,
                        corp_cls=market,
                        page_no=page_no,
                        page_count=100,
                    )
                except Exception as exc:  # noqa: BLE001 — cache miss / transport / budget
                    if on_error != "skip":
                        raise
                    # Keep the pages already read; a partial window is reported,
                    # never silently taken for a complete one.
                    result.missing_chunks.append(
                        (bgn, end, f"{market}: page {page_no}/{total_page} {type(exc).__name__}")
                    )
                    break
                page_rows = client_rows(body)
                total_page = int(body.get("total_page") or 1)
                result.scanned += len(page_rows)
                got += len(page_rows)
                for row in page_rows:
                    _, subtype_nm = parse_report_nm(row.get("report_nm"))
                    if subtype_nm in wanted:
                        seen.setdefault(row["rcept_no"], row)
                if not page_rows or page_no >= total_page:
                    break
            if log:
                log(f"  list {bgn}~{end} {market}: {got} rows over <= {total_page} page(s)")

    result.rows = sorted(seen.values(), key=lambda r: (r["rcept_dt"], r["rcept_no"]))
    return result
