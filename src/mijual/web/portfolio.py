"""내 포트폴리오 — the reader's own holdings, marks and 알림 preferences.

The service layer behind :mod:`mijual.web.routers.portfolio`, the same split
:mod:`mijual.web.auth` uses: the decisions live here, the transport lives there,
and the *composition* of the D-day list lives in
:func:`mijual.web.reads.load_portfolio` beside every other loader.

**This is the only gated surface in the product** (R5, `security`). Everything
else — the board, an event page, 내 종목 조회, the sample portfolio below — answers
without a cookie, and nothing this module adds changes that.

**Anonymous holdings never reach the server, by design.** R5 keeps an anonymous
or sample reader's edits in ``localStorage`` and a 조회 보유량 in
``sessionStorage``, and `security` states it as a boundary: "Anonymous state never
reaches the server … Migration into an account is **offered, never automatic**".
So there is no anonymous holdings endpoint and no anonymous write of any kind.
The 세션 이월 / 이전 제안 flows are entirely the client's: when the reader accepts
one, the browser makes the ordinary authenticated calls below, and when they
decline, nothing is sent.

**Every route here is owner-scoped and a stranger's row is a 404, not a 403.**
Every lookup carries ``account_id`` in its ``WHERE``; a holding that belongs to
somebody else is indistinguishable from one that does not exist, because a 403
would confirm that it does.

**Three prohibitions this module keeps structurally**, each one R5's:

* it stores **no money and no derived figure** — a holding is an issuer and a
  count, a 챙긴 돈 mark is a filing number, and every won amount in the product
  is still derived on read by :mod:`mijual.present` from the pipeline's rows;
* the 챙긴 돈 mark is a **user assertion** and reaches **no aggregate at all** —
  the portfolio payload has no total for it to reach;
* it invents no Korean. Failures travel as structural codes
  (``holding_exists`` · ``invalid_shares`` · ``invalid_lead_days`` ·
  ``not_found``) and the surface says what R5 signed.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from typing import Any

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from mijual.db.models import Account, Corp, Holding, LapseClaim, NotificationPref, PerformanceReport
from mijual.web.errors import ApiError, NotFound
from mijual.web.reads import HoldingEntry, stock_by_code

__all__ = [
    "DEFAULT_LEAD_DAYS",
    "LEAD_DAY_CHOICES",
    "MAX_SHARES",
    "SAMPLE_HOLDINGS",
    "add_holding",
    "claimed_reports",
    "delete_holding",
    "entries_of",
    "holding_payload",
    "holdings_of",
    "lead_days_of",
    "notifications_payload",
    "sample_entries",
    "set_claim",
    "set_lead_days",
    "update_holding",
]

#: 마감 임박 시점 칩, in the order R5 draws them. ``0`` is 당일.
LEAD_DAY_CHOICES = (7, 3, 1, 0)
#: R5's own default — 7일 전 + 1일 전. Served until the reader saves a setting;
#: see :class:`mijual.db.models.NotificationPref` for why no row is created at
#: signup.
DEFAULT_LEAD_DAYS = (7, 1)

#: An upper bound on a share count, not a business rule. 삼성전자 — the largest
#: listing on the market — has ~5.97 billion shares outstanding, so ten billion
#: cannot be a holding of a Korean company and a twenty-digit number is a typo or
#: a probe. Refusing it here keeps the column's own range honest.
MAX_SHARES = 10_000_000_000

#: The fixed R5-4 sample composition: four **real** filings covering the four
#: states the surface can be in, with the 보유량 stated on the card as an example.
#: The ``rcept_no`` beside each one is the filing R5 pinned; it is a comment
#: rather than a lookup key, because a holding is an *issuer* and the sample must
#: load whatever that issuer's rights actually are today (build prompt: "실제
#: corpus 이벤트를 그대로 로드, 수치는 서버 contract에서"). Verified 2026-08-22 —
#: all four still resolve to the event R5 named; see this slice's phase note for
#: what each one carries now.
SAMPLE_HOLDINGS = (
    ("00102618", 500),  # 계양전기 · ① 발행가 확정 전   · 20260724000546
    ("00109310", 300),  # 대동기어  · ② 전환청구 개시    · 20251016000315
    ("00162461", 500),  # 한화솔루션 · ① 소멸 (놓친 돈)  · 20260720000067
    ("00133618", 100),  # 세기상사  · ③ 통지 마감 지남   · 20260713000345
)


# ---------------------------------------------------------------------------
# holdings
# ---------------------------------------------------------------------------
def _validated_shares(raw: Any) -> int:
    """보유 주식 수: a positive whole number of shares, and nothing cleverer.

    R4's signed input is ``inputMode="numeric"`` with comma grouping and the
    100/500/1,000주 presets, so a fraction is not a thing the surface can produce
    and a zero is a deletion rather than a holding.
    """
    try:
        shares = int(raw)
    except (TypeError, ValueError):
        raise ApiError("invalid_shares", "shares must be a whole number") from None
    if shares < 1 or shares > MAX_SHARES:
        raise ApiError("invalid_shares", f"shares must be between 1 and {MAX_SHARES}")
    return shares


def holdings_of(db: Session, account: Account) -> list[Holding]:
    """This account's holdings, oldest first — the order the rows were added."""
    return list(
        db.scalars(
            select(Holding)
            .where(Holding.account_id == account.id)
            .order_by(Holding.created_at, Holding.id)
        ).all()
    )


def entries_of(db: Session, account: Account) -> list[HoldingEntry]:
    """This account's portfolio as composition input."""
    return [
        HoldingEntry(corp_code=row.corp_code, shares=row.shares, holding_id=row.id)
        for row in holdings_of(db, account)
    ]


def sample_entries() -> list[HoldingEntry]:
    """The R5-4 sample composition. No ``holding_id`` — nothing is stored."""
    return [HoldingEntry(corp_code=code, shares=shares) for code, shares in SAMPLE_HOLDINGS]


def _holding(db: Session, account: Account, holding_id: int) -> Holding:
    """One of **this** account's holdings, or a 404. See the module docstring."""
    row = db.scalars(
        select(Holding).where(
            Holding.id == holding_id, Holding.account_id == account.id
        )
    ).first()
    if row is None:
        raise NotFound("holding")
    return row


def add_holding(db: Session, account: Account, *, corp_code: str, shares: Any) -> Holding:
    """담기: one issuer, one count.

    The issuer arrives as a ``corp_code`` — the stable handle every reader surface
    already links by — and is validated against the corpus here. **Resolution of a
    typed 종목명 is not repeated in this module**: ``GET /stocks?q=`` is the one
    place a reader's text becomes a company, it owns R4's signed 검색 불일치 state,
    and a second resolver would be a second way to open the wrong company's page.

    A repeat 담기 of a company already held is **refused**, not merged — see
    :class:`mijual.db.models.Holding`.
    """
    count = _validated_shares(shares)
    corp = stock_by_code(db, (corp_code or "").strip())
    if corp is None:
        raise NotFound("stock")

    existing = db.scalars(
        select(Holding).where(
            Holding.account_id == account.id, Holding.corp_code == corp.corp_code
        )
    ).first()
    if existing is not None:
        raise ApiError(
            "holding_exists",
            "this account already holds that stock; edit the row instead",
            status_code=409,
        )

    row = Holding(account_id=account.id, corp_code=corp.corp_code, shares=count)
    db.add(row)
    try:
        db.flush()
    except IntegrityError as exc:  # two tabs, one account, one instant
        db.rollback()
        raise ApiError(
            "holding_exists",
            "this account already holds that stock; edit the row instead",
            status_code=409,
        ) from exc
    return row


def update_holding(db: Session, account: Account, holding_id: int, *, shares: Any) -> Holding:
    """보유량 수정 — R5's inline row edit. The 종목 of a row never changes."""
    row = _holding(db, account, holding_id)
    row.shares = _validated_shares(shares)
    db.flush()
    return row


def delete_holding(db: Session, account: Account, holding_id: int) -> None:
    """삭제 = **즉시**, with no dialog (R5).

    The 8초 되돌리기 is the client's, and undoing is an ordinary re-add: the row
    comes back with a new ``id``, which costs nothing because nothing in the
    product links to a holding by id.
    """
    db.delete(_holding(db, account, holding_id))
    db.flush()


def holding_payload(row: Holding, corp: Corp | None) -> dict[str, Any]:
    """What a mutation answers with: the row, named. Absent keys, never nulls."""
    out: dict[str, Any] = {
        "id": row.id,
        "corp_code": row.corp_code,
        "shares": row.shares,
    }
    if corp is not None:
        out["corp_name"] = corp.corp_name
        if corp.stock_code:
            out["stock_code"] = corp.stock_code
    return out


# ---------------------------------------------------------------------------
# 챙긴 돈 marks (R5-8)
# ---------------------------------------------------------------------------
def claimed_reports(db: Session, account: Account) -> frozenset[str]:
    """The 실적보고서 filing numbers this reader has marked 챙겼습니다."""
    return frozenset(
        db.scalars(
            select(LapseClaim.performance_rcept_no).where(
                LapseClaim.account_id == account.id
            )
        ).all()
    )


def set_claim(
    db: Session, account: Account, performance_rcept_no: str, *, claimed: bool
) -> bool:
    """체크 / 체크 해제 on one past ① 소멸 row. Idempotent, and it stores no amount.

    The filing number is checked against the corpus first: a claim is a statement
    about a **real 증권발행실적보고서 with a 소멸 outcome**, and validating it keeps
    an authenticated caller from turning this table into arbitrary storage. It is
    deliberately *not* checked against the caller's holdings — a reader may sell a
    position and their claim about a past offering stays true, and a check that
    depended on the current portfolio would silently drop marks on a 삭제.
    """
    key = (performance_rcept_no or "").strip()
    report = db.scalars(
        select(PerformanceReport).where(
            PerformanceReport.rcept_no == key, PerformanceReport.lapse.is_not(None)
        )
    ).first()
    if report is None:
        raise NotFound("lapse")

    existing = db.scalars(
        select(LapseClaim).where(
            LapseClaim.account_id == account.id,
            LapseClaim.performance_rcept_no == key,
        )
    ).first()
    if claimed and existing is None:
        db.add(LapseClaim(account_id=account.id, performance_rcept_no=key))
    elif not claimed and existing is not None:
        db.delete(existing)
    db.flush()
    return claimed


# ---------------------------------------------------------------------------
# 알림 설정 (R5-5 / R5-7) — preferences only; sending is P4's
# ---------------------------------------------------------------------------
def _validated_lead_days(raw: Any) -> list[int]:
    """The 시점 칩 selection: a subset of :data:`LEAD_DAY_CHOICES`, in chip order.

    An **empty** selection is valid and means no mail — R5's mail footer promises
    "알림 설정에서 끌 수 있습니다" and deselecting every chip is the only off switch
    the signed surface has, so it must persist rather than fall back to the
    default. Anything outside the four chips is refused: a lead time the UI cannot
    express is a lead time nobody could ever turn off again.
    """
    if not isinstance(raw, (list, tuple)):
        raise ApiError("invalid_lead_days", "lead_days must be a list of days")
    chosen: set[int] = set()
    for item in raw:
        if isinstance(item, bool) or not isinstance(item, int) or item not in LEAD_DAY_CHOICES:
            raise ApiError(
                "invalid_lead_days",
                f"lead_days may only contain {', '.join(str(d) for d in LEAD_DAY_CHOICES)}",
            )
        chosen.add(item)
    return [day for day in LEAD_DAY_CHOICES if day in chosen]


def lead_days_of(db: Session, account: Account) -> list[int]:
    """This account's 시점 칩, or the default when they have never saved one.

    **No row is created here.** A read that wrote would need a committing session
    on a ``GET``, which this service structurally refuses
    (:func:`mijual.web.deps.get_write_session`), and an absent row is the honest
    record of "never chosen" — it also means the default can be revised without
    touching a single stored account.
    """
    pref = db.scalars(
        select(NotificationPref).where(NotificationPref.account_id == account.id)
    ).first()
    if pref is None or not isinstance(pref.lead_days, list):
        return list(DEFAULT_LEAD_DAYS)
    return _sorted_chips(pref.lead_days)


def _sorted_chips(stored: Iterable[Any]) -> list[int]:
    values = {item for item in stored if isinstance(item, int)}
    return [day for day in LEAD_DAY_CHOICES if day in values]


def _pref_of(db: Session, account: Account) -> NotificationPref | None:
    return db.scalars(
        select(NotificationPref).where(NotificationPref.account_id == account.id)
    ).first()


def set_lead_days(db: Session, account: Account, raw: Any) -> list[int]:
    """Save the 시점 칩 selection, creating the row on first use. **An upsert.**

    ``D-7``, fixed in ``P4.S2``: this was a read-then-insert against
    ``uq_notification_pref_account``, so two saves racing on one account — two
    tabs, a double-tapped 저장, a retried request — resolved as a
    ``UniqueViolation`` 500 rather than as the second save winning. The window is
    small and the surface is one reader's own settings, but this is the row the
    D-day mail reads, and a save that failed is a reader who does not get the
    mail they just asked for.

    The recovery is dialect-neutral rather than an ``ON CONFLICT``: a savepoint
    around the insert, and on collision a re-select and an update. One code path
    on Postgres (the deployment) and SQLite (the tests), which matters more here
    than the round trip an upsert would save — this endpoint runs at human speed.
    The API contract does not change: same validation, same return value.
    """
    days = _validated_lead_days(raw)
    pref = _pref_of(db, account)
    if pref is not None:
        pref.lead_days = days
        db.flush()
        return days

    try:
        with db.begin_nested():
            db.add(NotificationPref(account_id=account.id, lead_days=days))
            db.flush()
    except IntegrityError:
        # Somebody else inserted this account's row between the select above and
        # the flush. Their row is the row; this save is an update of it.
        pref = _pref_of(db, account)
        if pref is None:  # pragma: no cover - the constraint said it exists
            raise
        pref.lead_days = days
        db.flush()
    return days


def notifications_payload(account: Account, lead_days: Sequence[int]) -> dict[str, Any]:
    """R5's 알림 설정 surface, minus the two things it must not carry.

    ``address`` **is** the account's email, because `security` fixes stored PII to
    email + password hash and a second address column would be a second thing to
    leak; "변경" therefore edits the account itself
    (:func:`mijual.web.auth.change_email`).

    There is **no KakaoTalk key**: R5 draws that row with a 「예정」 chip and no
    working control, and a stored flag for a channel that cannot be switched on
    would be exactly the non-functional switch the round forbids. The 로그아웃 and
    계정 삭제 rows on the same surface are already ``P5.S7``'s endpoints.
    """
    return {"address": account.email, "lead_days": list(lead_days)}
