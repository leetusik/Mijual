"""CLI for the labelled evalset (judge recorded per round) — 0 OpenDART requests, 0 LLM calls.

    # 1. draw the sample from the corpus and write the operator's sheet
    .venv/bin/python -m mijual.evalset sample

    # 2. (operator labels evalset/sheet.csv — see evalset/LABELING.md)
    .venv/bin/python -m mijual.evalset status

    # 3. read the labels back; refuses anything it cannot parse, and refuses an
    #    import that does not say who judged the rows
    .venv/bin/python -m mijual.evalset import --judged-by "사람 (운영자)" \\
        --basis "직접 판정 2026-08-21"

    # 4. the accuracy report (per-field precision, gate-block rate, over-blocking)
    .venv/bin/python -m mijual.evalset report

    # 5. re-freeze only the label-free 정정 recall proxy after the stored records
    #    were re-scored deterministically (`python -m mijual.extract recheck`)
    .venv/bin/python -m mijual.evalset refresh-recall

Only ``sample`` and ``refresh-recall`` touch the database. ``import`` and ``report`` read
``evalset/sample.json`` + the sheet, so the report is regenerable long after the
corpus has moved on — which is the point: a label is only true about the reading
it was made on.

``--judged-by`` is required and is never inherited from the previous file: the
judge is part of the number (N89), and a human re-judging a few rows must not
silently keep a machine's stamp.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from mijual.db.models import Base
from mijual.db.schema_sync import ensure_columns
from mijual.db.session import create_all, make_engine, make_session_factory, session_scope
from mijual.evalset.labels import (
    LABELS_PATH,
    LabelError,
    Provenance,
    load_labels,
    read_sheet_labels,
)
from mijual.evalset.report import build_report
from mijual.evalset.sample import (
    DEFAULT_BOOSTER,
    DEFAULT_QUOTAS,
    DEFAULT_SEED,
    SAMPLE_PATH,
    build_sample,
    correction_recall,
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
    imp.add_argument(
        "--judged-by",
        required=True,
        help="who or what judged these rows (recorded into labels.json; required)",
    )
    imp.add_argument(
        "--basis",
        default=None,
        help="on what authority, and with what caveat (e.g. 'operator directive … — "
        "not human ground truth')",
    )

    rep = sub.add_parser("report", help="per-field precision + gate-block rate")
    rep.add_argument("--out", default=None, help="also write the markdown here")

    fresh = sub.add_parser(
        "refresh-recall",
        help="re-freeze only the label-free 정정 recall proxy in the frozen sample",
    )
    fresh.add_argument("--database-url", default=None)
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
        provenance = Provenance.stamp(args.judged_by, args.basis)
        labels = read_sheet_labels(source, sample, provenance=provenance)
        path = labels.write(Path(args.labels))
    except LabelError as exc:
        print(f"import     : REFUSED\n{exc}")
        return 1
    judged = len(labels.judged)
    print(
        f"import     : {len(labels.labelled)} label(s) from {source} "
        f"({judged} judged, {len(labels.labelled) - judged} skip), "
        f"{len(labels.corrections)} corrected value(s) → {path}"
    )
    print(f"judged by  : {provenance.judge}")
    print(f"basis      : {provenance.basis} (기록 {provenance.imported_at})")
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


def _cmd_refresh_recall(args) -> int:
    """Re-freeze the one figure in the sample that no label feeds.

    The 정정 recall proxy is **derived** from the stored records, not from the
    draw and not from a label (the report even prints it under *라벨 불필요*), so
    when those records are re-scored — ``python -m mijual.extract recheck``, after
    the N92 matcher fix — the frozen copy is simply stale arithmetic and the
    report goes on printing a number the repo knows is wrong.

    This rewrites **that block and nothing else**: the drawn ``rows``, the seed,
    the strata, the per-field corpus stats and ``generated_at`` are untouched, so
    every ``row_id`` a label was made against still means the same reading and
    ``labels.json`` is never opened. Redrawing the sample (``sample``) is the
    thing that would break that, which is why this is a separate command.
    """
    path = Path(args.sample)
    sample = load_sample(path)
    before = dict(sample.correction_recall)
    with session_scope(_factory(args)) as session:
        after = correction_recall(session)

    def line(block: dict) -> str:
        recall = block.get("recall")
        return (
            f"{block.get('deterministic_rows')} row(s), uncovered {block.get('uncovered')}, "
            f"unsupported {block.get('unsupported')}/{block.get('model_changes')} → 재현율 "
            + ("—" if recall is None else f"{recall * 100:.2f}%")
            + f" ({block.get('records')} 건)"
        )

    print(f"stored     : {line(before)}")
    print(f"corpus     : {line(after)}")
    if before == after:
        print("sample     : unchanged — nothing written")
        return 0
    sample.correction_recall = after
    sample.write(path)
    print(f"sample     : {path} — correction_recall re-frozen "
          f"({len(sample.rows)} row(s) and every label key untouched)")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return {
        "sample": _cmd_sample,
        "sheet": _cmd_sheet,
        "status": _cmd_status,
        "import": _cmd_import,
        "report": _cmd_report,
        "refresh-recall": _cmd_refresh_recall,
    }[args.command](args)


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
