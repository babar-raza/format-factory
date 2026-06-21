"""Sprint 131 deepening – PBM pixel_area/dimension_sum, PGM pixel_area/dimension_sum."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.pbm.pbm_parser import pbm_pixel_area, pbm_dimension_sum
from src.python.pgm.pgm_parser import pgm_pixel_area, pgm_dimension_sum

PBM = _REPO / "samples" / "by-format" / "pbm" / "valid"
PGM = _REPO / "samples" / "by-format" / "pgm" / "valid"


class TestPbmPixelArea:
    def test_1x1(self):
        assert pbm_pixel_area(PBM / "1x1-black.pbm") == 1

    def test_2x2(self):
        assert pbm_pixel_area(PBM / "2x2-checker.pbm") == 4

    def test_3x2(self):
        assert pbm_pixel_area(PBM / "3x2-pattern.pbm") == 6

    def test_returns_int(self):
        assert isinstance(pbm_pixel_area(PBM / "1x1-black.pbm"), int)

    def test_positive(self):
        assert pbm_pixel_area(PBM / "1x1-black.pbm") > 0


class TestPbmDimensionSum:
    def test_1x1(self):
        assert pbm_dimension_sum(PBM / "1x1-black.pbm") == 2

    def test_2x2(self):
        assert pbm_dimension_sum(PBM / "2x2-checker.pbm") == 4

    def test_3x2(self):
        assert pbm_dimension_sum(PBM / "3x2-pattern.pbm") == 5

    def test_returns_int(self):
        assert isinstance(pbm_dimension_sum(PBM / "1x1-black.pbm"), int)

    def test_positive(self):
        assert pbm_dimension_sum(PBM / "1x1-black.pbm") > 0


class TestPgmPixelArea:
    def test_1x1(self):
        assert pgm_pixel_area(PGM / "1x1-white.pgm") == 1

    def test_2x2(self):
        assert pgm_pixel_area(PGM / "2x2-gradient.pgm") == 4

    def test_3x1(self):
        assert pgm_pixel_area(PGM / "3x1-ramp.pgm") == 3

    def test_returns_int(self):
        assert isinstance(pgm_pixel_area(PGM / "1x1-white.pgm"), int)

    def test_positive(self):
        assert pgm_pixel_area(PGM / "1x1-white.pgm") > 0


class TestPgmDimensionSum:
    def test_1x1(self):
        assert pgm_dimension_sum(PGM / "1x1-white.pgm") == 2

    def test_2x2(self):
        assert pgm_dimension_sum(PGM / "2x2-gradient.pgm") == 4

    def test_3x1(self):
        assert pgm_dimension_sum(PGM / "3x1-ramp.pgm") == 4

    def test_returns_int(self):
        assert isinstance(pgm_dimension_sum(PGM / "1x1-white.pgm"), int)

    def test_positive(self):
        assert pgm_dimension_sum(PGM / "1x1-white.pgm") > 0
