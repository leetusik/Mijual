"""The 정정 story: every version of a filing, and what the last 정정 moved.

This is the product's own point made visible. DART's detail endpoints return
**one row per event — the newest version only** — and the superseded values are
unrecoverable from the API (N2), so a reader who wants to know *what changed* has
nowhere to look. The corpus keeps every observed ``rcept_no`` as a
:class:`~mijual.db.models.FilingVersion` with its body snapshot, and this shape is
that history read back.

Three rules it enforces, all of them R3's:

**Verdicts never cross versions.** Exactly one row carries
``is_current_readable`` — the version the product is reading *right now*
(:func:`mijual.db.repository.current_version`) — and every value on the detail
page comes from that one. A countdown must never fall back to a superseded
version's date (N4), so the rail states which version is being read rather than
letting a reader assume.

**The moves are the filing's own words.** ``field_moves`` and
``interpretation`` are passed through **verbatim** from the stored
``correction_interpretation`` extraction; nothing here re-words, re-punctuates or
summarizes them. A ``new`` of ``None`` stays ``None`` — the "(정정 후 본문에서
삭제됨)" sentence is the surface's signed copy, not this layer's invention.

**The story only exists when its field passed the gate.** ``correction_interpretation``
is an LLM reading like any other field: if its citation did not resolve, it is
absent from the payload — no partial rail, no "정정 내용을 확인할 수 없습니다".
The version rail itself is deterministic (it is just rows) and is always there.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import date
from typing import Any

from mijual.present.event import FieldPayload
from mijual.present.values import iso_day

__all__ = ["CorrectionStory", "VersionRow", "correction_story"]


@dataclass(frozen=True)
class VersionRow:
    """One observed version of the filing — one row of the rail."""

    rcept_no: str
    #: 접수일. A calendar day, bare.
    rcept_dt: str | None
    #: ``original`` | ``기재정정`` | ``첨부정정`` — the pipeline's own token
    #: (:class:`mijual.db.models.CorrectionKind`), which for a 정정 *is* the
    #: bracketed prefix the filer printed. Not a label invented here.
    correction_kind: str | None
    #: ``report_nm`` as filed, prefix included.
    report_nm: str | None = None
    #: The one version every value on the page comes from.
    is_current_readable: bool = False

    def payload(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "rcept_no": self.rcept_no,
            "rcept_dt": self.rcept_dt,
            "correction_kind": self.correction_kind,
            "is_current_readable": self.is_current_readable,
        }
        if self.report_nm is not None:
            out["report_nm"] = self.report_nm
        return out


@dataclass(frozen=True)
class CorrectionStory:
    """The version rail plus the current version's reading of the last 정정."""

    versions: tuple[VersionRow, ...]
    #: What moved: the stored ``field_moves`` list, verbatim.
    field_moves: tuple[Mapping[str, Any], ...] = ()
    #: ``{changes, summary, schedule_impact}``, verbatim.
    interpretation: Mapping[str, Any] | None = None
    #: The citation of the ``correction_interpretation`` field itself.
    quote: str | None = None
    span: tuple[int, int] | None = None
    rcept_no: str | None = None

    @property
    def corrected(self) -> bool:
        """More than one version — the detail header's 정정 반영 line."""
        return len(self.versions) > 1

    @property
    def summary(self) -> str | None:
        return _text(self.interpretation, "summary")

    @property
    def schedule_impact(self) -> str | None:
        return _text(self.interpretation, "schedule_impact")

    def payload(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "corrected": self.corrected,
            "versions": [row.payload() for row in self.versions],
        }
        if self.field_moves:
            out["field_moves"] = [dict(move) for move in self.field_moves]
        if self.interpretation is not None:
            out["interpretation"] = dict(self.interpretation)
        for key in ("quote", "rcept_no"):
            value = getattr(self, key)
            if value is not None:
                out[key] = value
        if self.span is not None:
            out["span"] = list(self.span)
        return out


def _text(mapping: Mapping[str, Any] | None, key: str) -> str | None:
    value = (mapping or {}).get(key)
    return value if isinstance(value, str) and value else None


def correction_story(
    versions: Sequence[Any],
    *,
    current_rcept_no: str | None = None,
    interpretation: FieldPayload | None = None,
) -> CorrectionStory:
    """Build the story from :class:`~mijual.db.models.FilingVersion` rows.

    ``versions`` are the event's versions (any order — they are sorted here,
    oldest first, the order the rail reads in). ``interpretation`` is the
    **gate-passing** ``correction_interpretation`` field of the current version,
    or ``None``; a blocked one contributes nothing, exactly as it contributes no
    row to the card.
    """
    rows = tuple(
        VersionRow(
            rcept_no=version.rcept_no,
            rcept_dt=iso_day(version.rcept_dt),
            correction_kind=(
                version.correction_kind.value if version.correction_kind is not None else None
            ),
            report_nm=version.report_nm,
            is_current_readable=version.rcept_no == current_rcept_no,
        )
        for version in sorted(versions, key=lambda v: (v.rcept_dt or date.min, v.rcept_no))
    )
    value = interpretation.value if interpretation is not None else None
    if not isinstance(value, Mapping):
        value = {}
    moves = value.get("field_moves")
    reading = value.get("interpretation")
    return CorrectionStory(
        versions=rows,
        field_moves=tuple(m for m in moves if isinstance(m, Mapping)) if isinstance(moves, list) else (),
        interpretation=reading if isinstance(reading, Mapping) else None,
        quote=interpretation.quote if interpretation is not None else None,
        span=interpretation.span if interpretation is not None else None,
        rcept_no=interpretation.rcept_no if interpretation is not None else None,
    )
