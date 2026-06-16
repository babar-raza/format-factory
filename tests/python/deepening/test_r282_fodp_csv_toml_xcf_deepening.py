"""Sprint 52: FODP/CSV/TOML/XCF product deepening — 8 new analytics functions."""
import sys, tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

FODP = str(next((_REPO / "samples" / "by-format" / "fodp").glob("*.fodp")))
CSV = str(_REPO / "samples" / "by-format" / "csv" / "minimal-2x2.csv")
XCF = str(next((_REPO / "samples" / "by-format" / "xcf" / "valid").glob("*.xcf")))

# TOML uses tempfile (no sample)
_TOML_CONTENT = b'[server]\nhost = "localhost"\nport = 8080\ntags = ["web", "api"]\n'
_tf = tempfile.NamedTemporaryFile(suffix=".toml", delete=False)
_tf.write(_TOML_CONTENT)
_tf.close()
TOML = _tf.name


# --- FODP ---

class TestFodpTotalShapeCount:
    def test_returns_int(self):
        from fodp import fodp_total_shape_count
        assert isinstance(fodp_total_shape_count(FODP), int)

    def test_non_negative(self):
        from fodp import fodp_total_shape_count
        assert fodp_total_shape_count(FODP) >= 0


class TestFodpAvgShapesPerSlide:
    def test_returns_float(self):
        from fodp import fodp_avg_shapes_per_slide
        assert isinstance(fodp_avg_shapes_per_slide(FODP), float)

    def test_non_negative(self):
        from fodp import fodp_avg_shapes_per_slide
        assert fodp_avg_shapes_per_slide(FODP) >= 0.0


# --- CSV ---

class TestCsvMaxFieldValueLength:
    def test_returns_int(self):
        from src.python.csv.csv_parser import csv_max_field_value_length
        assert isinstance(csv_max_field_value_length(CSV), int)

    def test_non_negative(self):
        from src.python.csv.csv_parser import csv_max_field_value_length
        assert csv_max_field_value_length(CSV) >= 0


class TestCsvUniqueValueCount:
    def test_returns_int(self):
        from src.python.csv.csv_parser import csv_unique_value_count
        assert isinstance(csv_unique_value_count(CSV), int)

    def test_non_negative(self):
        from src.python.csv.csv_parser import csv_unique_value_count
        assert csv_unique_value_count(CSV) >= 0


# --- TOML ---

class TestTomlListCount:
    def test_returns_int(self):
        from toml import toml_list_count
        assert isinstance(toml_list_count(TOML), int)

    def test_non_negative(self):
        from toml import toml_list_count
        assert toml_list_count(TOML) >= 0


class TestTomlAvgKeyLength:
    def test_returns_float(self):
        from toml import toml_avg_key_length
        assert isinstance(toml_avg_key_length(TOML), float)

    def test_positive(self):
        from toml import toml_avg_key_length
        assert toml_avg_key_length(TOML) > 0.0


# --- XCF ---

class TestXcfPerimeter:
    def test_returns_int(self):
        from xcf import xcf_perimeter
        assert isinstance(xcf_perimeter(XCF), int)

    def test_positive(self):
        from xcf import xcf_perimeter
        assert xcf_perimeter(XCF) > 0


class TestXcfDiagonal:
    def test_returns_float(self):
        from xcf import xcf_diagonal
        assert isinstance(xcf_diagonal(XCF), float)

    def test_positive(self):
        from xcf import xcf_diagonal
        assert xcf_diagonal(XCF) > 0.0
