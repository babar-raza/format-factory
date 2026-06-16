"""test_dogfood_fods_cell_density_ndjson_export.py

Dogfood export path: FODS cell density analytics → NDJSON.

Uses fods_numeric_cell_count, fods_string_cell_count, fods_numeric_density,
fods_string_density, fods_max_row_count, fods_max_col_count on real FODS
sample files, then exports results as NDJSON records.

Sprint: product-deepening-fods-png-export-20260616 (TASK-017 dogfood)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fods.parser import parse_fods
from src.python.fods.neutral_model import (
    fods_numeric_cell_count,
    fods_string_cell_count,
    fods_numeric_density,
    fods_string_density,
    fods_max_row_count,
    fods_max_col_count,
)
from src.python.ndjson.ndjson_codec import write_ndjson

SAMPLES_DIR = _REPO / "samples" / "by-format" / "fods"
TYPED_VALUES = SAMPLES_DIR / "typed-values-basic.fods"
MULTI_SHEET = SAMPLES_DIR / "multi-sheet-basic.fods"
MINIMAL = SAMPLES_DIR / "minimal-spreadsheet.fods"


def _export_cell_density_record(path: Path) -> dict:
    wb = parse_fods(str(path))
    return {
        "file": path.name,
        "numeric_cell_count": fods_numeric_cell_count(wb),
        "string_cell_count": fods_string_cell_count(wb),
        "numeric_density": fods_numeric_density(wb),
        "string_density": fods_string_density(wb),
        "max_row_count": fods_max_row_count(wb),
        "max_col_count": fods_max_col_count(wb),
    }


class TestFodsCellDensityNdjsonExport:

    def test_typed_values_numeric_count_is_positive(self):
        rec = _export_cell_density_record(TYPED_VALUES)
        assert rec["numeric_cell_count"] >= 1

    def test_typed_values_string_count_is_positive(self):
        rec = _export_cell_density_record(TYPED_VALUES)
        assert rec["string_cell_count"] >= 1

    def test_typed_values_numeric_density_in_range(self):
        rec = _export_cell_density_record(TYPED_VALUES)
        assert 0.0 <= rec["numeric_density"] <= 1.0

    def test_typed_values_string_density_in_range(self):
        rec = _export_cell_density_record(TYPED_VALUES)
        assert 0.0 <= rec["string_density"] <= 1.0

    def test_typed_values_max_row_count_is_positive(self):
        rec = _export_cell_density_record(TYPED_VALUES)
        assert rec["max_row_count"] >= 1

    def test_typed_values_max_col_count_is_positive(self):
        rec = _export_cell_density_record(TYPED_VALUES)
        assert rec["max_col_count"] >= 1

    def test_multi_sheet_string_count_is_positive(self):
        rec = _export_cell_density_record(MULTI_SHEET)
        assert rec["string_cell_count"] >= 1

    def test_record_has_required_keys(self):
        rec = _export_cell_density_record(TYPED_VALUES)
        for key in ["file", "numeric_cell_count", "string_cell_count",
                    "numeric_density", "string_density", "max_row_count", "max_col_count"]:
            assert key in rec

    def test_ndjson_export_produces_valid_lines(self, tmp_path):
        records = [
            _export_cell_density_record(TYPED_VALUES),
            _export_cell_density_record(MULTI_SHEET),
        ]
        out = tmp_path / "fods_cell_density.ndjson"
        write_ndjson(records, str(out))
        lines = out.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 2
        for line in lines:
            parsed = json.loads(line)
            assert "numeric_cell_count" in parsed

    def test_ndjson_line_is_valid_json(self, tmp_path):
        records = [_export_cell_density_record(TYPED_VALUES)]
        out = tmp_path / "single.ndjson"
        write_ndjson(records, str(out))
        line = out.read_text(encoding="utf-8").strip()
        parsed = json.loads(line)
        assert parsed["file"] == "typed-values-basic.fods"

    def test_density_values_consistent(self):
        rec = _export_cell_density_record(TYPED_VALUES)
        # numeric + string densities should not exceed 1.0 per cell
        assert rec["numeric_density"] + rec["string_density"] <= 1.01  # allow float rounding

    def test_minimal_sample_exports_without_error(self):
        rec = _export_cell_density_record(MINIMAL)
        assert "file" in rec
        assert rec["max_row_count"] >= 0
