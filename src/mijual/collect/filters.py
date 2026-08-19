"""Correctness filters — **not** conveniences (phase constraint, D-1).

Publishing either of these as a live right is a correctness bug:

* ① a 유상증자 that issues **no 신주인수권증서** (제3자배정증자 / 일반공모증자);
* ③ a 합병 that grants **no 주식매수청구권** (소규모·간이합병).

Both are *recorded and excluded*, never dropped: the outcome is written to
``Event.suppressed_reason`` / ``suppressed_note`` (note N15), so the filter is
auditable — and ③'s suppressed set is itself a demo asset (6 overlapping
소규모합병 windows in the judging week).

**The ① decision here is provisional by design.** ``ic_mthn`` is the API's
증자방식 and is 100% filled (field-matrix §1.2), but the phase constraint is
explicit that the *final* exposure test is 본문 ``18. 신주인수권양도여부``, which
only ``P2.S3``/``P2.S5`` can read. This module therefore uses ``ic_mthn`` to
suppress what certainly issues no 증서, and lets everything else through to the
reading layer — it never *confirms* a right.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

__all__ = [
    "Suppression",
    "WARRANT_BEARING_IC_MTHN",
    "SMALL_MERGER_FORMS",
    "evaluate",
    "is_filled",
]

#: 증자방식 values that can issue a 신주인수권증서 (measured 2026 population:
#: 주주배정후 실권주 일반공모 32, 주주배정증자 3, 주주우선공모증자 1 — against
#: 제3자배정증자 263 and 일반공모증자 14, which cannot).
#: ``주주우선공모증자`` is kept UNsuppressed pending **O-5** (does it issue a 증서?
#: one case, ``20260807000339``) — the safer default is to let the reading layer
#: look, since suppression here would hide a possibly-real right.
WARRANT_BEARING_IC_MTHN = frozenset(
    {"주주배정후실권주일반공모", "주주배정증자", "주주우선공모증자"}
)

#: 합병 형태 (``mg_stn``) that grants no 주식매수청구권.
SMALL_MERGER_FORMS = ("소규모합병", "간이합병")

#: OpenDART writes an unfilled field as ``-``.
_EMPTY = {"", "-", "해당사항없음", "해당없음"}


def is_filled(value: str | None) -> bool:
    return re.sub(r"\s+", "", value or "") not in _EMPTY


def _norm(value: str | None) -> str:
    return re.sub(r"\s+", "", value or "")


@dataclass(frozen=True)
class Suppression:
    """Why an event was collected but must not be exposed as a live right."""

    reason: str
    note: str


def evaluate(endpoint: str, detail_row: dict | None) -> Suppression | None:
    """``None`` = keep (still subject to the later 본문/gate checks)."""
    if endpoint == "piicDecsn":
        return _evaluate_rights_offering(detail_row)
    if endpoint == "cmpMgDecsn":
        return _evaluate_merger(detail_row)
    return None


def _evaluate_rights_offering(row: dict | None) -> Suppression | None:
    if row is None:
        return None  # undecided — no detail row was fetched; counted, not suppressed
    ic_mthn = (row.get("ic_mthn") or "").strip()
    if not is_filled(ic_mthn):
        return Suppression(
            "ic_mthn_unknown",
            "piicDecsn.ic_mthn 미기재 — 증자방식을 확인할 수 없어 노출 보류",
        )
    if _norm(ic_mthn) in WARRANT_BEARING_IC_MTHN:
        return None
    return Suppression(
        "no_warrant_class",
        f"ic_mthn={ic_mthn} — 신주인수권증서 미발행 증자방식 "
        "(최종 확인은 본문 18. 신주인수권양도여부, P2.S3/S5)",
    )


def _evaluate_merger(row: dict | None) -> Suppression | None:
    if row is None:
        return None
    mg_stn = (row.get("mg_stn") or "").strip()
    form = _norm(mg_stn)
    if any(small in form for small in SMALL_MERGER_FORMS):
        return Suppression(
            "no_appraisal_right", f"mg_stn={mg_stn} — 주식매수청구권 미부여 합병"
        )
    if not (
        is_filled(row.get("aprskh_plnprc"))
        or is_filled(row.get("mgsc_aprskh_expd_bgd"))
        or is_filled(row.get("mgsc_aprskh_expd_edd"))
    ):
        return Suppression(
            "no_appraisal_right",
            "aprskh_plnprc / mgsc_aprskh_expd_bgd·edd 모두 미기재 — 매수청구권 부여 근거 없음",
        )
    return None
