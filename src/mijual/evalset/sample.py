"""The sample: deterministic, stratified, and frozen once written.

Determinism is a requirement, not a nicety — the report has to be regenerable
against exactly the rows the operator judged, and a re-drawn sample would quietly
invalidate every label. So the draw is a seeded shuffle over a **sorted** pool
(:data:`DEFAULT_SEED`, no clock, no ``id()``, no set iteration order), the seed is
per stratum (``f"{seed}:{stratum}"``) so re-tuning one quota cannot reshuffle
another stratum, and the whole result — every value, quote, context snippet and
gate verdict — is persisted to ``evalset/sample.json``.

The sampling **unit is a filing** (``kind:rcept_no``), not a field row: one
filing's fields are judged together because the operator pays the reading cost
once per document. Rows are then materialised from the selected filings.

Three picks, and the difference matters to the arithmetic:

``forced``
    a known hard case (:func:`hard_case`) — 철회, 추후결정, an unresolved citation
    span, a failed gate, a 실권주 cell that disagrees with its own Ⅶ tables, the
    REIT 실적보고서 form. Deliberately over-sampled; **excluded from the headline
    precision** and reported case by case instead.
``random``
    the seeded stratified draw. The only rows a precision estimate is computed
    from.
``booster``
    extra 정정 해석 rows, drawn at random from filings not already selected and
    contributing **only** their ``correction_interpretation`` row. Field 10 is
    otherwise the thinnest field in the corpus (N82); boosting it this way leaves
    every other field's sample untouched and still random.

One corpus quirk is handled here rather than in the sheet: ~28 % of ``rcept_no``
sit under two event keys (N21's residue, N81), so the same reading can be stored
twice. Duplicates are collapsed to one row — preferring the exposable event, then
the lowest id — because the evalset measures a *reading*, not a storage residue.
"""

from __future__ import annotations

import json
import random
import re
from collections import Counter
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Sequence

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from mijual.bodydoc import BodyDocument, Span, normalize
from mijual.config import ROOT
from mijual.db.models import Corp, Event, Extraction, FilingVersion, PerformanceReport, Snapshot
from mijual.extract.fields import FIELDS
from mijual.extract.store import summarize_value
from mijual.gates.outcome import REASON_LABELS_KO

__all__ = [
    "CORRECTION_FIELD",
    "DEFAULT_BOOSTER",
    "DEFAULT_QUOTAS",
    "DEFAULT_SEED",
    "EvalSample",
    "PERF_FIGURES",
    "Row",
    "SAMPLE_PATH",
    "build_sample",
    "collect_rows",
    "correction_recall",
    "hard_case",
    "load_sample",
    "select_sample",
]

#: Fixed seed. The judging date, so it reads as a decision rather than a nonce.
DEFAULT_SEED = 20260907

#: Committed evidence, not a run artifact: the labels are hand-made and are the
#: one thing in this repo that cannot be regenerated.
EVALSET_DIR = ROOT / "evalset"
SAMPLE_PATH = EVALSET_DIR / "sample.json"

CORRECTION_FIELD = "correction_interpretation"

#: How many filings each stratum draws **at random** (forced hard cases are added
#: on top, so the sample is ``forced + Σ quotas + booster`` filings). Sized to the
#: operator-time budget in ``evalset/LABELING.md``, not to the corpus.
DEFAULT_QUOTAS: dict[str, int] = {
    "R1_prose": 22,
    "R2_prose": 17,
    "R3_prose": 14,
    "perf": 12,
}
#: Extra 정정-해석-only filings (see the module docstring).
DEFAULT_BOOSTER = 12

#: The four 증권발행실적보고서 figures the 소멸 headline is built from (N67/N68),
#: in the order they appear in the document. The other parsed facts are kept in
#: the database; these are the ones whose column match decides a number.
PERF_FIGURES: tuple[str, ...] = (
    "warrants_issued",
    "warrants_exercised",
    "excess_subscribed",
    "lapse_stated",
)

#: Sheet ordering: ① first (the killer type), the deterministic table read last.
STRATUM_ORDER = {"R1_prose": 0, "R2_prose": 1, "R3_prose": 2, "perf": 3}

_RIGHTS_STRATUM = {"R1": "R1_prose", "R2": "R2_prose", "R3": "R3_prose"}

#: How much normalized text to show on each side of the cited span.
CONTEXT_CHARS = 120
#: Raw window flattened to produce it — markup inflates raw length several-fold.
_RAW_WINDOW = 1500

DART_VIEWER = "https://dart.fss.or.kr/dsaf001/main.do?rcpNo="


@dataclass(frozen=True)
class Row:
    """One candidate (filing, field) the operator may be asked to judge.

    Everything the sheet and the report need is captured here at sampling time.
    A row never re-reads the database afterwards: the corpus moves (N55/N83) and
    a label is only true about the reading it was made on.
    """

    unit: str
    kind: str
    stratum: str
    rights: str
    corp_code: str
    corp_name: str
    rcept_no: str
    field_key: str
    field_ko: str
    field_order: int
    extracted_value: str
    quote: str
    context: str
    gate_status: str
    gate_reason_code: str
    gate_reason_ko: str
    span_status: str
    is_current: bool
    hard_case: str
    source_id: int
    #: Filled by :func:`select_sample`.
    pick: str = ""
    row_id: str = ""

    @property
    def gate_blocked(self) -> bool:
        """Would the product withhold this field?

        Only ``passed`` and ``tbd`` are exposed (``mijual.gates.outcome``).
        ``deterministic`` is the 실적보고서's non-verdict: those figures pass
        through no §7 gate because no LLM read them — they are shown, so they are
        counted with the shown rows.
        """
        return self.gate_status not in ("passed", "tbd", "deterministic")

    @property
    def dart_url(self) -> str:
        return f"{DART_VIEWER}{self.rcept_no}"


@dataclass
class EvalSample:
    """The frozen sample plus the corpus statistics the report quotes."""

    seed: int
    generated_at: str
    quotas: dict[str, int]
    booster: int
    corpus: dict
    strata: dict
    field_stats: dict
    correction_recall: dict
    duplicates_collapsed: int
    rows: list[Row] = field(default_factory=list)

    @property
    def units(self) -> int:
        return len({r.unit for r in self.rows})

    def to_json(self) -> dict:
        payload = {k: v for k, v in self.__dict__.items() if k != "rows"}
        payload["rows"] = [asdict(r) for r in self.rows]
        return payload

    def write(self, path: Path = SAMPLE_PATH) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(self.to_json(), ensure_ascii=False, indent=1), encoding="utf-8"
        )
        return path

    def render(self) -> str:
        lines = [
            f"sample     : {self.units} filing(s), {len(self.rows)} row(s), seed {self.seed}",
            f"  picks    : {dict(sorted(Counter(r.pick for r in self.rows).items()))}",
            "  strata   :",
        ]
        for name in sorted(self.strata, key=lambda s: STRATUM_ORDER.get(s, 9)):
            s = self.strata[name]
            lines.append(
                f"    {name:<10} {s['units_selected']:>3} of {s['units_available']:>3} filing(s)"
                f" → {s['rows']:>3} row(s)"
            )
        lines.append("  per field (sampled / corpus):")
        counts = Counter(r.field_key for r in self.rows)
        for key in sorted(counts, key=lambda k: (self.field_stats.get(k, {}).get("order", 99), k)):
            corpus = self.field_stats.get(key, {}).get("total", 0)
            blocked = self.field_stats.get(key, {}).get("blocked", 0)
            lines.append(
                f"    {key:<28}{counts[key]:>4} / {corpus:<5} corpus gate-blocked {blocked}"
            )
        hard = [r for r in self.rows if r.hard_case]
        lines.append(f"  hard cases: {len(hard)} row(s) — {dict(sorted(Counter(r.hard_case for r in hard).items()))}")
        lines.append(f"  duplicates collapsed: {self.duplicates_collapsed}")
        return "\n".join(lines)


def load_sample(path: Path = SAMPLE_PATH) -> EvalSample:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    rows = [Row(**r) for r in payload.pop("rows", [])]
    return EvalSample(rows=rows, **payload)


# ---------------------------------------------------------------------------
# hard cases — the rows an evalset exists for
# ---------------------------------------------------------------------------
def hard_case(row: Extraction, event: Event) -> str:
    """Name the known-difficult thing about this extraction row, or ``""``.

    Purposive, and the report keeps it separate from the random draw for exactly
    that reason. Each name points at a phase finding: ``span_unresolved`` N37/N76,
    ``tbd`` N40, ``withdrawn`` N39/N47/N83, ``warrant_conflict`` N30/O-8,
    ``gate_failed`` the five §7 gates that fire on this corpus.
    """
    if row.span_status == "unresolved":
        return "span_unresolved"
    if row.gate_status == "failed":
        return f"gate_failed:{row.gate_reason_code}"
    if row.gate_status == "tbd":
        return "tbd_추후결정"
    if event.exposure_state == "withdrawn":
        return "withdrawn_철회"
    if "warrant_conflict" in event.flags:
        return "warrant_conflict"
    return ""


def _perf_hard_case(report: PerformanceReport, key: str, facts: dict) -> str:
    """N68: the filer's own 실권주 cell disagrees with its Ⅶ tables in 5 of 31."""
    if report.form == "reit":
        return "reit_form"
    stated = (facts.get("lapse_stated") or {}).get("value")
    derived = facts.get("lapse_derived")
    if key == "lapse_stated" and stated is not None and derived is not None:
        if int(stated) != int(derived):
            return "lapse_mismatch"
    return ""


# ---------------------------------------------------------------------------
# reading the corpus
# ---------------------------------------------------------------------------
#: Shown instead of a snippet when there is no span to centre one on — an
#: unresolved citation (N37) or a field the model reported absent. Those are
#: precisely the rows where the operator must open the original filing, so the
#: cell says so rather than sitting empty and looking like a bug.
NO_CONTEXT = "(원문 위치 없음 — dart_url을 열어 직접 확인해 주세요)"


def _trim_partial_tags(fragment: str, *, leading: bool) -> str:
    """Drop a half tag at the cut edge, which ``normalize`` cannot strip.

    A fixed-width raw window routinely starts or ends inside ``<TD WIDTH="…">``;
    without this the snippet shows the operator ``LE" HEIGHT="23">`` instead of
    Korean.
    """
    if leading:
        lt, gt = fragment.find("<"), fragment.find(">")
        if gt != -1 and (lt == -1 or gt < lt):
            return fragment[gt + 1 :]
        return fragment
    lt, gt = fragment.rfind("<"), fragment.rfind(">")
    return fragment[:lt] if lt != -1 and lt > gt else fragment


#: A 증권신고서 is millions of chars and must never be flattened whole (N33).
_FLATTEN_LIMIT = 400_000


def _fallback_context(doc: BodyDocument | None, anchor: str | None) -> str:
    """No span — so show the field's own anchor region, or say it is not there.

    The rows without a span are exactly the two the operator must think hardest
    about: a quote that failed to locate (N37) and a field the model called
    absent. Leaving the cell empty would push both onto a DART round trip; the
    anchor region makes most of them judgeable in place, and *not finding* the
    anchor is itself evidence that an ``absent`` verdict was right (N28: an
    absent label is a negative, not a gap).
    """
    if doc is None or not anchor or len(doc.text) > _FLATTEN_LIMIT:
        return NO_CONTEXT
    match = re.search(anchor, doc.flat.text)
    if match is None:
        return f"(본문 전체에서 '{anchor}' 표현을 찾지 못함 — 부재 판단의 방증)"
    lo = max(0, match.start() - CONTEXT_CHARS)
    hi = min(len(doc.flat.text), match.end() + CONTEXT_CHARS)
    return f"(인용 스팬 없음 · 항목 추정 위치) …{doc.flat.text[lo:hi]}…"


def _context(doc: BodyDocument | None, span: tuple[int, int] | None) -> str:
    """±120 normalized chars around the cited span, with the citation marked."""
    if doc is None or span is None:
        return NO_CONTEXT
    start, end = span
    before = _trim_partial_tags(doc.text[max(0, start - _RAW_WINDOW) : start], leading=True)
    after = _trim_partial_tags(doc.text[end : end + _RAW_WINDOW], leading=False)
    cited = doc.value_at(Span(start, end))
    return (
        f"…{normalize(before)[-CONTEXT_CHARS:]} 【{cited}】 "
        f"{normalize(after)[:CONTEXT_CHARS]}…"
    )


def _squash(text: str | None) -> str:
    return " ".join((text or "").split())


def _rendered_value(row: Extraction) -> str:
    """The value cell — and never a blank one, because blank reads as a bug.

    Two states render as text rather than as emptiness: a field the model
    reported **absent**, and N40's ``추후결정`` — a real extraction whose
    sub-fields are all ``null`` because the filing suspended the schedule. Both
    are judgements the operator must judge; an empty cell would hide them.
    """
    rendered = _squash(summarize_value(row.value, limit=900))
    if rendered:
        return rendered
    if row.status == "absent":
        return "(이 문서에 없다고 판단)"
    return "(추출은 됐으나 하위 항목이 모두 null — 값 없음)"


def _doc_for_snapshot(
    session: Session, snapshot_id: int | None, cache: dict[int, BodyDocument | None]
) -> BodyDocument | None:
    if snapshot_id is None:
        return None
    if snapshot_id not in cache:
        snap = session.get(Snapshot, snapshot_id)
        doc = None
        if snap is not None and snap.payload_bytes:
            try:
                doc = BodyDocument.from_bytes(snap.payload_bytes)
            except Exception:  # noqa: BLE001 - a bad body must not stop the sampler
                doc = None
        cache[snapshot_id] = doc
    return cache[snapshot_id]


def collect_rows(session: Session) -> tuple[list[Row], int]:
    """Every eval-eligible row in the corpus, deduplicated. Zero requests."""
    rows: list[Row] = []
    rows += _extraction_rows(session)
    deduped, collapsed = _dedupe(rows)
    return deduped + _perf_rows(session), collapsed


def _extraction_rows(session: Session) -> list[Row]:
    records = session.execute(
        select(Extraction, FilingVersion, Event, Corp)
        .join(FilingVersion, Extraction.filing_version_id == FilingVersion.id)
        .join(Event, Extraction.event_id == Event.id)
        .join(Corp, Event.corp_code == Corp.corp_code)
    ).all()
    cache: dict[int, BodyDocument | None] = {}
    out: list[Row] = []
    for row, version, event, corp in records:
        spec = FIELDS.get(row.field_key)
        if spec is None:  # pragma: no cover - the registry is a closed list
            continue
        stratum = _RIGHTS_STRATUM[event.rights_type.value]
        doc = _doc_for_snapshot(session, row.snapshot_id, cache)
        latest = event.latest_version
        out.append(
            Row(
                unit=f"extraction:{version.rcept_no}",
                kind="extraction",
                stratum=stratum,
                rights=event.rights_type.value,
                corp_code=corp.corp_code,
                corp_name=corp.corp_name or corp.corp_code,
                rcept_no=version.rcept_no,
                field_key=row.field_key,
                field_ko=f"#{spec.number} {spec.name}",
                field_order=spec.number,
                extracted_value=_rendered_value(row),
                quote=_squash(row.quote),
                context=(
                    _context(doc, row.span)
                    if row.span is not None
                    else _fallback_context(doc, spec.anchor)
                ),
                gate_status=row.gate_status or "",
                gate_reason_code=row.gate_reason_code or "",
                gate_reason_ko=REASON_LABELS_KO.get(row.gate_reason_code or "", ""),
                span_status=row.span_status or "",
                is_current=bool(latest is not None and latest.rcept_no == version.rcept_no),
                hard_case=hard_case(row, event),
                source_id=row.id,
            )
        )
    return out


def _dedupe(rows: list[Row]) -> tuple[list[Row], int]:
    """One reading per ``(rcept_no, field)`` — N21's residue is not evidence."""
    best: dict[tuple[str, str], Row] = {}
    collapsed = 0
    for row in sorted(rows, key=lambda r: (r.rcept_no, r.field_key, r.source_id)):
        key = (row.rcept_no, row.field_key)
        current = best.get(key)
        if current is None:
            best[key] = row
            continue
        collapsed += 1
        if row.is_current and not current.is_current:
            best[key] = row
    return list(best.values()), collapsed


def _perf_rows(session: Session) -> list[Row]:
    reports = session.scalars(
        select(PerformanceReport).where(PerformanceReport.parse_status == "parsed")
    ).all()
    out: list[Row] = []
    for report in reports:
        facts = report.facts or {}
        doc = None
        if report.payload_bytes:
            try:
                doc = BodyDocument.from_bytes(report.payload_bytes)
            except Exception:  # noqa: BLE001
                doc = None
        for order, key in enumerate(PERF_FIGURES, start=1):
            cited = facts.get(key)
            if not isinstance(cited, dict) or cited.get("span") is None:
                continue
            span = tuple(cited["span"])  # type: ignore[assignment]
            out.append(
                Row(
                    unit=f"perf:{report.rcept_no}",
                    kind="perf",
                    stratum="perf",
                    rights="R1",
                    corp_code=report.corp_code,
                    corp_name=report.corp_name or report.corp_code,
                    rcept_no=report.rcept_no,
                    field_key=f"perf_{key}",
                    field_ko=f"[실적] {cited.get('label') or key}",
                    field_order=20 + order,
                    extracted_value=str(cited.get("value") or ""),
                    quote=_squash(str(cited.get("raw") or "")),
                    context=_context(doc, span),
                    gate_status="deterministic",
                    gate_reason_code="",
                    gate_reason_ko="",
                    span_status="resolved",
                    is_current=True,
                    hard_case=_perf_hard_case(report, key, facts),
                    source_id=report.id,
                )
            )
    return out


# ---------------------------------------------------------------------------
# the draw — a pure function, so the determinism test needs no database
# ---------------------------------------------------------------------------
def select_sample(
    rows: Sequence[Row],
    *,
    quotas: dict[str, int] | None = None,
    booster: int = DEFAULT_BOOSTER,
    seed: int = DEFAULT_SEED,
) -> list[Row]:
    """Pick filings, then materialise their rows. Deterministic for a given seed.

    Pure: no database, no clock, no environment. Same ``rows`` + same seed → the
    same list, byte for byte, which is what ``tests/test_evalset.py`` asserts.
    """
    quotas = dict(quotas or DEFAULT_QUOTAS)
    units: dict[str, list[Row]] = {}
    for row in rows:
        units.setdefault(row.unit, []).append(row)
    for group in units.values():
        group.sort(key=lambda r: (r.field_order, r.field_key))

    stratum_of = {unit: group[0].stratum for unit, group in units.items()}
    picks: dict[str, tuple[str, frozenset[str] | None]] = {}

    for unit in sorted(u for u, g in units.items() if any(r.hard_case for r in g)):
        picks[unit] = ("forced", None)

    for stratum in sorted(quotas):
        pool = sorted(u for u in units if stratum_of[u] == stratum and u not in picks)
        random.Random(f"{seed}:{stratum}").shuffle(pool)
        for unit in pool[: max(0, quotas[stratum])]:
            picks[unit] = ("random", None)

    pool = sorted(
        u
        for u, group in units.items()
        if u not in picks and any(r.field_key == CORRECTION_FIELD for r in group)
    )
    random.Random(f"{seed}:booster").shuffle(pool)
    for unit in pool[: max(0, booster)]:
        picks[unit] = ("booster", frozenset({CORRECTION_FIELD}))

    chosen: list[Row] = []
    for unit, (pick, only) in picks.items():
        for row in units[unit]:
            if only is not None and row.field_key not in only:
                continue
            chosen.append(Row(**{**row.__dict__, "pick": pick}))

    chosen.sort(
        key=lambda r: (
            STRATUM_ORDER.get(r.stratum, 9),
            r.corp_name,
            r.rcept_no,
            r.field_order,
            r.field_key,
        )
    )
    prefix = {"extraction": "E", "perf": "P"}
    return [
        Row(**{**row.__dict__, "row_id": f"{prefix[row.kind]}{index:04d}"})
        for index, row in enumerate(chosen, start=1)
    ]


# ---------------------------------------------------------------------------
# corpus statistics — frozen beside the sample so the report needs no database
# ---------------------------------------------------------------------------
def _field_stats(all_rows: Iterable[Row]) -> dict:
    stats: dict[str, dict] = {}
    for row in all_rows:
        entry = stats.setdefault(
            row.field_key,
            {"order": row.field_order, "field_ko": row.field_ko, "total": 0,
             "blocked": 0, "by_status": {}, "reasons": {}},
        )
        entry["total"] += 1
        entry["by_status"][row.gate_status] = entry["by_status"].get(row.gate_status, 0) + 1
        if row.kind == "extraction" and row.gate_blocked:
            entry["blocked"] += 1
            code = row.gate_reason_code or "(none)"
            entry["reasons"][code] = entry["reasons"].get(code, 0) + 1
    for entry in stats.values():
        entry["block_rate"] = round(entry["blocked"] / entry["total"], 4) if entry["total"] else None
    return stats


def correction_recall(session: Session) -> dict:
    """§7 #10's recall proxy, stored free by S4 (N41): rows the model left uncovered.

    Records whose deterministic 정정사항 table did not parse (``items == 0``) are
    counted **separately**, never folded in. With ``items == 0`` every model
    change is trivially "unsupported", so mixing them in makes a parse gap read
    as a model regression — the corpus's 3 such records account for all 5 of its
    raw unsupported changes, and the gate already blocks each of them
    (``no_correction_rows``).

    Public because it is the one number on the sheet that no label feeds — it is
    a pure function of the stored records. That is what lets ``refresh-recall``
    re-freeze it after :func:`mijual.extract.runner.recheck_corrections` re-derives
    those records, without redrawing the sample the labels were made on.
    """
    totals = Counter()
    records = without_rows = 0
    for row in session.scalars(
        select(Extraction).where(Extraction.field_key == CORRECTION_FIELD)
    ).all():
        check = ((row.value or {}) if isinstance(row.value, dict) else {}).get(
            "deterministic_check"
        ) or {}
        if not check:
            continue
        if not int(check.get("items") or 0):
            without_rows += 1
            continue
        records += 1
        for key in ("items", "changes", "unsupported", "uncovered"):
            totals[key] += int(check.get(key) or 0)
    covered = totals["items"] - totals["uncovered"]
    return {
        "records": records,
        "records_without_parsed_rows": without_rows,
        "deterministic_rows": totals["items"],
        "model_changes": totals["changes"],
        "unsupported": totals["unsupported"],
        "uncovered": totals["uncovered"],
        "recall": round(covered / totals["items"], 4) if totals["items"] else None,
    }


def build_sample(
    session: Session,
    *,
    quotas: dict[str, int] | None = None,
    booster: int = DEFAULT_BOOSTER,
    seed: int = DEFAULT_SEED,
) -> EvalSample:
    """Read the corpus, draw the sample, and freeze both. Zero requests, zero calls."""
    all_rows, collapsed = collect_rows(session)
    chosen = select_sample(all_rows, quotas=quotas, booster=booster, seed=seed)

    available = Counter(r.stratum for r in {row.unit: row for row in all_rows}.values())
    selected = Counter(r.stratum for r in {row.unit: row for row in chosen}.values())
    rows_by_stratum = Counter(r.stratum for r in chosen)
    strata = {
        name: {
            "units_available": available[name],
            "units_selected": selected[name],
            "rows": rows_by_stratum[name],
        }
        for name in sorted(available, key=lambda s: STRATUM_ORDER.get(s, 9))
    }

    return EvalSample(
        seed=seed,
        generated_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        quotas=dict(quotas or DEFAULT_QUOTAS),
        booster=booster,
        corpus={
            "eligible_rows": len(all_rows),
            "eligible_filings": len({r.unit for r in all_rows}),
            "extraction_rows": sum(1 for r in all_rows if r.kind == "extraction"),
            "perf_rows": sum(1 for r in all_rows if r.kind == "perf"),
            "exposable_events": session.scalar(
                select(func.count(Event.id)).where(Event.exposure_state == "exposable")
            ),
            "parsed_performance_reports": session.scalar(
                select(func.count(PerformanceReport.id)).where(
                    PerformanceReport.parse_status == "parsed"
                )
            ),
        },
        strata=strata,
        field_stats=_field_stats(all_rows),
        correction_recall=correction_recall(session),
        duplicates_collapsed=collapsed,
        rows=chosen,
    )
