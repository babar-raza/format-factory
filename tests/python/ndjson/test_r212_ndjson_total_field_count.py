"""Tests for ndjson_total_field_count().

Sprint: product-deepening-rnext81
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ndjson.ndjson_codec import ndjson_total_field_count

ONE_FIELD = b'{"a": 1}\n'
THREE_FIELDS = b'{"a": 1}\n{"b": 2, "c": 3}\n'
TWO_RECORDS_SAME = b'{"x": 1, "y": 2}\n{"z": 3}\n'
NON_DICT = b'42\n"hello"\ntrue\n'
EMPTY = b""


class TestNdjsonTotalFieldCount:
    def test_import(self):
        assert callable(ndjson_total_field_count)

    def test_empty_source_is_zero(self):
        assert ndjson_total_field_count(EMPTY) == 0

    def test_single_field_record(self):
        assert ndjson_total_field_count(ONE_FIELD) == 1

    def test_multi_record_sum(self):
        assert ndjson_total_field_count(THREE_FIELDS) == 3

    def test_non_dict_records_contribute_zero(self):
        assert ndjson_total_field_count(NON_DICT) == 0

    def test_returns_int(self):
        result = ndjson_total_field_count(TWO_RECORDS_SAME)
        assert isinstance(result, int)
        assert result == 3
