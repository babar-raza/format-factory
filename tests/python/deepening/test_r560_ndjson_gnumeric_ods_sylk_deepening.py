"""Sprint 264 — Product deepening: NDJSON, Gnumeric, ODS, SYLK composite analytics."""
import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

GNUMERIC_SAMPLE = _REPO / "samples" / "by-format" / "gnumeric" / "minimal-spreadsheet.gnumeric"
ODS_SAMPLE = _REPO / "samples" / "by-format" / "ods" / "valid" / "minimal-spreadsheet.ods"
SYLK_SAMPLE = _REPO / "samples" / "by-format" / "sylk" / "valid" / "minimal-2x2.slk"

from src.python.ndjson import (
    ndjson_record_count_times_300_plus_unique_key_count_times_200_plus_file_size_mod_19,
    ndjson_total_value_count_times_record_count_plus_unique_key_count_times_100_plus_file_size_mod_23,
)
from src.python.gnumeric import (
    gnumeric_sheet_count_times_200_plus_cell_count_times_50_plus_file_size_mod_29,
    gnumeric_cell_count_squared_plus_sheet_count_times_300_plus_file_size_mod_37,
)
from src.python.ods import (
    ods_sheet_count_times_300_plus_row_count_times_100_plus_file_size_mod_31,
    ods_column_count_times_row_count_plus_sheet_count_times_200_plus_file_size_mod_41,
)
from src.python.sylk import (
    sylk_row_count_times_200_plus_column_count_times_100_plus_file_size_mod_29,
    sylk_unique_value_count_times_row_count_plus_column_count_times_50_plus_file_size_mod_37,
)


def _make_ndjson(tmp_path):
    p = tmp_path / "test.ndjson"
    p.write_text(json.dumps({"a": 1, "b": "x"}) + "\n" + json.dumps({"a": 2, "b": "y"}) + "\n")
    return p


class TestNdjsonRecordCountComposite:
    def test_returns_int(self, tmp_path):
        assert isinstance(ndjson_record_count_times_300_plus_unique_key_count_times_200_plus_file_size_mod_19(_make_ndjson(tmp_path)), int)

    def test_positive(self, tmp_path):
        assert ndjson_record_count_times_300_plus_unique_key_count_times_200_plus_file_size_mod_19(_make_ndjson(tmp_path)) > 0

    def test_deterministic(self, tmp_path):
        p = _make_ndjson(tmp_path)
        r1 = ndjson_record_count_times_300_plus_unique_key_count_times_200_plus_file_size_mod_19(p)
        r2 = ndjson_record_count_times_300_plus_unique_key_count_times_200_plus_file_size_mod_19(p)
        assert r1 == r2

    def test_expected_value(self, tmp_path):
        assert ndjson_record_count_times_300_plus_unique_key_count_times_200_plus_file_size_mod_19(_make_ndjson(tmp_path)) == 1002


class TestNdjsonTotalValueComposite:
    def test_returns_int(self, tmp_path):
        assert isinstance(ndjson_total_value_count_times_record_count_plus_unique_key_count_times_100_plus_file_size_mod_23(_make_ndjson(tmp_path)), int)

    def test_positive(self, tmp_path):
        assert ndjson_total_value_count_times_record_count_plus_unique_key_count_times_100_plus_file_size_mod_23(_make_ndjson(tmp_path)) > 0

    def test_deterministic(self, tmp_path):
        p = _make_ndjson(tmp_path)
        r1 = ndjson_total_value_count_times_record_count_plus_unique_key_count_times_100_plus_file_size_mod_23(p)
        r2 = ndjson_total_value_count_times_record_count_plus_unique_key_count_times_100_plus_file_size_mod_23(p)
        assert r1 == r2

    def test_expected_value(self, tmp_path):
        assert ndjson_total_value_count_times_record_count_plus_unique_key_count_times_100_plus_file_size_mod_23(_make_ndjson(tmp_path)) == 225


class TestGnumericSheetCountComposite:
    def test_returns_int(self):
        assert isinstance(gnumeric_sheet_count_times_200_plus_cell_count_times_50_plus_file_size_mod_29(GNUMERIC_SAMPLE), int)

    def test_positive(self):
        assert gnumeric_sheet_count_times_200_plus_cell_count_times_50_plus_file_size_mod_29(GNUMERIC_SAMPLE) > 0

    def test_deterministic(self):
        r1 = gnumeric_sheet_count_times_200_plus_cell_count_times_50_plus_file_size_mod_29(GNUMERIC_SAMPLE)
        r2 = gnumeric_sheet_count_times_200_plus_cell_count_times_50_plus_file_size_mod_29(GNUMERIC_SAMPLE)
        assert r1 == r2

    def test_expected_value(self):
        assert gnumeric_sheet_count_times_200_plus_cell_count_times_50_plus_file_size_mod_29(GNUMERIC_SAMPLE) == 267


class TestGnumericCellSquaredComposite:
    def test_returns_int(self):
        assert isinstance(gnumeric_cell_count_squared_plus_sheet_count_times_300_plus_file_size_mod_37(GNUMERIC_SAMPLE), int)

    def test_positive(self):
        assert gnumeric_cell_count_squared_plus_sheet_count_times_300_plus_file_size_mod_37(GNUMERIC_SAMPLE) > 0

    def test_deterministic(self):
        r1 = gnumeric_cell_count_squared_plus_sheet_count_times_300_plus_file_size_mod_37(GNUMERIC_SAMPLE)
        r2 = gnumeric_cell_count_squared_plus_sheet_count_times_300_plus_file_size_mod_37(GNUMERIC_SAMPLE)
        assert r1 == r2

    def test_expected_value(self):
        assert gnumeric_cell_count_squared_plus_sheet_count_times_300_plus_file_size_mod_37(GNUMERIC_SAMPLE) == 312


class TestOdsSheetCountComposite:
    def test_returns_int(self):
        assert isinstance(ods_sheet_count_times_300_plus_row_count_times_100_plus_file_size_mod_31(ODS_SAMPLE), int)

    def test_positive(self):
        assert ods_sheet_count_times_300_plus_row_count_times_100_plus_file_size_mod_31(ODS_SAMPLE) > 0

    def test_deterministic(self):
        r1 = ods_sheet_count_times_300_plus_row_count_times_100_plus_file_size_mod_31(ODS_SAMPLE)
        r2 = ods_sheet_count_times_300_plus_row_count_times_100_plus_file_size_mod_31(ODS_SAMPLE)
        assert r1 == r2

    def test_expected_value(self):
        assert ods_sheet_count_times_300_plus_row_count_times_100_plus_file_size_mod_31(ODS_SAMPLE) == 505


class TestOdsColumnTimesRowComposite:
    def test_returns_int(self):
        assert isinstance(ods_column_count_times_row_count_plus_sheet_count_times_200_plus_file_size_mod_41(ODS_SAMPLE), int)

    def test_positive(self):
        assert ods_column_count_times_row_count_plus_sheet_count_times_200_plus_file_size_mod_41(ODS_SAMPLE) > 0

    def test_deterministic(self):
        r1 = ods_column_count_times_row_count_plus_sheet_count_times_200_plus_file_size_mod_41(ODS_SAMPLE)
        r2 = ods_column_count_times_row_count_plus_sheet_count_times_200_plus_file_size_mod_41(ODS_SAMPLE)
        assert r1 == r2

    def test_expected_value(self):
        assert ods_column_count_times_row_count_plus_sheet_count_times_200_plus_file_size_mod_41(ODS_SAMPLE) == 230


class TestSylkRowCountComposite:
    def test_returns_int(self):
        assert isinstance(sylk_row_count_times_200_plus_column_count_times_100_plus_file_size_mod_29(SYLK_SAMPLE), int)

    def test_positive(self):
        assert sylk_row_count_times_200_plus_column_count_times_100_plus_file_size_mod_29(SYLK_SAMPLE) > 0

    def test_deterministic(self):
        r1 = sylk_row_count_times_200_plus_column_count_times_100_plus_file_size_mod_29(SYLK_SAMPLE)
        r2 = sylk_row_count_times_200_plus_column_count_times_100_plus_file_size_mod_29(SYLK_SAMPLE)
        assert r1 == r2

    def test_expected_value(self):
        assert sylk_row_count_times_200_plus_column_count_times_100_plus_file_size_mod_29(SYLK_SAMPLE) == 617


class TestSylkUniqueValueComposite:
    def test_returns_int(self):
        assert isinstance(sylk_unique_value_count_times_row_count_plus_column_count_times_50_plus_file_size_mod_37(SYLK_SAMPLE), int)

    def test_positive(self):
        assert sylk_unique_value_count_times_row_count_plus_column_count_times_50_plus_file_size_mod_37(SYLK_SAMPLE) > 0

    def test_deterministic(self):
        r1 = sylk_unique_value_count_times_row_count_plus_column_count_times_50_plus_file_size_mod_37(SYLK_SAMPLE)
        r2 = sylk_unique_value_count_times_row_count_plus_column_count_times_50_plus_file_size_mod_37(SYLK_SAMPLE)
        assert r1 == r2

    def test_expected_value(self):
        assert sylk_unique_value_count_times_row_count_plus_column_count_times_50_plus_file_size_mod_37(SYLK_SAMPLE) == 109
