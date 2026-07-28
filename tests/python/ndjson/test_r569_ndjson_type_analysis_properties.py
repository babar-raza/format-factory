"""R569: NDJSON type analysis properties — has_mixed_types, all_scalars, max_keys.

Tests for NdjsonDocument type analysis properties added in R569.
Spec refs: SAL-NDJSON-00001.
"""

import pytest
from pathlib import Path

import sys
_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ndjson.models import NdjsonDocument

SAMPLES = Path("samples/by-format/ndjson/valid")


def _make_doc(records=None):
    """Build a minimal NdjsonDocument from a list of records."""
    return NdjsonDocument(records or [])


class TestHasMixedTypes:
    def test_object_and_array_is_mixed(self):
        doc = _make_doc([{"a": 1}, [1, 2]])
        assert doc.has_mixed_types is True

    def test_object_and_scalar_is_mixed(self):
        doc = _make_doc([{"a": 1}, 42])
        assert doc.has_mixed_types is True

    def test_all_objects_not_mixed(self):
        doc = _make_doc([{"a": 1}, {"b": 2}])
        assert doc.has_mixed_types is False

    def test_all_arrays_not_mixed(self):
        doc = _make_doc([[1, 2], [3, 4]])
        assert doc.has_mixed_types is False

    def test_empty_doc_not_mixed(self):
        doc = _make_doc()
        assert doc.has_mixed_types is False

    def test_has_mixed_types_type(self):
        doc = _make_doc([{"a": 1}])
        assert isinstance(doc.has_mixed_types, bool)

    def test_mixed_exclusive_with_all_objects_arrays(self):
        for records in [[], [{"a": 1}], [[1]], [{"a": 1}, [1]]]:
            doc = _make_doc(records)
            if doc.has_mixed_types:
                assert not doc.all_objects and not doc.all_arrays


class TestAllScalars:
    def test_single_integer_is_scalar(self):
        doc = _make_doc([42])
        assert doc.all_scalars is True

    def test_multiple_scalars(self):
        doc = _make_doc([1, "hello", True])
        assert doc.all_scalars is True

    def test_objects_not_scalars(self):
        doc = _make_doc([{"a": 1}])
        assert doc.all_scalars is False

    def test_arrays_not_scalars(self):
        doc = _make_doc([[1, 2]])
        assert doc.all_scalars is False

    def test_empty_doc_not_scalars(self):
        doc = _make_doc()
        assert doc.all_scalars is False

    def test_all_scalars_type(self):
        doc = _make_doc([42])
        assert isinstance(doc.all_scalars, bool)

    def test_mix_not_all_scalars(self):
        doc = _make_doc([42, {"a": 1}])
        assert doc.all_scalars is False


class TestMaxKeys:
    def test_empty_doc_zero(self):
        doc = _make_doc()
        assert doc.max_keys == 0

    def test_single_object_one_key(self):
        doc = _make_doc([{"a": 1}])
        assert doc.max_keys == 1

    def test_object_three_keys(self):
        doc = _make_doc([{"a": 1, "b": 2, "c": 3}])
        assert doc.max_keys == 3

    def test_max_across_multiple_objects(self):
        doc = _make_doc([{"a": 1}, {"a": 1, "b": 2, "c": 3}])
        assert doc.max_keys == 3

    def test_arrays_not_counted(self):
        doc = _make_doc([[1, 2, 3, 4, 5]])
        assert doc.max_keys == 0

    def test_mixed_object_and_array(self):
        doc = _make_doc([{"a": 1, "b": 2}, [10, 20]])
        assert doc.max_keys == 2

    def test_max_keys_type(self):
        doc = _make_doc([{"x": 1}])
        assert isinstance(doc.max_keys, int)

    def test_empty_object_zero_keys(self):
        doc = _make_doc([{}])
        assert doc.max_keys == 0


class TestTypeAnalysisConsistency:
    def test_all_objects_implies_not_all_arrays(self):
        doc = _make_doc([{"a": 1}, {"b": 2}])
        assert doc.all_objects
        assert not doc.all_arrays
        assert not doc.has_mixed_types

    def test_all_scalars_implies_not_objects_or_arrays(self):
        doc = _make_doc([1, 2, 3])
        assert doc.all_scalars
        assert not doc.all_objects
        assert not doc.all_arrays

    def test_max_keys_ge_zero(self):
        for records in [[], [{"a": 1}], [[1, 2]], [42]]:
            doc = _make_doc(records)
            assert doc.max_keys >= 0

    def test_from_file_minimal(self):
        doc = NdjsonDocument.from_file(SAMPLES / "minimal.ndjson")
        assert isinstance(doc.has_mixed_types, bool)
        assert isinstance(doc.all_scalars, bool)
        assert isinstance(doc.max_keys, int)
