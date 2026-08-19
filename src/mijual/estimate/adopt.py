"""Targeted adoption of a 유상증자결정 the corpus does not hold.

``P2.S2`` collected 2026-01-01 onward, which is the right frame for *live*
rights. It is the wrong frame for a *lapse* number: the 청약 lands two to six
months after the 유상증자결정, so an offering decided in 2025-Q4 is exactly the
one whose 신주인수권 lapsed in early 2026. ``P2.S8``'s 실적보고서 census measured
the size of that blind spot — **7 of the 17** completed ① offerings of 2026 have
no 유상증자결정 in the corpus.

The cheap fix would have been "re-run the collector over 2025-H2", but the
collector is market-wide: it would have paid ~300 detail requests to reach seven
corps. So this module adopts **only the named corp**, using corp-scoped
``list.json`` (which has no 3-month window cap) and the corp-scoped detail
endpoint — 3 to 4 requests per offering, and no other event enters the corpus.

What lands is an ordinary :class:`~mijual.db.models.Event`: same N2 key, same
version rows, same snapshots. Everything downstream — ``bodydoc warrants``,
``extract``, ``gates`` — then treats it exactly like a natively collected one,
which is the point: an adopted event must not become a second class of evidence.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta

from mijual.collect.discovery import parse_report_nm
from mijual.dart import DartClient, DartError, RequestBudgetExceeded
from mijual.db.models import CorrectionKind, Event, RightsType
from mijual.db.repository import ensure_corp, ensure_event, ensure_snapshot, ensure_version

__all__ = ["AdoptionOutcome", "adopt_offering"]

#: 주요사항보고. The 유상증자결정 lives here (field-matrix §6.1).
_PBLNTF_TY = "B"
#: The two subtypes that issue a 신주인수권증서, and their detail endpoints.
#: ``유무상증자결정`` was invisible to every run before ``P2.S8`` — see
#: :data:`mijual.collect.targets.TARGETS`.
_SUBTYPES = {"유상증자결정": "piicDecsn", "유무상증자결정": "pifricDecsn"}
#: How far back of the 청약 종료일 to look for the 결정 공시. The longest 결의 →
#: 청약 gap measured in this corpus is ~5 months (한화솔루션 03-26 → 07-23), but a
#: corp-scoped ``list.json`` has no 3-month cap and costs the same at any width,
#: so the window is deliberately generous.
_LOOKBACK_DAYS = 800


@dataclass
class AdoptionOutcome:
    """What one adoption attempt did, and what it cost."""

    corp_code: str
    status: str = "skipped"
    event_id: int | None = None
    original_rcept_dt: date | None = None
    versions: int = 0
    documents: int = 0
    requests: int = 0
    note: str | None = None
    rcept_nos: list[str] = field(default_factory=list)


def adopt_offering(
    session,
    client: DartClient,
    *,
    corp_code: str,
    corp_name: str | None,
    subscription_end: date,
    documents: int = 2,
) -> AdoptionOutcome:
    """Adopt the 유상증자결정 whose 청약 closed on ``subscription_end``.

    The original is chosen as **the newest 유상증자결정 original filed on or
    before the 청약 종료일** — the same "nearest earlier original" rule ``P2.S2``
    pairs 정정 with (N3), applied from the other end of the offering.
    """
    outcome = AdoptionOutcome(corp_code=corp_code)
    started = client.request_count
    begin = subscription_end - timedelta(days=_LOOKBACK_DAYS)
    # A 정정 can land after the 청약 closes (a 실적보고서-era 기재정정), so the
    # window runs a month past it.
    end = subscription_end + timedelta(days=30)

    try:
        rows = client.filings(
            begin.strftime("%Y%m%d"),
            end.strftime("%Y%m%d"),
            corp_code=corp_code,
            pblntf_ty=_PBLNTF_TY,
            pages=5,
        )
    except RequestBudgetExceeded:
        raise
    except DartError as exc:
        outcome.status, outcome.note = "error", f"list.json failed: {type(exc).__name__}"
        outcome.requests = client.request_count - started
        return outcome

    closes = subscription_end.strftime("%Y%m%d")
    offering = [r for r in rows if parse_report_nm(r.get("report_nm"))[1] in _SUBTYPES]
    if not offering:
        outcome.status = "not_found"
        outcome.note = (
            f"no 유상/유무상증자결정 in corp-scoped list.json "
            f"{begin:%Y%m%d}~{end:%Y%m%d}"
        )
        outcome.requests = client.request_count - started
        return outcome

    # A corp can have filed both kinds over 800 days; the offering that closed on
    # ``subscription_end`` is the newest one that predates it.
    anchor = max(
        [r for r in offering if r.get("rcept_dt") and r["rcept_dt"] <= closes] or offering,
        key=lambda r: (r["rcept_dt"], r["rcept_no"]),
    )
    subtype = parse_report_nm(anchor.get("report_nm"))[1]
    endpoint = _SUBTYPES[subtype]
    offering = [r for r in offering if parse_report_nm(r.get("report_nm"))[1] == subtype]
    before_close = [r for r in offering if r.get("rcept_dt") and r["rcept_dt"] <= closes]
    originals = [
        r
        for r in before_close
        if CorrectionKind.from_report_nm(r.get("report_nm")) is CorrectionKind.ORIGINAL
    ]
    if originals:
        head = max(originals, key=lambda r: (r["rcept_dt"], r["rcept_no"]))
        method = "original"
    elif before_close:
        # N21's placeholder pattern, reached from the other end: OpenDART's
        # corp-scoped list can show a 정정 whose original is no longer listed
        # (코이즈 ``20260129000503``: six 기재정정, no original, over 2+ years).
        # The 정정's own 본문 carries the whole form, so the chain still yields
        # every value this estimate needs — it is the *identity* that is
        # provisional, and that is what the flag records.
        head = min(before_close, key=lambda r: (r["rcept_dt"], r["rcept_no"]))
        method = "unpaired_correction_head"
    else:
        outcome.status = "no_original"
        outcome.note = f"{len(offering)} {subtype} row(s), none on/before 청약 종료일"
        outcome.requests = client.request_count - started
        return outcome

    original = head
    chain = [r for r in offering if r["rcept_dt"] >= original["rcept_dt"]]

    ensure_corp(
        session,
        corp_code,
        corp_name=corp_name or original.get("corp_name"),
        stock_code=original.get("stock_code"),
        corp_cls=original.get("corp_cls"),
    )
    event = ensure_event(
        session,
        corp_code=corp_code,
        report_subtype=endpoint,
        original_rcept_dt=original["rcept_dt"],
        rights_type=RightsType.SUBSCRIPTION_WARRANT,
        report_nm=original.get("report_nm"),
    )
    for row in sorted(chain, key=lambda r: (r["rcept_dt"], r["rcept_no"])):
        version = ensure_version(
            session,
            event,
            rcept_no=row["rcept_no"],
            rcept_dt=row["rcept_dt"],
            report_nm=row.get("report_nm"),
            pairing_method=method if row is original else "adopted_chain",
        )
        ensure_snapshot(session, version, source="list", payload_json=row)
        outcome.versions += 1
        outcome.rcept_nos.append(row["rcept_no"])

    _adopt_detail(session, client, event, endpoint, original["rcept_dt"], subscription_end)
    outcome.documents = _adopt_documents(session, client, event, limit=documents)
    outcome.status = "adopted"
    outcome.note = f"{subtype} via {method}"
    outcome.event_id = event.id
    outcome.original_rcept_dt = event.original_rcept_dt
    outcome.requests = client.request_count - started
    return outcome


def _adopt_detail(
    session,
    client: DartClient,
    event: Event,
    endpoint: str,
    original_dt: str,
    subscription_end: date,
) -> None:
    """Snapshot the ``piicDecsn`` row onto the version it names.

    The detail endpoint windows on the **original** 접수일 (N3) and returns one
    row per event carrying the newest ``rcept_no`` (N2), so the row is attached
    to the version whose ``rcept_no`` it states — never to the original by
    default.
    """
    try:
        body = client.get_json(
            endpoint,
            corp_code=event.corp_code,
            bgn_de=original_dt,
            end_de=subscription_end.strftime("%Y%m%d"),
        )
    except RequestBudgetExceeded:
        raise
    except DartError:
        return
    for row in body.get("list") or []:
        for version in event.versions:
            if version.rcept_no == row.get("rcept_no"):
                ensure_snapshot(session, version, source=endpoint, payload_json=row)


def _adopt_documents(session, client: DartClient, event: Event, *, limit: int) -> int:
    """Fetch the newest ``limit`` readable 본문 — the 할인율 lives in 24-가 prose."""
    from mijual.bodydoc.backfill import load_document

    readable = sorted(
        (v for v in event.versions if v.correction_kind is not CorrectionKind.ATTACHMENT),
        key=lambda v: (v.rcept_dt or date.min, v.rcept_no),
        reverse=True,
    )
    fetched = 0
    for version in readable[:limit]:
        blob, origin = load_document(session, client, version, fetch=True)
        if blob is not None and origin in ("cache", "live"):
            fetched += 1
    return fetched
