"""The accuracy report: two error directions, one honest denominator each.

Precision alone would flatter §3.6's design, because the gate's whole job is to
delete the rows precision would have punished. So this report states both:

**(a) what the product shows.** Of the rows that passed their gate (or are an
honest ``추후결정``), how many did the judge call correct? That is the
number the pitch may quote — **beside the judge's identity**, which the report
prints from ``labels.json`` itself (N89: this repo's labels are Claude-judged
cross-model, not human ground truth, and a rate without that word means
something else).

**(b) what the gate costs.** Of the rows the gate **blocked**, how many did the
judge call correct readings all along? Those are right answers
the product withheld — S8 priced one such pattern at ▷ 49.2억원, 6.4 % of the
headline (N76). A gate with a low over-block rate is cheap; a gate with a high
one is buying trust with coverage.

Three disciplines the numbers depend on:

* only ``pick == "random"`` rows enter a rate. The forced hard cases are
  deliberately the corpus's worst rows and are listed individually instead.
* ``skip`` leaves the denominator; the count is printed, so a thin sample cannot
  hide behind a good-looking rate.
* every rate carries a **95 % Wilson interval**. At n ≈ 20 per field the interval
  is wide, and saying so is the difference between evidence and a slogan.

Reads two JSON files and nothing else: no database, no network, no model.
"""

from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass, field

from mijual.evalset.labels import Labels
from mijual.evalset.sample import EvalSample, Row

__all__ = ["EvalReport", "FieldScore", "build_report", "wilson_interval"]

#: 95 % two-sided normal quantile.
Z95 = 1.959964


def wilson_interval(successes: int, total: int, z: float = Z95) -> tuple[float, float] | None:
    """95 % Wilson score interval — correct at the small n an evalset actually has.

    The textbook normal interval is wrong here (it can exceed 1 and collapses to
    zero width at p = 1, which is exactly this corpus's common case). Wilson does
    not, needs no library, and is the honest way to report ``21/21``.
    """
    if total <= 0:
        return None
    p = successes / total
    denominator = 1 + z * z / total
    centre = (p + z * z / (2 * total)) / denominator
    margin = z * math.sqrt(p * (1 - p) / total + z * z / (4 * total * total)) / denominator
    return (max(0.0, centre - margin), min(1.0, centre + margin))


def _pct(value: float | None) -> str:
    return "—" if value is None else f"{value * 100:.1f}%"


@dataclass
class Bucket:
    """Labelled rows of one kind (shown / blocked) for one field."""

    correct: int = 0
    partial: int = 0
    wrong: int = 0
    skipped: int = 0
    unlabelled: int = 0

    @property
    def judged(self) -> int:
        return self.correct + self.partial + self.wrong

    @property
    def strict(self) -> float | None:
        """``partial`` counts as a miss — the number to quote."""
        return self.correct / self.judged if self.judged else None

    @property
    def lenient(self) -> float | None:
        """``partial`` counts as a hit — the upper edge, always stated beside it."""
        return (self.correct + self.partial) / self.judged if self.judged else None

    def interval(self) -> tuple[float, float] | None:
        return wilson_interval(self.correct, self.judged)

    def add(self, label: str | None) -> None:
        if label is None:
            self.unlabelled += 1
        elif label == "skip":
            self.skipped += 1
        else:
            setattr(self, label, getattr(self, label) + 1)


@dataclass
class FieldScore:
    """One field's two directions, plus its corpus-wide gate-block rate."""

    field_key: str
    field_ko: str
    order: int
    shown: Bucket = field(default_factory=Bucket)
    blocked: Bucket = field(default_factory=Bucket)
    corpus_total: int = 0
    corpus_blocked: int = 0
    corpus_reasons: dict = field(default_factory=dict)

    @property
    def block_rate(self) -> float | None:
        return self.corpus_blocked / self.corpus_total if self.corpus_total else None

    @property
    def over_block_rate(self) -> float | None:
        """Share of gate-blocked rows the judge called correct anyway."""
        return self.blocked.correct / self.blocked.judged if self.blocked.judged else None

    @property
    def over_blocked_estimate(self) -> float | None:
        """▷ how many corpus rows that rate implies were withheld though correct."""
        rate = self.over_block_rate
        return None if rate is None else rate * self.corpus_blocked


@dataclass
class EvalReport:
    sample: EvalSample
    labels: Labels
    scores: dict[str, FieldScore] = field(default_factory=dict)
    hard_cases: list[tuple[Row, str | None]] = field(default_factory=list)
    coverage: Counter = field(default_factory=Counter)

    # -- corpus-level aggregates ------------------------------------------
    @property
    def ordered(self) -> list[FieldScore]:
        return sorted(self.scores.values(), key=lambda s: (s.order, s.field_key))

    def totals(self) -> tuple[Bucket, Bucket]:
        shown, blocked = Bucket(), Bucket()
        for score in self.scores.values():
            for source, target in ((score.shown, shown), (score.blocked, blocked)):
                for name in ("correct", "partial", "wrong", "skipped", "unlabelled"):
                    setattr(target, name, getattr(target, name) + getattr(source, name))
        return shown, blocked

    def render(self) -> str:
        shown, blocked = self.totals()
        lines: list[str] = []
        lines.append("## 추출 정확도 (P2.S9 evalset)")
        lines.append("")
        lines.append(
            f"- 표본: **{self.sample.units}건의 공시 / {len(self.sample.rows)} 필드 행** "
            f"(seed {self.sample.seed}, 생성 {self.sample.generated_at})"
        )
        lines.append(
            f"- 라벨: {len(self.labels.labelled)} / {len(self.sample.rows)} 행 "
            f"({self.coverage['random']} random · {self.coverage['forced']} hard case · "
            f"{self.coverage['booster']} booster)"
        )
        lines.append(f"- 판정 출처: {_provenance(self.labels)}")
        lines.append(
            f"- 무작위 표본 기준 노출 필드 정밀도: **{_pct(shown.strict)}** "
            f"({shown.correct}/{shown.judged}, 95% CI {_interval(shown.interval())}), "
            f"partial 포함 시 {_pct(shown.lenient)}"
        )
        lines.append(
            f"- 게이트가 차단한 행 중 판정자가 '맞다'고 본 비율(과차단): "
            f"**{_pct(_rate(blocked.correct, blocked.judged))}** "
            f"({blocked.correct}/{blocked.judged})"
        )
        if shown.skipped or blocked.skipped:
            lines.append(f"- 판단 보류(skip): {shown.skipped + blocked.skipped} 행 — 분모에서 제외")
        lines.append("")
        lines.append("### 필드별")
        lines.append("")
        lines.append(
            "| 필드 | 노출 n | 정밀도 (strict) | 95% CI | partial 포함 | "
            "차단 n | 과차단 | 코퍼스 게이트 차단율 |"
        )
        lines.append("|---|---|---|---|---|---|---|---|")
        for score in self.ordered:
            lines.append(
                "| {name} | {n} | {strict} | {ci} | {lenient} | {bn} | {over} | "
                "{rate} ({blocked}/{total}) |".format(
                    name=score.field_ko,
                    n=score.shown.judged,
                    strict=_pct(score.shown.strict),
                    ci=_interval(score.shown.interval()),
                    lenient=_pct(score.shown.lenient),
                    bn=score.blocked.judged,
                    over=_pct(score.over_block_rate),
                    rate=_pct(score.block_rate),
                    blocked=score.corpus_blocked,
                    total=score.corpus_total,
                )
            )
        lines.append("")
        lines.append("### 게이트가 차단한 이유 (코퍼스 전체)")
        reasons: Counter = Counter()
        for score in self.scores.values():
            for code, count in score.corpus_reasons.items():
                reasons[code] += count
        for code, count in reasons.most_common():
            lines.append(f"- `{code}` × {count}")
        lines.append("")
        recall = self.sample.correction_recall
        lines.append("### 정정 해석 재현율 프록시 (S4가 저장한 결정론적 대조, 라벨 불필요)")
        lines.append(
            f"- 결정론적 정정사항 {recall.get('deterministic_rows')}행 중 "
            f"모델이 언급하지 않은 행 {recall.get('uncovered')} → 재현율 "
            f"{_pct(recall.get('recall'))} ({recall.get('records')} 건)"
        )
        lines.append(
            f"- 표가 뒷받침하지 않는 모델 변경(unsupported): {recall.get('unsupported')} / "
            f"{recall.get('model_changes')}"
        )
        without = recall.get("records_without_parsed_rows")
        if without:
            lines.append(
                f"- 정정사항 표 자체가 파싱되지 않은 건 {without} — 위 분모에서 제외 "
                "(게이트가 `no_correction_rows`로 이미 차단)"
            )
        lines.append("")
        lines.append("### 하드 케이스 (의도적으로 전수 포함 — 위 비율에는 들어가지 않음)")
        for row, label in sorted(self.hard_cases, key=lambda rl: (rl[0].hard_case, rl[0].row_id)):
            lines.append(
                f"- `{row.hard_case}` {row.corp_name} {row.rcept_no} {row.field_ko} → "
                f"라벨 **{label or '미기입'}**"
            )
        return "\n".join(lines)


def _provenance(labels: Labels) -> str:
    """The judge line, read off the artifact — never a constant in this file.

    A hardcoded sentence would go on printing "hand-labelled" after the labels
    stopped being hand-made (N95). What the report says about its own judge is
    therefore exactly what ``labels.json`` carries, and a file that carries
    nothing says so.
    """
    stamp = labels.provenance
    if stamp is None:
        return "**미기재** — labels.json에 판정 출처가 없습니다 (`import --judged-by …`로 재수입)"
    when = f" · 기록 {stamp.imported_at}" if stamp.imported_at else ""
    return f"**{stamp.judge}** · 근거: {stamp.basis}{when}"


def _rate(numerator: int, denominator: int) -> float | None:
    return numerator / denominator if denominator else None


def _interval(bounds: tuple[float, float] | None) -> str:
    return "—" if bounds is None else f"[{bounds[0] * 100:.0f}–{bounds[1] * 100:.0f}%]"


def build_report(sample: EvalSample, labels: Labels) -> EvalReport:
    """Score a labelled sample. Pure arithmetic over two files."""
    report = EvalReport(sample=sample, labels=labels)
    for row in sample.rows:
        label = labels.labelled.get(row.row_id)
        if label is not None:
            report.coverage[row.pick] += 1
        if row.hard_case:
            report.hard_cases.append((row, label))
        if row.pick != "random":
            continue
        stats = sample.field_stats.get(row.field_key, {})
        score = report.scores.setdefault(
            row.field_key,
            FieldScore(
                field_key=row.field_key,
                field_ko=row.field_ko,
                order=row.field_order,
                corpus_total=stats.get("total", 0),
                corpus_blocked=stats.get("blocked", 0),
                corpus_reasons=dict(stats.get("reasons", {})),
            ),
        )
        (score.blocked if row.gate_blocked else score.shown).add(label)
    return report
