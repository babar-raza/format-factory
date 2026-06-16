"""Sprint 50: PBM/PGM/ABW/Gnumeric product deepening — 8 new analytics functions."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

PBM = str(next((_REPO / "samples" / "by-format" / "pbm" / "valid").glob("*.pbm")))
PGM = str(next((_REPO / "samples" / "by-format" / "pgm" / "valid").glob("*.pgm")))
ABW = str(_REPO / "samples" / "by-format" / "abw" / "minimal-document.abw")
GNUMERIC = str(_REPO / "samples" / "by-format" / "gnumeric" / "minimal-spreadsheet.gnumeric")


# --- PBM ---

class TestPbmMinDimension:
    def test_returns_int(self):
        from pbm import pbm_min_dimension
        assert isinstance(pbm_min_dimension(PBM), int)

    def test_positive(self):
        from pbm import pbm_min_dimension
        assert pbm_min_dimension(PBM) > 0


class TestPbmBlackDensity:
    def test_returns_float(self):
        from pbm import pbm_black_density
        assert isinstance(pbm_black_density(PBM), float)

    def test_in_range(self):
        from pbm import pbm_black_density
        assert 0.0 <= pbm_black_density(PBM) <= 1.0


# --- PGM ---

class TestPgmMinDimension:
    def test_returns_int(self):
        from pgm import pgm_min_dimension
        assert isinstance(pgm_min_dimension(PGM), int)

    def test_positive(self):
        from pgm import pgm_min_dimension
        assert pgm_min_dimension(PGM) > 0


class TestPgmBrightnessRange:
    def test_returns_int(self):
        from pgm import pgm_brightness_range
        assert isinstance(pgm_brightness_range(PGM), int)

    def test_non_negative(self):
        from pgm import pgm_brightness_range
        assert pgm_brightness_range(PGM) >= 0


# --- ABW ---

class TestAbwSentenceDensity:
    def test_returns_float(self):
        from abw import abw_sentence_density
        assert isinstance(abw_sentence_density(ABW), float)

    def test_non_negative(self):
        from abw import abw_sentence_density
        assert abw_sentence_density(ABW) >= 0.0


class TestAbwHasUnicode:
    def test_returns_bool(self):
        from abw import abw_has_unicode
        assert isinstance(abw_has_unicode(ABW), bool)


# --- Gnumeric ---

class TestGnumericAvgRowCount:
    def test_returns_float(self):
        from gnumeric import gnumeric_avg_row_count
        assert isinstance(gnumeric_avg_row_count(GNUMERIC), float)

    def test_non_negative(self):
        from gnumeric import gnumeric_avg_row_count
        assert gnumeric_avg_row_count(GNUMERIC) >= 0.0


class TestGnumericNonemptyDensity:
    def test_returns_float(self):
        from gnumeric import gnumeric_nonempty_density
        assert isinstance(gnumeric_nonempty_density(GNUMERIC), float)

    def test_in_range(self):
        from gnumeric import gnumeric_nonempty_density
        assert 0.0 <= gnumeric_nonempty_density(GNUMERIC) <= 1.0
