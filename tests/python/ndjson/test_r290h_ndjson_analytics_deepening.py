"""Sprint R290H: NDJSON analytics deepening — avg_key_length, null_ratio, object_field_variance."""
import sys
import json
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ndjson.ndjson_codec import (
    ndjson_avg_key_length,
    ndjson_null_ratio,
    ndjson_object_field_variance,
)


@pytest.fixture
def sample_file(tmp_path):
    f = tmp_path / "test.ndjson"
    lines = [
        json.dumps({"name": "Alice", "age": 30, "city": None}),
        json.dumps({"name": "Bob", "age": 25}),
    ]
    f.write_text("\n".join(lines) + "\n")
    return f


@pytest.fixture
def uniform_file(tmp_path):
    f = tmp_path / "uniform.ndjson"
    lines = [
        json.dumps({"a": 1, "b": 2}),
        json.dumps({"a": 3, "b": 4}),
    ]
    f.write_text("\n".join(lines) + "\n")
    return f


class TestNdjsonAvgKeyLength:
    def test_returns_float(self, sample_file):
        assert isinstance(ndjson_avg_key_length(sample_file), float)

    def test_positive(self, sample_file):
        assert ndjson_avg_key_length(sample_file) > 0.0

    def test_list_input(self):
        records = [{"ab": 1, "cde": 2}]
        avg = ndjson_avg_key_length(records)
        assert avg == 2.5


class TestNdjsonNullRatio:
    def test_returns_float(self, sample_file):
        assert isinstance(ndjson_null_ratio(sample_file), float)

    def test_has_nulls(self, sample_file):
        assert ndjson_null_ratio(sample_file) > 0.0

    def test_list_input_no_nulls(self):
        records = [{"a": 1}, {"b": 2}]
        assert ndjson_null_ratio(records) == 0.0


class TestNdjsonObjectFieldVariance:
    def test_returns_float(self, sample_file):
        assert isinstance(ndjson_object_field_variance(sample_file), float)

    def test_uniform_zero(self, uniform_file):
        assert ndjson_object_field_variance(uniform_file) == 0.0

    def test_varied_positive(self, sample_file):
        assert ndjson_object_field_variance(sample_file) > 0.0
