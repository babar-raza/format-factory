"""
tests/python/dogfood/test_dogfood_gnumeric_data_ops2_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-87
Dogfood export: Gnumeric load -> data ops batch 2 -> write as NDJSON -> verify.
Uses: load, get_sheet_as_rows, row_count, min_column_value, average_row,
      correlation_columns, get_sheet_index, read_cell, gnumeric_column_count.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from gnumeric import (
    load,
    get_sheet_as_rows,
    row_count,
    min_column_value,
    average_row,
    correlation_columns,
    get_sheet_index,
    read_cell,
    gnumeric_column_count,
    get_sheet_names,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_GNU_DIR = _REPO / "samples" / "by-format" / "gnumeric"


def _ap(f):
    return os.path.abspath(str(f))


def _valid_gnumeric_files():
    return sorted(_GNU_DIR.glob("*.gnumeric"))


class TestGnumericDataOps2NdjsonExport:
    """Gnumeric -> data ops batch 2 -> NDJSON export -> roundtrip verification."""

    def test_row_column_count_basics(self):
        sample = _valid_gnumeric_files()[0]
        model = load(_ap(sample))
        rc = row_count(model, 0)
        cc = gnumeric_column_count(model, 0)
        assert isinstance(rc, int) and rc >= 0
        assert isinstance(cc, int) and cc >= 0

    def test_sheet_rows_basics(self):
        sample = _valid_gnumeric_files()[0]
        model = load(_ap(sample))
        rows = get_sheet_as_rows(model, 0)
        assert isinstance(rows, list)
        for r in rows:
            assert isinstance(r, list)

    def test_data_ops2_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_gnumeric_files():
            path = _ap(f)
            model = load(path)
            rows = get_sheet_as_rows(model, 0)
            rc = row_count(model, 0)
            min_val = min_column_value(model, 0, 0)
            avg_r = average_row(model, 0, 0)
            cc = gnumeric_column_count(model, 0)
            cell = read_cell(model, 0, 0, 0)
            assert isinstance(rows, list), f"get_sheet_as_rows must return list for {f.name}"
            assert isinstance(rc, int) and rc >= 0, f"row_count must be int >= 0 for {f.name}"
            assert min_val is None or isinstance(min_val, (int, float)), f"min_column_value must be float or None for {f.name}"
            assert isinstance(avg_r, float), f"average_row must return float for {f.name}"
            assert isinstance(cc, int) and cc >= 0, f"gnumeric_column_count must be int >= 0 for {f.name}"
            assert cell is None or isinstance(cell, str), f"read_cell must return str or None for {f.name}"
            records.append({
                "file": f.name,
                "row_count": rc,
                "column_count": cc,
                "average_row_0": avg_r,
                "min_col_0": float(min_val) if min_val is not None else None,
                "cell_0_0": cell,
                "sheet_rows": len(rows),
                "source_format": "gnumeric",
            })
        dest = tmp_path / "gnumeric-data-ops2.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_gnumeric_files():
            model = load(_ap(f))
            rc = row_count(model, 0)
            cc = gnumeric_column_count(model, 0)
            records.append({"file": f.name, "row_count": rc, "column_count": cc})
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["row_count"] == back["row_count"]

    def test_json_lines_valid(self, tmp_path):
        sample = _valid_gnumeric_files()[0]
        model = load(_ap(sample))
        rc = row_count(model, 0)
        cc = gnumeric_column_count(model, 0)
        records = [{"file": sample.name, "row_count": rc, "column_count": cc}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_sheet_index_correlation_export(self, tmp_path):
        records = []
        for f in _valid_gnumeric_files():
            path = _ap(f)
            model = load(path)
            names = get_sheet_names(path)
            idx = get_sheet_index(model, names[0]) if names else -1
            assert isinstance(idx, int), f"get_sheet_index must return int for {f.name}"
            corr = correlation_columns(model, 0, 0, 0)
            assert isinstance(corr, float), f"correlation_columns must return float for {f.name}"
            records.append({
                "file": f.name,
                "sheet_index": idx,
                "correlation_col0_col0": corr,
                "format": "gnumeric",
            })
        dest = tmp_path / "sheet-index-corr.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "gnumeric" for r in loaded)
        assert all(isinstance(r["sheet_index"], int) for r in loaded)
