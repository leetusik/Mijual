"""정정 pairing — deciding which event a ``[기재정정]`` filing belongs to.

This is the part of collection that is easy to get wrong and expensive to get
wrong (note N3, field-matrix §4.1): the event key is
``(corp_code, report_subtype, original_rcept_dt)``, so a correction must be
resolved to **its original's 접수일** before anything can be stored.

The §4.1 algorithm has two arms. The first — read ``<CORRECTION> 2. 정정대상
공시서류의 최초제출일`` from the 본문 — needs the XML parse layer, which is
``P2.S3``'s slice, and the field itself is filer-entered and sometimes years
wrong (``20260429000902`` declares 2022-08-01). This module implements the
**second, validated arm without any 본문 parsing**: same corp + same subtype,
**nearest earlier original**. S3 will backfill ``declared_original_dt`` and can
then flag or re-parent the pairings this module marks ``*_ambiguous``.

One deliberate refinement over ``scripts/spike/corrections.py``: the spike took
the nearest earlier *sibling*, which for a correction **chain** is the previous
*correction* (디모아 filed 6 against one 유증). Since the event key needs the
**original's** date, this module takes the nearest earlier row whose
``CorrectionKind`` is ``ORIGINAL`` — the whole chain then lands on one event.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import timedelta
from typing import Callable, Iterable

from mijual.collect.discovery import parse_report_nm
from mijual.db.models import CorrectionKind, parse_dart_date

__all__ = ["FilingIndex", "Pairing", "pair_correction"]

#: A correction older than this many days than the candidate original stops
#: counting the candidate as "plausibly the same event" for ambiguity flagging.
AMBIGUITY_LOOKBACK_DAYS = 400


@dataclass(frozen=True)
class Pairing:
    """Result of resolving one correction to its original."""

    original: dict | None
    method: str
    candidates: int = 0

    @property
    def paired(self) -> bool:
        return self.original is not None

    @property
    def ambiguous(self) -> bool:
        return self.method.endswith("_ambiguous")


class FilingIndex:
    """``list.json`` rows grouped by ``(corp_code, subtype_nm)``.

    Fed from the discovery window first and, on demand, from a corp-scoped
    ``list.json`` query (which carries **no 3-month cap**, so it can reach
    originals filed long before the collection window).
    """

    def __init__(self) -> None:
        self._groups: dict[tuple[str, str], dict[str, dict]] = defaultdict(dict)
        self.corps_with_history: set[str] = set()

    def add(self, rows: Iterable[dict]) -> int:
        added = 0
        for row in rows:
            _, subtype_nm = parse_report_nm(row.get("report_nm"))
            corp_code = row.get("corp_code")
            if not subtype_nm or not corp_code:
                continue
            group = self._groups[(corp_code, subtype_nm)]
            if row["rcept_no"] not in group:
                group[row["rcept_no"]] = row
                added += 1
        return added

    def group(self, corp_code: str, subtype_nm: str) -> list[dict]:
        rows = self._groups.get((corp_code, subtype_nm), {}).values()
        return sorted(rows, key=lambda r: (r["rcept_dt"], r["rcept_no"]))

    def earlier_originals(self, row: dict, subtype_nm: str) -> list[dict]:
        """Originals of the same corp+subtype at or before ``row``, oldest first."""
        here = (row["rcept_dt"], row["rcept_no"])
        return [
            candidate
            for candidate in self.group(row["corp_code"], subtype_nm)
            if candidate["rcept_no"] != row["rcept_no"]
            and (candidate["rcept_dt"], candidate["rcept_no"]) <= here
            and CorrectionKind.from_report_nm(candidate.get("report_nm"))
            is CorrectionKind.ORIGINAL
        ]


def _ambiguity(candidates: list[dict], row: dict) -> int:
    """How many originals could plausibly be the target of this correction."""
    correction_dt = parse_dart_date(row["rcept_dt"])
    floor = correction_dt - timedelta(days=AMBIGUITY_LOOKBACK_DAYS)
    return sum(1 for c in candidates if (parse_dart_date(c["rcept_dt"]) or floor) >= floor)


def pair_correction(
    index: FilingIndex,
    row: dict,
    subtype_nm: str,
    *,
    load_history: Callable[[str], Iterable[dict]] | None = None,
) -> Pairing:
    """Resolve one correction row to its original.

    ``load_history`` is called at most once per corp, and **only** when the
    discovery window holds no earlier original — that is the case field-matrix
    §4.1 measured as 10/40 "unpaired", every one of them an original filed
    before the sampled window rather than a method failure.
    """
    candidates = index.earlier_originals(row, subtype_nm)
    from_history = False

    if not candidates and load_history is not None:
        corp_code = row["corp_code"]
        if corp_code not in index.corps_with_history:
            index.corps_with_history.add(corp_code)
            index.add(load_history(corp_code))
        candidates = index.earlier_originals(row, subtype_nm)
        from_history = bool(candidates)

    if not candidates:
        return Pairing(None, "unpaired", 0)

    plausible = _ambiguity(candidates, row)
    method = "earlier_history" if from_history else "earlier"
    if plausible > 1:
        method += "_ambiguous"
    return Pairing(candidates[-1], method, plausible)
