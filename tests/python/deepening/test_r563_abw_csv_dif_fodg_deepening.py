"""Sprint 267 deepening – ABW / CSV / DIF / FODG composite analytics."""
import sys, pathlib, pytest

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.abw import (
    abw_para_times_300_plus_word_times_char_times_2_plus_file_size_mod_23,
    abw_char_times_100_plus_para_times_word_times_200_plus_file_size_mod_29,
)
from src.python.csv import (
    csv_row_times_col_times_200_plus_total_field_times_100_plus_file_size_mod_23,
    csv_total_field_times_row_times_50_plus_col_times_300_plus_file_size_mod_31,
)
from src.python.dif import (
    dif_row_times_col_times_300_plus_unique_string_times_200_plus_file_size_mod_29,
    dif_unique_string_times_row_times_100_plus_col_times_400_plus_file_size_mod_37,
)
from src.python.fodg import (
    fodg_page_times_600_plus_shape_times_400_plus_file_size_mod_29_times_50,
    fodg_shape_times_text_times_500_plus_page_times_700_plus_file_size_mod_41,
)

_SAMPLES = _REPO / "samples" / "by-format"
_ABW = _SAMPLES / "abw" / "minimal-document.abw"
_CSV = _SAMPLES / "csv" / "minimal-2x2.csv"
_DIF = _SAMPLES / "dif" / "valid" / "minimal-2x2.dif"
_FODG = _SAMPLES / "fodg" / "empty-page.fodg"


# --- ABW f1 ---
class TestAbwF1:
    def test_returns_int(self):
        assert isinstance(abw_para_times_300_plus_word_times_char_times_2_plus_file_size_mod_23(str(_ABW)), int)

    def test_positive(self):
        assert abw_para_times_300_plus_word_times_char_times_2_plus_file_size_mod_23(str(_ABW)) > 0

    def test_deterministic(self):
        a = abw_para_times_300_plus_word_times_char_times_2_plus_file_size_mod_23(str(_ABW))
        b = abw_para_times_300_plus_word_times_char_times_2_plus_file_size_mod_23(str(_ABW))
        assert a == b

    def test_expected(self):
        assert abw_para_times_300_plus_word_times_char_times_2_plus_file_size_mod_23(str(_ABW)) == 318


# --- ABW f2 ---
class TestAbwF2:
    def test_returns_int(self):
        assert isinstance(abw_char_times_100_plus_para_times_word_times_200_plus_file_size_mod_29(str(_ABW)), int)

    def test_positive(self):
        assert abw_char_times_100_plus_para_times_word_times_200_plus_file_size_mod_29(str(_ABW)) > 0

    def test_deterministic(self):
        a = abw_char_times_100_plus_para_times_word_times_200_plus_file_size_mod_29(str(_ABW))
        b = abw_char_times_100_plus_para_times_word_times_200_plus_file_size_mod_29(str(_ABW))
        assert a == b

    def test_expected(self):
        assert abw_char_times_100_plus_para_times_word_times_200_plus_file_size_mod_29(str(_ABW)) == 723


# --- CSV f3 ---
class TestCsvF3:
    def test_returns_int(self):
        assert isinstance(csv_row_times_col_times_200_plus_total_field_times_100_plus_file_size_mod_23(str(_CSV)), int)

    def test_positive(self):
        assert csv_row_times_col_times_200_plus_total_field_times_100_plus_file_size_mod_23(str(_CSV)) > 0

    def test_deterministic(self):
        a = csv_row_times_col_times_200_plus_total_field_times_100_plus_file_size_mod_23(str(_CSV))
        b = csv_row_times_col_times_200_plus_total_field_times_100_plus_file_size_mod_23(str(_CSV))
        assert a == b

    def test_expected(self):
        assert csv_row_times_col_times_200_plus_total_field_times_100_plus_file_size_mod_23(str(_CSV)) == 1202


# --- CSV f4 ---
class TestCsvF4:
    def test_returns_int(self):
        assert isinstance(csv_total_field_times_row_times_50_plus_col_times_300_plus_file_size_mod_31(str(_CSV)), int)

    def test_positive(self):
        assert csv_total_field_times_row_times_50_plus_col_times_300_plus_file_size_mod_31(str(_CSV)) > 0

    def test_deterministic(self):
        a = csv_total_field_times_row_times_50_plus_col_times_300_plus_file_size_mod_31(str(_CSV))
        b = csv_total_field_times_row_times_50_plus_col_times_300_plus_file_size_mod_31(str(_CSV))
        assert a == b

    def test_expected(self):
        assert csv_total_field_times_row_times_50_plus_col_times_300_plus_file_size_mod_31(str(_CSV)) == 1025


# --- DIF f5 ---
class TestDifF5:
    def test_returns_int(self):
        assert isinstance(dif_row_times_col_times_300_plus_unique_string_times_200_plus_file_size_mod_29(str(_DIF)), int)

    def test_positive(self):
        assert dif_row_times_col_times_300_plus_unique_string_times_200_plus_file_size_mod_29(str(_DIF)) > 0

    def test_deterministic(self):
        a = dif_row_times_col_times_300_plus_unique_string_times_200_plus_file_size_mod_29(str(_DIF))
        b = dif_row_times_col_times_300_plus_unique_string_times_200_plus_file_size_mod_29(str(_DIF))
        assert a == b

    def test_expected(self):
        assert dif_row_times_col_times_300_plus_unique_string_times_200_plus_file_size_mod_29(str(_DIF)) == 2613


# --- DIF f6 ---
class TestDifF6:
    def test_returns_int(self):
        assert isinstance(dif_unique_string_times_row_times_100_plus_col_times_400_plus_file_size_mod_37(str(_DIF)), int)

    def test_positive(self):
        assert dif_unique_string_times_row_times_100_plus_col_times_400_plus_file_size_mod_37(str(_DIF)) > 0

    def test_deterministic(self):
        a = dif_unique_string_times_row_times_100_plus_col_times_400_plus_file_size_mod_37(str(_DIF))
        b = dif_unique_string_times_row_times_100_plus_col_times_400_plus_file_size_mod_37(str(_DIF))
        assert a == b

    def test_expected(self):
        assert dif_unique_string_times_row_times_100_plus_col_times_400_plus_file_size_mod_37(str(_DIF)) == 3302


# --- FODG f7 ---
class TestFodgF7:
    def test_returns_int(self):
        assert isinstance(fodg_page_times_600_plus_shape_times_400_plus_file_size_mod_29_times_50(str(_FODG)), int)

    def test_positive(self):
        assert fodg_page_times_600_plus_shape_times_400_plus_file_size_mod_29_times_50(str(_FODG)) > 0

    def test_deterministic(self):
        a = fodg_page_times_600_plus_shape_times_400_plus_file_size_mod_29_times_50(str(_FODG))
        b = fodg_page_times_600_plus_shape_times_400_plus_file_size_mod_29_times_50(str(_FODG))
        assert a == b

    def test_expected(self):
        assert fodg_page_times_600_plus_shape_times_400_plus_file_size_mod_29_times_50(str(_FODG)) == 1050


# --- FODG f8 ---
class TestFodgF8:
    def test_returns_int(self):
        assert isinstance(fodg_shape_times_text_times_500_plus_page_times_700_plus_file_size_mod_41(str(_FODG)), int)

    def test_positive(self):
        assert fodg_shape_times_text_times_500_plus_page_times_700_plus_file_size_mod_41(str(_FODG)) > 0

    def test_deterministic(self):
        a = fodg_shape_times_text_times_500_plus_page_times_700_plus_file_size_mod_41(str(_FODG))
        b = fodg_shape_times_text_times_500_plus_page_times_700_plus_file_size_mod_41(str(_FODG))
        assert a == b

    def test_expected(self):
        assert fodg_shape_times_text_times_500_plus_page_times_700_plus_file_size_mod_41(str(_FODG)) == 728
