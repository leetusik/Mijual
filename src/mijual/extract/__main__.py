"""CLI for the extraction layer — probe, run, corrections, show.

    # 0. one call: does the credential's preset thinking level actually apply?
    .venv/bin/python -m mijual.extract probe

    # 1. cost check before spending anything (no API call at all)
    .venv/bin/python -m mijual.extract run --rights R1 --dry-run

    # 2. ① fields 1-5 over the warrant_confirmed corpus, under a hard ceiling
    .venv/bin/python -m mijual.extract run --rights R1 --max-calls 40

    # 3. §7 #10 — 정정 재추출 + diff on the same corpus
    .venv/bin/python -m mijual.extract corrections --rights R1 --max-calls 60

    # 4. read back what was stored, spans included (0 calls)
    .venv/bin/python -m mijual.extract show 20260724000546

    # 5. re-derive what is deterministic in what is already stored (0 calls):
    #    spans from the stored quotes, 정정 해석 scores from the stored 정정사항 rows
    .venv/bin/python -m mijual.extract relocate
    .venv/bin/python -m mijual.extract --dry-run recheck   # measure, write nothing

``--max-calls`` is **on by default** (50): this is the slice that spends real
money, so an unbounded run has to be asked for explicitly. Nothing here prints,
writes or accepts a secret — ``mijual.config`` reads the key in-process and it
only ever reaches the SDK.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, is_dataclass
from pathlib import Path

from sqlalchemy import select

from mijual.config import load_settings
from mijual.db.models import Base, Extraction, ExtractionCall, FilingVersion, RightsType
from mijual.db.schema_sync import ensure_columns
from mijual.db.session import create_all, make_engine, make_session_factory, session_scope
from mijual.extract.client import DEFAULT_MODEL, GeminiClient
from mijual.extract.fields import FIELDS, SCHEMA_VERSION
from mijual.extract.runner import (
    recheck_corrections,
    relocate_spans,
    run_corrections,
    run_extraction,
)

RIGHTS = {
    "R1": RightsType.SUBSCRIPTION_WARRANT,
    "R2": RightsType.CONVERTIBLE_OVERHANG,
    "R3": RightsType.APPRAISAL_RIGHT,
}


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="python -m mijual.extract", description=__doc__)
    p.add_argument("--database-url", default=None)
    p.add_argument("--model", default=DEFAULT_MODEL)
    p.add_argument("--max-calls", type=int, default=50, help="hard ceiling on LLM calls (money)")
    p.add_argument("--dry-run", action="store_true", help="build prompts, call nothing")
    p.add_argument("--report", default=None, help="also write the run's counts as JSON here")
    p.add_argument("--quiet", action="store_true")

    sub = p.add_subparsers(dest="command", required=True)
    sub.add_parser("probe", help="one minimal call; prints usage metadata")
    sub.add_parser("fields", help="print the §7 registry (0 calls)")
    sub.add_parser("relocate", help="re-resolve every stored quote's span (0 calls)")
    sub.add_parser(
        "recheck",
        help="re-score every stored 정정 해석 against its 정정사항 rows (0 calls; "
        "the global --dry-run, before the subcommand, measures without writing)",
    )
    sub.add_parser("summary", help="what is stored and what it cost (0 calls)")

    run = sub.add_parser("run", help="extract the prose fields of one rights type")
    run.add_argument("--rights", choices=sorted(RIGHTS), default="R1")
    run.add_argument("--limit", type=int, default=None, help="cap the event list")
    run.add_argument("--refresh", action="store_true", help="re-extract already-stored fields")
    run.add_argument("--include-conflict", action="store_true",
                     help="also read the warrant_conflict event (flagged, never exposed)")

    cor = sub.add_parser("corrections", help="§7 #10 — 정정 재추출 + diff")
    cor.add_argument("--rights", choices=sorted(RIGHTS), default="R1")
    cor.add_argument("--limit", type=int, default=None)
    cor.add_argument("--refresh", action="store_true")
    cor.add_argument("--include-conflict", action="store_true")

    show = sub.add_parser("show", help="print stored extractions for one rcept_no")
    show.add_argument("rcept_no")
    show.add_argument("--json", action="store_true")
    return p


def _factory(args):
    engine = make_engine(args.database_url)
    create_all(engine)
    added = ensure_columns(engine, Base)
    if added and not args.quiet:
        print(f"schema    : added {added}")
    return make_session_factory(engine)


def _dump(report, path: str | None) -> None:
    if not path:
        return

    def plain(value):
        if hasattr(value, "most_common"):
            return dict(value)
        if isinstance(value, dict):
            return {k: plain(v) for k, v in value.items()}
        if is_dataclass(value) and not isinstance(value, type):
            return asdict(value)
        if isinstance(value, list):
            return [plain(v) for v in value]
        return value

    payload = {k: plain(v) for k, v in vars(report).items()}
    Path(path).write_text(
        json.dumps(payload, ensure_ascii=False, indent=1, default=str), encoding="utf-8"
    )
    print(f"report    : {path}")


def _cmd_fields() -> int:
    print(f"schema version: {SCHEMA_VERSION}")
    for spec in sorted(FIELDS.values(), key=lambda s: s.number):
        print(f"{spec.number:>2}. [{spec.rights}] {spec.key:<28} {spec.name}")
        print(f"     본문 위치: {spec.location}")
        print(f"     gate     : {spec.gate}")
    return 0


def _cmd_probe(args) -> int:
    client = GeminiClient(
        settings=load_settings(), model=args.model, max_calls=args.max_calls,
        dry_run=args.dry_run,
    )
    result = client.probe()
    print(f"model      : {result.model} (server: {result.model_version})")
    print(f"status     : {result.status} in {result.latency_ms} ms, {result.attempts} attempt(s)")
    print(f"payload    : {result.payload}")
    print(
        f"usage      : prompt={result.usage.prompt_tokens} thinking={result.usage.thoughts_tokens} "
        f"output={result.usage.output_tokens} total={result.usage.total_tokens}"
    )
    print(
        "thinking   : preset ACTIVE (no thinking config was sent)"
        if result.usage.thoughts_tokens
        else "thinking   : no thought tokens reported — the preset may be absent"
    )
    print(f"cost       : ▷ ${result.cost_usd:.6f} estimated")
    return 0 if result.ok else 1


def _cmd_summary(args) -> int:
    """Regenerate the run's numbers from the database, never from a saved file.

    ``P2.S1``'s review lesson (N8): a committed summary must come from the final
    state, not from the run that happened to be open when the prose was written.
    """
    from collections import Counter

    with session_scope(_factory(args)) as session:
        rows = session.scalars(select(Extraction)).all()
        calls = session.scalars(select(ExtractionCall)).all()

        print(f"extractions: {len(rows)} row(s) over "
              f"{len({r.filing_version_id for r in rows})} filing version(s), "
              f"{len({r.event_id for r in rows})} event(s)")
        header = (f"  {'field':<28}{'rows':>5}{'extract':>8}{'absent':>7}{'err':>5}"
                  f"{'span_ok':>8}{'unres':>6}{'verif':>6}")
        print(header)
        for key in sorted({r.field_key for r in rows}):
            group = [r for r in rows if r.field_key == key]
            counted = Counter(r.status for r in group)
            spans = Counter(r.span_status for r in group)
            print(
                f"  {key:<28}{len(group):>5}{counted['extracted']:>8}{counted['absent']:>7}"
                f"{counted['error']:>5}{spans['resolved']:>8}{spans['unresolved']:>6}"
                f"{sum(1 for r in group if r.span_verified):>6}"
            )
        methods = Counter(r.locate_method or "-" for r in rows if r.quote)
        print(f"  locate methods: {dict(sorted(methods.items()))}")

        corrections = [r for r in rows if r.field_key == "correction_interpretation"]
        if corrections:
            items = changes = unsupported = uncovered = moves = sub_ok = sub_all = 0
            for row in corrections:
                value = row.value or {}
                check = value.get("deterministic_check") or {}
                items += check.get("items", 0)
                changes += check.get("changes", 0)
                unsupported += check.get("unsupported", 0)
                uncovered += check.get("uncovered", 0)
                moves += len(value.get("field_moves") or [])
                for change in (value.get("interpretation") or {}).get("changes") or []:
                    sub_all += 1
                    sub_ok += int(change.get("span_status") == "resolved")
            print(
                f"corrections: {len(corrections)} interpretation(s) | 정정사항 rows {items} "
                f"(uncovered {uncovered}) | model changes {changes} (unsupported {unsupported}) "
                f"| prose value moves {moves} | change quotes located {sub_ok}/{sub_all}"
            )

        by_task = Counter(c.task for c in calls)
        tokens = sum(c.total_tokens or 0 for c in calls)
        cost = sum(c.cost_usd or 0.0 for c in calls)
        print(
            f"calls      : {len(calls)} stored {dict(sorted(by_task.items()))}, "
            f"{sum(1 for c in calls if c.status != 'ok')} not ok"
        )
        print(
            f"tokens     : prompt {sum(c.prompt_tokens or 0 for c in calls):,} + thinking "
            f"{sum(c.thoughts_tokens or 0 for c in calls):,} + output "
            f"{sum(c.output_tokens or 0 for c in calls):,} = {tokens:,}"
        )
        print(f"cost       : ▷ ${cost:.4f} estimated over stored calls (not billed)")
        models = Counter(f"{c.model}/{c.model_version}" for c in calls)
        print(f"model      : {dict(models)}")
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
            rows = session.scalars(
                select(Extraction).where(Extraction.filing_version_id == version.id)
            ).all()
            calls = session.scalars(
                select(ExtractionCall).where(ExtractionCall.filing_version_id == version.id)
            ).all()
            print(f"{version.rcept_no}  event={version.event_id}  {len(rows)} extraction(s), "
                  f"{len(calls)} call(s)")
            for row in sorted(rows, key=lambda r: r.field_key):
                if args.json:
                    print(json.dumps(
                        {
                            "field": row.field_key, "status": row.status, "value": row.value,
                            "quote": row.quote, "span": row.span, "span_status": row.span_status,
                            "locate_method": row.locate_method, "verified": row.span_verified,
                        },
                        ensure_ascii=False, indent=1, default=str,
                    ))
                    continue
                print(
                    f"  {row.field_key:<28} {row.status:<9} span={str(row.span):<16} "
                    f"{str(row.span_status):<10} {str(row.locate_method):<8} "
                    f"verified={row.span_verified}"
                )
                if row.value_summary:
                    print(f"      값: {row.value_summary}")
                if row.quote:
                    print(f"      인용: {row.quote[:110]}")
            for call in calls:
                print(
                    f"  call {call.task:<12} {call.status:<8} {call.input_scope} "
                    f"{call.input_chars} chars, tokens {call.total_tokens}, "
                    f"▷ ${call.cost_usd or 0:.4f}"
                )
    return 0


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    log = None if args.quiet else print

    if args.command == "fields":
        return _cmd_fields()
    if args.command == "probe":
        return _cmd_probe(args)
    if args.command == "show":
        return _cmd_show(args)
    if args.command == "summary":
        return _cmd_summary(args)
    if args.command == "relocate":
        report = relocate_spans(_factory(args), log=log)
        print("\n" + report.render())
        _dump(report, args.report)
        return 0
    if args.command == "recheck":
        report = recheck_corrections(_factory(args), write=not args.dry_run, log=log)
        print("\n" + report.render())
        _dump(report, args.report)
        return 0

    client = GeminiClient(
        settings=load_settings(),
        model=args.model,
        max_calls=args.max_calls,
        dry_run=args.dry_run,
        log=log,
    )
    factory = _factory(args)
    runner = run_extraction if args.command == "run" else run_corrections
    report = runner(
        client,
        factory,
        rights=RIGHTS[args.rights],
        include_conflict=args.include_conflict,
        limit=args.limit,
        refresh=args.refresh,
        log=log,
    )
    print("\n" + report.render())
    print(client.ledger.render())
    if args.dry_run:
        print(f"dry run    : {report.planned_chars:,} input chars would have been sent")
    _dump(report, args.report)
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
