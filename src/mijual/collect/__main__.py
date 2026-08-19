"""CLI for one collection window — the entry point ``P2.S6`` will schedule.

    # offline, against the P1 response cache (no key, no network)
    .venv/bin/python -m mijual.collect --bgn 20260101 --end 20260818 \
        --offline --cache-dir scripts/spike/samples --detail-window 20260101 20260818

    # live, under an explicit request ceiling (O-1: daily quota unmeasured)
    .venv/bin/python -m mijual.collect --bgn 20260701 --end 20260819 --max-requests 200

Nothing here prints, writes or accepts a secret: the key is read in-process by
``mijual.config`` and only ever reaches the live request URL.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from mijual.collect.runner import collect_window
from mijual.collect.targets import DEFAULT_ENDPOINTS
from mijual.config import load_settings
from mijual.dart import DartClient
from mijual.db.session import create_all, make_engine, make_session_factory, reset_schema


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="python -m mijual.collect", description=__doc__)
    p.add_argument("--bgn", required=True, help="window start, YYYYMMDD")
    p.add_argument("--end", required=True, help="window end, YYYYMMDD (inclusive)")
    p.add_argument("--corp-cls", nargs="+", default=["Y", "K"],
                   help="Y KOSPI, K KOSDAQ, N KONEX, E 기타 (default: Y K)")
    p.add_argument("--endpoints", nargs="+", default=list(DEFAULT_ENDPOINTS),
                   help="detail endpoints to collect (default: piicDecsn cmpMgDecsn)")
    p.add_argument("--offline", action="store_true", help="cache only; never fetch")
    p.add_argument("--cache-dir", default=None, help="response cache (default: var/dart-cache)")
    p.add_argument("--database-url", default=None)
    p.add_argument("--detail-window", nargs=2, metavar=("BGN", "END"), default=None,
                   help="override the per-corp detail window (offline runs)")
    p.add_argument("--history-bgn", default=None,
                   help="how far back the corp-scoped pairing query reaches (default: 3y)")
    p.add_argument("--no-pair-history", action="store_true",
                   help="do not widen pairing with corp-scoped list.json queries")
    p.add_argument("--no-documents", action="store_true", help="skip 본문 ZIP snapshots")
    p.add_argument("--max-documents", type=int, default=None)
    p.add_argument("--documents-for-suppressed", action="store_true")
    p.add_argument("--max-requests", type=int, default=None,
                   help="hard ceiling on live OpenDART requests (O-1 guard)")
    p.add_argument("--reset", action="store_true", help="drop and recreate the schema first")
    p.add_argument("--dry-run", action="store_true", help="collect and report, persist nothing")
    p.add_argument("--report", default=None, help="also write the run's counts as JSON here")
    p.add_argument("--quiet", action="store_true")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    log = None if args.quiet else print

    settings = load_settings()
    client = DartClient(
        settings=settings,
        cache_dir=args.cache_dir,
        offline=args.offline,
        max_requests=args.max_requests,
    )
    if log:
        log(f"settings  : {settings}")  # masked — never prints a key
        log(f"cache dir : {client.cache_dir}{' (offline)' if args.offline else ''}")

    factory = None
    if not args.dry_run:
        engine = make_engine(args.database_url)
        reset_schema(engine) if args.reset else create_all(engine)
        factory = make_session_factory(engine)

    report = collect_window(
        client,
        factory,
        bgn_de=args.bgn,
        end_de=args.end,
        markets=tuple(args.corp_cls),
        endpoints=tuple(args.endpoints),
        detail_window=tuple(args.detail_window) if args.detail_window else None,
        history_bgn=args.history_bgn,
        pair_history=not args.no_pair_history,
        with_documents=not args.no_documents,
        max_documents=args.max_documents,
        documents_for_suppressed=args.documents_for_suppressed,
        dry_run=args.dry_run,
        log=log,
    )
    print("\n" + report.render())

    if args.report:
        # ``rows_by_kind`` is a Counter keyed by :class:`CorrectionKind`, and JSON
        # object keys must be strings — ``default=str`` only rescues *values*, so
        # the keys are stringified here. (Found by P2.S7's backfill: the run
        # itself had already persisted everything when the dump raised.)
        payload = {
            k: ({str(kk): vv for kk, vv in v.items()} if hasattr(v, "most_common") else v)
            for k, v in vars(report).items()
        }
        Path(args.report).write_text(
            json.dumps(payload, ensure_ascii=False, indent=1, default=str), encoding="utf-8"
        )
        print(f"report    : {args.report}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
