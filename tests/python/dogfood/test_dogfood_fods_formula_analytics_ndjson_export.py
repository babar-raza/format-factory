"""
tests/python/dogfood/test_dogfood_fods_formula_analytics_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-36
Dogfood export: FODS parse -> formula/cell-type analytics -> write as NDJSON -> verify.
Uses: parse_fods, fods_sheet_count, fods_total_cell_count, fods_empty_cell_count,
fods_has_formulas, fods_sheet_names, fods_string_cell_count, fods_numeric_cell_count,
fods_max_row_count.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fods import (
    parse_fods,
    fods_sheet_count,
    fods_total_cell_count,
    fods_empty_cell_count,
    fods_has_formulas,
    fods_sheet_names,
    fods_string_cell_count,
    fods_numeric_cell_count,
    fods_max_row_count,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_FODS_DIR = _REPO / "samples" / "by-format" / "fods"


def _ap(f):
    return os.path.abspath(str(f))


def _valid_fods_files():
    return sorted(_FODS_DIR.glob("*.fods"))


class TestFodsFormulaAnalyticsNdjsonExport:
    """FODS -> formula/cell-type analytics -> NDJSON export -> roundtrip verification."""

    def test_cell_type_counts(self):
        sample = _ap(_FODS_DIR / "typed-values-basic.fods")
        doc = parse_fods(sample)
        total = fods_total_cell_count(doc)
        strings = fods_string_cell_count(doc)
        nums = fods_numeric_cell_count(doc)
        empty = fods_empty_cell_count(doc)
        assert total >= 0
        assert strings >= 0
        assert nums >= 0
        assert empty >= 0

    def test_formula_detection(self):
        sample = _ap(_FODS_DIR / "formula-basic.fods")
        doc = parse_fods(sample)
        has_formulas = fods_has_formulas(doc)
        sheet_names = fods_sheet_names(doc)
        sheets = fods_sheet_count(doc)
        assert isinstance(has_formulas, bool)
        assert isinstance(sheet_names, list)
        assert sheets >= 1

    def test_formula_analytics_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_fods_files():
            path = _ap(f)
            doc = parse_fods(path)
            sheets = fods_sheet_count(doc)
            total = fods_total_cell_count(doc)
            empty = fods_empty_cell_count(doc)
            has_f = fods_has_formulas(doc)
            names = fods_sheet_names(doc)
            strings = fods_string_cell_count(doc)
            nums = fods_numeric_cell_count(doc)
            max_row = fods_max_row_count(doc)
            assert sheets >= 0, f"sheet_count must be >= 0 for {f.name}"
            assert total >= 0, f"total_cell_count must be >= 0 for {f.name}"
            assert empty >= 0, f"empty_cell_count must be >= 0 for {f.name}"
            assert strings >= 0, f"string_cell_count must be >= 0 for {f.name}"
            assert nums >= 0, f"numeric_cell_count must be >= 0 for {f.name}"
            assert max_row >= 0, f"max_row_count must be >= 0 for {f.name}"
            records.append({
                "file": f.name,
                "sheet_count": sheets,
                "total_cells": total,
                "empty_cells": empty,
                "has_formulas": has_f,
                "sheet_names": names,
                "string_cells": strings,
                "numeric_cells": nums,
                "max_row_count": max_row,
                "source_format": "fods",
            })
        dest = tmp_path / "fods-formula.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_fods_files():
            path = _ap(f)
            doc = parse_fods(path)
            records.append({
                "file": f.name,
                "sheet_count": fods_sheet_count(doc),
                "has_formulas": fods_has_formulas(doc),
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["sheet_count"] == back["sheet_count"]
            assert orig["has_formulas"] == back["has_formulas"]

    def test_json_lines_valid(self, tmp_path):
        sample = _ap(_FODS_DIR / "formula-basic.fods")
        doc = parse_fods(sample)
        records = [{"file": "formula-basic.fods", "has_formulas": fods_has_formulas(doc)}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_cell_type_distribution_export(self, tmp_path):
        records = []
        for f in _valid_fods_files():
            path = _ap(f)
            doc = parse_fods(path)
            total = fods_total_cell_count(doc)
            strings = fods_string_cell_count(doc)
            nums = fods_numeric_cell_count(doc)
            empty = fods_empty_cell_count(doc)
            assert strings >= 0
            assert nums >= 0
            assert empty >= 0
            records.append({
                "file": f.name,
                "total_cells": total,
                "string_cells": strings,
                "numeric_cells": nums,
                "empty_cells": empty,
                "format": "fods",
            })
        dest = tmp_path / "cell-types.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "fods" for r in loaded)
        assert all(r["total_cells"] >= 0 for r in loaded)
