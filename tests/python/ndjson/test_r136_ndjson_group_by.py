"""Tests for group_by() — NDJSON record grouping.

Sprint: FORMAT-FACTORY-AUTONOMY-ACCELERATION-SPRINT-4-001
TC-PRODUCT-NDJSON-GROUP-BY
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ndjson.ndjson_codec import group_by

_SAMPLE = b'{"type": "A", "v": 1}\n{"type": "B", "v": 2}\n{"type": "A", "v": 3}\n'


class TestGroupBy:
    def test_groups_by_field(self):
        result = group_by(_SAMPLE, "type")
        assert "A" in result
        assert "B" in result

    def test_a_group_has_two_records(self):
        result = group_by(_SAMPLE, "type")
        assert len(result["A"]) == 2

    def test_b_group_has_one_record(self):
        result = group_by(_SAMPLE, "type")
        assert len(result["B"]) == 1

    def test_missing_key_grouped_under_none(self):
        data = b'{"type": "A"}\n{"other": 1}\n'
        result = group_by(data, "type")
        assert None in result
        assert len(result[None]) == 1

    def test_returns_dict(self):
        result = group_by(_SAMPLE, "type")
        assert isinstance(result, dict)

    def test_values_are_lists(self):
        result = group_by(_SAMPLE, "type")
        for v in result.values():
            assert isinstance(v, list)

    def test_empty_source(self):
        result = group_by(b"", "type")
        assert result == {}

    def test_all_same_group(self):
        data = b'{"cat": "X"}\n{"cat": "X"}\n{"cat": "X"}\n'
        result = group_by(data, "cat")
        assert len(result) == 1
        assert len(result["X"]) == 3

    def test_non_dict_record_under_none(self):
        data = b'"string_record"\n{"k": "v"}\n'
        result = group_by(data, "k")
        assert None in result
        assert "string_record" in result[None]

    def test_order_preserved_within_group(self):
        data = b'{"g": "A", "i": 1}\n{"g": "A", "i": 2}\n{"g": "A", "i": 3}\n'
        result = group_by(data, "g")
        assert [r["i"] for r in result["A"]] == [1, 2, 3]

    def test_numeric_key_value(self):
        data = b'{"score": 1}\n{"score": 2}\n{"score": 1}\n'
        result = group_by(data, "score")
        assert len(result[1]) == 2
        assert len(result[2]) == 1
