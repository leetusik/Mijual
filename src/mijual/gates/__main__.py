"""CLI for the gate layer — judge, then read back what may be shown.

    # 1. judge every stored extraction, persist the verdicts (0 calls, 0 requests)
    .venv/bin/python -m mijual.gates run

    # 2. the exposure contract, regenerated from the database
    .venv/bin/python -m mijual.gates summary

    # 3. one filing: every field, its verdict, and the checks behind it
    .venv/bin/python -m mijual.gates show 20260724000546

    # 4. the 철회 detector's own audit: what the word would have caught vs what
    #    the row shape actually accepts
    .venv/bin/python -m mijual.gates withdrawals

Nothing here calls an LLM, spends an OpenDART request, or reads a secret. Running
``run`` twice is a no-op on the second pass — every verdict is re-derived from
the same stored evidence.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from sqlalchemy import select

from mijual.db.models import Base, Event, Extraction, FilingVersion, RightsType
from mijual.db.schema_sync import ensure_columns
from mijual.db.session import create_all, make_engine, make_session_factory, session_scope
from mijual.gates.exposure import event_exposure, exposure_of_all
from mijual.gates.outcome import REASON_LABELS_KO
from mijual.gates.runner import exposure_summary, run_gates
from mijual.gates.withdrawal import is_withdrawal_row, scan_withdrawal_rows

RIGHTS = {
    "R1": RightsType.SUBSCRIPTION_WARRANT,
    "R2": RightsType.CONVERTIBLE_OVERHANG,
    "R3": RightsType.APPRAISAL_RIGHT,
}


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="python -m mijual.gates", description=__doc__)
    p.add_argument("--database-url", default=None)
    p.add_argument("--report", default=None, help="also write the run's counts as JSON here")
    p.add_argument("--quiet", action="store_true")

    sub = p.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run", help="judge every stored extraction and refresh exposure")
    run.add_argument("--rights", choices=sorted(RIGHTS), default=None)
    run.add_argument("--only-exposable", action="store_true",
                     help="skip suppressed events (default: judge every event)")

    summary = sub.add_parser("summary", help="the exposure contract, from the database")
    summary.add_argument("--include-suppressed", action="store_true")
    summary.add_argument("--events", action="store_true", help="list every event")

    show = sub.add_parser("show", help="one filing's verdicts and the checks behind them")
    show.add_argument("rcept_no")

    sub.add_parser("reasons", help="every reason code with its Korean rendering")
    sub.add_parser("withdrawals", help="the 철회 detector's audit over the corpus")
    return p


def _factory(args):
    engine = make_engine(args.database_url)
    create_all(engine)
    added = ensure_columns(engine, Base)
    if added and not args.quiet:
        print(f"schema    : added {added}")
    return make_session_factory(engine)


def _cmd_run(args) -> int:
    report = run_gates(
        _factory(args),
        rights=RIGHTS.get(args.rights) if args.rights else None,
        only_exposable=args.only_exposable,
        log=None if args.quiet else print,
    )
    print("\n" + report.render())
    if args.report:
        payload = {
            k: (dict(v) if hasattr(v, "most_common") else v)
            for k, v in vars(report).items()
        }
        payload["per_field"] = {k: dict(v) for k, v in report.per_field.items()}
        Path(args.report).write_text(
            json.dumps(payload, ensure_ascii=False, indent=1, default=str), encoding="utf-8"
        )
        print(f"report    : {args.report}")
    return 0


def _cmd_summary(args) -> int:
    with session_scope(_factory(args)) as session:
        print(exposure_summary(session, include_suppressed=args.include_suppressed))
        if args.events:
            print()
            for view in exposure_of_all(
                session, include_suppressed=args.include_suppressed
            ):
                print(view.render())
    return 0


def _cmd_show(args) -> int:
    with session_scope(_factory(args)) as session:
        versions = session.scalars(
            select(FilingVersion).where(FilingVersion.rcept_no == args.rcept_no)
        ).all()
        if not versions:
            print(f"no filing version stored for {args.rcept_no}")
            return 2
        for version in versions:
            event = session.get(Event, version.event_id)
            exposure = event_exposure(session, event)
            print(exposure.render())
            rows = session.scalars(
                select(Extraction).where(Extraction.filing_version_id == version.id)
            ).all()
            for row in sorted(rows, key=lambda r: r.field_key):
                print(f"  {row.field_key:<28} {str(row.gate_status):<14} {row.gate_reason_code or ''}")
                if row.gate_note:
                    print(f"      {row.gate_note}")
    return 0


def _cmd_reasons() -> int:
    for code, korean in sorted(REASON_LABELS_KO.items()):
        print(f"  {code:<34} {korean}")
    return 0


def _cmd_withdrawals(args) -> int:
    """Print every 철회-mentioning 정정사항 row and whether the shape rules take it."""
    accepted = rejected = 0
    with session_scope(_factory(args)) as session:
        for event in session.scalars(select(Event)).all():
            for version, item in scan_withdrawal_rows(session, event):
                verdict = is_withdrawal_row(item)
                accepted += int(verdict)
                rejected += int(not verdict)
                mark = "철회" if verdict else "  - "
                print(
                    f"  {mark} {event.rights_type.value} {event.corp.corp_name:<14} "
                    f"{version.rcept_no} | 항목 {' '.join(item.item.split())[:34]!r} "
                    f"→ {' '.join(item.after.split())[:34]!r}"
                )
    print(f"\n  rows mentioning 철회: {accepted + rejected} | withdrawals: {accepted} | "
          f"rejected as boilerplate: {rejected}")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "run":
        return _cmd_run(args)
    if args.command == "summary":
        return _cmd_summary(args)
    if args.command == "show":
        return _cmd_show(args)
    if args.command == "reasons":
        return _cmd_reasons()
    if args.command == "withdrawals":
        return _cmd_withdrawals(args)
    return 2  # pragma: no cover - argparse enforces the choice


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
