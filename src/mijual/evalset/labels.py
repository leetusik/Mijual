"""Reading the operator's labels back: forgiving about spelling, strict about meaning.

An unknown label is **refused, never guessed** — a silently dropped or
misinterpreted row would corrupt the one number this slice exists to produce. So
the import fails loudly, naming the ``row_id`` and the offending text, and writes
nothing until every row parses.

Forgiving where it costs nothing: case, surrounding whitespace, the obvious
one-letter forms and the Korean words an operator will actually type all map onto
the four canonical labels. ``skip`` is one of them on purpose — an operator who
cannot judge a row must have somewhere to say so, or they will guess, and a guess
enters the measurement as if it were a judgement. Skipped rows leave the
denominator (:mod:`mijual.evalset.report`) and are counted separately.
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path

from mijual.evalset.sample import EVALSET_DIR, EvalSample

__all__ = [
    "LABEL_ALIASES",
    "LABEL_VALUES",
    "LABELS_PATH",
    "LabelError",
    "Labels",
    "load_labels",
    "parse_label",
    "read_sheet_labels",
]

LABELS_PATH = EVALSET_DIR / "labels.json"

#: The four canonical labels. ``partial`` = the value is partly right (one entry
#: of several wrong, a date right and an agent wrong, a rounded ratio…).
LABEL_VALUES = ("correct", "wrong", "partial", "skip")

LABEL_ALIASES: dict[str, str] = {
    **{v: v for v in LABEL_VALUES},
    "c": "correct", "o": "correct", "y": "correct", "맞음": "correct", "정확": "correct",
    "w": "wrong", "x": "wrong", "n": "wrong", "틀림": "wrong", "오류": "wrong",
    "p": "partial", "부분": "partial", "일부": "partial",
    "s": "skip", "?": "skip", "모름": "skip", "판단불가": "skip",
}


class LabelError(ValueError):
    """A label file that cannot be trusted — reported, never worked around."""


def parse_label(text: str | None) -> str | None:
    """``'  O '`` → ``'correct'``; empty → ``None``; anything else raises."""
    cleaned = (text or "").strip().lower()
    if not cleaned:
        return None
    try:
        return LABEL_ALIASES[cleaned]
    except KeyError:
        raise LabelError(
            f"unknown label {text!r} — use one of {', '.join(LABEL_VALUES)}"
        ) from None


@dataclass
class Labels:
    """Validated labels, keyed by ``row_id``."""

    source: str
    labelled: dict[str, str]
    corrections: dict[str, str]

    @property
    def judged(self) -> dict[str, str]:
        """Labels that count toward a rate (``skip`` is a non-judgement)."""
        return {k: v for k, v in self.labelled.items() if v != "skip"}

    def write(self, path: Path = LABELS_PATH) -> Path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(
                {
                    "source": self.source,
                    "labelled": self.labelled,
                    "corrections": self.corrections,
                },
                ensure_ascii=False,
                indent=1,
                sort_keys=True,
            ),
            encoding="utf-8",
        )
        return path


def load_labels(path: Path = LABELS_PATH) -> Labels:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return Labels(
        source=payload.get("source", str(path)),
        labelled=payload.get("labelled", {}),
        corrections=payload.get("corrections", {}),
    )


def read_sheet_labels(path: Path, sample: EvalSample | None = None) -> Labels:
    """Parse a labelled sheet. Raises :class:`LabelError` on anything unexpected.

    Checked, in order: the sheet has the columns it must have; every ``row_id``
    is one the sample actually contains (a re-drawn sample would otherwise be
    scored against stale labels); no ``row_id`` appears twice; every non-empty
    label parses.
    """
    path = Path(path)
    known = {row.row_id for row in sample.rows} if sample is not None else None
    labelled: dict[str, str] = {}
    corrections: dict[str, str] = {}
    problems: list[str] = []

    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        missing = {"row_id", "label"} - set(reader.fieldnames or [])
        if missing:
            raise LabelError(f"{path}: missing column(s) {sorted(missing)}")
        for line, row in enumerate(reader, start=2):
            row_id = (row.get("row_id") or "").strip()
            if not row_id:
                continue
            if known is not None and row_id not in known:
                problems.append(f"line {line}: {row_id} is not in the sample")
                continue
            if row_id in labelled or row_id in corrections:
                problems.append(f"line {line}: {row_id} appears twice")
                continue
            try:
                label = parse_label(row.get("label"))
            except LabelError as exc:
                problems.append(f"line {line} ({row_id}): {exc}")
                continue
            if label is not None:
                labelled[row_id] = label
            corrected = (row.get("corrected_value") or "").strip()
            if corrected:
                corrections[row_id] = corrected

    if problems:
        raise LabelError(
            f"{path}: {len(problems)} problem(s), nothing imported\n  "
            + "\n  ".join(problems[:20])
        )
    return Labels(source=str(path), labelled=labelled, corrections=corrections)
