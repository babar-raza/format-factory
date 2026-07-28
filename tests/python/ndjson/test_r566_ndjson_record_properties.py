"""R566: NDJSON record analysis properties — is_multi_record, all_objects, all_arrays.

Tests for NdjsonDocument record analysis properties added in R566.
Spec refs: SAL-NDJSON-00001 (ndjson:record).
"""

import pytest
from pathlib import Path

import sys
_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ndjson.models import NdjsonDocument

SAMPLES = Path("samples/by-format/ndjson/valid")


def _make_doc(records=None):
    """Build a minimal NdjsonDocument."""
    return NdjsonDocument(records or [])


class TestIsMultiRecord:
    def test_zero_records_not_multi(self):
        doc = _make_doc([])
        assert doc.is_multi_record is False

    def test_one_record_not_multi(self):
        doc = _make_doc([{"a": 1}])
        assert doc.is_multi_record is False

    def test_two_records_is_multi(self):
        doc = _make_doc([{"a": 1}, {"b": 2}])
        assert doc.is_multi_record is True

    def test_many_records(self):
        doc = _make_doc([{"x": i} for i in range(10)])
        assert doc.is_multi_record is True

    def test_is_multi_record_type(self):
        doc = _make_doc([{"a": 1}, {"b": 2}])
        assert isinstance(doc.is_multi_record, bool)

    def test_inverse_of_single_record(self):
        doc = _make_doc([{"a": 1}])
        assert doc.is_single_record is True
        assert doc.is_multi_record is False


class TestAllObjects:
    def test_empty_doc_not_all_objects(self):
        doc = _make_doc([])
        assert doc.all_objects is False

    def test_all_dicts_is_true(self):
        doc = _make_doc([{"a": 1}, {"b": 2}])
        assert doc.all_objects is True

    def test_mixed_types_is_false(self):
        doc = _make_doc([{"a": 1}, [1, 2]])
        assert doc.all_objects is False

    def test_all_lists_not_objects(self):
        doc = _make_doc([[1, 2], [3, 4]])
        assert doc.all_objects is False

    def test_single_dict_is_true(self):
        doc = _make_doc([{"key": "value"}])
        assert doc.all_objects is True

    def test_all_objects_type(self):
        doc = _make_doc([{"a": 1}])
        assert isinstance(doc.all_objects, bool)


class TestAllArrays:
    def test_empty_doc_not_all_arrays(self):
        doc = _make_doc([])
        assert doc.all_arrays is False

    def test_all_lists_is_true(self):
        doc = _make_doc([[1, 2], [3, 4]])
        assert doc.all_arrays is True

    def test_mixed_types_is_false(self):
        doc = _make_doc([[1, 2], {"key": "val"}])
        assert doc.all_arrays is False

    def test_all_dicts_not_arrays(self):
        doc = _make_doc([{"a": 1}])
        assert doc.all_arrays is False

    def test_single_list_is_true(self):
        doc = _make_doc([[1, 2, 3]])
        assert doc.all_arrays is True

    def test_all_arrays_type(self):
        doc = _make_doc([[1]])
        assert isinstance(doc.all_arrays, bool)


class TestRecordPropertyConsistency:
    def test_all_objects_and_all_arrays_exclusive(self):
        doc = _make_doc([{"a": 1}, {"b": 2}])
        assert doc.all_objects is True
        assert doc.all_arrays is False

    def test_empty_neither_objects_nor_arrays(self):
        doc = _make_doc([])
        assert doc.all_objects is False
        assert doc.all_arrays is False

    def test_from_file(self):
        doc = NdjsonDocument.from_file(SAMPLES / "minimal.ndjson")
        assert isinstance(doc.is_multi_record, bool)
        assert isinstance(doc.all_objects, bool)
        assert isinstance(doc.all_arrays, bool)
