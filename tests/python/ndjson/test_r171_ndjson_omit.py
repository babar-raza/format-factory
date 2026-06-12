"""Tests for NDJSON omit function (rnext38)."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ndjson.ndjson_codec import omit


class TestOmit:
    def test_omit_single_field(self):
        records = [{"a": 1, "b": 2, "c": 3}]
        result = omit(records, ["b"])
        assert result == [{"a": 1, "c": 3}]

    def test_omit_multiple_fields(self):
        records = [{"a": 1, "b": 2, "c": 3}]
        result = omit(records, ["a", "c"])
        assert result == [{"b": 2}]

    def test_omit_nonexistent_field(self):
        records = [{"a": 1}]
        result = omit(records, ["z"])
        assert result == [{"a": 1}]

    def test_omit_all_fields(self):
        records = [{"a": 1, "b": 2}]
        result = omit(records, ["a", "b"])
        assert result == [{}]

    def test_omit_empty_fields(self):
        records = [{"a": 1, "b": 2}]
        result = omit(records, [])
        assert result == [{"a": 1, "b": 2}]

    def test_omit_multiple_records(self):
        records = [
            {"name": "Alice", "age": 30, "secret": "x"},
            {"name": "Bob", "age": 25, "secret": "y"},
        ]
        result = omit(records, ["secret"])
        assert result == [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]

    def test_omit_empty_records(self):
        result = omit([], ["a"])
        assert result == []
