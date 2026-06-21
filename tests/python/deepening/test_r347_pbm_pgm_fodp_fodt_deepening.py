"""Sprint 117 — PBM/PGM/FODP/FODT cycle 12 product deepening tests."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.pbm.pbm_parser import pbm_edge_black_count, pbm_grid_density
from src.python.pgm.pgm_parser import pgm_top_row_mean, pgm_bottom_row_mean
from src.python.fodp.fodp_codec import fodp_text_density_per_slide, fodp_has_speaker_notes
from src.python.fodt.neutral_model import fodt_word_per_heading, fodt_block_text_sum

_PBM = next((_REPO / "samples" / "by-format" / "pbm" / "valid").glob("*.pbm"))
_PGM = next((_REPO / "samples" / "by-format" / "pgm" / "valid").glob("*.pgm"))
_FODP = next((_REPO / "samples" / "by-format" / "fodp").glob("*.fodp"))
_FODT = next((_REPO / "samples" / "by-format" / "fodt").glob("*.fodt"))


class TestPbmEdgeBlackCount:
    def test_returns_int(self):
        result = pbm_edge_black_count(_PBM)
        assert isinstance(result, int)

    def test_non_negative(self):
        assert pbm_edge_black_count(_PBM) >= 0


class TestPbmGridDensity:
    def test_returns_float(self):
        result = pbm_grid_density(_PBM)
        assert isinstance(result, float)

    def test_range_zero_to_one(self):
        result = pbm_grid_density(_PBM)
        assert 0.0 <= result <= 1.0


class TestPgmTopRowMean:
    def test_returns_float(self):
        result = pgm_top_row_mean(_PGM)
        assert isinstance(result, float)

    def test_non_negative(self):
        assert pgm_top_row_mean(_PGM) >= 0.0


class TestPgmBottomRowMean:
    def test_returns_float(self):
        result = pgm_bottom_row_mean(_PGM)
        assert isinstance(result, float)

    def test_non_negative(self):
        assert pgm_bottom_row_mean(_PGM) >= 0.0


class TestFodpTextDensityPerSlide:
    def test_returns_float(self):
        result = fodp_text_density_per_slide(_FODP)
        assert isinstance(result, float)

    def test_non_negative(self):
        assert fodp_text_density_per_slide(_FODP) >= 0.0


class TestFodpHasSpeakerNotes:
    def test_returns_bool(self):
        result = fodp_has_speaker_notes(_FODP)
        assert isinstance(result, bool)


class TestFodtWordPerHeading:
    def test_returns_float(self):
        result = fodt_word_per_heading(_FODT)
        assert isinstance(result, float)

    def test_non_negative(self):
        assert fodt_word_per_heading(_FODT) >= 0.0


class TestFodtBlockTextSum:
    def test_returns_int(self):
        result = fodt_block_text_sum(_FODT)
        assert isinstance(result, int)

    def test_non_negative(self):
        assert fodt_block_text_sum(_FODT) >= 0
