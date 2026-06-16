"""Tests for ndjson_all_records_nonempty and ndjson_max_field_name_length (Sprint 31)."""
import sys
import json
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ndjson import ndjson_all_records_nonempty, ndjson_max_field_name_length


def _write(tmp_path, name, records):
    p = tmp_path / f"{name}.ndjson"
    p.write_text("\n".join(json.dumps(r) for r in records) + "\n", encoding="utf-8")
    return str(p)


class TestNdjsonAllRecordsNonempty:
    def test_return_type(self, tmp_path):
        p = _write(tmp_path, "rt", [{"a": 1}])
        assert isinstance(ndjson_all_records_nonempty(p), bool)

    def test_all_nonempty(self, tmp_path):
        p = _write(tmp_path, "an", [{"a": 1}, {"b": 2}])
        assert ndjson_all_records_nonempty(p) is True

    def test_empty_record_detected(self, tmp_path):
        p = _write(tmp_path, "er", [{"a": 1}, {}])
        assert ndjson_all_records_nonempty(p) is False

    def test_all_empty_records(self, tmp_path):
        p = _write(tmp_path, "ae", [{}, {}])
        assert ndjson_all_records_nonempty(p) is False

    def test_empty_file(self, tmp_path):
        p = tmp_path / "empty.ndjson"
        p.write_text("")
        assert ndjson_all_records_nonempty(str(p)) is True


class TestNdjsonMaxFieldNameLength:
    def test_return_type(self, tmp_path):
        p = _write(tmp_path, "rt2", [{"ab": 1}])
        assert isinstance(ndjson_max_field_name_length(p), int)

    def test_exact_max(self, tmp_path):
        # 'name'=4, 'age'=3, 'value'=5 -> 5
        p = _write(tmp_path, "em", [{"name": "alice", "age": 30}, {"name": "bob", "value": 42}])
        assert ndjson_max_field_name_length(p) == 5

    def test_single_field(self, tmp_path):
        p = _write(tmp_path, "sf", [{"key": "v"}])
        assert ndjson_max_field_name_length(p) == 3

    def test_nonnegative(self, tmp_path):
        p = _write(tmp_path, "nn", [{"x": 1}])
        assert ndjson_max_field_name_length(p) >= 0

    def test_long_field_name(self, tmp_path):
        p = _write(tmp_path, "lf", [{"short": 1, "a_very_long_field_name": 2}])
        assert ndjson_max_field_name_length(p) == 22
