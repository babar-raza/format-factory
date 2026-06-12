"""
test_r170_ndjson_deep_coverage.py

Sprint: FORMAT-FACTORY-CAPABILITY-DEEPENING-LEDGER-REPAIR-001
Added: 2026-06-12

Tests for NDJSON deep functions: filter_records, get_field_names, head, tail,
count_records, sum_field, flatten_records, to_tsv, sort_records, get_unique_values,
write_ndjson, load_ndjson.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ndjson.ndjson_codec import (
    filter_records,
    get_field_names,
    head,
    tail,
    count_records,
    sum_field,
    flatten_records,
    to_tsv,
    sort_records,
    count_unique_values,
    write_ndjson,
    load_ndjson,
    probe_ndjson,
)

_SAMPLE = b'{"name":"alice","age":30,"city":"NYC"}\n{"name":"bob","age":25,"city":"LA"}\n{"name":"carol","age":35,"city":"NYC"}\n'
_SIMPLE = b'{"x":1}\n{"x":2}\n{"x":3}\n'
_NESTED = b'{"user":{"id":1,"score":10}}\n{"user":{"id":2,"score":20}}\n'


# ── filter_records ────────────────────────────────────────────────────────

class TestFilterRecords:

    def test_returns_list(self):
        result = filter_records(_SAMPLE, "city", "NYC")
        assert isinstance(result, list)

    def test_filter_by_string(self):
        result = filter_records(_SAMPLE, "city", "NYC")
        assert len(result) == 2

    def test_filter_no_match(self):
        result = filter_records(_SAMPLE, "city", "NOWHERE")
        assert result == []

    def test_filter_by_int(self):
        result = filter_records(_SAMPLE, "age", 30)
        assert len(result) == 1
        assert result[0]["name"] == "alice"

    def test_filter_result_fields(self):
        result = filter_records(_SAMPLE, "name", "bob")
        assert len(result) == 1
        assert result[0]["age"] == 25


# ── get_field_names ───────────────────────────────────────────────────────

class TestGetFieldNames:

    def test_returns_list(self):
        result = get_field_names(_SAMPLE)
        assert isinstance(result, list)

    def test_contains_expected_fields(self):
        result = get_field_names(_SAMPLE)
        assert "name" in result
        assert "age" in result
        assert "city" in result

    def test_simple_fields(self):
        result = get_field_names(_SIMPLE)
        assert "x" in result


# ── head ──────────────────────────────────────────────────────────────────

class TestHead:

    def test_returns_list(self):
        result = head(_SAMPLE)
        assert isinstance(result, list)

    def test_head_1(self):
        result = head(_SAMPLE, 1)
        assert len(result) == 1
        assert result[0]["name"] == "alice"

    def test_head_2(self):
        result = head(_SAMPLE, 2)
        assert len(result) == 2

    def test_head_all(self):
        result = head(_SAMPLE, 10)
        assert len(result) == 3


# ── tail ──────────────────────────────────────────────────────────────────

class TestTail:

    def test_returns_list(self):
        result = tail(_SAMPLE, 1)
        assert isinstance(result, list)

    def test_tail_1(self):
        result = tail(_SAMPLE, 1)
        assert len(result) == 1
        assert result[0]["name"] == "carol"

    def test_tail_2(self):
        result = tail(_SAMPLE, 2)
        assert len(result) == 2


# ── count_records ─────────────────────────────────────────────────────────

class TestCountRecords:

    def test_returns_int(self):
        assert isinstance(count_records(_SAMPLE), int)

    def test_correct_count(self):
        assert count_records(_SAMPLE) == 3

    def test_simple_count(self):
        assert count_records(_SIMPLE) == 3


# ── sum_field ─────────────────────────────────────────────────────────────

class TestSumField:

    def test_returns_float(self):
        result = sum_field(_SAMPLE, "age")
        assert isinstance(result, (int, float))

    def test_correct_sum(self):
        result = sum_field(_SAMPLE, "age")
        assert result == 90  # 30+25+35

    def test_simple_sum(self):
        result = sum_field(_SIMPLE, "x")
        assert result == 6  # 1+2+3


# ── flatten_records ───────────────────────────────────────────────────────

class TestFlattenRecords:

    def test_returns_list(self):
        result = flatten_records(_SAMPLE)
        assert isinstance(result, list)

    def test_flat_passthrough(self):
        result = flatten_records(_SIMPLE)
        assert len(result) == 3

    def test_nested_flattened(self):
        result = flatten_records(_NESTED)
        assert isinstance(result, list)
        assert len(result) == 2


# ── to_tsv ────────────────────────────────────────────────────────────────

class TestToTsv:

    def test_returns_string(self):
        result = to_tsv(_SIMPLE)
        assert isinstance(result, str)

    def test_has_tab_separator(self):
        result = to_tsv(_SAMPLE)
        assert "\t" in result

    def test_nonempty(self):
        result = to_tsv(_SAMPLE)
        assert len(result.strip()) > 0


# ── count_unique_values ───────────────────────────────────────────────────

class TestCountUniqueValues:

    def test_returns_int(self):
        result = count_unique_values(_SAMPLE, "city")
        assert isinstance(result, int)

    def test_correct_unique_count(self):
        result = count_unique_values(_SAMPLE, "city")
        assert result == 2  # NYC, LA

    def test_all_unique(self):
        result = count_unique_values(_SAMPLE, "name")
        assert result == 3


# ── write_ndjson + load_ndjson roundtrip ──────────────────────────────────

class TestWriteLoadRoundtrip:

    def test_write_creates_file(self, tmp_path):
        out = tmp_path / "out.ndjson"
        write_ndjson([{"key": "val"}], out)
        assert out.exists()

    def test_load_returns_list(self, tmp_path):
        out = tmp_path / "load.ndjson"
        write_ndjson([{"x": 1}, {"x": 2}], out)
        result = load_ndjson(out)
        assert isinstance(result, list)

    def test_roundtrip_count(self, tmp_path):
        out = tmp_path / "rt.ndjson"
        write_ndjson([{"a": i} for i in range(5)], out)
        result = load_ndjson(out)
        assert len(result) == 5

    def test_roundtrip_values(self, tmp_path):
        out = tmp_path / "rtv.ndjson"
        write_ndjson([{"name": "test", "val": 42}], out)
        result = load_ndjson(out)
        assert result[0]["name"] == "test"
        assert result[0]["val"] == 42
