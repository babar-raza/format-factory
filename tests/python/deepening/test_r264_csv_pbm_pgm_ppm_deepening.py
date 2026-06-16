"""R264 – CSV, PBM, PGM, PPM product deepening: 8 new analytics functions.

Sprint 12: 2 functions each across 4 formats.
"""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

CSV_DIR = _REPO / "samples" / "by-format" / "csv"
PBM_DIR = _REPO / "samples" / "by-format" / "pbm" / "valid"
PGM_DIR = _REPO / "samples" / "by-format" / "pgm" / "valid"
PPM_DIR = _REPO / "samples" / "by-format" / "ppm" / "valid"


CSV_VALID = [CSV_DIR / "minimal-2x2.csv", CSV_DIR / "single-cell.csv", CSV_DIR / "quoted-fields.csv"]


class TestCsvTotalCellCount:
    def test_returns_int(self):
        from src.python.csv.csv_parser import csv_total_cell_count
        assert isinstance(csv_total_cell_count(str(CSV_VALID[0])), int)

    def test_nonnegative(self):
        from src.python.csv.csv_parser import csv_total_cell_count
        for f in CSV_VALID:
            assert csv_total_cell_count(str(f)) >= 0


class TestCsvMinRowLength:
    def test_returns_int(self):
        from src.python.csv.csv_parser import csv_min_row_length
        assert isinstance(csv_min_row_length(str(CSV_VALID[0])), int)

    def test_le_max(self):
        from src.python.csv.csv_parser import csv_min_row_length, csv_max_row_length
        for f in CSV_VALID:
            assert csv_min_row_length(str(f)) <= csv_max_row_length(str(f))


class TestPbmWhitePixelCount:
    def test_returns_int(self):
        from pbm import pbm_white_pixel_count
        f = sorted(PBM_DIR.glob("*.pbm"))[0]
        assert isinstance(pbm_white_pixel_count(str(f)), int)

    def test_nonnegative(self):
        from pbm import pbm_white_pixel_count
        for f in PBM_DIR.glob("*.pbm"):
            assert pbm_white_pixel_count(str(f)) >= 0

    def test_black_plus_white_equals_total(self):
        from pbm import pbm_white_pixel_count, pbm_black_pixel_count
        from pbm import image_pixel_stats
        for f in PBM_DIR.glob("*.pbm"):
            stats = image_pixel_stats(str(f))
            total = stats["total_pixels"]
            assert pbm_black_pixel_count(str(f)) + pbm_white_pixel_count(str(f)) == total


class TestPbmPerimeter:
    def test_returns_int(self):
        from pbm import pbm_perimeter
        f = sorted(PBM_DIR.glob("*.pbm"))[0]
        assert isinstance(pbm_perimeter(str(f)), int)

    def test_positive(self):
        from pbm import pbm_perimeter
        for f in PBM_DIR.glob("*.pbm"):
            assert pbm_perimeter(str(f)) > 0


class TestPgmDimensionRatio:
    def test_returns_float(self):
        from pgm import pgm_dimension_ratio
        f = sorted(PGM_DIR.glob("*.pgm"))[0]
        assert isinstance(pgm_dimension_ratio(str(f)), float)

    def test_positive(self):
        from pgm import pgm_dimension_ratio
        for f in PGM_DIR.glob("*.pgm"):
            assert pgm_dimension_ratio(str(f)) > 0.0


class TestPgmIsSquare:
    def test_returns_bool(self):
        from pgm import pgm_is_square
        f = sorted(PGM_DIR.glob("*.pgm"))[0]
        assert isinstance(pgm_is_square(str(f)), bool)

    def test_1x1_is_square(self):
        from pgm import pgm_is_square
        f = PGM_DIR / "1x1-white.pgm"
        assert pgm_is_square(str(f)) is True

    def test_2x2_is_square(self):
        from pgm import pgm_is_square
        f = PGM_DIR / "2x2-gradient.pgm"
        assert pgm_is_square(str(f)) is True

    def test_3x1_not_square(self):
        from pgm import pgm_is_square
        f = PGM_DIR / "3x1-ramp.pgm"
        assert pgm_is_square(str(f)) is False


class TestPpmDimensionRatio:
    def test_returns_float(self):
        from ppm import ppm_dimension_ratio
        f = sorted(PPM_DIR.glob("*.ppm"))[0]
        assert isinstance(ppm_dimension_ratio(str(f)), float)

    def test_positive(self):
        from ppm import ppm_dimension_ratio
        for f in PPM_DIR.glob("*.ppm"):
            assert ppm_dimension_ratio(str(f)) > 0.0


class TestPpmIsSquare:
    def test_returns_bool(self):
        from ppm import ppm_is_square
        f = sorted(PPM_DIR.glob("*.ppm"))[0]
        assert isinstance(ppm_is_square(str(f)), bool)

    def test_1x1_is_square(self):
        from ppm import ppm_is_square
        f = PPM_DIR / "1x1-red.ppm"
        assert ppm_is_square(str(f)) is True

    def test_2x2_is_square(self):
        from ppm import ppm_is_square
        f = PPM_DIR / "2x2-rgbw.ppm"
        assert ppm_is_square(str(f)) is True
