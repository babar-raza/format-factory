"""
tests/python/ods/test_r279_ods_installed_workflow.py

Sprint: ff-sprint-s279-ods-installed-workflow-20260626
Authority: ODF ODS spreadsheet format

Tests for ods_installed_workflow() in ods_workflow.py.
"""
from __future__ import annotations

from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_SAMPLE = _REPO / "samples" / "by-format" / "ods" / "valid" / "minimal-spreadsheet.ods"
_NUMERIC = _REPO / "samples" / "by-format" / "ods" / "valid" / "numeric-row.ods"


class TestOdsInstalledWorkflowImport:
    """ods_installed_workflow is importable and callable."""

    def test_importable_from_ods_workflow(self):
        from ods.ods_workflow import ods_installed_workflow
        assert callable(ods_installed_workflow)

    def test_importable_from_package(self):
        import ods
        assert hasattr(ods, "ods_installed_workflow")


class TestOdsInstalledWorkflowOutput:
    """ods_installed_workflow returns correct output structure."""

    def test_returns_dict(self):
        from ods.ods_workflow import ods_installed_workflow
        result = ods_installed_workflow(str(_SAMPLE))
        assert isinstance(result, dict)

    def test_format_field_is_ods(self):
        from ods.ods_workflow import ods_installed_workflow
        result = ods_installed_workflow(str(_SAMPLE))
        assert result["format"] == "ods"

    def test_loaded_field_is_true(self):
        from ods.ods_workflow import ods_installed_workflow
        result = ods_installed_workflow(str(_SAMPLE))
        assert result["loaded"] is True

    def test_sheet_count_is_integer(self):
        from ods.ods_workflow import ods_installed_workflow
        result = ods_installed_workflow(str(_SAMPLE))
        assert isinstance(result["sheet_count"], int)

    def test_row_count_is_integer(self):
        from ods.ods_workflow import ods_installed_workflow
        result = ods_installed_workflow(str(_SAMPLE))
        assert isinstance(result["row_count"], int)

    def test_has_all_required_keys(self):
        from ods.ods_workflow import ods_installed_workflow
        result = ods_installed_workflow(str(_SAMPLE))
        assert {"format", "loaded", "sheet_count", "row_count"}.issubset(result.keys())

    def test_sheet_count_positive(self):
        from ods.ods_workflow import ods_installed_workflow
        result = ods_installed_workflow(str(_SAMPLE))
        assert result["sheet_count"] >= 1

    def test_consistent_across_calls(self):
        from ods.ods_workflow import ods_installed_workflow
        r1 = ods_installed_workflow(str(_SAMPLE))
        r2 = ods_installed_workflow(str(_SAMPLE))
        assert r1["sheet_count"] == r2["sheet_count"]
        assert r1["row_count"] == r2["row_count"]

    def test_numeric_row_doc(self):
        from ods.ods_workflow import ods_installed_workflow
        result = ods_installed_workflow(str(_NUMERIC))
        assert result["loaded"] is True
        assert result["sheet_count"] >= 1
