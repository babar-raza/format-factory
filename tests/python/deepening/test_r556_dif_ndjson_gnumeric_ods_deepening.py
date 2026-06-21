"""Sprint 260 — Product deepening: DIF, NDJSON, Gnumeric, ODS composite analytics."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

DIF_SAMPLE = _REPO / "samples" / "by-format" / "dif" / "valid" / "minimal-2x2.dif"
GNUMERIC_SAMPLE = _REPO / "samples" / "by-format" / "gnumeric" / "minimal-spreadsheet.gnumeric"
ODS_SAMPLE = _REPO / "samples" / "by-format" / "ods" / "valid" / "minimal-spreadsheet.ods"

from src.python.dif import (
    dif_row_count_times_column_count_plus_file_size_mod_19_times_100,
    dif_unique_string_count_squared_plus_file_size_plus_column_count_times_10,
)
from src.python.gnumeric import (
    gnumeric_sheet_count_times_1000_plus_file_size_mod_31_times_10_plus_cell_count,
    gnumeric_cell_count_squared_plus_sheet_count_times_500_plus_file_size_mod_23,
)
from src.python.ods import (
    ods_row_count_times_column_count_plus_file_size_mod_29_times_100,
    ods_sheet_count_times_500_plus_row_count_squared_plus_column_count_times_100,
)
from src.python.ndjson import (
    ndjson_record_count_squared_plus_unique_key_count_times_100,
    ndjson_total_value_count_times_record_count_plus_unique_key_count_times_50,
)


def _make_ndjson(tmp_path):
    p = tmp_path / "test.ndjson"
    p.write_text('{"name":"alice","age":30}\n{"name":"bob","age":25}\n')
    return p


class TestDifRowTimesCol:
    def test_returns_int(self):
        assert isinstance(dif_row_count_times_column_count_plus_file_size_mod_19_times_100(DIF_SAMPLE), int)

    def test_positive(self):
        assert dif_row_count_times_column_count_plus_file_size_mod_19_times_100(DIF_SAMPLE) > 0

    def test_deterministic(self):
        r1 = dif_row_count_times_column_count_plus_file_size_mod_19_times_100(DIF_SAMPLE)
        r2 = dif_row_count_times_column_count_plus_file_size_mod_19_times_100(DIF_SAMPLE)
        assert r1 == r2

    def test_expected_value(self):
        assert dif_row_count_times_column_count_plus_file_size_mod_19_times_100(DIF_SAMPLE) == 1608


class TestDifUniqueStringSquared:
    def test_returns_int(self):
        assert isinstance(dif_unique_string_count_squared_plus_file_size_plus_column_count_times_10(DIF_SAMPLE), int)

    def test_positive(self):
        assert dif_unique_string_count_squared_plus_file_size_plus_column_count_times_10(DIF_SAMPLE) > 0

    def test_deterministic(self):
        r1 = dif_unique_string_count_squared_plus_file_size_plus_column_count_times_10(DIF_SAMPLE)
        r2 = dif_unique_string_count_squared_plus_file_size_plus_column_count_times_10(DIF_SAMPLE)
        assert r1 == r2

    def test_expected_value(self):
        assert dif_unique_string_count_squared_plus_file_size_plus_column_count_times_10(DIF_SAMPLE) == 268


class TestNdjsonRecordSquared:
    def test_returns_int(self, tmp_path):
        p = _make_ndjson(tmp_path)
        assert isinstance(ndjson_record_count_squared_plus_unique_key_count_times_100(p), int)

    def test_positive(self, tmp_path):
        p = _make_ndjson(tmp_path)
        assert ndjson_record_count_squared_plus_unique_key_count_times_100(p) > 0

    def test_deterministic(self, tmp_path):
        p = _make_ndjson(tmp_path)
        r1 = ndjson_record_count_squared_plus_unique_key_count_times_100(p)
        r2 = ndjson_record_count_squared_plus_unique_key_count_times_100(p)
        assert r1 == r2

    def test_expected_value(self, tmp_path):
        p = _make_ndjson(tmp_path)
        assert ndjson_record_count_squared_plus_unique_key_count_times_100(p) == 204


class TestNdjsonTotalValueTimesRecord:
    def test_returns_int(self, tmp_path):
        p = _make_ndjson(tmp_path)
        assert isinstance(ndjson_total_value_count_times_record_count_plus_unique_key_count_times_50(p), int)

    def test_positive(self, tmp_path):
        p = _make_ndjson(tmp_path)
        assert ndjson_total_value_count_times_record_count_plus_unique_key_count_times_50(p) > 0

    def test_deterministic(self, tmp_path):
        p = _make_ndjson(tmp_path)
        r1 = ndjson_total_value_count_times_record_count_plus_unique_key_count_times_50(p)
        r2 = ndjson_total_value_count_times_record_count_plus_unique_key_count_times_50(p)
        assert r1 == r2

    def test_expected_value(self, tmp_path):
        p = _make_ndjson(tmp_path)
        assert ndjson_total_value_count_times_record_count_plus_unique_key_count_times_50(p) == 108


class TestGnumericSheetTimes1000:
    def test_returns_int(self):
        assert isinstance(gnumeric_sheet_count_times_1000_plus_file_size_mod_31_times_10_plus_cell_count(GNUMERIC_SAMPLE), int)

    def test_positive(self):
        assert gnumeric_sheet_count_times_1000_plus_file_size_mod_31_times_10_plus_cell_count(GNUMERIC_SAMPLE) > 0

    def test_deterministic(self):
        r1 = gnumeric_sheet_count_times_1000_plus_file_size_mod_31_times_10_plus_cell_count(GNUMERIC_SAMPLE)
        r2 = gnumeric_sheet_count_times_1000_plus_file_size_mod_31_times_10_plus_cell_count(GNUMERIC_SAMPLE)
        assert r1 == r2

    def test_expected_value(self):
        assert gnumeric_sheet_count_times_1000_plus_file_size_mod_31_times_10_plus_cell_count(GNUMERIC_SAMPLE) == 1281


class TestGnumericCellSquared:
    def test_returns_int(self):
        assert isinstance(gnumeric_cell_count_squared_plus_sheet_count_times_500_plus_file_size_mod_23(GNUMERIC_SAMPLE), int)

    def test_positive(self):
        assert gnumeric_cell_count_squared_plus_sheet_count_times_500_plus_file_size_mod_23(GNUMERIC_SAMPLE) > 0

    def test_deterministic(self):
        r1 = gnumeric_cell_count_squared_plus_sheet_count_times_500_plus_file_size_mod_23(GNUMERIC_SAMPLE)
        r2 = gnumeric_cell_count_squared_plus_sheet_count_times_500_plus_file_size_mod_23(GNUMERIC_SAMPLE)
        assert r1 == r2

    def test_expected_value(self):
        assert gnumeric_cell_count_squared_plus_sheet_count_times_500_plus_file_size_mod_23(GNUMERIC_SAMPLE) == 509


class TestOdsRowTimesCol:
    def test_returns_int(self):
        assert isinstance(ods_row_count_times_column_count_plus_file_size_mod_29_times_100(ODS_SAMPLE), int)

    def test_positive(self):
        assert ods_row_count_times_column_count_plus_file_size_mod_29_times_100(ODS_SAMPLE) > 0

    def test_deterministic(self):
        r1 = ods_row_count_times_column_count_plus_file_size_mod_29_times_100(ODS_SAMPLE)
        r2 = ods_row_count_times_column_count_plus_file_size_mod_29_times_100(ODS_SAMPLE)
        assert r1 == r2

    def test_expected_value(self):
        assert ods_row_count_times_column_count_plus_file_size_mod_29_times_100(ODS_SAMPLE) == 404


class TestOdsSheetTimes500:
    def test_returns_int(self):
        assert isinstance(ods_sheet_count_times_500_plus_row_count_squared_plus_column_count_times_100(ODS_SAMPLE), int)

    def test_positive(self):
        assert ods_sheet_count_times_500_plus_row_count_squared_plus_column_count_times_100(ODS_SAMPLE) > 0

    def test_deterministic(self):
        r1 = ods_sheet_count_times_500_plus_row_count_squared_plus_column_count_times_100(ODS_SAMPLE)
        r2 = ods_sheet_count_times_500_plus_row_count_squared_plus_column_count_times_100(ODS_SAMPLE)
        assert r1 == r2

    def test_expected_value(self):
        assert ods_sheet_count_times_500_plus_row_count_squared_plus_column_count_times_100(ODS_SAMPLE) == 704
