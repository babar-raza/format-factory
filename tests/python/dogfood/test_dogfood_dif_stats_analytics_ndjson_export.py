"""
tests/python/dogfood/test_dogfood_dif_stats_analytics_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-46
Dogfood export: DIF parse -> aggregate stats analytics -> write as NDJSON -> verify.
Uses: dif_stats, dif_numeric_range, dif_vector_density, dif_empty_row_count,
dif_string_cell_count, dif_total_numeric_count.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from dif import (
    parse_dif,
    dif_stats,
    dif_numeric_range,
    dif_empty_row_count,
    dif_string_cell_count,
    dif_total_numeric_count,
    dif_total_cell_count,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_DIF_DIR = _REPO / "samples" / "by-format" / "dif" / "valid"


def _valid_dif_files():
    return sorted(_DIF_DIR.glob("*.dif"))


class TestDifStatsAnalyticsNdjsonExport:
    """DIF -> aggregate stats analytics -> NDJSON export -> roundtrip verification."""

    def test_dif_stats(self):
        sample = str(_DIF_DIR / "minimal-2x2.dif")
        doc = parse_dif(sample)
        stats = dif_stats(doc)
        assert isinstance(stats, dict)

    def test_numeric_range_and_cell_counts(self):
        sample = str(_DIF_DIR / "minimal-2x2.dif")
        doc = parse_dif(sample)
        nr = dif_numeric_range(doc)
        str_c = dif_string_cell_count(doc)
        num_c = dif_total_numeric_count(doc)
        assert isinstance(nr, dict)
        assert str_c >= 0
        assert num_c >= 0

    def test_stats_analytics_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_dif_files():
            path = str(f)
            doc = parse_dif(path)
            stats = dif_stats(doc)
            nr = dif_numeric_range(doc)
            empty_rows = dif_empty_row_count(doc)
            str_cells = dif_string_cell_count(doc)
            num_cells = dif_total_numeric_count(doc)
            total = dif_total_cell_count(path)
            assert isinstance(stats, dict), f"dif_stats must be dict for {f.name}"
            assert isinstance(nr, dict), f"numeric_range must be dict for {f.name}"
            assert empty_rows >= 0, f"empty_row_count must be >= 0 for {f.name}"
            assert str_cells >= 0, f"string_cell_count must be >= 0 for {f.name}"
            assert num_cells >= 0, f"total_numeric_count must be >= 0 for {f.name}"
            records.append({
                "file": f.name,
                "has_stats": len(stats) > 0,
                "numeric_count": nr.get("numeric_count", 0),
                "empty_row_count": empty_rows,
                "string_cells": str_cells,
                "numeric_cells": num_cells,
                "total_cells": total,
                "source_format": "dif",
            })
        dest = tmp_path / "dif-stats.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_dif_files():
            path = str(f)
            doc = parse_dif(path)
            records.append({
                "file": f.name,
                "string_cells": dif_string_cell_count(doc),
                "numeric_cells": dif_total_numeric_count(doc),
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["string_cells"] == back["string_cells"]
            assert orig["numeric_cells"] == back["numeric_cells"]

    def test_json_lines_valid(self, tmp_path):
        sample = str(_DIF_DIR / "minimal-2x2.dif")
        doc = parse_dif(sample)
        records = [{"file": "minimal-2x2.dif", "has_stats": isinstance(dif_stats(doc), dict)}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_numeric_range_export(self, tmp_path):
        records = []
        for f in _valid_dif_files():
            path = str(f)
            doc = parse_dif(path)
            nr = dif_numeric_range(doc)
            str_cells = dif_string_cell_count(doc)
            num_cells = dif_total_numeric_count(doc)
            assert isinstance(nr, dict)
            assert str_cells >= 0
            assert num_cells >= 0
            records.append({
                "file": f.name,
                "numeric_count": nr.get("numeric_count", 0),
                "string_cells": str_cells,
                "numeric_cells": num_cells,
                "format": "dif",
            })
        dest = tmp_path / "vector-density.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "dif" for r in loaded)
        assert all(r["numeric_count"] >= 0 for r in loaded)
