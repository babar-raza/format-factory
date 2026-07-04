"""
tests/python/sylk/test_r273_sylk_workflow.py

Sprint: ff-sprint-s273-sylk-installed-workflow-20260626
Authority: SYLK spreadsheet format

Tests for sylk_installed_workflow() in sylk_workflow.py.
"""
from __future__ import annotations

from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_SAMPLE = _REPO / "samples" / "by-format" / "sylk" / "valid" / "minimal-2x2.slk"
_SINGLE = _REPO / "samples" / "by-format" / "sylk" / "valid" / "single-cell.slk"


class TestSylkInstalledWorkflowImport:
    """sylk_installed_workflow is importable and callable."""

    def test_importable_from_sylk_workflow(self):
        from sylk.sylk_workflow import sylk_installed_workflow
        assert callable(sylk_installed_workflow)

    def test_importable_from_package(self):
        import sylk
        assert hasattr(sylk, "sylk_installed_workflow")


class TestSylkInstalledWorkflowOutput:
    """sylk_installed_workflow returns correct output structure."""

    def test_returns_dict(self):
        from sylk.sylk_workflow import sylk_installed_workflow
        result = sylk_installed_workflow(str(_SAMPLE))
        assert isinstance(result, dict)

    def test_format_field_is_sylk(self):
        from sylk.sylk_workflow import sylk_installed_workflow
        result = sylk_installed_workflow(str(_SAMPLE))
        assert result["format"] == "sylk"

    def test_loaded_field_is_true(self):
        from sylk.sylk_workflow import sylk_installed_workflow
        result = sylk_installed_workflow(str(_SAMPLE))
        assert result["loaded"] is True

    def test_row_count_is_integer(self):
        from sylk.sylk_workflow import sylk_installed_workflow
        result = sylk_installed_workflow(str(_SAMPLE))
        assert isinstance(result["row_count"], int)

    def test_column_count_is_integer(self):
        from sylk.sylk_workflow import sylk_installed_workflow
        result = sylk_installed_workflow(str(_SAMPLE))
        assert isinstance(result["column_count"], int)

    def test_cell_count_is_integer(self):
        from sylk.sylk_workflow import sylk_installed_workflow
        result = sylk_installed_workflow(str(_SAMPLE))
        assert isinstance(result["cell_count"], int)

    def test_has_all_required_keys(self):
        from sylk.sylk_workflow import sylk_installed_workflow
        result = sylk_installed_workflow(str(_SAMPLE))
        assert {"format", "loaded", "row_count", "column_count", "cell_count"}.issubset(result.keys())

    def test_minimal_2x2_row_count(self):
        from sylk.sylk_workflow import sylk_installed_workflow
        result = sylk_installed_workflow(str(_SAMPLE))
        assert result["row_count"] == 2

    def test_minimal_2x2_column_count(self):
        from sylk.sylk_workflow import sylk_installed_workflow
        result = sylk_installed_workflow(str(_SAMPLE))
        assert result["column_count"] == 2

    def test_single_cell_doc(self):
        from sylk.sylk_workflow import sylk_installed_workflow
        result = sylk_installed_workflow(str(_SINGLE))
        assert result["loaded"] is True
        assert result["cell_count"] >= 1

    def test_consistent_across_calls(self):
        from sylk.sylk_workflow import sylk_installed_workflow
        r1 = sylk_installed_workflow(str(_SAMPLE))
        r2 = sylk_installed_workflow(str(_SAMPLE))
        assert r1["row_count"] == r2["row_count"]
        assert r1["cell_count"] == r2["cell_count"]
