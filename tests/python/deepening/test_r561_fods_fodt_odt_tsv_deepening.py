"""Sprint 265 deepening – FODS / FODT / ODT / TSV composite analytics."""
import sys, pathlib, pytest

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fods import (
    fods_sheet_count_times_500_plus_total_cell_count_times_300_plus_product,
    fods_total_cell_count_squared_times_2_plus_sheet_count_times_400,
    parse_fods_strict,
)
from src.python.fodt import (
    fodt_paragraph_count_times_300_plus_word_times_char_plus_file_size_mod_31,
    fodt_char_count_squared_plus_para_times_word_times_50_plus_file_size_mod_41,
)
from src.python.odt import (
    odt_paragraph_count_times_400_plus_char_times_word_plus_file_size_mod_37,
    odt_word_count_squared_plus_para_times_300_plus_char_times_10_plus_file_size_mod_43,
)
from src.python.tsv import (
    tsv_row_times_col_times_100_plus_unique_value_times_50_plus_file_size_mod_29,
    tsv_unique_value_squared_times_3_plus_row_times_200_plus_col_times_100_plus_file_size_mod_31,
)

_SAMPLES = _REPO / "samples" / "by-format"
_FODS = _SAMPLES / "fods" / "minimal-spreadsheet.fods"
_FODT = _SAMPLES / "fodt" / "minimal-document.fodt"
_ODT = _SAMPLES / "odt" / "valid" / "minimal-document.odt"
_TSV = _SAMPLES / "tsv" / "minimal-2x2.tsv"


@pytest.fixture
def fods_wb():
    return parse_fods_strict(str(_FODS))


# --- FODS f1 ---
class TestFodsF1:
    def test_returns_int(self, fods_wb):
        assert isinstance(fods_sheet_count_times_500_plus_total_cell_count_times_300_plus_product(fods_wb), int)

    def test_positive(self, fods_wb):
        assert fods_sheet_count_times_500_plus_total_cell_count_times_300_plus_product(fods_wb) > 0

    def test_deterministic(self, fods_wb):
        a = fods_sheet_count_times_500_plus_total_cell_count_times_300_plus_product(fods_wb)
        b = fods_sheet_count_times_500_plus_total_cell_count_times_300_plus_product(fods_wb)
        assert a == b

    def test_expected(self, fods_wb):
        assert fods_sheet_count_times_500_plus_total_cell_count_times_300_plus_product(fods_wb) == 801


# --- FODS f2 ---
class TestFodsF2:
    def test_returns_int(self, fods_wb):
        assert isinstance(fods_total_cell_count_squared_times_2_plus_sheet_count_times_400(fods_wb), int)

    def test_positive(self, fods_wb):
        assert fods_total_cell_count_squared_times_2_plus_sheet_count_times_400(fods_wb) > 0

    def test_deterministic(self, fods_wb):
        a = fods_total_cell_count_squared_times_2_plus_sheet_count_times_400(fods_wb)
        b = fods_total_cell_count_squared_times_2_plus_sheet_count_times_400(fods_wb)
        assert a == b

    def test_expected(self, fods_wb):
        assert fods_total_cell_count_squared_times_2_plus_sheet_count_times_400(fods_wb) == 402


# --- FODT f3 ---
class TestFodtF3:
    def test_returns_int(self):
        assert isinstance(fodt_paragraph_count_times_300_plus_word_times_char_plus_file_size_mod_31(str(_FODT)), int)

    def test_positive(self):
        assert fodt_paragraph_count_times_300_plus_word_times_char_plus_file_size_mod_31(str(_FODT)) > 0

    def test_deterministic(self):
        a = fodt_paragraph_count_times_300_plus_word_times_char_plus_file_size_mod_31(str(_FODT))
        b = fodt_paragraph_count_times_300_plus_word_times_char_plus_file_size_mod_31(str(_FODT))
        assert a == b

    def test_expected(self):
        assert fodt_paragraph_count_times_300_plus_word_times_char_plus_file_size_mod_31(str(_FODT)) == 333


# --- FODT f4 ---
class TestFodtF4:
    def test_returns_int(self):
        assert isinstance(fodt_char_count_squared_plus_para_times_word_times_50_plus_file_size_mod_41(str(_FODT)), int)

    def test_positive(self):
        assert fodt_char_count_squared_plus_para_times_word_times_50_plus_file_size_mod_41(str(_FODT)) > 0

    def test_deterministic(self):
        a = fodt_char_count_squared_plus_para_times_word_times_50_plus_file_size_mod_41(str(_FODT))
        b = fodt_char_count_squared_plus_para_times_word_times_50_plus_file_size_mod_41(str(_FODT))
        assert a == b

    def test_expected(self):
        assert fodt_char_count_squared_plus_para_times_word_times_50_plus_file_size_mod_41(str(_FODT)) == 274


# --- ODT f5 ---
class TestOdtF5:
    def test_returns_int(self):
        assert isinstance(odt_paragraph_count_times_400_plus_char_times_word_plus_file_size_mod_37(str(_ODT)), int)

    def test_positive(self):
        assert odt_paragraph_count_times_400_plus_char_times_word_plus_file_size_mod_37(str(_ODT)) > 0

    def test_deterministic(self):
        a = odt_paragraph_count_times_400_plus_char_times_word_plus_file_size_mod_37(str(_ODT))
        b = odt_paragraph_count_times_400_plus_char_times_word_plus_file_size_mod_37(str(_ODT))
        assert a == b

    def test_expected(self):
        assert odt_paragraph_count_times_400_plus_char_times_word_plus_file_size_mod_37(str(_ODT)) == 454


# --- ODT f6 ---
class TestOdtF6:
    def test_returns_int(self):
        assert isinstance(odt_word_count_squared_plus_para_times_300_plus_char_times_10_plus_file_size_mod_43(str(_ODT)), int)

    def test_positive(self):
        assert odt_word_count_squared_plus_para_times_300_plus_char_times_10_plus_file_size_mod_43(str(_ODT)) > 0

    def test_deterministic(self):
        a = odt_word_count_squared_plus_para_times_300_plus_char_times_10_plus_file_size_mod_43(str(_ODT))
        b = odt_word_count_squared_plus_para_times_300_plus_char_times_10_plus_file_size_mod_43(str(_ODT))
        assert a == b

    def test_expected(self):
        assert odt_word_count_squared_plus_para_times_300_plus_char_times_10_plus_file_size_mod_43(str(_ODT)) == 442


# --- TSV f7 ---
class TestTsvF7:
    def test_returns_int(self):
        assert isinstance(tsv_row_times_col_times_100_plus_unique_value_times_50_plus_file_size_mod_29(str(_TSV)), int)

    def test_positive(self):
        assert tsv_row_times_col_times_100_plus_unique_value_times_50_plus_file_size_mod_29(str(_TSV)) > 0

    def test_deterministic(self):
        a = tsv_row_times_col_times_100_plus_unique_value_times_50_plus_file_size_mod_29(str(_TSV))
        b = tsv_row_times_col_times_100_plus_unique_value_times_50_plus_file_size_mod_29(str(_TSV))
        assert a == b

    def test_expected(self):
        assert tsv_row_times_col_times_100_plus_unique_value_times_50_plus_file_size_mod_29(str(_TSV)) == 628


# --- TSV f8 ---
class TestTsvF8:
    def test_returns_int(self):
        assert isinstance(tsv_unique_value_squared_times_3_plus_row_times_200_plus_col_times_100_plus_file_size_mod_31(str(_TSV)), int)

    def test_positive(self):
        assert tsv_unique_value_squared_times_3_plus_row_times_200_plus_col_times_100_plus_file_size_mod_31(str(_TSV)) > 0

    def test_deterministic(self):
        a = tsv_unique_value_squared_times_3_plus_row_times_200_plus_col_times_100_plus_file_size_mod_31(str(_TSV))
        b = tsv_unique_value_squared_times_3_plus_row_times_200_plus_col_times_100_plus_file_size_mod_31(str(_TSV))
        assert a == b

    def test_expected(self):
        assert tsv_unique_value_squared_times_3_plus_row_times_200_plus_col_times_100_plus_file_size_mod_31(str(_TSV)) == 676
