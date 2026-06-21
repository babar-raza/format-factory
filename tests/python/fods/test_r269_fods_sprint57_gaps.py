"""Tests for FODS Sprint 57 gap closure (batch 2).

Closes:
  GAP-FODS-FOSS-FODS_FILE_SI-001   (Fods File Size Bytes)
  GAP-FODS-FOSS-FODS_MAX_SHE-001   (Fods Max Sheet Row Count)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.fods import parse_fods_strict, fods_file_size_bytes, fods_max_sheet_row_count

_DIR = _REPO / "samples" / "by-format" / "fods"
_MINIMAL = str(_DIR / "minimal-spreadsheet.fods")
_FORMULA = str(_DIR / "formula-basic.fods")
_MULTI = str(_DIR / "multi-sheet-basic.fods")
_TYPED = str(_DIR / "typed-values-basic.fods")


class TestFodsFileSizeBytes:
    def test_return_type(self):
        assert isinstance(fods_file_size_bytes(_MINIMAL), int)

    def test_exact_1421_for_minimal(self):
        assert fods_file_size_bytes(_MINIMAL) == 1421

    def test_exact_1973_for_formula(self):
        assert fods_file_size_bytes(_FORMULA) == 1973

    def test_exact_2008_for_multi(self):
        assert fods_file_size_bytes(_MULTI) == 2008

    def test_positive(self):
        assert fods_file_size_bytes(_MINIMAL) > 0

    def test_consistent_across_calls(self):
        assert fods_file_size_bytes(_MINIMAL) == fods_file_size_bytes(_MINIMAL)


class TestFodsMaxSheetRowCount:
    def test_return_type(self):
        wb = parse_fods_strict(_MINIMAL)
        assert isinstance(fods_max_sheet_row_count(wb), int)

    def test_exact_1_for_minimal(self):
        wb = parse_fods_strict(_MINIMAL)
        assert fods_max_sheet_row_count(wb) == 1

    def test_exact_4_for_formula(self):
        wb = parse_fods_strict(_FORMULA)
        assert fods_max_sheet_row_count(wb) == 4

    def test_exact_2_for_multi(self):
        wb = parse_fods_strict(_MULTI)
        assert fods_max_sheet_row_count(wb) == 2

    def test_exact_4_for_typed(self):
        wb = parse_fods_strict(_TYPED)
        assert fods_max_sheet_row_count(wb) == 4

    def test_positive(self):
        wb = parse_fods_strict(_MINIMAL)
        assert fods_max_sheet_row_count(wb) > 0

    def test_consistent_across_calls(self):
        wb = parse_fods_strict(_MINIMAL)
        assert fods_max_sheet_row_count(wb) == fods_max_sheet_row_count(wb)
