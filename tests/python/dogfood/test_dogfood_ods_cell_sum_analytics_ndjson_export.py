"""
tests/python/dogfood/test_dogfood_ods_cell_sum_analytics_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-70
Dogfood export: ODS parse -> cell/sum analytics -> write as NDJSON -> verify.
Uses: get_cell_count, count_nonempty_cells, sum_row, average_column,
ods_row_count, ods_column_count.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ods import (
    get_cell_count,
    count_nonempty_cells,
    sum_row,
    average_column,
    ods_row_count,
    ods_column_count,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_ODS_DIR = _REPO / "samples" / "by-format" / "ods" / "valid"


def _valid_ods_files():
    return sorted(_ODS_DIR.glob("*.ods"))


class TestOdsCellSumAnalyticsNdjsonExport:
    """ODS -> cell/sum analytics -> NDJSON export -> roundtrip verification."""

    def test_cell_count_basics(self):
        sample = str(next(_ODS_DIR.glob("*.ods")))
        cell_count = get_cell_count(sample, 0)
        nonempty = count_nonempty_cells(sample, 0)
        assert cell_count >= 0
        assert nonempty >= 0

    def test_sum_and_average_basics(self):
        sample = str(next(_ODS_DIR.glob("*.ods")))
        row_total = sum_row(sample, 0, 0)
        col_avg = average_column(sample, 0, 0)
        assert isinstance(row_total, float)
        assert isinstance(col_avg, float)

    def test_cell_sum_analytics_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_ods_files():
            path = str(f)
            cell_count = get_cell_count(path, 0)
            nonempty = count_nonempty_cells(path, 0)
            row_total = sum_row(path, 0, 0)
            col_avg = average_column(path, 0, 0)
            row_count = ods_row_count(path, 0)
            col_count = ods_column_count(path, 0)
            assert cell_count >= 0, f"get_cell_count must be >= 0 for {f.name}"
            assert nonempty >= 0, f"count_nonempty_cells must be >= 0 for {f.name}"
            assert isinstance(row_total, float), f"sum_row must be float for {f.name}"
            assert isinstance(col_avg, float), f"average_column must be float for {f.name}"
            assert row_count >= 0, f"ods_row_count must be >= 0 for {f.name}"
            assert col_count >= 0, f"ods_column_count must be >= 0 for {f.name}"
            records.append({
                "file": f.name,
                "cell_count": cell_count,
                "nonempty_cell_count": nonempty,
                "row0_sum": row_total,
                "col0_avg": col_avg,
                "row_count": row_count,
                "col_count": col_count,
                "source_format": "ods",
            })
        dest = tmp_path / "ods-cell-sum.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_ods_files():
            path = str(f)
            cell_count = get_cell_count(path, 0)
            nonempty = count_nonempty_cells(path, 0)
            records.append({
                "file": f.name,
                "cell_count": cell_count,
                "nonempty_cell_count": nonempty,
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["cell_count"] == back["cell_count"]
            assert orig["nonempty_cell_count"] == back["nonempty_cell_count"]

    def test_json_lines_valid(self, tmp_path):
        sample = str(next(_ODS_DIR.glob("*.ods")))
        cell_count = get_cell_count(sample, 0)
        row_total = sum_row(sample, 0, 0)
        records = [{"file": "sample.ods", "cell_count": cell_count, "row0_sum": row_total}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_cell_nonempty_export(self, tmp_path):
        records = []
        for f in _valid_ods_files():
            path = str(f)
            cell_count = get_cell_count(path, 0)
            nonempty = count_nonempty_cells(path, 0)
            col_avg = average_column(path, 0, 0)
            row_total = sum_row(path, 0, 0)
            assert cell_count >= 0
            assert nonempty >= 0
            assert isinstance(col_avg, float)
            assert isinstance(row_total, float)
            records.append({
                "file": f.name,
                "cell_count": cell_count,
                "nonempty_cell_count": nonempty,
                "col0_avg": col_avg,
                "row0_sum": row_total,
                "format": "ods",
            })
        dest = tmp_path / "cell-nonempty.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "ods" for r in loaded)
        assert all(r["cell_count"] >= 0 for r in loaded)
