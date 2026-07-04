"""
tests/python/dif/test_r277_dif_workflow.py

Sprint: ff-sprint-s277-dif-installed-workflow-20260626
Authority: DIF (Data Interchange Format) spreadsheet format

Tests for dif_installed_workflow() in dif_workflow.py.
"""
from __future__ import annotations

from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_SAMPLE = _REPO / "samples" / "by-format" / "dif" / "valid" / "minimal-2x2.dif"
_SINGLE = _REPO / "samples" / "by-format" / "dif" / "valid" / "single-cell.dif"


class TestDifInstalledWorkflowImport:
    """dif_installed_workflow is importable and callable."""

    def test_importable_from_dif_workflow(self):
        from dif.dif_workflow import dif_installed_workflow
        assert callable(dif_installed_workflow)

    def test_importable_from_package(self):
        import dif
        assert hasattr(dif, "dif_installed_workflow")


class TestDifInstalledWorkflowOutput:
    """dif_installed_workflow returns correct output structure."""

    def test_returns_dict(self):
        from dif.dif_workflow import dif_installed_workflow
        result = dif_installed_workflow(str(_SAMPLE))
        assert isinstance(result, dict)

    def test_format_field_is_dif(self):
        from dif.dif_workflow import dif_installed_workflow
        result = dif_installed_workflow(str(_SAMPLE))
        assert result["format"] == "dif"

    def test_loaded_field_is_true(self):
        from dif.dif_workflow import dif_installed_workflow
        result = dif_installed_workflow(str(_SAMPLE))
        assert result["loaded"] is True

    def test_row_count_is_integer(self):
        from dif.dif_workflow import dif_installed_workflow
        result = dif_installed_workflow(str(_SAMPLE))
        assert isinstance(result["row_count"], int)

    def test_column_count_is_integer(self):
        from dif.dif_workflow import dif_installed_workflow
        result = dif_installed_workflow(str(_SAMPLE))
        assert isinstance(result["column_count"], int)

    def test_has_all_required_keys(self):
        from dif.dif_workflow import dif_installed_workflow
        result = dif_installed_workflow(str(_SAMPLE))
        assert {"format", "loaded", "row_count", "column_count"}.issubset(result.keys())

    def test_minimal_2x2_column_count(self):
        from dif.dif_workflow import dif_installed_workflow
        result = dif_installed_workflow(str(_SAMPLE))
        assert result["column_count"] >= 1

    def test_consistent_across_calls(self):
        from dif.dif_workflow import dif_installed_workflow
        r1 = dif_installed_workflow(str(_SAMPLE))
        r2 = dif_installed_workflow(str(_SAMPLE))
        assert r1["row_count"] == r2["row_count"]
        assert r1["column_count"] == r2["column_count"]

    def test_single_cell_doc(self):
        from dif.dif_workflow import dif_installed_workflow
        result = dif_installed_workflow(str(_SINGLE))
        assert result["loaded"] is True
