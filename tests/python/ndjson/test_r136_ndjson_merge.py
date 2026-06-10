"""Tests for merge_ndjson() — NDJSON source merge.

Sprint: FORMAT-FACTORY-AUTONOMY-ACCELERATION-SPRINT-4-001
TC-PRODUCT-NDJSON-MERGE
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ndjson.ndjson_codec import merge_ndjson

_SRC_A = b'{"id": 1}\n{"id": 2}\n'
_SRC_B = b'{"id": 3}\n{"id": 4}\n'


class TestMergeNdjson:
    def test_combined_count(self):
        result = merge_ndjson(_SRC_A, _SRC_B)
        assert len(result) == 4

    def test_a_records_first(self):
        result = merge_ndjson(_SRC_A, _SRC_B)
        assert result[0] == {"id": 1}
        assert result[1] == {"id": 2}

    def test_b_records_second(self):
        result = merge_ndjson(_SRC_A, _SRC_B)
        assert result[2] == {"id": 3}
        assert result[3] == {"id": 4}

    def test_merge_empty_a(self):
        result = merge_ndjson(b"", _SRC_B)
        assert len(result) == 2
        assert result[0] == {"id": 3}

    def test_merge_empty_b(self):
        result = merge_ndjson(_SRC_A, b"")
        assert len(result) == 2

    def test_merge_both_empty(self):
        result = merge_ndjson(b"", b"")
        assert result == []

    def test_returns_list(self):
        result = merge_ndjson(_SRC_A, _SRC_B)
        assert isinstance(result, list)

    def test_mixed_types(self):
        a = b'"hello"\n42\n'
        b_ = b'{"x": 1}\n'
        result = merge_ndjson(a, b_)
        assert result == ["hello", 42, {"x": 1}]

    def test_file_sources(self, tmp_path):
        f1 = tmp_path / "a.ndjson"
        f2 = tmp_path / "b.ndjson"
        f1.write_text('{"a": 1}\n', encoding="utf-8")
        f2.write_text('{"b": 2}\n', encoding="utf-8")
        result = merge_ndjson(f1, f2)
        assert len(result) == 2
        assert result[0] == {"a": 1}
        assert result[1] == {"b": 2}

    def test_large_merge(self):
        recs = "\n".join(f'{{"n": {i}}}' for i in range(50)) + "\n"
        data = recs.encode()
        result = merge_ndjson(data, data)
        assert len(result) == 100
