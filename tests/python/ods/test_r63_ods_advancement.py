"""
test_r63_ods_advancement.py — R63 Train I: ODS format track advancement.

New capability: ods_cell_type_distribution(ods_doc)
  Returns distribution of cell types (numeric, text, empty, other).

R63 Sprint: FORMAT-FACTORY-R63-AI-ASSISTED-RC-CLOSURE-AND-WORKAHEAD-MULTI-SPRINT-MEGA-TRAIN-001
Train I — ODS format track advancement
"""
from __future__ import annotations
import sys
from pathlib import Path
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))
from src.python.ods.ods_stats import ods_cell_type_distribution


def _doc(sheets_data):
    sheets = []
    for name, rows_data in sheets_data:
        rows = [{"cells": [{"value": v, "text": str(v) if v else ""} for v in row]}
                for row in rows_data]
        sheets.append({"name": name, "rows": rows})
    return {"sheets": sheets}


class TestOdsCellTypeDistribution:
    def test_empty_doc(self):
        result = ods_cell_type_distribution({"sheets": []})
        assert result["total_cells"] == 0
        assert result["by_type"] == {}

    def test_numeric_cells(self):
        doc = _doc([("Sheet1", [[1, 2, 3]])])
        result = ods_cell_type_distribution(doc)
        assert result["by_type"].get("numeric", 0) == 3

    def test_empty_cells_tracked(self):
        doc = _doc([("Sheet1", [[None, None]])])
        result = ods_cell_type_distribution(doc)
        assert result["by_type"].get("empty", 0) == 2
        assert result["empty_fraction"] == 1.0

    def test_text_cells(self):
        doc = {"sheets": [{"name": "Sheet1", "rows": [
            {"cells": [{"text": "hello", "value": None}, {"text": "world", "value": None}]}
        ]}]}
        result = ods_cell_type_distribution(doc)
        assert result["by_type"].get("text", 0) == 2

    def test_mixed_cells(self):
        doc = {"sheets": [{"name": "Sheet1", "rows": [
            {"cells": [
                {"value": 42, "text": ""},
                {"value": None, "text": ""},
                {"text": "hello", "value": None},
            ]}
        ]}]}
        result = ods_cell_type_distribution(doc)
        assert result["total_cells"] == 3
        assert "numeric" in result["by_type"] or "empty" in result["by_type"] or "text" in result["by_type"]

    def test_returns_correct_keys(self):
        result = ods_cell_type_distribution({"sheets": []})
        assert "by_type" in result
        assert "total_cells" in result
        assert "empty_fraction" in result

    def test_empty_fraction_with_mixed(self):
        doc = _doc([("Sheet1", [[None, 1, None, 2]])])
        result = ods_cell_type_distribution(doc)
        assert result["total_cells"] == 4
        # 2 empty, 2 numeric
        assert result["empty_fraction"] == 0.5

    def test_callable_from_module(self):
        from src.python.ods import ods_stats
        assert callable(ods_stats.ods_cell_type_distribution)
