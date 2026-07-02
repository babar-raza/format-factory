"""Tests for R1281: NdjsonDocument record type distribution properties.

Properties under test:
    array_count    — number of records that are JSON arrays
    scalar_count   — number of records that are scalar values (not dict or list)
    object_fraction — fraction of records that are JSON objects

spec_fact_ref: FACT-NDJSON-001
"""

import pytest
from ndjson.models import NdjsonDocument


def _make_doc(records: list) -> NdjsonDocument:
    return NdjsonDocument(records)


# ── array_count ───────────────────────────────────────────────────────────────

class TestArrayCount:
    def test_no_records_zero(self):
        doc = _make_doc([])
        assert doc.array_count == 0

    def test_all_objects_zero_arrays(self):
        doc = _make_doc([{"a": 1}, {"b": 2}])
        assert doc.array_count == 0

    def test_one_array(self):
        doc = _make_doc([[1, 2, 3]])
        assert doc.array_count == 1

    def test_mixed_array_and_object(self):
        doc = _make_doc([{"a": 1}, [1, 2], [3, 4]])
        assert doc.array_count == 2

    def test_all_arrays(self):
        doc = _make_doc([[1], [2, 3], [4, 5, 6]])
        assert doc.array_count == 3


# ── scalar_count ──────────────────────────────────────────────────────────────

class TestScalarCount:
    def test_no_records_zero(self):
        doc = _make_doc([])
        assert doc.scalar_count == 0

    def test_all_objects_no_scalars(self):
        doc = _make_doc([{"a": 1}, {"b": 2}])
        assert doc.scalar_count == 0

    def test_all_arrays_no_scalars(self):
        doc = _make_doc([[1, 2], [3]])
        assert doc.scalar_count == 0

    def test_string_scalar(self):
        doc = _make_doc(["hello", "world"])
        assert doc.scalar_count == 2

    def test_numeric_scalar(self):
        doc = _make_doc([42, 3.14])
        assert doc.scalar_count == 2

    def test_mixed_types(self):
        doc = _make_doc([{"a": 1}, [1, 2], "text", 42])
        assert doc.scalar_count == 2


# ── object_fraction ───────────────────────────────────────────────────────────

class TestObjectFraction:
    def test_no_records_returns_zero(self):
        doc = _make_doc([])
        assert doc.object_fraction == pytest.approx(0.0)

    def test_all_objects_returns_one(self):
        doc = _make_doc([{"a": 1}, {"b": 2}, {"c": 3}])
        assert doc.object_fraction == pytest.approx(1.0)

    def test_no_objects_returns_zero(self):
        doc = _make_doc([[1, 2], [3, 4]])
        assert doc.object_fraction == pytest.approx(0.0)

    def test_half_objects(self):
        doc = _make_doc([{"a": 1}, {"b": 2}, [1], [2]])
        assert doc.object_fraction == pytest.approx(0.5)

    def test_one_of_three_objects(self):
        doc = _make_doc([{"a": 1}, [1, 2], "text"])
        assert doc.object_fraction == pytest.approx(1 / 3)


# ── cross-property consistency ────────────────────────────────────────────────

class TestCrossPropertyConsistency:
    def test_object_array_scalar_sum_to_total(self):
        records = [{"a": 1}, [1, 2], "text", 42, {"b": 2}]
        doc = _make_doc(records)
        assert doc.object_count + doc.array_count + doc.scalar_count == doc.record_count

    def test_all_objects_fraction_one(self):
        doc = _make_doc([{"x": i} for i in range(5)])
        assert doc.object_fraction == pytest.approx(1.0)
        assert doc.array_count == 0
        assert doc.scalar_count == 0

    def test_object_count_consistent_with_fraction(self):
        records = [{"a": 1}, {"b": 2}, [1, 2], "str"]
        doc = _make_doc(records)
        assert doc.object_fraction == pytest.approx(doc.object_count / doc.record_count)
