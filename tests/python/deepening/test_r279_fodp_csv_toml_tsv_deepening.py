"""Sprint 49: FODP/CSV/TOML/TSV product deepening — 8 new analytics functions."""
import sys, tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

FODP = str(_REPO / "samples" / "by-format" / "fodp" / "minimal-presentation.fodp")
CSV = str(_REPO / "samples" / "by-format" / "csv" / "minimal-2x2.csv")
TSV = str(_REPO / "samples" / "by-format" / "tsv" / "minimal-2x2.tsv")

TOML_CONTENT = b'[server]\nhost = "localhost"\nport = 8080\nenabled = true\n'


def _toml_file():
    f = tempfile.NamedTemporaryFile(suffix=".toml", delete=False)
    f.write(TOML_CONTENT)
    f.close()
    return f.name


# --- FODP ---

class TestFodpAvgNotesLength:
    def test_returns_float(self):
        from fodp import fodp_avg_notes_length
        assert isinstance(fodp_avg_notes_length(FODP), float)

    def test_non_negative(self):
        from fodp import fodp_avg_notes_length
        assert fodp_avg_notes_length(FODP) >= 0.0


class TestFodpShapeVariance:
    def test_returns_int(self):
        from fodp import fodp_shape_variance
        assert isinstance(fodp_shape_variance(FODP), int)

    def test_non_negative(self):
        from fodp import fodp_shape_variance
        assert fodp_shape_variance(FODP) >= 0


# --- CSV ---

class TestCsvAvgRowLength:
    def test_returns_float(self):
        from src.python.csv.csv_parser import csv_avg_row_length
        assert isinstance(csv_avg_row_length(CSV), float)

    def test_positive(self):
        from src.python.csv.csv_parser import csv_avg_row_length
        assert csv_avg_row_length(CSV) > 0.0


class TestCsvNumericColumnCount:
    def test_returns_int(self):
        from src.python.csv.csv_parser import csv_numeric_column_count
        assert isinstance(csv_numeric_column_count(CSV), int)

    def test_non_negative(self):
        from src.python.csv.csv_parser import csv_numeric_column_count
        assert csv_numeric_column_count(CSV) >= 0


# --- TOML ---

class TestTomlNumericDensity:
    def test_returns_float(self):
        from toml import toml_numeric_density
        assert isinstance(toml_numeric_density(_toml_file()), float)

    def test_in_range(self):
        from toml import toml_numeric_density
        assert 0.0 <= toml_numeric_density(_toml_file()) <= 1.0


class TestTomlDepth:
    def test_returns_int(self):
        from toml import toml_depth
        assert isinstance(toml_depth(_toml_file()), int)

    def test_nested_depth(self):
        from toml import toml_depth
        assert toml_depth(_toml_file()) >= 2  # top-level + [server]


# --- TSV ---

class TestTsvDataDensity:
    def test_returns_float(self):
        from tsv import tsv_data_density
        assert isinstance(tsv_data_density(TSV), float)

    def test_in_range(self):
        from tsv import tsv_data_density
        assert 0.0 <= tsv_data_density(TSV) <= 1.0


class TestTsvMinNumericValue:
    def test_returns_number_or_none(self):
        from tsv import tsv_min_numeric_value
        result = tsv_min_numeric_value(TSV)
        assert result is None or isinstance(result, (int, float))
