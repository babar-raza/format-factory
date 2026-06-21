"""Sprint 261 — Product deepening: FODS, FODT, ODT, TSV composite analytics."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

FODS_SAMPLE = _REPO / "samples" / "by-format" / "fods" / "minimal-spreadsheet.fods"
FODT_SAMPLE = _REPO / "samples" / "by-format" / "fodt" / "minimal-document.fodt"
ODT_SAMPLE = _REPO / "samples" / "by-format" / "odt" / "valid" / "minimal-document.odt"
TSV_SAMPLE = _REPO / "samples" / "by-format" / "tsv" / "minimal-2x2.tsv"

from src.python.fods import (
    parse_fods_strict,
    fods_sheet_count_times_1000_plus_total_cell_count_squared,
    fods_total_cell_count_times_sheet_count_plus_sheet_count_times_500,
)
from src.python.fodt import (
    fodt_paragraph_count_times_100_plus_word_count_squared_plus_file_size_mod_23,
    fodt_char_count_times_paragraph_count_plus_word_count_times_50_plus_file_size_mod_17,
)
from src.python.odt import (
    odt_paragraph_count_times_200_plus_char_count_squared_plus_file_size_mod_29,
    odt_word_count_times_char_count_plus_paragraph_count_times_100_plus_file_size_mod_19,
)
from src.python.tsv import (
    tsv_row_count_times_column_count_plus_file_size_mod_11_times_100,
    tsv_unique_value_count_squared_plus_row_count_times_100_plus_file_size,
)


def _fods_wb():
    return parse_fods_strict(FODS_SAMPLE)


class TestFodsSheetTimes1000:
    def test_returns_int(self):
        assert isinstance(fods_sheet_count_times_1000_plus_total_cell_count_squared(_fods_wb()), int)

    def test_positive(self):
        assert fods_sheet_count_times_1000_plus_total_cell_count_squared(_fods_wb()) > 0

    def test_deterministic(self):
        r1 = fods_sheet_count_times_1000_plus_total_cell_count_squared(_fods_wb())
        r2 = fods_sheet_count_times_1000_plus_total_cell_count_squared(_fods_wb())
        assert r1 == r2

    def test_expected_value(self):
        assert fods_sheet_count_times_1000_plus_total_cell_count_squared(_fods_wb()) == 1001


class TestFodsTotalCellTimesSheet:
    def test_returns_int(self):
        assert isinstance(fods_total_cell_count_times_sheet_count_plus_sheet_count_times_500(_fods_wb()), int)

    def test_positive(self):
        assert fods_total_cell_count_times_sheet_count_plus_sheet_count_times_500(_fods_wb()) > 0

    def test_deterministic(self):
        r1 = fods_total_cell_count_times_sheet_count_plus_sheet_count_times_500(_fods_wb())
        r2 = fods_total_cell_count_times_sheet_count_plus_sheet_count_times_500(_fods_wb())
        assert r1 == r2

    def test_expected_value(self):
        assert fods_total_cell_count_times_sheet_count_plus_sheet_count_times_500(_fods_wb()) == 501


class TestFodtParaCountTimes100:
    def test_returns_int(self):
        assert isinstance(fodt_paragraph_count_times_100_plus_word_count_squared_plus_file_size_mod_23(FODT_SAMPLE), int)

    def test_positive(self):
        assert fodt_paragraph_count_times_100_plus_word_count_squared_plus_file_size_mod_23(FODT_SAMPLE) > 0

    def test_deterministic(self):
        r1 = fodt_paragraph_count_times_100_plus_word_count_squared_plus_file_size_mod_23(FODT_SAMPLE)
        r2 = fodt_paragraph_count_times_100_plus_word_count_squared_plus_file_size_mod_23(FODT_SAMPLE)
        assert r1 == r2

    def test_expected_value(self):
        assert fodt_paragraph_count_times_100_plus_word_count_squared_plus_file_size_mod_23(FODT_SAMPLE) == 122


class TestFodtCharCountTimesPara:
    def test_returns_int(self):
        assert isinstance(fodt_char_count_times_paragraph_count_plus_word_count_times_50_plus_file_size_mod_17(FODT_SAMPLE), int)

    def test_positive(self):
        assert fodt_char_count_times_paragraph_count_plus_word_count_times_50_plus_file_size_mod_17(FODT_SAMPLE) > 0

    def test_deterministic(self):
        r1 = fodt_char_count_times_paragraph_count_plus_word_count_times_50_plus_file_size_mod_17(FODT_SAMPLE)
        r2 = fodt_char_count_times_paragraph_count_plus_word_count_times_50_plus_file_size_mod_17(FODT_SAMPLE)
        assert r1 == r2

    def test_expected_value(self):
        assert fodt_char_count_times_paragraph_count_plus_word_count_times_50_plus_file_size_mod_17(FODT_SAMPLE) == 123


class TestOdtParaCountTimes200:
    def test_returns_int(self):
        assert isinstance(odt_paragraph_count_times_200_plus_char_count_squared_plus_file_size_mod_29(ODT_SAMPLE), int)

    def test_positive(self):
        assert odt_paragraph_count_times_200_plus_char_count_squared_plus_file_size_mod_29(ODT_SAMPLE) > 0

    def test_deterministic(self):
        r1 = odt_paragraph_count_times_200_plus_char_count_squared_plus_file_size_mod_29(ODT_SAMPLE)
        r2 = odt_paragraph_count_times_200_plus_char_count_squared_plus_file_size_mod_29(ODT_SAMPLE)
        assert r1 == r2

    def test_expected_value(self):
        assert odt_paragraph_count_times_200_plus_char_count_squared_plus_file_size_mod_29(ODT_SAMPLE) == 392


class TestOdtWordTimesChar:
    def test_returns_int(self):
        assert isinstance(odt_word_count_times_char_count_plus_paragraph_count_times_100_plus_file_size_mod_19(ODT_SAMPLE), int)

    def test_positive(self):
        assert odt_word_count_times_char_count_plus_paragraph_count_times_100_plus_file_size_mod_19(ODT_SAMPLE) > 0

    def test_deterministic(self):
        r1 = odt_word_count_times_char_count_plus_paragraph_count_times_100_plus_file_size_mod_19(ODT_SAMPLE)
        r2 = odt_word_count_times_char_count_plus_paragraph_count_times_100_plus_file_size_mod_19(ODT_SAMPLE)
        assert r1 == r2

    def test_expected_value(self):
        assert odt_word_count_times_char_count_plus_paragraph_count_times_100_plus_file_size_mod_19(ODT_SAMPLE) == 141


class TestTsvRowTimesCol:
    def test_returns_int(self):
        assert isinstance(tsv_row_count_times_column_count_plus_file_size_mod_11_times_100(TSV_SAMPLE), int)

    def test_positive(self):
        assert tsv_row_count_times_column_count_plus_file_size_mod_11_times_100(TSV_SAMPLE) > 0

    def test_deterministic(self):
        r1 = tsv_row_count_times_column_count_plus_file_size_mod_11_times_100(TSV_SAMPLE)
        r2 = tsv_row_count_times_column_count_plus_file_size_mod_11_times_100(TSV_SAMPLE)
        assert r1 == r2

    def test_expected_value(self):
        assert tsv_row_count_times_column_count_plus_file_size_mod_11_times_100(TSV_SAMPLE) == 604


class TestTsvUniqueValueSquared:
    def test_returns_int(self):
        assert isinstance(tsv_unique_value_count_squared_plus_row_count_times_100_plus_file_size(TSV_SAMPLE), int)

    def test_positive(self):
        assert tsv_unique_value_count_squared_plus_row_count_times_100_plus_file_size(TSV_SAMPLE) > 0

    def test_deterministic(self):
        r1 = tsv_unique_value_count_squared_plus_row_count_times_100_plus_file_size(TSV_SAMPLE)
        r2 = tsv_unique_value_count_squared_plus_row_count_times_100_plus_file_size(TSV_SAMPLE)
        assert r1 == r2

    def test_expected_value(self):
        assert tsv_unique_value_count_squared_plus_row_count_times_100_plus_file_size(TSV_SAMPLE) == 244
