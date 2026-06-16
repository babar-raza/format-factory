"""Tests for ods_numeric_ratio and ods_is_square (Sprint 66)."""
import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src" / "python"))

from ods.ods_parser import ods_numeric_ratio, ods_is_square

ODS = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "ods" / "valid"


class TestOdsNumericRatio:
    def test_minimal(self):
        assert abs(ods_numeric_ratio(ODS / "minimal-spreadsheet.ods") - 0.25) < 0.01

    def test_numeric_row(self):
        assert abs(ods_numeric_ratio(ODS / "numeric-row.ods") - 1.0) < 0.01

    def test_single_cell(self):
        assert abs(ods_numeric_ratio(ODS / "single-cell.ods") - 0.0) < 0.01

    def test_returns_float(self):
        assert isinstance(ods_numeric_ratio(ODS / "minimal-spreadsheet.ods"), float)

    def test_nonnegative(self):
        for f in ["minimal-spreadsheet.ods", "numeric-row.ods", "single-cell.ods"]:
            assert ods_numeric_ratio(ODS / f) >= 0.0


class TestOdsIsSquare:
    def test_minimal_is_square(self):
        assert ods_is_square(ODS / "minimal-spreadsheet.ods") is True

    def test_numeric_row_not_square(self):
        assert ods_is_square(ODS / "numeric-row.ods") is False

    def test_single_cell_is_square(self):
        assert ods_is_square(ODS / "single-cell.ods") is True

    def test_returns_bool(self):
        assert isinstance(ods_is_square(ODS / "minimal-spreadsheet.ods"), bool)

    def test_all_files(self):
        results = [ods_is_square(ODS / f) for f in ["minimal-spreadsheet.ods", "numeric-row.ods", "single-cell.ods"]]
        assert any(r is True for r in results)
        assert any(r is False for r in results)
