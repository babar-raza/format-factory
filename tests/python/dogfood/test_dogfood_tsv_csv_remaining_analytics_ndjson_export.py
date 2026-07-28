"""
tests/python/dogfood/test_dogfood_tsv_csv_remaining_analytics_ndjson_export.py

Sprint: PRODUCT-DEEPENING-SPRINT-50
Dogfood export: TSV + CSV remaining uncovered analytics -> write as NDJSON -> verify.
TSV uses: tsv_data_density, tsv_min_numeric_value.
CSV uses: csv_avg_row_length, csv_data_density, csv_is_all_numeric,
          csv_is_single_column, csv_min_numeric_value, csv_nonempty_cell_count,
          csv_numeric_column_count.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
sys.path.insert(0, str(_REPO / "src" / "python"))

from tsv import tsv_data_density, tsv_min_numeric_value
from src.python.ff_csv.csv_parser import (
    csv_avg_row_length,
    csv_data_density,
    csv_is_all_numeric,
    csv_is_single_column,
    csv_min_numeric_value,
    csv_nonempty_cell_count,
    csv_numeric_column_count,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_TSV_DIR = _REPO / "samples" / "by-format" / "tsv"
_CSV_DIR = _REPO / "samples" / "by-format" / "csv"


def _valid_tsv_files():
    return sorted(_TSV_DIR.glob("*.tsv"))


def _valid_csv_files():
    return [f for f in sorted(_CSV_DIR.glob("*.csv")) if "invalid" not in f.name]


class TestTsvCsvRemainingAnalyticsNdjsonExport:
    """TSV + CSV remaining analytics -> NDJSON export -> roundtrip verification."""

    def test_tsv_data_density_and_min_numeric(self):
        s1 = str(_TSV_DIR / "minimal-2x2.tsv")
        s2 = str(_TSV_DIR / "multi-column.tsv")
        assert tsv_data_density(s1) == 1.0
        assert tsv_min_numeric_value(s1) == 25.0
        assert tsv_data_density(s2) == 1.0
        assert tsv_min_numeric_value(s2) == 1.0

    def test_csv_avg_row_length_and_data_density(self):
        s1 = str(_CSV_DIR / "minimal-2x2.csv")
        s2 = str(_CSV_DIR / "quoted-fields.csv")
        assert csv_avg_row_length(s1) == 2.0
        assert csv_data_density(s1) == 1.0
        assert csv_avg_row_length(s2) == 3.0
        assert csv_data_density(s2) == 1.0

    def test_csv_is_all_numeric_and_is_single_column(self):
        s_multi = str(_CSV_DIR / "minimal-2x2.csv")
        s_single = str(_CSV_DIR / "single-cell.csv")
        assert csv_is_all_numeric(s_multi) is False
        assert csv_is_single_column(s_multi) is False
        assert csv_is_all_numeric(s_single) is True
        assert csv_is_single_column(s_single) is True

    def test_csv_min_numeric_nonempty_numeric_col_count(self):
        s1 = str(_CSV_DIR / "minimal-2x2.csv")
        s2 = str(_CSV_DIR / "quoted-fields.csv")
        assert csv_min_numeric_value(s1) == 25.0
        assert csv_nonempty_cell_count(s1) == 4
        assert csv_numeric_column_count(s1) == 1
        assert csv_min_numeric_value(s2) == 9.99
        assert csv_nonempty_cell_count(s2) == 6
        assert csv_numeric_column_count(s2) == 1

    def test_tsv_remaining_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_tsv_files():
            path = str(f)
            density = tsv_data_density(path)
            min_num = tsv_min_numeric_value(path)
            assert isinstance(density, float), f"data_density must be float for {f.name}"
            assert min_num is None or isinstance(min_num, (int, float)), f"min_numeric must be numeric for {f.name}"
            records.append({
                "file": f.name,
                "data_density": density,
                "min_numeric_value": float(min_num) if min_num is not None else None,
                "source_format": "tsv",
            })
        dest = tmp_path / "tsv-remaining.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 2

    def test_csv_remaining_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_csv_files():
            path = str(f)
            avg_row = csv_avg_row_length(path)
            density = csv_data_density(path)
            is_numeric = csv_is_all_numeric(path)
            is_single = csv_is_single_column(path)
            min_num = csv_min_numeric_value(path)
            nonempty = csv_nonempty_cell_count(path)
            num_cols = csv_numeric_column_count(path)
            assert isinstance(avg_row, (int, float)), f"avg_row_length must be numeric for {f.name}"
            assert isinstance(density, float), f"data_density must be float for {f.name}"
            assert isinstance(is_numeric, bool), f"is_all_numeric must be bool for {f.name}"
            assert isinstance(is_single, bool), f"is_single_column must be bool for {f.name}"
            assert nonempty >= 0, f"nonempty_cell_count must be >= 0 for {f.name}"
            assert num_cols >= 0, f"numeric_column_count must be >= 0 for {f.name}"
            records.append({
                "file": f.name,
                "avg_row_length": float(avg_row),
                "data_density": density,
                "is_all_numeric": is_numeric,
                "is_single_column": is_single,
                "min_numeric_value": float(min_num) if min_num is not None else None,
                "nonempty_cell_count": nonempty,
                "numeric_column_count": num_cols,
                "source_format": "csv",
            })
        dest = tmp_path / "csv-remaining.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 2

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_tsv_files():
            path = str(f)
            records.append({
                "file": f.name,
                "data_density": tsv_data_density(path),
                "min_numeric_value": tsv_min_numeric_value(path),
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["data_density"] == back["data_density"]

    def test_json_lines_valid(self, tmp_path):
        s_tsv = str(_TSV_DIR / "minimal-2x2.tsv")
        s_csv = str(_CSV_DIR / "minimal-2x2.csv")
        records = [
            {"file": "minimal-2x2.tsv", "data_density": tsv_data_density(s_tsv), "format": "tsv"},
            {"file": "minimal-2x2.csv", "data_density": csv_data_density(s_csv), "format": "csv"},
        ]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)
