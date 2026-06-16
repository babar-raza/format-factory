"""
tests/python/dogfood/test_dogfood_tsv_cell_count_analytics_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-68
Dogfood export: TSV parse -> cell count analytics -> write as NDJSON -> verify.
Uses: tsv_nonempty_cell_count, tsv_numeric_cell_count, tsv_empty_row_count,
tsv_has_header, tsv_average_cell_length, tsv_row_count.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from tsv import (
    tsv_nonempty_cell_count,
    tsv_numeric_cell_count,
    tsv_empty_row_count,
    tsv_has_header,
    tsv_average_cell_length,
    tsv_row_count,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_TSV_DIR = _REPO / "samples" / "by-format" / "tsv"


def _valid_tsv_files():
    return sorted(_TSV_DIR.glob("*.tsv"))


class TestTsvCellCountAnalyticsNdjsonExport:
    """TSV -> cell count analytics -> NDJSON export -> roundtrip verification."""

    def test_cell_count_basics(self):
        sample = str(next(_TSV_DIR.glob("*.tsv")))
        nonempty = tsv_nonempty_cell_count(sample)
        numeric = tsv_numeric_cell_count(sample)
        empty_rows = tsv_empty_row_count(sample)
        assert nonempty >= 0
        assert numeric >= 0
        assert empty_rows >= 0

    def test_header_and_length_basics(self):
        sample = str(next(_TSV_DIR.glob("*.tsv")))
        has_header = tsv_has_header(sample)
        avg_len = tsv_average_cell_length(sample)
        row_count = tsv_row_count(sample)
        assert isinstance(has_header, bool)
        assert isinstance(avg_len, float)
        assert row_count >= 0

    def test_cell_count_analytics_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_tsv_files():
            path = str(f)
            nonempty = tsv_nonempty_cell_count(path)
            numeric = tsv_numeric_cell_count(path)
            empty_rows = tsv_empty_row_count(path)
            has_header = tsv_has_header(path)
            avg_len = tsv_average_cell_length(path)
            row_count = tsv_row_count(path)
            assert nonempty >= 0, f"tsv_nonempty_cell_count must be >= 0 for {f.name}"
            assert numeric >= 0, f"tsv_numeric_cell_count must be >= 0 for {f.name}"
            assert empty_rows >= 0, f"tsv_empty_row_count must be >= 0 for {f.name}"
            assert isinstance(has_header, bool), f"tsv_has_header must be bool for {f.name}"
            assert isinstance(avg_len, float), f"tsv_average_cell_length must be float for {f.name}"
            assert row_count >= 0, f"tsv_row_count must be >= 0 for {f.name}"
            records.append({
                "file": f.name,
                "nonempty_cell_count": nonempty,
                "numeric_cell_count": numeric,
                "empty_row_count": empty_rows,
                "has_header": has_header,
                "average_cell_length": avg_len,
                "row_count": row_count,
                "source_format": "tsv",
            })
        dest = tmp_path / "tsv-cell-count.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_tsv_files():
            path = str(f)
            nonempty = tsv_nonempty_cell_count(path)
            avg_len = tsv_average_cell_length(path)
            records.append({
                "file": f.name,
                "nonempty_cell_count": nonempty,
                "average_cell_length": avg_len,
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["nonempty_cell_count"] == back["nonempty_cell_count"]
            assert orig["average_cell_length"] == back["average_cell_length"]

    def test_json_lines_valid(self, tmp_path):
        sample = str(next(_TSV_DIR.glob("*.tsv")))
        nonempty = tsv_nonempty_cell_count(sample)
        has_header = tsv_has_header(sample)
        records = [{"file": "sample.tsv", "nonempty_cell_count": nonempty, "has_header": has_header}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_header_numeric_export(self, tmp_path):
        records = []
        for f in _valid_tsv_files():
            path = str(f)
            has_header = tsv_has_header(path)
            numeric = tsv_numeric_cell_count(path)
            empty_rows = tsv_empty_row_count(path)
            nonempty = tsv_nonempty_cell_count(path)
            assert isinstance(has_header, bool)
            assert numeric >= 0
            assert empty_rows >= 0
            assert nonempty >= 0
            records.append({
                "file": f.name,
                "has_header": has_header,
                "numeric_cell_count": numeric,
                "empty_row_count": empty_rows,
                "nonempty_cell_count": nonempty,
                "format": "tsv",
            })
        dest = tmp_path / "header-numeric.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "tsv" for r in loaded)
        assert all(isinstance(r["has_header"], bool) for r in loaded)
