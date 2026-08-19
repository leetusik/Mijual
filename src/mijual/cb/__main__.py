"""CLI for ② CB 오버행 — the calendar, its 본문 top-up, and the capped prose pass.

    # 1. the 오버행 캘린더 (0 requests, 0 calls) — P2.S7's evidence deliverable
    .venv/bin/python -m mijual.cb calendar --today 2026-09-07

    # 2. one event's structured facts, with the API field each came from
    .venv/bin/python -m mijual.cb show 20260521000775

    # 3. 본문 for the urgency set only, under an explicit ceiling
    .venv/bin/python -m mijual.cb documents --until 20261231 --limit 60 --max-requests 200

    # 4. fields 6–8 + the ② 정정 pass for the urgency set, under a call cap
    .venv/bin/python -m mijual.cb extract --until 20261231 --max-calls 80

Collection itself has no ② command: ``cvbdIsDecsn`` is a normal collector target
(``mijual.collect.targets``), so the 2026 window and the 2025-H2 backfill are both

    .venv/bin/python -m mijual.collect --bgn 20250601 --end <today> \\
        --endpoints cvbdIsDecsn --max-requests 2000 --no-documents

and the scheduled daily pipeline picks ② up with no extra entry.

Nothing here prints, writes or accepts a secret.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

from sqlalchemy import select

from mijual.calc import today_kst
from mijual.cb import (
    R2_REQUIRED_API_FIELDS,
    detail_row,
    event_facts,
    overhang_calendar,
    urgency_events,
)
from mijual.config import load_settings
from mijual.dart import DartClient, RequestBudgetExceeded
from mijual.db.models import Base, Event, FilingVersion, RightsType
from mijual.db.schema_sync import ensure_columns
from mijual.db.session import create_all, make_engine, make_session_factory, session_scope

#: Default urgency horizon: 전환청구 opening on or before this date is what makes
#: the 오버행 캘린더 urgent during the judging window (the D-1 backfill condition).
DEFAULT_UNTIL = "20261231"


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="python -m mijual.cb", description=__doc__)
    p.add_argument("--database-url", default=None)
    p.add_argument("--report", default=None, help="also write the run's counts as JSON here")
    p.add_argument("--quiet", action="store_true")
    sub = p.add_subparsers(dest="command", required=True)

    cal = sub.add_parser("calendar", help="the 오버행 캘린더 (0 requests, 0 calls)")
    cal.add_argument("--today", default=None, help="anchor date YYYYMMDD (default: today KST)")
    cal.add_argument("--horizons", nargs="+", type=int, default=[30, 90, 180])
    cal.add_argument("--show", type=int, default=12, help="rows of the soonest-opening table")
    cal.add_argument("--include-blocked", action="store_true",
                     help="also list events the exposure contract holds back")

    show = sub.add_parser("show", help="one ② event's structured facts")
    show.add_argument("rcept_no")

    docs = sub.add_parser("documents", help="본문 for the urgency set, budgeted")
    docs.add_argument("--until", default=DEFAULT_UNTIL, help="전환청구 개시일 horizon (YYYYMMDD)")
    docs.add_argument("--today", default=None, help="urgency anchor YYYYMMDD (default: today KST)")
    docs.add_argument("--limit", type=int, default=60, help="max documents to fetch live")
    docs.add_argument("--versions-per-event", type=int, default=2,
                      help="newest N readable versions per event (2 feeds the 정정 diff)")
    docs.add_argument("--blocked", action="store_true",
                      help="fetch for the events the exposure contract blocks instead "
                           "(no_detail / incomplete_api_row — where a 철회 hides)")
    docs.add_argument("--max-requests", type=int, default=300, help="live OpenDART ceiling")
    docs.add_argument("--cache-dir", default=None)
    docs.add_argument("--offline", action="store_true", help="cache only; never fetch")

    ext = sub.add_parser("extract", help="fields 6–8 + 정정 for the urgency set")
    ext.add_argument("--until", default=DEFAULT_UNTIL)
    ext.add_argument("--today", default=None, help="urgency anchor YYYYMMDD (default: today KST)")
    ext.add_argument("--limit", type=int, default=None, help="cap the event list")
    ext.add_argument("--max-calls", type=int, default=80, help="hard ceiling on LLM calls (money)")
    ext.add_argument("--dry-run", action="store_true", help="build prompts, call nothing")
    ext.add_argument("--no-corrections", action="store_true")
    return p


def _factory(args):
    engine = make_engine(args.database_url)
    create_all(engine)
    ensure_columns(engine, Base)
    return make_session_factory(engine)


def _as_date(value: str | None) -> date:
    if not value:
        return today_kst()
    return date(int(value[:4]), int(value[4:6]), int(value[6:8]))


# ---------------------------------------------------------------------------
def cmd_calendar(args, factory) -> dict:
    today = _as_date(args.today)
    with session_scope(factory) as session:
        calendar = overhang_calendar(session, today=today)
        print(calendar.render(horizons=tuple(args.horizons), show=args.show))
        payload = {
            "today": str(today),
            "events_total": calendar.events_total,
            "exposable": len(calendar.entries),
            "blocked": calendar.blocked,
            "by_filing_year": calendar.by_filing_year,
            "already_open": len(calendar.already_open),
            "opening_within": {
                str(d): [
                    {
                        "corp_name": e.corp_name,
                        "rcept_no": e.rcept_no,
                        "opens": str(e.facts.request_begin),
                        "overhang_pct": str(e.facts.overhang_pct),
                        "shares": str(e.facts.shares),
                        "conversion_price": str(e.facts.conversion_price),
                    }
                    for e in calendar.opening_within(d)
                ]
                for d in args.horizons
            },
        }
        if args.include_blocked:
            blocked = session.scalars(
                select(Event).where(
                    Event.rights_type == RightsType.CONVERTIBLE_OVERHANG,
                    Event.exposure_state != "exposable",
                )
            ).all()
            print("\nblocked events:")
            for event in sorted(blocked, key=lambda e: (e.exposure_state or "", e.corp_code))[:40]:
                print(
                    f"  [{event.exposure_state}:{event.exposure_reason}] {event.corp_code} "
                    f"{event.corp.corp_name if event.corp else ''} {event.original_rcept_dt}"
                )
        return payload


def cmd_show(args, factory) -> dict:
    with session_scope(factory) as session:
        version = session.scalar(
            select(FilingVersion).where(FilingVersion.rcept_no == args.rcept_no)
        )
        if version is None:
            print(f"no stored version {args.rcept_no}")
            return {}
        event = version.event
        facts = event_facts(session, event)
        row = detail_row(session, event)
        print(f"event      : {event.corp_code} {event.corp.corp_name} {event.report_subtype} "
              f"{event.original_rcept_dt} — {event.exposure_state}:{event.exposure_reason}")
        print(f"versions   : {[v.rcept_no for v in event.versions]}")
        print(f"API row    : rcept_no {facts.rcept_no} ({len(row)} field(s))")
        for key, name in R2_REQUIRED_API_FIELDS:
            print(f"  {name:<16} {key:<28} {row.get(key)}")
        print(f"  {'리픽싱 최저가액':<16} {'act_mktprcfl_cvprc_lwtrsprc':<28} {row.get('act_mktprcfl_cvprc_lwtrsprc')}")
        print(f"  {'사채 만기일':<16} {'bd_mtd':<28} {row.get('bd_mtd')}")
        print(f"  {'납입일':<16} {'pymd':<28} {row.get('pymd')}")
        print(f"parsed     : {facts}")
        return {"rcept_no": args.rcept_no, "complete": facts.complete}


def cmd_documents(args, factory) -> dict:
    """Fetch 본문 for the urgency set only — the prose fields are additive colour.

    Newest versions first inside each event, urgency order across events, so a
    ceiling that bites leaves the *soonest* countdown fully documented rather
    than every event half-documented.
    """
    from mijual.bodydoc.backfill import load_document
    from mijual.extract.runner import readable_versions

    settings = load_settings()
    client = DartClient(
        settings=settings,
        cache_dir=args.cache_dir,
        offline=args.offline,
        max_requests=args.max_requests,
    )
    until = _as_date(args.until)
    counts = {"events": 0, "wanted": 0, "snapshot": 0, "cache": 0, "live": 0,
              "missing": 0, "error": 0}
    started = client.request_count

    with session_scope(factory) as session:
        if args.blocked:
            # A ② event the contract blocks is exactly where a withdrawal hides:
            # OpenDART keeps the detail row of a withdrawn CB but blanks every
            # field to ``-``, so the countdown reads "incomplete" when the truth
            # is "cancelled". Only the 본문's 정정사항 row can tell the two apart.
            events = sorted(
                session.scalars(
                    select(Event).where(
                        Event.rights_type == RightsType.CONVERTIBLE_OVERHANG,
                        Event.exposure_state.in_(("no_detail", "incomplete_api_row")),
                    )
                ).all(),
                key=lambda e: (e.original_rcept_dt or date.min, e.corp_code),
                reverse=True,
            )
        else:
            events = urgency_events(session, until=until, today=_as_date(args.today))
        counts["events"] = len(events)
        wanted: list[FilingVersion] = []
        for event in events:
            # ``readable_versions`` is the same newest-last, 첨부정정-free ordering
            # the extractor and the gate layer use — one definition, three callers.
            readable = readable_versions(event)
            wanted.extend(reversed(readable[-args.versions_per_event:]))
        counts["wanted"] = len(wanted)

        for version in wanted:
            allow = counts["live"] < args.limit
            try:
                blob, origin = load_document(session, client, version, fetch=allow)
            except RequestBudgetExceeded:
                counts["budget_exhausted"] = True
                break
            counts[origin] = counts.get(origin, 0) + 1
            if blob is None and origin == "missing":
                continue
        session.flush()

    counts["requests"] = client.request_count - started
    scope = "blocked ② event(s)" if args.blocked else f"② event(s) opening <= {until}"
    print(f"targets    : {counts['events']} {scope}, {counts['wanted']} version(s) considered")
    print(
        f"documents  : snapshot {counts.get('snapshot', 0)}, cache {counts.get('cache', 0)}, "
        f"live {counts.get('live', 0)}, missing {counts.get('missing', 0)}, "
        f"errors {counts.get('error', 0)}"
    )
    print(f"requests   : {counts['requests']} live OpenDART request(s)"
          + (" — BUDGET EXHAUSTED" if counts.get("budget_exhausted") else ""))
    return counts


def cmd_extract(args, factory) -> dict:
    from mijual.extract.client import GeminiClient
    from mijual.extract.runner import run_corrections, run_extraction

    settings = load_settings()
    client = GeminiClient(settings=settings, max_calls=args.max_calls, dry_run=args.dry_run)
    until = _as_date(args.until)

    with session_scope(factory) as session:
        events = urgency_events(session, until=until, today=_as_date(args.today))
        ids = [e.id for e in events][: args.limit] if args.limit else [e.id for e in events]
    print(f"urgency    : {len(ids)} ② event(s) opening <= {until} (soonest first)")

    prose = run_extraction(
        client, factory, rights=RightsType.CONVERTIBLE_OVERHANG, event_ids=ids, log=None
    )
    print("\n" + prose.render())
    payload = {"prose": {"events": prose.events, "calls": prose.calls}}

    if not args.no_corrections and not prose.budget_exhausted:
        corrections = run_corrections(
            client, factory, rights=RightsType.CONVERTIBLE_OVERHANG, event_ids=ids, log=None
        )
        print("\n" + corrections.render())
        payload["corrections"] = {"events": corrections.events, "calls": corrections.calls}

    payload["spend"] = {
        "calls": client.call_count,
        "tokens": client.ledger.total_tokens,
        "cost_usd": round(client.ledger.cost_usd, 4),
    }
    print(
        f"\nspend      : {client.call_count} call(s), {client.ledger.total_tokens:,} token(s), "
        f"▷ ${client.ledger.cost_usd:.4f} estimated"
    )
    return payload


COMMANDS = {
    "calendar": cmd_calendar,
    "show": cmd_show,
    "documents": cmd_documents,
    "extract": cmd_extract,
}


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    payload = COMMANDS[args.command](args, _factory(args))
    if args.report:
        Path(args.report).write_text(
            json.dumps(payload, ensure_ascii=False, indent=1, default=str), encoding="utf-8"
        )
        print(f"report    : {args.report}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
