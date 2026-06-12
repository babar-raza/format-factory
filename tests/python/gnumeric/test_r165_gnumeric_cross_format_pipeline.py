"""Cross-format pipeline tests for Gnumeric — GAP-Gnumeric-FOSS-LOAD-001 closure.

Tests loading, transformation, and export across formats.
Demonstrates the Gnumeric load capability in a realistic pipeline context.

Sprint: FF-LIBFORGE-BROAD-IMPLEMENTATION-001
Taskcard: LFI-3-C01
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO_ROOT / "src" / "python"))

from gnumeric.gnumeric_codec import (
    create_gnumeric,
    write_gnumeric,
    load,
    export_to_csv,
    export_to_json,
    get_sheet_count,
    get_sheet_names,
    get_cell_value,
    get_row,
    get_column,
    sum_column,
    get_column_values,
)


@pytest.fixture
def simple_model():
    """Minimal single-sheet Gnumeric model."""
    return create_gnumeric([
        {"name": "Budget", "rows": [
            ["Category", "Q1", "Q2", "Q3"],
            ["Revenue", "100", "200", "300"],
            ["Expenses", "50", "80", "120"],
        ]}
    ])


@pytest.fixture
def multi_sheet_model():
    return create_gnumeric([
        {"name": "Sales", "rows": [["Item", "Amount"], ["A", "10"], ["B", "20"]]},
        {"name": "Costs", "rows": [["Item", "Amount"], ["X", "5"], ["Y", "15"]]},
    ])


# ---------------------------------------------------------------------------
# Load roundtrip
# ---------------------------------------------------------------------------


class TestLoadRoundtrip:
    def test_write_then_load_preserves_sheet_count(self, simple_model, tmp_path):
        dest = tmp_path / "budget.gnumeric"
        write_gnumeric(simple_model, dest)
        assert get_sheet_count(dest) == 1

    def test_write_then_load_preserves_sheet_name(self, simple_model, tmp_path):
        dest = tmp_path / "budget.gnumeric"
        write_gnumeric(simple_model, dest)
        assert "Budget" in get_sheet_names(dest)

    def test_write_then_load_preserves_cell_value(self, simple_model, tmp_path):
        dest = tmp_path / "budget.gnumeric"
        write_gnumeric(simple_model, dest)
        reloaded = load(dest)
        assert get_cell_value(reloaded, 0, 0, 0) == "Category"

    def test_multi_sheet_roundtrip(self, multi_sheet_model, tmp_path):
        dest = tmp_path / "multi.gnumeric"
        write_gnumeric(multi_sheet_model, dest)
        assert get_sheet_count(dest) == 2
        names = get_sheet_names(dest)
        assert "Sales" in names
        assert "Costs" in names


# ---------------------------------------------------------------------------
# Pipeline: Gnumeric → CSV
# ---------------------------------------------------------------------------


class TestGnumericToCsvPipeline:
    def test_export_to_csv_returns_string(self, simple_model, tmp_path):
        dest = tmp_path / "budget.gnumeric"
        write_gnumeric(simple_model, dest)
        csv_out = export_to_csv(dest)
        assert isinstance(csv_out, str)
        assert len(csv_out) > 0

    def test_export_to_csv_has_header(self, simple_model, tmp_path):
        dest = tmp_path / "budget.gnumeric"
        write_gnumeric(simple_model, dest)
        csv_out = export_to_csv(dest)
        assert "Category" in csv_out

    def test_export_to_csv_writes_file(self, simple_model, tmp_path):
        gnumeric_path = tmp_path / "budget.gnumeric"
        write_gnumeric(simple_model, gnumeric_path)
        csv_path = tmp_path / "budget.csv"
        csv_content = export_to_csv(gnumeric_path)
        csv_path.write_text(csv_content, encoding="utf-8")
        assert csv_path.exists()
        assert csv_path.stat().st_size > 0


# ---------------------------------------------------------------------------
# Pipeline: Gnumeric → JSON
# ---------------------------------------------------------------------------


class TestGnumericToJsonPipeline:
    def test_export_to_json_returns_string(self, simple_model, tmp_path):
        dest = tmp_path / "budget.gnumeric"
        write_gnumeric(simple_model, dest)
        json_out = export_to_json(dest)
        assert isinstance(json_out, str)

    def test_export_to_json_parseable(self, simple_model, tmp_path):
        dest = tmp_path / "budget.gnumeric"
        write_gnumeric(simple_model, dest)
        json_out = export_to_json(dest)
        parsed = json.loads(json_out)
        assert isinstance(parsed, (list, dict))

    def test_export_to_json_has_sheet_data(self, simple_model, tmp_path):
        dest = tmp_path / "budget.gnumeric"
        write_gnumeric(simple_model, dest)
        json_out = export_to_json(dest)
        # JSON should contain cell data
        assert "Category" in json_out or "Budget" in json_out


# ---------------------------------------------------------------------------
# Column operations on loaded model
# ---------------------------------------------------------------------------


class TestColumnOperations:
    def test_sum_column_numeric_data(self, simple_model, tmp_path):
        dest = tmp_path / "budget.gnumeric"
        write_gnumeric(simple_model, dest)
        reloaded = load(dest)
        # Column 1 (Q1): "Q1", "100", "50" — sum of numeric = 150
        total = sum_column(reloaded, 0, 1)
        assert total == 150

    def test_get_column_values_header_row(self, simple_model, tmp_path):
        dest = tmp_path / "budget.gnumeric"
        write_gnumeric(simple_model, dest)
        reloaded = load(dest)
        col0 = get_column_values(reloaded, 0, 0)
        assert "Category" in col0
        assert "Revenue" in col0

    def test_get_row_returns_list(self, simple_model, tmp_path):
        dest = tmp_path / "budget.gnumeric"
        write_gnumeric(simple_model, dest)
        reloaded = load(dest)
        row0 = get_row(reloaded, 0, 0)
        assert isinstance(row0, list)
        assert "Category" in row0
