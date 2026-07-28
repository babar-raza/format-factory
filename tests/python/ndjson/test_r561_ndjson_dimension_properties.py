"""R561: NDJSON dimension properties — is_empty, is_single_record, has_records.

Tests for NdjsonDocument dimension properties added in R561.
Spec refs: SAL-NDJSON-00001.
"""

import pytest
from pathlib import Path

import sys
_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ndjson.models import NdjsonDocument

SAMPLES = Path("samples/by-format/ndjson/valid")


class TestIsEmpty:
    def test_no_records_is_empty(self):
        doc = NdjsonDocument([])
        assert doc.is_empty is True

    def test_one_record_not_empty(self):
        doc = NdjsonDocument([{"a": 1}])
        assert doc.is_empty is False

    def test_multiple_records_not_empty(self):
        doc = NdjsonDocument([{"a": 1}, {"b": 2}, {"c": 3}])
        assert doc.is_empty is False

    def test_is_empty_type(self):
        doc = NdjsonDocument([])
        assert isinstance(doc.is_empty, bool)


class TestIsSingleRecord:
    def test_one_record_is_single(self):
        doc = NdjsonDocument([{"a": 1}])
        assert doc.is_single_record is True

    def test_zero_records_not_single(self):
        doc = NdjsonDocument([])
        assert doc.is_single_record is False

    def test_two_records_not_single(self):
        doc = NdjsonDocument([{"a": 1}, {"b": 2}])
        assert doc.is_single_record is False

    def test_is_single_record_type(self):
        doc = NdjsonDocument([{"a": 1}])
        assert isinstance(doc.is_single_record, bool)


class TestHasRecords:
    def test_one_record_has_records(self):
        doc = NdjsonDocument([{"a": 1}])
        assert doc.has_records is True

    def test_empty_no_records(self):
        doc = NdjsonDocument([])
        assert doc.has_records is False

    def test_multiple_records_has_records(self):
        doc = NdjsonDocument([1, 2, 3])
        assert doc.has_records is True

    def test_has_records_type(self):
        doc = NdjsonDocument([])
        assert isinstance(doc.has_records, bool)


class TestDimensionConsistency:
    def test_empty_and_has_records_exclusive(self):
        for n in [0, 1, 2, 5]:
            doc = NdjsonDocument([{"i": i} for i in range(n)])
            assert doc.is_empty != doc.has_records

    def test_single_implies_has_records(self):
        doc = NdjsonDocument([{"a": 1}])
        assert doc.is_single_record
        assert doc.has_records
        assert not doc.is_empty

    def test_from_file_minimal(self):
        doc = NdjsonDocument.from_file(SAMPLES / "minimal.ndjson")
        assert isinstance(doc.is_empty, bool)
        assert isinstance(doc.is_single_record, bool)
        assert isinstance(doc.has_records, bool)
