"""
tests/python/dogfood/test_dogfood_gnumeric_correlation_analytics_ndjson.py

Sprint: IDEMPOTENT-SWARM-SPRINT-58
Dogfood export: Gnumeric parse -> correlation/row analytics -> write as NDJSON -> verify.
Uses: load, correlation_columns, average_row, sum_row, count_nonempty_cells,
get_row_count, get_column_count.
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
    correlation_columns,
    average_row,
    sum_row,
    count_nonempty_cells,
    get_row_count,
    get_column_count,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_GNUMERIC_DIR = _REPO / "samples" / "by-format" / "gnumeric"


def _ap(f):
    return os.path.abspath(str(f))


def _valid_gnumeric_files():
    return sorted(_GNUMERIC_DIR.glob("*.gnumeric"))


class TestGnumericCorrelationAnalyticsNdjson:
    """Gnumeric -> correlation/row analytics -> NDJSON export -> roundtrip verification."""

    def test_load_and_row_stats(self):
        sample = _ap(next(_GNUMERIC_DIR.glob("*.gnumeric")))
        model = load(sample)
        row_count = get_row_count(model, 0)
        col_count = get_column_count(model, 0)
        assert row_count >= 0
        assert col_count >= 0

    def test_sum_average_and_correlation(self):
        sample = _ap(next(_GNUMERIC_DIR.glob("*.gnumeric")))
        model = load(sample)
        avg = average_row(model, 0, 0)
        total = sum_row(model, 0, 0)
        nonempty = count_nonempty_cells(model, 0)
        corr = correlation_columns(model, 0, 0, 1)
        assert isinstance(avg, float)
        assert isinstance(total, float)
        assert nonempty >= 0
        assert isinstance(corr, float)

    def test_correlation_analytics_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_gnumeric_files():
            path = _ap(f)
            model = load(path)
            avg = average_row(model, 0, 0)
            total = sum_row(model, 0, 0)
            nonempty = count_nonempty_cells(model, 0)
            row_count = get_row_count(model, 0)
            col_count = get_column_count(model, 0)
            corr = correlation_columns(model, 0, 0, 1)
            assert isinstance(avg, float), f"average_row must be float for {f.name}"
            assert isinstance(total, float), f"sum_row must be float for {f.name}"
            assert nonempty >= 0, f"count_nonempty_cells must be >= 0 for {f.name}"
            assert row_count >= 0, f"get_row_count must be >= 0 for {f.name}"
            assert col_count >= 0, f"get_column_count must be >= 0 for {f.name}"
            assert isinstance(corr, float), f"correlation_columns must be float for {f.name}"
            records.append({
                "file": f.name,
                "avg_row0": avg,
                "sum_row0": total,
                "nonempty_cells": nonempty,
                "row_count": row_count,
                "col_count": col_count,
                "correlation_col0_col1": corr,
                "source_format": "gnumeric",
            })
        dest = tmp_path / "gnumeric-correlation.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_gnumeric_files():
            path = _ap(f)
            model = load(path)
            avg = average_row(model, 0, 0)
            total = sum_row(model, 0, 0)
            records.append({
                "file": f.name,
                "avg_row0": avg,
                "sum_row0": total,
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["avg_row0"] == back["avg_row0"]
            assert orig["sum_row0"] == back["sum_row0"]

    def test_json_lines_valid(self, tmp_path):
        sample = _ap(next(_GNUMERIC_DIR.glob("*.gnumeric")))
        model = load(sample)
        nonempty = count_nonempty_cells(model, 0)
        records = [{"file": "sample.gnumeric", "nonempty_cells": nonempty}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_row_col_counts_export(self, tmp_path):
        records = []
        for f in _valid_gnumeric_files():
            path = _ap(f)
            model = load(path)
            row_count = get_row_count(model, 0)
            col_count = get_column_count(model, 0)
            nonempty = count_nonempty_cells(model, 0)
            assert row_count >= 0
            assert col_count >= 0
            assert nonempty >= 0
            records.append({
                "file": f.name,
                "row_count": row_count,
                "col_count": col_count,
                "nonempty_cells": nonempty,
                "format": "gnumeric",
            })
        dest = tmp_path / "row-col-counts.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "gnumeric" for r in loaded)
        assert all(r["row_count"] >= 0 for r in loaded)
