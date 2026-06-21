"""Sprint 263 — Product deepening: ABW, CSV, DIF, FODG composite analytics."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

ABW_SAMPLE = _REPO / "samples" / "by-format" / "abw" / "minimal-document.abw"
CSV_SAMPLE = _REPO / "samples" / "by-format" / "csv" / "minimal-2x2.csv"
DIF_SAMPLE = _REPO / "samples" / "by-format" / "dif" / "valid" / "minimal-2x2.dif"
FODG_SAMPLE = _REPO / "samples" / "by-format" / "fodg" / "empty-page.fodg"

from src.python.abw import (
    abw_paragraph_count_times_200_plus_word_count_squared_plus_file_size_mod_19,
    abw_char_count_times_paragraph_count_plus_word_count_times_50_plus_file_size_mod_13,
)
from src.python.csv import (
    csv_row_count_times_column_count_plus_file_size_mod_17_times_100,
    csv_row_count_squared_plus_column_count_times_50_plus_file_size,
)
from src.python.dif import (
    dif_row_count_times_100_plus_column_count_times_50_plus_file_size_mod_23,
    dif_unique_string_count_times_column_count_plus_row_count_times_200_plus_file_size_mod_29,
)
from src.python.fodg import (
    fodg_total_shape_count_times_300_plus_text_item_count_times_200_plus_file_size_mod_31_times_10,
    fodg_page_count_times_500_plus_total_shape_count_times_100_plus_file_size_mod_37,
)


class TestAbwParaCountComposite:
    def test_returns_int(self):
        assert isinstance(abw_paragraph_count_times_200_plus_word_count_squared_plus_file_size_mod_19(ABW_SAMPLE), int)

    def test_positive(self):
        assert abw_paragraph_count_times_200_plus_word_count_squared_plus_file_size_mod_19(ABW_SAMPLE) > 0

    def test_deterministic(self):
        r1 = abw_paragraph_count_times_200_plus_word_count_squared_plus_file_size_mod_19(ABW_SAMPLE)
        r2 = abw_paragraph_count_times_200_plus_word_count_squared_plus_file_size_mod_19(ABW_SAMPLE)
        assert r1 == r2

    def test_expected_value(self):
        assert abw_paragraph_count_times_200_plus_word_count_squared_plus_file_size_mod_19(ABW_SAMPLE) == 219


class TestAbwCharCountComposite:
    def test_returns_int(self):
        assert isinstance(abw_char_count_times_paragraph_count_plus_word_count_times_50_plus_file_size_mod_13(ABW_SAMPLE), int)

    def test_positive(self):
        assert abw_char_count_times_paragraph_count_plus_word_count_times_50_plus_file_size_mod_13(ABW_SAMPLE) > 0

    def test_deterministic(self):
        r1 = abw_char_count_times_paragraph_count_plus_word_count_times_50_plus_file_size_mod_13(ABW_SAMPLE)
        r2 = abw_char_count_times_paragraph_count_plus_word_count_times_50_plus_file_size_mod_13(ABW_SAMPLE)
        assert r1 == r2

    def test_expected_value(self):
        assert abw_char_count_times_paragraph_count_plus_word_count_times_50_plus_file_size_mod_13(ABW_SAMPLE) == 66


class TestCsvRowTimesColComposite:
    def test_returns_int(self):
        assert isinstance(csv_row_count_times_column_count_plus_file_size_mod_17_times_100(CSV_SAMPLE), int)

    def test_positive(self):
        assert csv_row_count_times_column_count_plus_file_size_mod_17_times_100(CSV_SAMPLE) > 0

    def test_deterministic(self):
        r1 = csv_row_count_times_column_count_plus_file_size_mod_17_times_100(CSV_SAMPLE)
        r2 = csv_row_count_times_column_count_plus_file_size_mod_17_times_100(CSV_SAMPLE)
        assert r1 == r2

    def test_expected_value(self):
        assert csv_row_count_times_column_count_plus_file_size_mod_17_times_100(CSV_SAMPLE) == 804


class TestCsvRowSquaredComposite:
    def test_returns_int(self):
        assert isinstance(csv_row_count_squared_plus_column_count_times_50_plus_file_size(CSV_SAMPLE), int)

    def test_positive(self):
        assert csv_row_count_squared_plus_column_count_times_50_plus_file_size(CSV_SAMPLE) > 0

    def test_deterministic(self):
        r1 = csv_row_count_squared_plus_column_count_times_50_plus_file_size(CSV_SAMPLE)
        r2 = csv_row_count_squared_plus_column_count_times_50_plus_file_size(CSV_SAMPLE)
        assert r1 == r2

    def test_expected_value(self):
        assert csv_row_count_squared_plus_column_count_times_50_plus_file_size(CSV_SAMPLE) == 129


class TestDifRowTimesComposite:
    def test_returns_int(self):
        assert isinstance(dif_row_count_times_100_plus_column_count_times_50_plus_file_size_mod_23(DIF_SAMPLE), int)

    def test_positive(self):
        assert dif_row_count_times_100_plus_column_count_times_50_plus_file_size_mod_23(DIF_SAMPLE) > 0

    def test_deterministic(self):
        r1 = dif_row_count_times_100_plus_column_count_times_50_plus_file_size_mod_23(DIF_SAMPLE)
        r2 = dif_row_count_times_100_plus_column_count_times_50_plus_file_size_mod_23(DIF_SAMPLE)
        assert r1 == r2

    def test_expected_value(self):
        assert dif_row_count_times_100_plus_column_count_times_50_plus_file_size_mod_23(DIF_SAMPLE) == 503


class TestDifUniqueStringComposite:
    def test_returns_int(self):
        assert isinstance(dif_unique_string_count_times_column_count_plus_row_count_times_200_plus_file_size_mod_29(DIF_SAMPLE), int)

    def test_positive(self):
        assert dif_unique_string_count_times_column_count_plus_row_count_times_200_plus_file_size_mod_29(DIF_SAMPLE) > 0

    def test_deterministic(self):
        r1 = dif_unique_string_count_times_column_count_plus_row_count_times_200_plus_file_size_mod_29(DIF_SAMPLE)
        r2 = dif_unique_string_count_times_column_count_plus_row_count_times_200_plus_file_size_mod_29(DIF_SAMPLE)
        assert r1 == r2

    def test_expected_value(self):
        assert dif_unique_string_count_times_column_count_plus_row_count_times_200_plus_file_size_mod_29(DIF_SAMPLE) == 221


class TestFodgShapeComposite:
    def test_returns_int(self):
        assert isinstance(fodg_total_shape_count_times_300_plus_text_item_count_times_200_plus_file_size_mod_31_times_10(FODG_SAMPLE), int)

    def test_non_negative(self):
        assert fodg_total_shape_count_times_300_plus_text_item_count_times_200_plus_file_size_mod_31_times_10(FODG_SAMPLE) >= 0

    def test_deterministic(self):
        r1 = fodg_total_shape_count_times_300_plus_text_item_count_times_200_plus_file_size_mod_31_times_10(FODG_SAMPLE)
        r2 = fodg_total_shape_count_times_300_plus_text_item_count_times_200_plus_file_size_mod_31_times_10(FODG_SAMPLE)
        assert r1 == r2

    def test_expected_value(self):
        assert fodg_total_shape_count_times_300_plus_text_item_count_times_200_plus_file_size_mod_31_times_10(FODG_SAMPLE) == 300


class TestFodgPageComposite:
    def test_returns_int(self):
        assert isinstance(fodg_page_count_times_500_plus_total_shape_count_times_100_plus_file_size_mod_37(FODG_SAMPLE), int)

    def test_positive(self):
        assert fodg_page_count_times_500_plus_total_shape_count_times_100_plus_file_size_mod_37(FODG_SAMPLE) > 0

    def test_deterministic(self):
        r1 = fodg_page_count_times_500_plus_total_shape_count_times_100_plus_file_size_mod_37(FODG_SAMPLE)
        r2 = fodg_page_count_times_500_plus_total_shape_count_times_100_plus_file_size_mod_37(FODG_SAMPLE)
        assert r1 == r2

    def test_expected_value(self):
        assert fodg_page_count_times_500_plus_total_shape_count_times_100_plus_file_size_mod_37(FODG_SAMPLE) == 517
