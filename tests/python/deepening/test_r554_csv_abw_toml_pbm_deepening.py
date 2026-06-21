"""Sprint 258 — Product deepening: CSV, ABW, TOML, PBM composite analytics."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

CSV_SAMPLE = _REPO / "samples" / "by-format" / "csv" / "minimal-2x2.csv"
ABW_SAMPLE = _REPO / "samples" / "by-format" / "abw" / "minimal-document.abw"
TOML_SAMPLE = _REPO / "samples" / "by-format" / "toml" / "minimal.toml"
PBM_SAMPLE = _REPO / "samples" / "by-format" / "pbm" / "valid" / "1x1-black.pbm"

from src.python.csv import (
    csv_row_count_times_column_count_plus_file_size_mod_23,
    csv_total_cell_count_squared_plus_column_count_times_100,
)
from src.python.abw import (
    abw_word_count_squared_plus_paragraph_count_times_50,
    abw_char_count_times_paragraph_count_plus_word_count_times_10,
)
from src.python.toml import (
    toml_table_count_squared_plus_depth_times_100_plus_key_count,
    toml_value_count_times_depth_plus_table_count_times_50,
)
from src.python.pbm import (
    pbm_width_times_height_plus_black_pixel_count_times_10,
    pbm_total_pixel_count_squared_plus_row_count_times_100,
)


class TestCsvRowTimesCol:
    def test_returns_int(self):
        assert isinstance(csv_row_count_times_column_count_plus_file_size_mod_23(CSV_SAMPLE), int)

    def test_positive(self):
        assert csv_row_count_times_column_count_plus_file_size_mod_23(CSV_SAMPLE) > 0

    def test_deterministic(self):
        r1 = csv_row_count_times_column_count_plus_file_size_mod_23(CSV_SAMPLE)
        r2 = csv_row_count_times_column_count_plus_file_size_mod_23(CSV_SAMPLE)
        assert r1 == r2

    def test_expected_value(self):
        assert csv_row_count_times_column_count_plus_file_size_mod_23(CSV_SAMPLE) == 6


class TestCsvTotalCellSquared:
    def test_returns_int(self):
        assert isinstance(csv_total_cell_count_squared_plus_column_count_times_100(CSV_SAMPLE), int)

    def test_positive(self):
        assert csv_total_cell_count_squared_plus_column_count_times_100(CSV_SAMPLE) > 0

    def test_deterministic(self):
        r1 = csv_total_cell_count_squared_plus_column_count_times_100(CSV_SAMPLE)
        r2 = csv_total_cell_count_squared_plus_column_count_times_100(CSV_SAMPLE)
        assert r1 == r2

    def test_expected_value(self):
        assert csv_total_cell_count_squared_plus_column_count_times_100(CSV_SAMPLE) == 216


class TestAbwWordCountSquared:
    def test_returns_int(self):
        assert isinstance(abw_word_count_squared_plus_paragraph_count_times_50(ABW_SAMPLE), int)

    def test_non_negative(self):
        assert abw_word_count_squared_plus_paragraph_count_times_50(ABW_SAMPLE) >= 0

    def test_deterministic(self):
        r1 = abw_word_count_squared_plus_paragraph_count_times_50(ABW_SAMPLE)
        r2 = abw_word_count_squared_plus_paragraph_count_times_50(ABW_SAMPLE)
        assert r1 == r2

    def test_expected_value(self):
        assert abw_word_count_squared_plus_paragraph_count_times_50(ABW_SAMPLE) == 51


class TestAbwCharCountTimesPara:
    def test_returns_int(self):
        assert isinstance(abw_char_count_times_paragraph_count_plus_word_count_times_10(ABW_SAMPLE), int)

    def test_non_negative(self):
        assert abw_char_count_times_paragraph_count_plus_word_count_times_10(ABW_SAMPLE) >= 0

    def test_deterministic(self):
        r1 = abw_char_count_times_paragraph_count_plus_word_count_times_10(ABW_SAMPLE)
        r2 = abw_char_count_times_paragraph_count_plus_word_count_times_10(ABW_SAMPLE)
        assert r1 == r2

    def test_expected_value(self):
        assert abw_char_count_times_paragraph_count_plus_word_count_times_10(ABW_SAMPLE) == 15


class TestTomlTableCountSquared:
    def test_returns_int(self):
        assert isinstance(toml_table_count_squared_plus_depth_times_100_plus_key_count(TOML_SAMPLE), int)

    def test_positive(self):
        assert toml_table_count_squared_plus_depth_times_100_plus_key_count(TOML_SAMPLE) > 0

    def test_deterministic(self):
        r1 = toml_table_count_squared_plus_depth_times_100_plus_key_count(TOML_SAMPLE)
        r2 = toml_table_count_squared_plus_depth_times_100_plus_key_count(TOML_SAMPLE)
        assert r1 == r2

    def test_expected_value(self):
        assert toml_table_count_squared_plus_depth_times_100_plus_key_count(TOML_SAMPLE) == 213


class TestTomlValueCountTimesDepth:
    def test_returns_int(self):
        assert isinstance(toml_value_count_times_depth_plus_table_count_times_50(TOML_SAMPLE), int)

    def test_positive(self):
        assert toml_value_count_times_depth_plus_table_count_times_50(TOML_SAMPLE) > 0

    def test_deterministic(self):
        r1 = toml_value_count_times_depth_plus_table_count_times_50(TOML_SAMPLE)
        r2 = toml_value_count_times_depth_plus_table_count_times_50(TOML_SAMPLE)
        assert r1 == r2

    def test_expected_value(self):
        assert toml_value_count_times_depth_plus_table_count_times_50(TOML_SAMPLE) == 114


class TestPbmWidthTimesHeightBlack:
    def test_returns_int(self):
        assert isinstance(pbm_width_times_height_plus_black_pixel_count_times_10(PBM_SAMPLE), int)

    def test_positive(self):
        assert pbm_width_times_height_plus_black_pixel_count_times_10(PBM_SAMPLE) > 0

    def test_deterministic(self):
        r1 = pbm_width_times_height_plus_black_pixel_count_times_10(PBM_SAMPLE)
        r2 = pbm_width_times_height_plus_black_pixel_count_times_10(PBM_SAMPLE)
        assert r1 == r2

    def test_expected_value(self):
        assert pbm_width_times_height_plus_black_pixel_count_times_10(PBM_SAMPLE) == 11


class TestPbmTotalPixelSquared:
    def test_returns_int(self):
        assert isinstance(pbm_total_pixel_count_squared_plus_row_count_times_100(PBM_SAMPLE), int)

    def test_positive(self):
        assert pbm_total_pixel_count_squared_plus_row_count_times_100(PBM_SAMPLE) > 0

    def test_deterministic(self):
        r1 = pbm_total_pixel_count_squared_plus_row_count_times_100(PBM_SAMPLE)
        r2 = pbm_total_pixel_count_squared_plus_row_count_times_100(PBM_SAMPLE)
        assert r1 == r2

    def test_expected_value(self):
        assert pbm_total_pixel_count_squared_plus_row_count_times_100(PBM_SAMPLE) == 101
