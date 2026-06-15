"""
test_rnext_ndjson_merge.py -- Dedicated test coverage for merge_ndjson.

Gap: GAP-NDJSON-FOSS-MERGE_NDJSON-001 (missing_test_coverage)
"""
from __future__ import annotations
import sys
from pathlib import Path
_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ndjson.ndjson_codec import merge_ndjson, write_ndjson


class TestMergeNdjson:
    def test_merge_two_files(self, tmp_path):
        a = tmp_path / "a.ndjson"
        b = tmp_path / "b.ndjson"
        write_ndjson([{"x": 1}], str(a))
        write_ndjson([{"x": 2}], str(b))
        result = merge_ndjson(str(a), str(b))
        assert len(result) == 2
        assert result[0]["x"] == 1
        assert result[1]["x"] == 2

    def test_merge_preserves_order(self, tmp_path):
        a = tmp_path / "a.ndjson"
        b = tmp_path / "b.ndjson"
        write_ndjson([{"i": 1}, {"i": 2}], str(a))
        write_ndjson([{"i": 3}, {"i": 4}], str(b))
        result = merge_ndjson(str(a), str(b))
        assert [r["i"] for r in result] == [1, 2, 3, 4]

    def test_merge_empty_first(self, tmp_path):
        a = tmp_path / "empty.ndjson"
        b = tmp_path / "b.ndjson"
        write_ndjson([], str(a))
        write_ndjson([{"v": 1}], str(b))
        result = merge_ndjson(str(a), str(b))
        assert len(result) == 1

    def test_merge_empty_second(self, tmp_path):
        a = tmp_path / "a.ndjson"
        b = tmp_path / "empty.ndjson"
        write_ndjson([{"v": 1}], str(a))
        write_ndjson([], str(b))
        result = merge_ndjson(str(a), str(b))
        assert len(result) == 1

    def test_merge_both_empty(self, tmp_path):
        a = tmp_path / "a.ndjson"
        b = tmp_path / "b.ndjson"
        write_ndjson([], str(a))
        write_ndjson([], str(b))
        result = merge_ndjson(str(a), str(b))
        assert result == []

    def test_merge_large_sets(self, tmp_path):
        a = tmp_path / "a.ndjson"
        b = tmp_path / "b.ndjson"
        write_ndjson([{"i": i} for i in range(50)], str(a))
        write_ndjson([{"i": i} for i in range(50, 100)], str(b))
        result = merge_ndjson(str(a), str(b))
        assert len(result) == 100

    def test_returns_list(self, tmp_path):
        a = tmp_path / "a.ndjson"
        b = tmp_path / "b.ndjson"
        write_ndjson([{"a": 1}], str(a))
        write_ndjson([{"b": 2}], str(b))
        result = merge_ndjson(str(a), str(b))
        assert isinstance(result, list)
