"""Mijual data & extraction pipeline (P2).

Layout:
    mijual.config   — process settings + secret handling (never echoed)
    mijual.dart     — OpenDART client (ported from the P1 spike, cache-compatible)
    mijual.db       — SQLAlchemy models (event / version / snapshot) + session helpers
    mijual.collect  — ① 유증 / ③ 매수청구 collection: discovery, 정정 pairing, filters
    mijual.smoke    — offline end-to-end smoke run
"""

__version__ = "0.1.0"
