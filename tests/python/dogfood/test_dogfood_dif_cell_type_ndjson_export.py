"""
tests/python/dogfood/test_dogfood_dif_cell_type_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-30
Dogfood export: DIF parse -> cell type analytics -> write as NDJSON -> verify.
Uses deeper DIF analytics: string density, numeric/empty counts, vectors, max cell length.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from dif import (
    dif_string_density,
    dif_numeric_cell_count,
    dif_empty_cell_count,
    dif_total_cell_count,
    dif_has_header,
    dif_max_cell_length,
    dif_vectors_count,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_DIF_DIR = _REPO / "samples" / "by-format" / "dif" / "valid"


class TestDifCellTypeNdjsonExport:
    """DIF -> cell type analytics -> NDJSON export -> roundtrip verification."""

    def test_string_density(self):
        sample = str(_DIF_DIR / "minimal-2x2.dif")
        density = dif_string_density(sample)
        assert isinstance(density, (int, float))
        assert 0.0 <= density <= 1.0

    def test_cell_counts_consistent(self):
        sample = str(_DIF_DIR / "minimal-2x2.dif")
        total = dif_total_cell_count(sample)
        numeric = dif_numeric_cell_count(sample)
        empty = dif_empty_cell_count(sample)
        assert numeric <= total, f"numeric ({numeric}) > total ({total})"
        assert empty <= total, f"empty ({empty}) > total ({total})"

    def test_cell_type_to_ndjson(self, tmp_path):
        records = []
        for f in sorted(_DIF_DIR.glob("*.dif")):
            total = dif_total_cell_count(str(f))
            numeric = dif_numeric_cell_count(str(f))
            assert numeric <= total
            records.append({
                "file": f.name,
                "total_cells": total,
                "numeric_cells": numeric,
                "empty_cells": dif_empty_cell_count(str(f)),
                "string_density": dif_string_density(str(f)),
                "has_header": dif_has_header(str(f)),
                "max_cell_length": dif_max_cell_length(str(f)),
                "vectors": dif_vectors_count(str(f)),
                "source_format": "dif",
            })
        dest = tmp_path / "dif-cell-types.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in sorted(_DIF_DIR.glob("*.dif")):
            records.append({
                "file": f.name,
                "total_cells": dif_total_cell_count(str(f)),
                "string_density": dif_string_density(str(f)),
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["total_cells"] == back["total_cells"]

    def test_json_lines_valid(self, tmp_path):
        sample = str(_DIF_DIR / "single-cell.dif")
        records = [{"file": "single-cell.dif", "density": dif_string_density(sample)}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_header_detection_export(self, tmp_path):
        records = []
        for f in sorted(_DIF_DIR.glob("*.dif")):
            records.append({
                "file": f.name,
                "has_header": dif_has_header(str(f)),
                "vectors": dif_vectors_count(str(f)),
                "format": "dif",
            })
        dest = tmp_path / "headers.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "dif" for r in loaded)
        assert all(isinstance(r["has_header"], bool) for r in loaded)
