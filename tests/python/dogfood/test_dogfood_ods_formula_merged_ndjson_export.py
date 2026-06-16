"""
tests/python/dogfood/test_dogfood_ods_formula_merged_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-48
Dogfood export: ODS parse -> formula/merged analytics -> write as NDJSON -> verify.
Uses: parse_ods, ods_formula_cell_count, ods_merged_cell_count, ods_cell_type_distribution,
ods_avg_cells_per_sheet, ods_sheet_name_list, ods_data_validation_count.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ods import (
    parse_ods,
    ods_formula_cell_count,
    ods_merged_cell_count,
    ods_cell_type_distribution,
    ods_avg_cells_per_sheet,
    ods_sheet_name_list,
    ods_data_validation_count,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_ODS_DIR = _REPO / "samples" / "by-format" / "ods" / "valid"


def _valid_ods_files():
    return sorted(_ODS_DIR.glob("*.ods"))


class TestOdsFormulaMergedNdjsonExport:
    """ODS -> formula/merged analytics -> NDJSON export -> roundtrip verification."""

    def test_formula_count_and_merged(self):
        sample = str(next(_ODS_DIR.glob("*.ods")))
        doc = parse_ods(sample)
        formula_count = ods_formula_cell_count(doc)
        merged_count = ods_merged_cell_count(sample)
        assert formula_count >= 0
        assert merged_count >= 0

    def test_cell_type_distribution_and_sheet_names(self):
        sample = str(next(_ODS_DIR.glob("*.ods")))
        doc = parse_ods(sample)
        type_dist = ods_cell_type_distribution(doc)
        avg_cells = ods_avg_cells_per_sheet(sample)
        names = ods_sheet_name_list(doc)
        validation_count = ods_data_validation_count(doc)
        assert isinstance(type_dist, dict)
        assert avg_cells >= 0.0
        assert isinstance(names, list)
        assert validation_count >= 0

    def test_formula_merged_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_ods_files():
            path = str(f)
            doc = parse_ods(path)
            formula_count = ods_formula_cell_count(doc)
            merged_count = ods_merged_cell_count(path)
            type_dist = ods_cell_type_distribution(doc)
            avg_cells = ods_avg_cells_per_sheet(path)
            names = ods_sheet_name_list(doc)
            validation_count = ods_data_validation_count(doc)
            assert formula_count >= 0, f"formula_cell_count must be >= 0 for {f.name}"
            assert merged_count >= 0, f"merged_cell_count must be >= 0 for {f.name}"
            assert isinstance(type_dist, dict), f"cell_type_distribution must be dict for {f.name}"
            assert avg_cells >= 0.0, f"avg_cells_per_sheet must be >= 0 for {f.name}"
            assert isinstance(names, list), f"sheet_name_list must be list for {f.name}"
            assert validation_count >= 0, f"data_validation_count must be >= 0 for {f.name}"
            records.append({
                "file": f.name,
                "formula_count": formula_count,
                "merged_count": merged_count,
                "type_count": len(type_dist),
                "avg_cells_per_sheet": avg_cells,
                "sheet_name_count": len(names),
                "validation_count": validation_count,
                "source_format": "ods",
            })
        dest = tmp_path / "ods-formula-merged.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_ods_files():
            path = str(f)
            doc = parse_ods(path)
            formula_count = ods_formula_cell_count(doc)
            merged_count = ods_merged_cell_count(path)
            records.append({
                "file": f.name,
                "formula_count": formula_count,
                "merged_count": merged_count,
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["formula_count"] == back["formula_count"]
            assert orig["merged_count"] == back["merged_count"]

    def test_json_lines_valid(self, tmp_path):
        sample = str(next(_ODS_DIR.glob("*.ods")))
        doc = parse_ods(sample)
        type_dist = ods_cell_type_distribution(doc)
        records = [{"file": "sample.ods", "type_count": len(type_dist)}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_sheet_name_export(self, tmp_path):
        records = []
        for f in _valid_ods_files():
            path = str(f)
            doc = parse_ods(path)
            names = ods_sheet_name_list(doc)
            avg_cells = ods_avg_cells_per_sheet(path)
            validation_count = ods_data_validation_count(doc)
            assert isinstance(names, list)
            assert avg_cells >= 0.0
            assert validation_count >= 0
            records.append({
                "file": f.name,
                "sheet_names": names,
                "avg_cells_per_sheet": avg_cells,
                "validation_count": validation_count,
                "format": "ods",
            })
        dest = tmp_path / "sheet-names.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "ods" for r in loaded)
        assert all(isinstance(r["sheet_names"], list) for r in loaded)
