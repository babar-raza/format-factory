"""Sprint 121 — PBM/PGM/FODP/FODT cycle 13 product deepening tests."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.pbm.pbm_parser import pbm_total_black_count, pbm_border_white_count
from src.python.pgm.pgm_parser import pgm_left_column_mean, pgm_right_column_mean
from src.python.fodp.fodp_codec import fodp_slide_text_range, fodp_text_per_image
from src.python.fodt.neutral_model import fodt_max_heading_text_length, fodt_heading_text_sum

_PBM = next((_REPO / "samples" / "by-format" / "pbm" / "valid").glob("*.pbm"))
_PGM = next((_REPO / "samples" / "by-format" / "pgm" / "valid").glob("*.pgm"))
_FODP = next((_REPO / "samples" / "by-format" / "fodp").glob("*.fodp"))
_FODT = next((_REPO / "samples" / "by-format" / "fodt").glob("*.fodt"))


class TestPbmTotalBlackCount:
    def test_returns_int(self):
        result = pbm_total_black_count(_PBM)
        assert isinstance(result, int)

    def test_non_negative(self):
        assert pbm_total_black_count(_PBM) >= 0


class TestPbmBorderWhiteCount:
    def test_returns_int(self):
        result = pbm_border_white_count(_PBM)
        assert isinstance(result, int)

    def test_non_negative(self):
        assert pbm_border_white_count(_PBM) >= 0


class TestPgmLeftColumnMean:
    def test_returns_float(self):
        result = pgm_left_column_mean(_PGM)
        assert isinstance(result, float)

    def test_non_negative(self):
        assert pgm_left_column_mean(_PGM) >= 0.0


class TestPgmRightColumnMean:
    def test_returns_float(self):
        result = pgm_right_column_mean(_PGM)
        assert isinstance(result, float)

    def test_non_negative(self):
        assert pgm_right_column_mean(_PGM) >= 0.0


class TestFodpSlideTextRange:
    def test_returns_int(self):
        result = fodp_slide_text_range(_FODP)
        assert isinstance(result, int)

    def test_non_negative(self):
        assert fodp_slide_text_range(_FODP) >= 0


class TestFodpTextPerImage:
    def test_returns_float(self):
        result = fodp_text_per_image(_FODP)
        assert isinstance(result, float)

    def test_non_negative(self):
        assert fodp_text_per_image(_FODP) >= 0.0


class TestFodtMaxHeadingTextLength:
    def test_returns_int(self):
        result = fodt_max_heading_text_length(_FODT)
        assert isinstance(result, int)

    def test_non_negative(self):
        assert fodt_max_heading_text_length(_FODT) >= 0


class TestFodtHeadingTextSum:
    def test_returns_int(self):
        result = fodt_heading_text_sum(_FODT)
        assert isinstance(result, int)

    def test_non_negative(self):
        assert fodt_heading_text_sum(_FODT) >= 0
