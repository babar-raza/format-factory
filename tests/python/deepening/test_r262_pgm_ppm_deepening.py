"""R262 – PGM & PPM product deepening: perimeter, unique values/colors.

Sprint 10: 4 new analytics functions across PGM (2) and PPM (2).
"""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

PGM_DIR = _REPO / "samples" / "by-format" / "pgm" / "valid"
PPM_DIR = _REPO / "samples" / "by-format" / "ppm" / "valid"


class TestPgmPerimeter:
    def test_returns_int(self):
        from pgm import pgm_perimeter
        f = sorted(PGM_DIR.glob("*.pgm"))[0]
        result = pgm_perimeter(str(f))
        assert isinstance(result, int)

    def test_1x1_perimeter(self):
        from pgm import pgm_perimeter
        f = PGM_DIR / "1x1-white.pgm"
        assert pgm_perimeter(str(f)) == 2 * (1 + 1)

    def test_2x2_perimeter(self):
        from pgm import pgm_perimeter
        f = PGM_DIR / "2x2-gradient.pgm"
        assert pgm_perimeter(str(f)) == 2 * (2 + 2)

    def test_3x1_perimeter(self):
        from pgm import pgm_perimeter
        f = PGM_DIR / "3x1-ramp.pgm"
        assert pgm_perimeter(str(f)) == 2 * (3 + 1)


class TestPgmUniqueValueCount:
    def test_returns_int(self):
        from pgm import pgm_unique_value_count
        f = sorted(PGM_DIR.glob("*.pgm"))[0]
        result = pgm_unique_value_count(str(f))
        assert isinstance(result, int)

    def test_1x1_has_one_value(self):
        from pgm import pgm_unique_value_count
        f = PGM_DIR / "1x1-white.pgm"
        assert pgm_unique_value_count(str(f)) == 1

    def test_gradient_has_multiple_values(self):
        from pgm import pgm_unique_value_count
        f = PGM_DIR / "2x2-gradient.pgm"
        assert pgm_unique_value_count(str(f)) >= 2

    def test_positive(self):
        from pgm import pgm_unique_value_count
        f = PGM_DIR / "3x1-ramp.pgm"
        assert pgm_unique_value_count(str(f)) > 0


class TestPpmUniqueColorCount:
    def test_returns_int(self):
        from ppm import ppm_unique_color_count
        f = sorted(PPM_DIR.glob("*.ppm"))[0]
        result = ppm_unique_color_count(str(f))
        assert isinstance(result, int)

    def test_1x1_has_one_color(self):
        from ppm import ppm_unique_color_count
        f = PPM_DIR / "1x1-red.ppm"
        assert ppm_unique_color_count(str(f)) == 1

    def test_rgbw_has_multiple_colors(self):
        from ppm import ppm_unique_color_count
        f = PPM_DIR / "2x2-rgbw.ppm"
        assert ppm_unique_color_count(str(f)) >= 2

    def test_positive(self):
        from ppm import ppm_unique_color_count
        f = PPM_DIR / "3x1-gradient.ppm"
        assert ppm_unique_color_count(str(f)) > 0


class TestPpmPerimeter:
    def test_returns_int(self):
        from ppm import ppm_perimeter
        f = sorted(PPM_DIR.glob("*.ppm"))[0]
        result = ppm_perimeter(str(f))
        assert isinstance(result, int)

    def test_1x1_perimeter(self):
        from ppm import ppm_perimeter
        f = PPM_DIR / "1x1-red.ppm"
        assert ppm_perimeter(str(f)) == 2 * (1 + 1)

    def test_2x2_perimeter(self):
        from ppm import ppm_perimeter
        f = PPM_DIR / "2x2-rgbw.ppm"
        assert ppm_perimeter(str(f)) == 2 * (2 + 2)

    def test_3x1_perimeter(self):
        from ppm import ppm_perimeter
        f = PPM_DIR / "3x1-gradient.ppm"
        assert ppm_perimeter(str(f)) == 2 * (3 + 1)
