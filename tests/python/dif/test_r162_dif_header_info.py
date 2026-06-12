"""
test_r162_dif_header_info.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT22-001
Added: 2026-06-12

Tests for DIF get_header_info function.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from dif.dif_parser import get_header_info

_SAMPLES = _REPO / "samples" / "by-format" / "dif" / "valid"


class TestGetHeaderInfo:
    def test_returns_dict(self):
        result = get_header_info(_SAMPLES / "single-cell.dif")
        assert isinstance(result, dict)

    def test_has_required_keys(self):
        result = get_header_info(_SAMPLES / "single-cell.dif")
        assert "title" in result
        assert "vectors" in result
        assert "tuples" in result
        assert "row_count" in result

    def test_vectors_is_int(self):
        result = get_header_info(_SAMPLES / "numeric-row.dif")
        assert isinstance(result["vectors"], int)

    def test_tuples_is_int(self):
        result = get_header_info(_SAMPLES / "numeric-row.dif")
        assert isinstance(result["tuples"], int)

    def test_row_count_is_int(self):
        result = get_header_info(_SAMPLES / "numeric-row.dif")
        assert isinstance(result["row_count"], int)

    def test_row_count_nonnegative(self):
        result = get_header_info(_SAMPLES / "single-cell.dif")
        assert result["row_count"] >= 0

    def test_minimal_2x2(self):
        result = get_header_info(_SAMPLES / "minimal-2x2.dif")
        assert result["row_count"] >= 1
