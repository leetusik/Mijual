"""End-to-end smoke run for the P2.S1 scaffold — offline, no API key needed.

    docker compose up -d postgres
    .venv/bin/python -m mijual.smoke

What it proves, in one pass:

1. the ported client's cache key still reproduces the P1 spike's scheme — every
   read below is a **cache hit against ``scripts/spike/samples/``** with the
   client in ``offline`` mode, so a key-scheme regression fails loudly
   (:class:`~mijual.dart.CacheMiss`) instead of silently re-fetching;
2. the N2 collapse is real — three ``list.json`` rows for 계양전기's 유증 event
   (original + 2× ``[기재정정]``) versus the **one** row ``piicDecsn`` returns,
   which carries only the newest ``rcept_no``;
3. the event / version / snapshot chain persists to Postgres and reads back;
4. collection is idempotent — the whole persist step runs twice and the row
   counts do not move.

No secret value is read, printed or written anywhere in this module.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass

from sqlalchemy import func, select

from mijual.config import SPIKE_CACHE_DIR, load_settings
from mijual.dart import DartClient, decode_document, rows
from mijual.db.models import Corp, CorrectionKind, Event, FilingVersion, RightsType, Snapshot
from mijual.db.repository import ensure_corp, ensure_event, ensure_snapshot, ensure_version
from mijual.db.session import (
    create_all,
    make_engine,
    make_session_factory,
    reset_schema,
    session_scope,
)

# ── fixture: 계양전기 (00102618) 2026 주주배정 유상증자 ────────────────────────
# The field matrix' worked ① example. Its three versions live on three cached
# `list` pages; `piicDecsn` and the 본문 ZIP of the newest version are cached too.
CORP_CODE = "00102618"
REPORT_SUBTYPE = "piicDecsn"
LIST_PROBES = [  # (bgn_de, end_de, page_no) — all `pblntf_ty=B`, `corp_cls=Y`
    ("20260401", "20260630", 3),
    ("20260401", "20260630", 2),
    ("20260701", "20260818", 2),
]
DETAIL_WINDOW = ("20260101", "20260818")


@dataclass
class Counts:
    corps: int
    events: int
    versions: int
    snapshots: int

    def __str__(self) -> str:
        return (
            f"corp={self.corps} event={self.events} "
            f"version={self.versions} snapshot={self.snapshots}"
        )


def _counts(session) -> Counts:
    def n(model) -> int:
        return int(session.scalar(select(func.count()).select_from(model)) or 0)

    return Counts(n(Corp), n(Event), n(FilingVersion), n(Snapshot))


def collect_offline(client: DartClient) -> dict:
    """Read the fixture event out of the cache. Every call must be a cache hit."""
    list_rows: dict[str, dict] = {}
    for bgn_de, end_de, page_no in LIST_PROBES:
        body = client.get_json(
            "list",
            bgn_de=bgn_de,
            end_de=end_de,
            corp_cls="Y",
            pblntf_ty="B",
            page_no=page_no,
            page_count=100,
        )
        for row in rows(body):
            if row.get("corp_code") == CORP_CODE and "유상증자결정" in (row.get("report_nm") or ""):
                list_rows[row["rcept_no"]] = row

    if not list_rows:
        raise SystemExit("fixture rows not found in the cached list pages")

    detail = client.get_json(
        REPORT_SUBTYPE,
        corp_code=CORP_CODE,
        bgn_de=DETAIL_WINDOW[0],
        end_de=DETAIL_WINDOW[1],
    )
    detail_rows = rows(detail)

    ordered = sorted(list_rows.values(), key=lambda r: (r["rcept_dt"], r["rcept_no"]))
    originals = [r for r in ordered if CorrectionKind.from_report_nm(r["report_nm"]) is CorrectionKind.ORIGINAL]
    original = originals[0] if originals else ordered[0]
    newest = ordered[-1]
    document = client.get_document(newest["rcept_no"])
    return {
        "versions": ordered,
        "original": original,
        "newest": newest,
        "detail_rows": detail_rows,
        "document": document,
    }


def persist(session, collected: dict) -> None:
    original, newest = collected["original"], collected["newest"]
    ensure_corp(
        session,
        CORP_CODE,
        corp_name=original.get("corp_name"),
        stock_code=original.get("stock_code"),
        corp_cls=original.get("corp_cls"),
    )
    event = ensure_event(
        session,
        corp_code=CORP_CODE,
        report_subtype=REPORT_SUBTYPE,
        original_rcept_dt=original["rcept_dt"],
        rights_type=RightsType.SUBSCRIPTION_WARRANT,
        report_nm="주요사항보고서(유상증자결정)",
    )
    for row in collected["versions"]:
        version = ensure_version(
            session,
            event,
            rcept_no=row["rcept_no"],
            rcept_dt=row["rcept_dt"],
            report_nm=row["report_nm"],
        )
        # The list row is the cheapest possible snapshot of "what we saw".
        ensure_snapshot(session, version, source="list", payload_json=row)
        # ... the detail row and the 본문 belong to the version they describe.
        for detail_row in collected["detail_rows"]:
            if detail_row.get("rcept_no") == row["rcept_no"]:
                ensure_snapshot(session, version, source=REPORT_SUBTYPE, payload_json=detail_row)
        if row["rcept_no"] == newest["rcept_no"]:
            ensure_snapshot(session, version, source="document", payload_bytes=collected["document"])


def report(session, collected: dict) -> None:
    event = session.scalar(
        select(Event).where(
            Event.corp_code == CORP_CODE, Event.report_subtype == REPORT_SUBTYPE
        )
    )
    corp = session.get(Corp, CORP_CODE)
    print(f"\nevent key : ({event.corp_code}, {event.report_subtype}, {event.original_rcept_dt})")
    print(f"corp      : {corp.corp_name} [{corp.stock_code}] corp_cls={corp.corp_cls}")
    print(f"rights    : {event.rights_type.value} ({event.rights_type.name})")
    print(f"suppressed: {event.is_suppressed}")
    print(f"versions  : {len(event.versions)}  (latest {event.latest_version.rcept_no})")
    for version in event.versions:
        marks = ", ".join(
            f"{s.source}:{s.content_sha1[:8]}({s.byte_size}B)" for s in version.snapshots
        )
        print(f"  - {version.rcept_no} {version.rcept_dt} {version.correction_kind.value:<9} [{marks}]")

    detail_nos = [r.get("rcept_no") for r in collected["detail_rows"]]
    print(
        f"\nN2 check  : list gave {len(collected['versions'])} versions, "
        f"{REPORT_SUBTYPE} gave {len(detail_nos)} row(s) -> {detail_nos} "
        "(newest only; superseded values unrecoverable from the API)"
    )

    blob = session.scalar(
        select(Snapshot.payload_bytes).where(Snapshot.source == "document").limit(1)
    )
    text = decode_document(blob)
    print(
        f"본문 check : ZIP {len(blob)}B -> {len(text)} XML chars, "
        f"'신주인수권증서' ×{text.count('신주인수권증서')}, "
        f"CORRECTION block: {'<CORRECTION' in text}"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="P2.S1 offline smoke run")
    parser.add_argument("--database-url", default=None)
    parser.add_argument("--cache-dir", default=str(SPIKE_CACHE_DIR))
    parser.add_argument(
        "--keep", action="store_true", help="do not drop/recreate the schema first"
    )
    args = parser.parse_args(argv)

    settings = load_settings()
    print(f"settings  : {settings}")  # masked — never prints a key
    client = DartClient(settings=settings, cache_dir=args.cache_dir, offline=True)
    print(f"cache dir : {client.cache_dir} (offline)")

    collected = collect_offline(client)
    print(
        f"collected : {len(collected['versions'])} list rows, "
        f"{len(collected['detail_rows'])} detail row(s), "
        f"document {len(collected['document'])}B — all cache hits, no key, no network"
    )

    engine = make_engine(args.database_url)
    if args.keep:
        create_all(engine)
    else:
        reset_schema(engine)
    factory = make_session_factory(engine)

    with session_scope(factory) as session:
        persist(session, collected)
        first = _counts(session)
    with session_scope(factory) as session:
        persist(session, collected)  # idempotency: same inputs, no new rows
        second = _counts(session)
    print(f"\npersisted : {first}\nre-run    : {second}")
    if (first.corps, first.events, first.versions, first.snapshots) != (
        second.corps,
        second.events,
        second.versions,
        second.snapshots,
    ):
        print("IDEMPOTENCY FAILED: re-running the collection changed the row counts")
        return 1

    with session_scope(factory) as session:
        report(session, collected)

    print("\nOK — event/version/snapshot chain persisted, re-read, and idempotent")
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
