#!/usr/bin/env python3
"""Generate the Hero orbiter's `@keyframes orbit` block (`P4.F11`).

The hero's orbiting star (R2: "orbiting star on offset-path, 26s") used to ride
an `offset-path: path(...)` ellipse by animating `offset-distance: 0% -> 100%`.
`offset-distance` is the one property on the landing Chrome cannot composite
(`P4.F7` measured it in a trace: `compositeFailed`, `unsupportedProperties:
["offset-distance"]`), and that single animation alone keeps the renderer's main
thread producing a frame 60 times a second for as long as the tab is open.

The motion is therefore re-expressed as a composited `transform` animation over
the SAME curve, in the same direction, from the same start point, at the same
constant ARC speed. The keyframe stops are samples of that curve placed at
percentages proportional to arc length, so the speed profile is unchanged --
constant along the arc, exactly as `offset-distance` makes it. Constant ANGULAR
speed (a rotated, scaled circle) is NOT the same motion and is not a shortcut
worth taking: it puts the star up to 83px from where it belongs.

**The curve is the browser's, not the textbook's.** An SVG `A` command is not
drawn as a true ellipse: every engine decomposes it into cubic Beziers, one per
90 degrees, by the SVG spec's own construction (control handles at 4/3*tan(dt/4)
of the tangent). That curve bulges ~0.05px outside the exact ellipse at the
minor axis, and it is what the reader sees today, so it is what this script
samples. Measured against Chrome 152: the decomposition below reproduces the
rendered path to <0.09px, where the exact ellipse is 0.05px off it everywhere.

    python3 frontend/scripts/gen_orbiter_keyframes.py            # the CSS block
    python3 frontend/scripts/gen_orbiter_keyframes.py --report   # the proof

Standard library only, deterministic, no arguments: run it again and the bytes
are the same. What it prints is the provenance of coordinates in
`components/landing/Hero.module.css` that no reader could derive by eye.
"""

from __future__ import annotations

import argparse
import bisect
import math

# --- the geometry, transcribed from Hero.module.css --------------------------
#
#   .orbiter { width: 5px; height: 5px;
#              offset-path: path("M -490 0 A 490 140 0 1 0 490 0
#                                          A 490 140 0 1 0 -490 0"); }
#
# Two 180-degree arcs of one ellipse centred on the zero-size `.track` box:
# rx 490, ry 140 (the 980x280 `.ellipseSmall` ring), starting at the LEFT end of
# the major axis and running counter-clockwise on screen (sweep-flag 0: left ->
# bottom -> right -> top -> left).  `offset-anchor` defaults to the element's
# transform-origin, i.e. its centre, so a `transform` that reproduces the motion
# translates the box by the curve point MINUS half the dot.
RX = 490.0
RY = 140.0
DOT = 5.0
ARC_SEGMENTS = 4  # 90 degrees each: what the SVG spec's arc decomposition emits

# `P4.F11` requires the star to stay within 0.25px of where `offset-distance`
# put it, at every instant and INCLUDING the 0.1px coordinate rounding. The stop
# count is solved against the tighter TARGET so the shipped block keeps a margin;
# BUDGET is the requirement and is asserted, never merely intended. 0.18px costs
# 89 stops / 5.3kB raw where 0.25px would cost 77 / 4.6kB -- 0.7kB for a third
# more headroom, which is the right side of that trade.
BUDGET_PX = 0.25
TARGET_PX = 0.18

COORD_DECIMALS = 1  # coordinates rounded to 0.1px
PCT_DECIMALS = 4  # 0.0001% of 26s = 26 microseconds

_PER_SEGMENT = 60_000  # t samples per cubic for the arc-length table


def _cubics() -> list[tuple[tuple[float, float], ...]]:
    """The SVG spec's decomposition of the two `A` commands: ARC_SEGMENTS cubic
    Beziers of 90 degrees each, walked from the left end of the major axis in
    the direction sweep-flag 0 gives."""

    def ellipse(deg: float) -> tuple[float, float]:
        r = math.radians(deg)
        return (RX * math.cos(r), RY * math.sin(r))

    def derivative(deg: float) -> tuple[float, float]:
        r = math.radians(deg)
        return (-RX * math.sin(r), RY * math.cos(r))

    span = -360.0 / ARC_SEGMENTS
    alpha = 4 / 3 * math.tan(math.radians(span) / 4)
    out = []
    for k in range(ARC_SEGMENTS):
        a, b = 180.0 + k * span, 180.0 + (k + 1) * span
        p0, p3 = ellipse(a), ellipse(b)
        d0, d3 = derivative(a), derivative(b)
        out.append(
            (
                p0,
                (p0[0] + alpha * d0[0], p0[1] + alpha * d0[1]),
                (p3[0] - alpha * d3[0], p3[1] - alpha * d3[1]),
                p3,
            )
        )
    return out


CUBICS = _cubics()


def _bezier(c, t: float) -> tuple[float, float]:
    m = 1 - t
    return (
        m * m * m * c[0][0] + 3 * m * m * t * c[1][0] + 3 * m * t * t * c[2][0] + t * t * t * c[3][0],
        m * m * m * c[0][1] + 3 * m * m * t * c[1][1] + 3 * m * t * t * c[2][1] + t * t * t * c[3][1],
    )


def _radius(c, t: float) -> float:
    """The osculating circle's radius: ~40px at the major-axis tips, ~1715px at
    the flat sides. That 43x range is why stops must be placed adaptively."""
    m = 1 - t
    dx = 3 * (m * m * (c[1][0] - c[0][0]) + 2 * m * t * (c[2][0] - c[1][0]) + t * t * (c[3][0] - c[2][0]))
    dy = 3 * (m * m * (c[1][1] - c[0][1]) + 2 * m * t * (c[2][1] - c[1][1]) + t * t * (c[3][1] - c[2][1]))
    ddx = 6 * (m * (c[2][0] - 2 * c[1][0] + c[0][0]) + t * (c[3][0] - 2 * c[2][0] + c[1][0]))
    ddy = 6 * (m * (c[2][1] - 2 * c[1][1] + c[0][1]) + t * (c[3][1] - 2 * c[2][1] + c[1][1]))
    cross = abs(dx * ddy - dy * ddx)
    return math.hypot(dx, dy) ** 3 / cross if cross else float("inf")


def _table():
    """One dense walk of the whole path: cumulative arc length, position, and
    the sampling measure ds/sqrt(R). A chord of length c across a curve of
    radius R deviates from it by c^2/(8R) at its middle, so an equal-deviation
    chord is proportional to sqrt(R) -- spacing stops evenly in that measure is
    what puts them densely at the tips and sparsely on the flat sides. Only the
    SHAPE of the measure matters; the stop count is solved below, against the
    measured deviation itself."""
    arc = [0.0]
    measure = [0.0]
    pts = [CUBICS[0][0]]
    for c in CUBICS:
        prev = _bezier(c, 0.0)
        for i in range(1, _PER_SEGMENT + 1):
            t = i / _PER_SEGMENT
            p = _bezier(c, t)
            step = math.dist(prev, p)
            arc.append(arc[-1] + step)
            measure.append(measure[-1] + step / math.sqrt(_radius(c, t - 0.5 / _PER_SEGMENT)))
            pts.append(p)
            prev = p
    return arc, measure, pts


_ARC, _MEASURE, _PTS = _table()
TOTAL_LEN = _ARC[-1]
QUARTER = len(_PTS) // 4  # index of the quarter-lap point (one cubic)


def _index(table: list[float], value: float) -> float:
    """Fractional index at which a monotone table reaches `value`."""
    i = bisect.bisect_left(table, value)
    if i <= 0:
        return 0.0
    if i >= len(table):
        return float(len(table) - 1)
    lo, hi = table[i - 1], table[i]
    return (i - 1) + (0.0 if hi == lo else (value - lo) / (hi - lo))


def _interp(table: list, x: float):
    i = int(x)
    if i >= len(table) - 1:
        return table[-1]
    f = x - i
    a, b = table[i], table[i + 1]
    return (a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f) if isinstance(a, tuple) else a + (b - a) * f


def point_at_arc(arc: float) -> tuple[float, float]:
    return _interp(_PTS, _index(_ARC, arc))


def stops(n_quarter: int):
    """(percent, x, y) for one lap. The first quadrant is sampled evenly in the
    measure and the other three are its mirror images, so the four quadrants are
    exactly symmetric and the lap closes on its own start."""
    quarter_measure = _MEASURE[QUARTER]
    quarter_arc = _ARC[QUARTER]
    arcs_q = [
        _interp(_ARC, _index(_MEASURE, quarter_measure * k / n_quarter))
        for k in range(n_quarter + 1)
    ]
    arcs_q[0], arcs_q[-1] = 0.0, quarter_arc

    lap: list[float] = []
    for quadrant in range(4):
        base = quadrant * quarter_arc
        if quadrant % 2 == 0:
            lap += [base + a for a in arcs_q[:-1]]
        else:
            lap += [base + (quarter_arc - a) for a in reversed(arcs_q[1:])]
    lap.append(TOTAL_LEN)

    return [(100.0 * a / TOTAL_LEN, *point_at_arc(a)) for a in lap]


def rounded(raw):
    return [
        (round(p, PCT_DECIMALS), round(x - DOT / 2, COORD_DECIMALS), round(y - DOT / 2, COORD_DECIMALS))
        for p, x, y in raw
    ]


def true_at(u: float) -> tuple[float, float]:
    """The exact `offset-distance` position at lap fraction `u`: the point at
    arc length u*L on the browser's own curve."""
    x, y = point_at_arc(u * TOTAL_LEN)
    return (x - DOT / 2, y - DOT / 2)


def max_deviation(pts, per_segment: int = 60):
    """Worst distance, at the SAME instant, between the keyframed position and
    the true one -- normal (chord) and tangential (timing) error together."""
    worst, where = 0.0, 0.0
    for i in range(len(pts) - 1):
        p0, x0, y0 = pts[i]
        p1, x1, y1 = pts[i + 1]
        for k in range(per_segment + 1):
            f = k / per_segment
            tx, ty = true_at((p0 + (p1 - p0) * f) / 100.0)
            d = math.hypot(x0 + (x1 - x0) * f - tx, y0 + (y1 - y0) * f - ty)
            if d > worst:
                worst, where = d, (p0 + (p1 - p0) * f) / 100.0
    return worst, where


def css(pts) -> str:
    def fmt(v: float) -> str:
        s = f"{v:.{COORD_DECIMALS}f}"
        return s[:-2] if s.endswith(".0") else s

    def pct(v: float) -> str:
        s = f"{v:.{PCT_DECIMALS}f}".rstrip("0").rstrip(".")
        return s or "0"

    lines = ["@keyframes orbit {"]
    for p, x, y in pts:
        lines.append(f"  {pct(p)}% {{ transform: translate3d({fmt(x)}px, {fmt(y)}px, 0); }}")
    lines.append("}")
    return "\n".join(lines)


def solve():
    """The smallest stop count whose measured deviation fits TARGET_PX."""
    n = 2
    while True:
        pts = rounded(stops(n))
        worst, _ = max_deviation(pts, per_segment=16)
        if worst <= TARGET_PX:
            worst, _ = max_deviation(pts, per_segment=200)
            assert worst <= BUDGET_PX, f"{worst} px exceeds the {BUDGET_PX} px budget"
            return n, pts
        n += 1


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", action="store_true")
    args = ap.parse_args()

    n, pts = solve()
    block = css(pts)
    if not args.report:
        print(block)
        return

    worst, where = max_deviation(pts, per_segment=200)
    seg = [math.hypot(pts[i + 1][1] - pts[i][1], pts[i + 1][2] - pts[i][2]) for i in range(len(pts) - 1)]
    print(f"curve              SVG arc -> {ARC_SEGMENTS} cubic Beziers, rx={RX:g} ry={RY:g}, dot {DOT:g}px (anchor = centre)")
    print(f"perimeter          {TOTAL_LEN:.4f} px    (quarter {TOTAL_LEN / 4:.4f})")
    print(f"vs exact ellipse   perimeter {TOTAL_LEN - 2135.1253:+.4f} px (the arc's cubics bulge outside it)")
    print(f"curvature radius   {_radius(CUBICS[0], 0.0):.2f} px at the tips, {_radius(CUBICS[0], 1.0):.2f} px at the flat sides")
    print(f"stops              {len(pts)}  ({n} per quadrant + the closing 100%)")
    print(f"chord length       {min(seg):.2f} .. {max(seg):.2f} px")
    print(f"budget             {BUDGET_PX} px required, {TARGET_PX} px solved for "
          f"(coordinates rounded to {10 ** -COORD_DECIMALS:g} px)")
    print(f"MAX DEVIATION      {worst:.4f} px, at lap fraction {where:.4f} (t = {where * 26:.3f}s of 26s)")
    print(f"css                {len(block.encode()):,} bytes raw")
    print()
    print("t (s)     keyframed (x,y)         true (x,y)              |d|")
    for k in range(13):
        u = k / 12
        ax, ay = _keyframed(pts, u)
        tx, ty = true_at(u)
        print(f"{u * 26:6.3f}   ({ax:9.3f},{ay:8.3f})   ({tx:9.3f},{ty:8.3f})   {math.hypot(ax - tx, ay - ty):.4f}")


def _keyframed(pts, u: float) -> tuple[float, float]:
    p = u * 100.0
    i = min(max(bisect.bisect_right([s[0] for s in pts], p) - 1, 0), len(pts) - 2)
    p0, x0, y0 = pts[i]
    p1, x1, y1 = pts[i + 1]
    f = 0.0 if p1 == p0 else (p - p0) / (p1 - p0)
    return (x0 + (x1 - x0) * f, y0 + (y1 - y0) * f)


if __name__ == "__main__":
    main()
