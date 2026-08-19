"""The four ported behaviours + the cache-key contract that keeps the P1 cache usable."""

from __future__ import annotations

import pytest

from mijual.config import SPIKE_CACHE_DIR
from mijual.dart import CacheMiss, DartClient, groups, rows, safe_query

# One real P1 cache filename. If the key scheme ever drifts, 1,002 cached
# responses stop being reachable and every offline test/smoke goes silent.
GOLDEN = (
    "list",
    dict(bgn_de="20260401", end_de="20260630", corp_cls="Y", pblntf_ty="B",
         page_no=3, page_count=100, corp_code=None, crtfc_key="SECRET"),
    "json",
    "bgn-de-20260401-corp-cls-Y-end-de-20260630-page-count-100-pa_fa18001a9a3b.json",
)


def test_cache_path_matches_the_spike_scheme(tmp_path):
    """Byte-compatible filename — and the key/None params never reach it."""
    endpoint, params, ext, expected = GOLDEN
    path = DartClient(cache_dir=tmp_path, offline=True).cache_path(endpoint, params, ext)
    assert path.name == expected
    assert path.parent.name == endpoint
    assert "SECRET" not in str(path)


@pytest.mark.skipif(not SPIKE_CACHE_DIR.exists(), reason="P1 sample cache is gitignored")
def test_spike_cache_is_a_working_offline_fixture():
    endpoint, params, ext, _ = GOLDEN
    client = DartClient(cache_dir=SPIKE_CACHE_DIR, offline=True)
    assert client.cache_path(endpoint, params, ext).exists()
    body = client.get_json(endpoint, **{k: v for k, v in params.items() if k != "crtfc_key"})
    assert body["status"] == "000" and rows(body)
    assert client.get_document("20260724000546").startswith(b"PK")


def test_none_params_are_dropped_and_the_key_is_stripped():
    # `corp_code=None` serialized as a literal would come back `status 100`.
    assert safe_query({"corp_code": None, "b": 2, "a": 1, "crtfc_key": "SECRET"}) == "a=1&b=2"


def test_groups_normalises_both_response_shapes():
    grouped = {"status": "000", "group": [{"title": "일반사항", "list": [{"x": 1}]}]}
    flat = {"status": "000", "list": [{"y": 2}]}
    assert groups(grouped) == [("일반사항", [{"x": 1}])]
    assert groups(flat) == [("list", [{"y": 2}])]
    assert groups({"status": "013", "message": "no data"}) == []
    assert rows({"status": "013"}) == []


def test_offline_miss_raises_without_needing_a_key(tmp_path):
    client = DartClient(cache_dir=tmp_path, offline=True, api_key=None)
    with pytest.raises(CacheMiss):
        client.get_json("list", bgn_de="20260101", end_de="20260102")
    with pytest.raises(CacheMiss):
        client.get_document("20260724000546")
