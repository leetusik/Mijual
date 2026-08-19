"""CLI for the 2026 소멸 신주인수권 가치 총액 estimate.

    # 1. the number, regenerated from the database — 0 requests, 0 LLM calls
    .venv/bin/python -m mijual.estimate report

    # 2. collect the 청약 결과 (census → 본문 → parse → link → adopt), budgeted
    .venv/bin/python -m mijual.estimate collect --bgn 20260101 --max-requests 400

    # 3. census only: how many 증권발행실적보고서 exist, and how many are equity
    .venv/bin/python -m mijual.estimate census --bgn 20260101

    # 4. one 실적보고서, every parsed figure with its citation span
    .venv/bin/python -m mijual.estimate show 20260521000623

``report`` is the command the committed numbers come from (N8): every figure the
result quotes is printed by it, so a stale hand-copied total cannot survive.
Nothing here prints, writes or accepts a secret.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

from sqlalchemy import select

from mijual.bodydoc import BodyDocument, Span
from mijual.calc import today_kst
from mijual.config import load_settings
from mijual.dart import DartClient
from mijual.db.models import Base, PerformanceReport
from mijual.db.schema_sync import ensure_columns
from mijual.db.session import create_all, make_engine, make_session_factory, session_scope
from mijual.estimate import build_report, won
from mijual.estimate.perf import census, parse_performance
from mijual.estimate.runner import collect_performance

DEFAULT_BGN = "20260101"


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="python -m mijual.estimate", description=__doc__)
    p.add_argument("--database-url", default=None)
    p.add_argument("--report", default=None, help="also write the run's payload as JSON here")
    p.add_argument("--quiet", action="store_true")
    sub = p.add_subparsers(dest="command", required=True)

    rep = sub.add_parser("report", help="the estimate, from the DB (0 requests, 0 calls)")
    rep.add_argument("--today", default=None, help="anchor date YYYYMMDD (default: today KST)")
    rep.add_argument("--korean", action="store_true", help="also print the 발표용 문장")

    col = sub.add_parser("collect", help="census + 본문 + parse + link (+ adopt)")
    col.add_argument("--bgn", default=DEFAULT_BGN)
    col.add_argument("--end", default=None, help="default: today KST")
    col.add_argument("--corp-cls", nargs="+", default=["Y", "K"])
    col.add_argument("--max-requests", type=int, default=400, help="live OpenDART ceiling")
    col.add_argument("--max-documents", type=int, default=None)
    col.add_argument("--no-adopt", action="store_true",
                     help="do not adopt a 유상증자결정 the corpus is missing")
    col.add_argument("--cache-dir", default=None)
    col.add_argument("--offline", action="store_true", help="cache only; never fetch")

    cen = sub.add_parser("census", help="count 증권발행실적보고서 in a window (no documents)")
    cen.add_argument("--bgn", default=DEFAULT_BGN)
    cen.add_argument("--end", default=None)
    cen.add_argument("--corp-cls", nargs="+", default=["Y", "K"])
    cen.add_argument("--max-requests", type=int, default=200)
    cen.add_argument("--offline", action="store_true")

    show = sub.add_parser("show", help="one stored 실적보고서 and its citation spans")
    show.add_argument("rcept_no")
    return p


def _factory(args):
    engine = make_engine(args.database_url)
    create_all(engine)
    ensure_columns(engine, Base)
    return make_session_factory(engine)


def _as_date(value: str | None) -> date:
    if not value:
        return today_kst()
    return date(int(value[:4]), int(value[4:6]), int(value[6:8]))


def _client(args):
    return DartClient(
        settings=load_settings(),
        cache_dir=getattr(args, "cache_dir", None),
        offline=getattr(args, "offline", False),
        max_requests=args.max_requests,
    )


# ---------------------------------------------------------------------------
def cmd_report(args, factory) -> dict:
    today = _as_date(args.today)
    with session_scope(factory) as session:
        estimate = build_report(session, today=today)
        print(estimate.render())
        if args.korean:
            print()
            print(korean_lines(estimate))
        return estimate.as_json()


def korean_lines(estimate) -> str:
    """The 발표/랜딩용 문장 — Korean product surface, with the trace behind each."""
    rate = estimate.overall_lapse_rate
    biggest = max(estimate.valued, key=lambda r: r.value, default=None)
    lines = [
        "발표용 문장 (근거는 report 표에서 그대로 재생성됨):",
        f"  · 2026년에 소멸한 신주인수권 가치는 ▷ 약 {won(estimate.total_value)}입니다.",
        f"    (증권발행실적보고서 {len(estimate.rows)}건 · 소멸 증서 {estimate.total_lapsed:,}주 "
        f"× 확정발행가 × 할인율/(1−할인율))",
    ]
    if rate is not None:
        lines.append(
            f"  · 주주에게 배정된 신주인수권증서 {estimate.total_issued:,}주 가운데 "
            f"{rate:.1%}가 청약도 매도도 되지 않고 사라졌습니다."
        )
    if biggest is not None:
        lines.append(
            f"  · 한 건에서만 {won(biggest.value)}이 사라졌습니다 "
            f"({biggest.corp_name}, 청약 종료 {biggest.subscription_end}, "
            f"소멸 {biggest.lapsed:,}주 — {biggest.performance_rcept_no})."
        )
    if estimate.pending:
        upcoming = [r for r in estimate.pending if r.reason == "청약 예정"]
        if upcoming:
            soonest = min(upcoming, key=lambda r: r.subscription_end or date.max)
            lines.append(
                f"  · 지금도 {len(upcoming)}건의 신주인수권이 소멸을 앞두고 있습니다 "
                f"(가장 빠른 청약 마감 {soonest.subscription_end}, {soonest.corp_name})."
            )
    lines.append(
        "  · 모든 수치는 DART 공시에서만 나왔고, 추정치는 ▷로 표시했습니다."
    )
    return "\n".join(lines)


def cmd_collect(args, factory) -> dict:
    client = _client(args)
    end = args.end or today_kst().strftime("%Y%m%d")
    result = collect_performance(
        client,
        factory,
        bgn_de=args.bgn,
        end_de=end,
        markets=tuple(args.corp_cls),
        max_documents=args.max_documents,
        adopt=not args.no_adopt,
        log=None if args.quiet else print,
    )
    print(result.render())
    return result.__dict__


def cmd_census(args, factory) -> dict:
    client = _client(args)
    end = args.end or today_kst().strftime("%Y%m%d")
    found = census(client, args.bgn, end, markets=tuple(args.corp_cls))
    print(found.render())
    for row in found.candidates:
        print(f"  {row['rcept_dt']} {row['rcept_no']} {row['corp_name']}")
    return {
        "scanned": found.scanned,
        "reports": len(found.reports),
        "candidates": [r["rcept_no"] for r in found.candidates],
        "requests": found.requests,
    }


def cmd_show(args, factory) -> dict:
    with session_scope(factory) as session:
        stored = session.scalar(
            select(PerformanceReport).where(PerformanceReport.rcept_no == args.rcept_no)
        )
        if stored is None:
            print(f"no stored 증권발행실적보고서 {args.rcept_no}")
            return {}
        doc = BodyDocument.from_bytes(stored.payload_bytes, rcept_no=stored.rcept_no)
        facts = parse_performance(doc)
        print(f"report     : {stored.rcept_no} {stored.corp_name} ({stored.rcept_dt}) "
              f"form={stored.form} link={stored.link_status} — {stored.link_note}")
        for row in facts.schedule:
            print(f"  일정      {row.group}: {row.begin.value if row.begin else '-'}"
                  f" ~ {row.end.value if row.end else '-'} / 납입 "
                  f"{row.pay.value if row.pay else '-'}")
        for label, cited in (
            ("증서 발행", facts.warrants_issued),
            ("증서 청약", facts.warrants_exercised),
            ("초과청약", facts.excess_subscribed),
            ("실권주(기재)", facts.lapse_stated),
            ("단수주", facts.fractional_shares),
            ("최종 배정 수량", facts.final_shares),
            ("최종 배정 금액", facts.final_amount),
        ):
            if cited is None:
                continue
            span = Span(*cited.span) if cited.span else None
            ok = doc.verify(span, cited.raw) if span else False
            print(f"  {label:<14} {cited.value!s:>18}  span={cited.span} "
                  f"verify={'ok' if ok else 'FAILED'}  [{cited.label}]")
        print(f"  소멸(도출)     {facts.lapse_derived!s:>18}   확정발행가 {facts.issue_price}")
        for note in facts.notes:
            print(f"  ! {note}")
        return facts.as_json()


COMMANDS = {
    "report": cmd_report,
    "collect": cmd_collect,
    "census": cmd_census,
    "show": cmd_show,
}


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    payload = COMMANDS[args.command](args, _factory(args))
    if args.report:
        Path(args.report).write_text(
            json.dumps(payload, ensure_ascii=False, indent=1, default=str), encoding="utf-8"
        )
        print(f"report file: {args.report}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
