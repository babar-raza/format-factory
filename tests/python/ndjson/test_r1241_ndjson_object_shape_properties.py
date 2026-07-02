"""Tests for R1241: NdjsonDocument object shape analysis properties.

Properties under test:
    has_uniform_keys — all object records have same key count (vacuously True for none)
    avg_keys         — average key count across object records (0.0 if none)
    is_wide_objects  — max_keys > 20

spec_fact_ref: FACT-NDJSON-001
"""

import pytest
from ndjson.models import NdjsonDocument


def _make_doc(records: list) -> NdjsonDocument:
    return NdjsonDocument(records)


# ── has_uniform_keys ──────────────────────────────────────────────────────────

class TestHasUniformKeys:
    def test_empty_document_uniform(self):
        doc = _make_doc([])
        assert doc.has_uniform_keys is True

    def test_no_object_records_uniform(self):
        doc = _make_doc([1, 2, 3])  # scalars, no objects
        assert doc.has_uniform_keys is True

    def test_all_same_key_count_uniform(self):
        doc = _make_doc([{"a": 1, "b": 2}, {"c": 3, "d": 4}, {"e": 5, "f": 6}])
        assert doc.has_uniform_keys is True

    def test_different_key_counts_not_uniform(self):
        doc = _make_doc([{"a": 1}, {"a": 1, "b": 2}])
        assert doc.has_uniform_keys is False

    def test_single_object_uniform(self):
        doc = _make_doc([{"a": 1, "b": 2, "c": 3}])
        assert doc.has_uniform_keys is True

    def test_mixed_types_uses_only_objects(self):
        # Arrays are ignored; only 2 objects with same key count
        doc = _make_doc([{"a": 1}, [1, 2], {"b": 2}])
        assert doc.has_uniform_keys is True

    def test_three_key_counts_not_uniform(self):
        doc = _make_doc([{"a": 1}, {"a": 1, "b": 2}, {"a": 1, "b": 2, "c": 3}])
        assert doc.has_uniform_keys is False


# ── avg_keys ──────────────────────────────────────────────────────────────────

class TestAvgKeys:
    def test_empty_returns_zero(self):
        doc = _make_doc([])
        assert doc.avg_keys == 0.0

    def test_no_object_records_returns_zero(self):
        doc = _make_doc([1, "text", [1, 2]])
        assert doc.avg_keys == 0.0

    def test_single_object_avg(self):
        doc = _make_doc([{"a": 1, "b": 2, "c": 3}])
        assert doc.avg_keys == pytest.approx(3.0)

    def test_uniform_objects_avg(self):
        doc = _make_doc([{"a": 1, "b": 2}, {"c": 3, "d": 4}])
        assert doc.avg_keys == pytest.approx(2.0)

    def test_variable_objects_avg(self):
        doc = _make_doc([{"a": 1}, {"a": 1, "b": 2, "c": 3}])  # 1 + 3 = 4 / 2 = 2.0
        assert doc.avg_keys == pytest.approx(2.0)

    def test_fractional_avg(self):
        doc = _make_doc([{"a": 1}, {"a": 1, "b": 2}])  # 1 + 2 = 3 / 2 = 1.5
        assert doc.avg_keys == pytest.approx(1.5)


# ── is_wide_objects ───────────────────────────────────────────────────────────

class TestIsWideObjects:
    def test_empty_not_wide(self):
        doc = _make_doc([])
        assert doc.is_wide_objects is False

    def test_no_objects_not_wide(self):
        doc = _make_doc([1, 2, 3])
        assert doc.is_wide_objects is False

    def test_21_keys_is_wide(self):
        record = {str(i): i for i in range(21)}
        doc = _make_doc([record])
        assert doc.is_wide_objects is True

    def test_exactly_20_keys_not_wide(self):
        record = {str(i): i for i in range(20)}
        doc = _make_doc([record])
        assert doc.is_wide_objects is False

    def test_fewer_than_20_keys_not_wide(self):
        doc = _make_doc([{"a": 1, "b": 2, "c": 3}])
        assert doc.is_wide_objects is False

    def test_one_wide_object_triggers_true(self):
        narrow = {"a": 1}
        wide = {str(i): i for i in range(25)}
        doc = _make_doc([narrow, wide])
        assert doc.is_wide_objects is True


# ── cross-property consistency ────────────────────────────────────────────────

class TestCrossPropertyConsistency:
    def test_uniform_consistent_with_min_max(self):
        doc = _make_doc([{"a": 1, "b": 2}, {"c": 3, "d": 4}])
        assert doc.has_uniform_keys is True
        assert doc.min_keys == doc.max_keys == 2

    def test_non_uniform_min_ne_max(self):
        doc = _make_doc([{"a": 1}, {"a": 1, "b": 2, "c": 3}])
        assert doc.has_uniform_keys is False
        assert doc.min_keys != doc.max_keys

    def test_wide_objects_consistent_with_max_keys(self):
        record = {str(i): i for i in range(25)}
        doc = _make_doc([record])
        assert doc.is_wide_objects is True
        assert doc.max_keys == 25

    def test_avg_consistent_with_sum(self):
        doc = _make_doc([{"a": 1, "b": 2}, {"a": 1, "b": 2, "c": 3, "d": 4}])
        assert doc.avg_keys == pytest.approx((2 + 4) / 2)
