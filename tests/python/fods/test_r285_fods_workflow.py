"""
tests/python/fods/test_r285_fods_workflow.py

Sprint: ff-sprint-s285-fods-installed-workflow-20260626
Authority: ODF FODS flat-XML spreadsheet format

Tests for fods_installed_workflow() in fods_workflow.py.
"""
from __future__ import annotations

from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_SAMPLE = _REPO / "samples" / "by-format" / "fods" / "minimal-spreadsheet.fods"
_MULTI = _REPO / "samples" / "by-format" / "fods" / "multi-sheet-basic.fods"


class TestFodsInstalledWorkflowImport:
    def test_importable_from_fods_workflow(self):
        from fods.fods_workflow import fods_installed_workflow
        assert callable(fods_installed_workflow)

    def test_importable_from_package(self):
        import fods
        assert hasattr(fods, "fods_installed_workflow")


class TestFodsInstalledWorkflowOutput:
    def test_returns_dict(self):
        from fods.fods_workflow import fods_installed_workflow
        assert isinstance(fods_installed_workflow(str(_SAMPLE)), dict)

    def test_format_field(self):
        from fods.fods_workflow import fods_installed_workflow
        assert fods_installed_workflow(str(_SAMPLE))["format"] == "fods"

    def test_loaded_true(self):
        from fods.fods_workflow import fods_installed_workflow
        assert fods_installed_workflow(str(_SAMPLE))["loaded"] is True

    def test_sheet_count_integer(self):
        from fods.fods_workflow import fods_installed_workflow
        assert isinstance(fods_installed_workflow(str(_SAMPLE))["sheet_count"], int)

    def test_has_required_keys(self):
        from fods.fods_workflow import fods_installed_workflow
        r = fods_installed_workflow(str(_SAMPLE))
        assert {"format", "loaded", "sheet_count"}.issubset(r.keys())

    def test_minimal_has_one_sheet(self):
        from fods.fods_workflow import fods_installed_workflow
        r = fods_installed_workflow(str(_SAMPLE))
        assert r["sheet_count"] >= 1

    def test_multi_sheet_doc(self):
        from fods.fods_workflow import fods_installed_workflow
        r = fods_installed_workflow(str(_MULTI))
        assert r["loaded"] is True and r["sheet_count"] >= 2

    def test_consistent(self):
        from fods.fods_workflow import fods_installed_workflow
        r1 = fods_installed_workflow(str(_SAMPLE))
        r2 = fods_installed_workflow(str(_SAMPLE))
        assert r1["sheet_count"] == r2["sheet_count"]
