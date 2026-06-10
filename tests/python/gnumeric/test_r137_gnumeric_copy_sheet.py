"""Tests for copy_sheet() — Gnumeric sheet copy.

Sprint: FORMAT-FACTORY-AUTONOMY-ACCELERATION-SPRINT-4-001
TC-PRODUCT-GNUMERIC-COPY-SHEET
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO_ROOT / "src" / "python"))

from gnumeric.gnumeric_codec import create_gnumeric, copy_sheet, GnumericError


class TestCopySheet:
    def test_sheet_count_increases(self):
        model = create_gnumeric([{"name": "Data"}])
        result = copy_sheet(model, 0)
        assert result["sheet_count"] == 2

    def test_copy_name_has_suffix(self):
        model = create_gnumeric([{"name": "Data"}])
        result = copy_sheet(model, 0)
        names = [s["name"] for s in result["sheets"]]
        assert "Data (Copy)" in names

    def test_original_sheet_preserved(self):
        model = create_gnumeric([{"name": "Data"}])
        result = copy_sheet(model, 0)
        names = [s["name"] for s in result["sheets"]]
        assert "Data" in names

    def test_copy_preserves_cell_data(self):
        model = create_gnumeric([{"name": "Data", "rows": [["A", "B"]]}])
        result = copy_sheet(model, 0)
        copy = result["sheets"][1]
        assert "A" in copy["cell_values"]
        assert "B" in copy["cell_values"]

    def test_does_not_mutate_original(self):
        model = create_gnumeric([{"name": "Data"}])
        copy_sheet(model, 0)
        assert model["sheet_count"] == 1

    def test_copy_is_independent(self):
        model = create_gnumeric([{"name": "Data", "rows": [["X"]]}])
        result = copy_sheet(model, 0)
        original_cells = result["sheets"][0]["cell_values"]
        copy_cells = result["sheets"][1]["cell_values"]
        assert original_cells == copy_cells

    def test_index_error_out_of_range(self):
        model = create_gnumeric([{"name": "S1"}])
        with pytest.raises(GnumericError):
            copy_sheet(model, 5)

    def test_type_error_on_non_dict(self):
        with pytest.raises(TypeError):
            copy_sheet("not a dict", 0)

    def test_copy_appended_at_end(self):
        model = create_gnumeric([{"name": "A"}, {"name": "B"}])
        result = copy_sheet(model, 0)
        assert result["sheets"][2]["name"] == "A (Copy)"

    def test_multiple_copies_distinct_names(self):
        model = create_gnumeric([{"name": "Sheet1"}])
        r1 = copy_sheet(model, 0)
        r2 = copy_sheet(r1, 1)
        assert r2["sheet_count"] == 3
