"""②'s fact strip — the six API-tier values a CB card states above its 본문 rows.

② is the one rights type whose countdown is not a 본문 reading (N6): 전환가액,
전환청구기간 and the 오버행 수량·비율 come from ``cvbdIsDecsn``, which is why an ②
event renders with **zero** extraction fields and still has a complete card. R3
puts those values in a fact strip above the field sections and names exactly six —
전환가액 · 오버행 % · 전환 시 주식수 · 권면총액 · 발행방법 · 만기 — so that is what
this shape carries. No more: a key nobody renders is a key a later surface will
render by accident.

Every one of them is a **fact**. They are printed in a filing's own structured
row, not derived by this product, so none carries 「추정」 — and none carries a
``quote``/``span`` either, because an API row has no character offsets into a
document. Its citation is the filing number and the DART link beside it.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from mijual.present.values import Figure, decimal_str, iso_day

if TYPE_CHECKING:  # pragma: no cover - imported for types only
    from mijual.cb import ConvertibleFacts

__all__ = ["ConvertibleView", "convertible_view"]


@dataclass(frozen=True)
class ConvertibleView:
    """The ② fact strip, as R3 lists it."""

    rcept_no: str | None = None
    #: 전환가액 (원/주).
    conversion_price: Figure | None = None
    #: 주식총수 대비 비율 (%) — **the 오버행 number**.
    overhang_pct: Figure | None = None
    #: 전환 시 발행될 주식수.
    shares: Figure | None = None
    #: 권면총액 (원).
    face_amount: Figure | None = None
    #: 발행방법 — 사모 / 공모, the filing's own word.
    issue_method: str | None = None
    #: 사채 만기일. A calendar day.
    maturity_date: str | None = None

    def payload(self) -> dict[str, Any]:
        out: dict[str, Any] = {}
        if self.rcept_no is not None:
            out["rcept_no"] = self.rcept_no
        for key in ("conversion_price", "overhang_pct", "shares", "face_amount"):
            figure: Figure | None = getattr(self, key)
            if figure is not None:
                out[key] = figure.payload()
        for key in ("issue_method", "maturity_date"):
            value = getattr(self, key)
            if value is not None:
                out[key] = value
        return out


def convertible_view(facts: "ConvertibleFacts | None") -> ConvertibleView | None:
    """The strip for one event's stored ``cvbdIsDecsn`` row, or ``None``."""
    if facts is None:
        return None
    rcept_no = facts.rcept_no
    return ConvertibleView(
        rcept_no=rcept_no,
        conversion_price=Figure.fact(decimal_str(facts.conversion_price), rcept_no=rcept_no),
        overhang_pct=Figure.fact(decimal_str(facts.overhang_pct), rcept_no=rcept_no),
        shares=Figure.fact(
            int(facts.shares) if facts.shares is not None else None, rcept_no=rcept_no
        ),
        face_amount=Figure.fact(decimal_str(facts.face_amount), rcept_no=rcept_no),
        issue_method=facts.issue_method,
        maturity_date=iso_day(facts.maturity_date),
    )
