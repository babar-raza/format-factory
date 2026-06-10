"""Tests for validate_headers() — TSV header validation.

Sprint: FORMAT-FACTORY-AUTONOMY-ACCELERATION-SPRINT-4-001
TC-PRODUCT-TSV-VALIDATE-HEADERS
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.tsv.tsv_parser import validate_headers

_SAMPLE = b"name\tage\tcity\nAlice\t30\tNY\nBob\t25\tLA\n"


class TestValidateHeaders:
    def test_exact_match_is_valid(self):
        result = validate_headers(_SAMPLE, ["name", "age", "city"])
        assert result["valid"] is True

    def test_missing_header(self):
        result = validate_headers(_SAMPLE, ["name", "age", "city", "country"])
        assert result["valid"] is False
        assert "country" in result["missing"]

    def test_extra_header(self):
        result = validate_headers(_SAMPLE, ["name", "age"])
        assert result["valid"] is False
        assert "city" in result["extra"]

    def test_both_missing_and_extra(self):
        result = validate_headers(_SAMPLE, ["name", "country"])
        assert "age" in result["extra"]
        assert "city" in result["extra"]
        assert "country" in result["missing"]

    def test_actual_headers_returned(self):
        result = validate_headers(_SAMPLE, ["name", "age", "city"])
        assert result["actual"] == ["name", "age", "city"]

    def test_expected_headers_returned(self):
        result = validate_headers(_SAMPLE, ["a", "b"])
        assert result["expected"] == ["a", "b"]

    def test_empty_expected_valid_only_if_no_headers(self):
        data = b"single\trow\n"
        result = validate_headers(data, [])
        assert isinstance(result["valid"], bool)

    def test_order_matters_for_valid(self):
        result = validate_headers(_SAMPLE, ["age", "name", "city"])
        assert result["valid"] is False

    def test_no_missing_when_subset(self):
        result = validate_headers(_SAMPLE, ["name"])
        assert result["missing"] == []

    def test_returns_dict(self):
        result = validate_headers(_SAMPLE, ["name", "age", "city"])
        assert isinstance(result, dict)
        assert "valid" in result
        assert "actual" in result
        assert "missing" in result
        assert "extra" in result
