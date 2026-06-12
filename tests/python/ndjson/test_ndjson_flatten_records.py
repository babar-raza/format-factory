"""
tests/python/ndjson/test_ndjson_flatten_records.py
Tests for flatten_records() added via QUEUE_DISPATCHED_EXECUTION.

Sprint: FORMAT-FACTORY-SELF-HEALING-QUEUE-PROFESSIONALIZE-RNEXT-001
Queue item: shq-q-002
"""

from __future__ import annotations

import sys
from pathlib import Path


_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.ndjson.ndjson_codec import flatten_records


class TestFlattenRecords:
    def test_returns_list(self) -> None:
        result = flatten_records([{"a": 1}])
        assert isinstance(result, list)

    def test_flat_records_unchanged(self) -> None:
        records = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]
        result = flatten_records(records)
        assert result == records

    def test_nested_dict_flattened(self) -> None:
        records = [{"meta": {"x": 1, "y": 2}, "value": 3}]
        result = flatten_records(records)
        assert result[0] == {"meta_x": 1, "meta_y": 2, "value": 3}

    def test_multiple_nested_keys(self) -> None:
        records = [{"a": {"p": 1, "q": 2}, "b": {"r": 3}}]
        result = flatten_records(records)
        assert result[0]["a_p"] == 1
        assert result[0]["a_q"] == 2
        assert result[0]["b_r"] == 3

    def test_empty_list(self) -> None:
        assert flatten_records([]) == []

    def test_prefix_applied(self) -> None:
        records = [{"name": "Alice", "score": {"math": 95}}]
        result = flatten_records(records, prefix="row_")
        assert "row_name" in result[0]
        assert "row_score_math" in result[0]
        assert result[0]["row_score_math"] == 95

    def test_non_dict_records_pass_through(self) -> None:
        records = [42, "string", None]
        result = flatten_records(records)
        assert result == [42, "string", None]

    def test_bytes_source(self) -> None:
        src = b'{"a": {"x": 1}}\n{"b": 2}\n'
        result = flatten_records(src)
        assert result[0] == {"a_x": 1}
        assert result[1] == {"b": 2}

    def test_empty_nested_dict(self) -> None:
        records = [{"meta": {}, "value": 5}]
        result = flatten_records(records)
        # meta is empty dict — no sub-keys to expand
        assert "meta" not in result[0]
        assert result[0]["value"] == 5

    def test_multiple_records_each_flattened(self) -> None:
        records = [
            {"a": {"x": 1}, "b": 2},
            {"a": {"x": 3}, "b": 4},
        ]
        result = flatten_records(records)
        assert result[0]["a_x"] == 1
        assert result[1]["a_x"] == 3

    def test_does_not_recurse_deeper(self) -> None:
        """Only one level of nesting is flattened."""
        records = [{"outer": {"inner": {"deep": 1}}}]
        result = flatten_records(records)
        # inner is a dict, so outer_inner is expanded but its value is the inner dict
        assert "outer_inner" in result[0]
        assert isinstance(result[0]["outer_inner"], dict)
