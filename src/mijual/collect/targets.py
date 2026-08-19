"""What this collector collects — and, just as importantly, what it does not.

**In scope:**

* ``piicDecsn`` — 주요사항보고서(유상증자결정) → rights type ① 신주인수권(증서) (S2).
* ``cmpMgDecsn`` — 주요사항보고서(회사합병결정) → rights type ③ 주식매수청구권 (S2).
* ``cvbdIsDecsn`` — 주요사항보고서(전환사채권발행결정) → rights type ② CB 오버행
  (S7). ``bdRs`` is **not** a second source for it: 사모 CB is 증권신고서-면제 and
  the 지분 관련 사채 fields were 0/77 filled (N5, field-matrix §2.2).

**Out of scope, deliberately:**

* **EB** (``exbdIsDecsn``) — dropped by D-1 for the MVP, even though its shape
  mirrors ②'s. 20 reports in 2026 against CB's 263.
* 분할합병(``cmpDvmgDecsn``) · 주식교환(``stkExtrDecsn``) are **out of MVP scope**
  (decision D-1), even though field-matrix §3 shows they mirror ③'s shape.

``Target.subtype_nm`` is the parenthetical of ``list.json``'s ``report_nm``
(``주요사항보고서(유상증자결정)``); ``Target.endpoint`` is both the detail endpoint
and the value stored in ``Event.report_subtype``.

The match is **exact string equality on that parenthetical**, and for ② that is
load-bearing: the same ``pblntf_ty=B`` stream carries 자기전환사채매도결정,
자기전환사채만기전취득결정, 전환사채매수선택권행사자지정, 제3자의전환사채매수선택권행사,
신주인수권부사채권발행결정 and 교환사채권발행결정 — none of which is a ② issuance
event. A substring match on ``전환사채`` would collect all of them.

:data:`DEFAULT_ENDPOINTS` is derived from :data:`TARGETS`, and
``mijual.scheduler.config.PipelineConfig.endpoints`` defaults to it — so a target
registered here is collected by the scheduled daily pipeline with no further
wiring. ② needs **zero** LLM (N6), so it is deliberately *not* added to
``DEFAULT_EXTRACT_RIGHTS``.
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
    "cvbdIsDecsn": Target(
        endpoint="cvbdIsDecsn",
        subtype_nm="전환사채권발행결정",
        rights_type=RightsType.CONVERTIBLE_OVERHANG,
        label="② CB 전환 오버행",
    ),
    # Registered by ``P2.S8``. A 유무상증자 (유상 + 무상 in one board resolution)
    # files 주요사항보고서(**유무상**증자결정) — a *different* subtype string and a
    # different endpoint — and the exact-equality match in this module therefore
    # never collected one. It is unambiguously ① : form 11308 carries the same
    # numbered 유상 section (``6. 확정발행가``, ``9. 배정주식수``, ``11. 청약예정일``,
    # ``18. 신주인수권양도여부``, 10/10 target labels) plus a trailing 무상 section,
    # and its 실적보고서 carries the same ``Ⅶ/Ⅷ 신주인수권증서`` tables. ``P2.S8``
    # found **6 of the 2026 offerings that lapsed** filed this way, invisible to
    # every earlier run — see the phase note.
    "pifricDecsn": Target(
        endpoint="pifricDecsn",
        subtype_nm="유무상증자결정",
        rights_type=RightsType.SUBSCRIPTION_WARRANT,
        label="① 유무상증자 신주인수권",
    ),
}

BY_SUBTYPE_NM: dict[str, Target] = {t.subtype_nm: t for t in TARGETS.values()}
DEFAULT_ENDPOINTS: tuple[str, ...] = tuple(TARGETS)
