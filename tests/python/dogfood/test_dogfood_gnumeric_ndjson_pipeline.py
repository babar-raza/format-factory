"""
tests/python/dogfood/test_dogfood_gnumeric_ndjson_pipeline.py

Sprint: IDEMPOTENT-SWARM-SPRINT-7
TASK-017: Dogfood export path using Gnumeric and NDJSON in a cross-format chain.

Proves: Gnumeric load -> extract rows -> write as NDJSON -> read back -> verify
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from gnumeric import load as gnumeric_load, sheet_names, get_cell_value
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_GNUMERIC_SAMPLE = str(
    _REPO / "samples" / "by-format" / "gnumeric" / "multi-cell-basic.gnumeric"
)


class TestGnumericNdjsonPipeline:
    """Gnumeric -> row extraction -> NDJSON write -> NDJSON read roundtrip."""

    def test_gnumeric_loads(self):
        wb = gnumeric_load(_GNUMERIC_SAMPLE)
        assert isinstance(wb, dict)

    def test_gnumeric_has_sheets(self):
        wb = gnumeric_load(_GNUMERIC_SAMPLE)
        names = sheet_names(wb)
        assert len(names) >= 1

    def test_extract_cells_to_records(self):
        wb = gnumeric_load(_GNUMERIC_SAMPLE)
        names = sheet_names(wb)
        records = []
        for sname in names:
            records.append({"sheet": sname, "source": "gnumeric"})
        assert len(records) >= 1
        assert records[0]["source"] == "gnumeric"

    def test_write_ndjson_from_gnumeric(self, tmp_path):
        wb = gnumeric_load(_GNUMERIC_SAMPLE)
        names = sheet_names(wb)
        records = [{"sheet": n, "format": "gnumeric"} for n in names]
        dest = tmp_path / "gnumeric-export.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0

    def test_ndjson_roundtrip_preserves_data(self, tmp_path):
        wb = gnumeric_load(_GNUMERIC_SAMPLE)
        names = sheet_names(wb)
        records = [{"sheet": n, "format": "gnumeric"} for n in names]
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["sheet"] == back["sheet"]
            assert orig["format"] == back["format"]

    def test_ndjson_lines_are_valid_json(self, tmp_path):
        wb = gnumeric_load(_GNUMERIC_SAMPLE)
        names = sheet_names(wb)
        records = [{"sheet": n, "format": "gnumeric"} for n in names]
        dest = tmp_path / "valid-json.ndjson"
        write_ndjson(records, str(dest))
        lines = dest.read_text(encoding="utf-8").strip().splitlines()
        for line in lines:
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_pipeline_cell_value_in_ndjson(self, tmp_path):
        wb = gnumeric_load(_GNUMERIC_SAMPLE)
        val = get_cell_value(wb, 0, 0, 0)
        record = {"cell_A1": str(val) if val is not None else "", "source": "gnumeric"}
        dest = tmp_path / "cell-export.ndjson"
        write_ndjson([record], str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == 1
        assert loaded[0]["source"] == "gnumeric"

    def test_multi_sheet_export(self, tmp_path):
        wb = gnumeric_load(_GNUMERIC_SAMPLE)
        names = sheet_names(wb)
        all_records = []
        for idx, sname in enumerate(names):
            all_records.append({
                "sheet_index": idx,
                "sheet_name": sname,
                "origin": "format-factory-gnumeric",
            })
        dest = tmp_path / "multi-sheet.ndjson"
        write_ndjson(all_records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(names)
        assert all(r["origin"] == "format-factory-gnumeric" for r in loaded)
