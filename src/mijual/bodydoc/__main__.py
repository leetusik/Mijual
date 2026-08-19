"""CLI for the 본문 layer — parse, backfill, confirm.

    # 1. parse-only survey over every 본문 already on disk (0 requests, no key)
    .venv/bin/python -m mijual.bodydoc scan --offline --cache-dir scripts/spike/samples

    # 2. <CORRECTION> backfill: hint -> declared_original_dt + pairing verdict
    .venv/bin/python -m mijual.bodydoc backfill --max-requests 200

    # 3. the ① filter's final test: 본문 18. 신주인수권양도여부
    .venv/bin/python -m mijual.bodydoc warrants --max-requests 40

    # 4. read one document (debugging, and how O-5 was answered)
    .venv/bin/python -m mijual.bodydoc show 20260807000339 --offline

Nothing here prints, writes or accepts a secret: the key is read in-process by
``mijual.config`` and only ever reaches the live request URL.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, is_dataclass
from pathlib import Path

from mijual.bodydoc.backfill import backfill_corrections, confirm_warrants
from mijual.bodydoc.correction import parse_correction
from mijual.bodydoc.document import BodyDocument
from mijual.bodydoc.labels import TARGET_LABELS, extract_labels
from mijual.bodydoc.sections import sections
from mijual.config import load_settings
from mijual.dart import CacheMiss, DartClient, DartError
from mijual.db.models import Base
from mijual.db.schema_sync import ensure_columns
from mijual.db.session import create_all, make_engine, make_session_factory


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="python -m mijual.bodydoc", description=__doc__)
    p.add_argument("--offline", action="store_true", help="cache only; never fetch")
    p.add_argument("--cache-dir", default=None, help="response cache (default: var/dart-cache)")
    p.add_argument("--database-url", default=None)
    p.add_argument("--max-requests", type=int, default=None,
                   help="hard ceiling on live OpenDART requests (O-1 guard)")
    p.add_argument("--max-documents", type=int, default=None,
                   help="stop fetching new 본문 after this many")
    p.add_argument("--no-fetch", action="store_true", help="use only 본문 already held")
    p.add_argument("--report", default=None, help="also write the run's counts as JSON here")
    p.add_argument("--quiet", action="store_true")

    sub = p.add_subparsers(dest="command", required=True)

    scan = sub.add_parser("scan", help="parse every cached/held 본문 and report coverage")
    scan.add_argument("--from-db", action="store_true", help="scan stored snapshots, not the cache")
    scan.add_argument("--limit", type=int, default=None)

    back = sub.add_parser("backfill", help="<CORRECTION> hint -> pairing verdict")
    back.add_argument("--limit", type=int, default=None, help="cap the candidate list")
    back.add_argument("--priorities", nargs="+", type=int, default=[0, 1, 2, 3],
                      help="0 exposable, 1 ambiguous/flagged, 2 unpaired, 3 rest")

    war = sub.add_parser("warrants", help="① filter's final test: 본문 18. 신주인수권양도여부")
    war.add_argument("--include-suppressed", action="store_true")
    war.add_argument("--dry-run", action="store_true")

    show = sub.add_parser("show", help="parse one 본문 and print what the layer sees")
    show.add_argument("rcept_no")
    show.add_argument("--sections", action="store_true", help="list <TITLE> sections instead")
    return p


def _client(args) -> DartClient:
    return DartClient(
        settings=load_settings(),
        cache_dir=args.cache_dir,
        offline=args.offline,
        max_requests=args.max_requests,
    )


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


def _cmd_scan(args, client: DartClient) -> int:
    """Parse-only evidence run: coverage + span round-trip over real documents."""
    documents: list[tuple[str, bytes]] = []
    if args.from_db:
        from sqlalchemy import select

        from mijual.db.models import FilingVersion, Snapshot
        from mijual.db.session import session_scope

        with session_scope(_factory(args)) as session:
            for version, snapshot in session.execute(
                select(FilingVersion, Snapshot).join(
                    Snapshot, Snapshot.filing_version_id == FilingVersion.id
                ).where(Snapshot.source == "document")
            ):
                documents.append((version.rcept_no, snapshot.payload_bytes))
    else:
        for path in sorted((client.cache_dir / "document").glob("*.zip")):
            match = re.match(r"rcept-no-(\d{14})_", path.name)
            if match:
                documents.append((match.group(1), path.read_bytes()))
    if args.limit:
        documents = documents[: args.limit]

    by_form: dict[str, list] = {}
    span_checks = span_failures = 0
    for rcept_no, blob in documents:
        try:
            doc = BodyDocument.from_bytes(blob, rcept_no=rcept_no)
        except DartError:
            continue
        labels = extract_labels(doc) if not doc.is_registration_statement else None
        block = parse_correction(doc)
        if labels is not None:
            for row in labels.rows:
                if row.span is None:
                    continue
                span_checks += 1
                if not doc.verify(row.span, row.raw):
                    span_failures += 1
        by_form.setdefault(f"{doc.form_code} {doc.doc_name}", []).append(
            (
                rcept_no,
                labels.target_coverage if labels else None,
                block.present,
                block.declared_original_dt,
                len(block.items),
                len(sections(doc)) if doc.is_registration_statement else 0,
            )
        )

    print(f"documents  : {len(documents)}")
    for form, entries in sorted(by_form.items()):
        full = sum(1 for e in entries if e[1] and e[1][0] == len(TARGET_LABELS))
        with_block = sum(1 for e in entries if e[2])
        with_hint = sum(1 for e in entries if e[3])
        items = sum(e[4] for e in entries)
        print(
            f"  {form:<40} n={len(entries):>3} 10/10-labels={full:>3} "
            f"<CORRECTION>={with_block:>3} hint={with_hint:>3} 정정사항 rows={items}"
        )
    print(f"span check : {span_checks - span_failures}/{span_checks} values re-slice to themselves")
    return 1 if span_failures else 0


def _cmd_show(args, client: DartClient) -> int:
    try:
        blob = client.get_document(args.rcept_no)
    except CacheMiss:
        print(f"not cached: {args.rcept_no} (drop --offline to fetch)")
        return 2
    doc = BodyDocument.from_bytes(blob, rcept_no=args.rcept_no)
    print(f"{doc}  form={doc.form_code} registration_statement={doc.is_registration_statement}")

    if args.sections or doc.is_registration_statement:
        for section in sections(doc):
            print(f"  lvl={section.level} {len(section.span):>9,} chars  {section.title[:70]}")
        return 0

    block = parse_correction(doc)
    print(
        f"<CORRECTION>: present={block.present} target={block.target_report} "
        f"최초제출일={block.declared_original_dt} ({block.source}) items={len(block.items)}"
    )
    for item in block.items[:12]:
        print(f"   · {item.item[:40]:<42} {item.before[:40]!r} -> {item.after[:40]!r}")

    labels = extract_labels(doc)
    found, total = labels.target_coverage
    print(f"labels     : {found}/{total} of the §1.3 target set, {len(labels)} rows")
    for row in labels.rows:
        if row.field_key is None:
            continue
        ok = doc.verify(row.span, row.raw) if row.span else None
        qualifier = "/".join(row.qualifier)
        print(
            f"   {str(row.number):>4}. {row.label[:28]:<30} {qualifier[:22]:<24} "
            f"{row.kind:<8} {str(row.value)[:28]:<30} span={row.span} verify={ok}"
        )
    return 0


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    log = None if args.quiet else print
    client = _client(args)
    if log:
        log(f"cache dir : {client.cache_dir}{' (offline)' if args.offline else ''}")

    if args.command == "scan":
        return _cmd_scan(args, client)
    if args.command == "show":
        return _cmd_show(args, client)

    factory = _factory(args)
    if args.command == "backfill":
        report = backfill_corrections(
            client,
            factory,
            limit=args.limit,
            max_documents=args.max_documents,
            fetch=not args.no_fetch,
            priorities=tuple(args.priorities),
            log=log,
        )
    else:
        report = confirm_warrants(
            client,
            factory,
            fetch=not args.no_fetch,
            max_documents=args.max_documents,
            include_suppressed=args.include_suppressed,
            dry_run=args.dry_run,
            log=log,
        )
    print("\n" + report.render())
    _dump(report, args.report)
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
