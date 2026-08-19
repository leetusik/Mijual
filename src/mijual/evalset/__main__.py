"""CLI for the hand-labelled evalset — 0 OpenDART requests, 0 LLM calls.

    # 1. draw the sample from the corpus and write the operator's sheet
    .venv/bin/python -m mijual.evalset sample

    # 2. (operator labels evalset/sheet.csv — see evalset/LABELING.md)
    .venv/bin/python -m mijual.evalset status

    # 3. read the labels back; refuses anything it cannot parse
    .venv/bin/python -m mijual.evalset import

    # 4. the accuracy report (per-field precision, gate-block rate, over-blocking)
    .venv/bin/python -m mijual.evalset report

Only ``sample`` touches the database. ``import`` and ``report`` read
``evalset/sample.json`` + the sheet, so the report is regenerable long after the
corpus has moved on — which is the point: a label is only true about the reading
it was made on.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from mijual.db.models import Base
from mijual.db.schema_sync import ensure_columns
from mijual.db.session import create_all, make_engine, make_session_factory, session_scope
from mijual.evalset.labels import LABELS_PATH, LabelError, load_labels, read_sheet_labels
from mijual.evalset.report import build_report
from mijual.evalset.sample import (
    DEFAULT_BOOSTER,
    DEFAULT_QUOTAS,
    DEFAULT_SEED,
    SAMPLE_PATH,
    build_sample,
    load_sample,
)
from mijual.evalset.sheet import SHEET_PATH, SheetHasLabels, existing_label_count, write_sheet


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="python -m mijual.evalset", description=__doc__)
    p.add_argument("--sample", default=str(SAMPLE_PATH), help="frozen sample JSON")
    p.add_argument("--sheet", default=str(SHEET_PATH), help="the operator's CSV")
    p.add_argument("--labels", default=str(LABELS_PATH), help="validated labels JSON")

    sub = p.add_subparsers(dest="command", required=True)

    draw = sub.add_parser("sample", help="draw the sample from the corpus and write the sheet")
    draw.add_argument("--database-url", default=None)
    draw.add_argument("--seed", type=int, default=DEFAULT_SEED)
    draw.add_argument("--booster", type=int, default=DEFAULT_BOOSTER)
    for stratum, count in DEFAULT_QUOTAS.items():
        draw.add_argument(f"--{stratum.replace('_', '-')}", type=int, default=count)
    draw.add_argument("--force", action="store_true", help="overwrite a sheet that holds labels")
    draw.add_argument("--no-sheet", action="store_true", help="write only the JSON")

    sheet = sub.add_parser("sheet", help="rewrite the CSV from the frozen sample")
    sheet.add_argument("--force", action="store_true")

    sub.add_parser("status", help="how much of the sheet is labelled")

    imp = sub.add_parser("import", help="validate the labelled sheet into labels.json")
    imp.add_argument("csv", nargs="?", default=None)

    rep = sub.add_parser("report", help="per-field precision + gate-block rate")
    rep.add_argument("--out", default=None, help="also write the markdown here")
    return p


def _factory(args):
    engine = make_engine(args.database_url)
    create_all(engine)
    ensure_columns(engine, Base)
    return make_session_factory(engine)


def _cmd_sample(args) -> int:
    # Checked *before* anything is written: sample.json and sheet.csv must never
    # diverge, because a label is only meaningful against the sample it was made
    # on. A labelled sheet stops the whole command, not just half of it.
    labelled = 0 if args.no_sheet else existing_label_count(Path(args.sheet))
    if labelled and not args.force:
        print(
            f"sample     : REFUSED — {args.sheet} already holds {labelled} label(s). "
            "Import them first, or pass --force to discard them."
        )
        return 1

    quotas = {s: getattr(args, s) for s in DEFAULT_QUOTAS}
    with session_scope(_factory(args)) as session:
        sample = build_sample(session, quotas=quotas, booster=args.booster, seed=args.seed)
    path = sample.write(Path(args.sample))
    print(sample.render())
    print(f"sample     : {path}")
    if not args.no_sheet:
        try:
            sheet = write_sheet(sample, Path(args.sheet), force=True)
        except SheetHasLabels:  # pragma: no cover - guarded above
            return 1
        print(f"sheet      : {sheet}")
    return 0


def _cmd_sheet(args) -> int:
    sample = load_sample(Path(args.sample))
    try:
        path = write_sheet(sample, Path(args.sheet), force=args.force)
    except SheetHasLabels as exc:
        print(f"sheet      : NOT written — {exc}")
        return 1
    print(f"sheet      : {path} ({len(sample.rows)} row(s))")
    return 0


def _cmd_status(args) -> int:
    sample = load_sample(Path(args.sample))
    done = existing_label_count(Path(args.sheet))
    total = len(sample.rows)
    print(f"sheet      : {args.sheet}")
    print(f"labelled   : {done} / {total} row(s) ({done / total * 100:.0f}%)" if total else "empty")
    return 0


def _cmd_import(args) -> int:
    sample = load_sample(Path(args.sample))
    source = Path(args.csv or args.sheet)
    try:
        labels = read_sheet_labels(source, sample)
    except LabelError as exc:
        print(f"import     : REFUSED\n{exc}")
        return 1
    path = labels.write(Path(args.labels))
    judged = len(labels.judged)
    print(
        f"import     : {len(labels.labelled)} label(s) from {source} "
        f"({judged} judged, {len(labels.labelled) - judged} skip), "
        f"{len(labels.corrections)} corrected value(s) → {path}"
    )
    missing = len(sample.rows) - len(labels.labelled)
    if missing:
        print(f"             {missing} row(s) still unlabelled")
    return 0


def _cmd_report(args) -> int:
    sample = load_sample(Path(args.sample))
    labels = load_labels(Path(args.labels))
    report = build_report(sample, labels)
    text = report.render()
    print(text)
    if args.out:
        Path(args.out).write_text(text + "\n", encoding="utf-8")
        print(f"\nwritten    : {args.out}")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return {
        "sample": _cmd_sample,
        "sheet": _cmd_sheet,
        "status": _cmd_status,
        "import": _cmd_import,
        "report": _cmd_report,
    }[args.command](args)


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
