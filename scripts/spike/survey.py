"""P1.S1 spike: structured-field coverage survey for the 3 MVP rights types.

For each rights type it discovers real 2026 filings via list.json, pulls the
matching 주요사항보고서 *and* 증권신고서 detail endpoints, and reports per-field
coverage (how many sampled rows carry a real value, not "" / "-") with an
evidence rcept_no per field.

Usage:
    python3 scripts/spike/survey.py                 # all three rights types
    python3 scripts/spike/survey.py rights1         # 유증 신주인수권 only
    python3 scripts/spike/survey.py docprobe        # Q3: document API parseability

Writes a machine-readable summary to scripts/spike/samples/_summary/*.json.
Throwaway-grade: no key ever printed, no framework, P2 owns the real collector.
"""

from __future__ import annotations

import concurrent.futures as cf
import json
import re
import sys
from collections import Counter, OrderedDict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dart  # noqa: E402

WINDOWS = [("20260101", "20260331"), ("20260401", "20260630"), ("20260701", "20260818")]
MARKETS = ["Y", "K"]  # KOSPI, KOSDAQ
YEAR = ("20260101", "20260818")
SUMMARY = dart.SAMPLES / "_summary"
IDENT = {"rcept_no", "corp_cls", "corp_code", "corp_name"}
EMPTY = {"", "-", "‐", "–"}


def discover(pblntf_ty: str) -> list[dict]:
    """Every 2026 list.json row of one 공시유형, KOSPI+KOSDAQ (3-month cap → windows)."""
    jobs = [(b, e, m) for b, e in WINDOWS for m in MARKETS]
    out: list[dict] = []
    with cf.ThreadPoolExecutor(6) as ex:
        for got in ex.map(lambda t: dart.filings(t[0], t[1], pblntf_ty=pblntf_ty, corp_cls=t[2], pages=10), jobs):
            out.extend(got)
    return out


def corps_of(rows: list[dict], name_re: str) -> list[str]:
    pat = re.compile(name_re)
    return sorted({r["corp_code"] for r in rows if pat.search(r["report_nm"])})


def pull(endpoint: str, corp_codes: list[str], limit: int = 40) -> list[dict]:
    """Detail-endpoint bodies for up to `limit` corps."""
    def one(cc: str) -> dict:
        return dart.get_json(endpoint, corp_code=cc, bgn_de=YEAR[0], end_de=YEAR[1])
    with cf.ThreadPoolExecutor(6) as ex:
        return list(ex.map(one, corp_codes[:limit]))


def coverage(section_rows: list[dict]) -> "OrderedDict[str, dict]":
    """field -> {n, filled, example, evidence} over the sampled rows."""
    stat: OrderedDict[str, dict] = OrderedDict()
    for row in section_rows:
        for k, v in row.items():
            s = stat.setdefault(k, {"n": 0, "filled": 0, "example": None, "evidence": None})
            s["n"] += 1
            if str(v).strip() not in EMPTY:
                s["filled"] += 1
                if s["example"] is None:
                    s["example"] = str(v).strip().replace("\n", " ⏎ ")[:70]
                    s["evidence"] = row.get("rcept_no")
    return stat


def show(title: str, section_rows: list[dict]) -> dict:
    print(f"\n### {title}  (rows sampled: {len(section_rows)})")
    if not section_rows:
        print("  (no rows)")
        return {}
    stat = coverage(section_rows)
    print(f"  {'field':28} {'filled/n':>10}  {'evidence rcept_no':18} example")
    payload = {}
    for k, s in stat.items():
        if k in IDENT:
            continue
        print(f"  {k:28} {s['filled']:>4}/{s['n']:<5}  {str(s['evidence'] or '-'):18} {s['example'] or ''}")
        payload[k] = s
    return payload


def collect_sections(bodies: list[dict]) -> "OrderedDict[str, list[dict]]":
    sections: OrderedDict[str, list[dict]] = OrderedDict()
    for body in bodies:
        for title, rws in dart.groups(body):
            sections.setdefault(title, []).extend(rws)
    return sections


def survey_endpoint(endpoint: str, corp_codes: list[str], limit: int = 40,
                    keep: "callable | None" = None) -> dict:
    bodies = pull(endpoint, corp_codes, limit)
    sections = collect_sections(bodies)
    if keep:
        sections = OrderedDict((t, [r for r in rws if keep(r)]) for t, rws in sections.items())
    out = {}
    for title, rws in sections.items():
        out[title] = show(f"{endpoint} :: {title}", rws)
    n_rcept = len({r.get("rcept_no") for rws in sections.values() for r in rws})
    print(f"  -> {endpoint}: {len(bodies)} corps queried, {n_rcept} distinct filings")
    return {"sections": out, "corps_queried": len(bodies), "filings": n_rcept}


def rights1(b_rows: list[dict], c_rows: list[dict]) -> dict:
    print("\n" + "=" * 100)
    print("① 유증 신주인수권 — 주요사항보고서(유상증자결정) piicDecsn + 증권신고서(지분증권) estkRs")
    print("=" * 100)
    res = {}
    corps = corps_of(b_rows, r"유상증자결정")
    n_rows = len([r for r in b_rows if "유상증자결정" in r["report_nm"]])
    print(f"\n2026 유상증자결정 filings: {n_rows} rows / {len(corps)} corps")
    res["piicDecsn"] = survey_endpoint("piicDecsn", corps, limit=40)

    bodies = pull("piicDecsn", corps, 40)
    methods = Counter(r.get("ic_mthn", "?") for b in bodies for r in dart.rows(b))
    print("\n  ic_mthn (증자방식) distribution over sampled rows:")
    for k, v in methods.most_common():
        print(f"    {v:>3}  {k}")
    res["ic_mthn_distribution"] = dict(methods)

    eq_corps = corps_of(c_rows, r"증권신고서\(지분증권\)")
    print(f"\n2026 증권신고서(지분증권) filings: "
          f"{len([r for r in c_rows if '증권신고서(지분증권)' in r['report_nm']])} rows / {len(eq_corps)} corps")
    res["estkRs"] = survey_endpoint("estkRs", eq_corps, limit=45)

    # Q1: does asstd (배정기준일) populate for 주주배정 filings?
    bodies = pull("estkRs", eq_corps, 45)
    kind_by_rcept, asstd_by_rcept = {}, {}
    for body in bodies:
        for title, rws in dart.groups(body):
            for r in rws:
                if title == "증권의종류" and r.get("slmthn"):
                    kind_by_rcept[r["rcept_no"]] = r["slmthn"]
                if title == "일반사항":
                    asstd_by_rcept[r["rcept_no"]] = (r.get("asstd", "-"), r.get("corp_name"), r.get("rpt_rcpn"))
    shareholder = {k: v for k, v in kind_by_rcept.items() if "주주배정" in v}
    filled = [k for k in shareholder if asstd_by_rcept.get(k, ("-",))[0] not in EMPTY]
    print(f"\n  Q1 — 주주배정-type 증권신고서 filings sampled: {len(shareholder)}; "
          f"with asstd(배정기준일) populated: {len(filled)}")
    for k in sorted(shareholder)[:12]:
        a, name, rpt = asstd_by_rcept.get(k, ("-", "?", "-"))
        print(f"    {k}  {str(name):14} asstd={a:20} slmthn={shareholder[k]:28} rpt_rcpn={rpt}")
    res["q1"] = {"shareholder_filings": len(shareholder), "asstd_filled": len(filled),
                 "samples": {k: {"asstd": asstd_by_rcept.get(k, ("-",))[0], "slmthn": shareholder[k],
                                 "rpt_rcpn": asstd_by_rcept.get(k, ("-", "", "-"))[2]}
                             for k in sorted(shareholder)}}
    return res


def rights2(b_rows: list[dict], c_rows: list[dict]) -> dict:
    print("\n" + "=" * 100)
    print("② CB·EB 오버행 — cvbdIsDecsn / exbdIsDecsn + 증권신고서(채무증권) bdRs")
    print("=" * 100)
    res = {}
    cb = corps_of(b_rows, r"전환사채권발행결정")
    eb = corps_of(b_rows, r"교환사채권발행결정")
    print(f"\n2026 전환사채권발행결정: {len([r for r in b_rows if '전환사채권발행결정' in r['report_nm']])} rows / {len(cb)} corps"
          f" | 교환사채권발행결정: {len([r for r in b_rows if '교환사채권발행결정' in r['report_nm']])} rows / {len(eb)} corps")
    res["cvbdIsDecsn"] = survey_endpoint("cvbdIsDecsn", cb, limit=35)
    res["exbdIsDecsn"] = survey_endpoint("exbdIsDecsn", eb, limit=20)
    bd = corps_of(c_rows, r"증권신고서\(채무증권\)")
    res["bdRs"] = survey_endpoint("bdRs", bd, limit=25)
    return res


def rights3(b_rows: list[dict], c_rows: list[dict]) -> dict:
    print("\n" + "=" * 100)
    print("③ 매수청구권 — cmpMgDecsn(회사합병) + 증권신고서(합병) mgRs  [siblings: 분할합병·주식교환]")
    print("=" * 100)
    res = {}
    mg = corps_of(b_rows, r"회사합병결정")
    print(f"\n2026 회사합병결정: {len([r for r in b_rows if '회사합병결정' in r['report_nm']])} rows / {len(mg)} corps")
    res["cmpMgDecsn"] = survey_endpoint("cmpMgDecsn", mg, limit=35)
    mgrs = corps_of(c_rows, r"증권신고서\(합병\)")
    res["mgRs"] = survey_endpoint("mgRs", mgrs, limit=20)
    for ep, pat in (("cmpDvmgDecsn", r"회사분할합병결정"), ("stkExtrDecsn", r"주식교환·이전결정|주식교환.이전결정")):
        corps = corps_of(b_rows, pat)
        if corps:
            res[ep] = survey_endpoint(ep, corps, limit=10)
    return res


# --- Q3: is the document API (본문 ZIP/XML) parseable enough for LLM extraction? ---
SERVICE_TERMS = ["신주인수권증서", "매매기간", "상장", "초과청약", "실권주", "청약", "배정기준일", "발행가액",
                 "리픽싱", "전환가액", "조정", "콜옵션", "보호예수", "매수청구", "반대의사", "통지"]


def docprobe(rcept_nos: list[str]) -> dict:
    print("\n" + "=" * 100)
    print("Q3 — document API (본문 ZIP) parseability probe")
    print("=" * 100)
    out = {}
    for rn in rcept_nos:
        try:
            members = dart.document_members(rn)
        except Exception as exc:  # noqa: BLE001
            print(f"\n{rn}: fetch failed — {type(exc).__name__}")
            out[rn] = {"error": type(exc).__name__}
            continue
        if not members:
            print(f"\n{rn}: response is not a ZIP (likely an error XML)")
            out[rn] = {"zip": False}
            continue
        text = dart.document_text(rn)
        enc = re.search(r'encoding="([^"]+)"', text[:200])
        tags = Counter(re.findall(r"<([A-Z-]{2,})[ >]", text))
        stripped = re.sub(r"<[^>]+>", " ", text)
        stripped = re.sub(r"\s+", " ", stripped)
        hits = {t: stripped.count(t) for t in SERVICE_TERMS if t in stripped}
        print(f"\n{rn}: ZIP ok, members={[(m, s) for m, s in members]}")
        print(f"  xml declared encoding={enc.group(1) if enc else '?'} | chars={len(text):,} | text chars={len(stripped):,}")
        print(f"  top tags: {', '.join(f'{t}×{c}' for t, c in tags.most_common(10))}")
        print(f"  service-term hits: {hits}")
        out[rn] = {"zip": True, "members": members, "encoding": enc.group(1) if enc else None,
                   "chars": len(text), "text_chars": len(stripped),
                   "top_tags": tags.most_common(12), "term_hits": hits}
    return out


# --- 본문 label stability: can a deterministic table-label parser carry the skeleton? ---
LABELS = ["신주배정기준일", "1주당 신주배정주식수", "청약예정일", "납입일", "실권주 처리계획",
          "신주의 상장예정일", "대표주관회사", "신주인수권양도여부", "신주인수권증서의 상장여부",
          "신주인수권증서의 매매"]
PROSE = ["신주인수권증서 상장예정기간", "상장예정기간", "초과청약", "실권주", "청약취급처", "매매기간"]


def labelscan(limit: int = 8) -> dict:
    """How stable are the 유증 주요사항보고서 본문 labels across real 주주배정 filings?"""
    print("\n" + "=" * 100)
    print("본문 label-stability scan — 주주배정 유상증자 주요사항보고서")
    print("=" * 100)
    b_rows = discover("B")
    piic = [r for r in b_rows if "주요사항보고서(유상증자결정)" in r["report_nm"]]
    corps = sorted({r["corp_code"] for r in piic})
    bodies = pull("piicDecsn", corps, 60)
    picked = [r for b in bodies for r in dart.rows(b) if "주주배정" in r.get("ic_mthn", "")][:limit]
    print(f"주주배정-type filings found among sampled corps: {len(picked)} (scanning {min(limit, len(picked))})")
    out = {}
    for row in picked:
        rn = row["rcept_no"]
        flat = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", dart.document_text(rn)))
        hit = {label: (label.replace(" ", "") in flat.replace(" ", "")) for label in LABELS + PROSE}
        m = re.search(r"신주인수권증서\s*상장\s*(?:예정)?기간\s*:?\s*([^)]{0,60})", flat)
        print(f"\n  {rn} {row['corp_name']} ({row['ic_mthn']}) chars={len(flat):,}")
        print(f"    labels present: {sum(1 for k in LABELS if hit[k])}/{len(LABELS)}"
              f" | prose terms: {[k for k in PROSE if hit[k]]}")
        if m:
            print(f"    증서 매매기간 in prose -> {m.group(1).strip()[:60]}")
        out[rn] = {"corp": row["corp_name"], "ic_mthn": row["ic_mthn"], "chars": len(flat),
                   "labels": hit, "certificate_period": m.group(1).strip()[:60] if m else None}
    return out


def population() -> dict:
    """2026 event universe per rights type — the size input to the P1.S2 scope call."""
    print("\n" + "=" * 100)
    print("2026 event universe (2026-01-01~08-18, KOSPI+KOSDAQ, every corp with such a filing)")
    print("=" * 100)
    b_rows = discover("B")
    out = {}

    corps = corps_of(b_rows, r"유상증자결정")
    rws = [r for b in pull("piicDecsn", corps, len(corps)) for r in dart.rows(b)]
    meth = Counter(r.get("ic_mthn", "?") for r in rws)
    holder = sum(v for k, v in meth.items() if "주주배정" in k)
    print(f"\n① 유상증자 결정 (piicDecsn): {len(rws)} distinct reports across {len(corps)} corps")
    for k, v in meth.most_common():
        print(f"    {v:>4}  {k}")
    print(f"  -> 주주배정 계열 (신주인수권증서가 발생하는 유형): {holder} "
          f"({holder / max(1, len(rws)):.0%} of 유상증자 reports)")
    out["piicDecsn"] = {"reports": len(rws), "corps": len(corps), "ic_mthn": dict(meth), "주주배정": holder}

    corps = corps_of(b_rows, r"회사합병결정")
    rws = [r for b in pull("cmpMgDecsn", corps, len(corps)) for r in dart.rows(b)]
    stn = Counter(r.get("mg_stn", "?") for r in rws)
    with_price = [r for r in rws if str(r.get("aprskh_plnprc", "-")).strip() not in EMPTY]
    with_period = [r for r in rws if str(r.get("mgsc_aprskh_expd_bgd", "-")).strip() not in EMPTY]
    print(f"\n③ 회사합병 결정 (cmpMgDecsn): {len(rws)} distinct reports across {len(corps)} corps")
    for k, v in stn.most_common():
        print(f"    {v:>4}  {k}")
    print(f"  -> 매수청구 예정가격(aprskh_plnprc) present: {len(with_price)}; "
          f"행사기간(mgsc_aprskh_expd_bgd) present: {len(with_period)}")
    print("  -> low fill is semantic, not a data gap: 소규모/간이합병 grants no 매수청구권")
    out["cmpMgDecsn"] = {"reports": len(rws), "corps": len(corps), "mg_stn": dict(stn),
                         "with_aprskh_price": len(with_price), "with_aprskh_period": len(with_period)}

    for label, pat, ep in (("② CB", r"전환사채권발행결정", "cvbdIsDecsn"), ("② EB", r"교환사채권발행결정", "exbdIsDecsn")):
        corps = corps_of(b_rows, pat)
        rws = [r for b in pull(ep, corps, len(corps)) for r in dart.rows(b)]
        print(f"\n{label} ({ep}): {len(rws)} distinct reports across {len(corps)} corps")
        out[ep] = {"reports": len(rws), "corps": len(corps)}
    return out


def main() -> None:
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    SUMMARY.mkdir(parents=True, exist_ok=True)

    if what == "population":
        payload = population()
        (SUMMARY / "population.json").write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
        return

    if what == "labelscan":
        payload = labelscan(int(sys.argv[2]) if len(sys.argv) > 2 else 8)
        (SUMMARY / "labelscan.json").write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
        return

    if what == "docprobe":
        nos = sys.argv[2:] or ["20260814004100", "20260724000546", "20260630000123"]
        payload = docprobe(nos)
        (SUMMARY / "docprobe.json").write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
        return

    b_rows = discover("B")  # 주요사항보고
    c_rows = discover("C")  # 발행공시 (증권신고서 등)
    print(f"discovery: pblntf_ty=B rows={len(b_rows)} | pblntf_ty=C rows={len(c_rows)} "
          f"(2026-01-01~08-18, KOSPI+KOSDAQ, 3-month windows)")

    payload = {}
    if what in ("all", "rights1"):
        payload["rights1"] = rights1(b_rows, c_rows)
    if what in ("all", "rights2"):
        payload["rights2"] = rights2(b_rows, c_rows)
    if what in ("all", "rights3"):
        payload["rights3"] = rights3(b_rows, c_rows)
    (SUMMARY / f"survey_{what}.json").write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\nsummary -> {SUMMARY / f'survey_{what}.json'}")


if __name__ == "__main__":
    main()
