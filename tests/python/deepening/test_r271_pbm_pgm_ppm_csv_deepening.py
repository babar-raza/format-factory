"""Sprint 19: PBM/PGM/PPM/CSV product deepening — 8 new analytics functions."""
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

class TestPbmIsSquare:
    def test_returns_bool(self):
        from pbm import pbm_is_square
        assert isinstance(pbm_is_square(PBM), bool)


class TestPbmIsLandscape:
    def test_returns_bool(self):
        from pbm import pbm_is_landscape
        assert isinstance(pbm_is_landscape(PBM), bool)


# --- PGM ---

class TestPgmIsLandscape:
    def test_returns_bool(self):
        from pgm import pgm_is_landscape
        assert isinstance(pgm_is_landscape(PGM), bool)


class TestPgmMaxDimension:
    def test_returns_int(self):
        from pgm import pgm_max_dimension
        result = pgm_max_dimension(PGM)
        assert isinstance(result, int)

    def test_positive(self):
        from pgm import pgm_max_dimension
        assert pgm_max_dimension(PGM) > 0


# --- PPM ---

class TestPpmIsLandscape:
    def test_returns_bool(self):
        from ppm import ppm_is_landscape
        assert isinstance(ppm_is_landscape(PPM), bool)


class TestPpmMaxDimension:
    def test_returns_int(self):
        from ppm import ppm_max_dimension
        result = ppm_max_dimension(PPM)
        assert isinstance(result, int)

    def test_positive(self):
        from ppm import ppm_max_dimension
        assert ppm_max_dimension(PPM) > 0


# --- CSV ---

class TestCsvNonemptyCellCount:
    def test_returns_int(self):
        from src.python.ff_csv.csv_parser import csv_nonempty_cell_count
        result = csv_nonempty_cell_count(CSV)
        assert isinstance(result, int)

    def test_non_negative(self):
        from src.python.ff_csv.csv_parser import csv_nonempty_cell_count
        assert csv_nonempty_cell_count(CSV) >= 0


class TestCsvStringDensity:
    def test_returns_float(self):
        from src.python.ff_csv.csv_parser import csv_string_density
        result = csv_string_density(CSV)
        assert isinstance(result, float)

    def test_density_in_range(self):
        from src.python.ff_csv.csv_parser import csv_string_density
        result = csv_string_density(CSV)
        assert 0.0 <= result <= 1.0
