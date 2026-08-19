"""The four things the 본문 layer must not get wrong (P2.S3).

Everything runs against the P1 response cache with the client offline — no key,
no network, no invented XML. Terse by the workspace rule: one case per property
that would silently break the product.
"""

from __future__ import annotations

from datetime import date

import pytest

from mijual.bodydoc import (
    BodyDocument,
    TARGET_LABELS,
    extract_labels,
    find_sections,
    normalize,
    parse_correction,
    sections,
)
from mijual.config import SPIKE_CACHE_DIR
from mijual.dart import CacheMiss, DartClient

pytestmark = pytest.mark.skipif(
    not SPIKE_CACHE_DIR.exists(), reason="P1 sample cache is gitignored"
)


def _doc(rcept_no: str) -> BodyDocument:
    client = DartClient(cache_dir=SPIKE_CACHE_DIR, offline=True)
    try:
        return BodyDocument.from_bytes(client.get_document(rcept_no), rcept_no=rcept_no)
    except CacheMiss:  # pragma: no cover - fixture guard
        pytest.skip(f"{rcept_no} not in the P1 cache")


def test_all_ten_label_rows_are_read_with_typed_values():
    """계양전기 20260724000546 — field-matrix §1.3's 10/10, and the types that
    matter downstream (dates for the D-day, a ratio for 배정, 양도여부 as a bool)."""
    labels = extract_labels(_doc("20260724000546"))
    assert labels.target_coverage == (len(TARGET_LABELS), 10)
    assert labels.value("allotment_record_date") == date(2026, 7, 28)
    assert labels.value("payment_date") == date(2026, 9, 11)
    assert labels.value("shares_per_share") == 0.2314082845
    assert labels.value("warrant_transferable") is True
    assert labels.value("lead_underwriter") == "케이비증권 주식회사"
    # 청약예정일 is 대상자별 and stays split — a raw string beats a wrong parse.
    assert labels.qualified("subscription_dates", "구주주", "종료일").value == date(2026, 9, 4)
    assert labels.qualified("subscription_dates", "우리사주조합", "시작일").value == date(2026, 9, 3)


def test_every_extracted_value_re_slices_to_itself_in_the_stored_snapshot():
    """The layer-2 citation-span contract: extract → slice the snapshot → same value."""
    for rcept_no in ("20260724000546", "20260810000482", "20260521000775"):
        doc = _doc(rcept_no)
        rows = [r for r in extract_labels(doc).rows if r.span is not None]
        assert rows, rcept_no
        assert all(doc.verify(row.span, row.raw) for row in rows), rcept_no
        # ... and the raw slice really is the XML, not a normalised copy.
        first = rows[0]
        assert normalize(doc.text[first.span.start : first.span.end]) == first.raw


def test_correction_block_yields_the_hint_and_the_before_after_rows():
    """계양전기's 07-24 정정: 최초제출일 hint + 예정발행가 4,985 → 3,200 (§4.3)."""
    block = parse_correction(_doc("20260724000546"))
    assert block.present and block.declared_original_dt == date(2026, 5, 8)
    assert block.target_report == "주요사항보고서(유상증자결정)"
    price = next(i for i in block.items if "발행가액" in i.item)
    assert "4,985" in price.before and "3,200" in price.after and price.changed
    # 정정 전/정정 후 are frequently whole nested tables; keeping their text is
    # the point (the P1 spike collapsed them to a "[표]" marker and lost the diff).
    funds = next(i for i in block.items if "자금조달" in i.item)
    assert "16,409,000,000" in funds.before and "8,440,000,000" in funds.after

    # An original filing has no <CORRECTION> block, and that is not an error.
    assert parse_correction(_doc("20260810000482")).present is False


def test_registration_statement_is_sliced_by_title_never_read_whole():
    """20260814004100: 3.4M XML chars → a 34k-char section (field-matrix §5)."""
    doc = _doc("20260814004100")
    assert doc.is_registration_statement and len(doc.text) > 3_000_000
    every = sections(doc)
    assert len(every) > 50
    # The slices tile the document, so every offset stays a real snapshot offset.
    assert sum(len(s.span) for s in every) <= len(doc.text)
    assert all(a.span.end <= b.span.start for a, b in zip(every, every[1:]))
    procedure = find_sections(doc, r"모집 또는 매출절차")[0]
    assert len(procedure.span) < len(doc.text) / 50
    assert "청약" in procedure.text_of(doc)
