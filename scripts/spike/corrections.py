"""P1.S1 spike: 정정공시(기재정정) pairing + diff-target discovery.

Answers phase question Q2. Two independent mechanisms are exercised:

  A) document-header parse — the 정정 filing's own <CORRECTION> block carries
     "정정대상 공시서류", "정정대상 공시서류의 최초제출일" and a 정정사항 table
     (항목 / 정정사유 / 정정 전 / 정정 후). This is a machine-readable what-changed
     block; no re-fetch diff is required to know which fields moved.
  B) structured re-fetch — query the 주요사항보고서 detail endpoint around both the
     original's and the correction's 접수일 to see which version the API returns.

Usage:
    python3 scripts/spike/corrections.py            # 20 corrections, all 3 rights types
    python3 scripts/spike/corrections.py 60         # bigger 항목-frequency sample
"""

from __future__ import annotations

import concurrent.futures as cf
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dart  # noqa: E402
from survey import WINDOWS, MARKETS, SUMMARY, YEAR  # noqa: E402

# rights type -> (report subtype in report_nm, 주요사항보고서 detail endpoint)
TARGETS = {
    "① 유증 신주인수권": ("유상증자결정", "piicDecsn"),
    "② CB 오버행": ("전환사채권발행결정", "cvbdIsDecsn"),
    "② EB 오버행": ("교환사채권발행결정", "exbdIsDecsn"),
    "③ 매수청구권": ("회사합병결정", "cmpMgDecsn"),
}
KDATE = re.compile(r"(\d{4})\s*년\s*(\d{1,2})\s*월\s*(\d{1,2})\s*일")


def discover_b() -> list[dict]:
    jobs = [(b, e, m) for b, e in WINDOWS for m in MARKETS]
    out: list[dict] = []
    with cf.ThreadPoolExecutor(6) as ex:
        for got in ex.map(lambda t: dart.filings(t[0], t[1], pblntf_ty="B", corp_cls=t[2], pages=10), jobs):
            out.extend(got)
    return out


def top_tables(block: str) -> list[str]:
    """Top-level <TABLE>...</TABLE> blocks (nested tables stay inside their parent)."""
    out, depth, start = [], 0, None
    for m in re.finditer(r"<TABLE\b|</TABLE>", block, re.I):
        if m.group(0).upper().startswith("<TABLE"):
            if depth == 0:
                start = m.start()
            depth += 1
        elif depth:
            depth -= 1
            if depth == 0 and start is not None:
                out.append(block[start:m.end()])
    return out


def text_of(fragment: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", fragment)).strip()


def table_rows(table: str) -> list[list[str]]:
    """Rows of one table's own cells; nested tables are collapsed to their text."""
    body = re.sub(r"<TABLE\b.*?</TABLE>", " [표] ", table[table.find(">") + 1:], flags=re.S | re.I)
    out = []
    for tr in re.findall(r"<TR\b.*?</TR>", body, re.S | re.I):
        row = [text_of(c)[:110] for c in re.findall(r"<T[DH]\b[^>]*>(.*?)</T[DH]>", tr, re.S | re.I)]
        if any(row):
            out.append(row)
    return out


def parse_correction(rcept_no: str) -> dict:
    """<CORRECTION> header of a 정정 filing: target report, original date, 정정사항 rows."""
    text = dart.document_text(rcept_no)
    m = re.search(r"<CORRECTION\b.*?</CORRECTION>", text, re.S)
    block = m.group(0) if m else text[:30000]
    flat = text_of(block)

    tgt = re.search(r"정정대상 공시서류\s*:?\s*(.{0,60}?)\s*(?:2\.\s*정정대상|정정대상 공시서류의)", flat)
    dt = re.search(r"최초제출일\s*:?\s*" + KDATE.pattern, flat)
    orig_dt = f"{dt.group(1)}{int(dt.group(2)):02d}{int(dt.group(3)):02d}" if dt else None

    items = []
    for table in top_tables(block):
        head = text_of(table[:3000])
        if not (("항 목" in head or "항목" in head) and ("정 정 전" in head or "정정전" in head)):
            continue  # only the 정정사항 table itself
        for row in table_rows(table):
            label = row[0]
            if not label or "항 목" in label or label in ("항목", "정정사유"):
                continue
            if len(row) >= 3:
                items.append({"item": label[:60], "before": row[-2][:90], "after": row[-1][:90]})
    return {"target_report": (tgt.group(1).strip() if tgt else None), "original_rcept_dt": orig_dt,
            "items": items}


def subtype(report_nm: str) -> str | None:
    m = re.search(r"\(([^)]+)\)$", report_nm)
    return m.group(1) if m else None


def main() -> None:
    want = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    b_rows = discover_b()

    # index every 2026 주요사항보고서 by (corp, subtype) for the pairing search
    index: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for r in b_rows:
        st = subtype(r["report_nm"])
        if st:
            index[(r["corp_code"], st)].append(r)
    for v in index.values():
        v.sort(key=lambda r: r["rcept_dt"])

    per_type = max(2, want // len(TARGETS))
    picked: list[tuple[str, dict, str]] = []
    for label, (st, endpoint) in TARGETS.items():
        corrs = [r for r in b_rows if r["report_nm"] == f"[기재정정]주요사항보고서({st})"]
        corrs.sort(key=lambda r: r["rcept_dt"])
        step = max(1, len(corrs) // per_type)
        picked += [(label, r, endpoint) for r in corrs[::step][:per_type]]

    print(f"corrections sampled: {len(picked)} across {len(TARGETS)} report subtypes "
          f"(2026-01-01~08-18, KOSPI+KOSDAQ)\n")

    results, item_freq = [], Counter()
    for label, row, endpoint in picked:
        st = subtype(row["report_nm"])
        try:
            head = parse_correction(row["rcept_no"])
        except Exception as exc:  # noqa: BLE001
            print(f"! {row['rcept_no']} parse failed: {type(exc).__name__}")
            continue

        # A) pair by (corp, subtype) + 최초제출일, else nearest earlier filing
        siblings = [s for s in index[(row["corp_code"], st)] if s["rcept_no"] != row["rcept_no"]]
        exact = [s for s in siblings if head["original_rcept_dt"] and s["rcept_dt"] == head["original_rcept_dt"]]
        earlier = [s for s in siblings if s["rcept_dt"] < row["rcept_dt"]]
        if exact:
            match, how = exact[0], "exact 최초제출일"
        elif earlier:
            match, how = earlier[-1], "nearest earlier"
        else:
            match, how = None, "unpaired (original outside the 2026 list window)"

        # B) which version does the structured endpoint return, and on which date is it indexed?
        year = dart.rows(dart.get_json(endpoint, corp_code=row["corp_code"], bgn_de=YEAR[0], end_de=YEAR[1]))
        bddd = next((KDATE.sub(lambda m: f"{m.group(1)}{int(m.group(2)):02d}{int(m.group(3)):02d}", r["bddd"])
                     for r in year if r.get("rcept_no") == row["rcept_no"] and r.get("bddd")), None)
        probe = {"year-window": [r["rcept_no"] for r in year],
                 "correction_rcept_no_returned": any(r["rcept_no"] == row["rcept_no"] for r in year),
                 "bddd": bddd}
        for tag, day in (("orig-submit-date", head["original_rcept_dt"]), ("corr-submit-date", row["rcept_dt"]),
                         ("bddd-date", bddd)):
            if not (day and re.fullmatch(r"\d{8}", day)):
                continue
            try:
                body = dart.get_json(endpoint, corp_code=row["corp_code"], bgn_de=day, end_de=day)
                probe[tag] = [r["rcept_no"] for r in dart.rows(body)]
            except Exception:  # noqa: BLE001 — OpenDART 503s on some windows; not load-bearing
                probe[tag] = ["<probe failed>"]

        for it in head["items"]:
            item_freq[re.sub(r"^[\d]+[-.]?\s*", "", it["item"])[:40]] += 1

        print(f"--- {label} | 정정 {row['rcept_no']} {row['corp_name']} ({row['rcept_dt']})")
        print(f"    target={head['target_report']} 최초제출일={head['original_rcept_dt']} "
              f"| paired original={match['rcept_no'] if match else '-'} ({how})")
        print(f"    {endpoint}: year-window returns {probe['year-window']} "
              f"(this 정정's rcept_no present: {probe['correction_rcept_no_returned']}); "
              f"bddd={probe['bddd']}")
        print(f"      single-day probes: orig={probe.get('orig-submit-date')} "
              f"corr={probe.get('corr-submit-date')} bddd={probe.get('bddd-date')}")
        for it in head["items"][:6]:
            print(f"      · {it['item']}: {it['before']}  ->  {it['after']}")
        if not head["items"]:
            print("      (no 정정사항 rows parsed — free-text 정정 or unusual layout)")
        results.append({"rights_type": label, "correction": row["rcept_no"], "corp": row["corp_name"],
                        "corp_code": row["corp_code"], "correction_dt": row["rcept_dt"],
                        "target_report": head["target_report"], "original_rcept_dt": head["original_rcept_dt"],
                        "paired_original": match["rcept_no"] if match else None, "pairing": how,
                        "endpoint": endpoint, "api_probe": probe, "items": head["items"]})

    paired = [r for r in results if r["paired_original"]]
    exactly = [r for r in results if r["pairing"] == "exact 최초제출일"]
    with_items = [r for r in results if r["items"]]
    print(f"\n== pairing: {len(paired)}/{len(results)} paired "
          f"({len(exactly)} by exact 최초제출일); {len(with_items)}/{len(results)} carry a parsed 정정사항 table")
    print("\n== diff-target 항목 frequency (what actually changes):")
    for k, v in item_freq.most_common(30):
        print(f"  {v:>3}  {k}")

    SUMMARY.mkdir(parents=True, exist_ok=True)
    (SUMMARY / "corrections.json").write_text(
        json.dumps({"pairs": results, "item_frequency": item_freq.most_common()}, ensure_ascii=False, indent=1),
        encoding="utf-8")
    print(f"\nsummary -> {SUMMARY / 'corrections.json'}")


if __name__ == "__main__":
    main()
