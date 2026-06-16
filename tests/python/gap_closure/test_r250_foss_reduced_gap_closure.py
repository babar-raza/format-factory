"""Tests for FOSS-reduced gap closure: NDJSON + SYLK existing functions.

Sprint: GAP-CLOSURE-FOSS-REDUCED-SPRINT7-20260616
Closes: GAP-NDJSON-FOSS-NDJSON_ALL_R-001, GAP-NDJSON-FOSS-NDJSON_MAX_F-001,
        GAP-SYLK-FOSS-SYLK_MIN_CEL-001, GAP-SYLK-FOSS-SYLK_MAX_NUM-001
"""
import os
import sys
import tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))


# --- NDJSON: ndjson_all_records_nonempty ---

class TestNdjsonAllRecordsNonempty:
    def _write_ndjson(self, records, path):
        from ndjson.ndjson_codec import write_ndjson
        write_ndjson(records, path)

    def test_returns_bool(self, tmp_path):
        from ndjson import ndjson_all_records_nonempty
        p = str(tmp_path / "test.ndjson")
        self._write_ndjson([{"a": 1}], p)
        assert isinstance(ndjson_all_records_nonempty(p), bool)

    def test_all_nonempty(self, tmp_path):
        from ndjson import ndjson_all_records_nonempty
        p = str(tmp_path / "test.ndjson")
        self._write_ndjson([{"a": 1}, {"b": 2}, {"c": 3}], p)
        assert ndjson_all_records_nonempty(p) is True

    def test_has_empty_record(self, tmp_path):
        from ndjson import ndjson_all_records_nonempty
        p = str(tmp_path / "test.ndjson")
        self._write_ndjson([{"a": 1}, {}], p)
        assert ndjson_all_records_nonempty(p) is False

    def test_single_nonempty(self, tmp_path):
        from ndjson import ndjson_all_records_nonempty
        p = str(tmp_path / "test.ndjson")
        self._write_ndjson([{"key": "value"}], p)
        assert ndjson_all_records_nonempty(p) is True


# --- NDJSON: ndjson_max_field_name_length ---

class TestNdjsonMaxFieldNameLength:
    def _write_ndjson(self, records, path):
        from ndjson.ndjson_codec import write_ndjson
        write_ndjson(records, path)

    def test_returns_int(self, tmp_path):
        from ndjson import ndjson_max_field_name_length
        p = str(tmp_path / "test.ndjson")
        self._write_ndjson([{"a": 1}], p)
        assert isinstance(ndjson_max_field_name_length(p), int)

    def test_correct_max_length(self, tmp_path):
        from ndjson import ndjson_max_field_name_length
        p = str(tmp_path / "test.ndjson")
        self._write_ndjson([{"a": 1, "bb": 2}, {"ccc": 3}], p)
        assert ndjson_max_field_name_length(p) == 3

    def test_single_field(self, tmp_path):
        from ndjson import ndjson_max_field_name_length
        p = str(tmp_path / "test.ndjson")
        self._write_ndjson([{"hello": 1}], p)
        assert ndjson_max_field_name_length(p) == 5

    def test_long_field_name(self, tmp_path):
        from ndjson import ndjson_max_field_name_length
        p = str(tmp_path / "test.ndjson")
        self._write_ndjson([{"x": 1, "very_long_field_name": 2}], p)
        assert ndjson_max_field_name_length(p) == len("very_long_field_name")


# --- SYLK: sylk_min_cell_value_length ---

class TestSylkMinCellValueLength:
    def _sylk_sample(self):
        files = sorted((_REPO / "samples" / "by-format" / "sylk" / "valid").glob("*.slk"))
        assert files, "No SYLK samples"
        return str(files[0])

    def test_returns_int(self):
        from sylk import sylk_min_cell_value_length
        result = sylk_min_cell_value_length(self._sylk_sample())
        assert isinstance(result, int)

    def test_nonnegative(self):
        from sylk import sylk_min_cell_value_length
        result = sylk_min_cell_value_length(self._sylk_sample())
        assert result >= 0

    def test_at_most_max(self):
        from sylk import sylk_min_cell_value_length, sylk_max_cell_value_length
        path = self._sylk_sample()
        min_len = sylk_min_cell_value_length(path)
        max_len = sylk_max_cell_value_length(path)
        assert min_len <= max_len

    def test_positive_for_nonempty_file(self):
        from sylk import sylk_min_cell_value_length, sylk_total_cell_count
        path = self._sylk_sample()
        if sylk_total_cell_count(path) > 0:
            assert sylk_min_cell_value_length(path) > 0


# --- SYLK: sylk_max_numeric_value ---

class TestSylkMaxNumericValue:
    def _sylk_sample(self):
        files = sorted((_REPO / "samples" / "by-format" / "sylk" / "valid").glob("*.slk"))
        assert files, "No SYLK samples"
        return str(files[0])

    def test_returns_float_or_none(self):
        from sylk import sylk_max_numeric_value
        result = sylk_max_numeric_value(self._sylk_sample())
        assert result is None or isinstance(result, (int, float))

    def test_numeric_sample_has_value(self):
        from sylk import sylk_max_numeric_value
        # numeric-row.slk should have numeric values
        files = sorted((_REPO / "samples" / "by-format" / "sylk" / "valid").glob("*numeric*.slk"))
        if files:
            result = sylk_max_numeric_value(str(files[0]))
            assert result is not None
            assert isinstance(result, float)

    def test_consistent_with_total_sum(self):
        from sylk import sylk_max_numeric_value, sylk_total_sum, sylk_numeric_cell_count
        path = self._sylk_sample()
        max_val = sylk_max_numeric_value(path)
        if max_val is not None:
            total = sylk_total_sum(path)
            count = sylk_numeric_cell_count(path)
            # max_val * count >= total (since max is the largest)
            assert max_val * count >= total - 0.001

    def test_at_least_as_large_as_any_column_max(self):
        from sylk import sylk_max_numeric_value, max_column_value, sylk_column_count
        path = self._sylk_sample()
        global_max = sylk_max_numeric_value(path)
        if global_max is None:
            return
        ncols = sylk_column_count(path)
        for col in range(1, ncols + 1):
            col_max = max_column_value(path, col)
            if col_max is not None:
                assert global_max >= col_max
