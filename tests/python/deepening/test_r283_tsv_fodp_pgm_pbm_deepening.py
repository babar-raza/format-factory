"""Sprint 53: TSV/FODP/PGM/PBM product deepening — 8 new analytics functions."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

TSV = str(_REPO / "samples" / "by-format" / "tsv" / "minimal-2x2.tsv")
FODP = str(next((_REPO / "samples" / "by-format" / "fodp").glob("*.fodp")))
PGM = str(next((_REPO / "samples" / "by-format" / "pgm" / "valid").glob("*.pgm")))
PBM = str(next((_REPO / "samples" / "by-format" / "pbm" / "valid").glob("*.pbm")))


# --- TSV ---

class TestTsvMaxFieldLength:
    def test_returns_int(self):
        from tsv import tsv_max_field_length
        assert isinstance(tsv_max_field_length(TSV), int)

    def test_non_negative(self):
        from tsv import tsv_max_field_length
        assert tsv_max_field_length(TSV) >= 0


class TestTsvUniqueValueCount:
    def test_returns_int(self):
        from tsv import tsv_unique_value_count
        assert isinstance(tsv_unique_value_count(TSV), int)

    def test_non_negative(self):
        from tsv import tsv_unique_value_count
        assert tsv_unique_value_count(TSV) >= 0


# --- FODP ---

class TestFodpEmptySlideCount:
    def test_returns_int(self):
        from fodp import fodp_empty_slide_count
        assert isinstance(fodp_empty_slide_count(FODP), int)

    def test_non_negative(self):
        from fodp import fodp_empty_slide_count
        assert fodp_empty_slide_count(FODP) >= 0


class TestFodpMaxTextLength:
    def test_returns_int(self):
        from fodp import fodp_max_text_length
        assert isinstance(fodp_max_text_length(FODP), int)

    def test_non_negative(self):
        from fodp import fodp_max_text_length
        assert fodp_max_text_length(FODP) >= 0


# --- PGM ---

class TestPgmArea:
    def test_returns_int(self):
        from pgm import pgm_area
        assert isinstance(pgm_area(PGM), int)

    def test_positive(self):
        from pgm import pgm_area
        assert pgm_area(PGM) > 0


class TestPgmMeanBrightness:
    def test_returns_float(self):
        from pgm import pgm_mean_brightness
        assert isinstance(pgm_mean_brightness(PGM), float)

    def test_non_negative(self):
        from pgm import pgm_mean_brightness
        assert pgm_mean_brightness(PGM) >= 0.0


# --- PBM ---

class TestPbmArea:
    def test_returns_int(self):
        from pbm import pbm_area
        assert isinstance(pbm_area(PBM), int)

    def test_positive(self):
        from pbm import pbm_area
        assert pbm_area(PBM) > 0


class TestPbmWhiteDensity:
    def test_returns_float(self):
        from pbm import pbm_white_density
        assert isinstance(pbm_white_density(PBM), float)

    def test_in_range(self):
        from pbm import pbm_white_density
        assert 0.0 <= pbm_white_density(PBM) <= 1.0
