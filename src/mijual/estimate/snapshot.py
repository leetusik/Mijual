"""The serving precomputation: what a request path may not compute for itself.

Two numbers the landing page and the ① detail card show cannot be derived on a
request:

* an offering's **확정발행가 / 할인율 / 배정비율 / 청약일정** — read by
  :func:`mijual.estimate.event_inputs`, which decodes the event's stored 본문 ZIP
  and parses its labels;
* the **소멸가치** of a closed offering — :func:`mijual.estimate.build_report`,
  which needs those inputs beside the 실적보고서's own cited counts.

Both live in :mod:`mijual.estimate`, and :mod:`mijual.estimate` imports
:mod:`mijual.dart`, :mod:`mijual.collect` and :mod:`mijual.extract` at module
level — the three modules that can spend an OpenDART request or a model call. The
`architecture` boundary forbids importing any of them from the HTTP layer, and
``tests/test_web_smoke.py`` enforces it by walking the imports. So this module is
the seam: **the worker computes, the request path reads.**

    .venv/bin/python -m mijual.estimate snapshot      # 0 requests, 0 LLM calls

What it writes is **inputs, never products**: :class:`~mijual.db.models.OfferingInput`
rows and one ``LapseRow`` mapping per 증권발행실적보고서. Every figure a surface
shows is still derived on read by :mod:`mijual.present`, so the stored rows cannot
disagree with the rendered ones — they can only be *older* than the corpus, which
is exactly what the board's 기준시각 says out loud.

Re-running is idempotent and cheap (one row per ① event, updated in place), and it
is safe to run beside the pipeline: it reads what the pipeline persisted and
writes only its own two places.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from mijual.db.models import Event, OfferingInput, PerformanceReport, RightsType
from mijual.estimate import build_report, event_inputs

__all__ = ["SnapshotReport", "refresh_serving_snapshot"]


@dataclass
class SnapshotReport:
    """What one refresh wrote."""

    offerings: int = 0
    priced: int = 0
    upcoming: int = 0
    lapse_rows: int = 0
    valued: int = 0
    notes: list[str] = field(default_factory=list)

    def render(self) -> str:
        lines = [
            f"offerings  : {self.offerings} ① event(s) precomputed "
            f"({self.priced} with a 확정발행가, {self.upcoming} with a 청약 still ahead)",
            f"lapse rows : {self.lapse_rows} 실적보고서 valued or counted ({self.valued} valued)",
        ]
        lines.extend(f"  ! {note}" for note in self.notes)
        return "\n".join(lines)


def refresh_serving_snapshot(session: Session, *, today: date) -> SnapshotReport:
    """Recompute both stores from persisted rows. **0 requests, 0 LLM calls.**

    ``today`` only reaches :func:`mijual.estimate.build_report`'s pending split
    (which the API does not read); nothing time-dependent is *stored*, so a stale
    snapshot is stale about the corpus, never about the calendar.
    """
    report = SnapshotReport()

    stored = {
        row.event_id: row
        for row in session.scalars(select(OfferingInput)).all()
    }
    events = session.scalars(
        select(Event).where(Event.rights_type == RightsType.SUBSCRIPTION_WARRANT)
    ).all()
    for event in events:
        inputs = event_inputs(session, event)
        row = stored.get(event.id)
        if row is None:
            row = OfferingInput(event_id=event.id)
            session.add(row)
        start, end = inputs.shareholder_window
        row.corp_code = event.corp_code
        row.decision_rcept_no = inputs.rcept_no
        row.price_confirmed = inputs.confirmed_price is not None
        row.subscription_start = start
        row.subscription_end = end
        row.inputs = inputs.as_json()
        report.offerings += 1
        report.priced += 1 if row.price_confirmed else 0
        report.upcoming += 1 if end is not None and end > today else 0
    session.flush()

    # The report is built after the inputs are written so both stores describe
    # the same reading of the same corpus.
    lapse = build_report(session, today=today)
    by_rcept = {
        row.performance_rcept_no: row for row in lapse.rows if row.performance_rcept_no
    }
    for stored_report in session.scalars(select(PerformanceReport)).all():
        row = by_rcept.get(stored_report.rcept_no)
        stored_report.lapse = row.as_json() if row is not None else None
        if row is not None:
            report.lapse_rows += 1
            report.valued += 1 if row.is_valued else 0
    session.flush()
    return report
