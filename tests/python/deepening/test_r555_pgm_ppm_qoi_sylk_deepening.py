"""Sprint 259 — Product deepening: PGM, PPM, QOI, SYLK composite analytics."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

PGM_SAMPLE = _REPO / "samples" / "by-format" / "pgm" / "valid" / "1x1-white.pgm"
PPM_SAMPLE = _REPO / "samples" / "by-format" / "ppm" / "valid" / "1x1-red.ppm"
QOI_SAMPLE = _REPO / "samples" / "by-format" / "qoi" / "valid" / "1x1-red.qoi"
SYLK_SAMPLE = _REPO / "samples" / "by-format" / "sylk" / "valid" / "minimal-2x2.slk"

from src.python.pgm import (
    pgm_width_times_height_plus_file_size_mod_11_times_100_plus_max_pixel,
    pgm_total_pixel_count_squared_plus_dark_pixel_count_times_50_plus_file_size,
)
from src.python.ppm import (
    ppm_width_times_height_plus_file_size_mod_13_times_100_plus_unique_pixel_count,
    ppm_red_dominant_count_times_50_plus_file_size_squared_mod_1000,
)
from src.python.qoi import (
    qoi_width_times_height_plus_channel_count_times_100_plus_file_size_mod_19,
    qoi_file_size_squared_plus_channel_count_times_50,
)
from src.python.sylk import (
    sylk_row_count_times_column_count_plus_file_size_mod_17_times_100,
    sylk_unique_value_count_squared_plus_row_count_times_100_plus_column_count,
)


class TestPgmWidthTimesHeight:
    def test_returns_int(self):
        assert isinstance(pgm_width_times_height_plus_file_size_mod_11_times_100_plus_max_pixel(PGM_SAMPLE), int)

    def test_positive(self):
        assert pgm_width_times_height_plus_file_size_mod_11_times_100_plus_max_pixel(PGM_SAMPLE) > 0

    def test_deterministic(self):
        r1 = pgm_width_times_height_plus_file_size_mod_11_times_100_plus_max_pixel(PGM_SAMPLE)
        r2 = pgm_width_times_height_plus_file_size_mod_11_times_100_plus_max_pixel(PGM_SAMPLE)
        assert r1 == r2

    def test_expected_value(self):
        assert pgm_width_times_height_plus_file_size_mod_11_times_100_plus_max_pixel(PGM_SAMPLE) == 1056


class TestPgmTotalPixelSquared:
    def test_returns_int(self):
        assert isinstance(pgm_total_pixel_count_squared_plus_dark_pixel_count_times_50_plus_file_size(PGM_SAMPLE), int)

    def test_positive(self):
        assert pgm_total_pixel_count_squared_plus_dark_pixel_count_times_50_plus_file_size(PGM_SAMPLE) > 0

    def test_deterministic(self):
        r1 = pgm_total_pixel_count_squared_plus_dark_pixel_count_times_50_plus_file_size(PGM_SAMPLE)
        r2 = pgm_total_pixel_count_squared_plus_dark_pixel_count_times_50_plus_file_size(PGM_SAMPLE)
        assert r1 == r2

    def test_expected_value(self):
        assert pgm_total_pixel_count_squared_plus_dark_pixel_count_times_50_plus_file_size(PGM_SAMPLE) == 20


class TestPpmWidthTimesHeight:
    def test_returns_int(self):
        assert isinstance(ppm_width_times_height_plus_file_size_mod_13_times_100_plus_unique_pixel_count(PPM_SAMPLE), int)

    def test_positive(self):
        assert ppm_width_times_height_plus_file_size_mod_13_times_100_plus_unique_pixel_count(PPM_SAMPLE) > 0

    def test_deterministic(self):
        r1 = ppm_width_times_height_plus_file_size_mod_13_times_100_plus_unique_pixel_count(PPM_SAMPLE)
        r2 = ppm_width_times_height_plus_file_size_mod_13_times_100_plus_unique_pixel_count(PPM_SAMPLE)
        assert r1 == r2

    def test_expected_value(self):
        assert ppm_width_times_height_plus_file_size_mod_13_times_100_plus_unique_pixel_count(PPM_SAMPLE) == 602


class TestPpmRedDominant:
    def test_returns_int(self):
        assert isinstance(ppm_red_dominant_count_times_50_plus_file_size_squared_mod_1000(PPM_SAMPLE), int)

    def test_positive(self):
        assert ppm_red_dominant_count_times_50_plus_file_size_squared_mod_1000(PPM_SAMPLE) > 0

    def test_deterministic(self):
        r1 = ppm_red_dominant_count_times_50_plus_file_size_squared_mod_1000(PPM_SAMPLE)
        r2 = ppm_red_dominant_count_times_50_plus_file_size_squared_mod_1000(PPM_SAMPLE)
        assert r1 == r2

    def test_expected_value(self):
        assert ppm_red_dominant_count_times_50_plus_file_size_squared_mod_1000(PPM_SAMPLE) == 411


class TestQoiWidthTimesHeight:
    def test_returns_int(self):
        assert isinstance(qoi_width_times_height_plus_channel_count_times_100_plus_file_size_mod_19(QOI_SAMPLE), int)

    def test_positive(self):
        assert qoi_width_times_height_plus_channel_count_times_100_plus_file_size_mod_19(QOI_SAMPLE) > 0

    def test_deterministic(self):
        r1 = qoi_width_times_height_plus_channel_count_times_100_plus_file_size_mod_19(QOI_SAMPLE)
        r2 = qoi_width_times_height_plus_channel_count_times_100_plus_file_size_mod_19(QOI_SAMPLE)
        assert r1 == r2

    def test_expected_value(self):
        assert qoi_width_times_height_plus_channel_count_times_100_plus_file_size_mod_19(QOI_SAMPLE) == 409


class TestQoiFileSizeSquared:
    def test_returns_int(self):
        assert isinstance(qoi_file_size_squared_plus_channel_count_times_50(QOI_SAMPLE), int)

    def test_positive(self):
        assert qoi_file_size_squared_plus_channel_count_times_50(QOI_SAMPLE) > 0

    def test_deterministic(self):
        r1 = qoi_file_size_squared_plus_channel_count_times_50(QOI_SAMPLE)
        r2 = qoi_file_size_squared_plus_channel_count_times_50(QOI_SAMPLE)
        assert r1 == r2

    def test_expected_value(self):
        assert qoi_file_size_squared_plus_channel_count_times_50(QOI_SAMPLE) == 929


class TestSylkRowTimesCol:
    def test_returns_int(self):
        assert isinstance(sylk_row_count_times_column_count_plus_file_size_mod_17_times_100(SYLK_SAMPLE), int)

    def test_positive(self):
        assert sylk_row_count_times_column_count_plus_file_size_mod_17_times_100(SYLK_SAMPLE) > 0

    def test_deterministic(self):
        r1 = sylk_row_count_times_column_count_plus_file_size_mod_17_times_100(SYLK_SAMPLE)
        r2 = sylk_row_count_times_column_count_plus_file_size_mod_17_times_100(SYLK_SAMPLE)
        assert r1 == r2

    def test_expected_value(self):
        assert sylk_row_count_times_column_count_plus_file_size_mod_17_times_100(SYLK_SAMPLE) == 704


class TestSylkUniqueValueSquared:
    def test_returns_int(self):
        assert isinstance(sylk_unique_value_count_squared_plus_row_count_times_100_plus_column_count(SYLK_SAMPLE), int)

    def test_positive(self):
        assert sylk_unique_value_count_squared_plus_row_count_times_100_plus_column_count(SYLK_SAMPLE) > 0

    def test_deterministic(self):
        r1 = sylk_unique_value_count_squared_plus_row_count_times_100_plus_column_count(SYLK_SAMPLE)
        r2 = sylk_unique_value_count_squared_plus_row_count_times_100_plus_column_count(SYLK_SAMPLE)
        assert r1 == r2

    def test_expected_value(self):
        assert sylk_unique_value_count_squared_plus_row_count_times_100_plus_column_count(SYLK_SAMPLE) == 218
