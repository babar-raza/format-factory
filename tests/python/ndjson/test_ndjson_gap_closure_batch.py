"""Gap closure tests for NDJSON — covering 15 open gaps.

Gaps cover: load_ndjson, write_ndjson, probe_ndjson, count_records,
    get_field_names, sum_field, average_value, min_value, max_value,
    ndjson_record_count, ndjson_null_field_count, ndjson_unique_field_names,
    ndjson_max_field_count, ndjson_average_field_count,
    NdjsonError, NdjsonParseError
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ndjson import (
    NdjsonError,
    NdjsonParseError,
    average_value,
    count_records,
    get_field_names,
    load_ndjson,
    max_value,
    min_value,
    ndjson_average_field_count,
    ndjson_max_field_count,
    ndjson_null_field_count,
    ndjson_record_count,
    ndjson_unique_field_names,
    probe_ndjson,
    sum_field,
    write_ndjson,
)


@pytest.fixture
def ndjson_file(tmp_path):
    """Create a simple NDJSON file with known data."""
    content = '{"name":"Alice","age":30,"city":"NYC"}\n{"name":"Bob","age":25,"city":"LA"}\n{"name":"Carol","age":35,"city":"SF"}\n'
    f = tmp_path / "test.ndjson"
    f.write_text(content, encoding="utf-8")
    return f


class TestErrorClasses:
    def test_ndjson_error_is_exception(self):
        assert issubclass(NdjsonError, Exception)

    def test_ndjson_parse_error_subclass(self):
        assert issubclass(NdjsonParseError, (NdjsonError, Exception))

    def test_message_preserved(self):
        err = NdjsonError("bad ndjson")
        assert "bad ndjson" in str(err)


class TestLoadNdjson:
    def test_returns_list(self, ndjson_file):
        records = load_ndjson(str(ndjson_file))
        assert isinstance(records, list)
        assert len(records) == 3


class TestWriteNdjson:
    def test_creates_file(self, tmp_path):
        records = [{"a": 1}, {"a": 2}]
        f = tmp_path / "out.ndjson"
        write_ndjson(records, str(f))
        assert f.exists()


class TestProbeNdjson:
    def test_valid_file(self, ndjson_file):
        result = probe_ndjson(str(ndjson_file))
        assert result is not None


class TestCountRecords:
    def test_count(self, ndjson_file):
        count = count_records(str(ndjson_file))
        assert count == 3


class TestGetFieldNames:
    def test_returns_list(self, ndjson_file):
        fields = get_field_names(str(ndjson_file))
        assert isinstance(fields, (list, set))
        field_list = list(fields)
        assert "name" in field_list
        assert "age" in field_list


class TestSumField:
    def test_sum_age(self, ndjson_file):
        total = sum_field(str(ndjson_file), "age")
        assert total == 90.0 or total == 90


class TestAverageValue:
    def test_average_age(self, ndjson_file):
        avg = average_value(str(ndjson_file), "age")
        assert abs(float(avg) - 30.0) < 0.01


class TestMinValue:
    def test_min_age(self, ndjson_file):
        result = min_value(str(ndjson_file), "age")
        assert float(result) == 25.0


class TestMaxValue:
    def test_max_age(self, ndjson_file):
        result = max_value(str(ndjson_file), "age")
        assert float(result) == 35.0


class TestNdjsonRecordCount:
    def test_count(self, ndjson_file):
        count = ndjson_record_count(str(ndjson_file))
        assert count == 3


class TestNdjsonNullFieldCount:
    def test_no_nulls(self, ndjson_file):
        count = ndjson_null_field_count(str(ndjson_file), "name")
        assert count == 0


class TestNdjsonUniqueFieldNames:
    def test_returns_result(self, ndjson_file):
        result = ndjson_unique_field_names(str(ndjson_file))
        assert isinstance(result, (int, list, set))


class TestNdjsonMaxFieldCount:
    def test_returns_int(self, ndjson_file):
        count = ndjson_max_field_count(str(ndjson_file))
        assert isinstance(count, int)
        assert count == 3


class TestNdjsonAverageFieldCount:
    def test_returns_number(self, ndjson_file):
        avg = ndjson_average_field_count(str(ndjson_file))
        assert isinstance(avg, (int, float))
        assert avg == 3.0 or avg == 3
