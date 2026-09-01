"""마감 임박 이메일: who gets one, about what, and never twice.

The last unbuilt product feature. R5 designed the setting (시점 칩 7일/3일/1일/당일,
기본 7일+1일) and the mail, P5 stored the preference, and this module is the part
that reads both and actually sends — as a **pipeline stage on its own lock**
(:func:`mijual.scheduler.pipeline.stage_notify`), fired by the ``notify-deadlines``
beat entry at 08:30 KST, an hour after the morning corpus run.

**Selection reuses the reader's own surface, exactly.** A candidate is a row of
:func:`mijual.web.reads.load_portfolio`'s ``upcoming`` list whose
``countdown.days`` is one of that reader's 시점 칩. That is deliberately the same
composition the 내 포트폴리오 page renders, not a query written for mail: a mail
that said ``D-7`` about a deadline the page did not show — or that used a second
definition of "다가오는" — would be the product contradicting itself in the one
place the reader cannot refresh. The same rule covers 알림 설정
(:func:`mijual.web.portfolio.lead_days_of`, so an absent row means R5's default
7일+1일 and ``[]`` means no mail) and the address
(:attr:`mijual.db.models.Account.email`: `security` fixes stored PII at email +
password hash, so there is no second address anywhere to send to).

**Idempotency is a row, not a guess** (:class:`mijual.db.models.NotificationSend`,
whose docstring carries the key's reasoning): one mail per
``(reader, event, lead day, anchor date)``, written **after** the transport
accepted the message and committed per message, so a stage that dies halfway
re-sends nothing it already sent. A 정정 that moves the 마감 is a new anchor date
and mails again, on purpose.

**Two ceilings and one containment rule.**

* ``max_mails`` is a structural ceiling like every other outward action in this
  codebase (``DartClient(max_requests=…)``, ``GeminiClient(max_calls=…)``): it is
  reported as ``budget_exhausted``, a **stop**, never an exception.
* A per-message failure is contained: one address the server rejects must not
  cost every other reader their mail, so it counts as ``failed`` and the run goes
  on.

**Logs carry account ids, ``rcept_no`` and lead days — never an email address and
never a subject.** An address in a log is the same address the schema promise is
about, and a subject line names a company a reader holds.

This module writes no Korean. Everything a reader reads comes from
:mod:`mijual.mailcopy` through :func:`mijual.mail.render`.
"""

from __future__ import annotations

import logging
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass, field
from datetime import date
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from mijual.beat import NOTIFY_MAX_MAILS
from mijual.calc import allotted_shares
from mijual.db.models import Account, Holding, NotificationSend
from mijual.db.session import session_scope
from mijual.mail import DEADLINE, Mailer, Message
from mijual.web.portfolio import entries_of, lead_days_of
from mijual.web.reads import load_portfolio

__all__ = [
    "DEFAULT_MAX_MAILS",
    "EVENT_PATH",
    "NOTIFICATIONS_PATH",
    "NotifyReport",
    "deadline_data",
    "send_deadlines",
]

log = logging.getLogger(__name__)

#: The structural ceiling on one run's outward mail — **declared in
#: :mod:`mijual.beat`** (200), the stdlib module both the scheduler config and
#: this one can read, so the number is stated once. It is far above today's
#: corpus (a handful of accounts) and far below anything that could look like a
#: mailing list, which is the point: a runaway selection stops and says so
#: instead of sending until the provider rate-limits it.
DEFAULT_MAX_MAILS = NOTIFY_MAX_MAILS

#: The two reader paths a mail links to. **Mirrored from
#: ``frontend/lib/routes.ts``, which is the path authority** (``eventPath`` and
#: ``ROUTES.notifications``) — not invented here, and not a second spelling of a
#: route: a mail whose link 404s is worse than no link.
EVENT_PATH = "/events/{rcept_no}"
NOTIFICATIONS_PATH = "/portfolio/notifications"


@dataclass
class NotifyReport:
    """What one send did, in counts. No address, no subject, no Korean."""

    anchor: str = ""
    transport: str = "console"
    accounts: int = 0
    candidates: int = 0
    sent: int = 0
    already_sent: int = 0
    skipped_no_chips: int = 0
    failed: int = 0
    budget_exhausted: bool = False
    max_mails: int | None = DEFAULT_MAX_MAILS
    notes: list[str] = field(default_factory=list)

    @property
    def summary(self) -> str:
        return (
            f"anchor {self.anchor} | transport {self.transport} | "
            f"{self.accounts} account(s), {self.candidates} candidate(s) -> "
            f"sent {self.sent}, already-sent {self.already_sent}, "
            f"skipped-no-chips {self.skipped_no_chips}, failed {self.failed}"
            + (f" | ceiling {self.max_mails}" if self.budget_exhausted else "")
        )

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


# ---------------------------------------------------------------------------
# one candidate row -> one message
# ---------------------------------------------------------------------------
def _figure(payload: Any, key: str) -> Any:
    """The ``value`` of a :class:`mijual.present.values.Figure` payload, or ``None``."""
    figure = payload.get(key) if isinstance(payload, Mapping) else None
    return figure.get("value") if isinstance(figure, Mapping) else None


def deadline_data(row: Mapping[str, Any], *, app_base_url: str) -> dict[str, str]:
    """One ``upcoming`` row as :data:`mijual.mail.DEADLINE` ``data``.

    **Data, never copy, and never a won amount.** ``label_ko`` and ``dday`` are
    the served strings passed through verbatim
    (:data:`mijual.present.event.COUNTDOWN_LABELS_KO` and
    :attr:`mijual.calc.DDay.label`), the ① conversion is
    :func:`mijual.calc.allotted_shares` — the same floored ``Decimal``
    multiplication the browser does, so the mail and the page cannot disagree by
    a share — and the price appears only as ``price_state``: ``confirmed`` or
    ``pending``. There is no key here a figure could travel in, which is how
    「확정발행가 전 금액 금지 — 메일에도 동일」 stays true by construction rather
    than by review.
    """
    countdown = row.get("countdown") or {}
    window = list(countdown.get("window") or [None, None])
    base = (app_base_url or "").rstrip("/")
    rcept_no = row.get("rcept_no") or ""

    data: dict[str, str] = {
        "corp_name": str(row.get("corp_name") or ""),
        "corp_code": str(row.get("corp_code") or ""),
        "rights_type": str(row.get("rights_type") or ""),
        "label_ko": str(countdown.get("label_ko") or ""),
        "date": str(countdown.get("date") or ""),
        "dday": str(countdown.get("dday") or ""),
        "days": str(countdown.get("days")) if countdown.get("days") is not None else "",
        "window_start": str(window[0] or ""),
        "window_end": str(window[1] or "") if len(window) > 1 else "",
        "rcept_no": str(rcept_no),
        "settings_url": f"{base}{NOTIFICATIONS_PATH}",
    }
    if rcept_no:
        data["event_url"] = base + EVENT_PATH.format(rcept_no=rcept_no)

    shares = row.get("shares")
    if isinstance(shares, int) and shares > 0:
        data["shares"] = str(shares)
        offering = row.get("offering")
        # ① only: ② and ③ have no share conversion and no price fact at all.
        if row.get("rights_type") == "R1" and isinstance(offering, Mapping):
            ratio = _figure(offering, "allotment_ratio")
            if ratio is not None:
                data["allotted_shares"] = str(allotted_shares(shares, ratio))
            data["price_state"] = (
                "confirmed" if offering.get("price_confirmed") else "pending"
            )
            final_price_date = offering.get("final_price_date")
            if final_price_date:
                data["final_price_date"] = str(final_price_date)
    return {key: value for key, value in data.items() if value}


def _message(account: Account, row: Mapping[str, Any], *, app_base_url: str) -> Message:
    return Message(
        to=account.email,
        kind=DEADLINE,
        data=deadline_data(row, app_base_url=app_base_url),
    )


# ---------------------------------------------------------------------------
# the run
# ---------------------------------------------------------------------------
class _Batch:
    """Hold one SMTP conversation open across a run — but only if one is needed.

    Opened **lazily, on the first actual send**, for two reasons: a day with no
    candidate costs no login, and a misconfigured SMTP host does not fail a stage
    that had nothing to send anyway. A transport with no ``open``/``close`` (the
    console one, a recording mailer in a test) is used exactly as it is.
    """

    def __init__(self, mailer: Mailer) -> None:
        self._mailer = mailer
        self._opened = False

    def send(self, message: Message) -> None:
        opener = getattr(self._mailer, "open", None)
        if not self._opened and callable(opener):
            opener()
            self._opened = True
        self._mailer.send(message)

    def close(self) -> None:
        closer = getattr(self._mailer, "close", None)
        if self._opened and callable(closer):
            closer()
            self._opened = False


def _candidates(
    session: Session, account: Account, lead_days: Sequence[int], *, today: date
) -> list[tuple[int, Mapping[str, Any]]]:
    """``(lead_day, row)`` for every 다가오는 deadline this reader asked about.

    ``load_portfolio``'s ``upcoming`` is dated rows first, then **open ② rows**
    (``days < 0``) and **추후결정 rows** (``date is None``) — neither of which is
    a deadline anyone can be warned about, and both of which are excluded here by
    the same one condition: ``days`` must be one of the reader's chips, and every
    chip is ``>= 0``.
    """
    entries = entries_of(session, account)
    if not entries:
        return []
    payload = load_portfolio(session, entries, today=today)
    chosen = set(lead_days)
    found: list[tuple[int, Mapping[str, Any]]] = []
    for row in payload.get("upcoming", []):
        days = (row.get("countdown") or {}).get("days")
        if isinstance(days, int) and days in chosen and (row.get("countdown") or {}).get("date"):
            found.append((days, row))
    return found


def send_deadlines(
    factory,
    mailer: Mailer,
    *,
    today: date,
    app_base_url: str,
    max_mails: int | None = DEFAULT_MAX_MAILS,
    transport: str = "console",
) -> NotifyReport:
    """Mail every reader the deadlines their 알림 설정 asked for. Once each.

    ``factory`` is a session factory rather than a session: the record of a send
    is committed **per message**, so a crash mid-run cannot un-remember mail that
    already left. ``today`` is the KST anchor (R5: 발송 앵커 KST) and is an
    argument rather than a clock read, so a test and the ``--notify-today``
    inspection knob use the same code path the beat does.
    """
    report = NotifyReport(anchor=today.isoformat(), transport=transport, max_mails=max_mails)
    with session_scope(factory) as session:
        account_ids = list(
            session.scalars(
                select(Holding.account_id).distinct().order_by(Holding.account_id)
            ).all()
        )
    report.accounts = len(account_ids)
    if not account_ids:
        return report

    batch = _Batch(mailer)
    try:
        for account_id in account_ids:
            if report.budget_exhausted:
                break
            with session_scope(factory) as session:
                account = session.get(Account, account_id)
                if account is None:  # deleted between the two reads
                    continue
                _send_for_account(
                    session, account, batch, report, today=today, app_base_url=app_base_url
                )
    finally:
        batch.close()
    return report


def _send_for_account(
    session: Session,
    account: Account,
    batch: _Batch,
    report: NotifyReport,
    *,
    today: date,
    app_base_url: str,
) -> None:
    lead_days = lead_days_of(session, account)
    if not lead_days:
        # `[]` is a valid, deliberate setting and the only off switch R5 ships.
        report.skipped_no_chips += 1
        return

    for lead_day, row in _candidates(session, account, lead_days, today=today):
        report.candidates += 1
        event_id = row.get("event_id")
        anchor_date = str((row.get("countdown") or {}).get("date") or "")
        if not isinstance(event_id, int) or not anchor_date:
            continue
        already = session.scalars(
            select(NotificationSend).where(
                NotificationSend.account_id == account.id,
                NotificationSend.event_id == event_id,
                NotificationSend.lead_day == lead_day,
                NotificationSend.anchor_date == anchor_date,
            )
        ).first()
        if already is not None:
            report.already_sent += 1
            continue
        if report.max_mails is not None and report.sent >= report.max_mails:
            report.budget_exhausted = True
            report.notes.append(
                f"ceiling {report.max_mails} reached — the rest of this run sent nothing"
            )
            return
        try:
            batch.send(_message(account, row, app_base_url=app_base_url))
        except Exception as exc:  # noqa: BLE001 - one address must not stop the run
            report.failed += 1
            # Account id and filing number, never the address, never the subject.
            log.warning(
                "notify: send failed for account %s rcept_no %s D-%s (%s)",
                account.id,
                row.get("rcept_no"),
                lead_day,
                type(exc).__name__,
            )
            continue
        session.add(
            NotificationSend(
                account_id=account.id,
                event_id=event_id,
                rcept_no=row.get("rcept_no"),
                lead_day=lead_day,
                anchor_date=anchor_date,
            )
        )
        # Committed message by message: the record of a send must survive
        # whatever kills the rest of the run.
        session.commit()
        report.sent += 1
        log.info(
            "notify: sent account %s rcept_no %s D-%s anchor %s",
            account.id,
            row.get("rcept_no"),
            lead_day,
            anchor_date,
        )
