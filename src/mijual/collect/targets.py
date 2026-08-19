"""What this collector collects — and, just as importantly, what it does not.

**In scope (P2.S2):**

* ``piicDecsn`` — 주요사항보고서(유상증자결정) → rights type ① 신주인수권(증서).
* ``cmpMgDecsn`` — 주요사항보고서(회사합병결정) → rights type ③ 주식매수청구권.

**Out of scope, deliberately:**

* ② CB·EB (``cvbdIsDecsn`` / ``exbdIsDecsn``) is ``P2.S7``'s slice — adding it
  here is a one-line change to :data:`TARGETS` plus a filter, by design.
* 분할합병(``cmpDvmgDecsn``) · 주식교환(``stkExtrDecsn``) are **out of MVP scope**
  (decision D-1), even though field-matrix §3 shows they mirror ③'s shape.

``Target.subtype_nm`` is the parenthetical of ``list.json``'s ``report_nm``
(``주요사항보고서(유상증자결정)``); ``Target.endpoint`` is both the detail endpoint
and the value stored in ``Event.report_subtype``.
"""

from __future__ import annotations

from dataclasses import dataclass

from mijual.db.models import RightsType

__all__ = ["Target", "TARGETS", "BY_SUBTYPE_NM", "DEFAULT_ENDPOINTS"]


@dataclass(frozen=True)
class Target:
    endpoint: str
    subtype_nm: str
    rights_type: RightsType
    label: str


TARGETS: dict[str, Target] = {
    "piicDecsn": Target(
        endpoint="piicDecsn",
        subtype_nm="유상증자결정",
        rights_type=RightsType.SUBSCRIPTION_WARRANT,
        label="① 유증 신주인수권",
    ),
    "cmpMgDecsn": Target(
        endpoint="cmpMgDecsn",
        subtype_nm="회사합병결정",
        rights_type=RightsType.APPRAISAL_RIGHT,
        label="③ 주식매수청구권",
    ),
}

BY_SUBTYPE_NM: dict[str, Target] = {t.subtype_nm: t for t in TARGETS.values()}
DEFAULT_ENDPOINTS: tuple[str, ...] = tuple(TARGETS)
