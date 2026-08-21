"""증권발행실적보고서 — discovery, and the deterministic reading of 청약 결과.

This is the one document family P1 never surveyed, and it is the missing half of
the 소멸 신주인수권 story: the 주요사항보고서 says how many 증서 *will* exist, and
the 실적보고서 — filed on the 납입일, after the 청약 closes — says how many were
actually used. Everything between those two numbers lapsed.

**No LLM touches this file.** The phase constraint is blunt (*anything
deterministically readable must not be paid for with an LLM call*), and the
numbers that matter sit in labelled tables:

* ``Ⅶ. 신주인수권증서 발행내역`` — how many 증서 the 명의개서대행기관 issued, and
  how many came back as 청약 (split 증서청약 / 초과청약);
* ``Ⅷ. 실권주 처리내역`` — the filer's own ``신주인수권증서 청약 실권주``;
* ``3. 청약 및 배정현황`` — the ``계`` row, whose 최종 금액 ÷ 최종 수량 **is** the
  확정발행가 (verified exactly against 본문 ``6. 확정발행가`` on 10/10 filings);
* ``1. 청약 및 납입일정`` — the report's own schedule, which is what binds it to
  an event rather than merely to a corp.

Two shapes exist and both are read here: the standard 주식 form and the
집합투자증권 (REIT) form, which carries the same 실권주 table inside its
``4. 청약, 배정 및 인수에 관한 사항`` and has **no** Ⅶ section at all.

Every figure comes back as a :class:`Cited` — value, the raw printed text, and a
character span into the decoded XML — so nothing this module produces can be
quoted without its evidence. A figure the table states across **several rows**
(``한국예탁결제원(신주인수권증서 청약)`` + ``직접청약(신주인수권증서 청약)``) carries
one :class:`CitedPart` per addend, because a single addend's cell does not state
the sum and quoting it as if it did would be a false citation (**D4**).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal, InvalidOperation

from mijual.bodydoc import BodyDocument, Cell, Span, cell_grid, tables
from mijual.bodydoc.labels import parse_korean_date
from mijual.dart import DartClient
from mijual.dart import rows as client_rows

__all__ = [
    "Cited",
    "CitedPart",
    "PERF_REPORT_PREFIX",
    "PerformanceFacts",
    "ScheduleRow",
    "census",
    "parse_performance",
    "squash",
]

#: 발행공시. ``list.json``'s ``pblntf_ty`` for 증권신고서 · 투자설명서 · 실적보고서.
PBLNTF_TY = "C"
#: The report family. ``증권발행실적보고서(집합투자증권)(…)`` (REIT) starts with it
#: too; ``증권발행실적보고서(합병등)`` is a merger report and is excluded by name.
PERF_REPORT_PREFIX = "증권발행실적보고서"
_EXCLUDED_SUFFIX = "(합병등)"
#: A corp that registered an equity offering in the window. Without this filter
#: the census is drowned by ELS/DLS: 2,533 of the 2026 실적보고서 rows are
#: 파생결합증권 issued by securities firms, and only 68 belong to a share offering.
_EQUITY_MARKERS = ("증권신고서(지분증권)", "소액공모공시서류(지분증권)")

_NUMERIC = re.compile(r"^-?[\d,]+(?:\.\d+)?$")


def squash(text: object) -> str:
    """Whitespace-free text — how every header cell is matched here."""
    return re.sub(r"\s+", "", str(text or ""))


def _number(text: str | None) -> Decimal | None:
    stripped = (text or "").strip()
    if not stripped or not _NUMERIC.match(stripped):
        return None
    try:
        return Decimal(stripped.replace(",", ""))
    except InvalidOperation:
        return None


@dataclass(frozen=True)
class CitedPart:
    """One cell that contributed to a figure — its printed text and its span."""

    raw: str
    span: tuple[int, int] | None

    def as_json(self) -> dict:
        return {"raw": self.raw, "span": list(self.span) if self.span else None}


@dataclass(frozen=True)
class Cited:
    """One figure, the text it was printed as, and where that text lives.

    Most figures are printed whole in one cell and ``raw``/``span`` *are* the
    citation. A few are a **sum the filer split across rows** — 한화솔루션's 청약
    38,430,497 is 예탁결제원 38,427,609 + 직접청약 2,888 — and there the whole
    number appears nowhere in the document. :attr:`parts` then holds every addend
    with its own text and span, so a surface can show the sum backed by all of
    them instead of quoting one and implying it says the rest (**D4**).
    ``parts`` is empty for the ordinary one-cell figure; when it is set,
    ``parts[0]`` is ``raw``/``span``, so every reader that knows only the single
    form keeps working and simply sees the first addend.
    """

    value: Decimal | date | None
    raw: str
    span: tuple[int, int] | None
    label: str = ""
    #: Every cell that was added up, and only when there was more than one.
    parts: tuple[CitedPart, ...] = ()

    def __post_init__(self) -> None:
        if not self.parts:
            return
        if len(self.parts) < 2:
            raise ValueError("one part is not a sum — leave parts empty and cite raw/span")
        first = self.parts[0]
        if first.raw != self.raw or first.span != self.span:
            raise ValueError("parts[0] must be raw/span: a multi-part citation starts there")

    @property
    def int_value(self) -> int | None:
        return int(self.value) if isinstance(self.value, Decimal) else None

    @property
    def citations(self) -> tuple[CitedPart, ...]:
        """Every cell backing this figure, one-cell figures included."""
        return self.parts or (CitedPart(raw=self.raw, span=self.span),)

    def as_json(self) -> dict:
        """The stored form. ``parts`` appears **only** on a real multi-addend sum,
        so a single-cell figure serializes byte-identically to before D4."""
        out: dict = {
            "value": str(self.value) if self.value is not None else None,
            "raw": self.raw,
            "span": list(self.span) if self.span else None,
            "label": self.label,
        }
        if self.parts:
            out["parts"] = [part.as_json() for part in self.parts]
        return out


@dataclass(frozen=True)
class ScheduleRow:
    """One row of ``1. 청약 및 납입일정``."""

    group: str
    begin: Cited | None
    end: Cited | None
    pay: Cited | None

    def as_json(self) -> dict:
        return {
            "group": self.group,
            "begin": self.begin.as_json() if self.begin else None,
            "end": self.end.as_json() if self.end else None,
            "pay": self.pay.as_json() if self.pay else None,
        }


@dataclass
class PerformanceFacts:
    """Everything one 실적보고서 states about the offering it reports."""

    rcept_no: str | None = None
    form: str = "none"
    schedule: tuple[ScheduleRow, ...] = ()
    #: Ⅶ — 발행된 신주인수권증서 수 (the denominator of every lapse rate).
    warrants_issued: Cited | None = None
    #: Ⅶ — 증서로 이루어진 청약 (초과청약 제외).
    warrants_exercised: Cited | None = None
    excess_subscribed: Cited | None = None
    #: Ⅷ — the filer's own 실권주 figure, and its 단수주-inclusive sibling.
    lapse_stated: Cited | None = None
    lapse_with_fractions: Cited | None = None
    fractional_shares: Cited | None = None
    #: ``3. 청약 및 배정현황`` 계 row (or the REIT form's 설정 좌수/금액).
    offer_shares: Cited | None = None
    final_shares: Cited | None = None
    final_amount: Cited | None = None
    notes: tuple[str, ...] = ()

    # -- derived ----------------------------------------------------------
    @property
    def lapse_derived(self) -> int | None:
        """발행 증서 − 청약 증서. The count this package actually uses (see calc)."""
        from mijual.calc import lapsed_warrants

        issued = self.warrants_issued.int_value if self.warrants_issued else None
        used = self.warrants_exercised.int_value if self.warrants_exercised else None
        return lapsed_warrants(issued, used)

    @property
    def issue_price(self) -> Decimal | None:
        """확정발행가 = 최종 배정 금액 ÷ 최종 배정 수량. Exact division only."""
        if self.final_amount is None or self.final_shares is None:
            return None
        amount, shares = self.final_amount.value, self.final_shares.value
        if not isinstance(amount, Decimal) or not isinstance(shares, Decimal) or shares <= 0:
            return None
        price = amount / shares
        return price if price == price.to_integral_value() else None

    @property
    def lapse_rate(self) -> Decimal | None:
        """소멸률 = 소멸 증서 ÷ 발행 증서."""
        issued = self.warrants_issued.int_value if self.warrants_issued else None
        lapsed = self.lapse_derived
        if not issued or lapsed is None:
            return None
        return (Decimal(lapsed) / Decimal(issued)).quantize(Decimal("0.0001"))

    @property
    def has_warrant_table(self) -> bool:
        return self.lapse_stated is not None or self.warrants_issued is not None

    def as_json(self) -> dict:
        return {
            "rcept_no": self.rcept_no,
            "form": self.form,
            "schedule": [row.as_json() for row in self.schedule],
            "warrants_issued": self.warrants_issued.as_json() if self.warrants_issued else None,
            "warrants_exercised": (
                self.warrants_exercised.as_json() if self.warrants_exercised else None
            ),
            "excess_subscribed": (
                self.excess_subscribed.as_json() if self.excess_subscribed else None
            ),
            "lapse_stated": self.lapse_stated.as_json() if self.lapse_stated else None,
            "lapse_with_fractions": (
                self.lapse_with_fractions.as_json() if self.lapse_with_fractions else None
            ),
            "fractional_shares": (
                self.fractional_shares.as_json() if self.fractional_shares else None
            ),
            "offer_shares": self.offer_shares.as_json() if self.offer_shares else None,
            "final_shares": self.final_shares.as_json() if self.final_shares else None,
            "final_amount": self.final_amount.as_json() if self.final_amount else None,
            "lapse_derived": self.lapse_derived,
            "issue_price": str(self.issue_price) if self.issue_price is not None else None,
            "lapse_rate": str(self.lapse_rate) if self.lapse_rate is not None else None,
            "notes": list(self.notes),
        }


# ---------------------------------------------------------------------------
# parsing
# ---------------------------------------------------------------------------
def _rows(doc: BodyDocument) -> list[list[list[Cell]]]:
    """Every table as a list of de-duplicated cell rows (ROWSPAN/COLSPAN expanded)."""
    out: list[list[list[Cell]]] = []
    for table in tables(doc):
        grid: list[list[Cell]] = []
        for line in cell_grid(table):
            cells: list[Cell] = []
            for cell in line:
                if not cells or cells[-1] is not cell:
                    cells.append(cell)
            if cells:
                grid.append(cells)
        if grid:
            out.append(grid)
    return out


def _cited(cell: Cell, label: str) -> Cited | None:
    value = _number(cell.text)
    if value is None:
        return None
    return Cited(value=value, raw=cell.text, span=(cell.span.start, cell.span.end), label=label)


def _cited_sum(value: Decimal, cells: list[Cell], label: str) -> Cited:
    """A figure summed over table rows, keeping **every** addend's cell.

    Dropping all but the first (which is what this module did before D4) leaves
    ``value`` stating the sum while ``raw``/``span`` state one term — the exact
    shape that made 7 figures in 4 filings uncitable.
    """
    parts = tuple(CitedPart(raw=c.text, span=(c.span.start, c.span.end)) for c in cells)
    return Cited(
        value=value,
        raw=parts[0].raw,
        span=parts[0].span,
        label=label,
        parts=parts if len(parts) > 1 else (),
    )


def _header_numbers(grid: list[list[Cell]]) -> list[tuple[str, Cited]]:
    """``(header text, number directly beneath it)`` for every column of a table.

    The 실권주 tables are two rows — a header row and one value row — but the
    column *order* is filer's choice (``P2.S8`` measured 실권주 in position 0, 1
    and 2 across the corpus) and so is the header wording. Reading them by
    position would be a bug waiting to happen; reading them by the header above
    the number is stable.
    """
    found: list[tuple[str, Cited]] = []
    for index in range(len(grid) - 1):
        head, below = grid[index], grid[index + 1]
        if len(head) != len(below) or len(head) < 2:
            continue
        for column, header_cell in enumerate(head):
            if _number(header_cell.text) is not None:
                continue  # a numeric "header" means this is not a header row
            cited = _cited(below[column], header_cell.text)
            if cited is not None:
                found.append((squash(header_cell.text), cited))
    return found


def _row_numbers(grid: list[list[Cell]]) -> list[tuple[str, Cited]]:
    """``(label, number beside it)`` for row-oriented tables (label | value | 비고).

    The 집합투자증권 form states its offering that way — ``설정 좌수 | 49,350,000``
    — instead of as a header row above a value row.
    """
    found: list[tuple[str, Cited]] = []
    for line in grid:
        if len(line) < 2 or _number(line[0].text) is not None:
            continue
        cited = _cited(line[1], line[0].text)
        if cited is not None:
            found.append((squash(line[0].text), cited))
    return found


def _schedule(grid: list[list[Cell]]) -> tuple[ScheduleRow, ...]:
    header = [squash(c.text) for c in grid[0]]
    if not any("청약개시일" in h for h in header):
        return ()
    begin_at = next(i for i, h in enumerate(header) if "청약개시일" in h)
    end_at = next((i for i, h in enumerate(header) if "청약종료일" in h), None)
    pay_at = next((i for i, h in enumerate(header) if "납입" in h), None)

    def cited(cells: list[Cell], index: int | None, label: str) -> Cited | None:
        if index is None or index >= len(cells):
            return None
        parsed = parse_korean_date(cells[index].text)
        if parsed is None:
            return None
        span = cells[index].span
        return Cited(value=parsed, raw=cells[index].text, span=(span.start, span.end), label=label)

    out: list[ScheduleRow] = []
    for line in grid[1:]:
        if len(line) <= begin_at:
            continue
        row = ScheduleRow(
            group=line[0].text,
            begin=cited(line, begin_at, "청약개시일"),
            end=cited(line, end_at, "청약종료일"),
            pay=cited(line, pay_at, "납입기일"),
        )
        if row.begin is not None:
            out.append(row)
    return tuple(out)


def _allocation(grid: list[list[Cell]]) -> tuple[Cited | None, Cited | None, Cited | None, str | None]:
    """``3. 청약 및 배정현황``'s ``계`` row → (최초 수량, 최종 수량, 최종 금액, note).

    The table is ten numeric columns wide — 최초(수량·비율) · 청약(건수·수량·금액·비율)
    · 최종(건수·수량·금액·비율) — so the last three that matter are at ``-3``,
    ``-2``. Anything of another width is refused with a note rather than read by
    guesswork.
    """
    flat = squash(" ".join(c.text for row in grid[:3] for c in row))
    if "최초배정" not in flat or "최종배정" not in flat:
        return (None, None, None, None)
    for line in grid:
        if squash(line[0].text) not in ("계", "합계", "합 계"):
            continue
        numbers = [_cited(cell, "계") for cell in line[1:]]
        numbers = [n for n in numbers if n is not None]
        if len(numbers) != 10:
            return (None, None, None, f"계 row has {len(numbers)} numeric columns, expected 10")
        return (numbers[0], numbers[7], numbers[8], None)
    return (None, None, None, None)


def _reit_offer(pairs: list[tuple[str, Cited]]) -> tuple[Cited | None, Cited | None]:
    """The 집합투자증권 form states the offering as 설정 좌수 / 설정 금액."""
    shares = amount = None
    for header, cited in pairs:
        if "설정좌수" in header:
            shares = cited
        elif "설정금액" in header:
            amount = cited
    return (shares, amount)


def parse_performance(doc: BodyDocument) -> PerformanceFacts:
    """Read one 증권발행실적보고서. Pure function of the document; no I/O."""
    grids = _rows(doc)
    facts = PerformanceFacts(rcept_no=doc.rcept_no)
    notes: list[str] = []
    schedule: tuple[ScheduleRow, ...] = ()
    pairs: list[tuple[str, Cited]] = []
    labelled: list[tuple[str, Cited]] = []

    for grid in grids:
        if not schedule:
            schedule = _schedule(grid)
        pairs.extend(_header_numbers(grid))
        labelled.extend(_row_numbers(grid))

        header = [squash(c.text) for c in grid[0]]
        # Ⅶ 신주인수권증서 발행내역: 청구일 | 발행시기 | 청구자 | 관계 | 주식수
        if any("발행시기" in h for h in header) and any("주식수" in h for h in header):
            column = next(i for i, h in enumerate(header) if "주식수" in h)
            for line in grid[1:]:
                if squash(line[0].text) in ("계", "합계") and len(line) > 1:
                    facts.warrants_issued = _cited(line[-1], "신주인수권증서 발행 계")
        # Ⅶ 신주인수권증서에 의한 청약내역: 청약일 | 청약자 | 관계 | 주식수
        elif any("청약자" in h for h in header) and any("주식수" in h for h in header):
            column = next(i for i, h in enumerate(header) if "주식수" in h)
            used = excess = Decimal(0)
            used_cells: list[Cell] = []
            excess_cells: list[Cell] = []
            for line in grid[1:]:
                if squash(line[0].text) in ("계", "합계") or len(line) <= column:
                    continue
                amount = _number(line[column].text)
                if amount is None:
                    continue
                who = squash(" ".join(c.text for c in line[:column]))
                if "초과" in who:
                    excess += amount
                    excess_cells.append(line[column])
                elif "신주인수권증서" in who or "증서" in who:
                    used += amount
                    used_cells.append(line[column])
            # 예탁결제원 청약 and 직접청약 are two rows of the same figure in 4 of
            # the 32 parsed reports; both are kept, so the sum can be cited.
            if used_cells:
                facts.warrants_exercised = _cited_sum(used, used_cells, "신주인수권증서 청약")
            if excess_cells:
                facts.excess_subscribed = _cited_sum(excess, excess_cells, "초과청약")

        if facts.final_shares is None:
            first, final_shares, final_amount, note = _allocation(grid)
            if final_shares is not None:
                facts.offer_shares, facts.final_shares, facts.final_amount = (
                    first,
                    final_shares,
                    final_amount,
                )
            elif note:
                notes.append(note)

    # Header wording is the filer's, and ``P2.S8`` measured that ``청약`` is the
    # discriminating word: 대동기어 ``20260728000264`` labels its 단수주 column
    # ``신주인수권증서 배정 실권주`` beside the real ``신주인수권증서 청약 실권주``,
    # so a match on 실권주 alone reads the 단수주 as the answer (9,397 vs
    # 1,437,309). Match on 청약, and treat 배정/단수주 wording as the 단수주.
    for header, cited in pairs:
        if "신주인수권증서" in header and "실권주" in header and "청약" in header:
            if "단수주" in header or "총계" in header:
                facts.lapse_with_fractions = facts.lapse_with_fractions or cited
            else:
                facts.lapse_stated = facts.lapse_stated or cited
        elif "단수주" in header and ("배정" in header or "구주주" in header):
            facts.fractional_shares = facts.fractional_shares or cited
        elif "신주인수권증서" in header and "배정" in header and "실권주" in header:
            facts.fractional_shares = facts.fractional_shares or cited

    if facts.offer_shares is None:
        shares, amount = _reit_offer(pairs + labelled)
        if shares is not None:
            facts.offer_shares = shares
            facts.final_shares, facts.final_amount = shares, amount
            facts.form = "reit"

    facts.schedule = schedule
    if facts.form != "reit":
        facts.form = "standard" if facts.has_warrant_table else "none"
    if not facts.has_warrant_table:
        notes.append("no 신주인수권증서 table — not a 주주배정 유증 (IPO/스팩/제3자배정)")
    if (
        facts.lapse_stated is not None
        and facts.lapse_derived is not None
        and facts.lapse_stated.int_value != facts.lapse_derived
    ):
        notes.append(
            f"lapse_mismatch: 실적보고서 states {facts.lapse_stated.int_value:,} but "
            f"Ⅶ gives {facts.lapse_derived:,} (발행 − 청약)"
        )
    facts.notes = tuple(notes)
    return facts


# ---------------------------------------------------------------------------
# discovery
# ---------------------------------------------------------------------------
@dataclass
class Census:
    """Every 증권발행실적보고서 filed in a window, and the equity-offering subset."""

    scanned: int = 0
    reports: list[dict] = field(default_factory=list)
    candidates: list[dict] = field(default_factory=list)
    equity_corps: set[str] = field(default_factory=set)
    requests: int = 0

    def render(self) -> str:
        return (
            f"census     : {self.scanned:,} 발행공시 row(s), "
            f"{len(self.reports):,} 증권발행실적보고서, "
            f"{len(self.candidates)} on an equity offering "
            f"({len({r['corp_code'] for r in self.candidates})} corp(s)) — "
            f"{self.requests} request(s)"
        )


def census(
    client: DartClient,
    bgn_de: str,
    end_de: str,
    *,
    markets: tuple[str, ...] = ("Y", "K"),
    months: int = 3,
    log=None,
) -> Census:
    """Every 증권발행실적보고서 filed in ``[bgn_de, end_de]`` — the honest frame.

    A "2026 소멸" number cannot be framed by the *filing* window of the
    주요사항보고서: the 청약 lands two to six months after the 유상증자결정, so a
    right that lapsed in 2026-02 was decided in 2025. Framing on the 실적보고서
    instead makes the population exactly *what completed in the window*, and
    ``P2.S8`` measured what that costs to ignore — **7 of the 17** completed ①
    offerings of 2026 were decided before the corpus's 2026-01-01 start.
    """
    from mijual.collect.discovery import chunk_windows

    result = Census()
    seen: dict[str, dict] = {}
    started = client.request_count

    for bgn, end in chunk_windows(bgn_de, end_de, months=months):
        for market in markets:
            page_no, total_page = 1, 1
            while page_no <= total_page:
                body = client.get_json(
                    "list",
                    bgn_de=bgn,
                    end_de=end,
                    pblntf_ty=PBLNTF_TY,
                    corp_cls=market,
                    page_no=page_no,
                    page_count=100,
                )
                page_rows = client_rows(body)
                total_page = int(body.get("total_page") or 1)
                result.scanned += len(page_rows)
                for row in page_rows:
                    name = (row.get("report_nm") or "").strip()
                    if any(marker in name for marker in _EQUITY_MARKERS):
                        result.equity_corps.add(row["corp_code"])
                    if name.startswith(PERF_REPORT_PREFIX) and _EXCLUDED_SUFFIX not in name:
                        seen.setdefault(row["rcept_no"], row)
                if not page_rows:
                    break
                page_no += 1
            if log:
                log(f"  list {bgn}~{end} {market}: {result.scanned:,} row(s) so far")

    result.reports = sorted(seen.values(), key=lambda r: (r["rcept_dt"], r["rcept_no"]))
    result.candidates = [r for r in result.reports if r["corp_code"] in result.equity_corps]
    result.requests = client.request_count - started
    return result
