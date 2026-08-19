"""OpenDART access layer (ported from ``scripts/spike/dart.py``)."""

from mijual.dart.client import (
    BASE_URL,
    CacheMiss,
    DartClient,
    DartError,
    DartFetchError,
    NotAZipError,
    decode_document,
    groups,
    rows,
    safe_query,
    status,
)

__all__ = [
    "BASE_URL",
    "CacheMiss",
    "DartClient",
    "DartError",
    "DartFetchError",
    "NotAZipError",
    "decode_document",
    "groups",
    "rows",
    "safe_query",
    "status",
]
