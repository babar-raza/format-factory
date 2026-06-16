"""Sprint 46: PBM/PGM/PPM/CSV product deepening — 8 new analytics functions."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

PBM = str(next((_REPO / "samples" / "by-format" / "pbm" / "valid").glob("*.pbm")))
PGM = str(next((_REPO / "samples" / "by-format" / "pgm" / "valid").glob("*.pgm")))
PPM = str(next((_REPO / "samples" / "by-format" / "ppm" / "valid").glob("*.ppm")))
CSV = str(_REPO / "samples" / "by-format" / "csv" / "minimal-2x2.csv")


# --- PBM ---

class TestPbmMaxDimension:
    def test_returns_int(self):
        from pbm import pbm_max_dimension
        assert isinstance(pbm_max_dimension(PBM), int)

    def test_positive(self):
        from pbm import pbm_max_dimension
        assert pbm_max_dimension(PBM) > 0


class TestPbmDiagonal:
    def test_returns_float(self):
        from pbm import pbm_diagonal
        assert isinstance(pbm_diagonal(PBM), float)

    def test_positive(self):
        from pbm import pbm_diagonal
        assert pbm_diagonal(PBM) > 0.0


# --- PGM ---

class TestPgmDiagonal:
    def test_returns_float(self):
        from pgm import pgm_diagonal
        assert isinstance(pgm_diagonal(PGM), float)

    def test_positive(self):
        from pgm import pgm_diagonal
        assert pgm_diagonal(PGM) > 0.0


class TestPgmAspectRatio:
    def test_returns_float(self):
        from pgm import pgm_aspect_ratio
        assert isinstance(pgm_aspect_ratio(PGM), float)

    def test_positive(self):
        from pgm import pgm_aspect_ratio
        assert pgm_aspect_ratio(PGM) > 0.0


# --- PPM ---

class TestPpmMinChannelSum:
    def test_returns_int(self):
        from ppm import ppm_min_channel_sum
        assert isinstance(ppm_min_channel_sum(PPM), int)

    def test_lte_max(self):
        from ppm import ppm_min_channel_sum, ppm_max_channel_sum
        assert ppm_min_channel_sum(PPM) <= ppm_max_channel_sum(PPM)


class TestPpmHasPureWhite:
    def test_returns_bool(self):
        from ppm import ppm_has_pure_white
        assert isinstance(ppm_has_pure_white(PPM), bool)


# --- CSV ---

class TestCsvMinNumericValue:
    def test_returns_numeric_or_none(self):
        from src.python.csv.csv_parser import csv_min_numeric_value
        result = csv_min_numeric_value(CSV)
        assert result is None or isinstance(result, (int, float))


class TestCsvDataDensity:
    def test_returns_float(self):
        from src.python.csv.csv_parser import csv_data_density
        assert isinstance(csv_data_density(CSV), float)

    def test_in_range(self):
        from src.python.csv.csv_parser import csv_data_density
        assert 0.0 <= csv_data_density(CSV) <= 1.0
