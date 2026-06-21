"""Tests for 6 new analytics: SYLK/ABW/ODS deepening sprint R422."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from src.python.sylk.sylk_parser import (
    sylk_cell_count_squared,
    sylk_cell_count_plus_row_count,
    sylk_total_cell_count,
    parse_sylk_strict,
)

from src.python.abw.abw_codec import (
    abw_paragraph_count_squared,
    abw_word_count_plus_paragraph_count,
    abw_paragraph_count,
    abw_word_count,
)

from src.python.ods.ods_parser import (
    ods_sheet_count_squared,
    ods_total_cells_plus_sheet_count,
    ods_sheet_count,
    ods_total_cells,
)

_SYLK = _REPO / "samples" / "by-format" / "sylk" / "valid" / "minimal-2x2.slk"
_ABW = _REPO / "samples" / "by-format" / "abw" / "minimal-document.abw"
_ODS = _REPO / "samples" / "by-format" / "ods" / "valid" / "minimal-spreadsheet.ods"


class TestSylkCellCountSquared:
    def test_returns_int(self):
        assert isinstance(sylk_cell_count_squared(_SYLK), int)

    def test_matches_formula(self):
        tc = sylk_total_cell_count(_SYLK)
        assert sylk_cell_count_squared(_SYLK) == tc * tc

    def test_positive(self):
        assert sylk_cell_count_squared(_SYLK) >= 1


class TestSylkCellCountPlusRowCount:
    def test_returns_int(self):
        assert isinstance(sylk_cell_count_plus_row_count(_SYLK), int)

    def test_positive(self):
        assert sylk_cell_count_plus_row_count(_SYLK) >= 1

    def test_consistent(self):
        assert sylk_cell_count_plus_row_count(_SYLK) == sylk_cell_count_plus_row_count(_SYLK)


class TestAbwParagraphCountSquared:
    def test_returns_int(self):
        assert isinstance(abw_paragraph_count_squared(_ABW), int)

    def test_matches_formula(self):
        pc = abw_paragraph_count(_ABW)
        assert abw_paragraph_count_squared(_ABW) == pc * pc

    def test_nonnegative(self):
        assert abw_paragraph_count_squared(_ABW) >= 0


class TestAbwWordCountPlusParagraphCount:
    def test_returns_int(self):
        assert isinstance(abw_word_count_plus_paragraph_count(_ABW), int)

    def test_matches_sum(self):
        assert abw_word_count_plus_paragraph_count(_ABW) == abw_word_count(_ABW) + abw_paragraph_count(_ABW)

    def test_nonnegative(self):
        assert abw_word_count_plus_paragraph_count(_ABW) >= 0


class TestOdsSheetCountSquared:
    def test_returns_int(self):
        assert isinstance(ods_sheet_count_squared(_ODS), int)

    def test_matches_formula(self):
        sc = ods_sheet_count(_ODS)
        assert ods_sheet_count_squared(_ODS) == sc * sc

    def test_positive(self):
        assert ods_sheet_count_squared(_ODS) >= 1


class TestOdsTotalCellsPlusSheetCount:
    def test_returns_int(self):
        assert isinstance(ods_total_cells_plus_sheet_count(_ODS), int)

    def test_matches_sum(self):
        assert ods_total_cells_plus_sheet_count(_ODS) == ods_total_cells(_ODS) + ods_sheet_count(_ODS)

    def test_positive(self):
        assert ods_total_cells_plus_sheet_count(_ODS) >= 1
