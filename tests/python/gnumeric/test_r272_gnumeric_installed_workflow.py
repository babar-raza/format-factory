"""
tests/python/gnumeric/test_r272_gnumeric_installed_workflow.py

Sprint: ff-sprint-s272-gnumeric-installed-workflow-20260626
Authority: FACT-GNUMERIC-001 (Gnumeric Workbook XML format)

Tests for gnumeric_installed_workflow() in gnumeric_codec.py.
"""
from __future__ import annotations

from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_SAMPLE = _REPO / "samples" / "by-format" / "gnumeric" / "minimal-spreadsheet.gnumeric"
_MULTI = _REPO / "samples" / "by-format" / "gnumeric" / "multi-cell-basic.gnumeric"


class TestGnumericInstalledWorkflowImport:
    """gnumeric_installed_workflow is importable and callable."""

    def test_importable_from_gnumeric_codec(self):
        from gnumeric.gnumeric_codec import gnumeric_installed_workflow
        assert callable(gnumeric_installed_workflow)

    def test_importable_from_package(self):
        import gnumeric
        assert hasattr(gnumeric, "gnumeric_installed_workflow")


class TestGnumericInstalledWorkflowOutput:
    """gnumeric_installed_workflow returns correct output structure."""

    def test_returns_dict(self):
        from gnumeric.gnumeric_codec import gnumeric_installed_workflow
        result = gnumeric_installed_workflow(str(_SAMPLE))
        assert isinstance(result, dict)

    def test_format_field_is_gnumeric(self):
        from gnumeric.gnumeric_codec import gnumeric_installed_workflow
        result = gnumeric_installed_workflow(str(_SAMPLE))
        assert result["format"] == "gnumeric"

    def test_loaded_field_is_true(self):
        from gnumeric.gnumeric_codec import gnumeric_installed_workflow
        result = gnumeric_installed_workflow(str(_SAMPLE))
        assert result["loaded"] is True

    def test_sheet_count_is_integer(self):
        from gnumeric.gnumeric_codec import gnumeric_installed_workflow
        result = gnumeric_installed_workflow(str(_SAMPLE))
        assert isinstance(result["sheet_count"], int)

    def test_cell_count_is_integer(self):
        from gnumeric.gnumeric_codec import gnumeric_installed_workflow
        result = gnumeric_installed_workflow(str(_SAMPLE))
        assert isinstance(result["cell_count"], int)

    def test_has_all_required_keys(self):
        from gnumeric.gnumeric_codec import gnumeric_installed_workflow
        result = gnumeric_installed_workflow(str(_SAMPLE))
        assert {"format", "loaded", "sheet_count", "cell_count"}.issubset(result.keys())

    def test_sheet_count_positive(self):
        from gnumeric.gnumeric_codec import gnumeric_installed_workflow
        result = gnumeric_installed_workflow(str(_SAMPLE))
        assert result["sheet_count"] >= 1

    def test_consistent_across_calls(self):
        from gnumeric.gnumeric_codec import gnumeric_installed_workflow
        r1 = gnumeric_installed_workflow(str(_SAMPLE))
        r2 = gnumeric_installed_workflow(str(_SAMPLE))
        assert r1["sheet_count"] == r2["sheet_count"]
        assert r1["cell_count"] == r2["cell_count"]

    def test_multi_cell_doc(self):
        from gnumeric.gnumeric_codec import gnumeric_installed_workflow
        result = gnumeric_installed_workflow(str(_MULTI))
        assert result["loaded"] is True
        assert result["cell_count"] >= 1
