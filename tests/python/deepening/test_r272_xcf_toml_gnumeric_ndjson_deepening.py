"""Sprint 20: XCF/TOML/Gnumeric/NDJSON product deepening — 8 new analytics functions."""
import sys, tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

XCF = str(next((_REPO / "samples" / "by-format" / "xcf" / "valid").glob("*.xcf")))
GNUMERIC = str(next((_REPO / "samples" / "by-format" / "gnumeric").glob("*.gnumeric")))


def _ndjson_tmp():
    f = Path(tempfile.mktemp(suffix=".ndjson"))
    f.write_text('{"a":1,"b":"hello"}\n{"a":2,"b":"world"}\n')
    return str(f)


# --- XCF ---

class TestXcfMinLayerDimension:
    def test_returns_int(self):
        from xcf import xcf_min_layer_dimension
        assert isinstance(xcf_min_layer_dimension(XCF), int)

    def test_positive(self):
        from xcf import xcf_min_layer_dimension
        assert xcf_min_layer_dimension(XCF) > 0


class TestXcfHasMultipleLayers:
    def test_returns_bool(self):
        from xcf import xcf_has_multiple_layers
        assert isinstance(xcf_has_multiple_layers(XCF), bool)


# --- TOML ---

class TestTomlHasTables:
    def test_returns_bool(self):
        from src.python.toml import toml_has_tables
        assert isinstance(toml_has_tables(b'[server]\nhost = "localhost"\n'), bool)

    def test_with_table(self):
        from src.python.toml import toml_has_tables
        assert toml_has_tables(b'[server]\nhost = "localhost"\n') is True

    def test_without_table(self):
        from src.python.toml import toml_has_tables
        assert toml_has_tables(b'a = 1\nb = 2\n') is False


class TestTomlHasLists:
    def test_returns_bool(self):
        from src.python.toml import toml_has_lists
        assert isinstance(toml_has_lists(b'a = [1, 2, 3]\n'), bool)

    def test_with_list(self):
        from src.python.toml import toml_has_lists
        assert toml_has_lists(b'a = [1, 2, 3]\n') is True


# --- Gnumeric ---

class TestGnumericDataDensity:
    def test_returns_float(self):
        from gnumeric import gnumeric_data_density
        assert isinstance(gnumeric_data_density(GNUMERIC), float)

    def test_density_in_range(self):
        from gnumeric import gnumeric_data_density
        result = gnumeric_data_density(GNUMERIC)
        assert 0.0 <= result <= 1.0


class TestGnumericMaxRowCount:
    def test_returns_int(self):
        from gnumeric import gnumeric_max_row_count
        assert isinstance(gnumeric_max_row_count(GNUMERIC), int)

    def test_non_negative(self):
        from gnumeric import gnumeric_max_row_count
        assert gnumeric_max_row_count(GNUMERIC) >= 0


# --- NDJSON ---

class TestNdjsonMinNumericValue:
    def test_returns_numeric(self):
        from ndjson import ndjson_min_numeric_value
        result = ndjson_min_numeric_value(_ndjson_tmp())
        assert isinstance(result, (int, float))

    def test_correct_value(self):
        from ndjson import ndjson_min_numeric_value
        assert ndjson_min_numeric_value(_ndjson_tmp()) == 1


class TestNdjsonHasStringFields:
    def test_returns_bool(self):
        from ndjson import ndjson_has_string_fields
        assert isinstance(ndjson_has_string_fields(_ndjson_tmp()), bool)

    def test_with_strings(self):
        from ndjson import ndjson_has_string_fields
        assert ndjson_has_string_fields(_ndjson_tmp()) is True
