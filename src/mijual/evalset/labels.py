"""Reading the labels back: forgiving about spelling, strict about meaning.

An unknown label is **refused, never guessed** — a silently dropped or
misinterpreted row would corrupt the one number this slice exists to produce. So
the import fails loudly, naming the ``row_id`` and the offending text, and writes
nothing until every row parses.

Forgiving where it costs nothing: case, surrounding whitespace, the obvious
one-letter forms and the Korean words a labeller will actually type all map onto
the four canonical labels. ``skip`` is one of them on purpose — a labeller who
cannot judge a row must have somewhere to say so, or they will guess, and a guess
enters the measurement as if it were a judgement. Skipped rows leave the
denominator (:mod:`mijual.evalset.report`) and are counted separately.

**Every written label file carries its judge.** ``evalset/labels.json`` is the
one artifact in this repository that cannot be regenerated from the corpus — a
judgement is not a computation — and *who* judged it changes what the resulting
accuracy number means (N89: the labels in this repo are Claude-judged
cross-model, **not** human ground truth). Prose beside the file does not travel
with it, so :class:`Provenance` travels *inside* it and :meth:`Labels.write`
**refuses to write an unstamped file**. The judge is never inherited or guessed:
a re-import states it again, because a human who re-judges a handful of rows
must not silently inherit a machine's stamp.
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from mijual.calc import KST
from mijual.evalset.sample import EVALSET_DIR, EvalSample

__all__ = [
    "LABEL_ALIASES",
    "LABEL_VALUES",
    "LABELS_PATH",
    "UNSTATED_BASIS",
    "LabelError",
    "Labels",
    "Provenance",
    "load_labels",
    "parse_label",
    "read_sheet_labels",
]

LABELS_PATH = EVALSET_DIR / "labels.json"

#: What ``basis`` says when the caller did not state one. Deliberately explicit
#: rather than empty: an unstated basis is a visible gap in the report, not a
#: blank the reader can mistake for "no caveats".
UNSTATED_BASIS = "기재되지 않음 (unstated)"

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


@dataclass(frozen=True)
class Provenance:
    """Who judged a label file, on what authority, and when it was imported."""

    judge: str
    basis: str = UNSTATED_BASIS
    imported_at: str = ""

    @classmethod
    def stamp(
        cls, judge: str, basis: str | None = None, *, at: str | None = None
    ) -> "Provenance":
        """Build a stamp for an import happening now. An empty judge is refused."""
        judge = (judge or "").strip()
        if not judge:
            raise LabelError(
                "provenance: --judged-by is empty — name the judge "
                "(who or what produced these labels)"
            )
        return cls(
            judge=judge,
            basis=(basis or "").strip() or UNSTATED_BASIS,
            # KST, offset-qualified: a stamp read beside a Korean disclosure date
            # must not need a mental timezone conversion to line up with it.
            imported_at=at
            or datetime.now(timezone.utc).astimezone(KST).isoformat(timespec="seconds"),
        )

    def as_dict(self) -> dict[str, str]:
        return {"judge": self.judge, "basis": self.basis, "imported_at": self.imported_at}

    @classmethod
    def from_payload(cls, payload: object, source: str) -> "Provenance | None":
        """Read the stored block. Absent → ``None``; malformed → refused."""
        if payload is None:
            return None
        if not isinstance(payload, dict) or not str(payload.get("judge", "")).strip():
            raise LabelError(
                f"{source}: `judged_by` is present but unreadable — it must be an object "
                "carrying a non-empty `judge`"
            )
        return cls(
            judge=str(payload["judge"]).strip(),
            basis=str(payload.get("basis") or UNSTATED_BASIS),
            imported_at=str(payload.get("imported_at") or ""),
        )


@dataclass
class Labels:
    """Validated labels, keyed by ``row_id``, with the judge that produced them."""

    source: str
    labelled: dict[str, str]
    corrections: dict[str, str]
    provenance: Provenance | None = None

    @property
    def judged(self) -> dict[str, str]:
        """Labels that count toward a rate (``skip`` is a non-judgement)."""
        return {k: v for k, v in self.labelled.items() if v != "skip"}

    def write(self, path: Path = LABELS_PATH) -> Path:
        """Write the file. Refuses to produce an unstamped artifact."""
        if self.provenance is None:
            raise LabelError(
                "refusing to write labels without provenance — an accuracy number "
                "whose judge is unrecorded cannot be read honestly (see N89)"
            )
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(
                {
                    "source": self.source,
                    "judged_by": self.provenance.as_dict(),
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
    """Read a label file. A file written before provenance existed still loads —
    with ``provenance is None``, which the report prints as a stated gap rather
    than passing off as a judgement of unknown origin."""
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return Labels(
        source=payload.get("source", str(path)),
        labelled=payload.get("labelled", {}),
        corrections=payload.get("corrections", {}),
        provenance=Provenance.from_payload(payload.get("judged_by"), str(path)),
    )


def read_sheet_labels(
    path: Path,
    sample: EvalSample | None = None,
    *,
    provenance: Provenance | None = None,
) -> Labels:
    """Parse a labelled sheet. Raises :class:`LabelError` on anything unexpected.

    Checked, in order: the sheet has the columns it must have; every ``row_id``
    is one the sample actually contains (a re-drawn sample would otherwise be
    scored against stale labels); no ``row_id`` appears twice; every non-empty
    label parses.

    ``provenance`` rides along untouched and is what makes the result writable —
    parsing a sheet says nothing about who judged it, so the caller must.
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
    return Labels(
        source=str(path),
        labelled=labelled,
        corrections=corrections,
        provenance=provenance,
    )
