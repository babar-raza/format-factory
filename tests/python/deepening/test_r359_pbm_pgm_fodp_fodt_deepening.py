"""Sprint 129 — PBM/PGM/FODP/FODT cycle 15: 8 new analytics functions."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.pbm.pbm_parser import pbm_row_transition_count, pbm_edge_black_ratio
from src.python.pgm.pgm_parser import pgm_column_mean_max, pgm_row_brightness_sum
from src.python.fodp.fodp_codec import fodp_shape_density, fodp_slide_word_count_total
from src.python.fodt.neutral_model import fodt_avg_block_text_length, fodt_longest_heading_text

_PBM = next((_REPO / "samples" / "by-format" / "pbm" / "valid").glob("*.pbm"))
_PGM = next((_REPO / "samples" / "by-format" / "pgm" / "valid").glob("*.pgm"))
_FODP = next((_REPO / "samples" / "by-format" / "fodp").glob("*.fodp"))
_FODT = next((_REPO / "samples" / "by-format" / "fodt").glob("*.fodt"))


class TestPbmRowTransitionCount:
    def test_returns_int(self):
        result = pbm_row_transition_count(_PBM)
        assert isinstance(result, int)

    def test_non_negative(self):
        assert pbm_row_transition_count(_PBM) >= 0


class TestPbmEdgeBlackRatio:
    def test_returns_float(self):
        result = pbm_edge_black_ratio(_PBM)
        assert isinstance(result, float)

    def test_in_range(self):
        r = pbm_edge_black_ratio(_PBM)
        assert 0.0 <= r <= 1.0


class TestPgmColumnMeanMax:
    def test_returns_float(self):
        result = pgm_column_mean_max(_PGM)
        assert isinstance(result, float)

    def test_non_negative(self):
        assert pgm_column_mean_max(_PGM) >= 0.0


class TestPgmRowBrightnessSum:
    def test_returns_int(self):
        result = pgm_row_brightness_sum(_PGM)
        assert isinstance(result, int)

    def test_non_negative(self):
        assert pgm_row_brightness_sum(_PGM) >= 0


class TestFodpShapeDensity:
    def test_returns_float(self):
        result = fodp_shape_density(_FODP)
        assert isinstance(result, float)

    def test_non_negative(self):
        assert fodp_shape_density(_FODP) >= 0.0


class TestFodpSlideWordCountTotal:
    def test_returns_int(self):
        result = fodp_slide_word_count_total(_FODP)
        assert isinstance(result, int)

    def test_non_negative(self):
        assert fodp_slide_word_count_total(_FODP) >= 0


class TestFodtAvgBlockTextLength:
    def test_returns_float(self):
        result = fodt_avg_block_text_length(_FODT)
        assert isinstance(result, float)

    def test_non_negative(self):
        assert fodt_avg_block_text_length(_FODT) >= 0.0


class TestFodtLongestHeadingText:
    def test_returns_int(self):
        result = fodt_longest_heading_text(_FODT)
        assert isinstance(result, int)

    def test_non_negative(self):
        assert fodt_longest_heading_text(_FODT) >= 0
