"""Tests for deduplicate() — NDJSON record deduplication.

Sprint: FORMAT-FACTORY-AUTONOMY-ACCELERATION-SPRINT-5-001
TC-PRODUCT-NDJSON-DEDUPLICATE
"""
from __future__ import annotations

import sys
from pathlib import Path


_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ndjson.ndjson_codec import deduplicate

_SAMPLE = b'{"id": 1, "v": "a"}\n{"id": 2, "v": "b"}\n{"id": 1, "v": "c"}\n'


class TestDeduplicate:
    def test_removes_duplicate_by_key(self):
        result = deduplicate(_SAMPLE, "id")
        ids = [r["id"] for r in result]
        assert ids.count(1) == 1
        assert ids.count(2) == 1

    def test_keeps_first_occurrence(self):
        result = deduplicate(_SAMPLE, "id")
        r = next(r for r in result if r["id"] == 1)
        assert r["v"] == "a"

    def test_no_duplicates_unchanged(self):
        data = b'{"id": 1}\n{"id": 2}\n{"id": 3}\n'
        result = deduplicate(data, "id")
        assert len(result) == 3

    def test_empty_source(self):
        assert deduplicate(b"", "id") == []

    def test_records_missing_key_kept(self):
        data = b'{"id": 1}\n{"name": "x"}\n{"id": 1}\n'
        result = deduplicate(data, "id")
        assert any("name" in r for r in result)

    def test_non_dict_records_kept(self):
        data = b'"hello"\n"hello"\n{"id": 1}\n'
        result = deduplicate(data, "id")
        assert "hello" in result

    def test_returns_list(self):
        assert isinstance(deduplicate(_SAMPLE, "id"), list)

    def test_all_duplicates_reduced_to_one(self):
        data = b'{"k": "x"}\n{"k": "x"}\n{"k": "x"}\n'
        result = deduplicate(data, "k")
        assert len(result) == 1

    def test_different_key_no_dedup(self):
        result = deduplicate(_SAMPLE, "missing_key")
        assert len(result) == 3
