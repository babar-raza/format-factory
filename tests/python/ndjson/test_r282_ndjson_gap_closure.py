"""Tests closing FOSS gaps: ndjson_avg_numeric_value, ndjson_min_record_size,
ndjson_has_lists, ndjson_schema_consistency, ndjson_total_numeric_sum,
ndjson_is_single_record."""
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.ndjson.ndjson_codec import (
    ndjson_avg_numeric_value,
    ndjson_min_record_size,
    ndjson_has_lists,
    ndjson_schema_consistency,
    ndjson_total_numeric_sum,
    ndjson_is_single_record,
)


@pytest.fixture
def multi_record(tmp_path):
    p = tmp_path / "data.ndjson"
    lines = [
        json.dumps({"name": "Alice", "score": 10, "tags": ["a", "b"]}),
        json.dumps({"name": "Bob", "score": 20, "tags": ["c"]}),
        json.dumps({"name": "Charlie", "score": 30}),
    ]
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return p


@pytest.fixture
def single_record(tmp_path):
    p = tmp_path / "single.ndjson"
    p.write_text(json.dumps({"x": 42}) + "\n", encoding="utf-8")
    return p


def test_ndjson_avg_numeric_value(multi_record):
    result = ndjson_avg_numeric_value(multi_record)
    assert isinstance(result, (int, float))
    # scores 10+20+30 = 60, 3 values → avg 20
    assert result > 0


def test_ndjson_min_record_size(multi_record):
    result = ndjson_min_record_size(multi_record)
    assert isinstance(result, (int, float))
    assert result > 0


def test_ndjson_has_lists_true(multi_record):
    result = ndjson_has_lists(multi_record)
    assert result is True


def test_ndjson_has_lists_false(single_record):
    result = ndjson_has_lists(single_record)
    assert result is False


def test_ndjson_schema_consistency(multi_record):
    result = ndjson_schema_consistency(multi_record)
    assert isinstance(result, (int, float))
    # Not all records have same keys → <1.0
    assert 0.0 <= result <= 1.0


def test_ndjson_total_numeric_sum(multi_record):
    result = ndjson_total_numeric_sum(multi_record)
    assert isinstance(result, (int, float))
    assert result >= 60  # 10+20+30


def test_ndjson_is_single_record_false(multi_record):
    result = ndjson_is_single_record(multi_record)
    assert result is False


def test_ndjson_is_single_record_true(single_record):
    result = ndjson_is_single_record(single_record)
    assert result is True
