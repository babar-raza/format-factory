"""Sprint R429 — FODS/FODT/ODS/ODT/FODP deepening round 3."""
import sys, pathlib, pytest

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fods.neutral_model import fods_row_count_squared, fods_avg_cells_plus_total_cells, fods_total_cell_count
from src.python.fods import parse_fods_strict
from src.python.fodt.neutral_model import fodt_paragraph_count_squared, fodt_total_chars_plus_word_count, fodt_paragraph_count, fodt_total_char_count, fodt_word_count
from src.python.ods.ods_parser import ods_sheet_count_squared, ods_total_cells_plus_row_count, ods_total_cells, ods_total_row_count, parse_ods_strict
from src.python.odt.odt_parser import odt_word_count_squared, odt_total_chars_times_two, odt_word_count, odt_total_char_count
from src.python.fodp.fodp_codec import fodp_slide_count_squared, fodp_word_count_squared, fodp_slide_count, fodp_word_count

_SAMPLES = _REPO / "samples" / "by-format"
_FODS = _SAMPLES / "fods" / "minimal-spreadsheet.fods"
_FODT = _SAMPLES / "fodt" / "minimal-document.fodt"
_ODS = _SAMPLES / "ods" / "valid" / "minimal-spreadsheet.ods"
_ODT = _SAMPLES / "odt" / "valid" / "minimal-document.odt"
_FODP = _SAMPLES / "fodp" / "title-only.fodp"


# === FODS ===
class TestFodsRowCountSquared:
    def test_returns_int(self):
        wb = parse_fods_strict(_FODS)
        assert isinstance(fods_row_count_squared(wb), int)

    def test_equals_square(self):
        wb = parse_fods_strict(_FODS)
        sheets = wb.get("sheets", [])
        rc = sum(len(s.get("rows", [])) for s in sheets)
        assert fods_row_count_squared(wb) == rc * rc

    def test_non_negative(self):
        wb = parse_fods_strict(_FODS)
        assert fods_row_count_squared(wb) >= 0


class TestFodsAvgCellsPlusTotalCells:
    def test_returns_number(self):
        wb = parse_fods_strict(_FODS)
        assert isinstance(fods_avg_cells_plus_total_cells(wb), (int, float))

    def test_exceeds_total(self):
        wb = parse_fods_strict(_FODS)
        tc = fods_total_cell_count(wb)
        assert fods_avg_cells_plus_total_cells(wb) >= tc

    def test_non_negative(self):
        wb = parse_fods_strict(_FODS)
        assert fods_avg_cells_plus_total_cells(wb) >= 0


# === FODT ===
class TestFodtParagraphCountSquared:
    def test_returns_int(self):
        assert isinstance(fodt_paragraph_count_squared(_FODT), int)

    def test_equals_square(self):
        pc = fodt_paragraph_count(_FODT)
        assert fodt_paragraph_count_squared(_FODT) == pc * pc

    def test_non_negative(self):
        assert fodt_paragraph_count_squared(_FODT) >= 0


class TestFodtTotalCharsPlusWordCount:
    def test_returns_int(self):
        assert isinstance(fodt_total_chars_plus_word_count(_FODT), int)

    def test_equals_sum(self):
        assert fodt_total_chars_plus_word_count(_FODT) == fodt_total_char_count(_FODT) + fodt_word_count(_FODT)

    def test_non_negative(self):
        assert fodt_total_chars_plus_word_count(_FODT) >= 0


# === ODS ===
class TestOdsSheetCountSquared:
    def test_returns_int(self):
        assert isinstance(ods_sheet_count_squared(_ODS), int)

    def test_equals_square(self):
        doc = parse_ods_strict(_ODS)
        sc = len(doc.sheets)
        assert ods_sheet_count_squared(_ODS) == sc * sc

    def test_non_negative(self):
        assert ods_sheet_count_squared(_ODS) >= 0


class TestOdsTotalCellsPlusRowCount:
    def test_returns_int(self):
        assert isinstance(ods_total_cells_plus_row_count(_ODS), int)

    def test_equals_sum(self):
        assert ods_total_cells_plus_row_count(_ODS) == ods_total_cells(_ODS) + ods_total_row_count(_ODS)

    def test_non_negative(self):
        assert ods_total_cells_plus_row_count(_ODS) >= 0


# === ODT ===
class TestOdtWordCountSquared:
    def test_returns_int(self):
        assert isinstance(odt_word_count_squared(_ODT), int)

    def test_equals_square(self):
        wc = odt_word_count(_ODT)
        assert odt_word_count_squared(_ODT) == wc * wc

    def test_non_negative(self):
        assert odt_word_count_squared(_ODT) >= 0


class TestOdtTotalCharsTimesTwo:
    def test_returns_int(self):
        assert isinstance(odt_total_chars_times_two(_ODT), int)

    def test_equals_double(self):
        assert odt_total_chars_times_two(_ODT) == odt_total_char_count(_ODT) * 2

    def test_non_negative(self):
        assert odt_total_chars_times_two(_ODT) >= 0


# === FODP ===
class TestFodpSlideCountSquared:
    def test_returns_int(self):
        assert isinstance(fodp_slide_count_squared(_FODP), int)

    def test_equals_square(self):
        sc = fodp_slide_count(_FODP)
        assert fodp_slide_count_squared(_FODP) == sc * sc

    def test_non_negative(self):
        assert fodp_slide_count_squared(_FODP) >= 0


class TestFodpWordCountSquared:
    def test_returns_int(self):
        assert isinstance(fodp_word_count_squared(_FODP), int)

    def test_equals_square(self):
        wc = fodp_word_count(_FODP)
        assert fodp_word_count_squared(_FODP) == wc * wc

    def test_non_negative(self):
        assert fodp_word_count_squared(_FODP) >= 0
