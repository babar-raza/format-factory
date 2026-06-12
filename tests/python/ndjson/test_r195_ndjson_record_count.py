"""Tests for ndjson_record_count — rnext64 product deepening."""
import json


def _make_ndjson(records):
    return "\n".join(json.dumps(r) for r in records).encode()


def test_import():
    from src.python.ndjson import ndjson_record_count
    assert callable(ndjson_record_count)


def test_three_records():
    from src.python.ndjson import ndjson_record_count
    data = _make_ndjson([{"a": 1}, {"b": 2}, {"c": 3}])
    assert ndjson_record_count(data) == 3


def test_single_record():
    from src.python.ndjson import ndjson_record_count
    data = _make_ndjson([{"x": 42}])
    assert ndjson_record_count(data) == 1


def test_empty_list():
    from src.python.ndjson import ndjson_record_count
    assert ndjson_record_count([]) == 0


def test_returns_int():
    from src.python.ndjson import ndjson_record_count
    result = ndjson_record_count([{"a": 1}, {"b": 2}])
    assert isinstance(result, int)


def test_accepts_list_directly():
    from src.python.ndjson import ndjson_record_count
    result = ndjson_record_count([{"a": 1}, {"b": 2}, {"c": 3}, {"d": 4}])
    assert result == 4
