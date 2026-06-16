"""Tests for 6 new NDJSON analytics functions.

Covers: ndjson_min_record_size, ndjson_has_numeric_fields, ndjson_has_lists,
    ndjson_schema_consistency, ndjson_total_numeric_sum, ndjson_is_single_record.
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ndjson import (
    ndjson_has_lists,
    ndjson_has_numeric_fields,
    ndjson_is_single_record,
    ndjson_min_record_size,
    ndjson_schema_consistency,
    ndjson_total_numeric_sum,
)


@pytest.fixture
def rich_ndjson(tmp_path):
    content = (
        '{"name": "alice", "age": 30, "scores": [95, 87]}\n'
        '{"name": "bob", "age": 25, "scores": [80]}\n'
        '{"name": "carol", "age": 35, "scores": [88, 90, 92]}\n'
    )
    f = tmp_path / "data.ndjson"
    f.write_text(content, encoding="utf-8")
    return f


@pytest.fixture
def string_only_ndjson(tmp_path):
    content = '{"name": "alice"}\n{"name": "bob"}\n'
    f = tmp_path / "string.ndjson"
    f.write_text(content, encoding="utf-8")
    return f


@pytest.fixture
def single_ndjson(tmp_path):
    content = '{"key": "value", "num": 42}\n'
    f = tmp_path / "single.ndjson"
    f.write_text(content, encoding="utf-8")
    return f


@pytest.fixture
def empty_ndjson(tmp_path):
    f = tmp_path / "empty.ndjson"
    f.write_text("", encoding="utf-8")
    return f


class TestNdjsonMinRecordSize:
    def test_returns_int(self, rich_ndjson):
        result = ndjson_min_record_size(rich_ndjson)
        assert isinstance(result, int)

    def test_positive_for_nonempty(self, rich_ndjson):
        result = ndjson_min_record_size(rich_ndjson)
        assert result > 0

    def test_zero_for_empty(self, empty_ndjson):
        assert ndjson_min_record_size(empty_ndjson) == 0

    def test_single_record_size(self, single_ndjson):
        result = ndjson_min_record_size(single_ndjson)
        assert result > 10


class TestNdjsonHasNumericFields:
    def test_true_for_numeric_data(self, rich_ndjson):
        assert ndjson_has_numeric_fields(rich_ndjson) is True

    def test_false_for_string_only(self, string_only_ndjson):
        assert ndjson_has_numeric_fields(string_only_ndjson) is False

    def test_returns_bool(self, rich_ndjson):
        assert isinstance(ndjson_has_numeric_fields(rich_ndjson), bool)

    def test_false_for_empty(self, empty_ndjson):
        assert ndjson_has_numeric_fields(empty_ndjson) is False


class TestNdjsonHasLists:
    def test_true_for_list_data(self, rich_ndjson):
        assert ndjson_has_lists(rich_ndjson) is True

    def test_false_for_scalar_data(self, string_only_ndjson):
        assert ndjson_has_lists(string_only_ndjson) is False

    def test_returns_bool(self, rich_ndjson):
        assert isinstance(ndjson_has_lists(rich_ndjson), bool)

    def test_false_for_empty(self, empty_ndjson):
        assert ndjson_has_lists(empty_ndjson) is False


class TestNdjsonSchemaConsistency:
    def test_returns_float(self, rich_ndjson):
        result = ndjson_schema_consistency(rich_ndjson)
        assert isinstance(result, float)

    def test_one_for_uniform_schema(self, string_only_ndjson):
        result = ndjson_schema_consistency(string_only_ndjson)
        assert result == 1.0

    def test_in_range(self, rich_ndjson):
        result = ndjson_schema_consistency(rich_ndjson)
        assert 0.0 <= result <= 1.0

    def test_zero_for_empty(self, empty_ndjson):
        assert ndjson_schema_consistency(empty_ndjson) == 0.0


class TestNdjsonTotalNumericSum:
    def test_returns_float(self, rich_ndjson):
        result = ndjson_total_numeric_sum(rich_ndjson)
        assert isinstance(result, float)

    def test_positive_for_numeric_data(self, rich_ndjson):
        result = ndjson_total_numeric_sum(rich_ndjson)
        assert result > 0

    def test_zero_for_no_numerics(self, string_only_ndjson):
        assert ndjson_total_numeric_sum(string_only_ndjson) == 0.0

    def test_zero_for_empty(self, empty_ndjson):
        assert ndjson_total_numeric_sum(empty_ndjson) == 0.0

    def test_single_record(self, single_ndjson):
        result = ndjson_total_numeric_sum(single_ndjson)
        assert result == pytest.approx(42.0)


class TestNdjsonIsSingleRecord:
    def test_true_for_single(self, single_ndjson):
        assert ndjson_is_single_record(single_ndjson) is True

    def test_false_for_multi(self, rich_ndjson):
        assert ndjson_is_single_record(rich_ndjson) is False

    def test_returns_bool(self, single_ndjson):
        assert isinstance(ndjson_is_single_record(single_ndjson), bool)

    def test_false_for_empty(self, empty_ndjson):
        assert ndjson_is_single_record(empty_ndjson) is False
