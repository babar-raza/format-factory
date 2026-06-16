"""Sprint 47: NDJSON/Gnumeric/DIF/SYLK product deepening — 8 new analytics functions."""
import sys
import tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

GNUMERIC = str(_REPO / "samples" / "by-format" / "gnumeric" / "minimal-spreadsheet.gnumeric")
DIF = str(next((_REPO / "samples" / "by-format" / "dif" / "valid").glob("*.dif")))
SYLK = str(next((_REPO / "samples" / "by-format" / "sylk" / "valid").glob("*.slk")))

NDJSON_CONTENT = b'{"name":"Alice","age":30,"active":true}\n{"name":"Bob","age":25,"active":false}\n'


def _ndjson_file():
    f = tempfile.NamedTemporaryFile(suffix=".ndjson", delete=False)
    f.write(NDJSON_CONTENT)
    f.close()
    return f.name


# --- NDJSON ---

class TestNdjsonHasBooleanFields:
    def test_returns_bool(self):
        from ndjson import ndjson_has_boolean_fields
        assert isinstance(ndjson_has_boolean_fields(_ndjson_file()), bool)


class TestNdjsonMaxStringLength:
    def test_returns_int(self):
        from ndjson import ndjson_max_string_length
        assert isinstance(ndjson_max_string_length(_ndjson_file()), int)

    def test_non_negative(self):
        from ndjson import ndjson_max_string_length
        assert ndjson_max_string_length(_ndjson_file()) >= 0


# --- Gnumeric ---

class TestGnumericMinRowCount:
    def test_returns_int(self):
        from gnumeric import gnumeric_min_row_count
        assert isinstance(gnumeric_min_row_count(GNUMERIC), int)

    def test_non_negative(self):
        from gnumeric import gnumeric_min_row_count
        assert gnumeric_min_row_count(GNUMERIC) >= 0


class TestGnumericHasEmptySheets:
    def test_returns_bool(self):
        from gnumeric import gnumeric_has_empty_sheets
        assert isinstance(gnumeric_has_empty_sheets(GNUMERIC), bool)


# --- DIF ---

class TestDifDataDensity:
    def test_returns_float(self):
        from dif import dif_data_density
        assert isinstance(dif_data_density(DIF), float)

    def test_in_range(self):
        from dif import dif_data_density
        assert 0.0 <= dif_data_density(DIF) <= 1.0


class TestDifAvgCellLength:
    def test_returns_float(self):
        from dif import dif_avg_cell_length
        assert isinstance(dif_avg_cell_length(DIF), float)

    def test_non_negative(self):
        from dif import dif_avg_cell_length
        assert dif_avg_cell_length(DIF) >= 0.0


# --- SYLK ---

class TestSylkDataDensity:
    def test_returns_float(self):
        from sylk import sylk_data_density
        assert isinstance(sylk_data_density(SYLK), float)

    def test_in_range(self):
        from sylk import sylk_data_density
        assert 0.0 <= sylk_data_density(SYLK) <= 1.0


class TestSylkAvgCellValueLength:
    def test_returns_float(self):
        from sylk import sylk_avg_cell_value_length
        assert isinstance(sylk_avg_cell_value_length(SYLK), float)

    def test_non_negative(self):
        from sylk import sylk_avg_cell_value_length
        assert sylk_avg_cell_value_length(SYLK) >= 0.0
