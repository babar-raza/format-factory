"""
test_r158_ods_count_sheets.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT18-001
Added: 2026-06-10

Tests for ODS count_sheets function.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ods.ods_parser import count_sheets, OdsError

_SAMPLES = _REPO / "samples" / "by-format" / "ods" / "valid"


class TestCountSheets:
    def test_minimal_spreadsheet(self):
        count = count_sheets(_SAMPLES / "minimal-spreadsheet.ods")
        assert count >= 1

    def test_single_cell(self):
        count = count_sheets(_SAMPLES / "single-cell.ods")
        assert count >= 1

    def test_numeric_row(self):
        count = count_sheets(_SAMPLES / "numeric-row.ods")
        assert count >= 1

    def test_returns_int(self):
        count = count_sheets(_SAMPLES / "minimal-spreadsheet.ods")
        assert isinstance(count, int)
