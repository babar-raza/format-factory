"""Tests for 10 new analytics: FODS/FODT/ODS/ODT/FODP deepening sprint R425."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from src.python.fods.neutral_model import (
    fods_total_cell_count_squared,
    fods_avg_cells_times_sheet_count,
    fods_total_cell_count,
    fods_sheet_count,
)
from src.python.fods import parse_fods_strict

from src.python.fodt.neutral_model import (
    fodt_word_count_squared,
    fodt_heading_count_plus_paragraph_count,
    fodt_word_count,
    fodt_heading_count,
    fodt_paragraph_count,
)

from src.python.ods.ods_parser import (
    ods_total_cells_squared,
    ods_avg_rows_times_sheet_count,
    ods_total_cells,
    ods_sheet_count,
)

from src.python.odt.odt_parser import (
    odt_paragraph_count_squared,
    odt_total_chars_plus_word_count,
    odt_paragraph_count,
    odt_total_char_count,
    odt_word_count,
)

from src.python.fodp.fodp_codec import (
    fodp_total_text_chars_squared,
    fodp_word_count_plus_slide_count,
    fodp_total_text_chars,
    fodp_word_count,
    fodp_slide_count,
)

_FODS = _REPO / "samples" / "by-format" / "fods" / "minimal-spreadsheet.fods"
_FODT = _REPO / "samples" / "by-format" / "fodt" / "minimal-document.fodt"
_ODS = _REPO / "samples" / "by-format" / "ods" / "valid" / "minimal-spreadsheet.ods"
_ODT = _REPO / "samples" / "by-format" / "odt" / "valid" / "minimal-document.odt"
_FODP = _REPO / "samples" / "by-format" / "fodp" / "title-only.fodp"


class TestFodsTotalCellCountSquared:
    def test_returns_int(self):
        wb = parse_fods_strict(_FODS)
        assert isinstance(fods_total_cell_count_squared(wb), int)

    def test_matches_formula(self):
        wb = parse_fods_strict(_FODS)
        tc = fods_total_cell_count(wb)
        assert fods_total_cell_count_squared(wb) == tc * tc

    def test_non_negative(self):
        wb = parse_fods_strict(_FODS)
        assert fods_total_cell_count_squared(wb) >= 0


class TestFodsAvgCellsTimesSheetCount:
    def test_returns_float(self):
        wb = parse_fods_strict(_FODS)
        assert isinstance(fods_avg_cells_times_sheet_count(wb), float)

    def test_equals_total_cells(self):
        wb = parse_fods_strict(_FODS)
        assert fods_avg_cells_times_sheet_count(wb) == float(fods_total_cell_count(wb))

    def test_non_negative(self):
        wb = parse_fods_strict(_FODS)
        assert fods_avg_cells_times_sheet_count(wb) >= 0.0


class TestFodtWordCountSquared:
    def test_returns_int(self):
        assert isinstance(fodt_word_count_squared(_FODT), int)

    def test_matches_formula(self):
        wc = fodt_word_count(_FODT)
        assert fodt_word_count_squared(_FODT) == wc * wc

    def test_non_negative(self):
        assert fodt_word_count_squared(_FODT) >= 0


class TestFodtHeadingCountPlusParagraphCount:
    def test_returns_int(self):
        assert isinstance(fodt_heading_count_plus_paragraph_count(_FODT), int)

    def test_matches_sum(self):
        assert fodt_heading_count_plus_paragraph_count(_FODT) == fodt_heading_count(_FODT) + fodt_paragraph_count(_FODT)

    def test_non_negative(self):
        assert fodt_heading_count_plus_paragraph_count(_FODT) >= 0


class TestOdsTotalCellsSquared:
    def test_returns_int(self):
        assert isinstance(ods_total_cells_squared(_ODS), int)

    def test_matches_formula(self):
        tc = ods_total_cells(_ODS)
        assert ods_total_cells_squared(_ODS) == tc * tc

    def test_non_negative(self):
        assert ods_total_cells_squared(_ODS) >= 0


class TestOdsAvgRowsTimesSheetCount:
    def test_returns_int(self):
        assert isinstance(ods_avg_rows_times_sheet_count(_ODS), int)

    def test_non_negative(self):
        assert ods_avg_rows_times_sheet_count(_ODS) >= 0


class TestOdtParagraphCountSquared:
    def test_returns_int(self):
        assert isinstance(odt_paragraph_count_squared(_ODT), int)

    def test_matches_formula(self):
        pc = odt_paragraph_count(_ODT)
        assert odt_paragraph_count_squared(_ODT) == pc * pc

    def test_non_negative(self):
        assert odt_paragraph_count_squared(_ODT) >= 0


class TestOdtTotalCharsPlusWordCount:
    def test_returns_int(self):
        assert isinstance(odt_total_chars_plus_word_count(_ODT), int)

    def test_matches_sum(self):
        assert odt_total_chars_plus_word_count(_ODT) == odt_total_char_count(_ODT) + odt_word_count(_ODT)

    def test_non_negative(self):
        assert odt_total_chars_plus_word_count(_ODT) >= 0


class TestFodpTotalTextCharsSquared:
    def test_returns_int(self):
        assert isinstance(fodp_total_text_chars_squared(_FODP), int)

    def test_matches_formula(self):
        tc = fodp_total_text_chars(_FODP)
        assert fodp_total_text_chars_squared(_FODP) == tc * tc

    def test_non_negative(self):
        assert fodp_total_text_chars_squared(_FODP) >= 0


class TestFodpWordCountPlusSlideCount:
    def test_returns_int(self):
        assert isinstance(fodp_word_count_plus_slide_count(_FODP), int)

    def test_matches_sum(self):
        assert fodp_word_count_plus_slide_count(_FODP) == fodp_word_count(_FODP) + fodp_slide_count(_FODP)

    def test_non_negative(self):
        assert fodp_word_count_plus_slide_count(_FODP) >= 0
