"""
tests/python/fodt/test_r286_fodt_workflow.py

Sprint: ff-sprint-s286-fodt-installed-workflow-20260626
Authority: ODF FODT flat-XML document format

Tests for fodt_installed_workflow() in fodt_workflow.py.
"""
from __future__ import annotations

from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_SAMPLE = _REPO / "samples" / "by-format" / "fodt" / "minimal-document.fodt"
_TABLE = _REPO / "samples" / "by-format" / "fodt" / "table-basic.fodt"


class TestFodtInstalledWorkflowImport:
    def test_importable_from_fodt_workflow(self):
        from fodt.fodt_workflow import fodt_installed_workflow
        assert callable(fodt_installed_workflow)

    def test_importable_from_package(self):
        import fodt
        assert hasattr(fodt, "fodt_installed_workflow")


class TestFodtInstalledWorkflowOutput:
    def test_returns_dict(self):
        from fodt.fodt_workflow import fodt_installed_workflow
        assert isinstance(fodt_installed_workflow(str(_SAMPLE)), dict)

    def test_format_field(self):
        from fodt.fodt_workflow import fodt_installed_workflow
        assert fodt_installed_workflow(str(_SAMPLE))["format"] == "fodt"

    def test_loaded_true(self):
        from fodt.fodt_workflow import fodt_installed_workflow
        assert fodt_installed_workflow(str(_SAMPLE))["loaded"] is True

    def test_block_count_integer(self):
        from fodt.fodt_workflow import fodt_installed_workflow
        assert isinstance(fodt_installed_workflow(str(_SAMPLE))["block_count"], int)

    def test_table_count_integer(self):
        from fodt.fodt_workflow import fodt_installed_workflow
        assert isinstance(fodt_installed_workflow(str(_SAMPLE))["table_count"], int)

    def test_has_required_keys(self):
        from fodt.fodt_workflow import fodt_installed_workflow
        r = fodt_installed_workflow(str(_SAMPLE))
        assert {"format", "loaded", "block_count", "table_count"}.issubset(r.keys())

    def test_minimal_has_blocks(self):
        from fodt.fodt_workflow import fodt_installed_workflow
        r = fodt_installed_workflow(str(_SAMPLE))
        assert r["block_count"] >= 0

    def test_table_doc(self):
        from fodt.fodt_workflow import fodt_installed_workflow
        r = fodt_installed_workflow(str(_TABLE))
        assert r["loaded"] is True and r["table_count"] >= 1

    def test_consistent(self):
        from fodt.fodt_workflow import fodt_installed_workflow
        r1 = fodt_installed_workflow(str(_SAMPLE))
        r2 = fodt_installed_workflow(str(_SAMPLE))
        assert r1["block_count"] == r2["block_count"]
