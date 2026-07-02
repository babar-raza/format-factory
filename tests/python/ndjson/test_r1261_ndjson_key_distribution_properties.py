"""Tests for R1261: NdjsonDocument key distribution analysis properties.

Properties under test:
    key_range          — max_keys - min_keys (0 if no object records)
    is_schema_consistent — all object records have the same key set
    object_count       — number of dict records

spec_fact_ref: FACT-NDJSON-001
"""

import pytest
from ndjson.models import NdjsonDocument


def _make_doc(records: list) -> NdjsonDocument:
    return NdjsonDocument(records)


# ── key_range ─────────────────────────────────────────────────────────────────

class TestKeyRange:
    def test_no_records_range_zero(self):
        doc = _make_doc([])
        assert doc.key_range == 0

    def test_uniform_objects_range_zero(self):
        doc = _make_doc([{"a": 1, "b": 2}, {"c": 3, "d": 4}])
        assert doc.key_range == 0

    def test_varying_key_counts(self):
        doc = _make_doc([{"a": 1}, {"a": 1, "b": 2, "c": 3}])
        assert doc.key_range == 2

    def test_single_record_range_zero(self):
        doc = _make_doc([{"x": 1, "y": 2}])
        assert doc.key_range == 0

    def test_arrays_ignored(self):
        doc = _make_doc([[1, 2, 3], [4, 5]])
        assert doc.key_range == 0


# ── is_schema_consistent ─────────────────────────────────────────────────────

class TestIsSchemaConsistent:
    def test_empty_doc_is_consistent(self):
        doc = _make_doc([])
        assert doc.is_schema_consistent is True

    def test_same_keys_consistent(self):
        doc = _make_doc([{"a": 1, "b": 2}, {"a": 3, "b": 4}])
        assert doc.is_schema_consistent is True

    def test_different_keys_not_consistent(self):
        doc = _make_doc([{"a": 1}, {"b": 2}])
        assert doc.is_schema_consistent is False

    def test_subset_keys_not_consistent(self):
        doc = _make_doc([{"a": 1, "b": 2}, {"a": 3}])
        assert doc.is_schema_consistent is False

    def test_single_record_consistent(self):
        doc = _make_doc([{"x": 1}])
        assert doc.is_schema_consistent is True

    def test_non_object_records_ignored(self):
        # Only dict records matter; arrays/scalars ignored
        doc = _make_doc([{"a": 1}, [1, 2], {"a": 99}])
        assert doc.is_schema_consistent is True


# ── object_count ──────────────────────────────────────────────────────────────

class TestObjectCount:
    def test_empty_doc_zero(self):
        doc = _make_doc([])
        assert doc.object_count == 0

    def test_all_objects(self):
        doc = _make_doc([{"a": 1}, {"b": 2}, {"c": 3}])
        assert doc.object_count == 3

    def test_mixed_types(self):
        doc = _make_doc([{"a": 1}, [1, 2], 42, {"b": 3}])
        assert doc.object_count == 2

    def test_no_objects(self):
        doc = _make_doc([[1, 2], [3, 4]])
        assert doc.object_count == 0


# ── cross-property consistency ────────────────────────────────────────────────

class TestCrossPropertyConsistency:
    def test_schema_consistent_implies_zero_range(self):
        doc = _make_doc([{"a": 1, "b": 2}, {"a": 3, "b": 4}])
        assert doc.is_schema_consistent is True
        assert doc.key_range == 0

    def test_inconsistent_implies_positive_range_or_different_keys(self):
        doc = _make_doc([{"a": 1}, {"b": 2}])
        assert doc.is_schema_consistent is False
        # Both have 1 key, so key_range=0 but keys differ
        assert doc.key_range == 0

    def test_object_count_le_record_count(self):
        doc = _make_doc([{"a": 1}, [1, 2], {"b": 3}])
        assert doc.object_count <= doc.record_count
