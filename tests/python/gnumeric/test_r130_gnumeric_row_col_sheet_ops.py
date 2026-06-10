"""Tests for Gnumeric get_row, get_column, delete_sheet, rename_sheet.

Sprint: FORMAT-FACTORY-AUTONOMY-ACCELERATION-SPRINT-2-001
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT / "src" / "python"))

from gnumeric.gnumeric_codec import (
    create_gnumeric,
    GnumericError,
    get_row,
    get_column,
    delete_sheet,
    rename_sheet,
)


@pytest.fixture
def two_sheet_model():
    return create_gnumeric([
        {"name": "Alpha", "rows": [["A1", "B1", "C1"], ["A2", "B2", "C2"]]},
        {"name": "Beta", "rows": [["X", "Y"], ["", "Z"]]},
    ])


# ---------------------------------------------------------------------------
# get_row
# ---------------------------------------------------------------------------

class TestGetRow:
    def test_basic_row(self, two_sheet_model):
        result = get_row(two_sheet_model, 0, 0)
        assert result == ["A1", "B1", "C1"]

    def test_second_row(self, two_sheet_model):
        result = get_row(two_sheet_model, 0, 1)
        assert result == ["A2", "B2", "C2"]

    def test_nonexistent_row_returns_empty(self, two_sheet_model):
        result = get_row(two_sheet_model, 0, 99)
        assert result == []

    def test_second_sheet_row(self, two_sheet_model):
        result = get_row(two_sheet_model, 1, 0)
        assert result == ["X", "Y"]

    def test_row_with_gap(self):
        model = create_gnumeric([{"name": "S", "rows": [["A", "", "C"]]}])
        result = get_row(model, 0, 0)
        assert result == ["A", "", "C"]

    def test_empty_sheet_returns_empty(self):
        model = create_gnumeric([{"name": "Empty"}])
        result = get_row(model, 0, 0)
        assert result == []

    def test_raises_on_invalid_sheet_index(self, two_sheet_model):
        with pytest.raises(GnumericError):
            get_row(two_sheet_model, 99, 0)

    def test_raises_on_non_dict(self):
        with pytest.raises(TypeError):
            get_row("not a dict", 0, 0)

    def test_returns_list(self, two_sheet_model):
        result = get_row(two_sheet_model, 0, 0)
        assert isinstance(result, list)


# ---------------------------------------------------------------------------
# get_column
# ---------------------------------------------------------------------------

class TestGetColumn:
    def test_first_column(self, two_sheet_model):
        result = get_column(two_sheet_model, 0, 0)
        assert result == ["A1", "A2"]

    def test_second_column(self, two_sheet_model):
        result = get_column(two_sheet_model, 0, 1)
        assert result == ["B1", "B2"]

    def test_nonexistent_column_returns_empty(self, two_sheet_model):
        result = get_column(two_sheet_model, 0, 99)
        assert result == []

    def test_column_with_gap(self):
        model = create_gnumeric([{"name": "S", "rows": [["A"], [], ["C"]]}])
        result = get_column(model, 0, 0)
        assert result[0] == "A"
        assert result[2] == "C"
        assert len(result) == 3

    def test_raises_on_invalid_sheet_index(self, two_sheet_model):
        with pytest.raises(GnumericError):
            get_column(two_sheet_model, 5, 0)

    def test_raises_on_non_dict(self):
        with pytest.raises(TypeError):
            get_column("not a dict", 0, 0)

    def test_returns_list(self, two_sheet_model):
        result = get_column(two_sheet_model, 0, 0)
        assert isinstance(result, list)


# ---------------------------------------------------------------------------
# delete_sheet
# ---------------------------------------------------------------------------

class TestDeleteSheet:
    def test_delete_first_sheet(self, two_sheet_model):
        new_model = delete_sheet(two_sheet_model, 0)
        assert new_model["sheet_count"] == 1
        assert new_model["sheets"][0]["name"] == "Beta"

    def test_delete_second_sheet(self, two_sheet_model):
        new_model = delete_sheet(two_sheet_model, 1)
        assert new_model["sheet_count"] == 1
        assert new_model["sheets"][0]["name"] == "Alpha"

    def test_does_not_mutate_original(self, two_sheet_model):
        delete_sheet(two_sheet_model, 0)
        assert two_sheet_model["sheet_count"] == 2

    def test_cell_count_updated(self, two_sheet_model):
        original_total = two_sheet_model["cell_count"]
        new_model = delete_sheet(two_sheet_model, 0)
        assert new_model["cell_count"] < original_total

    def test_raises_on_invalid_index(self, two_sheet_model):
        with pytest.raises(GnumericError):
            delete_sheet(two_sheet_model, 5)

    def test_raises_on_negative_index(self, two_sheet_model):
        with pytest.raises(GnumericError):
            delete_sheet(two_sheet_model, -1)

    def test_raises_on_non_dict(self):
        with pytest.raises(TypeError):
            delete_sheet("not a dict", 0)

    def test_is_gnumeric_preserved(self, two_sheet_model):
        new_model = delete_sheet(two_sheet_model, 0)
        assert new_model.get("is_gnumeric") is True


# ---------------------------------------------------------------------------
# rename_sheet
# ---------------------------------------------------------------------------

class TestRenameSheet:
    def test_rename_first_sheet(self, two_sheet_model):
        new_model = rename_sheet(two_sheet_model, 0, "NewAlpha")
        assert new_model["sheets"][0]["name"] == "NewAlpha"
        assert new_model["sheets"][1]["name"] == "Beta"

    def test_rename_second_sheet(self, two_sheet_model):
        new_model = rename_sheet(two_sheet_model, 1, "NewBeta")
        assert new_model["sheets"][1]["name"] == "NewBeta"

    def test_does_not_mutate_original(self, two_sheet_model):
        rename_sheet(two_sheet_model, 0, "NewAlpha")
        assert two_sheet_model["sheets"][0]["name"] == "Alpha"

    def test_sheet_count_unchanged(self, two_sheet_model):
        new_model = rename_sheet(two_sheet_model, 0, "X")
        assert new_model["sheet_count"] == two_sheet_model["sheet_count"]

    def test_empty_string_name(self, two_sheet_model):
        new_model = rename_sheet(two_sheet_model, 0, "")
        assert new_model["sheets"][0]["name"] == ""

    def test_raises_on_invalid_index(self, two_sheet_model):
        with pytest.raises(GnumericError):
            rename_sheet(two_sheet_model, 5, "X")

    def test_raises_on_non_dict(self):
        with pytest.raises(TypeError):
            rename_sheet("not a dict", 0, "X")

    def test_raises_on_non_string_name(self, two_sheet_model):
        with pytest.raises(TypeError):
            rename_sheet(two_sheet_model, 0, 42)

    def test_is_gnumeric_preserved(self, two_sheet_model):
        new_model = rename_sheet(two_sheet_model, 0, "X")
        assert new_model.get("is_gnumeric") is True
