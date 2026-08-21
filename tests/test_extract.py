"""The four things the extraction layer must not get wrong (P2.S4).

Offline and deterministic on purpose: **no live API call is ever made from the
test suite** — the money story lives in the run report, not in pytest. The
model's side is a fabricated payload, which is exactly what a test should feed a
component that must not trust its input.
"""

from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from mijual.bodydoc import BodyDocument, normalize
from mijual.bodydoc.labels import LABEL_FIELDS
from mijual.config import SPIKE_CACHE_DIR
from mijual.dart import CacheMiss, DartClient
from mijual.db.models import Base, Extraction, RightsType
from mijual.db.repository import ensure_corp, ensure_event, ensure_version
from mijual.extract.fields import FIELDS, SCHEMA_VERSION, TASKS, response_schema
from mijual.extract.inputs import build_input
from mijual.extract.labelfields import LABEL_SPECS, read_document
from mijual.extract.locate import QuoteLocator
from mijual.extract.runner import check_against_items, recheck_corrections
from mijual.extract.store import upsert_extraction


def _doc(rcept_no: str) -> BodyDocument:
    if not SPIKE_CACHE_DIR.exists():  # pragma: no cover - fixture guard
        pytest.skip("P1 sample cache is gitignored")
    client = DartClient(cache_dir=SPIKE_CACHE_DIR, offline=True)
    try:
        return BodyDocument.from_bytes(client.get_document(rcept_no), rcept_no=rcept_no)
    except CacheMiss:  # pragma: no cover - fixture guard
        pytest.skip(f"{rcept_no} not in the P1 cache")


def test_registry_is_exactly_the_ten_prose_targets_and_never_a_label_field():
    """§7 is a closed list, and it must not overlap the deterministic layer —
    paying an LLM for a ``본문-label`` row is the phase's explicit anti-rule."""
    assert sorted(s.number for s in FIELDS.values()) == list(range(1, 11))
    assert not set(FIELDS) & set(LABEL_FIELDS.values())
    # The label tier is the other side of the same rule, and the two never
    # overlap: a key is read by the model **or** parsed for free, never both.
    assert not set(FIELDS) & set(LABEL_SPECS)
    assert all(spec.label_field in LABEL_FIELDS.values() for spec in LABEL_SPECS.values())
    for spec in FIELDS.values():
        assert spec.schema["required"] == ["present", "value", "quote", "note"]
        assert spec.gate  # P2.S5's specification travels with the field
    # Every runnable task's response schema names its fields and nothing else.
    schema = response_schema(TASKS["r1_prose"])
    assert schema["properties"]["fields"]["required"] == list(TASKS["r1_prose"].fields)


def test_a_quote_is_located_in_the_snapshot_and_a_hallucinated_one_is_not():
    """계양전기 20260724000546 — the span contract (N33) applied to a model quote."""
    doc = _doc("20260724000546")
    document = build_input(doc, task=TASKS["r1_prose"])
    assert document.scope == "document" and document.chars < 10_000  # §5's one-shot unit
    locator = QuoteLocator(document.flat, doc)

    verbatim = "3) 신주인수권증서 상장예정기간 : 2026년 08월 19일~ 2026년 08월 25일"
    found = locator.locate(verbatim)
    assert found.resolved and found.method == "exact" and found.verified is True
    assert doc.verify(found.span, verbatim)  # the gate's own predicate (P2.S5)

    # A faithful quote whose spacing drifted still resolves — as `nospace`, and
    # deliberately not as `verified`, so the gate can tell the two apart.
    spaced = locator.locate("3) 신주인수권증서  상장예정기간: 2026년 08월 19일 ~2026년 08월 25일")
    assert spaced.resolved and spaced.method == "nospace" and spaced.verified is False
    assert normalize(doc.raw(spaced.span)) == normalize(verbatim)

    # A plausible paraphrase is NOT a citation: it is recorded unresolved.
    assert locator.locate("신주인수권증서 매매기간은 8월 19일부터 8월 25일까지입니다").status == (
        "unresolved"
    )
    assert locator.locate(None).status == "no_quote"


def test_a_registration_statement_is_sliced_never_sent_whole():
    """§5's hard rule, enforced where the money is spent: 3.4M chars in, one
    named section out — and the section's offsets stay snapshot offsets."""
    doc = _doc("20260814004100")
    assert doc.is_registration_statement and len(doc.text) > 3_000_000
    document = build_input(doc, spec=FIELDS["subscription_agents"])
    assert document.scope.startswith("section:")
    assert document.chars < 25_001
    quote = document.text[400:460]
    found = QuoteLocator(document.flat, doc).locate(quote)
    assert found.resolved and doc.raw(found.span) and found.span.start >= document.span.start


def test_a_label_tier_field_is_read_for_free_and_cites_the_cell_it_read():
    """③ 매수예정가격 (D-15): a value with two deterministic witnesses is never
    bought from a model — it is read out of the form cell, and its citation is
    composed from the document's own text rather than asked for."""
    spec = LABEL_SPECS["appraisal_price"]
    reading = read_document(_doc("20260604000612"), spec)  # (주)휴온스 — 32,886
    assert reading.status == "extracted" and reading.value == {"price": 32886}
    assert reading.quote == "매수예정가격 32,886"
    assert reading.located.resolved and reading.located.verified is True
    # ``매수예정가격 -`` states no price: absent, never 0 and never a guess.
    empty = read_document(_doc("20260129000274"), spec)  # (주)큐라클
    assert empty.status == "absent" and empty.value is None and empty.located is None


def test_storage_is_idempotent_and_leaves_the_gate_columns_to_p2_s5():
    """A re-extraction updates the row; it never mints a second one."""
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with sessionmaker(bind=engine)() as session:
        ensure_corp(session, "00102618", corp_name="계양전기")
        event = ensure_event(
            session,
            corp_code="00102618",
            report_subtype="piicDecsn",
            original_rcept_dt="20260508",
            rights_type=RightsType.SUBSCRIPTION_WARRANT,
        )
        version = ensure_version(session, event, rcept_no="20260724000546")

        first = upsert_extraction(
            session,
            version,
            field_key="warrant_trading_period",
            schema_version=SCHEMA_VERSION,
            status="extracted",
            value={"start_date": "2026-08-19", "end_date": "2026-08-25"},
            quote="3) 신주인수권증서 상장예정기간",
        )
        first.gate_status = "pass"  # what P2.S5 will write
        again = upsert_extraction(
            session,
            version,
            field_key="warrant_trading_period",
            schema_version=SCHEMA_VERSION,
            status="extracted",
            value={"start_date": "2026-08-20", "end_date": "2026-08-26"},
        )
        session.commit()

        assert again.id == first.id
        assert session.query(Extraction).count() == 1
        assert again.value["start_date"] == "2026-08-20"
        assert again.span_status == "not_applicable" and again.span is None
        # A re-read invalidates the old verdict rather than inheriting it.
        assert again.gate_status is None
        # A schema bump records a new reading beside the old one.
        upsert_extraction(
            session,
            version,
            field_key="warrant_trading_period",
            schema_version="v2",
            status="extracted",
            value={},
        )
        session.commit()
        assert session.query(Extraction).count() == 2


def test_the_deterministic_correction_rows_are_ground_truth_not_the_model():
    """A change the ``3. 정정사항`` table does not support is flagged, not accepted."""
    items = [
        {"item": "6. 신주발행가액", "before": "예정발행가 4,985", "after": "예정발행가 3,200"},
        {"item": "11. 청약예정일", "before": "2026년 08월 03일", "after": "2026년 09월 03일"},
    ]
    changes = [
        {"item": "6. 신주발행가액", "new": "3,200", "kind": "amount_changed"},
        {"item": "12. 납입일", "new": "2026-09-30", "kind": "date_moved"},  # not in the table
    ]
    checked = check_against_items(changes, items)
    assert checked == {"items": 2, "changes": 2, "unsupported": 1, "uncovered": 1}
    assert changes[0]["supported"] is True and changes[0]["deterministic_item"] == 0
    assert changes[1]["supported"] is False


def test_changes_corrected_to_the_same_string_consume_different_rows():
    """N92's trap: 에이전트AI moves several schedule rows to one identical string.

    The first matcher took each change's first candidate row without checking
    whether another change already held it, so all three bound to row 0 and two
    genuinely covered rows were counted ``uncovered`` — the recall proxy read
    85.3 % where the corpus deserved 88.7 %. Recall counts *rows*, so a row may
    be claimed once.
    """
    items = [
        {"item": "11. 청약예정일", "before": "2026년 07월 21일", "after": "-(추후 확정)"},
        {"item": "12. 납입일", "before": "2026년 07월 28일", "after": "-(추후 확정)"},
        {"item": "13. 상장예정일", "before": "2026년 08월 11일", "after": "-(추후 확정)"},
    ]
    changes = [
        {"item": "11. 청약예정일", "new": "-(추후 확정)"},  # names its row
        {"item": "일정 전반", "new": "-(추후 확정)"},  # value arm only
        {"item": "일정 전반", "new": "-(추후 확정)"},  # value arm only
    ]
    checked = check_against_items(changes, items)
    assert checked == {"items": 3, "changes": 3, "unsupported": 0, "uncovered": 0}
    assert sorted(c["deterministic_item"] for c in changes) == [0, 1, 2]
    assert changes[0]["deterministic_item"] == 0  # a name match still wins its row


def test_recheck_rescores_stored_records_and_a_second_run_is_a_no_op():
    """The re-check is derived-only: 0 calls, model output untouched, idempotent."""
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)
    items = [
        {"item": "11. 청약예정일", "before": "2026년 07월 21일", "after": "-(추후 확정)"},
        {"item": "12. 납입일", "before": "2026년 07월 28일", "after": "-(추후 확정)"},
    ]
    with factory() as session:
        ensure_corp(session, "00812766", corp_name="에이전트AI")
        event = ensure_event(
            session,
            corp_code="00812766",
            report_subtype="piicDecsn",
            original_rcept_dt="20260317",
            rights_type=RightsType.SUBSCRIPTION_WARRANT,
        )
        version = ensure_version(session, event, rcept_no="20260619000455")
        upsert_extraction(
            session,
            version,
            field_key="correction_interpretation",
            schema_version=SCHEMA_VERSION,
            status="extracted",
            value={
                "deterministic_items": items,
                "interpretation": {
                    "summary": "일정이 전면 보류되었습니다",
                    # as the old matcher stored them: both bound to row 0
                    "changes": [
                        {"item": "일정", "new": "-(추후 확정)", "quote": "청약예정일 : -(추후 확정)",
                         "supported": True, "deterministic_item": 0},
                        {"item": "일정", "new": "-(추후 확정)", "quote": "납입일 : -(추후 확정)",
                         "supported": True, "deterministic_item": 0},
                    ],
                },
                "deterministic_check": {
                    "items": 2, "changes": 2, "unsupported": 0, "uncovered": 1
                },
            },
            quote="청약예정일 : -(추후 확정)",
        )
        session.commit()

    report = recheck_corrections(factory)
    assert (report.rewritten, report.records) == (1, 1)
    assert (report.old["uncovered"], report.new["uncovered"]) == (1, 0)
    assert report.old["unsupported"] == report.new["unsupported"] == 0

    assert recheck_corrections(factory).rewritten == 0  # idempotent

    with factory() as session:
        row = session.query(Extraction).one()
        assert row.value["deterministic_check"] == {
            "items": 2, "changes": 2, "unsupported": 0, "uncovered": 0
        }
        stored = row.value["interpretation"]
        assert sorted(c["deterministic_item"] for c in stored["changes"]) == [0, 1]
        # nothing the model produced moved
        assert row.quote == "청약예정일 : -(추후 확정)"
        assert stored["summary"] == "일정이 전면 보류되었습니다"
        assert [c["quote"] for c in stored["changes"]] == [
            "청약예정일 : -(추후 확정)", "납입일 : -(추후 확정)"
        ]
        assert row.value["deterministic_items"] == items
