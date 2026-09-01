"""CLI for the scheduler — run the pipeline once, or read the beat schedule.

    # 1. the whole pipeline, synchronously, no broker involved
    .venv/bin/python -m mijual.scheduler once --window 14 --max-requests 300

    # 2. the same code path with $0 and 0 requests (cache only, prompts built
    #    but never sent) — the deterministic evidence run
    .venv/bin/python -m mijual.scheduler once --offline \
        --bgn 20260101 --end 20260331 --cache-dir scripts/spike/samples

    # 3. one stage
    .venv/bin/python -m mijual.scheduler once --stages gates

    # 4. the D-day mail, by hand (no broker, its own lock, a chosen anchor day)
    .venv/bin/python -m mijual.scheduler once --stages notify --no-lock \
        --label smoke-notify --notify-today 20260909

    # 5. what beat is configured to do (imports Celery; needs no broker)
    .venv/bin/python -m mijual.scheduler schedule

Exit codes: ``0`` ran, ``1`` a stage errored, ``3`` skipped because another run
holds the lock. Nothing here prints, writes or accepts a secret — ``mijual.config``
reads the keys in-process and they only ever reach a request URL or the SDK.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from mijual.scheduler.config import (
    DEFAULT_STAGES,
    DEFAULT_WINDOW_DAYS,
    NOTIFY_MAX_MAILS,
    RIGHTS_BY_ID,
    STAGES,
    PipelineConfig,
)
from mijual.scheduler.pipeline import run_pipeline


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="python -m mijual.scheduler", description=__doc__)
    sub = p.add_subparsers(dest="command", required=True)

    once = sub.add_parser("once", help="run the pipeline synchronously, no broker")
    once.add_argument("--window", type=int, default=DEFAULT_WINDOW_DAYS,
                      help=f"rolling discovery window in days (default: {DEFAULT_WINDOW_DAYS})")
    once.add_argument("--bgn", default=None, help="explicit window start, YYYYMMDD")
    once.add_argument("--end", default=None, help="explicit window end, YYYYMMDD")
    once.add_argument("--stages", nargs="+", default=list(DEFAULT_STAGES), choices=list(STAGES),
                      help="default: the six corpus stages. 'notify' (the D-day mail) is a "
                           "known stage but not a default one — it has its own 08:30 beat "
                           "entry and its own lock")
    once.add_argument("--offline", action="store_true",
                      help="cache only, prompts built but never sent (0 requests, 0 calls)")
    once.add_argument("--cache-dir", default=None, help="response cache (default: var/dart-cache)")
    once.add_argument("--database-url", default=None)
    once.add_argument("--redis-url", default=None, help="lock broker (default: Settings.redis_url)")
    once.add_argument("--max-requests", type=int, default=500,
                      help="collect stage's live OpenDART ceiling (O-1 guard)")
    once.add_argument("--bodydoc-max-requests", type=int, default=200,
                      help="본문 stage's live OpenDART ceiling")
    once.add_argument("--max-calls", type=int, default=60, help="LLM call ceiling for the run")
    once.add_argument("--rights", nargs="+", default=["R1", "R3"], choices=sorted(RIGHTS_BY_ID),
                      help="rights types the extraction stage reads (default: R1 R3)")
    once.add_argument("--no-corrections", action="store_true", help="skip §7 #10 정정 재추출")
    once.add_argument(
        "--notify-today",
        default=None,
        help="YYYYMMDD — anchor the notify stage's D-day arithmetic on this KST day "
        "instead of today (an inspection/demo knob; beat never sets it)",
    )
    once.add_argument(
        "--notify-max-mails",
        type=int,
        default=NOTIFY_MAX_MAILS,
        help=f"outward-mail ceiling for the notify stage (default: {NOTIFY_MAX_MAILS})",
    )
    once.add_argument("--no-lock", action="store_true", help="run without the overlap lock")
    once.add_argument("--lock-name", default="pipeline")
    once.add_argument("--label", default="cli")
    once.add_argument(
        "--trigger",
        default="manual",
        help="what fired this run, for the ops 최근 실행 표 (default: manual; beat "
        "entries carry 'beat')",
    )
    once.add_argument(
        "--no-run-log",
        action="store_true",
        help="do not write a pipeline_run row (an inspection run that must leave "
        "the operator's log untouched)",
    )
    once.add_argument("--report", default=None, help="also write the run's record as JSON here")
    once.add_argument("--quiet", action="store_true")

    sub.add_parser("schedule", help="print the beat schedule and the registered task names")
    return p


def _config(args) -> PipelineConfig:
    return PipelineConfig(
        window_days=args.window,
        bgn=args.bgn,
        end=args.end,
        stages=tuple(args.stages),
        offline=args.offline,
        cache_dir=args.cache_dir,
        database_url=args.database_url,
        redis_url=args.redis_url,
        collect_max_requests=args.max_requests,
        bodydoc_max_requests=args.bodydoc_max_requests,
        extract_max_calls=args.max_calls,
        extract_rights=tuple(RIGHTS_BY_ID[r] for r in args.rights),
        extract_corrections=not args.no_corrections,
        notify_today=args.notify_today,
        notify_max_mails=args.notify_max_mails,
        use_lock=not args.no_lock,
        lock_name=args.lock_name,
        label=args.label,
        trigger=args.trigger,
        write_run_log=not args.no_run_log,
    )


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "schedule":
        from mijual.scheduler.app import describe_schedule  # imports Celery

        print(describe_schedule())
        return 0

    result = run_pipeline(_config(args), log=None if args.quiet else print)
    print("\n" + result.render())
    if args.report:
        Path(args.report).write_text(
            json.dumps(result.as_dict(), ensure_ascii=False, indent=1, default=str),
            encoding="utf-8",
        )
        print(f"report    : {args.report}")
    if result.skipped:
        return 3
    return 0 if result.ok else 1


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
