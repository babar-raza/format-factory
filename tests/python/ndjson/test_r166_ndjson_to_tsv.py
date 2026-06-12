"""
tests/python/ndjson/test_r166_ndjson_to_tsv.py

Tests for NDJSON to_tsv export function.

Sprint: FORMAT-FACTORY-BROAD-SELF-HEALING-PRODUCT-ACCELERATION-RNEXT-001
Queue: broad-accel-q-003
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ndjson.ndjson_codec import to_tsv


class TestToTsv:
    def test_basic_records(self) -> None:
        records = [{"name": "Alice", "age": "30"}, {"name": "Bob", "age": "25"}]
        result = to_tsv(records)
        lines = result.splitlines()
        assert lines[0] == "name\tage"
        assert lines[1] == "Alice\t30"
        assert lines[2] == "Bob\t25"

    def test_empty_records(self) -> None:
        result = to_tsv([])
        assert result == ""

    def test_no_header(self) -> None:
        records = [{"x": "1", "y": "2"}]
        result = to_tsv(records, include_header=False)
        assert "\t" in result
        assert "x" not in result
        assert "y" not in result

    def test_missing_field_renders_empty(self) -> None:
        records = [{"a": "1", "b": "2"}, {"a": "3"}]
        result = to_tsv(records)
        lines = result.splitlines()
        assert lines[0] == "a\tb"
        assert lines[2] == "3\t"

    def test_tab_separated(self) -> None:
        records = [{"col1": "v1", "col2": "v2"}]
        result = to_tsv(records)
        assert "\t" in result

    def test_field_order_stable(self) -> None:
        records = [{"z": "1", "a": "2", "m": "3"}]
        result = to_tsv(records)
        header = result.splitlines()[0]
        assert header == "z\ta\tm"

    def test_numeric_values_stringified(self) -> None:
        records = [{"n": 42, "f": 3.14}]
        result = to_tsv(records)
        assert "42" in result
        assert "3.14" in result

    def test_from_bytes_source(self, tmp_path: Path) -> None:
        ndjson_bytes = b'{"x": "hello"}\n{"x": "world"}\n'
        result = to_tsv(ndjson_bytes)
        assert "hello" in result
        assert "world" in result
