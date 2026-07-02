"""R1227: NDJSON size classification properties — is_small, is_large, min_keys.

Tests for NdjsonDocument size and key analysis properties added in R1227.
Spec refs: FACT-NDJSON-001 (ndjson:record structure).
"""

from __future__ import annotations

import pytest
from pathlib import Path

import sys
_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ndjson.models import NdjsonDocument

SAMPLES = Path("samples/by-format/ndjson/valid")


def _make_doc(*records) -> NdjsonDocument:
    """Build an NdjsonDocument from positional record arguments."""
    return NdjsonDocument(list(records))


class TestIsSmall:
    def test_empty_is_small(self):
        doc = _make_doc()
        assert doc.is_small is True

    def test_one_record_is_small(self):
        doc = _make_doc({"a": 1})
        assert doc.is_small is True

    def test_ten_records_is_small(self):
        doc = NdjsonDocument([{"i": i} for i in range(10)])
        assert doc.is_small is True

    def test_eleven_records_not_small(self):
        doc = NdjsonDocument([{"i": i} for i in range(11)])
        assert doc.is_small is False

    def test_hundred_records_not_small(self):
        doc = NdjsonDocument([{"i": i} for i in range(100)])
        assert doc.is_small is False

    def test_returns_bool(self):
        doc = _make_doc({"a": 1})
        assert isinstance(doc.is_small, bool)

    def test_from_file(self):
        doc = NdjsonDocument.from_file(SAMPLES / "minimal.ndjson")
        assert isinstance(doc.is_small, bool)


class TestIsLarge:
    def test_empty_not_large(self):
        doc = _make_doc()
        assert doc.is_large is False

    def test_ten_not_large(self):
        doc = NdjsonDocument([{"i": i} for i in range(10)])
        assert doc.is_large is False

    def test_thousand_not_large(self):
        """Exactly 1000 — not large (threshold is > 1000)."""
        doc = NdjsonDocument([{"i": i} for i in range(1000)])
        assert doc.is_large is False

    def test_thousand_one_is_large(self):
        doc = NdjsonDocument([{"i": i} for i in range(1001)])
        assert doc.is_large is True

    def test_returns_bool(self):
        doc = _make_doc({"a": 1})
        assert isinstance(doc.is_large, bool)

    def test_not_large_from_file(self):
        doc = NdjsonDocument.from_file(SAMPLES / "minimal.ndjson")
        assert doc.is_large is False


class TestMinKeys:
    def test_empty_zero(self):
        doc = _make_doc()
        assert doc.min_keys == 0

    def test_no_objects_zero(self):
        doc = _make_doc([1, 2], "hello", 42)
        assert doc.min_keys == 0

    def test_single_object_returns_its_count(self):
        doc = _make_doc({"a": 1, "b": 2})
        assert doc.min_keys == 2

    def test_multiple_objects_returns_min(self):
        doc = NdjsonDocument([{"a": 1, "b": 2}, {"x": 1}])
        assert doc.min_keys == 1

    def test_mixed_records_uses_objects_only(self):
        """min_keys only considers dict records."""
        doc = NdjsonDocument([{"a": 1, "b": 2, "c": 3}, [1, 2], {"d": 4}])
        assert doc.min_keys == 1

    def test_returns_int(self):
        doc = _make_doc({"a": 1})
        assert isinstance(doc.min_keys, int)

    def test_min_keys_le_max_keys(self):
        doc = NdjsonDocument([{"a": 1}, {"b": 2, "c": 3, "d": 4}])
        assert doc.min_keys <= doc.max_keys

    def test_from_file(self):
        doc = NdjsonDocument.from_file(SAMPLES / "minimal.ndjson")
        assert isinstance(doc.min_keys, int)
        assert doc.min_keys >= 0
