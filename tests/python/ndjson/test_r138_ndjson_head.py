"""Tests for head() — NDJSON first N records.

Sprint: FORMAT-FACTORY-AUTONOMY-ACCELERATION-SPRINT-5-001
TC-PRODUCT-NDJSON-HEAD
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ndjson.ndjson_codec import head

_SAMPLE = b'{"i": 0}\n{"i": 1}\n{"i": 2}\n{"i": 3}\n{"i": 4}\n'


class TestHead:
    def test_head_three(self):
        result = head(_SAMPLE, 3)
        assert len(result) == 3
        assert result[0]["i"] == 0
        assert result[2]["i"] == 2

    def test_head_zero(self):
        assert head(_SAMPLE, 0) == []

    def test_head_more_than_available(self):
        result = head(_SAMPLE, 100)
        assert len(result) == 5

    def test_head_one(self):
        result = head(_SAMPLE, 1)
        assert len(result) == 1
        assert result[0]["i"] == 0

    def test_head_empty_source(self):
        assert head(b"", 5) == []

    def test_negative_n_raises(self):
        with pytest.raises(ValueError):
            head(_SAMPLE, -1)

    def test_returns_list(self):
        assert isinstance(head(_SAMPLE, 2), list)

    def test_records_in_order(self):
        result = head(_SAMPLE, 4)
        assert [r["i"] for r in result] == [0, 1, 2, 3]

    def test_exact_n(self):
        result = head(_SAMPLE, 5)
        assert len(result) == 5
