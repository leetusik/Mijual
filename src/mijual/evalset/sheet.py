"""The labelling sheet: one CSV the operator edits, and nothing else to install.

Three choices are about the operator's hands, not about the data:

* ``label`` and ``corrected_value`` are columns **A and B**, so the whole pass is
  typing down two columns with the evidence to the right — no horizontal
  scrolling, no hunting for the input cell.
* the file is written **UTF-8 with a BOM**, because Excel on macOS reads Korean
  as mojibake without one, and a sheet the operator cannot read is a sheet that
  does not get labelled.
* only ``row_id``, ``label`` and ``corrected_value`` are ever read back
  (:mod:`mijual.evalset.labels`). Every other column is evidence for the human,
  so a spreadsheet that helpfully rewrites ``20260805000454`` as
  ``2.02608E+13`` costs nothing — ``row_id`` is not numeric on purpose.

Refusing to clobber labelled work is part of the contract: re-running the
sampler must never silently destroy an hour of the operator's time, so
:func:`write_sheet` stops if the existing sheet already carries labels.
"""

from __future__ import annotations

import csv
from pathlib import Path

from mijual.evalset.sample import EVALSET_DIR, EvalSample

__all__ = ["SHEET_COLUMNS", "SHEET_PATH", "existing_label_count", "write_sheet"]

SHEET_PATH = EVALSET_DIR / "sheet.csv"

SHEET_COLUMNS = [
    "label",            # ← the operator types here
    "corrected_value",  # ← and, optionally, here
    "row_id",
    "corp_name",
    "rcept_no",
    "field",
    "extracted_value",
    "quote",
    "context",
    "gate",
    "gate_reason",
    "pick",
    "stratum",
    "dart_url",
]


class SheetHasLabels(RuntimeError):
    """The sheet on disk already carries operator work."""


def existing_label_count(path: Path = SHEET_PATH) -> int:
    """How many labels the sheet on disk already holds (0 if there is none)."""
    path = Path(path)
    if not path.exists():
        return 0
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return sum(1 for row in csv.DictReader(handle) if (row.get("label") or "").strip())


def write_sheet(sample: EvalSample, path: Path = SHEET_PATH, *, force: bool = False) -> Path:
    """Write the sheet. Refuses to overwrite labelled work unless ``force``."""
    path = Path(path)
    labelled = existing_label_count(path)
    if labelled and not force:
        raise SheetHasLabels(
            f"{path} already holds {labelled} label(s) — refusing to overwrite. "
            "Import them first, or pass --force to discard them."
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=SHEET_COLUMNS)
        writer.writeheader()
        for row in sample.rows:
            writer.writerow(
                {
                    "label": "",
                    "corrected_value": "",
                    "row_id": row.row_id,
                    "corp_name": row.corp_name,
                    "rcept_no": row.rcept_no,
                    "field": row.field_ko,
                    "extracted_value": row.extracted_value,
                    "quote": row.quote,
                    "context": row.context,
                    "gate": row.gate_status,
                    "gate_reason": (
                        f"{row.gate_reason_code} — {row.gate_reason_ko}"
                        if row.gate_reason_code
                        else ""
                    ),
                    "pick": row.pick,
                    "stratum": row.stratum,
                    "dart_url": row.dart_url,
                }
            )
    return path
